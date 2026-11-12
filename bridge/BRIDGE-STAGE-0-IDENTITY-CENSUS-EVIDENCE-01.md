# Pulse Bridge — Stage 0 §1.9 Identity Census Evidence Report 01

**Instrument:** PROBE-identity-census (Remmy-authored scripts, run by Ben in his own open tabs under the house probe pattern).
**Authorisation:** Ben, 2026-11-11 17:35 PST — the Stage 0 pack §1.9 bounded request, verbatim bounds.
**Bounds observed:** read-only; no clicks, focus, typing, sending, navigation, refresh, cache purge, forced re-fetch or page mutation; conversation bodies, prompts and attachment contents never read — scripts emit tag names, class names and attribute names only, and for id-like values only length, shape class and a short non-cryptographic fingerprint (scripts contain no text-reading or interaction calls; verified by grep before issue).
**Scripts:** v1 sha256 `0ae581d3d28094f48ac610318a71b929f0cf75010f576bd0ab13b8fff52a02fd`; v2 sha256 `7459b0f563af59f9f5f80429438edd07c0a73cebc081cb371b1aeb4000933452`.
**Evidence class:** OBSERVED (single census per platform state below). Persistence is NOT established anywhere in this report.

---

## 1. ChatGPT — EVIDENCE_NOT_FOUND (not run to completion)

- Attempt 1 (v1 script): executed on a ChatGPT tab rendering no conversation — **0 turns found**. No evidence about the platform either way.
- Attempt 2 (v2 script): **NOT RUN.** The manual console route failed at the operator step (console noise and clipboard truncation in transit; Ben: "i cant run the probe"). No further ChatGPT observation is claimed.
- **Status: ChatGPT source-identity keys remain UNKNOWN.** No candidate is asserted, and no absence is asserted. This is an evidence gap, not a finding.

## 2. Muse (muse.ai) — candidate keys OBSERVED

Census v2, run 2026-11-12T02:42:01Z on the Muse tab (66 message elements rendered):

| Attribute | Elements | Distinct values | Value shapes |
|---|---|---|---|
| `data-message-id` | 66 | **66** | token, uuid |
| `data-message-turn-id` | 66 | 55 | token, uuid |
| `data-message-group-id` | 66 | 56 | token, uuid |
| `data-message-side` | 66 | 2 | token |

- The message bubble element itself (`.hatch-chat-groupable-bubble`) carries **no attributes**; the identity attributes live on wrapper elements in the message structure.
- **Candidate assessment:** `data-message-id` is a candidate native per-message identifier under the adopted Gate 1 rule — present on every rendered message element with no repeated value in the census.
- **Open, honestly:** (a) the two value shapes (uuid-shaped and token-shaped) are unexplained by a single census — UNKNOWN; (b) the per-turn structural detail (exact wrapper relationship to the bubble) was **truncated in transit** when the census output was pasted — recorded as truncated, not reconstructed; (c) **persistence** of `data-message-id` across re-render, cache purge and source-history re-fetch is NOT established — per §1.9, that requires authoritative evidence or its own further authorisation.

## 3. Readiness consequence (for Alex's cross-check)

- Muse: candidate demonstrated at census level; persistence outstanding.
- ChatGPT: not demonstrated; the operator route failed, not the platform.
- The pack requires demonstration for **both** platforms before Stage 1 registration can be enabled. Whether the ChatGPT discovery may instead run as Stage 1's first build step (registration disabled until the keys are demonstrated, per the adopted fail-closed rule) is referred to Alex's readiness judgement and Ben's Stage 1 go.

*Report prepared by Remmy, 2026-11-11. Raw census outputs as received are preserved in the working record; nothing in this report is reconstructed from memory.*
