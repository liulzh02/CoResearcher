import os

import pytest

from coresearcher.config import load_settings
from coresearcher.models import FakeChatModel, ModelFactory
from coresearcher.models.settings import ModelConfig, ModelRegistryConfig, RoleModelConfig


def test_model_factory_resolves_role_override():
    config = ModelRegistryConfig(
        models={
            "fake": ModelConfig(name="fake"),
            "critic": ModelConfig(name="critic"),
        },
        roles=RoleModelConfig(default_model="fake", role_overrides={"critic": "critic"}),
    )
    factory = ModelFactory(config)
    assert factory.resolve_model_name(role="critic") == "critic"
    assert isinstance(factory.create(role="critic"), FakeChatModel)


def test_model_factory_rejects_missing_model_name():
    factory = ModelFactory()
    with pytest.raises(ValueError, match="Unknown model name"):
        factory.create(model_name="missing")


def test_model_factory_rejects_invalid_provider_class():
    config = ModelRegistryConfig(
        models={"bad": ModelConfig(name="bad", provider_class="NoDotPath")},
        roles=RoleModelConfig(default_model="bad"),
    )
    with pytest.raises(ValueError, match="full import path"):
        ModelFactory(config).create()


def test_model_factory_reports_missing_secret_without_value(monkeypatch):
    monkeypatch.delenv("CORESEARCHER_TEST_SECRET", raising=False)
    config = ModelRegistryConfig(
        models={
            "secret": ModelConfig(
                name="secret",
                secret_env_vars=["CORESEARCHER_TEST_SECRET"],
            )
        },
        roles=RoleModelConfig(default_model="secret"),
    )
    with pytest.raises(RuntimeError) as exc:
        ModelFactory(config).create()
    assert "CORESEARCHER_TEST_SECRET" in str(exc.value)
    assert "secret-value" not in str(exc.value)


def test_app_settings_loads_model_registry_from_yaml(tmp_path, monkeypatch):
    config_path = tmp_path / "coresearcher.yaml"
    config_path.write_text(
        """
models:
  models:
    researcher:
      name: researcher
      provider_class: coresearcher.models.factory.FakeChatModel
      display_name: Researcher
      secret_env_vars:
        - CORESEARCHER_TEST_MODEL_KEY
  roles:
    default_model: researcher
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("CORESEARCHER_CONFIG", str(config_path))

    settings = load_settings()

    assert settings.models.roles.default_model == "researcher"
    assert settings.models.models["researcher"].secret_env_vars == ["CORESEARCHER_TEST_MODEL_KEY"]


def test_load_settings_imports_dotenv_without_overriding_shell_env(tmp_path, monkeypatch):
    config_path = tmp_path / "coresearcher.yaml"
    config_path.write_text(
        """
models:
  models:
    researcher:
      name: researcher
      provider_class: coresearcher.models.factory.FakeChatModel
      secret_env_vars:
        - CORESEARCHER_TEST_MODEL_KEY
  roles:
    default_model: researcher
""",
        encoding="utf-8",
    )
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text(
        "\n".join(
            [
                f"CORESEARCHER_CONFIG={config_path}",
                "CORESEARCHER_TEST_MODEL_KEY=from-dotenv",
                "CORESEARCHER_EXISTING_VALUE=from-dotenv",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CORESEARCHER_CONFIG", raising=False)
    monkeypatch.delenv("CORESEARCHER_TEST_MODEL_KEY", raising=False)
    monkeypatch.setenv("CORESEARCHER_EXISTING_VALUE", "from-shell")

    try:
        settings = load_settings()

        assert settings.models.roles.default_model == "researcher"
        assert settings.models.models["researcher"].missing_secret_env_vars() == []
        assert os.getenv("CORESEARCHER_EXISTING_VALUE") == "from-shell"
    finally:
        os.environ.pop("CORESEARCHER_CONFIG", None)
        os.environ.pop("CORESEARCHER_TEST_MODEL_KEY", None)


def test_model_factory_reports_readiness_without_secret_values(monkeypatch):
    monkeypatch.delenv("CORESEARCHER_TEST_MODEL_KEY", raising=False)
    config = ModelRegistryConfig(
        models={
            "researcher": ModelConfig(
                name="researcher",
                secret_env_vars=["CORESEARCHER_TEST_MODEL_KEY"],
            )
        },
        roles=RoleModelConfig(default_model="researcher"),
    )

    status = ModelFactory(config).list_model_status()

    assert status["default_model"] == "researcher"
    assert status["models"][0]["id"] == "researcher"
    assert status["models"][0]["ready"] is False
    assert status["models"][0]["missing_secret_env_vars"] == ["CORESEARCHER_TEST_MODEL_KEY"]
    assert "secret-value" not in str(status)


@pytest.mark.asyncio
async def test_openai_compatible_chat_model_uses_env_secret_and_configured_endpoint(monkeypatch):
    from coresearcher.models.openai_compatible import OpenAICompatibleChatModel

    requests = []

    async def handler(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "provider response"}}]},
        )

    import httpx

    monkeypatch.setenv("CORESEARCHER_TEST_MODEL_KEY", "secret-value")
    transport = httpx.MockTransport(handler)
    model = OpenAICompatibleChatModel(
        model="demo-model",
        api_key_env="CORESEARCHER_TEST_MODEL_KEY",
        base_url="https://models.example.test/v1",
        transport=transport,
    )

    response = await model.ainvoke([{"role": "user", "content": "hello"}])

    assert response == "provider response"
    assert requests[0].url == "https://models.example.test/v1/chat/completions"
    assert requests[0].headers["authorization"] == "Bearer secret-value"


@pytest.mark.asyncio
async def test_openai_compatible_chat_model_streams_content_deltas(monkeypatch):
    from coresearcher.models.openai_compatible import OpenAICompatibleChatModel

    requests = []

    async def handler(request):
        requests.append(request)
        return httpx.Response(
            200,
            content=(
                'data: {"choices":[{"delta":{"content":"Hel"}}]}\n\n'
                'data: {"choices":[{"delta":{"content":"lo"}}]}\n\n'
                "data: [DONE]\n\n"
            ),
            headers={"content-type": "text/event-stream"},
        )

    import httpx

    monkeypatch.setenv("CORESEARCHER_TEST_MODEL_KEY", "secret-value")
    model = OpenAICompatibleChatModel(
        model="demo-model",
        api_key_env="CORESEARCHER_TEST_MODEL_KEY",
        base_url="https://models.example.test/v1",
        transport=httpx.MockTransport(handler),
    )

    chunks = [chunk async for chunk in model.astream("hello")]

    assert chunks == ["Hel", "lo"]
    assert requests[0].url == "https://models.example.test/v1/chat/completions"
    assert requests[0].headers["authorization"] == "Bearer secret-value"
    assert b'"stream":true' in requests[0].content
