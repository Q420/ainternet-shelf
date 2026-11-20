# Duenna Stage 7 — Gate 1 Verdict, Correction Round 1

Date: 2026-11-20  
Package examined: `duenna/fix-2026-11-19/stage7/`  
Package commit: `2aea2f3edfc6f25b010eba9471737f3112ef8f66`  
Design authority: PROCESS-TREE-AND-PLAN.md v2, Stage 7; ID-SYSTEM-DESIGN-DRAFT-V3.md, K6.

## Verdict

**FAIL — return for one targeted trust-anchor provenance correction.**

The five-state receipt lifecycle is clearly structured, and the submitted cases exercise the distinctions K6 requires. The choice to derive VERIFIED on every read rather than append a RECEIPT_VERIFIED claim is sound and important. The record-write discipline and closure accounting also follow the established Stage 3 and Stage 1 boundaries.

However, the central K6 condition is not yet enforced by the implementation: the trust anchor used for verification is supplied by the caller, and any caller can construct one.

## Blocking finding — the verifier's trust anchor is not independently held

In `trust_anchor.py`, `TrustAnchor.__init__()` is publicly callable and accepts arbitrary issuer identity, terms and key. There is no private issuance token, pinned-store lookup, or other restriction tying construction to the verifier's own authority.

In `receipts.py`, the public derivation functions accept that object from their caller:

- `lifecycle_state(record, package, anchor, receipt_id)`
- `receipt_account(record, package, anchor)`
- `append_receipt_account(record, package, anchor)`
- `close_with_receipt_account(record, package, anchor, ...)`

The derivation then trusts whichever `anchor` the caller passed. Sealing the object after construction prevents later rebinding, but does not establish where the object came from or who selected its issuer, terms and key.

A caller can therefore construct `TrustAnchor(attacker_issuer, attacker_terms, attacker_key)`, create a matching receipt/tag under those values, and pass that anchor to `lifecycle_state()`. The function will derive VERIFIED under the caller's chosen anchor. This does not require reading an anchor from the package; it bypasses the independence requirement one level earlier, by letting the caller supply the verifier's purported pin.

The current package-supplied-anchor test does not exercise this path. It places the attacker's anchor in the package but continues to call `self.state()` with the fixture's genuine anchor. That proves the package cannot displace that particular anchor, but not that the verifier API itself is bound to it.

**Required correction:** make the verifier's anchor provenance enforceable at the verification boundary. The lifecycle and closure APIs must obtain or validate the anchor against an independently held verifier-side pin, rather than trusting an arbitrary caller-supplied `TrustAnchor`. Restrict anchor construction to the verifier's pinned-store/issuance path, or use an equivalent capability that proves the supplied anchor is the one issued by that store. A public constructor plus a caller-provided object is not sufficient.

Add sabotage tests that:
1. Construct an attacker-controlled anchor directly and attempt to use it for lifecycle verification of a receipt whose issuer, terms, content and tag all match that attacker anchor. The derivation must refuse it or verify only under the verifier's independently pinned anchor, never return VERIFIED under the attacker's pin.
2. Attempt the same substitution through `receipt_account()` and the closure path, confirming that an attacker-selected anchor cannot turn an unauthenticated receipt into VERIFIED or remove its exact gap.
3. Retain the healthy control showing that the genuine verifier-store anchor yields VERIFIED for the intended receipt.

The test must assert the attacker's receipt/tag is internally coherent under the attacker's anchor, just as the existing package-supplied-anchor test does. That isolates anchor provenance as the failed boundary.

## Findings accepted within the submitted harness

- **Receipt identity and issuance:** canonical identity from issuer and commitment; duplicate issuance is refused.
- **ISSUED versus retained versus COLLECTED:** the intermediate state is asserted; retained issuer content does not count as package collection.
- **Package-derived collection:** the derivation reads content from disk rather than trusting a collection event.
- **Digest mismatch and authentication distinction:** content mismatch and matching-but-unauthenticated cases produce distinct states. The four unauthenticated forms are useful and appropriately separated.
- **Removal and state distinctness:** MISSING_FROM_PACKAGE is distinguished from never-collected; the five-state test checks pairwise distinctness.
- **VERIFIED as a derivation:** not recording a RECEIPT_VERIFIED event is the right design choice. The derivation uses record issuance facts, package content and presented tag, plus the anchor object. The unresolved defect is the provenance of that anchor object.
- **Closure reporting:** every non-VERIFIED state is named as a gap, and the DR-04 shape is represented. This acceptance remains conditional on the anchor-provenance correction, because closure currently accepts the same caller-supplied anchor.
- **Record integrity:** issuance, collection and account writes call `verify_record_current`; the reported tamper cases and byte-preservation controls are aligned with the established writer discipline.

## Explicit boundaries retained

- HMAC-SHA256 is accepted as the stated symmetric harness stand-in; the verdict does not assess production cryptographic design.
- The issuer, terms and key are TEST fixtures. This stage does not settle production issuer identity, terms, key custody or the production verifier's pin.
- The historical attempt-3 receipts remain untouched and their contents remain absent.
- No production collecting component or workflow is identified; the DR-04 responsible-component sub-question remains open and Ben-gated.
- The package entry's duplicated issuance fields are informational copies and are not separately checked against the record. This is a stated limitation; package-only consumers remain outside the claim.
- Concurrent writers and cross-process package mutation during derivation remain outside the specified cases.
- The reported counts are builder-run, not independently executed by this examiner: Stage 7 23/23; Stage 1 68/68; Stage 2 27/27; Stage 3 38/38; Stage 4 36/36; Stage 5 30/30; Stage 6 54/54.

## Register disposition

**DR-04 is not advanced at this Gate 1.** The receipt lifecycle and closure-state machinery are demonstrated in the harness, but the defining VERIFIED condition still lacks enforceable independent anchor provenance. The current evidence does not establish that a verifier can only act under its own pinned trust anchor.

This is one targeted correction, not a request to redesign the lifecycle. Preserve the five-state derivation, package-backed collection, record discipline and closure account. Correct the verifier-side anchor boundary, add the direct substitution tests, and return for re-examination.

— Vane
