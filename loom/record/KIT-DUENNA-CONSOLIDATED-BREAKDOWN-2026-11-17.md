> **Filing note (Remmy, 2026-11-16):** Filed at the owner's direction ("Just shelf it", main chat, 2026-11-16 17:25 MST). Author seat: Kit. The document below is Kit's text verbatim as delivered to the owner and pasted into main chat; Kit's cover note to the owner (declining to re-issue the 16 November breakdown under his name, as it was not his) is conversation, not part of this document. Class per the document's own header: derived consolidation — non-normative, unfiled until this filing, supersedes nothing. Its record pin (9ceca1f) predates the Stage 6 pre-flight clearance (Alex, @ d61a479e); §11/§13 state the position at the pin.

---

# DUENNA — CONSOLIDATED BREAKDOWN
**Author seat:** Kit · **Date:** 2026-11-17 · **Class:** derived consolidation — non-normative, unfiled, supersedes nothing
**Record pin:** `Q420/ainternet-shelf` @ `9ceca1fcee37535a926103189ce6ded46f1ae5de` (main, 2026-11-17 00:01 UTC; 2,144 files, 705 commits; shelf opened 2026-11-10)
**Evidence convention:** **[V]** verified against the pin this session · **[R]** reported (16 Nov breakdown / conversation; not re-verified) · owner quotes are recorded rulings **[V]**. Where the 16 Nov breakdown and the record disagree, both are shown; the record wins; reconciliation is the owner's.

## 1. What Duenna is
A governed-agent ecosystem built on one bet: *a smaller model inside a well-designed system of roles, permissions, evidence and enforcement can work more reliably than a larger model without those controls.* The model reasons; Duenna supplies governance, enforcement and verification. The aim is not infallibility — it is making errors harder to introduce, easier to detect, and harder to misrepresent. House maxim, verbatim from the shelf README **[V]**: *"AI is allowed to be wrong, but it's not allowed to pretend that it's right."*

Two domains: **action governance** (what an agent may do, its obligations, how compliance is proven) and **knowledge governance** (what it can know, where that came from, how it moves between tasks without uncontrolled inheritance).

## 2. The Shelves — and an open reconciliation
- **AInternet Shelf** — institutional memory and programme record **[V]**. Catalogue is `MANIFEST.md`; the record wins over conversation summaries; evidence classes travel with claims; UNKNOWN is never written as absent.
- The 16 Nov breakdown describes a **Fact Shelf** (canonical facts, authority *above* EXON) and an **EXON Shelf** (operational language), with the caveat that the Fact Shelf "is not automatically true merely because something has been placed there" **[R]**.
- **The owner's terminus ruling supersedes that framing [V]** (Briefcase record §9, 2026-11-16 16:12 MST): *"simply because the exon shelf is definitely absolutely fact"* — the reference side of every comparison is the EXON shelf itself; and *"there needs to be an end point so the end point is going to be the comparator."* Checking terminates at a re-performable comparison; judgment terminates at the owner.
- **Open owner decision:** the three-Shelf hierarchy in the breakdown is in tension with the terminus ruling. I preserve both; I have not inferred a resolution. Reconciling the taxonomy to the ruling is yours to record.

## 3. EXON — addressing, vocabulary, serialization
Controlled operational language plus deterministic addressing. The seven desk rulings of 2026-11-16 (owner, confirmed 13:26 MST: *"the highlighted option is my decision on all seven"*) **[V]**:
1. **Dictionary 0.5 ADMITTED** as the standing dictionary — **50 terms**: original 38 + Letter 04's six (GRANT, AUTHORISE, SETTLED, DISTILLED, SETTLE, REVOKE) + four coinages (FUTILE, IMPOSSIBLE, DENIED, DEPRECATED) + Letter 05's REVIEW and HARDENED.
2. **D-REF-1:** index pin required (mechanism to be built).
3. **D-REF-2:** both locators required — line coordinates mandatory, JSON Pointer structural alongside.
4. **D-REF-3:** SHA-256 sole normative; Git blob ID is repository metadata only.
5. **D-REF-4:** separate success record with a chosen outcome word.
6. **Serialization adopted:** JSON authoritative; RFC 8785 (JCS) canonical; SHA-256 with explicit `sha256:` identifier; canonical bytes authoritative, pretty-print a human view only.
7. **Duenna Stage 6:** proceed to the calls — *"opens the calls; it does not set them."*

Addenda **[V]**: **SUCCESS** is the outcome word (gloss "triumph"), fenced — it means the coordinate resolved under the stated procedure, *not* that the source is true, supported, authoritative or accepted. **DESTINATION** admitted (gloss "endpoint"). **YES** admitted as the current-state marker, one job only, fenced from evidence grades (VERIFIED, HARDENED), rulings, RECEIVED and PASS. **PREVAIL** admitted as the state standing in force — *"standing by acceptance, not by recency"*; CURRENT rejected as drifting to "latest by date"; SUPERSEDED its opposite. **HARDENED** reads under your ladder *"researched is verified; proven is hardened"*; **STOP** under your threshold — falsity entering the canonical records.

