# RESUBMISSION 2 — THE HELPER CORRECTION (INDEX 295) (2026-11-23)

For Vane's re-examination. The receipt correction passed (INDEX 295); this round closes the one remaining item — the raw evidence chain made exact from provider bytes to retained evidence — plus her receipt-retention detail. The proposal otherwise stands; Ben's INDEX 276 authorisation remains banked.

## The bytes now cross untouched

- The helper's raw mode no longer decodes anything: `call_raw()` returns the **actual status and the raw bytes read to EOF**, success and HTTP error alike, and the `chat-raw` envelope is now `{"status": <int>, "body_b64": <base64 of the exact bytes>}`. Helper: 176 lines, sha256 `e3be4160…`; the as-built copy is refreshed verbatim (identical hash). (For precision: the one remaining `errors="replace"` decode in the helper sits in `_provider_error()`, the *ordinary* path's bounded error-line retainer from the INDEX 262 diagnostic correction — the worker transport's diagnostics, never probe evidence. The raw path contains no decode at all.)
- The transport base64-decodes the envelope and applies the **declared probe-boundary policy — strict UTF-8** — now stated in its docstring. A valid body crosses byte-exact. An undecodable body yields an honest capture: the actual status stands, **no body is claimed**, and the diagnostics record that the body was not valid UTF-8 with its byte length and the **sha256 of the raw bytes** — provenance without substitution; no replacement character appears anywhere in such a capture (witnessed).

## The witnesses now aim at the helper itself

New suite **`live-demo/test_groq_helper_raw.py` — 11 checks, ALL PASS** — loading the real helper module with its opener seam stubbed (network-free), covering her five cases exactly: (i) success at an actual **201** with byte-exact body, in-process and through the envelope; (ii) an HTTP **429** whose **5,048-byte** body crosses whole and exact, beyond the ordinary 2,000 retention; (iii) a **70,048-byte** body preserved whole by the helper, then truncated **by the probe alone** to 64,000 with `evidence_complete` false; (iv) undecodable bytes (`\xff\xfe…`) crossing exactly, the transport claiming no body, diagnostics naming byte count + raw-bytes hash, **no U+FFFD anywhere**; (v) a body-read failure raising visibly in-process and yielding an honest no-body/no-status capture through the transport. W11's stub helpers moved to the `body_b64` envelope with every assertion's intent preserved — Groq transport suite **68, ALL PASS**.

## Receipt retention (her preservation detail)

Phase 2 now copies the validated receipt's **exact bytes** to **`decision-receipt.json`** in the run directory, after validation and before the judgement is recorded; a failed copy aborts phase 2 before any ASSEMBLY_JUDGED stands. The phase-2 report names the retained file beside the receipt hash. Witnessed (`test_probe_receipt.py`, **13 checks, ALL PASS**): the retained file is byte-identical to the receipt supplied and its canonical hash equals the hash bound in the judgement. At the real run, the retained receipt will also be shelved with the run evidence.

## Regressions

All green at exact counts, verified first-hand by Remmy (helper-raw 11 counted; Groq transport 68 counted; receipt 13 counted): NVIDIA transport 55; probe 57; A1 69; A2 80; A3 88; A3-CAT 37; retrieval 56 + evidence 41; checker 35; adapter 36; Pieces 2–5 73/41/35/43; onboarding 38; gates 74; orchestrator 55; observer 33. Probed + retrieval `--verify-config` clean. **No live provider calls were made**; the accidental-run directory was not touched.

Release of phase 1 is re-requested on the proposal's terms.
