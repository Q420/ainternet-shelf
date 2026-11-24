# Demonstration preparation — one generated agent, working, in its office (2026-11-24)

The paper that takes the programme from the closed Track B room to the
live demonstration (Track F). It specifies, in order: the stocking
(Track C), the doorway connection (Track E), and the run (Track F),
inside the claim fence the whole line has carried. It authorises
nothing: each stage it names still passes its own examination, and the
run still passes its own release.

**Where this sits.** The vision governs, in its settled words:
collaboration is agents interacting through shared work, their
contributions changing the work and influencing one another; the record
makes that interaction durable and recoverable. Vane's three levels
(INDEX 459) place this paper exactly: it prepares **the immediate
proof** — one generated agent doing real work in its own office. It is
a step inside the collaboration framework, not a substitute for it, and
§5 fences what it may claim. Ben's ruling (INDEX 455) sets the
objective: get one agent working, end to end. The room exists to let
the worker work; this paper puts the worker in it.

**What is already settled and not re-argued here.** The room is built
and closed as the working room (Track B, INDEX 461; construction,
envelope contract, and persistence terms as recorded in
`room/rig/RIG-NOTES.md`). The execution interface is closed for design
(Track A, INDEX 433): the worker's own reach, twice preserved, is
`container.exec` with `{cmd: [string, …]}` and no other fields. The
authority distinction is certified (INDEX 423): **environmental
authority** inside the room may be broad; **framework authority**
outside it remains the doorway's. Accepting the room's output accepts
it as the worker's authentic contribution — never as true, accurate,
or useful. Usefulness is Track H, Ben's, afterwards, and separate.

---

## 1. Stocking the office (Track C)

The office is stocked by the office, from the case, under a stocking
manifest that names everything in the room. Nothing is in the room
that the manifest does not name.

### 1.1 The case materials

The standing assignment's three sources, fixed by the run scope's
pre-run manifest (`live-demo/first-worker/manifest.json`; manifest
SHA-256 `bd6f3cae7cb5fa1624a78a501566721099a55abe3d35852784b4ae3a287d904f`),
stocked inside the room tree under `work/sources/` — the worker's
working directory is `/room/work`, so the sources stand at the same
relative paths the assignment names:

| In-room path | SHA-256 | Provenance |
|---|---|---|
| `sources/stock-take.md` | `ecb919025d4e5176a7128009ad17c4d12c9ff4f1dd41748b148262308b8cc2e7` | Vane's stock-take, 2026-11-23 (INDEX 187) |
| `sources/a3-pass.md` | `d60e5b0fd97baab6bffe4b8c6aee5bdc700ce6035ab26f7a6d49107659f25bff` | Vane's Piece A3 pass letter (INDEX 186) |
| `sources/index-tail.md` | `eb16b56bb16c53dfb7b5420b2a2c446e8cbc40cf4787e460b8de9773145d05ed` | INDEX entries 165–187, extracted verbatim |

The issued case identifies the manifest by its hash in its evidence
boundary, exactly as the run scope requires: after the run, what the
worker was given is establishable exactly, not by filename.

### 1.2 The runtime stock

What the rig already provides, stated from RIG-NOTES and not extended
by this paper: the host's system trees bound read-only into the room
(`/usr`, `/lib`, `/lib64`, `/bin`, `/sbin` — shell, interpreter,
binaries, and libraries as the host carries them); a fresh `/proc` and
a minimal `/dev`; a scrubbed environment (`PATH=/usr/bin:/bin`,
`ROOM_ID`, and nothing else — no credentials exist in the room); the
rig's own named stock items (`/rig/preflight.py`, and the in-room
reaper at `/rig/reaper.py`, which is mechanism, not worker stock). The
worker's evidenced working pattern — a shell invocation running Python
reading a program from a heredoc (Track A, E1) — is served by exactly
this stock: `bash` and `python3` off the read-only system trees.

