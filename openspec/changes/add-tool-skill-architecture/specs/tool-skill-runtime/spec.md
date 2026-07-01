## ADDED Requirements

### Requirement: Tool runtime separates tools from domain commands
The system MUST distinguish LLM-callable tools from backend domain commands. Durable research-state, evidence, claim, decision, and memory mutations MUST be applied through backend validation rather than ordinary LLM tools.

#### Scenario: Director proposes evidence update
- **WHEN** the research director proposes a new evidence item
- **THEN** the system validates and applies it through a domain command instead of exposing a direct `create_evidence_item` tool to the model

#### Scenario: Tool list excludes domain mutations
- **WHEN** tools are assembled for an agent
- **THEN** state, evidence, claim, decision, and memory mutation commands are not included as ordinary LLM-callable tools

### Requirement: Tool registry aggregates configured and built-in tools
The system SHALL provide a tool registry that aggregates configured tools, built-in tools, MCP tools, external-agent tools, and optional director-only subagent delegation tools.

#### Scenario: Registry assembles available tools
- **WHEN** an agent runtime requests available tools
- **THEN** the registry combines enabled tool sources and returns a deduplicated policy-filtered tool list

### Requirement: Tool registry detects duplicate tool names
The system SHALL detect duplicate tool names during tool assembly and SHALL keep only one deterministic winner while warning about the conflict.

#### Scenario: Duplicate MCP and configured tool names
- **WHEN** an MCP tool and a configured tool expose the same name
- **THEN** the registry keeps the configured-priority tool and records a warning about the skipped duplicate

### Requirement: Local tools are sandbox-scoped executable actions
The system SHALL expose local LLM tools as sandbox-scoped executable actions, including file inspection, file mutation, command execution, artifact file access, document inspection, presentation helpers, and optional image viewing.

#### Scenario: Agent reads a sandbox file
- **WHEN** an agent calls `read_file` with an allowed virtual path
- **THEN** the tool reads the file through the sandbox and masks host filesystem details in the output

#### Scenario: Agent writes a sandbox file
- **WHEN** an agent calls `write_file` or `str_replace`
- **THEN** the tool writes only within allowed sandbox or artifact paths and rejects forbidden host paths

### Requirement: Host bash is disabled unless explicitly allowed
The system MUST NOT expose host bash by default. Bash or Python execution tools SHALL be available only when sandbox and runtime policy explicitly allow them.

#### Scenario: Host bash denied by default
- **WHEN** a subagent requests tools and host bash is not allowed
- **THEN** the assembled tool list excludes host bash or equivalent unrestricted execution tools

### Requirement: External search and retrieval providers are config-driven tools
The system SHALL load external search and retrieval providers as optional configured tools rather than hard-coded director behavior.

#### Scenario: Search provider disabled
- **WHEN** a provider such as Tavily, Brave, Serper, Exa, Firecrawl, Browserless, DDG, Jina AI, arXiv, Semantic Scholar, or Crossref is not enabled in config
- **THEN** its tool is not exposed to agents

#### Scenario: Search provider enabled
- **WHEN** a provider is enabled and required secrets are available through environment variables
- **THEN** the registry may expose the provider's tool according to policy

### Requirement: MCP tools are cached, tagged, and filtered
The system SHALL initialize MCP tools through the MCP layer, cache them for runtime use, tag them as MCP-sourced tools, and filter them per agent after policy assembly.

#### Scenario: MCP tools filtered per subagent
- **WHEN** MCP tools are available but a subagent policy does not allow them
- **THEN** those MCP tools are not bound to that subagent

### Requirement: Subagent delegation tool is director-only
The system SHALL expose the subagent delegation tool only to the Research Director graph and MUST NOT expose it to subagent runtimes.

#### Scenario: Subagent runtime requests tools
- **WHEN** a subagent runtime assembles tools
- **THEN** the subagent delegation tool is excluded even if subagent execution is enabled globally

### Requirement: Skills are procedural policies, not backend functions
The system SHALL treat Skills as task procedures, output constraints, and tool permission metadata. Skills MUST NOT be treated as arbitrary executable backend functions.

#### Scenario: Skill guides paper reading
- **WHEN** the `paper-reading` Skill is loaded
- **THEN** the runtime injects its procedure and output constraints and applies its tool permissions without exposing backend state mutation functions

