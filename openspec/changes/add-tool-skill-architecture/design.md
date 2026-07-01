## Context

CoResearcher needs a tool and Skill runtime that is close to deer-flow's actual shape while preserving research-domain safety. Deer-flow exposes LLM-callable tools for sandbox file access, shell execution, search/API providers, MCP tools, presentation helpers, and subagent delegation. It does not treat every backend function as a tool.

The important correction for CoResearcher is to separate three layers:

- **LLM Tool:** an executable action the model can call, such as `bash`, `ls`, `glob`, `grep`, `read_file`, `write_file`, `str_replace`, search providers, MCP tools, or director-only subagent delegation.
- **Domain Command:** a backend-validated mutation such as creating evidence, recording decisions, updating research state, or promoting memory.
- **Skill:** task procedure, output contract, and tool permission policy, not an executable backend function.

## Goals / Non-Goals

**Goals:**

- Define the boundary between tools, domain commands, and Skills.
- Provide a deer-flow-inspired tool registry that aggregates configured tools, built-in tools, MCP tools, external-agent tools, and optional director-only subagent tools.
- Define CoResearcher local tool families around sandbox file operations, sandbox command execution, artifact files, PDF/document inspection, user presentation, and optional image viewing.
- Support external search/API tools such as DDG, Jina AI, Serper, Brave, Tavily, Firecrawl, Browserless, Exa, arXiv, Semantic Scholar, and Crossref through config-driven providers.
- Define Skill storage for built-in, user, and generated Skills.
- Enforce fail-closed tool filtering across global policy, tool groups, subagent policy, Skill policy, runtime context, and sandbox policy.
- Keep state/evidence/memory writes out of ordinary LLM tool calls.

**Non-Goals:**

- This change does not implement every community search provider in the MVP.
- This change does not expose arbitrary backend repository functions as LLM tools.
- This change does not allow subagents to call subagents recursively.
- This change does not enable user-generated Skills by default in the MVP.
- This change does not bypass sandbox boundaries for local files or bash.

## Decisions

### Use a three-layer model: Tool, Domain Command, Skill

Tools are model-callable actions. Domain commands are backend-validated state mutations. Skills are procedural knowledge and permission constraints.

This means research state updates, evidence writes, claim creation, decision recording, and memory promotion are not ordinary LLM tools. The model can propose structured updates, but backend services validate and apply them.

Alternative considered: expose domain mutations as tools such as `create_evidence_item` or `record_decision`. This is simpler to wire, but it gives the model direct mutation power over durable research facts and makes validation harder to centralize.

### Mirror deer-flow's tool aggregation shape

The tool registry should aggregate tools from:

- configured tools declared in application config
- built-in tools such as clarification, presentation, and optional image viewing
- sandbox/local tools such as `bash`, `ls`, `glob`, `grep`, `read_file`, `write_file`, and `str_replace`
- cached MCP tools initialized at application startup
- optional external-agent tools
- director-only subagent delegation tools

The registry should deduplicate by actual tool name and warn on config/tool name mismatch.

Alternative considered: manually bind a fixed tool list per agent. This is easy for the first test but does not scale to MCP, optional providers, model capability checks, or subagent-specific policy.

### Treat local tools as sandbox tools

CoResearcher local tools should be executable surfaces, not business services. The initial local tool families are:

- file inspection: `ls`, `glob`, `grep`, `read_file`
- file mutation: `write_file`, `str_replace`
- command execution: `bash` or `run_python` in a sandbox
- artifact file access: list/read/write files under controlled artifact roots
- document inspection: PDF text extraction and PDF page/image extraction
- presentation helpers: present file/artifact to user
- optional image viewing when the selected model supports vision

Host filesystem access and host bash must be disabled unless explicitly allowed by config and sandbox policy.

Alternative considered: implement research-specific database actions as tools. Those actions should remain domain commands.

### Configure external search/API providers as tools

Search and retrieval providers should be loaded as optional configured tools. CoResearcher can support DDG, Jina AI, Serper, Brave, Tavily, Firecrawl, Browserless, Exa, arXiv, Semantic Scholar, and Crossref through provider modules and config.

MVP should include only a small deterministic subset or fakes for tests. Provider availability and secrets must not be hard-coded.

Alternative considered: build one fixed web search integration into the director. That reduces flexibility and makes testing more brittle.

### Keep MCP tools tagged and policy-filtered

MCP tools should be initialized at startup, cached, tagged as MCP-sourced tools, and then filtered per agent after policy assembly. MCP filesystem or Obsidian tools must be treated as external capabilities with explicit server allowlists and runtime context.

