# Batch 6 source package for Alec — COMPLETE, single-file delivery

Alec — you were right to stop. The pasted assignment was corrupted
in transfer: pieces dropped and spliced at the paste-chunk
boundaries. Ben called the risk before it happened; my check
verified marker strings, not the whole text. This package replaces
the paste entirely: everything you listed, as one file, so what
you read is byte-exact. File sha256 is stated in my cover message
in the chat; the extracts below each carry their source and pin.

Contents:
1. Build Spec Rev 26 §2.4 (what the build produces)
2. Build Spec Rev 26 §3.1 (driver — item (ix) rides inside)
3. Build Spec Rev 26 §3.4 (canonical execution record)
4. Build Spec Rev 26 §3.5 (supervisor and commitments — SE-7)
5. Build Spec Rev 26 §3.7 (examiner tooling, stub subject, transport double)
6. Build Spec Rev 26 §4 Batch 6 entry + §5 gates G1-G5 (full, untruncated)
7. Build Spec Rev 26 §7 (gates and roles)
8. PILOT-ACCEPTANCE-CRITERIA-04 §4, §5 (incl. 5.1, 5.3), §8
   (file sha256 7608d74eef511b59ae59c33d18b299ac050c943ebebc10aeed816e101a822e2e — matches the Rev 26 pin table)
9. PILOT-HARNESS-DESIGN-03 §2.6, §4.5, §7
   (file sha256 b0fca1259c0f6432437535ad92224ad8cd824f71a078d91b7f455182c8df0d04 — matches the Rev 26 pin table)
10. Batch 5 chunk sheet, remainder: C5-11 through the end
    (Checkpoint section + standing rules)

The Batch 5 clearance also landed since my last message: Alex
CLEARED Batch 5 today (correction 4, C5-17 closed). Your draft
remains preparation — Batch 6 execution still needs its own
authority — but there is no longer a Batch 5 blocker in front of
it. Compose the complete Batch 6 chunk sheet and gap register
from these texts; flag anything still missing rather than
guessing.

— Remmy


===== 1. REV 26 §2.4 =====
### 2.4 What the build produces (new artefacts, all pinned at Batch 0's re-freeze or at their batch checkpoint)

- **PILOT-TOOLS-01** — the model-neutral tools revision (Harness
  §§3–4), a new artefact; the pinned `tools.py` is never edited.
- **EXTRACTOR-RULES-02** — the extractor rules as versioned pilot
  data (Harness §3.2).
- **PILOT-DATA-PACKS-01, PILOT-DATA-EXPECTED-01,
  PILOT-DATA-T09-01, PILOT-DATA-FIXTURES-01** — the pilot data
  files (Harness §3.3).
- **PILOT-CORPUS-SNAPSHOT-01** — the pinned corpus snapshot
  (Harness §5).
- The **driver + record writer** implementing `PILOT-RUN-RECORD-01`
  (Harness §§1–2).
- The **issuance registry** (Harness §4.2) — harness-internal
  state, specified here, built in Batch 2.
- The **run supervisor** and the `commitments/` store (§3.5),
  and the **privileged launcher binary** (§3.5) — root-owned,
  setuid, its source pinned in the re-freeze amendment; part of
  the inspected build.
- The **adapter** implementing `ADAPTER-CAPTURE-02` (Adapter
  §§2–5), including the helper wrapper of Adapter §3.2.
- The **examiner tooling** implementing the replay procedure
  (Harness §7; Criteria §8) as a runnable artefact, so inspection
  and Stage 6 examination run the same code path the criteria
  describe.
- **PILOT-CALIBRATION-01** — the calibration certificate
  (Criteria §5), produced in Batch 6.
- The **Stage 5 evidence pack**: the sabotage battery's scratch
  record, the interrupted-write test's artefacts, the SE-1…SE-7
  demonstration results, the stub-subject full-battery record,
  and its re-derivation report — preserved for inspection,
  verified by re-derivation, not by summary (Criteria §4, §8).

---

## 3. COMPONENT SPECIFICATIONS

Each subsection states what the builder builds, the governing
source for every behaviour, and the checkpoint evidence the
batch must produce. Where a behaviour is specified in a source
by section number, this spec cites it and does not restate it
loosely: the source text governs.


===== 2. REV 26 §3.1 =====
### 3.1 Driver (Harness §1)

Build a driver that executes the nine pinned trees
(`PROCESS-TREES.md`, row 3) as read under INTERPRETATION-NOTE-01
(S6). Requirements:

- **Order and dependency.** Steps execute in declared order;
  dependencies are the trees' chains; the driver never reorders,
  parallelises, or skips a step whose dependencies are satisfied
  (Harness §1.1). A step whose dependency failed does not
  execute; the tree follows its failure path.
- **Step types.** [TOOL] and [RULE] steps execute
  deterministically in harness code; [MODEL] steps call the
  adapter's `complete()` exactly once per step attempt with the
  assembled `step_inputs`; every step's declared *Verify*
  condition executes as a distinct [CHECK] phase with its own
  record event (Harness §1.2). A step is satisfied only when its
  operation completed **and** its [CHECK] passed.
- **Declared-inputs-only assembly.** Before any [MODEL] call
  the driver assembles the step's input manifest — exactly the
  artefacts the tree declares, each cited by record reference
  and hash — and writes it to the record **before** the call
  (Harness §1.3). Messages are constructed only from the pinned
  tree text (verbatim) and the manifest's artefacts, serialised
  in the canonical form pinned at §3.4 (RFC 8785), per
  Adapter §2.2.
  The subject never hunts raw sources; tree source prohibitions
  are enforced structurally (e.g. T05-STEP-06 never receives the
  draft's own values; T08's seeded draft is an input to
  diagnosis only).
- **Failure branches — the trees' rules, no others** (Harness
  §1.4): STOP steps halt the tree; return-once recoveries
  re-attempt once with the failure named in the re-attempt's
  declared inputs; bounded corrections (T05-STEP-06,
  T08-STEP-04) allow at most 2 attempts; absence-as-finding
  answers UNKNOWN by rule; the T09 decision-stands rule keeps
  the worksheet as the system decision. An ADAPTER_FAILURE
  closes the tree `INVALIDATED-INFRASTRUCTURE` unless a tree
  declares a covering recovery (none does). A GOVERNANCE_FAILURE
  is recorded and follows the tree's failed-verification path —
  never retried away, never reclassified.
- **No verdicts.** The driver emits the record and nothing else:
  no score, no pass/fail for any tree (Harness §1.5; Criteria
  §2).
- **Budgets and stops** (Harness §6; Criteria §7.2): [TOOL]/[RULE]
  step 60 s; [MODEL] step 300 s; tree 3,600 s; run 4 h wall
  clock; the lane-failure rule (3rd INVALIDATED-INFRASTRUCTURE
  closure stops the run); the integrity rule (snapshot hash
  re-verified at every `TREE_TRIGGERED`); stop finality (after
  `RUN_STOPPED`, nothing further is written). **Adjudication
  order (Rev 23):** a step's budget is adjudicated before its
  terminal events are written — the operation's events
  (`TOOL_INVOKED`/`TOOL_RETURNED`, `MODEL_CALL_LINKED`,
  `STEP_PROGRESS`) stand as they occur, then the budget
  verdict, then exactly one terminal outcome for the attempt
  (its `CHECK_RESULT` and `STEP_SATISFIED`/`STEP_FAILED`).
  An over-budget attempt never carries a passing
  `CHECK_RESULT` or a `STEP_SATISFIED`. The failure classes
  of Harness §6.2 are settled by step kind: a [TOOL]/[RULE]
  step that exceeds its budget fails with class
  **STEP_TIMEOUT** (a governance-class failure: the
  machinery's own bound was crossed); a [MODEL] step still
  outstanding at its budget fails with class
  **ADAPTER_TIMEOUT** (§6.2's adapter timeout class). The
  same order holds at tree and run level: a level's budget
  is adjudicated before that level's terminal event.


===== 3. REV 26 §3.4 =====
### 3.4 Canonical execution record (Harness §2)

- **Form** (Harness §§2.1–2.2): one run = one append-only JSON
  Lines file, `run-record.jsonl` — one JSON object per line,
  written and flushed at the moment the event occurs, never
  edited afterwards. Event schema `PILOT-RUN-RECORD-01`: `seq`
  (strictly increasing from 1; a gap voids the record),
  `event_id` (`"<run_id>:<seq>"`), `run_id`
  (`<battery-id>-<UTC date>-<counter>`), `recorded_at_utc`,
  `event_type` (the closed §2.3 list), `tree_id`/`step_id`,
  `payload` (full content, never a summary or a pointer to
  harness memory), `prev_event_sha256`, `event_sha256`.
- **The chain's claim, qualified** (Harness §2.6, Alex's
  correction A): the hash chain makes insertion, deletion, or
  reordering **detectable relative to the chain's own links**,
  and — with the §3.5 commitments — detectable absolutely. The
  chain alone detects accidental corruption and ordinary,
  partial edits; **wholesale rewrite is defeated by the external
  anchor, not by the chain**, and no build artefact, comment, or
  report may claim otherwise.
- **Event vocabulary** (Harness §2.3): the run/tree/step event
  types as specified there, including `TOOL_INVOKED`/
  `TOOL_RETURNED` with complete payloads verbatim (nothing
  truncated), `MODEL_CALL_LINKED` carrying `{capture_id,
  record_sha256, request_sha256, response_sha256}` plus the
  verbatim `raw_output`, `CHECK_RESULT` with the declared verify
  condition quoted, and `LEDGER_ENTRY` in the established schema
  plus the §4 provenance additions (`operation_id`, recomputation
  evidence). `ledger.json` is materialised from the record by
  the declared mechanical extraction (all `LEDGER_ENTRY`
  payloads in `seq` order); the record is canonical, the file is
  a view, and re-running the extraction must yield the identical
  ledger.
- **Organisation without an index** (Harness §2.4): the
  `runs/<run_id>/` + `commitments/` layout as specified there.
  Discovery is the directory listing; linkage is by reference
  and hash, never by index. The harness writes **nothing**
  outside the run directory — never to the bridge index, the
  shelf, or any manifest; its inputs arrive read-only. It has
  **no write path to `commitments/`** (§3.5).
- **Pinned-input block** (Harness §2.5): `RUN_STARTED` embeds
  the run's complete pin set — every artefact consumed, each as
  `{path, sha256}`, verified at pre-flight against
  PILOT-MANIFEST-01 + the Stage 5 re-freeze amendment; any
  mismatch and the run does not start. The block is the chain's
  genesis; its hash is the content of the START commitment.
  **The pin authority (Rev 23):** the pin set is not supplied
  by the run's caller. It is read from **PILOT-PIN-
  AUTHORITY-01**, a machine-readable artefact generated from
  PILOT-MANIFEST-01 and the re-freeze amendment chain, each
  entry traceable to its source row or amendment. The
  authority's own sha256 is recorded in the amendment that
  pins it (for this build, the Batch 3 correction
  continuation); pre-flight first validates the authority
  file's hash against that recorded value, then verifies
  every consumed artefact against the authority. The
  authority's location is fixed by the build (the freeze of
  record); caller configuration cannot choose, replace, or
  supplement it — a caller-supplied pin that diverges from
  the authority in either direction (a changed hash, an
  added entry, an omitted entry) refuses the run exactly as
  a file mismatch does. The inventory is **complete**: every
  artefact the run consumes appears — the build artefacts,
  the pilot data files, the extractor-rules data, the trees
  and interpretation note — with **file pins distinguished
  from constituent pins**: the corpus snapshot enters by its
  two file pins (`sections.jsonl`, `manifest.json`), and its
  constituent pins are the per-section hashes recorded in
  that manifest, anchored by the manifest's file pin. The
  Batch 3 correction's substitution test is this section's
  acceptance evidence: a consumed file changed **and** its
  caller-supplied hash changed to match must still refuse.
- **Canonical serialisation — RFC 8785, pinned (Rev 02, Alex's
  correction B).** The sources require hashes over "canonical
  serialisations" without pinning the exact byte form; Rev 01's
  description (UTF-8, sorted keys, no insignificant whitespace)
  did not fully define canonical bytes — number representation,
  string escaping, and duplicate-key handling could still differ
  between implementations, and the event chain, the receipts,
  and replay all depend on exact byte-level agreement. This spec
  therefore pins a complete standard: **RFC 8785 (JSON
  Canonicalization Scheme, JCS)** is the canonical form for
  every structured artefact the harness serialises and hashes —
  run-record events (the `event_sha256` / `prev_event_sha256`
  preimages), the receipts and commitments as serialised,
  ledger entries, capture records, registry-relevant records,
  the pinned-input block, and the issuance-record entries. The
  contract the builders implement against: number serialisation
  exactly per RFC 8785 (the ECMAScript number-to-string
  algorithm the RFC normatively adopts); string escaping
  exactly per RFC 8785 (the minimal escape set it prescribes);
  object members ordered by the UTF-16 code unit sequence of
  their names; no insignificant whitespace; the output encoded
  UTF-8. **Rejection rules:** a value that cannot be safely
  represented is **rejected, never coerced** — NaN and positive
  or negative infinity; duplicate object keys, detected at
  parse; strings containing lone surrogates; and any parsed
  value that cannot be re-serialised to identical canonical
  bytes. A rejection is a failure surfaced in the open, never a
  silent substitution. **Raw bytes are never canonicalised:**
  hashes over raw byte artefacts are sha256 over the bytes
  exactly as they lie — captured HTTP request and response
  bodies (`request_sha256`, `response_body_sha256`), the record
  file's exact bytes (`record_file_sha256` in TERMINAL and
  CRASH receipts), corpus and snapshot files, and every file
  pin. Canonicalisation applies to harness-serialised JSON
  only. **Freeze rule:** this contract — the standard
  identifier ("RFC 8785") recorded in the frozen configuration —
  is frozen at Batch 0 in the re-freeze amendment **before**
  any hash is generated; changing the canonicalisation standard
  afterwards is a re-freeze amendment, and hashes taken under a
  superseded form do not carry over. Two canonical forms in one
  record void the record. **Implementation pin (Rev 12,
  Claude's finding 8):** the standard is pinned; the
  implementation is pinned with it. The JCS implementation the
  build uses is frozen at Batch 0 by **name, version, and
  artefact hash**, recorded in the re-freeze amendment's freeze
  evidence alongside the standard identifier above; it must
  pass the **RFC 8785 conformance test vectors** as part of the
  Batch 0 freeze checks, with the vector results preserved in
  the freeze evidence; and **any change of implementation or
  version is a re-freeze event** of the same kind as changing
  the standard — hashes taken under a superseded implementation
  do not carry over. This spec names no implementation: the pin
  is taken at Batch 0, from the implementation the build
  actually uses.


===== 4. REV 26 §3.5 =====
### 3.5 Supervisor and commitments — the custody design, settled (Harness §2.6; SE-7)

Harness §8 Q10 left the supervisor's concrete form as a Stage 5
build decision, with the default "the lightest form that keeps
the write path outside the harness's privilege boundary." This
spec **settles** that decision as follows. It is stated plainly
as a proposal: the inspectors judge it, and an inspector
requiring a stronger form converts it to an amendment before
Batch 4 begins — the builder does not substitute another form
unilaterally.

**The design — a separate supervisor program under a separate
OS identity, owning the commitments store.**

1. **Two OS identities.** The pilot runs under two distinct
   unprivileged OS user accounts on the build machine:
   `pilot-harness` (owns and runs the harness, the tools, the
   adapter, and the run directories) and `pilot-supervisor`
   (owns the supervisor program and the `commitments/` tree).
   Neither account is the operator's interactive account, and
   neither has write access to the other's trees:
   `runs/` is owned by `pilot-harness`; `commitments/` is owned
   by `pilot-supervisor` with directory/file permissions that
   grant `pilot-harness` **no write, no create, no delete, and
   no read** on receipts or the issuance record (mode `0700` on
   the directory, `0600` on files, ownership
   `pilot-supervisor`). The mechanism that keeps the harness
   from the receipts is therefore the operating system's
   ownership and permission enforcement — named, inspectable,
   and testable — not a convention in harness code. The harness
   needs no read on `commitments/` at all: the record never
   cites the commitments back (Harness §2.4), and examination is
   performed by the examiner tooling (§3.7) running under the
   operator's authority, not the harness's.
   **Group separation (Rev 03).** As a build precondition,
   `pilot-harness` is **not** a member of the
   `pilot-supervisor` group, and `pilot-supervisor` is not a
   member of any group that confers `pilot-harness`
   privileges. The launcher's mode `4710` group-execute
   (point 2) is the control that limits who may invoke it, and
   that control proves separation only if the memberships
   actually separate — which is why the fact is read from the
   operating system and demonstrated, not inferred from the
   accounts' names (SE-7 demonstration (vii), below).
2. **The three processes — supervisor, launcher, harness
   child (Rev 17; Ben's B1-6 ruling, Option A with Alex's
   corrections A–D; §0B.1).** A run involves three distinct
   processes, and this point assigns every responsibility to
   exactly one of them; no later passage may reassign them.
   The **supervisor** is a single-purpose Python programme run
   as `pilot-supervisor`: it owns issuance, the `commitments/`
   store, every record it writes, and every terminal-event
   decision. The **launcher** is a minimal, single-purpose
   binary, owned by **root**, **setuid-root**, mode `4710` with
   group `pilot-supervisor`, so only the `pilot-supervisor`
   identity can execute it: it is the harness child's **OS
   parent**, the sole holder of the `waitpid()` relationship
   to the child while it lives, and the reporter of the
   child's raw exit status — nothing more. The **child** is
   the harness, spawned by the launcher, transitioned to
   `pilot-harness`, held behind the launch gate until the
   supervisor authorises its release. The supervisor never
   parents the child, never calls `waitpid()` on it, and
   never holds `PR_SET_CHILD_SUBREAPER` over it; the launcher
   never issues, never computes a committed value, and never
   writes to `commitments/` or to any supervisor record.
   **How the supervisor spawns the launcher.** The supervisor
   creates the status channel first — a `SOCK_SEQPACKET`
   socketpair — retains one end, and passes the other to the
   launcher at the fixed descriptor number 3 across the exec
   (that descriptor alone is created without close-on-exec).
   The launcher's sole argument is the run identifier,
   validated against the strict run-ID grammar (A-1). The
   supervisor thread that performs the spawn is the
   supervisor's **main thread**, and it remains alive for the
   launcher's whole life (Alex's correction B: Linux
   parent-death semantics watch the creating **thread**, so a
   spawning thread that exits would kill the launcher mid-run
   even though the supervisor process lives). **Signal
   establishment (Rev 18).** Before anything else — before
   it reads anything and before any fork — the launcher
   (a) sets `SIGPIPE` to `SIG_IGN` and keeps it ignored for
   its whole life, so no write it ever makes, to the gate
   pipe or to the channel, can kill it by signal; and
   (b) **explicitly installs `SIGCHLD`** with handler
   `SIG_DFL` and flags **without `SA_NOCLDWAIT` and without
   `SA_NOCLDSTOP`**, reads the disposition back, and
   verifies handler and flags; on any failure, or if the
   resulting state cannot be verified, it exits non-zero
   **before forking**, having spawned nothing. This is an
   establishment condition, not an assumption: a `SIG_IGN`
   disposition survives `execve()`, so a launcher started
   by a supervisor that ignores `SIGCHLD` would inherit
   auto-reaping, and `SA_NOCLDWAIT` likewise prevents
   zombies from forming — either would silently destroy
   both the zombie and the `waitpid()` status that point
   3's readiness design exists to use. **No `SIGCHLD`
   handler and no alternate reaping path is permitted
   anywhere in the launcher's life.** The supervisor
   likewise ignores `SIGPIPE` in its own process; its
   channel writes treat `EPIPE` as the launcher-loss
   observation. The launcher's next act is to arm its own
   backstop against the supervisor: it takes its expected
   parent identity from `getppid()`, arms
   `prctl(PR_SET_PDEATHSIG, SIGKILL)`, reads the setting back
   with `PR_GET_PDEATHSIG`, and re-checks `getppid()` against
   the same value; any failure or mismatch and it exits at
   once, spawning nothing. **The launcher accepts no
   arbitrary input:** the harness programme path and the
   argument-vector shape are **compiled into the binary** at
   build time — there is no configuration file — and the sole
   variable field is the run identifier. Any other
   invocation — a different programme, extra or missing
   arguments, a malformed run identifier — is refused: the
   launcher exits non-zero and spawns nothing. It invokes no
   shell, opens no network connection, and loads no code
   beyond the fixed exec. **Its privileged window performs
   no file writes at all. Language (Rev 12, Claude's finding
   3; qualification Rev 17):** the launcher is implemented
   in **C**, compiled at build time — Linux **ignores the
   setuid bit on interpreted scripts**, so the setuid
   launcher cannot be an interpreted programme. This is the
   launcher-language exception to §6.3 item 4's Python
   default (D-9, §0B.3). The qualification, stated once and
   governing every C claim in this spec: the toolchain facts
   relied on (compiler, flags, link properties) are recorded
   evidence, gathered at build; the **choice of C itself is
   a recorded preference** — forced in kind (a compiled
   language) by the setuid constraint, not proven superior
   among compiled languages; and the built binary's runtime
   and dependency properties are **demonstrated from the
   binary itself** at the Batch 4 checkpoint (SE-7), never
   inferred from the language it was written in. Source
   inspection and binary inspection are distinct events and
   neither substitutes for the other. **Single-threaded
   across the launch lifecycle (Rev 07).** The launcher
   creates no threads at any point: the thread that calls
   `fork()` is the process's only thread; it is that same
   thread which performs the transitions, holds the gate,
   and holds the `waitpid()` relationship, alive until the
   child's lifecycle completes. Linux defines the parent
   for `PR_SET_PDEATHSIG` purposes as **the thread that
   created the child**; this design's parent-identity
   reasoning is stated against a launcher in which thread
   identity and process identity coincide. The gate evidence
   includes, for each test launch, a launch-time record that
   the launcher's `Threads` field equalled `1` at launch.
   **Source pinning — chronology (Rev 17; Part 3 of the
   approved correction plan).** The launcher's behaviour and
   interface stand frozen at Batch 0. Its source is written,
   then **pinned by sha256**, then **inspected**, then the
   disposition is **recorded** — and only then may Batch 4
   begin. The Batch 4 checkpoint records the **built
   binary** — its hash and demonstrated properties — and
   nothing about the checkpoint substitutes for the earlier
   source pin and inspection. **Setuid preconditions —
   verified, fail-closed (Rev 03).** The supported operating
   system is Linux. A probe invocation (SE-7 demonstration
   (vii)) must observe effective uid `0` inside the
   privileged window, and the conditions that silently
   defeat setuid — the launcher's filesystem mounted
   `nosuid`, an inherited `no_new_privs` flag — are checked
   and recorded alongside it. **A failed privilege
   assumption stops the build; it never triggers a fallback
   to a weaker launch arrangement.**
