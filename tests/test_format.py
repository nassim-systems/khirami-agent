"""
Unit tests for `select_format(request_frame)`.

Tests the function alone, from hand-built frames, except the last test which
guards against a dead rule through a real `interpret()` call.

Contract: the output is a single canonical format string. When several rules
apply, the strict priority order decides; with no signal at all, the choice
falls back to `"paragraph"`.
"""

from __future__ import annotations

import pytest

from khirami_agent import interpret, select_format

CANONICAL_FORMATS = (
    "bullet_points",
    "paragraph",
    "executive_summary",
    "action_plan",
    "table",
    "email",
    "brief",
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


def test_condensed_depth():
    """depth=condensed -> executive_summary."""
    assert select_format(frame(depth="condensed")) == "executive_summary"


def test_in_depth():
    """depth=in_depth -> paragraph."""
    assert select_format(frame(depth="in_depth")) == "paragraph"


def test_client_target():
    """target=client -> action_plan."""
    assert select_format(frame(target="client")) == "action_plan"


def test_precision_constraint():
    """precision constraint -> table."""
    assert select_format(frame(constraints=["precision"])) == "table"


def test_brevity_constraint():
    """brevity constraint -> brief."""
    assert select_format(frame(constraints=["brevity"])) == "brief"


def test_constraint_outranks_depth():
    """A constraint outranks depth: precision wins over condensed."""
    chosen = select_format(frame(depth="condensed", constraints=["precision"]))

    assert chosen == "table", f"constraint should outrank depth, got {chosen!r}"


def test_neutral_fallback():
    """No signal at all -> paragraph."""
    assert select_format(NEUTRAL_FRAME) == "paragraph"


def test_is_deterministic():
    """Two identical calls must produce the same result."""
    request_frame = frame(
        objective="produce",
        target="client",
        tone="executive",
        depth="in_depth",
        constraints=["precision"],
    )

    first = select_format(request_frame)
    second = select_format(request_frame)

    assert first == second, f"not deterministic: {first!r} then {second!r}"


# ---------------------------------------------------------------------------
# Structural guarantees
# ---------------------------------------------------------------------------


def test_result_is_a_known_format():
    chosen = select_format(frame(objective="produce", target="client"))

    assert isinstance(chosen, str)
    assert chosen in CANONICAL_FORMATS, f"unknown format {chosen!r}"


@pytest.mark.parametrize(
    ("signal", "expected"),
    [
        ({"constraints": ["brevity"]}, "brief"),
        ({"constraints": ["precision"]}, "table"),
        ({"tone": "executive"}, "executive_summary"),
        ({"tone": "direct"}, "bullet_points"),
        ({"depth": "condensed"}, "executive_summary"),
        ({"depth": "in_depth"}, "paragraph"),
        ({"target": "client"}, "action_plan"),
        ({"target": "team"}, "bullet_points"),
        ({"target": "system"}, "table"),
        ({"objective": "produce"}, "paragraph"),
    ],
    ids=[
        "constraint-brevity",
        "constraint-precision",
        "tone-executive",
        "tone-direct",
        "depth-condensed",
        "depth-in-depth",
        "target-client",
        "target-team",
        "target-system",
        "objective-produce",
    ],
)
def test_every_rule_is_active(signal, expected):
    """Each rule must fire on the canonical values interpret() really produces."""
    chosen = select_format(frame(**signal))

    assert chosen == expected, f"rule {signal!r} should yield {expected!r}, got {chosen!r}"


@pytest.mark.parametrize(
    ("weaker", "expected"),
    [
        ({"tone": "executive"}, "brief"),
        ({"depth": "in_depth"}, "brief"),
        ({"target": "client"}, "brief"),
        ({"objective": "produce"}, "brief"),
    ],
    ids=["over-tone", "over-depth", "over-target", "over-objective"],
)
def test_brevity_outranks_every_other_signal(weaker, expected):
    """Rank 1 must win against every lower-ranked signal."""
    chosen = select_format(frame(constraints=["brevity"], **weaker))

    assert chosen == expected, f"brevity should outrank {weaker!r}, got {chosen!r}"


def test_tone_outranks_target_and_objective():
    """Tone must win against target and objective."""
    chosen = select_format(frame(tone="direct", target="client", objective="produce"))

    assert chosen == "bullet_points", f"tone should outrank target and objective, got {chosen!r}"


# ---------------------------------------------------------------------------
# Rank 3 - the client + executive conjunction
# ---------------------------------------------------------------------------


def test_client_and_executive_give_email():
    """target=client AND tone=executive -> email."""
    chosen = select_format(frame(target="client", tone="executive"))

    assert chosen == "email", f"expected 'email', got {chosen!r}"


@pytest.mark.parametrize(
    ("signal", "expected"),
    [
        ({"target": "client"}, "action_plan"),
        ({"tone": "executive"}, "executive_summary"),
        ({"target": "client", "tone": "direct"}, "bullet_points"),
        ({"target": "team", "tone": "executive"}, "executive_summary"),
    ],
    ids=["client-alone", "executive-alone", "client-other-tone", "executive-other-target"],
)
def test_email_requires_both_signals(signal, expected):
    """Either signal on its own must keep its own outcome."""
    chosen = select_format(frame(**signal))

    assert chosen == expected, f"{signal!r} should still yield {expected!r}, got {chosen!r}"


@pytest.mark.parametrize(
    ("constraint", "expected"),
    [(["brevity"], "brief"), (["precision"], "table")],
    ids=["brevity", "precision"],
)
def test_constraints_outrank_email(constraint, expected):
    """Ranks 1 and 2 must still win against the conjunction."""
    chosen = select_format(frame(target="client", tone="executive", constraints=constraint))

    assert chosen == expected, f"constraint {constraint!r} should outrank email, got {chosen!r}"


@pytest.mark.parametrize(
    "weaker",
    [
        {"depth": "condensed"},
        {"depth": "in_depth"},
        {"objective": "produce"},
    ],
    ids=["over-condensed", "over-in-depth", "over-objective"],
)
def test_email_outranks_depth_and_objective(weaker):
    """Rank 3 must win against every lower-ranked signal."""
    chosen = select_format(frame(target="client", tone="executive", **weaker))

    assert chosen == "email", f"email should outrank {weaker!r}, got {chosen!r}"


def test_email_is_reachable_from_a_real_framing():
    """
    Guard against a dead rule.

    `interpret()` derives the tone from the target, so a client request
    already carries the executive tone: the conjunction must fire on a frame
    the pipeline can actually produce, not only on a hand-built one.
    """
    chosen = select_format(interpret("Write a note for the client."))

    assert chosen == "email", f"the rule is unreachable from a real framing, got {chosen!r}"
