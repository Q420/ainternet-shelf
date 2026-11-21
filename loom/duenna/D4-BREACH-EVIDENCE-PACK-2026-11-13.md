# D-4 BREACH — EVIDENCE PACK

**Assembled:** 2026-11-13, by Remmy, from original local sources only — no provider contact was made to assemble this pack, and the Crusher harness was NOT invoked. Where a requested source is not held, this pack records UNKNOWN rather than reconstructing it.
**Destination:** the D-4 breach record in Rev 14 §C (per Alex's correction crosswalk, section C), and the programme record.
**Ruling on record:** Ben, 2026-11-13 14:06–14:08 MST — "Crusher's lane should not be outside the pilot build"; "If we're building a system, we should build the whole system." D-4 is a BREACH, not an exception. Adjudicated by Alex (pb-mwfivrac-f-hb9z): the discrepancy stands; it does not disturb the Batch 1 freeze.

## 1. The rule

STAGE5-BUILD-SPEC-13.md at pin bab720b2 (file sha256 ebefa4a14b73e8f3bfbb7f7188d4524de88460c38c2acd2eec302f584b8394b7), §6.3 item 5 (lines ~3425–3433):

> "Stage 5 makes **no contact with the provider host under any circumstances** — no chat completion, no listing, no probe (Rev 12); the first contact of any kind is Stage 6's."

followed by the enforcement paragraph ("No provider contact — enforced, not merely stated (Rev 12, Claude's finding 1; isolation boundary total, Rev 13)").

## 2. The lane

Crusher: local harness `~/workspace/pulse-bridge/index/crusher.py` v2.2 — a stateless retrieval worker running qwen/qwen3.8-27b via the Groq connector; every invocation is a provider request. Under Ben's 2026-11-13 boundary ruling, the lane is INSIDE the pilot system boundary.

## 3. The attempts (Stage 5 window, 2026-11-13)

Source: `crusher-log.jsonl` — full log 159 entries, 221,412 B, sha256 8e44d5021e272bb5c036879c0920d2fc9cd50b22ae7434fc9e4f0f7996590b5e. The 12 entries timestamped 2026-11-13 are the complete Stage 5 window; they are shelved verbatim as CRUSHER-FB12-LOG-EXTRACT-2026-11-13.jsonl (commit 4c6e0b31; file sha256 017a413ae934a8bd72fb5dc92b1359ab47ba77d11cfb63d27ae321cff2ae14b0) and their call IDs were re-verified against the live log at assembly time (exact match, same order).

| Call ID | UTC | MST | Requester | Status | Scope |
|---|---|---|---|---|---|
| 6f7ea28aed94 | 20:17:57Z | 13:17 | ben | answered | Lane check (is Crusher responsive; does his corpus hold any F-B1-2 record — answered: no) |
| 876f543f7252 | 20:18:08Z | 13:18 | alex | answered (UNKNOWN) | Retrieval Q1 — canonical V2 fixture ids |
| de773aae8b4d | 20:18:09Z | 13:18 | alex | answered (UNKNOWN) | Retrieval Q2 — v1 twelve-pack manifest |
| 0710316a8f41 | 20:18:10–11Z | 13:18 | alex | FAILED — HTTP 429 | Retrieval Q3, first attempt — pinned Batch 1 source refs |
| 361317d87095 | 20:19:44Z | 13:19 | alex | answered (UNKNOWN) | Retrieval Q3, resumed attempt (a separate invocation after the failure, not an automatic in-harness retry) |
| 8d390560275b | 20:20:17Z | 13:20 | alex | answered (UNKNOWN) | Retrieval Q4 — F-B1-2 records |
| b7e99b789d42 | 20:20:37Z | 13:20 | alex | answered (UNKNOWN) | Retrieval Q5 — T09 solely-identifier differences |
| fbf0be7d15e1 | 20:20:56–57Z | 13:20 | alex | FAILED — HTTP 429 | Retrieval Q6, attempt 1 — canonical rendering reproduces the twelve hashes (requested ~1340 expected output tokens) |
| e3c5e4d68a4b | 20:21:51Z | 13:21 | alex | FAILED — HTTP 429 | Retrieval Q6, attempt 2 at k=2 (requested ~1579); Q6 remains a recorded NON-ANSWER, not an UNKNOWN |

Provider responses of record: three HTTP 429 failures (Q3 attempt 1; Q6 attempts 1–2) — Groq on-demand output-token-per-minute cap. The retrieval return itself is preserved unedited as CRUSHER-FB12-RETURN-2026-11-13.txt (commit 105e4d50; file sha256 c78f718bb14b2ef8ab99ff6998e40b23a3066ace4a1a2a1b6f171e710323d198).

## 4. Authorisation context (record citations)

- The Crusher stop order was LIFTED by Ben on 2026-11-13 ~06:40 MST, conditioned on verifiability (jobs in by the marker, results through his lane, unedited). The original F-B1-2 retrieval dispatch (pb-20261113-fb12-retrieval-crusher) was authorised by Ben at ~06:40 MST the same day.
- Alex's FINAL Batch 1 adjudication (pb-20261113-batch1-adjudication-alex-final) made Crusher's independent Shelf-side evidence REQUIRED for the freeze.
- The invocation itself did not occur until Ben asked, 2026-11-13 ~13:16 MST, "Can we check on Crusher and make sure he's not frozen?" — which exposed that the marker letters had been posted but the harness never invoked. The lane check and retrieval ran 13:17–13:21 MST on that exposure.
- The contact was therefore: openly undertaken, under the owner's authorisations, for evidence the process required — and, per Ben's boundary ruling, inside the system and contrary to §6.3 item 5 as written. All three facts stand together in this record; none cancels another.

## 5. Related source references

- Stage 5 build go (Ben, 2026-11-12 22:22 MST) — the Stage 5 window's opening authority; the build remains in Stage 5 (Batch 1 frozen, Batch 2 closed).
- Batch 1 freeze disposition: duenna/batch1-reconciliation/FREEZE-DISPOSITION-2026-11-13.md (commit 260796c8) — NOT disturbed by this breach record.
- Design-time catalogue snapshot (distinguished from any live response): GET /v1/models response recovered from recorded connector stdout, helper-serialisation sha256 bacf2ec8c71a8972af2f0116f9b3cf16963238020678aa3f118f608af3f8f262; incorporated at commit 82111456; adapter_config_sha256 6cf57195d9ae27ca28d304dbb0dc8b8335e888e67a42bfba126629999a1f21eb. This is DESIGN-TIME evidence (2026-11-12 16:25 MST), not a Stage 5 provider contact.
- Current authoritative shelf refs: spec Rev 13 at bab720b2; Claude's inspection on main at 1d45ff8e (file sha256 5e654715…); Claude's full report set on branch claude-reviewer-test at 15d8a00c; baseline evidence pack at c2083de0.

## 6. UNKNOWN

- Provider-side request identifiers beyond the harness's own call IDs: UNKNOWN — the local log is the complete record held; nothing provider-side was retrieved for this pack (and retrieving it would itself be provider contact).
- No other Stage 5-window Crusher entries exist in the log beyond the 12 above (verified by full-log scan at assembly).
