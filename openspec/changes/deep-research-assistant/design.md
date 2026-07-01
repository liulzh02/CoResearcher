## Context

CoResearcher is starting from an empty project and needs an architectural baseline for a scientific deep research assistant. The target product is a collaborative research partner that helps users explore, analyze, discuss, choose, dig deeper, challenge assumptions, and iterate on a research direction.

The local deer-flow project provides a useful reference shape: a Python backend, FastAPI gateway, LangGraph-compatible runtime, a lead agent factory, middleware composition, structured thread state, subagent registry, bounded subagent concurrency, streaming events, tools, skills, artifacts, and persistence. CoResearcher should borrow those architectural patterns but use research-domain state, role names, artifacts, and quality controls.

## Goals / Non-Goals

**Goals:**

- Establish a backend-first MVP architecture using Python, FastAPI, LangGraph, and registry-driven subagents.
- Model CoResearcher around a research director agent that orchestrates specialized subagents and remains responsible for user alignment and synthesis.
- Persist structured research state separately from raw chat messages so research direction, evidence, claims, critique, and decisions can survive across turns.
- Make evidence traceability a first-class behavior: claims must be linkable to papers, source metadata, or explicit user-provided assumptions.
- Stream long-running research progress and subagent status so users can observe the process rather than wait for a final report.
- Keep the first implementation small enough to review and test.

**Non-Goals:**

- Build a complete frontend experience in this change.
- Implement a one-click paper generation workflow.
- Commit to a specific scholarly search provider, vector database, or production deployment topology.
- Implement multi-user enterprise permissions beyond the minimal interfaces needed for thread isolation and future auth.
- Guarantee scientific correctness automatically; the system must expose evidence, uncertainty, and critique rather than pretend to be authoritative.

## Decisions

### Use a Research Director graph as the primary LangGraph entry point

The backend will expose a `make_research_director` graph factory. The research director owns conversation continuity, clarification, research planning, subagent delegation, state updates, and synthesis.

Alternative considered: a fixed workflow graph with hard-coded phases such as search, read, synthesize, and report. That would be easier to test initially, but it would not match the desired collaborative loop where the user and AI repeatedly reshape the research direction. A director agent with structured state gives more flexibility while still allowing tests around state transitions and tool calls.

### Use registry-driven subagents

Subagents will be declared through a registry/config layer with name, description, system prompt, tool allowlist, skill allowlist, model override, max turns, and timeout. Initial built-in roles:

- `literature-scout`: discovers candidate papers, datasets, venues, authors, and related work.
- `paper-reader`: extracts contributions, methods, evidence, assumptions, limitations, and citation-worthy notes from papers or uploaded documents.
- `methodologist`: reasons about research methods, experiment design, baselines, evaluation, and feasibility.
- `coding-researcher`: implements small experiments, reproduction attempts, data analysis, baseline checks, and code-based validation in a constrained execution environment.
- `evidence-curator`: normalizes evidence items, source metadata, claims, and citation links.
- `critic`: challenges assumptions, identifies threats to validity, missing baselines, weak evidence, and alternative explanations.
- `synthesizer`: creates concise research briefs, comparison notes, direction options, and next-step recommendations.

Alternative considered: expose only a generic subagent. Generic subagents are simpler but tend to blur responsibilities and produce weaker research traces. Domain-specific roles make delegation clearer and allow safer tool limits.

### Persist research state as a typed state object

The graph state will extend the message state with typed research fields:

- research question and scope
- hypotheses
- papers
- evidence items
- claims
- open questions
- decisions
- critique notes
- artifacts
- todos

Alternative considered: store all information in chat history and summaries. That reduces schema work, but it makes evidence traceability, artifact generation, and iterative state inspection much harder.

### Treat evidence and citations as structured data

Claims should not be stored as free text only. Each claim should carry source links, confidence/quality signals, and the reasoning context needed to inspect it later. Uploaded papers and retrieved sources should be normalized into paper/source records before being used as evidence.

Alternative considered: rely on inline Markdown citations in generated responses. Inline citations are useful for display, but they are insufficient as the durable source of truth for later critique and iteration.

### Stream progress through backend events

