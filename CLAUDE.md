# Project instructions for Claude

This project follows the rules of the portfolio master plan:

1. No client code or data — the demo suite tests a fictional customer-support
   prompt, not any real product.
2. No committed secrets — `.env` is gitignored; committed cassettes contain
   only model *responses*, never API keys. `gitleaks` runs on pre-commit and
   in CI.
3. Every project reports numeric evaluation metrics — see `evals/results.md`.
4. Everything runs with a single command: `docker compose up` or `make test`
   — replay mode needs no API key at all.
5. README in English, with a short "Resumo em português" section at the end.
   Header banner + badges matching the other portfolio repos.
6. Small, descriptive commits using Conventional Commits.
7. Prefer simplicity — plain dataclasses and a dict-based assertion registry,
   no plugin system or DSL beyond the YAML suite format itself.

## Layout

- `src/promptcheck/providers.py` — thin wrapper over the real Anthropic/OpenAI
  SDKs.
- `src/promptcheck/cassette.py` — the VCR-style record/replay layer. Replay
  mode (the default) never calls an API — it raises `MissingCassetteError`
  instead. Only `mode="record"` spends money.
- `src/promptcheck/assertions.py` — the assertion registry (contains, regex,
  json_schema, custom, ...), each one a pure function, no I/O.
- `src/promptcheck/suite.py` / `runner.py` / `regression.py` / `report.py` —
  YAML loading, execution, baseline comparison, output rendering.
- `suites/example.yaml` — the demo suite; `suites/example_v2_regressed.yaml`
  is the same suite with one system prompt deliberately weakened, used to
  demonstrate regression detection.
- `cassettes/` — committed, recorded responses. `make test` and CI only ever
  replay these. Only `make record` makes real, billed API calls — never run
  it without the user's awareness of the cost.