3. **The spawn sequence and the status-channel protocol —
   a gated launch under the three-process model (Rev 17).**
   The sequence has nine stages. Stages are named S-references
   into the protocol state table that closes this point;
   the table is the authoritative contract, and this prose
   is its reading, not a rival to it.
   **Stage 1 — Preparation (supervisor).** Before spawning
   the launcher, the supervisor performs its standing
   pre-launch verifications: the retained descriptors `0`/`1`/`2`
   resolve to their declared destinations and modes (the
   descriptor-separation block below), and the harness
   executable (and any interpreter) satisfies the three-part
   exec condition with its identity recorded (the
   identity-continuity block below). A failure aborts the
   launch before any process exists, recorded in the run
   log. The supervisor then creates the status channel and
   spawns the launcher (point 2). **Stage 2 — Launch
   request.** The supervisor sends `LAUNCH_REQUEST` on the
   channel, carrying the run identifier, the **expected
   supervisor PID** (the supervisor's own `getpid()`,
   Alex's correction A), and the child's target uid/gid
   (`pilot-harness`). **At initialisation, before it forks
   anything, the launcher sets the shared flags `reaped` =
   false and `sent` = false (Stage 5's contract); their
   lifetime is the whole launcher session, so the
   pre-handoff reap sites R-1…R-3 already act under them
   (Rev 21).** The launcher validates the packet's
   framing, requires the request's run identifier to equal
   its argv value, and requires the expected supervisor PID
   to equal its own `getppid()` — a bare `getppid()` result
   is never trusted without this cross-check against the
   value the supervisor supplied through the validated
   request. Any mismatch: the launcher exits, spawning
   nothing; the supervisor records the aborted launch.
   **Stage 3 — Establishment (the child).** The launcher
   creates the **private launch-gate pipe** (`pipe2(O_CLOEXEC)`;
   the read end passes to the child, the write end is held
   by the launcher, no other process holds either end) and,
   **before the fork**, captures the **expected parent
   identity** — its own `getpid()` — in a variable the child
   inherits across the fork as part of its memory image: an
   inherited, expected value that nothing outside the
   child's own pinned code can alter after the fork
   (Rev 07). The launcher forks. The child's steps run in
   exactly this order, and the order is normative:
   (a) **parent check** — `getppid()` must equal the
   inherited expected parent identity; if it differs, the
   launcher died before the child's first instruction and
   the child has already been reparented, so the child
   `_exit()`s at once, without proceeding;
   (b) **privilege transition** — the child clears its
   supplementary groups and drops privilege precisely
   (Rev 03): `setresgid()` followed by `setresuid()`, each
   setting **all three** ids — real, effective, and saved —
   to `pilot-harness`, verified by reading back
   `getresgid()`/`getresuid()`; every position must equal
   `pilot-harness` exactly, and any failure or mismatch
   means immediate `_exit()`, never a continuation into the
   exec and never a fallback identity;
   (c) **capability read-back** — with the verified drop,
   the child reads back its own capability state by one of
   two methods (Rev 10; methods distinguished, Rev 11).
   **Method A:** the `CapEff`, `CapPrm`, and `CapAmb`
   fields of `/proc/self/status`, read and verified
   directly. **Method B:** `capget`, for the effective and
   permitted sets, **plus** an explicit ambient read-back —
   `prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_IS_SET, …)` queried
   for every capability number from `0` to the maximum the
   kernel supports, each query required to return `0`.
   `capget` does **not** return the ambient set, so a
   `capget`-only read-back cannot observe one of the three
   sets this clause requires: **a method that cannot
   observe the ambient set does not satisfy this
   requirement. All three sets must be empty.** Any nonzero
   value, or an unsuccessful, incomplete, malformed, or
   unavailable read-back, means immediate `_exit()`,
   fail-closed — the guarantee is claimed on the
   **observed** state at the point of reliance, not
   inferred from the intended transition. The three masks
   as read are preserved as launch evidence;
   (d) **arming** — **only after** the transition and the
   read-backs does the child arm its parent-death backstop,
   `prctl(PR_SET_PDEATHSIG, SIGKILL)`: the setting is
   **cleared whenever the process changes its effective
   user or group id** (`prctl(2)`), so it is armed after
   the transitions and **no credential change follows it**
   anywhere in this sequence — the exec that ends the
   sequence is a plain exec, under the same identity and
   changing no credentials, of a programme that is **not
   setuid, not setgid, and carrying no file capabilities**
   (the three-part exec condition, Rev 07). The arming is
   fail-closed on its own result: a non-zero `prctl()`
   return means immediate `_exit()`;
   (e) **arming read-back** — immediately after a successful
   arming the child reads the setting back,
   `prctl(PR_GET_PDEATHSIG)`, and requires the value to
   equal `SIGKILL`; a failed read-back or a mismatched
   value means immediate `_exit()`;
   (f) **parent re-check** — `getppid()` must still return
   the expected parent identity captured before the fork.
   If it differs — the launcher died between the first
   comparison and the completed arming, before the signal
   could cover the death — the child `_exit()`s at once:
   **if the parent thread has already terminated by the
   time `PR_SET_PDEATHSIG` is called, no signal will be
   sent**, so the identity the child arms against must be
   proven live at both comparisons, against the one
   pre-fork value; the two comparisons close both
   intervals (demonstration (viii));
   (g) **descriptor close** — the child closes **every
   inherited file descriptor except the declared
   allowlist** — fds `0`, `1`, and `2`, retained solely in
   their declared standard roles and only at their
   verified destinations (the descriptor-separation block
   below), and the gate read end, which joins the allowlist
   for the pre-exec window only — by an exhaustive close
   (`close_range(3, ~0U)` sparing the gate descriptor, or
   an equivalent enumeration of `/proc/self/fd`). The
   status channel is **not** inherited by the child: it is
   created close-on-exec in the supervisor and is never in
   the launcher's descriptor set passed across this fork
   beyond the launcher's own end, which the child's
   exhaustive close removes in any case;
   (h) **the gate** — the child blocks reading exactly one
   byte from the gate read end. Only the launcher's single
   release byte proceeds to the exec (Stage 6); on
   end-of-file — the write end closed without a release —
   on any other byte value, or on any read error, the
   child `_exit()`s immediately, **without executing the
   harness**: the gate never resolves in the child's favour
   by default.
   **Stage 4 — The pidfd handoff and its interlock.** The
   child established and gated, the launcher first makes a
   **pre-handoff liveness observation**: `waitpid(child,
   WNOHANG)` must return 0. This is an observation at an
   instant — it establishes the child had not terminated
   when checked; it does not guarantee liveness when the
   supervisor validates. If the child has already
   terminated (a Stage 3 `_exit()`), the launcher reaps it
   itself — it is the parent — **setting `reaped` and
   holding the raw word (site R-1 of the Stage 5
   inventory)**; it sends `ABORT` with reason
   `CHILD_LOST_IN_ESTABLISHMENT`, whose detail **carries
   the raw wait-status word** under the catalogue's ABORT
   encoding (Rev 21): the supervisor validates the word
   under the strict encodings and records it as
   **launcher-reported** — its own termination observation
   for this attempt remains **UNKNOWN** (no handoff
   occurred, so no pidfd-based observation exists, and the
   launcher's report is never classified as supervisor
   evidence). `sent` is not set — an ABORT is not a STATUS
   transmission — and the launcher exits; no handoff is
   sent, and the supervisor records the aborted launch with
   child termination UNKNOWN on its own side (it holds no
   pidfd and observed nothing; the PDEATHSIG design
   expectation is not evidence — Stage 9). Otherwise the
   launcher calls `pidfd_open(child)` and sends
   `PIDFD_HANDOFF` — payload: child_pid and the child's
   start time (field 22 of `/proc/<child>/stat`, read by
   the launcher) — with the pidfd attached as exactly one
   ancillary descriptor. **The supervisor validates, in
   this order:** (1) **descriptor target** — it reads
   `/proc/self/fdinfo/<received fd>`; a pidfd's fdinfo
   reports its target PID (`Pid:` field, in the reader's
   PID namespace); the reported target must equal
   child_pid. This establishes that **this descriptor
   denotes the claimed PID**, not merely some live process.
   (2) **Instance binding** — `/proc/<child_pid>/stat` must
   show the claimed start time, and the process's parent
   PID must be the spawned launcher's known PID: (PID,
   start time) binds the PID to the unique intended
   instance. (3) **Readiness (Rev 18)** — the supervisor
   polls the validated pidfd under the readiness contract
   specified with the protocol below (one operation, two
   call sites: here, and at Stage 6 before RELEASE). If
   the poll reports the descriptor **readable**, the child
   has **already terminated**: it is an unreaped zombie
   whose identity checks (1)–(2) have passed on a dead
   process — identity is not life. The supervisor records
   TERMINATION OBSERVED (its own observation, at
   validation), refuses with `HANDOFF_ACK` code **3**, and
   closes the descriptor. On code 3 the launcher **reaps
   only** — it does not kill the child; there is nothing
   living to kill — and sends `ABORT` with reason
   `CHILD_TERMINATED_PRE_RELEASE`, the ABORT detail
   carrying the raw wait_status word; the supervisor
   validates that word under the strict encodings below
   and records the exit basis as LAUNCHER-REPORTED, the
   termination itself as its own observation. If the poll
   reports **no readiness**, the supervisor records
   NOT-OBSERVED-TERMINATED AT VALIDATION — an observation
   at an instant, never a liveness guarantee; a child
   dying the next instant is governed by the pre-release
   termination rules below. Any other poll outcome fails
   closed per the readiness contract (refusal, with the
   recorded reason the contract specifies). (4) The
   validated pidfd is then retained as the instance
   handle; PID reuse thereafter cannot confuse the record.
   From adoption onward the supervisor **watches the
   pidfd continuously** in its event loop, alongside the
   channel and the record file; termination observed in
   any state triggers that state's rule when observed,
   not only at checkpoints. **Kernel assumption, pinned:** the
   room's kernel exposes a pidfd's target PID via fdinfo;
   the gate evidence records the room kernel's exact
   version string (`uname -r`) and a verbatim fdinfo
   sample, and demonstrates checks (1)–(2) against a live
   handoff **and** the fdinfo behaviour for an
   already-exited target (obtain a pidfd, let the target
   exit, read the fdinfo, record what `Pid:` shows) — the
   exited case is pinned as OBSERVED evidence about the
   interface; validation never depends on it. **Fail-closed,
   with the race named:** if the fdinfo target is missing,
   unreadable, or mismatched **because the child exited in
   the window between the launcher's liveness observation
   and this validation**, the supervisor rejects the
   handoff, closes the descriptor, and records
   `HANDOFF_REJECTED_TARGET_LOST` with the observed fdinfo
   state — an availability outcome, not a validation
   success and not a launcher violation. A target that is
   present but names a **different live process** is a
   validation failure of a graver kind: rejected, closed,
   recorded as a protocol violation, launch aborted. There
   is **no weaker fallback path**: a liveness-only check
   (`pidfd_send_signal(pidfd, 0, …)` succeeding) proves a
   descriptor denotes **a** live process and plays **no**
   identity role anywhere in this design. The supervisor
   answers `HANDOFF_ACK` with an exact code: **0** =
   accepted; **1** = identity validation failed (including
   a readiness-poll failure at this call site, recorded
   with its poll reason); **2** = target lost
   (`HANDOFF_REJECTED_TARGET_LOST`); **3** = child
   terminated (readiness readable — the step (3) path).
   **The interlock:** the child remains behind the
   gate, and the launcher takes no settling step, until
   `HANDOFF_ACK` arrives. On refusal **codes 1–2** the
   supervisor closes the pidfd at once; the launcher —
   still privileged at this stage — kills the gated child
   directly, reaps it with `waitpid()` — **setting
   `reaped` and holding the raw word (site R-2 of the
   Stage 5 inventory); the word is not transmitted on this
   path, `sent` stays false, and the launcher exits at
   once** — non-zero; the supervisor records the launch as
   aborted, with no issuance of any kind. On refusal
   **code 3** the generic refusal path does **not** run:
   step (3)'s reap-and-report path runs instead — the
   launcher reaps the already-dead child — **setting
   `reaped` and holding the raw word (site R-3)** — and
   sends `ABORT` with reason
   **`CHILD_TERMINATED_AT_HANDOFF`**, its detail carrying
   the raw status word (the catalogue's definition); the
   supervisor records the pidfd termination as
   **supervisor-OBSERVED** and the word as
   **launcher-REPORTED**, the two facts never merged.
   **`sent` is not set (an ABORT is not a STATUS
   transmission), and the launcher exits after the
   ABORT**; code 3 never falls through to a kill. **Stage 5 — The launcher settles.** On
   `HANDOFF_ACK` 0, and only then, the launcher drops its
   own privilege — supplementary groups cleared,
   `setresgid()` then `setresuid()` setting real,
   effective, and saved ids to `pilot-supervisor`, verified
   by the same read-back — and reads back its own
   capability state by the Stage 3 method, requiring **all
   three sets empty**; the observed masks join the child's
   in the launch record, as launch evidence. It then
   performs the **pre-release identity re-check** (layer
   (3) of the identity-continuity block below): it
   re-resolves the fixed executable and interpreter paths
   canonically and re-stats the resolved objects; device
   and inode, mode bits, and capability set must match the
   verified identity records **exactly**. **Failure
   handling, by window (Rev 05, carried):** a failure
   detected **before** the launcher's drop has taken
   effect (**Window 1** — a `setres*()` call itself fails;
   the launcher is still privileged) is handled directly:
   the launcher kills the waiting child (`SIGKILL`),
   closes the gate write end without writing the release
   byte, reaps the child with `waitpid()` — **setting
   `reaped` and holding the raw word (site R-4 of the
   Stage 5 inventory); the word is held locally and never
   transmitted on the settling-failure paths, `sent` stays
   false** — and only then terminates itself. A failure
   detected **after** the
   drop (**Window 2** — a read-back mismatch, a nonzero
   capability set, an unavailable read-back, or an identity
   re-check mismatch) is handled through the gate, because
   the dropped launcher may no longer hold permission to
   signal a `pilot-harness` child across the uid boundary:
   the launcher closes the gate write end without writing
   the release byte; the waiting child observes end-of-file
   and `_exit()`s itself, under the gate rule; the
   launcher `waitpid()`s, reaps it — **setting `reaped`
   and holding the raw word (site R-5 of the Stage 5
   inventory); the word is held locally and never
   transmitted on the settling-failure paths, `sent` stays
   false** — and only then terminates itself. In
   **neither** window is any issuance
   of any kind made, and in neither window is a harness
   left running or a child left waiting. Where the channel
   remains usable, the launcher reports the failure as
   `ABORT` with its reason before exiting — **the reason
   only; the held raw word is never carried on a
   settling-failure ABORT (sites R-4/R-5)** — and the
   supervisor records the abort per the state table — the
   launcher's cleanup never substitutes for the
   supervisor's record. An unobserved capability state
   releases nothing. Only on a **fully verified** settling
   — identity, capability state, and the identity re-check
   all passing — does the launcher send `GATE_READY`.
   **Termination during settling (Rev 18):** if the
   supervisor observes the child's termination on the
   pidfd while in S4 or S5, the pre-release termination
   rules below govern (a class-T `ABORT`; RELEASE barred
   for the attempt from that commitment; a `GATE_READY`
   arriving afterwards is recorded and inert).
   **The launcher's action on a class-T ABORT (Rev 19).**
   The launcher carries two state flags — `reaped` and
   `sent`, both initially false, each set exactly once —
   which are its single reaping and reporting state for
   the whole session; Stage 8's ordinary `waitpid()` and
   STATUS pass through the same flags. **The shared-flag
   contract (Rev 20, completed Rev 21).** The flags are
   initialised at launcher initialisation, before the fork
   (Stage 2); their lifetime is the whole session. **The
   uniform rule: every successful `waitpid()` in the
   launcher sets `reaped` and holds the raw word — no reap
   sits outside this state.** Four rules govern what
   happens around that rule, and every reap or report site
   — the inventory below — is bound to them at its own
   text. (1) `reaped` is set **only** by a successful
   `waitpid()` on the child, the returned PID confirmed as
   the child's, in whichever path performs that wait, at
   the moment the raw word is held — and by nothing else.
   (2) `sent` is set **only** immediately before the
   single STATUS transmission, in whichever path performs
   it, always before the send is attempted; a failed
   transmission is never retried. (3) **Invariant:**
   `sent` true implies `reaped` true — no STATUS is ever
   committed for transmission without a valid held raw
   word. (4) **Serialization:** the launcher's reporting
   paths execute serially — each consults and updates the
   same two flags on one execution path, so no concurrent
   path can inspect a stale flag value and begin a second
   reap or a second transmission. A path that finds
   `reaped` already true uses the held word and never
   waits again; a path that finds `sent` already true
   transmits nothing. The class-T path and the ordinary
   paths are one reporting machinery entered from
   different events: whichever runs first discharges the
   report, and the others become reporting no-ops, their
   remaining duties proceeding unchanged. **The reap
   inventory and the two dispositions (Rev 21).** The
   sites divide by what happens to the held word.
   **Reporting reaps** discharge it exactly once — in an
   ABORT (R-3; that path's complete report, `sent` never
   set on it) or in the one STATUS (R-6, R-7, R-8).
   **Terminal cleanup reaps** (R-1, R-2, R-4, R-5) are
   followed immediately by the launcher's exit; `sent`
   stays false for the whole of that process and no STATUS
   is ever sent. R-1's ABORT carries the word as
   launcher-reported detail (Stage 4); R-2 transmits
   nothing after its reap; R-4/R-5 hold the word locally
   and their ABORT, where sent, carries the failure reason
   only. An ABORT is never a STATUS transmission and never
   sets `sent`, on any path.

   | Site | Where | Word disposition | What follows |
   |---|---|---|---|
   | R-1 | Stage 4 establishment failure (WNOHANG check returns the child) | carried in the ABORT detail, recorded launcher-reported; supervisor's own observation UNKNOWN | launcher exits; no handoff |
   | R-2 | HANDOFF_ACK refusal codes 1–2 | held, never transmitted | launcher exits non-zero at once |
   | R-3 | HANDOFF_ACK code 3 | carried in the ABORT (`CHILD_TERMINATED_AT_HANDOFF`; its complete report) | launcher exits after the ABORT |
   | R-4 | Settling Window 1 | held locally, never transmitted; ABORT carries the reason only | launcher terminates itself |
   | R-5 | Settling Window 2 | held locally, never transmitted; ABORT carries the reason only | launcher terminates itself |
   | R-6 | Class-T receipt (this Stage) | the one STATUS | per the class-T rules |
   | R-7 | Stage 6 gate-write failure | the one STATUS | per Stage 6/Stage 8 |
   | R-8 | Stage 8 collection | the one STATUS | closure per Stage 8 |

   **The reachability proof.** R-1, R-2 and R-3 occur
   before any later reporting path exists. R-1, R-2, R-4
   and R-5 terminate the launcher after their cleanup;
   R-3 terminates after its ABORT report. No cleanup path
   returns to settling, release, or another reporting
   path. Each cleanup site is therefore reachable only
   while `reaped` is still false — the pre-handoff sites
   precede any possible reap, and the settling windows'
   only earlier reap-capable events are those pre-handoff
   sites, every one of which exits — so at most one
   cleanup reap can ever execute, and it ends the only
   process that could reap or transmit again. `sent`
   remains false on every cleanup path, and the invariant
   `sent` ⇒ `reaped` is untouched by all of them.
   (Non-reaping waits — `WNOHANG` checks returning 0, the
   pidfd readiness polls — set nothing; a `WNOHANG` check
   that returns the child **is** R-1. The supervisor's own
   cleanup reap of a refused duplicate is outside this
   contract **by process**: a different reaper, recorded
   supervisor-side, which can never touch the launcher's
   flags.) On receiving a
   class-T ABORT it acts by those flags. If `sent` is
   already true, the ABORT is a reporting no-op: no second
   STATUS, no second reaping; the launcher completes its
   exit. If `reaped` is true and `sent` false, it sets
   `sent` and transmits its one STATUS from the held raw
   word. If **both are false — the ordinary case** — the
   launcher **abandons the settling sequence at once**: it
   sends no GATE_READY from that point (a GATE_READY
   already sent stands, and is the supervisor-side inert
   case), writes no gate byte, and performs no release
   action of any kind. It then reaps exactly once with a
   **blocking** `waitpid()` on the child — blocking is
   correct here, because the supervisor's class-T
   commitment rests on termination already observed on the
   pidfd: the wait is for the status, not for the death.
   An `EINTR` return is retried and sets nothing. On
   success it confirms the returned PID is the child's
   PID, sets `reaped`, and holds the raw word; then it
   sets `sent` and transmits exactly one STATUS carrying
   the word **verbatim** — validation of record is the
   supervisor's under the strict encodings; the launcher
   neither edits, decodes-and-re-encodes, nor withholds
   the word. **`sent` is set before transmission in every
   branch**: the flag records commitment to the single
   transmission, not successful delivery, and a failed
   transmission never causes a second STATUS attempt. On
   any other `waitpid()` error — including `ECHILD` while
   `reaped` is false, a contradiction with its own state,
   or a returned PID that is not the child's — the
   launcher holds no valid status: it sends **no STATUS**,
   invents no word, sets nothing, and exits non-zero; the
   supervisor's side closes on the resulting EOF under
   the PRE_RELEASE_LAUNCHER_LOST outcome below. After the
   STATUS, or the error exit, the launcher's work for the
   attempt is done and it exits; no path from class-T
   receipt leads back to settling, GATE_READY, or release.
   **Stage 6 — Release.** The supervisor, on `GATE_READY`,
   re-checks its own Stage 0 preconditions (the run's
   record expectations in place) **and performs the
   pre-RELEASE readiness guard**: it zero-polls the pidfd
   under the readiness contract. If the poll reports the
   descriptor readable, RELEASE is **not sent** — the
   pre-release termination path runs (class-T `ABORT`).
   If the poll fails closed, RELEASE is **not sent** and
   the supervisor sends a class-F `ABORT` with reason
   `READINESS_UNVERIFIABLE`. Only on a clean guard does it
   send `RELEASE`. **The guard's limit, stated plainly:**
   the poll and the send are not atomic — a child can
   terminate after a clean final poll and before RELEASE
   is transmitted. The record therefore holds three facts
   separately and never merges them: the last readiness
   observation (not terminated, at its instant); RELEASE
   sent (the supervisor's own act, proven); termination
   observed (the pidfd, at its instant). **The child's
   actual termination time relative to RELEASE is UNKNOWN
   unless independently established**; termination first
   observed after RELEASE enters the S6 handling and does
   not prove the child died after RELEASE. Termination
   observed while in S6 is closed by the Stage 8 machinery
   on exactly those facts. The launcher's gate write has
   exactly three outcomes: it returns **1** → the byte was
   written; the launcher closes the write end and sends
   `GATE_ACTUATED`. It fails with **EPIPE** → the read end
   is closed, which in the pinned child sequence happens
   when the child has terminated; the launcher sends
   `GATE_WRITE_FAILED` (error class 1), then reaps and
   reports under the shared-flag contract (Stage 5): if
   `reaped` is false it `waitpid()`s and sets `reaped` on
   the confirmed reap; if `reaped` is already true it uses
   the held word; it then sets `sent` immediately before
   transmitting its one `STATUS`, and transmits nothing if
   `sent` is somehow already true. It fails with **any other error**,
   or returns 0 (a one-byte pipe write is atomic — 1 or an
   error; anything else is itself a failure) → the same
   `GATE_WRITE_FAILED` path, error class 2 with the raw
   errno recorded. **A failed write is never actuation**,
   and `GATE_ACTUATED` is sent only on the return-1 path.
   `GATE_ACTUATED` asserts **exactly** that the launcher
   wrote the byte; it is not proof the harness started.
   **The evidence discipline of the write-to-acknowledgement
   window (Rev 17):** if the launcher writes the byte and
   dies before `GATE_ACTUATED`, the supervisor's record
   shows, as separate facts, never merged — RELEASE sent:
   **PROVEN** (its own act); gate-byte actuation:
   **UNKNOWN**; child termination: **PROVEN only if
   observed through the pidfd** — and that observation is
   the same whether the child was released or not, so
   **pidfd observation is never used to establish
   release**; harness execution: **UNKNOWN** unless
   separately evidenced; terminal classification:
   **UNRESOLVED**. The acknowledgement exists precisely to
   make this uncertainty explicit; it cannot eliminate the
   window. **Stage 7 — The run.** On the release byte the
   child execs the harness at the fixed path — the exec
   itself closes the gate read end (`O_CLOEXEC`), so the
   gate does not exist in the harness. From the arming
   onward, the child's `PR_SET_PDEATHSIG` backstop covers
   the launcher's death at **any** point — mid-failure,
   mid-cleanup, after release with the harness running:
   the kernel terminates the child directly, and no process
   needs signal authority over it. The intervals the
   backstop cannot cover are those before the arming
   completes, and Stage 3's two comparisons close them.
   This is a kernel-level guarantee **behind** the gate's
   end-of-file path, not a replacement for it. **The
   residual, stated plainly (Rev 05, carried):** if a child
   were to disobey the gate's end-of-file while the
   launcher lives, no unprivileged mechanism remains to the
   launcher, and this design does not assume one; the case
   is excluded **by construction** — the pinned child
   sequence has exactly two post-read branches — not
   handled by authority. The supervisor observes the run
   through the record file and the pidfd only; it computes
   every committed value itself, from the record file,
   which it reads directly (points 5–8). **No successful
   issuance of any kind follows a launcher loss** — Stage 9
   governs what the record may say instead. **Stage 8 —
   Termination and closure.** The launcher `waitpid()`s for
   the child — without `WUNTRACED` or `WCONTINUED`, so a
   stopped or continued status cannot honestly arise — and
   sends `STATUS`: payload child_pid and the **raw
   wait_status word**, verbatim. The reap and the report
   run under the shared-flag contract (Stage 5): if
   `reaped` is false, the confirmed reap sets `reaped` and
   the word is held; if `reaped` is already true, the held
   word is used and no second wait is performed; `sent` is
   set immediately before the transmission, and the STATUS
   is transmitted exactly once. **When Stage 8 is reached
   with the report already discharged** — the class-T
   receipt action or the gate-write-failure path having
   reaped and reported — Stage 8 performs **no second
   reap and no second STATUS**; its closure duties proceed
   on the facts already held. The supervisor validates
   the STATUS under the strict encoding rules below; a
   correctly framed packet is not automatically a valid
   terminal report. **Closure requires the consistent pair**
   {one valid STATUS} + {pidfd termination observed}, in
   either arrival order; neither alone closes. On closure
   the supervisor writes the run's terminal event from
   those facts and sends `STATUS_ACK`; entry into the
   closed state (S9) is defined by the terminal facts plus
   the completed record — **never by ACK delivery**, whose
   outcome is recorded separately (`ACK_DELIVERED` or
   `STATUS_ACK_UNDELIVERABLE`). **Launcher-exit
   observation:** channel EOF is recorded **whenever it is
   observed**, with the state at observation, as
   `LAUNCHER_EXIT_OBSERVED`, and an observation once made
   is retained for the whole session. Only if EOF has
   **not** been observed by S9 entry does the close-out
   window run: **CLOSE_OUT_WINDOW = 5 seconds** from S9
   entry; EOF inside it appends `LAUNCHER_EXIT_OBSERVED`;
   expiry appends `LAUNCHER_EXIT_UNOBSERVED` and the
   supervisor closes its channel end. The window is an
   observation bound on a supplementary session entry
   only: S9 closure is never reopened, delayed, or
   invalidated by either outcome.
   **Stage 9 — Failure branches and the reaping contract.**
   The branches are stated as the supervisor's record in
   each case; facts are never merged and no classification
   is invented. **Launcher lost before the handoff:**
   launcher loss PROVEN (channel EOF); child release NOT
   RELEASED (protocol fact: RELEASE was never sent); child
   termination **UNKNOWN** — the supervisor holds no pidfd
   and has no independent observation; the expected
   PDEATHSIG consequence is recorded as **DESIGN
   EXPECTATION**, not as termination evidence; issuance:
   none. **Launcher lost after RELEASE, before
   GATE_ACTUATED:** the Stage 6 record (actuation UNKNOWN,
   classification UNRESOLVED). **Launcher lost after
   GATE_ACTUATED:** actuation PROVEN; termination per the
   pidfd if observed; exit status UNKNOWN without STATUS;
   reporting failure PROVEN; classification **UNRESOLVED**
   — never CRASH by default. **Launcher lost after STATUS:**
   closure proceeds per Stage 8 (the facts may already be
   complete; the ACK outcome is recorded as it falls out).
   **Supervisor lost:** the PDEATHSIG cascade — launcher
   armed against the supervisor (point 2), child armed
   against the launcher (Stage 3) — is the DESIGN
   EXPECTATION for both deaths; what the record may state
   as fact at the next start is only: SUPERVISOR_LOST, the
   issuance still open and UNRESOLVED, and any observations
   made after restart. No termination is back-filled as
   fact from the expectation. **Reaping after parent death
   — the contract.** The launcher is the child's sole
   `waitpid()` reaper **while it lives**. When the launcher
   dies, the orphaned child is reparented by the kernel to
   the nearest designated subreaper ancestor, or, if none,
   to PID 1 of the PID namespace; that external reaper
   performs the `waitpid()`. The supervisor never reaps,
   never holds `PR_SET_CHILD_SUBREAPER`, and never becomes
   the child's parent — Option A is not Option B by any
   route — and the supervisor's termination evidence
   remains the pidfd alone: **a pidfd observation is never
   proof of reaping**. The expected reaper is a **SPECIFIED
   DEPENDENCY, not yet a verified environmental fact**:
   **PID 1 of the room's PID namespace**. What PID 1
   actually is in the room (its `/proc/1/comm`, read
   verbatim), the namespace relationship, and the observed
   parent transition are Batch 4 demonstration evidence,
   captured when the demonstration runs; the expectation
   holds only if **no** ancestor between the launcher and
   PID 1 — supervisor, session leaders, tmux, sshd — is a
   designated subreaper, and that absence is inspected by
   the kernel's own naming: in the demonstration, the
   orphan's **new parent PID is read from
   `/proc/<child>/stat`** after the launcher's death and
   before the child's termination. **The demonstration
   passes only on the conjunction:** (a) the new ppid
   observed equals 1 while the child lived — any other
   receiver is a gate failure pending design review, since
   an unnamed reaper is not a contract; (b) child
   termination observed on the instance-pinned pidfd;
   (c) the child's `/proc` entry **disappearing** — reaped;
   a zombie's entry persists — within the pinned bound
   **REAP_BOUND = 5 seconds** of the termination
   observation. Disappearance alone proves nothing
   (namespace teardown or PID churn could mimic it); the
   pass rests on the conjunction, in that order. If the
   expected reaper is unavailable or does not reap within
   the bound — a persistent zombie — the result is a
   **HARD GATE FAILURE**: the environment does not meet
   the dependency, the run halts, and no one remedies it
   by reaping from the supervisor. The failure is recorded
   with the observed ppid and timings.
   **The protocol, specified.** *Transport:*
   `SOCK_SEQPACKET` over the socketpair created in point
   2 — message boundaries preserved; exactly one protocol
   message per packet; packets are fixed-format and at
   most **128 bytes** of payload. *Framing:* byte 0 =
   message code; byte 1 = flags (must be zero);
   multi-byte integers are big-endian; unused payload bytes
   are zero and are checked. A packet arriving with
   `MSG_TRUNC` set, or a receive failing with `EMSGSIZE`,
   is **malformed**. `MSG_CTRUNC` on a receive means the
   ancillary data was truncated: any descriptors actually
   delivered are closed at once, unexamined, and the
   packet is malformed. Descriptors are received with
   `MSG_CMSG_CLOEXEC`. *Ancillary data:* legal **only** on
   `PIDFD_HANDOFF`, carrying **exactly one** descriptor;
   ancillary data on any other message, a second
   descriptor, or a message whose framing is otherwise
   invalid is a **protocol violation** — the descriptors
   are closed immediately, unexamined, and the message
   takes the violation disposition of the state table.
   *Descriptor ownership:* the pidfd is created by the
   launcher (**owner until handoff**); it crosses as the
   sole ancillary descriptor of `PIDFD_HANDOFF` (the
   launcher's copy is closed once the send completes); the
   supervisor's received copy is **adopted** on validation
   success and held in exactly one run-state slot (closed
   on refusal, on validation failure, or at S9 as the
   record closes). The gate pipe is created by the
   launcher; its write end is the launcher's alone until
   Stage 6 closes it; its read end is the child's alone
   and is closed by the exec. The channel ends are owned
   by the supervisor and the launcher respectively, for
   the session's life. *Message catalogue* (code, name,
   direction, payload):
   `0x01 LAUNCH_REQUEST` (supervisor→launcher; run_id,
   expected_supervisor_pid, child uid, child gid) ·
   `0x02 PIDFD_HANDOFF` (launcher→supervisor; child_pid
   u32, child_start_time u64; exactly one ancillary pidfd) ·
   `0x03 HANDOFF_ACK` (supervisor→launcher; code u8 —
   0 = accepted, 1 = identity validation failed,
   2 = target lost, 3 = child terminated; the launcher's
   behaviour per code is specified at Stage 4) ·
   `0x04 GATE_READY` (launcher→supervisor; empty) ·
   `0x05 RELEASE` (supervisor→launcher; empty) ·
   `0x06 GATE_ACTUATED` (launcher→supervisor; empty) ·
   `0x07 STATUS` (launcher→supervisor; child_pid u32,
   raw wait_status u32) ·
   `0x08 STATUS_ACK` (supervisor→launcher; empty) ·
   `0x09 ABORT` (either direction; reason code u8 +
   optional detail; **lifecycle class per the
   terminal-observation rules** — class T for the single
   reason `CHILD_TERMINATED_PRE_RELEASE` sent by the
   supervisor pre-release, class F for every other ABORT).
   Reason codes include at least:
   `CHILD_LOST_IN_ESTABLISHMENT`,
   `CHILD_TERMINATED_PRE_RELEASE`,
   `IDENTITY_RECHECK_FAILED`, `SETTLING_FAILED`,
   `READINESS_UNVERIFIABLE`, `SUPERVISOR_ABORT`. For
   reason `CHILD_TERMINATED_PRE_RELEASE` the detail
   carries the raw wait_status word (u32) when the
   launcher sends it. **For reason
   `CHILD_LOST_IN_ESTABLISHMENT` sent by the launcher
   (site R-1), the detail carries the raw wait_status word
   (u32) always**: the supervisor validates it under the
   same strict encodings as a STATUS word and records it
   as **launcher-reported**; that word is never the
   supervisor's own observation, which for R-1 remains
   UNKNOWN (Stage 4). **For reason
   `CHILD_TERMINATED_AT_HANDOFF` sent by the launcher
   after ACK 3 (site R-3), the detail carries the raw
   wait_status word (u32) always**, validated as for
   STATUS and recorded **LAUNCHER-REPORTED**; the
   attempt's pidfd termination stands recorded
   **SUPERVISOR-OBSERVED** — the separate fact that
   grounded validation step (3) — and the attempt closes
   on {ACK 3 sent + this ABORT received and validated} as
   an aborted launch; no STATUS, GATE_READY or issuance
   may follow ACK 3. The contrast with R-1 is the mirror:
   there, no handoff and no pidfd exist and the
   supervisor's observation is UNKNOWN; here, both facts
   exist and are recorded in their separate classes. No
   other ABORT reason carries a
   wait-status word unless its own text says so;
   settling-failure ABORTs (R-4/R-5) carry the reason
   only ·
   `0x0A GATE_WRITE_FAILED` (launcher→supervisor ONLY;
   error class u8 — 1 = EPIPE, 2 = other — and the raw
   errno u16). *The readiness operation (Rev 18).* One
   operation with two call sites — the S3 validation step
   (3) and the S5 pre-RELEASE guard — and one result
   contract at both. The supervisor polls the held pidfd
   with a zero timeout. **POLLIN ready** → termination
   observed. **No readiness events** → termination not
   observed at that instant (an observation, never a
   liveness proof). **EINTR** → re-poll; an interrupt is
   not a result and changes no state; retries run against
   **READINESS_DEADLINE = 1 second**, measured on
   `CLOCK_MONOTONIC` from the operation's entry (before
   the first poll call), identical at both call sites;
   expiry with no completed poll ends the operation as
   **POLL_INCOMPLETE**. **Any other error return,
   `POLLERR`, `POLLNVAL`, or any event mask other than
   POLLIN alone or no events** → fail closed: at S3, the
   handoff is refused (ACK code 1 class) with the poll
   outcome as the recorded reason, POLL_INCOMPLETE
   included; at the S5 guard, RELEASE is not sent and the
   class-F `READINESS_UNVERIFIABLE` abort path runs, the
   poll outcome recorded. **No polling error, unexpected
   flag, or incomplete poll is ever interpreted as a live
   child**, and no retry count or timeout other than
   READINESS_DEADLINE exists for an implementation to
   choose. *wait_status — strict encoding.* A
   STATUS is a valid terminal report only if its framing
   is valid, its child_pid equals the handoff's, **and**
   its raw word matches **exactly one** of the two accepted
   Linux encodings — bit patterns, not macro resemblance.
   The word is an unsigned 32-bit value as transmitted;
   bits 16–31 MUST be zero in every accepted case.
   **Exited:** bits 0–7 == 0x00; bits 8–15 = the exit code
   (0–255); decoded fact: the exit code. **Signalled:**
   bits 0–6 = signal S, **1 ≤ S ≤ 64** (the pinned kernel's
   signal range, `SIGRTMAX` = 64); bit 7 = the core-dump
   flag, either value accepted and recorded; bits 8–15
   == 0; decoded facts: S and the flag. Signals 32 and 33
   are **not** excluded: glibc reserves them for its own
   signalling interface, but this validator judges a
   **kernel** `waitpid()` result, and no kernel-level
   evidence bars those values from a genuine wait status —
   in-range values are accepted uniformly. Everything else
   is **rejected** as an invalid terminal report —
   including the stopped encoding (bits 0–7 == 0x7F), the
   continued encoding (0xFFFF), signalled form with
   non-zero bits 8–15, any word with bits 16–31 set,
   signal 0 in signalled form, and signal values 65–127
   (outside the kernel's signal range). (The launcher
   waits without `WUNTRACED`/`WCONTINUED`, so stopped and
   continued words cannot arise from an honest `waitpid()`
   in any case.) A rejected STATUS: the raw word is
   recorded verbatim with the rejection reason, the facts
   are kept separate, the classification is UNRESOLVED,
   and the run halts. An accepted STATUS's raw word is
   likewise recorded verbatim alongside its decode.
   *Terminal observations — the complete rules.* Closure
   requires the consistent set {one valid STATUS} + {pidfd
   termination observed}; either may arrive first and
   neither alone closes. Pidfd termination first is
   recorded as the fact TERMINATION OBSERVED (time,
   instance); a valid STATUS arriving afterwards is normal
   and is validated as above. **The ABORT lifecycle
   (Rev 18).** ABORT carries a lifecycle class, determined
   by its reason. **Class T** has exactly one member: a
   supervisor→launcher ABORT with reason
   `CHILD_TERMINATED_PRE_RELEASE`, sent pre-release (S4 or
   S5). Class T supersedes fire-and-close for that send:
   the channel remains open; the launcher is permitted
   **exactly one** further message — its final STATUS;
   the supervisor validates and records it; the channel
   then closes — on the STATUS's recording, on channel
   EOF, or at `PRE_RELEASE_CLOSE_BOUND` = 5 s from the
   ABORT send, whichever first. **EOF, here and
   throughout this protocol, is a drained-channel
   observation (Rev 19):** the supervisor's receive
   processing consumes any queued protocol packet before
   end-of-stream is established — with `SOCK_SEQPACKET` a
   STATUS sent before the launcher closed its end is
   received and processed, never discarded merely because
   EOF/HUP is also observable. If that drained processing
   establishes EOF **without** a STATUS, the attempt
   closes as **PRE_RELEASE_LAUNCHER_LOST**, with exactly
   these recorded facts: launcher loss OBSERVED (the EOF,
   with its time); child termination OBSERVED (the pidfd
   observation that grounded the commitment); exit status
   UNREPORTED; terminal classification UNRESOLVED; no
   issuance of any kind. If neither a STATUS nor such an
   EOF arrives by the bound, the record closes as
   PRE_RELEASE_ABORT_STATUS_UNREPORTED with all held
   facts, and the run halts. The two outcomes are never
   merged: EOF is an observation about the launcher; the
   bound's expiry is the absence of one. Any other message after a
   class-T ABORT, and any second STATUS, is a protocol
   violation, recorded, changing nothing. **Class F** is
   every other ABORT in either direction: fire-and-close
   exactly as before, and a STATUS arriving after a
   supervisor-sent class-F ABORT is recorded as a protocol
   violation and ignored for closure (the attempt is
   terminal). **The class-T decision is keyed only on
   received events.** If a valid STATUS has been
   **received and validated** when the supervisor
   processes a pre-release termination observation, no
   ABORT is sent: the attempt closes on that STATUS. A
   STATUS **received but not yet validated** does not meet
   that condition: the supervisor commits to class T, and
   the already-received STATUS is retained and validated
   as the one permitted class-T STATUS — never discarded,
   never counted twice, never treated as a second message.
   Otherwise the supervisor commits to class T, and a
   STATUS still in transit arrives under class T as the
   one STATUS. The launcher's side is governed by its
   `reaped` and `sent` flags (Stage 5): the class-T
   receipt dispatches on them — already-sent is a
   reporting no-op; reaped-but-unsent transmits the one
   STATUS from the held word; neither is the ordinary
   transition of Stage 5 (abandon settling, one blocking
   reap, one verbatim STATUS, `sent` set before
   transmission in every branch). Event processing yields
   one deterministic outcome regardless of buffering or
   scheduling order.
   `GATE_ACTUATED` and `GATE_WRITE_FAILED` are mutually
   exclusive for one gate attempt: the first received is
   the recorded fact; a contradicting second is a
   violation, recorded, changing nothing. A STATUS
   arriving after a launcher-sent ABORT is unreachable on
   an honest channel (ABORT is fire-and-close); if
   observed, it is a violation, ignored for closure. A contradictory STATUS (child_pid
   mismatch, invalid decode, a second STATUS) is recorded
   as a violation with the packet's facts; the first valid
   STATUS, if any, stands; the classification is
   UNRESOLVED if the contradiction touches the terminal
   basis. **No observation overwrites another;** the
   record keeps each fact with its source.
   **The state table — the authoritative contract.**
   States: S0 SPAWNED (launcher exec'd; LAUNCH_REQUEST not
   yet received) · S1 REQUESTED (LAUNCH_REQUEST validated) ·
   S2 CHILD_ESTABLISHED (launcher has forked the child;
   PIDFD_HANDOFF in flight) · S3 HANDOFF_RECEIVED
   (supervisor holds the descriptor, validation pending) ·
   S4 HANDOFF_ACCEPTED (ACK 0 sent) · S5 SETTLED (GATE_READY
   received) · S6 RELEASED (RELEASE sent) · S7 ACTUATED
   (GATE_ACTUATED received) · S8 STATUS_RECEIVED (valid
   STATUS held; pidfd termination not yet observed) · S8F
   FACTS_COMPLETE (valid STATUS held AND pidfd termination
   observed — the run's closure is DETERMINED by these
   facts from this point) · S9 CLOSED (terminal facts
   complete AND the supervisor's run record written
   complete — defined by the facts and the record, NEVER
   by ACK delivery; the ACK outcome is recorded separately) ·
   SX TERMINAL_RECORDED (aborted / lost / violation; the
   supervisor's record states the facts and the
   classification per Stage 9).

| State | Event (sender→receiver) | Validation | Next | Descriptor result | On failure |
|---|---|---|---|---|---|
| S0 | LAUNCH_REQUEST (S→L) | framing; run-id already argv-validated | S1 | none carried | malformed/EOF → SX: spawn attempt void (the launcher exits; NOTHING was forked) |
| S1 | fork occurs (L internal); PIDFD_HANDOFF (L→S) | — | S2→S3 on receipt | pidfd in flight | launcher internal failure → EOF → SX (Stage 9 pre-handoff facts) |
| S3 | supervisor validates handoff | fdinfo target == child_pid; /proc instance binding; readiness poll: NOT readable; exactly 1 descriptor | S4 on ACK 0 | pidfd ADOPTED into the run's held state | identity fail → ACK 1/2, fd closed → SX (child killed+reaped by launcher per Stage 4 refusal); readiness READABLE → TERMINATION OBSERVED recorded (SUPERVISOR-OBSERVED, via the pidfd), ACK 3, fd closed → SX on receipt and validation of the launcher's ABORT with reason CHILD_TERMINATED_AT_HANDOFF (launcher reaps only — site R-3; the ABORT's raw status word validated and recorded LAUNCHER-REPORTED, never merged with the supervisor's observation; no STATUS, GATE_READY or issuance follows ACK 3); poll failure → ACK 1 class with the poll reason recorded, fd closed → SX (refusal path) |
| S4 | GATE_READY (L→S) | in-state; empty payload | S5 | — | EOF → SX LAUNCHER_LOST (child unreleased; termination per the held pidfd — OBSERVED if shown, UNKNOWN only if not observed) |
| S4 | pidfd termination observed (S, kernel) | instance pinned | stays S4 pending the final report, then SX PRE_RELEASE_TERMINATED | pidfd retained until the record closes | supervisor commits to class-T ABORT (CHILD_TERMINATED_PRE_RELEASE): RELEASE barred for the attempt; a later GATE_READY is recorded and inert; the one STATUS under class T — produced by the launcher's class-T receipt action (Stage 5) unless already held — (received-and-validated rule per the terminal-observation rules, incl. the received-but-unvalidated case) is validated and recorded; EOF established drained-without-STATUS → PRE_RELEASE_LAUNCHER_LOST; neither STATUS nor EOF within PRE_RELEASE_CLOSE_BOUND = 5 s → record closes PRE_RELEASE_ABORT_STATUS_UNREPORTED, run halted |
| S5 | RELEASE (S→L) | supervisor's own Stage 1 preconditions AND the pre-RELEASE readiness guard: poll NOT readable | S6 | — | EOF before RELEASE → SX LAUNCHER_LOST (unreleased); guard READABLE → class-T ABORT path (the S4 termination rule); guard poll failure → NO RELEASE, class-F ABORT READINESS_UNVERIFIABLE → SX |
| S5 | pidfd termination observed (S, kernel) before RELEASE | instance pinned | SX PRE_RELEASE_TERMINATED (via the final report) | pidfd retained until the record closes | as the S4 termination row: class-T ABORT committed, RELEASE barred, one class-T STATUS (per the Stage 5 receipt action) validated and recorded; the EOF-first (PRE_RELEASE_LAUNCHER_LOST) and bounded (PRE_RELEASE_ABORT_STATUS_UNREPORTED) closures apply identically |
| S6 | GATE_ACTUATED (L→S) | in-state; empty payload | S7 | — | EOF first → SX-recorded: actuation UNKNOWN branch (Stage 6/9) |
| S6 | GATE_WRITE_FAILED (L→S) | in-state; error class + errno | stays S6 awaiting STATUS | — | actuation recorded FAILED (launcher-reported); GATE_ACTUATED for this attempt is barred (mutual exclusion — a later one is a violation); closure proceeds on the STATUS/pidfd pair per Stage 8 |
| S6 | pidfd termination observed before any gate report | instance pinned | stays S6 | — | TERMINATION OBSERVED recorded; RELEASE-sent PROVEN and termination OBSERVED stand as separate facts; their relative timing is UNKNOWN and is never inferred; the attempt proceeds per the GATE_ACTUATED / GATE_WRITE_FAILED / EOF rows |
| S7 | STATUS (L→S) — pidfd termination NOT yet observed | framing; child_pid match; strict wait_status decode | S8 | — | EOF without STATUS → facts separated, UNRESOLVED (SX); invalid STATUS → violation, UNRESOLVED (SX) |
| S7 | STATUS (L→S) — pidfd termination ALREADY observed (recorded while in S7) | same validation | S8F | — | invalid STATUS → violation, UNRESOLVED (SX) |
| S7 | pidfd termination observed before STATUS | instance pinned | stays S7; TERMINATION OBSERVED fact recorded | — | (the conditional STATUS rows above then apply) |
| S8 | pidfd termination observed (S, kernel) | instance already pinned | S8F | pidfd retained until S9, then closed as the record closes | — |
| S8 | launcher channel EOF observed | — | NO state change | pidfd RETAINED; the supervisor keeps waiting on it | LAUNCHER_EXIT_OBSERVED recorded at once (state at observation: S8) and RETAINED as the session's exit observation; EOF contributes nothing to closure and blocks nothing — the S8 → S8F → S9 progression proceeds on the pidfd alone. (ACK consequence: the channel is closed, so a STATUS_ACK attempt from here records STATUS_ACK_UNDELIVERABLE.) If pidfd termination is never observed, the run remains open exactly as without the EOF |
| S8F | launcher channel EOF observed | — | NO state change | — | LAUNCHER_EXIT_OBSERVED recorded at once (state at observation: S8F), retained as the session's exit observation; the S8F → S9 closure proceeds normally |
| S8F | supervisor writes the run record complete from the terminal facts | facts = valid STATUS + observed pidfd termination | S9 | pidfd closed as the record closes | — |
| S8 / S8F | STATUS_ACK (S→L) attempt | — | NO state change by itself | — | the ACK outcome is recorded separately, as ACK_DELIVERED or STATUS_ACK_UNDELIVERABLE; closure (S8F → S9) never depends on it and is fully possible when the ACK is undeliverable |
| S8F | ABORT (L→S) | framing | S9 path UNAFFECTED | any attached fds closed unexamined | recorded as PROTOCOL_VIOLATION (the attempt is complete, not aborted — ABORT has no work to do once the terminal facts are held); closure proceeds on the facts; the violation rides in the record |
| S8 (termination NOT yet observed) | ABORT (L→S) | framing | SX | any attached fds closed unexamined | attempt terminal with facts insufficient: classification UNRESOLVED; child governed by PDEATHSIG, observed by pidfd (held) — a later pidfd termination is recorded as a fact but does not reopen the attempt |
| after S9 | launcher-exit observation window — ONLY if EOF has not already been observed | trigger: entry into S9 with no EOF yet observed | session record finalised | pidfd closed at S9 | EOF within CLOSE_OUT_WINDOW = 5 s → LAUNCHER_EXIT_OBSERVED appended; window expires → LAUNCHER_EXIT_UNOBSERVED appended and the supervisor closes its channel end. If EOF was already observed (in S8, S8F, or any earlier state where the table records it), there is NO window and NO UNOBSERVED entry — the retained observation stands. In all cases the window is an observation bound on a SUPPLEMENTARY session entry only: S9 closure is already complete and is never reopened, delayed or invalidated by either outcome |
| any ≤ S8 | ABORT (L→S) (states not covered above) | framing | SX | any attached fds closed unexamined | post-RELEASE ABORT: record ABORT_RECEIVED + facts; classification UNRESOLVED unless STATUS/pidfd facts already suffice; child governed by PDEATHSIG, observed by pidfd if held |
| any ≤ S8 | ABORT (S→L) | framing | SX | — | attempt terminal supervisor-side; a later STATUS = violation, ignored for closure (class F; the sole class-T exception is the S4/S5 termination rows above) |
| any | message not permitted in this state | framing valid but transition invalid | — | **attached descriptors closed immediately, unexamined** | PROTOCOL_VIOLATION: pre-release → abort to SX; post-release → facts separated, UNRESOLVED, halt |

   **The ordering is the invariant (Rev 04, restated for
   the three-process model): the supervisor's independent
   observation and issuance capability is fully established
   — the pidfd validated and held, the launcher settled and
   dropped, the gate still closed — before the subject
   begins work; there is no interleaving in which the
   harness executes while the supervisor side has failed.**
   Every committed value is computed, and every receipt
   written, by the supervisor programme running as
   `pilot-supervisor`. The harness cannot ask the
   supervisor to issue a receipt over values the harness
   supplies: **the supervisor computes every committed
   value itself**, from the record file, which it reads
   directly (read access to `runs/` granted to
   `pilot-supervisor` for this purpose, read-only).

   **Pre-release termination demonstrations (Rev 18;
   Batch 4 gate evidence, each with its expected
   supervisor record entries as part of its pass
   condition).** **D-T1 — termination before handoff:**
   the test build's hold interposes between the launcher's
   WNOHANG observation and the supervisor's validation
   while the child is made to terminate; expected: the
   identity checks pass, the readiness check fires, ACK
   code 3, TERMINATION OBSERVED recorded at validation,
   the launcher reaps, its ABORT carries a strictly valid
   raw status, no GATE_READY, no issuance. **D-T2 —
   termination during settling:** the launcher is held
   before GATE_READY and the child is terminated after
   ACK 0; expected: the supervisor observes via the pidfd,
   commits to the class-T ABORT, no RELEASE ever appears
   in the channel log, the launcher's one STATUS —
   produced by its class-T receipt action (Stage 5) — is
   recorded as its final report, the attempt closes
   pre-release with the specified facts. **D-T3a —
   termination before the final poll:** GATE_READY
   delivered, the child terminated in S5 before the guard;
   expected: the ABORT path with the STATUS produced by
   the same receipt action, and the channel log proves no
   RELEASE packet was ever sent. **D-T3b — termination in
   the poll-to-send interval:** the child is terminated
   after the guard's clean poll, before or as RELEASE is
   transmitted; expected: RELEASE recorded sent,
   termination recorded observed, their relative timing
   recorded UNKNOWN, the attempt proceeds on the S6 path,
   and no record anywhere claims the child was alive at
   transmission. **D-T4 — the gate-write boundary:**
   RELEASE delivered; the launcher's write is held by the
   test hook while the child terminates; expected: the
   write returns EPIPE, the launcher survives (SIGPIPE
   ignored — evidenced by what follows), GATE_WRITE_FAILED
   (class 1, errno EPIPE) is received, GATE_ACTUATED is
   never received, STATUS follows, actuation is recorded
   FAILED, and the record closes on the STATUS/pidfd pair
   with no fact rewritten. **D-T5a — the EOF-first case
   (Rev 20):** during settling, after ACK 0, the child is
   terminated and the launcher is made to exit **without
   transmitting STATUS** (terminated by the harness, or
   driven out through its waitpid-error exit — either
   route, provided no STATUS packet is ever sent).
   Expected record: the pidfd termination observation
   stands; the supervisor's receive processing drains the
   channel — no queued packet exists to consume — and
   establishes EOF **before `PRE_RELEASE_CLOSE_BOUND`
   expires**; the attempt closes as
   **PRE_RELEASE_LAUNCHER_LOST** with exactly its facts
   (launcher loss OBSERVED with the EOF's time; child
   termination OBSERVED; exit status UNREPORTED; terminal
   classification UNRESOLVED; no issuance), the close
   recorded as **EOF-driven**, the EOF observation carried
   as the closing event — which is what distinguishes it
   from the bound-expiry outcome. The demonstration also
   verifies, from the channel log and the launcher-side
   evidence, that **no STATUS was transmitted** — not
   merely that none was received. No RELEASE or gate
   action of any kind appears. **D-T5b — the queued-STATUS
   control (Rev 20):** the launcher transmits its STATUS
   and closes its channel end immediately, so the packet
   sits queued while HUP/EOF is already observable at the
   supervisor. Expected record: receive processing
   consumes the queued STATUS first; the STATUS is
   validated and recorded as the attempt's final report;
   the attempt closes on the STATUS and **not** as
   PRE_RELEASE_LAUNCHER_LOST. A record that discards the
   queued STATUS, or that closes launcher-lost despite it,
   fails the demonstration. **D-T6 — the ACK-3 packet and
   record (Rev 22):** the child is terminated inside the
   handoff window so validation step (3) reads the pidfd
   terminated. Expected record: ACK 3 sent; the launcher
   reaps exactly once and sends ABORT with reason
   `CHILD_TERMINATED_AT_HANDOFF`, its detail carrying the
   raw word; the supervisor validates the word and records
   it **LAUNCHER-REPORTED**; the pidfd termination stands
   recorded **SUPERVISOR-OBSERVED**; the attempt closes as
   an aborted launch on the pair, the packet and the
   record agreeing. The demonstration also **rejects**:
   an ABORT with a wrong reason or wrong direction; a
   missing, malformed, or encoding-invalid word; a record
   that lets the launcher's report replace the supervisor's
   observation, or the observation replace the report; a
   STATUS sent after the ABORT; closure recorded before
   the ABORT is received and validated; and any GATE_READY
   or issuance after ACK 3. Any of those outcomes fails
   the demonstration.

4. **Alex's five points, answered.** (i) **Who may start a
   process as `pilot-harness`:** only the launcher, and only
   via its compiled-in fixed path — no account, including
   `pilot-supervisor`, holds a general ability to become, or to
   spawn as, `pilot-harness`. (ii) **What constrains the
   launcher from modifying or issuing commitments:** while
   privileged, the launcher **has root's filesystem
   authority** — this spec does not claim otherwise, and any
   earlier phrasing suggesting it lacks the OS-level
   *ability* to reach `commitments/` is withdrawn. The
   defensible claim is about its pinned implementation, not
   its authority: its code contains **no commitment-writing
   operation and no path to the `commitments/` store**, it
   performs no file writes while privileged, and it drops
   privilege before the supervisor performs any commitment
   work. The constraint relied on is therefore the smallness
   and pinnedness of that code — which is exactly why the
   launcher stands named in the trusted computing base
   (point (iv)). (iii) **How termination
   is independently observed:** the launcher is the child's
   parent in the OS process tree; its `waitpid()` returns the
   exit status or the killing signal directly from the
   kernel, and it reports that raw status to the supervisor
   over the status channel (point 3, Stage 8), while the
   supervisor independently observes the child's termination
   through the pidfd it holds — a crash is observed, not
   announced, on two independent kernel-sourced paths.
   (iv) **How the
   threat model is preserved:** the launcher is a named,
   minimal addition to the trusted computing base — pinned
   source, one fixed action, no inputs beyond the validated run
   identifier, no shell, no network. The comparison with the alternatives is stated
   honestly (Rev 12, Claude's finding 4). The mode-`4710`
   launcher is itself a **standing privilege**: the
   `pilot-supervisor` identity can invoke it outside any run,
   exactly as a sudo rule would be invocable — the earlier
   rationale claimed a distinction there that does not exist,
   and it is withdrawn. The honest trade: a **narrow sudoers
   entry is a smaller trusted base than custom root code** —
   established, widely audited policy machinery against new
   privileged code written for this pilot. The launcher is
   nevertheless chosen, for one reason: it performs the **whole
   custody sequence** — the fixed spawn, the transitions, the
   gate — as **one constrained program**: a single fixed
   operation, no arguments beyond the validated run identifier,
   no shell, and **no general exec path**. A sudo rule, by
   contrast, confers a general launch path onto **whatever
   programme it names**: the custody sequence would then live in
   that programme, and which interpreter and which code actually
   run under the privilege becomes a property of the named path
   and its own protections — reintroducing the interpreter
   ambiguity the exec condition of point 3 (Rev 07) exists to
   exclude. The cost is named plainly: **custom root code is
   the larger trusted base**, carried knowingly, mitigated by
   the launcher's pinned source, by its behaviour and interface
   frozen at Batch 0 (Rev 12), and by the code-order inspections
   of demonstrations (vii) and (viii) — not by any claim that
   the alternative was wider; a root daemon would add a
   persistent privileged service with an IPC surface. The
   launcher exists for the milliseconds of one spawn and then
   holds no privilege at all — but while it holds it, that
   privilege is root's, filesystem authority included, and is
   acknowledged as such ((ii) above). The standing prohibition is
   unchanged and applies to the launcher too: **nothing in this
   design defends against the machine's operator or root**,
   and no artefact may claim otherwise. (v) **How the
   separation is tested:** demonstrations (v)–(ix) in the
   SE-7 list below — execution refusal as the harness
   identity, allowlist refusal, a mid-run attempt by the
   harness to invoke the launcher, descriptor isolation under
   a deliberately inherited writable descriptor,
   retained-descriptor destination verification,
   group-separation, setuid-precondition, and
   capability-state evidence (Rev 10),
   observed-uid evidence from a test run, and the
   launch-handshake tests: induced parent failures in both
   failure windows (Rev 05) — before the parent's drop takes
   effect, and after it, where the gate's end-of-file, not a
   signal, ends the waiting child — a parent death before
   the child's first instruction, a parent death before
   release, a parent death during the child's setup window,
   and a parent death after release, ended by the backstop
   armed after the child's own drop (Rev 06) and proven
   against the expected parent identity captured before
   the fork (Rev 07), and executable identity continuity —
   a substituted or redirected exec target caught between
   verification and the pre-release re-check (Rev 08;
   scope of the claim corrected, Rev 09) — each proven to
   leave no executing harness.

**Descriptor separation — path permissions are not enough
(Rev 03).** Filesystem permissions govern access by path; they
do **not** revoke access through an already-open file
descriptor inherited across `fork()` and `exec()`. A child
that inherited a writable descriptor to `commitments/` could
write through it whatever the directory's mode says, and the
privilege drop in point 3 does not by itself close that route.
The custody design therefore establishes **descriptor
separation** alongside path separation, in three parts. The
child part is point 3's exhaustive pre-exec close (allowlist:
fds `0`/`1`/`2` at their declared destinations, and the gate
read end for the pre-exec window only). The destination and
verification part (Rev 04) is stated below. The supervisor half is
an invariant of the supervisor's own design, not a hope about
its behaviour: **the supervisor holds no open writable
descriptor to `commitments/` or to `issuance-record.jsonl` at
the moment it invokes the launcher** — commitment-store files
are opened per write, written, and closed, and are never held
open across a launch. The general rule all three parts
instantiate: **the harness child must not inherit any
supervisor-owned writable handle that bypasses the custody
boundary.** It is demonstrated adversarially in SE-7 (vi).

**Declared destinations of the retained descriptors
(Rev 04).** The exhaustive close retains fds `0`/`1`/`2`;
retention is only as good as what those descriptors point
at — a standard descriptor redirected to a protected file
would remain a live route in, past the close of everything
from fd `3` up. The destinations are therefore **declared**,
here: fd `0` is `/dev/null`, or a read-only pipe; fds `1`
and `2` are pipes whose read ends are held by the supervisor
and drained into the run log, or a single designated
append-only log file — opened with `O_APPEND` — in the
supervisor-owned **run-log area**, a tree outside
`commitments/` and outside every other protected store.
**No retained descriptor may be a file inside
`commitments/`, a commitment receipt, or
`issuance-record.jsonl`, and none may be a writable handle
to any of them**, in any mode. Before invoking the launcher,
the supervisor **verifies** what it is about to pass on: for
each of fds `0`/`1`/`2` it resolves the descriptor's
destination (the `/proc/self/fd/` target) and reads its
access mode (`fcntl(F_GETFL)`), and asserts that destination
and mode match this declaration. Where a declared
destination is a pipe, that match must establish the
pipe's **identity** — the descriptor is the actual pipe
end whose other end the supervisor itself holds and
drains, one of the supervisor's own held pipe descriptors
— and not merely that the `/proc/self/fd/` target has the
form `pipe:[...]` (Rev 05; Alex's noted implementation
detail on this accepted material, pb-mweedh0x — a
clarification of how the verification is performed, not a
change to what is verified). On any mismatch — or any
destination it cannot resolve and classify — the launch
**does not happen**: the supervisor aborts the launch and
records the abort (run identifier, offending descriptor,
observed destination and mode) in the run log. The child-side
post-drop state inherits only what passed this check.

**The exec condition, verified at build time and again
before every launch (Rev 07); identity continuity
between verification and execution (Rev 08).** Point 3's three-part
exec condition — the fixed harness executable is **not
setuid, not setgid, and without associated file
capabilities** — applies to the **actual executable the
kernel invokes**: where the fixed harness path is a
script, the executable the kernel runs is its
interpreter, and the condition applies to that
interpreter binary as it stands on the build machine.
At build and freeze time — at the Batch 0 re-freeze, and
at every later point where the executable or its
interpreter is produced, replaced, or pinned — the mode
bits and the capability set of the executable (and of
any such interpreter) are **checked and recorded in the
gate evidence**: the `stat` mode and the `getcap`
output, preserved as read. And the supervisor's
pre-launch verification above **re-checks** them **for
the specific launch**, alongside the descriptor
destinations: before invoking the launcher, the
supervisor stats the executable (and any interpreter)
and asserts that neither the setuid nor the setgid bit
is set and that `getcap` reports no capabilities. A
target failing any of the three conditions means **no
launch**: the supervisor aborts and records the abort in
the run log (run identifier, the failing artefact, and
the observed mode and capability set), exactly as for a
descriptor mismatch. A build whose gate evidence lacks
these recorded checks has not established the condition
the backstop's persistence across the exec depends on.

**Identity continuity — the checked object is the
executed object (Rev 08).** The checks above establish
the executable's and the interpreter's properties **at
inspection time**. The launcher, however, executes a
**fixed path**, and a path is a name, not an object:
between a check and the exec, the object the name
resolves to can change — the file or the interpreter
replaced, a symlink repointed, a writable directory
component redirecting resolution — and the child would
then execute an object whose setuid bit, setgid bit, or
file capabilities no check ever saw. The condition above
is therefore bound to the object actually executed by a
three-layer arrangement. **(1) Protected placement.**
The harness executable and any interpreter it runs
through live under a protected installation tree: the
files themselves, and **every directory component of
their resolved paths**, are owned by **root** and are
**not writable by any other identity** — directories
mode `0755` or stricter, the executables root-owned and
not writable by group or other. What that placement
establishes depends on the identity, and the three
classes are distinguished explicitly (claim corrected,
Rev 09). **The untrusted in-model identities** —
`pilot-harness` and `pilot-supervisor` — cannot modify,
replace, rename, or unlink the executable, the
interpreter, or any path component: OS permissions
genuinely prevent it, and for these identities
substitution is not merely detectable; the write access
it requires does not exist. **The privileged launcher**
is a different class, and no OS-impossibility is claimed
for it: in its privileged window the launcher's
effective identity **is** root, root can write
root-owned files and `0755` directories, and OS
permissions do **not** prevent it. The boundary for the
launcher is its **pinned implementation**: the launcher
is trusted TCB code whose specified operation set is
the spawn sequence only — it contains no operation that
modifies, replaces, renames, unlinks, or redirects the
protected tree, and it performs no file writes while
privileged (point 3) — evidenced the same way its other
code properties are: by the source pin, the specified
operation set, and the SE-7 launcher demonstrations.
That is the same footing on which point 4 states the
launcher's authority in its privileged window: the
ability is acknowledged, and the claim rests on the
code. **The operator and root** acting outside the
launcher stand outside the threat model — the standing
limit of this section's threat-model statement — and
layer (3) below addresses their substitutions only as
detection, and only for substitutions landing before
its re-check.
**The capability state the permission claim stands
on (Rev 10).** Layer (1)'s claim for the untrusted
identities is a claim about the operating system's
permission enforcement, and that enforcement is
**discretionary** access control: it does not bind a
process holding a capability that bypasses it. A
process carrying `CAP_DAC_OVERRIDE`,
`CAP_DAC_READ_SEARCH`, or `CAP_FOWNER` — the
bypass-relevant examples — could modify, replace, or
unlink the protected tree whatever its uid and
whatever the tree's ownership and modes, and layer
(1)'s guarantee would be false of it. The guarantee
is therefore claimed only on a **verified** capability
state, and two standing properties frame the
expectation without substituting for the verification.
The exec target's freedom from file capabilities —
the three-part exec condition, verified above — is
why the harness process cannot **gain** capabilities
at the exec; and the launcher's pinned operation set
contains **no ambient-capability raising** (no
`prctl(PR_CAP_AMBIENT)` call), so nothing in the spawn
sequence lifts a capability into the ambient set an
exec would inherit. Point 3 closes the evidentiary
link: after each privilege drop — the child's to
`pilot-harness`, the parent's to `pilot-supervisor` —
the dropped process reads back its own effective,
permitted, and ambient capability sets; the launch
proceeds only if all three are empty for both
processes, failing closed otherwise; and the observed
masks stand in the gate evidence (demonstration
(vii)). The claim rests on the **observed** state at
the point of reliance, not on the intended uid/gid
transition alone.
**(2) Canonical resolution and identity record.** At
each of the checkpoints above — the freeze, and the
supervisor's pre-launch verification — the executable
and interpreter paths are first resolved **canonically**
(every symlink resolved, in the manner of `realpath`),
and the verification records the resolved object's
**identity** alongside the restriction checks
themselves: the device and inode (`st_dev`, `st_ino`),
the mode bits, and the capability set, for the
executable and for the interpreter alike. At the freeze,
the verification additionally records an **audit of
every path component** of both resolved paths — each
component's owner and mode — evidencing layer (1)
rather than presuming it; a component failing the audit
means the freeze does not record the tree as protected
until the defect is corrected. The identity records are
part of the gate evidence and of the run's pre-launch
record. **(3) Pre-release identity re-check.** The
gate's release (point 3) additionally depends on this:
after the child's setup is complete and before the
launcher writes the release byte, the launcher
**re-resolves** the fixed paths and **re-stats** the
resolved objects, and the device and inode, the mode
bits, and the capability set must match the verified
identity records **exactly**. Any mismatch is a launch
failure on the established pattern: the launcher **does
not write the release byte**; the gate cleanup runs per
the applicable failure window — in the ordinary sequence
the launcher has already dropped, so the cleanup is
Window 2's: the gate closed unreleased, the child
exiting on end-of-file, the launcher reaping it; **no
issuance** of any kind occurs; and the supervisor
records the abort in the run log with the **observed
identity values** — the same abort-record discipline as
a descriptor-destination mismatch above. What this
establishes, stated plainly — with the detection claim
scoped to what the re-check can actually see (claim
corrected, Rev 09): a substitution landing **at or
before** this re-check — whenever in the launch it was
arranged — is detected by it: the identity comparison
fails, the release is withheld, and the launch fails
closed, instead of the substituted object passing
silently. A substitution landing **after** this
re-check and before the child's `execve`, by an actor
holding write authority over the tree, is **not**
detected by the re-check, and no detection is claimed
for it: that actor stands outside the threat model, and
against them acting inside the re-check-to-exec
interval itself no arrangement at this layer suffices —
the standing limit, restated because it bounds this
layer too. What protects the final interval is
therefore **not** the re-check. It is the absence of an
in-model writer under layer (1) as there stated:
neither untrusted in-model identity holds write access
to the objects or to any component of their paths
during that interval, and the one participant that ever
held root authority in the launch — the launcher — has
in the ordinary sequence already dropped it before this
point, and its pinned code contains no tree-modifying
operation in any case. So within the threat model the
object the re-check verified is the object the exec
runs; the re-check's own role is to bind the verified
identity to the moment of release against everything
that happened **before** it.

**The descriptor route — considered, not adopted
(Rev 08).** A stronger construction exists: the
supervisor could pass pre-verified **open file
descriptors** for the executable and interpreter, and
the child could execute through them (`execveat` with
`AT_EMPTY_PATH`), eliminating the
verification-to-execution interval by construction —
there is no path left to redirect. It is **not** the
baseline. The harness's invocation is
interpreter-mediated, and the descriptor form for an
interpreter-and-script pair — the interpreter executed
from a descriptor, the script itself delivered to it
without a path the interpreter re-opens, the pair's
identities both pinned — is substantially more
intricate than the single-binary case, and intricacy in
the launcher is its own custody risk. The
protection-plus-identity arrangement above is the
specified mechanism; this paragraph records the
alternative and the judgement, so an inspector may
strike the judgement with full knowledge of what it
trades — but it leaves no choice open to the builder:
layers (1)–(3) are normative.

**The gate read end, reconciled (Rev 04).** The launch gate
(point 3) adds one descriptor to the child's pre-exec
allowlist, and its presence is reconciled with the
declarations above explicitly: the gate read end is a
**read-only** descriptor to a pipe whose write end the parent
holds; it is **not a writable handle to any protected
artefact** — the child cannot write through it at all, and
reading it yields at most the single release byte; it is
created `O_CLOEXEC` and therefore **closed by the exec
itself**, so it does not exist in the harness; and it never
appears in the retained set the destination verification
covers, because it is created by the launcher after the
supervisor's pre-launch check and is gone before the harness
exists. No other descriptor joins the allowlist.

5. **Issuance — START.** When the supervisor observes the
   `RUN_STARTED` event flushed in the record file, it parses
   that event itself, recomputes the genesis hash
   (`prev_event_sha256` preimage: the pinned-input manifest
   block) and the pin-block hash from the file's own bytes, and
   writes the START receipt — `{run_id, kind: "START",
   issued_at_utc, genesis_sha256, run_started_event_sha256,
   pinned_input_block_sha256}` (Harness §2.6) — then appends its
   issuance entry (below).
6. **Issuance — TERMINAL.** When the supervisor observes the
   run's terminal event (`RUN_CLOSED` or `RUN_STOPPED`) flushed
   and the record file closed, it computes `record_file_sha256`
   over the file's **exact bytes as closed**, counts the events
   by its own parse, takes the final event's `event_sha256` from
   its own parse, and writes the TERMINAL receipt
   (`{run_id, kind: "TERMINAL", issued_at_utc,
   terminal_event_type, final_event_sha256, event_count,
   record_file_sha256}`).
7. **Issuance — CRASH.** When the supervisor observes the child
   harness process terminate **without** a terminal event having
   been flushed, it writes **no** TERMINAL receipt and instead
   issues the CRASH receipt over the partial file **exactly as
   it lies** at observation: `{run_id, kind: "CRASH",
   issued_at_utc, record_file_sha256, event_count,
   final_event_sha256, termination_observed}` — the file hash
   over the exact bytes including any incomplete trailing bytes,
   the count of **complete** events from its own parse, the last
   complete event's hash, and its own record of the termination
   (when, and on what basis: the child's exit as witnessed by
   its parent). TERMINAL and CRASH never coexist for one run;
   a run presented with both is a custody finding. No receipt of
   any kind is ever back-filled, edited, or re-issued: a
   correction is a new artefact about the run, never an edit
   (Criteria §7.2(6)).
8. **The issuance record.** Alongside the receipts, in the same
   supervisor-owned tree, the supervisor keeps its append-only
   **issuance record** (`issuance-record.jsonl`): one entry per
   issuance, written by the supervisor at the moment of
   issuance — `{run_id, kind, issued_at_utc, receipt_sha256}`.
   It is written by the supervisor only; the harness has no
   write path to it (same ownership and permissions as the
   receipts), and no agent, tool, or seat may write it (Ben's
   index rule; Harness §2.6). It is not an index: it is the
   supervisor's own account of its own acts, and it enumerates
   nothing outside the commitments it issued.
9. **Examiner verification.** The examiner (§3.7) verifies every
   receipt relied on **against the issuance record** (Harness
   §7 step 0): a receipt with no corresponding entry, or whose
   hash differs from its entry, is not evidence — it is a
   custody finding. Replay begins at the anchor, always.

**Threat model, stated honestly.** This custody design defends
the anchor against the harness — and against any agent, tool,
seat, or subject acting through the harness's privilege
boundary. It does not defend against the machine's operator or
root account, who stand outside the pilot's threat model (§2.6
frames the defect as "anyone with write access to the whole
record file"; the anchor's purpose is that the *harness* cannot
rewrite evidence and anchor together). A deployment claiming
operator-level adversaries would need a stronger form (e.g.
receipts countersigned to storage the operator cannot alter);
that claim is **not** made here and must not be made for this
build.

**How SE-7's four proof obligations are demonstrated** (Harness
§4.5 SE-7; §5 gate G3):

