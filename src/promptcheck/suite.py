"""Loads a declarative YAML test suite into TestCase objects."""

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Assertion:
    type: str
    value: object = None


@dataclass
class TestCase:
    __test__ = False  # not a pytest test class, just named similarly

    id: str
    provider: str
    model: str
    messages: list[dict]
    asserts: list[Assertion]
    max_tokens: int = 500
    description: str = ""


def load_suite(path: Path) -> list[TestCase]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or []
    cases = []
    seen_ids: set[str] = set()
    for entry in raw:
        if "id" not in entry:
            raise ValueError(f"Test case missing required 'id' field: {entry}")
        if entry["id"] in seen_ids:
            raise ValueError(f"Duplicate test id {entry['id']!r} in {path}")
        seen_ids.add(entry["id"])

        asserts = [Assertion(**a) for a in entry.get("asserts", [])]
        cases.append(
            TestCase(
                id=entry["id"],
                provider=entry["provider"],
                model=entry["model"],
                messages=entry["messages"],
                asserts=asserts,
                max_tokens=entry.get("max_tokens", 500),
                description=entry.get("description", ""),
            )
        )
    return cases


def load_suites(paths: list[Path]) -> list[TestCase]:
    cases: list[TestCase] = []
    for path in paths:
        cases.extend(load_suite(path))
    return cases
