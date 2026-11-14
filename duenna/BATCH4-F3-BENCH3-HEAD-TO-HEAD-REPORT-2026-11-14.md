# F-3 Bench 3 — head-to-head evidence: STATUS pipe vs dedicated socketpair (2026-11-14)

Run in the room (Ben's laptop, kernel 6.18.58.1-microsoft-standard-WSL2) under Alex's direction in his combined design review (pb-mwgfmork): correct the two contract points, then run the prescribed matrix on both candidates under identical lifecycle and residue conditions. Corrections: BATCH4-F3-CONTRACT-CORRECTIONS-2026-11-14.md (shelved at 02fe15bd).

**Artefacts.** bench3.py sha256 baa4bd6c… · bench3_child.c sha256 e7c1ada7… · transcript bench3-transcript.txt sha256 250e9f47… (the final full run; earlier partial runs are described under Findings, not bundled). Topology = bench v2's: residue pre-queued into the child's CONTROL socket, real-C child, parent reads the candidate transport only after full child exit, 10 trials per cell, exact-record validation (code + child pid + test word).

## Results — main matrix (48 cells)

Residue shapes {empty, 1/2/3/5 zeros, ancillary ×1, ancillary ×3, data, NQ5′, mixed-data-last, trailing-zeros, queue-1500} × control-peer {open, closed} × candidate {pipe, pair}: **every cell VALID 10/10 for both candidates.** No STATUS lost, corrupted, duplicated, or hung anywhere — including queue-1500 in both peer states (no-hang, complete record, post-exit receipt). Parent descriptor count stable across the run (6 → 6): no leaked descriptors.

**The dedicated pair's escape hypothesis HELD on this evidence**: with its receive queue empty by construction, the survival law generalises — STATUS on the pair survived every residue the control channel carried. Candidate 2 is therefore NOT eliminated; it remains eligible, and the freeze decision between the two transports is Alex's on this evidence plus the contract differences (the pipe has no reverse direction at all; the pair needs the one-way rule + audit machinery below).

## Violation and failure cases (all 10/10)

- **V1 (prevention):** parent shutdown(SHUT_WR) on its status end, then deliberately attempts the forbidden send → **EPIPE at the peer in 10/10**, and STATUS still arrives exactly valid (the audit reads the EOF state as clean). Prevention works by construction.
- **V2 (audit):** prevention omitted, parent sends the forbidden packet → **VIOLATION-DETECTED 10/10**: the child withholds STATUS and exits by the violation route (44); no valid STATUS is accepted.
- **Writer failure (pipe):** reader closed before the write → **WRITEFAIL-EXPLICIT 10/10**: the child's write fails with EPIPE under SIG_IGN and it exits 45 — an explicit transport failure, never a false success.

## Finding — the audit had to learn to tell EOF from an empty packet (bench-proven, twice)

The launcher-side audit's first form read a bare `recvmsg` return of 0 as "a record was queued." Under prevention (peer write side shut), an empty queue ALSO returns 0 — it is EOF. Audit v1 false-positived 10/10 on V1. The correction is the poll mask captured BEFORE the read, with **POLLRDHUP explicitly requested** in the poll events (v2's first form forgot to request it and still false-positived — Remmy's error, caught by the same cell): RDHUP/HUP set + read 0 = EOF, clean; no RDHUP + read 0 = a live zero-length packet, violation; read > 0 = violation. With that form, V1 and V2 both pass 10/10.

**Named residual corner (not hidden):** a zero-length packet queued BEFORE the peer's shutdown is indistinguishable at the receiver from clean EOF. The contract closes it by ordering, not observation: prevention (SHUT_WR) is mandatory and is the supervisor's first act on the status end after spawn, before any other activity — so a pre-shutdown send can only come from a supervisor that violated at setup, and the supervisor-side instrumentation requirement (Alex's option 1) remains in the contract as the second net. The corner is recorded here and in the corrections note's terms for the freeze decision.

## What this evidence does and does not establish

It establishes, on the target kernel and the bench's topology: both dedicated transports deliver STATUS independently of control-channel residue across the full catalogue; the corrected violation machinery detects and prevents as specified; pipe write failure is explicit. It does NOT establish the full launcher integration (the bench child is a candidate-transport harness, not the launcher) — that proof belongs to the correction build's own suites after the design freeze. F-3 remains open; Batch 4 remains gated; the freeze decision is Alex's.
