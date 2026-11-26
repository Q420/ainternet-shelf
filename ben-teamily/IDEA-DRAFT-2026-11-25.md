# THE IDEA — Ben's version of Teamily (draft v6, 2026-11-25)

*Drafted at Ben's direction, 2026-11-25. v2 carries Ben's own description of the
shape (~18:05 MST): the dashboard is the product; chat is one part of it. v3
carries his measure of the distance (~18:05 MST): **"It's not far off from what
we have now. It's just the interface that's different really."** v4 carries his
interface sketch (~18:06 MST): instruct the agent from the interface, show the
shared briefcase, and watch the agents accessing and using it as they use it —
with the orchestrator chat as one of the parts. v5 adds his two live panels
(~18:07 MST): the output panel and the resources panel. v6 adds the part Ben
named the most crucial of the whole thing (~18:08 MST): the collaboration
window, where the agents talk and work with each other. A draft idea,
not a spec and not a build order. The name is Ben's to choose (his wordplay
from 2026-11-21 — TAIMWORK — sits in this territory).*

## The idea in one breath

A **dashboard** where Ben runs a crew of real AI agents: he hands a task to the
orchestrator, she generates the agents that job needs, each generated agent
appears in its own chat window on the dashboard, and Ben can go into any agent,
see what it is actually doing, and talk to it there — while underneath, every
agent is a real framework worker with a room, a briefcase, a journal and a
record, not a chat persona.

## The shape, in Ben's terms

- **The dashboard is home.** The whole crew and all running work, visible at a
  glance: who exists, what job each is on, what state it is in.
- **The orchestrator is the intake.** Ben hands a task to her — in plain words.
  She is the one who generates the agents for that job: the agent generator,
  held by a seat Ben can talk to, not a hidden mechanism.
- **Generation populates the dashboard.** Each agent she generates for the job
  appears in its own chat window. The window is how Ben talks to that agent —
  ask it, steer it, answer its questions — for the life of that job.
- **Every agent opens up.** Ben can go into any agent who is doing something
  and see what it is doing: its briefcase, its journal as it grows, its work as
  it lands — the room, made visible. Watching is not a log file; it is looking
  over the worker's shoulder.
- **Chat is one part of it.** Conversation lives in the per-agent windows (and
  with the orchestrator). Around the chat sit the other parts: the crew view,
  the per-agent drill-in, the work itself and its record.

## The interface, part by part (Ben's sketch)

- **The collaboration window — the most crucial part of the whole thing.**
  A chat window where the agents collaborate WITH EACH OTHER: not Ben talking
  to an agent, and not agents reporting upward, but the crew in one shared
  conversation — a finding handed across, a draft challenged, a question one
  agent puts to another whose work it touches. It is the framework's founding
  definition given a window: collaboration is agents interacting through
  shared work, their contributions changing the work and influencing one
  another. The talk is anchored to the shared briefcase and the shared files —
  they argue over artefacts that exist, point at the journal, at the draft in
  the output panel — not free-floating banter. Ben watches it live like
  everything else on the dashboard, and can step into it when he chooses.

- **The orchestrator chat.** A standing chat with the orchestrator on the
  dashboard itself. Ben hands her tasks there, asks her questions, watches her
  account for the crew. This chat is a part of the interface — the management
  conversation lives beside the work, not in a separate app.
- **Instructing the agent.** When a job is created, its instruction is visible:
  what the agent was told, what it was given, what it may use. Ben can instruct
  an agent directly in its window, and the instruction stands in the record —
  nothing is told to an agent that the dashboard cannot show.
- **The shared briefcase, on show.** The briefcase is a visible object on the
  dashboard: its contents as stocked — the brief, the files, the tools, the
  terms — openable by Ben at any time. Shared: the crew works from the same
  stocked case and the same files, as Ben ruled for the crew shape.
- **Watching them use it.** The live heart of the interface: as an agent works,
  Ben sees it access the briefcase and use what is inside — a file pulled, a
  block read, a journal entry appended, a contribution filed — each access
  shown as it happens, against the item it touched. Not a log to read later:
  the briefcase in use, watched live, the way the wall's readout already shows
  a worker's calls — here tied to the things the calls touch.
- **The agent window and the drill-in** — as above: chat with the agent in its
  window; go inside it to see the doing itself.
- **The output panel — file generation, live.** A panel that shows the agent's
  output as it is being output: files appearing in the room as they are created
  and growing as they are written — the draft taking shape line by line, the
  deliverable the moment it is filed. Ben watches the work product form, not
  just the process that forms it.
