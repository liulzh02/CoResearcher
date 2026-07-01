from __future__ import annotations

from pydantic import BaseModel, Field

from coresearcher.domain.state import ResearchState
from coresearcher.knowledge_base import KnowledgeBaseAdapter
from coresearcher.memory.markdown import MarkdownMemoryStore
from coresearcher.memory.models import MemoryScope
from coresearcher.prompting import sanitize_untrusted_source_text


class MemoryContextLayer(BaseModel):
    name: str
    content: str
    source: str | None = None


class MemoryContext(BaseModel):
    layers: list[MemoryContextLayer] = Field(default_factory=list)


def _is_relevant(text: str, query: str) -> bool:
    if not query.strip():
        return True
    words = {word.lower() for word in query.split() if len(word) > 2}
    lowered = text.lower()
    return any(word in lowered for word in words)


class LayeredMemoryRetriever:
    def __init__(
        self,
        store: MarkdownMemoryStore,
        knowledge_base: KnowledgeBaseAdapter | None = None,
    ) -> None:
        self.store = store
        self.knowledge_base = knowledge_base

    async def retrieve(
        self,
        *,
        thread_state: ResearchState,
        research_id: str,
        query: str,
        include_candidates: bool = False,
    ) -> MemoryContext:
        layers = [
            MemoryContextLayer(
                name="current_thread_state",
                content=thread_state.model_dump_json(),
                source="research_state",
            )
        ]

        research_memory = self.store.load_research_memory(research_id)
        layers.append(
            MemoryContextLayer(
                name="per_research_memory",
                content=sanitize_untrusted_source_text(research_memory.body),
                source=research_memory.path,
            )
        )

        global_memory = self.store.load_global_memory()
        if _is_relevant(global_memory.body, query):
            layers.append(
                MemoryContextLayer(
                    name="global_user_memory",
                    content=sanitize_untrusted_source_text(global_memory.body),
                    source=global_memory.path,
                )
            )

        if self.knowledge_base is not None:
            notes = await self.knowledge_base.retrieve_memory_notes(query)
            note_text = "\n".join(
                f"# {note.title}\n{sanitize_untrusted_source_text(note.content)}"
                for note in notes
                if _is_relevant(note.title + "\n" + note.content, query)
            )
            if note_text:
                layers.append(
                    MemoryContextLayer(
                        name="external_knowledge_base",
                        content=note_text,
                        source="knowledge_base",
                    )
                )

        if include_candidates:
            candidates = self.store.load_candidates(MemoryScope.RESEARCH, research_id=research_id)
            content = "\n".join(candidate.text for candidate in candidates)
            layers.append(
                MemoryContextLayer(
                    name="candidate_memory_review",
                    content=sanitize_untrusted_source_text(content),
                    source="candidate_memory",
                )
            )

        return MemoryContext(layers=layers)

