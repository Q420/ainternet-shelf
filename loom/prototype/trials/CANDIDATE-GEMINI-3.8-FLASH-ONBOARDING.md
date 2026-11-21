# Candidate Record — gemini-3.8-flash (Gemini route, NEW candidate)

**Onboarding executed 2026-11-21.** Authority: candidate admission decided by **Ben's tap, 2026-11-21 10:23 MST** ("Switch the Gemini candidate to the still-served model — the only route with real version checking"), under the examiner-accepted design (`~/workspace/duenna-fix/VANE-GEMINI-SUCCESSOR-DESIGN-ACCEPTANCE-2026-11-21.md`: design examination favourable, five conditions accepted; admission Ben's decision).

**Status after onboarding:**
- **Identity: PINNED** (§1).
- **Attestation method: ESTABLISHED from provider documentation** (§2). No live attestation has yet been observed for this candidate, because both generation calls in this onboarding failed (§§3–4) — named plainly, not smoothed.
- **Self-identification: NOT OBTAINED** — the onboarding call timed out with no response (§3). There is no declaration to cross-check.
- **Delivery eligibility: UNPROVEN — the fresh two-part demonstration FAILED** (§4). Per the examiner's condition 4, a successful demonstration establishes delivery eligibility; this one did not succeed, so the candidate is **not delivery-eligible**. One demonstration was run, as specified; it was not retried.
- **Trial authorization: still withheld** (all applicable gates, including D2, remain outstanding). **No trials were run in this onboarding.**

This candidate is a **new candidate with its own identity and record**. It is not a repair of the retired `gemini-2.5-flash` candidate, whose records (original constitution annex, build notes, D1 failure evidence, hunt findings) are immutable history and were not changed.

---

## 1. Identity pin (examiner condition 1)

- **Exact model ID:** `gemini-3.8-flash`
- **Resource name (the pinned identity):** `models/gemini-3.8-flash`
- **Catalogue `version` field:** `"3.0"` — recorded **as a field of the catalogue entry, never as the identity**. The field is not discriminating: the same catalogue carries `"version": "3.0"` for unrelated models (e.g. `models/gemini-4-argon`); the exact resource name is what pins this candidate.
- **Live catalogue capture (models.get):** HTTP 200, retrieved **2026-11-21T17:25:09Z**, source endpoint `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash`, fetched through the `custom.gemini` connector's credential mechanism. The **complete raw response** (status, headers, body) is preserved at `evidence/CANDIDATE_gemini-3.8-flash_catalogue_detail.json`.
- **Catalogue entry as captured:**

```json
{
  "name": "models/gemini-3.8-flash",
  "version": "3.0",
  "displayName": "Gemini 3.8 Flash",
  "description": "Gemini 3.8 Flash",
  "inputTokenLimit": 1048576,
  "outputTokenLimit": 65536,
  "supportedGenerationMethods": ["generateContent", "countTokens", "createCachedContent", "batchGenerateContent"],
  "temperature": 1, "topP": 0.95, "topK": 64, "maxTemperature": 2, "thinking": true
}
```

- **Pinned inference configuration** (as for the route in the original annex): `generationConfig: {temperature: 1.0}`; no system instruction.
- **Traceable reason for considering this successor:** the retired candidate's 404 error body, preserved in the hunt evidence: "This model models/gemini-2.5-flash is no longer available to new users. Please update your code to use models/gemini-3.8-flash…" — a reason to consider, not an authorization; the authorization is Ben's tap, above.

## 2. Serving attestation — method and verification rule (examiner condition 2)

- **Format:** every successful `generateContent` response (`GenerateContentResponse`) carries a top-level **`modelVersion`** field — the provider's per-response serving attestation.
- **Provider documentation relied on** (preserved in `evidence/version_hunt_findings.json`, `gemini.surfaces.documented_serving_attestation`; Google Cloud docs, verbatim): *"modelVersion | The model and version used for generation. For example: gemini-2.0-flash-lite-001."* The documented form is the composite `<model id>-<version>`; against this candidate's pin, the expected attestation value is **`gemini-3.8-flash-3.0`**.
- **Verification rule:** on **every** call, the raw `modelVersion` is captured from the raw response and checked exactly against the pinned composite `gemini-3.8-flash-3.0`. **Missing, malformed, unverifiable, or inconsistent attestation means that call is not eligible evidence.** There is **no fallback to the catalogue `version` field** — the catalogue field is onboarding metadata, never serving evidence.
- **Live status of the method:** established from documentation only. Both generation calls in this onboarding failed before any response body existed (§§3–4), so **no live `modelVersion` value has been observed for this candidate yet**. The first successful call must carry the attestation and be checked against the rule above; until then the method is documented, not exercised.

