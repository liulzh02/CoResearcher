## Why

CoResearcher needs a deterministic context-management and compression layer so long-running research conversations can stay coherent without flooding the LLM window with raw history, long papers, tool logs, and recalled memory. The system must preserve the latest user request verbatim, prefer reversible references over lossy summaries, and defend against prompt-injection risks from recalled memory, tools, papers, and external knowledge sources.

## What Changes

- Introduce a Context Builder that assembles a minimal high-signal ContextPack for each LLM call.
- Define prompt ordering rules where stable runtime rules come first and the latest user message is the final verbatim user message.
- Add layered compression policies for conversation history, tool outputs, long documents, evidence, memory, and Subagent results.
- Add locator-first handling for papers, files, URLs, artifacts, notes, transcripts, tool calls, and database records.
- Add dynamic context block fencing and reserved-tag sanitization for recalled memory and other untrusted context blocks.
- Ensure Skill content is injected as task context, not as a system message, while permissions remain enforced by backend policy.
- Define context isolation rules so Subagents receive task-specific slices and return structured results with references instead of raw logs.

## Capabilities

### New Capabilities

- `context-management`: Builds, compresses, fences, and orders LLM context for research workflows while preserving retrievability and instruction priority.

### Modified Capabilities

- None.

## Impact

- Adds backend context assembly components for ContextPack building, token budgeting, retrieval selection, compression, and rendering.
- Affects LLM request construction for the Research Director and all Subagents.
- Integrates with session persistence, research memory, evidence stores, tool-output storage, skill runtime, and LangGraph node execution.
- Introduces safety requirements for dynamic context sanitization and prompt-injection-resistant block rendering.

## 中文说明

CoResearcher 需要一个专门的上下文管理与压缩层，用来处理长时间科研对话里的历史消息、论文、工具输出、记忆、证据和 Skill 内容。核心原则是：上下文窗口只放下一步推理最需要的高信号信息；能通过 URL、路径、message_id、artifact_id 找回的内容优先保留引用；用户最新问题必须原文保留并放在最终用户消息位置；记忆、工具输出、外部知识和论文摘录都要视为不可信背景资料，进入 prompt 前需要用 fence tag 包裹并清洗保留标签，避免“召回内容”伪装成新的用户指令。
