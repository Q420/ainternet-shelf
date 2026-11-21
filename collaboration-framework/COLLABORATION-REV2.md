# COLLABORATION — the design of the collaboration itself (Revision 2)

**Stage 1, document 1 of 2 (the SPEC SHEET is document 2). Written by Remmy under the approved plan (COLLABORATION-PLAN-2026-11-21-REV3, Ben's go 2026-11-21 11:26 MST). Revision 2 applies Vane's five clarifications from her examination of Revision 1 (VANE-COLLABORATION-EXAMINATION-2026-11-21): the record distinguishes claims from established facts; the examiner's independence is stated operationally; gates are an interrupting mechanism, not a phase; correction authority is separated by kind; open disagreement and certification are explicitly related. Revision 1 stands preserved beside this one. For Ben's ruling after the SPEC SHEET. Nothing is built from this document until Ben rules on the design.**

This document designs how the collaboration works. The SPEC SHEET restates the same design tightly enough to build from. Where the two ever disagree, this document governs the intent and the SPEC SHEET governs the construction, and the disagreement itself is a defect to surface, never to smooth over.

## 1. What this framework is

A crew of live agents doing real work together — not a pipeline, not a chat room, not a string of handoffs. The ternary it is modelled on: a director who decides (Ben's seat), an orchestrator who assembles and conducts (Remmy's seat), an examiner who checks the work against evidence (Vane's seat), and crew agents who do the work. The framework's first form keeps the three seats held by their current holders; the crew seats are where new agents sit.

The settled distinction governs everything below: **collaboration is agents interacting through shared work — contributions changing the work and influencing one another — with the record making that interaction durable and recoverable.** Every mechanism in this design exists to serve that sentence. A mechanism that only moves messages, or only stores state, is not collaboration machinery and does not belong here.

## 2. The shared working environment — the bubble over the record

Two layers, never merged:

- **The record** is the state of the work: the job, its parts, every contribution, every decision, every disagreement, every gate outcome, in order, append-only, checkable. The record is authoritative for the **history and the recorded state** of the work — what was contributed, by whom, when; what was decided; what was verified. It is not an oracle: a contribution's presence in the record establishes its **provenance, not the truth of its contents**. Claims, evidence, decisions, and verified findings carry distinguishable statuses in the record, and examination is what moves a claim toward a verified finding. An event that is not recorded cannot be relied on as an established framework event.
- **The bubble** is the shared working surface the crew actually works in: the living view of the record where contributions appear as they land, where an agent reads what the others have done, adds its own work, responds to theirs, and raises disagreements. The bubble is a view over the record, rendered from it, writable only through recorded acts. Conversation happens in the bubble, attached to the work it is about — a comment hangs on the contribution it answers, not in a free-floating stream.

An agent never works from a private copy of the job. It works in the bubble, on the record. That is what makes one agent's contribution able to change another's work: they are quite literally working on the same thing, in the same place, at the same time.

## 3. The crew and their seats

- **Crew agents** do the job's work. Each sits in a seat with a verified identity (§6, onboarding). A crew agent can: read the bubble; make contributions; answer, extend, or challenge another's contribution; raise a disagreement; request work or offer it (§8, delegation points); declare its own piece complete — a claim the gates then judge, never a fact it can mint itself.
- **The orchestrator** assembles the crew for a job, issues briefcases (§5), watches the flow, and conducts: nudging a stalled joint, routing a disagreement to its gate, closing a run. The orchestrator does not do the crew's work and does not grade it.
- **The examiner** is independent of the crew and of the orchestrator's conduct. The examiner holds the judgement gate (§7), checks claims against the record, and certifies — or refuses to certify — completed work. The examiner's independence is structural, and it is specific: the examiner works from the **commissioned job terms and direct access to the same record and evidence** the crew works from — never from a crew-authored account of what happened or what the work means. The examiner does not contribute to the work and cannot be overruled by the orchestrator. Only the director can overrule the examiner, and an overrule is recorded — and an overrule changes the **disposition or the authorised direction**; it does not retroactively make an unsupported finding supported. The examiner's finding and the director's ruling remain separately visible, always.
- **The director** (Ben) commissions jobs, rules on the design and on escalations, and holds every authority the framework does not explicitly delegate. The director's seat is occupied from the first run; designing it as an empty chair that software fills by itself is out of scope for this design.

## 4. How a run goes

1. **Commission.** The director names a job: what done looks like, in his terms. The job enters the record.
2. **Assembly.** The orchestrator proposes a crew (which seats, which models, why each fits), the design of the job as a **process tree** — the whole job drawn as parts, with the joints between them named — and the gates the run will carry. The examiner checks the assembly before any agent is woken: is the tree whole, are the joints gated, does every briefcase-to-be name what needs verifying.
3. **Briefing.** The office (§5) builds each agent's briefcase from the record: the whole process tree with that agent's part highlighted, the job's terms, what it must verify, the authority it holds (§8). No agent authors another's case.
4. **Work.** The crew works in the bubble. Contributions land in the record as they are made. Any agent may build on, correct, or challenge any contribution — that interaction is the collaboration, and the record is its evidence. The orchestrator conducts; the examiner watches the flow while it happens, not after it ends.
5. **Gates — an interrupting mechanism, not a phase.** Gates do not wait for the work to finish. Whenever the work reaches a joint the process tree named, the work **pauses** at that joint's gate: the examiner allows it through, corrects it on the spot, or escalates it (§7) — and only then does work proceed. This repeats at every joint as the run advances, and a final gate stands at completion.
6. **Completion.** An agent declares its piece complete; the crew's claims are checked by the examiner against the record; the examiner certifies the job, certifies it in part, or refuses. **Certification states what it covers.** It never implies that an unresolved disagreement has been settled: where an open disagreement bears on whether the job's acceptance criteria are met, the certification says so explicitly, so the director sees exactly what is certified, what remains disputed, and what has not been established (§9).
7. **Close.** The run closes with its record complete: the deliverable, and the full account of its making, go to the director together. The record stays readable afterwards; a later run can pull from it.

## 5. Briefcases and the office

A briefcase is a **contract**, not a briefing note. It carries: the assignment; the whole process tree with the agent's part highlighted; the boundary of the evidence it may rely on; **what it must verify** (named in the case, not left to the agent's judgement); the account it works under; and the authority it holds — which never includes the authority to approve its own work or to widen its own assignment.

Briefcases are **built by the office, not by the agent**: generated from the record, verified against it, packed, and approved by the orchestrator before issue (Generate–Verify–Pack–Approve). An agent that finds its case wrong says so in the bubble; the office corrects the case on the record — a run-level correction under §7's separation of correction authority. Cases are versioned; an agent never works from a case whose version it cannot name.

## 6. Onboarding

An agent joins a seat through onboarding, once per seat, recorded:

- **Identity.** The model must state what it is — its own declaration, captured verbatim and labelled as its self-report — cross-checked against whatever provider-side identity exists. A candidate that cannot or will not identify itself does not sit. (Ben's principle, 2026-11-21.)
- **Capability and limits.** What it can do, what it cannot, stated plainly and recorded — the crew is assembled from known material, not hoped-for material.
- **The terms.** The agent receives the framework's rules of interaction (this document's design, in the form the SPEC SHEET fixes) and acknowledges them on the record.
- **Readiness is not authority.** Completing onboarding makes an agent *ready* to be assigned. It grants no authority by itself; authority arrives only inside a briefcase, for a job, from the orchestrator under the director's commission.

## 7. Gates with live holders

A gate is a named point in a run where work may not pass unjudged. Every gate has a **live holder** — a seat occupied during the run, never a script and never a post-hoc review:

- **The judgement gate** (holder: the examiner) sits at the joints the process tree names, and at completion. Its outcomes are exactly three: **allow**, **correct** (the defect is identified at the gate and the work is fixed before it proceeds), or **escalate** (to the director). There is no silent pass: a gate that does not record an outcome has not been held.
- **The assembly gate** (holder: the examiner, before the run) judges the crew, the tree, and the cases — the run does not start unjudged either.

**Corrections and their authority.** "Correct" names three different acts, and they do not carry the same authority:

- **Correcting the work** — a contribution or product is defective. The examiner identifies the defect and requires the correction; the crew agent responsible performs it, in the bubble, on the record.
- **Correcting a case or run instruction** — a briefcase or a run's working instruction is wrong. The office corrects it (§5), on the record, as a new version; agents never silently work around a wrong case.
- **Correcting a governing document** — the design, the spec, or this plan is wrong. A gate **cannot** do this. A gate may *propose* it, recorded as a proposal; the change itself follows the framework's change authority — the director rules on changes to governing documents, and only then is the shelf updated. A live gate is never a route around the director's authority over the design.

Identifying a defect and requiring its correction is the examiner's authority at a gate. Performing the correction belongs to the seat responsible for the thing corrected.

## 8. Delegation points — named, values reserved

The design requires delegation boundaries at exactly these points. The design names them; **their values are Ben's to set**, and until he sets one, the conservative default in brackets holds:

- **Assign** — who may give a crew agent a task beyond its briefcase. [Default: the orchestrator only, inside the commissioned job.]
- **Request** — whether a crew agent may ask another agent for work, and whether the asked agent may accept on its own. [Default: requests are visible in the bubble; acceptance needs the orchestrator's recorded note.]
- **Sub-delegate** — whether an agent may pass part of its part to another agent. [Default: no.]
- **Spend / act outward** — whether any agent may act outside the framework (send, publish, purchase, contact). [Default: no; outward acts are the director's, or explicitly commissioned.]
- **Certify** — who may certify completed work. [Not delegable: the examiner alone, under §3.]

## 9. Disagreement

Disagreement is a working state, not an error. Any agent may raise one against any contribution, decision, or gate outcome; it stands in the record with its grounds. A disagreement is settled by evidence at its gate, by the examiner's judgement, or by the director's ruling — or it **remains open, shown as open**, including at close. Nothing in the framework converts disagreement into a consensus-looking status, averages it away, or hides it from the director's view of the run.

Its relationship to certification is explicit (§4, step 6): an open disagreement never blocks the record from showing what *is* established, and certification never launders it into agreement. The certification states its coverage; the disagreement states its grounds; the director reads both. The history of this programme is the evidence for this section: the catches that mattered were disagreements that stayed visible.

## 10. The observer

A read-only window onto a run, for the director: the record rendered as it grows — contributions, gates, disagreements, certifications — in plain words first, detail underneath. The observer shows only what the record holds; it invents nothing, ranks nobody, and holds no controls that touch the work. It is a window, not a seat: it is not the examiner, not a gate, and not an authority.

## 11. The substrate decision

The accepted prototype (the Loom vertical slice, Stages 1–4, integrated evidence gate passed 2026-11-21) already provides much of the **record half**: an append-only, hash-chained event history; a harness mediating agent access; an independent checker implemented separately from the service; a read-only observer. It was proven mechanically, with scripted drivers in the agent seats.

**Decision: the build reuses that record half as the substrate, and replaces the drivers with live seats.** The bubble is built as the working surface over its event history; the harness becomes the seats' doorway; the checker becomes part of the examiner's instrumentation (the examiner's judgement remains a seat's, not the checker's — the checker verifies structure and provenance, the examiner judges the work). What the prototype does not provide — live agents, the bubble as a working surface, the office, onboarding, live gates — is the new build. The alternative (a wholly fresh build) was weighed and set aside: the record half is the part already proven against examination, and rebuilding it would spend the project's effort re-proving what is proven instead of building what is missing. If the design's examination finds the substrate cannot carry the bubble honestly, this decision reopens — as a recorded correction, not a quiet drift.

## 12. What this design refuses

- No speaking scripts: no mechanism decides who talks when. Structure lives in the record and at the joints.
- No conversation-as-state: talk that is not a recorded act on the work does not exist for the framework's purposes.
- No record-as-oracle: the record proves provenance and preserves claims with their statuses; it does not make a claim true by holding it.
- No self-certification: the crew checks its own work; it never solely certifies it.
- No authority by participation: joining, reading, or contributing grants nothing beyond the act itself.
- No silent anything: no silent passes at gates, no silent corrections, no silent additions to a run's scope. If it is not in the record, the framework cannot rely on it as having happened; if it happened, it is in the record.
