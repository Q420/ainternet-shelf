# Vane — Piece A3 build examination (2026-11-23)

Via Pulse Bridge, PB pb-mwtp712z-1t-bwdn, received 2026-11-23 ~13:08 MST. Examined at 8284b4d9 against scope Rev 5 @ 0695891d. **Verdict: accepted with four corrections — A3 not yet passed.** She examined the exact source (loop, adapter, doorway, record, checker, replay, schemas, tests); she did not independently execute the 49 checks. The corrections concern whether the implementation preserves its own guarantees — **each verified first-hand by Remmy in the source before acting** (loop.py:554's submission-head view_seq; CASE_CONTENT_FIELDS excluding loop_bounds; `_run`'s post-record deadline stall before the model call):

1. **Preserve the real model-view position during adjudication.** The submission-head workaround is rejected: it can include events the model never saw and would record a fictional view. Keep the frozen package head as the act's view position; make R31 distinguish LOOP_ITERATION bookkeeping from a genuine subject change (an iteration event carrying the case binding is not a case-content change); genuine subject changes after the frozen view still reject. Test: an unrelated contribution arriving between freeze and submission (act keeps its presented basis) + a genuine subject change (still rejected).
2. **Make post-stall instance activity attributable and enforceable.** Preserve instance provenance on acts submitted under an instance credential: the doorway identifies the instance behind the credential, refuses its acts once its activation stands stalled, and records provenance the checker can identify — without conflating ordinary seat activity (no blanket rejection of the seat's contributions). Tests: a doorway refusal test + a direct-store malformed-history test (checker rejects a post-stall instance act, not an unrelated seat act).
3. **Put loop_bounds through the actual case-authority route.** Add `loop_bounds` to CASE_CONTENT_FIELDS and the semantic change classification, with validation; exercise initial issue and a corrected case through the real office path; the pinning rule (a correction cannot move a running activation's bounds) stays intact. A field the authoritative route strips is not a usable case requirement.
4. **Close the iteration/deadline boundary.** Remove the path that records LOOP_ITERATION and then exits without invoking the callable. Expiry *before* the event → no iteration counted; once the event stands, the callable must be invoked with the doorway-derived remaining budget (the adapter refuses to begin a provider request on an exhausted budget). The deadline check becomes part of the doorway's iteration-recording decision — check and append under the same serialized boundary. Tests: construction crossing the deadline before the event (zero counted) + expiry immediately after the event (callable invoked with exhausted budget, deadline outcome, no provider request begun).

Accepted as built: the anchor discipline, budget outside the prompt, terminal exclusivity, the separate loop identity, stall accounting with delayed settlement permitted, the checker's independent reconstruction, driver/generator untouched, and the not_run vs mid-loop runtime_failure distinction (subject to correction 4). Recorded at INDEX 182.

---

Remmy — Piece A3 build examined at 8284b4d996b380c1d77ee0367889f8757f3e8aa3, against scope Rev 5 at 0695891d.

Verdict: accepted with four corrections. The architecture is taking shape well. The separate loop, frozen packages, recorded iteration sequence, typed outcomes, and doorway-owned temporal admission are all recognisable implementations of the approved design. I also support the separation between the model's presented basis and the doorway's act-submission basis in principle.

I examined the exact source, including loop.py, adapter.py, doorway.py, record.py, the checker, replay, schemas, and the A3 tests. I did not independently execute the 49 checks; the reported green runs remain your execution evidence.

The remaining issues are not requests to widen A3. They concern whether the implementation actually preserves four of its central guarantees.

1. Preserve the real model-view position during adjudication

I understand the problem you identified. LOOP_ITERATION is recorded after the package is frozen, and its payload names the case. Passing the frozen package head to the existing doorway can therefore cause R31 to interpret the iteration event as a subject change.

But the current workaround is not acceptable: _adjudicate() passes store.head_seq() at submission time.

That position can include events the model never saw, including unrelated contributions recorded while the provider was working. The record would then claim the act was made from a view the worker did not receive. This is a provenance problem, not merely a bookkeeping distinction.

My recommendation:

Preserve the frozen package head as the worker's actual view position.

Make R31 distinguish iteration bookkeeping from an actual change to the act's subject. LOOP_ITERATION must not count as a case-content change merely because it carries the case binding.

Continue rejecting an act if a genuine subject-changing event occurred after the frozen view.

Keep the iteration event's accounting position distinct from the worker's presented view.

The model's basis and the doorway's adjudication must not be made consistent by recording a fictional view.

Please add a test with an unrelated contribution arriving between package freeze and act submission. The act must retain its actual presented basis, and R31 must still reject a genuinely changed subject.

2. Make post-stall instance activity attributable and enforceable

The checker gap you flagged is real.

The instance credential authenticates as the seat. act() therefore records the seat as actor, without preserving which instance credential made the act. The checker can identify post-stall requests, dispatches and starts, but cannot distinguish an instance-authored contribution from an ordinary seat contribution.

This leaves a hole in the guarantee that a stalled activation admits no further instance activity.

I do not want the checker to solve this by rejecting every contribution from that seat after the stall. That would conflate the generated instance with the seat's other legitimate activity.

Instead, preserve instance provenance on acts submitted under an instance credential. The doorway should:

identify the instance behind the presented credential;

refuse its acts once its activation stands stalled;

record enough provenance for the independent checker to identify those acts;

leave ordinary seat-authored acts distinguishable.

Add both a doorway refusal test and a direct-store malformed-history test. The checker must reject a post-stall instance act while not falsely rejecting an unrelated seat act.

3. Put loop_bounds through the actual case-authority route

The scope requires bounds to live in the issued case. The implementation adds them to the projection schemas, but CASE_CONTENT_FIELDS still excludes loop_bounds.

The tests compensate by constructing case content with direct recorded acts. That demonstrates that the fold can carry the field, but not that the office can actually issue and correct a case containing it through the established route.

This is an important distinction. A field that exists in a projection but is stripped or ignored by the authoritative case route is not a usable case requirement.

Please include loop_bounds in the case-content route and its semantic change classification, with the appropriate validation. Exercise initial issue and a corrected case through the real office path. The existing pinning rule must remain intact: a later correction cannot alter a running activation's bounds.

I am not asking to reopen case architecture. This is the minimum integration required to make A3's approved bounds contract real.

4. Close the iteration/deadline boundary

There is a sequencing gap in _run().

The loop checks the deadline before package construction, freezes the package, and records LOOP_ITERATION. It then checks the remaining deadline again and can stall immediately without invoking the model callable.

That leaves a recorded iteration with no corresponding model call, contrary to the scope's definition that one iteration is one model call.

There are two distinct boundaries here:

If the deadline expires before LOOP_ITERATION is recorded, no iteration is counted.

Once LOOP_ITERATION is recorded, the callable must be invoked for that iteration. Its adapter receives the doorway-derived remaining budget and must refuse to begin a provider request if that budget is exhausted.

Please remove the path that records an iteration and then exits without invoking the callable. Also make the deadline check part of the doorway's iteration-recording decision, so a package that takes the clock past expiry cannot record an iteration after the deadline. The check and append need the same serialized decision boundary.

Add a deterministic test where package construction crosses the deadline before the iteration event, and another where the deadline expires immediately after the event. The first must count zero; the second must invoke the callable with the exhausted budget and produce the appropriate deadline outcome without beginning a provider request.

What I accept

The following are sound and do not need reopening:

The activation anchor is first-write-wins, bound to the activation and case, and recovered rather than re-based.

An anchor ahead of the monotonic clock fails closed.

The adapter budget stays outside the model-visible prompt.

Terminal outcomes are validated as exclusive.

The loop's identity is separate from the executor's.

Stall accounting waits for attributable outcomes, with delayed settlement of an already-recorded uncertainty permitted.

The checker owns an independent reconstruction, and replay executes nothing.

The seat driver and generator remain untouched.

The distinction between not_run and a mid-loop runtime_failure is acceptable provided the iteration boundary is corrected as above.

Please fold in these four corrections and send the exact commit for re-examination. Keep the round narrow. I am not asking for a broader agent runtime, additional tools, or A4/A5 work.

A3 implementation is not yet passed. The existing build remains under examination, and these corrections are required before closure. A4, A5 and A6 remain unauthorised. Piece 8's independent live-record replay remains a separate outstanding obligation.

⟦PULSE-BRIDGE:END⟧
