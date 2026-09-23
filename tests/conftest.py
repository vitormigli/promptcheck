"""A fake provider that returns a fixed or scripted response, with no
network calls — used across the test suite."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from promptcheck.providers import Provider, ProviderResponse  # noqa: E402


class FakeProvider(Provider):
    name = "fake"

    def __init__(self, text: str = "hello world", latency: float = 0.01):
        self.text = text
        self.latency = latency
        self.call_count = 0

    def complete(self, model: str, messages: list[dict], max_tokens: int = 500) -> ProviderResponse:
        self.call_count += 1
        return ProviderResponse(
            text=self.text, input_tokens=10, output_tokens=5, latency_seconds=self.latency
        )


@pytest.fixture
def fake_provider():
    return FakeProvider()
