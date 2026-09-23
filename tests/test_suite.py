import pytest

from promptcheck.suite import load_suite


def _write(tmp_path, content):
    path = tmp_path / "suite.yaml"
    path.write_text(content, encoding="utf-8")
    return path


def test_load_suite_parses_cases_and_asserts(tmp_path):
    path = _write(
        tmp_path,
        """
- id: greet
  provider: openai
  model: gpt-4o-mini
  messages:
    - role: user
      content: "hi"
  asserts:
    - type: contains
      value: "hello"
""",
    )
    cases = load_suite(path)
    assert len(cases) == 1
    assert cases[0].id == "greet"
    assert cases[0].asserts[0].type == "contains"
    assert cases[0].asserts[0].value == "hello"


def test_load_suite_missing_id_raises(tmp_path):
    path = _write(
        tmp_path,
        """
- provider: openai
  model: gpt-4o-mini
  messages: []
""",
    )
    with pytest.raises(ValueError, match="missing required 'id'"):
        load_suite(path)


def test_load_suite_duplicate_id_raises(tmp_path):
    path = _write(
        tmp_path,
        """
- id: dup
  provider: openai
  model: gpt-4o-mini
  messages: []
- id: dup
  provider: openai
  model: gpt-4o-mini
  messages: []
""",
    )
    with pytest.raises(ValueError, match="Duplicate test id"):
        load_suite(path)


def test_load_suite_defaults_max_tokens_and_description(tmp_path):
    path = _write(
        tmp_path,
        """
- id: minimal
  provider: openai
  model: gpt-4o-mini
  messages: []
""",
    )
    cases = load_suite(path)
    assert cases[0].max_tokens == 500
    assert cases[0].description == ""
