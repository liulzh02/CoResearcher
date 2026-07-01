from __future__ import annotations

import subprocess
from pathlib import Path
from threading import Lock

from coresearcher.security import SandboxPolicy
from coresearcher.tools.registry import ToolResult


class LocalSandboxTools:
    def __init__(self, policy: SandboxPolicy) -> None:
        self.policy = policy
        self._lock = Lock()

    def _resolve(self, path: str | Path) -> Path:
        candidate = Path(path)
        if not candidate.is_absolute():
            if not self.policy.allowed_roots:
                raise PermissionError("Sandbox has no allowed roots")
            candidate = self.policy.allowed_roots[0] / candidate
        return self.policy.validate_path(candidate)

    def _truncate(self, text: str, max_chars: int | None = None) -> ToolResult:
        limit = max_chars or self.policy.max_output_chars
        return ToolResult(content=text[:limit], truncated=len(text) > limit, untrusted=True)

    def ls(self, path: str | Path = ".") -> ToolResult:
        root = self._resolve(path)
        if not root.exists():
            return ToolResult(content="", untrusted=True)
        if root.is_file():
            return ToolResult(content=root.name, untrusted=True)
        return self._truncate("\n".join(sorted(child.name for child in root.iterdir())))

    def glob(self, pattern: str) -> ToolResult:
        if Path(pattern).is_absolute() or ".." in Path(pattern).parts:
            raise PermissionError("Glob pattern must be sandbox-relative")
        roots = [root.resolve() for root in self.policy.allowed_roots]
        matches: list[str] = []
        for root in roots:
            if not root.exists():
                continue
            for path in root.glob(pattern):
                if path.is_file():
                    matches.append(path.resolve().relative_to(root).as_posix())
        return self._truncate("\n".join(sorted(matches)))

    def grep(self, query: str, pattern: str = "**/*") -> ToolResult:
        hits: list[str] = []
        for rel in self.glob(pattern).content.splitlines():
            path = self._resolve(rel)
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                if query in line:
                    hits.append(f"{line} ({rel}:{line_no})")
        return self._truncate("\n".join(hits))

    def read_file(self, path: str | Path, *, max_chars: int | None = None) -> ToolResult:
        resolved = self._resolve(path)
        data = resolved.read_bytes()
        if b"\x00" in data:
            raise ValueError("Binary files cannot be read as text")
        text = data.decode("utf-8")
        return self._truncate(text, max_chars)

    def write_file(self, path: str | Path, content: str) -> ToolResult:
        if len(content) > self.policy.max_write_chars:
            raise ValueError("File write exceeds sandbox limit")
        resolved = self._resolve(path)
        with self._lock:
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.write_text(content, encoding="utf-8")
        return ToolResult(content=f"wrote {Path(path).as_posix()}", untrusted=False)

    def str_replace(self, path: str | Path, old: str, new: str) -> ToolResult:
        resolved = self._resolve(path)
        with self._lock:
            text = resolved.read_text(encoding="utf-8")
            if old not in text:
                raise ValueError("Text to replace was not found")
            updated = text.replace(old, new)
            if len(updated) > self.policy.max_write_chars:
                raise ValueError("File write exceeds sandbox limit")
            resolved.write_text(updated, encoding="utf-8")
        return ToolResult(content=f"updated {Path(path).as_posix()}", untrusted=False)

    def bash(self, command: str) -> ToolResult:
        self.policy.assert_bash_allowed()
        if not self.policy.allowed_roots:
            raise PermissionError("Sandbox has no allowed roots")
        completed = subprocess.run(
            command,
            cwd=self.policy.allowed_roots[0],
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            timeout=self.policy.timeout_seconds,
        )
        return self._truncate((completed.stdout or "") + (completed.stderr or ""))


class DocumentInspectionTools:
    def __init__(self, policy: SandboxPolicy) -> None:
        self.policy = policy
        self._files = LocalSandboxTools(policy)

    def read_pdf_text(self, path: str | Path) -> ToolResult:
        resolved = self._files._resolve(path)
        data = resolved.read_bytes()
        text = data.decode("latin-1", errors="ignore")
        text = text.replace("%PDF-1.4", "").replace("%%EOF", "").strip()
        return ToolResult(
            content=text[: self.policy.max_output_chars],
            truncated=len(text) > self.policy.max_output_chars,
            untrusted=True,
        )
