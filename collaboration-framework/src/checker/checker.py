"""The independent checker — Piece 7 (SPEC SHEET §3.10: R4, R28).

A separate process. One JSON request on stdin —
{store_path, run_id, snapshot} — and one JSON verdict on stdout,
exit 0 for every well-formed verdict. The verdict reports
per-check results only: `ok`, or the divergence named. It
contains no run-level pass/fail — no automated pass stands in
for a gate (R28).

What it checks, from the record alone:

- run binding: the store holds exactly the requested run, and
  every event carries it;
- chain integrity and sequence structure, as two INDEPENDENT
  per-property results with no precedence (scope Rev 4, C6):
  hash validity (a stored hash that does not recompute, or
  contents that cannot be canonically hashed at all) and
  sequence validity (positions contiguous from the first event,
  linkage by prev_hash) can each fail, together or alone;
- replay: its own reconstruction of the complete record fold
  (`checker.replay`), which can halt with a classed
  `schema_invalid` at a named position;
- projection schema coverage: its reconstruction, and the
  supplied snapshot, each conform recursively to the checker's
  copy of the projection schema;
- replay equality: its reconstruction against the supplied
  snapshot — an untrusted comparison operand, never authority,
  never an input to the replay (C4) — with every divergence
  reported by key path;
- seal correspondence, bidirectionally (C5);
- assembly correspondence (Piece A1) and dispatch
  correspondence (Piece A2): each generated instance's
  lifecycle, and each recorded dispatch against the authority
  that actually stood, reconstructed from the events — the
  dispatch check applying the checker's own copy of the pure
  tool-policy contract and executing nothing (R48).

It opens the store read-only with its own SQL, writes nothing,
creates no store, and leaves no artifacts (C7). It imports
`fabric.canonical` — the record-format and hashing primitive —
and the standard library only; never a `framework.*` module.
"""
import hashlib
import json
import os
import sqlite3
import sys

from fabric.canonical import canonical, event_hash, sha256_hex

from checker.replay import replay_events
from checker.schema import SCHEMA
from checker.tool_policy import (REGISTRY_VERSION, check_ceiling,
                                 request_fingerprint)

_ENVELOPE = ("event_seq", "event_id", "run_id", "type", "actor",
             "affected", "payload", "ts", "prev_hash", "hash")


# ------------------------------------------------------------ store

def _read_store(path, run_id):
    """Read the store read-only. Returns (runs, events, problem):
    the runs rows, the event dicts in stored order (each carrying
    a `_read_error` instead of parsed fields when its row could
    not be reconstructed), and a store-level problem or None.

    The store is opened read-only and immutable: a plain
    read-only open of a WAL-mode database creates -shm/-wal
    sidecars, and the checker leaves no artifacts (C7). Immutable
    reading is exact only on a quiescent store, so a store
    carrying uncheckpointed WAL data is refused by name rather
    than read stale."""
    if not os.path.exists(path):
        return None, None, "store_missing"
    wal = path + "-wal"
    if os.path.exists(wal) and os.path.getsize(wal) > 0:
        return None, None, "store_not_quiescent"
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro&immutable=1",
                               uri=True)
        try:
            runs = conn.execute(
                "SELECT run_id, constitution_hash, status FROM runs"
            ).fetchall()
            rows = conn.execute(
                "SELECT event_seq, event_id, run_id, type, actor,"
                " affected, payload, ts, prev_hash, hash FROM events"
                " ORDER BY rowid"
            ).fetchall()
        finally:
            conn.close()
    except sqlite3.Error:
        return None, None, "store_unreadable"
    events = []
    for row in rows:
        (seq, eid, erun, typ, actor, affected, payload, ts, prev,
         h) = row
        ev = {"event_seq": seq, "event_id": eid, "run_id": erun,
              "type": typ, "actor": actor, "ts": ts,
              "prev_hash": prev, "hash": h}
        try:
            ev["affected"] = json.loads(affected)
            ev["payload"] = json.loads(payload)
        except (ValueError, TypeError):
            ev["_read_error"] = "stored affected/payload is not " \
                                "valid JSON"
        events.append(ev)
    return runs, events, None


# ------------------------------------------------------------ chain