The API should expose run lifecycle events, subagent start/completion/failure events, research state update events, artifact events, and final answer events. Server-sent events are enough for the MVP and align with long-running research interactions.

Alternative considered: synchronous request/response only. This would simplify the first API but would make deep research feel opaque and brittle when subagents take time.

### Keep provider wiring pluggable

Model providers, scholarly search providers, PDF parsers, and embedding/vector stores should be behind interfaces/configuration. The MVP can ship with one simple implementation or stubs, but application code must not bake in secrets or one vendor.

Alternative considered: hard-code one provider to move quickly. That would increase early velocity but create avoidable rework and secret-handling risk.

## Detailed Architecture Modules

### LLM provider abstraction

CoResearcher will use a configuration-driven model factory similar to deer-flow. Runtime code asks for a named model or role-specific model, and the factory creates a LangChain-compatible chat model from configuration. Model configuration should record provider class, display metadata, tool-calling support, streaming support, vision support, long-context support, thinking/reasoning options, structured-output capability, and default runtime parameters.

The research director should default to a stronger reasoning model, while subagents may override the model based on task type. For example, `literature-scout` can prefer fast search-oriented models, `paper-reader` can prefer long-context models, `critic` and `methodologist` can prefer stronger reasoning models, and `coding-researcher` should prefer stable tool-calling behavior over raw generation quality.

### Tool and skill system

Tools should be grouped by research capability rather than exposed as one flat list. Initial groups should include search, paper ingestion, evidence management, knowledge-base access, coding sandbox execution, artifact generation, and user clarification. The runtime should assemble tools from configured tools, built-in research tools, MCP tools, knowledge-base adapters, coding sandbox tools, and the director-only subagent task tool.

Skills should remain distinct from tools. A skill provides task policy, domain procedure, output expectations, and tool restrictions; a tool performs an executable action. Subagents load only the skills and tools allowed by their configuration and by runtime security policy.

### Context management

CoResearcher should keep chat messages, structured research thread state, long-term research memory, and personal or domain knowledge base data as separate context layers. A context builder should select the smallest useful context for each run: recent conversation, active research question, relevant evidence, unresolved decisions, conflicting claims, and selected knowledge-base notes or graph entities.

The director may see a broader state summary, but each subagent should receive only task-relevant context. This prevents token growth, reduces accidental contamination between subtasks, and makes subagent outputs easier to audit.

### Multi-agent orchestration

The research director is the only component allowed to delegate to subagents in the MVP. Subagents must not recursively call other subagents. The subagent task tool should be exposed only to the director graph, and subagent runtimes should run with recursive delegation disabled by tool policy and runtime validation.

Subagent execution should be registry-driven, bounded by concurrency, timeout, max turns, token budget, and cancellation rules. Results from subagents should return to the director as structured observations. The director then decides whether to update research state, ask the user, launch another top-level delegation round, or synthesize an answer.

### Prompt design

Prompts should be layered instead of stored as one large role-play block. The shared research policy should define CoResearcher's identity, evidence rules, uncertainty rules, citation behavior, and user-alignment behavior. The director prompt should cover clarification, planning, delegation, synthesis, critique, state updates, and next-step selection. Each subagent prompt should define the role boundary, allowed output schema, evidence requirements, and restrictions on final conclusions.

`coding-researcher` needs an additional prompt contract: code outputs are experimental evidence or artifacts, not final scientific conclusions. It must report environment assumptions, inputs, commands or scripts, observed results, and limitations.

### Safety and permission management

Security should be enforced at several layers: user/thread isolation, tool allowlists, MCP server allowlists, environment-only secrets, sandboxed code execution, artifact path isolation, prompt-injection handling for untrusted sources, and audit logging. Tool permissions should be fail-closed: a subagent receives no tool unless both its configuration and runtime policy allow it.

For untrusted PDFs, web pages, and notes, source text must be treated as data rather than instructions. Coding execution must run in a constrained environment with explicit timeout, resource limits, network policy, file path boundaries, and artifact capture.

### Session persistence

Persistence should separate product state from runtime recovery state. Chat messages preserve conversation history; research state preserves durable scientific work; run events support streaming replay and debugging; LangGraph checkpoints support graph recovery; artifacts preserve generated research outputs; evidence and source records preserve traceability.

