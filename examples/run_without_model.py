"""
See Khirami Agent work without a model or an API key.

Usage (from the repository root, after `pip install -e .`):

    python examples/run_without_model.py

Shows, for the same request:
  1. the frame produced by `interpret()`,
  2. the mandate note of the deterministic stack,
  3. the engagement pipeline without a client: empty contracts, declared gaps,
  4. the clarification gate stopping a vague request.
No network call is made.
"""

from __future__ import annotations

import json
import sys

from khirami_agent import KhiramiAgent, interpret, run_engagement

REQUEST = (
    "Our support team is overwhelmed. We need a diagnosis and an action plan "
    "to cut response times by 30% before Q3."
)
VAGUE_REQUEST = "help"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("# 1. Frame\n")
    frame = {key: value for key, value in interpret(REQUEST).items() if key != "request"}
    print(json.dumps(frame, indent=2))

    print("\n# 2. Mandate note (deterministic, no model)\n")
    note = KhiramiAgent().run(REQUEST, modern=True)
    print(note["executive_summary"])
    print()
    for recommendation in note["recommendations"]:
        print(f"- {recommendation}")

    print("\n# 3. Engagement without a model client\n")
    state = run_engagement(REQUEST, business_context={"sector": "support"})
    print(f"Mode: {state.meta.mode} · Sector table: {state.meta.sector_table}")
    print(f"Executive summary: {state.strategy['executive_summary']!r} (nothing is invented)")
    print("Declared gaps:")
    for gap in state.meta.degraded:
        print(f"- {gap}")

    print("\n# 4. Clarification gate on a vague request\n")
    vague = run_engagement(VAGUE_REQUEST)
    print(f"Ready: {vague.clarification['ready']}")
    for question in vague.clarification["questions"]:
        print(f"- {question}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
