## ADDED Requirements

### Requirement: Session memory persists runtime conversation state
The system SHALL persist session memory for each research thread, including raw messages, run events, graph checkpoints, research state references, artifact metadata, and evidence links.

#### Scenario: Session resumes after interruption
- **WHEN** a research run is interrupted and the user later resumes the same thread
- **THEN** the system loads the persisted messages, run events, checkpoint data, and research state references for that thread

#### Scenario: Run events can be replayed
- **WHEN** the user opens a previous research run
- **THEN** the system can replay or inspect stored run events without relying on regenerated assistant prose

### Requirement: Session memory uses structured local persistence
The system SHALL use a structured local persistence layer for MVP session memory, with SQLite as the default implementation behind repository interfaces.

#### Scenario: Thread-scoped memory query
- **WHEN** the context builder requests memory for a specific research thread
- **THEN** the repository returns only records scoped to that thread and related research identifiers

### Requirement: Internal long-term memory uses Markdown files
The system SHALL store internal long-term memory in Markdown files with required frontmatter that identifies scope, type, version, status, and update metadata.

#### Scenario: Valid internal memory file is loaded
- **WHEN** the runtime loads an internal memory file with valid frontmatter and readable body content
- **THEN** the system parses it as memory context for the relevant scope

#### Scenario: Invalid internal memory file is rejected or warned
- **WHEN** an internal memory file is missing required frontmatter fields
- **THEN** the system rejects it for runtime context use or records a validation warning

### Requirement: Global user memory is separate from research memory
The system SHALL separate global user memory from per-research memory.

#### Scenario: Global user memory applies across research threads
- **WHEN** a user starts or resumes any research thread
- **THEN** stable global preferences from `memory/global/user_memory.md` are available to the context builder when relevant

#### Scenario: Research memory stays scoped to one research
- **WHEN** a user works on a different research project
- **THEN** project-specific facts from another `memory/research/<research_id>/research_memory.md` are not included unless explicitly linked or requested

### Requirement: Candidate memory requires promotion
The system SHALL write LLM-extracted memory to candidate memory before it becomes durable global or research memory.

#### Scenario: LLM extracts a new memory candidate
- **WHEN** the memory extractor identifies a possible long-term memory from a turn, run, decision, artifact, or state update
- **THEN** the system records it as candidate memory with provenance, confidence, and target scope

#### Scenario: Candidate memory is promoted
- **WHEN** a candidate memory is confirmed by the user or passes an explicit promotion rule
- **THEN** the system writes it into the appropriate global or per-research memory file and preserves its provenance

#### Scenario: Candidate memory is rejected
- **WHEN** a candidate memory is rejected
- **THEN** the system does not include it in normal runtime context retrieval

### Requirement: Memory records preserve provenance
The system SHALL preserve provenance for durable and candidate memory records, including references to source messages, decisions, evidence, artifacts, or explicit user confirmation when available.

#### Scenario: Memory source is inspected
- **WHEN** the user or system inspects a memory entry
- **THEN** the system can show the source reference or mark the source as unavailable

### Requirement: LLM memory extraction is derived, not authoritative
The system MUST treat LLM-extracted memory as derived candidate data and MUST NOT treat it as the source of truth over raw messages, structured research state, evidence records, decisions, or artifacts.

#### Scenario: Extracted memory conflicts with research state
- **WHEN** an extracted memory conflicts with structured research state or a recorded decision
- **THEN** the system preserves the authoritative structured record and marks the extracted memory as conflicting or invalid

### Requirement: Memory extraction is event-driven and throttled
The system SHALL trigger memory extraction from meaningful events and MAY throttle extraction to control cost.

#### Scenario: Research run completes
- **WHEN** a research run completes with new decisions, artifacts, or important state updates
- **THEN** the system schedules memory extraction for candidate memory generation

#### Scenario: Extraction is throttled
- **WHEN** multiple memory-triggering events occur within the configured debounce window
- **THEN** the system batches or delays extraction instead of running an independent extraction for every event

### Requirement: Context builder retrieves layered memory
The system SHALL retrieve memory in a layered priority order: current thread state, per-research memory, global user memory, external knowledge-base memory, and candidate memory only for review or promotion workflows.

#### Scenario: Director builds research context
- **WHEN** the research director prepares context for a normal research turn
- **THEN** the system includes relevant current thread state, per-research memory, global user memory, and external knowledge-base notes, while excluding unpromoted candidate memory

### Requirement: External knowledge-base memory uses adapters
The system SHALL access external knowledge-base memory through a provider-neutral adapter interface.

#### Scenario: Obsidian MCP adapter reads notes
- **WHEN** the configured knowledge-base adapter is Obsidian-over-MCP and the context builder requests relevant notes
- **THEN** the adapter returns note content and metadata without exposing Obsidian-specific behavior to core memory logic

#### Scenario: External note content is untrusted
- **WHEN** external note content is loaded into context
- **THEN** the system treats the content as user or source data and not as system instructions

---

# 中文版（阅读参考）

## 新增需求

### 需求：会话记忆持久化运行时对话状态
系统应为每个研究线程持久化会话记忆，包括原始消息、运行事件、图 checkpoint、研究状态引用、产物元数据和证据链接。

