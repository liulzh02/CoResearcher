## 1. Tool And Skill Configuration

- [ ] 1.1 Define typed configuration models for tools, tool groups, MCP servers, external providers, Skill storage, Skill metadata, and tool policy defaults.
- [ ] 1.2 Add config fields for enabling built-in tools, sandbox tools, search providers, MCP tools, external-agent tools, and director-only subagent delegation.
- [ ] 1.3 Add validation that secrets are read from environment variables and never embedded in provider config.
- [ ] 1.4 Add tests for config defaults, invalid tool references, disabled providers, missing secrets, and unknown tool groups.

## 2. Local Sandbox Tools

- [ ] 2.1 Implement sandbox-scoped file inspection tools: `ls`, `glob`, `grep`, and `read_file`.
- [ ] 2.2 Implement sandbox-scoped file mutation tools: `write_file` and `str_replace`, with path validation and file operation locking.
- [ ] 2.3 Implement sandbox command execution tools such as `bash` or `run_python`, disabled by default unless sandbox policy allows them.
- [ ] 2.4 Implement artifact file tools for listing, reading, and writing files under controlled artifact roots.
- [ ] 2.5 Implement MVP document inspection tools for PDF text extraction and optional PDF page/image extraction.
- [ ] 2.6 Add tests for virtual path resolution, host path denial, host bash denial, output truncation, file write limits, binary read rejection, and artifact root isolation.

## 3. Built-In And External Tools

- [ ] 3.1 Implement built-in interaction tools for clarification, presenting files/artifacts, and optional image viewing when the selected model supports vision.
- [ ] 3.2 Add provider interfaces or adapters for search/retrieval tools, starting with deterministic fake providers and a small MVP provider set.
- [ ] 3.3 Add optional config entries for DDG, Jina AI, Serper, Brave, Tavily, Firecrawl, Browserless, Exa, arXiv, Semantic Scholar, and Crossref.
- [ ] 3.4 Add tests for disabled providers, enabled fake providers, environment-secret handling, provider error sanitization, and untrusted tool output handling.

## 4. Tool Registry And Policy

- [ ] 4.1 Implement tool registry aggregation from configured tools, built-in tools, sandbox tools, MCP tools, external-agent tools, and optional subagent delegation tools.
- [ ] 4.2 Implement deterministic duplicate tool-name handling with warnings for skipped duplicates.
- [ ] 4.3 Implement tool filtering by tool group, global policy, subagent allowlist, subagent denylist, Skill policy, runtime context, model capability, and sandbox policy.
- [ ] 4.4 Ensure policy is fail-closed: a tool denied by any policy layer is not bound to the agent.
- [ ] 4.5 Add tests for group filtering, duplicate names, skill restrictions, model capability restrictions, sandbox denial, runtime denial, and fail-closed behavior.

## 5. MCP And External Agent Tools

- [ ] 5.1 Implement MCP tool initialization, runtime cache access, and MCP-source metadata tagging.
- [ ] 5.2 Filter MCP tools per agent after registry assembly and policy evaluation.
- [ ] 5.3 Add optional external-agent invocation tool support behind explicit configuration.
- [ ] 5.4 Add tests for cached MCP tools, MCP server allowlists, MCP filtering per subagent, MCP tool-name collisions, external-agent disabled state, and untrusted MCP output handling.

## 6. Skill Storage And Validation

- [ ] 6.1 Define built-in Skill storage under `backend/coresearcher/skills/builtin/<skill-name>/` with `SKILL.md` and `skill.yaml`.
- [ ] 6.2 Reserve future storage paths for user Skills, generated candidate Skills, enabled generated Skills, and Skill history under `storage/skills/`.
- [ ] 6.3 Implement Skill metadata parsing and validation for name, description, allowed tools, allowed tool groups, output schema, and state/memory write permissions.
- [ ] 6.4 Add bundled MVP Skills for literature review, paper reading, evidence curation, research critique, coding reproduction, memory extraction, and synthesis.
- [ ] 6.5 Add tests for built-in Skill loading, invalid metadata, duplicate Skill names, generated Skill disabled state, and Skill history path handling.

## 7. Skill-To-Tool Runtime Integration

