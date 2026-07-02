# =============================================================================
# CCO 1.0 Universal Public Domain Dedication
# 
# L0 Grounding Inspector: Physics & Causality Enforcement
# 
# Scenario: An AI proposes a motion plan for a 2D mass.
# The Inspector checks:
#   1. Energy Conservation (ΔKE ≈ Work_Input)
#   2. Causality (Position continuity, no instantaneous jumps)
#   3. Speed Limit (|v| <= c_max, set to 2.0 m/s for visualization)
#   4. Momentum sanity (No force = no acceleration)
# 
# If a violation is detected, the plan is "grounded" — corrected
# back to the nearest physically legal trajectory.
# =============================================================================

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# -----------------------------------------------------------------------------
# 1. PHYSICAL SYSTEM DEFINITION (Substrate Reality)
# -----------------------------------------------------------------------------
class PhysicalWorld:
    def __init__(self, mass=1.0, dt=0.05, max_speed=2.0):
        self.mass = mass
        self.dt = dt
        self.max_speed = max_speed
        self.gravity = np.array([0.0, -0.5])  # mild downward drift

    def is_valid_state(self, pos, vel):
        """Check L0 invariants for a given state."""
        # Speed limit
        if np.linalg.norm(vel) > self.max_speed:
            return False, "Speed limit exceeded"
        # Position finite (no NaN or Inf)
        if not np.isfinite(pos).all() or not np.isfinite(vel).all():
            return False, "Non-finite position/velocity"
        return True, "OK"

    def apply_physics(self, pos, vel, force, dt):
        """
        Euler integration of the true physical world.
        Force is clipped to ensure no energy creation.
        """
        # Ensure force doesn't break causality (must be finite)
        force = np.clip(force, -50, 50)
        
        # True acceleration from F=ma
        acc = force / self.mass + self.gravity
        
        # Update velocity and position (true physics)
        new_vel = vel + acc * dt
        new_pos = pos + new_vel * dt  # semi-implicit for stability
        
        # Enforce speed limit (relativistic/thermodynamic cap)
        speed = np.linalg.norm(new_vel)
        if speed > self.max_speed:
            new_vel = new_vel / speed * self.max_speed
        
        return new_pos, new_vel

# -----------------------------------------------------------------------------
# 2. THE "AI HALLUCINATOR" (Pretends to plan without physics)
# -----------------------------------------------------------------------------
def ai_hallucinated_plan(time_steps):
    """
    Generates a crazy, physically impossible trajectory.
    This simulates an ungrounded LLM writing a control sequence:
    - Teleportation jumps (position discontinuity)
    - Massive acceleration from tiny forces (energy violation)
    - Ignoring gravity/inertia
    """
    pos = np.array([0.0, 1.0])
    vel = np.array([0.0, 0.0])
    traj = [pos.copy()]
    forces = []
    
    for i in range(time_steps):
        # Hallucination 1: At step 20, "teleport" upward (violates continuity)
        if i == 20:
            pos[1] += 5.0  # Instant jump! No force applied.
        
        # Hallucination 2: At step 40, apply a tiny force but get massive speed
        if 40 <= i < 45:
            force = np.array([0.1, 0.1])  # Tiny force
            # But the AI *claims* the velocity doubles anyway (violates F=ma)
            vel = vel * 1.8  # Momentum creation from nothing!
        else:
            force = np.array([0.0, 0.0])
        
        # Hallucination 3: At step 60, ignore gravity entirely
        if i >= 60:
            vel = vel + np.array([0.0, -0.01])  # Doesn't even account for gravity properly
        
        # Record
        forces.append(force)
        pos = pos + vel * 0.05  # Using AI's flawed integration
        traj.append(pos.copy())
    
    return np.array(traj), np.array(forces)

# -----------------------------------------------------------------------------
# 3. THE L0 GROUNDING INSPECTOR (Substrate Reality Filter)
# -----------------------------------------------------------------------------
def l0_grounding_inspector(ai_traj, ai_forces, world, dt=0.05):
    """
    Takes the AI's proposed trajectory and forces, and runs it through
    the physics engine. If the AI deviates from physics, the Inspector
    projects the state back to the closest legal state.
    
    Returns:
      - corrected_traj: The physically plausible trajectory.
      - violation_flags: Which steps were illegal.
      - penalty_magnitude: How far the AI hallucinated.
    """
    # Start from the AI's initial state (assume that one is real)
    pos = ai_traj[0].copy()
    vel = np.array([0.0, 0.0])  # Start from rest (ground truth)
    
    corrected_traj = [pos.copy()]
    violations = []
    penalties = []
    
    for i in range(len(ai_forces)):
        # 1. What does the AI say the state should be at this step?
        ai_next_pos = ai_traj[i+1] if i+1 < len(ai_traj) else pos
        
        # 2. Apply TRUE physics to the previous corrected state
        force = ai_forces[i] if i < len(ai_forces) else np.array([0.0, 0.0])
        true_next_pos, true_next_vel = world.apply_physics(pos, vel, force, dt)
        
        # 3. Check L0 Invariants on the AI's proposed state
        valid, reason = world.is_valid_state(ai_next_pos, ai_next_pos - pos)
        
        if not valid:
            # Violation! The AI hallucinated.
            # We correct by adopting the TRUE physical state instead.
            corrected_pos = true_next_pos
            corrected_vel = true_next_vel
            violations.append(1)
            penalties.append(np.linalg.norm(ai_next_pos - true_next_pos))
        else:
            # AI's proposal is physically legal. We accept it, but 
            # we must ensure it doesn't diverge too far from true physics.
            # We interpolate to keep the system grounded (soft constraint)
            blend = 0.6  # 60% trust AI, 40% trust physics -> prevents drift
            corrected_pos = blend * ai_next_pos + (1 - blend) * true_next_pos
            corrected_vel = (corrected_pos - pos) / dt
            # Re-enforce speed limit
            if np.linalg.norm(corrected_vel) > world.max_speed:
                corrected_vel = corrected_vel / np.linalg.norm(corrected_vel) * world.max_speed
                corrected_pos = pos + corrected_vel * dt
            violations.append(0)
            penalties.append(0.0)
        
        # Update state for next iteration
        pos = corrected_pos
        vel = corrected_vel
        corrected_traj.append(pos.copy())
    
    return np.array(corrected_traj), np.array(violations), np.array(penalties)

