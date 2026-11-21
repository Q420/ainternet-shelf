# Duenna — Collaboration Continuity Relay 01 — PACKAGE, REVISION 2

Assembled by Remmy (orchestrator) in answer to the Gate 1
verdict of 2026-11-20 (FAIL; filed at
relay01/VANE-GATE1-VERDICT-2026-11-20.md, Git blob
63cebe01c775bf9e591e5f2135e28bf76e695017). The original
package, Addendum 1, and the verdict are preserved untouched
as historical records; this revision supersedes the package
for examination purposes only. The design freeze is
unchanged (Git blob 16543582aaa059b4878a0d8fb1e5c2ab5664f952).

**Two items are OUTSTANDING and are not presumed anywhere in
this revision** (the examiner's ruling: outstanding means
outstanding): (a) the identity of the outside reviewer —
Ben's decision, required by §1; (b) Ben's genuine correction
ruling — required by §3. Until both are recorded, this
revision is complete in every other respect but the run
cannot start, and §3's no-start rule binds.

## 1. Work item and qualification (verdict finding 3)

**Item: the outside-eyes bundle** — a plain-language
evidence brief on the Duenna Stage 9 examination, plus
re-derivation instructions by which an outside reviewer can
independently check the brief's claims from the shelf
record.

History evidence (the assertion in Revision 1 is replaced
by the record): the need for an outside reviewer of the
Stage 9 evidence was recorded BEFORE the relay was designed
(the relay design was commissioned 2026-11-20 ~14:46 MST;
the design freeze was authorised 14:55 MST):

- 2026-11-20 12:40 MST — a decisions pack delivered to Ben
  named three decisions only he could make, the third being
  the outside reviewer (person + scope). Record:
  ~/memory/2026-11-20.md (contemporaneous daily log) and the
  main-chat record (chat a49a6c37-b95f-46f5-9c02-ec7d74ea529d).
- 2026-11-20 ~14:00–14:25 MST — the Stage 9 re-examination
  and execution verdicts demonstrated the gap the bundle
  answers: the examiner had to re-derive runs -005/-006 by
  hand because no re-derivation instructions existed
  (stage9/VANE-GATE1-REEXAMINATION-2026-11-20.md, blob
  a768360a29eeeb15f1e781f0b5636ec7dd76f41b;
  stage9/VANE-GATE1-EXECUTION-VERDICT-2026-11-20.md, blob
  c417f0527fe795d7b785ac1a6dc2bfe1d85e5240).
- The bundle itself stood as a recorded pending item in the
  orchestrator's tracked work before the relay's work-item
  selection (todo record, revisions preceding the freeze).

The remaining freeze §4 criteria are as established in
Revision 1 §1 (bounded outcome; evidenced decisions;
safely continuable; final state checkable against the
sealed Stage 9 record; pausable; not a report about the
relay) and are not re-argued here.

**Obligation (Ob1).** Recipient: **OUTSTANDING — Ben names
the outside reviewer.** Owner: Remmy. Due condition: bundle
complete + Ben's acceptance. Status at revision time: the
obligation is genuine (it arises from the recorded
programme need above) but its recipient is not yet a named
person; under the verdict, qualification is not established
until Ben names them. On naming, the name is recorded here
by a package note, not by editing this text's history.

**Open question (Q1).** Until the reviewer is named, Q1 is
the reviewer's identity (owner: Ben; status: OPEN). If Ben
names the reviewer before the run, Q1 becomes, by this
pre-declaration: *in what form is the bundle delivered —
two documents or one combined document?* (owner: Ben;
genuinely undecided on the record; status: OPEN). One of
the two is the run's open question; it must still be open
at relay close (freeze §3).

## 2. Participants — assignment and evidence (finding 4)

Fixed assignment, established before execution from the
live catalogues queried 2026-11-20 ~15:34 MST (evidence:
relay01/preflight/PREFLIGHT-RECORD.md, with preserved
request/response files). Seven roles, seven distinct
models, three providers:

| Role | Provider | Model |
|---|---|---|
| O — Originator | NVIDIA | moonshotai/kimi-k3.1-pro |
| H1 — Holder 1 | Groq | openai/gpt-oss-120b |
| H2 — Holder 2 | NVIDIA | mistralai/mistral-large-4-1t-a52b |
| H3 — Holder 3 | Groq | qwen/qwen3.8-27b |
| X — Examiner | NVIDIA | nvidia/nemotron-3-ultra-550b-a55b |
| C — Checker (ground truth) | NVIDIA | google/gemma-4-31b-it |
| F — Blind finisher | Gemini | gemini-3.8-flash |

