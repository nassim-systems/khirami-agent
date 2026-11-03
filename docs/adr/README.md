# Architecture decision records

Short records of the decisions that shape the code. Each one states the
context, the decision and its consequences.

| # | Decision |
| --- | --- |
| [0001](0001-deterministic-framing-first.md) | Deterministic framing before any model call |
| [0002](0002-injected-model-client.md) | The model client is an injected callable |
| [0003](0003-process-before-automation.md) | Process before automation, traceability enforced in code |
| [0004](0004-two-pass-guard.md) | Two-pass guard: deterministic first, model only on violation |
| [0005](0005-multilingual-lexicons-as-data.md) | Multilingual lexicons isolated as data, canonical English categories |
| [0006](0006-anthropic-adapter.md) | Anthropic adapter as an optional extra, key from the environment only |
