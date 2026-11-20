# VANE — GATE 1 VERDICT: STAGE 2 (ARTEFACT CONSTRUCTION AND PROVENANCE)

**Verdict: FAIL — RETURN TO STAGE 2 FOR CORRECTION.**
**DR-02: NOT ADVANCED on this submission.**
**Dependency decision: Stage 5 receiver-idempotency work does not move before Stage 2, on the evidence presently examined.**
**Date:** 2026-11-20
**Examiner:** Vane

## Scope and materials

Examined the Stage 2 package at commit `6e041ee6f045fd07c7af1be62f344bc97eab1c7b`:

- `stage2/schema.py` (blob `78f5579c9b8fe934fddfc3d8795cfd49716c0a13`)
- `stage2/construction.py` (blob `0aab2116a85cc6617c6a4a0e853feb678cfebcc0`)
- `stage2/STAGE2-REPORT.md` (blob `4b5f5a4c89c0784748bbf0a79d6dfe54a572149b`)
- `stage1/record.py` (blob `888047ba3bc8dc95e8b50fd75fad9b400a4c134c`)
- `PROCESS-TREE-AND-PLAN.md` v2, Stage 2
- `ID-SYSTEM-DESIGN-DRAFT-V3.md`, K5/G2
- `DEFECT-REGISTER.md`, DR-02

The report records 21/21 Stage 2 tests and 68/68 Stage 1 regression tests as builder-run evidence. I have examined the source and the reported test cases; those reported counts are not represented here as an independent execution by the examiner.

## Findings

### 1. Frozen schema object — PASS within the demonstrated harness scope

The implementation freezes both sections in one construction act, exposes tuple sections, prevents ordinary post-construction attribute assignment, and computes one SHA-256 identity over version and both sections. The tests cover mutation attempts, duplicate and nameless fields, determinism, and identity changes when either section or version changes.

Qualification: `TEST_SCHEMA` is explicitly a test fixture, not the production per-run schema inventory. Its eight artefact fields and three response fields demonstrate the mechanism, not the final production field contract. This is candidly disclosed and is not by itself the reason for this return. Production inventory remains a run-configuration matter under K3.

### 2. Three-way construction close — PASS for the cases and inputs examined

`_differing` compares artefact fields, provenance-entry fields, and the frozen schema's artefact fields. It checks names and values, including the critical case where a schema-required field is absent from both artefact and entries. It also reports differing field identities rather than a bare refusal.

The positive controls and reported sabotages (a) through (f), plus the value-mismatch companion, address distinct failure modes. In particular, (b) demonstrates the schema acting as a third party, and (f) correctly rejects pairwise agreement between two incomplete representations.

### 3. Canonical provenance boundary — FAIL; material bypass remains

The implementation describes `append_provenance_entry` as the only way provenance enters the record. But Stage 1's `EventRecord.append(event_type, body)` remains a public, unrestricted generic append operation. It accepts an arbitrary event type and body. Stage 2's `read_provenance_entries` then trusts every record event whose type string equals `PROVENANCE_ENTRY` and whose body contains the expected artefact identity. It does not establish that the event was created through `append_provenance_entry`.

Consequently, a caller can bypass the purported canonical entry function and directly call the underlying record API with a `PROVENANCE_ENTRY` event carrying the expected `artefact_id`, `field`, and `value`. The reader will accept that event as provenance, the constructor will build from it, and the three-way close can pass if the fields and values match the schema.

This is materially different from sabotage (e). Sabotage (e) uses a foreign event type (`LEDGER_ENTRY`), which the reader correctly ignores. It does not test a forged event using the very event type the reader trusts. The current tests therefore demonstrate rejection of a foreign-type bypass, not enforcement of the claimed canonical entry path.

This is a source-level counterexample to the central claim: provenance-shaped content can still enter the accepted provenance stream without going through the validated canonical function. The fact that the generic append API is available in the same record implementation is directly relevant; the boundary is not enforced at the point where the record accepts the event.

Required correction: make the provenance event's accepted creation path enforceable at the record boundary, or otherwise redesign the record/API so that arbitrary callers cannot create an event that the provenance reader treats as canonical. Add an adversarial test that directly invokes the generic record append with event type `PROVENANCE_ENTRY` and a complete, schema-matching body, bypassing `append_provenance_entry`. The constructor must refuse it. Also test malformed canonical-type bodies and ensure they produce a recorded, controlled refusal rather than an uncaught exception or accidental admission.

Do not merely add a second comparison after reading the same forged event: the issue is provenance authority, not equality of its contents.

### 4. Construction and refusal records — partial PASS, boundary dependent

The constructor reads entries from the record, builds from those entries, and records close/refusal events with schema identity and differing field details. The Stage 1 chain is reused without modification. These are sound structural choices for the demonstrated local harness.

However, a successful close currently establishes only that the values supplied through the reader agree with the schema. Until the reader can distinguish canonical entries from directly forged canonical-type events, the close cannot establish the provenance invariant DR-02 requires.

### 5. Dependency decision — ACCEPTED

The examined Stage 1 record is an append-only local event log. Stage 2 reads provenance entries and performs construction and close synchronously, in-process. The Stage 2 path shown does not perform operation insertion, communicate with a receiver, cross a delivery boundary, or implement retry semantics.

On this evidence, Stage 2 does not depend on operation insertion. The plan's condition for moving Stage 5 receiver-idempotency work ahead of Stage 2 is not met. Stage 5 does not move. This is a scoped dependency finding, not a claim that the wider programme has no insertion/retry dependency.

## Disposition

**FAIL — RETURN TO STAGE 2 FOR CORRECTION.**

The schema mechanism and three-way comparison are substantially demonstrated. The reported positive controls and sabotages are useful evidence. But DR-02's required invariant is that no produced artefact field can exist without its canonical provenance entry, with construction, validation, and ledger completeness joined by a mechanically enforced invariant. The current generic record append path allows a caller to manufacture an event that the reader accepts as canonical without using the canonical entry function.

The missing adversarial case is decisive. Sabotage (e) does not cover it.

### Required resubmission

1. Close the direct generic-append bypass for `PROVENANCE_ENTRY` events.
2. Add the forged-canonical-event sabotage described above, exercising the actual constructor path.
3. Preserve the existing positive controls and separate sabotage cases (a)–(f); do not collapse them into one aggregate refusal test.
4. Re-run the Stage 2 suite and Stage 1 regression suite, reporting exact commands, counts, and exit codes. The report must distinguish builder-run evidence from any independent examiner execution.
5. Update the report and DR-02 disposition only after the corrected package is pinned. Do not describe DR-02 as advanced on the present evidence.

The Stage 5 dependency decision stands as recorded above.

No Stage 2 PASS is granted by this verdict. Later stages may proceed only within Ben's approval and their own controls; this return does not authorise bypassing the Stage 2 dependency or treating DR-02 as discharged.

— Vane
