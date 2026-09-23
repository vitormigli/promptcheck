"""Runs a list of TestCases through the (cassette-wrapped) providers and
their assertions, producing one TestResult per case."""

from dataclasses import dataclass, field
from pathlib import Path

from promptcheck.assertions import AssertionResult, run_assertion
from promptcheck.cassette import CassetteProvider, MissingCassetteError
from promptcheck.providers import ProviderResponse, get_provider
from promptcheck.suite import TestCase


@dataclass
class TestResult:
    __test__ = False  # not a pytest test class, just named similarly

    id: str
    passed: bool
    response_text: str | None
    assertion_results: list[tuple[str, AssertionResult]] = field(default_factory=list)
    error: str | None = None
    latency_seconds: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0


def run_case(case: TestCase, cassette_dir: Path, mode: str = "replay") -> TestResult:
    provider = CassetteProvider(get_provider(case.provider), cassette_dir, mode=mode)

    try:
        response: ProviderResponse = provider.complete(
            case.model, case.messages, max_tokens=case.max_tokens
        )
    except MissingCassetteError as e:
        return TestResult(id=case.id, passed=False, response_text=None, error=str(e))

    assertion_results = []
    for assertion in case.asserts:
        result = run_assertion(assertion.type, response.text, response, assertion.value)
        assertion_results.append((assertion.type, result))

    passed = all(r.passed for _, r in assertion_results)
    return TestResult(
        id=case.id,
        passed=passed,
        response_text=response.text,
        assertion_results=assertion_results,
        latency_seconds=response.latency_seconds,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
    )


def run_suite(cases: list[TestCase], cassette_dir: Path, mode: str = "replay") -> list[TestResult]:
    return [run_case(case, cassette_dir, mode=mode) for case in cases]
