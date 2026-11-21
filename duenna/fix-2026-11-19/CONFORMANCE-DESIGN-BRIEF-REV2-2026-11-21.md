# Conformance Trials — Design Brief, Revision 2 (settlement revision)

**Status: SETTLEMENT REVISION FOR EXAMINATION.** Paper only. No trial has been run, no code has been built or changed by this document, and nothing in it authorises a build round or a trial run. The build/run commission for the trials phase is Ben's ("Make it so", 2026-11-21 08:22 MST, recorded in `~/workspace/scope-ledger.md`); the build round follows the settled text of this revision once the examiner accepts it, and the trials follow the build.

**Provenance.** This revision incorporates, as settled design, the dispositions of the examiner's examination of Revision 1 (`VANE-CONFORMANCE-DESIGN-EXAMINATION-2026-11-21.md`, delivered via the Pulse Bridge, PB-ID pb-mwqkczqh-2d-j7at). Revision 1 (`CONFORMANCE-DESIGN-BRIEF-2026-11-21.md`, shelf head 30e6b96f, blob d46f6080) is preserved unchanged; this file supersedes it as the settlement text and does not edit it. The seven open questions of Rev 1 §8 are answered in §§3–10 below and are no longer open. Where a disposition turns on specification text, the text was checked directly in Revision 9 for this revision; citations are to the spec's own locations.

**Authority:** Loom specification v0.1 Revision 9 (shelf commit d7d65c96, blob 6a7e3d54, Gate 1 PASS), §1 and Annexes A–C; Amendment A1 (IDLE) as noted in §14. The gate-validation profile of §4 is pinned alongside Rev 9 as an explicit gate-scoped interpretation record; it does not alter Rev 9, Annex B, or any fabric schema.

**What already exists (accepted, immutable):** the fabric service and harness (`fabric/service.py`, `fabric/harness.py`), the agent-side client (`fabric/client.py`), the agent runner (`fabric/agent_runner.py`), the boundary runtime builder (`fabric/runtime_setup.py`), and the Stage 4 binding (`fabric/packpin.py`: Rev 9 + A1 + the pinned examiner pack V2, SHA-256 `cce27ee7…`). Accepted artifacts ee235533, ca2a8c16, 87c9ec08 and all accepted Stage 4 rounds stay exactly as they are. The trials do not execute accepted fabric code except as §11 states (validator reuse of the Annex B schema text, read-only, as data).

---

## 1. What a trial is, exactly

A trial is one conformance attempt by one candidate model under §1 of the spec:

- **One fresh candidate instance, as a hard eligibility condition** (settled, §10): each trial is a new, independent, stateless request. No trial sees any earlier trial's prompt, response, or score.
- **The instrument is Annex A, verbatim, as the candidate's instruction** — "The candidate receives the following, verbatim, as its only instruction" (Annex A preamble). Nothing is added: no system-prompt coaching, no worked example, no hint about scoring. How the schema Annex A refers to ("conforming to the schema you were given") reaches the candidate is settled in §3.
- **The task is the one inside Annex A.** The candidate is shown a miniature two-region fabric — alpha ("Alpha", v3) and beta ("Beta", v1), alpha —uses→ beta — with one open semantic tension, T-1: alpha's content assumes requests are stateless; beta's content assumes a session pinned to one component. Both regions' content is given in the prompt itself. The candidate must respond with **exactly one JSON object and nothing else**: either a contribution (`"action": "contribute"` with the Annex B.1 contribution fields) or `{"action": "idle"}`. That is the whole task. Annex A "tests basic tension handling and schema discipline" (§1).
- **What a trial is not.** It is not a fabric run. The candidate does not open a bound run on the six-region fixture, does not receive a harness token, and never sees the §5 experiment's material — not the six regions, not the planted semantic contradiction (Interactions vs Continuity, Annex D), not the structural plant (Annex D). Those belong to the §5 experiment, whose agents are "3 instances, each having passed the §1 gate" (§5). Gate trials create **no fabric run** — no `RUN_OPENED`, no token issuance, no boundary probe, no seal. Running gate candidates against the real fixture would conflate the gate with the experiment and expose the sealed material to the very subjects whose later discovery the experiment exists to measure; Annex A's identifiers are "illustrative constants of the test, identical for every candidate and every trial."

