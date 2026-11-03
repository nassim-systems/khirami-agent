"""
Unit tests for `run_agent(request_frame)`.

Tests the top layer of the frame-driven stack only. What it wraps is covered by
test_orchestrate_frame.py; here we check the envelope and the wiring.

Contract: the input is the dictionary `interpret()` returns. The output
carries four keys, always present: `frame` (the assembly), `status`, `version`
and `meta`.
"""

from __future__ import annotations

import pytest

from khirami_agent import KhiramiAgent, interpret, orchestrate, orchestrate_frame, run_agent

DELIVERABLE_KEYS = ("frame", "status", "version", "meta")
META_KEYS = ("non_regression", "deterministic")

EXPECTED_STATUS = "ok"
EXPECTED_VERSION = "v2"

# The neutral frame: exactly what interpret() returns for an empty request.
NEUTRAL_FRAME = {
    "objective": "answer",
    "target": "undetermined",
    "tone": "neutral",
    "depth": "standard",
    "constraints": [],
}

# A frame with every signal turned on, to exercise the whole stack at once.
LOADED_FRAME = {
    "objective": "produce",
    "target": "client",
    "tone": "executive",
    "depth": "in_depth",
    "constraints": ["precision", "brevity"],
}

ALL_FRAMES = [NEUTRAL_FRAME, LOADED_FRAME]
FRAME_IDS = ["neutral", "loaded"]


# ---------------------------------------------------------------------------
# Behaviour
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("request_frame", ALL_FRAMES, ids=FRAME_IDS)
def test_structure(request_frame):
    """Every key is present, whatever the framing."""
    deliverable = run_agent(request_frame)

    assert set(deliverable) == set(DELIVERABLE_KEYS), f"unexpected key set: {sorted(deliverable)!r}"
    assert isinstance(deliverable["frame"], dict)
    assert isinstance(deliverable["status"], str)
    assert isinstance(deliverable["version"], str)
    assert isinstance(deliverable["meta"], dict)
    assert set(deliverable["meta"]) == set(META_KEYS)


@pytest.mark.parametrize("request_frame", ALL_FRAMES, ids=FRAME_IDS)
def test_frame_is_the_orchestrated_frame(request_frame):
    """`frame` is exactly what orchestrate_frame() returns."""
    deliverable = run_agent(request_frame)

    assert deliverable["frame"] == orchestrate_frame(request_frame)


@pytest.mark.parametrize("request_frame", ALL_FRAMES, ids=FRAME_IDS)
def test_status_is_ok(request_frame):
    assert run_agent(request_frame)["status"] == EXPECTED_STATUS


@pytest.mark.parametrize("request_frame", ALL_FRAMES, ids=FRAME_IDS)
def test_version_is_v2(request_frame):
    assert run_agent(request_frame)["version"] == EXPECTED_VERSION


@pytest.mark.parametrize("request_frame", ALL_FRAMES, ids=FRAME_IDS)
def test_meta_flags(request_frame):
    meta = run_agent(request_frame)["meta"]

    assert meta["non_regression"] is True
    assert meta["deterministic"] is True


def test_is_deterministic():
    """Two identical calls must produce the same dict."""
    first = run_agent(LOADED_FRAME)
    second = run_agent(LOADED_FRAME)

    assert first == second, f"not deterministic: {first!r} then {second!r}"


def test_does_not_mutate_its_input():
    """The frame received is never modified, not even its constraint list."""
    request_frame = {**LOADED_FRAME, "constraints": list(LOADED_FRAME["constraints"])}
    original = {**request_frame, "constraints": list(request_frame["constraints"])}

    deliverable = run_agent(request_frame)

    assert request_frame == original, "run_agent() mutated the frame"

    # The carried list must be a copy, not a shared reference.
    deliverable["frame"]["constraints"].append("intruder")
    assert request_frame["constraints"] == original["constraints"], (
        "the assembled list aliases the input list"
    )


# ---------------------------------------------------------------------------
# Structural guarantees
# ---------------------------------------------------------------------------


def test_meta_is_rebuilt_on_every_call():
    """
    Guard against a shared mutable default.

    A caller tampering with `meta` must not corrupt the next call.
    """
    first = run_agent(NEUTRAL_FRAME)
    first["meta"]["non_regression"] = False
    first["meta"]["intruder"] = True

    second = run_agent(NEUTRAL_FRAME)

    assert second["meta"] == {"non_regression": True, "deterministic": True}


def test_frame_is_rebuilt_on_every_call():
    """Two calls must not share the same assembled dict."""
    first = run_agent(NEUTRAL_FRAME)
    second = run_agent(NEUTRAL_FRAME)

    assert first["frame"] is not second["frame"]
    assert first["frame"] == second["frame"]


def test_real_pipeline():
    """Full path: interpret() -> run_agent() -> a coherent deliverable."""
    request_frame = interpret("Write a detailed and precise analysis for the client.")

    deliverable = run_agent(request_frame)

    assert set(deliverable) == set(DELIVERABLE_KEYS)
    assert deliverable["status"] == EXPECTED_STATUS
    assert deliverable["version"] == EXPECTED_VERSION
    assert deliverable["frame"]["objective"] == "produce"
    assert deliverable["frame"]["target"] == "client"
    assert deliverable["frame"]["capabilities"], "no capability selected"
    assert deliverable["frame"]["format"], "no format selected"
    assert deliverable["frame"]["rules"]["precision"] is True


def test_planning_path_is_untouched():
    """`run_agent()` must not disturb the request-driven planning path."""
    run_agent(LOADED_FRAME)

    plan = orchestrate("Write a note for the client.")
    assert "response" in plan, "the planning path no longer returns a plan"

    rendered = KhiramiAgent().run("Write a note for the client.")
    assert isinstance(rendered, str) and rendered, "run() no longer renders text"
