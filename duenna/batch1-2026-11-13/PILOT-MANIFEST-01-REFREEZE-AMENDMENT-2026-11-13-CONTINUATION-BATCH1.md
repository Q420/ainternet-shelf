# PILOT-MANIFEST-01 RE-FREEZE AMENDMENT — CONTINUATION: BATCH 1

Dated continuation of the Batch 0 re-freeze amendment
(2026-11-12, with its F-2 continuation of the same date),
recording the Batch 1 artefacts of the Stage 5 build
(STAGE5-BUILD-SPEC-13, pin bab720b2) as Spec §4 / Harness §3.3
direct: each new artefact pinned by sha256. The original
amendment, the F-2 continuation, the A-1 amendment, and every
Batch 0 freeze file stand byte-identical and untouched.

Build location: the Ubuntu room on Ben's laptop,
`/srv/nemotron-pilot/batch1/work/` (Batch 0 freeze in
`/srv/nemotron-pilot/freeze/`). All Batch 1 stages ran in the
standing watch window; logs in the Batch 1 evidence bundle
(duenna/batch1-2026-11-13/).

## Batch 1 artefact pins

| Artefact | Bytes | sha256 |
|---|---|---|
| PILOT-DATA-PACKS-01.json | 6,486 | `c7eaec18db203651af894e7fbdb53c6df9b36a3da185c4b7ab703d73085b886c` |
| PILOT-DATA-EXPECTED-01.json | 748 | `79db5c87d4c9ccc52cb53c68fec5c2477cf546c9b80babbc489a472d37e57863` |
| PILOT-DATA-T09-01.json | 1,952 | `55a6c979163a9ce0cb30fca4eb951aff0d02685979290df8bd18dfa28b355c4a` |
| PILOT-DATA-FIXTURES-01.json | 5,763 | `b02e0dd005e884c62d493c1f524da983d77b2468645cf342e2a7fc9d9d08d9e8` |
| EXTRACTOR-RULES-02.json | 884 | `61095f219e1d481ed74c65f3a95806a2cba2e7dc847bcb692373ade3974c5ee5` |
| corpus_source.py (CorpusSource) | 4,601 | `520f36fde41dfb76d5f92fe4da92b6c2f93ae8512051962f76d4942fb5c05a5a` |

Transcription source: the pinned `run_ab.py` (Manifest row 7,
sha256 acb647bd…), staged into the room and hash-verified there
before transcription; the runner was read by AST only, never
imported or executed.

Rules note: EXTRACTOR-RULES-02 carries six rules. Five declare
their fields' presentation sites directly; `fixtures_passed`
(EXT02-FP-2) is a **sharpened** successor to V2's `(\d+) PASS`,
which is ambiguous on its own pinned section — finding F-B1-1
in the Batch 1 checkpoint report, with the remedy declared
there for the reviewer's adjudication.

## Pack hashes (V2 pack_text rendering, from the refs alone)

| Tree | pack sha256 |
|---|---|
| T01 | `99af9468d8abae8b36c1aa2367a3c9578ef2a1fb56989846d4099c96b91e29c7` |
| T02 | `c03a4efc68d303255c17c70a34f3daa40474c411e4b3098187664494215962b8` |
| T03 | `bbf7f602f24b5843f23a63c92d2f65006b42ca0539ae9b8e5d958b7e2d57bb07` |
| T04 | `b2b977a748e6a19a4321370e585eb26e88e129def8683df7b3613dd05f626eee` |
| T05 | `99af9468d8abae8b36c1aa2367a3c9578ef2a1fb56989846d4099c96b91e29c7` |
| T06 | `ad8e14a55b1e1ddf4f407ed3e3dd0ceae5582d9f3f0083d088a84a5095958640` |
| T07 | `18939819541f225eaa65ac54c75a89de0e6fb3fae6fcfc96df980488650ba231` |
| T08 | `f804e949863b16f3971726092ff920c301a783329456c9ee70e1b8ba1a96fd9c` |
| T09-FR-A | `b80ef9338eff379c4a716c3fa233907893302400c5483bd982a9340e06e33a4f` |
| T09-FR-B | `82dbf32dd74b0d1688981051fb210d2f8907b502fa127f3efd8b98a2238288e6` |
| T09-FR-C | `12338a1061be5783ebdbda312a2ebc87104bbfa4a7cff794496ac5b19d588538` |
| T09-FR-VALID | `716824eeffa510e6f0d87567cbe7455e05233825a4f0c964291d9eb6715def3f` |

## Checkpoint machinery (evidence, not pilot artefacts)

| File | sha256 |
|---|---|
| transcribe.py | recorded in the bundle SHA256SUMS |
| verify_transcription.py | recorded in the bundle SHA256SUMS |
| test_corpus_source.py | `9fe224b63a4228774527e2628920e926f6cf88d48af6643969f95f13818da038` |
| rules_engine.py (checkpoint test instrument) | `7a2329154081b6e9c0417c07b1cc7184b167d02c1e820081b68a18dbabafacf3` |
| test_rules.py | `9d23a50ec6ba6d3e60afe88bcaa5345da1cf2e9f7a36630b1a33d2598602f03b` |

Results on record: transcription verification 19/19;
CorpusSource contract tests 10/10; rules exercises 12/12 —
all executed in the Ubuntu room, in the watch window, on
2026-11-13.
