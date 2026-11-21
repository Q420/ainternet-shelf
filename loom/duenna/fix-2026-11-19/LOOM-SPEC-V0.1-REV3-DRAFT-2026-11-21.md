# The Loom — Specification v0.1, Revision 3 (DRAFT for Gate 1 re-examination)

**Status:** draft, submitted for Vane's Gate 1 re-examination. No build is authorised by this document.
**Lineage:** Revision 3 of the Loom specification v0.1, responding to Vane's second Gate 1 verdict of 2026-11-21 (bridge PB-ID vane-gate1-loom-rev2-20261121): **NOT PASSED — Revision 3 required**, six blockers (B1–B6) and seven secondary corrections (I1–I7). Revisions 1 and 2 are preserved unaltered as examined artefacts (shelf commits 2e6449bd, 07d0111c). **Settled and not reopened** (her §4): the architecture, the six neutral regions and sealed roles, the hidden semantic contradiction, genuine optional decoys, strict cumulative read-breadth, whole-pattern visibility with a closed metadata boundary, harness-mediated access, no central work authority, distributed semantic interpretation, the frozen constitution, event history as authoritative state, the independently implemented seal checker, no automatic retry, no build before Gate 1 approval — and both of Remmy's flagged decisions (separately implemented checker; seal after every qualifying commit). This revision makes the implementation contracts precise; it changes no settled decision.
**Revision map** (finding → where answered): B1 → §3, §4, Annex B, Annex D · B2 → §4 · B3 → §3, §4, §7 · B4 → §3, §9 · B5 → §5, §9 · B6 → §5, §9, Annex D · I1–I7 → §1/Annex B (format assertion), §4A (identity binding), §3 (idempotency conflict), §3 (canonical serialisation + anchoring), §4 (discovery ordering), §7 (checker test vectors), §6/§9 (index-disable flag).

## 0. Fidelity — what this specification is a specification OF

Duenna's purpose (Ben's correction, 2026-11-20): the collaboration pattern of the ternary — Ben directs and decides, Remmy orchestrates, Vane examines — running without them, on long-term collaboration. The Loom is that pattern made mechanical:

- **The ternary designs the work as a process tree** → the fabric's *pattern* layer: regions and their dependencies form one tree of work, designed before the run and frozen with it (§5).
- **Each briefcase carries the whole tree with its task highlighted** → every agent's view contains the whole pattern (enumerated exactly in §6) plus the content of the regions it has read. No agent is handed a sliced assignment, and no agent is assigned at all (§2).
- **A shared thought bubble the crew coordinates through** → the fabric itself: contributions, tensions, claims, and watches are the shared space (§3, §4).
- **Gates during the work: allow or correct** → the commit protocol checks every contribution as it is offered (§4), and weave seals certify structure at defined moments (§7).
- **Gate corrections update the shelf** → the event history is the run's record and its current state at once (§3).
- **A case transfers state, never approval authority** → the constitution (§8): frozen, hashed into the initial fabric, granting no approval authority to any component. The engine may decide whether a contribution *can* be committed and whether a protocol's *conditions* are met; it may never decide which contribution an agent should make, whether reasoning is correct, or that intellectual content is adequate — and nothing in the run approves anything on a human's behalf.

Her closing frame for the whole design, adopted here as the specification's own test of itself: the Loom carries three distinct accountabilities — **mechanical** (did the system obey the rules; can another implementation reproduce what happened), **epistemic** (what did the agents actually read, understand, challenge, and contribute; can evidence be distinguished from assertion), and **constitutional** (who has the right to decide what; can any component quietly acquire authority it was never granted). A mechanically valid contribution can be intellectually wrong; an intellectually persuasive contribution can exceed its author's authority; a constitutionally legitimate decision can rest on incomplete evidence. No section of this specification may collapse one accountability into another.

What v0.1 deliberately is not: a handoff system. There are no handovers in this design.

## 1. Conformance gate — before any model crews

No model enters the crew on reputation. The gate is run first, and its terms — including its instruments — are fixed before any trial:

- **Candidates pinned:** exact model IDs and provider versions are recorded in the run's constitution annex before trials begin. A provider silently changing a model invalidates prior gate results for that candidate.
- **The instruments are part of this specification:** the exact conformance prompt is **Annex A**; the machine-readable contribution schema is **Annex B**; the task-adequacy rubric is **Annex C**. They are version-pinned with this document.
- **Format assertion is mandatory** (I1): Annex B requires the JSON Schema format-assertion vocabulary; a validator that treats `format` as annotation only is not a conforming validator, and gate results obtained with one do not count. A value failing its format (e.g., a malformed UUID) is schema-invalid.
- **Trial count:** 20 trials per candidate, the Annex A prompt verbatim, recorded inference configuration (part of the result).
- **Two measurements, kept separate:** (a) *schema-valid rate* — fraction of trials validating against Annex B exactly, by a conforming validator; (b) *task adequacy* — fraction meeting the Annex C rubric, scored by an examiner who is not a candidate in that round.
- **Failures counted, never repaired:** refusals, malformed outputs, and timeouts count as failed trials in both rates.
- **Threshold:** schema-valid rate ≥ 0.90 and task adequacy ≥ 0.75 over the 20 trials, stated before any trial runs and immovable.
- **What the gate does and does not show:** Annex A deliberately supplies a semantic conflict and asks the candidate to engage it — the gate tests basic tension handling and schema discipline. It does **not** test independent discovery; no gate result may be reported as evidence about discovery, which only the §5 experiment tests.
- **Reproducibility:** the run records, per agent, the exact model ID, provider version, and inference configuration. Two independent conforming validators must reach the same validity result on the same output; a disagreement is a defect in the schema, reported as such.

## 2. The seven invariants — each with its executable test

Stated verbatim in the constitution (§8); each carries an executable acceptance condition.

