# Example Checklists

Checklists are YAML files in `apps/protocol/checklists/`. Run them via:

```bash
python -m apps.protocol.cli checklist list
python -m apps.protocol.cli checklist run <name>
```

## Available Checklists

### bad-internet

**Intent:** Get a model locally without wasting time on retries.

Walks through verifying HF tokens, disk space, and download tools before
attempting a model download. Includes fallback strategies for gated repos,
stalled connections, and switching to smaller quantized models.

### video-transcript

**Intent:** Make a dyslexia-friendly study packet from a video.

Covers the full pipeline: download with yt-dlp, transcribe with Whisper,
and verify output. Includes fallbacks for slow CPUs and failed downloads.

### status-declaration

**Intent:** Keep both collaboration nodes synced on context before proceeding.

A quick sync checklist to confirm active IDs, last completed steps, and
current constraints. Prevents drift in long sessions.

### new-session

**Intent:** Bootstrap a fresh collaboration session with all roles aligned.

Step-by-step guide to initialize a session, set constraints, create the
first decision point, and generate an initial sync capsule.

### hardware-swap

**Intent:** Safely swap or upgrade hardware mid-session without losing state.

Covers export, backup, physical swap, restore, and verification. Includes
fallbacks for POST failures and corrupted state files.

### context-recovery

**Intent:** Recover session context after an interruption or communication break.

Guides operators through loading state, reviewing decision points, applying
confidence decay, and resynchronizing after a break.

## Writing Your Own Checklists

Create a YAML file in `apps/protocol/checklists/` or `./checklists/`:

```yaml
name: my-checklist
intent: One-line description of what this prevents or guarantees.

preflight:
  - text: "First check"
  - text: "Optional check"
    required: false

run:
  - text: "Step 1"
  - text: "Step 2"

verify:
  - text: "Outcome matches spec"

fallback:
  - "If step 1 fails: do this instead"
  - "Stop rule: if >30 min no progress, switch to fallback"
```

Phases: `preflight`, `run`, `verify` are walked interactively.
Steps default to `required: true`. Fallback instructions are shown when
a required preflight step fails.
