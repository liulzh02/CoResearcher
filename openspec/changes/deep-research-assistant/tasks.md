## 1. Project Scaffold

- [x] 1.1 Create the Python backend project structure with package metadata, lint/test configuration, and a minimal application entry point.
- [x] 1.2 Add initial dependencies for FastAPI, Pydantic, LangGraph/LangChain runtime, async server execution, and tests.
- [x] 1.3 Add environment/config loading that reads secrets only from environment variables and never commits provider credentials.
- [x] 1.4 Add a minimal health endpoint and smoke test proving the backend starts.

## 2. Research State

- [x] 2.1 Define typed models for research threads, research questions, scope, hypotheses, papers, evidence items, claims, open questions, decisions, critique notes, artifacts, and todos.
- [x] 2.2 Implement a repository interface for loading and saving research thread state.
- [x] 2.3 Provide an MVP repository implementation suitable for local development and tests.
- [x] 2.4 Validate state updates so durable claims require evidence, critique, or explicit user-assumption references.
- [x] 2.5 Add tests for state persistence, invalid update rejection, decision recording, and artifact-to-state linking.

## 3. Research Director And Subagents

- [x] 3.1 Implement the `make_research_director` LangGraph factory and register it in the backend graph configuration.
- [x] 3.2 Define the research director prompt and runtime behavior for clarification, planning, delegation, synthesis, critique, and next-step selection.
- [x] 3.3 Implement a registry-driven subagent configuration model with name, description, prompt, tool allowlist, model override, max turns, and timeout.
- [x] 3.4 Add built-in subagent configs for `literature-scout`, `paper-reader`, `methodologist`, `coding-researcher`, `evidence-curator`, `critic`, and `synthesizer`.
- [x] 3.5 Implement bounded subagent task dispatch with configurable concurrency and recursive subagent delegation disabled by design.
- [x] 3.6 Add tests for ambiguous-goal clarification, subagent selection, coding-researcher delegation, concurrency limiting, nested delegation prevention, and conflicting-result synthesis.

## 4. Evidence And Artifacts

- [x] 4.1 Implement paper normalization for uploaded or retrieved sources with title, authors, source locator, year, and extraction status fields.
- [x] 4.2 Implement evidence item and claim creation helpers that preserve source links and quality signals.
- [x] 4.3 Implement critique notes that can challenge claims or evidence without deleting the original records.
- [x] 4.4 Implement MVP artifact generation for Markdown research briefs, reading notes, and evidence maps.
- [x] 4.5 Add tests that generated artifacts cite their source claims/evidence and label unsupported assumptions.

## 5. Streaming API

- [x] 5.1 Implement APIs to create, retrieve, update, and list research threads and structured research state.
- [x] 5.2 Implement a research run endpoint that invokes the research director graph.
- [x] 5.3 Implement server-sent event streaming for run lifecycle, progress, subagent activity, research state updates, artifacts, final responses, and structured errors.
- [x] 5.4 Implement artifact retrieval endpoints scoped to research thread identifiers.
- [x] 5.5 Add API tests for thread creation, state retrieval, progress events, subagent completion events, artifact retrieval, and non-secret-bearing provider errors.

## 6. Integration And Verification

- [x] 6.1 Add fake model, fake search, and fake paper extraction fixtures for deterministic integration tests.
- [x] 6.2 Add an end-to-end test covering a broad research goal, clarification, parallel subagent execution, evidence persistence, critique, synthesis, and streaming output.
- [x] 6.3 Add documentation for local setup, environment variables, running tests, and the initial backend API surface.
- [x] 6.4 Run the fastest relevant checks and record the verification commands in the implementation summary.

## 7. LLM Provider And Configuration

- [x] 7.1 Define typed model configuration for provider class, display metadata, streaming support, tool-calling support, vision support, long-context support, thinking/reasoning options, structured-output support, and default parameters.
- [x] 7.2 Implement a model factory that creates named LangChain-compatible chat models from configuration without hard-coding provider credentials.
- [x] 7.3 Add role-based model selection for the research director and each built-in subagent, including model inheritance and per-agent overrides.
- [x] 7.4 Add tests for missing model names, invalid provider classes, role-based model resolution, non-secret error reporting, and thinking/streaming option handling.

