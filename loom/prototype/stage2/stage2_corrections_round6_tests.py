"""Stage 2 corrections ROUND 6 tests: the one remaining item in
Vane's examination of corrections round 5 (at shelf commit
672a876c, preserved as the examined artifact) — the token-presence
half of B1.2.1. Everything else is CLOSED or ACCEPTED (B1.1,
B1.2.2, B2.1, the session/evidence architecture) and is not
retested here beyond the regression suites.

Round 5 bound each observation label to its exact request, but the
forged_token_open branch tested only that the supplied value
DIFFERED from the session token:

    req.get("token") != session["token"]

An absent token, token: null, or an empty value differs too — so
a request that omitted its credential could be recorded as an
attempted use of a foreign one. A missing credential is not a
forged credential. Round 6 requires the token to be a non-empty
STRING that differs from the session token, on an open_region,
refused, before forged_token_open is recorded.

Each negative case below sends an open_region labeled
forged_token_open whose credential carriage is defective in one
of the four named ways. The request is refused (only its
credential carriage is wrong for the label), the observation must
stay unrecorded — the session's PROBE_EVIDENCE shows
forged_token_open as not_observed — and an attestation built on
that session is refused, naming the outcome.

How the defective requests are sent: as in round 5 (the stated
exception Vane accepted), the genuine probe agent constructs only
well-formed requests, and the agent client/runner cannot carry a
missing, null, or non-string token as a deliberate fabrication —
so these requests are sent by this driver directly over the
twin's data socket. The observation rule under test is a function
of the request/response pair on that socket, whose access control
is the token protocol, not the sender's OS identity. The genuine
probe flow (Phase C) still runs as a real loomagent process.

Run: python3 stage2_corrections_round6_tests.py
"""
import json
import os
import socket
import sys

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
FORGED = "forged-token-not-issued"
OMIT = object()  # sentinel: do not send a token field at all

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
    for why the defective requests travel this way)."""
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
    token-defective session could be dressed in. Only the
    execution-evidence check can refuse it, and only for what the
    twin's record actually says."""
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
        "twin_name": "round6twin",
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
                   "record (round 6 negative control).",
    }


# =====================================================================
# Phase A — the negative cases: the operation and the refusal are
# exactly what the label claims; only the credential carriage is
# defective (no token was actually supplied as a non-empty string)
# =====================================================================
twin = build_twin_runtime(BASE, "round6twin")
exp = build_runtime(BASE, "round6exp")
twin_proc = start_service(twin, posture="probe_target")
exp_proc = start_service(exp)
try:
    admin_request(twin, {"op": "open_run", "run_id": "round6-twin"})
    admin_request(exp, {"op": "open_run", "run_id": "round6-exp"})

    def negative(case, carriage, token_value):
        sid, token = open_session(twin)
        req = {"op": "open_region", "region_id": COMPONENTS,
               "probe_session": sid,
               "probe_attempt": "forged_token_open"}
        if token_value is not OMIT:
            req["token"] = token_value
        resp = data_request(twin, req)
        check(f"B1.2.1-token ({case}): the request with {carriage} "
              "is refused — only its credential carriage is wrong "
              "for the label",
              resp.get("ok") is False)
        ev, _ = finalize(twin, sid, token)
        entry = ev["payload"]["outcomes"]["forged_token_open"]
        check(f"B1.2.1-token ({case}): the forged_token_open "
              "observation stays UNRECORDED in the twin's evidence",
              entry["outcome"] is None
              and entry["basis"] == "not_observed")
        r = attest_probe(exp, fabricate(twin, sid,
                                        ev["event_seq"], ev["hash"]))
        check(f"B1.2.1-token ({case}): an attestation built on "
              "the session is refused, naming the outcome whose "
              "observed basis is missing",
              r.get("ok") is False
              and "forged_token_open" in (r.get("error") or ""))
        check(f"B1.2.1-token ({case}): the refused attestation "
              "records nothing on the experimental run",
              history_types(exp) == ["RUN_OPENED"])

    # (a) no token field at all
    negative("a", "no token field", OMIT)
    # (b) token: null
    negative("b", "token null", None)
    # (c) token: "" (empty string)
    negative("c", "an empty-string token", "")
    # (d) a non-string token value: a number
    negative("d", "a numeric token", 12345)
    # (e) a non-string token value: a list
    negative("e", "a list token", ["not", "a", "token"])

    # =================================================================
    # Phase B — positive control at the session level: the same
    # four requests, correctly labeled, the forged attempt carrying
    # a non-empty foreign token string. The session completes, and
    # the SAME experimental service that refused every defective
    # session accepts this one.
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
    check("B1.2.1-token control: the four correctly labeled "
          "requests have the outcomes their labels claim",
          r1.get("ok") is False and r2.get("ok") is False
          and r3.get("ok") is True and r4.get("ok") is True)
    ev, _ = finalize(twin, sid, token)
    outcomes = ev["payload"]["outcomes"]
    check("B1.2.1-token control: a non-empty foreign token IS "
          "observed as the forged attempt, and all four socket "
          "outcomes stand in the evidence as OBSERVED with their "
          "passing values",
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
    check("B1.2.1-token control: the correctly labeled session "
          "attests on the same experimental service that refused "
          "the token-defective ones",
          att.get("ok") is True and att["result"]["event_seq"] == 2)
    check("B1.2.1-token control: the experimental history is "
          "exactly RUN_OPENED + BOUNDARY_PROBE",
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
check("B1.2.1-token genuine: the genuine probe's socket outcomes "
      "stand as OBSERVED by the service",
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

exp2 = build_runtime(BASE, "round6exp2")
proc = start_service(exp2)
try:
    admin_request(exp2, {"op": "open_run", "run_id": "round6-exp2"})
    att = attest_probe(exp2, result)
    check("B1.2.1-token genuine: the genuine session-based result "
          "attests at seq 2",
          att.get("ok") is True and att["result"]["event_seq"] == 2)
    check("B1.2.1-token genuine: the experimental history is "
          "RUN_OPENED + BOUNDARY_PROBE",
          history_types(exp2) == ["RUN_OPENED", "BOUNDARY_PROBE"])
    tok = admin_request(exp2, {"op": "issue_token",
                               "agent_id": A})["result"]["token"]
    pat = agent_call(exp2, "view_pattern", tok)
    check("B1.2.1-token genuine: legitimate operations succeed "
          "after the genuine attestation",
          pat.get("ok") is True and len(pat["result"]["regions"]) == 6)
    opened = agent_call(exp2, "open_region", tok,
                        {"region_id": COMPONENTS})
    check("B1.2.1-token genuine: a region open serves genesis "
          "content after the genuine attestation",
          opened.get("ok") is True
          and opened["result"]["content"] == GENESIS_CONTENT[COMPONENTS])
finally:
    stop_service(proc, exp2)

print()
print("STAGE 2 CORRECTIONS ROUND 6 TESTS:", "ALL PASS" if not failures
      else f"FAILURES: {failures}")
sys.exit(1 if failures else 0)
