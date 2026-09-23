import pytest

from promptcheck.cassette import CassetteProvider, MissingCassetteError, cassette_key


def test_cassette_key_is_deterministic():
    k1 = cassette_key("openai", "gpt-4o-mini", [{"role": "user", "content": "hi"}], 100)
    k2 = cassette_key("openai", "gpt-4o-mini", [{"role": "user", "content": "hi"}], 100)
    assert k1 == k2


def test_cassette_key_changes_with_prompt():
    k1 = cassette_key("openai", "gpt-4o-mini", [{"role": "user", "content": "hi"}], 100)
    k2 = cassette_key("openai", "gpt-4o-mini", [{"role": "user", "content": "bye"}], 100)
    assert k1 != k2


def test_replay_mode_never_calls_wrapped_provider_without_cassette(fake_provider, tmp_path):
    cassette = CassetteProvider(fake_provider, tmp_path, mode="replay")
    with pytest.raises(MissingCassetteError):
        cassette.complete("model-x", [{"role": "user", "content": "hi"}])
    assert fake_provider.call_count == 0


def test_record_mode_calls_wrapped_provider_and_saves(fake_provider, tmp_path):
    cassette = CassetteProvider(fake_provider, tmp_path, mode="record")
    response = cassette.complete("model-x", [{"role": "user", "content": "hi"}])
    assert response.text == "hello world"
    assert fake_provider.call_count == 1
    assert list(tmp_path.glob("*.json"))


def test_replay_mode_reads_cassette_without_calling_provider(fake_provider, tmp_path):
    recorder = CassetteProvider(fake_provider, tmp_path, mode="record")
    recorder.complete("model-x", [{"role": "user", "content": "hi"}])
    assert fake_provider.call_count == 1

    replayer = CassetteProvider(fake_provider, tmp_path, mode="replay")
    response = replayer.complete("model-x", [{"role": "user", "content": "hi"}])
    assert response.text == "hello world"
    assert fake_provider.call_count == 1  # unchanged — replay didn't call it again


def test_invalid_mode_rejected(fake_provider, tmp_path):
    with pytest.raises(ValueError):
        CassetteProvider(fake_provider, tmp_path, mode="live")
