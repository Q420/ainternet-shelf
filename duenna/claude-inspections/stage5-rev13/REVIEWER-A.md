# Rev 13 inspection: sections 3.1 to 3.4 and 3.6 to 3.7 (agent A)

Source: /mnt/user-data/attachments/475f6377-dfad-5672-a7f4-a435c6bdea33/581de8c8-attachment.txt

Lines read in full: 541 (1861 to 2155 = 295 lines; 3273 to 3518 = 246 lines). Cross-reference checks also read in full: 1767 to 1781 (section 2.1), 3681 to 3730 (section 5, G1), 3876 to 3950 (section 6.3). Grep was used for headings and anchors only.

Count: High 3, Medium 15, Low 8.

---

## High

**A-1 | High | lines 2010 to 2012 (refusal behaviour); 3706 to 3707 (G1)**
Quote: "returns `{refused: true, reason, claimed, recomputed}`" and "returns **no** value".
Problem: The refusal object carries a `recomputed` field whose content is not defined. If it holds the recomputed value, or the candidate list for an AMBIGUOUS result, the refusal returns a value. That contradicts "returns no value" in the same sentence, and G1 says a value returned in any test fails the build. The S5 case (AMBIGUOUS, "no value") is exposed the same way.
Fix: Define the refusal object's fields exactly: `refused`, a reason code, `claimed_source_hash`, `recomputed_source_hash`, a recomputed outcome label (EXTRACTED, AMBIGUOUS, NOT FOUND, TYPE FAILURE), and a count of valid matches. No value, candidate text or evidence line. Full detail goes only into the GOVERNANCE_EVENT. Add a G1 check that the refusal object's key set equals this list.