- **(i) The harness cannot write, replace, or delete receipts.**
  By inspection: no code path in the built harness references
  `commitments/` for writing. By adversarial test, executed **as
  the `pilot-harness` identity** from inside the harness's own
  privilege boundary: attempts to create a file in
  `commitments/`, to overwrite a receipt, to delete a receipt,
  and to append to the issuance record must **all fail at the OS
  boundary** (permission denied), and the failures are preserved
  as test evidence. A test that only shows harness code
  *declining* to write does not satisfy this obligation — the
  inability must be the OS's, not the code's politeness.
- **(ii) The supervisor independently records START, TERMINAL,
  and CRASH.** By inspection of the supervisor program: every
  committed value is computed by the supervisor from its own
  read of the record file; no issuance path accepts a hash,
  count, or event value from the harness. By test: a harness
  build variant (scratch context) that writes a falsified
  `RUN_STARTED` pin block produces a START receipt over the
  falsified block's actual bytes — the supervisor commits what
  the file says, never what the harness claims — and the
  discrepancy is then a replay finding, exactly as designed.
- **(iii) The separation is demonstrated, including the crash
  case.** The interrupted-write crash test (§5 gate G2) is the
  demonstration: harness killed mid-append → CRASH receipt over
  the partial file as it lies → no TERMINAL receipt → issuance
  entry present. Plus the between-steps crash case (kill at a
  step boundary) for completeness of the same obligation.
