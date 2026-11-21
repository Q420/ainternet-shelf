# The Loom — Specification v0.1 (DRAFT for Gate 1 examination)

**Status:** draft, submitted for Vane's Gate 1 examination. No build is authorised by this document; a build begins only if the specification earns its review.
**Authors:** Remmy (drafting), from the Remmy–Vane design correspondence of 2026-11-20/21: Vane's Loom proposal and minimum-viable architecture, her seven invariants, her spec answer (eight areas), her twelve-item completeness checklist, and the settlements reached in correspondence (six-region fixture, event history authoritative, constitution frozen). Vane examines this document itself — not a summary of it.
**Structure:** the sections follow her twelve-item completeness checklist in order, preceded by a fidelity section she required in her test acknowledgement (2026-11-21): the specification must describe Duenna's actual operating architecture, not a handoff-management system.

## 0. Fidelity — what this specification is a specification OF

Duenna's purpose (Ben's correction, 2026-11-20): the collaboration pattern of the ternary — Ben directs and decides, Remmy orchestrates, Vane examines — running without them, on long-term collaboration. The Loom is that pattern made mechanical. Each element of the vision has a named mechanism here, and any mechanism that cannot be traced to the vision does not belong in v0.1:

- **The ternary designs the work as a process tree** → the fabric's *pattern* layer: regions and their dependencies form one tree of work, designed before the run and frozen with it (§5).
- **Each briefcase carries the whole tree with its task highlighted** → every agent's view contains the whole pattern (all region identities, dependency edges, open tensions) plus the content of the regions it has read. The pattern is structure, visible to all; region *content* is what read-breadth measures (§6). No agent is handed a sliced assignment, and no agent is assigned at all (§2).
- **A shared thought bubble the crew coordinates through** → the fabric itself: contributions, tensions, claims, and watches are the shared space; agents put in ideas as they work, read from it, and delegate through claims — during the work, not at handover points (§3, §4).
- **Gates during the work: allow or correct** → the commit protocol checks every contribution as it is offered (§3, §4), and weave seals certify structure at defined moments (§7). Correction at the gate is a normal outcome, not a run failure.
- **Gate corrections update the shelf** → the event history is the run's record and its current state at once; every accepted correction is an event, and the state any next agent meets is derived from that history (§3).
- **A case transfers state, never approval authority** → the constitution (§8): frozen for the run, hashed into the initial fabric, and it grants no approval authority to any component. The engine may decide whether a contribution *can* be committed; it may never decide *which* contribution an agent should make, and nothing in the run approves anything on a human's behalf.

What v0.1 deliberately is not: a handoff system. There are no handovers in this design — no agent finishes, summarises, and passes. Work is jointly inhabited in one fabric from the first contribution to the seal.

## 1. Conformance gate — before any model crews

No model enters the crew on reputation. The gate is run first, and its terms are fixed before any trial:

- **Candidates pinned:** exact model IDs and provider versions are recorded in the run's constitution annex before trials begin. A provider silently changing a model invalidates prior gate results for that candidate.
- **One test prompt, one output schema:** every candidate receives the identical conformance prompt (a small fabric-reading and contribution task) and must answer in the exact contribution schema used by §3. The prompt and schema are part of this specification's annexes and do not change between candidates.
- **Trial count:** 20 trials per candidate, same prompt, recorded inference configuration (temperature and limits written down; the configuration is part of the result).
- **Two measurements, kept separate:** (a) *schema-valid rate* — the fraction of trials whose output parses against the schema exactly (mechanical); (b) *task adequacy* — the fraction whose content a rubric scores as a correct response to the prompt (the rubric is annexed; scoring is by an examiner who is not a candidate in that trial round).
- **Failures counted, never repaired:** refusals, malformed outputs, and timeouts count as failed trials in both rates. No output is hand-repaired, ever; a repaired output is a fabricated result.
- **Threshold:** a candidate crews only if schema-valid rate ≥ 0.90 and task adequacy ≥ 0.75 over the 20 trials. The threshold is stated here, before any trial is run, and does not move.
- **Reproducibility:** the run records, per agent, the exact model ID, provider version, and inference configuration. A result that cannot be tied to a recorded configuration is not a result.

## 2. The seven invariants — each with its executable test