Alternative considered: expose all MCP tools globally. That would make tool schemas large and create avoidable permission risk.

### Store built-in Skills in the project and future Skills in storage

Built-in Skills should live in the product codebase so they are version-controlled and testable:

```text
backend/coresearcher/skills/builtin/<skill-name>/
  SKILL.md
  skill.yaml
```

Future user or generated Skills can live under local storage:

```text
storage/skills/user/<skill-name>/SKILL.md
storage/skills/generated/candidates/<skill-name>/SKILL.md
storage/skills/generated/enabled/<skill-name>/SKILL.md
storage/skills/user/.history/<skill-name>.jsonl
```

This mirrors deer-flow's public/custom/history shape while leaving generated Skills disabled until reviewed.

Alternative considered: store all Skills under the project directory. That is good for built-ins but poor for user-editable or generated content.

### Skills constrain tools by names and groups

Skill metadata should declare allowed tool names and allowed tool groups. The policy layer should treat missing explicit declarations conservatively once any active Skill declares allowed tools. This mirrors deer-flow's explicit allowed-tools behavior while adding group-level convenience.

Example:

```yaml
name: paper-reading
allowed_tool_groups:
  - file
  - pdf
  - artifact
allowed_tools:
  - read_file
  - read_pdf_text
  - write_artifact
output_schema: paper_reading_result
can_write_state: false
can_write_memory: false
```

Alternative considered: include tool instructions only in `SKILL.md`. Free-form text is useful for model behavior, but enforceable permissions need structured metadata.

### Enforce fail-closed tool policy

The effective tool list is the intersection of global policy, configured groups, subagent allow/deny lists, Skill policy, runtime context, model capability, and sandbox policy.

```text
configured + builtin + MCP + external-agent + optional subagent
        |
        v
dedupe by tool name
        |
        v
global policy
        |
        v
subagent allow/deny
        |
        v
Skill allowed tools/groups
        |
        v
runtime + sandbox policy
        |
        v
agent-bound tools
```

Alternative considered: fail-open tools with runtime errors. That produces surprising tool availability and increases the chance that sensitive tools appear in model schemas.

### Keep subagent delegation director-only

The subagent task tool is only exposed to the Research Director graph. Subagent runtimes must not receive it, preserving the existing decision that subagents cannot recursively call other subagents.

Alternative considered: allow expert subagents to delegate their own subtasks. That adds complexity and makes runaway delegation harder to control.

## Risks / Trade-offs

- Too many tools can overwhelm model schemas -> Use tool groups, deferred discovery, and provider-level config.
- Domain commands may feel less flexible than direct tools -> Allow structured model proposals and backend validation.
- Search providers may require secrets or have inconsistent response formats -> Keep provider modules optional and use fake providers in tests.
- User Skills can grant unsafe tools -> Disable user/generated Skills in MVP and validate metadata before enabling.
- MCP tools may expose broad capabilities -> Tag MCP tools, require server allowlists, and filter after policy assembly.
- File tools can leak host paths -> Use virtual paths, sandbox path validation, and output masking.
- Bash/code execution is high risk -> Keep host bash disabled by default and require sandbox policy approval.

## Migration Plan

This is a new runtime capability, so no data migration is required.

1. Add tool and Skill configuration models.
2. Implement local sandbox tool wrappers and register built-in tools.
3. Implement registry aggregation, deduplication, and policy filtering.
4. Add Skill storage and metadata validation for built-in Skills.
5. Wire subagent tool filtering and director-only subagent delegation.
6. Add optional provider adapters for search/API and MCP loading.
7. Add tests around tool availability, policy denial, duplicate names, Skill filtering, and sandbox boundaries.

Rollback strategy: disable configured tools and MCP loading, keep only built-in clarification/presentation tools and fake providers.

## Open Questions

- Which search provider should be enabled by default for local development: DDG, Tavily, or a fake provider?
- Should arXiv and Semantic Scholar be first-class academic tools in the MVP or provider adapters behind generic search?
- Should user-defined Skills be read-only in the first release, or hidden entirely until a later Skill management UI exists?
- Should PDF tools be implemented as local tools immediately or first as domain services invoked by paper-ingestion workflows?

---

# 中文版（阅读参考）

## 上下文

CoResearcher 需要一套贴近 deer-flow 实际形态的工具与 Skill 运行时，同时保留科研场景的安全边界。deer-flow 暴露给 LLM 的工具主要是沙箱文件访问、Shell 执行、搜索/API provider、MCP 工具、展示辅助工具和 Subagent 分派，而不是所有后端函数。