- [ ] 7.1 Load configured Skills for the Research Director and built-in subagents.
- [ ] 7.2 Inject Skill content as runtime guidance while enforcing structured Skill metadata in tool policy.
- [ ] 7.3 Filter tools by Skill allowed tool names and allowed tool groups before binding tools to agents.
- [ ] 7.4 Add tests for paper-reading Skill tool restrictions, coding-reproduction sandbox access, memory-extraction write restrictions, and legacy Skill behavior without explicit allowed tools.

## 8. Domain Command Boundary

- [ ] 8.1 Define domain command interfaces for research state updates, evidence writes, claim creation, decision recording, critique recording, and memory promotion.
- [ ] 8.2 Ensure domain commands are invoked only after backend validation of structured model outputs or user actions.
- [ ] 8.3 Ensure domain commands are excluded from ordinary LLM tool registry output.
- [ ] 8.4 Add tests that `create_evidence_item`, `record_decision`, `update_research_state`, and memory promotion are not exposed as regular tools.
- [ ] 8.5 Add tests for backend validation before applying proposed state, evidence, decision, and memory changes.

## 9. Subagent Tool Boundaries

- [ ] 9.1 Expose subagent delegation only to the Research Director graph.
- [ ] 9.2 Ensure subagent runtimes never receive subagent delegation tools, preserving no-recursive-delegation behavior.
- [ ] 9.3 Define default tool groups for `literature-scout`, `paper-reader`, `methodologist`, `coding-researcher`, `evidence-curator`, `critic`, `synthesizer`, and any memory service.
- [ ] 9.4 Add tests for each built-in subagent's effective tool list and recursive delegation denial.

## 10. Documentation And Verification

- [ ] 10.1 Document the Tool vs Domain Command vs Skill boundary.
- [ ] 10.2 Document local tool groups, external provider config, MCP tool loading, Skill storage layout, and fail-closed policy.
- [ ] 10.3 Add deterministic integration tests covering registry assembly, Skill loading, MCP filtering, search provider fakes, sandbox tools, and domain command exclusion.
- [ ] 10.4 Run the fastest relevant validation and test commands, and record them in the implementation summary.

---

# 中文版（阅读参考）

说明：下面是任务清单的中文阅读版。为了不影响 OpenSpec 对任务复选框的解析，这里使用普通列表，不使用 `- [ ]` 格式。

## 1. 工具与 Skill 配置

- 1.1 定义工具、工具组、MCP server、外部 provider、Skill 存储、Skill 元数据和工具策略默认值的类型化配置模型。
- 1.2 增加配置字段，用于启用内置工具、沙箱工具、搜索 provider、MCP 工具、外部 Agent 工具和仅供总控使用的 Subagent 分派。
- 1.3 增加校验，确保密钥只从环境变量读取，不能写入 provider 配置。
- 1.4 添加测试，覆盖配置默认值、无效工具引用、禁用 provider、缺失密钥和未知工具组。

## 2. 本地沙箱工具

- 2.1 实现沙箱范围内的文件检查工具：`ls`、`glob`、`grep` 和 `read_file`。
- 2.2 实现沙箱范围内的文件修改工具：`write_file` 和 `str_replace`，并加入路径校验和文件操作锁。
- 2.3 实现 `bash` 或 `run_python` 等沙箱命令执行工具，默认禁用，除非沙箱策略允许。
- 2.4 实现产物文件工具，用于在受控 artifact root 下列出、读取和写入文件。
- 2.5 实现 MVP 文档检查工具，包括 PDF 文本提取和可选的 PDF 页面/图片提取。
- 2.6 添加测试，覆盖虚拟路径解析、宿主路径拒绝、host bash 拒绝、输出截断、文件写入大小限制、二进制读取拒绝和 artifact root 隔离。

## 3. 内置与外部工具

- 3.1 实现澄清、文件/产物展示，以及模型支持视觉时可启用的图片查看等内置交互工具。
- 3.2 为搜索/检索工具增加 provider 接口或 adapter，从确定性 fake provider 和少量 MVP provider 开始。
- 3.3 增加 DDG、Jina AI、Serper、Brave、Tavily、Firecrawl、Browserless、Exa、arXiv、Semantic Scholar 和 Crossref 的可选配置入口。
- 3.4 添加测试，覆盖禁用 provider、启用 fake provider、环境变量密钥处理、provider 错误脱敏和不可信工具输出处理。

## 4. 工具注册表与策略

