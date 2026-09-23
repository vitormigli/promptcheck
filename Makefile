.PHONY: test lint run record regression-demo eval

test:
	uv run pytest

lint:
	uv run ruff check .

run:
	uv run promptcheck run suites/example.yaml --cassette-dir cassettes

record:
	uv run promptcheck run suites/example.yaml --cassette-dir cassettes --save-baseline evals/baseline_v1.json
	uv run promptcheck record suites/example_v2_regressed.yaml --cassette-dir cassettes

regression-demo:
	uv run promptcheck run suites/example_v2_regressed.yaml --cassette-dir cassettes --baseline evals/baseline_v1.json

eval:
	uv run python evals/run_eval.py