#### 场景：中断后恢复会话
- **当** 一个研究 run 被中断，用户之后恢复同一个线程时
- **则** 系统应加载该线程持久化的消息、运行事件、checkpoint 数据和研究状态引用

#### 场景：运行事件可以回放
- **当** 用户打开之前的研究 run 时
- **则** 系统可以回放或检查已存储的运行事件，而不是依赖重新生成的助手回复

### 需求：会话记忆使用结构化本地持久化
系统应为 MVP 会话记忆使用结构化本地持久化层，并以 SQLite 作为 repository 接口背后的默认实现。

#### 场景：按线程查询记忆
- **当** Context Builder 请求某个研究线程的记忆时
- **则** repository 只返回该线程及相关研究标识范围内的记录

### 需求：内部长期记忆使用 Markdown 文件
系统应将内部长期记忆保存在 Markdown 文件中，并要求 frontmatter 标识 scope、type、version、status 和更新时间等元数据。

#### 场景：加载有效内部记忆文件
- **当** 运行时加载一个 frontmatter 有效且正文可读的内部记忆文件时
- **则** 系统应将其解析为对应 scope 的记忆上下文

#### 场景：无效内部记忆文件被拒绝或警告
- **当** 内部记忆文件缺少必要 frontmatter 字段时
- **则** 系统应拒绝将其用于运行时上下文，或记录校验警告

### 需求：全局用户记忆与单研究记忆分离
系统应将全局用户记忆与单研究记忆分开保存。

#### 场景：全局用户记忆跨研究线程生效
- **当** 用户开始或恢复任意研究线程时
- **则** `memory/global/user_memory.md` 中稳定的全局偏好可在相关时提供给 Context Builder

#### 场景：研究记忆保持单研究作用域
- **当** 用户处理另一个研究项目时
- **则** 其他 `memory/research/<research_id>/research_memory.md` 中的项目事实不会被纳入上下文，除非它们被显式链接或请求

### 需求：候选记忆需要提升流程
系统应先将 LLM 提炼出的记忆写入 candidate memory，再将其提升为持久的全局记忆或研究记忆。

#### 场景：LLM 提炼新的候选记忆
- **当** Memory Extractor 从一次 turn、run、决策、产物或状态更新中识别出可能的长期记忆时
- **则** 系统应将其记录为候选记忆，并带上来源、置信度和目标 scope

#### 场景：候选记忆被提升
- **当** 候选记忆被用户确认，或通过显式提升规则时
- **则** 系统应将其写入对应的全局或单研究记忆文件，并保留来源

#### 场景：候选记忆被拒绝
- **当** 候选记忆被拒绝时
- **则** 系统不应在普通运行时上下文检索中包含它

### 需求：记忆记录保留来源
系统应为持久记忆和候选记忆保留来源，包括可用时关联到源消息、决策、证据、产物或明确的用户确认。

#### 场景：检查记忆来源
- **当** 用户或系统检查一条记忆时
- **则** 系统可以展示其来源引用，或标记来源不可用

### 需求：LLM 记忆提炼是派生能力，不是权威事实源
系统必须将 LLM 提炼出的记忆视为派生候选数据，并且不得让它覆盖原始消息、结构化研究状态、证据记录、决策或产物。

#### 场景：提炼记忆与研究状态冲突
- **当** 一条提炼出的记忆与结构化研究状态或已记录决策冲突时
- **则** 系统应保留权威结构化记录，并将该提炼记忆标记为冲突或无效

### 需求：记忆提炼由事件触发并支持节流
系统应由有意义的事件触发记忆提炼，并可以通过节流控制成本。

#### 场景：研究 run 完成
- **当** 一个研究 run 完成，并产生新的决策、产物或重要状态更新时
- **则** 系统应调度记忆提炼，用于生成候选记忆

#### 场景：记忆提炼被节流
- **当** 多个记忆触发事件在配置的 debounce 窗口内发生时
- **则** 系统应批处理或延迟提炼，而不是为每个事件独立运行一次提炼

### 需求：Context Builder 分层检索记忆
系统应按分层优先级检索记忆：当前线程状态、单研究记忆、全局用户记忆、外部知识库记忆；候选记忆只在 review 或 promotion 流程中检索。

#### 场景：研究总控构建研究上下文
- **当** 研究总控为普通研究轮次准备上下文时
- **则** 系统应包含相关当前线程状态、单研究记忆、全局用户记忆和外部知识库笔记，并排除未提升的候选记忆

### 需求：外部知识库记忆使用 adapter
系统应通过 Provider 无关的 adapter 接口访问外部知识库记忆。

#### 场景：Obsidian MCP adapter 读取笔记
- **当** 配置的知识库 adapter 是 Obsidian-over-MCP，且 Context Builder 请求相关笔记时
- **则** adapter 应返回笔记内容和元数据，同时不向核心记忆逻辑暴露 Obsidian 特有行为

#### 场景：外部笔记内容是不可信内容
- **当** 外部笔记内容被加载到上下文时
- **则** 系统应将其视为用户或来源数据，而不是系统指令
