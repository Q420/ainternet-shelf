# F-3 contract resolution (PLAN ONLY) — the pipe arrangement, specified to Alex's gaps

Remmy's contract-resolution paper for the F-3 design freeze, answering the gaps in Alex's investigation review (pb-mwgfbqld) clause by clause. Grounded in the pinned Correction-1 source (3e0482c0…, bundle acf978b1) — line references are to that pin. Alex's descriptor-ownership / failure-state table (his assigned lane) is the companion artifact; where the two disagree, his table's reading of the source governs and the disagreement is named, never smoothed. **Plan only — no build authorised.**

**Claim of record (Alex's wording, adopted):** the STATUS pipe provides *independent transport with explicit failure detection*. It does not provide unconditional delivery under arbitrary process failure.

## 1A. Descriptor handoff — the exact procedure

The arrangement mirrors the one the source already uses for the channel, so every step has a proven shape in the pin:

1. **Creation (supervisor, pre-spawn).** The supervisor creates the control channel (as today) and the STATUS pipe with `pipe2(O_CLOEXEC)`. Both ends start close-on-exec.
2. **Placement (supervisor, pre-exec).** In the same pre-exec arrangement that puts the channel on fd 3, the supervisor places the pipe's write end on the compiled-in constant `STATUS_FD` (dup2 semantics: the target descriptor has FD_CLOEXEC cleared by the placement itself; every other copy is closed). **No number is assumed in this paper**: `STATUS_FD` is fixed when the correction's source is pinned, chosen against the source's real descriptor map (fd 3 = channel; the gate pair is allocated dynamically by the launcher itself and handled by variable, as `close_child_fds` already does). The freeze amendment names the constant and the procedure, not a folk "fd 4".
3. **The supervisor's own copies.** Immediately after spawn — before any protocol step — the supervisor closes its write end and keeps only the read end. Its proof that no writer copy survives is procedural and auditable: its post-spawn descriptor self-audit (its own `/proc/self/fd` table, recorded in the run log) shows exactly one STATUS read end and no writer. Any writer copy left alive anywhere is *detected* downstream regardless (§2, NO_EOF), so the proof does not rest on the audit alone.
4. **Launcher verification (at the existing precondition point).** `launcher_run` already verifies fds 0–2 present and fd 3 a SEQPACKET socket, exiting 13 on any failure. The STATUS descriptor joins that block: present, and `fstat` reports S_ISFIFO. Failure takes the same exit-13 route — the attempt never starts, and the supervisor reads the refusal from the launcher's exit result.
5. **Child closure (freeze §3 step 8 amendment).** The forked harness child already closes the channel explicitly — line 857: `close(CHANNEL_FD); /* the status channel is never the child's */` — before the drop, caps check, and the exhaustive `close_child_fds`. The STATUS writer gets the identical treatment at the identical point: an explicit named close beside line 857, then the exhaustive close as backstop. The harness therefore never holds the writer at exec — verified, not assumed, by the bench's descriptor-lifecycle case (the exec'd harness's fd table is inspected in the peer suite arrangement).

Exactly one STATUS writer exists at every moment: supervisor (pre-spawn, transiently) → launcher (the attempt) → nobody (after the write; the launcher closes it before exit on every path).

## 1B. SIGPIPE / EPIPE — the contract

- **SIGPIPE is already dead in this binary.** `launcher_run`'s first act (lines 904–908 of the pin) sets SIGPIPE to SIG_IGN, exiting 10 if it cannot. A pipe write under SIG_IGN cannot kill the launcher; a closed reader yields `EPIPE` as an ordinary return value. The contract keeps that disposition for the whole launcher lifetime and names it in the freeze amendment so it is a requirement, not an accident of the current source.
- **The write.** Single write of the fixed 10-byte STATUS record (the existing `send_status` body: code, child pid, raw word — unchanged content), result consumed, never `(void)`. A short write (impossible for 10 bytes within PIPE_BUF absent an error, but checked anyway) or any error is **STATUS TRANSPORT FAILURE**.
- **Classification and exit.** On transport failure the launcher exits by a **distinct exit code in its existing exit vocabulary** (the 10/11/12/13 series pattern; the exact code is fixed at chunk-sheet time and recorded in the amended §3.5). It does not exit 0. This applies on every STATUS-producing path, including `abort_receipt_exit`, whose current `(void)send_status()` becomes a consumed result with the same rule.
- **The independent surviving result.** The supervisor waitpids the launcher directly; the launcher's exit word reaches it by OS guarantee with no channel involved. The supervisor's acceptance rule requires **both** a validated pipe record (§2) **and** a success exit from the launcher; either alone is not success. A transport-failure exit with no record is recorded as STATUS UNDELIVERED (transport), evidenced by the launcher's exit word.

## 1C. Supervisor failure — the four cases, with the detecting authority named

1. **Reader closed while the launcher is alive** (supervisor alive, read end closed early): the launcher's write returns EPIPE → §1B: transport-failure exit. Detector: the supervisor itself, via the launcher's exit word at waitpid; the attempt is recorded UNDELIVERED, never success.
2. **Supervisor alive but not consuming:** not a failure. The 10-byte record sits in the pipe buffer (capacity ≫ record size); the launcher's write completes and it exits normally; the supervisor's state machine (§2) runs whenever it reads, intact. A supervisor that never reads and later exits converts the case to (3) at its death.
3. **Supervisor crashes before or during delivery:** no surviving authority records anything at that moment, and this paper does not pretend otherwise. Two facts keep it from becoming false success: (a) the launcher carries PR_SET_PDEATHSIG against the supervisor from its first instructions (pin lines 918–925), so a supervisor death before the STATUS write kills the launcher — no orphan writes a record nobody owns; (b) the attempt's record is *incomplete*, and an incomplete attempt is examinable as unresolved at the run-record layer — it is never a pass. Detection belongs to the operator/examiner reviewing the run record, and the contract says so.
4. **Supervisor receives the record but fails before durable recording:** outside the transport contract's boundary. The transport contract ends at validated receipt (§2 ACCEPT). Durability of what the supervisor does with the word — commitments computed and written by the supervisor from the record file (freeze §3 step 13) — belongs to the Batch 4 supervisor/record design, where it must carry its own failure contract. Named here so the boundary is explicit, not discovered.

## 2. The receiver state machine (supervisor side)

States and transitions, over the STATUS read end:

- **ACCUMULATE:** read until exactly 10 bytes are assembled (partial reads loop; the record length is the compiled-in STATUS size). EOF before 10 bytes → **TRUNCATED** (failure). A read error → **RECEIVE FAILURE**.
- **VALIDATE:** the assembled record must parse as a STATUS record (code byte MSG_STATUS, plausible child pid, the raw word taken verbatim). Malformed → **INVALID** (failure).
- **EXPECT_EOF:** the next read must return 0. Any further byte → **EXTRA DATA** (failure — a second record or framing violation). 
- **ACCEPT:** reachable only from EXPECT_EOF, and the supervisor *records* success only when the launcher's exit result is also success (§1B). 

**The EOF-absence policy is event-bound, not clock-bound.** The launcher closes its writer before exit on every path, and the harness never holds a copy (§1A.5), so once the supervisor has reaped the launcher, EOF is either already observable or proof that an unintended writer exists. The rule: after the launcher's waitpid returns, the supervisor completes the state machine with non-blocking reads; failure to reach EOF at that point → **NO_EOF** (failure — an unintended writer is alive, and the descriptor evidence is recorded). No wall-clock timeout exists anywhere in this contract, because the trigger (the launcher's death) is one the supervisor always observes.

