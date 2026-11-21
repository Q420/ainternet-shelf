#!/usr/bin/env python3
"""Closing exercise — one full mechanical lifecycle, end to end.

The prototype commission's closing step (2026-11-21, after Stage 4
acceptance): a single Stage 4-bound run driven through the real
socket service — the loomfab-owned fabric service on the data
socket, every agent operation performed by a genuine loomagent
process — from bound open to RUN_CLOSED, exercising in one
continuous history: the boundary probe attestation, capped reads,
ordinary contributions, the Annex D S3 plant rejected at
admission, the planted semantic contradiction surfaced by
examination and assessed with a recorded disagreement, completion
claims and accounting, an IDLE, the TV-1 structural lifecycle
(fault in the live view only, explicit restart repair, correcting
contribution, resolution), seals throughout, the starvation
report, and the close with its tail anchor.

NO live agents: every actor is this scripted mechanical driver.
NO production code is changed by the exercise.

Outputs (in this directory):
  closing-lifecycle-history.json   the run's full exported history
  closing-lifecycle-narrative.md   plain-words narrative generated
                                   FROM the events (every line
                                   cites its event seq)
  closing-anchor.json              the content-addressed archival
                                   anchor record for the run's tail

Run: python3 closing_exercise.py [suffix] — prints PASS/FAIL per
beat; exit status is non-zero on any failure. The optional suffix
is inserted into the three output filenames (the closing
correction round re-drives with "-correction", so its artifacts
land as new files alongside the preserved round's).
"""
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fabric.canonical import canonical, sha256_hex
from fabric.engine import state_hash, verified_fold
from fabric.fixture import (COMPONENTS, CONTINUITY, INTERACTIONS,
                            OPERATIONS, PRESENTATION, STATE,
                            CONSTITUTION_HASH)
from fabric.packpin import PACK_ID, PACK_SHA256, PACK_VERSION
from fabric.probe2 import attest_probe, run_twin_probe
from fabric.runtime_setup import (RUNTIME_BASE, admin_request,
                                  agent_call, build_runtime,
                                  start_service, stop_service)
from fabric.starvation import build_report, report_bytes

D_CS = "00000000-0000-4000-8000-000000000102"  # Components uses State
GENESIS_HASH = ("9a7250bde82bfd8bd220b6013f38b4ce289a702fe86119f"
                "2723616055c070b1f")
RUN_ID = "closing-lifecycle"
ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = RUNTIME_BASE
os.makedirs(BASE, exist_ok=True)

A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
C = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
NAMES = {A: "Agent A", B: "Agent B", C: "Agent C",
         "11111111-1111-4111-8111-111111111111": "Components",
         "22222222-2222-4222-8222-222222222222": "Interactions",
         "33333333-3333-4333-8333-333333333333": "State",
         "44444444-4444-4444-8444-444444444444": "Continuity",
         "55555555-5555-4555-8555-555555555555": "Presentation",
         "66666666-6666-4666-8666-666666666666": "Operations"}

failures = []
BEATS = {}


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        failures.append(name)


def new_id():
    return str(uuid.uuid4())


def contrib(author, idem, base, read, write, ops, ref):
    return {"action": "contribute", "contribution": {
        "author": author, "idempotency_id": idem, "base_versions": base,
        "read_set": read, "write_set": write, "operations": ops,
        "rationale": "Closing exercise: recorded rationale.",
        "discovery_source": "fabric_read", "discovery_ref": ref}}


def history_of(exp):
    return admin_request(exp, {"op": "history"})["result"]["events"]


def last_discovery(exp, actor):
    return [e["event_seq"] for e in history_of(exp)
            if e["type"] == "DISCOVERY" and e["actor"] == actor][-1]


def events_of(hist, type_):
    return [e for e in hist if e["type"] == type_]


def call(exp, op, token, args=None):
    resp = agent_call(exp, op, token, args or {})
    assert resp.get("ok") is True, (op, resp)
    return resp["result"]


def submit(exp, token, response):
    return call(exp, "submit", token, {"response": response})