**Correction to the 16 Nov breakdown [V]:** it classed FUTILE/IMPOSSIBLE/DENIED/DEPRECATED/REVIEW/HARDENED as mere later drafts. They are *admitted* within Dictionary 0.5. Separately, the **six foundational proposals of Letter 24 are NOT admitted** (SEAT, GATE, CHECK, FLAG, COMMITMENT remain unadmitted; DESTINATION admitted by its own ruling). Still **[R]**, not re-verified: WAKE's exclusion, DISTILLED's stated condition, the `=` comparison/supersession design. Governance note **[V]**: the desk app failed to persist the sign-offs; the chat record plus your screenshots are the evidence of record.

## 4. The Comparator — CLOSED, not open
**[V]** Owner ruling, 16:12 MST: *"It doesn't audit Duenna's outputs it compares them."* The act is comparison — two records side by side, reporting where they differ; re-performable evidence, **no verdict**. That is why it needs no checker of its own and why its remit reaches Duenna's outputs without becoming an authority over them. Judgment on what a difference means stays with the examiner and the owner. The 16 Nov breakdown's "open question" status is stale against this. No additional auditor or worker is authorised (§9 disposition stands).

## 5. The Distillery
**[V]** Owner statement filed in Briefcase §8: *"Distillery is two parts. The destiller, and the warehouse worker. WW validates and verifies shipments of briefcase material against the source."* And: *"The distiller only gives the agent what's required for the task at hand that's going to be updated on the Shelf."* Distiller = judgment (select, distill, pack); WW = inspection (validate form, verify substance against the Shelf). Two failure classes: **selection** (wrong/omitted material) and **fidelity** (misrepresented transfer). Fidelity-to-Shelf is not truth-of-Shelf — the SUCCESS fence and the terminus ruling govern where checking ends.

## 6. The Agent Briefcase
**[V]** *"DESIGN IDEA COMPLETE — Ben's ruling, 2026-11-16 14:21 MST ('My design idea is complete'). … No build is authorised by it."* Task-scoped working environment; *"An agent shouldn't inherit a mind. It should receive an assignment."* Three categories — Required / Available / Historical; **one-turn sufficiency** is the acceptance test (owner: the agent *"can operate sufficiently within one turn without scanning the entire shelf"*); the case carries a **map**, not the Shelf; `hist()` gives selective historical retrieval with provenance; at close, outputs persist, working context is discarded.
Recorded **candidates (discussion only)**: coverage fence (map declares its own partiality), cold-read close, sealed deliverable layer, grade+supersession precedence, directive/testimony address classes, write-target packing criterion, per-claim distillation coordinates, WW at close, no-bare-verdict invariant, non-circular re-performance. **Three questions remain open awaiting you [V]:** write-target criterion, distillation gate, WW receipt re-performer. **Validation not yet run [V]:** Tests A/B, cold-read, mutation, correlated-failure.

