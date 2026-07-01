from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from coresearcher.context.rendering import DEFAULT_RESERVED_CONTEXT_TAGS
from coresearcher.tools.registry import ToolGroup


class PersistenceSettings(BaseModel):
    backend: str = "json"
    data_dir: Path = Path(".coresearcher/data")


class GatewaySettings(BaseModel):
    title: str = "CoResearcher API"
    cors_origins: list[str] = Field(default_factory=list)


class SecuritySettings(BaseModel):
    default_user_id: str = "local-user"
    max_subagent_concurrency: int = 3
    allowed_mcp_servers: list[str] = Field(default_factory=list)


class SandboxSettings(BaseModel):
    timeout_seconds: float = 30.0
    max_output_chars: int = 20_000
    max_write_chars: int = 200_000
    network_enabled: bool = False
    allow_bash: bool = False
    artifact_root: Path = Path(".coresearcher/artifacts")
    allowed_roots: list[Path] = Field(default_factory=lambda: [Path(".coresearcher/workspaces")])


class ToolSwitchSettings(BaseModel):
    enabled: bool = True


class SubagentDelegationToolSettings(BaseModel):
    enabled: bool = True
    director_only: bool = True


class ExternalProviderSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    secret_env: str | None = None
    base_url: str | None = None

    def resolve_secret(self) -> str | None:
        if not self.secret_env:
            return None
        value = os.getenv(self.secret_env)
        if not value:
            raise RuntimeError(f"Required secret environment variable is missing: {self.secret_env}")
        return value


class McpServerSettings(BaseModel):
    name: str
    enabled: bool = False
    allowed_tools: list[str] = Field(default_factory=list)


class ConfiguredToolSettings(BaseModel):
    name: str
    group: ToolGroup
    enabled: bool = True


class ToolPolicySettings(BaseModel):
    default_allowed_groups: list[ToolGroup] = Field(default_factory=list)
    denied_tools: list[str] = Field(default_factory=list)
    allowed_mcp_servers: list[str] = Field(default_factory=list)


class SkillStorageSettings(BaseModel):
    builtin_root: Path = Path("backend/coresearcher/skills/builtin")
    storage_root: Path = Path("storage/skills")


class ContextSettings(BaseModel):
    default_prompt_budget: int = 12_000
    completion_reserve: int = 2_000
    director_prompt_budget: int = 12_000
    subagent_prompt_budget: int = 8_000
    per_section_limits: dict[str, int] = Field(
        default_factory=lambda: {
            "history": 2_000,
            "memory": 2_000,
            "evidence": 3_000,
            "tool_output": 1_500,
            "skill_context": 1_500,
        }
    )
    tool_output_char_limit: int = 6_000
    long_document_snippet_limit: int = 1_200
    emergency_summary_enabled: bool = True
    compression_thresholds: dict[str, float] = Field(
        default_factory=lambda: {
            "level_1": 0.75,
            "level_2": 1.10,
            "level_3": 1.55,
            "level_4": 2.25,
            "level_5": 3.20,
        }
    )
    reserved_tags: list[str] = Field(default_factory=lambda: list(DEFAULT_RESERVED_CONTEXT_TAGS))
    renderer_blocks: dict[str, str] = Field(
        default_factory=lambda: {
            "memory": "memory-context",
            "research_state": "research-state",
            "evidence": "evidence-context",
            "tool_output": "tool-output",
            "skill": "skill-context",
            "omitted": "omitted-context",
        }
    )


def _default_search_providers() -> dict[str, ExternalProviderSettings]:
    return {
        "fake": ExternalProviderSettings(enabled=False),
        "ddg": ExternalProviderSettings(enabled=False),
        "jina_ai": ExternalProviderSettings(enabled=False, secret_env="JINA_API_KEY"),
        "serper": ExternalProviderSettings(enabled=False, secret_env="SERPER_API_KEY"),
        "brave": ExternalProviderSettings(enabled=False, secret_env="BRAVE_SEARCH_API_KEY"),
        "tavily": ExternalProviderSettings(enabled=False, secret_env="TAVILY_API_KEY"),
        "firecrawl": ExternalProviderSettings(enabled=False, secret_env="FIRECRAWL_API_KEY"),
        "browserless": ExternalProviderSettings(enabled=False, secret_env="BROWSERLESS_API_KEY"),
        "exa": ExternalProviderSettings(enabled=False, secret_env="EXA_API_KEY"),
        "arxiv": ExternalProviderSettings(enabled=False),
        "semantic_scholar": ExternalProviderSettings(
            enabled=False, secret_env="SEMANTIC_SCHOLAR_API_KEY"
        ),
        "crossref": ExternalProviderSettings(enabled=False),
    }


class ToolRuntimeSettings(BaseModel):
    builtins: ToolSwitchSettings = Field(default_factory=ToolSwitchSettings)
    sandbox: ToolSwitchSettings = Field(default_factory=ToolSwitchSettings)
    subagent_delegation: SubagentDelegationToolSettings = Field(
        default_factory=SubagentDelegationToolSettings
    )
    configured_tools: list[ConfiguredToolSettings] = Field(default_factory=list)
    search_providers: dict[str, ExternalProviderSettings] = Field(
        default_factory=_default_search_providers
    )
    mcp_servers: list[McpServerSettings] = Field(default_factory=list)
    external_agents: dict[str, ExternalProviderSettings] = Field(default_factory=dict)
    policy: ToolPolicySettings = Field(default_factory=ToolPolicySettings)
    skills: SkillStorageSettings = Field(default_factory=SkillStorageSettings)

    @field_validator("search_providers")
    @classmethod
    def normalize_provider_names(
        cls, value: dict[str, ExternalProviderSettings]
    ) -> dict[str, ExternalProviderSettings]:
        normalized: dict[str, ExternalProviderSettings] = {}
        for name, settings in value.items():
            normalized[name.replace("-", "_")] = settings
        return normalized


class AppSettings(BaseModel):
    environment: str = "local"
    persistence: PersistenceSettings = Field(default_factory=PersistenceSettings)
    gateway: GatewaySettings = Field(default_factory=GatewaySettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    sandbox: SandboxSettings = Field(default_factory=SandboxSettings)
    tools: ToolRuntimeSettings = Field(default_factory=ToolRuntimeSettings)
    context: ContextSettings = Field(default_factory=ContextSettings)


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_settings(config_path: str | Path | None = None) -> AppSettings:
    data: dict[str, Any] = {}
    path = Path(config_path or os.getenv("CORESEARCHER_CONFIG", ""))
    if path and str(path) != "." and path.exists():
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, dict):
            raise ValueError("Configuration file must contain a mapping")
        data = loaded

    env_override: dict[str, Any] = {
        "environment": os.getenv("CORESEARCHER_ENV", data.get("environment", "local")),
        "security": {
            "default_user_id": os.getenv(
                "CORESEARCHER_DEFAULT_USER_ID",
                data.get("security", {}).get("default_user_id", "local-user"),
            )
        },
    }

    data = _deep_merge(data, env_override)
    return AppSettings.model_validate(data)


def require_env_secret(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required secret environment variable is missing: {name}")
    return value