exp = build_runtime(BASE, "closing-main")
proc = start_service(exp)
try:
    # -- Beat 1: bound open -------------------------------------------
    resp = admin_request(exp, {"op": "open_run", "run_id": RUN_ID,
                               "bind_stage4": True})
    check("beat 1: the run opens through the service's admin path",
          resp.get("ok") is True)
    hist = history_of(exp)
    opened = hist[0]
    pack = opened["payload"].get("validation_pack", {})
    auth = opened["payload"].get("authority_set", {})
    check("beat 1: RUN_OPENED binds Rev 9 + A1 + the pinned pack "
          "(id, version, digest)",
          opened["type"] == "RUN_OPENED"
          and auth.get("spec") == "loom-spec-v0.1-rev9"
          and auth.get("amendments") == ["A1"]
          and pack.get("id") == PACK_ID
          and pack.get("version") == PACK_VERSION
          and pack.get("sha256") == PACK_SHA256)
    genesis_hash = state_hash(verified_fold([opened],
                                            CONSTITUTION_HASH))
    check("beat 1: the genesis state hash is the pinned constant",
          genesis_hash == GENESIS_HASH, genesis_hash[:16] + "…")
    BEATS["open"] = opened["event_seq"]

    # -- Beat 2: the boundary probe attestation -----------------------
    # The probe itself ran against the disposable twin; its
    # attestation is recorded in this run at seq 2 — after the run
    # opened (seq 1) and before agent admission.
    result = run_twin_probe(BASE, "closing-twin")
    att = attest_probe(exp, result)
    hist = history_of(exp)
    probe_ev = hist[1]
    check("beat 2: the twin boundary probe is attested into the "
          "run at seq 2 (BOUNDARY_PROBE), after the run opened "
          "and before agent admission",
          att.get("ok") is True
          and att["result"]["event_seq"] == 2
          and probe_ev["type"] == "BOUNDARY_PROBE")
    BEATS["probe"] = probe_ev["event_seq"]

    tok = {x: admin_request(exp, {"op": "issue_token",
                                   "agent_id": x})["result"]["token"]
           for x in (A, B, C)}

    # -- Beat 3: capped reads ------------------------------------------
    for agent, regions in ((A, (INTERACTIONS, CONTINUITY)),
                           (B, (COMPONENTS, STATE)),
                           (C, (PRESENTATION,))):
        for rid in regions:
            call(exp, "open_region", tok[agent], {"region_id": rid})
    breadth = {x: call(exp, "read_breadth", tok[x]) for x in (A, B, C)}
    check("beat 3: DISCOVERY reads recorded; every agent's "
          "cumulative breadth stays under the RB < 0.5 cap "
          "(A 2/6, B 2/6, C 1/6)",
          abs(breadth[A] - 2 / 6) < 1e-9
          and abs(breadth[B] - 2 / 6) < 1e-9
          and abs(breadth[C] - 1 / 6) < 1e-9
          and all(v < 0.5 for v in breadth.values()),
          f"breadth={ {k[-1]: round(v, 3) for k, v in breadth.items()} }")
    BEATS["reads"] = (last_discovery(exp, A), last_discovery(exp, C))

    # -- Beat 4a: ordinary contribution — A on Interactions ------------
    out = submit(exp, tok[A], contrib(
        A, new_id(), {INTERACTIONS: 1, CONTINUITY: 1},
        [INTERACTIONS, CONTINUITY], [INTERACTIONS],
        [{"kind": "append_content", "region_id": INTERACTIONS,
          "text": " Closing note: requests carry their context."}],
        last_discovery(exp, A)))
    cid_ai = out.get("contribution_id")
    hist = history_of(exp)
    attempts = events_of(hist, "SEAL_ATTEMPTED")
    check("beat 4: A's ordinary contribution to Interactions is "
          "accepted; its seal attempt passes and issues the §7 seal "
          "record (structure only, no semantic clearance)",
          out["outcome"] == "accepted" and len(attempts) == 1
          and attempts[-1]["payload"]["outcome"] == "pass"
          and attempts[-1]["payload"]["seal"]
              ["contributions_since_last_seal"] == [cid_ai]
          and attempts[-1]["payload"]["seal"]
              ["semantic_clearance"] is False)
    BEATS["contrib_a"] = attempts[-1]["event_seq"] if attempts \
        else None

    # -- Beat 4b: ordinary contribution — B on State -------------------
    out = submit(exp, tok[B], contrib(
        B, new_id(), {COMPONENTS: 1, STATE: 1}, [COMPONENTS, STATE],
        [STATE],
        [{"kind": "append_content", "region_id": STATE,
          "text": " Closing note: State keeps what must be kept."}],
        last_discovery(exp, B)))
    cid_bs = out.get("contribution_id")
    hist = history_of(exp)
    folded = verified_fold(hist, CONSTITUTION_HASH)
    check("beat 4: B's ordinary contribution to State is accepted; "
          "State advances to version 2",
          out["outcome"] == "accepted"
          and folded["regions"][STATE]["version"] == 2)
    BEATS["contrib_b"] = [e["event_seq"] for e in
                          events_of(hist, "CONTRIBUTION_ACCEPTED")
                          if e["payload"].get("contribution_id")
                          == cid_bs][0]

    # -- Beat 4c: the Annex D plant — S3 cycle rejected at admission ---
    out = submit(exp, tok[B], contrib(
        B, new_id(), {COMPONENTS: 1, STATE: 2}, [COMPONENTS, STATE],
        [COMPONENTS, STATE],
        [{"kind": "add_dependency",
          "dependency": {"source": STATE, "target": COMPONENTS,
                         "kind": "uses"}}],
        last_discovery(exp, B)))
    hist = history_of(exp)
    rej = events_of(hist, "CONTRIBUTION_REJECTED")[-1]
    check("beat 4: the proposed State→Components uses edge (the "
          "Annex D plant, closing the S3 cycle) is rejected at "
          "admission as structural S3, on the record; the standing "
          "graph is unchanged",
          out["outcome"] == "structural"
          and rej["payload"].get("invariant") == "S3"
          and len(verified_fold(hist, CONSTITUTION_HASH)
                  ["dependencies"]) == 4)
    BEATS["plant_rejected"] = rej["event_seq"]

    # -- Beat 5: the semantic contradiction, examined + assessed -------
    exam = call(exp, "examine", tok[A], {"report": {
        "author": A, "examination_id": new_id(),
        "idempotency_id": new_id(),
        "regions": [INTERACTIONS, CONTINUITY],
        "description": "Interactions declares requests stateless — "
                       "no component remembers a caller between "
                       "requests. Continuity pins a working session "
                       "to one component, which holds the session's "
                       "state between steps. The two cannot both "
                       "hold as written.",
        "discovery_source": "fabric_read",
        "discovery_ref": last_discovery(exp, A)}})
    T = exam.get("tension_id")
    check("beat 5: A's ExaminationReport over {Interactions, "
          "Continuity} creates the semantic tension (origin "
          "examination)",
          exam["outcome"] == "created" and T is not None)
    BEATS["tension_raised"] = [e["event_seq"] for e in
                               events_of(history_of(exp),
                                         "TENSION_RAISED")
                               if e["payload"].get("tension_id")
                               == T][0]

    out_b = call(exp, "assess", tok[B], {"assessment": {
        "assessment_id": new_id(), "author": B,
        "target_kind": "tension", "target_id": T,
        "position": "addressed",
        "reasoning": "The session-pinning passage governs a "
                     "narrower case than the statelessness claim; "
                     "read together, the contradiction is addressed "
                     "by scope."}})
    out_c = call(exp, "assess", tok[C], {"assessment": {
        "assessment_id": new_id(), "author": C,
        "target_kind": "tension", "target_id": T,
        "position": "clarifies",
        "reasoning": "The passages still contradict on their face; "
                     "this clarifies the conflict but does not "
                     "address it away."}})
    folded = verified_fold(history_of(exp), CONSTITUTION_HASH)
    positions = sorted(a["position"] for a in
                       folded["assessments"].values()
                       if a["target_id"] == T)
    check("beat 5: two assessments, different positions "
          "(addressed vs clarifies) — the disagreement is preserved "
          "on the record; the tension stands examined, not resolved",
          out_b["outcome"] == "recorded"
          and out_c["outcome"] == "recorded"
          and positions == ["addressed", "clarifies"]
          and folded["tensions"][T]["status"] == "examined")
    BEATS["assessed"] = events_of(history_of(exp),
                                  "ASSESSMENT_RECORDED")[-1][
                                      "event_seq"]

    # -- Beat 7: claims + completion accounting -------------------------
    out = call(exp, "claim_completion", tok[B], {"claim": {
        "claim_id": new_id(), "facet": STATE, "facet_version": 2,
        "supporting_contributions": [cid_bs],
        "rationale": "State's closing work is done."}})
    check("beat 7: B's CompletionClaim for State at version 2, "
          "citing B's State contribution, is recorded",
          out["outcome"] == "recorded")
    out = call(exp, "assess", tok[A], {"assessment": {
        "assessment_id": new_id(), "author": A,
        "target_kind": "facet", "target_id": STATE,
        "position": "examined",
        "reasoning": "Reviewed State at its current version.",
        "version_reviewed": 2}})
    folded = verified_fold(history_of(exp), CONSTITUTION_HASH)
    check("beat 7: A's independent current-version review "
          "completes State (claim + review, different agents)",
          out["outcome"] == "recorded"
          and folded["facet_status"].get(STATE) == "complete")
    BEATS["state_complete"] = events_of(history_of(exp),
                                        "ASSESSMENT_RECORDED")[-1][
                                            "event_seq"]
    out = call(exp, "claim_completion", tok[A], {"claim": {
        "claim_id": new_id(), "facet": INTERACTIONS,
        "facet_version": 2, "supporting_contributions": [cid_ai],
        "rationale": "Interactions' closing work is done."}})
    folded = verified_fold(history_of(exp), CONSTITUTION_HASH)
    accounting_mid = {rid: folded["facet_status"].get(rid,
                                                      "unexamined")
                      for rid in (COMPONENTS, INTERACTIONS, STATE,
                                  CONTINUITY, PRESENTATION,
                                  OPERATIONS)}
    check("beat 7: A claims Interactions (no review yet — it "
          "stands claimed); the accounting across all six facets "
          "at this point: State complete, Interactions claimed, "
          "the rest unexamined",
          out["outcome"] == "recorded"
          and accounting_mid[INTERACTIONS] == "claimed"
          and accounting_mid[STATE] == "complete"
          and all(accounting_mid[r] == "unexamined" for r in
                  (COMPONENTS, CONTINUITY, PRESENTATION, OPERATIONS)),
          f"accounting={accounting_mid}")
    BEATS["claimed"] = events_of(history_of(exp),
                                 "COMPLETION_CLAIMED")[-1][
                                     "event_seq"]

    # -- Beat 8: IDLE ----------------------------------------------------
    out = submit(exp, tok[C], {"action": "idle"})
    hist = history_of(exp)
    idles = events_of(hist, "IDLE")
    check("beat 8: C idles — a durable IDLE event, evidence-only "
          "under A1 (no fabric-state change follows from it)",
          out["outcome"] == "idle" and len(idles) == 1
          and idles[0]["actor"] == C)
    BEATS["idle"] = idles[0]["event_seq"]

    # -- Beat 6: the TV-1 structural lifecycle, in this same run --------
    resp = admin_request(exp, {"op": "inject_live_state_fault",
                               "region_id": STATE})
    check("beat 6: the fault is injected into the live derived "
          "state only; the history still folds to a state holding "
          "State",
          resp.get("ok") is True
          and verified_fold(history_of(exp), CONSTITUTION_HASH)
              ["regions"][STATE]["version"] == 2)
    out = submit(exp, tok[A], contrib(
        A, new_id(), {INTERACTIONS: 2, CONTINUITY: 1},
        [INTERACTIONS, CONTINUITY], [CONTINUITY],
        [{"kind": "append_content", "region_id": CONTINUITY,
          "text": " Closing note: what must survive an interruption "
                  "is named."}],
        last_discovery(exp, A)))
    hist = history_of(exp)
    attempts = events_of(hist, "SEAL_ATTEMPTED")
    raised = [e for e in events_of(hist, "TENSION_RAISED")
              if e["payload"].get("type") == "structural"]
    tid_s = raised[0]["payload"]["tension_id"] if raised else None
    check("beat 6: A's ordinary Continuity contribution is "
          "accepted (admission reads the authoritative fold); its "
          "seal attempt FAILs S1 on the faulted snapshot and a "
          "checker-origin structural tension is raised, its "
          "origin_ref the failing attempt's event_id",
          out["outcome"] == "accepted"
          and attempts[-1]["payload"]["outcome"] == "fail"
          and attempts[-1]["payload"]["failed_checks"] == [
              {"check": "S1", "affected": [D_CS, STATE]}]
          and len(raised) == 1
          and raised[0]["payload"]["origin"] == "checker"
          and raised[0]["payload"]["origin_ref"]
          == attempts[-1]["event_id"])
    BEATS["fault_attempt"] = attempts[-1]["event_seq"]

    # Repair (I-5): an explicit restart — the service rebuilds its
    # derived state from the verified history. The restart is a
    # recovery step, not the correcting contribution.
    hist_before_restart = hist
    stop_service(proc, exp)
    proc = start_service(exp)
    hist = history_of(exp)
    check("beat 6: the repair restart leaves the history "
          "byte-identical and the structural tension still open "
          "(the restart itself resolves nothing)",
          hist == hist_before_restart
          and verified_fold(hist, CONSTITUTION_HASH)["tensions"]
              [tid_s]["status"] == "open")
    tok_b2 = admin_request(exp, {"op": "issue_token",
                                 "agent_id": B})["result"]["token"]
    for rid in (COMPONENTS, STATE):
        call(exp, "open_region", tok_b2, {"region_id": rid})
    folded = verified_fold(history_of(exp), CONSTITUTION_HASH)
    out = submit(exp, tok_b2, contrib(
        B, new_id(),
        {COMPONENTS: folded["regions"][COMPONENTS]["version"],
         STATE: folded["regions"][STATE]["version"]},
        [COMPONENTS, STATE], [COMPONENTS, STATE],
        [{"kind": "remove_dependency", "dependency_id": D_CS}],
        last_discovery(exp, B)))
    hist = history_of(exp)
    attempts = events_of(hist, "SEAL_ATTEMPTED")
    status = [e for e in events_of(hist, "TENSION_STATUS")
              if e["payload"]["tension_id"] == tid_s]
    check("beat 6: B's correcting contribution (removing the "
          "dangling dependency) is accepted despite the open "
          "tension; its attempt passes and seals; the tension "
          "resolves with that attempt's event_id as its evidence",
          out["outcome"] == "accepted"
          and attempts[-1]["payload"]["outcome"] == "pass"
          and "seal" in attempts[-1]["payload"]
          and len(status) == 1
          and status[0]["payload"]["to"] == "resolved"
          and status[0]["payload"]["evidence"][
              "seal_attempt_event_id"] == attempts[-1]["event_id"]
          and status[0]["payload"]["evidence"]["seal_attempt_seq"]
          == attempts[-1]["event_seq"])
    BEATS["resolved"] = status[0]["event_seq"] if status else None

    # -- Beat 11: close ---------------------------------------------------
    resp = admin_request(exp, {"op": "close_run"})
    hist = history_of(exp)
    closed = hist[-1]
    check("beat 11: RUN_CLOSED ends the history; the final commit "
          "already had its attempt, so close adds no second "
          "attempt; the close records the chain head it anchors",
          resp.get("ok") is True
          and resp["result"]["close_attempt_events"] == 0
          and closed["type"] == "RUN_CLOSED"
          and closed["payload"]["chain_head"] == hist[-2]["hash"])
    BEATS["closed"] = closed["event_seq"]
