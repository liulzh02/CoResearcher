from __future__ import annotations

from enum import StrEnum

from coresearcher.domain.state import ResearchState
from coresearcher.memory.models import (
    CandidateMemoryEntry,
    MemoryExtractionOutput,
    MemoryRecordType,
    MemoryScope,
    ProvenanceReference,
)


class MemoryExtractionTrigger(StrEnum):
    USER_TURN = "user_turn"
    RUN_COMPLETED = "run_completed"
    RESEARCH_STATE_UPDATED = "research_state_updated"
    ARTIFACT_CREATED = "artifact_created"
    DECISION_CREATED = "decision_created"
    EXPLICIT_REMEMBER_REQUEST = "explicit_remember_request"
    TOKEN_PRESSURE = "token_pressure"


def should_trigger_extraction(trigger: MemoryExtractionTrigger) -> bool:
    return trigger in set(MemoryExtractionTrigger)


class MemoryTriggerBatcher:
    def __init__(self, debounce_seconds: int = 30) -> None:
        self.debounce_seconds = debounce_seconds
        self._last_scheduled_at: dict[str, float] = {}

    def should_schedule(self, thread_id: str, now_seconds: float) -> bool:
        last = self._last_scheduled_at.get(thread_id)
        if last is not None and now_seconds - last < self.debounce_seconds:
            return False
        self._last_scheduled_at[thread_id] = now_seconds
        return True


MEMORY_EXTRACTION_PROMPT = """Extract candidate memory only.
Return user preferences, project facts, decisions, research goals, method preferences,
and open questions as candidates with provenance. Do not override raw messages,
ResearchState, evidence records, decisions, or artifacts.
"""


class MemoryExtractor:
    prompt: str = MEMORY_EXTRACTION_PROMPT

    def extract_candidates(
        self,
        text: str,
        *,
        trigger: MemoryExtractionTrigger,
        authoritative_state: ResearchState,
        research_id: str | None = None,
        provenance: list[ProvenanceReference] | None = None,
    ) -> MemoryExtractionOutput:
        lowered = text.lower()
        candidates: list[CandidateMemoryEntry] = []

        if "remember" in lowered or "记住" in text:
            scope = MemoryScope.GLOBAL if "prefer" in lowered or "偏好" in text else MemoryScope.RESEARCH
            record_type = (
                MemoryRecordType.USER_PREFERENCE
                if scope == MemoryScope.GLOBAL
                else MemoryRecordType.PROJECT_FACT
            )
            candidates.append(
                CandidateMemoryEntry(
                    text=text.replace("Remember that ", "").replace("remember that ", "").strip(),
                    target_scope=scope,
                    research_id=research_id if scope == MemoryScope.RESEARCH else None,
                    record_type=record_type,
                    confidence=0.8,
                    provenance=provenance or [ProvenanceReference(type="trigger", id=trigger.value)],
                )
            )

        if trigger == MemoryExtractionTrigger.RUN_COMPLETED and authoritative_state.decisions:
            for decision in authoritative_state.decisions:
                candidates.append(
                    CandidateMemoryEntry(
                        text=decision.text,
                        target_scope=MemoryScope.RESEARCH,
                        research_id=research_id or "unknown",
                        record_type=MemoryRecordType.DECISION,
                        confidence=0.9,
                        provenance=[ProvenanceReference(type="decision", id=decision.id)],
                    )
                )

        return MemoryExtractionOutput(candidates=candidates)

