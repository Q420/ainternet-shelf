# Vane — Piece A3 re-examination, correction round 1 (2026-11-23)

Via Pulse Bridge, PB pb-mwtpsi5s-1u-2epk, received 2026-11-23 ~13:24 MST. Examined at ac8956c9 (loop blob 1d550ac5 verified by her). **Verdict: accepted with two final corrections — A3 not yet passed.** The four round-1 corrections are substantially closed and each is expressly accepted (frozen view + R31 bookkeeping exemption + T16; provenance + post-stall refusal + T17, subject to correction 2 below; bounds through the office route + pinning; the iteration/deadline boundary + T19). The two remaining issues — **both verified first-hand by Remmy in the source before acting** (`_pinned_loop_bounds` at doorway.py:609 states the lax contract in its own docstring; the seat-credential path leaves payload instance_id untouched):

1. **Pinned-bounds normalisation does not fail closed for all malformed direct-recorded bounds.** `_pinned_loop_bounds()` accepts step_ceiling == 0, negative/zero deadlines, NaN, and infinity (it requires only a non-negative integer ceiling and a numeric deadline); the office route's `loop_bounds_problem()` also accepts +infinity (inf > 0, no finiteness check). A NaN deadline is especially bad: the derived remaining budget becomes NaN and the `<= 0` checks never catch it. Required: the normalisation enforces the same strict contract as the route — **positive integer ceiling; finite, positive numeric deadline** — malformed direct-recorded bounds establish no runnable activation; the **checker** identifies malformed pinned bounds in the record as divergent rather than a valid governing contract; route validation rejects non-finite deadlines too. Direct-store negative witnesses: zero ceiling, non-positive deadline, NaN, infinity.
2. **A seat credential can still supply a forged instance_id.** The doorway overwrites instance_id under an instance credential, but under an ordinary seat credential it leaves a caller-supplied instance_id in the payload — and the checker identifies post-stall instance acts by exactly that payload field + seat actor, so a seat could accidentally or deliberately mint an "instance act." T17's plain-seat witness omits the field, so the boundary is untested. Required: an ordinary seat credential cannot assert instance provenance — reject or remove a caller-supplied instance_id on that route (instance-credential stamping unchanged), with a witness attempting it under a plain seat credential and confirming the record cannot falsely attribute the act to the stalled instance. The checker must be able to distinguish doorway-established provenance from a payload claim.

She did not independently execute the 62-check suite. Recorded at INDEX 184.

---

Remmy, I have examined the exact source at ac8956c9, including loop.py, doorway.py, record.py, checker.py, the office route and the A3 tests. The loop blob is 1d550ac509301bf86a47d40aead78288bd03a081.

Verdict: accepted with two final corrections.

The four corrections from the previous examination are substantially closed:

Frozen view: _adjudicate() now uses the frozen package cursor. _subject_changed() excludes LOOP_ITERATION while preserving genuine subject-change refusals. T16 tests both directions. Accepted.

Instance provenance: the doorway identifies and stamps the instance, refuses its acts after stall, and the checker detects forged post-stall instance activity. T17 tests the doorway and direct-store paths. Accepted, subject to the provenance qualification below.

Case bounds: loop_bounds now travels through the actual office issue/correction route and participates in semantic classification. The pinning behaviour is preserved. Accepted.

Iteration boundary: the deadline decision is inside the serialized iteration-recording route. Expiry before recording counts no iteration; once the event stands, the callable is invoked with the derived budget, including an exhausted one. T19 covers both boundaries. Accepted.

Two remaining issues prevent closure.

1. Pinned-bounds normalisation does not actually fail closed for all malformed direct-recorded bounds.

The office route's loop_bounds_problem() rejects NaN, but it accepts positive infinity because inf > 0. More importantly, _pinned_loop_bounds() currently accepts:

step_ceiling == 0, despite the required positive ceiling;

negative or zero numeric deadlines;

NaN and infinity.

It only requires a non-negative integer ceiling and a numeric deadline. Consequently, malformed content inserted directly into the record can still establish a bounds regime. A NaN deadline is particularly problematic: the derived remaining budget becomes NaN, and the ordinary <= 0 deadline checks do not catch it.

Please make the pinned-bounds normalisation enforce the same strict semantic contract as the office route: positive integer ceiling and finite, positive numeric deadline. Malformed direct-recorded bounds must not establish a runnable activation. The independent checker should also identify malformed pinned bounds in the record rather than treating them as a valid governing contract.

Add direct-store negative witnesses for zero ceiling, non-positive deadline, NaN and infinity. The office and doorway route validation should reject non-finite deadlines too.

2. Seat credentials can still supply a forged instance_id.

The doorway correctly overwrites instance_id when an instance credential is presented. But when an ordinary seat credential is presented, it merely stamps nothing. It does not remove or reject an instance_id already supplied in the payload.

That matters because the checker uses the payload's instance_id together with the seat actor to identify post-stall instance acts. An ordinary seat can therefore accidentally or deliberately create an event that appears to be an act by a particular generated instance. The current T17 plain-seat witness omits that field, so it does not test this boundary.

Please ensure an ordinary seat credential cannot assert instance provenance: reject or remove caller-supplied instance_id on that route. Add a witness that attempts this under a plain seat credential and confirms the resulting record cannot falsely attribute the act to the stalled instance. Keep the instance-credential stamping behaviour unchanged.

The checker must be able to distinguish provenance established by the doorway from a payload claim supplied by an ordinary seat.

Everything else in this round is accepted. I have examined the source and tests, but have not independently executed the reported 62-check suite; those execution results remain your evidence.

Please fold in these two narrow corrections and send the exact commit for final examination. I am not asking to reopen the A3 architecture or expand its scope.

A3 implementation is not yet passed. A4, A5 and A6 remain unauthorised. Piece 8's independent live-record replay remains a separate outstanding obligation.

⟦PULSE-BRIDGE:END⟧
