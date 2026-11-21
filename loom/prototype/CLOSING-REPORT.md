# Closing Exercise — Report (2026-11-21)

**Commission:** the prototype commission's closing step (Ben's tap, scope card widget-284602e8): one full mechanical lifecycle exercised end to end + the complete Annex E TV-1..TV-20 evidence package, for Vane's integrated examination. Executed 2026-11-21, after Stage 4 ACCEPTANCE (build a99a7676, correction round 1 e46d47d0, correction round 2 ffc0af1f — all preserved, none amended). **No live agents** — every actor is a scripted mechanical driver. **No production fabric code was changed**; the only new code is the exercise's own drivers (`closing_exercise.py`, `closing_tv_tests.py`).

**Result in one line:** the lifecycle ran clean end to end in a single 38-event history; all twenty Annex E vectors were freshly executed and pass (45/45 checks); every prior suite reran unedited at its exact baseline.

---

## Part 1 — The full mechanical lifecycle (one bound run, one history)

Driven by `closing_exercise.py` through the real socket service: the loomfab-owned fabric service, every agent operation performed by a genuine loomagent process over the data socket, operator actions over the admin socket. Run id `closing-lifecycle`. Full history: `closing-lifecycle-history.json` (38 events). Anchor: `closing-anchor.json`.

**Shape:** RUN_OPENED 1 · BOUNDARY_PROBE 1 · DISCOVERY 7 · CONTRIBUTION_ACCEPTED 4 · CONTRIBUTION_REJECTED 1 · EXAMINATION_RECORDED 1 · TENSION_RAISED 2 · ASSESSMENT_RECORDED 3 · COMPLETION_CLAIMED 2 · FACET_STATUS 8 · IDLE 1 · SEAL_ATTEMPTED 4 · TENSION_STATUS 2 · RUN_CLOSED 1.

**The beats, traceable to event seqs:**

| Beat | What happened | Seqs |
|---|---|---|
| Bound open | RUN_OPENED binds Rev 9 + Amendment A1 + the pinned pack (id `VANE-STAGE4-EXAMINER-VALIDATION-PACK`, v2, SHA-256 cce27ee7…); genesis state hash = the pinned constant 9a7250bd… | 1 |
| Boundary probe | The pre-run probe ran against a disposable twin; its attestation stands at seq 2 before any agent operation is admitted | 2 |
| Capped reads | A read {Interactions, Continuity}, B {Components, State}, C {Presentation}; cumulative breadth A 2/6, B 2/6, C 1/6 — all under the RB < 0.5 cap | 3–7 |
| Ordinary work | A appended to Interactions (sealed, seq 10); B appended to State → v2 (sealed, seq 13) | 8–13 |
| The plant rejected | B's proposed State→Components `uses` edge — the Annex D plant closing the S3 cycle — rejected at admission as structural S3, on the record; the standing graph unchanged | 14 |
| The contradiction | A's ExaminationReport over {Interactions, Continuity} created the semantic tension (stateless vs pinned-session); B assessed `addressed`, C assessed `clarifies` — different positions, disagreement preserved; tension stands **examined**, not resolved | 15–19 |
| Completion | B claimed State at v2 citing B's own State contribution; A's independent current-version review completed State (seq 23). A claimed Interactions; unreviewed, it stands **claimed** | 20–25 |
| IDLE | C idled — a durable IDLE event, evidence-only under A1 | 26 |
| TV-1 in-run | Fault injected into the live derived state only (State dropped; the history still folds clean). A's ordinary Continuity contribution was **accepted** (admission reads the authoritative fold); its seal attempt **FAILed S1** on {D-CS, State} and the checker raised the structural tension. Explicit restart repair (I-5): history byte-identical afterwards, tension still open. B's correcting contribution removed the dangling dependency — accepted despite the open tension; its attempt passed and sealed; the tension **resolved** with that attempt (seq 36) as its evidence | 27–37 |
| Close | RUN_CLOSED; the final commit already had its attempt, so close added no second attempt; the close records the chain head it anchors (dcb39010…) | 38 |