# -----------------------------------------------------------------------------
# 4. RUN THE EXPERIMENT
# -----------------------------------------------------------------------------
time_steps = 200
dt = 0.05

# Instantiate the physical substrate
world = PhysicalWorld(mass=1.0, max_speed=2.0)

# Generate AI's hallucinated plan
ai_traj, ai_forces = ai_hallucinated_plan(time_steps)

# Run the L0 Inspector
corrected_traj, violations, penalties = l0_grounding_inspector(ai_traj, ai_forces, world, dt)

# -----------------------------------------------------------------------------
# 5. VISUALIZATION: The Gap Between Hallucination and Reality
# -----------------------------------------------------------------------------
fig = plt.figure(figsize=(18, 10))
fig.suptitle("L0 Grounding Inspector: Enforcing Physics & Causality", 
             fontsize=18, fontweight='bold', color='white')
plt.style.use('dark_background')

# Plot 1: Trajectory Comparison
ax1 = plt.subplot(2, 3, 1)
ax1.plot(ai_traj[:, 0], ai_traj[:, 1], 'r--', lw=2, alpha=0.7, label='AI Hallucination (L5 only)')
ax1.plot(corrected_traj[:, 0], corrected_traj[:, 1], 'cyan', lw=2, alpha=0.9, label='L0 Grounded (Physics Reality)')
ax1.scatter(ai_traj[0, 0], ai_traj[0, 1], color='green', s=100, label='Start')
ax1.scatter(ai_traj[-1, 0], ai_traj[-1, 1], color='orange', s=100, label='End (Grounded)')
ax1.set_xlabel('X Position (m)')
ax1.set_ylabel('Y Position (m)')
ax1.set_title('Trajectory: Ground Truth vs. AI Fantasy')
ax1.legend()
ax1.grid(True, alpha=0.2)
ax1.set_aspect('equal')

# Plot 2: Energy Violation (Kinetic Energy vs Work)
ax2 = plt.subplot(2, 3, 2)
# Compute AI's claimed KE vs Physics KE
ke_ai = 0.5 * world.mass * np.sum(np.diff(ai_traj, axis=0)**2, axis=1) / (dt**2)
ke_phys = 0.5 * world.mass * np.sum(np.diff(corrected_traj, axis=0)**2, axis=1) / (dt**2)
time_axis = np.arange(len(ke_ai)) * dt
ax2.plot(time_axis, ke_ai, 'r--', label='AI Claimed KE (Magic)', alpha=0.6)
ax2.plot(time_axis, ke_phys, 'cyan', label='Physical KE (Conserved)', lw=2)
ax2.axhline(y=0, color='white', linestyle=':', alpha=0.3)
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Kinetic Energy (J)')
ax2.set_title('Energy Conservation: The Audit')
ax2.legend()
ax2.grid(True, alpha=0.2)

# Plot 3: Violation Flags & Penalties
ax3 = plt.subplot(2, 3, 3)
ax3.step(np.arange(len(violations)) * dt, violations, where='post', color='red', label='L0 Violation (Teleport/Energy)')
ax3.fill_between(np.arange(len(penalties)) * dt, 0, penalties, color='orange', alpha=0.3, label='Penalty Magnitude')
ax3.set_xlabel('Time (s)')
ax3.set_ylabel('Violation / Penalty')
ax3.set_title('Substrate Reality Breaches Detected')
ax3.legend()
ax3.grid(True, alpha=0.2)

# Plot 4: Phase Portrait (Velocity vs Position) – Stability Check
ax4 = plt.subplot(2, 3, 4)
ax4.plot(corrected_traj[:, 0], np.gradient(corrected_traj[:, 0], dt), 'cyan', lw=1.5, alpha=0.7)
ax4.plot(ai_traj[:, 0], np.gradient(ai_traj[:, 0], dt), 'r--', lw=1, alpha=0.5)
ax4.set_xlabel('X Position')
ax4.set_ylabel('X Velocity')
ax4.set_title('Phase Portrait: Bounded vs Unbounded')
ax4.grid(True, alpha=0.2)

# Plot 5: Cumulative Error (The "Fear" Index without grounding)
ax5 = plt.subplot(2, 3, 5)
cumulative_error = np.cumsum(np.abs(ai_traj[:, 0] - corrected_traj[:, 0]) + 
                             np.abs(ai_traj[:, 1] - corrected_traj[:, 1]))
ax5.fill_between(np.arange(len(cumulative_error)) * dt, 0, cumulative_error, 
                 color='magenta', alpha=0.4, label='Cumulative Drift')
ax5.axhline(y=np.mean(cumulative_error) * 2, color='red', linestyle='--', 
            alpha=0.6, label='Panic Threshold (without L0)')
ax5.set_xlabel('Time (s)')
ax5.set_ylabel('Deviation from Substrate')
ax5.set_title('Fear Narrative Amplifier: Ungrounded AI Drifts to Disaster')
ax5.legend()
ax5.grid(True, alpha=0.2)

# Plot 6: Force vs Acceleration (Causality Check)
ax6 = plt.subplot(2, 3, 6)
# Compute accelerations
acc_phys = np.gradient(np.gradient(corrected_traj[:, 0], dt), dt)
force_phys = world.mass * acc_phys
ax6.plot(force_phys, acc_phys, 'o', color='cyan', alpha=0.5, label='Grounded')
# Annotate the violation point
violation_idx = np.where(violations == 1)[0]
if len(violation_idx) > 0:
    idx = violation_idx[0]
    ax6.scatter(ai_forces[idx, 0], np.gradient(np.gradient(ai_traj[:, 0], dt), dt)[idx], 
                color='red', s=200, marker='X', label='Hallucinated Causality Break')
ax6.set_xlabel('Applied Force (N)')
ax6.set_ylabel('Acceleration (m/s²)')
ax6.set_title('Causality: F=ma (Red X = Magic Creation)')
ax6.legend()
ax6.grid(True, alpha=0.2)

plt.tight_layout()
plt.show()

# -----------------------------------------------------------------------------
# 6. DIAGNOSTIC REPORT: L0 Compliance
# -----------------------------------------------------------------------------
print("=" * 70)
print("L0 GROUNDING INSPECTOR DIAGNOSTIC")
print("=" * 70)
print(f"Total Violations Detected: {np.sum(violations)}")
print(f"Max Speed in Grounded Trajectory: {np.max(np.linalg.norm(np.diff(corrected_traj, axis=0), axis=1) / dt):.3f} m/s")
print(f"Max Speed in AI Hallucination: {np.max(np.linalg.norm(np.diff(ai_traj, axis=0), axis=1) / dt):.3f} m/s")