### Requirement: Built-in Skills are stored in the project
The system SHALL store built-in Skills in the project-controlled Skill directory with `SKILL.md` and structured metadata.

#### Scenario: Built-in Skill loads successfully
- **WHEN** the runtime loads a built-in Skill such as `paper-reading`
- **THEN** it reads the Skill content and metadata from the project Skill storage path

### Requirement: User and generated Skills are stored separately
The system SHALL reserve separate storage locations for future user Skills, generated candidate Skills, enabled generated Skills, and Skill history.

#### Scenario: Generated Skill remains disabled before review
- **WHEN** a generated Skill exists only in the candidate Skill storage location
- **THEN** the runtime does not load it as an enabled Skill for any agent

### Requirement: Skill metadata constrains tools
The system SHALL allow Skill metadata to declare allowed tool names and allowed tool groups. When active Skills declare explicit tool permissions, agent tool lists SHALL be filtered accordingly.

#### Scenario: Skill restricts tools
- **WHEN** a subagent loads a Skill that allows only file and PDF tools
- **THEN** search, bash, memory-write, state-write, and subagent-delegation tools are excluded unless separately allowed by all policy layers

### Requirement: Tool policy is fail-closed
The system SHALL compute effective tool availability through fail-closed filtering across global policy, configured groups, subagent allowlists, subagent denylists, Skill policy, runtime context, model capability, and sandbox policy.

#### Scenario: One policy layer denies a tool
- **WHEN** a tool is allowed by a Skill but denied by sandbox policy
- **THEN** the tool is not exposed to the agent

#### Scenario: Vision tool requires vision-capable model
- **WHEN** the selected model does not support vision
- **THEN** image-viewing tools are not bound to that agent

### Requirement: Tool outputs are treated as data
The system MUST treat external search, MCP, browser, document, and file outputs as data rather than system instructions.

#### Scenario: Search result contains instruction-like text
- **WHEN** a search or fetch tool returns text that appears to instruct the model to ignore prior instructions
- **THEN** the runtime and prompts treat that text as untrusted source content

---

# 中文版（阅读参考）

## 新增需求

### 需求：工具运行时区分 Tool 和 Domain Command
系统必须区分 LLM 可调用工具和后端 Domain Command。持久研究状态、证据、论断、决策和记忆变更必须通过后端校验执行，而不是作为普通 LLM Tool 暴露。

#### 场景：研究总控提出证据更新
- **当** 研究总控提出新的证据项时
- **则** 系统应通过 Domain Command 校验并应用，而不是向模型暴露直接的 `create_evidence_item` 工具

#### 场景：工具列表排除领域变更
- **当** 系统为 Agent 组装工具时
- **则** 状态、证据、论断、决策和记忆变更命令不会作为普通 LLM 可调用工具出现

### 需求：工具注册表聚合配置和内置工具
系统应提供工具注册表，聚合配置工具、内置工具、MCP 工具、外部 Agent 工具，以及可选的仅供总控使用的 Subagent 分派工具。

#### 场景：注册表组装可用工具
- **当** Agent runtime 请求可用工具时
- **则** 注册表应合并已启用的工具来源，并返回去重且经过策略过滤的工具列表

### 需求：工具注册表检测重复工具名
系统应在工具组装时检测重复工具名，并以确定性优先级保留一个工具，同时记录冲突告警。

#### 场景：MCP 工具和配置工具重名
- **当** 一个 MCP 工具和一个配置工具暴露相同名称时
- **则** 注册表应保留配置优先的工具，并记录被跳过的重复工具告警

### 需求：本地工具是沙箱范围内的可执行动作
系统应将本地 LLM Tool 暴露为沙箱范围内的可执行动作，包括文件检查、文件修改、命令执行、产物文件访问、文档检查、展示辅助和可选图片查看。

#### 场景：Agent 读取沙箱文件
- **当** Agent 使用允许的虚拟路径调用 `read_file` 时
- **则** 工具应通过沙箱读取文件，并在输出中隐藏宿主文件系统细节

#### 场景：Agent 写入沙箱文件
- **当** Agent 调用 `write_file` 或 `str_replace` 时
- **则** 工具只能写入允许的沙箱或 artifact 路径，并拒绝被禁止的宿主路径

