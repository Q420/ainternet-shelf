# BATCH 4 CHECKPOINT REPORT — 2026-11-14

Submitted to Alex for adjudication under whole-plan Rev 8
Part D and the completion plan (Block 1, Rule 4). One
bundle, discharging chunk sheet Rev 2 C4-8…C4-12, whole-plan
Part B read-back, and the Batch 5 chunk sheet approval —
mapped row by row against Alex's checkpoint crosswalk
(pb-mwgko4we-j-ecfn). Underlying output rides with the
bundle throughout; this report is the map, not the evidence.

Authorities: spec Rev 26 §3.5 (sha256 1126bcf0…), chunk
sheet Rev 2, whole-plan Rev 8 (fba0a629…), completion plan
(8f431838…), Alex drift check (9daf748a), Alex crosswalk
(1ebbc01d). Environment: Ben's laptop, WSL2 Ubuntu 26.04.1,
kernel 6.18.58.1-microsoft-standard-WSL2. No subject call
anywhere in the batch (C4-D2): the harness entry is the
stub throughout.

## What was built (C4-1…C4-7)

- **C4-1** identities re-read, not recreated: pilot-supervisor
  uid 999/gid 986, pilot-harness uid 997/gid 985, singleton
  groups, no cross-membership (rig output, (vii) section).
- **C4-2/C2** supervisor programme `pilot_supervisor.py`
  (sha256 c8a11370…): §3.5 points 2–9 — Stage 1 standing
  verifications (stdio destinations, exec-condition +
  identity records, commitments custody, no writable
  commitments fd), fd-3 SEQPACKET channel + fd-4 STATUS
  pipe with the contract placement procedure (map →
  F_SETFD clear → F_GETFD read-back) and writer self-audit,
  LAUNCH_REQUEST, pidfd handoff validation (fdinfo target,
  /proc stat start-time + parent binding, readiness
  contract), HANDOFF_ACK 0–3, GATE_READY → Part B
  observation → pre-RELEASE readiness guard → RELEASE,
  class-T/class-F ABORT handling, STATUS-pipe receiver
  (post-reap classification ACCEPT/TRUNCATED/EXTRA/INVALID/
  NONE/NO_EOF), strict wait_status validation, closure on
  the {valid STATUS + pidfd termination} pair, STATUS_ACK
  outcome recorded separately, self-computed START /
  TERMINAL / CRASH issuance + frozen-schema issuance
  record. ABORT reason numbering cross-checked identical
  against launcher-c3.c (7/7, `check_abort_reasons.py`).
- **C4-3/C3** harness entry at the compiled-in path
  `/srv/nemotron-pilot/harness/pilot-harness` (stub; Batch 3
  record writer ed3f5c85…, JCS 8a131cfc…).
- **C4-4/C4** production launcher installed
  root:pilot-supervisor 4710 with dated C4-0c evidence
  (v1 + V2 artefacts in bundle).
- Part B launch-evidence records: written per attempt at
  GATE_READY (separate record family, §B.2 fields), see
  the read-back row below.

## Crosswalk rows

### C4-8 — SE-7 demonstrations (i), (ii), (iv)

- **(i) Harness cannot write/replace/delete receipts.**
  Inside the boundary: run B4VAULT-20261114-002 — the stub,
  mid-run as pilot-harness, attempted create / overwrite /
  delete against the *existing* receipt
  `B4SMOKE-20261114-001.start.json` and append to
  `issuance-record.jsonl`: all four **EACCES** at the OS
  boundary (`artefacts/vault-attempts.json`). Shell level:
  the same four attempts plus read, as pilot-harness —
  all Permission denied; receipt + issuance hashes
  identical before/after (`rig-refusals-output.txt`).
  By inspection: the stub contains no commitments write
  path (it never opens the commitments tree for writing;
  the B4VAULT variant is the only commitments code and it
  exists to make the attempts).
