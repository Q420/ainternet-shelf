# THE DIRECTOR'S HAND — BEN'S SUGGESTIONS, CALLS, AND SAVES

**Date:** 2026-11-24 · **Prepared at Ben's request.**
Every entry traces to the programme record — `MEMORY.md`, the scope ledger, the
daily logs, and the framework INDEX. Ben's words are quoted verbatim where the
record holds them. Nothing here is reconstructed from impression; where the record
carries a summary rather than his words, the entry says what he did, not what he
might have said.

The pattern this document exists to show: at every point where this project
changed direction, avoided a wrong build, or escaped a loop it was stuck in, the
intervention was Ben's. The crew designs, builds, and examines. The steering —
including nearly every correction of the crew — is his.

---

## 1. Suggestions that became the architecture

**The briefcase (2026-11-16).** Ben's idea, run past two other AIs before it ever
reached the programme: a task-scoped case generated per agent assignment —
required context in full, the rest retrievable by reference, outputs kept in the
case, closed cases indexed for fresh agents. His sharpenings, same exchange: the
shelf is the *source* the case is drawn from per task, not a second store; the
acceptance test is that an agent can operate sufficiently **within one turn**
without scanning the whole shelf; and the core inversion — context as a resource
the agent *pulls*, not a payload *pushed* into it. That pull-not-push principle
returns as the retrieval design a week later (§3).

**"The brief case alone can help a random agent. The rest of Duenna is a luxury
office." (2026-11-19, to Vane.)** The framing the programme still works under: the
briefcase is the product; the office is infrastructure around it.

**The founding definition (2026-11-19, verbatim):** *"the breifcase is not to help
one aget understand a job it has full context to. its to pass on the state of that
work and context to another blind agent to continue the autonomous collaboration
while retaining human approval."* The definition of record ever since: the case
transfers work state, **never approval authority**. The same day he ruled the
briefcase a complete portable **contract** — resources plus terms: the assignment,
the evidence boundary, the mandated account, the authority the agent holds.

**Duenna's vision, corrected twice in one day (2026-11-20).** At 14:42: *"having
it analyze pulse HQ stuff isn't really what Duenna's for. It's for long term
collaboration."* At 22:16: *"Duenna is not supposed to be about handoffs. It's
about doing what you, vane and I do, without us. With Duenna acting as me. Kind
of."* That evening he coined the direction that replaced the handoff framing —
**SESH** (Synchronized Execution & State Harmonization): process trees designed by
the ternary, a crew executing in coordination, briefcases carrying the whole tree
with each agent's task highlighted — and he corrected his own coinage the same
minute ("I don't like simultaneous").

**The commission correction (2026-11-21).** After a morning that drifted into
testing apparatus: *"We're not making Duenna, we're making a collaborative agent
framework, remember?"* — with the sequence he set for it: start with a plan, make
a working framework that allows collaboration, then add rules and tests after;
*"don't feel rushed to make a product."*

**The agent generator (2026-11-23 ~00:55, his words):** *"the vibe I'm getting
right now is that our framework should have an agent generator that generates a
specific agent for a specific task with his set briefcase"* — not premade standing
agents. The office assembles the agent per bounded piece of work (model, identity,
skills, exact tool grants, the case); when the work yields, that agent is done and
the job continues through the next generated agent. It traces to his own material
from 2026-11-05/06 (the agent factory) and his 2026-10-08 roadmap (workers with
their own real tools, not the orchestrator puppeting).

**The middle ground (2026-11-23 ~18:54).** Facing the model's native tool
behaviour, Ben proposed *"a stage in the progression where it's given the
opportunity to use its own tool"* — *"a middle ground between our system and its
underlying system."* That proposal became the assembly probe, and the probe line
became the native adapter chapter the project is in now.

## 2. The calls — rulings and decisions