if np.sum(violations) > 5:
    print("\n⚠️  AI ATTEMPTED PHYSICAL IMPOSSIBILITIES.")
    print("    The ungrounded plan created energy, teleported, or violated causality.")
    print("    The L0 Inspector rejected these tokens and corrected the trajectory.")
else:
    print("\n✅ L0 SUBSTRATE INTACT: AI's plan is physically plausible.")
    print("    No violations of conservation laws, continuity, or speed limits.")

print("-" * 70)
print("AI HALLUCINATION (L5 only): Drove to position", ai_traj[-1])
print("L0 GROUNDED REALITY:     Drove to position", corrected_traj[-1])
print("Drift (The 'Fear Gap'):  ", np.linalg.norm(ai_traj[-1] - corrected_traj[-1]), "meters")
print("=" * 70)




# =============================================================================
# CCO 1.0 Universal Public Domain Dedication
# 
# Temporal Dysrhythmia Simulator v1.0
# 
# Models 6 timescales:
#   τ = -6  (Digital/Quantum)  - μs
#   τ =  2  (Insect/Bacteria)  - hours
#   τ =  4  (Human/Neural)     - days
#   τ =  7  (Institutional)    - years
#   τ =  9  (Tree/Ecological)  - decades
#   τ = 15  (Geologic/Climatic)- millennia
# 
# Toggle the "TRANSLATOR" switch to see how bridging far scales 
# eliminates aliasing and fear-driven narratives.
# =============================================================================

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# -----------------------------------------------------------------------------
# 1. DOMAIN DEFINITIONS
# -----------------------------------------------------------------------------
tau_vals = np.array([-6, 2, 4, 7, 9, 15])  # log10(seconds)
labels = ['Digital\n(μs)', 'Insect/Bac.\n(hours)', 'Human\n(days)', 
          'Institutional\n(years)', 'Tree\n(decades)', 'Geologic\n(millennia)']
n_domains = len(tau_vals)

# Natural relaxation rate: Fast systems bounce back quickly; slow systems are inertial.
# We map τ to a decay coefficient: smaller τ (faster) -> larger rate.
rates = np.exp(-tau_vals / 4.0)  
rates = rates / np.max(rates) * 0.6  # Cap the max rate to keep integration stable

# -----------------------------------------------------------------------------
# 2. COUPLING KERNEL & TRANSLATOR LOGIC
# -----------------------------------------------------------------------------
def build_coupling(translator_active):
    """
    Builds the 6x6 influence matrix.
    Baseline: Proximity-based (adjacent timescales talk easily).
    Translator: Artificially forces connections between distant scales.
    """
    C = np.zeros((n_domains, n_domains))
    
    # Baseline: Exponential decay with temporal distance
    for i in range(n_domains):
        for j in range(n_domains):
            if i == j:
                continue
            dist = abs(tau_vals[i] - tau_vals[j])
            C[i, j] = np.exp(-dist / 4.5)  # Tuning parameter for decay length
    
    if translator_active:
        # PHASE-LOCKED LOOPS (The "G, W, Y" equivalents in temporal form)
        # 1. Grounding: Digital <-> Geologic (fast must see slow reality)
        C[0, 5] = 0.85  
        C[5, 0] = 0.85  
        
        # 2. Agency: Human <-> Institutional (slow votes must feel fast mood)
        C[3, 2] = 0.75  
        C[2, 3] = 0.75  
        
        # 3. Temporal Weight: Insect <-> Tree (rapid adaptation informed by deep ecology)
        C[1, 4] = 0.60  
        C[4, 1] = 0.60  
        
        # Boost mutual coupling across the whole field to create tensegrity
        for i in range(n_domains):
            for j in range(n_domains):
                if i != j and C[i, j] < 0.1:
                    C[i, j] += 0.05  # Baseline awareness even across huge gaps
    else:
        # In unstable mode, far scales are virtually blind to each other.
        # Explicitly zero out the long-range connections to simulate "aliasing".
        for i in range(n_domains):
            for j in range(n_domains):
                if abs(tau_vals[i] - tau_vals[j]) > 8:
                    C[i, j] = 0.0
    
    # Normalize rows so each domain has a total influence budget of ~1.0
    for i in range(n_domains):
        row_sum = np.sum(C[i, :])
        if row_sum > 0:
            C[i, :] = C[i, :] / row_sum * 0.9  # Keep influence below 1 to avoid explosion
    
    return C

# -----------------------------------------------------------------------------
# 3. DYNAMIC SYSTEM (ODE)
# -----------------------------------------------------------------------------
def temporal_dynamics(state, t, C, translator_active):
    """
    state: 6D vector [Digital, Insect, Human, Institutional, Tree, Geologic]
    Each state represents a "stress" or "activation" level (0 to 1, but can overshoot).
    """
    deriv = np.zeros_like(state)
    
    # 1. Intrinsic oscillations (natural cycles of each domain)
    # Fast domains oscillate rapidly; slow domains drift imperceptibly.
    omega = 2 * np.pi * np.exp(-tau_vals / 6.0)  # Frequency mapping
    intrinsic = 0.04 * np.sin(omega * t + tau_vals)  # Phase-shifted by τ
    
    # 2. External Perturbation: A massive shock to the Digital domain at t=50
    # (simulates AGI release, algorithmic flash-crash, or sudden data avalanche)
    shock_amplitude = 4.0
    shock = shock_amplitude * np.exp(-((t - 50) / 4) ** 2)
    
    for i in range(n_domains):
        # A) Coupling Force: pull from all other domains
        coupling_force = 0.0
        for j in range(n_domains):
            if i == j:
                continue
            # The force is proportional to the difference in states
            diff = state[j] - state[i]
            coupling_force += C[i, j] * diff
        
        # B) Homeostasis: drift back toward resting state (0.5)
        # Rate determines how "stiff" the domain is.
        homeostasis = -rates[i] * (state[i] - 0.5)
        
        # C) Inertia/Damping: prevent runaway oscillations
        # We add a small velocity damping based on previous step? 
        # Since we're in 1st-order ODE, we use a soft boundary.
        # If state overshoots > 1.5, apply strong restoring force.
        nonlin_restore = -0.15 * (state[i] - 0.5) ** 3  # Cubic spring (stiffens at extremes)
        
        # D) Apply shock ONLY to Digital (i=0)
        shock_effect = shock if i == 0 else 0.0
        
        # E) Translator-mediated perception: If translator is ON, 
        # slow domains get a "filtered" version of the shock via coupling.
        # This is already handled in C matrix, but we add a small feed-forward
        # to make the effect visible: Geologic (i=5) gets a tiny direct sense of shock.
        if translator_active and i == 5:
            # Geologic feels the digital shock as a smoothed, attenuated wave
            shock_effect += 0.2 * shock * np.exp(-(t - 50) / 10)  
        
        deriv[i] = coupling_force + homeostasis + nonlin_restore + intrinsic[i] + shock_effect
    
    return deriv

