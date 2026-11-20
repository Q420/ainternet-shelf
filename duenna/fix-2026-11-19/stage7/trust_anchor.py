"""Duenna Stage 7 — the independently pinned trust anchor
(K6's VERIFIED condition).

K6 (ID-SYSTEM-DESIGN-DRAFT-V3): a commitment receipt's
VERIFIED state "requires an independent trust anchor for the
receipt's issuer and the commitment terms — a digest match
alone proves the collected bytes match a digest (P8), not
that the receipt is authentic. The trust anchor and
commitment terms are themselves PINNED INDEPENDENTLY OF THE
PACKAGE BEING VERIFIED (v3): a verifier handed the receipt,
the digest and the purported anchor by the same source has
verified nothing."

This module is that anchor, mechanised:

- A ``TrustAnchor`` is the verifier's own pinned fact: the
  issuer identity it recognises, the commitment-terms digest
  it recognises, and the verification key for that issuer's
  authentication tags. It is sealed at construction (the
  Stage 3/4/6 seal discipline) — the pin a verifier acts
  under cannot be rebound mid-verification.
- The anchor is obtained from the verifier's own store,
  never from the package under verification. Nothing in
  receipts.py or package.py reads an anchor out of a
  package; a package that carries a purported anchor of its
  own has handed the verifier nothing.

CORRECTION ROUND 1 (Gate 1 verdict, shelf @ 9114fc3d): as
first built, this constructor was publicly callable with
arbitrary issuer, terms and key, and the derivation APIs in
receipts.py accepted any caller-supplied anchor — sealing
proved the object could not be rebound, not where it came
from, so a claimant could select the very pin their own
receipt verified under. Construction is now restricted to
the verifier's pinned-store path: the constructor requires
the module-private pin token (``_PIN_TOKEN``), which only
the store path (:func:`make_test_anchor` in-harness)
supplies; direct construction — of attacker values, or even
of the genuine values — raises :class:`AnchorRefused`. The
issued anchor carries the token, and consumers verify it at
the point of use (:func:`anchor_is_pinned`: the object is
an anchor, it carries THIS module's pin token, and its
issuer, terms digest and key all equal the independently
held pin), so an anchor-shaped object that never passed the
store — including one whose values copy the pin exactly —
is refused by every verification and closure entry point.
As with the Stage 4/6 seals, this is an API boundary, not a
sandbox: deliberately importing the private token name is
circumvention of the ``object.__setattr__`` class, outside
the declared threat model.
- Authentication is an HMAC-SHA256 tag over the receipt's
  identity, issuer, terms digest and content digest, keyed
  by the issuer's key. HMAC is the in-harness symmetric
  stand-in for issuer authentication: the property under
  test in this stage is the anchor's independent PLACEMENT
  and the distinctness of the lifecycle states, not the
  cryptography. A production system would hold a public
  verification key here against the issuer's private signing
  key; the placement — verifier-side, pinned, independent of
  the package — is identical.

TEST-ANCHOR DISTINCTION (Stage 0, plan v2; the Stage 6
test-authority precedent): the issuer, terms and key below
are clearly-marked TEST fixtures for this harness. They
settle nothing about any production receipt issuer or its
key custody.
"""

from __future__ import annotations

import hashlib
import hmac
import json


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def terms_digest(terms) -> str:
    """The digest of a commitment-terms value — the form in
    which terms are pinned, issued under, and authenticated
    against, so the terms themselves are never taken on a
    claimant's word."""
    return hashlib.sha256(_canonical(terms)).hexdigest()


def tag_message(receipt_id: str, issuer_id: str,
                terms_digest_value: str,
                content_digest: str) -> bytes:
    """The canonical message an authentication tag binds:
    this receipt, this issuer, these terms, this content."""
    return _canonical({
        "receipt_id": receipt_id,
        "issuer_id": issuer_id,
        "terms_digest": terms_digest_value,
        "content_digest": content_digest,
    })


def compute_tag(key: bytes, receipt_id: str, issuer_id: str,
                terms_digest_value: str,
                content_digest: str) -> str:
    """The issuer's authentication tag over a receipt's
    issuance facts, under the issuer's key."""
    return hmac.new(
        key,
        tag_message(receipt_id, issuer_id, terms_digest_value,
                    content_digest),
        hashlib.sha256).hexdigest()


class _Sealed:
    """The Stage 3/4/6 seal discipline: once ``_sealed`` is
    set at the end of construction, every later assignment or
    deletion raises. Anchor- and authority-bearing objects
    must not be rebindable after issuance."""

    def __setattr__(self, name, value):
        if getattr(self, "_sealed", False):
            raise AttributeError(
                f"{type(self).__name__} is sealed; {name!r} "
                f"cannot be assigned after construction")
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if getattr(self, "_sealed", False):
            raise AttributeError(
                f"{type(self).__name__} is sealed; {name!r} "
                f"cannot be deleted after construction")
        object.__delattr__(self, name)


