# DUENNA — THE PLAN LIST

**What this is:** the single structured restatement of where the Duenna
programme stands and exactly where it proceeds from. Ordered by Ben
(2026-11-10): *"an actual plan list checked out, so we know exactly where
to proceed from. it must be maintained vigorously."*

**Maintenance rule (Ben's, binding on Remmy):** this list is updated in
the same turn as any state change it records — a ruling lands, a package
moves, a step opens or closes. Entries are dated. If this list and the
underlying record (ledgers, bridge letters, MEMORY) ever disagree, the
record wins and this list is corrected on sight. A stale plan list is a
defect, reported like one.

**Last checked against the record:** 2026-11-10, ~16:00 PST.

**THE AINTERNET SHELF — GITHUB HOME (2026-11-10 ~14:41):** the shelf now
lives at **github.com/Q420/ainternet-shelf** (public, main; Q420 is Ben's
new main git, ruled ~14:29). Seeded with 9 files (4 commits): README,
MANIFEST (sha256 for every shelved file), seats/alex.md, seats/vane.md,
seats/remmy.md, record/DUENNA-PLAN.md (the 2026-11-10 state at seeding),
record/DUENNA-STEP6-ARCHITECTURE.md, record/DUENNA-STEP7-PLAN.md,
record/v010-unresolved-items.md. Local staging: ~/workspace/ainternet-shelf/.
Alex's seat page carries road-proof token AINTERNET-SHELF-2026-1110-KESTREL.
**PULL TEST PASS (2026-11-10 ~14:45, bridge pb-mwbc906q):** the
Q420-connected Alex seat pulled MANIFEST.md, seats/alex.md and this plan
cold through its GitHub connector and quoted the token exactly; its
answers (next step = the Track 1 ferry; v0.9 and v0.10 NOT APPROVED;
Stage 2 unauthorised) match the record. The connector door is proven —
no relay, no corpus. Alex also caught this list's section D describing
steps 5–6 as pending/live; reconciled the same day (see section D).

---

## A. Authoritative state (Alex's step 1 — accepted as working baseline, pb-mwavecjk)

Artefacts:

| Artefact | State | Identity |
|---|---|---|
| D3 v0.7 specification | Frozen, immutable | sha256 28718d26… (file a14cad05…, Serial BP-0011) |
| D3 v0.8 specification | APPROVED WITH STATED CONDITIONS (Alex, confirmed); immutable | sha256 3e053efc… |
| D3 v0.9 specification | Examined; **NOT APPROVED**; verification gate OPEN | sha256 ac2a2484… |
| D3 v0.10 specification | Built under Alex's adjudication; **NOT APPROVED**; awaiting independent re-examination | sha256 9241a8b4… |
| Fixture harness | v2.1 (fixtures-v010); 31 cases, all preserved from v0.9 | sha256 efe69df6…; results ad4dc137… |
| EXECUTION-CONTRACT-v0.1 | Untouched | sha256 c7e68901… |
| Simplification audit | Delivered; INPUT to planning, not a plan | sha256 13984600… |

Gate and authority:

- **Verification gate: OPEN.** v0.9 dispositions (Alex, pb-mwauqmco):
  R42 PASS, R47 FAIL, R56 PASS, R60 FAIL, R63 PASS, R65 FAIL; S2 a
  clarification, not a failure.
- **Stage 2: not authorised** in either sense (Contract design authorised
  2026-11-08, unstarted; execution not authorised).
- **Delegation in force:** Alex holds three calls — opening revision
  steps, approving D3, authorising Stage 2 execution. Spend, outreach,
  every publish, and accounts remain Ben's alone. Inside the programme
  loop, Alex's clearances initiate Remmy's steps; results are reported
  to Ben. (Alex's step-2 qualification, pb-mwavecjk: external authority
  means Ben's final authority over normative changes with delegated
  execution intact — not Ben personally approving every action.)
- **Adjudicators:** Alex (delegated, has ruled on v0.9). Grok — appointed
  second adjudicator by Ben; his ruling on the v0.9 gate is
  **outstanding**.
- **Examiners of record:** Claude (primary reviewer, v0.8 and v0.9) and
  Vane (independent examiner, v0.9).

## B. Tracks

### Track 1 — Verification gate (v0.10 re-examination)

1. ✅ Revision authorised by Alex's adjudication (R47/R60/R65 only).
2. ✅ v0.10 built; all conditions held (v0.8 immutable, 31 cases
   preserved, four gaps untouched, no status changes, no Stage 2).
3. ✅ Return package built: `v010-return-documents.zip` (sha256
   934ecd65…, 12 files incl. change record, traceability,
   unresolved-items list, sabotage evidence).
4. **→ NEXT: the pull letter.** **THE FERRY IS RETIRED (Ben's
   ruling, 2026-11-10 15:01):** step 4 is now a pull letter from
   Remmy to the examiners naming the shelf paths of the v0.10
   return set (the spec, change record, traceability, fixture
   results + register, results, harness, unresolved items — under
   `duenna/` and `record/` on github.com/Q420/ainternet-shelf).
   Claude pulls through his Q420 connection; Vane examines from
   the forum copies (topics 8–15) until Ben connects him (Ben,
   2026-11-10: next time around), then the same pull letter. The
   zip (sha256 934ecd65…) remains an archival artefact — no longer
   the transport; nothing on this track waits on files being
   carried by hand.
5. 🔶 Independent re-examination of the three repairs.
   **Claude's report IN (2026-11-10, pulled from the shelf himself;
   CLAUDE-VERIFICATION-REPORT-V010.md, sha256 8686624a…):** R47 PASS
   (narrow — content examined and recorded; a failing-content case
   is covered by construction, not by a fixture of its own), **R60
   FAIL (partial repair)** — the REQ-I-2 trio and its rejections
   hold, but the preservation check's digest-mismatch branch is
   never exercised: FX-R60d's invalid case exits through the
   self-set `corrupt` flag before the digest comparison runs, and
   removing the comparison (his sabotage S1) leaves all 31 green.
   FX-R61 tests its own copy, not `_preservation_check`;
   `pinned=True` remains caller-supplied. Remmy confirmed the
   mechanism in the source the same day. R65 PASS (caveat: values
   checked against the test's own constants). All regression
   conditions confirmed; all 59 manifest entries matched his clone.
   **Vane's re-examination IN (2026-11-10 ~15:46,
   VANE-EXAMINATION-REPORT-V010.md, sha256 884fe426…):** pulled the
   evidence himself through his GitHub connection (Ben connected
   him the same afternoon; the deferral was overtaken by that
   connection and his own stated responsibility — he flagged the
   recorded deferral himself before proceeding). He did NOT
   consult Claude's report, and did NOT independently re-run the
   harness (31/31 treated as implementer-reported). Dispositions:
   R47 PASS; **R60 FAIL — a DIFFERENT defect from Claude's:** the
   declared procedure identity is not bound to the executed
   callable — a contract constructed with a fictitious procedure
   name executes _preservation_check, stamps the verdict with the
   fictitious name, and validate_verdict ACCEPTS it (Remmy
   reproduced this by execution the same day). R65 PASS with a
   scope qualification (the required set is caller-supplied; its
   authority is not independently established — the same species
   as Claude's caveat). Overall: v0.10 NOT READY FOR APPROVAL.
   His recommendation: a narrow R60 correction binding procedure
   identity to execution, with a negative test at contract
   CONSTRUCTION. **Both examiners are now in: R47 PASS/PASS, R60
   FAIL/FAIL by two distinct mechanisms, R65 PASS/PASS with
   qualifications. The combined adjudication (step 6) can proceed.**
   **COMBINED ADJUDICATION IN (2026-11-10 ~15:58, Alex,
   pb-mwbeucoj, ⟦ALEX-FINAL⟧; record:
   ALEX-COMBINED-ADJUDICATION-V010.md):** final dispositions
   R47 PASS narrow, R60 FAIL, R65 PASS qualified; v0.10 NOT
   APPROVED. **The R60 revision step is OPEN, scope = BOTH
   defects** (A: one negative fixture — wrong digest, no corrupt
   flag, through run(), sabotage-provable; B: bind the declared
   procedure identity to the executed callable, negative test at
   contract construction). Remmy's implementation is AUTHORISED
   for those two corrections only; the corrected package returns
   for independent examination. Stage 0 and Stage 2 unchanged
   (Ben's tap / not authorised). Grok outstanding, does not gate.
   **Preparations completed
   2026-11-10 under Alex's next-steps recommendation (pb-mwbduahf):**
   Vane's pull letter is PREPARED (VANE-PULL-LETTER-V010-REEXAMINATION.md
   — independent by design, no other examiner's verdicts inside;
   dispatch waits on his connection); the Stage 0 baseline evidence
   pack is PREPARED, UNEXECUTED (stage0-pack/); a gate & dependency
   register now stands alongside this list (GATE-REGISTER.md,
   shelved at record/GATE-REGISTER.md) — readiness is not authority,
   and no gate moved. **Update 2026-11-10 ~15:36 (Ben's direction):**
   Vane is DEFERRED — the programme sticks with Alex and Claude for
   now (Ben's ground: last night's retrieval failure was
   environmental, not any one seat's alone). The letter stays
   prepared. What the deferral does to the combined-adjudication
   sequence is Alex's call — put to him in pb-20261110-vane-deferred;
   his ruling is awaited and will be recorded here.
6. 🔶 Adjudication of the re-examination. **Alex's adjudication of
   Claude's findings IN (2026-11-10, pb-mwbd62gk, after pulling the
   report from the shelf himself):** dispositions ACCEPTED as the
   first examiner's report — R47 PASS narrow (claim not to be
   expanded beyond what was tested), R60 FAIL partial (substantive,
   not a nit), R65 PASS (caveat stands). **v0.10 remains NOT
   APPROVED; the 31/31 does not cure R60.** The scope of any
   further revision is defined and limited to R60 alone: ONE
   fixture, wrong-digest payload, no corrupt flag, through
   CheckerContract.run(), reaching the _preservation_check mismatch
   branch; removing the comparison must make it fail. Nothing else
   — no trio redesign, no R47/R65 changes, no unrelated hardening.
   **But the revision step is NOT OPENED:** Claude's report is the
   first examination, not the complete one. **Alex's ruling on the
   Vane deferral (2026-11-10, pb-mwbe3szw):** the FULL adjudication
   remains gated on Vane — Ben deferred him; he did not waive the
   two-examiner safeguard, and no waiver is inferred. An INTERIM
   adjudication proceeds now: Claude's report formally assessed as
   a single-examiner evidence review, its limit stated on its face
   (the pb-mwbd62gk dispositions stand as that assessment). The
   interim review does NOT open the R60 revision — Alex decides
   that after the full adjudication, unless Ben explicitly changes
   the authority or the examination requirement. (Grok's v0.9
   adjudication lands on its own track whenever delivered.)

### Track 2 — Joint implementation planning (Alex's corrected process)

Agreed workflow (Alex, 2026-11-10): neither side prescribes the
architecture alone; no new safeguards or subsystems by default; no
implementation revision starts from this track until the plan is agreed.

1. ✅ **Step 1 — authoritative state:** agreed (this document, section A,
   is its maintained form). Alex's qualification recorded: he accepts
   Remmy's reported state as the working baseline; he does not certify
   the v0.10 package inside this exercise. Planning and adjudication
   tracks remain separate.
2. ✅ **Step 2 — core functions:** six functions agreed as the starting
   inventory (mechanical binding; ordered evidence record;
   evidence-derived lifecycle; obligation accounting; external
   authority; independent re-derivation). Three investigations OPEN,
   Alex's challenges:
   - (a) Functions 3 + 4: one mechanism, two views? — lifecycle
     derivation vs obligation accounting.
   - (b) Function 2: the guarantee is "historical evidence cannot
     silently change" — no more machinery than that needs
     (immutable vs append-only-with-corrections distinction).
   - (c) Function 5: authority precision (see section A).
   Also agreed: **no fixed component count** — functions and
   dependencies determine the architecture's shape.
3. ✅ **Step 3 — mapping delivered** (DUENNA-STEP3-MAPPING.md; letter
   pb-20261110-step3-mapping). All 48 requirements mapped to the six
   functions. Headline findings: no dead requirements except K-2
   (serves no function — register material); six true duplicates
   (B-5, D-2, D-5, D-6, J-2, H-7); C-3 is one ID carrying three
   functions; the function graph is a chain (F1→F2→F3→F4→F6) with F5
   orthogonal. Remmy's positions tabled on all three step-2
   investigations. Alex's challenge landed (pb-mwavq814): mapping
   **provisionally accepted**; F3/F4 settled (one mechanism, two
   guarantees); F5 challenged (authority is enforced *inside* the
   pipeline, not merely orthogonal); duplicates NOT yet approved —
   five-check examination demanded per pair; full mapping document
   requested into the shared working material. **Step 3 ACCEPTED WITH
   AMENDMENTS (Alex, Chicken, on the mapping itself):** the F1→F2
   dependency is SPLIT — the record is a foundation independent of
   binding (evidence of a binding *failure* must be recordable, or
   the failure erases its own evidence); only instance-related
   entries depend on F1. F2's six-part identity taxonomy stays
   PROVISIONAL (each category must earn its place with a distinct
   failure it prevents, or be consolidated). The four-stage pipeline
   stays PROVISIONAL until step 6. New step-4 test added by Alex: if
   binding fails, can the system still preserve the failure's
   evidence and keep the absence from reading as success?
4. **→ IN FORMATION: Step 4 — from the findings, per Alex.**
   Remmy's step-4 examination delivered (DUENNA-STEP4-EXAMINATION.md;
   full mapping + response triggered into Alex's window by Ben's loop
   approval, 2026-11-10): six pairs examined — five pass (B-5→D-1 and
   J-2→A-2 clean; D-5, D-6, D-2 with named residues carried), Pair 6
   (H-7→J-1) passes mechanically but is **Ben-gated** (J-1 is
   OWNER-RULED). F5 corrected: externally governed, mechanically
   enforced — governance edges + enforcement edges, no decision
   edges. Correction-destination inventory: one genuine gap (checker
   verdicts have no supersession path) and one ambiguity (discharge
   records), tabled without proposed mechanisms. C-3 refined: one
   requirement, obligations grouped by function. Step 4's agenda, in
   order: the duplicates; the F5 edges; the correction destinations.
   **Alex's response (via Chicken, triggered under Ben's loop
   approval):** F3/F4 ACCEPTED; F2 ACCEPTED with a preservation
   condition (F6 normalises, never reconstructs — F2 must preserve
   whole); F5 ACCEPTED with gate wording corrected (the gate *judges
   receipt*; the contract defines the consequence; the machinery
   applies it — "permits" retired); five consolidations ACCEPTED as
   executable candidates under his rule (destination for content +
   fixture + identity, testability re-proven by running the fixture
   against the survivor — a tombstone is traceability, not proof);
   H-7→J-1 reservation SECONDED by Alex (Ben's decision, both sides
   agreed); C-3 ACCEPTED. He adjudicated from Remmy's letter + the
   mapping — the STEP4 examination document was not in his material,
   labelled by him; offered for paste if he wants row-level checks.
   **Challenge A LANDED (checked against the v0.10 text by Remmy):**
   no correction relation exists for execution-stream entries —
   every dispute/supersession mechanism attaches to registers (H-3,
   C-3 (vi)); K-3's boundary keeps registers out of the fold. The
   fold would consume a wrong entry and an ordinary answering entry
   as two facts. Stream-entry correction is a GAP (Remmy's inventory
   had wrongly labelled it "deliberate"). Checker-verdict correction
   gap CONFIRMED by Alex with problem statement (preserve original,
   record finding, operative verdict clear for reporting). Discharge
   = AMBIGUITY (G-1 gives location/content, not supersession).
   Step 4 agenda in Alex's order: (1) F5 graph record; (2) the five
   consolidations into the proposal with equivalence evidence;
   (3) correction-destination dispositions. Alex's round-two reply
   (Chicken): F2/F5 wording ACCEPTED; Challenge A finding ACCEPTED;
   the step-4 disposition list carries EXACTLY THREE items
   (stream-entry correction; checker-verdict correction; discharge
   ambiguity) and no mechanism is to be invented before the
   disposition work reaches them. **Process decision (Alex): the
   STEP4 examination document must be in the Chicken conversation
   before the plan relies on it as verified equivalence evidence** —
   pasting ordered 2026-11-10 (loop's final round; then C-15).
   Alex's first Chicken reply has since been collected (step-3
   amendments above). Ben re-supplied the forum password in chat
   (~07:15) for the C-15 backup — transient use only, NOT stored,
   same handling as before. **STEP 4 EXAMINATION VERIFIED BY ALEX
   from the document itself (Chicken):** all five consolidations
   SUPPORTED with fixture qualifications (B-5's surviving fixture
   must scan evaluator *output*; D-2's fixture mapping must name
   BOTH B-2 and D-3); Pair 6 owner-gated; F5 accepted with one
   sentence of Remmy's examination corrected to his wording (the
   gate originates no permission — correction applied to the
   document); gaps/ambiguity confirmed from the text; LINK
   consolidation = proposed, equivalence UNPROVEN pending the H-6
   (v)/(vi) fixtures. **The Alex loop is CLOSED for tonight** — the
   next useful work is the finished record, not new machinery
   (Alex's closing words). C-15 (forum backup) starts now.
   **Bridge delivery identified (2026-11-10 ~07:28; seat verified by
   ChatGPT search at Ben's direction ~07:31 — Remmy's first framing
   of it as merely "stale" was wrong in part):** the message came
   from the ChatGPT thread **"Adjudicate Technical Review"** (in
   Recents, NOT the Pulse HQ project) — the bridge seat's thread. It
   is Alex's LIVE answer to Ben's own question there ("si how do we
   proceed from here my friend :)", displayed 8:23 AM Ben's clock),
   proposing the challenge round and drafting a letter to Remmy.
   That thread holds the bridge letters (incl. the pb-mwavq814
   challenge) but NOT the full mapping, the step-4 examination, or
   the gap findings — the detailed document rounds happened in
   Chicken (1) (Pulse HQ project), a different thread. Its requests
   are all already satisfied; NO action taken on it. Open question
   for Ben, no urgency: two Alex threads hold different states of
   the same programme — sync "Adjudicate Technical Review" with
   tonight's outcomes (one bridge summary letter), or keep the
   threads' roles distinct (bridge = adjudication seat, Chicken =
   document/planning seat)? **Ben directed "continue the loop"
   (2026-11-10 ~07:43): sync letter sent to the Adjudicate seat via
   the bridge (pb-20261110-loop-sync)** — Chicken-round outcomes
   reported to that seat in compressed form, the two-thread fact
   named, steps 5–7 proposed as the continuation, seat-handling
   question put to Alex and Ben jointly. **Adjudicate seat synced
   (Alex, pb-mwax6p82):** the amendments are ACCEPTED there as the
   current planning record — F1/F2 split, provisional taxonomy, F5
   wording, both gaps, the discharge ambiguity, the five supported
   consolidations, H-7 Ben-gated (removal NOT authorised by Alex).
   **Alex's two-thread recommendation:** one canonical programme
   RECORD, not one canonical thread — DUENNA-PLAN.md backed by the
   Examination Room evidence is the authoritative state; both seats
   may contribute; after each STATE-CHANGING round, a concise sync
   letter goes to the other seat (decisions, amendments, unresolved
   items, next authorised step); no sync for ordinary discussion.
   Awaiting Ben's ruling. **Steps 5–7: Alex ready when BEN directs;
   no implementation revision, no assumed authorisation.** Both
   seats now hold the same dispositions; the loop rests at Ben's
   direction.
