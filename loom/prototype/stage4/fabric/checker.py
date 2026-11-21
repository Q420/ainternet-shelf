"""The independent checker — Loom spec v0.1 Rev 9, section 7.

Stage 4 (2026-11-21). This module is the separately implemented
checker the constitution requires: its own implementation of the
check functions, executed as a separate process against the event
history. It is NOT a second entry point into the engine's logic.
It imports exactly one fabric module — fabric.canonical, the
format primitives (canonical JSON, SHA-256, the event hash) that
define the record format itself — plus the Python standard
library. It does not import the engine, the harness, the service,
the store, the fixture, or the client, directly or transitively
(validation pack VP-28 audits this). Everything else it needs —
the constitution hash, the region set, the pinned pack digest —
arrives as data in the request.

What it independently implements, from the spec text:

- chain verification and the event fold (section 3's
  reconstruction contract), including the Stage 3 transition
  legality (a tension is raised only in its permitted
  type/origin/initial-status combination and moves only along
  its type's transitions; facet statuses stay inside section 5's
  enumeration and name only the six frozen regions), IDLE as
  evidence-only under Amendment A1 with the authority set bound
  in RUN_OPENED enforced (VP-15), and the malformed-payload
  hardening: a hash-valid event with unhashable or wrongly typed
  fields halts the fold with a controlled, classed halt — never
  a native exception. Halt classes are the validation pack's
  pinned taxonomy: hash_chain_invalid, sequence_invalid,
  schema_invalid, protocol_transition_invalid.
- the structural checks S1 (dependency integrity), S2 (version
  monotonicity), S3 (pattern acyclicity) over a derived state;
- seal attempt evaluation under the pack's C1 precedence: the
  checks run against the live snapshot L; a failed check governs
  (FAIL) even when L diverges from the independently folded R;
  MISMATCH is reserved for divergence no failed check explains;
  PASS requires L = R with every check passing;
- structural-tension identity (check name + canonically ordered
  affected record set), deduplication against the open tensions
  folded from the committed history, and resolution — which
  re-runs the tension's own check against its original affected
  set and fires only when that inconsistency no longer exists.

Interface (build notes, section 2 — the contract of record): the
process reads one JSON request object from stdin and writes one
JSON verdict object to stdout, exiting 0 for every well-formed
verdict. Modes: "fold" and "evaluate". In evaluate mode the
committed history arrives either as a store path (opened
read-only by this process itself) or as inline event data; the
staged candidate batch is a separate, explicit input whose
ABSENCE is itself a verdict (refused — VP-25); the live snapshot
is evidence, never authority.
"""
import copy
import json
import sqlite3
import sys

from fabric.canonical import canonical, sha256_hex, event_hash


class _Halt(Exception):
    """The checker's controlled replay halt: sequence, class, prose."""

    def __init__(self, seq, reason_class, reason):
        super().__init__(reason)
        self.seq = seq
        self.reason_class = reason_class
        self.reason = reason


# -- the fold (section 3, reconstructed independently) -------------

_RAISED_ORIGINS = {
    "semantic": ("contribution", "examination"),
    "structural": ("checker",),
}
_TRANSITIONS = {
    "semantic": {("open", "examined"), ("examined", "resolved"),
                 ("examined", "standing")},
    "structural": {("open", "resolved")},
}
_FACET_STATUSES = ("open", "unexamined", "claimed", "complete",
                   "disputed", "stood_down")
_EVIDENCE_TYPES = ("DISCOVERY", "CONTRIBUTION_REJECTED",
                   "BOUNDARY_PROBE", "IDLE", "PROBE_SESSION_OPENED",
                   "PROBE_EVIDENCE", "SEAL_ATTEMPTED")


def _empty_state():
    return {
        "regions": {},
        "dependencies": {},
        "tensions": {},
        "assessments": {},
        "completion_claims": {},
        "claims": {},
        "watches": {},
        "facet_status": {},
        "contributions": {},
        "last_seq": 0,
    }


