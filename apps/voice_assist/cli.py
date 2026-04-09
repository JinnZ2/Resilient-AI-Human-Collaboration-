"""Voice assist CLI — transcription and dyslexia-friendly text tools."""

import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import typer

app = typer.Typer(help="Transcribe audio/video and format text for accessibility.")


def _transcribe(src: str, out_dir: str = "data/videos/transcripts") -> Path:
    """Core transcription logic. Returns the output file path."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print(
            "Error: faster-whisper is not installed.\n"
            "Run: pip install faster-whisper",
            file=sys.stderr,
        )
        raise SystemExit(1)

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    model_size = os.getenv("WHISPER_MODEL", "small")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(src)
    out = Path(out_dir) / (Path(src).stem + ".txt")
    with open(out, "w", encoding="utf-8") as f:
        for seg in segments:
            f.write(seg.text.strip() + "\n")
    print(f"Transcript -> {out}")
    return out


@app.command()
def transcribe(src: str, out_dir: str = "data/videos/transcripts") -> None:
    """Transcribe a local video or audio file to text."""
    _transcribe(src, out_dir)


@app.command()
def grab_and_transcribe(url: str) -> None:
    """Download a single YouTube video, then transcribe it."""
    dest = Path("data/videos/_single")
    dest.mkdir(parents=True, exist_ok=True)
    cmd = [
        "yt-dlp", "-f", "mp4",
        "-o", str(dest / "%(title).120B.%(ext)s"),
        "-ci", "-N", "4",
        "--retries", "50", "--fragment-retries", "50",
        url,
    ]
    subprocess.run(cmd, check=True)
    files = sorted(dest.glob("*.mp4"), key=os.path.getmtime)
    if not files:
        print("No file downloaded.", file=sys.stderr)
        raise SystemExit(1)
    _transcribe(str(files[-1]))


# ── accessibility / dyslexia-friendly formatting ────────────────


@app.command()
def format_text(
    src: str = typer.Argument(..., help="Path to a plain-text transcript file"),
    width: int = typer.Option(60, help="Max characters per line (dyslexia-friendly default: 60)"),
    out: str = typer.Option("", help="Output file path (default: <src>.formatted.txt)"),
) -> None:
    """Reformat a transcript for dyslexia-friendly reading.

    Applies short line widths, paragraph breaks on sentence boundaries,
    and clear section separators. Designed for high readability on screens
    and printed pages.
    """
    src_path = Path(src)
    if not src_path.exists():
        print(f"File not found: {src}", file=sys.stderr)
        raise SystemExit(1)

    raw = src_path.read_text(encoding="utf-8")
    formatted = _dyslexia_format(raw, width)

    out_path = Path(out) if out else src_path.with_suffix(".formatted.txt")
    out_path.write_text(formatted, encoding="utf-8")
    print(f"Formatted -> {out_path}")


@app.command()
def summarize(
    src: str = typer.Argument(..., help="Path to a plain-text transcript file"),
    sentences: int = typer.Option(5, help="Number of key sentences to extract"),
    out: str = typer.Option("", help="Output file path (default: <src>.summary.txt)"),
) -> None:
    """Extract key sentences from a transcript (extractive summary).

    Uses a simple frequency-based approach that works offline without
    any ML models — suitable for low-resource environments.
    """
    src_path = Path(src)
    if not src_path.exists():
        print(f"File not found: {src}", file=sys.stderr)
        raise SystemExit(1)

    raw = src_path.read_text(encoding="utf-8")
    summary = _extractive_summary(raw, sentences)

    out_path = Path(out) if out else src_path.with_suffix(".summary.txt")
    out_path.write_text(summary, encoding="utf-8")
    print(f"Summary -> {out_path}")


def _dyslexia_format(text: str, width: int = 60) -> str:
    """Reformat text for dyslexia-friendly reading.

    - Short lines (default 60 chars)
    - Extra blank line between paragraphs
    - Break on sentence boundaries where possible
    """
    paragraphs = re.split(r"\n\s*\n", text.strip())
    result_parts: list[str] = []

    for para in paragraphs:
        # Collapse internal whitespace
        clean = " ".join(para.split())
        wrapped = textwrap.fill(clean, width=width, break_long_words=False, break_on_hyphens=False)
        result_parts.append(wrapped)

    return "\n\n".join(result_parts) + "\n"


def _extractive_summary(text: str, n_sentences: int = 5) -> str:
    """Simple extractive summarizer using word frequency scoring.

    No external dependencies required — works fully offline.
    """
    # Split into sentences
    raw_sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if not raw_sentences:
        return ""

    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 10]
    if not sentences:
        return text.strip()

    # Build word frequency table (lowercased, ignore short words)
    freq: dict[str, int] = {}
    for sent in sentences:
        for word in re.findall(r"[a-zA-Z]{3,}", sent.lower()):
            freq[word] = freq.get(word, 0) + 1

    # Score sentences by sum of word frequencies
    scored = []
    for i, sent in enumerate(sentences):
        words = re.findall(r"[a-zA-Z]{3,}", sent.lower())
        score = sum(freq.get(w, 0) for w in words)
        # Slight bias toward earlier sentences
        score *= 1.0 / (1.0 + 0.05 * i)
        scored.append((score, i, sent))

    # Take top N by score, output in original order
    scored.sort(key=lambda x: x[0], reverse=True)
    top = sorted(scored[:n_sentences], key=lambda x: x[1])

    lines = [f"- {item[2]}" for item in top]
    header = f"Summary ({len(lines)} key points):\n"
    return header + "\n".join(lines) + "\n"


if __name__ == "__main__":
    app()