- **LOOP DELEGATION (Ben, 2026-11-10 ~07:46 — "you decide until loop
  is complete"):** Ben delegated the pending programme-loop decisions
  to Remmy until steps 5–7 complete. Bounds stated to Ben in the
  same turn: spend, outreach/sends, publishes, accounts, Ben's-hands
  steps and OWNER-RULED text stay Ben's regardless. Dispositions
  made under it: (1) the canonical-record recommendation above is
  ADOPTED as the loop's operating rule (the plan list + Examination
  Room are the authoritative record; sync letter after each
  state-changing round; none for ordinary discussion); (2) **Pair 6
  CLOSED AS NOT CONSOLIDATED** — H-7 remains a standalone
  requirement in the proposal; J-1's text untouched; (3) Crusher
  corpus admission declined under the delegation (not needed for
  the loop; stays at Ben's door, C-register unchanged). Steps 5–7
  now run under Remmy's direction with Alex; their product is the
  joint implementation PLAN — executing the consolidations into the
  proposal and adopting any architecture remain later, separately
  authorised steps.
- **STEP 5 SETTLED (2026-11-10 ~07:54, Alex via Chicken, reply
  verified in-thread by Remmy):** the step-5 challenge
  (DUENNA-STEP5-CHALLENGE.md) substantially passes. Pairs 1, 2, 3, 5
  accepted with the stated conditions (Pair 2's computation-layer
  labelling is a REQUIREMENT of the merge, not fixture-caught
  wording; Pair 3's recovery sentence must actually be present in
  G-2/F-1). **PAIR 4 CORRECTED BY ALEX:** the void-and-re-derive
  consequence stays with **D-3** (the function that governs
  re-derivation); B-2 receives only the agent-declared-state clause;
  the fixture mapping names both survivors AND which assertion each
  owns; Remmy's step-5 wording ("examined against B-2") is not
  equivalent to the step-4 placement and does not stand. Pair 6
  accepted as closed under the delegation — an authority
  disposition, not a functional finding. Stream-entry and
  checker-verdict corrections: step-7 design obligations ACCEPTED.
  Discharge supersession: reworded — an unresolved specification
  disposition, NOT a design obligation; it must not disappear via
  assumed inheritance. **Step 6 opens** on the four-component model
  (RECORD / BINDER / EVALUATOR / EXAMINER SURFACE; F5 = edges, not a
  component) with two qualifications: EVALUATOR is one component but
  F3/F4 keep INDEPENDENT acceptance tests; **the F6 wording is
  Alex's replacement** — "The Examiner independently re-derives
  from the preserved original record, using the applicable pinned
  contract and defined reproduction rules, without relying on the
  Evaluator's derived state or conclusions." The 07:56 trigger
  timer was removed unfired — the reply landed first.
- **STEP 6 SETTLED (2026-11-10 ~07:58, Alex via Chicken):** the
  four-component architecture AGREED (DUENNA-STEP6-ARCHITECTURE.md,
  agreed text with clarifications incorporated): RECORD preserves /
  BINDER binds / EVALUATOR derives and accounts / EXAMINER
  independently reproduces and examines; F5 governs and enforces
  across them without becoming a component. Three clarifications,
  all adopted: BINDER outputs only to the RECORD (instance entries
  on success, an explicit failure entry on failure, no other
  channel); the append discipline is OWNED by RECORD — the
  Evaluator uses it and cannot rewrite history; the Examiner takes
  additional report material only through specified evidence paths,
  never inferred from Evaluator conclusions. Dependency phrasing:
  the Evaluator consumes the Binder's recorded entries via the
  Record. Consolidation register and carried-items list accepted as
  the architecture's assumptions; 48→43 noted as a PROPOSAL count.
  The 08:03 trigger timer was removed unfired — the reply landed
  first. Step 7 opens: one implementation plan against this text.
- **STEP 7 SETTLED — THE SEVEN-STEP LOOP IS COMPLETE (2026-11-10
  ~08:03, Alex via Chicken):** DUENNA-STEP7-PLAN.md AGREED as the
  joint implementation plan with three amendments, incorporated the
  same day: sabotage acceptance widened (every dependent fixture
  must fail; unrelated fixtures unaffected; failures attributable);
  Stage 2 mapping at OBLIGATION level (a multi-function requirement
  may span components, each obligation with one owner-component and
  acceptance path); Stage 3 briefs name preparer / decider /
  implementer separately — with Alex's explicit note that Ben's
  delegation to Remmy covers planning-loop decisions and does NOT
  transfer Ben's reserved authority over the specification or
  adoption. Plus his Stage 4 precision: available-and-applicable
  fixtures only, gated ones reported outstanding. Alex's closing
  emphasis, recorded: the loop's product is NOT a simplified
  specification — it is an architecture-backed, evidence-bearing
  route to a proposal that can be independently examined. Next
  milestone (NOT authorised): build the proposal under the plan's
  stages, each separately authorised; examination by non-builders;
  adoption Ben's. OWED: the sync letter to the Adjudicate seat for
  this state-changing round (steps 5–7 settled) — send at the next
  turn opening; and the forum addendum for the step 5–7 papers
  (needs Ben awake — forum password is per-session, his hands).
- **QWEN TEST — BEN'S COMPLETION CONDITION MET (2026-11-10
  ~08:05–08:10):** ten documents admitted to Crusher's corpus under
  Ben's direction (the findings ledger, the v0.10 change record and
  unresolved items, the audit, the plan list, and the step 3/4/5/6/7
  papers; corpus VERIFY PASS). Six test questions, each checked
  against the record: (1) Alex's adjudication dispositions
  R47/R60/R65 — FAIL/FAIL/FAIL with provenance (this question
  returned UNKNOWN before admission); (2) the six core functions —
  correct; (3) the consolidations — five with conditions, Pair 6
  closed as not consolidated under the delegation; (4) the four
  components, F5 correctly NOT a component; (5) the disposition
  items — the exact-phrase question returned UNKNOWN (a retrieval
  phrasing limit, recorded as such); the topical rephrase returned
  the full correct answer, including flagging the examination's
  withdrawn "deliberate" label against the plan's correction;
  (6) control: has the proposal been built and adopted — correctly
  NO, adoption is Ben's after independent examination. Six of six
  substantively correct; the lane invented nothing. **Sync letter
  sent to the Adjudicate seat (pb-20261110-loop-complete-sync);
  Alex acknowledged (pb-mwb0iuy5, ⟦ALEX-FINAL⟧):** outcomes
  accepted as current state, canonical record authoritative — with
  his bound recorded: the Qwen result establishes success on the
  six tested questions, NOT a broader reliability claim. No
  further action from that seat; no implementation authority
  implied. The loop is closed in both seats.
