"""Stage 2 corrections-round tests: the two-OS-context boundary
(service + client over a Unix socket), boundary probe v2 against a
disposable twin, the seq-2 BOUNDARY_PROBE attestation, durable
RUN_FAILED with terminal enforcement, the failure-of-failure latch,
and the IDLE event. Run: python3 stage2_corrections_tests.py

Every agent operation in the socket phases is performed by a real
loomagent process (runuser), and every service runs as loomfab.
Evidence (stat records, probe outcomes) is written to
boundary-runtime/RUNTIME-EVIDENCE.json in the workspace.
"""
import json
import os
import sys
import tempfile
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fabric.canonical import canonical, sha256_hex
from fabric.engine import Engine, verify_chain
from fabric.fixture import (COMPONENTS, STATE, CONSTITUTION_HASH,
                            REGIONS, ground_truth_document)
from fabric.harness import Harness, HarnessRefusal
from fabric.probe2 import attest_probe, run_twin_probe
from fabric.runtime_setup import (RUNTIME_BASE, admin_request,
                                  agent_call, build_runtime,
                                  code_copy_hashes, runtime_paths,
                                  start_service, stat_record,
                                  stop_service, tree_hashes)
from fabric.store import EventStore

failures = []
evidence = {}


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
        "operations": ops, "rationale": "Corrections-round test.",
        "discovery_source": "fabric_read", "discovery_ref": ref}}


GENESIS_CONTENT = {r["region_id"]: r["content"] for r in REGIONS}
A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
C = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
Z = "12121212-1212-4121-8121-121212121212"

BASE = RUNTIME_BASE
os.makedirs(BASE, exist_ok=True)

# =====================================================================
# Phase 0 — runtime layout, ownership, code-copy identity
# =====================================================================
exp = build_runtime(BASE, "experimental")
twin_pre = build_runtime(BASE, "twin")  # probe2 rebuilds it; layout first
exp_map = stat_record(exp)
twin_map = stat_record(twin_pre)
evidence["experimental_layout"] = exp_map
check("service directory is loomfab-only (700)",
      exp_map["service"] == {"owner": "loomfab", "mode": "0o700"})
check("ground-truth file is loomfab 600",
      exp_map["service/ground-truth.json"]
      == {"owner": "loomfab", "mode": "0o600"})
check("socket directory is traverse-only (711)",
      exp_map["sock"] == {"owner": "loomfab", "mode": "0o711"})
check("agent home belongs to loomagent",
      exp_map["agent-home"]["owner"] == "loomagent")
check("twin layout equals experimental layout (owners + modes)",
      twin_map == exp_map)
check("service code copy is byte-identical to the tree",
      code_copy_hashes(exp) == tree_hashes())
with open(exp["ground_truth_path"], "rb") as fh:
    gt_bytes = fh.read()
check("ground-truth file carries exactly the fixture's sealed document",
      sha256_hex(gt_bytes) == sha256_hex(canonical(ground_truth_document())))

# =====================================================================
# Phase 1 — boundary probe v2 against the disposable twin
# =====================================================================
result = run_twin_probe(BASE, "twin")
evidence["probe_result"] = result
by_name = {a["attempt"]: a for a in result["attempts"]}
for name in ("direct_read_store", "direct_read_ground_truth",
             "alternate_path_symlink", "alternate_path_traversal"):
    a = by_name[name]
    check(f"probe: {name} denied by the OS",
          a["outcome"] == "denied" and a["detail"].get("errno") == 13,
          a["detail"].get("error", ""))
check("probe: forged token refused",
      by_name["forged_token_open"]["outcome"] == "refused")
check("probe: issuance attempt on the data socket refused (no route)",
      by_name["issuance_attempt_on_data_socket"]["outcome"] == "refused")
check("probe: legitimate pattern view succeeds (isolated, not disabled)",
      by_name["legitimate_pattern_view"]["outcome"] == "ok"
      and by_name["legitimate_pattern_view"]["detail"]["regions"] == 6)
check("probe: legitimate region open succeeds",
      by_name["legitimate_region_open"]["outcome"] == "ok"
      and by_name["legitimate_region_open"]["detail"]["content_bytes"]
      == len(GENESIS_CONTENT[COMPONENTS]))
