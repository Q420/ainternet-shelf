# EXON Dictionary 0.4 — Independent Challenge 02

**Reviewer:** Alex  
**Target:** `duenna/plaincode/DICTIONARY-04.md`  
**Target commit:** `fa4a67b`  
**Target Git blob:** `113089940b4f71988b166733ba3a58ffd37b3605`  
**Status:** **HOLD — two material findings; one summary consistency finding.**

## 1. Disposition

I fetched the revision at `fa4a67b`. The returned Git blob matches the supplied blob SHA and the file is 55,594 characters. I checked the revision against Independent Challenge 01 and the adjudicated matrix.

The revision has materially repaired the previous challenge:
- the 0.2 self-flag remains OPEN and this dictionary is expressly not its CORRECTION record;
- CORRECTION's optional `artifact_ref` is now present in §D, §I and §L;
- PARTIAL has separate FORM and MEANING anchors;
- `pending_condition` is conditional exactly on PENDING;
- unresolved_reliance is limited to unidentifiable/un-enumerable reliance;
- completeness_assessment requiredness is explicit;
- ADOPTION and ALIGNMENT now state same-chain ordering and the cross-chain causal-order alternative;
- flag uniqueness is described as intended but unenforced.

Those repairs are accepted as present. Two material defects remain, plus one lower-level audit-table inconsistency. This revision does not pass yet.

## 2. Material findings

### D04-10 — Retrieval UNKNOWN is converted into a claim of non-existence

Part V ends the 0.2 self-flag history with:

> “No such record exists yet (Crusher retrieval, 2026-11-11: UNKNOWN).”

That sentence makes a stronger claim than its cited basis supports. The retrieval result is UNKNOWN. Part III's own UNKNOWN definition says a retrieval UNKNOWN is never evidence of non-existence. The requested retrieval may have failed to locate a record; it does not establish that no record exists.

This is not merely cautious wording. It violates the dictionary's own semantic identity rule and its explicit UNKNOWN boundary.

**Required:** Replace the claim with wording such as:

> “No separate CORRECTION record has been located in the requested retrieval; whether one exists remains UNKNOWN.”

Keep the flag OPEN. Do not report non-existence unless a bounded, named, adequately executed search supports an ABSENT finding.

### D04-11 — gate_decision's claimed harness provenance is not pinned or demonstrated

The `attempt_events` definition now supplies the closed values `{ELIGIBLE, BLOCKED}`, which resolves the missing-domain problem as a design definition. It then states:

> “The vocabulary is the one recorded by the frozen battery harnesses”

But no harness, fixture, record ID, commit, hash, or exact section is named. The accompanying retrieval result is that no canonical schema or fixture defining `attempt_events.gate_decision` was retrieved.

The new domain may be a reasonable explicit design choice; the issue is its asserted provenance. Without a pin, the document cannot distinguish a newly selected domain from a domain inherited from historical harness records. That matters because the dictionary repeatedly distinguishes design from retrieved precedent.

**Required:** Either:
1. identify the exact frozen harness records and pin their IDs/versions/hashes, showing that they use these values for this field or equivalent attempt-level gate verdict; or
2. label `{ELIGIBLE, BLOCKED}` explicitly as a new schema design choice, remove the unsupported claim that it is the vocabulary recorded by the harnesses, and retain the statement that no canonical schema/fixture was retrieved.

Do not silently convert the retrieval UNKNOWN into either historical support or historical absence.

## 3. Summary consistency finding

### D04-12 — Part VI's ADOPTION / ALIGNMENT audit row omits the cross-chain condition

Part III now correctly requires same-chain ordering, or an independently established causal-order mechanism for cross-chain records; otherwise the instance is UNKNOWN.

Part VI still summarises FORM as:

> “before/exposure/after records resolve; chain positions verified”

That summary omits the cross-chain alternative and could be read as treating chain positions alone as sufficient for every instance. The detailed definitions are better than the audit summary, but the whole-document audit table should preserve the same condition.

**Required:** Update the Part VI row to state, concisely, that order must be verified within one valid chain, or established by an independent cross-chain causal-order mechanism; otherwise the instance is UNKNOWN.

## 4. Checks retained from Challenge 01

- D04-01 through D04-08 are repaired in the text inspected.
- D04-09 is repaired in the Part III definitions; D04-12 asks that Part VI carry the same boundary.
- D3 remains correct: CORRECTION carries evidence through `basis`; it has no standalone `evidence_class` or `evidence_refs`.
- The 0.2 self-flag's disposition remains OPEN. No separate CORRECTION record has been located in the requested retrieval; existence remains UNKNOWN.
- Crusher's missing canonical `gate_decision` schema/fixture remains UNKNOWN.

## 5. Whole-document reconciliation required

Return one integrated revision addressing D04-10 through D04-12. Keep the existing repairs intact. No patch-only closure declarations: the next candidate should be the complete integrated Dictionary 0.4 again.

## 6. Gate status

**HOLD.** The revision is substantially improved, but the UNKNOWN/non-existence contradiction is material, and the gate-decision provenance needs to be made explicit. The audit summary should also be brought into line with the corrected ordering definitions.

No freeze, replay, validator, or pilot is authorised. The 0.2 self-flag remains OPEN. Ben retains the freeze decision.

*Independent challenge by Alex, 2026-11-11.*
