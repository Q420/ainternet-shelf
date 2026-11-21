# CONCLUSION BUILD — SCOPE 03 (Pulse Bridge v0.22.0)

Status: DRAFT for Ben's build tap. Supersedes CONCLUSION-BUILD-SCOPE-02.md in full; Scopes 01 and 02 remain on the shelf as the reviewed record.

Review chain: Tansy's blind review of Scope 01 (OBJECT WITH CORRECTIONS, F1–F5) → errata E1–E5 → Scope 02 → Claude's closing check of Scope 02 (PB-ID pb-mwdcl9hy, OBJECT WITH CORRECTIONS: errata verified accurate with one citation slip; gaps G1–G3). Remmy re-verified the gaps and the slip against the source before writing this scope: G1 confirmed (background.js 426–427 returns {accepted:false, reason:"duplicate"}, indistinguishable from a rejection), G2 confirmed (forgetDetection, 101–107, deletes the fpToId/seenIds entries the intake duplicate check reads), citation slip confirmed (the wasUnconfirmed → DELIVERED-LATE logic is pbStationHandshake in station.js 165–171; storage.js 234–247 is its call site). G3 is a candidate; this scope answers it by coverage rule rather than by probes. Change map at the end.

Basis (read at its pin, per the Build Law): BRIDGE-PLAN-JOINT-DRAFT-01.md at blob 4fe7bf58 (ruled-in text). Parent: the delivered v0.21.0 build; source tree shelved at bridge/combined-build/source/ (37 files, hash-matched). The build starts from that tree, copied fresh.

Spine: **a conclusion must not outlive its evidence.**

## The retained handle (shared by Parts 2, 3 and 4)

When a pair closes, before the forget loop runs, the closing letter leaves a handle in a new persisted store (`state.handles`, background-owned):

