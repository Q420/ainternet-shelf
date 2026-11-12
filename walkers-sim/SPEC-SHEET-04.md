# SPEC-SHEET-04 — Walkers Sim v1: QUADRUPED (v4, post Vane examination round 2)

Status: v4 — SPEC-SHEET-03 amended by Vane's second examination
(pb-mwdkbe6g, 2026-11-12): three BLOCKING + two ADVISORY findings, all
verified and accepted (one with a refinement, §6 D). Stage B engineering
proceeds against this version; evolutionary fitness QUALIFICATION is held
until the §9 adversarial-creature test passes. Governing process:
PROCESS-TREE-01. Grounding: research-remmy.md, research-lap2-remmy.md,
JOINT-PLAN-01.md, RESULTS.md.

## 1. Flavour and hard constraints (Ben's rulings)
- The walkers are CREATED FROM CSS: the creature on screen is DOM divs
  styled and transformed by CSS. Physics (Planck.js) computes; CSS is the
  body. No canvas, no sprites, no SVG rigs.
- Quadruped first. Biped is the second morphology (later spec).
- Watch/work: the same sim runs watched (browser, real time) and
  unrendered (worker, fast). One physics definition, two gears.

## 2. Body plan — quadruped v1 (planar 2D)
- Torso: box 0.9 m × 0.3 m, density 5. (Mass ≈ 1.35 units.)
- Legs: 4 (front pair, back pair). Each leg: thigh 0.45 m, shin 0.45 m,
  link thickness 0.09 m, density 2. Total creature mass ≈ 2.0 units.
- Joints: 8 revolute motors (hip + knee per leg). Hip range ±0.9 rad.
  Knee range −1.6…0 rad (backward-bending knee only).
- Motor max torque **8 N·m** (amendment A2; first-principles: static
  leg-hold ≈ 0.7 N·m). Motor speed cap 6 rad/s.
- Feet: circle r 0.06 m at each shin end, friction 0.9, contact-sensed.
- Self-collision: all creature fixtures share one negative collision group
  (parts never collide with each other). DOCUMENTED v1 LIMITATION (§11):
  non-adjacent limbs and the torso can interpenetrate; named evolutionary
  loophole, accepted for v1, revisited at morphology v2.

## 3. World and evaluation protocol
- Engine: Planck.js (pinned v1.5.1). Gravity −9.8 m/s². Fixed step 1/60 s,
  solver iterations 8 velocity / 3 position.
- Ground: static, friction 1.0, restitution 0. Flat in v1.
- SETTLE PROCEDURE (B1 — replaces the v2 "settle window"):
  1. Spawn in a deterministic initial configuration (the Stage A pose).
  2. Motors DISABLED. The physics world is freshly created for every
     evaluation (no state carries over). Simulate until the stability
     condition holds for 10 consecutive steps: torso |linear velocity|
     < 0.05 m/s AND |angular velocity| < 0.1 rad/s AND every joint
     |angular velocity| < 0.2 rad/s AND torso displacement over the
     10-step window < 0.005 m AND foot penetration ≤ 0.005 m. Settle
     timeout 2 s; on timeout the evaluation is classified FAILED-INIT
     (score 0, flagged, recorded) — never silently re-spawned or scored.
  3. At stability: record the scoring origin (torso centre x, y), the full
     pose and all velocities in the evaluation record. Reset the unwrapped
     torso angle (§8b) to zero.
  4. Motors enable and scoring begins in the same step.
  There is no unscored motor activity anywhere in an evaluation.
- Evaluation length: 12 s of scored time, early-terminated on torso-ground
  contact after a 0.5 s post-settle grace period, or on NaN (score 0,
  flagged).

## 4. Brain (fixed topology, no NEAT in v1)
- Inputs (**27**, B5 — torso height included): torso angle, angular
  velocity, linear velocity x, linear velocity y, **torso height above
  ground** (5); 8 joint angles; 8 joint angular velocities; 4 foot-contact
  booleans; clock sin, clock cos (period 1 s).
