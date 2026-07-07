## Why

CoResearcher currently exposes only a deterministic `fake` model even when users want to configure a real LLM provider. Users need a clear, safe model configuration path so the workbench can distinguish "local fake runtime" from "real model ready" before launching research.

## What Changes

- Add model registry configuration to application settings and YAML config loading.
- Add an OpenAI-compatible chat model provider that reads API keys from environment variables only.
- Make `/models` return configured model metadata and readiness status without exposing secrets.
- Make research execution fail clearly when the selected model requires missing secrets.
- Update frontend runtime status to use backend model readiness rather than only checking for non-`fake` names.
- Document where to put local model config and where to put API keys.
- Keep the default fake model so tests and local smoke checks can still run without credentials.

## Capabilities

### New Capabilities
- `configurable-model-provider`: Covers app-level model registry configuration, provider secret validation, model readiness reporting, and frontend model readiness behavior.

### Modified Capabilities
None. This introduces a new configuration capability and leaves existing fake-runtime behavior available by default.

## Impact

- Affected backend areas: `AppSettings`, config loading, model factory/provider layer, `/models` API, research service model readiness checks, tests, and example config.
- Affected frontend areas: model runtime status parsing and launch gating.
- Expected dependencies: `httpx` is already available and can be reused for OpenAI-compatible HTTP calls; no new secret files should be introduced.
- Security considerations: API keys MUST remain in environment variables and MUST NOT be returned by APIs, logged, or committed to config files.