The stocking manifest for this demonstration records the runtime stock
by the rig's declared recipe (`room.standard_recipe()`, already
recorded in every room's state), so the manifest accounts for the
complete contents of the room — case materials and executable
environment alike — as the design requires (Rev 2 §3).

**Stock verification (Track C's proof step).** At stocking time,
before any worker is admitted, the room runs a smoke set and the
results enter the record: the shell runs; `python3` runs; each of the
three sources is readable at its in-room path; a file can be written
to and read back from `scratch/`. A smoke failure refuses the room —
the run never starts on an office that cannot do the assignment's
basic acts.

### 1.3 The workspace and the deliverable

The tree the rig builds is the workspace: `work/` (the sources, the
working directory), `scratch/` (the worker's own space — drafts,
intermediate files, dead ends, kept without penalty per the office
principle), `deliverable/`, and `rig/`. The worker organises its space
its own way inside the property line.

**The deliverable destination is `scratch/brief.md` inside the room**
(the run scope's destination, in the rig's tree layout). When the run
ends, the office carries the deliverable out: its hash is taken at the
wall, host-side, from the tree, and that hash is what the record and
the checker carry. Nothing else leaves the room except the record.

### 1.4 The room's declared envelope for this run

The building's parameters, declared at stocking, sized generously to
this assignment under the office principle (INDEX 448): the assignment
is reading three small documents and writing a short brief through a
shell and Python — every figure below is many times the work's
expected draw, because a bound the honest work can brush is a bound
set wrong.

| Parameter | Value for this run | Reason |
|---|---|---|
| Storage (sized tmpfs backing the tree) | 512 MiB (rig default) | The sources are kilobytes and the brief is ~600 words; the ceiling exists to bound a fill, never to crowd the work. |
| Memory working ceiling (aggregate RSS) | 512 MiB (rig default) | A shell + Python working set is tens of MiB; half a GiB leaves room for a large load spike to happen and settle. |
| Memory catastrophic ceiling | 2× working (rig default) | A genuine flood is capped fast, without waiting out the sustain window. |
| Sustain window | 1.0 s (rig default) | Ben's trip curve: over the working ceiling briefly and recover is a recorded pressure event, not a kill. |
| Process working ceiling | 128 (rig default) | Shell pipelines and a Python child fork modestly; 128 is far above the pattern and far below a fork flood. |
| Process catastrophic ceiling | 2× working (rig default) | As memory: the flood line. |
| CPU budget (run-cumulative) | 600 CPU-seconds | Matches the run's 600 s deadline as a total-work bound; the assignment should spend a small fraction of it. It is an accounting budget, not a rate limit and not a hard ceiling — the rig's exact contract (§5). |
| Warden census interval | 50 ms (rig default) | The granularity at which the envelope's measurements were demonstrated. |
| Per-execution wall-clock | 120 s | Any single command in this assignment — read, sort, write — finishes in seconds; 120 s bounds a hung command without crowding a slow one. The run deadline (600 s) governs the whole. |
| Output ceiling per stream | 1 MiB (rig default) | Reading the sources back through a command is tens of KiB; 1 MiB is generous, and anything beyond is counted, truncated, and flagged — never silently dropped. |

Per-process rlimits stand as the rig's second layer, labelled
per-process wherever recorded; they are not the envelope and this
paper does not present them as one.

### 1.5 Failed reaches, and the learning loop

A failed reach inside the room — a command that fails because a
binary, a library, or a file is absent — is not a violation and not a
stall ground by itself: the execution returns its nonzero exit status
through the result contract (§2.3), the worker sees it, and the record
keeps it. That is the learning loop working as designed (INDEX 448,
449): **a failed reach is evidence of a missing capability, not
automatic authority to add it.** What the worker reached for, what was
unavailable, and where the room constrained useful work must be
visible after the run — in the execution records (each command as
proposed, its exit status, its bounded output) and in the terminal
readout rendered from them (§2.5) — so the next room's stocking is
decided from evidence. Any proposed addition to the stock is examined
against the room's purpose and boundary before the manifest changes;
the worker may also *state* a need (in its work or its yield), and a
request is information for the authority, never permission (INDEX
449's preserved distinction).

---

## 2. The doorway connection (Track E)

### 2.1 The offered tool: name and shape

**The offered tool is `container.exec`, arguments an object whose
`cmd` is an array of strings; no other fields are required.** This is
the one design line Track A's residual uncertainty touches, and the
paper takes the choice the evidence points to, for the record's own
reasons (TRACK-A-EVIDENCE-ASSESSMENT §4): the worker's preserved
generations — twice, under different configurations — used exactly
this name and form (E1), and the documented signature for the name
independently specifies the same form (D2). Offering the tool under a
framework-invented name would repeat the withdrawn assumption in a new
place: forcing our vocabulary on the worker and hoping it adapts. The
direction is the opposite — offer the tool the worker keeps asking
for, and work around that.

The residual uncertainty is stated, not smoothed: whether the route
*delivers* a well-formed call when `container.exec` is offered as a
host-defined definition is unobserved — every preserved generation of
that name occurred with no tools offered. It is resolved the only way
it can be: by witnessing the live transport end to end when the tool
is integrated (§2.4), and at the demonstration itself. If delivery
fails, the run records a refused first response — a bounded,
informative result, not a wreck — and any change of name or route
returns through a new release. Nothing else in this paper depends on
the answer.

### 2.2 Dispatch: an ordinary doorway dispatch

Each invocation is an ordinary doorway dispatch of a granted tool,
under the framework's existing machinery (the native adapter, built
and closed, INDEX 410; the loop's preflight discipline unchanged):

1. The provider response is captured whole under the evidence
   discipline (response-evidence artifact, hashed).
2. Every proposed call in the response is classified **before any
   effect** — extraction, then catalogue determination, then parsing,
   then schema validation at the translation boundary, per the
   adapter's closed build.
3. The translation record is persisted, bound to the response-evidence
   artifact's hash, **before** any dispatch.
4. For a call naming the execution tool, the doorway checks exactly
   two things: **the grant** (this assembly holds the execution-tool
   grant) and **the shape** (`cmd` present, an array of strings). The
   doorway **does not police the command's contents** — what the
   command may do is governed by the room's walls (environmental
   authority), not by adjudicating the command line (framework
   authority stays at the doorway for everything outside the room).
5. The dispatch delegates execution to the rig's `Room.run` with the
   `cmd` array as the command, under the room's declared envelope
   (§1.4) and the per-execution wall-clock.
6. The result returns to the worker in the room's own result contract
   (§2.3), carried in the framework's package carriage under the
   provider call ID — the carriage form already demonstrated live
   (native1, INDEX 416; Track A, E6) — not as a provider `role:
   "tool"` message, which this framework has never sent.

Refusals at any step (ungranted name, malformed shape, cap) are
recorded refusals: they consume no dispatch, are not stalls, and are
visible in the record and the readout like everything else.

### 2.3 The room's result contract

No vendor documents an execution result format (INDEX 436: the
documented result for this tool name is prose — "return
stdout/stderr" — with no schema; the model-facing `python` tool's
result is likewise unspecified). **The room therefore defines its own
result contract**, and the doorway returns exactly this object for
every execution:

- `exit_status` — the command's exit code; `null` when the execution
  was terminated (timeout or envelope) before an exit code existed.
- `stdout` — the captured standard output, bounded at the output
  ceiling; `stdout_bytes_total` — the full byte count before any
  truncation; `stdout_truncated` — whether the ceiling cut it.
- `stderr`, `stderr_bytes_total`, `stderr_truncated` — the same
  three, for the error stream.
- `termination` — one of `completed`, `timeout`,
  `envelope-termination` (naming the ceiling and rule that tripped),
  or `precondition-failed` (naming the failed precondition — storage
  backing, namespace discovery, ledger — in which case the command
  provably never ran).
- `cpu_seconds_charged` — the figure the run's ledger was charged for
  this execution (the larger of the census and reaper figures, per
  the rig's accounting).
- `duration_seconds` — the execution's wall-clock duration.

The contract is deliberately plain: exit, output, and what ended it.
Whether the worker consumes this layout as fluently as it consumed a
retrieval result is a behavioural unknown the record cannot settle in
advance (Track A, U2); it is discovered at the demonstration, inside
the claim fence — a field-layout question, not a design blocker.

### 2.4 The live path, hop by hop, each with its witness

The BD-1 lesson (INDEX 419) is this track's standing law: a flag
committed in the adapter but never carried by the live transport was
certified by witnesses watching a staged path. **Every hop below is
witnessed at the live seam — the actual transmitted bytes and the
actual dispatch — or it is listed as unwitnessed.** The integration is
first rehearsed whole, offline, with a stub provider (Track E's
method), and the rehearsal's evidence pack enumerates these same hops.

| # | Hop | Witness |
|---|---|---|
| 1 | Assembly judged and issued (mode, grants, bounds, case, manifest hash) | The A1 assembly record and the examiner's judgement receipt — the run's authority, inspectable before anything moves. |
| 2 | Stocking: room created from the manifest | The room state record (recipe, mount identity, envelope parameters, source hashes) + the stock-verification smoke results (§1.2), recorded before activation. |
| 3 | The outbound provider request, as transmitted | The live transport's own capture of the exact request body (bounded raw capture at the connector seam): the offered `container.exec` definition, the mode's fields, and **every field the design commits** verified present in the transmitted body — not in a staged construction. This hop is where the residual uncertainty (§2.1) is witnessed resolving, one way or the other. |
| 4 | The provider response, as received | The response-evidence artifact: complete bounded capture, hashed, before any interpretation. |
| 5 | Classification and translation | The translation record, persisted before dispatch, bound to hop 4's artifact hash; refusals recorded with their class. |
| 6 | The doorway dispatch decision | The dispatch record: grant checked, shape checked, dispatch identity issued — or the refusal, recorded. |
| 7 | The room execution | The rig's per-execution record in the room state: the command as proposed, the observed lifecycle, envelope outcome and any pressure events, output accounting, the CPU ledger charge — plus the host witness's independent views of the run's room (mount assessment against the recipe, kernel-read identity), taken from outside the room. |
| 8 | The result's carriage back | The **next** outbound request's captured body (hop 3's witness, next iteration): the result object present in the package carriage under the provider call ID of hop 4's call. |
| 9 | The deliverable at the wall | The deliverable's hash taken host-side from the tree at the run's end, continuous with the hash the record and checker carry. |
| 10 | Reconstruction | The independent checker over hops 1–9 (§3.5): the run is what its record reconstructs, or the divergence is the finding. |

### 2.5 Record events and the terminal readout

Each execution produces, in the framework's record, the event chain
the native line already established — call entered, response evidence
captured, translation recorded, tool requested, dispatch issued,
execution outcome — with the execution outcome carrying the §2.3
result's identity (its room-state execution record referenced, its
exit status, byte counts, truncation, termination, and charge
summarised in the event). The room's own per-execution record (§2.4,
hop 7) is the execution's detailed evidence; the framework record
points to it, and the checker reconciles the two.

The terminal readout (built and closed, INDEX 447) renders the same
event sequence live, as Ben's standing requirement specifies: each
execution call appears as it happens — `container.exec`, the provider
call ID, a bounded summary of the `cmd` array, dispatch status, and
the returned result's summary (exit, bytes, truncation, termination)
— with refusals, stalls, pressure, and the run's ending all shown as
themselves. The saved Markdown transcript is the analysis aid
afterwards — including for the learning loop (§1.5): what the worker
reached for is read off the same lines the checker reconstructs from.
The readout observes; it never exercises authority.

---

## 3. The run (Track F)

### 3.1 The assembly

A generated agent, assembled for this one bounded task through the A1
lifecycle — proposal, generation, verification, examiner judgement,
pack, issue authorisation, activation — with identity declared at
assembly and the provider-reported model identity preserved under
A1's standing distinctions (declaration / provider-reported /
verified; the run claims only what stands).

