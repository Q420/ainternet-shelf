"""Framework-side projection exporter — Piece 7 (§3.10).

The framework's half of the checker contract: it folds the record
(`record.replay`) and exports the resulting state as the comparison
projection the independent checker answers to. The projection is
the complete record fold, rendered as plain JSON data (a canonical
round-trip, so the exported value is exactly the value compared).

This module also holds the framework's copy of the PROJECTION
SCHEMA: a recursive description of the fold state's shape — every
top-level field, every nested object's field set, every
collection's element shape, at every depth. The checker holds its
own independent copy (`checker.schema`); neither implementation
reads the other's. The Piece 7 suite witnesses that the two copies
are canonically identical and that the live fold state, this
export, and the checker's reconstruction each conform to the
schema recursively — so a new fold field, at any depth, fails the
witness until both copies and both implementations cover it
(scope Rev 4, C3/C4).
"""
import json

from fabric.canonical import canonical
from framework.record import replay

# Schema node vocabulary:
#   {"t": "any"}                 any JSON value
#   {"t": "str"} / {"t": "int"} / {"t": "bool"} / {"t": "null"}
#   {"t": "opt", "v": node}      null, or the node
#   {"t": "list", "v": node}     a list whose items conform
#   {"t": "map", "v": node}      an object with arbitrary keys
#                                whose values conform
#   {"t": "obj", "f": {k: node}} an object with exactly these keys
#   {"t": "fields", "f": {...}, "req": [...]}
#                                an object whose keys are a SUBSET
#                                of the named set — the permitted
#                                key set for a verbatim payload
#                                copy (a case's content): every
#                                field present must be named here
#                                (C3's exhaustiveness), named
#                                fields conform when present, and
#                                the "req" keys must be present
#
# Correction round 1 (Vane's examination of the first build):
# values whose shapes the record contract defines are described
# by those shapes — tree values are downstream-part lists, gate
# declarations map joints to kind strings, a seal boundary is a
# list of seat ids — never left as unconstrained `any` regions
# where a nested field could hide.

_ANY = {"t": "any"}
_STR = {"t": "str"}
_INT = {"t": "int"}
_BOOL = {"t": "bool"}


def _opt(v):
    return {"t": "opt", "v": v}


def _list(v):
    return {"t": "list", "v": v}


def _map(v):
    return {"t": "map", "v": v}


def _obj(f):
    return {"t": "obj", "f": f}


def _fields(f, req=()):
    return {"t": "fields", "f": f, "req": list(req)}


_TREE_SHAPE = _map(_list(_STR))

# The permitted case-content key set (round 2): the event
# metadata every case payload carries, the six semantic content
# fields, and the office's classification mapping — the union
# the system's own builders produce (office.py's issued content;
# doorway.py's criteria_mapping). Shapes follow the builders:
# the office's authority term is the sorted list of act types
# the seat's role may perform; brief fields drawn with .get()
# may be null.
_CASE_CONTENT = _fields({
    "case_id": _STR, "version": _INT, "seat": _STR,
    "representational": _BOOL,
    "assignment": _opt(_STR), "tree": _TREE_SHAPE,
    "part": _opt(_STR), "evidence_boundary": _list(_STR),
    "verification_list": _opt(_list(_STR)),
    "account": _STR, "authority": _list(_STR),
    "criteria_mapping": _map(_STR),
    # Piece A3 (R49): the loop bounds a case may carry — a
    # step ceiling and a deadline in seconds (a JSON number,
    # whole or fractional; the schema has no narrower node).
    "loop_bounds": _opt(_fields({
        "step_ceiling": _INT, "deadline_seconds": _ANY})),
}, req=("case_id", "version"))

_CASE_VERSION = _obj({
    "verified": _opt(_INT), "judged": _opt(_INT),
    "notified": _opt(_INT), "issued": _opt(_INT),
    "content": _opt(_CASE_CONTENT),
    "corrected": _BOOL, "corrected_seq": _opt(_INT),
    "representational": _BOOL, "acknowledged": _map(_INT),
})

