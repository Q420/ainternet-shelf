"""The framework observer (SPEC SHEET §3.9, R27; R33's observer
half). Built to the approved scope Rev 3
(src/PIECE6-OBSERVER-SCOPE-REV3-2026-11-22.md).

The observer accounts for the record; it does not become
another account of the underlying state. It verifies, reads,
consumes the existing derivations, and presents. It does not
manufacture state, judge evidence, expose sealed content, or
imply that a historical snapshot is live.

Discipline:

- READ-ONLY. The store is opened through a SQLite read-only
  URI. The framework's writable store class is never
  instantiated and the doorway is never imported: observing
  must not be able to change the observed, and a refusal must
  leave the filesystem untouched — no database created, no
  parent directory created.
- VERIFIED BEFORE READ. The required check set, no check
  implying another: exactly one run row; the row's run ID
  matches the requested run; every event's run ID matches it
  (verify_run_binding); the row's stored constitution hash
  equals the framework's CONSTITUTION_HASH; the event hash
  chain verifies (verify_chain). Any failure refuses, by
  name, with no output.
- ONE DERIVATION STACK. Derived matter comes from the same
  functions the doorway's state() composes — fold, then the
  gates enrichment, then the orchestrator derivations — run
  over the read events. The observer reconstructs nothing.
- SNAPSHOT-BOUNDED. Every render names the head it covers
  (sequence + hash). Statements that depend on the absence of
  a later event are qualified by that head.
- SEALED BY ALLOWLIST. An event carrying sealed material is
  represented by a fresh structure built from approved fields
  only (material reference, event position, holding seat,
  type, actor). The original payload never crosses into the
  render, so material under any other key has no path in.
"""
import json
import os
import sqlite3
import urllib.parse

from framework import gates as _gates
from framework import orchestrator as _orch
from framework.record import (CONSTITUTION_HASH, fold,
                              verify_chain, verify_run_binding)

HERE = os.path.dirname(os.path.abspath(__file__))

SEALED_EVENT_TYPES = {"MATERIAL_SEALED"}


class ObserverRefusal(Exception):
    """The observer will not render this store, and says why."""


def _read_ro(db_path):
    """Read (run_rows, events) through a read-only connection.
    A missing file or directory raises inside sqlite and is
    refused here — the read-only open creates nothing."""
    uri = "file:" + urllib.parse.quote(
        os.path.abspath(db_path)) + "?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
        try:
            run_rows = conn.execute(
                "SELECT run_id, constitution_hash FROM runs"
            ).fetchall()
            rows = conn.execute(
                "SELECT event_seq, event_id, run_id, type, actor,"
                " affected, payload, ts, prev_hash, hash"
                " FROM events ORDER BY event_seq"
            ).fetchall()
        finally:
            conn.close()
    except sqlite3.Error as exc:
        raise ObserverRefusal(
            f"cannot read a run store at {db_path} read-only "
            f"({exc}); nothing rendered")
    events = []
    for seq, eid, run_id, typ, actor, affected, payload, ts, \
            prev, h in rows:
        events.append({
            "event_seq": seq, "event_id": eid, "run_id": run_id,
            "type": typ, "actor": actor,
            "affected": json.loads(affected),
            "payload": json.loads(payload), "ts": ts,
            "prev_hash": prev, "hash": h,
        })
    return run_rows, events


def _verify(db_path, run_id):
    """The required check set (scope O1). Returns the verified
    events, or raises ObserverRefusal naming the failed check."""
    run_rows, events = _read_ro(db_path)
    if not run_rows:
        raise ObserverRefusal(
            "binding refused: the store holds no run row; "
            "nothing rendered")
    if len(run_rows) > 1:
        raise ObserverRefusal(
            "binding refused: the store holds duplicate run "
            f"rows ({len(run_rows)}); nothing rendered")
    row_run_id, row_constitution = run_rows[0]
    if row_run_id != run_id:
        raise ObserverRefusal(
            f"binding refused: the run row names {row_run_id}, "
            f"not the requested run {run_id}; nothing rendered")
    if not events:
        raise ObserverRefusal(
            "the store holds no events; the observer renders "
            "history, it does not create it; nothing rendered")
    if not verify_run_binding(events, run_id):
        raise ObserverRefusal(
            "binding refused: an event's run_id does not match "
            f"the requested run {run_id}; nothing rendered")
    if row_constitution != CONSTITUTION_HASH:
        raise ObserverRefusal(
            "binding refused: the run's stored constitution "
            "hash does not match the framework's "
            "CONSTITUTION_HASH; nothing rendered")
    if not verify_chain(events):
        raise ObserverRefusal(
            "verification refused: the event hash chain does "
            "not verify; nothing rendered")
    return events


