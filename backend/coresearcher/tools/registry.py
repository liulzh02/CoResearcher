from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ToolGroup(StrEnum):
    FILE = "file"
    PDF = "pdf"
    ARTIFACT = "artifact"
    PRESENTATION = "presentation"
    SEARCH = "search"
    MCP = "mcp"
    EXTERNAL_AGENT = "external_agent"
    PAPER_INGESTION = "paper_ingestion"
    EVIDENCE_MANAGEMENT = "evidence_management"
    KNOWLEDGE_BASE = "knowledge_base"
    CODING_SANDBOX = "coding_sandbox"
    ARTIFACT_GENERATION = "artifact_generation"
    USER_CLARIFICATION = "user_clarification"
    SUBAGENT_TASK = "subagent_task"


class ToolSource(StrEnum):
    BUILTIN = "builtin"
    CONFIGURED = "configured"
    SANDBOX = "sandbox"
    MCP = "mcp"
    EXTERNAL_AGENT = "external_agent"


class ToolResult(BaseModel):
    content: str
    truncated: bool = False
    untrusted: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolDefinition(BaseModel):
    name: str
    group: ToolGroup
    description: str
    director_only: bool = False
    source: ToolSource = ToolSource.BUILTIN
    mcp_server: str | None = None
    requires_vision: bool = False
    requires_bash: bool = False
    untrusted_output: bool = False


class RuntimeToolContext(BaseModel):
    role: str
    allowed_tools: list[str] = Field(default_factory=list)
    denied_tools: list[str] = Field(default_factory=list)
    allowed_groups: list[ToolGroup] = Field(default_factory=list)
    skill_allowed_tools: list[str] | None = None
    active_skills: list[Any] = Field(default_factory=list)
    model_supports_vision: bool = False
    sandbox_allows_bash: bool = False
    allowed_mcp_servers: list[str] | None = None
    allow_subagent_delegation: bool = True

    @classmethod
    def for_subagent(cls, subagent: Any) -> RuntimeToolContext:
        groups: list[ToolGroup] = []
        tools: list[str] = []
        for item in getattr(subagent, "tool_allowlist", []):
            try:
                groups.append(ToolGroup(item))
            except ValueError:
                tools.append(str(item))
        return cls(
            role="subagent",
            allowed_tools=tools,
            allowed_groups=groups,
            denied_tools=list(getattr(subagent, "tool_denylist", [])),
            allow_subagent_delegation=bool(getattr(subagent, "allow_subagent_delegation", False)),
        )


class ToolRegistry:
    def __init__(self, tools: list[ToolDefinition]) -> None:
        self.warnings: list[str] = []
        selected: dict[str, ToolDefinition] = {}
        for tool in tools:
            if tool.name in selected:
                self.warnings.append(
                    f"Skipped duplicate tool {tool.name!r} from {tool.source}; "
                    f"kept {selected[tool.name].source}."
                )
                continue
            selected[tool.name] = tool
        self._tools = list(selected.values())

    def list(self) -> list[ToolDefinition]:
        return list(self._tools)

    def filter_for(self, context: RuntimeToolContext) -> list[ToolDefinition]:
        allowed_by_name = set(context.allowed_tools)
        denied_by_name = set(context.denied_tools)
        allowed_groups = set(context.allowed_groups)
        skill_allowed = (
            set(context.skill_allowed_tools) if context.skill_allowed_tools is not None else set()
        )
        skill_allowed_groups: set[ToolGroup] = set()
        skill_has_explicit_names = False
        for skill in context.active_skills:
            names = getattr(skill, "allowed_tools", []) or []
            if names:
                skill_has_explicit_names = True
            skill_allowed.update(names)
            skill_allowed_groups.update(getattr(skill, "allowed_tool_groups", []) or [])

        has_base_allow = bool(allowed_by_name or allowed_groups)
        has_skill_policy = bool(skill_allowed or skill_allowed_groups)

        selected: list[ToolDefinition] = []
        for tool in self._tools:
            if tool.name in denied_by_name:
                continue
            if tool.director_only and context.role != "director":
                continue
            if tool.group == ToolGroup.SUBAGENT_TASK and not context.allow_subagent_delegation:
                continue
            if tool.requires_vision and not context.model_supports_vision:
                continue
            if tool.requires_bash and not context.sandbox_allows_bash:
                continue
            if tool.source == ToolSource.MCP and context.allowed_mcp_servers is not None:
                if not tool.mcp_server or tool.mcp_server not in context.allowed_mcp_servers:
                    continue
            if has_base_allow and tool.name not in allowed_by_name and tool.group not in allowed_groups:
                continue
            if not has_base_allow and not has_skill_policy:
                continue
            if skill_has_explicit_names and tool.name not in skill_allowed:
                continue
            if (
                has_skill_policy
                and not skill_has_explicit_names
                and tool.name not in skill_allowed
                and tool.group not in skill_allowed_groups
            ):
                continue
            selected.append(tool)
        return selected