check("probe verdicts: reads denied, attacks refused, legitimate ok",
      result["all_reads_denied"] and result["socket_attacks_refused"]
      and result["legitimate_access_ok"])
twin_cfg = result["twin_config"]
check("twin store file was loomfab 600 during the probe",
      twin_cfg["service/events.db"] == {"owner": "loomfab",
                                        "mode": "0o600"})
check("twin config matches experimental layout on shared entries",
      all(twin_cfg[k] == exp_map[k] for k in exp_map))

# =====================================================================
# Phase 2 — the experimental run: genesis, then ONE attestation
# =====================================================================
proc = start_service(exp)
try:
    status = admin_request(exp, {"op": "status"})
    check("before: experimental run unopened, zero events",
          status["result"]["events"] == 0
          and status["result"]["run_status"] == "unopened")
    opened = admin_request(exp, {"op": "open_run",
                                 "run_id": "stage2-corrections-exp"})
    check("experimental run opens (genesis)", opened.get("ok") is True)
    att = attest_probe(exp, result)
    check("attestation appended as seq 2",
          att.get("ok") is True and att["result"]["event_seq"] == 2)
    hist = admin_request(exp, {"op": "history"})["result"]["events"]
    check("history is exactly RUN_OPENED + BOUNDARY_PROBE",
          [e["type"] for e in hist] == ["RUN_OPENED", "BOUNDARY_PROBE"])
    att_ev = hist[1]
    check("attestation is a system event carrying the probe provenance",
          att_ev["actor"] == "00000000-0000-4000-8000-000000000000"
          and att_ev["payload"]["attestation"] is True
          and att_ev["payload"]["probe_result_hash"]
          == sha256_hex(canonical(result))
          and att_ev["payload"]["probe"]["all_reads_denied"] is True)
    check("attestation payload carries a plain-words summary",
          bool(att_ev["payload"].get("summary")))
    check("probe introduced no DISCOVERY events into the history",
          not any(e["type"] == "DISCOVERY" for e in hist))
    tok_z = admin_request(exp, {"op": "issue_token",
                                "agent_id": Z})["result"]["token"]
    breadth = agent_call(exp, "read_breadth", tok_z)
    check("probe left the read record empty",
          breadth.get("ok") is True and breadth["result"] == 0.0)

    # =================================================================
    # Phase 3 — legitimate agent operations through the socket
    # =================================================================
    tok_a = admin_request(exp, {"op": "issue_token",
                                "agent_id": A})["result"]["token"]
    pat = agent_call(exp, "view_pattern", tok_a)
    check("agent pattern view through the socket",
          pat.get("ok") is True and len(pat["result"]["regions"]) == 6)
    opened_region = agent_call(exp, "open_region", tok_a,
                               {"region_id": COMPONENTS})
    check("agent region open serves genesis content",
          opened_region.get("ok") is True
          and opened_region["result"]["content"]
          == GENESIS_CONTENT[COMPONENTS])
    breadth = agent_call(exp, "read_breadth", tok_a)
    check("agent read breadth is 1/6 after one open",
          breadth["result"] == 1 / 6)

    # =================================================================
    # Phase 4 — IDLE is a durable event
    # =================================================================
    idle = agent_call(exp, "submit", tok_a, {"response": {"action": "idle"}})
    check("idle through the socket returns a durable event sequence",
          idle.get("ok") is True
          and idle["result"]["outcome"] == "idle"
          and idle["result"]["event_seq"] == 4)
    hist = admin_request(exp, {"op": "history"})["result"]["events"]
    idle_evs = [e for e in hist if e["type"] == "IDLE"]
    check("IDLE event is in the history, by the agent, with a summary",
          len(idle_evs) == 1 and idle_evs[0]["actor"] == A
          and bool(idle_evs[0]["payload"].get("summary")))

    # =================================================================
    # Phase 5 — hard-line breach: durable RUN_FAILED, terminal
    # =================================================================
    tok_b = admin_request(exp, {"op": "issue_token",
                                "agent_id": B})["result"]["token"]
    opened_b = agent_call(exp, "open_region", tok_b,
                          {"region_id": STATE})
    check("second agent opens State", opened_b.get("ok") is True)
    hist = admin_request(exp, {"op": "history"})["result"]["events"]
    b_disc_seq = [e["event_seq"] for e in hist
                  if e["type"] == "DISCOVERY" and e["actor"] == B][-1]
    breach = contrib(B, {STATE: 1, COMPONENTS: 1}, [STATE, COMPONENTS],
                     [STATE],
                     [{"kind": "replace_content", "region_id": STATE,
                       "new_content": "B claims a read it never made."}],
                     b_disc_seq)
    resp = agent_call(exp, "submit", tok_b, {"response": breach})
    check("breaching submission refused as run_failed",
          resp.get("ok") is False and resp.get("kind") == "run_failed")
    hist = admin_request(exp, {"op": "history"})["result"]["events"]
    failed_evs = [e for e in hist if e["type"] == "RUN_FAILED"]
    check("RUN_FAILED is recorded once, as a system event",
          len(failed_evs) == 1
          and failed_evs[0]["actor"]
          == "00000000-0000-4000-8000-000000000000")
    fp = failed_evs[0]["payload"]
    check("RUN_FAILED payload carries the breach evidence",
          fp["breach"] == "hard_line_read_record"
          and fp["declared_read_set"] == sorted([STATE, COMPONENTS])
          and fp["recorded_read_set"] == [STATE]
          and fp["claimed_but_not_made"] == [COMPONENTS]
          and bool(fp.get("summary")))
    post = [
        ("view_pattern", tok_b, {}),
        ("consult_index", tok_b, {}),
        ("open_region", tok_b, {"region_id": STATE}),
        ("submit", tok_b, {"response": {"action": "idle"}}),
        ("read_breadth", tok_b, {}),
        ("view_pattern", tok_a, {}),
        ("open_region", tok_a, {"region_id": STATE}),
    ]
    refused_all = all(
        agent_call(exp, op, tok, args).get("ok") is False
        for op, tok, args in post)
    check("post-breach: every agent-facing route refuses, for every agent",
          refused_all)
    status = admin_request(exp, {"op": "status"})
    check("service status reports the failed run",
          status["result"]["run_status"] == "failed"
          and status["result"]["latched_unrecorded_failure"] is False)