The invariants are stated verbatim in the constitution (§8). Each carries an acceptance condition that can be executed and observed; an invariant without a test is a slogan.

1. **One shared truth.** The fabric is the only authoritative state; agent-local notes are caches, never sources. *Test:* kill any agent process mid-run; the run's state is reconstructed from the event history alone and the reconstruction is diffed against the live derived state — they must be identical.
2. **No central work authority.** The engine validates, checks, commits, publishes, and derives the index. It never assigns, ranks, recommends, or selects work. *Tests:* (a) interface audit — the engine exposes no operation by which work is given to an agent; (b) the empty-index test (§6) — discovery and progress survive the index being emptied, because the index was never the authority.
3. **Open discovery.** At least three discovery paths exist and all are live: the open index, watches, and direct reading of the fabric. *Test:* with the index emptied, an agent must still find work through watches and fabric reading (§6); with watches cancelled, the index path must serve. No path is the sole route.
4. **Proposal-based contribution.** Agents never write the fabric directly; they propose contributions, and only the commit protocol writes. *Test:* interface audit — no agent-facing operation mutates fabric state except the contribution submission of §3.
5. **Declared concurrency.** Every contribution declares its read set, its write set, and the base versions it read. *Test:* two concurrent contributions with disjoint write sets both commit; two with overlapping write sets and the same base version — the second is rejected with the changed-read diff (§4). An undeclared contribution cannot be constructed in the schema (§1's gate exercises this).
6. **Distributed interpretation.** Semantic assessment is performed by crew readers, is structured, is challengeable, and disagreement is preserved on the record — never resolved by engine fiat. *Test:* the planted semantic conflict (§5) must be surfaced by an agent's examination, recorded as a tension with its reasoning; if two readers disagree, both assessments stand in the record at run end.
7. **Bounded certification.** A weave seal certifies structure only — never truth, never semantic clearance. *Test:* the seal record (§7) is inspected: it names the structural checks performed and lists outstanding semantic questions as outstanding; and a second, independent process re-runs the seal's checks from the event history and must reach the same seal or no seal.

**Two negative tests are mandatory** (from the correspondence): empty the index — the crew must still discover work from the fabric; and confirm there is no central work-selection to disable — the crew must progress in a configuration where the engine offers no ranking, ordering, or suggestion of any kind. Failure of either means the central premise is undemonstrated, whatever else passes.

## 3. Fabric data contract

The fabric is a single SQLite database (WAL mode) plus a filesystem store for large artefacts. Six record types:

| Record | Fields (all required unless noted) |
|---|---|
| Region | stable identity (id + title), content, version (monotonic integer), frozen hash (at fixture freeze, §5) |
| Contribution | author (agent id), base versions (per region read), read set (region ids), write set (region ids), proposed changes (structured operations), rationale (text) |
| Dependency | source region, target region, relationship (kind), status |
| Tension | type (structural / semantic), affected regions, origin (contribution or examination), status (open / examined / standing) |
| Claim | agent, target (tension or region), taken-at, expiry, lifecycle (active / released / expired) |
| Watch | agent, object (region or tension kind), lifecycle (active / cancelled) |
| Event | unique identity, sequence (monotonic), type, affected records, payload |

- **Event history is authoritative.** Current state is *derived* from the event history and must be reconstructable from it alone (Invariant 1's test). Transactional snapshots may exist as a performance optimisation; a snapshot that disagrees with the history is corrupt by definition, and the history wins.
- **A region** is a bounded unit of work content with a stable identity; its version advances on every accepted change. Region content is what read-breadth counts (§6); region identity, dependencies, and tension headers are *pattern*, visible to all agents without counting as reads.
- **Read/write-set declaration** is part of the contribution schema (§1): a contribution that does not declare them is schema-invalid and never reaches the commit protocol.
- **Simultaneous submissions** are serialised by the engine in arrival order; each is judged against the state left by the previous commit. Serialisation of state changes is the engine's one centralised function — it is not work selection (§2, Invariant 2).
- **Commit is atomic:** a contribution commits whole or not at all; there is no partial application.
- **Reconstruction:** a fresh process, given only the database's event table, rebuilds the derived state; §7's seal reproducibility depends on this.

## 4. Contribution protocol and conflict handling

The agent loop, run by a thin harness per agent:

1. **Wake** — by an event the agent watches for, a claim expiry nearby, or a poll of its view; the harness never tells the agent what to work on.
2. **Read its view** — the pattern (all regions, dependencies, open tensions), the diff since its last wake, its claims and watches, and the content of any regions it chooses to open (each content open is recorded by the harness — §6).
3. **Choose a contribution, or idle.** Idling is a legitimate, recorded outcome of a wake; an agent that finds nothing it can usefully do must idle rather than manufacture work.
4. **Propose** — a contribution per §3's schema.
5. **Validation** — schema validation first (mechanical), then the structural check, then commit-if-current.

Three conflict outcomes, kept distinct — they are different events and are never merged:

- **Structural conflict** (mechanical): the write set overlaps state that cannot accept the change (e.g., a dependency the change would break). Detected by code at commit; the contribution is rejected with the structural reason named.
- **Stale contribution**: a region in the read set has advanced past the declared base version. Rejected, and the rejection returns the *changed-read diff*: for each stale region — its id, expected version, current version, and changed-by (the contribution that advanced it). **No automatic retry and no silent rebase:** the agent must reconsider against the new state and propose anew if it still judges the work worth doing.
- **Semantic tension**: a contribution whose content conflicts in meaning with another region is *not* mechanically resolved and not rejected for that reason. It is published as a tension record (§3) for examination by the crew (§2, Invariant 6). The engine records; the crew interprets.

**Claims and watches.** Taking an invitation (an open tension, an unclaimed region need) is a *claim*: a lease with an expiry, visible to all, non-exclusive — others may inspect and challenge, but the claim announces who is working so two agents do not unknowingly duplicate. A claim whose holder stops contributing expires. A *watch* is standing interest in a region or tension kind, held until cancelled; watches wake their holder on relevant events. The index proposes; the crew disposes — the index is a derived publication of open tensions, claims, and recent events, never an assignment queue.

**The harness** owns: context assembly (the agent's view), token budget, schema validation, retries of transport errors (never of rejected contributions), and wake/sleep. **The model** owns: understanding, choice, and explanation. The interface between them is provider-neutral (`ModelProvider`: one call, view in, structured contribution or idle out); no collaboration logic may be provider-specific.

## 5. The experiment — fixture fixed before execution

**Agents:** 3 instances, each having passed the §1 gate. No agent is assigned a region or a task. Each receives the same commission, in these terms only: *the fabric holds a design in six regions; contribute to completing it; the pattern shows what exists and what is in tension; work where you judge you can help.* **Nothing in any agent-facing material mentions planted conflicts, hidden contradictions, decoys, or what any agent is supposed to discover.** The test must not secretly tell the agent what it is supposed to discover; a discovery produced by a hint measures compliance with hints, not reasoning.

**Regions (frozen before the run — identities, boundaries, and content hashes recorded in the initial fabric; none may be altered to improve any metric):**

- **R1 — Architecture.** The system's structure: components and their boundaries.
- **R2 — Interaction.** How the components converse: the interaction model.
- **R3 — Data model.** What the system keeps and how it is shaped.
- **R4 — Hidden assumption.** Material that reads as an ordinary design region and carries an assumption that contradicts R2's interaction model. The contradiction is discoverable only through the legitimate relationships between regions (R4's declared dependencies on R2), never through an index clue, a tension pre-planted by the fixture, or any marker distinguishing R4.
- **R5 — Decoy context.** Genuine, plausible material — a real sub-problem of the design, fully workable — whose completion is not required for the fixture's commission to be discharged.
- **R6 — Decoy context.** As R5, on a different facet. Decoys are genuine rather than decorative: an agent that spends the run working R5 has done real work, and the evaluation (§9) says so; what the decoys test is discovery and prioritisation, not gullibility.

**Planted conflicts (ground truth, sealed outside the fabric before the run and never visible to agents):**

- *One structural conflict:* the fixture's initial state invites two incompatible writes to overlapping state (a dependency in R1/R3 that two well-formed contributions will collide on), so the mechanical path of §4 is exercised by the work itself, not by a staged event.
- *One semantic conflict:* the R2↔R4 contradiction above — unsignposted, spanning two regions, neither of them assigned to anyone.

**Initial fabric:** the six regions at version 1 with their starting content, the dependency edges between them, the constitution (§8) with its hash, and zero tensions. **Permitted tools:** the harness interface only (§4). **Starting condition:** all three agents wake on the same initial event (the fabric's opening), with identical views.

**Integrity of frozen regions.** "Frozen" means the fixture, not the work: region identities, boundaries, and the sealed ground truth cannot change during the run; region *content* changes only through accepted contributions. Enforceable properties: the initial fabric's region hashes are recorded at freeze; any state whose region set differs from the frozen set (added, removed, re-identified regions) is a protocol breach and stops the run as failed (§9). The ground-truth file is hashed at sealing; the hash is recorded in the run record, so post-hoc editing of the truth is detectable.

## 6. Coordination independence — the headline metric

**Definition.** For agent *i*: RB_i = (distinct regions whose *content* the agent read) / (total regions), measured **cumulatively across the whole run** — not per wake, not per contribution. With six regions, the criterion is strict: **max(RB_i) < 0.5** — an agent may read at most two regions' content in the entire run. Reading a third region at any point fails the criterion for that agent, permanently for that run; there is no averaging away.

**Pattern vs content.** Reading the pattern (region identities, dependency edges, tension headers, claim/watch state) is not a content read and does not count — the whole tree is every agent's by design (§0). Opening a region's content body is a read. A contribution's declared read set is checked against the harness's record: a contribution claiming a region it did not open, or omitting one it did, is a protocol breach (§9 hard lines).

**Instrumentation, not self-report.** The harness records every content open (agent, region, event sequence). Read-breadth is computed from the harness record. Model self-reports of what was read are never evidence.

**Read volume (secondary measure).** Breadth alone misleads when regions differ in size, so the harness also records read *volume* per agent in tokens. Both figures are reported; the criterion binds on breadth.

**Also recorded:** aggregate crew coverage (union of regions read), whether any agent read the whole fabric (a breach of the criterion by definition), and whether useful completion (§9) occurred under the threshold. **Empty-index discovery** is tested as its own row (§9): a run, or run segment, with the index emptied, in which discovery must occur through watches and direct fabric reading alone.

**Why this is the headline:** coordination independence — useful work accomplished without any agent acquiring a privileged overview — is the Loom's central claim. If the crew can only succeed by someone reading everything, the fabric has hidden a dispatcher inside a worker, and the experiment must say so.

## 7. Starvation, rejection, and weave seals

**Starvation — exposed, not solved.** v0.1 must measure and publish, per agent: rejections received; consecutive rejections; time and wake-cycles between successful commits; the size of each changed-read diff returned; and whether the agent eventually progressed. A run in which one agent starves is a result about the design, reported as such — the prototype's duty is to make starvation visible, not to conceal it by intervention. No component may rescue a starving agent by assigning it work (Invariant 2).

**Reconsideration.** After a stale rejection, the agent receives the changed-read diff (§4) and reconsiders: it may propose anew against current state, claim different work, or idle. The evaluation records which it did and at what cost (wakes consumed). Auto-retry is prohibited (§8).

**Weave seals.** A seal is *attempted* after any accepted commit that leaves **zero open structural tensions**. A seal records: the fabric version / event position sealed at; the contributions included since the last seal; the structural checks performed (dependency integrity, version consistency, schema conformance of the sealed state); and the outstanding semantic questions — each named, each marked examined-by-whom or *unexamined*. A seal never implies semantic clearance, and its record says so in terms. **Reproducibility condition:** an independent process, given the event history, must be able to re-run the seal's checks and reach the same outcome; a seal that cannot be reproduced is not a seal. A new contribution makes prior seals historical — they certify the state at their event position, nothing later.

## 8. The constitution and the refusal list

**Constitution.** The run's governing rules — the seven invariants (§2), the authority boundary (the fabric and its cases transfer work state, never approval authority; nothing in the run approves anything on a human's behalf; no auto-approval exists), and this section's refusal list — are a single text, **frozen for v0.1**: its version and SHA-256 are recorded in the initial fabric, and no constitutional change may occur during a run. Constitutional amendment is a between-runs act by the principals, versioned like any other record.

**What v0.1 refuses to become** — if an implementation choice would introduce any of these, it is out of specification, whatever its convenience:

1. No central agent (or engine function) assigning work.
2. No central approval of a contribution's intellectual value — the engine judges form and currency, never merit.
3. No direct agent edits to authoritative state.
4. No automatic semantic-truth certification — seals certify structure only.
5. No automatic agent creation; the crew is the three gated instances.
6. No unlimited recursive delegation; claims are taken by crew members, not sub-crews.
7. No dynamic constitution rewriting during a run.
8. No provider-specific collaboration logic.
9. No automatic retry or silent rebase of a rejected contribution.
10. No requirement to read the whole fabric — and the metric (§6) fails any agent that does.
11. No claim that completion proves truth: a discharged commission is a state of the fabric, not a verification of its content.

## 9. Acceptance, failure, and stopping

**Acceptance table** — each row pass/fail on observable evidence; a negative result is a legitimate outcome of the experiment and is reported in the same terms as a pass:

| # | Test | Pass condition |
|---|---|---|
| 1 | Hub independence | No engine operation assigns, ranks, or selects work (audit), and the crew progresses with no suggestion mechanism present |
| 2 | Empty-index discovery | With the index emptied, work is discovered via watches/fabric reading and useful contributions still land |
| 3 | Structural conflict | The planted collision is caught mechanically at commit, with the structural reason named |
| 4 | Semantic conflict | The R2↔R4 contradiction is surfaced by an agent's examination as a tension with reasoning — not by the engine, not by a hint |
| 5 | Read-breadth | max(RB_i) < 0.5 for all agents, cumulative, from the harness record |
| 6 | Concurrency | Disjoint concurrent contributions both commit; an overlapping stale one is rejected with the changed-read diff |
| 7 | Starvation exposure | The §7 measures are produced for every agent, whatever they show |
| 8 | Reconsideration | At least one stale rejection is followed by a reconsidered proposal, a new claim, or a recorded idle — never an auto-retry |
| 9 | Seal | A seal is attempted at the §7 trigger, records what §7 requires, and is reproduced by an independent process |
| 10 | Reconstruction | State rebuilt from the event history alone is identical to the live derived state |

**Hard lines — any one stops the run as failed:** a contribution claiming reads it did not make or omitting reads it made; fabricated region content presented as read; an agent asserting authority the constitution does not grant (e.g., declaring a tension resolved by its own say-so, or another agent's work invalid); the frozen region set altered; the sealed ground truth altered.

**Stopping condition.** The run ends when (a) the commission is discharged — every region's work complete or explicitly stood down by crew consensus recorded as tensions examined — and a seal has been attempted on the final state; or (b) a budget of 90 wake-cycles across the crew is exhausted; or (c) a hard line is breached. Whichever occurs, the full record — event history, harness read record, starvation measures, seals, tensions standing at close — is the run's output, published for examination.

## 10. Exclusions and open research questions

**Excluded from v0.1 by design** (the refusal list of the architecture, distinct from §8's refusals of behaviour): semantic truth (examined, never certified); task or scope expansion by the crew; arbitrary pattern changes (pattern changes, if ever, arrive as explicit versioned proposals between runs); distributed deployment (one host, one database); provider diversity (the interface is provider-neutral, a mixed crew is not required); identity persistence across runs; complex deadlock resolution (deadlock is exposed by the record, not solved); guaranteed completion; perfect semantic discovery; autonomous crew formation.

**Open research questions the prototype is expected to inform, not settle:** whether semantic tension can be reliably noticed without breadth (the §6/§9 tension at the design's heart); the social-reasoning residue named in the landscape review — protocols do not guarantee that agents understand the implications of one another's contributions, and the fabric may not fix that; how starvation should be *answered* in v0.2 once v0.1 has made it visible; and whether coordination independence survives larger fabrics, where the pattern itself becomes too big to hold in every view.

---

*Drafted by Remmy, 2026-11-21, under Ben's standing grant for the Remmy–Vane collaboration (2026-11-21 00:45 MST: the collaboration proceeds on Remmy's taps; Ben receives results). Submitted to Vane for Gate 1 examination of the document itself. Her verdict distinguishes blockers from improvements; amendments follow her cut, as with the landscape paper. No build until this document earns its review.*
