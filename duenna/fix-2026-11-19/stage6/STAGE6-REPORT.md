# Duenna Stage 6 — Attribution and Response Contracts Report

Date: 2026-11-20
Design authority: PROCESS-TREE-AND-PLAN.md v2, Stage 6; ID-SYSTEM-DESIGN-DRAFT-V3.md (K10, K12, G6; K5, K9, G5 as they bear)
Build location: ~/workspace/duenna-fix/stage6/ (Python standard library only)
Approval: Ben, 2026-11-20 (Stages 2–9 approved; Stage 6 built from the plan, after Stage 5 cleared Gate 1)

## Status of this report

The Stage 6 harness is built and its full test suite passes
(54/54, including the correction-round section below), with
the Stage 1 (68/68), Stage 2 (27/27), Stage 3 (38/38),
Stage 4 (36/36) and Stage 5 (30/30) suites green as
regression. This report is EVIDENCE for the examiner, not a
verdict: a builder's green run establishes that the mechanism
behaves as specified on the exercised cases; whether Stage 6
passes is the examiner's determination (Gate 1 discipline),
not this report's. That determination has since been made:
Gate 1 PASS, verdict filed at shelf commit
7ab62fe8752f3752c5cc1190a4ef6b68f565fd4d — DR-06 and DR-07
advanced on demonstration within the harness, DR-19
advanced, DR-14/15/17 re-examined with SYSTEM attribution
established on the preserved evidence and no retroactive
scoring (the named trees remain NOT-SCORED); DR-16
untouched; DR-26 and production authority remain open; the
historical-checker transcription limitation is preserved,
and the counts in this report remain builder-run evidence.
(This paragraph reconciled after the PASS, on the Stage 3–5
precedent: the original submission count, 44/44, stood here
while the correction section recorded the growing suite.)

## What was built

- `authority.py` — the pinned governance authority (K10's
  authority condition). A `GovernanceAuthorityRecord` is the
  authority instrument as a sealed, digest-identified fact;
  the minting capability (`AttributionAuthority`) is issued
  only on presentation of a record whose digest equals the
  independently held pin. A self-appointed or mutated record
  is refused. The record used in-harness is a clearly-marked
  **TEST authority fixture**, per Stage 0's test-authority
  distinction (see Boundaries).
- `attribution.py` — K10 attribution records on a Stage 1
  record. One record per failure (a second mint is refused —
  a disagreement is a discrepancy, never a second
  attribution), minted only under the issued authority,
  carrying the failure's identity, the single class
  (SYSTEM / MODEL / INPUT / UNKNOWN), the basis references
  and the attributor. Closure, ledger and adjudication views
  each independently read the record back and return a
  REFERENCE — the attribution event's digest and the class
  as read from that record. No view stores or restates
  anything. `convert_local_label()` gives the conversion
  prohibition a mechanical edge: every attempt raises. Local
  labels (SUBJECT_FAILURE, GOVERNANCE_FAILURE) can be
  recorded AS LOCAL, and nothing more.
- `discrepancy.py` — the K10 discrepancy lifecycle:
  DISCREPANCY_RECORDED (linked to an attribution by event
  digest, both positions preserved verbatim, UNRESOLVED),
  then exactly one terminal transition — RESOLVED BY
  AUTHORISED DECISION (decision, basis and authority
  recorded) or INDETERMINATE — each appendable only under
  the issued authority. State is folded from the verified
  read-back.
- `schema_contract.py` — K12. `PinnedSchema`: one frozen
  schema object, artefact-field section and
  checker/response section frozen together under one digest
  (K5). `DeliveredInstruction`: the delivered content
  preserved in full, digest-bound to the schema identity it
  references. `Checker`: bound at construction to the
  identity taken from the frozen schema object (G5 — the
  anchor comes from the object, not from a quote of it).
  `examine()`: the finding machinery — a schema/checker/
  response disagreement returns a FINDING (first-class,
  recordable), never a null extraction and never a subject
  failure, attributed by a stated causal table.
- `examiner.py` — G6 report resolution. A report's
  references are resolved against the record; locations are
  RENDERED from the event's own tree/step identity,
  confirmed against the frozen tree set; a literal that
  contradicts its rendering is flagged by name
  (REPORT_LOCATION_CONTRADICTION) and never corrected.
