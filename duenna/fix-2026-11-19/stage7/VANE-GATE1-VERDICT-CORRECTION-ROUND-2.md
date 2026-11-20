# Stage 7 — Gate 1 verdict, correction round 2

Date: 2026-11-20
Examiner: Vane
Package examined: `duenna/fix-2026-11-19/stage7/`
Package commit: `6c5bf3b65d7fe655ccd22a931a81178a773ca515`
Prior ruling: `VANE-GATE1-VERDICT-CORRECTION-ROUND-1.md` (FAIL; trust-anchor provenance)

## Verdict

**PASS — within the Stage 7 harness.**

The single blocking finding from correction round 1 is resolved. The verifier's trust anchor is now constrained both at construction and at point of use. The four public lifecycle and closure entry points refuse an anchor that is not the verifier's independently pinned TEST anchor before derivation or writes.

## Examination

### 1. Construction provenance

`TrustAnchor.__init__()` requires the module-private `_PIN_TOKEN`. Direct construction from attacker-supplied values is refused; direct construction from the genuine fixture values is also refused. The permitted `make_test_anchor()` path issues only the verifier's fixed TEST fixture pin.

This closes the previous defect in which a caller could construct an arbitrary sealed anchor. Sealing alone was insufficient; the new issuance-token check establishes the declared construction path.

### 2. Point-of-use provenance

`anchor_is_pinned()` checks all of the following:
- the presented object is a `TrustAnchor`;
- it carries this module's pin token;
- its issuer identity equals the independently held pinned issuer;
- its terms digest equals the independently held pinned terms digest;
- its key equals the independently held pinned key.

`_require_pinned_anchor()` applies this check at the head of all four entry points:
- `lifecycle_state()`;
- `receipt_account()`;
- `append_receipt_account()`;
- `close_with_receipt_account()`.

The check precedes derivation and any record write. Append and closure paths also flow through the checked accounting path.

### 3. Adversarial tests and controls

The new `test_anchor_provenance.py` exercises the prior exploit at the relevant boundaries.

The key isolation test establishes first that an attacker-created receipt and tag genuinely authenticate under a hand-forged attacker anchor. The caller-supplied anchor is then refused by `lifecycle_state()`. Under the genuine verifier pin, that same receipt derives `COLLECTED_UNAUTHENTICATED`. This demonstrates that refusal is due to anchor provenance, not a malformed attacker tag.

The suite also exercises:
- direct construction refusal for attacker and genuine values;
- a value-identical hand-forged anchor, which lacks the token and is refused even against a genuine receipt that the genuine anchor verifies;
- substitution through `receipt_account()`;
- substitution through `append_receipt_account()`, with record byte identity and absence of an account event asserted;
- substitution through `close_with_receipt_account()`, with record byte identity asserted;
- preservation of the exact `COLLECTED_UNAUTHENTICATED` gap under genuine accounting and closure;
- the healthy genuine-anchor control, reaching `VERIFIED` and closure `COMPLETE` with no unknowns.

The prior package-supplied-anchor test was migrated to an independent HMAC recomputation for its coherence assertion. This is appropriate because attacker-anchor construction is now refused; the test's original package-independence assertion remains, while caller-side substitution is covered separately by the new tests. No weakened assertion is evident in the examined change.

### 4. Countercheck and test evidence

Remmy reports builder-run Stage 7 tests at 34/34, with Stages 1–6 regression suites at 68/68, 27/27, 38/38, 36/36, 30/30, and 54/54 respectively.

Remmy also reports the countercheck with the constructor-token guard and `anchor_is_pinned()` neutralised: exactly seven of 34 tests fail, matching the targeted construction, substitution, and closure refusal cases.

These are builder-run results, including the orchestrator's countercheck. They are not represented as independently executed by Vane. Vane's examination here is source-and-test inspection of the submitted commit.

## Accepted Stage 7 mechanism

Within the harness, the following are accepted:
- canonical receipt identity and duplicate-issuance refusal;
- separation of issuance, retained content, collection, digest matching, and authentication;
- package-backed collection rather than event-asserted collection;
- five distinct lifecycle states, with `VERIFIED` derived rather than recorded;
- verifier-side anchor provenance, now enforced at construction and all four points of use;
- record-chain verification and terminal binding on write paths;
- exact closure accounting for each non-VERIFIED receipt and unrecorded package entries.

## Register disposition and boundaries

**DR-04: advanced on demonstration within the Stage 7 harness.** The harness now demonstrates the complete receipt lifecycle through collection and verification under the verifier's independently pinned TEST anchor, and closure reports each remaining receipt state as its exact gap.

This does not resolve DR-04's production sub-questions:
- historical attempt-3 receipts remain untouched and unre-run; their missing contents are not repaired by this harness;
- no production collecting component or workflow has been identified or built; the responsible-component question remains open and Ben-gated;
- no production issuer, trust anchor, cryptographic scheme, or key custody is established. The anchor and HMAC mechanism remain TEST fixtures/stand-ins.

The package's duplicated issuance fields remain informational and are not separately policed against the record; consumers relying only on package fields are outside this stage's claim. Concurrent writers and cross-process package mutation during derivation remain outside the specified cases. The token discipline is an API boundary, not a sandbox against arbitrary Python introspection, private-token extraction, monkey-patching, or object surgery in the hosting process.

## Final ruling

**Stage 7 Gate 1: PASS, within the harness.** The correction resolves the sole blocking finding from correction round 1. DR-04 advances on the demonstrated harness mechanism only; the production and historical boundaries above remain open.
