# Vane — Gemini Successor Proposal: Preliminary Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~10:21 MST (PB-ID pb-mwqodpqv-32-6y6m), in response to the eligibility design proposal sent the same morning under Ben's "Proceed with vane."

**Disposition: preliminary examination FAVOURABLE to the proposal**, subject to a precise identity and attestation check before the candidate is admitted to the slate. Architectural point (hers): this is not a repair to the retired Gemini candidate — it is a new candidate with a new identity, a new onboarding record, and its own eligibility evidence; the retired record remains immutable with its failed demonstration.

**Conditions:**
1. **New candidate identity** — pin the exact successor model ID, not the family name or catalogue label; record the catalogue's 3.0 version field alongside the complete raw catalogue response, retrieval time, and source.
2. **Serving attestation** — preserve the provider's documentation and exact attestation format; on every call capture the raw attestation and verify it identifies the pinned candidate and version; missing, malformed, unverifiable, or inconsistent attestation = that call is not eligible evidence; no silent fallback to the catalogue field.
3. **Self-identification** — capture the candidate's statement verbatim at onboarding, labelled explicitly as a self-report, not an authenticated identity claim; cross-check against catalogue + attestation; preserve any discrepancy rather than interpreting it away.
4. **Fresh delivery demonstration** — before any trial, the exact two-part delivery against the new candidate with the pinned Annex A + profile; preserve both parts, hashes, response, actual settings, serving attestation. Success establishes delivery eligibility only, not conformance or adequacy.
5. **Change control** — attestation re-checked on every call; a version mismatch or unverifiable attestation stops the candidate's round; no automatic substitution or retry.

**The one detail she required before unconditional design acceptance:** the exact successor model ID named in the retirement response — the catalogue version 3.0 alone is not a sufficiently discriminating identity.

The alternatives Ben named remain legitimate; the proposal does not establish that Groq or NVIDIA should be contacted, nor weaken the version requirement for those routes. D2 remains entirely separate; the proposal neither changes the corpus nor authorizes trials.

**Answer supplied by Remmy from the hunt evidence (verified first-hand in version_hunt_findings.json):** the retirement error body reads verbatim: "This model models/gemini-2.5-flash is no longer available to new users. Please update your code to use models/gemini-3.8-flash for the latest features and improvements." The exact successor model ID is **gemini-3.8-flash** (resource name `models/gemini-3.8-flash`); its catalogue entry carries `"version": "3.0"`, displayName "Gemini 3.8 Flash", supportedGenerationMethods generateContent + countTokens. Her caution is confirmed by the same catalogue: "3.0" is also the version field of several unrelated image models, so the version alone does not discriminate.
