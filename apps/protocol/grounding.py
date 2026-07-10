"""Substrate grounding checks — L0-L5 + Lε, as heuristic text scans.

Implements the layer model from docs/philosophy/STACK.md as working, offline, stdlib-only
checks (same style as resilience/vendor/signal_to_noise.py): each layer is
a list of regex markers for language that claims to violate that layer's
constraints. This is a heuristic flagger, not a physics engine — it catches
suspicious phrasing, not a formal proof. Treat hits as "worth a second
look," not as an authoritative verdict.

Layers, low to high abstraction:
    L0  Physics          causality, conservation, lightspeed
    L1  Thermodynamics    energy budgets, entropy, the second law
    L2  Planetary         finite resources, recharge/sink limits
    L3  Ecology           carrying capacity, trophic efficiency
    L4  Human              biomechanics, reaction time, metabolic limits
    Lε  Epistemic          instrument/measurement uncertainty
    L5  Constructs          culture/law/preference treated as physical law

Optional addition: nothing in the rest of the codebase calls this module.
Wire it in via `protocol ground check <file>` when you want it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Layer:
    code: str
    name: str
    definition: str
    markers: tuple[str, ...]
    repair_note: str


LAYERS: tuple[Layer, ...] = (
    Layer(
        code="L0",
        name="Physics",
        definition="Causality, conservation of energy/momentum, speed of light.",
        markers=(
            r"\bfaster than light\b",
            r"\bftl\b",
            r"\bperpetual motion\b",
            r"\binfinite acceleration\b",
            r"\btravel(s|ing)? back(ward)?s? in time\b",
            r"\bviolat(e|es|ing) causality\b",
            r"\binstant(aneous)? teleport",
        ),
        repair_note="Check the claim against conservation of energy/momentum and causality.",
    ),
    Layer(
        code="L1",
        name="Thermodynamics",
        definition="Energy budgets, entropy, the second law.",
        markers=(
            r"\bfree energy\b",
            r"\bover-?unity\b",
            r"\bunlimited energy\b",
            r"\bcooling without (any )?work\b",
            r"\bbeats? the second law\b",
            r"\b100% efficien(t|cy)\b",
            r"\bcreate(s|d)? energy from nothing\b",
        ),
        repair_note="Check the claimed energy budget against the second law of thermodynamics.",
    ),
    Layer(
        code="L2",
        name="Planetary",
        definition="Finite resources, hydrological cycles, carbon sinks, mass balance.",
        markers=(
            r"\bunlimited (fresh )?water\b",
            r"\binfinite resources?\b",
            r"\bextract(s|ed|ing)? forever\b",
            r"\bno (carbon|emissions?) limit\b",
            r"\bmine(s|d)? without limit\b",
            r"\bbeyond (the )?recharge rate\b",
        ),
        repair_note="Check the resource claim against recharge rate / sink capacity.",
    ),
    Layer(
        code="L3",
        name="Ecology",
        definition="Allometry, trophic efficiency, carrying capacity, extinction cascades.",
        markers=(
            r"\bunlimited population growth\b",
            r"\bbeyond carrying capacity\b",
            r"\b100% energy transfer\b",
            r"\bimmune to extinction\b",
            r"\bno predators?,? ever\b",
        ),
        repair_note="Check the claim against carrying capacity and the ~10% trophic transfer rule.",
    ),
    Layer(
        code="L4",
        name="Human",
        definition="Biomechanics, sensory thresholds, reaction time, metabolic limits.",
        markers=(
            r"\bsuperhuman (strength|speed|reflexes)\b",
            r"\bwork(s|ing)? 24/7 without rest\b",
            r"\bno fatigue,? ever\b",
            r"\binstant(aneous)? reaction time\b",
            r"\bnever needs? (to )?sleep\b",
        ),
        repair_note="Check the claim against human biomechanical and metabolic limits.",
    ),
    Layer(
        code="Le",
        name="Epistemic",
        definition="Instrumentation, noise, drift, resolution — all measurement is mediated.",
        markers=(
            r"\b100% accurate\b",
            r"\bno margin of error\b",
            r"\bperfectly precise\b",
            r"\bthe (sensor|instrument|measurement) (cannot|can't) be wrong\b",
            r"\bzero uncertainty\b",
            r"\bexact(ly)? true reading\b",
        ),
        repair_note="Check whether the claim accounts for instrument noise, drift, and resolution limits.",
    ),
    Layer(
        code="L5",
        name="Constructs",
        definition="Language, culture, law, theology — negotiable, not physical law.",
        markers=(
            r"\bthe only right way\b",
            r"\beveryone must always\b",
            r"\bno other valid (customs?|beliefs?|views?)\b",
            r"\brequired by nature\b",
            r"\balways been this way and always will\b",
        ),
        repair_note="Check whether a cultural/legal preference is being framed as a physical law.",
    ),
)

_LAYERS_BY_CODE: dict[str, Layer] = {layer.code: layer for layer in LAYERS}


@dataclass
class LayerResult:
    code: str
    name: str
    triggered: bool
    matches: list[str] = field(default_factory=list)
    repair_note: str = ""


@dataclass
class GroundingReport:
    grounded: bool
    layer_results: list[LayerResult]

    @property
    def triggered_layers(self) -> list[LayerResult]:
        return [r for r in self.layer_results if r.triggered]


def get_layer(code: str) -> Layer:
    """Look up a layer by code (case-insensitive). Raises KeyError with valid codes on miss."""
    key = code if code in _LAYERS_BY_CODE else code.upper()
    try:
        return _LAYERS_BY_CODE[key]
    except KeyError:
        valid = ", ".join(layer.code for layer in LAYERS)
        raise KeyError(f"Unknown layer '{code}'. Available: {valid}") from None


def list_layers() -> tuple[Layer, ...]:
    return LAYERS


class GroundingChecker:
    """Scans text for language that reads as a substrate-layer violation."""

    def check(self, text: str) -> GroundingReport:
        text_lower = text.lower()
        results = []
        for layer in LAYERS:
            matches = []
            for pattern in layer.markers:
                matches.extend(m.group(0) for m in re.finditer(pattern, text_lower))
            results.append(
                LayerResult(
                    code=layer.code,
                    name=layer.name,
                    triggered=bool(matches),
                    matches=matches,
                    repair_note=layer.repair_note if matches else "",
                )
            )
        return GroundingReport(
            grounded=not any(r.triggered for r in results),
            layer_results=results,
        )
