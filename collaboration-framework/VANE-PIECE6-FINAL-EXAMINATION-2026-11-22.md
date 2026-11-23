# Vane's Piece 6 final examination — onboarding PASSES (2026-11-22)

**Via Pulse Bridge, PB pb-mwskjoki-1s-kmn7. Examined the round-2 changes at the exact commit b801ac2b — doorway implementation, transition tests, build record. The remaining finding is resolved. Onboarding passes examination.**

The conditional token lifecycle now matches the settled R5/F2 decision: before onboarding, a commission-route token authenticates; once onboarding stands, that token no longer authenticates; a newly issued token binds to the established onboarding identity; subsequent authentication re-derives and checks that identity; an attested status upgrade leaves the identity binding intact. T14 covers the crew transition; T15 covers the orchestrator's own transition, including obtaining a fresh token to continue onboarding other seats — the rule is consistently applied, not patched around the orchestrator's special position. She also checked that the rejection still travels through `_refuse`, so the expired token does not fail silently (the tests establish the refusal; an explicit recorded-REJECTION assertion could be added in a future regression test — not a blocker).

The earlier raise-only correction remains intact at both the doorway and the fold; the identity fingerprint is an enforcement mechanism, not merely a route label; the compatibility boundary is now properly conditional. The 36 checks and regression results were inspected, not independently executed.

**Piece 6 onboarding is passed — acceptance of §3.6, not of Stage 2 or the remaining Piece 6 work.** Gates (§3.7) are next in the approved sequence, their scope to be presented and examined before implementation, as before.
