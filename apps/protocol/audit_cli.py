"""`protocol audit` subcommand — drift and signal-to-noise checks."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import typer

from .audit_log import append_audit_entry
from .resilience import MutualAudit, SNRAnalyzer, Speaker
from .state import load_state

audit_app = typer.Typer(help="Audit human-AI exchanges for drift and density.")


def _read_input(path: str) -> str:
    """Read text from a file path, or stdin if path is '-'."""
    if path == "-":
        return sys.stdin.read()
    p = Path(path)
    if not p.is_file():
        typer.echo(f"Not a file: {path}", err=True)
        raise typer.Exit(1)
    return p.read_text(encoding="utf-8")


def _emit(payload: dict, fmt: str) -> None:
    if fmt == "json":
        typer.echo(json.dumps(payload, indent=2, default=str))
    elif fmt == "text":
        _emit_text(payload)
    else:
        typer.echo(f"Unknown format: {fmt}. Use json or text.", err=True)
        raise typer.Exit(1)


def _emit_text(payload: dict) -> None:
    for key, value in payload.items():
        if isinstance(value, dict):
            typer.echo(f"{key}:")
            for k, v in value.items():
                typer.echo(f"  {k}: {v}")
        elif isinstance(value, list):
            typer.echo(f"{key}:")
            for item in value:
                typer.echo(f"  - {item}")
        else:
            typer.echo(f"{key}: {value}")


@audit_app.command("exchange")
def audit_exchange(
    human_file: str = typer.Argument(..., help="Path to human turn text (or '-' for stdin)."),
    ai_file: str = typer.Argument(..., help="Path to AI turn text (or '-' for stdin)."),
    session_id: str = typer.Option(
        "", help="Session id for the ledger entry. Defaults to active session."
    ),
    no_log: bool = typer.Option(
        False, "--no-log", help="Don't append to .protocol-audit.log.json."
    ),
    fmt: str = typer.Option("json", help="Output format: json or text."),
) -> None:
    """Scan one human/AI exchange for drift markers and SNR."""
    if human_file == "-" and ai_file == "-":
        typer.echo("Cannot read both inputs from stdin.", err=True)
        raise typer.Exit(1)

    human_text = _read_input(human_file)
    ai_text = _read_input(ai_file)

    if not session_id:
        state = load_state()
        if state is not None:
            session_id = state.sid

    audit = MutualAudit(session_id=session_id or None)
    exchange = audit.audit_exchange(human_text, ai_text)

    snr = SNRAnalyzer()
    human_snr = snr.analyze(human_text)
    ai_snr = snr.analyze(ai_text)

    ledger = audit.to_ledger_entry()

    logged = False
    if not no_log:
        append_audit_entry(ledger)
        logged = True

    payload = {
        "ledger": asdict(ledger),
        "exchange": {
            "combined_drift_score": exchange.combined_drift_score,
            "human_flag": exchange.human_flag,
            "ai_flag": exchange.ai_flag,
            "notes": exchange.notes,
        },
        "snr": {
            "human": asdict(human_snr),
            "ai": asdict(ai_snr),
        },
        "logged": logged,
    }
    _emit(payload, fmt)


@audit_app.command("snr")
def audit_snr(
    text_file: str = typer.Argument(..., help="Path to text (or '-' for stdin)."),
    speaker: str = typer.Option("ai", help="Speaker label for the result: ai or human."),
    fmt: str = typer.Option("json", help="Output format: json or text."),
) -> None:
    """Measure signal-to-noise / heat-leak density of a response."""
    if speaker not in ("ai", "human"):
        typer.echo("Speaker must be 'ai' or 'human'.", err=True)
        raise typer.Exit(1)

    text = _read_input(text_file)
    result = SNRAnalyzer().analyze(text)
    payload = {"speaker": speaker, **asdict(result)}
    _emit(payload, fmt)


@audit_app.command("claim")
def audit_claim(
    statement: str = typer.Argument(..., help="The claim to score."),
    speaker: str = typer.Option("ai", help="Who made the claim: ai or human."),
    proxy: str = typer.Option("", help="Measurable proxy description (if any)."),
    disconfirm: str = typer.Option("", help="Disconfirming condition (if any)."),
    testable: bool = typer.Option(False, help="A test can be run now."),
    evidence_for: str = typer.Option("", help="Comma-separated evidence for."),
    evidence_against: str = typer.Option("", help="Comma-separated evidence against."),
    fmt: str = typer.Option("json", help="Output format: json or text."),
) -> None:
    """Score a claim's falsifiability (0-10) and list gaps."""
    if speaker not in ("ai", "human"):
        typer.echo("Speaker must be 'ai' or 'human'.", err=True)
        raise typer.Exit(1)

    from .resilience import Claim, FalsifiabilityScorer

    claim = Claim(
        statement=statement,
        made_by=Speaker.AI if speaker == "ai" else Speaker.HUMAN,
        has_measurable_proxy=bool(proxy),
        proxy_description=proxy or None,
        has_disconfirming_condition=bool(disconfirm),
        disconfirming_condition=disconfirm or None,
        testable_now=testable,
        evidence_for=[s.strip() for s in evidence_for.split(",") if s.strip()],
        evidence_against=[s.strip() for s in evidence_against.split(",") if s.strip()],
    )
    score = FalsifiabilityScorer().score(claim)
    _emit(asdict(score), fmt)
