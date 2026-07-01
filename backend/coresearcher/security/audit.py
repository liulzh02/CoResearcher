from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from coresearcher.domain.state import new_id, utc_now


class AuditRecord(BaseModel):
    id: str = Field(default_factory=lambda: new_id("audit"))
    type: str
    user_id: str | None = None
    thread_id: str | None = None
    run_id: str | None = None
    actor: str | None = None
    status: str = "ok"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class AuditSink:
    def __init__(self) -> None:
        self.records: list[AuditRecord] = []

    def append(self, record: AuditRecord) -> AuditRecord:
        self.records.append(record)
        return record

    def list(self) -> list[AuditRecord]:
        return list(self.records)

