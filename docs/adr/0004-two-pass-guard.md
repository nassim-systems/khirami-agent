# 0004 — Two-pass guard: deterministic first, model only on violation

**Status:** accepted

## Context

A final quality gate must catch engineering jargon, hype, missing fields,
orphan actions and vague actions. Running a full model audit on every
deliverable is slow and costly.

## Decision

`run_guard()` first runs deterministic checks: off-register terms, hype
terms, required fields, traceability, owner and done-condition. The model is
called only if at least one violation is found, and only once. A corrected
deliverable replaces the strategy (`guard_status = "corrected"`). Without one,
the status stays `"pending"` for human review.

## Consequences

- A clean deliverable costs no model call, which a test verifies.
- Lexical checks are substring matches: they can flag a legitimate use of a
  listed word.
