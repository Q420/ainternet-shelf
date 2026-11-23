"""The checker's copy of the projection schema — Piece 7 (§3.10).

A recursive description of the record fold's shape: every
top-level field, every nested object's field set, every
collection's element shape, at every depth. The framework-side
exporter holds its own copy (`framework.projection.SCHEMA`); this
copy is held independently, and neither implementation reads the
other's. The Piece 7 suite witnesses that the two copies are
canonically identical and that both implementations'
projections conform to the schema recursively — so a new fold
field, at any depth, fails the witness until both copies and
both implementations cover it (scope Rev 4, C3).

Node vocabulary (the schema is data, compared as canonical JSON):
  {"t": "any"}                  any JSON value
  {"t": "str"} / {"t": "int"} / {"t": "bool"} / {"t": "null"}
  {"t": "opt", "v": node}       null, or the node
  {"t": "list", "v": node}      a list whose items conform
  {"t": "map", "v": node}       an object with arbitrary keys
                                whose values conform
  {"t": "obj", "f": {k: node}}  an object with exactly these keys
  {"t": "fields", "f": {...}, "req": [...]}
                                an object whose keys are a SUBSET
                                of the named set — the permitted
                                key set for a verbatim payload
                                copy (a case's content): every
                                field present must be named here,
                                named fields conform when present,
                                and the "req" keys must be present

Correction round 1: values whose shapes the record contract
defines carry those shapes here — a map may have an open key
set while still requiring a defined value shape (tree values
are downstream-part lists; gate declarations map joints to kind
strings; a seal boundary is a list of seat ids).
"""

