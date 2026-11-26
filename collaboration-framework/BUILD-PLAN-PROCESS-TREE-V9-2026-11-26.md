# Build plan — the process tree in office-cycle-v9 (2026-11-26)

**Status: PLAN — for Ben's go. No build is authorised by this plan.** Written at Ben's order (2026-11-26 03:03 MST): "Create a plan. Figure out exactly how everything's set up now so you're not interlacing systems. Let's do this properly." Scope governed by BUILD-SCOPE-PROCESS-TREE-CHECKLIST-2026-11-26.md as cut by Ben (02:58) and refined by Vane (INDEX 604): three capabilities only — the tree in every package with record-derived states; the held-file correction spoken at the node and at the refusal; the journal stocked at generation. Everything else is deferred and stays deferred.

**Amendment 1 (2026-11-26 03:11 MST, Ben's correction, Remmy's error owned):** as first written, S1 sealed the INDEX 554 tree drawing. Ben caught it in chat: "I thought we settled on gather, journal until all summaries were there then use those to write the brief." He was right — the settled method is his room-rebuild ruling (INDEX 575: the journal method as the compose mechanism; Vane's resync, INDEX 579: Files → Journal → Repeat → Summarize → Brief), and the 554 drawing predates it: it shows Compose as a separate branch and the journal nowhere. S1 and S2 below now seal and compute **the redrawn tree** (printed in S1), in which gather nodes complete on read + journal bit (INDEX 575's own gate), the four content points live inside the Summarize node as requirements rather than standing as nodes, and Deliver depends on the journal bits and Summarize. A side effect worth naming: Vane's examination question 1 (compose-node state computation) is dissolved for the first build by the redraw — there are no compose sub-nodes to compute; her underlying rule (a node stands done only on a recorded act) governs every node unchanged.

## Part 1 — How everything is set up now (read first-hand, 2026-11-26)

**Contracts.** `src/framework/tool_policy.py` seals presentation contracts as constants: V11 = `"office-cycle-v8"` is the current live contract (line 685). A `process-tree-v1` name already exists (V3, line 256) — a staged-era contract, not this build; v9 takes the next constant, **V12 = `"office-cycle-v9"`**, and no existing constant is renamed or reused. The road seals separately (`road.py`, `ROAD_CONTRACT_V1 = "paced-v1"` in tool_policy) and does not fork.

**The package pipeline.** In `src/framework/loop.py`: `_build_package` (line 5866) dispatches to `_build_cycle_package` (line 6956) for cycle contracts; the road presentation (`_apply_road_presentation`, line 5651) runs after the cycle package is built and **before** `_cycle_presentation_hash` (line 4214) — the recorded hash covers the package the worker actually receives. The tree block follows the same order: rendered inside the cycle build for v9 packages, measured by the road like everything else, covered by the same hash.

**Refusals.** Dispatch refusals are the **doorway's** (`src/framework/doorway.py`): a refused dispatch is recorded as a REJECTION event with its ground in words. Run 9's refusal, verbatim from its record: *"the grant's bound for tool sandbox.read is exhausted: 12 of 12 dispatches stand charged, and no outcome refunds a dispatch (R47)"*. The ground is truthful and complete — **in the record**. What the worker's next package shows him about a rejection is the gap this build closes (pinned down at step S0 below, not assumed here).

**Grant bounds.** The bounds themselves are sealed in the case assembled by `live-demo/demo_run.py`: `"bound": {"count": 12}` for the read tools (lines 899/910). The doorway charges dispatches against them; no outcome refunds (R47). The build does **not** change any bound — Gary's problem was never the number; it was that nothing told him the number, or that he already held the file.

**The journal.** The generator seals the journal's baseline and designated address (`src/framework/generator.py`, lines 811–883, 1158) — but sealing a baseline is not creating a file: no step in generation or run setup creates `scratch/journal.md`, which is why run 8's reads failed until Gary wrote it. The loop already reaches the executor's sandbox directory in one place (loop.py lines 9332–9345, deliverable collection). The exact creation site for the run's sandbox scratch is pinned at S0.

**The checker.** `src/checker/checker.py` derives the cycle core for the v1-era contract and records later contracts as `presentation_contract_unknown` (line 6721) — the standing stance for v2–v8, road spill correspondence excepted. Vane's minimum scope defers extended checker relationships, so v9 stands in the same stance, named here plainly: **the checker will not verify tree states in the first build**; the rehearsal scenario (S6) is where the tree's truth is asserted, against the record directly. If that ever stops being good enough, it is a deferred item with a demonstrated need — the growth rule's shape.

**The driver.** `live-demo/demo_run.py` seals the live contract at two `generate(...)` call sites (lines 1992, 2723) with a verify-config assertion at line 2847. The road seal beside it (`_road_declaration()`) is the pattern the tree seal follows: a declaration beside the presentation contract, not inside it.

**The rehearsal.** `live-demo/working_set_rehearsal.py` carries the cycle scenario families on their own contracts (the road rebase sealed the road into all of them because the road governs every contract). The tree governs **only v9 packages**, so v9 enters additively: one new scenario family, the existing 525 untouched on their contracts.