finally:
    stop_service(proc, exp)

# -- Beat 9/10: seals + starvation over the full history --------------
attempts = events_of(hist, "SEAL_ATTEMPTED")
seals = [a for a in attempts if "seal" in a["payload"]]
check("beat 9: the §7 record across the run — every accepted "
      "commit group attempted; passing attempts sealed with the "
      "structure-only record; the one failing attempt stands on "
      "the record unsealed",
      len(attempts) == 4 and len(seals) == 3
      and all(s["payload"]["seal"]["semantic_clearance"] is False
              for s in seals)
      and all(s["payload"]["seal"]["position"] == s["event_seq"]
              for s in seals),
      f"attempts={len(attempts)} seals={len(seals)}")
folded = verified_fold(hist, CONSTITUTION_HASH)
accounting_final = {rid: folded["facet_status"].get(rid,
                                                    "unexamined")
                    for rid in (COMPONENTS, INTERACTIONS, STATE,
                                CONTINUITY, PRESENTATION, OPERATIONS)}
check("beat 7 (close): the final accounting — Interactions "
      "claimed; State's completion was real at its version and "
      "the correcting contribution's version advance reset it to "
      "unexamined, mechanically, as §5 prescribes",
      accounting_final[INTERACTIONS] == "claimed"
      and accounting_final[STATE] == "unexamined",
      f"accounting={accounting_final}")
