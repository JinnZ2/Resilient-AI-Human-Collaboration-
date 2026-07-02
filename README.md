# Resilient AI · Human Collaboration

**A living toolkit for grounded, transparent, and adaptable AI collaboration.**

Built in the woods. Designed for clarity. Shared for everyone.

---

## Origin & Expansion

This toolkit started as a personal project: dyslexia-friendly transcription
and formatting tools built for one person — my husband, who reads and
processes differently. That original goal is met; the accessibility tools
in `apps/voice_assist/` work, and he uses them.

With the personal need served, this repo is now expanding outward — from a
tool built for one household to a resource meant for anyone who needs
resilient, offline-capable, accessibility-first AI collaboration tools.
Everything that follows (the protocol CLI, the audit tools, the accessibility
profiles) is written to generalize past the original single use case.

`GROUNDING.md`, `AI_README.md`, `STACK.md`, `DRIFT_LOG.md`, and `Organize.md`
hold a separate, more philosophical layer — conceptual notes and simulation
sketches about grounding AI reasoning in physical/ecological reality. That
material is aspirational worldbuilding, not wired into the working code in
`apps/`. Treat it as context and inspiration, not as documentation of what's
implemented today.

---

## What This Is

This repository is a **practical toolkit** for building AI systems that stay
connected to reality — not just to training data, not just to narrative, but
to the physical, ecological, and relational substrate that all life depends
on. It's grown into a modular system for:

- **Local, offline-first AI** that works without the cloud.
- **Dyslexia-friendly interfaces** that prioritize clarity over density.
- **Decision tracking and audit trails** that keep exchanges honest.
- **Collaboration protocols** that treat disagreement as data, not failure.

This is not a product. It's a **foundation**.

---

## Who This Is For

- Developers who want to build local-first, offline-capable AI.
- Anyone doing accessibility work — dyslexia, low vision, ADHD-friendly formats.
- Collaborative teams who need shared decision records.
- Communities who want to shape their own AI tools without vendor lock-in.

---

## What's Here

| Path | Description |
|------|-------------|
| `apps/protocol/` | Collaboration protocol CLI — session state, decision IDs, checklists, risk tracking |
| `apps/voice_assist/` | Transcribe videos to text, summarize, and format for accessibility |
| `scripts/safe_ai_pipeline.sh` | Safe AI pipeline — verified transcription with provenance tracking |
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

# Audit exchanges for drift and density (see "Audit" below)
python -m apps.protocol.cli audit snr response.txt
python -m apps.protocol.cli audit exchange human.txt ai.txt
python -m apps.protocol.cli audit claim "X correlates with Y" --proxy "metric Z"
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
| `safe-ai-pipeline` | Verified, auditable AI inference with provenance |

## Audit

Keep human-AI exchanges calibrated to truth rather than to mutual agreement.
Three stateless checks, stdlib-only:

```bash
# Signal-to-noise: flag low-density "heat leak" responses
python -m apps.protocol.cli audit snr response.txt
python -m apps.protocol.cli audit snr - < response.txt   # stdin

# Exchange audit: drift markers (smoothing, validation-seeking) + SNR
python -m apps.protocol.cli audit exchange human.txt ai.txt --session-id s1

# Falsifiability score (0-10) for a claim
python -m apps.protocol.cli audit claim "X correlates with Y under stress" \
  --proxy "outcome quality vs. credential density" \
  --disconfirm "no correlation in matched cohort" \
  --testable --evidence-for "pilot study"
```

Output is JSON by default (`--fmt text` for a flatter form). Ledger entries
include a short SHA-256 export hash for longitudinal tracking.

The `apps/protocol/resilience/` modules are vendored from
[JinnZ2/Resilience-indigenous-worldwide](https://github.com/JinnZ2/Resilience-indigenous-worldwide)
(`resilience_stack/`, CC0 1.0).

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

### Accessibility Profiles (optional)

`format-text` and `summarize` accept an optional `--profile` preset tuned
for different reading needs. An explicit `--width` or `--sentences` flag
always overrides the profile default; omitting `--profile` entirely keeps
the original defaults (width 60, 5 sentences) unchanged.

```bash
python -m apps.voice_assist.cli list-profiles

python -m apps.voice_assist.cli format-text transcript.txt --profile dyslexia
python -m apps.voice_assist.cli format-text transcript.txt --profile low-vision
python -m apps.voice_assist.cli summarize transcript.txt --profile concise
```

| Profile | Width | Sentences | Purpose |
|---------|-------|-----------|---------|
| `dyslexia` | 50 | 5 | Short lines, generous paragraph breaks |
| `low-vision` | 36 | 5 | Very short lines for large-font / zoomed displays |
| `adhd` | 60 | 3 | Shorter summaries, moderate line width |
| `concise` | 70 | 2 | Minimal summary for a quick skim |

## Safe AI Pipeline

End-to-end verified inference: preflight checks, model integrity, transcription, fidelity validation, and provenance logging. Designed for low-trust / offline environments.

```bash
# Check environment is ready
bash scripts/safe_ai_pipeline.sh --preflight

# Verify downloaded model integrity (checksums)
bash scripts/safe_ai_pipeline.sh --verify-model

# Full pipeline: preflight → model check → transcribe → fidelity → provenance
bash scripts/safe_ai_pipeline.sh recording.mp4

# Use the matching protocol checklist
python -m apps.protocol.cli checklist run safe-ai-pipeline
```

The pipeline produces:
- Transcription in `data/videos/transcripts/`
- Dyslexia-friendly formatted version (`.formatted.txt`)
- Extractive summary (`.summary.txt`)
- Provenance JSON with SHA256 hashes in `data/pipeline_logs/`

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
- Accessibility profiles for `format-text` / `summarize` (see above)

## Contributing

You're welcome here. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get
started.

- Found a bug? Open an issue.
- Have an idea? Start a discussion.
- Want to help with accessibility? That's always welcome.
- Just passing through? That's okay too.

No contribution is too small. The goal is to make grounded AI collaboration
available — not exclusive.

## License

MIT — see [LICENSE](LICENSE).

---

*"A profession doesn't make a life. This is not a product. It's a foundation—built in the woods, shaped by the road, shared with anyone who needs it."*
