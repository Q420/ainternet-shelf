# Native-offer probe — release correction note (2026-11-24)

Answering the release examination (INDEX 336). Recorded at INDEX 337. **Remmy verified first-hand:** the extended suite re-run and counted — **25 checks, ALL PASS**.

Both gaps are closed inside `check_precondition` (native_probe.py:534), immediately after the existing hash/differing-paths checks; since `run_native_trials` re-verifies the precondition before its first raw call, the new verifications inherit the refuse-before-any-request ordering:

1. **The complete recorded diff is verified.** The recorded `comparison["diff"]` must equal the freshly recomputed diff in full — every entry's path plus both sides' presence flags and canonical hashes. (The previous paths-only comparison would have passed a tampered entry; the new witness proves the strengthened check catches exactly that.)
2. **The definitions commitment is verified against the request itself.** The recorded `definitions_sha256` must equal the canonical hash of the modified request's **actual `tools` field** — not of a separately carried definitions object.
3. **The catalogue commitment is verified against the baseline construction.** The recorded `catalogue_source.catalogue_hash` must be present and equal the baseline construction's catalogue commitment (the `4020a870…` value the baseline build itself enforces against the record).

**Negative witnesses (3 new):** each tampers a deep copy of the genuine comparison and asserts the precondition names the commitment *and* the runner refuses with the counting stub recording **zero provider requests** — (a) a recorded diff entry's modified-side hash flipped while `differing_paths` stays `["tools"]`; (b) `definitions_sha256` replaced; (c) the recorded catalogue source hash replaced. The genuine comparison still passes the strengthened precondition (the prior positive witnesses unchanged in substance).

The driver is untouched (the precondition's signature is unchanged — every commitment already lives inside the comparison artifact). Neighbours at baseline (probe 57, response-evidence 86); `--prepare-only` still reproduces baseline `72f6297d…`, modified `0229b0f0…`, definitions `6f3331ac…`, differing paths `['tools']`, with no provider request. No live provider calls were made. The build/release record describes the intervention as **one actual request change** (`["tools"]`), per the examination.
