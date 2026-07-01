from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class SandboxPolicy(BaseModel):
    timeout_seconds: float = 30.0
    max_output_chars: int = 20_000
    max_write_chars: int = 200_000
    network_enabled: bool = False
    allow_bash: bool = False
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

    def validate_artifact_path(self, path: Path) -> Path:
        root = self.artifact_root.resolve()
        resolved = (root / path).resolve() if not path.is_absolute() else path.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise PermissionError(f"Path is outside artifact root: {resolved}") from exc
        return resolved

    def assert_bash_allowed(self) -> None:
        if not self.allow_bash:
            raise PermissionError("Bash execution is disabled by sandbox policy")

    def assert_network_allowed(self) -> None:
        if not self.network_enabled:
            raise PermissionError("Network access is disabled by sandbox policy")