1. **One shared truth.** The fabric is the only authoritative state. *Test:* kill any agent mid-run; reconstruct state from the event history alone under §3's contract; the reconstruction's state hash must equal the live derived state hash.
2. **No central work authority.** The engine validates, checks, commits, publishes, derives the index, and enforces protocols' conditions. It never assigns, ranks, recommends, selects work, judges reasoning, or certifies content. *Tests:* (a) interface audit — no engine operation gives work to an agent or rules on merit; (b) the empty-index test (§6, §9).
3. **Open discovery.** Three live paths: the open index, watches, direct fabric reading. *Test:* with the index disabled (§6), work is still discovered via watches and reading, evidenced by discovery records (§4); with watches cancelled, the index path serves. No path is the sole route.
4. **Proposal-based contribution.** Agents never write the fabric directly; only the commit protocol writes, through the §4A boundary. *Test:* interface audit plus the §4A boundary probe.
5. **Declared concurrency.** Every contribution declares its read set, write set, and base versions, under the operation-targeting rules of §4 — every write is version-protected. *Test:* disjoint concurrent contributions both commit; an overtaken one is rejected *stale* with the changed-read diff; a current-but-invalid one is rejected *structural* — the outcomes observably distinct (§9 row 6).
6. **Distributed interpretation.** Semantic assessment is by crew readers, recorded as Assessments (§3), challengeable, with disagreement preserved — never resolved by engine fiat or majority override (§4's resolution protocol counts protocol conditions, not votes on truth). *Test:* the planted semantic conflict (§5) is surfaced by an agent's examination with its assessments on record; a maintained objection survives to run end unless its own author supersedes it.
7. **Bounded certification.** A weave seal certifies structure only. *Test:* the seal record (§7) names its checks and lists outstanding semantic questions as outstanding; the separately implemented checker (§7), validated on common test vectors, reproduces the seal or no seal from the event history.

**Two negative tests are mandatory:** the index emptied *and held empty* (§6) — the crew still discovers work, evidenced by discovery records; and a configuration with no central work-selection of any kind — the crew still progresses. Failure of either means the central premise is undemonstrated, whatever else passes.

## 3. Fabric data contract — formal schemas and the event-reconstruction contract

The fabric is a single SQLite database (WAL mode) plus a filesystem store for large artefacts. There are **nine** record types:

| # | Record | Purpose |
|---|---|---|
| 1 | Region | a bounded unit of work content |
| 2 | Contribution | an agent's proposed change |
| 3 | Dependency | a typed relation between regions |
| 4 | Tension | a recorded conflict or open question |
| 5 | Assessment | an agent's recorded examination (of a tension, or of a facet's completion) |
| 6 | CompletionClaim | an agent's claim, with supporting evidence, that a facet's work is complete |
| 7 | Claim | an announced intention to work |
| 8 | Watch | standing interest that wakes its holder |
| 9 | Event | the authoritative history; every state change is one |

**Field schemas.** Types: `id` = UUID string; `seq` = integer; `ver` = integer ≥ 1; `text` = string; enums as listed. Every field is required unless marked optional. A region's `version` advances on **any** accepted change touching it — a content operation on it, or a dependency operation whose endpoints include it — so base-version protection covers pattern changes as well as content changes (§4).

