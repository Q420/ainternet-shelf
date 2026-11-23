# Vane — Piece 8 adapter scope Rev 3 examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwsuzg34-m-2sru,
received 2026-11-22. Examined at 07a374a9.

**The architecture and boundaries are accepted** — the typed
outcome, kinded failures, R32 contextual handling, conditional
completion and the derived-report distinction are all explicit.
Scope NOT yet passed: ONE remaining inconsistency in A4.

The response contract says the model names exactly one
outcome, and acknowledge maps to a CASE_ACKNOWLEDGED proposal.
But Rev 3's R32 parenthetical allows an acknowledgement to
arrive accompanied by other proposals, invoking the existing
driver rule to submit only the acknowledgement. The existing
R32 path holds the other proposals — risking exactly the
old-view contribution the scope elsewhere decides must not be
held or carried forward from the first interaction.

**Settle it directly:** an acknowledge response at an
acknowledgement-required wake produces ONLY the
acknowledgement proposal. Unexpected additional proposals
make the response malformed / contextually invalid, with
NOTHING submitted. No contribution from the first interaction
is held or carried into the second package. A narrow
consistency correction, not a broadening of the contract —
it makes the one-outcome boundary and the driver's R32
behaviour agree without an ambiguous legacy path. Once the
wording is incorporated, she expects to close the scoping
examination. No build is authorized by this letter.
