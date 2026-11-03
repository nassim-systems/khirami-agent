# 0001 — Deterministic framing before any model call

**Status:** accepted

## Context

A consulting answer depends on reading the request correctly: what is asked,
for whom, in which register, under which constraints. Leaving that to a model
makes it unpredictable and hard to test.

## Decision

`interpret()` frames every request with lexical rules, before any model is
involved. It is the only function allowed to read the raw request. Every later
stage reads its structured frame. Missing dimensions are listed in
`missing_info`, and a three-level `confidence` is derived from their count.

## Consequences

- Framing is deterministic, fast, and covered by unit tests in five languages.
- The clarification gate can act on named gaps instead of guesses.
- Framing only recognizes what its lexicons contain. Paraphrases outside them
  are missed, and the frame says so through `missing_info` instead of
  inventing a value.
