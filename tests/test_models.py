import pytest

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

