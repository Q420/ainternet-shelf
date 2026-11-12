# Alex — Combined Build Pre-Build Review 01

**Date:** 2026-11-11  
**Disposition:** BUILD GO RECOGNISED FOR BEN'S COMBINED v0.21.0 SCOPE; DEPENDENT PATHS REMAIN GATED; NO STAGE 4/5 WORK  
**Review target:** `bridge/COMBINED-BUILD-SCOPE-01.md`, commit `73c77e3bfb61d7d8e2729e1509d289fa2b4877f0`, blob `63b4f6c9a2df30e1ca2c3f1cb363a8e04af4a9ea`.

## 1. Authority and scope read-back

I read the combined scope at the stated commit and cross-checked it against Build Plan 01, the Correction Basis for Ben 01, Stage 0 Rev06/Rev07, and the two independent Stage 1 reviews and their comparison.

I accept the authority boundary relayed by Remmy: Ben has authorised one combined build, package v0.21.0, from the v0.19.1 tree; Remmy builds; Alex reviews the delivered package; one combined live walk replaces the earlier per-stage live-walk sequence. This is a specific owner ruling for this build. It does not authorise Stage 4, Stage 5, unapproved probes, or any Crusher path.

The combined walk is an explicit exception to Build Plan 01's sequential live gates (Plan §0.4, Stage 2 §4 entry/acceptance, Stage 3 §5 entry/acceptance). The package must not claim that Stage 1, Stage 2 or Stage 3 individually passed Ben's live gate. Keep fixture/source evidence per part, then record one final combined live result.

Part A carries the D1 capture-time token shape and the D2 two-tell exception correctly. Part B preserves the Stage 2 safe-delivery boundaries. Part C preserves the Stage 3 station/dispatch scope and its Stage 4/5 exclusions. Part D correctly makes Ben's visibility requirements acceptance conditions rather than decorative UI.

## 2. Blocking or material clarifications before dependent implementation

### A. The current identity gate conflicts with the required live normal-send walk

Stage 0 §1.8–1.9 records that neither ChatGPT nor Muse currently qualifies for managed registration: Muse produced only a candidate observation, and ChatGPT remains UNKNOWN. The three other platforms are outside the adopted Stage 1 identity scope. Stage 0 Rev07 preserves that restriction. The combined scope itself says platform identity qualification remains blocked and is not changed by this build.

But Part D's combined live walk requires normal messages each way, acknowledgement lines, Index IDs, append and push-through. Those operations require registered identities and an eligible active-send path. Under the currently adopted identity state, there is no evidenced qualified platform pair on which to perform that walk.

**Required boundary:** the combined build go does not imply identity qualification, managed registration, or live-page observation permission. Do not bypass the identity gate or infer qualification from a composer lease. Until Ben supplies/adopts qualifying identity evidence under the existing rule, build and fixture-test the generic/fail-closed infrastructure, but keep live send disabled for unqualified platforms. The final house report must state that the active-send part of Ben's combined live walk is blocked/UNKNOWN unless a platform becomes qualified through a separately authorised route. If a live normal-send acceptance is a condition of passing v0.21.0, this is a real acceptance dependency that requires Ben's separate decision; it cannot be solved by a test fixture.

### B. The single cross-tab station host is still an architecture dependency

The Stage 0 station supplement explicitly says the page-side draft does not create one shared object across two independent tab documents: each content script owns its own document, and mounting the same overlay in both can create two actionable stations. It also says the real physical layout and one authoritative station host must be established before implementation. The combined scope repeats the required outcome (one movable centre-screen station over both registered tabs) but does not state the production host/ownership mechanism or close the physical-layout question.

**Required boundary:** before copying the page-side sketch or implementing Part C, state the actual host architecture for Ben's two-seat display, identify exactly one authoritative station host and one append-lock/timer owner, and say how the other seat reflects its state without mounting a second actionable station. Confirm the real physical layout against Ben's current setup. The background remains authoritative for timers, append lock, identity, state and actions; UI mirrors acknowledged state only. Do not infer that shared background state makes two page DOM overlays one station.

