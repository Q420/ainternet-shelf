"""Duenna Stage 7 — the commitment receipt lifecycle (K6).

K6 (ID-SYSTEM-DESIGN-DRAFT-V3): "A commitment receipt is a
lifecycle of five linked facts under one receipt identity:
ISSUED, CONTENT (retained), DIGEST (at issuance), COLLECTED
(content entered the result package), VERIFIED." DR-04 is
the defect this stage answers: receipts were issued —
issuance events and SHA-256 values exist — and the lifecycle
stopped there; the contents were never collected into the
result package, and issuance was treated as if it
established retained, checkable evidence. It does not:
"Issuance never satisfies collection or verification."

THE FIVE FACTS, AS BUILT:

- ISSUED — a ``RECEIPT_ISSUED`` event on the run record
  (Stage 1's EventRecord), carrying the receipt identity,
  the commitment it receipts, the issuer, the terms digest,
  and the content digest. One receipt per (issuer,
  commitment): the identity is a canonical function of the
  pair, and re-issuance is refused.
- CONTENT (retained) — the committed bytes, retained by the
  issuer in its own store (``IssuerStore``) from issuance.
  Retention is the issuer's fact; it is not collection.
- DIGEST (at issuance) — the SHA-256 of the content,
  computed at issuance and carried identically by the record
  event and the package entry.
- COLLECTED — the content has entered the result package
  (package.py). Established by reading the package back,
  never from a ``RECEIPT_COLLECTED`` event's say-so: the
  event records the act, the package's bytes are the fact.
  (DR-04's lesson, mechanised: an event claiming collection
  over a package that lacks the content is exactly the
  papered-over failure this stage exists to refuse.)
- VERIFIED — a DERIVATION, recomputed at every read from
  primary facts: the record's issuance, the package's
  content bytes, the package entry's presented tag, and the
  verifier's independently pinned trust anchor
  (trust_anchor.py). Nothing — no event, no package field —
  can assert VERIFIED into being; a ``RECEIPT_VERIFIED``
  event is deliberately never written, because a recorded
  claim of verification is precisely what the derivation
  exists to replace.

THE LIFECYCLE STATES (distinct, and reported as exactly
themselves in the closure account):

- ``VERIFIED`` — collected, content digest matches the
  issuance digest, and the presented tag authenticates
  under the pinned anchor (pinned issuer, pinned terms).
- ``ISSUED_CONTENT_NOT_COLLECTED`` — issuance on the
  record, the receipt's entry in the package, but no
  content in the package. DR-04's state.
- ``MISSING_FROM_PACKAGE`` — issuance on the record, but
  the package carries no entry for the receipt at all (the
  Test 7 removal case). Distinct from the state above: the
  receipt itself is gone from the package, not merely its
  content uncollected.
- ``COLLECTED_DIGEST_MISMATCH`` — content in the package
  whose bytes do not hash to the issuance digest.
- ``COLLECTED_UNAUTHENTICATED`` — content present and
  digest-matching, but authentication fails: no tag, a
  forged tag, a tag minted under other terms, another
  issuer. A digest match alone proves the collected bytes
  match a digest — not that the receipt is authentic (P8).

RECORD DISCIPLINE (Stages 1–3, 5): every write path —
issuance, collection, the lifecycle account, closure —
first runs Stage 3's ``verify_record_current`` (chain
recomputation AND terminal binding) over the record it is
about to extend. An integrity failure raises
:class:`ReceiptRefused` carrying
``record_chain_verification_failed`` and writes NOTHING.

CLOSURE REPORTING (K6 + Stage 1): ``close_with_receipt_
account`` appends a ``RECEIPT_LIFECYCLE_ACCOUNT`` event
naming every issued receipt's derived state, then closes
the run through Stage 1's ClosureWriter with every
non-VERIFIED receipt named in the closure account's
unknowns as the exact gap it is — so the account is
INCOMPLETE while any receipt is short of VERIFIED, and no
deficient state is ever stated as, or rounded up to,
VERIFIED.

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (K6),
PROCESS-TREE-AND-PLAN.md v2, Stage 7; DEFECT-REGISTER.md
DR-04.
"""

from __future__ import annotations

import hashlib
import json
import os

from binder import CHAIN_VERIFICATION_FAILED, verify_record_current
from closure import ClosureWriter

