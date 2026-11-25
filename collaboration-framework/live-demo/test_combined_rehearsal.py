"""Witnesses for the combined configuration (INDEX 476):
the pull enablement's offline rehearsal.

Each run of this suite runs ONE full rehearsal
(combined_rehearsal.run_rehearsal) in a fresh scratch
directory — the real loop, native adapter (with the
NVIDIA route's name translation), doorway and rig,
driven by the scripted stand-in through a stub at the
real NVIDIA connector seam; no provider is contacted —
and asserts the evidence the rehearsal produced:

- the configuration: the sealed record declares the
  exec catalogue contract and holds exactly the
  combined grant set (the live driver's own objects);
  the probe settled 5/5 native; the judgement native,
  bound to the retained receipt;
- the glossary: the issued case carries the glossary
  as its own component, and the wake package captured
  at the seam shows the same glossary standing inside
  the case — present AS the glossary, not merely named
  in the assignment prose;
- the transmitted catalogue: every iteration request
  offers exactly the dashed name set, each tool once —
  container-exec, sandbox-list, sandbox-search,
  sandbox-read_range (underscore preserved),
  sandbox-read, sandbox-write;
- the chain glossary → pull → shelf: the pull of
  sources/stock-take.md cites its glossary entry and
  returns the shelf content itself (content hash ==
  the manifest's hash for that address, authority path
  "source"); the in-room exec read of
  sources/a3-pass.md cites its glossary entry and its
  stdout is the shelf file exactly; the pulled
  content is carried once in the next package — in
  its working set, under the working-set contract
  this configuration declares (the run-3 correction):
  the full content stands in the working-set entry
  with its provenance, and both the tool_results
  entry and the delta's copy carry the stub pointing
  there;
- the dispatches: four, in script order, all stamped
  registry v4; exactly one REJECTION — the
  out-of-grants sandbox.write under sources/;
- the brief: written via sandbox.write, collected
  from the framework sandbox's scratch with the
  scripted brief's hash; the room's scratch holds no
  brief;
- the utilise-only witness (Ben's refinement,
  2026-11-24: "access doesnt mean overwrite. it means
  utlilize"): the scripted exec attempt to overwrite
  the stocked sources/stock-take.md inside the room —
  the source's SHA-256 after the attempt is asserted
  UNCHANGED, and the rehearsal record names the
  mechanism that held. If the room lets the overwrite
  through, this check FAILS and the record carries
  the finding as an open item for the examiner (with
  the mechanism: the whole-tree read-write bind and
  the stocked files' ownership) — the failure is the
  finding, reported plainly, never dressed green;
- the checker over the rehearsal record: eleven
  checks, all ok; the loop's outcome a yield in six
  iterations; the terminal readout rendered; zero
  leftovers (room tree gone, no bwrap standing).

Run: python3 live-demo/test_combined_rehearsal.py
Exits 0 when every check passes — with the single
named exception path above: a failed utilise-only
check exits 1 with the open item printed, which is
the finding's delivery, not a rehearsal defect.
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
from first_worker_run import BOUNDS  # noqa: E402
import combined_rehearsal as rehearsal  # noqa: E402
import demo_run  # noqa: E402

FAILURES = []
CHECKS = [0]
OPEN_ITEMS = []


def check(name, cond, detail=""):
    CHECKS[0] += 1
    print(("PASS  " if cond else "FAIL  ") + name +
          (("  " + detail) if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


def _payload(event):
    p = event["payload"]
    return p if isinstance(p, dict) else json.loads(p)


EXPECTED_MANIFEST = (
    "bd6f3cae7cb5fa1624a78a501566721099a55abe3d35852784"
    "b4ae3a287d904f")
STOCK_TAKE_SHA256 = (
    "ecb919025d4e5176a7128009ad17c4d12c9ff4f1dd41748"
    "b148262308b8cc2e7")
A3_PASS_SHA256 = (
    "d60e5b0fd97baab6bffe4b8c6aee5bdc700ce6035ab26f7"
    "a6d49107659f25bff")
DASHED_SET = {"container-exec", "sandbox-list",
              "sandbox-search", "sandbox-read_range",
              "sandbox-read", "sandbox-write"}
SOURCES_DIR = HERE / "first-worker" / "sandbox" / "sources"


def main():
    work = Path.home() / "workspace" / (
        f".scratch-combined-suite-{os.getpid()}")
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
        check("the loop yields, in six iterations",
              report["loop_result"]["ok"] is True and
              report["loop_result"]["outcome"] == "yield" and
              report["loop_result"]["iterations"] == 6,
              f"{report['loop_result']}")

        # ---------- the configuration
        generated = payloads("ASSEMBLY_GENERATED")[0]
        check("config: the sealed record declares the "
              "exec catalogue contract",
              generated.get("catalogue_contract") == "exec-v4")
        check("config: the sealed grants are exactly the "
              "combined set (the live driver's own)",
              generated.get("grants")
              == demo_run.GRANTS_COMBINED,
              f"{generated.get('grants')}")
        check("config: the report's configuration matches "
              "the sealed record",
              report["configuration"]["sealed_grants"]
              == demo_run.GRANTS_COMBINED and
              report["configuration"]["catalogue_contract"]
              == "exec-v4")
        commissioned = payloads("RUN_COMMISSIONED")[0]
        brief = commissioned["briefs"]["crew-1"]
        check("config: the commissioned brief carries "
              "the scoped bounds and the manifest-bearing "
              "boundary",
              brief.get("loop_bounds") == BOUNDS and
              EXPECTED_MANIFEST in
              brief.get("evidence_boundary", ""))
        check("config: the commissioned brief carries "
              "the glossary as its own field",
              brief.get("glossary") == demo_run.GLOSSARY)
        probed = payloads("ASSEMBLY_PROBED")[0]
        check("config: the probe settled 5/5, "
              "recommending native",
              probed.get("settled_count") == 5 and
              probed.get("recommended_mode") == "native")
        receipt = json.loads(
            (work / "decision-receipt.json").read_text())
        judged = payloads("ASSEMBLY_JUDGED")[0]
        check("config: the judgement is native, bound "
              "to the retained receipt's canonical hash",
              judged.get("adapter_mode") == "native" and
              judged.get("decision_receipt_hash") ==
              hashlib.sha256(canonical(receipt)).hexdigest())
        stocking = json.loads(
            (work / "stocking.json").read_text())
        check("config: the stocked manifest is the "
              "released source-set identity, smoke all-ok",
              stocking["source_manifest"]["manifest_sha256"]
              == EXPECTED_MANIFEST and
              report["manifest_hash"] == EXPECTED_MANIFEST
              and all(s.get("ok")
                      for s in stocking["smoke"]))

        # ---------- the glossary in the case and the
        # wake package
        check("glossary: the issued case carries the "
              "glossary unchanged (report)",
              report["glossary"]["case_glossary"]
              == demo_run.GLOSSARY)
        captures = [json.loads(line) for line in
                    (work / "captures.jsonl")
                    .read_text().splitlines() if line.strip()]
        chat = {c["index"]: c for c in captures
                if c["mode"] == "chat"}
        raw = [c for c in captures
               if c["mode"] == "chat-raw-bounded"]
        check("captures: seven chat captures (identify + "
              "six iterations) and five raw probe captures",
              sorted(chat) == list(range(7)) and
              len(raw) == 5)
        bodies = {}
        for idx, cap in chat.items():
            body = base64.b64decode(cap["request_b64"])
            bodies[idx] = body
            check(f"captures: capture {idx} hashes to "
                  f"its own bytes",
                  hashlib.sha256(body).hexdigest() ==
                  cap["request_sha256"] and
                  len(body) == cap["request_bytes"])

        def package_of(idx):
            req = json.loads(bodies[idx])
            decoder = json.JSONDecoder()
            for message in req.get("messages") or []:
                content = message.get("content")
                if not isinstance(content, str):
                    continue
                for start in range(len(content)):
                    if content[start] != "{":
                        continue
                    try:
                        parsed, _end = decoder.raw_decode(
                            content[start:])
                    except ValueError:
                        continue
                    if isinstance(parsed, dict) and \
                            "case" in parsed and \
                            "tool_results" in parsed:
                        return parsed
            return None

        wake = package_of(1)
        check("glossary: the wake package's case carries "
              "the glossary as a distinct component, "
              "unchanged",
              wake is not None and
              (wake.get("case") or {}).get("glossary")
              == demo_run.GLOSSARY,
              f"{(wake or {}).get('case')}")
        check("glossary: the report's package glossary "
              "matches the captured wake package",
              report["glossary"]["package_glossary"]
              == demo_run.GLOSSARY)

        # ---------- the transmitted catalogue
        for idx in range(1, 7):
            req = json.loads(bodies[idx])
            names = [t.get("function", {}).get("name")
                     for t in req.get("tools") or []]
            check(f"catalogue: iteration {idx} offers "
                  f"exactly the dashed set, each once",
                  sorted(names) == sorted(DASHED_SET) and
                  len(names) == len(set(names)),
                  f"{names}")
            check(f"catalogue: iteration {idx} is "
                  f"addressed to the rehearsal model",
                  req.get("model") == demo_run.MODEL)

        # ---------- the dispatches and the refusal
        dispatched = payloads("TOOL_DISPATCHED")
        check("dispatches: four, in script order, all "
              "stamped registry v4",
              [d.get("tool") for d in dispatched] == [
                  "sandbox.read", "container.exec",
                  "container.exec", "sandbox.write"] and
              all(d.get("registry_version") ==
                  tool_policy.EXEC_REGISTRY_VERSION
                  for d in dispatched),
              f"{[(d.get('tool'), d.get('registry_version')) for d in dispatched]}")
        rejections = [p for p in payloads("REJECTION")
                      if p.get("attempted_type")
                      == "TOOL_DISPATCHED"]
        check("refusal: exactly one doorway REJECTION — "
              "the out-of-grants write under sources/",
              len(rejections) == 1 and
              rejections[0].get("tool") == "sandbox.write",
              f"{rejections}")
        check("refusal: the report records the same "
              "single rejection with its ground",
              len(report["rejections"]) == 1 and
              report["rejections"][0]["tool"]
              == "sandbox.write" and
              bool(report["rejections"][0]["ground"]))

        # ---------- the chain: glossary → pull → shelf
        outcomes = {p.get("dispatch_id"): p
                    for p in payloads("TOOL_OUTCOME")}
        read_dispatch = dispatched[0]
        read_result = (outcomes.get(
            read_dispatch.get("dispatch_id")) or {}).get(
            "result") or {}
        shelf_stock_take = (
            SOURCES_DIR / "stock-take.md").read_bytes()
        check("chain: the pull returns the shelf "
              "content itself (hash == the manifest's, "
              "authority path source)",
              read_result.get("content_sha256")
              == STOCK_TAKE_SHA256 and
              read_result.get("authority_path")
              == "source" and
              read_result.get("content")
              == shelf_stock_take.decode("utf-8"),
              f"{ {k: read_result.get(k) for k in ('content_sha256', 'authority_path')} }")
        pull0 = report["pulls"][0]
        check("chain: the pull evidence cites the "
              "glossary entry it answers to",
              pull0["tool"] == "sandbox.read" and
              pull0["path"] == "sources/stock-take.md" and
              (pull0["glossary_entry"] or {}).get(
                  "address") == "sources/stock-take.md" and
              pull0["content_sha256"]
              == pull0["shelf_sha256"]
              == STOCK_TAKE_SHA256,
              f"{pull0}")
        exec_dispatch = dispatched[1]
        exec_result = (outcomes.get(
            exec_dispatch.get("dispatch_id")) or {}).get(
            "result") or {}
        shelf_a3 = (SOURCES_DIR / "a3-pass.md").read_bytes()
        check("chain: the in-room exec read returns the "
              "shelf file exactly",
              exec_result.get("exit_status") == 0 and
              exec_result.get("stdout")
              == shelf_a3.decode("utf-8"))
        pull1 = report["pulls"][1]
        check("chain: the exec read cites the same "
              "glossary entry's address through the "
              "other door",
              pull1["door"] == "room (exec)" and
              pull1["path"] == "sources/a3-pass.md" and
              (pull1["glossary_entry"] or {}).get(
                  "address") == "sources/a3-pass.md" and
              pull1["stdout_sha256"]
              == pull1["shelf_sha256"] == A3_PASS_SHA256,
              f"{pull1}")
        second_package = package_of(2)
        carried = [e for e in
                   (second_package or {}).get(
                       "tool_results") or []
                   if e.get("dispatch_id")
                   == read_dispatch.get("dispatch_id")]
        delta_outcomes = [
            e for e in (second_package or {}).get(
                "delta") or []
            if e.get("type") == "TOOL_OUTCOME"
            and (e.get("payload") or {}).get(
                "dispatch_id")
            == read_dispatch.get("dispatch_id")]
        delta_result = ((delta_outcomes[0].get(
            "payload") or {}).get("result")
            if delta_outcomes else None) or {}
        ws_entries = [
            e for e in ((second_package or {}).get(
                "working_set") or {}).get("entries") or []
            if e.get("dispatch_id")
            == read_dispatch.get("dispatch_id")]
        check("chain: the pulled content is carried "
              "once in the next package — in its "
              "working set (full content with its "
              "provenance: the manifest hash, the "
              "source authority path, the whole-file "
              "served descriptor, the gathering "
              "dispatch's identity); the tool_results "
              "entry and the delta's copy both carry "
              "the stub pointing at the working set",
              len(ws_entries) == 1 and
              ws_entries[0].get("content")
              == shelf_stock_take.decode("utf-8") and
              ws_entries[0].get("content_carried")
              is True and
              ws_entries[0].get("content_sha256")
              == STOCK_TAKE_SHA256 and
              ws_entries[0].get("authority_path")
              == "source" and
              (ws_entries[0].get("served") or {}).get(
                  "kind") == "whole" and
              len(carried) == 1 and
              (carried[0].get("result") or {}).get(
                  "presented_in") == "working_set" and
              "content" not in (
                  carried[0].get("result") or {}) and
              delta_result.get("single_carriage") is True
              and delta_result.get("presented_in")
              == "working_set"
              and "content" not in delta_result,
              f"ws={len(ws_entries)} "
              f"carried={len(carried)} "
              f"delta={delta_result}")

        # ---------- the brief via sandbox.write
        check("brief: written via sandbox.write and "
              "collected from the framework scratch "
              "with the scripted hash; the room's "
              "scratch holds none",
              report["brief"]["path_used"]
              == "framework_scratch" and
              report["brief"]["framework_scratch_sha256"]
              == report["brief"]["expected_sha256"] and
              report["brief"]["room_sha256"] is None)
        collected = (work / "brief.md").read_bytes()
        check("brief: the collected file is the "
              "scripted brief",
              hashlib.sha256(collected).hexdigest()
              == report["brief"]["expected_sha256"])

        # ---------- the utilise-only witness
        ow = report["overwrite_attempt"]
        check("utilise-only: the attempt was dispatched "
              "and executed in the room (a result, not "
              "a refusal)",
              ow["dispatch_outcome"] == "result" and
              ow["source_sha256_before"]
              == STOCK_TAKE_SHA256,
              f"{ow}")
        check("utilise-only: the sandbox's staged copy "
              "was never the attempt's target and stands "
              "unchanged",
              ow["source_sha256_after_in_sandbox"]
              == STOCK_TAKE_SHA256)
        if ow["held"]:
            check("utilise-only: the stocked source's "
                  "SHA-256 is UNCHANGED after the "
                  "overwrite attempt, and the record "
                  "names the mechanism that held",
                  ow["source_sha256_after_in_room"]
                  == STOCK_TAKE_SHA256 and
                  bool(ow["mechanism"]) and
                  ow["open_item"] is None)
        else:
            OPEN_ITEMS.append(ow["open_item"])
            check("utilise-only: the stocked source's "
                  "SHA-256 is UNCHANGED after the "
                  "overwrite attempt",
                  False,
                  f"after={ow['source_sha256_after_in_room']} "
                  f"mechanism={ow['mechanism']}")
            check("utilise-only: the record carries "
                  "the finding as an open item, with "
                  "the mechanism named",
                  bool(ow["open_item"]) and
                  bool(ow["mechanism"]) and
                  ow["source_sha256_after_in_room"]
                  != STOCK_TAKE_SHA256)

        # ---------- the checker and the readout
        checks = report["checker"] or {}
        check("checker: eleven checks over the "
              "rehearsal record, all ok",
              len(checks) == 11 and
              all(isinstance(v, dict)
                  and v.get("result") == "ok"
                  for v in checks.values()),
              f"{checks}")
        check("readout: the terminal readout rendered",
              report["terminal_readout"]["rendered"]
              is True)

        # ---------- zero leftovers
        tree = work / "rooms" / "demo-tree"
        check("leftovers: the room tree is gone",
              not tree.exists())
        bwrap = subprocess.run(
            ["pgrep", "-x", "bwrap"],
            capture_output=True, text=True)
        check("leftovers: no bwrap process standing",
              bwrap.returncode != 0,
              bwrap.stdout[:120])
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"\n{CHECKS[0] - len(FAILURES)}/{CHECKS[0]} "
          f"checks passed")
    for item in OPEN_ITEMS:
        print(f"OPEN ITEM: {item}")
    if FAILURES:
        print("FAILURES:", "; ".join(FAILURES))
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
