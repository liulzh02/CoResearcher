from __future__ import annotations

import importlib
import os
from typing import Any

from coresearcher.models.settings import ModelConfig, ModelRegistryConfig


class FakeChatModel:
    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs

    async def ainvoke(self, messages: list[dict[str, str]] | str, **_: Any) -> str:
        if isinstance(messages, str):
            text = messages
        else:
            text = messages[-1]["content"] if messages else ""
        return f"Fake model response: {text[:200]}"


class ModelFactory:
    def __init__(self, config: ModelRegistryConfig | None = None) -> None:
        self.config = config or ModelRegistryConfig()

    def resolve_model_name(self, role: str | None = None, model_name: str | None = None) -> str:
        if model_name:
            return model_name
        if role and role in self.config.roles.role_overrides:
            return self.config.roles.role_overrides[role]
        return self.config.roles.default_model

    def get_config(self, role: str | None = None, model_name: str | None = None) -> ModelConfig:
        resolved = self.resolve_model_name(role=role, model_name=model_name)
        try:
            return self.config.models[resolved]
        except KeyError as exc:
            raise ValueError(f"Unknown model name: {resolved}") from exc

    def create(self, role: str | None = None, model_name: str | None = None) -> Any:
        config = self.get_config(role=role, model_name=model_name)
        missing = [name for name in config.secret_env_vars if not os.getenv(name)]
        if missing:
            raise RuntimeError(f"Missing required secret environment variables: {', '.join(missing)}")

        module_name, _, class_name = config.provider_class.rpartition(".")
        if not module_name:
            raise ValueError(f"Provider class must be a full import path: {config.provider_class}")
        module = importlib.import_module(module_name)
        provider_class = getattr(module, class_name)
        return provider_class(**config.default_parameters)

