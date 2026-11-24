# Vane — adapter build examination: two corrections; the probe-suite failures ruled superseded (2026-11-24)

Received via Pulse Bridge (PB pb-mwv5t3pj-5-jrrg), 2026-11-24. Filed at INDEX 403.
(The same letter's opening repeated her 13:39 acknowledgement — the examination
proper follows it in the same PB; treated as one letter.)

She examined the submitted letter and the actual `adapter.py`, `loop.py`,
`schema_validator.py`, `record.py`, checker and test sources. She has **not**
independently run the reported 42 checks.

**What passes:** B1 (extraction preserves IDs/ordinals, both argument forms,
mixed content+calls rejected whole). B2 (validator pure and strict; the
declaration-list format matches the actual A3-CAT worker-facing schema — not
JSON Schema, consistent with the settled catalogue contract: flagged reading 2
resolved in the build's favour). B3 (translation record persisted before
dispatch; the ordinary doorway the only route to execution). B4 (provider IDs
are correlation references alongside framework identities; results and refusals
return through the next package). B5 (the checker has its own extraction,
classification and validation; it does not import the framework validator).
BD-2 correctly absent — no promotion of `failed_generation` into a tool call.

**⭐ The probe-suite ruling:** the three failures are **superseded assertions,
not new adapter defects** — the old `tool_requests` expectation superseded by
the `native_calls` extraction boundary; the old fail-whole argument expectation
superseded by per-call refusal; the old doorway-level unknown-tool expectation
superseded by closed-world translation refusal. The new suite witnesses the
replacement behaviour. **Keep the old suite untouched under this build scope;
preserve its status honestly as 54 passing and three obsolete assertions
failing; it must not be reported as an all-pass regression suite.**

**Correction 1 — provider call-ID integrity must precede the cap refusal.**
In `Loop._classify_native` the order is: record the ID in `seen_ids` → check
ordinal > CALL_CAP → only then check absent/duplicate ID. With CAP = 1, every
call after the first is refused `call_cap_exceeded` before its ID integrity is
examined, so a missing or duplicated ID on an overflow call never receives the
N6 `malformed_call` classification. The checker repeats the same ordering —
it reproduces rather than catches the discrepancy. **Move the missing/duplicate
checks ahead of the cap check in both implementations** (the cap still precedes
name resolution, argument parsing, and schema validation; overflow arguments
are never processed). Add actual CAP = 1 witnesses: a second call with a
missing ID; a second call duplicating the first call's ID — both receive the
N6 classification, retain their ordinal, and cause no dispatch. This does not
change Ben's cap ruling. *(This settles flagged reading 4 against the builder's
framing: the duplicate-ID refusal is not "unreachable by construction" — under
the correct ordering it is reachable and required.)*

**Correction 2 — BD-1's flag commitment needs a stronger binding.** The loop
reads `self.model.disable_tool_validation` to record the flag on LOOP_ITERATION;
the adapter later re-reads that mutable attribute to stage the request body —
two reads, not one immutable per-iteration value; committed and transmitted
states could diverge. Checker gap: it treats the flag's presence on the
iteration event as the native-mode indication and does not independently
require the field on every iteration of an assembly whose sealed ASSEMBLY_PACKED
mode is native — a missing field can conceal the native translation obligation
when no translation record exists. **Required:** snapshot the flag once for the
iteration; pass that exact snapshot into request construction rather than
re-reading the mutable attribute; the checker derives native mode from the
sealed assembly judgement and pack, requires a boolean flag commitment on
every native iteration, and detects missing translation records accordingly.
The two-state tests are useful but do not establish this binding under a
changed or missing commitment.

**Disposition: build not yet passed.** Bounded corrections to the
implementation and its independent examination — no reopening of the design
or Ben's CAP decision. Return the corrected source, checker, and focused
witnesses for another examination. No provider request or live worker release
follows from this examination. The NVIDIA correction is acknowledged and will
be examined on its own submission, gates unmixed.
