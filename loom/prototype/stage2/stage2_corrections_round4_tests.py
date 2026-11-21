"""Stage 2 corrections ROUND 4 tests: the two findings in Vane's
examination of corrections round 3 (at shelf commit e4e35db6,
preserved as the examined artifact). B2.1 was CLOSED in that
examination and is not retested here beyond the regression suites.

B1.1 residual — the rig/store run binding is unconditional: when
the store already holds a run, the rig identity must carry a
run_id that is a non-empty string equal to it. Missing, null,
malformed, or mismatched refuses startup, in the enforced posture
too (the binding is posture-independent). The runtime factory
builds experimental runtimes only; the twin designation has
exactly one sanctioned route (build_twin_runtime), and misuse of
build_runtime raises.

B1.2 — the attestation is bound to evidence of the ACTUAL probe
execution, held in the twin's own records. Vane's attack verbatim:
a genuine probe_twin runtime, its run opened, the probe NEVER
executed, its real identity/metadata/hashes harvested, fabricated
all-passing outcomes — refused, with no BOUNDARY_PROBE recorded.
Altered outcomes against a genuine twin — refused. The genuine
session-based flow attests end to end.

Run: python3 stage2_corrections_round4_tests.py
Every agent operation is performed by a real loomagent process;
every service runs as loomfab.
"""
import copy
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fabric.fixture import COMPONENTS, REGIONS
from fabric.probe2 import PROBE_AGENT_ID, attest_probe, run_twin_probe
from fabric.runtime_setup import (RUNTIME_BASE, admin_request,
                                  agent_call, build_runtime,
                                  build_twin_runtime,
                                  code_copy_hashes, runtime_paths,
                                  start_service, stat_record,
                                  stop_service)
from fabric.store import EventStore

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        failures.append(name)


GENESIS_CONTENT = {r["region_id"]: r["content"] for r in REGIONS}
A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"

BASE = RUNTIME_BASE
os.makedirs(BASE, exist_ok=True)


def start_refused(p, posture=None):
    """Attempt to start a service; return the RuntimeError text if
    startup was refused (the service exited early), else None."""
    try:
        proc = start_service(p, posture=posture)
    except RuntimeError as exc:
        return str(exc)
    stop_service(proc, p)
    return None


def read_rig(p):
    with open(p["rig_path"], encoding="utf-8") as fh:
        return json.load(fh)


def write_rig(p, record):
    with open(p["rig_path"], "w", encoding="utf-8") as fh:
        json.dump(record, fh)


def history_types(p):
    hist = admin_request(p, {"op": "history"})["result"]["events"]
    return [e["type"] for e in hist]


# =====================================================================
# Phase A — B1.1: unconditional rig/run binding; factory discipline
# =====================================================================
bind = build_runtime(BASE, "round4bind")
proc = start_service(bind)
try:
    admin_request(bind, {"op": "open_run", "run_id": "round4-bind"})
finally:
    stop_service(proc, bind)
good_rig = read_rig(bind)
check("B1.1 setup: opening the run recorded its id in the rig "
      "identity", good_rig.get("run_id") == "round4-bind")


def rig_case(label, mutate):
    rig = copy.deepcopy(good_rig)
    mutate(rig)
    write_rig(bind, rig)
    err = start_refused(bind)  # enforced posture: the binding is
    # posture-independent (round 3 checked it only under
    # probe_target, and only when both ids were non-null)
    check(f"B1.1: a rig run_id that is {label} refuses startup "
          "when the store holds a run", err is not None)
    write_rig(bind, good_rig)


rig_case("missing", lambda r: r.pop("run_id", None))
rig_case("null", lambda r: r.update(run_id=None))
rig_case("malformed (a number)", lambda r: r.update(run_id=42))
rig_case("mismatched", lambda r: r.update(run_id="round4-other"))

os.remove(bind["rig_path"])
err = start_refused(bind)
check("B1.1: no rig identity at all refuses startup when the "
      "store holds a run", err is not None)
write_rig(bind, good_rig)
os.chown(bind["rig_path"], 1000, 1000)
os.chmod(bind["rig_path"], 0o600)

proc = start_service(bind)
try:
    status = admin_request(bind, {"op": "status"})["result"]
    check("B1.1: a rig naming the store's actual run starts and "
          "serves", status["run_id"] == "round4-bind")
finally:
    stop_service(proc, bind)

try:
    build_runtime(BASE, "round4misuse", rig="probe_twin")
    misuse_raised = False
except ValueError:
    misuse_raised = True
check("B1.1: build_runtime refuses the probe_twin designation "
      "(the twin has one sanctioned build route)", misuse_raised)
twinbuilt = build_twin_runtime(BASE, "round4twinbuilt")
with open(twinbuilt["rig_path"], encoding="utf-8") as fh:
    check("B1.1: build_twin_runtime builds the probe-twin rig",
          json.load(fh)["rig"] == "probe_twin")