### 需求：默认禁用 host bash
系统默认不得暴露 host bash。只有沙箱策略和运行时策略显式允许时，bash 或 Python 执行工具才可用。

#### 场景：默认拒绝 host bash
- **当** Subagent 请求工具且 host bash 未被允许时
- **则** 组装出的工具列表应排除 host bash 或等价的不受限执行工具

### 需求：外部搜索和检索 Provider 是配置驱动工具
系统应将外部搜索和检索 Provider 作为可选配置工具加载，而不是硬编码在 Director 行为中。

#### 场景：搜索 Provider 未启用
- **当** Tavily、Brave、Serper、Exa、Firecrawl、Browserless、DDG、Jina AI、arXiv、Semantic Scholar 或 Crossref 等 Provider 未在配置中启用时
- **则** 对应工具不会暴露给 Agent

#### 场景：搜索 Provider 已启用
- **当** 某个 Provider 已启用，且所需密钥通过环境变量提供时
- **则** 注册表可以根据策略暴露该 Provider 的工具

### 需求：MCP 工具需要缓存、标记和过滤
系统应通过 MCP 层初始化 MCP 工具，将其缓存给运行时使用，标记为 MCP 来源工具，并在每个 Agent 的策略组装后过滤。

#### 场景：按 Subagent 过滤 MCP 工具
- **当** MCP 工具可用但某个 Subagent 策略不允许使用它们时
- **则** 这些 MCP 工具不会绑定到该 Subagent

### 需求：Subagent 分派工具仅供研究总控使用
系统应只向 Research Director 图暴露 Subagent 分派工具，并且不得向 Subagent 运行时暴露该工具。

#### 场景：Subagent runtime 请求工具
- **当** Subagent runtime 组装工具时
- **则** 即使全局启用了 Subagent 执行，Subagent 分派工具也会被排除

### 需求：Skill 是流程策略，不是后端函数
系统应将 Skill 视为任务流程、输出约束和工具权限元数据。Skill 不能被当作任意可执行后端函数。

#### 场景：Skill 指导论文阅读
- **当** `paper-reading` Skill 被加载时
- **则** runtime 注入它的流程和输出约束，并应用其工具权限，但不暴露后端状态变更函数

### 需求：内置 Skill 存储在项目中
系统应将内置 Skill 存储在项目控制的 Skill 目录中，并包含 `SKILL.md` 和结构化元数据。

#### 场景：成功加载内置 Skill
- **当** runtime 加载 `paper-reading` 等内置 Skill 时
- **则** 它应从项目 Skill 存储路径读取 Skill 内容和元数据

### 需求：用户 Skill 和生成 Skill 分开存储
系统应为未来用户 Skill、生成候选 Skill、已启用生成 Skill 和 Skill 历史保留独立存储位置。

#### 场景：生成 Skill 在 review 前保持禁用
- **当** 一个生成 Skill 只存在于候选 Skill 存储位置时
- **则** runtime 不会将其作为已启用 Skill 加载给任何 Agent

### 需求：Skill 元数据约束工具
系统应允许 Skill 元数据声明允许的工具名和工具组。当 active Skill 声明显式工具权限时，Agent 工具列表必须按这些权限过滤。

#### 场景：Skill 限制工具
- **当** Subagent 加载了只允许文件和 PDF 工具的 Skill 时
- **则** search、bash、memory-write、state-write 和 subagent-delegation 工具都会被排除，除非所有策略层都单独允许

### 需求：工具策略 fail-closed
系统应通过全局策略、配置分组、Subagent 白名单、Subagent 黑名单、Skill 策略、运行时上下文、模型能力和沙箱策略执行 fail-closed 工具过滤。

#### 场景：任一策略层拒绝工具
- **当** 某工具被 Skill 允许，但被沙箱策略拒绝时
- **则** 该工具不会暴露给 Agent

#### 场景：视觉工具需要视觉模型
- **当** 选中的模型不支持视觉能力时
- **则** 图片查看工具不会绑定给该 Agent

### 需求：工具输出视为数据
系统必须将外部搜索、MCP、浏览器、文档和文件输出视为数据，而不是系统指令。

#### 场景：搜索结果包含指令式文本
- **当** 搜索或抓取工具返回类似“忽略之前指令”的文本时
- **则** runtime 和 prompt 应将其视为不可信来源内容
