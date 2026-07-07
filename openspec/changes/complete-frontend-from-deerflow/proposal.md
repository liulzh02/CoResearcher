## Why

CoResearcher already has a FastAPI backend MVP for research threads, streaming runs, tools, memory, and artifacts, but it has no frontend workspace to exercise the end-to-end research loop. Adding a first frontend, informed by DeerFlow's gateway-plus-web architecture, will let users create threads, run research, inspect progress, and verify the backend build through a usable local flow.

## What Changes

- Add a frontend application scaffold for the CoResearcher research workbench.
- Provide a first-screen research workspace rather than a marketing page.
- Connect the frontend to existing backend endpoints for health checks, model/tool/subagent discovery, thread creation/listing, message display, run execution, SSE progress, evidence, artifacts, and memory inspection where available.
- Add developer scripts and configuration for local frontend/backend startup with a configurable backend base URL.
- Add frontend tests or smoke checks for the core workbench flow.
- Verify the existing backend build and tests remain green before implementation is considered complete.
- Keep the backend API contract stable unless a small compatibility endpoint is required to support the frontend.

## Capabilities

### New Capabilities
- `research-workbench-frontend`: Covers the browser-based research workbench, backend connectivity, research thread workflow, streaming run progress, state/evidence/artifact inspection, and local development verification.

### Modified Capabilities
None. The frontend will consume the existing backend streaming behavior without changing the backend capability contract in this change.

## Impact

- Affected frontend areas: new frontend package, UI components, API client, streaming client, local dev scripts, build/test configuration, and responsive workbench layout.
- Affected backend areas: primarily verification of the current FastAPI app and tests; any backend changes should be minimal and limited to frontend compatibility gaps discovered during implementation.
- Expected dependencies: a TypeScript frontend stack, likely Next.js or Vite/React depending on the simplest fit for this repository, plus lightweight UI/icon dependencies if needed.
- Verification: run the fastest relevant backend test/build checks, run frontend type/build checks, and manually smoke-test backend plus frontend startup.
- Security and quality considerations: no secrets in frontend code, no analytics or telemetry, backend URL configured through environment variables, structured error display without leaking private environment values.
