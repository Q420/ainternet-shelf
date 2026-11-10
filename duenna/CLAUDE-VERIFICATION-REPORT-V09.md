# Claude — Independent Verification Report, D3 v0.9

Delivered 2026-11-10 via Ben (ferried, outside the bridge), from the v0.9 ferry package v2. Recorded verbatim as received.

---

The v0.9 package has no register or matrix, so I'll start with the instructions and the change record to see what v0.9 claims to do.

The change record says v0.9 is byte-identical to v0.8 apart from the R42 text and the header. I have the v0.8 spec from the earlier package, so I can diff the two directly.

The spec diff matches the change record in substance: the status header, the B-1 Behaviour, and the K-1 paragraph are the only changes. But the new header asserts v0.8 was approved, which v0.8's own immutable header said was not the case. Next I'll re-run the v0.9 harness in isolation and compare its output with the delivered results.

The re-run gives 31/31 PASS, identical to the delivered results. The "if adopted" phrasing is gone from the spec. Next I'll read the rewritten fixtures for the six FAIL slots, since passing a test doesn't show the test is meaningful.

The R47 fixture still doesn't exercise what its comment describes. FX-R47b's trigger carries `content_predicates`, but `fold()` never reads that field. I'll confirm by grep, then read R56, R60, and R65.

The R60 "validation procedure" fixture only compares a string the contract itself wrote, and FX-R47b still ignores the trigger's qualifying content. Next I'll read the traceability, fixture results, and register documents and compare them with my derivation.

The traceability and fixture documents both say FX-R47b now tests the trigger's qualifying content. The harness never reads that field, so I'm treating the R47 claim as unsupported. Last, I'll confirm the four gaps are still untested in v0.9.

I've verified v0.9 against its own sources. The fixes for R56, R63, and R65 hold up, but R47 is not fixed, and R60 is only partly fixed. The R42 text change is in place, but the status problem it raised is still there.

**The six FAIL slots**

- **R42, PASS.** Option 1 from the matrix is taken: the binding refusal is now unconditional, and the "if adopted" phrasing is gone. The spec diff confirms this. See S2 below for the status issue it leaves open.
- **R47, FAIL.** The change record says FX-R47b now shows a trigger with qualifying content establishing nothing. The harness never reads `content_predicates`, so the test passes because no determinations are supplied. The fold's C-2 INDETERMINATE resolution is real, and FX-R47c is fixed.
- **R56, PASS.** FX-R56a and FX-R56b cover the three-way separation, each role's necessity, and all the listed substitutions and self-verification. The validator is defined in the test, so this shows internal consistency.
- **R60, NOT VERIFIED.** Four of the five properties are exercised by independent fixtures. The "validation procedure" fixture (FX-R60b) only checks a string the contract wrote into its own verdict, so that property is not enforced.
- **R63, PASS.** Block order is checked on a stream from the binding machinery, with an interleaved negative. The stable identity, record position, and instance checks are covered as well.
- **R65, PASS.** Each of the five provenance relationships is mismatched in turn and fails.

**Scope and status**

- **Scope discipline: PASS.** Against the v0.8 spec (hash `3e053efc…`, which I re-computed), the spec differs only in the status header, the B-1 Behaviour, and the K-1 R42 paragraph.
- **S1, UX-1…UX-5 open and non-binding: PASS.** Unchanged.
- **S2, PROPOSED requirements not binding: FAIL, now sharper.** B-1 is still PROPOSED, but its text now says the refusal is "required by THIS requirement". That is the same status problem as before, but stated unconditionally. The matrix allowed this route, so the adjudicator has to decide whether an unconditional refusal can sit inside a PROPOSED requirement.
- **S3, v0.9 not represented as approved: PASS for v0.9.** The header says "NOT APPROVED".
- **S4, no Stage 2 work: PASS for the text only.** The spec and change record both say Stage 2 is not authorised.
- **S5, frozen artefacts: NOT VERIFIED.** The v0.8 hash is confirmed. v0.7 and the execution contract are not in the package.
- **Four gaps (R38, R48, R53, R55): still open, and correctly described.** The harness has no fixture for any of them.

**Discrepancies to take to adjudication**

1. The change record and fixture results say FX-R47b tests qualifying trigger content. The code doesn't read that content.
2. The v0.9 header says v0.8 was approved (citing pb-mwacx009). The immutable v0.8 header says "NOT APPROVED". The approval record is not in the package.
3. The change record cites Alex's authorisation (pb-mwad2zc6) and Ben's approval as "reported in that letter". Neither is in the package.
4. The traceability says the other slots were examined and adjudicated, but the adjudication record is not in the package.

**Reproduction**

I re-ran the harness in an isolated copy: 31 PASS, 0 FAIL. Apart from the Python version string, the output matches the delivered results exactly. Every file hash in the package matches the list in the handoff.

The honest headline for Alex: R56, R63, and R65 are now substantively fixed, R42's text is consistent, but R47 is not fixed, R60 is only partly fixed, and the status issue in S2 and the approval-record gaps need deciding. Do you want this as a published page, like the v0.8 report?
