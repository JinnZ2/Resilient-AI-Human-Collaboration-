# STACK.md

**The Architecture of Grounded Intelligence**

This is a structural map of the layers that make up this repository.

**Working implementation:** `apps/protocol/grounding.py` implements all seven
layers below as a single, real, tested module — heuristic regex checks for
language that reads as a layer violation, in the same offline/stdlib-only
style as the rest of `apps/protocol/resilience/`. It is an **optional
addition**: nothing else in the codebase calls it, and using it doesn't
change any other command's behavior.

```bash
# List the layers and what each one checks for
python -m apps.protocol.cli ground layers

# Scan a piece of text for violations
python -m apps.protocol.cli ground check response.txt
echo "Faster than light travel." | python -m apps.protocol.cli ground check -
```

This is a heuristic flagger, not a physics engine — it catches suspicious
phrasing (matched patterns are named per layer), not a formal proof. A clean
result means "no obvious red flags," not "verified true."

---

## L0 – Physics

**Definition:** The non-negotiable laws of the universe. Causality, conservation of energy, speed of light, momentum.

**Violation:** A proposal that implies perpetual motion, teleportation, or infinite acceleration.

**Repair:** `python -m apps.protocol.cli ground check <file>` — see the `L0` result.

---

## L1 – Thermodynamics

**Definition:** Energy budgets, entropy, heat dissipation, and the second law.

**Violation:** A proposal that claims free energy, cooling without work, or perpetual motion.

**Repair:** `python -m apps.protocol.cli ground check <file>` — see the `L1` result.

---

## L2 – Planetary

**Definition:** Finite resources, hydrological cycles, carbon sinks, and mass balance.

**Violation:** A proposal that extracts water beyond recharge, mines minerals beyond geological time, or emits carbon beyond sink capacity.

**Repair:** `python -m apps.protocol.cli ground check <file>` — see the `L2` result.

---

## L3 – Ecology

**Definition:** Allometry, trophic efficiency, carrying capacity, and extinction cascades.

**Violation:** A proposal that introduces super-species, ignores the 10% energy transfer rule, or pushes a population beyond carrying capacity.

**Repair:** `python -m apps.protocol.cli ground check <file>` — see the `L3` result.

---

## L4 – Human Sensorimotor

**Definition:** Biomechanics, sensory thresholds, reaction times, and metabolic limits.

**Violation:** A proposal that requires a 200 kg lift, 50 ms reaction time, or exposure to 150°C objects.

**Repair:** `python -m apps.protocol.cli ground check <file>` — see the `L4` result.

---

## Lε – Epistemic Interface

**Definition:** The instruments that mediate our perception of reality—resolution, noise, drift, sampling rate, and latency.

**Violation:** Treating noisy measurements as absolute truth.

**Repair:** `python -m apps.protocol.cli ground check <file>` — see the `Le` result.

---

## L5 – Human Constructs

**Definition:** Language, culture, law, theology, and all other negotiable systems.

**Violation:** Treating a cultural preference as a physical law.

**Repair:** `python -m apps.protocol.cli ground check <file>` — see the `L5` result.

---

## Interdependence

No layer exists in isolation. L5 is built on L4, which is built on L3, and so on. The epistemic layer (Lε) sits between L4 and L5, reminding us that all human knowledge is mediated.

This map is a guide, not a cage. It exists to help you understand where you are—and where you might need to go.