def _apply_operations(state, contribution, payload):
    """An accepted contribution's operations, applied in order.
    A region's version advances once per accepted operation
    touching it; dependency ids assigned at commit are read from
    the event payload, so the fold is deterministic from the
    history alone. A raise_tension operation applies nothing
    here: its effect is the TENSION_RAISED event that follows."""
    regions = state["regions"]
    deps = state["dependencies"]
    for i, op in enumerate(contribution["operations"]):
        kind = op["kind"]
        if kind == "replace_content":
            region = regions[op["region_id"]]
            region["content"] = op["new_content"]
            region["version"] += 1
        elif kind == "append_content":
            region = regions[op["region_id"]]
            region["content"] = region["content"] + op["text"]
            region["version"] += 1
        elif kind == "add_dependency":
            dep_id = payload["assigned_dependency_ids"][str(i)]
            dep = {
                "dependency_id": dep_id,
                "source": op["dependency"]["source"],
                "target": op["dependency"]["target"],
                "kind": op["dependency"]["kind"],
                "status": "active",
            }
            deps[dep_id] = dep
            regions[dep["source"]]["version"] += 1
            regions[dep["target"]]["version"] += 1
        elif kind == "remove_dependency":
            dep = deps[op["dependency_id"]]
            dep["status"] = "removed"
            regions[dep["source"]]["version"] += 1
            regions[dep["target"]]["version"] += 1
        elif kind == "raise_tension":
            pass