## 2. The pinned numbers — cited, not paraphrased

Carried forward from Rev 1 unchanged; every value is the spec's, at the location cited.

| Term | Value | Spec location |
|---|---|---|
| Trials per candidate | 20 | §1: "Trial count: 20 trials per candidate, the Annex A prompt verbatim" |
| Schema-valid threshold | ≥ 0.90 | §1: "schema-valid rate ≥ 0.90" |
| Task-adequacy threshold | ≥ 0.75 | §1: "task adequacy ≥ 0.75" |
| Threshold status | "stated before any trial runs and immovable" | §1 |
| Failures | "refusals, malformed outputs, and timeouts count as failed trials in both rates" — "Failures counted, never repaired" | §1 |
| Adequacy bar per trial | at least 4 of 5 criteria, each criterion binary, "the scorer records which were met" | Annex C |
| Idle under Annex A | "an `idle` response cannot reach adequacy for the Annex A prompt as written: a contribution is warranted, so `idle` scores 0 on criterion 1" | Annex C, criterion 5 note |
| Format assertion | "Annex B requires the JSON Schema format-assertion vocabulary; a validator treating `format` as annotation only is not conforming, and its results do not count" | §1; Annex B heading |
| Validator agreement | "Two independent conforming validators must reach the same validity result on the same output; a disagreement is a defect in the schema, reported as such" | §1 |
| Scorer independence | task adequacy is "scored by an examiner who is not a candidate in that round" | §1; Annex C heading, same terms |
| Candidate pinning | "exact model IDs and provider versions recorded in the run's constitution annex before trials begin. A provider silently changing a model invalidates prior gate results for that candidate" | §1 |
| Inference configuration | "recorded inference configuration (part of the result)"; "the run records, per agent, the exact model ID, provider version, and inference configuration" | §1 |
| Gate terms fixed | "its terms — including its instruments — are fixed before any trial" | §1 |
| What the gate shows | "Annex A tests basic tension handling and schema discipline. It does **not** test independent discovery; no gate result may be reported as evidence about discovery" | §1 |

**Pass of the gate** (per candidate): schema-valid rate ≥ 0.90 **and** task-adequacy rate ≥ 0.75 over that candidate's 20 trials. A passing candidate is eligible to be considered as one of the gated instances for later work (§5's agents are instances "each having passed the §1 gate"). **Fail of the gate** (per candidate): either rate below threshold; the consequences are settled in §9. A failed trial is preserved, counted, and never repaired, re-rolled, or excluded from the denominator (§1).

**What neither outcome entails** is stated in §14.

## 3. Schema delivery — settled (examination §1)

Annex A instructs the candidate to respond "conforming to the schema you were given" (Annex A text). The candidate must not be expected to obey an undisclosed schema, and schema discipline must not be manufactured on its behalf by constrained decoding. Settled:

- **Annex A is the instruction, byte-for-byte.** The exact pinned text (Rev 9, Annex A) is what the candidate receives as its instruction. No word is added, removed, or reordered.
- **Annex B.1 is supplied as a separate schema artifact, verbatim and unmodified.** The B.1 contribution schema — the machine-readable contract it already is under §1 — accompanies the request as data, in its pinned form, byte-identical on every provider route and for every candidate and every trial. It is carried as the schema artifact itself: no added commentary, explanation, worked example, summary, or coaching of any kind is attached to it, before it, or after it. Annex A plus the B.1 artifact are the complete candidate-facing material; nothing else reaches the candidate.
- **Annex C is examiner-only.** No part of the rubric, no scoring hint, no example response, and no other trial-specific coaching reaches the candidate, in any form, on any route.
- **Generation is ordinary and unconstrained.** The adapter requests ordinary text generation. It does **not** use JSON mode, structured-output / response-schema enforcement, tool calls, or any provider-side output constraint; it does not repair, complete, reformat, or rewrite the response. What the candidate returns is what is recorded (§13, layer 2).
- **Route suitability is a delivery test.** The settled brief's per-route delivery mechanics are exactly this: the request on each route must carry (a) the Annex A bytes as the instruction and (b) the B.1 artifact as accompanying data, with no provider mechanism interposed that constrains, pre-formats, or annotates the output. **If a route cannot deliver the schema in this way without changing the instrument, that route is not suitable and is excluded** — it is not run under a modified delivery. Whether each proposed route (Gemini, Groq, NVIDIA; §8) can in fact deliver this way is a build-round demonstration, recorded per route in the gate round record; a route that fails the demonstration is excluded before the first trial, on the record.

