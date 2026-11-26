# AIvory — examined implementation specification
Date: 2026-11-25
Examiner: Vane
Inputs: `ben-teamily/AIVORY-FULL-SCOPE-2026-11-25.md` (Parts A–D),
`ben-teamily/PLAN-AIVORY-2026-11-25.md`, and the current `aivory/`
implementation and `aivory/feed.json`.

Status: **S1 examination draft — submitted for Ben's ruling.**
This document specifies the product and its acceptance. It does not authorise
a build stage. The process tree is separate and carries the stage gates.

## 1. Governing product contract

AIvory is Ben's live interface to the real collaborative-agent framework.
It must both read authoritative framework state and drive the framework
through its authorised routes. It is not a simulation, a replay-only view,
a manually maintained representation, or a collection of chat personas.

The durable entity is the office/role. A generated worker occupies that
office for an assignment; the occupant can change. Office room, folder,
journal, record, tools, and governed role context belong to the office.
A worker receives the assignment and only the task context it needs, not
the previous occupant's mental state.

The common working ground is one shared briefcase. It contains a folder
for each office. The Collaboration Room is the crew's coordination layer:
the crew organises by role there, shares findings, delegates, challenges
work, and changes the common result. Work state can cross the briefcase;
approval authority does not.

## 2. Layout and presentation

**REQ-UI-01 — B2 frame.** A left sidebar contains the AIVORY header, CHATS,
VIEWS, and Decisions at the bottom. The stage displays one selected view.
A slim work strip remains pinned across the top of the stage.

**REQ-UI-02 — Sidebar.** CHATS contains the Orchestrator, Collaboration Room,
and one entry per actual office. Office titles are role-first, occupant/model
second. Live status comes from authoritative state. A historical run is not
automatically a current office.

**REQ-UI-03 — Work strip.** Show the current assignment, actual shared
briefcase sources as chips with true byte sizes, live counters, and the
feed's own generation/update timestamp. A client fetch time must never be
labelled as the feed's update time.

**REQ-UI-04 — Office centrepiece.** An office view shows its own conversation,
Journal, and Record beside one another. Journal contains actual office briefs
and dated record entries. Record contains per-run events, dispatches, checker
findings, and other fields only where the authoritative source carries them.

**REQ-UI-05 — Mobile.** Ben's phone is a primary access context. The sidebar
becomes a top bar plus a selectable list; the work strip remains visible and
the office/chat surfaces remain usable without horizontal overflow.

**REQ-UI-06 — Visual language.** Luxury Tech palette: Jet Black #0A0A0A,
Electric Blue #00D4FF, Neon Purple #7C3AED, Cyan Glow #22D3EE, Silver Gray
#C0C0C0. Monospace terminal type throughout. Radius no greater than 6px.
No gradients, glassmorphism, glow effects, emoji icons, or generic house UI.

## 3. Conversation contract

**REQ-CHAT-01 — Conversation semantics.** A chat contains ordered messages
from actual participants, with a working input. Run states and resource
summaries belong in Journal, Record, Output, and Resources, not in chat.

**REQ-CHAT-02 — Orchestrator.** Ben submits a job in plain words. The
Orchestrator is the coordinating point, not a simulated personality. Its
messages are true system statements about actions the application actually
performed. A submitted job must create a real framework job/workspace through
the approved assembly route before the corresponding office appears.
Assembly entries expose role, model, and grants from the real framework
record. Queued is not running.

**REQ-CHAT-03 — Office conversation.** Each office has its own conversation
with Ben and its actual occupant. Real transcripts already held by the record
must be loaded and labelled with their source run/date. New messages must
reach the actual occupant through the framework's live conversation route.
Until that route exists, one honest QUEUED system line is permitted after
a human post; no fabricated agent reply is permitted.

**REQ-CHAT-04 — Collaboration Room.** This is a first-class shared
conversation for the crew and Ben. Entries are real participant messages
or source-labelled completion records allowed by the scope. The collaboration
must have consequence: a contribution enters shared work and influences
another contribution or the result. Merely displaying agent messages does
not satisfy acceptance.

**REQ-CHAT-05 — Persistence and ordering.** Conversation messages are
persisted server-side, attributed to their true sender, and returned in
authoritative order. Retries must not silently duplicate posts. Browser-local
storage is not the system of record.

## 4. Shared briefcase, office continuity, and work

**REQ-WORK-01 — One shared briefcase.** One common briefcase is visible and
openable. It contains a distinct folder for every actual office. Do not
create a separate independent case per worker as a replacement for the
shared briefcase.

