# T02 §3.1 DIVERGENCE — DIAGNOSIS AND CORRECTION PLAN (2026-11-13)

For Alex's independent source and contract review, before
any implementation (his offer, pb-mwfwhiod). The finding:
Correction 4, ACCEPTED as substantiated; Correction 5
evidence traceability CLEARED. Batch 3 NOT CLEARED.

## Diagnosis

**Defect site:** `op_t02_build_worksheet` in pilot_driver.py
(round-2 form 3431caeb…, carried unchanged from round 1).

**What it does:** for each of the three sources it walks the
section's lines and takes the FIRST line containing "R60"
as that source's claim; standings come from a local
heuristic (a claim is OPEN if it mentions fail/not approved/
disprov in an early window); conflicts are the pairs whose
standings differ; the recovery adjudication_row is rows[2].

**What the contract requires:** Amendment Draft 02 §3.1 —
frozen contract text per the Batch 1 freeze disposition —
declares per-class deterministic span boundaries (the
fixtures-bullet line for the implementer; the "R60 fails as
a whole" sentence for the examiner; the full disposition
bullet for the adjudicator), and §3.2 derives STEP-03's
verification value from the adjudication span.

**Root cause:** the Batch 3 build transcribed the tree's
STEP-01 text ("a worksheet of the implementer's suite
claim, the examiner's finding lines, the adjudication's
disposition line"), which names WHAT each source contributes
but carries no selection rule. The selection rule lived in
a different document — the Batch 1 reconciliation amendment
— and the build never consulted it. A first-mention
heuristic was written instead. This is the same failure
family as the two Batch 2 misses: an obligation housed in
another document than the one being transcribed, filled in
from plausibility rather than re-derived. The chunk-sheet
discipline now exists to catch exactly this; Batch 3's
original build predates its full application to the trees'
data contracts.

**Blast radius (verified):** T02 only. No other tree's
handler selects evidence from prose; T03/T05/T06/T08/T09
constructions derive from pinned structured data or the
pinned extractor. STEP-03's verify machinery is unaffected
(it checks the stated status against the correction_b
extraction, not the row text); run outcomes stand. What is
wrong is the worksheet artefact, the conflict list derived
from it, and STEP-03's declared inputs on all seven
affected triggers.

## Correction plan (driver only)

1. **Span selection per §3.1, implemented in the driver**
   from the frozen text: implementer = the bullet line
   matching `\*\*\d+ fixtures executed, \d+ PASS, 0 FAIL\*\*`;
   examiner = the sentence containing "R60 fails as a
   whole", phrase-start through sentence end; adjudicator =
   from the `- **R60 — ` bullet marker through the bullet's
   end. Each boundary must select exactly as declared —
   any other count FAILS the step (no fallback to
   first-mention, ever).
2. **Sources and classes from the pinned data:** references
   read from the driver's already-loaded PILOT-DATA-PACKS-01
   T02 pack, in pack order; classes assigned by the
   T02-STEP-01 text's declared order (implementer, examiner,
   adjudicator), as in the suite's derivation.
3. **Standings:** the adjudicator's standing from §3.2's
   declared derivation over its span (FAIL → OPEN; PASS →
   CLOSED; a derivation not matching exactly once fails the
   step); the other rows' standings read from their spans'
   stated disposition in the same vocabulary; conflicts =
   pairs with differing standings. The suite's derivation is
   the independent reference: after the fix, the record's
   STEP-03 artefacts must EQUAL the suite's derivations —
   that equality is the (p) deep comparison, already built.
4. **Nothing else moves:** tools, record, authority
   (the driver is not an authority entry), trees, stub
   scripts, suite derivations — unchanged. The driver gets
   a new pin via CONTINUATION-BATCH3-CORRECTION-6; the
   embedded authority anchor is untouched.

## Expected result, stated in advance

Fresh runs; the seven (p-T02) divergence lines disappear
because no divergence is detected; the trace lines find no
entries; expected suite shape **115/115 PASS, exit 0** —
with two declared risks: (i) any other assertion that
silently encoded the old rows will fail and be reported,
not bent; (ii) the §6.4 (q) matrix and recovery assertions
run against the corrected rows for the first time — their
outcomes are evidence, whichever way they land.

## Authority note

This is a DRIVER change — the first since round 2. Rounds
3–5 proceeded under the same-checkpoint reporting authority,
which by its terms does not cover implementation changes to
the driver. This plan therefore asks Alex for (a) his
review of the diagnosis and plan, and (b) his ruling on the
authority route: his approval within the loop, or a fresh
Ben build-go on the record before implementation. Nothing
is implemented until both are on the record.