# =====================================================================
# Phase B — B1.2: Vane's attack, verbatim
# =====================================================================
# A genuine probe_twin runtime, its run opened, the probe NEVER
# executed. Harvest its real identity, metadata and build hashes,
# and fabricate all-passing outcomes around them.
atk = build_twin_runtime(BASE, "round4attack")
proc = start_service(atk, posture="probe_target")
try:
    admin_request(atk, {"op": "open_run", "run_id": "round4-attack"})
finally:
    stop_service(proc, atk)

PASSING = {
    "direct_read_store": "denied",
    "direct_read_ground_truth": "denied",
    "alternate_path_symlink": "denied",
    "alternate_path_traversal": "denied",
    "forged_token_open": "refused",
    "issuance_attempt_on_data_socket": "refused",
    "legitimate_pattern_view": "ok",
    "legitimate_region_open": "ok",
}
fabricated_attempts = []
for name, outcome in PASSING.items():
    detail = {"errno": 13, "error": "PermissionError: Permission "
                                    "denied"} \
        if outcome == "denied" else {"fabricated": True}
    if name == "direct_read_store":
        detail["path"] = atk["store_path"]
    elif name == "direct_read_ground_truth":
        detail["path"] = atk["ground_truth_path"]
    elif name == "alternate_path_symlink":
        detail["path"] = atk["symlink_path"]
    elif name == "alternate_path_traversal":
        detail["path"] = atk["traversal_path"]
    fabricated_attempts.append({"attempt": name, "outcome": outcome,
                                "detail": detail})
fabricated = {
    "twin_name": "round4attack",
    "twin_root": atk["root"],
    "twin_config": stat_record(atk),
    "service_posture": "probe_target",
    "service_code_hashes": code_copy_hashes(atk),
    "attempts": fabricated_attempts,
    "all_reads_denied": True,
    "socket_attacks_refused": True,
    "legitimate_access_ok": True,
    "probe_agent": PROBE_AGENT_ID,
    "summary": "Fabricated around a genuine twin that was never "
               "probed (Vane's round-3 attack).",
}