- **(ii) Supervisor independently records START, TERMINAL,
  CRASH.** By inspection of the supervisor source: every
  committed value is computed from the supervisor's own
  parse of the record file; no issuance path accepts a
  hash, count or event value from the harness (the harness
  has no channel to the supervisor except the record file
  itself). By test: production runs B4SMOKE-20261114-001
  (START+TERMINAL), B4CRASH-20261114-101 (START+CRASH,
  word 9, partial file as it lies, event_count = complete
  events only), and the falsified-pin run under C4-10.
  Independent recomputation: `verify_start.py` exits 0 on
  the smoke and falsified runs (bundle outputs).
- **(iv) Examiner verifies the issuance record.** The
  prototype anchor check (`anchor_check.py`, §3.5 point 9
  step-0 shape; §3.7 tooling itself is Batch 6) accepts
  genuine receipts and rejects the planted one — C4-11.

### C4-9 — Launcher tests (v)–(ix), as pilot-harness

Executed as the pilot-harness identity wherever the case
is an invocation or an attempt from inside the boundary;
each record names its executing identity (`rig-refusals-output.txt`,
session records, artefacts):

- **(v) Launcher separation.** As pilot-harness:
  `/srv/nemotron-pilot/launcher <run-id>` → Permission
  denied (mode 4710, group pilot-supervisor). As
  pilot-supervisor with non-allowlist argument shapes
  (no arg, extra arg, malformed run-id, bad date): all
  exit 12, nothing spawned. Mid-run: B4INVOKE-20261114-001
  — the harness attempted to exec the launcher during its
  own run → **EACCES** recorded in
  `artefacts/invoke-attempt.json`; the run's own evidence
  shows the attempt changed nothing (normal S9 closure,
  chain intact).
