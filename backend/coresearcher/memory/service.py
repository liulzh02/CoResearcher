from __future__ import annotations

from typing import Any

from coresearcher.knowledge_base import KnowledgeBaseAdapter
from coresearcher.memory.config import MemorySettings
from coresearcher.memory.markdown import MarkdownMemoryStore
from coresearcher.memory.models import (
    CandidateMemoryEntry,
    MemoryRecordType,
    MemoryScope,
    ProvenanceReference,
)
from coresearcher.memory.retrieval import LayeredMemoryRetriever
from coresearcher.memory.session import SQLiteSessionMemoryRepository


class MemoryService:
    def __init__(
        self,
        *,
        settings: MemorySettings | None = None,
        knowledge_base: KnowledgeBaseAdapter | None = None,
    ) -> None:
        self.settings = settings or MemorySettings()
        self.store = MarkdownMemoryStore(self.settings.memory_root)
        self.session = SQLiteSessionMemoryRepository(self.settings.sqlite_path)
        self.knowledge_base = knowledge_base
        self.retriever = LayeredMemoryRetriever(self.store, knowledge_base)

    def create_candidate(
        self,
        *,
        text: str,
        target_scope: MemoryScope,
        record_type: MemoryRecordType,
        confidence: float,
        provenance: list[ProvenanceReference],
        research_id: str | None = None,
    ) -> CandidateMemoryEntry:
        return self.store.add_candidate(
            CandidateMemoryEntry(
                text=text,
                target_scope=target_scope,
                record_type=record_type,
                confidence=confidence,
                provenance=provenance,
                research_id=research_id,
            )
        )

    def promote_candidate(self, candidate_id: str) -> CandidateMemoryEntry:
        return self.store.promote_candidate(candidate_id)

    def reject_candidate(self, candidate_id: str) -> CandidateMemoryEntry:
        return self.store.reject_candidate(candidate_id)

    async def inspect_memory(self, research_id: str, query: str = "") -> dict[str, Any]:
        external_notes = []
        if self.knowledge_base is not None:
            external_notes = await self.knowledge_base.retrieve_memory_notes(query)
        global_memory = self.store.load_global_memory()
        research_memory = self.store.load_research_memory(research_id)
        candidates = self.store.load_candidates(MemoryScope.RESEARCH, research_id=research_id)
        provenance = []
        for candidate in [
            *self.store.load_candidates(MemoryScope.GLOBAL),
            *candidates,
        ]:
            provenance.extend(candidate.provenance)
        return {
            "global_memory": global_memory,
            "research_memory": research_memory,
            "candidates": candidates,
            "provenance": provenance,
            "external_notes": external_notes,
        }