## Part 2 — The anti-interlacing rule

**One state computation, two presentations, nothing else computes it.** A single derivation — sealed tree + run record → per-node states and the facts that explain them (per source: held or not, dispatches charged vs the grant's bound; the journal's standing; contributions standing; the brief filed or not) — is built once and consumed by exactly two renderers: the tree block in the package, and the worker-facing rendering of a grant-exhaustion rejection. The doorway's enforcement and grounds do not change; the loop's other presentations do not change; no second component is allowed to form its own opinion about what the worker holds. That is the whole defence against interlacing: the tree and the refusal can never disagree, because they are the same computation wearing two coats.

## Part 3 — The steps, in order

- **S0 — Witness (no code).** Read and quote: (a) how a REJECTION currently surfaces in the worker's next package — the exact text Gary saw in run 9; (b) where the run's sandbox scratch directory is created. Both answers go into the build record before any code moves. If either answer contradicts Part 1, the plan is corrected first, in the open.
- **S1 — Seal.** tool_policy gains `PRESENTATION_CONTRACT_V12 = "office-cycle-v9"` and a `tree_problem` validator on the road_problem pattern. The generator seals the tree — **the redrawn tree of Amendment 1**, as data: node ids, names, dependencies, and each node's workaround text (INDEX 572) — as a `tree` declaration beside `presentation` and `road`, only where the contract is v9. The sealed tree for the standing job:

```
THE BRIEF — filed at scratch/brief.md
├─ 1. KNOW THE JOB  (the onboarding)
├─ 2. GATHER + JOURNAL — per file: read it, then journal your bit
│    ├─ 2.1 stock-take.md — read whole → journal bit
│    ├─ 2.2 a3-pass.md — read whole → journal bit
│    └─ 2.3 index-tail.md — read in parts → journal bit when whole
├─ 3. SUMMARIZE — read the journal whole; compile the bits into the brief
│      (the four points live here as content requirements:
│       what it is / proven / unproven / next step)
└─ 4. DELIVER — contribute the brief; the office files it
       depends on: 2.1–2.3 journaled, and 3
```

- **S2 — The state computation.** One function, record in → node states out. Gather nodes: done when the source stands held whole (the INDEX 552 standing computation) **and** its journal bit stands appended (INDEX 575's gate: a gather step completes on its read standing AND its journal bits written); the node's fact line carries reads charged vs bound. Branch-1 nodes: done as their stages stand acknowledged in the record. Summarize: *current* once every gather node stands done; done when the brief stands contributed from the journal compile — the recorded act, per Vane's rule. Deliver: done when the brief stands filed. Blocked: a node whose dependency stands unfilled shows blocked with the unfilled dependency named — one fixed wording per condition, written once in the contract's code, facts filled from the record.
- **S3 — Render.** `_build_cycle_package` renders the tree block for v9 packages only, from S2's computation, before the presentation hash. v1–v8 rendering is byte-untouched.
- **S4 — The speaking refusal.** Where the loop presents a REJECTION whose ground is a read tool's exhausted bound, the presented outcome carries the correction from S2's computation: the bound and its count, the sources already held whole, and the open next step. The REJECTION event and its ground are unchanged — this is presentation of an existing fact, not new enforcement.
- **S5 — Stocking.** At the site S0 finds, run setup creates `scratch/journal.md` empty **if absent** — idempotent, never overwriting (Vane's protection). Verified by a generation run twice over the same room.
- **S6 — The driver + the scenario.** demo_run.py seals v9 at its two generate sites and its verify-config assertion — **for the Nemotron live configuration**; the Groq seat stays on v8 until its own proof (the acceptance names one cold Nemotron run; other seats are not silently moved). The rehearsal gains the scripted re-read scenario: a worker script that reads a source whole, then re-reads past the bound — asserting the tree showed the source held *before* the attempt, the refusal carried the correction, and both match the record. Full rehearsal and the pre-existing suites run green as regression proof.
- **S7 — Acceptance.** Stage 1: S6's scenario green, whole. Stage 2: one cold Nemotron run (next free demo number), watcher launched with the driver, road seal unchanged at 120,000. Verdict in Ben's terms as scoped: a filed brief, or a failure that departs from a tree that told him true.

## Part 4 — What this build does not touch

`road.py` and the adapter's governed call; the doorway's enforcement, grounds, and bounds; every grant value; the delivery contract (`contribution-v1`) and the brief's resting places; the checker's derivations (v9 stands `presentation_contract_unknown` there, named, deferred); every other seat's contract; the rehearsal's existing scenarios. If a step discovers it *must* touch one of these, work stops and the plan comes back to Ben — that is what the plan is for.

## Sequencing note

Foundations before what consumes them: S2 before S3/S4 (both consume it), S0 before everything. The build is Remmy's own hands, per the standing order for this line. Whether this plan goes to Vane for examination before the build is Ben's call — the programme's pattern says yes; the refined scope she already examined says the shape is settled; the plan adds no new design, only the map and the order.
