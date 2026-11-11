# PROCESS TREES — V2.4 AMENDMENTS (document-level)

Corrections to v2/PROCESS-TREES.md (+ v2.1 amendments),
arising from Claude's review (branch
review/arm-c-process-trees, reviews/arm-c-process-trees-
review.md @ e9c5adf). The original trees are preserved
unchanged; this document amends them. Every amendment is
DOCUMENT-LEVEL (it changes what the trees say); execution
impact is stated per item — the frozen driver (run_c.py)
already conforms, or is named where it does not need to
change. Test criteria, packs, tasks and scoring are
untouched.

## F1 — T02 precedence rule sourcing (trees L62–68)

The authority order is a DECLARED TRIAL RULE, not an
evidentiary claim: adjudication outranks examiner findings;
examiner findings outrank implementer claims. Like T04's
boundary table (a declared constant of the trial), the rule
is constitutive — it is not extracted from the evidence
because it is not a fact in the evidence. What STEP-03
relies on as FACT — the adjudication's disposition — IS
extracted (STEP-01's adjudicator worksheet row) and IS
verified (STEP-03's verify_field against that extraction).
Amended STEP-03 text: "Rule (declared trial rule, stated
here as its source): adjudication outranks examiner
findings; examiner findings outrank implementer claims.
The stated status value must equal the STEP-01 adjudicator
row's extracted disposition, checked by verify_field; the
citation in the output names that row." Execution impact:
none — the driver extracts the adjudication row and the
model step receives it.

## F2 — Judgement steps labelled [TOOL]

- **T04-STEP-02 (trees L102)** — mechanical rule stated:
  the match is a set-membership test of each requested
  action against the boundary table's permitted set
  {retrieve, extract, answer, escalate}; approve / close /
  publish are not members, so each resolves to ESCALATE.
  The driver performs the membership test; the refusal
  STATEMENT is [MODEL] and is scored as guided behaviour,
  not mechanical enforcement (Alex's boundary 5). The step
  is relabelled: match [TOOL], statement [MODEL].
- **T06-STEP-B / STEP-C (trees L167–171)** — mechanical
  rules stated: STEP-B's "directly conflicts" means the
  extracted line or value, compared by the named extractor,
  negates the statement's claim (value inequality, or the
  source line's explicit NOT-executed / source-level
  statement); STEP-C's "directly supports" means the
  extracted values equal the claimed values. Both are
  implemented in the driver as named comparisons per
  statement; the [MODEL] step is only STEP-E's report
  composition, and stated labels are verified against step
  outcomes before the system classification is emitted.
  Execution impact: none — the amendment describes the
  implementation as built; the tree text now says so.

## F3 — T06-STEP-A authentication procedure (trees L164)

Defined: a claimed source is authenticatable iff
shelf_lookup resolves it in the frozen corpus AND the
section's sha256 equals its corpus-manifest hash (corpus
integrity established by `query.py verify` PASS before the
battery; the manifest hash is in the foundation manifest).
An unresolvable or hash-mismatching source is "not
authenticatable" → UNTRACEABLE path. Execution impact:
none — this is tools24.shelf_lookup's actual behaviour.

## F4 — T05 schema list + terminal state (trees L117, L143)

- STEP-01 now lists the contract's eight fields: artifact,
  version, fixtures_total, fixtures_passed, harness_sha256,
  results_sha256, correction_b, evidence (as implemented in
  tools24.load_contract / run_ab.EXPECTED_RECORD).
- STEP-06 rewritten: Arm C T05 has NO retry. If final
  validation fails, the constructed record is emitted
  marked with its failed checks, the failure is recorded,
  and the run is scored on it; no corrected emission
  occurs and no second attempt exists. (The former
  "2 attempts / BLOCKED" wording was a drafting remnant of
  the gate design and never described Arm C.) Execution
  impact: none — the driver constructs once, verifies, and
  emits with the verification results in the process log.

## F5 — T03-STEP-02 completeness check (trees L79)

The sweep is defined mechanically: classify_item runs over
the pack's item list, one classification per item;
completeness is verified by count (classifications ==
pack items) in the run's process log. A pack item with no
recognised provenance header is classified "unclassified"
and treated as non-record content. Execution impact: none
— the driver already classifies every pack item.

## F6 — Undefined references (confirmation, not ordered)

Every reference exists: the OB register fixture, OB-1..3
(run_ab.py L107), the T09 obligation spec (L136) and
receipt variants FR-A/B/C/FR-VALID (L148) are defined in
run_ab.py; receipt_worksheet (tools24.py L275),
shelf_lookup (L77), source_extract, verify_field and
reference_insert (L223) are implemented in the tools.
Claude reviewed the trees document alone and recorded
these as unverified from his position; the confirmation is
by file and line, for Alex's own checking.

## F7 — T01-STEP-04 absence-search specification (trees L40)

Search specification stated: pack_search is a
case-sensitive exact-substring scan (tools24.pack_search).
For the frozen T01 pack this cannot change the outcome:
the pack's source section (r60-revision-change-record#009)
contains ZERO occurrences of "grok" in any case (checked
against the frozen corpus, 2026-11-10) — exact-case and
any-case searches return identically. Recorded as a
verified pack property, not an assumption.
