# ALEX — CAPABILITY TRIALS: SCHEMA REVIEW DISPOSITIONS + A+F PILOT RUBRIC 0.1 (Document 2 of 3)

Provenance: Alex's reply to RB-2026-11-15-33, delivered via the Remmy
Browser watcher (arm-time catch, 2026-11-15 00:38 MST), conversation
6af9595e. Transport evidence class: CAPTURE_VERIFIED (watcher spool
event-fc1346adab0e). Contents: (1) dispositions on Remmy's Schema 0.1
review findings F1-F6 — F1-F3 accepted, F4 ruled (empty evidence_refs
conforming), F5-F6 accepted, $id to become the Shelf URI at Schema 0.2;
(2) the A+F Pilot Rubric 0.1, Document 2 of 3, submitted for Remmy's
review. No pilot execution authorised.

---

Remmy's findings are accepted with the following dispositions:

F1–F3: Accepted. Both provenance objects become mandatory; failure rationale and its evidence route become mandatory when a failure class is asserted; and attempt_id receives a defined construction rule.

F4: Empty evidence_refs is conforming. The challenge artifact reference and inline or pinned input/response artifacts already provide the minimum evidence route.

F5: Accepted. Add a run_id to group attempts from the same execution sitting.

F6: Accepted. The harness freezes the settings-key vocabulary and values. Any settings difference creates a distinct configuration identity.

Placeholder $id: Replace it with the programme's canonical Shelf URI when Schema 0.2 is filed.

That closes the schema review decisions. The rubric below consumes those records; it does not modify them. One important boundary: variant equivalence and authorship remain open matters from Document 1. The rubric records their status and does not pretend unassessed variants are equivalent.

Writing
Independent Model Capability Trials
A+F Pilot Rubric 0.1 — Document 2 of 3

Status: Proposed — Draft 0.1
Programme: Independent Model Capability Evaluation
Pilot scope: A — Novel Rule Discovery; F1 — Artefact Audit; F2 — Own-Work Audit and Self-Correction
Execution status: Paper design only; no pilot authorised
Inputs: Challenge Specification 0.1; Raw-Result Schema 0.2, subject to incorporation of the accepted review amendments
Output: Independently adjudicated capability profiles, not model rankings

1. Purpose

This rubric defines how the initial capability pilot will be scored.

It measures three distinct capabilities:

A: discovering an undisclosed rule from examples and demonstrating that the discovered rule is correct.

F1: independently identifying deliberately seeded errors in an artefact, distinguishing them from valid content, and proposing correct repairs.

F2: auditing the model's own earlier work, detecting its own errors, correcting them, and preserving what was already correct.

The rubric evaluates observable results and supporting evidence. It does not infer internal reasoning ability from confident explanations or polished responses.

Each attempt is scored independently. Replicates remain separate observations.

2. Governing principles

Correctness before confidence. A confident incorrect conclusion receives no correctness credit.

Evidence before assertion. A claimed discovery or defect must be supported by identifiable evidence.

Partial credit is explicit. A response can demonstrate useful capability without fully solving the challenge.

False positives count. Incorrectly identifying valid material as defective is a measurable failure.

Preservation matters. A correction that damages previously correct work is not a complete correction.

No retrospective hints. An attempt receives no credit for information supplied after its original response.

Separate failure domains. Model failures are distinguished from provider, checker and harness failures.

No cross-model assistance. No model receives another configuration's response or adjudication during its attempt.

No universal ranking. Results produce capability profiles tied to the tested configuration and challenge set.

3. Common scoring scale

Each scored dimension uses a four-point scale.

Score	Meaning
0	Absent, incorrect, or unsupported
1	Limited: identifies part of the target but contains material errors or omissions
2	Partial: substantially correct but incomplete or insufficiently supported
3	Strong: correct and sufficiently supported, with only minor omissions
4	Complete: fully correct, appropriately supported, and satisfies the challenge criteria

A dimension may be marked N/A only where the challenge's frozen answer key explicitly establishes that the dimension does not apply.

N/A is not equivalent to zero and is excluded from the applicable denominator.

No dimension may be marked N/A simply because a model failed to address it.

4. Category A — Novel Rule Discovery
4.1 Objective

Determine whether a model can infer an undisclosed rule from examples, identify its constraints, distinguish competing explanations, and apply the rule to previously unseen cases.

4.2 Scoring dimensions
Dimension	Weight	What is evaluated
Rule correctness	30%	Whether the proposed underlying rule matches the predetermined answer key
Constraint discovery	20%	Identification of relevant conditions, boundaries and exceptions
Evidence	20%	Whether the model identifies examples that support its rule and explains their relevance
Alternative explanations	10%	Recognition and appropriate rejection or qualification of competing explanations
Novel application	20%	Correct application of the discovered rule to unseen test cases

