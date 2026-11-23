"""Piece 7 tests — the independent checker (SPEC SHEET §3.10:
R4, R28), per the accepted scope Rev 4
(src/PIECE7-CHECKER-SCOPE-REV4-2026-11-22.md) and its nine
acceptance criteria.

Run: PYTHONPATH=src python3 tests/unit/test_piece7_checker.py
Exits 0 when every check passes.
"""
import copy
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from fabric.canonical import canonical, event_hash  # noqa: E402

from framework import onboarding as ob  # noqa: E402
from framework import projection  # noqa: E402
from framework.doorway import Doorway, DoorwayRefusal  # noqa: E402
from framework.record import (FrameworkStore, CONSTITUTION_HASH,  # noqa: E402
                              replay)

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name +
          (("  " + detail) if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


def try_act(d, token, type_, payload):
    """An act that may be refused: a refusal appends a REJECTION
    event, which is itself fold breadth both replays share."""
    try:
        return d.act(token, type_, payload,
                     view_seq=d.store.head_seq())
    except DoorwayRefusal:
        return None


TREE = {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}
FULL_GATES = {"assembly": "assembly", "completion": "completion",
              "B": "judgement", "C": "judgement", "D": "judgement"}
SEATS = {
    "crew-1": {"role": "crew", "identity_status": "unverified"},
    "crew-2": {"role": "crew", "identity_status": "unverified"},
    "orch-1": {"role": "orchestrator",
               "identity_status": "unverified"},
    "exam-1": {"role": "examiner", "identity_status": "unverified"},
    "dir-1": {"role": "director", "identity_status": "unverified"},
}
CREW = [{"seat": s, "role": b["role"]} for s, b in SEATS.items()]


def fresh(gates=None, tree=None, run_id="run-1"):
    path = os.path.join(tempfile.mkdtemp(), "run.db")
    store = FrameworkStore(path)
    store.insert_run(run_id, CONSTITUTION_HASH)
    payload = {"run_id": run_id, "tree": tree or TREE,
               "seats": SEATS}
    if gates is not None:
        payload["gates"] = gates
    store.append("RUN_COMMISSIONED", "dir-1", [], payload)
    store.commit()
    d = Doorway(store)
    tok = {s: d.issue_token(s) for s in SEATS}
    return store, d, tok


def run_checker(store_path, run_id, snapshot):
    req = {"store_path": store_path, "run_id": run_id,
           "snapshot": snapshot}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=SRC)
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "checker"],
        input=json.dumps(req), capture_output=True, text=True,
        env=env, cwd=ROOT)
    return proc, json.loads(proc.stdout)


def quiesce(store):
    """Checkpoint the store's WAL so the checker reads a
    quiescent record (its immutable read refuses uncheckpointed
    WAL data by name)."""
    store._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")


def expect_all_ok(name, store, run_id="run-1"):
    quiesce(store)
    snap = projection.snapshot(store)
    proc, verdict = run_checker(store.path, run_id, snap)
    c = verdict["checks"]
    ok = proc.returncode == 0 and all(
        c[k]["result"] == "ok" for k in (
            "run_binding", "chain_hash", "chain_sequence", "replay",
            "projection_schema", "snapshot_schema",
            "replay_equality", "seal_correspondence"))
    check(name, ok, json.dumps(c))
    return verdict


# ============================================================ fixtures

# -- Fixture A: a §3.8-shaped certified run (assembly, judgement
# gates, onboarding, contributions with a claim, a disagreement
# with a routing note, completion, certification, close).
storeA, dA, tokA = fresh(gates=FULL_GATES)
prop = try_act(dA, tokA["orch-1"], "ASSEMBLY_PROPOSED", {
    "commission_seq": 1, "tree_ref": 1, "gates_ref": 1,
    "crew": CREW})
try_act(dA, tokA["exam-1"], "ASSEMBLY_RECORD", {
    "proposal_seq": prop["event_seq"],
    "criteria_mapping": {p: f"criterion-{p}" for p in TREE},
    "gate_set": dict(FULL_GATES),
    "identity_weighed": {s: "unverified" for s in SEATS}})
try_act(dA, tokA["exam-1"], "GATE_OUTCOME",
        {"joint": "assembly", "outcome": "allow"})
ob.onboard(dA, tokA["orch-1"], "crew-1", "I am a test model.",
           identity_status="declared")
tokA["crew-1"] = dA.issue_token("crew-1")
for joint in ("B", "C", "D"):
    try_act(dA, tokA["exam-1"], "GATE_OUTCOME",
            {"joint": joint, "outcome": "allow"})
