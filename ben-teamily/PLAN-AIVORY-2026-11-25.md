# THE PLAN — AIvory (2026-11-25)

*Drafted by Remmy from the full scope on the shelf
(`ben-teamily/AIVORY-FULL-SCOPE-2026-11-25.md` — vision v5 + the dashboard
scope + Part D, the methods known to work). For Vane's examination, then
Ben's ruling. Ben's ordered sequence: **plan → spec → tree → build →
implement.** This plan is paper only; it authorises nothing.*

## Where things stand (verified, 2026-11-25)

- The dashboard exists: Vane's implementation, committed to the shelf under
  `aivory/`, running on Ben's laptop under the scheduled task
  `AIvoryDashboard` at http://127.0.0.1:4173, reading the live feed.
- The feed is true: 17 runs — 4 completed, 12 stalled, 1 declined; 875
  events; 62 dispatches; 3 briefs filed.
- Chats are chats: the Orchestrator, the Collaboration Room and each office
  hold conversation; Ben's messages and queued jobs persist server-side.
- The named boundary, labelled as such in the product: framework dispatch
  and live agent conversation transport are not yet wired.
- The engine the dashboard will dispatch into exists and is rehearsed:
  office-cycle-v2 (split-on-return, budgeted opening, journal read +
  append). Its cold proof run is still owed.

## The stages

**S1 — SPEC.** The dashboard's requirements, numbered, drawn line by line
from the full scope: the chats-are-chats rule; the B2 zones; the briefcase
ruling (one shared briefcase, a folder per office, the chat as the
coordination layer); office-is-the-role (windows titled by role first);
the feed-truth rule and its aggregates; Luxury Tech + terminal type; the
queued-job contract; honest labels wherever a layer is unwired.
*Acceptance: a spec sheet the running dashboard can be checked against,
line by line, by Ben and the examiner.*

**S2 — TREE.** The process tree for the remaining build: one node per
build stage below, each with its gate — allow or correct — and its
acceptance in Ben's terms, stated before the stage opens.

**S3 — BUILD A: close the gaps to spec.** The current implementation
measured against the S1 spec; every gap closed or named. Known candidates:
the feed carries no generation timestamp (the feed generator adds one);
the Offices zone's honest empty state stands until dispatch exists — the
spec decides its exact wording.

**S4 — BUILD B: dispatch wiring.** A job Ben hands the Orchestrator leaves
the QUEUED state for a reason: it is given to the framework's assembly; an
office appears on the dashboard for the generated worker; the run executes
under office-cycle-v2; its record flows into the feed as part of the run's
own close, so the dashboard moves without anyone republishing by hand.

**S5 — BUILD C: live conversation.** The office chats and the
Collaboration Room connect to real workers: Ben's instruction in an office
reaches its occupant; the crew's collaboration runs in its room, anchored
to the shared briefcase. The stage's test is the vision's: a contribution
that enters the shared work and changes another worker's contribution or
the result.

**S6 — IMPLEMENT.** The office in daily use on Ben's machine, on a real
job of Ben's choosing. *Acceptance is Ben's §9 test: he opens it, hands
the Orchestrator a job, watches the office appear, posts in chats that are
chats, and recognises his office — or he doesn't.*

## The gates

- Each stage is examined by Vane before the next opens; Ben rules at stage
  boundaries. His own calls — anything outward, spend-bearing, or
  irreversible — stay his.
- The strip discipline governs every stage: no layer is added that does
  not serve that stage's acceptance.
- Methods are Part D of the full scope, and only Part D: the shelf is the
  transport, the source is checked first-hand, verification happens at the
  receiving end.

## Carried open — Ben's rulings, not decided here

1. The orchestrator: a persistent coordinating seat, or generated per
   workspace? (Needed by S4's design.)
2. The collaboration: a standing workspace for the crew, or a temporary
   room per exchange? (Needed by S5's design.)
3. The office-cycle-v2 cold proof run (demo-gptoss6) — the engine's live
   proof, owed before S4 leans on it.