### C. Reset must rotate/revoke capabilities without silently deleting the permanent Stage 1 record

Correction Basis §3, Stream A item 7 states that reset must not silently erase the permanent Stage 1 record; an intentional destructive reset needs an owner-approved consequence and recovery rule. The current v0.19.0 house report specifically identifies that `pb-reset` resets to defaults and discards the Stage 1 ledger export. Combined Part A includes token rotation on reset by implication of the D1 lifecycle, but does not repeat the data-preservation rule.

**Required correction to Part A:** preserve the permanent registration/lifecycle record across token-generation reset. A reset may invalidate registrations/capabilities as authorised, but must not erase the Index ledger, lifecycle history, or unresolved record. If a destructive reset is genuinely required, it must be a distinct, explicit owner disposition with consequence and recovery handling—not the existing silent defaults replacement. Add a regression proving reset revokes old tokens while preserving the permanent record and unresolved work.

### D. Append must use the adopted Gate 4 wire contract, not just the summary phrase “exact text”

The Stage 0 Rev06 §4.4 delegated decision is specific: Option A, length-framed `PB-APPEND/1`; one Ben segment per message/window; commit sends; exact bytes are preserved as entered; an all-whitespace segment is rejected as empty without rewriting a non-empty segment; same PB-ID and same Index ID; both directions; append serialises after the complete original payload and before the F-6 trailer, with the original digest retained as provenance.

Part C says “exact text” and Part B says append serialization, but the combined scope does not identify this adopted wire format or its pinned decision source. This matters because the station supplement already found trimming in the page draft, which would alter Ben's segment.

**Required clarification:** pin Stage 0 §4.4 as a governing input to the combined build and explicitly use the adopted `PB-APPEND/1` framing and all six choices. Add exact-byte/whitespace, byte-count, digest, one-segment, same-identity and trailer-order fixtures. No trimming or normalisation of a non-empty segment.

### E. History parity needs an explicit precedence rule against Plan §5.9

Build Plan §5.9 says the popup does not regain a completed-receipts list at the bottom. New Part D requires the same exchange history, including each letter's number and state, visible from either seat's popup. This is Ben's newer explicit acceptance requirement and should govern, but it can be read as reintroducing the exact surface the plan excluded.

**Required clarification:** record Part D as Ben's explicit override of Plan §5.9 to the extent needed. Define the history view as one shared, authoritative exchange/lifecycle history rendered identically from either popup—not two local histories or a second ledger. State which terminal records are included. The view must not claim delivery beyond the actual receipt state.

### F. Cancel must be a per-item lifecycle disposition, not silent deletion or an unsafe recall claim

Part D's cancel is a new owner action. The prior Stage 3 contract already requires Ben's PUSH / DELETE / APPEND decision for held work, preserving the permanent record, and forbids items from moving or disappearing before the decision. The combined scope says cancel is an owner disposition event, which is compatible if it preserves those invariants, but it does not specify the dispatch race.

**Required clarification:** cancel names one exact PB-ID/Index ID/attempt and records an idempotent lifecycle disposition. It prevents dispatch only if it wins before the actual submit/TRANSIT boundary. Once the adapter has actually submitted, the system cannot claim to recall the message; it must report the truthful in-transit/unconfirmed/delivered state. A cancelled item remains registered and auditable; cancel is not ledger deletion, reset, or a queue-wide purge. Clarify whether this is the adopted DELETE disposition with a clearer label or a separate lifecycle event. Add cancellation-before-submit, cancel/dispatch race, duplicate cancel and post-dispatch-too-late fixtures.

## 3. Acceptance and regression coverage that must remain whole