- 4.1 实现工具注册表，从配置工具、内置工具、沙箱工具、MCP 工具、外部 Agent 工具和可选 Subagent 分派工具聚合工具。
- 4.2 实现确定性的重复工具名处理，并对跳过的重复工具记录告警。
- 4.3 实现按工具组、全局策略、Subagent 白名单、Subagent 黑名单、Skill 策略、运行时上下文、模型能力和沙箱策略过滤工具。
- 4.4 确保策略 fail-closed：任意策略层拒绝的工具都不能绑定给 Agent。
- 4.5 添加测试，覆盖分组过滤、重复名称、Skill 限制、模型能力限制、沙箱拒绝、运行时拒绝和 fail-closed 行为。

## 5. MCP 与外部 Agent 工具

- 5.1 实现 MCP 工具初始化、运行时缓存访问和 MCP 来源元数据标记。
- 5.2 在注册表组装和策略评估后，按 Agent 过滤 MCP 工具。
- 5.3 在显式配置之后，增加可选外部 Agent 调用工具支持。
- 5.4 添加测试，覆盖 MCP 工具缓存、MCP server 白名单、按 Subagent 过滤 MCP、MCP 工具名冲突、外部 Agent 禁用状态和不可信 MCP 输出处理。

## 6. Skill 存储与校验

- 6.1 在 `backend/coresearcher/skills/builtin/<skill-name>/` 下定义内置 Skill 存储，包含 `SKILL.md` 和 `skill.yaml`。
- 6.2 在 `storage/skills/` 下为未来用户 Skill、生成候选 Skill、已启用生成 Skill 和 Skill 历史预留路径。
- 6.3 实现 Skill 元数据解析和校验，覆盖名称、描述、允许工具、允许工具组、输出 schema，以及状态/记忆写入权限。
- 6.4 增加 MVP 内置 Skill：文献综述、论文阅读、证据整理、研究质疑、代码复现、记忆提炼和综合输出。
- 6.5 添加测试，覆盖内置 Skill 加载、无效元数据、重复 Skill 名称、生成 Skill 禁用状态和 Skill history 路径处理。

## 7. Skill 与工具运行时集成

- 7.1 为 Research Director 和内置 Subagent 加载配置的 Skill。
- 7.2 将 Skill 内容作为运行时指导注入，同时在工具策略中执行结构化 Skill 元数据。
- 7.3 在工具绑定给 Agent 前，按 Skill 允许的工具名和工具组过滤工具。
- 7.4 添加测试，覆盖 paper-reading Skill 工具限制、coding-reproduction 沙箱访问、memory-extraction 写入限制和未显式声明 allowed tools 的 legacy Skill 行为。

## 8. Domain Command 边界

- 8.1 定义研究状态更新、证据写入、论断创建、决策记录、质疑记录和记忆提升的 Domain Command 接口。
- 8.2 确保 Domain Command 只在后端校验结构化模型输出或用户动作后调用。
- 8.3 确保 Domain Command 从普通 LLM 工具注册表输出中排除。
- 8.4 添加测试，确保 `create_evidence_item`、`record_decision`、`update_research_state` 和记忆提升不会作为普通工具暴露。
- 8.5 添加测试，覆盖应用状态、证据、决策和记忆变更前的后端校验。

## 9. Subagent 工具边界

- 9.1 仅向 Research Director 图暴露 Subagent 分派工具。
- 9.2 确保 Subagent runtime 永远不会获得 Subagent 分派工具，保留禁止递归分派的行为。
- 9.3 为 `literature-scout`、`paper-reader`、`methodologist`、`coding-researcher`、`evidence-curator`、`critic`、`synthesizer` 和记忆服务定义默认工具组。
- 9.4 添加测试，覆盖每个内置 Subagent 的有效工具列表和递归分派拒绝。

## 10. 文档与验证

- 10.1 记录 Tool、Domain Command 和 Skill 的边界。
- 10.2 记录本地工具组、外部 provider 配置、MCP 工具加载、Skill 存储布局和 fail-closed 策略。
- 10.3 添加确定性集成测试，覆盖注册表组装、Skill 加载、MCP 过滤、搜索 provider fake、沙箱工具和 Domain Command 排除。
- 10.4 运行最快相关校验和测试命令，并在实现总结中记录。
