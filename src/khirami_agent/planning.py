"""
Deliverable planning — from a request to a structured deliverable plan.

`orchestrate()` runs four steps:

    interpret() → _select_plan_capabilities() → _select_template()
    → _apply_plan_rules()

The plan it returns is the input contract of `generate_output()`:
`response` (status, format, sections, register, notices, scope boundary),
`violations` and `tensions`.

This path uses its own capability vocabulary (framing, research, writing,
review…), distinct from the business capabilities of `selection.py`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .framing import interpret

PLAN_CAPABILITY_ORDER: tuple[str, ...] = (
    "framing",
    "research",
    "analysis",
    "arbitration",
    "planning",
    "production",
    "synthesis",
    "structuring",
    "writing",
    "review",
)
PLAN_CAPABILITIES_BY_OBJECTIVE: Mapping[str, tuple[str, ...]] = {
    "analyze": ("analysis", "structuring", "writing"),
    "plan": ("analysis", "planning", "structuring", "writing"),
    "produce": ("production", "structuring"),
    "summarize": ("synthesis", "writing"),
    "explain": ("structuring", "writing"),
    "decide": ("analysis", "arbitration", "writing"),
    "verify": ("analysis", "structuring", "writing"),
    "answer": ("writing",),
}
EXPANSIVE_CAPABILITIES: frozenset[str] = frozenset(("research", "arbitration"))

TEMPLATE_BY_OBJECTIVE: Mapping[str, str] = {
    "analyze": "analysis",
    "plan": "plan",
    "summarize": "synthesis",
    "explain": "direct_answer",
    "decide": "synthesis",
    "verify": "checklist",
    "answer": "direct_answer",
}
WIDER_TEMPLATE: Mapping[str, str] = {
    "direct_answer": "synthesis",
    "synthesis": "analysis",
    "analysis": "report",
    "list": "checklist",
}
NARROWER_TEMPLATE: Mapping[str, str] = {
    "report": "synthesis",
    "analysis": "synthesis",
    "plan": "synthesis",
    "synthesis": "direct_answer",
    "checklist": "list",
}
LOCKED_TEMPLATES: frozenset[str] = frozenset(("code",))

# (section id, role, optional)
SECTIONS_BY_TEMPLATE: Mapping[str, tuple[tuple[str, str, bool], ...]] = {
    "analysis": (
        ("framing", "scope and question addressed", False),
        ("established_facts", "what is observed, without interpretation", False),
        ("dynamics", "underlying mechanisms and causes", False),
        ("tension_points", "frictions and blind spots", True),
        ("prioritization", "ranking by impact", False),
        ("uncertainties", "assumptions and confidence level", True),
    ),
    "synthesis": (
        ("key_message", "the conclusion, up front", False),
        ("supporting_points", "the supporting points, few in number", False),
        ("trade_offs", "implications and choices made", True),
        ("set_aside", "what was deliberately left out", True),
    ),
    "plan": (
        ("objective", "target outcome and success criterion", False),
        ("sequencing", "steps and dependencies", False),
        ("milestones", "time horizons and checkpoints", True),
        ("resources", "means and responsibilities", True),
        ("risks", "anticipated risks and mitigations", False),
        ("decision_points", "where to correct the course", True),
    ),
    "report": (
        ("executive_summary", "what to decide, from page one", False),
        ("context_and_mandate", "origin and scope of the work", False),
        ("method_and_sources", "how the work was conducted", True),
        ("findings", "detailed results", False),
        ("options", "possibilities and the related trade-offs", True),
        ("recommendation", "a reasoned position, kept separate from the findings", False),
        ("implementation", "conditions of execution", True),
        ("appendices", "supporting evidence", True),
    ),
    "checklist": (
        ("scope", "what it covers and when to use it", False),
        ("checkpoints", "verifiable items, in order", False),
        ("criteria", "unambiguous validation", False),
        ("blockers", "blockers versus points to watch", True),
        ("owners", "who is responsible for what", True),
    ),
    "code": (
        ("artifact", "the technical deliverable itself", False),
        ("structure_notes", "architecture choices made", True),
    ),
    "list": (("items", "homogeneous, ranked items", False),),
    "direct_answer": (
        ("answer", "the answer, up front", False),
        ("support", "supporting evidence, if needed", True),
    ),
}
OUT_OF_SCOPE_SECTIONS: frozenset[str] = frozenset(
    ("options", "sources", "recommendation", "appendices", "implementation")
)

TONE_REGISTER: Mapping[str, str] = {
    "technical": "technical: exact vocabulary, no emphasis",
    "executive": "executive: ready to forward as is",
    "educational": "educational: progressive, no undefined jargon",
    "direct": "direct: no ceremony",
    "neutral": "neutral",
}
DEPTH_REGISTER: Mapping[str, str] = {
    "condensed": "condensed",
    "standard": "standard",
    "in_depth": "in depth",
}
NOTICE_BY_CONSTRAINT: Mapping[str, str] = {
    "precision": "every statement stays tied to its source",
    "restricted_scope": "work limited to the requested scope",
    "no_implementation": "structural output: no functional logic",
    "brevity": "optional sections dropped for brevity",
    "language": "output language imposed by the request",
}


def _select_plan_capabilities(interpretation: Mapping[str, Any]) -> list[str]:
    """
    Select the execution capabilities used by the plan.

    The objective sets the base; target and depth adjust it. Review is always
    included. The result is ordered by execution dependency.
    """
    objective = interpretation.get("objective", "answer")
    objectives = interpretation.get("objectives") or [objective]
    target = interpretation.get("target", "undetermined")
    depth = interpretation.get("depth", "standard")
    constraints = set(interpretation.get("constraints") or ())

    selected: set[str] = set()
    for goal in objectives:
        selected.update(
            PLAN_CAPABILITIES_BY_OBJECTIVE.get(goal, PLAN_CAPABILITIES_BY_OBJECTIVE["answer"])
        )
    if target == "undetermined":
        selected.add("framing")
    if "precision" in constraints:
        selected.add("research")
    if depth == "in_depth":
        selected.add("analysis")
    elif depth == "condensed":
        selected.add("synthesis")
        selected.discard("structuring")
    selected.add("review")

    return [capability for capability in PLAN_CAPABILITY_ORDER if capability in selected]


def _select_template(interpretation: Mapping[str, Any]) -> dict[str, Any]:
    """
    Select the deliverable template and its sections.

    The objective picks a template; depth moves it by one step at most. Each
    section is marked optional or not — that marking is what makes the later
    clean-up decidable.
    """
    objective = interpretation.get("objective", "answer")
    target = interpretation.get("target", "undetermined")
    depth = interpretation.get("depth", "standard")
    constraints = set(interpretation.get("constraints") or ())

    if objective == "produce":
        template = "code" if target == "system" else "report"
    else:
        template = TEMPLATE_BY_OBJECTIVE.get(objective, "direct_answer")

    if template not in LOCKED_TEMPLATES:
        if depth == "in_depth":
            template = WIDER_TEMPLATE.get(template, template)
        elif depth == "condensed":
            template = NARROWER_TEMPLATE.get(template, template)

    sections = [
        {"id": identifier, "role": role, "optional": optional}
        for identifier, role, optional in SECTIONS_BY_TEMPLATE[template]
    ]
    known = {section["id"] for section in sections}

    if target == "undetermined":
        sections.insert(
            0,
            {
                "id": "open_questions",
                "role": "what must be settled before real work starts",
                "optional": False,
            },
        )
    if "precision" in constraints and "sources" not in known:
        sections.append(
            {
                "id": "sources",
                "role": "origin and reliability of each element put forward",
                "optional": False,
            }
        )

    return {"format": template, "sections": sections}


def _apply_plan_rules(plan: Mapping[str, Any]) -> dict[str, Any]:
    """
    Apply tone, depth and constraints, then clean the plan up.

    Constraints remove what they forbid, never the reverse. Tensions between
    requirements are exposed, not arbitrated. Returns the final plan, matching
    the input contract of `generate_output()`.
    """
    interpretation = dict(plan.get("interpretation") or {})
    tone = interpretation.get("tone", "neutral")
    depth = interpretation.get("depth", "standard")
    constraints = set(interpretation.get("constraints") or ())

    capabilities = list(plan.get("capabilities") or ())
    sections = [dict(section) for section in (plan.get("sections") or ())]
    template = plan.get("format", "direct_answer")

    scope = "no restriction stated"
    if "restricted_scope" in constraints:
        scope = "scope limited to the request: nothing beyond what is explicitly asked"
        capabilities = [c for c in capabilities if c not in EXPANSIVE_CAPABILITIES]
        sections = [s for s in sections if s["id"] not in OUT_OF_SCOPE_SECTIONS]

    if "no_implementation" in constraints:
        for section in sections:
            if section["id"] == "artifact":
                section["role"] = "skeleton only: no functional logic"

    if "brevity" in constraints or depth == "condensed":
        trimmed = [s for s in sections if not s["optional"]]
        if trimmed:
            sections = trimmed

    if "review" not in capabilities:
        capabilities.append("review")

    tensions = []
    if "brevity" in constraints and depth == "in_depth":
        tensions.append("depth and brevity requested together: the trade-off is the user's call")
    if "speed" in constraints and "precision" in constraints:
        tensions.append(
            "precision required under time pressure: the review stays, the deadline moves"
        )
    if "restricted_scope" in constraints and template == "report":
        tensions.append("a full report is expected on an explicitly narrow mandate")
    if "no_implementation" in constraints and template == "code":
        tensions.append(
            "technical artifact expected without functional logic: the output will stay structural"
        )
    if interpretation.get("target") == "undetermined":
        tensions.append("audience not identified: the register still needs confirming")

    violations = []
    if not sections:
        violations.append("no section remains after the constraints are applied")
    if "writing" not in capabilities and "production" not in capabilities:
        violations.append(
            "no writing or production capability selected: nothing would produce the deliverable"
        )

    notices = [
        NOTICE_BY_CONSTRAINT[constraint]
        for constraint in sorted(constraints)
        if constraint in NOTICE_BY_CONSTRAINT
    ]
    notices.append("reviewed before delivery")

    if not sections:
        status = "suspended"
        sections = [
            {
                "id": "non_compliance_finding",
                "role": "the constraints leave nothing of substance to deliver",
            },
            {
                "id": "required_remediations",
                "role": "what must be relaxed to continue",
            },
        ]
    elif violations:
        status = "qualified"
        sections = [{"id": s["id"], "role": s["role"]} for s in sections] + [
            {
                "id": "reservations",
                "role": "inconsistencies found, to resolve before delivery",
            }
        ]
    else:
        status = "compliant"
        sections = [{"id": s["id"], "role": s["role"]} for s in sections]

    return {
        "response": {
            "status": status,
            "format": template,
            "sections": sections,
            "register": {
                "tone": TONE_REGISTER.get(tone, "neutral"),
                "depth": DEPTH_REGISTER.get(depth, "standard"),
                "length": "bounded by the request" if "brevity" in constraints else "free",
            },
            "mandatory_notices": notices,
            "scope_boundary": scope,
        },
        "violations": violations,
        "tensions": tensions,
        "interpretation": interpretation,
        "capabilities": capabilities,
    }


def orchestrate(request: str) -> dict[str, Any]:
    """Run the full planning path for a request and return the final plan."""
    interpretation = interpret(request)
    capabilities = _select_plan_capabilities(interpretation)
    structure = _select_template(interpretation)
    return _apply_plan_rules(
        {
            "interpretation": interpretation,
            "capabilities": capabilities,
            "format": structure["format"],
            "sections": structure["sections"],
        }
    )