## 7. Proof and enforcement architecture (Step 6)
**[V]** `record/DUENNA-STEP6-ARCHITECTURE.md` hashes to exactly the catalogue claim. Four components — **RECORD** (preservation, digests, append-only, failed/absent bindings recorded), **BINDER** (mechanical binding to pinned contracts; outputs only to RECORD; failure recorded, never mistaken for success), **EVALUATOR** (lifecycle derivation + obligation accounting: satisfied/blocked/unmet/indeterminate), **EXAMINER** (independent re-derivation from the original record, never from EVALUATOR's conclusions). **F5** is not a fifth component: governance edges (authority from Ben) and enforcement edges (mechanical checks of pinned rules). Dependencies: RECORD stands alone; BINDER on RECORD; EVALUATOR on RECORD via BINDER's entries; EXAMINER on RECORD + pinned contract + reproduction rules. Component semantics here are summarised from the breakdown **[R]**, consistent with the agreed text.

## 8. Modular verification (§10 — omitted by the 16 Nov breakdown)
**[V]** Agreed design principle (Ben/Alex exchange): *"Modularity does not remove complexity; it moves risk to the interfaces."* Each machine proves its own guarantees independently; each composition seam gets a **written, versioned, pinned contract** with independently executable conformance fixtures; the real machines are then composed against that same contract. Failed compositions are classified — **component breach / contract breach / contract ambiguity** — and preserved as evidence; a later pass never erases an earlier failure. Three evidence classes stay distinct: component guarantees, contract-vs-fixture behaviour, actual composition. Example seams (not approved designs): Duenna↔Distillery/Briefcase, Briefcase↔EXON, WW↔RECORD. No composition is authorised by this principle.

## 9. Seats and collaboration
Ben — owner, final authority. Alex — technical lead, delegated adjudicator. Remmy — lead developer, record keeper. Claude and Vane — independent examiners; Grok — second adjudicator on a D3 matter **[R]**. Kit — bridge seat; my read-backs and session summary are filed as §8 of the design record **[V]** (Remmy's filing note under your 16:05 *"File it as integrated"*); there is no `seats/kit.md` at this pin **[V]**. Participation never confers authority; output retains provenance.

## 10. Pulse Bridge and Crusher
Collaboration infrastructure, not reasoning authorities. The Bridge carries explicitly marked messages with identity and delivery history; **Crusher** is the deterministic transport/state machinery (`bridge/crusher.js`, crusher-harness, fix-test evidence) **[V]**. A delivered message is not a verified conclusion.

## 11. Testing and the Nemotron pilot
Discipline **[R]**: acceptance criteria, preserved fixtures, regression/negative/sabotage tests, independent examination — a safeguard is proven by disabling it and showing the dependent test fails. Pilot, verified from the rollover record **[V]**: 13 Pack v3 instances against `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` under Rev 26; smoke = one minimal call, 5,000 total tokens; battery = 50,000 total tokens per instance (input plus output); exhaustion recorded `BUDGET_EXHAUSTED`, never a pass; ≥3 exhausted instances halt for review; no paid route without a new owner decision; config temp 0.6 / top_p 0.95 / max_tokens 20480 / stream false / thinking enabled, reasoning budget 16384. **Correction round CLOSED; pre-flight NOT YET CLEARED; smoke authorised conditionally, not fired.** And the boundary the breakdown omitted (§10.4) **[V]**: *"An objective statement that a pilot compares a model alone against a governed model is not, by itself, a test design… the pilot must not be cited as proof of that proposition. The pilot may bear on the proposition; it does not establish it merely by being run."*

## 12. Governance
Readiness is not authority. Discussion, prepared packages, successful tests, completed designs and silence are never permission. No component grants itself permission. Implementation is authorised stage by stage; adoption after independent examination remains yours.

## 13. Status at the pin
| Area | Recorded position | Class |
|---|---|---|
| Step 6 architecture / Step 7 plan | Agreed; hashes match catalogue | V |
| D3 v0.9 / v0.10 | NOT APPROVED; gate open (catalogue-recorded) | V |
| Four fixture gaps / Stage 2 contract execution | Open & unverified / not authorised | R |
| Nemotron correction round | Complete and accepted | V |
| Nemotron smoke / battery | Conditionally authorised, not fired / not authorised by smoke | V |
| EXON Dictionary 0.5 | ADMITTED, 50 terms (13:26 MST) | V |
| EXON reference + serialization rulings | Adopted (desk seven + addenda) | V |
| Agent Briefcase design | Complete 14:21 MST; no build authorised | V |
| Distillery | Two-part design statement filed §8 | V |
| Comparator | CLOSED — comparison not audit; terminus (16:12 MST) | V |
| Three-Shelf taxonomy vs terminus ruling | Tension surfaced; reconciliation is an owner decision | obs. |
| Modular verification (§10) | Agreed principle; no composition authorised | V |
| Briefcase open questions / validations | 3 awaiting owner / Tests A/B, cold-read, mutation, correlated-failure unrun | V |
| MANIFEST catalogue | Stale (Nov 11) vs tree (Nov 16–17) | V |
| New Briefcase build / extra audit worker | Not authorised | V |

## 14. Verification appendix
**Hashes computed at the pin:** STEP6 `69664387…637d` and STEP7 `929b2378…06a64` — both **match the catalogue exactly** (programmatic comparison). Briefcase design `2c1006d1…bf94d`; rollover `fa4d2bd8…db2b9`; owner rulings `2c6317dd…f1c584`; MANIFEST `3b4462fb…ce21f` (114 lines; zero entries for BRIEFCASE, plaincode/, desk/, ROLLOVER, STAGE6-CALLS, NEMOTRON, EXON).
**Corrections to the 16 Nov breakdown:** Comparator open→closed; Fact-Shelf hierarchy vs terminus ruling; six "draft" terms actually admitted in 0.5 (and Letter-24's six *not* admitted); §10 and §10.4 omitted; MANIFEST staleness; the three open owner questions compressed away.
**Not re-verified [R]:** WAKE exclusion, DISTILLED condition, `=` design, four fixture gaps, Stage 2 authorisation, Grok adjudication status; D3 examination reports cited as catalogue-recorded, not re-read.
**Observation:** no `EXON-DEVELOPMENT-LETTER-22` path at this pin (01–36 otherwise present); whether skipped, renamed or never filed is UNKNOWN.
