"""`protocol ground` subcommand — L0-L5 + Lε substrate grounding checks."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import typer

from .grounding import GroundingChecker, list_layers

ground_app = typer.Typer(help="Check text against the L0-L5 substrate grounding layers.")


def _read_input(path: str) -> str:
    """Read text from a file path, or stdin if path is '-'."""
    if path == "-":
        return sys.stdin.read()
    p = Path(path)
    if not p.is_file():
        typer.echo(f"Not a file: {path}", err=True)
        raise typer.Exit(1)
    return p.read_text(encoding="utf-8")


@ground_app.command("check")
def ground_check(
    text_file: str = typer.Argument(..., help="Path to text (or '-' for stdin)."),
    fmt: str = typer.Option("json", help="Output format: json or text."),
) -> None:
    """Scan text for language that reads as a substrate-layer violation."""
    text = _read_input(text_file)
    report = GroundingChecker().check(text)

    if fmt == "json":
        typer.echo(json.dumps(asdict(report), indent=2))
        return
    if fmt != "text":
        typer.echo(f"Unknown format: {fmt}. Use json or text.", err=True)
        raise typer.Exit(1)

    typer.echo(f"Grounded: {report.grounded}")
    for result in report.layer_results:
        if not result.triggered:
            continue
        typer.echo(f"  [{result.code}] {result.name}: {', '.join(result.matches)}")
        typer.echo(f"    -> {result.repair_note}")


@ground_app.command("layers")
def ground_layers() -> None:
    """List the substrate layers and what each one checks for."""
    for layer in list_layers():
        typer.echo(f"[{layer.code}] {layer.name} — {layer.definition}")
