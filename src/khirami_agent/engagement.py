"""
Consulting engagement pipeline.

Carries the consulting work end to end — routing, intake, clarification,
diagnostic, process, automation, strategy, guard — around one state object
that each stage enriches.

    INPUT → ROUTER → INTAKE → CLARIFICATION GATE → DIAGNOSTIC → PROCESS
          → AUTOMATION → STRATEGY → GUARD

Positioning
    Khirami diagnoses a business situation, redesigns a process, then decides
    what deserves to be automated — in that order. It is not a technical
    agent: no stage produces code, configuration or engineering detail, and
    the guard flags anything that drifts into that register.

Three rules shape the whole
    1. Process before automation. The automation stage only sees the *target*
       flow produced by the process stage: a broken process is never automated.
    2. Every recommendation is traceable. Each action points to a root cause, a
       bottleneck or an automation candidate identified upstream.
    3. No invented figure. An estimate is labelled as such and carries the
       assumption it rests on.

Purity and injection
    Each model-backed stage is a function `run_xxx(state, client=None) -> state`.
    The model is injected as `client(system_prompt, task_prompt) -> str` and is
    never built here: this module makes no network call of its own. Without a
    client, stages return a structurally complete but empty block and declare
    the gap in `meta.degraded` — absence is named, never filled by invention.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from . import lexicons
from .framing import interpret
from .prompts import (
    PROMPT_AUTOMATION,
    PROMPT_CLARIFY,
    PROMPT_DIAGNOSTIC,
    PROMPT_GUARD,
    PROMPT_PROCESS,
    PROMPT_STRATEGY,
    SYSTEM_PROMPT,
    fill_prompt,
)
from .text import fold

ModelClient = Callable[[str, str], str]

# ----------------------------------------------------------------------
# Execution modes — each mode maps to a distinct service offer.
# ----------------------------------------------------------------------
MODES: Mapping[str, tuple[str, ...]] = {
    "quick_scan": ("diagnostic", "strategy"),
    "full_audit": ("diagnostic", "process", "automation", "strategy", "guard"),
    "automation_focus": ("process", "automation", "strategy"),
    "follow_up": ("strategy",),
}
DEFAULT_MODE: str = "full_audit"
DEFAULT_OUTPUT_LANGUAGE: str = "en"

# In quick_scan the deliverable is deliberately partial: what is missing is
# the argument for the full version.
QUICK_SCAN_FIELDS: tuple[str, ...] = (
    "executive_summary",
    "key_findings",
    "next_step",
)

# ----------------------------------------------------------------------
# Sector reference tables — loaded by the router before the diagnostic.
# ----------------------------------------------------------------------
SECTOR_TABLES: Mapping[str, Mapping[str, Any]] = {
    "sales": {
        "domain": "sales",
        "levers": ("qualification", "follow-up", "proposal", "closing"),
        "common_frictions": (
            "manual follow-ups",
            "uneven qualification",
            "information scattered across sales reps",
        ),
    },
    "support": {
        "domain": "support",
        "levers": ("triage", "first response", "escalation", "resolution"),
        "common_frictions": (
            "manual triage of requests",
            "answers rewritten every time",
            "escalation without explicit criteria",
        ),
    },
    "operations": {
        "domain": "operations",
        "levers": ("planning", "execution", "control", "reporting"),
        "common_frictions": (
            "re-entry between tools",
            "sequential approvals",
            "reporting rebuilt by hand",
        ),
    },
    "recruiting": {
        "domain": "recruiting",
        "levers": ("sourcing", "screening", "interview", "decision"),
        "common_frictions": (
            "manual screening of applications",
            "slow responses to candidates",
            "implicit evaluation criteria",
        ),
    },
    "administration": {
        "domain": "administration",
        "levers": ("collection", "data entry", "verification", "archiving"),
        "common_frictions": (
            "double data entry",
            "missing documents detected late",
            "unclear approval circuit",
        ),
    },
    "general": {
        "domain": "general",
        "levers": ("framing", "execution", "control"),
        "common_frictions": (),
    },
}
DEFAULT_SECTOR: str = "general"

# ----------------------------------------------------------------------
# Deterministic guardrails — first pass of the quality guard.
#
# Vocabulary that betrays a drift into the technical register. A consulting
# deliverable contains none of it: a technical symptom must have been
# translated into its business consequence long before reaching this point.
# ----------------------------------------------------------------------
OFF_REGISTER_TERMS: tuple[str, ...] = (
    "test case",
    "unit test",
    "assert",
    "bug",
    "regression",
    "selector",
    "endpoint",
    "stack trace",
    "repository",
    "deploy",
    "code snippet",
    "debug",
    "commit",
    "merge request",
    "pull request",
)

HYPE_TERMS: tuple[str, ...] = lexicons.HYPE_TERMS

REQUIRED_STRATEGY_FIELDS: tuple[str, ...] = (
    "executive_summary",
    "situation",
    "key_findings",
    "action_plan",
    "kpis",
    "risks",
    "next_step",
)

HORIZONS: tuple[str, ...] = ("now", "next", "later")

CLARIFICATION_THRESHOLD: str = "low"
MAX_QUESTIONS: int = 2

# A senior consultant asks one targeted question, not a questionnaire.
QUESTION_BY_GAP: Mapping[str, str] = {
    "objective": "What concrete outcome do you expect from this engagement?",
    "recipient": "Who is this work primarily intended for?",
    "scope": "What exact scope do you want us to work on?",
    "volumes": "What volumes or frequencies do you observe today?",
    "context": "Can you describe the situation in a few sentences?",
    "language": "In which language do you want the deliverable?",
}

ASSUMPTION_BY_GAP: Mapping[str, str] = {
    "objective": "assumed objective: clarify the situation before deciding",
    "recipient": "assumed recipient: the internal team concerned",
    "scope": "assumed scope: the process described in the request",
    "volumes": "volumes not quantified: no quantified estimate will be put forward",
    "context": "assumed context: limited to what is written",
    "language": "assumed output language: the language of the request",
}


# ----------------------------------------------------------------------
# Data contract.
# ----------------------------------------------------------------------
@dataclass
class EngagementMeta:
    """Engagement metadata — set by the router, completed along the way."""

    engagement_id: str = ""
    mode: str = DEFAULT_MODE
    sector_table: str = DEFAULT_SECTOR
    output_language: str = DEFAULT_OUTPUT_LANGUAGE
    created_at: str = ""
    guard_status: str = "pending"
    degraded: list[str] = field(default_factory=list)


@dataclass
class EngagementState:
    """
    The single object that travels through the whole pipeline.

    Each stage receives it, adds its block and returns it. No stage reads the
    raw output of another: it only reads the structured block that stage left.
    That is what makes each stage testable in isolation, without replaying the
    previous ones.
    """

    raw_input: str = ""
    business_context: dict[str, Any] = field(default_factory=dict)
    meta: EngagementMeta = field(default_factory=EngagementMeta)

    interpretation: dict[str, Any] | None = None
    clarification: dict[str, Any] | None = None
    diagnostic: dict[str, Any] | None = None
    process_map: dict[str, Any] | None = None
    automation_plan: dict[str, Any] | None = None
    strategy: dict[str, Any] | None = None
    audit: dict[str, Any] | None = None


# ----------------------------------------------------------------------
# Model call — injected, never built here.
# ----------------------------------------------------------------------
def _normalized_words(text: str) -> str:
    """Lower-case, accent-folded text, punctuation neutralized, bordered by spaces."""
    folded = fold(str(text or ""))
    return " " + " ".join("".join(c if c.isalnum() else " " for c in folded).split()) + " "


def _call_model(
    client: ModelClient | None,
    prompt: str,
    language: str,
    block: str,
    degraded: list[str],
) -> dict[str, Any] | None:
    """
    Query the model and return the expected JSON block.

    One retry on invalid JSON, with the error in context. On the second
    failure the gap is declared in `degraded` and nothing is returned: a silent
    partial deliverable would be worse than an announced gap.

    Without an injected client no invention is attempted — the gap is
    declared the same way.
    """
    if client is None:
        degraded.append(f"{block}: no generation client configured")
        return None

    system = fill_prompt(SYSTEM_PROMPT, {"output_language": language})
    request = prompt
    for attempt in range(2):
        try:
            raw = client(system, request)
            payload = json.loads(raw)
            if isinstance(payload, dict):
                return payload
            raise ValueError("expected a JSON object")
        except Exception as error:  # noqa: BLE001 — the reason is relayed, not hidden
            if attempt == 0:
                request = (
                    prompt
                    + "\n\nYour previous answer could not be parsed: "
                    + str(error)
                    + "\nReturn only the JSON object, nothing else."
                )
                continue
            degraded.append(f"{block}: unusable response ({error})")
    return None


def _to_json(value: Any) -> str:
    """Stable serialization, readable by the model."""
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


# ----------------------------------------------------------------------
# ROUTER — mode, sector table, output language. Runs before intake.
# ----------------------------------------------------------------------
def _elect(corpus: str, markers: Mapping[str, tuple[str, ...]]) -> str | None:
    """Category with the most markers; none on a tie or when nothing matches."""
    scores = {
        key: total
        for key, words in markers.items()
        if (total := sum(1 for word in words if f" {word} " in corpus))
    }
    if not scores:
        return None
    top = max(scores.values())
    leaders = [key for key, total in scores.items() if total == top]
    return leaders[0] if len(leaders) == 1 else None


def route(state: EngagementState, mode: str | None = None) -> EngagementState:
    """
    Set the execution mode, the sector table and the output language.

    The mode can be imposed by the caller — the common case, since it matches
    the offer sold. Otherwise it is inferred from the request, and
    `full_audit` remains the fallback: a complete run beats a run truncated by
    a misreading.

    The sector decides which reference table is loaded before the diagnostic.
    Without a clear signal, the general table applies: no sector benchmark is
    assumed.
    """
    corpus = _normalized_words(state.raw_input)

    selected = mode if mode in MODES else _elect(corpus, lexicons.ENGAGEMENT_MODE_MARKERS)
    state.meta.mode = selected or DEFAULT_MODE

    sector = state.business_context.get("sector")
    if sector not in SECTOR_TABLES:
        sector = _elect(corpus, lexicons.SECTOR_MARKERS)
    state.meta.sector_table = sector or DEFAULT_SECTOR

    if not state.meta.output_language:
        state.meta.output_language = DEFAULT_OUTPUT_LANGUAGE
    return state


# ----------------------------------------------------------------------
# INTAKE
# ----------------------------------------------------------------------
def run_intake(state: EngagementState) -> EngagementState:
    """
    Turn a messy client message into a structured business intent.

    Diagnoses nothing: this is framing. The `confidence` and `missing_info`
    produced here drive the clarification gate that follows.
    """
    state.interpretation = dict(interpret(state.raw_input))
    return state


# ----------------------------------------------------------------------
# CLARIFICATION GATE
# ----------------------------------------------------------------------
def run_gate(state: EngagementState, client: ModelClient | None = None) -> EngagementState:
    """
    Decide whether Khirami can conclude, or must ask a question first.

    Triggered when `confidence == "low"`. Two questions at most, never a form:
    a senior consultant asks one targeted question. When it can proceed on an
    explicit assumption it does — and the assumption is recorded, not hidden.

    An injected client refines the questions; without one, the gate still
    works on the gaps already named by the framing.
    """
    framing = state.interpretation or {}
    missing = list(framing.get("missing_info") or ())
    confidence = framing.get("confidence", "high")

    if confidence != CLARIFICATION_THRESHOLD:
        state.clarification = {
            "ready": True,
            "questions": [],
            "assumptions_if_proceeding": [
                ASSUMPTION_BY_GAP[gap] for gap in missing if gap in ASSUMPTION_BY_GAP
            ],
        }
        return state

    questions = [QUESTION_BY_GAP[gap] for gap in missing if gap in QUESTION_BY_GAP][:MAX_QUESTIONS]
    remaining = missing[MAX_QUESTIONS:]

    state.clarification = {
        "ready": not questions,
        "questions": questions,
        "assumptions_if_proceeding": [
            ASSUMPTION_BY_GAP[gap] for gap in remaining if gap in ASSUMPTION_BY_GAP
        ],
    }

    refined = _call_model(
        client,
        fill_prompt(
            PROMPT_CLARIFY,
            {
                "raw_input": state.raw_input,
                "interpretation_json": _to_json(framing),
            },
        ),
        state.meta.output_language,
        "clarification",
        state.meta.degraded,
    )
    if refined:
        state.clarification = {
            "ready": bool(refined.get("ready", False)),
            "questions": list(refined.get("questions") or ())[:MAX_QUESTIONS],
            "assumptions_if_proceeding": list(refined.get("assumptions_if_proceeding") or ()),
        }
    return state


# ----------------------------------------------------------------------
# DIAGNOSTIC
# ----------------------------------------------------------------------
MAX_ROOT_CAUSES: int = 3


def _empty_diagnostic() -> dict[str, Any]:
    return {
        "symptoms": [],
        "root_causes": [],
        "priority_ranking": [],
        "business_impact": {
            "summary": "",
            "estimated_cost_of_inaction": "",
            "estimate_basis": "",
        },
        "assumptions": [],
        "unknowns_that_would_change_this": [],
    }


def run_diagnostic(state: EngagementState, client: ModelClient | None = None) -> EngagementState:
    """
    Separate symptoms from root causes, size the impact, prioritize.

    Three root causes at most: a diagnosis that lists eight is an inventory,
    not a diagnosis. Selectivity is the seniority signal, and the cap is
    enforced here rather than left to the model.
    """
    block = _call_model(
        client,
        fill_prompt(
            PROMPT_DIAGNOSTIC,
            {
                "business_context": _to_json(state.business_context),
                "interpretation_json": _to_json(state.interpretation or {}),
                "sector_table": _to_json(SECTOR_TABLES[state.meta.sector_table]),
            },
        ),
        state.meta.output_language,
        "diagnostic",
        state.meta.degraded,
    )

    diagnostic = _empty_diagnostic()
    if block:
        diagnostic.update({key: block[key] for key in diagnostic if key in block})
        diagnostic["root_causes"] = list(diagnostic["root_causes"])[:MAX_ROOT_CAUSES]
        known = {cause.get("id") for cause in diagnostic["root_causes"]}
        diagnostic["priority_ranking"] = [
            identifier for identifier in diagnostic["priority_ranking"] if identifier in known
        ]
    state.diagnostic = diagnostic
    return state


# ----------------------------------------------------------------------
# PROCESS OPTIMIZATION
# ----------------------------------------------------------------------
def _empty_process() -> dict[str, Any]:
    return {
        "current_flow": [],
        "bottlenecks": [],
        "target_flow": [],
        "leverage_points": [],
        "quick_wins": [],
        "structural_changes": [],
    }


def run_process(state: EngagementState, client: ModelClient | None = None) -> EngagementState:
    """
    Map the actual flow, locate the frictions, design the target flow.

    The target flow must be shorter or cleaner than the current one: the same
    flow with digital tools is not an optimization. Every bottleneck points to
    a root cause of the diagnostic; orphan links are dropped here, before they
    contaminate the automation stage.
    """
    block = _call_model(
        client,
        fill_prompt(
            PROMPT_PROCESS,
            {
                "interpretation_json": _to_json(state.interpretation or {}),
                "diagnostic_json": _to_json(state.diagnostic or {}),
            },
        ),
        state.meta.output_language,
        "process_map",
        state.meta.degraded,
    )

    process_map = _empty_process()
    if block:
        process_map.update({key: block[key] for key in process_map if key in block})
        root_causes = {cause.get("id") for cause in (state.diagnostic or {}).get("root_causes", ())}
        process_map["bottlenecks"] = [
            bottleneck
            for bottleneck in process_map["bottlenecks"]
            if not root_causes or bottleneck.get("linked_root_cause") in root_causes
        ]
    state.process_map = process_map
    return state


# ----------------------------------------------------------------------
# AUTOMATION
# ----------------------------------------------------------------------
def _empty_automation() -> dict[str, Any]:
    return {
        "candidates": [],
        "do_not_automate": [],
        "sequence": [],
        "dependencies": [],
    }


MECHANISMS: frozenset[str] = frozenset(("rules_workflow", "ai_agent", "hybrid", "keep_human"))


def run_automation(state: EngagementState, client: ModelClient | None = None) -> EngagementState:
    """
    Decide what to automate, with which mechanism, and what stays human.

    Only sees the *target* flow: a step the process stage removed must never be
    automated. That rule is what gives the stage order its meaning — a broken
    process is never automated.

    The `do_not_automate` section is mandatory. Knowing when to say "we leave
    this alone" is the mark of a consultant, not of a tool vendor: when it
    comes back empty, the gap is declared.
    """
    target_flow = (state.process_map or {}).get("target_flow", [])

    block = _call_model(
        client,
        fill_prompt(
            PROMPT_AUTOMATION,
            {
                "diagnostic_json": _to_json(state.diagnostic or {}),
                "target_flow_json": _to_json(target_flow),
                "constraints": _to_json((state.interpretation or {}).get("constraints", [])),
            },
        ),
        state.meta.output_language,
        "automation_plan",
        state.meta.degraded,
    )

    plan = _empty_automation()
    if block:
        plan.update({key: block[key] for key in plan if key in block})
        plan["candidates"] = [
            candidate
            for candidate in plan["candidates"]
            if candidate.get("mechanism") in MECHANISMS
        ]
        known = {candidate.get("id") for candidate in plan["candidates"]}
        plan["sequence"] = [identifier for identifier in plan["sequence"] if identifier in known]
        if not plan["do_not_automate"]:
            state.meta.degraded.append("automation_plan: do_not_automate section missing")
    state.automation_plan = plan
    return state


# ----------------------------------------------------------------------
# STRATEGY OUTPUT
# ----------------------------------------------------------------------
def _empty_strategy() -> dict[str, Any]:
    return {
        "executive_summary": "",
        "situation": "",
        "key_findings": [],
        "action_plan": {horizon: [] for horizon in HORIZONS},
        "kpis": [],
        "expected_outcomes": [],
        "risks": [],
        "next_step": "",
    }


def run_strategy(state: EngagementState, client: ModelClient | None = None) -> EngagementState:
    """
    Turn everything upstream into a decision-ready consulting deliverable.

    The strategy stage synthesizes, it does not invent: nothing appears here
    that was not established upstream. In `quick_scan` the deliverable is
    deliberately reduced to the summary, the findings and the next step — the
    gap is assumed, not a silent degradation.
    """
    block = _call_model(
        client,
        fill_prompt(
            PROMPT_STRATEGY,
            {
                "diagnostic_json": _to_json(state.diagnostic or {}),
                "process_json": _to_json(state.process_map or {}),
                "automation_json": _to_json(state.automation_plan or {}),
                "business_context": _to_json(state.business_context),
            },
        ),
        state.meta.output_language,
        "strategy",
        state.meta.degraded,
    )

    strategy = _empty_strategy()
    if block:
        strategy.update({key: block[key] for key in strategy if key in block})
        plan = strategy["action_plan"]
        strategy["action_plan"] = {
            horizon: list(plan.get(horizon) or ()) if isinstance(plan, dict) else []
            for horizon in HORIZONS
        }

    if state.meta.mode == "quick_scan":
        reduced = _empty_strategy()
        for name in QUICK_SCAN_FIELDS:
            reduced[name] = strategy[name]
        strategy = reduced

    state.strategy = strategy
    return state


# ----------------------------------------------------------------------
# CONSULTANT GUARD
# ----------------------------------------------------------------------
def _upstream_ids(state: EngagementState) -> set[str]:
    """Every identifier established upstream — the only legitimate anchors."""
    upstream = {cause.get("id") for cause in (state.diagnostic or {}).get("root_causes", ())}
    upstream |= {
        bottleneck.get("id") for bottleneck in (state.process_map or {}).get("bottlenecks", ())
    }
    upstream |= {
        candidate.get("id") for candidate in (state.automation_plan or {}).get("candidates", ())
    }
    return {identifier for identifier in upstream if identifier}


def _deliverable_text(strategy: Mapping[str, Any]) -> str:
    """Flatten the deliverable for the lexical checks."""
    return _to_json(strategy).lower()


def run_guard(state: EngagementState, client: ModelClient | None = None) -> EngagementState:
    """
    Audit the deliverable before it is sent. It does not write: it validates
    and corrects.

    Two passes, in this order. The deterministic pass — off-register
    vocabulary, hype, required fields, traceability — handles most cases
    without any model call. The model pass only runs when the first pass found
    something, which spares a full call in the common case.

    One correction attempt only. Beyond that, the deliverable is flagged for
    human review rather than corrected in a loop.
    """
    strategy = state.strategy or _empty_strategy()
    violations: list[dict[str, str]] = []

    def flag(rule: str, location: str, fix: str) -> None:
        violations.append({"rule": rule, "location": location, "fix": fix})

    text = _deliverable_text(strategy)

    for term in OFF_REGISTER_TERMS:
        if term in text:
            flag("register", term, "translate the technical symptom into its business consequence")
    for term in HYPE_TERMS:
        if term in text:
            flag("hype", term, "replace the value claim with its evidence")

    for name in REQUIRED_STRATEGY_FIELDS:
        value = strategy.get(name)
        if value in (None, "", [], {}):
            flag("completeness", name, "required field missing from the deliverable")

    upstream = _upstream_ids(state)
    plan = strategy.get("action_plan") or {}
    for horizon in HORIZONS:
        for action in plan.get(horizon) or ():
            anchor = action.get("linked_to")
            if upstream and anchor not in upstream:
                flag(
                    "traceability",
                    f"action_plan.{horizon}",
                    "link the action to an upstream root cause, bottleneck or candidate",
                )
            if not action.get("owner_role"):
                flag("vagueness", f"action_plan.{horizon}", "name an owner")
            if not action.get("done_when"):
                flag("vagueness", f"action_plan.{horizon}", "set a verifiable done-condition")

    corrected: dict[str, Any] = {}
    if violations:
        model_audit = _call_model(
            client,
            fill_prompt(
                PROMPT_GUARD,
                {
                    "strategy_json": _to_json(strategy),
                    "diagnostic_json": _to_json(state.diagnostic or {}),
                    "process_json": _to_json(state.process_map or {}),
                    "automation_json": _to_json(state.automation_plan or {}),
                },
            ),
            state.meta.output_language,
            "audit",
            state.meta.degraded,
        )
        if model_audit:
            proposed = model_audit.get("corrected_deliverable") or {}
            if isinstance(proposed, dict) and proposed:
                corrected = proposed
                state.strategy = proposed

    if not violations:
        state.meta.guard_status = "pass"
    else:
        state.meta.guard_status = "corrected" if corrected else "pending"
    state.audit = {
        "pass": not violations,
        "violations": violations,
        "corrected_deliverable": corrected,
    }
    return state


# ----------------------------------------------------------------------
# Full pipeline.
# ----------------------------------------------------------------------
STAGES: Mapping[str, Callable[..., EngagementState]] = {
    "diagnostic": run_diagnostic,
    "process": run_process,
    "automation": run_automation,
    "strategy": run_strategy,
    "guard": run_guard,
}


def run_engagement(
    raw_input: str,
    business_context: Mapping[str, Any] | None = None,
    client: ModelClient | None = None,
    mode: str | None = None,
    engagement_id: str = "",
    created_at: str = "",
    output_language: str = "",
) -> EngagementState:
    """
    Run the engagement end to end.

    The mode decides which stages run; the clarification gate can stop the
    run before the diagnostic, in which case the state is returned as is,
    questions included, to resume once the client has answered.

    The returned state is complete whatever the path: a stage that did not run
    leaves its block at `None`, never half filled.
    """
    state = EngagementState(
        raw_input=raw_input or "",
        business_context=dict(business_context or {}),
        meta=EngagementMeta(
            engagement_id=engagement_id,
            created_at=created_at,
            output_language=output_language or DEFAULT_OUTPUT_LANGUAGE,
        ),
    )

    route(state, mode)
    run_intake(state)
    run_gate(state, client)

    if not (state.clarification or {}).get("ready", True):
        return state

    for stage in MODES[state.meta.mode]:
        STAGES[stage](state, client)

    return state
