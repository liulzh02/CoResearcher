from __future__ import annotations

from pathlib import Path
from typing import Protocol

from coresearcher.domain.state import ResearchThread


class ResearchRepository(Protocol):
    async def create(self, thread: ResearchThread) -> ResearchThread: ...

    async def get(self, thread_id: str, user_id: str | None = None) -> ResearchThread | None: ...

    async def save(self, thread: ResearchThread) -> ResearchThread: ...

    async def list(self, user_id: str | None = None) -> list[ResearchThread]: ...


class InMemoryResearchRepository:
    def __init__(self) -> None:
        self._threads: dict[str, ResearchThread] = {}

    async def create(self, thread: ResearchThread) -> ResearchThread:
        self._threads[thread.id] = thread
        return thread

    async def get(self, thread_id: str, user_id: str | None = None) -> ResearchThread | None:
        thread = self._threads.get(thread_id)
        if not thread:
            return None
        if user_id and thread.user_id != user_id:
            return None
        return thread.model_copy(deep=True)

    async def save(self, thread: ResearchThread) -> ResearchThread:
        thread.state.touch()
        self._threads[thread.id] = thread.model_copy(deep=True)
        return thread

    async def list(self, user_id: str | None = None) -> list[ResearchThread]:
        threads = list(self._threads.values())
        if user_id:
            threads = [thread for thread in threads if thread.user_id == user_id]
        return [thread.model_copy(deep=True) for thread in threads]


class JsonResearchRepository:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, thread_id: str) -> Path:
        return self.root / f"{thread_id}.json"

    async def create(self, thread: ResearchThread) -> ResearchThread:
        return await self.save(thread)

    async def get(self, thread_id: str, user_id: str | None = None) -> ResearchThread | None:
        path = self._path(thread_id)
        if not path.exists():
            return None
        thread = ResearchThread.model_validate_json(path.read_text(encoding="utf-8"))
        if user_id and thread.user_id != user_id:
            return None
        return thread

    async def save(self, thread: ResearchThread) -> ResearchThread:
        thread.state.touch()
        self.root.mkdir(parents=True, exist_ok=True)
        self._path(thread.id).write_text(thread.model_dump_json(indent=2), encoding="utf-8")
        return thread

    async def list(self, user_id: str | None = None) -> list[ResearchThread]:
        threads: list[ResearchThread] = []
        for path in self.root.glob("*.json"):
            thread = ResearchThread.model_validate_json(path.read_text(encoding="utf-8"))
            if not user_id or thread.user_id == user_id:
                threads.append(thread)
        return sorted(threads, key=lambda thread: thread.updated_at, reverse=True)

