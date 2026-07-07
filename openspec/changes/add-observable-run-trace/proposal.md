## Why

CoResearcher can now stream model output and basic run events, but frontend/backend debugging still feels opaque: raw SSE frames, assistant tokens, state updates, and runtime errors are mixed together without a clear run narrative. A DeerFlow-style observable run trace will make each research run understandable, replayable, and debuggable from the UI and backend logs.

## What Changes

- Introduce a unified run event envelope for user-visible progress, debug metadata, model streaming, state updates, subagent activity, and errors.
- Add structured run trace events around key backend stages such as thread loading, model selection, context building, model request start/first-token/completion, persistence, and run completion.
- Keep token deltas separate from process events so the frontend can render assistant output and run progress independently.
- Add structured backend logging keyed by `run_id` and `event_id`, sourced from the same events sent over SSE and stored for replay.
- Replace the current raw-event-first frontend display with a DeerFlow-style Run Trace panel, while keeping raw event inspection available for debugging.
- Preserve existing non-streaming run APIs and existing SSE compatibility where possible.

## Capabilities

### New Capabilities
- `observable-run-trace`: Defines the unified event envelope, event taxonomy, run replay semantics, and structured logging requirements for observable research runs.

### Modified Capabilities
- `research-streaming-api`: Clarifies that streamed events must include structured stage progress before final completion, not only raw or post-hoc events.
- `research-workbench-frontend`: Refines the frontend requirement from raw progress display to a user-readable Run Trace with assistant streaming, status steps, errors, and raw debug inspection.

## Impact

- Backend domain events, event store, research service streaming flow, gateway SSE endpoint, and backend logging.
- Frontend SSE parsing, run state management, timeline/run trace rendering, inspector tabs, loading/error states, and tests.
- Existing model provider streaming and fake/director run paths should remain supported.
- No new external telemetry service is required; logs and events remain local and non-secret-bearing.
