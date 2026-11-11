# PreSynS Infrastructure-Gap Register 0.1

**Status:** Working register; evidence-led, not an implementation specification  
**Prepared by:** Alex  
**Date:** 2026-11-11  
**Purpose:** Keep PreSynS dictionary and message specification claims separate from infrastructure that has not been established by the retrieved corpus.

This register records what the retrieved Shelf material establishes, what it does not establish, and what machinery would be required before a dictionary definition can claim mechanical enforcement. A retrieval result of UNKNOWN means the retrieved corpus does not establish the mechanism. It is not proof that the mechanism does not exist elsewhere.

## Gap 1 — Authoritative task registration and registry versioning

**Status:** UNKNOWN — not established by retrieved corpus.

**Retrieval basis:**
- Crusher Retrieval 03, verbatim answer: “UNKNOWN — the corpus does not say.”
- Closest sections returned: `d3-v07#004`, `d3-v09-specification#004`, `alex-combined-adjudication-r60rev#001`, `sync-document#001`, `process-tree-v04#005`.
- Recorded in `duenna/plaincode/EXACT-RETRIEVAL-03.md`, commit `cf6f2fe`.

**Not established:**
- The authorised operation that creates a task-registry entry.
- Which seat or mechanism may perform that operation.
- Immutable task identity and registry version identity.
- How a receiver resolves the registry version that governs a commitment.
- How duplicate, conflicting, amended, or retired task entries are handled.

**Machinery required before claiming FORM enforcement:**
- An authorised registration operation with a recorded actor and authority basis.
- A versioned, addressable registry snapshot or equivalent immutable registry reference.
- A task reference that resolves to one entry in the cited registry version.
- Deterministic rejection of missing, ambiguous, stale, or mismatched task references.
- An auditable record of registration and subsequent changes.

**Dictionary boundary:** REGISTER may define the intended act. It must not imply that the registration mechanism exists or that a task reference is mechanically valid until the above is implemented and verified.

## Gap 2 — Atomic live-head update

**Status:** UNKNOWN — not established by retrieved corpus.

**Retrieval basis:**
- Crusher Retrieval 03, verbatim answer: “UNKNOWN — the corpus does not say.”
- Closest sections returned: `execution-contract-v01#013`, `crusher-seat-ruling-01#002`, `d3-v07#042`, `d3-v09-specification#042`, `sync-document#001`.
- Recorded in `duenna/plaincode/EXACT-RETRIEVAL-03.md`, commit `cf6f2fe`.

**Not established:**
- A canonical live-head record for a commitment chain.
- An atomic compare-and-set or equivalent single-winner update.
- A rule for determining which successor becomes operative when two authorised successors target the same predecessor.
- A durable record of rejected or competing successor branches.

**Machinery required before claiming FORM enforcement:**
- One authoritative head per commitment chain.
- A single atomic operation that checks the expected predecessor and changes the head.
- A deterministic conflict result when the expected predecessor is no longer current.
- Preservation of losing successors as visible, non-operative records.
- A read-after-write confirmation identifying the new live head.

**Dictionary boundary:** LIVE and SUPERSEDE can describe intended states and acts. They cannot claim mechanically enforceable live-head semantics until an atomic head-change mechanism exists and is tested.

## Gap 3 — Concurrency and conflict resolution

**Status:** UNKNOWN — not established by retrieved corpus.

**Retrieval basis:**
- Crusher Retrieval 03, verbatim answer: “UNKNOWN — the corpus does not say.”
- Closest sections returned: `crusher-seat-ruling-01#002`, `grounding-gate-v12#011`, `process-tree-v04#016`, `d3-v07#042`, `d3-v09-specification#042`.
- Recorded in `duenna/plaincode/EXACT-RETRIEVAL-03.md`, commit `cf6f2fe`.

**Not established:**
- A general concurrency-control mechanism for simultaneous commitments or state changes.
- A conflict-resolution authority and procedure for competing branches.
- Whether conflicts are resolved by ordering, explicit adjudication, or another authorised mechanism.
- How dependent actions are prevented from proceeding against a conflicted state.

**Machinery required before claiming FORM enforcement:**
- Explicit conflict detection for operations sharing a commitment, task, or registry head.
- A deterministic non-operative state for conflicting successors until resolution.
- An authorised resolution record naming the conflict, affected references, decision, scope, and authority.
- A gate preventing downstream actions from relying on an unresolved branch.
- An audit trail preserving all competing records and the resolution.

**Dictionary boundary:** CONTESTED may describe conflicting evidence or records; it must not be treated as a concurrency-control mechanism. A semantic label does not resolve a live state conflict.

## Gap 4 — General supersession policy and reliance handling

**Status:** Partially evidenced; general policy UNKNOWN.

