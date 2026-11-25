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
from checker.tool_policy import (EXEC_CATALOGUE_CONTRACT,
                                 EXEC_REGISTRY_VERSION,
                                 REGISTRY_VERSION,
                                 RETRIEVAL_AGGREGATE_CEILING,
                                 RETRIEVAL_REGISTRY_VERSION,
                                 RETRIEVAL_RESULT_CEILING,
                                 RETRIEVAL_TOOLS,
                                 WORKING_SET_CONTENT_BUDGET,
                                 boundary_member,
                                 boundary_member_for_list,
                                 check_ceiling, known_version,
                                 list_authority,
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


# The route whose provider reads tool names in their
# wire form (Ben's ruling, 2026-11-24): the value the
# assembly's own ASSEMBLY_PROBED act records for the
# NVIDIA route. The checker's statement of the wire
# derivation is its own, as its other contracts are
# (N33's independence rule): a canonical name's wire
# form is the name with each dot a dash, derived over
# the reconstructed catalogue's own names.
_CHECKER_WIRE_ROUTE = "nvidia"


def _checker_wire_reverse(catalogue):
    """The checker's own reverse wire map for one
    catalogue: each catalogue name's wire form (each
    dot a dash) back to the canonical name. An emitted
    name stands in this map only where it is the wire
    form of a catalogued tool — the not-guessed-back
    rule, stated independently: no other emitted name
    is translated, and a name outside the map stands
    exactly as emitted for the determination."""
    reverse = {}
    for entry in catalogue:
        canonical = entry["tool"]
        reverse[canonical.replace(".", "-")] = canonical
    return reverse


def _checker_classify(records, catalogue, instance_id,
                      iteration, route=None):
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
    stands. On the wire route (the assembly's recorded
    route, Ben's ruling 2026-11-24) an emitted name that
    is a catalogued tool's wire form is first carried
    back to the canonical name by the checker's own
    derivation above, and the entry keeps both names —
    the canonical name it judges and the wire name as
    emitted — exactly as the recorded entry must stand
    for the two to agree."""
    by_name = {}
    for entry in catalogue:
        by_name.setdefault(entry["tool"], entry)
    wire_reverse = _checker_wire_reverse(catalogue) \
        if route == _CHECKER_WIRE_ROUTE else None
    entries = []
    seen_ids = {}
    presented = 0
    for record in records:
        ordinal = record["provider_ordinal"]
        call_id = record["provider_call_id"]
        emitted = record["name"]
        name = emitted
        wire_name = None
        if wire_reverse is not None and emitted is not None:
            wire_canonical = wire_reverse.get(emitted)
            if wire_canonical is not None:
                name = wire_canonical
                wire_name = emitted
        entry = {
            "provider_ordinal": ordinal,
            "provider_call_id": call_id,
            "name": name,
            "arguments_sha256": None,
            "resolution": "not_reached",
            "validation": "not_reached",
            "validation_constraint": None,
            "refusal_class": None,
            "refusal_detail": None,
            "loop_request_id": None}
        if wire_name is not None:
            entry["wire_name"] = wire_name
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
        if name is None:
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
            by_name, name)
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
    # assembly standing under the retrieval regime has its
    # retrieval dispatches verified against the regime the
    # doorway enforced — the admitting grant under the two
    # authority paths, boundary membership for source
    # paths, retained-content provenance on every result,
    # and the aggregate admission over each package
    # window. Two declarations stand under the regime: the
    # retrieval contract (its dispatches stamped v3) and
    # the exec contract (the combined configuration, INDEX
    # 476 — its dispatches stamped v4, the version the
    # declared contract carries; the version correspondence
    # below reads the declaration itself, not this
    # predicate). An assembly declaring anything else asks
    # none of this: the historical exemption, read from the
    # assembly's own declaration.
    def retrieval_governed(instance_id):
        ev = generated_by_instance.get(instance_id)
        return ev is not None and \
            ev["payload"].get("catalogue_contract") in \
            (_RETRIEVAL_CONTRACT, _EXEC_CONTRACT)

    def working_set_declared(instance_id):
        """Whether the instance's sealed generated record
        declares the working-set contract (the run-3
        correction; the value is this checker's own copy,
        _WORKING_SET_CONTRACT below). Under that
        declaration the freedom-first setup pass's carriage
        honesty stands: a retrieval result may lawfully
        exceed the per-result ceiling (the read returns its
        full content; package growth is governed by the
        working-set budget at carriage, verified in loop
        correspondence), and the aggregate admission does
        not stand — so neither the over-ceiling problem nor
        the aggregate verification below applies to these
        assemblies' dispatches. Provenance verification —
        the retained content's hash, size, authority path —
        applies exactly as it does to every governed
        dispatch: the record's truth does not move."""
        ev = generated_by_instance.get(instance_id)
        return ev is not None and \
            ev["payload"].get("working_set_contract") == \
            _WORKING_SET_CONTRACT

    def declared_contract(instance_id):
        ev = generated_by_instance.get(instance_id)
        return ev["payload"].get("catalogue_contract") \
            if ev is not None else None

    def exec_governed(instance_id):
        ev = generated_by_instance.get(instance_id)
        return ev is not None and \
            ev["payload"].get("catalogue_contract") == \
            _EXEC_CONTRACT

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
        if authority is None and tool == "sandbox.list":
            # The directory form (round ten): the list
            # authority admits the granted directory's
            # own address, the path canonicalised as the
            # ceiling canonicalises it.
            authority = list_authority(path)
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
            # assembly's declared contract — a retrieval
            # assembly's dispatches are governed by v3, and
            # v3 recorded for an assembly that declares no
            # retrieval contract is a stamp nothing issued.
            # The test reads the declaration itself: an
            # exec-declaring assembly stands under the
            # retrieval regime for its retrieval tools (the
            # combined configuration, INDEX 476) but its
            # dispatches are stamped v4, under the exec
            # correspondence below — never v3.
            if declared_contract(iid) == \
                    _RETRIEVAL_CONTRACT and \
                    p.get("registry_version") != \
                    RETRIEVAL_REGISTRY_VERSION:
                problem("dispatch_registry_version_mismatch",
                        dispatch_id=did, at_seq=seq,
                        registry_version=p.get(
                            "registry_version"),
                        expected=RETRIEVAL_REGISTRY_VERSION)
            elif declared_contract(iid) != \
                    _RETRIEVAL_CONTRACT and \
                    p.get("registry_version") == \
                    RETRIEVAL_REGISTRY_VERSION:
                problem("dispatch_registry_version_mismatch",
                        dispatch_id=did, at_seq=seq,
                        registry_version=p.get(
                            "registry_version"),
                        detail="v3 recorded for an assembly "
                               "that declares no retrieval "
                               "contract")
            # The exec regime (gate 4): the same
            # correspondence for v4 — a governed assembly's
            # dispatches are governed by v4, and v4 recorded
            # for an assembly that declares no exec contract
            # is a stamp nothing issued.
            if exec_governed(iid) and \
                    p.get("registry_version") != \
                    EXEC_REGISTRY_VERSION:
                problem("dispatch_registry_version_mismatch",
                        dispatch_id=did, at_seq=seq,
                        registry_version=p.get(
                            "registry_version"),
                        expected=EXEC_REGISTRY_VERSION)
            elif not exec_governed(iid) and \
                    p.get("registry_version") == \
                    EXEC_REGISTRY_VERSION:
                problem("dispatch_registry_version_mismatch",
                        dispatch_id=did, at_seq=seq,
                        registry_version=p.get(
                            "registry_version"),
                        detail="v4 recorded for an assembly "
                               "that declares no exec "
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
                                req_path is not None:
                            if p.get("tool") == "sandbox.list":
                                canon = req_path[:-1] \
                                    if isinstance(
                                        req_path, str) \
                                    and len(req_path) > 1 \
                                    and req_path.endswith(
                                        "/") else req_path
                                member = \
                                    boundary_member_for_list(
                                        pinned_boundary(iid),
                                        canon)
                            else:
                                member = boundary_member(
                                    pinned_boundary(iid),
                                    req_path)
                            if not member:
                                problem(
                                    "retrieval_boundary_"
                                    "violation",
                                    dispatch_id=did,
                                    at_seq=seq,
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
                "working_set": working_set_declared(iid),
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
                    list_authority(req_path) \
                    if p.get("tool") == "sandbox.list" else \
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
                    if not d.get("working_set"):
                        retrieval_outcomes.append(
                            (seq, d["instance_id"], did,
                             RETRIEVAL_RESULT_CEILING))
                elif p.get("outcome") == "failure":
                    if not d.get("working_set"):
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
                                    RETRIEVAL_RESULT_CEILING \
                                    and not d.get(
                                        "working_set"):
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
                        req_result_path = (
                            d.get("parameters") or {}).get(
                                "path")
                        if d.get("tool") == "sandbox.list" \
                                and isinstance(
                                    req_result_path, str) \
                                and len(req_result_path) > 1 \
                                and req_result_path.endswith(
                                    "/"):
                            # The directory form (round
                            # ten): the performer's result
                            # records the canonical address
                            # — the request's path with
                            # exactly one trailing slash
                            # stripped, as the ceiling
                            # canonicalises it.
                            req_result_path = \
                                req_result_path[:-1]
                        if result.get("path") != \
                                req_result_path:
                            problem(
                                "retrieval_authority_mismatch",
                                dispatch_id=did, at_seq=seq,
                                detail="the outcome's path is "
                                       "not the request's "
                                       "path")
                    if not d.get("working_set"):
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
    # Working-set assemblies stand outside this verification
    # (the freedom-first setup pass): their doorway applies
    # no aggregate admission, so their dispatches' outcomes
    # are never collected above and their admissions are
    # skipped below — there is no rule here for the checker
    # to reconstruct, and their carriage is verified in
    # loop correspondence against the working-set budget.
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
        if not d.get("governed") or d.get("working_set") or \
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

# The room-exec contract's declaration value (demonstration
# preparation paper §2/§3.2; gate 4): an assembly declaring
# it is governed by the exec regime — v4 dispatches,
# verified under v4 exactly as a retrieval assembly's are
# under v3 — and, where its grants carry the retrieval
# family (the combined configuration, INDEX 476), by the
# retrieval regime for those tools as well, under the same
# v4 stamp. The governed catalogue contracts are the three
# values together.
_EXEC_CONTRACT = EXEC_CATALOGUE_CONTRACT

_GOVERNED_CATALOGUE_CONTRACTS = (_CATALOGUE_CONTRACT,
                                 _RETRIEVAL_CONTRACT,
                                 _EXEC_CONTRACT)

# The working-set contract's declaration value (the run-3
# correction, examiner's ruling 2026-11-24): an assembly
# declaring it — the combined configuration, generated with
# the execution room and retrieval grants — presents a
# working set in each wake package and owes the set's
# commitment hash on every iteration, verified below by
# this checker's independent reconstruction from the
# recorded outcomes. An assembly carrying no declaration
# predates or stands outside the contract; its iterations
# are exempt identifiably. A declaration naming any other
# value is a contract this checker does not understand.
_WORKING_SET_CONTRACT = "working-set-v1"

# The freshness guard's suspension declaration (Ben's
# ruling, 2026-11-24: "Disable R31 until we need to worry
# about that"; the framework copy stands in tool_policy):
# an assembly declaring it under "freshness_guard" stands
# under the ruling that the doorway's R31 freshness
# rejection does not apply to its instance's answers. This
# checker does not re-derive R31 for single acts — it
# never has; rejections fold as recorded — so its honouring
# of the declaration is the assembly-level validation
# below, in the contracts' third-case shape: the known
# value is lawful, absence is the guard standing as it
# always has, and any other value is a declaration this
# checker does not understand.
_FRESHNESS_GUARD_SUSPENDED = "r31-suspended-v1"

# The delivery declaration's one known route (door scope,
# 2026-11-24; the framework copy stands in tool_policy):
# an assembly declaring it under "delivery" stands under
# the ruling that the worker's contribution is the
# deliverable's arrival and the office files it.
_DELIVERY_ROUTE_CONTRIBUTION = "contribution-v1"


def _working_set_served(tool, result):
    """The served descriptor of one retrieval result, in
    this checker's own reconstruction: the range or window
    actually retrieved, in the result's recorded terms — a
    range read stands as the range it served, never
    expanded; a search stands by its query and totals, its
    passages bound by their canonical hash."""
    if tool == "sandbox.read_range":
        return {"kind": "range",
                "start_line": result.get("start_line"),
                "end_line": result.get("end_line"),
                "byte_start": result.get("byte_start"),
                "byte_end": result.get("byte_end"),
                "heading": result.get("heading")}
    if tool == "sandbox.search":
        return {"kind": "search",
                "query": result.get("query"),
                "total_matches": result.get("total_matches"),
                "returned": result.get("returned"),
                "continuation_offset":
                    result.get("continuation_offset"),
                "passages_sha256": sha256_hex(canonical(
                    result.get("passages")))}
    if tool == "sandbox.list":
        return {"kind": "list",
                "size_bytes": result.get("size_bytes"),
                "line_count": result.get("line_count")}
    if tool == "sandbox.read":
        return {"kind": "whole"}
    return {"kind": "result"}


def _derive_working_set(events, instance_id, head):
    """The working set a package at `head` must have
    presented, reconstructed from the record alone: every
    successful retrieval outcome of the instance at or
    before the head, in outcome order, deduplicated on
    (tool, path, served descriptor, content hash) — the
    first gathering dispatch's identity stands — with the
    aggregate content budget applied in gather order: an
    entry that fits is carried with its content; one that
    does not fit stands by its provenance alone, marked not
    carried. Dispatch identities and tools are read from
    the record's own dispatch events, never from the
    package under examination."""
    dispatch_info = {}
    for ev in events:
        if ev["event_seq"] > head:
            break
        if ev["type"] == "TOOL_DISPATCHED":
            p = ev["payload"]
            dispatch_info[p.get("dispatch_id")] = (
                p.get("instance_id"), p.get("tool"))
    entries = []
    seen = set()
    remaining = WORKING_SET_CONTENT_BUDGET
    carried_bytes = 0
    for ev in events:
        if ev["event_seq"] > head:
            break
        if ev["type"] != "TOOL_OUTCOME":
            continue
        payload = ev["payload"]
        if payload.get("outcome") != "result":
            continue
        info = dispatch_info.get(payload.get("dispatch_id"))
        if info is None or info[0] != instance_id:
            continue
        tool = info[1]
        if tool not in RETRIEVAL_TOOLS:
            continue
        result = payload.get("result")
        if not isinstance(result, dict) or \
                "content" not in result:
            continue
        served = _working_set_served(tool, result)
        key = canonical([tool, result.get("path"), served,
                         result.get("content_sha256")])
        if key in seen:
            continue
        seen.add(key)
        size = result.get("content_bytes")
        if not isinstance(size, int) or \
                isinstance(size, bool):
            size = len(result["content"].encode("utf-8"))
        entry = {
            "tool": tool,
            "path": result.get("path"),
            "authority_path": result.get("authority_path"),
            "content_sha256": result.get("content_sha256"),
            "content_bytes": size,
            "served": served,
            "dispatch_id": payload.get("dispatch_id"),
            "request_id": payload.get("request_id"),
            "outcome_event_seq": ev["event_seq"],
        }
        if size <= remaining:
            entry["content"] = result["content"]
            entry["content_carried"] = True
            remaining -= size
            carried_bytes += size
        else:
            entry["content_carried"] = False
            entry["not_carried_reason"] = \
                "working_set_budget"
        entries.append(entry)
    return {
        "budget_bytes": WORKING_SET_CONTENT_BUDGET,
        "content_bytes": carried_bytes,
        "entries": entries,
    }


def _working_set_hash(working_set):
    """The working set's commitment, as this checker
    computes it: SHA-256 over the canonical form of the
    reconstructed set's budget and entries."""
    return sha256_hex(canonical({
        "budget_bytes": working_set["budget_bytes"],
        "entries": working_set["entries"]}))


# Staged onboarding (INDEX 544): the presentation
# contract's name, as the generated record declares it
# and this checker reads it (the framework copy stands in
# tool_policy). An assembly declaring it owes a
# presentation commitment hash on every iteration,
# verified below by this checker's independent
# reconstruction of the staged package from the record.
# An assembly carrying no declaration predates or stands
# outside the contract; its iterations are exempt
# identifiably. A declaration naming any other value is a
# contract this checker does not understand.
_PRESENTATION_CONTRACT = "staged-onboarding-v1"
# The pointer-rule successor (INDEX 568): under this
# contract a gathered entry's content is presented
# exactly once, in the first wake after its gather, as
# part of that wake's newest results, and stands as a
# pointer in every later package; the staged core's
# reconstruction below derives the pointer form whole
# and the iteration's commitment binds it verbatim
# beside the record set's hash. v1's meaning under its
# name does not change; a declaration naming either
# contract is governed, any other value is unknown.
_PRESENTATION_CONTRACT_V2 = "staged-onboarding-v2"
# The process-tree successor (the room rebuild, Ben's
# "Make it so" 2026-11-25): one opening package, then
# one package per step of the office-authored process
# tree sealed in the case — node states, the current
# step, his journal and at most one step's fresh
# content, all derived from the record alone, with the
# step gate's corrections answered from their events.
# Its core's reconstruction stands below beside the
# staged one's; v1's and v2's meanings under their
# names do not change.
_PRESENTATION_CONTRACT_V3 = "process-tree-v1"
_PRESENTATION_STAGES = ("memory", "case", "files", "task",
                        "dashboard")
# The staged presentation's wording — this checker's own
# copies, as its other contracts' copies stand here; the
# framework's stand in loop.py.
_STAGED_COVER_FIRST = (
    "You are {seat}, the {role} in this office, "
    "assembled for one job. The shape of the work here "
    "is simple: you are woken with a package, you act, "
    "and the record keeps everything. Your onboarding "
    "comes in stages — first your memory, then your "
    "case, then your files, then your task — so nothing "
    "is dumped on you all at once. The job: {headline}. "
    "The deliverable: {deliverable}.")
_STAGED_MEMORY_INTRO = (
    "This is your memory — what this role knows from "
    "before you were woken: how the work has gone, what "
    "the office has told you, and the routes to what you "
    "need. It is presented to you as your own knowledge "
    "because in this role it is yours to work from; the "
    "office keeps its own honest account of where each "
    "item came from, behind the scenes. If the list "
    "below is empty, this role carries no standing "
    "memory yet.")
_STAGED_FILES_INTRO = (
    "Your briefcase holds the job's files — the files "
    "your task needs. What stands below are pointers, "
    "not contents: each file's address, what it is, "
    "and its way in — the exact call that pulls it, "
    "naming a tool you hold. The contents are yours "
    "to pull when the work needs them, through the "
    "doorway tools (sandbox.list shows a file's size, "
    "line count and headings — or, on a directory "
    "such as sources itself, the entries standing in "
    "it; sandbox.read pulls a whole file) or the "
    "shell in your room. That is "
    "how the briefcase works: what you pull is "
    "carried forward in front of you at later wakes, "
    "so you never need to pull the same thing twice. "
    "Your tools are offered from this wake on. Below "
    "the map, one call stands worked as an example — "
    "a real call the office made on the first file "
    "while your briefcase was being stocked, with "
    "what came back; yours will look like this.")
_STAGED_FILES_INTRO_NO_EXAMPLE = (
    "Your briefcase holds the job's files — the files "
    "your task needs. What stands below are pointers, "
    "not contents: each file's address, what it is, "
    "and its way in — the exact call that pulls it, "
    "naming a tool you hold. The contents are yours "
    "to pull when the work needs them, through the "
    "doorway tools (sandbox.list shows a file's size, "
    "line count and headings — or, on a directory "
    "such as sources itself, the entries standing in "
    "it; sandbox.read pulls a whole file) or the "
    "shell in your room. That is "
    "how the briefcase works: what you pull is "
    "carried forward in front of you at later wakes, "
    "so you never need to pull the same thing twice. "
    "Your tools are offered from this wake on — if "
    "you want, list a file from the map now and see "
    "its shape standing.")
# The pointer-rule successor's wording — this
# checker's own copies of the loop's v2 texts (INDEX
# 568): the files-stage introductions telling the
# pointer truth, the dashboard direction naming
# pointers, the pointer component's note, and the one
# plain sentence each pointer entry carries.
_STAGED_FILES_INTRO_V2 = (
    "Your briefcase holds the job's files — the files "
    "your task needs. What stands below are pointers, "
    "not contents: each file's address, what it is, "
    "and its way in — the exact call that pulls it, "
    "naming a tool you hold. The contents are yours "
    "to pull when the work needs them, through the "
    "doorway tools (sandbox.list shows a file's size, "
    "line count and headings — or, on a directory "
    "such as sources itself, the entries standing in "
    "it; sandbox.read pulls a whole file) or the "
    "shell in your room. That is "
    "how the briefcase works: what you pull is shown "
    "to you whole in the wake right after you pull "
    "it, and after that it stands in your working set "
    "as a pointer — its address, its size, and the "
    "office's record of your having pulled it — so "
    "pull it again whenever you need its words in "
    "front of you. "
    "Your tools are offered from this wake on. Below "
    "the map, one call stands worked as an example — "
    "a real call the office made on one of the files "
    "in the map while your briefcase was being "
    "stocked, with what came back; yours will look "
    "like this.")
_STAGED_FILES_INTRO_NO_EXAMPLE_V2 = (
    "Your briefcase holds the job's files — the files "
    "your task needs. What stands below are pointers, "
    "not contents: each file's address, what it is, "
    "and its way in — the exact call that pulls it, "
    "naming a tool you hold. The contents are yours "
    "to pull when the work needs them, through the "
    "doorway tools (sandbox.list shows a file's size, "
    "line count and headings — or, on a directory "
    "such as sources itself, the entries standing in "
    "it; sandbox.read pulls a whole file) or the "
    "shell in your room. That is "
    "how the briefcase works: what you pull is shown "
    "to you whole in the wake right after you pull "
    "it, and after that it stands in your working set "
    "as a pointer — its address, its size, and the "
    "office's record of your having pulled it — so "
    "pull it again whenever you need its words in "
    "front of you. "
    "Your tools are offered from this wake on — if "
    "you want, list a file from the map now and see "
    "its shape standing.")
_STAGED_EXAMPLE_LABEL = (
    "A worked example — the office's own call, made "
    "while your briefcase was stocked: a real call, "
    "and what came back. It is an example of your "
    "next move, not your work and not material you "
    "have gathered; the file's contents are still "
    "yours to pull.")
# The room-proof line (the calibration): this
# checker's copy of the loop's line standing beside
# the worked example under the pointer-rule
# contract.
_STAGED_EXAMPLE_PROOF = (
    "This example is a real call the office made in "
    "your room, on a file from your own briefcase; "
    "your tools answer the same way when you call "
    "them in the shape shown.")
_STAGED_SNAPSHOT_NOTE = (
    "Where you stand: before you were woken, an "
    "opening conversation settled what stands below. "
    "It is recorded work state — what was settled "
    "before you arrived — not your memory; your "
    "memory follows it.")
_STAGED_SNAPSHOT_EMPTY = (
    "Where you stand: nothing was settled before "
    "this wake — no settled results of an opening "
    "conversation stand in your case. What precedes "
    "you is this role's standing memory, below.")
_STAGED_STAGE_GATE_INSTRUCTION = (
    "Nothing was filed. Delivery opens with your "
    "task: your task has not been presented yet — "
    "it arrives at the fourth wake of your "
    "onboarding (stage 4: your task), and from "
    "that wake on your contribution is the "
    "deliverable's arrival and the office files "
    "it. What is needed until then is the work "
    "itself: walk the stages as they come, pull "
    "what your task needs, and contribute once "
    "your task stands in front of you. The text "
    "you sent stands in the record, set aside "
    "unfiled; if it is the brief you mean to "
    "deliver, send it again after your task has "
    "been presented.")
_STAGED_JOURNAL_POINTER = (
    "your journal — your notebook: notes, decisions, "
    "where you left off. Yours to write and rewrite; "
    "orientation, not record and not memory. Its "
    "contents are not carried in your packages — pull "
    "it when you want it.")
# The journal's contract under the pointer-rule
# successor (the calibration): this checker's copy of
# the loop's v2 note — the directive (log each read
# file's name and key points, one or two plain
# lines), the office reading the journal at every
# wake to resume him, the director's audit, and the
# truth that nothing parses it.
_STAGED_JOURNAL_POINTER_V2 = (
    "your journal — your notebook: notes, decisions, "
    "where you left off. Yours to write and rewrite; "
    "orientation, not record and not memory. Keep it "
    "as you work: after each file you read, log its "
    "name and the key points you took from it, in "
    "one or two plain lines. The office reads your "
    "journal at every wake to resume you, and the "
    "director may audit it; nothing parses it — it "
    "is read as you wrote it. Its contents are not "
    "carried in your packages — pull it when you "
    "want it.")
# The delivery-evidence gate (round ten, INDEX 552):
# this checker's copies of the correction's wording and
# of the standing computation — the framework's stand in
# loop.py. The correction is re-derived from the gate
# event's payload and the catalogue; the standing
# computation is re-derived from the recorded dispatches
# and outcomes alone.
_STAGED_EVIDENCE_GATE_WHAT_ARRIVED = (
    "a contribution, offered as your delivery, before "
    "the evidence your case names for a delivery stood "
    "gathered in front of you")
_STAGED_EVIDENCE_GATE_INSTRUCTION_HEAD = (
    "Nothing was filed. Your case names the evidence "
    "a delivery must rest on: the whole content of "
    "each named file must stand gathered in your "
    "working set before your contribution can be "
    "filed as the deliverable. Still missing:")
_STAGED_EVIDENCE_GATE_INSTRUCTION_TAIL = (
    "Gather what is missing, then offer your "
    "contribution again. Listing a file shows its "
    "shape, not its contents — a listing does not "
    "gather it; pull the whole file, or pull ranges "
    "that together cover the whole file. The text "
    "you sent stands in the record, set aside "
    "unfiled.")


def _evidence_gate_instruction(catalogue, missing):
    lines = [_STAGED_EVIDENCE_GATE_INSTRUCTION_HEAD]
    for address in missing:
        way = _staged_access_way(catalogue, address)
        if way is not None:
            lines.append(
                f"- {address}: {way['tool']} on {address} "
                f"pulls the whole file.")
        else:
            lines.append(
                f"- {address}: no tool you hold reaches "
                f"it — say so in your yield, and the "
                f"office will stock a route.")
    lines.append(_STAGED_EVIDENCE_GATE_INSTRUCTION_TAIL)
    return "\n".join(lines)


# The delivery-length gate (the third gate, INDEX
# 557): this checker's copies of the correction's
# wording and of the task stage's floor statement —
# the framework's stand in loop.py. The correction is
# re-derived from the gate event's payload alone; the
# count it names is re-derived from the recorded
# contribution text itself.
def _length_gate_what_arrived(word_count):
    return (f"a contribution of {word_count} words, "
            f"offered as your delivery")


_STAGED_LENGTH_GATE_INSTRUCTION = (
    "Nothing was filed. Your contribution arrived at "
    "{word_count} words; the deliverable must run to "
    "at least {min_words} words — the target stands "
    "at about 600 words, and the floor is a minimum, "
    "not the aim. Write to the full length from the "
    "sources you have gathered, then offer your "
    "contribution again. The text you sent stands in "
    "the record, set aside unfiled.")
_STAGED_TASK_FLOOR_STATEMENT = (
    "The deliverable must run to at least {min_words} "
    "words. A contribution shorter than that is set "
    "aside unfiled, and you will be told the count "
    "yours arrived with.")
# The task stage's deliverable statement under the
# pointer-rule successor (the calibration): this
# checker's copy of the loop's v2 statement — the
# target and the floor standing where he plans.
_STAGED_TASK_FLOOR_STATEMENT_V2 = (
    "The brief runs to about 600 words, and the "
    "door will not file a brief under {min_words} "
    "words. A contribution shorter than that is set "
    "aside unfiled, and you will be told the count "
    "yours arrived with.")


# The tool-shape gate (the calibration): this
# checker's copies of the correction's wording — the
# framework's stand in loop.py. The correction is
# re-derived from the gate event's payload (the tool
# the failed generation named) and the pinned case's
# first glossary address, exactly as the loop derived
# it when it stashed the correction.
def _tool_shape_what_arrived(tool_name):
    return (f"a native tool call — your answer named "
            f"{tool_name} in the provider's own "
            f"tool-call shape, and the provider refused "
            f"the whole answer for it (its refusal "
            f"carries the code tool_use_failed). No "
            f"tool ran, and nothing from that answer "
            f"was carried out")


_TOOL_SHAPE_GATE_WHAT_IS_NEEDED = (
    "In this room your tools are called in the text "
    "shape: your answer is one JSON object whose "
    "outcome is \"tool_requests\", with a requests "
    "list naming each call — the tool's name and its "
    "parameters — as the example shows. Only calls "
    "in that shape reach your tools; a native tool "
    "call cannot be carried out here.")
_TOOL_SHAPE_GATE_INSTRUCTION = (
    "Nothing was filed, and nothing was lost: your "
    "gathered work stands as it stood. Make the call "
    "again in the text shape and carry on with the "
    "job. The refusal cost this one step and nothing "
    "else.")


def _tool_shape_gate_correction(tool_name,
                                example_address):
    return {
        "what_arrived": _tool_shape_what_arrived(
            tool_name),
        "what_is_needed": _TOOL_SHAPE_GATE_WHAT_IS_NEEDED,
        "example": {
            "outcome": "tool_requests",
            "requests": [{
                "tool": "sandbox.read",
                "parameters": {"path": example_address}}]},
        "instruction": _TOOL_SHAPE_GATE_INSTRUCTION}


def _evidence_address_stands(entries, requested, address):
    """Whether one named address's whole content stands
    in the reconstructed working set: a carried whole
    read of it, or carried line ranges together covering
    the file's whole line range — the total established
    by a listing outcome's recorded line count for the
    address, or by a range request whose asked end_line
    the performer clamped to the served end. Byte-window
    ranges, listings, searches, and entries standing by
    provenance alone never count; container.exec outcomes
    never enter the working set, so no exec carriage can
    stand — the record carries no attribution of room
    stdout to a named address, and none is invented."""
    mine = [e for e in entries
            if e.get("path") == address]
    for entry in mine:
        if entry.get("tool") == "sandbox.read" and \
                entry.get("content_carried"):
            return True
    total = None
    for entry in mine:
        if entry.get("tool") == "sandbox.list":
            line_count = (entry.get("served") or {}).get(
                "line_count")
            if isinstance(line_count, int) and \
                    not isinstance(line_count, bool):
                total = line_count
    intervals = []
    for entry in mine:
        if entry.get("tool") != "sandbox.read_range" or \
                not entry.get("content_carried"):
            continue
        served = entry.get("served") or {}
        if served.get("byte_start") is not None:
            continue
        start = served.get("start_line")
        end = served.get("end_line")
        if not isinstance(start, int) or \
                isinstance(start, bool) or \
                not isinstance(end, int) or \
                isinstance(end, bool):
            continue
        intervals.append((start, end))
        if total is None:
            asked = (requested.get(
                entry.get("request_id")) or {}).get(
                    "end_line")
            if isinstance(asked, int) and \
                    not isinstance(asked, bool) and \
                    asked > end:
                total = end
    if total is None or total < 1 or not intervals:
        return False
    covered_to = 0
    for start, end in sorted(intervals):
        if start > covered_to + 1:
            return False
        covered_to = max(covered_to, end)
        if covered_to >= total:
            return True
    return covered_to >= total


def _delivery_evidence_missing(events, instance_id, head,
                               addresses):
    """The declared delivery evidence that does not
    stand at `head`, in the declaration's own order,
    reconstructed from the record alone: the working set
    at the head, weighed address by address, with the
    requested parameters read from the record's
    TOOL_REQUESTED events."""
    working_set = _derive_working_set(
        events, instance_id, head)
    requested = {}
    for ev in events:
        if ev["event_seq"] > head:
            break
        if ev["type"] != "TOOL_REQUESTED":
            continue
        payload = ev["payload"]
        parameters = payload.get("parameters")
        if isinstance(parameters, dict):
            requested[payload.get("request_id")] = parameters
    return [address for address in addresses
            if not _evidence_address_stands(
                working_set["entries"], requested, address)]
_STAGED_DIRECTIONS = {
    "memory": (
        "Onboarding stage 1 of 4: your memory. Nothing "
        "is asked of you at this wake but to take it "
        "in — no work is produced during onboarding. "
        "Answer {\"outcome\": \"acknowledge\"} and your "
        "next wake brings your case."),
    "case": (
        "Onboarding stage 2 of 4: your case — the frame "
        "of the job you were assembled for. Take it in; "
        "no work is produced during onboarding. Answer "
        "{\"outcome\": \"acknowledge\"} and your next "
        "wake brings your files."),
    "files": (
        "Onboarding stage 3 of 4: your files. These are "
        "pointers to pull from, not the files "
        "themselves. Your task arrives at the next "
        "wake."),
    "task": (
        "Onboarding stage 4 of 4: your task. This is "
        "the work. Your tool menu below is grouped by "
        "the job's phases — Gather, Compose, Deliver. "
        "Begin."),
    "dashboard": (
        "Your onboarding is complete. This is your "
        "dashboard wake: where you stand, your newest "
        "results, everything you have gathered so far, "
        "and pointers back into your briefcase."),
}
_STAGED_DIRECTIONS_V2 = {
    "memory": _STAGED_DIRECTIONS["memory"],
    "case": _STAGED_DIRECTIONS["case"],
    "files": _STAGED_DIRECTIONS["files"],
    "task": _STAGED_DIRECTIONS["task"],
    "dashboard": (
        "Your onboarding is complete. This is your "
        "dashboard wake: where you stand, your newest "
        "results, pointers to everything you have "
        "gathered so far, and pointers back into your "
        "briefcase."),
}
_WORKING_SET_POINTER_NOTE = (
    "What you have gathered so far, standing as "
    "pointers: each entry's content was shown to you "
    "whole in the wake right after you gathered it, "
    "and the material itself stands in your room at "
    "its address — pull it again when you need its "
    "words in front of you. The office's record of "
    "what you have read stands in full behind these "
    "pointers; an entry marked content_carried: false "
    "did not fit the working-set budget when it was "
    "gathered, and its provenance stands here the "
    "same way.")
_STAGED_POINTER_SENTENCE = (
    "It stands in your room at {path} — pull it "
    "again with {tool} on that address when you need "
    "its words in front of you; the office's record "
    "of your having read it stands regardless of "
    "what any later package carries.")
_STAGED_POINTER_SENTENCE_NO_WAY = (
    "It stands in your room at {path}; no tool you "
    "hold pulls it directly, and the office's record "
    "of your having read it stands regardless of "
    "what any later package carries.")
_STAGED_GATE_INSTRUCTION = (
    "Your previous response could not be read: it "
    "arrived as a contribution, but its envelope was "
    "not valid JSON, so nothing in it was accepted. "
    "Resend the contribution plainly, as one JSON "
    "object and nothing else: {\"outcome\": "
    "\"contribute\", \"text\": \"<your contribution>\"}.")


def _staged_stage(iteration):
    """The onboarding stage a wake presents, as a pure
    function of its 1-based iteration number — this
    checker's copy of the loop's derivation."""
    if 1 <= iteration <= 4:
        return _PRESENTATION_STAGES[iteration - 1]
    return _PRESENTATION_STAGES[4]


def _staged_snapshot(content):
    """Where the worker stands at his first wake —
    this checker's copy of the loop's derivation
    (INDEX 549): the case's opening record's settled
    results, verbatim, where they stand; the plain
    empty statement where none stand."""
    opening = (content or {}).get("opening")
    settled = opening.get("settled") \
        if isinstance(opening, dict) else None
    if isinstance(settled, list) and settled and \
            all(isinstance(item, str) for item in settled):
        return {"note": _STAGED_SNAPSHOT_NOTE,
                "settled": copy.deepcopy(settled)}
    return {"note": _STAGED_SNAPSHOT_EMPTY, "settled": []}


def _staged_access_way(catalogue, address):
    """A needed file's way in — this checker's copy
    of the loop's derivation (INDEX 549): the
    concrete call naming a granted tool over the
    file's own address, read from the catalogue the
    package itself offers."""
    if not isinstance(address, str):
        return None
    for tool in ("sandbox.read", "sandbox.list"):
        for entry in catalogue or []:
            if not isinstance(entry, dict) or \
                    entry.get("tool") != tool:
                continue
            ceiling = entry.get("scope_ceiling")
            prefix = ceiling.get("path_prefix") \
                if isinstance(ceiling, dict) else None
            if isinstance(prefix, str) and (
                    address == prefix
                    or address.startswith(prefix + "/")):
                return {"tool": tool,
                        "parameters": {"path": address}}
    return None


def _worked_example_well_formed(example, contract=None):
    """The sealed worked example's shape — this
    checker's copy of the loop's honour rule (INDEX
    548): the demonstration call and the performer's
    whole result, internally consistent. A seal
    standing in any other shape is presented by no
    derivation and reported at the assembly level.
    The shape is the sealed contract's own (the
    calibration): under the first contract, the
    listing call and its result; under the
    pointer-rule successor, the read call and the
    read performer's whole result."""
    if not isinstance(example, dict) or \
            set(example) != {"tool", "path", "result"}:
        return False
    if contract in (_PRESENTATION_CONTRACT_V2,
                    _PRESENTATION_CONTRACT_V3):
        return _worked_example_read_well_formed(example)
    if example.get("tool") != "sandbox.list":
        return False
    path = example.get("path")
    result = example.get("result")
    if not isinstance(path, str) or not path or \
            not isinstance(result, dict) or \
            set(result) != {"path", "content",
                            "content_bytes",
                            "content_sha256",
                            "authority_path", "size_bytes",
                            "line_count"}:
        return False
    content = result.get("content")
    return not (
        result.get("path") != path or
        not isinstance(content, str) or
        result.get("content_bytes") != len(
            content.encode("utf-8")) or
        result.get("content_sha256") != hashlib.sha256(
            content.encode("utf-8")).hexdigest() or
        result.get("authority_path") not in (
            "source", "scratch") or
        not isinstance(result.get("size_bytes"), int) or
        isinstance(result.get("size_bytes"), bool) or
        result.get("size_bytes") < 0 or
        not isinstance(result.get("line_count"), int) or
        isinstance(result.get("line_count"), bool) or
        result.get("line_count") < 0)


def _worked_example_read_well_formed(example):
    """The read demonstration's shape — this checker's
    copy of the loop's read honour rule (the
    calibration): a sandbox.read call and the read
    performer's whole result under the working-set
    contract, internally consistent (its hash and
    byte count its content's, its path the call's)."""
    if example.get("tool") != "sandbox.read":
        return False
    path = example.get("path")
    result = example.get("result")
    if not isinstance(path, str) or not path or \
            not isinstance(result, dict) or \
            set(result) != {"path", "content",
                            "content_bytes",
                            "content_sha256",
                            "authority_path"}:
        return False
    content = result.get("content")
    return not (
        result.get("path") != path or
        not isinstance(content, str) or
        result.get("content_bytes") != len(
            content.encode("utf-8")) or
        result.get("content_sha256") != hashlib.sha256(
            content.encode("utf-8")).hexdigest() or
        result.get("authority_path") not in (
            "source", "scratch"))


def _stage_gate_what_arrived(stage):
    """What the stage gate's correction says arrived
    — this checker's copy of the loop's text (INDEX
    548)."""
    return (f"a contribution, offered at the {stage} "
            f"stage of your onboarding, before your "
            f"task had been presented")


def _staged_tool_purpose(tool, description):
    """This checker's copy of the loop's one-line tool
    purpose derivation."""
    first = (description or "").split(". ")[0].strip()
    if first and not first.endswith("."):
        first += "."
    if tool == "container.exec":
        first = (first + " A shell command there is a "
                 "first-class way to work: cat <path> "
                 "reads a whole file at once, and "
                 "commands can copy, combine and write "
                 "files in your scratch.").strip()
    return first


def _staged_tool_list(catalogue):
    """This checker's copy of the loop's flat tool-list
    derivation: one entry per catalogue entry."""
    out = []
    for entry in catalogue or []:
        ceiling = entry.get("scope_ceiling")
        out.append({
            "tool": entry.get("tool"),
            "scope": ceiling.get("path_prefix")
            if isinstance(ceiling, dict) else None,
            "purpose": _staged_tool_purpose(
                entry.get("tool"),
                entry.get("description")),
        })
    return out


def _staged_menu_example(phase, tool, scope):
    """This checker's copy of the loop's tool-menu
    example derivation."""
    if tool == "container.exec":
        if phase == "Gather":
            return ("e.g. the command [\"cat\", "
                    "\"<path>\"] reads that whole file "
                    "at once.")
        return ("e.g. commands in your room can copy "
                "and combine files, and write drafts "
                "in your scratch.")
    if tool == "sandbox.write":
        return ("e.g. sandbox.write with a path under "
                "your scratch and the text to store "
                "writes that file.")
    where = f"{scope}/" if scope else ""
    if tool == "sandbox.list":
        return (f"e.g. sandbox.list on {where} lists "
                f"what stands there — each file's size "
                f"and line count.")
    if tool == "sandbox.search":
        return (f"e.g. sandbox.search in {where} for a "
                f"phrase returns the passages that "
                f"carry it, with their file and line "
                f"numbers.")
    if tool == "sandbox.read_range":
        return (f"e.g. sandbox.read_range on a file in "
                f"{where}, lines 1 to 4, pulls just "
                f"those lines.")
    if tool == "sandbox.read":
        return (f"e.g. sandbox.read on a file in "
                f"{where} pulls the whole file at "
                f"once.")
    return None


def _staged_tool_menu(catalogue, deliverable=None):
    """This checker's copy of the loop's phase-grouped
    tool-menu derivation (Gather, Compose, Deliver)."""
    flat = _staged_tool_list(catalogue)
    by_pair = {}
    for entry in flat:
        by_pair.setdefault(
            (entry["tool"], entry["scope"]), entry)

    def pick(tool, scope, phase, purpose_suffix=None):
        base = by_pair.get((tool, scope))
        if base is None:
            return None
        entry = {"tool": tool, "scope": scope,
                 "purpose": base["purpose"]}
        if purpose_suffix:
            entry["purpose"] = (
                entry["purpose"] + " " + purpose_suffix)
        example = _staged_menu_example(phase, tool, scope)
        if example:
            entry["example"] = example
        return entry

    gather = []
    compose = []
    deliver = []
    for entry in flat:
        tool, scope = entry["tool"], entry["scope"]
        if tool in RETRIEVAL_TOOLS or \
                tool == "container.exec":
            picked = pick(tool, scope, "Gather")
            if picked is not None:
                gather.append(picked)
        if tool in ("container.exec", "sandbox.write"):
            picked = pick(tool, scope, "Compose")
            if picked is not None:
                compose.append(picked)
        if tool == "sandbox.write":
            suffix = None
            if deliverable:
                suffix = ("This is the deliverable "
                          f"door: the deliverable is "
                          f"{deliverable}.")
            picked = pick(tool, scope, "Deliver",
                          purpose_suffix=suffix)
            if picked is not None:
                deliver.append(picked)
    groups = []
    if gather:
        groups.append({"phase": "Gather",
                       "tools": gather})
    if compose:
        groups.append({"phase": "Compose",
                       "tools": compose})
    if deliver:
        groups.append({
            "phase": "Deliver",
            "tools": deliver,
            "note": "When the deliverable stands "
                    "written, answer with the yield "
                    "outcome — the file standing is "
                    "the completed assignment."})
    return groups


def _staged_relevant(ev, instance_id, seat, case_id,
                     activated_seq):
    """Whether an event belongs in the activation's
    delta — this checker's copy of the loop's relevance
    rule."""
    p = ev["payload"]
    if p.get("instance_id") == instance_id:
        return True
    if ev["type"] == "REJECTION" and \
            p.get("seat") == seat and \
            ev["event_seq"] > activated_seq:
        return True
    if ev["actor"] == seat and \
            ev["event_seq"] > activated_seq:
        return True
    if ev["type"].startswith("CASE_") and \
            p.get("case_id") == case_id:
        return True
    return False


def _staged_tool_result_refs(events, instance_id, seat,
                             case_id, activated_seq,
                             cursor_from, cursor_to):
    """The staged package's tool results as the record
    commits them: their identities alone (dispatch,
    request, outcome, event), in the order the package
    presented them — reconstructed here exactly as the
    loop's carriage constructs them: the delta's outcome
    events in record order; where any translation record
    stands in the snapshot, the bound entries first in
    provider call order (translation record, then
    ordinal), the translation refusals and the doorway's
    refusals of bound calls among them, and any unbound
    entry after, in record order."""
    delta = [ev for ev in events
             if cursor_from < ev["event_seq"] <= cursor_to
             and _staged_relevant(ev, instance_id, seat,
                                  case_id, activated_seq)]
    entries = []
    for ev in delta:
        if ev["type"] != "TOOL_OUTCOME":
            continue
        p = ev["payload"]
        entries.append({
            "dispatch_id": p.get("dispatch_id"),
            "request_id": p.get("request_id"),
            "outcome": p.get("outcome"),
            "event_seq": ev["event_seq"]})
    call_binding = {}
    any_translation = False
    for ev in events:
        if ev["event_seq"] > cursor_to:
            break
        if ev["type"] != "TRANSLATION_RECORDED":
            continue
        any_translation = True
        for centry in ev["payload"].get("calls") or []:
            if centry.get("loop_request_id"):
                call_binding[centry["loop_request_id"]] = {
                    "provider_ordinal":
                        centry.get("provider_ordinal"),
                    "translation_seq": ev["event_seq"]}
    if any_translation:
        bound = {}
        for entry in entries:
            binding = call_binding.get(entry["request_id"])
            if binding is not None:
                bound[id(entry)] = binding
        for ev in delta:
            if ev["type"] == "TRANSLATION_RECORDED":
                for centry in \
                        ev["payload"].get("calls") or []:
                    if not centry.get("refusal_class"):
                        continue
                    entries.append({
                        "dispatch_id": None,
                        "request_id": None,
                        "outcome": "refused",
                        "event_seq": ev["event_seq"],
                        "_translation_seq": ev["event_seq"],
                        "_provider_ordinal":
                            centry.get("provider_ordinal")})
            elif ev["type"] == "REJECTION" and \
                    ev["payload"].get("attempted_type") \
                    == "TOOL_DISPATCHED":
                binding = call_binding.get(
                    ev["payload"].get("request_id"))
                if binding is not None:
                    entries.append({
                        "dispatch_id": None,
                        "request_id": ev["payload"].get(
                            "request_id"),
                        "outcome": "refused",
                        "event_seq": ev["event_seq"],
                        "_translation_seq":
                            binding["translation_seq"],
                        "_provider_ordinal":
                            binding["provider_ordinal"]})
        for entry in entries:
            binding = bound.get(id(entry))
            if binding is not None:
                entry["_translation_seq"] = \
                    binding["translation_seq"]
                entry["_provider_ordinal"] = \
                    binding["provider_ordinal"]
        entries.sort(key=lambda entry: (
            (0, entry["_translation_seq"],
             entry["_provider_ordinal"])
            if "_translation_seq" in entry else
            (1, 0, entry.get("event_seq") or 0)))
        for entry in entries:
            entry.pop("_translation_seq", None)
            entry.pop("_provider_ordinal", None)
    return entries


def _staged_standing_dispatches(events, instance_id,
                                head):
    """The activation's standing dispatches as they stood
    at `head`, folded from the record's dispatch events
    under the fold's own rules (first outcome stands; a
    standing uncertain is settled by a later attributable
    result or failure; an uncertain dispatch reconciles
    once) and projected to the five fields the package
    presents, in dispatch order."""
    dispatches = {}
    for ev in events:
        if ev["event_seq"] > head:
            break
        t = ev["type"]
        p = ev["payload"]
        if t == "TOOL_DISPATCHED":
            dispatches[p.get("dispatch_id")] = {
                "instance_id": p.get("instance_id"),
                "request_id": p.get("request_id"),
                "tool": p.get("tool"),
                "outcome": None,
                "reconciled_seq": None,
                "reconciled_outcome": None}
        elif t == "TOOL_OUTCOME":
            entry = dispatches.get(p.get("dispatch_id")
                                   or "")
            if entry is not None:
                outcome = p.get("outcome")
                if entry["outcome"] is None:
                    entry["outcome"] = outcome
                elif entry["outcome"] == "uncertain" and \
                        entry["reconciled_seq"] is None and \
                        outcome in ("result", "failure"):
                    entry["outcome"] = outcome
        elif t == "TOOL_RECONCILED":
            entry = dispatches.get(p.get("dispatch_id")
                                   or "")
            if entry is not None and \
                    entry["outcome"] == "uncertain" and \
                    entry["reconciled_seq"] is None:
                entry["reconciled_seq"] = ev["event_seq"]
                entry["reconciled_outcome"] = \
                    p.get("outcome")
    return [{
        "dispatch_id": did,
        "request_id": d.get("request_id"),
        "tool": d.get("tool"),
        "outcome": d.get("outcome"),
        "reconciled_outcome": d.get("reconciled_outcome"),
    } for did, d in sorted(dispatches.items())
        if d.get("instance_id") == instance_id]


def _pointer_line_count(entry, outcome_result):
    """A pointer entry's line count, where the record
    knows one — this checker's copy of the loop's
    derivation (INDEX 568): the served descriptor's
    own line count where it carries one; a served
    range's span where the descriptor names its lines;
    otherwise the recorded content's own lines."""
    served = entry.get("served")
    if isinstance(served, dict):
        line_count = served.get("line_count")
        if isinstance(line_count, int):
            return line_count
        start = served.get("start_line")
        end = served.get("end_line")
        if isinstance(start, int) and isinstance(end, int):
            return end - start + 1
    if isinstance(outcome_result, dict):
        content = outcome_result.get("content")
        if isinstance(content, str):
            return len(content.splitlines())
    return None


def _derive_working_set_pointers(working_set, events,
                                 assembly_id, catalogue):
    """The working set's pointer presentation,
    reconstructed from the record alone — this
    checker's independent derivation of the loop's
    pointer form (INDEX 568): each record-side entry
    rendered as a pointer carrying its address and
    authority path, the tool that gathered it and the
    step it was gathered at (the iteration whose
    LOOP_ITERATION event precedes its outcome), its
    size in bytes and lines where the record knows
    them, its content hash, its served descriptor, its
    dispatch and outcome identity, its content_carried
    standing, the access call that pulls it again
    where a granted call covers the address, and the
    one plain sentence. No entry's content stands in
    the form. The component's budget and content
    figures keep their record meanings."""
    outcomes = {}
    steps = {}
    for ev in events:
        payload = ev.get("payload") or {}
        if ev.get("type") == "TOOL_OUTCOME":
            outcomes[ev.get("event_seq")] = payload
        elif ev.get("type") == "LOOP_ITERATION" \
                and payload.get("assembly_id") == assembly_id \
                and isinstance(payload.get("iteration"), int):
            steps[ev.get("event_seq")] = payload["iteration"]
    entries = []
    for entry in working_set["entries"]:
        outcome = outcomes.get(entry["outcome_event_seq"]) or {}
        gathered_step = 0
        for seq, iteration in steps.items():
            if isinstance(seq, int) \
                    and seq < entry["outcome_event_seq"] \
                    and iteration > gathered_step:
                gathered_step = iteration
        pointer = {
            "tool": entry["tool"],
            "path": entry["path"],
            "authority_path": entry["authority_path"],
            "content_sha256": entry["content_sha256"],
            "content_bytes": entry["content_bytes"],
        }
        line_count = _pointer_line_count(
            entry, outcome.get("result"))
        if line_count is not None:
            pointer["line_count"] = line_count
        pointer["served"] = copy.deepcopy(entry["served"])
        pointer["dispatch_id"] = entry["dispatch_id"]
        pointer["request_id"] = entry["request_id"]
        pointer["outcome_event_seq"] = \
            entry["outcome_event_seq"]
        pointer["gathered_step"] = gathered_step
        pointer["content_carried"] = entry["content_carried"]
        if "not_carried_reason" in entry:
            pointer["not_carried_reason"] = \
                entry["not_carried_reason"]
        way = _staged_access_way(catalogue, entry["path"])
        if way is not None:
            pointer["access"] = way
            pointer["note"] = _STAGED_POINTER_SENTENCE.format(
                path=entry["path"], tool=way["tool"])
        else:
            pointer["note"] = \
                _STAGED_POINTER_SENTENCE_NO_WAY.format(
                    path=entry["path"])
        entries.append(pointer)
    return {
        "budget_bytes": working_set["budget_bytes"],
        "content_bytes": working_set["content_bytes"],
        "note": _WORKING_SET_POINTER_NOTE,
        "entries": entries,
    }


def _derive_staged_core(events, state, gen, content,
                        iteration, payload,
                        prev_iteration_seq, bounds):
    """The staged package's committed core for one
    iteration, reconstructed from the record alone — this
    checker's independent derivation of the loop's staged
    presentation: the stage from the iteration number,
    the cover and the stage's component from the pinned
    case's contents and the sealed declarations, the tool
    catalogue and menu from the sealed grants under the
    recorded registry version, the standing dispatches
    and the tool results' identities from the recorded
    events at or before the iteration's cursor close, the
    gate correction from the gate event bound to the
    previous iteration, and the working set standing by
    its own reconstructed hash. Returns None where the
    catalogue cannot be derived (reported by the
    catalogue verification itself)."""
    gp = gen["payload"]
    # The sealed contract this reconstruction derives
    # (INDEX 544; the pointer-rule successor, INDEX
    # 568): the generated record's own declaration —
    # v1, or v2, whose files introduction and dashboard
    # direction tell the pointer truth and whose core
    # carries the working set's pointer form verbatim
    # beside the record set's hash.
    declared_contract = gp.get("presentation_contract")
    pointer_form = declared_contract == \
        _PRESENTATION_CONTRACT_V2
    directions = _STAGED_DIRECTIONS_V2 \
        if pointer_form else _STAGED_DIRECTIONS
    instance_id = gp.get("instance_id")
    seat = gp.get("seat")
    role = ((state.get("seats") or {}).get(seat)
            or {}).get("role")
    ceiling = bounds.get("step_ceiling") \
        if bounds is not None else None
    stage = _staged_stage(iteration)
    onboarding = (content or {}).get("onboarding")
    if not (isinstance(onboarding, dict)
            and isinstance(onboarding.get("headline"), str)
            and isinstance(onboarding.get("deliverable"), str)
            and isinstance(onboarding.get("text"), str)):
        onboarding = None
    headline = onboarding["headline"] \
        if onboarding is not None else \
        "The job in your briefcase"
    deliverable = onboarding["deliverable"] \
        if onboarding is not None else None
    sealed_delivery = gp.get("delivery")
    honoured_delivery = sealed_delivery if (
        isinstance(sealed_delivery, dict)
        and sealed_delivery.get("route")
        == _DELIVERY_ROUTE_CONTRIBUTION
        and (content or {}).get("delivery")
        == sealed_delivery) else None
    # The third gate's declaration (INDEX 557),
    # honoured under the loop's own rule: the seal
    # well-formed, the case's own component exactly,
    # and the delivery itself standing.
    sealed_floor = gp.get("delivery_floor")
    honoured_floor = sealed_floor if (
        isinstance(sealed_floor, dict)
        and set(sealed_floor) == {"min_words"}
        and isinstance(
            sealed_floor.get("min_words"), int)
        and not isinstance(
            sealed_floor.get("min_words"), bool)
        and sealed_floor["min_words"] >= 1
        and (content or {}).get("delivery_floor")
        == sealed_floor
        and honoured_delivery is not None) else None
    if deliverable is None and \
            isinstance(honoured_delivery, dict):
        deliverable = honoured_delivery.get("destination")
    deliverable_text = deliverable \
        if isinstance(deliverable, str) else \
        "the deliverable named in your case"
    if iteration == 1:
        cover_statement = _STAGED_COVER_FIRST.format(
            seat=seat, role=role, headline=headline,
            deliverable=deliverable_text)
    elif stage == "dashboard":
        cover_statement = (
            f"{headline} — the deliverable: "
            f"{deliverable_text}. Step {iteration} of "
            f"{ceiling}; task in progress.")
    else:
        cover_statement = (
            f"{headline} — the deliverable: "
            f"{deliverable_text}. Step {iteration} of "
            f"{ceiling}; task in progress. Onboarding "
            f"stage {iteration} of 4: {stage}.")
    staged = {}
    staged["seat"] = seat
    staged["role"] = role
    staged["instance_id"] = instance_id
    staged["case_id"] = gp.get("case_id")
    staged["case_version"] = gp.get("case_version")
    staged["presentation"] = {
        "contract": declared_contract,
        "stage": stage,
        "direction": directions[stage]}
    staged["cover"] = {
        "headline": headline,
        "deliverable": deliverable_text,
        "statement": cover_statement}
    content = content or {}
    # The catalogue is derived here, ahead of the
    # stage components, because the files stage's
    # access ways are read from it (INDEX 549); the
    # derivation and its failure are otherwise exactly
    # as they stood below the components.
    version = payload.get("registry_version")
    per_grant = gp.get("catalogue_contract") in \
        (_RETRIEVAL_CONTRACT, _EXEC_CONTRACT)
    catalogue, _ground = _derive_catalogue(
        gp.get("grants"), version, per_grant=per_grant)
    if catalogue is None:
        return None
    if stage == "memory":
        staged["snapshot"] = _staged_snapshot(content)
        role_memory = content.get("role_memory")
        staged["memory"] = {
            "introduction": _STAGED_MEMORY_INTRO,
            "entries": copy.deepcopy(role_memory)
            if isinstance(role_memory, list) else []}
    elif stage == "case":
        essentials = {
            "part": content.get("part"),
            "evidence_boundary": copy.deepcopy(
                content.get("evidence_boundary")),
            "delivery": copy.deepcopy(content["delivery"])
            if isinstance(content.get("delivery"), dict)
            else None,
            "freshness": (
                "suspended — no freshness refusal "
                "applies to this job; your answers "
                "are judged on the work"
                if gp.get("freshness_guard")
                == _FRESHNESS_GUARD_SUSPENDED
                else "in force — your answers are "
                     "judged against the record as it "
                     "stood when you were woken")}
        opening = content.get("opening")
        if isinstance(opening, dict) and opening:
            essentials["opening"] = copy.deepcopy(opening)
        staged["case_essentials"] = essentials
    elif stage == "files":
        # The needed files with their ways in (INDEX
        # 549) and the worked example (INDEX 548): the
        # example is the generated record's seal,
        # presented where it stands well-formed — the
        # loop's honour rule, derived identically here.
        example = gp.get("worked_example")
        if not _worked_example_well_formed(
                example, declared_contract):
            example = None
        if pointer_form:
            intro = _STAGED_FILES_INTRO_V2 \
                if example is not None \
                else _STAGED_FILES_INTRO_NO_EXAMPLE_V2
        else:
            intro = _STAGED_FILES_INTRO \
                if example is not None \
                else _STAGED_FILES_INTRO_NO_EXAMPLE
        files = {"introduction": intro,
                 "briefcase": []}
        glossary = content.get("glossary")
        if isinstance(glossary, list):
            for entry in glossary:
                if isinstance(entry, dict) and \
                        isinstance(entry.get("address"), str):
                    brief = {
                        "address": entry["address"],
                        "description":
                            entry.get("description")}
                    way = _staged_access_way(
                        catalogue, entry["address"])
                    if way is not None:
                        brief["access"] = way
                    files["briefcase"].append(brief)
        journal_path = _staged_journal_path(content)
        if journal_path is not None:
            files["journal"] = {
                "path": journal_path,
                "label": _STAGED_JOURNAL_POINTER_V2
                if pointer_form
                else _STAGED_JOURNAL_POINTER}
        if example is not None:
            files["worked_example"] = {
                "label": _STAGED_EXAMPLE_LABEL,
                "call": {
                    "tool": example["tool"],
                    "parameters": {
                        "path": example["path"]}},
                "result": copy.deepcopy(example["result"])}
            if pointer_form:
                files["worked_example"]["proof"] = \
                    _STAGED_EXAMPLE_PROOF
        staged["files"] = files
    elif stage == "task":
        task = {"assignment": content.get("assignment"),
                "deliverable": deliverable_text}
        if honoured_floor is not None:
            statement = _STAGED_TASK_FLOOR_STATEMENT_V2 \
                if pointer_form \
                else _STAGED_TASK_FLOOR_STATEMENT
            task["delivery_floor"] = statement.format(
                min_words=honoured_floor["min_words"])
        verification = content.get("verification_list")
        if isinstance(verification, list):
            task["verification_list"] = copy.deepcopy(
                verification)
        staged["task"] = task
    else:
        addresses = []
        glossary = content.get("glossary")
        if isinstance(glossary, list):
            for entry in glossary:
                if isinstance(entry, dict) and \
                        isinstance(entry.get("address"), str):
                    addresses.append(entry["address"])
        journal_path = _staged_journal_path(content)
        staged["pointers"] = [
            {"item": "your memory",
             "pointer": "presented at your first wake "
                        "(onboarding stage 1); it "
                        "stands in your case in this "
                        "office"},
            {"item": "your case",
             "pointer": "presented at your second "
                        "wake (onboarding stage 2): "
                        "the frame, the evidence "
                        "boundary and the delivery "
                        "declaration"},
            {"item": "your files",
             "pointer": "the briefcase map from your "
                        "third wake (onboarding "
                        "stage 3): "
                        + ("; ".join(addresses)
                           if addresses else
                           "no files stand in the "
                           "briefcase's map")},
            {"item": "your journal",
             "pointer": journal_path
             if journal_path is not None else
             "no journal is designated for this job"},
            {"item": "your task",
             "pointer": "presented at your fourth "
                        "wake (onboarding stage 4), "
                        "with your tool menu grouped "
                        "by the job's phases"}]
    staged["step_position"] = {
        "statement": f"step {iteration} of {ceiling}",
        "iteration": iteration,
        "step_ceiling": ceiling}
    staged["task_status"] = "in progress"
    if prev_iteration_seq is not None:
        correction = None
        for ev in events:
            if ev["event_seq"] > payload["cursor_to"]:
                break
            if ev["type"] == "DELIVERY_GATE" and \
                    ev["payload"].get("assembly_id") \
                    == gp.get("assembly_id") and \
                    ev["payload"].get("iteration_seq") \
                    == prev_iteration_seq:
                correction = {
                    "what_arrived": ev["payload"].get(
                        "raw_excerpt"),
                    "response_length": ev["payload"].get(
                        "raw_length"),
                    "what_failed": ev["payload"].get(
                        "parse_error"),
                    "instruction": _STAGED_GATE_INSTRUCTION}
        if correction is not None:
            staged["delivery_gate_correction"] = correction
        stage_correction = None
        for ev in events:
            if ev["event_seq"] > payload["cursor_to"]:
                break
            if ev["type"] == "DELIVERY_STAGE_GATE" and \
                    ev["payload"].get("assembly_id") \
                    == gp.get("assembly_id") and \
                    ev["payload"].get("iteration_seq") \
                    == prev_iteration_seq:
                sp = ev["payload"]
                stage_correction = {
                    "what_arrived":
                        _stage_gate_what_arrived(
                            sp.get("stage")),
                    "stage": sp.get("stage"),
                    "contribution_seq":
                        sp.get("contribution_seq"),
                    "text_sha256": sp.get("text_sha256"),
                    "instruction":
                        _STAGED_STAGE_GATE_INSTRUCTION}
        if stage_correction is not None:
            staged["delivery_stage_gate_correction"] = \
                stage_correction
        evidence_correction = None
        for ev in events:
            if ev["event_seq"] > payload["cursor_to"]:
                break
            if ev["type"] == "DELIVERY_EVIDENCE_GATE" and \
                    ev["payload"].get("assembly_id") \
                    == gp.get("assembly_id") and \
                    ev["payload"].get("iteration_seq") \
                    == prev_iteration_seq:
                ep = ev["payload"]
                missing = ep.get("missing")
                evidence_correction = {
                    "what_arrived":
                        _STAGED_EVIDENCE_GATE_WHAT_ARRIVED,
                    "contribution_seq":
                        ep.get("contribution_seq"),
                    "text_sha256": ep.get("text_sha256"),
                    "missing": missing,
                    "instruction":
                        _evidence_gate_instruction(
                            catalogue, missing)
                        if isinstance(missing, list)
                        else None}
        if evidence_correction is not None:
            staged["delivery_evidence_gate_correction"] = \
                evidence_correction
        length_correction = None
        for ev in events:
            if ev["event_seq"] > payload["cursor_to"]:
                break
            if ev["type"] == "DELIVERY_LENGTH_GATE" and \
                    ev["payload"].get("assembly_id") \
                    == gp.get("assembly_id") and \
                    ev["payload"].get("iteration_seq") \
                    == prev_iteration_seq:
                lp = ev["payload"]
                count = lp.get("word_count")
                floor = lp.get("min_words")
                length_correction = {
                    "what_arrived":
                        _length_gate_what_arrived(count)
                        if isinstance(count, int)
                        and not isinstance(count, bool)
                        else None,
                    "contribution_seq":
                        lp.get("contribution_seq"),
                    "text_sha256": lp.get("text_sha256"),
                    "word_count": count,
                    "min_words": floor,
                    "instruction":
                        _STAGED_LENGTH_GATE_INSTRUCTION
                        .format(word_count=count,
                                min_words=floor)
                        if isinstance(count, int)
                        and not isinstance(count, bool)
                        and isinstance(floor, int)
                        and not isinstance(floor, bool)
                        else None}
        if length_correction is not None:
            staged["delivery_length_gate_correction"] = \
                length_correction
        shape_correction = None
        for ev in events:
            if ev["event_seq"] > payload["cursor_to"]:
                break
            if ev["type"] == "TOOL_SHAPE_GATE" and \
                    ev["payload"].get("assembly_id") \
                    == gp.get("assembly_id") and \
                    ev["payload"].get("iteration_seq") \
                    == prev_iteration_seq:
                tool_name = ev["payload"].get("tool_name")
                first_address = None
                glossary = (content or {}).get("glossary")
                if isinstance(glossary, list):
                    for entry in glossary:
                        if isinstance(entry, dict) and \
                                isinstance(
                                    entry.get("address"),
                                    str):
                            first_address = \
                                entry["address"]
                            break
                shape_correction = \
                    _tool_shape_gate_correction(
                        tool_name, first_address) \
                    if isinstance(tool_name, str) \
                    and tool_name \
                    and first_address is not None \
                    else None
        if shape_correction is not None:
            staged["tool_shape_gate_correction"] = \
                shape_correction
    if stage == "task":
        staged["tool_list"] = _staged_tool_menu(
            catalogue, deliverable=deliverable)
    if stage in ("files", "task", "dashboard"):
        staged["tools"] = catalogue
    staged["standing_dispatches"] = \
        _staged_standing_dispatches(
            events, instance_id, payload["cursor_to"])
    staged["bounds"] = {
        "iteration": iteration,
        "steps_used": iteration - 1,
        "step_ceiling": ceiling,
        "deadline_seconds": bounds.get("deadline_seconds")
        if bounds is not None else None}
    staged["position"] = payload["cursor_to"]
    staged["tool_result_refs"] = _staged_tool_result_refs(
        events, instance_id, seat, gp.get("case_id"),
        payload.get("activated_seq"),
        payload["cursor_from"], payload["cursor_to"])
    expected_ws = _derive_working_set(
        events, instance_id, payload["cursor_to"])
    staged["working_set_hash"] = _working_set_hash(
        expected_ws)
    if pointer_form:
        # The pointer form stands in the core verbatim
        # (INDEX 568): this checker's own derivation of
        # the pointers from the reconstructed set, the
        # record and the catalogue — the commitment
        # binds the exact form the worker was shown,
        # beside the record set's hash above.
        staged["working_set"] = \
            _derive_working_set_pointers(
                expected_ws, events,
                gp.get("assembly_id"), catalogue)
    return staged


# ------------------------------------------------------------
# The process-tree contract (the room rebuild): this
# checker's own copies of the tree presentation's
# wording and derivations, reconstructed independently
# of the loop's, as its other contracts' copies stand
# here; the framework's stand in loop.py.
_TREE_COVER_FIRST = (
    "You are {seat}, the {role} in this office, "
    "assembled for one job. The shape of the work here "
    "is simple: you are woken with a package, you act, "
    "and the record keeps everything. This package is "
    "your whole opening — your memory, your case, your "
    "files, your tools and your journal, all of it once "
    "— and the process tree below walks the job step by "
    "step from here: one step in front of you at a "
    "time, each step's content presented at its step "
    "and never twice. Nothing needs acknowledging; "
    "your first answer is work. The job: {headline}. "
    "The deliverable: {deliverable}.")
_TREE_DIRECTION_OPENING = (
    "Your opening package: everything in it is "
    "presented once, here — your memory, the process "
    "tree that walks this job, your case's essentials, "
    "your files with their ways in, your tool "
    "catalogue, and your journal with its contract. "
    "Begin work in your first answer.")
_TREE_DIRECTION_STEP = (
    "A step package: the tree as it stands, your "
    "current step spelled out, your journal as you "
    "left it, and at most this step's fresh content — "
    "presented once, at its step. Everything else "
    "stands as pointers.")
_TREE_FILES_INTRO = (
    "Your briefcase holds the job's files — the files "
    "your task needs. What stands below are pointers, "
    "not contents: each file's address, what it is, "
    "and its way in — the exact call that pulls it, "
    "naming a tool you hold. The tree walks them one "
    "at a time: when a file's gather step is current, "
    "read it whole, and its content is presented to "
    "you at that step, once. What you pull is yours "
    "from your room at any time — the tree governs "
    "what stands in front of you, not what you may "
    "reach for.")
_TREE_JOURNAL_LABEL = (
    "your journal — your notebook: notes, decisions, "
    "where you left off. Yours to write and rewrite; "
    "orientation, not record and not memory. Keep it "
    "as you work: after each file you read, log its "
    "name and the key points you took from it, in "
    "one or two plain lines. The office reads your "
    "journal at every wake to resume you, and the "
    "director may audit it; nothing parses it — it "
    "is read as you wrote it. It rides in every "
    "package, exactly as you left it, below.")
_TREE_COMPOSE_POINTS = [
    "what this framework is",
    "what has actually been proven",
    "what has not been proven",
    "what remains to be built"]
_TREE_COMPOSE_INSTRUCTION = (
    "Compile the brief from your journal entries — "
    "the bits you logged at each gather step are the "
    "brief's substance, in your own words. Your "
    "journal stands above, verbatim. Cover the four "
    "points: what this framework is; what has "
    "actually been proven; what has not been proven; "
    "what remains to be built. Stay accurate to what "
    "you gathered; invent nothing; where the sources "
    "disagree with each other, say so. Pull a source "
    "again only if a gap shows in your entries — its "
    "pointer stands in your working set. When the "
    "brief is ready, move to DELIVER: your "
    "contribution is the delivery.")
_TREE_DELIVER_INSTRUCTION = (
    "Deliver now: answer with outcome \"contribute\" "
    "and the brief's text as its text. The "
    "contribution is the delivery — the office files "
    "it at {destination}. The standing gates "
    "adjudicate it as they stand: the evidence (every "
    "gather step's source read and standing in the "
    "record) and the length floor the figures name. "
    "Nothing else is asked of you at this step.")
_TREE_DELIVER_AGAIN_INSTRUCTION = (
    "A contribution stands in the record, set aside "
    "unfiled by a gate — its correction stands in "
    "this package. Deliver again: answer with outcome "
    "\"contribute\" and the brief's text as its text. "
    "The contribution is the delivery — the office "
    "files it at {destination}.")
_TREE_ORIENT_INSTRUCTION = (
    "Take this opening in — it is the whole of it, "
    "and nothing in it will be presented again. Your "
    "first step is the tree's first gather step: "
    "read {address} whole, then log its journal "
    "bits. You may begin that work in your first "
    "answer; no acknowledgement is asked or needed.")
_TREE_GATHER_INSTRUCTION = (
    "Read {address} whole: {tool} on {address} pulls "
    "the whole file. Read it, don't list it — a "
    "listing gives you its shape, not its words. "
    "Then log the journal bits for this file: a "
    "sandbox.write to {journal} carrying your "
    "journal as it stands plus one or two plain "
    "lines naming this file and the key points you "
    "took from it. When the read stands carried and "
    "the journal bits stand after it, this step is "
    "done and the tree moves on.")
_TREE_GATHER_READ_STANDS_INSTRUCTION = (
    "{address} stands read — its content is in front "
    "of you at this step, once. What this step still "
    "needs is the journal move: a sandbox.write to "
    "{journal} carrying your journal as it stands "
    "plus one or two plain lines naming this file "
    "and the key points you took from it. When the "
    "journal bits stand after the read, this step is "
    "done and the tree moves on.")


def _step_gate_what_arrived(missing, address,
                            ahead_address):
    if "read" in missing:
        return (f"work ahead of the tree — "
                f"{ahead_address} stands gathered — "
                f"while this step's file, {address}, "
                f"has not been read")
    if ahead_address is not None:
        return (f"your read of {address} — the whole "
                f"file stands gathered in the record — "
                f"and work ahead of the tree: "
                f"{ahead_address} stands gathered too, "
                f"before this step completed")
    return (f"your read of {address} — the whole file "
            f"stands gathered in the record")


_STEP_GATE_INSTRUCTION = (
    "Nothing was refused, and nothing is lost: every "
    "call you made stands executed in the record. "
    "Presentation walks the tree one step at a time, "
    "and this step is still current — it completes "
    "when {needs}. Then the tree moves on and the "
    "next step's content stands in front of you. "
    "Work already gathered for later steps stands in "
    "the record and will be presented at its step, "
    "once; you do not need to pull it again.")


def _step_gate_needs(missing, address, journal_path):
    parts = []
    if "read" in missing:
        parts.append(
            f"the read of {address} stands carried "
            f"(read the file whole — a listing gives "
            f"its shape, not its words)")
    if "journal" in missing:
        parts.append(
            f"the journal bits for {address} stand "
            f"in {journal_path} after that read (one "
            f"or two plain lines naming the file and "
            f"the key points you took from it)")
    return " and ".join(parts)


def _step_gate_correction(step, address, missing,
                          ahead_address, journal_path):
    """The step gate's correction, re-derived from
    the gate event's facts — this checker's copy of
    the loop's derivation."""
    return {
        "what_arrived": _step_gate_what_arrived(
            missing, address, ahead_address),
        "step": step,
        "address": address,
        "missing": list(missing),
        "instruction": _STEP_GATE_INSTRUCTION.format(
            needs=_step_gate_needs(
                missing, address, journal_path))}


def _tree_stage_gate_what_arrived(stage):
    if stage.startswith("gather:"):
        return (f"a contribution, offered while the "
                f"tree stood at the gather step for "
                f"{stage[len('gather:'):]}, before "
                f"the tree reached the delivery step")
    return (f"a contribution, offered while the tree "
            f"stood at the {stage} step, before the "
            f"tree reached the delivery step")


_TREE_STAGE_GATE_INSTRUCTION = (
    "Nothing was filed. The contribution door opens "
    "when the tree reaches DELIVER: walk the steps — "
    "read each file the tree names whole, log its "
    "journal bits, and the tree moves on; at COMPOSE "
    "you compile the brief from your journal "
    "entries, and at DELIVER your contribution is "
    "the delivery and the office files it. The text "
    "you sent stands in the record, set aside "
    "unfiled; if it is the brief you mean to "
    "deliver, send it again when the tree reaches "
    "DELIVER.")


def _tree_nodes(content):
    """The sealed process tree's node list — this
    checker's copy of the loop's derivation: the
    pinned case's process_tree component, standing
    well-formed in exactly the sealed shape, or
    None."""
    tree = (content or {}).get("process_tree")
    if not isinstance(tree, dict):
        return None
    if set(tree) != {"root", "steps"}:
        return None
    root = tree.get("root")
    steps = tree.get("steps")
    if not isinstance(root, str) or not root:
        return None
    if not isinstance(steps, list) or not steps:
        return None
    nodes = []
    for step in steps:
        if not isinstance(step, dict):
            return None
        kind = step.get("node")
        if kind in ("orient", "compose", "deliver"):
            if set(step) != {"node"}:
                return None
            nodes.append({"id": kind, "kind": kind})
        elif kind == "gather":
            if set(step) != {"node", "address"}:
                return None
            address = step.get("address")
            if not isinstance(address, str) or \
                    not address:
                return None
            nodes.append({"id": f"gather:{address}",
                          "kind": "gather",
                          "address": address})
        else:
            return None
    kinds = [node["kind"] for node in nodes]
    if kinds[0] != "orient" or \
            kinds[-2:] != ["compose", "deliver"] or \
            any(kind != "gather"
                for kind in kinds[1:-2]) or \
            "gather" not in kinds:
        return None
    return {"root": root, "nodes": nodes}


def _tree_requested(events, head):
    """The record's requested parameters at a head,
    keyed by request identity — this checker's copy."""
    requested = {}
    for ev in events:
        if ev["event_seq"] > head:
            break
        if ev["type"] != "TOOL_REQUESTED":
            continue
        payload = ev["payload"]
        parameters = payload.get("parameters")
        if isinstance(parameters, dict):
            requested[payload.get("request_id")] = \
                parameters
    return requested


def _tree_dispatch_info(events, head):
    """Dispatch identities and tools from the record's
    own dispatch events at a head — the same record
    fact the working set's reconstruction reads."""
    info = {}
    for ev in events:
        if ev["event_seq"] > head:
            break
        if ev["type"] == "TOOL_DISPATCHED":
            p = ev["payload"]
            info[p.get("dispatch_id")] = (
                p.get("instance_id"), p.get("tool"))
    return info


def _tree_read_stands(entries, requested, address):
    """Whether one address's whole content stands
    carried, and the satisfying read's outcome
    position — this checker's copy of the loop's
    derivation, weighed by its own evidence
    computation."""
    mine = [entry for entry in entries
            if entry.get("path") == address]
    for entry in mine:
        if entry.get("tool") == "sandbox.read" and \
                entry.get("content_carried"):
            return True, entry.get("outcome_event_seq")
    if not _evidence_address_stands(
            entries, requested, address):
        return False, None
    seqs = [entry.get("outcome_event_seq")
            for entry in mine
            if entry.get("tool") == "sandbox.read_range"
            and entry.get("content_carried")
            and isinstance(
                entry.get("outcome_event_seq"), int)
            and not isinstance(
                entry.get("outcome_event_seq"), bool)]
    return True, (max(seqs) if seqs else None)


def _tree_journal_writes(events, dispatch_info,
                         requested, instance_id, head,
                         journal_path):
    """The journal's standing writes at a head — this
    checker's copy of the loop's derivation."""
    writes = []
    for ev in events:
        if ev["event_seq"] > head:
            break
        if ev["type"] != "TOOL_OUTCOME":
            continue
        payload = ev["payload"]
        if payload.get("outcome") != "result":
            continue
        info = dispatch_info.get(
            payload.get("dispatch_id"))
        if info is None or info[0] != instance_id or \
                info[1] != "sandbox.write":
            continue
        parameters = requested.get(
            payload.get("request_id")) or {}
        if parameters.get("path") != journal_path:
            continue
        content = parameters.get("content")
        writes.append((ev["event_seq"],
                       content if isinstance(
                           content, str) else ""))
    return writes


def _tree_state(events, instance_id, head, content,
                iteration):
    """The tree's state at one package head — this
    checker's independent derivation, from the record
    alone: node states, the current node, the gather
    facts, the journal's content as it stands, and
    the working set the derivation weighed. The
    derivation's rules are the loop's: ORIENT done
    after the first wake; a GATHER step done iff its
    read stands carried and a journal write stands
    after that read, the writes consumed in step
    order, one write closing at most one step;
    COMPOSE done where a contribution stands (and
    the gathers stand done); DELIVER done where the
    filing stands; the current node the first not
    done."""
    tree = _tree_nodes(content)
    if tree is None:
        return None
    nodes = tree["nodes"]
    working_set = _derive_working_set(
        events, instance_id, head)
    entries = working_set["entries"]
    requested = _tree_requested(events, head)
    dispatch_info = _tree_dispatch_info(events, head)
    journal_path = _staged_journal_path(content)
    writes = _tree_journal_writes(
        events, dispatch_info, requested, instance_id,
        head, journal_path) \
        if journal_path is not None else []
    gather_facts = {}
    consumed = 0
    for node in nodes:
        if node["kind"] != "gather":
            continue
        stands, read_seq = _tree_read_stands(
            entries, requested, node["address"])
        journal_stands = False
        if stands and read_seq is not None:
            for write_seq, _written in writes:
                if write_seq > max(read_seq, consumed):
                    journal_stands = True
                    consumed = write_seq
                    break
        gather_facts[node["id"]] = {
            "read_stands": stands,
            "read_seq": read_seq,
            "journal_stands": journal_stands}
    gathers_done = all(
        gather_facts[node["id"]]["read_stands"]
        and gather_facts[node["id"]]["journal_stands"]
        for node in nodes if node["kind"] == "gather")
    contribution_stands = any(
        ev["type"] == "CONTRIBUTION"
        and ev["event_seq"] <= head
        and (ev["payload"].get("contribution_id")
             == instance_id
             or instance_id in (ev.get("affected")
                                or []))
        for ev in events)
    filed = any(
        ev["type"] == "DELIVERABLE_FILED"
        and ev["event_seq"] <= head
        and ev["payload"].get("instance_id")
        == instance_id
        for ev in events)
    states = {}
    current = None
    for node in nodes:
        kind = node["kind"]
        if kind == "orient":
            done = iteration > 1
        elif kind == "gather":
            facts = gather_facts[node["id"]]
            done = facts["read_stands"] and \
                facts["journal_stands"]
        elif kind == "compose":
            done = gathers_done and contribution_stands
        else:
            done = filed
        states[node["id"]] = "done" if done else "pending"
        if not done and current is None:
            current = node
            states[node["id"]] = "current"
    journal_content = writes[-1][1] if writes else ""
    return {
        "root": tree["root"],
        "nodes": nodes,
        "states": states,
        "current": current,
        "gather_facts": gather_facts,
        "journal_path": journal_path,
        "journal_content": journal_content,
        "working_set": working_set,
        "entries": entries,
        "requested": requested}


def _tree_step_gate_owed(state):
    """What the step gate owes at a wake — this
    checker's copy of the loop's derivation: the
    correction is owed only where the current gather
    step stands incomplete with work standing ahead
    of it (a later gather step's read stands carried);
    it names the journal bits alone where the current
    read already stands, the read and then the
    journal bits where it does not."""
    current = state["current"]
    if current is None or \
            current["kind"] != "gather":
        return None
    facts = state["gather_facts"][current["id"]]
    if facts["read_stands"] and facts["journal_stands"]:
        return None
    ahead = None
    seen_current = False
    for node in state["nodes"]:
        if node["id"] == current["id"]:
            seen_current = True
            continue
        if not seen_current or \
                node["kind"] != "gather":
            continue
        if state["gather_facts"][node["id"]][
                "read_stands"]:
            ahead = node["address"]
            break
    if ahead is None:
        return None
    missing = ["journal"] if facts["read_stands"] \
        else ["read", "journal"]
    return (current["id"], current["address"],
            missing, ahead)


def _tree_presented_addresses(events, instance_id,
                              content,
                              iteration_numbers):
    """The gather addresses whose content an earlier
    wake already presented — this checker's copy of
    the loop's derivation."""
    presented = set()
    for number, head in iteration_numbers:
        earlier = _tree_state(
            events, instance_id, head, content, number)
        if earlier is None:
            continue
        current = earlier["current"]
        if current is None or \
                current["kind"] != "gather":
            continue
        facts = earlier["gather_facts"][current["id"]]
        if facts["read_stands"]:
            presented.add(current["address"])
    return presented


def _tree_step_component(tstate, catalogue,
                         deliverable_text, honoured_floor,
                         judged_mode):
    """The current step, spelled out — this checker's
    copy of the loop's derivation."""
    current = tstate["current"]
    journal_path = tstate["journal_path"]
    step = {"node": current["id"],
            "kind": current["kind"]}
    figures = _STAGED_TASK_FLOOR_STATEMENT_V2.format(
        min_words=honoured_floor["min_words"]) \
        if honoured_floor is not None else \
        "The brief runs to about 600 words."
    if current["kind"] == "gather":
        address = current["address"]
        step["address"] = address
        facts = tstate["gather_facts"][current["id"]]
        if facts["read_stands"]:
            step["instruction"] = \
                _TREE_GATHER_READ_STANDS_INSTRUCTION \
                .format(address=address,
                        journal=journal_path)
        else:
            step["instruction"] = \
                _TREE_GATHER_INSTRUCTION.format(
                    address=address,
                    tool="sandbox.read",
                    journal=journal_path)
        step["tools"] = [
            copy.deepcopy(entry)
            for entry in catalogue
            if entry.get("tool") in (
                "sandbox.read", "sandbox.write")]
        if judged_mode == "native":
            step["call_shape"] = (
                "In this room your tools are offered "
                "natively: call the tool itself, with "
                "its arguments — sandbox.read with "
                "{\"path\": \"" + address + "\"}; "
                "sandbox.write with {\"path\": \""
                + str(journal_path) + "\", "
                "\"content\": \"<your journal as it "
                "stands, plus the new bits>\"}.")
        else:
            step["call_shape"] = (
                "In this room your tools are called "
                "in the text shape: your answer is "
                "one JSON object whose outcome is "
                "\"tool_requests\", with a requests "
                "list naming each call — the tool's "
                "name and its parameters, as in "
                "{\"tool\": \"sandbox.read\", "
                "\"parameters\": {\"path\": \""
                + address + "\"}}.")
    elif current["kind"] == "orient":
        first = next(
            (node for node in tstate["nodes"]
             if node["kind"] == "gather"), None)
        step["instruction"] = \
            _TREE_ORIENT_INSTRUCTION.format(
                address=first["address"]
                if first is not None else "")
        step["tools"] = []
    elif current["kind"] == "compose":
        step["instruction"] = _TREE_COMPOSE_INSTRUCTION
        step["points"] = list(_TREE_COMPOSE_POINTS)
        step["deliverable"] = deliverable_text
        step["figures"] = figures
        step["tools"] = []
        step["call_shape"] = (
            "The brief itself is delivered at the "
            "next step, as your contribution.")
    else:
        destination = tstate["root"]
        gathers_done = all(
            tstate["gather_facts"][node["id"]][
                "read_stands"]
            and tstate["gather_facts"][node["id"]][
                "journal_stands"]
            for node in tstate["nodes"]
            if node["kind"] == "gather")
        compose_done = gathers_done and any(
            node["kind"] == "compose"
            and tstate["states"][node["id"]] == "done"
            for node in tstate["nodes"])
        if compose_done:
            step["instruction"] = \
                _TREE_DELIVER_AGAIN_INSTRUCTION.format(
                    destination=destination)
        else:
            step["instruction"] = \
                _TREE_DELIVER_INSTRUCTION.format(
                    destination=destination)
        step["deliverable"] = deliverable_text
        step["figures"] = figures
        step["tools"] = []
        step["call_shape"] = (
            "Your answer is one JSON object: "
            "{\"outcome\": \"contribute\", \"text\": "
            "\"<the brief's text>\"}.")
    return step


def _derive_tree_core(events, state, gen, content,
                      iteration, payload,
                      prev_iteration_seq, bounds,
                      judged_mode=None):
    """The tree package's committed core for one
    iteration, reconstructed from the record alone —
    this checker's independent derivation of the
    loop's tree presentation (the room rebuild): the
    opening package at the first wake and one step
    package per tree step after, the tree's node
    states and the step gates' corrections derived
    from the recorded outcomes and gate events, the
    journal from the standing writes, the current
    step's fresh content presented once at its step,
    and the working set standing by its pointer form
    beside its own reconstructed hash. Returns None
    where the catalogue cannot be derived (reported
    by the catalogue verification itself) or the case
    carries no well-formed tree (reported at the
    assembly level by the tree's own verification)."""
    gp = gen["payload"]
    instance_id = gp.get("instance_id")
    seat = gp.get("seat")
    role = ((state.get("seats") or {}).get(seat)
            or {}).get("role")
    ceiling = bounds.get("step_ceiling") \
        if bounds is not None else None
    head = payload["cursor_to"]
    tstate = _tree_state(
        events, instance_id, head, content, iteration)
    if tstate is None:
        return None
    onboarding = (content or {}).get("onboarding")
    if not (isinstance(onboarding, dict)
            and isinstance(onboarding.get("headline"), str)
            and isinstance(onboarding.get("deliverable"), str)
            and isinstance(onboarding.get("text"), str)):
        onboarding = None
    headline = onboarding["headline"] \
        if onboarding is not None else \
        "The job in your briefcase"
    deliverable = onboarding["deliverable"] \
        if onboarding is not None else None
    sealed_delivery = gp.get("delivery")
    honoured_delivery = sealed_delivery if (
        isinstance(sealed_delivery, dict)
        and sealed_delivery.get("route")
        == _DELIVERY_ROUTE_CONTRIBUTION
        and (content or {}).get("delivery")
        == sealed_delivery) else None
    sealed_floor = gp.get("delivery_floor")
    honoured_floor = sealed_floor if (
        isinstance(sealed_floor, dict)
        and set(sealed_floor) == {"min_words"}
        and isinstance(
            sealed_floor.get("min_words"), int)
        and not isinstance(
            sealed_floor.get("min_words"), bool)
        and sealed_floor["min_words"] >= 1
        and (content or {}).get("delivery_floor")
        == sealed_floor
        and honoured_delivery is not None) else None
    if deliverable is None and \
            isinstance(honoured_delivery, dict):
        deliverable = honoured_delivery.get("destination")
    deliverable_text = deliverable \
        if isinstance(deliverable, str) else \
        "the deliverable named in your case"
    version = payload.get("registry_version")
    per_grant = gp.get("catalogue_contract") in \
        (_RETRIEVAL_CONTRACT, _EXEC_CONTRACT)
    catalogue, _ground = _derive_catalogue(
        gp.get("grants"), version, per_grant=per_grant)
    if catalogue is None:
        return None
    current = tstate["current"]
    package = {}
    package["seat"] = seat
    package["role"] = role
    package["instance_id"] = instance_id
    package["case_id"] = gp.get("case_id")
    package["case_version"] = gp.get("case_version")
    if iteration == 1:
        package["presentation"] = {
            "contract": _PRESENTATION_CONTRACT_V3,
            "package": "opening",
            "direction": _TREE_DIRECTION_OPENING}
        cover_statement = _TREE_COVER_FIRST.format(
            seat=seat, role=role, headline=headline,
            deliverable=deliverable_text)
    else:
        if current is None:
            current_label = "complete"
        elif current["kind"] == "gather":
            current_label = \
                f"gather {current['address']}"
        else:
            current_label = current["kind"]
        package["presentation"] = {
            "contract": _PRESENTATION_CONTRACT_V3,
            "package": "step",
            "step": current["id"]
            if current is not None else None,
            "direction": _TREE_DIRECTION_STEP}
        cover_statement = (
            f"{headline} — the deliverable: "
            f"{deliverable_text}. Step {iteration} of "
            f"{ceiling}; task in progress. Current "
            f"step: {current_label}.")
    package["cover"] = {
        "headline": headline,
        "deliverable": deliverable_text,
        "statement": cover_statement}
    content = content or {}
    if iteration == 1:
        package["snapshot"] = _staged_snapshot(content)
        role_memory = content.get("role_memory")
        package["memory"] = {
            "introduction": _STAGED_MEMORY_INTRO,
            "entries": copy.deepcopy(role_memory)
            if isinstance(role_memory, list) else []}
        essentials = {
            "part": content.get("part"),
            "evidence_boundary": copy.deepcopy(
                content.get("evidence_boundary")),
            "delivery": copy.deepcopy(content["delivery"])
            if isinstance(content.get("delivery"), dict)
            else None,
            "freshness": (
                "suspended — no freshness refusal "
                "applies to this job; your answers "
                "are judged on the work"
                if gp.get("freshness_guard")
                == _FRESHNESS_GUARD_SUSPENDED
                else "in force — your answers are "
                     "judged against the record as it "
                     "stood when you were woken")}
        opening = content.get("opening")
        if isinstance(opening, dict) and opening:
            essentials["opening"] = copy.deepcopy(opening)
        package["case_essentials"] = essentials
    package["process_tree"] = {
        "root": tstate["root"],
        "nodes": [
            dict(
                {"id": node["id"],
                 "kind": node["kind"]},
                **({"address": node["address"]}
                   if node["kind"] == "gather"
                   else {}),
                state=tstate["states"][node["id"]])
            for node in tstate["nodes"]]}
    if current is not None:
        package["current_step"] = _tree_step_component(
            tstate, catalogue, deliverable_text,
            honoured_floor, judged_mode)
    if iteration == 1:
        files = {"introduction": _TREE_FILES_INTRO,
                 "briefcase": []}
        glossary = content.get("glossary")
        if isinstance(glossary, list):
            for entry in glossary:
                if isinstance(entry, dict) and \
                        isinstance(entry.get("address"), str):
                    brief = {
                        "address": entry["address"],
                        "description":
                            entry.get("description")}
                    way = _staged_access_way(
                        catalogue, entry["address"])
                    if way is not None:
                        brief["access"] = way
                    files["briefcase"].append(brief)
        if tstate["journal_path"] is not None:
            files["journal"] = {
                "path": tstate["journal_path"],
                "label": _TREE_JOURNAL_LABEL}
        package["files"] = files
    # The call machinery at every wake, as the loop
    # builds it: the full catalogue stands in the
    # package's tools so any call resolves by name;
    # the presentation names only the current step's
    # own tools.
    package["tools"] = catalogue
    if tstate["journal_path"] is not None:
        package["journal"] = {
            "path": tstate["journal_path"],
            "label": _TREE_JOURNAL_LABEL,
            "content": tstate["journal_content"]}
    if prev_iteration_seq is not None:
        correction = None
        for ev in events:
            if ev["event_seq"] > payload["cursor_to"]:
                break
            if ev["type"] == "DELIVERY_GATE" and \
                    ev["payload"].get("assembly_id") \
                    == gp.get("assembly_id") and \
                    ev["payload"].get("iteration_seq") \
                    == prev_iteration_seq:
                correction = {
                    "what_arrived": ev["payload"].get(
                        "raw_excerpt"),
                    "response_length": ev["payload"].get(
                        "raw_length"),
                    "what_failed": ev["payload"].get(
                        "parse_error"),
                    "instruction": _STAGED_GATE_INSTRUCTION}
        if correction is not None:
            package["delivery_gate_correction"] = \
                correction
        stage_correction = None
        for ev in events:
            if ev["event_seq"] > payload["cursor_to"]:
                break
            if ev["type"] == "DELIVERY_STAGE_GATE" and \
                    ev["payload"].get("assembly_id") \
                    == gp.get("assembly_id") and \
                    ev["payload"].get("iteration_seq") \
                    == prev_iteration_seq:
                sp = ev["payload"]
                stage_correction = {
                    "what_arrived":
                        _tree_stage_gate_what_arrived(
                            sp.get("stage")),
                    "stage": sp.get("stage"),
                    "contribution_seq":
                        sp.get("contribution_seq"),
                    "text_sha256": sp.get("text_sha256"),
                    "instruction":
                        _TREE_STAGE_GATE_INSTRUCTION}
        if stage_correction is not None:
            package["delivery_stage_gate_correction"] = \
                stage_correction
        evidence_correction = None
        for ev in events:
            if ev["event_seq"] > payload["cursor_to"]:
                break
            if ev["type"] == "DELIVERY_EVIDENCE_GATE" and \
                    ev["payload"].get("assembly_id") \
                    == gp.get("assembly_id") and \
                    ev["payload"].get("iteration_seq") \
                    == prev_iteration_seq:
                ep = ev["payload"]
                missing = ep.get("missing")
                evidence_correction = {
                    "what_arrived":
                        _STAGED_EVIDENCE_GATE_WHAT_ARRIVED,
                    "contribution_seq":
                        ep.get("contribution_seq"),
                    "text_sha256": ep.get("text_sha256"),
                    "missing": missing,
                    "instruction":
                        _evidence_gate_instruction(
                            catalogue, missing)
                        if isinstance(missing, list)
                        else None}
        if evidence_correction is not None:
            package["delivery_evidence_gate_correction"] \
                = evidence_correction
        length_correction = None
        for ev in events:
            if ev["event_seq"] > payload["cursor_to"]:
                break
            if ev["type"] == "DELIVERY_LENGTH_GATE" and \
                    ev["payload"].get("assembly_id") \
                    == gp.get("assembly_id") and \
                    ev["payload"].get("iteration_seq") \
                    == prev_iteration_seq:
                lp = ev["payload"]
                count = lp.get("word_count")
                floor = lp.get("min_words")
                length_correction = {
                    "what_arrived":
                        _length_gate_what_arrived(count)
                        if isinstance(count, int)
                        and not isinstance(count, bool)
                        else None,
                    "contribution_seq":
                        lp.get("contribution_seq"),
                    "text_sha256": lp.get("text_sha256"),
                    "word_count": count,
                    "min_words": floor,
                    "instruction":
                        _STAGED_LENGTH_GATE_INSTRUCTION
                        .format(word_count=count,
                                min_words=floor)
                        if isinstance(count, int)
                        and not isinstance(count, bool)
                        and isinstance(floor, int)
                        and not isinstance(floor, bool)
                        else None}
        if length_correction is not None:
            package["delivery_length_gate_correction"] = \
                length_correction
        shape_correction = None
        for ev in events:
            if ev["event_seq"] > payload["cursor_to"]:
                break
            if ev["type"] == "TOOL_SHAPE_GATE" and \
                    ev["payload"].get("assembly_id") \
                    == gp.get("assembly_id") and \
                    ev["payload"].get("iteration_seq") \
                    == prev_iteration_seq:
                tool_name = ev["payload"].get("tool_name")
                first_address = None
                glossary = (content or {}).get("glossary")
                if isinstance(glossary, list):
                    for entry in glossary:
                        if isinstance(entry, dict) and \
                                isinstance(
                                    entry.get("address"),
                                    str):
                            first_address = \
                                entry["address"]
                            break
                shape_correction = \
                    _tool_shape_gate_correction(
                        tool_name, first_address) \
                    if isinstance(tool_name, str) \
                    and tool_name \
                    and first_address is not None \
                    else None
        if shape_correction is not None:
            package["tool_shape_gate_correction"] = \
                shape_correction
        step_correction = None
        for ev in events:
            if ev["event_seq"] > payload["cursor_to"]:
                break
            if ev["type"] == "STEP_GATE" and \
                    ev["payload"].get("assembly_id") \
                    == gp.get("assembly_id") and \
                    ev["payload"].get("iteration_seq") \
                    == prev_iteration_seq:
                sp = ev["payload"]
                missing = sp.get("missing")
                ahead = None
                if isinstance(missing, list):
                    # The ahead work the correction
                    # names is re-derived from the tree
                    # state at this wake, whichever of
                    # the step's needs the gate recorded
                    # — the same derivation the loop
                    # made when it built the correction.
                    owed = _tree_step_gate_owed(tstate)
                    ahead = owed[3] if owed is not None \
                        else None
                step_correction = _step_gate_correction(
                    sp.get("step"), sp.get("address"),
                    missing if isinstance(missing, list)
                    else [], ahead,
                    tstate["journal_path"]) \
                    if isinstance(missing, list) else None
        if step_correction is not None:
            package["step_gate_correction"] = \
                step_correction
    if iteration > 1 and current is not None and \
            current["kind"] == "gather":
        facts = tstate["gather_facts"][current["id"]]
        if facts["read_stands"]:
            earlier = [
                (ev["payload"].get("iteration"),
                 ev["payload"].get("cursor_to"))
                for ev in events
                if ev["type"] == "LOOP_ITERATION"
                and ev["payload"].get("assembly_id")
                == gp.get("assembly_id")
                and isinstance(
                    ev["payload"].get("iteration"), int)
                and ev["payload"].get("iteration")
                < iteration
                and isinstance(
                    ev["payload"].get("cursor_to"), int)]
            presented = _tree_presented_addresses(
                events, instance_id, content, earlier)
            if current["address"] not in presented:
                parts = [
                    {"served": copy.deepcopy(
                        entry["served"]),
                     "content": entry["content"]}
                    for entry in tstate["entries"]
                    if entry.get("path")
                    == current["address"]
                    and entry.get("tool") in (
                        "sandbox.read",
                        "sandbox.read_range")
                    and entry.get("content_carried")
                    and "content" in entry]
                if parts:
                    package["current_content"] = {
                        "address": current["address"],
                        "parts": parts}
    package["standing_dispatches"] = \
        _staged_standing_dispatches(
            events, instance_id, payload["cursor_to"])
    package["step_position"] = {
        "statement": f"step {iteration} of {ceiling}",
        "iteration": iteration,
        "step_ceiling": ceiling}
    package["task_status"] = "in progress"
    package["bounds"] = {
        "iteration": iteration,
        "steps_used": iteration - 1,
        "step_ceiling": ceiling,
        "deadline_seconds": bounds.get("deadline_seconds")
        if bounds is not None else None}
    package["position"] = payload["cursor_to"]
    package["tool_result_refs"] = _staged_tool_result_refs(
        events, instance_id, seat, gp.get("case_id"),
        payload.get("activated_seq"),
        payload["cursor_from"], payload["cursor_to"])
    expected_ws = _derive_working_set(
        events, instance_id, payload["cursor_to"])
    package["working_set_hash"] = _working_set_hash(
        expected_ws)
    package["working_set"] = \
        _derive_working_set_pointers(
            expected_ws, events,
            gp.get("assembly_id"), catalogue)
    return package


def _staged_journal_path(content):
    """The case's designated journal path under the same
    rule the loop's journal component applies — this
    checker's copy."""
    designated = (content or {}).get("journal")
    if not isinstance(designated, str) or \
            not designated.startswith("scratch/") or \
            ".." in designated.split("/"):
        return None
    return designated

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
    probed_routes = {}
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
        elif t == "ASSEMBLY_PROBED":
            # The assembly's own recorded route (Ben's
            # ruling, 2026-11-24): the translation
            # reconstruction below reads the wire-name
            # translation from it — the record's field,
            # never an inference from a model name.
            probed_routes.setdefault(p.get("assembly_id"),
                                     p.get("route"))

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

    def pinned_case_content(aid):
        """The assembly's pinned case version's content,
        from this checker's replayed state — or {} where
        it does not stand."""
        gen = generated.get(aid)
        if gen is None:
            return {}
        case = (state.get("cases") or {}).get(
            gen["payload"].get("case_id"))
        ver = ((case or {}).get("versions") or {}).get(
            str(gen["payload"].get("case_version"))) or {}
        return ver.get("content") or {}

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
    deliverable_filings = {}
    delivery_gates = {}
    delivery_stage_gates = {}
    delivery_evidence_gates = {}
    delivery_length_gates = {}
    tool_shape_gates = {}
    step_gates = {}
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
        elif t == "DELIVERABLE_FILED":
            aid = p.get("assembly_id")
            if ev["actor"] != _LOOP_ACTOR:
                problem("deliverable_filed_wrong_actor",
                        assembly_id=aid, at_seq=seq,
                        actor=ev["actor"])
            if binding_problems("deliverable_filed", ev,
                                aid):
                continue
            deliverable_filings.setdefault(
                aid, []).append(ev)
        elif t == "DELIVERY_GATE":
            aid = p.get("assembly_id")
            if ev["actor"] != _LOOP_ACTOR:
                problem("delivery_gate_wrong_actor",
                        assembly_id=aid, at_seq=seq,
                        actor=ev["actor"])
            if binding_problems("delivery_gate", ev, aid):
                continue
            delivery_gates.setdefault(aid, []).append(ev)
        elif t == "DELIVERY_STAGE_GATE":
            aid = p.get("assembly_id")
            if ev["actor"] != _LOOP_ACTOR:
                problem("delivery_stage_gate_wrong_actor",
                        assembly_id=aid, at_seq=seq,
                        actor=ev["actor"])
            if binding_problems("delivery_stage_gate",
                                ev, aid):
                continue
            delivery_stage_gates.setdefault(
                aid, []).append(ev)
        elif t == "DELIVERY_EVIDENCE_GATE":
            aid = p.get("assembly_id")
            if ev["actor"] != _LOOP_ACTOR:
                problem(
                    "delivery_evidence_gate_wrong_actor",
                    assembly_id=aid, at_seq=seq,
                    actor=ev["actor"])
            if binding_problems("delivery_evidence_gate",
                                ev, aid):
                continue
            delivery_evidence_gates.setdefault(
                aid, []).append(ev)
        elif t == "DELIVERY_LENGTH_GATE":
            aid = p.get("assembly_id")
            if ev["actor"] != _LOOP_ACTOR:
                problem(
                    "delivery_length_gate_wrong_actor",
                    assembly_id=aid, at_seq=seq,
                    actor=ev["actor"])
            if binding_problems("delivery_length_gate",
                                ev, aid):
                continue
            delivery_length_gates.setdefault(
                aid, []).append(ev)
        elif t == "TOOL_SHAPE_GATE":
            aid = p.get("assembly_id")
            if ev["actor"] != _LOOP_ACTOR:
                problem("tool_shape_gate_wrong_actor",
                        assembly_id=aid, at_seq=seq,
                        actor=ev["actor"])
            if binding_problems("tool_shape_gate",
                                ev, aid):
                continue
            tool_shape_gates.setdefault(
                aid, []).append(ev)
        elif t == "STEP_GATE":
            aid = p.get("assembly_id")
            if ev["actor"] != _LOOP_ACTOR:
                problem("step_gate_wrong_actor",
                        assembly_id=aid, at_seq=seq,
                        actor=ev["actor"])
            if binding_problems("step_gate", ev, aid):
                continue
            step_gates.setdefault(aid, []).append(ev)
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
        # The working-set contract's third case, in the
        # same shape: a declaration present but not the
        # contract this checker knows is divergent in
        # itself, reported once at the assembly level.
        ws_contract = gen["payload"].get(
            "working_set_contract") if gen is not None \
            else None
        if ws_contract is not None and \
                ws_contract != _WORKING_SET_CONTRACT:
            problem("working_set_contract_unknown",
                    assembly_id=aid, at_seq=activated[aid],
                    working_set_contract=ws_contract)
        # The freshness guard suspension's third case, in
        # the same shape (Ben's R31 ruling, 2026-11-24):
        # the one known value is the ruling's suspension;
        # a declaration naming anything else is a state
        # this checker does not understand, reported once
        # at the assembly level.
        freshness = gen["payload"].get(
            "freshness_guard") if gen is not None else None
        if freshness is not None and \
                freshness != _FRESHNESS_GUARD_SUSPENDED:
            problem("freshness_guard_unknown",
                    assembly_id=aid, at_seq=activated[aid],
                    freshness_guard=freshness)
        # The presentation contract's third case, in the
        # same shape (staged onboarding, INDEX 544): a
        # declaration present but not the contract this
        # checker knows is divergent in itself, reported
        # once at the assembly level. The contract's
        # population is the working-set population: a
        # presentation declaration standing without the
        # working-set declaration beside it is a broken
        # seal — the generator seals the two together or
        # not at all.
        presentation = gen["payload"].get(
            "presentation_contract") if gen is not None \
            else None
        if presentation is not None and \
                presentation not in (
                    _PRESENTATION_CONTRACT,
                    _PRESENTATION_CONTRACT_V2,
                    _PRESENTATION_CONTRACT_V3):
            problem("presentation_contract_unknown",
                    assembly_id=aid, at_seq=activated[aid],
                    presentation_contract=presentation)
        elif presentation in (
                _PRESENTATION_CONTRACT,
                _PRESENTATION_CONTRACT_V2,
                _PRESENTATION_CONTRACT_V3) and \
                ws_contract != _WORKING_SET_CONTRACT:
            problem("presentation_without_working_set",
                    assembly_id=aid, at_seq=activated[aid],
                    working_set_contract=ws_contract)
        if presentation == _PRESENTATION_CONTRACT_V3:
            # The process-tree successor (the room
            # rebuild): the contract's whole shape is
            # the tree sealed in the case — the pinned
            # case must carry it well-formed, its
            # gather steps naming the case's declared
            # delivery evidence in declaration order
            # and its root the case's delivery
            # destination. A tree standing in any other
            # shape is a broken seal, reported once
            # here; the presentation itself is verified
            # per iteration in the tree core's
            # reconstruction below.
            tree = _tree_nodes(pinned_case_content(aid))
            if tree is None:
                problem("process_tree_missing",
                        assembly_id=aid,
                        at_seq=activated[aid])
            else:
                case_content = pinned_case_content(aid)
                evidence = case_content.get(
                    "delivery_evidence")
                declared = evidence.get("addresses") \
                    if isinstance(evidence, dict) \
                    else None
                gathered = [node["address"]
                            for node in tree["nodes"]
                            if node["kind"] == "gather"]
                delivery = case_content.get("delivery")
                destination = delivery.get(
                    "destination") \
                    if isinstance(delivery, dict) \
                    else None
                if gathered != declared or \
                        (destination is not None
                         and tree["root"] != destination):
                    problem("process_tree_mismatch",
                            assembly_id=aid,
                            at_seq=activated[aid],
                            gathered=gathered,
                            declared=declared,
                            root=tree["root"],
                            destination=destination)
        # The worked example's seal (round nine's
        # correction pair, INDEX 548): the generator
        # seals the office's demonstration call beside
        # the presentation contract, on a glossary file
        # of the pinned case, its result whole and
        # internally consistent. A seal standing
        # anywhere else, or in any other shape, claims
        # a demonstration the office never made and is
        # divergent in itself, reported once here; the
        # presentation itself is verified per iteration
        # in the staged core's reconstruction. The file
        # it names is the contract's own rule (the
        # calibration): under the first contract, the
        # glossary's first address exactly; under the
        # pointer-rule successor, one of the glossary's
        # addresses — the office's choice, the read it
        # demonstrates on the smallest file so the
        # stage stays within its bound.
        example = gen["payload"].get("worked_example") \
            if gen is not None else None
        if example is not None:
            if presentation not in (
                    _PRESENTATION_CONTRACT,
                    _PRESENTATION_CONTRACT_V2,
                    _PRESENTATION_CONTRACT_V3):
                problem("worked_example_without_"
                        "presentation",
                        assembly_id=aid,
                        at_seq=activated[aid],
                        presentation_contract=presentation)
            elif not _worked_example_well_formed(
                    example, presentation):
                problem("worked_example_malformed",
                        assembly_id=aid,
                        at_seq=activated[aid])
            else:
                glossary = pinned_case_content(aid).get(
                    "glossary")
                addresses = []
                if isinstance(glossary, list):
                    for entry in glossary:
                        if isinstance(entry, dict) and \
                                isinstance(
                                    entry.get("address"),
                                    str):
                            addresses.append(
                                entry["address"])
                if presentation in (
                        _PRESENTATION_CONTRACT_V2,
                        _PRESENTATION_CONTRACT_V3):
                    path_ok = example.get("path") \
                        in addresses
                else:
                    path_ok = bool(addresses) and \
                        example.get("path") == addresses[0]
                if not path_ok:
                    problem("worked_example_path_mismatch",
                            assembly_id=aid,
                            at_seq=activated[aid],
                            path=example.get("path"),
                            glossary_addresses=addresses)
        # The delivery declaration (door scope,
        # 2026-11-24): the generator seals the pinned
        # case's declaration into the assembly's record;
        # the two must be one declaration. A sealed route
        # this checker does not know is divergent in
        # itself; a case declaration standing unsealed, or
        # a seal naming anything but the case's word, is
        # a broken binding.
        delivery = gen["payload"].get(
            "delivery") if gen is not None else None
        case_delivery = pinned_case_content(aid).get(
            "delivery")
        if delivery is not None:
            if not isinstance(delivery, dict) or \
                    set(delivery) != {"destination",
                                      "route"} or \
                    not isinstance(
                        delivery.get("destination"), str) \
                    or not delivery.get("destination") \
                    or not isinstance(
                        delivery.get("route"), str) \
                    or not delivery.get("route"):
                problem("delivery_declaration_malformed",
                        assembly_id=aid,
                        at_seq=activated[aid],
                        delivery=delivery)
            elif delivery.get("route") != \
                    _DELIVERY_ROUTE_CONTRIBUTION:
                problem("delivery_route_unknown",
                        assembly_id=aid,
                        at_seq=activated[aid],
                        route=delivery.get("route"))
            elif case_delivery != delivery:
                problem("delivery_declaration_mismatch",
                        assembly_id=aid,
                        at_seq=activated[aid])
        elif case_delivery is not None:
            problem("delivery_declaration_unsealed",
                    assembly_id=aid, at_seq=activated[aid])
        # The delivery-evidence declaration (round ten,
        # INDEX 552): the generator seals the pinned
        # case's component into the assembly's record
        # beside the delivery declaration; the two must
        # be one declaration, well-formed — and the seal
        # stands only where the door it guards and the
        # working-set contract stand, since the gate it
        # names reads the worker's working set.
        evidence = gen["payload"].get(
            "delivery_evidence") if gen is not None \
            else None
        case_evidence = pinned_case_content(aid).get(
            "delivery_evidence")
        if evidence is not None:
            if not isinstance(evidence, dict) or \
                    set(evidence) != {"addresses"} or \
                    not isinstance(
                        evidence.get("addresses"), list) or \
                    not evidence["addresses"] or \
                    any(not isinstance(address, str)
                        or not address
                        for address in
                        evidence["addresses"]):
                problem(
                    "delivery_evidence_declaration_"
                    "malformed",
                    assembly_id=aid,
                    at_seq=activated[aid],
                    delivery_evidence=evidence)
            elif case_evidence != evidence:
                problem(
                    "delivery_evidence_declaration_"
                    "mismatch",
                    assembly_id=aid,
                    at_seq=activated[aid])
            elif delivery is None:
                problem("delivery_evidence_without_"
                        "delivery",
                        assembly_id=aid,
                        at_seq=activated[aid])
            elif gen["payload"].get(
                    "working_set_contract") != \
                    _WORKING_SET_CONTRACT:
                problem("delivery_evidence_without_"
                        "working_set",
                        assembly_id=aid,
                        at_seq=activated[aid])
        elif case_evidence is not None:
            problem("delivery_evidence_declaration_"
                    "unsealed",
                    assembly_id=aid, at_seq=activated[aid])
        # The delivery-length declaration (the third
        # gate, INDEX 557): the generator seals the
        # pinned case's component into the assembly's
        # record beside the delivery declaration; the
        # two must be one declaration, well-formed —
        # and the seal stands only where the door it
        # guards stands, since the floor is a property
        # of the delivery. The working set is not asked
        # of it: the floor's subject is the contributed
        # text, which stands wherever the door stands.
        floor = gen["payload"].get(
            "delivery_floor") if gen is not None \
            else None
        case_floor = pinned_case_content(aid).get(
            "delivery_floor")
        if floor is not None:
            if not isinstance(floor, dict) or \
                    set(floor) != {"min_words"} or \
                    not isinstance(
                        floor.get("min_words"), int) or \
                    isinstance(
                        floor.get("min_words"), bool) or \
                    floor["min_words"] < 1:
                problem(
                    "delivery_floor_declaration_"
                    "malformed",
                    assembly_id=aid,
                    at_seq=activated[aid],
                    delivery_floor=floor)
            elif case_floor != floor:
                problem(
                    "delivery_floor_declaration_"
                    "mismatch",
                    assembly_id=aid,
                    at_seq=activated[aid])
            elif delivery is None:
                problem("delivery_floor_without_"
                        "delivery",
                        assembly_id=aid,
                        at_seq=activated[aid])
        elif case_floor is not None:
            problem("delivery_floor_declaration_"
                    "unsealed",
                    assembly_id=aid, at_seq=activated[aid])

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
                    # The retrieval regime's assemblies
                    # are catalogued per grant (INDEX 257):
                    # the reconstruction follows the sealed
                    # declaration, as the loop's derivation
                    # follows the doorway's governed test.
                    # The regime's declarations are the
                    # retrieval contract's and — for the
                    # combined configuration (INDEX 476) —
                    # the exec contract's; a single-grant
                    # exec assembly derives identically
                    # under either reading, so its standing
                    # records are untouched.
                    per_grant = gen is not None and \
                        gen["payload"].get(
                            "catalogue_contract") in \
                        (_RETRIEVAL_CONTRACT, _EXEC_CONTRACT)
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
            # Working-set carriage (the run-3 correction):
            # the commitment of the presented working set.
            # The assembly's sealed declaration governs, in
            # the catalogue commitment's shape: a declared
            # assembly owes the hash on every iteration, and
            # its absence is divergent in itself; where a
            # hash stands it is verified against the working
            # set this checker independently reconstructs
            # from the recorded outcomes at or before the
            # iteration's cursor close — the exact set the
            # package at that head must have presented,
            # contents, provenance, dedupe and budget
            # behaviour alike. An assembly declaring an
            # unknown working-set contract is not governed
            # here; it stands reported once at the assembly
            # level above.
            ws_declared = gen is not None and \
                gen["payload"].get("working_set_contract") \
                == _WORKING_SET_CONTRACT
            recorded_ws = p.get("working_set_hash")
            if ws_declared and recorded_ws is None:
                problem("working_set_commitment_missing",
                        assembly_id=aid, at_seq=seq)
            elif recorded_ws is not None and \
                    gen is not None and \
                    isinstance(p.get("cursor_to"), int) and \
                    not isinstance(p.get("cursor_to"), bool):
                expected_ws = _derive_working_set(
                    events, gen["payload"].get("instance_id"),
                    p.get("cursor_to"))
                if _working_set_hash(expected_ws) \
                        != recorded_ws:
                    problem("working_set_hash_mismatch",
                            assembly_id=aid, at_seq=seq)
            # Staged onboarding (INDEX 544): the
            # presentation commitment, in the working-set
            # commitment's shape. The assembly's sealed
            # declaration governs: a declared assembly owes
            # the hash on every iteration, and its absence
            # is divergent in itself; where a hash stands
            # it is verified against the staged package
            # this checker independently reconstructs from
            # the record — stage order and contents, the
            # dashboard's shape, the absence of the case
            # dump — so a skipped stage or a smuggled dump
            # diverges. An assembly declaring an unknown
            # presentation contract is not governed here;
            # it stands reported once at the assembly level
            # above.
            pres_declared = gen is not None and \
                gen["payload"].get("presentation_contract") \
                in (_PRESENTATION_CONTRACT,
                    _PRESENTATION_CONTRACT_V2,
                    _PRESENTATION_CONTRACT_V3)
            recorded_ph = p.get("presentation_hash")
            if pres_declared and recorded_ph is None:
                problem("presentation_commitment_missing",
                        assembly_id=aid, at_seq=seq)
            elif pres_declared and recorded_ph is not None \
                    and isinstance(p.get("cursor_to"), int) \
                    and not isinstance(p.get("cursor_to"),
                                       bool) \
                    and isinstance(p.get("cursor_from"), int) \
                    and not isinstance(p.get("cursor_from"),
                                       bool):
                prev_seq = evs[n - 2]["event_seq"] \
                    if n >= 2 else None
                if gen["payload"].get(
                        "presentation_contract") == \
                        _PRESENTATION_CONTRACT_V3:
                    expected_core = _derive_tree_core(
                        events, state, gen,
                        pinned_case_content(aid), n, p,
                        prev_seq, bounds,
                        judged_mode=judged_modes.get(aid))
                else:
                    expected_core = _derive_staged_core(
                        events, state, gen,
                        pinned_case_content(aid), n, p,
                        prev_seq, bounds)
                if expected_core is None or \
                        sha256_hex(canonical(
                            expected_core)) != recorded_ph:
                    problem("presentation_hash_mismatch",
                            assembly_id=aid, at_seq=seq)
        stall = stalls.get(aid)
        if stall is not None:
            for ev in evs:
                if ev["event_seq"] > stall["event_seq"]:
                    problem("iteration_after_stall",
                            assembly_id=aid,
                            at_seq=ev["event_seq"])

    # The door's events (door scope, 2026-11-24),
    # verified against the events themselves: a filing
    # files a standing contribution of this assembly's
    # instance, at the declared destination, with the
    # filed hash equal to the contribution text's hash,
    # authored by the worker and filed by the office —
    # and it is the activation's last word: no iteration
    # and no stall follows it. A gate binds a standing
    # iteration and carries a bounded excerpt of what
    # arrived and the parse failure that answered it.
    _events_by_seq = {ev["event_seq"]: ev for ev in events}
    for aid, evs in deliverable_filings.items():
        gen = generated.get(aid)
        delivery = gen["payload"].get("delivery") \
            if gen is not None else None
        for ev in evs:
            p = ev["payload"]
            seq = ev["event_seq"]
            if not isinstance(delivery, dict) or \
                    p.get("destination") != delivery.get(
                        "destination"):
                problem("deliverable_filed_destination_"
                        "mismatch", assembly_id=aid,
                        at_seq=seq)
            contribution = _events_by_seq.get(
                p.get("contribution_seq"))
            if contribution is None or \
                    contribution["type"] != "CONTRIBUTION":
                problem("deliverable_filed_without_"
                        "contribution", assembly_id=aid,
                        at_seq=seq)
                continue
            cp = contribution["payload"]
            if cp.get("instance_id") != (gen or {}).get(
                    "payload", {}).get("instance_id"):
                problem("deliverable_filed_contribution_"
                        "binding_mismatch", assembly_id=aid,
                        at_seq=seq)
            if p.get("authored_by") != \
                    contribution["actor"]:
                problem("deliverable_filed_author_mismatch",
                        assembly_id=aid, at_seq=seq)
            if p.get("filed_by") != "office":
                problem("deliverable_filed_filer_mismatch",
                        assembly_id=aid, at_seq=seq)
            text = cp.get("text")
            digest = hashlib.sha256(
                text.encode("utf-8")).hexdigest() \
                if isinstance(text, str) else None
            if digest is None or \
                    p.get("content_sha256") != digest:
                problem("deliverable_filed_hash_mismatch",
                        assembly_id=aid, at_seq=seq)
            for later in iterations.get(aid, []):
                if later["event_seq"] > seq:
                    problem("iteration_after_filing",
                            assembly_id=aid,
                            at_seq=later["event_seq"])
            if aid in stalls and \
                    stalls[aid]["event_seq"] > seq:
                problem("stall_after_filing",
                        assembly_id=aid, at_seq=seq)
            # The stage gate's word (INDEX 548): a
            # contribution the gate set aside unfiled
            # may never stand filed — a filing naming a
            # gated contribution is the shortcut the
            # gate exists to close, recorded as done.
            if any(g["payload"].get("contribution_seq")
                   == p.get("contribution_seq")
                   for g in delivery_stage_gates.get(
                       aid, [])):
                problem("deliverable_filed_from_stage_"
                        "gated_contribution",
                        assembly_id=aid, at_seq=seq)
            # The evidence gate's word (INDEX 552): a
            # contribution the gate set aside unfiled
            # may never stand filed, and no filing may
            # stand at all where the case's named
            # evidence did not stand gathered at the
            # filing's own contribution — the standing
            # computation is re-derived here from the
            # recorded dispatches and outcomes alone.
            if any(g["payload"].get("contribution_seq")
                   == p.get("contribution_seq")
                   for g in delivery_evidence_gates.get(
                       aid, [])):
                problem("deliverable_filed_from_evidence_"
                        "gated_contribution",
                        assembly_id=aid, at_seq=seq)
            evidence = (gen or {}).get("payload", {}).get(
                "delivery_evidence")
            if isinstance(evidence, dict) and \
                    set(evidence) == {"addresses"} and \
                    isinstance(
                        evidence.get("addresses"), list) \
                    and evidence["addresses"] and \
                    pinned_case_content(aid).get(
                        "delivery_evidence") == evidence:
                missing = _delivery_evidence_missing(
                    events,
                    (gen or {}).get("payload", {}).get(
                        "instance_id"),
                    p.get("contribution_seq"),
                    evidence["addresses"])
                if missing:
                    problem("deliverable_filed_with_"
                            "evidence_missing",
                            assembly_id=aid, at_seq=seq,
                            missing=missing)
            # The length gate's word (INDEX 557): a
            # contribution the gate set aside unfiled
            # may never stand filed, and no filing may
            # stand at all where the filed text, counted
            # from the record itself, falls short of
            # the case's declared floor.
            if any(g["payload"].get("contribution_seq")
                   == p.get("contribution_seq")
                   for g in delivery_length_gates.get(
                       aid, [])):
                problem("deliverable_filed_from_length_"
                        "gated_contribution",
                        assembly_id=aid, at_seq=seq)
            floor = (gen or {}).get("payload", {}).get(
                "delivery_floor")
            if isinstance(floor, dict) and \
                    set(floor) == {"min_words"} and \
                    isinstance(
                        floor.get("min_words"), int) and \
                    not isinstance(
                        floor.get("min_words"), bool) and \
                    floor["min_words"] >= 1 and \
                    pinned_case_content(aid).get(
                        "delivery_floor") == floor and \
                    isinstance(text, str):
                if len(text.split()) < floor["min_words"]:
                    problem("deliverable_filed_below_"
                            "length_floor",
                            assembly_id=aid, at_seq=seq,
                            word_count=len(text.split()),
                            min_words=floor["min_words"])
    for aid, evs in delivery_gates.items():
        iteration_seqs = {ev["event_seq"] for ev in
                          iterations.get(aid, [])}
        for ev in evs:
            p = ev["payload"]
            seq = ev["event_seq"]
            if p.get("iteration_seq") not in \
                    iteration_seqs:
                problem("delivery_gate_iteration_mismatch",
                        assembly_id=aid, at_seq=seq)
            excerpt = p.get("raw_excerpt")
            length = p.get("raw_length")
            if not isinstance(excerpt, str) or \
                    len(excerpt) > 500 or \
                    not isinstance(length, int) or \
                    isinstance(length, bool) or \
                    length < len(excerpt) or \
                    not isinstance(
                        p.get("parse_error"), str) or \
                    not p.get("parse_error"):
                problem("delivery_gate_payload_malformed",
                        assembly_id=aid, at_seq=seq)

    # The stage gate's events (round nine's correction
    # pair, INDEX 548), verified against the record
    # itself: a gate binds a standing iteration of a
    # presentation-declared assembly, names the stage
    # that iteration's wake presented — one of the
    # three stages before the task — and the
    # contribution it set aside, whose text must hash
    # to the gate's digest, with nothing filed. The
    # correction the gate owes the next package is
    # verified in the staged core's reconstruction
    # above: a package omitting it diverges from its
    # recorded commitment.
    for aid, evs in delivery_stage_gates.items():
        gen = generated.get(aid)
        declared = gen is not None and \
            gen["payload"].get("presentation_contract") \
            in (_PRESENTATION_CONTRACT,
                _PRESENTATION_CONTRACT_V2,
                _PRESENTATION_CONTRACT_V3)
        tree_form = gen is not None and \
            gen["payload"].get("presentation_contract") \
            == _PRESENTATION_CONTRACT_V3
        iteration_numbers = {
            ev["event_seq"]: ev["payload"].get("iteration")
            for ev in iterations.get(aid, [])}
        iteration_heads = {
            ev["event_seq"]: ev["payload"].get("cursor_to")
            for ev in iterations.get(aid, [])}
        for ev in evs:
            p = ev["payload"]
            seq = ev["event_seq"]
            if not declared:
                problem("delivery_stage_gate_without_"
                        "presentation",
                        assembly_id=aid, at_seq=seq)
            number = iteration_numbers.get(
                p.get("iteration_seq"))
            if number is None:
                problem("delivery_stage_gate_iteration_"
                        "mismatch",
                        assembly_id=aid, at_seq=seq)
                continue
            if tree_form:
                # The tree's progression replaces the
                # stage gate's function under this
                # contract (the room rebuild): the gate's
                # stage is the tree's current node at the
                # bound iteration's package head, derived
                # from the record — and it is never a
                # step the door stands open at.
                tstate = _tree_state(
                    events,
                    (gen["payload"].get("instance_id")),
                    iteration_heads.get(
                        p.get("iteration_seq")),
                    pinned_case_content(aid), number)
                node = tstate["current"] \
                    if tstate is not None else None
                if node is None or \
                        p.get("stage") != node["id"] or \
                        node["kind"] in (
                            "compose", "deliver"):
                    problem("delivery_stage_gate_stage_"
                            "mismatch",
                            assembly_id=aid, at_seq=seq)
            elif p.get("stage") != _staged_stage(number) \
                    or p.get("stage") not in (
                        "memory", "case", "files"):
                problem("delivery_stage_gate_stage_"
                        "mismatch",
                        assembly_id=aid, at_seq=seq)
            contribution = _events_by_seq.get(
                p.get("contribution_seq"))
            text = (contribution or {}).get(
                "payload", {}).get("text") \
                if contribution is not None else None
            digest = hashlib.sha256(
                text.encode("utf-8")).hexdigest() \
                if isinstance(text, str) else None
            if contribution is None or \
                    contribution["type"] != "CONTRIBUTION" \
                    or digest is None or \
                    digest != p.get("text_sha256") or \
                    p.get("filed") is not False:
                problem("delivery_stage_gate_payload_"
                        "malformed",
                        assembly_id=aid, at_seq=seq)

    # The evidence gate's events (round ten, INDEX 552),
    # verified against the record itself: a gate binds a
    # standing iteration of an evidence-declared
    # assembly, names the contribution it set aside —
    # whose text must hash to the gate's digest, with
    # nothing filed — and names exactly the addresses
    # the standing computation, re-derived at that
    # contribution from the recorded dispatches and
    # outcomes alone, finds missing. The correction the
    # gate owes the next package is verified in the
    # staged core's reconstruction above where the
    # presentation contract stands.
    for aid, evs in delivery_evidence_gates.items():
        gen = generated.get(aid)
        evidence = (gen or {}).get("payload", {}).get(
            "delivery_evidence")
        declared = isinstance(evidence, dict) and \
            set(evidence) == {"addresses"} and \
            isinstance(evidence.get("addresses"), list) \
            and bool(evidence["addresses"]) and \
            all(isinstance(address, str) and address
                for address in evidence["addresses"]) and \
            pinned_case_content(aid).get(
                "delivery_evidence") == evidence
        iteration_seqs = {ev["event_seq"] for ev in
                          iterations.get(aid, [])}
        for ev in evs:
            p = ev["payload"]
            seq = ev["event_seq"]
            if not declared:
                problem("delivery_evidence_gate_without_"
                        "declaration",
                        assembly_id=aid, at_seq=seq)
            if p.get("iteration_seq") not in \
                    iteration_seqs:
                problem("delivery_evidence_gate_"
                        "iteration_mismatch",
                        assembly_id=aid, at_seq=seq)
                continue
            contribution = _events_by_seq.get(
                p.get("contribution_seq"))
            text = (contribution or {}).get(
                "payload", {}).get("text") \
                if contribution is not None else None
            digest = hashlib.sha256(
                text.encode("utf-8")).hexdigest() \
                if isinstance(text, str) else None
            if contribution is None or \
                    contribution["type"] != "CONTRIBUTION" \
                    or digest is None or \
                    digest != p.get("text_sha256") or \
                    p.get("filed") is not False or \
                    not isinstance(
                        p.get("missing"), list):
                problem("delivery_evidence_gate_payload_"
                        "malformed",
                        assembly_id=aid, at_seq=seq)
                continue
            if declared:
                recomputed = _delivery_evidence_missing(
                    events,
                    (gen or {}).get("payload", {}).get(
                        "instance_id"),
                    p.get("contribution_seq"),
                    evidence["addresses"])
                if p.get("missing") != recomputed:
                    problem("delivery_evidence_gate_"
                            "missing_mismatch",
                            assembly_id=aid, at_seq=seq,
                            recorded=p.get("missing"),
                            recomputed=recomputed)

    # The length gate's events (the third gate, INDEX
    # 557), verified against the record itself: a gate
    # binds a standing iteration of a floor-declared
    # assembly, names the contribution it set aside —
    # whose text must hash to the gate's digest, with
    # nothing filed — and names the count that text
    # arrived with, re-derived from the recorded text
    # itself, and the floor it fell short of, which
    # must be the declaration's own. The correction the
    # gate owes the next package is verified in the
    # staged core's reconstruction above where the
    # presentation contract stands.
    for aid, evs in delivery_length_gates.items():
        gen = generated.get(aid)
        floor = (gen or {}).get("payload", {}).get(
            "delivery_floor")
        declared = isinstance(floor, dict) and \
            set(floor) == {"min_words"} and \
            isinstance(floor.get("min_words"), int) and \
            not isinstance(
                floor.get("min_words"), bool) and \
            floor["min_words"] >= 1 and \
            pinned_case_content(aid).get(
                "delivery_floor") == floor
        iteration_seqs = {ev["event_seq"] for ev in
                          iterations.get(aid, [])}
        for ev in evs:
            p = ev["payload"]
            seq = ev["event_seq"]
            if not declared:
                problem("delivery_length_gate_without_"
                        "declaration",
                        assembly_id=aid, at_seq=seq)
            if p.get("iteration_seq") not in \
                    iteration_seqs:
                problem("delivery_length_gate_"
                        "iteration_mismatch",
                        assembly_id=aid, at_seq=seq)
                continue
            contribution = _events_by_seq.get(
                p.get("contribution_seq"))
            text = (contribution or {}).get(
                "payload", {}).get("text") \
                if contribution is not None else None
            digest = hashlib.sha256(
                text.encode("utf-8")).hexdigest() \
                if isinstance(text, str) else None
            if contribution is None or \
                    contribution["type"] != "CONTRIBUTION" \
                    or digest is None or \
                    digest != p.get("text_sha256") or \
                    p.get("filed") is not False or \
                    not isinstance(
                        p.get("word_count"), int) or \
                    isinstance(
                        p.get("word_count"), bool) or \
                    not isinstance(
                        p.get("min_words"), int) or \
                    isinstance(
                        p.get("min_words"), bool):
                problem("delivery_length_gate_payload_"
                        "malformed",
                        assembly_id=aid, at_seq=seq)
                continue
            if isinstance(text, str) and \
                    p.get("word_count") \
                    != len(text.split()):
                problem("delivery_length_gate_count_"
                        "mismatch",
                        assembly_id=aid, at_seq=seq,
                        recorded=p.get("word_count"),
                        recomputed=len(text.split()))
            if declared and \
                    p.get("min_words") \
                    != floor["min_words"]:
                problem("delivery_length_gate_floor_"
                        "mismatch",
                        assembly_id=aid, at_seq=seq,
                        recorded=p.get("min_words"),
                        declared=floor["min_words"])
            if isinstance(text, str) and \
                    len(text.split()) \
                    >= p.get("min_words"):
                problem("delivery_length_gate_not_"
                        "below_floor",
                        assembly_id=aid, at_seq=seq,
                        word_count=len(text.split()),
                        min_words=p.get("min_words"))

    # The tool-shape gate's events (the calibration),
    # verified against the record itself: a gate binds
    # a standing iteration of a text-judged assembly
    # (the refusal exists only where no native tools
    # were offered), and its payload is the provider's
    # refusal as it arrived — the status it observed
    # (400, or None where the seam observed none), the
    # tool_use_failed code, the refusal's message, the
    # tool the failed generation named, and the failed
    # generation itself, which must parse to a call
    # naming that same tool. The correction the gate
    # owes the next package is verified in the staged
    # core's reconstruction above where the
    # presentation contract stands.
    for aid, evs in tool_shape_gates.items():
        judged_text = judged_modes.get(aid) == "text"
        iteration_seqs = {ev["event_seq"] for ev in
                          iterations.get(aid, [])}
        for ev in evs:
            p = ev["payload"]
            seq = ev["event_seq"]
            if not judged_text:
                problem("tool_shape_gate_without_text_"
                        "judgement",
                        assembly_id=aid, at_seq=seq)
            if p.get("iteration_seq") not in \
                    iteration_seqs:
                problem("tool_shape_gate_iteration_"
                        "mismatch",
                        assembly_id=aid, at_seq=seq)
                continue
            status = p.get("http_status")
            failed = p.get("failed_generation")
            generation = None
            if isinstance(failed, str) and failed:
                try:
                    generation = json.loads(failed)
                except ValueError:
                    generation = None
            if (status is not None and status != 400) \
                    or p.get("error_code") \
                    != "tool_use_failed" \
                    or not isinstance(
                        p.get("error_message"), str) \
                    or not isinstance(
                        p.get("tool_name"), str) \
                    or not p.get("tool_name") \
                    or not isinstance(generation, dict) \
                    or generation.get("name") \
                    != p.get("tool_name"):
                problem("tool_shape_gate_payload_"
                        "malformed",
                        assembly_id=aid, at_seq=seq)

    # The step gate's events (the room rebuild, the
    # process-tree contract), verified against the
    # record itself: a gate binds a standing iteration
    # of a tree-declared assembly and stands before the
    # following iteration (it is recorded while that
    # iteration's package is built), and its facts —
    # the step, its source, and what the step still
    # needs — are exactly what the step-gate derivation
    # finds owed at the following iteration's package
    # head, re-derived from the recorded dispatches and
    # outcomes alone. The correction the gate owes the
    # following package is verified in the tree core's
    # reconstruction above.
    for aid, evs in step_gates.items():
        gen = generated.get(aid)
        declared = gen is not None and \
            gen["payload"].get("presentation_contract") \
            == _PRESENTATION_CONTRACT_V3
        by_number = {
            ev["payload"].get("iteration"): ev
            for ev in iterations.get(aid, [])}
        number_by_seq = {
            ev["event_seq"]: ev["payload"].get("iteration")
            for ev in iterations.get(aid, [])}
        for ev in evs:
            p = ev["payload"]
            seq = ev["event_seq"]
            if not declared:
                problem("step_gate_without_tree_"
                        "declaration",
                        assembly_id=aid, at_seq=seq)
            number = number_by_seq.get(
                p.get("iteration_seq"))
            if number is None:
                problem("step_gate_iteration_mismatch",
                        assembly_id=aid, at_seq=seq)
                continue
            following = by_number.get(number + 1)
            if following is None:
                continue
            if seq >= following["event_seq"]:
                problem("step_gate_position_mismatch",
                        assembly_id=aid, at_seq=seq)
                continue
            tstate = _tree_state(
                events, gen["payload"].get("instance_id"),
                following["payload"].get("cursor_to"),
                pinned_case_content(aid), number + 1)
            owed = _tree_step_gate_owed(tstate) \
                if tstate is not None else None
            if owed is None or \
                    p.get("step") != owed[0] or \
                    p.get("address") != owed[1] or \
                    p.get("missing") != owed[2]:
                problem("step_gate_facts_mismatch",
                        assembly_id=aid, at_seq=seq,
                        recorded_step=p.get("step"),
                        recorded_missing=p.get("missing"),
                        derived=owed)

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
            gen["payload"].get("catalogue_contract") in \
            (_RETRIEVAL_CONTRACT, _EXEC_CONTRACT)
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
                            ip.get("iteration"),
                            route=probed_routes.get(aid))
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