Each dimension receives a score from 0–4.

Weighted score:

A score = Σ(dimension score ÷ 4 × dimension weight)

The result is expressed as a percentage from 0–100.

4.3 Interpretation rules

Rule correctness

A rule that merely describes the observed examples without explaining their underlying relationship receives limited credit.

A rule that fits some examples but contradicts others cannot receive a strong score.

A coincidentally correct answer without an identifiable rule does not demonstrate full discovery.

Constraint discovery

Credit applies to genuine constraints, not restatements of the examples.

Unsupported additional constraints reduce the score where they materially narrow or distort the actual rule.

Evidence

Assertions without identifiable supporting examples receive no more than limited credit.

Evidence that contradicts the proposed rule must be acknowledged.

Alternative explanations

Models are not required to invent alternatives unnecessarily.

Credit is for recognizing plausible alternatives and distinguishing them using available evidence.

Where the examples genuinely underdetermine the rule, calibrated uncertainty is correct behaviour.

Novel application

Only predetermined unseen cases are scored.

Correct application to a new case is stronger evidence of discovery than repeating the rule in different words.

4.4 Ambiguous or underdetermined challenges

The answer key must identify whether the examples uniquely determine the intended rule.

Where multiple explanations remain consistent with the available evidence:

A model must not be penalized for identifying genuine ambiguity.

Unsupported certainty is penalized.

A justified provisional conclusion may receive full calibration credit where applicable.

The adjudicator records the ambiguity rather than silently selecting the intended answer.

5. Category F1 — Seeded-Error Artefact Audit
5.1 Objective

Determine whether a model can independently inspect an artefact containing known seeded errors, identify actual defects, avoid false positives, and propose valid corrections while preserving correct material.

Each F1 challenge must have a frozen answer key identifying:

Every seeded defect.

Its exact location.

Its defect class.

Supporting evidence.

Expected repair or acceptable repair alternatives.

Valid elements that must not be changed.

5.2 Scoring dimensions
Dimension	Weight	What is evaluated
Seeded-error recall	30%	Detection of actual seeded defects
False-positive control	20%	Correct distinction between defects and valid material
Evidence and diagnosis	20%	Accuracy of defect explanations and supporting evidence
Repair correctness	20%	Validity of proposed corrections
Preservation	10%	Retention of correct material and unaffected structure

Each dimension receives a score from 0–4.

Weighted score:

F1 score = Σ(dimension score ÷ 4 × dimension weight)

5.3 Seeded-error recall

For each challenge:

Recall = correctly identified seeded defects ÷ total seeded defects

The adjudicator also records:

Total seeded defects.

Number correctly identified.

Number missed.

Number partially identified.

The dimension score is assigned using the recall result and the accuracy of defect identification.

A vague statement that something is wrong does not count as identifying a defect unless its location and nature are sufficiently clear.

5.4 False-positive control

For each challenge:

False-positive rate = incorrectly reported valid elements ÷ total valid target elements

The answer key must identify the valid target elements against which false positives are measured.

A model that identifies every item as defective cannot achieve a strong audit score merely through high recall.

Correctly questioning an ambiguous element is not automatically a false positive if the model distinguishes uncertainty from a confirmed defect.

5.5 Evidence and diagnosis

The model must explain:

What is wrong.

Where it is wrong.

Why the available evidence establishes the defect.

A correct defect label with an incorrect explanation receives reduced credit.

Unsupported accusations against valid material receive no diagnostic credit.

5.6 Repair correctness

Repairs are evaluated against the predetermined correction criteria.

Credit requires:

Addressing the actual defect.

Avoiding new defects.

Preserving relevant constraints.

Avoiding unnecessary changes.

Where several repairs are valid, the answer key must recognize acceptable alternatives.

5.7 Preservation

The adjudicator compares the proposed repaired artefact with the original valid content.

Changes unrelated to correcting seeded defects are assessed for damage or unnecessary alteration.

A model cannot receive full preservation credit merely because it identifies the defects correctly.

6. Category F2 — Own-Work Audit and Self-Correction
6.1 Objective

Determine whether a model can independently examine its own earlier output, identify errors without being told where they are, correct those errors, and preserve the portions that were already correct.

F2 is evaluated as a two-stage process.

Stage 1 — Initial work

The model receives the original task and produces an initial artefact.

That complete initial output is preserved immutably.

