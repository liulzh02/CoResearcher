## ADDED Requirements

### Requirement: Frontend app can run locally
The system SHALL provide a frontend application that developers can install, run, and build from the repository with documented scripts and a configurable backend base URL.

#### Scenario: Start local frontend
- **WHEN** a developer starts the frontend dev script with the backend base URL configured
- **THEN** the browser opens a research workbench that can attempt requests against the configured backend

#### Scenario: Build frontend
- **WHEN** a developer runs the frontend build check
- **THEN** the frontend compiles without TypeScript or bundling errors

### Requirement: Workbench shows backend connectivity
The frontend SHALL display backend connectivity status using the existing backend health endpoint.

#### Scenario: Backend is healthy
- **WHEN** the frontend receives a successful health response
- **THEN** the workbench shows the backend as connected with the reported version when available

#### Scenario: Backend is unavailable
- **WHEN** the health request fails
- **THEN** the workbench shows a non-blocking error state with the backend URL and allows retrying

### Requirement: Workbench supports research threads
The frontend SHALL allow users to create, list, select, and inspect research threads through the backend research thread APIs.

#### Scenario: Create thread
- **WHEN** a user submits an initial research question
- **THEN** the frontend creates a backend research thread and selects it in the workbench

#### Scenario: Select thread
- **WHEN** a user selects an existing research thread
- **THEN** the frontend displays that thread's messages and structured research state

### Requirement: Workbench runs research with streaming progress
The frontend SHALL allow users to submit a message to the selected thread and render streaming run events from the backend.

#### Scenario: Stream run progress
- **WHEN** a user starts a research run
- **THEN** the frontend displays progress events before the final response is complete

#### Scenario: Stream structured error
- **WHEN** the backend stream emits a structured error event
- **THEN** the frontend displays the error without exposing secrets or raw internal configuration

### Requirement: Workbench exposes research inspection panels
The frontend SHALL expose panels for inspecting the selected thread's evidence, artifacts, memory, tools, models, and subagents using available backend endpoints.

#### Scenario: Inspect evidence
- **WHEN** a user opens the evidence panel for a selected thread
- **THEN** the frontend shows evidence items and claims returned by the backend, or an empty state if none exist

#### Scenario: Inspect backend registries
- **WHEN** the workbench loads tool, model, and subagent registry data
- **THEN** the frontend displays the available backend capabilities in scannable lists

### Requirement: Workbench handles loading and empty states
The frontend SHALL render explicit loading, empty, and recoverable error states for all backend-backed workbench regions.

#### Scenario: No threads exist
- **WHEN** the thread list is empty
- **THEN** the frontend invites the user to create the first research thread without hiding the rest of the workbench shell

#### Scenario: Panel request fails
- **WHEN** a panel request fails
- **THEN** the frontend shows a localized panel error and keeps the rest of the workbench usable

### Requirement: Backend remains verifiable
The implementation SHALL verify that the existing backend still builds and passes the fastest relevant tests after adding the frontend.

#### Scenario: Backend verification passes
- **WHEN** implementation is complete
- **THEN** the recorded verification includes the backend test or build command and its successful result