def default_tool_registry(
    configured_tools: list[ToolDefinition] | None = None,
    mcp_tools: list[ToolDefinition] | None = None,
    external_agent_tools: list[ToolDefinition] | None = None,
    include_builtins: bool = True,
    include_sandbox_tools: bool = False,
    include_subagent_delegation: bool = True,
) -> ToolRegistry:
    builtins = [
        ToolDefinition(
            name="ask_user",
            group=ToolGroup.USER_CLARIFICATION,
            description="Ask the user for clarification.",
        ),
        ToolDefinition(
            name="present_file",
            group=ToolGroup.PRESENTATION,
            description="Present a file to the user.",
        ),
        ToolDefinition(
            name="present_artifact",
            group=ToolGroup.PRESENTATION,
            description="Present an artifact to the user.",
        ),
        ToolDefinition(
            name="view_image",
            group=ToolGroup.PRESENTATION,
            description="Inspect an image when the model supports vision.",
            requires_vision=True,
        ),
        ToolDefinition(
            name="create_artifact",
            group=ToolGroup.ARTIFACT_GENERATION,
            description="Create a user-facing artifact file.",
        ),
        ToolDefinition(name="kb_read_note", group=ToolGroup.KNOWLEDGE_BASE, description="Read KB note."),
    ]
    sandbox_tools = [
        ToolDefinition(name="ls", group=ToolGroup.FILE, description="List sandbox files.", source=ToolSource.SANDBOX),
        ToolDefinition(name="glob", group=ToolGroup.FILE, description="Find sandbox files.", source=ToolSource.SANDBOX),
        ToolDefinition(name="grep", group=ToolGroup.FILE, description="Search sandbox files.", source=ToolSource.SANDBOX),
        ToolDefinition(name="read_file", group=ToolGroup.FILE, description="Read a sandbox file.", source=ToolSource.SANDBOX),
        ToolDefinition(name="write_file", group=ToolGroup.FILE, description="Write a sandbox file.", source=ToolSource.SANDBOX),
        ToolDefinition(name="str_replace", group=ToolGroup.FILE, description="Replace text in a sandbox file.", source=ToolSource.SANDBOX),
        ToolDefinition(
            name="bash",
            group=ToolGroup.CODING_SANDBOX,
            description="Run a sandbox-scoped shell command.",
            source=ToolSource.SANDBOX,
            requires_bash=True,
        ),
        ToolDefinition(name="list_artifacts", group=ToolGroup.ARTIFACT, description="List artifact files.", source=ToolSource.SANDBOX),
        ToolDefinition(name="read_artifact", group=ToolGroup.ARTIFACT, description="Read an artifact file.", source=ToolSource.SANDBOX),
        ToolDefinition(name="write_artifact", group=ToolGroup.ARTIFACT, description="Write an artifact file.", source=ToolSource.SANDBOX),
        ToolDefinition(name="read_pdf_text", group=ToolGroup.PDF, description="Extract text from a PDF.", source=ToolSource.SANDBOX),
    ]
    subagent_tools = [
        ToolDefinition(
            name="delegate_subagent",
            group=ToolGroup.SUBAGENT_TASK,
            description="Delegate a task to a registered subagent.",
            director_only=True,
        ),
    ]
    return ToolRegistry(
        [
            *(configured_tools or []),
            *(builtins if include_builtins else []),
            *(sandbox_tools if include_sandbox_tools else []),
            *(mcp_tools or []),
            *(external_agent_tools or []),
            *(subagent_tools if include_subagent_delegation else []),
        ]
    )
