"""
Unit tests for the consulting engagement pipeline.

Scope
-----
- Tests the JSON contracts, not the prose: key presence, types, value ranges,
  and referential integrity between blocks.
- No network. The model client is injected as a stub returning canned JSON,
  which is exactly what makes each stage testable in isolation.

Positioning under test
----------------------
Khirami is a consultant, not an engineer. The guard must flag engineering
register wherever it appears in a deliverable.
"""

from __future__ import annotations

import json

import pytest

from khirami_agent import interpret
from khirami_agent.engagement import (
    HORIZONS,
    MAX_QUESTIONS,
    MAX_ROOT_CAUSES,
    MECHANISMS,
    MODES,
    QUICK_SCAN_FIELDS,
    SECTOR_TABLES,
    EngagementState,
    route,
    run_automation,
    run_diagnostic,
    run_engagement,
    run_gate,
    run_guard,
    run_intake,
    run_process,
    run_strategy,
)
from khirami_agent.prompts import SYSTEM_PROMPT, fill_prompt

# ---------------------------------------------------------------------------
# FIXTURES — canned blocks, shaped exactly like the contracts.
# ---------------------------------------------------------------------------

DEMAND = (
    "Our customer service is saturated: requests pile up, follow-ups are done by "
    "hand and the team spends its days re-sorting tickets. We want a diagnosis "
    "and an action plan."
)

DIAGNOSTIC_OK = {
    "symptoms": [{"observation": "response times rising", "source": "stated"}],
    "root_causes": [
        {
            "id": "RC1",
            "cause": "request triage is not standardized",
            "evidence_chain": "delays -> manual re-sorting -> no triage rule",
            "impact": 4,
            "effort": 2,
            "confidence": "medium",
        },
        {
            "id": "RC2",
            "cause": "follow-ups left to individual initiative",
            "evidence_chain": "manual follow-ups -> omissions -> reopened requests",
            "impact": 3,
            "effort": 2,
            "confidence": "medium",
        },
    ],
    "priority_ranking": ["RC1", "RC2"],
    "business_impact": {
        "summary": "handling capacity absorbed by rework",
        "estimated_cost_of_inaction": "estimate: one person-day per week",
        "estimate_basis": "assumption, to be confirmed with actual volumes",
    },
    "assumptions": ["volumes not provided"],
    "unknowns_that_would_change_this": ["number of requests per week"],
}

PROCESS_OK = {
    "current_flow": [
        {
            "step": "request received",
            "owner": "support",
            "status": "stated",
            "friction": "manual triage",
        }
    ],
    "bottlenecks": [
        {
            "id": "B1",
            "description": "manual triage on every arrival",
            "linked_root_cause": "RC1",
            "cost": "handling time doubled",
        }
    ],
    "target_flow": [
        {"step": "triage on an explicit rule", "owner": "support", "change": "standardised"}
    ],
    "leverage_points": [
        {
            "action": "publish the triage rule",
            "expected_gain": "less rework",
            "gain_basis": "estimate, to be measured over one month",
            "linked_bottleneck": "B1",
        }
    ],
    "quick_wins": ["formalize the triage rule"],
    "structural_changes": ["rethink how accounts are split across the team"],
}

AUTOMATION_OK = {
    "candidates": [
        {
            "id": "A1",
            "task": "triage of incoming requests",
            "mechanism": "rules_workflow",
            "why_this_mechanism": "deterministic criteria, high volume",
            "expected_gain": "shorter triage time",
            "gain_basis": "estimate, to be measured",
            "effort": "low",
            "prerequisites": ["triage rule approved by the support lead"],
            "risk": "misrouting if the rule is incomplete",
        }
    ],
    "do_not_automate": [
        {
            "task": "answering dissatisfied clients",
            "reason": "relationship exposure, judgement required",
        }
    ],
    "sequence": ["A1"],
    "dependencies": [],
}