SQLite is a reasonable MVP storage backend if wrapped in repository interfaces. This keeps local development simple while preserving a migration path to PostgreSQL or a managed database later.

### LangGraph graph design

The MVP should expose `make_research_director` as the primary graph factory. The graph should contain explicit nodes for loading context, director reasoning, clarification, delegation planning, subagent execution, result merging, state update, critique, synthesis, and event emission. The first version can keep the graph flexible, but the node boundaries should be explicit enough to test and observe.

The graph should prevent recursive delegation by construction: only the director node can reach subagent execution, and subagent graphs should not include the subagent task tool. Later changes can introduce more specialized graphs for literature review, paper reading, or experiment planning, but they should still preserve director ownership of the user-facing research thread.

### Configuration system

Configuration should use typed Pydantic models loaded from YAML and environment variables. It should include sections for models, tools, MCP servers, subagents, persistence, sandbox, knowledge base, gateway, tracing, and security. Secrets must be referenced through environment variables, never stored in config files.

Runtime overrides may tune model choice, timeouts, and enabled tools, but they must not bypass safety defaults. For example, enabling a tool in a subagent config should still pass through the security policy and sandbox policy before the tool becomes available.

### Gateway design

The FastAPI gateway should be thin. It validates requests, resolves auth/session context, invokes application services, streams events, serializes responses, and maps errors. It should not contain research orchestration logic directly.

Initial routers should cover health, models, tools, research threads, structured research state, messages, research runs, SSE run events, artifacts, evidence, and knowledge-base access. SSE should be the MVP streaming protocol for run lifecycle events, subagent progress, state updates, evidence creation, artifact creation, final answers, and structured errors.

## Risks / Trade-offs

- Research state schema becomes too broad too early -> Start with minimal fields required by the specs and allow additive schema evolution.
- Subagents produce conflicting conclusions -> Preserve conflicts as critique/open questions instead of overwriting earlier state.
- Evidence traceability slows down generation -> Make traceability mandatory for research claims and optional for conversational scaffolding.
- Long-running subagents may consume too many tokens or time -> Add bounded concurrency, max turns, timeouts, and token budget middleware.
- Code-executing research tasks may become unsafe or non-reproducible -> Run `coding-researcher` with explicit sandbox boundaries, timeouts, resource limits, artifact paths, and evidence recording rules.
- Search provider availability may vary -> Define provider interfaces and test against fake providers before integrating live services.
- The director agent may over-delegate simple tasks -> Prompt and middleware should prefer direct execution unless there are at least two meaningful parallel subtasks.
- Users may mistake the output for verified scientific truth -> Responses and artifacts must expose uncertainty, source quality, limitations, and critique notes.

## Migration Plan

This is a new project baseline, so no data migration is required.

1. Scaffold the Python backend project and OpenSpec-aligned modules.
2. Implement the research state models and in-memory or file-backed persistence.
3. Implement the research director graph with fake or minimal model/tool wiring for tests.
4. Add subagent registry and built-in role configs.
5. Add streaming API endpoints and event contracts.
6. Add evidence and artifact APIs after the core graph can run.

Rollback strategy: because this is an initial change, rollback means reverting the created backend scaffold and OpenSpec artifacts before any production data exists.

## Open Questions

- Which model provider should be the default local development path?
- Should the first scholarly search connector target Semantic Scholar, arXiv, Crossref, local uploaded PDFs, or a provider-agnostic fake first?
- Should persistence start as SQLite, JSONL files, or an abstract repository with in-memory tests only?
- Which artifact format should be considered MVP: Markdown research brief, evidence table, reading note, or all three?

## Chinese Supplement: Coding Subagent

本次设计新增 `coding-researcher` 作为内置 Subagent。它负责代码相关的科研验证工作，例如论文方法的最小复现、小实验脚本、数据处理、baseline 检查、统计分析和可视化。

`coding-researcher` 与 `methodologist` 的边界不同：`methodologist` 偏实验设计和方法论判断，`coding-researcher` 偏动手执行和代码验证。它产生的实验结果必须被记录为 evidence item 或 artifact，不能直接升级为最终研究结论。

该 Subagent 默认应运行在受限执行环境中，具备明确的超时、资源限制、文件产物路径和工具权限，避免代码执行任务失控或污染研究状态。