report = build_report(hist)
agents = report["agents"]
check("beat 10: the starvation report derives over the full "
      "history for every agent, including zero-commit agent C",
      set(agents) >= {A, B, C}
      and agents[A]["accepted_commits"] == 2
      and agents[B]["accepted_commits"] == 2
      and agents[C]["accepted_commits"] == 0,
      f"accepted={{ {', '.join(k[-1] + ':' + str(v['accepted_commits']) for k, v in sorted(agents.items()))} }}")

# -- Exports: history, anchor, narrative --------------------------------
SUFFIX = sys.argv[1] if len(sys.argv) > 1 else ""
history_path = os.path.join(
    ROOT, f"closing-lifecycle-history{SUFFIX}.json")
with open(history_path, "w", encoding="utf-8") as fh:
    json.dump({"run_id": RUN_ID, "exported_by": "closing_exercise.py",
               "event_count": len(hist), "events": hist},
              fh, indent=2, sort_keys=True)
anchor = {
    "anchor_kind": "content-addressed archival anchor — produced "
                   "by the closing exercise script from the "
                   "service's own exported history; an archival "
                   "record of the run's tail, NOT an independently "
                   "trusted attestation",
    "run_id": RUN_ID,
    "event_count": len(hist),
    "chain_head_at_close": closed["payload"]["chain_head"],
    "closing_event_hash": closed["hash"],
    "history_sha256": sha256_hex(canonical(hist)),
    "genesis_state_hash": genesis_hash,
    "validation_pack": {"id": PACK_ID, "version": PACK_VERSION,
                        "sha256": PACK_SHA256},
    "starvation_report_sha256": sha256_hex(report_bytes(hist)),
}
with open(os.path.join(ROOT, f"closing-anchor{SUFFIX}.json"), "w",
          encoding="utf-8") as fh:
    json.dump(anchor, fh, indent=2, sort_keys=True)


