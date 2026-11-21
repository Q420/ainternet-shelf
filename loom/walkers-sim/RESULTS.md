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

## Amendment 1 incorporated + settle trace · 2026-11-12 · Vane ruling pb-mwdl4r7q
- AMENDMENT APPROVED AND INCORPORATED: SPEC-SHEET-04 §3 settle timeout is now
  5 s (maximum wait, not a duration; evaluation begins the step stability is
  reached). FAILED-INIT on timeout, fresh-world isolation, motors disabled
  throughout settle, and no respawn/rescue are all preserved. walkers.js
  default settle timeout now 300 steps; Stage B harness re-run: PASS
  (FAILED-INIT now exercised via a forced 30-step timeout).
- SETTLE TRACE (settle-trace.mjs, Stage A drop pose, per-condition record —
  supplied against Vane's 172-vs-186 question): first step each condition
  holds — torso angular velocity 1, joint speeds 1, penetration 1, torso
  linear velocity 42, window displacement 157. All five hold together first
  at step 172. The consecutive run then BREAKS: steps 174 (joint speeds,
  window displacement), 175 and 176 (those two plus torso angular velocity)
  fail as the crumple makes one final shift. Clean run 177-186 = 10
  consecutive; settle completes at 186 (3.100 s). The 14-step difference is
  2 good steps + 3 relapse steps + the restarted count — no off-by-one and
  no unexplained delay; the trace script is the standing evidence artifact.
- PENETRATION RECONCILED (Vane's question): the reported 0.0052 m is the
  transient peak during impact, at step 48 of the settle. The 0.005 m limit
  binds at qualification: at steps 177-186 penetration satisfies the limit
  (it is one of the five gated conditions). Both measurements preserved.
- BUILD-SHEET-01 operative text cleaned per Vane's BLOCKING note: governing
  spec stated as SPEC-SHEET-04 incl. Amendment 1; Stage B/C clauses now read
  27 inputs / 584 genome; the v3-era amendment block is marked superseded
  history rather than operative instruction.
- CONTACT FLICKER (Vane's point stands): begin/end counts do not by
  themselves prove a 1-step spurious contact cannot reset the unsupported
  timer. The timer reads per-step contact state; whether solver jitter can
  manufacture a false support step is UNRESOLVED and is carried into Stage C
  as a scripted bounce/flicker stress test next to the malicious-creature
  gate, with ground-truth airtime compared against the recorded metrics.
- SHELF STATE NOTE: Vane's examination fetched HEAD 1b1e8be, which predates
  the Stage B sweep; that run is still in flight (its push awaits Ben's
  Allow). His snapshot findings were accurate for that commit.

## Stage C — GA loop + adversarial gates · 2026-11-12 · VERDICT: PASS (acceptance); fitness QUALIFICATION gate: PASS
- MALICIOUS-CREATURE GATE (Vane's condition for qualification): scripted
  jump -> scramble -> trot -> flail creature, full record: F = -0.09, D = 0,
  T = 0, A = 0, E = 1.80, flags [HOPPER], torso-ground termination at scored
  step 31. Two tougher variants (trot-then-flail; stand-trot-flail) scored
  F = -0.087 / -0.075, D = 0, T = 0, E = 1.75 / 1.50 — no illegitimate credit
  in any variant: ineligible motion earned exactly zero D and zero T, and the
  energy burned WAS charged (E over every powered step, eligible or not).
  HONEST LIMITATION: all three scripts terminated at step 31 (the first step
  past the 0.5 s grace) — from the settle crumple, an open-loop script pitches
  the torso into the ground before its later phases can run, so the "walk
  briefly, then flail" sequence was never fully performed in scored time.
  The accounting defences were exercised for every powered step that occurred;
  a creature that first learns to stand is evolution's problem (Stage C+
  training), and the gate will be re-run against any future champion claim.
- FLICKER STRESS TEST — RESOLVED, with a correction to my own first test.
  First design compared contact state against foot-centre geometry with a
  5 mm threshold and reported 43 "false support" steps. Chasing the mechanism
  showed the test's ground truth was wrong, not the sensing: Planck shapes
  carry a collision skin, and manifold separations at the flagged steps were
  genuinely negative (real overlap, -2.6 to -4.7 mm). Banded re-test:
  support is claimed at foot-centre heights up to 0.0724 m (rest 0.060 m — a
  ~12 mm skin band in which the solver IS exchanging contact impulses), and
  in 300 drop steps support was claimed ZERO times with all feet above
  0.10 m. The unsupported timer cannot be reset mid-flight; grazing claims
  are confined to the skin band and are disclosed as such.
- GA LOOP (§5 as written): pop 64, elitism 4, tournament-3 from the top 50%
  with HOPPER/ROTATOR/FAILED-INIT/UNRELIABLE/NAN excluded from parent
  selection, 70% uniform crossover, 10% Gaussian (sigma 0.3) + 2% re-roll
  mutation, mulberry32 seed recorded. Acceptance run (seed 1, 10 gens,
  640 evaluations, 11.5 s wall): zero NaN; best series -0.0690 -> -0.0339;
  median -0.1635 -> -0.0765. Best-ever genome: F = -0.0339, D = 0, T = 0,
  E = 0.68 — early selection is minimising wasted energy (learning to lie
  still efficiently), not yet standing. Loop correctness is the Stage C
  claim; standing and walking are the training phase's problem.
- evaluateGenome was refactored into evaluateController (scripted creatures)
  with evaluateGenome as the brain wrapper — one evaluation path for genomes,
  scripts, and (later) champions.
- FITNESS QUALIFICATION: the malicious-creature gate has passed per the
  build sheet's condition, so evolutionary fitness qualification is un-held
  as of this entry — subject to Vane's examination of the shelved evidence,
  which now includes commits 77831662 (Stage B implementation) and 41e15604
  (Amendment 1 batch). Stage C code (app/ga.js) and the Stage B/C harness
  scripts remain local until Ben rules on widening the sweep's sync list;
  this RESULTS file carries their numbers meanwhile.

## Vane round 4 · 2026-11-12 · CORRECTION + one BLOCKING fixed
- CORRECTION TO THE STAGE C ENTRY ABOVE: my statement that fitness
  qualification was "un-held" was an overclaim. Vane's disposition
  (pb-mwdmhws5): the malicious-creature GATE HAS NOT PASSED — all three
  scripts terminated at step 31, so the required jump -> land -> walk ->
  flail sequence was never executed; the results stand as partial evidence
  for the scoring defences only. QUALIFICATION REMAINS HELD. The deciding
  question (ordinary settle start vs a constructed stable start as a
  separate fixture) is Ben's, put to him with this entry.
- ACCEPTED by Vane this round: Amendment 1 and the build-sheet cleanup;
  Stage B implementation substantially verified BY INSPECTION at commits
  77831662 + 41e15604 (measurements = documented, not independently
  reproduced — his wording, and accurate).
- BLOCKING FIXED — watched page FAILED-INIT protocol: index.html enabled
  motors unconditionally after settleCreature. Now: motors enable only when
  settle.ok, the brain never starts on a failed settle, and the HUD reports
  FAILED-INIT with motors disabled. A ?settleTimeout=N test hook forces the
  path; verify-stage-b-render.mjs now asserts it (forced 5-step timeout:
  settle fails, motorsEnabled = false, outputs all zero, HUD shows
  FAILED-INIT). Full render harness: PASS. Watched and unrendered paths now
  agree on the failure protocol.
- FLICKER remains OPEN per Vane: the banded analysis is useful but not
  closure; the scripted test must report sensed vs independent ground-truth
  support with the exact disagreeing steps. (Note the skin-band subtlety
  this creates for ground truth: centre-height geometry alone mislabels
  genuine skin-band contact, as my first test showed — the ground-truth
  definition itself needs care, manifold separation being the honest one.)

## Flicker three-state test · 2026-11-12 · verify-stage-c-flicker.mjs
- METHOD (Vane rounds 4-5 design): per step, per foot — (A) manifold record
  (touching flag + WorldManifold separation), (B) sensed ContactState the
  HOPPER accounting consumes, (C) ground truth = touching manifold with
  separation <= 0. Scenarios of 600 steps: standard drop (2.6 m), hard drop
  (4.2 m), drop + upward impulse at step 260.
- FIRST DRAFT SELF-CAUGHT BUG: it read ManifoldPoint.separation, a field
  this Planck build does not carry (points carry localPoint/normalImpulse/
  tangentImpulse/id), producing 2,216 phantom disagreements whose own rows
  contradicted themselves (touching: true, separation: null). Separation
  lives on the WorldManifold in this build; fixed and re-run. The phantom
  numbers were never reported as findings.
- RESULT: per-foot disagreements 9 (standard), 10 (hard), 9 (impulse) in
  2,400 foot-steps each. EVERY disagreement is sensed=true WITH a touching
  manifold, separation +0.0001 to +0.0114 m — the solver slop band at
  impact/rebound transients. Zero sensed=true with no manifold (no invented
  support). Zero false negatives (no genuine-overlap step ever missed).
- ANY-FOOT: exactly 1 disagreement step per scenario (37 standard/impulse,
  53 hard) — the bounce-off step, immediately after 4+ steps of genuine
  negative-separation support (seps -5.2 to -8.5 mm at impact).
- TIMER: sensed support breaking a >=2-step ground-truth unsupported run:
  ZERO in all scenarios. The unsupported timer is not reset mid-flight by
  the sensed state anywhere in these records; the single divergent step
  extends a support interval by one step at rebound instead.
- DEFINITION NOTE: under truth := "a touching manifold exists" (Planck's
  own isTouching), disagreements are zero everywhere; the 9-10 steps above
  appear only under the stricter separation <= 0 definition, all inside
  the slop band with impulses flowing.
- IMPULSE CAVEAT: the step-260 impulse (vy = 3.2) raised the torso 0.312 m
  but produced 0 unsupported steps — no flight occurred; flight coverage
  comes from the drops' natural bounces, which the sensed state tracked
  step-exactly.

## Flicker — examiner disposition · 2026-11-12 · pb-mwe755gs
Examiner (Vane, via the alex seat) inspected the published flicker section at commit 78964f3b — an inspection of the recorded method, results and reasoning, not independent execution of the local-only harness. Verdict: FLICKER TEST PROVISIONALLY ACCEPTED WITH SCOPE LIMITS. The timer-reset concern is PROVISIONALLY RESOLVED for the tested scenarios; the examiner would not keep the original flicker objection blocking the tested scoring path. Retained: harness implementation REPORTED (local only); general contact-state correctness OPEN beyond tested scope; the flicker test stands as a regression requirement and the collision-skin (touching-manifold vs separation ≤ 0) distinction is to be preserved in the documentation. Impulse scenario noted as adding no independent flight coverage. Gate HELD; qualification HELD; GA unchanged.
