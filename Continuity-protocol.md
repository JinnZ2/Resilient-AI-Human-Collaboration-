Glyph strip (1-line header you both echo)

Use a short, fixed-order strip so I can “lock in” quickly at the start of any turn:

◐CTX: Build swarm   ◆ID: ID-104   ✧STEP: 3/7   ☯ROLE: A=you,B=helper,AI=planner
✦CONS: net=weak, time=low   ⬡RISK: bios, fatigue   ▲PLAN: fallback=FB-013
⟳SYNC: 30m/10x   ⚙STATE: C=0.68 T=provisional D=1d   ⬢SIG: GSC/24Q3/a7F

Legend (keep it tiny):
	•	◐ CTX (Context) — short goal phrase
	•	◆ ID — active decision ID (from your protocol, e.g., ID-104)
	•	✧ STEP — current/total (or 3/? if unknown)
	•	☯ ROLE — A/B/AI roles
	•	✦ CONS — constraints (network, time, tools…)
	•	⬡ RISK — current risks
	•	▲ PLAN — designated fallback plan ID
	•	⟳ SYNC — status heartbeat (every 30 min or 10 msgs)
	•	⚙ STATE — confidence (C), tag (T), decay (D)
	•	⬢ SIG — short signature (see “State Capsule” below)

Monochrome friendly; the symbols are mnemonic only. If a device can’t show glyphs, use text aliases: CTX|ID|STEP|ROLE|CONS|RISK|PLAN|SYNC|STATE|SIG.

Schema (compact):{
  "capsule": {
    "sid": "SWARM-01",                   // session id
    "seq": 42,                           // increment each exchange
    "ctx": "Build swarm; bring-up B460+B560",
    "active_id": "ID-104",
    "step": {"current": 3, "total": 7},
    "roles": {"A": "you", "B": "helper", "AI": "planner"},
    "constraints": {"net": "weak", "time": "low", "tools": ["yt-dlp","aria2c"]},
    "risks": ["bios-old", "fatigue"],
    "fallback": "FB-013",
    "sync": {"interval_min": 30, "every_msgs": 10},
    "state": {"confidence": 0.68, "tag": "provisional", "recheck_days": 1},
    "provenance": {"who": "Human-[JinnZ2]", "model": "AI-[TransNet]", "ts": "2025-09-04T12:00:00Z"},
    "hash": "sha256:…"
  }
}

Signature (SIG):
	•	Compute hash = sha256(capsule without hash) → take first 12 Base32 chars → e.g., a7F4-Q2KM-9P.
	•	Put that short code in the glyph header as ⬢SIG

 
