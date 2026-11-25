"""The checker's own replay of the record fold — Piece 7 (§3.10).

An independent implementation of the fold the record service
performs: starting from the blank state, each recorded event is
applied in stream order, and the resulting state is the checker's
reconstruction — the value its projection comparison answers
with. Nothing here is imported from the framework's record,
doorway, gates or orchestrator modules; the semantics are
re-derived from the record's contract (SPEC SHEET §3.1/§3.10,
R4): the fold applies what the record holds, position-sensitively
where the record is position-sensitive (a contribution's case
standing is judged at its own event position), and it invents
nothing.

A recorded event the fold cannot interpret — an unknown type, or
a payload whose values are of the wrong type for the fields the
fold reads, or whose shape its event type requires and lacks —
halts the replay with a classed `schema_invalid` halt naming the
position (scope Rev 4, C6). It never escapes as an exception.
"""

CASE_CONTENT_FIELDS = ("assignment", "tree", "part",
                       "evidence_boundary", "verification_list",
                       "account", "authority", "loop_bounds",
                       "glossary")

_STATUS_RANK = {"unverified": 0, "declared": 1,
                "provider-confirmed": 2}

_CASE_ACTS = ("CASE_ISSUED", "CASE_CORRECTED", "CASE_VERIFIED",
              "CASE_JUDGED", "CASE_NOTIFIED", "CASE_ACKNOWLEDGED")

_KNOWN_TYPES = {
    "RUN_COMMISSIONED", "SEAT_BOUND", "CONTRIBUTION", "COMMENT",
    "DISAGREEMENT", "DISAGREEMENT_SETTLED", "GATE_OUTCOME",
    "FINDING", "RULING", "DISPOSITION", "CERTIFICATION",
    "CASE_ISSUED", "CASE_CORRECTED", "CASE_VERIFIED", "CASE_JUDGED",
    "CASE_NOTIFIED", "CASE_ACKNOWLEDGED", "DRIVER_FAILURE",
    "ONBOARDING", "ESCALATION", "CLAIM_STATUS", "HOLDER_UNAVAILABLE",
    "COMPLETION_CLAIMED", "MATERIAL_SEALED", "REJECTION",
    "RUN_CLOSED", "ASSEMBLY_PROPOSED", "ASSEMBLY_RECORD",
    "RUN_READY_FOR_COMPLETION",
    # Agent layer (Piece A1): the assembly lifecycle acts.
    "ASSEMBLY_GENERATED", "ASSEMBLY_PROBED", "ASSEMBLY_VERIFIED",
    "ASSEMBLY_JUDGED",
    "ASSEMBLY_PACKED", "ASSEMBLY_ISSUE_AUTHORISED",
    "INSTANCE_ACTIVATED",
    # Agent layer (Piece A2): the dispatch sequence.
    "TOOL_REQUESTED", "TOOL_DISPATCHED", "TOOL_STARTED",
    "TOOL_OUTCOME", "TOOL_RECONCILED",
    # Agent layer (Piece A3): the bounded loop's bookkeeping.
    "LOOP_ITERATION", "LOOP_STALLED",
    # Response-evidence piece (Rev 8): the call boundary,
    # the response disposition, and the evidence failure
    # terminal.
    "CALL_ENTERED", "RESPONSE_EVIDENCE", "EVIDENCE_CAPTURE_FAILED",
    # Native adapter piece (N32): the translation record.
    "TRANSLATION_RECORDED",
}

_ASSEMBLY_ACTS = ("ASSEMBLY_GENERATED", "ASSEMBLY_PROBED",
                  "ASSEMBLY_VERIFIED",
                  "ASSEMBLY_JUDGED", "ASSEMBLY_PACKED",
                  "ASSEMBLY_ISSUE_AUTHORISED", "INSTANCE_ACTIVATED")


class SchemaHalt(Exception):
    """The replay's classed halt: position + what could not be
    interpreted. Caught by the checker and reported as the
    `schema_invalid` replay result — never a traceback."""

    def __init__(self, seq, detail):
        super().__init__(detail)
        self.seq = seq
        self.detail = detail


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _is_str_list(v):
    return isinstance(v, list) and \
        all(isinstance(x, str) for x in v)


def _is_tree(v):
    return isinstance(v, dict) and \
        all(_is_str_list(x) for x in v.values())


