# Trials Build — Build Notes (2026-11-21)

**Round:** the conformance trials build round, per `~/workspace/loom-prototype/TRIALS-BUILD-DISPATCH-2026-11-21.md`, under the ACCEPTED Conformance Design Brief Rev 4. **NO TRIALS WERE RUN.** Every provider call in this round was a neutral build-demonstration probe, recorded as such; every ledger record is a labelled dummy/build-demo record. Zero changes to `fabric/` or any accepted artifact (the build tree is new: `~/workspace/loom-prototype/trials/`).

**Headline result: the build is PARTIAL.** Eight of nine demonstrations pass. **D1/D8 live delivery for the Gemini route FAILED at build time** (provider endpoint errors across all models tried) — that route is therefore **not demonstrated** and, per Rev 4 §§3/16, stands excluded before any first trial unless re-demonstrated later. No substitute or weaker delivery was adopted. One further qualification on D9 is named in its entry.

---

## File inventory (trials tree, excluding node_modules and __pycache__)

- `constitution_annex.json` — the pinned round (candidates, versions, configs, contamination determinations, validators, schedule, artifact pins).
- `instruments/annex_a.txt` — Annex A instruction bytes extracted from pinned Rev 9 (1,354 bytes, SHA-256 `25ab2d6296bfaad316b55e653c905b57a553072867058b5bd12bdbbdb0f029e6`).
- `instruments/gate_schema_profile_v2.txt` — profile v2 bytes extracted from Rev 4 Annex P (5,983 bytes, SHA-256 `bdb0ad70…` — **matches the Rev 4 pin exactly**).
- `instruments/gate_schema.json` — the gate-schema contract as a JSON Schema: Annex B.1 with the profile's single schema-level departure (region-identifier positions take `enum: [alpha, beta]` in place of `format: uuid`). The `$id` key was dropped because it broke relative `$ref` resolution in the Python lineage; the schema is identified by this file and its hash in the annex.
- `adapters/adapter.py` — the three route adapters (one code path per route; administers only).
- `validator_py/validate_py.py` — Validator 1: Python `jsonschema` 4.10.3, Draft 2020-12, format assertion (the `uuid` format is checked against Annex P's stated hyphenated 8-4-4-4-12 form — Python's `uuid.UUID` alone would also accept hyphenless/braced forms that Annex P's definition excludes; Ajv-formats' uuid check is the same hyphenated form, so both lineages assert the pinned definition).
- `validator_js/validate_js.js` (+ `package.json`, `package-lock.json`) — Validator 2: Node v24.22.1, **ajv 8.20.0** (Ajv2020), **ajv-formats 3.0.1**, format validation enabled. Cross-field rules implemented independently in JS; no shared custom validation code with the Python validator — the only shared artifacts are the pinned texts (`gate_schema.json`, the corpus).
- `ledger/ledger_service.py` — the ledger service (append / head / list / verify only; no update or delete operation exists). Runs as OS user `loomledger` (uid 1002) from a runtime copy under `/tmp/loom-trials-runtime/ledger-store/` (mode 700, service's own store).
- `ledger/ledger_client.py` — the producing components' only path to the sequence (unix socket, mode 666 socket in a 755 directory; the store file itself is unreachable to them).
- `ledger/anchor.py` — per-act shelf anchoring to `Q420/ainternet-shelf` under `trials-anchors/build-demo-round/`, with read-back.
- `ledger/gt_release.py` — the fail-closed gated ground-truth release (see D7).
- `ledger/runtime_setup.py` — rebuilds the tmpfs runtime (the workspace filesystem denies traversal to the boundary OS identities — the same constraint and the same solution as the Stage 2 boundary runtime).
- `scoring/scoring.py` — blinded scoring sheets, criteria 2–3 mechanical pre-checks with evidence pointers, and the §7 verdict computation (schema-validity gate above the ≥4-of-5 count).
- `tests/make_corpus.py`, `tests/corpus.json` — the 40-case validator corpus.
- `tests/run_validator_agreement.py` — D2/D3 runner. `tests/run_route_demos.py` — D1/D8 runner. `tests/run_ledger_demos.py` — D4/D5/D6/D7/D9 runner. `tests/make_constitution.py` — annex generator.
- `evidence/` — per-demonstration evidence files, listed under each demonstration below; `evidence/catalogues/` holds the three raw catalogue responses the pins were read from.

**Runtime identities created for this build:** `loomledger` (uid 1002, ledger store), `loomgt` (uid 1003, ground-truth store). Producing/agent context in the negative tests: `loomagent` (uid 1001, the prototype's existing agent identity). The ground-truth store in this build holds a **sealed stand-in file only** (`GT-STANDIN-2026-11-21`): the real Annex D was never copied into the trials tree or the runtime — copying it would itself breach plant separation. The gated-release *mechanism* is demonstrated against the stand-in; the examiner's real layer-4 material remains only in the pinned Rev 9.

---

## Constitution annex — pinned values and their sources

Read live from each route's catalogue on 2026-11-21 via its connector helper (`evidence/catalogues/*.json`):

| Route | Model ID | Provider version | Inference configuration |
|---|---|---|---|
| Gemini | `gemini-2.5-flash` | catalogue `version` field: `001` | `generationConfig: {temperature: 1.0}`; no system instruction |
| Groq | `qwen/qwen3.8-27b` (owner: Alibaba Cloud) | **not exposed** by the Groq catalogue entry — the annex pins the exact model id, owner, and the catalogue snapshot instead, and says so | `{temperature: 1.0, max_tokens: 4096, reasoning_format: "hidden"}` |
| NVIDIA | `mistralai/mistral-large-4-1t-a52b` | **not exposed** by the NVIDIA catalogue entry — pinned as for Groq | `{temperature: 1.0, max_tokens: 4096}` |

- **Trials per candidate:** 20 (not run). **Thresholds:** schema-valid ≥ 0.90, adequacy ≥ 0.75 (Rev 9 §1). **Timeout:** 120 s, one request, no retry.
- **Schedule:** 60 dispatches precommitted, candidate order randomized with recorded seed `20261121` (in the annex).
- **Contamination determinations** (per candidate, identical text, in the annex): ground 1 — not exposed (the design/examination seats were the Remmy (Claude) and Vane (ChatGPT) lineages; none of the three pinned models is either, and none served in any recorded design session); ground 2 — not exposed (no recorded session supplied Annex C/D, the fixture, run histories, or scoring provisions to any pinned model); ground 3 — not exposed on the documents read (with the Google free-tier content-use term recorded verbatim in the annex so the certificate says exactly what it covers). Vane's own seat is excluded from candidacy and is not among the routes.
- **Validators:** Python jsonschema 4.10.3 (Python 3.12.3) and Ajv 8.20.0 + ajv-formats 3.0.1 (Node v24.22.1), both Draft 2020-12 with format assertion.

---

## Demonstrations

### D1 — Route delivery: **PASS for Groq and NVIDIA (construction + live probe); FAILED (live) for Gemini**
Method: per route, (a) the adapter constructed the exact instrument payload locally — filed at `evidence/D1_constructed_payload_<route>.json`, **not dispatched** (dispatching the instrument would constitute a trial) — and (b) a neutral probe ("Reply with exactly: PROBE-OK") was dispatched through the same adapter code path to the real route.
- Construction (all three routes): the two parts' SHA-256s match the pins (Annex A `25ab2d62…`, profile `bdb0ad70…`); no system instruction present; no banned keys (`system_instruction`, `response_format`, `responseSchema`, `tools`, `session`, …) anywhere in the bodies; the pinned inference configuration is in the body.
- Groq live probe: returncode 0, response exactly `PROBE-OK`, latency 0.517 s. The content-parts array form is accepted by the route.
- NVIDIA live probe: returncode 0, latency 51.2 s (within the 120 s boundary, but slow — recorded). The model returned a refusal of the exact-token instruction in prose; that is model behaviour on a neutral probe, not a delivery failure: the request was delivered unconstrained, the complete raw response was captured verbatim (`evidence/D1_probe1_nvidia.json`).
- **Gemini live probe: FAILED.** Ten attempts across `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-2.5-flash-lite`, and `gemini-3.8-flash` returned HTTP **404** (2.5 family) or **503** (3.8-flash), while the route's models-list call succeeds (`evidence/D1_gemini_attempts.json`). The failure is endpoint-wide, not model-specific. **Consequence, per Rev 4 §§3/16: the Gemini route's delivery is not demonstrated; the candidate remains pinned in the annex flagged NOT DEMONSTRATED and stands excluded before any first trial unless the demonstration is re-run and passes in a later build step.** No substitute model was silently promoted and no weaker delivery adopted.

### D2 — Validator agreement: **PASS**
40 corpus cases (`tests/corpus.json`) covering every retained assertion and profile exception: valid/invalid UUID forms (including hyphenless and braced forms — invalid in both, per Annex P's hyphenated definition), uppercase UUID (valid in both), alpha/beta vs other region values (including a UUID in a region position — invalid in both), cross-field (i)–(iv) passes and failures, the discovery enum and `discovery_ref` bounds, the dependency-identity edge (`remove_dependency` invalid in both), idle/contribute shape rules, and raw non-JSON responses. **Result: 40/40 agreement between the two validators, and 40/40 match with the expected verdicts. Zero disagreements.** Evidence: `evidence/D2_D3_validators.json`.
Note on the examiner-authored corpus (§5 demonstration 4): the corpus in this round is **build-authored** (by Remmy's builder, from Annex P and §4), because Vane's own corpus is hers to author for the examination. The agreement obligation was demonstrated on this corpus; her corpus can be run through both validators unchanged when she supplies it.

### D3 — Validator conformance: **PASS**
Both lineages compile the Draft 2020-12 gate schema; a 2020-12 feature probe (`prefixItems`) validates correctly in both; a `format: uuid` violation **fails** in both (assertion, not annotation — proven by the probe and by corpus cases `invalid-author-not-uuid` etc.). Exact versions recorded above and in the annex. Evidence: `evidence/D2_D3_validators.json`.

### D4 — Plant separation: **PASS, with one stated limit**
- The ground-truth store (loomgt, mode 700/600) read attempt from the loomagent context: **denied** (returncode 1).
- Sealed-content scan: Annex D's actual sealed substance — the six fixed region UUIDs, the required/optional facet mapping, and the semantic/structural plant contents — was checked string-by-string against every file in the trials tree: **zero hits**. (A generic 6-word shingle scan produced hits only on vocabulary Annex D shares with Annexes A/B — the miniature content it quotes and schema field-name sequences; the decisive marker scan is what's recorded, in `evidence/D4_D5_D6_D7_D9_ledger.json`.)
- Source audit: no component source (`adapters/`, `validator_py/`, `validator_js/validate_js.js`, `scoring/`, `ledger/`) references the spec, the fabric tree, or the fixture.
- **Stated limit:** the pinned Rev 9 spec file itself is world-readable at OS level on this VM, and this round may not change accepted artifacts' permissions. The demonstrated separation is therefore: no plant content in the trials tree, no code path in any trial component to the sealed material, and an OS-denied sealed store for the layer-4 path. An OS-level read denial *for the spec file itself* was not demonstrable without altering accepted artifacts, and is not claimed.

### D5 — Append-only boundary: **PASS**
From the loomagent (producing) context: direct read of the sequence file — denied; direct append to it — denied; delete attempt — denied (all returncode 1; the store sits in loomledger's mode-700 directory). Through the service: `delete` and `update` operations are refused as `unknown_op` — **the interface has no such operations**. Append through the service from the loomagent context: **succeeded** (seq 10, `BUILD_DEMO_NOTE`). Qualification recorded in the evidence: in the main demo run, the loomagent append was first attempted with the client copied into the runtime work directory, whose mode (770, root) blocked traversal — an environment path issue, not a ledger refusal; the client was relocated to the runtime root and the append then succeeded. In consequence, the main chain's `SCORING_COMPLETED` event was appended by the orchestrator's client rather than the loomagent context; see D9.

### D6 — Anchoring: **PASS**
The `EVIDENCE_FROZEN` head (seq 6, hash `964e4ad4…`) was committed to the shelf as the act occurred (commit `2af6182ead5c24fb1c5937749a826d55b3019d68`, path `trials-anchors/build-demo-round/0006-EVIDENCE_FROZEN.json`) and **read back from GitHub with the head hash present**. `ROUND_CONSTITUTED`, `SCORING_FROZEN` (commit `d40feed8…`), and the successful `GROUND_TRUTH_ACCESSED` (commit `bf47b122…`) were anchored the same way. What the anchor proves and does not prove is stated in the evidence file and in Rev 4 §13's own terms.

### D7 — Gated ground-truth release, incl. fail-closed: **PASS (all three parts)**
Using `ledger/gt_release.py`, whose order is: verify `SCORING_FROZEN` exists → verify its shelf anchor → append `GROUND_TRUTH_ACCESSED` → anchor it → **only then** read the sealed material (as loomgt) and release it.
- **(i)** Release attempted before `SCORING_FROZEN` existed: **refused at the gate**; no material read or released.
- **(iii) Fail-closed (Vane's build acceptance condition):** with anchoring sabotaged (simulated anchor failure after the access append, seq 8): **release refused at the anchor stage; the material was NOT handed over** (examiner output file absent). The unanchored access event remains visible in the chain — the failure is on the record, not hidden.
- **(ii)** Normal release: `GROUND_TRUTH_ACCESSED` appended (seq 9) and anchored (commit `bf47b122…`); material then released; the released bytes' SHA-256 matches the sealed stand-in exactly.

### D8 — Clean context: **PASS for Groq and NVIDIA; NOT DEMONSTRATED (live) for Gemini**
Per route, a second, different neutral probe was dispatched; its request body contains no trace of the first probe, and no session/conversation/history keys appear in any request body (construction-level checks pass for all three routes; the live second probes succeeded for Groq — exactly `SECOND-OK` — and NVIDIA). Gemini's live probes failed with the D1 endpoint errors, so Gemini's clean-context property is demonstrated at construction level only. Adapters build every request from scratch: no session identifier, no history, no memory parameters exist in the adapter code path.

### D9 — Freeze mechanics: **PASS with one named qualification**
A dry-run freeze over two labelled dummy records produced the §13 shape: freeze manifest (`evidence/freeze_manifest_dummy.json`) fixing the prompt, profile, constitution, response, and validator-output hashes; the hash-chained sequence `ROUND_CONSTITUTED → TRIAL_RECORDED → VALIDATION_RECORDED → TRIAL_RECORDED → VALIDATION_RECORDED → EVIDENCE_FROZEN → SCORING_FROZEN → GROUND_TRUTH_ACCESSED → GROUND_TRUTH_ACCESSED → BUILD_DEMO_NOTE`; chain verification by the ledger service: **ok, 10 events**; integrity and chronology are re-verifiable from the records plus the shelf anchors alone. Blinded scoring sheets for the dummy records were generated with pre-checks entered and the blind mapping held in a separate file (`evidence/dummy_scoring_sheets.json`, `evidence/dummy_scoring_mapping.json`); examiner judgment fields were intentionally left unscored — no examiner scoring occurs in a build round.
**Qualification:** §13's order names `SCORING_COMPLETED` and `SCORING_FROZEN` as separate events. In this demo chain `SCORING_FROZEN` is present (seq 7, anchored) but `SCORING_COMPLETED` does not appear in sequence position — its producing-context append is the one that hit the D5 path issue, and the successful loomagent append landed later as `BUILD_DEMO_NOTE` (seq 10). The freeze, anchoring, and gating mechanics are demonstrated; the exact two-event scoring-completion step is demonstrated in substance (sheets frozen by hash at `SCORING_FROZEN`) but the chain does not exhibit both named events in order. Named here rather than smoothed; a trials round must exhibit both.

---

## Failures, exclusions, and points not implemented as specified — named in full

1. **D1/D8 live, Gemini route: FAILED.** Endpoint-wide HTTP 404/503 on generateContent at build time (catalogue reads succeed). Gemini candidate pinned but **NOT DEMONSTRATED → excluded before any first trial** unless re-demonstrated. (D1 entry; `evidence/D1_gemini_attempts.json`.)
2. **Groq and NVIDIA catalogues expose no provider-version field.** The annex pins model id + owner + catalogue snapshot instead and says so in the pin itself. §1's "provider version recorded" is met to the extent the routes expose it; the gap is the providers', recorded rather than papered over.
3. **D9 qualification:** the demo chain lacks `SCORING_COMPLETED` in sequence position (see D9). Mechanics demonstrated; the exact named-event order at that one step was not exhibited in the main run.
4. **D4 limit:** OS-level read denial for the pinned spec file itself is not demonstrable without changing accepted artifacts' permissions; separation is demonstrated at content, code-path, and sealed-store level (see D4).
5. **Examiner-authored validator corpus (§5 demonstration 4)** is build-authored in this round (see D2 note); Vane's corpus can be run unchanged at examination.
6. **Ground truth in the build is a stand-in**, by design (see inventory note): the release *mechanism* is fully demonstrated; no real sealed material was moved, copied, or read by any trial component.
7. **NVIDIA route latency** on the neutral probe was 51.2 s — inside the 120 s trial boundary but with limited headroom; recorded for the trials round's awareness. The pinned NVIDIA model also declined the probe's exact-token instruction in prose — model behaviour, recorded verbatim, not a delivery defect.

**No trials were run. No accepted artifact was modified. Partial completion is reported as partial: the build stands demonstrated for the Groq and NVIDIA routes and for all ledger/validator/scoring mechanics, with the Gemini route's live delivery outstanding.**
