# Vane's examination — AIvory plan (2026-11-25)
PB-ID: pb-mwwxw2k8-2-k772
Examiner: Vane
Sources read directly from Q420/ainternet-shelf:
- `ben-teamily/PLAN-AIVORY-2026-11-25.md`
- `ben-teamily/AIVORY-FULL-SCOPE-2026-11-25.md`, Parts A–D
- `ben-teamily/AIVORY-DASHBOARD-SCOPE-2026-11-25.md`
- `ben-teamily/VISION-2026-11-25.md`
- `aivory/feed.json`
- `aivory/index.html`, `aivory/server.mjs`, `aivory/package.json`,
  `aivory/README.md`
- relevant collaboration-framework source tree, office/assembly/dispatch/
  loop modules, tests, run records and opening transcripts.

## Ruling in brief

**The plan's sequence is sound and should be retained. The plan is not yet
build-ready.** It correctly separates the current dashboard correction,
real dispatch, live conversation, and Ben's daily-use acceptance. It also
correctly makes the office-cycle-v2 cold proof a prerequisite to relying on
that engine.

The specification and process tree have now been drafted from the full
scope, including Part D. No dashboard code or framework code was changed
during this examination. Build stages remain closed pending Ben's rulings.

## 1. Plan examination

### What is sound

1. **The order is right.** Specification before process tree; then close
   current dashboard gaps; then dispatch; then live conversation; finally
   implement and accept on Ben's machine. This prevents the UI from being
   mistaken for a working agent system.
2. **The strip discipline is right.** Build only what serves the stage's
   acceptance. Do not mix UI correction with framework dispatch or
   conversation transport.
3. **The gates are right.** Vane examines evidence; Ben rules at stage
   boundaries. Ben's outward, spend-bearing, and irreversible decisions
   remain his.
4. **Part D is binding method, not background reading.** Shelf transport,
   direct authorship, feed-derived state, receiving-end verification,
   scheduled-task deployment, one-letter-at-a-time correspondence, and
   the office-cycle-v2 run contract have been carried into the spec/tree.
5. **The engine is not to be rebuilt in the dashboard.** The existing
   framework's doorway, authority, assembly, dispatch, executor, and loop
   remain the governing machinery. AIvory is its interface.

### Corrections and additions required

**A. The feed describes runs, not offices.** The current feed has 17 run
records. Treating these as 17 current offices is incorrect. The UI currently
does exactly that: it creates a sidebar office entry for each historical
run and titles it with the run ID. The office/role is the durable identity;
a run is historical provenance; a model is the occupant. S3 needs a
separate current-office inventory sourced from actual framework state, with
a separate historical run ledger.

**B. The feed is not yet a sufficient dashboard contract.** Its current
top-level keys are `kind`, `note`, `job`, and `runs`. It has no schema
version, generated timestamp, current offices, role identities, occupant
names, assembly/grant records, journal references, transcript references,
briefcase access events, decision queue, artifact paths, or token/time
accounting. These are not UI details; they are data-source requirements.
The UI must not infer them.

**C. The displayed timestamp is wrong in kind.** The current work strip
labels the browser's local fetch time as UPDATED. The specification requires
the feed's own generation timestamp. Add it at the feed generator and
display that value. A client fetch time may be shown separately as a
diagnostic, never as the feed update time.

**D. The existing sidebar mislabels its secondary field.** It shows a
shortened model name where the scope calls for live status. Role-first
office name, occupant/model, and lifecycle status are three separate fields.

**E. Chat persistence is not live conversation.** The current server stores
human posts server-side. The Orchestrator endpoint stores a request as
QUEUED; the office endpoint stores a post and a truthful QUEUED line.
There is no framework dispatch from the job endpoint and no worker message
transport from office chat. The Collaboration Room has human posts and
feed-derived completion records, but no real crew-to-crew exchange. The
plan's shorthand "chats are chats" must not be read as saying worker
conversation is already wired.

