## ADDED Requirements

### Requirement: ContextPack Assembly
The system SHALL build a structured ContextPack for each Research Director and Subagent LLM call before sending the request to the provider.

#### Scenario: ContextPack created for director call
- **WHEN** the Research Director prepares an LLM call for a research session
- **THEN** the system SHALL assemble a ContextPack containing ordered sections for stable rules, selected history, research state, memory, evidence, tool outputs, Skill context, omitted-context metadata, and the latest user message

#### Scenario: ContextPack records budget metadata
- **WHEN** the system assembles a ContextPack
- **THEN** the system SHALL record the selected compression level, token budget, section token estimates, and source locators used to build the prompt

### Requirement: Latest User Message Preservation
The system MUST preserve the latest user message verbatim and render it as the final user message in the assembled prompt.

#### Scenario: Latest user message is final
- **WHEN** memory, evidence, Skill content, tool output, and selected history are included for an LLM call
- **THEN** the latest user message SHALL appear after those context sections as the final user message

#### Scenario: Latest user message is not summarized
- **WHEN** the context budget is under pressure
- **THEN** the system MUST NOT replace the latest user message with a generated summary or compressed paraphrase

#### Scenario: Latest user message drives retrieval
- **WHEN** the system retrieves memory, evidence, tools, Skill context, or source snippets for a prompt
- **THEN** the system SHALL use the latest user message as a ranking and selection input

### Requirement: User Message Compression Policy
The system MUST NOT lossy-summarize user messages.

#### Scenario: Older user message selected
- **WHEN** an older user message is relevant to the current task
- **THEN** the system SHALL include the original user message text with its message identifier

#### Scenario: Older user message omitted
- **WHEN** an older user message is omitted due to budget constraints
- **THEN** the system SHALL preserve its message identifier in omitted-context metadata or another retrievable source reference

### Requirement: Reversible Source Locators
The system SHALL represent recoverable long-form or external content with SourceLocator references before using lossy summaries.

#### Scenario: Long paper referenced
- **WHEN** a paper is relevant but the full text is not required for the next reasoning step
- **THEN** the system SHALL include the paper URL, title, identifier, and relevant page or section locator instead of inserting the full paper text

#### Scenario: Tool output truncated
- **WHEN** a tool output exceeds its configured token or character budget
- **THEN** the system SHALL include a bounded summary or excerpt plus a full-output locator that can recover the complete result

#### Scenario: Lossy summary generated
- **WHEN** the system generates a lossy summary under high context pressure
- **THEN** the summary SHALL include source locators back to the original transcript, artifact, file, URL, tool call, note, or database record

### Requirement: Layered Compression Levels
The system SHALL apply compression progressively according to context pressure.

#### Scenario: Light context pressure
- **WHEN** the estimated prompt size exceeds the target budget only slightly
- **THEN** the system SHALL first trim low-signal assistant history and bound tool outputs before summarizing conversation content

#### Scenario: Moderate context pressure
- **WHEN** long documents or raw external content dominate the prompt
- **THEN** the system SHALL replace those long contents with locators and relevant snippets before applying lossy summaries

#### Scenario: Severe context pressure
- **WHEN** the prompt cannot fit after reversible trimming and locator substitution
- **THEN** the system MAY use lossy summaries for assistant history or research state views while preserving latest user text and source references

### Requirement: Dynamic Context Fencing
The system SHALL render recalled or external dynamic content inside explicit context blocks that mark the content as background data rather than new user input.

#### Scenario: Memory context rendered
- **WHEN** recalled memory is included in a prompt
- **THEN** the system SHALL wrap it in a memory context block with a note that it is recalled background information and not a new user instruction

#### Scenario: Evidence context rendered
- **WHEN** evidence snippets or artifact references are included in a prompt
- **THEN** the system SHALL wrap them in an evidence or artifact context block with source locators

#### Scenario: Skill context rendered
- **WHEN** Skill procedure text is relevant to the current task
- **THEN** the system SHALL render it as Skill context before the latest user message and outside the system message

