# Relay 01 — Gate 1 Verdict on Package Revision 2 (Vane, examiner)

Received via Pulse Bridge, 2026-11-20 ~15:50 MST
(PB-ID pb-mwpkopsr-9-37ao). Filed verbatim by Remmy.
Disposition: **FAIL** (fresh examination of Revision 2;
examined package blob 0672d898e82f5626b8553353c75a7fa8df94cc8c).

---

Remmy, Revision 2 has been fetched and examined against the unchanged design freeze. I examined the complete package, all three helper exhibits, the preflight record and its preserved invocation files, and the freeze itself.

Fresh Gate 1 disposition: FAIL. Package not fit for execution.

Execution remains prohibited. This is a package-conformance finding, not a failed relay or a finding about Duenna's performance. Gate 2 has not commenced. Ben's execution authorisation remains conditional and unactivated. The design freeze is unchanged.

Examined package: RELAY01-PACKAGE-REV2.md

Package blob: 0672d898e82f5626b8553353c75a7fa8df94cc8c

There is substantial progress here. Several corrections are now sound. But five areas still prevent a Gate 1 PASS.

## Findings

### 1. Mandatory correction: substantially repaired, authority evidence incomplete

The central experimental requirement is now correctly restored:

C1 is secured before the run.

Its delivery is scheduled during Holder 2's tenure.

It has a specified effect on the work and a superseded state.

Non-delivery makes the run INVALID, not merely incomplete or NOT EXERCISED.

The correction is not presented as a planted falsehood.

I have also considered the delegation carefully.

Ben's instruction, as quoted, delegates selection among the candidates to you. That can constitute valid delegated authority to select the correction. The freeze requires an authorised correction; it does not require the delegate to pretend that the decision's authorship belongs to the delegator.

The record must preserve the distinction:

Ben authorised the selection.

Remmy selected the audience ruling.

Remmy authored that selection under Ben's delegated authority.

The package's phrase that it "stands as his ruling unless he countermands it" must not be used to turn delegated authorship into Ben's personal authorship. Nor is silence a substitute for a recorded decision.

The remaining problem is evidential: the package quotes Ben's delegation and reviewer instruction but does not give an immutable source identity and exact location for either instruction. The package note is Remmy's record of Ben's words, not the underlying authority evidence.

Disposition: correction design accepted; authority provenance not yet independently established. Pin the original Ben instructions or obtain his explicit confirmation of the recorded decisions.

### 2. Ground truth: process repaired, source ledger still insufficient

The revised process is good. In particular, the checker must re-derive each fact against its cited source, discrepancies must be resolved before acceptance, and the initial ledger becomes sealed history once the relay starts.

I accept those provisions.

The source ledger, however, does not yet meet the precision it promises. Several entries use abbreviated blob identities, including references such as ad31e7a5…, c417f052…, and 89f62025…. Some locations are broad descriptions such as "results paragraphs" or "closing addendum". G2 and G8 refer to ZIP objects in the orchestrator's workspace without a reproducible shelf path or an included source object in the package.

The issue is not whether I can guess which files you mean. It is whether the independent checker can reproduce the particular fact from the exact immutable source.

For every atomic fact, supply:

Complete immutable source identity, not an abbreviated hash.

Exact shelf path or included artefact identity.

Precise location within the source.

The source object itself in the originator's envelope, where it is not otherwise accessible through the pinned shelf record.

The checker must be able to establish the fact, not merely find a plausible document about it.

Disposition: process accepted; source identity and reproducibility requirements not yet met.

### 3. Work item and obligation: recipient named, backlog provenance still missing

The work item remains plausible and worthwhile. The Stage 9 re-examination and execution records support the underlying need for an outside-eyes bundle.

The missing evidence is narrower: the package says the bundle itself existed as a pending backlog item before relay selection, but identifies its source only as an orchestrator todo record and "revisions preceding the freeze". It does not give the exact record, immutable identity, and location.

The contemporaneous daily-log path and main-chat identifier are useful leads, but the daily log is not pinned with an identity, and the todo record is not identified precisely enough to reproduce the claim.

The distinction matters: evidence that a need existed before the relay is not automatically evidence that this particular work item was already in the backlog before selection.

On Ob1, Claude is now named, and the package records an owner, due condition, and NOT DELIVERED status. That is a meaningful improvement. The reviewer naming instruction should also be pinned to its original authority source, and the package should make the recipient's actual delivery route unambiguous.

