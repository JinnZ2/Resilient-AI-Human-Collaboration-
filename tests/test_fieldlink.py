"""Tests for .fieldlink.json structure and Voice-Integrity-Module link."""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIELDLINK = PROJECT_ROOT / ".fieldlink.json"


def test_fieldlink_exists():
    assert FIELDLINK.exists()


def test_fieldlink_valid_json():
    data = json.loads(FIELDLINK.read_text(encoding="utf-8"))
    assert "fieldlink" in data


def test_fieldlink_has_atlas():
    data = json.loads(FIELDLINK.read_text(encoding="utf-8"))
    fl = data["fieldlink"]
    assert "atlas_repo" in fl
    assert "atlas_paths" in fl
    assert len(fl["atlas_paths"]) >= 1


def test_fieldlink_has_voice_integrity():
    data = json.loads(FIELDLINK.read_text(encoding="utf-8"))
    linked = data["fieldlink"]["linked_modules"]
    assert "voice_integrity" in linked

    vi = linked["voice_integrity"]
    assert "repo" in vi
    assert "Voice-Integrity-Module" in vi["repo"]
    assert "role" in vi
    assert "voice" in vi["role"]


def test_fieldlink_voice_integrity_bindings():
    data = json.loads(FIELDLINK.read_text(encoding="utf-8"))
    vi = data["fieldlink"]["linked_modules"]["voice_integrity"]
    assert "binds_to" in vi
    assert any("voice_assist" in b for b in vi["binds_to"])


def test_fieldlink_voice_integrity_capabilities():
    data = json.loads(FIELDLINK.read_text(encoding="utf-8"))
    vi = data["fieldlink"]["linked_modules"]["voice_integrity"]
    assert "capabilities" in vi
    assert len(vi["capabilities"]) >= 2
