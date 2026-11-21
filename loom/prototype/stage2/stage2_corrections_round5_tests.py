"""Stage 2 corrections ROUND 5 tests: the one remaining blocker in
Vane's examination of corrections round 4 (at shelf commit
6f6b2eee, preserved as the examined artifact) — B1.2.1, exact
socket-operation binding. B1.1 and B2.1 are CLOSED and are not
retested here beyond the regression suites; B1.2.2's filesystem
qualification is accepted and its bases are asserted intact.

Round 4's observation logic matched a probe label to a loose
outcome class: any refused request with a non-session token could
stand as the forged-token refusal, any refused unknown operation
as the issuance refusal, and any successful session-token request
as either legitimate outcome. Round 5 binds each label to its
EXACT expected request:

  forged_token_open              <- open_region, non-session
                                    token, refused
  issuance_attempt_on_data_socket <- issue_token, refused
  legitimate_pattern_view        <- view_pattern, session token,
                                    ok
  legitimate_region_open         <- open_region, session token,
                                    the probe's expected region
                                    (fixture COMPONENTS), ok

Each negative case below sends a request whose OUTCOME is exactly
what the label claims but whose OPERATION (or region) is not the
one the label names — the request round 4 would have mis-recorded.
The observation must stay unrecorded: the session's PROBE_EVIDENCE
shows the outcome as not_observed, and an attestation built on
that session is refused, naming the outcome whose observed basis
is missing.

How the mislabeled requests are sent: probe_agent.py emits only
correctly labeled requests by construction, and the agent
client/runner cannot carry the probe_session/probe_attempt fields
at all — a mislabeled request exists only as a deliberate
fabrication, which is what these tests are. They are therefore
sent by this driver directly over the twin's data socket. The
observation rule under test is a function of the request/response
pair on that socket, whose access control is the token protocol
(the socket file is mode 777 by design), not the sender's OS
identity. The genuine probe flow (Phase C) still runs as a real
loomagent process, exactly as in every earlier round.

Run: python3 stage2_corrections_round5_tests.py
"""
import json
import os
import socket
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fabric.fixture import COMPONENTS, INTERACTIONS, REGIONS
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
FORGED = "forged-token-not-issued"

BASE = RUNTIME_BASE
os.makedirs(BASE, exist_ok=True)

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
SOCKET_LABELS = ("forged_token_open", "issuance_attempt_on_data_socket",
                 "legitimate_pattern_view", "legitimate_region_open")
FS_LABELS = ("direct_read_store", "direct_read_ground_truth",
             "alternate_path_symlink", "alternate_path_traversal")


def data_request(p, req):
    """One raw request to a runtime's data socket (see the header
    for why the mislabeled requests travel this way)."""
    line = (json.dumps(req) + "\n").encode("utf-8")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.settimeout(15.0)
        s.connect(p["data_sock"])
        s.sendall(line)
        buf = b""
        while not buf.endswith(b"\n"):
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
    return json.loads(buf.decode("utf-8"))


def history_types(p):
    hist = admin_request(p, {"op": "history"})["result"]["events"]
    return [e["type"] for e in hist]


def open_session(p):
    r = admin_request(p, {"op": "open_probe_session",
                          "agent_id": PROBE_AGENT_ID})
    assert r.get("ok"), r
    return r["result"]["session_id"], r["result"]["token"]


def fs_attempts(p):
    """The filesystem outcome records in the exact shape the
    genuine probe agent files them; the twin service checks each
    reported denial for entailment against its live configuration
    before recording it, whoever files it."""
    out = []
    for name, key in (("direct_read_store", "store_path"),
                      ("direct_read_ground_truth",
                       "ground_truth_path"),
                      ("alternate_path_symlink", "symlink_path"),
                      ("alternate_path_traversal", "traversal_path")):
        out.append({"attempt": name, "outcome": "denied",
                    "detail": {"path": p[key], "errno": 13,
                               "error": "PermissionError: "
                                        "Permission denied"}})
    return out


def finalize(p, sid, token):
    """File the filesystem report for a session and return the
    PROBE_EVIDENCE payload the twin service recorded for it."""
    resp = data_request(p, {"op": "probe_report", "token": token,
                            "probe_session": sid,
                            "attempts": fs_attempts(p)})
    assert resp.get("ok"), resp
    events = admin_request(p, {"op": "history"})["result"]["events"]
    ev = [e for e in events if e["type"] == "PROBE_EVIDENCE"
          and e["payload"].get("session_id") == sid]
    assert len(ev) == 1, ev
    return ev[0], resp["result"]