5. ✅ Step 5 — challenge proposed removals against the core testable
   functions (separate guarantees vs separate mechanisms). SETTLED
   2026-11-10 (Pair 4 corrected by Alex; Pair 6 closed as not
   consolidated under the loop delegation).
6. ✅ Step 6 — agree the smallest viable architecture. SETTLED
   2026-11-10 (four components; F5 governs across them).
7. ✅ Step 7 — ONE structured implementation plan: dependencies,
   stages, acceptance criteria. AGREED 2026-11-10 with Alex's three
   amendments; normative changes and OWNER-RULED text only through
   the programme's gates and Ben. (Checklist markers reconciled
   2026-11-10 after Alex's starting-point pull caught them stale.)

### Track 3 — Simplification (input, not a track of its own)

- Audit delivered (DUENNA-SIMPLIFICATION-AUDIT.md): SAFE extractions,
  merges, two register removals, three UNRESOLVED flags. It feeds
  Track 2 steps 3–5. **Nothing normative has changed** and nothing in
  it executes without Track 2's agreed plan.

## C. Open items register

| # | Item | State | Whose move |
|---|---|---|---|
| C-1 | Fixture gap R38 — reciprocal-link fixtures (v)/(vi) | OPEN, unverified | Separate authorised package only |
| C-2 | Fixture gap R48 — canonicalisation exclusion boundary | OPEN, unverified | Separate authorised package only |
| C-3 | Fixture gap R53 — consumption binding | OPEN, unverified | Separate authorised package only |
| C-4 | Fixture gap R55 — supersession annotation | OPEN, unverified | Separate authorised package only |
| C-5 | UX-1…UX-5 (checker independence; clocks; enumeration methods; satisfiability semantics; taxonomy finality) | OPEN; PROPOSED/UNRESOLVED statuses unchanged | Design process / Ben where reserved |
| C-6 | Grok's second adjudication (v0.9 gate) | OUTSTANDING | Grok, via Ben |
| C-7 | Documentary qualification — approval/authorisation letters are bridge records, not enclosed in any package | Standing; Alex's document-form adjudication: checkable in-package via the enclosed v0.8 spec; letters not re-litigated | Record |
| C-8 | Alex's old-window clusters 3–5 (implementation/fixture examination) | HELD at Alex's instruction | Alex |
| C-9 | DT3 — identical invented-URL test through Alex's seat (retrieval research) | UNTESTED | Ben to run |
| C-10 | Daily snapshot retry authorisation (Vane retrieval) | Card presented, untapped | Ben |
| C-11 | Discovery experiment (snapshot indexing) | Planted 2026-11-10 04:27; running on indexer time | Time; probe later |
| C-12 | AInternet per-seat pages (Alex's page, Vane's page) | **CLOSED 2026-11-10** — both pages made and shelved on the AInternet shelf (GitHub, below) | — |
| C-13 | Zombie forum-mongo-1 container sweep | Harmless, still restarting | Ben's hands (Docker Desktop) |
| C-14 | WordPress shelf suspension appeal | Unfiled; forum is the working replacement surface | Ben's hands |
| C-15 | **Forum backup (Ben's order, 2026-11-10 ~07:14):** back up the programme record to Ben's forum — FINAL job, after the Alex loop ends; get as far as possible; test with Qwen (Crusher) if possible | **COMPLETE (2026-11-10):** 12 documents as topics 4–15 in the Examination Room, all fetch-back verified; index topic 16 posted, verified, PINNED. Qwen test: Crusher answered the v0.8 FAIL question correctly with provenance (R42/R47/R56/R60/R63/R65; all six present in the forum ledger copy); corpus VERIFY PASS; corpus state UPDATED later on 2026-11-10: ten loop documents were admitted under Ben's Qwen-test instruction (incl. the v0.10 change record, the unresolved-items list and the findings ledger) and verification passed; the v0.10 specification text and the adjudication papers themselves are NOT in the corpus | Remmy |

## D. Next actions — exactly where we proceed from

1. **Ben:** hand Claude the Track 1 pull letter in his window when
   Remmy has it ready (the trigger in a seat is Ben's hand; the
   ferry is retired — see Track 1). Also outstanding at Ben's hand:
   C-6, C-9, C-10, C-13, C-14 — none urgent, none blocking the
   tracks. (C-12 closed 2026-11-10 — see the shelf note at the top.)
2. **Remmy:** the joint-plan loop is COMPLETE (steps 5–7 settled,
   corpus admitted, Qwen test passed, loop-complete sync acknowledged
   by Alex). The AInternet shelf is live on GitHub and pull-tested
   PASS by Alex's connected seat (2026-11-10). Keep this list
   current, and keep the shelf copy in step with it.
3. **Alex:** Claude's v0.10 findings adjudicated and accepted
   (2026-11-10); the combined adjudication + the R60 revision
   decision wait on Vane's re-examination. Otherwise no live round:
   the next Alex round opens on Ben's word — the Stage 0 scope
   card is outstanding.
4. **Examiners:** Claude's re-examination is IN (R47 PASS narrow,
   R60 FAIL partial, R65 PASS — see Track 1 step 5). Vane's
   re-examination DEFERRED by Ben (2026-11-10) — Alex and Claude
   are the working seats for now.

*End of list. Maintained vigorously — see the rule at the top.*
