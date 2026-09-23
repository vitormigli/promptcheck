from promptcheck.assertions import run_assertion
from promptcheck.providers import ProviderResponse

RESP = ProviderResponse(text="", input_tokens=1, output_tokens=1, latency_seconds=0.1)


def test_custom_assertion_calls_referenced_function():
    result = run_assertion("custom", "SHOUTING", RESP, "tests.custom_checks_fixture:is_uppercase")
    assert result.passed


def test_custom_assertion_fails_when_function_returns_false():
    result = run_assertion(
        "custom", "not shouting", RESP, "tests.custom_checks_fixture:is_uppercase"
    )
    assert not result.passed
