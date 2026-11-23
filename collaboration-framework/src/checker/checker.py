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
- seal correspondence, bidirectionally (C5).

It opens the store read-only with its own SQL, writes nothing,
creates no store, and leaves no artifacts (C7). It imports
`fabric.canonical` — the record-format and hashing primitive —
and the standard library only; never a `framework.*` module.
"""
import json
import os
import sqlite3
import sys

from fabric.canonical import canonical, event_hash

from checker.replay import replay_events
from checker.schema import SCHEMA

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