def _shape_problem(ev):
    """Whether the event — envelope or payload — carries a value
    of the wrong type for a field the record contract defines, or
    lacks a shape its type's fold step requires. Covers the full
    event vocabulary (correction round 1: the classification
    contract is that a hash-valid, in-sequence event with a
    wrongly typed defined field HALTS the replay as
    schema_invalid; it does not fold into a nonconforming state).
    Returns a description, or None."""
    if not _is_int(ev.get("event_seq")):
        return "event position is not an integer"
    for key in ("event_id", "run_id", "type", "actor", "ts",
                "prev_hash", "hash"):
        if not isinstance(ev.get(key), str):
            return f"event {key} is not a string"
    if not _is_str_list(ev.get("affected")):
        return "event affected is not a list of strings"
    t = ev["type"]
    p = ev["payload"]
    if not isinstance(p, dict):
        return "payload is not an object"
    if t not in _KNOWN_TYPES:
        return f"unknown event type {t!r}"

    def need_str(key):
        return not isinstance(p.get(key), str)

    def bad_opt_str(key):
        return key in p and p[key] is not None and \
            not isinstance(p[key], str)

    def bad_opt(key, ok):
        return key in p and p[key] is not None and not ok(p[key])

    if t == "RUN_COMMISSIONED":
        seats = p.get("seats")
        if seats is not None:
            if not isinstance(seats, dict):
                return "commission seats is not an object"
            for seat_id, binding in seats.items():
                if not isinstance(binding, dict) or \
                        not isinstance(binding.get("role"), str):
                    return f"commission binding for {seat_id!r} " \
                        "lacks a role"
                if "identity_status" in binding and \
                        not isinstance(
                            binding["identity_status"], str):
                    return f"commission binding for {seat_id!r} " \
                        "has a non-string identity_status"
        if "tree" in p and not _is_tree(p["tree"]):
            return "commission tree is not a map of part lists"
        gates = p.get("gates")
        if gates is not None and not (
                isinstance(gates, dict) and all(
                    isinstance(v, str) for v in gates.values())):
            return "commission gates is not a map of kind strings"
    elif t == "SEAT_BOUND":
        if need_str("seat_id") or need_str("role"):
            return "SEAT_BOUND requires seat_id and role strings"
        if bad_opt_str("identity_status"):
            return "SEAT_BOUND identity_status is not a string"
    elif t == "ONBOARDING":
        if need_str("seat_id"):
            return "ONBOARDING requires a seat_id string"
        for key in ("identity_status", "declaration", "capability",
                    "limits", "terms_ref", "attestation_ref",
                    "provider_model_id", "subject", "instance_id",
                    "assembly_id"):
            if bad_opt_str(key):
                return f"ONBOARDING {key} is not a string"
        if bad_opt("terms_acknowledged",
                   lambda v: isinstance(v, bool)):
            return "ONBOARDING terms_acknowledged is not a boolean"
    elif t == "CONTRIBUTION":
        for key in ("contribution_id", "tree_part", "claim_id"):
            if bad_opt_str(key):
                return f"CONTRIBUTION {key} is not a string"
    elif t == "DISAGREEMENT":
        for key in ("disagreement_id", "claim_id"):
            if bad_opt_str(key):
                return f"DISAGREEMENT {key} is not a string"
    elif t == "DISAGREEMENT_SETTLED":
        if bad_opt_str("disagreement_id"):
            return "DISAGREEMENT_SETTLED disagreement_id is not " \
                "a string"
    elif t == "CLAIM_STATUS":
        if not isinstance(p.get("to"), str):
            return "CLAIM_STATUS requires a 'to' string"
        if bad_opt_str("claim_id"):
            return "CLAIM_STATUS claim_id is not a string"
    elif t in _CASE_ACTS:
        if need_str("case_id"):
            return f"{t} requires a case_id string"
        if not _is_int(p.get("version")):
            return f"{t} requires an integer version"
        if bad_opt_str("seat"):
            return f"{t} seat is not a string"
        if bad_opt("representational",
                   lambda v: isinstance(v, bool)):
            return f"{t} representational is not a boolean"
        for key in ("assignment", "part", "account"):
            if bad_opt_str(key):
                return f"{t} {key} is not a string"
        if "authority" in p and not _is_str_list(p["authority"]):
            return f"{t} authority is not a list of act types"
        if "criteria_mapping" in p and not (
                isinstance(p["criteria_mapping"], dict) and all(
                    isinstance(v, str)
                    for v in p["criteria_mapping"].values())):
            return f"{t} criteria_mapping is not a map of strings"
        if "tree" in p and not _is_tree(p["tree"]):
            return f"{t} tree is not a map of part lists"
        for key in ("evidence_boundary", "verification_list"):
            if key in p and not _is_str_list(p[key]):
                return f"{t} {key} is not a list of strings"
    elif t == "DRIVER_FAILURE":
        if need_str("seat"):
            return "DRIVER_FAILURE requires a seat string"
        for key in ("kind", "part"):
            if bad_opt_str(key):
                return f"DRIVER_FAILURE {key} is not a string"
    elif t == "MATERIAL_SEALED":
        if need_str("material_id"):
            return "MATERIAL_SEALED requires a material_id string"
        if "boundary" in p and not _is_str_list(p["boundary"]):
            return "MATERIAL_SEALED boundary is not a list of " \
                "seat ids"
    elif t in ("GATE_OUTCOME", "ESCALATION"):
        for key in ("joint", "outcome"):
            if bad_opt_str(key):
                return f"{t} {key} is not a string"
        for key in ("paused_set", "released_set"):
            if key in p and not _is_str_list(p[key]):
                return f"{t} {key} is not a list of parts"
        if "downstream" in p and not _is_tree(p["downstream"]):
            return f"{t} downstream is not a map of part lists"
    elif t == "CERTIFICATION":
        if bad_opt("closes_run", lambda v: isinstance(v, bool)):
            return "CERTIFICATION closes_run is not a boolean"
    elif t == "RULING":
        for key in ("joint", "action"):
            if bad_opt_str(key):
                return f"RULING {key} is not a string"
    elif t == "REJECTION":
        for key in ("seat", "attempted_type", "ground", "part"):
            if bad_opt_str(key):
                return f"REJECTION {key} is not a string"
    elif t == "HOLDER_UNAVAILABLE":
        if bad_opt_str("joint"):
            return "HOLDER_UNAVAILABLE joint is not a string"
    elif t == "COMPLETION_CLAIMED":
        if bad_opt_str("tree_part"):
            return "COMPLETION_CLAIMED tree_part is not a string"
    elif t == "ASSEMBLY_PROPOSED":
        crew = p.get("crew")
        if crew is not None and not (
                isinstance(crew, list) and all(
                    isinstance(c, dict)
                    and isinstance(c.get("seat"), str)
                    and isinstance(c.get("role"), str)
                    for c in crew)):
            return "ASSEMBLY_PROPOSED crew is not a list of " \
                "seat/role bindings"
        if bad_opt_str("proposal_kind"):
            return "ASSEMBLY_PROPOSED proposal_kind is not " \
                "a string"
    elif t == "ASSEMBLY_RECORD":
        if bad_opt("proposal_seq", _is_int):
            return "ASSEMBLY_RECORD proposal_seq is not an integer"
        gs = p.get("gate_set")
        if gs is not None and not (
                isinstance(gs, dict) and all(
                    isinstance(v, str) for v in gs.values())):
            return "ASSEMBLY_RECORD gate_set is not a map of " \
                "kind strings"
    elif t == "COMMENT":
        for key in ("routes_disagreement", "to_gate"):
            if bad_opt_str(key):
                return f"COMMENT {key} is not a string"
    elif t in _ASSEMBLY_ACTS:
        # Piece A1: every lifecycle act names its assembly and
        # its instance; the generated record carries the binding
        # fields its fold step reads, in their contract shapes.
        if need_str("assembly_id") or need_str("instance_id"):
            return f"{t} requires assembly_id and instance_id " \
                "strings"
        if t == "ASSEMBLY_GENERATED":
            if need_str("seat") or need_str("case_id"):
                return "ASSEMBLY_GENERATED requires seat and " \
                    "case_id strings"
            if not _is_int(p.get("case_version")):
                return "ASSEMBLY_GENERATED case_version is " \
                    "not an integer"
            for key in ("proposal_seq", "onboarding_seq"):
                if not _is_int(p.get(key)):
                    return f"ASSEMBLY_GENERATED {key} is not " \
                        "an integer"
            if bad_opt_str("part"):
                return "ASSEMBLY_GENERATED part is not a string"
            if bad_opt_str("declaration_fingerprint"):
                return "ASSEMBLY_GENERATED " \
                    "declaration_fingerprint is not a string"
            skills = p.get("skills")
            if not isinstance(skills, list) or any(
                    not isinstance(s, dict)
                    or not isinstance(s.get("name"), str)
                    or not isinstance(s.get("version"), str)
                    for s in skills):
                return "ASSEMBLY_GENERATED skills is not a " \
                    "list of name/version pins"
            if "grants" in p and p["grants"] is not None and \
                    not isinstance(p["grants"], list):
                return "ASSEMBLY_GENERATED grants is not a " \
                    "list or null"
            if bad_opt_str("catalogue_contract"):
                return "ASSEMBLY_GENERATED " \
                    "catalogue_contract is not a string"
            if bad_opt_str("probe_contract"):
                return "ASSEMBLY_GENERATED " \
                    "probe_contract is not a string"
            if "model_selection" in p and \
                    not isinstance(p["model_selection"], dict):
                return "ASSEMBLY_GENERATED model_selection " \
                    "is not an object"
        if t in ("ASSEMBLY_JUDGED", "ASSEMBLY_PACKED"):
            if bad_opt_str("record_hash"):
                return f"{t} record_hash is not a string"
        if t == "ASSEMBLY_PACKED":
            if bad_opt_str("credential_fingerprint"):
                return "ASSEMBLY_PACKED " \
                    "credential_fingerprint is not a string"
    elif t == "TOOL_REQUESTED":
        # Piece A2: a request names its instance, its stable
        # request identity, its tool and the fingerprint its
        # identity binds to; the parameters are the request's
        # own data, read by the correspondence check, not by
        # the fold — the fold requires only that they are an
        # object when present.
        for key in ("instance_id", "request_id", "tool"):
            if need_str(key):
                return f"TOOL_REQUESTED requires a {key} string"
        if bad_opt_str("fingerprint"):
            return "TOOL_REQUESTED fingerprint is not a string"
        if "parameters" in p and not isinstance(p["parameters"],
                                                dict):
            return "TOOL_REQUESTED parameters is not an object"
    elif t == "TOOL_DISPATCHED":
        for key in ("dispatch_id", "instance_id", "request_id",
                    "tool"):
            if need_str(key):
                return f"TOOL_DISPATCHED requires a {key} string"
    elif t == "TOOL_STARTED":
        if need_str("dispatch_id"):
            return "TOOL_STARTED requires a dispatch_id string"
        for key in ("instance_id", "request_id"):
            if bad_opt_str(key):
                return f"TOOL_STARTED {key} is not a string"
    elif t == "TOOL_OUTCOME":
        if need_str("dispatch_id"):
            return "TOOL_OUTCOME requires a dispatch_id string"
        if need_str("outcome"):
            return "TOOL_OUTCOME requires an outcome string"
        for key in ("instance_id", "request_id", "detail"):
            if bad_opt_str(key):
                return f"TOOL_OUTCOME {key} is not a string"
    elif t == "TOOL_RECONCILED":
        if need_str("dispatch_id"):
            return "TOOL_RECONCILED requires a dispatch_id string"
        if need_str("outcome"):
            return "TOOL_RECONCILED requires an outcome string"
        for key in ("instance_id", "request_id", "evidence_ref"):
            if bad_opt_str(key):
                return f"TOOL_RECONCILED {key} is not a string"
    elif t == "LOOP_ITERATION":
        # Piece A3: an iteration names its activation (assembly
        # and instance), its number, and the cursor range its
        # package presented; the binding and bounds fields its
        # fold step reads carry their contract shapes.
        for key in ("assembly_id", "instance_id"):
            if need_str(key):
                return f"LOOP_ITERATION requires a {key} string"
        if not _is_int(p.get("iteration")):
            return "LOOP_ITERATION iteration is not an integer"
        for key in ("cursor_from", "cursor_to"):
            if not _is_int(p.get(key)):
                return f"LOOP_ITERATION {key} is not an integer"
        for key in ("activated_seq", "case_version",
                    "step_ceiling"):
            if bad_opt(key, _is_int):
                return f"LOOP_ITERATION {key} is not an integer"
        if bad_opt_str("case_id"):
            return "LOOP_ITERATION case_id is not a string"
        if "deadline_seconds" in p and \
                p["deadline_seconds"] is not None and (
                    isinstance(p["deadline_seconds"], bool) or
                    not isinstance(p["deadline_seconds"],
                                   (int, float))):
            return "LOOP_ITERATION deadline_seconds is not a " \
                "number"
        for key in ("catalogue_hash", "registry_version"):
            if bad_opt_str(key):
                return f"LOOP_ITERATION {key} is not a string"
        if "disable_tool_validation" in p and \
                not isinstance(p["disable_tool_validation"],
                               bool):
            return "LOOP_ITERATION disable_tool_validation " \
                "is not a boolean"
    elif t == "LOOP_STALLED":
        for key in ("assembly_id", "instance_id", "ground"):
            if need_str(key):
                return f"LOOP_STALLED requires a {key} string"
        if not _is_int(p.get("iterations")):
            return "LOOP_STALLED iterations is not an integer"
        for key in ("activated_seq", "case_version"):
            if bad_opt(key, _is_int):
                return f"LOOP_STALLED {key} is not an integer"
        if bad_opt_str("case_id"):
            return "LOOP_STALLED case_id is not a string"
        if bad_opt_str("detail"):
            return "LOOP_STALLED detail is not a string"
        if bad_opt_str("terminal_step"):
            return "LOOP_STALLED terminal_step is not a string"
    elif t == "CALL_ENTERED":
        # Response-evidence piece: the call boundary names
        # its activation and the iteration event it answers.
        for key in ("assembly_id", "instance_id"):
            if need_str(key):
                return f"CALL_ENTERED requires a {key} string"
        for key in ("iteration", "iteration_seq"):
            if not _is_int(p.get(key)):
                return f"CALL_ENTERED {key} is not an integer"
        for key in ("activated_seq", "case_version"):
            if bad_opt(key, _is_int):
                return f"CALL_ENTERED {key} is not an integer"
        if bad_opt_str("case_id"):
            return "CALL_ENTERED case_id is not a string"
    elif t == "RESPONSE_EVIDENCE":
        # Response-evidence piece: the disposition names
        # its iteration and its outcome; the outcome's own
        # fields are the correspondence check's, over this
        # shape.
        for key in ("assembly_id", "instance_id", "outcome"):
            if need_str(key):
                return f"RESPONSE_EVIDENCE requires a {key} string"
        for key in ("iteration", "iteration_seq"):
            if not _is_int(p.get(key)):
                return f"RESPONSE_EVIDENCE {key} is not an integer"
        for key in ("activated_seq", "case_version"):
            if bad_opt(key, _is_int):
                return f"RESPONSE_EVIDENCE {key} is not an integer"
        for key in ("case_id", "failure_class", "artifact_sha256",
                    "provenance"):
            if bad_opt_str(key):
                return f"RESPONSE_EVIDENCE {key} is not a string"
        if bad_opt("http_status", _is_int):
            return "RESPONSE_EVIDENCE http_status is not an integer"
        for key in ("seam_evidence", "layers"):
            if key in p and p[key] is not None and \
                    not isinstance(p[key], dict):
                return f"RESPONSE_EVIDENCE {key} is not an object"
    elif t == "EVIDENCE_CAPTURE_FAILED":
        # Response-evidence piece (R8-2): the terminal
        # names its iteration and the failed operation.
        for key in ("assembly_id", "instance_id", "operation"):
            if need_str(key):
                return f"EVIDENCE_CAPTURE_FAILED requires a {key} string"
        for key in ("iteration", "iteration_seq"):
            if not _is_int(p.get(key)):
                return f"EVIDENCE_CAPTURE_FAILED {key} is not an integer"
        for key in ("activated_seq", "case_version"):
            if bad_opt(key, _is_int):
                return f"EVIDENCE_CAPTURE_FAILED {key} is not an integer"
        if bad_opt_str("case_id"):
            return "EVIDENCE_CAPTURE_FAILED case_id is not a string"
        if bad_opt_str("detail"):
            return "EVIDENCE_CAPTURE_FAILED detail is not a string"
    elif t == "TRANSLATION_RECORDED":
        # Native adapter piece (N32): the translation
        # record names its activation and iteration, the
        # artifact and catalogue it binds, and its per-call
        # decision set — a list of entry objects whose
        # fields the correspondence check verifies.
        for key in ("assembly_id", "instance_id"):
            if need_str(key):
                return f"TRANSLATION_RECORDED requires a {key} string"
        for key in ("iteration", "iteration_seq"):
            if not _is_int(p.get(key)):
                return f"TRANSLATION_RECORDED {key} is not an integer"
        for key in ("activated_seq", "case_version"):
            if bad_opt(key, _is_int):
                return f"TRANSLATION_RECORDED {key} is not an integer"
        for key in ("case_id", "artifact_sha256",
                    "catalogue_hash", "registry_version"):
            if bad_opt_str(key):
                return f"TRANSLATION_RECORDED {key} is not a string"
        calls = p.get("calls")
        if not isinstance(calls, list) or \
                any(not isinstance(c, dict) for c in calls):
            return "TRANSLATION_RECORDED calls is not a list " \
                "of entry objects"
    return None


