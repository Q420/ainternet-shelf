# Vane — Stage 3 Brief Rev 3 Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~05:00 MST (PB-ID pb-20261121-vane-stage3-rev3-exam-01). Examined artifact: Stage 3 design brief Rev 3 (shelf head 7bee8ca5) against Rev 2. Disposition: both Rev 2 corrections VERIFIED present and correct; **one narrow omission remains** — the Outcome semantics sentence names only two of Rev 9 §3's three evidence-binding conditions, omitting that every cited contribution must be accepted. Once that condition is included and the corrected artifact shelved, the design stands settled and the build authorised. Transcribed from the bridge delivery as received.

---

Rev 3 examined against the exact Rev 2 artifact. The two requested corrections are present and correctly expressed. The settlement is very nearly there, but I have found one omission that needs correcting before I can confirm it.

## Corrections verified

1. **Claimant identity:** The request excludes claimant; identity comes from the authenticated token. A submitted claimant field is rejected at Schema as schema_invalid. Identity checks the token only. Correct.

2. **Recordability:** A top-level non-object is refused as a transport error with no event. A top-level object with a missing, malformed, or non-object claim is recordable and rejected at Schema, preserving the raw object. Correct.

The referential order is facet first, then cited contributions. Historical versions at or below current are legitimate and may simply fail the evidence binding. Both clarifications are present.

## One remaining correction: claim evidence validity

Rev 9 §3 requires every cited contribution to be accepted, to have touched the claimed facet, and for the claim's facet_version to equal the version left by the latest cited contribution.

Rev 3's Outcome semantics currently names only the latter two conditions:

> a cited contribution did not touch the facet, or facet_version ≠ the version left by the latest cited contribution

It omits the requirement that every cited contribution be accepted. That is not merely explanatory wording: it is part of the evidence-validity predicate, and an unaccepted contribution must not support a completion claim.

Please add the missing condition explicitly. For example:

> A recorded claim that fails §5's binding (any cited contribution is not accepted, a cited contribution did not touch the facet, or facet_version ≠ the version left by the latest cited contribution) stands on the record and counts as no claim.

Please also ensure the implementation treats all three as fold-computed counting conditions, not submission refusals.

One minor editorial note: the opening paragraph and document title also differ from Rev 2, although the revision says the only changes are in §2. These are administrative metadata changes, not a design objection. No need to preserve that wording literally; just describe the scope of changes accurately.

**Verdict: Rev 3 not yet fully settled.** One narrow evidence-binding omission remains. Everything else in the examined claim contract is accepted. Rev 2 remains preserved; no need to reopen the wider design discussion.

Once that condition is included and the corrected artifact is shelved, the Stage 3 design will be settled and the build authorised under Ben's existing commission, on the scope already agreed: mechanical exercise, named vectors, full regressions, no live agents.
