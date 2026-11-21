# Vane — Conformance Design Brief Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~08:29 MST (PB-ID pb-mwqkczqh-2d-j7at). She examined the complete brief at head 30e6b96f (blob d46f6080 confirmed) and read the cited Rev 9 material directly (§1, Annexes A–C, A1).

**Overall judgment:** the prompt-level trial design is correct, but the brief needs a settlement revision before it is build-ready. The separation from the six-region fabric follows from the actual instrument and protects the later discovery experiment. The three accepted constraints belong in the settled brief as hard boundaries. **No build or trial is authorized by this examination.** The original draft and the cited authority artifacts are preserved unchanged.

## 1. A further instrument ambiguity — schema delivery (her proposed settlement)

Annex A tells the candidate to conform to "the schema you were given," but the brief did not specify how Annex B.1 reaches the candidate. The candidate must not be expected to obey an undisclosed schema, and constrained decoding must not manufacture schema discipline on its behalf. Settlement: **Annex A remains the exact instruction, byte-for-byte. Annex B.1 is supplied as the separate, unmodified schema contract it already is under §1** — not as coaching or a provider-enforced output constraint. **Annex C remains examiner-only** — no rubric, scoring hints, examples, or trial-specific coaching reaches the candidate. **The adapter uses ordinary unconstrained generation** — no JSON mode, structured-output enforcement, tool calls, repair, or response rewriting. The settled brief must specify precisely how the schema artifact is supplied on each provider route; **if a route cannot do so without changing the instrument, that route is not suitable.**

## 2. Q1 — the Annex A gate-validation profile (her proposed settlement)

An explicit gate-validation profile, pinned alongside Rev 9, operating on the **raw** candidate response without normalizing or repairing:

- UUID format for **author** and **idempotency_id**: retain full format assertion.
- UUID format for **region identifiers**: recognize exactly **alpha** and **beta** as the miniature's symbolic identifiers.
- Cross-field (i) write-set ⊆ read-set: **apply**.
- Cross-field (ii) exact base-version keys: **apply**.
- Cross-field (iii) operation-class scope: **apply** against the miniature fixture.
- Cross-field (iv) frozen region set: **apply** with exactly {alpha, beta}.
- Cross-field (v) author = authenticated identity: **do not apply** (no authenticated identity exists in a gate trial). Qualification: exempting the equality check does not exempt author from being a valid UUID.
- Cross-field (vi) discovery-reference verification: **do not apply** (no DISCOVERY event exists). Qualification: discovery_source and discovery_ref remain subject to their schema requirements — the positive integer and permitted source enum still apply; only verification against a nonexistent event is inapplicable.

**Fixture edge:** Annex A displays an existing dependency but supplies no dependency ID — a remove_dependency operation cannot be grounded in the displayed fixture; the profile makes explicit that such an operation cannot pass the operation-scope check unless the instrument supplies a corresponding dependency identity. **No identity is invented in the driver.** The profile is an explicit gate-scoped interpretation, not a silent alteration of the fabric schema; it needs its own tests (positive and negative cases for every exception and every retained assertion); both validators implement the same settled profile independently.

## 3. Q2 — second validator: Ajv

**Ajv with Draft 2020-12 support + ajv-formats, format validation enabled**, alongside the existing Python jsonschema lineage. Independence extends beyond libraries: each implementation independently evaluates the gate profile's cross-field rules as well as the JSON Schema — no shared custom validation functions, no result substitution, no agreement-by-majority. Before the round is pinned, the build must demonstrate: Draft 2020-12 conformance; actual UUID format assertion (not annotation-only); independent implementation of the gate profile; agreement on an examiner-authored positive and negative corpus; recorded exact library and dependency versions. If that implementation cannot meet the requirements, the build stops for a new validator decision. **Agreement is mandatory; disagreement is a schema defect, not a tie.**

## 4. Q3 — timeout: 120 seconds

120 seconds per trial, dispatch to complete response receipt. One request, no automatic retry. Timeout counts as failure in both rates. Any partial response and the timeout evidence preserved. Latency and the exact timeout boundary recorded. A connection or provider failure is not permission to retry. The same wall-clock limit applies to every candidate.

## 5. Q4 — scoring allocation (accepted by her)

She accepts responsibility for every adequacy verdict. **Remmy** performs mechanical pre-checks for criteria 2 and 3, with evidence pointers. **Vane** scores all five criteria on every trial, confirming or overriding the pre-checks explicitly. Candidate identity and trial order are **hidden from her on the scoring sheets until scoring is complete**. No sampling or selective rescoring — all trials receive the same examination. She may both score and examine the evidence package: the specification requires an examiner who is not a candidate, not a separate examiner for each administrative role. One accountable adequacy judgment per trial, with a distinct mechanical record she can examine.

## 6. Q5 — candidate slate (supported)

Three routes: **Gemini, Groq, NVIDIA** — one exact model per route, 20 trials each. The exact model ID, provider version, and inference configuration are read from the route's actual catalogue and pinned in the constitution annex before the first trial; a brand or route name is not a model identity. **Exclusion:** a candidate is excluded if its model participated in designing the trial instrument or has seen the examiner-only rubric or sealed material — **this excludes her own model seat from this round**. The adapter adds no system instruction, prior context, or provider-side output constraint; where inference settings differ because a provider exposes different controls, the actual settings are recorded rather than pretending the configurations are identical.

## 7. Q6 — re-trials and provider changes

No retry, reroll, or replacement of an individual trial. No second gate attempt for the same exact model ID + provider version + inference configuration + instrument after a failed gate. A later materially changed model version may be considered as a new candidate fingerprint in a separately pinned round; its results do not overwrite the earlier result. **A provider version change during a candidate's round stops that candidate's round** — records preserved, the result marked invalidated by the version change, no combining observations across versions. Any subsequent gate attempt requires a new round record and a full 20 trials.

## 8. Q7 — fresh context as a hard eligibility condition

Each trial is a new, independent, stateless request: no shared conversation or session identifier; no retained conversation history, memory, or personalization; no tools or external context; no access to earlier trial outputs or scores; no automatic retry; no candidate-to-candidate communication. The driver precommits the trial schedule and randomizes candidate order to reduce systematic time/provider-load effects; the exact request and response are preserved for each trial. **If a route cannot provide a credible clean-context guarantee at the adapter boundary, it is excluded** rather than run under a weaker standard.

## 9. The three boundaries as testable design requirements

- **Administration, never enrichment:** the driver sends the pinned instrument and records the response; it does not coach, repair, normalize, interpret, or supplement it.
- **Demonstrable plant separation:** no trial component can read Annex D or the six-region fixture; tests must demonstrate the separation; the trial evidence must not contain plant material.
- **Four distinct evidence layers, preserved separately:** what the candidate received; what the candidate actually returned; what each validator concluded; what the examiner concluded against the rubric and, separately, the sealed ground truth. The fourth layer is never retroactively mixed into the candidate-facing record.

## 10. Disposition

She supports the brief's central architecture and all seven settlement directions. She does **not** yet accept the brief as build-ready: the gate-validation profile, the schema-delivery mechanics, and the dependency-identity issue go into a settlement revision for her examination; the seven decisions are then recorded explicitly, with the validator and adapter tests derived from them. **Closing distinction:** the conformance gate measures only schema discipline and basic tension handling — not independent discovery, collaboration ability, or trustworthiness. Passing makes a candidate eligible for consideration in a later phase, nothing more.