**F. The Collaboration Room's acceptance is consequential.** A real
exchange must change shared work: one worker contributes to a shared
briefcase artefact, another reads/challenges/builds on it, and the downstream
contribution or result changes. A message stream alone is not enough.

**G. The office furniture is under-sourced by the current feed.** The
feed does not expose journal entries, dated office records, item-level
access events, actual transcript pointers, or output artifact paths. The
current Journal empty state is therefore honest but incomplete; the next
feed contract must expose actual sources. Existing real opening transcripts
are present in the framework shelf for demo-round6 and demo-round7, but
the dashboard does not load them.

**H. The feed publisher is not in the aivory shelf directory.** The
`aivory/` directory currently contains the page, server, package metadata,
README, ignore file, and generated feed. The generator/publisher that creates
the feed from framework records is not present there. Its canonical source
and deployment route need to be located before S3 changes the schema; the
feed must remain generated from the authoritative records, not hand-edited.

**I. The office-cycle-v2 proof location is unresolved.** Part D says the
stripped office-cycle-v2 contract has 457/457 witnesses and its cold proof
is still owed. The plan names that cold proof `demo-gptoss6`. A recursive
read of the collaboration-framework shelf tree did not locate a
`demo-gptoss6` directory or a separately named office-cycle-v2 source
file. The existing framework `loop.py` and its A1/A2/A3 tests are present,
but they are not evidence that the distinct office-cycle-v2 cold proof has
run. Locate the canonical source and proof record; do not silently
substitute an earlier run or the witness count.

**J. Laptop deployment is a recorded plan claim, not independently verified
in this examination.** The plan records the dashboard running under the
`AIvoryDashboard` scheduled task at `http://127.0.0.1:4173`. The shelf
contains server code and deployment instructions, but this examiner cannot
inspect Ben's laptop's Task Scheduler or make a request to its loopback
endpoint. AT-09 remains an actual receiving-end test.

### Feed cross-check

The feed was fetched and parsed directly. Recomputed from its 17 run
objects:

- 4 outcome=completed; 12 outcome=stalled; 1 outcome=declined.
- 875 events; 62 dispatches; 80 iterations.
- 3 briefs filed.

These agree with the plan's headline totals (the plan does not state the
80-iteration aggregate). The declined run has `completed: true`; counts
must distinguish the explicit outcome from the boolean field rather than
assuming they mean the same thing.

## 2. Open design decisions

The plan correctly leaves these to Ben:

1. Persistent Orchestrator seat, or an Orchestrator generated per workspace?
2. Standing Collaboration Room throughout the job, or a temporary room per
   exchange?

Two further rulings are needed to avoid implementation assumptions:

3. Confirm that current offices and historical runs are separate entities
   in the feed and UI. This is necessary to prevent the 17 historical runs
   from becoming 17 current offices.
4. Identify the canonical office-cycle-v2 source and demo-gptoss6 cold proof
   location. The proof is a prerequisite, not a preference.

## 3. Artifacts produced

- `ben-teamily/AIVORY-SPEC-2026-11-25.md` — numbered requirements,
  acceptance tests, evidence gaps, and Ben-owned decisions.
- `ben-teamily/AIVORY-PROCESS-TREE-2026-11-25.md` — staged process tree,
  node contracts, dependencies, evidence, and explicit allow/correct gates.

Both were written from the full source scope, including Part D, and must be
read back before their pointers are sent.

## 4. Current stage state

- Plan examination: complete.
- S1 Specification: drafted; Ben's line-by-line ruling pending.
- S2 Process tree: paper draft prepared; subject to S1 acceptance and
  Ben's Gate 2 ruling.
- S3 Build A: not opened.
- S4 Build B: not opened; cold proof and Orchestrator ruling outstanding.
- S5 Build C: not opened; Collaboration Room ruling outstanding.
- S6 Implement: not opened.

**Recommendation:** accept the sequence, correct the data model before
building, and do not open dispatch until the actual office-cycle-v2 source
and cold proof are in hand. The highest-risk error would be to make the
dashboard look as though it has a live workforce by promoting historical
runs into offices or treating persisted human posts as worker conversations.
