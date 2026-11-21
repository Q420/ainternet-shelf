# Stage 4 — Build Notes

Built 2026-11-21 from the pinned dispatch brief
(`STAGE4-BUILD-DISPATCH-2026-11-21.md`). Authority set: Rev 9 spec
(§7 core), Amendment A1, settled Stage 4 Design Brief Rev 2, and the
PINNED examiner validation pack V2 (blob 02e47728, SHA-256
cce27ee70d6041955364169a6b46f59fe98153f2fe2a30dc315ce0a015eead71).
Base: the accepted Stage 3 code (build 1e69f5d3 + correction
57e081a3). Genesis state hash must remain `9a7250bde82bfd8b…`.

**This file's mapping table (section 4 below) was recorded BEFORE
the pack was executed against either implementation**, as the
dispatch brief requires (item 8). Results are appended in section 6
after execution; nothing in sections 1–5 was rewritten afterwards.

---

## 1. Interpretations

**I-1. The seal regime is bound at RUN_OPENED.** Seal attempts,
the structural lifecycle, and the close-time attempt apply exactly
to runs whose `RUN_OPENED` payload carries the Stage 4 binding
(the authority set Rev 9 + A1, separately identified, and the pack
identifier/version/SHA-256 — VP-55). A run opened without the
binding is governed by the authority its own RUN_OPENED names
(VP-15's principle: no run changes its authority set mid-run), and
its behaviour is bit-for-bit the accepted Stage 3 behaviour. This
is also what keeps every prior suite green unedited: none of them
opens a bound run. The fabric service opens a bound run when the
operator's `open_run` request carries `bind_stage4: true`; a
`pack_sha256` supplied alongside that differs from the pinned
digest refuses the opening (VP-55's "blocks run opening").

**I-2. Attempts attach to accepted contribution commits.** §7's
trigger is "after every accepted commit" — the §4 commit protocol,
whose subject is a Contribution. Examination, assessment, and
completion-claim groups (Stage 3) append no SEAL_ATTEMPTED. The
pack nowhere tests an attempt after a Stage 3 action; VP-30's
"accepted contribution" wording agrees.

**I-3. S2's seal form is the staged-transition property.** S2
(version monotonicity) is evaluated as: folding the staged batch B
over the committed history H must not decrease any region's
version. A live snapshot whose version merely differs from replay
— with no staged regression — is divergence, handled by the C1
rule as MISMATCH (pack §2 says exactly this). Consequence, stated
plainly: VP-18's `FAIL(S2)` branch is **unreachable through any
foldable history in this build**, because the fold's operations
only ever advance versions, so no staged batch can decrease one.
The S2 check runs in both implementations, identically, and would
fire on such a transition; the case's reachable expectations
(protocol rejection before acceptance; MISMATCH for a supplied
regressed snapshot) are what is executed. This is a limit of the
operation set, not a waiver of the case.

**I-4. Attempt evidence names the attempt by event_seq.** A
resolving `TENSION_STATUS` carries evidence
`{"seal_attempt_seq": N, "check": …, "affected": […]}` and a
checker-raised `TENSION_RAISED` carries
`origin_ref: "seal-attempt:<seq>"`. Event_seq is this system's
positional identity for an event (the same identity
`discovery_ref` uses in §4); event_id UUIDs are assigned by the
store at append time, after the group is planned, so a payload
planned inside the group cannot name them.

**I-5. TV-1's derived-state repair is a replay rebuild.** The
VP-45 fault lives only in the live derived state (the service's
in-memory fold). While it stands, no contribution can lawfully
mention the missing region (the schema's frozen set is read from
that same state), so the correcting contribution cannot be
submitted until the derived state is repaired. The repair is the
system's own invariant-1 act: rebuild the derived state from the
verified history (a service restart in the socket form; an
`engine.replay()` swap in the in-process form). The record —
including the open structural tension — is untouched by the
repair, and the first accepted contribution after it is the
correction itself, so the resolution is earned by the correcting
contribution and its passing attempt, exactly as VP-45 steps
(5)–(8) require. The repair step is disclosed wherever TV-1 is
demonstrated; it is never hidden inside the attempt.

**I-6. VP-03's native form.** An IDLE submission carries no actor
field in this system: authorship is the token, and the harness
records the IDLE event under the authenticated identity only. The
evaluator-level form of the case is therefore: a staged batch
containing an IDLE event whose actor differs from the
authenticated submitter named in the evaluation request is refused
by both evaluators (outcome `refused`, nothing folded, no seal).

**I-7. Check-level pack cases assert the named check's verdict.**
VP-17, VP-19, VP-21 are written about one check ("S1 passes",
"S2 passes", "S3 passes"). Their adapters assert the named check
produces no finding; the overall attempt outcome is recorded in
the manifest as observed. Where a case's input can be shaped so
the overall outcome also matches (L = R), it is.

**I-8. The checker's history input has two forms.** When the
event store is file-backed (every service deployment, and the
file-backed test stores), the harness hands the checker the store
path and the checker opens the database **read-only itself**
(SQLite `mode=ro`) — the service never vouches for the history.
For in-memory stores and for pack validation (where both
implementations must receive byte-identical inputs), the history
is supplied inline as data read from the store. The checker never
writes to the store in either form.

**I-9. Structural tension records carry their identity.** A
checker-raised tension's payload — and therefore its folded
record — carries `check` and `affected` (the canonically sorted
affected record set) alongside the §3 fields, so the identity the
lifecycle deduplicates and resolves against is itself part of the
record, reconstructible from the history alone. Semantic tensions
carry neither field; their folded records are unchanged.

**I-10. Findings are per inconsistency instance.** S1 yields one
finding per (dependency, missing endpoint) pair; S3 one finding
per detected cycle (the first cycle found by the canonical
traversal — see I-11); S2 one per regressed region. Each finding
is a distinct structural identity (VP-40's rule).

**I-11. Deterministic cycle extraction.** S3 traverses regions in
sorted id order and each region's outgoing edges in sorted
dependency-id order; the reported cycle is the first back-edge
cycle that traversal closes, and its affected set is the sorted
set of dependency records on that cycle path. Two implementations
running the same traversal report the same set (VP-20's
determinism requirement).

**I-12. VP-50..VP-54 have one implementation by design.** The
starvation report is a derived read model, not one of the two
validated implementations (the engine and the checker). The pack
manifest executes it twice over byte-identical input — once via
the module API, once via the module's standalone CLI in a separate
process — and agreement is byte-identity of the two outputs (which
is also VP-54's own expectation). This is recorded as a pack-scope
observation, not smoothed over: §9's cases test the report
contract, and there is no second report implementation to agree
or disagree.

**I-13. VP-28 is executed as an import audit, once, against its
only subject.** The audit runs the checker in a subprocess under
an import hook that records every module loaded, and asserts no
engine/harness/service/store/fixture/client module appears,
directly or transitively; a static scan of checker.py's own
imports stands beside it. The manifest records the audit's verdict
in both columns with this note, because the case has one subject.

## 2. The checker interface contract (dispatch item 4, stated explicitly)

`fabric/checker.py` runs as a separate process
(`python3 -m fabric.checker`), reads ONE JSON request object from
stdin, writes ONE JSON verdict object to stdout, and exits 0 for
every well-formed verdict — including `halt` and `refused`
outcomes, which are verdicts, not process failures. A non-zero
exit, a timeout, or unparseable output is a process failure: in
the commit path that is machinery failure (VP-36).

It imports **only** `fabric/canonical.py` from the fabric package
(format primitives: canonical JSON, SHA-256, the event hash) plus
the Python standard library. It does not import engine, harness,
service, store, fixture, or client code, directly or transitively
(VP-28). Everything else it needs arrives as data: the constitution
hash, the region set (from the RUN_OPENED event itself), the
pinned pack digest (for VP-55 checks, when supplied).

**Inputs, per request:**

- `mode: "fold"` — `{constitution_hash, history}` →
  `{ok: true, state, state_hash}` or
  `{ok: false, halt: {seq, reason_class, reason}}`.
- `mode: "evaluate"` — the attempt evaluation:
  - `constitution_hash`;
  - the committed history H: `store_path` (the checker opens the
    event store read-only itself) or `history` (the events as
    data). Exactly one form per request;
  - `staged_batch`: the candidate event batch B as explicit data,
    in order — provisional `event_seq` values continuing H's head,
    no `hash`/`prev_hash` claimed for B (the checker validates B's
    sequence contiguity and applies its events; chain-hash
    validation applies to H, whose links are final). **The key's
    absence is meaningful**: a request without `staged_batch` is
    VP-25's omitted batch and the verdict is `refused`;
  - `snapshot`: the live derived state L at the attempt boundary
    (after B's state effects, before the attempt's own events), as
    data. Evidence, not authority;
  - `authenticated_actor` (optional): the identity the staged
    batch is submitted under; a staged IDLE naming a different
    actor is refused (I-6).
- `mode: "report"` is **not** a checker mode; the starvation
  report is `fabric/starvation.py`'s own CLI (I-12).

**Verdict (evaluate):** `{outcome, failed_checks, divergence,
raises, resolutions, attachments, seal}` where outcome is one of
`pass | fail | mismatch | refused | halt`; `failed_checks` is a
list of `{check, affected}` with `affected` canonically sorted;
`divergence` lists the differing record identities between L and
the checker's independently folded R; `raises`/`resolutions`/
`attachments` describe the structural lifecycle against the open
structural tensions folded from H; `seal` (on pass only) carries
the position-independent seal contents — contributions since the
last seal, checks performed, outstanding semantic questions — for
the caller to anchor at the SEAL_ATTEMPTED event's position.

**Independence.** The checker re-implements, from the spec text:
chain verification and the fold (including the Stage 3 transition
legality and the malformed-payload hardening, with the pack's
pinned reason taxonomy); S1/S2/S3; the C1 2×2 precedence; seal
eligibility and outcome; structural identity, deduplication, and
resolution (re-running the tension's own check against its
original affected set). Its fold treats IDLE as evidence-only
under A1 and enforces the authority set bound in RUN_OPENED
(VP-15). A history the engine's fold halts on halts the checker's
fold at the same sequence with the same reason class.

## 3. Starvation report — measure definitions (B8: defined before use)

`fabric/starvation.py` computes a deterministic derived report
over an event history. It mutates nothing. Definitions:

- **Agent set:** every actor of a `CONTRIBUTION_ACCEPTED`,
  `CONTRIBUTION_REJECTED`, `ASSESSMENT_RECORDED`,
  `EXAMINATION_RECORDED`, `COMPLETION_CLAIMED`, or `IDLE` event.
- **Wake:** one event, authored by the agent, of the types above —
  the agent's recorded turns.
- **Rejections by outcome:** counts over `CONTRIBUTION_REJECTED`
  events keyed by the payload's `outcome`, plus Stage 3 outcome
  events (`ASSESSMENT_RECORDED` / `EXAMINATION_RECORDED` /
  `COMPLETION_CLAIMED`) whose payload outcome is `rejected`,
  keyed `"stage3:<reason>"`.
- **Consecutive rejections:** over the agent's own rejection
  events in sequence order. The current run increments on each
  rejection and resets to zero **only** on that agent's accepted
  commit (`CONTRIBUTION_ACCEPTED`). IDLE and every other event —
  the agent's or anyone's — neither increments nor resets it
  (VP-51). The report carries both the current run and the maximum
  run observed.
- **Wakes between successful commits:** for each pair of
  consecutive accepted commits of the agent, the number of the
  agent's wakes with sequence strictly between the two commits'
  sequences; reported as a list in commit order. `null` when the
  agent has fewer than two accepted commits (no gap observed) —
  the field is always present (VP-52).
- **Time to first success:** `first_success_seq − first_wake_seq`
  in run events, plus `wakes_to_first_success` (the agent's wakes
  up to and including the first accepted commit). Both `null`
  when the agent has no accepted commit; fields always present.
- **Changed-read diff sizes:** for each of the agent's stale
  `CONTRIBUTION_REJECTED` events, in sequence order, the length of
  the recorded `diff` list — **regions**, read from the rejection
  evidence itself, never recomputed from current state (VP-53).
- **Progression:** `accepted_commits` (count) and
  `progressed_after_first_rejection` (an accepted commit exists
  after the agent's first rejection).
- **Form:** `{"agents": {…}, "events_considered": n}` serialised
  with the fabric's canonical JSON; agent keys sorted (VP-54:
  byte-identical for identical input).

## 4. Pack mapping table (recorded BEFORE execution)

Native forms shared by all cases: canned histories are built once
as serialized event dicts (hash-chained with the format primitives
both implementations share) and the identical bytes are fed to
both sides. The pack's abstract fixture (six regions at v1; deps
`D-CS` = C `uses` S, `D-NI` = N `constrains` I) is realised with
the Annex D region ids and dependency ids
`…0201` (D-CS) / `…0202` (D-NI); aliases C, I, S, N, P, O mean
Components, Interactions, State, Continuity, Presentation,
Operations. "Engine side" = `fabric.engine.verified_fold` for
fold cases and `fabric.seal.evaluate_attempt` for attempt cases
(the same code the commit path's contract is stated against);
"checker side" = the checker process in the matching mode. Live
commit-path cases run on a Stage-4-bound run (I-1) through
`Harness` in-process; their checker column is the checker verdict
for the same (H, B, L).

| Case | Engine-side realisation | Checker-side realisation | Expected |
|---|---|---|---|
| VP-01 | fold([RUN_OPENED bound]); evaluate(B=[], L=fold) | fold mode; evaluate mode, same inputs | fold ok; attempt PASS, seal issued |
| VP-02 | fold(H) vs fold(H+[IDLE by A]) | fold mode, same histories | state identical except last_seq; head advances |
| VP-03 | seal.evaluate_attempt(B=[IDLE by B], authenticated_actor=A) | evaluate, same inputs | `refused`; nothing folded; no seal (I-6) |
| VP-04 | fold(H with seq 2 prev_hash tampered) | fold mode | HALT(2, hash_chain_invalid) |
| VP-05 | fold(H with seq 2 duplicated at position 3) | fold mode | HALT(3, sequence_invalid) |
| VP-06 | fold(H: TENSION_RAISED missing `status`, hash-valid) | fold mode | HALT(2, schema_invalid) |
| VP-07 | fold(H: TENSION_RAISED type = array) | fold mode | HALT(2, schema_invalid), no native exception |
| VP-08 | fold(H: TENSION_STATUS from = object) | fold mode | HALT(3, schema_invalid), no native exception |
| VP-09 | fold(H: TENSION_STATUS to = array) | fold mode | HALT(3, schema_invalid), no native exception |
| VP-10 | fold(H: TENSION_RAISED type = "unknown-kind") | fold mode | HALT(2, schema_invalid) |
| VP-11 | fold(H: semantic+checker origin); fold(H: structural+contribution origin) | fold mode | HALT(2, protocol_transition_invalid) each |
| VP-12 | fold(H: semantic open→resolved); fold(H: …→resolved→examined) | fold mode | HALT at the offending seq, protocol_transition_invalid |
| VP-13 | fold(H: structural open→examined / open→standing / resolved→open) | fold mode | HALT at the offending seq, protocol_transition_invalid |
| VP-14 | fold(H: FACET_STATUS to = "bogus"); fold(H: FACET_STATUS target outside the six) | fold mode | HALT schema_invalid; HALT protocol_transition_invalid |
| VP-15 | fold(RUN_OPENED binding [A1] + IDLE); fold(RUN_OPENED binding [] + IDLE) | fold mode | A folds; B HALT(2, schema_invalid) |
| VP-16 | evaluate(H, B=[], L = fold(H) minus region S) | evaluate, same inputs | FAIL(S1, {D-CS, S}); no seal |
| VP-17 | evaluate(H, B=[], L = fold(H)) | evaluate, same inputs | no S1 finding (overall PASS) (I-7) |
| VP-18 | evaluate(H, B=[], L = fold(H) with C's version lowered) | evaluate, same inputs | MISMATCH; no seal (I-3: FAIL(S2) branch unreachable) |
| VP-19 | evaluate(H, B=[accept: add_dep C→P + content on I], L = fold(H+B)) | evaluate, same inputs | no S2 finding; PASS; versions advanced on C, P, I |
| VP-20 | evaluate(H, B=[], L = fold(H) + dep S→C active) | evaluate, same inputs | FAIL(S3, {D-CS, D-SC}); no seal |
| VP-21 | evaluate(H′ with convergent genesis deps, B=[], L = fold(H′)) | evaluate, same inputs | no S3 finding (overall PASS) (I-7) |
| VP-22 | bound run: contribution with content op outside write_set → rejected `schema`; no SEAL_ATTEMPTED in history | no staged batch exists; evaluate never invoked | NO_ATTEMPT both sides |
| VP-23 | bound run: stale contribution → CONTRIBUTION_REJECTED; no SEAL_ATTEMPTED | same as VP-22 | NO_ATTEMPT both sides |
| VP-24 | evaluate(H, B=[accept: content on I], L = fold(H+B)) | evaluate, same inputs | PASS; seal issued |
| VP-25 | seal.evaluate_attempt(staged_batch=None) | evaluate request WITHOUT the staged_batch key | `refused`; no seal |
| VP-26 | evaluate(H, B=[accept: content on I], L = fold(H+B) with P's content altered) | evaluate, same inputs | MISMATCH; divergence names P |
| VP-27 | evaluate(H with genesis dep C→Q, Q not a region; B=[], L = fold(H)) | evaluate, same inputs | replay ok; FAIL(S1, {D-CQ, Q}); no seal |
| VP-28 | import audit subprocess + static import scan of checker.py | (the audit is the case; recorded in both columns, I-13) | no forbidden module in the checker's transitive graph |
| VP-29 | the manifest's cross-implementation agreement computation over VP-01..VP-55 | same | identical contract-level outcomes on every case |
| VP-30 | bound run: one accepted contribution → exactly one SEAL_ATTEMPTED in its group | evaluate verdict for the same (H, B, L) | one attempt; verdict PASS |
| VP-31 | bound run: live-state fault (region dropped from engine state only) → attempt 1 FAIL raises structural tension; a further contribution still gets its attempt | evaluate verdicts for both attempts | attempt occurs despite the open tension |
| VP-32 | continuation: correcting group ends […, SEAL_ATTEMPTED, TENSION_STATUS(open→resolved)] with the attempt's seq in the evidence | evaluate verdict for the resolving attempt | order and anchoring as specified (repair per I-5) |
| VP-33 | VP-31's first attempt payload | evaluate verdict for the same inputs | outcome fail; failed checks + affected recorded; no seal record |
| VP-34 | bound run: semantic T1 open, semantic T2 examined, then a content contribution | evaluate verdict for that attempt | seal issues; both questions listed with marks; statuses unchanged |
| VP-35 | bound run: two accepted contributions with passing attempts | evaluate verdicts | seal 1 lists [cid1]; seal 2 lists [cid2] |
| VP-36 | bound run with the checker command replaced by a failing process: submit raises CheckerFailure; history unchanged | (the failing process IS the checker side failing) | no partial group; in the service form, RUN_FAILED (stage4_tests) |
| VP-37 | bound run: CONTRIBUTION_ACCEPTED appended directly (examiner-side), then close_run() | evaluate verdict for the close attempt (B=[]) | exactly one close-time SEAL_ATTEMPTED, then RUN_CLOSED |
| VP-38 | bound run: normal contribution (attempt follows), then close_run() | n/a — no attempt is presented | no second SEAL_ATTEMPTED; RUN_CLOSED appended |
| VP-39 | evaluate(H holding open T(S1,{D-CS,S}), B=[], L with the same dangling dep, deps enumerated in the other insertion order) | evaluate, same inputs | no raise; finding attaches to T |
| VP-40 | evaluate(same H, L with a different dangling dep D-NI / region I removed) | evaluate, same inputs | one raise with the new identity; T untouched |
| VP-41 | evaluate(H holding open T(S1,{D-CS,S}), B=[], L with S removed, P present) | evaluate, same inputs | T not resolved; finding attaches |
| VP-42 | evaluate(H holding open T(S1,{D-CS,S}), B=[accept: remove D-CS], L = fold(H+B)) | evaluate, same inputs | T resolved; evidence names the attempt |
| VP-43 | evaluate(H holding open T(S1,{D-CS,S}), B=[], L with S removed — S2 passes, S1 still fails) | evaluate, same inputs | T remains open |
| VP-44 | evaluate(H holding open T(S1,{D-CS,S}), B=[accept: content on C], L still missing S) | evaluate, same inputs | T remains open; finding attaches; no inferred transition |
| VP-45 | the nine-step lifecycle on a bound run in-process (fault in engine state only; repair per I-5; correction removes D-CS) | evaluate verdicts at both attempts | the nine expected steps, in order (socket form in stage4_tests) |
| VP-46 | VP-34's first seal: semantic tension open at a passing attempt | evaluate verdict | seal issues; tension status unchanged |
| VP-47 | evaluate(H, B=[], L = fold(H)) — content carries the planted semantic contradiction, structure sound | evaluate, same inputs | raises == [] both sides |
| VP-48 | bound run with an open structural tension: assess targeting it → rejected `structural_target` | evaluate verdict over the same H: tension still open, no assessment input exists | rejection recorded; no structural transition |
| VP-49 | bound run: a facet unexamined; passing contribution attempt | evaluate verdict | seal issues; facet status as folded, unchanged by the seal; no completion inferred |
| VP-50 | starvation.build_report over the constructed history (API) | the same module's CLI over the same serialized history (I-12) | report contains A, B, C; outputs byte-identical |
| VP-51 | report over R,R,accept,R for agent A | CLI, same input | max run 2; current run 1 |
| VP-52 | report over B: stale rejection + IDLE + schema rejection | CLI, same input | null fields present, never omitted, never zero |
| VP-53 | report over stale rejections with recorded diffs of 0, 1, 3 regions | CLI, same input | sizes [0, 1, 3], unit regions, from the evidence |
| VP-54 | build_report twice (API + CLI) over one closed history | — | byte-identical canonical outputs |
| VP-55 | Engine.open_run with a wrong pack digest → refused; with the pinned digest → RUN_OPENED names id/version/SHA-256 | fold mode with expected_pack_sha256 supplied: checker reports the bound digest and flags a mismatch | opening blocked on mismatch; binding exact on match |

## 5. Deviations and honest limits (recorded during the build)

*(Appended as they were found; see also section 6.)*

- The snapshot mechanism proves exactly this: the checker received
  a state L as data and compared it with its own fold. It cannot
  prove the service's *internal* state was L at any instant — the
  snapshot is produced by the harness from its hypothetical state
  inside the commit transaction, which is the strongest statement
  this architecture supports, and the pack's own terms ("L is
  evidence, not authority") already say so.
- The S2 seal check is a backstop whose failing branch the fold's
  operation set makes unreachable (I-3).
- TV-1's fault is injected, in the socket form, through an
  operator-path test hook (`inject_live_state_fault`) that mutates
  only the service process's in-memory derived state. The hook is
  not reachable from the data socket; it exists so the nine steps
  can be exercised against the real boundary rather than a
  simulation of it.
- **Admission attribution narrowing (a change to accepted Stage 2
  code, made in this round and recorded here).** The harness's
  commit-time structural check (`_structural_violation`) formerly
  scanned the whole hypothetical state for S1/S3 violations. With
  a pre-existing live-state fault standing (TV-1's injection),
  that scan rejected EVERY subsequent contribution as
  "structural", attributing the standing fault to innocent
  submissions — and no seal attempt could ever evaluate the
  faulted state, making the seal's structural lifecycle
  unreachable on the live path and TV-1/VP-45 impossible as
  specified. The S1 and S3 scans now judge the violations the
  submitted contribution itself introduces (the dependencies it
  adds; the cycles its additions close); a standing inconsistency
  is the seal regime's finding, recorded by the attempt that
  follows the accepted commit. On every history the earlier
  stages produce — the live state consistent until the
  contribution acts — the attributed and whole-state scans decide
  identically, and all prior suites pass unedited at their exact
  baseline counts (section 6). The narrowing is a deviation from
  the accepted Stage 2 text, taken because the pinned pack's
  TV-1/VP-45 sequence cannot otherwise be realised; it is
  Vane's to overrule at examination.
- **S2 alignment before execution.** The first implementation
  draft of both evaluators read S2 against the committed fold
  (a live version below the committed version = FAIL(S2)). The
  mapping table in section 4 — recorded before any pack
  execution — pins I-3's staged-transition reading, under which
  a supplied regressed snapshot is MISMATCH (VP-18, VP-47). Both
  implementations were aligned to I-3 before the pack was
  executed; the pack was never run against the earlier reading.
- **Fixture id correspondence.** The pack's abstract dependency
  labels map to the fixture's genesis ids: D-CS =
  `00000000-0000-4000-8000-000000000102` (Components uses State),
  D-NI = `…0103` (Continuity constrains Interactions). Canned
  histories carry the Annex D region ids and these dependency
  ids; the manifest records the actual ids used.

## 6. Results

Executed 2026-11-21, after the mapping table in section 4 was
complete and the S2 alignment (section 5) was made. Nothing below
was smoothed: every count is the suite's own printed count.

**Pack validation (pack_validation.py) — 61/61 case records
PASS.** The 55 pinned vectors are realised as 61 records (VP-01
split into fold + attempt records; VP-11, VP-12, VP-13, VP-14
split into their lettered sub-cases). Per implementation:

- Engine side (`fabric.engine.verified_fold` +
  `fabric.seal.evaluate_attempt`, plus the live harness path):
  every case's observed outcome equals the expected outcome.
- Checker side (`fabric.checker` process, fold + evaluate modes,
  plus the VP-28 module-graph audit): every case's observed
  outcome equals the expected outcome.
- **Disagreements between the implementations: none** (VP-29,
  computed over the manifest: identical contract-level outcomes
  on every comparable case). The full per-case manifest is at
  `pack-validation-manifest.json` (pack id/version/SHA-256,
  implementation build hashes, fixture hashes, observed vs
  expected, per pack §10.3).

**Stage 4 suite (stage4_tests.py) — 21/21 checks PASS**,
including: TV-1 in VP-45's nine-step form through the real
socket boundary (twin attestation, operator-hook fault
injection, repair by service restart per I-5, correction by a
genuine remove-dependency contribution); TV-6 (one
inconsistency, one tension, findings attached); TV-8
(stood-down follows the declared regions exactly); TV-13's
genuine resolution half (tension raised by a real failed
attempt; a fully valid "addressed" assessment rejected
`structural_target`; resolution only by the passing attempt);
the malformed-payload hardening negatives (array type, object
from, array to — controlled `schema_invalid` halts at the exact
sequences in BOTH folds, no native exception); VP-36 in service
form (RUN_FAILED with breach `checker_failure`, no partial
group); VP-55 in service form (wrong digest blocks the opening;
the bound opening names the pinned pack); VP-38 in service form
(close appends RUN_CLOSED, no duplicate attempt).

**Regressions — all prior suites unedited, exact baseline
counts, zero failures:** stage1_smoke 18, stage2_tests 40,
stage2_corrections 53, stage2_corrections_round2 27,
stage2_corrections_round3 34, stage2_corrections_round4 32,
stage2_corrections_round5 37, stage2_corrections_round6 31,
stage3_tests 71, stage3_corrections 37, observer safety 11 —
**391 checks**, matching the pre-Stage-4 baseline exactly.

**Genesis state hash:** `9a7250bde82bfd8b…` (full:
9a7250bde82bfd8bd220b6013f38b4ce289a702fe86119f2723616055c070b1f)
for both unbound and Stage-4-bound runs — unchanged.

**Totals for the round: 391 + 61 + 21 = 473 checks, all
passing.** The closing exercise and the complete TV-1..TV-20
evidence package are NOT part of this round and were not run.
No live agents were used at any point.
