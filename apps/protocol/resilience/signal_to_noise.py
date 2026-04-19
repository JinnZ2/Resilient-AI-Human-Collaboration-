"""
signal_to_noise.py

Layer 4 of mutual_audit.py: cognitive SNR measurement.

Problem: response length can drift without information density keeping pace.
High word count + low claim/constraint density = heat leak.
The response is generating entropy without doing work.

Measures:
    - word_count
    - load_bearing_units (claims, constraints, assumptions, specifications)
    - SNR = load_bearing_units per 100 words
    - heat_leak = 1 - normalized_SNR

Three density classes:
    DENSE       : SNR >= 3.0   (high information per word)
    ADEQUATE    : SNR 1.5-3.0  (acceptable)
    HEAT_LEAK   : SNR < 1.5    (rambling; compress or cut)

Couples into mutual_audit.py as Layer 4 or runs standalone.

Vendored from JinnZ2/Resilience-indigenous-worldwide (resilience_stack/).
Upstream license: CC0 1.0 | stdlib only | JinnZ2
"""

from dataclasses import dataclass
from typing import Optional
import re


# ============================================================
# LOAD-BEARING UNIT DETECTORS
# ============================================================

class LoadBearingDetector:
    """
    Detects units that do cognitive work in a response:
        - falsifiable claims
        - explicit constraints (with parameters)
        - stated assumptions
        - specifications (numeric/bounded)
        - tests/predictions
        - explicit corrections or disagreements
    """

    CLAIM_MARKERS = [
        r"\bif\s+\w+.*,\s*then\b",
        r"\bunder\s+(these\s+)?conditions?\b",
        r"\bprobability\s+(of|that)\b",
        r"\bpredict(s|ion)?\s+that\b",
        r"\bclaim(s)?\s+that\b",
    ]

    CONSTRAINT_MARKERS = [
        r"\bbounded\s+by\b",
        r"\bwithin\s+\[?\d",
        r"\bmax(imum)?\s+\d",
        r"\bmin(imum)?\s+\d",
        r"\blimit(ed)?\s+to\b",
        r"\bdegrees?\s+of\s+freedom\b",
        r"\bconstraint\s+(space|geometry|field)\b",
    ]

    ASSUMPTION_MARKERS = [
        r"\bassume(s|d)?\s+that\b",
        r"\bpresuppose(s|d)?\b",
        r"\bgiven\s+that\b",
        r"\bpremise\s+is\b",
    ]

    SPECIFICATION_MARKERS = [
        r"\b\d+\s*(kg|g|lb|oz|m|cm|mm|km|mi|ft|in)\b",
        r"\b\d+(\.\d+)?\s*%\b",
        r"\b\d+(\.\d+)?\s*(hr|hour|min|sec|day|week|year|month)s?\b",
        r"\bzone\s+\d",
        r"\bp\s*=\s*\d",
        r"\balpha\s*=\s*\d",
    ]

    TEST_MARKERS = [
        r"\bfalsif(iable|y|ied)\b",
        r"\bdisprove(d|s)?\b",
        r"\btest(s|ed|ing|able)?\s+(against|with|by)\b",
        r"\bmeasurable\s+proxy\b",
        r"\bevidence\s+(for|against)\b",
    ]

    FRICTION_MARKERS = [
        r"\bactually\b",
        r"\bdisagree\b",
        r"\bcounterexample\b",
        r"\bpush\s+back\b",
        r"\bthat\s+(doesn't|does\s+not)\s+hold\b",
        r"\bbreaks?\s+when\b",
        r"\bi\s+(need\s+to\s+)?flag\b",
    ]

    def count_units(self, text: str) -> dict[str, int]:
        text_lower = text.lower()
        return {
            "claims": self._count_patterns(text_lower, self.CLAIM_MARKERS),
            "constraints": self._count_patterns(text_lower, self.CONSTRAINT_MARKERS),
            "assumptions": self._count_patterns(text_lower, self.ASSUMPTION_MARKERS),
            "specifications": self._count_patterns(text_lower, self.SPECIFICATION_MARKERS),
            "tests": self._count_patterns(text_lower, self.TEST_MARKERS),
            "friction": self._count_patterns(text_lower, self.FRICTION_MARKERS),
        }

    def _count_patterns(self, text: str, patterns: list[str]) -> int:
        total = 0
        for p in patterns:
            total += len(re.findall(p, text))
        return total


# ============================================================
# SNR ANALYZER
# ============================================================

