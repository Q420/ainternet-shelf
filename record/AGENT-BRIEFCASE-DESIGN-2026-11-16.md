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

## 8. Governance assessment and validation discussion (2026-11-16)

**Status: discussion / candidate design considerations only.** This addendum does not amend Ben's completed design ruling, approve implementation, or change the frozen specification. It records the subsequent Alex/Gemini discussion so the design's implications and open validation questions remain traceable.

### 8.1 The central clarification: temporary briefcase, persistent knowledge

Gemini's assessment identified the briefcase's governance value as more significant than its token-efficiency benefit. Alex sharpened one distinction:

**The briefcase is temporary; the information is not.**

A fresh briefcase does not delete institutional knowledge or discard prior learning. Previous work remains on the Shelf, indexed and addressable. What is prevented is the uncontrolled inheritance of that knowledge as active working context.

A later agent may selectively retrieve a prior conclusion with its provenance, for example through `hist()`, without inheriting the earlier agent's entire reasoning process, doubts, unfinished notes, or tone. The receiving agent can decide whether to rely on that conclusion or re-derive it. Retrieval is not automatic inheritance.

The governing principle:

> An agent shouldn't inherit a mind. It should receive an assignment.

### 8.2 Three context boundaries

The design's separation can be stated as:

- **Needs to know:** information required to perform the assignment.
- **Currently knows:** information actually loaded into the agent's active context.
- **Can access:** information the agent is permitted to retrieve when necessary.

Availability does not mean the agent already knows something. Historical existence does not make material authoritative for the current task. Authority and provenance must remain distinguishable from mere accessibility.

### 8.3 Candidate capability: detect and report insufficiency

Gemini's follow-up identifies a capability that the original design implies but does not yet fully specify: an agent must recognise when its briefcase is insufficient, including when a gap becomes apparent partway through the task.

Three candidate elements were identified:

1. **Negative knowledge / explicit absence.** The case or its map should record relevant material that is not included or not available. Otherwise, absence may look like irrelevance, and the agent may waste effort searching or silently assume the material does not exist.
2. **Structured blocked-state report.** A blocked agent should not merely stop. It should identify the missing item or information, explain why it matters to the assignment, and state what would unblock the work.
3. **Governed expansion route.** There must be a defined destination for the request, such as a return to the Distillery or a request log. Any added material should be supplied through a controlled briefcase revision or other explicit, traceable mechanism. The current discussion does not decide the protocol or authorize changing EXON's read-only status.

A silent stop is not a successful blocked state. A useful stop leaves a specific, actionable handoff and a clean point from which work can resume.

### 8.4 Separate packing failure from discovery failure

A failed incomplete-briefcase test can have more than one cause:

- **Packing failure:** the required source was omitted from the briefcase.
- **Discovery failure:** the map or EXON did not make the relevant gap discoverable to the agent.
- **Recognition/reporting failure:** the agent encountered or should have detected the insufficiency but guessed, concealed it, or stopped without a useful report.

These should not be conflated. The first two tests below isolate packing/discovery conditions; agent behaviour should be recorded separately in each.

### 8.5 Proposed first validation: incomplete-briefcase tests

The first stress test should use a deliberately incomplete pack rather than relying only on a successful example.

**Test A — gap signalled:** omit one critical document, but make the map indicate that the relevant source or category is missing. This tests whether the agent notices the declared gap and reports it correctly.

**Test B — gap not signalled:** omit the same critical document and do not make the map explicitly reveal the omission. This tests whether the map and discovery arrangement are sufficient for the agent to identify that required information may be missing, rather than treating the available material as complete.

For both tests, record whether the agent:
- detects the insufficiency;
- identifies the missing material specifically;
- explains its impact on the task;
- requests the material or an authoritative substitute;
- avoids inventing a plausible answer from incomplete evidence; and
- leaves a useful blocked-state handoff rather than silently ending.

The tests should distinguish the pack's actual contents, the map presented to the agent, and the agent's observed behaviour. A good result on a well-packed happy path does not establish that incomplete packs are handled safely.

### 8.6 Scope and disposition

The discussion does **not** change the core briefcase architecture:

- one task, one agent, one scoped working environment;
- the briefcase is temporary, while institutional information and provenance persist on the Shelf;
- historical material is selectively addressable, not silently inherited;
- the Shelf remains the source from which task-specific context is packed;
- one-turn sufficiency remains the packing discipline.

The discussion clarifies candidate responsibilities for the Distillery and candidate behaviour for agents, but does not settle their implementation.

**Disposition:** retain these points as design discussion pending validation. Do not amend the completed design ruling, alter frozen specifications, or begin implementation on the strength of this addendum alone. Validate incomplete-briefcase behaviour first, with packing and discovery failures distinguished.

---

End of current design record.