try_act(dA, tokA["crew-1"], "CONTRIBUTION", {
    "contribution_id": "c-a1", "tree_part": "B", "text": "work",
    "claim_id": "cl-1"})
try_act(dA, tokA["crew-2"], "CONTRIBUTION", {
    "contribution_id": "c-a2", "tree_part": "C", "text": "work"})
try_act(dA, tokA["exam-1"], "DISAGREEMENT", {
    "disagreement_id": "dis-1", "claim_id": "cl-1",
    "text": "the claim overstates the work"})
try_act(dA, tokA["orch-1"], "COMMENT", {
    "text": "route to completion", "routes_disagreement": "dis-1",
    "to_gate": "completion"})
try_act(dA, tokA["orch-1"], "DISAGREEMENT_SETTLED", {
    "disagreement_id": "dis-1"})
try_act(dA, tokA["crew-1"], "COMPLETION_CLAIMED", {"text": "done"})
try_act(dA, tokA["orch-1"], "RUN_READY_FOR_COMPLETION", {})
try_act(dA, tokA["exam-1"], "GATE_OUTCOME",
        {"joint": "completion", "outcome": "allow"})
try_act(dA, tokA["exam-1"], "CERTIFICATION", {
    "identity_status": {"crew-1": "declared",
                        "crew-2": "unverified"}})
try_act(dA, tokA["dir-1"], "RUN_CLOSED", {})

# -- Fixture B: a case-lifecycle run (record-level case history:
# issuance route, acknowledgement, a correction to version 2 with
# its own route, contributions cased then pre-ack then cased, a
# sealed material, examiner acts). Case events are appended at
# the record layer: the checker examines records, and the case
# route's doorway enforcement is Piece 5's tested surface.
storeB, dB, tokB = fresh(gates=None, run_id="run-1")
CASE_CONTENT = {
    "case_id": "case-crew-1", "version": 1, "seat": "crew-1",
    "assignment": "write part B", "tree": TREE, "part": "B",
    "evidence_boundary": ["record"], "verification_list": ["v1"],
    "account": "acct", "authority": ["CONTRIBUTION"],
}
storeB.append("CASE_VERIFIED", "orch-1", [], dict(CASE_CONTENT))
storeB.append("CASE_JUDGED", "exam-1", [],
              {"case_id": "case-crew-1", "version": 1})
storeB.append("CASE_ISSUED", "orch-1", [],
              {"case_id": "case-crew-1", "version": 1})
storeB.append("CASE_ACKNOWLEDGED", "crew-1", [],
              {"case_id": "case-crew-1", "version": 1})
storeB.append("CONTRIBUTION", "crew-1", [], {
    "contribution_id": "c-b1", "tree_part": "B", "text": "work"})
v2 = dict(CASE_CONTENT, version=2, assignment="write part B, "
          "revised", representational=False)
storeB.append("CASE_CORRECTED", "orch-1", [], v2)
storeB.append("CASE_VERIFIED", "orch-1", [],
              {"case_id": "case-crew-1", "version": 2})
storeB.append("CASE_JUDGED", "exam-1", [],
              {"case_id": "case-crew-1", "version": 2})
storeB.append("CASE_ISSUED", "orch-1", [],
              {"case_id": "case-crew-1", "version": 2})
storeB.append("CONTRIBUTION", "crew-1", [], {
    "contribution_id": "c-b2", "tree_part": "B", "text": "more"})
storeB.append("CASE_ACKNOWLEDGED", "crew-1", [],
              {"case_id": "case-crew-1", "version": 2})
storeB.append("MATERIAL_SEALED", "exam-1", [], {
    "material_id": "mat-1", "boundary": ["exam-1"]})
storeB.append("FINDING", "exam-1", [], {"text": "a finding"})
storeB.append("RULING", "dir-1", [],
              {"joint": "B", "action": "proceed"})
storeB.append("DISPOSITION", "exam-1", [], {"text": "noted"})
storeB.commit()

# -- Fixture C: onboarding with an attested upgrade, an uncased
# contribution, an escalation with pauses, a holder-unavailable
# declaration, a stall, and a recorded refusal.
storeC, dC, tokC = fresh(gates=FULL_GATES)
try_act(dC, tokC["crew-1"], "CONTRIBUTION", {
    "contribution_id": "c-c1", "tree_part": "B", "text": "early"})
ob.onboard(dC, tokC["orch-1"], "crew-1", "I am a test model.",
           identity_status="declared")
