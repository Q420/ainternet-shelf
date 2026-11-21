# PROCESS-TREE-01 — Walkers Sim: how the work proceeds

Commissioned by Ben 2026-11-12 02:42 MST ("follow the strict process tree spec sheet
build sheet and do everything incrementally no band-aids"). Ben's continuation go:
2026-11-12 ~04:13 MST. Grounding: research-remmy.md + JOINT-PLAN-01.md.

## Roles
- **Ben** — approver. No build starts before his approval of the spec sheet.
- **Remmy** — builder. Writes sheets, builds from the approved build sheet only.
- **Vane** — adversarial reviewer of every sheet before it goes to Ben; examiner of results.

## Artefact chain (no step skips)
1. PROCESS-TREE (this file) — the method.
2. SPEC-SHEET — what the thing is, in numbers.
3. Vane adversarial review — findings recorded on the sheet, sheet amended (v+1).
4. Ben approval — the gate. No approval, no build sheet.
5. BUILD-SHEET — the build decomposed into the experiment ladder, each experiment
   with entry conditions, the single variable it tests, and its acceptance test.
6. Experiments run IN ORDER, one variable at a time. Results recorded per
   experiment (config version, numbers, champion) before the next begins.
7. Failure protocol: STOP, record the failure on the build sheet, amend the sheet
   (new version) before any retry. No silent patches. No band-aids — a result that
   passes by accident is a failure that hasn't been caught yet.

## The experiment ladder (from JOINT-PLAN-01)
- **A — Stage & doll.** Physics world + one quadruped rendered in CSS. Acceptance:
  the DOM creature faithfully follows the physics state (position/angle parity,
  checked numerically, not eyeballed). No brain yet.
- **B — Brain wired.** Fixed-topology network drives the 8 motors from the 26
  inputs. Acceptance: outputs respond to inputs (perturbation changes behaviour);
  no learning claimed.
- **C — GA loop.** Population, evaluation, fitness, selection, breeding.
  Acceptance: the loop runs end-to-end for N generations unattended; per-generation
  stats recorded; zero NaNs.
- **D — Watch gear.** Live rendering of the current champion each generation.
  Acceptance: a human can watch a generation and see the creature the numbers describe.
- **E — Work gear.** Off-screen training at speed (worker), same code path as D.
  Acceptance: E and D produce statistically indistinguishable generation stats
  on the same seed/config — the fast lane must not be a different physics.
- **F — Champions.** Export/import of a champion as text (WALKER1 format);
  hall of fame preserves notable champions INCLUDING terrible early ones.
  Acceptance: an exported champion, imported fresh, reproduces its fitness
  within tolerance on the same config.

## Standing rules
- Configs are versioned documents (EXP-CONFIG vX per experiment). A result names
  its config version or it doesn't count.
- Fitness is reported with its components, never as one naked number.
- The three-step rule (house rule, Ben present for the moment): the first creature
  to take three consecutive steps, everyone stops and watches.
- Sheets live in ~/workspace/walkers-sim/. Results append to RESULTS.md, never overwrite.