from trust_anchor import TrustAnchor, compute_tag, terms_digest

RECEIPT_ISSUED = "RECEIPT_ISSUED"
RECEIPT_COLLECTED = "RECEIPT_COLLECTED"
RECEIPT_LIFECYCLE_ACCOUNT = "RECEIPT_LIFECYCLE_ACCOUNT"

# The lifecycle states. Distinct values for distinct facts;
# the closure account states each receipt's state verbatim.
VERIFIED = "VERIFIED"
ISSUED_CONTENT_NOT_COLLECTED = "ISSUED_CONTENT_NOT_COLLECTED"
MISSING_FROM_PACKAGE = "MISSING_FROM_PACKAGE"
COLLECTED_DIGEST_MISMATCH = "COLLECTED_DIGEST_MISMATCH"
COLLECTED_UNAUTHENTICATED = "COLLECTED_UNAUTHENTICATED"

ALL_STATES = (VERIFIED, ISSUED_CONTENT_NOT_COLLECTED,
              MISSING_FROM_PACKAGE, COLLECTED_DIGEST_MISMATCH,
              COLLECTED_UNAUTHENTICATED)


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def receipt_id_for(issuer_id: str, commitment_id: str) -> str:
    """A receipt's identity: a canonical function of the
    issuer and the commitment it receipts — computed, not
    issued (the Stage 5 identity discipline), so one
    (issuer, commitment) pair names exactly one receipt in
    every process that derives it."""
    return _sha256(_canonical({
        "issuer_id": issuer_id,
        "commitment_id": commitment_id,
    }))


class ReceiptRefused(Exception):
    """A receipt operation was refused. Carries the receipt
    identity (``None`` for account-level operations) and the
    refusal evidence in ``details``. A refusal under
    ``record_chain_verification_failed`` is raised WITHOUT
    recording anything on the record."""

    def __init__(self, receipt_id, details: dict):
        self.receipt_id = receipt_id
        self.details = details
        super().__init__(
            f"receipt operation refused for {receipt_id!r}: "
            f"{details!r}")


class ReceiptIssuer:
    """The issuing capability: an issuer identity, its
    authentication key, and the commitment terms it issues
    under. Possession of the key IS the issuance authority —
    without it, no tag the pinned anchor accepts can be
    produced. Sealed after construction (the Stage 3/4/6
    discipline): the identity and terms an issuer acts under
    cannot be rebound after the fact."""

    def __init__(self, issuer_id: str, key: bytes, terms):
        if not isinstance(key, (bytes, bytearray)) or not key:
            raise ValueError("issuer key must be non-empty bytes")
        self.issuer_id = issuer_id
        self._terms_canonical = _canonical(terms)
        self.terms_digest = terms_digest(terms)
        self._key = bytes(key)
        self._sealed = True

    def __setattr__(self, name, value):
        if getattr(self, "_sealed", False):
            raise AttributeError(
                f"ReceiptIssuer is sealed; {name!r} cannot be "
                f"assigned after construction")
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if getattr(self, "_sealed", False):
            raise AttributeError(
                f"ReceiptIssuer is sealed; {name!r} cannot be "
                f"deleted after construction")
        object.__delattr__(self, name)

    @property
    def terms(self):
        return json.loads(self._terms_canonical.decode("utf-8"))

    def tag_for(self, receipt_id: str,
                content_digest: str) -> str:
        """This issuer's authentication tag over a receipt's
        issuance facts, under this issuer's key and terms."""
        return compute_tag(self._key, receipt_id, self.issuer_id,
                           self.terms_digest, content_digest)


class IssuerStore:
    """The issuer's retained content (K6's CONTENT fact):
    the committed bytes, held by the issuer from issuance
    until collection delivers them into the package. A
    directory on disk; reads go back to disk."""

    def __init__(self, root: str):
        self.root = root

    def _path(self, receipt_id: str) -> str:
        return os.path.join(self.root, receipt_id + ".content")

    def retain(self, receipt_id: str, content: bytes) -> None:
        os.makedirs(self.root, exist_ok=True)
        tmp = self._path(receipt_id) + ".tmp"
        with open(tmp, "wb") as f:
            f.write(bytes(content))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self._path(receipt_id))

    def retained(self, receipt_id: str) -> bytes | None:
        path = self._path(receipt_id)
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return f.read()


