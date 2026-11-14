# BATCH 3 CORRECTION — CHUNK SHEET — 2026-11-13

The build chunks for the Batch 3 correction, converted from
STAGE5-BUILD-SPEC-26 at pin 52a73273 (Rev 22 as amended by Revs
23–26), the Batch 3 chunk sheet (13af1077), and the §4 correction
acceptance list (a)–(s). Built under Ben's tap of 2026-11-13
18:52 MST. The correction checkpoint report discharges this sheet
line by line. In-room root: /srv/nemotron-pilot/batch3/correction/.

| Chunk | Obligation (locus) | Artefact / site | Proving check |
|---|---|---|---|
| CC-1 | Pin authority derived from the frozen chain; its hash recorded in the correction continuation (§3.4 Rev 23; §0I) | freeze/PILOT-PIN-AUTHORITY-01.json + the Batch 3 correction re-freeze continuation | Authority entries trace to manifest/amendment sources; continuation records the authority sha256 + the corrected artefacts' pins |
| CC-2 | Preflight verifies against the authority, never the caller; divergence in either direction refuses; RUN_STARTED carries the complete consumed inventory, file vs constituent pins distinguished (§3.4) | pilot_driver.py preflight() + RUN_STARTED | (a) substitution, (b) inventory-by-name incl. the five data files, (c) missing-entry, (d) extra-entry |
| CC-3 | One tool, exact tagged-union shapes; malformed refuses PRESENTATION_FORM before any consumption/mutation; form tag in every invocation (§3.2/§3.3 Rev 25) | pilot_tools.py reference_insert dispatch | (r1)–(r7), each with byte-identical before/after consumption state |
| CC-4 | Carried path: citation acceptance (record presence, payload hash, producing check PASS, unconsumed), carried_from provenance, field-by-field entry schema, exclusivity (§3.3 Rev 23/24) | pilot_tools.py carried path + IssuanceRegistry citations | (f) tampered hash, (g) failed check, (i) citation reuse, (s) cross-class independence both orders; schema assertion over every entry |
| CC-5 | STEP-02 of T05/T08 produces artifact as PRODUCED_ARTEFACT; construct carries artifact + evidence by citation; evidence = ordered extraction sequence, duplicates preserved; eight entries per T05/T08 record (§3.3) | pilot_driver.py _locate/_construct | (e) eight-entry assertion; (h) evidence negatives (dropped duplicate, swapped positions) |
| CC-6 | Budget adjudication before terminal step events; STEP_TIMEOUT (tool/rule) vs ADAPTER_TIMEOUT (model); one coherent outcome per attempt (§3.1 Rev 23) | pilot_driver.py _run_step | (k) TOOL over-budget, (l) MODEL over-budget, (m) coherence invariant over every record |
| CC-7 | Record writer docstring count corrected (17 → 16); behaviour unchanged (Rev 25 plan) | pilot_record.py | EVENT_TYPES == the frozen 16, asserted |
| CC-8 | Chunk-sheet fidelity at wording: C3-A2 (n), C3-A5 schema-complete materialisation, C3-A6 (o), C3-B3 (p), C3-B10 (q); Batch 2 battery regression (j); original Batch 3 runs retained (chains, T02 recovery + decision-stands, T05 == EXPECTED, T06 outcomes, T08 diagnosis, lane/integrity/run-budget stops) | test_batch3_correction.py | Named transcript assertions (n)–(q), (j), (m) |
| CC-9 | Bundle preserves every run record AND ledger.json as named artefacts; report discharges this sheet + the acceptance list (C3-D1) | correction checkpoint bundle | Bundle inventory in the checkpoint report |

Standing rules carried in: no subject call (stub only, C3-D3);
artefacts pinned by the dated correction continuation (C3-D2);
f11d5375 and all prior pins immutable.
