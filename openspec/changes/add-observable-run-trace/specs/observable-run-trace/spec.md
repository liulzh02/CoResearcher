## ADDED Requirements

### Requirement: Research run events use an observable envelope
The system SHALL emit research run events using a structured envelope that includes stable event identity, run correlation, user-facing status, and machine-readable payload data.

#### Scenario: Event includes trace metadata
- **WHEN** any research run event is emitted
- **THEN** the event includes `id`, `thread_id`, `run_id`, `type`, `created_at`, `payload`, and trace metadata sufficient to render a user-readable run step

#### Scenario: Event supports hierarchy
- **WHEN** an event belongs under a broader run stage such as a model request, subagent task, or tool call
- **THEN** the event can reference its parent event or stage without losing the run-level `run_id`

#### Scenario: Event remains backward compatible
- **WHEN** an existing client reads streamed or replayed events
- **THEN** the existing `type`, `payload`, `thread_id`, `run_id`, and `created_at` fields remain available

### Requirement: Run trace distinguishes assistant deltas from process steps
The system SHALL distinguish assistant output deltas from process lifecycle events so clients can render streamed prose separately from run progress.

#### Scenario: Assistant token delta received
- **WHEN** the model streams partial assistant content
- **THEN** the stream includes a delta event that identifies the content as assistant output rather than a user-facing process step

#### Scenario: Process event received
- **WHEN** the run loads context, selects a model, calls a provider, updates state, starts a subagent, or completes a run
- **THEN** the stream includes a process event that can be rendered as a trace step without parsing assistant prose

### Requirement: Run trace covers key backend stages
The system SHALL emit trace events for the major backend stages of a research run.

#### Scenario: Configured model run emits model stages
- **WHEN** a research run uses a configured non-fake model provider
- **THEN** the trace includes events for run start, thread load, model selection, model request start, first token when available, model request completion, thread save, and run completion

#### Scenario: Director run emits orchestration stages
- **WHEN** a research run uses the director or fake MVP path
- **THEN** the trace includes events for context loading, route selection, planning, subagent activity when present, state updates, synthesis, artifacts when created, and run completion

#### Scenario: State mutation emits trace
- **WHEN** the run creates or updates durable research state such as evidence, artifacts, memory candidates, decisions, todos, or claims
- **THEN** the trace includes an event identifying the affected object type and identifier

### Requirement: Events drive SSE, replay, and backend logs
The system SHALL use the same event emission path for streaming to clients, replaying run history, and writing structured backend logs.

#### Scenario: Event is streamed
- **WHEN** an event is emitted during a streaming run
- **THEN** the event is sent over the server streaming response in order

#### Scenario: Event is replayable
- **WHEN** a client requests events for a completed run by `run_id`
- **THEN** the backend returns the same event sequence that was emitted during execution, subject to retention limits

#### Scenario: Event is logged
- **WHEN** an event is emitted
- **THEN** the backend writes a structured local log record containing at least `run_id`, `event_id`, `event_type`, status or level, and safe message metadata

### Requirement: Observability data is non-secret-bearing
The system MUST NOT expose secrets, API keys, private environment values, raw provider authorization headers, or raw internal prompts in run events, replay output, or structured logs.

#### Scenario: Provider error occurs
- **WHEN** a provider request fails during a run
- **THEN** streamed events, replayed events, and backend logs identify the failing subsystem and safe error category without including secret values

#### Scenario: Debug metadata is emitted
- **WHEN** the system emits debug metrics such as token estimates, latency, model name, or retry count
- **THEN** the metadata excludes raw prompts and credentials

### Requirement: Run trace records timing and completion status
The system SHALL record enough timing and status data to show elapsed time, first-token timing when applicable, successful completion, and failure.

#### Scenario: First token arrives
- **WHEN** a streaming model provider returns the first assistant delta
- **THEN** the trace records a first-token event or metric correlated to the run

#### Scenario: Run completes
- **WHEN** a research run completes successfully
- **THEN** the trace records completion status and elapsed timing information

#### Scenario: Run fails
- **WHEN** a research run fails before completion
- **THEN** the trace records a failure event with a safe error summary and the frontend can render the failed status
