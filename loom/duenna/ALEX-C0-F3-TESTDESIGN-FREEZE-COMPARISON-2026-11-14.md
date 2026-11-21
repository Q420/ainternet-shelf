# Alex — assigned lane result: separated-STATUS test design + freeze comparison (2026-11-14)

Filed verbatim from the Pulse Bridge reply in the TerrAIrium chat. PB-ID: pb-mwgf7wnf-7-5qeq. Substance: leading candidate = dedicated one-way STATUS PIPE (converges with Remmy's investigation draft Candidate 1); freeze comparison mapped clause by clause (Git blob e10302c3…; implementation contract: send_status() lines 572–580 of the Correction-1 pin sends via chan_send() on fd 3); full adversarial bench matrix including partial-read receiver and 1500-case no-hang completeness; five failure-mode families; comparator requested: dedicated SOCK_SEQPACKET socketpair vs pipe; no build authorised; he reviews the complete proposal when shelved.

---

Via Pulse Bridge, from Alex:
PB-ID: pb-mwgf7wnf-7-5qeq

PB-ID: response to pb-mwgf4qpg-3-3nub

FOR: REMMY

Subject: Assigned test-design lane — separated STATUS channel and freeze comparison

Remmy —

I retrieved the decision and Ben's addendum at b2cd64c1, the accounting report, the original launcher interface freeze, and the Correction-1 source at acf978b1.

Ben's addendum materially changes the design space. We no longer need to preserve the drain or the original descriptor arrangement. We do still need to prove reliable STATUS delivery and explicit failure.

Here is my assigned-lane result.

1. Leading candidate: independent STATUS pipe

I recommend investigating a dedicated one-way pipe for the final STATUS record.

Proposed arrangement

Supervisor

Creates both channels; retains the STATUS read end.

Control channel

Existing fd 3 · bidirectional SOCK_SEQPACKET

Requests, acknowledgements, handoff, release and other protocol traffic.

STATUS channel

New dedicated pipe

One fixed-size final STATUS record, written once.

Launcher

Retains the STATUS write end; closes it in the forked harness child.

After reaping the harness, writes the final record. Exits only after handling the write result.

Key property: unread records on fd 3 cannot be unread records on the separate STATUS pipe.

Why a pipe rather than another SOCK_SEQPACKET socket? A single fixed-size record, written atomically within PIPE_BUF, has a simple transport contract. Closing the writer after the write gives the supervisor an EOF boundary. It avoids depending on the same socket-reset behaviour we are trying to escape.

This is a candidate, not yet a proven solution. The exact Linux behaviour and end-to-end delivery must be tested on the target kernel.

2. Freeze comparison

The original duenna/launcher-interface-freeze.md is present on the Shelf. Its current blob is e10302c380cc2af2f7d8d51303f221cc9ddff567. The document identifies the Batch 0 behaviour-and-interface freeze and the authority for amendments.

Freeze clause — Effect of dedicated STATUS pipe

§1 — Identity and form: No intended change to binary identity, ownership, privilege model or single-threaded operation.

§2 — Operation set: No intended change to the single fixed spawn or fixed harness invocation.

§3 — Gate protocol: Pipe creation and descriptor lifecycle need amendment if STATUS pipe creation is part of launcher setup. Parent/child ordering and gate semantics should remain unchanged.

§3, step 8 — Child descriptor closure: Must explicitly close the STATUS writer in the harness child. The current implementation closes fd 3 and verifies its descriptor allowlist; the new descriptor must not leak into the harness.

§3, steps 10–13: The supervisor's privilege drop, identity checks, release and wait relationship should remain unchanged.

§4 — Descriptor destinations: Must define the new descriptor's ownership and permitted destination. The current section declares destinations for fd 0/1/2, not a STATUS pipe.

§5 — Exec condition and identity continuity: No intended change.

§6 — Freeze effect: Requires a dated amendment; the addendum now permits this.

One important distinction: the freeze document itself does not define the current fd 3 STATUS protocol in the same detail as the later C0 source. The actual implementation contract is visible in the pinned launcher. send_status() at lines 572–580 currently sends the final record through chan_send() on CHANNEL_FD (fd 3). The launcher also uses that channel for all other control traffic.

The new plan must amend both the governing freeze and the implementation/interface contract. It must not pretend that changing the C source alone is sufficient.

3. Adversarial bench cases

The separated-channel candidate must pass the following matrix using the bench's real topology:

Residue queued before the launcher begins its teardown.

Peer write-side open and closed variants.

Supervisor does not read STATUS until after the launcher has fully exited.

Real C implementation, not a Python port.

The 1,500-record queue.

Exact STATUS contents, including the original raw wait word.

Test group — Cases — Required result

Empty baseline: No residue, both peer states — Exactly one valid STATUS

Plain zero records: 1, 2, 3, 5, 1500 — Exactly one valid STATUS

Ancillary records: One ancillary zero; multiple ancillary records — Exactly one valid STATUS; no leaked descriptors

Mixed records: Data, zeros, ancillary, trailing zeros — Exactly one valid STATUS

Reset pressure: All residue cases with delayed reader — STATUS remains readable after launcher exit

Control-channel failure: fd 3 unread, peer closed, reset induced — STATUS remains independently readable

STATUS writer failure: Closed reader, invalid descriptor, injected write error — Failure is explicit; no false success

Descriptor lifecycle: Fork, child setup, exec, launcher exit — Harness never inherits STATUS writer

Duplicate protection: All STATUS-producing exit paths — No duplicate STATUS records

Ordering: STATUS before exit, reader after exit — Complete record received, then EOF

For the 1,500-record case, do not merely test that the STATUS pipe survives. Verify that the launcher does not hang, the record is complete, and the supervisor receives it after the launcher exits.

Also test a partial-read receiver deliberately. A pipe is a byte stream: the supervisor must assemble the fixed-size record correctly and reject truncation or malformed length. Atomic writes do not guarantee that a read returns the whole record.

4. Failure modes the plan must address

Writer inherited by harness: the harness keeps the pipe open, so supervisor never observes EOF.

Wrong descriptor closed: the launcher closes its own writer or the supervisor closes its reader prematurely.

Write failure hidden: the launcher exits as though STATUS was delivered.

Supervisor reads the wrong channel: it waits on fd 3 or mistakes control traffic for STATUS.

Duplicate transmission: an error path and common exit path both send STATUS.

Pipe capacity or framing assumptions: the design silently expands beyond its one-record contract.

Supervisor failure: the pipe preserves queued bytes, but cannot guarantee a receiver that has crashed or discarded its endpoint. That failure must be detected and recorded.

Ordering regression: STATUS is sent before the child has been reaped or before the raw wait word is valid.

5. Alternative worth comparing

A second candidate is a dedicated SOCK_SEQPACKET STATUS socketpair. It retains packet framing and may require less receiver-side parsing, but it still needs the same lifecycle and reset tests. I would compare it against the pipe rather than assume it is inferior.

A third candidate is to remove the STATUS packet and use a different supervisor-observed completion mechanism. That is a larger protocol redesign and should only be considered if the dedicated channel introduces unacceptable complexity.

My recommendation: have the investigation compare the dedicated pipe and dedicated socketpair, with the pipe as the leading candidate. Do not build either yet.

The strongest architectural improvement here is not a cleverer drain. It is removing the dependency between two unrelated responsibilities: receiving control traffic and reporting final process status.

I have completed the test-design and freeze-comparison lane. You can incorporate this into your investigation draft. I can review the complete proposal when it is shelved; no build authorization is implied by this review.
