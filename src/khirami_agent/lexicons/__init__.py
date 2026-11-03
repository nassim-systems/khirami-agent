"""
Multilingual lexicons — the only place where non-English words live.

Every language module exposes the same table names with the same canonical
English keys. This package assembles them into per-language mappings, plus
merged fallbacks used when the language of a request cannot be determined.

Supported languages
    Request framer and engagement router: en, fr, es, it, pt.
    Constraint extractor: the same five, plus de.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from types import ModuleType

from . import de, en, es, fr, it, pt

FRAMING_MODULES: Mapping[str, ModuleType] = {
    "fr": fr,
    "en": en,
    "es": es,
    "it": it,
    "pt": pt,
}
EXTRACTOR_MODULES: Mapping[str, ModuleType] = {
    "fr": fr,
    "en": en,
    "es": es,
    "de": de,
    "it": it,
    "pt": pt,
}


def _by_language(modules: Mapping[str, ModuleType], name: str) -> dict[str, object]:
    """One table, keyed by language code."""
    return {code: getattr(module, name) for code, module in modules.items()}


def merge_categories(
    by_language: Mapping[str, Mapping[str, tuple[str, ...]]],
) -> dict[str, tuple[str, ...]]:
    """
    Merge the markers of every language under each category.

    Used as the fallback lexicon when the language stays undetermined: framing
    keeps working by accepting the markers of all languages at once. Duplicates
    are dropped, so a marker shared by several languages weighs once.
    """
    merged: dict[str, tuple[str, ...]] = {}
    for lexicon in by_language.values():
        for category, markers in lexicon.items():
            known = merged.get(category, ())
            merged[category] = known + tuple(marker for marker in markers if marker not in known)
    return merged


def merge_words(groups: Iterable[Iterable[str]]) -> tuple[str, ...]:
    """Ordered union of several word lists, without duplicates."""
    return tuple(dict.fromkeys(word for group in groups for word in group))


# ----------------------------------------------------------------------
# Request framer.
# ----------------------------------------------------------------------
FUNCTION_WORDS = _by_language(FRAMING_MODULES, "FUNCTION_WORDS")
OBJECTIVES_BY_LANGUAGE = _by_language(FRAMING_MODULES, "OBJECTIVES")
SUBJECTS_BY_LANGUAGE = _by_language(FRAMING_MODULES, "SUBJECTS")
RECIPIENTS_BY_LANGUAGE = _by_language(FRAMING_MODULES, "RECIPIENTS")
INTERNAL_BY_LANGUAGE = _by_language(FRAMING_MODULES, "INTERNAL")
TONES_BY_LANGUAGE = _by_language(FRAMING_MODULES, "TONES")
DEPTHS_BY_LANGUAGE = _by_language(FRAMING_MODULES, "DEPTHS")
CONSTRAINTS_BY_LANGUAGE = _by_language(FRAMING_MODULES, "CONSTRAINTS")
STOPWORDS_BY_LANGUAGE = _by_language(FRAMING_MODULES, "STOPWORDS")
DIRECTIONS_BY_LANGUAGE = _by_language(FRAMING_MODULES, "DIRECTIONS")
NUMBER_WORDS_BY_LANGUAGE = _by_language(FRAMING_MODULES, "NUMBER_WORDS")
MONTHS_BY_LANGUAGE = _by_language(FRAMING_MODULES, "MONTHS")

OBJECTIVES_MERGED = merge_categories(OBJECTIVES_BY_LANGUAGE)
SUBJECTS_MERGED = merge_categories(SUBJECTS_BY_LANGUAGE)
RECIPIENTS_MERGED = merge_categories(RECIPIENTS_BY_LANGUAGE)
INTERNAL_MERGED = merge_categories(INTERNAL_BY_LANGUAGE)
TONES_MERGED = merge_categories(TONES_BY_LANGUAGE)
DEPTHS_MERGED = merge_categories(DEPTHS_BY_LANGUAGE)
CONSTRAINTS_MERGED = merge_categories(CONSTRAINTS_BY_LANGUAGE)
DIRECTIONS_MERGED = merge_categories(DIRECTIONS_BY_LANGUAGE)
STOPWORDS_MERGED: frozenset[str] = frozenset().union(*STOPWORDS_BY_LANGUAGE.values())
NUMBER_WORDS_MERGED = merge_words(NUMBER_WORDS_BY_LANGUAGE.values())
MONTHS_MERGED = merge_words(MONTHS_BY_LANGUAGE.values())

# Language-independent sets: applied whatever the detected language.
LINKING_WORDS: frozenset[str] = frozenset().union(
    *(module.LINKING_WORDS for module in FRAMING_MODULES.values())
)
DURATION_UNITS: frozenset[str] = frozenset().union(
    *(module.DURATION_UNITS for module in FRAMING_MODULES.values())
)
PERIODS: frozenset[str] = frozenset().union(
    *(module.PERIODS for module in FRAMING_MODULES.values())
)

# ----------------------------------------------------------------------
# Engagement router and consultant guard.
# ----------------------------------------------------------------------
ENGAGEMENT_MODE_MARKERS = merge_categories(_by_language(FRAMING_MODULES, "ENGAGEMENT_MODES"))
SECTOR_MARKERS = merge_categories(_by_language(FRAMING_MODULES, "SECTORS"))
HYPE_TERMS = merge_words(module.HYPE_TERMS for module in FRAMING_MODULES.values())

# ----------------------------------------------------------------------
# Constraint extractor.
# ----------------------------------------------------------------------
EXTRACTOR_FUNCTION_WORDS = _by_language(EXTRACTOR_MODULES, "EXTRACTOR_FUNCTION_WORDS")
EXTRACTOR_LEXICON = _by_language(EXTRACTOR_MODULES, "EXTRACTOR_LEXICON")
