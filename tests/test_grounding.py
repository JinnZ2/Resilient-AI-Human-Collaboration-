"""Tests for the L0-L5 substrate grounding checks and `protocol ground` CLI."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from apps.protocol.cli import app
from apps.protocol.grounding import GroundingChecker, get_layer, list_layers

runner = CliRunner()


# ── layer registry ──────────────────────────────────────────────


def test_list_layers_covers_all_seven():
    codes = {layer.code for layer in list_layers()}
    assert codes == {"L0", "L1", "L2", "L3", "L4", "Le", "L5"}


def test_get_layer_known():
    layer = get_layer("L1")
    assert layer.name == "Thermodynamics"


def test_get_layer_case_insensitive():
    assert get_layer("l4").name == "Human"


def test_get_layer_unknown_raises():
    try:
        get_layer("L99")
        assert False, "expected KeyError"
    except KeyError as exc:
        assert "Available" in str(exc)


# ── GroundingChecker ─────────────────────────────────────────────


def test_clean_text_is_grounded():
    report = GroundingChecker().check(
        "Wild rice needs flowing water and a pH near neutral to establish well."
    )
    assert report.grounded is True
    assert report.triggered_layers == []


def test_detects_l0_physics_violation():
    report = GroundingChecker().check("This drive achieves faster than light travel.")
    assert report.grounded is False
    codes = [r.code for r in report.triggered_layers]
    assert "L0" in codes


def test_detects_l1_thermodynamics_violation():
    report = GroundingChecker().check("The generator produces free energy indefinitely.")
    codes = [r.code for r in report.triggered_layers]
    assert "L1" in codes


def test_detects_l4_human_violation():
    report = GroundingChecker().check("The operator has superhuman strength and never needs to sleep.")
    codes = [r.code for r in report.triggered_layers]
    assert "L4" in codes


def test_detects_epistemic_violation():
    report = GroundingChecker().check("This sensor reading is 100% accurate with no margin of error.")
    codes = [r.code for r in report.triggered_layers]
    assert "Le" in codes


def test_detects_multiple_layers():
    report = GroundingChecker().check(
        "Faster than light travel with 100% efficient perpetual motion."
    )
    codes = {r.code for r in report.triggered_layers}
    assert "L0" in codes
    assert "L1" in codes


# ── CLI ──────────────────────────────────────────────────────────


def test_ground_layers_cli():
    result = runner.invoke(app, ["ground", "layers"])
    assert result.exit_code == 0
    assert "L0" in result.output
    assert "L5" in result.output


def test_ground_check_cli_stdin_clean():
    result = runner.invoke(app, ["ground", "check", "-"], input="The river flows downhill.")
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["grounded"] is True


def test_ground_check_cli_stdin_violation():
    result = runner.invoke(
        app, ["ground", "check", "-"], input="We achieved unlimited energy from over-unity devices."
    )
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["grounded"] is False


def test_ground_check_cli_text_format():
    result = runner.invoke(
        app, ["ground", "check", "-", "--fmt", "text"], input="Faster than light travel is safe."
    )
    assert result.exit_code == 0
    assert "L0" in result.output


def test_ground_check_missing_file():
    result = runner.invoke(app, ["ground", "check", "/nonexistent/file.txt"])
    assert result.exit_code != 0
