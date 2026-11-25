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

The freedom scenario witnesses the freedom-first setup
pass (2026-11-24) on the same combined configuration:
a whole pull of index-tail (40,953 bytes — over the
retrieval regime's 12,000-byte per-result ceiling)
returns a recorded result and is carried whole in the
next wake's working set; the fourth wake holds all
three sources together (57,562 bytes, within the
budget); the package presenting the doorway's refusal
of an out-of-boundary read carries the failure
instruction — what was asked, the plain-terms why, the
stocked sources as the working alternative — and the
package presenting the identical second refusal names
it as a repeat of step 4; the checker stands eleven
checks, all ok, over this record too. The stocking
completability check is witnessed directly: the
standing sources' per-source facts (size, lines,
carriable whole, the accumulated set carriable
together), and a synthetic 70,001-byte required source
refused at setup, named with its size and the budget.

The orientation pass (Ben's rulings on the worker
consultation, 2026-11-24) is witnessed on the freedom
packages: every wake states its step position plainly
(step k of the sealed ceiling, matching the record's
iteration count) and its task status (in progress),
and the package's tool list equals the sealed grant
set exactly — names, scopes, count — with the
execution tool's line presenting a shell command as a
first-class method that can read a whole file (cat).

The batch scenario witnesses the examiner's repeat
correction (2026-11-24), judged text so one response
carries two identical requests: both fail at the
executor over a scratch file that does not stand, and
the package presenting both failures names NEITHER as
a repeat — neither had been presented when the calls
were made — while the identical request made after
those failures were presented IS named a repeat of
step 1, for this reason. The journal scenario
witnesses Part A of the orientation pass: the case
designates scratch/journal.md, and the packages
present the journal as it stands — empty at the first
wake, the first note verbatim at the second, both
notes in order at the third; the checker stands
eleven checks, all ok, over both records.

The journal adversarial section answers the
examiner's boundary finding on Part A: the journal's
resting places are the worker's own writing space, so
the designated path can be a worker-planted symlink
to a host file. Exercised directly against the
executor's host-side reader (the scripted worker
cooperates and cannot plant links through the stub):
an absolute symlink at the journal path, a relative
symlink escaping the scratch root, and the scratch
directory itself planted as a symlink are each
refused — nothing is returned, the host sentinel's
contents appear nowhere in the presented journal
component — while a regular journal file in either
resting place still presents verbatim.

The run-6 package (Ben's rulings and the worker's
briefcase consultation, 2026-11-24) is witnessed on
the same packages: every scenario's case carries the
onboarding, and the first wake's package opens with
it verbatim while later wakes carry the short cover
in its place; the components stand in the briefcase's
order; the carried assignment opens with the
deliverable statement (the file, the write door,
contribute-is-not-the-deliverable) before the task
text; the journal component carries its purpose
label in the worker's terms; and the tool list is
the phase-grouped menu — Gather, Compose, Deliver in
order — whose distinct tools are exactly the sealed
grant set (the orientation (C) checks below read the
menu's grouped shape; the property they assert is
the orientation pass's own: the presented set equals
the sealed grants, nothing hardcoded). The freshness
pair witnesses Ben's R31 ruling: the declared run's
contribution — run 5's shape, answered from a frozen
view the record has since advanced past — RECORDS,
flagged stale_basis, with no R31 rejection in the
record; the control run, sealing no declaration,
refuses the same answer in the same position under
R31; the checker stands eleven checks, all ok, over
both records.

