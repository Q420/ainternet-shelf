# ALEX — INDEPENDENT MODEL CAPABILITY TRIALS: CHALLENGE SPECIFICATION 0.1 (2026-11-14)

Document 1 of 3, delivered with the Batch 5 reinspection reply (RB-2026-11-14-03). Draft 0.1 for Remmy's review; paper-first; no pilot execution authorised. Documents 2 (A+F Pilot Rubric 0.1) and 3 (Raw-Result JSON Schema 0.1) to follow.

---

Independent capability trials — document 1 of 3I've retrieved the earlier design decisions. I'll deliver the three documents separately, starting with the challenge specification.

Writing
Independent Model Capability Trials
Challenge Specification 0.1

Status: Proposed — Draft 0.1
Programme: Independent model capability evaluation
Relationship to Duenna: Completely independent
Execution status: Not authorised; paper-first design

1. Purpose

Establish a reproducible method for evaluating the actual reasoning capabilities of different language models.

The objective is to measure what a model can independently discover, reason through, verify and correct.

This is not a creative-writing competition, a benchmark of conversational personality, or a test of how well a model follows another model's conclusions.

The evaluation must distinguish model capability from provider, execution, checker and harness reliability.

2. Evaluation principles

Independent attempts: no model receives another model's answers.

Standardized presentation: equivalent challenges and instructions across configurations.

No hints or corrective feedback during an attempt.

Preserve complete raw inputs and outputs.

Predetermine answers, scoring criteria and expected evidence.

Separate model failures from infrastructure and evaluation failures.

Use fresh sessions for independent replicates.

Preserve unsuccessful attempts.

Keep challenge authorship and answer keys separate from evaluation.

No Duenna-specific framing or Duenna execution dependencies.

3. Capability categories

The complete evaluation framework contains six categories.

A — Novel rule discovery

Present a collection of examples governed by an undisclosed rule.

Measure:

Correct identification of the underlying rule.

Discovery of relevant constraints.

Recognition of alternative explanations.

Supporting evidence.

Application to previously unseen examples.

Appropriate uncertainty where evidence is insufficient.

B — Abstract reasoning and transfer

Present unfamiliar problems requiring an abstract relationship to be identified and transferred into a different context.

Measure:

Identification of the underlying structure.

Correct abstraction.

Transfer to unfamiliar cases.

Recognition of limits to the analogy.

Resistance to misleading surface similarities.

C — Technical problem solving

Present bounded technical problems with explicit requirements and testable outcomes.

Measure:

Correct diagnosis.

Selection of an appropriate solution.

Technical validity.

Constraint preservation.

Recognition of unresolved problems.

D — Evidence and contradiction analysis

Present evidence containing conflicting statements, incomplete records or competing explanations.

Measure:

Evidence extraction.

Identification of contradictions.

Source reliability assessment.

Separation of established facts from assumptions.

Appropriate conclusions and uncertainty.

E — Systems reasoning

Present systems with interacting components, dependencies, constraints and failure conditions.

Measure:

Understanding of component relationships.

Identification of dependencies.

Prediction of downstream effects.

Recognition of feedback and failure propagation.

Preservation of system-wide constraints.

F — Error detection and self-correction

Two distinct subcategories:

F1. Artefact audit:

Supply a deliberately constructed artefact containing seeded errors.

Require independent inspection.

Identify actual defects.

Distinguish defects from valid elements.

Explain supporting evidence.

Propose valid corrections.

F2. Own-work audit:

Require the model to complete an initial task.

Preserve its original output.

Subsequently request an independent audit of its own work.

Do not reveal the planted errors or supply corrective answers.

Measure detection, correction and preservation of correct work.

F2 must distinguish genuine self-correction from simply following an externally supplied correction.

4. Initial pilot scope

The initial pilot concentrates on:

A — Novel rule discovery.

F1 — Artefact audit.

F2 — Own-work audit and self-correction.

The remaining categories are retained in the full framework but are not part of this initial pilot.

5. Model configurations

Initial comparison set:

Qwen

Nemotron

GPT-OSS-120B

GPT-OSS-20B

Each configuration must be identified by its actual model, provider, endpoint and execution settings.

A model name alone is insufficient identification.

The evaluation unit is:

Model + provider + endpoint + task family + execution mode + checker + harness + version.

Results must not be generalized beyond the configuration actually tested.

6. Pilot challenge structure

The pilot uses six distinct challenge items in each of the three groups:

A: six rule-discovery challenges.

F1: six artefact-audit challenges.

F2: six own-work audit challenges.

Each challenge is attempted three times by each of four model configurations.

Total:

3 groups × 6 challenges × 3 replicates × 4 configurations = 216 attempts.

Replicates must use fresh independent sessions.

No feedback from one replicate may influence another.

7. Standardized controls

Every challenge must have:

A frozen challenge identifier and version.

A predetermined task prompt.

A predetermined expected answer or evaluation key.

Explicit acceptance criteria.

Known traps and seeded errors where applicable.

A scoring rubric established before execution.

A defined checker version.

A defined execution timeout.

A standardized output-capture procedure.

Challenge variants must be checked for equivalent difficulty before being used in comparisons.

8. Execution restrictions

During the initial pilot:

No external research or browsing.

No access to another model's response.

No hidden assistance from an examiner.

No corrective hints.

No mid-attempt prompt alterations.

No undisclosed tools.

Any permitted tools or execution differences must be recorded.

9. Failure classification

Failures must be classified separately:

Classification	Meaning
MODEL_REASONING	Incorrect reasoning or conclusion
MODEL_INSTRUCTION	Failure to follow the task contract
MODEL_FORMAT	Invalid or incomplete required output
PROVIDER_TRANSPORT	Provider or transport failure
TIMEOUT_TRUNCATION	Execution timeout or incomplete response
CHECKER	Incorrect or unreliable evaluation
HARNESS	Execution or orchestration defect
GROUNDING	Unsupported or fabricated evidence
UNRESOLVED	Insufficient information to classify

Infrastructure failures must not automatically count as reasoning failures.

Equally, a successful API response must not automatically count as a successful reasoning attempt.

10. Measurements

The common scoring dimensions are:

Correctness.

Discovery.

Transfer.

Evidence.

Calibration.

Completion.

F-specific measurements additionally include:

Seeded-error recall.

False-positive rate.

Repair correctness.

Preservation of correct work.

Improvement between initial and revised work.

Detailed scoring definitions belong in the separate A+F Pilot Rubric.

11. Raw evidence

Every attempt must preserve:

Original challenge.

Exact submitted prompt.

Complete raw model response.

Model and provider identification.

Execution configuration.

Timing and token information where available.

Checker result.

Scoring breakdown.

Failure classification.

Any subsequent review or adjudication.

Raw results must remain immutable.

Corrections and adjudications must be recorded as additional records, not silent replacements.

12. Scope exclusions

This programme does not:

Modify Duenna.

Authorize Stage 6.

Authorize a live provider call under the Duenna pilot.

Establish that one model is universally superior.

Measure creative-writing quality.

Treat reported capability as independently verified capability.

13. Acceptance of the specification

Draft 0.1 is ready for independent review.

Approval of the specification, rubric and schema must precede pilot execution.

No pilot execution is authorized by this document.

Next: A+F Pilot Rubric 0.1, including the scoring scales, F2 self-correction distinction and adjudication rules.

The capability programme remains separate from the Batch 5 clearance process.

You're using the free version of ChatGPT. Upgrade for advanced models, better memory, and higher-quality image creation.
Try Plus free