SCHEMA = {
    "t": "obj",
    "f": {
        "run_id": {"t": "opt", "v": {"t": "str"}},
        "lifecycle": {"t": "str"},
        "lifecycle_seq": {"t": "opt", "v": {"t": "int"}},
        "seats": {"t": "map", "v": {"t": "obj", "f": {
            "role": {"t": "str"},
            "identity_status": {"t": "str"}}}},
        "onboarding": {"t": "map", "v": {"t": "obj", "f": {
            "declaration": {"t": "opt", "v": {"t": "str"}},
            "provider_model_id": {"t": "opt", "v": {"t": "str"}},
            "identity_status": {"t": "str"},
            "capability": {"t": "opt", "v": {"t": "str"}},
            "limits": {"t": "opt", "v": {"t": "str"}},
            "terms_acknowledged": {"t": "opt", "v": {"t": "bool"}},
            "terms_ref": {"t": "opt", "v": {"t": "str"}},
            "onboarded_seq": {"t": "int"},
            "attestation": {"t": "opt", "v": {"t": "obj", "f": {
                "event_seq": {"t": "int"},
                "attestation_ref": {"t": "str"}}}}}}},
        "instance_onboarding": {"t": "map", "v": {"t": "obj", "f": {
            "declaration": {"t": "opt", "v": {"t": "str"}},
            "provider_model_id": {"t": "opt", "v": {"t": "str"}},
            "identity_status": {"t": "str"},
            "capability": {"t": "opt", "v": {"t": "str"}},
            "limits": {"t": "opt", "v": {"t": "str"}},
            "terms_acknowledged": {"t": "opt", "v": {"t": "bool"}},
            "terms_ref": {"t": "opt", "v": {"t": "str"}},
            "onboarded_seq": {"t": "int"},
            "attestation": {"t": "opt", "v": {"t": "obj", "f": {
                "event_seq": {"t": "int"},
                "attestation_ref": {"t": "str"}}}},
            "seat": {"t": "opt", "v": {"t": "str"}},
            "assembly_id": {"t": "opt", "v": {"t": "str"}}}}},
        "assemblies": {"t": "map", "v": {"t": "obj", "f": {
            "instance_id": {"t": "opt", "v": {"t": "str"}},
            "seat": {"t": "opt", "v": {"t": "str"}},
            "part": {"t": "opt", "v": {"t": "str"}},
            "case_id": {"t": "opt", "v": {"t": "str"}},
            "case_version": {"t": "opt", "v": {"t": "int"}},
            "proposal_seq": {"t": "opt", "v": {"t": "int"}},
            "onboarding_seq": {"t": "opt", "v": {"t": "int"}},
            "generated_seq": {"t": "int"},
            "verified_seq": {"t": "opt", "v": {"t": "int"}},
            "judged_seq": {"t": "opt", "v": {"t": "int"}},
            "judged_hash": {"t": "opt", "v": {"t": "str"}},
            "packed_seq": {"t": "opt", "v": {"t": "int"}},
            "pack_hash": {"t": "opt", "v": {"t": "str"}},
            "authorised_seq": {"t": "opt", "v": {"t": "int"}},
            "activated_seq": {"t": "opt", "v": {"t": "int"}},
            "credential": {"t": "str"},
            "grants_present": {"t": "bool"}}}},
        "loop_activations": {"t": "map", "v": {"t": "obj", "f": {
            "instance_id": {"t": "opt", "v": {"t": "str"}},
            "activated_seq": {"t": "opt", "v": {"t": "int"}},
            "case_id": {"t": "opt", "v": {"t": "str"}},
            "case_version": {"t": "opt", "v": {"t": "int"}},
            "iterations": {"t": "list", "v": {"t": "obj", "f": {
                "iteration": {"t": "opt", "v": {"t": "int"}},
                "event_seq": {"t": "int"},
                "step_ceiling": {"t": "opt", "v": {"t": "int"}},
                "deadline_seconds": {"t": "any"},
                "cursor_from": {"t": "opt", "v": {"t": "int"}},
                "cursor_to": {"t": "opt", "v": {"t": "int"}}}}},
            "stalled": {"t": "opt", "v": {"t": "obj", "f": {
                "ground": {"t": "opt", "v": {"t": "str"}},
                "event_seq": {"t": "int"},
                "iterations": {"t": "opt", "v": {"t": "int"}}}}}}}},
        "tool_requests": {"t": "list", "v": {"t": "obj", "f": {
            "instance_id": {"t": "opt", "v": {"t": "str"}},
            "request_id": {"t": "opt", "v": {"t": "str"}},
            "fingerprint": {"t": "opt", "v": {"t": "str"}},
            "tool": {"t": "opt", "v": {"t": "str"}},
            "requested_seq": {"t": "int"},
            "dispatch_id": {"t": "opt", "v": {"t": "str"}}}}},
        "dispatches": {"t": "map", "v": {"t": "obj", "f": {
            "instance_id": {"t": "opt", "v": {"t": "str"}},
            "request_id": {"t": "opt", "v": {"t": "str"}},
            "tool": {"t": "opt", "v": {"t": "str"}},
            "dispatch_seq": {"t": "int"},
            "started_seq": {"t": "opt", "v": {"t": "int"}},
            "outcome": {"t": "opt", "v": {"t": "str"}},
            "outcome_seq": {"t": "opt", "v": {"t": "int"}},
            "uncertain_seq": {"t": "opt", "v": {"t": "int"}},
            "reconciled_seq": {"t": "opt", "v": {"t": "int"}},
            "reconciled_outcome": {"t": "opt", "v": {"t": "str"}}}}},
        "claims": {"t": "map", "v": {"t": "obj", "f": {
            "author": {"t": "str"},
            "status": {"t": "str"},
            "subject": {"t": "str"},
            "status_seq": {"t": "int"}}}},
        "disagreements": {"t": "map", "v": {"t": "obj", "f": {
            "status": {"t": "str"},
            "claim_id": {"t": "opt", "v": {"t": "str"}},
            "by": {"t": "str"},
            "status_seq": {"t": "int"}}}},
        "contributions": {"t": "map", "v": {"t": "obj", "f": {
            "author": {"t": "str"},
            "tree_part": {"t": "opt", "v": {"t": "str"}}}}},
        "cases": {"t": "map", "v": {"t": "obj", "f": {
            "version": {"t": "int"},
            "seat": {"t": "opt", "v": {"t": "str"}},
            "versions": {"t": "map", "v": {"t": "obj", "f": {
                "verified": {"t": "opt", "v": {"t": "int"}},
                "judged": {"t": "opt", "v": {"t": "int"}},
                "notified": {"t": "opt", "v": {"t": "int"}},
                "issued": {"t": "opt", "v": {"t": "int"}},
                "content": {"t": "opt", "v": {"t": "fields", "f": {
                    "case_id": {"t": "str"},
                    "version": {"t": "int"},
                    "seat": {"t": "str"},
                    "representational": {"t": "bool"},
                    "assignment": {"t": "opt", "v": {"t": "str"}},
                    "tree": {"t": "map", "v": {
                        "t": "list", "v": {"t": "str"}}},
                    "part": {"t": "opt", "v": {"t": "str"}},
                    "evidence_boundary": {
                        "t": "list", "v": {"t": "str"}},
                    "verification_list": {"t": "opt", "v": {
                        "t": "list", "v": {"t": "str"}}},
                    "account": {"t": "str"},
                    "authority": {
                        "t": "list", "v": {"t": "str"}},
                    "criteria_mapping": {
                        "t": "map", "v": {"t": "str"}},
                    "loop_bounds": {"t": "opt", "v": {
                        "t": "fields", "f": {
                            "step_ceiling": {"t": "int"},
                            "deadline_seconds": {"t": "any"}},
                        "req": []}}},
                    "req": ["case_id", "version"]}},
                "corrected": {"t": "bool"},
                "corrected_seq": {"t": "opt", "v": {"t": "int"}},
                "representational": {"t": "bool"},
                "acknowledged": {"t": "map", "v": {"t": "int"}}}}}}}},
        "gates": {"t": "map", "v": {"t": "obj", "f": {
            "outcome": {"t": "opt", "v": {"t": "str"}},
            "by": {"t": "str"},
            "event_seq": {"t": "int"}}}},
        "certifications": {"t": "list", "v": {"t": "obj", "f": {
            "by": {"t": "str"},
            "coverage": {"t": "any"},
            "event_seq": {"t": "int"}}}},
        "findings": {"t": "list", "v": {"t": "obj", "f": {
            "by": {"t": "str"},
            "event_seq": {"t": "int"}}}},
        "rulings": {"t": "list", "v": {"t": "obj", "f": {
            "by": {"t": "str"},
            "event_seq": {"t": "int"},
            "joint": {"t": "opt", "v": {"t": "str"}},
            "action": {"t": "opt", "v": {"t": "str"}}}}},
        "dispositions": {"t": "list", "v": {"t": "obj", "f": {
            "by": {"t": "str"},
            "event_seq": {"t": "int"}}}},
        "escalations": {"t": "list", "v": {"t": "obj", "f": {
            "by": {"t": "str"},
            "joint": {"t": "opt", "v": {"t": "str"}},
            "event_seq": {"t": "int"}}}},
        "rejections": {"t": "list", "v": {"t": "obj", "f": {
            "seat": {"t": "opt", "v": {"t": "str"}},
            "attempted": {"t": "opt", "v": {"t": "str"}},
            "ground": {"t": "opt", "v": {"t": "str"}},
            "event_seq": {"t": "int"},
            "part": {"t": "opt", "v": {"t": "str"}}}}},
        "sealed": {"t": "map", "v": {"t": "list", "v": {"t": "str"}}},
        "stalled": {"t": "map", "v": {"t": "obj", "f": {
            "kind": {"t": "opt", "v": {"t": "str"}},
            "part": {"t": "opt", "v": {"t": "str"}},
            "event_seq": {"t": "int"}}}},
        "tree": {"t": "map", "v": {"t": "list", "v": {"t": "str"}}},
        "paused": {"t": "map", "v": {"t": "obj", "f": {
            "source_seq": {"t": "int"},
            "source_joint": {"t": "opt", "v": {"t": "str"}},
            "downstream": {"t": "list", "v": {"t": "str"}}}}},
        "gate_declaration": {"t": "map", "v": {"t": "str"}},
        "gates_present": {"t": "bool"},
        "completion_claim_seq": {"t": "opt", "v": {"t": "int"}},
        "holder_unavailable": {"t": "list", "v": {"t": "obj", "f": {
            "joint": {"t": "opt", "v": {"t": "str"}},
            "by": {"t": "str"},
            "event_seq": {"t": "int"}}}},
        "commission_seq": {"t": "opt", "v": {"t": "int"}},
        "assembly_proposals": {"t": "list", "v": {"t": "obj", "f": {
            "event_seq": {"t": "int"},
            "crew": {"t": "opt", "v": {"t": "list", "v": {
                "t": "obj", "f": {
                    "seat": {"t": "str"},
                    "role": {"t": "str"}}}}},
            "proposal_kind": {"t": "str"}}}},
        "assembly_records": {"t": "list", "v": {"t": "obj", "f": {
            "event_seq": {"t": "int"},
            "proposal_seq": {"t": "opt", "v": {"t": "int"}},
            "gate_set": {"t": "map", "v": {"t": "str"}}}}},
        "run_ready_seq": {"t": "opt", "v": {"t": "int"}},
        "completion_claims": {"t": "list", "v": {"t": "obj", "f": {
            "event_seq": {"t": "int"},
            "by": {"t": "str"},
            "tree_part": {"t": "opt", "v": {"t": "str"}}}}},
        "routing_notes": {"t": "list", "v": {"t": "obj", "f": {
            "disagreement_id": {"t": "opt", "v": {"t": "str"}},
            "joint": {"t": "opt", "v": {"t": "str"}},
            "event_seq": {"t": "int"},
            "by": {"t": "str"}}}},
        "uncased": {"t": "map", "v": {
            "t": "list", "v": {"t": "str"}}},
        "pre_ack": {"t": "map", "v": {
            "t": "list", "v": {"t": "str"}}},
        "head_seq": {"t": "int"},
    },
}
