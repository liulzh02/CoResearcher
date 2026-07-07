from __future__ import annotations

import json
import logging
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
    THREAD_LOADED = "thread.loaded"
    THREAD_SAVED = "thread.saved"
    CONTEXT_BUILD_STARTED = "context.build.started"
    CONTEXT_BUILD_COMPLETED = "context.build.completed"
    CONTEXT_COMPRESSED = "context.compressed"
    MODEL_SELECTED = "model.selected"
    MODEL_REQUEST_STARTED = "model.request.started"
    MODEL_FIRST_TOKEN = "model.first_token"
    MODEL_REQUEST_COMPLETED = "model.request.completed"
    DIRECTOR_ROUTE_SELECTED = "director.route.selected"
    DIRECTOR_PLAN_CREATED = "director.plan.created"
    DIRECTOR_SYNTHESIS_STARTED = "director.synthesis.started"
    SUBAGENT_STARTED = "subagent.started"
    SUBAGENT_PROGRESS = "subagent.progress"
    SUBAGENT_COMPLETED = "subagent.completed"
    SUBAGENT_FAILED = "subagent.failed"
    SUBAGENT_TIMED_OUT = "subagent.timed_out"
    TOOL_STARTED = "tool.started"
    TOOL_OUTPUT = "tool.output"
    TOOL_COMPLETED = "tool.completed"
    TOOL_FAILED = "tool.failed"
    STATE_UPDATED = "state.updated"
    EVIDENCE_CREATED = "evidence.created"
    ARTIFACT_CREATED = "artifact.created"
    MEMORY_CANDIDATE_CREATED = "memory.candidate.created"
    DEBUG_LOG = "debug.log"
    DEBUG_METRIC = "debug.metric"
    DEBUG_WARNING = "debug.warning"
    FINAL_RESPONSE_DELTA = "final.response.delta"
    FINAL_RESPONSE = "final.response"
    STRUCTURED_ERROR = "error.structured"


class ResearchEventPhase(StrEnum):
    RUN = "run"
    THREAD = "thread"
    CONTEXT = "context"
    MODEL = "model"
    DIRECTOR = "director"
    SUBAGENT = "subagent"
    TOOL = "tool"
    STATE = "state"
    ARTIFACT = "artifact"
    MEMORY = "memory"
    ASSISTANT = "assistant"
    DEBUG = "debug"
    ERROR = "error"


class ResearchEventStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WARNING = "warning"