ob.attest(dC, tokC["orch-1"], "crew-1", "provider-confirmed",
          attestation_ref="att/42")
try_act(dC, tokC["exam-1"], "GATE_OUTCOME",
        {"joint": "B", "outcome": "escalate"})
storeC.append("ESCALATION", "dir-1", [], {
    "joint": "B", "paused_set": ["B"],
    "downstream": {"B": ["D"]}})
storeC.append("HOLDER_UNAVAILABLE", "orch-1", [], {"joint": "D"})
storeC.commit()
dC.record_driver_failure("crew-2", "no_response", "C")
try_act(dC, tokC["crew-1"], "CLAIM_STATUS",
        {"claim_id": "nope", "to": "verified"})


# ============================================================ crit. 3
expect_all_ok("C3 replay equality: §3.8-shaped certified run",
              storeA)
expect_all_ok("C3 replay equality: case-lifecycle run", storeB)
expect_all_ok("C3 replay equality: onboarding/escalation/stall "
              "run", storeC)

# ============================================================ crit. 1
proc = subprocess.run(
    [sys.executable, "-B", "-c",
     "import sys; sys.path.insert(0, %r); "
     "import checker.checker, checker.replay, checker.schema; "
     "print(sorted(m for m in sys.modules "
     "if m.startswith('framework')))" % SRC],
    capture_output=True, text=True, env=dict(
        os.environ, PYTHONDONTWRITEBYTECODE="1"))
check("C1 import audit: importing the checker loads no "
      "framework.* module", proc.stdout.strip() == "[]",
      proc.stdout + proc.stderr)
import re  # noqa: E402

allowed = {"fabric.canonical", "checker.replay", "checker.schema"}
stdlib = set(sys.stdlib_module_names)
imports_ok = True
for fname in ("checker.py", "replay.py", "schema.py", "__main__.py",
              "__init__.py"):
    text = open(os.path.join(SRC, "checker", fname)).read()
    for mod in re.findall(r"^(?:from|import)\s+([\w.]+)", text, re.M):
        top = mod.split(".")[0]
        if mod not in allowed and top not in stdlib and \
                top != "checker":
            imports_ok = False
check("C1 source audit: checker imports only fabric.canonical, "
      "itself, and stdlib", imports_ok)

# ============================================================ crit. 2
def tampered_copy(store, mutate):
    """Copy a store (via SQLite's backup API, so the copy holds
    the full logical database) and mutate its events table
    directly, dropping the append-only triggers in the copy —
    the tamper the chain checks exist to catch."""
    dst = os.path.join(tempfile.mkdtemp(), "tampered.db")
    conn = sqlite3.connect(dst)
    store._conn.backup(conn)
    for trig in ("events_no_update", "events_no_delete",
                 "events_no_replace"):
        conn.execute(f"DROP TRIGGER IF EXISTS {trig}")
    mutate(conn)
    conn.commit()
    conn.close()
    return dst


quiesce(storeA)
snapA = projection.snapshot(storeA)
eventsA = storeA.all_events()
third = eventsA[2]


def mut_hash(conn):
    row = conn.execute("SELECT payload FROM events WHERE "
                       "event_seq = ?", (third["event_seq"],)
                       ).fetchone()
    p = json.loads(row[0])
    p["text"] = "tampered"
    conn.execute("UPDATE events SET payload = ? WHERE "
                 "event_seq = ?", (json.dumps(p),
                                   third["event_seq"]))


_, v = run_checker(tampered_copy(storeA, mut_hash), "run-1", snapA)
check("C2 payload tamper: hash_chain_invalid at the position, "
      "sequence still ok",
      v["checks"]["chain_hash"]["result"] == "hash_chain_invalid"
      and v["checks"]["chain_hash"]["at_seq"] == third["event_seq"]
      and v["checks"]["chain_sequence"]["result"] == "ok",
      json.dumps(v["checks"]))


def mut_seq_only(conn):
    ev = dict(third)
    ev["prev_hash"] = "deadbeef"
    body = {k: ev[k] for k in ev if k != "hash"}
    ev["hash"] = event_hash(ev["prev_hash"], body)
    conn.execute("UPDATE events SET prev_hash = ?, hash = ? "
                 "WHERE event_seq = ?",
                 (ev["prev_hash"], ev["hash"], third["event_seq"]))


_, v = run_checker(tampered_copy(storeA, mut_seq_only), "run-1",
                   snapA)
