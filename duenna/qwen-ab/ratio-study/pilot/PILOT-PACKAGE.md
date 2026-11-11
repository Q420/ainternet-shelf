# FEASIBILITY PILOT — CONSTRUCTION PACKAGE V9

Correction per Alex's V8 re-inspection (d3bfde2
preserved in history), narrowly scoped as directed:
F-PROBE's assertions now cover the properties the
package claims. **Call sequence** is asserted
structurally — the unaided call first, the frozen
flow's internal call between, the revision call last.
**The three records** are asserted separately and
exactly: worker_before, mechanical, and worker_after
each equal the expected label set; both raw texts are
present and distinct. **Transmission** is asserted
per statement: the revision prompt must carry all
four mechanical classifications verbatim, not merely
mention one label. **Evidence identification** is
asserted separately from agreement, by route: S1
verbatim-quote, S2 grounded-absence, and S3 also
grounded-absence — the stub asserts the cited
section's absence and the artefact is verifiably
absent, so S3 qualifies honestly; S4 supplied no
evidence and is excluded. **Adoption** is recomputed
independently in the fixture and compared against the
probe's measurement, and a new probe field,
evidence_backed_adoption, lists only statements where
the label agrees AND the evidence was identified.
The regenerated runtime demonstration shows why the
distinction matters: agreement on all four statements
with evidence_backed_adoption EMPTY — an honest
negative, recorded as one, not a broken measurement
and not a forced positive. (One fixture expectation
was corrected during this round when the measurement
proved righter than the expectation — S3's grounded
absence — and the correction is commented in the
source.) All fixtures pass in both layouts.
**No pilot runs, no live model calls. Awaiting
Alex's pilot decision.**
