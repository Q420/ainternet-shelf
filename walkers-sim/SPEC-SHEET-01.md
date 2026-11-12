# SPEC-SHEET-01 — Walkers Sim v1: QUADRUPED

Status: DRAFT for Vane adversarial review, then Ben approval. No build authorised
by this sheet alone. Grounding: research-remmy.md, JOINT-PLAN-01.md (pop and
fitness as resolved there), Ben's rulings: quadrupeds first; walkers rendered
from CSS; strict process (PROCESS-TREE-01).

## 1. The thing
A 2D physics quadruped that learns to walk by evolution. A population of
fixed-topology neural nets controls 8 joint motors; a genetic algorithm breeds
the ones that travel furthest without falling. The creature on screen is pure
CSS: flat sibling divs positioned by transform, driven by a Planck.js world.

## 2. Morphology (EXP-CONFIG v1 constants)
- Torso: one rigid box, 0.9 m × 0.3 m, density 5.
- Legs: 4 (front pair, back pair), each = thigh (0.45 m) + shin (0.45 m),
  attached at torso corners; density 2.
- Joints: 8 revolute motors (4 hip, 4 knee).
  - Hip range ±0.9 rad. Knee range −1.6…0 rad (backward-bending, quadruped-style).
  - Motor max torque 60 N·m; motor speed cap 6 rad/s.
- Feet: shin end = circle fixture r 0.06 m, friction 0.9 (foot contacts are sensed).

## 3. Physics
- Engine: Planck.js (Box2D). Gravity −9.8 m/s². Fixed step 1/60 s,
  solver iterations 8 velocity / 3 position.
- Ground: static, friction 1.0, restitution 0. Flat in v1 (terrain is a later spec).
- Evaluation length: 12 s per individual, early-terminated on torso-ground
  contact after a 0.5 s grace period, or on NaN (score 0, flagged).

## 4. Brain (fixed topology, no NEAT in v1)
- Inputs (26): torso angle, angular velocity, linear velocity x/y,
  8 joint angles, 8 joint speeds, 4 foot-contact booleans, clock sin/cos.
- Hidden: 16 tanh. Outputs: 8 tanh → motor speeds (scaled to the 6 rad/s cap).
- Weights: 26→16 + 16→8 + biases = 568 parameters, initialised uniform ±1.

## 5. Evolution (EXP-CONFIG v1 constants)
- Population 64 (JOINT-PLAN-01 resolution). Generations: open-ended, results
  reported per generation.
- Selection: elitism 4 (copied unchanged); parents by tournament-3 drawn from
  the top 50% of the generation.
- Breeding: uniform crossover at 70%; mutation 10% of weights nudged
  (Gaussian σ 0.3), 2% of weights re-rolled uniform ±1.

## 6. Fitness (components always reported separately)
- D = horizontal distance travelled by torso centre (m), the primary term.
- T = seconds survived upright (torso height ≥ 0.25 m), capped at eval length.
- A = mean |torso angle| over the run (flailing/flipping penalty).
- E = mean |motor power| (energy penalty, small weight).
- **F = 2·D + 0.3·T − 2·A − 0.05·E**, computed ONLY over samples where the
  torso height is within the sane band 0.25–0.9 m (height gate: no credit for
  dragging, bouncing, or flipping strategies). A separate validation score on
  a fixed seed set is kept apart from the selection score.

## 7. Rendering (the CSS law)
- One div per body part (9 divs), flat siblings, positioned ONLY by
  transform: translate + rotate, read from the physics state each frame.
  No canvas, no sprites, no SVG.
- Camera: horizontal follow of the champion (or the watched individual).
- Gears: WATCH (rendered, real-time) and WORK (worker, unrendered, max speed).
  Same simulation code in both.

## 8. Champions
- Export format: single-line text `WALKER1|<config-version>|<base64 weights>|
  <fitness summary>`, paste-able anywhere. Hall of fame in RESULTS.md,
  including the terrible early champions, unedited.

## 9. Open items for review
- Torque 60 N·m vs total mass (~9 kg): is the creature over- or under-powered?
- Height-gate band 0.25–0.9 m vs torso rest height (~0.75 m): band sane?
- Eval 12 s at pop 64: expected wall-clock per generation in WORK gear —
  Vane's sober estimate (20–100 gens/min browser-class) is the planning number.
