"""
Unit tests for `interpret(request)`.

Scope
-----
- Tests `interpret()` only. No other function, no integration path.
- Every test is independent: one `interpret()` call per test, no shared mutable
  state, no ordering assumption.

Contract (verified by TestContract before anything else)
--------------------------------------------------------
`interpret(request)` returns a structured result exposing at least:

    objective    -> the extracted goal
    target       -> the recipient (client / team / system / undetermined)
    tone         -> the detected tone
    depth        -> requested depth (in_depth / condensed / standard)
    constraints  -> collection of explicit constraints (may be empty)

Empty input ("" / None / whitespace) returns a neutral result, it does not raise.

Languages
---------
`interpret()` detects the language (EN / FR / ES / IT / PT) and picks the
matching lexicon. The values it returns stay canonical whatever the language,
so the same request written in five languages must produce the same framing -
`TestMultilingual` asserts exactly that.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping, Sequence

import pytest

from khirami_agent import interpret

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

F_OBJECTIVE = "objective"
F_TARGET = "target"
F_TONE = "tone"
F_DEPTH = "depth"
F_CONSTRAINTS = "constraints"

CONTRACT_FIELDS = (F_OBJECTIVE, F_TARGET, F_TONE, F_DEPTH, F_CONSTRAINTS)

# Vocabulary the implementation is expected to produce.
VOCAB_CLIENT = ("client",)
VOCAB_TEAM = ("team",)
VOCAB_SYSTEM = ("system",)
VOCAB_DEPTH_DEEP = ("in_depth",)
VOCAB_DEPTH_SHORT = ("condensed",)
VOCAB_PRECISION = ("precision",)
VOCAB_BREVITY = ("brevity",)
VOCAB_NO_TARGET = ("undetermined",)

# Neutral fallback returned when no objective is stated.
VOCAB_NEUTRAL_OBJECTIVE = ("answer",)

# Same request in five languages: the lexicons differ, the framing must not.
LANGUAGES = ("en", "fr", "es", "it", "pt")

REQUEST_DETAILED_ANALYSIS = {
    "en": "Write a detailed analysis for the client, with a formal tone, only about pricing.",
    "fr": "Rédige une analyse détaillée pour le client, avec un ton formel, "
    "uniquement sur la partie tarifaire.",
    "es": "Escribe un análisis detallado para el cliente, con un tono formal, "
    "únicamente sobre los precios.",
    "it": "Scrivi un'analisi dettagliata per il cliente, con un tono formale, "
    "unicamente sui prezzi.",
    "pt": "Escreva uma análise detalhada para o cliente, com um tom formal, "
    "somente sobre os preços.",
}

REQUEST_BRIEF_SUMMARY = {
    "en": "Give me a brief summary for the team, no fluff.",
    "fr": "Fais-moi un résumé bref pour l'équipe, sans blabla.",
    "es": "Dame un resumen breve para el equipo, sin rodeos.",
    "it": "Fammi un riassunto breve per la squadra, senza fronzoli.",
    "pt": "Faça um resumo breve para a equipe, sem rodeios.",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def read(result: object, field: str) -> object:
    """Read one contract field, whether the result is a Mapping or an object."""
    if isinstance(result, Mapping):
        assert field in result, f"missing field {field!r} in result: {result!r}"
        return result[field]
    assert hasattr(result, field), f"missing attribute {field!r} on result: {result!r}"
    return getattr(result, field)


def flatten(value: object) -> str:
    """Turn any field value (str, list, dict, None) into a normalized searchable string."""
    if value is None:
        return ""
    if isinstance(value, Mapping):
        parts = [f"{k} {v}" for k, v in value.items()]
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        parts = [str(item) for item in value]
    else:
        parts = [str(value)]
    decomposed = unicodedata.normalize("NFKD", " ".join(parts))
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def mentions(value: object, *tokens: str) -> bool:
    """True if any token appears in the field value, ignoring case and accents."""
    haystack = flatten(value)
    return any(flatten(token) in haystack for token in tokens)


def is_blank(value: object) -> bool:
    """True for the neutral/empty forms a field can take."""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0
    return False


def as_size(value: object) -> int:
    """Number of items in a collection field, 0 when the field is empty."""
    if value is None:
        return 0
    if isinstance(value, str):
        return 1 if value.strip() else 0
    if isinstance(value, (list, tuple, set, dict)):
        return len(value)
    return 1


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def analyze():
    """Call interpret() and assert the structural contract before the test's own assertions."""

    def _analyze(request):
        result = interpret(request)
        assert result is not None, f"interpret({request!r}) returned None"
        for field in CONTRACT_FIELDS:
            read(result, field)  # raises AssertionError if the contract is broken
        return result

    return _analyze


