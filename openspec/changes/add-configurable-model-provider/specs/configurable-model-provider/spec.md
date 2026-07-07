## ADDED Requirements

### Requirement: Application loads model registry configuration
The system SHALL load model registry configuration from application YAML through `AppSettings` while retaining the fake model as the default when no model config is provided.

#### Scenario: Default fake model remains available
- **WHEN** the application starts without a `models` config section
- **THEN** the model registry contains the fake local test model

#### Scenario: YAML model config is loaded
- **WHEN** `CORESEARCHER_CONFIG` points to a YAML file with a `models` section
- **THEN** the application uses the configured model registry and role defaults

### Requirement: Model secrets are environment-referenced
The system MUST reference model secrets by environment variable name and MUST NOT require or expose inline API key values in YAML, code, or API responses.

#### Scenario: Missing model secret
- **WHEN** a configured model declares a required secret environment variable that is not set
- **THEN** model readiness reports the missing environment variable name without exposing any secret value

#### Scenario: Present model secret
- **WHEN** all required secret environment variables for a configured model are set
- **THEN** model readiness reports that the model is ready without returning the secret values

### Requirement: Backend exposes model readiness
The system SHALL expose configured model metadata and readiness through the existing `/models` API.

#### Scenario: Frontend requests models
- **WHEN** a client requests `/models`
- **THEN** the response includes model metadata, readiness state, missing secret env var names, and the default model name

### Requirement: OpenAI-compatible provider can be configured
The system SHALL provide an OpenAI-compatible chat model provider that can be configured through model default parameters and environment-sourced API keys.

#### Scenario: Provider invokes chat completions
- **WHEN** the OpenAI-compatible provider is created with a valid API key environment variable and invoked with messages
- **THEN** it sends a chat completions request to the configured base URL and returns the assistant content

### Requirement: Research execution blocks when default model is not ready
The system SHALL return or stream a structured model configuration error before research execution when the configured default model is not ready.

#### Scenario: Default model missing API key
- **WHEN** a user starts a research run and the default model requires a missing API key environment variable
- **THEN** the backend reports a structured configuration error instead of returning fake research output

### Requirement: Frontend uses backend readiness for run gating
The frontend SHALL enable or disable research runs based on backend model readiness fields rather than only model names.

#### Scenario: Backend reports missing secret
- **WHEN** `/models` reports that the default model is not ready because a secret env var is missing
- **THEN** the frontend disables Run and displays the missing configuration guidance

#### Scenario: Backend reports ready model
- **WHEN** `/models` reports that the default model is ready
- **THEN** the frontend enables Run for a selected research thread
