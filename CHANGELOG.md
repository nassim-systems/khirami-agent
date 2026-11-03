# Changelog

All notable changes to this project are documented in this file. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.0 - 2026-11-03

First version.

### Added

- **Request framing** (`interpret()`): objective, subject, recipient, tone,
  depth, constraints, quoted focus, measurable targets, missing information
  and a three-level confidence. Language detection for English, French,
  Spanish, Italian and Portuguese that returns `undetermined` instead of
  guessing.
- **Consulting engagement pipeline** (`run_engagement()`): a deterministic
  router, then seven modules — intake, clarification gate, diagnostic,
  process optimization, automation, strategy output and guard — around a
  single `EngagementState`. Four execution modes: `full_audit`,
  `quick_scan`, `automation_focus`, `follow_up`.
- **Rules enforced in code** after each model answer: three root causes at
  most, bottlenecks linked to a diagnosed cause, automation limited to the
  target flow, a mandatory do-not-automate list, three plan horizons, one
  retry on invalid JSON, and gaps declared in `meta.degraded`.
- **Consultant guard**: deterministic checks for traceability, technical
  register, hype, completeness and vague actions. The model is called for a
  correction only when a check fails.
- **Anthropic adapter** (`AnthropicClient`), as the optional `anthropic`
  extra: default model `claude-sonnet-5-5`, key read from
  `ANTHROPIC_API_KEY` only, timeout, bounded retries and explicit errors.
- **Deterministic stacks** with no model call: `orchestrate()` with
  `generate_output()` (Markdown deliverable plan), and `run_agent()` with
  `render_output()` (mandate note), behind `KhiramiAgent.run()`.
- **Standalone constraint extractor** (`detect_language()`,
  `extract_constraints()`) for six languages. It is not yet wired into the
  decision paths.
- **Examples**: `examples/run_engagement.py` (full engagement on Claude) and
  `examples/run_without_model.py` (no key, no network).
- **Documentation**: README, architecture notes, style guide, six
  architecture decision records, a real sample engagement and a security
  policy.
- **Quality**: 326 tests, one of them a live API test skipped without a key,
  and a CI workflow running `ruff` and `pytest` on Python 3.10 to 3.13.
