"""
Unit tests for `render_output(agent_frame)`.

Tests the consulting renderer only. What it projects is covered by
test_orchestrate_frame.py and test_run_agent.py; here we check the projection.

Contract: the input is the dictionary `run_agent()` returns. The output
carries five keys, always present: executive_summary, analysis,
recommendations, format, meta.

`render_output()` and `generate_output()` are independent renderers; the last
test guards that rendering one leaves the other working.
"""

from __future__ import annotations

import pytest

from khirami_agent import KhiramiAgent, generate_output, interpret, run_agent
from khirami_agent.rendering import (
    MAX_RECOMMENDATIONS,
    MIN_RECOMMENDATIONS,
    RENDER_KEYS,
    render_output,
)

MAX_SUMMARY_LINES = 5

# The neutral frame: exactly what interpret() returns for an empty request.
NEUTRAL_FRAME = {
    "objective": "answer",
    "target": "undetermined",
    "tone": "neutral",
    "depth": "standard",
    "constraints": [],
}

# A frame with every signal turned on, to exercise the whole projection.
LOADED_FRAME = {
    "objective": "produce",
    "target": "client",
    "tone": "executive",
    "depth": "in_depth",
    "constraints": ["precision", "brevity"],
}

ALL_FRAMES = [NEUTRAL_FRAME, LOADED_FRAME]
FRAME_IDS = ["neutral", "loaded"]


def deliverable(request_frame):
    """The run_agent() envelope for a given framing."""
    return run_agent(request_frame)


# ---------------------------------------------------------------------------
# Behaviour
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("request_frame", ALL_FRAMES, ids=FRAME_IDS)
def test_structure(request_frame):
    """Every key is present, whatever the framing."""
    rendered = render_output(deliverable(request_frame))

    assert set(rendered) == set(RENDER_KEYS), f"unexpected key set: {sorted(rendered)!r}"
    assert isinstance(rendered["executive_summary"], str)
    assert isinstance(rendered["analysis"], str)
    assert isinstance(rendered["recommendations"], list)
    assert isinstance(rendered["format"], str)
    assert isinstance(rendered["meta"], dict)


@pytest.mark.parametrize("request_frame", ALL_FRAMES, ids=FRAME_IDS)
def test_summary_length(request_frame):
    """The executive summary must hold in five lines at most."""
    summary = render_output(deliverable(request_frame))["executive_summary"]
    lines = summary.split("\n")

    assert len(lines) <= MAX_SUMMARY_LINES, f"summary runs to {len(lines)} lines: {summary!r}"
    assert all(line.strip() for line in lines), "the summary holds a blank line"


@pytest.mark.parametrize("request_frame", ALL_FRAMES, ids=FRAME_IDS)
def test_recommendations_count(request_frame):
    """Between three and seven actions, always."""
    recommendations = render_output(deliverable(request_frame))["recommendations"]

    assert MIN_RECOMMENDATIONS <= len(recommendations) <= MAX_RECOMMENDATIONS, (
        f"{len(recommendations)} recommendations: {recommendations!r}"
    )


@pytest.mark.parametrize("request_frame", ALL_FRAMES, ids=FRAME_IDS)
def test_meta_passthrough(request_frame):
    """`meta` is carried over unchanged."""
    envelope = deliverable(request_frame)

    assert render_output(envelope)["meta"] == envelope["meta"]


def test_does_not_mutate_its_input():
    """The envelope received is never modified."""
    envelope = deliverable(LOADED_FRAME)
    original = {
        "frame": {**envelope["frame"], "constraints": list(envelope["frame"]["constraints"])},
        "status": envelope["status"],
        "version": envelope["version"],
        "meta": dict(envelope["meta"]),
    }

    rendered = render_output(envelope)

    assert envelope["frame"] == original["frame"], "render_output() mutated the frame"
    assert envelope["meta"] == original["meta"], "render_output() mutated meta"

    # The carried meta must be a copy, not a shared reference.
    rendered["meta"]["intruder"] = True
    assert envelope["meta"] == original["meta"], "the rendered meta aliases the input"


def test_is_deterministic():
    """Two identical calls must produce the same dict."""
    envelope = deliverable(LOADED_FRAME)

    first = render_output(envelope)
    second = render_output(envelope)

    assert first == second, f"not deterministic: {first!r} then {second!r}"


def test_full_path_from_interpret():
    """Full path: interpret() -> run_agent() -> render_output()."""
    request_frame = interpret("Write a detailed and precise analysis for the client.")

    rendered = render_output(run_agent(request_frame))

    assert set(rendered) == set(RENDER_KEYS)
    assert rendered["executive_summary"].strip()
    assert rendered["analysis"].strip()
    assert MIN_RECOMMENDATIONS <= len(rendered["recommendations"]) <= MAX_RECOMMENDATIONS
    assert rendered["format"] == run_agent(request_frame)["frame"]["format"]


# ---------------------------------------------------------------------------
# Structural guarantees
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("request_frame", ALL_FRAMES, ids=FRAME_IDS)
def test_recommendations_have_no_duplicate(request_frame):
    recommendations = render_output(deliverable(request_frame))["recommendations"]

    assert len(recommendations) == len(set(recommendations)), (
        f"duplicate recommendation in {recommendations!r}"
    )


@pytest.mark.parametrize("request_frame", ALL_FRAMES, ids=FRAME_IDS)
def test_format_mirrors_the_frame(request_frame):
    envelope = deliverable(request_frame)

    assert render_output(envelope)["format"] == envelope["frame"]["format"]


def test_projection_reflects_the_signals():
    """
    Guard against a rendering that ignores its input.

    Two different framings must not produce the same prose.
    """
    neutral = render_output(deliverable(NEUTRAL_FRAME))
    loaded = render_output(deliverable(LOADED_FRAME))

    assert neutral["executive_summary"] != loaded["executive_summary"]
    assert neutral["analysis"] != loaded["analysis"]
    assert neutral["recommendations"] != loaded["recommendations"]


def test_malformed_input_is_handled():
    """A malformed envelope must not raise: every key still comes back."""
    for broken in ({}, {"frame": None}, {"frame": {}, "meta": None}):
        rendered = render_output(broken)

        assert set(rendered) == set(RENDER_KEYS)
        assert MIN_RECOMMENDATIONS <= len(rendered["recommendations"]) <= MAX_RECOMMENDATIONS


def test_plan_renderer_is_unaffected():
    """`generate_output()` must keep rendering the planning path."""
    render_output(deliverable(LOADED_FRAME))

    assert callable(generate_output)
    rendered = KhiramiAgent().run("Write a note for the client.")
    assert isinstance(rendered, str) and rendered, "the plan renderer broke"