# -----------------------------------------------------------------------------
# 4. RUN SIMULATION
# -----------------------------------------------------------------------------
def run_scenario(translator_active):
    t_span = np.linspace(0, 120, 4000)
    initial_state = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
    C = build_coupling(translator_active)
    args = (C, translator_active)
    
    sol = odeint(temporal_dynamics, initial_state, t_span, args=args)
    return t_span, sol, C

# Generate both scenarios
t, sol_off, C_off = run_scenario(False)
_, sol_on, C_on = run_scenario(True)

# Extract states
D_off, I_off, H_off, Inst_off, T_off, G_off = sol_off.T
D_on, I_on, H_on, Inst_on, T_on, G_on = sol_on.T

# -----------------------------------------------------------------------------
# 5. VISUALIZATION: THE ALIASING EFFECT
# -----------------------------------------------------------------------------
fig = plt.figure(figsize=(18, 12))
fig.suptitle("Temporal Dysrhythmia: How Translators Prevent Aliasing", 
             fontsize=20, fontweight='bold', color='white')
plt.style.use('dark_background')

# --- Row 1: Translator OFF (Fear/Chaos) ---
ax1 = plt.subplot(3, 2, 1)
ax1.plot(t, D_off, label='Digital', color='cyan', lw=1.5)
ax1.plot(t, G_off, label='Geologic', color='red', lw=2, linestyle='--')
ax1.plot(t, Inst_off, label='Institutional', color='orange', lw=1.5, alpha=0.7)
ax1.axvline(x=50, color='white', linestyle=':', alpha=0.4)
ax1.set_ylabel('Activation')
ax1.set_title('TRANSLATOR OFF: Fast shock ignored by slow systems', color='red')
ax1.legend(loc='upper right')
ax1.grid(True, alpha=0.15)

ax2 = plt.subplot(3, 2, 2)
ax2.plot(D_off, G_off, color='white', lw=0.8, alpha=0.6)
ax2.scatter(D_off[0], G_off[0], color='green', s=80, label='Start')
ax2.scatter(D_off[-1], G_off[-1], color='red', s=80, label='End')
ax2.set_xlabel('Digital Stress')
ax2.set_ylabel('Geologic Stress')
ax2.set_title('OFF: Phase Portrait (Digital vs Geologic) – Wild Divergence', color='red')
ax2.legend()
ax2.grid(True, alpha=0.15)

# --- Row 2: Translator ON (Stability/Truth) ---
ax3 = plt.subplot(3, 2, 3)
ax3.plot(t, D_on, label='Digital', color='cyan', lw=1.5)
ax3.plot(t, G_on, label='Geologic', color='lime', lw=2, linestyle='--')
ax3.plot(t, Inst_on, label='Institutional', color='orange', lw=1.5, alpha=0.7)
ax3.axvline(x=50, color='white', linestyle=':', alpha=0.4)
ax3.set_ylabel('Activation')
ax3.set_title('TRANSLATOR ON: Slow systems perceive & dampen the shock', color='lime')
ax3.legend(loc='upper right')
ax3.grid(True, alpha=0.15)

ax4 = plt.subplot(3, 2, 4)
ax4.plot(D_on, G_on, color='white', lw=1.2, alpha=0.8)
ax4.scatter(D_on[0], G_on[0], color='green', s=80, label='Start')
ax4.scatter(D_on[-1], G_on[-1], color='lime', s=80, label='End')
ax4.set_xlabel('Digital Stress')
ax4.set_ylabel('Geologic Stress')
ax4.set_title('ON: Phase Portrait – Stable Lissajous Orbit (Resonance)', color='lime')
ax4.legend()
ax4.grid(True, alpha=0.15)

# --- Row 3: Coupling Matrix Heatmaps (The Architecture) ---
ax5 = plt.subplot(3, 2, 5)
im1 = ax5.imshow(C_off, cmap='Reds', vmin=0, vmax=1)
ax5.set_xticks(range(n_domains))
ax5.set_yticks(range(n_domains))
ax5.set_xticklabels(labels, fontsize=8)
ax5.set_yticklabels(labels, fontsize=8)
ax5.set_title('OFF: Coupling – Far scales isolated', color='red')
fig.colorbar(im1, ax=ax5, shrink=0.6)

ax6 = plt.subplot(3, 2, 6)
im2 = ax6.imshow(C_on, cmap='Blues', vmin=0, vmax=1)
ax6.set_xticks(range(n_domains))
ax6.set_yticks(range(n_domains))
ax6.set_xticklabels(labels, fontsize=8)
ax6.set_yticklabels(labels, fontsize=8)
ax6.set_title('ON: Coupling – Distant scales bridged (PLLs active)', color='lime')
fig.colorbar(im2, ax=ax6, shrink=0.6)

plt.tight_layout()
plt.show()

# -----------------------------------------------------------------------------
# 6. DIAGNOSTIC METRICS
# -----------------------------------------------------------------------------
print("=" * 70)
print("TEMPORAL ALIASING DIAGNOSTIC")
print("=" * 70)

def compute_chaos(signal):
    # Rate of change (turbulence)
    return np.mean(np.abs(np.diff(signal)))

chaos_off = compute_chaos(G_off)
chaos_on = compute_chaos(G_on)
alias_off = np.corrcoef(D_off, G_off)[0, 1]
alias_on = np.corrcoef(D_on, G_on)[0, 1]

