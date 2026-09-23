"""CLI: `promptcheck run suites/*.yaml` (replay, free) and
`promptcheck record suites/*.yaml` (real API calls, opt-in)."""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from promptcheck.regression import compare_to_baseline, load_baseline, save_results
from promptcheck.report import render_console, render_regression
from promptcheck.runner import run_suite
from promptcheck.suite import load_suites


def _run(args: argparse.Namespace, mode: str) -> int:
    load_dotenv()
    paths = [Path(p) for p in args.suites]
    cases = load_suites(paths)
    results = run_suite(cases, cassette_dir=Path(args.cassette_dir), mode=mode)
    print(render_console(results))

    exit_code = 0 if all(r.passed for r in results) else 1

    if args.baseline:
        baseline = load_baseline(Path(args.baseline))
        report = compare_to_baseline(results, baseline)
        print()
        print(render_regression(report))
        if report.has_regressions:
            exit_code = 1

    if args.save_baseline:
        save_results(results, Path(args.save_baseline))

    return exit_code


def main() -> None:
    parser = argparse.ArgumentParser(prog="promptcheck")
    subparsers = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("suites", nargs="+", help="YAML suite file(s)")
    common.add_argument("--cassette-dir", default="cassettes")
    common.add_argument("--baseline", default=None, help="Path to a baseline results.json")
    common.add_argument("--save-baseline", default=None, help="Path to write this run's results")

    run_parser = subparsers.add_parser(
        "run", parents=[common], help="Replay mode — free, never calls the API"
    )
    run_parser.set_defaults(mode="replay")

    record_parser = subparsers.add_parser(
        "record", parents=[common], help="Record mode — calls the real API for any missing cassette"
    )
    record_parser.set_defaults(mode="record")

    args = parser.parse_args()
    exit_code = _run(args, mode=args.mode)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
