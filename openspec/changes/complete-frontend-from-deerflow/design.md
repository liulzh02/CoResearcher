## Context

CoResearcher currently exposes a Python/FastAPI backend with research thread APIs, streaming run events, tool and subagent registries, memory endpoints, and artifact retrieval. The repository has no frontend package, so developers cannot easily run the product loop end to end or inspect backend state through a browser.

DeerFlow is a useful reference at the architectural level: keep a clear separation between the Python gateway/backend and a browser frontend, expose a local development flow that starts both pieces, and make the first screen an operator workspace for long-running research instead of a static landing page. This change should adapt that shape to CoResearcher's existing backend rather than cloning DeerFlow code.

## Goals / Non-Goals

**Goals:**
- Add a frontend app that can be developed and built from this repository.
- Provide a research workbench with thread creation, thread selection, messages, run input, streaming progress, and inspection panels for state, evidence, artifacts, memory, tools, models, and subagents.
- Use a typed API client around the existing FastAPI endpoints and a dedicated streaming client for `text/event-stream` responses.
- Make backend connectivity visible through health/status UI so local setup failures are obvious.
- Add the minimal scripts and checks needed to build the frontend and verify the backend still passes its fastest relevant checks.

**Non-Goals:**
- Rebuild the backend orchestration or memory architecture.
- Add production authentication, multi-tenant authorization, deployment infrastructure, telemetry, or analytics.
- Require provider secrets to run the frontend shell.
- Match DeerFlow's UI pixel-for-pixel or import DeerFlow source code.

## Decisions

1. Use a repo-local frontend package with TypeScript.

   Rationale: The backend is already Python-only, so a separate `frontend/` package keeps dependency boundaries clear and mirrors the backend-plus-web shape used by DeerFlow. TypeScript gives a safer contract for the existing Pydantic-shaped JSON responses.

   Alternatives considered: Server-rendering all UI from FastAPI would reduce toolchain size but make interactive streaming and state inspection awkward. A monolithic Python UI framework would be faster to prototype but would not fit the long-term web workspace direction.

2. Prefer a lightweight app shell over a marketing page.

   Rationale: The immediate milestone is to run the CoResearcher flow, not explain the product. The default route should show a usable workbench with dense, scannable research state and controls.

   Alternatives considered: A landing page plus a separate app route would add polish but slows down the first useful loop.

3. Keep backend compatibility changes minimal.

   Rationale: Existing endpoints already cover health, models, tools, subagents, research threads, messages, runs, SSE, evidence, artifacts, and memory. The frontend should adapt to those contracts first. Any backend changes should be limited to gaps discovered during implementation and covered by tests.

   Alternatives considered: Introduce a frontend-specific aggregation endpoint. That could reduce client requests, but it would expand backend scope before the basic loop is proven.

4. Implement streaming with fetch-based SSE parsing.

   Rationale: The backend stream endpoint uses POST with a JSON body, which browser `EventSource` cannot send directly. A fetch reader can POST the message, parse SSE frames, and preserve the existing API.

   Alternatives considered: Change the backend to GET-based `EventSource`; this would be simpler in the browser but would alter the backend API contract unnecessarily.

5. Use environment-based backend configuration.

   Rationale: Local development needs to point the frontend at the FastAPI server without hard-coding ports or secrets. A public frontend variable for the base URL is sufficient and must not contain credentials.

   Alternatives considered: Proxy every API call through a frontend server route. That adds indirection and is unnecessary for the first local workflow unless CORS or deployment constraints appear during implementation.

## Risks / Trade-offs

- Backend CORS or browser fetch restrictions block local API calls -> Add a narrowly scoped backend CORS configuration or frontend dev proxy, with tests or documented smoke checks.
- SSE parsing misses multi-line data frames or structured errors -> Implement a small tested parser that handles event names, data lines, blank-frame delimiters, and `error.structured` events.
- New frontend dependencies make the repo heavier -> Keep dependency choices minimal and avoid broad UI frameworks unless the implementation clearly benefits.
- Backend tests are already failing for unrelated reasons -> Record exact failures and keep frontend work isolated; do not mask backend regressions.
- UI overfits current sample data -> Render empty states and error states for every panel so the app remains useful before real provider integrations are configured.

## Migration Plan

1. Add the frontend package and local configuration.
2. Implement the typed API and streaming clients against existing backend endpoints.
3. Build the workbench UI around the current research thread and run lifecycle.
4. Add frontend checks and run the backend test/build verification.
5. Start backend and frontend locally and smoke-test thread creation plus a streaming run.

Rollback is straightforward because the change is additive: remove the frontend package and any minimal backend compatibility edits introduced during implementation.

## Open Questions

- Which frontend stack should be selected during implementation: Next.js for parity with DeerFlow's web shape, or Vite/React for a smaller local workbench footprint?
- Does the existing FastAPI app need CORS configuration for local browser development, or can the chosen frontend dev server proxy API calls cleanly?
- Should generated artifacts be listed from thread state first, or only fetched when the backend exposes known artifact identifiers?