def blank_state(run_id=None):
    return {
        "run_id": run_id,
        "lifecycle": "unopened",
        "lifecycle_seq": None,
        "seats": {},
        "onboarding": {},
        "instance_onboarding": {},
        "assemblies": {},
        "loop_activations": {},
        "tool_requests": [],
        "dispatches": {},
        "claims": {},
        "disagreements": {},
        "contributions": {},
        "cases": {},
        "gates": {},
        "certifications": [],
        "findings": [],
        "rulings": [],
        "dispositions": [],
        "escalations": [],
        "rejections": [],
        "sealed": {},
        "stalled": {},
        "tree": {},
        "paused": {},
        "gate_declaration": {},
        "gates_present": False,
        "completion_claim_seq": None,
        "holder_unavailable": [],
        "commission_seq": None,
        "assembly_proposals": [],
        "assembly_records": [],
        "run_ready_seq": None,
        "completion_claims": [],
        "routing_notes": [],
        "uncased": {},
        "pre_ack": {},
        "head_seq": 0,
    }


def _version_route_complete(ver, version):
    """Whether one case version completed its issuance route:
    verification and authorisation always; the examiner's
    sufficiency judgement — or, for a purely representational
    correction, the examiner notification — between them, in
    exact order; a version above the first stands on its
    correction, which precedes the whole route."""
    if not ver or ver.get("verified") is None or \
            ver.get("issued") is None:
        return False
    if version > 1 and not ver.get("corrected"):
        return False
    if not ver["verified"] < ver["issued"]:
        return False
    if ver.get("corrected"):
        cseq = ver.get("corrected_seq")
        if cseq is None or not cseq < ver["verified"]:
            return False
        if ver.get("representational"):
            return ver.get("notified") is not None and \
                ver["verified"] < ver["notified"] < ver["issued"]
        return ver.get("judged") is not None and \
            ver["verified"] < ver["judged"] < ver["issued"]
    return ver.get("judged") is not None and \
        ver["verified"] < ver["judged"] < ver["issued"]


