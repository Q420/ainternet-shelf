"""Onboarding (SPEC SHEET §3.6, R18-R20; Piece 6).

Once per seat, before its first case, the orchestrator records the
seat's onboarding on the record, through the doorway:

- `onboard` records the model's identity declaration **verbatim**,
  its capability and limits as stated, and its acknowledgement of
  the terms (the rules of interaction as fixed by COLLABORATION),
  labelled with the declaration's status (R18-R19).
- `attest` records a later attestation: an ONBOARDING act carrying
  the attestation reference, which may raise the seat's identity
  status. The fold preserves the original onboarding record
  untouched and keeps the attestation as the upgrade's provenance.
  The reference is recorded provenance — recording it does not
  independently verify the provider's claim, and no live
  attestation service exists in this piece.

Onboarding confers readiness only (R20): it changes no authority,
records no case, and wakes no driver. The doorway binds the seat's
token at onboarding (scope F2 as settled: where an onboarding
record stands, `issue_token` binds against it).
"""

from __future__ import annotations

from .record import FrameworkStore  # noqa: F401  (typing aid)
from .doorway import Doorway  # noqa: F401


def onboard(doorway, orchestrator_token, seat_id, declaration,
            capability=None, limits=None, terms_acknowledged=None,
            terms_ref=None, identity_status="declared",
            attestation_ref=None, view_seq=None):
    """Record a seat's onboarding (R18-R19). The declaration is
    carried byte-for-byte; the doorway refuses a provider-confirmed
    claim that arrives without its attestation reference, and the
    refusal is recorded."""
    if view_seq is None:
        view_seq = doorway.state()["head_seq"]
    payload = {
        "seat_id": seat_id,
        "declaration": declaration,
        "capability": capability,
        "limits": limits,
        "terms_acknowledged": terms_acknowledged,
        "terms_ref": terms_ref,
        "identity_status": identity_status,
    }
    if attestation_ref is not None:
        payload["attestation_ref"] = attestation_ref
    return doorway.act(orchestrator_token, "ONBOARDING", payload,
                       view_seq=view_seq)


def attest(doorway, orchestrator_token, seat_id, identity_status,
           attestation_ref, view_seq=None):
    """Record an attestation for an onboarded seat (R18): the only
    route by which an identity status rises. The act carries the
    reference under which the attestation is filed; the original
    declaration and onboarding details stand untouched."""
    if view_seq is None:
        view_seq = doorway.state()["head_seq"]
    return doorway.act(
        orchestrator_token, "ONBOARDING",
        {"seat_id": seat_id, "identity_status": identity_status,
         "attestation_ref": attestation_ref},
        view_seq=view_seq)


def onboarding_record(doorway, seat_id):
    """The seat's onboarding record as the fold derives it, or
    None where no onboarding stands."""
    return doorway.state()["onboarding"].get(seat_id)
