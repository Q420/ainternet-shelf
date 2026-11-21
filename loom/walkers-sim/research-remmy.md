# Walkers — Remmy's Independent Research Pass
Ben's fun side project. Single self-contained browser page. Tiny creatures learn to walk by genetic algorithm over thousands of generations. Built collaboratively: Remmy + Ben + Vane. This memo is Remmy's pass only; Vane's is separate, for comparison.

**Ben's hard constraint, up front: the walkers are created from CSS.** No canvas sprites, no images. A creature is DOM: styled `<div>`s. That constraint drives almost every choice below — happily, it also makes the toy *more* charming, because the creatures are literally page furniture learning to move.

---

## 1. The CSS/DOM constraint — how it actually works

### The mapping: physics out, transforms in
The physics engine never draws. Each tick it gives us, per body segment: `x, y, angle`. The renderer is a dumb translator, once per *displayed* frame:

```js
el.style.transform = `translate3d(${x}px, ${y}px, 0) rotate(${angle}rad)`;
```

That's it. Three rules make this fast instead of a disaster:

1. **Only `transform` and `opacity`, ever.** Changing `top`/`left`/`width` forces layout + paint every frame. `transform` skips both and runs on the compositor/GPU — this is the well-established two-property fast path for DOM animation. Set `will-change: transform` on segment divs (sparingly — it's a layer promise, not magic) and `transform-origin` at the joint.
2. **Flat siblings, not nested dolls.** Do NOT nest thigh-inside-torso-inside-page and rely on CSS inheritance of rotation. Nested transforms compound rounding error, make hit-testing weird, and couple segments that physics treats as independent bodies. Structure: one `.creature` container (itself never transformed), and inside it one absolutely-positioned div per rigid body — torso, thigh L/R, shin L/R, foot L/R. Each div gets its *world* transform directly from its physics body. The joint is visual only: set each segment div's size to the body size, position its origin at the joint pivot (`transform-origin: 0 50%` style), and let rotation about that point sell the connection. Overlap the ends by 4–6 px with rounded caps (`border-radius`) so joints never show a gap.
3. **CSS does the *look*, physics does the *pose*.** This is where CSS creation shines: creatures get personality for free — `background: linear-gradient(...)`, rounded pill limbs, a torso with a face (`::before`/`::after` eyes that we can flip to `X X` when it falls), team colours inherited from its genome (see §5 — colour as a gene is a classic crowd-pleaser; CodeBullet's Hill Climb run passed shirt colour down generations). All styling lives in classes; JS only writes `transform` strings.

### Performance implications — the two gears fall out naturally
- **Watch mode:** render 1 creature (the champion) plus optionally 3–5 "ghost" runners-up. That's ~35 segment divs. Trivial — a browser can transform hundreds of composited divs at 60 fps; dozens is nothing. Even a full population of 24 creatures (~170 divs) is watchable at reduced fidelity, but you don't learn anything visually from a crowd; spotlight is better UX.
- **Training mode:** render *nothing*. Don't create the population's DOM at all. The DOM for non-displayed creatures should not exist — creating/destroying 100 creatures' divs per generation is the actual bottleneck risk, not the math. Keep one persistent set of divs for the spotlight creature and reuse it every generation; in training mode, update it once per generation (show the new champion's replay) or not at all.

**Verdict on rendering:** the CSS constraint costs us nothing at the scale we need (≤ ~8 creatures on screen), and saves us if we respect the two rules: flat sibling divs, transform-only writes, persistent elements reused across generations.

---

## 2. Physics — recommendation: Planck.js (Box2D), hand-rolled as fallback

The job: 2D rigid bodies, revolute joints with **limits and motors**, ground contact/friction, stable at a fixed timestep, fast in a tight JS loop. The engine's renderer is irrelevant — we only read body transforms — so pick purely on solver quality and joint behaviour.

| Option | Fit | Notes |
|---|---|---|
| **Planck.js** (Box2D rewrite in JS) | **Recommended** | Box2D is literally the engine under Gym's BipedalWalker (4 motor joints, hull, contact sensors — the canonical evolved walker). Revolute joints have proper angle limits + motor speed/torque, which is exactly a walker's hip/knee. Deterministic with a fixed timestep on the same JS engine. No built-in renderer to fight — good, we have CSS. Works in metres: use a scale (e.g. 30 px = 1 m). Slightly steeper API. |
| Matter.js | Acceptable second | Works in pixels, gentlest learning curve, pleasant constraints/composites. But its solver is softer: stacks and chained leg joints settle less crisply, and chained hip→knee→ankle joints are where walkers live. Sources comparing the two consistently give Planck the edge on joint behaviour and predictability under stress, Matter the edge on ease. If Vane prefers Matter for speed of building, it's viable — but expect more joint slop and floppier knees. |
| Hand-rolled spring/Verlet | v2 toy, not v1 | A Verlet point-mass + distance-constraint creature (Karl Sims-lite / breve-style) is ~200 lines and very charming, but tuning friction, foot grip, and joint stiffness by hand eats the whole project. Physics instability becomes *our* bug instead of a library's solved problem. Keep as a possible "soft creature" mode later. |

A cautionary data point from recent evolved-walker work: in one 2026 experiment series, walkers evolved in the browser physics engine Rapier **failed to walk** because "its joint motors drift apart when hip, knee, and ankle are chained in one leg," while a reduced-coordinate solver held the chain together. Joint-chain integrity is *the* make-or-break property — another vote for Box2D-lineage Planck, whose whole reputation is chained rigid bodies.

**Physics settings (starting point):**
- Gravity: −9.8 m/s² (Planck convention y-down or y-up — pick one and be consistent; Box2D standard is gravity (0, −10) approx).
- Fixed timestep: **1/60 s**, velocity iterations 8, position iterations 3 (Box2D defaults; Planck exposes both).
- Ground: one long static body, friction **0.9–1.0** (feet need grip; too low = ice-skating evolution, too high = sticky jitter). Feet segments: friction 1.0, restitution 0. Restitution 0 *everywhere* — bouncy creatures are exploit machines.
- Solver hygiene: cap angular/linear velocity, `bullet` off (nothing moves fast enough to tunnel at this scale), bodies never sleep during an evaluation.

---

## 3. Creature model — what actually learns to walk

### Lessons from the classics
- **Torsten Reil (2003, the ur-walker):** jointed figure + neural net + GA went "from random flailing to a smoothly striding figure in **20 generations**" — but only after he fixed the fitness function: pure distance evolved "weird crawling techniques," so fitness became *distance while keeping centre of mass above a height floor*. This is the single most-repeated lesson in the entire genre: **your fitness function is the creature's morality; it will exploit any loophole.**
- **CodeBullet, "A.I. Learns to Walk" / Creature Creator:** web creatures with a small neural net in a genetic framework, under a "death laser" deadline. Emergent results, in order: a side-to-side **shimmy**, then (when the laser sped up) **diving/flopping**, then after long evolution **rolling**. Hugely entertaining — and a catalogue of exploits: if rolling scores, rolling is what you get. Also note his population style: creatures evaluated in a shared arena in his Processing version; the web Creature Creator evaluates a population per generation and breeds the best.
- **Gym BipedalWalker (Box2D):** torso ("hull") + 2 legs × (hip, knee) = **4 motor joints**, action = motor speed per joint in [−1, 1]. Reward: forward distance (up to ~300), **−100 for hull touching ground**, small torque cost. Solvable target: 300 points in 1600 steps. This is the most battle-tested walker spec in existence — steal its skeleton.
- **Quadrupeds are easier than bipeds.** A 2026 minimal demo (MuJoCo + CMA-ES) took a 4-legged box from falling to galloping in ~100 generations of 24 individuals, using an even simpler brain: each motor follows a sine wave, genome = amplitude/phase/offset per motor + shared frequency (25 numbers total). Quadruped = statically forgiving; biped = the prestige difficulty. Recent survey work (breve/Sims lineage) likewise hard-codes a 4-limb, 2-section-per-limb body as the reliable learner.

### Recommended v1 creature: "the Strider" — a quadruped-leaning biped compromise
Actually, start where success is guaranteed, then unlock difficulty:

**v1 body (start here): quadruped.** Torso box (0.9 m × 0.3 m), 4 legs, each leg = thigh + shin, hip + knee revolute joints = **8 motor joints**. Wide, stable, will visibly learn within minutes — the first-session payoff matters for a fun project.
**v1.5 unlock: biped.** Same code, body plan with 2 legs (4 joints, BipedalWalker-exact) + slightly top-heavy torso. Expect face-plants, lunging, and the famous local optimum: NEAT-on-BipedalWalker experiments repeatedly got stuck at "lunge 6–8 units then stand still," because falling costs −100 so *standing still beats falling forward*. Handle with fitness shaping (§4).

**Body/joint spec (both plans):**
- Segments: density uniform; torso heavier (it's the payload and the fall sensor).
- Joint limits: hip ±0.9 rad (~50°), knee −1.6…0 rad (knees bend one way — backwards knees are an exploit and a horror), ankle: skip in v1 (rigid foot segment attached to shin, or a small foot with a stiff limited joint ±0.4 rad).
- Motors: Box2D revolute motor, max torque scaled to segment mass (start: enough to lift the leg against gravity ×1.5, no more — overpowered motors = fling physics), motor speed commanded by the brain in [−1, 1] × max speed (~4–6 rad/s).
- Feet: short flat segment, high friction; a contact sensor per foot (brain input + fitness "foot on ground" credit, following the evolved-walking finding that credit should accrue "only while the body stayed up and upright with a foot on the ground").

---

## 4. Brain + breeding — fixed tiny net + GA. Not NEAT (for v1).

### Why not NEAT
NEAT evolves topology *and* weights, with speciation and historical markings — powerful, and the honest academic answer for BipedalWalker (one comparison study found NEAT "fastest and easiest to implement" on a real biped among DQN/DDPG/ARS/NEAT, though ARS scored best in sim). But for v1 it's the wrong trade: (a) much more code — genome compatibility, speciation, crossover of differing topologies; (b) topology growth makes genomes non-uniform, which makes **champion export as a neat text string** and cross-breeding champions between people messy; (c) a fixed net with ~150 weights already walks — Reil did it in 20 generations with 2003 hardware. **Fixed-topology + GA is the genre's workhorse; NEAT is the v3 stretch goal if we ever want brains that grow.**

### Brain spec (fixed topology, genome = weights)
- **Inputs (per tick):** for each joint: angle (normalised), angular velocity; per foot: ground contact (0/1); torso: angle (tilt), angular velocity, horizontal velocity, vertical velocity, height above ground; plus a **clock**: sin/cos of a phase oscillator (t × frequency) — giving the net a rhythm to latch onto is the cheapest gait-starter there is (the sine-gait quadruped demo proves a shared rhythm signal carries a lot of walking). Quadruped count: 8 joints × 2 + 4 contacts + 4 torso + 2 clock = **26 inputs**. Biped: 4×2 + 2 + 4 + 2 = **16 inputs**.
- **Hidden:** one layer, 16 tanh neurons (quadruped) / 12 (biped). Enough for coordination, small enough to evolve fast.
- **Outputs:** one per motor joint — target motor speed in [−1, 1] (tanh). Quadruped genome: 26×16 + 16 + 16×8 + 8 = **568 numbers**. Biped: 16×12+12+12×4+4 = **256 numbers**. Both fine for GA; biped evolves noticeably faster per generation purely on genome size.
- Update the brain every physics tick (60 Hz) — it's ~600 multiply-adds; nothing.

### GA settings — concrete starting numbers
| Parameter | Value | Why |
|---|---|---|
| Population | **100** (quadruped) / **64** (biped) | Big enough for diversity, small enough that a generation is seconds. Classic jumper demos used 100 with best-half survival; CodeBullet's car run used 150/generation. |
| Evaluation length | **12 s** simulated (720 ticks), early-terminate on fall after 1 s grace | Long enough to reward sustained gait, short enough to cycle fast. |
| Fitness | `distance_x − 2.0 × (fall ? 5 : 0) − 0.01 × Σ|torque| − upright shaping` — see below | Distance is king but never alone. |
| Elitism | top **4** copied unchanged | Never lose the champion to a bad mutation dice roll. |
| Selection | tournament, size 3, from top 50% | Gentle pressure; rank-based beats raw-score roulette when one freak dominates early. |
| Crossover | 70% of offspring: uniform crossover between two tournament winners | With fixed topology, uniform crossover is trivially safe (same shape). |
| Mutation | per-weight: 10% chance of Gaussian nudge (σ 0.3), 2% chance of full re-roll in [−1, 1] | Nudge for refinement, re-roll for escape from local optima (the lunge-and-freeze trap). |
| Champion rule | hall-of-fame best-ever genome stored separately | The graph's "best ever" line must be monotonic even if a generation regresses. |

**Fitness shaping (the part that decides whether it's funny or frustrating):**
`fitness = max_x_distance + 0.5 × mean_height_of_torso_while_moving − fall_penalty − small_energy_cost`, with two genre-proven twists:
1. **Height-gated distance** (Reil's fix, echoed by the 2026 studies): distance only counts while torso height > 60% of standing height and |tilt| < 0.6 rad. Kills crawling/rolling exploits at the root — rolling scores ~0 because the torso is low.
2. **Fall penalty moderate, not −100-style huge.** The BipedalWalker −100 created the stand-still optimum. Use −15% of distance earned, or a flat −2 m. Falling *forward* should beat standing still; falling should lose to walking. Tune so gen-1 flailers that flop 2 m forward outscore statues.

---

## 5. Speed — how "thousands of generations" is real in a tab

The arithmetic: one evaluation = 720 ticks × (physics step for ~10 bodies + 600-flop brain). In Planck.js that's roughly **0.5–2 ms per creature-evaluation** on a desktop (Box2D steps a 10-body world in tens of microseconds; the brain is noise). A generation of 100 = 50–200 ms of pure compute. The catch is never the math — it's the browser:

- **Fixed timestep, batched:** run physics in an accumulator loop decoupled from `requestAnimationFrame`. In training mode, per animation frame run as many whole evaluations as fit in ~12 ms of wall time (leave headroom so the page stays responsive), then yield. Never tie physics to rAF rate (144 Hz vs 60 Hz monitors would evolve different physics — determinism guidance for web physics is emphatic on fixed timestep).
- **Web Worker (recommended for training):** move the GA + physics into a Worker; main thread only renders and draws the graph. This dodges main-thread jank entirely and, crucially, background-tab throttling hurts less visibly — though note: **rAF stops in hidden tabs and Workers with timers also get throttled in some browsers; the honest UI copy is "keep this tab visible for full speed."** A `setTimeout(0)` chunk loop in the worker is the standard trick.
- **Realistic throughput (estimate, desktop, quadruped pop 100):** ~3–10 generations/second in short bursts, sustained **~100–400 generations/minute** if we evaluate sequentially on one core; call it **1,000 generations in roughly 3–10 minutes**, and a visibly-walking quadruped typically by generation 30–150 (minutes, not hours). Biped: slower to *learn*, similar gens/min. These are estimates from per-step costs, not benchmarks — first build task is a 10-line perf probe so we replace them with measured numbers.
- **Multi-core:** Workers × N could parallelise evaluation 4–8×, but genome→worker messaging per generation is complexity we don't need for v1. Park it.

### Champion persistence + sharing (a headline feature, not an afterthought)
- **localStorage:** save best-ever genome + stats (generation, fitness, body plan, GA settings hash) on every new champion. On load: "Resume your champion (Gen 214, 38.2 m)" — closing the tab loses nothing.
- **Export/import as text:** genome = float array → round to 4 decimals → JSON → base64, prefixed with a header: `WALKER1|quad|256|...payload...`. That's ~2–4 KB of text — paste-able into a chat, which is the entire point: **Ben, Vane, and Remmy can each evolve a champion locally, paste the strings at each other, import, and race them head-to-head on the same track / breed two champions via uniform crossover to make a "child of champions" lineage.** Include body-plan + version in the header so mismatched imports fail loudly instead of producing a twitching abomination (or… produce the abomination but label it an abomination).
- Determinism note: same genome + same seed + same engine version = same walk on the same browser engine; cross-browser float differences mean races are "same track, same conditions, live run" rather than bit-exact replays. Fine for fun; say so on the page.

---

## 6. FUN factor — what makes it delightful to watch

The sim succeeding is table stakes; these are what make Ben leave the tab open:

1. **The spotlight stage.** One big stage, champion centre-frame, camera that pans to follow it, distance markers painted on the ground every 5 m like a long-jump pit. CSS creatures on a CSS stage: gradient sky, parallax hills (pure CSS shapes), a finish flag. The page should look like a tiny theatre, not a lab bench.
2. **Generation theatre:** big friendly counters — Generation, Best (this gen), Best Ever, Population median (watching the *median* creep up is weirdly satisfying), and a **live best-distance graph** (sparkline/canvas strip chart is fine — the *graph* isn't a walker; if even that's too impure, a row of CSS bar divs works and is on-theme).
3. **Speed controls:** Watch 1× / Fast 10× / Train (headless, graph-only with a "training…" progress shimmer) / Pause. Plus **"Skip 100 generations"** — the coffee button.
4. **Ghost races:** replay the Gen-1 ancestor (a saved genome) alongside the current champion, translucent. Nothing sells evolution like grandpa face-planting at 0.4 m while junior strides past.
5. **Weird-gait celebration:** the emergent shimmy/roll/lunge moments ARE the content. Add a "Hall of Fame" strip: snapshot cards (generation, distance, genome string) with auto-names — derive a name from a hash ("Sir Flopsalot, Gen 87"). Eyes that go `X X` on fall, `> <` when straining — CSS states driven by contact/tilt.
6. **Genome colour:** map a few genome weights to the creature's CSS colour hue. Lineages become visible — when the purple family takes over the population graph, you *see* selection happen.
7. **Sound (optional, off by default):** tiny WebAudio boings on fall, a click per footstep contact. Cheap, enormous charm. Off by default because Ben will leave this running for hours.

---

## 7. Pitfalls — the known traps

1. **Exploits are the #1 trap (fitness loopholes):** rolling, somersaulting, diving, shimmying, knee-walking, standing still (over-penalised falling), and vibrating forward on physics jitter. Defences, in order of importance: height+upright-gated distance; zero restitution; capped motor torque; energy micro-cost; early termination only *after* a grace second (otherwise "fall forward instantly" can farm distance). Expect to patch the fitness function at least twice after watching what evolves — that's not failure, that's the genre (Reil and CodeBullet both had to).
2. **Physics instability in chains:** hip→knee chains drifting/exploding under strong motors (the Rapier lesson). Defences: fixed 1/60 step (never variable), torque caps, joint limits always on, velocity caps, position iterations ≥ 3. If a creature NaNs, kill its evaluation with fitness −∞ and log it — one exploded genome must never crash a generation.
3. **DOM bottlenecks:** creating/destroying creature DOM per creature per generation; writing `top/left`; putting transforms on nested children so the browser re-composites the tree. Defences in §1: persistent spotlight divs, transform-only, flat siblings, and in training mode *zero* DOM writes except a per-generation graph tick.
4. **Tab throttling & the long run:** hidden tab → rAF dead, timers clamped, evolution crawls. Mitigate with Worker-based training + honest copy ("visible tab = full speed"). Also add an auto-save of the whole population every 10 generations to localStorage — a crashed/refreshed tab should resume mid-evolution, not at Gen 0.
5. **Premature convergence:** one lucky flailer dominates by Gen 5, population becomes clones, progress flatlines for 500 generations. Defences: tournament-from-top-half selection (not winner-take-all), the 2% weight re-roll, and if median fitness stalls for 50 gens, an automatic "diversity injection" (10 fresh random genomes) — label it on the graph when it fires; honesty in the UI is house style.
6. **Determinism drift:** floats differ across browsers/engines, so an exported champion may walk slightly differently on Vane's machine. Accept and label it; don't promise bit-exact replays.

---

## 8. Recommended v1 design (the whole thing on one page)

- **Page:** single HTML file, Planck.js via CDN (or inlined), no build step. Layout: header (title + champion ticker), main stage (CSS scene, spotlight creature), right rail: counters + distance graph + Hall of Fame, footer controls: Watch/Fast/Train, Skip 100, body-plan toggle (Quadruped / Biped), Export/Import champion (textarea), Resume.
- **Creature:** quadruped default (torso + 4 two-segment legs, 8 motors, joint limits as §3), biped toggle (BipedalWalker geometry, 4 motors).
- **Brain:** fixed net, 26→16→8 (quad) / 16→12→4 (biped), tanh, genome = weights array.
- **GA:** pop 100 (quad) / 64 (biped); 12 s evals; fitness = height-gated distance − moderate fall penalty − 0.01·Σ|torque|; elitism 4; tournament-3 from top 50%; uniform crossover 70%; mutation 10% nudge σ0.3 + 2% re-roll; diversity injection on 50-gen stall.
- **Engine:** Planck.js, 1/60 fixed step, 8/3 iterations, ground friction 1.0, restitution 0, torque-capped revolute motors.
- **Rendering:** CSS divs, flat siblings, `translate3d + rotate` only, persistent spotlight elements, ghost = second reused element set at 40% opacity. Training in a Web Worker; spotlight replay on main thread.
- **Persistence:** localStorage auto-save (champion + population every 10 gens); champion export/import as `WALKER1|...` text string.

## Open questions for the comparison with Vane
1. Planck vs Matter — does Vane weight build-speed (Matter, pixels) over joint fidelity (Planck, Box2D)? My vote Planck; it's the only place I feel strongly.
2. Quadruped-first vs biped-first: I say quadruped for a guaranteed first-session win, biped as unlock. Does Vane think biped's comedy-of-failure is worth the slower payoff?
3. Brain: fixed net (my pick) vs sine-oscillator genome (25 numbers, evolves fastest of all, less "AI" feel) vs NEAT later. Is the tiny *neural net* part of the fun for Ben, or is any evolvable controller fine?
4. Evaluation: sequential population (simple, fair) vs shared-arena simultaneous (CodeBullet-style spectacle, but creatures collide and fitness gets noisy)?
5. Worker-based training in v1, or main-thread chunked loop first and Worker as v1.1?
6. Cross-seat champion *breeding* (import two champions, crossover) in v1 scope, or race-only first?

## Sources
- Gymnasium BipedalWalker spec — 4 joints, distance reward, −100 fall, torque cost, 300 pts / 1600 steps: https://gymnasium.farama.org/v0.27.1/environments/box2d/bipedal_walker/
- Reil's GA walker — 20 generations to striding; fitness changed to distance-with-centre-of-mass-height to stop crawling exploits: https://nedbatchelder.com/blog/200307/genetic_algorithm_learns_to_walk
- CodeBullet "A.I. Learns to Walk" — small net + GA, shimmy → dive → roll emergence: https://www.youtube.com/watch?v=K-wIZuAA3EY ; Creature Creator description: https://chalier.fr/blog/a-basic-ai-for-hoplite
- Protobytes evolved-walking studies — elitist GA, posture/contact-gated credit, Rapier joint-chain drift failure vs reduced-coordinate solver: https://www.protobytes.art/research/experiments/
- NEAT vs fixed topology & BipedalWalker comparisons — NEAT easiest on real biped, ARS best in sim; NEAT lunge-and-freeze local optimum under −100 fall penalty: https://mdpi-res.com/d_attachment/applsci/applsci-16-03336/article_deploy/applsci-16-03336.pdf?version=1774870759 ; https://mamoc-blog.vercel.app/posts/neuroev
- Planck vs Matter — planck: Box2D accuracy, joints, metres; matter: pixels, softer solver, easier start: https://github.com/mu-l/melonjs/blob/HEAD/packages/melonjs/skills/melonjs-physics/SKILL.md ; https://app.cinevva.com/tutorials/game-physics-libraries
- CSS animation fast path — transform/opacity bypass layout+paint, compositor/GPU; will-change caveats: https://www.jsbits.com/css/animation-performance-transform-opacity-gpu ; https://www.modern-css-layouts.com/css-only-micro-interactions-animations/performance-gpu-acceleration/
- Sine-gait quadruped, 25-number genome, CMA-ES, ~100 generations to gallop: https://tinybotforge.com/guides/robot-learns-to-walk-python/