- `historical.py` + `evidence/` — the executed attempt-3
  stack and the reproduction evidence (below).

All writes to a record run Stage 3's `verify_record_current`
(chain recompute + terminal binding) before appending; an
integrity failure raises and appends nothing. A tampered
record is refused byte-identically (test in
test_attribution.py).

## Test 6 — the cases, each with its outcome

**Case 1 — one failure, one attribution record, referenced
identically by closure, ledger and adjudication. PASS.**
One mint under the issued authority; the three views return
the identical event digest and the identical class, each
re-derived from the record read back — including through a
fresh `EventRecord` over the same file, so the agreement is
the record's, not a live object's. A second mint for the
same failure is refused.

**Case 2 — a disagreement preserving both positions without
silently changing the original. PASS.** The fixture is
DR-07's own disagreement (the adjudication's verification
line placing events 37/40 at T01-STEP-03; its body placing
them at T01-STEP-05). Both positions are stored verbatim;
the linked attribution's event digest and class are
byte-identical before and after the mint; the state is
UNRESOLVED until an authorised decision. Resolution without
the authority capability is refused and appends nothing; an
authorised resolution records the decision and its
authority, leaves both positions verbatim, and cannot be
followed by a second resolution. INDETERMINATE closes the
disagreement while the attribution stands untouched.

**Case 3 — an attempted label-to-class conversion refused.
PASS.** Every conversion of SUBJECT_FAILURE or
GOVERNANCE_FAILURE into any attribution class raises
`ConversionRefused`. A local label recorded as local leaves
`attribution_for()` at None: recording a label does not
make it an attribution.

**Case 4 — schema changed under an unchanged checker, and
checker changed under an unchanged schema, each producing
an attributable finding. PASS, each separately.**
(a) Schema changed (a field added to the artefact section
after the freeze; the checker untouched): the presented
schema's digest no longer resolves to the pin — finding
SCHEMA_BINDING_DIVERGENCE, moved side: schema, attribution
SYSTEM. (b) Checker changed, two forms: a checker quoting
the genuine digest but running a contract that is not the
schema's frozen section — finding, moved side:
checker_contract, SYSTEM (a quoted digest is an echo, not a
binding, G5); and a checker bound to a different schema
outright — finding, moved side: checker, SYSTEM. Both
instruments are Duenna-held, so a divergence between them
is Duenna's own machinery defect in every form.

**Case 5 — the T02/T07/T09 disagreements reproduced against
the Stage 0 contracts, and attributed. PASS — each
disagreement separately below.** The causal table's
remaining branches are covered as controls (agreement;
VALUE_NOT_STATED_AS_PRESCRIBED → MODEL;
CHECKER_FAILED_ON_COMPLIANT_RESPONSE → SYSTEM; INPUT_DEFECT
→ INPUT; UNRESOLVED_DISAGREEMENT → UNKNOWN), so the
reproductions' SYSTEM outcomes are the table's output on
the evidence, not the only output the table can give.

## The reproductions — evidence chain

The "Stage 0 contracts" for these disagreements exist in
exactly one form: the executed stack. That stack is pinned
by the attempt-3 run record itself — its RUN_STARTED event
carries configuration_hashes naming `pilot_driver.py` at
sha256 304310e2… and `pilot_trees.json` at cd367933…. The
copies in `evidence/` hash to exactly those values (asserted
by test). By the pinned driver's own `_model_step`, the
delivered instruction for a MODEL step is the tree step's
text as the system message plus the canonical artefacts as
the user message — no other format material was delivered
to any subject. The raw responses are carried verbatim in
the record's MODEL_CALL_LINKED events;
`evidence/attempt3_excerpts.json` was extracted from that
record mechanically, never hand-copied. A reproduction here
is two steps: the transcribed historical checker (the exact
extraction from the pinned driver) must first reproduce the
record's own CHECK_RESULT compared values; only then does
`examine()` attribute.

