## Context

The backend already has `ModelConfig`, `ModelRegistryConfig`, and `ModelFactory`, but application settings do not load model registry configuration from YAML. The gateway currently creates `ModelFactory()` with defaults, so `/models` always reports the fake local test model. The research director is also deterministic and does not call a real model provider yet.

The frontend correctly blocks research runs when only fake models are available, but it needs backend readiness data to tell users whether real model configuration and required API key environment variables are present.

## Goals / Non-Goals

**Goals:**
- Load model registry configuration from `CORESEARCHER_CONFIG` YAML through `AppSettings`.
- Keep fake model as the default local/test behavior.
- Add an OpenAI-compatible chat provider wrapper using `httpx` and environment-sourced secrets.
- Return model readiness metadata from `/models` without exposing secret values.
- Block research execution when the selected default model is not ready because required secret env vars are missing.
- Update the frontend to use backend readiness fields when deciding whether Run is enabled.
- Document a local config file shape and env-var setup commands.

**Non-Goals:**
- Store API keys in YAML or source code.
- Implement full agentic LLM reasoning in the research director.
- Add OAuth, hosted secret management, multi-provider UI forms, or production deployment settings.
- Replace deterministic fake tests with live provider calls.

## Decisions

1. Extend `AppSettings` with `models: ModelRegistryConfig`.

   Rationale: The repository already has strongly typed model registry classes. Adding them to app settings lets `load_settings()` parse YAML consistently with existing config sections.

   Alternative considered: Read a separate model config file directly in `ModelFactory`. That would bypass the existing config path and make gateway/runtime behavior harder to reason about.

2. Report readiness separately from model metadata.

   Rationale: `/models` should tell the frontend whether each model can be used without exposing secret values. A model is ready when all required `secret_env_vars` are present, or when it requires no secrets.

   Alternative considered: Have the frontend infer readiness from model names. That already proved misleading because `fake` is valid for tests but not real research.

3. Add OpenAI-compatible provider as a small HTTP wrapper.

   Rationale: `httpx` is already a project dependency, and an OpenAI-compatible `/chat/completions` wrapper supports OpenAI and compatible endpoints without adding a new SDK dependency. The wrapper only needs enough behavior for backend integration and tests.

   Alternative considered: Add the official OpenAI SDK. That may be useful later, but it expands dependencies before the project needs advanced SDK features.

4. Validate readiness before research execution.

   Rationale: Users should get an explicit model configuration error instead of seeing fake-looking output or late provider failures. The first check can guard the configured default model before invoking the deterministic graph.

   Alternative considered: Let provider creation fail inside a future model call. That is less clear and does not help the current frontend gating flow.

## Risks / Trade-offs

- [Risk] `/models` shape changes could break the frontend -> Keep `models` as an array and add fields rather than replacing existing fields.
- [Risk] Users may expect real reasoning immediately after model config -> Clearly document that this change enables configuration/readiness and provider creation, while full director LLM reasoning remains a later capability.
- [Risk] Secret names could leak operational details -> Return missing env var names because users need actionable setup, but never return secret values.
- [Risk] OpenAI-compatible endpoints vary -> Keep provider parameters configurable for `base_url`, `model`, `temperature`, and compatible payload fields.

## Migration Plan

1. Add model registry to app settings and example config.
2. Add readiness helpers and `/models` readiness response.
3. Add OpenAI-compatible provider wrapper and tests with mocked HTTP transport.
4. Guard research execution when the default configured model is not ready.
5. Update frontend runtime gating and docs.

Rollback is additive: remove the config section and provider wrapper, and the app returns to fake-only defaults.

## Open Questions

- Which real provider/model should the user configure first in local config: OpenAI, another OpenAI-compatible endpoint, or both examples?
- When a future change makes the director actually call the model, should model selection be per role, per thread, or global default only?
