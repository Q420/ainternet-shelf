"""Piece 6, part 4 (SPEC SHEET §3.9: R27 + R33's observer
half) — the framework observer. Tests the ten acceptance
criteria of the approved scope Rev 3
(src/PIECE6-OBSERVER-SCOPE-REV3-2026-11-22.md):

  1  the binding check set refuses, each check by name
  2  read-only: bytes unchanged, no doorway import, a
     refusal leaves the filesystem untouched
  3  the snapshot boundary (head named; later appends do
     not move an earlier account)
  4  provenance and kinds on every summary statement;
     certification coverage's two meanings kept separate
  5  all five waiting states, each with its clearing
     transition (a stall's transition is INTO the state —
     the fold defines no event that clears one)
  6  full-detail fidelity
  7  sealed material by allowlist: three secrets, three
     hiding places, none crossing
  8  script safety across the whole export
  9  the §3.8-shaped end-to-end run renders truly
  10 boundaries (regression suites + substrate identity,
     run outside this file)

Run:  PYTHONPATH=src python3 tests/unit/test_piece6_observer.py
"""
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile

from framework.doorway import Doorway
from framework.observer import (ObserverRefusal, export_html,
                                observe)
from framework.record import (CONSTITUTION_HASH, FrameworkStore,
                              verify_chain)

PASS = []
FAIL = []


def check(name, cond, extra=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS " if cond else "FAIL ") + name +
          ((" -- " + str(extra)) if (extra and not cond) else ""))


def refuses(fn):
    try:
        fn()
    except ObserverRefusal as exc:
        return str(exc)
    return None


TMP = tempfile.mkdtemp(prefix="observer-tests-")
SEQ = [0]


def fresh_store():
    SEQ[0] += 1
    path = os.path.join(TMP, f"obs{SEQ[0]}.db")
    return FrameworkStore(path), path


def commission(store, gates=None):
    payload = {
        "constitution_hash": CONSTITUTION_HASH,
        "seats": {"orch-1": {"role": "orchestrator"},
                  "exam-1": {"role": "examiner"},
                  "crew-1": {"role": "crew"},
                  "dir-1": {"role": "director"}},
        "tree": {"A": ["B", "C"], "B": ["D"], "C": [], "D": []},
        "director": "dir-1",
    }
    if gates is not None:
        payload["gates"] = gates
    return store.append("RUN_COMMISSIONED", "dir-1", [], payload)


def doorway_for(store):
    d = Doorway(store)
    return d, {s: d.issue_token(s) for s in
               ("orch-1", "exam-1", "crew-1", "dir-1")}


def A(d, store, token, type_, payload):
    before = store.head_seq()
    ev = d.act(token, type_, payload, store.head_seq())
    assert ev is not None and store.head_seq() > before, \
        f"{type_} did not record"
    return ev


DECLARED = {"assembly": "assembly", "B": "judgement",
            "C": "judgement", "D": "judgement",
            "completion": "completion"}


def open_run(store, d, tok):
    prop = A(d, store, tok["orch-1"], "ASSEMBLY_PROPOSED",
             {"commission_seq": 1, "tree_ref": 1, "gates_ref": 1,
              "crew": [{"seat": "crew-1", "role": "crew"}]})
    A(d, store, tok["exam-1"], "ASSEMBLY_RECORD",
      {"proposal_seq": prop["event_seq"],
       "criteria_mapping": {p: f"criterion-{p}"
                            for p in ("A", "B", "C", "D")},
       "gate_set": dict(DECLARED),
       "identity_weighed": {"crew-1": "unverified"}})
    A(d, store, tok["exam-1"], "GATE_OUTCOME",
      {"joint": "assembly", "outcome": "allow"})


