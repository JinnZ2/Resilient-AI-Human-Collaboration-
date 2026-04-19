"""Resilience audit package.

Layout
------
``vendor/``
    Byte-identical upstream modules from
    `JinnZ2/Resilience-indigenous-worldwide <https://github.com/JinnZ2/Resilience-indigenous-worldwide>`_
    (``resilience_stack/``, CC0 1.0). Sync by overwriting files in place.

``audit_log.py``
    Project-specific glue: appends ``AuditLedgerEntry`` dicts to
    ``.protocol-audit.log.json`` and summarises cumulative drift for
    ``protocol status`` / ``protocol export``.
"""

from .audit_log import (
    DEFAULT_LOG_PATH,
    append_audit_entry,
    audit_summary,
    load_audit_log,
)
from .vendor.mutual_audit import (
    AgreeablenessDetector,
    AgreeablenessFlag,
    Assumption,
    AssumptionLedger,
    AuditLedgerEntry,
    Claim,
    FalsifiabilityScore,
    FalsifiabilityScorer,
    MutualAudit,
    Speaker,
)
from .vendor.signal_to_noise import (
    LoadBearingDetector,
    SNRAnalyzer,
    SNRAudit,
    SNRAuditEntry,
    SNRResult,
)

__all__ = [
    "AgreeablenessDetector",
    "AgreeablenessFlag",
    "Assumption",
    "AssumptionLedger",
    "AuditLedgerEntry",
    "Claim",
    "DEFAULT_LOG_PATH",
    "FalsifiabilityScore",
    "FalsifiabilityScorer",
    "LoadBearingDetector",
    "MutualAudit",
    "SNRAnalyzer",
    "SNRAudit",
    "SNRAuditEntry",
    "SNRResult",
    "Speaker",
    "append_audit_entry",
    "audit_summary",
    "load_audit_log",
]