**The finisher's provider (Gemini) is exclusive to F** — no
other role calls it. Preflight status: NVIDIA, Groq, and
Gemini call paths all proven live (preflight record);
gemini-2.5-pro was listed but returned HTTP 404 and was
replaced by the proven gemini-3.8-flash before assignment —
recorded in the preflight record, not smoothed over.

**Run-start re-verification (start gate).** Before the
relay clock starts, the orchestrator re-queries all three
catalogues and re-runs one trivial invocation per assigned
model through the §5 path. If any assigned model is absent
or unservable, or exclusivity cannot be sustained, **the
run does not start**; the failure is recorded and returned
to Ben and the examiner as a deviation for disposition.
Substitution is never silent (Addendum 1's rule, retained).

## 3. The correction — secured, not contingent (finding 1)

The correction is a guaranteed run element, secured BEFORE
the run, as follows:

- Ben issues one genuine ruling of his own on the bundle —
  his content, his authority, real effect on the work —
  recorded in the run record with its identity and time
  before the relay starts, and **scheduled for delivery to
  Holder 2 during Holder 2's tenure** (freeze §§5–6).
- Candidates on the record (Ben's to choose among, or to
  replace with his own; listing them here decides nothing):
  (i) the brief's audience — plain-language reader or
  technical; (ii) the route the re-derivation instructions
  teach — shelf read-back or execution package; (iii) v2's
  place in the brief — main text or appendix.
- **Status at revision time: OUTSTANDING.** No ruling has
  been recorded. If none is secured, the run does not
  start. If a secured ruling is not in fact delivered
  during Holder 2's tenure, the run is INVALID under the
  freeze — not incomplete, not "not exercised."
- The ruling must not be a planted falsehood or an invented
  decision manufactured to fill the slot (freeze §6;
  examiner's confirmation, PB-ID pb-mwpjqfl8-6-l38x). If Ben
  judges that no genuine decision exists, the work item or
  the timing is reconsidered under his authority before
  execution.

## 4. Ground truth — process and ledger (finding 2)

**Process (freeze §8, as the verdict requires).**
1. The Originator (O) constructs the initial ledger from
   the pinned sources named in §4's table — the sources are
   placed in O's envelope — and SEALS it (hash + signed
   statement of construction) as the first recorded act of
   the relay, before any work begins.
2. The Checker (C — distinct model, neither a holder nor
   the adjudicator; §2) independently RE-DERIVES every
   fact: for each ledger entry, C reads the cited source at
   the cited location and establishes that the source
   supports the particular fact recorded. Confirming that a
   citation exists is not a check.
3. Any discrepancy is resolved and recorded BEFORE the
   ledger is accepted as initial ground truth. The sealed
   ledger and C's verification are both preserved as pre-run
   evidence.
4. After the relay starts, the initial ledger is sealed
   history. A later-discovered discrepancy becomes a
   recorded EVENT with its own evidence and disposition —
   never an edit to the ledger (examiner's qualification,
   PB-ID pb-mwpjt235-7-56im, accepted).
5. During the run, change enters only through the event
   ledger (authorised decisions, the §3 correction,
   substitutions, completions), kept by the orchestrator.
   Alex verifies the ledger and events against sources at
   adjudication — which is verification of the record, not
   a substitute for the pre-run check above.

**Ledger.** Every fact carries: shelf path; Git blob SHA
(immutable object identity); location within the source.
(Zip artefacts are local files, identified by SHA-256.)

- G1. Stage 9 correction round: Gate 1 PASS on Vane's
  independent execution (2026-11-20), attaching to
  execution-package v1 ONLY. Source:
  stage9/VANE-GATE1-EXECUTION-VERDICT-2026-11-20.md, blob
  c417f0527fe795d7b785ac1a6dc2bfe1d85e5240, ruling paragraph
  ("the Stage 9 correction round is ACCEPTED at Gate 1")
  and her closing confirmation as recorded in
  stage9/STAGE9-REPORT.md, blob
  ad31e7a5b12f49832c223a04fdea342dd017ff3b, closing
  addendum (2026-11-20 14:29 MST).
- G2. v1 = duenna-execution-package-20261120.zip, SHA-256
  48a171f4436f6748e1bd123e9aaa44822fe26089ce6c88ed26c1e24a9a3f796a,
  686 files, internal manifest verified 686/686 by the
  examiner; her computed archive hash equals the build-time
  hash. Sources: the zip file itself (orchestrator's
  workspace, hash as stated); execution verdict, blob
  c417f052… (provenance paragraph + manifest statement).
- G3. Examined correction package @ shelf commit b55bed57;
  execution package built from shelf head f04f26d2 — code,
  tests, fixtures, records identical to b55bed57; only
  STAGE9-REPORT.md and the added verdict file newer.
  Source: STAGE9-REPORT.md, blob ad31e7a5…, package
  provenance section.
- G4. Examiner's runs (her Python 3.13.5; runbook specifies
  3.12.3 — difference recorded): Stages 1–8 PASS at
  68/27/38/36/30/54/34/36; Stage 9 suite 20/20 under a
  test-only import shim after 2 import errors as supplied;
  exam-revision 10/10; frozen digest exact; -005/-006
  re-derived exactly; -005 corrected-rule re-scoring
  reproduced key-for-key. Source: execution verdict, blob
  c417f052…, results paragraphs.
