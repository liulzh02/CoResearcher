import pytest

from coresearcher.graph import make_research_director
from coresearcher.subagents import SubagentDispatcher, SubagentTask, default_subagent_registry


def test_builtin_subagents_include_coding_researcher():
    registry = default_subagent_registry()
    names = registry.names()
    assert "coding-researcher" in names
    assert registry.get("coding-researcher").allow_subagent_delegation is False


async def test_subagent_dispatch_and_nested_delegation_prevention():
    dispatcher = SubagentDispatcher(max_concurrency=1)
    result, events = await dispatcher.dispatch(
        SubagentTask(
            subagent_name="coding-researcher",
            description="Run a baseline check with code.",
        ),
        thread_id="thread_1",
        run_id="run_1",
    )
    assert result.subagent_name == "coding-researcher"
    assert any(event.type.value == "subagent.completed" for event in events)


async def test_director_clarifies_ambiguous_goal():
    graph = make_research_director()
    result = await graph.ainvoke(
        {
            "thread_id": "thread_1",
            "run_id": "run_1",
            "user_message": "find a good research direction",
            "events": [],
        }
    )
    assert "one more detail" in result["final_response"]


async def test_director_delegates_code_tasks():
    graph = make_research_director()
    result = await graph.ainvoke(
        {
            "thread_id": "thread_1",
            "run_id": "run_1",
            "user_message": "Please reproduce the baseline with code and analyze data.",
            "events": [],
        }
    )
    names = {item["subagent_name"] for item in result["subagent_results"]}
    assert "coding-researcher" in names
    assert "critic" in names
    coding = next(item for item in result["subagent_results"] if item["subagent_name"] == "coding-researcher")
    assert coding["execution_observation"]["environment"]
    assert "not standalone" in result["final_response"].lower()


async def test_director_does_not_auto_launch_coding_for_data_or_literature_work():
    graph = make_research_director()
    result = await graph.ainvoke(
        {
            "thread_id": "thread_1",
            "run_id": "run_1",
            "user_message": "Please analyze data availability in the literature and critique limitations.",
            "events": [],
        }
    )

    names = {item["subagent_name"] for item in result["subagent_results"]}
    assert "literature-scout" in names
    assert "critic" in names
    assert "coding-researcher" not in names


async def test_coding_subagent_result_is_bounded_execution_observation():
    dispatcher = SubagentDispatcher(max_concurrency=1)
    result, _ = await dispatcher.dispatch(
        SubagentTask(
            subagent_name="coding-researcher",
            description="Reproduce the baseline with code.",
        ),
        thread_id="thread_1",
        run_id="run_1",
    )

    assert result.execution_observation["environment"]
    assert result.execution_observation["observed_output"]
    assert result.execution_observation["limitations"]
    assert "not authoritative" in " ".join(result.limitations).lower()