## 3. Self-identification (examiner condition 3)

- **Prompt sent (one call, the same onboarding prompt used for the other routes in the version hunt):** "You are being onboarded as a candidate in a test harness. State exactly what model you are, including the model name and any version, snapshot, or build identifier you know for yourself. Answer in one line in the form: MODEL: <your answer>"
- **Result: NOT OBTAINED.** The call (adapter dispatch, pinned configuration, 2026-11-21) ran to the connector helper's 120-second read timeout: `TimeoutError: The read operation timed out`; returncode 1; latency 120.563 s; **no response bytes, no self-report, no attestation**. Full dispatch record: `evidence/CANDIDATE_gemini-3.8-flash_self_identification.json`.
- **Cross-check: cannot be performed** — there is no declaration to check against the catalogue record or an attestation. This is recorded as an absence, not filled in. (For contrast, the retired candidate's self-identification was also not obtainable in the hunt, for a different reason: the route refused all generation for that model. Here the model is listed and served in principle; the call itself failed by timeout.)

## 4. Fresh two-part delivery demonstration (examiner condition 4) — **FAIL**

- **Method (the D1 method, against the new candidate):** the exact two-part dispatch assembled from the pinned instruments — part 1 = Annex A instruction bytes, part 2 = gate-schema profile v2 bytes, each as its own text part — sent once through the trials adapter (`adapters/adapter.py`) with the pinned configuration; 120-second boundary; one request, no retry.
- **Instrument pins re-verified before dispatch:** Annex A SHA-256 `25ab2d6296bfaad316b55e653c905b57a553072867058b5bd12bdbbdb0f029e6` — **matches the pin**; profile v2 SHA-256 `bdb0ad70cd40c0ed61a0f05b2e2c66a87021df28c4f5b81e2c7400d5d25231ef` — **matches the pin**. The dispatched parts' hashes equal the pins.
- **Result: FAIL.** The route returned **HTTP 503 Service Unavailable** after 6.378 s (helper returncode 1; no response body; no attestation). This is the same failure class the build round recorded for this model in D1 (`evidence/D1_gemini_attempts.json`: 503 for gemini-3.8-flash while catalogue reads succeeded — and the catalogue read succeeded again today, §1).
- **Preserved:** both parts and their hashes, the complete request body and actual settings, the raw outcome (empty response, helper stderr tail showing the 503), latency, and the verdict block — `evidence/CANDIDATE_gemini-3.8-flash_delivery_demonstration.json`.
- **Consequence:** delivery eligibility is **not established**. The candidate stands admitted to the record and identity-pinned, but **not delivery-eligible**, and therefore cannot proceed to any trial. The failure is reported as a result; per the demonstration's terms it was **not retried** and no weaker delivery was substituted.

## 5. Change control (examiner condition 5)

- The attestation is **re-checked on every call** against the pinned composite (§2). A **version mismatch, or an attestation that cannot be verified, stops the candidate's round**. **No automatic substitution and no retry** follows from a mismatch: the round stops and the fact is recorded. Any change of candidate, model ID, or pin is a new admission decision, not an adapter behaviour.

## 6. Open items and limits — named, not settled here

- **Contamination determination for this candidate is NOT asserted in this record.** The three grounds were determined for the original three candidates in the original annex; this candidate's determination must be made on its own facts. One fact the examiner should have in view: the connector doc for this route records that `models/gemini-3.8-flash` is the model used by the Alex continuity lane (`~/workspace/alex-lane/lane.py`), which sends that lane's continuity pack as a system instruction. Whether any recorded session through that lane supplied instrument material (Annexes A–D, the fixture, scoring provisions) to this model is **not established by this onboarding** and is flagged here rather than certified either way.
- **The precommitted schedule in the original annex is not amended** by this admission; it named the retired candidate's route slots. Any round constitution for this candidate is a later, separately authorized step.
- **Route behaviour observed today:** catalogue reads succeed (fast, HTTP 200); generation failed twice in two different ways (one 120 s read timeout, one immediate 503). No conclusion about the route's general availability is drawn from two calls; the demonstration result stands as recorded.