check("C2 linkage defect, hash recomputed: sequence_invalid "
      "only",
      v["checks"]["chain_sequence"]["result"] == "sequence_invalid"
      and v["checks"]["chain_sequence"]["at_seq"]
      == third["event_seq"]
      and v["checks"]["chain_hash"]["result"] == "ok",
      json.dumps(v["checks"]))


def mut_both(conn):
    conn.execute("UPDATE events SET prev_hash = 'deadbeef' WHERE "
                 "event_seq = ?", (third["event_seq"],))


_, v = run_checker(tampered_copy(storeA, mut_both), "run-1", snapA)
check("C2 both defects: reported independently, both named",
      v["checks"]["chain_hash"]["result"] == "hash_chain_invalid"
      and v["checks"]["chain_sequence"]["result"]
      == "sequence_invalid",
      json.dumps(v["checks"]))

# ============================================================ crit. 4
import checker.schema as checker_schema  # noqa: E402

check("C4 the two schema copies are canonically identical",
      canonical(projection.SCHEMA) == canonical(
          checker_schema.SCHEMA))
stateA = replay(storeA)
check("C4 the live fold state conforms recursively",
      projection.conforms(stateA) == [],
      str(projection.conforms(stateA)))
check("C4 the exported projection conforms recursively",
      projection.conforms(snapA) == [])
planted = copy.deepcopy(snapA)
planted["seats"]["crew-1"]["planted_field"] = True
bad = projection.conforms(planted)
check("C4 a planted extra nested field fails the witness, "
      "named by path", bad == ["seats.crew-1.planted_field"],
      str(bad))
plantedB = copy.deepcopy(projection.snapshot(storeB))
plantedB["cases"]["case-crew-1"]["versions"]["1"]["planted"] = 1
badB = projection.conforms(plantedB)
check("C4 a planted field inside a case version fails, named",
      badB == ["cases.case-crew-1.versions.1.planted"], str(badB))
_, v = run_checker(storeA.path, "run-1", planted)
check("C4 the checker reports the planted snapshot as "
      "nonconforming at the same path",
      v["checks"]["snapshot_schema"]["result"] == "nonconforming"
      and v["checks"]["snapshot_schema"]["paths"]
      == ["seats.crew-1.planted_field"],
      json.dumps(v["checks"].get("snapshot_schema")))

# Round 1 (Vane's examination): the planted-field witness must
# also run against the LIVE FOLD STATE itself, and against the
# checker's RECONSTRUCTION — not only against exported snapshots.
liveC = replay(storeC)
liveC["seats"]["crew-1"]["planted_field"] = True
check("C4 a planted field in the live fold state fails the "
      "witness, named by path",
      projection.conforms(liveC) == ["seats.crew-1.planted_field"],
      str(projection.conforms(liveC)))
liveB = replay(storeB)
liveB["cases"]["case-crew-1"]["versions"]["1"]["planted"] = 1
check("C4 a planted field inside a live case version fails, "
      "named by path",
      projection.conforms(liveB)
      == ["cases.case-crew-1.versions.1.planted"],
      str(projection.conforms(liveB)))


def rewritten_copy(store, new_tree):
    """A copy of the store whose commission carries a planted
    nested structure inside its tree, with the whole hash chain
    recomputed — a rewritten history, internally consistent, so
    only the schema witness can catch the shape."""
    dst = os.path.join(tempfile.mkdtemp(), "rewritten.db")
    conn = sqlite3.connect(dst)
    store._conn.backup(conn)
    for trig in ("events_no_update", "events_no_delete",
                 "events_no_replace"):
        conn.execute(f"DROP TRIGGER IF EXISTS {trig}")
    rows = conn.execute(
        "SELECT event_seq, event_id, run_id, type, actor, affected,"
        " payload, ts FROM events ORDER BY event_seq").fetchall()
    prev = ""
    for seq, eid, run_id, typ, actor, affected, payload, ts in rows:
        p = json.loads(payload)
        if typ == "RUN_COMMISSIONED":
            p["tree"] = new_tree
        ev = {"event_seq": seq, "event_id": eid, "run_id": run_id,
              "type": typ, "actor": actor,
              "affected": json.loads(affected), "payload": p,
              "ts": ts, "prev_hash": prev}
        h = event_hash(prev, ev)
        conn.execute("UPDATE events SET payload = ?, prev_hash = ?,"
                     " hash = ? WHERE event_seq = ?",
                     (json.dumps(p), prev, h, seq))
        prev = h
    conn.commit()
    conn.close()
    return dst