def _sealed_representation(ev):
    """The allowlist representation of a sealed event (scope
    O5): a fresh structure carrying only approved existence
    metadata. The original payload is never copied across."""
    p = ev["payload"]
    return {
        "event_seq": ev["event_seq"],
        "type": ev["type"],
        "actor": ev["actor"],
        "ts": ev["ts"],
        "sealed": {
            "material_id": p.get("material_id"),
            "boundary": list(p.get("boundary", [])),
            "held_by": ev["actor"],
            "event_seq": ev["event_seq"],
        },
    }


def _detail(events):
    """The full-detail tier: every event, in record order,
    with attribution and types intact — sealed events by
    their allowlist representation only."""
    out = []
    for ev in events:
        if ev["type"] in SEALED_EVENT_TYPES:
            out.append(_sealed_representation(ev))
        else:
            out.append({
                "event_seq": ev["event_seq"],
                "type": ev["type"],
                "actor": ev["actor"],
                "ts": ev["ts"],
                "affected": ev["affected"],
                "payload": ev["payload"],
            })
    return out


def _summary(events, state):
    """The plain-words tier. Every statement carries the event
    positions it rests on and its kind: recorded (read from
    events) or derived (from the one derivation stack, and
    qualified by the snapshot head where it rests on the
    absence of a later event)."""
    head = state["head_seq"]
    stmts = []

    def rec(text, seqs):
        stmts.append({"kind": "recorded", "text": text,
                      "events": list(seqs)})

    def der(text, seqs):
        stmts.append({"kind": "derived", "text": text,
                      "events": list(seqs), "as_of_head": head})

    commission = next(
        (e for e in events if e["type"] == "RUN_COMMISSIONED"),
        None)
    if commission is not None:
        p = commission["payload"]
        parts = ", ".join((p.get("tree") or {}).keys())
        rec(f"Run commissioned by {commission['actor']}: "
            f"tree parts {parts}.",
            [commission["event_seq"]])

    by_part = {}
    for e in events:
        if e["type"] == "CONTRIBUTION":
            part = e["payload"].get("tree_part") or "(job)"
            by_part.setdefault(part, []).append(e)
    for part in sorted(by_part):
        evs = by_part[part]
        rec(f"{len(evs)} contribution(s) on part {part}, by "
            + ", ".join(sorted({e['actor'] for e in evs})) + ".",
            [e["event_seq"] for e in evs])

    for e in events:
        if e["type"] == "GATE_OUTCOME":
            rec(f"Gate {e['payload'].get('joint')}: outcome "
                f"{e['payload'].get('outcome')}, recorded by "
                f"{e['actor']}.", [e["event_seq"]])
        elif e["type"] == "DISAGREEMENT":
            rec(f"Disagreement "
                f"{e['payload'].get('disagreement_id')} raised "
                f"by {e['actor']} over claim "
                f"{e['payload'].get('claim_id')}.",
                [e["event_seq"]])
        elif e["type"] == "DISAGREEMENT_SETTLED":
            rec(f"Disagreement "
                f"{e['payload'].get('disagreement_id')} "
                f"settled.", [e["event_seq"]])
        elif e["type"] == "CERTIFICATION":
            p = e["payload"]
            covers = p.get("covers_parts")
            scope_txt = ("the whole run" if covers is None
                         else "parts " + ", ".join(covers))
            statuses = p.get("identity_status") or {}
            status_txt = "; ".join(
                f"{s} {statuses[s]}" for s in sorted(statuses))
            rec(f"Certification recorded by {e['actor']} "
                f"covering {scope_txt}"
                + (f" — identity as declared: {status_txt}."
                   if status_txt else "."),
                [e["event_seq"]])
        elif e["type"] == "MATERIAL_SEALED":
            p = e["payload"]
            rec(f"Sealed material {p.get('material_id')} "
                f"exists, sealed by {e['actor']} for boundary "
                f"seats {', '.join(p.get('boundary', []))} — "
                f"its content is not shown.",
                [e["event_seq"]])

    if state.get("rejections"):
        rec(f"{len(state['rejections'])} act(s) were refused "
            f"and recorded as rejections.",
            [r["event_seq"] for r in state["rejections"]])

    # ---- derived tier (the one stack, labelled, head-bound)
    gate_set = state.get("gate_set") or {}
    if gate_set.get("declared"):
        support = []
        if commission is not None:
            support.append(commission["event_seq"])
        records = state.get("assembly_records") or []
        if records:
            support.append(
                max(r["event_seq"] for r in records))
        der(f"The operative gate set is "
            f"{gate_set.get('operative')} (valid: "
            f"{gate_set.get('valid')}).", support)
    waiting = state.get("waiting") or {}
    commission_seq = (commission["event_seq"]
                      if commission is not None else None)

    def last_outcome_seq(joint):
        seqs = [e["event_seq"] for e in events
                if e["type"] == "GATE_OUTCOME"
                and e["payload"].get("joint") == joint]
        return seqs[-1] if seqs else commission_seq

    for name in ("awaiting_gate", "awaiting_ruling",
                 "holder_unavailable", "paused_by_gate"):
        for joint in waiting.get(name) or []:
            if name == "holder_unavailable":
                support = [d["event_seq"]
                           for d in
                           state.get("holder_unavailable", [])
                           if d.get("joint") == joint]
            elif name == "paused_by_gate":
                entry = (state.get("paused") or {}).get(joint) \
                    or {}
                support = [entry["source_seq"]] \
                    if entry.get("source_seq") else []
            else:
                seq = last_outcome_seq(joint)
                support = [seq] if seq else []
            der(f"As of event {head}, {joint} stands "
                f"{name.replace('_', ' ')}.", support)
    for seat, stall in sorted(
            (state.get("stalled") or {}).items()):
        der(f"Seat {seat} is stalled ({stall.get('kind')}) "
            f"on part {stall.get('part')}.",
            [stall.get("event_seq")])
    for cert in state.get("certifications") or []:
        ev = next(e for e in events
                  if e["event_seq"] == cert["event_seq"])
        derived = _orch.certification_coverage(
            state, ev["payload"].get("covers_parts"))
        if derived is not None:
            status_txt = "; ".join(
                f"{s} {derived[s]}" for s in sorted(derived))
            der(f"Derived coverage of the certification at "
                f"event {cert['event_seq']}: "
                f"{status_txt or 'no contributors'}. "
                f"(Derived — the certification as declared "
                f"stands above, as recorded.)",
                [cert["event_seq"]])
    return stmts


