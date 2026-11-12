# BUILD-SHEET-01 — Walkers Sim v1 build, staged

Authority: Ben's preapproval, 2026-11-12 ~04:17 MST ("preapproved for the full
build, stages, batches, build, rewords… and implementation").
Governing sheets: PROCESS-TREE-01, SPEC-SHEET-01 (EXP-CONFIG v1).
Vane's spec review runs as a parallel gate; findings amend sheets en route.
Results append to RESULTS.md per stage. Nothing is "done" until its acceptance
test passes on recorded numbers.

## Stage A — Stage & doll (no brain)
- A1. Page shell: Planck.js world (gravity −9.8, fixed step 1/60, iters 8/3),
  static ground (friction 1.0, restitution 0).
- A2. Quadruped builder per SPEC §2: torso 0.9×0.3 (density 5); 4 legs
  (thigh 0.45 + shin 0.45, density 2); hip ±0.9 rad, knee −1.6…0 rad;
  motors present but OFF (doll); foot circles r 0.06, friction 0.9.
- A3. CSS rendering: 9 flat sibling divs, transform-only, camera follows torso x.
- A4. Test hook: window.__WT exposes body positions/angles + DOM rects.
- ACCEPTANCE: (i) drop test from 1.5 m — creature lands, settles, no NaN,
  no tunnelling, torso rest height in the sane band; (ii) render parity —
  DOM rect centres match physics-projected positions within 2 px over
  sampled frames, computed independently in the harness.

## Stage B — Brain wired (no learning)
- B1. 26-input sensor read per SPEC §4 (incl. 4 foot contacts via contact
  listener, clock sin/cos). B2. 26→16→8 forward pass; outputs → motor speeds.
- ACCEPTANCE: input-perturbation test — zeroing/clamping sensor groups changes
  motor outputs measurably; outputs bounded to the 6 rad/s cap.

## Stage C — GA loop
- C1. Population 64, genome = 568 floats; evaluation harness (12 s, early
  termination, height gate); fitness per SPEC §6 with components recorded.
- C2. Selection/breeding per SPEC §5. Per-generation stats to RESULTS.md.
- ACCEPTANCE: 10 generations unattended, zero NaN genomes, stats recorded,
  best-fitness series present (learning NOT required at this stage — loop
  correctness is the claim).

## Stage D — Watch gear
- D1. Live view: current champion replays/runs rendered in real time;
  generation counter + fitness components on screen.
- ACCEPTANCE: a watched generation visually matches its recorded numbers.

## Stage E — Work gear
- E1. Same sim code in a Web Worker, unrendered, batched evaluations.
- E2. Equivalence check: same seed + config through D-path and E-path;
  generation stats compared.
- ACCEPTANCE: best/median fitness per generation agree within tolerance
  over 5 generations (the fast lane is the same physics).

## Stage F — Champions
- F1. WALKER1 export/import (single-line text). F2. Hall of fame in RESULTS.md.
- ACCEPTANCE: exported champion re-imported fresh reproduces its recorded
  fitness within tolerance on the same config.

## After the ladder
Training runs toward an actual walking champion; the three-step rule applies
(first creature to take three consecutive steps, everyone stops and watches).
Results reported to Ben per stage, not as momentum.
