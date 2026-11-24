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
  tool-policy contract and executing nothing (R48). For an
  assembly declaring the retrieval contract (RETRIEVAL-SCOPE
  Rev 5), dispatch correspondence additionally verifies the
  retrieval regime from the record: the v3 version stamp,
  the admitting grant under the two authority paths with
  boundary membership for source paths, each result's
  retained-content provenance (sha256 and byte size
  recomputed over the exact content the outcome carries),
  and the aggregate admission over each package window;
- loop correspondence (Piece A3): each activation's iteration
  bookkeeping and recorded stall against the activation and
  the pinned case bounds that actually stood — numbering,
  ceiling, cursor chain, stall grounds and count, dispatch
  accounting closed before the stall, and no instance activity
  after it;
- response evidence (response-evidence piece, Rev 8): inside
  loop correspondence, each governed activation's call
  boundaries and dispositions reconstructed — CALL_ENTERED
  exactly once per entered iteration, exactly one disposition
  per entered iteration (a missing one an integrity failure,
  never reinterpreted, and reported beside an evidence
  failure terminal that discharges nothing), outcome/class/
  evidence pairing re-derived from the filed artifact, every
  layer hash recomputed from the stored base64, no dispatch
  inside the entered-but-undispositioned window, and any
  on-disk artifact bound by no disposition reported as an
  orphan.

