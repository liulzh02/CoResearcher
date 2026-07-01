## 1. Memory Models And Configuration

- [ ] 1.1 Define typed models for session memory records, internal memory files, candidate memory entries, provenance references, and memory validation results.
- [ ] 1.2 Add memory configuration for SQLite session storage, Markdown memory root, global memory path, per-research memory path template, candidate memory files, extraction triggers, and debounce settings.
- [ ] 1.3 Add tests for memory configuration defaults, invalid paths, missing required fields, and disabled memory features.

## 2. Session Memory Persistence

- [ ] 2.1 Implement repository interfaces for messages, run events, graph checkpoints, research state references, artifact metadata, and evidence links.
- [ ] 2.2 Implement the MVP SQLite-backed session memory repositories behind the interfaces.
- [ ] 2.3 Add thread-scoped query helpers for context building, run replay, and interrupted-run recovery.
- [ ] 2.4 Add tests for session resume, run event ordering, thread scoping, checkpoint lookup, and repository failure handling.

## 3. Markdown Internal Memory

- [ ] 3.1 Implement Markdown memory file parsing with required frontmatter validation for scope, type, version, status, timestamps, and identifiers.
- [ ] 3.2 Implement `memory/global/user_memory.md` creation, loading, validation, and update helpers.
- [ ] 3.3 Implement `memory/research/<research_id>/research_memory.md` creation, loading, validation, and update helpers.
- [ ] 3.4 Add tests for valid memory files, missing frontmatter, malformed frontmatter, user-edited body content, and scope isolation.

## 4. Candidate Memory Workflow

- [ ] 4.1 Implement candidate memory file handling for `memory/global/candidates.md` and `memory/research/<research_id>/candidates.md`.
- [ ] 4.2 Implement candidate memory creation from memory extraction output with provenance, confidence, target scope, and status.
- [ ] 4.3 Implement candidate promotion to global user memory or per-research memory while preserving provenance.
- [ ] 4.4 Implement candidate rejection so rejected entries are excluded from normal runtime context retrieval.
- [ ] 4.5 Add tests for candidate creation, promotion, rejection, provenance preservation, and conflict handling.

## 5. Memory Extraction

- [ ] 5.1 Define the memory extraction prompt and output schema for candidate user preferences, project facts, decisions, research goals, method preferences, and open questions.
- [ ] 5.2 Implement event-driven extraction triggers for user turns, run completion, important research state updates, artifact creation, decisions, explicit remember requests, and token-pressure events.
- [ ] 5.3 Implement extraction debounce or batching so closely spaced events do not run redundant memory extraction jobs.
- [ ] 5.4 Ensure extracted memory never overrides raw messages, structured research state, evidence records, decisions, or artifacts.
- [ ] 5.5 Add tests for trigger selection, debounce behavior, extracted-memory conflicts, and source-of-truth precedence.

## 6. Context Builder Integration

- [ ] 6.1 Implement layered memory retrieval in priority order: current thread state, per-research memory, global user memory, external knowledge-base memory, and candidate memory only for review workflows.
- [ ] 6.2 Add relevance filtering so global user memory and external notes are included only when useful for the active research turn.
- [ ] 6.3 Add guardrails that treat external notes and Markdown body content as data, not system instructions.
- [ ] 6.4 Add tests for layered retrieval, candidate exclusion, cross-research isolation, global memory inclusion, and prompt-injection text handling.

## 7. External Knowledge-Base Adapter

- [ ] 7.1 Extend the provider-neutral knowledge-base adapter contract with memory-oriented note retrieval and metadata mapping.
- [ ] 7.2 Implement Obsidian-over-MCP memory note reads behind the adapter without exposing Obsidian-specific behavior to core memory logic.
- [ ] 7.3 Link external note metadata to memory provenance and research state references where available.
- [ ] 7.4 Add tests with a fake adapter for note retrieval, metadata mapping, adapter failures, and untrusted note handling.

## 8. API, Documentation, And Verification

- [ ] 8.1 Add internal service APIs for inspecting global memory, per-research memory, candidate memory, and provenance records.
- [ ] 8.2 Add documentation for memory directory layout, Markdown frontmatter schema, candidate review workflow, and local setup.
- [ ] 8.3 Add deterministic integration tests covering session resume, memory extraction, candidate promotion, context building, and external note retrieval.
- [ ] 8.4 Run the fastest relevant validation and test commands, and record them in the implementation summary.

---

# 中文版（阅读参考）

说明：下面是任务清单的中文阅读版。为了不影响 OpenSpec 对任务复选框的解析，这里使用普通列表，不使用 `- [ ]` 格式。

