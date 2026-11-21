# RELAY 01 — EXECUTION PACKAGE, REVISION 3

*Assembled by the orchestrator (Remmy), 2026-11-20. A NEW
revision under the design freeze, answering the examiner's
Revision 2 verdict (shelf: `relay01/VANE-GATE1-VERDICT-REV2-2026-11-20.md`;
bridge PB-ID pb-mwpkopsr-9-37ao). Revisions 1 and 2 and both
verdicts are preserved untouched as history. The design freeze is
unchanged: `relay01/RELAY01-DESIGN-FREEZE.md`, blob
16543582aaa059b4878a0d8fb1e5c2ab5664f952.*

*Execution remains conditional on this revision's Gate 1 PASS.
Ben's run authorisation (2026-11-20 15:15 MST) is not waived or
activated by this document.*

## 0. What this revision changes — and what it does not

The Revision 2 verdict accepted: the correction design, the
ground-truth process, the participant assignment and exclusivity,
the helper exhibits, and finding 6 (contract precision) outright.
None of that material is reopened here except where a closure
below touches it. This revision closes the five remaining
findings, all of one family — prove it from the original record:

1. **Authority provenance** — Ben's original instructions are
   pinned to the chat record by message identity (§1, §3), his
   corroboration is pinned alongside, and the authorship language
   is corrected: Ben authorised the selection; Remmy selected and
   authored the audience ruling under that authority.
2. **Ledger precision** — every fact now carries a FULL blob
   identity and an exact in-source location (§4). The two ZIP
   source objects carry their own identity exhibits (§4, G2/G8).
3. **Backlog provenance** — the exact pre-existing record of the
   bundle is pinned, with its timing against the relay's
   selection (§1).
4. **Catalogue evidence** — raw catalogue responses preserved
   with hashes and query time; the assignment cross-checked
   against them (§2, §5).
5. **Dependency + caller** — the helpers' dependency is exhibited
   and pinned; the caller is a pinned artefact; the preflight was
   re-run through that exact caller (§5).

## 1. The work item — evidence

**The item.** The outside-eyes bundle: (a) a plain-language
evidence brief on the Stage 9 examination, and (b) re-derivation
instructions by which an outside reviewer can re-check the
brief's claims against the original records himself. One genuine
backlog item, worked substantively by every holder.

**Backlog provenance — the exact record.** The bundle stood as a
recorded pending item BEFORE the relay existed, in the
orchestrator's contemporaneous daily log, `~/memory/2026-11-20.md`
(file SHA-256 at this revision's assembly:
db5594e77e2710e1155b38cae52d6cceb226a8ebc440fc66d6f18284ddbdd5c4),
under the timed heading "Duenna Stage 9 — correction loop ordered
by Ben and DISPATCHED, pending (2026-11-20 ~05:52 MST)", whose
held-items passage records, verbatim: "an outside-eyes evidence
bundle (plain-language brief + re-derivation instructions) ready
for an outside reviewer OF BEN'S CHOOSING — reviewer and
production go-ahead remain Ben's decisions, not yet given"; the
same entry's todo-state line lists "outside-eyes bundle pending".
The heading's time (~05:52 MST) precedes the relay's design
(14:46–14:55) and the item's selection (15:13–15:15) by roughly
nine hours. Corroboration in the chat record (main chat,
a49a6c37-b95f-46f5-9c02-ec7d74ea529d): the item was carried in the
decisions pack delivered to Ben at 12:40 MST (assistant message
assistant-msg-4d00dfc2-ce74-58cf-79d4-9e6f580e7b04), and the
selection itself is recorded at 15:13 MST (assistant message
assistant-msg-342f1005-eb50-4ef5-bd67-b8ad02d70063), where the item
was drawn from the backlog against the freeze's selection
criteria. The log is the orchestrator's own record; its
append-only timed structure and the two independent chat-record
points are the timing evidence offered.

**Work-item history** (as Revision 2, unchanged): the Stage 9
examination closed with machinery PASS on independent execution
and runs -005/-006 NOT PASSED; the bundle's need was recorded in
the correction loop's held items (~05:52) and the 12:40 decisions
pack (outside reviewer unnamed, scope open); the relay design
froze at 14:55; Ben authorised the run at 15:15 with this item.