class AnchorRefused(Exception):
    """An anchor claim did not resolve to the verifier's
    independently held pin. Carries the reason in
    ``details``. Nothing is verified on this path, ever."""

    def __init__(self, details: dict):
        self.details = details
        super().__init__(f"anchor refused: {details!r}")


# The pin token: a module-private unique object. Only the
# verifier's pinned-store path (make_test_anchor, below)
# holds it, and the anchor constructor requires it —
# construction is therefore possible only on the store path
# (correction round 1; the Stage 6 issuance-token pattern).
_PIN_TOKEN = object()


class TrustAnchor(_Sealed):
    """The verifier's independently pinned trust anchor.

    Obtainable only through the verifier's pinned-store
    path (:func:`make_test_anchor` in-harness): the
    constructor requires the module-private pin token,
    supplied only by that path. It is never read out of, or
    influenced by, the package under verification — that
    independence is the whole of its evidentiary value
    (K6, v3)."""

    def __init__(self, issuer_id: str, terms, key: bytes,
                 _token=None):
        if _token is not _PIN_TOKEN:
            raise AnchorRefused(
                {"reason": "the trust anchor is constructed "
                           "only by the verifier's "
                           "pinned-store path, from the pin "
                           "the verifier itself holds; direct "
                           "construction is a claimant "
                           "selecting their own pin",
                 "presented_issuer": issuer_id})
        if not isinstance(key, (bytes, bytearray)) or not key:
            raise ValueError("anchor key must be non-empty bytes")
        self.issuer_id = issuer_id
        # The terms are held as their canonical encoding, so
        # the anchor pins exactly the terms it was given and
        # hands out a fresh copy on every read.
        self._terms_canonical = _canonical(terms)
        self.terms_digest = terms_digest(terms)
        self._key = bytes(key)
        self._pin_token = _token
        self._sealed = True

    @property
    def terms(self):
        return json.loads(self._terms_canonical.decode("utf-8"))

    def authenticates(self, *, receipt_id: str, issuer_id: str,
                      terms_digest_value: str,
                      content_digest: str, tag) -> bool:
        """True iff the presented tag is this anchor's
        issuer's authentic tag over these exact issuance
        facts: the issuer must be the pinned issuer, the
        terms the pinned terms, and the tag must recompute
        under the pinned key. A tag that is absent, forged
        under another key, minted under other terms, or
        carried by another issuer's receipt fails — each is
        the same outcome (not authenticated), because the
        anchor recognises exactly one issuer acting under
        exactly one set of terms."""
        if issuer_id != self.issuer_id:
            return False
        if terms_digest_value != self.terms_digest:
            return False
        if not isinstance(tag, str) or not tag:
            return False
        expected = compute_tag(self._key, receipt_id, issuer_id,
                               terms_digest_value, content_digest)
        return hmac.compare_digest(expected, tag)


# ----------------------------------------------------------------
# TEST fixtures (see the module docstring's distinction).
# Marked TEST in their identities so no result obtained under
# them can be mistaken for a production verification.

TEST_ISSUER_ID = "TEST-ISSUER-STAGE7"

TEST_TERMS = {
    "instrument": "TEST FIXTURE — Stage 7 harness commitment "
                  "terms; not a production instrument",
    "commitment_class": "session-commitment",
    "obligation": "the issuer retains the committed content "
                  "and delivers it into the result package",
}

TEST_KEY = b"stage7-test-issuer-key-not-a-production-secret"


# The verifier's pin: the one (issuer, terms, key) this
# verifier recognises, held here independently of any
# claimant or package. Derived once from the TEST fixture
# above — the same values an examiner re-derives from the
# pinned fixture on the shelf. A production verifier's pin
# is its own deployment fact, held the same way.
_PINNED_ISSUER_ID = TEST_ISSUER_ID
_PINNED_TERMS_DIGEST = terms_digest(TEST_TERMS)
_PINNED_KEY = bytes(TEST_KEY)


def make_test_anchor() -> TrustAnchor:
    """The verifier's pinned-store path — the ONLY route by
    which an anchor is constructed: it issues the anchor
    under the verifier's own pin (the TEST fixture values
    in-harness), carrying the pin token no other caller
    holds. Standing in for the verifier's production pin
    in-harness only."""
    return TrustAnchor(TEST_ISSUER_ID, TEST_TERMS, TEST_KEY,
                       _PIN_TOKEN)


def anchor_is_pinned(anchor) -> bool:
    """Point-of-use verification for anchor consumers
    (correction round 1, defence in depth): the object is a
    TrustAnchor, it carries the pin token it could only have
    received from the pinned-store path, and the issuer,
    terms digest and key it acts under all equal the
    independently held pin. An anchor-shaped object
    assembled without the store — constructor bypassed,
    attributes set by hand — fails the token check even if
    its values copy the pin exactly."""
    return isinstance(anchor, TrustAnchor) \
        and getattr(anchor, "_pin_token", None) is _PIN_TOKEN \
        and anchor.issuer_id == _PINNED_ISSUER_ID \
        and anchor.terms_digest == _PINNED_TERMS_DIGEST \
        and getattr(anchor, "_key", None) == _PINNED_KEY
