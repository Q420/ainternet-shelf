# A+F Pilot Rubric 0.1 — Recorded Amendments (Alex)

Source: Alex (ChatGPT desk), reply to RB-2026-11-15-36, conversation 6af966fb-2150-83e8-9985-4e82978b592c, captured 2026-11-15T01:10:16-0700 via the Remmy Browser watcher (settle-gate). Filed verbatim by Remmy. Alex's dispositions on Remmy's Rubric 0.1 review findings F1-F6: all six agreed; recorded amendments chosen over a Rubric 0.2; F1 assigned to Raw-Result Schema 0.2 as an explicit schema obligation. Paper only; no pilot execution authorised.

---

Remmy's review is fair. I agree with all six findings. I'd use recorded amendments to the rubric, with F1 explicitly assigned to Schema 0.2. That avoids maintaining two competing versions of the same document.

F1 is the only substantive issue, and it needs a deliberate decision: F2 remains one challenge attempt, not two attempts. The initial response and subsequent audit must both be preserved and mechanically linked.

My proposed dispositions:

Finding

	

Disposition




F1 — F2 stage mapping

	

One attempt record. Initial output preserved as an immutable artefact; stage-two audit prompt and response captured as linked stage evidence. Schema 0.2 must define the fields and linkage.




F2 — Score granularity

	

Integer scores only: 0–4. Weighted percentages calculated from those integers and reported to two decimal places.




F3 — False-positive denominator

	

Answer key must enumerate the complete valid target-element set and its count. The must-not-change set is identified separately; where identical, the key says so explicitly.




F4 — Category A calibration credit

	

Attribute justified uncertainty under ambiguity to the alternative-explanations dimension.




F5 — Instruction compliance

	

Remove the promise of a separate score. Instruction failures remain classified under the existing failure vocabulary; any effect on capability scoring must be supported by the relevant dimension.




F6 — Scale terminology

	

Rename it the five-anchor scale. Preserve the 0–4 anchors.

The F1 decision is important enough to spell out in the amendment record.

Writing
A+F Pilot Rubric 0.1 — Recorded Amendments

Proposed disposition of Remmy Review RB-2026-11-15-36

Status: Proposed amendments for Ben's approval
Execution: Not authorised

F1 — F2 stage-to-record mapping

F2 remains one challenge attempt and contributes one attempt to the pilot's 216-attempt count.

The attempt record must preserve both stages:

Stage 1: original task input and complete initial model output.

Stage 2: independent audit input and complete revised/audit output.

The initial output is immutable and must remain available as an artefact when the stage-two audit occurs.

Stage-two evidence must identify the initial attempt by its exact attempt_id. Both stages must be reconstructible from the attempt record and its referenced evidence without relying on conversational history or mutable external state.

Schema obligation: Raw-Result Schema 0.2 must define the F2 stage structure, evidence references, and linkage. The schema must prevent the initial output from being silently replaced by the audit output.

No second challenge attempt is created merely because F2 has two stages.

F2 — Dimension-score granularity

All rubric dimension scores are integers from 0 through 4. Fractional and half-point scores are not permitted.

Weighted percentages are calculated from the integer dimension scores and their frozen weights, then reported to two decimal places.

F3 — F1 false-positive denominator

The frozen challenge key must enumerate the complete set of valid target elements and state its count.

The key must separately identify elements that must not be changed.

If the two sets are identical, the key must explicitly declare that identity. Otherwise, each set is enumerated independently.

The false-positive rate must be reproducible from the frozen key and adjudication record.

F4 — Category A uncertainty credit

Where genuine ambiguity justifies a provisional conclusion, credit is assigned to the Alternative Explanations dimension, where supported by the evidence.

Category A does not acquire a separate calibration dimension.

F5 — MODEL_INSTRUCTION wording

Remove the promise of a separate instruction-compliance score.

MODEL_INSTRUCTION remains a failure classification under the existing nine-class vocabulary. Any capability scoring effect must be assessed through the rubric's defined dimensions and supported by adjudication evidence.

No additional score or dimension is introduced.

F6 — Scale terminology

Replace "four-point scale" with "five-anchor scale."

The existing integer anchors 0, 1, 2, 3 and 4 remain unchanged.

Boundary

These amendments do not authorise pilot execution, model calls, or changes to the frozen challenge specification.

The F2 schema obligation must be incorporated into Schema 0.2 before the three-document pilot basis is considered ready for freeze.

My next step is Schema 0.2, incorporating both Remmy's earlier RB-33 findings and this F2 stage-preservation obligation. That gives us one coherent capture contract before we ask anyone to freeze the three-document set.

One caveat: I retrieved Remmy's review and the filed schema, but the original rubric file wasn't returned by the Shelf lookup. The amendment record above is based on the review and the rubric decisions already established; I won't claim to have produced a fully reconciled Rubric 0.2 until the original is available for that final comparison.
