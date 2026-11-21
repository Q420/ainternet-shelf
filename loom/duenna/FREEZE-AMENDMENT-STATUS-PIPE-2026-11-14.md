# LAUNCHER INTERFACE FREEZE — AMENDMENT 2026-11-14-A (DRAFT for Alex's review)

**Amends:** launcher-interface-freeze.md (Batch 0, sha256 6bb9ae80…). **Authority:** Alex's F-3 adjudication (pb-mwgfxtg8), selecting the dedicated STATUS pipe for design freeze, under Ben's negotiability addendum (b2cd64c1) and the drain ruling's objective (STATUS delivered reliably, failure never silent). **Status: DRAFT** — Alex reviews this package before implementation; this amendment authorises nothing by itself.

## §3 (gate protocol) — additions

1. **STATUS descriptor establishment.** Before the gate pipe is created, the launcher holds a dedicated STATUS pipe write end on the reserved descriptor **STATUS_FD = 4** (see §4 addition). It arrives by supervisor handoff across the exec (procedure in the §3.5 amendment, which is part of this amendment's contract): the supervisor creates the pipe, maps the writer onto descriptor 4, explicitly clears FD_CLOEXEC (F_SETFD), reads the flags back (F_GETFD), and rejects the launch if the verified state is not the expected state — for this and for EVERY mapped inherited descriptor, without relying on dup2 semantics in either direction of the same-descriptor case.
2. **Launcher verification (precondition block).** At the existing descriptor-precondition point (the checks that exit 13), the launcher additionally verifies STATUS_FD: present; `fstat` reports S_ISFIFO; `F_GETFL` access mode is write-only or read-write (open for writing); `F_GETFD` shows FD_CLOEXEC clear. Any defect exits 13 with the attempt unstarted. Descriptor inspection establishes these properties only; the peer relationship is established by the controlled creation-and-handoff procedure, and no clause claims otherwise.
3. **SIGPIPE.** The launcher's startup disposition of SIGPIPE to SIG_IGN (present in the pin) is a freeze requirement, verified in force at the STATUS write. Pipe writes therefore return EPIPE as a value, never a signal death.
4. **Child lifecycle.** In the forked harness child, the STATUS writer is closed by explicit named close at the same point where the child closes the channel (the pin's line-857 position), BEFORE the exhaustive descriptor sweep. It is never added to the child's descriptor allowlist. The sweep's verification then proves its absence.

## §4 (descriptor destinations) — addition

- **STATUS_FD = 4:** a pipe write end. Owner of the object: the supervisor creates the pipe pre-spawn and retains the read end; exactly one write end exists — the supervisor's transient pre-spawn copy is closed immediately after successful spawn (its post-spawn descriptor self-audit, recorded in the run log, shows no writer), the launcher's copy is its sole holder for the attempt's life, and the harness never holds it (§3.4 above). Destination verification before launch follows the same resolve-and-assert discipline as fds 0–2: the supervisor asserts the read end it retains is the peer of the writer it placed (identity by controlled creation, recorded as such — not by target-form matching).
- No other §4 destination changes. Fds 0/1/2 and the fd 3 control channel are unchanged; the fd 3 protocol is byte-identical.

## §6 (effect) — amendment record

This amendment is the dated amendment the freeze's §6 route contemplates. It changes the frozen interface in exactly the respects above and no others. The governing STATUS transport contract is the §3.5 amendment issued with it (STATUS-PIPE-CONTRACT, same date); the two documents are synchronized and move together — a divergence between them is a defect in the package, not a builder's choice.
