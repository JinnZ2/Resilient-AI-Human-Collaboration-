# Resilient AI-Human Collaboration

**Goal:** Practical, resilient tools that bridge complex communication — especially for dyslexia-friendly learning, local AI, and offline/low-bandwidth environments.

## What's Here

| Path | Description |
|------|-------------|
| `scripts/hf_get.sh` | Resilient Hugging Face model downloader (resume + token) |
| `scripts/yt_bulk.sh` | Resilient YouTube bulk downloader |
| `scripts/prep_cpu.sh` | One-shot Ubuntu dependency installer |
| `apps/voice_assist/` | Transcribe videos to text for study |
| `docs/` | Human-AI collaboration protocols and checklists |

## Quickstart (Ubuntu)

```bash
git clone https://github.com/JinnZ2/Resilient-AI-Human-Collaboration-.git
cd Resilient-AI-Human-Collaboration-
cp env.example .env && nano .env   # put HF_TOKEN
bash scripts/prep_cpu.sh

# Download a small open model first (example)
bash scripts/hf_get.sh TheBloke/Mistral-7B-Instruct-v0.2-GGUF mistral-7b-instruct-v0.2.Q4_K_M.gguf

# Grab a channel for offline study
bash scripts/yt_bulk.sh "data/videos" "https://www.youtube.com/playlist?list=PL..."
```

## Accessibility / Dyslexia

- **Video to Text** transcripts (`apps/voice_assist`)
- Dictation + local models (future: Vosk / Whisper streaming)
- Large text, high-contrast CLI output

## License

MIT — see [LICENSE](LICENSE).