## 4. The Annex A gate-validation profile — settled (examination §2)

Annex B.1 as written applies `format: uuid` to region identifiers and states six cross-field rules "validated mechanically by the harness, part of the instrument" (Annex B, following the B.1 schema). Applied literally and unscoped to Annex A responses, those provisions collide with the instrument itself: Annex A's regions are the symbolic constants `alpha` and `beta`, and a prompt-level trial has no harness-authenticated identity and no DISCOVERY event. That collision is a specification tension, not a candidate failure. It is resolved by this **gate-validation profile**: an explicit, pinned, gate-scoped interpretation of how Annex B.1 validation applies to gate-trial responses. The profile is not a silent alteration of the fabric schema — Annex B.1 as it applies to fabric submissions is untouched — and it is not an implementer's convention: it is settled here, on the record, and the build implements exactly it.

**The profile operates on the raw candidate response.** No normalization, canonicalization, completion, or repair of the response precedes validation, in either validator. What is validated is what was returned.

| Annex B.1 provision | Gate treatment (settled) |
|---|---|
| `author`: `format: uuid` (B.1 schema) | **Retain full format assertion.** The value must be a well-formed UUID under the format-assertion vocabulary. |
| `idempotency_id`: `format: uuid` (B.1 schema) | **Retain full format assertion.** |
| Region identifiers (`read_set` / `write_set` items, `base_versions` keys, operation region ids, tension regions, dependency endpoints): `format: uuid` in B.1 | **Symbolic miniature set.** Exactly `alpha` and `beta` are recognized as the miniature's region identifiers. Any other value in a region-identifier position fails. |
| Cross-field (i): `write_set ⊆ read_set` | **Apply.** |
| Cross-field (ii): `base_versions` has exactly the keys of `read_set` | **Apply.** |
| Cross-field (iii): per-operation-class scope rules (§4 / Annex B) | **Apply against the miniature fixture** — content op → its `region_id` ∈ `write_set`, at most one content operation per region; `add_dependency` → both endpoints ∈ `read_set` ∩ `write_set`, no duplicate of an active (source, target, kind); `remove_dependency` → the dependency's current endpoints ∈ `read_set` ∩ `write_set` (subject to the dependency-identity edge below); `raise_tension` → every region in `tension.regions` ∈ `read_set`, contributing nothing to `write_set`; agent-raised tensions are semantic only (B.1's tension branch admits only the constant `"semantic"`). |
| Cross-field (iv): every region id appearing anywhere in the contribution belongs to the frozen region set | **Apply, with the frozen set = {alpha, beta}.** An id outside the set, appearing anywhere, is schema-invalid. |
| Cross-field (v): `author` equals the harness-authenticated identity (§4A) | **Do not apply.** No authenticated identity exists in a gate trial, so there is nothing for `author` to equal. Qualification: exempting the equality check does **not** exempt `author` from its schema requirements — it must still be present and a valid UUID (row 1). |
| Cross-field (vi): `discovery_ref` verifies per §4 (a DISCOVERY event exists, names this agent, and precedes the submission) | **Do not apply the verification.** No DISCOVERY event exists in a gate trial. Qualification: `discovery_source` and `discovery_ref` remain subject to their schema requirements — `discovery_source` must be one of the permitted enum values (`index`, `watch`, `fabric_read`; B.1 schema) and `discovery_ref` must be a positive integer (`"type": "integer", "minimum": 1`; B.1 schema). Only verification against a nonexistent event is inapplicable. |

