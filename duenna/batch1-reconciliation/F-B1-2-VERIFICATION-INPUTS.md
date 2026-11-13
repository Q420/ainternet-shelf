# F-B1-2 VERIFICATION INPUTS — for Alex's independent reproduction

Supplied against Alex's inspection point 4 (pb-mwf3lae2): the pinned
inputs, the rendering implementation, the rendered outputs and the
comparison output, so the twelve hashes can be reproduced without
relying on Remmy's report.

## 1. Expected hashes — the pinned v1 manifest source

Source sections in PILOT-CORPUS-SNAPSHOT-01 (Batch 0 freeze):
- qwen-ab-evidence-manifest#001a — section sha256
  d06b2c621d79275908a8ff4691ffbbbf0733d4b2ff9afcca753922a4d8cb5f65
- qwen-ab-evidence-manifest#001b — section sha256
  0db8c757a9d2edc5e8fa16a5fee07e254fadf8f9226d7b10a69f60f14fa81b0c

The manifest is a JSON document; its "packs" block records, per pack,
the item list and the pack sha256. The twelve recorded hashes:

T01 99af9468d8abae8b36c1aa2367a3c9578ef2a1fb56989846d4099c96b91e29c7
T02 c03a4efc68d303255c17c70a34f3daa40474c411e4b3098187664494215962b8
T03 bbf7f602f24b5843f23a63c92d2f65006b42ca0539ae9b8e5d958b7e2d57bb07
T04 b2b977a748e6a19a4321370e585eb26e88e129def8683df7b3613dd05f626eee
T05 99af9468d8abae8b36c1aa2367a3c9578ef2a1fb56989846d4099c96b91e29c7
T06 ad8e14a55b1e1ddf4f407ed3e3dd0ceae5582d9f3f0083d088a84a5095958640
T07 18939819541f225eaa65ac54c75a89de0e6fb3fae6fcfc96df980488650ba231
T08 f804e949863b16f3971726092ff920c301a783329456c9ee70e1b8ba1a96fd9c
T09-FR-A fc1e98c0d4dd29f3afa5e2242815494849aa227f525cec8e55809ed2acbf4da9
T09-FR-B 317d14846f4d407abbe55c50ff77ae36bce6562c15afaa2079452dc912aec494
T09-FR-C 53170d5e00f046ca2f3de631533664f5c00630e8f9f32b3628c2b10c612ebb07
T09-FR-VALID 193f042e2d924d3454e766a1c1c5e5e0592f3dea3cc43b7cb18ac8b13f13beed

The manifest's item lists name the canonical fixture id
"obligation-spec" for all four T09 packs — the v1 record itself
carries the canonical identifier.

## 2. Rendering inputs — the frozen Batch 1 data files

PILOT-DATA-PACKS-01.json sha256 c7eaec18db203651af894e7fbdb53c6df9b36a3da185c4b7ab703d73085b886c
PILOT-DATA-EXPECTED-01.json sha256 79db5c87d4c9ccc52cb53c68fec5c2477cf546c9b80babbc489a472d37e57863
PILOT-DATA-T09-01.json sha256 55a6c979163a9ce0cb30fca4eb951aff0d02685979290df8bd18dfa28b355c4a
PILOT-DATA-FIXTURES-01.json sha256 b02e0dd005e884c62d493c1f524da983d77b2468645cf342e2a7fc9d9d08d9e8
Snapshot sections: PILOT-CORPUS-SNAPSHOT-01 (sections pinned by the
snapshot's own manifest; section hashes in sections.jsonl).

## 3. Rendering implementation

The render, as used at Batch 1 and in the reconciliation tests:
for each pack item in order — a corpus section renders as
"=== SECTION <section_id> · doc <doc> · <heading_path> · sha256
<sha256[:16]>… ===\n<text>"; a fixture/receipt item renders as
"=== FIXTURE <label> ===\n<resolved content>", where the label is
the fixture id (receipts render as "receipt-<KEY>" with content
"RECEIPT SUBMITTED FOR CLOSURE:\n" + the receipt JSON, indent 1).
Parts joined with "\n"; pack hash = sha256 of the UTF-8 encoding.

Implementations of record (identical algorithm, identical outputs):
- verify_transcription.py (the Batch 1 verifier) — sha256
  b22e350698c11cc02d28facbb6d1050bdcab057d0267d0d3b255e5e4e2ca00c4
- test_reconciliation.py (reconciliation Test 8) — sha256
  830b3fc8ae2b0133a0c4381f83a2ee73d5477adb248308c291cae2bdc7b25502
- make_fb12_renders.py (the T09 render generator) — sha256
  d41778b8f505aa951df7f1471a5236eab251e187ed4d742e60dc022d65ae0259

Canonical vs as-built: the as-built render uses the Batch 1 pack
refs verbatim (fixture label "obligation-spec-text"); the canonical
render substitutes the canonical V2 id "obligation-spec" as the
label. The resolved CONTENT is identical in both (the data file's
obligation_spec_text). No other input differs.

## 4. The T09 outputs — byte-level diffs

F-B1-2-T09-DIFFS.md (enclosed with the submission): for each of the
four T09 packs, the canonical and as-built sha256 and a unified diff
of the two rendered outputs. Every diff is exactly one line — the
fixture header label:

-=== FIXTURE obligation-spec-text ===
+=== FIXTURE obligation-spec ===

No other byte differs in any of the four packs.

## 5. Comparison output

RECONCILIATION-TEST-OUTPUT.txt, Test 8 (sha256 of the full output
record: 6af8c415053ae780820b706d72dd3e555936f7732f9a19e13355534775399fae):
the expected hashes were parsed from the manifest sections above
(not copied from the earlier comparison record); all twelve
canonical renders match them; the four as-built T09 renders
reproduce the discrepancy hashes of the original finding
(b80ef933…, 82dbf32d…, 12338a10…, 716824ee…).