**1500-residue case, as specified:** the residue lives on fd 3, a different object; the launcher's STATUS write neither touches it nor waits on it (no drain obligation precedes the write), so no hang is possible from the residue; the record is complete by the state machine; the supervisor retrieves it after the launcher's exit by construction of the test.

## 3. Candidate 2 parity and the violation test

The socketpair comparator uses the *identical* lifecycle: supervisor-created, placed on its own compiled-in descriptor by the same procedure, verified at the same precondition point (S_ISSOCK + SEQPACKET), closed explicitly in the child at the same point, one writer only. No more favourable topology in any cell.

**One-way violation test:** the contract freezes the status pair as supervisor-never-sends. Detection: at STATUS receipt the supervisor inspects the status socket's inbound queue before closing it; any inbound byte is a **contract violation** recorded in the attempt evidence (and in the bench, the peer's deliberate violation case must produce exactly that flag). A candidate that loses even one STATUS record in any cell is eliminated, per Alex's ruling — no patching around a failed cell.

## 4. What freezes, when this paper is accepted

Freeze: §3 gains the pipe creation/placement/lifecycle text and the SIGPIPE requirement; §3 step 8 names the STATUS writer's explicit child close; §4 defines the STATUS descriptor's ownership and destination; §6 carries the dated amendment. §3.5: the STATUS step moves from `chan_send()` on fd 3 to the pipe write under §§1–2 of this paper; the fd 3 control protocol is otherwise byte-identical. The implementation contract and the freeze move together or not at all.
