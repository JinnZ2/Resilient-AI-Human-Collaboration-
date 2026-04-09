"""Tests for capsule and glyph strip generation."""

from apps.protocol.capsule import generate_capsule, generate_glyph_strip
from apps.protocol.models import DecisionPoint, SessionState


def _make_state(**kwargs) -> SessionState:
    defaults = {"sid": "SESSION-test", "ctx": "Unit tests"}
    defaults.update(kwargs)
    return SessionState(**defaults)


def test_generate_capsule_basic():
    state = _make_state()
    capsule = generate_capsule(state)

    assert capsule["sid"] == "SESSION-test"
    assert capsule["ctx"] == "Unit tests"
    assert capsule["active_id"] is None
    assert "hash" in capsule
    assert capsule["hash"].startswith("sha256:")


def test_capsule_includes_constraints():
    state = _make_state()
    state.constraints.net = "offline"
    state.constraints.time = "low"
    state.constraints.tools = ["aria2c"]

    capsule = generate_capsule(state)
    assert capsule["constraints"]["net"] == "offline"
    assert capsule["constraints"]["time"] == "low"
    assert capsule["constraints"]["tools"] == ["aria2c"]


def test_capsule_with_active_decision():
    dp = DecisionPoint(id="ID-001", description="Test", last_completed_step=3)
    state = _make_state(
        decision_points={"ID-001": dp},
        active_id="ID-001",
    )
    capsule = generate_capsule(state)
    assert capsule["active_id"] == "ID-001"
    assert capsule["step"]["current"] == 3


def test_capsule_hash_changes_with_data():
    state1 = _make_state(ctx="Alpha")
    state2 = _make_state(ctx="Beta")
    h1 = generate_capsule(state1)["hash"]
    h2 = generate_capsule(state2)["hash"]
    assert h1 != h2


def test_capsule_extras_merged_into_constraints():
    state = _make_state()
    state.constraints.extras = {"gpu": "none", "ram": "8GB"}
    capsule = generate_capsule(state)
    assert capsule["constraints"]["gpu"] == "none"
    assert capsule["constraints"]["ram"] == "8GB"


def test_generate_glyph_strip_basic():
    state = _make_state()
    strip = generate_glyph_strip(state)
    assert "CTX: Unit tests" in strip
    assert "SIG:" in strip
    assert "SYNC:" in strip


def test_glyph_strip_with_active_id():
    dp = DecisionPoint(id="ID-007", description="Bond mission", last_completed_step=2)
    state = _make_state(
        decision_points={"ID-007": dp},
        active_id="ID-007",
    )
    strip = generate_glyph_strip(state)
    assert "ID: ID-007" in strip
    assert "STEP: 2/?" in strip


def test_glyph_strip_with_risks():
    state = _make_state(risks=["overheat", "power-loss"])
    strip = generate_glyph_strip(state)
    assert "overheat" in strip
    assert "power-loss" in strip