# ----------------------------------------------------------------
# Record discipline


def _verify_or_refuse(record, receipt_id):
    """The shared pre-write check: the record's current chain
    must recompute AND its terminal must be the terminal this
    record instance is about to extend. Returns the verified
    events; raises ReceiptRefused (writing nothing) on any
    integrity failure."""
    events, failure = verify_record_current(record)
    if failure is not None:
        raise ReceiptRefused(receipt_id, {
            CHAIN_VERIFICATION_FAILED: failure})
    return events


def _issuance_event(events, receipt_id: str):
    for ev in events:
        if ev.get("type") == RECEIPT_ISSUED \
                and ev.get("body", {}).get("receipt_id") \
                == receipt_id:
            return ev
    return None


# ----------------------------------------------------------------
# Issuance and collection


def issue_receipt(record, package, issuer: ReceiptIssuer,
                  store: IssuerStore, commitment_id: str,
                  content: bytes) -> dict:
    """Issue a commitment receipt: retain the content in the
    issuer's store, place the receipt (issuance facts + the
    issuer's authentication tag, NO content) into the
    package, and record RECEIPT_ISSUED on the run record.

    Issuance establishes exactly the ISSUED fact. The receipt
    it produces is in state ISSUED_CONTENT_NOT_COLLECTED
    until collection — issuance never satisfies collection
    or verification (K6)."""
    if not isinstance(commitment_id, str) \
            or not commitment_id.strip():
        raise ValueError(
            f"commitment_id must name something: "
            f"{commitment_id!r}")
    if not isinstance(content, (bytes, bytearray)):
        raise TypeError("content must be bytes")
    content = bytes(content)
    receipt_id = receipt_id_for(issuer.issuer_id, commitment_id)
    events = _verify_or_refuse(record, receipt_id)
    if _issuance_event(events, receipt_id) is not None:
        raise ReceiptRefused(receipt_id, {
            "reason": "a receipt for this (issuer, commitment) "
                      "already stands issued on the record; "
                      "one commitment has exactly one receipt",
            "commitment_id": commitment_id})
    content_digest = _sha256(content)
    issuance = {
        "receipt_id": receipt_id,
        "commitment_id": commitment_id,
        "issuer_id": issuer.issuer_id,
        "terms_digest": issuer.terms_digest,
        "content_digest": content_digest,
    }
    # CONTENT (retained): the issuer keeps the bytes from
    # issuance. Retention is not collection.
    store.retain(receipt_id, content)
    # The receipt as it enters the package: the issuance
    # facts plus the issuer's authentication tag. No content
    # — collection is a separate, later fact.
    package.write_entry(receipt_id, {
        **issuance,
        "auth_tag": issuer.tag_for(receipt_id, content_digest),
    })
    return record.append(RECEIPT_ISSUED, issuance)


def collect_receipt(record, package, store: IssuerStore,
                    receipt_id: str) -> dict:
    """Collect a receipt's retained content into the result
    package, and record RECEIPT_COLLECTED. Collection is
    established by the package's bytes (see the module
    docstring); this event records the act."""
    events = _verify_or_refuse(record, receipt_id)
    issuance = _issuance_event(events, receipt_id)
    if issuance is None:
        raise ReceiptRefused(receipt_id, {
            "reason": "no issuance for this receipt stands on "
                      "the record; there is nothing to collect"})
    if package.read_entry(receipt_id) is None:
        raise ReceiptRefused(receipt_id, {
            "reason": "the receipt is missing from the "
                      "package; collection delivers content "
                      "into the receipt's package entry, and "
                      "there is no entry to collect into"})
    if package.has_content(receipt_id):
        raise ReceiptRefused(receipt_id, {
            "reason": "this receipt's content already stands "
                      "collected in the package"})
    content = store.retained(receipt_id)
    if content is None:
        raise ReceiptRefused(receipt_id, {
            "reason": "the issuer retains no content for this "
                      "receipt; collection has nothing to "
                      "deliver"})
    package.write_content(receipt_id, content)
    return record.append(RECEIPT_COLLECTED, {
        "receipt_id": receipt_id,
        "commitment_id": issuance["body"]["commitment_id"],
        "content_digest": _sha256(content),
    })


