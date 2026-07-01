from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

from coresearcher.tools.registry import ToolGroup


class SkillMetadata(BaseModel):
    name: str
    description: str
    allowed_tools: list[str] = Field(default_factory=list)
    allowed_tool_groups: list[ToolGroup] = Field(default_factory=list)
    output_schema: str | None = None
    can_write_state: bool = False
    can_write_memory: bool = False


class Skill(BaseModel):
    metadata: SkillMetadata
    content: str
    path: Path


class SkillStoragePaths(BaseModel):
    builtin: Path
    user: Path
    generated_candidates: Path
    generated_enabled: Path
    history: Path


class SkillLoader:
    def __init__(self, paths: SkillStoragePaths) -> None:
        self.paths = paths

    @classmethod
    def default(cls, *, project_root: Path, storage_root: Path = Path("storage/skills")) -> SkillLoader:
        root = storage_root
        return cls(
            SkillStoragePaths(
                builtin=project_root / "backend/coresearcher/skills/builtin",
                user=root / "user",
                generated_candidates=root / "generated/candidates",
                generated_enabled=root / "generated/enabled",
                history=root / "user/.history",
            )
        )

    def history_path(self, skill_name: str) -> Path:
        return self.paths.history / f"{skill_name}.jsonl"

    def load_from_directory(self, directory: Path) -> Skill:
        skill_md = directory / "SKILL.md"
        metadata_yaml = directory / "skill.yaml"
        if not skill_md.exists() or not metadata_yaml.exists():
            raise ValueError(f"Skill directory is missing SKILL.md or skill.yaml: {directory}")
        data = yaml.safe_load(metadata_yaml.read_text(encoding="utf-8")) or {}
        try:
            metadata = SkillMetadata.model_validate(data)
        except ValidationError as exc:
            raise ValueError(f"Invalid Skill metadata in {metadata_yaml}: {exc}") from exc
        return Skill(
            metadata=metadata,
            content=skill_md.read_text(encoding="utf-8"),
            path=directory,
        )

    def load_enabled(self) -> list[Skill]:
        skills: list[Skill] = []
        for root in [self.paths.builtin, self.paths.user, self.paths.generated_enabled]:
            if not root.exists():
                continue
            for directory in sorted(path for path in root.iterdir() if path.is_dir()):
                skills.append(self.load_from_directory(directory))

        seen: set[str] = set()
        unique: list[Skill] = []
        for skill in skills:
            if skill.metadata.name in seen:
                raise ValueError(f"Duplicate Skill name: {skill.metadata.name}")
            seen.add(skill.metadata.name)
            unique.append(skill)
        return unique

    def load_skill(self, name: str) -> Skill:
        for skill in self.load_enabled():
            if skill.metadata.name == name:
                return skill
        raise ValueError(f"Unknown Skill: {name}")