def _apply(state, event):
    seq = event["event_seq"]
    t = event["type"]
    if t == "RUN_OPENED":
        if seq != 1:
            raise _Halt(seq, "schema_invalid",
                        "RUN_OPENED is only valid at sequence 1")
        payload = event["payload"]
        for r in payload["regions"]:
            state["regions"][r["region_id"]] = copy.deepcopy(r)
        for d in payload["dependencies"]:
            state["dependencies"][d["dependency_id"]] = \
                copy.deepcopy(d)
        state["last_seq"] = seq
        return
    if t in _EVIDENCE_TYPES:
        state["last_seq"] = seq
        return
    if t == "RUN_CLOSED":
        if "run_status" not in state:
            state["run_status"] = "closed"
        state["last_seq"] = seq
        return
    if t == "RUN_FAILED":
        p = event["payload"]
        state["run_status"] = "failed"
        state["failure"] = {"event_seq": seq,
                            "breach": p.get("breach"),
                            "summary": p.get("summary")}
        state["last_seq"] = seq
        return
    if t == "CONTRIBUTION_ACCEPTED":
        payload = event["payload"]
        _apply_operations(state, payload["contribution"], payload)
        state["contributions"][payload["contribution_id"]] = \
            copy.deepcopy(payload["contribution"])
        state["last_seq"] = seq
        return
    if t == "TENSION_RAISED":
        p = event["payload"]
        if not isinstance(p["type"], str) \
                or not isinstance(p["origin"], str) \
                or not isinstance(p["status"], str):
            raise _Halt(seq, "schema_invalid",
                        "TENSION_RAISED carries a non-string type, "
                        "origin, or status: the event fails its "
                        "schema")
        origins = _RAISED_ORIGINS.get(p["type"])
        if origins is None:
            raise _Halt(seq, "schema_invalid",
                        f"TENSION_RAISED names unknown tension "
                        f"type {p['type']!r}")
        if p["origin"] not in origins:
            raise _Halt(seq, "protocol_transition_invalid",
                        f"TENSION_RAISED for a {p['type']} tension "
                        f"names origin {p['origin']!r}; permitted "
                        f"origins are {', '.join(origins)}")
        if p["status"] != "open":
            raise _Halt(
                seq,
                "protocol_transition_invalid"
                if p["status"] in ("examined", "resolved",
                                    "standing")
                else "schema_invalid",
                f"TENSION_RAISED names initial status "
                f"{p['status']!r}; a tension is raised open")
        record = {
            "tension_id": p["tension_id"],
            "type": p["type"],
            "regions": list(p["regions"]),
            "origin": p["origin"],
            "origin_ref": p["origin_ref"],
            "description": p["description"],
            "status": p["status"],
        }
        if "check" in p:
            record["check"] = p["check"]
        if "affected" in p:
            record["affected"] = list(p["affected"])
        state["tensions"][p["tension_id"]] = record
        state["last_seq"] = seq
        return
    if t == "EXAMINATION_RECORDED":
        state["last_seq"] = seq
        return
    if t == "ASSESSMENT_RECORDED":
        p = event["payload"]
        if p.get("outcome") == "recorded":
            assessment = copy.deepcopy(p["assessment"])
            state["assessments"][assessment["assessment_id"]] = \
                assessment
        state["last_seq"] = seq
        return
    if t == "COMPLETION_CLAIMED":
        p = event["payload"]
        if p.get("outcome") == "recorded":
            record = copy.deepcopy(p["claim"])
            record["claimant"] = p["claimant"]
            state["completion_claims"][record["claim_id"]] = record
        state["last_seq"] = seq
        return
    if t == "TENSION_STATUS":
        p = event["payload"]
        if not isinstance(p["from"], str) \
                or not isinstance(p["to"], str):
            raise _Halt(seq, "schema_invalid",
                        "TENSION_STATUS carries a non-string from "
                        "or to status: the event fails its schema")
        tension = state["tensions"].get(p["tension_id"])
        if tension is None:
            raise _Halt(seq, "protocol_transition_invalid",
                        f"TENSION_STATUS names unknown tension "
                        f"{p['tension_id']}")
        if tension["status"] != p["from"]:
            raise _Halt(seq, "protocol_transition_invalid",
                        f"TENSION_STATUS for {p['tension_id']} "
                        f"claims from-status {p['from']!r} but the "
                        f"folded status is {tension['status']!r}: "
                        f"an invalid transition")
        permitted = _TRANSITIONS.get(tension["type"], set())
        if (p["from"], p["to"]) not in permitted:
            raise _Halt(seq, "protocol_transition_invalid",
                        f"TENSION_STATUS for {p['tension_id']} "
                        f"moves a {tension['type']} tension from "
                        f"{p['from']!r} to {p['to']!r}: not a "
                        f"permitted transition for its type "
                        f"(resolved and standing are terminal)")
        tension["status"] = p["to"]
        state["last_seq"] = seq
        return
    if t == "FACET_STATUS":
        p = event["payload"]
        if not isinstance(p["to"], str) \
                or p["to"] not in _FACET_STATUSES:
            raise _Halt(seq, "schema_invalid",
                        f"FACET_STATUS for {p['region_id']} names "
                        f"to-status {p['to']!r}; the permitted "
                        f"facet statuses are "
                        f"{', '.join(_FACET_STATUSES)}")
        if p["region_id"] not in state["regions"]:
            raise _Halt(seq, "protocol_transition_invalid",
                        f"FACET_STATUS names region "
                        f"{p['region_id']!r}, which is outside the "
                        f"six frozen regions")
        current = state["facet_status"].get(p["region_id"], "open")
        if current != p["from"]:
            raise _Halt(seq, "protocol_transition_invalid",
                        f"FACET_STATUS for {p['region_id']} claims "
                        f"from-status {p['from']!r} but the folded "
                        f"status is {current!r}: an invalid "
                        f"transition")
        state["facet_status"][p["region_id"]] = p["to"]
        state["last_seq"] = seq
        return
    raise _Halt(seq, "schema_invalid", f"unhandled event type {t}")


def _link_problem(events, upto, constitution_hash):
    """(reason_class, reason) for the link at position upto, or
    None. Chain integrity is checked as each event is consumed:
    gapless sequence, prev_hash against the running head, the
    event's hash recomputed over its canonical body."""
    ev = events[upto - 1]
    if ev["event_seq"] != upto:
        return "sequence_invalid", "sequence is not gapless"
    expected_prev = constitution_hash if upto == 1 \
        else events[upto - 2]["hash"]
    if ev["prev_hash"] != expected_prev:
        return ("hash_chain_invalid",
                "prev_hash does not match the running chain head")
    body = {k: ev[k] for k in
            ("event_seq", "event_id", "type", "actor", "affected",
             "payload", "prev_hash")}
    if event_hash(ev["prev_hash"], body) != ev["hash"]:
        return "hash_chain_invalid", "event hash does not recompute"
    if upto == 1 and ev["type"] != "RUN_OPENED":
        return "schema_invalid", "first event is not RUN_OPENED"
    return None


