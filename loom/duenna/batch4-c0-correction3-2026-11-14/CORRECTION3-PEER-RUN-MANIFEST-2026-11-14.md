# CORRECTION 3 — FIVE-RUN PEER EVIDENCE MANIFEST (2026-11-14)

Prepared for Alex's evidence-manifest inspection (his F-3
Correction 3 review, pb-mwgk6fzc-g-f26a / pb-mwgk3tgx-b-d8xy:
the two code findings PASS; clearance held only on his
independent check of the five-run evidence). No code change.

All five logs live in this bundle directory:
duenna/batch4-c0-correction3-2026-11-14/ (commit 221d7df5).

| Run | Path | SHA256 | Started (header, in-room UTC) | Result |
|---|---|---|---|---|
| 1 | duenna/batch4-c0-correction3-2026-11-14/corr3-peer-1.log | fb6e6ce13f66111bb4a96486c728ebdffb373e8abd65a2cff90dfc258bef1d7b | 2026-11-14T15:21:20Z | peer: 166/166 PASS |
| 2 | duenna/batch4-c0-correction3-2026-11-14/corr3-peer-2.log | a32371d3ca03a3eda44740eb33ba13a37a578703b0b4d59977dc77e50a41f103 | 2026-11-14T15:21:36Z | peer: 166/166 PASS |
| 3 | duenna/batch4-c0-correction3-2026-11-14/corr3-peer-3.log | e99fdd67012c4e254bcebce00f1ffe00b4406f2da65b2182da281a11c3454be0 | 2026-11-14T15:21:52Z | peer: 166/166 PASS |
| 4 | duenna/batch4-c0-correction3-2026-11-14/corr3-peer-4.log | 3c2217948eb7c986be1042401e2bf9e847bd9ef50ebdd2113265306fb3baa814 | 2026-11-14T15:22:09Z | peer: 166/166 PASS |
| 5 | duenna/batch4-c0-correction3-2026-11-14/corr3-peer-5.log | 11dc74798b9589b662ea6ec525e1aeb6c7d4b8176ead6378c36d9eb7d0a2183f | 2026-11-14T15:22:24Z | peer: 166/166 PASS |

Notes:
- Five distinct SHA256 hashes for five distinct artefacts.
- Every log's header records the same build under test:
  launcher.c sha256 001543f39b4d557f1bd157209a316c38104d4f7f37a42b6fab8ad664894de0de
  (the launcher-c3.c pin) and test_launcher.py sha256
  8570cea5e44d63e43470e29e6e25dfac804881eaa77e442219a0025f1a3ebf80
  (the test_launcher_c3.py pin).
- Wall times from the runner console: 16 s, 16 s, 16 s,
  15 s, 16 s.
- The in-room WSL clock runs about one hour ahead of the
  wall clock (the 15:21Z headers are ~14:21 UTC); the
  timestamps are reproduced as recorded in the artefacts.
