# Rulebook Register — classification pass

Started: 2026-11-26, at Ben's direction ("reorganize your thinking"; "Start at your leisure").

## Safety frame (settled before any classification)

- Restore point: `~/workspace/rulebook/snapshot-2026-11-26/` — 702 files, 34 MB, checksum manifest, verified against originals (AGENTS.md, MEMORY.md, scope-ledger.md byte-identical at snapshot time).
- This pass deletes nothing and rewrites nothing in the sources. Classification is a label in this register only.
- The archive (scope ledger, daily logs) is evidence. Only rules still governing behaviour get extracted into the eventual rulebook.
- Conflicts between Ben's rulings are NOT resolved here. They are listed as CONFLICT-CANDIDATE for Ben to rule on.
- Any later switchover (changing what Remmy wakes up to) requires Ben's ruling on the finished draft.

## Status vocabulary

- **STANDING** — still governs behaviour today.
- **SPENT** — a one-time approval/decision whose work completed; evidence only.
- **SUPERSEDED** — replaced by a later ruling; the replacement is named.
- **LESSON** — a dated incident note; the general rule inside it may be STANDING, the incident itself is history.
- **DUPLICATE** — the same rule stated in more than one source; merge candidate (one canonical wording).
- **DERIVED** — a restatement layer (alignment synthesis, summaries). Never a source; never outranks the record it restates.
- **CONFLICT-CANDIDATE** — two standing texts point different ways; Ben rules.

## Source map (measured 2026-11-25/26)

| Source | Size | Role | Treatment |
|---|---|---|---|
| `~/AGENTS.md` | 27,053 B / 119 lines | Wake-up doctrine (injected) | Extract rule by rule |
| `~/workspace/AGENTS.md` | 4 bullets | Workspace house rules (AIvory-era) | Extract; mostly STANDING, partly DUPLICATE of MEMORY.md entries |
| `~/MEMORY.md` | 69,859 B / 163 lines | Curated long-term memory (injected, truncated mid-file in injection) | Extract; separate facts about Ben/projects from rules about behaviour |
| `~/SOUL.md` | 1,874 B | Persona/tone | Keep as its own layer; not a rule source to merge away |
| `~/USER.md`, `~/IDENTITY.md` | small | Identity facts | Keep; not rules |
| `~/PROACTIVE_PREFERENCES.md` | 5,698 B | Proactivity preferences | Extract standing preferences |
| `~/workspace/scope-ledger.md` | 607,135 B / 1,301 entries / 330 date headers | Approval record since 2026-10-19 | Classify entries standing vs spent; do not reorganise the ledger itself |
| `~/workspace/gate-ledger/` | ~71 KB | Gate authorisations/executions/incidents | Evidence + coverage inventory; extract only the standing gate law (already in AGENTS.md) |
| `~/workspace/confidence-check.md` | 2,033 B | Canonical 8-question check | STANDING; AGENTS.md carries a restatement (DUPLICATE) |
| `~/workspace/custom-skills/` (18 skills) | ~55 KB | Learned playbooks | Classify each: standing playbook vs restatement of AGENTS.md rules |
| `~/memory/` daily logs (64 files) | 14,388,800 B | Raw history | Evidence only; mine ONLY for rulings never promoted to MEMORY.md/AGENTS.md |
| `~/dreams/alignment/derived/ALIGNMENT_SYNTHESIS.md` | 21,253 B | Nightly restatement | DERIVED — read for drift-checking, never as authority |

## Pass 1 — `~/AGENTS.md` (root), section by section