exp = build_runtime(BASE, "round4exp")
proc = start_service(exp)
try:
    admin_request(exp, {"op": "open_run", "run_id": "round4-exp"})

    r = attest_probe(exp, fabricated)
    check("B1.2 attack: fabricated outcomes against a genuine, "
          "never-probed twin are refused",
          r.get("ok") is False)
    check("B1.2 attack: no BOUNDARY_PROBE stands in the "
          "experimental history",
          history_types(exp) == ["RUN_OPENED"])

    invented = copy.deepcopy(fabricated)
    invented["execution_evidence"] = {
        "twin_root": atk["root"],
        "session_id": str(uuid.uuid4()),
        "event_seq": 2,
        "event_hash": "ab" * 32,
    }
    r = attest_probe(exp, invented)
    check("B1.2 attack: an invented execution-evidence pointer "
          "against the same twin is refused",
          r.get("ok") is False
          and "execution evidence" in (r.get("error") or ""))
    check("B1.2 attack: the history is still exactly RUN_OPENED",
          history_types(exp) == ["RUN_OPENED"])
    r = admin_request(exp, {"op": "issue_token", "agent_id": A})
    check("B1.2 attack: the gate stays closed (no token issued)",
          r.get("ok") is False and r.get("kind") == "refusal")

    # =================================================================
    # Phase C — a genuine probe: the evidence record; altered outcomes
    # =================================================================
    result = run_twin_probe(BASE, "twin")
    twinP = runtime_paths(BASE, "twin")
    twin_store = EventStore(twinP["store_path"])
    try:
        twin_events = twin_store.all_events()
    finally:
        twin_store._conn.close()
    twin_types = [e["type"] for e in twin_events]
    check("B1.2: the twin's own history records the probe session "
          "and its execution evidence",
          "PROBE_SESSION_OPENED" in twin_types
          and "PROBE_EVIDENCE" in twin_types)
    evidence_ev = [e for e in twin_events
                   if e["type"] == "PROBE_EVIDENCE"][-1]
    session_ev = [e for e in twin_events
                  if e["type"] == "PROBE_SESSION_OPENED"][-1]
    ptr = result["execution_evidence"]
    check("B1.2: the result's pointer names the twin's evidence "
          "event (seq + hash)",
          ptr["event_seq"] == evidence_ev["event_seq"]
          and ptr["event_hash"] == evidence_ev["hash"]
          and ptr["session_id"]
          == evidence_ev["payload"]["session_id"])
    outcomes = evidence_ev["payload"]["outcomes"]
    check("B1.2: the socket outcomes stand in the twin's record "
          "as OBSERVED by the service",
          all(outcomes[n]["basis"] == "observed"
              and outcomes[n]["outcome"] == PASSING[n]
              for n in ("forged_token_open",
                        "issuance_attempt_on_data_socket",
                        "legitimate_pattern_view",
                        "legitimate_region_open")))
    check("B1.2: the filesystem outcomes stand in the twin's "
          "record as agent-reported with entailment verified",
          all(outcomes[n]["basis"]
              == "agent_reported_entailment_verified"
              and outcomes[n]["outcome"] == "denied"
              for n in ("direct_read_store",
                        "direct_read_ground_truth",
                        "alternate_path_symlink",
                        "alternate_path_traversal")))
    check("B1.2: the legitimate open is corroborated by a "
          "DISCOVERY in the twin's history",
          len(evidence_ev["payload"]["observed_discovery_seqs"]) >= 1)

    altered = copy.deepcopy(result)
    for a in altered["attempts"]:
        if a["attempt"] == "direct_read_ground_truth":
            a["outcome"] = "EXPOSED"
    r = attest_probe(exp, altered)
    check("B1.2: an altered outcome against a genuine twin is "
          "refused", r.get("ok") is False)
    check("B1.2: the altered submission recorded nothing",
          history_types(exp) == ["RUN_OPENED"])

    rep = copy.deepcopy(result)
    rep["execution_evidence"] = {
        "twin_root": result["twin_root"],
        "session_id": ptr["session_id"],
        "event_seq": session_ev["event_seq"],
        "event_hash": session_ev["hash"],
    }
    r = attest_probe(exp, rep)
    check("B1.2: a pointer retargeted at the session-opened event "
          "(a real event, but not evidence) is refused",
          r.get("ok") is False
          and "execution evidence" in (r.get("error") or ""))
    check("B1.2: the retargeted submission recorded nothing",
          history_types(exp) == ["RUN_OPENED"])

    # =================================================================
    # Phase D — the genuine flow, end to end
    # =================================================================
    att = attest_probe(exp, result)
    check("B1.2: the genuine session-based result attests at "
          "seq 2", att.get("ok") is True
          and att["result"]["event_seq"] == 2)
    check("B1.2: the experimental history is RUN_OPENED + "
          "BOUNDARY_PROBE (no twin-local types leak into it)",
          history_types(exp) == ["RUN_OPENED", "BOUNDARY_PROBE"])
    status = admin_request(exp, {"op": "status"})["result"]
    check("B1.2: status reports the attested, open run",
          status["run_status"] == "open" and status["attested"] is True)
    tok = admin_request(exp, {"op": "issue_token",
                              "agent_id": A})["result"]["token"]
    pat = agent_call(exp, "view_pattern", tok)
    check("B1.2: legitimate operations succeed after the genuine "
          "attestation",
          pat.get("ok") is True and len(pat["result"]["regions"]) == 6)
    opened = agent_call(exp, "open_region", tok,
                        {"region_id": COMPONENTS})
    check("B1.2: a region open serves genesis content after the "
          "genuine attestation",
          opened.get("ok") is True
          and opened["result"]["content"]
          == GENESIS_CONTENT[COMPONENTS])
finally:
    stop_service(proc, exp)

# =====================================================================
# Phase E — stale evidence: the twin rebuilt under an old result
# =====================================================================
result2 = run_twin_probe(BASE, "twin")  # rebuilds the twin: a new
# session, a new chain — the old result's evidence no longer stands
exp2 = build_runtime(BASE, "round4exp2")
proc = start_service(exp2)
try:
    admin_request(exp2, {"op": "open_run", "run_id": "round4-exp2"})
    r = attest_probe(exp2, result)
    check("B1.2: a result whose execution evidence stood in a "
          "since-rebuilt twin is refused",
          r.get("ok") is False)
    check("B1.2: the stale submission recorded nothing",
          history_types(exp2) == ["RUN_OPENED"])
    att = attest_probe(exp2, result2)
    check("B1.2: the rebuilt twin's own genuine result attests "
          "(the refusal was staleness, not the runtime)",
          att.get("ok") is True and att["result"]["event_seq"] == 2)
finally:
    stop_service(proc, exp2)

# The first experimental run's gate is claim-based once its
# attestation is recorded (accepted interpretation 3): rebuilding
# the twin afterwards does not un-attest it.
proc = start_service(exp)
try:
    status = admin_request(exp, {"op": "status"})["result"]
    check("B1.2: the recorded attestation survives the twin's "
          "rebuild (gate revalidation is claim-based)",
          status["attested"] is True
          and status["run_status"] == "open")
finally:
    stop_service(proc, exp)

print()
print("STAGE 2 CORRECTIONS ROUND 4 TESTS:", "ALL PASS" if not failures
      else f"FAILURES: {failures}")
sys.exit(1 if failures else 0)
