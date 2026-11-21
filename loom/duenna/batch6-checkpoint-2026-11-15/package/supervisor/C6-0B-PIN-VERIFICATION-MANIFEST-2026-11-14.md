# C6-0B — PIN VERIFICATION MANIFEST (2026-11-14)

Pre-batch gate C6-0b of the approved Batch 6 chunk sheet (disposition ALEX-C6-0A-2026-11-14, shelf commit e2cab33; approved sheet blob sha1 3a7632d2683e1cb8592ae75c2e289c461ba4a9fd, verified byte-for-byte). Method: every sha256 recomputed from the artefact itself; expected values read from the pin records on disk (PILOT-PIN-AUTHORITY-01, freeze-manifest.sha256, checkpoint MANIFEST.sha256 files, installed-pins.txt) — none typed from memory. The installed tree (/srv/nemotron-pilot, laptop WSL Ubuntu) was read back live via the SSH door on 2026-11-14 (read-back record: installed-readback-2026-11-14.txt).

## Alex's C6-0a condition — disposition

- (a) Formal Batch 4 clearance: ESTABLISHED by citation. Adjudication sha256 `79cbadea0b60f8f56fcfd8afe848057df101625c416be28e4fda32c8b2312614` records the bounded C4-10 hold; the crosswalk erratum sha256 `77d20e5f61e0aab7c6ff5c7a72276eedd659a6e0b0540cee31f12db3ff9feb62` — filed at Alex's direction (PB-ID pb-mwgz9mjj-2-dp2t), quoting his withdrawal ('My earlier crosswalk wording was wrong… I withdraw it') — records 'BATCH 4 CHECKPOINT: CLEARED.' Both shelved (filings @ 905b9eb3; checkpoint bundle @ 5f518804).
- (b) Launcher binary identity: VERIFIED LIVE. /srv/nemotron-pilot/launcher sha256 `9ea9b615a22bc7ea035d375fd3dd17c8fb5c7e8cdc9861a152882e382a637722` (owner root:pilot-supervisor, mode 4710, size 31224) — identical to the C4-12 pin record and to the reference Alex cited in his approval. Per the Gap 2 ruling, SE-7 (v)–(ix) are carried by pin citation; the re-execution trigger does NOT fire.
- Batch 5 clearance citation: ALEX-BATCH5-CLEARANCE-2026-11-14.md sha256 `275c7319036713df23bfc86f858bf2a58be17ddd2a70477b004061add258de3a`, shelved @ 8aabe8eb (checkpoint @ dde40a23, correction 4 @ 84048c65).
- Pin authority of record: PILOT-PIN-AUTHORITY-01.json sha256 `e245cabc504e4b8f6fdefda030fea46476700887ac02172f042a33648fef247d` (batch3-correction2 copy; generated_from: PILOT-MANIFEST-01 and the re-freeze continuations F2, BATCH1, BATCH2, BATCH2-CORRECTION, BATCH3, BATCH3-CORRECTION; round-2 form: consumed inputs only (no driver, no suite), anchored by the hash embedded in the round-2 driver and recorded in CONTINUATION-BATCH3-CORRECTION-2). Entries passing against installed and/or local copies: 17 of 17.
- Catalogue bare-body hash 8a80b8e7… (Rev 26 §3.5 (viii)): verified at the Batch 5 C5-0c gate (C5-0C-GATE-RECORD.md, recomputed there) and carried by that citation; the snapshot FILE and helper-stdout artefacts are re-verified below against the freeze manifest.

## Observation (not a gate failure)

The Batch 5 checkpoint MANIFEST.sha256 uses a three-space hash/filename separator, which stock `sha256sum -c` parses as a leading-space filename (every entry reports 'FAILED open or read'). With the separator normalised, the bundle verifies complete (see row below). Batch 6's own manifest (C6-12) must use the standard two-character separator. The Batch 5 bundle's artefacts are unaffected.

## Verification rows (31)

