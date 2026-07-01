from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from coresearcher.domain.state import new_id, utc_now


class MemoryScope(StrEnum):
    GLOBAL = "global"
    RESEARCH = "research"


class MemoryFileType(StrEnum):
    USER_MEMORY = "user_memory"
    RESEARCH_MEMORY = "research_memory"
    CANDIDATES = "candidates"


class MemoryRecordType(StrEnum):
    USER_PREFERENCE = "user_preference"
    PROJECT_FACT = "project_fact"
    DECISION = "decision"
    RESEARCH_GOAL = "research_goal"
    METHOD_PREFERENCE = "method_preference"
    OPEN_QUESTION = "open_question"


class MemoryFileStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    INVALID = "invalid"


class CandidateStatus(StrEnum):
    PENDING = "pending"
    PROMOTED = "promoted"
    REJECTED = "rejected"
    CONFLICTING = "conflicting"
    INVALID = "invalid"


class ProvenanceReference(BaseModel):
    type: str
    id: str
    path_or_url: str | None = None
    note: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryFrontmatter(BaseModel):
    scope: MemoryScope
    type: MemoryFileType
    version: int = 1
    status: MemoryFileStatus = MemoryFileStatus.ACTIVE
    id: str = Field(default_factory=lambda: new_id("memfile"))
    user_id: str | None = None
    research_id: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_scope_fields(self) -> MemoryFrontmatter:
        if self.scope == MemoryScope.RESEARCH and not self.research_id:
            raise ValueError("research memory requires research_id")
        return self


class MemoryValidationResult(BaseModel):
    valid: bool
    warnings: list[str] = Field(default_factory=list)


class MemoryFile(BaseModel):
    frontmatter: MemoryFrontmatter
    body: str
    path: str | None = None
    validation: MemoryValidationResult = Field(
        default_factory=lambda: MemoryValidationResult(valid=True)
    )


class CandidateMemoryEntry(BaseModel):
    id: str = Field(default_factory=lambda: new_id("memcand"))
    text: str
    target_scope: MemoryScope
    record_type: MemoryRecordType
    confidence: float = Field(ge=0.0, le=1.0)
    provenance: list[ProvenanceReference] = Field(default_factory=list)
    status: CandidateStatus = CandidateStatus.PENDING
    research_id: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    conflict_reason: str | None = None

    @model_validator(mode="after")
    def validate_target_scope(self) -> CandidateMemoryEntry:
        if self.target_scope == MemoryScope.RESEARCH and not self.research_id:
            raise ValueError("research-scoped candidate requires research_id")
        return self


class MemoryExtractionOutput(BaseModel):
    candidates: list[CandidateMemoryEntry] = Field(default_factory=list)