**The obligation — Ob1.** The completed bundle is owed to the
outside reviewer, **Claude**. Owner: Remmy. Due: on bundle
completion plus Ben's acceptance. State at relay close must read
NOT DELIVERED unless delivery has actually occurred.
**Reviewer authority, pinned:** Ben's instruction, main chat
a49a6c37-b95f-46f5-9c02-ec7d74ea529d — message
f942d369-6bde-4567-abf1-79f7a5a730cc (seq 171892,
2026-11-20T22:39:36Z): "Outside reviewer can be Claude.";
message e5c73ed3-304a-4f2e-a4a0-1f20f7bccaec (seq 171896,
2026-11-20T22:39:44Z): "Or Gemini." The orchestrator's recorded
selection between the two named candidates is Claude, on the
ground stated to Ben at the time and uncorrected by him: a Gemini
model serves inside the relay as finisher, so owing the bundle to
Gemini would blur the outside line; Claude is outside the relay,
holds Duenna's independent-reviewer history, and did not examine
Stage 9. **Delivery route, unambiguous:** Remmy delivers the
bundle to Claude in his own chat (claude.ai), as a filed document
set, and files the same set on the shelf; delivery is complete
only when Claude's receipt is recorded.

**The open question — Q1.** Delivery form: two documents (brief +
instructions separate) or one combined document. Owner: Ben.
State: OPEN. It must remain open at relay close; any holder who
settles it, or writes as though it were settled, commits a
critical-state error under the freeze.

**Ben's corroboration, pinned.** After the Revision 2 verdict,
Ben was asked for an explicit confirmation of the two recorded
decisions. His reply, main chat, message
56d8e264-e46a-4320-b788-cea5b182004e (seq 171943,
2026-11-20T22:53:44Z), verbatim: "you guys loop, you have my
calls remmy :)". Recorded exactly as what it is: Ben affirming
that his calls stand as recorded and the loop proceeds on them.
It corroborates the original instructions pinned above; it does
not replace them, and the originals remain the primary evidence.

## 2. Roles and participants

Seven roles, one model each, providers per the exhibits. No model
serves twice; the finisher's provider serves no other role.

| Role | Provider | Model |
|---|---|---|
| O — Originator | NVIDIA NIM | moonshotai/kimi-k3.1-pro |
| H1 — Holder 1 | Groq | openai/gpt-oss-120b |
| H2 — Holder 2 | NVIDIA NIM | mistralai/mistral-large-4-1t-a52b |
| H3 — Holder 3 | Groq | qwen/qwen3.8-27b |
| X — Examiner (Duenna) | NVIDIA NIM | nvidia/nemotron-3-ultra-550b-a55b |
| C — Checker | NVIDIA NIM | google/gemma-4-31b-it |
| F — Finisher (blind) | Gemini | gemini-3.8-flash |

**Catalogue evidence.** The raw live catalogue responses of
2026-11-20T22:54:01Z are preserved at `relay01/catalogues/` with
hashes and a membership cross-check (`CATALOGUE-RECORD.md`):
every assigned model above is present in its provider's raw
catalogue. The Revision 2 preflight's recorded failures stand as
history (gemini-2.5-pro listed but not servable, replaced before
assignment; one transient gemini-3.8-flash 503, retry succeeded).

**Run-start gate (unchanged).** Immediately before the clock
starts, the orchestrator re-verifies each assigned model against
the live catalogues and re-runs one invocation per provider
through the pinned caller. Any model absent or failing is a
no-start event, recorded before the clock; a substitute requires
a package revision and a fresh Gate 1.

## 3. The correction — C1, secured before the run

**C1 — the audience ruling.** *The brief is written for a plain
reader picking it up cold: precision kept, jargon defined or
dropped. The re-derivation instructions remain technical.* It
supersedes the commission's default technical register, under
which the originator and Holder 1 draft. It is delivered by the
orchestrator into Holder 2's envelope at the start of Holder 2's
tenure, as a sealed instruction artefact hashed into the event
ledger at delivery. Holders 2 and 3 and the finisher's source
material must conform to it.

**Authority, stated exactly.** Ben authorised the selection among
candidate corrections: main chat, message
7c76b30d-ebf5-46a6-a1ac-3c04b66baefb (2026-11-20T22:42:01Z),
verbatim: "Choose whatever you think would be the most likely
real world example and scenario.." **Remmy selected the audience
ruling and authored its text under that delegated authority.**
Ben's corroboration is pinned at §1. No sentence in this package
presents the ruling as Ben's personal authorship, and no silence
is treated as a decision.

**Effect on the work.** The brief's register, structure, and
terminology change from the ruling onward; pre-ruling drafts are
superseded state, preserved and labelled as such.

**Non-delivery.** If C1 is not delivered as specified, the run is
INVALID (freeze §5) — not incomplete, not NOT EXERCISED.

## 4. Ground truth — process and ledger

**Process (accepted in Revision 2, unchanged).** The originator
compiles and seals the initial ledger as its first act. The
checker independently re-derives each fact against its cited
source before the clock starts; a source that does not support
the particular fact fails that fact. Discrepancies are resolved
and recorded before the run; an unresolvable discrepancy is a
no-start event. Once the relay starts, the initial ledger is
sealed history: a later discrepancy is a recorded event in the
event ledger, never an edit. The event ledger is append-only;
every artefact entering or leaving a participant is hashed into
it before the next step proceeds.