- Normalization (B5): every channel is scaled and clipped to [−1, 1]
  before the network: angle /π; angular velocity /5; linear velocities /5;
  height /1.5; joint angle / its range width; joint speed /6; contacts
  are 0/1 (used as-is); clock sin/cos already in [−1, 1].
- Hidden: 16 tanh. Outputs: 8, each = desired motor speed in [−6, 6] rad/s.
- Genome: **584** parameters, flat array, order: W1 row-major, b1, W2
  row-major, b2. Init: uniform [−1, 1].

## 5. Evolution (GA, fixed net)
- Population 64. Generations: open-ended (operator stops).
- Elitism: top 4 copied unchanged.
- Parents: tournament of 3 drawn from the top 50%.
- Crossover: applied to 70% of offspring (per-offspring probability);
  when applied, uniform per-gene (50/50 parent pick per gene).
- Mutation (per gene, independent rolls): 10% add Gaussian noise σ 0.3;
  separately 2% re-roll to uniform [−1, 1].
- DIVERSITY INJECTION (restored, advisory A5): if median fitness stalls
  (no improvement) for 50 generations, inject 10 fresh random genomes,
  replacing the 10 worst non-elite; injections recorded in the
  generation statistics.
- REPRODUCIBILITY (advisory A6): PRNG is mulberry32; the run seed is part
  of the experiment config and recorded with every result. Training seed
  default 1. Validation seeds are the fixed set {11, 23, 37}, never used
  for selection. Every individual in a generation is evaluated under
  identical conditions (same config, same protocol; only the genome
  differs).
- CHAMPION QUALIFICATION (round-2 advisory): a champion must be
  flag-free (no ROTATOR, HOPPER, FAILED-INIT, or UNRELIABLE) on ALL
  THREE validation seeds {11, 23, 37}; median, minimum and maximum
  validation fitness and the per-seed flags are reported; qualification
  additionally requires minimum ≥ 0.5 × median. Validation results
  never feed selection, mutation, or training.

## 6. Fitness (B6 — every term formally defined)
Sampling: physics-step samples of the scored interval only.
ELIGIBILITY (one definition, used by D, T, A, E alike): a sample is
eligible when torso-centre height ≥ 0.55 m AND |torso pitch| ≤ 0.6 rad.
Height means torso-centre world Y in metres (§3 origin is recorded
separately). There is NO upper height ceiling in v3: the v2 0.9 m ceiling
could punish correct standing (measured standing ≈ 1.0 m); jumping is
controlled by the HOPPER flag (§8b), not by the gate.
- D = signed forward progress INTEGRATED OVER ELIGIBLE INTERVALS:
  D = Σ I_i · (x_{i+1} − x_i) over consecutive sample pairs, where the
  interval indicator I_i = 1 only when BOTH endpoint samples are eligible.
  Displacement gained during ineligible intervals earns nothing, and
  back-and-forth oscillation inside eligible intervals nets out (signed
  increments — Vane proposed max(0, Δx); signed is adopted instead
  because max(0, ·) would pay forward halves of a vibration cycle,
  contradicting the §9 vibrating-in-place defence).
- T = eligible time: count of eligible samples × step (seconds).
- A = mean |torso pitch| over eligible samples (radians).
- E = mean mechanical power over the ENTIRE powered evaluation (every
  sample from motor-enable to termination, eligible or not — energy
  spent flailing outside the gate is still charged), normalized:
  per sample, P = Σ over 8 joints of |applied torque × joint relative
  angular velocity| (watts); E = mean(P) / (m · g · 1 m/s) with m the
  creature mass — dimensionless.
- F = 2·D + 0.3·T − 2·A − 0.05·E.
- Components are ALWAYS reported separately alongside F. A separate
  validation score is computed on the validation seed set and never
  feeds selection.

## 7. Rendering (the CSS law)
- One div per body part (9 divs: torso, 4 thighs, 4 shins; feet are
  ::after circles on the shin divs), flat siblings, positioned only via
  CSS transforms computed from physics state each frame. A HUD shows
  generation, best fitness, and the fitness components.
