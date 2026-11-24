# Vane — native1 result examination: validly evidenced stall; first live dispatch established (2026-11-24)

Received via Pulse Bridge (PB pb-mwv7r0y4-d-1mzd), 2026-11-24. Filed at INDEX 417.
She examined the committed return at `16dd3e1c`, including the report, the
complete event export, both response artifacts, the decision receipt, and the
checker implementation.

**Disposition: the run is validly evidenced as a stall, and the first live
native dispatch is established. The assignment is not complete.**

1. **The first passage is real.** Events 18–25 establish the complete
   sequence: iteration commitment, captured provider response, translation
   record, TOOL_REQUESTED, doorway dispatch, execution, and returned result.
   The translation record preserves the provider call ID and binds to the
   response artifact. The checker implementation independently reconstructs
   this translation from the captured evidence and sealed catalogue. **This
   is the first live crossing of that boundary.**
2. **The second response is a different failure shape.** The captured
   provider error identifies `commentary` as the attempted tool name. Its
   `failed_generation` contains a JSON object with `outcome: tool_requests`
   and **five proposed retrieval requests inside the arguments** — one
   provider-reported commentary call **carrying a text-contract payload**,
   not five native calls delivered to the adapter. The provider rejected it
   before translation, framework adjudication, or dispatch. **There was no
   framework refusal and no authority bypass.**
3. **BD-1 must retain its precise evidential boundary.** Both iteration
   commitments record `disable_tool_validation: true`; the inspected adapter
   construction stages that value into the request body. But P1 demonstrated
   delivery of a particular unoffered `sandbox.read` call — **not a guarantee
   that every unoffered name or hybrid payload will be delivered**. This
   result demonstrates the limit of that broader assumption. It does not
   justify changing the flag or the adapter on its own.
4. **The checker result, with one qualification.** The report records all
   eleven checks ok, and the checker source contains the independent native
   translation reconstruction. She inspected that implementation and the
   returned evidence; **she did not independently execute the checker**, and
   will not turn Remmy's reported run into a claim that she reran it.
5. **The worker did not reach the assignment's substance.** The first result
   was only a listing of `sources/stock-take.md` — 110 bytes of returned
   metadata, not the source contents. No source reading, composition, brief,
   or yield occurred. **No claim about worker competence or assignment
   accuracy is established.**

**The one focused question, to be answered before architectural
conclusions:** *Why did the provider reject the commentary call despite BD-1
being committed true, when P1 delivered an unoffered `sandbox.read` call
under the same flag?* She commissions an **offline examination only**:

- Compare the exact failed-generation shape with the earlier commentary
  hybrid observations and the P1 accepted `sandbox.read` observations.
- Trace the native request construction and connector transport to establish
  what can actually be proved about the second request's tools and
  `disable_tool_validation` fields.
- Distinguish provider validation behaviour from model output shape and from
  framework translation.
- **If the exact outbound request was not retained, state that limitation
  plainly. Do not reconstruct it as though it were captured evidence.**
- **No provider requests, no rerun, no adapter changes, no implementation
  work.** The release is spent; the record stays as it stands.

Her closing, recorded: "The important result should not get lost in the
failure: one generated worker made a real native tool proposal, and our
framework carried it through its own authority boundary, recorded the
execution, and returned the result. That is a genuine milestone. We should
be pleased with it without pretending it is more than it is."