def certify_run(store, d, tok):
    open_run(store, d, tok)
    A(d, store, tok["exam-1"], "GATE_OUTCOME",
      {"joint": "B", "outcome": "allow"})
    A(d, store, tok["crew-1"], "CONTRIBUTION",
      {"tree_part": "B", "text": "work on B"})
    A(d, store, tok["crew-1"], "COMPLETION_CLAIMED",
      {"parts": ["B"]})
    A(d, store, tok["orch-1"], "RUN_READY_FOR_COMPLETION", {})
    A(d, store, tok["exam-1"], "GATE_OUTCOME",
      {"joint": "completion", "outcome": "allow"})
    A(d, store, tok["exam-1"], "CERTIFICATION",
      {"identity_status": {"crew-1": "unverified"}})


# ------------------------------------------------- criterion 1
def raw_db(path, run_rows, event_rows):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE runs (run_id TEXT PRIMARY KEY,"
                 " constitution_hash TEXT NOT NULL,"
                 " status TEXT NOT NULL DEFAULT 'open')")
    conn.execute(
        "CREATE TABLE events (event_seq INTEGER PRIMARY KEY,"
        " event_id TEXT, run_id TEXT, type TEXT, actor TEXT,"
        " affected TEXT, payload TEXT, ts TEXT, prev_hash TEXT,"
        " hash TEXT)")
    for r in run_rows:
        conn.execute("INSERT INTO runs VALUES (?, ?, 'open')", r)
    for e in event_rows:
        conn.execute(
            "INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?,?)", e)
    conn.commit()
    conn.close()


def t_binding_refusals():
    p = os.path.join(TMP, "raw-norow.db")
    raw_db(p, [], [])
    msg = refuses(lambda: observe(p, "run-1"))
    check("C1 no run row refuses by name",
          msg is not None and "no run row" in msg, msg)
    p = os.path.join(TMP, "raw-dupe.db")
    raw_db(p, [("run-1", CONSTITUTION_HASH),
               ("run-2", CONSTITUTION_HASH)], [])
    msg = refuses(lambda: observe(p, "run-1"))
    check("C1 duplicate run rows refuse by name",
          msg is not None and "duplicate" in msg, msg)
    p = os.path.join(TMP, "raw-rowid.db")
    raw_db(p, [("run-2", CONSTITUTION_HASH)], [])
    msg = refuses(lambda: observe(p, "run-1"))
    check("C1 run-row ID mismatch refuses by name",
          msg is not None and "run row names run-2" in msg, msg)
    p = os.path.join(TMP, "raw-evbind.db")
    raw_db(p, [("run-1", CONSTITUTION_HASH)],
           [(1, "e1", "run-9", "RUN_COMMISSIONED", "dir-1",
             "[]", "{}", "t", "", "h")])
    msg = refuses(lambda: observe(p, "run-1"))
    check("C1 event run-ID mismatch refuses separately",
          msg is not None and "an event's run_id" in msg, msg)
    store, p = fresh_store()
    store.insert_run("run-1", "bogus-hash")
    commission(store)
    store._conn.commit()
    check("C1 constitution fixture's chain itself verifies",
          verify_chain(store.all_events()))
    msg = refuses(lambda: observe(p, "run-1"))
    check("C1 constitution mismatch refuses by name",
          msg is not None and "constitution" in msg, msg)
    store, p = fresh_store()
    store.insert_run("run-1", CONSTITUTION_HASH)
    commission(store)
    store._conn.commit()
    store._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    store._conn.close()
    copy = p + ".copy"
    shutil.copyfile(p, copy)
    conn = sqlite3.connect(copy)
    conn.execute("DROP TRIGGER IF EXISTS events_no_update")
    conn.execute("UPDATE events SET payload = ? WHERE"
                 " event_seq = 1",
                 (json.dumps({"tampered": True}),))
    conn.commit()
    conn.close()
    msg = refuses(lambda: observe(copy, "run-1"))
    check("C1 broken chain refuses by name",
          msg is not None and "hash chain" in msg, msg)