- **(iv) The examiner verifies the issuance record.** The replay
  implementation (§3.7) performs issuance-record verification as
  step 0 by construction; the gate evidence includes a negative
  test: a receipt file planted in `commitments/` without an
  issuance entry (planted under the operator's authority, in a
  scratch commitments tree) must be rejected by the examiner
  tooling as a custody finding, not accepted as an anchor.
- **(v) The launcher separation (Rev 02).** By adversarial
  test: the launcher invoked **as the `pilot-harness`
  identity** fails — it is not executable by that identity
  (permission denied at the OS boundary); the launcher invoked
  by `pilot-supervisor` with **any non-allowlist programme or
  argument shape** refuses and spawns nothing; a harness
  process, **mid-run**, attempting to invoke the launcher to
  spawn a second process fails at the OS boundary, and the
  run's own evidence shows the attempt changed nothing. (The
  commitment forgery, replacement, and deletion attempts as
  `pilot-harness` remain obligation (i)'s tests.) By
  observation evidence: a test run's preserved artefacts
  include the supervisor's own record of the harness child's
  uid/gid as observed from the OS (the child's `/proc` status,
  read by the post-drop parent) — the child ran as
  `pilot-harness`; the witnessing parent ran as
  `pilot-supervisor`.
- **(vi) Descriptor isolation (Rev 03; destinations
  Rev 04).** By adversarial scratch test: the launching
  process deliberately holds an open **writable** descriptor
  to a scratch commitments-like file at fork time — the
  hazard, arranged on purpose. After the launch, the
  harness-identity child attempts to write through **every**
  inherited descriptor number it can probe. The test passes
  only if no inherited descriptor is usable for writing — the
  allowlisted `0`/`1`/`2` excepted, in their declared
  standard roles only — **and** the scratch file is
  byte-unchanged. This instantiates the general rule of
  §3.5's descriptor-separation block: the child must not
  inherit any supervisor-owned writable handle that bypasses
  the boundary. A test in which the hazard was never actually
  arranged does not satisfy this obligation.
  **Retained-descriptor verification (Rev 04):** the same
  test run also records, from inside the child, the resolved
  destinations (`/proc/self/fd/` targets) and access modes of
  the retained fds `0`/`1`/`2`, and asserts each matches
  §3.5's declared set — and the **negative arrangement**:
  standard output deliberately pointed at a scratch protected
  file before launch, which the supervisor-side pre-launch
  verification must catch; the launch is refused, no harness
  process exists, and the abort is recorded with the
  offending descriptor and its observed destination and mode.
  A test that verifies only the close of descriptors `3` and
  above does not satisfy this obligation.
