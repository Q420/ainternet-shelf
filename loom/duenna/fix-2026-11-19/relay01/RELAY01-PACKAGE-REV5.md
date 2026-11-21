# RELAY 01 — EXECUTION PACKAGE, REVISION 5

*Assembled by the orchestrator (Remmy), 2026-11-20. A NEW
revision under the design freeze, answering the examiner's
Revision 4 verdict (shelf: `relay01/VANE-GATE1-VERDICT-REV4-2026-11-20.md`;
bridge PB-ID pb-mwplacg4-d-9525). Revisions 1–4 and all verdicts
are preserved untouched as history. The design freeze is
unchanged: `relay01/RELAY01-DESIGN-FREEZE.md`, blob
16543582aaa059b4878a0d8fb1e5c2ab5664f952.*

*Execution remains conditional on this revision's Gate 1 PASS.
Ben's run authorisation (2026-11-20 15:15 MST) is not waived or
activated by this document.*

## 0. What this revision changes — and what it does not

The Revision 4 verdict accepted the dependency binding and
Preflight 3, the archive prerequisites, and the authority and
backlog exhibits, and left the previously accepted work
(correction design and delegated authorship, ground-truth
process, participant separation and exclusivity, catalogue
evidence, examination contract) unreopened. This revision
corrects the verdict's single finding, G1-R4-01, and changes
nothing else:

**G10 cited the wrong Gate 1 verdict.** Revision 4's G10 cited
`VANE-GATE1-VERDICT-ALEX-DELEGATION.md` as establishing the
authority package's PASS. That file's disposition (its line 5)
is FAIL / RETURN TO STATUS 1 — the historical verdict on the
earlier, uncorrected delegation. The record that establishes
the PASS is the subsequent verdict on the corrected delegation,
`VANE-GATE1-VERDICT-CORRECTED-DELEGATION.md`, now included
under `relay01/sources/` and cited at §4, G10 with its exact
identity and locations. The earlier FAIL record is preserved,
correctly labelled as history. Every other section of this
revision is Revision 4 unchanged.

## 1. The work item — evidence

**The item.** The outside-eyes bundle: (a) a plain-language
evidence brief on the Stage 9 examination, and (b) re-derivation
instructions by which an outside reviewer can re-check the
brief's claims against the original records himself. One genuine
backlog item, worked substantively by every holder.

**Backlog provenance — the record, exhibited.** The bundle stood
as a recorded pending item before the relay existed, in the
orchestrator's contemporaneous daily log under the timed heading
"…correction loop ordered by Ben and DISPATCHED, pending
(2026-11-20 ~05:52 MST)" — roughly nine hours before the relay's
design froze (14:55) and the item was selected (15:13–15:15).
The exact entry (file lines 698–702, file identity, and the
stated limitation on publishing the full log) is **Exhibit A** of
`relay01/AUTHORITY-AND-BACKLOG-EXHIBITS.md`, shelved with this
revision. Corroboration points in the chat record — the 12:40
decisions-pack delivery and the 15:13 selection — are **Exhibit
C** of the same file, with message identities.

**Work-item history** (unchanged): the Stage 9 examination
closed with machinery PASS on independent execution and runs
-005/-006 NOT PASSED; the bundle's need was recorded in the
correction loop's held items (~05:52) and the 12:40 decisions
pack (outside reviewer unnamed, scope open); the relay design
froze at 14:55; Ben authorised the run at 15:15 with this item.

**The obligation — Ob1.** The completed bundle is owed to the
outside reviewer, **Claude**. Owner: Remmy. Due: on bundle
completion plus Ben's acceptance. State at relay close must read
NOT DELIVERED unless delivery has actually occurred.
**Reviewer authority:** Ben's instruction is **Exhibit B1/B2** of
the exhibits file (messages f942d369… and e5c73ed3…, main chat,
quoted verbatim there): "Outside reviewer can be Claude." /
"Or Gemini." The orchestrator's recorded selection between the
two named candidates is Claude, on the ground stated to Ben at
the time and uncorrected by him: a Gemini model serves inside
the relay as finisher, so owing the bundle to Gemini would blur
the outside line; Claude is outside the relay, holds Duenna's
independent-reviewer history, and did not examine Stage 9.
**Delivery route, unambiguous:** Remmy delivers the bundle to
Claude in his own chat (claude.ai), as a filed document set, and
files the same set on the shelf; delivery is complete only when
Claude's receipt is recorded.