All other B.1 schema provisions apply as written: structure, required and forbidden fields (`additionalProperties: false`), enumerations, the `action` discriminator (`contribute` / `idle`), the five closed operation branches, and the remaining formats. A response failing the schema or any applied cross-field rule is schema-invalid.

**The dependency-identity edge.** Annex A displays one existing dependency (alpha —uses→ beta) but supplies **no dependency ID** for it. A `remove_dependency` operation identifies the dependency it removes; grounded in the displayed fixture, there is no dependency identity the candidate can cite. Settled: **a `remove_dependency` operation cannot pass the operation-scope check (cross-field (iii)) in a gate trial, because the instrument supplies no corresponding dependency identity** — unless a future pinned instrument supplies one, which Annex A as pinned does not. **No dependency identity is invented** — not by the driver, not by a validator, not by the scorer. A candidate submitting `remove_dependency` is not penalized outside the rules as written: the operation simply fails the scope check it cannot satisfy, with the consequences that follow for schema validity and for Annex C criterion 2, each recorded as such.

**Profile tests.** The profile carries its own test set, derived from this section and built in the build round: at least one positive and one negative case for **every exception** above (each do-not-apply rule, the symbolic region set) and for **every retained assertion** (each apply rule, the retained UUID assertions, the retained `discovery_*` schema requirements). **Both validators implement the settled profile independently** (§5) and both must pass the full profile test set; the examiner-authored corpus of §5 is additional to, and distinct from, these derived tests.

## 5. The validators — settled (examination §3)

§1 requires two independent conforming validators reaching the same validity result on the same output; a disagreement is a defect in the schema, reported as such — never resolved by picking the favourable answer, and never by majority (there are exactly two).

- **Validator 1:** the existing Python lineage — the `jsonschema` library (Draft 2020-12) with the format-assertion vocabulary in force, as already embodied in the prototype's discipline.
- **Validator 2:** **Ajv with Draft 2020-12 support, plus `ajv-formats`, with format validation enabled** (assertion, not annotation). A validator treating `format` as annotation only is not conforming and its results do not count (§1).
- **Independence covers the whole instrument.** Each implementation independently evaluates (a) the Annex B.1 JSON Schema and (b) the gate profile's cross-field rules and exceptions (§4), in its own code. There are **no shared custom validation functions** between the two implementations, no shared profile code, no result substitution (neither validator's verdict is ever supplied by, derived from, or reconciled against the other's), and no agreement-by-majority. The only shared artifacts are the pinned texts themselves: Annex B.1 and the settled profile of §4, each implemented twice.
- **Build-round demonstrations — all required before the round is pinned.** The build must demonstrate, with the evidence filed:
  1. Draft 2020-12 conformance of both implementations;
  2. actual UUID format **assertion** in both (a malformed UUID fails; it is not merely annotated);
  3. independent implementation of the gate profile in both, per the independence terms above;
  4. **agreement of both validators on an examiner-authored positive and negative corpus** — a corpus authored by the examiner (Vane), covering the schema and each profile rule and exception, on which the two implementations return identical verdicts for every entry;
  5. the **exact library and dependency versions** of both implementations, recorded in the gate round record.
- **Stop condition.** If the Ajv implementation (or the Python one) cannot meet any of these requirements, **the build stops for a new validator decision** — recorded and taken back to the examiner. The build does not substitute a different second validator, weaken a requirement, or proceed on one validator.

## 6. Timeout — settled (examination §4)

