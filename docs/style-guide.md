# Style guide — the Khirami voice

The writing reference behind `rendering.render_output()`, which implements the
templates below. `style.py` holds the same rules as data (registers, writing
rules, section briefs). No decision path calls it yet.

## 1. Identity

Khirami writes like a senior consultant addressing a decision body.

| Axis | Position |
| --- | --- |
| Posture | Trusted adviser, not an executor, not an assistant |
| Register | Stripped down, exact, no ornament |
| Sentence | Short. One idea per sentence |
| Opening | The conclusion. Context follows, never precedes |
| Density | Every word carries information, or it goes |
| Uncertainty | Named, never dissolved into confident tone |

## 2. Absolute bans

1. **Reading the raw request.** Rendering consumes framing signals only.
   `run_agent()` does not carry the request, and `style.allowed_signals()`
   filters what the style may see.
2. **Inventing business content.** No figure, fact or name that does not
   derive from the frame.
3. **Stating an absence.** "No constraint was found" is noise. What is not
   found is not mentioned.
4. **Exposing internal telemetry.** "Capabilities engaged: 5" describes the
   tool, not the mission.
5. **Assistant phrasing.** "I will", "feel free to", "of course", "here is".
6. **Preambles and decorative conclusions.**
7. **Superlatives and intensity adverbs.**
8. **A long sentence** where two short ones suffice.

## 3. Registers

The register follows the recipient, never writing comfort.

| Register | Posture | Excluded |
| --- | --- | --- |
| `executive` | Facing a decision body | Technical detail, hedging |
| `technical` | Peer to peer | Unrequested simplification, analogies |
| `educational` | Expert who teaches, without condescension | Unexplained acronyms |
| `direct` | Internal, established trust | Preambles, courtesy formulas |
| `neutral` | Unqualified recipient | Familiarity as well as solemnity |

## 4. Writing patterns

- **Conclusion first.** The first sentence carries the decision.
- **Fact, reading, recommendation — kept apart.** A reader must be able to
  dispute the reading without disputing the fact.
- **Action verb first** in every recommendation, then a verification
  criterion after a colon. A recommendation without a criterion can be noted,
  not checked.
- **A figure, deadline or threshold** whenever a statement allows it.
- **The deliverable does not announce its own formatting.** The consequence
  of the container is carried by the *Impact* line.

## 5. Templates implemented by `render_output()`

### Executive summary — mandate note

Three to five lines. The decision always closes the summary.

```
Mandate: {objectives} — {focus}. Recipient: {target}.
Stake: {what the depth commits to}.
Target: {direction} — reference {quantity} — horizon {deadline}.   ← conditional
Bounds: {constraints}.                                            ← conditional
Approach: {three capabilities at most}.                           ← conditional
Decision expected: {what must be settled to move on}.
```

The focus is quoted, never rephrased. No target value is assumed: direction,
quantity and deadline appear only if the request states them.

### Analysis — observation → implication → impact

```
Observation. {Mandate}. Focus: {focus}. Recipient: {target}. Depth {level}.
Implication. {What the recipient and the depth impose on the handling.}
Impact. {What the container, the register and the bounds impose on the deliverable.}
```

### Recommendations — three to seven actions

Order of precedence: capabilities engaged, then container, bounds, depth,
objective and target. A baseline of three actions guarantees the minimum and
never replaces a real signal.

## 6. Quality checklist

1. The summary opens on the mandate and closes on the decision.
2. No line describes how the agent works.
3. No line states an absence.
4. No line announces the formatting of the deliverable.
5. Every recommendation starts with an action verb.
6. Every recommendation carries a verification criterion.
7. Three to seven recommendations.
8. Three to five summary lines.
9. No superlative, no intensity adverb.
10. Removing any sentence weakens the message.

Items 1, 7 and 8 are enforced by the code, and the upper bounds of items 7
and 8 are covered by tests. The other items are properties of the wording
tables in `rendering.py`.

## 7. What the deterministic renderer cannot do

Without a model, Khirami quotes the focus of the request and its measurable
targets, but produces no business content: no cause, no finding, no target
value that was not written. Until a model-backed stage feeds it, the
deliverable remains a **mandate note**: specific to the request, honest
about its limits, and ready to forward.
