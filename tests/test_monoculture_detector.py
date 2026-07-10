"""Tests for the monoculture/variance-collapse diversity audit."""

from __future__ import annotations

from apps.protocol.resilience.monoculture_detector import (
    THRESHOLDS,
    MonocultureDetector,
)

NARROW_CORPUS = [
    "The model is great. The model is powerful. The model performs well. "
    "The model achieves state of the art. The model beats the baseline. "
    "The model shows strong results. The model is excellent."
] * 3

DIVERSE_CORPUS = [
    "The ecosystem evolved over millennia, with feedback loops "
    "between soil chemistry and plant metabolism driving emergent "
    "stability. Energy gradients dissipate through the biological "
    "network. This approximation fails at geological timescales.",
    "According to Ostrom, commons governance depends on boundary "
    "conditions. The market price signal breaks down when feedback "
    "is severed. Derived from multi-decade field studies.",
    "Millisecond-scale reactions in cellular metabolism are coupled "
    "to daily circadian rhythms, which in turn are nested within "
    "annual seasonal cycles. Each scale has distinct failure modes.",
]


def test_audit_returns_seven_axes():
    report = MonocultureDetector().audit(DIVERSE_CORPUS)
    assert len(report.axes) == 7
    assert {a.name for a in report.axes} == set(THRESHOLDS)


def test_narrow_corpus_flags_variance_collapse():
    report = MonocultureDetector().audit(NARROW_CORPUS)
    assert report.overall_status in ("YELLOW", "RED")
    assert any(a.status != "GREEN" for a in report.axes)


def test_diverse_corpus_scores_better_than_narrow():
    diverse = MonocultureDetector().audit(DIVERSE_CORPUS)
    narrow = MonocultureDetector().audit(NARROW_CORPUS)
    diverse_green_count = sum(1 for a in diverse.axes if a.status == "GREEN")
    narrow_green_count = sum(1 for a in narrow.axes if a.status == "GREEN")
    assert diverse_green_count > narrow_green_count


def test_empty_corpus_does_not_crash():
    report = MonocultureDetector().audit([""])
    assert report.n_documents == 1
    assert report.overall_status in ("GREEN", "YELLOW", "RED")


def test_to_json_round_trips():
    import json

    report = MonocultureDetector().audit(DIVERSE_CORPUS)
    payload = json.loads(report.to_json())
    assert payload["n_documents"] == 3
    assert len(payload["axes"]) == 7


def test_custom_thresholds_override_defaults():
    lenient = {name: {"green": 0.0, "yellow": 0.0} for name in THRESHOLDS}
    report = MonocultureDetector(thresholds=lenient).audit(NARROW_CORPUS)
    assert report.overall_status == "GREEN"