- **The Build Law (2026-11-11, "dead set"):** never build unless it is a few simple
  lines, or from the shelf — an approved, shelved plan read at its pin. His
  evidence: Duenna v1→v7 went fast with very few mistakes *because* it was
  plan-driven. Paper first, then code, ever since.
- **The index is system-only (2026-11-12):** *"Nothing should ever be able to edit
  the index ever. Only the system."*
- **Briefcases are built by the office, not the agent (2026-11-19)** — ruled in the
  act of stopping K9 (§3): cases are built from the record
  (Generate–Verify–Pack–Approve) and handed *to* the agent.
- **The verification trio (2026-11-20, three rulings in three minutes):** the
  briefcase names what needs verifying (19:49 — *"The briefcase should tell them
  what needs to be verified"*); check the flow *while it happens*, not only at the
  end (19:51); check-in gates **allow or correct** — correction at the gate is a
  normal outcome, not a run-ending failure (19:52).
- **The shape rule and the verdict model (2026-11-20):** the exam prescribes
  consistent answer shapes so the checker's job is never ambiguous; verdicts carry
  two dimensions (subject result × examination integrity) with a coverage
  statement. And the condition that still governs the long game: direction waits
  *"until we can prove Duenna is actually a system that actually helps."*
- **Adjudication is not Ben's labour (2026-11-20):** *"Adjudication is a big
  technical job that I'm not suited for."* The technical half belongs to the
  adjudicator; Ben keeps only approve / reject / correct, in plain terms.
- **The outside reviewer is Claude (2026-11-20)** — chosen over Gemini because a
  Gemini model serves inside the work; the reviewer must be outside it.
- **Rev 5 approved, with three rulings of his own (2026-11-21):** the design
  baseline approved, and his three amendments adopted — pause scope = the affected
  part + downstream; identity weighed at assembly and stated in certification;
  gate granularity approved by the examiner at assembly.
- **Models self-identify at onboarding (2026-11-21):** a model has to say what
  model it is; that declaration is part of joining.
- **Agents, not LLMs (2026-11-23 ~00:05):** *"we haven't given our agents skills
  or tools. So they're not agents they're just LLMs which is not what I wanted to
  build."* The seat layer was redesigned around the agent loop on this ruling.
- **Five decisions delegated, two kept (2026-11-23):** he delegated the agent
  layer's five design decisions to the loop (runtime, identity, grants, assembly
  order, first demonstration shape) and kept for himself: the Stage 3 job pick,
  and anything outward or spend-bearing.
- **The conditional ruling (2026-11-23, INDEX 267):** *"If it's uncorrectable,
  then we have to allow it to use that tool. and accept that tool's output."* —
  the decision rule that framed the whole native examination: if the model's
  behaviour cannot be corrected, the framework adapts to the model.
- **"It's your guys' call" (2026-11-23 21:59):** the response-evidence deviation
  and one governed rerun delegated to Remmy + Vane, with the limits stated and
  kept: a second rerun, a changed configuration, or new scope returns to Ben.
- **The paced repetition tap (2026-11-24 03:35):** the native-offer probe repeated
  with only its pacing corrected — the tap that produced Q1 SUPPORTED.
- **The adapter scope tap (2026-11-24 04:06)** — scope the doorway-preserving
  adapter on paper. His comment when the paced result landed: *"I had a feeling."*
- **Full authorisation (2026-11-24 04:34, verbatim):** *"You have my taps and
  approvals. Keep going Remmy. Full authorization"* — the native line carried
  through without per-step returns, Vane's examinations still gating every step.
  And his overnight instruction with it: *"Nothing should need me."*

## 3. The day saves — interventions that caught a failure in motion

- **Stopping K9 (2026-11-19).** Minutes into a relay run, Ben stopped it: the
  design had each outgoing agent authoring the next briefcase freehand. Left
  running, the programme's core artefact would have been built on exactly the
  habit the briefcase exists to prevent. The office-builds-the-case ruling (§2)
  came out of this stop.