# ----------------------------------------------------------------
# The lifecycle derivation


def _state_from(events, package, anchor: TrustAnchor,
                receipt_id: str):
    """Derive one receipt's lifecycle state from primary
    facts: the record's issuance, the package as it stands
    on disk, and the verifier's pinned anchor. Returns None
    when no issuance for this receipt stands on the record
    (not a lifecycle receipt)."""
    issuance = _issuance_event(events, receipt_id)
    if issuance is None:
        return None
    body = issuance["body"]
    entry = package.read_entry(receipt_id)
    if entry is None:
        return MISSING_FROM_PACKAGE
    content = package.read_content(receipt_id)
    if content is None:
        return ISSUED_CONTENT_NOT_COLLECTED
    if _sha256(content) != body["content_digest"]:
        return COLLECTED_DIGEST_MISMATCH
    if not anchor.authenticates(
            receipt_id=receipt_id,
            issuer_id=body["issuer_id"],
            terms_digest_value=body["terms_digest"],
            content_digest=body["content_digest"],
            tag=entry.get("auth_tag")):
        return COLLECTED_UNAUTHENTICATED
    return VERIFIED


def lifecycle_state(record, package, anchor: TrustAnchor,
                    receipt_id: str):
    """One receipt's lifecycle state, derived from the
    record and package read back under a verified chain.
    This derivation IS the verification: VERIFIED is
    returned only when the full independently authenticated
    lifecycle stands — issued, content collected, digest
    matching, and the presented tag authenticating under
    the pinned anchor."""
    events = _verify_or_refuse(record, receipt_id)
    return _state_from(events, package, anchor, receipt_id)


def receipt_account(record, package,
                    anchor: TrustAnchor) -> dict:
    """Every receipt's lifecycle state, derived in issuance
    order, plus any package entries that no issuance on the
    record accounts for. The closure account is built from
    this — the states are derived once, here, from primary
    facts, and reported verbatim."""
    events = _verify_or_refuse(record, None)
    receipts = []
    issued_ids = []
    for ev in events:
        if ev.get("type") == RECEIPT_ISSUED:
            body = ev["body"]
            receipt_id = body["receipt_id"]
            issued_ids.append(receipt_id)
            receipts.append({
                "receipt_id": receipt_id,
                "commitment_id": body["commitment_id"],
                "state": _state_from(events, package, anchor,
                                     receipt_id),
            })
    unrecorded = sorted(set(package.entry_ids())
                        - set(issued_ids))
    return {"receipts": receipts,
            "unrecorded_package_entries": unrecorded}


def append_receipt_account(record, package,
                           anchor: TrustAnchor) -> dict:
    """Append the RECEIPT_LIFECYCLE_ACCOUNT event: the
    derived state of every receipt on the record, stated
    exactly as derived."""
    account = receipt_account(record, package, anchor)
    return record.append(RECEIPT_LIFECYCLE_ACCOUNT, account)


def close_with_receipt_account(record, package,
                               anchor: TrustAnchor,
                               termination: str,
                               failures=None,
                               execution: str = "COMPLETED",
                               adjudication: str
                               = "NOT_REQUIRED"):
    """Close a run with its receipt lifecycle accounted.

    Appends the RECEIPT_LIFECYCLE_ACCOUNT, then closes
    through Stage 1's ClosureWriter. Every receipt short of
    VERIFIED — and every package entry no issuance accounts
    for — is named in the closure account's unknowns as the
    exact gap it is, so the closure account is INCOMPLETE
    while any gap stands (Stage 1's rule: an account naming
    unknowns cannot declare COMPLETE), and a deficient
    receipt is never stated as VERIFIED. Returns
    ``(account_event, closure_event)``."""
    account_event = append_receipt_account(record, package,
                                           anchor)
    account = account_event["body"]
    gaps = [
        f"receipt {r['receipt_id']} "
        f"(commitment {r['commitment_id']}): {r['state']}"
        for r in account["receipts"] if r["state"] != VERIFIED
    ]
    gaps += [
        f"package entry {rid}: no issuance on the record"
        for rid in account["unrecorded_package_entries"]
    ]
    closure_event = ClosureWriter(record).close(
        termination,
        failures=failures,
        execution=execution,
        adjudication=adjudication,
        unknowns=gaps,
    )
    return account_event, closure_event