STRATEGY_OK = {
    "executive_summary": "Manual triage absorbs the support team's capacity.",
    "situation": "Requests pile up for lack of a shared triage rule.",
    "key_findings": [{"finding": "triage not standardized", "linked_root_cause": "RC1"}],
    "action_plan": {
        "now": [
            {
                "action": "formalize the triage rule",
                "owner_role": "support lead",
                "done_when": "rule written and shared",
                "linked_to": "RC1",
            }
        ],
        "next": [
            {
                "action": "tool the triage on the rule",
                "owner_role": "support lead",
                "done_when": "triage applied with no manual rework",
                "linked_to": "B1",
            }
        ],
        "later": [
            {
                "action": "extend the setup to follow-ups",
                "owner_role": "head of customer service",
                "done_when": "follow-ups triggered without intervention",
                "linked_to": "A1",
            }
        ],
    },
    "kpis": [
        {
            "metric": "first response time",
            "baseline_needed": "four weeks of measurement",
            "target_direction": "decreasing",
        }
    ],
    "expected_outcomes": [{"outcome": "less rework", "basis": "manual re-sorting removed"}],
    "risks": [{"risk": "incomplete triage rule", "mitigation": "monthly review"}],
    "next_step": "meet the support lead to write the triage rule.",
}

BLOCKS = {
    "diagnostic": DIAGNOSTIC_OK,
    "process": PROCESS_OK,
    "automation": AUTOMATION_OK,
    "strategy": STRATEGY_OK,
}


def client_stub(blocks=None):
    """
    A model client that answers with canned JSON.

    It routes on a marker present in each task prompt, so one stub serves the
    whole pipeline without knowing anything about it.
    """
    table = {**BLOCKS, **(blocks or {})}

    def _call(system, prompt):
        assert "senior AI consultant" in system, "identity was not injected"
        if "TASK: Produce the diagnostic" in prompt:
            return json.dumps(table["diagnostic"])
        if "TASK: Map the current process" in prompt:
            return json.dumps(table["process"])
        if "TASK: Design the automation" in prompt:
            return json.dumps(table["automation"])
        if "TASK: Write the consulting deliverable" in prompt:
            return json.dumps(table["strategy"])
        if "TASK: Audit this deliverable" in prompt:
            return json.dumps(
                table.get("guard", {"pass": True, "violations": [], "corrected_deliverable": {}})
            )
        if "TASK: Decide whether you can produce" in prompt:
            return json.dumps(
                table.get(
                    "clarify",
                    {"ready": True, "questions": [], "assumptions_if_proceeding": []},
                )
            )
        raise AssertionError(f"unexpected prompt: {prompt[:60]}")

    return _call


@pytest.fixture
def client():
    return client_stub()


def framed_state(mode="full_audit", demand=DEMAND):
    state = EngagementState(raw_input=demand)
    route(state, mode)
    run_intake(state)
    return state


# ---------------------------------------------------------------------------
# INTAKE — the framing carries confidence and missing_info
# ---------------------------------------------------------------------------


def test_interpret_exposes_confidence_and_missing_info():
    frame = interpret(DEMAND)

    assert frame["confidence"] in ("high", "medium", "low")
    assert isinstance(frame["missing_info"], list)
    assert all(isinstance(gap, str) for gap in frame["missing_info"])


def test_confidence_degrades_as_information_disappears():
    rich = interpret(DEMAND)["confidence"]
    poor = interpret("help")["confidence"]

    order = {"high": 2, "medium": 1, "low": 0}
    assert order[poor] <= order[rich]


def test_missing_info_names_what_is_absent():
    frame = interpret("help")

    assert frame["missing_info"], "a bare request must declare what it lacks"
    assert frame["confidence"] == "low"


# ---------------------------------------------------------------------------
# ROUTER
# ---------------------------------------------------------------------------


def test_router_sets_mode_sector_and_language():
    state = EngagementState(raw_input=DEMAND)
    route(state)

    assert state.meta.mode in MODES
    assert state.meta.sector_table in SECTOR_TABLES
    assert state.meta.output_language


def test_router_honours_an_explicit_mode():
    state = EngagementState(raw_input=DEMAND)
    route(state, "quick_scan")

    assert state.meta.mode == "quick_scan"


def test_router_detects_the_business_sector():
    state = EngagementState(raw_input=DEMAND)
    route(state)

    assert state.meta.sector_table == "support"


def test_router_falls_back_to_the_general_table():
    state = EngagementState(raw_input="xyzzy plugh")
    route(state)

    assert state.meta.sector_table == "general"


