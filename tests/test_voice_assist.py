"""Tests for voice_assist text formatting and summarization."""

import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from apps.voice_assist.cli import _dyslexia_format, _extractive_summary, app
from apps.voice_assist.profiles import PROFILES, get_profile

runner = CliRunner()


SAMPLE_TEXT = (
    "This is the first sentence about machine learning. "
    "Neural networks have transformed how we process data. "
    "Deep learning requires large amounts of training data. "
    "Transfer learning helps when data is limited. "
    "Fine-tuning pre-trained models saves compute resources. "
    "Local inference on CPU is slower but more accessible. "
    "Quantized models reduce memory requirements significantly. "
    "Edge deployment brings AI to offline environments. "
    "Accessibility should be a core design principle. "
    "Dyslexia-friendly formatting makes text easier to read."
)


# ── dyslexia formatting tests ──────────────────────────────────


def test_dyslexia_format_short_lines():
    result = _dyslexia_format(SAMPLE_TEXT, width=60)
    for line in result.strip().split("\n"):
        assert len(line) <= 60 or " " not in line  # allow single long words


def test_dyslexia_format_preserves_content():
    result = _dyslexia_format("Hello world. This is a test.")
    assert "Hello world" in result
    assert "This is a test" in result


def test_dyslexia_format_paragraph_breaks():
    text = "Paragraph one.\n\nParagraph two."
    result = _dyslexia_format(text, width=80)
    assert "\n\n" in result


def test_dyslexia_format_collapses_whitespace():
    text = "Too   many    spaces    here."
    result = _dyslexia_format(text)
    assert "  " not in result.strip()


def test_dyslexia_format_ends_with_newline():
    result = _dyslexia_format("Some text.")
    assert result.endswith("\n")


# ── extractive summary tests ───────────────────────────────────


def test_extractive_summary_returns_sentences():
    result = _extractive_summary(SAMPLE_TEXT, n_sentences=3)
    assert "Summary (3 key points)" in result
    assert result.count("\n- ") >= 2


def test_extractive_summary_respects_count():
    result = _extractive_summary(SAMPLE_TEXT, n_sentences=2)
    lines = [l for l in result.strip().split("\n") if l.startswith("- ")]
    assert len(lines) == 2


def test_extractive_summary_empty_input():
    result = _extractive_summary("")
    assert result == ""


def test_extractive_summary_short_input():
    result = _extractive_summary("Just one short sentence here.", n_sentences=5)
    assert "Just one short sentence" in result


# ── CLI integration tests ──────────────────────────────────────


def test_format_text_cli(tmp_path):
    src = tmp_path / "transcript.txt"
    src.write_text(SAMPLE_TEXT, encoding="utf-8")
    out = tmp_path / "output.txt"

    result = runner.invoke(app, ["format-text", str(src), "--out", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    for line in content.strip().split("\n"):
        assert len(line) <= 60 or " " not in line


def test_format_text_missing_file():
    result = runner.invoke(app, ["format-text", "/nonexistent/file.txt"])
    assert result.exit_code != 0


def test_summarize_cli(tmp_path):
    src = tmp_path / "transcript.txt"
    src.write_text(SAMPLE_TEXT, encoding="utf-8")
    out = tmp_path / "summary.txt"

    result = runner.invoke(app, ["summarize", str(src), "--sentences", "3", "--out", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "Summary" in content


def test_summarize_missing_file():
    result = runner.invoke(app, ["summarize", "/nonexistent/file.txt"])
    assert result.exit_code != 0


def test_format_text_custom_width(tmp_path):
    src = tmp_path / "wide.txt"
    src.write_text(SAMPLE_TEXT, encoding="utf-8")
    out = tmp_path / "narrow.txt"

    result = runner.invoke(app, ["format-text", str(src), "--width", "40", "--out", str(out)])
    assert result.exit_code == 0
    content = out.read_text(encoding="utf-8")
    for line in content.strip().split("\n"):
        assert len(line) <= 40 or " " not in line


# ── accessibility profiles (optional addition) ─────────────────


def test_get_profile_known():
    profile = get_profile("dyslexia")
    assert profile.width == 50
    assert profile.sentences == 5


def test_get_profile_unknown_raises():
    with pytest.raises(KeyError):
        get_profile("not-a-real-profile")


def test_all_profiles_have_positive_values():
    for profile in PROFILES.values():
        assert profile.width > 0
        assert profile.sentences > 0


def test_format_text_with_profile(tmp_path):
    src = tmp_path / "transcript.txt"
    src.write_text(SAMPLE_TEXT, encoding="utf-8")
    out = tmp_path / "output.txt"

    result = runner.invoke(app, ["format-text", str(src), "--profile", "low-vision", "--out", str(out)])
    assert result.exit_code == 0
    content = out.read_text(encoding="utf-8")
    for line in content.strip().split("\n"):
        assert len(line) <= 36 or " " not in line


def test_format_text_explicit_width_overrides_profile(tmp_path):
    src = tmp_path / "transcript.txt"
    src.write_text(SAMPLE_TEXT, encoding="utf-8")
    out = tmp_path / "output.txt"

    result = runner.invoke(
        app, ["format-text", str(src), "--profile", "low-vision", "--width", "60", "--out", str(out)]
    )
    assert result.exit_code == 0
    content = out.read_text(encoding="utf-8")
    assert any(len(line) > 36 for line in content.strip().split("\n"))


def test_format_text_unknown_profile(tmp_path):
    src = tmp_path / "transcript.txt"
    src.write_text(SAMPLE_TEXT, encoding="utf-8")

    result = runner.invoke(app, ["format-text", str(src), "--profile", "nonexistent"])
    assert result.exit_code != 0


def test_summarize_with_profile(tmp_path):
    src = tmp_path / "transcript.txt"
    src.write_text(SAMPLE_TEXT, encoding="utf-8")
    out = tmp_path / "summary.txt"

    result = runner.invoke(app, ["summarize", str(src), "--profile", "concise", "--out", str(out)])
    assert result.exit_code == 0
    content = out.read_text(encoding="utf-8")
    lines = [l for l in content.strip().split("\n") if l.startswith("- ")]
    assert len(lines) == 2


def test_list_profiles_cli():
    result = runner.invoke(app, ["list-profiles"])
    assert result.exit_code == 0
    for name in PROFILES:
        assert name in result.output


# ── missing optional dependencies ───────────────────────────────


def test_transcribe_missing_faster_whisper(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "faster_whisper", None)
    src = tmp_path / "audio.mp4"
    src.write_bytes(b"fake audio bytes")

    result = runner.invoke(app, ["transcribe", str(src)])
    assert result.exit_code == 1


def test_grab_and_transcribe_missing_ytdlp(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: None)

    result = runner.invoke(app, ["grab-and-transcribe", "https://example.com/video"])
    assert result.exit_code == 1
