"""VCR-style cassette recording/replay. A cassette is keyed by a hash of
(provider, model, messages, max_tokens) — the exact request shape — so the
same request always maps to the same file, and any change to the prompt
naturally invalidates the cassette rather than silently replaying a stale
response against a different question."""

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from promptcheck.providers import Provider, ProviderResponse


class MissingCassetteError(Exception):
    def __init__(self, cassette_key: str, cassette_path: Path):
        self.cassette_key = cassette_key
        self.cassette_path = cassette_path
        super().__init__(
            f"No cassette found for request {cassette_key} (expected at {cassette_path}). "
            "Run with mode='record' (or `promptcheck record`) to create it — this makes a "
            "real, billed API call. Replay mode never calls the API for an unrecorded request."
        )


def cassette_key(provider: str, model: str, messages: list[dict], max_tokens: int) -> str:
    payload = json.dumps(
        {"provider": provider, "model": model, "messages": messages, "max_tokens": max_tokens},
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


class CassetteProvider(Provider):
    """Wraps a real Provider. In "replay" mode (the default, used in tests
    and CI) it only ever reads from disk — it never calls the wrapped
    provider, so a test suite can never accidentally spend money. In
    "record" mode it calls the real provider and saves the response."""

    def __init__(self, wrapped: Provider, cassette_dir: Path, mode: str = "replay"):
        if mode not in ("replay", "record"):
            raise ValueError(f"mode must be 'replay' or 'record', got {mode!r}")
        self.wrapped = wrapped
        self.cassette_dir = Path(cassette_dir)
        self.mode = mode
        self.name = wrapped.name

    def _path_for(self, key: str) -> Path:
        return self.cassette_dir / f"{key}.json"

    def complete(self, model: str, messages: list[dict], max_tokens: int = 500) -> ProviderResponse:
        key = cassette_key(self.wrapped.name, model, messages, max_tokens)
        path = self._path_for(key)

        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return ProviderResponse(**data)

        if self.mode == "replay":
            raise MissingCassetteError(key, path)

        response = self.wrapped.complete(model, messages, max_tokens=max_tokens)
        self.cassette_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(asdict(response), indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return response
