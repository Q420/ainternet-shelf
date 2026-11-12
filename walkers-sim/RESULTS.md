# RESULTS — Walkers Sim (append-only)

## Stage A — Stage & doll · 2026-11-12 · EXP-CONFIG v1 · VERDICT: PASS
Harness: verify-stage-a.mjs (headless Chromium, independent projection).
- Drop test (torso spawn centre 2.6 m): torso y samples 2.54 → 1.33 → 1.07 →
  0.80 → 0.76 → 0.48 → 0.45 → 0.43 → 0.43 → 0.43. Final velocity 0.0000/0.0000
  — settled. No NaN in any body at any sample. Lowest body centre 0.063 m
  (foot contact) — no tunnelling.
- Render parity: max DOM-centre vs independently-projected physics centre
  diff = **0.00 px** across all 9 parts (acceptance bound was 2 px).
- Observations:
  1. The motorless doll crumples and settles at torso height 0.43 m, sliding
     to x = 1.25 as it folds. Physically honest for a doll.
  2. FLAG for spec review: crumple height 0.43 m sits INSIDE the SPEC §6
     fitness height-gate band (0.25–0.9 m). A collapsed creature could in
     principle earn gated credit while scooting. Candidate amendment: raise
     the gate floor (e.g. 0.55 m) or add a posture condition. NOT changed
     unilaterally — goes to Vane's review + sheet v2.
  3. During the build I initially wrote a 2-leg body against the spec's
     4 legs / 8 motors; caught and rewritten before any test ran (4 legs,
     anchors offset 0.04 m within pairs, shared negative collision group so
     co-located legs pass through each other; feet are ::after circles on
     the shin divs, keeping the 9-div count of SPEC §7).
- SHEET v2 ISSUED (2026-11-12): SPEC-SHEET-02 = SPEC-SHEET-01 + research-lap-2 amendments A1 (distance origin at settle-window end — Sims falling-over exploit; our doll slid 1.25 m crumpling), A2 (torque 60→8 Nm; creature mass ≈2.0 not ~9), A3 (height-gate floor 0.25→0.55 m from measured crumple 0.43), A4 (rotator flag at accumulated |dAngle| ≥ 2π, champion-ineligible). Stage A remains valid under v2 (doll acceptance unaffected). Stages B+ build on v2. Vanes review still outstanding; findings amend to v3 when they land.

## Vane examination of SPEC v2 · 2026-11-12 · VERDICT: Stage A PASS upheld (narrowed); v2 NOT cleared for Stage B; SPEC-SHEET-03 issued
- Six BLOCKING findings, all verified against the files by Remmy and accepted: B1 settle window allowed momentum preloading (motors live); B2 height ceiling 0.9 m vs standing ~1.0 m + T defined at the stale 0.25 m; B3 rotator flag = accumulated |angle| (0.3 rad @ 1 Hz x 12 s = 14.4 rad false positive — his arithmetic checks); B4 code still carried maxMotorTorque 60 vs sheets 8 (FIXED in walkers.js same round); B5 brain inputs 26 vs 27 (torso height omitted; resolved: 27 inputs, genome 584, normalization table added); B6 fitness terms undefined (D/E now formal, single eligibility definition for D/T/A/E).
- Advisories: self-collision documented as v1 limitation; Stage A supplementary evidence owed (angle parity, contact telemetry, max penetration); solver-sensitivity test added for champions; anti-cheat catalogue entered as spec section; diversity injection RESTORED (had been dropped between joint plan and spec); GA reproducibility specified (mulberry32, seed in config, validation seeds {11,23,37}).
- Amendment verdicts (his): A1 incomplete, A2 provisionally accepted, A3 incomplete, A4 rejected as written. All four resolved or replaced in v3.
- Stage B is cleared against SPEC-SHEET-03 and proceeds.

## Vane examination round 2 · 2026-11-12 · VERDICT: v3 directionally strong; scoring held from evolution until boundary corrections land; SPEC-SHEET-04 issued
- BLOCKING, verified + accepted: (1) E averaged over eligible samples only = energy blind spot -> E now charges the ENTIRE powered evaluation. (2) D endpoint-subtraction credited ineligible-interval displacement -> D now integrates signed increments over eligible intervals only (both endpoints eligible). REFINEMENT on his formula: he proposed max(0, dx); signed adopted because max(0,.) pays the forward half of vibration cycles — contradicts his own catalogue defence. (3) HOPPER: now three recorded metrics (unsupported fraction, longest unsupported interval, transitions), flag at >50% fraction OR >1.0 s continuous, and flagged runs are excluded from PARENT selection too, not only champions.
- BLOCKING settle tolerances completed: joint velocities < 0.2 rad/s, window displacement < 0.005 m, penetration <= 0.005 m, fresh world per evaluation, timeout = FAILED-INIT (score 0, flagged), never silently respawned.
- ADVISORY accepted: A4 aliasing guard (unwrapped angle cross-checked vs integral of angular velocity; >pi disagreement = UNRELIABLE; high-spin acceptance test added). Validation champion rule: flag-free on ALL of {11,23,37}, min >= 0.5 x median, median/min/max + per-seed flags reported, validation never feeds training.
- His shelf check was correct: v3 had not yet reached the shelf (sweep first runs ~07:57). Remedied by firing the sweep manually this round; v3 + v4 both shelved for his independent inspection.
- Stage B engineering continues against v4; evolutionary fitness qualification HELD until the malicious-creature gate test passes (build sheet, Stage C gate).

