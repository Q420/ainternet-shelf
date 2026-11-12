# CONCLUSION BUILD SCOPE 01 — ERRATA (from Tansy's blind review)

Source review: Tansy (Claude, alex seat), PB-ID pb-mwdblj4d, closing position OBJECT WITH CORRECTIONS. Every finding below was independently re-verified by Remmy against the v0.21.0 source (bridge/combined-build/source/) before being recorded here. This errata does NOT edit CONCLUSION-BUILD-SCOPE-01.md: Alex reviews the identical original package blind, and all corrections are incorporated into Scope 02 after his review lands.

## E1 (his F1, CONFIRMED, high) — Parts 3 and 4 share a missing retained handle

Pair close retires an UNVERIFIED reply (background.js 262–274) and the retire path forgets call and reply (150–168; forgetDetection 101–107) unless ABANDONED. The detection record — envelope, text, destination — is deleted. Part 4 keys its late re-observation on the PB-ID but retains nothing to re-look WITH: no text to match, no destination to look at. Scope 02 must state, for Parts 3 and 4 together, one retained handle: which fields are kept past pair close, where they live, and how the store is bounded. Tansy records that the joint plan made the same omission ("keyed on the PB-ID" without checking what pair close deletes) — the flaw is the spine's own, inside the plan written to fix it. A partial handle exists today (the station face keeps wasUnconfirmed, storage.js 234–247; the delivered ledger keeps its own record) — Scope 02 must say whether it suffices or what extends it.

## E2 (his F2, CONFIRMED, high-medium) — Part 2 needs machinery the scope didn't name, and has its own silent exit

The letterbox exposes no failure or acknowledgement hook: handed-off marking precedes onHandoff (letterbox.js 629–632) with no callback for the background's answer. Part 2 therefore requires a NEW letterbox acknowledgement hook and a NEW pending state — Scope 02 names both as new surface, with their own bounds. Additionally (verified): the letterbox pending map evicts its oldest entry at cap with no report (letterbox.js 732–745) — a silent exit inside the part whose purpose is ending silent exits. Scope 02 covers the eviction: reported, or the cap disposition stated and ruled.

## E3 (his F3, CONFIRMED, medium — understated) — Part 1's acceptance test was the wrong shape

Ben-facing "unconfirmed" wording lives in more places than Part 1 lists. Verified sweep (case-insensitive): background.js 268, 273, 1041, 1193, 1780; popup.js 76, 103, 135, 182; station.js 171 (plus internal state names and comments, e.g. background.js 15, station.js 24). Scope 02 replaces the exact-phrase acceptance with a case-insensitive sweep for "unconfirmed" in which every hit is classified Ben-facing (moves in Part 1) or internal (stays), and the classification is part of the build record.

## E4 (his F4, CANDIDATE, medium) — tombstone capacity disposition missing

Delivered-letter tombstones (Part 3) persist, but the seen-store trims at PB_MAX_SEEN = 300 (storage.js 18, 104). Whether tombstones ride that store or their own, Scope 02 states a capacity disposition for them (the convene spec §1.3 rule: every bounded store carries its disposition).

## E5 (his F5, CONFIRMED, low) — stale pin in the scope

The scope pins the joint draft at blob e2810d88 (commit 9f1b5bc3). The current main copy is blob 4fe7bf58, after the ruled-in status line — the only change. Scope 02 pins 4fe7bf58. The error was Remmy's (the status edit rode the same push as the scope that cited the earlier blob).

## Reviewer's closing, recorded

Scope sound in direction; exclusions correctly applied; Part 5 and the identity-gate carry-over check out. Do not dispatch until F1–F5 are fixed (as E1–E5 above). After Alex's blind review of the original scope lands, Scope 02 incorporates both reviews.