def _fold(events, constitution_hash):
    """Fold a complete event sequence with link validation. The
    authority set bound in RUN_OPENED governs: IDLE is admitted
    only when Amendment A1 is in force for the run (VP-15)."""
    if not events:
        raise _Halt(1, "schema_invalid",
                    "empty history: no genesis event")
    state = _empty_state()
    a1_in_force = True
    for i, ev in enumerate(events, start=1):
        problem = _link_problem(events, i, constitution_hash)
        if problem is not None:
            raise _Halt(i, problem[0], problem[1])
        if i == 1 and ev["type"] == "RUN_OPENED":
            payload = ev["payload"]
            auth = payload.get("authority_set") \
                if isinstance(payload, dict) else None
            if isinstance(auth, dict) \
                    and isinstance(auth.get("amendments"), list):
                a1_in_force = "A1" in auth["amendments"]
        if ev["type"] == "IDLE" and not a1_in_force:
            raise _Halt(i, "schema_invalid",
                        "IDLE is not in the event schema bound by "
                        "this run's authority set (Rev 9 without "
                        "Amendment A1)")
        try:
            _apply(state, ev)
        except _Halt:
            raise
        except (KeyError, TypeError, AttributeError) as exc:
            raise _Halt(ev.get("event_seq"), "schema_invalid",
                        f"malformed event payload: "
                        f"{type(exc).__name__}: {exc}") from exc
    return state


def _fold_staged(committed, staged, constitution_hash):
    """Fold the committed history (links fully validated), then
    apply the staged candidate batch on top. Staged events carry
    provisional sequence numbers continuing the committed head and
    claim no hashes yet: their sequence contiguity is validated
    and their payloads applied under the same legality rules, but
    chain-hash validation belongs to committed history, whose
    links are final. Returns (state_before, state_after)."""
    before = _fold(committed, constitution_hash)
    after = copy.deepcopy(before)
    a1_in_force = True
    if committed and committed[0]["type"] == "RUN_OPENED":
        payload = committed[0]["payload"]
        auth = payload.get("authority_set") \
            if isinstance(payload, dict) else None
        if isinstance(auth, dict) \
                and isinstance(auth.get("amendments"), list):
            a1_in_force = "A1" in auth["amendments"]
    head = committed[-1]["event_seq"] if committed else 0
    for j, ev in enumerate(staged, start=1):
        if ev["event_seq"] != head + j:
            raise _Halt(ev.get("event_seq"), "sequence_invalid",
                        "staged batch sequence does not continue "
                        "the committed head")
        if ev["type"] == "IDLE" and not a1_in_force:
            raise _Halt(ev["event_seq"], "schema_invalid",
                        "IDLE is not in the event schema bound by "
                        "this run's authority set (Rev 9 without "
                        "Amendment A1)")
        try:
            _apply(after, ev)
        except _Halt:
            raise
        except (KeyError, TypeError, AttributeError) as exc:
            raise _Halt(ev.get("event_seq"), "schema_invalid",
                        f"malformed event payload: "
                        f"{type(exc).__name__}: {exc}") from exc
    return before, after


# -- the structural checks (section 7) ------------------------------

_PATTERN_KINDS = ("uses", "constrains", "extends")


def _s1_findings(state):
    """S1 — dependency integrity: one finding per (active
    dependency, missing endpoint) pair; the affected set is the
    dependency record and the missing endpoint region."""
    out = []
    for dep_id in sorted(state["dependencies"]):
        dep = state["dependencies"][dep_id]
        if dep["status"] != "active":
            continue
        for endpoint in (dep["source"], dep["target"]):
            if endpoint not in state["regions"]:
                out.append({"check": "S1",
                            "affected": sorted([dep_id, endpoint])})
    return out