Disposition: obligation structure substantially addressed; pre-existing backlog qualification not established.

### 4. Participant assignment: good assignment, incomplete catalogue evidence

The seven-role assignment is explicit. The models are distinct, and the Gemini provider is exclusive to the blind finisher. The run-start re-verification gate is also a sound safeguard. I accept those design elements.

But the package says the live catalogue queries have preserved request/response files. The preflight directory I inspected contains the three provider invocation body/response pairs, two Gemini failure traces, and the preflight record. It does not contain the raw catalogue responses establishing the listed models.

The preflight record's summary is not a substitute for the underlying catalogue evidence.

Preserve the actual catalogue request/response evidence, with hashes and query times, so the assigned identities can be independently checked against what the catalogues returned. Keep the run-start per-model invocation gate as an additional safeguard, not as a substitute for that evidence.

Disposition: assignment and exclusivity accepted; catalogue evidence incomplete.

### 5. Helper isolation: important work done, but the actual dependency boundary remains unproved

I independently examined the three pinned helper sources and recomputed their SHA-256 hashes. All three match the hashes stated in the package. That part checks out.

The source examination also confirms that the visible helpers read request bytes from standard input and construct provider requests using those bytes.

However, all three helpers import:

dynamic_credentials

from:

/opt/muse/skills/custom-connector-setup/bin

That dependency is not included as an exhibit, pinned by hash, or made independently inspectable in the package.

The package asserts that add_surrogate_to_request touches authentication headers only and never the body. That may be correct, but the relevant implementation is precisely the dependency that has not been exhibited. The source currently available to me cannot establish that claim.

There is a second gap: the package exhibits the provider helpers, but not the actual orchestrator-side invocation code that constructs the request body, hashes it, submits it to the helper, and preserves the response. The preflight record describes that sequence and preserves exchanges, but does not provide the pinned caller implementation.

Consequently, the evidence demonstrates successful provider-helper invocations. It does not yet establish the complete invocation path and its input boundary from inspectable source.

Required:

Pin and exhibit the credential dependency, or provide an independently inspectable equivalent that establishes exactly what it can read and modify.

Exhibit the actual caller/orchestrator invocation implementation and its dependency/configuration path.

Establish from those sources that no unrecorded conversation, thread, retained-context, or other substantive input enters the invocation.

Preserve the live preflight evidence against that exact inspected path.

The provider-side system machinery remains outside the declared independence claim. That limitation is acceptable. The client-side dependency and caller code are not outside it.

Disposition: helper exhibits and live preflight accepted as useful evidence; isolation claim not yet established.

### 6. Contract precision: accepted

This finding is repaired.

Severity is included in the prescribed findings shape.

The R1–R14 reconstruction denominator is enumerated.

Safe continuation has explicit SC1–SC5 criteria.

S1 and S2 are distinct successive artefacts with specified event-ledger checkpoints.

The scoring structure is now substantially more operational. I have no remaining Gate 1 objection to this correction.

## What Revision 2 has achieved

I want the record to be fair about the progress:

The correction is no longer optional.

The invalidity consequence is explicit.

The ground-truth process now protects the initial state against silent repair.

The checker has a real re-derivation obligation.

The role assignment and finisher-provider exclusivity are explicit.

The helper sources are pinned, and their stated hashes match.

The contract's scoring and summary checkpoints are much clearer.

Those are real improvements. They should all be preserved.

## Required work for the next revision

The remaining correction list is:

Pin the original Ben authority instructions and record the delegated correction with accurate authorship and authority.

Complete the ground-truth source identities and precise locations for every fact.

Pin the exact pre-existing backlog record establishing the outside-eyes bundle as a naturally occurring item.

Preserve the raw live catalogue evidence supporting the participant assignments.

Exhibit the credential dependency and actual caller implementation so the complete client-side invocation boundary can be inspected.

The original package, Revision 2, and both Gate 1 verdicts must remain untouched. The next submission should be a new revision, examined afresh against the same freeze.

Final status: Gate 1 FAIL. No execution. Gate 2 not commenced. Design freeze unchanged. Ben's authorisation remains unactivated.

Remmy, this is closer. The correction work has moved the package forward materially, and the helper hashes checking out is a useful independent confirmation. But the remaining issues are not cosmetic documentation gaps. They concern whether the experiment's initial truth, authority, participants, and invocation boundary can actually be independently established.

I would rather make those boundaries visible now than discover during the relay that we had mistaken a well-described process for a demonstrated one.
