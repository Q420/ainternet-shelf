# BATCH 4 — PROBE REPORT: ZERO-LENGTH ANCILLARY RECORDS (2026-11-14)

Answers the remaining finding in Alex's Rev 7 adjudication
(pb-mwgack03): can a zero-length record carrying SCM_RIGHTS exist on
the specified AF_UNIX SOCK_SEQPACKET channel, queued behind a pending
zero, invisible to FIONREAD?

Probe run in the environment of record (Ben's laptop room, WSL2,
kernel 6.18.58.1-microsoft-standard-WSL2, Python 3.14.4).
Artefacts: probe_ancillary.py sha256 ea13b0cc…; transcript
probe-ancillary-2026-11-14.txt sha256 48c34126…. Every claim below is
a transcript line.

## Findings

1. THE RECORD FORM IS POSSIBLE (Sequence A). A zero-length sendmsg
   carrying one SCM_RIGHTS descriptor queues as its own record on an
   open channel: FIONREAD reports 0, POLLIN is set, and a receive
   returns n=0 WITH the descriptor, which is live and readable.

2. ALEX'S SEQUENCE IS REAL (Sequence B: [Z, Z+rights, shutdown]).
   After the first (plain) zero is received, the observations are
   exactly the Rev 7 closure pair — FIONREAD=0, POLLRDHUP observed —
   while the ancillary record is still queued. Under the Rev 7 rule
   as written, closure-equivalence would be classified and the
   ancillary record never received. The gap is confirmed, not
   hypothetical.

3. A HEAD PEEK SEES THE ANCILLARY RECORD (Sequences B, C). A
   MSG_PEEK receive taken with a control buffer, at the moment the
   ancillary record is at the head of the queue, returns n=0 WITH
   SCM_RIGHTS present. The peek does not consume the record: the
   following real receive delivers it (descriptor closed by the
   receiver, per §A.3). A peek at a plain zero head returns n=0 with
   no ancillary — indistinguishable from an empty queue.

4. PEEK DELIVERS REAL DESCRIPTORS (Sequence D). Each peek at the
   ancillary record installed a NEW descriptor in the probing
   process (fd count rose by one per peek; the peeked numbers
   differed each time), and the record still delivered a further
   descriptor at the real receive. Consequence for the contract:
   a peek is an observation that can itself deliver descriptors —
   any descriptor a peek delivers must be closed immediately, and
   ancillary presence on a peek is a signal, never a receipt.

5. NO OBSERVATION PROVES THE QUEUE EMPTY OF RECORDS (Sequences B, C,
   E). With the queue empty and the peer shut down, FIONREAD=0,
   POLL=POLLIN|POLLRDHUP and PEEK n=0/no-ancillary are IDENTICAL to
   their values while a plain zero-length record is still queued.
   A peek returns EAGAIN only when the peer is still OPEN and the
   queue is empty. So no drain-termination proof exists in this
   primitive set: an ancillary record queued behind a FURTHER plain
   zero (Sequence C, check-time head = plain zero) is not visible
   to a head peek, and no observation distinguishes "one more plain
   zero queued" from "queue empty, peer closed" (the Q7 residue,
   now evidenced for this case as well).

## What this settles and what it does not

Settled: the record form exists; Alex's sequence defeats the Rev 7
closure rule as written; a head peek with a control buffer detects
the ancillary record in Alex's sequence and in any state where the
ancillary record has reached the head of the queue.

Not settled by any demonstrated primitive: an ancillary record
queued behind one or more plain zero-length records at the moment
of the closure check. That residue is the same in-principle class
as Q7 (zero-length records are invisible to every whole-queue
observation demonstrated on this kernel) and is carried into
Revision 8 as a disclosed limitation in the Treatment A family —
stated, bounded, and never claimed as solved.