**Retrieval basis:**
- Crusher found no consolidated or general supersession policy; exact status returned: “UNKNOWN — the corpus does not say.”
- Errata precedent: `process-tree-v04#021a` (v0.3 to v0.4 change record).
- Reliance precedent: `d3-v08-change-record#004` and `fixture-harness-v09#018`.
- Recorded verbatim in `duenna/plaincode/EXACT-RETRIEVAL-03.md`, commit `cf6f2fe`.

**Established:**
- Errata can correct an approved entry without deleting the original record.
- Reliance on checker judgements may need to be explicitly recorded.
- A concrete conditional-reliance rule was implemented in the D3 v0.8 correction pass.

**Not established:**
- A general rule authorising one message to supersede another.
- A general whole-message versus partial-replacement policy.
- A canonical live-head mechanism.
- A general procedure for actions already taken in reliance on a superseded commitment.

**Machinery and policy required:**
- Explicit authority to supersede the relevant commitment class and scope.
- Exact predecessor identification and preservation.
- A prospective effect rule that does not silently rewrite historical action.
- A reliance record identifying actions already taken under the predecessor.
- An authorised STOP or RULING path where reliance requires an operational response.
- Atomic live-head handling as described in Gap 2.

**Dictionary boundary:** SUPERSEDE may state the intended semantics, but its enforcement class must remain explicitly unimplemented/MEANING-dependent until authority, live-head, concurrency, and reliance mechanisms are established.

## Gap 5 — Scoped authority state versus authority registry

**Status:** Authority state and specific delegation evidenced; dedicated registry not found.

**Retrieval basis:**
- `sync-document#003` records current authority state and the specific delegation to Alex for three Duenna-programme acts.
- It records matters retained by Ben alone, including spend, outreach, Shelf publication, accounts, and acts requiring Ben's hands or eyes.
- `process-tree-v04#018` records the earlier structural authority rule. The later sync document explicitly reconciles the specific delegation with that earlier state.
- Crusher found no dedicated scoped-authority or delegation registry document.
- Exact excerpts and reconciliation are recorded in `duenna/plaincode/EXACT-RETRIEVAL-03.md`, commit `cf6f2fe`.

**Established:**
- Authority originates with Ben.
- Delegations are bounded and explicit; the current sync record identifies the delegated Duenna-programme acts.
- Older structural records remain historically preserved and must not silently be rewritten.
- Mechanical binding applies an approved, version-pinned rule; it does not create authority or choose which rule applies (`d3-v07#055`, retrieved in `EXACT-RETRIEVAL-01.md`, commit `e2d70a6`).

**Not established:**
- A dedicated, machine-readable, versioned authority registry.
- A general registry-resolution procedure for arbitrary act classes and scopes.
- A mechanical test that resolves every disputed act against current delegated authority.

**Machinery required before claiming FORM enforcement:**
- A canonical authority-state record or registry with version identity.
- Explicit seat, act class, scope, permitted/prohibited actions, validity interval or state, and source authority.
- Deterministic resolution of the applicable current record, including later specific delegations.
- Fail-closed handling of missing, conflicting, stale, or ambiguous authority records.
- Human/adjudicator resolution where scope interpretation is substantive.

**Dictionary boundary:** AUTHORITY describes the recorded right. The existence of an authority record does not by itself establish a complete registry or mechanical authority enforcement.

## Register-wide controls

1. **UNKNOWN is preserved as UNKNOWN.** No gap is upgraded to “does not exist” solely because retrieval returned no source.
2. **Reported retrieval is not independent verification.** Source excerpts and hashes must be checked against their canonical records before implementation decisions rely on them.
3. **FORM and MEANING remain separate.** A resolvable record or passing mechanical check does not prove that the underlying authority, evidence, or interpretation is substantively correct.
4. **No retroactive edits.** This register does not amend frozen process trees, adjudications, authority records, or prior decisions.
5. **No implied implementation.** Dictionary definitions may describe intended semantics while explicitly recording that enforcement machinery is absent, partial, or UNKNOWN.
6. **Reassessment trigger.** A gap changes status only when an exact source or implemented mechanism is retrieved, inspected, version-pinned, and independently tested.

## Source index

- `duenna/plaincode/EXACT-RETRIEVAL-01.md` — commit `e2d70a6`.
- `duenna/plaincode/EXACT-RETRIEVAL-02.md` — commit `25378b3`.
- `duenna/plaincode/EXACT-RETRIEVAL-03.md` — commit `cf6f2fe`.
- `sync-document#003`, `process-tree-v04#018`, `d3-v07#055`, `process-tree-v04#021a`, `d3-v08-change-record#004`, `fixture-harness-v09#018`.

**Scope note:** This is a gap register, not a design approval, implementation claim, or permission to build the listed machinery. The PreSynS pilot remains paused.