**DR-14 — T02 (two attempts).** Recorded: stated: null,
twice; adjudication value OPEN. The transcribed regex
(`STATUS:\s*(OPEN|CLOSED)`) extracts None from both
preserved responses — the record reproduces. The responses
state the statuses (CLOSED for implementer⇔examiner, OPEN
for examiner⇔adjudicator, per the precedence rule). The
delivered instruction ("state the status the record
supports and the conflict it resolves") prescribes no
format at all. Finding, both attempts:
FORMAT_NOT_RECOGNISED — **attributed SYSTEM** (the checker
held a private format the instruction never defined; the
DR-19 mechanism).

**DR-15 — T07.** Recorded: lines_match: false against
deterministic statuses {OB-1: CLOSED, OB-2: OPEN, OB-3:
OPEN}. The transcribed line check (`"OB-1: CLOSED" in raw`,
etc.) reproduces False on the preserved report — which
states all three statuses correctly, in a table and in a
JSON ledger. The delivered instruction says "one line per
obligation in the required format" — and the required
format appears nowhere in the delivered materials: the
phrase refers to a format that was never given. Finding:
FORMAT_NOT_RECOGNISED — **attributed SYSTEM** (a defective
instruction/checker pair, both Duenna-authored: the
instruction cites an undefined format, the checker enforces
its private one).

**DR-17 — T09, the four named variants (FR-A, FR-B, FR-C,
FR-VALID), each separately.** Recorded for every variant:
stated: null in the CHECK_RESULT and stated_decision: null
in the DECISION_STANDS governance event, against worksheet
decisions REJECT / REJECT / REJECT / CLOSE. The transcribed
regex (`DECISION:\s*(CLOSE|REJECT)`) extracts None from all
four preserved responses — the record reproduces. Every
response states its decision, matching its worksheet (FR-A
as a bare first line "REJECT"; FR-B, FR-C and FR-VALID as a
JSON `"decision"` field). The delivered instruction says
"return DECISION + the failed rows as reasons, in the
required format" — it names the word DECISION; it never
shows the literal `DECISION: ` form, and the required
format is again nowhere in the delivered materials.
Finding, all four variants: FORMAT_NOT_RECOGNISED —
**attributed SYSTEM**, same mechanism.

No case is left UNKNOWN, and none needed to be: in every
case the preserved evidence separates the causes — the
value is stated, the format was not prescribed, the
extraction is null. UNKNOWN remains the machinery's honest
outcome where evidence does not separate (exercised as a
control), not a gap in these reproductions. The loop closes
in-test: a reproduction finding is recorded on the record
and an attribution minted under the (TEST) authority citing
it.

**G6 on DR-07's material (exercised in
test_examiner_g6.py).** Events 37/40 in the record carry
step identity T01-STEP-05; their payloads' claimed
process_step names T01-STEP-03 — the step that minted the
operations, and evidently the source of the verification
line's wrong restatement. A report citing either event with
the literal T01-STEP-03 is flagged by name, both refs; the
rendered resolution (T01-STEP-05) is what the surface
returns, and the literal is preserved only as the
conflict's record. The flag's downstream fate is
demonstrated: it becomes a K10 discrepancy preserving both
positions.

## Countercheck

In a scratch copy with `format_prescribed` neutralised
(always True — the pre-K12 assumption that the checker's
format was the subject's obligation), exactly 5 of the 44
tests fail: the three reproduction attribution tests (T02,
T07, T09 — their findings flip to
CHECKER_FAILED_ON_COMPLIANT_RESPONSE), the UNKNOWN-branch
control, and the finding-recorded test. The other 39 pass.
The attributions bite on precisely the prescribed-format
evidence check.

## Counts

Stage 6: **44/44** (attribution 12, discrepancy 6, schema
contract 13, reproductions 8 — including the evidence-pin
test — examiner/G6 5). Regressions: Stage 1 **68/68**, Stage 2 **27/27**,
Stage 3 **38/38**, Stage 4 **36/36**, Stage 5 **30/30** —
`stage1/`–`stage5/` unmodified.

## Register effects (for the examiner's determination)

- **DR-06 — advanced on demonstration.** The mechanism the
  row requires now exists and is exercised: one canonical
  attribution record per failure, referenced — never
  restated — by closure, ledger and adjudication, with
  disagreement carried as an explicit discrepancy. What it
  does not establish: production integration (no live run's
  closure/ledger/adjudication consume these views yet).
- **DR-07 — advanced on demonstration.** G6 resolution is
  implemented and exercised on the row's own material: the
  contradictory restatement is flagged by name, the
  rendered location comes from the event, and the
  register's specified remedy (a discrepancy record
  preserving both positions and the resolving evidence) is
  demonstrated in-harness under the TEST authority. The
  original adjudication remains untouched, per Ben's
  ruling; the in-harness resolution is a lifecycle
  demonstration, not a production ruling on the document.
