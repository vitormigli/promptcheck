"""Console and Markdown report rendering for a test run."""

from promptcheck.regression import RegressionReport
from promptcheck.runner import TestResult


def render_console(results: list[TestResult]) -> str:
    lines = []
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        lines.append(f"[{status}] {r.id}")
        if r.error:
            lines.append(f"       error: {r.error}")
            continue
        for assertion_type, result in r.assertion_results:
            if not result.passed:
                lines.append(f"       failed assertion ({assertion_type}): {result.message}")

    n_passed = sum(r.passed for r in results)
    lines.append(f"\n{n_passed}/{len(results)} passed")
    return "\n".join(lines)


def render_regression(report: RegressionReport) -> str:
    lines = []
    if report.regressions:
        lines.append(f"REGRESSIONS ({len(report.regressions)}): {', '.join(report.regressions)}")
    if report.fixed:
        lines.append(f"Fixed since baseline ({len(report.fixed)}): {', '.join(report.fixed)}")
    if report.new_tests:
        lines.append(f"New tests ({len(report.new_tests)}): {', '.join(report.new_tests)}")
    if not report.regressions:
        lines.append("No regressions vs. baseline.")
    return "\n".join(lines)


def render_markdown_summary(results: list[TestResult], title: str = "Test Results") -> str:
    n_passed = sum(r.passed for r in results)
    total_latency = sum(r.latency_seconds for r in results)
    lines = [f"# {title}", ""]
    lines.append(f"{n_passed}/{len(results)} passed. Total replay time: {total_latency:.3f}s.\n")
    lines.append("| Test | Status | Latency |")
    lines.append("|---|---|---|")
    for r in results:
        status = "✅" if r.passed else "❌"
        lines.append(f"| {r.id} | {status} | {r.latency_seconds:.3f}s |")
    return "\n".join(lines)
