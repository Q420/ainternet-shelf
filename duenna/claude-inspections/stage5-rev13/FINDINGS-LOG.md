# Independent inspection — STAGE5-BUILD-SPEC-13 (pin bab720b2, sha256 ebefa4a1…)
Package: /mnt/user-data/attachments/475f6377-dfad-5672-a7f4-a435c6bdea33/581de8c8-attachment.txt (4105 lines)
Inspector: Claude (independent; not builder). Verdict returns via Ben, unedited.

## Coverage
| Lines | Content | Status |
|---|---|---|
| 1–133 | Part 1 commission; Part 2 header/status | READ |
| 134–1023 | Rev 13/12/11/10/9/8/7 amendment summaries (history) | READ (skimmed for changes) |
| 1024–4105 | Remainder: spec body §§1–7, gates, batches | NOT YET |
| 3469–3515 | §3.7 adapter boundary incl. Rev 13 correction | READ |
| 3691–3730 | §5 G1 incl. Rev 13 widening | READ (partial) |
| 3885–3905 | §6.3 item 2 mirror | READ |

## Findings so far
(none raised yet — Rev 13 correction checked: present, consistent across §3.7, §5 G1, §6.3 item 2)

## Points to test in the full read
- §3.7(a): does the loopback check cover hostnames resolving to non-loopback addresses, or only literal IPs?
- G1 zero-egress: is isolation required for the whole build, or only as measured at gate time?

## Hash verification against shelf clone (commit 0124a20; pins from spec §2.2 / §2.3)
- STAGE5-BUILD-SPEC-13.md sha256 ebefa4a1… MATCHES pin.
- S3 HARNESS-DESIGN-03 b0fca125… MATCH. S4 ADAPTER-DESIGN-03 5be7eb0e… MATCH.
- S5 ACCEPTANCE-CRITERIA-04 7608d74e… MATCH. S6 INTERPRETATION-NOTE-01 94d40cc7… MATCH.
- S7 V2-QUALIFICATION-01 6ae47780… MATCH.
- §2.3 rows 2–7, 11, 12 (V2-PACKAGE, PROCESS-TREES, tools.py, demo_tools.py, DEMO-RESULTS.json, run_ab.py, MANIFEST.md, QWEN-AB-EVIDENCE-MANIFEST.json): all MATCH.
- S10 NOTE-20261112-duenna-flow-both.md: NOT IN CLONE — unverified.
- rows 8–10 (EXTERNAL corpus files): outside shelf — unverified by me.

## FINDING F1 (Medium) — S1 plan pin does not match the plan text it describes
- §2.2 S1 pins sha256 2449c259… and 7,497 B. Shelved NEMOTRON-PILOT-PLAN-01-DRAFT.md is 8,205 B, sha 743e7dd4….
- PILOT-MANIFEST-01 row 1 says the pinned file is "local (not on the shelf)" at ~/workspace/duenna-letters/, pinned at ADOPTED state (16:42 MST).
- The shelved file adds the 2026-11-12 16:45 MST index amendment (lines ~142–153), appended after adoption.
- Spec §2.2 S1 describes the pin as recording that index amendment. The hash/size pin cannot cover both. Either the pin is stale, or the description is wrong.
- Effect: the build's governing-plan pin is unverifiable from the shelf and internally inconsistent. Index read-only rule is load-bearing for §2.3 rows 8–10.
- Recommended disposition: re-pin S1 to the amended shelved bytes (or pin both states explicitly) and place the pinned bytes on the shelf.

## Coverage update
- Read: §1 (1697–1763), §2 (1765–1858). Remaining normative: §3 (1861–3518), §4 (3519–3680), §5 (3681–3813), §6 (3814–3963), §7 (3964–4015), Parts 3–4 (4038–4105).