SCHEMA = _obj({
    "run_id": _opt(_STR),
    "lifecycle": _STR,
    "lifecycle_seq": _opt(_INT),
    "seats": _map(_obj({
        "role": _STR, "identity_status": _STR})),
    "onboarding": _map(_obj({
        "declaration": _opt(_STR),
        "provider_model_id": _opt(_STR), "identity_status": _STR,
        "capability": _opt(_STR), "limits": _opt(_STR),
        "terms_acknowledged": _opt(_BOOL),
        "terms_ref": _opt(_STR),
        "onboarded_seq": _INT,
        "attestation": _opt(_obj({
            "event_seq": _INT, "attestation_ref": _STR}))})),
    "instance_onboarding": _map(_obj({
        "declaration": _opt(_STR),
        "provider_model_id": _opt(_STR), "identity_status": _STR,
        "capability": _opt(_STR), "limits": _opt(_STR),
        "terms_acknowledged": _opt(_BOOL),
        "terms_ref": _opt(_STR),
        "onboarded_seq": _INT,
        "attestation": _opt(_obj({
            "event_seq": _INT, "attestation_ref": _STR})),
        "seat": _opt(_STR), "assembly_id": _opt(_STR)})),
    "assemblies": _map(_obj({
        "instance_id": _opt(_STR), "seat": _opt(_STR),
        "part": _opt(_STR), "case_id": _opt(_STR),
        "case_version": _opt(_INT),
        "proposal_seq": _opt(_INT), "onboarding_seq": _opt(_INT),
        "generated_seq": _INT,
        "verified_seq": _opt(_INT), "judged_seq": _opt(_INT),
        "judged_hash": _opt(_STR),
        "packed_seq": _opt(_INT), "pack_hash": _opt(_STR),
        "authorised_seq": _opt(_INT),
        "activated_seq": _opt(_INT),
        "credential": _STR, "grants_present": _BOOL,
        "catalogue_contract": _opt(_STR)})),
    "loop_activations": _map(_obj({
        "instance_id": _opt(_STR), "activated_seq": _opt(_INT),
        "case_id": _opt(_STR), "case_version": _opt(_INT),
        "iterations": _list(_obj({
            "iteration": _opt(_INT), "event_seq": _INT,
            "step_ceiling": _opt(_INT), "deadline_seconds": _ANY,
            "cursor_from": _opt(_INT),
            "cursor_to": _opt(_INT),
            "catalogue_hash": _opt(_STR),
            "registry_version": _opt(_STR)})),
        "stalled": _opt(_obj({
            "ground": _opt(_STR), "event_seq": _INT,
            "iterations": _opt(_INT)}))})),
    "tool_requests": _list(_obj({
        "instance_id": _opt(_STR), "request_id": _opt(_STR),
        "fingerprint": _opt(_STR), "tool": _opt(_STR),
        "requested_seq": _INT, "dispatch_id": _opt(_STR)})),
    "dispatches": _map(_obj({
        "instance_id": _opt(_STR), "request_id": _opt(_STR),
        "tool": _opt(_STR), "dispatch_seq": _INT,
        "started_seq": _opt(_INT), "outcome": _opt(_STR),
        "outcome_seq": _opt(_INT), "uncertain_seq": _opt(_INT),
        "reconciled_seq": _opt(_INT),
        "reconciled_outcome": _opt(_STR)})),
    "claims": _map(_obj({
        "author": _STR, "status": _STR, "subject": _STR,
        "status_seq": _INT})),
    "disagreements": _map(_obj({
        "status": _STR, "claim_id": _opt(_STR), "by": _STR,
        "status_seq": _INT})),
    "contributions": _map(_obj({
        "author": _STR, "tree_part": _opt(_STR)})),
    "cases": _map(_obj({
        "version": _INT, "seat": _opt(_STR),
        "versions": _map(_CASE_VERSION)})),
    "gates": _map(_obj({
        "outcome": _opt(_STR), "by": _STR, "event_seq": _INT})),
    "certifications": _list(_obj({
        "by": _STR, "coverage": _ANY, "event_seq": _INT})),
    "findings": _list(_obj({"by": _STR, "event_seq": _INT})),
    "rulings": _list(_obj({
        "by": _STR, "event_seq": _INT, "joint": _opt(_STR),
        "action": _opt(_STR)})),
    "dispositions": _list(_obj({"by": _STR, "event_seq": _INT})),
    "escalations": _list(_obj({
        "by": _STR, "joint": _opt(_STR), "event_seq": _INT})),
    "rejections": _list(_obj({
        "seat": _opt(_STR), "attempted": _opt(_STR),
        "ground": _opt(_STR), "event_seq": _INT,
        "part": _opt(_STR)})),
    "sealed": _map(_list(_STR)),
    "stalled": _map(_obj({
        "kind": _opt(_STR), "part": _opt(_STR),
        "event_seq": _INT})),
    "tree": _TREE_SHAPE,
    "paused": _map(_obj({
        "source_seq": _INT, "source_joint": _opt(_STR),
        "downstream": _list(_STR)})),
    "gate_declaration": _map(_STR),
    "gates_present": _BOOL,
    "completion_claim_seq": _opt(_INT),
    "holder_unavailable": _list(_obj({
        "joint": _opt(_STR), "by": _STR, "event_seq": _INT})),
    "commission_seq": _opt(_INT),
    "assembly_proposals": _list(_obj({
        "event_seq": _INT,
        "crew": _opt(_list(_obj({
            "seat": _STR, "role": _STR}))),
        "proposal_kind": _STR})),
    "assembly_records": _list(_obj({
        "event_seq": _INT, "proposal_seq": _opt(_INT),
        "gate_set": _map(_STR)})),
    "run_ready_seq": _opt(_INT),
    "completion_claims": _list(_obj({
        "event_seq": _INT, "by": _STR,
        "tree_part": _opt(_STR)})),
    "routing_notes": _list(_obj({
        "disagreement_id": _opt(_STR), "joint": _opt(_STR),
        "event_seq": _INT, "by": _STR})),
    "uncased": _map(_list(_STR)),
    "pre_ack": _map(_list(_STR)),
    "head_seq": _INT,
})


