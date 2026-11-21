# Probe report — the drain's emptiness problem, measured (2026-11-14)

For Alex's F-3 correction design (Ben's ruling 2026-11-14 ~04:30 MST: Alex designs, Remmy builds and probe-verifies, Alex reviews). All results in-room, AF_UNIX SOCK_SEQPACKET, stub peers only. Scripts and transcripts bundle with this report.

## What was probed, and one error owned

**Probe 2** (probe_drain2.py) tested whether `shutdown(SHUT_RD)` purges the receive queue, plus STATUS-survival variants. Its Part 1 is valid; **its Parts 2–3 are INVALID and are not evidence**: the residue was queued in the wrong direction (sent by the exiting process itself, so its own receive queue was empty at exit and STATUS survived vacuously, 0/20 everywhere). Its first run also deadlocked on the 1500-record part (send buffer) and was killed; the re-run's Parts 2–3 carry the direction error. Part 1 stands.

**Probes 3 and 4** (probe_drain3.py, probe_drain4.py) re-ran the survival question with the residue in the correct direction — sent by the supervisor-role parent into the exiting child-role process's receive queue; the child sends STATUS, acts, exits; the parent waits for full exit, then reads (the F-3 non-concurrent shape).

## Results

**Purge is disproven.** After `shutdown(SHUT_RD)` with [data, Z, Z, Z, Z+rights] queued: the data record was still receivable (`HELLO` returned), and the queued descriptor was NOT closed by the kernel (a write to the held pipe write-end succeeded — a read end still existed). Send direction unaffected. Probe 3's purge variant on the mixed residue: STATUS lost 20/20, identical to plain exit. `shutdown(SHUT_RD)` does not discard this channel's receive queue on this kernel. Any drain design must consume records by receiving them.

**The survival law (plain exit, residue in the exiting process's queue):**

| Residue at exit | STATUS lost |
|---|---|
| 1 plain zero | 0/20 |
| 1 ancillary zero | 0/20 |
| 2 plain zeros | 20/20 |
| 3 plain zeros | 20/20 |
| 1500 plain zeros | 10/10 |
| 1 data record (3 bytes) | 20/20 |
| mixed: 3 zeros + ancillary zero + data | 20/20 |

STATUS survives iff the exiting queue holds **at most one record, and that record is zero-length**. Any data record alone, or any two records, destroy it. (Mechanism internals not resolved; the empirical law is consistent across nine configurations.)

**F3-R1 is demonstrated objectively, not just in the source.** Residue [ancillary zero, data, Z, Z, Z] (byte-bearing records first, three plain zeros trailing): the Correction-1 drain lost STATUS **20/20** — it consumes the ancillary and data records, reaches the first trailing zero, the closure triple (FIONREAD 0, RDHUP, head-peek clean) reports empty, it stops with two zeros queued, and the survival law does the rest. On the earlier mixed residue (data record LAST) the same drain scored 0/20: it passes only when a byte-bearing record happens to come last.

## Terrain for the design

1. **Peer still open:** a non-blocking receive returning EAGAIN is a definitive proof the queue holds no records — real zeros are always returned before EAGAIN. Drain-to-EAGAIN is a complete proof in this case.
2. **Peer closed (the NQ5' case):** receives return 0 perpetually; a real zero and the phantom EOF zero are indistinguishable per receive (Q7). FIONREAD counts bytes only; the head-peek sees ancillary only at the head. No single observation counts records.
3. **A computable bound exists in principle:** once RDHUP is observed the queue is frozen (the peer can send nothing more). The number of records it can hold is bounded by the socket's receive-buffer charge — each record's skb charges a minimum truesize, and the channel socket's SO_RCVBUF is readable (and, at Batch 4 setup time, settable by the system itself). A drain that, after the last non-zero record, consumes (buffer-derived maximum record count + 1) further zeros has provably consumed every real zero; the remainder are phantoms. The per-record minimum charge on this kernel is measurable by probe (fill until send blocks, count). Whether this invariant is the design's proof — and how bound-exhaustion and observation failure are reported rather than silenced (F3-R3) — is the design question.
4. The drain's obligation is unchanged and now sharper: consume **every** record — zeros included (two leftover zeros are exactly as fatal as a leftover data record) — close every received descriptor on sight, classify nothing, change no outcome or exit route, stay bounded.

## Pins
- probe_drain2.py sha256 066c16f4… · transcript 0e18190b… (Part 1 only)
- probe_drain3.py sha256 b6224bfe… · transcript 23fa7848…
- probe_drain4.py sha256 e180656b… · transcript d8f7a30e…