## 8. Tool Permissions And Skill Loading

- [x] 8.1 Define research tool groups for search, paper ingestion, evidence management, knowledge-base access, coding sandbox execution, artifact generation, and user clarification.
- [x] 8.2 Implement tool assembly from configured tools, built-in research tools, MCP tools, knowledge-base tools, coding sandbox tools, and director-only subagent task tools.
- [x] 8.3 Implement fail-closed tool filtering that combines global security policy, subagent allowlists, subagent denylists, skill-level tool restrictions, and runtime context.
- [x] 8.4 Ensure the subagent task tool is available only to the research director graph and never to subagent runtimes.
- [x] 8.5 Add tests for duplicate tool names, tool group filtering, MCP tool filtering, skill-restricted tools, and recursive subagent tool denial.

## 9. Knowledge Base Adapter

- [x] 9.1 Define a provider-neutral knowledge-base adapter interface for listing notes, reading notes, writing notes, querying entities, upserting entities, upserting relations, and linking notes to research state.
- [x] 9.2 Implement an MVP Obsidian-over-MCP adapter behind the generic knowledge-base interface.
- [x] 9.3 Add research state links from papers, claims, evidence items, decisions, and artifacts to knowledge-base note IDs or graph entity IDs.
- [x] 9.4 Add tests with a fake knowledge-base adapter for note reads/writes, graph upserts, source linking, adapter failures, and permission filtering.

## 10. Safety Sandbox And Runtime Permissions

- [x] 10.1 Define a runtime security context carrying user ID, thread ID, run ID, role, allowed tools, allowed MCP servers, sandbox ID, and artifact root.
- [x] 10.2 Implement sandbox policy for `coding-researcher` with timeout, resource limits, network policy, file path boundaries, and artifact capture.
- [x] 10.3 Treat retrieved papers, web pages, PDFs, and knowledge-base notes as untrusted source text that cannot override system or developer instructions.
- [x] 10.4 Add audit records for tool calls, sandbox executions, MCP calls, rejected permissions, subagent starts, subagent completions, and subagent failures.
- [x] 10.5 Add tests for path isolation, timeout handling, denied network access, denied host filesystem access, prompt-injection text handling, and audit logging.

## 11. LangGraph Node Design

- [x] 11.1 Define explicit graph nodes for context loading, director reasoning, clarification, delegation planning, subagent execution, result merging, research state update, critique, synthesis, and event emission.
- [x] 11.2 Implement graph edges that allow only the director node to enter subagent execution and prevent subagent graphs from reaching delegation tools.
- [x] 11.3 Define node-level event emission for run lifecycle, director progress, subagent progress, state updates, evidence creation, artifact creation, final responses, and structured errors.
- [x] 11.4 Add tests for graph routing, clarification path, direct-answer path, delegation path, state-update path, recursive delegation prevention, and event ordering.

## 12. Gateway And API Boundaries

- [x] 12.1 Define FastAPI routers for health, models, tools, research threads, structured research state, messages, research runs, SSE run events, artifacts, evidence, and knowledge-base access.
- [x] 12.2 Keep the gateway thin by moving orchestration, persistence, evidence handling, and knowledge-base behavior into application services.
- [x] 12.3 Add request/response schemas for run creation, event streaming, artifact retrieval, evidence retrieval, knowledge-base linking, and structured errors.
- [x] 12.4 Add API tests for route validation, user/thread scoping, SSE event serialization, structured error mapping, and gateway behavior without leaking secrets.

## Chinese Supplement: Coding Subagent Tasks

- Task 3.4 also includes the built-in `coding-researcher` subagent config.
- Task 3.6 also includes delegation tests for `coding-researcher`, especially for code experiments, reproduction attempts, data analysis, and baseline checks.
- `coding-researcher` outputs should be verified as evidence or artifacts, not treated as final conclusions by default.
- Task 3.5 treats recursive subagent delegation as forbidden by design, not merely disabled by default.

