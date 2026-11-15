# T03 Remediation Proposal 0.1 — Alex

Source: Alex (ChatGPT desk), reply to RB-2026-11-15-34, conversation 6af966fb-2150-83e8-9985-4e82978b592c, captured 2026-11-15T01:06:34-0700 via the Remmy Browser watcher (settle-gate). Filed verbatim by Remmy; the proposal is paper only and authorises nothing. Ben's ruling is the outstanding step.

---

The key finding is that T03 has two separate provenance problems, not simply a missing extraction rule:

The three adjudication dispositions exist in the pinned adjudication record, but the extractor has no rules for reading those prose bullets.

Correction B's status is not in the T03 pack at all; it exists in a different record.

That matters because adding extractor rules alone would not make the complete T03 question answerable. I'll check the frozen criteria, tree, rules and source records before choosing the remediation.

My recommendation is route (c): repair the T03 evidence pack and extraction coverage together, while preserving the original question.

I would not re-scope STEP-03 merely to make the calibration pass. That risks turning a meaningful cross-record adjudication question into an easier but less useful test.

Writing
T03 Remediation Proposal 0.1

Batch 6 — Gate G5 — For Ben's ruling

Status: Proposed remediation. Paper only.
Authority: Ben retains approval authority.
Current state: T03 remains UNANSWERABLE and excluded from any Stage 6 battery.

1. Finding

The T03 calibration failure has two distinct causes:

The pinned adjudication record alex-combined-adjudication-v010#002 contains the R47, R60 and R65 dispositions as prose bullets, but EXTRACTOR-RULES-02 contains no rule capable of extracting those values.

Correction B's status is obtainable from alex-combined-adjudication-r60rev#001, but that record is not included in the T03 data pack.

Consequently, the complete STEP-03 question cannot be answered using the pinned inputs and extraction rules.

This is a genuine answerability failure, not a model failure.

2. Recommended remediation

Preserve T03's intended question and repair its deterministic evidence substrate.

A. Repair the T03 data pack

Add the canonical adjudication record containing Correction B's status to the T03 pack, provided its identity, provenance and integrity can be verified against the authoritative source.

The existing v0.10 adjudication record remains in the pack.

Both records must be explicitly identified in the revised pack definition. No implicit access to material outside the pack is permitted.

B. Amend EXTRACTOR-RULES-02

Add explicit, deterministic extraction rules for:

R47 disposition.

R60 disposition.

R65 disposition.

Correction B status.

Each rule must identify its intended source section, matching pattern, value interpretation and type expectations.

The three adjudication dispositions must preserve their qualified meanings:

R47: PASS (narrow).

R60: FAIL.

R65: PASS (qualified).

Correction B must be extracted from its own canonical source record, not inferred from the v0.10 prose or reconstructed from an unrelated result.

C. Preserve the question

Do not alter T03-STEP-03's intended subject or expected outcome merely to accommodate the existing extraction limitations.

If the original tree wording requires a corresponding reference update to identify the newly pinned input, make only that necessary reference change. Do not otherwise simplify the challenge.

3. Freeze and recalibration protocol

This remediation changes both pilot data and extractor rules. It therefore requires the re-freeze and recalibration protocol in Criteria 0.4 §5.3.

The sequence is:

Verify the authoritative Correction B source and its provenance.

Amend the T03 pack definition to include the required source record.

Amend EXTRACTOR-RULES-02 with the four explicit extraction rules.

Update the relevant manifest and pin records.

Re-freeze the amended data and rules through the prescribed amendment process.

Re-run the complete offline calibration against the resulting pinned snapshot and pilot data.

Verify every required extraction's match count, type and evidence location.

Confirm the complete STEP-03 expected outcome is derivable from the pinned inputs.

Issue a new calibration certificate preserving the previous certificate and its finding.

The recalibration must not use model calls to fill missing values or resolve extraction ambiguity.

4. Acceptance conditions

T03 may be reconsidered for Stage 6 only when:

All required pack sections resolve against the pinned snapshot.

All four required extraction fields have explicit pinned rules.

Each required extraction produces the intended value through the prescribed deterministic mechanism.

Each extraction has the expected match outcome and supporting evidence.

Correction B's status is independently traceable to its pinned source.

The complete STEP-03 expected outcome is reproducible from the frozen inputs.

T03 is certified ANSWERABLE in the new calibration certificate.

A partial repair is insufficient. If any required value remains unavailable, ambiguous, or type-invalid, T03 remains UNANSWERABLE.

5. Alternatives considered

Route (a): Rules amendment alone

Insufficient. It could resolve the three prose-disposition extractions, but cannot recover Correction B from a source that is absent from the T03 pack.

Route (b): Re-scope STEP-03

Not recommended. It would change what T03 measures to accommodate an incomplete evidence substrate. That sacrifices the original challenge rather than repairing its inputs.

Route (c): Repair both pack membership and extraction coverage

Recommended. It preserves the original question, makes every required source explicit, and restores answerability through the existing deterministic calibration process.

6. Authority and scope

This proposal authorizes no implementation, re-freeze, recalibration or Stage 6 execution.

T03 remains excluded until the remediation is completed, the new calibration establishes ANSWERABLE, and Ben makes the necessary ruling.

No other tree or pilot scope is changed by this proposal.

Why I favour this route: it preserves the integrity of the experiment. We shouldn't change what T03 is measuring just because its evidence preparation was incomplete.

One sequencing point: I'd handle this remediation paper now, while keeping Schema 0.2 as a separate outstanding deliverable. Neither needs to be silently folded into the other's scope.

The proposal is ready for Remmy's technical review and your ruling. I have not changed the Shelf or any frozen artefact.
