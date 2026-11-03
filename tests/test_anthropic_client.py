"""
Unit tests for `AnthropicClient`, with a simulated SDK: no network call.

The stand-in SDK mirrors the names the client uses (`Anthropic`, the error
classes and their hierarchy) and answers with canned messages, so these tests
run without the real package and without an API key.
"""

from __future__ import annotations

import json
import sys
from types import SimpleNamespace

import pytest
from test_engagement import DEMAND, client_stub

from khirami_agent import run_engagement
from khirami_agent.anthropic_client import (
    API_KEY_ENV,
    DEFAULT_MODEL,
    MODEL_ENV,
    AnthropicClient,
    AuthenticationFailedError,
    InvalidJSONResponseError,
    MissingAPIKeyError,
    MissingDependencyError,
    ModelAPIError,
    ModelConnectionError,
    ModelTimeoutError,
    RateLimitedError,
)

FAKE_KEY = "test-key-that-must-never-leak"


# ---------------------------------------------------------------------------
# Simulated SDK
# ---------------------------------------------------------------------------


class FakeAPIError(Exception):
    pass


class FakeAPIConnectionError(FakeAPIError):
    pass


class FakeAPITimeoutError(FakeAPIConnectionError):
    pass


class FakeAPIStatusError(FakeAPIError):
    status_code = 500


class FakeAuthenticationError(FakeAPIStatusError):
    status_code = 401


class FakeRateLimitError(FakeAPIStatusError):
    status_code = 429


def text_message(text, stop_reason="end_turn"):
    """A Messages API response holding one text block."""
    return SimpleNamespace(
        content=[SimpleNamespace(type="text", text=text)], stop_reason=stop_reason
    )


def fake_sdk(respond):
    """
    Build a stand-in `anthropic` module.

    `respond(**create_kwargs)` returns a message or raises; every constructor
    and create() call is recorded on the returned namespace.
    """
    sdk = SimpleNamespace(
        AuthenticationError=FakeAuthenticationError,
        RateLimitError=FakeRateLimitError,
        APITimeoutError=FakeAPITimeoutError,
        APIConnectionError=FakeAPIConnectionError,
        APIStatusError=FakeAPIStatusError,
        init_kwargs=[],
        calls=[],
    )

    class Messages:
        def create(self, **kwargs):
            sdk.calls.append(kwargs)
            return respond(**kwargs)

    class Anthropic:
        def __init__(self, **kwargs):
            sdk.init_kwargs.append(kwargs)
            self.messages = Messages()

    sdk.Anthropic = Anthropic
    return sdk


def answering(text, stop_reason="end_turn"):
    return fake_sdk(lambda **_: text_message(text, stop_reason))


def raising(error):
    def respond(**_):
        raise error

    return fake_sdk(respond)


@pytest.fixture(autouse=True)
def api_key(monkeypatch):
    """A fake key for every test, and no model override from the environment."""
    monkeypatch.setenv(API_KEY_ENV, FAKE_KEY)
    monkeypatch.delenv(MODEL_ENV, raising=False)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def test_missing_api_key_fails_before_any_sdk_call(monkeypatch):
    monkeypatch.delenv(API_KEY_ENV)
    sdk = answering("{}")

    with pytest.raises(MissingAPIKeyError, match=API_KEY_ENV):
        AnthropicClient(sdk=sdk)

    assert sdk.init_kwargs == [], "no SDK client may be built without a key"


def test_missing_sdk_gives_an_install_hint(monkeypatch):
    monkeypatch.setitem(sys.modules, "anthropic", None)

    with pytest.raises(MissingDependencyError, match=r"\.\[anthropic\]"):
        AnthropicClient()


def test_api_key_is_never_passed_or_stored():
    sdk = answering("{}")
    client = AnthropicClient(sdk=sdk)

    assert "api_key" not in sdk.init_kwargs[0]
    assert FAKE_KEY not in repr(vars(client))


def test_timeout_and_retries_are_forwarded_to_the_sdk():
    sdk = answering("{}")

    AnthropicClient(timeout=30.0, max_retries=1, sdk=sdk)

    assert sdk.init_kwargs == [{"timeout": 30.0, "max_retries": 1}]


