## ADDED Requirements

### Requirement: Research threads persist structured state
The system SHALL persist structured research state for each research thread, including research question, scope, hypotheses, papers, evidence items, claims, open questions, decisions, critique notes, artifacts, and todos.

#### Scenario: State survives follow-up turns
- **WHEN** a user asks a follow-up question after an earlier research turn
- **THEN** the system loads the prior structured research state and applies the follow-up to that state

### Requirement: Research state is separate from chat messages
The system MUST store research-domain objects separately from raw conversation messages.

#### Scenario: Evidence retrieved from state
- **WHEN** the director needs to inspect prior evidence
- **THEN** the system retrieves structured evidence items instead of relying only on previous assistant prose

### Requirement: Research state updates are typed
The system SHALL validate research state updates against typed schemas before persistence.

#### Scenario: Invalid evidence update
- **WHEN** a component attempts to persist an evidence item without a source reference or user-provided assumption marker
- **THEN** the system rejects or marks the update invalid before it becomes part of durable research state

### Requirement: Decisions are recorded explicitly
The system SHALL record user-approved or director-proposed research decisions with timestamp, rationale, and related evidence or critique references when available.

#### Scenario: User chooses a direction
- **WHEN** a user selects one proposed research direction from several options
- **THEN** the system records the selected direction as a decision and links it to the options and rationale

### Requirement: Open questions remain visible
The system SHALL retain unresolved research questions and uncertainties until they are answered, closed, or explicitly deprioritized.

#### Scenario: Critic identifies a weakness
- **WHEN** the critic subagent identifies a missing baseline or validity threat
- **THEN** the system records it as an open question or critique note for later discussion

### Requirement: Artifacts link back to state
The system SHALL associate generated artifacts with the research thread and the state objects they summarize or depend on.

#### Scenario: Research brief generated
- **WHEN** the system generates a Markdown research brief
- **THEN** the artifact record references the claims, evidence items, decisions, or critique notes used to produce it

---

# 中文版（阅读参考）

## 新增需求

### 需求：研究线程持久化结构化状态
系统应为每个研究线程持久化结构化研究状态，包括研究问题、研究范围、假设、论文、证据项、论断、开放问题、决策、质疑记录、产物和待办事项。

#### 场景：状态在追问中保留
- **当** 用户在早先的研究轮次之后提出追问时
- **则** 系统应加载之前的结构化研究状态，并基于该状态处理追问

### 需求：研究状态与聊天消息分离
系统必须将研究领域对象与原始对话消息分开存储。

#### 场景：从状态中取回证据
- **当** 研究总控需要检查既有证据时
- **则** 系统应读取结构化证据项，而不是只依赖历史助手回复中的自然语言描述

### 需求：研究状态更新需要类型校验
系统应在持久化之前，使用类型化 schema 校验研究状态更新。

#### 场景：无效证据更新
- **当** 某个组件尝试持久化一个没有来源引用、也没有标记为用户假设的证据项时
- **则** 系统应在该更新进入持久化研究状态之前拒绝它，或将其标记为无效

### 需求：显式记录决策
系统应记录用户确认或总控提出的研究决策，并包含时间戳、理由，以及可用时关联的证据或质疑记录。

#### 场景：用户选择一个方向
- **当** 用户从多个候选研究方向中选择一个时
- **则** 系统应将所选方向记录为决策，并关联对应选项和理由

### 需求：开放问题保持可见
系统应保留尚未解决的研究问题和不确定性，直到它们被回答、关闭或明确降级优先级。

#### 场景：Critic 识别出薄弱点
- **当** 批判性质疑 Subagent 识别出缺少基线或存在有效性威胁时
- **则** 系统应将其记录为开放问题或质疑记录，供后续讨论

### 需求：产物回链到研究状态
系统应将生成的产物与研究线程及其所总结或依赖的状态对象关联起来。

#### 场景：生成研究简报
- **当** 系统生成 Markdown 研究简报时
- **则** 产物记录应引用用于生成该简报的论断、证据项、决策或质疑记录
