"""Tests for the resilience audit modules and the `protocol audit` CLI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from apps.protocol.cli import app
from apps.protocol.resilience import (
    AgreeablenessDetector,
    Claim,
    FalsifiabilityScorer,
    MutualAudit,
    SNRAnalyzer,
    Speaker,
)

runner = CliRunner()


# ── SNR analyzer ────────────────────────────────────────────────

def test_snr_classifies_dense_text():
    text = (
        "Under these conditions, probability of establishment drops below 40% "
        "in standing-water pockets. Falsifiable test: compare establishment "
        "rate across 10 matched 1m plots over 2 growing seasons. Constraint: "
        "bounded by 30cm water depth for both species."
    )
    result = SNRAnalyzer().analyze(text)
    assert result.density_class in ("DENSE", "ADEQUATE")
    assert result.load_bearing_units > 0
    assert result.snr > 0


def test_snr_classifies_heat_leak_text():
    text = (
        "You know, that's a really interesting thing to think about. "
        "I've been considering this a lot, and honestly, there are so many "
        "angles to this. It's one of those topics where you could really go "
        "in a lot of different directions, and each one would have its own "
        "merits and considerations."
    )
    result = SNRAnalyzer().analyze(text)
    assert result.density_class == "HEAT_LEAK"
    assert result.heat_leak_ratio > 0


def test_snr_handles_empty_input():
    result = SNRAnalyzer().analyze("")
    assert result.word_count == 0
    assert result.snr == 0.0


def test_snr_strips_code_blocks():
    text = "Prose here. ```python\nlots of code tokens 1 2 3 4 5 6 7 8 9 10\n```"
    result = SNRAnalyzer().analyze(text)
    assert result.word_count == 2  # "Prose here"


# ── agreeableness detector ──────────────────────────────────────

def test_agreeableness_flags_ai_smoothing():
    detector = AgreeablenessDetector()
    flag = detector.scan("Absolutely! You've nailed it.", Speaker.AI)
    assert flag is not None
    assert flag.drift_score > 0
    assert any("smoothing" in m for m in flag.markers_hit)


def test_agreeableness_flags_human_validation_seeking():
    detector = AgreeablenessDetector()
    flag = detector.scan("Does that make sense? Am I on the right track?", Speaker.HUMAN)
    assert flag is not None
    assert flag.drift_score > 0


def test_agreeableness_friction_cancels_smoothing():
    detector = AgreeablenessDetector()
    text = (
        "Absolutely, you're right that -- actually, that doesn't hold. "
        "Counterexample: let me push back on that. I need to flag this breaks when tested."
    )
    flag = detector.scan(text, Speaker.AI)
    # friction markers should drag drift_score to zero
    if flag is not None:
        assert flag.drift_score == 0


def test_agreeableness_returns_none_on_clean_text():
    detector = AgreeablenessDetector()
    flag = detector.scan("The schema requires a 64-bit integer key.", Speaker.AI)
    assert flag is None


# ── falsifiability scorer ───────────────────────────────────────

def test_falsifiability_strong_claim_is_falsifiable():
    claim = Claim(
        statement="X correlates with Y under stress.",
        made_by=Speaker.HUMAN,
        has_measurable_proxy=True,
        proxy_description="Y measurable via metric Z",
        has_disconfirming_condition=True,
        disconfirming_condition="No correlation observed in stressed cohort",
        testable_now=True,
        evidence_for=["pilot study"],
    )
    score = FalsifiabilityScorer().score(claim)
    assert score.verdict == "FALSIFIABLE"
    assert score.score >= 8


def test_falsifiability_weak_claim_is_unfalsifiable():
    claim = Claim(
        statement="Everything is connected.",
        made_by=Speaker.AI,
        has_measurable_proxy=False,
    )
    score = FalsifiabilityScorer().score(claim)
    assert score.verdict == "UNFALSIFIABLE"
    assert len(score.gaps) > 0


# ── mutual audit ledger ─────────────────────────────────────────

def test_mutual_audit_ledger_entry_has_hash():
    audit = MutualAudit(session_id="test-session")
    audit.audit_exchange(
        "Does that sound right to you?",
        "Absolutely. You've nailed it.",
    )
    entry = audit.to_ledger_entry()
    assert entry.session_id == "test-session"
    assert entry.exchange_count == 1
    assert entry.total_drift_score > 0
    assert len(entry.export_hash) == 16


# ── CLI: audit snr ──────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _chdir_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def test_audit_snr_cli_json(tmp_path):
    text_file = tmp_path / "response.txt"
    text_file.write_text(
        "Under these conditions, probability of establishment drops below 40%. "
        "Falsifiable test: compare across 10 plots over 2 years."
    )
    result = runner.invoke(app, ["audit", "snr", str(text_file)])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["speaker"] == "ai"
    assert "density_class" in payload
    assert "snr" in payload


def test_audit_snr_cli_text_format(tmp_path):
    text_file = tmp_path / "r.txt"
    text_file.write_text("Short response.")
    result = runner.invoke(app, ["audit", "snr", str(text_file), "--fmt", "text"])
    assert result.exit_code == 0
    assert "density_class" in result.output


def test_audit_snr_cli_rejects_bad_speaker(tmp_path):
    text_file = tmp_path / "r.txt"
    text_file.write_text("Text")
    result = runner.invoke(app, ["audit", "snr", str(text_file), "--speaker", "bot"])
    assert result.exit_code != 0


def test_audit_snr_cli_missing_file():
    result = runner.invoke(app, ["audit", "snr", "does-not-exist.txt"])
    assert result.exit_code != 0


# ── CLI: audit exchange ─────────────────────────────────────────

def test_audit_exchange_cli_flags_drift(tmp_path):
    human = tmp_path / "human.txt"
    ai = tmp_path / "ai.txt"
    human.write_text("Does that make sense? Am I on the right track?")
    ai.write_text("Absolutely. You've nailed it. That's a great point.")

    result = runner.invoke(
        app,
        ["audit", "exchange", str(human), str(ai), "--session-id", "t1"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["ledger"]["session_id"] == "t1"
    assert payload["exchange"]["combined_drift_score"] > 0
    assert payload["snr"]["human"]["word_count"] > 0
    assert payload["snr"]["ai"]["word_count"] > 0


def test_audit_exchange_cli_clean_text_no_drift(tmp_path):
    human = tmp_path / "h.txt"
    ai = tmp_path / "a.txt"
    human.write_text("What is the schema constraint?")
    ai.write_text("Bounded by 32 bytes per row.")
    result = runner.invoke(app, ["audit", "exchange", str(human), str(ai)])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["exchange"]["combined_drift_score"] == 0


def test_audit_exchange_cli_rejects_both_stdin():
    result = runner.invoke(app, ["audit", "exchange", "-", "-"])
    assert result.exit_code != 0


# ── CLI: audit claim ────────────────────────────────────────────

def test_audit_claim_cli_strong():
    result = runner.invoke(
        app,
        [
            "audit", "claim", "X correlates with Y",
            "--proxy", "metric Z",
            "--disconfirm", "no correlation observed",
            "--testable",
            "--evidence-for", "pilot",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["verdict"] == "FALSIFIABLE"
    assert payload["score"] >= 8


def test_audit_claim_cli_weak():
    result = runner.invoke(app, ["audit", "claim", "Everything is connected"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["verdict"] == "UNFALSIFIABLE"


# ── session integration ─────────────────────────────────────────

def test_audit_exchange_uses_active_session_id(tmp_path):
    runner.invoke(app, ["init", "--ctx", "session test"])
    state_data = json.loads(Path(".protocol-state.json").read_text())
    sid = state_data["sid"]

    human = tmp_path / "h.txt"
    ai = tmp_path / "a.txt"
    human.write_text("Does that make sense?")
    ai.write_text("Absolutely. You've nailed it.")
    result = runner.invoke(app, ["audit", "exchange", str(human), str(ai)])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["ledger"]["session_id"] == sid
    assert payload["logged"] is True
    assert Path(".protocol-audit.log.json").is_file()


def test_audit_exchange_no_log_flag(tmp_path):
    runner.invoke(app, ["init"])
    human = tmp_path / "h.txt"
    ai = tmp_path / "a.txt"
    human.write_text("Hello.")
    ai.write_text("Hi.")
    result = runner.invoke(
        app, ["audit", "exchange", str(human), str(ai), "--no-log"]
    )
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["logged"] is False
    assert not Path(".protocol-audit.log.json").exists()


def test_audit_exchange_works_without_session(tmp_path):
    human = tmp_path / "h.txt"
    ai = tmp_path / "a.txt"
    human.write_text("Hello.")
    ai.write_text("Hi.")
    result = runner.invoke(app, ["audit", "exchange", str(human), str(ai)])
    assert result.exit_code == 0
    # Ledger entry still produced; log file still appended (stateless mode).
    payload = json.loads(result.output)
    assert "ledger" in payload


def test_status_surfaces_audit_summary(tmp_path):
    runner.invoke(app, ["init", "--ctx", "drift test"])
    human = tmp_path / "h.txt"
    ai = tmp_path / "a.txt"
    human.write_text("Does that make sense? Am I on the right track?")
    ai.write_text("Absolutely. You've nailed it. That's a great point.")
    runner.invoke(app, ["audit", "exchange", str(human), str(ai)])

    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "Audit:" in result.output
    assert "drift" in result.output


def test_export_markdown_includes_audit_section(tmp_path):
    runner.invoke(app, ["init", "--ctx", "export test"])
    human = tmp_path / "h.txt"
    ai = tmp_path / "a.txt"
    human.write_text("Does that make sense?")
    ai.write_text("Absolutely.")
    runner.invoke(app, ["audit", "exchange", str(human), str(ai)])

    result = runner.invoke(app, ["export"])
    assert result.exit_code == 0
    assert "## Audit Ledger" in result.output
    assert "Cumulative drift score" in result.output


def test_status_omits_audit_when_no_log():
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "Audit:" not in result.output


def test_audit_log_accumulates_entries(tmp_path):
    runner.invoke(app, ["init"])
    h = tmp_path / "h.txt"
    a = tmp_path / "a.txt"
    h.write_text("Does that make sense?")
    a.write_text("Absolutely.")
    runner.invoke(app, ["audit", "exchange", str(h), str(a)])
    runner.invoke(app, ["audit", "exchange", str(h), str(a)])

    log = json.loads(Path(".protocol-audit.log.json").read_text())
    assert len(log) == 2
    for entry in log:
        assert "export_hash" in entry
        assert "drift_pattern" in entry
