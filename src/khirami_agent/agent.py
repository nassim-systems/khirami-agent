"""
Agent entry point — one `run()` method, two deterministic stacks.

    KhiramiAgent().run(request)               → Markdown text
        interpret → orchestrate → generate_output

    KhiramiAgent().run(request, modern=True)  → structured dictionary
        interpret → run_agent → render_output

Neither stack calls a language model. The model-backed consulting pipeline is
`engagement.run_engagement()`.
"""

from __future__ import annotations

from typing import Any

from .framing import interpret
from .planning import orchestrate
from .rendering import generate_output, render_output
from .selection import run_agent


class KhiramiRouter:
    """
    Pass-through to `orchestrate()`.

    No logic, no state: every decision belongs to `orchestrate()`. The router
    is the single hand-off point between the agent and the planning path.
    """

    def route(self, request: str) -> dict[str, Any]:
        """Delegate to `orchestrate()` and relay its plan unchanged."""
        return orchestrate(request)


class KhiramiAgent:
    """Functional entry point of Khirami Agent."""

    def __init__(self) -> None:
        self.router = KhiramiRouter()

    def run(self, request: str, modern: bool = False) -> str | dict[str, Any]:
        """
        Process a text request and return the deliverable.

        `modern=False` (default) — the router plans, `generate_output()` writes,
        a Markdown string is returned.

        `modern=True` — `interpret()` frames, `run_agent()` assembles,
        `render_output()` projects; a dictionary with the keys
        executive_summary, analysis, recommendations, format and meta is
        returned. This path does not go through the router.

        Only `interpret()` reads the raw request, on both paths.
        """
        if modern:
            return render_output(run_agent(interpret(request)))

        return generate_output(self.router.route(request))
