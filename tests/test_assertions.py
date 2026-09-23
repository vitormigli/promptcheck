from promptcheck.assertions import run_assertion
from promptcheck.providers import ProviderResponse

RESP = ProviderResponse(text="", input_tokens=1, output_tokens=1, latency_seconds=0.5)


def test_contains_pass():
    assert run_assertion("contains", "Hello World", RESP, "World").passed


def test_contains_fail():
    assert not run_assertion("contains", "Hello World", RESP, "Bye").passed


def test_icontains_case_insensitive():
    assert run_assertion("icontains", "Hello World", RESP, "world").passed


def test_not_contains():
    assert run_assertion("not_contains", "Hello World", RESP, "Bye").passed
    assert not run_assertion("not_contains", "Hello World", RESP, "World").passed


def test_equals():
    assert run_assertion("equals", "exact", RESP, "exact").passed
    assert run_assertion("equals", "  exact  ", RESP, "exact").passed  # trims whitespace
    assert not run_assertion("equals", "exact", RESP, "different").passed


def test_regex():
    assert run_assertion("regex", "order #12345", RESP, r"#\d+").passed
    assert not run_assertion("regex", "no numbers here", RESP, r"#\d+").passed


def test_max_length():
    assert run_assertion("max_length", "short", RESP, 10).passed
    assert not run_assertion("max_length", "this is a long string", RESP, 10).passed


def test_min_length():
    assert run_assertion("min_length", "long enough", RESP, 5).passed
    assert not run_assertion("min_length", "hi", RESP, 5).passed


def test_json_valid():
    assert run_assertion("json_valid", '{"a": 1}', RESP).passed
    assert not run_assertion("json_valid", "not json", RESP).passed


def test_json_schema_pass():
    schema = {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}
    assert run_assertion("json_schema", '{"name": "Ana"}', RESP, schema).passed


def test_json_schema_fail_missing_required():
    schema = {"type": "object", "required": ["name"]}
    assert not run_assertion("json_schema", "{}", RESP, schema).passed


def test_json_schema_fail_invalid_json():
    schema = {"type": "object"}
    assert not run_assertion("json_schema", "not json", RESP, schema).passed


def test_latency_under():
    fast = ProviderResponse(text="", input_tokens=1, output_tokens=1, latency_seconds=0.1)
    slow = ProviderResponse(text="", input_tokens=1, output_tokens=1, latency_seconds=5.0)
    assert run_assertion("latency_under", "", fast, 1.0).passed
    assert not run_assertion("latency_under", "", slow, 1.0).passed


def test_unknown_assertion_type_raises():
    import pytest

    with pytest.raises(ValueError):
        run_assertion("not_a_real_type", "text", RESP)