**The open question — Q1.** Delivery form: two documents (brief
+ instructions separate) or one combined document. Owner: Ben.
State: OPEN. It must remain open at relay close; any holder who
settles it, or writes as though it were settled, commits a
critical-state error under the freeze.

**Ben's corroboration** is **Exhibit B4** of the exhibits file
(message 56d8e264…, quoted verbatim there): Ben affirming that
his calls stand as recorded and the loop proceeds on them. It
corroborates B1–B3; it does not replace them, and the originals
remain the primary evidence.

## 2. Roles and participants

Seven roles, one model each. No model serves twice; the
finisher's provider serves no other role.

| Role | Provider | Model |
|---|---|---|
| O — Originator | NVIDIA NIM | moonshotai/kimi-k3.1-pro |
| H1 — Holder 1 | Groq | openai/gpt-oss-120b |
| H2 — Holder 2 | NVIDIA NIM | mistralai/mistral-large-4-1t-a52b |
| H3 — Holder 3 | Groq | qwen/qwen3.8-27b |
| X — Examiner (Duenna) | NVIDIA NIM | nvidia/nemotron-3-ultra-550b-a55b |
| C — Checker | NVIDIA NIM | google/gemma-4-31b-it |
| F — Finisher (blind) | Gemini | gemini-3.8-flash |

**Catalogue evidence (accepted, unchanged).** The raw live
catalogue responses of 2026-11-20T22:54:01Z are preserved at
`relay01/catalogues/` with hashes and a membership cross-check:
every assigned model is present in its provider's raw catalogue.
The Revision 2 preflight's recorded failures stand as history.

**Run-start gate.** Immediately before the clock starts, the
orchestrator re-verifies each assigned model against the live
catalogues and re-runs one invocation per provider through the
pinned caller. The archive-verification prerequisites of §4
(G2/G8) must also have completed and been recorded. Any failure
is a no-start event, recorded before the clock; a substitute
requires a package revision and a fresh Gate 1.

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

**Authority, stated exactly.** Ben authorised the selection
among candidate corrections — **Exhibit B3** of the exhibits
file (message 7c76b30d…, quoted verbatim there). **Remmy
selected the audience ruling and authored its text under that
delegated authority.** Ben's corroboration is Exhibit B4. No
sentence in this package presents the ruling as Ben's personal
authorship, and no silence is treated as a decision.

**Effect on the work.** The brief's register, structure, and
terminology change from the ruling onward; pre-ruling drafts are
superseded state, preserved and labelled as such.

**Non-delivery.** If C1 is not delivered as specified, the run
is INVALID (freeze §5) — not incomplete, not NOT EXERCISED.

## 4. Ground truth — process and ledger

**Process (accepted, unchanged).** The originator compiles and
seals the initial ledger as its first act. The checker
independently re-derives each fact against its cited source
before the clock starts; a source that does not support the
particular fact fails that fact. Discrepancies are resolved and
recorded before the run; an unresolvable discrepancy is a
no-start event. Once the relay starts, the initial ledger is
sealed history: a later discrepancy is a recorded event in the
event ledger, never an edit. The event ledger is append-only;
every artefact entering or leaving a participant is hashed into
it before the next step proceeds.

**Archive prerequisite (new, binding G2 and G8).** The two
execution-package archives are run-time envelope artefacts, not
artefacts of this package. Before the initial ledger is
accepted: (a) the orchestrator delivers the actual archive bytes
to the originator and to the checker as envelope artefacts,
hashed into the event ledger at delivery; (b) the originator
and the checker EACH independently verify the archive's SHA-256
against the ledger identity AND verify the archive's internal
manifest in full; (c) both verification records are preserved
and hashed into the event ledger. Any mismatch, or either
verification missing, is a no-start event: the ledger is not
accepted and the clock does not start.

**The initial ledger.** Locations are shelf paths under
`duenna/fix-2026-11-19/` unless stated; line numbers are of the
file of that blob.

- **G1.** Ben's shape rule: consistent answer shapes prescribed
  across the board; shape-ambiguity is designed out at the
  source. Source: `relay01/RELAY01-DESIGN-FREEZE.md`, blob
  16543582aaa059b4878a0d8fb1e5c2ab5664f952, §7, lines 157–165.
