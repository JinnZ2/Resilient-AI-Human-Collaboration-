"""Accessibility profiles for voice_assist formatting.

Optional presets for --profile on `format-text` / `summarize`. Profiles
only supply defaults — an explicit --width or --sentences flag always
wins. Omitting --profile keeps the original built-in defaults.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AccessibilityProfile:
    name: str
    description: str
    width: int
    sentences: int


PROFILES: dict[str, AccessibilityProfile] = {
    "dyslexia": AccessibilityProfile(
        name="dyslexia",
        description="Short lines, generous paragraph breaks.",
        width=50,
        sentences=5,
    ),
    "low-vision": AccessibilityProfile(
        name="low-vision",
        description="Very short lines for large-font / zoomed displays.",
        width=36,
        sentences=5,
    ),
    "adhd": AccessibilityProfile(
        name="adhd",
        description="Shorter summaries, moderate line width.",
        width=60,
        sentences=3,
    ),
    "concise": AccessibilityProfile(
        name="concise",
        description="Minimal summary for a quick skim.",
        width=70,
        sentences=2,
    ),
}


def get_profile(name: str) -> AccessibilityProfile:
    """Look up a profile by name. Raises KeyError with the valid names on miss."""
    try:
        return PROFILES[name]
    except KeyError:
        valid = ", ".join(sorted(PROFILES))
        raise KeyError(f"Unknown profile '{name}'. Available: {valid}") from None


def list_profiles() -> list[AccessibilityProfile]:
    return list(PROFILES.values())
