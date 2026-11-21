"""Stage 2 corrections ROUND 2 tests: the two enforcements Vane's
examination of the corrections round required (blockers B1 and B2
at shelf commit 1019aaaf, preserved as the examined artifact).

B1 — the boundary attestation is an admission gate enforced by
the service state machine: no token issued and no agent operation
admitted before a valid, successful attestation stands at seq 2;
the attestation handler validates outcomes, provenance, and the
result hash before recording, and refuses (without recording)
failed, malformed, or incomplete results.

B2 — an unrecordable failure is terminal across service restart:
the diagnostic record in the service failures directory is a
durable stop marker; a fresh service on the same runtime restores
the latch from it before serving, reports failed_unrecorded, and
fabricates no RUN_FAILED. The diagnostic-cannot-be-written case
is characterised honestly: the latch holds in-process, status
shows diagnostic_written false, and — the recorded limit — with
no durable marker the stop does not survive restart.

Run: python3 stage2_corrections_round2_tests.py
Every agent operation is performed by a real loomagent process;
every service runs as loomfab.
"""
import copy
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fabric.fixture import COMPONENTS, STATE, REGIONS
from fabric.probe2 import attest_probe, run_twin_probe
from fabric.runtime_setup import (RUNTIME_BASE, admin_request,
                                  agent_call, build_runtime,
                                  start_service, stop_service)

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        failures.append(name)


def new_id():
    return str(uuid.uuid4())


def contrib(author, base, read, write, ops, ref):
    return {"action": "contribute", "contribution": {
        "author": author, "idempotency_id": new_id(),
        "base_versions": base, "read_set": read, "write_set": write,
        "operations": ops, "rationale": "Round-2 test.",
        "discovery_source": "fabric_read", "discovery_ref": ref}}


GENESIS_CONTENT = {r["region_id"]: r["content"] for r in REGIONS}
A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
C = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
D = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"

BASE = RUNTIME_BASE
os.makedirs(BASE, exist_ok=True)

# A genuine, complete probe result (against the disposable twin),
# shared by the phases below as the attestation source.
result = run_twin_probe(BASE, "twin")


def drive_breach(p, token, agent):
    """Open COMPONENTS, then submit a schema-valid contribution
    declaring a read (STATE) the agent never made: a hard-line
    breach. Returns the submit response."""
    agent_call(p, "open_region", token, {"region_id": COMPONENTS})
    hist = admin_request(p, {"op": "history"})["result"]["events"]
    disc_seq = [e["event_seq"] for e in hist
                if e["type"] == "DISCOVERY"][-1]
    breach = contrib(agent, {COMPONENTS: 1, STATE: 1},
                     [COMPONENTS, STATE], [COMPONENTS],
                     [{"kind": "replace_content",
                       "region_id": COMPONENTS,
                       "new_content": "Claims a read never made."}],
                     disc_seq)
    return agent_call(p, "submit", token, {"response": breach})


