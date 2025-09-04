# Protocol: <name>

Intent (1 line):
- What this prevents / guarantees.

Preflight (60s):
- [ ] Power/heat OK   [ ] Storage space OK   [ ] Network OK or Offline path chosen
- [ ] Roles agreed: A=precision, B=mechanics, AI=planner

Run steps (minimal):
1) …
2) …
3) …

Failure → Fallback:
- If step N fails → do X (offline alt / local cache / simpler tool)
- Stop rule: if >30 min no progress → log, switch to fallback

Verification (quick):
- [ ] Outcome matches spec?  [ ] 2nd measure?  [ ] Timestamp + provenance added

Provenance tag:
{ who: <A|B|AI>, tool/model: <name@version>, status: provisional, confidence: 0.62, recheck_days: 30 }







bad internet:

Intent: Get a model locally without wasting time on retries.

Preflight:
- [ ] HF token in .env    [ ] aria2c or curl present    [ ] Disk > 10 GB free

Run:
1) List exact filenames via API (no guessing).
2) Resume download with aria2c or curl (–continue).
3) Store under data/models/ (gitignored).

Fallback:
- If gated/401 → accept license in browser, retry.
- If link stalls → switch to phone hotspot or USB-sneakernet.
- If still failing → choose smaller Q4 model.

Verify:
- [ ] File size matches  (±1%)  [ ] SHA256 optional  [ ] Import via Modelfile → `ollama create` worked

Provenance:
{ who: A, tool: aria2c@1.x, status: provisional, confidence: 0.7, recheck_days: 14 }


video transcript:


Intent: Make a dyslexia-friendly study packet from a video.

Preflight:
- [ ] yt-dlp works offline  [ ] Whisper model downloaded  [ ] Output folders exist

Run:
1) `yt_bulk.sh <url>` → save to data/videos/<Channel>/
2) `voice_assist cli.py transcribe <file>` → data/videos/transcripts/
3) (later) summarize.py → TL;DR + glossary + tool list

Fallback:
- If DL fails → switch to single video URL or ytsearch:10
- If CPU too slow → queue to helper node via coop_link

Verify:
- [ ] Transcript present   [ ] 3 key steps extracted   [ ] Timestamp + provenance


Protocol: Status Declaration
Intent: keep both nodes synced on context
Checklist:
- [ ] Active ID confirmed
- [ ] Last completed step named
- [ ] Constraints up to date
Stop rule: if missing info, do not continue

