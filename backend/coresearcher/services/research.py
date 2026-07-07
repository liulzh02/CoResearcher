from __future__ import annotations

from collections.abc import AsyncIterator
from time import monotonic

from coresearcher.artifacts import create_research_brief
from coresearcher.domain.events import EventStore, ResearchEvent, ResearchEventType, RunEventEmitter
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
        self.event_emitter = RunEventEmitter(self.event_store)
        self.model_factory = model_factory or ModelFactory()
        self.graph = make_research_director()

    def _emit(self, event: ResearchEvent) -> ResearchEvent:
        return self.event_emitter.emit(event)

    def _record_events(self, events: list[ResearchEvent]) -> list[ResearchEvent]:
        return [self._emit(event) for event in events]

    def _safe_user_payload(self, message: str) -> dict[str, str | int]:
        return {"message": message[:240], "message_length": len(message)}

    def _model_messages(self, message: str) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": (
                    "You are CoResearcher, a human-in-the-loop scientific research "
                    "assistant. Give a concise, evidence-aware next response."
                ),
            },
            {"role": "user", "content": message},
        ]

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
                payload=self._safe_user_payload(message),
            )
        ]
        thread.add_message("user", message)
        if self.model_factory.resolve_model_name() != "fake":
            model_key = self.model_factory.resolve_model_name()
            model_config = self.model_factory.get_config()
            events.append(
                ResearchEvent(
                    type=ResearchEventType.THREAD_LOADED,
                    thread_id=thread.id,
                    run_id=run_id,
                    payload={"message_count": len(thread.messages)},
                )
            )
            events.append(
                ResearchEvent(
                    type=ResearchEventType.MODEL_SELECTED,
                    thread_id=thread.id,
                    run_id=run_id,
                    payload={"model_id": model_key, "model_name": model_config.name},
                )
            )
            events.append(
                ResearchEvent(
                    type=ResearchEventType.MODEL_REQUEST_STARTED,
                    thread_id=thread.id,
                    run_id=run_id,
                    payload={"model_id": model_key, "model_name": model_config.name},
                )
            )
            model_started = monotonic()
            final_response = await model.ainvoke(
                self._model_messages(message)
            )
            duration_ms = int((monotonic() - model_started) * 1000)
            events.append(
                ResearchEvent(
                    type=ResearchEventType.MODEL_REQUEST_COMPLETED,
                    thread_id=thread.id,
                    run_id=run_id,
                    payload={"model_id": model_key, "response_length": len(final_response)},
                    duration_ms=duration_ms,
                )
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
            events.append(
                ResearchEvent(
                    type=ResearchEventType.THREAD_SAVED,
                    thread_id=thread.id,
                    run_id=run_id,
                    payload={"message_count": len(thread.messages)},
                )
            )
            return thread, self._record_events(events)

        events.append(
            ResearchEvent(
                type=ResearchEventType.THREAD_LOADED,
                thread_id=thread.id,
                run_id=run_id,
                payload={"message_count": len(thread.messages)},
            )
        )
        events.append(
            ResearchEvent(
                type=ResearchEventType.CONTEXT_BUILD_STARTED,
                thread_id=thread.id,
                run_id=run_id,
                payload={"message": "Building director context."},
            )
        )
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
        result["events"].append(
            ResearchEvent(
                type=ResearchEventType.THREAD_SAVED,
                thread_id=thread.id,
                run_id=run_id,
                payload={"message_count": len(thread.messages)},
            )
        )
        return thread, self._record_events(result["events"])

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
        model_key = self.model_factory.resolve_model_name()
        model_config = self.model_factory.get_config()
        run_id = new_id("run")

        run_started = monotonic()
        yield self._emit(
            ResearchEvent(
                type=ResearchEventType.RUN_STARTED,
                thread_id=thread.id,
                run_id=run_id,
                payload=self._safe_user_payload(message),
            )
        )
        thread.add_message("user", message)
        yield self._emit(
            ResearchEvent(
                type=ResearchEventType.THREAD_LOADED,
                thread_id=thread.id,
                run_id=run_id,
                payload={"message_count": len(thread.messages)},
            )
        )
        yield self._emit(
            ResearchEvent(
                type=ResearchEventType.MODEL_SELECTED,
                thread_id=thread.id,
                run_id=run_id,
                payload={"model_id": model_key, "model_name": model_config.name},
            )
        )
        yield self._emit(
            ResearchEvent(
                type=ResearchEventType.MODEL_REQUEST_STARTED,
                thread_id=thread.id,
                run_id=run_id,
                payload={"model_id": model_key, "model_name": model_config.name},
            )
        )

        messages = self._model_messages(message)
        final_parts: list[str] = []
        model_started = monotonic()
        first_token_seen = False
        try:
            if hasattr(model, "astream"):
                async for delta in model.astream(messages):
                    if not first_token_seen:
                        first_token_seen = True
                        yield self._emit(
                            ResearchEvent(
                                type=ResearchEventType.MODEL_FIRST_TOKEN,
                                thread_id=thread.id,
                                run_id=run_id,
                                payload={"model_id": model_key},
                                duration_ms=int((monotonic() - model_started) * 1000),
                            )
                        )
                    final_parts.append(delta)
                    yield self._emit(
                        ResearchEvent(
                            type=ResearchEventType.FINAL_RESPONSE_DELTA,
                            thread_id=thread.id,
                            run_id=run_id,
                            payload={"content": delta, "is_assistant_delta": True},
                        )
                    )
                final_response = "".join(final_parts)
            else:
                final_response = await model.ainvoke(messages)
        except Exception as exc:
            yield self._emit(
                ResearchEvent(
                    type=ResearchEventType.RUN_FAILED,
                    thread_id=thread.id,
                    run_id=run_id,
                    payload={
                        "error": exc.__class__.__name__,
                        "detail": str(exc)[:240],
                        "subsystem": "model",
                    },
                    duration_ms=int((monotonic() - run_started) * 1000),
                )
            )
            return
        model_duration_ms = int((monotonic() - model_started) * 1000)

        yield self._emit(
            ResearchEvent(
                type=ResearchEventType.MODEL_REQUEST_COMPLETED,
                thread_id=thread.id,
                run_id=run_id,
                payload={
                    "model_id": model_key,
                    "response_length": len(final_response),
                    "delta_count": len(final_parts),
                },
                duration_ms=model_duration_ms,
            )
        )

        thread.messages.append(ChatMessage(role="assistant", content=final_response))
        yield self._emit(
            ResearchEvent(
                type=ResearchEventType.FINAL_RESPONSE,
                thread_id=thread.id,
                run_id=run_id,
                payload={"content": final_response},
            )
        )
        await self.repository.save(thread)
        yield self._emit(
            ResearchEvent(
                type=ResearchEventType.THREAD_SAVED,
                thread_id=thread.id,
                run_id=run_id,
                payload={"message_count": len(thread.messages)},
            )
        )
        yield self._emit(
            ResearchEvent(
                type=ResearchEventType.RUN_COMPLETED,
                thread_id=thread.id,
                run_id=run_id,
                payload={"final_response": final_response},
                duration_ms=int((monotonic() - run_started) * 1000),
            )
        )

    async def get_artifact(self, thread_id: str, artifact_id: str, user_id: str) -> str | None:
        thread = await self.repository.get(thread_id, user_id=user_id)
        if not thread:
            return None
        artifact = next((item for item in thread.state.artifacts if item.id == artifact_id), None)
        return artifact.content if artifact else None

    def get_run_events(self, run_id: str) -> list[ResearchEvent]:
        return self.event_store.for_run(run_id)
