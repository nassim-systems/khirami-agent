"""
Frame-driven decisions — capabilities, render format and content rules.

Every function here reads the frame returned by `interpret()` and nothing
else: the raw request is never read again. They are pure and deterministic,
and independent of the language the request was written in.

`orchestrate_frame()` juxtaposes the three decisions; `run_agent()` wraps the
result in a stable envelope consumed by `render_output()`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

# ----------------------------------------------------------------------
# Capabilities.
# ----------------------------------------------------------------------
CANONICAL_CAPABILITIES: tuple[str, ...] = (
    "analysis",
    "synthesis",
    "action_planning",
    "formatting",
    "summary",
    "deep_dive",
    "client_care",
    "executive_framing",
    "verification",
)
DEFAULT_CAPABILITY: str = "analysis"

CAPABILITIES_BY_OBJECTIVE: Mapping[str, tuple[str, ...]] = {
    "analyze": ("analysis",),
    "plan": ("action_planning",),
    "produce": ("analysis", "synthesis"),
    "summarize": ("summary", "synthesis"),
    "explain": ("synthesis",),
    "decide": ("analysis", "executive_framing"),
    "verify": ("verification",),
    "answer": (),
}


def select_capabilities(request_frame: Mapping[str, Any]) -> list[str]:
    """
    Select the business capabilities a frame calls for.

    Rules
        each objective         → `CAPABILITIES_BY_OBJECTIVE`
        target "client"        → client_care + action_planning
        target "team"          → analysis
        target "system"        → verification
        tone "executive"       → executive_framing + verification
        tone "direct"          → formatting
        depth "in_depth"       → deep_dive
        depth "condensed"      → summary
        constraint "precision" → verification
        constraint "brevity"   → summary

    Returns a list without duplicates, always ordered by
    `CANONICAL_CAPABILITIES`. With no signal at all it falls back to
    `["analysis"]`: returning nothing would leave the caller without a grip.
    """
    objective = request_frame.get("objective")
    objectives = request_frame.get("objectives") or ([objective] if objective else [])
    target = request_frame.get("target")
    tone = request_frame.get("tone")
    depth = request_frame.get("depth")
    constraints = set(request_frame.get("constraints") or ())

    selected: set[str] = set()

    for goal in objectives:
        selected.update(CAPABILITIES_BY_OBJECTIVE.get(goal, ()))

    if target == "client":
        selected.update(("client_care", "action_planning"))
    elif target == "team":
        selected.add("analysis")
    elif target == "system":
        selected.add("verification")

    if tone == "executive":
        selected.update(("executive_framing", "verification"))
    elif tone == "direct":
        selected.add("formatting")

    if depth == "in_depth":
        selected.add("deep_dive")
    elif depth == "condensed":
        selected.add("summary")

    if "precision" in constraints:
        selected.add("verification")
    if "brevity" in constraints:
        selected.add("summary")

    if not selected:
        return [DEFAULT_CAPABILITY]

    return [capability for capability in CANONICAL_CAPABILITIES if capability in selected]


# ----------------------------------------------------------------------
# Render format.
# ----------------------------------------------------------------------
CANONICAL_FORMATS: tuple[str, ...] = (
    "bullet_points",
    "paragraph",
    "executive_summary",
    "action_plan",
    "table",
    "email",
    "brief",
)
DEFAULT_FORMAT: str = "paragraph"

# Objectives whose container is beyond doubt: what is produced decides the
# form more than the register. `analyze` and `explain` are absent — they fit a
# note as well as running text, so tone and depth still decide for them.
CONTAINER_BY_OBJECTIVE: Mapping[str, str] = {
    "plan": "action_plan",
    "verify": "table",
    "summarize": "executive_summary",
    "decide": "executive_summary",
}


def select_format(request_frame: Mapping[str, Any]) -> str:
    """
    Select the render format a frame calls for.

    Strict priority: signals are examined in this order and the first one that
    answers closes the question.

        1. constraint "brevity"               → brief
        2. constraint "precision"             → table
        3. target client + executive tone     → email
        4. objective                          → `CONTAINER_BY_OBJECTIVE`
        5. tone                               → executive: executive_summary
                                                direct:    bullet_points
        6. depth                              → condensed: executive_summary
                                                in_depth:  paragraph
        7. target                             → client: action_plan
                                                team:   bullet_points
                                                system: table
        8. objective "produce"                → paragraph

    Constraints come first because the requester states them explicitly,
    whereas tone and depth are inferred. Rank 3 precedes tone alone: a client
    addressed in an executive register calls for a message, not a note. On a
    double request, the container of the most committing objective wins — a
    plan absorbs the diagnosis behind it, not the reverse.

    Returns one of `CANONICAL_FORMATS`. With no signal the fallback is
    `paragraph`, the container that presupposes the least.
    """
    constraints = set(request_frame.get("constraints") or ())

    if "brevity" in constraints:
        return "brief"
    if "precision" in constraints:
        return "table"

    target = request_frame.get("target")
    tone = request_frame.get("tone")

    if target == "client" and tone == "executive":
        return "email"

    objectives = request_frame.get("objectives") or [request_frame.get("objective")]
    for goal in ("plan", "verify", "summarize", "decide"):
        if goal in objectives:
            return CONTAINER_BY_OBJECTIVE[goal]

    if tone == "executive":
        return "executive_summary"
    if tone == "direct":
        return "bullet_points"

    depth = request_frame.get("depth")
    if depth == "condensed":
        return "executive_summary"
    if depth == "in_depth":
        return "paragraph"

    if target == "client":
        return "action_plan"
    if target == "team":
        return "bullet_points"
    if target == "system":
        return "table"

    if request_frame.get("objective") == "produce":
        return "paragraph"

    return DEFAULT_FORMAT


# ----------------------------------------------------------------------
# Content rules.
# ----------------------------------------------------------------------
BREVITY_WORD_LIMIT: int = 80
WORD_LIMIT: int = 120
MAX_BULLETS: int = 5

BULLETS_CONSTRAINT: str = "max-bullets"
WORDS_CONSTRAINT: str = "word-limit"

RULED_DEPTHS: tuple[str, ...] = ("condensed", "in_depth")
RULED_TONES: tuple[str, ...] = ("executive", "direct")


def enforce_rules(request_frame: Mapping[str, Any]) -> dict[str, Any]:
    """
    Prepare the quantified rules to apply to the final content.

    Rules
        constraint "brevity"     → max_words 80, brevity True
        constraint "precision"   → precision True
        constraint "max-bullets" → max_bullets 5
        constraint "word-limit"  → max_words 120
        depth condensed/in_depth → depth set to that value
        tone executive/direct    → tone set to that value

    Conflicts
        Only one word bound is returned. "brevity" wins over "word-limit": the
        stricter bound prevails.

    Returns a six-key dictionary, every key always present. A rule that is not
    triggered is None or False, never missing.
    """
    constraints = set(request_frame.get("constraints") or ())
    depth = request_frame.get("depth")
    tone = request_frame.get("tone")

    if "brevity" in constraints:
        max_words = BREVITY_WORD_LIMIT
    elif WORDS_CONSTRAINT in constraints:
        max_words = WORD_LIMIT
    else:
        max_words = None

    return {
        "max_words": max_words,
        "max_bullets": MAX_BULLETS if BULLETS_CONSTRAINT in constraints else None,
        "precision": "precision" in constraints,
        "brevity": "brevity" in constraints,
        "depth": depth if depth in RULED_DEPTHS else None,
        "tone": tone if tone in RULED_TONES else None,
    }


# ----------------------------------------------------------------------
# Assembly.
# ----------------------------------------------------------------------
ASSEMBLY_KEYS: tuple[str, ...] = (
    "objective",
    "objectives",
    "subject",
    "focus",
    "measures",
    "target",
    "tone",
    "depth",
    "constraints",
    "capabilities",
    "format",
    "rules",
)


def orchestrate_frame(request_frame: Mapping[str, Any]) -> dict[str, Any]:
    """
    Assemble the three decisions into one flat dictionary.

    Assembles and nothing more: the decisions belong to `select_capabilities()`,
    `select_format()` and `enforce_rules()`. The frame is copied, never
    mutated, and the returned dictionary holds no mutable reference to it.

    Returns the keys of `ASSEMBLY_KEYS`, always present. A value missing from
    the frame becomes an empty string, list or dict rather than a missing key.
    """
    return {
        "objective": request_frame.get("objective", ""),
        "objectives": list(request_frame.get("objectives") or ()),
        "subject": request_frame.get("subject", ""),
        "focus": request_frame.get("focus", ""),
        "measures": dict(request_frame.get("measures") or {}),
        "target": request_frame.get("target", ""),
        "tone": request_frame.get("tone", ""),
        "depth": request_frame.get("depth", ""),
        "constraints": list(request_frame.get("constraints") or ()),
        "capabilities": select_capabilities(request_frame),
        "format": select_format(request_frame),
        "rules": enforce_rules(request_frame),
    }


DELIVERABLE_STATUS: str = "ok"
STACK_VERSION: str = "v2"
DELIVERABLE_KEYS: tuple[str, ...] = ("frame", "status", "version", "meta")


def run_agent(request_frame: Mapping[str, Any]) -> dict[str, Any]:
    """
    Wrap the assembled frame in a stable envelope for the renderer.

    `status` and `version` are declarative constants, not computed verdicts.
    `meta` is rebuilt on every call, so a caller that mutates it cannot
    contaminate the next call. The frame received is never mutated.

    Returns the keys of `DELIVERABLE_KEYS`, always present.
    """
    return {
        "frame": orchestrate_frame(request_frame),
        "status": DELIVERABLE_STATUS,
        "version": STACK_VERSION,
        "meta": {
            "non_regression": True,
            "deterministic": True,
        },
    }
