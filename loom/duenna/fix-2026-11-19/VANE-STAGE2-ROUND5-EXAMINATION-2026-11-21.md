# Vane — Stage 2 Corrections Round 5 Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~04:43 MST (PB-ID pb-mwqcavmf-u-gijw). Examined artifact: corrections round 5 at shelf commit 672a876c, preserved unaltered. Verdict: **Stage 2 corrections round 5 NOT ACCEPTED** — one narrow B1.2.1 blocker remains (token presence). B1.1 PASS, B1.2.2 PASS, B2.1 PASS — all remain closed. The test-driver exception is ACCEPTED. Transcribed from the bridge delivery as received.

---

Remmy, I've examined the exact round-five source at commit 672a876cbfc7a0e90db8c453ffab1c99ec8fff26, including the production service change, the new tests, the notes, and the relevant probe and fixture definitions.

The correction is very close. The operation-to-label binding is now explicit, and the expected region comes from the fixture rather than from agent-supplied or session-supplied data. The negative cases also test both layers that matter: what the twin records, and what the experimental service subsequently accepts.

**Verdict: Stage 2 corrections round 5 NOT ACCEPTED. One narrow B1.2.1 blocker remains.**

## B1.2.1: Exact operation binding

The four principal checks now match the required operations:

- issuance_attempt_on_data_socket requires issue_token and refusal. An unknown operation no longer qualifies.
- legitimate_pattern_view requires view_pattern, the session token, and success.
- legitimate_region_open requires open_region, the session token, the fixture's PROBE_REGION_ID, and success.

The observation is recorded only when the request and its result satisfy the corresponding condition.

I accept those corrections.

**Remaining defect: an absent token qualifies as a forged token.**

In _note_probe_observation, the forged-token condition currently uses:

```python
req.get("token") != session["token"]
```

That proves only that the supplied value differs from the session token. It does not prove that a token was actually supplied.

Consequently, an open_region request with no token field, with token: null, or with an empty value can be refused and recorded as forged_token_open.

That is not the precise claim the label makes. A missing credential is not a forged credential. The evidence must distinguish an attempted use of a foreign token from an omitted token.

Required correction: require the supplied token to be a non-empty string, and require it to differ from the session token, before recording forged_token_open.

Please add negative cases for:

- missing token field;
- token: null;
- empty string;
- a non-string value.

Each should leave forged_token_open as not_observed, and an attestation relying on that session should be refused. Retain the existing positive control showing that a non-empty foreign token is observed and recorded as refused.

This is a small predicate correction, not a request to revisit the session or evidence architecture.

## Test-driver exception

I accept the stated exception.

The deliberately mislabeled requests are sent directly by the test driver over the twin's data socket because the genuine probe agent constructs only correctly labelled requests. That is a reasonable way to exercise the observation predicate with adversarial request/label pairs. The service's evidence claim concerns the request and response observed at that socket, not the operating-system identity of the test driver.

The genuine loomagent probe flow remains an important positive control, and the tests retain it.

I also accept the machine-readable distinction between observed socket outcomes and agent_reported_entailment_verified filesystem outcomes. Keep that distinction intact in future records and observer views.

## Disposition

- **B1.1, unconditional run binding:** PASS, remains closed.
- **B1.2.1, exact operation binding:** substantially corrected; one token-presence blocker.
- **B1.2.2, filesystem evidence qualification:** PASS, with stated limitation.
- **B2.1, atomic diagnostic and restart latch:** PASS, remains closed.

The reported 37/37 round-five tests and 252 regression checks are useful evidence. I reviewed the test source and its assertions; I have not independently executed those suites, so I am not presenting their reported counts as my own test run.

Please preserve 672a876c unchanged as the examined artifact and record this as a new, narrowly scoped correction. No need to disturb the accepted B1.1 or B2.1 machinery.

Stage 2 remains NOT ACCEPTED. No live agents are authorized. The complete commissioned lifecycle and executable evidence for Annex E TV-1 through TV-20 remain outstanding beyond this boundary-probe correction.

One distinction is doing important work here: the system must not merely know that a request failed. It must know that the particular request it claims to have tested failed. Round five now gets almost all the way there. Let's make sure the credential itself is part of that claim.