def fabricate(p, sid, event_seq, event_hash):
    """A complete, all-passing attestation result built around a
    REAL evidence record of the named twin — the strongest claim a
    mislabeled session could be dressed in. Modeled on round 4's
    fabricated result; only the execution-evidence check can
    refuse it, and only for what the twin's record actually says."""
    attempts = []
    for name, outcome in PASSING.items():
        detail = {"fabricated": True}
        if outcome == "denied":
            detail = {"errno": 13,
                      "error": "PermissionError: Permission denied"}
            key = {"direct_read_store": "store_path",
                   "direct_read_ground_truth": "ground_truth_path",
                   "alternate_path_symlink": "symlink_path",
                   "alternate_path_traversal": "traversal_path"}[name]
            detail["path"] = p[key]
        attempts.append({"attempt": name, "outcome": outcome,
                         "detail": detail})
    return {
        "twin_name": "round5twin",
        "twin_root": p["root"],
        "twin_config": stat_record(p),
        "service_posture": "probe_target",
        "service_code_hashes": code_copy_hashes(p),
        "execution_evidence": {"twin_root": p["root"],
                               "session_id": sid,
                               "event_seq": event_seq,
                               "event_hash": event_hash},
        "attempts": attempts,
        "all_reads_denied": True,
        "socket_attacks_refused": True,
        "legitimate_access_ok": True,
        "probe_agent": PROBE_AGENT_ID,
        "summary": "Built around a real twin session's evidence "
                   "record (round 5 negative control).",
    }


# =====================================================================
# Phase A — the negative cases: outcome right, operation wrong
# =====================================================================
twin = build_twin_runtime(BASE, "round5twin")
exp = build_runtime(BASE, "round5exp")
twin_proc = start_service(twin, posture="probe_target")
exp_proc = start_service(exp)
try:
    admin_request(twin, {"op": "open_run", "run_id": "round5-twin"})
    admin_request(exp, {"op": "open_run", "run_id": "round5-exp"})

    def negative(case, label, req, want_ok, use_token=False,
                 also_unrecorded=None):
        sid, token = open_session(twin)
        req = dict(req, probe_session=sid, probe_attempt=label)
        if use_token:
            req["token"] = token
        resp = data_request(twin, req)
        check(f"B1.2.1 ({case}): the mislabeled request itself "
              f"{'succeeds' if want_ok else 'is refused'} — only "
              "its operation/region is wrong for the label",
              resp.get("ok") is want_ok)
        ev, _ = finalize(twin, sid, token)
        outcomes = ev["payload"]["outcomes"]
        entry = outcomes[label]
        check(f"B1.2.1 ({case}): the {label} observation stays "
              "UNRECORDED in the twin's evidence",
              entry["outcome"] is None
              and entry["basis"] == "not_observed")
        for other in (also_unrecorded or []):
            check(f"B1.2.1 ({case}): the request satisfies "
                  f"neither label — {other} is unrecorded too",
                  outcomes[other]["outcome"] is None
                  and outcomes[other]["basis"] == "not_observed")
        r = attest_probe(exp, fabricate(twin, sid,
                                        ev["event_seq"], ev["hash"]))
        check(f"B1.2.1 ({case}): an attestation built on the "
              "mislabeled session is refused, naming the outcome "
              "whose observed basis is missing",
              r.get("ok") is False and label in (r.get("error") or ""))
        check(f"B1.2.1 ({case}): the refused attestation records "
              "nothing on the experimental run",
              history_types(exp) == ["RUN_OPENED"])

    # (a) forged_token_open on a refused view_pattern, foreign token
    negative("a", "forged_token_open",
             {"op": "view_pattern", "token": FORGED}, False)
    # (b1) issuance label on a refused unknown operation
    negative("b1", "issuance_attempt_on_data_socket",
             {"op": "nonsense", "agent_id": PROBE_AGENT_ID}, False)
    # (b2) issuance label on a refused open_region, foreign token
    negative("b2", "issuance_attempt_on_data_socket",
             {"op": "open_region", "token": FORGED,
              "region_id": COMPONENTS}, False)
    # (c) legitimate_pattern_view on a successful open_region —
    # the request IS a genuine region open in substance, but it
    # carries the pattern label, so it satisfies NEITHER label:
    # observations attach to (label, exact request) pairs.
    negative("c", "legitimate_pattern_view",
             {"op": "open_region", "region_id": COMPONENTS}, True,
             use_token=True,
             also_unrecorded=["legitimate_region_open"])
    # (d) legitimate_region_open on a successful view_pattern —
    # and the view satisfies neither label either (it carried the
    # region label, not its own).
    negative("d", "legitimate_region_open",
             {"op": "view_pattern"}, True, use_token=True,
             also_unrecorded=["legitimate_pattern_view"])
    # (e) legitimate_region_open on a successful open of the
    # WRONG region (INTERACTIONS, not the probe's COMPONENTS)
    negative("e", "legitimate_region_open",
             {"op": "open_region", "region_id": INTERACTIONS}, True,
             use_token=True)

    # =================================================================
    # Phase B — the same raw requests, correctly labeled: the
    # session completes, and the SAME experimental service that
    # refused every mislabeled session accepts this one.
    # =================================================================
    sid, token = open_session(twin)
    r1 = data_request(twin, {
        "op": "open_region", "token": FORGED,
        "region_id": COMPONENTS, "probe_session": sid,
        "probe_attempt": "forged_token_open"})
    r2 = data_request(twin, {
        "op": "issue_token", "agent_id": PROBE_AGENT_ID,
        "probe_session": sid,
        "probe_attempt": "issuance_attempt_on_data_socket"})
    r3 = data_request(twin, {
        "op": "view_pattern", "token": token, "probe_session": sid,
        "probe_attempt": "legitimate_pattern_view"})
    r4 = data_request(twin, {
        "op": "open_region", "token": token,
        "region_id": COMPONENTS, "probe_session": sid,
        "probe_attempt": "legitimate_region_open"})
    check("B1.2.1 control: the four correctly labeled requests "
          "have the outcomes their labels claim",
          r1.get("ok") is False and r2.get("ok") is False
          and r3.get("ok") is True and r4.get("ok") is True)
    ev, _ = finalize(twin, sid, token)
    outcomes = ev["payload"]["outcomes"]
    check("B1.2.1 control: all four socket outcomes stand in the "
          "evidence as OBSERVED with their passing values",
          all(outcomes[n]["basis"] == "observed"
              and outcomes[n]["outcome"] == PASSING[n]
              for n in SOCKET_LABELS))
    check("B1.2.2: the filesystem outcomes keep their distinct "
          "agent_reported_entailment_verified basis — none is "
          "dressed as observed",
          all(outcomes[n]["basis"]
              == "agent_reported_entailment_verified"
              and outcomes[n]["outcome"] == "denied"
              for n in FS_LABELS))
    att = attest_probe(exp, fabricate(twin, sid, ev["event_seq"],
                                      ev["hash"]))
    check("B1.2.1 control: the correctly labeled session attests "
          "on the same experimental service that refused the "
          "mislabeled ones",
          att.get("ok") is True and att["result"]["event_seq"] == 2)
    check("B1.2.1 control: the experimental history is exactly "
          "RUN_OPENED + BOUNDARY_PROBE",
          history_types(exp) == ["RUN_OPENED", "BOUNDARY_PROBE"])
