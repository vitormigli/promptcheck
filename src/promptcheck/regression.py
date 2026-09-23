"""Compares a current run's results against a stored baseline (a previous
run's results.json) and flags regressions: tests that passed before and fail
now. A newly added test, or one that was already failing, is not a regression."""

import json
from dataclasses import dataclass
from pathlib import Path

from promptcheck.runner import TestResult


@dataclass
class RegressionReport:
    regressions: list[str]
    fixed: list[str]
    new_tests: list[str]
    unchanged_pass: list[str]
    unchanged_fail: list[str]

    @property
    def has_regressions(self) -> bool:
        return len(self.regressions) > 0


def save_results(results: list[TestResult], path: Path) -> None:
    payload = {r.id: r.passed for r in results}
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_baseline(path: Path) -> dict[str, bool]:
    if not Path(path).exists():
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def compare_to_baseline(results: list[TestResult], baseline: dict[str, bool]) -> RegressionReport:
    regressions, fixed, new_tests, unchanged_pass, unchanged_fail = [], [], [], [], []

    for r in results:
        previous = baseline.get(r.id)
        if previous is None:
            new_tests.append(r.id)
        elif previous and not r.passed:
            regressions.append(r.id)
        elif not previous and r.passed:
            fixed.append(r.id)
        elif previous and r.passed:
            unchanged_pass.append(r.id)
        else:
            unchanged_fail.append(r.id)

    return RegressionReport(
        regressions=regressions,
        fixed=fixed,
        new_tests=new_tests,
        unchanged_pass=unchanged_pass,
        unchanged_fail=unchanged_fail,
    )
