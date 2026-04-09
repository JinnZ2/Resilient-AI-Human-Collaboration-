"""Tests for safe_ai_pipeline.sh and the pipeline checklist."""

import subprocess
from pathlib import Path

import pytest

from apps.protocol.checklist import load_checklist

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "safe_ai_pipeline.sh"


def test_pipeline_script_exists():
    assert SCRIPT.exists()
    assert SCRIPT.stat().st_mode & 0o111  # executable


def test_pipeline_help():
    result = subprocess.run(
        ["bash", str(SCRIPT), "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "Usage:" in result.stdout
    assert "--preflight" in result.stdout
    assert "--verify-model" in result.stdout


def test_pipeline_preflight():
    result = subprocess.run(
        ["bash", str(SCRIPT), "--preflight"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "[PASS]" in result.stdout
    assert "Preflight complete" in result.stdout


def test_pipeline_verify_model():
    result = subprocess.run(
        ["bash", str(SCRIPT), "--verify-model"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "MODEL INTEGRITY" in result.stdout


def test_pipeline_missing_file():
    result = subprocess.run(
        ["bash", str(SCRIPT), "/nonexistent/file.mp4"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "FAIL" in result.stdout


def test_pipeline_no_args():
    result = subprocess.run(
        ["bash", str(SCRIPT)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "No input file" in result.stdout


def test_safe_ai_pipeline_checklist():
    cl = load_checklist("safe-ai-pipeline")
    assert cl.name == "safe-ai-pipeline"
    assert "pipeline" in cl.intent.lower() or "verified" in cl.intent.lower()
    assert len(cl.preflight) >= 4
    assert len(cl.run) >= 3
    assert len(cl.verify) >= 4
    assert len(cl.fallback) >= 3
