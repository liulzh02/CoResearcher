# Tool And Skill Runtime

CoResearcher keeps three runtime surfaces separate:

- **LLM Tool:** model-callable executable actions such as `ls`, `glob`, `grep`, `read_file`, `write_file`, `str_replace`, `bash`, search providers, MCP tools, presentation helpers, and director-only subagent delegation.
- **Domain Command:** backend-validated durable mutations such as `create_evidence_item`, `record_decision`, `update_research_state`, and memory promotion. These are not exposed as ordinary LLM tools.
- **Skill:** procedural guidance plus structured metadata for output contracts and tool permissions. Skills are loaded as runtime guidance; their metadata constrains tool binding.

## Local Tools

Local tools are sandbox-scoped:

- `ls`, `glob`, `grep`, `read_file` inspect allowed sandbox paths.
- `write_file` and `str_replace` mutate only allowed sandbox paths and enforce write limits.
- `bash` is disabled unless both runtime context and sandbox policy explicitly allow it.
- `list_artifacts`, `read_artifact`, and `write_artifact` operate only under `artifact_root`.
- `read_pdf_text` provides MVP PDF text inspection for sandboxed files.

Tool output from files, documents, search, MCP, and external providers is treated as untrusted data.

## Provider Config

Search/retrieval providers are optional config-driven tools. The config surface reserves entries for `fake`, `ddg`, `jina_ai`, `serper`, `brave`, `tavily`, `firecrawl`, `browserless`, `exa`, `arxiv`, `semantic_scholar`, and `crossref`.

Secrets must be referenced by environment variable name via `secret_env`; inline secret values are rejected by the configuration model.

## MCP And External Agents

MCP tools are cached by server, tagged with `source=mcp` and `mcp_server`, and filtered per runtime context using server allowlists. External-agent tools are disabled unless configured explicitly.

## Skill Storage

Built-in Skills live in the project:

```text
backend/coresearcher/skills/builtin/<skill-name>/
  SKILL.md
  skill.yaml
```

Future local storage is reserved under:

```text
storage/skills/user/
storage/skills/generated/candidates/
storage/skills/generated/enabled/
storage/skills/user/.history/
```

Generated candidates are not loaded until moved into the enabled generated path.

## Fail-Closed Policy

Effective tools are filtered by:

- explicit tool names and groups
- denied tool names
- director-only flags
- Skill `allowed_tools` and `allowed_tool_groups`
- model capability such as vision support
- sandbox permission such as bash execution
- MCP server allowlists
- subagent delegation policy

If any policy layer denies a tool, the tool is not bound to the agent.