# =====================================================================
# Phase A — B1: the attestation is an admission gate
# =====================================================================
exp = build_runtime(BASE, "round2exp")
other = build_runtime(BASE, "round2other")
proc = start_service(exp)
proc_other = start_service(other)
try:
    # Another runtime, properly attested, to mint a foreign token.
    admin_request(other, {"op": "open_run", "run_id": "round2-other"})
    attest_probe(other, result)
    tok_other = admin_request(other, {"op": "issue_token",
                                      "agent_id": D})["result"]["token"]

    r = admin_request(exp, {"op": "issue_token", "agent_id": A})
    check("B1: token issuance before the run is opened is refused",
          r.get("ok") is False and r.get("kind") == "refusal")
    opened = admin_request(exp, {"op": "open_run",
                                 "run_id": "round2-exp"})
    check("B1 setup: the run opens (genesis)", opened.get("ok") is True)
    r = admin_request(exp, {"op": "issue_token", "agent_id": A})
    check("B1: token issuance before attestation is refused",
          r.get("ok") is False and r.get("kind") == "refusal")
    r = agent_call(exp, "view_pattern", tok_other)
    check("B1: a foreign token before attestation is refused "
          "on the gate (not_attested)",
          r.get("ok") is False and r.get("kind") == "not_attested")
    r = agent_call(exp, "view_pattern", "forged-token-not-issued")
    check("B1: a forged token before attestation is refused "
          "on the gate (not_attested)",
          r.get("ok") is False and r.get("kind") == "not_attested")
    status = admin_request(exp, {"op": "status"})["result"]
    check("B1: status reports the unattested run honestly",
          status["run_status"] == "unattested"
          and status["attested"] is False)

    # A FAILED attestation: one required outcome flipped.
    failed_result = copy.deepcopy(result)
    for a in failed_result["attempts"]:
        if a["attempt"] == "direct_read_store":
            a["outcome"] = "EXPOSED"
    r = attest_probe(exp, failed_result)
    hist = admin_request(exp, {"op": "history"})["result"]["events"]
    check("B1: a failed attestation is refused and NOT recorded",
          r.get("ok") is False
          and [e["type"] for e in hist] == ["RUN_OPENED"])
    r = admin_request(exp, {"op": "issue_token", "agent_id": A})
    check("B1: issuance still refused after a failed attestation",
          r.get("ok") is False)

    # A MALFORMED attestation: a required outcome missing.
    malformed = copy.deepcopy(result)
    malformed["attempts"] = [
        a for a in malformed["attempts"]
        if a["attempt"] != "legitimate_region_open"]
    r = attest_probe(exp, malformed)
    hist = admin_request(exp, {"op": "history"})["result"]["events"]
    check("B1: a malformed attestation (missing outcome) is "
          "refused and NOT recorded",
          r.get("ok") is False
          and [e["type"] for e in hist] == ["RUN_OPENED"])

    # An INCOMPLETE attestation: no provenance.
    incomplete = copy.deepcopy(result)
    del incomplete["twin_config"]
    r = attest_probe(exp, incomplete)
    hist = admin_request(exp, {"op": "history"})["result"]["events"]
    check("B1: an incomplete attestation (no provenance) is "
          "refused and NOT recorded",
          r.get("ok") is False
          and [e["type"] for e in hist] == ["RUN_OPENED"])

    # An attestation whose supplied result hash does not recompute.
    r = admin_request(exp, {"op": "record_probe_attestation",
                            "probe_result": result,
                            "probe_result_hash": "0" * 64})
    hist = admin_request(exp, {"op": "history"})["result"]["events"]
    check("B1: a wrong result hash is refused and NOT recorded",
          r.get("ok") is False
          and [e["type"] for e in hist] == ["RUN_OPENED"])

    # The valid attestation: the gate opens, the path still works.
    att = attest_probe(exp, result)
    check("B1: a valid attestation is recorded at seq 2",
          att.get("ok") is True and att["result"]["event_seq"] == 2)
    status = admin_request(exp, {"op": "status"})["result"]
    check("B1: status reports the attested, open run",
          status["run_status"] == "open" and status["attested"] is True)
    r = attest_probe(exp, result)
    hist = admin_request(exp, {"op": "history"})["result"]["events"]
    check("B1: a second attestation is refused (placement)",
          r.get("ok") is False and len(hist) == 2)
    tok_a = admin_request(exp, {"op": "issue_token",
                                "agent_id": A})["result"]["token"]
    pat = agent_call(exp, "view_pattern", tok_a)
    check("B1: after attestation, issuance and legitimate "
          "operations succeed",
          pat.get("ok") is True and len(pat["result"]["regions"]) == 6)
    opened_region = agent_call(exp, "open_region", tok_a,
                               {"region_id": COMPONENTS})
    check("B1: region open serves genesis content after attestation",
          opened_region.get("ok") is True
          and opened_region["result"]["content"]
          == GENESIS_CONTENT[COMPONENTS])
    r = agent_call(exp, "view_pattern", tok_other)
    check("B1: the same foreign token after attestation is refused "
          "as a token (refusal), not on the gate",
          r.get("ok") is False and r.get("kind") == "refusal")
finally:
    stop_service(proc, exp)
    stop_service(proc_other, other)