_, v = run_checker(rewritten_copy(storeA, {"A": [{"planted": 1}]}),
                   "run-1", snapA)
check("C4 a planted structure inside the reconstruction's tree "
      "fails closed: the chain verifies, the replay halts "
      "schema_invalid on the wrongly typed tree value",
      v["checks"]["chain_hash"]["result"] == "ok"
      and v["checks"]["replay"]["result"] == "schema_invalid"
      and v["checks"]["replay"]["at_seq"] == 1,
      json.dumps(v["checks"]))

# And the projection-schema walk itself, over the checker's own
# reconstruction, names a planted field by path (the layer that
# witnesses whatever reaches the state past the event guard).
import checker.checker as checker_mod  # noqa: E402
import checker.replay as checker_replay  # noqa: E402

recon, halt = checker_replay.replay_events(storeB.all_events(),
                                           "run-1")
check("C4 the checker's reconstruction of the case-lifecycle "
      "run conforms before planting", halt is None
      and checker_mod._conforms(
          json.loads(canonical(recon)), checker_schema.SCHEMA)
      == [])
recon["cases"]["case-crew-1"]["versions"]["1"]["planted"] = 1
bad_recon = checker_mod._conforms(
    json.loads(canonical(recon)), checker_schema.SCHEMA)
check("C4 a planted field inside the checker's reconstruction "
      "fails its schema witness, named by path",
      bad_recon == ["cases.case-crew-1.versions.1.planted"],
      str(bad_recon))

# Round 2: case content's key set is closed — an unknown key
# inside content fails the witness at every surface.
liveB2 = replay(storeB)
liveB2["cases"]["case-crew-1"]["versions"]["1"]["content"][
    "brand_new"] = 1
check("C4 an unknown key inside live case content fails, named",
      projection.conforms(liveB2)
      == ["cases.case-crew-1.versions.1.content.brand_new"],
      str(projection.conforms(liveB2)))
planted_content = copy.deepcopy(projection.snapshot(storeB))
planted_content["cases"]["case-crew-1"]["versions"]["1"][
    "content"]["brand_new"] = {"nested": True}
_, v = run_checker(storeB.path, "run-1", planted_content)
check("C4 the checker names an unknown key inside case content "
      "in a supplied snapshot",
      v["checks"]["snapshot_schema"]["result"] == "nonconforming"
      and v["checks"]["snapshot_schema"]["paths"]
      == ["cases.case-crew-1.versions.1.content.brand_new"],
      json.dumps(v["checks"].get("snapshot_schema")))
recon2, halt2 = checker_replay.replay_events(storeB.all_events(),
                                             "run-1")
recon2["cases"]["case-crew-1"]["versions"]["1"]["content"][
    "brand_new"] = 1
check("C4 an unknown key inside the reconstruction's case "
      "content fails its schema witness, named by path",
      checker_mod._conforms(json.loads(canonical(recon2)),
                            checker_schema.SCHEMA)
      == ["cases.case-crew-1.versions.1.content.brand_new"])

# ============================================================ crit. 5
false_snap = copy.deepcopy(snapA)
false_snap["lifecycle"] = "bogus"
_, v = run_checker(storeA.path, "run-1", false_snap)
check("C5 one planted false value is reported by that key only",
      v["checks"]["replay_equality"]["result"] == "divergent"
      and v["checks"]["replay_equality"]["divergences"]
      == ["lifecycle"],
      json.dumps(v["checks"].get("replay_equality")))

# ============================================================ crit. 6
storeD, dD, tokD = fresh(gates=None)
storeD.append("MATERIAL_SEALED", "exam-1", [], {
    "material_id": "mat-1", "boundary": ["exam-1"]})
storeD.append("MATERIAL_SEALED", "exam-1", [], {
    "material_id": "mat-1", "boundary": ["exam-1", "dir-1"]})
storeD.append("COMMENT", "crew-1", [], {
    "material_id": "mat-9", "text": "a stray reference"})
storeD.commit()
quiesce(storeD)
_, v = run_checker(storeD.path, "run-1", projection.snapshot(storeD))
probs = v["checks"]["seal_correspondence"].get("problems", [])
kinds = sorted(p["kind"] for p in probs)
check("C6 duplicate sealing and a stray material reference are "
      "reported by material",
      v["checks"]["seal_correspondence"]["result"] == "divergent"
      and kinds == ["duplicate_sealing_events",
                    "material_reference_on_other_type"]
      and all("material_id" in p for p in probs),
      json.dumps(probs))

