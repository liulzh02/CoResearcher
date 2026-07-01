from __future__ import annotations

from coresearcher.artifacts import create_research_brief
from coresearcher.domain.events import EventStore, ResearchEvent, ResearchEventType
from coresearcher.domain.state import ChatMessage, ResearchThread, new_id
from coresearcher.graph import make_research_director
from coresearcher.storage import InMemoryResearchRepository, ResearchRepository


class ResearchService:
    def __init__(
        self,
        repository: ResearchRepository | None = None,
        event_store: EventStore | None = None,
    ) -> None:
        self.repository = repository or InMemoryResearchRepository()
        self.event_store = event_store or EventStore()
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

    async def get_artifact(self, thread_id: str, artifact_id: str, user_id: str) -> str | None:
        thread = await self.repository.get(thread_id, user_id=user_id)
        if not thread:
            return None
        artifact = next((item for item in thread.state.artifacts if item.id == artifact_id), None)
        return artifact.content if artifact else None

    def get_run_events(self, run_id: str) -> list[ResearchEvent]:
        return self.event_store.for_run(run_id)