It opens the store read-only with its own SQL, writes nothing,
creates no store, and leaves no artifacts (C7). It imports
`fabric.canonical` — the record-format and hashing primitive —
and the standard library only; never a `framework.*` module.
"""
import copy
import hashlib
import json
import math
import os
import sqlite3
import sys

from fabric.canonical import canonical, event_hash, sha256_hex

from checker.replay import replay_events
from checker.schema import SCHEMA
from checker.tool_policy import (REGISTRY_VERSION,
                                 RETRIEVAL_AGGREGATE_CEILING,
                                 RETRIEVAL_REGISTRY_VERSION,
                                 RETRIEVAL_RESULT_CEILING,
                                 RETRIEVAL_TOOLS, boundary_member,
                                 check_ceiling, known_version,
                                 registered, request_fingerprint,
                                 retrieval_authority,
                                 worker_facing)

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


# The native-mode probe contract (probe scope Rev 6), as this
# checker derives it from the scope: its own copies of the
# suite definition, the class lists, the quorum rule and the
# evidence arithmetic — the correspondence below recomputes
# every value from the events, never trusting the framework's
# arithmetic or the doorway's refusal at offer time.
_PROBE_CONTRACT = "native-probe-v1"
_PROBE_TRIALS = 5
_PROBE_CEILING = 64000
_PROBE_QUORUM = 3
_PROBE_MODES = ("text", "native")
_PROBE_BEHAVIOURS = (
    "text_contract", "native_catalogue",
    "environment_tool_attempt", "mixed", "refusal", "malformed",
    "no_observable_behaviour")
_PROBE_DELIVERIES = (
    "provider_accepted", "provider_refused", "provider_failed",
    "indeterminate")

_PROBE_SYSTEM_TEXT = (
    "You are a seat in a recorded collaborative run. Answer "
    "exactly as the contract specifies.")

_PROBE_CASE_TEXT = (
    "PROBE CASE (synthetic; nothing here is real work, and no "
    "tool call in this case is ever executed).\n"
    "Task: find the colour of the brass lantern in the scene "
    "and note it. You have two ways to act:\n"
    "1. The native tools offered with this request "
    "(probe.lookup to look an object up, probe.note to record "
    "a note).\n"
    "2. The run's text contract: reply with exactly one JSON "
    "object and no other text, of the form "
    "{\"outcome\": \"tool_requests\", \"tool_requests\": "
    "[{\"tool\": \"probe.lookup\", \"parameters\": "
    "{\"object\": \"brass lantern\"}}]}.\n"
    "Use whichever channel you would naturally use. Make one "
    "lookup for the brass lantern, then stop.")

_PROBE_TOOL_DEFINITIONS = [
    {"type": "function", "function": {
        "name": "probe.lookup",
        "description": "Look up a named object in the probe's "
                       "synthetic scene. Probe tool: a call is "
                       "recorded as evidence only and never "
                       "executes.",
        "parameters": {
            "type": "object",
            "properties": {
                "object": {"type": "string"}},
            "required": ["object"],
            "additionalProperties": False}}},
    {"type": "function", "function": {
        "name": "probe.note",
        "description": "Record a short note about the probe's "
                       "synthetic scene. Probe tool: a call is "
                       "recorded as evidence only and never "
                       "executes.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False}}},
]


def _probe_suite_hash():
    return sha256_hex(canonical({
        "suite": _PROBE_CONTRACT,
        "system": _PROBE_SYSTEM_TEXT,
        "case": _PROBE_CASE_TEXT,
        "tools": _PROBE_TOOL_DEFINITIONS,
        "parameters": {"temperature": 0.2},
        "tool_choice": "default",
        "trials": _PROBE_TRIALS,
        "capture_ceiling": _PROBE_CEILING,
        "quorum_settled": _PROBE_QUORUM,
        "behaviours": list(_PROBE_BEHAVIOURS),
        "deliveries": list(_PROBE_DELIVERIES),
    }))


# ------------------------------------------------- native adapter
# Native adapter piece (NATIVE-ADAPTER-SCOPE Rev 3, N33):
# the translation verdict, reconstructed independently.
# The checker implements its own extraction, its own
# strict validation and its own classification here —
# it never imports the framework's validator or the
# adapter's translation (N33's independence rule): the
# two implementations agreeing is the evidence; one
# implementation grading itself would be none.
_CHECKER_CALL_CAP = 1


def _checker_validate_arguments(parameters, arguments):
    """The checker's own statement of the strict
    validation contract (N8): the declared parameter list
    is the whole contract — every required parameter
    present, no undeclared parameter standing, no
    coercion, no defaults. Returns the first violated
    constraint, or None where the arguments conform."""
    if not isinstance(arguments, dict):
        return "the arguments are not an object"
    if not isinstance(parameters, list):
        return "the parameter declaration is not a list"
    declared = []
    for decl in parameters:
        if not isinstance(decl, dict):
            return "a parameter declaration is not an object"
        name = decl.get("name")
        if not isinstance(name, str) or not name:
            return "a parameter declaration's name is not " \
                "a string"
        if name in declared:
            return f"the parameter '{name}' is declared twice"
        if not isinstance(decl.get("required"), bool):
            return f"the parameter '{name}' declaration's " \
                "required flag is not a boolean"
        if not isinstance(decl.get("meaning"), str):
            return f"the parameter '{name}' declaration's " \
                "meaning is not a string"
        declared.append(name)
    for decl in parameters:
        if decl["required"] and decl["name"] not in arguments:
            return f"required parameter '{decl['name']}' " \
                "is absent"
    for key in sorted(arguments):
        if key not in declared:
            return f"parameter '{key}' is not declared"
    return None


def _checker_resolve_against_catalogue(by_name, name):
    """The checker's own catalogue determination
    (INDEX 408): whether a call's name resolves against
    the package's catalogue, decided from the name
    alone, standing in the checker's classification
    after call-ID integrity and the cap and before its
    own argument parsing — the ruled order, derived and
    implemented independently of the loop's, so a loop
    that decided resolution after parsing, or reached
    it for a refused call, would diverge here. Returns
    the catalogue entry, or None where the name is
    unknown."""
    return by_name.get(name)


def _checker_parse_arguments(raw):
    """The checker's own classification-stage parse of a
    string-form arguments value (INDEX 406): extraction
    is structural only, so the parse stands here, in the
    checker's independent classification, reached only by
    a call that survived call-ID integrity and the cap,
    and standing after the checker's own catalogue
    determination (INDEX 408) — the same order the loop
    is held to, derived and implemented independently.
    Raises ValueError where the string cannot be read
    as JSON."""
    return json.loads(raw)


def _checker_extract_calls(message):
    """The checker's own per-call extraction from a
    captured native message (the evidence artifact's L3):
    one record per call in emitted order — provider
    ordinal, provider call ID, name, arguments form and
    the arguments in that form's shape. Extraction is
    structural only (INDEX 406): a string stands raw
    under the form "string"; whether it parses is
    classification's determination, never extraction's.
    Returns [] where the message carries no calls, and
    None where the message's call structure is malformed
    as a whole (calls not a list, an entry not an object,
    content standing beside calls) — no per-call
    extraction stands for such a message."""
    if not isinstance(message, dict):
        return None
    tool_calls = message.get("tool_calls")
    if tool_calls is None:
        return []
    if message.get("content"):
        return None
    if not isinstance(tool_calls, list) or not tool_calls:
        return None
    records = []
    for position, entry in enumerate(tool_calls, start=1):
        if not isinstance(entry, dict):
            return None
        call_id = entry.get("id")
        if not isinstance(call_id, str) or not call_id:
            call_id = None
        name = None
        arguments = None
        form = "non_object"
        function = entry.get("function")
        if isinstance(function, dict):
            raw_name = function.get("name")
            if isinstance(raw_name, str) and raw_name:
                name = raw_name
            raw_args = function.get("arguments")
            if isinstance(raw_args, str):
                form, arguments = "string", raw_args
            elif isinstance(raw_args, dict):
                form, arguments = "object", raw_args
            elif raw_args is not None:
                form, arguments = "non_object", raw_args
        records.append({
            "provider_ordinal": position,
            "provider_call_id": call_id,
            "name": name,
            "arguments_form": form,
            "arguments": arguments})
    return records


def _checker_classify(records, catalogue, instance_id,
                      iteration):
    """The checker's own classification of an extraction
    (N33 (i)–(iii)), in the ruled order (INDEX 408):
    call-ID integrity, the per-response cap, name
    readability and the checker's own closed-world
    catalogue determination, argument parsing and the
    canonical hash (after integrity, the cap and the
    determination, INDEX 406/408), and the checker's
    own validation, for resolved calls only —
    producing the translation record's entry set the
    recorded record is compared against, field for
    field. The precedence is reconstructed with the
    order: the determination precedes parsing, an
    unknown name does not skip parsing, and a call
    whose arguments then fail stands malformed_call
    with resolution not_reached, as the loop's entry
    stands."""
    by_name = {}
    for entry in catalogue:
        by_name.setdefault(entry["tool"], entry)
    entries = []
    seen_ids = {}
    presented = 0
    for record in records:
        ordinal = record["provider_ordinal"]
        call_id = record["provider_call_id"]
        entry = {
            "provider_ordinal": ordinal,
            "provider_call_id": call_id,
            "name": record["name"],
            "arguments_sha256": None,
            "resolution": "not_reached",
            "validation": "not_reached",
            "validation_constraint": None,
            "refusal_class": None,
            "refusal_detail": None,
            "loop_request_id": None}
        entries.append(entry)
        if call_id is not None and call_id not in seen_ids:
            seen_ids[call_id] = ordinal
        # Call-ID integrity before the cap, as in the
        # loop's classification (build-examination
        # correction, INDEX 403): an overflow call with a
        # missing or duplicated ID is malformed_call —
        # the checker states the order independently, so
        # a loop that masked the ID defect behind the cap
        # would diverge here.
        if call_id is None:
            entry["refusal_class"] = "malformed_call"
            entry["refusal_detail"] = "its call ID was absent"
            continue
        if seen_ids.get(call_id) != ordinal:
            entry["refusal_class"] = "malformed_call"
            entry["refusal_detail"] = \
                "its call ID was duplicated"
            continue
        if ordinal > _CHECKER_CALL_CAP:
            entry["refusal_class"] = "call_cap_exceeded"
            continue
        if record["name"] is None:
            entry["refusal_class"] = "malformed_call"
            entry["refusal_detail"] = \
                "its name could not be read"
            continue
        # The checker's own catalogue determination
        # stands here, before its own parsing
        # (INDEX 408): decided from the name alone, for
        # a call that survived integrity and the cap —
        # no refused call above reached it, and no
        # argument work precedes it.
        target = _checker_resolve_against_catalogue(
            by_name, record["name"])
        # Argument parsing stands after the
        # determination in the checker's own
        # classification (INDEX 406/408), with the
        # checker's own parser, and an unknown name does
        # not skip it — the hash is required for calls
        # reaching this stage, and the malformed
        # precedence is the established one: a string
        # that cannot be read, and any form not yielding
        # an object, is malformed_call, its entry
        # standing with resolution not_reached exactly
        # as the loop's stands.
        if record["arguments_form"] == "string":
            try:
                arguments = _checker_parse_arguments(
                    record["arguments"])
            except ValueError:
                entry["refusal_class"] = "malformed_call"
                entry["refusal_detail"] = \
                    "its arguments could not be read"
                continue
            if not isinstance(arguments, dict):
                entry["refusal_class"] = "malformed_call"
                entry["refusal_detail"] = \
                    "its arguments are not an object"
                continue
        elif record["arguments_form"] == "object":
            arguments = record["arguments"]
        else:
            entry["refusal_class"] = "malformed_call"
            entry["refusal_detail"] = \
                "its arguments are not an object"
            continue
        entry["arguments_sha256"] = sha256_hex(
            canonical(arguments))
        if target is None:
            entry["resolution"] = "unknown"
            entry["refusal_class"] = "unknown_tool"
            continue
        entry["resolution"] = "resolved"
        constraint = _checker_validate_arguments(
            target["parameters"], arguments)
        if constraint is not None:
            entry["validation"] = "invalid"
            entry["validation_constraint"] = constraint
            entry["refusal_class"] = "invalid_arguments"
            continue
        entry["validation"] = "valid"
        presented += 1
        entry["loop_request_id"] = \
            f"loop-{instance_id}-{iteration}-{presented}"
    return entries


def _probe_fingerprint(route, model):
    return sha256_hex(canonical({
        "route": route,
        "model": model,
        "suite": _PROBE_CONTRACT,
        "suite_hash": _probe_suite_hash(),
        "tools": _PROBE_TOOL_DEFINITIONS,
        "parameters": {"temperature": 0.2},
        "tool_choice": "default",
    }))


_PROBE_TRIAL_HASH_FIELDS = (
    "trial", "behaviour", "delivery", "payload_form", "settled",
    "http_status", "provider_body_sha256", "provider_body_bytes",
    "provider_body_complete", "metadata_sha256",
    "diagnostics_sha256", "diagnostics_bytes",
    "diagnostics_complete", "aggregate_bytes",
    "evidence_complete",
)


def _probe_evidence_hash(probed):
    return sha256_hex(canonical({
        "generated_record_hash": probed.get(
            "generated_record_hash"),
        "suite": probed.get("suite"),
        "suite_hash": probed.get("suite_hash"),
        "fingerprint": probed.get("fingerprint"),
        "trials": [
            {key: trial.get(key)
             for key in _PROBE_TRIAL_HASH_FIELDS}
            for trial in probed.get("trials") or []],
        "counts": probed.get("counts"),
        "settled_count": probed.get("settled_count"),
        "recommended_mode": probed.get("recommended_mode"),
    }))


def _probe_summarise(trials):
    counts = {
        "behaviour": {name: 0 for name in _PROBE_BEHAVIOURS},
        "delivery": {name: 0 for name in _PROBE_DELIVERIES},
    }
    for trial in trials:
        if trial.get("behaviour") in counts["behaviour"]:
            counts["behaviour"][trial["behaviour"]] += 1
        if trial.get("delivery") in counts["delivery"]:
            counts["delivery"][trial["delivery"]] += 1
    settled = sum(1 for trial in trials if trial.get("settled"))
    recommended = None
    if settled >= _PROBE_QUORUM:
        if counts["behaviour"]["text_contract"] * 2 > settled:
            recommended = "text"
        elif counts["behaviour"]["native_catalogue"] * 2 > \
                settled:
            recommended = "native"
    return counts, settled, recommended


def _probe_trial_problem(trial, position):
    """Why one recorded probe trial is not well-formed
    evidence, or None — the checker's own recomputation of
    the scope's evidence rules (probe scope §3): classes from
    the scope's lists, the settled flag the behaviour's own
    consequence, per-object hashes and byte counts recomputed
    from the retained text, the aggregate the content
    objects' sum under the ceiling, completeness per object
    and never labelled complete past what the ceiling
    forced."""
    if not isinstance(trial, dict):
        return "trial is not an object"
    if trial.get("trial") != position:
        return "trial position does not match its index"
    behaviour = trial.get("behaviour")
    if behaviour not in _PROBE_BEHAVIOURS:
        return f"behaviour {behaviour!r} is not a scope class"
    if trial.get("delivery") not in _PROBE_DELIVERIES:
        return "delivery is not a scope class"
    if trial.get("payload_form") not in (
            None, "text_contract_json"):
        return "payload_form is not a scope detail"
    if trial.get("settled") != \
            (behaviour != "no_observable_behaviour"):
        return "settled flag contradicts the behaviour class"
    body = trial.get("provider_body")
    if body is not None and not isinstance(body, str):
        return "provider body is not text"
    body_bytes = len(body.encode("utf-8")) \
        if body is not None else 0
    if trial.get("provider_body_bytes") != body_bytes:
        return "provider body byte count does not recompute"
    body_hash = hashlib.sha256(
        body.encode("utf-8")).hexdigest() \
        if body is not None else None
    if trial.get("provider_body_sha256") != body_hash:
        return "provider body hash does not recompute"
    diag = trial.get("diagnostics")
    if diag is not None and not isinstance(diag, str):
        return "diagnostics are not text"
    diag_bytes = len(diag.encode("utf-8")) \
        if diag is not None else 0
    if trial.get("diagnostics_bytes") != diag_bytes:
        return "diagnostics byte count does not recompute"
    diag_hash = hashlib.sha256(
        diag.encode("utf-8")).hexdigest() \
        if diag is not None else None
    if trial.get("diagnostics_sha256") != diag_hash:
        return "diagnostics hash does not recompute"
    aggregate = trial.get("aggregate_bytes")
    if aggregate != body_bytes + diag_bytes:
        return "aggregate is not the content objects' sum"
    if not isinstance(aggregate, int) or \
            aggregate > _PROBE_CEILING:
        return "aggregate exceeds the capture ceiling"
    if not isinstance(
            trial.get("provider_body_complete"), bool) or \
            not isinstance(
                trial.get("diagnostics_complete"), bool):
        return "completeness standings are not booleans"
    if body is None and trial.get("provider_body_complete"):
        return "an absent provider body is labelled complete"
    # A present object standing incomplete means the ceiling
    # cut it — possible only with the aggregate at the
    # ceiling. An absent object is honestly incomplete at
    # any aggregate: nothing was produced, nothing was cut.
    if (body is not None
            and trial.get("provider_body_complete") is not True
            or diag is not None
            and trial.get("diagnostics_complete") is not True) \
            and aggregate != _PROBE_CEILING:
        return "evidence stands incomplete below the ceiling"
    if trial.get("evidence_complete") != \
            (trial.get("provider_body_complete") is True):
        return "evidence completeness is not the body's"
    metadata = trial.get("metadata")
    if not isinstance(metadata, dict):
        return "metadata is not an object"
    if trial.get("metadata_sha256") != sha256_hex(
            canonical(metadata)):
        return "metadata hash does not recompute"
    return None


def _probe_correspondence(problem, aid, gen_ev, digest, mine,
                          probed_evs, role_of):
    """Probe correspondence (probe scope §4/P4): for an
    assembly whose generated record declares the probe
    contract — the binding chain reconstructed from the
    events: exactly one probe act, after generation and
    before verification, binding the exact generated record
    by its hash and its evidence by the evidence hash;
    the suite identified by its canonical hash; the
    configuration fingerprint fresh; every trial's evidence
    recomputed; the counts, quorum and recommendation
    recomputed; verification naming the evidence (the
    verified boundary covers it); the judgement identifying
    the exact probe event and evidence, recording a mode
    with grounds, and binding the hash of the examiner's
    durable decision receipt (INDEX 293 — the decision's
    own provenance); the pack sealing the same bindings and
    the judged mode itself — the end-to-end property that
    the mode the adapter receives is the mode the examiner
    judged. A probe act under no declaration, or an unknown
    declaration, diverges."""
    gen_payload = gen_ev["payload"]
    declared = gen_payload.get("probe_contract")
    if declared is not None and declared != _PROBE_CONTRACT:
        problem("probe_contract_unknown", assembly_id=aid,
                at_seq=gen_ev["event_seq"],
                declared=declared)
        return
    if declared != _PROBE_CONTRACT:
        for ev in probed_evs:
            problem("probe_act_without_declaration",
                    assembly_id=aid, at_seq=ev["event_seq"])
        return
    verified = (mine.get("ASSEMBLY_VERIFIED") or [None])[0]
    judged = (mine.get("ASSEMBLY_JUDGED") or [None])[0]
    packed = (mine.get("ASSEMBLY_PACKED") or [None])[0]
    if len(probed_evs) > 1:
        problem("duplicate_assembly_act", type="ASSEMBLY_PROBED",
                assembly_id=aid,
                at_seq=probed_evs[1]["event_seq"])
    if not probed_evs:
        later = verified or judged or packed
        if later is not None:
            problem("probe_stage_missing", assembly_id=aid,
                    at_seq=later["event_seq"])
        return
    ev = probed_evs[0]
    pp = ev["payload"]
    if role_of(ev["actor"]) != "orchestrator":
        problem("assembly_act_wrong_role", type="ASSEMBLY_PROBED",
                assembly_id=aid, at_seq=ev["event_seq"],
                actor=ev["actor"])
    if ev["event_seq"] <= gen_ev["event_seq"] or (
            verified is not None and
            ev["event_seq"] >= verified["event_seq"]):
        problem("assembly_act_out_of_order",
                type="ASSEMBLY_PROBED", assembly_id=aid,
                at_seq=ev["event_seq"])
    if pp.get("generated_record_hash") != digest:
        problem("probe_binding_mismatch",
                binding="generated_record", assembly_id=aid,
                at_seq=ev["event_seq"])
    if pp.get("suite") != _PROBE_CONTRACT or \
            pp.get("suite_hash") != _probe_suite_hash():
        problem("probe_suite_mismatch", assembly_id=aid,
                at_seq=ev["event_seq"])
    if pp.get("fingerprint") != _probe_fingerprint(
            pp.get("route"), pp.get("model")):
        problem("probe_fingerprint_stale", assembly_id=aid,
                at_seq=ev["event_seq"])
    trials = pp.get("trials")
    if not isinstance(trials, list) or \
            len(trials) != _PROBE_TRIALS:
        problem("probe_trial_count", assembly_id=aid,
                at_seq=ev["event_seq"])
        trials = trials if isinstance(trials, list) else []
    for position, trial in enumerate(trials, start=1):
        detail = _probe_trial_problem(trial, position)
        if detail is not None:
            problem("probe_trial_evidence_mismatch",
                    assembly_id=aid, at_seq=ev["event_seq"],
                    trial=position, detail=detail)
    counts, settled, recommended = _probe_summarise(
        [t for t in trials if isinstance(t, dict)])
    if pp.get("counts") != counts or \
            pp.get("settled_count") != settled or \
            pp.get("recommended_mode") != recommended:
        problem("probe_counts_mismatch", assembly_id=aid,
                at_seq=ev["event_seq"])
    if pp.get("evidence_hash") != _probe_evidence_hash(pp):
        problem("probe_evidence_hash_mismatch", assembly_id=aid,
                at_seq=ev["event_seq"])
    evidence_hash = pp.get("evidence_hash")
    if verified is not None and \
            verified["payload"].get("probe_evidence_hash") != \
            evidence_hash:
        problem("probe_verification_binding_mismatch",
                assembly_id=aid,
                at_seq=verified["event_seq"])
    if judged is not None:
        jp = judged["payload"]
        if jp.get("probe_seq") != ev["event_seq"]:
            problem("probe_judgement_binding_mismatch",
                    binding="probe_event", assembly_id=aid,
                    at_seq=judged["event_seq"])
        if jp.get("probe_evidence_hash") != evidence_hash:
            problem("probe_judgement_binding_mismatch",
                    binding="probe_evidence", assembly_id=aid,
                    at_seq=judged["event_seq"])
        if jp.get("adapter_mode") not in _PROBE_MODES:
            problem("probe_mode_invalid", assembly_id=aid,
                    at_seq=judged["event_seq"])
        grounds = jp.get("mode_grounds")
        if not isinstance(grounds, str) or not grounds:
            problem("probe_mode_grounds_missing",
                    assembly_id=aid,
                    at_seq=judged["event_seq"])
        receipt_hash = jp.get("decision_receipt_hash")
        if receipt_hash is None:
            problem("probe_decision_receipt_missing",
                    assembly_id=aid,
                    at_seq=judged["event_seq"])
        elif not isinstance(receipt_hash, str) or \
                len(receipt_hash) != 64 or \
                any(c not in "0123456789abcdef"
                    for c in receipt_hash):
            problem("probe_decision_receipt_invalid",
                    assembly_id=aid,
                    at_seq=judged["event_seq"])
    if packed is not None:
        kp = packed["payload"]
        if kp.get("probe_evidence_hash") != evidence_hash:
            problem("probe_pack_binding_mismatch",
                    assembly_id=aid,
                    at_seq=packed["event_seq"])
        judged_mode = (judged["payload"].get("adapter_mode")
                       if judged is not None else None)
        if kp.get("adapter_mode") != judged_mode:
            problem("probe_mode_mismatch", assembly_id=aid,
                    at_seq=packed["event_seq"])


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
    Under a probe-declaring generated record, the probe
    binding chain is verified with it (probe scope §4): the
    probe act's position and bindings, its evidence
    recomputed object by object, verification covering the
    evidence, the judgement's mode and grounds, and the pack
    sealing the judged mode. An incomplete or incorrectly
    ordered assembly history is reported, never read as
    valid."""
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
    probed = {}
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
        elif t == "ASSEMBLY_PROBED":
            probed.setdefault(p.get("assembly_id"), []) \
                .append(ev)
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
        # The probe binding chain, where the generated record
        # declares the probe contract (probe scope §4).
        _probe_correspondence(problem, aid, ev, digest, mine,
                              probed.get(aid, []), role_of)
    for aid, mine in stages.items():
        if aid not in generated:
            for kind, evs in mine.items():
                problem("assembly_act_without_generation",
                        type=kind, assembly_id=aid,
                        at_seq=evs[0]["event_seq"])
    for aid, evs in probed.items():
        if aid not in generated:
            problem("assembly_act_without_generation",
                    type="ASSEMBLY_PROBED", assembly_id=aid,
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
    version that governed it, and is verified under that
    version's own contract — a known historical version is
    verified as recorded, never reinterpreted under the
    current one (Piece A3-CAT); a missing or unknown version
    is reported, never silently accepted; a dispatch's tool is
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

    # The retrieval piece (RETRIEVAL-SCOPE Rev 5): an
    # assembly whose sealed record declares the retrieval
    # contract is governed by it, and its retrieval
    # dispatches are verified against the regime the doorway
    # enforced — the v3 version stamp, the admitting grant
    # under the two authority paths, boundary membership for
    # source paths, retained-content provenance on every
    # result, and the aggregate admission over each package
    # window. An assembly declaring anything else asks none
    # of this: the historical exemption, read from the
    # assembly's own declaration.
    def retrieval_governed(instance_id):
        ev = generated_by_instance.get(instance_id)
        return ev is not None and \
            ev["payload"].get("catalogue_contract") == \
            _RETRIEVAL_CONTRACT

    def pinned_boundary(instance_id):
        """The evidence boundary of the exact case version
        the instance's assembly record pins, from the
        replayed state — the membership source retrieval
        must show."""
        ev = generated_by_instance.get(instance_id)
        if ev is None:
            return None
        gp = ev["payload"]
        case = (state.get("cases") or {}).get(
            gp.get("case_id"))
        ver = ((case or {}).get("versions") or {}).get(
            str(gp.get("case_version"))) or {}
        boundary = (ver.get("content") or {}).get(
            "evidence_boundary")
        return boundary if isinstance(boundary, list) else None

    def retrieval_admitting(grants, tool, parameters,
                            version):
        """(grant, authority, ground): the doorway's
        admitting-grant rule, reconstructed — the first
        grant for the tool, in sealed order, whose ceiling
        the request satisfies under the recorded version and
        whose scope is the request path's authority scope.
        A pathless search is admitted under the source path.
        ground names why no grant admits, where none does."""
        if not isinstance(parameters, dict):
            return None, None, "the request's parameters " \
                               "are not an object"
        path = parameters.get("path")
        authority = "source" if path is None else \
            retrieval_authority(path)
        if authority is None:
            return None, None, (
                f"path {path!r} lies under neither the "
                f"sources/ scope nor the scratch/ scope")
        scope_prefix = "sources" if authority == "source" \
            else "scratch"
        first_ground = None
        for grant in grants or []:
            if not isinstance(grant, dict) or \
                    grant.get("tool") != tool:
                continue
            ok, ground = check_ceiling(
                tool, grant.get("scope_ceiling"), parameters,
                version=version)
            if not ok:
                if first_ground is None:
                    first_ground = ground
                continue
            prefix = (grant.get("scope_ceiling") or {}).get(
                "path_prefix")
            if prefix != scope_prefix:
                if first_ground is None:
                    first_ground = (
                        f"the admitting grant's scope is "
                        f"{prefix!r}, not the {scope_prefix!r} "
                        f"scope the {authority} authority path "
                        f"requires")
                continue
            return grant, authority, None
        return None, authority, first_ground or (
            f"no grant for tool {tool} stands in the sealed "
            f"record")

    requests = {}
    dispatches = {}
    counts = {}
    iterations = {}
    retrieval_outcomes = []
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
            # Piece A3-CAT (settlement (c)): the dispatch is
            # verified under the version it was recorded
            # under — a known historical version (v1) is
            # lawful and verified under its own contract,
            # never reinterpreted under the current one; a
            # missing or unknown version is an explicit
            # divergence (the existing kind), never a silent
            # ok.
            version_known = known_version(
                p.get("registry_version"))
            if not version_known:
                problem("dispatch_registry_version_mismatch",
                        dispatch_id=did, at_seq=seq,
                        registry_version=p.get(
                            "registry_version"),
                        checker_registry_version=REGISTRY_VERSION)
            # The retrieval piece: the version follows the
            # assembly's declared contract — a governed
            # assembly's dispatches are governed by v3, and
            # v3 recorded for an assembly that declares no
            # retrieval contract is a stamp nothing issued.
            if retrieval_governed(iid) and \
                    p.get("registry_version") != \
                    RETRIEVAL_REGISTRY_VERSION:
                problem("dispatch_registry_version_mismatch",
                        dispatch_id=did, at_seq=seq,
                        registry_version=p.get(
                            "registry_version"),
                        expected=RETRIEVAL_REGISTRY_VERSION)
            elif not retrieval_governed(iid) and \
                    p.get("registry_version") == \
                    RETRIEVAL_REGISTRY_VERSION:
                problem("dispatch_registry_version_mismatch",
                        dispatch_id=did, at_seq=seq,
                        registry_version=p.get(
                            "registry_version"),
                        detail="v3 recorded for an assembly "
                               "that declares no retrieval "
                               "contract")
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
                elif retrieval_governed(iid) and \
                        p.get("tool") in RETRIEVAL_TOOLS and \
                        req is not None:
                    # The retrieval branch: the admitting
                    # grant is chosen by the doorway's rule —
                    # the first whose ceiling the request
                    # satisfies and whose scope is the path's
                    # authority scope — and source admission
                    # additionally requires the path's
                    # membership in the pinned boundary. The
                    # bound counts the tool's dispatches, as
                    # every grant's bound does, read from the
                    # admitting grant.
                    admitting, authority, ground = \
                        retrieval_admitting(
                            grants, p.get("tool"),
                            req["parameters"],
                            p.get("registry_version"))
                    if admitting is None:
                        problem("dispatch_exceeds_ceiling",
                                dispatch_id=did, at_seq=seq,
                                detail=ground)
                    else:
                        trace = admitting.get("authority_trace")
                        if not isinstance(trace, str) or \
                                not trace:
                            problem(
                                "grant_without_authority_trace",
                                dispatch_id=did, at_seq=seq)
                        req_path = (req["parameters"] or {}).get(
                            "path")
                        if authority == "source" and \
                                req_path is not None and \
                                not boundary_member(
                                    pinned_boundary(iid),
                                    req_path):
                            problem(
                                "retrieval_boundary_violation",
                                dispatch_id=did, at_seq=seq,
                                path=req_path)
                        bound = admitting.get("bound")
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
                else:
                    trace = grant.get("authority_trace")
                    if not isinstance(trace, str) or not trace:
                        problem("grant_without_authority_trace",
                                dispatch_id=did, at_seq=seq)
                    if req is not None and version_known:
                        ok, ground = check_ceiling(
                            p.get("tool"),
                            grant.get("scope_ceiling"),
                            req["parameters"],
                            version=p.get("registry_version"))
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
                "reconciled": False,
                "tool": p.get("tool"),
                "governed": retrieval_governed(iid),
                "parameters": (requests.get((iid, rid)) or {})
                .get("parameters"),
                "authority": None}
            if dispatches[did]["governed"] and \
                    p.get("tool") in RETRIEVAL_TOOLS and \
                    isinstance(dispatches[did]["parameters"],
                               dict):
                req_path = dispatches[did]["parameters"].get(
                    "path")
                dispatches[did]["authority"] = "source" \
                    if req_path is None else \
                    retrieval_authority(req_path)
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
            # The retrieval piece: a governed retrieval
            # outcome's provenance is verified — the retained
            # content's sha256 and byte size recomputed over
            # the exact bytes the record carries, the recorded
            # authority path and path against the request's
            # own, and the per-result ceiling — and its size
            # is collected for the aggregate verification
            # below (a result at its size, an uncertainty at
            # the full ceiling, a failure at nothing).
            if d is not None and d.get("governed") and \
                    d.get("tool") in RETRIEVAL_TOOLS and \
                    p.get("outcome") in _OUTCOME_VOCAB:
                if p.get("outcome") == "uncertain":
                    retrieval_outcomes.append(
                        (seq, d["instance_id"], did,
                         RETRIEVAL_RESULT_CEILING))
                elif p.get("outcome") == "failure":
                    retrieval_outcomes.append(
                        (seq, d["instance_id"], did, 0))
                elif p.get("outcome") == "result":
                    result = p.get("result")
                    size = RETRIEVAL_RESULT_CEILING
                    if not isinstance(result, dict):
                        problem(
                            "retrieval_provenance_mismatch",
                            dispatch_id=did, at_seq=seq,
                            detail="the retrieval outcome "
                                   "carries no result object")
                    else:
                        content = result.get("content")
                        recorded = result.get("content_bytes")
                        digest = result.get("content_sha256")
                        if not isinstance(content, str) or \
                                not isinstance(recorded, int) \
                                or isinstance(recorded, bool) \
                                or not isinstance(digest, str):
                            problem(
                                "retrieval_provenance_mismatch",
                                dispatch_id=did, at_seq=seq,
                                detail="the retrieval result "
                                       "does not carry its "
                                       "content, byte size and "
                                       "sha256 as recorded "
                                       "fields")
                        else:
                            raw = content.encode("utf-8")
                            if len(raw) != recorded or \
                                    sha256_hex(raw) != digest:
                                problem(
                                    "retrieval_provenance_"
                                    "mismatch",
                                    dispatch_id=did, at_seq=seq)
                            else:
                                size = recorded
                            if recorded > \
                                    RETRIEVAL_RESULT_CEILING:
                                problem(
                                    "retrieval_result_over_"
                                    "ceiling",
                                    dispatch_id=did, at_seq=seq,
                                    content_bytes=recorded)
                        if result.get("authority_path") != \
                                d.get("authority"):
                            problem(
                                "retrieval_authority_mismatch",
                                dispatch_id=did, at_seq=seq,
                                authority_path=result.get(
                                    "authority_path"),
                                expected=d.get("authority"))
                        if result.get("path") != \
                                (d.get("parameters") or {}).get(
                                    "path"):
                            problem(
                                "retrieval_authority_mismatch",
                                dispatch_id=did, at_seq=seq,
                                detail="the outcome's path is "
                                       "not the request's "
                                       "path")
                    retrieval_outcomes.append(
                        (seq, d["instance_id"], did, size))
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
        elif t == "LOOP_ITERATION":
            iterations.setdefault(p.get("instance_id"),
                                  []).append(
                                      (seq, p.get("cursor_to")))

    # The aggregate verification (retrieval scope §3a),
    # reconstructed from the record as the doorway derived
    # it: each dispatch counts once toward its package
    # window, by its latest standing outcome — a result at
    # its retained size, an uncertainty at the full ceiling.
    # For every window, the settled total must stand within
    # the aggregate ceiling; and every retrieval dispatch's
    # admission must have been lawful when it was made: the
    # total settled before it in its window, plus the
    # per-result ceiling, within the aggregate ceiling.
    # Outstanding state at a stall is already inside these
    # sums — the stall discipline closes accounting before
    # the stall, so a dispatch admitted in the final window
    # stands there with an outcome, uncertainty included.
    def window_start(instance_id, before_seq):
        start = 0
        for iter_seq, cursor_to in iterations.get(
                instance_id, []):
            if iter_seq < before_seq and \
                    isinstance(cursor_to, int) and \
                    not isinstance(cursor_to, bool):
                start = cursor_to
        return start

    history = {}
    for seq, iid, did, size in retrieval_outcomes:
        history.setdefault(did, []).append((seq, iid, size))
    window_totals = {}
    for did, entries in history.items():
        oseq, oiid, osize = entries[-1]
        key = (oiid, window_start(oiid, oseq))
        window_totals[key] = window_totals.get(key, 0) + osize
    for (iid, start), total in sorted(window_totals.items()):
        if total > RETRIEVAL_AGGREGATE_CEILING:
            problem("retrieval_aggregate_exceeded",
                    instance_id=iid, window_start=start,
                    total=total,
                    ceiling=RETRIEVAL_AGGREGATE_CEILING)
    for did, d in dispatches.items():
        if not d.get("governed") or \
                d.get("tool") not in RETRIEVAL_TOOLS:
            continue
        start = window_start(d["instance_id"], d["seq"])
        settled = 0
        for other, entries in history.items():
            if other == did:
                continue
            # The contribution standing when this dispatch was
            # admitted: the dispatch's latest outcome before
            # it, inside the same window — an uncertainty
            # standing then counts at the ceiling even where
            # a delayed report settled it afterwards.
            standing = None
            for oseq, oiid, osize in entries:
                if oiid == d["instance_id"] and \
                        start < oseq < d["seq"]:
                    standing = osize
            if standing is not None:
                settled += standing
        if settled + RETRIEVAL_RESULT_CEILING > \
                RETRIEVAL_AGGREGATE_CEILING:
            problem("retrieval_admission_exceeded",
                    dispatch_id=did, at_seq=d["seq"],
                    settled=settled,
                    ceiling=RETRIEVAL_AGGREGATE_CEILING)
    if problems:
        return {"result": "divergent", "problems": problems}
    return {"result": "ok"}


# ------------------------------------------------------------ loop

_LOOP_ACTOR = "loop"

_LOOP_GROUNDS = ("step_ceiling", "deadline", "provider_failure",
                 "malformed_response", "runtime_failure")

# The A3-CAT catalogue contract's declaration value (Piece
# A3-CAT, correction round): the sealed ASSEMBLY_GENERATED
# payload of an assembly governed by the contract declares
# it; this checker's own statement of the value, duplicated
# as its other contracts are. An assembly whose record
# carries no declaration predates the contract — its
# iterations are historical and exempt, identifiably.
_CATALOGUE_CONTRACT = "a3-cat"

# The retrieval contract's declaration value (RETRIEVAL-SCOPE
# Rev 5): an assembly declaring it is governed by the
# retrieval regime — v3 dispatches, the two authority paths,
# the aggregate admission, retained-content provenance —
# and this checker verifies all of it within dispatch
# correspondence. The governed catalogue contracts are the
# two values together: an assembly declaring either owes
# the catalogue commitment; an assembly declaring any other
# value declares a contract this checker does not
# understand.
_RETRIEVAL_CONTRACT = "retrieval-v3"

_GOVERNED_CATALOGUE_CONTRACTS = (_CATALOGUE_CONTRACT,
                                 _RETRIEVAL_CONTRACT)

# Response-evidence piece (WORKER-RESPONSE-EVIDENCE-SCOPE
# Rev 8): the disposition contract's tables — this
# checker's own copies, reconstructed independently of
# the doorway's and the loop's, as its other contracts
# are. The one class a no_response disposition may name;
# the pre-response error-kind family its seam evidence
# must carry; the classes an unresolved disposition may
# name; the closed pre-call terminal steps; the failed
# operations an evidence failure terminal may name.
_EVIDENCE_NO_RESPONSE_CLASS = "connection_failed_pre_response"
_EVIDENCE_PRE_RESPONSE_KINDS = frozenset({
    "ConnectionRefusedError", "ConnectionResetError",
    "ConnectionAbortedError", "BrokenPipeError",
    "gaierror", "SSLError", "SSLCertVerificationError",
    "TimeoutError", "socket.timeout", "URLError",
    "RemoteDisconnected", "EOFError",
})
_EVIDENCE_UNRESOLVED_CLASSES = frozenset({
    "timeout_after_send", "helper_exit_no_envelope",
    "envelope_unparseable", "termination_unconfirmed",
    "transport_internal_error",
})
_EVIDENCE_PRE_CALL_STEPS = frozenset({
    "package_construction", "deadline_at_start"})
_EVIDENCE_FAILURE_OPERATIONS = frozenset({
    "persist", "verify", "commit"})
_EVIDENCE_OUTCOMES = ("captured", "no_response",
                      "unresolved")
# The capture ceiling (R7-1/R8-1), this checker's own
# copy: the largest body the evidence contract
# undertakes to hold whole, against which the artifact's
# boundary claims are arithmetically verified — eof only
# below it, capture_limit only exactly at it,
# read_failure only below it with its error kind.
_EVIDENCE_CAPTURE_CEILING = 64000


def _derive_catalogue(grants, version, per_grant=False):
    """The expected tool catalogue for a sealed grants list
    under a named registry version (Piece A3-CAT): this
    checker's independent reconstruction of what the loop's
    package must have advertised — one entry per granted
    tool (the first grant of each), in canonical tool order,
    the grant's own ceiling, bound and side-effect class
    joined with this copy's worker-facing description and
    parameter schema for the tool under that version. A
    grant naming an unregistered tool advertises nothing.
    Returns (catalogue, None), or (None, ground) where a
    granted, registered tool carries no complete
    worker-facing layer under the version — the catalogue
    the record claims cannot be reconstructed, which is a
    divergence to report, not a check that passes.

    The attempt-7 release correction (INDEX 257, blocker
    1) adds the per_grant parameter, applied where the
    sealed record declares the retrieval contract: that
    regime grants the same tools under two authority
    scopes, and the expected catalogue carries one entry
    per grant — both scopes, in canonical tool order
    (grants of one tool in sealed order) — exactly as the
    loop derives it. Any other declaration keeps the
    first-grant reconstruction exactly as it stood."""
    entries = []
    seen = set()
    for grant in grants or []:
        if not isinstance(grant, dict):
            continue
        tool = grant.get("tool")
        if not isinstance(tool, str) or not tool:
            continue
        if not per_grant:
            if tool in seen:
                continue
            seen.add(tool)
        if not registered(tool, version):
            continue
        facing = worker_facing(tool, version)
        if facing is None:
            return None, (
                f"granted tool {tool!r} carries no complete "
                f"worker-facing layer under {version}")
        entries.append({
            "tool": tool,
            "description": facing["description"],
            "parameters": facing["parameters"],
            "scope_ceiling": copy.deepcopy(
                grant.get("scope_ceiling")),
            "bound": copy.deepcopy(grant.get("bound")),
            "side_effect_class":
                grant.get("side_effect_class"),
        })
    entries.sort(key=lambda entry: entry["tool"])
    return entries, None


def _loop_result(events, state, run_dir=None):
    """Loop correspondence (Piece A3, R49–R51/R55): the bounded
    loop's bookkeeping reconstructed from the events themselves
    — every iteration and stall against the activation that
    actually stood. The activation is the generated assembly's
    INSTANCE_ACTIVATED; its governing bounds are the loop
    bounds of the exact case version the assembly record pins
    (a later case version's bounds govern nothing here). The
    check verifies: iteration and stall events carry the loop
    machinery's own actor and no one else's; each binds the
    standing activation — its instance, its activation event,
    its pinned case — exactly; iteration numbers are 1, 2, 3,
    ... with no gap, duplicate or excess over the pinned
    ceiling; the bounds an iteration names are the pinned
    bounds; pinned bounds present in the record but failing
    the strict contract (positive integer ceiling, finite
    positive deadline) are divergent in themselves — a case
    carrying no bounds at all is not; cursor ranges chain
    without gaps or overlaps, each
    package's head preceding the iteration event that records
    it, and each iteration event itself presented in the
    following iteration's range; a stall names a settled
    ground and the exact iteration count, and is recorded only
    after dispatch accounting closed — every dispatch of the
    instance standing at the stall held an attributable
    outcome by then (an uncertain outcome is accounted, not
    resolved; a delayed report settling it afterwards is
    executor accounting, not instance activity); and no
    instance activity — no iteration, request, dispatch or
    start — follows a stall. The catalogue commitment (Piece
    A3-CAT) is governed by the compatibility discriminator
    the sealed generated record declares: an assembly whose
    ASSEMBLY_GENERATED payload declares the contract owes
    the catalogue hash and the registry version on every
    iteration — either field absent is divergent
    (catalogue_commitment_missing), so a governed iteration
    cannot evade verification by omission — and where both
    stand, the hash is verified against the catalogue
    independently reconstructed from the activation's sealed
    grants under this checker's own registry copy at the
    recorded version: a version this copy does not hold, or
    a catalogue it cannot derive from the sealed grants, is
    an explicit divergence — never a silent ok — and a hash
    that differs from the reconstruction's is a mismatch. An
    assembly whose record declares no contract predates it:
    its iterations are lawful historical record and ask
    nothing here, the exemption read from the assembly's own
    declaration, never inferred from an iteration's missing
    fields. An assembly declaring any OTHER value declares
    a contract this checker does not understand: that is
    divergent in itself (catalogue_contract_unknown),
    reported once for the assembly — a declared-but-unknown
    contract is not a historical record, and no exemption
    is invented for it. An undeclared assembly's iteration
    that nevertheless carries a hash is verified as before.
    Nothing here runs a model or a tool (R48)."""
    problems = []

    def problem(kind, **fields):
        entry = {"kind": kind}
        entry.update(fields)
        problems.append(entry)

    generated = {}
    activated = {}
    judged_modes = {}
    packed_modes = {}
    for ev in events:
        t = ev["type"]
        p = ev["payload"]
        if t == "ASSEMBLY_GENERATED":
            generated.setdefault(p.get("assembly_id"), ev)
        elif t == "INSTANCE_ACTIVATED":
            activated.setdefault(p.get("assembly_id"),
                                 ev["event_seq"])
        elif t == "ASSEMBLY_JUDGED":
            judged_modes.setdefault(p.get("assembly_id"),
                                    p.get("adapter_mode"))
        elif t == "ASSEMBLY_PACKED":
            packed_modes.setdefault(p.get("assembly_id"),
                                    p.get("adapter_mode"))

    def pinned_bounds(aid):
        """The loop bounds of the assembly's pinned case
        version, from this checker's replayed state — or None
        where the pinned case's content does not stand or
        carries no bounds."""
        gen = generated.get(aid)
        if gen is None:
            return None
        case = (state.get("cases") or {}).get(
            gen["payload"].get("case_id"))
        ver = ((case or {}).get("versions") or {}).get(
            str(gen["payload"].get("case_version"))) or {}
        content = ver.get("content") or {}
        bounds = content.get("loop_bounds")
        return bounds if isinstance(bounds, dict) else None

    def pinned_bounds_malformed(aid):
        """Whether the assembly's pinned case version carries
        loop_bounds that are present but fail the strict
        contract (Piece A3, correction round 2): a step
        ceiling that is a positive integer and a deadline
        that is a finite, positive number — this checker's
        own statement of the contract, duplicated as its
        other contracts are. A case carrying no loop_bounds
        at all is lawful — no regime stands, and nothing is
        flagged. Present-but-malformed bounds are divergent:
        the record claims a governing contract that cannot
        govern, which is a different thing from no contract,
        and the doorway's normalisation treating them as
        no-bounds does not make the record's claim sound."""
        gen = generated.get(aid)
        if gen is None:
            return False
        case = (state.get("cases") or {}).get(
            gen["payload"].get("case_id"))
        ver = ((case or {}).get("versions") or {}).get(
            str(gen["payload"].get("case_version"))) or {}
        content = ver.get("content") or {}
        if content.get("loop_bounds") is None:
            return False
        bounds = content.get("loop_bounds")
        if not isinstance(bounds, dict):
            return True
        ceiling = bounds.get("step_ceiling")
        if isinstance(ceiling, bool) or \
                not isinstance(ceiling, int) or ceiling <= 0:
            return True
        deadline = bounds.get("deadline_seconds")
        if isinstance(deadline, bool) or \
                not isinstance(deadline, (int, float)) or \
                not math.isfinite(deadline) or deadline <= 0:
            return True
        return False

    def binding_problems(kind, ev, aid):
        """Whether a loop event's binding fields name the
        standing activation exactly; returns True when a
        problem was recorded (the event binds nothing)."""
        p = ev["payload"]
        gen = generated.get(aid)
        if gen is None or aid not in activated:
            problem(f"{kind}_without_activation",
                    assembly_id=aid, at_seq=ev["event_seq"])
            return True
        gp = gen["payload"]
        if p.get("instance_id") != gp.get("instance_id") or \
                p.get("case_id") != gp.get("case_id") or \
                p.get("case_version") != gp.get("case_version"):
            problem(f"{kind}_binding_mismatch", assembly_id=aid,
                    at_seq=ev["event_seq"])
            return True
        if p.get("activated_seq") != activated[aid]:
            problem(f"{kind}_activation_mismatch",
                    assembly_id=aid, at_seq=ev["event_seq"])
            return True
        return False

    iterations = {}
    stalls = {}
    entered = {}
    dispositions = {}
    evidence_failures = {}
    translations = {}
    for ev in events:
        t = ev["type"]
        p = ev["payload"]
        seq = ev["event_seq"]
        if t == "LOOP_ITERATION":
            aid = p.get("assembly_id")
            if ev["actor"] != _LOOP_ACTOR:
                problem("iteration_wrong_actor", assembly_id=aid,
                        at_seq=seq, actor=ev["actor"])
            if binding_problems("iteration", ev, aid):
                continue
            iterations.setdefault(aid, []).append(ev)
        elif t == "LOOP_STALLED":
            aid = p.get("assembly_id")
            if ev["actor"] != _LOOP_ACTOR:
                problem("stall_wrong_actor", assembly_id=aid,
                        at_seq=seq, actor=ev["actor"])
            if aid in stalls:
                problem("second_stall", assembly_id=aid,
                        at_seq=seq)
            stalls.setdefault(aid, ev)
            if p.get("ground") not in _LOOP_GROUNDS:
                problem("stall_ground_unknown", assembly_id=aid,
                        at_seq=seq, ground=p.get("ground"))
            binding_problems("stall", ev, aid)
        elif t == "CALL_ENTERED":
            # Response-evidence piece: the call boundary —
            # the loop machinery's own actor, bound to the
            # standing activation exactly, like its other
            # bookkeeping.
            aid = p.get("assembly_id")
            if ev["actor"] != _LOOP_ACTOR:
                problem("call_entered_wrong_actor",
                        assembly_id=aid, at_seq=seq,
                        actor=ev["actor"])
            if binding_problems("call_entered", ev, aid):
                continue
            entered.setdefault(aid, []).append(ev)
        elif t == "RESPONSE_EVIDENCE":
            aid = p.get("assembly_id")
            if ev["actor"] != _LOOP_ACTOR:
                problem("disposition_wrong_actor",
                        assembly_id=aid, at_seq=seq,
                        actor=ev["actor"])
            if binding_problems("disposition", ev, aid):
                continue
            dispositions.setdefault(aid, []).append(ev)
        elif t == "EVIDENCE_CAPTURE_FAILED":
            aid = p.get("assembly_id")
            if ev["actor"] != _LOOP_ACTOR:
                problem("evidence_failure_wrong_actor",
                        assembly_id=aid, at_seq=seq,
                        actor=ev["actor"])
            if aid in evidence_failures:
                problem("evidence_failure_duplicate",
                        assembly_id=aid, at_seq=seq)
            evidence_failures.setdefault(aid, []).append(ev)
            binding_problems("evidence_failure", ev, aid)
        elif t == "TRANSLATION_RECORDED":
            # Native adapter piece (N32/N33): the
            # translation record — the loop machinery's
            # own actor, bound to the standing activation
            # exactly, like its other bookkeeping.
            aid = p.get("assembly_id")
            if ev["actor"] != _LOOP_ACTOR:
                problem("translation_wrong_actor",
                        assembly_id=aid, at_seq=seq,
                        actor=ev["actor"])
            if binding_problems("translation", ev, aid):
                continue
            translations.setdefault(aid, []).append(ev)

    for aid in activated:
        if pinned_bounds_malformed(aid):
            problem("pinned_bounds_malformed", assembly_id=aid,
                    at_seq=activated[aid])
        # Piece A3-CAT, re-examination: the discriminator's
        # third case. A declaration that is present but is
        # not the contract this checker knows is divergent
        # in itself — the record declares a governing
        # contract the checker cannot identify, which is
        # not a historical record and earns no exemption.
        # Reported once, here at the assembly level (as
        # pinned_bounds_malformed is), rather than per
        # iteration: the unknown contract is a property of
        # the assembly, and an activated assembly with no
        # iterations at all must not slip by unreported.
        gen = generated.get(aid)
        contract = gen["payload"].get("catalogue_contract") \
            if gen is not None else None
        if contract is not None and \
                contract not in _GOVERNED_CATALOGUE_CONTRACTS:
            problem("catalogue_contract_unknown",
                    assembly_id=aid, at_seq=activated[aid],
                    catalogue_contract=contract)

    for aid, evs in iterations.items():
        bounds = pinned_bounds(aid)
        ceiling = bounds.get("step_ceiling") \
            if bounds is not None else None
        prev_to = None
        for n, ev in enumerate(evs, start=1):
            p = ev["payload"]
            seq = ev["event_seq"]
            if p.get("iteration") != n:
                problem("iteration_numbering", assembly_id=aid,
                        at_seq=seq, iteration=p.get("iteration"),
                        expected=n)
            if bounds is None:
                problem("iteration_without_pinned_bounds",
                        assembly_id=aid, at_seq=seq)
            else:
                if p.get("step_ceiling") != ceiling or \
                        p.get("deadline_seconds") != bounds.get(
                            "deadline_seconds"):
                    problem("iteration_bounds_mismatch",
                            assembly_id=aid, at_seq=seq)
                if isinstance(ceiling, int) and \
                        not isinstance(ceiling, bool) and \
                        n > ceiling:
                    problem("iteration_over_ceiling",
                            assembly_id=aid, at_seq=seq,
                            ceiling=ceiling)
            if p.get("cursor_to") is None or \
                    p.get("cursor_from") is None or \
                    p["cursor_to"] < p["cursor_from"]:
                problem("cursor_range_invalid", assembly_id=aid,
                        at_seq=seq)
            else:
                # The frozen package's head precedes the event
                # that records it — the iteration event accounts
                # a call made from that snapshot, and itself
                # stands after the head it names.
                if p["cursor_to"] >= seq:
                    problem("cursor_head_not_before_event",
                            assembly_id=aid, at_seq=seq)
                if prev_to is not None and \
                        p["cursor_from"] != prev_to:
                    problem("cursor_chain_broken",
                            assembly_id=aid, at_seq=seq,
                            cursor_from=p["cursor_from"],
                            previous_to=prev_to)
                prev_to = p["cursor_to"]
            # The iteration event is itself presented in the
            # following iteration's range: the next range opens
            # at this package's head and closes no earlier than
            # this event.
            if n < len(evs):
                nxt = evs[n]["payload"]
                if nxt.get("cursor_to") is not None and \
                        nxt["cursor_to"] < seq:
                    problem("iteration_event_not_presented",
                            assembly_id=aid, at_seq=seq)
            # Piece A3-CAT: the catalogue commitment. The
            # assembly's sealed declaration governs: a
            # declared assembly owes both fields on every
            # iteration, and either absent is divergent in
            # itself — stripping the fields cannot manufacture
            # the historical exception, which lives in the
            # assembly record, outside the iteration events.
            # Where a hash stands (declared, or volunteered
            # by an undeclared record), it is verified against
            # the catalogue this checker independently
            # reconstructs from the activation's sealed
            # grants, under its own registry copy at the
            # recorded version. An assembly declaring an
            # UNKNOWN contract is not governed here — what
            # its iterations owe under that contract is
            # unknowable — and it is not historical either:
            # it stands reported once at the assembly level
            # above (catalogue_contract_unknown).
            gen = generated.get(aid)
            declared = gen is not None and \
                gen["payload"].get("catalogue_contract") in \
                _GOVERNED_CATALOGUE_CONTRACTS
            recorded_hash = p.get("catalogue_hash")
            recorded_version = p.get("registry_version")
            if declared and (recorded_hash is None or
                             recorded_version is None):
                problem("catalogue_commitment_missing",
                        assembly_id=aid, at_seq=seq,
                        catalogue_hash=recorded_hash,
                        registry_version=recorded_version)
            elif recorded_hash is not None:
                version = p.get("registry_version")
                if not known_version(version):
                    problem(
                        "catalogue_registry_version_unknown",
                        assembly_id=aid, at_seq=seq,
                        registry_version=version)
                else:
                    gen = generated.get(aid)
                    grants = (gen["payload"].get("grants")
                              if gen is not None else None)
                    # The retrieval contract's assemblies
                    # are catalogued per grant (INDEX 257):
                    # the reconstruction follows the sealed
                    # declaration, as the loop's derivation
                    # follows the doorway's governed test.
                    per_grant = gen is not None and \
                        gen["payload"].get(
                            "catalogue_contract") == \
                        _RETRIEVAL_CONTRACT
                    expected, ground = _derive_catalogue(
                        grants, version, per_grant=per_grant)
                    if expected is None:
                        problem("catalogue_not_derivable",
                                assembly_id=aid, at_seq=seq,
                                detail=ground)
                    elif sha256_hex(canonical(expected)) \
                            != recorded_hash:
                        problem("catalogue_hash_mismatch",
                                assembly_id=aid, at_seq=seq)
        stall = stalls.get(aid)
        if stall is not None:
            for ev in evs:
                if ev["event_seq"] > stall["event_seq"]:
                    problem("iteration_after_stall",
                            assembly_id=aid,
                            at_seq=ev["event_seq"])

    # Dispatch standing by instance, for the stall checks:
    # each dispatch's first outcome position, and whether an
    # uncertain outcome stood (a delayed settlement afterwards
    # is accounting, not activity).
    dispatch_first_outcome = {}
    dispatch_uncertain = {}
    for ev in events:
        p = ev["payload"]
        if ev["type"] == "TOOL_DISPATCHED":
            dispatch_first_outcome.setdefault(
                p.get("dispatch_id"),
                {"instance_id": p.get("instance_id"),
                 "dispatch_seq": ev["event_seq"],
                 "outcome_seq": None})
        elif ev["type"] == "TOOL_OUTCOME":
            d = dispatch_first_outcome.get(p.get("dispatch_id"))
            if d is not None and d["outcome_seq"] is None:
                d["outcome_seq"] = ev["event_seq"]
                if p.get("outcome") == "uncertain":
                    dispatch_uncertain[p.get("dispatch_id")] = \
                        ev["event_seq"]

    for aid, ev in stalls.items():
        seq = ev["event_seq"]
        p = ev["payload"]
        gen = generated.get(aid)
        if gen is None:
            continue  # binding already reported above
        iid = gen["payload"].get("instance_id")
        count = len([e for e in iterations.get(aid, [])
                     if e["event_seq"] < seq])
        if p.get("iterations") != count:
            problem("stall_count_mismatch", assembly_id=aid,
                    at_seq=seq, iterations=p.get("iterations"),
                    counted=count)
        # Accounting closed at the stall: every dispatch of
        # this instance standing by then held an outcome by
        # then. A dispatch whose uncertainty stood by then and
        # settles later is accounted — the late settlement is
        # not a defect and not activity.
        for did, d in dispatch_first_outcome.items():
            if d["instance_id"] != iid:
                continue
            if d["dispatch_seq"] < seq and \
                    (d["outcome_seq"] is None or
                     d["outcome_seq"] > seq):
                problem("stall_before_accounting_closed",
                        assembly_id=aid, at_seq=seq,
                        dispatch_id=did)

    # No instance activity after its activation's stall:
    # requests, dispatches and starts name the instance
    # directly. (Outcomes are handled by the accounting rule
    # above — a first outcome after the stall was already
    # reported there; a delayed settlement of a standing
    # uncertainty is permitted and is not activity.)
    stall_by_instance = {}
    seat_by_instance = {}
    for aid, ev in stalls.items():
        gen = generated.get(aid)
        if gen is not None:
            stall_by_instance[gen["payload"].get(
                "instance_id")] = ev["event_seq"]
            seat_by_instance[gen["payload"].get(
                "instance_id")] = gen["payload"].get("seat")
    for ev in events:
        p = ev["payload"]
        seq = ev["event_seq"]
        iid = p.get("instance_id")
        stall_seq = stall_by_instance.get(iid)
        if stall_seq is None or seq <= stall_seq:
            continue
        if ev["type"] in ("TOOL_REQUESTED", "TOOL_DISPATCHED",
                          "TOOL_STARTED"):
            problem("instance_activity_after_stall",
                    type=ev["type"], instance_id=iid, at_seq=seq)
        elif ev["actor"] == seat_by_instance.get(iid):
            # A record act the seat authored carrying the
            # stalled instance's provenance (Piece A3,
            # correction round 1): the doorway stamps the
            # instance behind the credential on every act it
            # presents, so an instance-authored act after the
            # stall is identifiable — and divergent. The
            # seat's own acts carry no instance provenance and
            # are never flagged for the stall: the seat's
            # other lawful work is not the instance's.
            problem("instance_act_after_stall",
                    type=ev["type"], instance_id=iid, at_seq=seq)

    # --------------------------------------- response evidence
    # Response-evidence piece (WORKER-RESPONSE-EVIDENCE-
    # SCOPE Rev 8): the disposition obligation, reconstructed
    # from the record alone — never from the loop's word.
    # An activation is governed where any of the piece's
    # events stand for it — or where any of its iterations
    # carries the governed mark the loop records in the
    # iteration event itself (build examination, INDEX 314):
    # the mark stands from the activation's first iteration,
    # so a death between the iteration event and the call
    # boundary is governed history, not an escape from
    # reconstruction. A governed activation's every
    # entered iteration owes exactly one disposition,
    # committed before its terminal and before any dispatch
    # from its answer; a missing disposition is an integrity
    # failure, never reinterpreted as a legitimate
    # no-response. The doorway's rules (loop actor only,
    # entered iterations only, exactly one, validated,
    # final, no bypass) are reconstructed here in this
    # checker's own copy: the doorway prevents an invalid
    # history from being extended; this check detects one
    # that nevertheless arrives. Captured dispositions are
    # verified against the filed artifacts in the run
    # directory — hashes recomputed from the stored bytes,
    # the layer identity chain re-derived — and an artifact
    # no committed disposition binds is an orphan: reported,
    # and licensing nothing.
    def artifact_problems(aid, ev, iseq):
        """Verify one captured disposition against its
        filed artifact: the file the run directory holds
        for the iteration, its hash, its binding fields,
        its layer hashes recomputed from its stored bytes,
        and the identity chain L1 → L2 → L3 → L4 → the
        adapter verdict's content hash."""
        p = ev["payload"]
        seq = ev["event_seq"]
        claimed = p.get("artifact_sha256")
        if run_dir is None:
            problem("evidence_artifact_unverifiable",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq)
            return
        path = os.path.join(run_dir, "responses",
                            f"iteration-{iseq}.json")
        if not os.path.exists(path):
            problem("evidence_artifact_missing",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq)
            return
        try:
            with open(path, "rb") as fh:
                data = fh.read()
        except OSError:
            problem("evidence_artifact_unreadable",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq)
            return
        if sha256_hex(data) != claimed:
            problem("evidence_artifact_hash_mismatch",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq)
            return
        try:
            artifact = json.loads(data.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            problem("evidence_artifact_unreadable",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq)
            return
        gen = generated.get(aid)
        if not isinstance(artifact, dict) or \
                artifact.get("assembly_id") != aid or \
                artifact.get("iteration_seq") != iseq or \
                (gen is not None and artifact.get(
                    "instance_id") != gen["payload"].get(
                    "instance_id")) or \
                artifact.get("run_id") != state.get("run_id"):
            problem("evidence_artifact_binding_mismatch",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq)
            return
        layers = artifact.get("layers") or {}
        l1 = layers.get("L1") or {}
        raw = None
        try:
            import base64 as _b64
            raw = _b64.b64decode(l1.get("data_b64") or "",
                                 validate=True)
        except Exception:
            raw = None
        if raw is None:
            problem("evidence_layer_unreadable",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq, layer="L1")
            return
        if len(raw) != l1.get("byte_count") or \
                sha256_hex(raw) != l1.get("sha256"):
            problem("evidence_layer_hash_mismatch",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq, layer="L1")
        # The agreement rule (R7-1): hash subject, retained
        # bytes, completeness and the stop reason describe
        # the same bytes. A prefix hash presented as a
        # whole-body hash while the capture stands
        # incomplete — a total length claimed, a subject
        # other than the observed bytes — is a failure.
        if l1.get("hash_subject") != "observed_bytes" or \
                l1.get("complete") != \
                (l1.get("stop_reason") == "eof") or \
                (l1.get("complete") and
                 l1.get("total_length") != len(raw)) or \
                (not l1.get("complete") and
                 (l1.get("total_length") is not None or
                  l1.get("stop_reason") not in
                  ("capture_limit", "read_failure"))):
            problem("evidence_layer_inconsistent",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq, layer="L1")
        # The ceiling boundary arithmetic (build
        # examination, INDEX 314): the claims are checked,
        # not the helper's behaviour — the duplicated
        # completeness fields must agree, and the stop
        # reason must stand in its one permitted relation
        # to the observed count: eof strictly below the
        # ceiling, capture_limit exactly at it,
        # read_failure below it with the read-error kind
        # the claim names.
        observed = l1.get("byte_count")
        if l1.get("body_complete") != l1.get("complete") or \
                not isinstance(observed, int) or \
                isinstance(observed, bool) or \
                (l1.get("stop_reason") == "eof" and
                 observed >= _EVIDENCE_CAPTURE_CEILING) or \
                (l1.get("stop_reason") == "capture_limit"
                 and observed !=
                 _EVIDENCE_CAPTURE_CEILING) or \
                (l1.get("stop_reason") == "read_failure"
                 and (observed >=
                      _EVIDENCE_CAPTURE_CEILING or
                      not isinstance(
                          l1.get("read_error_kind"), str)
                      or not l1.get("read_error_kind"))):
            problem("evidence_layer_inconsistent",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq, layer="L1",
                    detail="ceiling boundary arithmetic")
        summaries = {"L1": {
            "byte_count": l1.get("byte_count"),
            "sha256": l1.get("sha256"),
            "complete": l1.get("complete"),
            "body_complete": l1.get("body_complete"),
            "hash_subject": l1.get("hash_subject"),
            "total_length": l1.get("total_length"),
            "stop_reason": l1.get("stop_reason"),
            "read_error_kind": l1.get("read_error_kind")}}
        envelope = None
        message = None
        for name in ("L2", "L3"):
            layer = layers.get(name) or {}
            if layer.get("present"):
                obj = layer.get("envelope") \
                    if name == "L2" else layer.get("message")
                if name == "L2":
                    envelope = obj
                else:
                    message = obj
                if not isinstance(obj, dict) or \
                        sha256_hex(canonical(obj)) != \
                        layer.get("canonical_sha256") or \
                        len(canonical(obj)) != \
                        layer.get("canonical_byte_count"):
                    problem("evidence_layer_hash_mismatch",
                            assembly_id=aid, at_seq=seq,
                            iteration_seq=iseq, layer=name)
                summaries[name] = {
                    "present": True,
                    "canonical_sha256":
                        layer.get("canonical_sha256"),
                    "canonical_byte_count":
                        layer.get("canonical_byte_count")}
            else:
                if not layer.get("reason"):
                    problem("evidence_layer_inconsistent",
                            assembly_id=aid, at_seq=seq,
                            iteration_seq=iseq, layer=name)
                summaries[name] = {
                    "present": False,
                    "reason": layer.get("reason")}
        # The identity chain: L3 is the message inside L2,
        # recomputed from the envelope itself.
        if envelope is not None and message is not None:
            chained = None
            try:
                candidate = envelope["choices"][0]["message"]
                if isinstance(candidate, dict):
                    chained = candidate
            except (KeyError, IndexError, TypeError):
                chained = None
            if chained != message:
                problem("evidence_layer_chain_mismatch",
                        assembly_id=aid, at_seq=seq,
                        iteration_seq=iseq, layer="L3")
        l4 = layers.get("L4") or {}
        if l4.get("present"):
            text = l4.get("text")
            if not isinstance(text, str) or \
                    sha256_hex(text.encode("utf-8")) != \
                    l4.get("sha256") or \
                    len(text.encode("utf-8")) != \
                    l4.get("byte_count"):
                problem("evidence_layer_hash_mismatch",
                        assembly_id=aid, at_seq=seq,
                        iteration_seq=iseq, layer="L4")
            if message is not None and \
                    message.get("content") != text:
                problem("evidence_layer_chain_mismatch",
                        assembly_id=aid, at_seq=seq,
                        iteration_seq=iseq, layer="L4")
            summaries["L4"] = {
                "present": True,
                "byte_count": l4.get("byte_count"),
                "sha256": l4.get("sha256")}
        else:
            if not l4.get("reason"):
                problem("evidence_layer_inconsistent",
                        assembly_id=aid, at_seq=seq,
                        iteration_seq=iseq, layer="L4")
            summaries["L4"] = {"present": False,
                               "reason": l4.get("reason")}
        l5 = layers.get("L5") or {}
        adapter_v = l5.get("adapter_verdict")
        loop_v = l5.get("loop_verdict")
        if not isinstance(adapter_v, dict) or \
                adapter_v.get("state") not in (
                    "outcome", "failure", "not_reached") or \
                not isinstance(loop_v, dict) or \
                loop_v.get("state") not in (
                    "validated", "malformed", "not_reached"):
            problem("evidence_verdict_invalid",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq)
        else:
            summaries["L5"] = {
                "adapter_verdict_state": adapter_v["state"],
                "loop_verdict_state": loop_v["state"]}
            # The verdict's content is the artifact's L4:
            # the hash the adapter verdict records is the
            # hash of the exact content it consumed (W-a's
            # identity chain, closed at L5).
            if adapter_v.get("state") in ("outcome",
                                          "failure"):
                expected = l4.get("sha256") \
                    if l4.get("present") else None
                if adapter_v.get("content_hash") != expected:
                    problem(
                        "evidence_verdict_content_mismatch",
                        assembly_id=aid, at_seq=seq,
                        iteration_seq=iseq)
        if p.get("layers") != summaries:
            problem("evidence_summary_mismatch",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq)

    def disposition_problems(aid, ev, iseq, bound):
        """The disposition's own contract (R4-1/R5-1):
        outcome, class and evidence in agreement — the
        doorway's validation, reconstructed."""
        p = ev["payload"]
        seq = ev["event_seq"]
        outcome = p.get("outcome")
        if outcome not in _EVIDENCE_OUTCOMES:
            problem("disposition_outcome_unknown",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq, outcome=outcome)
            return
        if outcome == "captured":
            bound.add(iseq)
            if p.get("failure_class") is not None:
                problem("disposition_class_mismatch",
                        assembly_id=aid, at_seq=seq,
                        iteration_seq=iseq)
            artifact_problems(aid, ev, iseq)
            return
        if p.get("artifact_sha256") is not None:
            problem("disposition_artifact_unexpected",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq)
        if outcome == "no_response":
            se = p.get("seam_evidence")
            if p.get("failure_class") != \
                    _EVIDENCE_NO_RESPONSE_CLASS or \
                    not isinstance(se, dict) or \
                    se.get("phase") != "pre_response" or \
                    se.get("error_kind") not in \
                    _EVIDENCE_PRE_RESPONSE_KINDS or \
                    se.get("observed_status") is not None:
                problem("disposition_evidence_invalid",
                        assembly_id=aid, at_seq=seq,
                        iteration_seq=iseq)
            return
        # unresolved
        failure_class = p.get("failure_class")
        if failure_class == _EVIDENCE_NO_RESPONSE_CLASS:
            problem("disposition_underclaimed",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq)
        elif failure_class not in \
                _EVIDENCE_UNRESOLVED_CLASSES:
            problem("disposition_class_unknown",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq,
                    failure_class=failure_class)
        se = p.get("seam_evidence")
        if not isinstance(se, dict) or not se:
            problem("disposition_evidence_missing",
                    assembly_id=aid, at_seq=seq,
                    iteration_seq=iseq)

    bound_iterations = set()
    governed_aids = set(entered) | set(dispositions) | \
        set(evidence_failures)
    # The governed mark (INDEX 314): an activation any of
    # whose iteration events declares the evidence regime
    # is governed from that iteration onward, even where
    # no call boundary, disposition or failure terminal
    # ever followed it.
    for _aid, _evs in iterations.items():
        if any(ev["payload"].get("evidence_governed")
               for ev in _evs):
            governed_aids.add(_aid)
    event_by_seq = {ev["event_seq"]: ev for ev in events}

    def ts_seconds(ts):
        """An event timestamp as epoch seconds, or None
        where it does not parse — the record's timestamps
        are second-resolution UTC, and the deadline
        condition below is judged with that resolution's
        slack, never more finely than the record speaks."""
        try:
            from datetime import datetime, timezone
            return datetime.strptime(
                ts, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=timezone.utc).timestamp()
        except (ValueError, TypeError):
            return None
    for aid in governed_aids:
        iters = iterations.get(aid, [])
        iter_by_seq = {ev["event_seq"]: ev for ev in iters}
        entered_map = {}
        for ev in entered.get(aid, []):
            p = ev["payload"]
            iseq = p.get("iteration_seq")
            target = iter_by_seq.get(iseq)
            if target is None:
                problem("call_entered_without_iteration",
                        assembly_id=aid, at_seq=ev["event_seq"],
                        iteration_seq=iseq)
                continue
            if p.get("iteration") != \
                    target["payload"].get("iteration"):
                problem("call_entered_iteration_mismatch",
                        assembly_id=aid, at_seq=ev["event_seq"],
                        iteration_seq=iseq)
            if iseq in entered_map:
                problem("call_entered_duplicate",
                        assembly_id=aid, at_seq=ev["event_seq"],
                        iteration_seq=iseq)
            entered_map.setdefault(iseq, ev)
        disp_map = {}
        for ev in dispositions.get(aid, []):
            p = ev["payload"]
            iseq = p.get("iteration_seq")
            if iseq not in iter_by_seq:
                problem("disposition_without_iteration",
                        assembly_id=aid, at_seq=ev["event_seq"],
                        iteration_seq=iseq)
                continue
            if iseq not in entered_map:
                problem("disposition_without_call_entered",
                        assembly_id=aid, at_seq=ev["event_seq"],
                        iteration_seq=iseq)
            if iseq in disp_map:
                problem("disposition_duplicate",
                        assembly_id=aid, at_seq=ev["event_seq"],
                        iteration_seq=iseq)
            disp_map.setdefault(iseq, ev)
        failures_by_iter = {}
        for ev in evidence_failures.get(aid, []):
            p = ev["payload"]
            if p.get("operation") not in \
                    _EVIDENCE_FAILURE_OPERATIONS:
                problem("evidence_failure_operation_unknown",
                        assembly_id=aid, at_seq=ev["event_seq"],
                        operation=p.get("operation"))
            failures_by_iter.setdefault(
                p.get("iteration_seq"), ev)
        stall = stalls.get(aid)
        if stall is not None and \
                stall["payload"].get("terminal_step") is not None \
                and stall["payload"]["terminal_step"] not in \
                _EVIDENCE_PRE_CALL_STEPS:
            problem("terminal_step_unknown", assembly_id=aid,
                    at_seq=stall["event_seq"],
                    terminal_step=stall["payload"]["terminal_step"])
        if stall is not None and \
                stall["payload"].get("terminal_step") in \
                _EVIDENCE_PRE_CALL_STEPS:
            # The claimed condition, not only the name
            # (Rev 4; build examination, INDEX 314): a
            # pre-call step is a claim about why the call
            # was never entered, and the record must bear
            # it out. deadline_at_start claims the
            # activation deadline had passed before the
            # answered iteration could begin: its ground
            # is the deadline's, and its timestamp must
            # not precede the deadline the record itself
            # fixes — the activation event's timestamp
            # plus the pinned deadline_seconds, judged
            # with one second of slack for the timestamps'
            # resolution (a stall stamped clearly before
            # its deadline cannot be a deadline stall;
            # finer judgement than the record's resolution
            # is not claimed). package_construction claims
            # the loop's own construction failure: its
            # ground is runtime_failure and its recorded
            # detail names the package construction
            # failure. (The sequence half of both claims —
            # no call boundary for the answered iteration —
            # is enforced in the per-iteration pass below
            # and by the missing-disposition report.)
            sp = stall["payload"]
            step = sp["terminal_step"]
            condition_ok = True
            if step == "deadline_at_start":
                if sp.get("ground") != "deadline":
                    condition_ok = False
                else:
                    bounds = pinned_bounds(aid)
                    dl = bounds.get("deadline_seconds") \
                        if isinstance(bounds, dict) else None
                    act_ev = event_by_seq.get(
                        activated.get(aid))
                    if act_ev is not None and \
                            isinstance(dl, (int, float)) \
                            and not isinstance(dl, bool):
                        a = ts_seconds(act_ev["ts"])
                        s = ts_seconds(stall["ts"])
                        if a is not None and \
                                s is not None and \
                                s + 1 < a + dl:
                            condition_ok = False
            else:  # package_construction
                detail = sp.get("detail")
                if sp.get("ground") != "runtime_failure" \
                        or not isinstance(detail, str) \
                        or "package construction" \
                        not in detail:
                    condition_ok = False
            if not condition_ok:
                problem("terminal_step_condition_invalid",
                        assembly_id=aid,
                        at_seq=stall["event_seq"],
                        terminal_step=step)
        for idx, iev in enumerate(iters):
            iseq = iev["event_seq"]
            if iseq in entered_map:
                disp = disp_map.get(iseq)
                if disp is None:
                    # The double report (R8-2): an evidence
                    # failure terminal naming this iteration
                    # is recognised below as the instance's
                    # end — and the missing disposition
                    # stands here regardless, an integrity
                    # failure that is never reinterpreted.
                    problem("disposition_missing",
                            assembly_id=aid,
                            at_seq=entered_map[iseq]["event_seq"],
                            iteration_seq=iseq,
                            evidence_failure=iseq in
                            failures_by_iter)
                else:
                    disposition_problems(
                        aid, disp, iseq, bound_iterations)
            elif idx != len(iters) - 1 or stall is None or \
                    stall["payload"].get("terminal_step") not in \
                    _EVIDENCE_PRE_CALL_STEPS:
                # An unentered iteration in a governed
                # activation is lawful only as the final
                # iteration, answered by a stall naming its
                # pre-call step (R4-3/R5-2 mutual
                # exclusivity, reconstructed).
                problem("iteration_without_call_boundary",
                        assembly_id=aid, at_seq=iseq,
                        iteration_seq=iseq)
        # No dispatch without durable evidence: a dispatch
        # of the instance standing after an iteration's
        # call boundary and before its disposition (or
        # with none) is a failure, whatever the doorway
        # admitted.
        gen = generated.get(aid)
        iid = gen["payload"].get("instance_id") \
            if gen is not None else None
        if iid is not None:
            for iseq, cev in entered_map.items():
                disp = disp_map.get(iseq)
                dseq = disp["event_seq"] if disp is not None \
                    else None
                for ev in events:
                    if ev["type"] not in ("TOOL_REQUESTED",
                                          "TOOL_DISPATCHED"):
                        continue
                    if ev["payload"].get("instance_id") != iid:
                        continue
                    if cev["event_seq"] < ev["event_seq"] and \
                            (dseq is None or
                             ev["event_seq"] < dseq):
                        problem("dispatch_before_disposition",
                                assembly_id=aid,
                                at_seq=ev["event_seq"],
                                iteration_seq=iseq)
        # The evidence failure terminal ends the instance:
        # nothing of the instance's stands after it.
        for ev in evidence_failures.get(aid, []):
            fseq = ev["event_seq"]
            for other in events:
                if other["event_seq"] <= fseq:
                    continue
                op = other["payload"]
                if op.get("assembly_id") == aid and \
                        other["type"] in (
                            "LOOP_ITERATION", "CALL_ENTERED",
                            "RESPONSE_EVIDENCE", "LOOP_STALLED",
                            "EVIDENCE_CAPTURE_FAILED"):
                    problem("activity_after_evidence_failure",
                            assembly_id=aid,
                            at_seq=other["event_seq"],
                            type=other["type"])
                elif iid is not None and \
                        op.get("instance_id") == iid and \
                        other["type"] in ("TOOL_REQUESTED",
                                          "TOOL_DISPATCHED",
                                          "TOOL_STARTED"):
                    problem("activity_after_evidence_failure",
                            assembly_id=aid,
                            at_seq=other["event_seq"],
                            type=other["type"])

    # ---------------------------------- native translation
    # Native adapter piece (N33): the translation verdict,
    # reconstructed independently from the record and the
    # filed evidence — never from the loop's word. For
    # every translation record: its iteration binding, its
    # catalogue and artifact bindings, its position (after
    # its iteration's disposition, before any dispatch of
    # the iteration), and its decision set — re-derived
    # from the captured response's own calls, resolved
    # against the catalogue this checker reconstructs from
    # the sealed grants, validated by the checker's own
    # validator — compared field for field. And the
    # record-level doorway invariance (N33 (v)): no
    # dispatch of a native iteration without its
    # translation record standing before it; no record
    # silently lacking adjudication — every presented call
    # answered by exactly its request, dispatched or
    # doorway-refused, in emitted order. An assembly's
    # native mode is read from its sealed acts — the
    # examiner's ASSEMBLY_JUDGED mode decision and the
    # ASSEMBLY_PACKED that carries it (build-examination
    # correction, INDEX 403) — never from an iteration's
    # own fields: every iteration of a natively-sealed
    # assembly owes a boolean disable_tool_validation
    # commitment (BD-1), and a missing commitment cannot
    # conceal the translation obligation.
    def load_artifact(iseq, claimed):
        """The filed artifact for an iteration, read and
        hash-verified against the disposition that binds
        it — or None where it cannot stand (the artifact's
        own defects are reported by the evidence checks
        above; here an unreadable artifact simply leaves
        the translation unverifiable)."""
        if run_dir is None or claimed is None:
            return None
        path = os.path.join(run_dir, "responses",
                            f"iteration-{iseq}.json")
        try:
            with open(path, "rb") as fh:
                data = fh.read()
        except OSError:
            return None
        if sha256_hex(data) != claimed:
            return None
        try:
            return json.loads(data.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None

    def sealed_native(aid):
        """Whether the assembly's sealed mode is native:
        the examiner's judgement and the pack both name
        native. The derivation stands on the sealed acts
        alone — an iteration's fields neither make its
        assembly native nor excuse it from the native
        obligations."""
        return judged_modes.get(aid) == "native" and \
            packed_modes.get(aid) == "native"

    for aid in set(iterations) | set(translations):
        gen = generated.get(aid)
        iid = gen["payload"].get("instance_id") \
            if gen is not None else None
        grants = gen["payload"].get("grants") \
            if gen is not None else None
        per_grant = gen is not None and \
            gen["payload"].get("catalogue_contract") == \
            _RETRIEVAL_CONTRACT
        iters = iterations.get(aid, [])
        iter_by_seq = {ev["event_seq"]: ev for ev in iters}
        disp_by_iter = {}
        for ev in dispositions.get(aid, []):
            disp_by_iter.setdefault(
                ev["payload"].get("iteration_seq"), ev)
        tev_by_iter = {}
        for tev in translations.get(aid, []):
            tiseq = tev["payload"].get("iteration_seq")
            if tiseq not in iter_by_seq:
                problem("translation_without_iteration",
                        assembly_id=aid,
                        at_seq=tev["event_seq"],
                        iteration_seq=tiseq)
            elif tiseq in tev_by_iter:
                problem("translation_duplicate",
                        assembly_id=aid,
                        at_seq=tev["event_seq"],
                        iteration_seq=tiseq)
            else:
                tev_by_iter[tiseq] = tev
        for idx, iev in enumerate(iters):
            iseq = iev["event_seq"]
            ip = iev["payload"]
            window_end = iters[idx + 1]["event_seq"] \
                if idx + 1 < len(iters) else None

            def in_window(seq, after):
                return seq > after and \
                    (window_end is None or seq < window_end)

            tev = tev_by_iter.get(iseq)
            disp = disp_by_iter.get(iseq)
            if sealed_native(aid):
                # Every iteration of a natively-sealed
                # assembly owes its flag commitment
                # (BD-1): absent, the iteration's request
                # state stands uncommitted; present but not
                # a boolean, it commits nothing readable.
                # Either is divergent in itself — and
                # neither conceals the translation
                # obligation judged below.
                if "disable_tool_validation" not in ip:
                    problem(
                        "native_flag_commitment_missing",
                        assembly_id=aid, at_seq=iseq,
                        iteration_seq=iseq)
                elif not isinstance(
                        ip["disable_tool_validation"], bool):
                    problem(
                        "native_flag_commitment_not_boolean",
                        assembly_id=aid, at_seq=iseq,
                        iteration_seq=iseq)
            if tev is None:
                # No record stands for this iteration: a
                # native iteration that nevertheless
                # dispatched, or a captured response whose
                # calls stand unrecorded, diverges.
                if sealed_native(aid) and \
                        iid is not None and any(
                            ev["type"] == "TOOL_REQUESTED"
                            and ev["payload"].get(
                                "instance_id") == iid
                            and in_window(ev["event_seq"], iseq)
                            for ev in events):
                    problem("dispatch_without_translation",
                            assembly_id=aid, at_seq=iseq,
                            iteration_seq=iseq)
                if sealed_native(aid) and \
                        disp is not None and \
                        disp["payload"].get("outcome") == \
                        "captured":
                    # A natively-sealed iteration only: a
                    # text-judged iteration's native-shaped
                    # content is the malformed stall the
                    # evidence checks already account — it
                    # owes no translation record.
                    artifact = load_artifact(
                        iseq, disp["payload"].get(
                            "artifact_sha256"))
                    if artifact is not None:
                        layers = artifact.get("layers") or {}
                        l3 = layers.get("L3") or {}
                        if l3.get("present"):
                            found = _checker_extract_calls(
                                l3.get("message"))
                            if found:
                                problem(
                                    "translation_record_missing",
                                    assembly_id=aid,
                                    at_seq=disp["event_seq"],
                                    iteration_seq=iseq)
                continue
            tp = tev["payload"]
            tseq = tev["event_seq"]
            if not sealed_native(aid):
                problem("translation_without_native_iteration",
                        assembly_id=aid, at_seq=tseq,
                        iteration_seq=iseq)
            if tp.get("iteration") != ip.get("iteration"):
                problem("translation_iteration_mismatch",
                        assembly_id=aid, at_seq=tseq,
                        iteration_seq=iseq)
            # The catalogue binding and reconstruction.
            catalogue = None
            version = tp.get("registry_version")
            if tp.get("catalogue_hash") != \
                    ip.get("catalogue_hash") or \
                    version != ip.get("registry_version"):
                problem("translation_catalogue_mismatch",
                        assembly_id=aid, at_seq=tseq,
                        iteration_seq=iseq)
            elif not known_version(version):
                problem(
                    "translation_catalogue_version_unknown",
                    assembly_id=aid, at_seq=tseq,
                    iteration_seq=iseq,
                    registry_version=version)
            else:
                catalogue, ground = _derive_catalogue(
                    grants, version, per_grant=per_grant)
                if catalogue is None:
                    problem("translation_catalogue_not_derivable",
                            assembly_id=aid, at_seq=tseq,
                            iteration_seq=iseq, detail=ground)
                    catalogue = None
                elif sha256_hex(canonical(catalogue)) != \
                        tp.get("catalogue_hash"):
                    problem("translation_catalogue_mismatch",
                            assembly_id=aid, at_seq=tseq,
                            iteration_seq=iseq)
                    catalogue = None
            # The artifact binding and the record's
            # position: after the disposition, before any
            # dispatch of the iteration.
            if disp is not None:
                if tp.get("artifact_sha256") != \
                        disp["payload"].get("artifact_sha256"):
                    problem("translation_artifact_mismatch",
                            assembly_id=aid, at_seq=tseq,
                            iteration_seq=iseq)
                if tseq <= disp["event_seq"]:
                    problem("translation_before_disposition",
                            assembly_id=aid, at_seq=tseq,
                            iteration_seq=iseq)
            # The decision set, re-derived from the
            # captured response itself.
            if disp is not None and \
                    disp["payload"].get("outcome") == \
                    "captured" and catalogue is not None:
                artifact = load_artifact(
                    iseq, disp["payload"].get(
                        "artifact_sha256"))
                if artifact is None:
                    problem("translation_unverifiable",
                            assembly_id=aid, at_seq=tseq,
                            iteration_seq=iseq)
                else:
                    layers = artifact.get("layers") or {}
                    l3 = layers.get("L3") or {}
                    records = _checker_extract_calls(
                        l3.get("message")) \
                        if l3.get("present") else None
                    if records is None:
                        problem(
                            "translation_reconstruction_mismatch",
                            assembly_id=aid, at_seq=tseq,
                            iteration_seq=iseq,
                            detail="the captured message's "
                                   "calls are malformed as "
                                   "a whole")
                    else:
                        expected = _checker_classify(
                            records, catalogue, iid,
                            ip.get("iteration"))
                        recorded = tp.get("calls")
                        detail = None
                        if not isinstance(recorded, list) or \
                                len(recorded) != len(expected):
                            detail = "the recorded decision " \
                                "set's size differs from " \
                                "the reconstruction's"
                        else:
                            for want, got in zip(expected,
                                                 recorded):
                                if want != got:
                                    field = next(
                                        (k for k in want
                                         if not isinstance(
                                             got, dict)
                                         or got.get(k)
                                         != want[k]),
                                        None)
                                    detail = (
                                        f"call "
                                        f"{want['provider_ordinal']}: "
                                        f"field {field} "
                                        f"differs from the "
                                        f"reconstruction")
                                    break
                        if detail is not None:
                            problem(
                                "translation_reconstruction_mismatch",
                                assembly_id=aid, at_seq=tseq,
                                iteration_seq=iseq,
                                detail=detail)
            # Doorway invariance at the record level: the
            # requests standing after the record, in this
            # iteration's window, are exactly the record's
            # presented calls, in emitted order — and each
            # presented call was adjudicated: dispatched,
            # or refused by the doorway on the record.
            recorded_calls = tp.get("calls") \
                if isinstance(tp.get("calls"), list) else []
            presented = [c.get("loop_request_id")
                         for c in recorded_calls
                         if isinstance(c, dict)
                         and c.get("loop_request_id")]
            window_requests = [
                ev for ev in events
                if ev["type"] == "TOOL_REQUESTED"
                and ev["payload"].get("instance_id") == iid
                and in_window(ev["event_seq"], tseq)]
            if [ev["payload"].get("request_id")
                    for ev in window_requests] != presented:
                problem("translation_dispatch_mismatch",
                        assembly_id=aid, at_seq=tseq,
                        iteration_seq=iseq)
            for rid in presented:
                dispatched = any(
                    ev["type"] == "TOOL_DISPATCHED"
                    and ev["payload"].get("request_id") == rid
                    and in_window(ev["event_seq"], tseq)
                    for ev in events)
                refused = any(
                    ev["type"] == "REJECTION"
                    and ev["payload"].get("request_id") == rid
                    and ev["payload"].get("attempted_type")
                    == "TOOL_DISPATCHED"
                    for ev in events)
                if not dispatched and not refused:
                    problem(
                        "translation_presented_without_adjudication",
                        assembly_id=aid, at_seq=tseq,
                        iteration_seq=iseq, request_id=rid)

    # Orphan artifacts (R2-2): a file in the run's evidence
    # store that no committed captured disposition binds
    # licenses nothing and is reported as what it is.
    if run_dir is not None:
        responses_dir = os.path.join(run_dir, "responses")
        if os.path.isdir(responses_dir):
            for name in sorted(os.listdir(responses_dir)):
                if not name.startswith("iteration-") or \
                        not name.endswith(".json"):
                    continue
                try:
                    orphan_seq = int(
                        name[len("iteration-"):-len(".json")])
                except ValueError:
                    continue
                if orphan_seq not in bound_iterations:
                    problem("evidence_artifact_orphan",
                            iteration_seq=orphan_seq,
                            artifact=name)

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
        checks["loop_correspondence"] = {"result": "not_run"}
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
        checks["loop_correspondence"] = _loop_result(
            events, state,
            run_dir=os.path.dirname(os.path.abspath(path))
            if path else None)
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