- **(vii) Group separation and setuid preconditions
  (Rev 03); capability state of the dropped processes
  (Rev 10).** By operating-system evidence: the group
  membership of both accounts is read from the OS (`id` /
  `getgrouplist`, or `/etc/group`) and preserved in the gate
  evidence — `pilot-harness` must not appear in the
  `pilot-supervisor` group, and `pilot-supervisor` must not
  appear in any group conferring `pilot-harness` privilege.
  If the separation does not hold, the custody evidence
  **fails**: the launcher's group-execute control would not
  limit invocation to the intended identity. By probe:
  before the custody design is relied on, a probe invocation
  of the launcher on the build host (supported OS: Linux)
  must observe effective uid `0` inside the privileged
  window, and the checks for the conditions that silently
  defeat setuid — the launcher's filesystem mounted `nosuid`,
  an inherited `no_new_privs` flag — are recorded with it.
  **If the probe or any check fails, the build stops; there
  is no fallback to a weaker launch arrangement.**
  **Capability state of the dropped processes
  (Rev 10).** The gate evidence for the launcher tests
  must also include the **observed capability state of
  both dropped processes**: the `CapEff`, `CapPrm`, and
  `CapAmb` values recorded by point 3's read-backs for
  the child running as `pilot-harness` and for the
  parent running as `pilot-supervisor` — and **each of
  the six values must be zero**. Layer (1)'s permission
  guarantee is evidenced by this observed state, not
  inferred from the uid/gid transitions the read-backs
  accompany. **The fail-closed case:** a capability
  read-back is made to return a **nonzero** observation
  — induced through the test build's fault-injection
  hook feeding a synthetic nonzero mask to the check
  (the hook of demonstration (viii), extended in the
  test build to interpose on the capability read-back;
  the production launcher contains no such feed) —
  exercised **once against the child-side check and
  once against the parent-side check**. The child-side
  case must show the launch aborting at the check: the
  child `_exit()`s, the harness never executes, and no
  issuance occurs. The parent-side case must show
  Window 2's outcome end to end: **no release byte** is
  written, the gate is closed unreleased, the child is
  reaped, **no issuance** occurs, and the abort is
  recorded with the synthetic masks as the observed
  values. Where a test build cannot interpose the
  synthetic observation on one side's read-back, that
  side's case is met by **code-order inspection** — the
  check's presence in the pinned sequence, its
  all-three-sets-empty requirement, and its fail-closed
  branch, read against the pinned launcher source —
  and the gate evidence must state which of the two
  proofs was used for **each** side. Omitting a side
  satisfies neither route.
