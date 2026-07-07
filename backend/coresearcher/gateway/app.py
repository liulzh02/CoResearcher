from __future__ import annotations

import os
from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse

from coresearcher import __version__
from coresearcher.config import AppSettings, load_settings
from coresearcher.gateway.schemas import (
    CreateThreadRequest,
    RunResearchRequest,
    RunResearchResponse,
    StructuredError,
    ThreadListResponse,
    ThreadResponse,
    UpdateStateRequest,
)
from coresearcher.knowledge_base import FakeKnowledgeBaseAdapter, KnowledgeBaseNote
from coresearcher.memory import MemoryRecordType, MemoryScope, MemoryService, ProvenanceReference
from coresearcher.memory.config import MemorySettings
from coresearcher.models import ModelFactory
from coresearcher.services import ResearchService
from coresearcher.subagents import default_subagent_registry
from coresearcher.tools import default_tool_registry


def _get_user_id(request: Request) -> str:
    settings: AppSettings = request.app.state.settings
    return request.headers.get("x-user-id", settings.security.default_user_id)


def _service(request: Request) -> ResearchService:
    return request.app.state.research_service


def _memory_service(request: Request) -> MemoryService:
    return request.app.state.memory_service


def _model_factory(request: Request) -> ModelFactory:
    return request.app.state.model_factory


def _safe_error(exc: Exception) -> StructuredError:
    return StructuredError(error=exc.__class__.__name__, detail=str(exc)[:300])


