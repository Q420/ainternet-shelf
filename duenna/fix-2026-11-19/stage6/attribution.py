"""Duenna Stage 6 — attribution records (K10) and the three
referencing views.

K10's core rule (Ben's ruling 4, 2026-11-18): attribution is
ONE FACT. One attribution record per failure, minted by the
adjudicating authority under the pinned governance record
(see authority.py). Closure, ledger and adjudication REFERENCE
that record — none restates a class. A consumer that restated
the class would create a second home for the fact, and two
homes diverge (that divergence is DR-06, the defect this
stage's mechanism answers; DR-07 is the same disease in step
locations, answered by G6 in examiner.py).

The event stream's historical failure_class values
(SUBJECT_FAILURE, GOVERNANCE_FAILURE) are LOCAL mechanism
classifications. They are preserved as local — recorded as
what they are — and conversion of a local label into an
attribution class is PROHIBITED without the evidence and
adjudication Ben's rules require. :func:`convert_local_label`
exists so the prohibition has a mechanical edge: every
attempt raises :class:`ConversionRefused`.

Record discipline (Stages 1–3, 5): every write runs
``verify_record_current`` first — the persisted chain must
recompute AND its terminal must match this writer's in-memory
length and head. An integrity failure raises
:class:`RecordIntegrityRefused` and appends NOTHING. Every
fact a view returns is established from the record read back,
never from a live object's memory.

CORRECTION ROUND 1 (Gate 1 verdict, shelf @ b9916f4f): the
ledger no longer accepts a capability on type alone. The
authority is verified with ``capability_is_issued`` when the
ledger is constructed AND again inside ``mint_attribution``
at the moment of the act, so a capability-shaped object
that never passed the verified issuance path — or one
swapped onto the ledger after construction — cannot mint.
"""

from __future__ import annotations

from binder import CHAIN_VERIFICATION_FAILED, verify_record_current

from authority import (AttributionAuthority,
                       PINNED_AUTHORITY_DIGEST, capability_is_issued)

ATTRIBUTION_RECORDED = "ATTRIBUTION_RECORDED"
LOCAL_LABEL_RECORDED = "LOCAL_LABEL_RECORDED"

SYSTEM = "SYSTEM"
MODEL = "MODEL"
INPUT = "INPUT"
UNKNOWN = "UNKNOWN"
ATTRIBUTION_CLASSES = (SYSTEM, MODEL, INPUT, UNKNOWN)

# The historical local mechanism classifications carried by
# the event stream. Local means local: they classify what the
# mechanism did, they do not attribute the failure.
LOCAL_LABELS = ("SUBJECT_FAILURE", "GOVERNANCE_FAILURE")


class RecordIntegrityRefused(Exception):
    """The record the writer was about to extend failed its
    integrity check. Carries the chain failure under
    ``record_chain_verification_failed``. Nothing was
    appended."""

    def __init__(self, details: dict):
        self.details = details
        super().__init__(f"record integrity refused: {details!r}")


class AttributionRefused(Exception):
    """A mint was refused: no authority, a second attribution
    for one failure, or a class outside Ben's vocabulary.
    Nothing was appended."""

    def __init__(self, details: dict):
        self.details = details
        super().__init__(f"attribution refused: {details!r}")


class ConversionRefused(Exception):
    """A local mechanism label was presented for conversion
    into an attribution class. K10 prohibits the conversion
    itself — a label is not evidence, and no adjudication
    stands behind it. The label remains what it was: local."""

    def __init__(self, label, target):
        self.label = label
        self.target = target
        super().__init__(
            f"conversion refused: local label {label!r} is a "
            f"mechanism classification, not an attribution; "
            f"it cannot become {target!r} without evidence "
            f"and adjudication under the pinned authority")


def _verified_events(record):
    events, failure = verify_record_current(record)
    if failure is not None:
        raise RecordIntegrityRefused(
            {CHAIN_VERIFICATION_FAILED: failure})
    return events


def _find(events, event_type, key, value):
    for ev in events:
        if ev.get("type") == event_type \
                and ev.get("body", {}).get(key) == value:
            return ev
    return None


