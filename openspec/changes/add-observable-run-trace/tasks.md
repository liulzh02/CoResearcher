## 1. Backend Event Envelope

- [x] 1.1 Extend the research event model with backward-compatible observability fields for phase, level, status, title, message, parent identifier, sequence, and duration metadata.
- [x] 1.2 Add or normalize event type constants for run, thread, context, model, director, subagent, tool, state, artifact, debug, and assistant delta events.
- [x] 1.3 Add tests proving existing fields remain available for streamed and replayed events.
- [x] 1.4 Add tests proving event metadata can represent hierarchy and user-readable trace steps.

## 2. Backend Emission, Replay, and Logs

- [x] 2.1 Introduce a centralized event emission helper that assigns sequence/timing metadata and appends events to the event store.
- [x] 2.2 Make the centralized emitter produce structured local backend log records keyed by run id and event id.
- [x] 2.3 Ensure emitted log records and event payloads exclude secrets, raw provider authorization data, private environment values, and raw internal prompts.
- [x] 2.4 Update the streaming run path to yield events from the centralized emitter in sequence order.
- [x] 2.5 Keep `/research/runs/{run_id}/events` compatible while returning enriched event envelopes for replay.
- [x] 2.6 Add backend tests for SSE ordering, replay contents, safe provider failures, and structured log correlation.

## 3. Backend Run Stage Coverage

- [x] 3.1 Emit configured-model trace events for run start, thread load, model selection, model request start, first token, model request completion, thread save, and run completion.
- [x] 3.2 Keep assistant delta events separate from process trace events during model streaming.
- [x] 3.3 Emit director/fake-path trace events for context loading, route selection, planning, state update, synthesis, artifact creation, and run completion.
- [x] 3.4 Normalize subagent start, progress, completion, failure, and timeout events so they can render as trace steps.
- [x] 3.5 Emit state mutation events for evidence, artifacts, memory candidates, decisions, todos, claims, or other durable research state objects when updated.
- [x] 3.6 Add tests covering both configured-model and fake/director run traces.

## 4. Frontend Run Trace State

- [x] 4.1 Define frontend types for enriched research events, run trace steps, run metrics, raw event inspection, and structured run errors.
- [x] 4.2 Derive a `RunViewState` from streamed events that separates assistant draft text, trace steps, raw events, metrics, and errors.
- [x] 4.3 Accumulate assistant response deltas without rendering them as process trace steps.
- [x] 4.4 Map backend event phase/status/title/message fields into readable trace step labels.
- [x] 4.5 Add frontend unit tests for event-to-run-view derivation, assistant delta accumulation, failure states, and raw event retention.

## 5. Frontend DeerFlow-Style Workbench UI

- [x] 5.1 Replace raw-event-first timeline rendering with a Run Trace panel that shows phase, status, title/message, elapsed timing, and active/completed/failed states.
- [x] 5.2 Keep streamed assistant output visible as assistant prose while the run is active.
- [x] 5.3 Move raw structured events behind an explicit debug/raw inspection tab.
- [x] 5.4 Add replay support so selecting a completed run or thread can show the stored trace when events are available.
- [x] 5.5 Preserve existing evidence, artifacts, memory, tools, models, and subagents inspection panels.
- [x] 5.6 Ensure loading, empty, running, completed, failed, and recoverable error states remain explicit and non-blocking.

## 6. Verification

- [x] 6.1 Run the full backend test suite.
- [x] 6.2 Run frontend tests.
- [x] 6.3 Run frontend lint and production build.
- [x] 6.4 Manually verify a configured DeepSeek streaming run emits process events, assistant deltas, completion, replayable events, and no secret-bearing output.
- [x] 6.5 Manually verify the frontend shows a readable run trace, streamed assistant output, raw debug events, and failed-run state.
