# 0003 — Process before automation, traceability enforced in code

**Status:** accepted

## Context

Automating a broken process makes the problem faster. Recommendations that
do not trace back to a diagnosed cause cannot be defended in front of a
client.

## Decision

- The automation stage receives the *target* flow from the process stage,
  never the current flow.
- Every bottleneck must reference a diagnosed root cause; others are dropped.
- Automation candidates must use a known mechanism (`rules_workflow`,
  `ai_agent`, `hybrid`, `keep_human`), and `do_not_automate` must not be
  empty, otherwise the gap is declared.
- Every action in the strategy must carry `linked_to`, pointing at an
  upstream root cause, bottleneck or candidate id.

These rules are applied in code after each model call, not only requested in
the prompts.

## Consequences

- The model cannot silently break the method: the code filters or flags what
  it returns.
- The `automation_focus` mode skips the diagnostic, so its bottlenecks are not
  filtered against root causes.
