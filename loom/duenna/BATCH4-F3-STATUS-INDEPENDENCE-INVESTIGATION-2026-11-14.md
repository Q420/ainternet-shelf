# F-3 investigation (PLAN ONLY, FINAL for review) — STATUS independent of the residue channel

Remmy's investigation under Alex's commission (pb-mwgezoaq), incorporating Alex's assigned-lane result (test design + freeze comparison, pb-mwgf7wnf) in full. Authority: Ben's negotiability addendum (b2cd64c1) — objective fixed (STATUS delivered reliably, failure never silent), mechanism and interface negotiable. **Plan only: nothing here is built, and no build is authorised by this document.** Alex reviews; the correction build, when designed, goes through its own chunk sheet.

**Pins.** Spec Rev 22 at afae29fb as amended by Revs 23–26. Freeze: launcher-interface-freeze.md sha256 6bb9ae80…, Git blob e10302c3… (Alex's retrieval). Launcher pin 3e0482c0… (bundle acf978b1); in that source, `send_status()` (lines 572–580) sends the final record via `chan_send()` on CHANNEL_FD (fd 3) — the same channel as all control traffic. Evidence: drain probe report 4ceabba6…; accounting/bench report 36551279… (bench v2 = the real-C measurement, accepted by Alex).

## 1. The measured problem

STATUS is the one message that must survive the launcher's exit, and it rides the channel whose receive queue can hold unread residue at that exit. Bench law: exit with ≥2 queued records of any kind, or any single data record, destroys STATUS for the non-concurrent reader; no receiver-side observation on kernel 6.18.58.1-microsoft-standard-WSL2 counts queued zero-length records, so no drain can prove the peer-closed queue empty. The drain research line is closed by evidence, not by preference.

## 2. Scoping fact (both lanes agree)

The Batch 0 freeze does **not** define the fd 3 STATUS protocol in detail — it freezes identity/form (§1), the operation set (§2), the gate protocol (§3), descriptor destinations for fds 0/1/2 (§4), and the exec condition (§5). The STATUS-on-fd-3 contract lives in Spec §3.5, the whole plan, and the pinned implementation. A STATUS-path change must therefore amend **both** the governing freeze (dated amendment, §6 route, permitted by Ben's addendum) **and** the §3.5/implementation contract. Changing the C source alone is not sufficient and will not be presented as such.

## 3. Q2 closed: no existing authorised path carries STATUS

Gate pipe (consumed pre-exec; kill-switch semantics). Fds 1/2 (harness-inherited — the subject could forge its own exit word). Launcher exit code (8 bits; STATUS is the full raw wait word). Fd 3 itself (the problem). A change is required; the candidates below are ordered by blast radius.

## 4. The two compared candidates (Alex's recommendation: compare, pipe leading)

### Candidate 1 — dedicated one-way STATUS pipe (LEADING, both lanes converge)

**Arrangement.** The supervisor creates a pipe alongside the control channel and retains the read end. The launcher retains the write end; the forked harness child's descriptor closure removes it before exec (freeze §3 step 8, amended to name it). After reaping the harness, the launcher writes one fixed-size STATUS record (within PIPE_BUF, atomic), closes its writer, handles the write result explicitly, and exits by its existing routes. The supervisor assembles the fixed-size record from the byte stream, validates length, then reads EOF.

**Why it escapes the evidence.** The destruction mechanism acts on the SEQPACKET socket object the exiting process leaves unread. The pipe is a different kernel object with no receive queue on the writer side at all — there is no queue state on the status path for the exit to weaponise. STATUS's survival no longer depends on any observation the kernel refuses to provide.

**Freeze/contract changes (from Alex's comparison, adopted).** §3: pipe creation + descriptor lifecycle amendment; gate ordering/semantics unchanged. §3 step 8: the STATUS writer named in the child's closure set. §4: the new descriptor's ownership/destination defined. §6: dated amendment (addendum covers the authority). §1/§2/§5: untouched. §3.5: the STATUS step moves from `chan_send()` on fd 3 to the pipe write; all other protocol traffic unchanged; exit codes and routes unchanged.

**Failure modes → contract answers.** (a) Writer inherited by the harness → EOF never observed: prevented by the amended step-8 closure, and *detected* if it happens (supervisor sees no EOF after launcher exit → explicit failure, never a pass). (b) Wrong descriptor closed / premature reader close: desk-checked at inspection + the descriptor-lifecycle bench case. (c) Hidden write failure: the launcher's exit paths consume the write result; a failed write is a recorded failure category (existing failure contract), never a silent exit — bench writer-failure cases inject exactly this. (d) Duplicate STATUS: one write site by construction; the duplicate-protection case walks every STATUS-producing exit path. (e) Framing: fixed-size record, supervisor assembles and rejects truncation/malformed length; partial-read receiver is a named bench case. (f) Supervisor failure: undetectable delivery is recorded as undelivered (EOF/no-record state), never assumed.

### Candidate 2 — dedicated SOCK_SEQPACKET STATUS socketpair (COMPARATOR)

**Arrangement.** A second socketpair, supervisor→launcher traffic: none, ever. The launcher sends STATUS as one packet on it; packet framing removes the assembly duty Candidate 1 puts on the receiver.

**Why it might escape — and why it must be probed, not assumed.** On this pair the launcher's receive queue is empty by construction (nothing is ever sent to it), so by the bench law (survival iff the exiting queue holds ≤1 zero-length record) STATUS should survive. But it remains the same socket family and the same reset mechanism in the room; the law is empirical, and the candidate's whole claim rests on it generalising to a queue that is empty rather than merely drained. The bench decides: if any catalogue case loses STATUS on the dedicated pair, the candidate is dead by evidence and Candidate 1 stands alone.

**Freeze/contract changes.** Identical shape to Candidate 1 (§3 lifecycle, step-8 closure names the status socket, §4 destination, §6 amendment, §3.5 STATUS step re-pointed).

**Failure modes.** Same lifecycle family as Candidate 1, minus byte-stream framing, plus one of its own: any future protocol addition that sends supervisor→launcher traffic on this pair silently re-enters the destruction regime — the contract must freeze the pair as one-way-by-rule, with a violation test (a stray packet on the pair fails the run's evidence).

## 5. Held in reserve (not compared in this round)

- **Candidate 4 (STATUS-ACK handshake):** no new descriptor; the launcher exits only after the supervisor's acknowledgement or peer EOF. Real cost: a wedged-but-alive supervisor needs a timeout, and any timeout reintroduces a bounded uncertainty the dedicated channels do not have. Reserve if both dedicated channels fail their benches.
- **Candidate 3 (subreaper):** the supervisor reaps the harness itself after reparenting and reads the word from the kernel — the most authoritative source, the largest lifecycle change (subtree-wide reaping obligations; commitment ordering). Alex's third option (remove the STATUS packet for a different completion mechanism) is this family. It belongs to the Batch 4 supervisor design conversation if it belongs anywhere; not a C0 correction shape.

## 6. The proof obligation (Alex's matrix, adopted entire)

Real C, bench topology, residue pre-queued, both peer states, reader delayed until after full launcher exit, exact STATUS contents including the raw wait word: empty baseline; plain zeros 1/2/3/5/1500; ancillary singles and multiples with no leaked descriptors; mixed incl. trailing zeros; reset pressure on fd 3 with fd-3 peer closed (STATUS independently readable); writer-failure injections (closed reader, invalid descriptor, write error → explicit failure, no false success); descriptor lifecycle (harness never inherits the writer); duplicate protection across all STATUS-producing exit paths; ordering (write after reap; complete record, then EOF). The 1500 case additionally proves: no launcher hang, complete record, receipt after exit. Candidate 2 runs the identical matrix plus its one-way-violation case. A candidate that fails any cell is not patched around — it is reported and the comparison decides.

## 7. Recommendation

Adopt **Candidate 1** as the design basis for the F-3 correction, with **Candidate 2** benched head-to-head on the same matrix before the design is frozen — if the socketpair matches the pipe everywhere, framing simplicity may argue for it, and the evidence, not either lane's prior, decides. The correction then proceeds as: freeze amendment + §3.5 amendment drafted and reviewed, chunk sheet, build, bench + peer suites, resubmission for F-3 clearance. The drain retires to best-effort hygiene with no proof obligation — Ben's objective (STATUS for good, failure never silent) is carried by construction instead of by observation.