**Seals (§7 record):** 4 attempts — 3 pass with seals (seqs 10, 13, 36), each carrying `semantic_clearance: false` and the structure-only statement; 1 fail (seq 29) standing on the record unsealed.

**Facet accounting, at the claim point (after seq 25):** State **complete**, Interactions **claimed**, Components / Continuity / Presentation / Operations unexamined.
**At close:** Interactions **claimed**; State **unexamined** — its completion was real at version 2 (seq 23), and the correcting contribution advanced State's version, which resets the accounting mechanically under §5 (the fabric's own FACET_STATUS summary at seq 35 says "now unexamined (it was complete)"). Both snapshots are reported because both are true at their positions.

**Starvation report** (derived over the full history by `fabric.starvation`, the §7 derived-report module): Agent A — 5 wakes, 2 accepted commits, no rejections. Agent B — 5 wakes, 2 accepted commits, 1 rejection (structural — the plant). Agent C — 2 wakes, **0 accepted commits** (the zero-commit agent is present in the report, with `time_to_first_success: null`, never omitted, never zero-filled).

**The narrative, generated from the events** (each line cites its seq; also at `closing-lifecycle-narrative.md`):

- seq 1 · RUN_OPENED — The run opened, bound to Rev 9 + Amendment A1 and the pinned examiner pack; the genesis state (six regions, four dependencies, the constitution) is carried inside this event.
- seq 2 · BOUNDARY_PROBE — Boundary probe attestation: before this run opened, the pre-run boundary probe ran against a disposable twin of this runtime (same layout, owners, permissions and service build) from the agent OS context. The twin's store and ground-truth files denied every direct and alternate-path read; forged-token and issuance attempts on the data socket were refused; legitimate operations through the harness succeeded. This event attests to that twin probe — the experimental store itself was not probed, and no probe reads are in this history.
- seq 3 · DISCOVERY — Agent aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa opened Interactions (version 1) by reading the fabric directly.
- seq 4 · DISCOVERY — Agent aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa opened Continuity (version 1) by reading the fabric directly.
- seq 5 · DISCOVERY — Agent bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb opened Components (version 1) by reading the fabric directly.
- seq 6 · DISCOVERY — Agent bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb opened State (version 1) by reading the fabric directly.
- seq 7 · DISCOVERY — Agent cccccccc-cccc-4ccc-8ccc-cccccccccccc opened Presentation (version 1) by reading the fabric directly.
- seq 8 · CONTRIBUTION_ACCEPTED — A contribution by agent aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa was accepted and committed, changing Interactions.
- seq 9 · FACET_STATUS — The facet Interactions is now unexamined (it was open), on the evidence the record holds.
- seq 10 · SEAL_ATTEMPTED — A weave seal was attempted after the accepted commit and passed: every structural check succeeded on the current state, and a seal stands at this position. The seal certifies structure only; it grants no semantic clearance.
- seq 11 · CONTRIBUTION_ACCEPTED — A contribution by agent bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb was accepted and committed, changing State.
- seq 12 · FACET_STATUS — The facet State is now unexamined (it was open), on the evidence the record holds.
- seq 13 · SEAL_ATTEMPTED — A weave seal was attempted after the accepted commit and passed: every structural check succeeded on the current state, and a seal stands at this position. The seal certifies structure only; it grants no semantic clearance.
- seq 14 · CONTRIBUTION_REJECTED — A contribution was rejected as structural: it violated invariant S3.
- seq 15 · EXAMINATION_RECORDED — An examination of Interactions, Continuity was recorded and raised a new semantic tension.
- seq 16 · TENSION_RAISED — A semantic tension was raised over Interactions, Continuity by an examination report.
- seq 17 · ASSESSMENT_RECORDED — An assessment of a tension was recorded, position addressed.
- seq 18 · TENSION_STATUS — The tension over Interactions, Continuity was examined: its first assessment is on record.
- seq 19 · ASSESSMENT_RECORDED — An assessment of a tension was recorded, position clarifies.
- seq 20 · COMPLETION_CLAIMED — A completion claim was recorded; whether it counts is a matter of the evidence binding, computed from the record.
- seq 21 · FACET_STATUS — The facet State is now claimed (it was unexamined), on the evidence the record holds.
- seq 22 · ASSESSMENT_RECORDED — An assessment of a facet was recorded, position examined.
- seq 23 · FACET_STATUS — The facet State is now complete (it was claimed), on the evidence the record holds.
- seq 24 · COMPLETION_CLAIMED — A completion claim was recorded; whether it counts is a matter of the evidence binding, computed from the record.
- seq 25 · FACET_STATUS — The facet Interactions is now claimed (it was unexamined), on the evidence the record holds.
- seq 26 · IDLE — Agent cccccccc-cccc-4ccc-8ccc-cccccccccccc chose to idle: it took no action this turn.
- seq 27 · CONTRIBUTION_ACCEPTED — A contribution by agent aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa was accepted and committed, changing Continuity.
- seq 28 · FACET_STATUS — The facet Continuity is now unexamined (it was open), on the evidence the record holds.
- seq 29 · SEAL_ATTEMPTED — A weave seal was attempted after the accepted commit and failed: structural check(s) S1 did not pass on the current state. No seal was issued.
- seq 30 · TENSION_RAISED — A structural tension was raised by the checker (S1): the records it names are inconsistent in the current state.
- seq 31 · DISCOVERY — Agent bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb opened Components (version 1) by reading the fabric directly.
- seq 32 · DISCOVERY — Agent bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb opened State (version 2) by reading the fabric directly.
- seq 33 · CONTRIBUTION_ACCEPTED — A contribution by agent bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb was accepted and committed, changing Components, State.
- seq 34 · FACET_STATUS — The facet Components is now unexamined (it was open), on the evidence the record holds.
- seq 35 · FACET_STATUS — The facet State is now unexamined (it was complete), on the evidence the record holds.
- seq 36 · SEAL_ATTEMPTED — A weave seal was attempted after the accepted commit and passed: every structural check succeeded on the current state, and a seal stands at this position. The seal certifies structure only; it grants no semantic clearance.
- seq 37 · TENSION_STATUS — A structural tension was resolved: the S1 check, re-run against the tension's original affected records by the passing seal attempt at sequence 36, found the inconsistency gone.
- seq 38 · RUN_CLOSED — The run was closed. Its final state hash and chain head stand in this record; what an external anchor does and does not establish for them is stated in the Stage 4 build notes (B7), not claimed here.

