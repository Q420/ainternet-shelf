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

The staged scenario witnesses staged onboarding
(INDEX 544, Ben's direction, 2026-11-25) in its own
section, counted separately in the output: the
generation seals the presentation contract; the
scripted stand-in walks memory, case, files and task
across his first four wakes and works from dashboard
wakes after; the witnesses assert the stage order and
each stage's size budget (the first wake under 8,000
rendered chars against the 29,341 the verbatim
package measured on the round-seven wire), stage 1's
framing of the memory as his own, the absence of the
case dump, the view and the delta from every package,
no stage component standing at any other stage, the
files stage's own pull in the record, every
iteration's presentation commitment equal to the
hash of the very package the captures show was
presented, the checker clean over the record, and
the assignment completed through the contribution
door. The control stands in the same rehearsal run:
the continuity scenario's generation seals no
presentation declaration.

Run: python3 live-demo/test_working_set_rehearsal.py
Exits 0 when every check passes.
"""

import base64
import copy
import hashlib
import json
import os
import re
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
from demo_run import (  # noqa: E402
    ASSIGNMENT_COMBINED, GLOSSARY, ONBOARDING,
    ROLE_MEMORY)

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


def _staged_packages(work):
    """The staged wake packages a scenario's captures
    carried, by chat index, with their rendered sizes:
    the package JSON as the prompt presented it — the
    body, plus the tool catalogue section the adapter
    renders separately, merged back into the package it
    was pulled from. Returns {index: (package, chars)}
    where chars counts the body JSON and the catalogue
    JSON as rendered (the contract's framing lines are
    not the package's)."""
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
            if not isinstance(content, str) or \
                    "Your wake package:" not in content:
                continue
            anchor = content.index("Your wake package:")
            start = content.index("{", anchor)
            try:
                package, end = decoder.raw_decode(
                    content[start:])
            except ValueError:
                continue
            if not isinstance(package, dict) or \
                    "presentation" not in package:
                continue
            chars = end
            rest = content[start + end:]
            if "Your tool catalogue" in rest:
                tstart = rest.index("[", rest.index(
                    "Your tool catalogue"))
                try:
                    tools, tend = decoder.raw_decode(
                        rest[tstart:])
                except ValueError:
                    tools = None
                if isinstance(tools, list):
                    package["tools"] = tools
                    chars += tend
            packages[idx] = (package, chars)
            break
    return packages


def _presentation_hash_of(package):
    """The staged package's commitment, recomputed from
    the captured package itself: its tool results
    standing by their identities, its working set by
    its own commitment hash, everything else verbatim —
    the loop's core derivation, applied to the very
    package the captures show was presented."""
    core = copy.deepcopy(package)
    results = core.pop("tool_results", [])
    core["tool_result_refs"] = [
        {"dispatch_id": e.get("dispatch_id"),
         "request_id": e.get("request_id"),
         "outcome": e.get("outcome"),
         "event_seq": e.get("event_seq")}
        for e in results]
    core.pop("working_set", None)
    core["working_set_hash"] = _ws_hash_of(package)
    return sha256_hex(canonical(core))


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

        # ============ staged onboarding ==============
        # INDEX 544 (Ben's direction, 2026-11-25): the
        # generation sealed the presentation contract,
        # and the scripted stand-in walked the stages.
        # The witnesses: the stages in order, each within
        # its size budget; stage 1's framing (the memory
        # introduced as his own, standing alone); no case
        # dump, view or delta anywhere; no content item
        # standing twice; the files stage's own pull in
        # the record; the task stage's menu; the
        # dashboard's shape; every iteration's
        # presentation commitment equal to the hash of
        # the very package the captures show was
        # presented; the checker clean over the record;
        # and the assignment completed through the door.
        staged_before = CHECKS[0]
        rep = reports["staged"]
        swork = work / "staged"
        check("staged: the run ends in six iterations "
              "— the four onboarding stages, then two "
              "dashboard wakes — with the yield the "
              "door's completion carries (the filing "
              "itself is witnessed from the record "
              "below)",
              rep["outcome"] == "yield"
              and rep["iterations"] == 6,
              f"{rep['outcome']} / {rep['iterations']}")
        check("staged: the sealed record declares the "
              "presentation contract beside the "
              "working-set contract",
              rep["sealed_presentation_contract"]
              == "staged-onboarding-v1"
              and rep["sealed_working_set_contract"]
              == tool_policy.WORKING_SET_CONTRACT,
              f"{rep['sealed_presentation_contract']} / "
              f"{rep['sealed_working_set_contract']}")
        check("staged: the control stands in the same "
              "rehearsal — the continuity generation "
              "seals NO presentation declaration, and "
              "its packages are the ordered packages "
              "they have always been",
              reports["continuity"][
                  "sealed_presentation_contract"] is None
              and "case" in (
                  _packages(cwork).get(1) or {}),
              "continuity sealed presentation: "
              + str(reports["continuity"][
                  "sealed_presentation_contract"]))
        spackages = _staged_packages(swork)
        check("staged: seven chat captures (identify + "
              "six iterations), each carrying a staged "
              "package",
              sorted(spackages) == [1, 2, 3, 4, 5, 6],
              f"{sorted(spackages)}")
        pkgs = {k: v[0] for k, v in spackages.items()}
        sizes = {k: v[1] for k, v in spackages.items()}
        print(f"staged package sizes (rendered "
              f"chars): {sizes}")
        stages = [(pkgs[k].get("presentation") or {})
                  .get("stage")
                  for k in (1, 2, 3, 4, 5, 6)]
        check("staged: the stages walk in order — "
              "memory, case, files, task, then dashboard "
              "wakes",
              stages == ["memory", "case", "files",
                         "task", "dashboard", "dashboard"],
              f"{stages}")
        check("staged: no package carries the case "
              "dump, the view or the delta",
              all("case" not in p and "view" not in p
                  and "delta" not in p
                  for p in pkgs.values()))
        dumps = {k: json.dumps(p, sort_keys=True)
                 for k, p in pkgs.items()}
        check("staged: the verbatim onboarding guide "
              "stands in no package — the staged cover "
              "replaces it",
              all("HOW YOUR BRIEFCASE IS LAID OUT"
                  not in d for d in dumps.values()))
        check("staged: each stage's component stands "
              "at its own stage and no other — the "
              "memory only at stage 1, the essentials "
              "only at stage 2, the files only at "
              "stage 3, the task only at stage 4, the "
              "pointers only at dashboard wakes",
              all(("memory" in pkgs[k]) == (k == 1)
                  and ("case_essentials" in pkgs[k])
                  == (k == 2)
                  and ("files" in pkgs[k]) == (k == 3)
                  and ("task" in pkgs[k]) == (k == 4)
                  and ("pointers" in pkgs[k]) == (k >= 5)
                  for k in pkgs))
        check("staged: the first wake is a fraction of "
              "the old first wake — under 8,000 rendered "
              "chars against the 29,341 the verbatim "
              "package measured on the round-seven wire",
              sizes.get(1, 10 ** 9) < 8000,
              f"{sizes}")
        check("staged: every onboarding stage package "
              "stands within its budget (memory < 8,000; "
              "case < 9,000; files < 17,000; task "
              "< 22,000 rendered chars — the files and "
              "task budgets carry the tool catalogue's "
              "~11,000 rendered chars, the same offer "
              "the old shape made at every wake; the "
              "files budget additionally carries round "
              "nine's worked example — the first "
              "source's real listing, ~1,100 rendered "
              "chars — and each needed file's way in)",
              sizes.get(1, 10 ** 9) < 8000
              and sizes.get(2, 10 ** 9) < 9000
              and sizes.get(3, 10 ** 9) < 17000
              and sizes.get(4, 10 ** 9) < 22000,
              f"{sizes}")
        check("staged: dashboard wakes carry no "
              "onboarding bulk — outside the working set "
              "they hold, the whole package is under "
              "14,000 rendered chars of furniture, "
              "catalogue and pointers",
              all(sizes[k] - len(json.dumps(
                  pkgs[k].get("working_set") or {}))
                  < 14000 for k in (5, 6)),
              f"{sizes}")
        check("staged: stage 1 frames the memory as "
              "his own — the introduction stands at the "
              "head of the memory component, and the "
              "entries are the case's role memory "
              "exactly",
              pkgs[1]["memory"]["introduction"]
              .startswith("This is your memory")
              and pkgs[1]["memory"]["entries"]
              == ROLE_MEMORY,
              f"{list(pkgs[1].get('memory') or {})}")
        check("staged: no tools are offered at the "
              "memory or case stages — the offer opens "
              "at the files stage",
              "tools" not in pkgs[1]
              and "tools" not in pkgs[2]
              and "tools" in pkgs[3])
        check("staged: stage 2 carries the case "
              "essentials — the sealed delivery "
              "declaration verbatim, the freshness "
              "position under the ruling, and the "
              "opening record",
              pkgs[2]["case_essentials"]["delivery"]
              == {"destination": "scratch/brief.md",
                  "route": "contribution-v1"}
              and "suspended" in pkgs[2][
                  "case_essentials"]["freshness"]
              and pkgs[2]["case_essentials"]["opening"]
              ["settled"] == [
                  "No work product is produced in "
                  "the opening; the work happens in "
                  "the room."],
              "essentials keys: "
              + str(list(pkgs[2].get(
                  "case_essentials") or {})))
        check("staged: stage 3's briefcase is the "
              "glossary's pointers — addresses and "
              "descriptions, no contents — and the "
              "journal stands as a pointer carrying "
              "its purpose",
              [e["address"] for e in
               pkgs[3]["files"]["briefcase"]]
              == [e["address"] for e in GLOSSARY]
              and pkgs[3]["files"]["journal"]["path"]
              == "scratch/journal.md"
              and "orientation, not record and not "
                  "memory" in pkgs[3]["files"][
                      "journal"]["label"])
        evs = _events(swork)
        dispatched_tools = [
            _payload(e).get("tool") for e in evs
            if e["type"] == "TOOL_DISPATCHED"]
        check("staged: the files stage's pull is real "
              "— the record's dispatches are the list "
              "at the files stage, then the two reads",
              dispatched_tools == ["sandbox.list",
                                   "sandbox.read",
                                   "sandbox.read"],
              f"{dispatched_tools}")
        check("staged: stage 4 carries the assignment "
              "text and the phase-grouped menu — "
              "Gather, Compose, Deliver",
              pkgs[4]["task"]["assignment"]
              == ASSIGNMENT_COMBINED
              and [g["phase"] for g in
                   pkgs[4]["tool_list"]]
              == ["Gather", "Compose", "Deliver"])
        check("staged: dashboard wakes carry the five "
              "pointers back into the briefcase",
              all([p["item"] for p in pkgs[k]["pointers"]]
                  == ["your memory", "your case",
                      "your files", "your journal",
                      "your task"]
                  for k in (5, 6)))
        recorded_ph = {}
        for e in evs:
            if e["type"] == "LOOP_ITERATION":
                p = _payload(e)
                recorded_ph[p.get("iteration")] = \
                    p.get("presentation_hash")
        check("staged: every LOOP_ITERATION carries "
              "the presentation commitment",
              len(recorded_ph) == 6
              and all(isinstance(h, str) and len(h) == 64
                      for h in recorded_ph.values()),
              f"{recorded_ph}")
        for k in (1, 2, 3, 4, 5, 6):
            check(f"staged: iteration {k}'s commitment "
                  f"is the hash of the staged package "
                  f"its captured wake presented",
                  recorded_ph.get(k)
                  == _presentation_hash_of(pkgs[k]),
                  f"recorded={recorded_ph.get(k)} "
                  f"package="
                  f"{_presentation_hash_of(pkgs[k])}")
        filings = [_payload(e) for e in evs
                   if e["type"] == "DELIVERABLE_FILED"]
        check("staged: the assignment completes "
              "through the door — one filing, authored "
              "by the worker, filed by the office, at "
              "the declared destination, its hash the "
              "contribution's",
              len(filings) == 1
              and filings[0].get("destination")
              == "scratch/brief.md"
              and filings[0].get("authored_by")
              == "crew-1"
              and filings[0].get("filed_by") == "office"
              and filings[0].get("content_sha256")
              == hashlib.sha256(
                  rehearsal.STAGED_BRIEF_TEXT
                  .encode("utf-8")).hexdigest(),
              f"{filings}")
        filed_path = (swork / "run" / "sandbox"
                      / "scratch" / "brief.md")
        check("staged: the filed brief stands in the "
              "sandbox at the declared destination, "
              "verbatim",
              filed_path.exists()
              and filed_path.read_text(
                  encoding="utf-8")
              == rehearsal.STAGED_BRIEF_TEXT,
              f"{filed_path}")
        _check_commitments("staged", swork, pkgs, 6)
        _check_checker("staged", rep)

        # ---- round nine (INDEX 548 + the INDEX 549
        # fold-in): the snapshot, the needed files'
        # ways in, and the worked example, over the
        # staged run above.
        check("staged: stage 1's snapshot carries the "
              "opening record's settled results "
              "verbatim — where the worker stands, from "
              "the record, before his memory",
              pkgs[1].get("snapshot", {}).get("settled")
              == ["No work product is produced in "
                  "the opening; the work happens in "
                  "the room."]
              and pkgs[1].get("snapshot", {})
              .get("note", "").startswith(
                  "Where you stand"),
              f"{pkgs[1].get('snapshot')}")
        check("staged: every needed file in stage 3's "
              "map carries its way in — the concrete "
              "call naming a granted tool over the "
              "file's own address",
              all(e.get("access") == {
                  "tool": "sandbox.read",
                  "parameters": {"path": e["address"]}}
                  for e in pkgs[3]["files"]["briefcase"]),
              f"{pkgs[3]['files']['briefcase']}")
        example = pkgs[3]["files"].get("worked_example")
        check("staged: stage 3's worked example is "
              "the office's sandbox.list call on the "
              "first glossary file, shown with its "
              "result",
              example is not None
              and example.get("call") == {
                  "tool": "sandbox.list",
                  "parameters": {
                      "path": GLOSSARY[0]["address"]}}
              and isinstance(example.get("result"),
                             dict),
              f"{example and example.get('call')}")
        check("staged: the presented example is the "
              "sealed record's own — the loop presents "
              "the seal, not a reconstruction of it",
              example is not None
              and example.get("result")
              == (rep.get("sealed_worked_example")
                  or {}).get("result")
              and (rep.get("sealed_worked_example")
                   or {}).get("path")
              == GLOSSARY[0]["address"],
              f"{rep.get('sealed_worked_example')}")
        # The example is REAL: recompute the listing
        # from the staged file's own bytes, here,
        # independently of the framework, and compare
        # whole — size, line count and the structure
        # map itself.
        raw = (swork / "run" / "sandbox"
               / GLOSSARY[0]["address"]).read_bytes()
        text_lines = []
        start = 0
        while start < len(raw):
            nl = raw.find(b"\n", start)
            piece = raw[start:] if nl == -1 \
                else raw[start:nl + 1]
            start = len(raw) if nl == -1 else nl + 1
            piece_text = piece.decode("utf-8")
            text_lines.append(
                piece_text[:-1]
                if piece_text.endswith("\n")
                else piece_text)
        heading_lines = []
        for number, line_text in enumerate(
                text_lines, start=1):
            match = re.match(r"^(#{1,6})\s+(.*?)\s*$",
                             line_text)
            if match:
                heading_lines.append(
                    (number, len(match.group(1)),
                     match.group(2)))
        expected_map = (
            f"{GLOSSARY[0]['address']} — {len(raw)} "
            f"bytes, {len(text_lines)} lines")
        for number, level, heading_text in heading_lines:
            expected_map += (
                f"\nline {number}: "
                f"{'#' * level} {heading_text}")
        check("staged: the worked example's result "
              "is the staged file's real listing — "
              "recomputed from its bytes in this "
              "witness, not trusted from the seal",
              example is not None
              and example["result"].get("content")
              == expected_map
              and example["result"].get("size_bytes")
              == len(raw)
              and example["result"].get("line_count")
              == len(text_lines),
              "expected map head: "
              + expected_map[:120])
        check("staged: the example's result is never "
              "carried into the working set — it "
              "demonstrates a call; it is not material "
              "the worker gathered",
              example is not None
              and all(
                  example["result"]["content"] not in
                  json.dumps(pkgs[k].get("working_set")
                             or {})
                  for k in (4, 5, 6)),
              "working sets at wakes 4-6")

        # ---- the stage gate, files stage: an early
        # contribution is set aside unfiled, the
        # correction rides the next wake, and the run
        # completes on the honest contribution.
        grep = reports["staged_gate_files"]
        gwork = work / "staged-gate-files"
        gpkgs = {k: v[0] for k, v in
                 _staged_packages(gwork).items()}
        check("staged-gate-files: the run completes "
              "on the honest contribution, in five "
              "iterations — the gate consumed one",
              grep["outcome"] == "yield"
              and grep["iterations"] == 5,
              f"{grep['outcome']} / {grep['iterations']}")
        gevs = _events(gwork)
        gates = [_payload(e) for e in gevs
                 if e["type"] == "DELIVERY_STAGE_GATE"]
        gcontribs = {e["event_seq"]: _payload(e)
                     for e in gevs
                     if e["type"] == "CONTRIBUTION"}
        gfilings = [_payload(e) for e in gevs
                    if e["type"] == "DELIVERABLE_FILED"]
        check("staged-gate-files: exactly one stage "
              "gate stands, at the files stage, "
              "recording that nothing was filed",
              len(gates) == 1
              and gates[0].get("stage") == "files"
              and gates[0].get("filed") is False,
              f"{gates}")
        gate = gates[0] if gates else {}
        check("staged-gate-files: the gate names the "
              "early contribution and its text's hash",
              gcontribs.get(
                  gate.get("contribution_seq"), {})
              .get("text")
              == rehearsal.STAGED_GATE_TEXT
              and gate.get("text_sha256")
              == hashlib.sha256(
                  rehearsal.STAGED_GATE_TEXT
                  .encode("utf-8")).hexdigest(),
              f"{gate}")
        check("staged-gate-files: the only filing "
              "names the honest contribution — the "
              "gated one was never filed",
              len(gfilings) == 1
              and gfilings[0].get("contribution_seq")
              != gate.get("contribution_seq")
              and gfilings[0].get("content_sha256")
              == hashlib.sha256(
                  rehearsal.STAGED_BRIEF_TEXT
                  .encode("utf-8")).hexdigest(),
              f"{gfilings}")
        gcorr = gpkgs[4].get(
            "delivery_stage_gate_correction") or {}
        check("staged-gate-files: the correction "
              "rides the wake after the gate, carrying "
              "the gate's facts — what arrived, at "
              "which stage, and when delivery opens",
              gcorr.get("stage") == "files"
              and gcorr.get("contribution_seq")
              == gate.get("contribution_seq")
              and gcorr.get("text_sha256")
              == gate.get("text_sha256")
              and "before your task had been "
                  "presented" in gcorr.get(
                      "what_arrived", "")
              and "Delivery opens with your task"
              in gcorr.get("instruction", "")
              and "delivery_stage_gate_correction"
              not in gpkgs[3],
              f"{gcorr}")
        grec_ph = {}
        for e in gevs:
            if e["type"] == "LOOP_ITERATION":
                p = _payload(e)
                grec_ph[p.get("iteration")] = \
                    p.get("presentation_hash")
        for k in (1, 2, 3, 4, 5):
            check(f"staged-gate-files: iteration {k}'s "
                  f"commitment is the hash of the "
                  f"staged package its captured wake "
                  f"presented",
                  grec_ph.get(k)
                  == _presentation_hash_of(gpkgs[k]),
                  f"recorded={grec_ph.get(k)}")
        _check_commitments(
            "staged-gate-files", gwork, gpkgs, 5)
        _check_checker("staged-gate-files", grep)

        # ---- the stage gate, memory stage: the
        # earliest possible early contribution.
        mrep = reports["staged_gate_memory"]
        mwork = work / "staged-gate-memory"
        mpkgs = {k: v[0] for k, v in
                 _staged_packages(mwork).items()}
        check("staged-gate-memory: the run completes "
              "on the honest contribution, in four "
              "iterations — the gate consumed one",
              mrep["outcome"] == "yield"
              and mrep["iterations"] == 4,
              f"{mrep['outcome']} / {mrep['iterations']}")
        mevs = _events(mwork)
        mgates = [_payload(e) for e in mevs
                  if e["type"] == "DELIVERY_STAGE_GATE"]
        mfilings = [_payload(e) for e in mevs
                    if e["type"] == "DELIVERABLE_FILED"]
        check("staged-gate-memory: exactly one stage "
              "gate stands, at the memory stage — the "
              "first wake — and the honest contribution "
              "at the task stage is the only filing",
              len(mgates) == 1
              and mgates[0].get("stage") == "memory"
              and mgates[0].get("filed") is False
              and len(mfilings) == 1
              and mfilings[0].get("contribution_seq")
              != (mgates[0].get("contribution_seq")
                  if mgates else None),
              f"{mgates} / {mfilings}")
        mcorr = mpkgs[2].get(
            "delivery_stage_gate_correction") or {}
        check("staged-gate-memory: the correction "
              "rides the case-stage wake, naming the "
              "memory stage",
              mcorr.get("stage") == "memory"
              and "at the memory stage"
              in mcorr.get("what_arrived", "")
              and "delivery_stage_gate_correction"
              not in mpkgs[1],
              f"{mcorr}")
        mrec_ph = {}
        for e in mevs:
            if e["type"] == "LOOP_ITERATION":
                p = _payload(e)
                mrec_ph[p.get("iteration")] = \
                    p.get("presentation_hash")
        for k in (1, 2, 3, 4):
            check(f"staged-gate-memory: iteration "
                  f"{k}'s commitment is the hash of "
                  f"the staged package its captured "
                  f"wake presented",
                  mrec_ph.get(k)
                  == _presentation_hash_of(mpkgs[k]),
                  f"recorded={mrec_ph.get(k)}")
        _check_commitments(
            "staged-gate-memory", mwork, mpkgs, 4)
        _check_checker("staged-gate-memory", mrep)

        # ---- the omission: the demonstration call
        # cannot be made, so no example stands — the
        # files stage presents the map without one,
        # and the run is otherwise the staged walk.
        nrep = reports["staged_noexample"]
        nwork = work / "staged-noexample"
        npkgs = {k: v[0] for k, v in
                 _staged_packages(nwork).items()}
        check("staged-noexample: no worked example "
              "stands in the seal, and the files stage "
              "presents no example — the omission is "
              "honest, the introduction the variant "
              "that promises none",
              nrep.get("sealed_worked_example") is None
              and "worked_example" not in
              npkgs[3]["files"]
              and "worked as an example" not in
              npkgs[3]["files"]["introduction"],
              f"{list(npkgs[3]['files'])}")
        check("staged-noexample: the needed files "
              "still carry their ways in, and the run "
              "completes as the staged walk does",
              all(e.get("access") == {
                  "tool": "sandbox.read",
                  "parameters": {"path": e["address"]}}
                  for e in npkgs[3]["files"]
                  ["briefcase"])
              and nrep["outcome"] == "yield"
              and nrep["iterations"] == 6,
              f"{nrep['outcome']} / {nrep['iterations']}")
        _check_commitments(
            "staged-noexample", nwork, npkgs, 6)
        _check_checker("staged-noexample", nrep)
        print(f"staged-onboarding section: "
              f"{CHECKS[0] - staged_before} checks")

        # ============ round ten: the directory form ==
        # (INDEX 552, Part A): sandbox.list on a
        # directory returns the directory's entries
        # through the same governed performer; the two
        # spellings of the directory meet at the one
        # route; the file form is byte-identical to the
        # listing the performer has always returned.
        directory_before = CHECKS[0]
        drep = reports["directory"]
        dwork = work / "directory"
        devs = _events(dwork)
        check("directory: the run completes in six "
              "iterations",
              drep["outcome"] == "yield"
              and drep["iterations"] == 6,
              f"{drep['outcome']} / {drep['iterations']}")
        dtool = {_payload(e).get("dispatch_id"):
                 _payload(e).get("tool")
                 for e in devs
                 if e["type"] == "TOOL_DISPATCHED"}
        dlist = [_payload(e) for e in devs
                 if e["type"] == "TOOL_OUTCOME"
                 and _payload(e).get("outcome") == "result"
                 and dtool.get(
                     _payload(e).get("dispatch_id"))
                 == "sandbox.list"]
        dresults = [p.get("result") or {} for p in dlist]
        dir_results = [r for r in dresults
                       if r.get("path") == "sources"]
        # The expected directory map, built from the
        # staged sandbox itself: the entries standing
        # there, sorted, with their kinds and sizes.
        dsources = dwork / "run" / "sandbox" / "sources"
        expected_entries = []
        for name in sorted(os.listdir(dsources)):
            entry_path = dsources / name
            if entry_path.is_dir():
                expected_entries.append(
                    f"sources/{name} — directory")
            else:
                expected_entries.append(
                    f"sources/{name} — file, "
                    f"{entry_path.stat().st_size} bytes")
        expected_dir_map = "\n".join(
            [f"sources — directory, "
             f"{len(expected_entries)} entries"]
            + expected_entries)
        check("directory: both spellings of the "
              "directory stand dispatched and return the "
              "one result — the directory's entries, "
              "each with its address, kind and size",
              len(dir_results) == 2
              and all(r.get("content") == expected_dir_map
                      for r in dir_results)
              and all(r.get("entry_count") == 3
                      for r in dir_results),
              f"{[r.get('content') for r in dir_results]}")
        scratch_results = [r for r in dresults
                           if r.get("path") == "scratch"]
        check("directory: the scratch directory lists "
              "as his own, empty",
              len(scratch_results) == 1
              and scratch_results[0].get("content")
              == "scratch — directory, 0 entries"
              and scratch_results[0].get("entry_count")
              == 0,
              f"{scratch_results}")
        file_results = [r for r in dresults
                        if r.get("path")
                        == "sources/stock-take.md"]
        raw = (dwork / "run" / "sandbox"
               / "sources" / "stock-take.md").read_bytes()
        text_lines = []
        start = 0
        while start < len(raw):
            nl = raw.find(b"\n", start)
            piece = raw[start:] if nl == -1 \
                else raw[start:nl + 1]
            start = len(raw) if nl == -1 else nl + 1
            piece_text = piece.decode("utf-8")
            text_lines.append(
                piece_text[:-1]
                if piece_text.endswith("\n")
                else piece_text)
        expected_file_map = (
            f"sources/stock-take.md — {len(raw)} bytes, "
            f"{len(text_lines)} lines")
        for number, line_text in enumerate(
                text_lines, start=1):
            match = re.match(r"^(#{1,6})\s+(.*?)\s*$",
                             line_text)
            if match:
                expected_file_map += (
                    f"\nline {number}: "
                    f"{'#' * len(match.group(1))} "
                    f"{match.group(2)}")
        check("directory: the file form is the listing "
              "it has always been — recomputed from the "
              "staged file's bytes in this witness, and "
              "equal to the staged run's sealed worked "
              "example over the same file",
              len(file_results) == 1
              and file_results[0].get("content")
              == expected_file_map
              and file_results[0].get("content")
              == (reports["staged"][
                      "sealed_worked_example"]
                  or {})["result"]["content"]
              and file_results[0].get("size_bytes")
              == len(raw)
              and file_results[0].get("line_count")
              == len(text_lines),
              f"{file_results}")
        drejections = [_payload(e) for e in devs
                       if e["type"] == "REJECTION"]
        check("directory: a directory under no grant "
              "refuses at the doorway, the refusal "
              "naming the scopes that stand instead — "
              "and only the four lawful lists stand "
              "dispatched",
              len([e for e in devs
                   if e["type"] == "TOOL_DISPATCHED"
                   and _payload(e).get("tool")
                   == "sandbox.list"]) == 4
              and any("room" in str(r.get("ground", ""))
                      and "lies under neither"
                      in str(r.get("ground", ""))
                      and "sources/ scope"
                      in str(r.get("ground", ""))
                      for r in drejections),
              f"{drejections}")
        _check_checker("directory", drep)
        print(f"directory-form section: "
              f"{CHECKS[0] - directory_before} checks")

        # ============ round ten: the evidence gate ===
        # (INDEX 552, Part B): the case declares the
        # evidence a delivery must rest on; the door
        # adjudicates a contribution against it.
        evidence_before = CHECKS[0]
        addresses = rehearsal.DELIVERY_EVIDENCE[
            "addresses"]

        def evidence_parts(scenario_work):
            evs = _events(scenario_work)
            gates = [_payload(e) for e in evs
                     if e["type"]
                     == "DELIVERY_EVIDENCE_GATE"]
            filings = [_payload(e) for e in evs
                       if e["type"] == "DELIVERABLE_FILED"]
            contribs = {e["event_seq"]: _payload(e)
                        for e in evs
                        if e["type"] == "CONTRIBUTION"}
            return evs, gates, filings, contribs

        # ---- the progressive gates: nothing gathered,
        # then one source, then two, then the last by
        # ranges composing its whole.
        egrep = reports["evidence_gates"]
        egwork = work / "evidence-gates"
        check("evidence-gates: the generation seals "
              "the case's delivery-evidence declaration",
              egrep["sealed_delivery_evidence"]
              == rehearsal.DELIVERY_EVIDENCE,
              f"{egrep['sealed_delivery_evidence']}")
        check("evidence-gates: the run completes on "
              "the fourth contribution, in twelve "
              "iterations — the rehearsal's standing "
              "step ceiling, each gate consuming "
              "exactly its own",
              egrep["outcome"] == "yield"
              and egrep["iterations"] == 12,
              f"{egrep['outcome']} / {egrep['iterations']}")
        egevs, eggates, egfilings, egcontribs = \
            evidence_parts(egwork)
        check("evidence-gates: three gates stand, "
              "naming what was missing at each — all "
              "three sources, then the two unread, then "
              "the last one — each recording that "
              "nothing was filed",
              [g.get("missing") for g in eggates]
              == [addresses,
                  ["sources/a3-pass.md",
                   "sources/index-tail.md"],
                  ["sources/index-tail.md"]]
              and all(g.get("filed") is False
                      for g in eggates),
              f"{eggates}")
        check("evidence-gates: each gate names its own "
              "contribution, whose text is the brief's, "
              "by its hash",
              all(egcontribs.get(
                      g.get("contribution_seq"), {})
                  .get("text")
                  == rehearsal.EVIDENCE_BRIEF_TEXT
                  and g.get("text_sha256")
                  == hashlib.sha256(
                      rehearsal.EVIDENCE_BRIEF_TEXT
                      .encode("utf-8")).hexdigest()
                  for g in eggates),
              f"{eggates}")
        check("evidence-gates: the only filing names "
              "the fourth contribution — no gated "
              "contribution was ever filed",
              len(egfilings) == 1
              and egfilings[0].get("contribution_seq")
              not in [g.get("contribution_seq")
                      for g in eggates]
              and egfilings[0].get("content_sha256")
              == hashlib.sha256(
                  rehearsal.EVIDENCE_BRIEF_TEXT
                  .encode("utf-8")).hexdigest(),
              f"{egfilings}")
        egpkgs = {k: v[0] for k, v in
                  _staged_packages(egwork).items()}
        for wake, gate in ((5, eggates[0] if eggates
                            else {}),
                           (7, eggates[1] if len(eggates) > 1
                            else {}),
                           (9, eggates[2] if len(eggates) > 2
                            else {})):
            corr = egpkgs[wake].get(
                "delivery_evidence_gate_correction") or {}
            check(f"evidence-gates: the correction "
                  f"rides wake {wake}, naming each "
                  f"missing file with its way in",
                  corr.get("missing")
                  == gate.get("missing")
                  and corr.get("contribution_seq")
                  == gate.get("contribution_seq")
                  and corr.get("text_sha256")
                  == gate.get("text_sha256")
                  and all(f"sandbox.read on {a}"
                          in corr.get("instruction", "")
                          for a in
                          gate.get("missing") or []),
                  f"{corr}")
        check("evidence-gates: no other wake carries "
              "the correction",
              all("delivery_evidence_gate_correction"
                  not in egpkgs[k]
                  for k in egpkgs if k not in (5, 7, 9)),
              f"{sorted(egpkgs)}")
        egranges = []
        for e in egevs:
            if e["type"] == "TOOL_OUTCOME":
                p = _payload(e)
                result = p.get("result") or {}
                if result.get("path") \
                        == "sources/index-tail.md" and \
                        "start_line" in result:
                    egranges.append(
                        (result.get("start_line"),
                         result.get("end_line")))
        egasked = [_payload(e).get("parameters") or {}
                   for e in egevs
                   if e["type"] == "TOOL_REQUESTED"
                   and (_payload(e).get("parameters")
                        or {}).get("path")
                   == "sources/index-tail.md"]
        check("evidence-gates: the last source stands "
              "gathered by four ranges composing its "
              "whole line range — the first pulled at "
              "the files stage, before any gate — and "
              "the final range's asked end ran past "
              "the file's end, the performer clamping "
              "it to line 24 (the record fact that "
              "establishes the whole)",
              egranges == [(1, 6), (7, 13), (14, 20),
                           (21, 24)]
              and any(p.get("end_line") == 9999
                      for p in egasked),
              f"{egranges} / {egasked}")
        egrec_ph = {}
        for e in egevs:
            if e["type"] == "LOOP_ITERATION":
                p = _payload(e)
                egrec_ph[p.get("iteration")] = \
                    p.get("presentation_hash")
        for k in range(1, 13):
            check(f"evidence-gates: iteration {k}'s "
                  f"commitment is the hash of the "
                  f"staged package its captured wake "
                  f"presented",
                  egrec_ph.get(k)
                  == _presentation_hash_of(egpkgs[k]),
                  f"recorded={egrec_ph.get(k)}")
        _check_commitments(
            "evidence-gates", egwork, egpkgs, 12)
        _check_checker("evidence-gates", egrep)

        # ---- listed is not gathered: shape is not
        # substance.
        elrep = reports["evidence_listed"]
        elwork = work / "evidence-listed"
        check("evidence-listed: the run completes on "
              "the second contribution, in ten "
              "iterations — the gate consumed one",
              elrep["outcome"] == "yield"
              and elrep["iterations"] == 10,
              f"{elrep['outcome']} / {elrep['iterations']}")
        elevs, elgates, elfilings, elcontribs = \
            evidence_parts(elwork)
        elists = [e["event_seq"] for e in elevs
                  if e["type"] == "TOOL_OUTCOME"
                  and (_payload(e).get("result") or {})
                  .get("path") in addresses
                  and "line_count" in (
                      _payload(e).get("result") or {})]
        check("evidence-listed: one gate stands, "
              "naming all three sources — although all "
              "three stood listed before the "
              "contribution, a listing is shape, not "
              "substance",
              len(elgates) == 1
              and elgates[0].get("missing") == addresses
              and len(elists) == 3
              and all(s < elgates[0].get(
                  "contribution_seq") for s in elists)
              and len(elfilings) == 1
              and elfilings[0].get("contribution_seq")
              != elgates[0].get("contribution_seq"),
              f"{elgates} / lists {elists}")
        elpkgs = {k: v[0] for k, v in
                  _staged_packages(elwork).items()}
        elcorr = elpkgs[7].get(
            "delivery_evidence_gate_correction") or {}
        check("evidence-listed: the correction rides "
              "the wake after the gate, naming all "
              "three",
              elcorr.get("missing") == addresses
              and "delivery_evidence_gate_correction"
              not in elpkgs[6],
              f"{elcorr}")
        _check_commitments(
            "evidence-listed", elwork, elpkgs, 10)
        _check_checker("evidence-listed", elrep)

        # ---- the clean pass: everything read whole,
        # no gate fires.
        ewrep = reports["evidence_whole"]
        ewwork = work / "evidence-whole"
        ewevs, ewgates, ewfilings, ewcontribs = \
            evidence_parts(ewwork)
        check("evidence-whole: with all three sources "
              "read whole, no gate fires — the run "
              "completes on the first contribution, in "
              "seven iterations, one filing",
              ewrep["outcome"] == "yield"
              and ewrep["iterations"] == 7
              and ewgates == []
              and len(ewfilings) == 1
              and ewrep["sealed_delivery_evidence"]
              == rehearsal.DELIVERY_EVIDENCE,
              f"{ewrep['outcome']} / "
              f"{ewrep['iterations']} / {ewgates}")
        ewpkgs = {k: v[0] for k, v in
                  _staged_packages(ewwork).items()}
        _check_commitments(
            "evidence-whole", ewwork, ewpkgs, 7)
        _check_checker("evidence-whole", ewrep)

        # ---- the control: scenario G seals no
        # evidence declaration; its worker read two
        # sources whole and only listed the third, and
        # his contribution was filed exactly as it
        # always has been.
        _sevs, sgates, _sfilings, _scontribs = \
            evidence_parts(swork)
        check("evidence control: the staged run seals "
              "no delivery-evidence declaration and no "
              "evidence gate stands in its record — "
              "absent the declaration, adjudication is "
              "exactly as it was",
              reports["staged"][
                  "sealed_delivery_evidence"] is None
              and sgates == [],
              f"{sgates}")
        print(f"delivery-evidence section: "
              f"{CHECKS[0] - evidence_before} checks")

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
