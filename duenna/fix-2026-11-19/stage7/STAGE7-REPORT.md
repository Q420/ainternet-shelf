# Duenna Stage 7 — Receipt Lifecycle Report

Date: 2026-11-20
Design authority: PROCESS-TREE-AND-PLAN.md v2, Stage 7; ID-SYSTEM-DESIGN-DRAFT-V3.md (K6)
Build location: ~/workspace/duenna-fix/stage7/ (Python standard library only)
Approval: Ben, 2026-11-20 (Stages 2–9 approved; Stage 7 built from the plan, after Stage 6 cleared Gate 1)

## Status of this report

The Stage 7 harness is built and its full test suite passes
(23/23, below), with the Stage 1 (68/68), Stage 2 (27/27),
Stage 3 (38/38), Stage 4 (36/36), Stage 5 (30/30) and
Stage 6 (54/54) suites green as regression. This report is
EVIDENCE for the examiner, not a verdict: a builder's green
run establishes that the mechanism behaves as specified on
the exercised cases; whether Stage 7 passes is the
examiner's determination (Gate 1 discipline), not this
report's. Nothing here declares Stage 7 complete.

## What was built

- `trust_anchor.py` — the independently pinned trust
  anchor (K6's VERIFIED condition). A sealed `TrustAnchor`
  holds the issuer identity the verifier recognises, the
  commitment-terms digest it recognises, and the
  verification key for that issuer's authentication tags.
  It is obtained from the verifier's own pinned store —
  nothing in this stage reads an anchor out of a package.
  Authentication is an HMAC-SHA256 tag over (receipt
  identity, issuer, terms digest, content digest).
- `package.py` — the result package as a directory on
  disk: one entry file per receipt (the issuance facts as
  carried by the package, plus the issuer's authentication
  tag) and one content file per collected receipt. Every
  read goes back to disk; the package's state is what its
  files say.
- `receipts.py` — the lifecycle itself. `ReceiptIssuer`
  (the issuing capability: possession of the key is the
  issuance authority; sealed after construction),
  `IssuerStore` (the issuer's retained content), issuance
  and collection as record events under the established
  verify-then-extend discipline, the lifecycle derivation,
  and closure reporting through Stage 1's ClosureWriter.

## The five facts, and where each lives

- ISSUED — a `RECEIPT_ISSUED` event on the run record,
  carrying the receipt identity, the commitment, the
  issuer, the terms digest and the content digest. The
  identity is a canonical function of (issuer, commitment)
  — computed, not issued (Stage 5's discipline) — and
  re-issuance of the same commitment is refused: one
  commitment, exactly one receipt.
- CONTENT (retained) — the committed bytes, retained by
  the issuer in its own store from issuance. Retention is
  the issuer's fact; it is not collection.
- DIGEST (at issuance) — SHA-256 of the content, computed
  at issuance and carried identically by the record event
  and the package entry.
- COLLECTED — the content has entered the result package.
  Established by reading the package back, never from the
  `RECEIPT_COLLECTED` event's say-so: the event records
  the act, the package's bytes are the fact. An event
  claiming collection over a package lacking the content
  would be DR-04's papered-over failure in a new form; the
  derivation does not permit it.
- VERIFIED — a derivation, recomputed at every read from
  primary facts: the record's issuance, the package's
  content bytes, the package entry's presented tag, and
  the verifier's pinned anchor. No `RECEIPT_VERIFIED`
  event is ever written: a recorded claim of verification
  is precisely what the derivation exists to replace.

## The lifecycle states

Five distinct states, reported verbatim wherever a state
is reported: `VERIFIED`; `ISSUED_CONTENT_NOT_COLLECTED`
(issuance on the record, entry in the package, no content
— DR-04's state); `MISSING_FROM_PACKAGE` (issuance on the
record, no entry in the package at all);
`COLLECTED_DIGEST_MISMATCH` (content present, bytes not
hashing to the issuance digest);
`COLLECTED_UNAUTHENTICATED` (content present and
digest-matching, authentication failing for any reason —
absent tag, forged tag, other terms, another issuer).

Issuance facts for the derivation are taken from the
RECORD (the issuance event); the package contributes the
content bytes and the presented tag; the anchor is the
verifier's pin. The package entry's duplicated issuance
fields are informational copies: the derivation neither
trusts them nor polices them (a stated boundary, below).

## Test 7 — each case, its outcome, its state

- **Full lifecycle (the end-to-end claim)** — issue,
  collect: `VERIFIED`. The intermediate state after
  issuance alone is asserted separately: content retained
  in the issuer's store, absent from the package, state
  `ISSUED_CONTENT_NOT_COLLECTED` — issuance never
  satisfies collection or verification, as its own test.
- **Case 1 — receipt issued without content** →
  `ISSUED_CONTENT_NOT_COLLECTED`. PASS.
- **Case 2 — content mismatching the digest** — issued,
  collected (state `VERIFIED`), then the collected
  content rewritten by an outside hand →
  `COLLECTED_DIGEST_MISMATCH`. PASS.
- **Case 3 — matching content and digest without valid
  issuer/commitment authentication** →
  `COLLECTED_UNAUTHENTICATED` in every form exercised:
  (a) the tag removed from the package entry; (b) the tag
  forged under an attacker key; (c) the package supplying
  its own purported anchor, with a tag genuinely valid
  under THAT anchor — the verifier's pinned anchor is
  never displaced by package-supplied material, and the
  receipt does not authenticate (design v3's sentence,
  mechanised; the test asserts the attack is coherent by
  verifying the forged tag against the attacker's anchor
  first); (d) a genuine issuer key minting under terms
  the anchor does not pin — honestly computed tag,
  matching content and digest, still unauthenticated.
  PASS, each form separately.
- **Case 4 — receipt removed from the package after
  issuance** → `MISSING_FROM_PACKAGE`, in two forms:
  removed after collection (from `VERIFIED`), and removed
  after issuance before collection — the second form
  asserted distinct from case 1's state. PASS.
- **Distinctness** — one run holding five receipts, one
  in each state: the five derived states are pairwise
  distinct, and exactly one receipt is `VERIFIED`. PASS.

## Closure reporting

`close_with_receipt_account` appends a
`RECEIPT_LIFECYCLE_ACCOUNT` event naming every issued
receipt's derived state, then closes through Stage 1's
ClosureWriter with every non-VERIFIED receipt named in
the closure account's unknowns as the exact gap it is.
Exercised: a run holding one receipt in each state closes
INCOMPLETE with exactly four gap lines, each naming its
receipt and its exact state; the VERIFIED receipt is
named in no gap; no gap line contains the word VERIFIED.
A run whose receipts are all VERIFIED closes COMPLETE
with no receipt gaps. DR-04 is reproduced in its own
shape as a dedicated case: the session START and TERMINAL
commitments issued, contents never collected — the
account states both as `ISSUED_CONTENT_NOT_COLLECTED`,
the closure is INCOMPLETE, and neither receipt is omitted
or rounded up. A package entry no issuance on the record
accounts for is reported in the account's
`unrecorded_package_entries` and named as a closure gap;
it is not a receipt in any lifecycle state (the derivation
returns None for it).

## Record discipline

Issuance, collection and the account all run Stage 3's
`verify_record_current` (chain recomputation + terminal
binding) before appending. Exercised through the record's
real persistence path: an event body edited on disk with
its stored digest retained → issuance, collection and the
account each refuse carrying
`record_chain_verification_failed`, the record file
byte-identical afterwards, and the refused operations
create no package or store state. The record file
truncated to empty after issuance → collection refuses on
the terminal mismatch and the emptied file stays exactly
empty.

## Countercheck

With `TrustAnchor.authenticates` neutralised in a scratch
copy (every presented tag accepted), exactly 6 of the 23
tests fail — the four `COLLECTED_UNAUTHENTICATED` cases,
the five-state distinctness test, and the closure-gap test
(whose unauthenticated receipt would round up to
VERIFIED) — and the other 17 pass. The assertions bite on
precisely the authentication mechanism.

## Fixture judgements and boundaries, stated plainly

- The trust anchor's issuer, terms and key are TEST
  fixtures (trust_anchor.py, marked TEST in their
  identities), on Stage 6's test-authority precedent: the
  harness verifier pins the harness issuer. They settle
  nothing about any production receipt issuer, its terms,
  or its key custody.
- HMAC is a symmetric stand-in for issuer authentication.
  The K6 property under test is the anchor's independent
  placement and the states' distinctness, not the
  cryptography; a production verifier would hold a public
  verification key against the issuer's private signing
  key, with the placement identical.
- The package entry's duplicated issuance fields are not
  separately policed against the record (see "The
  lifecycle states", above): the derivation takes issuance
  facts from the record, so a rewritten entry field cannot
  change an outcome — but a consumer reading only the
  package could be misled by one, and such a consumer is
  outside this stage's claim. The discipline the stage
  establishes is: derive from the record, as this stage
  does.
- The issuer's retained-content store is a directory in
  the harness temp space, standing in for whatever
  retention the production issuer performs; the lifecycle
  facts (retained vs collected) are the claim, not the
  storage medium.
- Concurrent writers and cross-process package mutation
  mid-derivation are outside the specified cases, as in
  every earlier stage (single-writer discipline assumed).

## Register effect (for the examiner's determination)

DR-04 — advanced on demonstration **within the harness**:
the receipt lifecycle is complete at the package boundary
— issuance, retained content, issuance digest, collection
and verification are distinct, linked facts under one
receipt identity; issuance alone satisfies neither
collection nor verification; verification requires the
independently pinned issuer/commitment anchor, not a
digest match; and closure states every receipt's actual
state as exactly the gap it is. What this does **not**
establish: the historical attempt-3 receipts are untouched
and unre-run (their contents remain absent, as recorded);
no production collecting component or workflow is
identified or built — DR-04's "responsible component
unresolved" sub-question, held open with DR-03's checkout
question (Ben-gated), is not discharged by a harness
mechanism; and no production trust anchor, issuer, or key
custody is settled (the anchor here is a marked TEST
fixture).

## Counts

Stage 7: 23/23. Regressions: Stage 1, 68/68; Stage 2,
27/27; Stage 3, 38/38; Stage 4, 36/36; Stage 5, 30/30;
Stage 6, 54/54. `stage1/`–`stage6/` unmodified.
