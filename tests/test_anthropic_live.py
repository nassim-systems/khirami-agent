"""
One optional test against the real Anthropic API.

Skipped unless ANTHROPIC_API_KEY is set and the SDK is installed. It sends a
single short request (a few dozen tokens) and checks that a JSON object comes
back.
"""

from __future__ import annotations

import importlib.util
import json
import os

import pytest

from khirami_agent.anthropic_client import API_KEY_ENV, AnthropicClient

pytestmark = pytest.mark.skipif(
    not os.environ.get(API_KEY_ENV) or importlib.util.find_spec("anthropic") is None,
    reason=f"live test: needs {API_KEY_ENV} and the anthropic package",
)


def test_live_call_returns_a_json_object():
    client = AnthropicClient(max_tokens=64, max_retries=1)

    answer = client(
        "Answer with a single JSON object and nothing else.",
        'Return exactly this object: {"ok": true}',
    )

    assert json.loads(answer) == {"ok": True}
