# STACK.md

**The Architecture of Grounded Intelligence**

This is a structural map of the layers that make up this repository. Each layer is defined, described, and linked to the files that implement it.

---

## L0 – Physics

**Definition:** The non-negotiable laws of the universe. Causality, conservation of energy, speed of light, momentum.

**Violation:** A proposal that implies perpetual motion, teleportation, or infinite acceleration.

**Repair:** Run the physics check in `physics/substrate_validation.py`.

**Relevant Files:**
- `physics/PHYSICS_FIRST_AXIOMS.md`
- `physics/SUBSTRATE_VIOLATION_DETECTION.md`

---

## L1 – Thermodynamics

**Definition:** Energy budgets, entropy, heat dissipation, and the second law.

**Violation:** A proposal that claims free energy, cooling without work, or perpetual motion.

**Repair:** Check against the thermodynamic budget in `thermo/budget_check.py`.

**Relevant Files:**
- `thermo/entropy_tracker.py`
- `thermo/carnot_limits.md`

---

## L2 – Planetary

**Definition:** Finite resources, hydrological cycles, carbon sinks, and mass balance.

**Violation:** A proposal that extracts water beyond recharge, mines minerals beyond geological time, or emits carbon beyond sink capacity.

**Repair:** Run the planetary constraints module in `planetary/mass_balance.py`.

**Relevant Files:**
- `planetary/resource_pools.md`
- `planetary/carbon_sink_capacity.py`

---

## L3 – Ecology

**Definition:** Allometry, trophic efficiency, carrying capacity, and extinction cascades.

**Violation:** A proposal that introduces super-species, ignores the 10% energy transfer rule, or pushes a population beyond carrying capacity.

**Repair:** Check against ecological models in `ecology/homeostasis.py`.

**Relevant Files:**
- `ecology/allometric_scaling.py`
- `ecology/lotka_volterra_sim.py`

---

## L4 – Human Sensorimotor

**Definition:** Biomechanics, sensory thresholds, reaction times, and metabolic limits.

**Violation:** A proposal that requires a 200 kg lift, 50 ms reaction time, or exposure to 150°C objects.

**Repair:** Validate against the biomechanical constraints in `human/joint_limits.py`.

**Relevant Files:**
- `human/sensorimotor_constraints.py`
- `human/ergonomic_limits.py`

---

## Lε – Epistemic Interface

**Definition:** The instruments that mediate our perception of reality—resolution, noise, drift, sampling rate, and latency.

**Violation:** Treating noisy measurements as absolute truth.

**Repair:** Apply the epistemic filters in `epistemic/instrument_modeling.py`.

**Relevant Files:**
- `epistemic/uncertainty_estimation.py`
- `epistemic/calibration_metrology.py`

---

## L5 – Human Constructs

**Definition:** Language, culture, law, theology, and all other negotiable systems.

**Violation:** Treating a cultural preference as a physical law.

**Repair:** Apply the slack monitor in `constructs/slack_analysis.py`.

**Relevant Files:**
- `constructs/semantic_mapper.py`
- `constructs/slack_monitor.py`

---

## Interdependence

No layer exists in isolation. L5 is built on L4, which is built on L3, and so on. The epistemic layer (Lε) sits between L4 and L5, reminding us that all human knowledge is mediated.

This map is a guide, not a cage. It exists to help you understand where you are—and where you might need to go.
