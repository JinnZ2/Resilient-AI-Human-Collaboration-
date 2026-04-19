"""Resilience audit modules.

Vendored from JinnZ2/Resilience-indigenous-worldwide (resilience_stack/).
Upstream license: CC0 1.0 Universal (public domain dedication).

Exposes two layers of the upstream stack that fit this project's
human-AI collaboration protocol:

- ``mutual_audit``: drift detector, assumption ledger, falsifiability scorer
- ``signal_to_noise``: cognitive SNR / heat-leak measurement
"""

from .mutual_audit import (
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
from .signal_to_noise import (
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
    "FalsifiabilityScore",
    "FalsifiabilityScorer",
    "LoadBearingDetector",
    "MutualAudit",
    "SNRAnalyzer",
    "SNRAudit",
    "SNRAuditEntry",
    "SNRResult",
    "Speaker",
]
