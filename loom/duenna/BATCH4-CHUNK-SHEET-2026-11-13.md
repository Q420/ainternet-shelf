# BATCH 4 — CHUNK SHEET (2026-11-13)

Drafted from the shelf: STAGE5-BUILD-SPEC-22 (pin afae29fb)
as amended by Revs 23–26, §3.5 (lines 4165–6041 of the
Rev 26 text) and §4 Batch 4. Each chunk is discharged by
the Batch 4 checkpoint report line by line. Batch 4 opens
under Ben's 2026-11-13 build go (Batches 2–6 in order);
Batch 3 was CLEARED by Alex 2026-11-13 (pb-mwg0ed5x).

## The pre-batch gate (before any Batch 4 build)

- **C4-0a — Launcher source.** The custody launcher is
  written against the Batch 0 behaviour-and-interface
  freeze (§3.5 point 2), from §3.5's protocol text chunk
  by chunk — never from memory.
- **C4-0b — Pin + inspection + disposition.** The source
  is pinned by sha256; Alex inspects it; the disposition
  is recorded — all BEFORE Batch 4 begins (§4 chronology,
  Rev 17). The checkpoint later pins the BUILT BINARY,
  a distinct event from the source inspection.
- **C4-0c — Custody setup evidence.** The two OS
  identities, group memberships, launcher ownership and
  mode are operator work; the setup script (or a recorded
  transcript of manual steps) is preserved as a freeze
  artefact of this batch. (The identities already exist
  in the room from the acceptance probe — their existing
  state is re-evidenced, not re-created silently.)
- **C4-0d — Environment probe.** The setuid-viability
  probe of §3.5 point 2 (effective uid 0 in the
  privileged window; nosuid and no_new_privs checked) is
  run by the operator; output preserved in the Batch 0
  freeze evidence. A failed probe stops the build.

## The build (§3.5)

- **C4-1 — Two OS identities** (§3.5 point 1): supervisor
  and harness identities, groups and boundaries as
  specified; the supervisor holds custody, the harness
  holds none.
- **C4-2 — The three processes** (§3.5 point 2):
  supervisor, launcher, harness — roles, privilege
  windows and the launcher's allowlist behaviour.
- **C4-3 — Spawn sequence + status-channel protocol**
  (§3.5 point 3): the SOCK_SEQPACKET catalogue, HANDOFF
  acks and codes 0–3, pidfd establishment with fdinfo
  target check and start-time binding, PDEATHSIG
  ordering, the namespace-reaper contract, strict
  wait_status encodings, EOF discipline, class-T/class-F
  ABORT lifecycle incl. CHILD_TERMINATED_AT_HANDOFF
  (Rev 22), the shared reaped/sent flag contract
  (sent ⇒ reaped), the eight-site reap inventory
  R-1…R-8.
- **C4-4 — Alex's five points** (§3.5 point 4): who may
  start whom, and the four companion rulings, implemented
  as specified.
- **C4-5 — Issuance** (§3.5 points 5–8): START, TERMINAL
  and CRASH issuance; the issuance record alongside the
  receipts; supervisor self-computation of issuance (no
  trusted caller values).
- **C4-6 — Commitments store**: the `commitments/`
  directory as specified — supervisor-custodied,
  harness-inaccessible, its writes following the issuance
  lifecycle.
- **C4-7 — Examiner verification hooks** (§3.5 point 9):
  every issuance and receipt verifiable by the §3.7
  examiner tooling (built in Batch 6; the data shapes
  land here).

## The checkpoint (§4 Batch 4)

- **C4-8 — SE-7 demonstrations (i), (ii), (iv)** run as
  specified in §3.5.
- **C4-9 — Launcher tests (v)–(ix)**: OS-boundary refusal
  tests executed AS the pilot-harness identity, including
  the launcher's refusal of the harness identity and of
  non-allowlist invocations.
- **C4-10 — Self-computation check**: supervisor
  self-computation verified against a falsified pin block
  in a scratch run.
- **C4-11 — Planted-receipt negative**: a planted receipt
  is rejected by a prototype anchor check.
- **C4-12 — Binary pin**: the built launcher binary's
  hash and demonstrated properties recorded; the binary's
  inspection is a distinct event from C4-0b.
- Crash cases (between-steps kill; interrupted-write)
  are NOT this checkpoint's — they run formally at gate
  G2 on the assembled package (Batch 6).

## Standing rules

- **C4-D1** — records and artefacts ride with the
  checkpoint bundle; pins by dated continuation.
- **C4-D2** — no subject call anywhere in this batch;
  the harness side runs against the stub only.