# ---------------------------------------------------------------------------
# 0. Contract - the shape of the returned object
# ---------------------------------------------------------------------------


class TestContract:
    """Everything below depends on this. If these fail, fix the shape first."""

    def test_returns_all_contract_fields(self):
        result = interpret("Write an onboarding email for a new client.")

        for field in CONTRACT_FIELDS:
            read(result, field)

    def test_constraints_field_is_a_collection(self, analyze):
        result = analyze("Summarize this report in 3 bullet points.")

        constraints = read(result, F_CONSTRAINTS)
        assert isinstance(constraints, (list, tuple, set)), (
            f"{F_CONSTRAINTS} should be a collection, got {type(constraints).__name__}"
        )

    def test_is_deterministic(self):
        request = "Explain our pricing model to a client, keep it short."

        first = interpret(request)
        second = interpret(request)

        for field in CONTRACT_FIELDS:
            assert flatten(read(first, field)) == flatten(read(second, field)), (
                f"field {field!r} is not deterministic across two identical calls"
            )

    def test_does_not_mutate_its_input(self):
        request = "Draft a status update for the team."
        original = str(request)

        interpret(request)

        assert request == original, "interpret() must not mutate the request it receives"


# ---------------------------------------------------------------------------
# 1. Simple case - plain text with a clear objective
# ---------------------------------------------------------------------------


class TestSimpleRequest:
    def test_clear_objective_is_extracted(self, analyze):
        result = analyze("Write a follow-up email to a client after a demo call.")

        objective = read(result, F_OBJECTIVE)
        assert not is_blank(objective), f"objective should be extracted, got {objective!r}"

    def test_plain_request_yields_no_constraint(self, analyze):
        result = analyze("Explain what our AI agent does.")

        constraints = read(result, F_CONSTRAINTS)
        assert as_size(constraints) == 0, (
            f"no constraint expected on a plain request, got {constraints!r}"
        )

    def test_objective_reflects_the_requested_action(self, analyze):
        result = analyze("Summarize the client meeting notes.")

        objective = read(result, F_OBJECTIVE)
        assert mentions(objective, "summar"), (
            f"objective should reflect the summarize intent, got {objective!r}"
        )


# ---------------------------------------------------------------------------
# 2 & 3. Edge cases - empty, None, whitespace, oversized input
# ---------------------------------------------------------------------------


class TestEdgeCases:
    @pytest.mark.parametrize(
        "request_text",
        ["", None, "   ", "\n\t  \n"],
        ids=["empty-string", "none", "spaces", "whitespace-mix"],
    )
    def test_blank_input_is_handled_without_crashing(self, request_text):
        result = interpret(request_text)

        assert result is not None, f"interpret({request_text!r}) should return a neutral result"
        for field in CONTRACT_FIELDS:
            read(result, field)

    @pytest.mark.parametrize("request_text", ["", None], ids=["empty-string", "none"])
    def test_blank_input_extracts_no_objective(self, request_text):
        result = interpret(request_text)

        objective = read(result, F_OBJECTIVE)
        assert is_blank(objective) or mentions(objective, *VOCAB_NEUTRAL_OBJECTIVE), (
            f"blank input must not invent an objective, got {objective!r}"
        )

    @pytest.mark.parametrize("request_text", ["", None], ids=["empty-string", "none"])
    def test_blank_input_extracts_no_constraint(self, request_text):
        result = interpret(request_text)

        assert as_size(read(result, F_CONSTRAINTS)) == 0, "blank input must yield no constraint"

    def test_oversized_input_is_handled(self, analyze):
        request = "Write a report for the client. " * 500

        result = analyze(request)

        assert not is_blank(read(result, F_OBJECTIVE)), "long input should still be interpreted"