class ResearchEventLevel(StrEnum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ResearchEvent(BaseModel):
    id: str = Field(default_factory=lambda: new_id("evt"))
    type: ResearchEventType
    thread_id: str
    run_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    phase: ResearchEventPhase | None = None
    level: ResearchEventLevel = ResearchEventLevel.INFO
    status: ResearchEventStatus | None = None
    title: str | None = None
    message: str | None = None
    parent_id: str | None = None
    sequence: int | None = None
    duration_ms: int | None = None

    def to_sse(self) -> str:
        return f"event: {self.type.value}\ndata: {self.model_dump_json()}\n\n"

    def with_trace_defaults(self, sequence: int | None = None) -> "ResearchEvent":
        update: dict[str, Any] = {}
        if sequence is not None and self.sequence is None:
            update["sequence"] = sequence
        if self.phase is None:
            update["phase"] = _phase_for_type(self.type)
        if self.status is None:
            update["status"] = _status_for_type(self.type)
        if self.level == ResearchEventLevel.INFO and self.type in {
            ResearchEventType.RUN_FAILED,
            ResearchEventType.SUBAGENT_FAILED,
            ResearchEventType.TOOL_FAILED,
            ResearchEventType.STRUCTURED_ERROR,
        }:
            update["level"] = ResearchEventLevel.ERROR
        if self.title is None:
            update["title"] = _title_for_type(self.type)
        if self.message is None:
            update["message"] = _message_for_event(self)
        return self.model_copy(update=update)

    def safe_log_record(self) -> dict[str, Any]:
        return {
            "event": "research_event",
            "event_id": self.id,
            "event_type": self.type.value,
            "run_id": self.run_id,
            "thread_id": self.thread_id,
            "sequence": self.sequence,
            "phase": self.phase.value if self.phase else None,
            "status": self.status.value if self.status else None,
            "level": self.level.value,
            "title": self.title,
            "message": self.message,
            "duration_ms": self.duration_ms,
            "parent_id": self.parent_id,
        }


class EventStore(BaseModel):
    events: list[ResearchEvent] = Field(default_factory=list)

    def append(self, event: ResearchEvent) -> ResearchEvent:
        self.events.append(event)
        return event

    def for_run(self, run_id: str) -> list[ResearchEvent]:
        return [event for event in self.events if event.run_id == run_id]

    def next_sequence(self, run_id: str) -> int:
        sequences = [event.sequence or 0 for event in self.events if event.run_id == run_id]
        return (max(sequences) if sequences else 0) + 1


class RunEventEmitter:
    def __init__(
        self,
        store: EventStore,
        logger: logging.Logger | None = None,
    ) -> None:
        self.store = store
        self.logger = logger or logging.getLogger("coresearcher.events")

    def emit(self, event: ResearchEvent) -> ResearchEvent:
        enriched = event.with_trace_defaults(sequence=self.store.next_sequence(event.run_id))
        self.store.append(enriched)
        self.logger.info(json.dumps(enriched.safe_log_record(), ensure_ascii=True, sort_keys=True))
        return enriched

    def enrich(self, event: ResearchEvent) -> ResearchEvent:
        return event.with_trace_defaults(sequence=self.store.next_sequence(event.run_id))


def _phase_for_type(event_type: ResearchEventType) -> ResearchEventPhase:
    prefix = event_type.value.split(".", 1)[0]
    if prefix == "final":
        return ResearchEventPhase.ASSISTANT
    try:
        return ResearchEventPhase(prefix)
    except ValueError:
        return ResearchEventPhase.RUN


def _status_for_type(event_type: ResearchEventType) -> ResearchEventStatus:
    value = event_type.value
    if value.endswith(".started") or value.endswith(".progress") or value.endswith(".delta"):
        return ResearchEventStatus.RUNNING
    if value.endswith(".failed") or event_type == ResearchEventType.STRUCTURED_ERROR:
        return ResearchEventStatus.FAILED
    if value.endswith(".warning"):
        return ResearchEventStatus.WARNING
    return ResearchEventStatus.COMPLETED


def _title_for_type(event_type: ResearchEventType) -> str:
    titles = {
        ResearchEventType.RUN_STARTED: "Run started",
        ResearchEventType.RUN_COMPLETED: "Run completed",
        ResearchEventType.RUN_FAILED: "Run failed",
        ResearchEventType.THREAD_LOADED: "Thread loaded",
        ResearchEventType.THREAD_SAVED: "Thread saved",
        ResearchEventType.CONTEXT_BUILD_STARTED: "Building context",
        ResearchEventType.CONTEXT_BUILD_COMPLETED: "Context ready",
        ResearchEventType.CONTEXT_COMPRESSED: "Context compressed",
        ResearchEventType.MODEL_SELECTED: "Model selected",
        ResearchEventType.MODEL_REQUEST_STARTED: "Calling model",
        ResearchEventType.MODEL_FIRST_TOKEN: "First token received",
        ResearchEventType.MODEL_REQUEST_COMPLETED: "Model response complete",
        ResearchEventType.DIRECTOR_ROUTE_SELECTED: "Director route selected",
        ResearchEventType.DIRECTOR_PLAN_CREATED: "Director plan created",
        ResearchEventType.DIRECTOR_SYNTHESIS_STARTED: "Synthesizing response",
        ResearchEventType.SUBAGENT_STARTED: "Subagent started",
        ResearchEventType.SUBAGENT_PROGRESS: "Subagent progress",
        ResearchEventType.SUBAGENT_COMPLETED: "Subagent completed",
        ResearchEventType.SUBAGENT_FAILED: "Subagent failed",
        ResearchEventType.SUBAGENT_TIMED_OUT: "Subagent timed out",
        ResearchEventType.STATE_UPDATED: "State updated",
        ResearchEventType.EVIDENCE_CREATED: "Evidence created",
        ResearchEventType.ARTIFACT_CREATED: "Artifact created",
        ResearchEventType.MEMORY_CANDIDATE_CREATED: "Memory candidate created",
        ResearchEventType.FINAL_RESPONSE_DELTA: "Assistant response delta",
        ResearchEventType.FINAL_RESPONSE: "Assistant response complete",
        ResearchEventType.STRUCTURED_ERROR: "Structured error",
    }
    return titles.get(event_type, event_type.value.replace(".", " ").title())


def _message_for_event(event: ResearchEvent) -> str | None:
    for key in ("message", "detail", "summary", "result_summary", "final_response"):
        value = event.payload.get(key)
        if isinstance(value, str):
            return value
    if event.type == ResearchEventType.FINAL_RESPONSE_DELTA:
        return None
    content = event.payload.get("content")
    if isinstance(content, str) and event.type == ResearchEventType.FINAL_RESPONSE:
        return "Assistant response is complete."
    return event.title or _title_for_type(event.type)
