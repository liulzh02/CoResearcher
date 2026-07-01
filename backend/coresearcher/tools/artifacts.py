from __future__ import annotations

from pathlib import Path

from coresearcher.security import SandboxPolicy
from coresearcher.tools.registry import ToolResult


class ArtifactFileTools:
    def __init__(self, policy: SandboxPolicy) -> None:
        self.policy = policy

    def _resolve(self, path: str | Path) -> Path:
        candidate = Path(path)
        if candidate.is_absolute():
            raise PermissionError("Artifact paths must be relative")
        return self.policy.validate_artifact_path(candidate)

    def list_artifacts(self) -> ToolResult:
        root = self.policy.artifact_root.resolve()
        if not root.exists():
            return ToolResult(content="", untrusted=True)
        files = [path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()]
        text = "\n".join(sorted(files))
        return ToolResult(
            content=text[: self.policy.max_output_chars],
            truncated=len(text) > self.policy.max_output_chars,
            untrusted=True,
        )

    def read_artifact(self, path: str | Path) -> ToolResult:
        resolved = self._resolve(path)
        text = resolved.read_text(encoding="utf-8")
        return ToolResult(
            content=text[: self.policy.max_output_chars],
            truncated=len(text) > self.policy.max_output_chars,
            untrusted=True,
        )

    def write_artifact(self, path: str | Path, content: str) -> ToolResult:
        if len(content) > self.policy.max_write_chars:
            raise ValueError("Artifact write exceeds sandbox limit")
        resolved = self._resolve(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")
        return ToolResult(content=f"wrote artifact {Path(path).as_posix()}", untrusted=False)