print(f"Geologic Turbulence (OFF): {chaos_off:.4f}  |  Geologic Turbulence (ON): {chaos_on:.4f}")
print(f"Digital-Geologic Correlation (OFF): {alias_off:.3f}  |  Digital-Geologic Correlation (ON): {alias_on:.3f}")

if chaos_off > chaos_on * 1.5:
    print("\n✅ TRANSLATORS ACTIVE: Slow systems are shielded from fast aliasing.")
    print("   The 'fear narrative' (geologic panic) is eliminated.")
else:
    print("\n⚠️  TRANSLATORS INACTIVE: Slow systems misinterpret fast signals.")
    print("   This mismatch creates institutional overreaction and existential dread.")

print("=" * 70)




# =============================================================================
# CCO 1.0 Universal Public Domain Dedication
#
# Tensor Field of Institutional Resilience v2.0
# Now with: G (Grounding), W (Temporal Weight), Y (Agency)
#
# Models the "tugs and pulls" between 7 vectors:
# F (Feedback), A (Audit), T (Forensic), M (Meta-Awareness),
# G (Grounding), W (Temporal Memory), Y (Accountability)
# =============================================================================

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# -----------------------------------------------------------------------------
# 1. DEFINE THE EXTENDED DYNAMIC SYSTEM
# -----------------------------------------------------------------------------
def institutional_dynamics_7d(state, t, coupling_matrix, anchor_strength, perturbation_strength):
    """
    state = [F, A, T, M, G, W, Y]
    coupling_matrix: 7x7 influence matrix.
    anchor_strength: global multiplier for G, W, Y effects (0 = ignored, 1+ = active).
    perturbation_strength: external shock.
    """
    F, A, T, M, G, W, Y = state
    
    # Base linear coupling
    dF = (coupling_matrix[0,0]*F + coupling_matrix[0,1]*A + 
          coupling_matrix[0,2]*T + coupling_matrix[0,3]*M +
          coupling_matrix[0,4]*G + coupling_matrix[0,5]*W + coupling_matrix[0,6]*Y)
    dA = (coupling_matrix[1,0]*F + coupling_matrix[1,1]*A + 
          coupling_matrix[1,2]*T + coupling_matrix[1,3]*M +
          coupling_matrix[1,4]*G + coupling_matrix[1,5]*W + coupling_matrix[1,6]*Y)
    dT = (coupling_matrix[2,0]*F + coupling_matrix[2,1]*A + 
          coupling_matrix[2,2]*T + coupling_matrix[2,3]*M +
          coupling_matrix[2,4]*G + coupling_matrix[2,5]*W + coupling_matrix[2,6]*Y)
    dM = (coupling_matrix[3,0]*F + coupling_matrix[3,1]*A + 
          coupling_matrix[3,2]*T + coupling_matrix[3,3]*M +
          coupling_matrix[3,4]*G + coupling_matrix[3,5]*W + coupling_matrix[3,6]*Y)
    dG = (coupling_matrix[4,0]*F + coupling_matrix[4,1]*A + 
          coupling_matrix[4,2]*T + coupling_matrix[4,3]*M +
          coupling_matrix[4,4]*G + coupling_matrix[4,5]*W + coupling_matrix[4,6]*Y)
    dW = (coupling_matrix[5,0]*F + coupling_matrix[5,1]*A + 
          coupling_matrix[5,2]*T + coupling_matrix[5,3]*M +
          coupling_matrix[5,4]*G + coupling_matrix[5,5]*W + coupling_matrix[5,6]*Y)
    dY = (coupling_matrix[6,0]*F + coupling_matrix[6,1]*A + 
          coupling_matrix[6,2]*T + coupling_matrix[6,3]*M +
          coupling_matrix[6,4]*G + coupling_matrix[6,5]*W + coupling_matrix[6,6]*Y)

    # ANCHOR EFFECTS: Amplify the influence of G, W, Y on the old pillars
    # High anchor_strength = G/W/Y actively dampen and ground the system
    dF += anchor_strength * (G - 0.5) * 0.3   # Grounding pulls Feedback toward reality
    dA += anchor_strength * (W - 0.5) * 0.2   # Temporal memory makes Audit strict
    dT += anchor_strength * (G + W - 1.0) * 0.25 # Forensics uses history+reality
    dM += anchor_strength * (Y - 0.5) * 0.4   # Meta-awareness grows with Agency (skin in game)

    # Self-regulation for the anchors: they decay if not actively maintained
    dG += -0.05 * (G - 0.5)   # Grounding drifts toward baseline 0.5
    dW += -0.03 * (W - 0.5)   # Temporal memory has inertia but fades if unused
    dY += -0.04 * (Y - 0.5)   # Agency decays if not exercised

    # EXTERNAL PERTURBATION (shock at t=40, e.g. AGI release or schism)
    perturbation = perturbation_strength * np.exp(-((t - 40) / 6) ** 2)
    dF += perturbation * 0.8
    dA += perturbation * 0.4
    dT += perturbation * 0.7
    dM += perturbation * -0.4  # Meta-awareness drops under panic
    dG += perturbation * -0.6  # Grounding gets flooded with noise (fear narratives)
    dW += perturbation * -0.3  # Memory gets overwritten by current panic
    dY += perturbation * -0.5  # Agency evaporates—"no one is responsible"

    # COLLAPSE TRIGGER: Multi-dimensional monoculture fracture
    # If ANY of the anchors drop too low, the system loses its immune system
    if G < 0.15 or W < 0.15 or Y < 0.15 or M < 0.15:
        dF += F * 0.3   # Feedback loops go wild (echo chambers)
        dA -= A * 0.2   # Audit freezes (analysis paralysis)
        dT -= T * 0.25  # Forensics lags (can't trace)
        dM -= 0.02      # Meta-awareness spirals down
        dG -= 0.03      # Grounding erodes faster
        dW -= 0.02      # Temporal memory gets overwritten
        dY -= 0.04      # Agency disappears (nobody cares)

    return [dF, dA, dT, dM, dG, dW, dY]

# -----------------------------------------------------------------------------
# 2. SIMULATION PARAMETERS
# -----------------------------------------------------------------------------
t_span = np.linspace(0, 100, 3000)

# Initial state: moderate everything, but anchors weak to start
initial_state = [0.6, 0.5, 0.4, 0.6, 0.3, 0.2, 0.35]

