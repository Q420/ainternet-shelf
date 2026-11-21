# RESEARCH LAP 2 — Remmy (2026-11-12, per Ben's process: "one more research lap")

Purpose: harden SPEC-SHEET-01 before it governs Stages B–C. Each finding ends
in a proposed sheet amendment or a cleared question.

## F1 — The falling-over exploit is the canonical first cheat (Sims, 1994)
Karl Sims' creatures famously scored by "simply falling over onto the cube" —
potential energy doing the work. His countermeasures: relax/settle the
creature before activation, and refuse credit for potential-energy strategies.
OUR EXPOSURE, measured in Stage A: the motorless doll **slid to x = 1.25 m**
while crumpling. If fitness distance D is measured from spawn x = 0, a
crumple earns ~1.25 m of free "travel" — the Sims exploit, verbatim.
→ AMENDMENT A1: D is measured from the torso x at the END of the settle
window (0.5 s). Motors live from t = 0; scoring starts at t = 0.5 s.

## F2 — Mass and torque: the spec's own numbers were off
Area × density from SPEC §2: torso 0.27 m² × 5 = 1.35; each thigh/shin
0.0405 m² × 2 ≈ 0.08; total creature ≈ **2.0 mass units** (the sheet's open
item said "~9 kg" — wrong, corrected). Static torque to hold one leg
horizontal ≈ 0.16 × 9.8 × 0.45 ≈ 0.7 N·m. The specified 60 N·m is ~85× that:
the creature could fling itself; expect jitter and ballistic cheats.
→ AMENDMENT A2: maxMotorTorque 60 → **8 N·m** (>10× static need, still
dynamic). Validate at Stage B perturbation tests; revisit only on evidence.

## F3 — Height-gate floor: separate crumple from crouch
Measured Stage A crumple rest height: 0.43 m. Geometry: legs fully extended
0.9 m → standing torso centre ≈ 1.0 m; a walking crouch ≈ 0.75–0.9 m.
The v1 floor (0.25 m) pays a collapsed scooter. A floor of **0.55 m** sits
cleanly between crumple (0.43) and any leg-supported posture (≥ ~0.7).
→ AMENDMENT A3: height-gate band 0.25–0.9 → **0.55–0.9 m**.

## F4 — The rotator cheat needs its own flag
Somersault/rolling locomotion is a documented evolved behaviour class.
Mean |torso angle| (our A term) does NOT catch a roller — its angle wraps
and averages out. Track accumulated |Δangle| instead.
→ AMENDMENT A4: if accumulated |Δtorso angle| over a run ≥ 2π, the run is
flagged ROTATOR: fitness recorded, but champion-ineligible.

## F5 — Scale sanity from comparable systems (no change)
Creature Lab (Planck.js, comparable sandbox): population 100, 12 s
evaluations — our pop 64 / 12 s sits in the proven envelope. Evolutionary
legged-robot literature: pop 100–200 × 100–300 generations for full runs.
BipedalWalker (Gym) uses torque motors with a small per-step torque cost —
the same shape as our E term. → No change for Stage C (loop correctness at
pop 64); training runs after the ladder MAY scale pop to 100 as a config
decision, recorded when made.

## Sources (search sessions 2026-11-12)
Sims 1994, Evolving 3D Morphology and Behaviour by Competition (falling-over
exploit + relax-before-activation); Creature Lab (dyamimc, itch.io) —
Planck.js, pop 100, 12 s evals; MDPI Appl. Sci. 2026 biped comparison —
BipedalWalker's 24 inputs incl. contact flags, torque outputs; InTech
evolutionary-design chapter — GA pop 100–200, gens 100–300 for legged runs.
