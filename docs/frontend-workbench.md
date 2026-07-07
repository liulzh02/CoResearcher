# CoResearcher Frontend Workbench

## Stack choice

The frontend uses Vite, React, and TypeScript.

This project currently has a Python/FastAPI backend and no frontend package. Vite keeps the first workbench lightweight, fast to build, and easy to run against the existing POST-based streaming endpoint. The app follows DeerFlow's broad backend-plus-web shape without copying DeerFlow source code.

## Local commands

The backend starts with the deterministic `fake` model. That lets the UI and API flow run without secrets, but it is not a real LLM-backed research run. The frontend shows `Model not configured` and disables launching research until the backend default model is a ready non-`fake` model.

Create a local config file for real model settings:

```powershell
Copy-Item configs/coresearcher.example.yaml configs/coresearcher.local.yaml
```

In `configs/coresearcher.local.yaml`, uncomment or add a model under `models.models`, set `models.roles.default_model` to that model name, and keep API key values out of the file. The YAML should reference environment variable names only:

```yaml
models:
  models:
    gpt-4o-mini:
      name: gpt-4o-mini
      display_name: GPT-4o mini
      provider_class: coresearcher.models.openai_compatible.OpenAICompatibleChatModel
      supports_streaming: true
      supports_tool_calling: true
      supports_structured_output: true
      secret_env_vars:
        - OPENAI_API_KEY
      default_parameters:
        model: gpt-4o-mini
        api_key_env: OPENAI_API_KEY
        base_url: https://api.openai.com/v1
  roles:
    default_model: gpt-4o-mini
```

The backend loads `.env` from the project root on startup without overriding variables already set in the shell. Put secret values in `.env` or set them in the shell, but do not commit them.

If you want to keep using the edited example config directly, add this non-secret line to `.env`:

```text
CORESEARCHER_CONFIG=configs/coresearcher.example.yaml
```

Or set the config path in the shell before starting the backend:

```powershell
$env:CORESEARCHER_CONFIG = "configs/coresearcher.local.yaml"
$env:OPENAI_API_KEY = "your-api-key"
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

Start the backend:

```bash
python -m uvicorn coresearcher.gateway.app:create_app --factory --host 127.0.0.1 --port 8000
```

Start the frontend:

```bash
cd frontend
npm run dev
```

By default, the Vite dev server proxies `/api` to `http://127.0.0.1:8000`. To point the frontend directly at another backend:

```bash
cd frontend
$env:VITE_CORESEARCHER_API_URL = "http://127.0.0.1:8000"
npm run dev
```

## Verification

Backend:

```bash
python -m pytest
```

Frontend:

```bash
cd frontend
npm test
npm run build
```

Smoke-test flow:

1. Open the frontend dev URL.
2. Confirm the backend status shows connected.
3. Create a new research thread.
4. Select the thread.
5. Submit a run message and confirm streaming events appear before the final thread refresh.
