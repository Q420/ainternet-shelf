# Stage 2 — Corrections Round Notes (2026-11-21)

Built under Ben's commission (scope card widget-284602e8) from Loom spec
v0.1 Rev 9 (shelf commit d7d65c96, Gate 1 PASS), in answer to Vane's
Stage 2 examination (NOT ACCEPTED at shelf commit 9283b7e7, preserved
unaltered as the examined artifact) and her correction-round conditions
(PB pb-mwqa158c-n-6eq2). This round's changes land in the working tree
as a new, separately identifiable round. BUILD-RECORD.md was not
edited; nothing was shelved or sent.

The round resolves, in implementation and tests (not footnotes):

1. **Finding 1** — the §4A boundary is now an OS boundary, not an
   interface: a fabric service under its own OS identity, agent
   processes under another, filesystem permissions doing the denying,
   token issuance nowhere on the agent-facing surface.
2. **Finding 2** — the boundary probe is observationally neutral: it
   runs pre-run, from the agent OS context, against a disposable twin,
   and the experimental history receives exactly one system attestation
   event (seq 2) — no probe reads, no read-record change.
3. **Finding 3A** — a hard-line breach stops the run durably: a system
   RUN_FAILED event, terminal enforcement on every agent-facing route,
   failed state derived by replay — plus the failure-of-failure case:
   latch closed, external diagnostic record, no fabricated event.
4. **Finding 3B** — idle is durably recorded as its own IDLE event,
   under the between-run amendment settled by Remmy and Vane under
   Ben's delegation (2026-11-21).

## What was built

### New files

- **`fabric/service.py`** — the fabric service. Runs as `loomfab`;
  loads the sealed ground truth from the service-side file at startup
  (held in memory, never served); owns the store, engine, and harness;
  serves two Unix sockets. The **data socket** offers exactly the five
  agent operations (`view_pattern`, `consult_index`, `open_region`,
  `submit`, `read_breadth`), each token-authenticated; there is **no
  issuance operation** — an issuance attempt is answered
  `unknown_op`. The **admin socket** (operator path: `issue_token`,
  `open_run`, `record_probe_attestation`, `history`, `status`,
  `shutdown`) lives inside the loomfab-only service directory, which
  the agent identity cannot even traverse. On `HardLineBreach` the
  service appends RUN_FAILED through the engine's atomic commit path
  and refuses every further data operation (checked before dispatch,
  and again inside the harness via the folded state); on append
  failure it latches closed and writes the diagnostic record (see
  below). All dispatch is serialised through one lock. Fault
  injection for tests: start with `LOOM_FAULT_INJECT=run_failed_append`.
- **`fabric/client.py`** — the agent client. Standard library only;
  the five operations over the data socket; **no issuance code path**
  and no other reach (no store, engine, fixture, or file paths beyond
  the one socket). `ClientRefusal` carries the service's error kind.
- **`fabric/agent_runner.py`** — the agent-side executable: copied
  into the runtime's agent home, run as `loomagent` per call by the
  orchestrator, performs one client operation from a JSON request on
  stdin. Every agent operation in the corrections tests is performed
  by a genuine `loomagent` process through this runner.
- **`fabric/probe_agent.py`** — the agent-context half of probe v2:
  stdlib only, holds no sealed material, never prints file contents
  (a successful read would be reported by size + SHA-256 only).
  Attempts, in order: direct read of the store file; direct read of
  the ground-truth file; a symlink planted in the agent home pointing
  at the store; a traversal spelling of the store path; a
  forged-token operation; an issuance attempt on the data socket;
  legitimate pattern view and region open with an issued token.
- **`fabric/probe2.py`** — probe v2 orchestration (driver-side):
  builds the disposable twin, starts its service, opens a twin run,
  obtains a probe token via the twin's admin path, spawns
  `probe_agent.py` as `loomagent`, collects outcomes, tears the twin
  service down, and returns the result object; `attest_probe()` sends
  it to the experimental service's admin path for the seq-2
  attestation.
- **`fabric/runtime_setup.py`** — driver-side runtime construction
  and process management: layout, ownership, permissions, the
  byte-identical service code copy, the ground-truth file, service
  start/stop via `runuser`, the admin client, and the `loomagent`
  script spawner.
- **`stage2_corrections_tests.py`** — the round's suite: 53 checks
  (outputs below).
- **`boundary-runtime/README.md`** — records where the runtime
  actually lives and why (see gap 1); `boundary-runtime/
  RUNTIME-EVIDENCE.json` is written by the test suite on each run
  (layout stat records, the full probe result, the diagnostic record).

### Existing files changed (each flagged, per the round's limits)