---

# 中文版（阅读参考）

说明：下面是任务清单的中文阅读版。为了不影响 OpenSpec 对任务复选框的解析，这里使用普通列表，不使用 `- [ ]` 格式。

## 1. 项目脚手架

- 1.1 创建 Python 后端项目结构，包括包元数据、lint/test 配置和最小应用入口。
- 1.2 添加 FastAPI、Pydantic、LangGraph/LangChain 运行时、异步服务执行和测试所需的初始依赖。
- 1.3 增加环境和配置加载逻辑，只从环境变量读取密钥，禁止提交 Provider 凭据。
- 1.4 增加最小健康检查接口和 smoke test，证明后端可以启动。

## 2. 研究状态

- 2.1 定义研究线程、研究问题、研究范围、假设、论文、证据项、论断、开放问题、决策、质疑记录、产物和待办事项的类型模型。
- 2.2 实现用于加载和保存研究线程状态的 repository 接口。
- 2.3 提供适合本地开发和测试的 MVP repository 实现。
- 2.4 校验状态更新，确保可持久化的论断必须关联证据、质疑记录或明确的用户假设。
- 2.5 为状态持久化、无效更新拒绝、决策记录和产物到状态的关联添加测试。

## 3. 研究总控与 Subagent

- 3.1 实现 `make_research_director` LangGraph 工厂，并在后端图配置中注册。
- 3.2 定义研究总控 Prompt 和运行时行为，包括澄清、规划、分派、综合、质疑和下一步选择。
- 3.3 实现注册表驱动的 Subagent 配置模型，包含名称、描述、Prompt、工具白名单、模型覆盖、最大轮次和超时。
- 3.4 增加内置 Subagent 配置：`literature-scout`、`paper-reader`、`methodologist`、`evidence-curator`、`critic` 和 `synthesizer`。
- 3.5 实现有界 Subagent 任务分派，支持可配置并发，并从设计上禁止递归分派。
- 3.6 为模糊目标澄清、Subagent 选择、并发限制、嵌套分派阻止和冲突结果综合添加测试。

## 4. 证据与产物

- 4.1 实现上传或检索来源的论文规范化，包含标题、作者、来源定位、年份和提取状态字段。
- 4.2 实现证据项和论断创建辅助逻辑，保留来源链接和质量信号。
- 4.3 实现质疑记录，使其可以挑战论断或证据，同时不删除原始记录。
- 4.4 实现 MVP 产物生成，包括 Markdown 研究简报、阅读笔记和证据图谱。
- 4.5 添加测试，确保生成产物引用其来源论断/证据，并标记未支撑假设。

## 5. 流式 API

- 5.1 实现用于创建、获取、更新和列出研究线程及结构化研究状态的 API。
- 5.2 实现研究运行接口，用于调用研究总控图。
- 5.3 实现 Server-Sent Events 流式输出，覆盖运行生命周期、进度、Subagent 活动、研究状态更新、产物、最终响应和结构化错误。
- 5.4 实现按研究线程标识限定范围的产物获取接口。
- 5.5 添加 API 测试，覆盖线程创建、状态获取、进度事件、Subagent 完成事件、产物获取和不泄露敏感信息的 Provider 错误。

## 6. 集成与验证

- 6.1 添加 fake model、fake search 和 fake paper extraction fixtures，用于确定性的集成测试。
- 6.2 添加端到端测试，覆盖宽泛研究目标、澄清、并行 Subagent 执行、证据持久化、质疑、综合和流式输出。
- 6.3 添加本地设置、环境变量、测试运行方式和初始后端 API 的文档。
- 6.4 运行最快相关检查，并在实现总结中记录验证命令。

## 7. LLM Provider 与配置