---

# 中文版（阅读参考）

## 上下文

CoResearcher 当前从一个空项目开始，需要先建立面向科研深度研究助手的架构基线。目标产品不是简单的报告生成器，而是一个能帮助用户探索、分析、讨论、选择、深挖、质疑并迭代研究方向的科研搭子。

本地 deer-flow 项目提供了有价值的参考形态：Python 后端、FastAPI Gateway、LangGraph 兼容运行时、Lead Agent 工厂、中间件组合、结构化线程状态、Subagent 注册表、有界 Subagent 并发、流式事件、工具、技能、产物和持久化。CoResearcher 可以借鉴这些架构模式，但需要换成科研领域的状态、角色、产物和质量控制。

## 目标 / 非目标

**目标：**

- 建立以后端为先的 MVP 架构，技术栈使用 Python、FastAPI、LangGraph 和注册表驱动的 Subagent。
- 将 CoResearcher 建模为一个研究总控 Agent，由它编排专门的 Subagent，并负责用户对齐和综合输出。
- 将结构化研究状态与原始聊天消息分开持久化，使研究方向、证据、论断、质疑和决策能跨轮次保留。
- 将证据可追踪性作为一等行为：论断必须能关联到论文、来源元数据或明确的用户假设。
- 流式展示长时间研究进度和 Subagent 状态，让用户能看到研究过程，而不是只等待最终报告。
- 保持第一版足够小，便于评审和测试。

**非目标：**

- 本次变更不构建完整前端体验。
- 本次变更不实现一键生成论文工作流。
- 本次变更不绑定具体学术搜索 Provider、向量数据库或生产部署拓扑。
- 除线程隔离和未来认证所需的最小接口外，不实现多用户企业级权限。
- 不承诺自动保证科学正确性；系统应暴露证据、不确定性和质疑，而不是假装绝对权威。

## 设计决策

### 使用研究总控图作为主要 LangGraph 入口

后端将暴露 `make_research_director` 图工厂。研究总控负责对话连续性、澄清、研究计划、Subagent 分派、状态更新和综合。

备选方案是使用固定工作流图，例如硬编码为检索、阅读、综合和报告等阶段。这样初期更容易测试，但不符合用户和 AI 反复重塑研究方向的协作循环。带结构化状态的总控 Agent 更灵活，同时仍然可以围绕状态转换和工具调用编写测试。

### 使用注册表驱动的 Subagent

Subagent 将通过注册表/配置层声明，字段包括名称、描述、System Prompt、工具白名单、技能白名单、模型覆盖、最大轮次和超时。初始内置角色如下：

- `literature-scout`：发现候选论文、数据集、会议、作者和相关工作。
- `paper-reader`：从论文或上传文档中提取贡献、方法、证据、假设、局限和可引用笔记。
- `methodologist`：分析研究方法、实验设计、基线、评估和可行性。
- `evidence-curator`：规范化证据项、来源元数据、论断和引用链接。
- `critic`：挑战假设，识别有效性威胁、缺失基线、薄弱证据和替代解释。
- `synthesizer`：生成简洁研究简报、对比笔记、方向选项和下一步建议。

备选方案是只暴露一个通用 Subagent。通用 Subagent 更简单，但职责容易模糊，研究轨迹也更弱。领域角色能让分派更清晰，也便于限制工具权限。

### 将研究状态持久化为类型化状态对象

图状态将在消息状态之外扩展以下研究字段：

- 研究问题和研究范围
- 假设
- 论文
- 证据项
- 论断
- 开放问题
- 决策
- 质疑记录
- 产物
- 待办事项

备选方案是把所有信息都放在聊天历史和摘要中。这样 schema 工作更少，但会让证据追踪、产物生成和迭代式状态检查变得困难。

### 将证据和引用视为结构化数据

论断不应只以自由文本形式存储。每个论断应携带来源链接、置信度/质量信号，以及后续检查所需的推理上下文。上传论文和检索来源在作为证据使用之前，应先规范化为论文/来源记录。

备选方案是在生成回复中依赖 Markdown 内联引用。内联引用适合展示，但不足以作为后续质疑和迭代的持久事实来源。

