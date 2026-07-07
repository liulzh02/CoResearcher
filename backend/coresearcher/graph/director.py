from __future__ import annotations

from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from coresearcher.context import ContextBuilder, ContextPack
from coresearcher.domain.events import ResearchEvent, ResearchEventType
from coresearcher.domain.state import OpenQuestion, ResearchState
from coresearcher.subagents.dispatcher import SubagentDispatcher, SubagentTask


class DirectorGraphState(TypedDict, total=False):
    thread_id: str
    run_id: str
    user_message: str
    research_state: ResearchState
    events: list[ResearchEvent]
    plan: list[str]
    subagent_tasks: list[SubagentTask]
    subagent_results: list[dict[str, Any]]
    context_pack: ContextPack
    final_response: str
    route: Literal["clarify", "delegate", "answer"]


def _needs_clarification(message: str) -> bool:
    lowered = message.lower()
    too_short = len(message.strip()) < 16
    vague = "good research direction" in lowered
    return too_short or vague


def _requests_execution_based_validation(message: str) -> bool:
    lowered = message.lower()
    phrases = [
        "coding subagent",
        "code execution",
        "run code",
        "run the code",
        "execute code",
        "reproduce",
        "reproduction",
        "replicate",
        "benchmark",
        "baseline with code",
        "implement and test",
        "inspect the implementation",
    ]
    return any(phrase in lowered for phrase in phrases)


def _requests_literature_work(message: str) -> bool:
    lowered = message.lower()
    words = [
        "paper",
        "literature",
        "source",
        "citation",
        "critique",
        "limitation",
        "data availability",
    ]
    return any(word in lowered for word in words)


def _node_event(
    state: DirectorGraphState,
    message: str,
    event_type: ResearchEventType = ResearchEventType.RUN_PROGRESS,
) -> ResearchEvent:
    return ResearchEvent(
        type=event_type,
        thread_id=state["thread_id"],
        run_id=state["run_id"],
        payload={"message": message},
    )


def _load_context(state: DirectorGraphState) -> DirectorGraphState:
    research_state = state.get("research_state") or ResearchState()
    context_pack = ContextBuilder().build_director_pack(
        latest_user_message=state["user_message"],
        research_state=research_state,
    )
    events = state.get("events", [])
    events.append(_node_event(state, "Loaded research context.", ResearchEventType.CONTEXT_BUILD_COMPLETED))
    return {
        **state,
        "research_state": research_state,
        "context_pack": context_pack,
        "events": events,
    }


def _director_reasoning(state: DirectorGraphState) -> DirectorGraphState:
    events = state.get("events", [])
    message = state["user_message"]
    if _needs_clarification(message):
        route: Literal["clarify", "delegate", "answer"] = "clarify"
        plan: list[str] = ["Ask for missing research domain, target question, or constraints."]
    elif _requests_execution_based_validation(message):
        route = "delegate"
        plan = [
            "Ask coding-researcher to perform bounded code-based validation.",
            "Ask critic to identify assumptions and limitations.",
        ]
    elif _requests_literature_work(message):
        route = "delegate"
        plan = [
            "Ask literature-scout to identify candidate sources.",
            "Ask paper-reader to extract paper evidence.",
            "Ask critic to identify limitations.",
        ]
    else:
        route = "answer"
        plan = ["Create a concise research direction response and record open questions."]

    events.append(
        ResearchEvent(
            type=ResearchEventType.DIRECTOR_ROUTE_SELECTED,
            thread_id=state["thread_id"],
            run_id=state["run_id"],
            payload={"route": route, "message": f"Director selected route: {route}."},
        )
    )
    return {**state, "events": events, "route": route, "plan": plan}


def _clarification(state: DirectorGraphState) -> DirectorGraphState:
    events = state.get("events", [])
    response = (
        "I need one more detail before launching research: please specify the research domain, "
        "target question, expected output, or key constraints."
    )
    events.append(
        ResearchEvent(
            type=ResearchEventType.FINAL_RESPONSE,
            thread_id=state["thread_id"],
            run_id=state["run_id"],
            payload={"content": response},
        )
    )
    return {**state, "events": events, "final_response": response}


def _delegation_planning(state: DirectorGraphState) -> DirectorGraphState:
    tasks: list[SubagentTask] = []
    for item in state.get("plan", []):
        if "coding-researcher" in item:
            tasks.append(SubagentTask(subagent_name="coding-researcher", description=item))
        elif "literature-scout" in item:
            tasks.append(SubagentTask(subagent_name="literature-scout", description=item))
        elif "paper-reader" in item:
            tasks.append(SubagentTask(subagent_name="paper-reader", description=item))
        elif "critic" in item:
            tasks.append(SubagentTask(subagent_name="critic", description=item))
    events = state.get("events", [])
    events.append(
        ResearchEvent(
            type=ResearchEventType.DIRECTOR_PLAN_CREATED,
            thread_id=state["thread_id"],
            run_id=state["run_id"],
            payload={
                "task_count": len(tasks),
                "message": f"Planned {len(tasks)} subagent task(s).",
            },
        )
    )
    return {**state, "subagent_tasks": tasks, "events": events}