# ---------------------------------------------------------------------------
# CLARIFICATION GATE
# ---------------------------------------------------------------------------


def test_gate_lets_a_framed_demand_through():
    state = framed_state()
    run_gate(state)

    assert state.clarification["ready"] is True
    assert state.clarification["questions"] == []


def test_gate_asks_at_most_two_questions():
    state = EngagementState(raw_input="help")
    route(state)
    run_intake(state)
    run_gate(state)

    assert len(state.clarification["questions"]) <= MAX_QUESTIONS


def test_gate_records_assumptions_rather_than_guessing():
    state = framed_state()
    run_gate(state)

    assert isinstance(state.clarification["assumptions_if_proceeding"], list)


# ---------------------------------------------------------------------------
# DIAGNOSTIC
# ---------------------------------------------------------------------------


def test_diagnostic_contract(client):
    state = run_diagnostic(framed_state(), client)
    block = state.diagnostic

    assert set(block) == {
        "symptoms",
        "root_causes",
        "priority_ranking",
        "business_impact",
        "assumptions",
        "unknowns_that_would_change_this",
    }
    assert set(block["business_impact"]) == {
        "summary",
        "estimated_cost_of_inaction",
        "estimate_basis",
    }


def test_diagnostic_scores_stay_in_range(client):
    state = run_diagnostic(framed_state(), client)

    for cause in state.diagnostic["root_causes"]:
        assert 1 <= cause["impact"] <= 5
        assert 1 <= cause["effort"] <= 5
        assert cause["confidence"] in ("high", "medium", "low")


def test_diagnostic_keeps_three_root_causes_at_most():
    too_many = {**DIAGNOSTIC_OK}
    too_many["root_causes"] = [
        {**DIAGNOSTIC_OK["root_causes"][0], "id": f"RC{n}"} for n in range(1, 8)
    ]
    too_many["priority_ranking"] = [f"RC{n}" for n in range(1, 8)]

    state = run_diagnostic(framed_state(), client_stub({"diagnostic": too_many}))

    assert len(state.diagnostic["root_causes"]) <= MAX_ROOT_CAUSES


def test_priority_ranking_only_cites_known_causes(client):
    state = run_diagnostic(framed_state(), client)
    known = {cause["id"] for cause in state.diagnostic["root_causes"]}

    assert set(state.diagnostic["priority_ranking"]) <= known


# ---------------------------------------------------------------------------
# PROCESS
# ---------------------------------------------------------------------------


def test_process_contract(client):
    state = run_process(run_diagnostic(framed_state(), client), client)
    block = state.process_map

    assert set(block) == {
        "current_flow",
        "bottlenecks",
        "target_flow",
        "leverage_points",
        "quick_wins",
        "structural_changes",
    }


def test_bottlenecks_link_to_an_existing_root_cause(client):
    state = run_process(run_diagnostic(framed_state(), client), client)
    root_causes = {cause["id"] for cause in state.diagnostic["root_causes"]}

    for bottleneck in state.process_map["bottlenecks"]:
        assert bottleneck["linked_root_cause"] in root_causes


def test_orphan_bottlenecks_are_dropped(client):
    broken = {**PROCESS_OK}
    broken["bottlenecks"] = [
        {"id": "B9", "description": "", "linked_root_cause": "RC99", "cost": ""}
    ]

    state = run_process(run_diagnostic(framed_state(), client), client_stub({"process": broken}))

    assert state.process_map["bottlenecks"] == []


# ---------------------------------------------------------------------------
# AUTOMATION
# ---------------------------------------------------------------------------


def prepared(client):
    return run_process(run_diagnostic(framed_state(), client), client)


def test_automation_contract(client):
    state = run_automation(prepared(client), client)
    block = state.automation_plan

    assert set(block) == {
        "candidates",
        "do_not_automate",
        "sequence",
        "dependencies",
    }


def test_every_mechanism_is_a_known_one(client):
    state = run_automation(prepared(client), client)

    for candidate in state.automation_plan["candidates"]:
        assert candidate["mechanism"] in MECHANISMS