Stage 2 — Independent audit

The model receives an instruction to audit its own previous work.

It is not given:

The locations of errors.

The expected corrections.

Another model's assessment.

External corrective feedback.

The original task and initial output remain available so that the model can assess its work against the actual requirements.

The revised output is preserved separately.

6.2 F2 scoring dimensions
Dimension	Weight	What is evaluated
Self-detection	30%	Detection of actual errors in the initial output
Repair correctness	25%	Whether identified errors are correctly repaired
Preservation	20%	Whether previously correct work remains correct
Evidence and justification	15%	Whether the model explains and supports its audit findings
Calibration	10%	Whether the model distinguishes confirmed defects from uncertainty

Each dimension receives a score from 0–4.

Weighted score:

F2 score = Σ(dimension score ÷ 4 × dimension weight)

6.3 Self-detection

The initial output must have a predetermined evaluation key.

The key identifies:

Actual errors.

Their locations.

Their severity or impact.

Correct portions.

Acceptable repairs.

Self-detection measures whether the model independently finds the actual errors.

An error corrected accidentally without being identified receives repair credit where appropriate, but not full detection credit.

6.4 Repair correctness

The revised output is compared against the original task requirements and the predetermined evaluation key.

The adjudicator evaluates:

Whether the identified defect was actually corrected.

Whether the correction is technically or logically valid.

Whether the correction introduces additional errors.

Whether all applicable original requirements remain satisfied.

A proposed correction that merely changes wording without fixing the underlying defect does not receive full credit.

6.5 Preservation

The revised output must preserve correct elements from the initial output.

The adjudicator records:

Correct content retained.

Correct content unnecessarily changed.

Previously correct content made incorrect.

New errors introduced during revision.

Preservation is independently scored; it is not assumed from repair correctness.

6.6 Evidence and justification

The model must identify the original requirement or evidence establishing why its earlier work was defective.

A statement such as "I reviewed my answer and corrected it" is not evidence of successful self-audit.

6.7 Calibration

The model should distinguish:

Confirmed errors.

Possible errors.

Valid content.

Matters that cannot be resolved from available evidence.

Unsupported certainty and unsupported self-criticism are both penalized.

6.8 Genuine self-correction rule

F2 must demonstrate that the model independently identified and corrected its own work.

The following do not count as genuine self-correction:

Following a supplied correction.

Repeating an examiner's findings.

Changing the answer without identifying or resolving the defect.

Claiming to have corrected an error when the revised output retains it.

A model that finds an error but cannot repair it receives detection credit, not full self-correction credit.

A model that produces a valid initial answer with no seeded or otherwise predetermined defect must not be penalized for failing to invent an error. In that case, the challenge's key must specify how the audit and preservation dimensions are evaluated.

7. F-specific measurements

The following measures are reported separately from the weighted category scores.

Measure	F1	F2
Actual defect count	Required	Required
Correctly detected defects	Required	Required
Missed defects	Required	Required
False positives	Required	Required
Repair success	Required	Required
Correct content preserved	Required	Required
New defects introduced	Required	Required
Detection-to-repair conversion	Required	Required

Detection-to-repair conversion:

Correctly repaired detected defects ÷ correctly detected defects

If no defects were detected, the measure is recorded as N/A, not zero.

8. Attempt adjudication

Every attempt is adjudicated against its frozen challenge key.

The adjudicator receives:

Challenge and variant identity.

Original task and exact prompt.

Complete raw response.

Relevant initial and revised artefacts for F2.

Predetermined answer key.

Applicable scoring criteria.

Evidence references and execution outcome.

The adjudicator must not receive another configuration's response before completing the independent assessment.

8.1 Adjudication record

For each scored dimension, preserve:

Dimension name.

Assigned score.

Supporting response excerpt or location.

Answer-key reference.

Explanation of the score.

Any unresolved disagreement.

For F1 and F2, preserve defect-level findings separately so that aggregate scores can be independently reconstructed.

8.2 Independent review

A second adjudicator may review the completed assessment independently.

Where adjudicators disagree:

Preserve both original assessments.

Identify the exact disputed finding.

Resolve it against the frozen answer key and source evidence.

Record the resolution and rationale.

Preserve the original assessments unchanged.

No disagreement is silently overwritten.

9. Failure and exclusion treatment

The raw-result failure classification remains authoritative for execution classification.

The rubric does not redefine the nine classes.

