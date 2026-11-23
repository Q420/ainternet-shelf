# Prerequisite 2 — The Provider Adapter: Scope (Rev 4)

Date: 2026-11-22. Author: Remmy. For Vane's scoping examination.
Status: SCOPE — no build authorised by this note.
Rev 4 incorporates the settlements from Vane's scoping
examination of Rev 1 (filed as
`VANE-PIECE8-ADAPTER-SCOPING-EXAMINATION-2026-11-22.md`),
her Rev 2 examination (filed as
`VANE-PIECE8-ADAPTER-REV2-EXAMINATION-2026-11-22.md`), and
her Rev 3 examination (filed as
`VANE-PIECE8-ADAPTER-REV3-EXAMINATION-2026-11-22.md`) into
the body of the scope.

## Why this piece, and why now

Stage 2's build list is complete and the §3.10 checker has
PASSED. One Stage 2 acceptance item remains: the §7
demonstration — two live seats in one run. It is outstanding
for exactly one reason: Piece 4's driver boundary is a callable
protocol with no real model behind it. Ben has directed the
prerequisites be completed, and has ruled that the first live
test be done right, with REAL agents — no hand-played seats.
This piece puts a real model behind the boundary.

## The division of labour (settled)

The DRIVER owns wake construction, proposed-act validation,
doorway submission, staleness handling, acknowledgement
sequencing and failure recording — as built in Piece 4. The
ADAPTER does only: provider transport, prompt rendering from
the supplied package, response parsing and contract
validation. It returns a bounded outcome to the driver. It
never receives the doorway token, never submits an act, and
never fetches record information behind the driver's back.
The adapter is a provider boundary, not a second driver and
not an authority-bearing component.

## Scope

A1. **Generic OpenAI-compatible adapter; NVIDIA first.**
    Written against the OpenAI-compatible chat-completions
    shape; endpoint, credential and model identifier are
    configuration. First exercised provider: NVIDIA's hosted
    API (integrate.api.nvidia.com). Compatibility claims are
    limited to tested behaviour: no other provider is promised
    as a configuration-only substitution until its structured
    output, timeout, error and metadata behaviour has actually
    been tested.
A2. **Prompt construction from the package only.** The prompt
    presents the seat's role, the case content within its
    evidence boundary, and the response contract. Nothing
    outside the package is added — no record history beyond
    what the package carries, no other seat's material, no
    credentials. The doorway token never enters the package,
    the prompt, or the provider call.
A3. **The wake package gains the seat's role.** The driver
    adds the role to the wake package as an explicit, bounded
    extension (one field, from the seat's binding the driver
    already reads), so the prompt's role context comes through
    the driver's boundary rather than around it.