1. Part A must include the full correction regression set in Correction Basis §5, not only the abbreviated examples in Combined Scope Part A item 6. That includes no-token/no-arming, wrong seat/tab/generation/epoch rejection, re-registration/disconnect/reset rotation, both worker-restart outcomes, import validation, read-back mismatch, uncertain-save idempotence, multiple candidates using one current generation token, reset record preservation, and clean-room builder reproducibility.
2. Restore the Stage 2 and Stage 3 live acceptance points from Build Plan §§4–5 into the single combined walk where the currently approved identity/platform scope makes them testable: Ben's manual composer remains untouched; the station is genuinely singular and visible over the real two-seat layout; direction matches the physical left/right seats; station movement and position persistence are verified; append pauses the authoritative timer and preserves original bytes; one allowed and one blocked PUSH-THROUGH case; F-5 HOLD and LOGIC-FAULT remain distinct; actual submit/receipt states are honest; held work stays in owner-review until Ben decides it.
3. For the new visibility items, verify INCOMING and SENDING from authoritative acknowledged state; animation is only a progress presentation and never a delivery proof. Verify identical history/IDs/status from both popups and cancellation of one named held item.
4. Preserve first-run honesty. The prior Correction Basis also retained held-work visibility as a Stage 3 acceptance requirement. With the station now included, the station must expose the complete set of items requiring Ben's review; do not make “the active card is visible” stand in for an inventory if other held items can exist behind it.

Fixtures remain separately reported by part and by test file. The single combined live walk is one owner acceptance gate, not a reason to collapse fixture results or claim intermediate stage passes.

## 4. Entry gates correctly named in the scope

- **Gate 6 basic-fix snippet:** still OPEN. Build Plan §4 entry allows the exact snippet to be supplied and mapped, or Ben explicitly to say it does not apply. No reconstruction or guessed selector. Do not implement the affected fix path until one of those two conditions is recorded.
- **F-7 composer evidence:** no probes. For every platform, record source evidence and disposition. If uniqueness/ownership/submit evidence cannot be completed from existing sources, name that platform as excluded from active send scope. Do not describe an excluded adapter as active-send supported. A later probe needs its own explicit Ben authorisation.
- **Identity qualification:** remains independently blocked as described in §2A. Composer evidence does not qualify source identity.
- **Stage 4 and Stage 5:** remain outside scope. No aggregate implementation, NEW-9, or adjacent opportunistic additions.

The direction labels must remain exactly as Ben's screen ruling states: Remmy → Alex RIGHT-TO-LEFT; Alex → Remmy LEFT-TO-RIGHT. Do not silently edit the governing sheet; if Stage 0's formal erratum-admission checkbox remains open, link the already adopted owner-screen direction ruling and retain the historical wording.

## 5. Provenance pin required for final delivery

The combined scope says the package is built from a “v0.19.1 tree (Stage 1 delivery + terminal readout)” but does not give that tree's commit, exact source manifest or package hash. In the current Shelf main tree I can verify the v0.19.0 delivery files and the combined scope commit, but I cannot independently identify a v0.19.1 parent-tree pin from the scope itself.

Before delivery, the house report must name the exact v0.19.1 parent commit/tree SHA, the terminal-readout source changes, the complete parent file list, and the resulting v0.21.0 ZIP SHA-256. Do not use the v0.19.0 folder by accident or state a parent as verified without its pin.

## 6. Disposition

The combined build is authorised by Ben as one v0.21.0 build, and the prior per-stage live-gate sequence is superseded for this build only. The six clarifications above are not a blanket rejection of the build go. They are boundaries that must be resolved in the design/source record before their dependent implementation or acceptance claims proceed—especially identity-gated live sending, station host architecture, reset preservation and the adopted append wire format.

No Stage 4/5 work. No probes. No Crusher. Alex's review responsibility continues on the complete delivered package, including source, tests, manifest, ZIP hash, house report and a clear list of excluded active-send platforms.