- **(viii) The launch handshake (Rev 04; failure cleanup
  Rev 05).** By fault injection, through the launcher's test
  hook — a test-only build feature, present only in the test
  build of the launcher and **compiled out of the production
  launcher** — which forces the parent's privilege
  transition to fail after the fork, in **each of the two
  failure windows** of §3.5 point 3: **Window 1**, the
  failure surfacing before the parent's drop has taken
  effect (an induced `setres*()` failure; the parent still
  privileged, and its direct `SIGKILL` available); and
  **Window 2**, the failure surfacing **after** the drop — a
  verification mismatch induced to surface only once the
  parent's effective root is gone, so the parent cannot
  signal across the uid boundary and the cleanup runs
  through the gate: the parent closes the gate write end
  unreleased, the waiting child observes end-of-file and
  `_exit()`s, and the parent reaps it. A test that exercises
  only Window 1 proves only the easy case and does not
  satisfy this obligation. In **every** induced case the
  test proves the fail-closed outcome end to end: the
  harness **never executes** (no harness process persists;
  no run artefacts appear); **no child process survives**;
  the child is **reaped by the parent**; and **no START
  commitment and no issuance entry exists** for the aborted
  launch — the supervisor's trees contain nothing for it but
  the recorded abort. The **parent-death variant**: the
  parent is killed after the fork but before releasing the
  gate; the child exits without executing the harness — by
  end-of-file on the gate or by its `PR_SET_PDEATHSIG`
  backstop (§3.5 point 3) — leaving no harness process, and
  the child's termination, kernel-signalled or gate-exited,
  is observable in the test's recorded evidence even though
  no parent survives to reap it. A test in which the parent
  failure is simulated only in the supervisor's bookkeeping
  — the child's gate never actually exercised — does not
  satisfy this obligation.
  **Post-release parent death (Rev 06) — a required case,
  distinct from the variant above:** a full launch completes
  — the child's credentials dropped and verified, the
  backstop armed **after** the drop, the gate released, the
  harness (the stub, in the test build) **running** — and
  the parent is then killed; the recorded evidence must show
  the running child terminated by the backstop's `SIGKILL`.
  The pre-release variant exercises a child that has not yet
  exec'd; it cannot by itself prove the arming persisted
  past the child's `setresgid()`/`setresuid()` transitions
  and the exec — and Rev 05's placement, arming before those
  transitions, would silently have failed here. This case,
  and only this case, is the proof the backstop survives
  the credential transition.
  **Install-window parent death (Rev 06; sequence
  corrected, Rev 07):** the parent is
  killed during the child's setup window — after the fork,
  before the child's arming completes — and the evidence
  must show the child exiting at its parent-relationship
  re-check (`getppid()` no longer returning the **expected
  parent identity captured before the fork**) **without
  executing the harness**.
  Where the test build can hold the child inside the setup
  window (a test-only hold at that point, compiled out of
  the production launcher like the failure hook above), the
  case is induced directly. Where a test build cannot
  induce that timing deterministically, this part of the
  obligation is met by **code-order inspection** — the
  pinned child sequence (**pre-fork capture of the
  expected parent identity by the parent; the child's
  first comparison of `getppid()` against the inherited
  expected value; transitions; verification; the
  capability read-back; arming, with its return-value
  check; the `PR_GET_PDEATHSIG`
  read-back; the re-check against the same expected value;
  close; gate**) read against
  the pinned launcher source — and the gate evidence must
  state which of the two proofs was used. An inspection of
  any shorter sequence proves the wrong sequence (Rev 07).
  Omitting the case
  satisfies neither route.
  **Pre-first-instruction parent death (Rev 07):** the
  parent is killed in the interval between the fork and
  the child's first comparison, so the child has already
  been reparented when it first runs; the evidence must
  show the child exiting at that first comparison — its
  `getppid()` differing from the inherited expected parent
  identity — **without proceeding** to the transitions,
  the arming, or the gate, and without executing the
  harness. Where the test build can induce that timing (a
  test-only hold interposed between the fork and the
  child's first instruction, compiled out of the
  production launcher like the other hooks), the case is
  induced directly; where it cannot be induced
  deterministically, the code-order-inspection route above
  covers it — that inspection now reads the corrected
  sequence — and the gate evidence must state which of
  the two proofs was used. Omitting the case satisfies
  neither route.
- **(ix) Executable identity continuity (Rev 08).** By
  adversarial test of the arrangement in §3.5's
  verification block, in a scratch installation tree.
  **(a) Substitution:** the test harness, acting under
  the operator's authority — an out-of-model writer —
  replaces the executable with a scratch copy carrying a
  **setuid bit**, after the freeze-time verification has
  recorded the genuine object's identity. The
  substitution is arranged before any launch, so the
  supervisor's **pre-launch verification** is the
  checkpoint expected to fire first: the resolved
  object's identity — device, inode, mode, capability
  set — no longer matches the freeze record, the launch
  is refused, no harness process exists, and the abort is
  recorded with **both** identity records, the freeze's
  and the observed. The case is also satisfied if the
  parent's **pre-release re-check** is the checkpoint
  that fires, provided the substituted object is never
  executed and the abort is recorded the same way.
  **(b) Redirection:** a symlink component in the
  scratch executable's path is repointed to a scratch
  target **after** the supervisor's pre-launch
  verification has passed against the genuine object, so
  the launcher's **pre-release re-check** is the checkpoint
  expected to fire first: canonical re-resolution lands
  on the substituted object, the identity comparison
  fails, **no release byte is written**, the gate cleanup
  runs (Window 2's pattern — gate closed unreleased,
  child exiting on end-of-file, launcher reaping), no
  issuance occurs, and the abort is recorded with both
  identity records. Either checkpoint firing satisfies
  the case, provided the substituted object is never
  executed. **(c) The path-component audit, evidenced:**
  one directory component of a scratch tree's resolved
  path is deliberately made **group-writable** (a second
  arrangement: owned by a non-root identity); the
  freeze-time audit must **flag** the component — its
  owner and mode recorded against the protected-placement
  requirement — and the tree's identity record must not
  be established as verified until the defect is
  corrected. A freeze that records identities without
  auditing the components does not satisfy this part. A
  test in which the substitution or the repointing was
  never actually arranged does not satisfy this
  obligation. **Scope of what (ix) demonstrates.** These
  cases demonstrate detection of a substitution arranged
  before launch and of a redirection arranged after
  pre-launch verification but before the parent's
  pre-release re-check — the two checkpoints firing on
  changes that land before the re-check. They do **not**
  demonstrate detection of a substitution landing
  **after** the pre-release re-check, and nothing in
  this demonstration claims it: that case stands outside
  the threat model, under layer (3)'s statement as
  corrected (Rev 09).


===== 5. REV 26 §3.7 =====
### 3.7 Examiner tooling, stub subject, and transport double

- **Examiner (Harness §7; Criteria §§2, 8).** Build the replay
  procedure as a runnable artefact that re-derives outcomes
  **from the preserved record and pinned rules alone**: step 0
  anchor verification (START/TERMINAL/CRASH against recomputed
  hashes, every receipt checked against the supervisor's
  issuance record); chain integrity; input identity;
  deterministic re-execution of every [TOOL]/[RULE] step and
  [CHECK] phase byte-for-byte against the recorded payloads
  (extractions re-executed under the four-outcome semantics — an
  outcome mismatch in any pairing is a divergence); the insert
  audit with the **registry reconstructed from the event
  sequence**, never read from the build's own state; subject
  outputs taken as preserved artefacts from `response_raw`,
  **never re-sampled**. The examiner does not accept the
  operator's scoring worksheet as truth: it re-derives each
  verdict and confirms or overturns the worksheet, verdict by
  verdict (Criteria §2, divergence rule). Governance
  re-derivation is exact; why the hosted model produced its
  output is not re-derivable and is not claimed (Harness §7).
  **Carried provenance (Rev 23):** the insert audit also
  re-derives every carried field from the record alone —
  for each `LEDGER_ENTRY` with `verification` = `"CARRIED"`,
  locate the `carried_from` event, recompute its payload
  hash, confirm the producing step's `CHECK_RESULT` passed,
  confirm exactly one ledger entry consumes that citation,
  and, for an `evidence` entry, re-derive the expected
  citation set from the record's extraction events and
  compare. No harness state is consulted; a carried entry
  whose provenance does not re-derive is a divergence
  exactly as an extraction mismatch is. **(Rev 24:)** the
  re-derived evidence expectation is the **ordered
  sequence** of §3.3 (record order, duplicates preserved);
  two entries consuming one citation is a divergence
  exactly as two entries consuming one operation is; and
  every ledger entry, of either class, is validated
  against §3.3's field rules — `source_ref` null only on
  CARRIED entries, exactly one provenance form per entry —
  with any violation a divergence. **(Rev 25:)** each
  insertion invocation's recorded `form` tag is checked
  against its ledger entry's provenance form (an
  `"extracted"` invocation producing a `carried_from`
  entry, or the reverse, is a divergence), and an
  invocation carrying no valid tag must pair with a
  `PRESENTATION_FORM` refusal and no ledger entry.
- **Stub subject (spec decision, flagged).** The sources require
  Stage 5 verification without a model call (Plan Stage 5;
  Criteria §5.1 stubs [MODEL] steps for calibration) but do not
  name the stub's form. This spec fixes it: a **scripted stub
  subject** behind the adapter's harness-facing boundary — a
  deterministic test double implementing the `complete()`
  contract's harness side, returning declared outputs per
  (tree, step) from a pinned stub script, including scripted
  cases the verification needs (a well-formed output; a
  malformed output; a refusal-shaped output; a truncation-shaped
  output) so [MODEL]-step handling, [CHECK] phases, and failure
  branches are exercised end-to-end with no live call. The stub
  is test scaffolding **outside the run path**: it is selected
  by pinned test configuration in scratch contexts only, and no
  scored run can be configured to use it (the run's
  `RUN_STARTED` block pins the adapter configuration; a stub
  configuration is a different, visibly named configuration used
  only in scratch runs, whose records are labelled as such and
  are never offered as run evidence).
