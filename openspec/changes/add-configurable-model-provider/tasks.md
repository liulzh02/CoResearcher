## 1. Backend Model Configuration

- [x] 1.1 Add model registry configuration to application settings and YAML loading.
- [x] 1.2 Add model readiness helpers that report missing secret env var names without exposing values.
- [x] 1.3 Update `/models` to return configured models, readiness, missing secrets, and default model name.
- [x] 1.4 Add backend tests for default fake config, YAML model config loading, and `/models` readiness output.

## 2. Provider Runtime

- [x] 2.1 Add an OpenAI-compatible chat provider that uses env-sourced API keys and configurable base URL/model parameters.
- [x] 2.2 Add provider tests using mocked HTTP transport without live network calls or real secrets.
- [x] 2.3 Guard research execution when the configured default model is not ready.
- [x] 2.4 Add backend tests for missing-secret research run and streaming structured error behavior.

## 3. Frontend Runtime Status

- [x] 3.1 Update frontend model response types to include backend readiness fields.
- [x] 3.2 Update frontend runtime gating to use backend readiness for the default model.
- [x] 3.3 Add frontend tests for missing-secret and ready-model gating.

## 4. Documentation and Examples

- [x] 4.1 Update example config with a commented real-model configuration shape.
- [x] 4.2 Document local config and API key environment variable setup without including secret values.

## 5. Verification

- [x] 5.1 Run backend tests.
- [x] 5.2 Run frontend lint, tests, and build.
- [x] 5.3 Confirm OpenSpec apply progress is complete.
