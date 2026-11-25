"""Witnesses for working-set carriage (the run-3
correction, examiner's ruling 2026-11-24).

Each run of this suite runs ONE full rehearsal
(working_set_rehearsal.run_rehearsal) in a fresh scratch
directory — the real loop, native adapter (with the
NVIDIA route's name translation), doorway and executor,
driven by a scripted stand-in through a stub at the real
NVIDIA connector seam; no provider is contacted — and
asserts the evidence against the examiner's narrow
examination list:

  (a) a source read in one iteration is still present,
      with its actual content, at the next wake;
  (b) a second source read, both remain available
      together;
  (c) a repeated read creates no duplicate working-set
      entries (the entry keeps the first gathering
      dispatch's identity);
  (d) provenance and hashes verified against the
      recorded outcomes (path, authority path, content
      hash, served range, dispatch identity, outcome
      position);
  (e) the aggregate ceiling exercised with a synthetic
      oversized gather: the entry that does not fit
      stands by its provenance alone, marked not
      carried with the reason — no silent truncation —
      and a later smaller entry that fits is carried;
  (f) the checker reconstructs the exact working set
      presented at each iteration: every LOOP_ITERATION
      carries the working-set commitment, the commitment
      equals the hash of the very package the captures
      show was presented, and the checker's eleven
      checks stand all-ok over both scenario records.

Also asserted: the range read stands in the set as the
range actually retrieved (lines 1–4 of the index tail),
never expanded into the whole file; no gathered content
appears anywhere in a package except in its working-set
entry (the tool_results entries and the delta's copies
carry the provenance stub pointing at the working set);
the packages carry the budget and the note telling the
worker that not-carried material stands in the record
and may be re-pulled with its retrieval tools; zero
leftovers (no bwrap standing; the scratch tree removed).

Run: python3 live-demo/test_working_set_rehearsal.py
Exits 0 when every check passes.
"""

import base64
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "room" / "rig"))

from fabric.canonical import canonical, sha256_hex  # noqa: E402

from framework import tool_policy  # noqa: E402
import working_set_rehearsal as rehearsal  # noqa: E402

FAILURES = []
CHECKS = [0]

BUDGET = tool_policy.WORKING_SET_CONTENT_BUDGET
STOCK_TAKE_SHA256 = (
    "ecb919025d4e5176a7128009ad17c4d12c9ff4f1dd41748"
    "b148262308b8cc2e7")
A3_PASS_SHA256 = (
    "d60e5b0fd97baab6bffe4b8c6aee5bdc700ce6035ab26f7"
    "a6d49107659f25bff")
INDEX_TAIL_SHA256 = (
    "eb16b56bb16c53dfb7b5420b2a2c446e8cbc40cf4787e4"
    "60b8de9773145d05ed")