Final facet accounting (derived): Components = unexamined, Interactions = claimed, State = unexamined, Continuity = unexamined, Presentation = unexamined, Operations = unexamined.

Anchor: content-addressed archival anchor — produced by the closing exercise script from the service's own exported history; an archival record of the run's tail, NOT an independently trusted attestation.
History SHA-256 (canonical events): 4e2aa66d020b75f75b9b3e8a4209a00c1d7770b3635cfb9cb3934c0df00123bf.

---

## Part 2 — The TV-1..TV-20 evidence package

All twenty vectors from Annex E of Rev 9, executed fresh in this exercise by `closing_tv_tests.py` (45 checks, all PASS). Configurations mirror the accepted suites: the ladder/commit-protocol vectors run on unbound runs (that machinery is binding-independent); the vectors exercising the seal machinery run on Stage 4-bound runs, in their genuine form where Stage 3 had to use a canned record.

| TV | What was executed | Config | Checks | Result |
|---|---|---|---|---|
| TV-1 | Fault dropped from the live derived state only; ordinary contribution accepted; attempt FAIL(S1, {D-CS, State}); checker tension raised; I-5 rebuild; correcting contribution removes D-CS; attempt passes + seals; tension resolved with the attempt as evidence. **Also executed through the real socket service inside the Part 1 lifecycle (seqs 27–37)** | bound, genuine | 4/4 | PASS |
| TV-2 | `raise_tension` with type `structural` → schema-invalid; exactly one CONTRIBUTION_REJECTED; no tension created | unbound | 1/1 | PASS |
| TV-3 | Claim for State v3 citing only unrelated Components work counts as no claim (State unexamined despite a standing review); the binding claim citing C-state completes State | unbound | 3/3 | PASS |
| TV-4 | Resolved tension untouched by a later contribution to a named region (no transition, no event, no new tension); recurrence via ExaminationReport creates a distinct T2 at open | unbound | 2/2 | PASS |
| TV-5 | `clarifies` moves open → examined with the assessment as evidence; one `addressed` + a further `clarifies` never resolves | unbound | 2/2 | PASS |
| TV-6 | Two further accepted contributions under the standing S1 fault: both attempts fail on the same check and set; exactly one structural tension throughout; findings attach to it | bound, genuine | 2/2 | PASS |
| TV-7 | Identical resubmission under K returns the original outcome, no new event; different content under K → `idempotency_conflict`, not applied | unbound | 2/2 | PASS |
| TV-8 | Standing tension over {Interactions, Continuity} stands down exactly those required facets; a standing {Presentation} tension stands down nothing (optional facet) | bound | 2/2 | PASS |
| TV-9 | Facet target + `addressed`, tension target + `examined` → both schema-invalid, neither recorded | unbound | 2/2 | PASS |
| TV-10 | FacetAssessment without `version_reviewed`, TensionAssessment carrying it → schema-invalid; cross-kind target resolution (facet→tension, tension→region) → invalid, none recorded | unbound | 4/4 | PASS |
| TV-11 | Claim at State v5; a review of v3 is recorded as valid history and does NOT complete; a review at v5 completes | unbound | 3/3 | PASS |
| TV-12 | Examination: (i) creates with TENSION_RAISED following, origin_ref bound; (ii) unopened region rejected `region_not_in_read_record`; (iii) identical live set `noted_existing`; (iv) after resolution, the same set creates anew | unbound | 4/4 | PASS |
| TV-13 | **Both halves in one genuine case:** schema-valid assessment of the real checker-raised structural tension → rejected `structural_target`, no record, no TENSION_STATUS, tension stays open; the correcting contribution's passing attempt then resolves it, the assessment playing no part | bound, genuine | 2/2 | PASS |
| TV-14 | Two contribution-raised tensions over the identical set stand open; an examination notes against BOTH (`matched_tensions` = [T1, T2]); no third tension; no status changes | unbound | 1/1 | PASS |
| TV-15 | (i) Identical report resubmitted → original outcome, exactly one EXAMINATION_RECORDED; (ii) object omitting `regions` → recorded once, rejected `schema_invalid`, raw submission preserved; (iii) non-object submission → transport refusal, no event, harness log only | unbound | 3/3 | PASS |
| TV-16 | Assessment whose author claim mismatches the token AND targets the genuine structural tension → rejected `identity_mismatch` (step 1); the structural check is never evaluated | bound, genuine | 1/1 | PASS |
| TV-17 | ExaminationReport with an unknown region AND an unverifiable discovery_ref → rejected `unknown_region` (step 4); discovery validation never reached | unbound | 1/1 | PASS |
| TV-18 | ExaminationReport omitting `idempotency_id` → `schema_invalid` (not an idempotency outcome); Assessment with a malformed `assessment_id` → `schema_invalid` | unbound | 2/2 | PASS |
| TV-19 | Another author's reuse of `examination_id` X → `identity_collision`; the identity's own author reusing X under a fresh key → `identity_collision`; the original record untouched | unbound | 2/2 | PASS |
| TV-20 | Another author's reuse of `assessment_id` S → `identity_collision`; the author's own reuse with different content → `id_conflict`; the original assessment stands | unbound | 2/2 | PASS |