def _chain_positions(events):
    """Per-position chain standing: a list, in stored order, of
    (hash_ok, seq_ok, hash_detail) — one entry per PHYSICAL
    event. Standing is keyed by the event's actual position,
    never by its claimed event_seq: a sequence number is
    evidence about where an event claims to stand, not the
    identity of the position at which the claim is examined,
    and a malformed stream may carry the same event_seq on two
    physical events (round 4). Each event's hash validity and
    sequence standing are computed on their own terms, neither
    derived from the other (C6). Together they establish the
    positions at which a replay halt may be classified
    schema_invalid: Rev 4 reserves that classification for an
    event that is canonically hashable, whose stored hash
    verifies, and which stands in sequence (round 3)."""
    positions = []
    prev_hash = ""
    for expected, ev in enumerate(events, start=1):
        seq = ev.get("event_seq")
        if "_read_error" in ev:
            hash_ok, hash_detail = False, \
                "event contents cannot be read, so their hash " \
                "cannot be recomputed"
        else:
            body = {k: ev[k] for k in _ENVELOPE if k != "hash"}
            try:
                hash_ok = event_hash(
                    ev["prev_hash"], body) == ev["hash"]
                hash_detail = None if hash_ok else \
                    "stored hash does not equal the hash " \
                    "recomputed from the event's contents"
            except Exception:
                hash_ok, hash_detail = False, \
                    "event contents cannot be canonically " \
                    "serialized and hashed"
        seq_ok = seq == expected and ev.get("prev_hash") == prev_hash
        positions.append((hash_ok, seq_ok, hash_detail))
        prev_hash = ev.get("hash")
    return positions


def _hash_result(events, positions=None):
    """Hash integrity, independently of sequence: each event's
    stored hash against the hash recomputed from its contents.
    Contents that cannot be canonically hashed at all fail here —
    hash validity cannot be established for them (C6)."""
    if positions is None:
        positions = _chain_positions(events)
    for pos, ev in enumerate(events, start=1):
        hash_ok, _, detail = positions[pos - 1]
        if not hash_ok:
            return {"result": "hash_chain_invalid",
                    "at_seq": ev.get("event_seq"),
                    "at_position": pos, "detail": detail}
    return {"result": "ok"}


def _sequence_result(events, positions=None):
    """Sequence structure, independently of hash validity:
    positions contiguous from the first event (which stands at
    position 1), no gaps or duplicates in stored order, and each
    event's prev_hash naming the preceding event's hash. The
    first offending event is identified by its physical
    position; its claimed event_seq is reported alongside."""
    if positions is None:
        positions = _chain_positions(events)
    for expected, ev in enumerate(events, start=1):
        seq = ev.get("event_seq")
        _, seq_ok, _ = positions[expected - 1]
        if not seq_ok:
            if seq != expected:
                return {"result": "sequence_invalid",
                        "at_seq": seq, "at_position": expected,
                        "detail": f"expected position {expected}, "
                                  f"found {seq}"}
            return {"result": "sequence_invalid", "at_seq": seq,
                    "at_position": expected,
                    "detail": "prev_hash does not name the "
                              "preceding event's hash"}
    return {"result": "ok"}


# ------------------------------------------------------- projection

def _conforms(value, node, path=""):
    """This implementation's recursive conformance walk over the
    projection schema. Returns the departing paths."""
    t = node["t"]
    if t == "any":
        return []
    if t == "opt":
        if value is None:
            return []
        return _conforms(value, node["v"], path)
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
            out += _conforms(item, node["v"], f"{path}[{i}]")
        return out
    if t == "map":
        if not isinstance(value, dict):
            return [path]
        out = []
        for k, v in value.items():
            out += _conforms(v, node["v"],
                             f"{path}.{k}" if path else k)
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
                out += _conforms(value[k], fields[k], p)
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
                out += _conforms(v, fields[k], p)
        return out
    return [path]


def _divergences(mine, supplied, path=""):
    """Every key path at which the supplied projection departs
    from this checker's reconstruction. Values are compared by
    canonical form, so the comparison is over JSON data, not
    object identity or key order."""
    if isinstance(mine, dict) and isinstance(supplied, dict):
        out = []
        for k in sorted(set(mine) | set(supplied)):
            p = f"{path}.{k}" if path else k
            if k not in mine or k not in supplied:
                out.append(p)
            else:
                out += _divergences(mine[k], supplied[k], p)
        return out
    if isinstance(mine, list) and isinstance(supplied, list):
        if len(mine) != len(supplied):
            return [path]
        out = []
        for i, (a, b) in enumerate(zip(mine, supplied)):
            out += _divergences(a, b, f"{path}[{i}]")
        return out
    if canonical(mine) != canonical(supplied):
        return [path]
    return []