def check(name, cond, detail=""):
    CHECKS[0] += 1
    print(("PASS  " if cond else "FAIL  ") + name +
          (("  " + detail) if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


def _payload(event):
    p = event["payload"]
    return p if isinstance(p, dict) else json.loads(p)


def _first_lines(data, n):
    """The first n lines of `data`, each as it stands
    (bytes up to and including its newline)."""
    out = []
    start = 0
    while len(out) < n and start < len(data):
        nl = data.find(b"\n", start)
        if nl == -1:
            out.append(data[start:])
            break
        out.append(data[start:nl + 1])
        start = nl + 1
    return b"".join(out)


def _packages(work):
    """The wake packages a scenario's captures carried,
    by chat index (0 is the identify call; iteration k's
    package stands at index k)."""
    captures = [json.loads(line) for line in
                (work / "captures.jsonl")
                .read_text().splitlines() if line.strip()]
    chat = {c["index"]: c for c in captures
            if c["mode"] == "chat"}
    packages = {}
    decoder = json.JSONDecoder()
    for idx, cap in sorted(chat.items()):
        body = json.loads(base64.b64decode(
            cap["request_b64"]))
        for message in body.get("messages") or []:
            content = message.get("content")
            if not isinstance(content, str):
                continue
            found = None
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
                    found = parsed
                    break
            if found is not None:
                packages[idx] = found
                break
    return packages


def _events(work):
    export = json.loads(
        (work / "run" / "run-export.json").read_text())
    return export["events"]


def _ws_hash_of(package):
    ws = package.get("working_set") or {}
    return sha256_hex(canonical({
        "budget_bytes": ws.get("budget_bytes"),
        "entries": ws.get("entries")}))


def _check_commitments(scenario, work, packages,
                       iterations):
    """(f) at the package level: every recorded
    iteration carries the working-set commitment, and
    the commitment equals the hash of the exact working
    set the captured package at that iteration
    presented."""
    evs = _events(work)
    recorded = {}
    for e in evs:
        if e["type"] == "LOOP_ITERATION":
            p = _payload(e)
            recorded[p.get("iteration")] = \
                p.get("working_set_hash")
    check(f"{scenario}: every LOOP_ITERATION carries "
          f"the working-set commitment",
          len(recorded) == iterations and
          all(isinstance(h, str) and len(h) == 64
              for h in recorded.values()),
          f"{recorded}")
    for k in range(1, iterations + 1):
        pkg = packages.get(k) or {}
        check(f"{scenario}: iteration {k}'s commitment "
              f"is the hash of the working set its "
              f"captured package presented",
              recorded.get(k) is not None and
              recorded.get(k) == _ws_hash_of(pkg),
              f"recorded={recorded.get(k)} "
              f"package={_ws_hash_of(pkg)}")


def _check_checker(scenario, report):
    checks = report["checker"] or {}
    check(f"{scenario}: the checker stands eleven "
          f"checks over the record, all ok (its "
          f"reconstruction of every presented working "
          f"set included)",
          len(checks) == 11 and
          all(isinstance(v, dict)
              and v.get("result") == "ok"
              for v in checks.values()),
          f"{checks}")
    check(f"{scenario}: the terminal readout rendered",
          report["terminal_readout"]["rendered"] is True)


def main():
    work = Path(tempfile.mkdtemp(
        prefix="working-set-rehearsal-"))
    try:
        reports = rehearsal.run_rehearsal(work)

        # ================= continuity =================
        rep = reports["continuity"]
        cwork = work / "continuity"
        check("continuity: the run yields in five "
              "iterations",
              rep["outcome"] == "yield"
              and rep["iterations"] == 5,
              f"{rep['outcome']} / {rep['iterations']}")
        check("continuity: the sealed record declares "
              "the working-set contract",
              rep["sealed_working_set_contract"]
              == tool_policy.WORKING_SET_CONTRACT,
              f"{rep['sealed_working_set_contract']}")
        packages = _packages(cwork)
        check("continuity: six chat captures (identify "
              "+ five iterations), each with a package",
              sorted(packages) == [0, 1, 2, 3, 4, 5]
              or sorted(packages) == [1, 2, 3, 4, 5],
              f"{sorted(packages)}")
        evs = _events(cwork)
        dispatched = [_payload(e) for e in evs
                      if e["type"] == "TOOL_DISPATCHED"]
        outcomes = {}
        outcome_seqs = {}
        for e in evs:
            if e["type"] == "TOOL_OUTCOME":
                p = _payload(e)
                outcomes[p.get("dispatch_id")] = \
                    p.get("result") or {}
                outcome_seqs[p.get("dispatch_id")] = \
                    e["event_seq"]
        check("continuity: four dispatches in script "
              "order (read, read, read again, read_range)",
              [d.get("tool") for d in dispatched] == [
                  "sandbox.read", "sandbox.read",
                  "sandbox.read", "sandbox.read_range"],
              f"{[d.get('tool') for d in dispatched]}")
        first_read = dispatched[0]
        stock_take = (cwork / "run" / "sandbox"
                      / "sources"
                      / "stock-take.md").read_bytes()
        a3_pass = (cwork / "run" / "sandbox" / "sources"
                   / "a3-pass.md").read_bytes()
        index_tail = (cwork / "run" / "sandbox"
                      / "sources"
                      / "index-tail.md").read_bytes()
        check("continuity: the staged sources hash to "
              "the manifest's entries",
              hashlib.sha256(stock_take).hexdigest()
              == STOCK_TAKE_SHA256
              and hashlib.sha256(a3_pass).hexdigest()
              == A3_PASS_SHA256
              and hashlib.sha256(index_tail).hexdigest()
              == INDEX_TAIL_SHA256)

        # (a) the first read survives to the next wake.
        ws2 = (packages[2].get("working_set") or {})
        entries2 = ws2.get("entries") or []
        check("(a) the wake after the first read "
              "presents a working set holding exactly "
              "that read — full content, provenance "
              "together: the manifest hash, the source "
              "authority path, the whole-file served "
              "descriptor, the gathering dispatch's "
              "identity",
              len(entries2) == 1
              and entries2[0].get("path")
              == "sources/stock-take.md"
              and entries2[0].get("content")
              == stock_take.decode("utf-8")
              and entries2[0].get("content_carried")
              is True
              and entries2[0].get("content_sha256")
              == STOCK_TAKE_SHA256
              and entries2[0].get("authority_path")
              == "source"
              and (entries2[0].get("served") or {}).get(
                  "kind") == "whole"
              and entries2[0].get("dispatch_id")
              == first_read.get("dispatch_id"),
              f"{entries2}")
        check("continuity: the first wake's working "
              "set stands empty, under the declared "
              "budget, with the note the worker reads",
              (packages[1].get("working_set") or {}).get(
                  "entries") == []
              and ws2.get("budget_bytes") == BUDGET
              and "retrieve it again" in (
                  ws2.get("note") or ""))

        # (b) both sources together at the third wake.
        entries3 = (packages[3].get("working_set")
                    or {}).get("entries") or []
        check("(b) the wake after the second read "
              "holds both sources together, each with "
              "its full content",
              [e.get("path") for e in entries3] == [
                  "sources/stock-take.md",
                  "sources/a3-pass.md"]
              and entries3[0].get("content")
              == stock_take.decode("utf-8")
              and entries3[1].get("content")
              == a3_pass.decode("utf-8")
              and all(e.get("content_carried") is True
                      for e in entries3),
              f"{[e.get('path') for e in entries3]}")

        # (c) the repeat read adds no entry.
        entries4 = (packages[4].get("working_set")
                    or {}).get("entries") or []
        check("(c) the wake after the repeated read "
              "still holds exactly two entries, and the "
              "stock-take entry keeps the FIRST "
              "gathering dispatch's identity",
              len(entries4) == 2
              and entries4[0].get("dispatch_id")
              == first_read.get("dispatch_id")
              and entries4[0].get("outcome_event_seq")
              == outcome_seqs.get(
                  first_read.get("dispatch_id")),
              f"{[(e.get('path'), e.get('dispatch_id')) for e in entries4]}")

        # The range read, preserved as the range.
        entries5 = (packages[5].get("working_set")
                    or {}).get("entries") or []
        slice_text = _first_lines(
            index_tail, 4).decode("utf-8")
        range_entry = entries5[2] if len(entries5) > 2 \
            else {}
        check("continuity: the fifth wake holds three "
              "entries; the index-tail entry is the "
              "range actually retrieved (lines 1–4, "
              "the exact slice, never the whole file)",
              len(entries5) == 3
              and range_entry.get("tool")
              == "sandbox.read_range"
              and range_entry.get("path")
              == "sources/index-tail.md"
              and (range_entry.get("served") or {}).get(
                  "kind") == "range"
              and (range_entry.get("served") or {}).get(
                  "start_line") == 1
              and (range_entry.get("served") or {}).get(
                  "end_line") == 4
              and range_entry.get("content") == slice_text
              and range_entry.get("content")
              != index_tail.decode("utf-8"),
              f"{range_entry.get('served')}")

        # (d) provenance and hashes against the record.
        all_match = True
        for entry in entries5:
            recorded = outcomes.get(
                entry.get("dispatch_id")) or {}
            if entry.get("content_sha256") != \
                    recorded.get("content_sha256") or \
                    entry.get("content") != \
                    recorded.get("content") or \
                    entry.get("authority_path") != \
                    recorded.get("authority_path") or \
                    entry.get("path") != \
                    recorded.get("path") or \
                    entry.get("outcome_event_seq") != \
                    outcome_seqs.get(
                        entry.get("dispatch_id")) or \
                    entry.get("content_sha256") != \
                    hashlib.sha256(
                        (entry.get("content") or "")
                        .encode("utf-8")).hexdigest():
                all_match = False
        check("(d) every working-set entry's content, "
              "hash, path, authority path and outcome "
              "position verify against the recorded "
              "outcome it cites",
              all_match and len(entries5) == 3)

        # No duplicate copies within a package.
        blob5 = json.dumps(packages[5])
        check("continuity: in the fifth package each "
              "gathered content appears exactly once "
              "(in its working-set entry) — the "
              "tool_results entries and the delta's "
              "copies carry the stub pointing at the "
              "working set",
              blob5.count(json.dumps(
                  stock_take.decode("utf-8"))) == 1
              and blob5.count(json.dumps(
                  a3_pass.decode("utf-8"))) == 1
              and blob5.count(json.dumps(slice_text))
              == 1
              and all(
                  (tr.get("result") or {}).get(
                      "presented_in") == "working_set"
                  and "content" not in (
                      tr.get("result") or {})
                  for tr in packages[5].get(
                      "tool_results") or []
                  if tr.get("outcome") == "result")
              and all(
                  ((e.get("payload") or {}).get(
                      "result") or {}).get(
                      "presented_in") == "working_set"
                  for e in packages[5].get("delta")
                  or []
                  if e.get("type") == "TOOL_OUTCOME"
                  and (e.get("payload") or {}).get(
                      "outcome") == "result"),
              "")
        ws5 = packages[5].get("working_set") or {}
        check("continuity: the fifth set's carried "
              "byte total is the sum of its carried "
              "entries, under the budget",
              ws5.get("content_bytes") == sum(
                  e.get("content_bytes") or 0
                  for e in entries5
                  if e.get("content_carried"))
              and ws5.get("content_bytes") <= BUDGET)

        _check_commitments("continuity", cwork,
                           packages, 5)
        _check_checker("continuity", rep)

        # ================= budget =================
        rep = reports["budget"]
        bwork = work / "budget"
        check("budget: the run yields in nine "
              "iterations",
              rep["outcome"] == "yield"
              and rep["iterations"] == 9,
              f"{rep['outcome']} / {rep['iterations']}")
        check("budget: the sealed record declares the "
              "working-set contract",
              rep["sealed_working_set_contract"]
              == tool_policy.WORKING_SET_CONTRACT)
        packages = _packages(bwork)
        evs = _events(bwork)
        dispatched = [_payload(e) for e in evs
                      if e["type"] == "TOOL_DISPATCHED"]
        requests = {}
        for e in evs:
            if e["type"] == "TOOL_REQUESTED":
                p = _payload(e)
                requests[p.get("request_id")] = \
                    p.get("parameters") or {}
        outcomes = {}
        for e in evs:
            if e["type"] == "TOOL_OUTCOME":
                p = _payload(e)
                outcomes[p.get("dispatch_id")] = \
                    p.get("result") or {}
        script_order = [
            ("sources/synth-a.md", 1, 100),
            ("sources/synth-a.md", 101, 200),
            ("sources/synth-a.md", 201, 300),
            ("sources/synth-a.md", 301, 400),
            ("sources/synth-b.md", 1, 100),
            ("sources/synth-b.md", 101, 200),
            ("sources/synth-b.md", 201, 210),
            ("sources/synth-b.md", 211, 310)]
        seen_order = []
        for d in dispatched:
            params = requests.get(
                d.get("request_id")) or {}
            seen_order.append((
                params.get("path"),
                params.get("start_line"),
                params.get("end_line")))
        check("budget: eight read_range dispatches in "
              "script order",
              [d.get("tool") for d in dispatched]
              == ["sandbox.read_range"] * 8
              and seen_order == script_order,
              f"{seen_order}")
        sizes = [(outcomes.get(
            d.get("dispatch_id")) or {}).get(
            "content_bytes") for d in dispatched]
        check("budget: the recorded gathers total "
              "more than the working-set budget (the "
              "ceiling is genuinely exercised)",
              all(isinstance(s, int) for s in sizes)
              and sum(sizes) > BUDGET
              and sum(sizes[:7]) <= BUDGET
              and sum(sizes[:7]) + sizes[7] > BUDGET,
              f"sizes={sizes} budget={BUDGET}")

        entries8 = (packages[8].get("working_set")
                    or {}).get("entries") or []
        check("budget: the eighth wake holds seven "
              "entries, all carried",
              len(entries8) == 7
              and all(e.get("content_carried") is True
                      for e in entries8),
              f"{len(entries8)}")
        ws9 = packages[9].get("working_set") or {}
        entries9 = ws9.get("entries") or []
        last = entries9[-1] if entries9 else {}
        synth_b = (bwork / "run" / "sandbox" / "sources"
                   / "synth-b.md").read_bytes()
        slice8 = synth_b[210 * 100:310 * 100].decode(
            "utf-8")
        eighth = dispatched[7]
        check("(e) the final wake holds eight entries: "
              "the first seven carried (including the "
              "small late range that still fits), the "
              "eighth standing by its provenance alone "
              "— marked not carried, reason named, no "
              "content key, nothing truncated — its "
              "hash the recorded slice's hash",
              len(entries9) == 8
              and all(e.get("content_carried") is True
                      for e in entries9[:7])
              and last.get("content_carried") is False
              and last.get("not_carried_reason")
              == "working_set_budget"
              and "content" not in last
              and last.get("path")
              == "sources/synth-b.md"
              and last.get("dispatch_id")
              == eighth.get("dispatch_id")
              and last.get("content_sha256")
              == hashlib.sha256(
                  slice8.encode("utf-8")).hexdigest()
              and last.get("content_sha256")
              == (outcomes.get(
                  eighth.get("dispatch_id")) or {}).get(
                  "content_sha256")
              and (last.get("served") or {}).get(
                  "start_line") == 211
              and (last.get("served") or {}).get(
                  "end_line") == 310
              and ws9.get("content_bytes")
              == sum(sizes[:7])
              and ws9.get("budget_bytes") == BUDGET
              and "retrieve it again" in (
                  ws9.get("note") or ""),
              f"last={ {k: last.get(k) for k in ('path', 'content_carried', 'not_carried_reason', 'content_sha256')} }")
        _check_commitments("budget", bwork, packages, 9)
        _check_checker("budget", rep)

        # ---------- zero leftovers
        bwrap = subprocess.run(
            ["pgrep", "-x", "bwrap"],
            capture_output=True, text=True)
        check("leftovers: no bwrap process standing",
              bwrap.returncode != 0, bwrap.stdout[:120])
    finally:
        shutil.rmtree(work, ignore_errors=True)
    check("leftovers: the scratch tree is removed",
          not work.exists())
    print(f"\n{CHECKS[0] - len(FAILURES)}/{CHECKS[0]} "
          f"checks passed")
    if FAILURES:
        print("FAILURES:", "; ".join(FAILURES))
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