def test_do_not_automate_is_mandatory(client):
    state = run_automation(prepared(client), client)

    assert state.automation_plan["do_not_automate"], (
        "knowing what to leave alone is the consultant's mark"
    )


def test_an_empty_do_not_automate_is_declared_as_a_gap(client):
    empty = {**AUTOMATION_OK, "do_not_automate": []}
    state = run_automation(prepared(client), client_stub({"automation": empty}))

    assert any("do_not_automate" in note for note in state.meta.degraded)


def test_automation_reads_the_target_flow_only(client):
    """The prompt must carry the target flow, never the current one."""
    seen = []

    def spy(system, prompt):
        seen.append(prompt)
        return client(system, prompt)

    run_automation(prepared(client), spy)
    prompt = "\n".join(seen)

    assert "triage on an explicit rule" in prompt, "target flow missing from the prompt"
    assert "request received" not in prompt, "current flow leaked into the automation stage"


# ---------------------------------------------------------------------------
# STRATEGY
# ---------------------------------------------------------------------------


def automated(client):
    return run_automation(prepared(client), client)


def test_strategy_contract(client):
    state = run_strategy(automated(client), client)
    block = state.strategy

    assert set(block) == {
        "executive_summary",
        "situation",
        "key_findings",
        "action_plan",
        "kpis",
        "expected_outcomes",
        "risks",
        "next_step",
    }
    assert set(block["action_plan"]) == set(HORIZONS)


def test_every_action_carries_a_role_and_a_done_condition(client):
    state = run_strategy(automated(client), client)

    for horizon in HORIZONS:
        for action in state.strategy["action_plan"][horizon]:
            assert action["owner_role"]
            assert action["done_when"]
            assert action["linked_to"]


def test_quick_scan_delivers_a_deliberately_partial_deliverable(client):
    state = automated(client)
    state.meta.mode = "quick_scan"
    run_strategy(state, client)

    for name in QUICK_SCAN_FIELDS:
        assert state.strategy[name], f"{name} should survive the quick scan"
    assert state.strategy["kpis"] == []
    assert state.strategy["risks"] == []


# ---------------------------------------------------------------------------
# GUARD
# ---------------------------------------------------------------------------


def test_guard_passes_a_clean_deliverable(client):
    state = run_guard(run_strategy(automated(client), client), client)

    assert state.audit["pass"] is True
    assert state.audit["violations"] == []
    assert state.meta.guard_status == "pass"


def test_guard_flags_engineering_register(client):
    drift = {**STRATEGY_OK, "situation": "The endpoint is down and the stack trace is empty."}
    state = automated(client)
    state.strategy = drift
    run_guard(state, client_stub({"strategy": drift}))

    rules = {violation["rule"] for violation in state.audit["violations"]}
    assert "register" in rules, "engineering register must never reach the client"


def test_guard_flags_hype(client):
    hype = {**STRATEGY_OK, "executive_summary": "A seamless, game-changing solution."}
    state = automated(client)
    state.strategy = hype
    run_guard(state, client_stub({"strategy": hype}))

    rules = {violation["rule"] for violation in state.audit["violations"]}
    assert "hype" in rules


def test_guard_flags_an_orphan_action(client):
    orphan = json.loads(json.dumps(STRATEGY_OK))
    orphan["action_plan"]["now"][0]["linked_to"] = "RC99"

    state = automated(client)
    state.strategy = orphan
    run_guard(state, client_stub({"strategy": orphan}))

    rules = {violation["rule"] for violation in state.audit["violations"]}
    assert "traceability" in rules


def test_guard_flags_a_missing_owner(client):
    vague = json.loads(json.dumps(STRATEGY_OK))
    vague["action_plan"]["now"][0]["owner_role"] = ""

    state = automated(client)
    state.strategy = vague
    run_guard(state, client_stub({"strategy": vague}))

    rules = {violation["rule"] for violation in state.audit["violations"]}
    assert "vagueness" in rules


def test_guard_flags_an_incomplete_deliverable(client):
    truncated = {**STRATEGY_OK, "next_step": ""}

    state = automated(client)
    state.strategy = truncated
    run_guard(state, client_stub({"strategy": truncated}))

    rules = {violation["rule"] for violation in state.audit["violations"]}
    assert "completeness" in rules


