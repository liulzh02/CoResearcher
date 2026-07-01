from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class RuntimeSecurityContext(BaseModel):
    user_id: str
    thread_id: str
    run_id: str
    role: str
    allowed_tools: list[str] = Field(default_factory=list)
    allowed_mcp_servers: list[str] = Field(default_factory=list)
    sandbox_id: str | None = None
    artifact_root: Path = Path(".coresearcher/artifacts")

