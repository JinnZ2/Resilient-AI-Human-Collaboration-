"""Protocol CLI — turn collaboration protocols into actionable tools."""

from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone

import typer

from .audit_cli import audit_app
from .capsule import generate_capsule, generate_glyph_strip
from .resilience import audit_summary
from .checklist import list_checklists, load_checklist, run_checklist_interactive
from .models import Constraints, DecisionPoint, SessionState
from .state import require_state, save_state, load_state

app = typer.Typer(help="Resilient AI-Human collaboration protocol tools.")
id_app = typer.Typer(help="Manage decision point IDs.")
cl_app = typer.Typer(help="Run and manage checklists.")
app.add_typer(id_app, name="id")
app.add_typer(cl_app, name="checklist")
app.add_typer(audit_app, name="audit")


# ── session commands ─────────────────────────────────────────────

@app.command()
def init(
    ctx: str = typer.Option("", help="One-line session context / goal."),
) -> None:
    """Start a new protocol session."""
    if load_state() is not None:
        overwrite = typer.confirm(".protocol-state.json already exists. Overwrite?")
        if not overwrite:
            raise typer.Exit()

    sid = f"SESSION-{secrets.token_hex(2)}"
    state = SessionState(sid=sid, ctx=ctx)
    save_state(state)
    print(f"Session {sid} created.")
    print(f"State file: .protocol-state.json")
    if ctx:
        print(f"Context: {ctx}")


@app.command()
def status() -> None:
    """Show current session state."""
    state = require_state()
    print(generate_glyph_strip(state))
    print()
    print(f"  Session:    {state.sid}  (seq {state.seq})")
    print(f"  Context:    {state.ctx or '(none)'}")
    print(f"  Active ID:  {state.active_id or 'none'}")
    print(f"  Confidence: {state.confidence:.2f} ({state.tag})")
    print(f"  Constraints: net={state.constraints.net}, time={state.constraints.time}")
    if state.constraints.tools:
        print(f"  Tools:      {', '.join(state.constraints.tools)}")
    if state.risks:
        print(f"  Risks:      {', '.join(state.risks)}")

    active = [dp for dp in state.decision_points.values() if dp.status == "active"]
    paused = [dp for dp in state.decision_points.values() if dp.status == "paused"]
    if active:
        print(f"\n  Active IDs:")
        for dp in active:
            print(f"    {dp.id}: {dp.description} [{dp.tier}]")
    if paused:
        print(f"  Paused IDs:")
        for dp in paused:
            print(f"    {dp.id}: {dp.description}")

    summary = audit_summary()
    if summary:
        print(f"\n  Audit:      {summary['entries']} entries, "
              f"drift {summary['total_drift_score']} ({summary['risk']})")
        print(f"              last: {summary['last_pattern']}")


@app.command()
def sync() -> None:
    """Dump the full state capsule and update sync timestamp."""
    state = require_state()
    state.last_sync_at = datetime.now(timezone.utc)
    capsule = generate_capsule(state)
    print(generate_glyph_strip(state))
    print()
    print(json.dumps(capsule, indent=2, default=str))
    save_state(state)


@app.command()
def constraint(key: str, value: str) -> None:
    """Set a constraint (e.g., `protocol constraint net offline`)."""
    state = require_state()
    if key in ("net", "time"):
        setattr(state.constraints, key, value)
    elif key == "tools":
        state.constraints.tools = [t.strip() for t in value.split(",")]
    else:
        state.constraints.extras[key] = value
    save_state(state)
    print(f"Constraint {key} = {value}")


# ── decision point commands ──────────────────────────────────────

def _next_id(state: SessionState) -> str:
    nums = []
    for key in state.decision_points:
        try:
            nums.append(int(key.split("-")[1]))
        except (IndexError, ValueError):
            pass
    n = max(nums, default=0) + 1
    return f"ID-{n:03d}"


