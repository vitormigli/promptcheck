"""Thin, uniform interface over real provider SDKs. Every provider takes
messages in OpenAI's {"role", "content"} shape and returns a ProviderResponse
— this is the seam CassetteProvider wraps, so cassette logic never needs to
know which vendor answered."""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ProviderResponse:
    text: str
    input_tokens: int
    output_tokens: int
    latency_seconds: float


class Provider(ABC):
    name: str

    @abstractmethod
    def complete(
        self, model: str, messages: list[dict], max_tokens: int = 500
    ) -> ProviderResponse: ...


class OpenAIProvider(Provider):
    name = "openai"

    def __init__(self, client=None):
        self._client = client

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI()
        return self._client

    def complete(self, model: str, messages: list[dict], max_tokens: int = 500) -> ProviderResponse:
        client = self._get_client()
        start = time.monotonic()
        response = client.chat.completions.create(
            model=model, messages=messages, max_tokens=max_tokens
        )
        latency = time.monotonic() - start
        return ProviderResponse(
            text=response.choices[0].message.content or "",
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            latency_seconds=latency,
        )


class AnthropicProvider(Provider):
    name = "anthropic"

    def __init__(self, client=None):
        self._client = client

    def _get_client(self):
        if self._client is None:
            from anthropic import Anthropic

            self._client = Anthropic()
        return self._client

    def complete(self, model: str, messages: list[dict], max_tokens: int = 500) -> ProviderResponse:
        client = self._get_client()
        system = "\n".join(m["content"] for m in messages if m["role"] == "system") or None
        chat_messages = [m for m in messages if m["role"] != "system"]
        start = time.monotonic()
        kwargs = {"model": model, "max_tokens": max_tokens, "messages": chat_messages}
        if system:
            kwargs["system"] = system
        response = client.messages.create(**kwargs)
        latency = time.monotonic() - start
        text = "".join(b.text for b in response.content if b.type == "text")
        return ProviderResponse(
            text=text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            latency_seconds=latency,
        )


PROVIDERS: dict[str, type[Provider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
}


def get_provider(name: str) -> Provider:
    try:
        return PROVIDERS[name]()
    except KeyError:
        raise ValueError(f"Unknown provider {name!r}. Known: {list(PROVIDERS)}") from None