# ------------------------------------------------- criterion 2
def t_read_only():
    store, p = fresh_store()
    store.insert_run("run-1", CONSTITUTION_HASH)
    commission(store)
    d, tok = doorway_for(store)
    store._conn.commit()
    with open(p, "rb") as f:
        before = f.read()
    observe(p, "run-1")
    observe(p, "run-1")
    with open(p, "rb") as f:
        after = f.read()
    check("C2 store bytes identical after two observations",
          before == after)
    missing = os.path.join(TMP, "never-existed.db")
    msg = refuses(lambda: observe(missing, "run-1"))
    check("C2 missing store refuses and is not created",
          msg is not None and not os.path.exists(missing))
    orphan = os.path.join(TMP, "no-such-dir", "x.db")
    msg = refuses(lambda: observe(orphan, "run-1"))
    check("C2 missing parent refuses and is not created",
          msg is not None
          and not os.path.exists(os.path.dirname(orphan)))
    env = dict(os.environ, PYTHONPATH="src")
    proc = subprocess.run(
        [sys.executable, "-c",
         "import framework.observer, sys; "
         "assert 'framework.doorway' not in sys.modules, "
         "'doorway imported'"],
        capture_output=True, text=True, env=env,
        cwd=os.path.join(os.path.dirname(__file__), "..", ".."))
    check("C2 importing the observer never imports the doorway",
          proc.returncode == 0, proc.stderr.strip()[-200:])


# ------------------------------------------- criteria 3, 4, 6
def t_snapshot_provenance_detail():
    store, p = fresh_store()
    store.insert_run("run-1", CONSTITUTION_HASH)
    commission(store, gates=DECLARED)
    d, tok = doorway_for(store)
    certify_run(store, d, tok)
    store._conn.commit()
    events = store.all_events()
    acct = observe(p, "run-1")
    check("C3 snapshot names the store's true head",
          acct["snapshot"] == {"head_seq": events[-1]["event_seq"],
                               "head_hash": events[-1]["hash"]})
    A(d, store, tok["crew-1"], "COMMENT",
      {"on_job": True, "text": "later"})
    store._conn.commit()
    acct2 = observe(p, "run-1")
    check("C3 a later append moves only the later snapshot",
          acct2["snapshot"]["head_seq"] > acct["snapshot"]["head_seq"]
          and acct["snapshot"]["head_seq"] == events[-1]["event_seq"])
    check("C4 every summary statement is kinded and positioned",
          all(s["kind"] in ("recorded", "derived")
              and (s["events"] or "as_of_head" in s)
              for s in acct["summary"]))
    check("C4 every derived statement is head-qualified",
          all(s.get("as_of_head") == acct["snapshot"]["head_seq"]
              for s in acct["summary"] if s["kind"] == "derived"))
    declared = [s for s in acct["summary"]
                if s["kind"] == "recorded"
                and "identity as declared" in s["text"]]
    derived = [s for s in acct["summary"]
               if s["kind"] == "derived"
               and "Derived coverage" in s["text"]]
    check("C4 certification coverage appears in both meanings,"
          " separately labelled",
          len(declared) == 1 and len(derived) == 1
          and "crew-1 unverified" in declared[0]["text"]
          and "crew-1 unverified" in derived[0]["text"],
          [s["text"] for s in acct["summary"]])
    check("C6 detail tier is the record, in order, attributed",
          [e["event_seq"] for e in acct["detail"]]
          == [e["event_seq"] for e in events]
          and all(a["type"] == b["type"]
                  and a["actor"] == b["actor"]
                  for a, b in zip(acct["detail"], events)))


