"""Tests for protocol data models."""

from datetime import datetime, timezone

from apps.protocol.models import (
    ChecklistDef,
    ChecklistRun,
    ChecklistStep,
    Constraints,
    DecisionPoint,
    SessionState,
)


def test_decision_point_defaults():
    dp = DecisionPoint(id="ID-001", description="Test decision")
    assert dp.status == "active"
    assert dp.tier == "flexible"
    assert dp.paused_at is None
    assert dp.resumed_at is None
    assert dp.last_completed_step is None
    assert isinstance(dp.created_at, datetime)


def test_decision_point_all_fields():
    now = datetime.now(timezone.utc)
    dp = DecisionPoint(
        id="ID-042",
        description="Power bypass",
        status="paused",
        tier="critical",
        created_at=now,
        paused_at=now,
        last_completed_step=3,
    )
    assert dp.id == "ID-042"
    assert dp.status == "paused"
    assert dp.tier == "critical"
    assert dp.last_completed_step == 3


def test_constraints_defaults():
    c = Constraints()
    assert c.net == "stable"
    assert c.time == "normal"
    assert c.tools == []
    assert c.extras == {}


def test_constraints_custom():
    c = Constraints(net="offline", time="low", tools=["aria2c"], extras={"gpu": "none"})
    assert c.net == "offline"
    assert c.tools == ["aria2c"]
    assert c.extras["gpu"] == "none"


def test_session_state_defaults():
    state = SessionState(sid="SESSION-abcd")
    assert state.sid == "SESSION-abcd"
    assert state.seq == 0
    assert state.ctx == ""
    assert state.decision_points == {}
    assert state.active_id is None
    assert state.confidence == 0.5
    assert state.tag == "provisional"
    assert state.roles == {"A": "operator", "B": "helper", "AI": "planner"}
    assert state.risks == []
    assert state.checklist_runs == []


def test_session_state_with_decision_points():
    dp = DecisionPoint(id="ID-001", description="Test")
    state = SessionState(
        sid="SESSION-1234",
        decision_points={"ID-001": dp},
        active_id="ID-001",
    )
    assert "ID-001" in state.decision_points
    assert state.active_id == "ID-001"


def test_checklist_step_defaults():
    step = ChecklistStep(text="Check power")
    assert step.required is True


def test_checklist_step_optional():
    step = ChecklistStep(text="SHA256 check", required=False)
    assert step.required is False


def test_checklist_def_minimal():
    cl = ChecklistDef(name="test", intent="Test checklist")
    assert cl.preflight == []
    assert cl.run == []
    assert cl.verify == []
    assert cl.fallback == []


def test_checklist_run_defaults():
    run = ChecklistRun(checklist_name="bad-internet")
    assert run.status == "passed"
    assert run.completed_at is None
    assert run.phase_results == {}


def test_session_state_roundtrip():
    """Model can serialize and deserialize without data loss."""
    state = SessionState(
        sid="SESSION-beef",
        ctx="Build swarm",
        confidence=0.72,
        tag="confirmed",
        risks=["power-loss", "slow-net"],
    )
    data = state.model_dump()
    restored = SessionState.model_validate(data)
    assert restored.sid == state.sid
    assert restored.confidence == state.confidence
    assert restored.risks == state.risks
