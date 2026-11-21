# PLAN — A Collaborative Agent Framework

**On paper, 2026-11-21. Written by Remmy from the discussion Ben commissioned — Remmy and Vane: what a framework should have, the attempts, where they succeeded and failed, the lessons. For Vane's examination, then Ben's ruling. This plan authorises nothing by itself.**

## The foundation (agreed in the discussion)

Live agents. Shared work. Visibility. Interaction. Disagreement. Coordination. A durable record.

## The distinction the plan is built on (settled in the discussion)

Communication is not collaboration. A shared record is not collaboration either. **Collaboration is agents interacting through shared work — their contributions changing the work and influencing one another — with the record making that interaction durable and recoverable.**

The attempts examined (AutoGen, CrewAI, MetaGPT, ChatDev, LangGraph, and our own subagents and Room) each hold one half of that or neither. None joins the two as its centre. This plan builds the joined thing.

## The six lessons (as amended and settled)

1. Build live collaboration around shared work and a durable record — the joined thing is the centre.
2. Structure belongs in the record and at the joints, not in a prescribed speaking sequence. Prescribed workflows can produce coherence, but they constrain the form collaboration can take.
3. Conversation is a view over the work, never its underlying state.
4. Shared state alone does not make a collaborating crew.
5. Design explicitly for the systemic failure points the research identifies — specification, organization, coordination, verification — without claiming every failure is systemic or the list exhaustive.
6. Participation is not authority. The crew may examine and check its own contributions; it cannot be the sole authority certifying its own work. Independent examination stays distinct.

## The sequence (Ben's order)

**This plan → the design paper → the framework built from the design → then adding, one piece at a time.** Rules and tests are added after the working framework exists, against something real. Nothing is built from this plan directly; the design paper comes next, and Ben rules on the paper before any build.

## Stage 1 — The design paper

**What:** a process tree (the whole shape of the framework) and a spec sheet (its parts, interfaces, the shared working environment, the record, the rules of interaction), written from this plan and the six lessons. Examined by Vane against the foundation and the lessons. Ruled on by Ben.
**Done when:** Ben can read the paper and say what the framework is, what each part does, and what gets built first — and the paper holds nothing the lessons forbid: no speaking scripts, no conversation-as-state, no crew certifying its own work.

## Stage 2 — Build the framework core

**What:** the smallest complete implementation of the design: the shared working environment where agents interact through the work itself, the durable record beneath it, live agent seats receiving briefcases, an orchestrator, and a read-only observer. Built from the spec sheet, not improvised around it.
**On the substrate:** the accepted prototype already provides much of the record half — fabric, harness, event history, independent checker, observer — proven mechanically, with scripted drivers only. Whether the build reuses it, and where, is a decision the design paper makes explicitly; this plan assumes neither way.
**Done when:** the framework stands as a running thing Ben can open and watch, ready for a job — collaboration possible end to end, nothing yet added beyond the core.

## Stage 3 — The first collaboration

**What:** two or three live agents, onboarded and briefcased, working one small real job inside the framework — a job chosen with Ben because a crew genuinely helps it. The examiner watches the record, not the talk.
**Done when:** Ben receives the job's deliverable **and** the record of its making, and can point in that record to at least one place where one agent's contribution changed another agent's work — and to any disagreement that stood, and how it was settled.

## Stage 4 — Add, one piece at a time

**What:** the pieces the working framework shows it needs, in the order it shows them. Candidates, named now so they are not surprises: onboarding as a repeatable mechanism; gates with live holders at the joints; the briefcase office as a mechanism; then the rules and the tests, written against the running framework's real behaviour. Each addition follows the same small cycle: paper first, examined, built, reported as a finished result or honestly as stopped.
**Done when:** each piece is either in and working, or named and deferred by a ruling — never accumulated silently.

## Stage 5 — Through time

**What:** repeated real jobs in the framework. The crew's own working format is observed as it forms and written down from observation. At least once, an honest comparison: the same class of job done by one agent with equal resources.
**Done when:** Ben can see the crew getting better in ways he can point at — or see that it isn't, stated just as plainly. His judgement at the end of this stage decides what the framework becomes next, including whether an autonomous form is ever papered.

## Held lines (from the lessons, binding on every stage)

- Structure in the record and at the joints; never a script for who speaks when.
- Conversation is a view; the record is the state.
- The crew checks its own work; it never solely certifies it.
- A step not in this plan is not taken. Adding one is a visible act, and a change of direction goes to Ben first.

## Parked (intact, not in this plan's path)

- The conformance line — gate designs, trials build, version hunt, candidate work. Record complete on the shelf.
- The old REV line / Relay 01 run-02 — its fate is Ben's open decision; this plan does not need it either way.
- Observer v2 — deferred at Ben's word; the observer as it stands serves Stages 2–3.

## Ben's decisions

1. **Go / no-go on this plan.**
2. **The first job** (Stage 3) — chosen with him when the framework stands.
3. **The system's name** — open since 2026-11-21 02:10; blocks nothing.
4. **The delegation boundary** — not asked until Stage 5's judgement; nothing in Stages 1–4 needs it.
