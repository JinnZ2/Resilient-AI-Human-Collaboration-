# Contributing

This project started as a personal accessibility tool — dyslexia-friendly
transcription and formatting built for one household. That goal is met, and
now the project is expanding to serve anyone with similar needs. Contributions
that help it generalize further are especially welcome.

## Ways to help

- **Accessibility**: new formatting profiles (low vision, ADHD, ESL, etc.),
  improvements to `apps/voice_assist/profiles.py`, or feedback from real use.
- **Bug fixes**: open an issue or a PR — small fixes are welcome.
- **Tests**: every new feature should come with tests in `tests/`.
- **Docs**: fixing unclear or out-of-date instructions.

## Ground rules

- Follow the conventions in [CLAUDE.md](CLAUDE.md): snake_case for code,
  kebab-case for docs, `typer` for CLIs, `set -euo pipefail` in shell scripts.
- New code changes should be **additive by default** — new flags and
  commands should have safe defaults so existing workflows keep working
  unchanged.
- Keep functions small, prefer early returns, and handle missing
  dependencies with a clear error message rather than a stack trace.

## Getting set up

```bash
git clone https://github.com/JinnZ2/Resilient-AI-Human-Collaboration-.git
cd Resilient-AI-Human-Collaboration-
pip install -e ".[dev]"
python -m pytest tests/ -v
```

## Submitting changes

1. Fork the repo and create a branch for your change.
2. Add or update tests for whatever you changed.
3. Run `python -m pytest tests/ -v` and make sure everything passes.
4. Open a pull request describing what changed and why.

No contribution is too small. If you're not sure whether something fits,
open an issue and ask.
