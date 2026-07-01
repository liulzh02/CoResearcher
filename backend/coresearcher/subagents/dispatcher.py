from __future__ import annotations

import asyncio
from typing import Any

from pydantic import BaseModel, Field

from coresearcher.domain.events import ResearchEvent, ResearchEventType
from coresearcher.domain.state import SourceLocator, new_id
from coresearcher.subagents.registry import SubagentRegistry, default_subagent_registry


class SubagentTask(BaseModel):
    id: str = Field(default_factory=lambda: new_id("subtask"))
    subagent_name: str
    description: str
    payload: dict[str, Any] = Field(default_factory=dict)


class SubagentTaskResult(BaseModel):
    task_id: str
    subagent_name: str
    summary: str
    source_locators: list[SourceLocator] = Field(default_factory=list)
    artifact_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    status: str = "completed"


class SubagentDispatcher:
    def __init__(
        self,
        registry: SubagentRegistry | None = None,
        max_concurrency: int = 3,
    ) -> None:
        self.registry = registry or default_subagent_registry()
        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def dispatch(
        self,
        task: SubagentTask,
        *,
        thread_id: str,
        run_id: str,
    ) -> tuple[SubagentTaskResult, list[ResearchEvent]]:
        config = self.registry.get(task.subagent_name)
        if config.allow_subagent_delegation:
            raise ValueError("Recursive subagent delegation is disabled for MVP")

        events = [
            ResearchEvent(
                type=ResearchEventType.SUBAGENT_STARTED,
                thread_id=thread_id,
                run_id=run_id,
                payload={
                    "subagent": config.name,
                    "task_id": task.id,
                    "description": task.description,
                },
            )
        ]
        async with self._semaphore:
            result = SubagentTaskResult(
                task_id=task.id,
                subagent_name=config.name,
                summary=f"{config.name} completed task: {task.description}",
                limitations=["MVP fake subagent runtime; no live provider or external tools used."],
            )
        events.append(
            ResearchEvent(
                type=ResearchEventType.SUBAGENT_COMPLETED,
                thread_id=thread_id,
                run_id=run_id,
                payload={
                    "subagent": config.name,
                    "task_id": task.id,
                    "status": result.status,
                    "result_summary": result.summary,
                    "artifact_ids": result.artifact_ids,
                },
            )
        )
        return result, events

    async def dispatch_many(
        self,
        tasks: list[SubagentTask],
        *,
        thread_id: str,
        run_id: str,
    ) -> tuple[list[SubagentTaskResult], list[ResearchEvent]]:
        pairs = await asyncio.gather(
            *(self.dispatch(task, thread_id=thread_id, run_id=run_id) for task in tasks)
        )
        results: list[SubagentTaskResult] = []
        events: list[ResearchEvent] = []
        for result, task_events in pairs:
            results.append(result)
            events.extend(task_events)
        return results, events