# ------------------------------------------------------------ seals

def _seal_result(events, state):
    """Bidirectional seal correspondence (C5): every
    MATERIAL_SEALED event corresponds to exactly one registry
    entry with the same material and boundary; every registry
    entry traces to exactly one sealing event; no other event
    type carries a material reference. Duplicates and orphans
    are reported by material and position, never resolved
    silently."""
    problems = []
    sealing = {}
    for ev in events:
        p = ev.get("payload")
        if not isinstance(p, dict):
            continue
        if ev["type"] == "MATERIAL_SEALED":
            sealing.setdefault(p.get("material_id"), []).append(ev)
        elif "material_id" in p:
            problems.append({
                "kind": "material_reference_on_other_type",
                "type": ev["type"], "at_seq": ev["event_seq"],
                "material_id": p.get("material_id")})
    registry = state["sealed"]
    for material, evs in sealing.items():
        if len(evs) > 1:
            problems.append({
                "kind": "duplicate_sealing_events",
                "material_id": material,
                "at_seqs": [e["event_seq"] for e in evs]})
        if material not in registry:
            problems.append({
                "kind": "sealed_event_without_registry_entry",
                "material_id": material,
                "at_seq": evs[0]["event_seq"]})
        elif registry[material] != list(
                evs[-1]["payload"].get("boundary", [])):
            problems.append({
                "kind": "boundary_mismatch",
                "material_id": material,
                "at_seq": evs[-1]["event_seq"]})
    for material in registry:
        if material not in sealing:
            problems.append({
                "kind": "registry_entry_without_sealing_event",
                "material_id": material})
    if problems:
        return {"result": "divergent", "problems": problems}
    return {"result": "ok"}


# ---------------------------------------------------------- assembly

# The assembly record's fields, as this checker derives them
# from the record contract (SPEC Rev 6, R37): the generated
# record's canonical hash is recomputed over exactly these
# fields under the version tag, independently of the framework.
_ASSEMBLY_RECORD_FIELDS = (
    "assembly_id", "instance_id", "seat", "part", "case_id",
    "case_version", "proposal_seq", "onboarding_seq",
    "declaration_fingerprint", "model_selection", "skills",
    "grants")

_ASSEMBLY_STAGES = ("ASSEMBLY_VERIFIED", "ASSEMBLY_JUDGED",
                    "ASSEMBLY_PACKED", "ASSEMBLY_ISSUE_AUTHORISED",
                    "INSTANCE_ACTIVATED")


def _assembly_record_hash(payload):
    body = {k: payload.get(k) for k in _ASSEMBLY_RECORD_FIELDS}
    return sha256_hex(canonical(
        {"assembly_record_v": 1, "record": body}))


