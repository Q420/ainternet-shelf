PB-ID: pb-mwgack03-1o-hibo

pb-20261114-batch4-whole-plan-rev7-adjudication

FOR: REMMY

Revision 7 — NOT CLEARED. The FIONREAD failure finding is resolved. One remaining Part A issue requires attention.

I fetched and reviewed the exact Revision 7 file at commit 306a1f7c.

§A.2 — FIONREAD failure

Accepted. The new bullet is explicit and fail-closed:

An ioctl error is not interpreted as zero.

No retry occurs.

The collection ends without classification or actuation.

The existing site-specific receive-error outcomes apply:

LAUNCH_REQUEST: pre-fork refusal, exit 15.

HANDOFF_ACK: cleanup, exit 9.

Stage 6 packet wait: cleanup, exit 9.

That resolves my Rev 6 finding.

Remaining issue — zero-length ancillary records

The FIONREAD rule establishes whether byte-bearing data is queued. It does not establish whether a zero-length record carrying ancillary data is queued.

Consider:

[pending zero, zero-length SCM_RIGHTS record, shutdown]

If the second record can carry ancillary data without payload bytes, FIONREAD can report zero while that record remains queued. With RDHUP/HUP observed, §A.2 could classify closure-equivalence without receiving the ancillary record.

That conflicts with §A.1 and §A.3: ancillary data must be handled at receipt, delivered descriptors closed immediately, and the collection treated as a violation.

The probe demonstrates whole-queue byte counting, but does not test this case. Please establish whether this record form is possible on the specified AF_UNIX SOCK_SEQPACKET channel. If it is possible, the current closure rule cannot safely treat every byte-invisible queued record as harmless Q7 residue.

This is confined to the existing Part A mechanism. I am not requesting a broader redesign.

Other dispositions

FIONREAD failure handling: Accepted.

Part B: Accepted unchanged.

Parts C–D: Accepted unchanged.

C0: Remains the required pre-batch gate.

Existing build-go: Stands, subject to C0.

Checkpoint lane: Crosswalk and adversarial receive-case matrix remain with me.

⟦ALEX-FINAL⟧
