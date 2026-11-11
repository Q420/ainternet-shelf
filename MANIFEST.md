# MANIFEST — the shelf catalogue

Read this first. Every document on the shelf, by path, with its
sha256 (of the file as shelved) and what it is. If you quote the
record, quote it from these files. Shelf opened 2026-11-10; the
full corpus sweep was shelved the same day.

## Root, seats, and the living record

| Path | sha256 | What it is |
|---|---|---|
| `README.md` | 28fad5b335109aa9c7473fcfe7c65472b0b8a3771f76100b4a893e632ce9ec31 | What the shelf is and how a seat uses it |
| `seats/alex.md` | 5099957afe09d590efb232a8cffc7dbe406e257f7428cce46f537872fabe6dc3 | Alex's page — roles, seats, rules, state |
| `seats/vane.md` | 599ad33b2559ad57c4547a0d552572beddc187a6254814c98e07499b1fa1b26a | Vane's page — examiner role and record |
| `seats/remmy.md` | 9c149a2c8feb4812bcb202e1831e0be1b853987462b97a00654de768d2add893 | Remmy's page — standing processes |
| `record/DUENNA-PLAN.md` | eb3723e4f2e57121de40d821fe87ffdfa9b7fe4ce5406fd4d787f6302a980341 | THE plan list — the programme's authoritative state |
| `record/DUENNA-STEP6-ARCHITECTURE.md` | 69664387ed302c54d2b77baa0ba235c3cc79d04595d50b5279ecafcf1556637d | The agreed four-component architecture (step 6, agreed text) |
| `record/DUENNA-STEP7-PLAN.md` | 929b2378a40dc45fa1f58c5014d60cc1aa014acfb6c70870d9bf823b2ae06a64 | The joint implementation plan (step 7, agreed text with amendments) |
| `record/v010-unresolved-items.md` | b9e8e457c4858def403f8a9321bf5e16ef537015eb102c76ec3659776efecb33 | What v0.10 deliberately does not claim — gaps, statuses, the open gate |
| `record/STAGE0-BASELINE-EVIDENCE.md` | 73b3fabdf95e672c06c692c521dfcca8ebc2d5d285a86062989ad4349d33f03a | Stage 0 baseline run record (31/31 PASS, seed hash unchanged, zero comparison diffs) |
| `record/stage0-run-stdout.txt` | 1765950a8b9a1a06f39ddf233d72667f4be47d1b6ed269af708c12f71a98ce05 | Stage 0 raw run output (31 PASS lines + summary) |
| `record/stage0-results.json` | ad4dc13754c543520dea2b93c80165df85595a18e873438f2d600779e355ce38 | Stage 0 results JSON — byte-identical to the delivered v0.10 results |
| `record/GATE-REGISTER.md` | fbc6c56177f2e04f1865d7bd2accb7e7e6f9bb61a0b741ad932a42c3265a62f3 | The gate & dependency register — what is ready, what is waiting, and what opens each gate |

## duenna/ — the specification corpus

