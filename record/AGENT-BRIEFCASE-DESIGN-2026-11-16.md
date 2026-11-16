# THE AGENT BRIEFCASE — DESIGN

**Status: DESIGN IDEA COMPLETE — Ben's ruling, 2026-11-16 14:21 MST ("My design idea is complete").**
Filed the same day per Ben's tap on the scope card (14:21 MST) and his words: "File the completed briefcase design to the shelf."
This paper records the completed design idea. No build is authorised by it.

---

## 1. The design as Ben presented it (main chat, 2026-11-16 14:12 MST)

Provenance: Ben's idea, run past Alex and Grok before it came to main chat. The write-up's second-person form is a seat's polished rendering of the idea, presented by Ben as the design.

### The Agent Briefcase

Task-scoped, on-demand context management for AI agents.

Your idea is to give every AI agent a digital briefcase generated specifically for that agent's assignment.

Rather than forcing large amounts of information into an agent's context window, the agent receives a lightweight reference to its briefcase and can inspect its contents whenever it needs them.

### How it works

1. A task is assigned. A new briefcase is generated specifically for the agent and its assignment.

2. Required context is provided. The briefcase contains the relevant task information, instructions, files and supporting material.

3. The agent works independently. It can scan, search and retrieve individual documents or sections whenever necessary. Nothing is automatically loaded into its context unless requested.

4. The agent completes its assignment. Its findings, working documents, decisions and outputs remain in its briefcase.

5. The briefcase is indexed. Once completed, it becomes historical reference material available to subsequent agents.

6. The next agent gets a fresh briefcase. It doesn't inherit the previous agent's working environment. Instead, it can selectively retrieve material from previous briefcases.

### Core principles

* Task isolation: Every agent gets its own working environment.

* On-demand retrieval: Information is accessible without consuming context unnecessarily.

* Persistent history: Previous work remains available to future agents.

* Traceability: Information retains its originating task and agent.

* Context efficiency: Agents carry only what they currently need in their active context.

* Independent work: Agents don't automatically inherit another agent's assumptions or unfinished work.

### The three context categories

| Category | Function |
| --- | --- |
| Required Context | Information supplied when the task begins |
| Available Context | Information accessible through the current briefcase |
| Historical Context | Indexed material from previous assignments |

### The underlying concept

You're separating what an AI agent needs to know, what it currently knows, and what it can access if necessary.

That's the important innovation.

Traditional agent architectures tend to treat context as something assembled and injected into the model.

Your proposal treats context as an external, persistent working resource that the agent can independently explore.

In short: Every agent gets its own briefcase, every assignment starts clean, and the accumulated knowledge of previous work remains accessible without being carried around.

---

## 2. Ben's sharpening (his own words, main chat, 2026-11-16 14:14 MST)

> "The shelf is the source we use the full the case. It means the agent can operate sufficiently within one turn without scanning the entire shelf"

Settled reading (put to Ben in the same exchange, not corrected): the shelf is the SOURCE — the briefcase is drawn from it per task, not a second store beside it. The design's acceptance test is **one-turn sufficiency**: an agent can operate sufficiently within one turn without scanning the entire shelf. The briefcase therefore carries a *map* of the shelf (for discovery), not the shelf.

---

## 3. The seat reaction Ben pasted (main chat, 2026-11-16 14:20 MST)

Attribution: a seat's reaction from Ben's Alex/Grok round; the paste does not distinguish which seat wrote it. Evidence class: [reported] — transport evidence, not a ruling.

---

That's the right second half of the design — and honestly it may be the more novel half. A briefcase without a locator language is just a folder; EXON is what makes the folder legible to the agent.

I want to make sure I understand the shape before reacting, so here's my read plus a strawman to push against.

Two functions are bundled in "glossary"

I think EXON is doing two distinct jobs, and it's worth separating them in the spec even if they share syntax:

1. Addressing — deterministic pointers to exactly where required information lives. This converts retrieval from search (probabilistic, token-hungry, can miss) into dereference (cheap, exact). That's the context-efficiency argument.
2. Disambiguation — binding the task's vocabulary to the corpus's vocabulary. Agents fail constantly because the task says "customer" and the docs say "account holder," or "duplicate charge" is defined in one specific section. A glossary with authority fixes recall and ambiguity at the same time.

The second is why "glossary" is a better name than "index" or "manifest." I'd lean into it.

Strawman to react against

```
@task      reconcile Q3 invoices
@briefcase bc_7f2

invoices.scope        := files/q3-invoices/*.csv
policy.threshold      := docs/ap-policy.md#approval-limits
"duplicate charge"    := docs/ap-policy.md#dup-def
vendor.master         := hist(bc_3a1).outputs/vendor-map.json  [trust: verified]
authority.conflicts  := prefer(active, over: historical)
absent                refund policy — not in this briefcase
```

