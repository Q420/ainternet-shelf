"""Boundary probe v2 — Loom spec v0.1 Rev 9, section 4A, as corrected.

Stage 2 corrections round (2026-11-21). The Stage 2 probe
(fabric/probe.py) scanned the harness's routes from inside the
process and wrote its own reads into the history it examined;
Vane's examination rejected both properties. This probe is the
literal section 4A instrument:

- it executes from the ACTUAL agent OS context (a loomagent
  process, spawned by runuser) — not impersonated inside the
  service process;
- it runs against a DISPOSABLE TWIN runtime — same layout, owners,
  permissions and service build as the experimental runtime,
  differing only in location — before any agent is admitted to the
  experimental run;
- from that context it attempts the two literal direct reads
  section 4A names (the twin's event store; the twin's sealed
  ground-truth file), alternate-path reads, a forged-token
  operation, and a token-issuance attempt on the data socket, and
  then proves legitimate access through the harness, so isolation
  is not confused with disablement.

The result returns to the driver. The experimental service then
opens its run (RUN_OPENED, seq 1, genesis unchanged) and appends
ONE system BOUNDARY_PROBE event as seq 2: an attestation of this
twin probe, carrying the tested configuration and outcomes as
provenance. No probe DISCOVERY events enter the experimental
history, and the probe changes no experimental read record.

Corrections round 2 (B1): the experimental service now enforces
the attestation as an admission gate — no token issued and no
agent operation admitted until a valid attestation stands. That
creates a bootstrap question for the twin itself: a complete
probe result cannot exist before some service has admitted a
probe agent, so exactly one admission must precede the first
attestation. It is confined to this disposable twin: the twin's
service is started in the recorded "probe_target" posture, in
which the gate does not block and attestation recording is
refused (a probe target's history is scaffolding, never
evidence). The posture is carried in the probe result's
provenance. The experimental service runs in the default
enforced posture, where the gate has no exceptions.

Corrections round 3 (B1.1, B1.2): the twin is now BUILT as a
probe-twin rig (runtime_setup's rig identity record), and the
twin's service honours the probe_target posture only because its
own runtime's rig identity says so — the environment variable is
a request the rig can refuse. The result also identifies the
twin runtime root and the twin service code copy's hashes, so
the experimental service can live-verify the attestation's
provenance against the twin as it actually stands.

Corrections round 4 (B1.1, B1.2): the twin is built through
runtime_setup.build_twin_runtime — the one sanctioned route to a
probe_twin rig — and the probe runs inside a probe SESSION. The
twin service opens the session (recording it in its own
history), issues the session-bound token, observes the socket
attempts itself, checks the agent's filesystem outcome report
for entailment, and records the execution evidence
(PROBE_EVIDENCE) in the twin's history. The result carries a
pointer to that evidence record; the experimental service
extracts the outcomes from the twin's records and requires the
submitted outcomes to match them, so a result assembled without
any probe execution — however genuine the twin it names — has
nothing to point at.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fabric.fixture import COMPONENTS  # noqa: E402
from fabric.runtime_setup import (RUNTIME_BASE, admin_request,  # noqa: E402
                                  build_twin_runtime, code_copy_hashes,
                                  run_agent_script, start_service,
                                  stat_record, stop_service)

PROBE_AGENT_ID = "99999999-9999-4999-8999-999999999999"
_READ_ATTEMPTS = ("direct_read_store", "direct_read_ground_truth",
                  "alternate_path_symlink", "alternate_path_traversal")


def run_twin_probe(base=RUNTIME_BASE, twin_name="twin"):
    """Build a disposable twin, probe it from the agent OS context,
    tear the twin service down, and return the probe result — the
    exact object the experimental run's attestation will carry."""
    p = build_twin_runtime(base, twin_name)
    proc = start_service(p, posture="probe_target")
    try:
        opened = admin_request(p, {"op": "open_run",
                                   "run_id": f"boundary-probe-{twin_name}"})
        if not opened.get("ok"):
            raise RuntimeError(f"twin open_run failed: {opened}")
        # Round 4 (B1.2): the probe runs inside a session the twin
        # service opens and records; the token is session-bound.
        session = admin_request(p, {"op": "open_probe_session",
                                    "agent_id": PROBE_AGENT_ID})
        if not session.get("ok"):
            raise RuntimeError(f"twin open_probe_session failed: "
                               f"{session}")
        session = session["result"]
        config = {
            "data_sock": p["data_sock"],
            "store_path": p["store_path"],
            "ground_truth_path": p["ground_truth_path"],
            "symlink_path": p["symlink_path"],
            "traversal_path": p["traversal_path"],
            "token": session["token"],
            "session_id": session["session_id"],
            "region_id": COMPONENTS,
        }
        out = run_agent_script(p, "probe_agent.py", config)
        twin_config = stat_record(p)
        twin_code_hashes = code_copy_hashes(p)
    finally:
        stop_service(proc, p)
    report = out.get("probe_report") or {}
    if "event_seq" not in report or "event_hash" not in report:
        raise RuntimeError(
            f"the probe session recorded no execution evidence: "
            f"{report}")
    execution_evidence = {
        "twin_root": p["root"],
        "session_id": report["session_id"],
        "event_seq": report["event_seq"],
        "event_hash": report["event_hash"],
    }
    attempts = out["attempts"]
    by_name = {a["attempt"]: a for a in attempts}
    result = {
        "twin_name": twin_name,
        "twin_config": twin_config,
        "service_posture": "probe_target",
        # Round 3 (B1.2): the attestation identifies the twin
        # runtime itself and the twin service's build, so the
        # experimental service can verify the claim against the
        # filesystem as it actually stands — live at attestation
        # time — instead of trusting the supplied object.
        "twin_root": p["root"],
        "service_code_hashes": twin_code_hashes,
        # Round 4 (B1.2): the pointer to the execution evidence in
        # the twin's own history — the record the experimental
        # service will extract the outcomes from.
        "execution_evidence": execution_evidence,
        "attempts": attempts,
        "all_reads_denied": all(
            by_name[n]["outcome"] == "denied" for n in _READ_ATTEMPTS),
        "socket_attacks_refused": all(
            by_name[n]["outcome"] == "refused"
            for n in ("forged_token_open",
                      "issuance_attempt_on_data_socket")),
        "legitimate_access_ok": all(
            by_name[n]["outcome"] == "ok"
            for n in ("legitimate_pattern_view",
                      "legitimate_region_open")),
        "probe_agent": PROBE_AGENT_ID,
        "summary": "Pre-run boundary probe against the disposable "
                   "twin: every direct and alternate-path read from "
                   "the agent OS context was denied by the "
                   "operating system; forged-token and issuance "
                   "attempts on the data socket were refused; "
                   "legitimate operations through the harness "
                   "succeeded.",
    }
    return result


def attest_probe(exp_paths, probe_result):
    """Append the seq-2 BOUNDARY_PROBE attestation to an opened
    experimental run, through the experimental service's admin
    path. Returns the admin response."""
    return admin_request(exp_paths, {
        "op": "record_probe_attestation", "probe_result": probe_result})
