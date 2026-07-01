from __future__ import annotations

from enum import IntEnum, StrEnum
from typing import Any

from pydantic import BaseModel, Field


class CompressionLevel(IntEnum):
    LEVEL_0 = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5


class ContextSectionType(StrEnum):
    STABLE_RULES = "stable_rules"
    RUNTIME_RULES = "runtime_rules"
    HISTORY = "history"
    RESEARCH_STATE = "research_state"
    MEMORY = "memory"
    EVIDENCE = "evidence"
    TOOL_OUTPUT = "tool_output"
    SKILL_CONTEXT = "skill_context"
    OMITTED_CONTEXT = "omitted_context"
    SUBAGENT_TASK = "subagent_task"
    LATEST_USER_MESSAGE = "latest_user_message"


class ContextSourceLocator(BaseModel):
    type: str
    id: str | None = None
    path_or_url: str | None = None
    title: str | None = None
    hash: str | None = None
    page_range: str | None = None
    line_range: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class OmittedContextRecord(BaseModel):
    reason: str
    source_locator: ContextSourceLocator
    estimated_tokens: int = 0
    recovery_metadata: dict[str, Any] = Field(default_factory=dict)


class ContextSection(BaseModel):
    type: ContextSectionType
    content: str
    source_locators: list[ContextSourceLocator] = Field(default_factory=list)
    estimated_tokens: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class LatestUserMessage(BaseModel):
    content: str
    message_id: str | None = None


class ContextBuildMetadata(BaseModel):
    compression_level: CompressionLevel = CompressionLevel.LEVEL_0
    prompt_budget: int = 0
    completion_reserve: int = 0
    context_window_occupancy: float = 0.0
    over_context_window: bool = False
    section_token_estimates: dict[str, int] = Field(default_factory=dict)
    source_locator_count: int = 0
    omitted_context: list[OmittedContextRecord] = Field(default_factory=list)
    retrieval_query: str = ""


class MessageRecord(BaseModel):
    id: str
    role: str
    content: str


class LongDocument(BaseModel):
    title: str
    content: str
    locator: ContextSourceLocator
    snippet: str | None = None


class ToolOutputRecord(BaseModel):
    id: str
    content: str
    locator: ContextSourceLocator


class ContextPack(BaseModel):
    sections: list[ContextSection]
    latest_user_message: LatestUserMessage
    metadata: ContextBuildMetadata

    def render_messages(self) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        for section in self.sections:
            if section.type == ContextSectionType.LATEST_USER_MESSAGE:
                messages.append({"role": "user", "content": self.latest_user_message.content})
            elif section.type == ContextSectionType.STABLE_RULES:
                messages.append({"role": "system", "content": section.content})
            else:
                messages.append({"role": "user", "content": section.content})
        return messages