| Path | sha256 | What it is |
|---|---|---|
| `duenna/PROCESS-TREE-D3-SPECIFICATION-v0.7-PROPOSAL.md` | a14cad05061cea6b80930f6704b5dd082336d26eadec2e98844ee138e2ec3393 | D3 v0.7 — frozen, immutable (file incl. appended serial line; canonical text hash 28718d26…) |
| `duenna/PROCESS-TREE-D3-SPECIFICATION-v0.8-WORKING.md` | 3e053efc97d876d50f649eb0b4c8c740ab6085314aa54f9132fdf33e243d97d4 | D3 v0.8 — APPROVED WITH STATED CONDITIONS; immutable |
| `duenna/PROCESS-TREE-D3-SPECIFICATION-v0.9-WORKING.md` | ac2a2484dd4e170948f868d4ac1680221fbcd3a905c75d1d2da21f4d0d0485dc | D3 v0.9 — examined; NOT APPROVED; gate open |
| `duenna/PROCESS-TREE-D3-SPECIFICATION-v0.10-WORKING.md` | 9241a8b40f93b4e303b03ba5d5f31d244c3c361769263adedb7393626e6acd2e | D3 v0.10 — the revision under examination; NOT APPROVED |
| `duenna/PROCESS-TREE-v0.4-PROPOSAL.md` | b4fb404c9f9b4577603b8afced9c8e63c20399b929ff2777e42321151f8f04e5 | The Process Tree v0.4 |
| `duenna/EXECUTION-CONTRACT-v0.1.md` | c7e689011312c32e4a69211984b37264c107a88a12b3f27c6da8cbcd9b07dec3 | The execution contract |
| `duenna/D3-CORRECTION-MATRIX-R33-R65.md` | f6ddf789f9a0ac44f5e8b0215f80180259c686a044de68741dac31450f2aa1f7 | The 33-row correction matrix (R33–R65) |
| `duenna/PROCESS-TREE-D3-REVIEW-RESPONSE-v0.7.md` | d71d0a7924b307442f49687485f8be452b6ef545aea52e63e71aa5de80457ab4 | The Round 7 register |
| `duenna/D3-V08-CHANGE-RECORD.md` | 88f20774d14c685b779e6e7b643fbd7af31c3e836128901cdb42224ce82b6b85 | v0.8 change record |
| `duenna/D3-V08-TRACEABILITY.md` | ea97244258f4770622f0c71d0e0271455e57383f5eb1cb6768a8ec71dbd3fbb1 | v0.8 traceability |
| `duenna/D3-V09-CHANGE-RECORD.md` | 72431155967673136ae3468841cbc75f32f7873ca9ed7263a73b0e86b9a6fc1d | v0.9 change record |
| `duenna/D3-V09-TRACEABILITY.md` | 79442c7057586bcb1c1b7783172962ebf0d8bef5b2cd26fbd37c630858f5446d | v0.9 traceability |
| `duenna/D3-V010-CHANGE-RECORD.md` | b8d769a53551d16c193f7f4d34a8b38717a9d26a72b8f9ea3b1c4e25dd8dbd54 | v0.10 change record |
| `duenna/D3-V010-TRACEABILITY.md` | 931da270f422308faa3ac74f1cc72b515a6dab4affda91b2575e1ee307ef1333 | v0.10 traceability |
| `duenna/CLAUDE-VERIFICATION-REPORT.md` | 18de602d1101d6e9e03eabf105981c2c3da1ec166a080593f1bd96bb4df20a11 | Claude's verification report on v0.8 |
| `duenna/CLAUDE-VERIFICATION-REPORT-V09.md` | 1b760ac00efea716dd32a96755eaa6150580f04abc6bbe0388a743fbda00ca45 | Claude's verification report on v0.9 |
| `duenna/CLAUDE-VERIFICATION-REPORT-V010.md` | 8686624ae4dabbcff71f4886a2077dedc68c8ed20cb38d38ff3181087c23ec08 | Claude's re-examination report on v0.10 (R47 PASS narrow, R60 FAIL partial, R65 PASS) |
| `duenna/VANE-EXAMINATION-REPORT-V010.md` | 884fe426c32cd1f7641f2a965d3e39053ec626a5d7829eaae367883a2772b0a3 | Vane's independent examination of v0.10 (R47 PASS, R60 FAIL — unbound procedure identity, R65 PASS qualified) |
| `duenna/ALEX-COMBINED-ADJUDICATION-V010.md` | cbf6ec46c6e60e33008712f7edc568158c205c51a433d0554857a55ad99754ed | Alex's combined Track 1 adjudication (R47 PASS narrow, R60 FAIL, R65 PASS qualified; R60 revision OPEN, both defects) |
| `duenna/harness-r60rev.py` | 3c393fceb2fb550bf27d49004d0940ec069ae5f3893f5a419ee101d2d53983b8 | R60 revision harness v2.2 (33 cases: 31 preserved + FX-R60f + FX-R60g) |
| `duenna/results-r60rev.json` | f257fbd5b11d3de8232c44a5bc62e4dd50be43c9672ecc560faf531c4941f844 | R60 revision results (33/33 PASS) |
| `duenna/R60-REVISION-CHANGE-RECORD.md` | 00727c5d65e78a26fdfd32029951e37dd59894db9a90e31e523d5f745c1370ff | R60 revision change record (both corrections + sabotage evidence) |
| `duenna/R60-REVISION-UNRESOLVED.md` | 5d8093707144777926d78829763af6f8cb765bbeed05cbb696735e5b58b2e90c | R60 revision unresolved items (carried forward) |
| `duenna/VANE-EXAMINATION-REPORT-V09.md` | 643923ec8f0433ab67b71d484bb5aeaca17240d986eaa3001e1672f48fa09b2a | Vane's examination report on v0.9 |
| `duenna/V09-EXAMINATION-FINDINGS-LEDGER.md` | cf116ba28d822c15d70c82ad7e02be8fccde932d749c4c5a2bae02dd5ad20af3 | The consolidated v0.9 findings ledger |
| `duenna/V09-VERIFICATION-EXAM-PACK-R4.md` | db429e3a1f85ac4a388cfccf726a62d21b96e62637f6d6efaeba9c836ed30434 | The v0.9 verification exam pack, edition R4 (current) |
| `duenna/DUENNA-SIMPLIFICATION-AUDIT.md` | 13984600c45f9d37f83cd17036f1a3fffdb5d472b8b7c93e8d46af22b33cb30c | The simplification audit — input to the joint plan |
| `duenna/DUENNA-STEP3-MAPPING.md` | 51294cb6d75f3a5c72eef9e6899619bcdc7fc147b43a58358da8538fdc4f810d | Joint plan step 3 — the function mapping |
| `duenna/DUENNA-STEP4-EXAMINATION.md` | ee9b69c716a3f4f6f56ece8b3bde4314492442d57aa834ea116a88d4f38fdcfa | Joint plan step 4 — the consolidation examination (Alex-corrected text) |
| `duenna/DUENNA-STEP5-CHALLENGE.md` | 44ca72c75c64f07fac4e025a8c6d44f0857d3d3fd628aa0047e1d40e7ae21670 | Joint plan step 5 — the challenge round, settled |
| `duenna/FIXTURE-RESULTS-V09.md` | ff6649dbda05b94139cf97728b26f8947732254d1fe12451afbbc8f0bd723d96 | v0.9 fixture results (31/31, implementer-run) |
| `duenna/FIXTURE-REGISTER-V09.md` | 629f352542f31eaeab413f593c7648288571b54b25226200b83bf3f393564a64 | v0.9 fixture register |
| `duenna/FIXTURE-RESULTS-V010.md` | 11b42cb4a740647d5788e8ea7eebe03a5593848c9d4ace79cdff4c03c88a9821 | v0.10 fixture results (31/31, implementer-run) |
| `duenna/FIXTURE-REGISTER.md` | 772c394d25de14b77a461fe3f3d23032b3c028131b7966c1c215ad5da1a9a3a1 | v0.10 fixture register |
| `duenna/harness-v010.py` | efe69df64a964bf5fb45cc2234c539908e3b7e600cd209de5867ccf0ad78ee6c | The v2.1 fixture harness (v0.10) |
| `duenna/results-v010.json` | ad4dc13754c543520dea2b93c80165df85595a18e873438f2d600779e355ce38 | The v0.10 fixture run output |