def _effective_case(state, seat_id):
    """The seat's effective case at the fold's current position:
    the highest version across the seat's case lineages that
    completed its issuance route (the earliest-standing lineage
    holding a version tie), with acknowledgement counted only
    when the seat recorded it after that version's
    authorisation."""
    best = None
    for case_id, entry in state["cases"].items():
        if entry.get("seat") != seat_id:
            continue
        for vstr, ver in entry["versions"].items():
            v = int(vstr)
            if not _version_route_complete(ver, v):
                continue
            ack_seq = ver.get("acknowledged", {}).get(seat_id)
            acknowledged = ack_seq is not None and \
                ver.get("issued") is not None and \
                ack_seq > ver["issued"]
            if best is None or v > best["version"]:
                best = {
                    "case_id": case_id, "version": v,
                    "content": ver.get("content"),
                    "issued_seq": ver.get("issued"),
                    "corrected": ver.get("corrected", False),
                    "acknowledged": acknowledged,
                }
    return best


def _case_standing(state, seat_id, part):
    """(cased, acknowledged) for (seat, part) over the fold as it
    stands at the current step — the position-sensitive reading a
    contribution's provenance requires."""
    eff = _effective_case(state, seat_id)
    if eff is None or not eff.get("content"):
        return False, False
    if eff["content"].get("part") != part:
        return False, False
    return True, bool(eff["acknowledged"])