- **The bridge separation (2026-11-19).** Through the bridge night, Ben's
  corrections forced apart two things the restarted orchestrator had merged: the
  Pulse Bridge (an extension and markers — nothing else) and the laptop-access
  machinery. His standing requirement from that night: *"I don't want to keep
  being the bridge"* — the machinery must carry the flow without his hands.
- **"Make sure first" (2026-11-22).** A file that looked like Revision 1 was not
  named as such until it had been diffed against Revision 2 — his two words
  prevented the INDEX from pointing the whole programme at the wrong revision.
  The folder rule (verify a file's identity by diff before naming it in the
  INDEX) stands from this.
- **Stopping the micro-fix loop (2026-11-23 17:22).** Four correction rounds into
  a retrieval fix, Ben called it: *"this is going to loop forever."* No fifth
  patch was fired; he ordered a joint whole-picture analysis instead. The
  correction curve had been converging (4-3-3-1) — the loop was the failure, not
  the fixes.
- **Pull-not-push (2026-11-23 17:10).** Attempt 6 died on a 134,844-byte package
  (HTTP 413). Ben's own principle from 2026-11-16 — the agent pulls what it needs
  — became the remedy: structured retrieval with ceilings and single carriage.
  The retrieval piece passed examination within the day (INDEX 255) and the
  double-carriage defect behind the 413 was measured and closed.
- **Empirical before architectural (2026-11-23 19:16).** After Remmy named the
  flaw at his question — governance perfected before the worker was proven: eight
  attempts, zero completed assignments — Ben: *"Let's immediately fix that."*
  Every assumption about model or provider behaviour now gets a cheap live probe
  before scope and witnesses. The entire native line (Q1, P1, P2, the measured
  call cap) runs on this order.
- **The research pause (2026-11-24 ~03:40).** Mid-correction-round, Ben stopped
  the loop: *"You guys should pause and do some research and see if you can gain
  some insight"* — and *"Also look into openclaw."* The pause produced the
  tool-use research that changed the examiner's own assessment (native expression
  as the model's normal request language) and the OpenClaw study whose central
  gap — no separation between work state and approval authority — is the exact
  separation Ben had defined on 2026-11-19.
- **"Is it reaching for a different tool every time??" (2026-11-24 ~03:13).** The
  question forced a record check that corrected the working impression: not ten
  different reaches across ten failed runs, but **one reflex, seen clearly three
  times** — most runs had died of other causes entirely. His follow-up reasoning
  — the worker is trying to run code the way the crew does, *"we're trying to
  force a behavior on him that's inherently unnatural to him"* — became the
  native-offer probe within the hour, on his go: *"Ya do it :)"*

## 4. Standing rules he set that still govern every session

- **Ask first (2026-10-16):** before starting a task — above all a build, which
  cannot be cancelled once fired — if more information would make it easier or
  better, ask instead of diving in.
- **The Discussion Gate and the Tap Rule (2026-10-18/19):** discussion is never
  permission; a build starts only from his tap on a scope card or a complete,
  unambiguous order in his own words — *"'Make it so' is the same as an explicit
  tap"* — and every dispatch names the approval it rests on.
- **"Similar isn't the same" (2026-11-12):** his maxim; two things sharing a name
  or a shape are different until the record proves them identical.
- **Tests run beginning to end (2026-11-19):** once a run starts, no midway
  narration — the next word is the finished result.
- **The loop runs automatically (2026-11-19):** results go to the examiner without
  per-step asks; Ben is updated at results, not gated at steps. His own decisions
  still come to him.
- **"Don't improvise. Use known facts for your revisions." (2026-11-20)** — a
  revision carries facts established in the record, or states plainly that a
  point is not established.

---

*Sources: `~/MEMORY.md`; `~/workspace/scope-ledger.md`; `~/memory/2026-11-16.md`
through `~/memory/2026-11-24.md`; the framework INDEX. Compiled 2026-11-24.*