| Artefact | Expected (pin) | Actual | Verdict | Pin source |
|---|---|---|---|---|
| installed:launcher | `9ea9b615a22bc7ea…` | `9ea9b615a22bc7ea…` | PASS (live read-back) | installed-pins.txt (Batch 4 bundle) vs live read-back 2026-11-14 |
| installed:pilot-harness | `367207ff5cb7f336…` | `367207ff5cb7f336…` | PASS (live read-back) | installed-pins.txt (Batch 4 bundle) vs live read-back 2026-11-14 |
| installed:pilot_record.py | `ed3f5c8521159d87…` | `ed3f5c8521159d87…` | PASS (live read-back) | installed-pins.txt (Batch 4 bundle) vs live read-back 2026-11-14 |
| installed:pilot_jcs.py | `8a131cfce23c9762…` | `8a131cfce23c9762…` | PASS (live read-back) | installed-pins.txt (Batch 4 bundle) vs live read-back 2026-11-14 |
| installed:pilot_supervisor.py | `c8a11370d06af575…` | `c8a11370d06af575…` | PASS (live read-back) | installed-pins.txt (Batch 4 bundle) vs live read-back 2026-11-14 |
| installed:pilot_jcs.py | `8a131cfce23c9762…` | `8a131cfce23c9762…` | PASS (live read-back) | installed-pins.txt (Batch 4 bundle) vs live read-back 2026-11-14 |
| PA:corpus-snapshot-sections | `b107e8926abc5fed…` | `b107e8926abc5fed…` | local PASS | PILOT-PIN-AUTHORITY-01 |
| PA:corpus-snapshot-manifest | `c93eaa1906a068c5…` | `c93eaa1906a068c5…` | local PASS | PILOT-PIN-AUTHORITY-01 |
| PA:PILOT-DATA-PACKS-01 | `c7eaec18db203651…` | `c7eaec18db203651…` | installed PASS | PILOT-PIN-AUTHORITY-01 |
| PA:PILOT-DATA-EXPECTED-01 | `79db5c87d4c9ccc5…` | `79db5c87d4c9ccc5…` | installed PASS | PILOT-PIN-AUTHORITY-01 |
| PA:PILOT-DATA-FIXTURES-01 | `b02e0dd005e884c6…` | `b02e0dd005e884c6…` | installed PASS | PILOT-PIN-AUTHORITY-01 |
| PA:PILOT-DATA-T09-01 | `55a6c979163a9ce0…` | `55a6c979163a9ce0…` | installed PASS | PILOT-PIN-AUTHORITY-01 |
| PA:EXTRACTOR-RULES-02 | `61095f219e1d481e…` | `61095f219e1d481e…` | installed PASS | PILOT-PIN-AUTHORITY-01 |
| PA:corpus_source.py | `520f36fde41dfb76…` | `520f36fde41dfb76…` | installed PASS | PILOT-PIN-AUTHORITY-01 |
| PA:rules_engine.py | `7a2329154081b6e9…` | `7a2329154081b6e9…` | installed PASS | PILOT-PIN-AUTHORITY-01 |
| PA:pilot_jcs.py | `8a131cfce23c9762…` | `8a131cfce23c9762…` | local PASS | PILOT-PIN-AUTHORITY-01 |
| PA:pilot_tools.py | `df1045f7923b458c…` | `df1045f7923b458c…` | installed PASS | PILOT-PIN-AUTHORITY-01 |
| PA:pilot_record.py | `ed3f5c8521159d87…` | `ed3f5c8521159d87…` | installed PASS | PILOT-PIN-AUTHORITY-01 |
| PA:pilot_trees.json | `d23f35f660ee4967…` | `d23f35f660ee4967…` | installed PASS | PILOT-PIN-AUTHORITY-01 |
| PA:stub_subject.py | `465d325a53f7ef57…` | `465d325a53f7ef57…` | installed PASS | PILOT-PIN-AUTHORITY-01 |
| PA:stub_script_main.json | `dde24b6a5ad98f68…` | `dde24b6a5ad98f68…` | installed PASS | PILOT-PIN-AUTHORITY-01 |
| PA:stub_script_lane.json | `ed590514b23bfef6…` | `ed590514b23bfef6…` | installed PASS | PILOT-PIN-AUTHORITY-01 |
| PA:stub_script_budget.json | `793d7b58dee76b88…` | `793d7b58dee76b88…` | installed PASS | PILOT-PIN-AUTHORITY-01 |
| freeze:adapter-config-f2-2026-11-12.canonical.json | `6cf57195d9ae27ca…` | `6cf57195d9ae27ca…` | PASS | freeze-manifest.sha256 (Batch 0 freeze) |
| freeze:adapter-config-f2-2026-11-12.json | `beb8b7fd670d5bde…` | `beb8b7fd670d5bde…` | PASS | freeze-manifest.sha256 (Batch 0 freeze) |
| freeze:catalogue-snapshot-2026-11-12.json | `17d69d609ec5449b…` | `17d69d609ec5449b…` | PASS | freeze-manifest.sha256 (Batch 0 freeze) |
| freeze:recovered-catalogue-response-2026-11-12.json | `bacf2ec8c71a8972…` | `bacf2ec8c71a8972…` | PASS | freeze-manifest.sha256 (Batch 0 freeze) |
| Adapter ADAPTER-CAPTURE-02 | `8a11f399bdaf0181…` | `8a11f399bdaf0181…` | PASS | Batch 5 checkpoint MANIFEST @ dde40a23 |
| Transport double | `ec91b79caff8069d…` | `ec91b79caff8069d…` | PASS | Batch 5 checkpoint MANIFEST @ dde40a23 |
| JCS (Batch 5 sources) | `8a131cfce23c9762…` | `8a131cfce23c9762…` | PASS | Batch 5 checkpoint MANIFEST @ dde40a23 |
| Batch 5 checkpoint bundle self-consistency | `41 entries…` | `41 OK / 0 FAILED…` | PASS | MANIFEST.sha256 @ dde40a23 (separator normalised for the check; see observation) |

## Result: C6-0b SATISFIED — every resolved pin verifies; Alex’s condition (a)+(b) established

Generator: verify_c6_0b.py (this directory). Full paths per row are in the generator's row table.
