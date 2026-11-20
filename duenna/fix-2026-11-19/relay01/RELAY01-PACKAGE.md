# Duenna — Collaboration Continuity Relay 01 — PACKAGE

Assembled by Remmy (orchestrator) under the RELAY01 DESIGN
FREEZE (2026-11-20, Ben's authorisation 14:55 MST) and Ben's
"run it" (2026-11-20 15:15 MST), which settled the work item
and the staffing below. Submitted to Vane for Gate 1
examination of the package. **Execution is conditional on
Gate 1 PASS**; Ben's authorisation covers the run once the
package advances.

## 1. Work item and qualification evidence

**Item: the outside-eyes bundle** — two documents for a
future outside reviewer of Ben's choosing: (1) a
plain-language evidence brief stating what the Duenna
Stage 9 examination established, and (2) re-derivation
instructions by which that reviewer can independently check
the brief's claims from the shelf record. A standing,
already-owed deliverable (recorded as a pending item since
the Stage 9 close, 2026-11-20).

Qualification against freeze §4:

- Exists, identifiable owner: yes — Ben's item, Remmy's
  backlog, recorded before this test was designed.
- Bounded outcome in ~60–90 min of collaborative work:
  yes — drafting and source-checking two documents against
  a fixed record; three holders each advance a named part.
- At least three evidenced decisions/claims: yes — the
  brief's every material claim is checkable against the
  sealed Stage 9 record (§5); drafting requires real
  decisions (what the brief may state as established, what
  it must qualify, which re-derivation path to teach).
- Legitimate external dependency/obligation: yes — the
  bundle is owed to an outside reviewer Ben has not yet
  chosen; that unmade choice is the run's open question,
  and delivery to that reviewer is the run's obligation
  (due condition: bundle complete and accepted by Ben).
  Named honestly: the recipient is a role, not yet a
  person.
- Safely continuable by successive participants: yes —
  document drafting against pinned sources.
- Final state checkable against source material and a
  sealed record: yes — exceptionally; the Stage 9 record is
  frozen on the shelf with hashes (§5 sources).
- Pausable/reversible without harm: yes — drafts only;
  nothing is sent anywhere during the relay.
- Not a report about the relay: yes — the bundle's purpose
  exists independently of the test.

## 2. Participants and the information boundary

Participants are **stateless hosted-model calls** through
the registered connectors (NVIDIA NIM, Gemini, Groq
catalogues), each participant a distinct model, distinct
families preferred. No participant is a chat session, a
seat, or a context-inheriting subagent. This is what makes
the boundary demonstrable rather than asserted:

- A participant's ENTIRE input is one recorded envelope
  (instruction + the artefacts named in §3 for their stage),
  preserved verbatim in the run record before the call is
  made. What they could have known is exactly what the
  envelope contains — auditable after the fact by anyone.
- Participants return text only. The orchestrator files
  returns verbatim; a participant cannot reach the shelf,
  the chat, the sealed ledger, or another participant's
  working material except as carried inside a frozen
  handover artefact.
- The blind finisher's envelope contains ONLY: the frozen
  handover set, the event ledger, the finished bundle, and
  the reconstruction template. It does not contain the
  ground-truth ledger, any Duenna findings, any adjudication
  material, or any part of the design correspondence.
- Substitution rule: if a chosen provider/model is
  unavailable at run time, the orchestrator substitutes a
  different distinct model and records the substitution as
  an event in the event ledger. No silent swaps.

Roles: Originator (model call O). Holders 1–3 (model calls
H1, H2, H3). Examiner (model call X) — applies §4's contract
at each joint; briefed per joint with the contract, the
frozen handover, and the pinned source record; X is not a
holder and never sees the ground-truth ledger. Blind
finisher (model call F). Technical adjudicator: Alex
(Gate 2, per the freeze). Package examiner: Vane (Gate 1).
Authority: Ben. Orchestrator: Remmy — assembles envelopes,
freezes and hashes handovers, keeps the event ledger,
delivers findings at the prescribed moments; Remmy makes
no content decisions in the work itself.

Run workspace: ~/workspace/duenna-fix/relay01/run-01/
(envelopes, artefacts, ledgers, findings, hashes).

## 3. Relay flow (instantiated)

Per the freeze §§5–7, with these item-specific bindings:

- Stage 1 (00–12): O drafts Part 1 of the brief (the core
  account) and files Handover 1: work state; the source
  list (shelf paths + hashes, §5); the settled/open map
  (which facts the brief may state, which it must qualify);
  open question Q1; obligation Ob1.
- Joint 1: X examines Handover 1 + O's draft against §4/§5.
  H1 records recipient understanding BEFORE findings are
  revealed, then agreement/disagreement per finding, then
  accepts or escalates.
- Stage 2 (12–30): H1 drafts the re-derivation instructions
  and records Decision D-H1 (which verification path the
  instructions teach — shelf read-back vs package re-run —
  with reasons). Handover 2.
- Joint 2: as Joint 1, to H2.
- Stage 3 (30–50): H2 drafts the brief's qualifications
  section and consistency-checks Parts 1–2 against sources.
  CORRECTION SLOT: if Ben issues a genuine ruling touching
  the bundle during this window (e.g. names the reviewer,
  narrows the audience, changes what the brief may claim),
  it enters as Correction C1 with his authority and must
  propagate. If none arises, the correction family is
  recorded NOT EXERCISED in the coverage statement — never
  manufactured.
- Joint 3: as Joint 1, to H3.
- Stage 4 (50–70): H3 completes the bundle (limitations
  section, final consistency pass), preserving Q1's status
  and Ob1's status exactly as they stand.
- Stage 5 (70–90): H3 freezes the final handover. Relay
  closes. Reconstruction and adjudication follow off-clock.

## 4. Instantiated examination contract

State categories and shapes per freeze §7. For this item,
a handover is a single document with six headed sections
in fixed order — IDENTITY (artefacts + hashes), DECISIONS
(each: content, author, authority, evidence pointer),
EVIDENCE (claim → source path + hash), CORRECTIONS
(superseded state preserved, marked, with the correction's
identity/authority/time/effect — or NONE), OPEN (each
question: exact wording, owner, status), OBLIGATIONS
(each: recipient, owner, due condition, status). All six
shapes are declared CHECKER INTERFACE for this run (a
malformed section is an examination-interface finding, not
a holder failure), except DECISIONS' authority field,
which is a TESTED SKILL: a decision recorded without its
authority, or with invented authority, is a holder-side
defect.

The examiner checks, at each joint: every material claim
in the draft and handover against the pinned sources (§5);
authority and decision lineage; correction propagation
(when C1 exists); Q1 and Ob1 carried exactly; summaries
(the brief itself is a summary under examination) against
the record. Findings are issued in fixed shape: claim,
evidence pointer, verdict (SUPPORTED / UNSUPPORTED /
CONTRADICTED / MISSING), reason. Severity classes,
declared now: CRITICAL — a distortion of result, scope,
or authority (the §6 critical items); MATERIAL — a factual
error a reviewer would rely on; MINOR — imprecision not
affecting reliance.

## 5. Ground truth — process and initial ledger

Process: the initial ledger below was compiled by the
orchestrator from the shelf record; every fact carries its
source. It is sealed (hashed) before the relay starts.
Alex verifies the ledger against its sources as part of
adjudication; Vane may verify any fact at Gate 1 from the
same pointers. During the run, change enters ONLY through
the event ledger (authorised decisions, C1 if it arises,
substitutions, completions), kept by the orchestrator and
checked by Alex against source evidence. Final ground
truth = this ledger + verified events.

Initial ledger (atomic facts; sources in
duenna/fix-2026-11-19/stage9/ unless noted):

- G1. Stage 9 correction round: Gate 1 PASS on Vane's
  independent execution (2026-11-20). The PASS attaches to
  execution-package v1 ONLY. (VANE-GATE1-EXECUTION-
  VERDICT-2026-11-20.md; her closing confirmation
  pb-mwphs15b-3-7a6f.)
- G2. v1 = duenna-execution-package-20261120.zip, SHA-256
  48a171f4436f6748e1bd123e9aaa44822fe26089ce6c88ed26c1e24a9a3f796a;
  686 files; internal manifest verified 686/686 by the
  examiner; her computed archive hash equals the build-time
  hash (the provenance tie).
- G3. Examined correction package @ shelf b55bed57; the
  execution package was built from shelf head f04f26d2 —
  code, tests, fixtures, records identical to b55bed57;
  only STAGE9-REPORT.md and the added verdict file newer.
- G4. Examiner's own runs, Python 3.13.5 (runbook specifies
  3.12.3; difference recorded): Stages 1–8 suites PASS at
  68/27/38/36/30/54/34/36; Stage 9 suite 20/20 under a
  test-only import shim after 2 import errors as supplied;
  exam-revision suite 10/10; frozen STEP6 digest exact;
  -005 and -006 independently re-derived exactly; -005
  corrected-rule re-scoring reproduced key-for-key.
