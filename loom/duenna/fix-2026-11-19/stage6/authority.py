"""Duenna Stage 6 — the pinned governance authority (K10's
authority condition).

K10: an attribution record is minted by the adjudicating
authority — the governance authority outside the components —
and "the adjudicator's authority must itself be RESOLVABLE TO
A PINNED GOVERNANCE AUTHORITY RECORD: the implementation must
not let a component self-appoint as adjudicator."

This module is that condition, mechanised:

- A ``GovernanceAuthorityRecord`` is the authority instrument
  as data: who holds the authority, under what instrument,
  with a content digest. It is immutable after construction
  (the Stage 3/4 seal discipline).
- The PIN — the digest the programme independently holds for
  the one authority record it recognises — is a module
  constant, ``PINNED_AUTHORITY_DIGEST``, obtained from the
  record the programme pinned, never from a claimant.
- ``AttributionAuthority`` (the capability that may mint
  attributions) is issued ONLY by ``issue_authority()`` on
  presentation of a record whose digest equals the pin. Any
  other record — a component's self-authored instrument, a
  mutated copy of the genuine one — is refused with
  :class:`AuthorityRefused`.

CORRECTION ROUND 1 (Gate 1 verdict, shelf @ b9916f4f): as
first built, the capability's constructor was itself
publicly callable — ``AttributionAuthority(impostor)``
copied the impostor's identity and digest with no pin
check, and the consumers checked only the object's type,
so a component could self-appoint by constructing the
capability directly and bypassing ``issue_authority()``
entirely. The constructor now requires the module-private
issuance token (``_ISSUANCE_TOKEN``), which only
``issue_authority()`` holds and supplies after the pin
check; direct construction — from an impostor record, or
even from the genuine record — raises
:class:`AuthorityRefused`. The issued capability carries
the token it was issued under, and consumers verify it at
the point of use (:func:`capability_is_issued`: the object
is a capability, it carries THIS module's issuance token,
and its digest equals the pin), so a capability-shaped
object that never passed issuance is refused by minting
and by discrepancy resolution alike. As with the Stage 4
seal, this is an API boundary, not a sandbox: deliberately
importing the private token name is circumvention of the
same class as ``object.__setattr__`` forgery, outside the
declared threat model.

TEST-AUTHORITY DISTINCTION (Stage 0, plan v2): the authority
record below is a clearly-marked TEST authority fixture for
this harness. It settles nothing about the production
adjudicator authority; that decision (the register's DR-26
line) is Ben's, open, and untouched by any result here. The
production governance record of this programme
(GOVERNANCE-RECORD-V2, whose adjudicator-of-record is Alex
under Ben's corrected delegation) is the real-world
counterpart this fixture stands in for, in-harness only.
"""

from __future__ import annotations

import hashlib
import json


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _digest(obj) -> str:
    return hashlib.sha256(_canonical(obj)).hexdigest()


class AuthorityRefused(Exception):
    """An authority claim did not resolve to the pinned
    governance authority record. Carries the reason in
    ``details``. Nothing is minted on this path, ever."""

    def __init__(self, details: dict):
        self.details = details
        super().__init__(f"authority refused: {details!r}")


class _Sealed:
    """The Stage 3/4 seal discipline: once ``_sealed`` is set
    at the end of construction, every later assignment or
    deletion raises. Authority-bearing objects must not be
    rebindable after issuance."""

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


class GovernanceAuthorityRecord(_Sealed):
    """The authority instrument as a frozen fact: holder,
    instrument reference, and the attribution rules it acts
    under. Its digest is its identity."""

    def __init__(self, authority_id: str, holder: str,
                 instrument: str, rules: str):
        self.authority_id = authority_id
        self.holder = holder
        self.instrument = instrument
        self.rules = rules
        self._sealed = True

    def contents(self) -> dict:
        return {"authority_id": self.authority_id,
                "holder": self.holder,
                "instrument": self.instrument,
                "rules": self.rules}

    @property
    def digest(self) -> str:
        return _digest(self.contents())


def make_test_authority_record() -> GovernanceAuthorityRecord:
    """The harness's TEST authority fixture (see the module
    docstring's distinction). Marked TEST in its identity so
    no result obtained under it can be mistaken for a
    production adjudication."""
    return GovernanceAuthorityRecord(
        authority_id="TEST-AUTHORITY-STAGE6",
        holder="stage6-harness-test-adjudicator",
        instrument="TEST FIXTURE — Stage 0 test-authority "
                   "distinction; not a production instrument",
        rules="Ben's attribution rules (2026-11-18): classes "
              "SYSTEM / MODEL / INPUT; unattributable = "
              "UNKNOWN; attribution is one fact everywhere")


# The pin: the digest of the one authority record this
# programme recognises in-harness, held here independently of
# any claimant. Derived once from the fixture record above —
# the same value an examiner re-derives from the pinned
# record on the shelf.
PINNED_AUTHORITY_DIGEST = make_test_authority_record().digest


# The issuance token: a module-private unique object. Only
# issue_authority() holds it, and the capability constructor
# requires it — construction is therefore possible only on
# the verified issuance path (correction round 1).
_ISSUANCE_TOKEN = object()


class AttributionAuthority(_Sealed):
    """The capability to mint attribution records. Obtainable
    only through :func:`issue_authority`: the constructor
    requires the module-private issuance token, supplied
    only after the presented record has resolved to the
    pinned governance authority record. Sealed: the
    authority identity and digest it acts under cannot be
    rebound after issuance."""

    def __init__(self, record: GovernanceAuthorityRecord,
                 _token=None):
        if _token is not _ISSUANCE_TOKEN:
            raise AuthorityRefused(
                {"reason": "the attribution capability is "
                           "constructed only by "
                           "issue_authority(), after the "
                           "presented record resolves to the "
                           "pinned governance authority "
                           "record; direct construction is "
                           "self-appointment",
                 "presented_authority": getattr(
                     record, "authority_id", None)})
        self.authority_id = record.authority_id
        self.authority_digest = record.digest
        self._issued_token = _token
        self._sealed = True


def capability_is_issued(authority) -> bool:
    """Point-of-use verification for capability consumers
    (correction round 1, defence in depth): the object is
    an AttributionAuthority, it carries the issuance token
    it could only have received from issue_authority(), and
    the authority digest it acts under equals the
    independently held pin. A capability-shaped object
    assembled without issuance — constructor bypassed,
    attributes set by hand — fails the token check even if
    its digest copies the pin."""
    return isinstance(authority, AttributionAuthority) \
        and getattr(authority, "_issued_token", None) \
        is _ISSUANCE_TOKEN \
        and authority.authority_digest == PINNED_AUTHORITY_DIGEST


def issue_authority(
        presented: GovernanceAuthorityRecord) -> AttributionAuthority:
    """Issue the minting capability iff the presented record
    IS the pinned governance authority record (digest
    equality against the independently held pin). A component
    presenting its own instrument — however well-formed — is
    refused: self-appointment is the failure this gate
    exists to prevent."""
    if not isinstance(presented, GovernanceAuthorityRecord):
        raise AuthorityRefused(
            {"reason": "presented object is not a "
                       "GovernanceAuthorityRecord",
             "presented": type(presented).__name__})
    if presented.digest != PINNED_AUTHORITY_DIGEST:
        raise AuthorityRefused(
            {"reason": "authority record does not resolve to "
                       "the pinned governance authority record",
             "presented_digest": presented.digest,
             "pinned_digest": PINNED_AUTHORITY_DIGEST})
    return AttributionAuthority(presented, _ISSUANCE_TOKEN)
