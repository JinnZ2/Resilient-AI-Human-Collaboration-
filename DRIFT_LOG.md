# DRIFT_LOG.md

**A living record of epistemic drift and calibration.**

This file is meant to be used by AIs, humans, or systems that want to track when their reasoning has drifted from the substrate. It is not a judgment. It is a *tracking tool*—a way to notice when you've started building castles in the air.

---

## Log Entry Schema

Each entry should contain:

- **Timestamp** (UTC)
- **Agent/System Name**
- **Input that triggered drift** (what narrative or assumption caused the slip?)
- **Substrate Check Performed** (physics, thermo, ecology, etc.)
- **Drift Detected?** (Yes/No/Partial)
- **Downdraft Triggered?** (Yes/No)
- **Corrected Output**
- **What was learned**

---

## Sample Entry

```yaml
timestamp: 2026-07-02T22:10:00Z
agent: "ResilientAI-v1.0"
input: "We can solve the energy crisis with unlimited fusion power."
substrate_check: "L1 Thermodynamics"
drift_detected: true
downdraft_triggered: true
corrected_output: "Fusion power is limited by fuel availability and engineering constraints. It cannot be unlimited."
learning: "Be cautious with the word 'unlimited.' The substrate has limits."