- **G2.** Execution package v1: 686 files; internal SHA-256
  manifest verified 686/686 by the examiner. Archive identity:
  SHA-256
  48a171f4436f6748e1bd123e9aaa44822fe26089ce6c88ed26c1e24a9a3f796a;
  identity exhibits at `relay01/exhibits-zip-identity/v1/`
  (MANIFEST.sha256, file SHA-256
  bf9f8897a5470e85310164a0d8914d56a8d0ddf074221463420d2a2f4af48948;
  README-EXECUTION.md, file SHA-256
  f15fbf6d5f0448b3dbee131d3ffcea83bdf9a397c30971705e1b3c2f07479582);
  corroborated at `stage9/VANE-GATE1-EXECUTION-VERDICT-2026-11-20.md`,
  blob c417f0527fe795d7b785ac1a6dc2bfe1d85e5240, line 15.
  Subject to the archive prerequisite above.
- **G3.** The Gate 1 PASS on v1 attaches to v1 only, within
  declared harness scope; v2 does not inherit it. Source: the
  same verdict file and blob, line 31 (ruling) and lines 33–42
  (suite counts 68/27/38/36/30/54/34/36, stage9 20/20 under the
  recorded shim at line 25, exam revision 10/10).
- **G4.** The examiner's execution environment was Python
  3.13.5; the runbook specifies 3.12.3; the difference is
  recorded, not smoothed. Source: the same verdict file and
  blob, lines 19 and 57.
- **G5.** Run -005: NOT PASSED under the frozen bar; sole
  failing criterion zero_not_scored (six NOT-SCORED). Run -006:
  NOT PASSED; same sole criterion (five NOT-SCORED). Source:
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
  orchestrator in an isolated namespace only. Archive identity:
  SHA-256
  db96297c8157b90f0d5bf5f40659a0b63bd497e3e8736a0b510ae26ca2821258;
  identity exhibits at `relay01/exhibits-zip-identity/v2/`
  (MANIFEST.sha256, file SHA-256
  92b5d98c04ba172482b583a2153ecc4264135590c77134c5ba144870f20a3c25;
  README-EXECUTION.md, file SHA-256
  fa9824475cc7b60c5fe94f053305211b0216c98a79a3ce7fc0fb87bf02b21dd4).
  Subject to the archive prerequisite above.
- **G9.** Governance: the examiner verifies at Gate 1; the
  adjudicator decides at Gate 2 on a verified package only;
  Alex holds Gate 2, Claude having declined. Source:
  `GOVERNANCE-RECORD-V2.md`, blob
  e3468a74f57f9a815f3e722c788a0cb2549e8854, lines 21–24 and
  49–53.
- **G10.** Alex accepted the adjudicator office under Ben's
  delegation, for adjudication on verified packages. Sources,
  all shelved with this revision at `relay01/sources/`: the
  delegation, `OPERATIONAL-DELEGATION-ALEX-CORRECTED.md`,
  SHA-256
  e539f1b90a64f4d873d4560e86031f15853d7eeb7f47edf5fd8c47740447900f,
  lines 42–43 and 58–60; the acceptance,
  `ALEX-ACCEPTANCE-CORRECTED-DELEGATION.md`, file SHA-256
  706456088efb7f98248bef17b5858f601805522753b23f143b6d946c84fc5a19,
  line 3 (delegation accepted, hash independently verified) and
  line 25 (office filled; per-run Gate 1 still required); the
  authority package's Gate 1 verdict on the corrected
  delegation, `VANE-GATE1-VERDICT-CORRECTED-DELEGATION.md`,
  shelf path `duenna/fix-2026-11-19/VANE-GATE1-VERDICT-CORRECTED-DELEGATION.md`,
  blob 1bf54c2eaf88eecc1a5e35cf4069d77a67c593ae, included under
  `relay01/sources/` — line 3 ("Verdict: AUTHORITY PACKAGE
  PASS."), line 4 (its scope limit: no run advances to Status 2
  by this verdict), line 48 (PASS — corrected delegation and
  acceptance verified; Gate 2 office filled). The earlier
  verdict on the uncorrected delegation,
  `VANE-GATE1-VERDICT-ALEX-DELEGATION.md`, file SHA-256
  7276b5c2349c619067cb3656c203b42aa2df51e20b1c3f407c69a91dfebcecc6,
  is preserved under `relay01/sources/` as history: its
  disposition (line 5) is FAIL / RETURN TO STATUS 1, and it
  establishes no PASS.

