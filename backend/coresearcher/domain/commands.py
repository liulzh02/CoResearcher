from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from coresearcher.domain.state import (
    Claim,
    CritiqueNote,
    Decision,
    EvidenceItem,
    ResearchState,
    TodoItem,
)


class MemoryPromotionRequest(BaseModel):
    text: str
    scope: str = "research"
    provenance_ids: list[str] = Field(default_factory=list)


class DomainCommandService:
    command_names = {
        "create_evidence_item",
        "create_claim",
        "record_decision",
        "record_critique",
        "update_research_state",
        "promote_memory",
    }

    def apply(self, command: str, payload: dict[str, Any], state: ResearchState) -> BaseModel:
        if command == "create_evidence_item":
            item = EvidenceItem.model_validate(payload)
            state.evidence_items.append(item)
            state.touch()
            return item
        if command == "create_claim":
            claim = Claim.model_validate(payload)
            state.claims.append(claim)
            state.touch()
            return claim
        if command == "record_decision":
            decision = Decision.model_validate(payload)
            state.decisions.append(decision)
            state.touch()
            return decision
        if command == "record_critique":
            critique = CritiqueNote.model_validate(payload)
            state.critique_notes.append(critique)
            state.touch()
            return critique
        if command == "update_research_state":
            todo = TodoItem.model_validate(payload)
            state.todos.append(todo)
            state.touch()
            return todo
        if command == "promote_memory":
            request = MemoryPromotionRequest.model_validate(payload)
            state.touch()
            return request
        raise ValueError(f"Unknown domain command: {command}")