def conforms(value, node=None, path=""):
    """Recursive conformance of a value to the projection schema.

    Returns the list of paths at which the value departs from the
    schema (empty when it conforms). An object whose key set
    differs from an "obj" node's field set reports each missing
    and each unexpected key by path — at any depth.
    """
    if node is None:
        node = SCHEMA
    t = node["t"]
    if t == "any":
        return []
    if t == "opt":
        if value is None:
            return []
        return conforms(value, node["v"], path)
    if t == "str":
        return [] if isinstance(value, str) else [path]
    if t == "int":
        ok = isinstance(value, int) and not isinstance(value, bool)
        return [] if ok else [path]
    if t == "bool":
        return [] if isinstance(value, bool) else [path]
    if t == "null":
        return [] if value is None else [path]
    if t == "list":
        if not isinstance(value, list):
            return [path]
        out = []
        for i, item in enumerate(value):
            out += conforms(item, node["v"], f"{path}[{i}]")
        return out
    if t == "map":
        if not isinstance(value, dict):
            return [path]
        out = []
        for k, v in value.items():
            out += conforms(v, node["v"], f"{path}.{k}" if path else k)
        return out
    if t == "obj":
        if not isinstance(value, dict):
            return [path]
        out = []
        fields = node["f"]
        for k in fields:
            p = f"{path}.{k}" if path else k
            if k not in value:
                out.append(p)
            else:
                out += conforms(value[k], fields[k], p)
        for k in value:
            if k not in fields:
                out.append(f"{path}.{k}" if path else k)
        return out
    if t == "fields":
        if not isinstance(value, dict):
            return [path]
        out = []
        fields = node["f"]
        for k in node.get("req", []):
            if k not in value:
                out.append(f"{path}.{k}" if path else k)
        for k, v in value.items():
            p = f"{path}.{k}" if path else k
            if k not in fields:
                out.append(p)
            else:
                out += conforms(v, fields[k], p)
        return out
    return [path]


def project(state):
    """The comparison projection of a fold state: the state itself,
    carried through a canonical round-trip so the exported value is
    plain JSON data, exactly as it will be compared."""
    return json.loads(canonical(state))


def snapshot(store):
    """The framework's exported projection for a store's run: the
    record folded by the record service, projected as data. This is
    the untrusted comparison operand the checker receives (C4) —
    the checker never treats it as authority."""
    return project(replay(store))
