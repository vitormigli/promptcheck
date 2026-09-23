# 2. Cassette key is a hash of the request, not the test's id

## Status

Accepted

## Context

An earlier design keyed cassettes by test id (`greets_in_portuguese.json`).
That has a subtle bug: if the prompt for that test changes but the id stays
the same, the old cassette keeps matching — the test would silently replay a
response to a *different* question than the one it now asks, and pass or fail
for the wrong reason.

## Decision

`cassette_key()` (`cassette.py`) hashes `(provider, model, messages,
max_tokens)` — the exact request. Two test cases with different ids but an
identical prompt share a cassette (and only cost one real call to record);
one test case whose prompt changes gets a new cassette key automatically.

## Consequences

- Editing a test's prompt always requires a fresh recording — there is no way
  to silently go stale, which is the property this project's regression-demo
  suite relies on (`suites/example_v2_regressed.yaml` reuses every id from
  `example.yaml`, but only the one entry whose prompt actually changed needed
  a new cassette).
- Cassette filenames are opaque hashes, not test ids — a minor readability
  cost, traded for correctness.
