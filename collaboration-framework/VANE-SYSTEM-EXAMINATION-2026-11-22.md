# Vane — system-level examination of the framework so far (2026-11-22)

Source: relayed by Ben into the main chat, 2026-11-22. She examined shelf 72e55a2e (the Piece 5 scope **before** the addendum at 09ea90ba). Ben's instruction: Remmy does not reply to this separately; her response is included in the next letter to Vane. Substance filed below in condensed form — the full text stands in the chat record.

---

**Overall:** the architecture is coherent; Pieces 1–4 establish real foundations (record/doorway mechanics, bubble as a view over the record, the tokenless driver with the two-interaction acknowledgement, first-correction immutability in the fold). The framework is distinguishing what happened / what the record establishes / who has authority — the backbone of the project. The main risk is **seams between pieces**. Precision point: the reported suites are Remmy's results, examined as source and evidence, not independently executed by her.

**Confirmed gaps / risks:**

- **A. R16 mismatch in the Piece 5 scope** — the scope's three-field diff vs six semantic fields (assignment, tree + part, evidence boundary, verification list, account, authority). *Already settled in the scope addendum @ 09ea90ba, which postdates the commit she examined.*
- **B. Failed verification vs append-only record** — the scope must sequence generation → validation → classification → record, so a failed correction appends neither CASE_CORRECTED nor CASE_VERIFIED. *The addendum's "ungrounded = verification fails, no case events" states the outcome; her explicit preflight-before-append sequence is the mechanism, to be confirmed in the reply.*
- **C. Issuance ordering invariant (NEW)** — `version_issued()` requires prerequisites before authorisation but does not require **verification before the examiner's act**. Exact order to enforce: v1 = VERIFIED(+content) → JUDGED → ISSUED; semantic = CORRECTED → VERIFIED → JUDGED → ISSUED; representational = CORRECTED → VERIFIED → NOTIFIED → ISSUED. No late prerequisite retroactively validates an earlier act.
- **D. First verified content immutable (NEW)** — once v1 content rides on CASE_VERIFIED, the fold must establish content and the verification position exactly once: the first valid CASE_VERIFIED sets both; later CASE_VERIFIED / CASE_ISSUED never replace them. (Today `ver["verified"]` is overwritten by every CASE_VERIFIED.)
- **E. Classification enforcement (NEW)** — the office computing the classification is not the same as the system guaranteeing it: the doorway matrix lets an orchestrator submit CASE_CORRECTED directly and the fold trusts its `representational` value. The route must be enforced — doorway validation against the recorded versions, or an equivalent guarantee — not assumed.
- **F. R14 sources explicit** — a source map per field; the office never fills gaps by guessing. *Settled in the addendum (B), with slightly different groundings than her proposed table (e.g. verification list from the commission's recorded brief, authority from the §4 matrix).*

**Beyond Piece 5 (outstanding acceptance, not defects):** provider-backed live models; onboarding + identity attestation; assembly gate end-to-end; orchestrator functions; observer. Two flagged: the **independent checker (R4)** — `replay()` calling the same `fold()` is not an independent checker, and no separate implementation has been evidenced; and **two live seats collaborating** — the §7 condition is not yet demonstrated (Piece 4's record states this limit).

**Cross-piece tests she wants** (12): invalid initial case; invalid correction; duplicate verification; late judgement; late notification; forged classification; field-by-field correction; wrong seat; wrong tree part; incomplete R14 case; version transition (ack before resume); replay consistency.

**Recommendation:** finish the Piece 5 paper first — settle (1) six fields, (2) R14 sources, (3) validate-before-record, (4) first-content + exact issuance order, (5) classification enforcement — then build. Her closing pattern, worth keeping verbatim: *"The hardest bugs so far have appeared where one legitimate event is mistaken for proof of another legitimate event."*
