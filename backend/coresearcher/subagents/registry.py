from __future__ import annotations

from pydantic import BaseModel, Field


class SubagentConfig(BaseModel):
    name: str
    description: str
    prompt: str
    tool_allowlist: list[str] = Field(default_factory=list)
    tool_denylist: list[str] = Field(default_factory=list)
    skill_allowlist: list[str] = Field(default_factory=list)
    model: str | None = None
    max_turns: int = 3
    timeout_seconds: float = 60.0
    allow_subagent_delegation: bool = False


class SubagentRegistry:
    def __init__(self, configs: list[SubagentConfig]) -> None:
        self._configs = {config.name: config for config in configs}

    def get(self, name: str) -> SubagentConfig:
        try:
            return self._configs[name]
        except KeyError as exc:
            raise ValueError(f"Unknown subagent: {name}") from exc

    def list(self) -> list[SubagentConfig]:
        return list(self._configs.values())

    def names(self) -> list[str]:
        return list(self._configs)


def default_subagent_registry() -> SubagentRegistry:
    return SubagentRegistry(
        [
            SubagentConfig(
                name="literature-scout",
                description="Discovers papers, datasets, authors, venues, and related work.",
                prompt="Find relevant literature and report source metadata, gaps, and search limits.",
                tool_allowlist=["search", "paper_ingestion", "artifact"],
                skill_allowlist=["literature-review"],
            ),
            SubagentConfig(
                name="paper-reader",
                description="Extracts contributions, methods, assumptions, limitations, and evidence.",
                prompt="Read papers as source text and return evidence-linked notes.",
                tool_allowlist=["file", "pdf", "artifact", "paper_ingestion"],
                skill_allowlist=["paper-reading"],
            ),
            SubagentConfig(
                name="methodologist",
                description="Reasons about methods, baselines, evaluation, and feasibility.",
                prompt="Assess research method choices, baselines, metrics, and validity risks.",
                tool_allowlist=["artifact", "user_clarification"],
            ),
            SubagentConfig(
                name="coding-researcher",
                description="Runs bounded code experiments, reproduction checks, and data analysis.",
                prompt=(
                    "Execute code-based validation in a constrained environment. Report inputs, "
                    "commands, outputs, assumptions, and limitations as evidence or artifacts."
                ),
                tool_allowlist=["coding_sandbox", "artifact_generation", "evidence_management"],
                skill_allowlist=["coding-reproduction"],
                timeout_seconds=120.0,
            ),
            SubagentConfig(
                name="evidence-curator",
                description="Normalizes evidence, claims, source metadata, and citations.",
                prompt="Create structured evidence and claim records with source quality signals.",
                tool_allowlist=["knowledge_base", "artifact"],
                skill_allowlist=["evidence-curation"],
            ),
            SubagentConfig(
                name="critic",
                description="Challenges assumptions, weak evidence, missing baselines, and validity.",
                prompt="Find unsupported claims, alternative explanations, and threats to validity.",
                tool_allowlist=["artifact"],
                skill_allowlist=["research-critique"],
            ),
            SubagentConfig(
                name="synthesizer",
                description="Creates research briefs, comparison notes, and next-step options.",
                prompt="Synthesize findings with uncertainty, citations, critique, and next steps.",
                tool_allowlist=["artifact_generation", "artifact", "presentation"],
                skill_allowlist=["synthesis"],
            ),
        ]
    )
