from __future__ import annotations

import asyncio
from typing import Any

from pydantic import BaseModel, Field

from coresearcher.context import ContextBuilder, ContextPack
from coresearcher.domain.events import ResearchEvent, ResearchEventType
from coresearcher.domain.state import SourceLocator, SourceType, new_id
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
    execution_observation: dict[str, Any] = Field(default_factory=dict)
    source_locators: list[SourceLocator] = Field(default_factory=list)
    artifact_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    status: str = "completed"
    context_pack: ContextPack | None = None


class SubagentDispatcher:
    def __init__(
        self,
        registry: SubagentRegistry | None = None,
        max_concurrency: int = 3,
        context_builder: ContextBuilder | None = None,
    ) -> None:
        self.registry = registry or default_subagent_registry()
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self.context_builder = context_builder or ContextBuilder()

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

        context_pack = self.context_builder.build_subagent_pack(
            task=task,
            latest_user_message=task.description,
        )
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
            execution_observation: dict[str, Any] = {}
            limitations = ["MVP fake subagent runtime; no live provider or external tools used."]
            if config.name == "coding-researcher":
                execution_observation = {
                    "commands_run": [],
                    "environment": "MVP simulated coding runtime; no isolated execution provider used.",
                    "inputs": task.payload.get("inputs", "not provided"),
                    "observed_output": f"No code was executed for task: {task.description}",
                    "failure_logs": [],
                    "limitations": [
                        "This is a bounded execution observation stub.",
                        "It is not authoritative research evidence by itself.",
                    ],
                    "confidence": "low",
                }
                limitations.append(
                    "Coding observation is not authoritative and not standalone proof of a research claim."
                )
            result = SubagentTaskResult(
                task_id=task.id,
                subagent_name=config.name,
                summary=f"{config.name} completed task: {task.description}",
                execution_observation=execution_observation,
                source_locators=[
                    SourceLocator(
                        type=SourceType.TOOL_CALL,
                        id=task.id,
                        title=f"Subagent task: {config.name}",
                        metadata={"subagent": config.name},
                    )
                ],
                limitations=limitations,
                context_pack=context_pack,
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

    def run_sync(
        self,
        task: SubagentTask,
        *,
        thread_id: str,
        run_id: str,
    ) -> tuple[SubagentTaskResult, list[ResearchEvent]]:
        return asyncio.run(self.dispatch(task, thread_id=thread_id, run_id=run_id))

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