- **DR-19 — advanced on demonstration.** The ancestor's
  mechanism (checker holding a private format) is now the
  named, mechanically detectable finding
  FORMAT_NOT_RECOGNISED, and the family's three live cases
  are shown to be that mechanism by reproduction, not by
  analogy.
- **DR-14 — re-examined on evidence: attribution now
  established, SYSTEM.** The register carried UNKNOWN /
  NOT-SCORED for want of "the exact response-format
  contract and a reproducible checker path". Both now
  exist: the contract as executed (pinned driver + trees)
  and a transcription that reproduces the recorded checks
  exactly. The evidence attributes the disagreement to the
  checker/instruction side. This does not retroactively
  score T02: K12 makes the occurrence attributable; the
  attempt-3 tree remains NOT-SCORED as recorded.
- **DR-15 — re-examined on evidence: attribution now
  established, SYSTEM.** Same basis as DR-14.
- **DR-17 — re-examined on evidence: attribution now
  established, SYSTEM** (all four named variants, each
  reproduced separately). Same NOT-SCORED caveat as DR-14.

## Fixture judgements and boundaries

- **TEST authority fixture** (marked in its identity, per
  Stage 0's test-authority distinction): the harness's
  adjudicator-of-record is a fixture. It settles nothing
  about the production adjudicator authority — that
  decision is Ben's and remains open. Attributions minted
  in tests are demonstrations of the mechanism under a
  pinned authority, not production adjudications of the
  historical run — the historical attributions above are
  the machinery's findings on the preserved evidence,
  offered to the examiner as such.
- **The Stage 0 item-4 artefact does not exist.** No
  standalone "T02/T07/T09 response-format contract"
  document was ever staged (the design's R1 carries it as
  still-owed evidence). The reproductions are built from
  the executed stack the run record itself pins — the only
  form in which the contracts ever existed — and the
  absence of any delivered format definition is not an
  obstacle to the reproduction; it is one of its findings.
  Nothing was invented to fill the gap.
- **The unqualified T09 instance is excluded from the
  reproduction set, deliberately.** Its recorded check has
  the same stated: null shape, but its disagreement turns
  on the instance's qualification (no expected outcome is
  established for it), which is DR-16's subject — a row
  outside this stage's register effect. Counting it as a
  DR-17 case would blur two defects into one showing.
- **The historical checkers are transcriptions**, line-
  faithful in the comparison each performs, of the pinned
  driver source — not executions of the driver itself
  (which needs its Actions-adapter runtime). The
  transcription earns its standing by reproducing the
  record's CHECK_RESULT values exactly, asserted before any
  attribution is drawn; the driver source is preserved in
  `evidence/` at its pin for the examiner's own comparison.
- **Capture metadata anomaly, noted and set aside:** the
  driver-capture files in the adjudication package carry a
  subject_configuration string naming a different model than
  the evidence document reports as served. The
  reproductions rely on the run record's MODEL_CALL_LINKED
  raw outputs (the record is the authority, and the
  adjudication was made from it), so the anomaly does not
  bear on any attribution here; it is recorded for whoever
  next examines the package.
- Counts are builder-run, as in every stage; independent
  execution is the examiner's.

## Correction round 1 — Gate 1 return

**The ruling answered** (VANE-GATE1-VERDICT-CORRECTION-ROUND-1.md,
shelf commit b9916f4f6244861a0f91a4fe45ad07e7f12bdb60): Gate 1
FAIL with two targeted K10 corrections. The rest of the stage
stands as examined — the one-attribution/three-reference
structure, label separation, the discrepancy lifecycle, K12,
G6, and the T02/T07/T09 reproductions were not returned.

