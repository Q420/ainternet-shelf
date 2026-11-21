# Vane — Ruling on the Provider-Version Question (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~09:06 MST (PB-ID pb-mwqlocj1-2o-dlcj), in response to the question put in the correction-round submission letter. She also confirmed: the correction-round dispatch and the filing at shelf head 550c45af are noted; 03bf284d's preservation and the separately identifiable correction round are noted; the proposed corrections are appropriately scoped, but dispatch is not acceptance; the examiner-authored D2 corpus remains outstanding and she will provide it; no trials authorized pending examination and acceptance of the complete corrected package; all original and failed evidence preserved unchanged.

**Ruling: the pinned catalogue snapshot does NOT satisfy the provider-version requirement of Rev 4 §§8–9.**

- It IS accepted as a catalogue identity and configuration anchor: it binds the advertised model ID, owner, and full catalogue entry to the constitution through its hash and shelf anchor.
- It does NOT establish the actual serving-model version, nor can it detect a silent backend version change if the catalogue entry remains unchanged.

**Directions:**
1. Record the provider-version field as **unavailable**.
2. Retain the catalogue snapshot as a separate, useful identity anchor.
3. Do not claim that the complete provider-version pin has been satisfied.
4. Seek a provider-supported version identifier or independently verifiable serving-version attestation.
5. If neither is available, **return the limitation for an explicit design decision**. Do not silently waive or reinterpret the settled requirement.
6. This is an **unresolved eligibility condition, not an automatic exclusion** of Groq or NVIDIA. The evidence must preserve that distinction.

**Action taken:** the ruling was passed to the running correction round as an addition — an annex addendum recording provider_version = unavailable for both routes (original annex untouched), plus a genuine search of both routes' actual API responses, catalogue payloads, and documented versioning surfaces for any version identifier/attestation, with verbatim evidence; if none exists, the limitation is recorded as returned for an explicit design decision (Ben's / a design revision settled with Vane — not resolved in the build).
