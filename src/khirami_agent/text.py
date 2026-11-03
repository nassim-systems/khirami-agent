"""
Text normalization and marker counting shared by the framing layers.

Requests are compared word by word, not character by character: text is
lower-cased, accent-folded and stripped of punctuation, then padded with
spaces so that a marker only matches whole words.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

ACCENT_FOLDING = str.maketrans(
    "àâäáãåçéèêëíìîïñóòôöõúùûüýÿ",
    "aaaaaaceeeeiiiinooooouuuuyy",
)


def fold(text: str) -> str:
    """Lower-case and accent-folded text, ligatures expanded."""
    return text.lower().replace("œ", "oe").replace("æ", "ae").translate(ACCENT_FOLDING)


def split_words(text: str) -> list[str]:
    """Split on every non-alphanumeric character."""
    return "".join(char if char.isalnum() else " " for char in text).split()


def padded(words: Sequence[str]) -> str:
    """Normalized text bordered by spaces, for whole-word matching."""
    return " " + " ".join(words) + " "


def count_markers(corpus: str, lexicon: Mapping[str, Sequence[str]]) -> dict[str, int]:
    """Number of markers found, for each category that has at least one."""
    return {
        category: total
        for category, markers in lexicon.items()
        if (total := sum(1 for marker in markers if f" {marker} " in corpus))
    }


def dominant(scores: Mapping[str, int], priority: Sequence[str]) -> str | None:
    """Highest-scoring category; the priority order breaks ties."""
    if not scores:
        return None
    return min(
        scores,
        key=lambda category: (
            -scores[category],
            priority.index(category) if category in priority else len(priority),
        ),
    )