# ---------------------------------------------------------------------------
# 4. Constraints
# ---------------------------------------------------------------------------


class TestConstraints:
    @pytest.mark.parametrize(
        "request_text",
        [
            "Explain the architecture, be precise.",
            "Give me the answer, keep it brief.",
            "Summarize this in 3 bullet points maximum.",
            "Answer briefly, in under 100 words.",
        ],
        ids=["precision", "brevity", "max-bullets", "word-limit"],
    )
    def test_explicit_constraint_is_captured(self, analyze, request_text):
        result = analyze(request_text)

        constraints = read(result, F_CONSTRAINTS)
        assert as_size(constraints) >= 1, (
            f"expected at least one constraint for {request_text!r}, got {constraints!r}"
        )

    def test_precision_constraint_is_identified(self, analyze):
        result = analyze("Explain the fallback logic, be precise and factual.")

        constraints = read(result, F_CONSTRAINTS)
        assert mentions(constraints, *VOCAB_PRECISION), (
            f"precision constraint not identified in {constraints!r}"
        )

    def test_brevity_constraint_is_identified(self, analyze):
        result = analyze("Explain the fallback logic, keep it short.")

        constraints = read(result, F_CONSTRAINTS)
        assert mentions(constraints, *VOCAB_BREVITY), (
            f"brevity constraint not identified in {constraints!r}"
        )

    def test_two_constraints_are_both_captured(self, analyze):
        result = analyze("Explain the fallback logic: be precise, and keep it short.")

        constraints = read(result, F_CONSTRAINTS)
        assert as_size(constraints) >= 2, (
            f"both constraints should be captured, got {constraints!r}"
        )

    def test_constraint_does_not_replace_the_objective(self, analyze):
        result = analyze("Draft the onboarding message, keep it short.")

        assert not is_blank(read(result, F_OBJECTIVE)), (
            "a constraint must not erase the extracted objective"
        )


# ---------------------------------------------------------------------------
# 5. Explicit target
# ---------------------------------------------------------------------------


class TestTarget:
    @pytest.mark.parametrize(
        ("request_text", "expected_vocab"),
        [
            ("Write an onboarding message for the client.", VOCAB_CLIENT),
            ("Write a weekly update for the team.", VOCAB_TEAM),
            ("Generate a maintenance report for the system.", VOCAB_SYSTEM),
        ],
        ids=["client", "team", "system"],
    )
    def test_explicit_target_is_detected(self, analyze, request_text, expected_vocab):
        result = analyze(request_text)

        target = read(result, F_TARGET)
        assert mentions(target, *expected_vocab), (
            f"expected target among {expected_vocab} for {request_text!r}, got {target!r}"
        )

    def test_distinct_targets_produce_distinct_results(self, analyze):
        for_client = analyze("Write the release note for the client.")
        for_team = analyze("Write the release note for the team.")

        assert flatten(read(for_client, F_TARGET)) != flatten(read(for_team, F_TARGET)), (
            "client and team requests must not resolve to the same target"
        )

    def test_missing_target_stays_neutral(self, analyze):
        result = analyze("List the three main risks.")

        target = read(result, F_TARGET)
        assert is_blank(target) or mentions(target, *VOCAB_NO_TARGET), (
            f"no target should be inferred when none is stated, got {target!r}"
        )


# ---------------------------------------------------------------------------
# 6. Tone
# ---------------------------------------------------------------------------


class TestTone:
    def test_explicit_tone_is_detected(self, analyze):
        result = analyze("Answer the client in a formal, professional tone.")

        tone = read(result, F_TONE)
        assert not is_blank(tone), f"an explicit tone request should set the tone, got {tone!r}"

    def test_opposite_tones_are_not_collapsed(self, analyze):
        formal = analyze("Reply to the client in a formal tone.")
        casual = analyze("Reply to the client in a casual, friendly tone.")

        assert flatten(read(formal, F_TONE)) != flatten(read(casual, F_TONE)), (
            "formal and casual requests must not produce the same tone"
        )

    def test_tone_does_not_leak_into_the_objective(self, analyze):
        neutral = analyze("Write the incident summary.")
        toned = analyze("Write the incident summary in a formal tone.")

        assert flatten(read(neutral, F_OBJECTIVE)) == flatten(read(toned, F_OBJECTIVE)), (
            "adding a tone must not change the extracted objective"
        )


