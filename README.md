# Resilient AI-Human Collaboration

**Goal:** Practical, resilient tools that bridge complex communication — especially for dyslexia-friendly learning, local AI, and offline/low-bandwidth environments.

## What's Here

| Path | Description |
|------|-------------|
| `apps/protocol/` | Collaboration protocol CLI — session state, decision IDs, checklists, risk tracking |
| `apps/voice_assist/` | Transcribe videos to text, summarize, and format for accessibility |
| `scripts/hf_get.sh` | Resilient Hugging Face model downloader (resume + token) |
| `scripts/yt_bulk.sh` | Resilient YouTube bulk downloader |
| `scripts/prep_cpu.sh` | One-shot Ubuntu dependency installer |
| `docs/` | Human-AI collaboration protocols and checklists |
| `tests/` | Test suite (pytest) |

## Quickstart (Ubuntu)

```bash
git clone https://github.com/JinnZ2/Resilient-AI-Human-Collaboration-.git
cd Resilient-AI-Human-Collaboration-
cp env.example .env && nano .env   # put HF_TOKEN

# Install project
pip install -e ".[dev]"

# Or system setup first
bash scripts/prep_cpu.sh
```

## Protocol CLI

Manage structured collaboration sessions with decision tracking, constraints, and sync capsules.

```bash
# Start a session
python -m apps.protocol.cli init --ctx "Build swarm"

# Manage decision points
python -m apps.protocol.cli id new "Power supply bypass"
python -m apps.protocol.cli id list
python -m apps.protocol.cli id pause ID-001
python -m apps.protocol.cli id resume ID-001
python -m apps.protocol.cli id complete ID-001
python -m apps.protocol.cli id step ID-001 3

# Set constraints
python -m apps.protocol.cli constraint net offline
python -m apps.protocol.cli constraint time low

# Manage risks
python -m apps.protocol.cli risk add "power-loss"
python -m apps.protocol.cli risk list
python -m apps.protocol.cli risk remove "power-loss"

# Set confidence
python -m apps.protocol.cli confidence 0.85 --tag confirmed

# View status and sync
python -m apps.protocol.cli status
python -m apps.protocol.cli sync

# Export session report
python -m apps.protocol.cli export              # markdown
python -m apps.protocol.cli export --fmt json    # JSON

# Run checklists
python -m apps.protocol.cli checklist list
python -m apps.protocol.cli checklist run bad-internet
```

### Available Checklists

| Checklist | Purpose |
|-----------|---------|
| `bad-internet` | Download models on unreliable connections |
| `video-transcript` | Create dyslexia-friendly study packets from video |
| `status-declaration` | Sync context between collaborators |
| `new-session` | Bootstrap a fresh collaboration session |
| `hardware-swap` | Swap hardware mid-session without losing state |
| `context-recovery` | Recover after an interruption or communication break |

## Voice Assist

Transcribe audio/video and format text for accessibility.

```bash
# Transcribe a local file
python -m apps.voice_assist.cli transcribe <file>

# Download + transcribe a YouTube video
python -m apps.voice_assist.cli grab-and-transcribe <url>

# Reformat text for dyslexia-friendly reading (short lines, clear breaks)
python -m apps.voice_assist.cli format-text transcript.txt --width 60

# Extract key sentences from a transcript (offline, no ML needed)
python -m apps.voice_assist.cli summarize transcript.txt --sentences 5
```

## Scripts

```bash
# Download a Hugging Face model
bash scripts/hf_get.sh TheBloke/Mistral-7B-Instruct-v0.2-GGUF mistral-7b-instruct-v0.2.Q4_K_M.gguf

# Bulk-download YouTube playlist
bash scripts/yt_bulk.sh "data/videos" "https://www.youtube.com/playlist?list=PL..."
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=apps --cov-report=term-missing
```

## Accessibility / Dyslexia

- **Video to Text** transcripts (`apps/voice_assist`)
- **Dyslexia-friendly formatting** — short lines, clear paragraph breaks
- **Extractive summaries** — key points without needing ML models
- Dictation + local models (future: Vosk / Whisper streaming)
- Large text, high-contrast CLI output

## License

MIT — see [LICENSE](LICENSE).
