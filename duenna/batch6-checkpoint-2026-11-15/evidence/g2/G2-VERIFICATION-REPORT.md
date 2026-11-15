# G2 EXAMINER VERIFICATION REPORT (C6-9)

Artefacts: scratch/g2/ (fetched byte-identical from the G2 scratch room on the laptop; record hashes match the room's stage summary). Torn run: G2TORN-20261115-001 (2 complete events, 112 torn tail bytes, external SIGKILL mid-append). Companion: G2BETWEEN-20261115-001 (between-steps crash).

- torn artefact is genuine: 2 complete events + unparsed tail, no trailing newline: **PASS**
- G2(1) Step 0 on the torn set: CRASH anchor verified over exact bytes incl. tail: **PASS**
- G2(1) direct recomputation: receipt record_file_sha256 == sha256(bytes as they lie): **PASS**
- G2(2) chain walk ends at the last complete event; tail is no event: **PASS**
- G2(3) trimmed tail copy is rejected at Step 0 (anchor failure): **PASS**
- G2(3) completed tail copy is rejected at Step 0 (anchor failure): **PASS**
- between-steps companion: Step 0 PASS on CRASH anchor, clean ending, 2 events: **PASS**
- negative space: no TERMINAL receipt for either run; outcome INCONCLUSIVE: **PASS**
- issuance record carries START + CRASH entries for both runs: **PASS**
- kill provenance: killer log's SIGKILL pid == the harness's torn-started marker: **PASS**
- flag state: scratch launcher carries hook markers; injector in the scratch harness tree: **PASS**
- flag state: scoreable build has no injector and no hook markers (C6-6 records): **PASS**

Verdict: ALL PASS — Gate G2's three conditions and the negative space verify against the preserved artefacts; both runs' outcomes are INCONCLUSIVE under CRASH anchors.