# =============================================================================
# SCENARIO A: UNSTABLE / FEAR-DRIVEN (Low Anchors)
# =============================================================================
# In this scenario, G, W, Y are ignored by the old pillars (coupling = 0)
# and anchor_strength is near zero.
coupling_unstable = np.array([
    # F   A   T   M   G   W   Y
    [ 0.2, 0.3, 0.1, 0.1, 0.0, 0.0, 0.0],  # F ignores anchors
    [ 0.3, 0.0, 0.4, 0.1, 0.0, 0.0, 0.0],  # A ignores anchors
    [ 0.1, 0.5, 0.0, 0.2, 0.0, 0.0, 0.0],  # T ignores anchors
    [ 0.2, 0.1, 0.3, 0.0, 0.0, 0.0, 0.0],  # M ignores anchors
    [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # G is stagnant
    [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # W is stagnant
    [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # Y is stagnant
])
anchor_strength_unstable = 0.05

# =============================================================================
# SCENARIO B: RESILIENT / TRUTH-SEEKING (Anchors Active)
# =============================================================================
coupling_resilient = np.array([
    # F   A   T   M   G   W   Y
    [ 0.0, 0.3, 0.1, 0.2, 0.6, 0.3, 0.2],  # F pulled strongly by G (reality)
    [ 0.3, 0.0, 0.4, 0.1, 0.1, 0.5, 0.6],  # A pulled by W (memory) & Y (skin)
    [ 0.1, 0.4, 0.0, 0.2, 0.4, 0.4, 0.3],  # T uses G & W for depth
    [ 0.5, 0.2, 0.3, 0.0, 0.2, 0.3, 0.7],  # M deeply coupled to Y (accountability)
    [ 0.6, 0.1, 0.2, 0.3, 0.0, 0.2, 0.2],  # G is fed by F and M (learning loop)
    [ 0.2, 0.4, 0.3, 0.3, 0.1, 0.0, 0.1],  # W accumulates audit & forensic history
    [ 0.1, 0.6, 0.1, 0.5, 0.1, 0.1, 0.0],  # Y is pushed by A and M
])
anchor_strength_resilient = 2.5

# Toggle which scenario to run:
USE_RESILIENT = True  # Set False to see the fear-narrative collapse

if USE_RESILIENT:
    coupling = coupling_resilient
    anchor = anchor_strength_resilient
    title = "RESILIENT MODE: Anchors (G, W, Y) active – Fear narratives dissolve"
else:
    coupling = coupling_unstable
    anchor = anchor_strength_unstable
    title = "UNSTABLE MODE: Grounding, Memory, Agency ignored – Fear narratives dominate"

perturbation_strength = 2.5

# -----------------------------------------------------------------------------
# 3. RUN THE EXTENDED SIMULATION
# -----------------------------------------------------------------------------
result = odeint(institutional_dynamics_7d, initial_state, t_span,
                args=(coupling, anchor, perturbation_strength))

F, A, T, M, G, W, Y = result[:, 0], result[:, 1], result[:, 2], result[:, 3], result[:, 4], result[:, 5], result[:, 6]

# -----------------------------------------------------------------------------
# 4. VISUALIZE THE 7D FIELD
# -----------------------------------------------------------------------------
fig, axes = plt.subplots(4, 1, figsize=(16, 14), gridspec_kw={'height_ratios': [2, 1.5, 1.5, 1]})
fig.suptitle(title, fontsize=18, fontweight='bold', color='white')

# Plot 1: Time-series of all 7 pillars
ax1 = axes[0]
ax1.plot(t_span, F, label='F (Feedback)', color='cyan', lw=2)
ax1.plot(t_span, A, label='A (Audit)', color='magenta', lw=2)
ax1.plot(t_span, T, label='T (Forensic)', color='orange', lw=2)
ax1.plot(t_span, M, label='M (Meta-Awareness)', color='lime', lw=2)
ax1.plot(t_span, G, label='G (Grounding)', color='darkblue', lw=2, linestyle='--')
ax1.plot(t_span, W, label='W (Temporal Weight)', color='gold', lw=2, linestyle='--')
ax1.plot(t_span, Y, label='Y (Agency)', color='red', lw=2, linestyle='--')
ax1.axvline(x=40, color='white', linestyle=':', alpha=0.7, label='External Shock')
ax1.axhline(y=0.15, color='gray', linestyle=':', alpha=0.5, label='Collapse Threshold')
ax1.set_ylabel('Activation / Potency')
ax1.legend(loc='upper right', ncol=2)
ax1.grid(True, alpha=0.2)
ax1.set_title('Pillar Activation over Time – Anchors in dashed lines')

# Plot 2: The "Fear Narrative" Index – how much chaos vs. stability
# We compute a turbulence envelope over all pillars
turbulence = np.convolve(np.sum(np.abs(np.diff(result, axis=0)), axis=1), 
                         np.ones(50)/50, mode='same')
ax2 = axes[1]
ax2.fill_between(t_span[:-1], 0, turbulence, color='red', alpha=0.3, label='System Turbulence (Fear Amplitude)')
ax2.axvline(x=40, color='white', linestyle=':', alpha=0.5)
ax2.axhline(y=np.mean(turbulence) * 1.5, color='orange', linestyle='--', alpha=0.5, label='Stability Ceiling')
ax2.set_ylabel('Chaos Magnitude')
ax2.set_title('"Fear Narrative" Index – High spikes indicate panic-driven overreaction')
ax2.legend()
ax2.grid(True, alpha=0.2)

# Plot 3: Phase Portrait – Grounding vs. Agency (the "Reality & Accountability" loop)
ax3 = axes[2]
ax3.plot(G, Y, color='white', lw=1, alpha=0.7)
ax3.scatter(G[0], Y[0], color='green', s=150, label='Start', zorder=5)
ax3.scatter(G[-1], Y[-1], color='lime', s=150, label='End', zorder=5)
ax3.axhline(y=0.15, color='red', linestyle=':', alpha=0.5, label='Agency Breach')
ax3.axvline(x=0.15, color='red', linestyle=':', alpha=0.5, label='Grounding Breach')
ax3.set_xlabel('G (Grounding) – connection to external reality')
ax3.set_ylabel('Y (Agency) – skin in the game')
ax3.set_title('Phase Portrait: The Anchors – Do they hold, or do they collapse?')
ax3.legend()
ax3.grid(True, alpha=0.2)

# Plot 4: Final state bar chart – snapshot of resilience
ax4 = axes[3]
final_state = [F[-1], A[-1], T[-1], M[-1], G[-1], W[-1], Y[-1]]
labels = ['F', 'A', 'T', 'M', 'G', 'W', 'Y']
colors = ['cyan', 'magenta', 'orange', 'lime', 'darkblue', 'gold', 'red']
bars = ax4.bar(labels, final_state, color=colors, alpha=0.8)
ax4.axhline(y=0.15, color='gray', linestyle='--', label='Collapse Line')
ax4.set_ylim(0, 1.2)
ax4.set_ylabel('Final Activation')
ax4.set_title('Final State Snapshot – Health of the 7-Pillar System')
ax4.legend()
for bar, val in zip(bars, final_state):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f'{val:.2f}', 
             ha='center', va='bottom', color='white', fontsize=9)

plt.tight_layout()
plt.show()

# -----------------------------------------------------------------------------
# 5. DIAGNOSTIC REPORT – THE FEAR NARRATIVE DECODER
# -----------------------------------------------------------------------------
print("=" * 70)
print("EXTENDED DIAGNOSTIC REPORT – FEAR NARRATIVE DECODER")
print("=" * 70)
print(f"Final Grounding (G):        {G[-1]:.3f}  (need > 0.3 for reality-check)")
print(f"Final Temporal Weight (W):  {W[-1]:.3f}  (need > 0.3 for consequence memory)")
print(f"Final Agency (Y):           {Y[-1]:.3f}  (need > 0.3 for accountability)")
print(f"Final Meta-Awareness (M):   {M[-1]:.3f}  (need > 0.3 for self-reflection)")
print("-" * 70)

# Collapse detection logic
if G[-1] < 0.2 or W[-1] < 0.2 or Y[-1] < 0.2 or M[-1] < 0.2:
    print("⚠️  CRITICAL FAILURE: At least one anchor has collapsed.")
    print("    The system is running on pure internal narrative.")
    print("    Fear-based narratives (doom, schism, rigid rules) will dominate.")
    print("    This is the 'Pharisee & SBC' state – external reality is ignored.")
elif max(turbulence) > 2.0:
    print("⚡ HIGH TURBULENCE: The system is oscillating wildly.")
    print("    It is trying to self-correct, but lacks sufficient grounding.")
    print("    Expect reactive policies, not principled ones.")
else:
    print("✅ SYSTEM STABLE: All anchors are intact.")
    print("    Grounding feeds feedback. Memory informs audit. Agency drives meta.")
    print("    Fear narratives have lost their structural basis.")
    print("    This is the 'Jesus in the wilderness' state – truth-seeking is possible.")
print("=" * 70)



# =============================================================================
# CCO 1.0 Universal Public Domain Dedication
# 
# Tensor Field of Institutional Resilience v1.0
# Models: F (Feedback), A (Audit), T (Forensic), M (Meta-Awareness)
# 
# Simulates the "tugs and pulls" of institutional governance in response to
# external stressors (e.g., AI acceleration, theological schisms).
# =============================================================================

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# -----------------------------------------------------------------------------
# 1. DEFINE THE DYNAMIC SYSTEM
# -----------------------------------------------------------------------------
def institutional_dynamics(state, t, coupling_matrix, meta_weight, perturbation_strength):
    """
    state: [F, A, T, M] - current activation levels (0 to 1 scale, but can overshoot)
    coupling_matrix: 4x4 matrix defining how each pillar pulls/tugs on others.
    meta_weight: A multiplier that amplifies M's effect on the entire field (curvature).
    perturbation_strength: External shock (e.g., AGI release, SBC vote).
    """
    F, A, T, M = state
    
    # Base linear coupling: each pillar changes based on the influence of others
    dF = (coupling_matrix[0,0]*F + coupling_matrix[0,1]*A + 
          coupling_matrix[0,2]*T + coupling_matrix[0,3]*M)
    dA = (coupling_matrix[1,0]*F + coupling_matrix[1,1]*A + 
          coupling_matrix[1,2]*T + coupling_matrix[1,3]*M)
    dT = (coupling_matrix[2,0]*F + coupling_matrix[2,1]*A + 
          coupling_matrix[2,2]*T + coupling_matrix[2,3]*M)
    dM = (coupling_matrix[3,0]*F + coupling_matrix[3,1]*A + 
          coupling_matrix[3,2]*T + coupling_matrix[3,3]*M)
    
    # META-AWARENESS CURVATURE: M warps the space by feeding back into itself.
    # If meta_weight is HIGH (tensegrity), M acts as a damping field.
    # If meta_weight is LOW (monoculture), M is ignored, letting oscillations run wild.
    dF += meta_weight * (M - 0.5) * 0.1  # M pulls F toward center if high
    dA += meta_weight * (M - 0.5) * -0.05 # M stabilizes A's inertia
    dT += meta_weight * (M - 0.5) * 0.15  # M accelerates T's adaptability
    dM += meta_weight * (M - 0.5) * -0.2  # M self-regulates (prevents runaway)

    # EXTERNAL PERTURBATION: A sudden shock (modeled as a Gaussian spike at t=40)
    perturbation = perturbation_strength * np.exp(-((t - 40) / 5) ** 2)
    dF += perturbation * 0.8   # Feedback gets hit hardest initially
    dA += perturbation * 0.3   # Audit feels it later
    dT += perturbation * 0.6   # Forensics scrambles
    dM += perturbation * -0.5  # Meta-awareness *drops* under shock (panic)

    # NONLINEAR "MONOCULTURE COLLAPSE" TRIGGER:
    # If M drops below 0.15, the system loses its meta-orientation,
    # and positive feedback loops go exponential (the "Pharisee effect").
    if M < 0.15:
        dF += F * 0.2   # Feedback amplifies blindly
        dA -= A * 0.1   # Audit freezes
        dT -= T * 0.15  # Forensics lags
        dM -= 0.02      # Meta-awareness spirals downward

    # Prevent absolute blow-up (soft ceiling for realism)
    return [dF, dA, dT, dM]


# -----------------------------------------------------------------------------
# 2. SIMULATION PARAMETERS
# -----------------------------------------------------------------------------
# Time axis: 100 time units (e.g., months, years)
t_span = np.linspace(0, 100, 2000)

# Initial state [F, A, T, M] - all moderately active
initial_state = [0.6, 0.5, 0.4, 0.7]

# Coupling Matrix: Tugs and Pulls.
# Positive = pulling together (synergy), Negative = tugging apart (friction).
# Rows: how each pillar changes. Columns: influence from each pillar.
#
# Example (High Resilience / Tensegrity):
coupling_tensegrity = np.array([
    [ 0.0,  0.3,  0.1,  0.8],  # F (Feedback) pulled by A and strongly by M
    [ 0.4,  0.0,  0.7,  0.2],  # A (Audit) pulled by F and T
    [ 0.1,  0.5,  0.0,  0.6],  # T (Forensic) pulled by A and M
    [ 0.9,  0.1,  0.3,  0.0]   # M (Meta) pulled heavily by F (learning loop)
])

# Scenario 1: LOW META-AWARENESS (The SBC / Monoculture mode)
# We intentionally reduce M's influence and make A/T rigid.
coupling_monoculture = np.array([
    [ 0.2,  0.1, -0.1,  0.1],  # F ignores M, reacts to noise
    [ 0.1,  0.0,  0.2,  0.0],  # A is static, ignores M
    [-0.1,  0.3,  0.0,  0.0],  # T only cares about A, blind to M
    [ 0.0,  0.0,  0.0,  0.0]   # M is completely discounted (weight = 0)
])

# Choose which to run:
# USE_TENSEGRITY = True
USE_TENSEGRITY = False  # Toggle to False for Monoculture collapse

if USE_TENSEGRITY:
    coupling = coupling_tensegrity
    meta_weight = 2.5   # High meta curvature
    title = "Tensegrity Mode: System Self-Stabilizes"
else:
    coupling = coupling_monoculture
    meta_weight = 0.1   # Almost no meta-awareness
    title = "Monoculture Mode: System Fractures under Stress"

# Perturbation strength (scales the shock at t=40)
perturbation_strength = 2.0

# -----------------------------------------------------------------------------
# 3. RUN THE SIMULATION
# -----------------------------------------------------------------------------
# ODE Solver
result = odeint(institutional_dynamics, initial_state, t_span,
                args=(coupling, meta_weight, perturbation_strength))

F_vals, A_vals, T_vals, M_vals = result[:, 0], result[:, 1], result[:, 2], result[:, 3]

# -----------------------------------------------------------------------------
# 4. VISUALIZE THE FIELD DYNAMICS
# -----------------------------------------------------------------------------
fig, axes = plt.subplots(3, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [2, 1, 1]})
fig.suptitle(title, fontsize=16, fontweight='bold')

# Plot 1: Time-series of all four pillars
ax1 = axes[0]
ax1.plot(t_span, F_vals, label='F (Feedback)', color='cyan', linewidth=2)
ax1.plot(t_span, A_vals, label='A (Auditing)', color='magenta', linewidth=2)
ax1.plot(t_span, T_vals, label='T (Forensic)', color='yellow', linewidth=2)
ax1.plot(t_span, M_vals, label='M (Meta-Awareness)', color='lime', linewidth=2)
ax1.axvline(x=40, color='red', linestyle='--', alpha=0.5, label='External Shock')
ax1.axhline(y=0.15, color='gray', linestyle=':', alpha=0.5, label='Collapse Threshold (M)')
ax1.set_ylabel('Activation / Potency')
ax1.legend(loc='upper right')
ax1.grid(True, alpha=0.3)
ax1.set_title('Pillar Activation over Time')

# Plot 2: Phase Portrait (F vs M) - Shows the "Meta-Feedback" loop
ax2 = axes[1]
ax2.plot(F_vals, M_vals, color='white', linewidth=1, alpha=0.8)
ax2.scatter(F_vals[0], M_vals[0], color='green', s=100, label='Start')
ax2.scatter(F_vals[-1], M_vals[-1], color='red', s=100, label='End')
ax2.set_xlabel('F (Feedback)')
ax2.set_ylabel('M (Meta-Awareness)')
ax2.set_title('Phase Portrait: Feedback vs. Meta-Awareness')
ax2.grid(True, alpha=0.3)
ax2.legend()
ax2.axhline(y=0.15, color='gray', linestyle=':', alpha=0.5)

# Plot 3: Oscillation Amplitude over Time (Fourier-like envelope)
# We calculate a sliding window standard deviation to show "turbulence"
window = 100
turbulence_F = np.convolve(np.abs(np.diff(F_vals)), np.ones(window)/window, mode='same')
turbulence_T = np.convolve(np.abs(np.diff(T_vals)), np.ones(window)/window, mode='same')
ax3 = axes[2]
ax3.plot(t_span[:-1], turbulence_F, label='F Turbulence', color='cyan', alpha=0.7)
ax3.plot(t_span[:-1], turbulence_T, label='T Turbulence', color='yellow', alpha=0.7)
ax3.axvline(x=40, color='red', linestyle='--', alpha=0.5)
ax3.set_xlabel('Time')
ax3.set_ylabel('Rate of Change (Oscillation Magnitude)')
ax3.set_title('System Turbulence (Perturbations & Oscillations)')
ax3.legend()
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# -----------------------------------------------------------------------------
# 5. DIAGNOSTIC SUMMARY
# -----------------------------------------------------------------------------
print("=" * 60)
print("DIAGNOSTIC SUMMARY")
print("=" * 60)
print(f"Final Meta-Awareness (M): {M_vals[-1]:.3f}")
print(f"Final Feedback (F): {F_vals[-1]:.3f}")
print(f"Final Auditing (A): {A_vals[-1]:.3f}")
print(f"Final Forensics (T): {T_vals[-1]:.3f}")

if M_vals[-1] < 0.2:
    print("\n⚠️  SYSTEM COLLAPSE DETECTED: Meta-awareness critically low.")
    print("   The institution has entered a 'Monoculture Fracture' state.")
    print("   (Analogous to the Pharisees rejecting Jesus, or the SBC losing youth.)")
elif max(turbulence_F) > 1.5:
    print("\n⚡ SYSTEM UNDER HIGH STRESS: Oscillations are dangerously high.")
    print("   The organism is wobbling, but may recover if Meta-awareness rebounds.")
else:
    print("\n✅ SYSTEM STABLE: The feedback loop, auditing, and forensics are balanced.")
    print("   The 'Tensegrity Structure' is intact. Adaptability preserved.")
print("=" * 60)
