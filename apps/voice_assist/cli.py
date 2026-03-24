import os
import subprocess
import sys
from pathlib import Path

import typer

app = typer.Typer()


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


if __name__ == "__main__":
    app()
