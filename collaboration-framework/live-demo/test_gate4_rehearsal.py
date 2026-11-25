"""Witnesses for gate 4: the doorway connection and its
offline rehearsal (DEMONSTRATION-PREPARATION-2026-11-24.md
§2.4's ten-hop table, exercised offline).

Each run of this suite runs ONE full rehearsal
(gate4_rehearsal.run_rehearsal) in a fresh scratch directory
— the real loop, native adapter, doorway and rig, driven by
the scripted stand-in through a stub at the real NVIDIA
connector seam; no provider is contacted — and asserts, hop
by hop, the evidence the rehearsal produced:

- hop 1: the assembly record — the exec catalogue contract
  declared, the sealed grants exactly the execution tool
  only, the case's bounds and manifest-bearing boundary,
  the probe settled 5/5 native, the judgement native and
  bound to the retained decision receipt's canonical hash,
  the pack sealing native;
- hop 2: the stocking record — the released source-set
  identity, every smoke check ok, the deliverable absent
  at stocking's end, two smoke executions standing in the
  room state before any worker execution;
- hop 3: the transmitted requests, captured at the seam —
  every loop-iteration request carries exactly one offered
  tool definition, container.exec, with the registry's own
  description; the captures hash to their own bytes;
- hop 4: a captured response-evidence disposition for
  every iteration, each cross-checked against its filed
  artifact;
- hop 5: a translation record per call-bearing iteration,
  bound to its disposition's artifact hash; the ungranted
  name refused as unknown_tool; the malformed shape
  resolved valid at translation (its refusal is the
  doorway's, hop 6);
- hop 6: five dispatches, all stamped registry v4; exactly
  one REJECTION, its ground the doorway's cmd-shape check;
- hop 7: the room's executions reconcile 1:1 with the five
  dispatches by command array, after the two smoke
  executions; exactly one rig-integrity event, the
  tampered execution refused with failed_precondition
  rig-integrity;
- hop 8: the next outbound request's captured bytes carry
  the previous result — iteration 2's request holds
  dispatch-1's provider call ID, its exit status and the
  stock-take's own text; iteration 8's holds the final
  execution's in-room hash output;
- hop 9: the deliverable's hash at the wall equals the
  scripted brief's hash;
- hop 10: the independent checker's eleven checks all ok,
  and the loop's own outcome a yield in eight iterations.

And the result contract end to end: every exec outcome's
result carries exactly the paper §2.3's ten fields, with
the tampered execution's precondition refusal standing as
a "result" outcome — exit_status null, termination naming
the precondition — not a failure, not a crash. And the
terminal readout: the rehearsal's export renders through
live-demo/terminal_readout.py without error and shows the
five exec dispatches. And zero leftovers: the room tree
gone, no mount for it in the live mount table, no bwrap
process standing.

Run: python3 live-demo/test_gate4_rehearsal.py
Exits 0 when every check passes.
"""

import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "room" / "rig"))

from fabric.canonical import canonical  # noqa: E402

from framework import tool_policy  # noqa: E402
from first_worker_run import (  # noqa: E402
    BOUNDS, _filed_artifact_check)
import gate4_rehearsal as rehearsal  # noqa: E402

FAILURES = []
CHECKS = [0]


