# REV 24 CORRECTION PLAN — 2026-11-13

Drafted by Remmy, for Alex's inspection. Answers his Rev 24 inspection
(pb-mwfr4v06-9-1tyj; NOT CLEARED: 2 HIGH, 1 MEDIUM). On his approval,
Rev 25 is drafted from the Rev 24 pin (871d90f7) incorporating exactly
what is listed here, and nothing else. Rev 24, Rev 23, Rev 22, the
original Batch 3 bundle (f11d5375) and all earlier artefacts remain
immutable. No correction implementation is authorised by this plan.

---

## Item 1 (HIGH) — one tool, two paths: the interface settled

**Finding.** §3.3 names `reference_insert_carried` as if it were a
second tool; §3.2's frozen five-tool inventory, its `reference_insert`
signature, and the logging contract know only the one tool. The
design question — sixth tool, internal entry point, or tagged union —
was left open.

**Settlement proposed: one tool, tagged-union presentation.** The
five-tool inventory is preserved exactly. `reference_insert` remains
the single insertion tool; its presentation argument is a tagged
union, and the tag selects the path:

- `{form: "extracted", operation_id}` → the EXTRACTED path
  (Batch 2's rules, unchanged).
- `{form: "carried", citation: {event_id, payload_sha256}}` → the
  CARRIED path (§3.3's carried rules).

The complete public signature is therefore
`reference_insert(field, process_step, presentation)`. There is no
externally callable `reference_insert_carried`; that name survives
only as the tool's internal dispatch target, stated as such wherever
§3.3 currently uses it as a signature — §3.3's path descriptions are
rewritten to the tagged forms above.

**Reconciliation, section by section (all in Rev 25):**

- **§3.2 inventory + signatures:** the `reference_insert` row gains
  the tagged-union presentation and one sentence: the tool has two
  paths selected by the presentation's `form` tag; the carried path
  is internal dispatch of the same tool, not a sixth tool.
- **§3.2 logging contract:** every insertion call — either path,
  success or refusal — is logged by the established
  TOOL_INVOKED/TOOL_RETURNED pair with `tool` =
  `"reference_insert"` and the invocation payload carrying
  `form` ("extracted" | "carried"), so the invocation identity of
  every carried call is unambiguous in the record. The
  LEDGER_ENTRY's `operation` field remains `"reference_insert"` on
  both paths (consistent with Rev 24's carried schema).
- **§3.3 dispatch paragraph:** rewritten to the tagged-union
  contract; malformed presentations (missing/unknown tag, both
  handles, a value accompanying a citation) refuse
  `PRESENTATION_FORM` before any consumption or mutation — the tag
  check is the tool's first act.
- **Registry (§3.3):** one registry serves the tool; it records
  extraction operations and citation consumptions as the two
  distinct sets Rev 24 already defines — no second registry, no
  second tool state.
- **Replay (§3.7):** the insert audit reads `form` from each
  invocation payload and applies that path's rules; an invocation
  whose `form` disagrees with the ledger entry's provenance form
  is a divergence.

**Tests.** The cross-form group (Item 2, assertion (r)) exercises
this contract directly: a presentation tagged "carried" carrying an
operation_id, and one tagged "extracted" carrying a citation, both
refuse `PRESENTATION_FORM` with no state change — which is only
testable because the interface is one tool with a tag.

---

## Item 2 (HIGH) — the two missing test groups enter §4

**Finding.** The approved Rev 23 plan required the cross-form
refusal group and the cross-class independence group; §4(a)–(q)
carries neither (the structural prose describes the behaviour; it
does not prove it).

**Resolution.** Rev 25's §4 acceptance list gains two named
assertions, each with state-before/state-after checks and its own
transcript lines:

- **(r) Cross-form refusal.** Setup: a live scratch registry
  holding one unconsumed extraction operation and one unconsumed
  citable artefact event; snapshot both consumption sets.
  Presentations: (i) `{form: "carried", operation_id: <the live
  operation>}`; (ii) `{form: "extracted", citation: <the live
  citation>}`; (iii) a citation accompanied by a caller-supplied
  value. Assertions: all three refuse `PRESENTATION_FORM`; no
  LEDGER_ENTRY is emitted; both consumption sets are byte-identical
  to the snapshot after each refusal (nothing consumed, nothing
  mutated).
- **(s) Cross-class independence.** Order 1: consume the extraction
  operation by its insertion → assert the citation set is unchanged
  (the citable event remains unconsumed) and the carried insertion
  then succeeds. Order 2 (fresh scratch state): consume the
  citation by its carried insertion → assert the operation set is
  unchanged and the extraction insertion then succeeds. Each order
  carries its own transcript lines and state assertions.

**Affected.** §4 acceptance list only ((a)–(q) unchanged; (r) and
(s) appended); §0K records them.

---

## Item 3 (MEDIUM) — C3-A2 enumerated completely in §4(n)

**Finding.** §4(n) asserts presence and types but does not assert
`event_type` against the closed vocabulary, nor the types and
nullability of `tree_id`/`step_id`, though the chunk sheet names
them.

**Resolution.** §4(n) is rewritten as a field-by-field enumeration
over **every** event of every record:

- `seq` — integer, strictly increasing from 1 (with C3-A1);
- `event_id`, `run_id` — strings, `event_id` of the form
  `"<run_id>:<seq>"`;
- `recorded_at_utc` — string, ISO-8601-parseable, UTC;
- `event_type` — string, **a member of the closed Harness §2.3
  vocabulary** (the seventeen types), asserted per event;
- `tree_id`, `step_id` — **string or null**: null exactly on
  run-level events (RUN_STARTED, RUN_CLOSED, RUN_STOPPED,
  GOVERNANCE_EVENT where the schema permits) and strings naming a
  declared tree/step on tree- and step-level events, per the
  §2.3 payload rules;
- `payload` — object (never a summary or pointer);
- `prev_event_sha256`, `event_sha256` — strings, 64-hex,
  present on every event (their chain validity is C3-A3's check;
  presence, type and format are asserted here).

**Affected.** §4(n) only.

---

## Drafting order on approval

Rev 25 is drafted from the Rev 24 pin incorporating Items 1–3 and
nothing else: the diff footprint is §3.2 (inventory row + logging
contract), §3.3 (dispatch paragraph + the carried subsection's
signature references), §3.7 (one clause), §4 ((n) rewritten; (r),
(s) appended), the header, and §0K. It is submitted for Alex's
inspection; the Batch 3 correction build proceeds only on his
clearance of the Rev 25 pin.
