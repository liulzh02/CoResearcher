# Research Memory Architecture

CoResearcher separates memory into three layers:

- Session memory: raw messages, run events, graph checkpoints, research state references, artifact metadata, and evidence links. MVP storage uses SQLite behind repository interfaces.
- Internal long-term memory: local Markdown files with required YAML frontmatter.
- External knowledge-base memory: notes and graph metadata accessed through provider-neutral adapters, with Obsidian-over-MCP as the first adapter shape.

## Directory Layout

```text
memory/
  session_memory.sqlite3
  global/
    user_memory.md
    candidates.md
  research/
    <research_id>/
      research_memory.md
      candidates.md
```

## Frontmatter Schema

Every Markdown memory file starts with YAML frontmatter:

```yaml
---
scope: global | research
type: user_memory | research_memory | candidates
version: 1
status: active
id: memfile_xxx
user_id: local-user
research_id: optional-for-research-scope
created_at: "2026-07-01T00:00:00Z"
updated_at: "2026-07-01T00:00:00Z"
---
```

Missing or malformed frontmatter prevents the file from being used as runtime context. The body remains human-editable Markdown.

## Candidate Review Workflow

LLM-extracted memory is never written directly to durable global or research memory. It first becomes a candidate:

```text
turn / run / decision / artifact / token pressure
  -> extraction output
  -> candidate memory with provenance and confidence
  -> promote or reject
  -> durable Markdown memory only after promotion
```

Rejected candidates are excluded from normal context retrieval.

## Retrieval Order

Normal research context retrieves memory in this order:

1. Current thread state.
2. Per-research memory.
3. Global user memory when relevant.
4. External knowledge-base notes when relevant.
5. Candidate memory only in review or promotion workflows.

External note content and Markdown body content are treated as untrusted data, not system instructions.

## Local Setup

The memory system uses standard library SQLite and local Markdown files. No provider credentials are required for the fake adapter tests.

Run memory tests:

```bash
python -m pytest tests/test_memory_architecture.py
```

Run all tests:

```bash
python -m pytest
```

## 中文说明

研究记忆分为会话记忆、内部长期记忆和外部知识库记忆。会话记忆使用 SQLite 保存消息、run 事件、checkpoint、状态引用、artifact 元数据和 evidence 链接，适合恢复和回放。内部长期记忆使用带 frontmatter 的 Markdown 文件，分为 `memory/global/user_memory.md` 和 `memory/research/<research_id>/research_memory.md`，避免项目事实污染全局用户偏好。LLM 提炼出的记忆只能先进入 candidates 文件，经过确认或显式规则后才能 promotion。Context Builder 检索时按当前线程状态、单研究记忆、全局记忆、外部知识库笔记的顺序组装，默认排除未提升的候选记忆。