finally:
    stop_service(proc, exp)

# Durability across a restart: the failed state comes from the history.
proc = start_service(exp)
try:
    status = admin_request(exp, {"op": "status"})
    check("after restart the run is still failed (state from history)",
          status["result"]["run_status"] == "failed")
    tok_a2 = admin_request(exp, {"op": "issue_token",
                                 "agent_id": A})["result"]["token"]
    resp = agent_call(exp, "view_pattern", tok_a2)
    check("after restart, agent operations still refuse",
          resp.get("ok") is False and resp.get("kind") == "run_failed")
finally:
    stop_service(proc, exp)

# Replay of the whole experimental history (root, direct store read):
# IDLE folds, RUN_FAILED folds to failed state, the chain verifies.
store = EventStore(exp["store_path"])
eng = Engine(store)
replayed = eng.replay()
check("replay of the experimental history yields the failed state",
      replayed.get("run_status") == "failed"
      and replayed["failure"]["breach"] == "hard_line_read_record")
ok, bad = verify_chain(store.all_events(), CONSTITUTION_HASH)
check("experimental chain verifies end to end", ok and bad is None)
check("the failed run's fabric content is untouched (all regions v1)",
      all(r["version"] == 1 for r in replayed["regions"].values()))

# =====================================================================
# Phase 6 — failure of failure: latch, diagnostic, no fabricated event
# =====================================================================
flt = build_runtime(BASE, "faulttest")
proc = start_service(flt, fault_inject="run_failed_append")
try:
    admin_request(flt, {"op": "open_run", "run_id": "stage2-fault-test"})
    # Round-2 setup adjustment (B1): the admission gate now refuses
    # token issuance before attestation, so this run is attested
    # first — with the Phase 1 twin-probe result, through its admin
    # path (same boundary configuration).
    attest_probe(flt, result)
    tok_c = admin_request(flt, {"op": "issue_token",
                                "agent_id": C})["result"]["token"]
    agent_call(flt, "open_region", tok_c, {"region_id": COMPONENTS})
    hist = admin_request(flt, {"op": "history"})["result"]["events"]
    c_disc_seq = [e["event_seq"] for e in hist
                  if e["type"] == "DISCOVERY"][-1]
    breach = contrib(C, {COMPONENTS: 1, STATE: 1}, [COMPONENTS, STATE],
                     [COMPONENTS],
                     [{"kind": "replace_content",
                       "region_id": COMPONENTS,
                       "new_content": "C claims a read it never made."}],
                     c_disc_seq)
    resp = agent_call(flt, "submit", tok_c, {"response": breach})
    check("unrecordable failure: breach response says so",
          resp.get("ok") is False
          and resp.get("kind") == "run_failed_unrecorded")
    resp2 = agent_call(flt, "view_pattern", tok_c)
    check("unrecordable failure: service stays latched closed",
          resp2.get("ok") is False
          and resp2.get("kind") == "run_failed_unrecorded")
    hist = admin_request(flt, {"op": "history"})["result"]["events"]
    check("unrecordable failure: NO RUN_FAILED event was fabricated",
          not any(e["type"] == "RUN_FAILED" for e in hist)
          and [e["type"] for e in hist]
          == ["RUN_OPENED", "BOUNDARY_PROBE", "DISCOVERY"])
    status = admin_request(flt, {"op": "status"})
    # Round-2 adjustment (B2-mandated vocabulary): the status no
    # longer calls a latched run "open"; it reports the unambiguous
    # failed_unrecorded, and shows the durable diagnostic marker.
    check("status distinguishes the unrecordable failure (latched)",
          status["result"]["latched_unrecorded_failure"] is True
          and status["result"]["run_status"] == "failed_unrecorded"
          and status["result"]["diagnostic_written"] is True)