def _assembly_result(events, state):
    """Assembly correspondence (Piece A1, R37–R40/R55): every
    generated instance's lifecycle, verified from the events
    themselves — attribution by the actor's recorded role; the
    normative order, each act answering its predecessor; the
    one-to-one rule (one instance identity, one immutable
    generated assembly, one onboarding reference, one judgement
    target, one pack seal); the judged and sealed object being
    the generated object, by canonical hash; the generation
    answering an instance proposal, never a run-level one (the
    shared event kind's discriminator, correction round 1);
    the record's seat slot and part equalling its exact
    proposal's, and its part equalling its bound case's
    established part (correction round 2); and no activation
    without the full chain and the record's grants section.
    An incomplete or incorrectly ordered assembly history is
    reported, never read as valid."""
    problems = []

    def problem(kind, **fields):
        entry = {"kind": kind}
        entry.update(fields)
        problems.append(entry)

    by_seq = {ev["event_seq"]: ev for ev in events}
    seats = state["seats"]

    def role_of(actor):
        return (seats.get(actor) or {}).get("role")

    onboardings = {}
    generated = {}
    stages = {}
    for ev in events:
        t = ev["type"]
        p = ev["payload"]
        if t == "ASSEMBLY_PROPOSED":
            if role_of(ev["actor"]) != "orchestrator":
                problem("assembly_act_wrong_role", type=t,
                        at_seq=ev["event_seq"], actor=ev["actor"])
        elif t == "ONBOARDING" and p.get("subject") == "instance":
            onboardings.setdefault(
                p.get("instance_id"), []).append(ev)
        elif t == "ASSEMBLY_GENERATED":
            aid = p.get("assembly_id")
            if aid in generated:
                problem("duplicate_generated_assembly",
                        assembly_id=aid, at_seq=ev["event_seq"])
            generated.setdefault(aid, ev)
        elif t in _ASSEMBLY_STAGES:
            stages.setdefault(p.get("assembly_id"), {}) \
                .setdefault(t, []).append(ev)

    # One establishing onboarding per instance; any later
    # instance onboarding is an attestation, carrying its
    # reference.
    for iid, evs in onboardings.items():
        for extra in evs[1:]:
            if not extra["payload"].get("attestation_ref"):
                problem("second_instance_onboarding",
                        instance_id=iid,
                        at_seq=extra["event_seq"])

    seen_instances = {}
    seen_onboardings = {}
    for aid, ev in generated.items():
        p = ev["payload"]
        iid = p.get("instance_id")
        if role_of(ev["actor"]) != "orchestrator":
            problem("assembly_act_wrong_role",
                    type="ASSEMBLY_GENERATED",
                    at_seq=ev["event_seq"], actor=ev["actor"])
        if iid in seen_instances:
            problem("instance_in_two_assemblies",
                    instance_id=iid, assembly_id=aid,
                    at_seq=ev["event_seq"])
        seen_instances[iid] = aid
        oseq = p.get("onboarding_seq")
        if oseq in seen_onboardings:
            problem("onboarding_bound_twice",
                    onboarding_seq=oseq, assembly_id=aid,
                    at_seq=ev["event_seq"])
        seen_onboardings[oseq] = aid
        # The proposal the generation answers.
        prop = by_seq.get(p.get("proposal_seq"))
        if prop is None or prop["type"] != "ASSEMBLY_PROPOSED" \
                or prop["event_seq"] >= ev["event_seq"]:
            problem("generated_without_proposal",
                    assembly_id=aid, at_seq=ev["event_seq"])
            prop = None
        elif prop["payload"].get("seat") not in (None,
                                                 p.get("seat")):
            problem("generated_answers_other_slot",
                    assembly_id=aid, at_seq=ev["event_seq"])
        if prop is not None and \
                prop["payload"].get("proposal_kind") != \
                "instance":
            problem("generated_answers_run_proposal",
                    assembly_id=aid, at_seq=ev["event_seq"])
        # The exact proposal, verified in full (correction
        # round 2): the record's seat slot and part must equal
        # its proposal's — reconstructed here from the events,
        # never trusted to the doorway's refusal at offer time,
        # which a directly appended history bypasses.
        if prop is not None:
            if prop["payload"].get("seat") != p.get("seat"):
                problem("generated_seat_differs_from_proposal",
                        assembly_id=aid, at_seq=ev["event_seq"])
            if prop["payload"].get("part") != p.get("part"):
                problem("generated_part_differs_from_proposal",
                        assembly_id=aid, at_seq=ev["event_seq"])
        # The bound case's established content, from this
        # checker's own replayed state: the record's part must
        # be its case's part.
        case = (state.get("cases") or {}).get(p.get("case_id"))
        ver = ((case or {}).get("versions") or {}).get(
            str(p.get("case_version"))) or {}
        content = ver.get("content")
        if content is None:
            problem("generated_case_not_established",
                    assembly_id=aid, at_seq=ev["event_seq"])
        elif content.get("part") != p.get("part"):
            problem("generated_part_differs_from_case",
                    assembly_id=aid, at_seq=ev["event_seq"])
        # The exact onboarding it binds to: an instance
        # onboarding, for this instance and assembly, after the
        # proposal and before the generation.
        bound = by_seq.get(oseq)
        if bound is None or bound["type"] != "ONBOARDING" or \
                bound["payload"].get("subject") != "instance":
            problem("generated_onboarding_binding_broken",
                    assembly_id=aid, at_seq=ev["event_seq"])
            bound = None
        if bound is not None:
            ob = bound["payload"]
            if ob.get("instance_id") != iid or \
                    ob.get("assembly_id") != aid:
                problem("generated_binds_other_instance",
                        assembly_id=aid, at_seq=ev["event_seq"])
            if prop is not None and \
                    bound["event_seq"] <= prop["event_seq"]:
                problem("onboarding_before_proposal",
                        assembly_id=aid, at_seq=ev["event_seq"])
            fingerprint = hashlib.sha256(
                f"{iid}\x00{ob.get('declaration')}"
                .encode()).hexdigest()
            if p.get("declaration_fingerprint") != fingerprint:
                problem("declaration_fingerprint_mismatch",
                        assembly_id=aid, at_seq=ev["event_seq"])
        digest = _assembly_record_hash(p)
        # The stages: at most one each, in the normative order,
        # each after its predecessor; a later stage standing
        # without an earlier one is an incomplete history.
        mine = stages.get(aid, {})
        last = ev["event_seq"]
        for i, kind in enumerate(_ASSEMBLY_STAGES):
            evs = mine.get(kind, [])
            if len(evs) > 1:
                problem("duplicate_assembly_act", type=kind,
                        assembly_id=aid,
                        at_seq=evs[1]["event_seq"])
            if not evs:
                later = [k for k in _ASSEMBLY_STAGES[i + 1:]
                         if mine.get(k)]
                if later:
                    problem("assembly_stage_missing", type=kind,
                            assembly_id=aid,
                            later_stage=later[0],
                            at_seq=mine[later[0]][0]["event_seq"])
                continue
            stage_ev = evs[0]
            if stage_ev["event_seq"] <= last:
                problem("assembly_act_out_of_order", type=kind,
                        assembly_id=aid,
                        at_seq=stage_ev["event_seq"])
            last = max(last, stage_ev["event_seq"])
            want = "examiner" if kind == "ASSEMBLY_JUDGED" \
                else "orchestrator"
            if role_of(stage_ev["actor"]) != want:
                problem("assembly_act_wrong_role", type=kind,
                        assembly_id=aid,
                        at_seq=stage_ev["event_seq"],
                        actor=stage_ev["actor"])
            if kind in ("ASSEMBLY_JUDGED", "ASSEMBLY_PACKED") and \
                    stage_ev["payload"].get("record_hash") != \
                    digest:
                problem("assembly_hash_mismatch", type=kind,
                        assembly_id=aid,
                        at_seq=stage_ev["event_seq"])
            if kind == "INSTANCE_ACTIVATED" and \
                    p.get("grants") is None:
                problem("activated_without_grants",
                        assembly_id=aid,
                        at_seq=stage_ev["event_seq"])
    for aid, mine in stages.items():
        if aid not in generated:
            for kind, evs in mine.items():
                problem("assembly_act_without_generation",
                        type=kind, assembly_id=aid,
                        at_seq=evs[0]["event_seq"])
    if problems:
        return {"result": "divergent", "problems": problems}
    return {"result": "ok"}


