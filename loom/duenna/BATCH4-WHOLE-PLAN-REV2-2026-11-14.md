# BATCH 4 — THE WHOLE PLAN, REVISION 2 (2026-11-14)

Revision 2 of the whole plan ruled by Ben
2026-11-14 02:17 MST. Revision 1 (62e92c1c…,
commit 6a215eac) is preserved unchanged; this
revision answers Alex's two adjudications of
2026-11-14 (pb-mwg9b6f5, pb-mwg9byjs) as ONE
consolidated correction, as he required.

Changes, mapped to his findings:
- A1: §A.2 rewritten — no claim of a proven or
  drained queue; the closure-equivalence rule is
  stated as what it is (a classification rule
  over an established indistinguishability, Q7).
- A2: per-site closure and receive-error
  outcomes specified (§A.2 table).
- A3: the packet-classification boundary is
  completed (§A.3): malformed packets, wrong
  type for the site, invalid ABORT framing or
  reason, unexpected sequences.
- A4: the invariance claim is narrowed (§A.4)
  and the D-series is bounded by the existing
  lifecycle rules.
- B1: Part B now specifies CapEff, CapPrm,
  CapAmb — the three masks frozen in Rev 26
  §3.5 point 3 — for both launcher and child.
- B2: the mask evidence goes in a SEPARATE
  launch-evidence record (§B.2); the frozen
  issuance-record schema is untouched.
- Part C: C1 is restated as the PRE-BATCH GATE
  and C4-1 is mapped explicitly.
Ben's §A.0 ruling stands unchanged: the
architecture was his choice and is not reopened
by these corrections, which are confined to the
written contract against the freeze and the Q7
evidence.

==================================================
PART A — THE RECEIVE DISCIPLINE
==================================================

## A.0 The ruled architecture (from Revision 1, unchanged)

The launcher never classifies a zero-length read
at the moment it happens. It COLLECTS: a zero
read enters the site's collection as PENDING —
neither record nor closure — and classification
happens only when the collection closes, from
the ordering of what was collected. No clock
defines "immediately preceding"; the notion is
"nothing decisive in between". Treatment A's
outcomes at both affected sites are preserved
exactly (Stage 6: STATUS + exit 0; ACK wait:
cleanup + exit 6). A bare empty record on a
channel that stays open is classified when its
collection closes — by a following packet (which
the pending zero poisons; the packet is not
acted on), by the closure-equivalent outcome,
or by the attempt's own end. An empty record
never actuates anything, in any design.

## A.1 Collection, per receive site

One mechanism, three sites (LAUNCH_REQUEST wait,
HANDOFF_ACK wait, Stage 6 packet wait). Entries:

- ENTRY(record): a received packet, bytes as
  received. Ancillary data is handled at receipt,
  exactly as in the current source: any control
  data closes every delivered descriptor
  immediately and enters a VIOLATION(ancillary)
  entry. A descriptor is never buffered.
- ENTRY(pending-zero): a zero-length receive
  with no ancillary data.
- ENTRY(closure-equivalent): appended under the
  rule in §A.2.
- A receive ERROR closes the collection at once
  with the site's error outcome (§A.2 table).
- MSG_CTRUNC on any received message enters
  VIOLATION(truncated), as today.

The collection CLOSES on the first of: (a) a
packet completing the site's expected step —
classified under §A.3; (b) any VIOLATION entry —
the site's violation outcome; (c) a
closure-equivalent entry — §A.2; (d) a receive
error — §A.2. The protocol's existing waits and
the supervisor's attempt lifecycle bound the
collection; collection introduces no timeout of
its own.

## A.2 Closure-equivalence and per-site outcomes

The rule, stated without overclaim (Q7):

- A pending zero followed by a nonzero packet
  is DECISIVE: on a FIFO channel closure cannot
  precede data, so the zero was a record.
- A pending zero followed by ancillary data or
  another violation is handled as a violation.
- After RDHUP/HUP is observed, a zero return is
  treated as the Treatment A CLOSURE-EQUIVALENT
  outcome. Any number of descriptor-free
  zero-length records immediately preceding
  shutdown may be indistinguishable from
  shutdown itself (Q7); they are treated as
  closure-equivalent. This is an explicit
  protocol limitation and classification rule —
  NOT a claim that the queue was observed
  drained, and NOT a claim that such records
  were proven absent.

Outcomes by site (closure-equivalent / receive
error), matching the existing launcher contract:

- LAUNCH_REQUEST: closure-equivalent before any
  request packet = an aborted launch BEFORE
  FORK — refusal/exit 15 route; no child exists,
  no child cleanup, no STATUS, no issuance.
  A receive error at this site takes the same
  pre-fork refusal route (exit 15); there is no
  child to clean up.
- HANDOFF_ACK: closure-equivalent = cleanup and
  exit 6 (the EOF outcome). Receive error =
  cleanup and exit 9.
- Stage 6 packet wait: closure-equivalent =
  gate handling, STATUS, and exit 0 (the EOF
  outcome). Receive error = cleanup and exit 9.

Pending zeros at LAUNCH_REQUEST followed by a
valid request packet: the zeros were records
(FIFO-decisive) — the request is poisoned per
§A.3 and refused (exit 15 route); nothing is
forked.

## A.3 Classification (a pure function of the collection)

Exactly one outcome per site, from the collected
sequence alone:

- CLEAN: the collection is exactly the site's
  expected packet — no pending zeros, no other
  entries → the site proceeds as in the current
  contract (request validated; ABORT at the ACK
  wait dispatched per abort_packet_valid();
  RELEASE actuates; a Stage 6 ABORT takes the
  class-T/class-F lifecycle, unchanged).
- POISONED: one or more pending zeros precede an
  otherwise valid expected packet → protocol
  violation (exit 8 route; the packet is NOT
  acted on). A pending zero is never silently
  discarded merely because a later packet is
  otherwise valid.
- MALFORMED / WRONG TYPE / BADLY FRAMED: any
  received packet that is malformed, of the
  wrong message type for the site, an ABORT with
  invalid framing or an out-of-catalogue reason
  value, or part of an unexpected packet sequence
  for the site's state → protocol violation
  (exit 8 route, or the site's refusal route at
  LAUNCH_REQUEST), no actuation. These packets
  close the collection under §A.1(b).
- VIOLATION ENTRY (ancillary / truncated)
  anywhere → the violation outcome, as today
  (Z1/Z2/NQ3 outcomes preserved).
- CLOSURE-EQUIVALENT with only pending zeros
  before it → the site's closure outcome (§A.2).
  A closure-equivalent entry cannot follow a
  completed expected packet (the collection
  would already have closed).

## A.4 The bounded invariance claim

The claim is exactly this: the CLASSIFICATION of
zero-length reads no longer depends on a 250 ms
watch or on scheduler timing. The protocol's
existing site waits and the supervisor's attempt
lifecycle remain in force and can still end an
attempt on their own terms. The D-series stall
tests therefore use delays WITHIN the existing
site and lifecycle bounds; any test of a
lifecycle timeout itself is a separate, named
case, not part of the D-series.

## A.5 What Part A removes; test rework

Removed: zero_classify() and the peek; the
poll-sampling classification; the 250 ms watch;
correction-plan Revisions 5–6; W1–W4 and L1/L2
(tests of a retired window). Retained exactly:
the ancillary walk at receipt; chan_recv's
receipt-level returns (malformed/truncated/
error/ancillary are RECEIPT facts, not
classifications); abort_packet_valid(); every
exit-code route and cleanup contract of the
current source.

Test mapping (outcomes preserved): P-series and
A1–A5 unchanged. Z1/Z2 unchanged (receipt
facts). Z3/Z4 → Z3'/Z4': empty record then the
site's expected packet → poisoned (violation,
packet not acted on); plus empty record then
attempt teardown → no classification, no
actuation. NQ1 unchanged in outcome. NQ2 → NQ2':
pending zeros then closure-equivalent, both
sites → the closure outcomes, labelled
limitation demonstrations. NQ3 → NQ3': pending
zero, then a descriptor-bearing record → the
VIOLATION entry closes the collection (exit 8,
descriptor closed at receipt, kernel-discard
check retained). D-series: test-builds-only
stall hook at named points in the collection
path, delays within lifecycle bounds (50/300 ms
class); every stalled case's outcome identical
to its unstalled form. Full suite five
consecutive runs, individual results, as before.

==================================================
PART B — CAPABILITY-MASK EVIDENCE (freeze §3)
==================================================

## B.1 The observation

Rev 26 §3.5 point 3 requires three masks —
CapEff, CapPrm, CapAmb — successfully and
unambiguously observed and EMPTY. (The ambient
set is named because capget alone cannot
establish it.) The supervisor observes, from
/proc/<pid>/status, for BOTH processes:

- the LAUNCHER's CapEff, CapPrm, CapAmb;
- the CHILD's CapEff, CapPrm, CapAmb.