- **The resources panel — usage, live.** A panel that shows resources as they
  are being used: the calls an agent has made and what each carried, the tokens
  spent against the road's limits, the dispatch bounds and how much of them
  remain, the time a job has taken. The machinery already keeps these figures
  (the call ledger, the bounds, the budgets); the panel makes the cost of the
  work as visible as the work itself — nothing burns in the dark.

## How a job flows through it

1. Ben hands the orchestrator a task.
2. She breaks it into the work and generates the agent (or agents) for it —
   model, identity, skills, tool grants, briefcase — per the framework's
   assembly.
3. The dashboard gains the agent's window; Ben sees it appear, named for its
   job.
4. The agent works in its room — pulling material in blocks, journalling,
   producing contributions — while its window carries the conversation and its
   drill-in shows the doing.
5. Work lands back through the window; anything needing Ben's approval arrives
   at his chair as a decision, not a notification. When the work yields, the
   agent is done; the record of the job remains on the dashboard.

## What is already proven (the honest inventory)

- **Agent generation and assembly** — built and passed (the framework's agent
  layer, November 2026). The orchestrator's core act already exists.
- **A generated agent completing real work in its own office, beginning to
  end** — first demonstrated 2026-11-24 (round six).
- **The worker using its own tools natively** — witnessed live 2026-11-25.
- **Seeing what the agent is doing** — the terminal readout already renders a
  worker's tool calls and progress live; the wall already carries it to Ben's
  screens. The drill-in is that, productised per agent.
- **Continuity that survives the worker** — role memory and the journal mean a
  job's thread outlives any one occupant (three models have sat in one role's
  chair).
- **A working multi-seat chat discipline** — the Pulse Bridge has carried real
  directed work between Ben, the orchestrator and the examiner for weeks.

## What makes his different from Teamily

- **A dashboard of real work, not a chat with personas.** Teamily's centre is
  the group conversation; Ben's centre is the work — who is doing it, what
  state it is in, what it produced. Chat serves the work here, not the reverse.
- **Generation is visible and held by a person-shaped seat.** The orchestrator
  generating an agent is an act Ben watches and can question — not a routing
  feature behind a text box.
- **Every agent opens up.** Its briefcase, journal and record are inspectable.
  A claim about finished work can be traced, not just read.
- **Approval stays with the human.** The briefcase transfers work state, never
  approval authority; outward and irreversible acts arrive at Ben's chair.
- **An examiner in the building.** Quality is a seat with authority to send
  work back — the ternary shape that produced the results.
- **His routes, his costs.** The crew runs on the models and tiers Ben
  chooses, free routes included — not a per-seat subscription to someone
  else's models.

## The first version (leanest shape)

- The dashboard: crew view + running jobs + states, riding the office/wall
  lineage that already exists.
- The orchestrator's intake: Ben states a task; she generates ONE agent for it
  (the multi-agent crew generation is growth).
- One chat window per generated agent, populated at generation.
- The drill-in: the agent's journal and live activity, read from its record.
- **Not in the first version:** outside users, billing, app stores, a
  documents/slides studio, voice, group chat with many humans.

## How far off it is (Ben's measure: not far — the interface)

What already stands, in working form:

- **The engine** — assembly, rooms, briefcases, journals, records, gates: the
  framework, proven piece by piece through November.
- **The orchestrator** — the intake-and-generation role exists and works daily;
  it is Remmy's chair in the present setup.
- **A crew surface with dispatch** — the October AI office: named crew, task
  board, brief queue, a dispatcher turning briefs into crew work.
- **The live drill-in, in crude form** — the wall and the terminal readout
  already show a worker's calls and progress as they happen, on Ben's screens.
- **Chat transport between seats** — the Pulse Bridge, carrying real directed
  work for weeks.

What is actually new — the interface, and only the interface:

- **One dashboard** uniting those pieces: crew, jobs, states, windows.
- **Generation made visible** — an agent appearing in its own chat window when
  the orchestrator creates it, as an event Ben watches.
- **The drill-in per agent** — briefcase, journal, activity — as a designed
  view into the record, replacing the wall's raw panes.
- **The orchestrator's intake as a place on the dashboard**, not a separate
  chat Ben happens to have.

So the eventual build is interface work on a standing engine — prototyped
first, judged on its own page, per Ben's standing rules — not a new system.

## Open questions (Ben's calls)

1. The name.
2. Who else sits in it — crew only, or his people too?
3. The orchestrator's chair — Remmy herself in the product seat, or a
   generated orchestrator per workspace?