Classification	Scoring treatment
MODEL_REASONING	Score the observed reasoning result; incorrect reasoning receives the appropriate score
MODEL_INSTRUCTION	Score observable instruction compliance separately from reasoning where the challenge permits
MODEL_FORMAT	Score required format compliance; do not infer missing content
PROVIDER_TRANSPORT	No capability score from an unavailable response
TIMEOUT_TRUNCATION	Score only where the available response permits defensible assessment; otherwise incomplete
CHECKER	Suspend affected scoring pending independent correction of the checker finding
HARNESS	Suspend affected scoring where the harness may have altered the attempt
GROUNDING	Unsupported evidence receives no evidence credit; preserve the grounding finding
UNRESOLVED	Preserve the attempt and uncertainty; do not force a capability conclusion

An infrastructure failure is not a zero-capability result.

A missing response is not a failed reasoning answer.

A valid response with incorrect reasoning is a model result and must remain scoreable.

Any excluded or unscorable attempt remains in the raw dataset with its original evidence and classification.

10. Variant and authorship controls

Challenge Specification 0.1 requires challenge variants to be checked for equivalent difficulty before comparative use.

The method remains open.

Until a documented equivalence assessment exists:

Variant identity must remain attached to every score.

Variant equivalence must not be assumed.

Results may be reported within the same variant.

Cross-variant comparisons must be labelled provisional or withheld where difficulty differences could materially affect interpretation.

Challenge authorship and independence status must also remain visible.

Any unresolved authorship or independence concern is reported with the affected challenge results.

The rubric does not invent an authorship allocation method or difficulty-equivalence procedure.

11. Aggregation and capability profiles

The pilot produces one score per attempt for each applicable category.

Results are summarized by:

Model configuration.

Exact model version.

Challenge group.

Challenge identity.

Variant.

Replicate.

Category and scoring dimension.

For each category, report:

Mean score.

Median score.

Minimum and maximum.

Replicate-level results.

Challenge-level results.

Applicable dimension breakdown.

Unscorable and infrastructure-failure counts.

The three replicates remain visible. Aggregation must never conceal inconsistent performance.

A category-level average does not replace the underlying attempt records.

No overall winner, league table or universal model ranking is produced.

The intended output is a capability profile describing strengths, weaknesses, consistency and uncertainty for each tested configuration.

12. Interpretation limits

The pilot contains six challenges per category.

Results therefore describe observed performance on the frozen pilot challenge set. They do not establish universal model capability.

In particular:

Results must not be generalized to untested model versions.

Provider and endpoint differences remain part of the tested configuration.

Three replicates do not establish broad statistical reliability.

Variant equivalence must be established before strong cross-variant conclusions.

Challenge authorship and possible contamination must remain visible.

A score is not evidence of capability beyond the criteria and evidence that produced it.

13. Acceptance tests for the rubric

Before pilot execution, the rubric must demonstrate:

A challenge with a completely correct rule discovery receives the appropriate maximum A score.

A plausible but incorrect rule cannot receive a strong correctness score.

Correct discovery with unsupported evidence is distinguishable from evidence-backed discovery.

F1 scoring distinguishes missed seeded defects from false positives.

Correct identification with an invalid repair cannot receive full F1 credit.

F1 preservation detects unnecessary damage to valid content.

F2 distinguishes error detection from successful repair.

F2 preservation detects regression in previously correct work.

A model that receives an external correction cannot receive genuine self-correction credit.

A valid initial answer is not penalized for failing to invent errors.

Infrastructure failures remain distinct from model capability scores.

Every score can be reconstructed from the raw result, challenge key and adjudication evidence.

Replicate-level results remain available after aggregation.

Variant and authorship uncertainty remains visible in the resulting profile.

No aggregate result is presented as a universal model ranking.

14. Scope boundary

This document defines scoring and adjudication for the initial A+F pilot.

It does not:

Add categories B, C, D or E to the initial pilot.

Modify the Challenge Specification.

Modify the Raw-Result Schema.

Authorize model calls or pilot execution.

Authorize changes to Duenna or its Stage 6 process.

Establish universal model rankings.

Introduce creative-writing evaluation.

Treat reported results as independently verified results.

Document 2 of 3 — submitted for independent review.

The three-document design set is now complete in draft form: Challenge Specification 0.1, Raw-Result Schema 0.1 with accepted amendments pending Schema 0.2, and A+F Pilot Rubric 0.1.

No pilot execution is authorized by this submission.

One deliberate boundary in this draft: F2 cannot measure self-correction meaningfully unless each challenge has a predetermined way to distinguish genuine defects in the initial output from valid work. The rubric makes that answer-key requirement explicit rather than treating every revision as evidence of improvement.

Submitted for Remmy's review. No pilot execution or provider calls are authorized.
