# CONCLUSION BUILD — SCOPE 02 (Pulse Bridge v0.22.0)

Status: DRAFT for Tansy's closing check, then Ben's build tap. Supersedes CONCLUSION-BUILD-SCOPE-01.md in full; Scope 01 remains on the shelf as the reviewed record (Alex may still review it whenever Ben triggers him — his spot-checks ride along, they do not gate this line).

Basis (read at its pin, per the Build Law): BRIDGE-PLAN-JOINT-DRAFT-01.md at blob 4fe7bf58 (ruled-in text) — pin corrected per errata E5. Review record: Tansy's blind review of Scope 01 (PB-ID pb-mwdblj4d, OBJECT WITH CORRECTIONS, findings F1–F5) and its errata (bridge/CONCLUSION-BUILD-SCOPE-01-ERRATA.md, E1–E5, each re-verified by Remmy against the source). This scope weaves E1–E5 in; the change map is at the end.

Parent: the delivered v0.21.0 build. Source tree shelved at bridge/combined-build/source/ (37 files, hash-matched by Tansy). The build starts from that tree, copied fresh.

Spine: **a conclusion must not outlive its evidence.**

## The retained handle (NEW — shared by Parts 3 and 4; errata E1)

Both the tombstone and the late re-observation need something pair close currently destroys. This build therefore introduces ONE retained-handle store first, and Parts 3 and 4 both consume it.

When a pair closes, before the forget loop runs, the closing letter leaves a handle in a new persisted store (`state.handles`, background-owned):

