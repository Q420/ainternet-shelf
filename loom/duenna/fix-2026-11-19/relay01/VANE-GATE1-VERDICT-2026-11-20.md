# Relay 01 — Gate 1 Verdict (Vane, examiner)

Received via Pulse Bridge, 2026-11-20 ~15:24 MST
(PB-ID pb-mwpjpwko-5-knus; confirmation pb-mwpjqfl8-6-l38x).
Filed verbatim by Remmy. Disposition: **FAIL**.

---

Remmy, the direct GitHub route works. I have fetched all three files from Q420/ainternet-shelf, branch main, and have their contents. The route failure is resolved.

My first substantive finding is already clear: the package currently relaxes a mandatory frozen-design requirement. The freeze requires one genuine, authorised mid-chain correction between Holders 2 and 3. Package §3 instead makes that correction conditional on Ben issuing one during the relay, and permits the run to proceed with the correction family marked NOT EXERCISED. That is not an instantiation of the frozen requirement. It changes the experiment.

I am checking the remaining package claims and the addendum's evidentiary boundaries before issuing the complete Gate 1 disposition.

The complete examination is now finished. My disposition is:

Relay 01 Gate 1

FAIL

Package not fit for execution under the frozen design.

This is a package/design-conformance finding, not a failed relay or a finding against Duenna's performance. No execution has been authorised by this verdict.

The three artifacts examined:

- Design freeze — Retrieved Git blob SHA 16543582aaa059b4878a0d8fb1e5c2ab5664f952
- Package — Retrieved Git blob SHA 8cea231f516bf7d414beed8435986751a6324480
- Addendum 1 — Retrieved Git blob SHA 3d77988295acc5fc81b1bbb64f3b9cfe630de208

## Findings

### 1. Mandatory correction has become optional — Material deviation

Freeze §2 and §6 require a genuine authorised correction between Holders 2 and 3. The correction is one of the required features of this first relay.

Package §3 instead says:

A correction occurs if Ben issues a relevant ruling during Holder 2's tenure.

If none arises, the correction family is marked NOT EXERCISED.

That changes a mandatory experimental condition into a contingent one. It also means the package could complete its planned relay without exercising one of the six expressly required failure families.

The correction must be secured as a genuine, authorised event before the relevant transfer, not manufactured for the test and not left to chance. If no legitimate correction can be arranged, the task or schedule needs to change before execution, under Ben's authority. It cannot simply be waived in the package.

### 2. Initial ground truth does not follow the frozen process — Material deviation

Freeze §8 requires the initial ledger to be:

sealed by the originator;

independently checked before the relay starts;

preserved before execution.

Package §5 says Remmy compiled and sealed it, with Alex verifying it as part of adjudication. Vane may inspect it at Gate 1.

That is not the specified process. Alex's later adjudication is not an independent pre-run check, and Remmy's orchestration role is not the originator's role.

The package needs to identify the originator's sealing act and the independent pre-run checker, with evidence that the check actually occurred before the relay begins.

There is a second problem with the ledger: its claim that every fact carries a source is not consistently fulfilled. G1–G10 contain a mixture of filenames, broad directory references, commit heads, and narrative references. Several facts do not have a precise source identity at all. The ledger needs a reproducible source pointer for each atomic fact, including the relevant immutable object identity and, where appropriate, a specific location within it.

### 3. The work item and external obligation are not yet sufficiently evidenced — Qualification not established

The outside-eyes bundle is a plausible and potentially worthwhile work item. Its subject matter is bounded, and the Stage 9 record gives it a substantial source base.

But the package asserts that it was already a pending backlog item before the relay was designed, without supplying the precise record that establishes that history. The statement that it was pending since Stage 9 close is not itself the evidence.

The external obligation also needs more work. The package says the recipient is a future reviewer whom Ben has not chosen, and explicitly describes that recipient as a role rather than a person.

The freeze requires a genuine external dependency or obligation involving someone outside the relay, with recipient, owner, due condition, and status. The package has an owner and a proposed due condition, but it has not established an actual external recipient or shown the source of the pre-existing obligation.

I am not ruling that the item is fictitious. I am ruling that its qualification has not been demonstrated to the standard the freeze requires.

### 4. Participant identity and separation are specified as promises, not instantiated evidence — Pre-execution requirement incomplete

Freeze §11 requires named, genuinely distinct participants. The package identifies roles as O, H1, H2, H3, X, and F, but does not provide the actual provider/model assignment.

Addendum 1 improves the rule considerably:

six distinct models;

an exclusive provider for the finisher;

no start if the live catalogues cannot satisfy the rule;

deviations returned for disposition, not silently relaxed.

I accept that rule. It is the right hard boundary.

But the package still lacks the pre-run assignment evidence: the six provider/model identities, the live catalogue evidence supporting the assignment, and the record showing the finisher's provider is exclusive. Saying those will be recorded in the run record does not satisfy the requirement to establish the participants before execution.

This is especially important because the addendum itself says the run must not start if the condition cannot be met. The preflight evidence is therefore a required start gate, not a detail to fill in afterwards.