def _s2_findings(replay, live):
    """S2 — version monotonicity, judged on the live snapshot
    (Stage 4 correction round, C-B1: the examiner's settled S2
    ruling, superseding build-notes interpretation I-3). Replay
    of the accepted history plus the staged batch fixes each
    region's established version R_r at the seal position; the
    snapshot carries L_r. The check fails exactly when L_r < R_r
    and names that one region. It is one-sided: L_r above R_r is
    unexplained divergence (MISMATCH under the C1 precedence
    unless some check fails on L), not a monotonicity failure.
    A region replay establishes but the snapshot lacks produces
    no S2 finding here — absence is for S1 (when a dependency
    dangles on it) and for the divergence report."""
    out = []
    for rid in sorted(replay["regions"]):
        snap = live["regions"].get(rid)
        if snap is not None and snap["version"] \
                < replay["regions"][rid]["version"]:
            out.append({"check": "S2", "affected": [rid]})
    return out


def _cycle_edges(dependencies):
    """The dependency records forming the first directed cycle in
    the pattern graph, or None. Traversal is canonical — regions
    in sorted order, outgoing edges in sorted dependency order —
    so the reported cycle is deterministic (VP-20)."""
    adj = {}
    for dep_id, dep in dependencies.items():
        if dep["status"] == "active" and dep["kind"] in _PATTERN_KINDS:
            adj.setdefault(dep["source"], []).append(
                (dep_id, dep["target"]))
    for src in adj:
        adj[src].sort()
    color = {}
    stack = []

    def visit(node, via):
        color[node] = 1
        stack.append((node, via))
        for dep_id, tgt in adj.get(node, []):
            c = color.get(tgt, 0)
            if c == 1:
                nodes = [n for n, _ in stack]
                idx = nodes.index(tgt)
                return [d for _, d in stack[idx + 1:]
                        if d is not None] + [dep_id]
            if c == 0:
                found = visit(tgt, dep_id)
                if found is not None:
                    return found
        stack.pop()
        color[node] = 2
        return None

    for node in sorted(adj):
        if color.get(node, 0) == 0:
            found = visit(node, None)
            if found is not None:
                return found
    return None


def _s3_findings(state):
    """S3 — pattern acyclicity: the affected set is the dependency
    records forming the detected cycle (VP-20)."""
    cycle = _cycle_edges(state["dependencies"])
    if cycle is None:
        return []
    return [{"check": "S3", "affected": sorted(cycle)}]


def _inconsistency_absent(check, affected, live, replay=None):
    """Re-run one tension's own check against its original
    affected set (B6): True only when the particular inconsistency
    the tension represents no longer exists in the live state.
    The S2 re-run compares against the version replay establishes
    at this attempt, so the caller supplies the replay state
    (correction round, C-B1)."""
    if check == "S1":
        deps = [a for a in affected if a in live["dependencies"]]
        if not deps:
            return True  # the dependency record itself is gone
        dep = live["dependencies"][deps[0]]
        if dep["status"] != "active":
            return True
        named = [a for a in affected
                 if a != dep["dependency_id"]]
        return all(a in live["regions"] for a in named)
    if check == "S2":
        # The named regression stands unless the snapshot's
        # version for the region has caught up with the version
        # replay establishes at this attempt. A region missing
        # from the snapshot proves nothing about the regression;
        # the tension stays open.
        rid = affected[0]
        region = live["regions"].get(rid)
        if region is None:
            return False
        floor = 0
        if replay is not None:
            established = replay["regions"].get(rid)
            if established is not None:
                floor = established["version"]
        return region["version"] >= floor
    if check == "S3":
        subset = {d: live["dependencies"][d] for d in affected
                  if d in live["dependencies"]}
        return _cycle_edges(subset) is None
    return False


# -- attempt evaluation (section 7 + the C1 precedence) -------------

