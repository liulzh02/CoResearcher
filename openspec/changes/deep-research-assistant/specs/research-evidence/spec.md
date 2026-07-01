## ADDED Requirements

### Requirement: Papers are normalized before use as evidence
The system SHALL normalize retrieved or uploaded papers into paper records with title, authors, venue or source, year when available, locator, and extraction status before using them as research evidence.

#### Scenario: Uploaded PDF processed
- **WHEN** a user uploads a paper PDF for analysis
- **THEN** the system creates a paper record before storing claims or evidence extracted from the paper

### Requirement: Claims link to evidence
The system MUST link every durable research claim to at least one evidence item, critique note, or explicit user-provided assumption.

#### Scenario: Claim from paper summary
- **WHEN** the paper reader extracts a claim from a paper
- **THEN** the persisted claim references the paper and supporting evidence item

### Requirement: Evidence includes source quality signals
The system SHALL store source quality signals for evidence when available, such as source type, recency, venue, citation context, extraction confidence, and whether the source is user-provided.

#### Scenario: Literature scout adds search result
- **WHEN** the literature scout adds a candidate paper from a search result
- **THEN** the system stores available metadata and source quality signals with the paper or evidence record

### Requirement: Evidence can be challenged
The system SHALL allow critique notes to challenge claims or evidence items without deleting the original evidence.

#### Scenario: Critic disputes a claim
- **WHEN** the critic subagent identifies that a claim is unsupported or overgeneralized
- **THEN** the system records a critique note linked to the challenged claim or evidence item

### Requirement: Research outputs cite evidence
The system MUST include citation or evidence references when generating research briefs, reading notes, evidence maps, or direction recommendations.

#### Scenario: Direction recommendation generated
- **WHEN** the system recommends a research direction
- **THEN** the recommendation includes references to supporting evidence and limitations or open questions

### Requirement: Unsupported claims are labeled
The system SHALL label claims as unsupported or assumption-based when they cannot be linked to a source or evidence item.

#### Scenario: User hypothesis added
- **WHEN** a user proposes a hypothesis without supporting sources
- **THEN** the system records it as a user-provided assumption until evidence is added

---

# 中文版（阅读参考）

## 新增需求

### 需求：论文在作为证据前需要规范化
系统应先将检索到或上传的论文规范化为论文记录，再将其作为研究证据使用。论文记录应包含标题、作者、会议或来源、可用年份、定位信息和提取状态。

#### 场景：处理上传的 PDF
- **当** 用户上传一篇论文 PDF 供系统分析时
- **则** 系统应先创建论文记录，再存储从该论文中提取的论断或证据

### 需求：论断需要关联证据
每一个持久化的研究论断必须关联至少一个证据项、质疑记录，或明确的用户提供假设。

#### 场景：来自论文总结的论断
- **当** 论文阅读 Subagent 从论文中提取出一个论断时
- **则** 被持久化的论断应引用该论文和支持它的证据项

### 需求：证据包含来源质量信号
系统应在可用时为证据存储来源质量信号，例如来源类型、时效性、发表场所、引用语境、提取置信度，以及该来源是否由用户提供。

#### 场景：文献发现 Subagent 添加搜索结果
- **当** 文献发现 Subagent 从搜索结果中添加候选论文时
- **则** 系统应将可用的元数据和来源质量信号存入论文或证据记录

### 需求：证据可以被质疑
系统应允许质疑记录挑战论断或证据项，同时不删除原始证据。

#### 场景：Critic 质疑一个论断
- **当** 批判性质疑 Subagent 发现某个论断缺乏支撑或过度泛化时
- **则** 系统应记录一条质疑记录，并将其关联到被挑战的论断或证据项

### 需求：研究输出需要引用证据
系统生成研究简报、阅读笔记、证据图谱或方向建议时，必须包含引用或证据引用关系。

#### 场景：生成方向建议
- **当** 系统推荐一个研究方向时
- **则** 该建议应包含支持证据，以及相关局限或开放问题

### 需求：未支撑论断需要标记
当论断无法关联到来源或证据项时，系统应将其标记为未支撑论断或基于假设的论断。

#### 场景：添加用户假设
- **当** 用户提出一个没有支持来源的假设时
- **则** 系统应将其记录为用户提供的假设，直到后续补充证据