def render(events, state, run_id):
    head_ev = events[-1]
    return {
        "run_id": run_id,
        "snapshot": {"head_seq": head_ev["event_seq"],
                     "head_hash": head_ev["hash"]},
        "summary": _summary(events, state),
        "waiting": state.get("waiting") or {},
        "stalled": state.get("stalled") or {},
        "detail": _detail(events),
    }


def observe(db_path, run_id):
    """Verify the store, read it, derive through the one
    stack, and return the observer's account of the run."""
    events = _verify(db_path, run_id)
    state = _orch.derive(_gates.enrich(fold(events, run_id)))
    return render(events, state, run_id)


def script_safe_json(obj) -> str:
    """Serialize for embedding inside an HTML <script>
    element: the HTML-significant characters are
    unicode-escaped, so a stored value containing '</script>'
    stays inert data (the carried observer's discipline)."""
    return (json.dumps(obj)
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026"))


def export_html(db_path, run_id, out_path, template_path=None):
    """Render the run to a single self-contained page
    (scope O6): a static snapshot that names its head and
    never presents itself as the run's current state."""
    account = observe(db_path, run_id)
    template_path = template_path or os.path.join(
        HERE, "observer-template.html")
    with open(template_path, encoding="utf-8") as f:
        template = f.read()
    page = template.replace(
        "__OBSERVER_DATA__", script_safe_json(account))
    page = page.replace("__RUN_ID__", account["run_id"])
    page = page.replace(
        "__HEAD_SEQ__", str(account["snapshot"]["head_seq"]))
    page = page.replace(
        "__HEAD_HASH__", account["snapshot"]["head_hash"])
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    return account