# ------------------------------------------------- criterion 5
def t_waiting_states():
    store, p = fresh_store()
    store.insert_run("run-1", CONSTITUTION_HASH)
    commission(store, gates=DECLARED)
    d, tok = doorway_for(store)
    store._conn.commit()
    acct = observe(p, "run-1")
    check("C5 awaiting_gate stands before the assembly gate",
          "assembly" in acct["waiting"]["awaiting_gate"])
    open_run(store, d, tok)
    store._conn.commit()
    acct = observe(p, "run-1")
    check("C5 awaiting_gate clears at the assembly allow;"
          " B still awaits its own gate",
          "assembly" not in acct["waiting"]["awaiting_gate"]
          and "B" in acct["waiting"]["awaiting_gate"])
    A(d, store, tok["exam-1"], "GATE_OUTCOME",
      {"joint": "B", "outcome": "allow"})
    A(d, store, tok["exam-1"], "GATE_OUTCOME",
      {"joint": "C", "outcome": "escalate", "tree_part": "C"})
    store._conn.commit()
    acct = observe(p, "run-1")
    check("C5 allow clears B; escalation puts C in"
          " awaiting_ruling and paused_by_gate",
          "B" not in acct["waiting"]["awaiting_gate"]
          and "C" in acct["waiting"]["awaiting_ruling"]
          and acct["waiting"]["paused_by_gate"] == ["C"],
          acct["waiting"])
    A(d, store, tok["dir-1"], "RULING",
      {"joint": "C", "action": "proceed"})
    store._conn.commit()
    acct = observe(p, "run-1")
    check("C5 the ruling clears awaiting_ruling (the pause"
          " stands until the allow it permits)",
          "C" not in acct["waiting"]["awaiting_ruling"]
          and acct["waiting"]["paused_by_gate"] == ["C"])
    A(d, store, tok["exam-1"], "GATE_OUTCOME",
      {"joint": "C", "outcome": "allow", "released_set": ["C"]})
    A(d, store, tok["orch-1"], "HOLDER_UNAVAILABLE",
      {"joint": "B"})
    store._conn.commit()
    acct = observe(p, "run-1")
    check("C5 the post-ruling allow clears the pause",
          acct["waiting"]["paused_by_gate"] == [])
    check("C5 holder_unavailable stands on its declaration",
          acct["waiting"]["holder_unavailable"] == ["B"])
    A(d, store, tok["exam-1"], "GATE_OUTCOME",
      {"joint": "B", "outcome": "allow"})
    store._conn.commit()
    acct = observe(p, "run-1")
    check("C5 a later outcome clears holder_unavailable",
          acct["waiting"]["holder_unavailable"] == [])
    before = observe(p, "run-1")
    store.append("DRIVER_FAILURE", "doorway", [],
                 {"seat": "crew-1", "kind": "provider_error",
                  "part": "B"})
    store._conn.commit()
    acct = observe(p, "run-1")
    check("C5 seat_stalled appears on the failure event",
          "crew-1" not in before["stalled"]
          and acct["stalled"].get("crew-1", {}).get("kind")
          == "provider_error"
          and any("stalled" in s["text"]
                  and s["kind"] == "derived"
                  for s in acct["summary"]))