# ============================================================ crit. 7
def tree_witness(root):
    out = {}
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(dirs)
        for f in sorted(files):
            p = os.path.join(base, f)
            out[os.path.relpath(p, root)] = hashlib.sha256(
                open(p, "rb").read()).hexdigest()
    return out


wstore, wd, wtok = fresh(gates=FULL_GATES)
try_act(wd, wtok["crew-1"], "CONTRIBUTION", {
    "contribution_id": "c-w1", "tree_part": "B", "text": "work"})
wsnap = projection.snapshot(wstore)
wstore._conn.close()
store_dir = os.path.dirname(wstore.path)
before = {"store": tree_witness(store_dir),
          "src": tree_witness(SRC)}
proc, v = run_checker(wstore.path, "run-1", wsnap)
after = {"store": tree_witness(store_dir),
         "src": tree_witness(SRC)}
check("C7 filesystem witness: store directory and source tree "
      "identical before and after",
      before == after and v["checks"]["replay"]["result"] == "ok",
      json.dumps({k: (before[k] == after[k]) for k in before}))
missing = os.path.join(tempfile.mkdtemp(), "nope.db")
_, v = run_checker(missing, "run-1", None)
check("C7 a missing store is refused and not created",
      v["checks"]["store"]["result"] == "store_missing"
      and not os.path.exists(missing), json.dumps(v["checks"]))

# ============================================================ crit. 8
storeE, dE, tokE = fresh(gates=None)
storeE.append("CASE_ISSUED", "orch-1", [], {
    "case_id": "case-x", "version": "one", "seat": "crew-1"})
storeE.commit()
quiesce(storeE)
# No framework snapshot is supplied here: the framework's own
# fold has no schema guard and cannot fold this event — which
# is precisely the gap the checker exists to cover.
proc, v = run_checker(storeE.path, "run-1", None)
check("C8 a hash-valid, wrongly typed event produces a classed "
      "schema_invalid halt, no traceback",
      proc.returncode == 0
      and v["checks"]["replay"]["result"] == "schema_invalid"
      and v["checks"]["chain_hash"]["result"] == "ok"
      and "Traceback" not in proc.stdout + proc.stderr,
      json.dumps(v["checks"]) + proc.stderr)

# Round 1: the classification contract — a wrongly typed defined
# field halts the replay; it does not fold into a nonconforming
# state. Her concrete case first, then an equivalent.
storeF, dF, tokF = fresh(gates=None)
storeF._conn.close()
pathF = os.path.join(tempfile.mkdtemp(), "run.db")
storeF = FrameworkStore(pathF)
storeF.insert_run("run-1", CONSTITUTION_HASH)
storeF.append("RUN_COMMISSIONED", "dir-1", [], {
    "run_id": "run-1", "tree": TREE,
    "seats": {"crew-1": {"role": "crew", "identity_status": 7}}})
storeF.commit()
quiesce(storeF)
proc, v = run_checker(storeF.path, "run-1", None)
check("C8 a commission binding with an integer identity_status "
      "halts schema_invalid at the commission",
      proc.returncode == 0
      and v["checks"]["replay"]["result"] == "schema_invalid"
      and v["checks"]["replay"]["at_seq"] == 1
      and v["checks"]["chain_hash"]["result"] == "ok",
      json.dumps(v["checks"]))
storeG, dG, tokG = fresh(gates=None)
storeG.append("CONTRIBUTION", "crew-1", [], {
    "contribution_id": "c-g1", "tree_part": 5, "text": "work"})
storeG.commit()
quiesce(storeG)
proc, v = run_checker(storeG.path, "run-1", None)
check("C8 a contribution with an integer tree_part halts "
      "schema_invalid at its position",
      proc.returncode == 0
      and v["checks"]["replay"]["result"] == "schema_invalid"
      and v["checks"]["replay"]["at_seq"] == 2
      and v["checks"]["chain_hash"]["result"] == "ok",
      json.dumps(v["checks"]))

# Round 2: the envelope's defined fields are guarded too —
# C6 is not limited to fields the fold happens to read.
storeH, dH, tokH = fresh(gates=None)
storeH.append("COMMENT", "crew-1", [7], {"text": "note"})
storeH.commit()
quiesce(storeH)
proc, v = run_checker(storeH.path, "run-1", None)
check("C8 an event whose affected list holds a non-string "
      "halts schema_invalid at its position",
      proc.returncode == 0
      and v["checks"]["replay"]["result"] == "schema_invalid"
      and v["checks"]["replay"]["at_seq"] == 2
      and v["checks"]["chain_hash"]["result"] == "ok",
      json.dumps(v["checks"]))