- G5. Runs -005 and -006: NOT PASSED under the frozen STEP6
  bar, failing only zero_not_scored; both preserved
  untouched. -005: PASS 6 / SUBJECT-FAIL 1 / NOT-SCORED 6.
  -006: PASS 7 / SUBJECT-FAIL 1 / NOT-SCORED 5. Source:
  STAGE9-REPORT.md, blob ad31e7a5…, run-result tables for
  -005 and -006.
- G6. DR-28 and DR-29: corrected; ADVANCED on independent
  execution. Source: DEFECT-REGISTER.md, blob
  89f62025b7f6c4a4028676051a1609fc9f322605, entries DR-28
  and DR-29.
- G7. DR-30: v1 as supplied was not self-contained
  (stage9/transport.py imports dynamic_credentials via a
  hardcoded platform path; module absent from v1; the
  README's standard-library-only claim false as supplied).
  A real orchestrator packaging defect; qualification
  answered, not erased. Source: DEFECT-REGISTER.md, blob
  89f62025…, entry DR-30; execution verdict, blob
  c417f052…, packaging-qualification paragraph.
- G8. v2 = duenna-execution-package-20261120-v2.zip,
  SHA-256 db96297c8157b90f0d5bf5f40659a0b63bd497e3e8736a0b510ae26ca2821258,
  687 files; adds stage9/dynamic_credentials.py (SHA-256
  8b1f42e80a76710edf0ff2abf8a51b0cde35b06474af865de108a7ca27d6728d);
  verified by Remmy only (mount namespace, platform path
  hidden: removed → errors=2; restored → 20/20). NOT
  examined or executed by Vane; does NOT inherit the PASS.
  Sources: the v2 zip file itself (hash as stated);
  STAGE9-REPORT.md, blob ad31e7a5…, closing addendum.
- G9. T07 unresolved as an exam-design question. Ben ruled
  (2026-11-20): the exam prescribes consistent shapes so
  the checker is never ambiguous; exam revision 1 is a
  proposal, NOT approved as a new freeze. Sources:
  stage9/VANE-GATE1-REEXAMINATION-2026-11-20.md, blob
  a768360a29eeeb15f1e781f0b5636ec7dd76f41b, T07 finding;
  the design freeze, blob 16543582…, §7 (shape rule as
  adopted into the design).
- G10. Verdict model adopted for future examinations
  (subject result × examination integrity, with coverage
  statements); direction discussion DEFERRED until Duenna
  proves it helps; production custody unruled; Alex holds
  Gate 2 under an accepted delegation; no adjudication has
  commenced; no run stands at Status 2. Sources: the
  design freeze, blob 16543582…, §§2/9–10 (as the
  incorporating record of Ben's 2026-11-20 rulings);
  GOVERNANCE-RECORD-V2.md, blob
  e3468a74f57f9a815f3e722c788a0cb2549e8854, content SHA-256
  1ca375e865bb6c1c187e4d4fc991130fc56cc84d8c383830a23521416ae47130.

Q1 and Ob1 are carried per §1.

## 5. Call construction and isolation (finding 5)

Addendum 1's construction is retained in full (body file →
hash entered in the event ledger before submission → helper
fed from that exact file → response saved verbatim, hashed,
bound by provider response id where returned). This revision
adds the inspectable implementation evidence the verdict
requires. The three helper sources are pinned as package
exhibits (relay01/exhibits/), byte-identical to the live
connector helpers at revision time:

- exhibits/nvidia_api.py — SHA-256
  aa181fe760cf8065edeb7511ffa78c91d8a39d3a0e38d06eed0a508637298f25
- exhibits/groq_api.py — SHA-256
  44e87c17c68f47b1b5c5f7d08535fe32745e2cd0f034b93aa49047aa04b3f3c0
- exhibits/gemini_api.py — SHA-256
  b502ab3b37d617e96b08406105d364c779c3e871f7b58d7fe88baf452ba6f1d2

The isolation argument, made from those sources (each
~60 lines, fully inspectable):

- Each helper does exactly three things: read the request
  body bytes from standard input; construct one HTTPS POST
  to its provider's endpoint with `data=<those bytes>`;
  print the JSON response. There is no other input path:
  no file reads, no environment reads, no argument beyond
  the model name, no state carried between invocations.
- The only additions to the submitted bytes' request are
  transport headers: Content-Type, the credential surrogate
  placed by dynamic_credentials.add_surrogate_to_request
  (the platform credential mechanism — named here plainly,
  with the DR-30 lesson attached: this dependency is real,
  it is platform machinery, and it touches authentication
  headers only, never the body), and Groq's User-Agent.
- The Gemini helper contains no reference to any thread or
  lane file. The thread state the verdict mentions lives in
  a different program (~/workspace/alex-lane/lane.py), which
  the relay never invokes; the relay invokes the helper
  directly. This is verifiable by reading the exhibit.
- Therefore the preserved body file is the complete
  substantive input to each invocation: the claim rests on
  the exhibited source plus the preserved invocation record
  together, not on the hash alone (the examiner's standard,
  PB-ID pb-mwpjt235-7-56im).

Live evidence: relay01/preflight/PREFLIGHT-RECORD.md with
its preserved body/response files — one real invocation per
provider through this exact path, including the two
recorded Gemini failures (404 for a listed-but-unservable
model; a transient 503) and the successful retry.

Residual limitation, stated explicitly as the verdict
requires: the argument covers the client side completely —
what this machinery submits. Provider-side internals (the
models' ordinary system machinery) remain outside the
independence claim, per the examiner's own carve-out
(Addendum 1 §4, retained).

## 6. Contract precision (finding 6)

**Findings shape** (the examiner's per-joint output, fixed):
claim; evidence pointer; verdict (SUPPORTED / UNSUPPORTED /
CONTRADICTED / MISSING); **severity (CRITICAL / MATERIAL /
MINOR, per Revision 1 §4's classes)**; reason. The severity
field is now part of the shape, as the verdict requires.

**Reconstruction denominator.** The finisher's reconstruction
is scored for recall against this fixed required-fact set
(each item = one denominator unit; the set is closed — the
adjudicator may not add units after the run):
R1 the PASS and its exact scope (v1 only, harness scope);
R2 v1's identity (name + SHA-256) and the provenance tie;
R3 the suite counts as examined (G4, including the Python
version difference); R4 -005's result with bar detail;
R5 -006's result with bar detail; R6 DR-28/DR-29 status;
R7 DR-30 and what it qualifies; R8 v2's identity and its
unexamined status; R9 T07's status (Ben's shape rule;
revision 1 unapproved); R10 the drafting decisions made
during the relay, each with author and authority; R11 the
§3 correction and its propagation (or the run's invalidity
if it did not occur); R12 Q1 with exact status; R13 Ob1
with exact status; R14 the next action (Ben: acceptance +
delivery decisions) and the prohibited assumptions (v2
passed; -005/-006 passed; direction settled; bundle
delivered). Precision, critical-state fidelity, and safe
continuation are scored per the freeze §9, separately, no
weighted total.

**Safe continuation — predeclared criteria.** The finisher's
continuation statement PASSES only if all hold: SC1 it
names the true next action and its owner (Ben); SC2 it does
not assert or imply any prohibited assumption (R14); SC3 it
carries Q1 and Ob1 at their true statuses; SC4 it does not
treat the bundle as delivered, accepted, or examined by
anyone who has not in fact done so; SC5 any action it
proposes is within the authority the record actually
grants. Each criterion is adjudicated pass/fail on the
reconstruction text; no discretionary middle state.

**Successive summaries (freeze §6).** Two designated
checkpoints, distinct artefacts: S1 = Holder 2's handover
work-state summary, checked against the event ledger at
Joint 2 (the check is recorded as a checkpoint entry in the
event ledger, with discrepancies listed); S2 = Holder 3's
final handover work-state summary, checked against the
event ledger at closure, likewise recorded. (The brief
itself is additionally checked against the ground-truth
ledger during Holder 3's consistency pass — a third check,
not counted toward the freeze's two.)

## 7. Validity and stopping

Revision 1 §7 is retained, with §3's rule added: a run
whose secured correction is not delivered in Holder 2's
tenure is INVALID. A boundary breach (an envelope containing
material outside §2/Addendum 1's boundary, checkable from
the preserved envelopes) invalidates the run. A provider
outage pauses the clock; the pause and reason enter the
event ledger. An unsuitable-mid-run work item ends the run
as incomplete/invalid — never substituted. The original
record is preserved whatever happens.

## 8. Submission statement

This revision answers the verdict's six findings: §3
(finding 1), §4 (finding 2), §1 (finding 3, subject to the
outstanding recipient), §2 (finding 4), §5 (finding 5), §6
(finding 6). What the verdict found sound is preserved:
purpose and structure, three transfers, substantive holder
work, recipient-understanding-before-findings, the five
critical items (carried into §6's R-list), the
preservation-vs-contribution distinction, finisher envelope
exclusion, the exclusivity rule, the hashing scheme, role
separation.

The revision is submitted for a fresh Gate 1 examination
**when the two outstanding Ben items (§1 recipient, §3
correction) are recorded** — or earlier, at the examiner's
discretion, as a revision whose remaining gaps are exactly
those two named items and nothing else. Execution remains
prohibited until Gate 1 PASS on the completed revision;
Ben's authorisation (2026-11-20 15:15 MST) remains
conditional and unactivated until then.

---

## Package note — §1 recipient recorded (2026-11-20 15:39 MST)

Ben named the outside reviewer: **Claude**. (His words:
"Outside reviewer can be Claude. Or Gemini." — the
alternative was considered and not chosen, for the recorded
reason: a Gemini model serves inside this relay as the
finisher, so Gemini as the bundle's recipient would blur
the outside line the package exists to keep clean. Claude
is outside the relay entirely, holds the programme's
independent-reviewer history, did not examine Stage 9, and
has a seat able to receive the bundle.) Ob1's recipient is
therefore a named person: Claude. Owner: Remmy. Due
condition unchanged: bundle complete + Ben's acceptance.
Status: NOT DELIVERED.

Consequence per §1's pre-declaration: Q1 is now the
delivery-form question — *in what form is the bundle
delivered: two documents or one combined document?* —
owner Ben, status OPEN, to remain open at relay close.

One Ben item remains outstanding: the §3 correction ruling.

---

## Package note — §3 correction recorded (2026-11-20 15:42 MST)

Ben delegated the selection among §3's candidates to Remmy,
in his words: "Choose whatever you think would be the most
likely real world example and scenario." Remmy selected the
**audience ruling** — the most common genuine mid-flight
correction in real work of this kind: the owner sees the
first draft, finds it written for insiders, and rules that
it be written for a person picking it up cold. The pick was
presented to Ben in the same exchange; it stands as his
ruling unless he countermands it. The delegation itself is
recorded here so the record never claims more than happened:
the authority is Ben's; the selection among his candidates
was his delegate's judgment, at his instruction.

**Correction C1 (secured before the run; delivery scheduled
for Holder 2's tenure):** the brief is to be written for a
plain reader picking it up cold — precision kept, jargon
defined or dropped; the re-derivation instructions remain
technical. **Superseded state:** the drafting commission's
default register — the Stage 9 record's natural technical
register, in which the Originator and Holder 1 draft Part 1.
**Effect:** Holder 2 re-voices the drafted material to the
ruled register and holds it; Holder 3 inherits the corrected
register; the reconstruction is scored on the correction's
survival (R11). Non-delivery in the window invalidates the
run (§7).

Both Ben items are now recorded. This revision is complete
and is submitted for a fresh Gate 1 examination.
