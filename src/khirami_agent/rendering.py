"""
Rendering — the last step, turning decisions into a readable deliverable.

Two renderers, one per decision path:

    generate_output(plan)   Markdown text from the plan of `orchestrate()`.
    render_output(envelope) A structured consulting deliverable (executive
                            summary, analysis, recommendations) from the
                            envelope of `run_agent()`.

Neither renderer takes a decision: they make visible what was settled
upstream. No field is invented — only fields the upstream stages actually
produce are consumed.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

# ======================================================================
# Plan renderer — `generate_output()`.
#
# Input contract (exact output of `orchestrate()`):
#     response.status            — compliant | qualified | suspended
#     response.format            — selected template
#     response.sections          — [{"id", "role"}, ...] in assembly order
#     response.register          — {"tone", "depth", "length"}
#     response.mandatory_notices — notices imposed by the rules applied
#     response.scope_boundary    — declared scope boundary
#     violations                 — rules broken
#     tensions                   — frictions exposed, never arbitrated
# ======================================================================

FORMAT_TITLES: Mapping[str, str] = {
    "analysis": "Analysis",
    "synthesis": "Synthesis",
    "summary": "Synthesis",
    "plan": "Action plan",
    "report": "Report",
    "checklist": "Checklist",
    "direct_answer": "Answer",
    "list": "List",
    "table": "Comparison table",
    "code": "Technical deliverable",
}

SECTION_LABELS: Mapping[str, str] = {
    "open_questions": "Open questions",
    "framing": "Framing",
    "established_facts": "Established facts",
    "dynamics": "Underlying dynamics",
    "tension_points": "Tension points",
    "prioritization": "Prioritization",
    "uncertainties": "Uncertainties",
    "key_message": "Key message",
    "supporting_points": "Supporting points",
    "trade_offs": "Trade-offs",
    "set_aside": "Deliberately left out",
    "objective": "Objective",
    "sequencing": "Sequencing",
    "milestones": "Milestones",
    "resources": "Resources",
    "risks": "Risks",
    "decision_points": "Decision points",
    "executive_summary": "Executive summary",
    "context_and_mandate": "Context and mandate",
    "method_and_sources": "Method and sources",
    "findings": "Findings",
    "options": "Options",
    "recommendation": "Recommendation",
    "implementation": "Implementation",
    "appendices": "Appendices",
    "scope": "Scope",
    "checkpoints": "Checkpoints",
    "criteria": "Validation criteria",
    "blockers": "Blockers and watch points",
    "owners": "Owners",
    "answer": "Answer",
    "support": "Basis",
    "items": "Items",
    "columns": "Comparison axes",
    "rows": "Items compared",
    "artifact": "Artifact",
    "structure_notes": "Structure notes",
    "sources": "Sources",
    "reservations": "Caveats",
    "non_compliance_finding": "Non-compliance finding",
    "required_remediations": "Required changes",
}

STATUS_BANNERS: Mapping[str, str | None] = {
    "compliant": None,
    "qualified": "Status: conditional — ready to deliver once the issues below are resolved.",
    "suspended": "Status: suspended — the issues found block delivery.",
}


def _label(identifier: Any) -> str:
    """Readable label of a section, otherwise its reformatted identifier."""
    if identifier in SECTION_LABELS:
        return SECTION_LABELS[identifier]
    readable = str(identifier).replace("_", " ").strip()
    return readable[:1].upper() + readable[1:] if readable else "Section"


def _sentence(text: Any) -> str:
    """Normalize a section role into a standalone sentence."""
    text = str(text or "").strip()
    if not text:
        return ""
    if text[0].islower():
        text = text[0].upper() + text[1:]
    if text[-1] not in ".!?:":
        text += "."
    return text


def _bullets(entries: Iterable[Any]) -> str:
    """Render items as a bulleted list."""
    return "\n".join("- " + str(entry).strip() for entry in entries if str(entry).strip())


def _section_body(
    identifier: str, role: Any, response_format: str, violations: Sequence[str]
) -> str:
    """Body of a section, specialized when the template requires it."""
    if identifier == "reservations":
        return _bullets(violations) or "- no caveats recorded"
    if identifier == "artifact" and response_format == "code":
        return "```\n" + str(role or "artifact to produce").strip() + "\n```"
    if identifier == "checkpoints" and response_format == "checklist":
        return "- [ ] " + str(role or "").strip()
    if identifier == "items" and response_format == "list":
        return "- " + str(role or "").strip()
    if identifier == "rows" and response_format == "table":
        return "| Item | Criterion | Assessment |\n| --- | --- | --- |\n|  |  |  |"
    return _sentence(role)


def _register_line(register: Mapping[str, Any]) -> str:
    """Register line — tone, depth, length."""
    parts = []
    if register.get("tone"):
        parts.append("tone " + str(register["tone"]))
    if register.get("depth"):
        parts.append("depth " + str(register["depth"]))
    if register.get("length"):
        parts.append("length " + str(register["length"]))
    return " · ".join(parts)


def _trailer(notices: Sequence[str], boundary: str, tensions: Sequence[str]) -> list[str]:
    """Closing blocks shared by every status: notices, boundary, tensions."""
    blocks = []
    if notices:
        blocks.append("**Mandatory notices**\n" + _bullets(notices))
    if boundary:
        blocks.append("**Scope boundary**\n" + _sentence(boundary))
    if tensions:
        blocks.append("**Flagged tensions**\n" + _bullets(tensions))
    return blocks


def generate_output(plan: Any) -> str:
    """
    Turn the plan assembled by `orchestrate()` into final Markdown text.

    Statuses
        compliant — regular deliverable.
        qualified — deliverable completed by a "Reservations" section fed by
                    the violations found.
        suspended — the deliverable is replaced by a non-compliance finding:
                    a partial rendering would hide the issue.

    Accepts the dictionary returned by `orchestrate()`, or its `response`
    sub-dictionary alone. Returns a string; no printing, no side effect.
    """
    # 1. Defensive read — accept only what the contract guarantees.
    source = plan if isinstance(plan, dict) else {}
    response = source.get("response")
    if not isinstance(response, dict):
        response = source

    status = response.get("status") or "compliant"
    response_format = response.get("format") or "direct_answer"
    sections = [
        section for section in (response.get("sections") or ()) if isinstance(section, dict)
    ]
    register = response.get("register")
    register = register if isinstance(register, dict) else {}
    notices = [str(notice) for notice in (response.get("mandatory_notices") or ())]
    boundary = response.get("scope_boundary") or ""
    violations = [str(violation) for violation in (source.get("violations") or ())]
    tensions = [str(tension) for tension in (source.get("tensions") or ())]

    # 2. Suspended status — the finding replaces the deliverable.
    if status == "suspended":
        blocks = ["# Non-compliance finding", STATUS_BANNERS["suspended"]]
        blocks.append("Assembly stopped: delivering as is would hide the problem.")
        blocks.append("**Rules broken**\n" + (_bullets(violations) or "- no rule named"))
        for section in sections:
            if section.get("id") == "required_remediations":
                blocks.append(
                    "**" + _label("required_remediations") + "**\n" + _sentence(section.get("role"))
                )
        blocks.extend(_trailer(notices, boundary, tensions))
        return "\n\n".join(block for block in blocks if block)

    # 3. Header — template and register.
    blocks = ["# " + FORMAT_TITLES.get(response_format, "Deliverable")]
    banner = STATUS_BANNERS.get(status)
    if banner:
        blocks.append(banner)
    register_line = _register_line(register)
    if register_line:
        blocks.append("_" + register_line + "_")

    # 4. Body — the sections, in the order decided by the assembly.
    rendered_ids = set()
    for section in sections:
        identifier = section.get("id") or ""
        rendered_ids.add(identifier)
        body = _section_body(identifier, section.get("role"), response_format, violations)
        blocks.append("## " + _label(identifier) + ("\n" + body if body else ""))

    # 5. Reservations — guaranteed even if the section was not assembled.
    if status == "qualified" and "reservations" not in rendered_ids:
        blocks.append(
            "## "
            + _label("reservations")
            + "\n"
            + (_bullets(violations) or "- no caveats recorded")
        )

    # 6. Closing — notices, scope boundary, tensions.
    trailer = _trailer(notices, boundary, tensions)
    if trailer:
        blocks.append("---")
        blocks.extend(trailer)

    return "\n\n".join(block for block in blocks if block)


# ======================================================================
# Consulting renderer — `render_output()`.
#
# Consumes the envelope of `run_agent()`. Shares nothing with
# `generate_output()`.
# ======================================================================

RENDER_KEYS: tuple[str, ...] = (
    "executive_summary",
    "analysis",
    "recommendations",
    "format",
    "meta",
)

MIN_RECOMMENDATIONS: int = 3
MAX_RECOMMENDATIONS: int = 7
MAX_SUMMARY_LINES: int = 5

# ----------------------------------------------------------------------
# Mandate — what is asked, about what, for whom.
# ----------------------------------------------------------------------
SHORT_MANDATE: Mapping[str, str] = {
    "analyze": "diagnosis",
    "plan": "action plan",
    "produce": "deliverable",
    "summarize": "summary",
    "explain": "explanation",
    "decide": "decision support",
    "verify": "review",
    "answer": "answer",
}

SUBJECT_LABEL: Mapping[str, str] = {
    "client": "the client relationship",
    "team": "the internal organization",
    "system": "the technical system",
    "self": "a personal matter",
}

# The quoted focus outranks the inferred category: "ticket handling delays"
# says what "the client relationship" never will.
DIRECTION_LABEL: Mapping[str, str] = {
    "decrease": "decrease",
    "increase": "increase",
}
MEASURE_ACTION: str = "Set the target value and the date it will be measured."

DESTINATION: Mapping[str, str] = {
    "client": "external client",
    "team": "internal team",
    "system": "technical system",
    "self": "personal use",
    "undetermined": "not identified",
}

STAKE: Mapping[str, str] = {
    "in_depth": "What matters: find the causes, not just describe the symptoms.",
    "condensed": "What matters: make the call, and cut without losing substance.",
    "standard": "What matters: reach a conclusion without going further than needed.",
}

DECISION: Mapping[str, str] = {
    "analyze": "Decision needed: confirm the scope of the diagnosis.",
    "plan": "Decision needed: agree on what success looks like.",
    "produce": "Decision needed: approve the direction before production starts.",
    "summarize": "Decision needed: confirm what can be left out.",
    "explain": "Decision needed: confirm the reading level to aim for.",
    "decide": "Decision needed: agree on the options to compare.",
    "verify": "Decision needed: set the pass threshold.",
    "answer": "Decision needed: approve the direction before production starts.",
}

# Approach announced in the summary — an executive reading of the capabilities.
CAPABILITY_APPROACH: Mapping[str, str] = {
    "analysis": "root-cause analysis",
    "synthesis": "distilling the key points",
    "action_planning": "sequencing the work",
    "formatting": "prioritizing the content",
    "summary": "condensing",
    "deep_dive": "backing every conclusion",
    "client_care": "writing for an external reader",
    "executive_framing": "leading with the conclusion",
    "verification": "review before delivery",
}
MAX_APPROACHES: int = 3

TARGET_LABEL: Mapping[str, str] = {
    "client": "an external client",
    "team": "an internal team",
    "system": "a technical system",
    "self": "personal use",
    "undetermined": "not identified",
}

DEPTH_LABEL: Mapping[str, str] = {
    "in_depth": "in depth",
    "condensed": "condensed",
    "standard": "standard",
}

CONSTRAINT_LABEL: Mapping[str, str] = {
    "brevity": "brevity",
    "speed": "tight deadline",
    "precision": "precision",
    "restricted_scope": "narrow scope",
    "no_implementation": "structure only, no logic",
    "imposed_format": "required format",
    "language": "required language",
    "max-bullets": "bullet limit",
    "word-limit": "length limit",
}

# ----------------------------------------------------------------------
# Analysis — observation, implication, impact.
# ----------------------------------------------------------------------
IMPLICATION_BY_TARGET: Mapping[str, str] = {
    "client": "An external reader needs a self-contained message with no unexplained "
    "internal terms.",
    "team": "An internal audience needs clear ownership: who is responsible for what.",
    "system": "A technical subject calls for exact terms, never paraphrase.",
    "self": "For personal use, maximum density and minimal formatting are fine.",
    "undetermined": "The audience is not identified, so the register must be confirmed "
    "before sharing.",
}

IMPLICATION_BY_DEPTH: Mapping[str, str] = {
    "in_depth": "The requested depth means explaining mechanisms, not just their effects.",
    "condensed": "Brevity forces trade-offs: what is left out matters as much as what stays.",
    "standard": "The expected level is what is needed, and no more.",
}

IMPACT_BY_FORMAT: Mapping[str, str] = {
    "bullet_points": "The format calls for one idea per bullet.",
    "paragraph": "The format calls for one continuous line of argument.",
    "executive_summary": "The format calls for the conclusion first.",
    "action_plan": "The format calls for steps that can be executed as written.",
    "table": "The format calls for axes defined before the table is filled in.",
    "email": "The format calls for the subject in the first line.",
    "brief": "The format calls for a single page, with no appendix.",
}

IMPACT_BY_TONE: Mapping[str, str] = {
    "executive": "An executive register rules out technical detail and hedging.",
    "technical": "A technical register rules out unrequested simplification.",
    "educational": "An educational register means defining every term introduced.",
    "direct": "A direct register rules out preambles and stock phrases.",
    "neutral": "A neutral register avoids both familiarity and formality.",
}

# ----------------------------------------------------------------------
# Recommendations — imperative, measurable, outcome-oriented.
#
# Form: an action verb first, then a check after a colon. A recommendation
# without a check can be noted, not verified.
# ----------------------------------------------------------------------
CAPABILITY_ACTION: Mapping[str, str] = {
    "analysis": "Establish the causes before proposing anything: no recommendation "
    "without an identified cause.",
    "synthesis": "Boil the message down to its key points: five at most.",
    "action_planning": "Sequence the steps and name their dependencies: every step has "
    "an explicit prerequisite.",
    "formatting": "Prioritize the content: the essentials must be clear on a first read.",
    "summary": "Cut every statement that carries no information.",
    "deep_dive": "Back every conclusion: one fact or source per claim.",
    "client_care": "Write for an external reader: no unexplained internal terms.",
    "executive_framing": "Open with the decision needed, never with the background.",
    "verification": "Check the deliverable against the mandate before sending it.",
}

FORMAT_ACTION: Mapping[str, str] = {
    "bullet_points": "Keep one idea per bullet: no compound sentences.",
    "paragraph": "Keep a single line of argument from start to finish.",
    "executive_summary": "Lead with the conclusion, then give the context.",
    "action_plan": "Make every step executable as written: name an owner and a deadline.",
    "table": "Define the comparison axes before filling in the table.",
    "email": "State the subject in the first line.",
    "brief": "Fit it on one page, with no appendix.",
}

CONSTRAINT_ACTION: Mapping[str, str] = {
    "brevity": "Cut anything that adds nothing.",
    "speed": "Deliver the useful core now rather than everything late.",
    "precision": "Tie every claim to its source.",
    "restricted_scope": "Stay strictly within the requested scope.",
    "no_implementation": "Stick to structure and produce no logic.",
    "imposed_format": "Follow the requested format as given.",
    "language": "Write in the requested language.",
    "max-bullets": "Stay within the bullet limit.",
    "word-limit": "Stay within the length limit.",
}

DEPTH_ACTION: Mapping[str, str] = {
    "in_depth": "Address causes, not symptoms.",
    "condensed": "Make the call: cut without losing substance.",
    "standard": "Cover what is needed, and no more.",
}

OBJECTIVE_ACTION: Mapping[str, str] = {
    "analyze": "Frame the question before starting the analysis.",
    "plan": "Define success before sequencing the steps.",
    "produce": "Make sure the deliverable stands on its own, without its author.",
    "summarize": "Choose what to leave out as carefully as what to keep.",
    "explain": "Start from what the reader knows, not from what the author knows.",
    "decide": "Show the options that were set aside, and why.",
    "verify": "Separate blockers from points to watch.",
    "answer": "Answer first, then justify.",
}

TARGET_ACTION: Mapping[str, str] = {
    "client": "Remove unexplained internal jargon.",
    "team": "Name who is responsible for what.",
    "system": "Use the exact technical terms.",
    "self": "Get to the point and skip unnecessary formatting.",
    "undetermined": "Confirm who the audience is before sharing.",
}

BASELINE_ACTIONS: tuple[str, ...] = (
    "Lead with the conclusion, then build the argument.",
    "Tie every claim to what supports it.",
    "Cut every sentence that carries no information.",
)


def _unique(entries: Iterable[str | None]) -> list[str]:
    """Non-empty entries, deduplicated, in order of appearance."""
    ordered: list[str] = []
    for entry in entries:
        if entry and entry not in ordered:
            ordered.append(entry)
    return ordered


def _enumerate(labels: Sequence[str]) -> str:
    """Readable enumeration of labels."""
    return ", ".join(labels)


def _scope(focus: str, subject: str, target: str) -> str:
    """
    What the mandate is about.

    The quoted focus wins: it names what the inferred category can only
    approach. Otherwise the category takes over — and only if it differs from
    the recipient, since repeating it adds nothing.
    """
    if focus:
        return focus
    scope = SUBJECT_LABEL.get(subject)
    return scope if scope and subject != target else ""


def _mandate(
    objective: str, objectives: Sequence[str], focus: str, subject: str, target: str
) -> str:
    """
    Mandate line — what is asked, about what, for whom.

    A double request is announced as such: hiding it would deliver one of the
    two parts without saying so.
    """
    parts = [SHORT_MANDATE[goal] for goal in objectives if goal in SHORT_MANDATE]
    if len(parts) > 1:
        statement = f"{parts[0]}, then {parts[1]}"
    elif parts:
        statement = parts[0]
    else:
        statement = SHORT_MANDATE.get(objective, "answer")

    scope = _scope(focus, subject, target)
    if scope:
        statement = f"{statement} — {scope}"

    recipient = TARGET_LABEL.get(target, "not identified")
    return f"Mandate: {statement}. Audience: {recipient}."


def _quantified_target(measures: Mapping[str, Any]) -> str:
    """
    Measurable markers found in the request, or nothing.

    No value is assumed: what was not stated is not invented. A missing target
    is corrected by a question, not by a number.
    """
    segments = []
    direction = DIRECTION_LABEL.get(measures.get("direction"))
    if direction:
        segments.append(direction)
    if measures.get("quantity"):
        segments.append(str(measures["quantity"]))
    if measures.get("deadline"):
        segments.append(f"by {measures['deadline']}")
    return "Target: " + ", ".join(segments) + "." if segments else ""


def _executive_summary(
    objective: str,
    objectives: Sequence[str],
    focus: str,
    subject: str,
    target: str,
    depth: str,
    capabilities: Sequence[str],
    constraints: Sequence[str],
    measures: Mapping[str, Any],
) -> str:
    """
    Executive summary — three to five lines, decision-oriented.

    Mandate, stake, imposed bounds if any, approach, expected decision. The
    decision always closes the summary: it is what the reader must take away.
    """
    lines = [
        _mandate(objective, objectives, focus, subject, target),
        STAKE.get(depth, STAKE["standard"]),
    ]
    quantified = _quantified_target(measures)
    if quantified:
        lines.append(quantified)
    if constraints:
        lines.append(f"Constraints: {_enumerate(constraints)}.")

    approaches = [
        CAPABILITY_APPROACH[capability]
        for capability in capabilities
        if capability in CAPABILITY_APPROACH
    ][:MAX_APPROACHES]
    if approaches:
        lines.append(f"Approach: {_enumerate(approaches)}.")

    decision = DECISION.get(objective, "Decision needed: approve the direction.")
    return "\n".join(lines[: MAX_SUMMARY_LINES - 1] + [decision])


def _analysis(
    objectives: Sequence[str],
    focus: str,
    subject: str,
    target: str,
    tone: str,
    depth: str,
    template: str,
    constraints: Sequence[str],
) -> str:
    """
    Consulting analysis — observation, implication, impact.

    One movement per line. The observation states without interpreting, the
    implication draws the handling constraint, the impact the consequence on
    the deliverable.
    """
    parts = [SHORT_MANDATE[goal] for goal in objectives if goal in SHORT_MANDATE]
    if len(parts) > 1:
        head = f"Two-part mandate: {parts[0]}, then {parts[1]}."
    else:
        head = f"Mandate: {parts[0] if parts else 'answer'}."

    facts = [head]
    scope = _scope(focus, subject, target) or SUBJECT_LABEL.get(subject)
    if scope:
        facts.append(f"Focus: {scope}.")
    facts.append(f"Audience: {DESTINATION.get(target, 'not identified')}.")
    facts.append(f"Depth: {DEPTH_LABEL.get(depth, 'standard')}.")
    observation = "Observation. " + " ".join(facts)

    implication = "Implication. " + " ".join(
        (
            IMPLICATION_BY_TARGET.get(target, IMPLICATION_BY_TARGET["undetermined"]),
            IMPLICATION_BY_DEPTH.get(depth, IMPLICATION_BY_DEPTH["standard"]),
        )
    )

    consequences = [
        IMPACT_BY_FORMAT.get(template, IMPACT_BY_FORMAT["paragraph"]),
        IMPACT_BY_TONE.get(tone, IMPACT_BY_TONE["neutral"]),
    ]
    if constraints:
        consequences.append(
            f"The stated constraints ({_enumerate(constraints)}) take priority over any "
            "formatting preference."
        )
    impact = "Impact. " + " ".join(consequences)

    return "\n".join((observation, implication, impact))


def _recommendation_pool(
    objective: str, target: str, depth: str, template: str, constraints: Sequence[str]
) -> list[str | None]:
    """
    Action pool beyond capabilities — container, bounds, depth, mandate.

    The order follows the signal hierarchy. The baseline closes the list: it
    only guarantees the floor, never replaces a real signal.
    """
    pool: list[str | None] = [FORMAT_ACTION.get(template)]
    pool.extend(CONSTRAINT_ACTION.get(constraint) for constraint in constraints)
    pool.append(DEPTH_ACTION.get(depth))
    pool.append(OBJECTIVE_ACTION.get(objective))
    pool.append(TARGET_ACTION.get(target))
    pool.extend(BASELINE_ACTIONS)
    return pool


def render_output(agent_frame: Any) -> dict[str, Any]:
    """
    Project the assembled frame into a structured consulting deliverable.

    Reads `agent_frame["frame"]` only — never the raw request, which is not in
    it. Every rendered sentence derives from a frame signal; no business
    content is added and no decision is taken here.

    Composition
        executive_summary — three to five lines: mandate, stake, bounds,
                            approach, expected decision.
        analysis          — observation, implication, impact.
        recommendations   — three to seven imperative actions. Capabilities
                            come first, then container, bounds, depth,
                            objective and target.

    The input is never mutated; `meta` is copied rather than shared.
    Returns the keys of `RENDER_KEYS`, always present.
    """
    envelope = agent_frame if isinstance(agent_frame, dict) else {}
    frame = envelope.get("frame")
    frame = frame if isinstance(frame, dict) else {}
    meta = envelope.get("meta")
    meta = dict(meta) if isinstance(meta, dict) else {}

    objective = frame.get("objective") or "answer"
    target = frame.get("target") or "undetermined"
    subject = frame.get("subject") or "undetermined"
    tone = frame.get("tone") or "neutral"
    depth = frame.get("depth") or "standard"
    constraints = list(frame.get("constraints") or ())
    capabilities = list(frame.get("capabilities") or ())
    template = frame.get("format") or "paragraph"
    objectives = list(frame.get("objectives") or (objective,))
    focus = frame.get("focus") or ""
    measures = frame.get("measures")
    measures = measures if isinstance(measures, dict) else {}

    stated_constraints = [
        CONSTRAINT_LABEL.get(constraint, constraint) for constraint in constraints
    ]

    executive_summary = _executive_summary(
        objective,
        objectives,
        focus,
        subject,
        target,
        depth,
        capabilities,
        stated_constraints,
        measures,
    )
    analysis = _analysis(
        objectives, focus, subject, target, tone, depth, template, stated_constraints
    )

    engaged = [CAPABILITY_ACTION.get(capability) for capability in capabilities]
    if any(measures.values()):
        engaged.append(MEASURE_ACTION)
    complement = _recommendation_pool(objective, target, depth, template, constraints)
    recommendations = _unique(engaged + complement)[:MAX_RECOMMENDATIONS]
    if len(recommendations) < MIN_RECOMMENDATIONS:
        recommendations = _unique(recommendations + list(BASELINE_ACTIONS))[:MIN_RECOMMENDATIONS]

    return {
        "executive_summary": executive_summary,
        "analysis": analysis,
        "recommendations": recommendations,
        "format": template,
        "meta": meta,
    }
