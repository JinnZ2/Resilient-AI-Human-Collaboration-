"""Tests for the protocol CLI commands via typer testing."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from apps.protocol.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def _chdir_tmp(tmp_path, monkeypatch):
    """Run every test in a temporary directory so state files don't collide."""
    monkeypatch.chdir(tmp_path)


def test_init_creates_state():
    result = runner.invoke(app, ["init", "--ctx", "Build swarm"])
    assert result.exit_code == 0
    assert "SESSION-" in result.output
    assert Path(".protocol-state.json").exists()


def test_init_with_context():
    result = runner.invoke(app, ["init", "--ctx", "Test context"])
    assert result.exit_code == 0
    assert "Test context" in result.output


def test_status_requires_init():
    result = runner.invoke(app, ["status"])
    assert result.exit_code != 0


def test_status_after_init():
    runner.invoke(app, ["init", "--ctx", "Test"])
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "SESSION-" in result.output
    assert "Confidence" in result.output


def test_id_new():
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["id", "new", "Power bypass"])
    assert result.exit_code == 0
    assert "ID-001" in result.output
    assert "Power bypass" in result.output


def test_id_list():
    runner.invoke(app, ["init"])
    runner.invoke(app, ["id", "new", "First task"])
    runner.invoke(app, ["id", "new", "Second task"])
    result = runner.invoke(app, ["id", "list"])
    assert result.exit_code == 0
    assert "ID-001" in result.output
    assert "ID-002" in result.output


def test_id_pause_and_resume():
    runner.invoke(app, ["init"])
    runner.invoke(app, ["id", "new", "Task one"])

    result = runner.invoke(app, ["id", "pause", "ID-001"])
    assert result.exit_code == 0
    assert "PAUSED" in result.output

    result = runner.invoke(app, ["id", "resume", "ID-001"])
    assert result.exit_code == 0
    assert "RESUMED" in result.output


def test_id_complete():
    runner.invoke(app, ["init"])
    runner.invoke(app, ["id", "new", "Finish this"])
    result = runner.invoke(app, ["id", "complete", "ID-001"])
    assert result.exit_code == 0
    assert "COMPLETED" in result.output


def test_id_step():
    runner.invoke(app, ["init"])
    runner.invoke(app, ["id", "new", "Stepped task"])
    result = runner.invoke(app, ["id", "step", "ID-001", "3"])
    assert result.exit_code == 0
    assert "step 3" in result.output


def test_constraint():
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["constraint", "net", "offline"])
    assert result.exit_code == 0
    assert "net = offline" in result.output


def test_sync_outputs_capsule():
    runner.invoke(app, ["init", "--ctx", "Sync test"])
    result = runner.invoke(app, ["sync"])
    assert result.exit_code == 0
    assert "sid" in result.output
    assert "hash" in result.output


def test_checklist_list():
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["checklist", "list"])
    assert result.exit_code == 0
    assert "bad-internet" in result.output


def test_id_unknown_returns_error():
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["id", "pause", "ID-999"])
    assert result.exit_code != 0


# ── risk command tests ──────────────────────────────────────────


def test_risk_add():
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["risk", "add", "power-loss"])
    assert result.exit_code == 0
    assert "power-loss" in result.output


def test_risk_list():
    runner.invoke(app, ["init"])
    runner.invoke(app, ["risk", "add", "overheat"])
    runner.invoke(app, ["risk", "add", "slow-net"])
    result = runner.invoke(app, ["risk", "list"])
    assert result.exit_code == 0
    assert "overheat" in result.output
    assert "slow-net" in result.output


def test_risk_remove():
    runner.invoke(app, ["init"])
    runner.invoke(app, ["risk", "add", "fatigue"])
    result = runner.invoke(app, ["risk", "remove", "fatigue"])
    assert result.exit_code == 0
    assert "removed" in result.output.lower()


def test_risk_remove_unknown():
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["risk", "remove", "nonexistent"])
    assert result.exit_code != 0


def test_risk_list_empty():
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["risk", "list"])
    assert "No risks" in result.output


# ── confidence command tests ────────────────────────────────────


def test_confidence_set():
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["confidence", "0.85"])
    assert result.exit_code == 0
    assert "0.85" in result.output


def test_confidence_with_tag():
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["confidence", "0.90", "--tag", "confirmed"])
    assert result.exit_code == 0
    assert "confirmed" in result.output


def test_confidence_out_of_range():
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["confidence", "1.5"])
    assert result.exit_code != 0


# ── export command tests ────────────────────────────────────────


def test_export_markdown():
    runner.invoke(app, ["init", "--ctx", "Export test"])
    runner.invoke(app, ["id", "new", "Test decision"])
    result = runner.invoke(app, ["export"])
    assert result.exit_code == 0
    assert "# Session Report" in result.output
    assert "Export test" in result.output
    assert "ID-001" in result.output


def test_export_json():
    runner.invoke(app, ["init", "--ctx", "JSON test"])
    result = runner.invoke(app, ["export", "--fmt", "json"])
    assert result.exit_code == 0
    assert '"sid"' in result.output