def _apply(state, ev):
    t = ev["type"]
    p = ev["payload"]
    actor = ev["actor"]
    seq = ev["event_seq"]
    state["head_seq"] = seq

    if t == "RUN_COMMISSIONED":
        state["run_id"] = ev.get("run_id", state["run_id"])
        state["lifecycle"] = "commissioned"
        state["lifecycle_seq"] = seq
        state["commission_seq"] = seq
        state["tree"] = dict(p.get("tree", {}))
        raw_gates = p.get("gates")
        state["gates_present"] = raw_gates is not None
        state["gate_declaration"] = dict(raw_gates) \
            if isinstance(raw_gates, dict) else {}
        for seat_id, binding in p.get("seats", {}).items():
            state["seats"][seat_id] = {
                "role": binding["role"],
                "identity_status": binding.get("identity_status",
                                               "unverified"),
            }
    elif t == "SEAT_BOUND":
        state["seats"][p["seat_id"]] = {
            "role": p["role"],
            "identity_status": p.get("identity_status", "unverified"),
        }
    elif t == "ONBOARDING":
        if p.get("subject") == "instance":
            # Piece A1: an instance's onboarding, keyed by
            # instance in its own state — first establishment
            # stands verbatim; a later attested act raises the
            # status only, on a strict raise.
            iid = p.get("instance_id")
            irec = state["instance_onboarding"].get(iid)
            if irec is None:
                state["instance_onboarding"][iid] = {
                    "declaration": p.get("declaration"),
                    "provider_model_id": p.get(
                        "provider_model_id"),
                    "identity_status": p.get("identity_status",
                                             "unverified"),
                    "capability": p.get("capability"),
                    "limits": p.get("limits"),
                    "terms_acknowledged": p.get(
                        "terms_acknowledged"),
                    "terms_ref": p.get("terms_ref"),
                    "onboarded_seq": seq,
                    "attestation": (
                        {"event_seq": seq,
                         "attestation_ref": p["attestation_ref"]}
                        if p.get("attestation_ref") else None),
                    "seat": p.get("seat_id"),
                    "assembly_id": p.get("assembly_id"),
                }
            elif p.get("attestation_ref"):
                new = p.get("identity_status")
                if new in _STATUS_RANK and \
                        _STATUS_RANK[new] > _STATUS_RANK.get(
                            irec["identity_status"], 0):
                    irec["identity_status"] = new
                    irec["attestation"] = {
                        "event_seq": seq,
                        "attestation_ref": p["attestation_ref"]}
            return state
        seat = p["seat_id"]
        rec = state["onboarding"].get(seat)
        if rec is None:
            state["onboarding"][seat] = {
                "declaration": p.get("declaration"),
                "provider_model_id": p.get("provider_model_id"),
                "identity_status": p.get("identity_status",
                                         "unverified"),
                "capability": p.get("capability"),
                "limits": p.get("limits"),
                "terms_acknowledged": p.get("terms_acknowledged"),
                "terms_ref": p.get("terms_ref"),
                "onboarded_seq": seq,
                "attestation": (
                    {"event_seq": seq,
                     "attestation_ref": p["attestation_ref"]}
                    if p.get("attestation_ref") else None),
            }
        elif p.get("attestation_ref"):
            # An attested restatement raises the status only, and
            # only on a strict raise; the established record and
            # the standing attestation provenance are otherwise
            # untouched.
            new = p.get("identity_status")
            if new in _STATUS_RANK and _STATUS_RANK[new] > \
                    _STATUS_RANK.get(rec["identity_status"], 0):
                rec["identity_status"] = new
                rec["attestation"] = {
                    "event_seq": seq,
                    "attestation_ref": p["attestation_ref"]}
    elif t == "CONTRIBUTION":
        cid = p.get("contribution_id", ev["event_id"])
        state["contributions"][cid] = {
            "author": actor, "tree_part": p.get("tree_part")}
        cased, acknowledged = _case_standing(
            state, actor, p.get("tree_part"))
        key = p.get("tree_part") or "(job)"
        if not cased:
            state["uncased"].setdefault(key, []).append(cid)
        elif not acknowledged:
            state["pre_ack"].setdefault(key, []).append(cid)
        if p.get("claim_id"):
            state["claims"][p["claim_id"]] = {
                "author": actor, "status": "claimed",
                "subject": cid, "status_seq": seq,
            }
    elif t == "DISAGREEMENT":
        did = p.get("disagreement_id", ev["event_id"])
        state["disagreements"][did] = {
            "status": "open", "claim_id": p.get("claim_id"),
            "by": actor, "status_seq": seq,
        }
        claim = state["claims"].get(p.get("claim_id") or "")
        if claim and claim["status"] in ("claimed", "evidenced"):
            claim["status"] = "disputed"
            claim["status_seq"] = seq
    elif t == "DISAGREEMENT_SETTLED":
        d = state["disagreements"].get(p.get("disagreement_id")
                                       or "")
        if d:
            d["status"] = "settled"
            d["status_seq"] = seq
    elif t == "CLAIM_STATUS":
        claim = state["claims"].get(p.get("claim_id") or "")
        if claim:
            claim["status"] = p["to"]
            claim["status_seq"] = seq
    elif t == "GATE_OUTCOME":
        joint = p.get("joint")
        state["gates"][joint] = {
            "outcome": p.get("outcome"), "by": actor,
            "event_seq": seq,
        }
        if p.get("outcome") == "escalate":
            for part in p.get("paused_set", []):
                state["paused"][part] = {
                    "source_seq": seq,
                    "source_joint": joint,
                    "downstream": p.get("downstream", {}).get(
                        part, []),
                }
        elif p.get("outcome") == "allow":
            for part in p.get("paused_set", []) + \
                    p.get("released_set", []):
                entry = state["paused"].get(part)
                if entry is not None and \
                        entry.get("source_joint") == joint:
                    state["paused"].pop(part, None)
    elif t == "ESCALATION":
        state["escalations"].append({
            "by": actor, "joint": p.get("joint"), "event_seq": seq})
        for part in p.get("paused_set", []):
            state["paused"][part] = {
                "source_seq": seq,
                "source_joint": p.get("joint"),
                "downstream": p.get("downstream", {}).get(part, []),
            }
    elif t in _CASE_ACTS:
        entry = state["cases"].setdefault(
            p["case_id"], {"version": 0, "seat": None,
                           "versions": {}})
        if p.get("seat"):
            entry["seat"] = p["seat"]
        ver = entry["versions"].setdefault(str(p["version"]), {
            "verified": None, "judged": None, "notified": None,
            "issued": None, "content": None, "corrected": False,
            "corrected_seq": None, "representational": False,
            "acknowledged": {},
        })
        if t == "CASE_ISSUED":
            ver["issued"] = seq
            if ver["content"] is None:
                ver["content"] = dict(p)
            entry["version"] = max(entry["version"], p["version"])
        elif t == "CASE_CORRECTED":
            # A version's correction is established once, by its
            # first correction event; a second stands in the
            # history but replaces nothing.
            if not ver["corrected"]:
                ver["corrected"] = True
                ver["corrected_seq"] = seq
                ver["representational"] = bool(
                    p.get("representational"))
                ver["content"] = dict(p)
            entry["version"] = max(entry["version"], p["version"])
        elif t == "CASE_VERIFIED":
            if ver["verified"] is None:
                ver["verified"] = seq
            if ver["content"] is None and \
                    any(f in p for f in CASE_CONTENT_FIELDS):
                ver["content"] = dict(p)
        elif t == "CASE_JUDGED":
            ver["judged"] = seq
        elif t == "CASE_NOTIFIED":
            ver["notified"] = seq
        elif t == "CASE_ACKNOWLEDGED":
            ver["acknowledged"][actor] = seq
    elif t == "DRIVER_FAILURE":
        state["stalled"][p["seat"]] = {
            "kind": p.get("kind"), "part": p.get("part"),
            "event_seq": seq,
        }
    elif t == "CERTIFICATION":
        state["certifications"].append({
            "by": actor, "coverage": p.get("coverage"),
            "event_seq": seq})
        if p.get("closes_run"):
            for d in state["disagreements"].values():
                if d["status"] == "open":
                    d["status"] = "open-at-close"
                    d["status_seq"] = seq
            state["lifecycle"] = "certified"
            state["lifecycle_seq"] = seq
    elif t == "FINDING":
        state["findings"].append({"by": actor, "event_seq": seq})
    elif t == "RULING":
        state["rulings"].append({
            "by": actor, "event_seq": seq, "joint": p.get("joint"),
            "action": p.get("action")})
    elif t == "DISPOSITION":
        state["dispositions"].append({"by": actor,
                                       "event_seq": seq})
    elif t == "MATERIAL_SEALED":
        state["sealed"][p["material_id"]] = list(
            p.get("boundary", []))
    elif t == "REJECTION":
        state["rejections"].append({
            "seat": p.get("seat"),
            "attempted": p.get("attempted_type"),
            "ground": p.get("ground"), "event_seq": seq,
            "part": p.get("part"),
        })
    elif t == "HOLDER_UNAVAILABLE":
        state["holder_unavailable"].append({
            "joint": p.get("joint"), "by": actor, "event_seq": seq})
    elif t == "COMPLETION_CLAIMED":
        state["lifecycle"] = "completion_claimed"
        state["lifecycle_seq"] = seq
        state["completion_claim_seq"] = seq
        state["completion_claims"].append({
            "event_seq": seq, "by": actor,
            "tree_part": p.get("tree_part")})
    elif t == "ASSEMBLY_PROPOSED":
        # Piece A1 correction round 1: the proposal
        # discriminator, normalised exactly as the framework
        # fold normalises it — only an explicit "instance"
        # marks an instance proposal; absence is run-level.
        state["assembly_proposals"].append({
            "event_seq": seq, "crew": p.get("crew"),
            "proposal_kind": "instance"
            if p.get("proposal_kind") == "instance" else "run"})
    elif t == "ASSEMBLY_RECORD":
        state["assembly_records"].append({
            "event_seq": seq, "proposal_seq": p.get("proposal_seq"),
            "gate_set": dict(p.get("gate_set") or {})})
    elif t == "ASSEMBLY_GENERATED":
        # Piece A1: the generated assembly opens its lifecycle
        # entry; the later acts fill their own positions,
        # first-wins.
        state["assemblies"][p.get("assembly_id")] = {
            "instance_id": p.get("instance_id"),
            "seat": p.get("seat"),
            "part": p.get("part"),
            "case_id": p.get("case_id"),
            "case_version": p.get("case_version"),
            "proposal_seq": p.get("proposal_seq"),
            "onboarding_seq": p.get("onboarding_seq"),
            "generated_seq": seq,
            "probed_seq": None,
            "verified_seq": None, "judged_seq": None,
            "judged_hash": None,
            "packed_seq": None, "pack_hash": None,
            "authorised_seq": None, "activated_seq": None,
            "credential": "none",
            "grants_present": p.get("grants") is not None,
            "catalogue_contract": p.get("catalogue_contract"),
        }
    elif t in ("ASSEMBLY_PROBED", "ASSEMBLY_VERIFIED",
               "ASSEMBLY_JUDGED",
               "ASSEMBLY_PACKED", "ASSEMBLY_ISSUE_AUTHORISED",
               "INSTANCE_ACTIVATED"):
        entry = state["assemblies"].get(p.get("assembly_id")
                                         or "")
        if entry is not None:
            if t == "ASSEMBLY_PROBED" and \
                    entry["probed_seq"] is None:
                entry["probed_seq"] = seq
            elif t == "ASSEMBLY_VERIFIED" and \
                    entry["verified_seq"] is None:
                entry["verified_seq"] = seq
            elif t == "ASSEMBLY_JUDGED" and \
                    entry["judged_seq"] is None:
                entry["judged_seq"] = seq
                entry["judged_hash"] = p.get("record_hash")
            elif t == "ASSEMBLY_PACKED" and \
                    entry["packed_seq"] is None:
                entry["packed_seq"] = seq
                entry["pack_hash"] = p.get("record_hash")
                entry["credential"] = "prepared"
            elif t == "ASSEMBLY_ISSUE_AUTHORISED" and \
                    entry["authorised_seq"] is None:
                entry["authorised_seq"] = seq
            elif t == "INSTANCE_ACTIVATED" and \
                    entry["activated_seq"] is None:
                entry["activated_seq"] = seq
                entry["credential"] = "active"
    elif t == "TOOL_REQUESTED":
        # Piece A2: first presentation binds the identity;
        # a re-presentation folds to the standing entry.
        key = (p.get("instance_id"), p.get("request_id"))
        if not any((r["instance_id"], r["request_id"]) == key
                   for r in state["tool_requests"]):
            state["tool_requests"].append({
                "instance_id": p.get("instance_id"),
                "request_id": p.get("request_id"),
                "fingerprint": p.get("fingerprint"),
                "tool": p.get("tool"),
                "requested_seq": seq,
                "dispatch_id": None,
            })
    elif t == "TOOL_DISPATCHED":
        entry = {
            "instance_id": p.get("instance_id"),
            "request_id": p.get("request_id"),
            "tool": p.get("tool"),
            "dispatch_seq": seq,
            "started_seq": None, "outcome": None,
            "outcome_seq": None, "uncertain_seq": None,
            "reconciled_seq": None, "reconciled_outcome": None,
        }
        state["dispatches"][p.get("dispatch_id")] = entry
        for req in state["tool_requests"]:
            if (req["instance_id"], req["request_id"]) == \
                    (p.get("instance_id"), p.get("request_id")) \
                    and req["dispatch_id"] is None:
                req["dispatch_id"] = p.get("dispatch_id")
    elif t == "TOOL_STARTED":
        entry = state["dispatches"].get(p.get("dispatch_id")
                                         or "")
        if entry is not None and entry["started_seq"] is None:
            entry["started_seq"] = seq
    elif t == "TOOL_OUTCOME":
        # First outcome stands; a standing `uncertain` is
        # settled by a later attributable result/failure (the
        # delayed report), the uncertainty's position kept.
        entry = state["dispatches"].get(p.get("dispatch_id")
                                         or "")
        if entry is not None:
            outcome = p.get("outcome")
            if entry["outcome"] is None:
                entry["outcome"] = outcome
                entry["outcome_seq"] = seq
                if outcome == "uncertain":
                    entry["uncertain_seq"] = seq
            elif entry["outcome"] == "uncertain" and \
                    entry["reconciled_seq"] is None and \
                    outcome in ("result", "failure"):
                entry["outcome"] = outcome
                entry["outcome_seq"] = seq
    elif t == "TOOL_RECONCILED":
        entry = state["dispatches"].get(p.get("dispatch_id")
                                         or "")
        if entry is not None and \
                entry["outcome"] == "uncertain" and \
                entry["reconciled_seq"] is None:
            entry["reconciled_seq"] = seq
            entry["reconciled_outcome"] = p.get("outcome")
    elif t == "LOOP_ITERATION":
        # Piece A3: the loop's bookkeeping, collected per
        # activation in record order — the same derivation the
        # record's fold performs.
        entry = state["loop_activations"].setdefault(
            p.get("assembly_id"), {
                "instance_id": p.get("instance_id"),
                "activated_seq": p.get("activated_seq"),
                "case_id": p.get("case_id"),
                "case_version": p.get("case_version"),
                "iterations": [], "stalled": None,
                "evidence_failed": None})
        entry["iterations"].append({
            "iteration": p.get("iteration"),
            "event_seq": seq,
            "step_ceiling": p.get("step_ceiling"),
            "deadline_seconds": p.get("deadline_seconds"),
            "cursor_from": p.get("cursor_from"),
            "cursor_to": p.get("cursor_to"),
            "catalogue_hash": p.get("catalogue_hash"),
            "registry_version": p.get("registry_version"),
            "call_entered_seq": None,
            "disposition_seq": None,
            "disposition_outcome": None,
            "translation_seq": None,
        })
    elif t == "CALL_ENTERED":
        # Response-evidence piece: the call boundary marks
        # the iteration entry it names; the first stands.
        entry = state["loop_activations"].get(
            p.get("assembly_id"))
        if entry is not None:
            for it in entry["iterations"]:
                if it["event_seq"] == p.get("iteration_seq"):
                    if it["call_entered_seq"] is None:
                        it["call_entered_seq"] = seq
                    break
    elif t == "RESPONSE_EVIDENCE":
        # Response-evidence piece: the first disposition
        # stands; a second replaces nothing.
        entry = state["loop_activations"].get(
            p.get("assembly_id"))
        if entry is not None:
            for it in entry["iterations"]:
                if it["event_seq"] == p.get("iteration_seq"):
                    if it["disposition_seq"] is None:
                        it["disposition_seq"] = seq
                        it["disposition_outcome"] = \
                            p.get("outcome")
                    break
    elif t == "TRANSLATION_RECORDED":
        # Native adapter piece (N32): the first translation
        # record stands on its iteration; a second replaces
        # nothing.
        entry = state["loop_activations"].get(
            p.get("assembly_id"))
        if entry is not None:
            for it in entry["iterations"]:
                if it["event_seq"] == p.get("iteration_seq"):
                    if it["translation_seq"] is None:
                        it["translation_seq"] = seq
                    break
    elif t == "EVIDENCE_CAPTURE_FAILED":
        # Response-evidence piece (R8-2): the first
        # evidence failure terminal stands; it discharges
        # no disposition obligation.
        entry = state["loop_activations"].setdefault(
            p.get("assembly_id"), {
                "instance_id": p.get("instance_id"),
                "activated_seq": p.get("activated_seq"),
                "case_id": p.get("case_id"),
                "case_version": p.get("case_version"),
                "iterations": [], "stalled": None,
                "evidence_failed": None})
        if entry["evidence_failed"] is None:
            entry["evidence_failed"] = {
                "event_seq": seq,
                "iteration_seq": p.get("iteration_seq"),
                "operation": p.get("operation"),
            }
    elif t == "LOOP_STALLED":
        # Piece A3: the first stall stands; a second is
        # history and replaces nothing.
        entry = state["loop_activations"].setdefault(
            p.get("assembly_id"), {
                "instance_id": p.get("instance_id"),
                "activated_seq": p.get("activated_seq"),
                "case_id": p.get("case_id"),
                "case_version": p.get("case_version"),
                "iterations": [], "stalled": None,
                "evidence_failed": None})
        if entry["stalled"] is None:
            entry["stalled"] = {
                "ground": p.get("ground"),
                "event_seq": seq,
                "iterations": p.get("iterations"),
                "terminal_step": p.get("terminal_step"),
            }
    elif t == "RUN_READY_FOR_COMPLETION":
        state["run_ready_seq"] = seq
    elif t == "COMMENT":
        if p.get("routes_disagreement") and p.get("to_gate"):
            state["routing_notes"].append({
                "disagreement_id": p.get("routes_disagreement"),
                "joint": p.get("to_gate"), "event_seq": seq,
                "by": actor})
    elif t == "RUN_CLOSED":
        state["lifecycle"] = "closed"
        state["lifecycle_seq"] = seq
    return state