def create_app() -> FastAPI:
    settings = load_settings()
    app = FastAPI(title=settings.gateway.title)
    app.state.settings = settings
    app.state.model_factory = ModelFactory(settings.models)
    app.state.research_service = ResearchService(model_factory=app.state.model_factory)
    app.state.kb = FakeKnowledgeBaseAdapter()
    memory_root = Path(os.getenv("CORESEARCHER_MEMORY_ROOT", "memory"))
    sqlite_path = os.getenv("CORESEARCHER_MEMORY_SQLITE_PATH")
    app.state.memory_service = MemoryService(
        settings=MemorySettings(
            memory_root=memory_root,
            sqlite_path=Path(sqlite_path) if sqlite_path else None,
        ),
        knowledge_base=app.state.kb,
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/models")
    async def models(factory: ModelFactory = Depends(_model_factory)) -> dict:
        return factory.list_model_status()

    @app.get("/tools")
    async def tools() -> dict:
        return {"tools": default_tool_registry().list()}

    @app.get("/subagents")
    async def subagents() -> dict:
        return {"subagents": default_subagent_registry().list()}

    @app.post("/research/threads", response_model=ThreadResponse)
    async def create_thread(
        body: CreateThreadRequest,
        service: ResearchService = Depends(_service),
        user_id: str = Depends(_get_user_id),
    ) -> ThreadResponse:
        thread = await service.create_thread(
            user_id=user_id,
            initial_message=body.initial_message,
            title=body.title,
        )
        return ThreadResponse(thread=thread)

    @app.get("/research/threads", response_model=ThreadListResponse)
    async def list_threads(
        service: ResearchService = Depends(_service),
        user_id: str = Depends(_get_user_id),
    ) -> ThreadListResponse:
        return ThreadListResponse(threads=await service.list_threads(user_id=user_id))

    @app.get("/research/threads/{thread_id}", response_model=ThreadResponse)
    async def get_thread(
        thread_id: str,
        service: ResearchService = Depends(_service),
        user_id: str = Depends(_get_user_id),
    ) -> ThreadResponse:
        thread = await service.get_thread(thread_id, user_id=user_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Research thread not found")
        return ThreadResponse(thread=thread)

    @app.get("/research/threads/{thread_id}/messages")
    async def get_messages(
        thread_id: str,
        service: ResearchService = Depends(_service),
        user_id: str = Depends(_get_user_id),
    ) -> dict:
        thread = await service.get_thread(thread_id, user_id=user_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Research thread not found")
        return {"messages": thread.messages}

    @app.put("/research/threads/{thread_id}/state", response_model=ThreadResponse)
    async def update_state(
        thread_id: str,
        body: UpdateStateRequest,
        service: ResearchService = Depends(_service),
        user_id: str = Depends(_get_user_id),
    ) -> ThreadResponse:
        thread = await service.get_thread(thread_id, user_id=user_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Research thread not found")
        thread.state = body.state
        await service.save_thread(thread)
        return ThreadResponse(thread=thread)

    @app.post("/research/threads/{thread_id}/runs", response_model=RunResearchResponse)
    async def run_research(
        thread_id: str,
        body: RunResearchRequest,
        service: ResearchService = Depends(_service),
        user_id: str = Depends(_get_user_id),
    ) -> RunResearchResponse:
        try:
            thread, events = await service.run_research(
                thread_id=thread_id,
                user_id=user_id,
                message=body.message,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Research thread not found") from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        final_event = next((event for event in reversed(events) if event.type.value == "final.response"), None)
        run_id = events[0].run_id if events else None
        return RunResearchResponse(
            thread=thread,
            run_id=run_id,
            final_response=final_event.payload.get("content") if final_event else None,
        )

    @app.post("/research/threads/{thread_id}/runs/stream")
    async def stream_run(
        thread_id: str,
        body: RunResearchRequest,
        service: ResearchService = Depends(_service),
        user_id: str = Depends(_get_user_id),
    ) -> StreamingResponse:
        async def generate() -> AsyncIterator[str]:
            try:
                async for event in service.stream_research(
                    thread_id=thread_id,
                    user_id=user_id,
                    message=body.message,
                ):
                    yield event.to_sse()
            except Exception as exc:
                safe = _safe_error(exc)
                yield f"event: error.structured\ndata: {safe.model_dump_json()}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    @app.get("/research/runs/{run_id}/events")
    async def get_run_events(
        run_id: str,
        service: ResearchService = Depends(_service),
    ) -> dict:
        return {"events": service.get_run_events(run_id)}

    @app.get("/research/threads/{thread_id}/artifacts/{artifact_id}")
    async def get_artifact(
        thread_id: str,
        artifact_id: str,
        service: ResearchService = Depends(_service),
        user_id: str = Depends(_get_user_id),
    ) -> dict[str, str]:
        content = await service.get_artifact(thread_id, artifact_id, user_id=user_id)
        if content is None:
            raise HTTPException(status_code=404, detail="Artifact not found")
        return {"content": content}

    @app.get("/research/threads/{thread_id}/evidence")
    async def get_evidence(
        thread_id: str,
        service: ResearchService = Depends(_service),
        user_id: str = Depends(_get_user_id),
    ) -> dict:
        thread = await service.get_thread(thread_id, user_id=user_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Research thread not found")
        return {"evidence_items": thread.state.evidence_items, "claims": thread.state.claims}

    @app.get("/knowledge-base/notes")
    async def list_kb_notes(request: Request) -> dict:
        notes = await request.app.state.kb.list_notes()
        return {"notes": notes}

    @app.post("/knowledge-base/notes")
    async def write_kb_note(note: KnowledgeBaseNote, request: Request) -> dict:
        return {"note": await request.app.state.kb.write_note(note)}

    @app.get("/memory/global")
    async def get_global_memory(
        memory: MemoryService = Depends(_memory_service),
    ) -> dict:
        return {"memory": memory.store.load_global_memory()}

    @app.get("/memory/research/{research_id}")
    async def get_research_memory(
        research_id: str,
        memory: MemoryService = Depends(_memory_service),
    ) -> dict:
        return {"memory": memory.store.load_research_memory(research_id)}

    @app.get("/memory/research/{research_id}/candidates")
    async def get_research_candidates(
        research_id: str,
        memory: MemoryService = Depends(_memory_service),
    ) -> dict:
        return {"candidates": memory.store.load_candidates(MemoryScope.RESEARCH, research_id)}

    @app.post("/memory/candidates")
    async def create_memory_candidate(
        body: dict,
        memory: MemoryService = Depends(_memory_service),
    ) -> dict:
        provenance = [
            ProvenanceReference.model_validate(item)
            for item in body.get("provenance", [])
        ]
        candidate = memory.create_candidate(
            text=body["text"],
            target_scope=MemoryScope(body["target_scope"]),
            record_type=MemoryRecordType(body["record_type"]),
            confidence=body.get("confidence", 0.5),
            provenance=provenance,
            research_id=body.get("research_id"),
        )
        return {"candidate": candidate}

    @app.post("/memory/candidates/{candidate_id}/promote")
    async def promote_memory_candidate(
        candidate_id: str,
        memory: MemoryService = Depends(_memory_service),
    ) -> dict:
        return {"candidate": memory.promote_candidate(candidate_id)}

    @app.post("/memory/candidates/{candidate_id}/reject")
    async def reject_memory_candidate(
        candidate_id: str,
        memory: MemoryService = Depends(_memory_service),
    ) -> dict:
        return {"candidate": memory.reject_candidate(candidate_id)}

    @app.get("/memory/research/{research_id}/inspect")
    async def inspect_memory(
        research_id: str,
        query: str = "",
        memory: MemoryService = Depends(_memory_service),
    ) -> dict:
        return await memory.inspect_memory(research_id=research_id, query=query)

    return app