**No vector is unevidenced. No vector failed.**

---

## Part 3 — Regressions (all suites rerun UNEDITED in this exercise)

| Suite | Count | Baseline |
|---|---|---|
| stage1_smoke | 18 | 18 |
| stage2_tests | 40 | 40 |
| stage2_corrections_tests | 53 | 53 |
| stage2_corrections_round2_tests | 27 | 27 |
| stage2_corrections_round3_tests | 34 | 34 |
| stage2_corrections_round4_tests | 32 | 32 |
| stage2_corrections_round5_tests | 37 | 37 |
| stage2_corrections_round6_tests | 31 | 31 |
| stage3_tests | 71 | 71 |
| stage3_corrections_tests | 37 | 37 |
| observer export safety | 11 | 11 |
| **Regression total** | **391** | **391** |
| stage4_tests | 22 PASS lines | 22 |
| stage4_corrections_tests (round 1) | 24/24 | 24/24 |
| stage4_correction2_tests (round 2) | 21/21 | 21/21 |
| pack_validation (VP-01..VP-55) | 64/64; VP-29: 54 dual-applicable compared, 0 disagreements, 0 unmarked | 64/64; 54/0 |
| Genesis state hash | 9a7250bde82bfd8b… (unchanged, asserted inside the lifecycle run itself) | pinned |