## 1. 记忆模型与配置

- 1.1 定义会话记忆记录、内部记忆文件、候选记忆条目、来源引用和记忆校验结果的类型模型。
- 1.2 增加记忆配置，覆盖 SQLite 会话存储、Markdown 记忆根目录、全局记忆路径、单研究记忆路径模板、候选记忆文件、提炼触发器和 debounce 设置。
- 1.3 添加测试，覆盖记忆配置默认值、无效路径、缺失必填字段和关闭记忆功能的场景。

## 2. 会话记忆持久化

- 2.1 实现消息、运行事件、图 checkpoint、研究状态引用、产物元数据和证据链接的 repository 接口。
- 2.2 在接口之后实现 MVP 版 SQLite-backed 会话记忆 repository。
- 2.3 增加按线程查询的辅助逻辑，用于 Context Builder、run 回放和中断 run 恢复。
- 2.4 添加测试，覆盖会话恢复、运行事件排序、线程范围、checkpoint 查找和 repository 失败处理。

## 3. Markdown 内部记忆

- 3.1 实现 Markdown 记忆文件解析，并校验 scope、type、version、status、时间戳和标识符等必需 frontmatter。
- 3.2 实现 `memory/global/user_memory.md` 的创建、加载、校验和更新辅助逻辑。
- 3.3 实现 `memory/research/<research_id>/research_memory.md` 的创建、加载、校验和更新辅助逻辑。
- 3.4 添加测试，覆盖有效记忆文件、缺失 frontmatter、frontmatter 格式错误、用户手改正文和作用域隔离。

## 4. 候选记忆流程

- 4.1 实现 `memory/global/candidates.md` 和 `memory/research/<research_id>/candidates.md` 的候选记忆文件处理。
- 4.2 从记忆提炼输出创建候选记忆，并记录来源、置信度、目标 scope 和状态。
- 4.3 实现候选记忆提升到全局用户记忆或单研究记忆，并保留来源。
- 4.4 实现候选记忆拒绝逻辑，确保被拒绝条目不会进入普通运行时上下文检索。
- 4.5 添加测试，覆盖候选创建、提升、拒绝、来源保留和冲突处理。

## 5. 记忆提炼

- 5.1 定义记忆提炼 Prompt 和输出 schema，覆盖候选用户偏好、项目事实、决策、研究目标、方法偏好和开放问题。
- 5.2 实现事件驱动提炼触发器，包括用户 turn、run 完成、重要研究状态更新、产物创建、决策、明确记住请求和 token 压力事件。
- 5.3 实现提炼 debounce 或批处理，避免密集事件重复运行记忆提炼任务。
- 5.4 确保提炼出的记忆永远不能覆盖原始消息、结构化研究状态、证据记录、决策或产物。
- 5.5 添加测试，覆盖触发选择、debounce 行为、提炼记忆冲突和事实源优先级。

## 6. Context Builder 集成

- 6.1 实现分层记忆检索，优先级为当前线程状态、单研究记忆、全局用户记忆、外部知识库记忆；候选记忆只在 review 流程中检索。
- 6.2 增加相关性过滤，确保全局用户记忆和外部笔记只在对当前研究 turn 有帮助时进入上下文。
- 6.3 增加防护，将外部笔记和 Markdown 正文视为数据，而不是系统指令。
- 6.4 添加测试，覆盖分层检索、候选排除、跨研究隔离、全局记忆引入和 prompt injection 文本处理。

## 7. 外部知识库 Adapter

- 7.1 扩展 Provider 无关的知识库 adapter 契约，增加面向记忆的笔记检索和元数据映射。
- 7.2 在 adapter 后实现 Obsidian-over-MCP 记忆笔记读取，不向核心记忆逻辑暴露 Obsidian 特有行为。
- 7.3 在可用时，将外部笔记元数据链接到记忆来源和研究状态引用。
- 7.4 使用 fake adapter 添加测试，覆盖笔记检索、元数据映射、adapter 失败和不可信笔记处理。

## 8. API、文档与验证

- 8.1 增加内部服务 API，用于检查全局记忆、单研究记忆、候选记忆和来源记录。
- 8.2 添加文档，说明记忆目录结构、Markdown frontmatter schema、候选记忆 review 流程和本地设置。
- 8.3 添加确定性集成测试，覆盖会话恢复、记忆提炼、候选提升、上下文构建和外部笔记检索。
- 8.4 运行最快相关校验和测试命令，并在实现总结中记录。
