## Context

CoResearcher currently has the pieces of an observable research run: `ResearchEvent`, an in-memory `EventStore`, `/research/threads/{thread_id}/runs/stream`, `/research/runs/{run_id}/events`, frontend SSE parsing, assistant token deltas, and raw event display. The pieces are useful for development, but they are not yet a coherent trace experience. Events are inconsistent in payload shape, raw JSON is shown as the primary frontend progress surface, model token deltas are mixed with process events, and backend logs do not provide a structured `run_id` trail for postmortem debugging.

The desired experience is DeerFlow-like: when a user starts a research run, the UI should show where the run is in the pipeline, which subsystem is active, whether the model has started producing output, what changed in state, and where errors occurred. Developers should be able to correlate the same run through frontend trace, replay endpoint, and backend logs without exposing secrets or raw internal prompts.

## Goals / Non-Goals

**Goals:**

- Define a stable run event envelope with fields that support user-facing progress, debug inspection, hierarchy, replay, and structured logging.
- Emit meaningful backend stage events for both configured model runs and existing fake/director runs.
- Keep assistant token deltas separate from run process events so the frontend can render streamed prose and trace steps independently.
- Make the SSE stream, stored event replay, and backend structured logs originate from the same event emission path.
- Add a frontend Run Trace panel that summarizes progress in readable steps, while retaining raw event inspection for debugging.
- Keep events and errors non-secret-bearing.

**Non-Goals:**

- Do not introduce an external telemetry, tracing, or analytics service.
- Do not redesign the research director, subagent planner, memory subsystem, or model provider interface beyond the observability hooks needed for this change.
- Do not replace existing `/runs` non-streaming behavior.
- Do not expose raw prompts, API keys, provider request headers, or private environment values in events or logs.
- Do not build multi-user collaborative trace viewing.

## Decisions

### Decision: Extend `ResearchEvent` rather than introduce a separate trace model

Use the existing event model as the trace source of truth and add optional observability fields such as `phase`, `level`, `status`, `title`, `message`, `parent_id`, `sequence`, and `duration_ms`.

Alternatives considered:

- A separate `RunTrace`/`TraceSpan` model would be more formally aligned with distributed tracing, but it would duplicate the current EventStore/SSE contract and slow the MVP.
- Keeping the current payload-only model would avoid migration work, but it forces the frontend to infer meaning from ad hoc payload keys.

Rationale: the existing code already streams and stores `ResearchEvent`; extending it creates the least new machinery while preserving a path to span-like hierarchy via `parent_id`.

### Decision: Use a small event taxonomy with phase/status semantics

Event types should remain specific enough for code paths and tests, while `phase` and `status` support generic UI grouping. The initial taxonomy should cover:

- `run.*`: lifecycle and cancellation/failure.
- `thread.*`: thread load/save checkpoints.
- `context.*`: context build start/completion/compression.
- `model.*`: model selected, request started, first token, delta, request completed.
- `director.*`: route selection, plan creation, synthesis.
- `subagent.*`: started, progress, completed, failed.
- `tool.*`: started, output, completed, failed.
- `state.*`: state object updates, evidence, artifacts, memory candidates.
- `debug.*`: local debug metrics and warnings.

Token output may continue to use `final.response.delta` for compatibility, but the frontend should treat it as assistant content rather than a trace step.

Alternatives considered:

- Only using existing `run.progress` with a message string is simple but does not support reliable rendering, filtering, metrics, or replay.
- Using OpenTelemetry naming directly would be familiar to tracing tools, but the project is local-first and does not need external trace export yet.

### Decision: Centralize event emission

Create a single backend helper/path that, for each emitted event:

1. Assigns sequence/timestamps and safe metadata.
2. Appends to `EventStore`.
3. Writes a structured backend log line keyed by `run_id` and `event_id`.
4. Yields the event to SSE when streaming.

The helper should redact or omit secrets and should avoid logging raw prompts. For non-streaming `/runs`, events should still go through the same path so replay and logs remain consistent.

Alternatives considered:

- Let each subsystem append/log/yield separately. This matches the current code style, but creates drift between UI, replay, and logs.
- Only log at the FastAPI gateway. This misses internal stage boundaries and makes subagent/tool events harder to correlate.

### Decision: Frontend derives a `RunViewState` from events

The frontend should parse structured events into a view model:

- `assistantDraft`: accumulated token content.
- `steps`: user-readable trace steps with phase/status/title/message/time.
- `rawEvents`: full structured events for debug inspection.
- `metrics`: started time, first token time, completed time, delta count, model name, elapsed time.
- `error`: structured error when present.

The primary UI should show the assistant answer and Run Trace. Raw JSON should move behind a Debug/Raw tab.

Alternatives considered:

- Continue rendering raw SSE frames in the timeline. This is useful for debugging but too noisy for normal operation.
- Render only assistant prose. This hides the pipeline state and does not solve frontend/backend debugging.

### Decision: Keep replay API compatible while enriching output

`/research/runs/{run_id}/events` should continue returning events, but those events should include the enriched envelope. The frontend can use replay to show the previous run trace when a thread is reselected.

### Decision: Treat logs as local observability, not telemetry

Structured backend logs should remain local process logs or configured local file logs. They should not add analytics, remote telemetry, or network calls.

## Risks / Trade-offs

- Event schema churn can break frontend assumptions -> Add unit tests around representative event types and keep compatibility for existing fields (`type`, `payload`, `created_at`, `run_id`, `thread_id`).
- Too many delta events can make raw trace noisy and memory-heavy -> Do not show token deltas as trace steps; summarize delta count and keep raw inspection available.
- Logging raw payloads may leak prompt or private configuration -> Use safe event metadata, redact secrets, and avoid raw prompt bodies in logs.
- Fake/director runs and real model runs may diverge -> Route both through the same event emission helper and cover both in tests.
- Frontend trace can become visually crowded -> Group by phase, use compact step rows, and place raw/debug details behind tabs.
- EventStore is currently in-memory for the gateway app -> Preserve existing behavior for this change; durable replay can build on the session memory repository later.

## Migration Plan

1. Add optional event envelope fields in a backward-compatible way.
2. Introduce centralized event emission without removing existing event types.
3. Convert configured model streaming path to emit enriched model/thread/run events.
4. Convert fake/director path and subagent events to use the same envelope fields where possible.
5. Update frontend SSE handling to derive a Run Trace view while keeping raw event inspection.
6. Add tests for event envelope shape, streaming order, raw replay, frontend view derivation, and non-secret error/log behavior.
7. Rollback can retain old frontend raw event display and ignore new envelope fields because the core SSE/event types remain compatible.

## Open Questions

- Should `final.response.delta` remain the long-term token event name, or should it become `model.delta` with `final.response.delta` kept as a compatibility alias?
- Should backend structured logs write only to stdout initially, or should a local file sink be configurable?
- Should replay load only the latest run for a thread in the frontend, or provide a selectable run history?
- Should event `sequence` be per run or globally monotonic within a process?