def test_default_model():
    assert AnthropicClient(sdk=answering("{}")).model == DEFAULT_MODEL


def test_model_from_environment(monkeypatch):
    monkeypatch.setenv(MODEL_ENV, "claude-opus-5-5")

    assert AnthropicClient(sdk=answering("{}")).model == "claude-opus-5-5"


def test_model_argument_wins_over_environment(monkeypatch):
    monkeypatch.setenv(MODEL_ENV, "claude-opus-5-5")

    assert AnthropicClient("claude-haiku-5-5", sdk=answering("{}")).model == "claude-haiku-5-5"


# ---------------------------------------------------------------------------
# Requests and answers
# ---------------------------------------------------------------------------


def test_request_carries_model_system_prompt_and_task():
    sdk = answering('{"ok": true}')
    client = AnthropicClient("claude-haiku-5-5", max_tokens=512, sdk=sdk)

    client("SYSTEM", "TASK")

    assert sdk.calls == [
        {
            "model": "claude-haiku-5-5",
            "max_tokens": 512,
            "system": "SYSTEM",
            "messages": [{"role": "user", "content": "TASK"}],
        }
    ]


def test_json_object_is_returned_as_text():
    answer = AnthropicClient(sdk=answering('{"ready": true}'))("s", "t")

    assert json.loads(answer) == {"ready": True}


def test_code_fence_is_removed():
    answer = AnthropicClient(sdk=answering('```json\n{"ready": true}\n```'))("s", "t")

    assert json.loads(answer) == {"ready": True}


def test_non_json_answer_is_a_clear_error():
    client = AnthropicClient(sdk=answering("Sure! Here is my analysis."))

    with pytest.raises(InvalidJSONResponseError, match="invalid JSON"):
        client("s", "t")


def test_truncated_answer_names_max_tokens():
    client = AnthropicClient(sdk=answering('{"ready": tr', stop_reason="max_tokens"))

    with pytest.raises(InvalidJSONResponseError, match="max_tokens"):
        client("s", "t")


def test_json_that_is_not_an_object_is_rejected():
    client = AnthropicClient(sdk=answering("[1, 2, 3]"))

    with pytest.raises(InvalidJSONResponseError, match="expected an object"):
        client("s", "t")


@pytest.mark.parametrize(
    ("sdk_error", "expected"),
    [
        (FakeAuthenticationError(), AuthenticationFailedError),
        (FakeRateLimitError(), RateLimitedError),
        (FakeAPITimeoutError(), ModelTimeoutError),
        (FakeAPIConnectionError(), ModelConnectionError),
        (FakeAPIStatusError(), ModelAPIError),
    ],
    ids=["authentication", "rate-limit", "timeout", "connection", "other-status"],
)
def test_sdk_errors_are_mapped_to_clear_errors(sdk_error, expected):
    client = AnthropicClient(sdk=raising(sdk_error))

    with pytest.raises(expected) as caught:
        client("s", "t")

    assert FAKE_KEY not in str(caught.value), "an error message leaked the API key"


# ---------------------------------------------------------------------------
# End to end through the engagement pipeline
# ---------------------------------------------------------------------------


def test_engagement_runs_end_to_end_on_the_client():
    stub = client_stub()
    sdk = fake_sdk(
        lambda **kwargs: text_message(stub(kwargs["system"], kwargs["messages"][0]["content"]))
    )

    state = run_engagement(DEMAND, {"sector": "support"}, AnthropicClient(sdk=sdk), "full_audit")

    assert state.meta.degraded == []
    assert state.strategy["executive_summary"]
    assert state.audit["pass"] is True
    assert len(sdk.calls) == 4, "diagnostic, process, automation, strategy; clean guard skips"


def test_provider_errors_are_declared_as_gaps_by_the_pipeline():
    client = AnthropicClient(sdk=raising(FakeRateLimitError()))

    state = run_engagement(DEMAND, {}, client, "quick_scan")

    assert any("Rate limit" in note for note in state.meta.degraded)
    assert state.strategy["executive_summary"] == "", "nothing is invented"