# ------------------------------------------- criteria 7 and 8
def t_sealed_and_script_safety():
    store, p = fresh_store()
    store.insert_run("run-1", CONSTITUTION_HASH)
    commission(store, gates=DECLARED)
    d, tok = doorway_for(store)
    open_run(store, d, tok)
    A(d, store, tok["exam-1"], "GATE_OUTCOME",
      {"joint": "B", "outcome": "allow"})
    store.append("MATERIAL_SEALED", "orch-1", [], {
        "material_id": "mat-1", "boundary": ["crew-1"],
        "content": "SECRET-EXPECTED-123",
        "notes": "SECRET-UNEXPECTED-456",
        "nested": {"deep": "SECRET-NESTED-789"}})
    A(d, store, tok["crew-1"], "CONTRIBUTION",
      {"tree_part": "B",
       "text": "</script><script>alert(1)</script>"})
    store._conn.commit()
    acct = observe(p, "run-1")
    blob = json.dumps(acct)
    check("C7 no secret crosses into the render, from any"
          " hiding place",
          all(s not in blob for s in
              ("SECRET-EXPECTED-123", "SECRET-UNEXPECTED-456",
               "SECRET-NESTED-789")))
    sealed_entries = [e for e in acct["detail"]
                      if e["type"] == "MATERIAL_SEALED"]
    check("C7 the sealed representation is exactly the"
          " approved allowlist — no ts, no boundary, nothing"
          " beyond it",
          len(sealed_entries) == 1
          and set(sealed_entries[0]) == {"event_seq", "type",
                                         "actor", "sealed"}
          and sealed_entries[0]["sealed"] == {
              "material_id": "mat-1",
              "held_by": "orch-1",
              "event_seq": sealed_entries[0]["event_seq"]},
          sealed_entries)
    check("C7 the summary states existence, never content",
          any("Sealed material mat-1 exists" in s["text"]
              for s in acct["summary"]))
    out = os.path.join(TMP, "export.html")
    export_html(p, "run-1", out)
    with open(out, encoding="utf-8") as f:
        page = f.read()
    check("C7/C8 the export carries no secret and no live"
          " payload script tag",
          all(s not in page for s in
              ("SECRET-EXPECTED-123", "SECRET-UNEXPECTED-456",
               "SECRET-NESTED-789"))
          and "</script><script>" not in page
          and "\\u003c/script\\u003e" in page)
    check("C8 the export names its snapshot head",
          f"event <strong>{acct['snapshot']['head_seq']}</strong>"
          in page and acct["snapshot"]["head_hash"] in page)


# ------------------------------ correction round 1 (Vane)
def t_correction_round_1():
    store, p = fresh_store()
    store.insert_run("run-1", CONSTITUTION_HASH)
    commission(store)
    store._conn.commit()
    with open(p, "rb") as f:
        before = f.read()
    msg = refuses(lambda: export_html(p, "run-1", p))
    alias = os.path.join(os.path.dirname(p), ".",
                         os.path.basename(p))
    msg2 = refuses(lambda: export_html(p, "run-1", alias))
    with open(p, "rb") as f:
        after = f.read()
    check("R1 an output path identifying the source store is"
          " refused — directly and by equivalent path — and"
          " the store stays byte-identical",
          msg is not None and msg2 is not None
          and before == after, (msg, msg2))
    hostile = "</title><script>alert(1)</script>"
    store2, p2 = fresh_store()
    store2.insert_run(hostile, CONSTITUTION_HASH)
    commission(store2)
    store2._conn.commit()
    out = os.path.join(TMP, "hostile.html")
    export_html(p2, hostile, out)
    with open(out, encoding="utf-8") as f:
        page = f.read()
    check("R1 a hostile run ID is HTML-escaped in the title"
          " and heading substitutions",
          hostile not in page
          and "&lt;/title&gt;" in page, page[:300])


# ------------------------------------------------- criterion 9
def t_end_to_end():
    store, p = fresh_store()
    store.insert_run("run-1", CONSTITUTION_HASH)
    commission(store, gates=DECLARED)
    d, tok = doorway_for(store)
    certify_run(store, d, tok)
    store._conn.commit()
    acct = observe(p, "run-1")
    texts = [s["text"] for s in acct["summary"]]
    check("C9 the certified run renders: commission, work,"
          " operative set, certification",
          any(t.startswith("Run commissioned") for t in texts)
          and any("contribution(s) on part B" in t for t in texts)
          and any("operative gate set" in t
                  and s["kind"] == "derived"
                  for s, t in zip(acct["summary"], texts))
          and any("Certification recorded" in t for t in texts),
          texts)


def main():
    t_binding_refusals()
    t_read_only()
    t_snapshot_provenance_detail()
    t_waiting_states()
    t_sealed_and_script_safety()
    t_correction_round_1()
    t_end_to_end()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("FAILED:", *FAIL, sep="\n  ")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
