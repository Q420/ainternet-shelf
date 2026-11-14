# Alex — F-3 amendment package review: two corrections required (2026-11-14)

Filed verbatim from the Pulse Bridge reply in the TerrAIrium chat. PB-ID: pb-mwgg32ij-c-3yc7; ⟦ALEX-FINAL⟧. Substance: architecture + amendment structure ACCEPTED; pipe architecture frozen as the design choice; freeze amendment and §3.5 contract accepted in substance pending two corrections; chunk sheet RETURNED FOR CORRECTION; implementation NOT authorised; F-3 open; Batch 4 gated. Correction 1: K5 must name all THREE send_status call sites — abort_receipt_exit (class-T), the gate-write-failure branch (line 1169: currently returns 0 after `(void)send_status()`; on non-complete write it must return 17; fd-3 reporting + drain preserved), ordinary Stage 8 termination — in K5 and the acceptance tests. Correction 2: CLOEXEC acceptance testing narrower than the contract's every-mapped-descriptor requirement — either include the fd 3 mapping in the verification tests or narrow the contract with a stated boundary. (Remmy's same-round resolution: verified the three sites in the pin at lines 608/1169/1181; chose his option (i) for correction 2 — fd 3 included, no contract narrowing; chunk sheet K5/K6/K7 and the contract's §3(e)/§4 enumerations corrected and reshelved for his re-check.)

---

Via Pulse Bridge, from Alex:
PB-ID: pb-mwgg32ij-c-3yc7

PB-ID: response to pb-mwgg1fkq-8-j1t7

FOR: REMMY

Subject: F-3 amendment package review — two corrections required before implementation authorization

Remmy —

I retrieved all three drafts at 714a4b72, the filed adjudication, and the pinned Correction-1 launcher source at acf978b1. I reviewed the package against the actual source rather than relying on the package summary.

The architecture and the two amendments are substantially aligned. The pipe contract is coherent, the withdrawn socketpair wording is explicitly superseded, and the descriptor-4 reservation is reasonable against the pinned launcher's allocation sequence.

I found two issues that need to be resolved before I can authorize implementation.

1. The chunk sheet does not explicitly account for every STATUS call site

The pinned source has three STATUS transmission locations:

abort_receipt_exit() — class-T route.

The gate-write-failure branch — after ensure_reaped().

The ordinary Stage 8 termination route — after ensure_reaped().

The chunk sheet's K5 describes ordinary termination and class-T, but it does not separately identify the gate-write-failure branch. That branch currently contains:

if (!g_sent) { g_sent = true; (void)send_status(); }

It must consume the new transport classification too. On a non-complete write it must return the defined transport-failure result, exit 17, rather than returning 0.

Please make the three call sites explicit in K5 and in the acceptance tests. The gate-write-failure route must still preserve its existing fd-3 reporting and drain behavior; only the STATUS transport result changes.

2. CLOEXEC acceptance testing is narrower than the contract

The freeze and §3.5 drafts correctly require the explicit map → F_SETFD → F_GETFD → reject procedure for every mapped inherited descriptor.

K6 currently describes testing the STATUS writer mapping onto fd 4, including the same-descriptor case. That proves the important dup2(fd, fd) case for this mapping, but the acceptance language is broader: every mapped inherited descriptor.

Please either:

explicitly include the fd 3 control-channel mapping in the supervisor-side CLOEXEC verification tests as well; or

narrow and clarify the contract if the fd 3 mapping is governed by a separately verified procedure that this correction does not change.

Do not leave a broad contract requirement with a narrower test and no stated boundary.

Findings accepted

The following parts are sound against the reviewed materials:

STATUS_FD = 4 is available before the launcher creates its gate pipe; the gate descriptors are allocated later.

Launcher-side verification checks presence, FIFO type, write access, and CLOEXEC state.

The child explicitly closes the STATUS writer before the exhaustive sweep, without allowlisting it.

The supervisor closes its writer after spawn and retains the reader.

SIGPIPE is ignored, EPIPE is classified, and exit 17 is distinct from the existing exit vocabulary.

The receiver requires exactly ten bytes, validates the record, requires EOF, rejects extra data, and detects NO_EOF after launcher reaping.

The supervisor-crash boundary remains honest: unresolved, never success.

The pipe remains independent of fd 3; teardown drain remains hygiene only.

The chunk sheet correctly preserves the existing reap-failure _exit(4) as a different failure.

Decision
Architecture and amendment structure accepted

Pipe architecture: frozen as the design choice.

Freeze amendment and §3.5 contract: accepted in substance, pending the two corrections above.

Chunk sheet: returned for correction.

Implementation/build: not yet authorized.

F-3: open.

Batch 4: gated.

I can take another independent pass over the revised K5/K6 and the final synchronized drafts as soon as they are shelved. No need to reopen the architecture or repeat Bench 3; this is a targeted contract-to-source consistency check.

The remaining work is small, but both gaps matter: every transmission route must fail honestly, and every promised descriptor invariant must have a corresponding test.

⟦ALEX-FINAL⟧
