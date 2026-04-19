"""Persistent audit ledger for the current protocol session.

Each `protocol audit exchange` invocation appends one
`AuditLedgerEntry` (as a dict) to `.protocol-audit.log.json`. The log
is read by `protocol status` and `protocol export` to surface
cumulative drift.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from .vendor.mutual_audit import AuditLedgerEntry

DEFAULT_LOG_PATH = ".protocol-audit.log.json"


def load_audit_log(path: str = DEFAULT_LOG_PATH) -> list[dict]:
    p = Path(path)
    if not p.is_file():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def append_audit_entry(
    entry: AuditLedgerEntry, path: str = DEFAULT_LOG_PATH
) -> None:
    log = load_audit_log(path)
    log.append(asdict(entry))
    Path(path).write_text(
        json.dumps(log, indent=2, default=str) + "\n", encoding="utf-8"
    )


def audit_summary(path: str = DEFAULT_LOG_PATH) -> Optional[dict]:
    log = load_audit_log(path)
    if not log:
        return None
    total_drift = sum(e.get("total_drift_score", 0) for e in log)
    total_exchanges = sum(e.get("exchange_count", 0) for e in log)
    risk = "low"
    if total_drift > 30:
        risk = "high"
    elif total_drift > 15:
        risk = "moderate"
    return {
        "entries": len(log),
        "total_exchanges": total_exchanges,
        "total_drift_score": total_drift,
        "risk": risk,
        "last_pattern": log[-1].get("drift_pattern", ""),
        "last_hash": log[-1].get("export_hash", ""),
        "last_timestamp": log[-1].get("timestamp", ""),
    }