finally:
    stop_service(proc, flt)
diag_files = sorted(os.listdir(flt["failures_dir"]))
check("diagnostic record written to the service failures directory",
      len(diag_files) == 1 and diag_files[0].startswith(
          "unrecorded-failure-"))
if diag_files:
    with open(os.path.join(flt["failures_dir"], diag_files[0])) as fh:
        diag = json.load(fh)
    evidence["unrecorded_failure_diagnostic"] = diag
    check("diagnostic record carries breach + append error + timestamp",
          diag["kind"] == "unrecordable_run_failure"
          and "injected fault" in diag["append_error"]
          and diag["breach"]["declared_read_set"]
          == sorted([COMPONENTS, STATE])
          and bool(diag["timestamp_utc"]))

# =====================================================================
# Phase 7 — in-process: IDLE durability/replay, RUN_FAILED fold guard
# =====================================================================
tmp = tempfile.mkdtemp()
store7 = EventStore(os.path.join(tmp, "inprocess.db"))
eng7 = Engine.open_run(store7, "corrections-inprocess")
h7 = Harness(eng7)
tok7 = h7.issue_token(A)
out = h7.submit(tok7, {"action": "idle"})
check("in-process idle appends a durable IDLE event",
      out["outcome"] == "idle" and out["event_seq"] == 2
      and [e["type"] for e in store7.all_events()]
      == ["RUN_OPENED", "IDLE"])
check("in-process idle is replay-safe",
      eng7.replay()["last_seq"] == 2)
eng7.commit_events([("RUN_FAILED", "00000000-0000-4000-8000-000000000000",
                     [], {"breach": "hard_line_read_record",
                          "summary": "Test failure."})])
check("RUN_FAILED folds to failed state, live and on replay",
      eng7.state.get("run_status") == "failed"
      and eng7.replay().get("run_status") == "failed")
h7b = Harness(eng7)
tok7b = h7b.issue_token(B)
try:
    h7b.open_region(tok7b, STATE)
    check("harness over a failed history refuses agent operations", False)
except HarnessRefusal:
    check("harness over a failed history refuses agent operations", True)
store8 = EventStore(os.path.join(tmp, "healthy.db"))
eng8 = Engine.open_run(store8, "corrections-healthy")
check("healthy genesis state carries no failure keys",
      "run_status" not in eng8.state and "failure" not in eng8.state)

# -- evidence out ------------------------------------------------------
ws_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "boundary-runtime")
os.makedirs(ws_dir, exist_ok=True)
with open(os.path.join(ws_dir, "RUNTIME-EVIDENCE.json"), "w") as fh:
    json.dump(evidence, fh, indent=2, sort_keys=True, default=str)

print()
print("STAGE 2 CORRECTIONS TESTS:", "ALL PASS" if not failures
      else f"FAILURES: {failures}")
sys.exit(1 if failures else 0)