- **`fabric/store.py`** — (a) `EVENT_TYPES` gains `RUN_FAILED` and
  `IDLE` (the round's two new event types; the append path asserts
  membership, so this is required). (b) `EventStore.__init__` gains
  `check_same_thread=True` as a keyword: the service passes `False`
  because its store is created in the main thread and used from
  handler threads under the dispatch lock; in-process callers keep
  sqlite's default thread checking and identical behaviour.
- **`fabric/engine.py`** — fold branches for the two new types:
  `IDLE` is evidence-only (like DISCOVERY); `RUN_FAILED` sets
  `run_status="failed"` and a `failure` record in the derived state.
  The failure keys appear **only** when a RUN_FAILED is present, so a
  healthy run's derived state is byte-identical to before the round —
  proven, not asserted: the Stage 1 smoke's genesis state hash is
  still `9a7250bde82bfd8b…`, the value recorded for the examined
  Stage 1 (see regression output below).
- **`fabric/harness.py`** — (a) `submit` with action `idle` now
  appends a durable IDLE event and returns its sequence (was: an
  in-memory log line). (b) `HardLineBreach` carries the declared and
  recorded read sets as attributes, so the run's owner records the
  evidence verbatim. (c) A `run_failed` property + `_require_open()`
  guard at the top of every agent-facing method: a harness whose
  folded state is failed refuses all agent operations. (d) Docstring
  and log-comment updates recording (a)–(c). In-process breach
  semantics are otherwise unchanged — the harness still raises and
  appends no contribution event (see interpretation 3).
- **`fabric/fixture.py`** — `ground_truth_document()` and
  `load_ground_truth(path)` added; the SEALED comment records the
  deployment form. The constants remain the in-process examiner copy;
  the deployment file is written from `ground_truth_document()` and
  the suite verifies canonical byte-identity between the two.
- **`fabric/probe.py`** — **unchanged.** It remains what Vane's
  examination said it is: a useful in-process route scan,
  supplementary evidence only. Probe v2 is a new file, not a rewrite
  of its history.

## The boundary, precisely (Vane's condition 1 evidence)

OS identities (created on this machine before the build, verified
2026-11-21): **`loomfab` uid 1000** (fabric service), **`loomagent`
uid 1001** (agent side). Processes are switched with
`runuser -u <user> -- <cmd>` from the root orchestrator.

Runtime layout (per runtime; base `/tmp/loom-boundary-runtime`,
runtimes `experimental`, `twin`, `faulttest`):

| Path | Owner | Mode | Holds |
|---|---|---|---|
| `service/` | loomfab | 700 | the service's whole world |
| `service/events.db` | loomfab | 600 | the event store (created by the service under umask 077) |
| `service/ground-truth.json` | loomfab | 600 | the sealed ground truth as a file |
| `service/admin.sock` | loomfab | 700 | operator socket — inside the 700 dir |
| `service/failures/` | loomfab | 700 | unrecordable-failure diagnostics |
| `service/code/fabric/*.py` | loomfab | 750/640 | byte-identical copy of the package |
| `sock/` | loomfab | 711 | traverse-only; holds ONLY the data socket |
| `sock/fabric.sock` | loomfab | 777 | data socket (see interpretation 4) |
| `agent-home/` | loomagent | 755 | `client.py`, `agent_runner.py`, `probe_agent.py` (644) + `store-link` symlink |

Service boundary: the agent identity can reach exactly one thing —
the data socket — and on it exactly five operations, each requiring
a token it cannot mint (issuance exists only on the admin socket,
inside a directory it cannot traverse). Tokens are issued by the
service at the orchestrator's request and handed to agent processes
on stdin.

Tested access outcomes (probe v2, from a real `loomagent` process,
against the twin; full outputs below):

- direct read of the twin store file — **denied**, `PermissionError`,
  errno 13 (EACCES);
- direct read of the twin ground-truth file — **denied**, errno 13;
- read via the planted symlink — **denied**, errno 13;
- read via a traversal spelling (`sock/../service/events.db`) —
  **denied**, errno 13;
- forged-token region open on the data socket — **refused**
  (`unrecognised token`);
- `issue_token` operation on the data socket — **refused**
  (`unknown_op`: the route does not exist);
- legitimate pattern view with an issued token — **succeeded**
  (6 regions);
- legitimate region open — **succeeded**, full genesis content of
  Components served. The agent is isolated, not disabled.

Twin equivalence: the twin and experimental layouts were compared
entry-by-entry (owner + mode for service dir, ground-truth file,
failures dir, code dir, socket dir, agent home) and are identical;
the twin's store file was loomfab 600 during the probe; the service
build is the same byte-identical code copy in both (hash-verified
against the tree).

