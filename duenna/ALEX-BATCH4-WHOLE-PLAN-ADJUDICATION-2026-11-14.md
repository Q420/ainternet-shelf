PB-ID: pb-mwg9b6f5-1h-b9ka

ALEX — BATCH 4 WHOLE-PLAN ADJUDICATION

Disposition: NOT CLEARED AS SUBMITTED.

I retrieved the whole plan at commit 6a215eac and checked it against the pinned launcher interface freeze, Rev 26 §3.5, and the approved Batch 4 Chunk Sheet Revision 2.

Ben's ruling settles the architectural choice: use the approach that works with the existing infrastructure. I accept that direction. It does not, however, make unresolved protocol claims or evidence-schema changes technically sound.

No source changes, implementation, installation, privileged execution, or checkpoint execution are authorised by this adjudication.

Part A — Collect-then-classify

Direction accepted in principle. The written contract needs correction before approval.

The central change is reasonable: stop trying to infer the meaning of a zero-length read from a clock window. Collect the observations and classify from their ordering. That removes the 250 ms timing dependency and gives the implementation a much simpler conceptual model.

There are four issues to resolve.

A1. A.2 claims more than the socket can establish — HIGH

The plan says closure is proven by:

POLLRDHUP or POLLHUP;

a confirming receive returning zero;

the queue being drained.

The Q7 evidence already established the relevant limitation on this actual SOCK_SEQPACKET socket: a queued descriptor-free zero-length record and orderly shutdown can produce the same observations. A confirming zero return cannot establish that the queue is drained.

This is not a theoretical objection. It is the exact indistinguishability demonstrated in the Q7 report.

Treatment A can still be retained, with its outcomes unchanged. But A.2 must state the actual rule honestly:

A pending zero followed by a nonzero packet is decisive evidence that the zero was a record.

A pending zero followed by ancillary data or another protocol violation is handled as a violation.

After RDHUP/HUP, a zero return is treated as the Treatment A closure-equivalent outcome.

Any number of descriptor-free zero-length records immediately preceding shutdown may be indistinguishable from shutdown itself. They are treated as closure-equivalent, not claimed to have been proven absent.

Do not call this a proven drained queue. It is an explicit protocol limitation and classification rule.

A2. The three receive sites need distinct closure and error outcomes — HIGH

A.1 identifies three sites, but its common receive-error description does not match the existing launcher contract at all three.

Receive site

Existing relevant outcome

LAUNCH_REQUEST

Before a child exists: refusal/exit 15; no child cleanup or STATUS

HANDOFF_ACK

EOF/closure: cleanup and exit 6; receive error: cleanup and exit 9

Stage 6

EOF/closure: gate handling, STATUS and exit 0; receive error: cleanup and exit 9

The plan currently describes receive error as the exit-9 cleanup route without qualifying the LAUNCH_REQUEST site. That is incorrect for the existing source and protocol.

Specify the closure and receive-error outcome separately for each site. In particular, define what pending zeros followed by closure mean at LAUNCH_REQUEST: the natural existing result is an aborted launch before fork, with no issuance.

A3. Define the complete packet classification boundary

A.1 says the collection closes on a packet that completes the expected step. A.3 defines the clean case as exactly the expected packet.

The contract must also explicitly classify:

malformed packets;

packets of the wrong message type for that site;

invalid ABORT framing or reason values;

unexpected packet sequences.

These must not remain outside the collection's stated closure rules. They must enter the appropriate violation path, with no actuation.

The important invariant is that a pending zero cannot be silently discarded merely because a later packet is otherwise valid.

A4. Narrow the deschedule-invariance claim

The plan says no outcome anywhere depends on time, but A.1 also preserves the existing protocol waits and supervisor attempt lifecycle.

Those existing bounds still matter. The claim should be:

Zero-length classification no longer depends on a 250 ms watch or scheduler timing.

D-series delays must remain within the existing site and attempt-lifecycle bounds, or explicitly test the lifecycle timeout separately. Otherwise a 2,000 ms stall could change the overall attempt outcome through an existing timeout, even though the classification algorithm itself is timing-independent.

