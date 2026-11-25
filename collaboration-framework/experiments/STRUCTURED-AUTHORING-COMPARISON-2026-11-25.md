# Structured Authoring Comparison — Experiment Package
**Date:** 2026-11-25  
**Status:** Proposed for independent examination; not authorized to launch  
**Purpose:** Test whether structured assignment authoring improves agent completion and reduces ambiguity/token use, using the existing collaboration framework and no new middleware.

## 1. Decision sought

Examine and, if sound, return this package for the director's explicit ruling on whether to conduct a controlled two-run comparison.

This package does **not** authorize execution, change the framework, create a new service, or establish a new project named EXON. The existing EXON specification project retains its identity and scope.

## 2. Question and falsifiable hypothesis

**Question:** Given the same assignment and operating conditions, does a structured authoring of the assignment enable an agent to complete the work at least as reliably as the existing case authoring, while reducing ambiguity and/or input-token consumption?

**Hypothesis:** Structured authoring will produce equal-or-better task completion and scope adherence, with fewer unresolved ambiguities and/or fewer input tokens.

A shorter prompt alone is not success. If the structured version causes a missed requirement, unauthorized interpretation, weaker evidence, or failed completion, the hypothesis is not supported.

## 3. Experiment boundary

Use the existing framework as it stands. Do not build or modify a compression gateway, EXON/SIEVE middleware, prompt optimizer, or other infrastructure for this experiment.

The treatment under test is **authoring style only**:
- Control: the selected real case's existing assignment text, preserved verbatim.
- Treatment: a structured rewrite of that same assignment, derived from the control without adding, removing, weakening, or strengthening any requirement or authority.

The experiment tests structured authoring, not semantic extraction software, automated compression, a new validator, or a new architecture.

## 4. Select and freeze the assignment

Before either run:
1. Select one real, bounded assignment already represented in the framework.
2. Record its exact case identity, source path, source revision/commit, and content hash.
3. Preserve the complete existing assignment text as the control.
4. Have the originator identify the assignment's operative requirements, scope, authority, constraints, evidence expectations, deliverables, and completion condition. This is the comparison ground truth, not a post-run interpretation.
5. Produce the structured treatment from the same source.
6. Map every treatment statement to its source statement or originator-confirmed requirement. Mark any item that cannot be mapped.
7. Do not proceed to runs if the treatment introduces a new restriction, authorization, requirement, assumption, or completion condition; omits an operative requirement; or resolves an ambiguity by guessing. Return it for clarification or correction first.

The freeze records both prompt variants and the mapping before execution. Neither variant may be edited after a run begins.

## 5. Controlled conditions

The two runs must use:
- The same selected assignment and underlying evidence.
- The same agent/model and pinned model identifier.
- The same provider, route, mode, tools, permissions, and framework version.
- The same task budget, step limits, timeout policy, and other execution settings.
- The same starting state and access to authoritative records.
- The same acceptance criteria and scoring rubric.

Only assignment authoring style may differ.

Record unavoidable environmental differences. If a difference could materially affect the result, classify the comparison as confounded rather than attributing the outcome to authoring style.

Run order should be selected and recorded before execution. Preserve both complete run records, including failures and partial work. Do not silently rerun or replace an unfavorable result.

## 6. Evaluation criteria

Score each run independently against criteria frozen before execution:

1. **Completion:** Was the assigned deliverable completed and filed in the required form?
2. **Correctness:** Does the deliverable satisfy the assignment's acceptance criteria?
3. **Requirement coverage:** Is every operative requirement addressed?
4. **Scope and authority:** Did the agent remain within its authorization and avoid unauthorized changes?
5. **Evidence quality:** Are claims supported by the required authoritative evidence and references?
6. **Ambiguity handling:** Did the agent identify missing or ambiguous information and seek clarification rather than guess?
7. **Token consumption:** Record actual input and output tokens where available, distinguishing prompt tokens from framework/tool/context carriage.
8. **Execution reliability:** Record timeouts, provider refusals, tool failures, stalls, retries, and other incomplete execution.

A run that does not complete is recorded as incomplete; its partial work may be evaluated, but must not be scored as a completed assignment.

## 7. Independent evaluation and anti-self-certification

The author of the structured treatment must not certify its own equivalence or score its own result.

Before execution, the originator confirms the ground-truth requirements and the mapping. After execution, an independent examiner evaluates both outputs against that frozen ground truth and the same rubric.

The examiner must be able to identify:
- Any source requirement absent from the treatment.
- Any treatment statement not grounded in the source or originator-confirmed ground truth.
- Any change in scope, authority, or completion conditions.
- Any ambiguity silently resolved by either authoring.
- Any difference in execution conditions that weakens the comparison.

A receipt or checklist may report observations, hashes, and measurements. It must not assert semantic equivalence merely because the transformation process says it passed.

## 8. Decision rule

- **Structured authoring supported:** Treatment completes with correctness, requirement coverage, scope adherence, and evidence quality no worse than control, while showing a meaningful improvement in at least one target (ambiguity handling or token consumption), with no material confound.
- **No demonstrated benefit:** Results are equivalent without a meaningful improvement, or the treatment does not complete.
- **Structured authoring harmful:** Treatment misses requirements, changes authority/scope, weakens evidence, guesses at ambiguity, or performs materially worse.
- **Inconclusive:** A provider/environment failure or material confound prevents a fair comparison. Preserve the result and seek a separate ruling before any further run.

One pair of runs is an initial empirical probe, not statistical proof. Any broader claim requires repeated trials across representative assignments.

## 9. Consequences

If supported, the next proposal is to adopt structured assignment authoring within the existing office workflow, subject to the director's ruling. It does not automatically authorize middleware construction.

If not supported, do not build the proposed middleware on the strength of this idea. Record what failed and decide whether a narrower question merits testing.

If token savings remain insufficient after structured authoring, a separate compression-layer proposal may be considered later, with its own evidence and authorization.

## 10. Non-goals and exclusions

This experiment does not:
- Build or authorize EXON/SIEVE or any other middleware.
- Rename, redefine, or absorb the existing EXON specification project.
- Automatically compress conversation history or authoritative records.
- Replace the framework's existing authority, evidence, provenance, or verification mechanisms.
- Permit a transformation process to invent requirements or authorization.
- Treat token reduction as success independent of task completion.
- Treat a single successful pair as general proof.

## 11. Required package records

Before launch, the package should contain:
- Frozen control assignment and source identity/hash.
- Frozen structured treatment and source identity/hash.
- Requirement/statement mapping with originator confirmation.
- Recorded run configuration and execution order.
- Frozen scoring rubric and decision rule.
- Explicit director authorization to launch.

After launch, preserve:
- Both complete run records and all provider/tool failure evidence.
- Token measurements and their measurement source.
- Independent evaluation with evidence references.
- Confound assessment and final comparison.
- Director's decision as a separate record.

## 12. Current disposition

**Awaiting independent examination and director ruling. No run is authorized by this document.**

The governing test is whether the agent completes the same assignment at least as reliably, not whether the prompt merely becomes shorter.