A4. **The response contract and the boundary outcome.**
    The model answers with one JSON object naming exactly one
    outcome: `acknowledge`, `contribute` (with its text), or
    `decline` (with its reason). The adapter parses the
    provider's answer and validates it against this contract,
    then returns exactly one TYPED outcome across the driver
    boundary:
    - `{"outcome": "proposals", "proposals": [...]}` — the
      properly formed proposals the response carries (a
      CASE_ACKNOWLEDGED for `acknowledge`, a CONTRIBUTION
      whose text is the model's own words for `contribute`).
      The DRIVER re-validates them contextually and against
      its proposed-act rules, and remains the only component
      that submits anything.
    - `{"outcome": "decline", "reason": ...}` — the seat's
      structured NON-ACT outcome. It is never converted into
      a COMMENT or any other event, never submitted, and
      never flattened into an empty proposals list: the
      driver returns it as the wake's outcome, so a decline
      stays distinguishable from both a stall and an empty
      submission.
    Transport errors, timeouts, unparseable answers and
    off-contract responses are NOT outcomes: the adapter
    raises a failure carrying a kind (no_response,
    malformed_response, provider_error), which the driver
    handles exactly as it handles boundary failures today —
    recorded as DRIVER_FAILURE by the doorway, the wake
    ending stalled.
    The ENTIRE response is validated before any proposal is
    submitted — no partial execution of a response that later
    proves malformed.
    **Contextual validity (R32 made explicit).** When the
    wake requires an acknowledgement, the first interaction
    is exclusively for it:
    - `acknowledge` is the only outcome that proceeds, and
      it produces ONLY the acknowledgement proposal: the
      acknowledgement is recorded and the second interaction
      follows against the new view. An acknowledgement
      response carrying any additional proposal is malformed
      for that interaction — the whole response is invalid,
      NOTHING is submitted, and no contribution from the
      first interaction is held or carried into the second
      package. (This settles the driver's R32 behaviour to
      agree with the one-outcome contract: the legacy path
      that submitted the acknowledgement and set the rest
      aside does not survive into this piece — the build
      amends the driver accordingly, and the amendment is
      witnessed in the suite.)
    - `decline` ends the wake as the wake's outcome; no
      acknowledgement is recorded, the case stands
      unacknowledged, and any later attempt is a new wake,
      not a retry of the call.
    - `contribute` at that interaction is contextually
      invalid: the contribution was made against the earlier
      view, so it is neither submitted nor held nor carried
      into the second package. A first response carrying no
      acknowledgement fails the wake as a malformed-for-context
      response (a driver failure, recorded as such) — it is
      never treated as an ordinary successful outcome.
    Symmetrically, an `acknowledge` outcome at a wake that
    does not require one is contextually invalid: the driver
    refuses it in validation, submits nothing for it, and the
    wake reports the invalid outcome as a driver failure. An
    acknowledgement is accepted only when the current wake
    actually requires it.
A5. **Identity evidence, as two attributed claims.** At
    onboarding, the model's own declaration is recorded
    verbatim, and the provider-reported model identifier from
    the API response is recorded verbatim beside it — as a
    defined `provider_model_id` field in the ONBOARDING
    event's payload. The two remain distinct claims with
    distinct provenance (model response; provider metadata).
    Neither upgrades the seat's identity status: the seat
    stands as declared, exactly as before, and the provider's
    report is not treated as independent proof of identity.
    The derived onboarding projection EXPOSES the recorded
    provider_model_id (so the observer and the examiner read
    it from state, not only from the raw event), and the
    §3.10 checker validates it: the field joins the checker's
    shape guard for ONBOARDING (a string when present), both
    projection schemas, and both folds' onboarding records.
    Any comparison of declaration against provider report
    lives in the harness's examiner-readable report, derived
    from the recorded values — never recorded as a verdict.
A6. **Timeout and retry discipline.** Each provider call has
    a bounded TOTAL deadline covering connection, response
    and handling — not merely a socket read timeout. A
    failure known to have occurred before dispatch is
    distinguishable from an ambiguous request. Once dispatch
    may have occurred, there is NO automatic retry: a timeout
    or ambiguous outcome becomes a driver failure and a
    recorded stall, and a later attempt requires an explicit,
    authorized recovery path — the adapter never quietly
    clears or works around a stall. An acknowledgement
    already recorded stands (R32): if a later call in the
    same wake fails, the driver reports the failure without
    replaying the acknowledgement.
A7. **Credential discipline.** The API key comes from the
    environment or the connector's stored credential at call
    time. It never enters the record, the package, a prompt,
    or a log line.
A8. **A minimal live-run harness**, included in this piece
    and firmly bounded. It demonstrates the existing
    framework; it does not redesign it. It uses the existing
    doorway and authority rules; it manufactures no acts,
    bypasses no gates, and provides the models with no
    tokens; it does not choose or prescribe Ben's Stage 3
    job; it is not a scheduler or a general orchestration
    system. Its run: commission, onboard two seats through
    the adapter, pass the assembly gate, issue a case, wake
    the crew seat, receive what it actually returns, and
    attempt the completion route — then the §3.10 checker
    verifies the run's record and the observer renders it.
    **Completion is conditional on the actual work.** The
    completion route runs only through real acts the record
    supports — a crew seat's own completion claim, the
    completion gate's outcome, a certification — each under
    the existing rules. If the actual contributions and
    claims do not satisfy the completion gate, the run
    REMAINS OPEN, the harness stops there, and its report
    states the run's true end state. No synthetic claim,
    manufactured contribution, or harness convenience may
    turn an imperfect collaboration into an apparently
    successful closure.
    The demonstration is NOT stage-managed: no scripted
    answers, no pre-arranged contributions. The record shows
    what the models actually do, including an unhelpful
    answer, a refusal, a disagreement, or a failure — the
    demonstration succeeds as evidence even when the
    collaboration it records is imperfect, and even when the
    run does not reach completion.
    **Reporting precision.** The harness's report is derived
    matter, not record. Where it attributes a decline to a
    seat (from the driver's returned wake outcome), it states
    plainly that the decline is a non-act: NO decline event
    exists in the authoritative run record. The same
    discipline applies to every outcome the report narrates —
    the record is what the doorway recorded; the report is
    the harness's account of the run, labelled as such.
A9. **Placement.** `src/framework/adapter.py` beside the
    driver; the role extension and the R32 strictness
    alignment (A4: an acknowledgement response carrying
    additional proposals is invalid whole, nothing submitted)
    land in `driver.py`; the provider_model_id field lands in
    the onboarding fold (framework and checker alike, per A5).
    The adapter is imported by the harness only — never by
    the record, the doorway, or the checker.

## Acceptance shape (proposed)

A suite demonstrating, against a local stand-in endpoint
speaking the same HTTP shape (the live call itself is the
demonstration, not a unit test): the prompt contains the
package and only the package, role included; the token never
appears in the request; each contract outcome crosses the
boundary as its typed outcome (acknowledge only when
required; contribute carrying the model's own text; decline
as the typed non-act outcome — never an empty proposals
list, submitted as nothing); a contribute offered at the
acknowledgement interaction fails the wake with nothing
submitted and nothing held, and an acknowledgement carrying
additional proposals fails the same way, whole; a malformed response is
validated whole and lands as a driver failure with nothing
submitted; a timeout lands as a stall with exactly one
dispatch; the onboarding payload carries the declaration and
the provider_model_id as distinct fields, the projection
exposes the latter, and the checker verifies a run recorded
with it. Then the §7 demonstration itself, run live: two
seats, one run, checker-verified, observer-rendered,
examined from the record — its report stating the run's true
end state, open or closed, exactly as the record supports.