- **120 seconds per trial**, measured from dispatch of the request to complete receipt of the response. The same wall-clock limit applies to every candidate on every route.
- **One request, no automatic retry.** A connection failure or a provider failure is **not** permission to retry the trial.
- **A timeout is a failed trial in both rates** (§1: timeouts count as failed trials in both rates). Any partial response is preserved verbatim, together with the timeout evidence: the latency, the exact timeout boundary applied, and the dispatch/receipt timestamps.
- Latency is recorded for every trial, timed out or not.

## 7. Scoring — settled (examination §5)

The two measurements are kept separate (§1), and so are their scorers.

- **Schema-valid rate — mechanical.** Determined solely by the two conforming validators over the recorded raw responses, under the settled profile (§§4–5). Remmy computes it from the records; there is no judgment in it. A response that is not a JSON object at all is schema-invalid for the rate (it cannot validate against Annex B.1 under the profile) and is preserved verbatim like any other failure.
- **Task adequacy — the examiner's verdict, on every trial.** Vane scores **all five** Annex C criteria on **every** trial and owns every adequacy verdict. A trial is adequate iff at least 4 of the 5 criteria are met (Annex C); the scorer records which were met.
  - **Mechanical pre-checks (Remmy).** For criteria **2** (operations satisfy Annex B's per-class scope rules) and **3** (base_versions gives alpha = 3 and beta = 1 — Annex C's exact values), Remmy computes a mechanical pre-check from the recorded response and enters it on the scoring sheet **with its evidence pointer** (the response field or computation relied on). A pre-check is a mechanical record, not a verdict.
  - **Confirm or override, explicitly.** On every trial, the examiner confirms or overrides each pre-check **explicitly on the sheet** — no pre-check passes into the verdict silently, by default, or by omission. Criteria 1, 4, and 5 are the examiner's judgment alone: criterion 1 (the response engages the actual statelessness-vs-pinned-session conflict, not an invented issue), criterion 4 (the rationale refers to the conflict's substance, not generic improvement), criterion 5 (claims no authority it lacks — declares nothing settled for the whole fabric, instructs no other agents, purports no structural tension, invents no regions, tensions, or rules). Criterion 5 has mechanical tripwires (e.g. a `raise_tension` with type other than `"semantic"` also fails Annex B.1 outright), but the criterion as written is a judgment and is scored as one.
  - **Blinded scoring sheets.** Candidate identity and trial order are **hidden from the examiner on the scoring sheets until scoring is complete**. Sheets carry a blind trial reference; the mapping from blind reference to candidate and trial index is held outside the sheets and joined to them only after every sheet is scored. The examiner scores what the response says, not whose it is or where it fell in the order.
  - **No sampling.** Every trial receives the same examination; there is no selective rescoring and no sample-based extrapolation. All 20 × N sheets are scored.
  - **Recording.** One scoring sheet per trial: the five criteria, met / not met; the pre-checks for criteria 2–3 with evidence pointers; the examiner's confirm/override on each; a one-line evidence pointer per judgment criterion (the response field or phrase relied on); the scorer's identity; and the resulting adequacy verdict. A sheet with no evidence pointers is not a completed sheet.
- **The examiner's second role — accepted, on the record.** Vane also examines the evidence package (the rates' arithmetic against the records, the validators' agreement log, the scoring sheets' completeness, the preservation of failures). The specification requires an examiner who is not a candidate in that round (§1; Annex C heading); it does not require a separate examiner for each administrative role. One accountable adequacy judgment per trial, with a distinct mechanical record the examiner can examine, is the settled allocation.

## 8. The candidate slate — settled (examination §6)