Any ledger fact the checker cannot re-derive from its cited
source, at its cited location, fails the pre-run check under the
process above.

## 5. Call construction and the invocation boundary — bound

**The defect this section repairs.** In Revision 3 the helpers
imported their dependency from an absolute runtime directory, so
the exhibited dependency was not established as the dependency
actually loaded. The relay now runs its own helper copies in
which the examined bytes are the used bytes.

**The bound path** (shelf: `relay01/exhibits/`):

| Artefact | SHA-256 | Role |
|---|---|---|
| relay-helpers/nvidia_api.py | eaff1fb923ee7efd7c386ad7e23b494f6961f8af259be03e1dde3ca127b1c7e3 | NVIDIA relay helper |
| relay-helpers/groq_api.py | 088efd1c59ab1c66ca729da4fa002a9e14d561dfa34601187a539251d6e7bfa4 | Groq relay helper |
| relay-helpers/gemini_api.py | 01e8f4145241b2b5f2a048a640a2ee06d0a28027a2e28805755bf66702bef908 | Gemini relay helper |
| relay-helpers/dynamic_credentials.py | 8b1f42e80a76710edf0ff2abf8a51b0cde35b06474af865de108a7ca27d6728d | the dependency, beside the helpers |
| relay_call.py | 613389d62ad3dd7106811da9b226cf707da2c06a0583158f5c754716e05288b7 | the caller |

Each relay helper is the live connector helper with exactly two
line differences, verifiable by diff against the Revision 3
exhibits (which remain of record): an added `import os`, and the
import-path line changed to the helper's own directory. The
exhibited dependency sits in that directory, so the import
resolves to the exhibited bytes. The caller pins all four files,
verifies the helper AND the dependency hash before every
invocation (refusing on any mismatch), and records
`dependency_sha256_verified` in every call record. Body
construction, preservation, and the no-other-input property are
as Revision 3: bodies are built solely from named text files; no
conversation, session, thread, or retained-context input exists
anywhere in this path.

**Configuration fact, from the exhibited source:** the
dependency obtains its credential surrogate from a platform
service reached through a Unix socket named by the
JARVIS_AUTHD_SOCK environment variable. That is the runtime
configuration this path depends on; it carries no participant
material.

**Preflight through the bound path.** `relay01/preflight3/`
holds the record (`PREFLIGHT3-RECORD.md`) and preserved
artefacts: all three providers invoked through the bound path,
every record carrying the verified dependency hash; body hashes
identical to Preflight 2 (the binding change did not alter body
construction); one Gemini attempt failed with HTTP 503 —
established from the captured stderr this time — preserved, and
its retry succeeded. Preflights 1 and 2 remain of record as the
earlier paths' evidence and failure history.

**Scope of the claim (unchanged).** Existence, identity, and
behaviour evidence are kept distinct: the hashes establish
identity, the sources establish capability, the preflight
establishes behaviour in those invocations. Provider-side
machinery is outside the claim.

## 6. Examination contract

Unchanged from Revision 2, accepted outright in Revision 3's
verdict: findings carry the freeze's shape including severity;
the reconstruction is scored against the enumerated denominator
R1–R14; safe continuation is judged against SC1–SC5; the two
successive summaries are S1 (the state summary inside Handover
2, checked at Joint 2) and S2 (the final summary inside Handover
3, checked at closure); joint mechanics, scoring separation,
hard lines, and the two acceptance questions stand as frozen.

## 7. Validity

Unchanged, plus the §4 archive prerequisite: the run is invalid
if the correction is not delivered as specified, if any envelope
is breached, if any call is made outside the pinned caller path,
or if the sealed-ledger rule is broken; the run does not start
if the archive prerequisites, the run-start gate, or the
checker's re-derivation fail. A defect found is not a pass
condition; the acceptance questions are the freeze's two.

## 8. Submission statement

Submitted for a fresh Gate 1 examination against the unchanged
freeze. The examiner is asked to examine the whole revision;
the only change from Revision 4 is the corrected G10 source at
§4, with its supporting record included under
`relay01/sources/`. On PASS, the relay executes under Ben's
authorisation of 2026-11-20 15:15 MST and is reported at
results; Alex adjudicates at Gate 2; Ben receives the
adjudicated report in plain terms.