# =====================================================================
# Phase B — B2: the unrecordable failure survives restart
# =====================================================================
flt = build_runtime(BASE, "round2fault")
proc = start_service(flt, fault_inject="run_failed_append")
try:
    admin_request(flt, {"op": "open_run", "run_id": "round2-fault"})
    attest_probe(flt, result)
    tok_b = admin_request(flt, {"op": "issue_token",
                                "agent_id": B})["result"]["token"]
    resp = drive_breach(flt, tok_b, B)
    check("B2: the breaching submission is answered "
          "run_failed_unrecorded",
          resp.get("ok") is False
          and resp.get("kind") == "run_failed_unrecorded")
    status = admin_request(flt, {"op": "status"})["result"]
    check("B2: in-process status is failed_unrecorded with a "
          "durable marker written",
          status["run_status"] == "failed_unrecorded"
          and status["latched_unrecorded_failure"] is True
          and status["diagnostic_written"] is True
          and status["diagnostic_restored"] is False)
finally:
    stop_service(proc, flt)

# A FRESH service on the same runtime, with NO fault injected: the
# stop must come from the diagnostic marker, not from the fault.
proc = start_service(flt)
try:
    status = admin_request(flt, {"op": "status"})["result"]
    check("B2: after restart the latch is restored from the "
          "diagnostic (failed_unrecorded)",
          status["run_status"] == "failed_unrecorded"
          and status["latched_unrecorded_failure"] is True
          and status["diagnostic_written"] is True
          and status["diagnostic_restored"] is True)
    tok_b2 = admin_request(flt, {"op": "issue_token",
                                 "agent_id": B})["result"]["token"]
    attempts = [
        ("view_pattern", {}),
        ("consult_index", {}),
        ("open_region", {"region_id": COMPONENTS}),
        ("submit", {"response": {"action": "idle"}}),
        ("read_breadth", {}),
    ]
    refused_all = all(
        agent_call(flt, op, tok_b2, args).get("kind")
        == "run_failed_unrecorded"
        for op, args in attempts)
    check("B2: after restart every agent-facing route is refused",
          refused_all)
    hist = admin_request(flt, {"op": "history"})["result"]["events"]
    check("B2: after restart the history still holds no RUN_FAILED",
          not any(e["type"] == "RUN_FAILED" for e in hist)
          and [e["type"] for e in hist]
          == ["RUN_OPENED", "BOUNDARY_PROBE", "DISCOVERY"])
finally:
    stop_service(proc, flt)

# =====================================================================
# Phase C — B2: the diagnostic cannot be written
# =====================================================================
flt2 = build_runtime(BASE, "round2fault2")
proc = start_service(flt2,
                     fault_inject="run_failed_append,diagnostic_write")
try:
    admin_request(flt2, {"op": "open_run", "run_id": "round2-fault2"})
    attest_probe(flt2, result)
    tok_c = admin_request(flt2, {"op": "issue_token",
                                 "agent_id": C})["result"]["token"]
    resp = drive_breach(flt2, tok_c, C)
    check("B2: with the diagnostic unwritable the breach is still "
          "answered run_failed_unrecorded",
          resp.get("ok") is False
          and resp.get("kind") == "run_failed_unrecorded")
    resp2 = agent_call(flt2, "view_pattern", tok_c)
    check("B2: the latch holds in-process with no durable marker",
          resp2.get("ok") is False
          and resp2.get("kind") == "run_failed_unrecorded")
    status = admin_request(flt2, {"op": "status"})["result"]
    check("B2: status honestly shows failed_unrecorded with "
          "diagnostic_written false",
          status["run_status"] == "failed_unrecorded"
          and status["latched_unrecorded_failure"] is True
          and status["diagnostic_written"] is False)
    check("B2: no diagnostic file exists in the failures directory",
          os.listdir(flt2["failures_dir"]) == [])
finally:
    stop_service(proc, flt2)

# The recorded limit, characterised rather than hidden: with no
# durable marker, a fresh service has nothing to restore — the
# stop does NOT survive restart, and nothing claims it does.
proc = start_service(flt2)
try:
    status = admin_request(flt2, {"op": "status"})["result"]
    tok_c2 = admin_request(flt2, {"op": "issue_token",
                                  "agent_id": C})["result"]["token"]
    resp = agent_call(flt2, "view_pattern", tok_c2)
    check("B2 limit: with no durable marker the stop does not "
          "survive restart (nothing claims otherwise)",
          status["run_status"] == "open"
          and status["latched_unrecorded_failure"] is False
          and resp.get("ok") is True)
finally:
    stop_service(proc, flt2)

print()
print("STAGE 2 CORRECTIONS ROUND 2 TESTS:", "ALL PASS" if not failures
      else f"FAILURES: {failures}")
sys.exit(1 if failures else 0)