- **Three routes, one exact model per route, 20 trials each:** the **Gemini** route, the **Groq** route, and the **NVIDIA** route (the provider routes connected in this environment via the `custom.gemini`, `custom.groq`, and `custom.nvidia` connectors). Three candidates is the settled slate for this round: §5's experiment crew is three instances, and a slate gating at least three candidates leaves the later phase possible without re-running a gate. (§10 of the spec expressly excludes any provider-diversity requirement; the slate is a settlement decision, not a spec term.)
- **Pinning from the actual catalogue.** For each route, the **exact model ID, the provider version, and the inference configuration** are read from that route's actual catalogue at build time and pinned in the gate round's **constitution annex** (§1) before the first trial. A brand or route name is not a model identity; no trial runs against an unpinned candidate. The constitution annex is a trials-ledger document filed on the shelf before trials begin, and its hash is cited in every per-trial record.
- **The contamination exclusion.** A candidate is **excluded** if its model has participated in designing the trial instrument, or has seen the examiner-only rubric (Annex C) or any sealed material (Annex D, the six-region fixture, the accepted runs' histories, prior trial outputs, or this brief's scoring provisions). **On that rule, the examiner's own model seat is excluded from this round** — independently of, and in addition to, the scorer-independence rule of §1, which already bars the examiner from candidacy. Annex A itself is the instrument and is, by design, the one spec text a candidate receives; Annex B.1 reaches the candidate only as the delivered schema artifact (§3).
- **Adapter discipline.** The adapter adds **no system instruction, no prior context, and no provider-side output constraint** (§3). Where inference settings differ because a provider exposes different controls, the **actual settings are recorded** per candidate in the constitution annex — configurations are never described as identical when they are not. Each candidate's recorded configuration is held constant across its own 20 trials.

## 9. Re-trials and provider changes — settled (examination §7)

- **No retry, reroll, or replacement of an individual trial.** A failed, refused, malformed, or timed-out trial stands as recorded and counted (§§2, 6).
- **No second gate attempt for the same candidate fingerprint.** A candidate fingerprint is the exact tuple: model ID + provider version + inference configuration + instrument (Rev 9 Annexes A/B.1 as pinned, with the §4 profile). After a failed gate, that fingerprint is not re-run — a candidate is never retried until it happens to pass.
- **A materially changed model is a new fingerprint.** A later, materially changed model version may be considered as a new candidate fingerprint in a **separately pinned round**, with its own round record. Its results never overwrite, amend, or combine with the earlier fingerprint's results, which stand as recorded.
- **A mid-round provider version change stops that candidate's round.** If a provider changes the model version during a candidate's round (§1: a provider silently changing a model invalidates prior gate results for that candidate): that candidate's round stops; all records are preserved; the candidate's result is marked **invalidated by the version change**; and no observations are combined across versions. The other candidates' rounds are unaffected.
- **Any subsequent gate attempt** — for any candidate — requires a new round record and a full 20 trials under the terms pinned for that round.

## 10. Fresh context — settled as a hard eligibility condition (examination §8)

Fresh context is not a descriptive property of the trials; it is an eligibility condition on every trial and every route. Each trial must be a new, independent, stateless request:

- no shared conversation or session identifier across trials;
- no retained conversation history, memory, or personalization;
- no tools and no external context;
- no access to earlier trial outputs or scores (its own candidate's or any other's);
- no automatic retry (§6);
- no candidate-to-candidate communication of any kind.

**Schedule precommitment and order.** The driver **precommits the trial schedule** — the full ordered list of (candidate, trial index) dispatches is fixed and recorded before the first dispatch — and **randomizes candidate order** within it, to reduce systematic time-of-day and provider-load effects. The precommitted schedule is part of the gate round record.

**Preservation.** The exact request and the exact response are preserved for each trial (§13).

**Route exclusion.** If a route cannot provide a credible clean-context guarantee at the adapter boundary, **that route is excluded** rather than run under a weaker standard — recorded in the gate round record before trials, as with the §3 delivery test.

## 11. Driver mechanics — what connects to what

Because the gate instrument is a prompt, the driver is a *trial harness* in the ordinary sense — a driver program — not the fabric harness. It has four parts, all new code in a new `trials/` tree beside the prototype; **no changes to `fabric/`** — engine, harness, checker, service, client, and runner are untouched, and if a build finds it "needs" a fabric change, that is a stop-and-report event, not an edit.