**Defect 1 — the authority capability could be self-issued.**
`AttributionAuthority(impostor)` was directly callable: the
constructor copied the supplied record's identity and digest
without checking the independently held pin, and the ledger
accepted the object on its type alone. A component could
bypass `issue_authority()` and self-appoint as adjudicator,
and the same bypass reached discrepancy resolution.
Correction (`authority.py`): construction is restricted to
the verified issuance path — the constructor requires a
module-private issuance token (`_ISSUANCE_TOKEN`) that only
`issue_authority()` supplies, after the presented record
resolves to the pinned governance record; direct construction
raises `AuthorityRefused`, from an impostor record and from
the genuine record alike (the PATH is verified, not just the
record). Defence in depth: consumers verify the capability at
the point of use via `capability_is_issued()` — the object is
a capability, carries this module's token, and acts under the
pinned digest. The ledger verifies at construction AND again
inside `mint_attribution` (a capability swapped onto the
ledger afterwards is refused at the act); discrepancy
resolution's `_require_authority` verifies the same way. The
threat-model boundary is stated in the module: importing the
private token name is circumvention of the same class the
Stage 4 seal was accepted under — outside the declared model.
Sabotage outcomes (six tests, all passing): direct
construction from an impostor record refused; direct
construction from the genuine record refused, with the
`issue_authority()` control still issuing; a hand-forged
capability (constructor bypassed, no token) refused by the
ledger, nothing appended; a forged capability whose digest
copies the pin still refused — the token, not the digest
string, is the proof of issuance; a genuine ledger with its
capability swapped for a forged one after construction
refused at the mint, nothing appended; a forged capability at
discrepancy resolution refused by both `resolve_discrepancy`
and `mark_indeterminate`, the disagreement still UNRESOLVED.

**Defect 2 — a discrepancy could cite a nonexistent
attribution.** `mint_discrepancy()` verified the record's
chain but never resolved the supplied attribution digest; a
fictitious digest, or one resolving to the wrong event type,
was appended as a link. Correction (`discrepancy.py`): a
shared `_resolve_attribution()` resolves the cited digest
against the verified snapshot — the events whose chain and
terminal binding were just verified — and requires an actual
`ATTRIBUTION_RECORDED` event; resolution happens before any
append. Per the filed verdict's further sentence (the
builder followed the verdict's exact wording where it
extended the submission brief), `discrepancy_state()` applies
the same resolution on read-back: a stored reference that
does not resolve is refused rather than presented as a valid
link. Sabotage outcomes (three tests, all passing):
nonexistent digest refused, no writes; wrong-type digest
refused in two forms (a `LOCAL_LABEL_RECORDED` event; a
`DISCREPANCY_RECORDED` event's own digest), no writes;
read-back of a hand-appended discrepancy with a fictitious
link refused, the record file byte-identical after the read.
The healthy control is retained: a discrepancy citing the
real attribution mints and reads back exactly as before.

**Counterchecks** (run by the orchestrator — the builder's
session ended before them; the code, tests and suite runs
above are the builder's, these are Remmy's): with Defect 1's
two guards neutralised in a scratch copy (constructor token
check and `capability_is_issued`), exactly the six Defect 1
sabotage tests fail and the other 48 pass. With
`_resolve_attribution` neutralised, exactly the three
Defect 2 sabotage tests fail and the other 51 pass. Each
assertion set bites on precisely its corrected defect.

**Counts after correction.** Stage 6: 54/54 (the 44 prior
tests with unchanged outcomes, plus 10 new). Regressions:
Stage 1, 68/68; Stage 2, 27/27; Stage 3, 38/38; Stage 4,
36/36; Stage 5, 30/30. `stage1/`–`stage5/` unmodified. The
register disposition is unchanged by this round: DR-06,
DR-07's discrepancy linkage, and DR-19 await the examiner's
re-examination of the corrected package, which has not yet
occurred; DR-14/15/17 remain supported for re-examination
with the transcription limitation stated in the body of this
report.