**REQ-WORK-02 — Item truth.** Source names, paths, byte counts, contents,
and access activity are derived from the real briefcase/feed. Access activity
is shown against the item accessed, not as a chat message.

**REQ-WORK-03 — Office identity.** Office/role is the durable identity.
Occupant/model is an attribute of the current assignment and may change.
Historical run identifiers may appear as provenance, never as invented
office roles.

**REQ-WORK-04 — Journal and Record.** Journals and records are read from
the office's real persistent stores. The dashboard does not infer journal
entries from event counts or turn a report into a transcript.

**REQ-WORK-05 — Output.** Files appear as they are genuinely produced and
filed. Links, names, paths, previews, and byte sizes require source evidence.

**REQ-WORK-06 — Resources.** Show real usage against known limits: tokens,
dispatches, time, and other measures only when instrumented. Unknown usage
is omitted or explicitly unavailable, never estimated.

## 5. Live state and data integrity

**REQ-DATA-01 — Authoritative feed.** Read the framework-generated
`aivory/feed.json` server-side on initial open, explicit Refresh, and the
installed 15-minute refresh. Do not hand-edit or manually curate its facts.

**REQ-DATA-02 — Render-time aggregates.** Compute every aggregate from the
current feed at render. Do not hard-code counts.

**REQ-DATA-03 — Feed failure.** If the feed cannot be read or validated,
show the honest unreachable state and no figures, run records, source
inventory, or stale cached numbers.

**REQ-DATA-04 — Timestamp.** The feed must carry its own generation timestamp
and the UI must display that timestamp. Client fetch time is a separate
diagnostic and must not impersonate feed time.

**REQ-DATA-05 — Typed records.** The feed must distinguish current offices
from historical runs and expose the authoritative office/role identity,
current occupant, assignment, lifecycle status, run provenance, and links
to the actual Journal/Record/transcript/output sources. Missing fields remain
missing; the UI must not infer them from run IDs or model names.

**REQ-DATA-06 — Schema validation.** Validate feed kind, schema/version,
timestamp, and required collection shapes before rendering. A malformed
feed fails closed exactly like an unreachable feed.

**REQ-DATA-07 — Decisions.** Decisions shown in the sidebar are actual
pending decisions from the framework. Do not invent decision cards or
assume none are waiting if the source does not establish that fact.

## 6. Dispatch and live conversation boundaries

**REQ-DISPATCH-01 — Real assembly.** A queued Orchestrator request advances
only when the framework's real commission/assembly path accepts it. The
dashboard must not manufacture a worker record or label a queued job running.

**REQ-DISPATCH-02 — Assembly visibility.** The new office appears from the
real assembly/office identity and records, role-first, with model and grants
from the generated assembly record.

**REQ-DISPATCH-03 — Office cycle.** The worker executes under the approved
office-cycle-v2 contract: one budgeted opening package; one pulled block
at a time; journal read + append, never carried in packages; allow/correct
cycle gates; results split on return so one wake carries one block; the
per-call budget stated in the opening. The dashboard must consume actual
cycle state and must not reimplement the engine's authority or gates.

**REQ-DISPATCH-04 — Cold proof prerequisite.** The office-cycle-v2 cold proof
run (named in the plan as demo-gptoss6) must be located, run, and examined
before Build B relies on it. The plan says this proof is still owed; a
rehearsal or 457/457 witness count is not a live cold proof.

**REQ-CHAT-06 — Live delivery.** A message from Ben to an office reaches the
actual occupant; a worker response returns under that worker's real identity
and is stored in the office conversation. The Collaboration Room transports
real crew exchanges and shared-work references. Transport failures are
visible and do not create phantom replies.

## 7. Safety and authority

**REQ-AUTH-01 — Framework authority.** The dashboard is a client of the
framework's existing doorway, permissions, grants, checker, and record.
It must not bypass them, duplicate them with weaker UI-side checks, or
become an authority for its own actions.

**REQ-AUTH-02 — Human decisions.** Outward, spend-bearing, and irreversible
actions remain at Ben's decision point. Shared work and chat never transfer
approval authority.

**REQ-AUTH-03 — Local deployment.** Ben's established deployment is
`C:\Users\Ben\aivory`, served at `http://127.0.0.1:4173` by the
`AIvoryDashboard` scheduled task so it survives remote-session closure.
Do not replace that with a transient remote-session server. Preserve
loopback binding unless Ben explicitly approves a different exposure.

## 8. Acceptance tests

**AT-01 — Feed truth.** Page served; server feed endpoint answers; totals
reconcile to the raw feed; Refresh and 15-minute update re-read the source;
unreachable and malformed feed states show no numbers.

