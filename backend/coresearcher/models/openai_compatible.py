from __future__ import annotations

import os
import json
from typing import Any

import httpx


class OpenAICompatibleChatModel:
    def __init__(
        self,
        *,
        model: str,
        api_key_env: str,
        base_url: str = "https://api.openai.com/v1",
        temperature: float | None = None,
        timeout: float = 60.0,
        transport: httpx.AsyncBaseTransport | None = None,
        **extra_parameters: Any,
    ) -> None:
        self.model = model
        self.api_key_env = api_key_env
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.timeout = timeout
        self.transport = transport
        self.extra_parameters = extra_parameters

    async def ainvoke(self, messages: list[dict[str, str]] | str, **_: Any) -> str:
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing required secret environment variable: {self.api_key_env}")

        normalized_messages = (
            [{"role": "user", "content": messages}] if isinstance(messages, str) else messages
        )
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": normalized_messages,
            **self.extra_parameters,
        }
        if self.temperature is not None:
            payload["temperature"] = self.temperature

        async with httpx.AsyncClient(timeout=self.timeout, transport=self.transport) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"authorization": f"Bearer {api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return str(data["choices"][0]["message"]["content"])

    async def astream(self, messages: list[dict[str, str]] | str, **_: Any):
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing required secret environment variable: {self.api_key_env}")

        normalized_messages = (
            [{"role": "user", "content": messages}] if isinstance(messages, str) else messages
        )
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": normalized_messages,
            "stream": True,
            **self.extra_parameters,
        }
        if self.temperature is not None:
            payload["temperature"] = self.temperature

        async with httpx.AsyncClient(timeout=self.timeout, transport=self.transport) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={"authorization": f"Bearer {api_key}"},
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line.removeprefix("data:").strip()
                    if not data or data == "[DONE]":
                        continue
                    chunk = json.loads(data)
                    choices = chunk.get("choices") or []
                    if not choices:
                        continue
                    content = choices[0].get("delta", {}).get("content")
                    if content:
                        yield str(content)
