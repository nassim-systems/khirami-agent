"""
Request framing — the only layer allowed to read the raw request.

`interpret()` turns a free-text request into a structured frame: objective,
subject, recipient, tone, depth, explicit constraints, the quoted focus of the
request and its measurable targets, plus what is missing and how confident
the framing is. Every later stage consumes the frame, never the raw text.

The analysis is lexical. It frames what is written and never goes beyond it:
what is not found is left empty, not guessed.

Multilingual
    The language is detected first (en, fr, es, it, pt), then the matching
    lexicon is used. The returned values are canonical English categories, so
    the same request written in five languages produces the same frame.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from . import lexicons
from .text import count_markers, dominant, fold, padded, split_words

OBJECTIVE_PRIORITY: tuple[str, ...] = (
    "produce",
    "plan",
    "analyze",
    "verify",
    "decide",
    "summarize",
    "explain",
)

# Logical execution order, distinct from the tie-breaking priority: a double
# request is announced in the order it is handled — diagnose before planning,
# plan before producing.
OBJECTIVE_LOGICAL_ORDER: tuple[str, ...] = (
    "analyze",
    "decide",
    "plan",
    "produce",
    "verify",
    "summarize",
    "explain",
    "answer",
)

DEFAULT_OBJECTIVE: str = "answer"

TARGET_PRIORITY: tuple[str, ...] = ("client", "team", "system", "self")
UNDETERMINED: str = "undetermined"

TONE_PRIORITY: tuple[str, ...] = ("technical", "executive", "educational", "direct")
TONE_BY_TARGET: Mapping[str, str] = {
    "client": "executive",
    "team": "direct",
    "system": "technical",
    "self": "direct",
    UNDETERMINED: "neutral",
}

SUPPORTED_LANGUAGES: tuple[str, ...] = ("en", "fr", "es", "it", "pt")

# A language that cannot be settled is declared as such rather than guessed.
UNDETERMINED_LANGUAGE: str = "undetermined"

# Number of markers a language must gather to be retained.
LANGUAGE_THRESHOLD: int = 2

FOCUS_MAX_WORDS: int = 8

FRAMING_MIN_WORDS: int = 6
HIGH_CONFIDENCE_MAX_GAPS: int = 1
MEDIUM_CONFIDENCE_MAX_GAPS: int = 3


def _tokens(text: str) -> list[str]:
    """Comparable words: lower-case, no accents, no punctuation."""
    return split_words(fold(text))


def _raw_tokens(text: str) -> list[str]:
    """
    Same split as `_tokens()`, without folding case or accents.

    Both lists are aligned index by index: `_tokens()` is used to recognize,
    this one to quote the focus exactly as it was written.
    """
    return split_words(text)


def _co_dominant(scores: Mapping[str, int], order: Sequence[str]) -> list[str]:
    """
    Categories tied at the top score, returned in the given order.

    A request carrying two objectives at the same signal level really carries
    two. Breaking the tie silently would lose one.
    """
    if not scores:
        return []
    top = max(scores.values())
    retained = {category for category, value in scores.items() if value == top}
    return [category for category in order if category in retained]


def _lexicon_signals(corpus: str, language: str) -> int:
    """Total number of business markers recognized in one language."""
    return sum(
        total
        for lexicon in (
            lexicons.OBJECTIVES_BY_LANGUAGE[language],
            lexicons.SUBJECTS_BY_LANGUAGE[language],
            lexicons.TONES_BY_LANGUAGE[language],
            lexicons.DEPTHS_BY_LANGUAGE[language],
            lexicons.CONSTRAINTS_BY_LANGUAGE[language],
        )
        for total in count_markers(corpus, lexicon).values()
    )


def _leader(scores: Mapping[str, int]) -> tuple[str | None, bool]:
    """
    Language leading a count, and whether its lead clears the threshold.

    Returns `(language, reaches_threshold)`. A tie at the top names nobody: it
    returns `(None, False)`, never a winner picked by declaration order.
    """
    if not scores:
        return None, False
    top = max(scores.values())
    leaders = [language for language, total in scores.items() if total == top]
    if len(leaders) > 1:
        return None, False
    return leaders[0], top >= LANGUAGE_THRESHOLD


def _detect_language(corpus: str) -> str:
    """
    Language of the request, by counting characteristic function words.

    Two passes, in this order:

        1. Function words — articles, prepositions and pronouns specific to
           each language. They outrank everything else.
        2. Business lexicon — consulted only when function words did not
           settle the question, and never when they contradict each other.

    Three safeguards:

        Threshold   — a language needs at least `LANGUAGE_THRESHOLD` markers.
                      A single isolated hint is not enough.
        Tie         — two languages neck and neck name nobody. No static order
                      breaks the tie: that arbitrary tie-break used to read
                      Italian and Portuguese as Spanish.
        Consistency — if the business lexicon points to another language than
                      the weak function-word lead, the disagreement counts as
                      no answer.

    Returns one of `SUPPORTED_LANGUAGES` or `UNDETERMINED_LANGUAGE`. Never a
    wrong language: uncertainty is declared, not filled.
    """
    direct = count_markers(corpus, lexicons.FUNCTION_WORDS)
    candidate, settled = _leader(direct)
    if settled:
        return candidate
    if direct and candidate is None:
        return UNDETERMINED_LANGUAGE

    lexical = {
        language: total
        for language in SUPPORTED_LANGUAGES
        if (total := _lexicon_signals(corpus, language))
    }
    backed, confirmed = _leader(lexical)
    if not confirmed:
        return UNDETERMINED_LANGUAGE
    if candidate is not None and backed != candidate:
        return UNDETERMINED_LANGUAGE
    return backed


def _depth(corpus: str, lexicon: Mapping[str, Sequence[str]]) -> str:
    """Requested depth; when signals tie, no side is taken."""
    scores = count_markers(corpus, lexicon)
    in_depth = scores.get("in_depth", 0)
    condensed = scores.get("condensed", 0)
    if in_depth > condensed:
        return "in_depth"
    if condensed > in_depth:
        return "condensed"
    return "standard"


def _focus(words: Sequence[str], raw: Sequence[str], language: str) -> str:
    """
    Most informative noun phrase of the request, quoted as written.

    A focus is a run of content words, possibly joined by linking prepositions
    — "ticket handling delays" counts as one. Objective markers are excluded:
    "action plan" says what is asked, not what it is about.

    The longest phrase wins. With no candidate, an empty string: Khirami does
    not fill what it did not find.
    """
    stopwords = lexicons.STOPWORDS_BY_LANGUAGE.get(language, lexicons.STOPWORDS_MERGED)
    linking = lexicons.LINKING_WORDS
    markers = {
        marker
        for group in lexicons.OBJECTIVES_BY_LANGUAGE.get(
            language, lexicons.OBJECTIVES_MERGED
        ).values()
        for marker in group
        if " " not in marker
    }

    groups: list[list[int]] = []
    current: list[int] = []
    for index, word in enumerate(words):
        if word in stopwords or word in markers or word.isdigit():
            if current:
                groups.append(current)
                current = []
        elif word in linking:
            if current:
                current.append(index)
        else:
            current.append(index)
    if current:
        groups.append(current)

    def tail_of_expression(group: Sequence[int]) -> bool:
        """
        Is the group only the end of an objective phrase?

        In "action plan", "action" alone is not a focus. A single word preceded
        by an objective marker — linking words aside — belongs to that phrase.
        """
        if len(group) != 1:
            return False
        before = group[0] - 1
        while before >= 0 and words[before] in linking:
            before -= 1
        return before >= 0 and words[before] in markers

    retained: list[list[int]] = []
    for group in groups:
        while group and words[group[-1]] in linking:
            group = group[:-1]
        if group and not tail_of_expression(group):
            retained.append(group[:FOCUS_MAX_WORDS])
    if not retained:
        return ""

    best = max(retained, key=len)
    return " ".join(raw[index] for index in best)


def _measures(words: Sequence[str], raw: Sequence[str], language: str) -> dict[str, str]:
    """
    Measurable markers of the request — direction, quantity, deadline.

    A plan without a quantified criterion is not a plan. These three signals
    are captured when explicitly written, and left empty otherwise: no target
    value is ever assumed.
    """
    direction = ""
    for sense, verbs in lexicons.DIRECTIONS_BY_LANGUAGE.get(
        language, lexicons.DIRECTIONS_MERGED
    ).items():
        if any(word in verbs for word in words):
            direction = sense
            break

    stopwords = lexicons.STOPWORDS_BY_LANGUAGE.get(language, lexicons.STOPWORDS_MERGED)

    def with_unit(index: int) -> str:
        """The number, followed by what it counts — never by a stopword."""
        following = index + 1
        if following < len(words) and words[following] not in stopwords:
            return f"{raw[index]} {raw[following]}"
        return raw[index]

    quantity = ""
    number_words = lexicons.NUMBER_WORDS_BY_LANGUAGE.get(language, lexicons.NUMBER_WORDS_MERGED)
    for index, word in enumerate(words):
        if (word.isdigit() and len(word) != 4) or word in number_words:
            quantity = with_unit(index)
            break

    deadline = ""
    months = lexicons.MONTHS_BY_LANGUAGE.get(language, lexicons.MONTHS_MERGED)
    for index, word in enumerate(words):
        if word in months or word in lexicons.PERIODS:
            deadline = raw[index]
            break
        if word.isdigit() and len(word) == 4 and word.startswith("20"):
            deadline = raw[index]
            break
        if (
            word in lexicons.DURATION_UNITS
            and index
            and (words[index - 1].isdigit() or words[index - 1] in number_words)
        ):
            deadline = " ".join(raw[index - 1 : index + 1])
            break

    return {"direction": direction, "quantity": quantity, "deadline": deadline}


def _missing_information(
    objective: str,
    target: str,
    focus: str,
    measures: Mapping[str, str],
    language: str,
    words: Sequence[str],
) -> list[str]:
    """
    List what is missing to conclude reliably.

    Each entry names a framing dimension left empty, in consulting terms:
    which objective, for whom, on what scope, at what volume. This list arms
    the clarification gate — a named gap can be closed by a question; a silent
    gap contaminates the whole diagnosis.

    A dimension is declared missing only when no signal filled it.
    """
    missing = []
    if objective == DEFAULT_OBJECTIVE:
        missing.append("objective")
    if target == UNDETERMINED:
        missing.append("recipient")
    if not focus:
        missing.append("scope")
    if not measures.get("quantity"):
        missing.append("volumes")
    if language == UNDETERMINED_LANGUAGE:
        missing.append("language")
    if len(words) < FRAMING_MIN_WORDS:
        missing.append("context")
    return missing


def _confidence(missing: Sequence[str]) -> str:
    """
    Confidence of the framing, derived from what is missing.

    Three levels only. A finer scale would suggest a precision the signal does
    not have — the clarification gate, not nuance, absorbs uncertainty.
    """
    total = len(missing)
    if total <= HIGH_CONFIDENCE_MAX_GAPS:
        return "high"
    if total <= MEDIUM_CONFIDENCE_MAX_GAPS:
        return "medium"
    return "low"


def interpret(request: str) -> dict[str, Any]:
    """
    Frame an incoming request.

    Double requests
        Two objectives with the same signal are two objectives. `objective`
        stays the dominant one — the one that decides the container — and
        `objectives` returns them all, in the order they are handled.

    Subject and recipient
        "customer service" talks about the client; "for the client" addresses
        it. `subject` carries what the request is about, `target` who the
        deliverable is for. Without a directional marker the target stays
        `undetermined` rather than inferred from the subject — a wrong target
        costs more than a missing one, which triggers clarification.

    Focus and measures
        `focus` is the most informative noun phrase, quoted as written;
        `measures` holds direction, quantity and deadline. Nothing is
        rephrased, nothing is assumed: what is not found stays empty.

    Returns
        request, objective, objectives, subject, focus, measures, target, tone,
        depth, constraints, missing_info, confidence.
    """
    text = request if isinstance(request, str) else ("" if request is None else str(request))
    words = _tokens(text)
    raw = _raw_tokens(text)
    corpus = padded(words)

    language = _detect_language(corpus)

    objective_scores = count_markers(
        corpus,
        lexicons.OBJECTIVES_BY_LANGUAGE.get(language, lexicons.OBJECTIVES_MERGED),
    )
    objective = dominant(objective_scores, OBJECTIVE_PRIORITY) or DEFAULT_OBJECTIVE
    objectives = _co_dominant(objective_scores, OBJECTIVE_LOGICAL_ORDER) or [objective]

    subject = (
        dominant(
            count_markers(
                corpus,
                lexicons.SUBJECTS_BY_LANGUAGE.get(language, lexicons.SUBJECTS_MERGED),
            ),
            TARGET_PRIORITY,
        )
        or UNDETERMINED
    )
    recipient = dominant(
        count_markers(
            corpus,
            lexicons.RECIPIENTS_BY_LANGUAGE.get(language, lexicons.RECIPIENTS_MERGED),
        ),
        TARGET_PRIORITY,
    ) or dominant(
        count_markers(
            corpus,
            lexicons.INTERNAL_BY_LANGUAGE.get(language, lexicons.INTERNAL_MERGED),
        ),
        TARGET_PRIORITY,
    )
    if recipient is not None:
        target = recipient
    elif subject == "system":
        target = "system"
    else:
        target = UNDETERMINED

    tone = dominant(
        count_markers(corpus, lexicons.TONES_BY_LANGUAGE.get(language, lexicons.TONES_MERGED)),
        TONE_PRIORITY,
    )

    focus = _focus(words, raw, language)
    measures = _measures(words, raw, language)
    missing = _missing_information(
        objective=objective,
        target=target,
        focus=focus,
        measures=measures,
        language=language,
        words=words,
    )

    return {
        "request": text,
        "objective": objective,
        "objectives": objectives,
        "subject": subject,
        "focus": focus,
        "measures": measures,
        "target": target,
        "tone": tone or TONE_BY_TARGET[target],
        "depth": _depth(corpus, lexicons.DEPTHS_BY_LANGUAGE.get(language, lexicons.DEPTHS_MERGED)),
        "constraints": sorted(
            count_markers(
                corpus,
                lexicons.CONSTRAINTS_BY_LANGUAGE.get(language, lexicons.CONSTRAINTS_MERGED),
            )
        ),
        "missing_info": missing,
        "confidence": _confidence(missing),
    }