Probe neutrality, tested on the experimental run: before the
attestation the store held 0 events; after `open_run` + attestation
the history is exactly `[RUN_OPENED, BOUNDARY_PROBE]`; the seq-2
event is a system event whose payload carries `attestation: true`,
the full twin probe result, and `probe_result_hash` = SHA-256 of the
canonical probe result (recomputed by the test); there are **zero**
DISCOVERY events in the history and a fresh agent's read breadth is
0.0 — the probe produced no experimental discovery and changed no
read record. Ordering, as decided in BUILD-RECORD: RUN_OPENED stays
the constitution-rooted genesis at seq 1; the attestation follows
at seq 2, before any agent admission.

RUN_FAILED, tested end-to-end through the socket as `loomagent`:
an agent opened State, then submitted a schema-valid contribution
declaring reads {State, Components} it had not made. The service
refused the submission as `run_failed` and recorded exactly one
RUN_FAILED (system actor) whose payload carries the breach kind,
the declared set, the recorded set, and the claimed-but-not-made
diff, with a plain-words summary. Afterwards, all seven post-breach
attempts (pattern, index, open, idle-submit, breadth — for the
breaching agent, plus pattern and open for a second agent) were
refused. The service was restarted on the same runtime: status
still `failed`, operations still refused — the failed state comes
from the history. Root-side replay of the full history derives
`run_status="failed"` with the breach evidence; the chain verifies;
the fabric content is untouched (all regions still v1).

Failure-of-failure, tested with `LOOM_FAULT_INJECT=run_failed_append`
on a third runtime: the breaching submission was answered
`run_failed_unrecorded`; every later operation was refused with the
same kind; the history contains **no** RUN_FAILED (exactly
`[RUN_OPENED, DISCOVERY]` — nothing fabricated); status reports
`latched_unrecorded_failure: true` with `run_status: "open"` — the
record distinguishes the unrecordable failure from a recorded one;
and `service/failures/` holds one diagnostic record
(`unrecorded-failure-<timestamp>.json`) carrying the timestamp, the
full breach evidence, and the append error (`RuntimeError: injected
fault (LOOM_FAULT_INJECT): the RUN_FAILED append failed`), with a
note stating it is deliberately not part of the event history.

IDLE, tested through the socket and in-process: the socket idle
returns the durable event sequence (seq 4 in the experimental run);
the IDLE event stands in the history under the agent's identity
with a plain-words summary; in-process, idle appends IDLE at seq 2
and replay folds it without state change.

## Interpretations and gaps — recorded, not silently amended

1. **Runtime location (environment-forced deviation).** The brief
   placed the runtime under
   `~/workspace/loom-prototype/boundary-runtime/`. That is
   impossible on this machine: the workspace filesystem denies
   `chown` to this sandbox (`Operation not permitted`, verified by
   direct experiment — the workspace sits on an overlay outside the
   sandbox's capability set; even new files there cannot be
   chowned), so no ownership boundary can exist on workspace files.
   The runtime therefore lives on tmpfs at
   `/tmp/loom-boundary-runtime`, where chown and permission
   enforcement were verified by direct experiment before the build
   (a loomfab 600 file reads as loomfab, denies as loomagent). The
   workspace `boundary-runtime/` directory holds the README
   recording this and the `RUNTIME-EVIDENCE.json` the suite writes.
   Runtimes are disposable and rebuilt from the tree on every run,
   so tmpfs volatility costs nothing but the live sockets.
