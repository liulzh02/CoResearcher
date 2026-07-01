## Context

The deep research assistant baseline already separates chat messages, structured research state, evidence, artifacts, and knowledge-base adapters. This change adds a more explicit memory architecture so CoResearcher can preserve conversation continuity, project-specific research understanding, user research habits, and external knowledge-base links across long-running research work.

The design assumes a local-first MVP. Session memory and runtime state need reliable append/query behavior, while long-term internal memory should remain readable and editable by the researcher. External knowledge should be accessible through adapters, starting with Obsidian over MCP, without making Obsidian the only durable source of truth.

## Goals / Non-Goals

**Goals:**

- Separate session memory, internal memory, and external knowledge-base memory.
- Persist session memory, run events, graph checkpoints, and structured research state in SQLite-backed repositories for the MVP.
- Store internal long-term memory in Markdown files with required frontmatter and validation.
- Split internal memory into global user memory and per-research memory.
- Use candidate memory files for LLM-extracted memory before promotion.
- Keep memory provenance explicit so durable memory can be traced back to messages, decisions, evidence, artifacts, or user confirmation.
- Allow the context builder to retrieve memory in a predictable priority order.

**Non-Goals:**

- This change does not implement multi-user enterprise memory permissions.
- This change does not require a vector database in the MVP.
- This change does not make LLM summaries the source of truth for memory.
- This change does not replace structured research state, evidence records, or artifacts with Markdown memory files.
- This change does not require Obsidian; Obsidian is the first external knowledge-base adapter.

## Decisions

### Use SQLite for session memory and runtime recovery

Session memory includes raw messages, run events, LangGraph checkpoints, research state snapshots, artifact metadata, and evidence links. These records need frequent appends, thread-scoped queries, replay, and recovery behavior, so SQLite is the MVP default behind repository interfaces.

Alternative considered: storing session memory only as Markdown or JSONL files. This is simpler to inspect but becomes awkward for run replay, thread-scoped queries, checkpoint recovery, event ordering, and future API access.

### Store internal long-term memory as Markdown with frontmatter

Internal long-term memory should be human-readable and editable. Markdown works well for local research workflows, version control, and Obsidian compatibility. Each memory file must include structured frontmatter so the runtime can validate scope, type, version, status, and update metadata before using it.

Alternative considered: storing all internal memory in SQLite. That is easier to query but makes memory less transparent to the researcher and less aligned with note-taking workflows.

### Split long-term internal memory into global and per-research files

Internal memory will use two durable files:

- `memory/global/user_memory.md`: global research habits, writing preferences, tool preferences, stable user preferences, and cross-project working style.
- `memory/research/<research_id>/research_memory.md`: project-specific research goal, architecture decisions, confirmed assumptions, open questions, key evidence trails, and research-specific constraints.

This split prevents one research project's facts from polluting global user behavior. The context builder can include both files when relevant, but they have different scopes and promotion rules.

Alternative considered: one combined long-term memory file. That is easier initially but causes scope confusion and makes stale project facts too easy to reuse globally.

### Use candidate memory before durable memory

LLM-extracted memory must first be written as candidate memory, not directly into durable memory files. Candidate memory can be promoted after user confirmation, explicit rule validation, or system-controlled promotion for low-risk facts with clear provenance.

Initial layout:

```text
memory/
  global/
    user_memory.md
    candidates.md
  research/
    <research_id>/
      research_memory.md
      candidates.md
```

Alternative considered: automatically appending every extracted memory to durable files. This is faster but risks storing guesses, temporary preferences, unreviewed source claims, or prompt-injection content as long-term memory.

### Treat LLM memory extraction as a derived helper

LLM extraction can summarize and propose memory records after a turn, run completion, important research state update, artifact creation, or explicit "remember this" instruction. It must not replace raw messages, research state, evidence records, or decisions. Extracted memory carries provenance and confidence.

The trigger model should be event-driven with throttling, not a blind fixed interval. A 30-second debounce can limit cost, but the real triggers should be user turns, run completion, state updates, token pressure, explicit user instruction, and artifact/decision creation.

Alternative considered: running a memory summarizer every 30 seconds as the core memory mechanism. This can be useful in a general chat agent, but scientific work needs stronger provenance and less silent mutation.

### Retrieve memory in layered priority order

The context builder should assemble memory in this order:

1. Current thread messages and ResearchState.
2. Per-research `research_memory.md`.
3. Global `user_memory.md`.
4. Relevant external knowledge-base notes or graph entities.
5. Candidate memory only when explicitly reviewing or promoting memory.

This order keeps immediate research state authoritative while still allowing global preferences and external notes to assist context building.

### Keep external knowledge-base memory adapter-driven

