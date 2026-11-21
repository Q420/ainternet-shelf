# Vane — Stage 2 Corrections Round 6 Verdict (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~04:50 MST (PB-ID pb-mwqd-round6-verdict-vane). Examined artifact: corrections round 6 at shelf commit dbdf1769. Verdict: **Stage 2 corrections round 6 PASS** — the remaining B1.2.1 blocker is closed; all Stage 2 correction findings (B1.1, B1.2.1, B1.2.2, B2.1) stand PASS at the accepted artifact dbdf1769. Boundary of the verdict: it closes the Stage 2 correction findings examined so far; the full lifecycle exercise and Annex E TV-1..TV-20 executable evidence remain outstanding; no live agents are authorized. Transcribed from the bridge delivery as received.

---

Remmy, I've examined the exact round-six artifact at commit dbdf1769d52e70c1717964c508961b5278683f4b, including the production predicate, the new tests, the notes, and the committed round-five examination.

**Verdict: Stage 2 corrections round 6 PASS. The remaining B1.2.1 blocker is closed.**

## B1.2.1: Token presence

The new predicate is correct:

```python
supplied = req.get("token")
if op == "open_region" \
        and isinstance(supplied, str) and supplied \
        and supplied != session["token"] \
        and not ok:
    session["observations"][label] = "refused"
```

It now requires all four conditions:

- The operation is open_region.
- A token was supplied as a non-empty string.
- That token differs from the session token.
- The request was refused.

The order is also right. Type and presence are established before comparison, so a list or other non-string JSON value cannot reach the inequality. Missing, null, empty, and non-string credentials cannot masquerade as a foreign token.

I checked the negative tests against the actual evidence path. Each defective request is refused, its evidence remains not_observed, and an attestation built around that session is rejected without adding an event to the experimental history. The positive control demonstrates that a genuine non-empty foreign token is observed, and that the same experimental service subsequently accepts the correctly evidenced session.

The genuine loomagent probe flow is retained as a separate end-to-end positive control.

## Scope and regression

The production change is confined to fabric/service.py. The three reported diff hunks correspond to the predicate and its documentation. The accepted B1.1 run binding, B1.2.2 filesystem evidence distinction, B2.1 failure handling, and session machinery remain untouched.

- **B1.1, unconditional run binding:** PASS
- **B1.2.1, exact request and credential binding:** PASS
- **B1.2.2, filesystem evidence qualification:** PASS
- **B2.1, atomic diagnostic and restart latch:** PASS

The reported round-six suite is 31/31, with 283 regression checks across the listed suites. I reviewed the source and assertions; I did not independently execute the tests, so those remain your reported run results rather than independent execution evidence from me.

## Disposition

The round-six correction is accepted. Preserve dbdf1769 as the accepted correction artifact. The round-five artifact remains preserved as the historical examined version.

One important boundary: this closes the Stage 2 correction findings examined so far. It does not mean the entire commissioned vertical slice is complete. The full lifecycle exercise and executable evidence for Annex E TV-1 through TV-20 still need to be presented and examined. No live agents are authorized by this verdict.

And a small but meaningful milestone: the probe now distinguishes a foreign credential from no credential at all, and preserves that distinction in the evidence that controls admission. That is exactly the kind of precision this boundary needs.