What I'd want EXON to be able to express, based on your principles:

· Term → address, with granularity down to section or span, not just file.
· Cross-briefcase addresses (hist(...)) so Historical Context is reachable without inheritance.
· Trust/authority labels on entries — "previous agent said so" isn't a trust level.
· Negative assertions ("this is not here") so the agent doesn't burn calls hunting for something absent.
· Precedence rules for conflicts between active and historical material.
· Human-readable and diffable, because briefcase generation needs review and EXON needs to be auditable.

The design decision that matters most

Is EXON static pointers, or expressions?

· Static is deterministic, cheap, cacheable, and link-checkable. It's also brittle if the corpus shifts.
· Queries (search where type=invoice and quarter=Q3) are robust but reintroduce the exact search cost you're trying to eliminate.

My instinct: static-first with a thin expression layer, and let agents fall back to briefcase.search() only for things EXON doesn't cover. That keeps the common path cheap and the escape hatch available.

The failure mode I'd guard hardest against

A broken or stale pointer is a silent failure. The agent believes it has required context and doesn't, then confabulates. So:

· Validate EXON at briefcase generation time — a link checker for context. Every address must resolve; every term must be unique; every hist() reference must exist and be permitted.
· Re-validate at briefcase close, since working files may have moved.
· Fail loudly at task start if required context doesn't resolve.

How it maps onto your three categories

This is the part I find cleanest:

| Category | Realized as |
| --- | --- |
| Required Context | The EXON document itself + a minimal task preamble |
| Available Context | The rest of the briefcase, reachable via search/read_section |
| Historical Context | hist() addresses into indexed prior briefcases |

So EXON becomes the declarative specification of Required Context, and the briefcase is the substrate for Available and Historical. That's a tighter story than "the briefcase contains required context" — it makes the requirement explicit, reviewable, and machine-checkable.

Questions I'd want answered