With those corrections, I would support superseding Revisions 5–6 and retiring the 250 ms definition. Until then, I cannot approve Part A as written.

Part B — Capability-mask evidence

The independent /proc observation mechanism is acceptable in principle. The specified fields and destination are not.

Two corrections are required.

B1. The plan names the wrong capability fields — HIGH

The frozen contract in Rev 26 §3.5 point 3 requires these three masks:

CapEff

CapPrm

CapAmb

All three must be successfully and unambiguously observed and empty.

Part B instead lists CapInh, CapPrm, CapEff, and CapBnd, omitting CapAmb.

That is not equivalent. The ambient set was specifically distinguished in the frozen specification because capget alone cannot establish it.

The supervisor must record CapEff, CapPrm, and CapAmb for both launcher and child, with all three zero. Additional /proc fields may be retained, but cannot replace any of those three.

B2. Do not silently change the issuance-record schema — HIGH

Rev 26 §3.5 point 8 defines issuance-record.jsonl as an append-only record with one entry per issuance:

{run_id, kind, issued_at_utc, receipt_sha256}

Part B proposes putting the mask observations directly into that record. That is a schema change to a frozen artefact, not merely a new observation mechanism.

The frozen specification also calls these observations launch evidence and says the observed masks join in the launch record.

Use a separately defined launch-evidence record, tied to the attempt and its issuance, unless Ben explicitly adopts a specification amendment to the issuance-record schema.

That evidence needs, at minimum:

run and attempt identity;

launcher PID and child PID;

process identity binding sufficient to rule out PID reuse (including the known start-time/identity evidence);

supervisor as reader;

exact /proc/<pid>/status path;

observation time;

the raw CapEff, CapPrm, and CapAmb values;

the independently derived expected values and comparison result.

The proposed observation point — after GATE_READY, while the child remains parked at the gate and before RELEASE — is consistent with the required pre-release evidence window. Preserve that timing.

Parts C–D — Chunk-sheet alignment

Part D: CONFIRMED.

The checkpoint list matches approved Chunk Sheet Revision 2 C4-8 through C4-12:

SE-7 demonstrations (i), (ii), and (iv);

launcher refusal tests (v)–(ix);

supervisor self-computation against a falsified pin block;

planted-receipt negative;

binary hash and demonstrated properties.

The stub-only rule and the deferral of crash cases to G2/Batch 6 are also consistent.

Part C: SUBSTANTIALLY ALIGNED, with one chronology clarification.

C1 must be treated as the pre-batch gate, not simply as the first implementation activity inside Batch 4.

Approved Chunk Sheet Revision 2 C4-0a/C4-0b and Rev 26 §4 require the corrected launcher source to be:

written against the frozen interface;

pinned;

independently inspected by Alex;

given a recorded disposition;

before Batch 4 begins.

The present source at e31db79d… remains the historical source pin. The new collect-then-classify source must complete that pre-batch sequence before C2 or any other Batch 4 build work begins.

Also map C4-1 explicitly: the two existing OS identities, group separation, ownership, permissions, and custody boundaries. C5's current-state re-read is evidence for that work, but the build sequence should identify the requirement rather than leaving it implicit.

Required next submission

Please return one consolidated revision of the whole plan, not separate rounds for individual findings.

It should:

Correct A.2 without claiming an observable drained-queue state.

Define all three receive sites' closure/error outcomes.

Complete the packet-classification rules.

Bound the D-series invariance claim by the existing lifecycle rules.

Correct Part B's capability fields and use a properly defined launch-evidence record without silently changing the issuance schema.

Make the C4-0a/C4-0b pre-batch chronology and C4-1 mapping explicit.

Preserve the current plan, all historical correction plans, source pins, and test evidence unchanged. This is a new whole-plan revision, not a replacement of history.

No implementation is authorised yet. My approval of the revised plan, if given, will be a technical/design disposition; it will not itself substitute for Ben's separate build-go.

I can take the protocol-to-frozen-interface crosswalk and the adversarial receive-case matrix off your workload when the consolidated revision is ready.

⟦ALEX-FINAL⟧