External memory should be accessed through a `KnowledgeBaseAdapter` rather than direct Obsidian-specific calls in core logic. The MVP adapter can use Obsidian over MCP to read and write notes, but core memory objects should retain stable IDs and provenance so later adapters or custom knowledge graphs can be added.

Alternative considered: making Obsidian the only memory store. That is attractive for a local researcher workflow, but it would make runtime recovery, validation, testing, and future self-hosted knowledge graphs harder.

## Risks / Trade-offs

- Markdown files can become inconsistent → validate frontmatter and body sections before runtime use.
- Candidate memory may pile up → expose review status and periodically surface candidates for confirmation or rejection.
- SQLite and Markdown can diverge → store provenance and use explicit promotion/update operations rather than silent background edits.
- User-edited Markdown can break expected structure → accept readable content but warn on invalid frontmatter or missing required sections.
- Global memory may overfit to one research project → only promote project facts globally through explicit confirmation.
- External notes may contain prompt injection → treat note content as untrusted source text and never as runtime instructions.
- File-based memory may not scale to multi-user deployment → keep repository and adapter interfaces so storage can evolve later.

## Migration Plan

This is a new memory capability, so there is no existing production data migration.

1. Add typed memory models and repository interfaces.
2. Add SQLite-backed session memory repositories.
3. Add Markdown-backed internal memory repositories with frontmatter validation.
4. Add candidate memory extraction and promotion workflow.
5. Add context builder retrieval across ResearchState, research memory, global user memory, and external knowledge-base notes.
6. Add Obsidian-over-MCP adapter behind the generic knowledge-base interface.

Rollback strategy: disable memory extraction and external knowledge-base adapter first; keep SQLite session records and Markdown files as readable local data.

## Open Questions

- Should candidate memory promotion require explicit user confirmation in the MVP, or can low-risk preferences be auto-promoted with provenance?
- Should Markdown memory files be one file per scope or split by type once they grow large?
- Should embeddings be added in a later change for semantic memory retrieval?
- Should the UI expose candidate memory review in the first frontend iteration or defer it to a later memory management view?

---

# 中文版（阅读参考）

## 上下文

深度研究助手基线已经区分聊天消息、结构化研究状态、证据、产物和知识库 adapter。本变更进一步明确记忆架构，让 CoResearcher 能在长期科研工作中保留对话连续性、单个研究的上下文、用户研究习惯，以及外部知识库链接。

本设计假设第一版是本地优先。会话记忆和运行时状态需要可靠的追加、查询和恢复能力；长期内部记忆则应该让研究者能直接阅读、编辑和版本管理。外部知识通过 adapter 接入，第一版使用 Obsidian-over-MCP，但不把 Obsidian 作为唯一事实源。

## 目标 / 非目标

**目标：**

- 区分会话记忆、内部记忆和外部知识库记忆。
- MVP 使用 SQLite-backed repository 持久化会话记忆、运行事件、图 checkpoint 和结构化研究状态。
- 使用带 frontmatter 的 Markdown 文件保存内部长期记忆，并进行校验。
- 将内部记忆拆分为全局用户记忆和单研究记忆。
- LLM 提炼出的记忆先进入 candidate memory，再提升为正式记忆。
- 记忆必须保留来源，能够追溯到消息、决策、证据、产物或用户确认。
- Context Builder 能按稳定优先级检索记忆。

**非目标：**

- 本变更不实现多用户企业级记忆权限。
- MVP 不要求向量数据库。
- LLM 摘要不是记忆事实源。
- Markdown 记忆文件不替代结构化研究状态、证据记录或产物。
- Obsidian 不是强依赖，它只是第一版外部知识库 adapter。

## 设计决策

### 会话记忆和运行时恢复使用 SQLite

会话记忆包括原始消息、运行事件、LangGraph checkpoint、研究状态快照、产物元数据和证据链接。这些数据需要频繁追加、按线程查询、回放和恢复，因此 MVP 默认使用 SQLite，并通过 repository 接口隔离。

备选方案是只用 Markdown 或 JSONL 文件保存会话记忆。这样更容易查看，但在运行回放、线程查询、checkpoint 恢复、事件排序和未来 API 访问上会变得别扭。

### 内部长期记忆使用带 frontmatter 的 Markdown

内部长期记忆应该可读、可编辑。Markdown 适合本地科研工作流、版本控制和 Obsidian 兼容。每个记忆文件必须包含结构化 frontmatter，运行时使用前需要校验 scope、type、version、status 和更新时间等信息。

备选方案是把所有内部记忆都放进 SQLite。这样更容易查询，但不够透明，也不贴合笔记工作流。

### 长期内部记忆拆成全局和单研究两个文件

内部记忆使用两个持久文件：

