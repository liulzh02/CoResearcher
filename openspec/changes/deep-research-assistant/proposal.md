## Why

CoResearcher needs a product and backend foundation for a deep research scientific assistant that collaborates with researchers throughout the research process instead of only producing a static literature summary or paper draft. The first version should establish a multi-subagent, LangGraph-based architecture that can support investigation, critique, evidence tracking, discussion, and iterative narrowing of research directions.

## What Changes

- Introduce a research director agent that owns the long-running conversation, research state, user alignment, and final synthesis.
- Introduce specialized research subagents for literature discovery, paper reading, methodology analysis, code-based experiment/reproduction, evidence curation, skeptical critique, and synthesis.
- Add structured research thread state for research questions, hypotheses, papers, evidence items, claims, open questions, decisions, critique notes, artifacts, and todos.
- Define the backend architecture around Python, FastAPI, LangGraph, streaming run events, and a registry-driven subagent configuration model inspired by deer-flow.
- Define research outputs as iterative artifacts such as research briefs, evidence maps, critique notes, reading summaries, and next-step recommendations.
- Defer frontend implementation details, provider-specific model wiring, and production deployment hardening to later changes unless needed for the backend MVP.

## Capabilities

### New Capabilities

- `research-orchestration`: Covers the research director agent, subagent delegation model, research lifecycle, and iterative user collaboration behavior.
- `research-state`: Covers structured persistence of research questions, hypotheses, papers, claims, evidence, critique notes, decisions, todos, and artifacts.
- `research-evidence`: Covers citation-aware evidence capture, claim-to-source traceability, paper summaries, and source quality signals.
- `research-streaming-api`: Covers backend APIs and event streaming needed to expose long-running research progress, subagent activity, and artifacts.

### Modified Capabilities

None. This is the first OpenSpec change in the project and there are no existing capabilities under `openspec/specs/`.

## Impact

- Affected backend areas: Python project scaffold, FastAPI gateway, LangGraph graph factory, agent/subagent runtime, model configuration, persistence, and streaming events.
- Affected data model areas: research thread state, paper metadata, evidence items, claims, decisions, critique notes, and artifact records.
- Expected dependencies: LangGraph/LangChain runtime, FastAPI, Pydantic, async persistence layer, PDF/text ingestion utilities, and optional search or scholarly source connectors.
- Security and quality considerations: no secrets in code, explicit provider configuration through environment variables, citation traceability for research claims, bounded subagent concurrency, and tests for behavior-changing runtime paths.

## Chinese Supplement: Coding Subagent

Subagent 范围新增 `coding-researcher`，用于代码实验、论文方法复现、数据分析和 baseline 检查。它的输出应作为 evidence item 或 artifact 进入研究状态，不能默认视为最终研究结论。

---

# 中文版（阅读参考）

## 背景与动机

CoResearcher 需要一套面向科研场景的产品和后端基础，用来构建一个深度研究科研助手。它的目标不是只生成静态文献总结或论文草稿，而是持续参与研究过程，和研究者一起讨论、推敲和收敛方向。第一版应建立基于多 Subagent 和 LangGraph 的架构，支持调研、质疑、证据追踪、讨论和研究方向迭代。

## 变更内容

- 引入研究总控 Agent，负责长周期对话、研究状态、用户对齐和最终综合。
- 引入专门的科研 Subagent，分别处理文献发现、论文阅读、证据整理、方法分析、批判性质疑和综合输出。
- 增加结构化研究线程状态，覆盖研究问题、假设、论文、证据项、论断、开放问题、决策、质疑记录、产物和待办事项。
- 围绕 Python、FastAPI、LangGraph、流式运行事件和注册表驱动的 Subagent 配置模型定义后端架构，并参考 deer-flow 的架构形态。
- 将研究输出定义为可迭代产物，例如研究简报、证据图谱、质疑记录、阅读总结和下一步建议。
- 前端实现细节、具体模型 Provider 接入和生产部署加固暂不纳入本次变更，除非后端 MVP 必须依赖。

## 能力范围

### 新增能力

- `research-orchestration`：覆盖研究总控 Agent、Subagent 分派模型、研究生命周期和迭代式用户协作行为。
- `research-state`：覆盖研究问题、假设、论文、论断、证据、质疑记录、决策、待办事项和产物的结构化持久化。
- `research-evidence`：覆盖带引用意识的证据采集、论断到来源的可追踪性、论文总结和来源质量信号。
- `research-streaming-api`：覆盖后端 API 和事件流能力，用于暴露长时间研究进度、Subagent 活动和研究产物。

### 修改能力

无。本项目当前是第一次 OpenSpec 变更，`openspec/specs/` 下还没有已有能力。

## 影响范围

- 影响后端区域：Python 项目脚手架、FastAPI Gateway、LangGraph 图工厂、Agent/Subagent 运行时、模型配置、持久化和流式事件。
- 影响数据模型区域：研究线程状态、论文元数据、证据项、论断、决策、质疑记录和产物记录。
- 预期依赖：LangGraph/LangChain 运行时、FastAPI、Pydantic、异步持久化层、PDF/文本解析工具，以及可选的搜索或学术来源连接器。
- 安全和质量要求：代码中不包含密钥，通过环境变量配置 Provider；研究论断需要可追踪引用；Subagent 并发必须有边界；运行时行为变化需要配套测试。