# ---------------------------------------------------------------------------
# 7. Depth
# ---------------------------------------------------------------------------


class TestDepth:
    @pytest.mark.parametrize(
        "request_text",
        [
            "Give me an in-depth analysis of the fallback strategy.",
            "Explain the architecture in detail, step by step.",
        ],
        ids=["in-depth", "detailed"],
    )
    def test_deep_request_is_detected(self, analyze, request_text):
        result = analyze(request_text)

        depth = read(result, F_DEPTH)
        assert mentions(depth, *VOCAB_DEPTH_DEEP), (
            f"expected an in-depth reading for {request_text!r}, got {depth!r}"
        )

    @pytest.mark.parametrize(
        "request_text",
        [
            "Give me a synthetic overview of the fallback strategy.",
            "Quick summary of the architecture, high level only.",
        ],
        ids=["synthetic", "high-level"],
    )
    def test_condensed_request_is_detected(self, analyze, request_text):
        result = analyze(request_text)

        depth = read(result, F_DEPTH)
        assert mentions(depth, *VOCAB_DEPTH_SHORT), (
            f"expected a condensed reading for {request_text!r}, got {depth!r}"
        )

    def test_deep_and_condensed_do_not_collapse(self, analyze):
        deep = analyze("Give me an in-depth analysis of the pricing model.")
        short = analyze("Give me a synthetic overview of the pricing model.")

        assert flatten(read(deep, F_DEPTH)) != flatten(read(short, F_DEPTH)), (
            "in-depth and condensed requests must not resolve to the same depth"
        )


# ---------------------------------------------------------------------------
# 8. Mixed signals
# ---------------------------------------------------------------------------


class TestMixedSignals:
    MIXED = "Write a short onboarding email for the client, formal tone, be precise."

    def test_all_signals_are_extracted_together(self, analyze):
        result = analyze(self.MIXED)

        assert not is_blank(read(result, F_OBJECTIVE)), "objective missing in a mixed request"
        assert mentions(read(result, F_TARGET), *VOCAB_CLIENT), "target missing in a mixed request"
        assert not is_blank(read(result, F_TONE)), "tone missing in a mixed request"
        assert as_size(read(result, F_CONSTRAINTS)) >= 1, "constraints missing in a mixed request"

    def test_signals_do_not_cancel_each_other(self, analyze):
        mixed = analyze(self.MIXED)
        target_only = analyze("Write an onboarding email for the client.")

        assert flatten(read(mixed, F_TARGET)) == flatten(read(target_only, F_TARGET)), (
            "the target must be extracted identically with or without the other signals"
        )

    def test_constraint_and_depth_coexist(self, analyze):
        result = analyze(
            "Give the team an in-depth breakdown of the incident, in 5 bullet points max."
        )

        assert mentions(read(result, F_TARGET), *VOCAB_TEAM)
        assert mentions(read(result, F_DEPTH), *VOCAB_DEPTH_DEEP)
        assert as_size(read(result, F_CONSTRAINTS)) >= 1

    def test_signal_order_does_not_change_the_result(self, analyze):
        first = analyze("For the client, in a formal tone: write a short release note.")
        second = analyze("Write a short release note for the client, in a formal tone.")

        for field in (F_TARGET, F_TONE):
            assert flatten(read(first, field)) == flatten(read(second, field)), (
                f"field {field!r} should not depend on the order of the signals"
            )


# ---------------------------------------------------------------------------
# 9. Multilingual - EN / FR / ES / IT / PT
# ---------------------------------------------------------------------------


