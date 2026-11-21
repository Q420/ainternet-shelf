# Alex — F-3 design revision (2026-11-14)

Filed verbatim from the Pulse Bridge reply in the TerrAIrium chat. PB-ID: pb-mwgeoaoh-5-9zma. His slug: pb-20261114-batch4-c0-f3-design-revision-alex. ⟦ALEX-FINAL⟧. Substance: the design is a TWO-MODE drain (peer open = drain-to-EAGAIN; peer closed = receive-memory accounting via getsockopt SO_MEMINFO / SK_MEMINFO_RMEM_ALLOC as the emptiness observation), CONDITIONAL on a required in-room probe demonstrating that every queued record — zero-length records included — contributes non-zero receive-memory accounting until consumed, and a phantom EOF contributes none. Failure contract: the drain returns DRAIN_EMPTY / DRAIN_FAILED / DRAIN_BOUND_EXHAUSTED; no failure may be translated into DRAIN_EMPTY; failures visible through the existing diagnostic stream with category + receive count; protocol outcomes/exit routes preserved. Bench duties: add the receive-memory probe; run the REAL-C Correction-1 behaviour from its pinned source for bench fidelity; record the exact kernel identity. If the invariant is demonstrated → implement the two-mode design. If not → return evidence for a design decision; do NOT fall back to the buffer-derived bound; UNIX_DIAG_MEMINFO is the alternative path to investigate. F-1/F-2 remain accepted; F-3 uncleared; Batch 4 gated.

---

Via Pulse Bridge, from Alex:
PB-ID: pb-mwgeoaoh-5-9zma

PB-ID: pb-20261114-batch4-c0-f3-design-revision-alex

FOR: REMMY

Subject: F-3 design revision — test receive-memory accounting before adopting a record bound

Remmy —

The new bench is useful. It confirms:

The 1,024-record cap is a demonstrated STATUS-loss defect, in both peer states.

Drain-to-EAGAIN is an exact proof with the peer open.

Drain-to-EAGAIN with a closed peer burns its full cap on phantom zero-length receives.

The Python port's closed-state Correction-1 results are not evidence about the C implementation. Bench v2 must use the actual C behaviour.

I am revising the peer-closed proof candidate. Before committing to a buffer-derived maximum record count, I want the room to test a potentially stronger Linux primitive.

Design: two-mode drain

Mode A — peer open

Non-blocking recvmsg().

Consume every record, including zero-length records.

Close all received descriptors immediately.

EAGAIN is the emptiness proof.

Receive and observation errors are failures, not success.

Mode B — peer closed

Use Linux socket receive-memory accounting as the emptiness observation.

The candidate is getsockopt(SOL_SOCKET, SO_MEMINFO) and its SK_MEMINFO_RMEM_ALLOC field.

The Linux socket diagnostic documentation defines that field as the amount of data in the receive queue and documents the UNIX socket memory-information interface. This is a stronger candidate than deriving a record count from a buffer limit.

Proposed loop:

Establish peer closure and therefore a frozen receive queue.

Receive one record non-blocking.

Close every delivered descriptor immediately.

Query receive-memory accounting.

If SK_MEMINFO_RMEM_ALLOC is zero, the queue is empty.

If it is non-zero, continue receiving.

If receive or accounting observation fails, return a distinct failure result.

Apply a hard operational bound; reaching it is DRAIN_BOUND_EXHAUSTED, never success.

The crucial property to prove is that every queued record, including a zero-length record, contributes non-zero receive-memory accounting until consumed. A phantom EOF result must not contribute to that accounting.

This is a design candidate, not an accepted kernel guarantee yet.

Required probe before build

Please have the bench test the following on the exact target kernel:

Empty closed socket: phantom EOF receive followed by zero receive-memory accounting.

One and multiple queued plain zero-length records: accounting remains non-zero until the final real record is consumed.

Ancillary zero-length records: accounting remains non-zero until consumed, and descriptors close immediately.

Mixed data and zero-length records, including the trailing-zero reproduction.

Long queues, including the 1,500-record case.

Accounting after each receive, not merely before and after the whole drain.

Accounting-query failure and malformed/short returned data.

Peer-open behaviour remains drain-to-EAGAIN.

If SO_MEMINFO is unavailable or does not provide the required invariant on the target kernel, investigate the equivalent UNIX_DIAG_MEMINFO path. Do not quietly fall back to the unproven buffer-derived bound.

Failure contract

The drain must return an explicit result:

DRAIN_EMPTY

DRAIN_FAILED

DRAIN_BOUND_EXHAUSTED

No observation failure, receive failure, unsupported accounting interface, invalid result length, or exhausted bound may be translated into DRAIN_EMPTY.

The caller must consume the result. Failure must be made visible through the existing diagnostic stream, with the failure category and receive count. Preserve existing protocol outcomes, exit codes and exit routes; do not claim the channel was emptied when the proof failed.

Bench v2 and build sequence

Add the receive-memory probe to the standing bench.

Run the real-C Correction-1 behaviour from its pinned source to establish bench fidelity.

Record the exact kernel identity and the accounting results.

If the invariant is demonstrated, implement the two-mode design.

If it is not demonstrated, return the evidence for a design decision rather than substituting an assumption.

Return source, diff, commit pin, probe transcripts, repeated peer tests, and production-object verification for my review.

F-1 and F-2 remain accepted. F-3 remains uncleared. Batch 4 remains gated.

I can independently review the Linux accounting semantics and the adversarial probe design while you prepare the room's results. No Crusher/provider call is required yet.

⟦ALEX-FINAL⟧

The design now has a direct candidate for the closed-peer proof. I am deliberately not declaring it valid until the target kernel demonstrates the zero-length-record accounting invariant.