CoResearcher 需要明确区分 3 层：

- **LLM Tool：** 模型可调用的执行动作，例如 `bash`、`ls`、`glob`、`grep`、`read_file`、`write_file`、`str_replace`、搜索 provider、MCP 工具或仅供总控使用的 Subagent 分派。
- **Domain Command：** 后端校验后的状态变更，例如创建证据、记录决策、更新研究状态或提升记忆。
- **Skill：** 任务流程、输出契约和工具权限策略，不是可执行后端函数。

## 目标 / 非目标

**目标：**

- 明确 Tool、Domain Command 和 Skill 的边界。
- 提供参考 deer-flow 的工具注册表，聚合配置工具、内置工具、MCP 工具、外部 Agent 工具和可选的仅供总控使用的 Subagent 工具。
- 围绕沙箱文件操作、沙箱命令执行、产物文件、PDF/文档检查、用户展示和可选图片查看定义 CoResearcher 本地工具族。
- 通过配置驱动支持 DDG、Jina AI、Serper、Brave、Tavily、Firecrawl、Browserless、Exa、arXiv、Semantic Scholar 和 Crossref 等外部搜索/API 工具。
- 定义内置、用户和生成 Skill 的存储位置。
- 通过全局策略、工具组、Subagent 策略、Skill 策略、运行时上下文和沙箱策略执行 fail-closed 工具过滤。
- 将状态、证据和记忆写入排除在普通 LLM 工具调用之外。

**非目标：**

- 本变更不在 MVP 中实现所有 community search provider。
- 本变更不把任意后端 repository 函数暴露成 LLM Tool。
- 本变更不允许 Subagent 递归调用 Subagent。
- 本变更不在 MVP 中默认启用用户生成 Skill。
- 本变更不绕过本地文件或 bash 的沙箱边界。

## 设计决策

### 使用 Tool、Domain Command、Skill 三层模型

Tool 是模型可调用动作。Domain Command 是后端校验后的状态变更。Skill 是流程知识和权限约束。

这意味着研究状态更新、证据写入、论断创建、决策记录和记忆提升都不是普通 LLM Tool。模型可以提出结构化更新，但由后端服务校验并应用。

备选方案是暴露 `create_evidence_item` 或 `record_decision` 等领域变更工具。这样接线更简单，但会让模型直接改写持久研究事实，难以集中校验。

### 复用 deer-flow 的工具聚合形态

工具注册表应聚合以下来源：

- 应用配置中声明的配置工具
- 澄清、展示和可选图片查看等内置工具
- `bash`、`ls`、`glob`、`grep`、`read_file`、`write_file` 和 `str_replace` 等沙箱/本地工具
- 应用启动时初始化并缓存的 MCP 工具
- 可选外部 Agent 工具
- 仅供总控使用的 Subagent 分派工具

注册表应按实际 tool name 去重，并在配置名称与工具实际名称不一致时告警。

备选方案是为每个 Agent 手动绑定固定工具列表。这样第一版测试很容易，但不适合 MCP、可选 provider、模型能力检查和 Subagent 级工具策略。

### 本地工具都视为沙箱工具

CoResearcher 本地工具应是执行面，而不是业务服务。初始本地工具族包括：

- 文件检查：`ls`、`glob`、`grep`、`read_file`
- 文件修改：`write_file`、`str_replace`
- 命令执行：沙箱中的 `bash` 或 `run_python`
- 产物文件访问：在受控 artifact root 下列出、读取和写入文件
- 文档检查：PDF 文本提取和 PDF 页面/图片提取
- 展示辅助：向用户展示文件或产物
- 选配图片查看：当模型支持视觉能力时启用

除非配置和沙箱策略显式允许，否则禁止宿主文件系统访问和 host bash。

备选方案是把科研数据库动作做成本地工具。这些动作应保留为 Domain Command。

### 外部搜索/API provider 作为配置工具

搜索和检索 provider 应作为可选配置工具加载。CoResearcher 可以通过 provider 模块和配置支持 DDG、Jina AI、Serper、Brave、Tavily、Firecrawl、Browserless、Exa、arXiv、Semantic Scholar 和 Crossref。

MVP 应只启用少量确定性 provider 或 fake provider 用于测试。Provider 可用性和密钥不能硬编码。

备选方案是把一个固定 Web Search 集成写死在 Director 中。这样灵活性低，也更难测试。

### MCP 工具需要标记和策略过滤

MCP 工具应在启动时初始化、缓存，并标记为 MCP-sourced tools，然后在每个 Agent 的策略组装后再过滤。MCP filesystem 或 Obsidian 工具必须被视为外部能力，需要显式 server allowlist 和 runtime context。