- message_id (the PB-ID — the record's key)
- from / to (seat pair)
- body (the letter's full text as carried — the late look matches on this; the PB-ID itself is not observable on any page)
- fingerprint (the carried body's fingerprint)
- closedAt, closeState (ACKNOWLEDGED or UNVERIFIED), closeReason

Capacity disposition (convene spec §1.3 — every bounded store states one): the store holds the most recent 300 handles, the same order as PB_MAX_SEEN. Eviction of the oldest handle is LOGGED, never silent. Named consequence, accepted in advance: a supersede, an exact re-sighting or a late look arriving after its handle was evicted behaves as the current build does — bounded memory with its failure mode on the label. ABANDONED letters keep their existing permanent treatment and do not consume handle slots. The delivered ledger is untouched; the handle is a pointer-rich shadow, not a second ledger.

## The six parts, in build order

Each part lands with its fixtures green before the next part starts. Fixture counts are reported exactly. Nothing is reported live until Part 6 closes.

### Part 1 — P3: the receipt rename

The SENT-UNCONFIRMED face becomes words that state only what is known. Candidate wording (Claude's): "clicked; receipt not yet observed." Acceptance: a case-insensitive sweep for "unconfirmed" across the built tree; EVERY hit is classified in the build record as Ben-facing (its wording moves in this part) or internal (state keys, comments — they stay). Known Ben-facing hits at scope time: background.js 268, 273, 1041, 1193, 1780; popup.js 76, 103, 135, 182; station.js 171. The internal state key does not change.

### Part 2 — P2: no silent exit (the detection send)

New surface (this part ADDS machinery; it does not merely rewire):

- A letterbox acknowledgement hook: onHandoff gains an answer. The background replies to every pb-detection with one of FOUR answer classes:
  - **accepted** — the letter is recorded; the letterbox marks it handed off.
  - **duplicate, already recorded** — TERMINAL (errata G1). The letter is already in the background's record; the letterbox marks it handed off and does NOT retry. A duplicate answer also writes a re-sighting log line.
  - **rejected** (with reason — unregistered tab, malformed) — NOT handed off; retryable.
  - **unanswered** (no reply arrives) — NOT handed off; retryable.
- Handed-off marking happens on accepted and duplicate-terminal answers only. Rejected and unanswered detections retry on a bounded schedule; a final failure writes a log line AND a panel-visible note.
- The intake side gains the matching wiring (errata G2): before accepting, intake consults the handle store — an exact re-sighting of a COMPLETED letter (fingerprint or message_id matches a handle) answers duplicate-terminal from the handle, so completed letters keep a background-side duplicate authority after the forget loop has run. Live detections and in-flight letters are unaffected.
- The pb-capture-drop reports ride the same acknowledged path.
- The letterbox pending map's cap eviction (letterbox.js 732–745, silent today) is reported via the drop channel — no eviction without a record.

Acceptance includes the named surfaces from the plan: the baseline-drop report (popup log) and the intake rejection (background log, 413–415) must each be shown to reach a surface Ben reads — verified in Part 6, not assumed here. Fixtures: detection into an unavailable background surfaces and retries; a rejected detection is never marked handed off; a duplicate answer is terminal — marked handed off, zero retries, re-sighting logged; an exact re-sighting of a completed letter after pair close answers duplicate-terminal from the handle store; a drop-report failure is itself reported; a pending-cap eviction leaves a record.

### Part 3 — P1: the completed-letter tombstone

Consumes the retained handle. A supersede arriving whose supersedesFingerprint matches a handle with closeState ACKNOWLEDGED or UNVERIFIED does NOT route as a new letter: it surfaces as a visible growth notice — "this letter grew after completion" — showing the added text (new body minus the handled body), with carry-or-dismiss as Ben's explicit control, never automatic. Supersedes of letters still in flight (no handle — pair not closed) are unchanged, as are supersedes matched to a live detection (the existing fold). Fixtures: completed letter + post-completion growth folds to a notice, no second delivery; in-flight growth still carries; handle survives a simulated restart and the fold still works; carry and dismiss each do exactly what Ben chose; a supersede against an EVICTED handle routes as new and the log says the handle was gone.

### Part 4 — P4: late re-observation (upgrade only)

Consumes the retained handle. For handles with closeState UNVERIFIED, a bounded second look runs on a stated schedule (first look at pair close + 60 s, then every 60 s, ending at + 10 min): the destination tab's adapter is asked whether the handled body is now observable as a settled turn; matching is on the retained body (normalised comparison), never on the PB-ID. A match moves the letter UNVERIFIED → DELIVERED-LATE — feeding the station handshake that already speaks DELIVERED-LATE (station.js 165–171) — and logs the upgrade with the observation time. No path from the late pass to a send exists or is created; the pass cannot retry delivery, only revise the verdict. At the bound, the letter rests UNVERIFIED under Part 1's honest wording.

Coverage rule (errata G3 — answered by rule, not by new probes): the re-look REUSES each adapter's existing settled-turn observation — the same observation the receipt-verdict polling already runs — re-queried later; no new observation machinery is invented per platform. Per-platform coverage is established by fixture proof at build time and NAMED in the build record as COVERED or NOT COVERED. A platform whose existing observation cannot be re-queried standalone is NOT COVERED in v0.22.0: its letters rest at Part 1's honest wording, and the build record says so by name. No live platform probes are run before dispatch; live qualification of covered platforms runs in Part 6. If NO platform proves coverable by fixture, Part 4 does not ship a shell — it reports back and the part is re-scoped.

Fixtures: a letter confirmed after its window closed upgrades and shows the change; the pass cannot trigger a send under any fixture; the pass ends at its bound; an evicted handle ends its pass early, logged; each adapter's re-look is fixture-proven or the platform is named NOT COVERED.

### Part 5 — P5: log the overlay refusal

When host election refuses Ben's push-through or append ("not the acting station"), the refusal writes a log line and a panel-visible note naming the action refused and why. No other host behaviour changes. Fixture: a refused action leaves both traces; an allowed action is unchanged.

### Part 6 — P6: the verification pass (acceptance gate, not code)

Before anything is called fixed or live: Ben's screen, the popup log and the background log are read against one letter of each fault class (F1 duplicate, F2 lost reply, F3 receipt wording). Log-written versus panel-shown is settled per class, on his real flow. This pass is also where the two open discriminators close or stay named: which version was loaded during the 2026-11-11 test, and which F2 loss point fired that night. Known carried limit, stated now: the identity gate from v0.21.0 is unchanged by this build — no platform has qualified for managed registration, so live active-send acceptance remains bounded exactly as the v0.21.0 house report states.

## Exclusions (from the plan, binding)

No decoration-blind comparison. No station or fence redesign — Part 5 adds a log line at the refusal point only; Part 4 consumes the existing DELIVERED-LATE machinery only. No adapter rewrites beyond the Part 4 re-look reuse. No change to the in-flight growth rule. Alex's reviews ride along when Ben triggers him; they inform and do not gate this line (Ben, 2026-11-12).

## Change map

- Scope 01 → 02: errata E1–E5 (retained handle; Part 2 ack hook named as new surface; Part 1 classified sweep; capacity disposition; basis pin corrected).
- Scope 02 → 03: **G1** — Part 2 gains the four-class answer taxonomy; duplicate is terminal, never retried. **G2** — intake consults the handle store; the handle is the background-side duplicate authority for completed letters (Part 2 wiring + Part 3 header). **G3** — Part 4 gains the coverage rule (reuse of existing settled-turn observation, fixture-proven per platform, NOT COVERED named, no pre-dispatch probes, no shell ships). **Citation** — wasUnconfirmed logic cited to station.js 165–171; the Scope 01 errata's storage.js citation is corrected here and stands corrected in this chain (the errata file itself is the historical record and is not rewritten).

## Dispatch

Claude's closing position on Scope 02: fix G1–G3 and the citation, then dispatch. Those fixes are this scope. Ben's tap on the build scope card dispatches implementation, package v0.22.0.
