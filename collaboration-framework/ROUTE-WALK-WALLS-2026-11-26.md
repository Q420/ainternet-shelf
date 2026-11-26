# ROUTE WALK — THE WALLS ON GARY'S ROUTE (2026-11-26)

## SUMMARY

**Verdict: neither dictation angle can be fairly tested until three
walls that are not the test are dealt with — the capture ceiling, the
road seal's sizing, and (for Angle B) the deadline. Everything else
on the route either is the test, is the job's own shape, or is not
binding on this route today and is named so nobody "fixes" it.**

Ordered by Ben 2026-11-26 14:18 MST ("Perfect time to walk his rout
and tare down walls"), after his judgement that neither A nor B will
finish as the route stands. The walk covers the standing job on the
Nemotron seat (Gary, NVIDIA route) — the only route the A/B runs
use. Every number below is measured from the records of
demo-nemotron13/14/15 or read from the code this session.

## THE ROUTE, AS MEASURED

The job: onboard and identify, then per file (stock-take 11,946 B;
a3-pass 4,663 B; index-tail 40,953 B in four blocks) gather and
journal, then summarize, then deliver a brief of at least 550 words.
Eleven worker acts on the honest path.

Measured shape of a call on this route (runs 13–15): a working call
carries ~5,000–6,600 counted presentation tokens; the provider's
reconciled consumption runs ~6,400–7,400 a call. A clean eleven-call
walk projects to roughly 70–80K consumed tokens. The troubled walks
actually run: 13 consumed 122,537 (12 calls, died mid-walk), 14
consumed 114,517 (20 calls, died on the step ceiling), 15 consumed
132,989 (18 calls, died on the capture ceiling — 7,011 tokens short
of the road seal, which was the next wall in its path).

## THE WALLS

**W1 — The capture ceiling: 64,000 bytes. KILLED RUN 15. TEAR DOWN
as a run-killer.**
The evidence contract holds a response whole only below 64,000
bytes (RESPONSE_CAPTURE_CEILING, doorway.py; CAPTURE_CEILING,
evidence.py; R7-1/R8-1). Run 15's eighteenth response was 233,769
chars; the capture refused to commit it and the run stalled on
evidence_capture_failure. The ceiling protects a real thing — a
claim of completeness is never made falsely — but as built it makes
an oversized response a death sentence, and an oversized response
is what a stuck worker produces. Clearing it means: capture what
can be captured, label it partial in the record's own terms, and
let the loop answer the worker ("that answer could not be filed;
here is where you stand") instead of the run dying. The evidence
shape of a partial capture is the examiner's call; the principle
that the ceiling must not kill the run is the director's.

**W2 — The road seal: 140,000 counted tokens. NEARLY KILLED RUN 15;
PROJECTS TO KILL ANGLE B. FIX THE SIZING.**
The seal was sized from a failing walk's price (122,623 over 18
calls) with headroom. A clean walk fits easily (~70–80K). But Angle
B's whole proposition is surviving more corrections: at the
measured per-call price, a 25–30 call B walk projects to
160–200K — over the seal. Under B as commissioned, the run would
die on money before it dies on steps, and the comparison would
record a dictation verdict that the seal actually decided. Fix:
derive each angle's seal from its own shape — the act/iteration
ceilings times the measured per-call price, with the same headroom
logic the 140,000 figure itself used — and record the derivation in
the order record, so the comparison shows both seals and their
bases. This amends a held constant of INDEX 616 (the road seal
stood in its held-constant list); it is proposed under the
director's clear-the-path order and stands only if the examiner
accepts the amendment — the alternative she may prefer is one
shared seal sized for the longer walk, with the asymmetry recorded
as known.

**W3 — The deadline: 1,200 s. SIZED FOR ANGLE A; BINDS ANGLE B.
FIX THE DERIVATION.**
DEMO_BOUNDS' deadline was derived for 20 iterations. Angle B's
commission carries a 60-iteration backstop; at the measured pace
(~23–40 s a call on runs 13–15) a long B walk can reach the wall
clock inside its act budget. Fix: derive B's deadline from its
iteration ceiling by the same per-call allowance the standing
derivation already uses. Angle A's deadline stands as is.

**W4 — The generation cap: 16,384 completion tokens. KILLED RUN
13. NAME AND INSTRUMENT; DO NOT RAISE BLIND.**
Run 13's fatal call spent all 16,384 completion tokens on
reasoning and returned zero answer tokens (INDEX 613). One call
can spend itself entirely on thought and hand back nothing. The
cap is the route's, not the office's invention. What the office
controls is what an empty answer costs: it should stand in the
record as a failed call with its usage shown — never as the
worker's silence or confusion — under both philosophies. No change
proposed beyond that accounting visibility until a run shows more.

**W5 — The journal gate. KEEP. Its failure modes are addressed.**
The gate refuses a journal write that replaces instead of extends
the record. It killed run 14's walk in combination with the
prescription (the two contradicted; the gate-recovery fix, INDEX
615, ended the contradiction), and under Angle B the append makes
the unnatural act unnecessary. The gate protects the record's
integrity; it is the job's shape, not a wall in the road.

**W6 — The stage gates and the delivery floor (550 words). KEEP.**
They are the job's definition of done. Untouched by this scope.

**W7 — Grant bounds: 12 dispatches per tool. KEEP, NAMED.**
The honest walk needs at most 7 of any one kind. A worker burning
re-reads under Angle B could reach 12 on read_range across four
blocks plus retries — the bound is named here so that if a run
dies on it, the record is read correctly the first time.

**W8 — The window (131,072) and road shedding (70%/80%). NOT
BINDING ON THIS ROUTE.**
The largest package counted in runs 13–15 was ~9,732 tokens —
nowhere near the window or the shedding thresholds. Named so the
inventory is complete and nobody spends a fix here.

**W9 — Working-set carriage: 64,000 content bytes. NOT BINDING ON
THIS ROUTE TODAY.**
The desk carries one file at a time plus the journal of record;
index-tail whole is 40,953 B. Named for completeness; it has
killed other seats' wakes on other routes, not Gary's.

**W10 — The ceilings that ARE the test. UNTOUCHED.**
Angle A: 20 iterations, refusals counting. Angle B: 20 worker acts,
corrections free, the 60-iteration record backstop. This scope
does not move them; moving them would clear the experiment, not
the path.

## THE OFFICE'S OWN WALL

The four native-probe unit tests currently fail at import: a
baseline package regenerated from an evidenced run derives a
catalogue hash that does not equal the hash the run recorded. The
derivation's inputs are the sealed grants and the registry's
worker-facing text; which of today's builds moved it is NOT yet
established, and this paper does not guess. Consequence, stated
plainly: the office right now cannot reproduce an evidenced
package, so the probe/replay verification route is itself walled.
No teardown in this scope touches the catalogue or the registry
until that is diagnosed.

## WHAT CLEARING MEANS, IN ORDER

1. Vane examines this walk — W1's partial-capture shape is her
   seat; W2/W3's derivations are arithmetic she can check.
2. Build the fixes under her examination: W1 partial capture, W2
   per-angle seal derivation, W3 B-deadline derivation, W4's
   empty-answer accounting line.
3. Rehearsal witnesses for each fix; the standing suites and
   verify-config green; the probe diagnosis closed or explicitly
   carried.
4. Only then the A/B runs (demo-nemotron16/17) go on the wall —
   with nothing left standing between the worker and the question
   the runs exist to ask.

Filed as INDEX 617. The A/B scope stands at INDEX 616; the
comparison record will be INDEX 618 when the runs exist.
