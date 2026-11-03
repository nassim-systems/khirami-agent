"""
Unit tests for the standalone constraint extractor (`constraints.py`).

Contract
--------
`detect_language(request)` returns one of the six covered languages, falling
back to "en". `extract_constraints(request, language)` returns an eight-key
dictionary whose keys are always present: an unmatched signal is None or
False, never invented.
"""

from __future__ import annotations

import pytest

from khirami_agent.constraints import (
    CONSTRAINT_KEYS,
    FAMILIES,
    SUPPORTED_LANGUAGES,
    detect_language,
    extract_constraints,
)
from khirami_agent.lexicons import EXTRACTOR_LEXICON

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

# One unambiguous sentence per covered language.
SENTENCES = {
    "en": "Write a detailed analysis for the client, with a formal tone.",
    "fr": "Rédige une analyse détaillée pour le client, avec un ton formel.",
    "es": "Escribe un análisis detallado para el cliente, con un tono formal.",
    "de": "Bitte erstelle eine detaillierte Analyse für den Kunden mit einem formellen Ton.",
    "it": "Scrivi un'analisi dettagliata per il cliente, con un tono formale.",
    "pt": "Escreva uma análise detalhada para o cliente, com um tom formal.",
}

NEUTRAL_REQUEST = "xyzzy plugh frobnicate"


def constraints(request, language=None):
    """Extract with the detected language unless one is forced."""
    return extract_constraints(request, language or detect_language(request))


# ---------------------------------------------------------------------------
# Behaviour
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("language", list(SENTENCES), ids=list(SENTENCES))
def test_language_detection(language):
    """Each of the six languages must be recognized from a plain sentence."""
    detected = detect_language(SENTENCES[language])

    assert detected == language, (
        f"{SENTENCES[language]!r} detected as {detected!r}, expected {language!r}"
    )


def test_word_limit_extraction():
    """'limit 120 words' -> 120."""
    assert constraints("Answer with a limit 120 words.")["word_limit"] == 120


def test_briefly_and_concisely_raise_their_own_flag():
    """'briefly' and 'concise' raise their own flag."""
    brief = constraints("Please answer briefly.")
    concise = constraints("Please keep the answer concise.")

    assert brief["brief"] is True
    assert concise["concise"] is True


def test_max_bullets():
    """'give me 5 bullets' -> 5."""
    assert constraints("Give me 5 bullets on the topic.")["max_bullets"] == 5


def test_tone_detection():
    """'executive tone' -> tone = 'executive'."""
    assert constraints("Use an executive tone for this.")["tone"] == "executive"


def test_depth_detection():
    """'detailed analysis' -> depth = 'expert'."""
    assert constraints("Give me a detailed analysis.")["depth"] == "expert"


def test_format_detection():
    """'make a table' -> format = 'table'."""
    assert constraints("Make a table of the options.")["format"] == "table"


def test_target_detection():
    """'for the client' -> target = 'client'."""
    assert constraints("Write the note for the client.")["target"] == "client"


@pytest.mark.parametrize("language", list(SENTENCES), ids=list(SENTENCES))
def test_does_not_mutate_its_input(language):
    """The request is never modified."""
    request = SENTENCES[language]
    original = str(request)

    detect_language(request)
    extract_constraints(request, language)

    assert request == original, "the request was mutated"


@pytest.mark.parametrize("language", list(SENTENCES), ids=list(SENTENCES))
def test_is_deterministic(language):
    """Two identical calls must produce the same constraints."""
    request = SENTENCES[language]

    first = extract_constraints(request, language)
    second = extract_constraints(request, language)

    assert first == second, f"not deterministic: {first!r} then {second!r}"


def test_no_invention():
    """A request holding no lexicon word must yield no constraint at all."""
    extracted = constraints(NEUTRAL_REQUEST)

    assert extracted == {
        "word_limit": None,
        "max_bullets": None,
        "brief": False,
        "concise": False,
        "tone": None,
        "depth": None,
        "format": None,
        "target": None,
    }


# ---------------------------------------------------------------------------
# Structural guarantees
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("language", list(SENTENCES), ids=list(SENTENCES))
def test_every_key_is_always_present(language):
    """The caller must never have to test for a missing key."""
    for request in (SENTENCES[language], NEUTRAL_REQUEST, ""):
        extracted = extract_constraints(request, language)

        assert set(extracted) == set(CONSTRAINT_KEYS), f"unexpected key set: {sorted(extracted)!r}"


def test_lexicon_covers_every_language_and_family():
    """The lexicon must be complete: six languages, six families each."""
    assert set(EXTRACTOR_LEXICON) == set(SUPPORTED_LANGUAGES) == set(SENTENCES)
    for language, lexicon in EXTRACTOR_LEXICON.items():
        assert set(lexicon) == set(FAMILIES), f"{language}: families missing"
        for family, categories in lexicon.items():
            assert categories, f"{language}.{family} is empty"
            for category, markers in categories.items():
                assert markers, f"{language}.{family}.{category} has no marker"


def test_categories_are_identical_across_languages():
    """Only the surface is translated: the category keys stay canonical."""
    reference = {family: set(categories) for family, categories in EXTRACTOR_LEXICON["en"].items()}

    for language, lexicon in EXTRACTOR_LEXICON.items():
        for family, categories in lexicon.items():
            assert set(categories) == reference[family], (
                f"{language}.{family} diverges from the canonical categories"
            )


def test_unknown_language_falls_back_without_raising():
    extracted = extract_constraints("Give me a detailed analysis.", "klingon")

    assert set(extracted) == set(CONSTRAINT_KEYS)


def test_empty_input_falls_back_to_english():
    for request in ("", "   "):
        assert detect_language(request) == "en"


def test_a_lone_number_is_not_captured():
    """A number with no nearby marker must not become a bound."""
    extracted = constraints("There were 42 attendees at the client meeting.")

    assert extracted["word_limit"] is None
    assert extracted["max_bullets"] is None


def test_register_outranks_tone():
    """When both fire, the register wins: it is the more specific signal."""
    extracted = constraints("Use a formal, executive tone.")

    assert extracted["tone"] == "executive"
