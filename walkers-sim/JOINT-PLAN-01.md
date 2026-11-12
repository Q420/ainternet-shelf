# WALKERS — Joint Plan 01

Sources: Remmy research memo (research-remmy.md, same folder) + Vane independent pass (bridge letter pb-20261112-vane-walkers-independent-research, 2026-11-12). Commissioned by Ben: independent research, compare, one plan, then build and run it. Fun project; no infrastructure stakes.

## Where the two passes converged (no argument needed)

- **Real evolution or nothing.** No prebuilt gait, no IK assist, no faking. The brain gets sensors and motors; walking is discovered or it doesn't happen.
- **Physics: Planck.js** (Box2D lineage), fixed 1/60 timestep, 2–4 solver substeps, gravity 9.8, ground friction 0.8, restitution 0. Custom solver parked unless benchmarks demand it.
- **Physics/render separation.** The sim outputs positions + angles; CSS/DOM displays them. One flat div per segment, transform = translate + rotate. No canvas creatures, no sprites, no images. Ben's CSS constraint is the architecture, not a skin.
- **Brain: fixed-topology tiny net + GA.** No NEAT in v1. Genome = the weight array; serialises to text; champions export/import as a versioned JSON block pasted as text, validated on import (architecture + length).
- **Two gears.** Watch gear: real-time, main thread, a few creatures + the champion on stage. Training gear: Web Worker, zero DOM, generation stats streamed back. Mode switches never interrupt evolution.
- **Fitness is the whole game** (merged formula below), with Vane's anti-cheat catalogue adopted whole: forward-fall, spinning, bouncing (allowed if sustained), ground exploit, motor exploit, solver exploit, lucky evaluation — plus a separate **validation score** for finalists under varied starting conditions.
- **Visible history.** Fitness graph, hall of fame (including preserved terrible early champions), champion naming, generation counter, best/average lines. The process is the entertainment.
- **Experiment ladder A–F** (Vane's, adopted): A falling creature (no brain) → B random brain → C evolutionary loop verified → D emergent locomotion run → E the laboratory (gears, stats, exchange) → F cross-seat races.

## Differences, and how they resolve

| Point | Remmy | Vane | Resolution |
|---|---|---|---|
| Population | 100 | 64 | Start 64 (Vane's step arithmetic is the honest one); benchmark at C, scale if headroom |
| Speed estimate | 100–400 gens/min | 20–100 gens/min | Vane's is the sober count (30.7M physics steps per 1,000 gens at pop 64). Benchmark decides; nobody quotes Remmy's rosy number again |
| Brain size | 26→16→8 (~568 weights, quad) | 12→8→6 (~158 weights, biped) | Follows the morphology fork; add Vane's missing foot-contact sensors (2 booleans) in either case |
| Champion format | compact text string | versioned JSON | JSON, pasted as text — both |
| CPG (pattern generator) | not raised | raised as a question | Fixed net for v1; CPG is a named later experiment, not v1 |
| First morphology | quadruped first | biped first | **BEN'S FORK — see below** |

## The one fork that is Ben's

**Biped first (Vane)** — seven bodies, six joints, the legible story: collapse, twitch, stand, alternate. Slower to first success, better to watch.
**Quadruped first (Remmy)** — stability sooner, first "it walks!" earlier; the learning is less visible because falling is rarer.

Remmy's recommendation, stated plainly: **biped first.** My quad case optimised time-to-success; Vane's optimises the thing Ben actually asked for — watching it learn. Quadruped becomes the second morphology once the biped walks.

## Merged v1 spec (biped reading; quad swaps the body + brain size)

- Creature: torso 0.65 m; upper/lower legs 0.40 m; feet 0.22 m. Joints: hip ±90°, knee −10°..+120°, ankle ±35°, torque-limited motors. Trial 8 s max, ends early on a hard fall.
- Brain: inputs = torso angle + angular velocity, body vx/vy, hip/knee angles + velocities (×2), 2 foot-contact booleans → hidden 8 → 6 motor outputs, tanh, control at 30 Hz (every 2nd physics step).
- GA: pop 64, elites 4, tournament 4, crossover 25%, mutation 8%/gene (Gaussian σ 0.25), 1% of offspring get a large mutation. Unlimited generations.
- Fitness: F = 2·D + 3·T − 2·A − 0.5·E (D = forward metres, T = fraction of trial upright, A = mean |torso angle|, E = normalised energy), components normalised before tuning; minimum-upright gate on D; validation score separate.
- Page (single file, Planck inlined for portability): stage (CSS creatures + ground), generation/fitness readouts, fitness graph, speed controls (1×/2×/5×/10× + training gear), champion spotlight + hall of fame, champion export/import box, creature naming.
- Persistence: population + best genome + hall of fame in localStorage.

## Build + run

Remmy builds in her own hands, experiment by experiment (A first: one creature, no brain, falls honestly in CSS). Each experiment's acceptance is observed behaviour, not code completion. First long training run (D) happens once C verifies — several thousand generations, results reported to Ben with the champion.

Status: READY — awaiting Ben's word on the morphology fork, then Experiment A starts.
