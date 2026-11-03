"""
Unit tests for `select_capabilities(request_frame)`.

Tests the function alone, from hand-built frames: no call to `interpret()`,
no lexicon, no language detection, no I/O.

Contract: the output is a list of canonical capabilities, without duplicates,
always in `CANONICAL_ORDER`. With no signal at all, the selection falls back
to `["analysis"]`.
"""

from __future__ import annotations

import pytest

from khirami_agent import select_capabilities

CANONICAL_ORDER = (
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

# The neutral frame: exactly what interpret() returns for an empty request.
NEUTRAL_FRAME = {
    "objective": "answer",
    "target": "undetermined",
    "tone": "neutral",
    "depth": "standard",
    "constraints": [],
}


def frame(**overrides):
    """A neutral frame with only the signals under test turned on."""
    return {**NEUTRAL_FRAME, **overrides}


# ---------------------------------------------------------------------------
# Behaviour
# ---------------------------------------------------------------------------


def test_detailed_analysis():
    """objective=produce + depth=in_depth -> analysis + deep_dive."""
    capabilities = select_capabilities(frame(objective="produce", depth="in_depth"))

    assert "analysis" in capabilities, f"expected 'analysis' in {capabilities!r}"
    assert "deep_dive" in capabilities, f"expected 'deep_dive' in {capabilities!r}"


def test_brief_summary():
    """depth=condensed + brevity constraint -> summary."""
    capabilities = select_capabilities(frame(depth="condensed", constraints=["brevity"]))

    assert "summary" in capabilities, f"expected 'summary' in {capabilities!r}"


def test_client_action_plan():
    """target=client -> action_planning."""
    capabilities = select_capabilities(frame(target="client"))

    assert "action_planning" in capabilities, f"expected 'action_planning' in {capabilities!r}"


def test_neutral_fallback():
    """No signal at all -> the selection falls back to ["analysis"]."""
    assert select_capabilities(NEUTRAL_FRAME) == ["analysis"]


def test_is_deterministic():
    """Two identical calls must produce the same result."""
    request_frame = frame(
        objective="produce",
        target="client",
        tone="executive",
        depth="in_depth",
        constraints=["precision", "brevity"],
    )

    first = select_capabilities(request_frame)
    second = select_capabilities(request_frame)

    assert first == second, f"not deterministic: {first!r} then {second!r}"


def test_no_duplicates():
    """No capability may appear twice, even when several rules elect the same one."""
    # precision, executive tone and system target all elect "verification";
    # condensed depth and the brevity constraint both elect "summary".
    capabilities = select_capabilities(
        frame(
            objective="produce",
            target="system",
            tone="executive",
            depth="condensed",
            constraints=["precision", "brevity"],
        )
    )

    assert len(capabilities) == len(set(capabilities)), f"duplicate capability in {capabilities!r}"


# ---------------------------------------------------------------------------
# Structural guarantees
# ---------------------------------------------------------------------------


def test_result_is_a_list_of_known_capabilities():
    capabilities = select_capabilities(frame(objective="produce", target="client"))

    assert isinstance(capabilities, list)
    assert set(capabilities) <= set(CANONICAL_ORDER), f"unknown capability in {capabilities!r}"


@pytest.mark.parametrize(
    ("signal", "expected"),
    [
        ({"objective": "produce"}, "synthesis"),
        ({"target": "client"}, "client_care"),
        ({"target": "team"}, "analysis"),
        ({"target": "system"}, "verification"),
        ({"tone": "executive"}, "executive_framing"),
        ({"tone": "direct"}, "formatting"),
        ({"depth": "in_depth"}, "deep_dive"),
        ({"depth": "condensed"}, "summary"),
        ({"constraints": ["precision"]}, "verification"),
        ({"constraints": ["brevity"]}, "summary"),
    ],
    ids=[
        "objective-produce",
        "target-client",
        "target-team",
        "target-system",
        "tone-executive",
        "tone-direct",
        "depth-in-depth",
        "depth-condensed",
        "constraint-precision",
        "constraint-brevity",
    ],
)
def test_every_rule_is_active(signal, expected):
    """Each rule must fire on the canonical values interpret() really produces."""
    capabilities = select_capabilities(frame(**signal))

    assert expected in capabilities, (
        f"rule {signal!r} did not elect {expected!r}, got {capabilities!r}"
    )


def test_order_is_canonical():
    capabilities = select_capabilities(
        frame(
            objective="produce",
            target="client",
            tone="executive",
            depth="in_depth",
            constraints=["precision"],
        )
    )

    ranks = [CANONICAL_ORDER.index(capability) for capability in capabilities]
    assert ranks == sorted(ranks), f"order is not canonical: {capabilities!r}"
