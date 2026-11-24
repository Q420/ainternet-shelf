# Retrieval implementation — exact revision manifest (2026-11-23)

Supplied at Vane's request (INDEX 251) so the implementation is examined from the record, not from reports. **Implementation shelf commit: `47934af024531ad8874f1236b4408fbc7a7b5fb8`** (Q420/ainternet-shelf, main). Blob = git blob SHA-1 of the file as shelved at that commit; sha256 = the file's SHA-256.

| Path (under collaboration-framework/) | Blob | SHA-256 |
|---|---|---|
| src/framework/tool_policy.py | 30aff4861569f6ac4109f9b830e1914e108a29db | e0a22212c027c86808c4a3ede70305a0fc6f5a5d47e4ee0d8376af5264920e84 |
| src/checker/tool_policy.py | 23e396a941beac9f2b373b9842a6872163255c02 | c21e26b85ccd47a0c1a4c57f7430f68fa8b2de31f9f25239f27c3fcd3dffd8f2 |
| src/framework/doorway.py | 9492a0d7d064861aab29d224cbc207abbebea34c | de22134348ede76f9552881b0a8f077a8ce66723220e6246aabcd55fa185225c |
| src/framework/generator.py | e9879b08a0722987b48ca97b05a90b8004c975c9 | d3356f056ea0c3af338ae2a4509e649c9066e43261cb50e2dfc3f1bb5a6cbdb2 |
| src/framework/executor.py | 2c636d1aed2b91cb5ea4a76ce174061907dbe54e | 92748b66780c40b671f08b63bfc4a77acb667a3e0ea4c9177440153a2b660376 |
| src/framework/loop.py | 2a5a5311a7d55b59966673b7e9b44c334ad82632 | 8f2406ab0c89a74d8ebd6ade50dbab2e9cc47f1701fccf222e546586149c7806 |
| src/checker/checker.py | 05dbc5070439e7bb6745255a08a8850fefb604e0 | 40644e10be1e47063007daff7a2d24959836570d4f0ff6e81788572fdee67d12 |
| tests/unit/test_piece_retrieval.py (witness suite, 56 checks) | 0047cfc437b3faee90774d0173ebaebf04d586f7 | 93d46ae1d5084ac6fb00cc0481fc28dd675db0ba40be58ff055189606861d43c |
| live-demo/retrieval-r5-measurements.json | 6762befdb7e5ef38a900dde0fe8fed16764a1520 | 6863b8e6a6f18f2a6f8b851fd42cc6065520c945f3f5f86b345a175d951a76bd |
| live-demo/package-breakdown-attempt6.json (INDEX 247) | 157bb947c13ee2b979225ba53c52f61474ce5103 | 835edd6730ac62a3030bc84801c1cecf6565f3e53145ade9c32eeef3b346301f |

Governing scope: RETRIEVAL-SCOPE-2026-11-23.md at Rev 5 — blob a1ac33901be4466d7c29555a7a2a8f0d7a41d504, sha256 e031cb2c1f29eb350e4b7c19837f188fa790158688be0767e57a1dfd5ee8c8af.

**Authorisation of record for the build (named at Vane's INDEX 251 correction):** Ben's direction, tap + words, 2026-11-23 (INDEX 236: pull structured access forward), executed under the standing Remmy–Vane loop authorisation (Ben, 2026-11-21/22) by which pieces build on the examiner's scope pass, and shaped by his stop-and-analyze order (INDEX 245) and the joint analysis (INDEX 246). Vane's acceptance (INDEX 249) examined and passed the design's technical direction; it did not authorise the build, and this record does not treat it as doing so. Attempt 7's release remains Ben's.