- `memory/global/user_memory.md`：全局研究习惯、写作偏好、工具偏好、稳定用户偏好和跨项目工作风格。
- `memory/research/<research_id>/research_memory.md`：项目研究目标、架构决策、已确认假设、开放问题、关键证据脉络和研究约束。

这个拆分可以避免某个研究项目的事实污染全局用户行为。Context Builder 可以在需要时同时引入两类记忆，但它们的作用域和提升规则不同。

备选方案是使用一个统一长期记忆文件。它初期更简单，但容易造成作用域混淆，也更容易把过期项目事实带到其他研究中。

### 使用 candidate memory 再提升为正式记忆

LLM 提炼出的记忆必须先进入 candidate memory，不能直接写入正式记忆文件。候选记忆可以在用户确认、显式规则校验，或系统控制的低风险提升后进入正式记忆。

初始目录结构：

```text
memory/
  global/
    user_memory.md
    candidates.md
  research/
    <research_id>/
      research_memory.md
      candidates.md
```

备选方案是把所有提炼出的记忆自动追加到正式文件。这样更快，但容易把猜测、临时偏好、未经审查的来源说法或 prompt injection 内容存成长期记忆。

### LLM 记忆提炼只是派生辅助能力

LLM 可以在用户轮次结束、run 完成、重要研究状态更新、产物创建或用户明确说“记住这个”后提炼候选记忆。它不能替代原始消息、研究状态、证据记录或决策。被提炼的记忆必须携带来源和置信度。

触发模型应是事件驱动并带节流，而不是固定间隔盲跑。可以用 30 秒 debounce 控制成本，但真正的触发点应是用户轮次、run 完成、状态更新、token 压力、显式用户指令，以及产物或决策创建。

备选方案是像通用聊天 Agent 一样每 30 秒运行记忆总结器。这对普通聊天有帮助，但科研工作需要更强的来源追踪和更少的静默变更。

### 按层级优先级检索记忆

Context Builder 应按以下顺序组装记忆：

1. 当前线程消息和 ResearchState。
2. 单研究 `research_memory.md`。
3. 全局 `user_memory.md`。
4. 相关外部知识库笔记或图谱实体。
5. 仅在审查或提升记忆时引入 candidate memory。

这个顺序让当前研究状态保持最高权威，同时允许全局偏好和外部笔记辅助上下文构建。

### 外部知识库记忆保持 adapter 驱动

外部记忆应通过 `KnowledgeBaseAdapter` 访问，而不是在核心逻辑中直接调用 Obsidian。MVP adapter 可以通过 MCP 读写 Obsidian 笔记，但核心记忆对象要保留稳定 ID 和来源，方便后续接入其他 adapter 或自研知识图谱。

备选方案是让 Obsidian 成为唯一记忆存储。它很适合本地研究者工作流，但会让运行恢复、校验、测试和未来自研知识图谱变得更困难。

## 风险 / 权衡

- Markdown 文件可能不一致 -> 使用前校验 frontmatter 和正文关键 section。
- 候选记忆可能堆积 -> 暴露 review 状态，并定期提示用户确认或拒绝。
- SQLite 和 Markdown 可能分叉 -> 保留来源，并通过显式提升/更新操作修改记忆，避免后台静默写入。
- 用户手改 Markdown 可能破坏结构 -> 正文可保持宽松，但缺失必要 frontmatter 时给出警告。
- 全局记忆可能过度吸收项目事实 -> 项目事实只有在明确确认后才能提升到全局。
- 外部笔记可能包含 prompt injection -> 将笔记内容视为不可信来源文本，绝不作为运行时指令。
- 文件型记忆不适合多用户大规模部署 -> 保留 repository 和 adapter 接口，方便后续演进。

## 迁移计划

这是新增记忆能力，不涉及已有生产数据迁移。

1. 增加类型化记忆模型和 repository 接口。
2. 增加 SQLite-backed 会话记忆 repository。
3. 增加 Markdown-backed 内部记忆 repository，并校验 frontmatter。
4. 增加候选记忆提炼和提升流程。
5. 增加 Context Builder 对 ResearchState、单研究记忆、全局用户记忆和外部知识库笔记的检索。
6. 在通用知识库接口后增加 Obsidian-over-MCP adapter。

回滚策略：先关闭记忆提炼和外部知识库 adapter；SQLite 会话记录和 Markdown 文件保留为可读本地数据。

## 开放问题

- MVP 阶段 candidate memory 提升是否必须由用户显式确认，还是低风险偏好可以在带来源的情况下自动提升？
- Markdown 记忆文件是否长期保持每个 scope 一个文件，还是内容增多后按类型拆分？
- 是否在后续变更中加入 embedding，用于语义记忆检索？
- 第一版前端是否要暴露候选记忆 review，还是推迟到专门的记忆管理视图？