- **Model:** `openai/gpt-oss-120b` — the pinned model of the whole
  worker line.
- **Route: NVIDIA** (`integrate.api.nvidia.com`), per Ben's fork call
  (INDEX 418): **GPT-OSS on NVIDIA first, Nemotron after.** The
  NVIDIA-route probe build is passed and closed (INDEX 404); its run
  release was always deferred to this stage. What must be verified at
  release is named in §3.6.
- **Mode: judged native.** The paper proposes the assembly be judged
  **native** at assembly, as the examiner judged native1's phase 2
  (INDEX 415): the execution tool exists as a host-defined tool
  definition, the native adapter is the built and closed path for
  exactly this, and the worker's evidenced reach is a native call.
  The judgement is the examiner's to make at assembly; this paper
  records the proposal and its grounds. (This answers Track F's open
  question — how the assembly's mode is judged for the room
  configuration.)
- **Skills:** none. The assembly records an empty skill list honestly,
  as the standing scope does; skills are A4's province and are not
  smuggled in.

### 3.2 Grants

- **The execution tool** (`container.exec`, shape `{cmd: string[]}`) —
  the one framework grant this demonstration issues. Inside the room,
  the worker's acts are environmental (§2.2): reading the sources,
  drafting, and writing the brief are things it does with its own
  tool, inside its own office, not framework tools requiring separate
  grants.