@id_app.command("new")
def id_new(
    description: str,
    tier: str = typer.Option("flexible", help="critical, adaptable, or flexible"),
) -> None:
    """Create a new decision point and make it active."""
    state = require_state()
    dp_id = _next_id(state)
    dp = DecisionPoint(id=dp_id, description=description, tier=tier)
    state.decision_points[dp_id] = dp
    state.active_id = dp_id
    save_state(state)
    print(f"[{dp_id}: {description}] ({tier})")


@id_app.command("list")
def id_list() -> None:
    """List all decision points."""
    state = require_state()
    if not state.decision_points:
        print("No decision points yet.")
        return
    for dp in state.decision_points.values():
        marker = {"active": ">", "paused": "||", "completed": "+"}[dp.status]
        print(f"  [{marker}] {dp.id}: {dp.description} [{dp.tier}] ({dp.status})")


@id_app.command("pause")
def id_pause(dp_id: str) -> None:
    """Pause a decision point (context switch away)."""
    state = require_state()
    dp = state.decision_points.get(dp_id.upper())
    if dp is None:
        print(f"Unknown ID: {dp_id}")
        raise typer.Exit(1)
    dp.status = "paused"
    dp.paused_at = datetime.now(timezone.utc)
    if state.active_id == dp.id:
        state.active_id = None
    save_state(state)
    print(f"[{dp.id} PAUSED]")


@id_app.command("resume")
def id_resume(dp_id: str) -> None:
    """Resume a paused decision point."""
    state = require_state()
    dp = state.decision_points.get(dp_id.upper())
    if dp is None:
        print(f"Unknown ID: {dp_id}")
        raise typer.Exit(1)
    dp.status = "active"
    dp.resumed_at = datetime.now(timezone.utc)
    state.active_id = dp.id
    save_state(state)
    step = dp.last_completed_step or 0
    print(f"[{dp.id} RESUMED: last completed step {step}]")


@id_app.command("complete")
def id_complete(dp_id: str) -> None:
    """Mark a decision point as completed."""
    state = require_state()
    dp = state.decision_points.get(dp_id.upper())
    if dp is None:
        print(f"Unknown ID: {dp_id}")
        raise typer.Exit(1)
    dp.status = "completed"
    if state.active_id == dp.id:
        state.active_id = None
    save_state(state)
    print(f"[{dp.id} COMPLETED]")


@id_app.command("step")
def id_step(dp_id: str, step_num: int) -> None:
    """Record the last completed step for a decision point."""
    state = require_state()
    dp = state.decision_points.get(dp_id.upper())
    if dp is None:
        print(f"Unknown ID: {dp_id}")
        raise typer.Exit(1)
    dp.last_completed_step = step_num
    save_state(state)
    print(f"[{dp.id}: step {step_num} completed]")


# ── risk & confidence commands ───────────────────────────────────

@app.command()
def risk(
    action: str = typer.Argument(..., help="add, remove, or list"),
    value: str = typer.Argument("", help="Risk description (for add/remove)"),
) -> None:
    """Manage risks: add <text>, remove <text>, or list."""
    state = require_state()
    action = action.lower()
    if action == "add":
        if not value:
            print("Usage: protocol risk add <description>", file=__import__("sys").stderr)
            raise typer.Exit(1)
        state.risks.append(value)
        save_state(state)
        print(f"[+] Risk added: {value}")
    elif action == "remove":
        try:
            state.risks.remove(value)
            save_state(state)
            print(f"[-] Risk removed: {value}")
        except ValueError:
            print(f"Risk not found: {value}")
            raise typer.Exit(1)
    elif action == "list":
        if not state.risks:
            print("No risks recorded.")
        else:
            for r in state.risks:
                print(f"  - {r}")
    else:
        print(f"Unknown action: {action}. Use add, remove, or list.")
        raise typer.Exit(1)


