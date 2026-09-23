"""This project's own "eval": runs the demo suite in replay mode (free,
proving cassette replay works), then re-runs the intentionally-regressed
variant against a saved baseline to demonstrate regression detection for
real. Writes results.md. No network calls — everything here replays
committed cassettes."""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from promptcheck.regression import compare_to_baseline, load_baseline  # noqa: E402
from promptcheck.runner import run_suite  # noqa: E402
from promptcheck.suite import load_suite  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
EVALS_DIR = Path(__file__).parent
CASSETTE_DIR = ROOT / "cassettes"


def main() -> None:
    # 1. Replay-mode run of the main suite: proves the cassette system works
    # end to end with zero API calls, and times how fast that is.
    v1_cases = load_suite(ROOT / "suites" / "example.yaml")
    start = time.monotonic()
    v1_results = run_suite(v1_cases, CASSETTE_DIR, mode="replay")
    replay_seconds = time.monotonic() - start
    v1_pass_rate = sum(r.passed for r in v1_results) / len(v1_results)

    # 2. Regression demo: the "v2" suite has one system prompt deliberately
    # weakened (a guardrail instruction removed). Compare it against the
    # v1 baseline saved earlier by `make record`.
    v2_cases = load_suite(ROOT / "suites" / "example_v2_regressed.yaml")
    v2_results = run_suite(v2_cases, CASSETTE_DIR, mode="replay")
    baseline = load_baseline(EVALS_DIR / "baseline_v1.json")
    regression_report = compare_to_baseline(v2_results, baseline)

    summary = {
        "replay_mode": {
            "n_tests": len(v1_results),
            "pass_rate": v1_pass_rate,
            "total_replay_seconds": replay_seconds,
            "live_api_calls_made": 0,
        },
        "regression_demo": {
            "regressions_detected": regression_report.regressions,
            "n_regressions": len(regression_report.regressions),
        },
    }
    (EVALS_DIR / "results.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    lines = ["# promptcheck — Self-Evaluation", ""]
    lines.append(
        f"Replay mode: {v1_pass_rate:.0%} pass rate on {len(v1_results)} tests, "
        f"{replay_seconds * 1000:.1f}ms total, 0 live API calls.\n"
    )
    lines.append(
        f"Regression demo: {len(regression_report.regressions)} regression(s) correctly "
        f"detected when comparing the weakened-prompt suite against the v1 baseline "
        f"(`{', '.join(regression_report.regressions)}`).\n"
    )
    (EVALS_DIR / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