### 通过后端事件流式展示进度

API 应暴露运行生命周期事件、Subagent 启动/完成/失败事件、研究状态更新事件、产物事件和最终回答事件。Server-Sent Events 对 MVP 足够，并且适合长时间研究交互。

备选方案是只使用同步请求/响应。这会简化第一版 API，但当 Subagent 执行耗时时，深度研究过程会变得不透明且脆弱。

### 保持 Provider 接入可插拔

模型 Provider、学术搜索 Provider、PDF 解析器和 Embedding/向量存储都应通过接口和配置接入。MVP 可以只提供一个简单实现或 stub，但应用代码不能硬编码密钥或绑定单一供应商。

备选方案是为了快速推进而硬编码一个 Provider。这样短期速度更快，但会带来重复改造和密钥处理风险。

## 详细模块设计

### LLM Provider 抽象

CoResearcher 应采用类似 deer-flow 的配置驱动模型工厂。运行时代码只请求命名模型或角色模型，由工厂根据配置创建兼容 LangChain 的 Chat Model。模型配置需要记录 Provider 类、展示信息、工具调用能力、流式能力、视觉能力、长上下文能力、thinking/reasoning 选项、结构化输出能力和默认运行参数。

研究总控默认使用推理能力更强的模型。Subagent 可以按任务类型覆盖模型：`literature-scout` 偏向快速检索模型，`paper-reader` 偏向长上下文模型，`critic` 和 `methodologist` 偏向强推理模型，`coding-researcher` 则优先考虑稳定的工具调用能力。

### 工具与技能系统

工具应按科研能力分组，而不是作为一个扁平列表暴露。初始工具组包括 search、paper、evidence、knowledge-base、coding sandbox、artifact 和 user clarification。运行时从配置工具、内置科研工具、MCP 工具、知识库 adapter、代码沙箱工具和仅供总控使用的 Subagent task tool 中组装可用工具。

技能应与工具分离。Skill 描述任务策略、领域流程、输出要求和工具限制；Tool 负责实际执行动作。Subagent 只能加载其配置和运行时安全策略共同允许的技能与工具。

### 上下文管理

CoResearcher 应将聊天消息、结构化研究线程状态、长期研究记忆、个人或领域知识库分为不同上下文层。Context Builder 每次只选择最有用的上下文：最近对话、当前研究问题、相关证据、未决决策、冲突论断，以及知识库中相关的笔记或图谱实体。

研究总控可以看到更宽的状态摘要，但每个 Subagent 只接收与任务相关的上下文。这样可以控制 token 增长，减少子任务之间的污染，也让 Subagent 输出更容易审计。

### 多智能体编排

MVP 阶段只有研究总控可以分派 Subagent。Subagent 禁止递归调用其他 Subagent。Subagent task tool 只能暴露给研究总控图；Subagent 运行时需要通过工具策略和运行时校验关闭递归分派能力。

Subagent 执行由注册表驱动，并受并发数、超时、最大轮次、token 预算和取消规则约束。Subagent 结果以结构化观察返回给研究总控，再由研究总控决定是否更新研究状态、询问用户、启动下一轮顶层分派，或综合输出答案。

### 提示词设计

Prompt 应分层组织，而不是写成一个巨大的角色扮演文本。共享研究策略定义 CoResearcher 的身份、证据规则、不确定性规则、引用行为和用户对齐方式。研究总控 Prompt 覆盖澄清、规划、分派、综合、质疑、状态更新和下一步选择。每个 Subagent Prompt 定义角色边界、输出 schema、证据要求和最终结论限制。

`coding-researcher` 需要额外约束：代码输出只能作为实验性证据或产物，不能直接成为最终科学结论。它必须报告环境假设、输入、命令或脚本、观察结果和限制。

### 安全与权限管理

安全应在多层执行：用户和线程隔离、工具白名单、MCP server 白名单、密钥仅来自环境变量、代码沙箱、产物路径隔离、非可信来源的 prompt injection 防护，以及审计日志。工具权限默认 fail-closed：只有 Subagent 配置和运行时策略都允许时，工具才会被暴露。

对于不可信 PDF、网页和笔记，来源文本必须被视为数据，而不是指令。代码执行必须运行在受限环境中，并有明确的超时、资源限制、网络策略、文件路径边界和产物捕获机制。

