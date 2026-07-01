from __future__ import annotations

from pydantic import BaseModel

from coresearcher.domain.state import ResearchState, ResearchThread


class CreateThreadRequest(BaseModel):
    initial_message: str | None = None
    title: str | None = None


class ThreadResponse(BaseModel):
    thread: ResearchThread


class ThreadListResponse(BaseModel):
    threads: list[ResearchThread]


class UpdateStateRequest(BaseModel):
    state: ResearchState


class RunResearchRequest(BaseModel):
    message: str


class RunResearchResponse(BaseModel):
    thread: ResearchThread
    run_id: str | None = None
    final_response: str | None = None


class StructuredError(BaseModel):
    error: str
    detail: str

