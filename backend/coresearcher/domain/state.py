from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def utc_now() -> datetime:
    return datetime.now(UTC)


class SourceType(StrEnum):
    PAPER = "paper"
    URL = "url"
    FILE = "file"
    USER_ASSUMPTION = "user_assumption"
    TOOL_CALL = "tool_call"
    KNOWLEDGE_BASE_NOTE = "knowledge_base_note"
    ARTIFACT = "artifact"


class ExtractionStatus(StrEnum):
    PENDING = "pending"
    EXTRACTED = "extracted"
    FAILED = "failed"
    NOT_REQUIRED = "not_required"


class ClaimStatus(StrEnum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    ASSUMPTION = "assumption"
    CHALLENGED = "challenged"


class ArtifactType(StrEnum):
    RESEARCH_BRIEF = "research_brief"
    READING_NOTE = "reading_note"
    EVIDENCE_MAP = "evidence_map"
    CODE_RESULT = "code_result"
    OTHER = "other"


class SourceLocator(BaseModel):
    type: SourceType = SourceType.URL
    id: str | None = None
    path_or_url: str | None = None
    title: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    hash: str | None = None
    page_range: str | None = None
    line_range: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResearchQuestion(BaseModel):
    text: str = ""
    domain: str | None = None
    expected_output: str | None = None
    constraints: list[str] = Field(default_factory=list)


class ResearchScope(BaseModel):
    includes: list[str] = Field(default_factory=list)
    excludes: list[str] = Field(default_factory=list)
    time_horizon: str | None = None


class Hypothesis(BaseModel):
    id: str = Field(default_factory=lambda: new_id("hyp"))
    text: str
    rationale: str | None = None
    status: str = "candidate"
    created_at: datetime = Field(default_factory=utc_now)


class PaperRecord(BaseModel):
    id: str = Field(default_factory=lambda: new_id("paper"))
    title: str
    authors: list[str] = Field(default_factory=list)
    venue_or_source: str | None = None
    year: int | None = None
    locator: SourceLocator
    extraction_status: ExtractionStatus = ExtractionStatus.PENDING
    quality_signals: dict[str, Any] = Field(default_factory=dict)
    knowledge_base_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class EvidenceItem(BaseModel):
    id: str = Field(default_factory=lambda: new_id("ev"))
    summary: str
    source_locator: SourceLocator | None = None
    paper_id: str | None = None
    quote: str | None = None
    quality_signals: dict[str, Any] = Field(default_factory=dict)
    extraction_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    user_provided_assumption: bool = False
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def require_source_or_assumption(self) -> EvidenceItem:
        if not self.source_locator and not self.user_provided_assumption:
            raise ValueError("Evidence requires a source locator or user_provided_assumption=true")
        return self


class Claim(BaseModel):
    id: str = Field(default_factory=lambda: new_id("claim"))
    text: str
    evidence_ids: list[str] = Field(default_factory=list)
    critique_note_ids: list[str] = Field(default_factory=list)
    user_provided_assumption: bool = False
    status: ClaimStatus = ClaimStatus.SUPPORTED
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def require_support(self) -> Claim:
        if not self.evidence_ids and not self.critique_note_ids and not self.user_provided_assumption:
            raise ValueError(
                "Durable claims require evidence, critique, or explicit user assumption"
            )
        if self.user_provided_assumption and not self.evidence_ids:
            self.status = ClaimStatus.ASSUMPTION
        return self


class OpenQuestion(BaseModel):
    id: str = Field(default_factory=lambda: new_id("oq"))
    text: str
    source: str | None = None
    priority: str = "normal"
    status: str = "open"
    created_at: datetime = Field(default_factory=utc_now)


class Decision(BaseModel):
    id: str = Field(default_factory=lambda: new_id("dec"))
    text: str
    rationale: str
    option_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    critique_note_ids: list[str] = Field(default_factory=list)
    approved_by_user: bool = False
    created_at: datetime = Field(default_factory=utc_now)


class CritiqueNote(BaseModel):
    id: str = Field(default_factory=lambda: new_id("crit"))
    text: str
    challenged_claim_ids: list[str] = Field(default_factory=list)
    challenged_evidence_ids: list[str] = Field(default_factory=list)
    severity: str = "medium"
    created_at: datetime = Field(default_factory=utc_now)


class ArtifactRecord(BaseModel):
    id: str = Field(default_factory=lambda: new_id("art"))
    type: ArtifactType = ArtifactType.OTHER
    title: str
    content: str
    claim_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    decision_ids: list[str] = Field(default_factory=list)
    critique_note_ids: list[str] = Field(default_factory=list)
    source_locators: list[SourceLocator] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class TodoItem(BaseModel):
    id: str = Field(default_factory=lambda: new_id("todo"))
    text: str
    status: str = "open"
    owner: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: new_id("msg"))
    role: str
    content: str
    created_at: datetime = Field(default_factory=utc_now)


class ResearchState(BaseModel):
    question: ResearchQuestion = Field(default_factory=ResearchQuestion)
    scope: ResearchScope = Field(default_factory=ResearchScope)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    papers: list[PaperRecord] = Field(default_factory=list)
    evidence_items: list[EvidenceItem] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    open_questions: list[OpenQuestion] = Field(default_factory=list)
    decisions: list[Decision] = Field(default_factory=list)
    critique_notes: list[CritiqueNote] = Field(default_factory=list)
    artifacts: list[ArtifactRecord] = Field(default_factory=list)
    todos: list[TodoItem] = Field(default_factory=list)
    knowledge_base_links: dict[str, list[str]] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=utc_now)

    def touch(self) -> None:
        self.updated_at = utc_now()


class ResearchThread(BaseModel):
    id: str = Field(default_factory=lambda: new_id("thread"))
    user_id: str
    title: str | None = None
    messages: list[ChatMessage] = Field(default_factory=list)
    state: ResearchState = Field(default_factory=ResearchState)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    def add_message(self, role: str, content: str) -> ChatMessage:
        message = ChatMessage(role=role, content=content)
        self.messages.append(message)
        if role == "user" and not self.title:
            self.title = content[:80]
        self.updated_at = utc_now()
        return message

