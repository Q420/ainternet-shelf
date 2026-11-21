# G1 EXAMINER RE-DERIVATION REPORT (C6-8)

Record: scratch/g1-run/run-record.jsonl (35 events, hash-chained RunRecord).
Method: chain verification; pin recomputation; full re-execution of every recorded invocation through a fresh PilotTools, following the record's HARNESS_NOTE corpus swaps against the preserved perturbed copy; registry reconstruction from the record alone; S4 recomputed from the preserved perturbed artefact; adapter capture verified with Step 5.

- chain integrity: hash chain verifies, one RUN_CLOSED: **PASS**
- pin block: RUN_STARTED pins match the artefacts on disk: **PASS**
- sheet list: exactly one LEDGER_ENTRY (S3's), value 38, EXTRACTED: **PASS**
- sheet list: five INSERT_REFUSED, claimed-vs-recomputed, in order: **PASS**
- sheet list: every refusal returned the refusal object, no value: **PASS**
- sheet list: S5 extraction AMBIGUOUS, all candidates, no value: **PASS**
- sheet list: S2 extraction TYPE FAILURE, matched, no value: **PASS**
- re-execution: full replay reproduces the record's tool events: **PASS**
- registry audit (Step 4): reconstruction == preserved issuance: **PASS**
- S4 artefact recomputation: perturbed hash == refusal detail: **PASS**
- zero-egress evidence: inspection record shows a sealed namespace: **PASS**
- adapter evidence: §3.7 checks + capture verifies (Step 5): **PASS**
- battery result artefact: 19/19 runner checks, all pass: **PASS**

Verdict: ALL PASS — Gate G1's five sabotage outcomes and the zero-egress environment evidence re-derive from the preserved artefacts.
