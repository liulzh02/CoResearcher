## Why

CoResearcher needs a clear boundary between LLM-callable tools, backend domain commands, and skills before implementation starts. Without this boundary, research-state updates, evidence writes, and memory writes could be incorrectly exposed as ordinary tools, making the system harder to secure and audit.

## What Changes

- Define LLM tools as executable external actions such as sandbox file operations, shell execution, document reading, web/search API calls, MCP tools, user interaction helpers, and director-only subagent delegation.
- Define domain commands as backend-validated state mutations such as creating claims, writing evidence, recording decisions, promoting memory, or updating research state; these are not exposed as ordinary LLM tools.
- Define skills as task procedures, output constraints, and tool permission policies rather than executable backend functions.
- Add a deer-flow-inspired tool registry that aggregates configured tools, built-in tools, MCP tools, ACP/external-agent tools, and optional director-only subagent tools.
- Add fail-closed tool filtering across global policy, tool groups, subagent allowlists/denylists, skill allowed tools, runtime context, and sandbox policy.
- Define local tool families for sandbox file operations, sandbox command execution, artifact file access, PDF/document inspection, user presentation, and optional image viewing.
- Define Skill storage locations for built-in skills and future user/generated skills, with versioned metadata and allowed-tool declarations.

## Capabilities

### New Capabilities

- `tool-skill-runtime`: Covers LLM tool registration, local tool categories, external search/API tools, MCP tool loading, Skill storage, Skill-to-tool policy, subagent tool filtering, and the boundary between tools and backend domain commands.

### Modified Capabilities

None. This change introduces a dedicated tool and Skill runtime capability that complements the existing deep research assistant architecture.

## Impact

- Affected backend areas: tool registry, sandbox tools, MCP integration, Skill storage, Skill parser/validator, subagent runtime, tool policy, runtime context, and configuration.
- Affected agent behavior: Research Director and subagents receive only policy-filtered tools; state/evidence/memory mutations flow through backend domain commands rather than direct tool calls.
- Expected dependencies: LangChain tool interfaces, sandbox provider, MCP client/cache, YAML/frontmatter parsing for Skill metadata, and optional community search providers.
- Security and quality considerations: high-risk tools such as bash, file writes, network fetch, code execution, and subagent delegation must be explicitly allowed; duplicate tool names must be detected; untrusted MCP/API outputs must be treated as data, not instructions.

---

# 中文版（阅读参考）

## 背景与动机

CoResearcher 在实现前需要明确区分 LLM 可调用工具、后端 Domain Command 和 Skill。否则，研究状态更新、证据写入和记忆写入可能被错误地暴露成普通工具，导致系统难以保护和审计。

## 变更内容

- 将 LLM Tool 定义为可执行的外部动作，例如沙箱文件操作、Shell 执行、文档读取、Web/Search API 调用、MCP 工具、用户交互辅助工具，以及仅供研究总控使用的 Subagent 分派工具。
- 将 Domain Command 定义为后端校验后的状态变更，例如创建论断、写入证据、记录决策、提升记忆或更新研究状态；这些能力不作为普通 LLM Tool 暴露。
- 将 Skill 定义为任务流程、输出约束和工具权限策略，而不是可执行后端函数。
- 增加参考 deer-flow 的工具注册表，聚合配置工具、内置工具、MCP 工具、ACP/外部 Agent 工具，以及可选的仅供总控使用的 Subagent 工具。
- 增加 fail-closed 工具过滤，综合全局策略、工具组、Subagent 白名单/黑名单、Skill 允许工具、运行时上下文和沙箱策略。
- 定义本地工具族：沙箱文件操作、沙箱命令执行、产物文件访问、PDF/文档检查、用户展示和可选图片查看。
- 定义 Skill 存储位置，用于内置 Skill 和未来的用户/生成 Skill，并支持版本化元数据和 allowed-tools 声明。

## 能力范围

### 新增能力

- `tool-skill-runtime`：覆盖 LLM Tool 注册、本地工具分类、外部搜索/API 工具、MCP 工具加载、Skill 存储、Skill-to-tool 策略、Subagent 工具过滤，以及工具和后端 Domain Command 的边界。

### 修改能力

无。本变更新增独立的工具与 Skill 运行时能力，用来补充现有 deep research assistant 架构。

## 影响范围

- 影响后端区域：工具注册表、沙箱工具、MCP 集成、Skill 存储、Skill 解析/校验、Subagent 运行时、工具策略、运行时上下文和配置系统。
- 影响 Agent 行为：Research Director 和 Subagent 只能获得策略过滤后的工具；状态、证据和记忆变更通过后端 Domain Command 执行，而不是直接工具调用。
- 预期依赖：LangChain tool 接口、sandbox provider、MCP client/cache、用于 Skill 元数据的 YAML/frontmatter 解析，以及可选 community search provider。
- 安全与质量要求：bash、文件写入、网络抓取、代码执行和 Subagent 分派等高风险工具必须显式允许；必须检测重复工具名；不可信 MCP/API 输出必须被视为数据，而不是指令。
