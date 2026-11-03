"""
Unit tests for `enforce_rules(request_frame)`.

Tests the function alone, from hand-built frames: no call to `interpret()`,
no lexicon, no language detection, no I/O.

Contract: the output is a six-key dictionary whose keys are always present;
a rule that is not triggered is None or False, never missing.
"""

from __future__ import annotations

import pytest

from khirami_agent import enforce_rules

RULE_KEYS = (
    "max_words",
    "max_bullets",
    "precision",
    "brevity",
    "depth",
    "tone",
)

WORDS_BREVITY = 80
WORDS_LIMIT = 120
BULLETS = 5

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


def test_brevity():
    """brevity constraint -> max_words = 80."""
    assert enforce_rules(frame(constraints=["brevity"]))["max_words"] == WORDS_BREVITY


def test_word_limit():
    """word-limit constraint -> max_words = 120."""
    assert enforce_rules(frame(constraints=["word-limit"]))["max_words"] == WORDS_LIMIT


def test_precision():
    """precision constraint -> precision = True."""
    assert enforce_rules(frame(constraints=["precision"]))["precision"] is True


def test_max_bullets():
    """max-bullets constraint -> max_bullets = 5."""
    assert enforce_rules(frame(constraints=["max-bullets"]))["max_bullets"] == BULLETS


def test_depth_condensed():
    """depth condensed -> depth = "condensed"."""
    assert enforce_rules(frame(depth="condensed"))["depth"] == "condensed"


def test_depth_in_depth():
    """depth in_depth -> depth = "in_depth"."""
    assert enforce_rules(frame(depth="in_depth"))["depth"] == "in_depth"


def test_tone_executive():
    """executive tone -> tone = "executive"."""
    assert enforce_rules(frame(tone="executive"))["tone"] == "executive"


def test_tone_direct():
    """direct tone -> tone = "direct"."""
    assert enforce_rules(frame(tone="direct"))["tone"] == "direct"


def test_stricter_word_bound_wins():
    """brevity outranks word-limit: the stricter bound wins."""
    rules = enforce_rules(frame(constraints=["brevity", "word-limit"]))

    assert rules["max_words"] == WORDS_BREVITY, (
        f"brevity (80) should outrank word-limit (120), got {rules['max_words']!r}"
    )


def test_neutral_fallback():
    """No signal at all -> every rule is None or False."""
    rules = enforce_rules(NEUTRAL_FRAME)

    assert rules == {
        "max_words": None,
        "max_bullets": None,
        "precision": False,
        "brevity": False,
        "depth": None,
        "tone": None,
    }


def test_is_deterministic():
    """Two identical calls must produce the same dict."""
    request_frame = frame(
        objective="produce",
        target="client",
        tone="executive",
        depth="in_depth",
        constraints=["precision", "brevity", "max-bullets"],
    )

    first = enforce_rules(request_frame)
    second = enforce_rules(request_frame)

    assert first == second, f"not deterministic: {first!r} then {second!r}"


# ---------------------------------------------------------------------------
# Structural guarantees
# ---------------------------------------------------------------------------


def test_every_key_is_always_present():
    """The caller must never have to test for a missing key."""
    for request_frame in (NEUTRAL_FRAME, frame(constraints=["brevity"])):
        rules = enforce_rules(request_frame)

        assert set(rules) == set(RULE_KEYS), f"unexpected key set: {sorted(rules)!r}"


def test_brevity_flag_follows_the_brevity_constraint():
    assert enforce_rules(frame(constraints=["brevity"]))["brevity"] is True
    assert enforce_rules(NEUTRAL_FRAME)["brevity"] is False


@pytest.mark.parametrize(
    "depth", ["standard", None, "unknown"], ids=["standard", "none", "unknown"]
)
def test_unruled_depth_stays_none(depth):
    assert enforce_rules(frame(depth=depth))["depth"] is None


@pytest.mark.parametrize(
    "tone",
    ["neutral", "technical", "educational", None],
    ids=["neutral", "technical", "educational", "none"],
)
def test_unruled_tone_stays_none(tone):
    """Only executive and direct are ruled: the other canonical tones stay None."""
    assert enforce_rules(frame(tone=tone))["tone"] is None


def test_bullets_and_words_are_independent():
    """A bullet bound must not silently set a word bound, and the reverse."""
    bullets_only = enforce_rules(frame(constraints=["max-bullets"]))
    words_only = enforce_rules(frame(constraints=["word-limit"]))

    assert bullets_only["max_words"] is None
    assert words_only["max_bullets"] is None


def test_does_not_mutate_its_input():
    request_frame = frame(constraints=["brevity", "precision"])
    original = {**request_frame, "constraints": list(request_frame["constraints"])}

    enforce_rules(request_frame)

    assert request_frame == original, "enforce_rules() must not mutate the frame"
