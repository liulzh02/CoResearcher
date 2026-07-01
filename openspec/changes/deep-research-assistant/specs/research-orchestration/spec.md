## ADDED Requirements

### Requirement: Research director owns the research loop
The system SHALL provide a research director agent that manages the iterative research loop across clarification, planning, subagent delegation, synthesis, critique, user discussion, and next-step selection.

#### Scenario: Director starts a new research thread
- **WHEN** a user starts a research thread with a broad research goal
- **THEN** the system creates or updates the research question, scope, open questions, and an initial research plan before producing a final research answer

#### Scenario: Director continues an existing research thread
- **WHEN** a user asks a follow-up question in an existing research thread
- **THEN** the system uses the persisted research state and prior decisions to continue the same research direction

### Requirement: Director clarifies ambiguous research goals
The system MUST ask for clarification before launching research work when the research goal is missing the domain, target question, expected output, or critical constraints needed to proceed safely.

#### Scenario: Missing research domain
- **WHEN** a user asks the system to "find a good research direction" without a field or topic
- **THEN** the system asks for the missing domain or topic instead of launching subagents

### Requirement: Director delegates to specialized subagents
The system SHALL support specialized subagents for literature discovery, paper reading, methodology analysis, evidence curation, skeptical critique, and synthesis.

#### Scenario: Parallel decomposition
- **WHEN** a research task contains multiple independent subtasks such as searching literature, analyzing methods, and identifying limitations
- **THEN** the director delegates those subtasks to appropriate specialized subagents and later synthesizes their results

### Requirement: Director delegates code-based research validation
The system SHALL support a specialized coding research subagent for code-based experiment, reproduction, data analysis, baseline checking, and validation tasks.

#### Scenario: Code reproduction task
- **WHEN** a research task requires implementing a small experiment, reproducing a method, running a baseline check, or analyzing data with code
- **THEN** the director delegates the work to the coding research subagent and records the result as evidence or an artifact rather than treating it as an unqualified conclusion

### Requirement: Subagent concurrency is bounded
The system MUST enforce a configurable maximum number of concurrent subagent tasks per director response.

#### Scenario: Too many subtasks
- **WHEN** the director identifies more subtasks than the configured subagent concurrency limit
- **THEN** the system runs the subtasks in batches and does not launch more than the configured limit in one response

### Requirement: Subagents cannot recursively delegate
The system MUST prevent subagents from invoking other subagents unless explicitly enabled by configuration.

#### Scenario: Subagent attempts nested delegation
- **WHEN** a subagent receives or constructs a task that would require another subagent
- **THEN** the system executes the task with the subagent's allowed tools or returns the limitation to the director without nested delegation

### Requirement: Director synthesizes conflicting findings
The system SHALL preserve and explain conflicting findings from different subagents rather than silently choosing one result.

#### Scenario: Conflicting evidence
- **WHEN** two subagents return incompatible interpretations of a paper or research direction
- **THEN** the director records the conflict as an open question or critique note and presents the uncertainty to the user

## 中文补充（阅读参考）

### 需求：总控分派代码级科研验证任务
系统应支持一个专门的代码研究 Subagent，用于处理代码实验、论文方法复现、数据分析、baseline 检查和代码级验证任务。

#### 场景：代码复现任务
- **当** 研究任务需要实现小实验、复现方法、运行 baseline 检查，或用代码分析数据时
- **则** 研究总控应将任务分派给代码研究 Subagent，并将结果记录为证据或产物，而不是直接视为无条件结论

---

# 中文版（阅读参考）

## 新增需求

### 需求：研究总控负责完整研究循环
系统应提供一个研究总控 Agent，负责管理澄清、规划、Subagent 分派、综合、质疑、用户讨论和下一步选择等迭代研究流程。

#### 场景：总控开启新的研究线程
- **当** 用户用一个宽泛的研究目标开启研究线程时
- **则** 系统应先创建或更新研究问题、研究范围、开放问题和初始研究计划，而不是直接给出最终研究答案

#### 场景：总控继续已有研究线程
- **当** 用户在已有研究线程中提出追问时
- **则** 系统应使用已持久化的研究状态和历史决策，沿着同一研究方向继续推进

### 需求：总控澄清模糊研究目标
当研究目标缺少研究领域、目标问题、期望输出或关键约束，导致无法安全推进时，系统必须先向用户澄清，再启动研究工作。

#### 场景：缺少研究领域
- **当** 用户只说「帮我找一个好的研究方向」，但没有提供领域或主题时
- **则** 系统应询问缺失的领域或主题，而不是直接启动 Subagent

### 需求：总控分派给专门的 Subagent
系统应支持面向文献发现、论文阅读、方法分析、证据整理、批判性质疑和综合写作的专门 Subagent。

#### 场景：并行拆解
- **当** 一个研究任务包含多个相互独立的子任务，例如检索文献、分析方法和识别局限时
- **则** 总控应将这些子任务分派给合适的专门 Subagent，并在结果返回后进行综合

### 需求：限制 Subagent 并发数量
系统必须强制执行可配置的 Subagent 并发上限，限制每次总控响应中可同时启动的 Subagent 任务数量。

#### 场景：子任务过多
- **当** 总控识别出的子任务数量超过配置的 Subagent 并发上限时
- **则** 系统应分批执行这些子任务，并且单次响应中启动的任务数不得超过配置上限

### 需求：Subagent 默认不能递归分派
除非配置显式启用，否则系统必须阻止 Subagent 再调用其他 Subagent。

#### 场景：Subagent 尝试嵌套分派
- **当** Subagent 收到或构造出一个需要另一个 Subagent 的任务时
- **则** 系统应使用该 Subagent 已允许的工具执行任务，或把能力限制返回给总控，不进行嵌套分派

### 需求：总控综合冲突发现
系统应保留并解释不同 Subagent 返回的冲突发现，而不是静默选择其中一个结果。

#### 场景：证据冲突
- **当** 两个 Subagent 对同一篇论文或同一个研究方向给出不兼容的解释时
- **则** 总控应将冲突记录为开放问题或质疑记录，并向用户呈现这种不确定性