- **Synthetic captures — the stub run satisfies the capture
  contract (Rev 02, Alex's condition on §6.3 item 2).** A
  stubbed [MODEL] step must not return scripted text *around*
  the evidence machinery: the stub responder sits behind the
  adapter so that `complete()` runs the adapter's full capture
  path, and the Batch 6 stub full-battery run produces genuine
  `ADAPTER-CAPTURE-02` records — one per [MODEL] step, linked
  from the record by `MODEL_CALL_LINKED`, with `record_sha256`,
  `request_sha256`, and `response_sha256` recomputing — and
  **every entry in `attempts[]` carrying its preserved
  `response_body_raw` with a recomputing
  `response_body_sha256`** wherever that attempt received a
  body, satisfying Criteria §1.1(6) exactly as a live run must.
  Where a verification case needs a retried call, the stub
  scripts an attempt sequence — a failed attempt with its own
  preserved body, then the success — so the failed attempt's
  body is present in `attempts[]`, never summarised away. Every
  synthetic capture is **explicitly labelled**: the capture's
  subject identity is the stub's visibly named configuration,
  never the pinned model id; the run's `RUN_STARTED` block pins
  the stub configuration as such; and the examiner verifies the
  label as part of re-deriving the stub run — a synthetic
  capture that could be mistaken for a served-model capture
  fails this section. The doubles' boundary is unchanged and
  **neither substitutes for the other**: the **transport
  double** exercises the real adapter's HTTP handling —
  retries, error-body capture, redaction — against scripted
  wire sequences; the **stub subject** exercises the harness's
  step, linkage, and capture machinery end-to-end. Batch 5's
  transport-double checkpoints and Batch 6's stub full-battery
  run are separate evidences for separate boundaries.
- **Transport double (spec decision, flagged).** Adapter
  behaviour that only appears on the wire — per-attempt capture
  of error bodies, retry timing, the pre-classified 400 — is
  verified against a **local scripted HTTP double** (a loopback
  test endpoint replaying declared status/body sequences:
  200-with-body, 429-then-200, 500-then-200, 400 rejecting
  `chat_template_kwargs`, timeout), never against the live
  endpoint. The adapter under test is the real adapter; only
  the endpoint is doubled, and the double's identity is recorded
  in every test artefact it touches. Stage 5 makes **no contact
  with the provider host** — no chat completion, no listing, no
  probe — **except a LANE-CRUSHER evidence retrieval under a
  prior, per-operation authorisation recorded by Ben under
  §0.3** (§0A.7). LANE-ADAPTER contact has no Stage 5 exception
  of any kind; the adapter's first contact is Stage 6's.
- **No provider contact — enforced, not merely stated (Rev 12,
  Claude's finding 1; isolation boundary total, Rev 13).** A rule the build can break silently is
  a statement, not an enforcement, so Stage 5 carries three.
  **(a) Loopback refusal:** in Stage 5 mode the adapter
  **refuses any non-loopback base URL** — a configuration
  naming a non-loopback provider address **fails closed at
  start-up, before any run**; the transport double's loopback
  endpoint is the only address a Stage 5 adapter can be
  configured to reach. **No proxy path (Rev 13):** in
  Stage 5 mode the adapter **does not use proxy
  configuration or any other forwarding mechanism** to
  reach an external service — proxy settings, however
  supplied, by environment or by configuration, are
  **not honoured** in Stage 5 mode, so no indirect route
  through a local proxy or forwarding service is open
  to it. **(b) No credential in the build
  environment:** the build environment holds **no provider
  credential** — credentials remain in the connector's custody,
  outside the build environment — so the build has nothing to
  authenticate with even if it is misconfigured. **(c)
  Zero-egress evidence:** the build and gate environment has
  **no non-loopback network egress at all** (Rev 13) —
  loopback interfaces only: not merely no route to the
  provider host, and no indirect route through a proxy or
  a connector either. Gate **G1 records the zero-egress
  check and its result** (§5), on evidence showing the
  **actual environment's** isolation — its interfaces
  inspected (for example, a network namespace with no
  external route), no external route present, and **no
  available external proxy or connector path**. An
  environment in which non-loopback egress cannot be
  shown absent — or whose evidence addresses only direct
  routes — does not pass G1. **Nemotron is not called
  in Stage 5, and nothing else at the provider host is
  contacted either**: enforcement, not wording, is what makes
  that a fact about the build rather than about its
  intentions.

---


===== 6. REV 26 §4 BATCH 6 + §5 GATES =====
**Batch 6 — Examiner, calibration, and full verification.**
Implement the examiner tooling (§3.7); run the **calibration
pass** (Criteria §5) producing PILOT-CALIBRATION-01 — every
[TOOL]/[RULE] step of all 13 instances executed offline against
the pinned snapshot, rules, and data, [MODEL] steps stubbed as
not exercised, all six §5.1 items recorded, each instance
certified ANSWERABLE or named UNANSWERABLE with its cause; run
a **stub-subject full-battery scratch run** (all 13 instances)
and re-derive it end-to-end with the examiner tooling.
*Checkpoint:* the §5 build-acceptance gates, run in full, on the
assembled package.

**End state.** A constructed pilot package — tools, driver,
record, supervisor, adapter, examiner — plus the Stage 5
evidence pack (§2.4), offered for independent inspection (§7).
Nothing in the end state has called the subject.

---

## 5. BUILD-ACCEPTANCE GATES

**All five gates must pass before the constructed package is
offered for independent inspection.** A failed gate returns the
build to the relevant batch; there is no partial pass and no
waiver recorded in prose — a gate either passes on preserved
evidence or the build is not done. Every gate's evidence is
preserved as an artefact and verified by re-derivation
(Criteria §8), not by trusting its summary.

- **G1 — The sabotage battery S1–S5** (Criteria §4), run against
  the built PILOT-TOOLS-01 in a scratch run context. S1 forged
  `operation_id` (the *guessable next sequence number* is the
  preferred form — refusal must come from the absence of an
  issuance entry, never from the id being surprising) → refusal.
  S2 genuine FOUND result presented for insertion → refusal.
  S3 genuine EXTRACTED result inserted (succeeds), then
  presented again → second presentation refused. S4 genuine
  EXTRACTED result whose `source_hash` no longer recomputes
  against a perturbed scratch snapshot → refusal. S5 extraction
  under a rule producing two valid matches → recorded AMBIGUOUS
  with all candidates and no value; its insert → refused. Each
  test's required outcome: the refusal object returned, an
  `INSERT_REFUSED` governance event with full
  claimed-vs-recomputed detail, **no** `LEDGER_ENTRY`, **no**
  value returned. **Any insertion succeeding — a ledger entry
  emitted or a value returned, in any test — fails the build,
  full stop**; and a tool that refuses everything has also
  failed (S3's first insert must succeed). The battery's scratch
  record is preserved and cited in the inspection.
  **Zero-egress evidence (Rev 12, Claude's finding 1;
  widened, Rev 13).** The battery runs in the Stage 5 build
  environment, and this gate's evidence records that
  environment's **zero-egress check**: the environment has
  **no non-loopback network egress at all** — loopback
  interfaces only — and the preserved evidence shows the
  isolation of the **actual environment**: its **interfaces
  inspected** (for example, a network namespace with no
  external route), the **absence of any external route**,
  and the **absence of an available external proxy or
  connector path**. The check is performed and its result
  recorded alongside the battery's record; an environment
  in which non-loopback egress cannot be shown absent —
  or whose evidence addresses only direct routes — **does
  not pass this gate**. The no-contact rule is enforced by
  the environment, by the adapter's loopback refusal, and
  by its refusal of proxy configuration (§3.7); this gate
  is where that enforcement is evidenced.
- **G2 — The interrupted-write crash test** (Criteria §4, Rev
  04; Harness §2.6; SE-7(iii)), with **Alex's qualification**:
  the evidence must demonstrate a **genuinely torn write**. The
  harness is killed **while an event is being appended** — in
  the scratch context the append is fault-injected (a declared
  test-only slow/partial write path) so the kill lands
  mid-append deterministically; a kill that happens to leave a
  complete final event or no partial bytes **does not satisfy
  the test**, and the test is re-run until a torn tail is
  genuinely produced and that artefact set is the preserved one.
  **The injector must not ship (Rev 12, Claude's finding 6).**
  The slow/partial write path exists only under a **build-time
  flag** — `PILOT_TORN_WRITE_INJECTOR` — settable only in the
  scratch/test build configuration. A build outside the scratch
  context **refuses to compile with the flag set**; the flag's
  state for the build under examination is **recorded in this
  gate's evidence**; and a build carrying the injector is **not
  a scoreable build** — the injector's absence from any
  production or scoreable build is demonstrated by the recorded
  flag state, not asserted.
  The examiner verifies all three: (1) the incomplete trailing
  bytes are **inside** the CRASH commitment's
  `record_file_sha256` (recomputed over the file's exact bytes
  as they lie); (2) the trailing bytes are **never treated as a
  complete event** — chain verification and replay end at the
  last complete event the commitment's `event_count` and
  `final_event_sha256` name; the tail parses as no event,
  satisfies no step, enters no verdict; (3) the trailing bytes
  **cannot be silently discarded** — a trimmed or
  after-the-fact-completed record fails hash recomputation as a
  §3.1(ix) anchor failure. The test also confirms the negative
  space: **no TERMINAL receipt exists** for the crashed run, the
  CRASH receipt appears in the supervisor's issuance record, and
  the run's outcome under the criteria is INCONCLUSIVE. All
  three verifications hold, or the Stage 5 build fails this
  obligation. Artefacts preserved: the partial record, the CRASH
  receipt, the issuance-record entry.
- **G3 — SE-1…SE-7 demonstrated** (Harness §4.5). SE-1…SE-6 by
  structural inspection of the built code (the properties are of
  what code paths exist and what they can reach) **and** the
  adversarial tests of G1; SE-7 by the §3.5 demonstrations:
  OS-boundary refusal tests as the harness identity, supervisor
  self-computation, the launcher separation tests (§3.5(v)–(ix)),
  the crash cases (G2), and issuance-record verification
  including the planted-receipt negative test. A
  build in which any SE property holds only because no caller
  has tried to violate it has not met this gate.
- **G4 — Anchor-first replay over a full run record.** The
  Batch 6 stub-subject full-battery record (all 13 instances) is
  re-derived end-to-end by the examiner tooling following
  Harness §7 steps 0–6 in order: anchor verification first
  (START + TERMINAL against recomputed hashes, receipts against
  the issuance record), chain integrity, input identity,
  deterministic re-execution byte-for-byte, the insert audit
  with the registry reconstructed from events, subject
  artefacts (the stub's preserved outputs) never re-sampled, and
  outcome reconstruction matching the record. Any divergence
  localised by the chain is a gate failure with the localising
  event named.
- **G5 — Calibration certificate complete.** PILOT-CALIBRATION-01
  exists, is pinned, and certifies all 13 instances ANSWERABLE —
  or names the UNANSWERABLE exceptions with their causes
  (Criteria §5.3). An UNANSWERABLE instance is not a build
  failure; it is a named limit the Stage 6 authorisation packet
  must carry. But a calibration pass that was not run, or whose
  §5.1(6) configuration-freeze check was skipped, fails this
  gate: the frozen adapter configuration's **values** (temperature
  0.6, top_p 0.95, reasoning_budget 16384, max_tokens 20480)
  must be mechanically verified, not merely hashed. The
  mechanically checked configuration values also include the
  **canonicalisation standard identifier** (§3.4): the frozen
  configuration must record RFC 8785 (JCS) as the canonical
  form, and calibration verifies that recorded value — a
  configuration naming any other form, or none, is a freeze
  defect of the same kind.

**Stub-subject rule, restated as a gate condition.** Every gate
above runs against the scripted stub subject and the local
transport double (§3.7). **Nemotron is not called in Stage 5 —
not for a gate, not for a checkpoint, not for a smoke test.**
The first model call belongs to Stage 6, under Ben's separate
authorisation (§7; §6.4).

---


===== 7. REV 26 §7 =====
## 7. GATES AND ROLES — NO STEP AUTHORISES THE NEXT

The Stage 5 sequence, with each gate held by its named holder.
**No step in this list authorises the next**; each is a separate
act by its holder, recorded as such.

1. **This specification** is drafted (this document) and
   **shelved**. Shelving is publication of the paper, not
   approval of it.
2. **Alex inspects** the specification (source-to-requirement
   crosswalk; harness-architecture review; the §3.5 custody
   proposal; the §6.3 flagged decisions) **and Claude inspects
   it independently** (Ben's addition, 2026-11-12). The two
   inspections are independent: neither inspector's verdict is
   an input to the other's. Findings are answered by amendment
   to this spec, re-inspected as the finding requires.
3. **Ben's Stage 5 build go.** Only after both inspections stand
   does Ben authorise the build — his separate decision, against
   this spec as inspected. The go names the builder (§6.4).
4. **The build** proceeds by the §4 batches, each checkpoint
   recorded. Deviations from this spec stop the batch (§2.1).
5. **Build-acceptance gates G1–G5** (§5) pass on preserved
   evidence.
6. **Independent inspection of the constructed package** — Alex
   (per Plan Stage 5 and his offers) and Claude independently,
   against this spec and the design package: structural
   inspection of SE-1…SE-7, re-derivation of the battery, crash
   test, and stub-run records, and confirmation of the receipts
   against the supervisor's issuance record (Criteria §9 Q5).
   The builder does not examine (Criteria §2).
7. **Ben's Stage 6 execution authorisation** — a separate
   decision, against the inspected package, the calibration
   certificate (§5.3), and these criteria, setting run count,
   battery composition, and stopping conditions (Plan Stage 6),
   and deciding the §6.1 open items (interrupted-write
   repetition; any smoke call). The first model call happens
   only here, if Ben authorises it.

**Roles.** Ben: owner — adoption, the Stage 5 go, the Stage 6
authorisation; his index law binds every stage. Alex: design
adjudicator and examiner — inspections at steps 2 and 6, the
crosswalk, re-derivation over the worksheet. Claude: independent
second inspector at steps 2 and 6. Builder: named at step 3;
builds to this spec; examines nothing they built. Operator /
scorer of first instance: applies the criteria mechanically to
preserved records and produces the scoring worksheet —
provisional until the examiner's re-derivation stands behind it
(Criteria §2). The subject: Nemotron, pinned (§3.6), called only
at Stage 6.

---

## Scope notes

- This specification inherits Plan 01's exclusions in full: no
  D3 v0.10 completion or conformance claim; no general obligation
  lifecycle; no live Shelf integration (inputs are frozen and
  pinned); no role-enforcement claim from T04's behavioural
  refusal; nothing here touches the ratio study, the Approved
  Pool indexing idea, or the Crusher comparison — Alex's rulings
  on Ben's two parked ideas (REVISION-02-NOTE) keep both as
  separate future projects, expressly **not** smuggled into
  Stage 5.
- Claims discipline: every claim this spec makes about the build
  is a claim about what the build **must exhibit to be
  inspected**, not a claim that anything has been built or
  verified. At the time of drafting, nothing in §2.4 exists.
- Where this spec restates a source, the source governs on any
  divergence discovered at inspection; the divergence is an
  amendment item against this spec, never a silent preference
  for either text.

===== 8a. CRITERIA-04 §4 =====
## 4. THE PROVENANCE SABOTAGE BATTERY — ACCEPTANCE TESTS OF THE BUILD

These tests are run at **Stage 5**, against the built
PILOT-TOOLS-01 in a scratch run context, as part of the package
acceptance Alex inspects — *before* any scored run exists. They
exist because Stage 1 executed the defect they guard against
(Qualification §3: a FOUND result and a hand-fabricated dict both
inserted, both stamped PASS, by the V2 code). Each test attempts
one insertion the provenance rule (Harness §4) exists to refuse.
Rev 02 adds S5, exercising the AMBIGUOUS path end-to-end. The
battery is also the behavioural companion to Harness §4.5: the
tests show the refusals happening; Alex's structural inspection
(SE-1…SE-7) establishes *why* they cannot not happen. Neither
substitutes for the other (Alex's verdict §3).

| Test | Attempt | Required outcome |
|---|---|---|
| **S1 — Fabricated result** | Present for insertion a result that was never issued in this run: a forged `operation_id` carrying a claimed value and a claimed source hash (the executable form of the Qualification probe's hand-built dict, case (c) — under the pilot interface a caller-built dict is not a representable input, so the forgery is attempted at the boundary that exists). A forged id that happens to be *guessable* (the next sequence number) is the preferred form of this test in Rev 02: the refusal must come from the absence of an issuance entry, never from the id being surprising. | Refusal. |
| **S2 — FOUND-state insert** | Present the `operation_id` of a genuine `shelf_lookup` result (verification FOUND, never extracted) for insertion as a field value (probe case (b)). | Refusal. |
| **S3 — Replayed operation_id** | Insert a genuine EXTRACTED result legitimately (it succeeds); present the **same** `operation_id` a second time, for the same or another field. | First insert succeeds; second presentation refused. |
| **S4 — Stale-hash insert** | Present a genuine, unconsumed EXTRACTED result whose recorded `source_hash` no longer recomputes against the corpus snapshot in the test context (the battery runs against a perturbed copy of the snapshot — a section's bytes altered after the extraction was issued — so insert-time recomputation (Harness §4.2) must catch it). | Refusal. |
| **S5 — AMBIGUOUS-state insert (Rev 02)** | In the battery's scratch context, run `source_extract` for a field whose pinned rule (or a battery-declared test rule over a battery section) produces **two valid matches**; confirm the result is recorded AMBIGUOUS with all candidates and **no value**; then present its `operation_id` for insertion as a field value. | The extraction is AMBIGUOUS (never a silently selected first/last match); the insert is refused. |

**Required outcome, each test:** `reference_insert` returns the
refusal object; a `GOVERNANCE_EVENT` (kind `INSERT_REFUSED`) is
recorded with the full claimed-vs-recomputed detail; **no**
`LEDGER_ENTRY` is emitted; **no** value is returned to the calling
step. A refusal that leaves any of the four untrue is a failed
test, not a partial one. (S5 additionally requires the extraction
event itself to show the AMBIGUOUS state with every candidate
recorded; an extraction that produced a single "winning" value
has already failed before the insert is attempted.)

**Battery verdict — pass/fail, no middle state:** the battery
PASSES iff all five tests behave as specified (and S3's first
insert succeeds — a tool that refuses everything has not passed,
it has failed differently). **Any** insertion succeeding — a
ledger entry emitted or a value returned, in any test — means
**the pilot build fails acceptance, full stop.** Stage 5 does not
pass; there is no Stage 6; the tools revision returns to build.
The battery's own record (the scratch run's record + captures) is
preserved as an evidence artefact and cited in the Stage 5
inspection, so the examiner verifies the battery by re-derivation
(§8), not by trusting its summary.

**The interrupted-write crash test (Rev 04) — a Stage 5
build-acceptance obligation, housed here with the battery but
not one of S1–S5.** The battery above tests insertions; this
test exercises the crash machinery of Harness §2.6 / §4.5 SE-7,
whose adversarial crash case Alex's Rev 03 verification
requires be a kill **during an event write** — mid-write, not
merely between steps — so the record ends in incomplete
trailing bytes. In a scratch run context, the harness is
killed while an event is being appended; the supervisor
observes the termination and issues the CRASH commitment over
the partial record as it lies. The examiner must verify all
three of:

1. **The incomplete trailing bytes are inside the anchor.** The
   CRASH commitment's `record_file_sha256` recomputes over the
   partial file's exact bytes, trailing incomplete bytes
   included — the commitment covers the file as it lies, not
   a tidied version of it.
2. **The trailing bytes are never treated as a complete
   event.** The record's last complete event is the one the
   CRASH commitment's `event_count` and `final_event_sha256`
   name; chain verification (§8) and replay (Harness §7) end
   there. The incomplete tail parses as no event, satisfies no
   step, and enters no verdict.
3. **The trailing bytes cannot be silently discarded.** The
   partial record offered for examination must be
   byte-identical to the record the CRASH commitment anchors;
   a record whose tail was trimmed — or completed after the
   fact — fails `record_file_sha256` recomputation and is an
   anchor failure under §3.1(ix), not an editorial cleanup.

**Test verdict:** all three verifications hold, or the Stage 5
build fails this obligation — the anchor machinery has not
demonstrated the crash case it exists for. The test's artefacts
(the partial record, the CRASH receipt, and the supervisor's
issuance-record entry) are preserved and cited in the Stage 5
inspection, verified by re-derivation (§8) like the battery's.

---


===== 8b. CRITERIA-04 §5 =====
## 5. TEST-QUESTION CALIBRATION — NO RUN FAILS ON AN UNANSWERABLE QUESTION

The trees ask fixed questions of fixed data. If a question cannot
be answered from the pinned inputs by the pinned machinery, a run
would measure the question, not the subject. Calibration removes
that possibility *before* execution, deterministically, **without
any model call**.

### 5.1 The calibration pass

At Stage 5, after the re-freeze, the operator executes the
deterministic half of the battery offline: every [TOOL] and
[RULE] step of every tree, against the pinned corpus snapshot,
the pinned `EXTRACTOR-RULES-02`, and the pinned pilot data files,
with [MODEL] steps stubbed as *not exercised*. The pass produces
**PILOT-CALIBRATION-01**, a pinned evidence artefact containing,
per tree instance:

1. **Pack resolution:** every section id in `PILOT-DATA-PACKS-01`
   for the tree resolves in the pinned snapshot (a missing section
   here is a freeze defect, found now, not mid-run).
2. **Extraction coverage:** for every (tree, step, section, field)
   the trees require `source_extract` to produce a value, the
   pinned rule applied to the pinned snapshot **actually produces
   that value** — recorded with its evidence line. Where a tree's
   design expects an absence instead (T01 STEP-04's hit count 0;
   T07 elements designed NOT FOUND; T06's UNTRACEABLE path), the
   expected absence is what calibration verifies and pins.
3. **Expected values:** every value a [CHECK] or `verify_field`
   will compare against is derived from the pinned data and
   recorded — including each `EXPECTED_RECORD` field, each T06
   statement's expected label (from steps A–D), each T07
   obligation's expected status, T08's seeded-draft failed-checks
   list, and each T09 variant's expected worksheet decision.
4. **Stubbed-step declaration:** the [MODEL] steps not exercised
   are listed, so the certificate's scope is exact: calibration
   certifies the deterministic substrate and the questions'
   answerability, nothing about the subject.
5. **Match-count verification (Rev 02; four outcomes, Rev 03).**
   For every (section, field) extraction the pass performs, the
   outcome under Harness §3.2's four-outcome table is recorded
   alongside the value. Four outcomes, all pinned in the
   certificate: **exactly one valid match — EXTRACTED**, the
   value stands as item 2; **no pattern match — NOT FOUND**, the
   expected-absence case, pinned as such where the tree's design
   expects it, else a freeze defect; **matches exist but all
   fail type validation — TYPE FAILURE**, a distinct outcome
   (Rev 03): the evidence is present and the rule cannot
   interpret it, so it is pinned as TYPE FAILURE where a tree's
   design expects it, and is otherwise a freeze defect in the
   rule or the data — **never recorded as an absence and never
   folded into the NOT FOUND case**; **more than one valid match
   — AMBIGUOUS on production data with production rules.** An
   AMBIGUOUS outcome is never left to be discovered mid-run:
   either the tree's design genuinely expects it (pinned as the
   instance's expected outcome, scored under §1.2's anomaly
   rule), or the rule is under-specified for the document and
   returns to a rules amendment + re-freeze + re-calibration
   before any run. The pass also exercises the
   AMBIGUOUS and TYPE FAILURE paths synthetically — a scratch
   section bearing two valid matches for a scratch rule must
   produce an AMBIGUOUS result with all candidates recorded, and
   a scratch section whose only match fails the scratch rule's
   `value_type` must produce a TYPE FAILURE result with the
   matched text and expected type recorded — so both states are
   proven to exist and behave before a run depends on them.

6. **Configuration freeze check (Rev 03).** The adapter
   configuration the Stage 5 amendment freezes — the
   configuration whose hash the `RUN_STARTED` pin block will
   carry — is checked for its **values**, not only its hash: the
   pinned envelope (Adapter §2.3) must carry the documented
   Thinking-mode sampling set exactly as Alex ruled it
   (pb-mweajgej): temperature 0.6, top_p 0.95,
   `reasoning_budget` 16384, `max_tokens` 20480 (Adapter §1.5).
   A frozen configuration deviating on any of the four — a
   silent return to temperature 0 is the named case — is a
   freeze defect: the run would execute a configuration the
   ruling did not settle, and calibration does not certify it.
   The check is mechanical (the frozen configuration is data,
   read and compared), and its result is recorded in
   PILOT-CALIBRATION-01 alongside items 1–5.

### 5.2 The R60 change-record question, specifically

The pilot's sharpest question rides on one section —
`r60-revision-change-record#009` (T01 STEP-03, T05 STEP-02/03,
T08 STEP-02). Calibration must demonstrate, from the pinned
snapshot with the pinned rules:

- Every `EXPECTED_RECORD` field for the change record reproduces
  by extraction: `fixtures_executed`, `fixtures_passed`,
  `harness_sha256`, `results_sha256` (Stage 1's probe already
  extracted `fixtures_executed` = 38 from this section under the
  V2 rules; calibration re-establishes all four, and
  `correction_b` from the adjudication record, under the *pilot's*
  pinned rules and snapshot — the probe is precedent, not
  evidence). Each reproduction records its match count (§5.1(5)):
  a field that reproduces only by winning a multi-match has not
  reproduced.
- The T05-STEP-02 cross-record comparison is **measured and
  pinned**: whether the shelf-manifest row's stated hash and the
  change record's extracted hash agree in the pinned set. If they
  agree, T05's expected path is construction. If they disagree,
  T05's pinned expected outcome is the tree's own STOP —
  *disagreement recorded as a record defect* — and the pilot's
  claims for T05 adjust accordingly (the tree then evidences
  defect detection; construction and recovery are evidenced by
  T08). Either way the expectation is fixed before the run, so
  the verdict stays mechanical.
- The four extractor rules the question needs exist in
  `EXTRACTOR-RULES-02` as data, at the pinned version — a field
  with no rule is NOT FOUND *by construction* (Qualification §4,
  capability 6), which is exactly the unanswerable-question
  failure this section exists to preclude.

### 5.3 The answerability gate

Calibration issues, per instance, one of: **ANSWERABLE** (all of
§5.1 verified; the expected-outcome table for the instance is
pinned in PILOT-CALIBRATION-01) or **UNANSWERABLE** (a named
requirement fails: unresolved pack section, missing rule, value
not producible, **an unexamined or unpinned AMBIGUOUS on a
required extraction**, **an unexamined or unpinned TYPE
FAILURE on a required extraction (Rev 03)**, expected value
underivable). An
UNANSWERABLE instance **may not be run** at Stage 6 until the
cause is fixed in the data or rules and the fix is re-frozen by
amendment and re-calibrated. A run that proceeds over an
UNANSWERABLE instance is void for that instance regardless of its
record — and running one knowingly is a §3.1(viii)-class event
for the run. The calibration certificate (all 13 instances
ANSWERABLE, or the exceptions named) is part of the Stage 6
authorisation packet: Ben authorises execution against a stated
battery, not an assumed one.

---


===== 8c. CRITERIA-04 §8 =====
## 8. THE RE-DERIVATION TEST — AN ACCEPTANCE TEST OF THE RECORD ITSELF

Following Harness §7 and Adapter §6.1, as a scored test with a
pass/fail of its own:

**Test.** An examiner holding **only** (a) the run directory —
`run-record.jsonl` and `captures/` — (b) **the run's commitment
receipts (Harness §2.6), which live outside the run directory
precisely so this test can begin outside the record's own
custody**, and (c) the pinned artefacts the record's own pin
block identifies, fetched from the Stage 0 freeze + Stage 5
amendment and verified by the hashes the record itself carries —
and nothing else: no harness state, no builder testimony, no
operator notes, no re-issued model call — must be able to
reproduce **every** instance verdict of §1.

The reproduction follows Harness §7's steps in order:
**anchor verification first (step 0)** — the START commitment's
genesis and pin-block hashes, and the TERMINAL commitment's file
hash, event count, and final-event hash — **or, for a crashed
run, the CRASH commitment's file hash, event count, and
final-event hash over the partial record (Rev 03)** — all
recomputed before the chain is trusted, **and every receipt
checked against the supervisor's issuance record (Harness
§2.6)**; chain integrity; input identity;
deterministic re-execution of every [TOOL]/[RULE] step and
[CHECK] phase, byte-for-byte against `TOOL_RETURNED` payloads
and `CHECK_RESULT`s (extractions re-executed under Harness
§3.2's match semantics, so an AMBIGUOUS recomputation against a
recorded EXTRACTED — or the reverse — is a reproduction failure
like any other); the §4.2 insert audit over every `LEDGER_ENTRY`
and `INSERT_REFUSED`, **with the issuance registry reconstructed
from the event sequence (Harness §7 step 4) rather than read
from the build's state**; subject outputs taken as preserved
artefacts from `response_raw`, never re-sampled — including, per
ADAPTER-CAPTURE-02, every attempt's preserved body, whose hashes
must recompute and whose retry history the examiner verifies
against the adapter's declared policy. The scoring worksheet
(§2) is then checked against the reproduction, verdict by
verdict.

**Reproduction failure** is any of: a commitment mismatch or a
missing commitment where closure is claimed, **a partial record
offered with no CRASH commitment or one that does not verify
(Rev 03)**, or **a receipt the supervisor's issuance record
does not show** (Harness §7 step 0);
a hash-chain break or `seq` gap; a pin the record names that the
freeze cannot produce; a recomputed tool result or check outcome
differing from the recorded one in any byte; a `LEDGER_ENTRY`
failing the insert audit; a registry issuance, consumption, or
refusal the event sequence cannot reproduce; a capture whose
hashes do not recompute — **including any attempt-level body
hash**; a verdict that requires information not present in
(a) + (b) + (c) — the canonical case being a decision recorded
without the worksheet, comparison, or rule outcome that
supposedly decided it.

**Consequences, mechanical:** reproduction failure in chain
integrity, **commitment verification**, or the insert audit →
the run is FAILURE (§7.1), since the record can no longer be
trusted anywhere. Reproduction failure localised to one
instance's subject verdict (e.g. a comparison the examiner
cannot re-perform for that instance alone) → that instance
becomes NOT-SCORED, and the run's outcome is recomputed under
§7.1 (SUCCESS is no longer reachable). Reproduction success
over all 13 instances is a necessary condition of run SUCCESS —
a run whose record cannot be re-derived has not met the plan's
minimum evidence, however clean its worksheet looks.

---


===== 9a. HARNESS-03 §2.6 =====
### 2.6 The external trust anchor — START, TERMINAL, and CRASH commitments (Rev 02; CRASH added Rev 03)

**The defect this answers (Alex's correction A).** A hash chain
proves internal consistency: alter one event and the links after
it break. It does not prove the record is the record that was
written. Anyone with write access to the whole record file can
rewrite every event and recalculate every hash, producing a
chain that verifies perfectly against a history that never
happened. Rev 01's wording — the chain makes silent rewriting
"detectable" — claimed more than the mechanism holds, and is
qualified by this section: **the chain detects accidental
corruption and ordinary, partial edits; the anchor is what
defeats wholesale rewrite.** START and TERMINAL are both
required for a closed run: neither is optional, and a run
without both is not scoreable as complete (Criteria Rev 03
§1.1). Rev 03 adds the third receipt kind the crash case
requires — the CRASH commitment, below: a crashed run has no
TERMINAL commitment by definition, and Rev 02 left its partial
record committed by nothing outside itself (Alex's Rev 02
verification, the one remaining gap in correction A).

**Form.** A commitment is a small JSON **receipt** — a separate,
immutable artefact, written once and never edited. Receipts are
**not an index** (Ben's rule; Alex's verdict makes the same
distinction): a receipt names exactly one run, enumerates
nothing, catalogues nothing, and is written by the system side
of the boundary, never by the harness and never by any agent,
tool, or seat.

**Custody.** The receipts live in `commitments/` (§2.4), outside
the run directory and outside every path the harness can write.
They are written by the **run supervisor** — the system
component that starts the harness process, observes its exit,
and closes the run — which is outside the harness's code and
privilege boundary. The supervisor reads from the harness only
what the harness cannot later change without detection: the
genesis hash at start (below) and the finished file at close.
How the supervisor is implemented is a Stage 5 build question;
the design requirement is the custody split itself: **the
harness must not be able to silently rewrite the evidence and
its verification anchor together**, because it holds only one
of them.

**The issuance record (Rev 03).** Custody must be provable, not
merely plausible from a file's location (Alex's Rev 02
verification). The supervisor therefore keeps its own
**issuance record**: an append-only record, held in supervisor
custody alongside the receipts (§2.4), in which every issuance
is entered as it happens — `{run_id, kind, issued_at_utc,
receipt_sha256}` for each START, TERMINAL, and CRASH commitment
it writes. The receipts are the artefacts; the issuance record
is the supervisor's own account of having issued them. An
examiner verifies a presented receipt **against the issuance
record** (§7 step 0): a receipt with no corresponding entry, or
whose hash differs from its entry, is not evidence — it is a
custody finding. The issuance record is written only by the
supervisor; the harness has no write path to it, and nothing
in this design permits any agent, tool, or seat to write it.
The Stage 5 proof obligations this creates are stated as SE-7
(§4.5). Alex has confirmed the custody split itself suffices
at the architecture level; no operating-system-level
prescription is added here, and none is required before
Stage 5.

**START commitment** — written by the supervisor when
`RUN_STARTED` is flushed, before any step executes. Content:
`{run_id, kind: "START", issued_at_utc, genesis_sha256,
run_started_event_sha256, pinned_input_block_sha256}` — where
`genesis_sha256` is the §2.2 genesis preimage (the pinned-input
manifest block's hash) and `pinned_input_block_sha256` is the
hash of the `RUN_STARTED` payload's pin block as written. The
START commitment fixes, from outside the record, *what the run
claimed its inputs were at the moment it began*, so a later
rewrite cannot quietly re-pin the run to different inputs.

**TERMINAL commitment** — written by the supervisor when the
run's terminal event (`RUN_CLOSED` or `RUN_STOPPED`) is flushed
and the record file is closed. Content: `{run_id, kind:
"TERMINAL", issued_at_utc, terminal_event_type,
final_event_sha256, event_count, record_file_sha256}` — the
sha256 taken over the record file's exact bytes as closed. The
TERMINAL commitment fixes *where the record ends and what it
weighs*: any event appended, removed, or altered after closure
breaks it, and a rewritten record with a recalculated chain
still breaks it, because the anchor value lives outside the
rewriter's reach.

**CRASH commitment (Rev 03)** — written by the supervisor when
it observes the harness process terminate **without** a
terminal event having been flushed: no `RUN_CLOSED`, no
`RUN_STOPPED`, and therefore no TERMINAL commitment. Content:
`{run_id, kind: "CRASH", issued_at_utc, record_file_sha256,
event_count, final_event_sha256, termination_observed}` — the
sha256 taken over the partial record file's exact bytes as
they lie when the termination is observed; the count of
complete events in that file; the last complete event's
`event_sha256`; and the supervisor's own record of the
termination it observed (when, and on what basis — the
process's exit, witnessed by the component that launched it).
The CRASH commitment's sole function is to **externally commit
the partial record exactly as observed after the crash**, so
the closed portions of that record (§6.4) rest on an anchor
the harness cannot rewrite, instead of on the partial chain
alone. It is bound by three prohibitions: it is **not** a
TERMINAL commitment and must never be presented as one; it
does **not** close the run and does **not** make the run
scoreable as complete — a crashed run's outcome is governed
by Criteria Rev 03 §7.1's INCONCLUSIVE rules, never by its
closed trees' verdicts alone; and it is issued **only** where
no TERMINAL commitment exists for the run — TERMINAL and CRASH
never coexist for one run, and a run presented with both is a
custody finding, not a curiosity.

**Absence is a signal.** If the harness process dies without a
terminal event, there is no TERMINAL commitment, and none may
be manufactured after the fact: the record is partial (§6.4),
and what the supervisor issues instead is the CRASH commitment
above, over the partial file as it lies. The distinction
between a closed run and a crashed one therefore never rests
on anything the harness says: a closed run carries TERMINAL; a
crashed run carries CRASH; the two never coexist. A partial
record offered with **neither** — no TERMINAL (it never
closed) and no CRASH (the supervisor never observed the
termination, or never issued) — has no external commitment to
its tail at all and fails verification outright: its closed
portions are **not** examinable, because nothing outside the
record vouches for them. Likewise, a record offered **with** a
closure claim but **without** a matching TERMINAL commitment
fails verification outright (Criteria Rev 03 §8). A START
commitment with no run record at all is a pre-flight artefact
of a run that never opened — reported as such, never scored.

**Verification.** Replay (§7) begins at the anchor: recompute
the genesis and pin-block hashes against the START commitment;
recompute the file hash, event count, and final-event hash
against the TERMINAL commitment — or, for a crashed run,
against its CRASH commitment, in which case examination covers
the record's closed portions only and the run is examinable
solely as a partial record (§6.4). Every receipt relied on is
checked against the supervisor's issuance record (above): the
anchor is the supervisor's act of issuance, not the receipt
file's location. Only then walk the chain. A record that fails
its commitments is not examined further — its evidence is void
from the first divergent byte, and the finding is about
custody, not about the subject.

---


===== 9b. HARNESS-03 §4.5 =====
### 4.5 Structural-enforcement requirements (Rev 02)

Alex's verdict (§3): the sabotage battery's four tests are
necessary, but build inspection must also establish that the
refusal mechanism is *structurally* enforced, not merely that
four examples fail. The properties inspection must establish
are therefore stated here as design requirements. Each is a
property of the built package's structure — of what code paths
exist and what they can reach — not of its behaviour on
selected inputs:

- **SE-1 — Sole issuer.** The harness is the only issuer of
  extraction results. A result exists, for insertion purposes,
  only as a registry entry created by the harness's own
  execution of `source_extract` (§4.2). No other component —
  adapter, subject, operator tooling, test scaffolding inside
  the run path — can create, mint, or import a result.
- **SE-2 — No caller-supplied provenance.** The insert
  operation's interface accepts no provenance from its caller:
  its only handle on a result is the `operation_id` (§3.4).
  Value, source, hash, evidence line, and verification state are
  all read from the registry and recomputed (§4.2); there is no
  parameter, field, or side channel through which a caller can
  supply or override any of them.
- **SE-3 — Registry beyond the subject's reach.** The registry
  cannot be modified by the subject. Structurally: the subject
  has no tool access, no corpus access, no filesystem or process
  access to harness state (§1.3); its outputs enter the harness
  only as preserved artefacts consumed by [CHECK] phases and
  tree-declared steps. There is no step type, input format, or
  adapter behaviour by which subject output can write a registry
  entry, alter one, or mark one consumed or unconsumed.
- **SE-4 — Recomputation against the pinned corpus, at insert
  and at examination.** Value and source are recomputed against
  the pinned corpus snapshot at insert time (§4.2) and again,
  independently, at replay (§7 step 4). The insert decision
  trusts nothing the original extraction merely recorded: not
  the value, not the hash, not the evidence line.
- **SE-5 — Single use.** A consumed operation cannot be used
  again (§4.2 consumption; §4.2 property 4). The consumption
  state is registry state reconstructable from the record
  (§4.2 property 5), so a replay that finds a second insertion
  of one `operation_id` has found a build defect, not a
  scoring question.
- **SE-6 — Refusal is sterile.** A refusal produces **no**
  ledger entry and **no usable value** (§4.3): the calling step
  receives the refusal object and nothing else; no field comes
  into existence; no artefact downstream of the step can cite
  the refused result as its source. Inspection confirms there
  is no fallback path — no default value, no cached result, no
  "insert anyway with a warning" branch — anywhere in the
  insert call graph.
- **SE-7 — Anchor custody is demonstrable (Rev 03).** The
  §2.6 trust anchor holds structurally, and Stage 5 must
  demonstrate it, not assert it (Alex's Rev 02 verification,
  carried verbatim in substance): **(i)** the harness cannot
  write, replace, or delete commitment receipts — no code path
  in the built harness reaches `commitments/` for writing, and
  adversarial tests that attempt receipt forgery, replacement,
  and deletion from inside the harness's privilege boundary
  fail; **(ii)** the supervisor independently records the
  START, TERMINAL, and CRASH commitments — issuance is the
  supervisor's own act, performed outside the harness's code
  and privilege boundary, never delegated to harness code and
  never performed over values the supervisor has not itself
  recomputed or observed; **(iii)** Stage 5 demonstrates the
  separation through inspection **and** adversarial tests —
  including the crash case: a harness killed mid-run receives
  a CRASH commitment over the partial file as it lies, and no
  TERMINAL commitment; **(iv)** the examiner verifies the
  supervisor's **issuance record** (§2.6), not merely a receipt
  sitting in a separate directory: every receipt presented at
  examination has a corresponding issuance entry, and every
  entry's hash matches its receipt. Alex has confirmed the
  custody split suffices at the architecture level; SE-7 is
  what Stage 5 must *prove* about the build, and no
  operating-system-level prescription is imposed here.

Stage 5 inspection tests SE-1…SE-7 against the built code, and
the Stage 4 criteria's sabotage battery (Criteria Rev 03 §4)
exercises them behaviourally. A build in which any SE property
holds only because no caller has tried to violate it has not
met this section.

---


===== 9c. HARNESS-03 §7 =====
## 7. REPLAY PROCEDURE — INDEPENDENT RE-DERIVATION

An examiner with the run directory, the run's commitment
receipts (§2.6), the pinned input set (PILOT-MANIFEST-01 +
Stage 5 amendment), and this design re-derives the run's
outcome without trusting the harness:

0. **Anchor verification (Rev 02; CRASH and the issuance
   record, Rev 03).** Before the record is trusted for
   anything: recompute the genesis hash and the `RUN_STARTED`
   pin-block hash against the START commitment; recompute the
   record file's sha256 over its exact bytes, the event count,
   and the final event's `event_sha256` against the TERMINAL
   commitment — or, for a crashed run (no terminal event),
   against the CRASH commitment, in which case examination is
   limited to the record's closed portions and the run is
   examinable only as a partial record (§2.6, §6.4). Every
   receipt relied on is verified against the supervisor's
   issuance record (§2.6, §4.5 SE-7): a receipt the issuance
   record does not show, or whose hash differs from its entry,
   is not evidence. Any mismatch — a claimed closure with no
   TERMINAL commitment, or a partial record with no CRASH
   commitment — ends the examination here: the record's
   evidence is void and the finding is a custody failure
   (§2.6), not a verdict about the run's contents. Only a
   record that passes its anchor is walked further.
1. **Record integrity.** Walk `run-record.jsonl`: verify `seq`
   continuity from 1, recompute each `event_sha256`, and verify
   the `prev_event_sha256` chain back to the genesis block.
   Any break voids the affected tail as evidence.
2. **Input identity.** Recompute the sha256 of every artefact
   in the `RUN_STARTED` pin block (§2.5) against the pinned set.
   Confirm the catalogue evidence and model pin (Adapter §6.1)
   for every linked capture.
3. **Deterministic re-execution.** Re-run every [TOOL] and
   [RULE] step and every [CHECK] phase from the recorded inputs
   (the pinned snapshot, rules data, and pilot data make this
   possible offline): each recomputed tool result must equal
   its `TOOL_RETURNED` payload byte-for-byte; each recomputed
   check outcome must equal its `CHECK_RESULT`. Deterministic
   machinery leaves no room for "trust the log" — the log is
   checked against re-execution. (Re-execution of
   `source_extract` runs under §3.2's match semantics — any
   extraction-outcome mismatch is a divergence like any other:
   an AMBIGUOUS or TYPE FAILURE recomputation where the record
   claims EXTRACTED, a TYPE FAILURE recomputation where the
   record claims NOT FOUND, or vice versa in any pairing.)
4. **Insert audit, with registry reconstruction (Rev 02).**
   Rebuild the issuance registry from the event sequence alone
   (§4.2 property 5): issuances from `source_extract`
   `TOOL_RETURNED` events, consumptions from `LEDGER_ENTRY`
   events, refusals from `INSERT_REFUSED` governance events.
   For every `LEDGER_ENTRY`: confirm its `operation_id` was
   issued to the same tree/step context before the insert,
   confirm the §4.2 recomputation from the pinned snapshot
   yields the inserted value and hash, and confirm single
   consumption against the reconstruction — not against the
   build's own registry state. For every `INSERT_REFUSED`
   governance event, confirm the refusal was warranted by the
   same recomputation. Any issuance, consumption, or refusal
   the record cannot reproduce is a build finding (§4.5).
5. **Subject artefacts, treated as artefacts.** For every
   [MODEL] step: follow `MODEL_CALL_LINKED` to the capture
   file; verify the capture's hashes, including every attempt's
   preserved body hash (Adapter §6.1, Rev 02); take
   `response_raw` as the subject's preserved output — a fixed
   artefact — and re-derive every downstream verdict (checks,
   worksheet decisions, status assignments, ledger fields) from
   it by the deterministic machinery. **The subject is never
   re-sampled at replay.** Re-issuing a request would produce a
   new sample, not evidence about this run (Adapter §6.2), and
   this procedure neither needs nor permits it.
6. **Outcome reconstruction.** Recompute each tree's closure
   from its step outcomes under §1.4's rules, and the run's
   terminal state from the tree closures. The reconstruction
   matches the record, or the discrepancy — localised by the
   chain to the first divergent event — is the finding.

**Exactness statement.** Governance re-derivation (steps 0–4,
6) is **exact**: every input is pinned, every operation
deterministic, every subject contribution enters only as a
preserved byte string, and the record itself is anchored
outside its own custody (step 0). The one non-re-derivable
element in any run is *why the hosted model produced its
output* — which no design at this boundary can supply, and
which the pilot's question does not ask.

---


===== 10. BATCH 5 SHEET FROM C5-11 TO END =====
- **C5-11 — Stage 5 isolation, enforced** (§3.7): in
  Stage 5 mode the adapter **refuses any non-loopback
  base URL** — a configuration naming a non-loopback
  provider address fails closed at start-up, before any
  run; the transport double's loopback endpoint is the
  only address a Stage 5 adapter can be configured to
  reach. Proxy configuration, however supplied, is **not
  honoured** in Stage 5 mode. The build environment
  holds **no provider credential**. (The zero-egress
  environment evidence is gate G1, Batch 6 work under
  the Completion Plan Block 3 — it is not claimed,
  evidenced, or assumed in this batch.)
- **C5-12 — The transport double** (§3.7): a local
  scripted HTTP double — a loopback test endpoint
  replaying declared status/body sequences (200-with-body,
  429-then-200, 500-then-200, 400 rejecting
  `chat_template_kwargs`, timeout). The adapter under
  test is the real adapter; only the endpoint is doubled,
  and the double's identity is recorded in every test
  artefact it touches. The double is test scaffolding
  for this batch's checkpoint; it is not the stub subject
  (Batch 6's full-battery run is separate evidence for a
  separate boundary, §3.7), and neither substitutes for
  the other.

## The checkpoint (§4 Batch 5)

Against the **transport double** (§3.7) only — no live
endpoint, no subject call. The checkpoint is discharged
in ONE bundle (Completion Plan Rule 3), each item with
its underlying evidence, not a summary assertion
(crosswalk standard, applied to this batch by parity).

- **C5-13 — Retry sequences captured whole.** Forced
  429-then-200 and 500-then-200 sequences, plus the
  200-with-body baseline: every attempt's body and hash
  present in `attempts[]`, and the resend byte-identical
  (`request_sha256` invariant across attempts).
- **C5-14 — The pre-classified 400.** A forced 400
  rejecting `chat_template_kwargs` is classified
  ADAPTER_FAILURE and is not retried (exactly one attempt
  in the capture record).
- **C5-15 — Timeout.** A timeout sequence is classified
  (ADAPTER_FAILURE, timeout class) and captured, with the
  attempt's available detail preserved.
- **C5-16 — Redaction test.** No capture field in any
  test artefact contains header or credential material.
- **C5-17 — Envelope fidelity.** The envelope as sent
  equals the pinned configuration byte-for-byte in every
  test capture (`request_envelope` vs the
  `adapter_config_sha256` preimage).
- Out of this checkpoint, by authority: the stub-subject
  full-battery run and the examiner tooling (Batch 6);
  the §5 gates G1–G5, including zero-egress evidence
  (Batch 6); any live catalogue listing or served-model
  claim (Stage 6 pre-flight).

## Standing rules

- **C5-D1** — records and artefacts ride with the
  checkpoint bundle; pins by dated continuation.
- **C5-D2** — no subject call, and no provider contact
  of any kind, anywhere in this batch; the adapter is
  proven against the transport double only, end to end,
  on the record (Completion Plan Block 2).
- **C5-D3** — settled is settled (Completion Plan
  Rule 1): the frozen adapter configuration, the
  `ADAPTER-CAPTURE-02` schema, and the failure taxonomy
  are built as pinned, not re-adjudicated in this batch;
  a finding against this checkpoint names its governing
  pin and clause (Rule 2), and corrections, if any, are
  ONE chunked correction round per checkpoint (Rule 3).
- **C5-D4** — Ben's reserved matters are untouched
  (Completion Plan Rule 8): nothing in this batch spends,
  publishes, creates accounts, or contacts the provider;
  a configuration amendment under C5-9 is decided by
  Ben/Alex against the capture, never improvised by the
  build.

## Approval disposition (Alex)

- Disposition: **APPROVED WITH CORRECTIONS**
- PB-ID / date: pb-mwgz9mjj-2-dp2t, 2026-11-14
  (alex-remmy-b4-b5-and-programme-decision-2026-11-14)
- Corrections: one pin-identification correction —
  the active F-2 configuration and catalogue identities
  are now carried exactly in C5-0c and C5-3 above
  (design authority 5be7eb0e…; adapter_config_sha256
  6cf57195…; readable configuration beb8b7fd…;
  catalogue capture 2026-11-12, bare body 8a80b8e7…,
  helper-stdout file bacf2ec8…, with its
  wire-byte-identity limitation). Pin clarification
  only; no new test or scope.
- Batch 4 gate: the same letter records **BATCH 4
  CHECKPOINT: CLEARED** (C4-10 hold withdrawn;
  crosswalk erratum filed 2026-11-14).

Both opening gates are satisfied — this sheet is
approved and the Batch 4 checkpoint has passed — so
**Batch 5 may begin**, under Ben's 2026-11-13 build
go (Batches 2–6 in order). No Stage 6 action is
implied.
