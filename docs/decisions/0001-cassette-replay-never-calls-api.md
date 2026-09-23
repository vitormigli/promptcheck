# 1. Replay mode never calls the wrapped provider, even on a miss

## Status

Accepted

## Context

The entire point of this tool is to make prompt regression testing safe to run
in CI and safe to run often. A framework that silently falls back to a real
API call whenever a cassette is missing would defeat that — a typo in a
prompt, or a forgotten `make record`, would quietly start spending money and
introduce network flakiness into CI, exactly the failure mode this project
exists to prevent.

## Decision

`CassetteProvider` in replay mode (`cassette.py`) raises `MissingCassetteError`
on a cache miss instead of falling back to a live call. Only `mode="record"`
is allowed to call the wrapped provider.

## Consequences

- A test suite can never accidentally spend money just by being run.
- Forgetting to record a cassette for a new test case is a loud, immediate
  failure (`MissingCassetteError` names the exact missing file) rather than a
  silent live call that happens to work today and breaks tomorrow when the
  key is missing.
- Recording is a deliberate, separate step (`make record` / `promptcheck
  record`) — never bundled into the default test command.