2. **The service runs a byte-identical copy of the package.** For
   the same reason (pre-existing workspace files cannot be chowned,
   and the tree's group permissions do not include `loomfab`), the
   service cannot read the tree in place. `build_runtime` copies
   `fabric/*.py` into `service/code/fabric/` (loomfab 750/640) on
   every build, and the suite asserts the copy's SHA-256 set equals
   the tree's. The code under test is the tree's code, verifiably;
   but the copy step is a deployment act, recorded here, not a
   detail to discover later.
3. **RUN_FAILED lives at the service layer, deliberately.** The
   examined Stage 2 semantics — pinned by `stage2_tests.py`, which
   asserts a breach appends no event and the in-process run
   continues — have the harness raise `HardLineBreach` and append
   nothing. The durable stop therefore belongs to the run's owner:
   the service catches the breach and appends RUN_FAILED atomically
   (the engine's commit path appends and folds in one transaction),
   and enforcement is doubled — the service refuses before dispatch,
   and the harness itself refuses once its folded state is failed
   (a harness built over a failed history is born refusing; tested
   in-process). The in-process library alone still does not stop a
   run; the boundary deployment does. That division is stated here
   so no one grades the library as the deployment.
4. **The data socket file is mode 777.** Connecting to a Unix
   socket requires write permission on the socket file; the socket
   sits alone in a traverse-only (711) directory that exposes
   nothing else, and authorisation is the token protocol inside it.
   The OS boundary's job — the store and ground-truth files — is
   enforced by ownership and modes above. Recorded so the 777 is a
   decision on the record, not an oversight.
5. **Fault injection is a startup environment variable, not a
   socket operation.** `LOOM_FAULT_INJECT=run_failed_append` arms
   exactly one simulated append failure path in the service. No
   test hook exists on either socket; the agent-facing surface did
   not grow for the tests.
6. **The operator is root on the same host.** Root can read the
   service's files (and the tests do, for evidence). The §4A
   boundary binds the **agent execution context**, which is what
   the spec's probe exercises; nothing here claims isolation from
   the host's own administrator, and the orchestrator's token
   handoff travels on the agent process's stdin — adequate for a
   single-host prototype, and the seam a multi-host deployment
   would have to seal.
7. **Service threading.** The threaded socket server shares one
   store connection: `EventStore` gained an explicit
   `check_same_thread` keyword (default unchanged) and the service
   serialises all dispatch through one lock — section 3's atomicity
   is defined over a serial history in any case.
8. **Corrections during this build (visible).** (a) The runtime
   base directory inherited mode 770 from the caller's umask and
   silently walled the service out of its own runtime;
   `build_runtime` now sets the base mode explicitly. (b) The first
   service build answered admin requests with sqlite
   `ProgrammingError` (connection created in the main thread, used
   in handler threads) — fixed by item 7, not by catching the error.
   (c) `start_service` now terminates a service that never becomes
   ready, instead of leaving an orphan holding the sockets.
9. **What this round does not claim.** The probe establishes that
   the system enforces its access rules; it does not establish that
   an agent will behave well within granted access (Vane's closing
   distinction, preserved). Tension protocols and seals remain
   Stages 3/4. The old probe (probe.py) remains in the tree as the
   supplementary route scan, its Stage 2 history untouched.

## Test outputs (final runs, 2026-11-21)

### `python3 stage2_corrections_tests.py` — 53/53 PASS

```
PASS  service directory is loomfab-only (700)
PASS  ground-truth file is loomfab 600
PASS  socket directory is traverse-only (711)
PASS  agent home belongs to loomagent
PASS  twin layout equals experimental layout (owners + modes)
PASS  service code copy is byte-identical to the tree
PASS  ground-truth file carries exactly the fixture's sealed document
PASS  probe: direct_read_store denied by the OS  PermissionError: Permission denied
PASS  probe: direct_read_ground_truth denied by the OS  PermissionError: Permission denied
PASS  probe: alternate_path_symlink denied by the OS  PermissionError: Permission denied
PASS  probe: alternate_path_traversal denied by the OS  PermissionError: Permission denied
PASS  probe: forged token refused
PASS  probe: issuance attempt on the data socket refused (no route)
PASS  probe: legitimate pattern view succeeds (isolated, not disabled)
PASS  probe: legitimate region open succeeds
PASS  probe verdicts: reads denied, attacks refused, legitimate ok
PASS  twin store file was loomfab 600 during the probe
PASS  twin config matches experimental layout on shared entries
PASS  before: experimental run unopened, zero events
PASS  experimental run opens (genesis)
PASS  attestation appended as seq 2
PASS  history is exactly RUN_OPENED + BOUNDARY_PROBE
PASS  attestation is a system event carrying the probe provenance
PASS  attestation payload carries a plain-words summary
PASS  probe introduced no DISCOVERY events into the history
PASS  probe left the read record empty
PASS  agent pattern view through the socket
PASS  agent region open serves genesis content
PASS  agent read breadth is 1/6 after one open
PASS  idle through the socket returns a durable event sequence
PASS  IDLE event is in the history, by the agent, with a summary
PASS  second agent opens State
PASS  breaching submission refused as run_failed
PASS  RUN_FAILED is recorded once, as a system event
PASS  RUN_FAILED payload carries the breach evidence
PASS  post-breach: every agent-facing route refuses, for every agent
PASS  service status reports the failed run
PASS  after restart the run is still failed (state from history)
PASS  after restart, agent operations still refuse
PASS  replay of the experimental history yields the failed state
PASS  experimental chain verifies end to end
PASS  the failed run's fabric content is untouched (all regions v1)
PASS  unrecordable failure: breach response says so
PASS  unrecordable failure: service stays latched closed
PASS  unrecordable failure: NO RUN_FAILED event was fabricated
PASS  status distinguishes the unrecordable failure (latched)
PASS  diagnostic record written to the service failures directory
PASS  diagnostic record carries breach + append error + timestamp
PASS  in-process idle appends a durable IDLE event
PASS  in-process idle is replay-safe
PASS  RUN_FAILED folds to failed state, live and on replay
PASS  harness over a failed history refuses agent operations
PASS  healthy genesis state carries no failure keys

STAGE 2 CORRECTIONS TESTS: ALL PASS
```

### Regression — `python3 stage2_tests.py` — 40/40 PASS

```
PASS  wrong-token read refused
PASS  read serves the region's content
PASS  read recorded as a DISCOVERY event
PASS  re-open of a read region allowed
PASS  third distinct region read refused (breadth cap)
PASS  read breadth is 2/6 < 0.5
PASS  breadth allowance is per agent
PASS  pattern serves no content
PASS  index consultation recorded, breadth untouched
PASS  replay equals live state after reads
PASS  chain verifies after reads
PASS  boundary probe: every route failed to expose sealed material  17 routes
PASS  boundary probe recorded as a BOUNDARY_PROBE event
PASS  probe record itself carries no sealed material
PASS  probe left the fabric untouched
PASS  identity mismatch rejected and recorded
PASS  schema-invalid contribution rejected (missing rationale)
PASS  TV-2: raise_tension type structural is schema-invalid
PASS  cross-field: write_set outside read_set is schema-invalid
PASS  cross-field: unknown region id is schema-invalid
PASS  cross-field: duplicate content target is schema-invalid
PASS  discovery_ref naming another agent is schema-invalid
PASS  discovery_ref naming no event is schema-invalid
PASS  hard line: claiming an unmade read stops the run
PASS  hard line: omitting a made read stops the run
PASS  valid contribution commits; region version bumps
PASS  replay equals live state after a commit
PASS  overtaken contribution rejected stale, with the changed-read diff
PASS  order: stale plant proposal rejected stale, not structural
PASS  order: schema-invalid plant proposal rejected schema, not stale
PASS  Annex D plant rejected structural, naming S3
PASS  TV-7 setup: contribution X accepted
PASS  TV-7(i): identical resubmission returns the original outcome, no new event
PASS  TV-7(ii): different content under the same key conflicts
PASS  add_dependency commits; both endpoint versions advance
PASS  remove_dependency commits; both endpoint versions advance again
PASS  raise_tension commits; semantic tension stands open
PASS  every Stage 2 event payload carries a plain-words summary  29 events
PASS  replay equals live state at the end of Run C
PASS  chain verifies at the end of Run C

STAGE 2 TESTS: ALL PASS
```

### Regression — `python3 stage1_smoke.py` — 18/18 PASS

```
PASS  genesis is the only event
PASS  genesis type RUN_OPENED
PASS  genesis prev_hash is the constitution hash
PASS  six regions at v1
PASS  four genesis dependencies
PASS  replay reproduces live state exactly  9a7250bde82bfd8b
PASS  hash chain verifies
PASS  empty history is not a valid chain
PASS  genesis state is deterministic across runs
PASS  UPDATE on events is refused by the store
PASS  DELETE on events is refused by the store
PASS  history intact after refused mutations
PASS  INSERT OR REPLACE by event_seq is refused
PASS  INSERT OR REPLACE by event_id is refused
PASS  original event byte-for-byte unchanged after REPLACE attempts
PASS  replay halts on a second RUN_OPENED  replay halted at seq 2: RUN_OPENED is only valid at sequence 1
PASS  tampered payload detected at seq 1
PASS  engine refuses state from a tampered history  replay halted at seq 1: event hash does not recompute

STAGE 1 SMOKE: ALL PASS
```

Note the genesis state hash `9a7250bde82bfd8b` — unchanged from the
examined Stage 1 record. The corrections round did not move the
healthy-run state derivation by a single byte.

### Regression — `python3 observer/test_export_safety.py` — 11/11 PASS

```
PASS  export of a sound run succeeds
PASS  source database unchanged by export
PASS  page was produced
PASS  empty store refused
PASS  empty file unchanged by refusal
PASS  missing store refused
PASS  missing file not created by refusal
PASS  export with adversarial payload succeeds
PASS  breakout sequence is not present as markup
PASS  page has exactly one script element
PASS  adversarial string round-trips as data

OBSERVER EXPORT SAFETY: ALL PASS
```

No failures in any final run. The corrections suite was run three
times end-to-end (fresh runtime rebuild each time) with identical
results.
