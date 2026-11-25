# The process tree — design (2026-11-25, Ben's direction; Remmy's design, for his ruling)

**Status: DESIGN ONLY.** Ben's direction (2026-11-25 01:34 MST): "We should just design this process tree anyway.. That can be part of his onboarding." This note is the paper. No build is authorised by it; the build is a separate step, sequenced after the round-ten build (INDEX 552) lands and verifies, because both touch the loop's presentation layer.

## The gap it closes (INDEX 553)

The governing design (INDEX 457/459, SESH): the ternary designs work as process trees; each briefcase carries the whole tree with the worker's task highlighted. Gary has never been given one — he receives an assignment paragraph and a staged walk. The stages are the tree's shadow without the tree: no whole visible at once, no dependencies drawn, no position in the work's own structure.

## The tree for this job (the standing test assignment)

```
THE BRIEF — delivered and filed at scratch/brief.md
│
├─ 1. KNOW THE JOB  (the onboarding walk)
│    ├─ 1.1 Snapshot — what was settled before you woke
│    ├─ 1.2 Your memory — what this role knows
│    ├─ 1.3 Your case — your part, the evidence boundary, how delivery works
│    ├─ 1.4 Your files — the map, the worked example, the ways in
│    └─ 1.5 Your task — the assignment itself
│
├─ 2. GATHER  (the evidence the brief must rest on)
│    ├─ 2.1 sources/stock-take.md — pulled whole
│    ├─ 2.2 sources/a3-pass.md — pulled whole
│    └─ 2.3 sources/index-tail.md — pulled whole
│
├─ 3. COMPOSE  (about 600 words, plain, nothing invented)
│    ├─ 3.1 What the framework is
│    ├─ 3.2 What has actually been proven
│    ├─ 3.3 What is unproven and open
│    └─ 3.4 The honest next step
│
└─ 4. DELIVER
     ├─ 4.1 Contribute the brief
     │      depends on: 2.1, 2.2, 2.3 standing complete
     └─ 4.2 The office files it at scratch/brief.md
```

## The design decisions

1. **The tree is part of his onboarding — the whole of it, from the first wake.** Ben's words place it there. The staged walk already visits branch 1 in order; the change is that the worker SEES the whole tree while he walks it: at his first wake the snapshot is followed by the tree entire, his branch lit. Onboarding stops being a corridor and becomes a map he is standing in.
2. **Every package shows the tree with his position and the nodes' states** — pending, current, done — in place of the bare step position the dashboard carries now. A glance tells him what the job is, where he is, and what remains.
3. **Node states derive from the record, never from a second account.** Gather nodes stand done exactly when the INDEX 552 standing computation says the source's whole content stands in his working set; branch 1's nodes complete as their stages are acknowledged; deliver's dependency state is the gate's own state. The tree is a VIEW over the record — the same presentation-commitment machinery (INDEX 546/550) can bind what was shown, and the checker can verify the shown states against the record.
4. **The dependency edge is drawn before it can bite.** Deliver's lock is visible on the tree from the first wake — he can see 4.1 hangs on 2.1–2.3 before he ever reaches the door. When a gate does fire, the next package's tree shows exactly which nodes stand unfilled. The gate stops being a refusal that arrives from nowhere; it is the tree keeping its own shape, which he has been looking at all along.
5. **The tree is office-authored, sealed in the case at assembly** — designed by the ternary for the job, as the vision holds; the worker reads it and works it, he does not draw it. Its shape is general: a node carries a name, what done looks like, and its dependencies. Depth and breadth are the job's, not a fixed template.
6. **The crew consequence, noted not built:** one shared tree, different branches highlighted per worker, is the same object INDEX 545's shared base memory and INDEX 480's group job need — the tree is the shared map a crew works from, and node states are how collaborators see each other's progress without a word. The single-worker build should not pre-decide the crew's form, but it must not preclude it either: states derive from the record, and the record is already shared.

## Sequencing

Round ten remains the INDEX 552 build's proof run (the gate is one edge of this tree, built first). The tree's build — presentation of the sealed tree + record-derived states in the staged packages, checker verification of the shown states — is briefed on top of that landed build, and round eleven is its proof. Folding the tree into the running build is possible only by stopping it; the design does not ask for that.