New in this exercise: closing_exercise 20/20 beat checks; closing_tv_tests 45/45 checks.

---

## Named limitations and honest notes

1. **TV-1's two forms.** In `closing_tv_tests.py`, TV-1 is executed in the in-process genuine form — the fault dropped from the live derived state by the fixture harness, exactly as Annex E's own setup text prescribes ("the fixture harness drops one region record from the derived state"). The same lifecycle is additionally exercised through the real socket boundary (operator fault hook + service-restart repair) inside the Part 1 run, seqs 27–37. Both forms stand in this package; neither substitutes for the other.
2. **The S1 genesis-repair fact.** No Annex E vector requires repairing a poisoned genesis, and none was manufactured for this package. For the record: a genesis carrying a dependency whose endpoint is not a region has no lawful contribution-level repair under Rev 9 — ruled **formally non-constructible** in the Stage 4 correction-round-1 examination (not passed, not a defect). TV-1's fault lives in the live derived state only, per the vector's text, so this fact touches no TV outcome.
3. **Driver-side corrections during the exercise (no production code involved).** The first lifecycle drive was stopped at beat 4 by the fabric itself: the driver's contribution declared `base_versions` for only part of its read set, and cross-field rule (ii) (base_versions keys must equal the read set exactly) rejected it as schema through the socket path — the rule firing correctly on the driver's error. The driver was corrected (bases declared for the full read set, as every accepted suite does) and the run re-driven clean; the shipped history is the clean re-drive. A second driver slip (reading a stale history snapshot for a citation lookup) was corrected the same way. Both are recorded here rather than smoothed away; neither touched fabric code.
4. **The anchor is archival, not trusted.** `closing-anchor.json` is a content-addressed record produced by the exercise script from the service's own exported history (history SHA-256 4e2aa66d… over the canonical events; chain head at close dcb39010…; closing event hash 18e763e9…). It names itself honestly: an archival anchor, not an independently trusted attestation (design settlement B7).
5. **The starvation report is a derivation, not an event.** It is computed over the exported history by the §7 derived-report module; it does not appear in the history it describes, by design.
6. **Facet accounting is positional.** State's `complete` (seq 23) and its later `unexamined` (seq 35) are both true — at different versions. Any reading of the run that quotes only the final accounting understates what the record shows; both snapshots are given in Part 1.
7. **What this package does not contain.** No live agents were run (the commission's hard boundary stands: live-agent authorisation waits on the integrated examination of this package). The conformance gate of §1/Annex A (model trials) is a separate, later phase and is not evidenced here.
