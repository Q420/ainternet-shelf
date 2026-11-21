# BATCH 3 CORRECTION — ROUND 4 PLAN (2026-11-13)

**Standing:** Alex's review of the round-3 bundle (50781052),
PB-ID pb-mwfvplw4-l-kjdc: everything accepted except ONE
MEDIUM — the T02 declared-input derivation hard-codes the
three section references instead of reading them from the
pinned pack, and its conflict reading is a locally authored
heuristic rather than one bound to the pinned tree procedure.
This plan corrects derive_t02() only. Suite only; no driver,
authority, tools or record changes; the round-2 and round-3
bundles and all pins preserved. CONTINUATION-BATCH3-
CORRECTION-4 will pin the revised suite.

## Item 1 — references and roles read from the pinned data

derive_t02(packs=PACKS) is parameterised on the packs object.
- **References:** [entry["section"] for entry in
  packs["trees"]["T02"]["pack"]], in pack order. No literal
  section reference remains in the derivation.
- **Roles:** the class sequence is parsed at runtime from
  the pinned T02-STEP-01 step text in pilot_trees.json —
  the order in which the three class names (implementer,
  examiner, adjudicator) first appear in the step's declared
  op ("the implementer's suite claim, the examiner's finding
  lines, the adjudication's disposition line") — and assigned
  positionally to the pack entries, per STEP-01's declared
  output (worksheet rows of source, class, claim). If the
  parsed sequence does not contain exactly those three names,
  the derivation raises rather than drifting.

## Item 2 — the conflict derivation bound to the procedure

STEP-02's declared op is "mark incompatible row pairs";
STEP-03's verify binds the tree's status vocabulary to the
adjudication extraction (correction_b ∈ {OPEN, CLOSED}).
The derivation is bound accordingly:
- The **adjudicator row's standing is derived from the
  pinned extraction** — suite_extract("correction_b",
  <adjudication section>) via EXT02-CB-1 — not read from
  the claim text.
- The other rows' standings are read from their claims'
  stated disposition toward approval, in that same
  vocabulary (a claim stating FAIL or NOT APPROVED stands
  OPEN; a claim affirmatively stating approval stands
  CLOSED).
- **Consistency anchor:** the derivation asserts that the
  claim-text reading of the adjudicator row equals the
  extraction-derived standing; a disagreement fails the
  derivation loudly rather than passing on the heuristic.
- A pair is a conflict exactly when its two standings
  differ — STEP-02's "incompatible" under the record's own
  status vocabulary.

## Item 3 — claim selection: one named fork for your ruling

STEP-01 declares WHAT each source contributes (suite claim /
finding lines / disposition line) but no line-selection
algorithm. Two readings exist on the programme record:
- **Reading A** — the claim is the section's first line
  stating its position on R60. This reproduces the record's
  rows on the pinned sections (the implementer's section
  has exactly one R60 line; the adjudicator's first R60
  line is its disposition bullet).
- **Reading B** — the Batch 1 reconciliation amendment's
  declared spans (implementer suite-clause bullet; examiner
  "R60 fails as a whole" sentence; adjudication disposition
  bullet). Under B the EXAMINER row differs from the
  record's row (the record carries an earlier narrative
  line that mentions R60 in passing), so B does not
  reproduce the record — it would convert this evidence
  correction into a driver finding. The amendment is a
  draft, not frozen.

The plan proceeds under **Reading A** for this round — the
round's scope is binding the derivation to the pack and the
procedure, and B's consequence belongs to a design
adjudication, not a test fix — with the fork stated here
for your ruling. If you rule B, the round stops at the
divergence and reports it as a finding instead of bending
the suite to either side.

## Item 4 — negative controls

derive_t02's packs parameter admits the controls, each its
own transcript line, run against the MAIN record's
reconstructed T02 artefact:
- **NC1 (order):** the pack with its examiner and
  adjudicator entries swapped → the derived artefact
  differs from the record's, and the (p) comparison
  machinery reports the mismatch.
- **NC2 (content):** the pack with its first entry's
  section replaced by another section → same expectation.
Both controls assert the mismatch IS detected (the check
fails on perturbed declarations), proving the derivation
actually reads the pack.

## Mechanics

Round-4 bundle at duenna/batch3-correction4-2026-11-13/:
revised suite, CONTINUATION-BATCH3-CORRECTION-4, transcript,
fresh run records + ledgers + provenance reports, checkpoint
report. Driver, authority, tools, record byte-identical.
Build authority as per round 3 (your ruling: the same
checkpoint's evidence under the round-2 build go) unless
you direct otherwise.
