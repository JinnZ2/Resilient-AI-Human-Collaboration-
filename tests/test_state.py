"""Tests for state load/save operations."""

import json
from pathlib import Path

from apps.protocol.models import SessionState
from apps.protocol.state import load_state, save_state, require_state

import pytest


@pytest.fixture()
def state_file(tmp_path):
    """Return a path for a temporary state file."""
    return str(tmp_path / ".protocol-state.json")


def test_load_state_missing(state_file):
    assert load_state(state_file) is None


def test_save_and_load_roundtrip(state_file):
    state = SessionState(sid="SESSION-0001", ctx="test context")
    save_state(state, state_file)

    loaded = load_state(state_file)
    assert loaded is not None
    assert loaded.sid == "SESSION-0001"
    assert loaded.ctx == "test context"
    assert loaded.seq == 1  # save_state increments seq


def test_save_increments_seq(state_file):
    state = SessionState(sid="SESSION-0002")
    assert state.seq == 0

    save_state(state, state_file)
    assert state.seq == 1

    save_state(state, state_file)
    assert state.seq == 2


def test_save_creates_valid_json(state_file):
    state = SessionState(sid="SESSION-0003", risks=["power", "heat"])
    save_state(state, state_file)

    raw = Path(state_file).read_text(encoding="utf-8")
    data = json.loads(raw)
    assert data["sid"] == "SESSION-0003"
    assert data["risks"] == ["power", "heat"]


def test_require_state_exits_when_missing(state_file):
    with pytest.raises(SystemExit):
        require_state(state_file)


def test_require_state_returns_state(state_file):
    state = SessionState(sid="SESSION-0004")
    save_state(state, state_file)

    result = require_state(state_file)
    assert result.sid == "SESSION-0004"
