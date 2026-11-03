# Architecture

Khirami Agent is a library with three entry paths that share one framing
layer. This document describes what the code does. Design rationale lives in
[`adr/`](adr/).

## 1. Framing — `framing.py`

`interpret(request)` is the only function that reads the raw request. It
returns a frame:

| Key | Content |
| --- | --- |
| `objective` / `objectives` | Dominant objective, and every objective tied at the top score, in logical order (`analyze` → `decide` → `plan` → `produce` → …) |
| `subject` | What the request is about (`client`, `team`, `system`, `self`, `undetermined`) |
| `target` | Who the deliverable is for. Set only by a directional marker ("for the client") or a first-person plural; otherwise `undetermined` |
| `tone`, `depth` | Requested register and depth; tone falls back to a default derived from the target |
| `constraints` | Explicit constraints: `brevity`, `speed`, `precision`, `restricted_scope`, `no_implementation`, `imposed_format`, `language` |
| `focus` | The longest content-word phrase, quoted as written |
| `measures` | `direction`, `quantity`, `deadline`, when written explicitly |
| `missing_info`, `confidence` | Named gaps and a three-level confidence derived from their count |

**Language detection.** Function words are counted first. A language needs
at least two markers and a strict lead. A tie returns `undetermined` instead
of a guess. When function words give no answer, business-lexicon markers
decide, unless they contradict a weak function-word lead. With an
undetermined language, framing uses the merged lexicons of all five
languages, so the frame is still produced.

## 2. Consulting engagement — `engagement.py`

One mutable `EngagementState` travels through the stages. Each stage writes
its own block (`interpretation`, `clarification`, `diagnostic`, `process_map`,
`automation_plan`, `strategy`, `audit`) and reads only the blocks written
before it.

```
route → run_intake → run_gate → [mode-dependent stages] → state
```

- **Router.** Sets `meta.mode` (explicit or inferred, fallback `full_audit`)
  and `meta.sector_table` (from `business_context["sector"]` or inferred,
  fallback `general`).
- **Model calls.** `_call_model()` fills the system prompt, calls the
  injected client, parses JSON, retries once with the parse error, then
  records the gap in `meta.degraded`.
- **Post-processing in code.** Each stage caps or filters what the model
  returns: three root causes at most, bottlenecks linked to a known root
  cause, known automation mechanisms only, a sequence limited to known
  candidates, three fixed horizons.
- **Guard.** Deterministic checks for off-register vocabulary, hype terms,
  required fields, traceability (`linked_to` must match an upstream id), and
  vague actions (missing `owner_role` or `done_when`). The model is called
  only if at least one violation is found. Its corrected deliverable replaces
  the strategy, and `guard_status` becomes `corrected`. If no correction comes
  back, the status stays `pending`.

## 3. Deterministic stacks

### Planning — `planning.py` → `rendering.generate_output()`

`orchestrate(request)` selects plan capabilities and a template (analysis,
synthesis, plan, report, checklist, code, list, direct answer), applies the
constraints, and returns a plan with a status:

| Status | Condition | Rendering |
| --- | --- | --- |
| `compliant` | no violation | template sections, notices, scope boundary, tensions |
| `qualified` | a violation but sections remain | same, with a status banner and a "Reservations" section |
| `suspended` | no section survives the constraints | a non-compliance finding replaces the deliverable |

`generate_output()` renders that plan as Markdown. It never adds, reorders or
drops a section.

### Frame-driven — `selection.py` → `rendering.render_output()`

`select_capabilities()`, `select_format()` and `enforce_rules()` each read the
frame and nothing else. `orchestrate_frame()` puts them side by side, and
`run_agent()` wraps the result in a stable envelope. `render_output()`
projects it into an executive summary (three to five lines, always closing on
the expected decision), an observation / implication / impact analysis, and
three to seven imperative recommendations.

### Entry point — `agent.py`

`KhiramiAgent().run(request)` runs the planning stack.
`KhiramiAgent().run(request, modern=True)` runs the frame-driven stack.

## 4. Supporting modules

- `prompts.py` — the system prompt and the six task prompts, each with the
  exact JSON schema it expects. Placeholders use `<<name>>`, so the JSON braces
  are never confused with Python formatting.
- `constraints.py` — a standalone extractor for numeric bounds (word and
  bullet limits), register, tone, depth, format and target, in six languages.
  It is not yet called by any path.
- `style.py` — a registry of registers, writing rules and per-section briefs,
  described in [`style-guide.md`](style-guide.md). It is not yet called by any
  path.
- `lexicons/` — per-language data modules with identical table names and
  canonical English keys.
- `text.py` — normalization, accent folding and marker counting shared by the
  framing layers.