备选方案是全局暴露所有 MCP 工具。这样会让工具 schema 过大，也带来不必要的权限风险。

### 内置 Skill 放项目内，未来 Skill 放 storage

内置 Skill 应位于产品代码库中，便于版本控制和测试：

```text
backend/coresearcher/skills/builtin/<skill-name>/
  SKILL.md
  skill.yaml
```

未来用户或生成 Skill 可以放在本地 storage：

```text
storage/skills/user/<skill-name>/SKILL.md
storage/skills/generated/candidates/<skill-name>/SKILL.md
storage/skills/generated/enabled/<skill-name>/SKILL.md
storage/skills/user/.history/<skill-name>.jsonl
```

这借鉴了 deer-flow 的 public/custom/history 形态，同时保证生成 Skill 在 review 前默认不启用。

备选方案是把所有 Skill 都放在项目目录。内置 Skill 适合这么做，但用户可编辑或生成内容不适合。

### Skill 用名称和分组约束工具

Skill 元数据应声明 allowed tool names 和 allowed tool groups。策略层在任意 active Skill 声明显式 allowed tools 后，应采用保守行为。这个规则借鉴 deer-flow 的 explicit allowed-tools 行为，并增加 group 级便利。

示例：

```yaml
name: paper-reading
allowed_tool_groups:
  - file
  - pdf
  - artifact
allowed_tools:
  - read_file
  - read_pdf_text
  - write_artifact
output_schema: paper_reading_result
can_write_state: false
can_write_memory: false
```

备选方案是只在 `SKILL.md` 中写工具说明。自由文本适合指导模型行为，但可执行权限需要结构化元数据。

### 工具权限 fail-closed

最终工具列表是全局策略、配置分组、Subagent 白名单/黑名单、Skill 策略、运行时上下文、模型能力和沙箱策略共同过滤后的结果。

```text
configured + builtin + MCP + external-agent + optional subagent
        |
        v
按 tool name 去重
        |
        v
global policy
        |
        v
subagent allow/deny
        |
        v
Skill allowed tools/groups
        |
        v
runtime + sandbox policy
        |
        v
绑定给 Agent 的工具
```

备选方案是 fail-open，然后在运行时报错。这样会让工具可见性难以预测，也更容易把敏感工具暴露给模型。

### Subagent 分派只给研究总控

Subagent task tool 只暴露给 Research Director 图。Subagent 运行时不得获得它，从而保留“Subagent 不能递归调用 Subagent”的既有决策。

备选方案是允许专家 Subagent 自己分派子任务。这会增加复杂度，也更难控制失控分派。

## 风险 / 权衡

- 工具过多会压垮模型 schema -> 使用工具组、延迟发现和 provider 级配置。
- Domain Command 不如直接工具灵活 -> 允许模型提出结构化更新，再由后端校验。
- Search provider 需要密钥且响应不稳定 -> provider 模块保持可选，测试使用 fake provider。
- 用户 Skill 可能授权危险工具 -> MVP 禁用用户/生成 Skill，启用前校验 metadata。
- MCP 工具可能暴露过宽能力 -> 标记 MCP 工具，要求 server allowlist，并在策略组装后过滤。
- 文件工具可能泄露宿主路径 -> 使用虚拟路径、沙箱路径校验和输出脱敏。
- Bash/代码执行风险高 -> 默认禁用 host bash，并要求沙箱策略显式允许。

## 迁移计划

这是新的运行时能力，不需要数据迁移。

1. 增加工具与 Skill 配置模型。
2. 实现本地沙箱工具包装和内置工具注册。
3. 实现工具注册表聚合、去重和策略过滤。
4. 增加内置 Skill 存储和元数据校验。
5. 接入 Subagent 工具过滤和仅供总控使用的 Subagent 分派。
6. 增加可选搜索/API provider adapter 和 MCP 加载。
7. 添加工具可见性、权限拒绝、重复名称、Skill 过滤和沙箱边界测试。

回滚策略：关闭配置工具和 MCP 加载，只保留澄清/展示内置工具和 fake provider。

## 开放问题

- 本地开发默认启用哪个搜索 provider：DDG、Tavily，还是 fake provider？
- arXiv 和 Semantic Scholar 是否作为 MVP 一等学术工具，还是先放在 generic search adapter 后？
- 第一版用户自定义 Skill 是只读加载，还是完全隐藏到后续 Skill 管理界面？
- PDF 工具应立即作为本地工具实现，还是先作为 paper-ingestion workflow 内部的 Domain Service？