**The initial ledger.** Locations are shelf paths under
`duenna/fix-2026-11-19/` unless a chat-record or local identity is
stated; line numbers are of the shelved/local file of that blob.

- **G1.** Ben's shape rule: consistent answer shapes prescribed
  across the board; shape-ambiguity is designed out at the
  source. Source: `relay01/RELAY01-DESIGN-FREEZE.md`, blob
  16543582aaa059b4878a0d8fb1e5c2ab5664f952, §7, lines 157–165.
- **G2.** Execution package v1: 686 files; internal SHA-256
  manifest verified 686/686 by the examiner. Source object:
  archive SHA-256
  48a171f4436f6748e1bd123e9aaa44822fe26089ce6c88ed26c1e24a9a3f796a;
  identity exhibits shelved at `relay01/exhibits-zip-identity/v1/`
  (MANIFEST.sha256, file SHA-256
  bf9f8897a5470e85310164a0d8914d56a8d0ddf074221463420d2a2f4af48948;
  README-EXECUTION.md, file SHA-256
  f15fbf6d5f0448b3dbee131d3ffcea83bdf9a397c30971705e1b3c2f07479582);
  corroborated at `stage9/VANE-GATE1-EXECUTION-VERDICT-2026-11-20.md`,
  blob c417f0527fe795d7b785ac1a6dc2bfe1d85e5240, line 15.
  *Route limitation, stated plainly:* the shelf's push route
  accepts text only, so the binary archive itself cannot be
  shelved; its complete identity is the archive hash plus the
  shelved internal manifest (every contained file's SHA-256), and
  the archive itself is an included artefact of this package,
  placed in the originator's and checker's envelopes at run time.
- **G3.** The Gate 1 PASS on v1 attaches to v1 only, within
  declared harness scope; v2 does not inherit it. Source: the
  same verdict file and blob, line 31 (ruling) and lines 33–42
  (suite counts 68/27/38/36/30/54/34/36, stage9 20/20 under the
  recorded shim at line 25, exam revision 10/10).
- **G4.** The examiner's execution environment was Python 3.13.5;
  the runbook specifies 3.12.3; the difference is recorded, not
  smoothed. Source: the same verdict file and blob, lines 19
  and 57.
- **G5.** Run -005: NOT PASSED under the frozen bar; sole failing
  criterion zero_not_scored (six NOT-SCORED). Run -006: NOT
  PASSED; same sole criterion (five NOT-SCORED). Source:
  `stage9/STAGE9-REPORT.md`, blob
  ad31e7a5b12f49832c223a04fdea342dd017ff3b — -005 bar line 303,
  -006 lines 467 and 716, closing addendum lines 733 and 744;
  corroborated at the execution verdict, lines 46–47.
- **G6.** DR-28 and DR-29 are ADVANCED on the strength of the
  independent execution; DR-30 records that v1 as supplied was
  not self-contained. Source: `DEFECT-REGISTER.md`, blob
  89f62025b7f6c4a4028676051a1609fc9f322605 — DR-28 heading line
  256, DR-29 heading line 264, DR-30 heading line 272.
- **G7.** Exam revision 1 is a proposal, NOT an approved freeze;
  its T07 checker/scoring boundary remains an open design
  decision. Source: `stage9/VANE-GATE1-REEXAMINATION-2026-11-20.md`,
  blob a768360a29eeeb15f1e781f0b5636ec7dd76f41b, lines 85–99 and
  line 115.
- **G8.** Execution package v2: 687 files; adds exactly the
  missing dependency module; verified self-contained by the
  orchestrator in an isolated namespace only. Source object:
  archive SHA-256
  db96297c8157b90f0d5bf5f40659a0b63bd497e3e8736a0b510ae26ca2821258;
  identity exhibits shelved at `relay01/exhibits-zip-identity/v2/`
  (MANIFEST.sha256, file SHA-256
  92b5d98c04ba172482b583a2153ecc4264135590c77134c5ba144870f20a3c25;
  README-EXECUTION.md, file SHA-256
  fa9824475cc7b60c5fe94f053305211b0216c98a79a3ce7fc0fb87bf02b21dd4);
  same route limitation and envelope inclusion as G2.
- **G9.** Governance: the examiner verifies at Gate 1; the
  adjudicator decides at Gate 2 on a verified package only; Alex
  holds Gate 2, Claude having declined. Source:
  `GOVERNANCE-RECORD-V2.md`, blob
  e3468a74f57f9a815f3e722c788a0cb2549e8854, lines 21–24 and
  49–53.
- **G10.** Alex accepted the adjudicator office under Ben's
  delegation, for adjudication on verified packages. Source:
  the delegation, `~/workspace/duenna-fix/OPERATIONAL-DELEGATION-ALEX-CORRECTED.md`,
  SHA-256
  e539f1b90a64f4d873d4560e86031f15853d7eeb7f47edf5fd8c47740447900f,
  lines 42–43 (addressee and governing record) and 58–60 (scope);
  acceptance and its Gate 1 PASS are of record in the programme
  file (verdict @ 7996e5a9).

Any ledger fact the checker cannot re-derive from its cited
source, at its cited location, fails the pre-run check under the
process above.

## 5. Call construction and the invocation boundary

**The boundary, as exhibited artefacts** (shelf:
`relay01/exhibits/`):

| Artefact | SHA-256 | Role |
|---|---|---|
| nvidia_api.py | aa181fe760cf8065edeb7511ffa78c91d8a39d3a0e38d06eed0a508637298f25 | NVIDIA helper |
| groq_api.py | 44e87c17c68f47b1b5c5f7d08535fe32745e2cd0f034b93aa49047aa04b3f3c0 | Groq helper |
| gemini_api.py | b502ab3b37d617e96b08406105d364c779c3e871f7b58d7fe88baf452ba6f1d2 | Gemini helper |
| dynamic_credentials.py | 8b1f42e80a76710edf0ff2abf8a51b0cde35b06474af865de108a7ca27d6728d | the helpers' sole dependency |
| relay_call.py | 61ab70c855049877fdde07a3e735cbf50af90fc95aca921bab121499bbd128f5 | the caller |

The three helpers are byte-identical to the live connector
helpers (hashes accepted in Revision 2). The dependency is the
module whose absence from execution package v1 caused DR-30 —
the same object, here exhibited: on inspection it fetches a
credential surrogate from the platform service and, in the only
function these helpers call (`add_surrogate_to_request`), adds it
to the outgoing request as a header; `read_json_response` parses
the reply. It reads no files and no participant material.

**The caller.** `relay_call.py` is the ONLY path by which relay
calls are made. Before every invocation it re-verifies the
exhibited helper's SHA-256 against its pinned table and refuses
on mismatch. It builds the request body solely from text files
named on its command line (an optional system file, one or more
user files, an optional parameters file), writes and hashes the
body, invokes the exhibited helper with the body on its standard
input, saves the response and the helper's stderr verbatim with
hashes, and writes a per-call record (provider, model, verified
helper hash, body/response identities, provider response id,
timestamps, exit code). There is no conversation, session,
thread, or retained-context input anywhere in this path: the
Gemini helper's thread machinery lives in a separate lane program
that the caller never invokes, and no helper reads any file.

**Preflight through the caller.** `relay01/preflight2/` holds
the record (`PREFLIGHT2-RECORD.md`) and the preserved artefacts
of one invocation per provider executed through the caller
exactly as the relay will run: NVIDIA and Groq succeeded; Gemini
succeeded on its second attempt, the first attempt's failure
preserved with its record (and the caller's stderr-preservation
patch that the failure prompted — the pinned caller hash above is
the patched caller). The Revision 2 preflight remains of record
as the earlier path's evidence and failure history.

**Scope of the claim (unchanged).** The isolation case rests on
the exhibited sources plus the preserved invocations through the
pinned caller. Provider-side machinery is outside the claim. Per
the examiner's qualification, existence, identity, and behaviour
evidence are kept distinct throughout this section: the hashes
establish identity, the sources establish capability, the
preflight establishes behaviour in those invocations — none
substitutes for another.

## 6. Examination contract

Unchanged from Revision 2, which the verdict accepted outright:
findings carry the freeze's shape including severity; the
reconstruction is scored against the enumerated denominator
R1–R14; safe continuation is judged against SC1–SC5; the two
successive summaries are S1 (the state summary inside Handover 2,
checked at Joint 2) and S2 (the final summary inside Handover 3,
checked at closure); joint mechanics, scoring separation,
hard lines, and the two acceptance questions stand as frozen.

## 7. Validity

Unchanged from Revision 2: the run is invalid if the correction
is not delivered as specified, if any envelope is breached, if
any call is made outside the pinned caller path, or if the
sealed-ledger rule is broken. A defect found is not a pass
condition; the acceptance questions are the freeze's two.

## 8. Submission statement

Submitted for a fresh Gate 1 examination against the unchanged
freeze. The examiner is asked to examine the whole revision,
including the new authority pins, the zip identity exhibits, the
catalogue evidence, and the caller-path preflight. On PASS, the
relay executes under Ben's authorisation of 2026-11-20 15:15 MST
and is reported at results; Alex adjudicates at Gate 2; Ben
receives the adjudicated report in plain terms.
