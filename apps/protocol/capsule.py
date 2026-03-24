"""Generate state capsules and glyph strips from session state."""

from __future__ import annotations

import hashlib
import json
from base64 import b32encode

from .models import SessionState


def generate_capsule(state: SessionState) -> dict:
    """Build the JSON capsule described in continuity-protocol.md."""
    active_dp = state.decision_points.get(state.active_id or "")
    step_current = active_dp.last_completed_step if active_dp else None

    capsule = {
        "sid": state.sid,
        "seq": state.seq,
        "ctx": state.ctx,
        "active_id": state.active_id,
        "step": {"current": step_current, "total": None},
        "roles": state.roles,
        "constraints": {
            "net": state.constraints.net,
            "time": state.constraints.time,
            "tools": state.constraints.tools,
            **state.constraints.extras,
        },
        "risks": state.risks,
        "fallback": state.fallback,
        "sync": {
            "interval_min": state.sync_interval_min,
            "every_msgs": state.sync_every_msgs,
        },
        "state": {
            "confidence": state.confidence,
            "tag": state.tag,
            "recheck_days": state.recheck_days,
        },
        "provenance": {
            "ts": state.last_sync_at.isoformat(),
        },
    }

    # Compute signature
    raw = json.dumps(capsule, sort_keys=True, default=str)
    digest = hashlib.sha256(raw.encode()).digest()
    sig = b32encode(digest).decode()[:12]
    capsule["hash"] = f"sha256:{sig}"
    return capsule


def generate_glyph_strip(state: SessionState) -> str:
    """One-line glyph header per continuity-protocol.md."""
    active_dp = state.decision_points.get(state.active_id or "")
    step = f"{active_dp.last_completed_step or '?'}/?" if active_dp else "-/-"
    roles = ",".join(f"{k}={v}" for k, v in state.roles.items())
    cons = f"net={state.constraints.net}, time={state.constraints.time}"
    risks = ", ".join(state.risks) if state.risks else "none"
    fb = state.fallback or "none"

    # Compute short sig for the strip
    raw = json.dumps({"sid": state.sid, "seq": state.seq}, sort_keys=True)
    sig = b32encode(hashlib.sha256(raw.encode()).digest()).decode()[:8]

    return (
        f"\u25d0CTX: {state.ctx or '(none)'}  "
        f"\u25c6ID: {state.active_id or 'none'}  "
        f"\u2727STEP: {step}  "
        f"\u262fROLE: {roles}  "
        f"\u2726CONS: {cons}  "
        f"\u2b21RISK: {risks}  "
        f"\u25b2PLAN: {fb}  "
        f"\u27f3SYNC: {state.sync_interval_min}m/{state.sync_every_msgs}x  "
        f"\u2699STATE: C={state.confidence:.2f} T={state.tag} D={state.recheck_days}d  "
        f"\u2b22SIG: {sig}"
    )