1. **THE BRIDGE** — STANDING (definition, marker form, laptop machinery is not the bridge, compaction-dump rule). Note: the "State (updated 2026-11-19 23:45)" line predates the rebuilt bridge v1.0.3 acceptance — wording is stale even though the definition stands. Flagged for the update list, not silently edited.
2. **WHERE REMMY KEEPS FALLING SHORT (watch-list)** — STANDING. Seven named failure patterns with the act each demands. This is behaviour law, not history.
3. **THE BUILD LAW** — STANDING. Duplicated in substance inside MEMORY.md and the alignment synthesis (DUPLICATE as restatements; AGENTS.md wording is canonical).
4. **THE DISCUSSION GATE** — STANDING. Overlaps the Tap Rule and the Universal Gate: three texts govern the same chokepoint. Merge candidate — one canonical gate text, the others point to it.
5. **THE TAP RULE** — STANDING, with a **CONFLICT-CANDIDATE inside it**: the no-carve-out amendment says prose never dispatches a build, however imperative; Ben's clarification recorded in the same section says a complete, unambiguous order in his own words IS an approval equal to a tap. Both cannot be the literal rule at once. Ben to rule which formulation stands.
6. **THE UNIVERSAL GATE** — STANDING. Its own text labels almost everything procedural-only except website publishes via gate.py — that honesty about enforcement is part of the rule and must survive any merge.
7. **THE CONFIDENCE CHECK** — STANDING; canonical text lives in `~/workspace/confidence-check.md`; the AGENTS.md version is a restatement (DUPLICATE).
8. **SCOPE BEFORE SPEC / STACKED AND GROUPED WORK** — STANDING (scope-before-spec, patch limit, prototype-before-production, UI in Remmy's own hands, full-flow check before "live", website publishes through gate.py).
9. **Conventions** — meta-instruction about this file; not a behaviour rule for the rulebook.
10. **Lessons** — mostly LESSON (dated incidents). Standing rules embedded in them, each also stated elsewhere (DUPLICATE): report results not momentum; status checks must touch the live thing; keep working stretches short; the pool drain at focus return; ChatGPT share links need the browser; revised files under a new filename. The rest are tool/site quirks — they belong in TOOLS.md territory, not the rulebook.

## Pass 2 — `~/workspace/AGENTS.md` (workspace house rules)

All four bullets STANDING (Ben, 2026-11-25):
1. Full scope to builders, never a summary.
2. The shelf is the transport, chat is not.
3. AIvory: source-checked always, no improvisation (project-scoped to AIvory).
4. Every proposed change compared to the scope (stated for AIvory; the same rule was stated generally the same evening — scope of the general form to confirm in MEMORY.md pass).

Each also appears in MEMORY.md in near-identical words (DUPLICATE). Canonical home to be decided in the rulebook draft; the rulebook should carry each rule ONCE.

## Open items this pass has already produced

- CONFLICT-CANDIDATE 1: Tap Rule — "prose never dispatches" vs "a complete unambiguous order is a tap". Ben to rule.
- STALE WORDING 1: Bridge state line dated 2026-11-19 inside a STANDING section. Update candidate, Ben to approve wording.
- MERGE CANDIDATES: Discussion Gate / Tap Rule / Universal Gate (one chokepoint, three texts); Confidence Check (two texts); the four 2026-11-25 rules (two homes each).

## Next in the pass

- `~/MEMORY.md` extraction: separate (a) facts about Ben and the projects, (b) behaviour rules, (c) project state that belongs in project files, not the wake-up layer.
- Scope-ledger classification: standing rulings vs spent approvals, entry by entry, mechanically first (dated one-off approvals for completed work = SPENT), human-checked where ambiguous.
- Custom-skills classification.
- Conflict list consolidated for Ben's ruling.

## Pass 3 — `~/MEMORY.md` (141 entries, 69,859 B)

Sections: Facts (lines 5–66, ~62 entries), Preferences (67–116, ~50), Commitments (117–123), then project sections (Sven shortlist, AI Office) to line 163.

What the file actually holds, by kind:
- **Facts about Ben and his life/business** (~25 entries: Sicamous, Skunk, designer, Mr. Night, autism, dyslexia, welfare, the brutal 2026, White Tulip, brand structure, family). These are MEMORY's proper load. Not rules.
- **Behaviour rules for Remmy** (~55 entries — the majority of the file): turn discipline, pause, reporting, privacy, bridge operation, seat handling, approval evidence, brevity, ask-first, personal-hands, account rule. Most are STANDING. Many DUPLICATE AGENTS.md or each other.
- **Project state and project rulings** (~45 entries: Pulse HQ pricing/positioning, CRM, Duenna rulings, framework design rulings, AIvory). These go stale in place and inflate the wake-up layer; their proper home is the project files, with MEMORY carrying at most a pointer.
- **Parked/unruled items wearing settled formatting** (~6): the house motto (candidate, unruled), the 550 words-vs-letters reading, production custody, R16 three-vs-six, the town-name scrub (open item), the showcase PDF re-render (owed).

Structural finding: **the injected copy of MEMORY.md is truncated in the middle (~49,000 characters omitted)** — the file has outgrown what actually reaches Remmy at wake. Part of her own memory is written but never read. Any rulebook that comes out of this pass must be sized to what arrives, with the rest behind pointers.

Duplicate census (major rules with 2–3 homes): Build Law (AGENTS + MEMORY), Universal Gate (AGENTS + MEMORY), Report Results Not Momentum (AGENTS lessons + MEMORY + a custom skill), UI Hands (AGENTS + MEMORY), Personal-Hands (MEMORY + AGENTS in UI form), Shelf Transport (workspace AGENTS + MEMORY), Full Scope to Builders (workspace AGENTS + MEMORY), Confidence Check (AGENTS + its own file), Bridge definition (AGENTS + MEMORY's laptop entry).

## Pass 4 — `~/workspace/scope-ledger.md` (1,301 entries)

Mechanical first pass (keyword scan, human-checkable):
- 473 entries mention a tap/approval — overwhelmingly one-off approvals for specific work on specific days: **SPENT** once their work completed.
- 150 entries carry standing-language markers (standing / always / never / from now on) — the candidate STANDING set for extraction.
- 88 entries mention void / correction / supersede — the ledger corrects itself inline, so a voided entry and its void sit pages apart with nothing linking them. A reader skimming can pick up a dead ruling as live. This is not hypothetical: the false mode ruling of 2026-11-25 23:36 was ledgered, voided 23:37, and the pair still stands unlinked.
- The remainder (~590) are scopes, states, and notes for work in their day — evidence.

Classification rule adopted for the draft: the ledger is EVIDENCE, never live law. Standing rulings get extracted into the rulebook with their ledger citation; the ledger itself is not reorganised.

## Pass 5 — custom skills (18)

- **Restatements of the law in skill form (5)** — DUPLICATE as rules; their procedure detail is the only new content: discussion_before_build_gate (Discussion Gate), result_only_status_reporting (watch-list), grounded_user_history_checks (self-awareness method), settled_text_fidelity_checks, verify_dispatch_at_receipt.
- **Genuine playbooks (13)** — procedure not stated in the law; STANDING as playbooks: agent-reach, first_hand_prospect_research, local-burst-input-confirmation, local-platform-setup-precheck, local_absence_claim_labelling, local_blocked_decision_escalation, local_real_path_verification, local_reviewer_channel_cadence, pictured_simplicity_first, pinned_revision_review_verification, recovered-skill-notes, resilient_scheduled_loops, wake_path_arming_for_new_seat_chats.
- Draft principle: skills hold procedure and point at the law; they do not restate it. A rule changed in the rulebook should not need hunting through skills to stay true.

## Consolidated judgment list — for Ben's ruling

- **J1 — The approval chokepoint contradicts itself.** AGENTS.md's Tap Rule amendment: prose never dispatches, however imperative. AGENTS.md's own clarification + MEMORY.md (two entries, one "restated with force"): a complete, unambiguous order in Ben's words IS a tap's equal, and a scope card is NOT required then. Both stand as law today. Which formulation governs?
- **J2 — Standing permissions vs the per-operation gate.** MEMORY.md carries a standing consent (apply settled rulings without asking, 2026-10-17), the open-ended tap delegation to Alex (Duenna loop), and the ledger carries standing approvals to implementation (AIvory, 2026-11-25). The Universal Gate demands per-operation approval. The exceptions are real but their boundaries live in three texts. Confirm the exception scopes as written, or narrow them?
- **J3 — The wake-up layer must fit what actually arrives.** MEMORY.md is truncated in injection; AGENTS.md + MEMORY.md + synthesis together exceed 115 KB of standing text. Set the rulebook's size discipline: behaviour law in one file sized to arrive whole; facts and project state behind pointers.
- **J4 — One canonical home per rule.** At least nine major rules currently live in 2–3 places. Proposed homes: AGENTS.md (or its successor) = behaviour law only; MEMORY.md = facts about Ben + preferences; project rulings live in project files; skills = procedure only.
- **J5 — Bridge text merge.** The bridge definition lives in AGENTS.md and again in MEMORY.md (the laptop entry), and AGENTS.md's state line is dated 2026-11-19, before the rebuilt bridge's acceptance. Merge to one canonical bridge text; approve the updated state wording.
- **J6 — The ledger's inline voids.** 88 correction/void entries sit unlinked from what they void. Proposal: extraction (Pass 4) resolves this for the standing set; the ledger stays untouched as evidence. Confirm that approach or direct another.
- **J7 — Parked items wearing settled formatting.** Motto (unruled), 550 words-vs-letters (unruled), production custody, R16, the town-name scrub, the showcase PDF re-render. Keep them parked — but labelled PARKED in the rulebook so they stop reading as settled law.

## Examiner input — Alex (relayed by Ben, 2026-11-26 00:15 MST; transport evidence, not a ruling)

- The truncation finding is the most serious: written memory, believed memory, and received memory are three different states; a store larger than its retrieval is a continuity defect even with perfect preservation.
- The scope ledger stays unreorganised; STANDING / SPENT / SUPERSEDED / DERIVED is the right distinction — a historical approval must never become a present permission by accident.
- **Provenance requirement for the eventual rulebook:** every extracted standing rule carries its original source, original ruling date, relevant approval/decision, subsequent amendments, and current classification. The rulebook is the operational view of the history, never a replacement for it.
- J1 and J2 are the critical decisions and must stay SEPARATE: J1 = what constitutes authorisation; J2 = how long authorisation remains valid and what it covers. Remmy must not resolve either by synthesising her own interpretation.
- Layer separation endorsed: behaviour law / personal facts / project files / skills as procedure / ledger as evidence / SOUL as persona.
- Protective principle: the refined rulebook must never become the only surviving representation of the original memory — originals preserved, rulebook a versioned interpretation, so a future Remmy can see not just what governs her but how it came to.
- Recommendation: finish classification without resolving the judgment items; examine the complete proposed rulebook and the seven judgments together before authorising any wake-up change. No premature switchover.
- Closing line, recorded verbatim: "Memory refinement should improve continuity, not manufacture a cleaner past."

## Ben's rulings on the judgment list (2026-11-26)

- **J1 — RULED: BOTH.** A tap on a scope card counts as approval, AND a complete, unambiguous order in Ben's own words counts as approval ("Make it so" = a tap). Fragments, corrections, questions, observations, and unfinished bursts never count. Approval is scope-bound to the thing proposed. The two standing texts both stand; the no-carve-out text governs ambiguous prose, the clarification governs clear orders.
- **J2 — RULED: standing permissions stand, each inside its named scope.** The standing consent (2026-10-17), Alex's tap delegation (Duenna/Alex loop, open-ended until Ben says otherwise), and the AIvory approvals-to-implementation (2026-11-25) remain valid; none of them reaches outside the scope it names. The Universal Gate's per-operation approval governs everything outside those named scopes.
- **J3 — RULED: one law file, sized to arrive whole; the rest behind pointers.** The behaviour law lives in a single file small enough to reach Remmy untruncated at every wake. Facts and project state stay on the shelf behind pointers in that file. (Ben asked whether this could be undone; it can, at every stage — ruling, draft, and switchover are each reversible, and the 2026-11-26 snapshot is the restore point.)
- **J4 — RULED: one canonical home per rule.** Layers: behaviour law in the law file; facts about Ben and preferences in MEMORY.md; project rulings and state in project files; skills hold procedure only; the scope ledger is evidence; SOUL.md is persona. A rule changes in exactly one place.
- **J5 — RULED: merge the bridge into one canonical text, state updated.** One bridge text in the law file; the state line is brought current past 2026-11-19 (rebuilt bridge installed and accepted); MEMORY.md's duplicate becomes a pointer.
- **J6 — RULED: the ledger stays untouched as evidence.** No reorganisation of `~/workspace/scope-ledger.md`. Standing rules are extracted into the rulebook with provenance (source, ruling date, amendments, classification) per Alex's safeguard; the unlinked-voids problem is solved in the rulebook, not in the evidence.
- **J7 — RULED: parked items stay parked, labelled PARKED.** The motto, the 550 words-vs-letters question, production custody, R16, the town-name scrub, and the showcase PDF re-render go into the rulebook's PARKED section, visibly unruled — never formatted as settled law.

**All seven judgments ruled by Ben, 2026-11-26 00:16–00:20 MST.** Next step per the agreed order: Remmy drafts the rulebook beside the originals (provenance on every rule, per Alex's safeguard), Ben examines the draft and these rulings together, and no wake-up file changes until Ben authorises the switchover.

## Draft v1 built (2026-11-26, per Ben's "Proceed")

`~/workspace/rulebook/RULEBOOK-DRAFT.md` — 18,755 B, 152 lines, 9 sections, 29 STANDING rules each carrying provenance. Built beside the originals; no live file changed. Awaiting Ben's examination (with the J1–J7 rulings) before any switchover is proposed.

## Examination of Draft v1 (Ben, 2026-11-26)

- §1 Approval and gates — STANDS AS WRITTEN (Ben, 00:28 MST).
- §2 Building — STANDS AS WRITTEN (Ben, 00:29 MST).
- §3 The bridge — STANDS AS WRITTEN (Ben, 00:30 MST).
- §4 Working with Ben — CHANGES REQUIRED (Ben, 00:32 MST): **4.1 corrected** — READ. WORK. RESPOND. is the discipline for working with VANE, to keep the loop going; it is never for Ben. With Ben, we discuss first. Draft §4.1 amended in place with the corrected scope and provenance.
- §4 Working with Ben — STANDS AS AMENDED (Ben, 00:32 MST).
- §5 Memory and the record — CHANGES REQUIRED (Ben, 00:33 MST): **5.2 amended** — include shelf pushes for every change; a change is not current until it is pushed, not merely saved locally.
- §5 Memory and the record — STANDS AS AMENDED (Ben, 00:33 MST).
- §6–§9 — STAND AS WRITTEN (Ben, 00:34 MST).

**Examination complete.** Draft v1 examined section by section; two amendments made at Ben's direction (§4.1 loop-discipline scope; §5.2 shelf pushes for every change). The switchover decision is Ben's, separately.

## SWITCHOVER EXECUTED (2026-11-26 00:37 MST, Ben: "Okay, do the switch.")

- `~/AGENTS.md` now contains THE RULEBOOK v1, byte-identical to `~/workspace/rulebook/RULEBOOK.md` — sha256 `8486e672170d6779873c2fcd1e3836b281db728cd37a2419899bb81adb8720fa`, 19,756 B (replacing the 27,053 B original).
- The original AGENTS.md stands preserved in `~/workspace/rulebook/snapshot-2026-11-26/AGENTS.md` with its checksum in the snapshot manifest. Undo = restore that file and verify the checksum.
- `~/MEMORY.md` untouched, per the staged plan; its facts-layer pass is a separate, later examination.
- Note: the shell could not write `~/AGENTS.md` (root-owned, 660); the switch was written through the file tools and verified by hash at the receiving end.
