# Vane — Piece 8 adapter scoping examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwsut2m0-k-3j1l,
received 2026-11-22. Examined at f1e73e90 against the existing
driver, onboarding, doorway and record boundaries.

**Overall: the shape is right; the adapter should be the next
piece. Scope NOT yet passed** — the five questions deserve
explicit decisions, plus two further boundaries. Settlements:

- **Q1 (provider order):** keep the generic OpenAI-compatible
  adapter, NVIDIA first. Endpoint/credential/model id are
  configuration. Other providers are supported only after
  their compatibility is actually tested — "OpenAI-compatible"
  does not guarantee identical structured-output, timeout,
  error or metadata behaviour; do not promise config-only
  substitution yet.
- **Q2 (identity evidence):** the model's declaration and the
  provider-reported model id are preserved as DISTINCT,
  attributed claims (model response vs provider metadata),
  verbatim. The comparison belongs in an examiner-readable
  report DERIVED from the recorded values — never recorded as
  a verdict or an established identity fact; the provider's
  report is not independent proof and must NOT upgrade the
  seat's identity status. Implementation made explicit: add a
  defined `provider_model_id` field to the ONBOARDING event's
  evidence contract, with checker validation, and decide
  whether the derived onboarding projection exposes it — it
  must not disappear silently or ride as an unexamined extra
  field. (The fold currently does not retain it in the
  projection; the raw event preserves its payload.)
- **Q3 (response contract):** structured JSON yes; malformed
  → driver failure yes. Precision required: acknowledge = a
  properly formed CASE_ACKNOWLEDGED proposal, when
  acknowledgement is actually required; contribute = a
  CONTRIBUTION proposal with the model's own text; decline =
  a structured NON-ACT outcome with a reason — not silently
  converted into a COMMENT or another event, and an empty
  proposal list is not an adequate substitute (it erases the
  distinction between declining and having nothing to submit).
  Decide the recording mechanism deliberately. Validate the
  ENTIRE response before submitting any proposal — no partial
  execution.
- **Q4 (retries):** no automatic retry after an ambiguous
  dispatch; a pre-dispatch failure may be distinguished from
  an ambiguous request; once dispatch may have occurred, no
  retry — timeout/ambiguity becomes a driver failure and a
  recorded stall, recoverable only through an explicit
  authorized path; the adapter must not quietly clear the
  stall. The timeout is a TOTAL call deadline (connection +
  response handling), not merely a socket read timeout. R32:
  an acknowledgement already recorded stands; a later call's
  failure is reported without replaying the acknowledgement.
- **Q5 (harness):** include the minimal §7 harness in this
  piece, firmly bounded: it demonstrates the existing
  framework and does not redesign it; uses the existing
  doorway and authority rules; manufactures no acts, bypasses
  no gates, gives models no tokens; does not choose or
  prescribe Ben's Stage 3 job; does not become a scheduler or
  general orchestration system. The demonstration is evidence
  two real seats can participate in one recorded run — not
  evidence every kind of collaborative job works.

**Two additional boundaries:**
1. **Role in the wake package.** The driver's package carries
   seat, case, view, reasons, position — not the seat's role,
   though A2's prompt presents the role. The adapter must not
   fetch record information behind the driver's back: either
   the driver adds the role to the package as an explicit,
   bounded extension (her favour), or the prompt does not
   claim to provide it.
2. **The adapter must not become a second driver.** The
   driver owns wake construction, validation, submission,
   staleness, acknowledgement sequencing and failure
   recording. The adapter does only provider transport, prompt
   rendering from the supplied package, response parsing and
   contract validation, returning a bounded outcome. It never
   receives the doorway token and never submits an act.

**Further conditions:** the checker must recognize and
validate any newly recorded provider-identity evidence. The
first live run must not be stage-managed — no scripted
answers or pre-arranged contributions; the record shows what
the models actually do, including an unhelpful answer, a
refusal, a disagreement, or a failure.
