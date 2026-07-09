# REVIEW.md

Review of this repo against `CLAUDE.md`, as of the current `apps/`-based
codebase (protocol CLI, voice_assist CLI, accessibility profiles, L0-L5
grounding checks).

---

## 1. Structural Consistency & Conventions

**File naming — mostly compliant, two real issues:**
- `apps/`, `tests/`, `scripts/` all use snake_case correctly (`cli.py`,
  `hf_get.sh`, `test_voice_assist.py`).
- `docs/` is correctly kebab-case (`continuity-protocol.md`,
  `example-checklists.md`, `protocols.md`).
- Root-level UPPERCASE docs (`README.md`, `CLAUDE.md`, `CONTRIBUTING.md`,
  `STACK.md`, `GROUNDING.md`, `AI_README.md`, `DRIFT_LOG.md`,
  `INVITATION.md`, `LICENSE`) follow standard GitHub convention for
  top-level meta-docs — not a CLAUDE.md violation, but see §4 for volume.
- **Bug:** `tests/monoculture_detector.py` opens with smart quotes
  (`“”"` instead of `"""`) and is a **syntax error** — `python -c
  "import ast; ast.parse(open('tests/monoculture_detector.py').read())"`
  raises `SyntaxError: invalid character '“'`. It also isn't collected
  by pytest (no `test_` prefix), so nothing currently catches this.

**`data/` gitignore:** correctly covers `data/models/`, `data/videos/`,
`data/cache/`, `data/pipeline_logs/`. Verified `git ls-files data/`
returns nothing — no binaries or logs accidentally committed.

**`requirements.txt` vs `pyproject.toml`:**
- `apps/protocol/requirements.txt` matches the core deps in
  `pyproject.toml` exactly (`typer`, `pydantic`, `pyyaml`) — in sync.
- `apps/voice_assist/requirements.txt` pins `whisper-timestamped==1.15.4`,
  which is **not** in `pyproject.toml`'s `voice` extra and is not
  imported anywhere in `apps/voice_assist/`. Looks like drift from an
  earlier design — either wire it in or drop it.

**`typer` + type hints:** consistently used across `apps/protocol/cli.py`,
`audit_cli.py`, `ground_cli.py`, `apps/voice_assist/cli.py`.

**Shell scripts:** all four (`hf_get.sh`, `prep_cpu.sh`,
`safe_ai_pipeline.sh`, `yt_bulk.sh`) have `#!/usr/bin/env bash` +
`set -euo pipefail`, and quote variable expansions
(`"${OUT_DIR}"`, `"${1:?...}"`).

---

## 2. README & Discoverability

- Purpose (dyslexia-friendly, local AI, offline/low-bandwidth) is clearly
  stated in README's "Origin & Expansion" and "What This Is" sections.
- One-liner usage examples are present and copy-pasteable for every
  major tool (`transcribe`, `format-text`, `protocol init`, `ground check`).
- **Missing:** `CITATION.cff`, `KEYWORDS.txt`, repo topics, license badge,
  an explicit "Why This Matters" callout. Snippets below.

**`CITATION.cff`** (new file, root):
```yaml
cff-version: 1.2.0
title: Resilient AI-Human Collaboration
message: If you use this software, please cite it.
type: software
authors:
  - name: JinnZ2
repository-code: https://github.com/JinnZ2/Resilient-AI-Human-Collaboration-
license: MIT
```

**`KEYWORDS.txt`** (new file, root):
```
accessibility, dyslexia-friendly, offline-first, local-ai,
collaboration-protocol, whisper, low-bandwidth, resilience
```

**License badge** (top of `README.md`, under the title):
```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
```

**"Why This Matters"** (one paragraph, could slot right after "Origin &
Expansion" in `README.md`):
```markdown
## Why This Matters

Accessibility tools and offline AI are usually treated as separate
concerns — accessibility is a UI afterthought, offline is an enterprise
edge case. This repo treats them as the same problem: software that
works for someone who reads differently, on a connection that isn't
guaranteed, without needing a subscription or a cloud account to do it.
```

---

## 3. Code Audit Highlights

- Functions are small and single-purpose with early returns
  (`format_text`, `summarize`, every `id_*` command in
  `apps/protocol/cli.py` — validate, then return/raise `typer.Exit`
  immediately on the bad path).
- Missing-dependency handling: `apps/voice_assist/cli.py:_transcribe`
  catches `ImportError` on `faster_whisper` and prints a clear
  `pip install` message before exiting — good pattern. **Gap:**
  `grab_and_transcribe` shells out to `yt-dlp` via `subprocess.run`
  with no check for the binary's presence first; if `yt-dlp` isn't
  installed, the user gets a raw `FileNotFoundError` traceback instead
  of a friendly message.
- Test coverage: strong for the protocol CLI (`test_cli.py`,
  `test_audit.py`, `test_grounding.py`, `test_checklist.py`,
  `test_state.py`, `test_capsule.py`) and for `format-text`/`summarize`/
  profiles (`test_voice_assist.py`). **Gap:** `transcribe` and
  `grab_and_transcribe` have zero tests — understandable since they need
  `faster-whisper`/`yt-dlp`, but at minimum a test asserting the
  friendly-error path (no `faster_whisper` installed → exit 1 with a
  clear message) is missing.
- Security: no `shell=True`, `os.system`, or `eval`/`exec` anywhere in
  `apps/` or `scripts/`. The one `subprocess.run` call
  (`grab_and_transcribe`) passes a list, not a shell string. `HF_TOKEN`
  is read from the environment and used only in an HTTP header, never
  logged or echoed. No issues found.

---

## 4. Organizational Suggestions

- **Root clutter:** `env.example` is fine, but `GROUNDING.md`,
  `AI_README.md`, `STACK.md`, `DRIFT_LOG.md`, `INVITATION.md`, and
  `Organize.md` (163 KB, 3645 lines) form a second, philosophical layer
  sitting at root alongside the practical project docs. README.md
  already flags the split ("Origin & Expansion" section), but a
  newcomer running `ls` still hits 6 large narrative files before
  reaching `apps/`. Consider moving them into `docs/philosophy/` (or
  similar), keeping `README.md`, `CLAUDE.md`, `CONTRIBUTING.md`, and
  `LICENSE` at root. Would cut root markdown files from 9 to 3.
- `tests/monoculture_detector.py` doesn't belong in `tests/` — it's a
  standalone CC0 analysis tool, not a pytest test, and (per §1) doesn't
  currently parse. Move it to `apps/protocol/resilience/` or a new
  `tools/` directory, and fix the smart-quote syntax error either way.
- `apps/protocol` vs `apps/voice_assist` as separate installable
  packages: current single-`pyproject.toml` layout (with `voice` as an
  optional extra) is appropriate for this repo's size. No need to split
  into separate packages yet — revisit if `voice_assist` grows enough
  dependencies to want its own release cadence.
- `.fieldlink.json` at root references external repos (`BioGrid2.0`,
  `Voice-Integrity-Module`) that aren't mentioned anywhere in
  `README.md`, `CLAUDE.md`, or `AI_README.md`. Worth a one-line pointer
  in `AI_README.md` so it doesn't read as an orphaned config file.
- `docs/` and `tests/` are otherwise well-structured — flat, clearly
  named, one file per topic/module.

---

## 5. Repository Topics Suggestion

```
accessibility, dyslexia-friendly, offline-first, local-ai,
collaboration-protocol, whisper, low-bandwidth, resilience
```
