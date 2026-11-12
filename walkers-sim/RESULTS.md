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
