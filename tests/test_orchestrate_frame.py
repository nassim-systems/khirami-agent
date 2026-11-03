"""
Unit tests for `orchestrate_frame(request_frame)`.

Tests the assembly layer only. The three decisions it juxtaposes are covered
by test_capabilities.py, test_format.py and test_rules.py; here we check that
they are wired in faithfully and that nothing else happens.

Naming: the function is `orchestrate_frame()`, not `orchestrate()`. The latter
names the request-driven planning entry point; the two layers must not shadow
each other.
"""

from __future__ import annotations

import pytest

from khirami_agent import (
    enforce_rules,
    interpret,
    orchestrate,
    orchestrate_frame,
    select_capabilities,
    select_format,
)

ASSEMBLY_KEYS = (
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

# Framing fields copied straight from the frame, grouped by the default they
# take when the frame does not carry them. Asserting them apart keeps the next
# added field from slipping through: it has to be declared in one of these.
FRAMING_STRINGS = ("objective", "subject", "focus", "target", "tone", "depth")
FRAMING_LISTS = ("objectives", "constraints")
FRAMING_DICTS = ("measures",)

# The neutral frame: exactly what interpret() returns for an empty request.
NEUTRAL_FRAME = {
    "objective": "answer",
    "objectives": ["answer"],
    "subject": "undetermined",
    "focus": "",
    "measures": {},
    "target": "undetermined",
    "tone": "neutral",
    "depth": "standard",
    "constraints": [],
}

# A frame with every signal turned on, to exercise all three layers at once.
LOADED_FRAME = {
    "objective": "produce",
    "objectives": ["analyze", "produce"],
    "subject": "client",
    "focus": "quarterly report",
    "measures": {},
    "target": "client",
    "tone": "executive",
    "depth": "in_depth",
    "constraints": ["precision", "brevity"],
}


def frame(**overrides):
    """A neutral frame with only the signals under test turned on."""
    return {**NEUTRAL_FRAME, **overrides}


# ---------------------------------------------------------------------------
# Behaviour
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("request_frame", [NEUTRAL_FRAME, LOADED_FRAME], ids=["neutral", "loaded"])
def test_structure(request_frame):
    """Every key is present, whatever the framing."""
    assembled = orchestrate_frame(request_frame)

    assert set(assembled) == set(ASSEMBLY_KEYS), f"unexpected key set: {sorted(assembled)!r}"
    assert isinstance(assembled["constraints"], list)
    assert isinstance(assembled["capabilities"], list)
    assert isinstance(assembled["format"], str)
    assert isinstance(assembled["rules"], dict)


@pytest.mark.parametrize("request_frame", [NEUTRAL_FRAME, LOADED_FRAME], ids=["neutral", "loaded"])
def test_capabilities_are_wired_in(request_frame):
    """`capabilities` is exactly what select_capabilities() returns."""
    assembled = orchestrate_frame(request_frame)

    assert assembled["capabilities"] == select_capabilities(request_frame)


@pytest.mark.parametrize("request_frame", [NEUTRAL_FRAME, LOADED_FRAME], ids=["neutral", "loaded"])
def test_format_is_wired_in(request_frame):
    """`format` is exactly what select_format() returns."""
    assembled = orchestrate_frame(request_frame)

    assert assembled["format"] == select_format(request_frame)


@pytest.mark.parametrize("request_frame", [NEUTRAL_FRAME, LOADED_FRAME], ids=["neutral", "loaded"])
def test_rules_are_wired_in(request_frame):
    """`rules` is exactly what enforce_rules() returns."""
    assembled = orchestrate_frame(request_frame)

    assert assembled["rules"] == enforce_rules(request_frame)


def test_is_deterministic():
    """Two identical calls must produce the same dict."""
    first = orchestrate_frame(LOADED_FRAME)
    second = orchestrate_frame(LOADED_FRAME)

    assert first == second, f"not deterministic: {first!r} then {second!r}"


def test_does_not_mutate_its_input():
    """The frame received is never modified, not even its constraint list."""
    request_frame = {**LOADED_FRAME, "constraints": list(LOADED_FRAME["constraints"])}
    original = {**request_frame, "constraints": list(request_frame["constraints"])}

    assembled = orchestrate_frame(request_frame)

    assert request_frame == original, "orchestrate_frame() mutated the frame"

    # The assembled list must be a copy, not a shared reference.
    assembled["constraints"].append("intruder")
    assert request_frame["constraints"] == original["constraints"], (
        "the assembled list aliases the input list"
    )


def test_real_pipeline():
    """Full path: interpret() -> orchestrate_frame() -> a coherent dict."""
    request = "Write a detailed and precise analysis for the client."

    request_frame = interpret(request)
    assembled = orchestrate_frame(request_frame)

    assert set(assembled) == set(ASSEMBLY_KEYS)

    # The framing is carried over untouched.
    for field in FRAMING_STRINGS:
        assert assembled[field] == request_frame[field], f"field {field!r} was altered"
    for field in FRAMING_LISTS:
        assert assembled[field] == list(request_frame[field]), f"field {field!r} was altered"
    for field in FRAMING_DICTS:
        assert assembled[field] == dict(request_frame[field]), f"field {field!r} was altered"

    # The three decisions agree with a direct call.
    assert assembled["capabilities"] == select_capabilities(request_frame)
    assert assembled["format"] == select_format(request_frame)
    assert assembled["rules"] == enforce_rules(request_frame)

    # And the framing itself is what this request should yield.
    assert assembled["objective"] == "produce"
    assert assembled["target"] == "client"
    assert assembled["depth"] == "in_depth"
    assert "precision" in assembled["constraints"]


# ---------------------------------------------------------------------------
# Structural guarantees
# ---------------------------------------------------------------------------


def test_missing_fields_become_empty_values():
    """A partial frame still yields every key."""
    assembled = orchestrate_frame({})

    assert set(assembled) == set(ASSEMBLY_KEYS)
    for field in FRAMING_STRINGS:
        assert assembled[field] == "", f"{field!r} should default to an empty string"
    for field in FRAMING_LISTS:
        assert assembled[field] == [], f"{field!r} should default to an empty list"
    for field in FRAMING_DICTS:
        assert assembled[field] == {}, f"{field!r} should default to an empty dict"


def test_assembly_adds_no_decision_of_its_own():
    """
    Guard against creeping logic.

    Everything in the output must be traceable either to the frame itself or
    to one of the three delegated calls - nothing is invented in between.
    """
    request_frame = frame(target="team", tone="direct", constraints=["precision"])

    assembled = orchestrate_frame(request_frame)

    assert assembled == {
        "objective": request_frame["objective"],
        "objectives": list(request_frame["objectives"]),
        "subject": request_frame["subject"],
        "focus": request_frame["focus"],
        "measures": dict(request_frame["measures"]),
        "target": request_frame["target"],
        "tone": request_frame["tone"],
        "depth": request_frame["depth"],
        "constraints": list(request_frame["constraints"]),
        "capabilities": select_capabilities(request_frame),
        "format": select_format(request_frame),
        "rules": enforce_rules(request_frame),
    }


def test_does_not_shadow_the_planning_entry_point():
    """`orchestrate()` must still be the request-driven planning entry point."""
    assert orchestrate is not orchestrate_frame
    plan = orchestrate("Write a note for the client.")
    assert "response" in plan, "the planning entry point no longer returns a plan"
