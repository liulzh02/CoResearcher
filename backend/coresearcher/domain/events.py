from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from coresearcher.domain.state import new_id, utc_now


class ResearchEventType(StrEnum):
    RUN_STARTED = "run.started"
    RUN_PROGRESS = "run.progress"
    RUN_COMPLETED = "run.completed"
    RUN_FAILED = "run.failed"
    SUBAGENT_STARTED = "subagent.started"
    SUBAGENT_COMPLETED = "subagent.completed"
    SUBAGENT_FAILED = "subagent.failed"
    SUBAGENT_TIMED_OUT = "subagent.timed_out"
    STATE_UPDATED = "state.updated"
    EVIDENCE_CREATED = "evidence.created"
    ARTIFACT_CREATED = "artifact.created"
    FINAL_RESPONSE_DELTA = "final.response.delta"
    FINAL_RESPONSE = "final.response"
    STRUCTURED_ERROR = "error.structured"


class ResearchEvent(BaseModel):
    id: str = Field(default_factory=lambda: new_id("evt"))
    type: ResearchEventType
    thread_id: str
    run_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    def to_sse(self) -> str:
        return f"event: {self.type.value}\ndata: {self.model_dump_json()}\n\n"


class EventStore(BaseModel):
    events: list[ResearchEvent] = Field(default_factory=list)

    def append(self, event: ResearchEvent) -> ResearchEvent:
        self.events.append(event)
        return event

    def for_run(self, run_id: str) -> list[ResearchEvent]:
        return [event for event in self.events if event.run_id == run_id]