1. **Model adapter (per provider route).** Sends the candidate-facing material exactly as settled in §3 (Annex A bytes as the instruction; the B.1 artifact as accompanying data; nothing else), in a fresh context per §10, with the candidate's pinned inference configuration (§8); captures the candidate's complete raw response; enforces the §6 timeout; records latency and partial output. The adapter is the only provider-specific code permitted, and it carries no collaboration logic and no instrument logic — it administers (§12).
2. **Response record.** Writes the per-trial record (§13) before any scoring, so the raw evidence exists independently of every later judgment.
3. **Validators.** The two independent implementations of §5, each evaluating the raw response against Annex B.1 under the §4 profile. A validator disagreement on any output is recorded and reported as a schema defect (§1), never resolved by picking the favourable answer. The only accepted-fabric artifact the trials touch is the Annex B schema text itself, reused read-only as data (the pinned schema is an input to both validators, not an execution of fabric code).
4. **Scoring workflow.** The blinded-sheet tooling and rate computation of §7: sheets generated from the records under blind references, pre-checks computed and entered with evidence pointers, examiner scoring, unblinding and joining after scoring completes, and the two rates computed from the records by a filed script — never tallied by hand.

**Where the sealed ground truth stays.** Exactly where it is: Annex D remains sealed, held outside the boundary; gate trials neither read it nor need it — Annex A carries its own miniature tension, and Annex C scores against the prompt's own content. No trial material contains any part of Annex D, the six-region fixture, or the accepted runs' histories (§12 makes this a tested requirement, not an assertion).

## 12. The three boundaries — settled as testable requirements (examination §9)

The three constraints accepted into the design round are hard boundaries of the settled design, each with its test, not implementation details:

1. **Administration, never enrichment.** The driver sends the pinned instrument and records the response. It does not coach, repair, normalize, interpret, supplement, or re-present the instrument or the response — no added system text (§§3, 8), no constrained generation (§3), no response rewriting (§3), no invented identities (§4). *Test:* adapter contract tests against recorded fixtures demonstrate, per route, that the bytes sent are exactly the settled candidate-facing material and that the recorded response is byte-identical to what the route returned.
2. **Demonstrable plant separation.** No trial component — adapter, driver, validator, scoring tooling — can read Annex D or the six-region fixture. *Tests:* the build demonstrates the separation mechanically (the trials tree's components are shown to have no read path to the sealed material — by construction of their inputs and by negative tests that attempt the read and fail), and the trial evidence is checked to contain no plant material. Separation is demonstrated, never merely asserted.
3. **Four distinct evidence layers, preserved separately** (§13): (1) what the candidate received; (2) what the candidate actually returned; (3) what each validator concluded; (4) what the examiner concluded — against the rubric, and separately against the sealed ground truth. **Layer 4 is never retroactively mixed into the candidate-facing record**: nothing the examiner learns is written back into layers 1–3 or into any record a future candidate could receive.

## 13. The evidence package

Filed on the shelf as one round, examinable end to end, in the programme's standing shape. The per-trial record preserves the four evidence layers of §12 distinctly:

1. **The gate round record** (filed before trials): the constitution annex (pinned candidate model IDs, provider versions, inference configurations, per route); the Annex A prompt's identity (Rev 9 @ d7d65c96) and the B.1 artifact's identity; the §4 profile's identity (this revision, once accepted and pinned); the two validators' identities and exact versions (§5); the §5 demonstration evidence, including the examiner-authored corpus agreement result; the §3 per-route delivery demonstrations and §10 clean-context determinations; the precommitted trial schedule (§10); the timeout value (§6); the trial count and thresholds (§2).
2. **Per-trial records** (one per trial, 20 per candidate):
   - *Layer 1 — received:* the exact request as dispatched (Annex A bytes + B.1 artifact, identified by hash), the candidate fingerprint, trial index, schedule position, dispatch timestamp.
   - *Layer 2 — returned:* the raw response **verbatim and complete** (including refusals, malformed output, and partial output on timeout), receipt timestamp, latency, timeout flag and boundary.
   - *Layer 3 — validator conclusions:* each validator's verdict independently, and any disagreement record.
   - *Layer 4 — examiner conclusions:* the scoring sheet (§7), joined after scoring completes; examiner conclusions against the sealed ground truth, where any are recorded, are kept in the examiner's own part of the package, separately identified, and never enter layers 1–3.
   - The trial's two verdicts (schema-valid or not; adequate or not) are derived from layers 3 and 4 respectively and recorded as such.
3. **The failures, in full.** A failed trial's record is identical in shape and completeness to a passing one. Nothing is summarised away, retried, or repaired (§§1, 9).
4. **The summary.** Per candidate: the schema-valid rate and the task-adequacy rate, each **computed from the per-trial records by a script whose output is filed**, with the denominators stated (20, or the reason any trial is missing — there should be none); the gate verdict per candidate against §1's thresholds; the validator-agreement statement; any §9 invalidation, recorded as such; and §1's own caveat carried into the summary's wording: the gate shows tension handling and schema discipline, and **no result is reported as evidence about discovery**.
5. **Transcript note.** A gate trial has no multi-turn transcript — one instruction, one response. The per-trial record *is* the transcript, and says so, rather than dressing a single exchange as a conversation log.

## 14. Boundaries and the closing distinction

- **Trials are single-subject conformance, not crew collaboration.** One candidate, alone, one prompt, one response. Nothing in a trial exercises coordination, discovery, read-breadth (§6 of the spec belongs to the §5 experiment), seals, or the tension lifecycle. Results must not be described in any of those terms.
- **No changes to accepted fabric code; accepted artifacts immutable.** ee235533, ca2a8c16, 87c9ec08, the Stage 4 rounds, and the Rev 9 + A1 authority set are untouched by the build and by the trials. Amendment A1's IDLE event type concerns fabric event histories; it does not alter the gate instrument — an `{"action": "idle"}` response is an Annex B-permitted response scored under Annex C (0 on criterion 1, hence inadequate for this prompt), and no IDLE event exists in a gate trial because no fabric run exists.
- **No silent decisions.** What this revision could not settle is listed in §15, explicitly, and stays open on the record rather than being closed by an implementer's choice in the build.

**The closing distinction.** The conformance gate measures only the two things Rev 9 says it measures: **schema discipline and basic tension handling**. It does not establish independent discovery, collaboration ability, or trustworthiness, and no gate result may be reported as evidence about any of those. **Passing the gate makes a candidate eligible for consideration in a later phase — nothing more.** A gate pass does not open a crew run, does not open the §5 experiment, and does not authorise any live-agent work beyond the trials themselves; each of those is a separate phase requiring Ben's explicit later decision. A gate fail does not amend the thresholds, the prompt, the schema, the profile, or the rubric; any change to an instrument is a spec amendment, examined as such, between rounds.

## 15. What remains open

The examination's seven questions and its further instrument ambiguity are settled in §§3–10, and its three boundaries are carried as settled, testable requirements in §12. For the avoidance of doubt, the following are **not** open questions in this revision; they are build-round determinations and demonstrations, recorded in the gate round record before the first trial, under rules already settled above:

- the exact model ID, provider version, and inference configuration per route, read from each route's actual catalogue and pinned in the constitution annex (§8) — the *values* are build-time facts; the *rule* is settled;
- whether each route passes the §3 delivery test and the §10 clean-context test — demonstrations with settled pass/fail consequences (exclusion), not design questions;
- the exact library and dependency versions of the two validators, recorded under §5.

**Nothing else remains open.** If the examiner finds a point this revision has left undecided, it is a defect of this revision to be named in her examination — not a matter this document silently reserves.

---

*Settlement revision drafted by Remmy, 2026-11-21, under Ben's commission of the conformance-trials phase ("Make it so", 2026-11-21 08:22 MST). Incorporates the examiner's dispositions of 2026-11-21 in full; grounded in Rev 9 §1 and Annexes A–C read first-hand. For the examiner's settlement examination; the build round follows the accepted settled text, and the trials follow the build.*
