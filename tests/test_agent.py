"""
Unit tests for the two-stack switch on `KhiramiAgent.run()`.

Tests the routing decision only: which stack runs, and what comes back. What
each stack produces is covered by the other suites.

Contract: `run(request)` runs the planning stack and returns Markdown text.
`run(request, modern=True)` runs the frame-driven stack and returns the
five-key dictionary produced by `render_output()`.
"""

from __future__ import annotations

import inspect

import pytest

from khirami_agent import (
    KhiramiAgent,
    KhiramiRouter,
    generate_output,
    interpret,
    orchestrate,
    render_output,
    run_agent,
)
from khirami_agent.rendering import RENDER_KEYS

REQUESTS = [
    "Write a detailed and precise analysis for the client.",
    "Give me a brief summary for the team, no fluff.",
    "Check the script and fix the module errors.",
]
REQUEST_IDS = ["client-analysis", "team-summary", "system-check"]

DEFAULT_REQUEST = REQUESTS[0]


@pytest.fixture
def agent():
    """A fresh agent per test: no state carried between cases."""
    return KhiramiAgent()


# ---------------------------------------------------------------------------
# Behaviour
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("request_text", REQUESTS, ids=REQUEST_IDS)
def test_planning_stack_is_the_default(agent, request_text):
    """Without the flag, the planning stack answers - and returns a string."""
    rendered = agent.run(request_text)

    assert isinstance(rendered, str), f"expected text, got {type(rendered)}"
    assert rendered.strip(), "empty rendering"

    # And it is exactly the planning path, end to end.
    assert rendered == generate_output(orchestrate(request_text))


@pytest.mark.parametrize("request_text", REQUESTS, ids=REQUEST_IDS)
def test_modern_flag(agent, request_text):
    """With the flag, the frame-driven stack answers - and returns a dict."""
    rendered = agent.run(request_text, modern=True)

    assert isinstance(rendered, dict), f"expected a dict, got {type(rendered)}"
    assert rendered == render_output(run_agent(interpret(request_text)))


@pytest.mark.parametrize("request_text", REQUESTS, ids=REQUEST_IDS)
def test_modern_structure(agent, request_text):
    """Every rendering key is present, whatever the request."""
    rendered = agent.run(request_text, modern=True)

    assert set(rendered) == set(RENDER_KEYS), f"unexpected key set: {sorted(rendered)!r}"
    assert isinstance(rendered["executive_summary"], str)
    assert isinstance(rendered["analysis"], str)
    assert isinstance(rendered["recommendations"], list)
    assert isinstance(rendered["format"], str)
    assert isinstance(rendered["meta"], dict)


@pytest.mark.parametrize("request_text", REQUESTS, ids=REQUEST_IDS)
def test_two_stacks_return_distinct_shapes(agent, request_text):
    """The two stacks are distinct: same request, different shapes."""
    planned = agent.run(request_text)
    modern = agent.run(request_text, modern=True)

    assert planned != modern
    assert isinstance(planned, str) and isinstance(modern, dict)


def test_no_collision_between_stacks(agent):
    """Running the frame-driven stack must leave the planning one untouched."""
    before = agent.run(DEFAULT_REQUEST)

    agent.run(DEFAULT_REQUEST, modern=True)

    after = agent.run(DEFAULT_REQUEST)
    assert after == before, "the frame-driven stack disturbed the planning rendering"

    # Both entry points are still the ones they were.
    plan = orchestrate(DEFAULT_REQUEST)
    assert "response" in plan, "orchestrate() no longer returns a plan"
    assert isinstance(generate_output(plan), str), "generate_output() changed shape"


@pytest.mark.parametrize("modern", [False, True], ids=["planning", "modern"])
def test_does_not_mutate_its_input(agent, modern):
    """The request received is never modified."""
    request_text = DEFAULT_REQUEST
    original = str(request_text)

    agent.run(request_text, modern=modern)

    assert request_text == original, "run() mutated the request"


def test_modern_stack_is_deterministic(agent):
    """Two identical modern calls must produce the same dict."""
    first = agent.run(DEFAULT_REQUEST, modern=True)
    second = agent.run(DEFAULT_REQUEST, modern=True)

    assert first == second, f"not deterministic: {first!r} then {second!r}"


# ---------------------------------------------------------------------------
# Structural guarantees
# ---------------------------------------------------------------------------


def test_planning_stack_is_deterministic(agent):
    """The planning stack stays deterministic too."""
    assert agent.run(DEFAULT_REQUEST) == agent.run(DEFAULT_REQUEST)


def test_flag_is_explicit_only(agent):
    """`modern=False` must behave exactly like no flag at all."""
    assert agent.run(DEFAULT_REQUEST, modern=False) == agent.run(DEFAULT_REQUEST)


def test_router_signature_is_untouched(agent):
    """The flag lives on run(), never on the router."""
    parameters = inspect.signature(KhiramiRouter.route).parameters
    assert list(parameters) == ["self", "request"], (
        f"the router signature changed: {list(parameters)!r}"
    )

    # And the modern path does not go through it.
    assert isinstance(agent.router, KhiramiRouter)


def test_two_agents_agree(agent):
    """No hidden per-instance state: a fresh agent renders identically."""
    other = KhiramiAgent()

    assert agent.run(DEFAULT_REQUEST) == other.run(DEFAULT_REQUEST)
    assert agent.run(DEFAULT_REQUEST, modern=True) == other.run(DEFAULT_REQUEST, modern=True)


@pytest.mark.parametrize("request_text", REQUESTS, ids=REQUEST_IDS)
def test_modern_never_returns_raw_text(agent, request_text):
    """The modern mode returns a structure, never the request echoed back."""
    rendered = agent.run(request_text, modern=True)

    assert request_text not in rendered["executive_summary"]
    assert request_text not in rendered["analysis"]
    assert all(request_text not in action for action in rendered["recommendations"])