class AttributionLedger:
    """Mints and reads attribution records on one record,
    under one issued authority. The ledger holds no
    attribution state in memory: what exists is what the
    record read-back shows."""

    def __init__(self, record, authority: AttributionAuthority):
        if not isinstance(authority, AttributionAuthority):
            raise AttributionRefused(
                {"reason": "minting requires an issued "
                           "AttributionAuthority (authority.py); "
                           "a component cannot appoint itself",
                 "presented": type(authority).__name__})
        self._require_issued(authority)
        self.record = record
        self.authority = authority

    @staticmethod
    def _require_issued(authority):
        """The capability must be one the verified issuance
        path could have produced (correction round 1): it
        carries issue_authority()'s issuance token and acts
        under the pinned digest. A directly constructed or
        hand-assembled capability object is refused here,
        before any mint is attempted under it."""
        if not capability_is_issued(authority):
            raise AttributionRefused(
                {"reason": "the presented capability was not "
                           "issued through the verified "
                           "issuance path (authority.py "
                           "issue_authority); a forged or "
                           "self-constructed capability cannot "
                           "mint",
                 "presented_digest": getattr(
                     authority, "authority_digest", None),
                 "pinned_digest": PINNED_AUTHORITY_DIGEST})

    # ------------------------------------------------------
    # Minting
    # ------------------------------------------------------
    def mint_attribution(self, failure_ref: str, cls: str,
                         basis_refs) -> dict:
        """Mint THE attribution record for one failure.
        ``failure_ref`` is the failure's identity (K9: run /
        event reference). ``basis_refs`` are the evidence
        references the class rests on. One record per failure:
        a second mint for the same failure is refused — a
        disagreement about an attribution is a discrepancy
        (discrepancy.py), never a second attribution."""
        # Verified again at the moment of the act
        # (correction round 1): a capability swapped onto
        # this ledger after construction is refused here,
        # before anything is read or written under it.
        self._require_issued(self.authority)
        if cls not in ATTRIBUTION_CLASSES:
            raise AttributionRefused(
                {"reason": "class outside Ben's attribution "
                           "vocabulary",
                 "class": cls,
                 "vocabulary": list(ATTRIBUTION_CLASSES)})
        events = _verified_events(self.record)
        existing = _find(events, ATTRIBUTION_RECORDED,
                         "failure_ref", failure_ref)
        if existing is not None:
            raise AttributionRefused(
                {"reason": "an attribution record already "
                           "exists for this failure; one "
                           "failure, one record — a "
                           "disagreement mints a discrepancy, "
                           "not a second attribution",
                 "failure_ref": failure_ref,
                 "existing_event": existing["digest"]})
        event = self.record.append(ATTRIBUTION_RECORDED, {
            "failure_ref": failure_ref,
            "class": cls,
            "basis_refs": list(basis_refs),
            "attributor": self.authority.authority_id,
            "authority_digest": self.authority.authority_digest,
        })
        return event

    def record_local_label(self, failure_ref: str,
                           label: str) -> dict:
        """Preserve a historical local mechanism label AS
        LOCAL. This is the only legitimate fate of a label in
        this stage: recorded, named as local, never converted."""
        if label not in LOCAL_LABELS:
            raise AttributionRefused(
                {"reason": "not a historical local label",
                 "label": label, "local_labels": list(LOCAL_LABELS)})
        _verified_events(self.record)
        return self.record.append(LOCAL_LABEL_RECORDED, {
            "failure_ref": failure_ref,
            "local_label": label,
            "status": "local mechanism classification — "
                      "preserved as local, not an attribution",
        })

    # ------------------------------------------------------
    # Reading back
    # ------------------------------------------------------
    def attribution_for(self, failure_ref: str):
        """The recorded attribution for a failure, established
        from the verified read-back: the event digest (the
        reference every consumer cites) and the body as
        recorded. None when no attribution exists."""
        events = _verified_events(self.record)
        ev = _find(events, ATTRIBUTION_RECORDED,
                   "failure_ref", failure_ref)
        if ev is None:
            return None
        return {"attribution_event": ev["digest"],
                "seq": ev["seq"], "body": ev["body"]}


def convert_local_label(label: str, target_class: str):
    """The prohibited conversion, given a mechanical edge so
    it can be refused rather than merely discouraged. There
    is no path through this function: it always raises."""
    raise ConversionRefused(label, target_class)


# ----------------------------------------------------------
# The three referencing views (K10: REFERENCE, never restate)
# ----------------------------------------------------------
def _reference_view(record, failure_ref: str, surface: str):
    """Each surface independently re-derives its view from
    the record read back: it locates the one attribution
    record and returns a REFERENCE to it — the event digest,
    and the class AS READ FROM THAT RECORD at read time. A
    view stores nothing and asserts nothing of its own; if
    the record's attribution changed (it cannot — appends
    only, one per failure), every view would show the change
    identically, because there is only one fact to show."""
    events = _verified_events(record)
    ev = _find(events, ATTRIBUTION_RECORDED,
               "failure_ref", failure_ref)
    if ev is None:
        return {"surface": surface, "failure_ref": failure_ref,
                "attribution_event": None, "class": None}
    return {"surface": surface, "failure_ref": failure_ref,
            "attribution_event": ev["digest"],
            "class": ev["body"]["class"],
            "attributor": ev["body"]["attributor"]}


def closure_view(record, failure_ref: str) -> dict:
    return _reference_view(record, failure_ref, "closure")


def ledger_view(record, failure_ref: str) -> dict:
    return _reference_view(record, failure_ref, "ledger")


def adjudication_view(record, failure_ref: str) -> dict:
    return _reference_view(record, failure_ref, "adjudication")
