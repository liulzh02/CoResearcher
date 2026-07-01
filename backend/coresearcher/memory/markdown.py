from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from coresearcher.domain.state import utc_now
from coresearcher.memory.models import (
    CandidateMemoryEntry,
    CandidateStatus,
    MemoryFile,
    MemoryFileStatus,
    MemoryFileType,
    MemoryFrontmatter,
    MemoryScope,
    MemoryValidationResult,
    ProvenanceReference,
)

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.DOTALL)


class MarkdownMemoryStore:
    def __init__(self, memory_root: Path) -> None:
        self.root = memory_root
        self.root.mkdir(parents=True, exist_ok=True)

    def global_memory_path(self) -> Path:
        return self.root / "global" / "user_memory.md"

    def global_candidates_path(self) -> Path:
        return self.root / "global" / "candidates.md"

    def research_memory_path(self, research_id: str) -> Path:
        return self.root / "research" / research_id / "research_memory.md"

    def research_candidates_path(self, research_id: str) -> Path:
        return self.root / "research" / research_id / "candidates.md"

    def _serialize(self, frontmatter: MemoryFrontmatter, body: str) -> str:
        data = frontmatter.model_dump(mode="json")
        return f"---\n{yaml.safe_dump(data, sort_keys=False)}---\n{body.rstrip()}\n"

    def _write_file(self, path: Path, frontmatter: MemoryFrontmatter, body: str) -> MemoryFile:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._serialize(frontmatter, body), encoding="utf-8")
        return MemoryFile(frontmatter=frontmatter, body=body.rstrip() + "\n", path=str(path))

    def _default_body(self, title: str) -> str:
        return f"# {title}\n\n## Memories\n\n"

    def ensure_global_memory(self, user_id: str | None = None) -> MemoryFile:
        path = self.global_memory_path()
        if path.exists():
            return self.load_file(path)
        frontmatter = MemoryFrontmatter(
            scope=MemoryScope.GLOBAL,
            type=MemoryFileType.USER_MEMORY,
            user_id=user_id,
        )
        return self._write_file(path, frontmatter, self._default_body("Global User Memory"))

    def ensure_research_memory(
        self,
        research_id: str,
        user_id: str | None = None,
    ) -> MemoryFile:
        path = self.research_memory_path(research_id)
        if path.exists():
            return self.load_file(path)
        frontmatter = MemoryFrontmatter(
            scope=MemoryScope.RESEARCH,
            type=MemoryFileType.RESEARCH_MEMORY,
            user_id=user_id,
            research_id=research_id,
        )
        return self._write_file(path, frontmatter, self._default_body("Research Memory"))

    def validate_file(self, path: Path) -> MemoryValidationResult:
        try:
            self.load_file(path)
            return MemoryValidationResult(valid=True)
        except Exception as exc:
            return MemoryValidationResult(valid=False, warnings=[str(exc)])

    def load_file(self, path: Path) -> MemoryFile:
        text = path.read_text(encoding="utf-8")
        match = FRONTMATTER_RE.match(text)
        if not match:
            raise ValueError("Markdown memory file is missing required frontmatter")
        raw_frontmatter, body = match.groups()
        loaded = yaml.safe_load(raw_frontmatter)
        if not isinstance(loaded, dict):
            raise ValueError("Markdown memory frontmatter must be a mapping")
        frontmatter = MemoryFrontmatter.model_validate(loaded)
        return MemoryFile(frontmatter=frontmatter, body=body, path=str(path))

    def load_global_memory(self) -> MemoryFile:
        return self.ensure_global_memory()

    def load_research_memory(self, research_id: str) -> MemoryFile:
        return self.ensure_research_memory(research_id)

    def append_memory(
        self,
        scope: MemoryScope,
        text: str,
        *,
        research_id: str | None = None,
        provenance: list[ProvenanceReference] | None = None,
    ) -> MemoryFile:
        if scope == MemoryScope.GLOBAL:
            memory = self.ensure_global_memory()
            path = self.global_memory_path()
        else:
            if not research_id:
                raise ValueError("research_id is required for research memory")
            memory = self.ensure_research_memory(research_id)
            path = self.research_memory_path(research_id)

        provenance_text = ""
        if provenance:
            provenance_text = " " + json.dumps(
                [item.model_dump(mode="json") for item in provenance],
                ensure_ascii=True,
            )
        line = f"- {text}{provenance_text}\n"
        memory.frontmatter.updated_at = utc_now()
        return self._write_file(path, memory.frontmatter, memory.body.rstrip() + "\n" + line)

    def _candidate_path(self, scope: MemoryScope, research_id: str | None = None) -> Path:
        if scope == MemoryScope.GLOBAL:
            return self.global_candidates_path()
        if not research_id:
            raise ValueError("research_id is required for research candidates")
        return self.research_candidates_path(research_id)

    def _candidate_frontmatter(
        self,
        scope: MemoryScope,
        research_id: str | None = None,
    ) -> MemoryFrontmatter:
        return MemoryFrontmatter(
            scope=scope,
            type=MemoryFileType.CANDIDATES,
            research_id=research_id,
        )

    def _read_candidates_from_path(self, path: Path) -> list[CandidateMemoryEntry]:
        if not path.exists():
            return []
        memory_file = self.load_file(path)
        entries: list[CandidateMemoryEntry] = []
        for line in memory_file.body.splitlines():
            if not line.startswith("<!-- candidate:"):
                continue
            raw = line.removeprefix("<!-- candidate:").removesuffix("-->").strip()
            entries.append(CandidateMemoryEntry.model_validate_json(raw))
        return entries

    def _write_candidates(
        self,
        path: Path,
        scope: MemoryScope,
        candidates: list[CandidateMemoryEntry],
        research_id: str | None = None,
    ) -> None:
        body_lines = ["# Candidate Memory", "", "## Candidates", ""]
        for candidate in candidates:
            body_lines.append(
                "<!-- candidate: "
                + candidate.model_dump_json()
                + " -->"
            )
            body_lines.append(
                f"- [{candidate.status.value}] {candidate.text} "
                f"(confidence: {candidate.confidence})"
            )
        self._write_file(
            path,
            self._candidate_frontmatter(scope, research_id),
            "\n".join(body_lines),
        )

    def add_candidate(self, candidate: CandidateMemoryEntry) -> CandidateMemoryEntry:
        path = self._candidate_path(candidate.target_scope, candidate.research_id)
        candidates = self._read_candidates_from_path(path)
        candidates.append(candidate)
        self._write_candidates(path, candidate.target_scope, candidates, candidate.research_id)
        return candidate

    def load_candidates(
        self,
        scope: MemoryScope,
        research_id: str | None = None,
    ) -> list[CandidateMemoryEntry]:
        return self._read_candidates_from_path(self._candidate_path(scope, research_id))

    def _find_candidate(
        self,
        candidate_id: str,
    ) -> tuple[Path, MemoryScope, str | None, list[CandidateMemoryEntry], CandidateMemoryEntry]:
        locations: list[tuple[Path, MemoryScope, str | None]] = [
            (self.global_candidates_path(), MemoryScope.GLOBAL, None)
        ]
        research_root = self.root / "research"
        if research_root.exists():
            for child in research_root.iterdir():
                if child.is_dir():
                    locations.append(
                        (self.research_candidates_path(child.name), MemoryScope.RESEARCH, child.name)
                    )
        for path, scope, research_id in locations:
            candidates = self._read_candidates_from_path(path)
            for candidate in candidates:
                if candidate.id == candidate_id:
                    return path, scope, research_id, candidates, candidate
        raise KeyError(f"Candidate not found: {candidate_id}")

    def promote_candidate(self, candidate_id: str) -> CandidateMemoryEntry:
        path, scope, research_id, candidates, candidate = self._find_candidate(candidate_id)
        candidate.status = CandidateStatus.PROMOTED
        candidate.updated_at = utc_now()
        self.append_memory(
            candidate.target_scope,
            candidate.text,
            research_id=candidate.research_id,
            provenance=candidate.provenance,
        )
        self._write_candidates(path, scope, candidates, research_id)
        return candidate

    def reject_candidate(self, candidate_id: str) -> CandidateMemoryEntry:
        path, scope, research_id, candidates, candidate = self._find_candidate(candidate_id)
        candidate.status = CandidateStatus.REJECTED
        candidate.updated_at = utc_now()
        self._write_candidates(path, scope, candidates, research_id)
        return candidate

