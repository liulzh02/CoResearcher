from __future__ import annotations

from collections.abc import AsyncIterator

from coresearcher.artifacts import create_research_brief
from coresearcher.domain.events import EventStore, ResearchEvent, ResearchEventType
from coresearcher.domain.state import ChatMessage, ResearchThread, new_id
from coresearcher.graph import make_research_director
from coresearcher.models import ModelFactory
from coresearcher.storage import InMemoryResearchRepository, ResearchRepository


class ResearchService:
    def __init__(
        self,
        repository: ResearchRepository | None = None,
        event_store: EventStore | None = None,
        model_factory: ModelFactory | None = None,
    ) -> None:
        self.repository = repository or InMemoryResearchRepository()
        self.event_store = event_store or EventStore()
        self.model_factory = model_factory or ModelFactory()
        self.graph = make_research_director()

    async def create_thread(
        self,
        *,
        user_id: str,
        initial_message: str | None = None,
        title: str | None = None,
    ) -> ResearchThread:
        thread = ResearchThread(user_id=user_id, title=title)
        if initial_message:
            thread.add_message("user", initial_message)
            thread.state.question.text = initial_message
        return await self.repository.create(thread)

    async def get_thread(self, thread_id: str, user_id: str | None = None) -> ResearchThread | None:
        return await self.repository.get(thread_id, user_id=user_id)

    async def list_threads(self, user_id: str | None = None) -> list[ResearchThread]:
        return await self.repository.list(user_id=user_id)

    async def save_thread(self, thread: ResearchThread) -> ResearchThread:
        return await self.repository.save(thread)

    async def run_research(
        self,
        *,
        thread_id: str,
        user_id: str,
        message: str,
    ) -> tuple[ResearchThread, list[ResearchEvent]]:
        thread = await self.repository.get(thread_id, user_id=user_id)
        if not thread:
            raise KeyError("Research thread not found")
        model = self.model_factory.create()

        run_id = new_id("run")
        events = [
            ResearchEvent(
                type=ResearchEventType.RUN_STARTED,
                thread_id=thread.id,
                run_id=run_id,
                payload={"message": message},
            )
        ]
        thread.add_message("user", message)
        if self.model_factory.resolve_model_name() != "fake":
            events.append(
                ResearchEvent(
                    type=ResearchEventType.RUN_PROGRESS,
                    thread_id=thread.id,
                    run_id=run_id,
                    payload={"message": "Invoking configured chat model."},
                )
            )
            final_response = await model.ainvoke(
                [
                    {
                        "role": "system",
                        "content": (
                            "You are CoResearcher, a human-in-the-loop scientific research "
                            "assistant. Give a concise, evidence-aware next response."
                        ),
                    },
                    {"role": "user", "content": message},
                ]
            )
            thread.messages.append(ChatMessage(role="assistant", content=final_response))
            events.append(
                ResearchEvent(
                    type=ResearchEventType.FINAL_RESPONSE,
                    thread_id=thread.id,
                    run_id=run_id,
                    payload={"content": final_response},
                )
            )
            events.append(
                ResearchEvent(
                    type=ResearchEventType.RUN_COMPLETED,
                    thread_id=thread.id,
                    run_id=run_id,
                    payload={"final_response": final_response},
                )
            )
            await self.repository.save(thread)
            for event in events:
                self.event_store.append(event)
            return thread, events

        result = await self.graph.ainvoke(
            {
                "thread_id": thread.id,
                "run_id": run_id,
                "user_message": message,
                "research_state": thread.state,
                "events": events,
            }
        )
        thread.state = result["research_state"]
        final_response = result.get("final_response", "")
        if final_response:
            thread.messages.append(ChatMessage(role="assistant", content=final_response))

        if thread.state.claims or thread.state.evidence_items or thread.state.open_questions:
            artifact = create_research_brief(thread.state)
            thread.state.artifacts.append(artifact)
            result["events"].append(
                ResearchEvent(
                    type=ResearchEventType.ARTIFACT_CREATED,
                    thread_id=thread.id,
                    run_id=run_id,
                    payload={"artifact_id": artifact.id, "type": artifact.type.value},
                )
            )

        await self.repository.save(thread)
        for event in result["events"]:
            self.event_store.append(event)
        return thread, result["events"]

    async def stream_research(
        self,
        *,
        thread_id: str,
        user_id: str,
        message: str,
    ) -> AsyncIterator[ResearchEvent]:
        if self.model_factory.resolve_model_name() == "fake":
            _, events = await self.run_research(thread_id=thread_id, user_id=user_id, message=message)
            for event in events:
                yield event
            return

        thread = await self.repository.get(thread_id, user_id=user_id)
        if not thread:
            raise KeyError("Research thread not found")
        model = self.model_factory.create()
        run_id = new_id("run")

        async def emit(event: ResearchEvent) -> ResearchEvent:
            self.event_store.append(event)
            return event

        yield await emit(
            ResearchEvent(
                type=ResearchEventType.RUN_STARTED,
                thread_id=thread.id,
                run_id=run_id,
                payload={"message": message},
            )
        )
        thread.add_message("user", message)
        yield await emit(
            ResearchEvent(
                type=ResearchEventType.RUN_PROGRESS,
                thread_id=thread.id,
                run_id=run_id,
                payload={"message": "Streaming configured chat model."},
            )
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are CoResearcher, a human-in-the-loop scientific research "
                    "assistant. Give a concise, evidence-aware next response."
                ),
            },
            {"role": "user", "content": message},
        ]
        final_parts: list[str] = []
        if hasattr(model, "astream"):
            async for delta in model.astream(messages):
                final_parts.append(delta)
                yield await emit(
                    ResearchEvent(
                        type=ResearchEventType.FINAL_RESPONSE_DELTA,
                        thread_id=thread.id,
                        run_id=run_id,
                        payload={"content": delta},
                    )
                )
            final_response = "".join(final_parts)
        else:
            final_response = await model.ainvoke(messages)

        thread.messages.append(ChatMessage(role="assistant", content=final_response))
        yield await emit(
            ResearchEvent(
                type=ResearchEventType.FINAL_RESPONSE,
                thread_id=thread.id,
                run_id=run_id,
                payload={"content": final_response},
            )
        )
        yield await emit(
            ResearchEvent(
                type=ResearchEventType.RUN_COMPLETED,
                thread_id=thread.id,
                run_id=run_id,
                payload={"final_response": final_response},
            )
        )
        await self.repository.save(thread)

    async def get_artifact(self, thread_id: str, artifact_id: str, user_id: str) -> str | None:
        thread = await self.repository.get(thread_id, user_id=user_id)
        if not thread:
            return None
        artifact = next((item for item in thread.state.artifacts if item.id == artifact_id), None)
        return artifact.content if artifact else None

    def get_run_events(self, run_id: str) -> list[ResearchEvent]:
        return self.event_store.for_run(run_id)
