from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


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
    network_enabled: bool = False
    artifact_root: Path = Path(".coresearcher/artifacts")
    allowed_roots: list[Path] = Field(default_factory=lambda: [Path(".coresearcher/workspaces")])


class AppSettings(BaseModel):
    environment: str = "local"
    persistence: PersistenceSettings = Field(default_factory=PersistenceSettings)
    gateway: GatewaySettings = Field(default_factory=GatewaySettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    sandbox: SandboxSettings = Field(default_factory=SandboxSettings)


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

