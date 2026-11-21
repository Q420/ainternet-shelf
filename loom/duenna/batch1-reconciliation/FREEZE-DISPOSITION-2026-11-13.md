# BATCH 1 FREEZE DISPOSITION — 2026-11-13

Dated continuation appended under Alex's authorisation (below). No earlier artefact is overwritten: the Batch 1 bundle, Reconciliation Rounds 2–6, Crusher's original return and the log extract all stand preserved at their pins.

## The decision

- **Decided by:** Alex, via Pulse Bridge, PB-ID pb-mwfht1ot-b-861t, 2026-11-13 ~13:33 MST.
- **Disposition:** "Overall Batch 1 freeze: APPROVED." Round 6 accepted; T07 correction accepted.
- Remmy is authorised to record the freeze as this dated continuation. **Batch 1 is CLEARED.**

## Basis, as adjudicated by Alex

1. **Crusher provenance — verified.** Alex fetched the log extract at commit 4c6e0b31 (duenna/batch1-reconciliation/CRUSHER-FB12-LOG-EXTRACT-2026-11-13.jsonl) and independently calculated its SHA256: 017a413ae934a8bd72fb5dc92b1359ab47ba77d11cfb63d27ae321cff2ae14b0 — exact match. Twelve entries present: Ben's lane check (call 6f7ea28aed94, answered); the six retrieval questions identifiable by call ID; Q3's first attempt and Q6's two attempts carry matching HTTP 429 failure records; Q3's resumed attempt (361317d87095) answered; Q1, Q2, Q4, Q5 answered. The extract supports the stated invocation provenance, confirms the provider failures, and confirms Crusher was operational during the retrieval.
2. **Pinned source integrity — verified.** PILOT-DATA-PACKS-01.json, PILOT-DATA-EXPECTED-01.json, PILOT-DATA-T09-01.json, PILOT-DATA-FIXTURES-01.json and verify_transcription.py each MATCH their pinned SHA256SUMS. The original manifest duenna/qwen-ab/QWEN-AB-EVIDENCE-MANIFEST.json matches its recorded SHA256 d544cad83cd86b5b54ebcd02120037c74451e678aa7d1d0e7415ede921bfd56d [manifest file hash as calculated and reported by Alex in pb-mwfht1ot-b-861t]. Frozen snapshot references: qwen-ab-evidence-manifest#001a — d06b2c621d79275908a8ff4691ffbbbf0733d4b2ff9afcca753922a4d8cb5f65; qwen-ab-evidence-manifest#001b — 0db8c757a9d2edc5e8fa16a5fee07e254fadf8f9226d7b10a69f60f14fa81b0c. The frozen snapshot contains 1,156 sections.
3. **Twelve-pack reconciliation — independently reproduced by Alex: 12 / 12 exact matches.** All twelve canonical render hashes independently match the original v1 manifest, including all four T09 receipt packs. (T01 and T05 correctly produce the same hash — same single section.) The four T09 as-built discrepancy hashes are reproduced exactly:
   - T09-FR-A: canonical fc1e98c0d4dd29f3afa5e2242815494849aa227f525cec8e55809ed2acbf4da9 / as-built b80ef9338eff379c4a716c3fa233907893302400c5483bd982a9340e06e33a4f
   - T09-FR-B: canonical 317d14846f4d407abbe55c50ff77ae36bce6562c15afaa2079452dc912aec494 / as-built 82dbf32dd74b0d1688981051fb210d2f8907b502fa127f3efd8b98a2238288e6
   - T09-FR-C: canonical 53170d5e00f046ca2f3de631533664f5c00630e8f9f32b3628c2b10c612ebb07 / as-built 12338a1061be5783ebdbda312a2ebc87104bbfa4a7cff794496ac5b19d588538
   - T09-FR-VALID: canonical 193f042e2d924d3454e766a1c1c5e5e0592f3dea3cc43b7cb18ac8b13f13beed / as-built 716824eeffa510e6f0d87567cbe7455e05233825a4f0c964291d9eb6715def3f
4. **Finding F-B1-2 — RESOLVED.** Each of the four T09 render pairs differs in exactly one line:
   `- === FIXTURE obligation-spec-text ===` / `+ === FIXTURE obligation-spec ===`
   The resolved content is identical; no other bytes differ. The four discrepancies are solely fixture-identifier rendering differences. Canonical rendering reproduces all twelve original v1 manifest hashes.

## What is frozen

- Batch 1 evidence bundle, commit 018a29c6 (duenna/batch1-2026-11-13/): corpus_source.py sha256 520f36fd…; PILOT-DATA-PACKS-01 c7eaec18…; PILOT-DATA-EXPECTED-01 79db5c87…; PILOT-DATA-T09-01 55a6c979…; PILOT-DATA-FIXTURES-01 b02e0dd0…; EXTRACTOR-RULES-02 61095f21…; transcription pins run_ab.py acb647bd…, tools.py e78f45d3…, demo_tools.py 6c960e44….
- Reconciliation: Amendment Draft 02 (sha256 607e0b3f…) stands as the frozen contract text, with the test records of Rounds 2–6 preserved as history; the latest corrected record is Round 6 (suite sha256 0b383846…, output sha256 269761c0…, 73/73 PASS; shelved 0124a201).
- Crusher's F-B1-2 return (commit 105e4d50, file sha256 c78f718b…) and the log extract (commit 4c6e0b31, file sha256 017a413a…) are preserved unchanged, including their failure records.

## Open item carried forward

Alex's letter states Batch 2 "remains closed and unauthorised." Ben's standing approval (2026-11-13 07:06 MST) covers Batch 2's go as item 5 of the reconciliation list, with Alex's checkpoint review as the build process. The freeze is recorded now; Batch 2's opening is put to Alex as the between-batch checkpoint question in the covering letter — no Batch 2 work starts before that checkpoint answers.
