from promptcheck.runner import run_case
from promptcheck.suite import Assertion, TestCase


def _case(**overrides):
    defaults = dict(
        id="t1",
        provider="fake",
        model="model-x",
        messages=[{"role": "user", "content": "hi"}],
        asserts=[Assertion(type="contains", value="hello")],
    )
    defaults.update(overrides)
    return TestCase(**defaults)


def test_run_case_passes_when_assertions_hold(fake_provider, tmp_path, monkeypatch):
    monkeypatch.setattr("promptcheck.runner.get_provider", lambda name: fake_provider)
    result = run_case(_case(), tmp_path, mode="record")
    assert result.passed
    assert result.response_text == "hello world"


def test_run_case_fails_when_assertion_fails(fake_provider, tmp_path, monkeypatch):
    monkeypatch.setattr("promptcheck.runner.get_provider", lambda name: fake_provider)
    case = _case(asserts=[Assertion(type="contains", value="goodbye")])
    result = run_case(case, tmp_path, mode="record")
    assert not result.passed
    assert result.assertion_results[0][1].passed is False


def test_run_case_missing_cassette_in_replay_mode_fails_cleanly(
    fake_provider, tmp_path, monkeypatch
):
    monkeypatch.setattr("promptcheck.runner.get_provider", lambda name: fake_provider)
    result = run_case(_case(), tmp_path, mode="replay")
    assert not result.passed
    assert result.error is not None
    assert fake_provider.call_count == 0


def test_run_case_replays_recorded_cassette_without_calling_provider(
    fake_provider, tmp_path, monkeypatch
):
    monkeypatch.setattr("promptcheck.runner.get_provider", lambda name: fake_provider)
    run_case(_case(), tmp_path, mode="record")
    assert fake_provider.call_count == 1

    result = run_case(_case(), tmp_path, mode="replay")
    assert result.passed
    assert fake_provider.call_count == 1
