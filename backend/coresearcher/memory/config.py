from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator


class MemorySettings(BaseModel):
    enabled: bool = True
    memory_root: Path = Path("memory")
    sqlite_path: Path | None = None
    extraction_triggers: list[str] = Field(
        default_factory=lambda: [
            "user_turn",
            "run_completed",
            "research_state_updated",
            "artifact_created",
            "decision_created",
            "explicit_remember_request",
            "token_pressure",
        ]
    )
    extraction_debounce_seconds: int = 30

    @field_validator("extraction_debounce_seconds")
    @classmethod
    def debounce_must_be_non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("extraction_debounce_seconds must be >= 0")
        return value

    @model_validator(mode="after")
    def fill_defaults(self) -> MemorySettings:
        if self.sqlite_path is None:
            self.sqlite_path = self.memory_root / "session_memory.sqlite3"
        return self

    @property
    def global_memory_path(self) -> Path:
        return self.memory_root / "global" / "user_memory.md"

    @property
    def global_candidates_path(self) -> Path:
        return self.memory_root / "global" / "candidates.md"

    def research_memory_path(self, research_id: str) -> Path:
        return self.memory_root / "research" / research_id / "research_memory.md"

    def research_candidates_path(self, research_id: str) -> Path:
        return self.memory_root / "research" / research_id / "candidates.md"

