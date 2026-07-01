from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class SandboxPolicy(BaseModel):
    timeout_seconds: float = 30.0
    max_output_chars: int = 20_000
    network_enabled: bool = False
    allowed_roots: list[Path] = Field(default_factory=list)
    artifact_root: Path = Path(".coresearcher/artifacts")

    def validate_path(self, path: Path) -> Path:
        resolved = path.resolve()
        if not self.allowed_roots:
            raise PermissionError("Sandbox has no allowed roots")
        for root in self.allowed_roots:
            try:
                resolved.relative_to(root.resolve())
                return resolved
            except ValueError:
                continue
        raise PermissionError(f"Path is outside sandbox roots: {resolved}")

    def assert_network_allowed(self) -> None:
        if not self.network_enabled:
            raise PermissionError("Network access is disabled by sandbox policy")

