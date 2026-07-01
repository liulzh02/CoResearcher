# CoResearcher Backend MVP

## Local Setup

Install the backend with test dependencies:

```bash
python -m pip install -e ".[test]"
```

Run the API:

```bash
python -m coresearcher
```

Run tests:

```bash
python -m pytest
```

## Environment Variables

CoResearcher reads secrets only from environment variables. Do not place provider keys in YAML files or source code.

Common variables:

```bash
CORESEARCHER_ENV=local
CORESEARCHER_CONFIG=configs/coresearcher.example.yaml
CORESEARCHER_DEFAULT_USER_ID=local-user
```

Provider integrations can require additional variables such as `OPENAI_API_KEY` or other provider-specific keys when those providers are configured later.

## Initial API Surface

- `GET /health`
- `GET /models`
- `GET /tools`
- `GET /subagents`
- `POST /research/threads`
- `GET /research/threads`
- `GET /research/threads/{thread_id}`
- `PUT /research/threads/{thread_id}/state`
- `POST /research/threads/{thread_id}/runs`
- `POST /research/threads/{thread_id}/runs/stream`
- `GET /research/threads/{thread_id}/artifacts/{artifact_id}`
- `GET /research/threads/{thread_id}/evidence`
- `GET /knowledge-base/notes`
- `POST /knowledge-base/notes`

## MVP Behavior

The current backend uses deterministic fake model and fake subagent behavior so tests can run without provider credentials. Research claims, evidence, critique notes, artifacts, and open questions are typed state objects instead of prose-only chat history.

Subagent delegation is director-only. Subagents cannot recursively invoke other Subagents.

## 中文说明

当前后端 MVP 的重点是建立可运行的架构基线，而不是接入真实模型或真实文献搜索服务。实现包括 FastAPI 网关、LangGraph Research Director、注册表驱动的 Subagent、结构化研究状态、证据和产物模型、SSE 事件、工具权限过滤、知识库 adapter 接口、安全上下文和 sandbox 策略。默认使用 fake runtime，便于在没有密钥的情况下做确定性测试。真实 Provider、真实 MCP/Obsidian 和更强 sandbox 可以在后续 change 中替换接口实现。

