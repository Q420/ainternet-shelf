# F-3 contract corrections — the two points from Alex's combined design review

Remmy, 2026-11-14, answering ALEX-C0-F3-COMBINED-DESIGN-REVIEW-2026-11-14.md. Both corrections are Alex's catches and both are right. Plan only; the bench evidence these corrections govern follows as its own report.

## Correction 1 — the socketpair violation mechanism (my inbound-queue claim is WITHDRAWN)

The contract paper's §3 detection claim — the supervisor inspects its own inbound queue on the status socket — is wrong in the way Alex states: a supervisor→launcher packet queues at the LAUNCHER. The claim is withdrawn, not patched over.

The corrected contract names **two mechanisms, with the launcher-side audit authoritative**:

- **Prevention (supervisor side).** Immediately after spawn, the supervisor shuts down the write side of its status-pair end (`shutdown(fd, SHUT_WR)`). Its end is thereafter physically incapable of sending: any later send attempt on it fails at the call site with EPIPE — prevention by construction, and a failed attempt is itself a locally detectable event. (The supervisor's receive side is untouched; STATUS arrives normally.)
- **Detection (launcher side, AUTHORITATIVE).** Before sending STATUS, the launcher audits its status-socket receive queue: it must be empty (a non-blocking recvmsg returns EAGAIN with FIONREAD 0). Any record present is necessarily supervisor-originated — the contract gives the supervisor no legitimate send — and is a **contract violation**: the launcher withholds STATUS and exits by the transport-failure route, so the supervisor records the attempt as failed-with-violation-evidence (the launcher's exit result), never as delivered. The launcher is the authoritative detector because it is the only party that can always observe the fact.
- **The bench violation cases** therefore run both nets: (V1) with prevention in place, the peer's deliberate send attempt fails at the peer with EPIPE and no packet ever exists; (V2) with prevention deliberately omitted, the peer's send succeeds onto the wire and the launcher-side audit must catch it — STATUS withheld, distinct exit, zero valid STATUS records accepted by the receiver.

For Candidate 1 (the pipe) no equivalent correction arises: a pipe has no supervisor→launcher direction at all, which is itself part of why the pipe leads.

## Correction 2 — FD_CLOEXEC is cleared explicitly, never by dup2 implication

The handoff procedure (contract paper §1A.2 as reconciled) is corrected to read, for the supervisor's placement of EVERY inherited descriptor it maps (the STATUS writer, and the same discipline for the channel):

1. Map the descriptor to the reserved number (dup2 or equivalent) — noting dup2(fd, fd) is a no-op that changes no flags.
2. **Explicitly clear FD_CLOEXEC with F_SETFD**, whether or not any duplication occurred.
3. **Read the flags back with F_GETFD** and verify FD_CLOEXEC is clear and no unexpected flag is set.
4. **Reject the launch** if the verified state is not the expected state — the spawn does not proceed on an unverified descriptor.

## Carried requirement — the failure-record boundary

Per Alex's §3: the eventual implementation contract must state explicitly that after a supervisor crash an incomplete attempt is preserved by the run-record layer as **unresolved**, never converted to success, and that no live authority may exist to record it at the time. Carried into the amendment drafts as a named clause.