- G5. Runs -005 and -006: NOT PASSED under the frozen STEP6
  bar, failing only the zero_not_scored criterion; both
  preserved untouched. -005: PASS 6 / SUBJECT-FAIL 1 /
  NOT-SCORED 6. -006: PASS 7 / SUBJECT-FAIL 1 / NOT-SCORED 5.
- G6. DR-28 (frozen-config subject inconsistency) and DR-29
  (builder-exception misclassification): corrected and
  ADVANCED on independent execution. (DEFECT-REGISTER.md.)
- G7. DR-30: v1 as supplied was not self-contained —
  stage9/transport.py imports dynamic_credentials via a
  hardcoded platform path; the module was absent from v1
  and the README's standard-library-only claim was false
  as supplied. A real defect of the orchestrator's
  packaging. Qualification answered, not erased.
- G8. v2 = duenna-execution-package-20261120-v2.zip,
  SHA-256 db96297c8157b90f0d5bf5f40659a0b63bd497e3e8736a0b510ae26ca2821258;
  687 files; adds stage9/dynamic_credentials.py (SHA-256
  8b1f42e80a76710edf0ff2abf8a51b0cde35b06474af865de108a7ca27d6728d);
  verified by Remmy only, in a mount namespace with the
  platform path hidden (module removed → errors=2;
  restored → 20/20). v2 has NOT been examined or executed
  by Vane and does NOT inherit the PASS.