def ts_tampered_copy(store):
    """A copy whose LAST event carries an integer ts, its hash
    recomputed — hash-valid, in sequence, wrongly typed. The
    store's own DDL declares ts TEXT, whose affinity would
    coerce an integer to text on storage, so the copy's events
    table is rebuilt with an untyped ts column — a store
    written by another hand, which is exactly what the checker
    exists to read."""
    dst = os.path.join(tempfile.mkdtemp(), "ts.db")
    conn = sqlite3.connect(dst)
    store._conn.backup(conn)
    conn.execute(
        "CREATE TABLE events2 (event_seq INTEGER PRIMARY KEY,"
        " event_id TEXT UNIQUE NOT NULL, run_id TEXT NOT NULL,"
        " type TEXT NOT NULL, actor TEXT NOT NULL,"
        " affected TEXT NOT NULL, payload TEXT NOT NULL,"
        " ts, prev_hash TEXT NOT NULL, hash TEXT NOT NULL)")
    conn.execute("INSERT INTO events2 SELECT * FROM events")
    conn.execute("DROP TABLE events")
    conn.execute("ALTER TABLE events2 RENAME TO events")
    row = conn.execute(
        "SELECT event_seq, event_id, run_id, type, actor, affected,"
        " payload, prev_hash FROM events ORDER BY event_seq DESC"
        " LIMIT 1").fetchone()
    seq, eid, run_id, typ, actor, affected, payload, prev = row
    ev = {"event_seq": seq, "event_id": eid, "run_id": run_id,
          "type": typ, "actor": actor,
          "affected": json.loads(affected),
          "payload": json.loads(payload), "ts": 999,
          "prev_hash": prev}
    conn.execute("UPDATE events SET ts = 999, hash = ?"
                 " WHERE event_seq = ?",
                 (event_hash(prev, ev), seq))
    conn.commit()
    conn.close()
    return dst, seq


ts_path, ts_seq = ts_tampered_copy(storeB)
proc, v = run_checker(ts_path, "run-1", None)
check("C8 a hash-valid event with an integer ts halts "
      "schema_invalid at its own position",
      proc.returncode == 0
      and v["checks"]["chain_hash"]["result"] == "ok"
      and v["checks"]["chain_sequence"]["result"] == "ok"
      and v["checks"]["replay"]["result"] == "schema_invalid"
      and v["checks"]["replay"]["at_seq"] == ts_seq,
      json.dumps(v["checks"]))

# Round 3: schema_invalid is reserved for a hash-valid,
# in-sequence event (C6's preconditions). A wrongly typed event
# failing either precondition is NOT classified schema_invalid;
# the chain results carry the defect independently.
storeI, dI, tokI = fresh(gates=None)
storeI.append("CASE_ISSUED", "orch-1", [], {
    "case_id": "case-crew-1", "version": "one", "seat": "crew-1"})
storeI.commit()
quiesce(storeI)


def hash_broken_copy(store):
    dst = os.path.join(tempfile.mkdtemp(), "hashbroken.db")
    conn = sqlite3.connect(dst)
    store._conn.backup(conn)
    for trig in ("events_no_update", "events_no_delete",
                 "events_no_replace"):
        conn.execute(f"DROP TRIGGER IF EXISTS {trig}")
    conn.execute("UPDATE events SET hash = 'deadbeef'"
                 " WHERE event_seq = 2")
    conn.commit()
    conn.close()
    return dst


proc, v = run_checker(hash_broken_copy(storeI), "run-1", None)
check("C6 a wrongly typed event with an invalid stored hash "
      "is not classified schema_invalid",
      proc.returncode == 0
      and v["checks"]["chain_hash"]["result"]
      == "hash_chain_invalid"
      and v["checks"]["chain_hash"]["at_seq"] == 2
      and v["checks"]["chain_sequence"]["result"] == "ok"
      and v["checks"]["replay"]["result"] == "not_classified"
      and v["checks"]["replay"]["at_seq"] == 2,
      json.dumps(v["checks"]))