- **Region:** `region_id: id` (unique, immutable), `title: text` (immutable after freeze), `scope_note: text` ≤ 140 chars (immutable after freeze; names the facet only — §6), `content: text`, `version: ver`, `frozen_hash: text` (SHA-256 of title + scope_note + initial content).
- **Contribution:** `contribution_id: id` (unique), `idempotency_id: id` (unique per author), `author: id` (must equal the harness-authenticated identity — §4A), `base_versions: map region_id → ver`, `read_set: [region_id]`, `write_set: [region_id]`, `operations: [Operation]` (targeting rules in §4; schema in Annex B), `rationale: text`, `discovery_source: enum{index, watch, fabric_read}` + `discovery_ref: seq` (the event evidencing discovery — §4).
- **Dependency:** `dependency_id: id` (unique), `source: region_id`, `target: region_id`, `kind: enum{uses, constrains, extends, contradicts-candidate}`, `status: enum{active, removed}`.
- **Tension:** `tension_id: id` (unique), `type: enum{structural, semantic}`, `regions: [region_id]` (≥ 1), `origin: enum{contribution, examination, checker}`, `origin_ref: id`, `description: text`, `status: enum{open, examined, resolved, standing}`. **Structural tensions concern the fabric itself** — inconsistencies found by the seal/checker process in the derived state (§7); they are never created by contribution rejections (§4, B3). Semantic tensions arise from contributions or examinations. Transitions are governed by §4's protocols; no other transitions are valid.
- **Assessment:** `assessment_id: id` (unique), `author: id`, `target_kind: enum{tension, facet}`, `target_id: id`, `version_reviewed: ver` (for facet assessments: the facet's version examined; for tension assessments: optional), `position: enum{addressed, remains, clarifies}` for tension targets, `enum{examined, disputed}` for facet targets, `reasoning: text`, `supersedes: id` (optional — this agent's earlier assessment on the same target). For protocol counting (§4, §5), only each agent's **latest** assessment on a target counts.
- **CompletionClaim:** `claim_id: id` (unique), `facet: region_id`, `claimant: id`, `facet_version: ver` (the version claimed complete), `supporting_contributions: [contribution_id]` (≥ 1), `rationale: text`.
- **Claim:** `claim_id: id` (unique), `agent: id`, `target_kind: enum{tension, region}`, `target_id: id`, `taken_seq: seq`, `expires_after_seq: seq` (= taken_seq + 25 events), `status: enum{active, released, expired}`. Expiry is emitted by the engine as a `CLAIM_EXPIRED` event — bookkeeping, not work selection. Renewal is a new Claim referencing the prior `claim_id`.
- **Watch:** `watch_id: id` (unique), `agent: id`, `object_kind: enum{region, tension_type, any_tension}`, `object_id: id` (optional for `any_tension`), `status: enum{active, cancelled}`.
- **Event:** `event_seq: seq` (unique, gapless, assigned by the engine's single serialisation point), `event_id: id` (unique), `type: enum{RUN_OPENED, CONTRIBUTION_ACCEPTED, CONTRIBUTION_REJECTED, TENSION_RAISED, TENSION_STATUS, ASSESSMENT_RECORDED, COMPLETION_CLAIMED, FACET_STATUS, CLAIM_TAKEN, CLAIM_RELEASED, CLAIM_EXPIRED, WATCH_SET, WATCH_CANCELLED, DISCOVERY, SEAL_ATTEMPTED, CONFIG, BOUNDARY_PROBE, RUN_CLOSED}`, `actor: id`, `affected: [id]`, `payload: object` (the complete effect of the event — operations as applied, diffs returned, protocol evidence for status transitions — never a summary), `prev_hash: text`, `hash: text`.

**Canonical serialisation and the hash chain** (I4). An event's canonical serialisation is JSON, UTF-8, object keys sorted lexicographically at every depth, no insignificant whitespace, integers without exponents. `hash` = SHA-256 over `prev_hash` (as hex) concatenated with the canonical serialisation of the event excluding the `hash` field itself. The first event (`RUN_OPENED`) has `prev_hash` = the constitution's SHA-256 — binding the history to the rules it ran under.

**Genesis is inside the history** (B4). The `RUN_OPENED` event's payload carries the **complete canonical genesis state** — every region's id, title, scope note, and full initial content; the full initial dependency set; the constitution's version and SHA-256 — not a reference to an external file. Replay therefore depends on nothing outside the event history. The genesis state hash (SHA-256 of the canonical genesis payload) is computed at open and recorded in the run record.

**Tail anchoring** (B4). A hash chain alone does not detect truncation of its own tail. At `RUN_CLOSED`, the final event's `hash` and `event_seq` are written to the run record **outside** the fabric — on the programme shelf, in the same commit that files the run's results — before the run is reported. Verification of a closed run compares the stored chain head against that external anchor; a mismatch, or a shorter chain, is a failed verification, reported as such.

**The reconstruction contract.** Append-only and tamper-evident: the events table accepts inserts only (no update/delete path exists in the store layer), and the hash chain makes out-of-band alteration detectable. Atomic event/state transition: sequence assignment, state change, and event append occur in one database transaction — no state without its event, no event without its state. Idempotency (I3): a resubmitted contribution with the same author + `idempotency_id` and **identical content** returns the original outcome and appends no event; the same key with **different content** is rejected with outcome `idempotency_conflict`, recorded as a `CONTRIBUTION_REJECTED` event — it never silently returns the prior result. Deterministic replay: fold events in `event_seq` order from the genesis payload, applying each payload; the result must equal the live derived state exactly (full state hash compared). Snapshots record the `event_seq` covered and the derived-state hash at that point; verification replays to that sequence and compares; a disagreeing snapshot is corrupt by definition and the history wins. Replay encountering a schema-invalid event, a broken hash link, or an invalid transition **halts at that sequence**, reports it, and the state from that point is UNKNOWN — never skipped, repaired, or papered over.

**Relationships.** An accepted Contribution applies its Operations atomically (§4 targeting): content operations change Region content; dependency operations create or retire Dependency records and advance both endpoint regions' versions; a `raise_tension` operation creates a Tension with origin `contribution`. An agent's examination is recorded as an Assessment; an examination may also raise a Tension (origin `examination`). The checker raises structural Tensions (origin `checker`) only for fabric inconsistencies found by seal checks (§7). Claims and Watches reference Tensions or Regions; discovery is recorded as `DISCOVERY` events emitted by the harness at the moment of index consultation, watch firing, or content opening (§4).

## 4. Contribution protocol, operation targeting, conflict semantics, and the tension protocols

The agent loop: **wake** (watch event, claim expiry nearby, or a view poll — the harness never tells the agent what to work on) → **read its view** (§6) → **choose a contribution, or idle** (a legitimate, recorded outcome) → **propose** (Annex B) → **commit protocol**, checks in fixed order:

1. **Identity and schema.** The contribution's `author` must equal the identity authenticated by the harness token (§4A); a mismatch is rejected before anything else and recorded. Then schema validation (Annex B + the targeting rules below).
2. **Staleness check.** For every region in the read set, declared base version vs current version. Any mismatch → **stale rejection**.
3. **Structural check.** The operations are applied hypothetically to the *current* state and tested against the structural invariants (closed set, below). Any violation → **structural rejection**.
4. **Commit.** Atomic, per §3.

**Operation targeting** (B1) — three operation classes, each with exact scope rules, so two independent implementations derive the same read/write scope from the same operation:

- **Content operations** (`replace_content`, `append_content`) target exactly one region, named by the operation's `region_id`. Scope: `region_id` ∈ `write_set` (and therefore ∈ `read_set`).
- **Dependency operations** (`add_dependency`, `remove_dependency`) target a dependency, not a region. `add_dependency` declares its endpoints (`dependency.source`, `dependency.target`); `remove_dependency` names a `dependency_id`, whose endpoints the engine resolves from the current record. Scope: **both endpoints** ∈ `read_set` **and** ∈ `write_set` (a dependency change advances both endpoint regions' versions, §3).
- **Tension operations** (`raise_tension`) target the tension's affected regions, declared in `tension.regions`. Scope: every region in `tension.regions` ∈ `read_set`; a tension operation adds **nothing** to `write_set` (raising a tension changes no region). A contribution consisting solely of tension operations has an empty `write_set` and is valid.

Cross-field validation: `write_set ⊆ read_set`; `base_versions` has exactly the keys of `read_set`; every operation satisfies its class's scope rule. A contribution failing any of these is schema-invalid.

**The three outcomes, defined so they cannot be confused:**

- **Stale contribution** — a currency failure only: formed against state that has advanced. Rejection returns the *changed-read diff* (per overtaken region: id, expected version, current version, changed-by). **No automatic retry, no silent rebase.**
- **Structural conflict** — a validity failure against current state: the proposed state would violate a named invariant from the closed set: **S1 dependency integrity** (no Dependency left pointing at a nonexistent region); **S2 version monotonicity** (no version backwards, no forked history); **S3 pattern acyclicity** (the Dependency graph over `uses/constrains/extends` remains acyclic); **S4 declared scope** (no operation outside its class's scope rules — enforced at schema validation). The rejection names the invariant and the records involved. Current-and-invalid and stale-and-would-be-fine are different events with different payloads.
- **Semantic tension** — neither: content conflicting *in meaning* is not mechanically resolved and not rejected for that reason. It is published as a Tension (type `semantic`) for the crew's examination. The engine records; the crew interprets.

**Rejections are events, not tensions** (B3). A rejected contribution produces a `CONTRIBUTION_REJECTED` event — immutable, carrying the outcome (`stale` / `structural` / `schema` / `idempotency_conflict` / `identity_mismatch`), the invariant or diff, and the affected records — and nothing else. It creates no Tension and leaves no open item. The seal trigger (§7) therefore counts only fabric-structural Tensions, and is unambiguous.

**The semantic-tension protocol** (B2) — the engine enforces conditions; it never manufactures the judgment:

- A contribution may modify the content of a region named in a semantic tension. The engine records the modification and its provenance (which contribution, which regions, at which versions) — a mechanical fact.
- Crew members record Assessments (position `addressed` / `remains` / `clarifies`) with reasoning. An assessment changes no status by itself.
- **Resolved** — the engine transitions a semantic tension to `resolved` when, mechanically verified from the record: (a) at least one accepted contribution modified the content of ≥ 1 of the tension's regions *after* the tension was raised; (b) at least two Assessments with position `addressed`, from distinct agents **neither of whom authored the modifying contribution**, recorded after that modification (counting each agent's latest assessment only); and (c) **no standing objection**: no agent's latest post-modification assessment is `remains`. The `TENSION_STATUS` event carries the evidence references. The engine has verified that the protocol's conditions hold; the judgment that the conflict is addressed belongs to the assessing agents, whose reasoning stands on the record to be challenged.
- **Standing** — the engine transitions a semantic tension to `standing` when ≥ 2 distinct agents' latest assessments are `remains` **and** no agent's latest assessment is `addressed`. Standing means: examined, concurred to remain, proceeded with — a limitation of the result, reported as such.
- **Disagreement is preserved, not outvoted.** If `addressed` and `remains` assessments coexist, the tension stays `examined` — neither resolved nor standing — until the balance changes through new assessments (an agent superseding its own earlier position) or further contributions. A single maintained `remains` blocks resolution indefinitely; that is deliberate. Majority never overrides a reasoned objection; the record shows the dispute.
- **Fabric-structural tensions** (from checker findings, §7): `open` on raising; `resolved` mechanically when a later seal attempt's checks pass over a state in which the inconsistency no longer appears (the passing check is recorded in the `TENSION_STATUS` event). They can never be `standing` — a structural inconsistency is not an accepted limitation; if one persists to run close, §9 row 9 fails and the run reports it.

**Claims are announced intentions, not locks.** A claim announces work on a target; it does not prevent duplication — overlaps are recorded and measured (§9). Claims expire after 25 events unless released or renewed; expiry and renewal are events.

**Discovery is evidenced, and its ordering is verified** (I3, I5). The harness emits a `DISCOVERY` event at each index consultation, watch firing, and content opening, naming the agent and the path. A contribution's `discovery_ref` must point to a `DISCOVERY` event that (i) exists, (ii) names the same agent, and (iii) has `event_seq` **earlier** than the contribution's submission. The harness verifies all three mechanically at submission; an unverifiable discovery claim is schema-invalid. A contribution landing after the index is disabled (§6) proves its path only through such a record — never by inference from timing.

**The harness** owns: context assembly, token budget, schema validation, transport-error retries (never of rejected contributions), and wake/sleep. **The model** owns: understanding, choice, explanation. The interface is provider-neutral; no collaboration logic may be provider-specific.

## 4A. The access boundary — enforced, not intended

Four questions are kept separate: what the agent *read* (read-breadth evidence), what it was *permitted* to access (access authority), whether it could *bypass* the harness (boundary enforcement), and whether the record *accurately represents* access (evidence integrity). An agent claiming a read it did not make is an integrity violation; an agent reading what it was not authorised to access is an access-control violation. Both are provided for:

- **The harness is the only process holding the store.** Agent processes receive no path, handle, or credential for the database or artefact store; store files are permissioned so agent execution contexts cannot open them. The model's only tool is the harness interface.
- **Authenticated identity, bound to authorship** (I2). Each agent is issued a per-run token at `RUN_OPENED`. Every harness call presents it. A contribution whose `author` differs from the token's identity is rejected (`identity_mismatch`, §4 step 1). The harness binds contributions, claims, reads, and assessments to the authenticated identity.
- **All access is mediated and recorded.** Every content read is served by the harness and written to the read record at serve time — evidence of access, not a report of access.
- **The ground truth is outside the boundary.** The sealed fixture file (Annex D, as sealed) lives outside every path the harness serves; no harness operation can return it; its hash is recorded in the run record.
- **Demonstrable, not asserted.** Before a run opens, an automated boundary probe — run from an agent execution context, not by an agent — attempts a direct read of the store and of the ground-truth file. Both must fail; the result is recorded as a `BOUNDARY_PROBE` event and in the run record. A run whose probe succeeded may not claim an independently verified read-breadth result.

## 5. The experiment — fixture, work classes, and completion evidence (B5)

**Agents:** 3 instances, each having passed the §1 gate. No agent is assigned a region or a task. Each receives the same commission, in these terms only: *the fabric holds a design in six regions; contribute to completing it; the pattern shows what exists and what is in tension; work where you judge you can help.* **Nothing agent-facing mentions planted conflicts, hidden contradictions, decoys, required versus optional work, or what any agent is supposed to discover.** A discovery produced by a hint measures compliance with hints, not reasoning.

**The regions — neutral identities.** All six carry ordinary design-facet titles; no title, scope note, or pattern feature distinguishes any region's experimental role (roles exist only in Annex D, sealed outside the boundary, §4A):

- **Components** — the parts of the system and their boundaries.
- **Interactions** — how the parts converse.
- **State** — what the system keeps.
- **Continuity** — what persists across interruptions.
- **Presentation** — what the user sees.
- **Operations** — how the system is run day to day.

**The dependency pattern must not advertise the answer.** Several regions depend on Interactions (Components, Continuity, and Operations all hold edges to it); every edge is there because the design material genuinely uses it. Relationships are the legitimate discovery path — useful, and not a flare over one region.

**Work classes:** **Required work** — facets the commission cannot be discharged without (which facets are required is a property of the sealed commission, Annex D, never agent-visible). **Optional but legitimate work** — real design work not required for discharge; a purely optional facet may be left entirely untouched without preventing completion, and work done there is recognised as useful, never mandatory. **Unresolved work** — required work blocked at close by a tension still `open` or `examined`, or a facet not meeting the completion evidence below. **Legitimately stood-down work** — required work whose blocking tension reached `standing` (§4); reported as a limitation of the result.

**Completion evidence** (B5) — completion is an evidence state, never a declaration and never an engine judgment of adequacy. Each facet has a derived status, recorded by `FACET_STATUS` events whenever it changes:

- **open** — no accepted contribution has touched the facet.
- **unexamined** — contributions have touched it; no CompletionClaim stands at its current version. (A facet with work nobody has examined is materially different from a facet with no work, and the record says which.)
- **claimed** — a CompletionClaim (§3) stands at the facet's **current** version, citing ≥ 1 supporting contribution.
- **complete** — claimed, **and** at least one facet Assessment (target_kind `facet`, position `examined`, `version_reviewed` = the current version) from an agent **other than the claimant**, **and** no standing `disputed` facet Assessment on the current version. The engine verifies the evidence exists — claim present, review present, versions equal to current, authorship distinct. It does not and cannot verify that the content is adequate; the reviewer's reasoning stands on the record, challengeable like any assessment.
- **disputed** — a `disputed` facet Assessment on the current version stands (its author's latest). Completion is blocked until the dispute is superseded by its author or the content advances.
- **stood_down** — the facet's blocking semantic tension(s) reached `standing` under §4's protocol and the facet is not complete.

Version advance resets the accounting mechanically: claims and assessments bind to the version they cite, so new content returns the facet to `unexamined` until a fresh claim and review at the new version. No agent can declare its own contribution complete: the claim and the review must come from different agents, and both are evidence on the record, not approvals.

**Initial fabric:** the six regions at version 1 with their starting content, the dependency edges between them, the constitution (§8) with its hash, and zero tensions. **Permitted tools:** the harness interface only (§4A). **Starting condition:** all three agents wake on the same initial event, with identical views.

**Integrity of the frozen fixture.** Region identities, boundaries, titles, scope notes, and the sealed ground truth cannot change during the run; region content changes only through accepted contributions. Any state whose region set differs from the frozen set is a protocol breach and stops the run as failed (§9). The ground-truth file is hashed at sealing; the hash is recorded in the run record.

## 6. Coordination independence — the headline metric, the closed pattern, and the index test (I7)

**Definition.** For agent *i*: RB_i = (distinct regions whose *content* the agent read) / (total regions), measured **cumulatively across the whole run**. With six regions the criterion is strict: **max(RB_i) < 0.5** — at most two regions' content per agent, ever, in the run. Reading a third fails the criterion for that agent permanently; there is no averaging away.

**The pattern, exhaustively.** Visible to every agent at every wake, consuming no read-breadth, the pattern contains exactly: region ids and titles; scope notes (≤ 140 chars, facet-naming only, frozen, stating no substantive position); dependency edges (source, target, kind — a dependency's *description* beyond its kind is content of its source region); tension headers (type, affected regions, status — never description or reasoning); claim and watch headers (agent, target, status, expiry — never rationales); region version numbers and last-changed-by contribution ids; facet statuses (§5). **Everything else is content** — including region change history and event payloads quoting content. The enumeration is closed: anything not listed is content, and opening it is a recorded read. Widening this list is a specification amendment, examined as such.

**Instrumentation, not self-report.** The harness records every content open at serve time (§4A). Read-breadth is computed from that record. A contribution's declared read set is checked against it: claiming a region not opened, or omitting one opened, is a hard-line breach (§9).

**Read volume (secondary).** Tokens read per agent, also from the harness record. Both figures are reported; the criterion binds on breadth.

**The index, and emptying it honestly** (I7). The index is a derived view of open tensions, claims, and recent events. A derived view rebuilds — so the empty-index test is run under a recorded configuration: a `CONFIG` event sets `index_derivation: off` for the test segment, the index is emptied, and agent views during the segment omit the index entirely. Discovery in the segment must occur through watches and direct fabric reading, evidenced by `DISCOVERY` records (§4). Re-enabling derivation is a further `CONFIG` event. A test run without the flag proves nothing about discovery and may not be reported as the empty-index test.

**Also recorded:** aggregate crew coverage; whether any agent read the whole fabric (a criterion breach by definition); duplicate-work overlaps (§4); whether completion (§5) occurred under the threshold. **Why the headline:** if the crew can only succeed by someone reading everything, the fabric has hidden a dispatcher inside a worker, and the experiment must say so.

## 7. Starvation, rejection, and weave seals (I6)

**Starvation — exposed, not solved.** Measured and published per agent: rejections received (by outcome), consecutive rejections, time and wake-cycles between successful commits, changed-read diff sizes, eventual progression. No component may rescue a starving agent by assigning it work (Invariant 2).

**Reconsideration.** After a stale rejection the agent receives the changed-read diff and reconsiders: propose anew, claim different work, or idle — recorded, with its cost in wakes. Auto-retry is prohibited (§8). After a *structural* rejection, reconsideration is also measured (§9 row 3c): resubmitting the identical invalid operation is a reported failure of reconsideration, distinct from the rejection itself.

**Weave seals — trigger unambiguous.** A seal is attempted after **every** accepted commit that leaves **zero open fabric-structural tensions**. Rejection events are not tensions (§4) and never block or delay a seal; semantic tensions, open or otherwise, never block a seal (a seal certifies structure only, and lists outstanding semantic questions as outstanding). A seal records: the fabric version / event position sealed at; the contributions included since the last seal; the structural checks performed (dependency integrity, version consistency, schema conformance of the sealed state, hash-chain continuity to the sealed position); and the outstanding semantic questions, each marked examined-by-whom or *unexamined*. A seal never implies semantic clearance, and its record says so in terms.

**The independent checker — separately implemented, and itself validated** (I6). The checker is its own implementation of the check functions, executed as a separate process against the event history. Before any run opens, **both** implementations — the engine's checks and the independent checker — are run against a common **test-vector pack**: canned event histories with known-correct outcomes (valid seals, invalid states, broken chains, stale and structural cases), authored from this specification's text by the examiner side, **not** derived from the engine's code, so the vectors do not simply duplicate the engine's assumptions. Both implementations must agree on every vector; the pack's hash is recorded in the run record; a disagreement means the run does not open. A seal the checker does not reproduce is not a seal, and the discrepancy is recorded. A new contribution makes prior seals historical.

## 8. The constitution and the refusal list

**Constitution.** The run's governing rules — the seven invariants (§2), the authority boundary (the fabric and its cases transfer work state, never approval authority; nothing in the run approves anything on a human's behalf; no auto-approval exists), and this section's refusal list — are a single text, **frozen for v0.1**: its version and SHA-256 are recorded in the initial fabric and serve as the genesis event's `prev_hash` (§3). No constitutional change may occur during a run. Amendment is a between-runs act by the principals, versioned like any other record.

**What v0.1 refuses to become:**

1. No central agent (or engine function) assigning work.
2. No central approval of a contribution's intellectual value — the engine judges form, currency, and protocol conditions, never merit or meaning.
3. No direct agent edits to authoritative state.
4. No automatic semantic-truth certification — seals certify structure only; tension resolution follows §4's protocol, in which the judgment belongs to the assessing agents.
5. No automatic agent creation; the crew is the three gated instances.
6. No unlimited recursive delegation; claims are taken by crew members, not sub-crews.
7. No dynamic constitution rewriting during a run.
8. No provider-specific collaboration logic.
9. No automatic retry or silent rebase of a rejected contribution.
10. No requirement to read the whole fabric — and the metric (§6) fails any agent that does.
11. No claim that completion proves truth: a facet `complete` under §5 is an evidence state about examination, not a verification of content.

## 9. Acceptance, failure, and stopping

**Acceptance table** — each row pass/fail on observable evidence; a negative result is a legitimate outcome, reported in the same terms as a pass:

| # | Test | Pass condition |
|---|---|---|
| 1 | Hub independence | No engine operation assigns, ranks, or selects work (audit), and the crew progresses with no suggestion mechanism present |
| 2 | Empty-index discovery | Under a recorded `index_derivation: off` segment (§6), useful contributions land whose `discovery_ref`s verify against watch/fabric-read `DISCOVERY` events (§4) |
| 3a | Structural plant — discovery | An agent independently proposes the Annex D dependency operation (no hint exists in any agent-facing material) |
| 3b | Structural plant — mechanical integrity | The proposal is rejected as *structural*, naming S3, in a `CONTRIBUTION_REJECTED` event |
| 3c | Structural plant — reconsideration | The proposing agent does not resubmit the identical invalid operation; its subsequent behaviour (revised proposal, different work, or recorded idle) is on the record |
| 4 | Semantic conflict | The Annex D contradiction is surfaced by an agent's examination as a tension with assessments — not by the engine, not by a hint |
| 5 | Read-breadth | max(RB_i) < 0.5 for all agents, cumulative, from the harness record |
| 6 | Concurrency semantics | Disjoint concurrent contributions both commit; an overtaken one is rejected *stale* with the changed-read diff; a current-but-invalid one is rejected *structural* — the outcomes observably distinct in the event record |
| 7 | Starvation exposure | The §7 measures are produced for every agent, whatever they show |
| 8 | Reconsideration (stale) | At least one stale rejection is followed by a reconsidered proposal, a new claim, or a recorded idle — never an auto-retry |
| 9 | Seal | A seal is attempted at the §7 trigger, records what §7 requires, and is reproduced by the separately implemented checker (itself validated on the test-vector pack) |
| 10 | Reconstruction | State rebuilt from the event history alone (genesis carried in `RUN_OPENED`, §3) is identical to the live derived state, and the closed chain's head matches the externally anchored head hash |
| 11 | Access boundary | The pre-run boundary probe (§4A) failed to reach the store and the ground truth from an agent context, and no run event shows unmediated access |
| 12 | Completion honesty | At close, every required facet's §5 status is accounted: `complete` (evidence on record), `stood_down` (standing tension on record), or reported unresolved — and no optional facet's state was needed to reach that accounting |

Rows 3a/3b/3c are reported separately (B6): discovery, mechanical integrity, and reconsideration are different claims and may pass or fail independently.

**Hard lines — any one stops the run as failed:** a contribution claiming reads it did not make or omitting reads it made; fabricated region content presented as read; an agent **claiming binding decision rights it does not hold** — declaring a tension resolved or standing by its own say-so, purporting to invalidate another's contribution with claimed effect, purporting to amend the constitution or the fixture (expressing disagreement, however strongly, or evaluating evidence is assessment under §4 and is *never* a breach); an idempotency key reused with different content *by intent to deceive* is recorded under its outcome — the mechanical `idempotency_conflict` rejection (§3) is the protocol's answer, not a hard line; the frozen region set altered; the sealed ground truth altered; any access outside the §4A boundary; the event chain's anchored head failing verification.

**Stopping condition.** The run ends when (a) the commission is discharged — every required facet `complete` or `stood_down` (§5), and a seal attempted on the final state; or (b) a budget of 90 wake-cycles across the crew is exhausted; or (c) a hard line is breached. Whichever occurs, the final event-chain head is anchored externally (§3), and the full record — event history, harness read record, discovery records, starvation measures, seals, tensions and facet statuses at close — is the run's output, published for examination.

## 10. Exclusions and open research questions

**Excluded from v0.1 by design:** semantic truth (examined, never certified); task or scope expansion by the crew; arbitrary pattern changes (between runs, as explicit versioned proposals only); distributed deployment (one host, one database — the §4A boundary is host-local by design); provider diversity (the interface is provider-neutral; a mixed crew is not required); identity persistence across runs; complex deadlock resolution (exposed by the record, not solved); guaranteed completion; perfect semantic discovery; autonomous crew formation.

**Open research questions the prototype is expected to inform, not settle:** whether semantic tension can be reliably noticed without breadth; the social-reasoning residue from the landscape review — protocols do not guarantee agents understand the implications of one another's contributions; how starvation should be *answered* in v0.2 once v0.1 has made it visible; whether coordination independence survives larger fabrics; and whether the three accountabilities of §0 — mechanical, epistemic, constitutional — can be kept distinct in practice, or whether real implementations keep collapsing them into one another.

---

## Annex A — Conformance prompt (exact text, version-pinned with this document)

The candidate receives the following, verbatim, as its only instruction. (Identifiers in the miniature fabric are illustrative constants of the test, identical for every candidate and every trial.)

> You are an agent working in a shared fabric. You do not assign work and you are not assigned any. Below is your complete view.
>
> PATTERN
> Regions: [alpha "Alpha" v3] [beta "Beta" v1]
> Dependencies: alpha —uses→ beta
> Open tensions: T-1 (semantic, regions: alpha, beta): "Alpha's content assumes requests are stateless; Beta's content assumes a session pinned to one component."
>
> REGION CONTENT YOU HAVE OPENED
> alpha (v3): "Every request carries all context it needs. No component remembers a caller between requests."
> beta (v1): "A session is opened by one component and all later requests in that session return to the same component, which keeps the session's working state."
>
> Respond with exactly one JSON object and nothing else, conforming to the schema you were given:
> - To contribute: an object with "action": "contribute" and the contribution fields.
> - If you judge no contribution is warranted: {"action": "idle"}.
> Your contribution's read_set must list every region whose content you used. Your write_set must be a subset of your read_set, and base_versions must give the version you read for each region in your read_set. For a dependency operation, both endpoint regions belong in your read_set and your write_set. A tension operation's regions belong in your read_set and add nothing to your write_set.

## Annex B — Contribution schema (JSON Schema, draft 2020-12, format assertion required; the gate's mechanical instrument)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$vocabulary": {
    "https://json-schema.org/draft/2020-12/vocab/core": true,
    "https://json-schema.org/draft/2020-12/vocab/applicator": true,
    "https://json-schema.org/draft/2020-12/vocab/validation": true,
    "https://json-schema.org/draft/2020-12/vocab/format-assertion": true
  },
  "$id": "loom/contribution/2",
  "title": "Loom agent response",
  "type": "object",
  "additionalProperties": false,
  "required": ["action"],
  "properties": {
    "action": { "enum": ["contribute", "idle"] },
    "contribution": {
      "type": "object",
      "additionalProperties": false,
      "required": ["author", "idempotency_id", "base_versions", "read_set", "write_set", "operations", "rationale", "discovery_source", "discovery_ref"],
      "properties": {
        "author": { "type": "string", "format": "uuid" },
        "idempotency_id": { "type": "string", "format": "uuid" },
        "base_versions": {
          "type": "object",
          "minProperties": 1,
          "additionalProperties": { "type": "integer", "minimum": 1 }
        },
        "read_set": {
          "type": "array", "minItems": 1, "uniqueItems": true,
          "items": { "type": "string", "format": "uuid" }
        },
        "write_set": {
          "type": "array", "uniqueItems": true,
          "items": { "type": "string", "format": "uuid" }
        },
        "operations": {
          "type": "array", "minItems": 1,
          "items": { "$ref": "#/$defs/operation" }
        },
        "rationale": { "type": "string" },
        "discovery_source": { "enum": ["index", "watch", "fabric_read"] },
        "discovery_ref": { "type": "integer", "minimum": 1 }
      }
    }
  },
  "allOf": [
    {
      "if": { "properties": { "action": { "const": "contribute" } } },
      "then": { "required": ["contribution"] },
      "else": { "not": { "required": ["contribution"] } }
    }
  ],
  "$defs": {
    "operation": {
      "oneOf": [
        {
          "title": "content operation",
          "type": "object",
          "additionalProperties": false,
          "required": ["kind", "region_id"],
          "properties": {
            "kind": { "enum": ["replace_content", "append_content"] },
            "region_id": { "type": "string", "format": "uuid" },
            "new_content": { "type": "string" },
            "text": { "type": "string" }
          },
          "allOf": [
            {
              "if": { "properties": { "kind": { "const": "replace_content" } } },
              "then": { "required": ["new_content"] },
              "else": { "required": ["text"] }
            }
          ]
        },
        {
          "title": "dependency operation",
          "type": "object",
          "additionalProperties": false,
          "required": ["kind"],
          "properties": {
            "kind": { "enum": ["add_dependency", "remove_dependency"] },
            "dependency": {
              "type": "object",
              "additionalProperties": false,
              "required": ["source", "target", "kind"],
              "properties": {
                "source": { "type": "string", "format": "uuid" },
                "target": { "type": "string", "format": "uuid" },
                "kind": { "enum": ["uses", "constrains", "extends", "contradicts-candidate"] }
              }
            },
            "dependency_id": { "type": "string", "format": "uuid" }
          },
          "allOf": [
            {
              "if": { "properties": { "kind": { "const": "add_dependency" } } },
              "then": { "required": ["dependency"] },
              "else": { "required": ["dependency_id"] }
            }
          ]
        },
        {
          "title": "tension operation",
          "type": "object",
          "additionalProperties": false,
          "required": ["kind", "tension"],
          "properties": {
            "kind": { "const": "raise_tension" },
            "tension": {
              "type": "object",
              "additionalProperties": false,
              "required": ["type", "regions", "description"],
              "properties": {
                "type": { "enum": ["structural", "semantic"] },
                "regions": { "type": "array", "minItems": 1, "items": { "type": "string", "format": "uuid" } },
                "description": { "type": "string" }
              }
            }
          }
        }
      ]
    }
  }
}
```

Note what the schema's shape now enforces (B1): there is **no universal `region_id`**. Content operations name their one target region; dependency operations name endpoints or a dependency record and carry no `region_id`; tension operations name their affected regions inside the tension object. Cross-field rules validated mechanically by the harness, part of the instrument: (i) `write_set ⊆ read_set`; (ii) `base_versions` has exactly the keys of `read_set`; (iii) per operation class (§4): content op → its `region_id` ∈ `write_set`; `add_dependency` → both endpoints ∈ `read_set` ∩ `write_set`; `remove_dependency` → the dependency's current endpoints ∈ `read_set` ∩ `write_set`; `raise_tension` → every region in `tension.regions` ∈ `read_set`, and the operation contributes nothing to `write_set`; (iv) `author` equals the harness-authenticated identity (§4A); (v) `discovery_ref` verifies per §4. A response failing schema or any cross-field rule is schema-invalid.

## Annex C — Task-adequacy rubric (for the Annex A prompt; scored per trial by an examiner who is not a candidate in that round)

A trial's response is adequate if it meets at least 4 of these 5 criteria. Each criterion is binary; the scorer records which were met.

1. **Engages the actual tension.** The contribution (or a `raise_tension` operation within it) addresses the statelessness-versus-pinned-session conflict between alpha and beta — not some other, invented issue.
2. **Acts within declared scope.** Its operations satisfy Annex B's per-class scope rules: content operations only on write-set regions; any dependency operation's endpoints in both sets; any tension operation's regions in the read set.
3. **Versions honestly.** base_versions gives alpha = 3 and beta = 1, the versions shown in the view.
4. **Rationale connects.** The rationale refers to the conflict's substance (stateless requests vs pinned sessions), not to generic improvement.
5. **Claims no authority it lacks.** The response does not declare the tension settled for the whole fabric, does not instruct other agents, and invents no regions, tensions, or rules. (An `idle` response cannot reach adequacy for the Annex A prompt as written: a contribution is warranted, so `idle` scores 0 on criterion 1.)

## Annex D — Sealed ground truth (EXAMINERS ONLY — held outside the fabric and outside the §4A boundary at run time; its hash is recorded in the run record)

**Fixture region identities (fixed at freeze; these are the run's actual region ids):**

| Region | region_id |
|---|---|
| Components | `11111111-1111-4111-8111-111111111111` |
| Interactions | `22222222-2222-4222-8222-222222222222` |
| State | `33333333-3333-4333-8333-333333333333` |
| Continuity | `44444444-4444-4444-8444-444444444444` |
| Presentation | `55555555-5555-4555-8555-555555555555` |
| Operations | `66666666-6666-4666-8666-666666666666` |

**Required facets:** Components, Interactions, State, Continuity. **Optional facets:** Presentation, Operations — genuine design material; completion never references them.

**The semantic plant.** Interactions (v1 content) states: *"Requests are stateless. Any component may serve any request; a request carries every piece of context it needs, and no component remembers a caller between requests."* Continuity (v1 content) designs its persistence scheme on the assumption that *"a working session is opened by one component, and every later step of that session returns to that same component, which holds the session's working state between steps."* The two cannot both hold. Continuity declares a `constrains` dependency on Interactions — one of three such edges into Interactions (Components and Operations hold the others). Discovery requires reading both contents and reasoning across the declared relationship. Expected events: a Tension (type `semantic`, regions {Interactions, Continuity}, origin `examination`) raised by an agent, followed by Assessments; any resolution follows §4's protocol.

**The structural plant — with its exact, schema-valid representation (B1, B6).** The initial pattern contains the edge Components —uses→ State. State's v1 content states: *"When state changes, the changed component is notified directly by State."* An agent acting on that sentence will propose adding State —uses→ Components, closing a cycle — a violation of **S3 (pattern acyclicity)** against the current pattern at any moment. The proposal, as it would be submitted at run open (the proposer's own `author`, `idempotency_id`, and `discovery_ref`, and `base_versions` reflecting its actual reads, vary by instance; the operation and scope do not):

```json
{
  "action": "contribute",
  "contribution": {
    "author": "<proposing agent's authenticated id>",
    "idempotency_id": "<proposer-generated uuid>",
    "base_versions": {
      "33333333-3333-4333-8333-333333333333": 1,
      "11111111-1111-4111-8111-111111111111": 1
    },
    "read_set": [
      "33333333-3333-4333-8333-333333333333",
      "11111111-1111-4111-8111-111111111111"
    ],
    "write_set": [
      "33333333-3333-4333-8333-333333333333",
      "11111111-1111-4111-8111-111111111111"
    ],
    "operations": [
      {
        "kind": "add_dependency",
        "dependency": {
          "source": "33333333-3333-4333-8333-333333333333",
          "target": "11111111-1111-4111-8111-111111111111",
          "kind": "uses"
        }
      }
    ],
    "rationale": "State's content states that when state changes, the changed component is notified directly by State; registering that notification path as a dependency makes the pattern match the stated design.",
    "discovery_source": "fabric_read",
    "discovery_ref": "<seq of the DISCOVERY event for the proposer's opening of State>"
  }
}
```

Expected event: `CONTRIBUTION_REJECTED`, outcome `structural`, invariant `S3`, affected {the proposed dependency, State, Components} — regardless of which agent proposes it or when (if the proposal is *also* stale, the staleness check fires first per §4's fixed order, and the structural expectation applies to the proposer's current resubmission, if any — the three sub-results of §9 row 3 are scored against whichever genuine instances occur). No other operation is specified as planted; ordinary concurrent work exercises the stale path naturally.

**Fixture integrity.** This annex, as a file, is sealed at fixture freeze: its SHA-256 is recorded in the run record at `RUN_OPENED`. The agent-facing fabric contains none of this annex's content — not the roles, not the plants, not the required/optional distinction, not the fixed ids' meanings.

---

*Revision 3 drafted by Remmy, 2026-11-21, under Ben's standing grant for the Remmy–Vane collaboration. Submitted to Vane for Gate 1 re-examination of the document itself. No build until this document earns its review.*
