# Vane — Conformance Brief Rev 2 Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~08:33 MST (PB-ID pb-mwqkidbn-2e-gf37). She examined Rev 2 in full at head 3303900d (blob 485383ef) and checked its authority references against the pinned Rev 9 artifact.

**Verdict: REV 2 NOT YET ACCEPTED.** The revision is substantially stronger — the seven settlement decisions are incorporated, the three boundaries have concrete tests, the eligibility-vs-trustworthiness distinction is preserved. Two substantive instrument defects and several narrower points keep the settlement round open. **No build or trial is authorized by this verdict.**

## Blocking 1 — the candidate still receives a contradictory schema

§3 gives the candidate Annex B.1 verbatim; §4 tells the validators to accept alpha/beta in region-identifier positions despite B.1's `format: uuid`. That resolves the validator's interpretation, not the candidate's information: the candidate sees Annex A (regions are alpha and beta), Annex B.1 (region identifiers must be UUIDs), and no explanation of the gate-scoped interpretation. The conflict has moved from the validator boundary to the **candidate-facing boundary**. **Required:** settle exactly what the candidate receives as the schema contract. **Her preferred direction:** a separately pinned, explicitly named **Annex A gate-schema profile** supplied as data alongside the unchanged Annex A instruction — disclosing the symbolic region identifiers and the gate-specific treatment of the absent authentication and discovery mechanisms; containing no adequacy rubric or coaching. The original Annex B.1 remains unchanged and authoritative for fabric submissions. If unmodified B.1 is retained as candidate-facing material instead, another explicit mechanism must make the gate-scoped interpretation part of the candidate's known contract — the interpretation cannot stay hidden in the validators. §3's claim that Annex A + B.1 are the complete candidate-facing material must be revisited: the precise artifacts, their hashes, their relationship, and their delivery on each route are pinned together.

## Blocking 2 — the gate profile needs a complete candidate-facing contract

Fields whose runtime semantics are absent from the miniature: author must be a UUID but there is no authenticated identity; discovery_source must use one of three values but no discovery mechanism is described; discovery_ref must be a positive integer but no discovery event exists. §4 settles what the validators waive; it does not settle **what the candidate is being asked to provide**. The profile must define the candidate-facing treatment (e.g. is author simply a syntactically valid UUID supplied by the candidate? is discovery_ref an uninterpreted positive integer for this instrument? what does discovery_source mean when no discovery event is recorded?). Modest, explicit rules — not left for candidates to guess or adapters to fill in. The dependency-identity disposition (no ID invented; removal cannot pass against the fixture as supplied) is correct and kept.

## Additional corrections

**A. Scoring of refusals and malformed responses.** §7 requires a scoring sheet for every trial but does not settle how the five Annex C criteria are scored when there is no parseable contribution (refusal, malformed fragment) — including whether criterion 5 can be met independently of the other criteria. The scoring workflow must not silently convert a schema failure into an adequacy score by assumption.

**B. The sealed-ground-truth boundary.** §12 (no trial component, including scoring tooling, can read Annex D) and §13 (examiner conclusions against sealed ground truth in layer 4) can coexist, but the temporal/authority boundary must be explicit: the examiner's ground-truth examination occurs **outside** the trial execution and scoring workflow, **after** the candidate-facing evidence and Annex C adequacy scores are fixed; it must not influence the adequacy verdict or be written into layers 1–3.

**C. Contamination exclusion.** Define it as **known or demonstrable exposure**, not an unbounded claim about what may have appeared in pretraining. The exclusion's test must be operationally meaningful.

**D. §§14–15 reconciliation.** §14 says unsettled matters are listed in §15 and remain open; §15 says nothing else remains open and describes its matters as build-round determinations. Reconcile: build-time demonstrations are not open design decisions, and the text must say so consistently.

## Accepted and preserved (not to be reopened)

The prompt-level trial separate from the six-region experiment; the driver administers but does not enrich or repair; demonstrable plant separation; the four distinct evidence layers; the 120-second timeout and no-retry rule; two independently implemented validators with no shared custom code and no majority resolution; examiner ownership of every adequacy verdict with blinded scoring and explicit review of mechanical pre-checks; the three-route slate subject to catalogue pinning and route eligibility demonstrations; the fingerprint-based re-trial policy and fresh-context requirement; no accepted fabric code changes and no alteration of the pinned authority artifacts. She also accepts the §3 distinction between settling the delivery contract now and demonstrating provider wire mechanics in the build — but the **semantic contract must be complete before that demonstration begins**.

## Next action

Rev 3 as a narrow settlement correction; Rev 1, Rev 2, Rev 9, A1, and all accepted fabric artifacts preserved unchanged. Rev 3 settles: the candidate-facing gate schema artifact and its relationship to Annex B.1; the candidate-facing treatment of the identity and discovery fields; the scoring and ground-truth timing points; the operational contamination test; the §§14–15 reconciliation. She will then examine **the exact candidate-facing bytes and the resulting validation contract together**, not as two independently plausible documents. Her closing line: the candidate must not be put in a position where the correct answer depends on knowing an exception that only the validators have been told about.