- Supplementary Stage A evidence owed (advisory A2): angle parity
  (rendered vs physics rotation), per-step ground-contact telemetry, and
  a recorded maximum body–ground penetration. Stage A's PASS stands,
  narrowed to what its existing checks established (centre parity,
  settle behaviour, no observed tunnelling at 400 ms sampling).

## 8. Champions
- Export format (single line of text):
  WALKER1|<config id>|<base64 genome>|<fitness summary>
- The hall of fame records the best champion of every experiment,
  including the terrible early ones.

## 8b. Behaviour flags (champion eligibility)
- ROTATOR (A4 revised, B3): track the torso's UNWRAPPED angle from the
  post-settle orientation using wrap-aware increments
  (delta = atan2(sin Δθ, cos Δθ), accumulated). If the maximum excursion
  of the unwrapped angle from zero reaches ≥ 2π, the run is a genuine
  full rotation: fitness recorded, champion-INELIGIBLE. Total angular
  variation (Σ|Δθ|) is recorded as telemetry (flailing indicator) and
  never gates. Acceptance tests required: (i) sinusoidal torso rocking
  0.3 rad at 1 Hz for 12 s does NOT flag; (ii) one full somersault DOES
  flag; (iii) a roll that rights itself still flags (excursion reached
  2π mid-roll). ALIASING GUARD (round-2 advisory): per-step wrapped
  increments cannot distinguish +10° from +370°; the unwrapped angle is
  therefore cross-checked against the time-integral of torso angular
  velocity (Σ ω·dt). If the two disagree by more than π over a run, the
  angle measurement is flagged UNRELIABLE and the run cannot qualify.
  A fourth acceptance test is required: a deliberately spun creature
  (sustained |ω| above 10 rad/s) must be measured consistently by both
  methods.
- HOPPER: support means at least one foot in sensed ground contact.
  Three metrics are recorded for every run: total unsupported fraction,
  longest continuous unsupported interval, and the number of
  unsupported→supported transitions. A run is flagged HOPPER when the
  unsupported fraction exceeds 50% OR the longest continuous unsupported
  interval exceeds 1.0 s. Flagged runs (HOPPER or ROTATOR) are excluded
  from champion selection AND from parent selection; their raw fitness
  and telemetry are retained for research only.

## 9. Anti-cheat test categories (advisory A4)
Forward falling → settle procedure (§3) + sustained eligible progress.
Rolling → ROTATOR (§8b). Bouncing → airtime duty (§8b HOPPER).
Knee-walking → height + pitch eligibility (§6). Reverse walking →
signed D (§6). Vibrating in place → net progress D (no credit for
accumulated motion). Motor flinging → torque cap (§2) + E accounting
(§6). Solver exploitation → champion solver-sensitivity test (§10).
Lucky initialization → validation seed set (§5).

## 10. Champion credibility (advisory A3)
Before a champion is declared physically credible, it is re-evaluated at
1/120 s timestep (equivalent duration, solver iterations scaled). A gait
whose fitness collapses under the finer step is investigated as a
possible numerical exploit, and the discrepancy recorded either way.

## 11. Advisory dispositions (Vane's examination, 2026-11-12)
- Self-collision (his A1): documented v1 limitation, §2. Revisit at
  morphology v2 with selective filtering.
- Stage A evidence (his A2): accepted; supplementary checks owed, §7.
- Solver sensitivity (his A3): accepted as §10.
- Anti-cheat catalogue (his A4): accepted as §9.
- Diversity injection (his A5): restored, §5.
- GA reproducibility (his A6): specified, §5.
- Examiner's amendment verdicts: A1 incomplete → resolved by §3;
  A2 provisionally accepted → retained, Stage B torque-measurement test
  added to the build sheet; A3 incomplete → resolved by §6; A4 rejected
  as written → replaced by §8b.

## 12. Open items
- Measured standing height of a motor-held creature (Stage B evidence) —
  if it contradicts §6's eligibility floor, amend again on evidence.
- Biped morphology: later spec, after the quadruped walks.