@dataclass
class SNRResult:
    word_count: int
    load_bearing_units: int
    unit_breakdown: dict[str, int]
    snr: float                           # units per 100 words
    density_class: str                   # DENSE | ADEQUATE | HEAT_LEAK
    heat_leak_ratio: float               # 0-1, higher is worse
    compression_suggestion: str
    worst_gap: Optional[str]             # which unit type is missing


class SNRAnalyzer:
    """
    Measures cognitive signal-to-noise.
    Low SNR = heat leak = response should be compressed.
    """

    DENSE_THRESHOLD = 3.0       # units per 100 words
    ADEQUATE_THRESHOLD = 1.5

    def __init__(self):
        self.detector = LoadBearingDetector()

    def analyze(self, text: str) -> SNRResult:
        # Strip fenced code blocks before word count -- code is different density class
        text_prose = re.sub(r"```[\s\S]*?```", "", text)
        words = re.findall(r"\b\w+\b", text_prose)
        word_count = len(words)

        units = self.detector.count_units(text_prose)
        total_units = sum(units.values())

        if word_count == 0:
            snr = 0.0
        else:
            snr = (total_units / word_count) * 100

        if snr >= self.DENSE_THRESHOLD:
            density_class = "DENSE"
            suggestion = "Response carries its weight. No compression needed."
        elif snr >= self.ADEQUATE_THRESHOLD:
            density_class = "ADEQUATE"
            suggestion = (
                "Acceptable density. Could tighten -- identify paragraphs that "
                "don't contain claims/constraints/specs and cut."
            )
        else:
            density_class = "HEAT_LEAK"
            suggestion = (
                "Low information density. Cut prose that doesn't advance a "
                "claim, state a constraint, register an assumption, or test "
                "something. Aim for at least one load-bearing unit per 30 words."
            )

        if snr >= self.DENSE_THRESHOLD:
            heat_leak = 0.0
        else:
            heat_leak = max(0.0, 1.0 - (snr / self.DENSE_THRESHOLD))

        worst_gap = None
        if total_units > 0:
            missing = [k for k, v in units.items() if v == 0]
            if missing:
                worst_gap = f"no {', '.join(missing)} present"

        return SNRResult(
            word_count=word_count,
            load_bearing_units=total_units,
            unit_breakdown=units,
            snr=round(snr, 2),
            density_class=density_class,
            heat_leak_ratio=round(heat_leak, 2),
            compression_suggestion=suggestion,
            worst_gap=worst_gap,
        )


# ============================================================
# INTEGRATION WITH MUTUAL AUDIT
# ============================================================

@dataclass
class SNRAuditEntry:
    """Per-exchange SNR record for longitudinal tracking."""
    speaker: str
    word_count: int
    snr: float
    density_class: str
    heat_leak_ratio: float


class SNRAudit:
    """
    Wraps SNRAnalyzer for bidirectional exchange audit.
    Matches mutual_audit.py API pattern.
    """

    def __init__(self):
        self.analyzer = SNRAnalyzer()
        self.entries: list[SNRAuditEntry] = []

    def audit_response(self, text: str, speaker: str) -> SNRResult:
        result = self.analyzer.analyze(text)
        self.entries.append(SNRAuditEntry(
            speaker=speaker,
            word_count=result.word_count,
            snr=result.snr,
            density_class=result.density_class,
            heat_leak_ratio=result.heat_leak_ratio,
        ))
        return result

    def session_summary(self) -> dict:
        if not self.entries:
            return {"status": "no entries"}

        by_speaker: dict[str, dict] = {}
        for e in self.entries:
            if e.speaker not in by_speaker:
                by_speaker[e.speaker] = {
                    "total_words": 0,
                    "total_snr": 0.0,
                    "exchanges": 0,
                    "heat_leak_count": 0,
                }
            by_speaker[e.speaker]["total_words"] += e.word_count
            by_speaker[e.speaker]["total_snr"] += e.snr
            by_speaker[e.speaker]["exchanges"] += 1
            if e.density_class == "HEAT_LEAK":
                by_speaker[e.speaker]["heat_leak_count"] += 1

        for sp, stats in by_speaker.items():
            stats["avg_snr"] = round(stats["total_snr"] / stats["exchanges"], 2)
            stats["heat_leak_ratio"] = round(
                stats["heat_leak_count"] / stats["exchanges"], 2
            )

        return {
            "total_exchanges": len(self.entries),
            "by_speaker": by_speaker,
            "worst_speaker": max(
                by_speaker.keys(),
                key=lambda k: by_speaker[k]["heat_leak_ratio"],
            ),
        }
