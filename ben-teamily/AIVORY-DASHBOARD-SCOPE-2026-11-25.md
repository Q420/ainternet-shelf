# AIVORY — DASHBOARD SCOPE (2026-11-25)

The full scope for the AIvory dashboard build, assembled from Ben's own words,
his rulings, and the examined vision (VISION v5). This document IS the brief:
a builder works from this text whole. It supersedes every earlier Remmy
summary, brief, and send_input digest for this build.

## 1. What this is

Ben's version of Teamily, on his own framework: a dashboard where a human
directs and works alongside a generated workforce of AI agents — real
generated workers (rooms, briefcases, journals, records, an examiner), not
chat personas. Working project name (Ben, 2026-11-25): **AIvory** — "because
we're creating persistent memory and what not, I think of mastadons or
elephants."

Ben's measure of the distance: "It's not far off from what we have now. It's
just the interface that's different really." The engine exists (the
collaborative agent framework: assembly, rooms, briefcases, journals,
records, live runs). The dashboard is its interface — it READS the system's
real state and DRIVES the system. It is not a simulation of an office, not a
replay viewer, and not a representation someone updates by hand.

## 2. The room, in Ben's words (verbatim, 2026-11-25)

- "A dashboard. Chat is one part of it. I can go into each agent who's doing
  something, see what they're doing, if I have a task I can hand it to the
  orchestrator and she can be the one that generates the agents for that job
  it populates the different chat windows with that agent and that's how I
  can talk"
- "we need to take what we know about how to create an agent create the
  interface make sure that we can instruct the agent we can also show the
  shared briefcase watch them accessing it and using it as they use it we
  can have the orchestrator chat this could be the way it goes"
- "file generation live view a panel that shows their output as they're
  outputting it another panel that shows resources as they're being used"
- "And then the most crucial part of the whole thing a chat window where
  each agent can collaborate with each other"
- "Individual chats for each agent. A side panel where I can choose those
  from. The main view is where all the meat and potatoes are."
- On the failed builds: "You even hard-coded a fail into it." / "You're
  simulating an office and not a dashboard." / "Why are all the chats just
  filled with different run states for different that those aren't chats"

## 3. Chats are chats (the definition this build is judged by)

A chat is a CONVERSATION: messages from participants, in order, with a
working input where Ben writes and his message posts. Specifically:

- **The Orchestrator chat** is the front door. Ben hands her a task in words.
  She is the point of coordination: on a submitted job, the office for that
  job is created and appears in the sidebar (generation made visible as an
  assembly entry in her chat: role, model, grants — from the framework's
  real assembly vocabulary). Her replies at this layer are limited to TRUE
  system statements (what the app itself did: job received, office created,
  queued state with its timestamp). She never performs a personality and
  never claims an agent has started work when it has not.
- **Each office has its own chat** — Ben's conversation with that office,
  where he can instruct the agent. Where the record holds a REAL transcript
  for that office (e.g. the Brief Writer office's opening conversation,
  demo-round6, 2026-11-24), that conversation stands in the chat, labelled
  with its run and date as record. Ben's new messages post and are stored;
  until the live conversation wiring lands, a message to an office is
  marked QUEUED in one plain system line — stated once, as fact.
- **The Collaboration Room** is a first-class chat, the most crucial part:
  the shared room where the crew's work meets Ben's voice. Entries are
  either Ben's posts (stored) or true record entries sourced from the feed
  (a run's completion with its real outcome figures), each labelled by its
  source. NO invented agent dialogue, anywhere, under any label.
- **A chat NEVER contains run states, record entries dressed as messages,
  or an "account of work."** Run states belong to the Record, the Journal,
  Output and Resources views — where they already live.

## 4. The office is the role (Ben, 2026-11-25)

"Each roll is assumed by the office therein. The office is the role the agent
slips into it." Windows and sidebar entries are titled by OFFICE/ROLE first,
occupant second. The room, the folder, the journal, the record belong to the
office; the occupant (the model) is interchangeable and is labelled from the
feed's fact (model only, unless the feed carries a name).

## 5. The briefcase (Ben's ruling, 2026-11-25)

ONE shared briefcase as the crew's shared context; a folder inside it for
each agent; the collaboration chat tells them who is doing what and how to
delegate; the crew organises itself based on role. The briefcase view shows
the real sources from the feed with true byte sizes, and a folder per
office. Access activity, when the feed carries it, shows against the item
itself — never as a chat message.

## 6. Layout — B2 (Ben's tap, 2026-11-25, from the layout images)

- Left sidebar: AIVORY header; CHATS (Orchestrator, Collaboration Room, one
  entry per office) with live status; VIEWS (Shared Briefcase, Output,
  Resources); Decisions at the bottom ("No decisions waiting" unless the
  feed carries one — never invent one).
- The stage shows ONE selected view at a time; the main view is where the
  meat and potatoes are.
- A slim work strip pinned across the top of the stage, always visible: the
  current job, the briefcase's sources as chips, live counters, and the
  feed-updated timestamp.
- An office opens up: its chat, with its JOURNAL and RECORD beside the chat
  (the B2 centrepiece). Journal = the office's briefs and dated record
  entries from the feed; Record = events, dispatches, checker where the
  feed carries it, per run.
- Mobile-first: Ben opens this on his phone. The sidebar becomes a top bar
  + selectable list; the work strip stays visible.

## 7. The live wire (Ben's condition, 2026-11-25)

"Maybe you're actually going to be a little wire live metrics into it or is
it just going to be a representation that you have to manually update
because that's not going to work." — LIVE, or it does not ship:

- All metrics and record content come from the STATE FEED at
  https://raw.githubusercontent.com/Q420/ainternet-shelf/main/aivory/feed.json
  — generated from the framework's real run records (live-demo/*/report.json),
  republished whenever the record changes. Read server-side at first open,
  on the Refresh control, and on the installed 15-minute refresh.
- Aggregates are computed from the feed at render. If the feed cannot be
  read, the dashboard says "feed unreachable — showing nothing rather than
  stale figures" and shows NO numbers.
- Job submissions in the Orchestrator chat are stored by the app as QUEUED
  job requests, labelled queued. Dispatch wiring (a queued job starting a
  real agent through the framework) is the NEXT layer and is named as such
  in the UI; nothing pretends a queued job has started an agent.

## 8. Look and type (Ben's fine-tuning, 2026-11-25)

- Palette "Luxury Tech" (his image, exact hexes): Jet Black #0A0A0A ground;
  Electric Blue #00D4FF; Neon Purple #7C3AED; Cyan Glow #22D3EE; Silver Gray
  #C0C0C0 text family. Silver-gray primary text; electric blue / cyan the
  working accents; neon purple sparingly (Orchestrator, Decisions).
  Streamlined and futuristic; NOT the old house UI; NOT the generic rushed
  AI UI (no gradient washes, no glassmorphism, no glow effects, no emoji
  icons; corner radius ≤ 6px).
- Terminal font throughout — a monospace stack for everything: labels,
  chats, panels, data.
- EVERYTHING SHOWN IS FACT (Ben): every figure, name, status and label
  traces to the feed or to the product's real furniture (the AIVORY name,
  the view names, the job and sources in the feed). No placeholder people,
  no example file names, no invented statuses, no decorative sample text —
  including empty states, which state the true fact and nothing more.

## 9. Acceptance (Ben's terms)

Ben opens it, hands the Orchestrator a job in his own words, watches the
office appear and the room work, posts in the chats like chats — and
recognises his office, or he doesn't. A single run state found inside a
chat view fails the build. A single invented figure fails the build.
