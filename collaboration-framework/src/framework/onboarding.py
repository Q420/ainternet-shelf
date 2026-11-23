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

Piece A1 (SPEC Rev 6, R38) adds the instance path beside the seat
path: the same ONBOARDING act, extended — never duplicated — with
an explicit subject discriminator. An instance onboards once, at
its assembly, under its own instance id; the fold keeps the
per-instance state beside the per-seat state, and neither
rewrites the other. Existing seat records and behaviour are
unchanged: a seat payload's subject is "seat", and histories
recorded before the discriminator existed carry no subject and
fold as seat records, as they always did.
"""

from __future__ import annotations

from .record import FrameworkStore  # noqa: F401  (typing aid)
from .doorway import Doorway  # noqa: F401


def onboard(doorway, orchestrator_token, seat_id, declaration,
            capability=None, limits=None, terms_acknowledged=None,
            terms_ref=None, identity_status="declared",
            attestation_ref=None, provider_model_id=None,
            view_seq=None):
    """Record a seat's onboarding (R18-R19). The declaration is
    carried byte-for-byte; the doorway refuses a provider-confirmed
    claim that arrives without its attestation reference, and the
    refusal is recorded. Piece 8 (A5): where a provider adapter
    supplies the provider-reported model identifier, it is
    recorded verbatim as its own attributed claim beside the
    declaration — it never raises the identity status."""
    if view_seq is None:
        view_seq = doorway.state()["head_seq"]
    payload = {
        "subject": "seat",
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
    if provider_model_id is not None:
        payload["provider_model_id"] = provider_model_id
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


def onboard_instance(doorway, orchestrator_token, seat_id,
                     instance_id, assembly_id, declaration,
                     provider_model_id=None, identity_status="declared",
                     capability=None, limits=None,
                     terms_acknowledged=None, terms_ref=None,
                     attestation_ref=None, view_seq=None):
    """Record a generated instance's onboarding (Piece A1, R38).

    The declaration is the instance's own, taken at its assembly
    (the provider adapter's `identify()` supplies it, with the
    provider-reported model id as its own attributed claim beside
    it — it never raises the identity status). The payload names
    the seat slot the instance fills and the assembly it belongs
    to; the ASSEMBLY_GENERATED that follows binds to this exact
    event by position and by the declaration's fingerprint —
    identity claims live only here, never duplicated into the
    assembly record."""
    if view_seq is None:
        view_seq = doorway.state()["head_seq"]
    payload = {
        "subject": "instance",
        "seat_id": seat_id,
        "instance_id": instance_id,
        "assembly_id": assembly_id,
        "declaration": declaration,
        "identity_status": identity_status,
        "capability": capability,
        "limits": limits,
        "terms_acknowledged": terms_acknowledged,
        "terms_ref": terms_ref,
    }
    if attestation_ref is not None:
        payload["attestation_ref"] = attestation_ref
    if provider_model_id is not None:
        payload["provider_model_id"] = provider_model_id
    return doorway.act(orchestrator_token, "ONBOARDING", payload,
                       view_seq=view_seq)


def instance_onboarding_record(doorway, instance_id):
    """The instance's onboarding record as the fold derives it,
    or None where no instance onboarding stands."""
    return doorway.state()["instance_onboarding"].get(instance_id)