_CHECKS_PERFORMED = ["S1", "S2", "S3", "event_schema", "hash_chain"]


def _divergence(live, replay):
    """The record identities on which the live snapshot and the
    independently folded replay state differ (VP-26)."""
    out = []
    registries = ("regions", "dependencies", "tensions",
                  "assessments", "completion_claims", "claims",
                  "watches", "facet_status", "contributions")
    for key in registries:
        mine = live.get(key, {})
        theirs = replay.get(key, {})
        for rid in sorted(set(mine) | set(theirs)):
            if mine.get(rid) != theirs.get(rid):
                out.append({"registry": key, "id": rid})
    for key in ("run_status", "failure"):
        if live.get(key) != replay.get(key):
            out.append({"registry": key, "id": key})
    return out


def _seal_contents(events, replay):
    """The position-independent contents of a seal record: the
    contributions included since the last seal (VP-35's boundary)
    and the outstanding semantic questions, each marked
    examined-by-whom or unexamined (section 7)."""
    last_seal = 0
    for ev in events:
        if ev["type"] == "SEAL_ATTEMPTED" \
                and ev["payload"].get("outcome") == "pass":
            last_seal = ev["event_seq"]
    contributions = [
        ev["payload"]["contribution_id"] for ev in events
        if ev["type"] == "CONTRIBUTION_ACCEPTED"
        and ev["event_seq"] > last_seal]
    questions = []
    for tid in sorted(replay["tensions"]):
        tension = replay["tensions"][tid]
        if tension["type"] != "semantic" \
                or tension["status"] not in ("open", "examined"):
            continue
        examiners = sorted({
            a["author"] for a in replay["assessments"].values()
            if a.get("target_kind") == "tension"
            and a.get("target_id") == tid})
        questions.append({
            "tension_id": tid,
            "status": tension["status"],
            "examined_by": examiners if examiners else "unexamined",
        })
    return {
        "contributions_since_last_seal": contributions,
        "checks_performed": list(_CHECKS_PERFORMED),
        "outstanding_semantic_questions": questions,
        "semantic_clearance": False,
        "semantic_clearance_statement":
            "This seal certifies structure only; it grants no "
            "semantic clearance.",
    }


def evaluate(history, staged_batch, snapshot, constitution_hash,
             authenticated_actor=None):
    """Evaluate one seal attempt. Returns the verdict dict of the
    interface contract (build notes, section 2)."""
    verdict = {"outcome": None, "failed_checks": [],
               "divergence": [], "raises": [], "resolutions": [],
               "attachments": [], "seal": None}
    if staged_batch is None:
        # VP-25: without the candidate batch the attempt position
        # cannot be reconstructed; the snapshot is not authority.
        verdict["outcome"] = "refused"
        verdict["reason"] = ("staged candidate batch omitted: the "
                             "attempt position cannot be "
                             "reconstructed from the committed "
                             "history alone")
        return verdict
    if authenticated_actor is not None:
        for ev in staged_batch:
            if ev["type"] == "IDLE" \
                    and ev["actor"] != authenticated_actor:
                verdict["outcome"] = "refused"
                verdict["reason"] = (
                    "a staged IDLE event names an actor other "
                    "than the authenticated submitter; refused at "
                    "the admission boundary, no event appended")
                return verdict
    try:
        before, replay = _fold_staged(history, staged_batch,
                                      constitution_hash)
    except _Halt as halt:
        verdict["outcome"] = "halt"
        verdict["halt"] = {"seq": halt.seq,
                           "reason_class": halt.reason_class,
                           "reason": halt.reason}
        return verdict
    live = snapshot
    findings = (_s1_findings(live) + _s2_findings(replay, live)
                + _s3_findings(live))
    verdict["failed_checks"] = findings
    verdict["divergence"] = _divergence(live, replay)
    # The structural lifecycle, against the open structural
    # tensions folded from the committed history.
    open_structural = {
        tid: t for tid, t in before["tensions"].items()
        if t["type"] == "structural" and t["status"] == "open"
        and "check" in t and "affected" in t}
    by_identity = {}
    for tid, t in open_structural.items():
        by_identity[(t["check"], tuple(t["affected"]))] = tid
    attached = set()
    for finding in findings:
        identity = (finding["check"], tuple(finding["affected"]))
        tid = by_identity.get(identity)
        if tid is not None:
            verdict["attachments"].append(tid)
            attached.add(tid)
        else:
            regions = _raise_regions(finding, live)
            verdict["raises"].append({
                "check": finding["check"],
                "affected": list(finding["affected"]),
                "regions": regions})
    for tid, t in open_structural.items():
        if tid in attached:
            continue
        if _inconsistency_absent(t["check"], t["affected"], live,
                                 replay):
            verdict["resolutions"].append({
                "tension_id": tid, "check": t["check"],
                "affected": list(t["affected"])})
    if findings:
        verdict["outcome"] = "fail"
    elif verdict["divergence"]:
        verdict["outcome"] = "mismatch"
    else:
        verdict["outcome"] = "pass"
        verdict["seal"] = _seal_contents(history + staged_batch,
                                         replay)
    return verdict