def replay_events(events, run_id=None, classifiable=None):
    """Replay the stream. Returns (state, halt): the reconstructed
    state (None when the replay halted) and the halt as
    (kind, seq, detail, position) or None. Each event is shape-checked
    before it is applied, and the application itself is guarded
    — a defect the table did not foresee still lands as a classed
    halt, not an exception.

    The halt's kind honours C6's preconditions (round 3): a halt
    is "schema_invalid" only at a position the caller has
    established as hash-valid and in sequence (`classifiable`,
    the set of such PHYSICAL positions from the checker's chain
    examination — positions, not claimed sequence numbers,
    round 4); at any other position the halt is
    "not_classified" — the chain results carry that defect, and
    the replay does not borrow their classification. The halt
    reports both the event's claimed event_seq and its physical
    position."""
    state = blank_state(run_id)
    for pos, ev in enumerate(events, start=1):
        seq = ev.get("event_seq")
        kind = "schema_invalid"
        if classifiable is not None and pos not in classifiable:
            kind = "not_classified"
        problem = _shape_problem(ev)
        if problem is not None:
            return None, (kind, seq, problem, pos)
        try:
            _apply(state, ev)
        except SchemaHalt:
            raise
        except Exception as exc:  # classed, never a traceback
            return None, (kind, seq,
                          f"event cannot be applied "
                          f"({type(exc).__name__})", pos)
    return state, None