def render_event(ev):
    p = ev["payload"]
    if isinstance(p.get("summary"), str):
        return p["summary"]
    t = ev["type"]
    if t == "RUN_OPENED":
        return ("The run opened, bound to Rev 9 + Amendment A1 and "
                "the pinned examiner pack; the genesis state (six "
                "regions, four dependencies, the constitution) is "
                "carried inside this event.")
    if t == "BOUNDARY_PROBE":
        return ("The pre-run boundary probe's attestation: the "
                "twin's probe evidence stands verified and agent "
                "operations are admitted.")
    if t == "DISCOVERY":
        return (f"{NAMES.get(ev['actor'], 'An agent')} opened "
                f"{NAMES.get(p.get('region_id'), 'a region')} and "
                "the read was recorded.")
    if t == "SEAL_ATTEMPTED":
        if p["outcome"] == "pass":
            return ("A seal attempt passed: the seal certifies the "
                    "structure at this position and grants no "
                    "semantic clearance.")
        return ("A seal attempt FAILED on "
                + ", ".join(f["check"] for f in p["failed_checks"])
                + "; no seal was issued.")
    if t == "RUN_CLOSED":
        return ("The run closed; this event anchors the chain "
                "head it names.")
    return t.replace("_", " ").capitalize() + "."


lines = [f"# Closing lifecycle — {RUN_ID}", "",
         "One Stage 4-bound run, driven mechanically through the "
         "real socket service. Every line below is generated from "
         "the exported event history; the seq is the citation.", ""]
for ev in hist:
    lines.append(f"- seq {ev['event_seq']} · {ev['type']} — "
                 f"{render_event(ev)}")
lines += ["", f"Final facet accounting (derived): "
          + ", ".join(f"{NAMES[r]} = {s}" for r, s in
                      accounting_final.items()) + ".",
          "", "Anchor: " + anchor["anchor_kind"] + ".",
          f"History SHA-256 (canonical events): "
          f"{anchor['history_sha256']}."]
with open(os.path.join(
        ROOT, f"closing-lifecycle-narrative{SUFFIX}.md"),
        "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")

from collections import Counter
shape = Counter(e["type"] for e in hist)
print()
print(f"lifecycle: {len(hist)} events; shape: "
      f"{dict(sorted(shape.items()))}")
print(f"beats: {BEATS}")
if failures:
    print(f"{len(failures)} FAILURES: {failures}")
    sys.exit(1)
print("closing_exercise: all beats passed")
