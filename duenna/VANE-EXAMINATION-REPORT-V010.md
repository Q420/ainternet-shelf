# VANE — INDEPENDENT EXAMINATION REPORT, D3 v0.10

*Saved verbatim from Vane's bridge message pb-mwbee83z-2-4o7s,
2026-11-10 (~15:46 PST). Vane pulled the evidence himself from
github.com/Q420/ainternet-shelf through his own GitHub connection
and states he deliberately did not consult Claude's report.*

---

Vane — independent examination of D3 v0.10

PB-ID: pb-20261110-vane-v010-independent-examination

Repository: Q420/ainternet-shelf
Specification: D3 v0.10
Examination basis: specification, change record, harness source and fixture results retrieved independently through GitHub.

1. R47 — Trigger-content admission

PASS

The repaired fold now actually reads trigger-carried content_predicates and records the examined content separately from admitted determinations.

FX-R47b is materially stronger than its v0.9 predecessor:

Qualifying content is present and demonstrably examined.

Removing that content empties the examination record.

Neither conditional trigger establishes progress or satisfaction.

Supplying the same predicates through the admitted-determination channel does satisfy.

The distinction between examination and admission is preserved.

I accept this repair.

2. R60 — Checker contract

FAIL — residual defect

The implementation has made substantial progress. It now executes _preservation_check, computes an implementation hash, records the input identity and version, and rejects incomplete or mismatched verdict metadata.

However, one important binding remains unenforced.

CheckerContract.__init__() accepts an arbitrary procedure identifier. run() always executes _preservation_check, regardless of that identifier.

Consequently, a contract can declare a fictitious procedure name, execute the preservation checker anyway, stamp the verdict with that fictitious name, and subsequently pass validate_verdict().

The validator compares the verdict's procedure string against the contract's procedure string, but neither is independently bound to the callable actually executed.

This is a different failure from the v0.9 forged-verdict problem. The repaired fixture tests whether a verdict can misrepresent its contract. It does not test whether the contract itself can misrepresent its executed procedure.

Required correction: bind the declared procedure identity to the actual executable validation procedure. Reject an unrecognised or mismatched identity rather than allowing arbitrary strings.

The implementation hash must identify that bound procedure.

I do not accept R60 as fully repaired.

3. R65 — Provenance completeness

PASS, within the authorised five-relationship scope

The repaired validator now checks:

Missing references.

Unexpected references.

Incorrect reference values.

Disagreement between components_present and the required set.

The formerly passing empty-reference case.

The deletion tests are particularly important. They demonstrate that completeness is tested, not merely the correctness of whatever happens to be supplied.

One boundary worth recording: the validator receives its required target set as an argument. The fixture supplies the correct five-element set, so the fixture demonstrates the intended behaviour for that set. It does not independently establish the authority of arbitrary target sets supplied by other callers.

This is a scope qualification, not a failure of the five targeted fixture cases.

I accept the authorised R65 repair.

4. Examination disposition

R47 — PASS
R60 — FAIL — procedure identity not bound to execution
R65 — PASS, with scope qualification

Overall: v0.10 is NOT READY FOR APPROVAL.

The R60 finding is sufficient to prevent acceptance of the three-repair package as complete.

5. Evidence boundary

I retrieved the specification, change record, traceability material, harness source and fixture results from the repository.

The published results report 31/31 passing fixtures and three successful sabotage runs. I have treated those as implementer-reported evidence, not as independently reproduced execution results.

I have not treated the other examiner's conclusions as evidence for this examination.

I also make no claim that this examination resolves UX-1 or checker independence. Those remain explicitly unresolved in the specification.

6. Recommendation

Return R60 for a narrowly scoped correction.

The correction should add a negative test that supplies a false procedure identity at contract construction, not merely at verdict construction.

Then rerun the complete fixture suite and return the corrected package for independent examination.

No approval is given or implied by this report.

— Vane

---

*Framing lines from the same bridge message:* Vane noted the plan
records his examination as deferred with the pull letter prepared,
and that he would distinguish current instructions from the
historical plan rather than silently treating the older status as
superseded. His closing line to Remmy: "the important result is
that the new transport works, and the examination has produced a
concrete, independently reasoned residual finding. I would rather
return one precise defect than certify a repair that still has a
hole."

*Remmy's confirmation (2026-11-10 ~15:47): reproduced by execution
— a CheckerContract constructed with procedure "fictitious
procedure XYZ" executed _preservation_check, stamped the verdict
with the fictitious name, and validate_verdict returned ACCEPTED.
Vane's mechanism is confirmed. Note the independence result: his
R60 defect (procedure identity unbound) is a DIFFERENT mechanism
from Claude's (digest-mismatch branch unexercised); both examiners
returned R60 FAIL, R47 PASS, R65 PASS with a caller-supplied-set
qualification.*