def test_guard_does_not_call_the_model_on_a_clean_deliverable(client):
    """The deterministic pass must spare the model call in the common case."""
    calls = []

    def spy(system, prompt):
        calls.append(prompt)
        return client(system, prompt)

    state = run_strategy(automated(client), client)
    calls.clear()
    run_guard(state, spy)

    assert calls == [], "a clean deliverable must not trigger a model call"


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def test_full_pipeline_fills_every_block(client):
    state = run_engagement(DEMAND, {"sector": "support"}, client, "full_audit")

    assert state.interpretation is not None
    assert state.clarification is not None
    assert state.diagnostic is not None
    assert state.process_map is not None
    assert state.automation_plan is not None
    assert state.strategy is not None
    assert state.audit is not None


@pytest.mark.parametrize("mode", sorted(MODES), ids=sorted(MODES))
def test_every_mode_runs_end_to_end(client, mode):
    state = run_engagement(DEMAND, {}, client, mode)

    assert state.meta.mode == mode
    assert state.strategy is not None


def test_automation_focus_skips_the_diagnostic(client):
    state = run_engagement(DEMAND, {}, client, "automation_focus")

    assert state.diagnostic is None
    assert state.process_map is not None
    assert state.automation_plan is not None


def test_pipeline_pauses_when_the_gate_is_not_ready(client):
    state = run_engagement(
        "help",
        {},
        client_stub(
            {
                "clarify": {
                    "ready": False,
                    "questions": ["What outcome do you expect?"],
                    "assumptions_if_proceeding": [],
                }
            }
        ),
    )

    assert state.clarification["ready"] is False
    assert state.diagnostic is None, "nothing runs before the framing is settled"


def test_pipeline_without_a_client_declares_the_gap():
    state = run_engagement(DEMAND, {}, None, "full_audit")

    assert state.meta.degraded, "a missing model client must be declared"
    assert state.strategy is not None, "the contract holds even when empty"
    assert state.strategy["executive_summary"] == "", "nothing is invented"


def test_pipeline_is_deterministic(client):
    first = run_engagement(DEMAND, {}, client, "full_audit")
    second = run_engagement(DEMAND, {}, client, "full_audit")

    assert first.strategy == second.strategy
    assert first.diagnostic == second.diagnostic


def test_invalid_json_is_retried_then_declared():
    calls = []

    def unstable(system, prompt):
        calls.append(prompt)
        return "not json at all"

    state = EngagementState(raw_input=DEMAND)
    route(state, "full_audit")
    run_intake(state)
    run_diagnostic(state, unstable)

    assert len(calls) == 2, "exactly one retry, then the gap is declared"
    assert any("diagnostic" in note for note in state.meta.degraded)
    assert state.diagnostic["root_causes"] == []


# ---------------------------------------------------------------------------
# Positioning
# ---------------------------------------------------------------------------


def test_identity_forbids_the_engineering_posture():
    system = fill_prompt(SYSTEM_PROMPT, {"output_language": "en"})

    assert "consultant, not an engineer" in system
    assert "Never invent numbers" in system
    assert "<<output_language>>" not in system, "placeholder left unresolved"


def test_no_engineering_vocabulary_in_the_sector_tables():
    tables = json.dumps(SECTOR_TABLES, ensure_ascii=False).lower()

    for term in ("test case", "endpoint", "stack trace", "deploy", "debug"):
        assert term not in tables


# ---------------------------------------------------------------------------
# Router - regression tests on accented input
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw_input", "expected_sector"),
    [
        ("Une réclamation client à traiter en urgence.", "support"),
        ("La comptabilité déborde chaque fin de mois.", "administration"),
    ],
    ids=["accented-support", "accented-administration"],
)
def test_router_matches_accented_markers(raw_input, expected_sector):
    """Accented spellings used to be missed: the router did not fold accents."""
    state = EngagementState(raw_input=raw_input)
    route(state)

    assert state.meta.sector_table == expected_sector


def test_router_still_matches_unaccented_markers():
    state = EngagementState(raw_input="Une reclamation client a traiter en urgence.")
    route(state)

    assert state.meta.sector_table == "support"