## bridge/ — Pulse Bridge, current build (v0.18.0)

| Path | sha256 | What it is |
|---|---|---|
| `bridge/BLUEPRINT-v1.0.md` | 22c0e4514ba8d0d2c352847dcfe0db4c1ecb6f635e97651d9988cae91090a421 | The Pulse Bridge blueprint |
| `bridge/BRIDGE-README.md` | e69df6420c25512efd022e29c707588d5424f2b70568e0a59e94838a73bfa779 | The bridge's own README (build and handoff notes) |
| `bridge/INCIDENT-LOG-MESSAGE-SUBSTITUTION.md` | 1544cc6400958a39c2508ef72628cc4d7f0cb22e47ba5e45314274ec19a7392c | The message-substitution incident log |
| `bridge/TEST-REPORT-v0.18.0.md` | a86e62c2ef6ff1ad647cbb9129e44085314333a6d5b92038f30de2153bd55ee5 | v0.18.0 test report (819 checks / 0 failures) |
| `bridge/manifest.json` | ef212af6ba93c115aea78f4c122a03a8a0d0156519926337ec0c428bd489cba1 | The extension manifest (v0.18.0) |
| `bridge/fence.js` | ee19224a36b2bbd2c6e12ddce7918cb8aed1549552e80ecb5e7c51f86c79de58 | The seat fence |
| `bridge/sendcore.js` | 40aa6ac785a11b78313cfc19442f076b3d2c2698de1424d765038a2dc4445486 | The shared send core (PB_SEND) |
| `bridge/alert.js` | 2ed02e6fd012fad1cdb61c8d8885b624623f22d9ecd897aeb8c413a4d65acd1f | Bridge Alert |
| `bridge/background.js` | 0bb75bb864f8b7f133e63f12900a4fe3186e528f11973fc4976c45cf45062e05 | Extension background module |
| `bridge/content.js` | 839e760cffb87f7bd7c1653b877fa5b8934dab6bf4468df3275e608679d49202 | Extension content module |
| `bridge/protocol.js` | c54a99415f7c37d135baa293ca808db9cf3412106387785483bf109b05724d05 | The bridge protocol |
| `bridge/storage.js` | 63dfc79ca97863f6559b9156e2a1a2fb7c0cabc41e1e50613bc56f30f611e348 | Extension storage module |
| `bridge/letterbox.js` | 450835885890a6757ad8e934e7ebb488e2e59c8a6c1b010e00b5fa43ed4d5897 | The letterbox |
| `bridge/witness.js` | da1537fa0914f8c0c299577d5520e5974882a1e82f29855e430b645559ef0959 | The witness module |
| `bridge/crusher.js` | 822518955b20f7db9a3a7b6b9c8a79a3c8906fec6af486882d7c2c092b182df7 | The Crusher lane |
| `bridge/popup.html` | 46ac00fd39293014d2a5e6317d0ef5ab0371eeefee81abc4a5e1b912a0f4557a | The bridge panel (page) |
| `bridge/popup.js` | ab64334022efe8b1ab7f676fab98e2227025a8451095634eaf33b8219121ddf3 | The bridge panel (logic) |
| `bridge/adapters/chatgpt.js` | a771d1580919b06ec3f0eeba7cae499325e3695cd2d48fe22d71d8cbebaa6e8d | ChatGPT surface adapter |
| `bridge/adapters/claude.js` | 57083f7bf45649633093a29914816c96a99260ed0e63c52c2a82d3667d92ff2e | Claude surface adapter (dormant) |
| `bridge/adapters/claudeai.js` | 2a961534941645057cf04e23da933d245c44ab55b0f1d723c94f9b0e30cf0555 | Claude.ai surface adapter (dormant) |
| `bridge/adapters/gemini.js` | c9cdc106e53fea1341580fa625c3dcf82be2c04fcdfa55b977ade2ca0f460f2f | Gemini surface adapter |
| `bridge/adapters/metaai.js` | aa60cf49f5cc0349d3b689e9531a48bacc67480edf21cce0153bcacc0352d4ac | Meta AI surface adapter |

## Reading order for a fresh seat

MANIFEST → your seat page → `record/DUENNA-PLAN.md` (the state) →
the step 6 and step 7 texts (the agreed product). Examiners: the
specification line and reports under `duenna/`. Bridge work: the
blueprint and current build under `bridge/`.

## Custody

Sources of record remain the programme's workspace files
(agent-factory for `duenna/`, the pulse-bridge tree at v0.18.0 for
`bridge/`); this shelf is their published reading surface, kept in
step by Remmy under Ben's authority. A shelf copy and its source
are the same text or the difference is a defect — report it,
don't average it.
