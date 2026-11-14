# The Drain Bench — built under Ben's "Do it" (2026-11-14 ~04:44 MST)

A standing test program in Ben's laptop room, replacing memory-carried probe setups. It fixes the topology in code (supervisor-role parent queues the named residue into the launcher-role child's receive queue before the fork; the child sends STATUS, performs the plugged exit behaviour, exits; the parent reads only after the child has fully exited), carries the residue shapes as a named catalogue, treats peer state (open / write-side-closed) as part of the case, sizes its own buffers, fills queues non-blocking with a deadline and reports the count actually queued, prints every case as it completes, and sanity-checks itself before measuring (empty residue + plain exit must survive 10/10 — it did).

## What the first full run establishes (10 trials per case; transcript bundled)

- **The survival law replicates exactly, in both peer states.** Plain exit: one zero-length leftover (plain or ancillary) harmless (0/10 lost); two zeros, three zeros, one data record, nq5, mixed, trailing-zeros, and the 1500 queue all fatal (10/10). Probes 3–4's law is now bench-verified, not probe-carried.
- **F3-R2 is demonstrated in both peer states.** The Correction-1 drain's 1024-record cap loses STATUS 10/10 on the 1500-record queue, consuming exactly 1024 and leaving 476 behind. The cap is fatal, not theoretical.
- **Drain-to-EAGAIN (reference behaviour):** with the peer open it is a perfect, exactly-terminating proof (consumed == queued in every case, 0 lost). With the peer closed it still saves STATUS everywhere — but only by burning its full 20000 cap on phantom zeros (consumed 20000 against queues of 0–5 records). Correct, and visibly wasteful: the closed-peer case is where a real emptiness proof is needed.

## The fidelity flag (stated plainly)

The bench's "drain-corr1" is a Python port of the Correction-1 algorithm, and in the peer-closed state the port's closure triple **never held** (it consumed the 1024 cap even on an empty queue) — so its closed-state survivals are cap-burn artefacts, NOT measurements of the C build's triple, and they do not contradict probe 4's Q-F result (the C drain's F3-R1 failure, 20/20 on trailing zeros). The port diverges from the C build somewhere in the peek/poll behaviour; the divergence is itself now a bench-visible defect to chase. **Bench v2, queued for Alex's design round: behaviours plug in as real C** (the design will be C; a port cannot judge it) — the drain functions lifted verbatim from the pinned source into a bench child, hash-tied to the pin.

## Pins
- drain_bench.py sha256 85f143f7… · drain-bench-transcript.txt sha256 fd81aff0…
- Full verdict table: the transcript, 60 cases + sanity.
