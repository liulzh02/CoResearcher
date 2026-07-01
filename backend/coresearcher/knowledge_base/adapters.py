from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, Field


class KnowledgeBaseNote(BaseModel):
    id: str
    title: str
    content: str = ""
    path: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeBaseEntity(BaseModel):
    id: str
    type: str
    name: str
    properties: dict[str, Any] = Field(default_factory=dict)


class KnowledgeBaseRelation(BaseModel):
    source_id: str
    target_id: str
    type: str
    properties: dict[str, Any] = Field(default_factory=dict)


class KnowledgeBaseAdapter(Protocol):
    async def list_notes(self) -> list[KnowledgeBaseNote]: ...

    async def read_note(self, note_id: str) -> KnowledgeBaseNote | None: ...

    async def write_note(self, note: KnowledgeBaseNote) -> KnowledgeBaseNote: ...

    async def query_entities(self, query: str) -> list[KnowledgeBaseEntity]: ...

    async def upsert_entity(self, entity: KnowledgeBaseEntity) -> KnowledgeBaseEntity: ...

    async def upsert_relation(self, relation: KnowledgeBaseRelation) -> KnowledgeBaseRelation: ...

    async def link_note_to_state(self, note_id: str, state_object_id: str) -> None: ...


class FakeKnowledgeBaseAdapter:
    def __init__(self) -> None:
        self.notes: dict[str, KnowledgeBaseNote] = {}
        self.entities: dict[str, KnowledgeBaseEntity] = {}
        self.relations: list[KnowledgeBaseRelation] = []
        self.links: dict[str, list[str]] = {}

    async def list_notes(self) -> list[KnowledgeBaseNote]:
        return list(self.notes.values())

    async def read_note(self, note_id: str) -> KnowledgeBaseNote | None:
        return self.notes.get(note_id)

    async def write_note(self, note: KnowledgeBaseNote) -> KnowledgeBaseNote:
        self.notes[note.id] = note
        return note

    async def query_entities(self, query: str) -> list[KnowledgeBaseEntity]:
        lowered = query.lower()
        return [entity for entity in self.entities.values() if lowered in entity.name.lower()]

    async def upsert_entity(self, entity: KnowledgeBaseEntity) -> KnowledgeBaseEntity:
        self.entities[entity.id] = entity
        return entity

    async def upsert_relation(self, relation: KnowledgeBaseRelation) -> KnowledgeBaseRelation:
        self.relations.append(relation)
        return relation

    async def link_note_to_state(self, note_id: str, state_object_id: str) -> None:
        self.links.setdefault(state_object_id, []).append(note_id)


class ObsidianMcpKnowledgeBaseAdapter:
    def __init__(self, mcp_client: Any, server_name: str = "obsidian") -> None:
        self.mcp_client = mcp_client
        self.server_name = server_name

    async def list_notes(self) -> list[KnowledgeBaseNote]:
        result = await self.mcp_client.call_tool(self.server_name, "list_notes", {})
        return [KnowledgeBaseNote.model_validate(item) for item in result]

    async def read_note(self, note_id: str) -> KnowledgeBaseNote | None:
        result = await self.mcp_client.call_tool(self.server_name, "read_note", {"note_id": note_id})
        return KnowledgeBaseNote.model_validate(result) if result else None

    async def write_note(self, note: KnowledgeBaseNote) -> KnowledgeBaseNote:
        result = await self.mcp_client.call_tool(
            self.server_name,
            "write_note",
            {"note": note.model_dump(mode="json")},
        )
        return KnowledgeBaseNote.model_validate(result)

    async def query_entities(self, query: str) -> list[KnowledgeBaseEntity]:
        result = await self.mcp_client.call_tool(self.server_name, "query_entities", {"query": query})
        return [KnowledgeBaseEntity.model_validate(item) for item in result]

    async def upsert_entity(self, entity: KnowledgeBaseEntity) -> KnowledgeBaseEntity:
        result = await self.mcp_client.call_tool(
            self.server_name,
            "upsert_entity",
            {"entity": entity.model_dump(mode="json")},
        )
        return KnowledgeBaseEntity.model_validate(result)

    async def upsert_relation(self, relation: KnowledgeBaseRelation) -> KnowledgeBaseRelation:
        result = await self.mcp_client.call_tool(
            self.server_name,
            "upsert_relation",
            {"relation": relation.model_dump(mode="json")},
        )
        return KnowledgeBaseRelation.model_validate(result)

    async def link_note_to_state(self, note_id: str, state_object_id: str) -> None:
        await self.mcp_client.call_tool(
            self.server_name,
            "link_note_to_state",
            {"note_id": note_id, "state_object_id": state_object_id},
        )

