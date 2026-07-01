from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from coresearcher.domain.events import ResearchEvent
from coresearcher.domain.state import ChatMessage


class StateReferenceRecord(BaseModel):
    thread_id: str
    reference_id: str
    payload: dict[str, Any] = Field(default_factory=dict)


class ArtifactMetadataRecord(BaseModel):
    thread_id: str
    artifact_id: str
    payload: dict[str, Any] = Field(default_factory=dict)


class EvidenceLinkRecord(BaseModel):
    thread_id: str
    claim_id: str
    evidence_id: str


class SessionMemoryBundle(BaseModel):
    messages: list[ChatMessage] = Field(default_factory=list)
    events: list[ResearchEvent] = Field(default_factory=list)
    state_references: list[StateReferenceRecord] = Field(default_factory=list)
    artifact_metadata: list[ArtifactMetadataRecord] = Field(default_factory=list)
    evidence_links: list[EvidenceLinkRecord] = Field(default_factory=list)


class SQLiteSessionMemoryRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    research_id TEXT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS run_events (
                    id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS checkpoints (
                    thread_id TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    node_name TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY(thread_id, run_id, node_name)
                );
                CREATE TABLE IF NOT EXISTS state_references (
                    thread_id TEXT NOT NULL,
                    reference_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY(thread_id, reference_id)
                );
                CREATE TABLE IF NOT EXISTS artifact_metadata (
                    thread_id TEXT NOT NULL,
                    artifact_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY(thread_id, artifact_id)
                );
                CREATE TABLE IF NOT EXISTS evidence_links (
                    thread_id TEXT NOT NULL,
                    claim_id TEXT NOT NULL,
                    evidence_id TEXT NOT NULL,
                    PRIMARY KEY(thread_id, claim_id, evidence_id)
                );
                """
            )

    def append_message(
        self,
        thread_id: str,
        message: ChatMessage,
        research_id: str | None = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO messages
                (id, thread_id, research_id, role, content, created_at, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message.id,
                    thread_id,
                    research_id,
                    message.role,
                    message.content,
                    message.created_at.isoformat(),
                    message.model_dump_json(),
                ),
            )

    def append_event(self, event: ResearchEvent) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO run_events
                (id, thread_id, run_id, type, created_at, payload)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.thread_id,
                    event.run_id,
                    event.type.value,
                    event.created_at.isoformat(),
                    event.model_dump_json(),
                ),
            )

    def save_checkpoint(
        self,
        thread_id: str,
        run_id: str,
        node_name: str,
        payload: dict[str, Any],
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO checkpoints
                (thread_id, run_id, node_name, payload)
                VALUES (?, ?, ?, ?)
                """,
                (thread_id, run_id, node_name, json.dumps(payload)),
            )

    def get_checkpoint(self, thread_id: str, run_id: str, node_name: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT payload FROM checkpoints
                WHERE thread_id = ? AND run_id = ? AND node_name = ?
                """,
                (thread_id, run_id, node_name),
            ).fetchone()
        return json.loads(row["payload"]) if row else None

    def save_state_reference(
        self,
        thread_id: str,
        reference_id: str,
        payload: dict[str, Any],
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO state_references
                (thread_id, reference_id, payload)
                VALUES (?, ?, ?)
                """,
                (thread_id, reference_id, json.dumps(payload)),
            )

    def save_artifact_metadata(
        self,
        thread_id: str,
        artifact_id: str,
        payload: dict[str, Any],
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO artifact_metadata
                (thread_id, artifact_id, payload)
                VALUES (?, ?, ?)
                """,
                (thread_id, artifact_id, json.dumps(payload)),
            )

    def save_evidence_link(self, thread_id: str, claim_id: str, evidence_id: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO evidence_links
                (thread_id, claim_id, evidence_id)
                VALUES (?, ?, ?)
                """,
                (thread_id, claim_id, evidence_id),
            )

    def load_thread_memory(self, thread_id: str) -> SessionMemoryBundle:
        with self._connect() as conn:
            message_rows = conn.execute(
                "SELECT payload FROM messages WHERE thread_id = ? ORDER BY created_at ASC",
                (thread_id,),
            ).fetchall()
            event_rows = conn.execute(
                "SELECT payload FROM run_events WHERE thread_id = ? ORDER BY created_at ASC",
                (thread_id,),
            ).fetchall()
            state_rows = conn.execute(
                "SELECT * FROM state_references WHERE thread_id = ?",
                (thread_id,),
            ).fetchall()
            artifact_rows = conn.execute(
                "SELECT * FROM artifact_metadata WHERE thread_id = ?",
                (thread_id,),
            ).fetchall()
            evidence_rows = conn.execute(
                "SELECT * FROM evidence_links WHERE thread_id = ?",
                (thread_id,),
            ).fetchall()

        return SessionMemoryBundle(
            messages=[
                ChatMessage.model_validate_json(row["payload"])
                for row in message_rows
            ],
            events=[
                ResearchEvent.model_validate_json(row["payload"])
                for row in event_rows
            ],
            state_references=[
                StateReferenceRecord(
                    thread_id=row["thread_id"],
                    reference_id=row["reference_id"],
                    payload=json.loads(row["payload"]),
                )
                for row in state_rows
            ],
            artifact_metadata=[
                ArtifactMetadataRecord(
                    thread_id=row["thread_id"],
                    artifact_id=row["artifact_id"],
                    payload=json.loads(row["payload"]),
                )
                for row in artifact_rows
            ],
            evidence_links=[
                EvidenceLinkRecord(
                    thread_id=row["thread_id"],
                    claim_id=row["claim_id"],
                    evidence_id=row["evidence_id"],
                )
                for row in evidence_rows
            ],
        )