def check(name, cond, detail=""):
    CHECKS[0] += 1
    print(("PASS  " if cond else "FAIL  ") + name +
          (("  " + detail) if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


def _payload(event):
    p = event["payload"]
    return p if isinstance(p, dict) else json.loads(p)


CONTRACT_FIELDS = {
    "exit_status", "stdout", "stdout_bytes_total",
    "stdout_truncated", "stderr", "stderr_bytes_total",
    "stderr_truncated", "termination", "cpu_seconds_charged",
    "duration_seconds"}

EXPECTED_MANIFEST = (
    "bd6f3cae7cb5fa1624a78a501566721099a55abe3d35852784"
    "b4ae3a287d904f")
INDEX_TAIL_SHA256 = (
    "eb16b56bb16c53dfb7b5420b2a2c446e8cbc40cf4787e460b8"
    "de9773145d05ed")


def main():
    work = Path.home() / "workspace" / (
        f".scratch-gate4-suite-{os.getpid()}")
    if work.exists():
        shutil.rmtree(work)
    try:
        report = rehearsal.run_rehearsal(work)
        run_dir = work / "run"
        export = json.loads(
            (run_dir / "run-export.json").read_text())
        events = export["events"]
        by_type = {}
        for e in events:
            by_type.setdefault(e["type"], []).append(e)

        def payloads(type_):
            return [_payload(e) for e in by_type.get(type_, [])]

        # ---------- the run's own outcome
        check("the loop yields, in eight iterations",
              report["loop_result"]["ok"] is True and
              report["loop_result"]["outcome"] == "yield" and
              report["loop_result"]["iterations"] == 8,
              f"{report['loop_result']}")

        # ---------- hop 1: assembly judged and issued
        generated = payloads("ASSEMBLY_GENERATED")[0]
        check("hop 1: the sealed record declares the exec "
              "catalogue contract",
              generated.get("catalogue_contract") == "exec-v4")
        check("hop 1: the sealed grants are the execution "
              "tool only",
              generated.get("grants") == rehearsal.GRANTS_EXEC)
        commissioned = payloads("RUN_COMMISSIONED")[0]
        brief = commissioned["briefs"]["crew-1"]
        check("hop 1: the case carries the scoped bounds",
              brief.get("loop_bounds") == BOUNDS)
        check("hop 1: the case boundary names the released "
              "manifest hash",
              EXPECTED_MANIFEST in
              brief.get("evidence_boundary", ""))
        probed = payloads("ASSEMBLY_PROBED")[0]
        check("hop 1: the probe settled 5/5, recommending "
              "native",
              probed.get("settled_count") == 5 and
              probed.get("recommended_mode") == "native")
        receipt = json.loads(
            (work / "decision-receipt.json").read_text())
        judged = payloads("ASSEMBLY_JUDGED")[0]
        check("hop 1: the judgement is native, bound to the "
              "retained receipt's canonical hash",
              judged.get("adapter_mode") == "native" and
              judged.get("decision_receipt_hash") ==
              hashlib.sha256(canonical(receipt)).hexdigest())
        packed = payloads("ASSEMBLY_PACKED")[0]
        check("hop 1: the pack seals the native mode",
              packed.get("adapter_mode") == "native")

        # ---------- hop 2: stocking
        stocking = json.loads(
            (work / "stocking.json").read_text())
        check("hop 2: the room stands stocked",
              stocking.get("stocked") is True)
        check("hop 2: the stocked manifest is the released "
              "source-set identity",
              stocking["source_manifest"]["manifest_sha256"]
              == EXPECTED_MANIFEST and
              report["manifest_hash"] == EXPECTED_MANIFEST)
        check("hop 2: every smoke check passed",
              all(s.get("ok") for s in stocking["smoke"]),
              f"{[s for s in stocking['smoke'] if not s['ok']]}")
        check("hop 2: no deliverable stands at stocking's "
              "end",
              stocking["deliverable"]
              ["present_at_stocking_end"] is False)
        check("hop 2: two smoke executions stand recorded "
              "at stocking",
              stocking["room_state_executions_at_stocking"]
              == 2)

        # ---------- hop 3: the transmitted requests
        captures = [json.loads(line) for line in
                    (work / "captures.jsonl")
                    .read_text().splitlines() if line.strip()]
        chat = {c["index"]: c for c in captures
                if c["mode"] == "chat"}
        raw = [c for c in captures
               if c["mode"] == "chat-raw-bounded"]
        check("hop 3: nine chat captures (identify + eight "
              "iterations) and five raw probe captures",
              sorted(chat) == list(range(9)) and len(raw) == 5)
        bodies = {}
        for idx, cap in chat.items():
            body = base64.b64decode(cap["request_b64"])
            bodies[idx] = body
            check(f"hop 3: capture {idx} hashes to its own "
                  f"bytes",
                  hashlib.sha256(body).hexdigest() ==
                  cap["request_sha256"] and
                  len(body) == cap["request_bytes"])
        facing = tool_policy.worker_facing(
            "container.exec",
            version=tool_policy.EXEC_REGISTRY_VERSION)
        for idx in range(1, 9):
            req = json.loads(bodies[idx])
            tools = req.get("tools") or []
            ok = len(tools) == 1 and \
                tools[0].get("function", {}).get("name") == \
                "container.exec" and \
                tools[0]["function"].get("description") == \
                facing["description"] and \
                tools[0]["function"].get("parameters") == \
                {"type": "object", "properties": {}} and \
                req.get("model") == rehearsal.MODEL
            check(f"hop 3: iteration {idx}'s transmitted "
                  f"request offers exactly container.exec, "
                  f"with the registry's description", ok)

        # ---------- hop 4: response evidence
        dispositions = payloads("RESPONSE_EVIDENCE")
        check("hop 4: a captured disposition for every "
              "iteration",
              len(dispositions) == 8 and all(
                  d.get("outcome") == "captured"
                  for d in dispositions))
        disp_by_seq = {d["iteration_seq"]: d
                       for d in dispositions}
        for d in dispositions:
            check(f"hop 4: iteration_seq "
                  f"{d['iteration_seq']}'s filed artifact "
                  f"cross-checks ok",
                  _filed_artifact_check(
                      str(run_dir), d["iteration_seq"], d)
                  == "ok")

        # ---------- hop 5: translation
        translations = payloads("TRANSLATION_RECORDED")
        check("hop 5: a translation record for each of the "
              "seven call-bearing iterations",
              len(translations) == 7)
        for t in translations:
            check(f"hop 5: iteration {t['iteration']}'s "
                  f"translation is bound to its artifact, "
                  f"under registry v4",
                  t.get("artifact_sha256") ==
                  disp_by_seq[t["iteration_seq"]]
                  .get("artifact_sha256") and
                  t.get("registry_version") ==
                  "tool-registry-v4")
        calls = {t["iteration"]: t["calls"][0]
                 for t in translations}
        check("hop 5: the ungranted name is refused at "
              "translation as unknown_tool",
              calls[4].get("name") == "sandbox.read" and
              calls[4].get("resolution") == "unknown" and
              calls[4].get("refusal_class") == "unknown_tool")
        check("hop 5: the malformed shape resolves valid "
              "at translation (its refusal is the doorway's)",
              calls[5].get("name") == "container.exec" and
              calls[5].get("resolution") == "resolved" and
              calls[5].get("validation") == "valid")

        # ---------- hop 6: the dispatch decision
        dispatches = payloads("TOOL_DISPATCHED")
        check("hop 6: five dispatches, all container.exec, "
              "all stamped registry v4",
              len(dispatches) == 5 and all(
                  d.get("tool") == "container.exec" and
                  d.get("registry_version") ==
                  "tool-registry-v4" for d in dispatches))
        rejections = payloads("REJECTION")
        check("hop 6: exactly one rejection — the doorway's "
              "cmd-shape refusal of the malformed call",
              len(rejections) == 1 and
              "container.exec requires its cmd" in
              rejections[0].get("ground", ""),
              f"{rejections}")
        check("hop 6: six tool requests stand (the refused "
              "translation produced none)",
              len(payloads("TOOL_REQUESTED")) == 6)

        # ---------- the result contract, end to end
        outcomes = {o["dispatch_id"]: o
                    for o in payloads("TOOL_OUTCOME")}
        results = {}
        for d in dispatches:
            o = outcomes[d["dispatch_id"]]
            results[d["dispatch_id"]] = o
            r = o.get("result") or {}
            check(f"contract: {d['dispatch_id']}'s result "
                  f"carries exactly the §2.3 fields",
                  set(r.keys()) == CONTRACT_FIELDS,
                  f"{sorted(r.keys())}")
            check(f"contract: {d['dispatch_id']}'s result "
                  f"field types stand",
                  (r.get("exit_status") is None or
                   isinstance(r.get("exit_status"), int)) and
                  isinstance(r.get("stdout"), str) and
                  isinstance(r.get("stderr"), str) and
                  isinstance(r.get("stdout_bytes_total"), int)
                  and isinstance(
                      r.get("stderr_bytes_total"), int) and
                  isinstance(r.get("stdout_truncated"), bool)
                  and isinstance(
                      r.get("stderr_truncated"), bool) and
                  isinstance(r.get("termination"), str) and
                  isinstance(r.get("cpu_seconds_charged"),
                             (int, float)) and
                  isinstance(r.get("duration_seconds"),
                             (int, float)))
        first = results["dispatch-1"]["result"]
        check("contract: the source read completes, exit 0, "
              "untruncated, totals equal to the carried bytes",
              first["termination"] == "completed" and
              first["exit_status"] == 0 and
              first["stdout_truncated"] is False and
              first["stdout_bytes_total"] ==
              len(first["stdout"].encode("utf-8")))
        tampered = results["dispatch-4"]
        tr = tampered["result"]
        check("contract: the tampered execution returns as "
              "a result — precondition-failed naming "
              "rig-integrity, exit null, no output",
              tampered["outcome"] == "result" and
              tr["termination"] ==
              "precondition-failed: rig-integrity" and
              tr["exit_status"] is None and
              tr["stdout"] == "" and
              tr["stdout_bytes_total"] == 0)
        last = results["dispatch-5"]["result"]
        check("contract: the restored execution completes "
              "with the third source's in-room hash as its "
              "output",
              last["termination"] == "completed" and
              last["exit_status"] == 0 and
              INDEX_TAIL_SHA256 in last["stdout"])

        # ---------- hop 7: the room execution
        room_state = json.loads(
            (work / "room-state.json").read_text())
        executions = room_state["executions"]
        requested = [p["parameters"]["cmd"] for p in
                     payloads("TOOL_REQUESTED")
                     if p["tool"] == "container.exec" and
                     isinstance(p["parameters"].get("cmd"),
                                list)]
        worker_execs = executions[2:]
        check("hop 7: seven room executions stand — two "
              "smoke, then the five worker executions — and "
              "five exec requests were dispatched",
              len(executions) == 7 and
              len(worker_execs) == 5 and
              len(requested) == 5,
              f"execs={[e['argv'] for e in worker_execs]} "
              f"requested={requested}")
        check("hop 7: the room's executions reconcile 1:1 "
              "with the five dispatches, by command array, "
              "in order",
              [e["argv"] for e in worker_execs] == requested)
        check("hop 7: exactly one rig-integrity event; the "
              "tampered execution refused on that "
              "precondition, never ran",
              len(room_state.get("rig_integrity_events",
                                 [])) == 1 and
              worker_execs[3]["refused"] is True and
              worker_execs[3]["failed_precondition"] ==
              "rig-integrity" and
              worker_execs[3]["rc"] is None)

        # ---------- hop 8: the carriage back
        # The captured bodies are JSON: their message text
        # is read parsed (a non-ASCII character in the
        # carried output travels escaped in the raw bytes),
        # while the call IDs and field names stand in the
        # raw bytes themselves.
        def carried_text(idx):
            req = json.loads(bodies[idx])
            return "\n".join(
                str(m.get("content") or "")
                for m in req.get("messages") or [])
        iter2_raw = bodies[2].decode("utf-8", "replace")
        iter2 = carried_text(2)
        # The package renders its record as JSON text, so
        # the carried output's non-ASCII characters stand
        # escaped there; the escaped form of the source's
        # first line is the exact string to look for.
        escaped_line0 = json.dumps(
            first["stdout"].splitlines()[0])[1:-1]
        tr_at = iter2.find('"tool_results"')
        tr_section = iter2[tr_at:tr_at + 20000] \
            if tr_at >= 0 else ""
        check("hop 8: iteration 2's transmitted request "
              "carries dispatch-1's result in its "
              "tool_results carriage — the result's exit "
              "status and the stock-take's own text — with "
              "the call's provider ID standing in the same "
              "request",
              "fc-g4-1" in iter2_raw and
              tr_at >= 0 and
              '"exit_status": 0' in tr_section and
              escaped_line0 in tr_section)
        iter8_raw = bodies[8].decode("utf-8", "replace")
        check("hop 8: iteration 8's transmitted request "
              "carries the final execution's result — its "
              "call ID and the in-room hash output",
              "fc-g4-7" in iter8_raw and
              INDEX_TAIL_SHA256 in carried_text(8))

        # ---------- hop 9: the deliverable at the wall
        check("hop 9: the deliverable's hash at the wall "
              "is the scripted brief's hash",
              report["brief_sha256"] ==
              report["brief_expected_sha256"] ==
              hashlib.sha256(rehearsal.BRIEF_TEXT
                             .encode("utf-8")).hexdigest())

        # ---------- hop 10: reconstruction
        checks = report["checker"] or {}
        check("hop 10: the independent checker's eleven "
              "checks all ok",
              len(checks) == 11 and all(
                  v.get("result") == "ok"
                  for v in checks.values()),
              f"{checks}")

        # ---------- the terminal readout
        readout = (work / "terminal-readout.md").read_text()
        check("readout: the rehearsal's readout stands, "
              "showing the five exec dispatches",
              report["terminal_readout"]["rendered"] is True
              and readout.count(
                  "dispatched · container.exec") == 5 and
              "fc-g4-1" in readout)
        again = subprocess.run(
            [sys.executable,
             str(HERE / "terminal_readout.py"), "render",
             str(run_dir / "run-export.json"), "-o",
             str(work / "readout-again.md")],
            capture_output=True, text=True)
        check("readout: the export renders through "
              "terminal_readout.py without error",
              again.returncode == 0,
              again.stderr[-300:])

        # ---------- zero leftovers
        tree = Path(stocking["tree"])
        mounts = Path("/proc/mounts").read_text()
        check("leftovers: the room tree is gone and no "
              "mount for it stands",
              not tree.exists() and str(tree) not in mounts)
        bwrap = subprocess.run(["pgrep", "-x", "bwrap"],
                               capture_output=True, text=True)
        check("leftovers: no bwrap process stands",
              bwrap.returncode != 0 and
              not bwrap.stdout.strip(),
              bwrap.stdout)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"\n{CHECKS[0] - len(FAILURES)}/{CHECKS[0]} checks "
          f"passed")
    if FAILURES:
        print("FAILURES:", *FAILURES, sep="\n  ")
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