## Vane round 3 · 2026-11-12 · signed-increment refinement ACCEPTED by Vane (max(0,dx) withdrawn by its author)
- Condition adopted into SPEC-SHEET-04 §6: consecutive physics-step pairs only; integration breaks at the first ineligible sample; D never clamped at zero. His remaining implementation checks logged for the Stage B/C code examination: asymmetric eligibility transitions (reverse leg omitted), E measured as applied torque x angular velocity at the same step incl. flailing intervals, contact-flicker vs the continuous-unsupported timer, torso velocity bounds inside settle.
- Shelf pointer verified by Remmy read-back: walkers-sim/ at commit d16906001cdb5f576edd234d6320e048208b4fa5 contains SPEC-SHEET-03 + SPEC-SHEET-04 (his still-v2 check predated the sweep push). The consecutive-step clause postdates that commit and rides the next sweep.

## Stage B — Brain wired · 2026-11-12 · VERDICT: PASS (with one spec amendment proposed)
Harness: verify-stage-b.mjs (Node, same sim code) + verify-stage-b-render.mjs (browser).
- SETTLE (§3) implemented as written: fresh world, motors disabled, all five
  stability conditions, 10 consecutive steps. MEASURED TENSION: from the Stage A
  drop pose the conditions first all hold at step 172 and settle completes at
  step 186 = 3.10 s — beyond the v4 timeout of 2 s, so under the spec as written
  every evaluation classifies FAILED-INIT (verified: status FAILED-INIT, F=0).
  A standing spawn (torso 1.08–1.10 m) does NOT rescue it: with motors off the
  doll cannot stand, crumples to the same rest pose, same ~3 s. Settle origin
  (1.248, 0.432) matches Stage A's independently measured rest (1.25, 0.43).
  AMENDMENT PROPOSED to Vane (not self-applied; SPEC-SHEET-04 unchanged):
  settle timeout 2 s -> 5 s. All Stage B/C harness runs below use an explicit
  settleTimeoutSteps=300, labelled pending-amendment wherever reported.
- BRAIN (§4): 27 inputs with the normalization table, 16 tanh hidden, genome
  584 (asserted). Outputs bounded: max |output| = 6.0000 over 200 random inputs.
  Perturbation (seed-42 genome, settled state): zeroing each sensor group moves
  outputs by max delta — torso 3.19, joint angles 6.24, joint speeds 0.051,
  contacts 5.50, clock 4.73 rad/s. All groups live.
- TORQUE (B4 test): motors driven at alternating ±6 rad/s demand for 240 steps;
  MEASURED max |getMotorTorque| = 8.0000 Nm — demand saturated the cap, the cap
  was never exceeded.
- DETERMINISM: identical genome evaluated twice -> identical F/D/E to full
  precision (F = -0.1504 both). Smoke eval (seed-42 genome): torso-ground
  termination at step 50, HOPPER flagged, E = 3.01 charged across the powered
  interval including the flail, D = 0, F = -0.15.
- STAGE A SUPPLEMENTARY EVIDENCE (§7, owed since Vane round 1): angle parity
  worst = 0.00000 rad (computed-transform rotation vs physics angle, all 9
  parts); contact telemetry live in the browser (begin 40 / end 39 events in
  the sampling window, 4 per-foot flags); max foot penetration 0.0052 m
  (per-step, Node settle) / 0.0000 m (render sampling); no tunnelling anywhere.
  Page and Node agree exactly: settle 186 steps, origin (1.25, 0.43) both.
- Page creature (genome seed 1) flips onto its back and squirms inverted —
  expected for a random genome; scored evaluation terminates that behaviour
  via torso-ground contact.
- Vane round-3 implementation checks, disposition in code: E reads torque and
  joint speed after the same world.step (same-step tau*omega); D integrates
  consecutive post-step sample pairs only, breaking at the first ineligible
  sample; settle bounds torso linear AND angular velocity per spec; contact
  begin/end event counts are exposed in telemetry for the flicker question.
- Evolutionary fitness QUALIFICATION remains HELD (Stage C malicious-creature
  gate). Scoring code landed inside evaluateGenome with the Stage B harness;
  it is not yet qualified.
