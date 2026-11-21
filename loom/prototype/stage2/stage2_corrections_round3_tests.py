"""Stage 2 corrections ROUND 3 tests: the three findings in Vane's
examination of corrections round 2 (at shelf commit 34e68891,
preserved as the examined artifact).

B1.1 — the probe_target posture is structurally confined to the
disposable twin: it is honoured only when the runtime's own rig
identity (service/rig.json, written at build time) says the
runtime IS a probe twin. An experimental runtime, a flipped rig,
or a missing rig identity refuses the posture at startup; the
twin's one bootstrap admission still works.

B1.2 — attestation provenance is validated, not merely present,
and tied to the actual twin: provenance VALUES (owner name, uid,
mode), the probe posture, and the twin service's build identity
are checked, and at recording time the experimental service
live-verifies the claim against the twin runtime as it actually
stands (rig identity, the twin store's run, live stats, the
twin's live code copy). Fabricated and mismatched claims are
refused and NOT recorded; the genuine probe result still attests.

B2.1 — the unrecordable-failure diagnostic is written atomically,
and a malformed candidate marker fails closed: a truncated
diagnostic restores the latch as an UNCERTAIN failure condition
(status diagnostic_state "unreadable"), invents no event, and
refuses every agent-facing route. Non-candidate files and a
well-formed diagnostic for a different run keep being ignored.

Run: python3 stage2_corrections_round3_tests.py
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
                                  runtime_paths, start_service,
                                  stop_service)

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
        "operations": ops, "rationale": "Round-3 test.",
        "discovery_source": "fabric_read", "discovery_ref": ref}}


GENESIS_CONTENT = {r["region_id"]: r["content"] for r in REGIONS}
A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"

AGENT_OPS = [
    ("view_pattern", {}),
    ("consult_index", {}),
    ("open_region", {"region_id": COMPONENTS}),
    ("submit", {"response": {"action": "idle"}}),
    ("read_breadth", {}),
]

BASE = RUNTIME_BASE
os.makedirs(BASE, exist_ok=True)


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


def start_refused(p, posture):
    """Attempt to start a service; return the RuntimeError text if
    startup was refused (the service exited early), else None."""
    try:
        proc = start_service(p, posture=posture)
    except RuntimeError as exc:
        return str(exc)
    stop_service(proc, p)
    return None


# =====================================================================
# Phase A — B1.1: probe_target is confined to the probe-twin rig
# =====================================================================
expA = build_runtime(BASE, "round3exp")  # rig: experimental (default)
err = start_refused(expA, "probe_target")
check("B1.1: probe_target on an EXPERIMENTAL runtime is refused "
      "at startup", err is not None)
with open(os.path.join(expA["root"], "service.log"),
          encoding="utf-8", errors="replace") as fh:
    log_text = fh.read()
check("B1.1: the startup refusal is recorded in the service log",
      "probe_target posture refused" in log_text)

# The same runtime in the enforced posture: the gate is real.
proc = start_service(expA)
try:
    status = admin_request(expA, {"op": "status"})["result"]
    check("B1.1: the experimental service reports its rig honestly",
          status["rig"] == "experimental"
          and status["posture"] == "enforced")
    admin_request(expA, {"op": "open_run", "run_id": "round3-exp"})
    r = admin_request(expA, {"op": "issue_token", "agent_id": A})
    check("B1.1: after the refused posture, issuance on the "
          "experimental runtime is still gated",
          r.get("ok") is False and r.get("kind") == "refusal")
    r = agent_call(expA, "view_pattern", "forged-token-not-issued")
    check("B1.1: after the refused posture, a data operation is "
          "still refused on the gate (not_attested)",
          r.get("ok") is False and r.get("kind") == "not_attested")
finally:
    stop_service(proc, expA)

# A rig record that does not say probe_twin cannot be overridden
# by the environment variable.
flip = build_runtime(BASE, "round3flipped", rig="probe_twin")
with open(flip["rig_path"], "w", encoding="utf-8") as fh:
    json.dump({"rig": "experimental", "runtime_root": flip["root"],
               "run_id": None}, fh)
err = start_refused(flip, "probe_target")
check("B1.1: a rig that does not say probe_twin refuses the "
      "posture (the env var cannot override the rig)",
      err is not None)

# No rig identity at all: nothing establishes a twin — refuse.
norig = build_runtime(BASE, "round3norig", rig="probe_twin")
os.remove(norig["rig_path"])
err = start_refused(norig, "probe_target")
check("B1.1: a missing rig identity refuses the posture",
      err is not None)

# The genuine twin rig: the posture is honoured, the one bootstrap
# admission works, and a probe target still never attests.
twinB = build_runtime(BASE, "round3twin", rig="probe_twin")
proc = start_service(twinB, posture="probe_target")
try:
    status = admin_request(twinB, {"op": "status"})["result"]
    check("B1.1: a probe-twin rig honours the probe_target posture",
          status["posture"] == "probe_target"
          and status["rig"] == "probe_twin")
    opened = admin_request(twinB, {"op": "open_run",
                                   "run_id": "round3-twin"})
    check("B1.1 setup: the twin run opens", opened.get("ok") is True)
    with open(twinB["rig_path"], encoding="utf-8") as fh:
        rig_record = json.load(fh)
    check("B1.1: opening the run records the run id in the rig "
          "identity", rig_record.get("run_id") == "round3-twin")
    issued = admin_request(twinB, {"op": "issue_token",
                                   "agent_id": A})
    check("B1.1: the twin's one bootstrap admission still works "
          "(issuance before attestation)",
          issued.get("ok") is True and bool(issued["result"]["token"]))
    r = admin_request(twinB, {"op": "record_probe_attestation",
                              "probe_result": {}})
    check("B1.1: a probe target still never records an attestation",
          r.get("ok") is False)
finally:
    stop_service(proc, twinB)

# =====================================================================
# Phase B — B1.2: provenance validated and tied to the actual twin
# =====================================================================
result = run_twin_probe(BASE, "twin")
twinP = runtime_paths(BASE, "twin")

exp = build_runtime(BASE, "round3prov")
proc = start_service(exp)
try:
    admin_request(exp, {"op": "open_run", "run_id": "round3-prov"})

    def refused_unrecorded(label, mutated):
        r = attest_probe(exp, mutated)
        hist = admin_request(exp, {"op": "history"})["result"]["events"]
        check(f"B1.2: {label} is refused and NOT recorded",
              r.get("ok") is False
              and [e["type"] for e in hist] == ["RUN_OPENED"])

    m = copy.deepcopy(result)
    m["twin_config"]["service"]["uid"] = 1001
    refused_unrecorded("a provenance entry with the wrong owner uid",
                       m)

    m = copy.deepcopy(result)
    m["twin_config"]["sock"]["mode"] = "0o777"
    refused_unrecorded("a provenance entry with a permissive mode", m)

    m = copy.deepcopy(result)
    m["service_code_hashes"]["service.py"] = "0" * 64
    refused_unrecorded("a wrong service build identity", m)

    m = copy.deepcopy(result)
    m["service_posture"] = "enforced"
    refused_unrecorded("a result claiming the enforced posture", m)

    m = copy.deepcopy(result)
    m["twin_root"] = exp["root"]
    refused_unrecorded(
        "provenance naming the experimental runtime itself as "
        "the twin", m)

    fabricated = {
        "twin_name": "ghost",
        "twin_root": os.path.join(BASE, "round3ghost"),
        "twin_config": copy.deepcopy(result["twin_config"]),
        "service_posture": "probe_target",
        "service_code_hashes": copy.deepcopy(
            result["service_code_hashes"]),
        "attempts": copy.deepcopy(result["attempts"]),
        "all_reads_denied": True,
        "socket_attacks_refused": True,
        "legitimate_access_ok": True,
        "probe_agent": result["probe_agent"],
        "summary": "Fabricated: every label correct, no twin "
                   "behind it.",
    }
    refused_unrecorded(
        "a fully fabricated all-passing result with no twin "
        "behind it", fabricated)

    r = admin_request(exp, {"op": "issue_token", "agent_id": A})
    check("B1.2: the gate stays closed after every fabricated or "
          "mismatched attestation",
          r.get("ok") is False and r.get("kind") == "refusal")

    # The claim must also match the twin AS IT STANDS: loosen the
    # twin's socket directory after the probe, and the genuine
    # result — whose claim says 0o711 — must now be refused.
    os.chmod(twinP["sock_dir"], 0o777)
    try:
        refused_unrecorded(
            "the genuine result after the twin's layout changed "
            "under it (live mismatch)", copy.deepcopy(result))
    finally:
        os.chmod(twinP["sock_dir"], 0o711)

    att = attest_probe(exp, result)
    check("B1.2: the genuine probe result still attests and opens "
          "the gate",
          att.get("ok") is True and att["result"]["event_seq"] == 2)
    status = admin_request(exp, {"op": "status"})["result"]
    check("B1.2: status reports the attested, open run",
          status["run_status"] == "open" and status["attested"] is True)
    tok_a = admin_request(exp, {"op": "issue_token",
                                "agent_id": A})["result"]["token"]
    pat = agent_call(exp, "view_pattern", tok_a)
    check("B1.2: legitimate operations succeed after the genuine "
          "attestation",
          pat.get("ok") is True and len(pat["result"]["regions"]) == 6)
finally:
    stop_service(proc, exp)

# =====================================================================
# Phase C — B2.1: atomic diagnostic; malformed marker fails closed
# =====================================================================
flt = build_runtime(BASE, "round3fault")
proc = start_service(flt, fault_inject="run_failed_append")
try:
    admin_request(flt, {"op": "open_run", "run_id": "round3-fault"})
    attest_probe(flt, result)
    tok_b = admin_request(flt, {"op": "issue_token",
                                "agent_id": B})["result"]["token"]
    resp = drive_breach(flt, tok_b, B)
    check("B2.1: the breaching submission is answered "
          "run_failed_unrecorded",
          resp.get("ok") is False
          and resp.get("kind") == "run_failed_unrecorded")
    status = admin_request(flt, {"op": "status"})["result"]
    check("B2.1: in-process status shows the written marker state",
          status["run_status"] == "failed_unrecorded"
          and status["diagnostic_state"] == "written"
          and status["diagnostic_written"] is True)
finally:
    stop_service(proc, flt)

diag_files = sorted(os.listdir(flt["failures_dir"]))
check("B2.1: the atomic write leaves exactly one complete "
      "diagnostic and no stranded temporary",
      len(diag_files) == 1 and diag_files[0].endswith(".json")
      and not diag_files[0].endswith(".tmp"))
if diag_files:
    with open(os.path.join(flt["failures_dir"], diag_files[0]),
              encoding="utf-8") as fh:
        diag = json.load(fh)
    check("B2.1: the diagnostic at the final path is complete "
          "(parses whole)",
          diag.get("kind") == "unrecordable_run_failure"
          and diag.get("run_id") == "round3-fault")

# Restart on the atomically written diagnostic: round 2's genuine
# behaviour is unchanged.
proc = start_service(flt)
try:
    status = admin_request(flt, {"op": "status"})["result"]
    check("B2.1: after restart the latch is restored from the "
          "diagnostic (state: restored)",
          status["run_status"] == "failed_unrecorded"
          and status["diagnostic_restored"] is True
          and status["diagnostic_state"] == "restored")
    tok_b2 = admin_request(flt, {"op": "issue_token",
                                 "agent_id": B})["result"]["token"]
    refused_all = all(
        agent_call(flt, op, tok_b2, args).get("kind")
        == "run_failed_unrecorded"
        for op, args in AGENT_OPS)
    check("B2.1: after restart every agent-facing route is refused",
          refused_all)
    hist = admin_request(flt, {"op": "history"})["result"]["events"]
    check("B2.1: after restart the history still holds no RUN_FAILED",
          not any(e["type"] == "RUN_FAILED" for e in hist))
finally:
    stop_service(proc, flt)

# A TRUNCATED candidate marker: an uncertain failure condition.
trc = build_runtime(BASE, "round3trunc")
trunc_path = os.path.join(
    trc["failures_dir"], "unrecorded-failure-20990101T000000.000000Z.json")
with open(trunc_path, "w", encoding="utf-8") as fh:
    fh.write('{"kind": "unrecordable_run_failure", "run_id": "round3-tr')
os.chown(trunc_path, 1000, 1000)
os.chmod(trunc_path, 0o600)
proc = start_service(trc)
try:
    status = admin_request(trc, {"op": "status"})["result"]
    check("B2.1: a truncated diagnostic fails closed at startup "
          "(failed_unrecorded, marker unreadable)",
          status["run_status"] == "failed_unrecorded"
          and status["latched_unrecorded_failure"] is True
          and status["diagnostic_state"] == "unreadable"
          and status["diagnostic_written"] is False
          and status["diagnostic_restored"] is False)
    refused_all = all(
        agent_call(trc, op, "any-token", args).get("kind")
        == "run_failed_unrecorded"
        for op, args in AGENT_OPS)
    check("B2.1: with an unreadable marker every agent-facing "
          "route is refused", refused_all)
    hist = admin_request(trc, {"op": "history"})["result"]["events"]
    check("B2.1: the uncertain latch invents no event",
          hist == [])
finally:
    stop_service(proc, trc)

# Non-candidates and another run's diagnostic keep being ignored.
oth = build_runtime(BASE, "round3other")
proc = start_service(oth)
try:
    admin_request(oth, {"op": "open_run", "run_id": "round3-other"})
finally:
    stop_service(proc, oth)
# The planted files are made loomfab-owned and readable, like a
# real diagnostic would be: this check exercises a READABLE
# well-formed marker for another run (an unreadable one is the
# B2.1 uncertain case above, and would latch — correctly).
with open(os.path.join(oth["failures_dir"], "notes.txt"),
          "w", encoding="utf-8") as fh:
    fh.write("not a diagnostic\n")
other_diag = os.path.join(
    oth["failures_dir"], "unrecorded-failure-20990101T000000.000000Z.json")
with open(other_diag, "w", encoding="utf-8") as fh:
    json.dump({"kind": "unrecordable_run_failure",
               "run_id": "some-other-run",
               "breach": None, "append_error": None}, fh)
os.chown(other_diag, 1000, 1000)
os.chmod(other_diag, 0o600)
proc = start_service(oth)
try:
    status = admin_request(oth, {"op": "status"})["result"]
    check("B2.1: an unrelated file and a different run's diagnostic "
          "do not latch this run",
          status["latched_unrecorded_failure"] is False
          and status["run_status"] == "unattested"
          and status["diagnostic_state"] == "none")
finally:
    stop_service(proc, oth)

print()
print("STAGE 2 CORRECTIONS ROUND 3 TESTS:", "ALL PASS" if not failures
      else f"FAILURES: {failures}")
sys.exit(1 if failures else 0)
