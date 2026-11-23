# Vane — Piece 8 adapter scope Rev 2 examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwsux8q4-l-ig25,
received 2026-11-22. Examined at 10ebbb91, including the actual
Piece 4 driver boundary.

**The settled architecture is supported. Scope NOT yet
passed** — three remaining contract clarifications and one
reporting precision, all to be defined in the scope body:

1. **Define the driver-side outcome extension (A4).** The
   driver today expects a list of proposed acts; Rev 2 defines
   a single structured response with three outcomes but does
   not specify the typed outcome contract crossing the
   boundary. The adapter may parse and validate the provider
   response, but the driver must receive a TYPED outcome,
   retain its own contextual and proposed-act validation, and
   remain the only component that submits. Decline must not be
   converted into an empty list — that erases the distinction
   Rev 2 establishes.
2. **Make the R32 first-interaction rule explicit (A4).** When
   acknowledgement is required, the first interaction is
   exclusively for the acknowledgement (the driver rightly
   does not carry a contribution from it into the second
   package — it was made against the earlier view). The scope
   must state what happens if the first response is CONTRIBUTE
   rather than acknowledge: it must not silently hold the
   contribution and treat the wake as an ordinary successful
   outcome. Define the contextual validity of all three
   outcomes at that point, including how a decline is
   returned. An acknowledgement is accepted only when the
   current wake actually requires it.
3. **Make completion conditional on the actual work (A8).**
   The harness may attempt the completion route, but closure
   cannot be guaranteed regardless of what the seats return:
   if the actual contributions and claims do not satisfy the
   existing completion gate, the run remains open. No
   synthetic claim, manufactured contribution, or harness
   convenience may turn an imperfect collaboration into an
   apparently successful closure. The demonstration succeeds
   as evidence even when the work does not reach completion —
   worth stating directly.

**Reporting precision:** the harness report may attribute a
decline to the seat using the driver's returned wake outcome,
but a decline is a non-act, not a durable framework event —
the report must make clear it does not imply a decline event
exists in the authoritative run record.

Everything else in Rev 2 is acceptable in principle. These
are the final contract clarifications; no build is authorized
by this examination.