class TestMultilingual:
    """
    The lexicons are per-language, the contract values are canonical.

    Each request below is the same demand written in five languages. Whatever
    the language, `interpret()` must return the same framing.
    """

    @pytest.mark.parametrize("language", LANGUAGES)
    def test_detailed_analysis_is_framed_in_every_language(self, analyze, language):
        result = analyze(REQUEST_DETAILED_ANALYSIS[language])

        assert not is_blank(read(result, F_OBJECTIVE)), f"[{language}] objective missing"
        assert mentions(read(result, F_TARGET), *VOCAB_CLIENT), (
            f"[{language}] client target not detected, got {read(result, F_TARGET)!r}"
        )
        assert not is_blank(read(result, F_TONE)), f"[{language}] tone missing"
        assert mentions(read(result, F_DEPTH), *VOCAB_DEPTH_DEEP), (
            f"[{language}] in-depth reading not detected, got {read(result, F_DEPTH)!r}"
        )
        assert as_size(read(result, F_CONSTRAINTS)) >= 1, (
            f"[{language}] explicit constraint not captured"
        )

    @pytest.mark.parametrize("language", LANGUAGES)
    def test_brief_summary_is_framed_in_every_language(self, analyze, language):
        result = analyze(REQUEST_BRIEF_SUMMARY[language])

        assert not is_blank(read(result, F_OBJECTIVE)), f"[{language}] objective missing"
        assert mentions(read(result, F_TARGET), *VOCAB_TEAM), (
            f"[{language}] team target not detected, got {read(result, F_TARGET)!r}"
        )
        assert not is_blank(read(result, F_TONE)), f"[{language}] tone missing"
        assert mentions(read(result, F_DEPTH), *VOCAB_DEPTH_SHORT), (
            f"[{language}] condensed reading not detected, got {read(result, F_DEPTH)!r}"
        )
        assert mentions(read(result, F_CONSTRAINTS), *VOCAB_BREVITY), (
            f"[{language}] brevity constraint not captured"
        )

    @pytest.mark.parametrize(
        "requests",
        [REQUEST_DETAILED_ANALYSIS, REQUEST_BRIEF_SUMMARY],
        ids=["detailed-analysis", "brief-summary"],
    )
    def test_the_same_demand_yields_the_same_framing_across_languages(self, analyze, requests):
        framings = {language: analyze(text) for language, text in requests.items()}

        for field in CONTRACT_FIELDS:
            values = {
                language: flatten(read(result, field)) for language, result in framings.items()
            }
            assert len(set(values.values())) == 1, (
                f"field {field!r} diverges across languages: {values!r}"
            )


# ---------------------------------------------------------------------------
# 10. Missing information - regression tests
# ---------------------------------------------------------------------------


class TestMissingVolumes:
    """`volumes` used to be unreachable: the measures dict always has three keys."""

    def test_missing_quantity_is_reported(self):
        frame = interpret("Write an action plan for the team on ticket handling delays.")

        assert frame["measures"]["quantity"] == ""
        assert "volumes" in frame["missing_info"]

    def test_stated_quantity_is_not_reported(self):
        frame = interpret("Write an action plan for the team to cut ticket delays by 30% by Q3.")

        assert frame["measures"]["quantity"]
        assert "volumes" not in frame["missing_info"]


class TestQuantityUnits:
    """Unit symbols used to be dropped by tokenization: "30%" became "30"."""

    @pytest.mark.parametrize(
        ("request_text", "expected"),
        [
            ("Cut response times by 30% before Q3.", "30%"),
            ("Reduce churn by 15 % by June.", "15%"),
            ("Keep a budget of 200€ for Q3.", "200€"),
            ("Spend $300 on tooling.", "$300"),
            ("Reduce delays by 30 before Q3.", "30"),
            ("Answer in under 100 words.", "100 words"),
        ],
        ids=["percent", "spaced-percent", "euro-suffix", "dollar-prefix", "no-symbol", "unit-word"],
    )
    def test_quantity_keeps_its_unit(self, request_text, expected):
        assert interpret(request_text)["measures"]["quantity"] == expected

    def test_symbol_is_read_from_the_same_number(self):
        frame = interpret("We have 2 agents and 30% growth.")

        assert frame["measures"]["quantity"] == "2 agents"