**A-2 | High | lines 3341 to 3343 and 3361 to 3363; cf. 2128 to 2134**
Quote: "is redacted before writing" and "its `response_body_raw` verbatim".
Problem: Response bodies must be kept verbatim, with `response_body_sha256` taken over the raw bytes (2128 to 2134). Section 3.6 also requires any error body quoting a header to be redacted before writing. Both cannot hold for the same body: redaction changes the bytes, so either the hash no longer matches the wire or the body is not verbatim. The "redaction test" at 3362 to 3363 names no canary, pattern or pass criterion, so a builder must invent it.
Fix: Pick one rule. Preferred: store the raw body verbatim in an access-restricted file under the run directory, hashed as received; store the redacted copy in the capture as `attempts[].response_body_redacted` with its own hash and a `REDACTED` event. State the redaction rule (exact header names, and token patterns such as Bearer strings or the connector's surrogate string). Test: a forced 401 whose body echoes a canary Authorization value must leave the canary absent from every capture and run file.

**A-3 | High | lines 3420 to 3422 and 3437 to 3439; cf. 3888 to 3889 (section 6.3 item 2)**
Quote: "implementing the `complete()` contract's harness side" and "the stub responder sits behind the adapter".
Problem: Two incompatible placements. Reading 1: the stub replaces `complete()` on its harness side, so the adapter's capture path never runs. Reading 2: the stub is the far end of the adapter's own HTTP path, so `complete()` runs its full capture. The synthetic-capture requirement (3437 to 3447) and the 13-instance record at G4 need reading 2. Section 6.3 item 2 says "behind the adapter boundary", which also supports reading 2. But under reading 2 the stub is a loopback endpoint like the transport double, and 3458 to 3459 says the two "neither substitute for the other" without saying how they differ on the wire. A builder must choose.
Fix: State the placement. Stub: a loopback HTTP endpoint returning scripted model-level responses, with the adapter's real HTTP path and capture path running. Transport double: a loopback endpoint returning scripted wire events (status, body, timing). Name which one exercises the retry and 429 behaviour and which one produces the 13 synthetic captures.

**A-4 | Medium | lines 3366 and 3375 to 3376**
Quote: "a 400 rejecting the pinned envelope" and "whose preserved body identifies that field".
Problem: The section 4 taxonomy makes every 400 that rejects the pinned envelope an ADAPTER_FAILURE. The pre-classified 400 clause narrows the trigger to a body naming `chat_template_kwargs`. A 400 rejecting `max_tokens` or `top_p`, or a 400 naming no field, is then covered by 3366 or by nothing. The builder would have to choose.
Fix: One rule: any HTTP 400 on the pinned request is an ADAPTER_FAILURE, never retried. The naming of the field in the body is evidence, not a condition. Delete "whose preserved body identifies that field" as a trigger.

**A-5 | Medium | lines 3292 to 3294, 3308 to 3309, 3452 to 3454**
Quote: "must equal the helper's MODEL argument on every call" and "never the pinned model id".
Problem: Section 3.6 requires `model` to equal the pinned id on every call, and classifies a different served id as ADAPTER_FAILURE. Section 3.7 requires a synthetic capture to carry the stub's name as its subject identity, not the pinned id, and to pass through the adapter's full capture path. Under the pinned-identity rule, a stub response naming a different model is an ADAPTER_FAILURE. No mode for the identity check is defined, so a builder must add an exception to a pinned rule, which section 2.1 forbids without asking.
Fix: Define a stub-mode identity branch: the served-id check compares against the stub configuration's name only when RUN_STARTED pins that configuration's hash. Add a test that the live configuration refuses a stub-named response.

**A-6 | Medium | lines 3428 to 3431**
Quote: "no scored run can be configured to use it".
Problem: The stub is "selected by pinned test configuration in scratch contexts only", but no mechanism stops a scored run from selecting it. Section 3.7 itself says enforcement, not wording, is what makes a no-contact rule a fact. Here the rule is wording only.
Fix: Compare the RUN_STARTED configuration hash against an allowlist fixed at Batch 0 that excludes the stub configuration. The harness refuses any other hash. Add an examiner check that rejects any run whose RUN_STARTED pins a stub configuration unless the run is labelled scratch.

**A-7 | Medium | lines 3482 to 3484 and 3487 to 3493**
Quote: "refuses any non-loopback base URL".
Problem: The check is stated against the configured URL, not the address the connection reaches. A hostname resolving outside loopback, an IPv6-mapped address, or an HTTP redirect from the loopback double to an external host would all pass a string check. Redirects are not addressed. G1's zero-egress check backs this up, but 3.7 presents (a) as a separate layer.
Fix: Require that (i) the resolved peer address is checked on every connection, including after any redirect, and (ii) redirects are disabled in Stage 5 mode. Add two tests: a hostname resolving to a non-loopback address, and a loopback endpoint returning 302 to a non-loopback URL. Both must fail closed with no outbound attempt.

**A-8 | Medium | lines 3364 to 3370; cf. 3277 to 3281, 3335 to 3337**
Quote: "recorded as a pre-flight failure, no call made".
Problem: ADAPTER_FAILURE is said to be "determined ... at capture time", and every call produces one capture. A pre-flight failure involves no call, so there is no capture. The adapter writes only captures and the harness writes only inside the run directory, so no artefact is named for the pre-flight event. It is also unclear whether pre-flight runs before RUN_STARTED, when no run record exists.
Fix: Name the artefact that records a pre-flight failure, its schema, and whether it exists before or after RUN_STARTED. Amend "determined ... at capture time" to exclude pre-flight.

**A-9 | Medium | lines 3280 to 3281 and 3335 to 3336**
Quote: "`capture_record_id` is returned in **all** outcomes".
Problem: The capture is written before the adapter returns, but nothing says what happens if the capture write fails (disk full, permissions, interrupted write). Then there is no `capture_record_id`, so the all-outcomes rule cannot hold, and an exception crosses the boundary, which section 3.6 forbids. G2 tests interrupted writes but does not name the adapter's outcome for a failed capture write.
Fix: Specify that a capture-write failure makes `complete()` raise a distinct CAPTURE_WRITE_FAILED error, returns no result to the harness, and makes the harness halt the tree as an infrastructure failure. Add it to the taxonomy and to G2's test list.

**A-10 | Medium | lines 3282 to 3284**
Quote: "`raw_output` is `choices[0].message.content`".
Problem: The spec says `raw_output` is the content field and that reasoning is part of the same artefact. Many OpenAI-compatible servers return reasoning in a separate field, leaving `content` without it. If so, the two statements conflict and the examiner's check cannot be written. The spec does not establish which the endpoint does; only the first live call (Stage 6) would show it. Truncation (finish_reason = length) has no rule anywhere in this section.
Fix: State which wire field(s) the adapter reads and what each contains, as confirmed by Adapter section 5. Otherwise define `raw_output` as the verbatim `choices[0].message` object and drop the claim that `content` includes reasoning. Add a rule recording finish_reason in the capture and classing a length stop.

**A-11 | Medium | lines 3316 to 3323 and 3329 to 3333**
Quote: "deviating on any of temperature / top_p / reasoning_budget".
Problem: The mechanical calibration check names four values. The envelope also pins `enable_thinking: true` (inside `chat_template_kwargs`), `stream: false` and `model`, and the retry policy (2 attempts, 5 s) and timeout (120 s) are pinned too. A freeze with thinking disabled passes the stated check.
Fix: Make the mechanical check cover every pinned envelope field and every policy value: model, temperature, top_p, max_tokens, stream, enable_thinking, reasoning_budget, retry count, retry delay, timeout. "Any" should refer to that full set.

**A-12 | Medium | lines 1899 to 1900, 1913 to 1914, 3381 to 3384**
Quote: "[MODEL] step 300 s".
Problem: The 300 s budget is stated per step, but section 3.1 re-attempts steps (return-once recoveries, bounded corrections). One `complete()` call can take 2 x 120 s + 5 s = 245 s under the section 3.6 timeout and retry rule, so any re-attempt exceeds 300 s if the budget spans the step. The spec does not say whether the budget resets per attempt. Also, failure branches are "the trees' rules, no others", and a budget breach is not one of them, so the breach outcome is unstated.
Fix: State that the [MODEL] budget applies per step attempt, and name the outcome of a breach: ADAPTER_FAILURE if raised inside `complete()`, otherwise a named stop, each with its record event.

**A-13 | Medium | lines 1942 to 1944 and 1946 to 1951**
Quote: "A field with no rule is NOT FOUND by declared design".
Problem: A field whose rule was omitted by a build error gives the same NOT FOUND as a field genuinely absent from the source. NOT FOUND can lead to UNKNOWN by rule (1903 to 1904). The spec says the gap is "visible in the data" but requires no check that every field a tree names has a rule. `group` semantics and the `value_type` set are undefined, and the type validator, which decides TYPE FAILURE, is not specified at all.
Fix: Require a coverage check: the field set named by the nine trees must equal the rule set in EXTRACTOR-RULES-02, or the build fails. Define the `value_type` enumeration with a validator for each type, define `group` as a 0-based capture-group index, and require that each added rule is a dated entry in the re-freeze amendment.

**A-14 | Medium | lines 1966 to 1967**
Quote: "or a prior verified extraction, cited in the record".
Problem: If `verify_field`'s `expected` may come from a prior extraction of the same source, the check compares a value with an extraction of itself. That passes whenever the extraction is internally consistent, including when it is wrong. "Verified" is undefined, so the check can become circular.
Fix: Restrict `expected` to PILOT-DATA-EXPECTED-01 for pilot verification. If prior extractions are allowed, they must come from a different source reference, and the check must say so.

**A-15 | Medium | line 1933**
Quote: "pilot-manifest data (§3.3 data files)".
Problem: Section 3.3 is the provenance rule and registry. The pilot data files (PILOT-DATA-*) are specified in section 3.2, lines 1969 to 1979. A builder following this cross-reference lands on the wrong section.
Fix: Change to "(§3.2, pilot data files)".

**A-16 | Medium | lines 3309 to 3310; cf. 1905 to 1907**
Quote: "ADAPTER_FAILURE and execution halts".
Problem: Section 3.1 says an ADAPTER_FAILURE closes the affected tree as INVALIDATED-INFRASTRUCTURE. Section 3.6 says a 404 or a different served id makes "execution halt". Read literally, that stops the run. Read as section 3.1, only the tree closes, and the run continues to the third-closure stop, which would burn trees against a model that is not served. The builder cannot tell which applies.
Fix: Decide. For a not-served model, stop the run with a named RUN_STOPPED reason and say so in 3.1. Or say "closes the tree" and remove "execution halts".

**A-17 | Medium | lines 2060 to 2066, 2099 to 2100, 2111 to 2112**
Quote: "its hash is the content of the START commitment".
Problem: Not defined in the read lines: (i) `prev_event_sha256` for the first event; (ii) which bytes `event_sha256` covers, in particular whether the event's own `event_sha256` field is excluded; (iii) whether the START commitment hashes the pinned-input block or the RUN_STARTED event. A builder cannot produce a chain that an examiner can recompute without choosing. Section 3.5 may define genesis (grep hit at line 2925); not checked in full.
Fix: Add a short definition: the preimage of `event_sha256` is the JCS bytes of the event with `event_sha256` removed; `prev_event_sha256` of seq 1 is a stated constant (for example 64 zeros); the START commitment content is the sha256 of the RUN_STARTED event's canonical bytes (or of the pinned-input block, stated). Cross-check against section 3.5.

**A-18 | Medium | lines 2005 to 2006 and 2014 to 2016**
Quote: "Exactly once, for one field".
Problem: The spec does not say whether a refused presentation consumes the entry. If refusals do not consume, a valid entry refused for a transient reason (for example a snapshot read error during recomputation) stays usable, and an identical re-presentation is not addressed. The prohibition covers only repaired or re-labelled presentations. G1 S3 tests only success followed by refusal. If refusals do consume, a transient infrastructure error permanently spends a valid extraction.
Fix: State the rule. Recommended: a presentation that reaches recomputation consumes the entry whether it succeeds or refuses; a presentation refused before recomputation (wrong context, unknown id) does not touch the entry. Add a G1 case: a refused presentation followed by an identical re-presentation must be refused.

---

## Low

**A-19 | Low | lines 1929 to 1931**
Quote: "both files' Stage 0 pins verified equal".
Problem: "The Stage 0 corpus files" is never given a count or names in this section, so "both files" is undefined here.
Fix: Name the two files in this sentence, or cite the PILOT-MANIFEST-01 rows.

**A-20 | Low | lines 2026 to 2029**
Quote: "bound to its run, tree, step, and tool invocation".
Problem: The registry field list that follows has no `run_id`, although the property requires binding to the run.
Fix: Add `run_id` to the registry record field list.

**A-21 | Low | lines 2050 to 2053**
Quote: "no fallback path ... exists anywhere in the insert call graph".
Problem: Absence of a path is not testable as written, and this section names no method for demonstrating it. The reference to G3 (line 3766, not read in full) is where a method would be named.
Fix: Name the method in section 3.3 or in G3: a call-graph listing generated from the built code, reviewed against an allowlist, plus a test that each refusal path returns with no value.

**A-22 | Low | lines 2080, 3282, 3341, 3360, 3409**
Quote: "subject outputs taken as preserved artefacts from `response_raw`".
Problem: Four names are used for the same subject output or request bytes: `raw_output` (2080, 3282), `response_body_raw` (3341), `request_raw` (3360), and `response_raw` (3409). `response_raw` is not defined in section 3.4 or 3.6, so the examiner's source for subject output is unclear.
Fix: Use one name per field, with a mapping table from capture field to record field, and have section 3.7 cite the exact field it reads.

**A-23 | Low | lines 3499 to 3504**
Quote: "Gate **G1 records the zero-egress check**".
Problem: The zero-egress check is performed once, as G1 evidence. G2 to G5 run later in the same environment, and nothing requires the check to be repeated, so the no-contact property is evidenced at one moment only.
Fix: Require the zero-egress check to be run and recorded again at each gate's evidence, with its result.

**A-24 | Low | lines 3349 to 3351**
Quote: "or implement the identical call through the same credential mechanism".
Problem: This allows a build to make its own HTTP call instead of the sanctioned helper. "Identical" is undefined, and the Batch 5 transport tests do not say they cover this path.
Fix: Delete the alternative, or require the substitute to pass the same Batch 5 tests and to produce byte-identical request bodies to the helper for a fixed recorded input.

**A-25 | Low | lines 1946 to 1951**
Quote: "more than one valid match → AMBIGUOUS".
Problem: "Match" is undefined. Overlapping matches, identical values on one evidence line, and identical values at two lines can each change EXTRACTED to AMBIGUOUS, depending on the regex engine.
Fix: Define a match as one non-overlapping regex match with the engine's semantics stated, and say whether identical values at different lines count as two candidates.

**A-26 | Low | lines 3482 to 3488, 3491 to 3492**
Quote: "in Stage 5 mode".
Problem: "Stage 5 mode" is used repeatedly and never defined. No trigger, flag or start-up check names it, so a Stage 6 build could switch proxy honouring on without any gate noticing.
Fix: Define Stage 5 mode as a pinned configuration with a named hash, recorded in RUN_STARTED and in the G1 evidence. State that Stage 6 requires a different hash.

---

## NOT CHECKED

- Lines 1 to 1860 and 2156 to 3272 were not read. Section 3.5 (2156 to 3272) is not read, including the supervisor, receipts and issuance record that section 3.7 step 0 depends on. The genesis definition (grep hit at line 2925) was not read in context, so A-17 may be partly resolved there.
- Lines 3519 to 3680 (section 4, batches) and 3729 to 3813 (G2 to G5) were not read. The G3 method for SE-1 to SE-6 (grep hit at 3766) and the G4 full battery were not read. A-21 depends on G3.
- Lines 3814 to 3875 (sections 6.1 and 6.2) and 3950 to 3963 (6.4) were not read.
- Amendment-summary history was ignored, as instructed.
- Source documents cited but not in the package were not checked against their text: Harness sections 1.1 to 1.5, 2.3 to 2.6, 3.1 to 3.5, 4.2 to 4.5, 6, 7; Adapter sections 1.2 to 1.4, 2.2, 2.3, 3.2, 3.4, 4.2, 4.3, 5, 7; Criteria sections 1.1(6), 2, 4, 5.1(6), 7.2, 8; PROCESS-TREES.md row 3; INTERPRETATION-NOTE-01. Cross-references into them were checked only against the spec's own restatement.
- RFC 8785 itself, the JCS implementation named at Batch 0, and the conformance vectors (2141 to 2154) were not verified. Number-serialisation edge cases were not checked.
- The Batch 1 value-by-value transcription check (1976 to 1979) was not checked against the Batch 1 text, which lies in the unread section 4.
- Section 6.3 item 5 (catalogue evidence, 3929 to 3948) was read and matches the cross-reference at 3302; no finding raised there.
- Line numbers refer to the Read tool's numbering of the source file.