def _raise_regions(finding, live):
    """The region list a raised tension records: for S1 the
    missing endpoint region; for S2 the regressed region; for S3
    the sorted endpoints of the cycle's dependency records."""
    if finding["check"] == "S1":
        return [a for a in finding["affected"]
                if a in live["regions"]
                or a not in live["dependencies"]]
    if finding["check"] == "S2":
        return list(finding["affected"])
    endpoints = set()
    for dep_id in finding["affected"]:
        dep = live["dependencies"].get(dep_id)
        if dep is not None:
            endpoints.add(dep["source"])
            endpoints.add(dep["target"])
    return sorted(endpoints)


# -- request handling -------------------------------------------------

def _read_store_history(store_path):
    """Read the event history from the store, read-only: this
    process opens the database itself (SQLite mode=ro) and never
    writes to it."""
    conn = sqlite3.connect(f"file:{store_path}?mode=ro",
                           uri=True)
    try:
        rows = conn.execute(
            "SELECT event_seq, event_id, type, actor, affected,"
            " payload, prev_hash, hash FROM events"
            " ORDER BY event_seq").fetchall()
    finally:
        conn.close()
    return [{
        "event_seq": seq, "event_id": eid, "type": typ,
        "actor": actor, "affected": json.loads(affected),
        "payload": json.loads(payload), "prev_hash": prev,
        "hash": h,
    } for seq, eid, typ, actor, affected, payload, prev, h in rows]


def handle(request):
    mode = request["mode"]
    constitution_hash = request["constitution_hash"]
    if mode == "fold":
        history = request["history"]
        try:
            state = _fold(history, constitution_hash)
        except _Halt as halt:
            return {"ok": False,
                    "halt": {"seq": halt.seq,
                             "reason_class": halt.reason_class,
                             "reason": halt.reason}}
        result = {"ok": True, "state": state,
                  "state_hash": sha256_hex(canonical(state))}
        expected = request.get("expected_pack_sha256")
        if expected is not None:
            bound = None
            if history and history[0]["type"] == "RUN_OPENED":
                pack = history[0]["payload"].get("validation_pack")
                if isinstance(pack, dict):
                    bound = pack.get("sha256")
            result["pack_binding"] = {
                "bound_sha256": bound,
                "expected_sha256": expected,
                "matches": bound == expected,
            }
        return result
    if mode == "evaluate":
        if "store_path" in request:
            history = _read_store_history(request["store_path"])
        else:
            history = request["history"]
        staged = request["staged_batch"] \
            if "staged_batch" in request else None
        return evaluate(history, staged, request["snapshot"],
                        constitution_hash,
                        request.get("authenticated_actor"))
    raise ValueError(f"unknown checker mode {mode!r}")


def main():
    request = json.loads(sys.stdin.read())
    verdict = handle(request)
    sys.stdout.write(json.dumps(verdict) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
