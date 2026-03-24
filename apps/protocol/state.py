"""Load / save session state from .protocol-state.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from .models import SessionState

DEFAULT_PATH = ".protocol-state.json"


def load_state(path: str = DEFAULT_PATH) -> Optional[SessionState]:
    p = Path(path)
    if not p.exists():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    return SessionState.model_validate(data)


def save_state(state: SessionState, path: str = DEFAULT_PATH) -> None:
    state.seq += 1
    Path(path).write_text(
        state.model_dump_json(indent=2) + "\n", encoding="utf-8",
    )


def require_state(path: str = DEFAULT_PATH) -> SessionState:
    state = load_state(path)
    if state is None:
        print("No active session. Run `protocol init` first.", file=sys.stderr)
        raise SystemExit(1)
    return state
