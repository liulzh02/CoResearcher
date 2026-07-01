## Why

CoResearcher needs a memory architecture that can support long-running scientific collaboration without losing traceability, user preferences, or project-specific decisions. The current deep research architecture separates chat messages and research state, but it does not yet define how session memory, internal long-term memory, and external knowledge-base memory should work together.

## What Changes

- Introduce a dedicated research memory capability for session memory, internal memory, and external knowledge-base memory.
- Persist session memory and runtime recovery data in a local structured store, with SQLite as the MVP default.
- Store long-term internal memory as human-readable Markdown files with structured frontmatter.
- Split long-term internal memory into global user memory and per-research memory so project facts do not pollute global user preferences.
- Add candidate memory files so LLM-extracted memories are reviewed, validated, or promoted before becoming durable memory.
- Treat LLM-based memory extraction as a derived helper, not as the source of truth.
- Integrate external knowledge-base memory through a provider-neutral adapter, with Obsidian-over-MCP as the first MVP adapter.

## Capabilities

### New Capabilities

- `research-memory`: Covers session memory persistence, internal Markdown memory files, candidate memory promotion, global user memory, per-research memory, external knowledge-base memory, and memory retrieval for context building.

### Modified Capabilities

None. This change introduces a new memory capability that complements the existing deep research assistant planning change.

## Impact

- Affected backend areas: persistence repositories, context builder, memory extraction workflow, knowledge-base adapter, and configuration.
- Affected storage areas: SQLite session store, local Markdown memory directory, artifact files, and external knowledge-base adapter metadata.
- Expected dependencies: YAML/frontmatter parsing, local file storage, SQLite repository layer, and optional Obsidian MCP integration.
- Security and quality considerations: candidate memories must not be silently promoted to durable memory; memory records need provenance; untrusted source text must not override system behavior; user-editable Markdown memory should be validated before runtime use.

---

# 中文版（阅读参考）

## 背景与动机

CoResearcher 需要一套记忆架构，用来支持长期科研协作，同时保留可追溯性、用户偏好和项目内决策。当前深度研究架构已经区分聊天消息和研究状态，但还没有明确会话记忆、内部长期记忆和外部知识库记忆如何协作。

## 变更内容

- 引入独立的 research memory 能力，覆盖会话记忆、内部记忆和外部知识库记忆。
- 将会话记忆和运行时恢复数据持久化到本地结构化存储中，MVP 默认使用 SQLite。
- 将长期内部记忆保存为带结构化 frontmatter 的 Markdown 文件，保证可读、可编辑、可版本管理。
- 将长期内部记忆拆分为全局用户记忆和单个研究的内部记忆，避免项目事实污染用户全局偏好。
- 增加 candidate memory 文件，LLM 提炼出的记忆先进入候选区，经过校验、确认或提升后再成为持久记忆。
- 将 LLM 记忆提炼视为派生辅助能力，而不是事实源。
- 通过 Provider 无关的 adapter 接入外部知识库，MVP 第一版使用 Obsidian-over-MCP。

## 能力范围

### 新增能力

- `research-memory`：覆盖会话记忆持久化、内部 Markdown 记忆文件、候选记忆提升、全局用户记忆、单研究记忆、外部知识库记忆，以及上下文构建中的记忆检索。

### 修改能力

无。本变更新增记忆能力，用来补充现有的 deep research assistant 规划。

## 影响范围

- 影响后端区域：持久化 repository、Context Builder、记忆提炼流程、知识库 adapter 和配置系统。
- 影响存储区域：SQLite 会话存储、本地 Markdown 记忆目录、产物文件和外部知识库 adapter 元数据。
- 预期依赖：YAML/frontmatter 解析、本地文件存储、SQLite repository 层，以及可选的 Obsidian MCP 集成。
- 安全与质量要求：候选记忆不能静默提升为持久记忆；记忆记录需要来源；不可信来源文本不能覆盖系统行为；用户可编辑的 Markdown 记忆在运行时使用前需要校验。