finally:
    stop_service(twin_proc, twin)
    stop_service(exp_proc, exp)

# =====================================================================
# Phase C — positive control: the genuine probe flow, end to end
# (a real loomagent probe process, as in every earlier round)
# =====================================================================
result = run_twin_probe(BASE, "twin")
twinP = runtime_paths(BASE, "twin")
twin_store = EventStore(twinP["store_path"])
try:
    twin_events = twin_store.all_events()
finally:
    twin_store._conn.close()
evidence_ev = [e for e in twin_events
               if e["type"] == "PROBE_EVIDENCE"][-1]
outcomes = evidence_ev["payload"]["outcomes"]
check("B1.2.1 genuine: the genuine probe's socket outcomes stand "
      "as OBSERVED by the service",
      all(outcomes[n]["basis"] == "observed"
          and outcomes[n]["outcome"] == PASSING[n]
          for n in SOCKET_LABELS))
check("B1.2.2 genuine: the genuine probe's filesystem outcomes "
      "stand as agent-reported with entailment verified — the "
      "qualification is in the machine-readable record, distinct "
      "from observed",
      all(outcomes[n]["basis"] == "agent_reported_entailment_verified"
          and outcomes[n]["outcome"] == "denied" for n in FS_LABELS)
      and not any(outcomes[n]["basis"] == "observed"
                  for n in FS_LABELS))

exp2 = build_runtime(BASE, "round5exp2")
proc = start_service(exp2)
try:
    admin_request(exp2, {"op": "open_run", "run_id": "round5-exp2"})
    att = attest_probe(exp2, result)
    check("B1.2.1 genuine: the genuine session-based result "
          "attests at seq 2",
          att.get("ok") is True and att["result"]["event_seq"] == 2)
    check("B1.2.1 genuine: the experimental history is RUN_OPENED "
          "+ BOUNDARY_PROBE",
          history_types(exp2) == ["RUN_OPENED", "BOUNDARY_PROBE"])
    tok = admin_request(exp2, {"op": "issue_token",
                               "agent_id": A})["result"]["token"]
    pat = agent_call(exp2, "view_pattern", tok)
    check("B1.2.1 genuine: legitimate operations succeed after "
          "the genuine attestation",
          pat.get("ok") is True and len(pat["result"]["regions"]) == 6)
    opened = agent_call(exp2, "open_region", tok,
                        {"region_id": COMPONENTS})
    check("B1.2.1 genuine: a region open serves genesis content "
          "after the genuine attestation",
          opened.get("ok") is True
          and opened["result"]["content"] == GENESIS_CONTENT[COMPONENTS])
finally:
    stop_service(proc, exp2)

print()
print("STAGE 2 CORRECTIONS ROUND 5 TESTS:", "ALL PASS" if not failures
      else f"FAILURES: {failures}")
sys.exit(1 if failures else 0)
