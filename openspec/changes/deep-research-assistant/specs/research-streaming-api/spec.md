## ADDED Requirements

### Requirement: Backend exposes research thread APIs
The system SHALL expose backend APIs to create, retrieve, update, and list research threads and their structured research state.

#### Scenario: Create research thread
- **WHEN** a client creates a new research thread with an initial user message
- **THEN** the backend returns a thread identifier and initializes empty or inferred research state

### Requirement: Backend streams research run events
The system SHALL stream long-running research run events to clients using a server-supported streaming mechanism.

#### Scenario: Run emits progress
- **WHEN** a research run is executing
- **THEN** the client receives progress events before the final answer is complete

### Requirement: Streaming events include subagent activity
The system SHALL emit events when subagents start, complete, fail, time out, or return notable intermediate results.

#### Scenario: Subagent completes
- **WHEN** a paper reader subagent finishes analyzing a paper
- **THEN** the stream includes a completion event with subagent type, task description, status, and result summary or artifact reference

### Requirement: Streaming events include research state changes
The system SHALL emit events when the research run adds or updates major research state objects such as papers, evidence items, claims, decisions, critique notes, todos, or artifacts.

#### Scenario: Evidence item added
- **WHEN** an evidence curator adds a new evidence item to the research state
- **THEN** the stream includes a state update event identifying the object type and identifier

### Requirement: API exposes research artifacts
The system SHALL expose generated research artifacts through stable backend artifact endpoints.

#### Scenario: Artifact retrieved
- **WHEN** a client requests a generated research brief by artifact identifier
- **THEN** the backend returns the artifact content or a clear not-found response scoped to the research thread

### Requirement: API errors are explicit and non-secret-bearing
The system MUST return explicit, structured errors without leaking secrets, provider keys, private environment values, or raw internal prompts.

#### Scenario: Provider failure
- **WHEN** a model or search provider fails during a research run
- **THEN** the backend returns or streams a structured error that identifies the failing subsystem without exposing credentials or private configuration

---

# 中文版（阅读参考）

## 新增需求

### 需求：后端提供研究线程 API
系统应提供后端 API，用于创建、获取、更新和列出研究线程及其结构化研究状态。

#### 场景：创建研究线程
- **当** 客户端用一条初始用户消息创建新的研究线程时
- **则** 后端应返回线程标识，并初始化空的或推断出的研究状态

### 需求：后端流式输出研究运行事件
系统应使用服务端支持的流式机制，将长时间运行的研究过程事件推送给客户端。

#### 场景：运行过程产生进度
- **当** 一个研究运行正在执行时
- **则** 客户端应在最终答案完成之前收到进度事件

### 需求：流式事件包含 Subagent 活动
系统应在 Subagent 启动、完成、失败、超时或返回重要中间结果时发出事件。

#### 场景：Subagent 完成
- **当** 论文阅读 Subagent 完成一篇论文分析时
- **则** 流中应包含完成事件，事件里包括 Subagent 类型、任务描述、状态，以及结果摘要或产物引用

### 需求：流式事件包含研究状态变更
当研究运行新增或更新论文、证据项、论断、决策、质疑记录、待办事项或产物等主要研究状态对象时，系统应发出事件。

#### 场景：新增证据项
- **当** 证据整理 Subagent 向研究状态添加新的证据项时
- **则** 流中应包含状态更新事件，并标识对象类型和对象 ID

### 需求：API 暴露研究产物
系统应通过稳定的后端产物端点暴露生成的研究产物。

#### 场景：获取产物
- **当** 客户端通过产物标识请求已生成的研究简报时
- **则** 后端应返回产物内容，或返回一个限定在该研究线程范围内的明确未找到响应

### 需求：API 错误明确且不泄露敏感信息
系统必须返回明确的结构化错误，并且不得泄露密钥、Provider Key、私有环境变量或原始内部 Prompt。

#### 场景：Provider 失败
- **当** 模型或搜索 Provider 在研究运行期间失败时
- **则** 后端应返回或流式输出结构化错误，说明失败的子系统，但不得暴露凭据或私有配置