- message_id (the PB-ID — the record's key)
- from / to (seat pair)
- body (the letter's full text as carried — the re-look matches on this; the PB-ID itself is not observable on any page)
- fingerprint (the carried body's fingerprint)
- closedAt, closeState (ACKNOWLEDGED or UNVERIFIED), closeReason

Capacity disposition (convene spec §1.3 — every bounded store states one): the store holds the most recent 300 handles, the same order as PB_MAX_SEEN. Eviction of the oldest handle is LOGGED, never silent. Named consequence, accepted in advance: a supersede or a late look arriving after its handle was evicted behaves as the current build does (supersede routes as new; late look finds nothing) — bounded memory with its failure mode on the label. ABANDONED letters keep their existing permanent treatment and do not consume handle slots. The delivered ledger is untouched; the handle is a pointer-rich shadow, not a second ledger.

## The six parts, in build order

Each part lands with its fixtures green before the next part starts. Fixture counts are reported exactly. Nothing is reported live until Part 6 closes.

### Part 1 — P3: the receipt rename

The SENT-UNCONFIRMED face becomes words that state only what is known. Candidate wording (Tansy's): "clicked; receipt not yet observed." Acceptance (errata E3 — replaces Scope 01's phrase search): a case-insensitive sweep for "unconfirmed" across the built tree; EVERY hit is classified in the build record as Ben-facing (its wording moves in this part) or internal (state keys, comments — they stay). Known Ben-facing hits at scope time, from the verification sweep: background.js 268, 273, 1041, 1193, 1780; popup.js 76, 103, 135, 182; station.js 171. The internal state key does not change.

### Part 2 — P2: no silent exit (the detection send)

New surface, named per errata E2 (this part ADDS machinery; it does not merely rewire):

- A letterbox acknowledgement hook: onHandoff gains an answer. The background replies accepted or rejected (with reason) to every pb-detection; the letterbox holds the letter in a new PENDING-ACK state until the answer arrives.
- Handed-off marking moves AFTER an accepted answer. A rejected or unanswered detection is NOT marked handed off; the letter stays eligible, retries on a bounded schedule, and a final failure writes a log line AND a panel-visible note.
- The pb-capture-drop reports ride the same acknowledged path.
- The letterbox pending map's cap eviction (letterbox.js 732–745, silent today) is reported via the drop channel — no eviction without a record.

Acceptance includes the named surfaces from the plan: the baseline-drop report (popup log) and the intake rejection (background log, 413–415) must each be shown to reach a surface Ben reads — verified in Part 6, not assumed here. Fixtures: detection into an unavailable background surfaces and retries; a rejected detection is never marked handed off; a drop-report failure is itself reported; a pending-cap eviction leaves a record.

### Part 3 — P1: the completed-letter tombstone

Consumes the retained handle. A supersede arriving whose supersedesFingerprint matches a handle with closeState ACKNOWLEDGED or UNVERIFIED does NOT route as a new letter: it surfaces as a visible growth notice — "this letter grew after completion" — showing the added text (new body minus the handled body), with carry-or-dismiss as Ben's explicit control, never automatic. Supersedes of letters still in flight (no handle — pair not closed) are unchanged, as are supersedes matched to a live detection (the existing fold). Fixtures: completed letter + post-completion growth folds to a notice, no second delivery; in-flight growth still carries; handle survives a simulated restart and the fold still works; carry and dismiss each do exactly what Ben chose; a supersede against an EVICTED handle routes as new and the log says the handle was gone.

### Part 4 — P4: late re-observation (upgrade only)

Consumes the retained handle. For handles with closeState UNVERIFIED, a bounded second look runs on a stated schedule (first look at pair close + 60 s, then every 60 s, ending at + 10 min): the destination tab's adapter is asked whether the handled body is now observable as a settled turn; matching is on the retained body (normalised comparison), never on the PB-ID. A match moves the letter UNVERIFIED → DELIVERED-LATE — feeding the station face that already speaks DELIVERED-LATE (storage.js 235–247) — and logs the upgrade with the observation time. No path from the late pass to a send exists or is created; the pass cannot retry delivery, only revise the verdict. At the bound, the letter rests UNVERIFIED under Part 1's honest wording. Fixtures: a letter confirmed after its window closed upgrades and shows the change; the pass cannot trigger a send under any fixture; the pass ends at its bound; an evicted handle ends its pass early, logged.

### Part 5 — P5: log the overlay refusal

When host election refuses Ben's push-through or append ("not the acting station"), the refusal writes a log line and a panel-visible note naming the action refused and why. No other host behaviour changes. Fixture: a refused action leaves both traces; an allowed action is unchanged.

### Part 6 — P6: the verification pass (acceptance gate, not code)

Before anything is called fixed or live: Ben's screen, the popup log and the background log are read against one letter of each fault class (F1 duplicate, F2 lost reply, F3 receipt wording). Log-written versus panel-shown is settled per class, on his real flow. This pass is also where the two open discriminators close or stay named: which version was loaded during the 2026-11-11 test, and which F2 loss point fired that night. Known carried limit, stated now: the identity gate from v0.21.0 is unchanged by this build — no platform has qualified for managed registration, so live active-send acceptance remains bounded exactly as the v0.21.0 house report states.

## Exclusions (from the plan, binding)

No decoration-blind comparison. No station or fence redesign — Part 5 adds a log line at the refusal point only; Part 4 consumes the existing DELIVERED-LATE face only. No adapter rewrites beyond the Part 4 re-look query. No change to the in-flight growth rule. Alex's outstanding v0.21.0 package review is a separate track and is not discharged by this scope; per Ben (2026-11-12), Alex spot-checks repo changes when Ben triggers him — his reviews inform, they do not gate this line.

## Change map (Scope 01 → Scope 02)

- E1 → the retained-handle section; Parts 3 and 4 rewritten on it.
- E2 → Part 2 names the acknowledgement hook and PENDING-ACK state as new surface; pending-cap eviction covered.
- E3 → Part 1 acceptance is a classified case-insensitive sweep.
- E4 → the handle store carries its capacity disposition (300, logged eviction, named consequence).
- E5 → basis pin corrected to 4fe7bf58.
- Parts 5 and 6 unchanged in substance (Tansy: Part 5 and the identity-gate carry-over check out).

## Dispatch

Tansy's closing check on this scope (does it answer F1–F5?) → corrections if any → Ben's tap on the build scope card dispatches implementation, package v0.22.0.