### 会话持久化

持久化需要区分产品状态和运行时恢复状态。聊天消息保存对话历史；研究状态保存可持续迭代的科研工作；运行事件用于流式回放和调试；LangGraph checkpoint 用于图恢复；产物保存生成的研究输出；证据和来源记录保存可追溯性。

SQLite 适合作为 MVP 存储后端，但应包在 repository 接口之后。这样本地开发足够简单，也保留未来迁移到 PostgreSQL 或托管数据库的路径。

### LangGraph 图设计

MVP 应暴露 `make_research_director` 作为主要图工厂。图中应包含清晰节点：加载上下文、总控推理、澄清、分派规划、Subagent 执行、结果合并、状态更新、质疑、综合和事件发送。第一版可以保持图的灵活性，但节点边界需要足够清楚，便于测试和观测。

图结构应从设计上阻止递归分派：只有 director 节点可以到达 Subagent 执行节点，Subagent 图中不包含 Subagent task tool。后续可以增加文献综述、论文阅读或实验规划等专用图，但仍应由研究总控掌握用户可见研究线程。

### 配置系统

配置系统应使用 Pydantic 类型模型，从 YAML 和环境变量加载。配置分区包括 models、tools、MCP servers、subagents、persistence、sandbox、knowledge base、gateway、tracing 和 security。密钥只能通过环境变量引用，不能写入配置文件。

运行时 override 可以调整模型选择、超时和启用工具，但不能绕过安全默认值。例如，在 Subagent 配置中启用某个工具后，仍必须经过安全策略和沙箱策略过滤，才能真正暴露给模型。

### 网关设计

FastAPI Gateway 应保持轻量。它负责请求校验、解析 auth/session 上下文、调用应用服务、流式发送事件、序列化响应和映射错误，不直接承载研究编排逻辑。

初始 router 应覆盖 health、models、tools、research threads、structured research state、messages、research runs、SSE run events、artifacts、evidence 和 knowledge-base access。MVP 使用 SSE 作为流式协议，覆盖 run 生命周期、Subagent 进度、状态更新、证据创建、产物创建、最终答案和结构化错误。

## 风险 / 权衡

- 研究状态 schema 过早膨胀 -> 先保留 specs 必需的最小字段，并允许后续增量演进。
- Subagent 输出相互冲突 -> 将冲突保留为质疑记录或开放问题，而不是覆盖旧状态。
- 证据可追踪性降低生成速度 -> 对研究论断强制要求可追踪，对一般对话铺垫可放宽。
- 长时间运行的 Subagent 消耗过多 token 或时间 -> 增加有界并发、最大轮次、超时和 token 预算中间件。
- 搜索 Provider 可用性不稳定 -> 先定义 Provider 接口，并用 fake provider 测试，再接入真实服务。
- 研究总控可能过度分派简单任务 -> Prompt 和中间件应要求只有存在至少 2 个有意义的并行子任务时才使用 Subagent。
- 用户可能误以为输出就是已验证的科学真理 -> 回复和产物必须暴露不确定性、来源质量、局限和质疑记录。

## 迁移计划

这是一个新项目基线，因此不需要数据迁移。

1. 搭建 Python 后端项目和符合 OpenSpec 的模块结构。
2. 实现研究状态模型，以及内存或文件持久化。
3. 使用 fake 或最小模型/工具接线实现研究总控图，便于测试。
4. 增加 Subagent 注册表和内置角色配置。
5. 增加流式 API 端点和事件契约。
6. 在核心图可以运行后，再增加证据和产物 API。

回滚策略：由于这是初始变更，回滚就是在没有生产数据之前撤销创建的后端脚手架和 OpenSpec 产物。

## 开放问题

- 本地开发默认使用哪个模型 Provider？
- 第一版学术搜索连接器应优先接 Semantic Scholar、arXiv、Crossref、本地上传 PDF，还是先做 Provider 无关的 fake？
- 持久化应从 SQLite、JSONL 文件开始，还是先只定义抽象 repository 并使用内存测试？
- MVP 产物格式应选择 Markdown 研究简报、证据表、阅读笔记，还是三者都做？
