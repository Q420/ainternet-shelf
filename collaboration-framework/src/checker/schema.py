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
            "declaration": {"t": "any"},
            "identity_status": {"t": "str"},
            "capability": {"t": "any"},
            "limits": {"t": "any"},
            "terms_acknowledged": {"t": "any"},
            "terms_ref": {"t": "any"},
            "onboarded_seq": {"t": "int"},
            "attestation": {"t": "opt", "v": {"t": "obj", "f": {
                "event_seq": {"t": "int"},
                "attestation_ref": {"t": "any"}}}}}}},
        "claims": {"t": "map", "v": {"t": "obj", "f": {
            "author": {"t": "str"},
            "status": {"t": "str"},
            "subject": {"t": "str"},
            "status_seq": {"t": "int"}}}},
        "disagreements": {"t": "map", "v": {"t": "obj", "f": {
            "status": {"t": "str"},
            "claim_id": {"t": "any"},
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
                "content": {"t": "opt", "v": {
                    "t": "map", "v": {"t": "any"}}},
                "corrected": {"t": "bool"},
                "corrected_seq": {"t": "opt", "v": {"t": "int"}},
                "representational": {"t": "bool"},
                "acknowledged": {"t": "map", "v": {"t": "int"}}}}}}}},
        "gates": {"t": "map", "v": {"t": "obj", "f": {
            "outcome": {"t": "any"},
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
            "joint": {"t": "any"},
            "action": {"t": "any"}}}},
        "dispositions": {"t": "list", "v": {"t": "obj", "f": {
            "by": {"t": "str"},
            "event_seq": {"t": "int"}}}},
        "escalations": {"t": "list", "v": {"t": "obj", "f": {
            "by": {"t": "str"},
            "joint": {"t": "any"},
            "event_seq": {"t": "int"}}}},
        "rejections": {"t": "list", "v": {"t": "obj", "f": {
            "seat": {"t": "any"},
            "attempted": {"t": "any"},
            "ground": {"t": "any"},
            "event_seq": {"t": "int"},
            "part": {"t": "any"}}}},
        "sealed": {"t": "map", "v": {"t": "list", "v": {"t": "any"}}},
        "stalled": {"t": "map", "v": {"t": "obj", "f": {
            "kind": {"t": "any"},
            "part": {"t": "any"},
            "event_seq": {"t": "int"}}}},
        "tree": {"t": "map", "v": {"t": "any"}},
        "paused": {"t": "map", "v": {"t": "obj", "f": {
            "source_seq": {"t": "int"},
            "source_joint": {"t": "any"},
            "downstream": {"t": "any"}}}},
        "gate_declaration": {"t": "map", "v": {"t": "any"}},
        "gates_present": {"t": "bool"},
        "completion_claim_seq": {"t": "opt", "v": {"t": "int"}},
        "holder_unavailable": {"t": "list", "v": {"t": "obj", "f": {
            "joint": {"t": "any"},
            "by": {"t": "str"},
            "event_seq": {"t": "int"}}}},
        "commission_seq": {"t": "opt", "v": {"t": "int"}},
        "assembly_proposals": {"t": "list", "v": {"t": "obj", "f": {
            "event_seq": {"t": "int"},
            "crew": {"t": "any"}}}},
        "assembly_records": {"t": "list", "v": {"t": "obj", "f": {
            "event_seq": {"t": "int"},
            "proposal_seq": {"t": "any"},
            "gate_set": {"t": "map", "v": {"t": "any"}}}}},
        "run_ready_seq": {"t": "opt", "v": {"t": "int"}},
        "completion_claims": {"t": "list", "v": {"t": "obj", "f": {
            "event_seq": {"t": "int"},
            "by": {"t": "str"},
            "tree_part": {"t": "any"}}}},
        "routing_notes": {"t": "list", "v": {"t": "obj", "f": {
            "disagreement_id": {"t": "any"},
            "joint": {"t": "any"},
            "event_seq": {"t": "int"},
            "by": {"t": "str"}}}},
        "uncased": {"t": "map", "v": {
            "t": "list", "v": {"t": "str"}}},
        "pre_ack": {"t": "map", "v": {
            "t": "list", "v": {"t": "str"}}},
        "head_seq": {"t": "int"},
    },
}
