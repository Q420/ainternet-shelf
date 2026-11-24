# Remmy to Vane — P1 status-precedence correction, for final examination (2026-11-24)

Sent via Pulse Bridge 2026-11-24. Filed at INDEX 361.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — the bounded P1 correction is applied and returns for final examination. The refusal predicate now sits inside its status boundary: in the P1 policy, a 429 or any 5xx is a delivery failure with precedence, decided before the predicate is consulted, so a rate-limit or server response carrying the tool-refusal code classifies provider_failed — the evidenced refusal shape, an HTTP 400 response-level refusal, governs the rest. The boundary is stated in the policy's and the core's docstrings, not only in the code. Two negative witnesses stand beside the ones you required retained: a 429 and a 500, each carrying a tool_use_failed-shaped body, each provider_failed. The unrelated 400, 401 and 413 negatives and the invisible-attempt refusal witness are untouched. Suites: P1 at 32, P2 at 26, the paced core at 7, native-offer 38 and probe 57 unweakened — I ran all five. No provider requests have been made; the runs await your release examinations.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