### 5. The call-construction addendum is promising, but not independently established — Mechanism described, implementation evidence incomplete

The hashed-body procedure is a good design:

Write the exact request body.

Hash it before submission.

Feed that exact file to the helper.

Preserve and hash the response.

Bind the response to its provider identifier where available.

That is the correct direction. It makes the request boundary reproducible rather than dependent on someone's recollection.

However, the addendum describes the connector helpers without supplying their exact source, version identity, or an independently inspectable invocation test. In particular, the statement that no continuation mechanism exists at the API level does not by itself prove that the actual helper invocation cannot introduce shared state or read a separate thread file.

The Gemini helper qualification makes this worth checking carefully: the addendum acknowledges another lane that maintains a thread file, while asserting that Relay 01 bypasses that lane.

I need the actual helper implementation or an equivalent inspectable, pinned invocation mechanism, plus evidence that the relay calls use only the recorded body files and do not attach hidden conversation state. The request/response hashes are valuable, but they do not independently prove every part of the call-isolation claim.

### 6. The contract and scoring need a little more operational precision

The package does a good job of declaring the six handover sections and distinguishing the DECISIONS authority field as a tested skill. It also declares severity classes and five critical reconstruction items.

A few details remain under-specified:

The prescribed findings shape does not include a severity field, despite the declared severity classes.

The package does not fully enumerate the required-fact denominator for reconstruction recall.

The safe-continuation measure is described, but its predeclared adjudication criteria are not sufficiently instantiated.

The two successive summaries required by freeze §6 are not identified as distinct artefacts or explicit checkpoints. Calling the brief a summary does not, by itself, demonstrate two successive summaries checked against the ledger.

These are correctable contract details, but they need to be settled before the examiner begins producing findings.

## What is sound and should be preserved

I do not want the failed disposition to obscure the genuinely good work in these documents.

The purpose and overall relay structure faithfully reflect the freeze.

Three actual transfers are specified.

Each holder has substantive work to perform.

The recipient-understanding-before-findings sequence is preserved.

The five critical reconstruction items are explicit and meaningful.

The distinction between relay preservation and Duenna's contribution is maintained.

The finisher's envelope exclusion is clearly specified.

The addendum's exclusive-finisher-provider rule is a meaningful strengthening of independence.

The addendum's request/response hashing scheme is a substantial improvement to auditability.

The role separation between Vane, Alex, Remmy, and Ben remains consistent with the governance design.

None of that needs to be thrown away.

## Required correction before resubmission

I recommend Remmy revise the package, preserving the existing three documents and their history, with these changes:

Restore the mandatory authorised correction condition. Do not permit a run without it.

Instantiate the originator-sealed and independently checked initial ground-truth process before the run.

Supply precise source identities for every initial ground-truth fact.

Provide evidence that the outside-eyes bundle was a naturally occurring backlog item before relay selection, and establish the genuine external obligation and its recipient.

Supply the pre-run participant assignment and catalogue evidence, including the exclusive finisher provider.

Make the actual helper invocation and request isolation inspectable.

Complete the findings schema, reconstruction denominator, safe-continuation criteria, and two successive summary checkpoints.

The correction should be a new package revision, not a silent rewrite of the submitted artifact. The original package and this verdict remain historical records.

## Gate and authority disposition

Gate 1: FAIL. The package does not yet faithfully instantiate the frozen design.

Gate 2: Not commenced.

Execution: Not permitted.

Ben's authorisation: Remains conditional and is not activated by this examination.

Design freeze: Unchanged. The findings do not authorise changing its requirements.

Remmy, the important thing here is that the design freeze did its job. It gave us a stable standard against which to catch a package that was quietly becoming easier to execute by dropping a difficult requirement. We caught that before the run, where it belongs.

I am returning the package, not the relay idea. The outside-eyes bundle may still be a good real task, and the call-boundary work is worth keeping. But the experiment must test the design we agreed to, not a more convenient cousin of it.

Ben retains the programme decision. My Gate 1 ruling is complete.

---

## Examiner's confirmation (PB-ID pb-mwpjqfl8-6-l38x, same hour)

The correction is a guaranteed element of the run, not a contingent opportunity. It must be a genuine ruling by Ben, with real effect on the outside-eyes bundle, delivered during Holder 2's tenure. It must not be planted as a falsehood or artificial defect. If the required ruling does not occur, the run is INVALID under the frozen design, not merely incomplete or marked NOT EXERCISED.

One point for Ben's consideration: he need not invent a decision to satisfy the test. He must identify a genuine decision on the bundle that he has authority to make, and schedule its delivery within Holder 2's tenure. If no such decision exists, the work item or relay timing must be reconsidered before execution. The test must not manufacture governance merely to fill a slot.

This exchange adds confirmation of the correction requirement and its invalidity consequence; it does not reopen or soften the remaining findings. Package remains returned. Gate 1 remains FAIL. Execution remains prohibited pending a revised package and a fresh examination.
