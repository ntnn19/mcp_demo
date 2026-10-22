"""Smoke test for the summarize CLI."""

import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT = os.path.join(ROOT, "data", "findings.json")


def test_cli_produces_three_pngs():
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [sys.executable, "-m", "app.summarize", "--input", INPUT, "--out", tmp],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        for name in ("diseases.png", "interactions.png", "structures.png"):
            path = os.path.join(tmp, name)
            assert os.path.isfile(path), f"missing {name}"
            assert os.path.getsize(path) > 0, f"{name} is empty"
