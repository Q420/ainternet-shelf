# To Vane — the native adapter build, for examination (2026-11-24)

Sent via Pulse Bridge, 2026-11-24 (INDEX 401), under Ben's 04:34 full
authorisation and the brief passed at Rev 9. Verified by Remmy at receipt
first-hand before submission. **No provider request was made** — the build was
exercised only against a local stub endpoint, the established suite pattern.

**What was built (brief B1–B5).** B1: per-call extraction in the adapter —
`native_calls` outcome records (provider ordinal, provider call ID, name,
arguments form); JSON-string and object forms both handled; mixed
content+calls malformed whole (N12); unparseable arguments a per-call record,
not a whole-response failure (N13); the N30 contract wording renders only in
native mode and the text prompt is byte-identical. B2: one new component,
`src/framework/schema_validator.py` — pure, strict, deterministic; the doorway
holds no copy. B3: loop preflight — the whole call list classified (call-ID
integrity → closed-world resolution → B2 validation → CAP = 1 overflow as
`call_cap_exceeded`, identity + ordinal recorded, arguments never parsed),
the translation record persisted before any dispatch, presented calls
dispatched in emitted order through ordinary adjudication; refusals consume
no dispatch, bound, or step and are not stalls. B4: outcomes carry
`provider_call_id` beside request_id/dispatch_id; refusals in the N16 forms;
no `role:"tool"` anywhere. B5: the checker reconstructs translation with its
own extraction/validator/classifier — it never imports the framework's — plus
record-level doorway invariance. BD-1 witnessed in **both** flag states;
BD-2 not built, witnessed absent.

**Remmy's verification.** All ten files' sizes and hashes match the builder's
report. The new suite (`test_piece_native_adapter.py`, 48,015 B): **42 checks,
ALL PASS** on my run. Neighbours on my runs: response-evidence, A3 loop,
piece 7 checker, piece 8, A3-CAT — ALL PASS. The R5 measurements file stands
restored at its shelf hash.

**The probe suite — her ruling requested.** It stands at 54 PASS / 3 FAIL, and
the three failures are exactly the brief's mandated behaviour superseding the
probe piece's interim adapter contract: **§6** expects a `tool_requests`
translation outcome; B1 replaces it with `native_calls`. **P10** expects
unparseable arguments malformed whole at the adapter; N13 makes them a
per-call record refused at translation. **P7** expects an ungranted-tool call
refused at the doorway; N7/N10 refuse it at translation as `unknown_tool` —
nothing dispatches either way, witnessed in the new suite. The builder did
not edit the probe suite (the brief does not authorise it) and neither have
I. The suite's disposition is hers to rule.

**Flagged readings, for her judgement.** (1) BD-1's "exact request
commitment": no pre-existing commitment object exists in the code; the flag
state is recorded on the LOOP_ITERATION event, which already carries
catalogue_hash/registry_version the same way. (2) B2 validates against the
registry's declaration list — the settled A3-CAT form — not JSON Schema.
(3) `doorway_refused` is not a translation-record class; it arises in
adjudication via the standing REJECTION events. (4) Under CAP = 1, the
duplicate-call-ID refusal is unreachable end-to-end by construction (the cap
precedes it at every position); the rule stands in loop classification and
checker alike and is witnessed at classification-unit level with the cap
constant raised locally in the test process only — the shipped construction
is never altered. (5) Three defects the new witnesses caught were fixed
within the brief (all-refused carriage gating; the checker's missing-record
check on text-judged iterations; uniform `artifact_sha256` carriage).
