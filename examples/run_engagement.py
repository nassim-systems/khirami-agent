"""
Run a full consulting engagement on Claude.

Usage (from the repository root, after `pip install -e ".[anthropic]"`):

    python examples/run_engagement.py
    python examples/run_engagement.py --mode quick_scan
    python examples/run_engagement.py --model claude-opus-5-5 --json engagement.json

The API key is read from the ANTHROPIC_API_KEY environment variable only.
Every run calls a paid API: a full_audit sends between 4 and 12 requests.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from typing import Any

from khirami_agent import AnthropicClient, EngagementState, run_engagement
from khirami_agent.anthropic_client import ModelClientError
from khirami_agent.engagement import HORIZONS, MODES

DEFAULT_REQUEST = (
    "Our support team is overwhelmed. We need a diagnosis and an action plan "
    "to cut response times by 30% before Q3."
)


class CountingClient:
    """Wrap a model client and count the requests it sends."""

    def __init__(self, client: Any) -> None:
        self.client = client
        self.calls = 0

    def __call__(self, system_prompt: str, task_prompt: str) -> str:
        self.calls += 1
        return self.client(system_prompt, task_prompt)


def _section(title: str) -> None:
    print(f"\n## {title}\n")


def _bullets(items: list[Any], render: Any) -> None:
    if not items:
        print("- (none)")
    for item in items:
        print(f"- {render(item)}")


def print_report(state: EngagementState) -> None:
    """Print the engagement state as a readable Markdown report."""
    meta = state.meta
    print("# Khirami engagement")
    print(f"\nMode: {meta.mode} · Sector table: {meta.sector_table} · Guard: {meta.guard_status}")

    clarification = state.clarification or {}
    if not clarification.get("ready", True):
        _section("Clarification needed")
        _bullets(clarification.get("questions", []), str)
        return

    if state.diagnostic:
        _section("Diagnostic — root causes")
        _bullets(
            state.diagnostic["root_causes"],
            lambda c: (
                f"[{c.get('id')}] {c.get('cause')} "
                f"(impact {c.get('impact')}/5, effort {c.get('effort')}/5, "
                f"confidence {c.get('confidence')})"
            ),
        )

    if state.process_map:
        _section("Process — bottlenecks")
        _bullets(
            state.process_map["bottlenecks"],
            lambda b: (
                f"[{b.get('id')}] {b.get('description')} (root cause {b.get('linked_root_cause')})"
            ),
        )

    if state.automation_plan:
        _section("Automation — candidates")
        _bullets(
            state.automation_plan["candidates"],
            lambda a: f"[{a.get('id')}] {a.get('task')} — {a.get('mechanism')}",
        )
        _section("Automation — do not automate")
        _bullets(
            state.automation_plan["do_not_automate"],
            lambda d: f"{d.get('task')} — {d.get('reason')}",
        )

    if state.strategy:
        strategy = state.strategy
        _section("Executive summary")
        print(strategy.get("executive_summary") or "(empty)")
        for horizon in HORIZONS:
            _section(f"Action plan — {horizon}")
            _bullets(
                strategy["action_plan"][horizon],
                lambda a: (
                    f"{a.get('action')} (owner: {a.get('owner_role')}; "
                    f"done when: {a.get('done_when')}; linked to {a.get('linked_to')})"
                ),
            )
        _section("KPIs")
        _bullets(strategy["kpis"], lambda k: f"{k.get('metric')} — {k.get('target_direction')}")
        _section("Risks")
        _bullets(strategy["risks"], lambda r: f"{r.get('risk')} — {r.get('mitigation')}")
        _section("Next step")
        print(strategy.get("next_step") or "(empty)")

    if state.audit:
        _section("Guard violations")
        _bullets(
            state.audit["violations"],
            lambda v: f"{v.get('rule')} at {v.get('location')}: {v.get('fix')}",
        )

    _section("Declared gaps")
    _bullets(meta.degraded, str)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0].strip())
    parser.add_argument("--request", default=DEFAULT_REQUEST, help="client request")
    parser.add_argument("--sector", default="support", help="business sector table")
    parser.add_argument("--mode", default="full_audit", choices=sorted(MODES))
    parser.add_argument("--model", default=None, help="model ID (default: adapter default)")
    parser.add_argument("--json", metavar="PATH", help="also write the full state as JSON")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # model text may hold any character

    try:
        client = CountingClient(AnthropicClient(args.model))
    except ModelClientError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    started = time.monotonic()
    state = run_engagement(
        args.request,
        business_context={"sector": args.sector},
        client=client,
        mode=args.mode,
    )
    elapsed = time.monotonic() - started

    print_report(state)
    print(
        f"\n---\nModel: {client.client.model} · Model requests: {client.calls} · "
        f"Duration: {elapsed:.0f} s"
    )

    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(asdict(state), handle, ensure_ascii=False, indent=2)
        print(f"Full state written to {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