Run: python3 live-demo/test_working_set_rehearsal.py
Exits 0 when every check passes.
"""

import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "room" / "rig"))

from fabric.canonical import canonical, sha256_hex  # noqa: E402

from framework import tool_policy  # noqa: E402
from framework.doorway import Doorway  # noqa: E402
from framework.executor import Executor  # noqa: E402
from framework.loop import Loop  # noqa: E402
from framework.record import FrameworkStore  # noqa: E402
import working_set_rehearsal as rehearsal  # noqa: E402
import stock_demo  # noqa: E402
from demo_run import ONBOARDING  # noqa: E402

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

        # ================= freedom =================
        # The freedom-first setup pass (2026-11-24):
        # carriage honesty at the whole pull, failure
        # instruction at the genuine wall, the repeat
        # named.
        rep = reports["freedom"]
        fwork = work / "freedom"
        check("freedom: the run yields in six "
              "iterations",
              rep["outcome"] == "yield"
              and rep["iterations"] == 6,
              f"{rep['outcome']} / {rep['iterations']}")
        check("freedom: the sealed record declares "
              "the working-set contract",
              rep["sealed_working_set_contract"]
              == tool_policy.WORKING_SET_CONTRACT)
        packages = _packages(fwork)
        evs = _events(fwork)
        f_requests = {}
        for e in evs:
            if e["type"] == "TOOL_REQUESTED":
                p = _payload(e)
                f_requests[p.get("request_id")] = (
                    p.get("tool"), p.get("parameters") or {})
        f_dispatched = [_payload(e) for e in evs
                        if e["type"] == "TOOL_DISPATCHED"]
        check("freedom: exactly three dispatches — "
              "the three whole reads; the two "
              "out-of-boundary calls were refused at "
              "the doorway and never dispatched",
              [f_requests.get(d.get("request_id"),
                              (None, {}))[1].get("path")
               for d in f_dispatched] == [
                  "sources/index-tail.md",
                  "sources/stock-take.md",
                  "sources/a3-pass.md"],
              f"{[f_requests.get(d.get('request_id'), (None, {})) for d in f_dispatched]}")
        f_outcomes = {}
        for e in evs:
            if e["type"] == "TOOL_OUTCOME":
                p = _payload(e)
                f_outcomes[p.get("dispatch_id")] = p
        tail_outcome = f_outcomes.get(
            f_dispatched[0].get("dispatch_id")) or {}
        tail_result = tail_outcome.get("result") or {}
        index_tail_f = (fwork / "run" / "sandbox"
                        / "sources"
                        / "index-tail.md").read_bytes()
        stock_take_f = (fwork / "run" / "sandbox"
                        / "sources"
                        / "stock-take.md").read_bytes()
        a3_pass_f = (fwork / "run" / "sandbox" / "sources"
                     / "a3-pass.md").read_bytes()
        check("freedom: the whole pull of index-tail "
              "stands in the record as a result — "
              "40,953 bytes, over the 12,000-byte "
              "per-result ceiling the old populations "
              "refuse at, its content the file itself",
              tail_outcome.get("outcome") == "result"
              and tail_result.get("content_bytes")
              == 40953
              and tail_result.get("content_bytes")
              > tool_policy.RETRIEVAL_RESULT_CEILING
              and tail_result.get("content")
              == index_tail_f.decode("utf-8")
              and tail_result.get("content_sha256")
              == INDEX_TAIL_SHA256,
              f"{tail_result.get('content_bytes')}")
        entries_f2 = (packages[2].get("working_set")
                      or {}).get("entries") or []
        check("freedom: the wake after the whole pull "
              "carries index-tail whole in the working "
              "set — one entry, the whole-file served "
              "descriptor, full content, carried",
              len(entries_f2) == 1
              and entries_f2[0].get("path")
              == "sources/index-tail.md"
              and (entries_f2[0].get("served") or {})
              .get("kind") == "whole"
              and entries_f2[0].get("content")
              == index_tail_f.decode("utf-8")
              and entries_f2[0].get("content_bytes")
              == 40953
              and entries_f2[0].get("content_carried")
              is True,
              f"{[(e.get('path'), e.get('content_bytes')) for e in entries_f2]}")
        ws_f4 = packages[4].get("working_set") or {}
        entries_f4 = ws_f4.get("entries") or []
        check("freedom: the fourth wake holds all "
              "three sources together, each whole and "
              "carried — 57,562 bytes against the "
              "64,000 budget",
              [e.get("path") for e in entries_f4] == [
                  "sources/index-tail.md",
                  "sources/stock-take.md",
                  "sources/a3-pass.md"]
              and [e.get("content") for e in entries_f4]
              == [index_tail_f.decode("utf-8"),
                  stock_take_f.decode("utf-8"),
                  a3_pass_f.decode("utf-8")]
              and all(e.get("content_carried") is True
                      for e in entries_f4)
              and ws_f4.get("content_bytes") == 57562
              and ws_f4.get("budget_bytes") == BUDGET,
              f"{[(e.get('path'), e.get('content_bytes'), e.get('content_carried')) for e in entries_f4]} "
              f"total={ws_f4.get('content_bytes')}")

        def refused_entry(package):
            for tr in package.get("tool_results") or []:
                if tr.get("outcome") == "refused" and \
                        tr.get("refusal_class") \
                        == "doorway_refused":
                    return tr
            return {}

        first_refusal = refused_entry(packages[5])
        instr5 = first_refusal.get("instruction") or {}
        check("freedom: the package presenting the "
              "out-of-boundary refusal carries the "
              "failure instruction — what was asked, "
              "the plain-terms why (boundary membership, "
              "no regulation citation), the stocked "
              "sources as the working alternative — "
              "and no repeat (nothing identical had "
              "failed before it)",
              instr5.get("asked") == {
                  "tool": "sandbox.read",
                  "parameters": {
                      "path": "sources/not-stocked.md"}}
              and "not a member of the pinned case's "
                  "sealed evidence boundary"
                  in (instr5.get("why") or "")
              and "R44" not in (instr5.get("why") or "")
              and all(name in (
                  instr5.get("alternative") or "")
                  for name in (
                      "sources/stock-take.md",
                      "sources/a3-pass.md",
                      "sources/index-tail.md"))
              and "repeat" not in instr5,
              f"{instr5}")
        second_refusal = refused_entry(packages[6])
        instr6 = second_refusal.get("instruction") or {}
        repeat6 = instr6.get("repeat") or {}
        check("freedom: the package presenting the "
              "identical second refusal names it as a "
              "repeat — this exact call already failed "
              "at step 4 — with the alternative standing",
              instr6.get("asked") == {
                  "tool": "sandbox.read",
                  "parameters": {
                      "path": "sources/not-stocked.md"}}
              and repeat6.get("already_failed_step") == 4
              and "step 4" in (repeat6.get("note") or "")
              and all(name in (
                  instr6.get("alternative") or "")
                  for name in (
                      "sources/stock-take.md",
                      "sources/a3-pass.md",
                      "sources/index-tail.md")),
              f"{instr6}")
        _check_commitments("freedom", fwork, packages, 6)
        _check_checker("freedom", rep)

        # ---------- orientation (Parts B, C, D) on the
        # freedom packages: his position, his task
        # state, and his tools stated plainly.
        f_iterations = sorted(k for k in packages
                              if k >= 1)
        check("orientation (B): every freedom wake "
              "states its step position plainly — "
              "step k of the sealed ceiling, matching "
              "the record's iteration count at that "
              "wake",
              f_iterations == [1, 2, 3, 4, 5, 6]
              and all(
                  (packages[k].get("step_position")
                   or {}).get("statement")
                  == f"step {k} of 12"
                  and (packages[k].get("step_position")
                       or {}).get("iteration") == k
                  and (packages[k].get("step_position")
                       or {}).get("step_ceiling") == 12
                  for k in f_iterations),
              f"{[(k, (packages[k].get('step_position') or {})) for k in f_iterations]}")
        check("orientation (D): every freedom wake "
              "states the task status plainly — "
              "in progress",
              all(packages[k].get("task_status")
                  == "in progress"
                  for k in f_iterations),
              f"{[packages[k].get('task_status') for k in f_iterations]}")
        sealed_grants = None
        for e in evs:
            if e["type"] == "ASSEMBLY_GENERATED":
                sealed_grants = _payload(e).get("grants")
        expected_tools = sorted(
            (g.get("tool"),
             (g.get("scope_ceiling") or {}).get(
                 "path_prefix"))
            for g in sealed_grants or [])
        # The run-6 package groups the tool list by the
        # job's phases; the (C) property is unchanged —
        # the presented set equals the sealed grant set
        # exactly — read across the menu's groups: the
        # distinct (tool, scope) pairs standing in the
        # groups, the groups in the phase order.
        menu = packages[6].get("tool_list") or []
        presented_tools = sorted(
            {(t.get("tool"), t.get("scope"))
             for group in menu
             for t in (group.get("tools") or [])})
        check("orientation (C): the wake package's "
              "tool list — the phase-grouped menu — "
              "presents the sealed grant set exactly: "
              "groups in the phase order Gather, "
              "Compose, Deliver, and the distinct tools "
              "across the groups are every grant's tool "
              "and scope, the same count, nothing "
              "hardcoded",
              sealed_grants is not None
              and [g.get("phase") for g in menu]
              == ["Gather", "Compose", "Deliver"]
              and len(presented_tools) == 10
              and presented_tools == expected_tools,
              f"presented={presented_tools} "
              f"expected={expected_tools}")
        exec_lines = [t for group in menu
                      if group.get("phase") == "Gather"
                      for t in (group.get("tools") or [])
                      if t.get("tool") == "container.exec"]
        check("orientation (C): the execution tool's "
              "Gather line presents it as a first-class "
              "working method — a shell command can "
              "read a whole file at once (cat)",
              len(exec_lines) == 1
              and "cat" in (
                  exec_lines[0].get("purpose") or "")
              and "whole file" in (
                  exec_lines[0].get("purpose") or ""),
              f"{exec_lines}")

        # ---------- completability at stocking
        _manifest, _mhash, real_stock = \
            stock_demo.verify_source_set()
        facts = stock_demo.check_completability(
            real_stock, BUDGET)
        by_path = {f["path"]: f
                   for f in facts["sources"]}
        check("completability: the standing sources "
              "pass — per-source facts (size, lines, "
              "carriable whole) as stocked, the "
              "accumulated set carriable together",
              facts.get("ok") is True
              and facts.get("budget_bytes") == BUDGET
              and facts.get("accumulated_bytes") == 57562
              and facts.get("accumulated_carriable")
              is True
              and {p: (f["bytes"], f["lines"])
                   for p, f in by_path.items()} == {
                      "sources/stock-take.md":
                          (11946, 155),
                      "sources/a3-pass.md": (4663, 55),
                      "sources/index-tail.md":
                          (40953, 24)}
              and all(f["carriable_whole"] is True
                      for f in by_path.values())
              and all(f["obtainable_via"]
                      for f in by_path.values()),
              f"{facts}")
        refusal = None
        try:
            stock_demo.check_completability(
                {"sources/huge.md": b"x" * 70001}, BUDGET)
        except stock_demo.StockingError as exc:
            refusal = str(exc)
        check("completability: a synthetic 70,001-byte "
              "required source is REFUSED at setup — "
              "the refusal names the source, its size "
              "and the budget",
              refusal is not None
              and "sources/huge.md" in refusal
              and "70001" in refusal
              and str(BUDGET) in refusal,
              f"{refusal}")

        # ================= batch =================
        # The examiner's repeat correction: a repeat
        # must have been PRESENTED in an earlier wake.
        rep = reports["batch"]
        bwork2 = work / "batch"
        check("batch: the run yields in three "
              "iterations",
              rep["outcome"] == "yield"
              and rep["iterations"] == 3,
              f"{rep['outcome']} / {rep['iterations']}")
        packages_b = _packages(bwork2)
        evs_b = _events(bwork2)
        b_dispatched = [_payload(e) for e in evs_b
                        if e["type"] == "TOOL_DISPATCHED"]
        b_failures = [_payload(e) for e in evs_b
                      if e["type"] == "TOOL_OUTCOME"
                      and _payload(e).get("outcome")
                      == "failure"]
        check("batch: all three identical requests "
              "were dispatched (a granted door) and all "
              "three failed at the executor — the file "
              "does not stand",
              len(b_dispatched) == 3
              and len(b_failures) == 3,
              f"dispatched={len(b_dispatched)} "
              f"failures={len(b_failures)}")

        def failure_entries(package):
            return [tr for tr in
                    (package.get("tool_results") or [])
                    if tr.get("outcome") == "failure"]

        batch_entries = failure_entries(packages_b[2])
        check("batch (a): the package presenting the "
              "batch's two failures carries both, each "
              "with its failure instruction — and "
              "NEITHER is named a repeat: neither "
              "failure had been presented when the "
              "calls were made, however identical they "
              "are",
              len(batch_entries) == 2
              and all(
                  (e.get("instruction") or {}).get(
                      "asked") == {
                          "tool": "sandbox.read",
                          "parameters": {
                              "path":
                                  "scratch/not-here.md"}}
                  and "no file stands at "
                      "scratch/not-here.md"
                      in ((e.get("instruction")
                           or {}).get("why") or "")
                  and "repeat" not in (
                      e.get("instruction") or {})
                  for e in batch_entries),
              f"{batch_entries}")
        third_entries = failure_entries(packages_b[3])
        third_repeat = ((third_entries[0].get(
            "instruction") or {}).get("repeat") or {}) \
            if third_entries else {}
        check("batch (b): the identical request made "
              "after the batch failures were presented "
              "IS named a repeat — of step 1, for this "
              "reason: the earlier failures stand "
              "presented in the wake between, with the "
              "same plain reason",
              len(third_entries) == 1
              and third_repeat.get(
                  "already_failed_step") == 1
              and "step 1" in (
                  third_repeat.get("note") or "")
              and "for this reason" in (
                  third_repeat.get("note") or ""),
              f"{third_entries}")
        _check_commitments("batch", bwork2, packages_b, 3)
        _check_checker("batch", rep)

        # ================= journal =================
        # The orientation pass, Part A: his notebook,
        # presented back as it stands.
        rep = reports["journal"]
        jwork = work / "journal"
        check("journal: the run yields in three "
              "iterations",
              rep["outcome"] == "yield"
              and rep["iterations"] == 3,
              f"{rep['outcome']} / {rep['iterations']}")
        packages_j = _packages(jwork)
        j_first = packages_j[1].get("journal") or {}
        check("journal (A): the first wake presents "
              "the designated journal — his path, "
              "labelled his own working notes, empty: "
              "the notebook is his to start",
              j_first.get("path")
              == "scratch/journal.md"
              and "your journal" in (
                  j_first.get("label") or "")
              and j_first.get("content") == ""
              and j_first.get("bytes_total") == 0
              and j_first.get("complete") is True,
              f"{j_first}")
        j_second = packages_j[2].get("journal") or {}
        check("journal (A): the wake after the first "
              "note presents the journal as it stands — "
              "the note verbatim, complete, from his "
              "sandbox scratch",
              j_second.get("content")
              == rehearsal.JOURNAL_NOTE_1
              and j_second.get("bytes_total") == len(
                  rehearsal.JOURNAL_NOTE_1.encode(
                      "utf-8"))
              and j_second.get("bytes_carried") == len(
                  rehearsal.JOURNAL_NOTE_1.encode(
                      "utf-8"))
              and j_second.get("complete") is True
              and j_second.get("resting_place")
              == "sandbox",
              f"{j_second}")
        j_third = packages_j[3].get("journal") or {}
        both_notes = (rehearsal.JOURNAL_NOTE_1
                      + rehearsal.JOURNAL_NOTE_2)
        check("journal (A): the second note stands "
              "appended to the first — the worker's own "
              "cooperative convention (he rewrote the "
              "notebook carrying both; append is not "
              "mechanically enforced) — and the next "
              "wake's journal carries both notes in "
              "order, the first unchanged",
              j_third.get("content") == both_notes
              and j_third.get("bytes_total") == len(
                  both_notes.encode("utf-8"))
              and j_third.get("complete") is True,
              f"{j_third}")
        _check_commitments("journal", jwork, packages_j,
                           3)
        _check_checker("journal", rep)

        # ============ run-6 package structure ========
        # Ben's rulings and the worker's briefcase
        # consultation (2026-11-24), witnessed on the
        # continuity packages (the onboarding and the
        # cover), the journal packages (the component
        # order with a journal standing), and the
        # carried assignment itself.
        packages_c6 = _packages(work / "continuity")
        first6 = packages_c6[1]
        later6 = packages_c6[2]
        check("run-6 package (1): the first wake's "
              "package opens with the onboarding, "
              "verbatim — its first component is the "
              "case's onboarding text, word for word",
              list(first6.keys())[0] == "onboarding"
              and first6.get("onboarding")
              == ONBOARDING["text"],
              f"{list(first6.keys())[:3]}")
        cover6 = later6.get("cover") or {}
        check("run-6 package (1): a later wake carries "
              "the short cover, not the onboarding — "
              "the cover stands first, names the "
              "headline and the deliverable, and states "
              "his step and his task's state",
              list(later6.keys())[0] == "cover"
              and "onboarding" not in later6
              and cover6.get("headline")
              == ONBOARDING["headline"]
              and cover6.get("deliverable")
              == ONBOARDING["deliverable"]
              and "Step 2 of 12" in (
                  cover6.get("statement") or "")
              and "in progress" in (
                  cover6.get("statement") or "")
              and len(cover6.get("statement") or "")
              < 400,
              f"{cover6}")
        check("run-6 package (3): the first wake's "
              "components stand in the briefcase's "
              "order — onboarding, position, status, "
              "the case, the working set, the tool "
              "menu, then the record's furniture",
              list(first6.keys())[:6]
              == ["onboarding", "step_position",
                  "task_status", "case", "working_set",
                  "tool_list"],
              f"{list(first6.keys())}")
        check("run-6 package (3): with a journal "
              "standing, it stands in the order between "
              "the working set and the tool menu",
              list(packages_j[1].keys())[:7]
              == ["onboarding", "step_position",
                  "task_status", "case", "working_set",
                  "journal", "tool_list"],
              f"{list(packages_j[1].keys())}")
        assignment6 = (first6.get("case") or {}).get(
            "assignment") or ""
        check("run-6 package (2): the carried "
              "assignment opens with the deliverable "
              "statement — the file scratch/brief.md, "
              "the write door named, and submitting "
              "the text as a contribute outcome stated "
              "NOT to be the deliverable — before the "
              "task text",
              assignment6.startswith("THE DELIVERABLE")
              and "scratch/brief.md" in assignment6
              and "sandbox.write" in assignment6
              and "NOT the deliverable" in assignment6
              and assignment6.index("THE DELIVERABLE")
              < assignment6.index("THE TASK"),
              f"{assignment6[:160]}")
        label6 = (packages_j[1].get("journal") or {}).get(
            "label") or ""
        check("run-6 package (3): the journal "
              "component carries its purpose label in "
              "his terms — your notebook: notes, "
              "decisions, where you left off; it "
              "returns to you at every wake; it is "
              "yours to write and rewrite",
              "your notebook" in label6
              and "notes, decisions" in label6
              and "returns to you at every wake"
              in label6
              and "yours to write and rewrite"
              in label6,
              f"{label6}")
        menu6 = first6.get("tool_list") or []
        entries6 = [t for group in menu6
                    for t in (group.get("tools") or [])]
        deliver6 = next(
            (g for g in menu6
             if g.get("phase") == "Deliver"), {})
        deliver_entries6 = deliver6.get("tools") or []
        check("run-6 package (4): the Deliver group "
              "names the deliverable and the yield — "
              "its one entry is the write tool, its "
              "purpose names scratch/brief.md as the "
              "deliverable, the group states the yield "
              "outcome, and every menu entry carries a "
              "purpose and an example",
              len(deliver_entries6) == 1
              and deliver_entries6[0].get("tool")
              == "sandbox.write"
              and "scratch/brief.md" in (
                  deliver_entries6[0].get("purpose")
                  or "")
              and "yield" in (
                  deliver6.get("note") or "")
              and all(t.get("purpose")
                      and t.get("example")
                      for t in entries6),
              f"{deliver6}")

        # ============ freshness (R31 pair) ===========
        # Ben's ruling (2026-11-24): the freshness
        # rejection is declaration-governed. The
        # declared run's contribution — run 5's shape,
        # answered from a frozen view the record has
        # since advanced past (the iteration's own
        # response-evidence event names the case) —
        # records; the control's identical answer in
        # the identical position stands refused.
        rep = reports["freshness"]
        fwork6 = work / "freshness"
        check("freshness: the declared run yields in "
              "two iterations, its sealed record "
              "declaring the freshness guard suspended",
              rep["outcome"] == "yield"
              and rep["iterations"] == 2
              and rep["sealed_freshness_guard"]
              == "r31-suspended-v1",
              f"{rep['outcome']} / {rep['iterations']} / "
              f"{rep['sealed_freshness_guard']}")
        fevs = _events(fwork6)
        f_contribs = [_payload(e) for e in fevs
                      if e["type"] == "CONTRIBUTION"]
        f_r31 = [e for e in fevs
                 if e["type"] == "REJECTION"
                 and "(R31)" in (
                     _payload(e).get("ground") or "")]
        check("freshness (5): under the declaration, "
              "the contribution in run 5's position "
              "RECORDS — it stands in the record with "
              "its text, flagged stale_basis, and no "
              "R31 rejection stands anywhere in the "
              "record",
              len(f_contribs) == 1
              and f_contribs[0].get("text")
              == rehearsal.CONTRIBUTION_TEXT
              and f_contribs[0].get("stale_basis")
              is True
              and not f_r31,
              f"contribs={len(f_contribs)} "
              f"r31={len(f_r31)}")
        _check_commitments("freshness", fwork6,
                           _packages(fwork6), 2)
        _check_checker("freshness", rep)

        rep = reports["freshness_control"]
        fcwork6 = work / "freshness-control"
        check("freshness control: the undeclared run "
              "yields in two iterations, its sealed "
              "record declaring no suspension",
              rep["outcome"] == "yield"
              and rep["iterations"] == 2
              and rep["sealed_freshness_guard"] is None,
              f"{rep['outcome']} / {rep['iterations']} / "
              f"{rep['sealed_freshness_guard']}")
        fcevs = _events(fcwork6)
        fc_contribs = [e for e in fcevs
                       if e["type"] == "CONTRIBUTION"]
        fc_r31 = [_payload(e) for e in fcevs
                  if e["type"] == "REJECTION"
                  and "(R31)" in (
                      _payload(e).get("ground") or "")]
        check("freshness control (5): without the "
              "declaration the same answer in the same "
              "position is REFUSED under R31 — no "
              "contribution stands, and the rejection "
              "names the changed subject since view "
              "(the rule lives)",
              not fc_contribs
              and len(fc_r31) == 1
              and "changed since view" in (
                  fc_r31[0].get("ground") or ""),
              f"contribs={len(fc_contribs)} "
              f"r31={fc_r31}")
        _check_commitments("freshness control", fcwork6,
                           _packages(fcwork6), 2)
        _check_checker("freshness control", rep)

        # ============ journal, adversarial ============
        # The examiner's journal finding (2026-11-24):
        # the journal's resting places are the worker's
        # own writing space, so the designated path can
        # be a worker-planted SYMLINK to a host file, and
        # the host-side presentation reader must never
        # follow it out of the scratch root. The scripted
        # rehearsal's worker cooperates and cannot plant
        # links through the stub, so this case is
        # exercised directly against the reader that
        # actually lives with the hazard — the executor's
        # read_designated_scratch — and against the
        # loop's journal component built on it.
        adv = work / "journal-adversarial"
        outside = adv / "outside"
        outside.mkdir(parents=True)
        sentinel = ("HOST-SENTINEL-4f2c: contents that "
                    "must never be presented")
        (outside / "sentinel.txt").write_text(sentinel)
        room_tree = adv / "room-tree"
        (room_tree / "scratch").mkdir(parents=True)
        adv_sandbox = adv / "sandbox"
        (adv_sandbox / "scratch").mkdir(parents=True)
        adv_store = FrameworkStore(str(adv / "run.db"))
        adv_executor = Executor(
            Doorway(adv_store), str(adv_sandbox),
            room=SimpleNamespace(tree=room_tree))
        designated = "scratch/journal.md"
        room_journal = room_tree / "scratch" / "journal.md"
        box_journal = adv_sandbox / "scratch" / "journal.md"

        # (1) an absolute symlink at the room's journal
        # path, nothing in the sandbox: refused whole.
        os.symlink(str(outside / "sentinel.txt"),
                   room_journal)
        found = adv_executor.read_designated_scratch(
            designated)
        check("journal adversarial: an absolute symlink "
              "at the room's journal path is refused — "
              "the reader returns nothing, never the "
              "link target's contents",
              found is None, f"{found}")

        # (2) a relative symlink in the sandbox escaping
        # the scratch root (../../): refused whole.
        room_journal.unlink()
        os.symlink("../../outside/sentinel.txt",
                   box_journal)
        found = adv_executor.read_designated_scratch(
            designated)
        check("journal adversarial: a relative symlink "
              "escaping the sandbox scratch root is "
              "refused — the reader returns nothing",
              found is None, f"{found}")

        # (3) both places hostile: the loop's journal
        # component is the established empty
        # presentation, and the sentinel appears
        # nowhere in it.
        os.symlink(str(outside / "sentinel.txt"),
                   room_journal)
        loop_shell = Loop.__new__(Loop)
        loop_shell.executor = adv_executor
        comp = loop_shell._journal_component(
            {"content": {"journal": designated}})
        check("journal adversarial: with both resting "
              "places hostile, the presented journal "
              "component is empty and the host sentinel "
              "appears nowhere in it",
              comp.get("content") == ""
              and comp.get("bytes_total") == 0
              and sentinel not in json.dumps(
                  comp, sort_keys=True),
              f"{comp}")
        room_journal.unlink()
        box_journal.unlink()

        # (4) the scratch directory itself planted as a
        # symlink to a directory holding a journal:
        # refused at the component, nothing read.
        (adv_sandbox / "scratch").rmdir()
        elsewhere = adv / "elsewhere"
        elsewhere.mkdir()
        (elsewhere / "journal.md").write_text(
            sentinel + " (second)")
        os.symlink(str(elsewhere), adv_sandbox / "scratch")
        found = adv_executor.read_designated_scratch(
            designated)
        check("journal adversarial: the scratch "
              "directory itself planted as a symlink is "
              "refused — no component of the path is "
              "followed",
              found is None, f"{found}")
        (adv_sandbox / "scratch").unlink()
        (adv_sandbox / "scratch").mkdir()

        # (5) ordinary presentation preserved: a
        # regular journal file in the room presents
        # verbatim, from the room resting place.
        room_journal.write_text("note one\n")
        found = adv_executor.read_designated_scratch(
            designated)
        comp = loop_shell._journal_component(
            {"content": {"journal": designated}})
        check("journal adversarial: a regular journal "
              "file in the room still presents normally "
              "— verbatim, resting place room",
              found == ("room", b"note one\n", None)
              and comp.get("content") == "note one\n"
              and comp.get("resting_place") == "room",
              f"{found} / {comp}")

        # (6) and a regular journal file in the sandbox
        # presents normally when the room holds none.
        room_journal.unlink()
        box_journal.write_text("sandbox note\n")
        found = adv_executor.read_designated_scratch(
            designated)
        check("journal adversarial: a regular journal "
              "file in the sandbox still presents "
              "normally — verbatim, resting place "
              "sandbox",
              found == ("sandbox", b"sandbox note\n",
                        None),
              f"{found}")

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