@app.command()
def confidence(
    value: float = typer.Argument(..., help="Confidence value 0.0-1.0"),
    tag: str = typer.Option("", help="Set tag: provisional or confirmed"),
) -> None:
    """Set the session confidence level (0.0 to 1.0)."""
    state = require_state()
    if not 0.0 <= value <= 1.0:
        print("Confidence must be between 0.0 and 1.0.", file=__import__("sys").stderr)
        raise typer.Exit(1)
    state.confidence = value
    if tag:
        if tag not in ("provisional", "confirmed"):
            print("Tag must be 'provisional' or 'confirmed'.", file=__import__("sys").stderr)
            raise typer.Exit(1)
        state.tag = tag
    save_state(state)
    print(f"Confidence: {state.confidence:.2f} ({state.tag})")


@app.command()
def export(
    fmt: str = typer.Option("markdown", help="Export format: markdown or json"),
) -> None:
    """Export the current session state as a readable report."""
    state = require_state()
    if fmt == "json":
        print(state.model_dump_json(indent=2))
    elif fmt == "markdown":
        _export_markdown(state)
    else:
        print(f"Unknown format: {fmt}. Use markdown or json.")
        raise typer.Exit(1)


def _export_markdown(state: SessionState) -> None:
    """Print a markdown summary of the session."""
    lines = [
        f"# Session Report: {state.sid}",
        "",
        f"**Context:** {state.ctx or '(none)'}",
        f"**Confidence:** {state.confidence:.2f} ({state.tag})",
        f"**Sequence:** {state.seq}",
        f"**Created:** {state.created_at.isoformat()}",
        f"**Last Sync:** {state.last_sync_at.isoformat()}",
        "",
        "## Constraints",
        "",
        f"- **Network:** {state.constraints.net}",
        f"- **Time:** {state.constraints.time}",
    ]
    if state.constraints.tools:
        lines.append(f"- **Tools:** {', '.join(state.constraints.tools)}")
    for k, v in state.constraints.extras.items():
        lines.append(f"- **{k}:** {v}")

    if state.risks:
        lines += ["", "## Risks", ""]
        for r in state.risks:
            lines.append(f"- {r}")

    if state.decision_points:
        lines += ["", "## Decision Points", ""]
        for dp in state.decision_points.values():
            marker = {"active": "ACTIVE", "paused": "PAUSED", "completed": "DONE"}[dp.status]
            lines.append(f"- **{dp.id}** [{marker}] {dp.description} (tier: {dp.tier})")
            if dp.last_completed_step is not None:
                lines.append(f"  - Last completed step: {dp.last_completed_step}")

    if state.checklist_runs:
        lines += ["", "## Checklist Runs", ""]
        for run in state.checklist_runs:
            lines.append(f"- **{run.checklist_name}**: {run.status}")

    summary = audit_summary()
    if summary:
        lines += [
            "",
            "## Audit Ledger",
            "",
            f"- **Entries:** {summary['entries']}",
            f"- **Total exchanges:** {summary['total_exchanges']}",
            f"- **Cumulative drift score:** {summary['total_drift_score']} ({summary['risk']})",
            f"- **Last pattern:** {summary['last_pattern']}",
            f"- **Last hash:** `{summary['last_hash']}`",
        ]

    lines += ["", "---", f"*Exported at sequence {state.seq}*", ""]
    print("\n".join(lines))


# ── checklist commands ───────────────────────────────────────────

@cl_app.command("list")
def checklist_list() -> None:
    """List available checklists."""
    names = list_checklists()
    if not names:
        print("No checklists found in ./checklists/ or bundled.")
        return
    for name in names:
        print(f"  - {name}")


@cl_app.command("run")
def checklist_run(name: str) -> None:
    """Interactively run a checklist by name."""
    state = require_state()
    cl = load_checklist(name)
    result = run_checklist_interactive(cl)
    state.checklist_runs.append(result)
    save_state(state)


if __name__ == "__main__":
    app()
