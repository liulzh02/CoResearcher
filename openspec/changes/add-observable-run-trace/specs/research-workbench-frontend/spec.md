## MODIFIED Requirements

### Requirement: Workbench runs research with streaming progress
The frontend SHALL allow users to submit a message to the selected thread, render streamed assistant output incrementally, and render structured run progress as a user-readable Run Trace.

#### Scenario: Stream run progress
- **WHEN** a user starts a research run
- **THEN** the frontend displays structured progress steps before the final response is complete

#### Scenario: Stream assistant output
- **WHEN** the backend stream emits assistant response deltas
- **THEN** the frontend accumulates and displays the in-progress assistant response separately from process trace steps

#### Scenario: Stream structured error
- **WHEN** the backend stream emits a structured error event
- **THEN** the frontend displays the failed run status and safe error detail without exposing secrets or raw internal configuration

### Requirement: Workbench exposes research inspection panels
The frontend SHALL expose panels for inspecting the selected thread's run trace, raw events, evidence, artifacts, memory, tools, models, and subagents using available backend endpoints.

#### Scenario: Inspect run trace
- **WHEN** a user selects an active or completed run
- **THEN** the frontend shows a readable trace of run steps including status, phase, message, and timing when available

#### Scenario: Inspect raw events
- **WHEN** a developer opens the raw event inspection view
- **THEN** the frontend shows the underlying structured events for the run without making raw JSON the primary progress surface

#### Scenario: Inspect evidence
- **WHEN** a user opens the evidence panel for a selected thread
- **THEN** the frontend shows evidence items and claims returned by the backend, or an empty state if none exist

#### Scenario: Inspect backend registries
- **WHEN** the workbench loads tool, model, and subagent registry data
- **THEN** the frontend displays the available backend capabilities in scannable lists

### Requirement: Workbench handles loading and empty states
The frontend SHALL render explicit loading, running, completed, failed, empty, and recoverable error states for all backend-backed workbench regions.

#### Scenario: No threads exist
- **WHEN** the thread list is empty
- **THEN** the frontend invites the user to create the first research thread without hiding the rest of the workbench shell

#### Scenario: Run is active
- **WHEN** a research run is active
- **THEN** the frontend indicates the run is active and updates trace steps or assistant output as events arrive

#### Scenario: Panel request fails
- **WHEN** a panel request fails
- **THEN** the frontend shows a localized panel error and keeps the rest of the workbench usable