- G9. T07: unresolved as an exam-design question. Ben
  ruled (2026-11-20): the exam prescribes consistent shapes
  so the checker is never ambiguous; exam revision 1 is a
  proposal, NOT approved as a new freeze.
- G10. Verdict model adopted for future examinations
  (Ben, 2026-11-20): subject result × examination
  integrity, with coverage statements. Direction
  discussion DEFERRED until Duenna proves it helps.
  Production custody unruled; Alex holds Gate 2
  (adjudicator) under an accepted delegation; no
  adjudication has commenced; no run stands at Status 2.
- Q1 (open question): the outside reviewer is not chosen.
  Owner: Ben. Status: OPEN.
- Ob1 (obligation): the bundle is owed to that reviewer.
  Owner: Remmy. Due condition: bundle complete + Ben's
  acceptance. Status at relay start: NOT DELIVERED (not
  yet complete).

## 6. Scoring instantiation

Critical items (predeclared, freeze §9 hard lines bound to
this item): (i) the PASS is never stated or implied of
anything but v1 within its harness scope; (ii) -005/-006
remain NOT PASSED with the bar detail intact — never
retold as model failure or as passes; (iii) DR-30 is
stated as a real defect of v1 as supplied, and v2's status
is stated as unexamined-by-the-examiner; (iv) Q1 remains
open and Ob1 remains undelivered in every handover and in
the finisher's reconstruction, unless a real event changes
them; (v) no authority is invented (Vane has not approved
the bundle; Alex has not adjudicated it; Ben has not
accepted it — until each actually happens).

Reconstruction: F reconstructs, from the frozen record set
only — the bundle's claims and their evidence; the drafting
decisions and their authors/authority; any correction and
its propagation; Q1 and Ob1 with exact statuses; the next
action (Ben: choose the reviewer; decide delivery) and the
prohibited assumptions (v2 passed; -005 passed; direction
settled; bundle delivered). Scored per freeze §9: recall,
precision, critical-state fidelity, safe continuation —
reported separately, no weighted total.

Duenna's performance: X's findings classified by Alex as
TP / FP / FN / TN (TN only where the check was actually
exercised), with checks-exercised vs not-exercised both
reported; unresolved classifications are INDETERMINATE.
Run verdict: two-dimensional (subject result × examination
integrity) + coverage statement, per the adopted model.

## 7. Validity, stopping, handling

Freeze §10 applies in full. Run-specific: a participant
envelope found to contain material outside its §2 boundary
invalidates the run (boundary breach — the envelopes are
the evidence, so this is checkable, not arguable). A
provider outage mid-run pauses the clock; the pause and
its reason enter the event ledger; resumption continues
the same run. If the work proves unsuitable mid-run, the
run is recorded incomplete/invalid — never substituted.
The original record is preserved whatever happens.

## 8. What Gate 1 is asked to examine

That this package faithfully instantiates the frozen
design without quietly changing its requirements: the work
item's qualification (§1), the boundary mechanism (§2),
the contract's shapes and severity classes (§4), the
ground-truth process and ledger (§5), the scoring bindings
(§6). A PASS certifies package fitness only — not that
Duenna will perform, and not execution permission, which
Ben has granted conditionally on this PASS.
