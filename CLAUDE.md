# CLAUDE.md — Project Guide

## Project Overview

Resilient AI-Human Collaboration: practical, resilient tools for complex
communication — dyslexia-friendly learning, local AI, and offline/low-bandwidth
environments.

## Repository Layout

```
scripts/          Shell utilities (download, setup)
apps/             Application code (Python)
  voice_assist/   Whisper-based transcription CLI + accessibility formatting
  protocol/       Collaboration protocol CLI (decision IDs, checklists, state capsules)
docs/             Protocol docs and checklists
tests/            Test suite (pytest)
.github/          CI workflows
env.example       Template for .env (HF_TOKEN, YTDLP_OPTS)
pyproject.toml    Project config and dependencies
```

## Conventions

- **File naming**: lowercase kebab-case for docs (`continuity-protocol.md`),
  snake_case for code (`cli.py`, `hf_get.sh`).
- **Shell scripts**: always use `set -euo pipefail` and a shebang of
  `#!/usr/bin/env bash`.
- **Python**: Python 3.10+. Use `typer` for CLIs, type hints where practical.
- **Dependencies**: declared in `pyproject.toml`; per-app `requirements.txt`
  kept for standalone use.
- **Data directories** (`data/models/`, `data/videos/`, `data/cache/`) are
  gitignored — never commit large binaries.

## Common Commands

```bash
# Install project (editable, with dev deps)
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v

# System setup (Ubuntu)
bash scripts/prep_cpu.sh

# Download a Hugging Face model
bash scripts/hf_get.sh <repo> <file>

# Bulk-download YouTube playlist
bash scripts/yt_bulk.sh <dest> <url>

# Transcribe a local file
python -m apps.voice_assist.cli transcribe <file>

# Format text for dyslexia-friendly reading
python -m apps.voice_assist.cli format-text <file> --width 60

# Summarize a transcript (offline, no ML)
python -m apps.voice_assist.cli summarize <file> --sentences 5

# Protocol tools — session management
python -m apps.protocol.cli init --ctx "Build swarm"
python -m apps.protocol.cli id new "Power supply bypass"
python -m apps.protocol.cli id list
python -m apps.protocol.cli risk add "power-loss"
python -m apps.protocol.cli confidence 0.85 --tag confirmed
python -m apps.protocol.cli checklist run bad-internet
python -m apps.protocol.cli status
python -m apps.protocol.cli sync
python -m apps.protocol.cli export
python -m apps.protocol.cli export --fmt json
```

## Code Quality

- Keep functions small and single-purpose.
- Prefer early returns over deep nesting.
- Handle missing dependencies gracefully with clear error messages.
- Shell scripts should quote all variable expansions.
- All new features should include tests.
