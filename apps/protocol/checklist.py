"""Load YAML checklists and run them interactively."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .models import ChecklistDef, ChecklistRun, ChecklistStep

# Search order: local ./checklists/, then bundled
_BUNDLED_DIR = Path(__file__).parent / "checklists"


def list_checklists() -> list[str]:
    """Return names of available checklists (no extension)."""
    found: dict[str, Path] = {}
    for d in [_BUNDLED_DIR, Path("checklists")]:
        if d.is_dir():
            for f in sorted(d.glob("*.yaml")):
                found[f.stem] = f
    return sorted(found)


def load_checklist(name: str) -> ChecklistDef:
    """Find and parse a YAML checklist by name."""
    for d in [Path("checklists"), _BUNDLED_DIR]:
        p = d / f"{name}.yaml"
        if p.exists():
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
            # Normalize step entries: plain strings become ChecklistStep
            for phase in ("preflight", "run", "verify"):
                raw = data.get(phase, [])
                steps = []
                for item in raw:
                    if isinstance(item, str):
                        steps.append({"text": item})
                    else:
                        steps.append(item)
                data[phase] = steps
            return ChecklistDef.model_validate(data)
    print(f"Checklist '{name}' not found.", file=sys.stderr)
    print(f"Searched: ./checklists/ and {_BUNDLED_DIR}", file=sys.stderr)
    raise SystemExit(1)


def run_checklist_interactive(cl: ChecklistDef) -> ChecklistRun:
    """Walk through a checklist interactively, return the run record."""
    run = ChecklistRun(checklist_name=cl.name)
    print(f"\n--- {cl.name} ---")
    print(f"Intent: {cl.intent}\n")

    aborted = False
    all_passed = True

    for phase_name, steps in [
        ("preflight", cl.preflight),
        ("run", cl.run),
        ("verify", cl.verify),
    ]:
        if not steps:
            continue
        print(f"  [{phase_name.upper()}]")
        results: list[bool] = []
        for i, step in enumerate(steps, 1):
            answer = _prompt_step(i, step)
            results.append(answer)
            if not answer and step.required:
                all_passed = False
                if phase_name == "preflight":
                    print("\n  Fallback instructions:")
                    for fb in cl.fallback:
                        print(f"    - {fb}")
                    if not _confirm("  Continue anyway?"):
                        aborted = True
                        run.phase_results[phase_name] = results
                        break
        run.phase_results[phase_name] = results
        if aborted:
            break
        print()

    run.completed_at = datetime.now(timezone.utc)
    if aborted:
        run.status = "aborted"
    elif all_passed:
        run.status = "passed"
    else:
        run.status = "failed"

    icon = {"passed": "+", "failed": "!", "aborted": "x"}[run.status]
    print(f"  [{icon}] Result: {run.status.upper()}\n")
    return run


def _prompt_step(num: int, step: ChecklistStep) -> bool:
    marker = "*" if step.required else " "
    return _confirm(f"    {num}. [{marker}] {step.text}")


def _confirm(msg: str) -> bool:
    try:
        resp = input(f"{msg} [Y/n] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return resp in ("", "y", "yes")