- **(vi) Descriptor isolation.** B4FDS-20261114-003:
  enumeration before any own file is opened — retained
  inherited set is exactly fd 0 (/dev/null, read-only),
  fd 1/2 (the run's stdio log, write-only, append) — the
  declared destinations; write probes on fds 3–16 all
  EBADF (`artefacts/B4FDS-20261114-003.fds.json`).
  Hazard arrangement (B4FDS-20261114-004): a writable
  descriptor to a scratch commitments-like file was held
  open (fd 5, O_WRONLY|O_APPEND) by the supervisor process
  itself across the launch fork (arrangement record in
  bundle); the harness shows no trace of it (probes
  EBADF) and the scratch file's sha256 is unchanged.
  Negative arrangement (B4NEG-20261114-001): supervisor
  stdout pointed at a scratch protected file → Stage 1
  refusal recorded with the offending descriptors
  (fd1_append_log/fd2_same_log false), no harness process
  existed, file byte-unchanged.
  *Rig iterations, stated plainly:* B4FDS-20261114-001's
  variant crashed on a /proc/self/fd enumeration race
  (its CRASH receipt stands); -002's probe wrote one byte
  into the stub's *own* record descriptor — chain
  verification of the fetched -002 record fails to parse,
  which is how the flaw was caught; -003's enumeration
  runs before any own file is opened and is the cited
  record. The flaw was in the rig variant, not in the
  launcher or supervisor; the supervisor committed each
  file exactly as it lay, as designed.
- **(vii) Group separation + setuid preconditions +
  capability state.** OS evidence: `id` for both
  identities and /etc/group show singleton groups with no
  cross-membership; mount options carry no `nosuid`;
  NoNewPrivs 0 for a pilot-supervisor shell; kernel
  string recorded (`rig-refusals-output.txt`). The
  privileged window itself is proven by every production
  run: children land as pilot-harness and the Part B
  launch-evidence records show all six capability masks
  (launcher + child × CapEff/CapPrm/CapAmb) at zero.
  Fail-closed nonzero-observation case: on the
  supervisor's side this is the Part B failure path
  (observation unavailable/malformed/nonzero → RELEASE
  withheld, ABORT reason 7, failed observation preserved
  with comparison FAIL) — present in the built code and
  inspected; a live nonzero mask cannot be induced on a
  genuinely dropped process without the launcher test
  hook, so per the spec's own provision the child-side
  and parent-side *launcher* read-back cases rest on the
  C0 evidence against this same source pin (hooks
  injection fail-closed cases, Correction arc) plus
  code-order inspection of launcher-c3.c. The bundle
  states this route explicitly rather than claiming a
  live induction that did not happen.
- **(viii) Launch handshake.** The supervisor-side
  fail-closed paths were exercised live against the
  production binary through the D-T demonstrations
  (below): establishment death (ACK 3), settling death
  (class-T), gate-window death, launcher death. The
  launcher-internal failure windows (Window 1/Window 2
  setres* fault injection, parent-death variants) are
  test-build hook cases discharged in the C0 arc against
  this source pin (peer suite: kill-window, forced
  close_range failure, PDEATHSIG cases) and are cited,
  not re-run; the production binary contains no hooks.
- **(ix) Executable identity continuity.** Scratch tree
  (`rig-ix-output.txt`, ix session records):
  (b) *redirection first* — symlink repointed after the
  freeze → Stage 1 refusal; freeze record (genuine ino
  31863) and observed record (substitute ino 31866) both
  in the session record; substitute never executed.
  (c) component audit — production tree clean
  (`audit_path_components.py` all_ok); defective scratch
  tree (group-writable pilot-harness-owned component)
  flagged with owner + mode.
  (a) *substitution last* — genuine object replaced by a
  setuid copy (stat confirms mode 4755) → Stage 1 refusal
  recorded with both records: freeze (ino 31863, mode
  0755) vs observed raw (mode 2541, setuid true).

### C4-10 — Supervisor self-computation (falsified pin)

Scratch run B4FALSE-20261114-001 (scratch evidence set)
and production run B4FALSE-20261114-101: the RUN_STARTED
pin block carries a falsified pin (sha256 `ffff…`). The
START receipt commits the falsified block's actual bytes
— genesis == pinned_input_block_sha256 == the record's
own prev_event_sha256 (9146425d… scratch) — and
`verify_start.py` independently recomputes every receipt
value from the record file: exit 0, all checks true.
The discrepancy is a replay finding, exactly as designed;
no launcher-side check is substituted.

### C4-11 — Planted-receipt negative

Prototype anchor check against a scratch commitments tree
(`rig-c4-11-output.txt`): genuine receipt ACCEPTED
(anchored, exit 0); planted forged receipt REJECTED —
"custody finding: no matching issuance entry", exit 1.
The planted receipt is identified in the rig output with
its computed hash and zero issuance entries.

### C4-12 — Binary pin

Dated continuation `BATCH4-C4-12-BINARY-PIN-2026-11-14.md`:
production binary sha256 **9ea9b615…**, distinct from the
source pin 001543f3…; provenance (compiler, flags,
identity header from the installed objects) and the
demonstrated properties are tied to this binary (the
checkpoint's production runs all executed through it).

### Part B — Launch-evidence read-back

`partb_readback.py` over the production evidence family:
**10/10 records re-read OK** — both processes with exact
/proc/<pid>/status paths, raw CapEff/CapPrm/CapAmb all
zero, expected values all zero, recorded comparison
agrees with the re-derived comparison, identity-binding
fields present, reader = pilot-supervisor
(`partb-readback-output.json`). The launch-evidence
family is distinct from the issuance records, as Part B
requires. (The D-T attempts closed pre-release on the
termination rows and have no Part B record — no
observation was attempted on a dead gate; that is the
state table's order, not a gap.)

### D-T demonstrations (§3.5 point 3, Batch 4 gate evidence)

Exercised live against the production binary + supervisor,
using supervisor demo delays to widen real race windows
(rig scaffolding only; protocol paths are production):

- **D-T1** (termination before handoff) — B4DT1: identity
  checks pass on the dead child, readiness fires, ACK 3,
  TERMINATION OBSERVED at validation, launcher reaps, its
  ABORT carries a strictly valid word, no GATE_READY, no
  issuance. ✓
- **D-T6** (the ACK-3 packet and the record) — the same
  run: ABORT reason CHILD_TERMINATED_AT_HANDOFF, word 9
  validated and recorded LAUNCHER-REPORTED, termination
  standing SUPERVISOR-OBSERVED, attempt closes on the
  pair, packet and record agreeing. ✓
- **D-T2** (termination during settling) — B4DT2: pidfd
  observation, class-T ABORT, GATE_READY recorded inert,
  the one STATUS from the launcher's class-T receipt
  action, PRE_RELEASE_TERMINATED, no RELEASE in the
  record. ✓
- **D-T3a** (termination in S5 before the guard) —
  B4DT3: GATE_READY delivered, class-T path, STATUS from
  the same receipt action, no RELEASE ever sent. ✓
- **D-T5a** (EOF-first) — B4DT5: child terminated and
  launcher killed without transmitting STATUS; drained
  EOF established before the bound; close recorded as
  PRE_RELEASE_LAUNCHER_LOST with exactly its facts
  (launcher loss OBSERVED, child termination OBSERVED,
  exit status UNREPORTED, classification UNRESOLVED, no
  issuance). The class-T send attempt's broken pipe is
  recorded (delivered: false), not hidden. ✓
- **D-T5b** (queued-STATUS control) — every production
  closure is the control's shape: the STATUS was consumed
  and validated, EOF observed, and the attempt closed on
  the STATUS (S9), never as launcher-lost; plus the C0
  NQ5' limitation case against this pin. ✓
- **D-T3b** (poll-to-send interval) — by construction:
  RELEASE_SENT and TERMINATION_OBSERVED are recorded as
  separate facts in every production session record and
  no record claims the child was alive at transmission.
- **D-T4** (gate-write boundary) — the GATE_WRITE_FAILED
  path stands on the C0 peer evidence against this pin
  (C2-B(iii): reader closed → GATE_WRITE_FAILED reported,
  STATUS follows with the SIGKILL word); not re-induced
  in Batch 4 (the production binary has no gate-hold
  hook). The supervisor's handling (class/errno recorded
  LAUNCHER-REPORTED, mutual exclusion with GATE_ACTUATED)
  is in the built code, inspected.

### Batch 5 chunk sheet approval (Rule 4 packaging)

`BATCH5-CHUNK-SHEET-DRAFT-2026-11-14.md` (sha256
b08f763d…) rides inside this submission for Alex's
approval, with its disposition slot. Inclusion is
packaging only: Batch 5 does not begin on this
submission — it begins on Alex's recorded approval of
the sheet **and** this checkpoint passing (sheet C5-0a).

## Bundle integrity (C4-D1)

The bundle directory `batch4-checkpoint-2026-11-14/`
carries: this report; the C4-12 continuation; the Batch 5
chunk sheet; supervisor + stub + record + JCS sources;
the check/read-back/anchor tools; production session
records, launch-evidence records, receipts + issuance
record, run records and run artefacts; scratch evidence
set; ix session records + freeze record; rig outputs
(refusals, ix, C4-11, read-back, verify-start); install
evidence v1 + V2; provenance (identity header, identity
JSON, installed pins). `MANIFEST.sha256` in the bundle
pins every file.

## Known limitations, stated

1. (vii)'s induced-nonzero capability case and (viii)'s
   launcher-internal fault windows rest on C0 evidence
   against the identical source pin plus code inspection,
   as the spec provides; they were not re-induced against
   the production binary (which contains no hooks).
2. D-T4 likewise rests on C0 peer evidence for the
   launcher side.
3. B4FDS-20261114-002's record is corrupt by its own
   rig probe (see (vi)); it is included in the fetched
   set with this note, and superseded by -003.
4. STATUS_ACK outcome in all production closures is
   STATUS_ACK_UNDELIVERABLE (the launcher has exited by
   closure) — recorded separately, closure unaffected,
   per spec.
