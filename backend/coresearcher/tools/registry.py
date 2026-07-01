from __future__ import annotations

from enum import StrEnum
from typing import Callable

from pydantic import BaseModel, Field


class ToolGroup(StrEnum):
    SEARCH = "search"
    PAPER_INGESTION = "paper_ingestion"
    EVIDENCE_MANAGEMENT = "evidence_management"
    KNOWLEDGE_BASE = "knowledge_base"
    CODING_SANDBOX = "coding_sandbox"
    ARTIFACT_GENERATION = "artifact_generation"
    USER_CLARIFICATION = "user_clarification"
    SUBAGENT_TASK = "subagent_task"


class ToolDefinition(BaseModel):
    name: str
    group: ToolGroup
    description: str
    director_only: bool = False
    source: str = "builtin"


class RuntimeToolContext(BaseModel):
    role: str
    allowed_tools: list[str] = Field(default_factory=list)
    denied_tools: list[str] = Field(default_factory=list)
    allowed_groups: list[ToolGroup] = Field(default_factory=list)
    skill_allowed_tools: list[str] | None = None


class ToolRegistry:
    def __init__(self, tools: list[ToolDefinition]) -> None:
        names = [tool.name for tool in tools]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if duplicates:
            raise ValueError(f"Duplicate tool names: {', '.join(duplicates)}")
        self._tools = tools

    def list(self) -> list[ToolDefinition]:
        return list(self._tools)

    def filter_for(self, context: RuntimeToolContext) -> list[ToolDefinition]:
        allowed_by_name = set(context.allowed_tools)
        denied_by_name = set(context.denied_tools)
        allowed_groups = set(context.allowed_groups)
        skill_allowed = set(context.skill_allowed_tools) if context.skill_allowed_tools is not None else None

        selected: list[ToolDefinition] = []
        for tool in self._tools:
            if tool.name in denied_by_name:
                continue
            if tool.director_only and context.role != "director":
                continue
            if allowed_by_name and tool.name not in allowed_by_name:
                continue
            if allowed_groups and tool.group not in allowed_groups:
                continue
            if skill_allowed is not None and tool.name not in skill_allowed:
                continue
            if not allowed_by_name and not allowed_groups:
                continue
            selected.append(tool)
        return selected


def default_tool_registry(
    configured_tools: list[ToolDefinition] | None = None,
    mcp_tools: list[ToolDefinition] | None = None,
) -> ToolRegistry:
    builtins = [
        ToolDefinition(name="ask_user", group=ToolGroup.USER_CLARIFICATION, description="Ask user."),
        ToolDefinition(name="create_evidence", group=ToolGroup.EVIDENCE_MANAGEMENT, description="Create evidence."),
        ToolDefinition(name="create_artifact", group=ToolGroup.ARTIFACT_GENERATION, description="Create artifact."),
        ToolDefinition(name="kb_read_note", group=ToolGroup.KNOWLEDGE_BASE, description="Read KB note."),
        ToolDefinition(name="sandbox_bash", group=ToolGroup.CODING_SANDBOX, description="Run sandboxed bash."),
        ToolDefinition(
            name="delegate_subagent",
            group=ToolGroup.SUBAGENT_TASK,
            description="Delegate a task to a registered subagent.",
            director_only=True,
        ),
    ]
    return ToolRegistry([*(configured_tools or []), *builtins, *(mcp_tools or [])])

