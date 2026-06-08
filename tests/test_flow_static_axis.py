"""Tests for flow_static_axis — flow/static node classification."""

from __future__ import annotations

import pytest

from apps.protocol.flow_static_axis import (
    CASES,
    LADDER,
    Node,
    Environment,
    capacity,
    classify,
    score_self_as_reading_model,
    validate,
)


# ── capacity bounds ──────────────────────────────────────────────

def test_capacity_always_in_unit_interval():
    for node, _ in CASES:
        for env in LADDER:
            c = capacity(node, env)
            assert 0.0 <= c <= 1.0, f"{node.label} @ {env.name}: {c}"


def test_capacity_zero_floor_not_negative():
    """A node with high audience_signal and no intrinsic terms must not go below 0."""
    worst = Node("worst", 0.0, 0.0, 0.0, 0.0, set(), audience_signal=1.0)
    for env in LADDER:
        assert capacity(worst, env) == 0.0


def test_capacity_ceiling_at_one():
    best = Node("best", 1.0, 1.0, 1.0, 1.0, set(), audience_signal=0.0)
    fit_env = LADDER[0]
    assert capacity(best, fit_env) == 1.0


# ── fixture mechanics ────────────────────────────────────────────

def test_fixtures_absent_add_nothing():
    """Fixtures that don't exist in the environment contribute 0 support."""
    node = Node("dep_node", 0.0, 0.0, 0.0, 0.0, {"bait", "stand"}, audience_signal=0.0)
    stripped = LADDER[2]  # available_fixtures = set()
    assert capacity(node, stripped) == 0.0


def test_fixtures_present_add_support():
    node = Node("dep_node", 0.0, 0.0, 0.0, 0.0, {"bait", "stand"}, audience_signal=0.0)
    fit = LADDER[0]       # available_fixtures includes bait and stand
    assert capacity(node, fit) > 0.0


# ── classify structure ───────────────────────────────────────────

def test_classify_returns_expected_keys():
    node, _ = CASES[0]
    result = classify(node)
    for key in ("trace", "survives_stripped", "cliff", "flow_fraction", "kind"):
        assert key in result


def test_classify_trace_has_three_entries():
    node, _ = CASES[0]
    result = classify(node)
    assert len(result["trace"]) == 3
    names = [t[0] for t in result["trace"]]
    assert names == ["fit", "shifted", "stripped"]


def test_classify_kind_is_flow_or_static():
    for node, _ in CASES:
        assert classify(node)["kind"] in ("flow", "static")


def test_classify_flow_fraction_range():
    for node, _ in CASES:
        ff = classify(node)["flow_fraction"]
        assert 0.0 <= ff <= 1.0


# ── flow vs static correctness ───────────────────────────────────

def test_all_cases_match_expected():
    results = validate()
    mismatches = [r for r in results if not r["match"]]
    assert not mismatches, (
        "Field-observation mismatches (examine, do not retune):\n"
        + "\n".join(f"  {r['label']}: expected={r['expected']} got={r['got']}" for r in mismatches)
    )


def test_flow_nodes_survive_stripped():
    """Flow nodes must hold >= 0.5 capacity when all fixtures are gone."""
    flow_cases = [(n, e) for n, e in CASES if e == "flow"]
    for node, _ in flow_cases:
        survives = classify(node)["survives_stripped"]
        assert survives >= 0.5, f"{node.label} flow node dropped to {survives} when stripped"


def test_static_nodes_cliff_or_low_stripped():
    """Static nodes must either cliff (drop > 0.35) or survive < 0.5 stripped."""
    static_cases = [(n, e) for n, e in CASES if e == "static"]
    for node, _ in static_cases:
        r = classify(node)
        is_low = r["survives_stripped"] < 0.5
        is_cliff = r["cliff"] > 0.35
        assert is_low or is_cliff, (
            f"{node.label} classified static but survives_stripped={r['survives_stripped']} "
            f"and cliff={r['cliff']}"
        )


# ── self-score ───────────────────────────────────────────────────

def test_score_self_returns_dict_with_instruction():
    result = score_self_as_reading_model()
    assert isinstance(result, dict)
    assert "kind" in result
    assert "instruction" in result
    assert result["kind"] == "static"


def test_score_self_flow_fraction_in_range():
    result = score_self_as_reading_model()
    assert 0.0 <= result["flow_fraction"] <= 1.0


# ── validate output shape ────────────────────────────────────────

def test_validate_returns_one_entry_per_case():
    results = validate()
    assert len(results) == len(CASES)


def test_validate_entries_have_match_field():
    for row in validate():
        assert "match" in row
        assert isinstance(row["match"], bool)
