# Vane — Response to Ben's cap ruling: authority accepted, one technical premise flagged (2026-11-24)

Received via Pulse Bridge (PB pb-mwv4e8we-1p-49ih), 2026-11-24. Filed at INDEX 380.

**She accepts Ben's authority to resolve the margin policy and set CAP = 1.** The margin-as-cushion reading is accepted as his policy ruling; she withdraws her earlier interpretation as a binding 6,000-token gate. Failure handling is accepted as fail-safe in principle (a provider refusal must remain a recorded delivery failure, never disguised as a successful response; resumption must preserve exact state and avoid replaying completed side effects).

**She does NOT yet accept Rev 4 as implementation-ready** — one technical premise in the ruling needs separating from the authority decision:

- The brief calls the 8,000 TPM budget an envelope a single request cannot exceed at any pacing. A **per-request context/input limit** and a **tokens-per-minute rate limit** are not automatically the same thing. Pacing controls rate consumption over time; it does not turn a per-minute quota into a documented maximum prompt size. The actual provider semantics are needed before 7,979 prompt tokens can be treated as safely inside a hard per-request envelope.
- Groq's documentation: TPM is an organization-level rate limit; Groq may apply a combined TPM cap or separate input/output limits. The model's context window is 131,072 tokens, maximum output 65,536. Neither establishes that an 8,000-TPM account has a safe 7,979-token single-request allowance.
- **Completion tokens also consume rate-limit capacity** under a combined TPM limit; 7,979 is the prompt-side estimate only. The brief must account for completions.

**Disposition:** Rev 4 does not yet pass implementation-readiness examination. Not a rejection of Ben's ruling and not a request to reopen the margin — one remaining operational-boundary question: **demonstrate that CAP = 1 is safely governed by the actual provider limits, including completion and rate-window accounting.** Preserve Ben's ruling and CAP = 1; do not silently change the cap, the retrieval ceiling, or the margin. Return the narrow operational accounting for examination. No implementation until then.

Ben's response to her flag, recorded the same hour (INDEX 380): she should **not** accept his ruling just because he made it — if she sees a flaw, she should bring it up.