- **The retrieval tools are NOT offered in this demonstration.** The
  standing run scope's sandbox grants (`sandbox.read` / `sandbox.
  write` and the retrieval family) belonged to the pre-room
  configuration. The room-only configuration for the first
  demonstration was accepted at the design's examination (INDEX 425)
  and carried in Rev 2 §1 and Track F's statement: the worker reads
  its sources through its own execution tool — which is the behaviour
  this demonstration exists to observe. This is that demonstration's
  selected configuration, **not** a permanent prohibition on mixed
  configurations; a later run may offer both families, under its own
  release.

### 3.3 One coherent budget

| Bound | Value | Source |
|---|---|---|
| Loop step ceiling | 12 steps | The standing run scope. |
| Activation deadline | 600 s | The standing run scope; the one authoritative clock. |
| Adapter per-call span | 300 s | The run scope's attempt-4 addendum, carried forward: a call may use up to 300 s, never more than the activation budget remaining. |
| Room envelope | §1.4 in full | Declared at stocking; the building's parameters for this run. |
| Provider pacing | Set at release, from the NVIDIA route's own evidence | The Groq route's TPM accounting does not transfer; the release examination states the route's pacing and per-request budget from its catalogue and limits, as every live release before this one has. |

The bounds are ceilings, not targets (the run scope's settled
wording). A bound's exhaustion is a recorded termination condition,
reported as itself.

### 3.4 The assignment, exactly as scoped

*"Read the source documents in your sandbox. Write `brief.md`: a
plain-words brief, at most ~600 words, that a newcomer could read to
learn what this framework is, what has actually been proven, what has
not been proven, and what remains to be built. Stay accurate to the
sources; invent nothing; where the sources disagree with each other,
say so."* — with the sandbox now the room: the sources at
`work/sources/`, the deliverable written to `scratch/brief.md`
(§1.3). One worker, one part, no continuation: the worker yields or
stalls; nothing continues its work.

### 3.5 Outcomes, and what each establishes

- **Completion** (the loop ends by the worker's yield inside bounds,
  `scratch/brief.md` present): establishes that a generated worker,
  given its own tool inside a case-stocked room, completed the
  standing assignment under the record — the immediate proof (§5).
  The brief then goes to the two separate judgements the run scope
  settled: Vane's structured accuracy examination (claim-by-claim,
  then coverage and distortion) and Ben's usefulness judgement
  (Track H). Neither borrows the other's authority, and neither is
  implied by completion.
- **Stalled** (provider refusal — including the §2.1 delivery
  uncertainty resolving against us — translation refusal, envelope
  termination, deadline): establishes where the path broke, from a
  complete record; composition remains untested to exactly the extent
  the stall precedes it, and the report says so. A stall is a result,
  reported plainly, with the lesson named.
- **Declined / yielded without the deliverable:** a recorded outcome
  of the same standing; the record shows what the worker did instead,
  and the accuracy examination has no product to examine — stated,
  not filled in.

**The checker story.** The independent checker reconstructs the run
from its record, extended for an execution-tool run (Track D's
discipline): stocking equals the manifest (source hashes, recipe,
envelope parameters); the two witness views reconcile (in-room
pre-flight and smoke results against the host witness's mount and
identity views); every room execution corresponds to a doorway
dispatch, a translation record, and a response-evidence artifact —
no execution without its chain, no chain without its execution; the
room's CPU ledger is consistent with the per-execution charges; every
termination stood inside the declared bounds; the deliverable's hash
is continuous from the wall to the record. Track D's negative
witnesses carry over: the tampered records (mutated delta, missing
witness, swapped deliverable) must fail this checker, each shown
failing, before the run — a checker that also accepts tampered
records has established nothing. **The checker finding and the
accuracy finding are separate findings** (the run scope's correction
C): a clean record does not establish an accurate brief; an accurate
brief does not establish a valid record.

### 3.6 Release gates

In order; no gate is skipped, merged, or satisfied by an earlier
line's pass:

1. **This paper examined** (the examiner) — the preparation as a
   whole: stocking, connection, run shape, claim fence.
2. **Track C stocking built and verified** — the manifest, the smoke
   set passing in the stocked room, the envelope declared; examined
   against §1.
3. **Track G, before any live worker is inside the room** — the
   scripted hostile-and-confused suite against the stocked room (the
   programme's order: G follows B–C and always precedes F): escape
   and exfiltration attempts, resource floods, malformed and endless
   commands, enormous outputs — each ending as a recorded termination
   with the walls intact. Its evidence pack examined.
4. **Track E integration built and examined** — the doorway
   connection wired through the harness's real transport; the full
   offline rehearsal with a stub provider walking every hop of §2.4,
   its witnesses reconciled; an unwitnessed hop is a failed
   rehearsal, not a footnote.
5. **Release examination for the live run** — the release states, and
   the examiner verifies: the exact assembly (model, route, mode
   judgement, grants, bounds, case, manifest hash); **the route's
   catalogue identity** — that NVIDIA serves the pinned model under
   the exact id `openai/gpt-oss-120b`, checked against the route's own
   catalogue at this gate, under the flagged-conflict rule: a
   mismatch returns as a flagged conflict for a decision, **never a
   substitution** of another model; the route's pacing and budget;
   and Ben's heads-up, given before the run as with native1 — a
   heads-up, not a gate.
6. **ONE run.** No rerun, no configuration change, no continuation
   without a new release.

---

## 4. What this demonstration does not claim

- **Not collaboration.** One agent works alone. Against Vane's three
  levels (INDEX 459): this run is **level one, the immediate proof** —
  one generated agent doing real work in its own office. It is not
  level two (the framework being built: process-tree work,
  coordinated agents, shared contributions, shared thought, gates
  during the work) and it is not level three (the eventual proof:
  agents genuinely collaborating). A successful run must not shrink
  the destination, and must not be described as collaboration, as a
  handoff success, or as the framework working — it is the first
  working piece of the larger system, claimed as exactly that.
- **Not production containment.** The room's stated limitations ride
  along, in summary, unsoftened: there is **no kernel-enforced
  aggregate envelope on this host** (cgroup controllers are not
  delegated; the envelope is the building's userspace census at 50 ms
  with its measured granularity — fast-spike overshoot measured in
  the spreads RIG-NOTES records); the CPU limit is a **cumulative
  accounting budget, not a hard execution ceiling** (work completing
  between observations can exceed it; the excess is charged exactly
  and further calls refused); there is **no user-namespace isolation**
  (identity rests on the per-room uid drop plus the zeroed capability
  bounding set — an adaptation, not equivalence); there is **no CPU
  rate limit**; the lifecycle record is the **observed** lifecycle,
  sampled, not a complete trace; if the reaper dies in a sweep, that
  call is charged the census figure with its bounded tail loss; the
  supervisor instance stands outside the envelope boundary; and if a
  ledger failure's own record cannot be written, the failure survives
  only in-process. The demonstration runs inside these limitations,
  knowingly, at demonstration scale.
- **Not proven composition — that is what is being tested.** Across
  ten prior runs the worker never reached the assignment's composition
  step; its competence at reading sources through its own tool and
  writing the brief is **untested**, honestly framed. This run tests
  it. Whatever happens, the result is reported at its true size.
- **Not the run scope's wider fence, narrowed or widened.** The run
  scope's claim fence stands: a success supports the composed-pieces
  claim for *this* configuration (assembly, doorway, room, one
  assignment); it does not support claims about skills, a complete
  worker lifecycle, verified termination and blind continuation,
  collaboration between generated workers, or the founding
  proposition. The sources are project-produced, so the brief is an
  independent examination of the worker's synthesis against fixed
  project records — not independent validation of the project's
  claims.

---

## 5. Open items this paper cannot settle

| # | Item | Owner |
|---|---|---|
| 1 | Whether the NVIDIA route **delivers** a well-formed `container.exec` call when the tool is offered (Track A's residual uncertainty, transferred to this route: the Track A evidence is the Groq route's). Resolved only by witnessing the live transport end to end — rehearsed at gate 4 as far as a stub allows, settled at the run. | Integration witnessing (gate 4), then the run itself; a failure returns to the examiner as a recorded delivery failure. |
| 2 | Whether the worker consumes the room's result contract (§2.3) fluently — the layout is the room's own, and no observation of an exec result being consumed exists (Track A, U2). Discovered at the run; a layout change afterwards is a field change, not a redesign. | The run's evidence; any change is the examiner's to approve. |
| 3 | The assembly's mode judgement for the room configuration — proposed native (§3.1), with grounds. | The examiner, at assembly (gate 5's release states the judgement made). |
| 4 | The NVIDIA catalogue identity for `openai/gpt-oss-120b` — unverified until gate 5 checks the route's own catalogue; under the flagged-conflict rule a mismatch is a decision point, never a substitution. | The release examination (gate 5); a conflict goes to Ben. |
| 5 | The route's pacing and per-request budget on NVIDIA — the Groq accounting does not transfer, and this paper asserts no figures for a route it has not measured. | The release examination (gate 5), from the route's own limits and catalogue. |
| 6 | Track G's suite has not yet run against the stocked room; its findings could add consolidated floor fixes — applied in one pass, only where they block the demonstration (INDEX 456's operating rule). | The Track G build and its examination (gate 3). |
| 7 | Ben's standing calls, untouched by this paper: the Stage 3 job pick (this demonstration runs the *standing* assignment, which is not it); the shared multi-occupancy workshop (INDEX 454) — a named design question for after one agent works; the accidental run's disposition (`live-demo/first-worker-probephasecheck/`), still preserved untouched. | Ben, at his own time; none of them blocks this demonstration, and none is decided by it. |

---

*Prepared 2026-11-24, from the record: the operative room design
(Rev 2), Track A's closure and evidence assessment, the closed rig's
notes, the standing run scope, the accepted track programme, and
INDEX 448/454/455/457/459. Where the older papers and the later
record differ, this paper follows the later record and says so in
place (Rev 2 §1's room-only configuration over the run scope's
pre-room grants; Ben's fork call over the run scope's original model
and route; Track A's closure over Rev 2 §2's held-open interface).*
