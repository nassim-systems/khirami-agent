"""
Khirami Agent — a deterministic framing and orchestration core for an AI
business-consulting agent.

Public API
    interpret()           frame a free-text request
    orchestrate()         plan a deliverable from a request
    generate_output()     render a plan as Markdown
    run_agent()           assemble frame-driven decisions
    render_output()       render a consulting deliverable
    run_engagement()      run the model-backed consulting pipeline
    KhiramiAgent          single entry point over the two deterministic stacks
    AnthropicClient       model client for run_engagement() (optional extra)
"""

from .agent import KhiramiAgent, KhiramiRouter
from .anthropic_client import AnthropicClient
from .constraints import detect_language, extract_constraints
from .engagement import EngagementMeta, EngagementState, run_engagement
from .framing import interpret
from .planning import orchestrate
from .rendering import generate_output, render_output
from .selection import (
    enforce_rules,
    orchestrate_frame,
    run_agent,
    select_capabilities,
    select_format,
)

__version__ = "0.1.0"

__all__ = [
    "AnthropicClient",
    "EngagementMeta",
    "EngagementState",
    "KhiramiAgent",
    "KhiramiRouter",
    "__version__",
    "detect_language",
    "enforce_rules",
    "extract_constraints",
    "generate_output",
    "interpret",
    "orchestrate",
    "orchestrate_frame",
    "render_output",
    "run_agent",
    "run_engagement",
    "select_capabilities",
    "select_format",
]
