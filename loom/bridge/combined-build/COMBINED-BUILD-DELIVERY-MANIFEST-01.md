# Combined Build — Delivery Manifest 01 (v0.21.0)

ZIP: pulse-bridge-v0.21.0.zip — 28 files (tests-stage1 excluded)
ZIP SHA-256: 47c2944449011081d91467c7bdbaed8b9e78e37083647dc46aeb3fe97e35acce
Parent: v0.19.1 per bridge/COMBINED-BUILD-PARENT-MANIFEST-01.md
Fixtures: 188/188 (identity 44, ledger 56, batch3 21, delivery 4, correction 21, completeness 17, fence 9, lease 6, station 10); rebuild-verify PASSED; worker load OK.

## Build tree file hashes (SHA-256, all 37 files incl. tests)

```text
a771d1580919b06ec3f0eeba7cae499325e3695cd2d48fe22d71d8cbebaa6e8d   adapters/chatgpt.js
57083f7bf45649633093a29914816c96a99260ed0e63c52c2a82d3667d92ff2e   adapters/claude.js
2a961534941645057cf04e23da933d245c44ab55b0f1d723c94f9b0e30cf0555   adapters/claudeai.js
c9cdc106e53fea1341580fa625c3dcf82be2c04fcdfa55b977ade2ca0f460f2f   adapters/gemini.js
aa60cf49f5cc0349d3b689e9531a48bacc67480edf21cce0153bcacc0352d4ac   adapters/metaai.js
2ed02e6fd012fad1cdb61c8d8885b624623f22d9ecd897aeb8c413a4d65acd1f   alert.js
4d3cc64cc9080cb9dc94143d6f4715f71e22dbb6474e9a379ac8c2e1eb5339bd   background.js
69afc85e8d54155e4bb61f593cd72a53c423e35066401f6e0f961a0f4e34c8b3   build-stage1-bundle.js
c461bf972ab0478d5eea35ffbc12f7f5215bc2da7e0eabdf6b363ccfb2c23cc8   capture.js
0eb2b5cc976cc194c607a27da92fc0bd039441985674f0eed18bb95920d05b82   completeness.js
8330204a4448094ef21e845085d644e933fb63712ae19b66dc1c4a743465b183   content.js
822518955b20f7db9a3a7b6b9c8a79a3c8906fec6af486882d7c2c092b182df7   crusher.js
2d25b7fd1bba71751bd4f8f7ff9656bff5c4691d95ca195e5691ff2cf8b9a012   fence.js
02ea08c0e97e918168a3eacfec6baf140d71ca5befa9dd2dbb018aefd68ee467   identity.js
b5b70290ce8f9c7d53a49aab0ac395415431d0004769580ae16cd650d242b89f   ledger.js
d6757350bec41e81bf440343cd3b81d89c36f0a44ef6ee9a36e4c37f302cabd0   letterbox.js
cad2e5845b6807fba8b86a3beeda29b390d88fe36cda97c3e7d2a87d5df320cb   manifest.json
f68fa341b9b2302e395f536a7bc4ba0fd3ab3f6ebae3f32e88d2873ee3c57538   migration.js
efd33499722685f6f58f36fb2e899e5a8b37efd4c4ca44b253cf12f92010e9da   popup.html
9b934b47d63dba26305cc3cba0951eb46933b7e5f7f9b568088dc83f5f806770   popup.js
c54a99415f7c37d135baa293ca808db9cf3412106387785483bf109b05724d05   protocol.js
4d3fb5e8166f0b91a507828bf4e33ca15e0f1f83c548dc46b2f1f70911f72cd1   sendcore.js
65fd7e7c3a6b29aec5755c5b3d9e9b0175e5195a0366d489c302aa9f1dadb80d   stage1-wiring.js
ace1a3ae04741af6bd6c2752c9891d23030306ad27aa7dfed0e531046dd9082a   stage1core.js
821bb919e930caaa5077c1a3bc394f87cc097900603bef03736a15e306ff8d09   station.js
1806cb072eeff88b08ac95b425186aaa23112134e8f70bfddab4419672f9781a   storage.js
12080f1976317cfa08b6bcae736706e26f96ccf69d9ead1ccfd2f450c9805887   tests-stage1/batch3.fixtures.js
8f7f0779504aa960805b225186e8dbc0b7cd2b34d71c4764d65798c2eab2f3fa   tests-stage1/completeness.fixtures.js
5f6e5d997dcbb10bdc52d346ae1bf820778a33923396b9f55d4a38545aa92044   tests-stage1/correction.fixtures.js
c60eb3050384e61b6586a9e62f1219657ae7d3ac34ed4ef5a4f8d6b6f509c9fc   tests-stage1/delivery.fixtures.js
0a379cd626282bf5a305788c33c0383570b9eb900f492fb48f9669afc64238b5   tests-stage1/fence.fixtures.js
252a64b6f191b152b465fe4b3ccb7d0a3fd5de10e0eaae4b5a3e83ccc832039a   tests-stage1/identity.fixtures.js
6bb6345c44f48dbe9cbe2aedd1375b767ed2b38ca23984446e898f698bdad298   tests-stage1/lease.fixtures.js
cd2e781a71b7d490f8f796ff6d0c75907da13017ad1d92e78b447070bc9a92a4   tests-stage1/ledger.fixtures.js
7461c3defb1c2861b70ce293424d4eeba8fc06057f1df9b3d90177f11e2fd8e3   tests-stage1/rebuild-verify.js
8d294d34cc0637b95e05bacb12f5a074ec901a01822b040d4d19f8f136585f0f   tests-stage1/station.fixtures.js
da1537fa0914f8c0c299577d5520e5974882a1e82f29855e430b645559ef0959   witness.js
```

## Source addendum (2026-11-11, after Tansys match attempt)

The exact v0.21.0 build tree (all 37 pinned files, incl. adapters/ and tests-stage1/) is shelved at bridge/combined-build/source/ so the pins above can be matched file-for-file. It was NOT on the shelf when the manifest was first published — Tansys review caught that; the gap is recorded, not smoothed over.
