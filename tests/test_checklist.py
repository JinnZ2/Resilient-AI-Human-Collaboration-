"""Tests for checklist loading and listing."""

from pathlib import Path

import pytest

from apps.protocol.checklist import list_checklists, load_checklist


def test_list_checklists_finds_bundled():
    names = list_checklists()
    assert "bad-internet" in names
    assert "status-declaration" in names
    assert "video-transcript" in names


def test_load_checklist_bad_internet():
    cl = load_checklist("bad-internet")
    assert cl.name == "bad-internet"
    assert cl.intent
    assert len(cl.preflight) >= 2
    assert len(cl.run) >= 2
    assert len(cl.verify) >= 1
    assert len(cl.fallback) >= 1


def test_load_checklist_status_declaration():
    cl = load_checklist("status-declaration")
    assert cl.name == "status-declaration"
    assert len(cl.preflight) >= 2
    assert len(cl.run) >= 2


def test_load_checklist_video_transcript():
    cl = load_checklist("video-transcript")
    assert cl.name == "video-transcript"
    assert "dyslexia" in cl.intent.lower() or "study" in cl.intent.lower()


def test_load_checklist_not_found():
    with pytest.raises(SystemExit):
        load_checklist("nonexistent-checklist-xyz")


def test_checklist_steps_are_parsed():
    cl = load_checklist("bad-internet")
    for step in cl.preflight:
        assert hasattr(step, "text")
        assert hasattr(step, "required")


def test_checklist_optional_step():
    cl = load_checklist("bad-internet")
    optional = [s for s in cl.verify if not s.required]
    assert len(optional) >= 1  # SHA256 is optional
