from __future__ import annotations

from coresearcher.context.models import CompressionLevel, ContextSection, ContextSectionType


def estimate_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4) if text else 0


class ContextBudgeter:
    def __init__(
        self,
        *,
        prompt_budget: int = 12_000,
        completion_reserve: int = 2_000,
        per_section_limits: dict[ContextSectionType, int] | None = None,
    ) -> None:
        self.prompt_budget = prompt_budget
        self.completion_reserve = completion_reserve
        self.available_prompt_budget = max(1, prompt_budget - completion_reserve)
        self.per_section_limits = per_section_limits or {}

    def section_limit(self, section_type: ContextSectionType, default: int = 4_000) -> int:
        return self.per_section_limits.get(section_type, default)

    def estimate_sections(self, sections: list[ContextSection]) -> dict[str, int]:
        return {section.type.value: estimate_tokens(section.content) for section in sections}

    def select_level(self, *, estimated_prompt_tokens: int) -> CompressionLevel:
        ratio = estimated_prompt_tokens / max(1, self.available_prompt_budget)
        if ratio <= 0.75:
            return CompressionLevel.LEVEL_0
        if ratio <= 1.10:
            return CompressionLevel.LEVEL_1
        if ratio <= 1.55:
            return CompressionLevel.LEVEL_2
        if ratio <= 2.25:
            return CompressionLevel.LEVEL_3
        if ratio <= 3.20:
            return CompressionLevel.LEVEL_4
        return CompressionLevel.LEVEL_5
