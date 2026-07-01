from __future__ import annotations

from collections.abc import AsyncIterator

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
from coresearcher.models import ModelFactory
from coresearcher.services import ResearchService
from coresearcher.subagents import default_subagent_registry
from coresearcher.tools import default_tool_registry


def _get_user_id(request: Request) -> str:
    settings: AppSettings = request.app.state.settings
    return request.headers.get("x-user-id", settings.security.default_user_id)


def _service(request: Request) -> ResearchService:
    return request.app.state.research_service


def _safe_error(exc: Exception) -> StructuredError:
    return StructuredError(error=exc.__class__.__name__, detail=str(exc)[:300])


def create_app() -> FastAPI:
    settings = load_settings()
    app = FastAPI(title=settings.gateway.title)
    app.state.settings = settings
    app.state.research_service = ResearchService()
    app.state.kb = FakeKnowledgeBaseAdapter()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/models")
    async def models() -> dict:
        factory = ModelFactory()
        return {"models": list(factory.config.models.values())}

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
                _, events = await service.run_research(
                    thread_id=thread_id,
                    user_id=user_id,
                    message=body.message,
                )
                for event in events:
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

    return app
