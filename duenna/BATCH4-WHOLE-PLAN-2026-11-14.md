# BATCH 4 — THE WHOLE PLAN (2026-11-14)

RULED BY BEN, 2026-11-14 02:17 MST, in his words:
"Whatever will work with the existing infrastructure
is what I choose." The plan below is the
infrastructure-based design — it is ADOPTED,
including §A.0 (classification deferred to
collection close; "immediately preceding" defined
by ordering, not by a clock). It now goes to Alex
ONCE for adjudication of the Part A supersessions
against his Rev 5/6 approvals; Parts B–D restate
already-approved material (chunk sheet Rev 2,
Rev 26 §3.5, the freeze).


Drafted from the existing infrastructure — Rev 26
§3.5, the Batch 0 interface freeze
(launcher-interface-freeze.md, 6bb9ae80…), and the
Batch 4 chunk sheet Revision 2 (approved at
6dde1790) — at Ben's direction of 2026-11-14
02:12 MST: one plan for the whole remaining path,
ruled on by BEN before Alex sees it.

This plan replaces the serial correction-round
path for the launcher. It covers, in one document:

  A. the receive discipline (collect-then-classify)
  B. the capability-mask evidence (freeze §3
     carry-forward, Alex's open Batch 4 gate item)
  C. the Batch 4 build sequence (supervisor,
     harness, installation, commitments)
  D. the checkpoint: demonstrations and acceptance
  E. what this plan supersedes, and the process
     rule that keeps it whole

Nothing in Parts C–D is new design: they restate
chunk sheet Rev 2 and Rev 26 §3.5/§4 as one build
sequence. Part A is the one architectural change,
and §A.0 is the ruling Ben is asked for.

==================================================
PART A — THE RECEIVE DISCIPLINE
==================================================

## A.0 The ruling requested

The launcher's classification problem exists
because the current mechanism CLASSIFIES A
ZERO-LENGTH READ AT THE MOMENT IT HAPPENS. Every
defect of the last six rounds lives in that
instant: the read is ambiguous (a record, or the
peer closing), so the mechanism samples other
state (poll, peek, RdHUP, a 250 ms watch) to guess
which — and timing machinery breeds timing
findings.

The proposed discipline never classifies a
zero-length read when it happens. It COLLECTS.
A zero read is entered in the site's collection
as PENDING — neither record nor closure — and
classification happens only when the collection
closes on evidence that ordering (FIFO) makes
decisive:

- a real packet arrives AFTER a pending zero:
  the zero preceded data on a FIFO channel,
  closure cannot precede data, so the zero WAS
  a record. (Decisive.)
- closure is PROVEN (see A.2): any pending zeros
  take the closure outcome — the Treatment A
  limitation, restated in ordering terms: zeros
  with nothing decisive between them and a
  proven closure are equivalent to closure.
  Identical outcomes to the present ruling at
  both sites (Stage 6: STATUS + exit 0;
  ACK wait: cleanup + exit 6). What changes is
  that NO CLOCK defines "immediately": the
  notion is "nothing decisive in between".

Consequences Ben is ruling on, stated plainly:

1. The 250 ms watch and plan Revisions 5–6 are
   retired unbuilt/built-but-superseded. There
   is no window and no deadline inside
   classification at all; scheduler behaviour
   cannot change an outcome.
2. A bare empty record on a channel that stays
   open (today's Z3/Z4) is no longer classified
   the moment it is read. Its violation is
   determined when the collection closes: by a
   following packet (which the pending zero
   poisons — the packet is NOT acted on), by
   proven closure (closure outcome, per the
   limitation), or by the attempt's own end
   (teardown by PDEATHSIG / supervisor action,
   where classification never happens because
   the attempt is already dead). The safety
   property is unchanged: an empty record never
   actuates anything, in any design.

## A.1 Collection, per receive site

One mechanism, three sites (LAUNCH_REQUEST wait,
HANDOFF_ACK wait, Stage 6 packet wait). At each
site the launcher holds a collection:

- ENTRY(record): a received packet, bytes as
  received. Ancillary data is handled at receipt,
  exactly as now: any control data on a message
  closes every delivered descriptor immediately
  and enters a VIOLATION(ancillary) entry — a
  descriptor is never buffered.
- ENTRY(pending-zero): a zero-length receive
  with no ancillary data.
- ENTRY(closure): appended when closure is
  proven (A.2).
- A receive ERROR (−3 class today) closes the
  collection at once with the existing fail-closed
  outcome (cleanup, no STATUS, exit 9 route).
- MSG_CTRUNC on any received message enters
  VIOLATION(truncated) (as today).

The collection CLOSES on the first of:
(a) a packet that completes the site's expected
    step — classified under A.3;
(b) a VIOLATION entry — the site's violation
    outcome (exit 8 route, cleanup, no STATUS,
    nothing actuated);
(c) a closure entry — A.3;
(d) receive error — as above.
The site's normal bound applies while collecting
(the protocol's existing waits and the
supervisor's attempt lifecycle; collection
introduces no new timeout of its own).

## A.2 Proven closure

After a pending-zero, closure is proven when:
a poll shows POLLRDHUP/POLLHUP, AND a confirming
receive returns zero with the queue drained.
Proof is a STATE (the peer has closed and
nothing remains), not an inference from a single
read — and it is only ever used to close a
collection, never to classify a packet.

## A.3 Classification (a pure function of the collection)

When the collection closes, exactly one outcome
per site, decided from the collected sequence
alone — no clock is consulted:

- Clean: the collection is exactly the site's
  expected packet, no pending zeros, no other
  entries → the site proceeds as today
  (request validated; ACK dispatched per
  abort_packet_valid() where ABORT is the packet;
  RELEASE actuates; ABORT at Stage 6 takes the
  class-T/class-F lifecycle, unchanged).
- Poisoned: one or more pending zeros precede
  the expected packet → protocol violation
  (exit 8 route; the packet is NOT acted on —
  NQ1's outcome, now structural).
- Ancillary / truncated VIOLATION entry anywhere
  → violation outcome, as today (Z1/Z2/NQ3
  outcomes preserved; NQ3's queued descriptor is
  a collected VIOLATION entry — the peek and its
  MSG_CTRUNC assumption are gone entirely).
- Closure with only pending zeros before it →
  the closure outcome (Treatment A residue,
  A.0). Closure with a partial/expected packet
  already collected is impossible by construction
  (the collection would have closed at (a)).

## A.4 What Part A removes

zero_classify() and the peek; the poll-sampling
classification; the 250 ms watch; Revisions 5–6
of the correction plan; W1–W4 and L1/L2 (tests of
a window that no longer exists). The ancillary
walk at receipt, chan_recv's −2/−3/−4 returns at
the point of receipt (malformed/truncated/error/
ancillary are RECEIPT facts, not classifications),
abort_packet_valid(), and every exit-code route
and cleanup contract remain exactly as built.

## A.5 Test rework (mapping, not a new suite)

Every existing peer case maps to a collection
form with its outcome preserved, except the
window tests, which are retired with the window:

- P-series, A1–A5 (ACK-wait ABORT validation):
  unchanged in form and outcome.
- Z1/Z2 (descriptor on the consumed record):
  unchanged (receipt fact).
- Z3/Z4 → Z3'/Z4': empty record, then the site's
  expected packet → poisoned: violation, packet
  not acted on; plus empty record, then attempt
  teardown → no classification, no actuation.
- NQ1: unchanged outcome (poisoned RELEASE).
- NQ2 → NQ2': pending zeros then proven closure,
  both sites → closure outcomes, labelled
  limitation demonstrations (as now).
- NQ3 → NQ3': pending zero, then a descriptor-
  bearing record, then closure → the descriptor
  entry closes the collection as a violation
  before closure is reached: exit 8, descriptor
  closed at receipt, kernel-discard check
  retained.
- NEW D-series (deschedule invariance): a
  test-builds-only stall hook at several points
  in the collection path (before a read, after a
  pending zero, before classification) with
  delays of 50/300/2000 ms; every case's outcome
  must be IDENTICAL to its unstalled form,
  because no outcome depends on time. This is
  the property the watch could not offer, stated
  as a test.
- Stability: the full suite five consecutive
  runs, individual results, as before.

==================================================
PART B — CAPABILITY-MASK EVIDENCE (freeze §3)
==================================================

The freeze requires the three observed capability
masks to be preserved as launch evidence, the
parent's joining the child's in the launch
record. Mechanism, from existing infrastructure
(/proc, read by the supervisor — the route Alex
accepted in principle at the readings round, now
specified as he required):

- Observation points: (i) the LAUNCHER's masks —
  read by the supervisor from
  /proc/<launcher_pid>/status (CapInh/CapPrm/
  CapEff/CapBnd) after GATE_READY, before it
  sends RELEASE; (ii) the CHILD's masks — read
  by the supervisor from /proc/<child_pid>/status
  at the same point (the child is then parked at
  the gate, pre-exec, in its settled identity).
- Record: both observations are written into the
  issuance record for the attempt, each with its
  provenance: reader (the supervisor), the /proc
  path, the pid, and the read time. The
  launcher's in-process caps_verified_empty()
  remains a pass/fail actuation gate; the RECORD
  carries the observed values, which is what the
  freeze asks for.
- Read-back: the Batch 4 checkpoint re-reads the
  record and independently re-derives the
  expected mask values from the protocol
  (launcher settled: supervisor identity, all
  masks zero except as §3.5 specifies; child at
  gate: harness identity, zero masks), and the
  comparison is part of the checkpoint evidence.

==================================================
PART C — THE BATCH 4 BUILD SEQUENCE
==================================================

One build, from chunk sheet Rev 2 / Rev 26 §3.5:

C1. Launcher source corrected per Part A (one
    source change, one new pin, diff against
    e31db79d…), unit + peer suites per A.5.
C2. Supervisor programme (Python, pilot-
    supervisor): the §3.5 points 2–9 build —
    descriptor verification, exec-condition
    checks, pidfd establishment validation and
    the readiness contract, the state table,
    issuance START/TERMINAL/CRASH and the
    issuance record (with Part B's mask
    observations), the commitments store
    (supervisor-custodied, harness-inaccessible),
    examiner verification hooks (data shapes;
    §3.7 tooling itself is Batch 6). ABORT reason
    numbering 1–7 cross-checked identically
    against the launcher and recorded.
C3. Harness entry at the compiled-in path
    (pilot-harness identity), against the stub
    subject only — no subject call anywhere in
    the batch (standing rule C4-D2).
C4. Launcher binary built from the C1 pin,
    installed root:pilot-supervisor mode 4710,
    with the dated operator evidence item
    (chown, chmod, OS read-back) per the chunk
    sheet's C4-0c addendum.
C5. Pre-batch evidence as already gathered:
    current-state re-read (f1186a70…) and probe-
    evidence verification (18d9b0d9…) stand.

==================================================
PART D — CHECKPOINT
==================================================

One checkpoint bundle, discharging chunk sheet
Rev 2 C4-8…C4-12 in a single submission:

- SE-7 demonstrations (i), (ii), (iv).
- Launcher refusal tests (v)–(ix), executed as
  the pilot-harness identity (the launcher
  refuses the harness identity and non-allowlist
  invocations at the OS boundary).
- Supervisor self-computation verified against a
  falsified pin block in a scratch run.
- Planted-receipt negative rejected by a
  prototype anchor check.
- Part B read-back evidence.
- The built binary's hash + demonstrated
  properties pinned by a dated continuation
  (distinct from the source pin, per C4-0b).
- Records and artefacts ride with the bundle
  (standing rule C4-D1).
The crash cases (between-steps kill;
interrupted write) are NOT this checkpoint's —
they run formally at gate G2 on the assembled
package (Batch 6), as already ruled.

==================================================
PART E — SUPERSESSIONS AND THE PROCESS RULE
==================================================

Superseded by this plan on Ben's ruling:
- Launcher correction plan Revisions 5 and 6
  (the watch and its fixes) — Rev 6 was approved
  by Alex but is UNBUILT; the source stands at
  pin e31db79d… and all bundles/pins/history are
  preserved unchanged.
- The 250 ms definition of "immediately
  preceding" — replaced by A.0's ordering
  definition, outcomes preserved.

Preserved without change: Treatment A's outcomes
at both sites; Fix B; the ancillary rules; the
packet catalogue; custody; the ABORT lifecycle;
chunk sheet Rev 2 Parts C4-1…C4-12 groupings;
every historical pin and bundle.

Process rule (Ben, 2026-11-14): work is proposed
in WHOLE ROUNDS. A plan covers the whole
remaining path it belongs to; corrections after
a checkpoint are batched into one correction
round per checkpoint, not one round per finding.
Alex receives this plan once (after Ben's
ruling), reviews the built checkpoint once.

Open items after this plan, named so they are
not surprises: Alex's adjudication of Part A's
supersession of his Rev 5/6 approvals and of the
"immediately preceding" redefinition; the Batch
4 checkpoint itself; then Batches 5 and 6 under
Ben's standing build go.
