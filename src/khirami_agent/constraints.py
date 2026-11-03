"""
Constraint extractor — a standalone lexical layer.

Recognizes the signals explicitly written in a request — length bounds,
register, tone, depth, format, target — and returns them as usable
constraints.

Principle
    Lexical mapping, nothing else. This module does not decide, infer or
    invent: it recognizes what is written and stays silent about the rest. A
    signal absent from the lexicon is never guessed.

Scope
    Six languages — en, fr, es, de, it, pt — and six marker families per
    language: constraints, registers, tones, depths, formats, targets.

Status
    Self-contained and fully tested, but not yet wired into the decision
    paths, which rely on `framing.interpret()`.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from . import lexicons
from .text import count_markers, dominant, fold, padded, split_words

# Tie-break order when two languages gather the same number of markers.
TIE_BREAK_ORDER: tuple[str, ...] = ("fr", "en", "es", "de", "it", "pt")
SUPPORTED_LANGUAGES: tuple[str, ...] = tuple(lexicons.EXTRACTOR_LEXICON)
DEFAULT_LANGUAGE: str = "en"

# Search window for a number around a quantifiable marker.
NUMBER_WINDOW: int = 4

FAMILIES: tuple[str, ...] = (
    "constraints",
    "registers",
    "tones",
    "depths",
    "formats",
    "targets",
)

# Priorities — break ties, from the most specific to the most general.
REGISTER_PRIORITY: tuple[str, ...] = ("executive", "consultant", "technical", "plain")
TONE_PRIORITY: tuple[str, ...] = ("formal", "synthetic", "dynamic", "neutral")
DEPTH_PRIORITY: tuple[str, ...] = ("expert", "detailed", "medium", "brief")
FORMAT_PRIORITY: tuple[str, ...] = ("table", "plan", "analysis", "synthesis", "list")
TARGET_PRIORITY: tuple[str, ...] = ("client", "management", "team", "system")

CONSTRAINT_KEYS: tuple[str, ...] = (
    "word_limit",
    "max_bullets",
    "brief",
    "concise",
    "tone",
    "depth",
    "format",
    "target",
)


def _tokens(text: Any) -> list[str]:
    """Comparable words: lower-case, no accents, no punctuation."""
    folded = fold(str(text)).replace("ß", "ss").replace("ü", "u")
    return split_words(folded)


def _number_near(words: Sequence[str], markers: Sequence[str]) -> int | None:
    """
    Number attached to a quantifiable marker.

    Looks for the integer closest to a marker, within a window on either side.
    Outside the window nothing is returned: a stray number in the sentence is
    not presumed to refer to the marker.
    """
    number_positions = [index for index, word in enumerate(words) if word.isdigit()]
    if not number_positions:
        return None

    marker_positions = [
        index for index, word in enumerate(words) if any(marker == word for marker in markers)
    ]
    if not marker_positions:
        return None

    best = min(
        (
            (abs(number - marker), number)
            for number in number_positions
            for marker in marker_positions
        ),
        default=None,
    )
    if best is None or best[0] > NUMBER_WINDOW:
        return None
    return int(words[best[1]])


def _lexicon_signals(corpus: str, language: str) -> int:
    """Total number of lexicon markers recognized in one language."""
    return sum(
        total
        for family in lexicons.EXTRACTOR_LEXICON[language].values()
        for total in count_markers(corpus, family).values()
    )


def detect_language(request: str) -> str:
    """
    Determine the language of a request.

    Simple heuristic, in two successive passes:

        1. Function words — count the grammatical words characteristic of
           each language. The best-scoring language wins; `TIE_BREAK_ORDER`
           breaks ties.
        2. Lexicon words — a short request may contain no recognized function
           word ("Use a formal, executive tone."). The business vocabulary
           then decides: a register or format marker identifies the language
           as surely as an article.

    Falls back to `DEFAULT_LANGUAGE` only when neither pass gives a signal:
    empty request, or a language that is not covered.
    """
    corpus = padded(_tokens(request))

    direct = dominant(count_markers(corpus, lexicons.EXTRACTOR_FUNCTION_WORDS), TIE_BREAK_ORDER)
    if direct:
        return direct

    scores = {
        language: total
        for language in TIE_BREAK_ORDER
        if (total := _lexicon_signals(corpus, language))
    }
    return dominant(scores, TIE_BREAK_ORDER) or DEFAULT_LANGUAGE


def extract_constraints(request: str, language: str) -> dict[str, Any]:
    """
    Extract the constraints explicitly written in a request.

    An unknown language falls back to `DEFAULT_LANGUAGE` rather than failing.
    Only markers present in the language lexicon are recognized; an absent
    signal is `None` or `False`, never a guessed value.

    Numeric bounds
        `word_limit` and `max_bullets` are only returned when a number sits
        right next to the marker. "limit 120 words" gives 120; a number lost
        elsewhere in the sentence is not captured.

    Tone
        Registers and tones feed the same key. The register wins: it is more
        specific than a tone colour.

    Returns the eight keys of `CONSTRAINT_KEYS`, always present.
    """
    lexicon = (
        lexicons.EXTRACTOR_LEXICON.get(language) or lexicons.EXTRACTOR_LEXICON[DEFAULT_LANGUAGE]
    )

    words = _tokens(request)
    corpus = padded(words)

    constraints = lexicon["constraints"]
    register = dominant(count_markers(corpus, lexicon["registers"]), REGISTER_PRIORITY)
    tone = dominant(count_markers(corpus, lexicon["tones"]), TONE_PRIORITY)

    return {
        "word_limit": _number_near(words, constraints["word-limit"]),
        "max_bullets": _number_near(words, constraints["max-bullets"]),
        "brief": bool(count_markers(corpus, {"x": constraints["briefly"]})),
        "concise": bool(count_markers(corpus, {"x": constraints["concisely"]})),
        "tone": register or tone,
        "depth": dominant(count_markers(corpus, lexicon["depths"]), DEPTH_PRIORITY),
        "format": dominant(count_markers(corpus, lexicon["formats"]), FORMAT_PRIORITY),
        "target": dominant(count_markers(corpus, lexicon["targets"]), TARGET_PRIORITY),
    }
