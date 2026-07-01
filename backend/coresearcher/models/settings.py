from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    name: str
    provider_class: str = "coresearcher.models.factory.FakeChatModel"
    display_name: str | None = None
    supports_streaming: bool = False
    supports_tool_calling: bool = False
    supports_vision: bool = False
    supports_long_context: bool = False
    supports_thinking: bool = False
    supports_structured_output: bool = False
    default_parameters: dict[str, Any] = Field(default_factory=dict)
    secret_env_vars: list[str] = Field(default_factory=list)


class RoleModelConfig(BaseModel):
    default_model: str = "fake"
    role_overrides: dict[str, str] = Field(default_factory=dict)


class ModelRegistryConfig(BaseModel):
    models: dict[str, ModelConfig] = Field(
        default_factory=lambda: {
            "fake": ModelConfig(
                name="fake",
                display_name="Fake local test model",
                supports_streaming=True,
                supports_tool_calling=True,
                supports_structured_output=True,
            )
        }
    )
    roles: RoleModelConfig = Field(default_factory=RoleModelConfig)

