## MODIFIED Requirements

### Requirement: Backend streams research run events
The system SHALL stream long-running research run events to clients using a server-supported streaming mechanism, and the streamed events SHALL include structured stage progress before final completion rather than only post-hoc or raw debug output.

#### Scenario: Run emits progress
- **WHEN** a research run is executing
- **THEN** the client receives structured progress events before the final answer is complete

#### Scenario: Run emits model progress
- **WHEN** a configured streaming model provider is invoked
- **THEN** the stream includes model request start, first-token when available, assistant delta, and model completion events before run completion

#### Scenario: Stream preserves event order
- **WHEN** multiple events are emitted during a run
- **THEN** the streaming response delivers those events in run sequence order

### Requirement: Streaming events include subagent activity
The system SHALL emit structured events when subagents start, make notable progress, complete, fail, time out, or return notable intermediate results.

#### Scenario: Subagent completes
- **WHEN** a paper reader subagent finishes analyzing a paper
- **THEN** the stream includes a completion event with subagent type, task description, status, and result summary or artifact reference

#### Scenario: Subagent is visible in trace
- **WHEN** a subagent starts or completes during a research run
- **THEN** the stream includes enough event metadata for the frontend to render that subagent as a run trace step

### Requirement: Streaming events include research state changes
The system SHALL emit events when the research run adds or updates major research state objects such as papers, evidence items, claims, decisions, critique notes, todos, memory candidates, or artifacts.

#### Scenario: Evidence item added
- **WHEN** an evidence curator adds a new evidence item to the research state
- **THEN** the stream includes a state update event identifying the object type and identifier

#### Scenario: Artifact is created
- **WHEN** the run creates a generated artifact
- **THEN** the stream includes an artifact event identifying the artifact identifier and type

### Requirement: API errors are explicit and non-secret-bearing
The system MUST return explicit, structured errors without leaking secrets, provider keys, private environment values, raw internal prompts, or raw provider authorization data.

#### Scenario: Provider failure
- **WHEN** a model or search provider fails during a research run
- **THEN** the backend returns or streams a structured error that identifies the failing subsystem without exposing credentials or private configuration

#### Scenario: Streamed failure is replayable
- **WHEN** a streaming run fails after emitting earlier events
- **THEN** the failure event is available in the run event replay without exposing secret-bearing details