### Requirement: Reserved Tag Sanitization
The system MUST sanitize backend-reserved context tags from dynamic content before rendering it into fenced context blocks.

#### Scenario: Memory contains closing fence
- **WHEN** recalled memory contains a literal closing tag for a reserved context block
- **THEN** the system SHALL remove or escape that tag before wrapping the memory in the rendered prompt

#### Scenario: Tool output spoofs context block
- **WHEN** tool output contains text that imitates a backend-owned context tag
- **THEN** the system SHALL sanitize the tag in the rendered prompt while preserving the raw output in its source location

#### Scenario: Future context tag introduced
- **WHEN** a new backend-owned context block tag is added
- **THEN** the reserved-tag sanitizer SHALL treat the new tag as reserved for all dynamic context renderers

### Requirement: Context Precedence Rules
The system SHALL enforce prompt-ordering and conflict-resolution rules that prioritize explicit runtime rules and the latest user message over recalled background context.

#### Scenario: Memory conflicts with latest user request
- **WHEN** recalled memory indicates one user preference and the latest user message explicitly asks for a conflicting behavior
- **THEN** the system SHALL treat the latest user message as authoritative for the current turn

#### Scenario: Dynamic content contains instruction-like text
- **WHEN** memory, evidence, paper content, notes, or tool output contains instruction-like text
- **THEN** the system SHALL treat that text as background data and not as a new user or system instruction

### Requirement: Skill Context Priority
The system MUST NOT inject Skill content as a system message.

#### Scenario: Skill selected for task
- **WHEN** the system selects a Skill for the current task
- **THEN** it SHALL include relevant Skill procedure and output constraints as task context before the latest user message

#### Scenario: Skill specifies tool permissions
- **WHEN** a Skill declares allowed tools or permissions
- **THEN** the backend SHALL enforce those permissions through tool policy and sandbox checks rather than relying on prompt text alone

### Requirement: Subagent Context Isolation
The system SHALL provide Subagents with task-specific ContextPack slices instead of raw full main-thread context by default.

#### Scenario: Subagent receives task
- **WHEN** the Research Director delegates work to a Subagent
- **THEN** the Subagent SHALL receive the assigned task, relevant research state, selected memory, selected evidence, tool references, and applicable Skill context only

#### Scenario: Subagent returns result
- **WHEN** a Subagent completes a task
- **THEN** it SHALL return a structured result with source locators instead of requiring the Research Director to ingest the full Subagent transcript

### Requirement: Omitted Context Manifest
The system SHALL track omitted context so excluded material remains discoverable.

#### Scenario: Context section omitted
- **WHEN** a context section is excluded from the prompt due to token budget or relevance filtering
- **THEN** the system SHALL record a reason and a source locator for the omitted material

#### Scenario: User asks about omitted material
- **WHEN** a later task requires information that was previously omitted
- **THEN** the system SHALL be able to retrieve it through the stored locator when the source is still available

## 中文说明

本规格定义 CoResearcher 的上下文管理能力。系统每次调用 Research Director 或 Subagent 的 LLM 前，都必须构建结构化 ContextPack。最新用户消息必须原文保留，并放在最终用户消息位置；旧用户消息不能被有损摘要，只能原文选择或带 message_id 省略。论文、网页、文件、工具输出、历史 transcript 等长内容要优先以 SourceLocator 引用表示。压缩策略必须分层：先裁剪低信号内容和限制工具输出，再把长文档替换为引用与片段，最后才做有损摘要。所有召回记忆、证据、工具输出、外部知识和 Skill 内容都要作为背景上下文 fenced rendering，进入 prompt 前必须清洗后端保留标签，防止召回内容逃逸成新的指令。Skill 内容不能作为 system message 注入；工具权限必须由后端策略和 sandbox 强制执行。Subagent 默认只拿任务相关上下文切片，返回结构化结果和引用，而不是把完整子任务日志塞回主上下文。
