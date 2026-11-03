# 0002 — The model client is an injected callable

**Status:** accepted

## Context

The engagement pipeline needs a language model, but tying the library to one
provider SDK would add a dependency, network access in tests, and lock-in.

## Decision

Model-backed stages take `client: Callable[[str, str], str] | None`. It
receives the system prompt and the task prompt, and returns raw text that
must parse as a JSON object. The library builds no client and makes no
network call of its own.

Without a client, each stage returns its empty contract and records
`"<stage>: no generation client configured"` in `meta.degraded`.

## Consequences

- Zero runtime dependencies; tests use a stub that returns canned JSON.
- Any provider can be plugged in with a few lines of code.
- No provider adapter ships yet, so a real engagement requires the caller to
  write one.