**AT-02 — Office identity.** Actual offices appear from framework records,
role-first; historical runs do not become offices; occupant/model is
secondary and replaceable.

**AT-03 — Orchestrator path.** Submit a human-written assignment. Verify
server persistence, framework commission, real assembly, office creation,
and the exact QUEUED → accepted/assembled → running transitions. No earlier
state may be claimed.

**AT-04 — Conversation.** Verify ordered, persisted human and worker
messages, actual sender attribution, office routing, and reconnect/reload
continuity. A stored human post without worker delivery does not pass.

**AT-05 — Collaboration consequence.** One worker's contribution enters
the shared briefcase; another worker reads/challenges/builds on it; the
final result or another contribution demonstrably changes. Verify from
source artefacts and records, not chat claims alone.

**AT-06 — Office furniture.** Open an office and verify its actual Journal,
Record, transcript, briefcase folder, and Output against the source stores.

**AT-07 — Resources.** Compare displayed values and limits to underlying
provider/framework records. No uninstrumented figure appears.

**AT-08 — Authority.** Exercise a human decision boundary and verify the
framework's existing authorisation path remains authoritative.

**AT-09 — Laptop operation.** Verify the scheduled task, page, feed endpoint,
job submission, and persisted QUEUED system line on Ben's laptop; close the
remote connection and verify the task continues serving.

**AT-10 — Visual/phone acceptance.** Verify B2, exact palette/type rules,
phone navigation, persistent work strip, and no horizontal overflow.

## 9. Known evidence and present gaps (2026-11-25 shelf examination)

The current feed was read directly. It contains 17 historical run records:
4 outcome=completed, 12 stalled, 1 declined; 875 events; 62 dispatches;
80 iterations; 3 filed briefs. Its keys are `kind`, `note`, `job`,
and `runs`. The job has title, target_words, floor_words, and sources.
Each run has run, model, outcome, completed, iterations, events,
dispatches, brief_filed, and brief_words. It has no generated_at timestamp,
office/role identity, current-office collection, assembly/grants, journal
entries, access events, token/time usage, transcript reference, decision
collection, or artifact paths.

The current `aivory/index.html` and `server.mjs` are a real starting
implementation, not a conforming final product:
- Sidebar office entries are historical run IDs, not role-first offices;
  the secondary nav label shows a shortened model, not live status.
- The work strip labels client fetch time as UPDATED; the feed itself has
  no generation timestamp.
- The server stores jobs in `.data/state.json` as QUEUED, but does not
  call the framework commission/assembly route.
- Office messages are stored and marked QUEUED, but no live worker transport
  exists.
- The Collaboration Room has human posts and feed-derived completed-run
  records, but no crew message transport or shared-work consequence.
- Existing Journal surfaces are empty because the feed does not expose the
  office journal source. Existing Output shows brief filing/counts, not live
  file artefacts.
- The existing feed's runs are historical run records, not evidence of
  17 concurrently staffed offices.
- The UI does not yet consume a feed generation timestamp or a typed office
  inventory. The current source inventory and totals are factual.
- The current server is unauthenticated and loopback-bound by default.
  Preserve that boundary.

The plan says the dashboard is running on Ben's laptop under the
`AIvoryDashboard` scheduled task and that its chats/jobs persist server-side.
That is a claim in the plan; this examination has verified the shelf source,
not independently operated Ben's laptop. Laptop acceptance remains AT-09.

The collaboration-framework shelf contains the existing assembly, office,
doorway, dispatch, executor, and bounded-loop modules and their tests.
The plan identifies office-cycle-v2 as a separate stripped build with
457/457 witnesses and an owed cold proof named demo-gptoss6. A search of
the current collaboration-framework tree did not locate a
`demo-gptoss6` directory or a separately named office-cycle-v2 source file.
That is a source-location/evidence gap to resolve before S4, not grounds to
invent an implementation.

## 10. Ben's decisions still required

These are not for the examiner to settle by assumption:
1. Orchestrator: persistent coordinating seat for the office, or generated
   per workspace?
2. Collaboration: standing workspace for the crew throughout the job, or
   temporary room per exchange?
3. The plan names demo-gptoss6 as the office-cycle-v2 cold proof; locate the
   canonical source/run and decide whether the proof must be performed now
   before Build B (the plan's stated prerequisite).
4. Confirm the proposed separation between current office inventory and
   historical run ledger as the data model. This is required to avoid turning
   all 17 feed runs into current offices.

## 11. Stage boundary

This is the S1 specification for Ben's line-by-line examination. The next
stage is S2 process tree, followed by S3 Build A only after the specification
is accepted. S4 dispatch and S5 live conversation remain separately gated.
No code has been changed by this specification.