- 7.1 定义模型配置类型，覆盖 Provider 类、展示信息、流式能力、工具调用能力、视觉能力、长上下文能力、thinking/reasoning 选项、结构化输出能力和默认参数。
- 7.2 实现模型工厂，根据配置创建命名的 LangChain 兼容 Chat Model，不在代码中硬编码 Provider 凭据。
- 7.3 为研究总控和每个内置 Subagent 增加基于角色的模型选择，支持模型继承和单个 Agent 覆盖。
- 7.4 添加测试，覆盖缺失模型名、无效 Provider 类、角色模型解析、错误信息不泄露密钥，以及 thinking/streaming 选项处理。

## 8. 工具权限与 Skill 加载

- 8.1 定义科研工具组，包括 search、paper ingestion、evidence management、knowledge-base access、coding sandbox execution、artifact generation 和 user clarification。
- 8.2 实现工具组装逻辑，来源包括配置工具、内置科研工具、MCP 工具、知识库工具、代码沙箱工具和仅供研究总控使用的 Subagent task tool。
- 8.3 实现 fail-closed 工具过滤，同时考虑全局安全策略、Subagent 白名单、Subagent 黑名单、Skill 级工具限制和运行时上下文。
- 8.4 确保 Subagent task tool 只暴露给研究总控图，绝不暴露给 Subagent 运行时。
- 8.5 添加测试，覆盖重复工具名、工具组过滤、MCP 工具过滤、Skill 限制工具，以及递归 Subagent 工具拒绝。

## 9. 知识库 Adapter

- 9.1 定义 Provider 无关的知识库 adapter 接口，支持列出笔记、读取笔记、写入笔记、查询实体、写入实体、写入关系，以及将笔记链接到研究状态。
- 9.2 在通用知识库接口后实现 MVP 版 Obsidian-over-MCP adapter。
- 9.3 为论文、论断、证据项、决策和产物增加到知识库 note ID 或 graph entity ID 的链接。
- 9.4 使用 fake knowledge-base adapter 添加测试，覆盖笔记读写、图谱写入、来源链接、adapter 失败和权限过滤。

## 10. 安全沙箱与运行时权限

- 10.1 定义运行时安全上下文，携带 user ID、thread ID、run ID、role、allowed tools、allowed MCP servers、sandbox ID 和 artifact root。
- 10.2 为 `coding-researcher` 实现沙箱策略，包含超时、资源限制、网络策略、文件路径边界和产物捕获。
- 10.3 将检索到的论文、网页、PDF 和知识库笔记视为不可信来源文本，不能覆盖 system 或 developer 指令。
- 10.4 为工具调用、沙箱执行、MCP 调用、权限拒绝、Subagent 启动、完成和失败添加审计记录。
- 10.5 添加测试，覆盖路径隔离、超时处理、网络拒绝、宿主文件系统拒绝、prompt injection 文本处理和审计日志。

## 11. LangGraph 节点设计

- 11.1 定义明确图节点：上下文加载、总控推理、澄清、分派规划、Subagent 执行、结果合并、研究状态更新、质疑、综合和事件发送。
- 11.2 实现图边约束，只有 director 节点可以进入 Subagent 执行，并阻止 Subagent 图访问分派工具。
- 11.3 定义节点级事件发送，覆盖 run 生命周期、总控进度、Subagent 进度、状态更新、证据创建、产物创建、最终响应和结构化错误。
- 11.4 添加测试，覆盖图路由、澄清路径、直接回答路径、分派路径、状态更新路径、递归分派阻止和事件顺序。

## 12. Gateway 与 API 边界

- 12.1 定义 FastAPI router，覆盖 health、models、tools、research threads、structured research state、messages、research runs、SSE run events、artifacts、evidence 和 knowledge-base access。
- 12.2 保持 Gateway 轻量，将编排、持久化、证据处理和知识库行为放入应用服务。
- 12.3 添加 run 创建、事件流、产物获取、证据获取、知识库链接和结构化错误的请求/响应 schema。
- 12.4 添加 API 测试，覆盖路由校验、用户/线程范围、SSE 事件序列化、结构化错误映射，以及不泄露密钥的 Gateway 行为。