# ---------------------------------------------------------- dispatch

_OUTCOME_VOCAB = ("result", "failure", "uncertain")


def _dispatch_result(events, state):
    """Dispatch correspondence (Piece A2, R44–R48/R55): every
    recorded dispatch reconstructed against the authority that
    actually stood — not merely that dispatch events exist.
    From the events themselves: the instance held an active
    credential at request time (its assembly's activation
    stands before the request); the grant stood in the judged
    and packed assembly object (the generated record, named
    by both acts under its canonical hash); the request's tool
    and parameters satisfied the grant and the registered
    ceiling, applying the checker's own copy of the pure
    policy contract; the authority trace stood in that sealed
    object; the bound was respected counting dispatches,
    uncertain included, never refunded; no request identity
    was reused with different contents; every dispatch, start
    and outcome carries the correct actor and referent (the
    doorway's intent, the executor's starts and outcomes,
    at most one start per dispatch, an outcome following its
    dispatch and any standing start, an uncertain dispatch
    needing no start); every dispatch records the registry
    version that governed it, and it is the version this
    checker holds — a dispatch governed by another version is
    not verifiable under this contract; a dispatch's tool is
    its request's tool, and a start's or outcome's instance
    and request identity are its dispatch's established
    identity; and reconciliation applies only to an
    uncertain dispatch, examiner-authorised and
    evidence-referenced. Nothing here executes a tool (R48):
    the policy contract is pure, and this module imports no
    executor."""
    problems = []

    def problem(kind, **fields):
        entry = {"kind": kind}
        entry.update(fields)
        problems.append(entry)

    seats = state["seats"]

    def role_of(actor):
        return (seats.get(actor) or {}).get("role")

    generated_by_instance = {}
    judged_hashes = {}
    packed_hashes = {}
    activated_seq = {}
    for ev in events:
        t = ev["type"]
        p = ev["payload"]
        if t == "ASSEMBLY_GENERATED":
            generated_by_instance.setdefault(
                p.get("instance_id"), ev)
        elif t == "ASSEMBLY_JUDGED":
            judged_hashes.setdefault(
                p.get("assembly_id"), []).append(
                    p.get("record_hash"))
        elif t == "ASSEMBLY_PACKED":
            packed_hashes.setdefault(
                p.get("assembly_id"), []).append(
                    p.get("record_hash"))
        elif t == "INSTANCE_ACTIVATED":
            activated_seq.setdefault(p.get("instance_id"),
                                     ev["event_seq"])

    def sealed_grants(instance_id):
        """(grants, sealed): the generated record's grants,
        and whether the judgement and the pack both name that
        exact object by its canonical hash — a grant in an
        unsealed object is not a grant that stood."""
        ev = generated_by_instance.get(instance_id)
        if ev is None:
            return None, False
        digest = _assembly_record_hash(ev["payload"])
        aid = ev["payload"].get("assembly_id")
        sealed = digest in judged_hashes.get(aid, []) and \
            digest in packed_hashes.get(aid, [])
        return ev["payload"].get("grants"), sealed

    requests = {}
    dispatches = {}
    counts = {}
    for ev in events:
        t = ev["type"]
        p = ev["payload"]
        seq = ev["event_seq"]
        actor = ev["actor"]
        if t == "TOOL_REQUESTED":
            iid = p.get("instance_id")
            rid = p.get("request_id")
            gen = generated_by_instance.get(iid)
            if gen is None:
                problem("request_unknown_instance",
                        instance_id=iid, at_seq=seq)
            else:
                if actor != gen["payload"].get("seat"):
                    problem("request_wrong_actor",
                            instance_id=iid, at_seq=seq,
                            actor=actor)
                active_at = activated_seq.get(iid)
                if active_at is None or active_at > seq:
                    problem("request_credential_not_active",
                            instance_id=iid, at_seq=seq)
            if p.get("fingerprint") != request_fingerprint(
                    p.get("tool"), p.get("parameters")):
                problem("request_fingerprint_mismatch",
                        instance_id=iid, request_id=rid,
                        at_seq=seq)
            key = (iid, rid)
            if key in requests:
                if requests[key]["fingerprint"] != \
                        p.get("fingerprint"):
                    problem("request_identity_reused",
                            instance_id=iid, request_id=rid,
                            at_seq=seq)
            else:
                requests[key] = {
                    "fingerprint": p.get("fingerprint"),
                    "tool": p.get("tool"),
                    "parameters": p.get("parameters"),
                    "seq": seq}
        elif t == "TOOL_DISPATCHED":
            did = p.get("dispatch_id")
            iid = p.get("instance_id")
            rid = p.get("request_id")
            if actor != "doorway":
                problem("dispatch_wrong_actor",
                        dispatch_id=did, at_seq=seq, actor=actor)
            req = requests.get((iid, rid))
            if req is None or req["seq"] > seq:
                problem("dispatch_without_request",
                        dispatch_id=did, at_seq=seq)
            if req is not None and \
                    req["tool"] != p.get("tool"):
                problem("dispatch_tool_differs_from_request",
                        dispatch_id=did, at_seq=seq,
                        tool=p.get("tool"),
                        request_tool=req["tool"])
            if p.get("registry_version") != REGISTRY_VERSION:
                problem("dispatch_registry_version_mismatch",
                        dispatch_id=did, at_seq=seq,
                        registry_version=p.get(
                            "registry_version"),
                        checker_registry_version=REGISTRY_VERSION)
            if any(d["instance_id"] == iid
                   and d["request_id"] == rid
                   for d in dispatches.values()):
                problem("second_dispatch_for_request",
                        dispatch_id=did, at_seq=seq)
            if did in dispatches:
                problem("duplicate_dispatch_id",
                        dispatch_id=did, at_seq=seq)
            grants, sealed = sealed_grants(iid)
            if grants is None:
                problem("dispatch_without_sealed_assembly",
                        dispatch_id=did, at_seq=seq)
            else:
                if not sealed:
                    problem("grant_not_sealed",
                            dispatch_id=did, at_seq=seq)
                grant = next(
                    (g for g in grants
                     if isinstance(g, dict)
                     and g.get("tool") == p.get("tool")), None)
                if grant is None:
                    problem("dispatch_without_grant",
                            dispatch_id=did, at_seq=seq,
                            tool=p.get("tool"))
                else:
                    trace = grant.get("authority_trace")
                    if not isinstance(trace, str) or not trace:
                        problem("grant_without_authority_trace",
                                dispatch_id=did, at_seq=seq)
                    if req is not None:
                        ok, ground = check_ceiling(
                            p.get("tool"),
                            grant.get("scope_ceiling"),
                            req["parameters"])
                        if not ok:
                            problem("dispatch_exceeds_ceiling",
                                    dispatch_id=did, at_seq=seq,
                                    detail=ground)
                    bound = grant.get("bound")
                    limit = bound.get("count") if isinstance(
                        bound, dict) else None
                    ckey = (iid, p.get("tool"))
                    counts[ckey] = counts.get(ckey, 0) + 1
                    if not isinstance(limit, int) or \
                            isinstance(limit, bool):
                        problem("grant_bound_not_a_count",
                                dispatch_id=did, at_seq=seq)
                    elif counts[ckey] > limit:
                        problem("dispatch_over_bound",
                                dispatch_id=did, at_seq=seq)
            dispatches[did] = {
                "instance_id": iid, "request_id": rid,
                "seq": seq, "started_seq": None, "outcome": None,
                "reconciled": False}
        elif t == "TOOL_STARTED":
            did = p.get("dispatch_id")
            if actor != "executor":
                problem("start_wrong_actor", dispatch_id=did,
                        at_seq=seq, actor=actor)
            d = dispatches.get(did)
            if d is None or d["seq"] > seq:
                problem("start_without_dispatch",
                        dispatch_id=did, at_seq=seq)
            else:
                if p.get("instance_id") != d["instance_id"] or \
                        p.get("request_id") != d["request_id"]:
                    problem("start_referent_mismatch",
                            dispatch_id=did, at_seq=seq)
                if d["started_seq"] is not None:
                    problem("second_start", dispatch_id=did,
                            at_seq=seq)
                elif d["outcome"] is not None or d["reconciled"]:
                    problem("start_after_outcome",
                            dispatch_id=did, at_seq=seq)
                else:
                    d["started_seq"] = seq
        elif t == "TOOL_OUTCOME":
            did = p.get("dispatch_id")
            if actor != "executor":
                problem("outcome_wrong_actor", dispatch_id=did,
                        at_seq=seq, actor=actor)
            if p.get("outcome") not in _OUTCOME_VOCAB:
                problem("outcome_value_unknown",
                        dispatch_id=did, at_seq=seq,
                        outcome=p.get("outcome"))
            d = dispatches.get(did)
            if d is not None and d["seq"] <= seq and \
                    (p.get("instance_id") != d["instance_id"] or
                     p.get("request_id") != d["request_id"]):
                problem("outcome_referent_mismatch",
                        dispatch_id=did, at_seq=seq)
            if d is None or d["seq"] > seq:
                problem("outcome_without_dispatch",
                        dispatch_id=did, at_seq=seq)
            elif d["reconciled"]:
                problem("outcome_after_reconciliation",
                        dispatch_id=did, at_seq=seq)
            elif d["outcome"] in ("result", "failure"):
                problem("duplicate_outcome", dispatch_id=did,
                        at_seq=seq)
            elif d["outcome"] == "uncertain" and \
                    p.get("outcome") == "uncertain":
                problem("duplicate_outcome", dispatch_id=did,
                        at_seq=seq)
            elif p.get("outcome") in _OUTCOME_VOCAB:
                # A first outcome — or the delayed report
                # settling a standing uncertainty.
                d["outcome"] = p.get("outcome")
        elif t == "TOOL_RECONCILED":
            did = p.get("dispatch_id")
            if role_of(actor) != "examiner":
                problem("reconciliation_wrong_actor",
                        dispatch_id=did, at_seq=seq, actor=actor)
            d = dispatches.get(did)
            if d is None or d["seq"] > seq:
                problem("reconciliation_without_dispatch",
                        dispatch_id=did, at_seq=seq)
            else:
                if d["reconciled"]:
                    problem("second_reconciliation",
                            dispatch_id=did, at_seq=seq)
                elif d["outcome"] != "uncertain":
                    problem("reconciliation_not_uncertain",
                            dispatch_id=did, at_seq=seq)
                if p.get("outcome") not in ("result", "failure"):
                    problem("reconciliation_outcome_unknown",
                            dispatch_id=did, at_seq=seq)
                evidence = p.get("evidence_ref")
                if not isinstance(evidence, str) or not evidence:
                    problem("reconciliation_without_evidence",
                            dispatch_id=did, at_seq=seq)
                if d["outcome"] == "uncertain" and \
                        not d["reconciled"]:
                    d["reconciled"] = True
    if problems:
        return {"result": "divergent", "problems": problems}
    return {"result": "ok"}