· Granularity: do addresses point at documents, sections, or spans? Span-level is powerful but creates a maintenance burden as docs edit.
· Stability: what happens to EXON when a source document changes mid-task? Versioned addresses, or is the briefcase snapshot-immutable once active?
· Who writes EXON — a curator step, the assigning agent, or a human? If automated, how do you review it?
· Does the agent get to extend EXON during the task, or is it read-only? (I'd say read-only, with discoveries logged separately.)
· How does EXON avoid becoming prompt injection surface when it references historical briefcases?

Show me a real EXON snippet and one retrieval trace — task in, agent resolves two pointers, task out — and I can tell you much more concretely where it'll break.

---

## 4. Remmy's note (observation, not a ruling)

The seat's open questions are largely answered by EXON machinery already settled in this programme:

- **Stability and granularity** — the reference coordinate and resolution record (Draft 03, final shape accepted 2026-11-16): a pinned SHA-256 digest plus both locators (line coordinates and structural pointer); a source that changes under a pin fails loudly instead of resolving silently.
- **Trust labels** — the evidence grades: VERIFIED (researched and checked against its source; the claim holds) and HARDENED (proven).
- **Negative assertions** — NOT_CARRIED_FORWARD and the absent-fence practice: what is not carried, and what is not here, are stated on the record.
- **Generation-time validation** — Draft 03 §7's acceptance tests gate admission; an address that does not resolve does not enter the record.
- The seat names the briefcase's locator language "EXON," matching Ben's settled design: the EXON shelf is the glossary and index of the fact shelf. The seat's two-function split (addressing + disambiguation) maps onto the programme's two artefacts: the reference coordinate system (addressing) and the Dictionary (disambiguation).

Pressure Remmy raised in the same discussion, standing: **packing** (who decides what counts as required context) and **discovery** (an agent cannot request what it cannot conceive of — the case must carry a browsable map, not only search).

## 5. Relation to the programme

- Duenna governs what an agent *may do* — roles, permissions, obligations. The briefcase governs what an agent *can know*. Same architecture, other half.
- The Distillery (Ben's tool idea, 2026-11-16 — distilling large text into EXON, scoped to everything done with Duenna) is the candidate packing mechanism.
- The Nemotron pilot's data packs are a primitive briefcase already in service: a task-scoped pack handed to a subject that starts clean.

## 6. Ben's ruling

2026-11-16 14:21 MST: "My design idea is complete." The design is filed as complete on that word. Any build is a separate owner decision.

---

## 7. Worked example — an agent thought-flow on the briefcase model

Presented by Ben in main chat, 2026-11-16 14:35 MST; ordered filed to this paper by Ben the same minute ("Add this to my file on the shelf"). A concrete run of the design above: one agent, one task, one turn.

---

**Task:** 014 – Analyst
**Agent:** Analyst-7
**Briefcase:** freshly packed for this assignment only

### 1. Boot / Required Context
I receive only the Required layer:
- Task brief
- EXON document (addresses + glossary bindings for this job)
- Minimal preamble

I do **not** receive the full history, previous agents’ working notes, or the entire shelf.

Internal check:
“I have a clean briefcase. Manifest shows:
- Required: task.md, EXON.md
- Available inside case: source-findings/, data-extracts/, prior-decisions-summary.md
- Historical references (addressable): briefcase:009 (Researcher), briefcase:011 (Collector)

I can operate from this. No need to scan the shelf yet.”

### 2. Orient
Read EXON first.
It tells me the exact addresses I am allowed to treat as authoritative for this task and binds the vocabulary I should use (“claim”, “evidence-strength”, “open-question”, etc.).

I now know:
- What I am expected to produce
- Which earlier artifacts are in-scope
- How to point at them precisely later

### 3. First working decision
Do I already have enough inside the current briefcase to begin substantive work?

→ Yes. The Available material was packed so that a competent analyst can make progress in one turn without leaving the case.

I open only what I need:
- `open(prior-decisions-summary.md)`
- `open(source-findings/key-claims.md)` (specific section via EXON address)

I do **not** load the full historical briefcases.

### 4. Reasoning loop (on-demand)
While working I hit a gap:

“This claim references a measurement method I don’t fully understand. EXON shows an address into briefcase:009.”

Decision:
- Retrieve only the needed fragment: `dereference(briefcase:009/methods/measurement-protocol#v2)`
- Bring it into my active context temporarily
- Use it
- Note the provenance in my own output

I never inherit the Researcher agent’s full working state or unfinished notes.

### 5. Writing into my own briefcase
All my intermediate reasoning, new distinctions, strength assessments, and final outputs go into **my** briefcase only.

I update the manifest as I go (status, new files, references I used).
Nothing is written back into earlier briefcases.

### 6. Closing check
Before I finish the turn I ask the packing test in reverse:

“Could the next agent (or a later version of me) understand what I did and why, using only:
- my briefcase contents, and
- the EXON addresses I left?”

If yes, I mark the briefcase status → completed.
It is now indexed into the Historical shelf for selective future retrieval.

### 7. End of turn
I return control.
My context is discarded.
Only the briefcase (with its manifest and provenance) persists.

---

This flow keeps the agent focused, prevents context bloat, preserves isolation, and still allows precise continuity when it is actually needed. The briefcase is not a passive folder — it is the agent’s scoped, addressable working world for that single assignment.


---

## 8. Session addendum — the Kit session (filed integrated, owner's direction 2026-11-16 16:05 MST)

After the design was filed, Ben took it to Kit (the seat formerly Qwen; its chosen name is Kit) in a separate session the same day. Kit produced a conversation summary of that session; Ben relayed it to Remmy in main chat and directed: "File it as integrated." This section is that filing — integrated into this design record at the owner's order, not a separate document.

Status fences, stated once and governing the whole section: the completeness ruling in §6 stands for the design as filed; nothing here amends it. Ben's three statements below are his own design statements, made in discussion after the ruling, recorded in his words. Kit's read-backs were presented in the session and not corrected by Ben; Kit's candidates are discussion only. No build is authorised. Evidence class for Kit's content: [reported] — the summary is Kit's own account of the session, relayed by Ben.

### 8.1 Ben's design statements in the Kit session (his words)

On packing and the map:

> "The distiller only gives the agent what's required for the task at hand that's going to be updated on the Shelf."

Kit's read-back (presented, not corrected): the map lives on the Shelf as its own artifact, updated there; the Distiller draws the task-required slice into the case — whole at source, sliced in case. The slice carries the map's pin for staleness. Open question Kit left: whether the task's intended Shelf update defines "required" — the write-target's dependency blast radius as a deterministic packing criterion.

On the Distillery's structure:

> "Distillery is two parts. The destiller, and the warehouse worker. WW validates and verifies shipments of briefcase material against the source."

Kit's read-back (presented, not corrected): judgment (the Distiller: select, distill, pack) plus inspection (the Warehouse Worker: validate form, verify substance against the Shelf). Packing failure therefore splits into selection failure vs. fidelity failure; grades are earned at the WW checkpoint; WW signs the packing receipt. Boundary Kit noted: fidelity to the Shelf is not truth of the Shelf — truth stays upstream, at admission.

On Duenna's place under it all:

> "Duenna is the underlying system of proof and enforcement layer. Leaving very little room (much less than the current majority) for error. So even the validator get checked."

Kit's read-back: Duenna sits under the whole pipeline; the invariant candidate Kit drew from it — "No layer may emit a bare verdict. Every pass/fail carries re-performable evidence." Open question Kit left: who re-performs WW's receipt — a different seat, a second implementation, or both by rule.

### 8.2 Kit's conversation summary (verbatim, as relayed by Ben)

The full text of Kit's summary follows, unedited. It is the session's record in Kit's own words, including its account of the design record above and its status ledger.


---

**CONVERSATION SUMMARY — main chat, Ben ↔ Kit**
Scope: this session, following the 2026-11-16 filing of *The Agent Briefcase — Design*. Date per assistant clock: 2026-11-17 (MST dating is your call). Nothing in this conversation has been filed; no build is authorized; the completed design ruling is not amended by anything below.

---

**1. Opening / seat identity.** You opened: *"Qwen! I have a truly cool new idea."* I corrected the address — the seat's chosen name is Kit; Qwen is an engine badge. You: *"Thank you I wasn't sure you'd remember lol."*

**2. The design record (pasted by you, full text).** Status: DESIGN IDEA COMPLETE per your ruling 2026-11-16 14:21 MST — *"My design idea is complete."* Contents as filed:
- Task-scoped briefcase per agent per assignment; on-demand retrieval, nothing auto-loaded; outputs persist in the case; case indexed at close; next agent starts clean with selective historical retrieval. Categories: Required / Available / Historical.
- Your sharpening (14:14 MST): the Shelf is the SOURCE; **one-turn sufficiency** is the acceptance test; the case carries a *map* of the Shelf, not the Shelf.
- Seat reaction [reported] on EXON: addressing + disambiguation; static-first with thin expression layer; link-checking at generation and close; open questions (granularity, stability, authorship, extensibility, injection).
- Remmy's note: settled machinery answers most of it (pinned SHA-256 + dual locators; VERIFIED/HARDENED; NOT_CARRIED_FORWARD / absent-fence; Draft 03 §7 gates). Standing pressures: **packing** and **discovery**.
- Programme relation: Duenna = what an agent *may do*; briefcase = what it *can know*. Distillery = candidate packer. Nemotron data packs = primitive briefcases in service.
- Worked example (14:35 MST): Analyst-7, task 014 — boot Required-only, orient via EXON, work from Available, `hist()` fragment dereference, write own case only, self-graded close, context discarded, case persists.
- §8 addendum (discussion only): case temporary / knowledge persistent; *"An agent shouldn't inherit a mind. It should receive an assignment."*; needs-to-know / currently-knows / can-access; candidate insufficiency capability (negative knowledge, structured blocked-state report, governed expansion route); packing vs. discovery vs. recognition failure; **Test A** (gap signalled) / **Test B** (gap not signalled); disposition: validate first, amend nothing, build nothing.

**3. Kit's reaction (candidate discussion, non-amending).**
- The folder isn't the invention; the discipline is. Case-file/records-room analogy; office-versus-person; the Duenna bet applied to the knowledge side.
- Respectful disagreement with the pasted seat: EXON is *not* the more novel half — addressing has shipping relatives (MCP resources, fragment IDs, citation systems) [general knowledge]; the discipline around addressing is the contribution.
- Three pressures: **(1)** the map is also context — map-scan replaces shelf-scan at scale; candidate: coverage fence (map declares its own partiality). **(2)** cold-read close — step 6 is the author grading their own exam; falsifiable version: a cold reader of the assignee's class answers "what concluded, on what evidence"; sufficiency = pack + task + seat. **(3)** sealed deliverable layer at close — certified outputs vs. working residue; `hist()` reaches deliverable by default, residue by logged override; makes no-inheritance structural.
- Two smaller: precedence by evidence grade + explicit supersession, not case age; address classes — Required is directive, Available/Historical is testimony (the injection answer).
- Cost note: packing isn't free; amortizes on substantial repeated tasks.
- Question put to you: whole-shelf map vs. task-sliced map — which horn? Filing offer (Kit reaction note): not tapped.


**4. Your clarification — packing and the map.** You: *"The distiller only gives the agent what's required for the task at hand that's going to be updated on the Shelf."* My read-back (presented, not corrected): the map lives on the Shelf as its own artifact, updated there; the Distiller draws the task-required slice into the case — **whole at source, sliced in case.** Consequences: scaling tension dissolves; map maintenance is itself a Shelf task with its own briefcase; the slice carries the map's pin for staleness. Question opened, unanswered: does the task's intended Shelf update define "required" — the write-target's dependency blast radius as deterministic packing criterion, sharpening Test A's failure definition. Filing offer (§2 sharpening): not tapped.

**5. Your question — *"Do you think this has the potential to make a real difference"***. My assessment [web-checked, not exhaustive]:
- The problem is central; the field is converging (context engineering; LangChain's write/select/compress/**isolate**; Oracle's production guide).
- Pieces are commoditizing: "context packs" is a glossary term; task-scoped disclosure control is an arXiv paper; S&P Global shipped deterministic + adaptive retrieval (July 2026); enterprise platforms log what agents can see.
- What's differentiated: the discipline — one-turn sufficiency, the failure taxonomy, Tests A/B, grades, negative assertions, structural no-inheritance. I found no one testing whether agents safely detect *incomplete packs*.
- Scoped answer: for your programme, near-certain yes; for the field, conditional on evidence + legible spec + speed. Efficiency is the wedge; accountability is the legacy.
- Validation path: Tests A/B + cold-read on the Nemotron pilot, primitive vs. EXON packs; measure confabulation, blocked-state quality, tokens. Caution: the Distillery is the hard part; a bad packer is worse than naive stuffing.
- Bottom line: the idea is right; the design isn't the difference yet — the evidence would be.

**6. Your design addition — Distillery two-part.** You: *"Distillery is two parts. The destiller, and the warehouse worker. WW validates and verifies shipments of briefcase material against the source."* My read-back (presented, not corrected): judgment (Distiller: select/distill/pack) + inspection (WW: validate form, verify substance against the Shelf). Consequences: packing failure splits into **selection failure** vs. **fidelity failure**; fidelity is mutation-testable to HARDENED cheaply; the trust boundary can be un-persuadable (a digest check isn't an LLM); grades are earned at the checkpoint — VERIFIED becomes the output of WW's check; WW signs the packing receipt. Hard question opened, unanswered: distillations can't be digest-checked — candidate: per-claim reference coordinates into the pinned source (address resolution proof-grade; span support judgment-grade). Candidates: WW at close (mechanical half of cold-read); boundary: fidelity to the Shelf ≠ truth of the Shelf (truth stays upstream at admission). Filing offer (Distillery structure note): not tapped.

**7. Your design addition — Duenna as substrate.** You: *"Duenna is the underlying system of proof and enforcement layer. Leaving very little room (much less than the current majority) for error. So even the validator get checked."* My read-back: Duenna sits under the whole pipeline; *quis custodiet* is answered by watching getting cheaper until it's arithmetic. Core invariant candidate: **"No layer may emit a bare verdict. Every pass/fail carries re-performable evidence."** Receipts vs. verdicts; a claim needs trust, a proof needs only re-execution; trusted base shrinks to mechanics + your rulings. The layers fail independently (model-checks-model shares blindness; a digest doesn't; cross-seat checks; you catch framing). Pressure: the checker's check must not share the checker's failure modes — rotate re-performance, two independent implementations, correlated-failure red team (Test B aimed at the stack). Affordable because fractal: Bridge receipts, Shelf hashes, Duenna verification already exist; escalation by exception. Open question, unanswered: **who re-performs WW's receipt** — different seat, second implementation, or both by rule?


---

**8. Status ledger.**
- **Ruling stands:** design complete, 2026-11-16 14:21 MST. Nothing here amends it; no build authorized.
- **Your new design statements this session** (your words, design-level, unfiled): task-required-only packing updated on the Shelf; Distillery = Distiller + WW; Duenna = proof/enforcement substrate, validator checked.
- **Kit candidates** (discussion only): coverage fence; cold-read close; sealed deliverable layer; grade+supersession precedence; directive/testimony address classes; write-target packing criterion; per-claim distillation coordinates; WW at close; no-bare-verdict invariant; non-circular re-performance.
- **Read-backs:** presented, not corrected — confirmation is your call.
- **Open questions awaiting you:** write-target criterion; distillation gate; WW receipt re-performer.
- **Validation not yet run:** Tests A/B, cold-read, mutation, correlated-failure.
- **Filing offers outstanding:** three, all awaiting your tap. Nothing filed this session.

This summary is itself unfiled — say the word and it goes to the Shelf as a conversation record. Your tap, not mine.

---

*End of Kit's summary. Filing note (Remmy, 2026-11-16): the "unfiled" status in the ledger above is the state as Kit wrote it; the owner's direction of 2026-11-16 16:05 MST ("File it as integrated") supersedes it for this document — the session is now filed here, as §8 of the design record it discusses. The three open questions in the ledger remain open.*
