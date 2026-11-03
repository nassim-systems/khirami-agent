"""
Smoke tests for the scripts in `examples/`, so they cannot silently break.

No network call: the model-free example runs end to end, and the Claude
example is only checked for its behaviour when no API key is set.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

EXAMPLES = pathlib.Path(__file__).resolve().parent.parent / "examples"


def run_example(name, env):
    return subprocess.run(
        [sys.executable, str(EXAMPLES / name)],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )


def environment_without_key():
    env = dict(os.environ)
    env.pop("ANTHROPIC_API_KEY", None)
    source = str(EXAMPLES.parent / "src")
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [source, env.get("PYTHONPATH")]))
    return env


def test_model_free_example_runs():
    result = run_example("run_without_model.py", environment_without_key())

    assert result.returncode == 0, result.stderr
    assert "no generation client configured" in result.stdout
    assert "Ready: False" in result.stdout


def test_claude_example_fails_cleanly_without_a_key():
    result = run_example("run_engagement.py", environment_without_key())

    assert result.returncode == 2
    assert "ANTHROPIC_API_KEY is not set" in result.stderr
    assert "Traceback" not in result.stderr


def test_claude_example_prints_a_full_report(monkeypatch, tmp_path, capsys):
    """Run the Claude example in-process, with the canned-JSON stub as the model."""
    import importlib.util
    import json

    from test_engagement import client_stub

    spec = importlib.util.spec_from_file_location("run_engagement", EXAMPLES / "run_engagement.py")
    example = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(example)

    class StubClient:
        model = "stub"

        def __init__(self, model=None):
            self._call = client_stub()

        def __call__(self, system_prompt, task_prompt):
            return self._call(system_prompt, task_prompt)

    monkeypatch.setattr(example, "AnthropicClient", StubClient)
    output_file = tmp_path / "engagement.json"

    assert example.main(["--json", str(output_file)]) == 0

    report = capsys.readouterr().out
    for heading in ("Diagnostic — root causes", "Action plan — now", "Next step"):
        assert heading in report
    assert "Model requests: 4" in report
    assert json.loads(output_file.read_text(encoding="utf-8"))["meta"]["guard_status"] == "pass"
