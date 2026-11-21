# Combined Build — Parent Manifest 01 (the v0.19.1 parent, pinned)

**Purpose:** Alex's pre-build review (item 9) found the combined scope named the v0.19.1 tree without an independently identifiable pin. This manifest is that pin.
**Parent tree:** `build-v0.19.1` — the Stage 1 delivery (v0.19.0, shelf commit 0a9fb9199f95ca9aeb559fbcf597030e2d4c6481) plus the terminal-readout overlay, and nothing else.
**Diff vs the v0.19.0 tree (verified by directory diff, 2026-11-11):** exactly four files differ — `content.js`, `letterbox.js`, `manifest.json`, `popup.js`. The readout: letterbox `peekNewest()`, content `pb-state-query` carrying `retrieval`, popup live-state terminal lines, manifest version 0.19.1.
**ZIP:** pulse-bridge-v0.19.1.zip (tests-stage1/ excluded), SHA-256 `3b5887aa8ac533be669185aff35eea46e1b12379686adf7c982b7d1a9ae73d55`.
**Combined build base:** `build-v0.21.0` was copied from this tree on 2026-11-11 and verified file-identical to it before any change; the full Stage 1 suite ran 125/125 in the copy.

## File hashes (SHA-256, parent tree)

```text
a771d1580919b06ec3f0eeba7cae499325e3695cd2d48fe22d71d8cbebaa6e8d  adapters/chatgpt.js
57083f7bf45649633093a29914816c96a99260ed0e63c52c2a82d3667d92ff2e  adapters/claude.js
2a961534941645057cf04e23da933d245c44ab55b0f1d723c94f9b0e30cf0555  adapters/claudeai.js
c9cdc106e53fea1341580fa625c3dcf82be2c04fcdfa55b977ade2ca0f460f2f  adapters/gemini.js
aa60cf49f5cc0349d3b689e9531a48bacc67480edf21cce0153bcacc0352d4ac  adapters/metaai.js
2ed02e6fd012fad1cdb61c8d8885b624623f22d9ecd897aeb8c413a4d65acd1f  alert.js
24cc596cc31c1e22cea330a2af0e4abccc946bfad3f664f7a39480cb28074f20  background.js
81dc1f5cf3d78ef35ae1b2e6b3c4983b002d0499321ce5a1e8361cfdbf391204  build-stage1-bundle.js
b17abc2bec960a9a06a77d4322a8b8e184eda7e211509eb17f6c3b1f81cc01cb  capture.js
2cc660155a76d4a3150cd3b8e8ddadbdeb6ee24ca1436d21ce025d9ef5275462  content.js
822518955b20f7db9a3a7b6b9c8a79a3c8906fec6af486882d7c2c092b182df7  crusher.js
ee19224a36b2bbd2c6e12ddce7918cb8aed1549552e80ecb5e7c51f86c79de58  fence.js
02ea08c0e97e918168a3eacfec6baf140d71ca5befa9dd2dbb018aefd68ee467  identity.js
b5b70290ce8f9c7d53a49aab0ac395415431d0004769580ae16cd650d242b89f  ledger.js
2b5d766243f5f3499a2c3c03ddd0544727c0d56ec52d6a2ef88a844db3fa9622  letterbox.js
07bac44f143f8426d817ffd8f0fcdc3e55c33cfd0b0334a61c2306370f0441ec  manifest.json
f68fa341b9b2302e395f536a7bc4ba0fd3ab3f6ebae3f32e88d2873ee3c57538  migration.js
46ac00fd39293014d2a5e6317d0ef5ab0371eeefee81abc4a5e1b912a0f4557a  popup.html
dcd49e8a83ffef3953754fb17b0a93ed5d9a892430614ec3ca9c552e763711f2  popup.js
c54a99415f7c37d135baa293ca808db9cf3412106387785483bf109b05724d05  protocol.js
40aa6ac785a11b78313cfc19442f076b3d2c2698de1424d765038a2dc4445486  sendcore.js
14d1cc6fb008fee7a684d903876c606eb5e0778f3bce8c340025eb544714b0d4  stage1-wiring.js
783fdeb6ff531d114738c094838f43d5ef75a8331253404652e4288bde8b10ee  stage1core.js
63dfc79ca97863f6559b9156e2a1a2fb7c0cabc41e1e50613bc56f30f611e348  storage.js
da1537fa0914f8c0c299577d5520e5974882a1e82f29855e430b645559ef0959  witness.js
12080f1976317cfa08b6bcae736706e26f96ccf69d9ead1ccfd2f450c9805887  tests-stage1/batch3.fixtures.js
c60eb3050384e61b6586a9e62f1219657ae7d3ac34ed4ef5a4f8d6b6f509c9fc  tests-stage1/delivery.fixtures.js
252a64b6f191b152b465fe4b3ccb7d0a3fd5de10e0eaae4b5a3e83ccc832039a  tests-stage1/identity.fixtures.js
cd2e781a71b7d490f8f796ff6d0c75907da13017ad1d92e78b447070bc9a92a4  tests-stage1/ledger.fixtures.js
```
