"""Protocol CLI — turn collaboration protocols into actionable tools."""

from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone

import typer

from .capsule import generate_capsule, generate_glyph_strip
from .checklist import list_checklists, load_checklist, run_checklist_interactive
from .models import Constraints, DecisionPoint, SessionState
from .state import require_state, save_state, load_state

app = typer.Typer(help="Resilient AI-Human collaboration protocol tools.")
id_app = typer.Typer(help="Manage decision point IDs.")
cl_app = typer.Typer(help="Run and manage checklists.")
app.add_typer(id_app, name="id")
app.add_typer(cl_app, name="checklist")


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
