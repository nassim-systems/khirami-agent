"""
Unit tests for the request framer's language detection and the promise it
carries: the same demand, written in five languages, must produce the same
framing.

Guarantees under test
---------------------
- Function words outrank the business lexicon.
- A language needs `LANGUAGE_THRESHOLD` markers to be retained.
- A tie names nobody: no static priority ever breaks it.
- The detected language is correct or `undetermined`, never wrong.
"""

from __future__ import annotations

import pytest

from khirami_agent import interpret, select_format
from khirami_agent.framing import (
    LANGUAGE_THRESHOLD,
    SUPPORTED_LANGUAGES,
    UNDETERMINED_LANGUAGE,
    _detect_language,
    _tokens,
)
from khirami_agent.text import padded

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

# The same demand, written in the five covered languages.
MULTILINGUAL_DEMAND = {
    "en": "Customer service is saturated, we need a diagnosis and an action plan.",
    "fr": "Le service client est saturé, on veut un diagnostic et un plan d'action.",
    "es": "El servicio al cliente está saturado, necesitamos un diagnóstico y un plan de acción.",
    "it": "Il servizio clienti è saturo, serve una diagnosi e un piano d'azione.",
    "pt": "O serviço ao cliente está saturado, precisamos de um diagnóstico e um plano de ação.",
}

LANGUAGES = list(MULTILINGUAL_DEMAND)

EXPECTED_OBJECTIVES = ["analyze", "plan"]
ALLOWED_TARGETS = {"team", "undetermined"}
ALLOWED_FORMATS = {"action_plan", "paragraph"}


def language_of(text):
    """Detected language for a raw request."""
    return _detect_language(padded(_tokens(text)))


# ---------------------------------------------------------------------------
# The promise
# ---------------------------------------------------------------------------


def test_same_demand_same_framing_in_five_languages():
    """
    Five languages, one demand: the language must be right or admitted as
    undetermined - never wrong - and the framing must not depend on it.
    """
    framings = {}

    for language, text in MULTILINGUAL_DEMAND.items():
        detected = language_of(text)

        assert detected in (language, UNDETERMINED_LANGUAGE), (
            f"[{language}] detected as {detected!r} - a wrong language is never acceptable"
        )

        frame = interpret(text)
        framings[language] = frame

        assert frame["objectives"] == EXPECTED_OBJECTIVES, (
            f"[{language}] objectives={frame['objectives']!r}, expected {EXPECTED_OBJECTIVES!r}"
        )
        assert frame["target"] in ALLOWED_TARGETS, (
            f"[{language}] target={frame['target']!r}, expected one of {sorted(ALLOWED_TARGETS)!r}"
        )
        assert frame["target"] != "client", (
            f"[{language}] 'customer service' is the subject, not the recipient"
        )
        assert select_format(frame) in ALLOWED_FORMATS, (
            f"[{language}] format={select_format(frame)!r}, expected one of "
            f"{sorted(ALLOWED_FORMATS)!r}"
        )

    # The promise itself: one framing, whatever the language.
    #
    # `target` is deliberately out of this check: both "team" and
    # "undetermined" are allowed for this demand, because only English and
    # French carry an explicit first-person recipient marker ("we", "on").
    for field in ("objectives", "objective", "depth", "constraints"):
        values = {language: framings[language][field] for language in LANGUAGES}
        distinct = {str(value) for value in values.values()}
        assert len(distinct) == 1, f"field {field!r} diverges across languages: {values!r}"


# ---------------------------------------------------------------------------
# The rules that make the promise hold
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("language", LANGUAGES, ids=LANGUAGES)
def test_each_language_is_detected(language):
    """Every covered language must be named, not merely not-wrong."""
    assert language_of(MULTILINGUAL_DEMAND[language]) == language


def test_never_a_wrong_language():
    """The core guarantee: correct or undetermined, never a third answer."""
    for language, text in MULTILINGUAL_DEMAND.items():
        assert language_of(text) in (language, UNDETERMINED_LANGUAGE)


def test_below_threshold_is_undetermined():
    """A single isolated marker is not enough to name a language."""
    assert language_of("zzz le zzz") == UNDETERMINED_LANGUAGE


def test_no_signal_is_undetermined():
    """Nothing recognizable - the answer is said, not guessed."""
    for text in ("", "   ", "xyzzy plugh frobnicate", "1234 5678"):
        assert language_of(text) == UNDETERMINED_LANGUAGE


def test_tie_is_undetermined_not_arbitrated():
    """
    A tie names nobody.

    This is the regression this suite exists for: Italian and Portuguese used
    to be read as Spanish because a tie was silently broken by declaration
    order.
    """
    # One Spanish marker against one Italian marker: nothing may win.
    assert language_of("el questo") == UNDETERMINED_LANGUAGE

    # And the order of appearance must not change the answer either.
    assert language_of("questo el") == UNDETERMINED_LANGUAGE


def test_declaration_order_never_decides():
    """The first declared language must not win by that fact alone."""
    assert SUPPORTED_LANGUAGES[0] == "en"

    # One English marker against one Italian marker.
    assert language_of("the questo") == UNDETERMINED_LANGUAGE


def test_threshold_is_the_documented_one():
    """`LANGUAGE_THRESHOLD` markers are enough; one fewer is not."""
    assert LANGUAGE_THRESHOLD == 2

    assert language_of("zzz della zzz") == UNDETERMINED_LANGUAGE
    assert language_of("zzz della gli zzz") == "it"


def test_business_lexicon_only_speaks_second():
    """
    The business lexicon rescues a request with no function word, but never
    overrides function words that contradict each other.
    """
    # No function word at all: the business vocabulary decides.
    assert language_of("Answer briefly, in under 100 words.") == "en"

    # Contradictory function words: the business lexicon stays silent.
    assert language_of("el questo diagnostico diagnosi") == UNDETERMINED_LANGUAGE


def test_undetermined_language_still_frames_the_demand():
    """
    An unnamed language must not cost the framing.

    The merged lexicons keep `interpret()` working, which is what lets the
    promise hold even when detection abstains.
    """
    frame = interpret("diagnostic plan action client")

    assert frame["objectives"] == EXPECTED_OBJECTIVES
    assert frame["constraints"] == []


def test_detection_is_deterministic():
    for text in MULTILINGUAL_DEMAND.values():
        assert language_of(text) == language_of(text)


def test_detection_does_not_mutate_its_input():
    text = MULTILINGUAL_DEMAND["fr"]
    original = str(text)

    language_of(text)
    interpret(text)

    assert text == original
