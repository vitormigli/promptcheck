"""Assertion library. Each assertion is a pure function of
(response_text, provider_response, value) -> AssertionResult — no I/O, no
model calls, so the whole library is trivially unit-testable."""

import json
import re
from dataclasses import dataclass
from importlib import import_module

from promptcheck.providers import ProviderResponse


@dataclass
class AssertionResult:
    passed: bool
    message: str


def _contains(text: str, response: ProviderResponse, value: str) -> AssertionResult:
    passed = value in text
    return AssertionResult(passed, f"expected text to contain {value!r}")


def _icontains(text: str, response: ProviderResponse, value: str) -> AssertionResult:
    passed = value.lower() in text.lower()
    return AssertionResult(passed, f"expected text to contain {value!r} (case-insensitive)")


def _not_contains(text: str, response: ProviderResponse, value: str) -> AssertionResult:
    passed = value not in text
    return AssertionResult(passed, f"expected text to NOT contain {value!r}")


def _equals(text: str, response: ProviderResponse, value: str) -> AssertionResult:
    passed = text.strip() == value.strip()
    return AssertionResult(passed, f"expected text to equal {value!r}, got {text!r}")


def _regex(text: str, response: ProviderResponse, value: str) -> AssertionResult:
    passed = re.search(value, text) is not None
    return AssertionResult(passed, f"expected text to match regex {value!r}")


def _max_length(text: str, response: ProviderResponse, value: int) -> AssertionResult:
    passed = len(text) <= value
    return AssertionResult(passed, f"expected length <= {value}, got {len(text)}")


def _min_length(text: str, response: ProviderResponse, value: int) -> AssertionResult:
    passed = len(text) >= value
    return AssertionResult(passed, f"expected length >= {value}, got {len(text)}")


def _json_valid(text: str, response: ProviderResponse, value=None) -> AssertionResult:
    try:
        json.loads(text)
        return AssertionResult(True, "text is valid JSON")
    except json.JSONDecodeError as e:
        return AssertionResult(False, f"text is not valid JSON: {e}")


def _json_schema(text: str, response: ProviderResponse, value: dict) -> AssertionResult:
    import jsonschema

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        return AssertionResult(False, f"text is not valid JSON: {e}")
    try:
        jsonschema.validate(parsed, value)
        return AssertionResult(True, "JSON matches schema")
    except jsonschema.ValidationError as e:
        return AssertionResult(False, f"JSON schema violation: {e.message}")


def _latency_under(text: str, response: ProviderResponse, value: float) -> AssertionResult:
    passed = response.latency_seconds <= value
    return AssertionResult(
        passed, f"expected latency <= {value}s, got {response.latency_seconds:.2f}s"
    )


def _custom(text: str, response: ProviderResponse, value: str) -> AssertionResult:
    """`value` is "module.path:function_name" — the function receives
    (text, response) and returns True/False or an AssertionResult."""
    module_path, func_name = value.split(":")
    func = getattr(import_module(module_path), func_name)
    result = func(text, response)
    if isinstance(result, AssertionResult):
        return result
    return AssertionResult(bool(result), f"custom check {value} returned {result!r}")


ASSERTIONS = {
    "contains": _contains,
    "icontains": _icontains,
    "not_contains": _not_contains,
    "equals": _equals,
    "regex": _regex,
    "max_length": _max_length,
    "min_length": _min_length,
    "json_valid": _json_valid,
    "json_schema": _json_schema,
    "latency_under": _latency_under,
    "custom": _custom,
}


def run_assertion(
    assertion_type: str, text: str, response: ProviderResponse, value=None
) -> AssertionResult:
    try:
        fn = ASSERTIONS[assertion_type]
    except KeyError:
        raise ValueError(
            f"Unknown assertion type {assertion_type!r}. Known: {list(ASSERTIONS)}"
        ) from None
    return fn(text, response, value)