Observation point (as adjudicated consistent):
after GATE_READY, while the child is parked at
the gate, before the supervisor sends RELEASE.
Additional /proc fields may be retained in the
evidence but cannot replace any of the three.
The launcher's in-process caps_verified_empty()
remains a pass/fail actuation gate; the RECORD
carries the observed values.

## B.2 The launch-evidence record (separate)

The frozen issuance-record schema (Rev 26 §3.5
point 8: {run_id, kind, issued_at_utc,
receipt_sha256}) is NOT changed. The mask
observations go in a separately defined
LAUNCH-EVIDENCE record, one per attempt, tied
to the attempt and its issuance, carrying at
minimum:

- run identity and attempt identity;
- launcher PID and child PID;
- process identity binding sufficient to rule
  out PID reuse (the start-time/identity
  evidence already used by the handoff
  contract);
- the reader: the supervisor;
- the exact /proc/<pid>/status path read, per
  process;
- the observation time;
- the raw CapEff, CapPrm, CapAmb values, per
  process;
- the independently derived expected values
  (all zero) and the comparison result.

Checkpoint read-back: the Batch 4 checkpoint
re-reads the launch-evidence records and the
comparison results as part of its evidence.

==================================================
PART C — THE BATCH 4 BUILD SEQUENCE
==================================================

C0. THE PRE-BATCH GATE (C4-0a/C4-0b, binding
    chronology): the corrected launcher source
    (Part A) is written against the frozen
    interface, pinned, independently inspected
    by Alex, and given a recorded disposition —
    ALL BEFORE Batch 4 begins. The current
    source pin e31db79d… remains the historical
    pin; the new source completes this gate as
    its own pin.
C4-1 (mapped explicitly): the two existing OS
    identities (pilot-supervisor, pilot-harness),
    group separation, ownership, permissions and
    custody boundaries stand as established; the
    current-state re-read (f1186a70…) is this
    chunk's evidence; any divergence stops the
    batch and is reported. No identities are
    recreated.
C2. Supervisor programme (pilot-supervisor):
    the §3.5 points 2–9 build — descriptor
    verification, exec-condition checks, pidfd
    establishment validation and the readiness
    contract, the state table, issuance
    START/TERMINAL/CRASH and the issuance record
    (frozen schema), the Part B launch-evidence
    records, the commitments store
    (supervisor-custodied, harness-inaccessible),
    examiner verification hooks (data shapes;
    §3.7 tooling itself is Batch 6). ABORT
    reason numbering 1–7 cross-checked
    identically against the launcher and
    recorded.
C3. Harness entry at the compiled-in path
    (pilot-harness identity), against the stub
    subject only — no subject call anywhere in
    the batch (standing rule C4-D2).
C4. Launcher binary built from the C0-cleared
    pin, installed root:pilot-supervisor mode
    4710, with the dated operator evidence item
    (chown, chmod, OS read-back) per the chunk
    sheet's C4-0c addendum.
C5. Pre-batch evidence as already gathered:
    current-state re-read (f1186a70…) and
    probe-evidence verification (18d9b0d9…)
    stand.

==================================================
PART D — CHECKPOINT (as confirmed)
==================================================

One checkpoint bundle, discharging chunk sheet
Rev 2 C4-8…C4-12 in a single submission: SE-7
demonstrations (i), (ii), (iv); launcher refusal
tests (v)–(ix) executed as the pilot-harness
identity; supervisor self-computation against a
falsified pin block; planted-receipt negative
against a prototype anchor check; Part B
read-back evidence; the built binary's hash and
demonstrated properties pinned by dated
continuation (distinct from the source pin);
records and artefacts ride with the bundle
(C4-D1). The crash cases run formally at gate
G2 on the assembled package (Batch 6), as
already ruled.

==================================================
PART E — SUPERSESSIONS AND THE PROCESS RULE
==================================================

Superseded: correction-plan Revisions 5–6 and
the 250 ms definition of "immediately preceding"
(replaced by §A.0's ordering definition, outcomes
preserved). Preserved: Revision 1 of this plan
and all historical plans, pins, bundles and test
evidence; Treatment A's outcomes; Fix B; the
ancillary rules; the packet catalogue; custody;
the ABORT lifecycle; the frozen issuance-record
schema; chunk sheet Rev 2.

Process rule (Ben, 2026-11-14): whole rounds.
Corrections are batched one round per checkpoint.
Parallel lanes: while the build proceeds, Alex
holds the protocol-to-frozen-interface crosswalk
and the adversarial receive-case matrix (his
offer, accepted) so the checkpoint review starts
from his own matrix.
