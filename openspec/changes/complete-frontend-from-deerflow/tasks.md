## 1. Frontend Scaffold

- [x] 1.1 Choose the frontend stack after checking the current repository constraints and document the choice in implementation notes.
- [x] 1.2 Create the repo-local frontend package with TypeScript, package scripts, lint/type/build scripts, and environment configuration for the backend base URL.
- [x] 1.3 Add a local development entry point that can run the frontend against the FastAPI backend without requiring provider secrets.

## 2. Backend Client Layer

- [x] 2.1 Implement typed frontend models for health, thread, message, state, run, registry, evidence, artifact, and memory responses based on the existing FastAPI schemas.
- [x] 2.2 Implement a backend API client for health, models, tools, subagents, thread create/list/get/messages/state, run, evidence, artifact, and memory endpoints.
- [x] 2.3 Implement a fetch-based SSE client for POSTing research run messages and parsing event names, data frames, final responses, and structured errors.
- [x] 2.4 Add focused tests for the API client and SSE parser, including multi-line data frames and `error.structured` events.

## 3. Research Workbench UI

- [x] 3.1 Build the first-screen workbench shell with thread navigation, run composer, message timeline, streaming progress, and status summary regions.
- [x] 3.2 Add backend connectivity status using `/health`, including connected, loading, retry, and unavailable states.
- [x] 3.3 Implement thread creation, thread list refresh, thread selection, message loading, and selected thread state rendering.
- [x] 3.4 Implement run submission for the selected thread and render streaming progress before final completion.
- [x] 3.5 Add inspection panels for evidence, artifacts, memory, tools, models, and subagents with loading, empty, and recoverable error states.
- [x] 3.6 Make the UI responsive for desktop and mobile without overlapping controls or text.

## 4. Backend Compatibility

- [x] 4.1 Run the backend tests before frontend integration and record the baseline result.
- [x] 4.2 Verify browser calls can reach the backend locally; if blocked, add the smallest CORS or dev-proxy compatibility fix.
- [x] 4.3 Add or update backend tests only for any backend compatibility behavior changed during implementation.

## 5. Verification

- [x] 5.1 Run the frontend install and fastest relevant lint/type/test/build checks.
- [x] 5.2 Run the backend build or test command after frontend integration.
- [x] 5.3 Start the backend and frontend locally and smoke-test health, thread creation, thread selection, and a streaming run.
- [x] 5.4 Update documentation with copy-pastable commands for starting the backend, starting the frontend, and running verification checks.