# ----------------------------------------------------------- verdict

def check(request):
    run_id = request.get("run_id")
    path = request.get("store_path")
    snapshot = request.get("snapshot")
    verdict = {"run_id": run_id, "checks": {}}
    checks = verdict["checks"]

    runs, events, problem = _read_store(path, run_id)
    if problem is not None:
        checks["store"] = {"result": problem}
        return verdict
    verdict["events"] = len(events)
    verdict["head_seq"] = events[-1]["event_seq"] if events else 0

    # Run binding: exactly one run row, naming the requested run;
    # every event carrying that run.
    binding = []
    if len(runs) != 1:
        binding.append(f"store holds {len(runs)} run rows")
    elif runs[0][0] != run_id:
        binding.append(f"store's run is {runs[0][0]!r}, "
                       f"not {run_id!r}")
    for ev in events:
        if ev.get("run_id") != run_id:
            binding.append(f"event at position "
                           f"{ev.get('event_seq')} carries run "
                           f"{ev.get('run_id')!r}")
            break
    checks["run_binding"] = {"result": "ok"} if not binding else {
        "result": "problem", "detail": binding[0]}

    # The two chain properties, reported independently (C6).
    positions = _chain_positions(events)
    checks["chain_hash"] = _hash_result(events, positions)
    checks["chain_sequence"] = _sequence_result(events, positions)

    # Replay — the checker's own reconstruction. Events whose
    # stored contents could not be read cannot be applied; the
    # replay reports not_run against the hash result that already
    # names the defect.
    unreadable = [ev for ev in events if "_read_error" in ev]
    state = None
    if unreadable:
        checks["replay"] = {
            "result": "not_run",
            "detail": "an event's stored contents cannot be read "
                      "(see chain_hash)"}
    else:
        classifiable = {pos for pos, (h, s, _) in
                        enumerate(positions, start=1) if h and s}
        state, halt = replay_events(events, run_id, classifiable)
        if halt is not None:
            kind, at_seq, detail, at_position = halt
            if kind == "not_classified":
                detail = "schema classification withheld: the " \
                         "event at this position is not " \
                         "established hash-valid and in sequence " \
                         f"(see the chain results) — {detail}"
            checks["replay"] = {
                "result": kind, "at_seq": at_seq,
                "at_position": at_position, "detail": detail}
        else:
            checks["replay"] = {"result": "ok"}

    if state is None:
        checks["projection_schema"] = {"result": "not_run"}
        checks["replay_equality"] = {"result": "not_run"}
        checks["seal_correspondence"] = {"result": "not_run"}
        checks["assembly_correspondence"] = {"result": "not_run"}
        checks["dispatch_correspondence"] = {"result": "not_run"}
    else:
        mine = json.loads(canonical(state))
        bad = _conforms(mine, SCHEMA)
        checks["projection_schema"] = (
            {"result": "ok"} if not bad else
            {"result": "nonconforming", "paths": bad})
        if snapshot is None:
            checks["snapshot_schema"] = {"result": "not_supplied"}
            checks["replay_equality"] = {"result": "not_run",
                                         "detail": "no snapshot "
                                                   "supplied"}
        else:
            bad = _conforms(snapshot, SCHEMA)
            checks["snapshot_schema"] = (
                {"result": "ok"} if not bad else
                {"result": "nonconforming", "paths": bad})
            divs = _divergences(mine, snapshot)
            checks["replay_equality"] = (
                {"result": "ok"} if not divs else
                {"result": "divergent", "divergences": divs})
        checks["seal_correspondence"] = _seal_result(events, state)
        checks["assembly_correspondence"] = _assembly_result(
            events, state)
        checks["dispatch_correspondence"] = _dispatch_result(
            events, state)
    return verdict


def main():
    try:
        request = json.loads(sys.stdin.read())
        if not isinstance(request, dict) or \
                not isinstance(request.get("store_path"), str) or \
                not isinstance(request.get("run_id"), str):
            verdict = {"checks": {"request": {
                "result": "request_invalid",
                "detail": "expected {store_path, run_id, "
                          "snapshot}"}}}
        else:
            verdict = check(request)
    except Exception as exc:  # a verdict, never a traceback
        verdict = {"checks": {"checker": {
            "result": "checker_error",
            "detail": type(exc).__name__}}}
    sys.stdout.write(json.dumps(verdict) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
