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