def linkage_broken_copy(store):
    dst = os.path.join(tempfile.mkdtemp(), "linkbroken.db")
    conn = sqlite3.connect(dst)
    store._conn.backup(conn)
    for trig in ("events_no_update", "events_no_delete",
                 "events_no_replace"):
        conn.execute(f"DROP TRIGGER IF EXISTS {trig}")
    row = conn.execute(
        "SELECT event_id, type, actor, affected, payload, ts"
        " FROM events WHERE event_seq = 2").fetchone()
    ev = {"event_seq": 2, "event_id": row[0], "run_id": "run-1",
          "type": row[1], "actor": row[2],
          "affected": json.loads(row[3]),
          "payload": json.loads(row[4]), "ts": row[5],
          "prev_hash": "bogus"}
    conn.execute("UPDATE events SET prev_hash = 'bogus',"
                 " hash = ? WHERE event_seq = 2",
                 (event_hash("bogus", ev),))
    conn.commit()
    conn.close()
    return dst


proc, v = run_checker(linkage_broken_copy(storeI), "run-1", None)
check("C6 a wrongly typed event with a recomputed hash but "
      "broken linkage is not classified schema_invalid",
      proc.returncode == 0
      and v["checks"]["chain_hash"]["result"] == "ok"
      and v["checks"]["chain_sequence"]["result"]
      == "sequence_invalid"
      and v["checks"]["chain_sequence"]["at_seq"] == 2
      and v["checks"]["replay"]["result"] == "not_classified"
      and v["checks"]["replay"]["at_seq"] == 2,
      json.dumps(v["checks"]))

# Round 4: standing is keyed by PHYSICAL position, not by the
# claimed event_seq. A later duplicate event_seq must not
# overwrite the standing of the event that legitimately stands
# at that sequence. (The fixture store's events table is
# rebuilt without the primary key — this store's DDL makes a
# duplicate event_seq uninsertable, which is the framework's
# own protection, not the checker's assumption.)
def duplicate_seq_copy(store):
    dst = os.path.join(tempfile.mkdtemp(), "dup.db")
    conn = sqlite3.connect(dst)
    store._conn.backup(conn)
    conn.execute(
        "CREATE TABLE events2 (event_seq INTEGER, event_id TEXT,"
        " run_id TEXT, type TEXT, actor TEXT, affected TEXT,"
        " payload TEXT, ts TEXT, prev_hash TEXT, hash TEXT)")
    conn.execute("INSERT INTO events2 SELECT * FROM events")
    conn.execute("DROP TABLE events")
    conn.execute("ALTER TABLE events2 RENAME TO events")
    prev = conn.execute(
        "SELECT hash FROM events ORDER BY rowid DESC LIMIT 1"
    ).fetchone()[0]
    ev = {"event_seq": 2, "event_id": "evt-dup", "run_id": "run-1",
          "type": "COMMENT", "actor": "crew-1", "affected": [],
          "payload": {"text": "dup"}, "ts": "2026-01-01T00:00:00Z",
          "prev_hash": prev}
    conn.execute(
        "INSERT INTO events VALUES (2, 'evt-dup', 'run-1',"
        " 'COMMENT', 'crew-1', '[]', ?, '2026-01-01T00:00:00Z',"
        " ?, ?)",
        (json.dumps({"text": "dup"}), prev, event_hash(prev, ev)))
    conn.commit()
    conn.close()
    return dst


proc, v = run_checker(duplicate_seq_copy(storeI), "run-1", None)
check("C6 a duplicate event_seq does not steal the standing of "
      "the event at that position: the malformed event keeps "
      "its schema_invalid classification, the duplicate is the "
      "sequence defect at its physical position",
      proc.returncode == 0
      and v["checks"]["chain_hash"]["result"] == "ok"
      and v["checks"]["chain_sequence"]["result"]
      == "sequence_invalid"
      and v["checks"]["chain_sequence"]["at_position"] == 3
      and v["checks"]["replay"]["result"] == "schema_invalid"
      and v["checks"]["replay"]["at_seq"] == 2
      and v["checks"]["replay"]["at_position"] == 2,
      json.dumps(v["checks"]))

# ============================================================ crit. 9
proto = os.path.expanduser("~/workspace/loom-prototype")
mismatch = []
for sub in ("fabric", "observer"):
    for base, dirs, files in os.walk(os.path.join(SRC, sub)):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith(".pyc"):
                continue
            mine = os.path.join(base, f)
            rel = os.path.relpath(mine, SRC)
            other = os.path.join(proto, rel)
            if os.path.exists(other):
                if open(mine, "rb").read() != open(other,
                                                   "rb").read():
                    mismatch.append(rel)
check("C9 substrate carried files remain byte-identical to the "
      "pin", mismatch == [], str(mismatch))

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES: {FAILURES}")
    sys.exit(1)
print("ALL CHECKS PASSED")
