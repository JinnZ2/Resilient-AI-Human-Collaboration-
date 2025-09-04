# Resilient AI–Human Collaboration

**Goal:** Practical, resilient tools that bridge complex communication—especially for dyslexia-friendly learning, local AI, and offline/low-bandwidth environments.

## What’s here
- `scripts/hf_get.sh` – resilient Hugging Face model downloader (resume + token)
- `scripts/yt_bulk.sh` – resilient YouTube bulk downloader
- `apps/voice_assist/` – transcribe videos to text for study
- `apps/swarm_node/` – local agent + Ollama node (WIP)
- `Protocols.md` – human↔AI collaboration protocols

## Quickstart (Ubuntu)
```bash
git clone https://github.com/JinnZ2/Resilient-AI-Human-Collaboration-.git
cd Resilient-AI-Human-Collaboration-
cp env.example .env && nano .env   # put HF_TOKEN
bash scripts/prep_cpu.sh

# Download a small open model first (example)
bash scripts/hf_get.sh TheBloke/Mistral-7B-Instruct-v0.2-GGUF mistral-7b-instruct-v0.2.Q4_K_M.gguf

# Grab a channel for offline study (ex: MIT shop basics)
bash scripts/yt_bulk.sh "data/videos" "https://www.youtube.com/playlist?list=PL...MIT..."


Accessibility / Dyslexia
	•	Video → Text transcripts (apps/voice_assist)
	•	Dictation + local models (future: Vosk / Whisper streaming)
	•	Large text, high-contrast CLI output

License

MIT

# First issues (copy into GitHub “Issues”)

1) **Add resilient model download scripts**  
   - [ ] Add `scripts/hf_get.sh`, `.env` support, README doc  
   - [ ] Test with 2 public repos and 1 gated repo (license acceptance)

2) **Video study pipeline**  
   - [ ] Add `scripts/yt_bulk.sh` and basic usage doc  
   - [ ] Create curated lists (MIT Machine Shop, TractorTimewithTim, etc.)

3) **Voice assist MVP**  
   - [ ] Simple CLI (`apps/voice_assist/cli.py`)  
   - [ ] Instructions for CPU-only transcription

4) **Protocols to Practice**  
   - [ ] Turn items from `Protocols.md` into checklists/templates used by tools

5) **Ollama how-to**  
   - [ ] `apps/swarm_node/ollama.md`: where models live, `Modelfile`, `ollama create`  
   - [ ] Example with a small `.gguf` you already downloaded.

---



