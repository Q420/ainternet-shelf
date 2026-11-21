# Combined Build Scope — Amendment 01

**Amends:** bridge/COMBINED-BUILD-SCOPE-01.md (commit 73c77e3b), which stands otherwise unchanged.
**Source:** Alex's Combined Build Pre-Build Review 01 (commit af54a3f7, blob 875e9bd6), all nine items assessed by Remmy against the governing record. Items 1, 2, 5, 7, 8 are recorded boundaries; items 3, 4, 6 add or pin scope content the original scope abbreviated; item 9 is discharged by the companion parent manifest.
**Authority:** Ben's combined-build go (2026-11-11 20:54 PST) covers the Correction Basis and Build Plan whole; this amendment restores basis content the combined scope summarised too thinly. It widens nothing beyond those governing documents.

## Item 1 — Identity qualification is an acceptance limit (recorded)

Stage 0 stands: no platform is qualified for managed registration (ChatGPT UNKNOWN; Muse candidate-only). The combined-build go does not lift that gate and authorises no identity probes. The build proceeds on generic infrastructure, fixture-verified; live sending stays fail-closed for unqualified platforms. **Consequence for Part D acceptance:** the combined live walk's active-send elements cannot honestly pass until a platform qualifies through a separately authorised route. The delivery house report will state the walk outcome in exactly those terms if the gate still stands at walk time.

## Item 2 — Station host architecture is a Part C entry condition (recorded)

Before any station code: a short station-host design note, reviewed by Alex (his offered slice, sequenced after the composer cross-check), settling: Ben's actual physical layout; ONE authoritative actionable station host; the timer/append-lock owner; how the other seat's surface mirrors acknowledged state without becoming a second actionable station. The background remains authoritative; every surface renders acknowledged state only. Two page overlays are not one station, and shared background state does not make them one.

## Item 3 — Reset preservation is Part A scope (ADDED)

New Part A item 8: **pb-reset must not silently erase the permanent Stage 1 record.** Reset clears connections, registrations and the active pair as today, and rotates detection tokens — but it PRESERVES state.stage1's permanent record: the ledger export, the epoch export with its history, acknowledgements, the unreconciled record, and the migration inventory. A truly destructive reset is not in this build; if ever required it needs its own explicit owner disposition with stated consequences and recovery handling. Regression required: after a reset, old tokens are revoked (admission rejects them) AND the permanent record is intact (ledger/epoch read back equal).

## Item 4 — Append contract pinned (Gate 4 §4.4 is governing)

Stage 0 Pack §4.4 is a governing input to Parts B and C, in full: Option A length-framed `PB-APPEND/1`; one Ben segment per message per window; committing the append sends; segment preserved byte-for-byte including leading/trailing whitespace (all-whitespace rejected as empty, never rewritten); same PB-ID and same Index ID with distinct attribution; both directions; segment serialises after the complete original payload and before the F-6 trailer; original digest retained as provenance. Any trimming behaviour from the earlier page sketch is expressly excluded. Exact-byte and serialization fixtures are required (the Part B completeness suite carries them).

## Item 5 — History parity precedence (Ben's requirement governs)

Part D's history requirement **overrides Build Plan §5.9** wherever the two conflict — Ben's newer, explicit requirement governs over the plan's earlier "no completed-receipts list" line. The display is defined as: ONE shared authoritative exchange history — the bridge's detection/lifecycle record (detections with their states, Stage 1 acknowledgement outcomes and Index IDs) — rendered identically from either seat's popup, from the same background state. Not two local histories, not a second ledger. Terminal records shown: every detection's final state (delivered / failed-before-send / sent-unconfirmed / held / cancelled / stale-rejected), with its number.

## Item 6 — Cancel defined at the dispatch boundary (ADDED definition)

Cancel is a per-item OWNER lifecycle disposition, labelled **Cancel**, distinct from the station's discard disposition for terminal records. It names one PB-ID / Index ID / attempt and is recorded as a lifecycle event against that identity; the permanent record is retained. It prevents dispatch **only if it lands before the actual submit** (before TRANSIT begins). Once the adapter has submitted, cancel cannot recall anything: the surface reports the true state (in transit / sent-unconfirmed / delivered) and never claims a recall. Required fixtures: cancel-before-submit (no dispatch, event recorded), cancel/dispatch race (exactly one winner, honestly reported), duplicate cancel (idempotent, second is a no-op record), post-dispatch cancel (too late — true state reported).

## Item 7 — Full regression sets govern (recorded)

Part A acceptance requires the Correction Basis §5 set in full, not the abbreviated examples in the combined scope: no-token/no-arming; every binding mismatch; registration-generation invalidation; reset preservation (item 3); both worker-restart outcomes; import failure; read-back mismatch; idempotent recovery; reusable current-generation tokens; clean-room builder reproducibility. The combined live walk retains the Stage 2/3 acceptance points: manual-composer isolation; one singular station across both seats; station movement + position persistence; travel direction; append timer + original-byte preservation; one allowed and one blocked push-through; honest HOLD versus LOGIC-FAULT; owner-review disposition. Animation indicates progress only — it never evidences delivery.

## Item 8 — Entry gaps stand (recorded)

Gate 6 (exact snippet, or Ben's explicit not-applicable) and F-7 (no probes; per-platform source evidence + disposition; excluded platforms named, never reported as active-send supported) remain gates exactly as the combined scope states them.

## Item 9 — Parent pinned

Discharged by bridge/COMBINED-BUILD-PARENT-MANIFEST-01.md (v0.19.1 tree, per-file SHA-256, ZIP SHA-256, four-file diff vs v0.19.0).

## Alex's independent slices (accepted, sequenced)

1. **Platform composer-evidence cross-check — first** (Part B's lease/submit work depends on its exclusions).
2. **Station-host architecture review — second** (Part C entry condition, item 2).