async def _subagent_execution(state: DirectorGraphState) -> DirectorGraphState:
    dispatcher = SubagentDispatcher()
    results, events = await dispatcher.dispatch_many(
        state.get("subagent_tasks", []),
        thread_id=state["thread_id"],
        run_id=state["run_id"],
    )
    all_events = [*state.get("events", []), *events]
    return {
        **state,
        "events": all_events,
        "subagent_results": [result.model_dump(mode="json") for result in results],
    }


def _result_merging(state: DirectorGraphState) -> DirectorGraphState:
    research_state = state["research_state"]
    for result in state.get("subagent_results", []):
        if result["subagent_name"] == "critic":
            research_state.open_questions.append(
                OpenQuestion(text=f"Critique follow-up: {result['summary']}", source="critic")
            )
    events = state.get("events", [])
    events.append(_node_event(state, "Merged subagent results."))
    return {**state, "research_state": research_state, "events": events}


def _state_update(state: DirectorGraphState) -> DirectorGraphState:
    research_state = state["research_state"]
    message = state["user_message"]
    if not research_state.question.text:
        research_state.question.text = message
    if not research_state.open_questions:
        research_state.open_questions.append(
            OpenQuestion(text="What evidence would best validate this direction?", source="director")
        )
    events = state.get("events", [])
    events.append(
        ResearchEvent(
            type=ResearchEventType.STATE_UPDATED,
            thread_id=state["thread_id"],
            run_id=state["run_id"],
            payload={"object_type": "research_state", "object_id": state["thread_id"]},
        )
    )
    return {**state, "research_state": research_state, "events": events}


def _critique(state: DirectorGraphState) -> DirectorGraphState:
    events = state.get("events", [])
    events.append(_node_event(state, "Checked uncertainty and critique notes."))
    return {**state, "events": events}


def _synthesis(state: DirectorGraphState) -> DirectorGraphState:
    events = state.get("events", [])
    events.append(_node_event(state, "Synthesizing final response.", ResearchEventType.DIRECTOR_SYNTHESIS_STARTED))
    plan = state.get("plan", [])
    subagent_results = state.get("subagent_results", [])
    if subagent_results:
        result_lines = "\n".join(
            f"- {item['subagent_name']}: {item['summary']}" for item in subagent_results
        )
        coding_note = ""
        if any(item["subagent_name"] == "coding-researcher" for item in subagent_results):
            coding_note = (
                "\n\nCoding observations are execution evidence with scope limits; they are "
                "not standalone authoritative conclusions without corroborating evidence."
            )
        response = (
            "Here is the current research loop result:\n\n"
            f"Plan:\n{chr(10).join(f'- {item}' for item in plan)}\n\n"
            f"Subagent findings:\n{result_lines}\n\n"
            "These findings should be treated as provisional until linked to stronger evidence."
            f"{coding_note}"
        )
    else:
        response = (
            "A useful next step is to turn the broad goal into 2-3 testable research questions, "
            "then compare literature coverage, method feasibility, and evidence gaps."
        )
    events.append(
        ResearchEvent(
            type=ResearchEventType.FINAL_RESPONSE,
            thread_id=state["thread_id"],
            run_id=state["run_id"],
            payload={"content": response},
        )
    )
    return {**state, "final_response": response, "events": events}


def _event_emission(state: DirectorGraphState) -> DirectorGraphState:
    events = state.get("events", [])
    events.append(
        ResearchEvent(
            type=ResearchEventType.RUN_COMPLETED,
            thread_id=state["thread_id"],
            run_id=state["run_id"],
            payload={"final_response": state.get("final_response", "")},
        )
    )
    return {**state, "events": events}


def _route_after_reasoning(state: DirectorGraphState) -> str:
    return state["route"]


def make_research_director():
    graph = StateGraph(DirectorGraphState)
    graph.add_node("context_loading", _load_context)
    graph.add_node("director_reasoning", _director_reasoning)
    graph.add_node("clarification", _clarification)
    graph.add_node("delegation_planning", _delegation_planning)
    graph.add_node("subagent_execution", _subagent_execution)
    graph.add_node("result_merging", _result_merging)
    graph.add_node("research_state_update", _state_update)
    graph.add_node("critique", _critique)
    graph.add_node("synthesis", _synthesis)
    graph.add_node("event_emission", _event_emission)

    graph.add_edge(START, "context_loading")
    graph.add_edge("context_loading", "director_reasoning")
    graph.add_conditional_edges(
        "director_reasoning",
        _route_after_reasoning,
        {
            "clarify": "clarification",
            "delegate": "delegation_planning",
            "answer": "research_state_update",
        },
    )
    graph.add_edge("clarification", "event_emission")
    graph.add_edge("delegation_planning", "subagent_execution")
    graph.add_edge("subagent_execution", "result_merging")
    graph.add_edge("result_merging", "research_state_update")
    graph.add_edge("research_state_update", "critique")
    graph.add_edge("critique", "synthesis")
    graph.add_edge("synthesis", "event_emission")
    graph.add_edge("event_emission", END)
    return graph.compile()
