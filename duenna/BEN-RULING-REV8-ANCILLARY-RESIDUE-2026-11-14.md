# BEN'S RULING — WHOLE-PLAN REV 8 ANCILLARY RESIDUE (2026-11-14)

Ruled by Ben, 2026-11-14 03:00 MST (tap on the ruling card,
widget-38f85353, and his own words in the same message):

    "Accept the limitation — Rev 8 clears on my ruling"

## What was ruled

Alex's Rev 8 adjudication (pb-mwgakmnz, shelved verbatim at
6c40acbb) accepted every part of Revision 8 except one disclosed
residue, which he held he could not approve on disclosure alone
because it weakens the existing ancillary-rejection rule rather
than merely describing an observability limit:

- An ancillary-bearing zero-length record queued behind a further
  plain zero-length record, followed by shutdown, is invisible to
  the §A.2 closure observations (FIONREAD counts no bytes; the
  head peek sees only the plain zero at the head). The collection
  can therefore take the closure-equivalent outcome, and that
  ancillary record loses its violation classification.
- Established by the in-room probe (ea13b0cc…, transcript
  48c34126…), sequences C and E, and disclosed in Rev 8 §A.2 with
  the NQ5' limitation demonstration in §A.5.

## The ruling's terms

Ben accepts that loss of ancillary violation classification, in
exactly that bounded case, as an acceptable limitation — in the
family of Treatment A (which covered descriptor-free zero-length
records only), and as a conscious, recorded exception to the
ancillary-rejection rule for this residue alone.

What the acceptance covers:
- The residue exactly as disclosed in Rev 8 §A.2: ancillary
  records queued behind one or more plain zero-length records at
  the moment of the closure check, on this channel/kernel.
- The NQ5' test reporting that case as a limitation
  demonstration, never as a pass of the violation expectation.

What it does NOT cover:
- Ancillary data in any other position: at the head (caught by
  the §A.2 head-ancillary check → violation), on any received
  message (§A.1/§A.3 walk → violation), or delivered by a peek
  (closed on sight). The ancillary-rejection rule stands in full
  everywhere the record is observable.
- Any other weakening of the plan. Parts B–D, the C0 pre-batch
  gate, and the build-go's scope are unchanged.

Recorded consequences, as presented to Ben before he ruled:
the queued descriptor is never installed in the collector, so
nothing leaks; nothing executes; the gate is unaffected; the only
loss is the violation classification of a record in a sequence
the system's own protocol peers cannot produce (neither peer ever
sends ancillary data). The trade named to Ben: acceptance clears
the last open point on the whole plan and opens the C0 gate;
rejection leaves the plan blocked behind a case no demonstrated
observation on this kernel can reach.

## Effect

On the strength of this ruling, Alex is asked to record Rev 8
CLEARED. The C0 pre-batch gate remains the next step and is not
itself authorised by this ruling beyond the standing build-go
(Ben, 2026-11-13 ~16:40 MST, Batches 2–6 in order, subject to C0).
