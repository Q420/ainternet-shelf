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

The pointer scenario witnesses the pointer rule
(INDEX 568, Ben's tap, 2026-11-25) in its own
section, counted separately in the output: the same
staged walk under the successor presentation
contract, staged-onboarding-v2 — a gathered entry's
content presented exactly once, in the first wake
after its gather, as part of that wake's newest
results, and standing as a pointer in every later
package. The witnesses assert the pointer form's
fields against the record, the content-once
standings across all nine wakes (twice for the
re-pulled source), the fully-gathered dashboard
wake's size under its stated bound, every
iteration's presentation commitment recomputed
from the captured packages under the pointer-form
core, the evidence gate filing on record-standing
reads whose contents stand in no current package,
and the checker clean over the record, deriving
the pointer form independently. The v1 scenarios
stand as its control: their seals and packages are
exactly what they were.

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
from framework import loop as loop_module  # noqa: E402
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


def _tree_native_packages(work):
    """The native-lane scenario's wake packages, by
    loop iteration: its captures travel the bounded
    mode (the Groq transport's seam), where index 0 is
    the identify call, indices 1-5 are the probe's
    trials, and loop iteration k stands at index 5+k.
    The extraction is _staged_packages' own, over that
    mode: the package JSON as the prompt presented it,
    plus the tool catalogue section the adapter renders
    separately, merged back in, with rendered chars."""
    captures = [json.loads(line) for line in
                (work / "captures.jsonl")
                .read_text().splitlines() if line.strip()]
    bounded = {c["index"]: c for c in captures
               if c["mode"] == "chat-raw-bounded"}
    packages = {}
    decoder = json.JSONDecoder()
    for idx, cap in sorted(bounded.items()):
        if idx < 6:
            continue
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
            packages[idx - 5] = (package, chars)
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


def _presentation_hash_of_v2(package, working_set_hash):
    """The pointer-rule package's commitment, recomputed
    from the captured package itself: its tool results
    standing by their identities, its working set — the
    pointers — standing verbatim in the core, and the
    record set's own commitment hash beside it, exactly
    as the loop's pointer-form core derivation builds
    it."""
    core = copy.deepcopy(package)
    results = core.pop("tool_results", [])
    core["tool_result_refs"] = [
        {"dispatch_id": e.get("dispatch_id"),
         "request_id": e.get("request_id"),
         "outcome": e.get("outcome"),
         "event_seq": e.get("event_seq")}
        for e in results]
    core["working_set_hash"] = working_set_hash
    return sha256_hex(canonical(core))


def _all_strings(value):
    """Every string standing anywhere in a package —
    the content-once witness's net: a source's body
    counts as standing in a package only where the
    whole body stands as one value in it."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _all_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_strings(item)


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

        # ============ the third gate: length ========
        # (INDEX 557): the case declares the length a
        # delivery must reach; the door adjudicates a
        # contribution's sufficiency against it — last
        # in the family's order, after the stage gate
        # and the evidence gate.
        length_before = CHECKS[0]
        floor = rehearsal.DELIVERY_FLOOR["min_words"]

        def length_parts(scenario_work):
            evs = _events(scenario_work)
            gates = [_payload(e) for e in evs
                     if e["type"]
                     == "DELIVERY_LENGTH_GATE"]
            egates = [_payload(e) for e in evs
                      if e["type"]
                      == "DELIVERY_EVIDENCE_GATE"]
            sgates = [_payload(e) for e in evs
                      if e["type"]
                      == "DELIVERY_STAGE_GATE"]
            filings = [_payload(e) for e in evs
                       if e["type"] == "DELIVERABLE_FILED"]
            contribs = {e["event_seq"]: _payload(e)
                        for e in evs
                        if e["type"] == "CONTRIBUTION"}
            return evs, gates, egates, sgates, filings, \
                contribs

        check("length texts: the rehearsal's counted "
              "texts stand at exactly one under the "
              "floor and exactly at it, under the "
              "office's own count",
              len(rehearsal.LENGTH_TEXT_UNDER.split())
              == floor - 1
              and len(rehearsal.LENGTH_TEXT_AT.split())
              == floor,
              f"{len(rehearsal.LENGTH_TEXT_UNDER.split())}"
              f" / {len(rehearsal.LENGTH_TEXT_AT.split())}"
              f" of {floor}")

        # ---- the boundary: evidence standing, one
        # word under the floor gates; exactly at the
        # floor files.
        lgrep = reports["length_gate"]
        lgwork = work / "length-gate"
        check("length-gate: the generation seals the "
              "case's delivery-length declaration beside "
              "its evidence declaration",
              lgrep["sealed_delivery_floor"]
              == rehearsal.DELIVERY_FLOOR
              and lgrep["sealed_delivery_evidence"]
              == rehearsal.DELIVERY_EVIDENCE,
              f"{lgrep['sealed_delivery_floor']}")
        check("length-gate: the run completes on the "
              "resubmission, in eight iterations — the "
              "gate consuming exactly its own",
              lgrep["outcome"] == "yield"
              and lgrep["iterations"] == 8,
              f"{lgrep['outcome']} / {lgrep['iterations']}")
        _levs, lgates, legates, lsgates, lfilings, \
            lcontribs = length_parts(lgwork)
        check("length-gate: one length gate stands — "
              "549 words arrived against the 550 floor, "
              "nothing filed — and neither the evidence "
              "gate nor the stage gate fired (the "
              "evidence stood, the stage was the task's)",
              len(lgates) == 1
              and lgates[0].get("word_count") == floor - 1
              and lgates[0].get("min_words") == floor
              and lgates[0].get("filed") is False
              and legates == [] and lsgates == [],
              f"{lgates}")
        check("length-gate: the gate names its own "
              "contribution, whose text is the under-"
              "floor brief, by its hash",
              lcontribs.get(
                  lgates[0].get("contribution_seq"), {})
              .get("text") == rehearsal.LENGTH_TEXT_UNDER
              and lgates[0].get("text_sha256")
              == hashlib.sha256(
                  rehearsal.LENGTH_TEXT_UNDER
                  .encode("utf-8")).hexdigest(),
              f"{lgates}")
        check("length-gate: the only filing names the "
              "resubmission at exactly the floor — the "
              "gated contribution was never filed",
              len(lfilings) == 1
              and lfilings[0].get("contribution_seq")
              != lgates[0].get("contribution_seq")
              and lfilings[0].get("content_sha256")
              == hashlib.sha256(
                  rehearsal.LENGTH_TEXT_AT
                  .encode("utf-8")).hexdigest(),
              f"{lfilings}")
        lgpkgs = {k: v[0] for k, v in
                  _staged_packages(lgwork).items()}
        lgcorr = lgpkgs[8].get(
            "delivery_length_gate_correction") or {}
        check("length-gate: the correction rides the "
              "wake after the gate, naming both counts "
              "— what arrived and what is needed",
              lgcorr.get("word_count") == floor - 1
              and lgcorr.get("min_words") == floor
              and lgcorr.get("contribution_seq")
              == lgates[0].get("contribution_seq")
              and lgcorr.get("text_sha256")
              == lgates[0].get("text_sha256")
              and f"{floor - 1} words"
              in lgcorr.get("what_arrived", "")
              and f"{floor - 1} words"
              in lgcorr.get("instruction", "")
              and f"at least {floor} words"
              in lgcorr.get("instruction", ""),
              f"{lgcorr}")
        check("length-gate: no other wake carries the "
              "correction",
              all("delivery_length_gate_correction"
                  not in lgpkgs[k]
                  for k in lgpkgs if k != 8),
              f"{sorted(lgpkgs)}")
        check("length-gate: the floor is stated in his "
              "task before it can bite — the task stage's "
              "deliverable statement names the minimum, "
              "and no other stage's package states it",
              f"at least {floor} words"
              in (lgpkgs[4].get("task") or {}).get(
                  "delivery_floor", "")
              and all("task" not in lgpkgs[k]
                      for k in lgpkgs if k != 4),
              f"{lgpkgs[4].get('task')}")
        _check_commitments(
            "length-gate", lgwork, lgpkgs, 8)
        _check_checker("length-gate", lgrep)

        # ---- the order, from the evidence side: a
        # short contribution with evidence missing is
        # the evidence gate's, not the length gate's.
        loerep = reports["length_order_evidence"]
        loework = work / "length-order-evidence"
        check("length-order-evidence: the run "
              "completes in nine iterations — each gate "
              "consuming exactly its own",
              loerep["outcome"] == "yield"
              and loerep["iterations"] == 9,
              f"{loerep['outcome']} / "
              f"{loerep['iterations']}")
        _loeevs, loelgates, loeegates, loesgates, \
            loefilings, loecontribs = length_parts(
                loework)
        short_count = len(
            rehearsal.EVIDENCE_BRIEF_TEXT.split())
        check("length-order-evidence: the first short "
              "contribution — evidence missing — drew "
              "the evidence gate alone; the same brief "
              "with the evidence standing drew the "
              "length gate, in that order",
              len(loeegates) == 1
              and loeegates[0].get("missing") == addresses
              and len(loelgates) == 1
              and loelgates[0].get("word_count")
              == short_count
              and loelgates[0].get("contribution_seq")
              != loeegates[0].get("contribution_seq")
              and loesgates == []
              and len(loefilings) == 1
              and loefilings[0].get("contribution_seq")
              not in (
                  loeegates[0].get("contribution_seq"),
                  loelgates[0].get("contribution_seq")),
              f"evidence {loeegates} / length {loelgates}")
        loepkgs = {k: v[0] for k, v in
                   _staged_packages(loework).items()}
        check("length-order-evidence: the evidence "
              "correction rides wake 5 and the length "
              "correction wake 9 — each gate's answer at "
              "its own next wake, neither standing in "
              "for the other",
              "delivery_evidence_gate_correction"
              in loepkgs[5]
              and "delivery_length_gate_correction"
              not in loepkgs[5]
              and "delivery_length_gate_correction"
              in loepkgs[9]
              and loepkgs[9][
                  "delivery_length_gate_correction"]
              .get("word_count") == short_count,
              f"{sorted(loepkgs)}")
        _check_commitments(
            "length-order-evidence", loework, loepkgs, 9)
        _check_checker("length-order-evidence", loerep)

        # ---- the order, from the stage side: a short
        # contribution before the task is the stage
        # gate's, not the length gate's.
        losrep = reports["length_order_stage"]
        loswork = work / "length-order-stage"
        check("length-order-stage: the run completes "
              "in seven iterations — the stage gate "
              "consuming exactly its own",
              losrep["outcome"] == "yield"
              and losrep["iterations"] == 7,
              f"{losrep['outcome']} / "
              f"{losrep['iterations']}")
        _losevs, loslgates, losegates, lossgates, \
            losfilings, loscontribs = length_parts(
                loswork)
        check("length-order-stage: the short "
              "contribution at the files stage drew the "
              "stage gate alone — no evidence gate, no "
              "length gate stands for it — and the "
              "at-floor contribution filed",
              len(lossgates) == 1
              and lossgates[0].get("stage") == "files"
              and loslgates == [] and losegates == []
              and len(losfilings) == 1
              and losfilings[0].get("contribution_seq")
              != lossgates[0].get("contribution_seq"),
              f"stage {lossgates} / length {loslgates}")
        lospkgs = {k: v[0] for k, v in
                   _staged_packages(loswork).items()}
        check("length-order-stage: the stage correction "
              "rides wake 4, and no wake carries a "
              "length correction",
              "delivery_stage_gate_correction"
              in lospkgs[4]
              and all(
                  "delivery_length_gate_correction"
                  not in lospkgs[k] for k in lospkgs),
              f"{sorted(lospkgs)}")
        _check_commitments(
            "length-order-stage", loswork, lospkgs, 7)
        _check_checker("length-order-stage", losrep)

        # ---- the control: no floor declared — the
        # evidence scenarios' short brief files exactly
        # as it always has, and scenario G's record
        # holds no length gate either.
        _ewevs, ewlgates, _ewegates, _ewsgates, \
            ewfilings2, _ewcontribs = length_parts(
                ewwork)
        check("length control: with no floor declared, "
              "the evidence-whole run seals none, holds "
              "no length gate, and its short brief — "
              "well under any floor — files exactly as "
              "it always has",
              ewrep["sealed_delivery_floor"] is None
              and ewlgates == []
              and len(ewfilings2) == 1
              and ewfilings2[0].get("content_sha256")
              == hashlib.sha256(
                  rehearsal.EVIDENCE_BRIEF_TEXT
                  .encode("utf-8")).hexdigest()
              and len(rehearsal.EVIDENCE_BRIEF_TEXT
                      .split()) < floor,
              f"{ewlgates}")
        _s2evs, slgates, _segates, _ssgates, \
            _sfilings2, _scontribs2 = length_parts(swork)
        check("length control: the staged run seals no "
              "length declaration and no length gate "
              "stands in its record",
              reports["staged"][
                  "sealed_delivery_floor"] is None
              and slgates == [],
              f"{slgates}")
        print(f"delivery-length section: "
              f"{CHECKS[0] - length_before} checks")

        # ============ pointer rule ===================
        # INDEX 568 (Ben's tap, 2026-11-25): the staged
        # walk under the successor presentation contract.
        # The witnesses: the seal names v2 while the v1
        # control in the same rehearsal seals v1 exactly
        # as it always has; the stages walk in order with
        # the standing furniture standing (snapshot,
        # ways in, worked example, menu); the working set
        # stands as pointers at every wake — no content
        # key anywhere in it — each pointer carrying its
        # address, hash, size, gathering step, way back
        # in and sentence, its hash the one its outcome
        # event recorded; each source's content stands
        # in exactly one package (the wake after its
        # gather) as a newest result — twice for the
        # first source, whose re-pull is its second
        # gather — and in no other, save the second
        # source, whose content also stands at the
        # files stage as the calibration's worked
        # example (the office's demonstration read,
        # witnessed below); the fully-gathered
        # dashboard wake renders under the stated bound;
        # every iteration's presentation commitment is
        # the hash of the pointer-form core of the very
        # package its captured wake presented; the
        # evidence gate files on the record while the
        # contents stand in no current package; the
        # checker stands eleven, all ok, deriving the
        # pointer form independently.
        pointer_before = CHECKS[0]
        prep = reports["pointer"]
        pwork = work / "pointer"
        check("pointer: the run ends in nine "
              "iterations — the four onboarding stages, "
              "then five dashboard wakes — with the "
              "yield the door's completion carries",
              prep["outcome"] == "yield"
              and prep["iterations"] == 9,
              f"{prep['outcome']} / {prep['iterations']}")
        check("pointer: the sealed record declares "
              "the pointer-rule presentation contract "
              "beside the working-set contract",
              prep["sealed_presentation_contract"]
              == "staged-onboarding-v2"
              and prep["sealed_working_set_contract"]
              == tool_policy.WORKING_SET_CONTRACT,
              f"{prep['sealed_presentation_contract']} / "
              f"{prep['sealed_working_set_contract']}")
        check("pointer: the control stands in the same "
              "rehearsal — the staged generation seals "
              "v1 exactly as it always has, its meaning "
              "under its name unchanged",
              reports["staged"][
                  "sealed_presentation_contract"]
              == "staged-onboarding-v1",
              "staged sealed presentation: "
              + str(reports["staged"][
                  "sealed_presentation_contract"]))
        ppackages = _staged_packages(pwork)
        check("pointer: ten chat captures (identify + "
              "nine iterations), each carrying a staged "
              "package",
              sorted(ppackages)
              == [1, 2, 3, 4, 5, 6, 7, 8, 9],
              f"{sorted(ppackages)}")
        ppkgs = {k: v[0] for k, v in ppackages.items()}
        psizes = {k: v[1] for k, v in ppackages.items()}
        print(f"pointer package sizes (rendered "
              f"chars): {psizes}")
        pstages = [(ppkgs[k].get("presentation") or {})
                   .get("stage")
                   for k in range(1, 10)]
        check("pointer: the stages walk in order — "
              "memory, case, files, task, then dashboard "
              "wakes — and every package names the "
              "pointer-rule contract as its own",
              pstages == ["memory", "case", "files",
                          "task", "dashboard", "dashboard",
                          "dashboard", "dashboard",
                          "dashboard"]
              and all((ppkgs[k].get("presentation")
                       or {}).get("contract")
                      == "staged-onboarding-v2"
                      for k in ppkgs),
              f"{pstages}")
        check("pointer: no package carries the case "
              "dump, the view or the delta",
              all("case" not in p and "view" not in p
                  and "delta" not in p
                  for p in ppkgs.values()))
        check("pointer: every stage package stands "
              "within the standing budgets (memory "
              "< 8,000; case < 9,000; files < 24,000; "
              "task < 22,000 rendered chars) — the "
              "files stage's bound is the population's "
              "standing maximum package bound, the "
              "dashboard bound: under the calibration "
              "the stage carries the worked example as "
              "a whole real read, the one stage that "
              "shows a whole file, and it stands within "
              "the bound the dashboard wakes already "
              "observe",
              psizes.get(1, 10 ** 9) < 8000
              and psizes.get(2, 10 ** 9) < 9000
              and psizes.get(3, 10 ** 9) < 24000
              and psizes.get(4, 10 ** 9) < 22000,
              f"{psizes}")
        check("pointer: the files stage's "
              "introduction tells the pointer truth — "
              "a pull is shown whole in the wake right "
              "after it and stands as a pointer after; "
              "the carried-forward promise stands "
              "nowhere in it",
              "shown to you whole in the wake right "
              "after you pull it" in ppkgs[3]["files"][
                  "introduction"]
              and "carried forward" not in ppkgs[3][
                  "files"]["introduction"])
        check("pointer: the dashboard direction names "
              "pointers to everything gathered, not the "
              "gatherings themselves",
              "pointers to everything you have "
              "gathered so far" in ppkgs[9][
                  "presentation"]["direction"])
        check("pointer: stage 1's snapshot carries "
              "the opening record's settled results "
              "verbatim, and the memory is the case's "
              "role memory exactly",
              ppkgs[1].get("snapshot", {}).get("settled")
              == ["No work product is produced in "
                  "the opening; the work happens in "
                  "the room."]
              and ppkgs[1]["memory"]["entries"]
              == ROLE_MEMORY)
        check("pointer: no tools are offered at the "
              "memory or case stages — the offer opens "
              "at the files stage",
              "tools" not in ppkgs[1]
              and "tools" not in ppkgs[2]
              and "tools" in ppkgs[3])
        check("pointer: stage 3's briefcase is the "
              "glossary's pointers, each with its way "
              "in; the journal stands as its pointer; "
              "and the worked example stands — the "
              "office's real read call on the smallest "
              "file in the map (the calibration: the "
              "demonstration is the pull his job is "
              "made of, on the file whose whole content "
              "keeps the stage within its bound)",
              [e["address"] for e in
               ppkgs[3]["files"]["briefcase"]]
              == [e["address"] for e in GLOSSARY]
              and all("access" in e for e in
                      ppkgs[3]["files"]["briefcase"])
              and ppkgs[3]["files"]["journal"]["path"]
              == "scratch/journal.md"
              and ppkgs[3]["files"]["worked_example"][
                  "call"] == {
                      "tool": "sandbox.read",
                      "parameters": {
                          "path": "sources/a3-pass.md"}})
        pexample = ppkgs[3]["files"]["worked_example"]
        check("pointer: the presented example is the "
              "sealed record's own — the loop presents "
              "the seal, not a reconstruction of it",
              pexample.get("result")
              == (prep.get("sealed_worked_example")
                  or {}).get("result")
              and (prep.get("sealed_worked_example")
                   or {}).get("tool") == "sandbox.read"
              and (prep.get("sealed_worked_example")
                   or {}).get("path")
              == "sources/a3-pass.md",
              f"{prep.get('sealed_worked_example')}")
        # The example is REAL: recompute the read from
        # the staged file's raw bytes, here,
        # independently of the framework, and compare
        # whole — the content itself, its byte count
        # and its hash. The choice of file is
        # recomputed too: the smallest of the map's
        # staged files.
        praw = {e["address"]: (pwork / "run" / "sandbox"
                               / e["address"]).read_bytes()
                for e in GLOSSARY
                if (pwork / "run" / "sandbox"
                    / e["address"]).is_file()}
        pchosen = min(praw, key=lambda a: len(praw[a]))
        check("pointer: the worked example's result "
              "is the staged file's real read — "
              "recomputed from its raw bytes in this "
              "witness, not trusted from the seal — and "
              "the file it names is the map's smallest, "
              "recomputed from the staged bytes",
              pchosen == "sources/a3-pass.md"
              and pexample["result"].get("content")
              == praw[pchosen].decode("utf-8")
              and pexample["result"].get("content_bytes")
              == len(praw[pchosen])
              and pexample["result"].get("content_sha256")
              == hashlib.sha256(praw[pchosen]).hexdigest()
              and pexample["result"].get("authority_path")
              == "source",
              "chosen: " + pchosen)
        check("pointer: the room-proof line stands "
              "beside the worked example — the example "
              "is a real call made in his room, and his "
              "tools answer the same way in the shape "
              "shown",
              pexample.get("proof") == (
                  "This example is a real call the "
                  "office made in your room, on a file "
                  "from your own briefcase; your tools "
                  "answer the same way when you call "
                  "them in the shape shown."),
              f"{pexample.get('proof')}")
        check("pointer: stage 3's journal pointer "
              "carries the journal's contract (the "
              "calibration) — after each file you read, "
              "log its name and the key points you took "
              "from it, in one or two plain lines; the "
              "office reads it at every wake to resume "
              "you; the director may audit it; nothing "
              "parses it",
              ppkgs[3]["files"]["journal"]["label"] == (
                  "your journal — your notebook: notes, "
                  "decisions, where you left off. Yours "
                  "to write and rewrite; orientation, "
                  "not record and not memory. Keep it as "
                  "you work: after each file you read, "
                  "log its name and the key points you "
                  "took from it, in one or two plain "
                  "lines. The office reads your journal "
                  "at every wake to resume you, and the "
                  "director may audit it; nothing parses "
                  "it — it is read as you wrote it. Its "
                  "contents are not carried in your "
                  "packages — pull it when you want "
                  "it."),
              f"{ppkgs[3]['files']['journal']['label']}")
        check("pointer: stage 4 carries the "
              "assignment text and the phase-grouped "
              "menu — Gather, Compose, Deliver",
              ppkgs[4]["task"]["assignment"]
              == ASSIGNMENT_COMBINED
              and [g["phase"] for g in
                   ppkgs[4]["tool_list"]]
              == ["Gather", "Compose", "Deliver"])
        check("pointer: dashboard wakes carry the "
              "five pointers back into the briefcase",
              all([p["item"] for p in ppkgs[k]["pointers"]]
                  == ["your memory", "your case",
                      "your files", "your journal",
                      "your task"]
                  for k in (5, 6, 7, 8, 9)))
        pevs = _events(pwork)
        poutcomes = {e["event_seq"]: _payload(e)
                     for e in pevs
                     if e["type"] == "TOOL_OUTCOME"}
        check("pointer: no working-set entry in any "
              "package carries a content key — the set "
              "is pointers at every wake, including the "
              "first",
              all("content" not in entry
                  for k in ppkgs
                  for entry in (ppkgs[k].get("working_set")
                                or {}).get("entries")
                  or []))
        ws9 = ppkgs[9]["working_set"]
        entries9 = ws9.get("entries") or []
        check("pointer: at the final wake the working "
              "set stands as five pointers — the files "
              "stage's listing, the three whole reads, "
              "and the second listing — under the "
              "pointer note, its budget and carried "
              "figures keeping their record meanings "
              "(the sum of the entries' carried bytes)",
              len(entries9) == 5
              and ws9.get("note", "").startswith(
                  "What you have gathered so far, "
                  "standing as pointers")
              and ws9.get("budget_bytes") == BUDGET
              and ws9.get("content_bytes") == sum(
                  e["content_bytes"] for e in entries9)
              and all(e["content_carried"]
                      for e in entries9),
              f"{len(entries9)} entries; content_bytes "
              f"{ws9.get('content_bytes')}")
        check("pointer: the re-pull added no second "
              "entry — at the wake after it the set "
              "still stands at four pointers (the "
              "gather dedupes on the record, pointers "
              "or not)",
              len((ppkgs[8].get("working_set") or {})
                  .get("entries") or []) == 4)
        reads9 = {e["path"]: e for e in entries9
                  if e["tool"] == "sandbox.read"}
        source_facts = {
            "sources/stock-take.md": (
                STOCK_TAKE_SHA256, 4),
            "sources/a3-pass.md": (
                A3_PASS_SHA256, 5),
            "sources/index-tail.md": (
                INDEX_TAIL_SHA256, 6)}
        bodies = {}
        for path, (sha, _step) in source_facts.items():
            bodies[path] = (pwork / "run" / "sandbox"
                            / path).read_bytes() \
                .decode("utf-8")
            entry = reads9.get(path) or {}
            check(f"pointer: the {path} pointer "
                  f"carries its address, hash, size and "
                  f"lines exactly as the record stands",
                  entry.get("content_sha256") == sha
                  and entry.get("content_bytes")
                  == len(bodies[path].encode("utf-8"))
                  and entry.get("line_count")
                  == len(bodies[path].splitlines())
                  and entry.get("authority_path")
                  == "source",
                  f"{entry.get('content_sha256')} / "
                  f"{entry.get('content_bytes')} / "
                  f"{entry.get('line_count')}")
            check(f"pointer: the {path} pointer names "
                  f"the step that gathered it, its way "
                  f"back in, and its sentence — the "
                  f"material in his room at that "
                  f"address, the pull named, the "
                  f"office's record standing regardless",
                  entry.get("gathered_step") == _step
                  and entry.get("access") == {
                      "tool": "sandbox.read",
                      "parameters": {"path": path}}
                  and entry.get("note") == (
                      f"It stands in your room at "
                      f"{path} — pull it again with "
                      f"sandbox.read on that address "
                      f"when you need its words in "
                      f"front of you; the office's "
                      f"record of your having read it "
                      f"stands regardless of what any "
                      f"later package carries."),
                  f"step {entry.get('gathered_step')}")
        check("pointer: every pointer's hash and "
              "dispatch are the ones its outcome event "
              "recorded — the pointers verify against "
              "the record, entry by entry",
              all(poutcomes.get(e["outcome_event_seq"],
                                {}).get("result", {})
                  .get("content_sha256")
                  == e["content_sha256"]
                  and poutcomes.get(
                      e["outcome_event_seq"], {})
                  .get("dispatch_id")
                  == e["dispatch_id"]
                  for k in ppkgs
                  for e in (ppkgs[k].get("working_set")
                            or {}).get("entries") or []))
        listings9 = {e["path"]: e for e in entries9
                     if e["tool"] == "sandbox.list"}
        check("pointer: the two listing pointers "
              "carry the listed files' line counts "
              "from the record — a listing's pointer "
              "names the shape it showed",
              listings9.get("sources/stock-take.md", {})
              .get("line_count")
              == len(bodies["sources/stock-take.md"]
                     .splitlines())
              and listings9.get("sources/stock-take.md",
                                {}).get("gathered_step")
              == 3
              and listings9.get("sources/a3-pass.md", {})
              .get("line_count")
              == len(bodies["sources/a3-pass.md"]
                     .splitlines())
              and listings9.get("sources/a3-pass.md", {})
              .get("gathered_step") == 8)
        expected_standings = {
            "sources/stock-take.md": [5, 8],
            "sources/index-tail.md": [7]}
        for path, expected in expected_standings.items():
            standings = [k for k in range(1, 10)
                         if bodies[path] in set(
                             _all_strings(ppkgs[k]))]
            check(f"pointer: {path}'s content stands "
                  f"in exactly the wake after its "
                  f"gather"
                  + (" and the wake after its re-pull"
                     if len(expected) == 2 else "")
                  + " — as a newest result each time, "
                  "and in no other package",
                  standings == expected
                  and all(any(
                      (te.get("result") or {})
                      .get("content") == bodies[path]
                      for te in ppkgs[k]["tool_results"])
                      for k in expected),
                  f"standings {standings}")
        check("pointer: the second source's content "
              "stands in exactly two packages — the "
              "files stage, as the office's worked "
              "example (the calibration's demonstration "
              "read, labelled the office's example and "
              "never entering his working set), and the "
              "wake after his own gather of it, as his "
              "newest result — and in no other package",
              [k for k in range(1, 10)
               if bodies["sources/a3-pass.md"] in set(
                   _all_strings(ppkgs[k]))] == [3, 6]
              and ppkgs[3]["files"]["worked_example"][
                  "result"]["content"]
              == bodies["sources/a3-pass.md"]
              and any(
                  (te.get("result") or {}).get("content")
                  == bodies["sources/a3-pass.md"]
                  for te in ppkgs[6]["tool_results"])
              and all(
                  bodies["sources/a3-pass.md"] not in
                  json.dumps(ppkgs[k].get("working_set")
                             or {})
                  for k in range(1, 10)),
              "a3-pass standings")
        check("pointer: the fully-gathered dashboard "
              "wake — all three sources gathered, "
              "standing as pointers, only a small "
              "listing in the newest results — renders "
              "under 24,000 chars: the standing "
              "dashboard furniture bound (14,000) plus "
              "five pointers and the listing, nearer "
              "the task stage's ~20,000 than the "
              "85,862 bytes the full-set wake measured "
              "on the live wire",
              psizes.get(9, 10 ** 9) < 24000,
              f"{psizes}")
        recorded_ph = {}
        recorded_ws = {}
        for e in pevs:
            if e["type"] == "LOOP_ITERATION":
                p = _payload(e)
                recorded_ph[p.get("iteration")] = \
                    p.get("presentation_hash")
                recorded_ws[p.get("iteration")] = \
                    p.get("working_set_hash")
        check("pointer: every LOOP_ITERATION carries "
              "both commitments — the presentation "
              "hash and the record working set's hash",
              len(recorded_ph) == 9
              and all(isinstance(h, str) and len(h) == 64
                      for h in recorded_ph.values())
              and all(isinstance(h, str) and len(h) == 64
                      for h in recorded_ws.values()),
              f"{recorded_ph}")
        for k in range(1, 10):
            check(f"pointer: iteration {k}'s "
                  f"presentation commitment is the hash "
                  f"of the pointer-form core of the "
                  f"package its captured wake presented "
                  f"— the pointers verbatim, the record "
                  f"set's hash beside them",
                  recorded_ph.get(k)
                  == _presentation_hash_of_v2(
                      ppkgs[k], recorded_ws.get(k)),
                  f"recorded={recorded_ph.get(k)}")
        pfilings = [_payload(e) for e in pevs
                    if e["type"] == "DELIVERABLE_FILED"]
        check("pointer: the assignment completes "
              "through the door — one filing, authored "
              "by the worker, filed by the office, at "
              "the declared destination, its hash the "
              "contribution's — adjudicated while the "
              "three sources' contents stand in no "
              "current package: the evidence gate read "
              "the record, not the package",
              len(pfilings) == 1
              and pfilings[0].get("destination")
              == "scratch/brief.md"
              and pfilings[0].get("authored_by")
              == "crew-1"
              and pfilings[0].get("filed_by") == "office"
              and pfilings[0].get("content_sha256")
              == hashlib.sha256(
                  rehearsal.EVIDENCE_BRIEF_TEXT
                  .encode("utf-8")).hexdigest()
              and not any(bodies[path] in set(
                  _all_strings(ppkgs[9]))
                  for path in bodies),
              f"{pfilings}")
        check("pointer: no evidence gate event "
              "stands in the record — the delivery "
              "stood the first time it was offered",
              not any(e["type"]
                      == "DELIVERY_EVIDENCE_GATE"
                      for e in pevs))
        pfiled = (pwork / "run" / "sandbox" / "scratch"
                  / "brief.md")
        check("pointer: the filed brief stands in "
              "the sandbox at the declared "
              "destination, verbatim",
              pfiled.exists()
              and pfiled.read_text(encoding="utf-8")
              == rehearsal.EVIDENCE_BRIEF_TEXT,
              f"{pfiled}")
        _check_checker("pointer", prep)
        print(f"pointer-rule section: "
              f"{CHECKS[0] - pointer_before} checks")

        # ============ the calibration =================
        # The GPT-OSS worker's debrief as blueprint
        # (INDEX 571; Ben's direction, 2026-11-25):
        # the tool-shape gate and the number where he
        # plans, witnessed over the two scenarios above.
        # In the first, the stand-in's native reach at
        # the task stage meets the provider's refusal
        # body — HTTP 400's shape, code tool_use_failed,
        # the failed generation preserved — and the
        # refusal becomes a gate: its event stands in
        # the record with what arrived verbatim, the
        # next wake's package carries the correction
        # byte-exact (what arrived, what is needed, one
        # concrete well-formed example, the
        # instruction), the iteration is consumed, and
        # the run continues to a filed brief. In the
        # second, the same position meets a rate-limit
        # refusal: no gate event, no correction, the
        # stall a provider failure exactly as before —
        # the gate's narrowness witnessed beside its
        # firing. The task stage's deliverable statement
        # carries the figures before any refusal can.
        calibration_before = CHECKS[0]
        trep = reports["toolshape"]
        twork = work / "toolshape"
        check("calibration: the tool-shape run "
              "completes in six iterations — the four "
              "onboarding stages, the gate's consumed "
              "iteration among them, and the delivery — "
              "with the yield the door's completion "
              "carries",
              trep["outcome"] == "yield"
              and trep["iterations"] == 6,
              f"{trep['outcome']} / {trep['iterations']}")
        tpackages = _staged_packages(twork)
        tpkgs = {k: v[0] for k, v in tpackages.items()}
        check("calibration: the task stage's "
              "deliverable statement states the figures "
              "before any refusal can — about 600 "
              "words; the door will not file a brief "
              "under 550 words",
              tpkgs[4]["task"].get("delivery_floor") == (
                  "The brief runs to about 600 words, "
                  "and the door will not file a brief "
                  "under 550 words. A contribution "
                  "shorter than that is set aside "
                  "unfiled, and you will be told the "
                  "count yours arrived with."),
              f"{tpkgs[4]['task'].get('delivery_floor')}")
        tevs = _events(twork)
        tgates = [_payload(e) for e in tevs
                  if e["type"] == "TOOL_SHAPE_GATE"]
        titer4 = [e["event_seq"] for e in tevs
                  if e["type"] == "LOOP_ITERATION"
                  and _payload(e).get("iteration") == 4]
        check("calibration: exactly one tool-shape "
              "gate event stands in the record, bound "
              "to the task-stage iteration, carrying "
              "what arrived verbatim — the refusal's "
              "code and message, the tool the failed "
              "generation named, and the failed "
              "generation itself, preserved whole; the "
              "seam observed no status, and none is "
              "claimed",
              len(tgates) == 1
              and len(titer4) == 1
              and tgates[0].get("iteration_seq")
              == titer4[0]
              and tgates[0].get("tool_name")
              == "container.exec"
              and tgates[0].get("error_code")
              == "tool_use_failed"
              and tgates[0].get("error_message") == (
                  "Tool choice is none, but model "
                  "called a tool")
              and tgates[0].get("failed_generation")
              == rehearsal.TOOLSHAPE_FAILED_GENERATION
              and tgates[0].get("http_status") is None,
              f"{tgates}")
        expected_correction = {
            "what_arrived": (
                "a native tool call — your answer "
                "named container.exec in the provider's "
                "own tool-call shape, and the provider "
                "refused the whole answer for it (its "
                "refusal carries the code "
                "tool_use_failed). No tool ran, and "
                "nothing from that answer was carried "
                "out"),
            "what_is_needed": (
                "In this room your tools are called in "
                "the text shape: your answer is one "
                "JSON object whose outcome is "
                "\"tool_requests\", with a requests "
                "list naming each call — the tool's "
                "name and its parameters — as the "
                "example shows. Only calls in that "
                "shape reach your tools; a native tool "
                "call cannot be carried out here."),
            "example": {
                "outcome": "tool_requests",
                "requests": [{
                    "tool": "sandbox.read",
                    "parameters": {
                        "path": "sources/stock-take.md"}}]},
            "instruction": (
                "Nothing was filed, and nothing was "
                "lost: your gathered work stands as it "
                "stood. Make the call again in the text "
                "shape and carry on with the job. The "
                "refusal cost this one step and nothing "
                "else.")}
        check("calibration: the wake after the gate "
              "carries the correction byte-exact — what "
              "arrived (the native call, named), what "
              "is needed (the text shape), one concrete "
              "well-formed tool_requests example for a "
              "read of the first glossary file, and the "
              "instruction — and no other package "
              "carries it",
              tpkgs[5].get("tool_shape_gate_correction")
              == expected_correction
              and all(
                  "tool_shape_gate_correction" not in
                  tpkgs[k]
                  for k in tpkgs if k != 5),
              f"{tpkgs[5].get('tool_shape_gate_correction')}")
        tfilings = [_payload(e) for e in tevs
                    if e["type"] == "DELIVERABLE_FILED"]
        tfiled = (twork / "run" / "sandbox" / "scratch"
                  / "brief.md")
        check("calibration: the run continues past "
              "the gate to a filed brief — one filing "
              "at the declared destination, the brief "
              "standing verbatim in the sandbox, its "
              "length over the floor the task stage "
              "stated",
              len(tfilings) == 1
              and tfilings[0].get("destination")
              == "scratch/brief.md"
              and tfiled.exists()
              and tfiled.read_text(encoding="utf-8")
              == rehearsal.TOOLSHAPE_BRIEF_TEXT
              and len(rehearsal.TOOLSHAPE_BRIEF_TEXT
                      .split()) >= 550,
              f"{tfilings}")
        _check_checker("toolshape", trep)
        rrep = reports["toolshape_refused"]
        rwork = work / "toolshape-refused"
        revs = _events(rwork)
        rstalls = [_payload(e) for e in revs
                   if e["type"] == "LOOP_STALLED"]
        rpackages = _staged_packages(rwork)
        check("calibration: the rate-limit refusal "
              "is not the gate's business — the run "
              "stalls at the task stage as a provider "
              "failure, no tool-shape gate event stands "
              "in its record, and no package carries a "
              "tool-shape correction",
              rrep["outcome"] == "stalled"
              and rrep["iterations"] == 4
              and len(rstalls) == 1
              and rstalls[0].get("ground")
              == "provider_failure"
              and not any(e["type"] == "TOOL_SHAPE_GATE"
                          for e in revs)
              and all(
                  "tool_shape_gate_correction" not in pkg
                  for pkg, _size in
                  rpackages.values()),
              f"{rrep['outcome']} / {rstalls}")
        _check_checker("toolshape-refused", rrep)
        print(f"calibration section: "
              f"{CHECKS[0] - calibration_before} checks")

        # ============= process tree (the room rebuild)
        # The process-tree contract's witnesses (Ben's
        # "Make it so", 2026-11-25): one opening package
        # and no acknowledge wakes; the tree walked one
        # step at a time, each step's content presented
        # exactly once at its step; the step gate
        # correcting work that runs ahead; the batch
        # shape held to one step of presentation; and
        # the native lane on the corrected Groq
        # transport. The per-package bound stated for
        # these packages — the package JSON as the
        # prompt presented it, plus the catalogue
        # section the adapter renders from it, the
        # staged sections' own measure — is 64,000
        # rendered chars: the largest honest package,
        # the index-tail gather step of tree-honest
        # (its 40,953-byte content plus the tree, the
        # journal, the step and the catalogue
        # furniture), measures 61,955.
        tree_before = CHECKS[0]
        TREE_BOUND = 64000
        G1 = "gather:sources/stock-take.md"
        G2 = "gather:sources/a3-pass.md"
        G3 = "gather:sources/index-tail.md"

        # ---- tree-honest: the honest path ----
        trep = reports["tree_honest"]
        twork = work / "tree-honest"
        tevs = _events(twork)
        tpkg = _staged_packages(twork)
        check("tree-honest: the run completes in "
              "seven iterations — opening, three "
              "gather steps at two wakes each (the "
              "step, then its content), compose — and "
              "the brief stands filed",
              trep["outcome"] == "yield"
              and trep["iterations"] == 7
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in tevs),
              f"{trep['outcome']} / {trep['iterations']}")
        check("tree-honest: the sealed record "
              "declares the process-tree presentation "
              "contract, and no worked example stands "
              "in the seal (the tree's first gather "
              "step is the demonstration's replacement)",
              trep["sealed_presentation_contract"]
              == "process-tree-v1"
              and trep["sealed_worked_example"] is None,
              f"{trep['sealed_presentation_contract']}")
        check("tree-honest: seven packages stand in "
              "the captures — the first the opening, "
              "the rest step packages, every one under "
              "the process-tree contract",
              sorted(tpkg) == [1, 2, 3, 4, 5, 6, 7]
              and tpkg[1][0]["presentation"]["package"]
              == "opening"
              and all(
                  tpkg[k][0]["presentation"]["package"]
                  == "step"
                  and tpkg[k][0]["presentation"]
                  ["contract"] == "process-tree-v1"
                  for k in range(2, 8)),
              f"{sorted(tpkg)}")
        opening = tpkg[1][0]
        check("tree-honest: the opening package "
              "carries the whole of it once — his "
              "memory, the case essentials, the files "
              "map, the sealed tree, the tool "
              "catalogue, the journal with its "
              "contract — and his first response is "
              "work: the first request the record "
              "stands is the first gather step's read, "
              "no acknowledge outcome anywhere",
              all(k in opening for k in (
                  "memory", "case_essentials", "files",
                  "process_tree", "tools", "journal",
                  "current_step"))
              and opening["current_step"]["node"]
              == "orient"
              and len(opening["tools"]) == 10
              and [p.get("tool") for p in
                   (_payload(e) for e in tevs
                    if e["type"] == "TOOL_REQUESTED")
                   ][:1] == ["sandbox.read"]
              and not any(
                  e["type"] == "TOOL_REQUESTED"
                  and _payload(e).get("tool")
                  not in ("sandbox.read", "sandbox.write")
                  for e in tevs),
              f"{sorted(opening)}")
        currents = [tpkg[k][0]["current_step"]["node"]
                    for k in range(1, 8)]
        check("tree-honest: the walk's current steps "
              "in order — orient, then each gather "
              "step twice (the step's wake, then its "
              "content's wake), then compose",
              currents == ["orient", G1, G2, G2, G3, G3,
                           "compose"],
              f"{currents}")
        states2 = {n["id"]: n["state"] for n in
                   tpkg[2][0]["process_tree"]["nodes"]}
        states7 = {n["id"]: n["state"] for n in
                   tpkg[7][0]["process_tree"]["nodes"]}
        check("tree-honest: the tree's node states "
              "derive from the record — at the first "
              "gather step orient stands done and the "
              "rest pending; at compose every gather "
              "stands done and deliver pending",
              states2.get("orient") == "done"
              and states2.get(G1) == "current"
              and states2.get(G2) == "pending"
              and states7.get(G1) == "done"
              and states7.get(G2) == "done"
              and states7.get(G3) == "done"
              and states7.get("compose") == "current"
              and states7.get("deliver") == "pending",
              f"{states2} / {states7}")
        bodies = {}
        for name in ("stock-take", "a3-pass",
                     "index-tail"):
            bodies[name] = (twork / "run" / "sandbox"
                            / "sources"
                            / f"{name}.md") \
                .read_bytes().decode("utf-8")
        homes = {"stock-take": 2, "a3-pass": 4,
                 "index-tail": 6}
        for name, home in homes.items():
            standing = [k for k in range(1, 8)
                        if bodies[name] in list(
                            _all_strings(tpkg[k][0]))]
            check(f"tree-honest: {name}'s whole body "
                  f"stands in exactly one package — "
                  f"its own step's content package "
                  f"(package {home}) — and as pointers "
                  f"everywhere else",
                  standing == [home],
                  f"standing in {standing}")
        check("tree-honest: the journal rides every "
              "package verbatim, growing by exactly "
              "the step's bits — empty at the first "
              "gather step, the first note at the "
              "second, two at the third, all three at "
              "compose",
              tpkg[2][0]["journal"]["content"] == ""
              and tpkg[3][0]["journal"]["content"]
              == rehearsal.TREE_NOTE_1
              and tpkg[5][0]["journal"]["content"]
              == rehearsal.TREE_NOTE_1
              + rehearsal.TREE_NOTE_2
              and tpkg[7][0]["journal"]["content"]
              == rehearsal.TREE_NOTE_1
              + rehearsal.TREE_NOTE_2
              + rehearsal.TREE_NOTE_3)
        compose_step = tpkg[7][0]["current_step"]
        check("tree-honest: the compose package "
              "carries the figures and the four "
              "points and the compile-from-your-"
              "journal instruction, and no source "
              "content rides it (the content-once "
              "checks above stand over it too)",
              "600" in compose_step.get("figures", "")
              and compose_step.get("points") == [
                  "what this framework is",
                  "what has actually been proven",
                  "what has not been proven",
                  "what remains to be built"]
              and "journal entries" in compose_step
              .get("instruction", ""),
              f"{compose_step.get('figures')}")
        filed = (twork / "run" / "sandbox" / "scratch"
                 / "brief.md").read_text()
        check("tree-honest: the filed brief is the "
              "contributed text, at the tree's root",
              filed == rehearsal._tree_deliverable_text()
              and any(
                  e["type"] == "DELIVERABLE_FILED"
                  and _payload(e).get("destination")
                  == "scratch/brief.md" for e in tevs))
        check("tree-honest: no step gate stands in "
              "the honest record — the correction "
              "answers work ahead of the current "
              "step, and the honest walk has none",
              not any(e["type"] == "STEP_GATE"
                      for e in tevs))
        sizes = {k: size for k, (_p, size)
                 in tpkg.items()}
        check("tree-honest: every package stands "
              "under the stated bound of 64,000 "
              "rendered chars, and the largest is "
              "the index-tail step's content package",
              all(s <= TREE_BOUND for s in sizes.values())
              and max(sizes, key=sizes.get) == 6,
              f"{sizes}")
        print(f"tree-honest package sizes (rendered "
              f"chars): {sizes}")
        _check_checker("tree-honest", trep)

        # ---- tree-journal-gate: the step gate ----
        grep_ = reports["tree_journal_gate"]
        gwork = work / "tree-journal-gate"
        gevs = _events(gwork)
        gpkg = _staged_packages(gwork)
        gates = [_payload(e) for e in gevs
                 if e["type"] == "STEP_GATE"]
        iter_seqs = {_payload(e).get("iteration"):
                     e["event_seq"] for e in gevs
                     if e["type"] == "LOOP_ITERATION"}
        check("tree-journal-gate: the run completes "
              "in seven iterations with the brief "
              "filed, and exactly one step gate "
              "stands — bound to the second "
              "iteration, naming the first gather "
              "step and the journal bits it still "
              "needs",
              grep_["outcome"] == "yield"
              and grep_["iterations"] == 7
              and len(gates) == 1
              and gates[0].get("step") == G1
              and gates[0].get("missing") == ["journal"]
              and gates[0].get("iteration_seq")
              == iter_seqs.get(2),
              f"{gates}")
        corr = gpkg[3][0].get("step_gate_correction")
        check("tree-journal-gate: the package after "
              "the ahead read carries the gate's "
              "correction in the INDEX 475 shape — "
              "what arrived (the second source's "
              "read), the step it stays on, the "
              "journal bits still needed — and the "
              "step stays current with no content "
              "re-presented",
              corr is not None
              and corr.get("step") == G1
              and corr.get("missing") == ["journal"]
              and "sources/a3-pass.md" in corr.get(
                  "what_arrived", "")
              and "journal" in corr.get(
                  "instruction", "")
              and gpkg[3][0]["current_step"]["node"]
              == G1
              and "current_content" not in gpkg[3][0],
              f"{corr}")
        check("tree-journal-gate: the journal write "
              "advances the walk — the next package "
              "stands at the second gather step, and "
              "the ahead read's content is presented "
              "there, at its own step, exactly once "
              "in the whole run",
              gpkg[4][0]["current_step"]["node"] == G2
              and gpkg[4][0].get("current_content", {})
              .get("address") == "sources/a3-pass.md"
              and [k for k in range(1, 8)
                   if bodies["a3-pass"] in list(
                       _all_strings(gpkg[k][0]))] == [4])
        _check_checker("tree-journal-gate", grep_)

        # ---- tree-batch: three reads, one response --
        brep = reports["tree_batch"]
        bwork = work / "tree-batch"
        bevs = _events(bwork)
        bpkg = _staged_packages(bwork)
        check("tree-batch: the run completes in "
              "five iterations with the brief filed "
              "— the batch, three per-step journal "
              "writes, the contribution",
              brep["outcome"] == "yield"
              and brep["iterations"] == 5
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in bevs),
              f"{brep['outcome']} / {brep['iterations']}")
        first_dispatches = [
            _payload(e) for e in bevs
            if e["type"] == "TOOL_DISPATCHED"]
        check("tree-batch: all three reads of the "
              "one batch response stand dispatched "
              "in the record — his work executed as "
              "it arrived, none of it refused for "
              "arriving ahead",
              [d.get("tool") for d in first_dispatches]
              [:3] == ["sandbox.read"] * 3
              and [(_payload(e).get("parameters") or {})
                   .get("path") for e in bevs
                   if e["type"] == "TOOL_REQUESTED"][:3]
              == ["sources/stock-take.md",
                  "sources/a3-pass.md",
                  "sources/index-tail.md"],
              f"{[d.get('tool') for d in first_dispatches]}")
        bgates = [_payload(e) for e in bevs
                  if e["type"] == "STEP_GATE"]
        check("tree-batch: the step gate corrects "
              "the ahead work at the first two "
              "gather steps — the record still shows "
              "a later read standing at each — each "
              "naming the journal bits the current "
              "step still needs",
              len(bgates) == 2
              and all(g.get("missing") == ["journal"]
                      for g in bgates)
              and [g.get("step") for g in bgates]
              == [G1, G2],
              f"{bgates}")
        check("tree-batch: the first step package "
              "presents only the first file's "
              "content; the second and third files "
              "stand in it as working-set pointers — "
              "entries with no content — their "
              "contents presented at their own "
              "steps, exactly once each",
              bpkg[2][0].get("current_content", {})
              .get("address") == "sources/stock-take.md"
              and all(
                  "content" not in entry
                  for entry in bpkg[2][0]
                  ["working_set"]["entries"]
                  if entry.get("path") in (
                      "sources/a3-pass.md",
                      "sources/index-tail.md"))
              and [k for k in range(1, 6)
                   if bodies["a3-pass"] in list(
                       _all_strings(bpkg[k][0]))] == [3]
              and [k for k in range(1, 6)
                   if bodies["index-tail"] in list(
                       _all_strings(bpkg[k][0]))] == [4],
              f"{bpkg[2][0].get('current_content', {}).get('address')}")
        check("tree-batch: the per-step journal "
              "writes advance the presentation "
              "through the contents already in the "
              "room — gather two at package three, "
              "gather three at four, compose at "
              "five — and every package stands "
              "under the stated bound",
              [bpkg[k][0]["current_step"]["node"]
               for k in range(1, 6)]
              == ["orient", G1, G2, G3, "compose"]
              and all(size <= TREE_BOUND
                      for _p, size in bpkg.values()),
              f"{[bpkg[k][0]['current_step']['node'] for k in range(1, 6)]}")
        _check_checker("tree-batch", brep)

        # ---- tree-native: the BD-1 lane ----
        nrep = reports["tree_native"]
        nwork = work / "tree-native"
        nevs = _events(nwork)
        npkg = _tree_native_packages(nwork)
        check("tree-native: the run completes in "
              "eight iterations with the brief "
              "filed — the honest walk plus the "
              "refused call's wake",
              nrep["outcome"] == "yield"
              and nrep["iterations"] == 8
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in nevs),
              f"{nrep['outcome']} / {nrep['iterations']}")
        check("tree-native: the walk's current "
              "steps in order — the second gather "
              "step stands current across the "
              "refused call's wake, its content "
              "presented once, at its step",
              [npkg[k][0]["current_step"]["node"]
               for k in range(1, 9)]
              == ["orient", G1, G2, G2, G2, G3, G3,
                  "compose"]
              and [k for k in range(1, 9)
                   if bodies["a3-pass"] in list(
                       _all_strings(npkg[k][0]))] == [4],
              f"{[npkg[k][0]['current_step']['node'] for k in range(1, 9)]}")
        nreq = {}
        for e in nevs:
            if e["type"] == "TOOL_REQUESTED":
                nreq[_payload(e).get("request_id")] = \
                    _payload(e)
        ndisp = {}
        for e in nevs:
            if e["type"] == "TOOL_DISPATCHED":
                ndisp[_payload(e).get("request_id")] = \
                    _payload(e)
        nout = {}
        for e in nevs:
            if e["type"] == "TOOL_OUTCOME":
                nout[_payload(e).get("dispatch_id")] = \
                    _payload(e)
        granted = [r for r in nreq.values()
                   if r.get("tool") == "sandbox.read"
                   and (r.get("parameters") or {})
                   .get("path") == "sources/stock-take.md"]
        check("tree-native: the granted native "
              "call — a read under his sealed "
              "grants — dispatched and answered with "
              "its result",
              len(granted) == 1
              and granted[0].get("request_id") in ndisp
              and nout.get(ndisp[granted[0].get(
                  "request_id")].get("dispatch_id"),
                  {}).get("outcome") == "result",
              f"{granted}")
        ungranted = [r for r in nreq.values()
                     if r.get("tool") == "sandbox.write"
                     and (r.get("parameters") or {})
                     .get("path") == "sources/stock-take.md"]
        rejections = [_payload(e) for e in nevs
                      if e["type"] == "REJECTION"]
        check("tree-native: the ungranted native "
              "call — a write to a stocked source, "
              "outside the write grant's scratch "
              "scope — is refused at the doorway: "
              "no dispatch stands for its request, "
              "and the refusal stands recorded in "
              "the family's shape, a REJECTION "
              "naming the attempted dispatch and "
              "the grant ceiling it lies outside; "
              "the source itself stands unaltered",
              len(ungranted) == 1
              and ungranted[0].get("request_id")
              not in ndisp
              and any(
                  r.get("request_id") == ungranted[0]
                  .get("request_id")
                  and r.get("attempted_type")
                  == "TOOL_DISPATCHED"
                  and "ceiling" in r.get("ground", "")
                  for r in rejections)
              and (nwork / "run" / "sandbox" / "sources"
                   / "stock-take.md").read_bytes()
              .decode("utf-8") == bodies["stock-take"],
              f"{rejections}")
        ncaps = [json.loads(line) for line in
                 (nwork / "captures.jsonl")
                 .read_text().splitlines() if line.strip()]
        loop_bodies = []
        for c in ncaps:
            if c["mode"] == "chat-raw-bounded" \
                    and c["index"] >= 6:
                loop_bodies.append(json.loads(
                    base64.b64decode(c["request_b64"])))
        wire = [b for b in loop_bodies
                if isinstance(b.get("tools"), list)]
        check("tree-native: the actual outbound "
              "requests the captures record — the "
              "corrected Groq transport's own "
              "construction, not a staged path — "
              "carry the sealed tools offered "
              "natively on every loop call, with "
              "tool_choice permitting calls and "
              "disable_tool_validation exactly as "
              "staged (true)",
              len(wire) == 8
              and all(
                  b.get("tool_choice") == "auto"
                  and b.get(
                      "disable_tool_validation") is True
                  and any(
                      (t.get("function") or {})
                      .get("name") == "sandbox.read"
                      for t in b["tools"])
                  for b in wire),
              f"{len(wire)} wired calls of "
              f"{len(loop_bodies)}")
        _check_checker("tree-native", nrep)
        print(f"process-tree section: "
              f"{CHECKS[0] - tree_before} checks")

        # ============= office cycle (the plan of
        # 2026-11-25) =============
        # The office-cycle contract's witnesses (the
        # plan of 2026-11-25, Ben's approval and Vane's
        # examination on the record): the stocking
        # portioned into blocks at the ruled ceiling;
        # one block in front of him at a time, its
        # content presented once at its cycle; the
        # journal read + append and never carried, its
        # appends the cycle gate's second leg; the
        # catalogue living in the office — the wire
        # offering each cycle's tools while the record
        # resolves against the sealed grants; and every
        # call estimated under the per-call budget
        # before it is sent.
        cycle_before = CHECKS[0]
        JOURNAL = "scratch/journal.md"
        NOTES = [rehearsal.CYCLE_NOTE_1,
                 rehearsal.CYCLE_NOTE_2,
                 rehearsal.CYCLE_NOTE_3,
                 rehearsal.CYCLE_NOTE_4,
                 rehearsal.CYCLE_NOTE_5,
                 rehearsal.CYCLE_NOTE_6]

        def _cycle_packages(scenario):
            return _staged_packages(work / scenario)

        def _journal_free(package, *, opening):
            """No journal content anywhere in a package:
            no journal component beyond the opening's
            designation (path + contract, no content),
            and no journal entry text in any component
            — except inside the one tool-results entry
            answering his own journal read, which is
            his pull answered once, not carriage."""
            for key, value in package.items():
                if key == "journal":
                    if not opening:
                        return False
                    if set(value) != {"path", "contract"}:
                        return False
                    continue
                if key == "tool_results":
                    for entry in value:
                        result = entry.get("result") \
                            if isinstance(entry, dict) \
                            else None
                        if isinstance(result, dict) \
                                and result.get("path") \
                                == JOURNAL:
                            continue
                        blob = canonical(entry).decode(
                            "utf-8", "replace")
                        if any(note[:40] in blob
                               for note in NOTES):
                            return False
                    continue
                blob = canonical(value).decode(
                    "utf-8", "replace")
                if any(note[:40] in blob
                       for note in NOTES):
                    return False
            return True

        def _offer_names(package):
            return [t.get("tool")
                    for t in package.get("tools") or []]

        # ---- cycle-honest: the honest path ----
        crep = reports["cycle_honest"]
        cwork = work / "cycle-honest"
        cevs = _events(cwork)
        cpkg = _cycle_packages("cycle-honest")
        check("cycle-honest: the run completes in "
              "nine iterations — opening, one wake per "
              "block (its content presented, its append "
              "and the next pull in one answer), "
              "summarize, the journal read, the filing "
              "— and the brief stands filed",
              crep["outcome"] == "yield"
              and crep["iterations"] == 9
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in cevs),
              f"{crep['outcome']} / {crep['iterations']}")
        check("cycle-honest: the honest path records "
              "no gate of any kind — zero cycle gates, "
              "zero journal gates — and exactly six "
              "journal appends, one per block",
              not any(e["type"] == "CYCLE_GATE"
                      for e in cevs)
              and not any(e["type"] == "JOURNAL_GATE"
                          for e in cevs)
              and sum(1 for e in cevs
                      if e["type"] == "JOURNAL_APPEND")
              == 6,
              f"{[e['type'] for e in cevs if 'GATE' in e['type']]}")
        check("cycle-honest: the sealed record "
              "declares the office-cycle presentation "
              "contract, no worked example stands in "
              "the seal, and the journal baseline seals "
              "the designated address with the empty "
              "journal's hash as its trusted initial "
              "state",
              crep["sealed_presentation_contract"]
              == "office-cycle-v1"
              and crep["sealed_worked_example"] is None
              and crep["sealed_journal_baseline"] == {
                  "address": JOURNAL,
                  "initial_sha256": sha256_hex(b"")},
              f"{crep['sealed_presentation_contract']}")
        sealed_map = crep["sealed_block_map"]
        sandbox = cwork / "run" / "sandbox"
        contents = {}
        for address in ("sources/stock-take.md",
                        "sources/a3-pass.md",
                        "sources/index-tail.md"):
            contents[address] = (
                sandbox / address).read_bytes()
        check("cycle-honest: the sealed block map is "
              "the office's portioning of the stocked "
              "files at the ruled ceiling, re-derived "
              "from the staged bytes whole — and its "
              "coverage is complete: every block at or "
              "under 12,000 bytes of content, and the "
              "ranges of each file's blocks together "
              "covering the file's lines exactly",
              sealed_map == tool_policy.compute_block_map(
                  list(contents), contents)
              and all(b["content_bytes"] <= 12000
                      for b in sealed_map)
              and all(
                  [ln for b in sealed_map
                   if b["address"] == address
                   for ln in range(
                       b["line_start"] or 1,
                       (b["line_end"] or len(
                           tool_policy.split_lines(
                               contents[address]))) + 1)]
                  == list(range(1, len(
                      tool_policy.split_lines(
                          contents[address])) + 1))
                  for address in contents),
              f"{len(sealed_map or [])} blocks")
        check("cycle-honest: nine packages stand in "
              "the captures — the first the opening, "
              "six cycle packages, then summarize "
              "twice (the journal read's wake and the "
              "filing's) — every one under the "
              "office-cycle contract",
              sorted(cpkg) == list(range(1, 10))
              and cpkg[1][0]["presentation"]["package"]
              == "opening"
              and all(
                  cpkg[k][0]["presentation"]["package"]
                  == "cycle"
                  and cpkg[k][0]["presentation"]
                  ["contract"] == "office-cycle-v1"
                  for k in range(2, 8))
              and all(
                  cpkg[k][0]["presentation"]["package"]
                  == "summarize"
                  for k in (8, 9)),
              f"{sorted(cpkg)}")
        opening = cpkg[1][0]
        check("cycle-honest: the opening package "
              "carries the job whole and nothing else — "
              "his memory as his own knowledge, the "
              "task (assignment, deliverable, the four "
              "points, the figures), the cycle poster "
              "(the sketch flow and the block map, an "
              "access way per block), the journal's "
              "designated address and contract, his "
              "position at cycle 1 — and no catalogue "
              "as presented matter, no journal content, "
              "no working set, no case dump",
              all(k in opening for k in (
                  "memory", "case_essentials", "task",
                  "poster", "journal"))
              and opening["journal"]["path"] == JOURNAL
              and set(opening["journal"])
              == {"path", "contract"}
              and all(k in opening["task"] for k in (
                  "assignment", "deliverable", "points",
                  "figures"))
              and len(opening["task"]["points"]) == 4
              and [b["block_id"] for b in
                   opening["poster"]["blocks"]]
              == [b["block_id"] for b in sealed_map]
              and all("access" in b for b in
                      opening["poster"]["blocks"])
              and "working_set" not in opening
              and "process_tree" not in opening
              and _offer_names(opening) == [
                  "sandbox.read", "sandbox.read_range",
                  "sandbox.write"],
              f"{sorted(opening)}")
        check("cycle-honest: his first response is "
              "work — the first request the record "
              "stands is the first block's pull, no "
              "acknowledge outcome anywhere",
              [p.get("tool") for p in
               (_payload(e) for e in cevs
                if e["type"] == "TOOL_REQUESTED")
               ][:1] == ["sandbox.read"]
              and not any(
                  e["type"] == "TOOL_REQUESTED"
                  and _payload(e).get("tool")
                  not in ("sandbox.read",
                          "sandbox.read_range",
                          "sandbox.write")
                  for e in cevs),
              "")
        presented = {}
        for k in range(1, 10):
            bc = cpkg[k][0].get("block_content")
            if bc is not None:
                presented.setdefault(
                    bc["block_id"], []).append(k)
        sealed_by_id = {b["block_id"]: b
                        for b in sealed_map}

        def _block_bytes(block):
            data = contents[block["address"]]
            if block["line_start"] is None:
                return data
            lines = tool_policy.split_lines(data)
            return b"".join(lines[
                block["line_start"] - 1:
                block["line_end"]])

        check("cycle-honest: each block's content is "
              "presented exactly once, at its own "
              "cycle's package — blocks B1..B6 at "
              "packages 2..7 — and the presented "
              "content is the block's exact bytes from "
              "the stocked file",
              presented == {f"B{i}": [i + 1]
                            for i in range(1, 7)}
              and all(
                  cpkg[k][0]["block_content"]["content"]
                  == _block_bytes(sealed_by_id[
                      cpkg[k][0]["block_content"]
                      ["block_id"]]).decode("utf-8")
                  for k in range(2, 8)),
              f"{presented}")
        check("cycle-honest: after its cycle, a block "
              "stands as a pointer — the packages after "
              "its presentation carry its entry with "
              "fingerprint, size and dispatch "
              "provenance, and its content nowhere",
              all(
                  (lambda entry: entry is not None
                   and entry.get("content_sha256")
                   == blk["content_sha256"]
                   and entry.get("dispatch_id")
                   is not None)(
                      next((b for b in
                            cpkg[k][0]["blocks"]
                            if b["block_id"]
                            == blk["block_id"]), None))
                  for blk in sealed_map
                  for k in (8, 9)),
              "")
        check("cycle-honest: the summarize package "
              "carries no source content and no block "
              "content — its instruction is to read "
              "the journal whole and compile the brief "
              "from it — and its offer set is the "
              "journal's tools alone (read and write)",
              cpkg[8][0].get("block_content") is None
              and cpkg[8][0]["current_cycle"]["stage"]
              == "summarize"
              and JOURNAL in cpkg[8][0]
              ["current_cycle"]["instruction"]
              and _offer_names(cpkg[8][0]) == [
                  "sandbox.read", "sandbox.write"],
              "")
        check("cycle-honest: no package in the run "
              "carries journal content or a journal "
              "component beyond the opening's "
              "designation, and no package presents "
              "the catalogue — every offer set is the "
              "cycle's tools plus the journal tools, "
              "never the sealed ten",
              all(_journal_free(cpkg[k][0],
                                opening=(k == 1))
                  for k in range(1, 10))
              and all(len(cpkg[k][0]["tools"]) <= 3
                      for k in range(1, 10)),
              "")
        estimates = crep["call_estimates"]
        print(f"cycle-honest: opening package "
              f"estimated at "
              f"{estimates[0]['serialized_bytes']} "
              f"bytes / "
              f"{estimates[0]['estimated_tokens']} "
              f"tokens; largest cycle package "
              f"{max(e['serialized_bytes'] for e in estimates)} "
              f"bytes / "
              f"{max(e['estimated_tokens'] for e in estimates)} "
              f"tokens")
        check("cycle-honest: every serialized "
              "request's estimate stands at or under "
              "the per-call budget of 4,000 tokens — "
              "the opening included — the figures "
              "printed above",
              len(estimates) == 9
              and all(e["estimated_tokens"] <= 4000
                      for e in estimates),
              f"{estimates}")
        _check_checker("cycle-honest", crep)

        # ---- cycle-run-ahead: the cycle gate ----
        rrep = reports["cycle_run_ahead"]
        revs = _events(work / "cycle-run-ahead")
        rpkg = _cycle_packages("cycle-run-ahead")
        gates = [e for e in revs
                 if e["type"] == "CYCLE_GATE"]
        check("cycle-run-ahead: pulling the third "
              "block while the second cycle stands "
              "incomplete records exactly one cycle "
              "gate — cycle 2, block B2, the read ahead "
              "of it B3 — and the run still files, in "
              "nine iterations",
              len(gates) == 1
              and _payload(gates[0])["cycle"] == 2
              and _payload(gates[0])["block_id"] == "B2"
              and _payload(gates[0])["ahead_block_id"]
              == "B3"
              and rrep["outcome"] == "yield"
              and rrep["iterations"] == 9
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in revs),
              f"{len(gates)} gates")
        correction = rpkg[3][0].get(
            "cycle_gate_correction") or {}
        check("cycle-run-ahead: the correction rides "
              "the next package in the gate's own "
              "shape — what arrived (the B3 read, "
              "nothing refused, nothing lost), what is "
              "needed (cycle 2's append), an example — "
              "its facts the gate event's own, its "
              "exact bytes hash-verified by the "
              "checker's independent derivation (the "
              "11/11 below)",
              correction.get("cycle") == 2
              and correction.get("block_id") == "B2"
              and correction.get("ahead_block_id")
              == "B3"
              and "nothing is refused" in
              correction.get("what_arrived", "")
              and "cycle 2" in
              correction.get("instruction", "")
              and "sandbox.write" in
              correction.get("example", ""),
              f"{sorted(correction)}")
        check("cycle-run-ahead: the gate fires once "
              "only — the packages after the correction "
              "carry no further cycle correction, and "
              "no journal gate stands anywhere",
              all("cycle_gate_correction" not in
                  rpkg[k][0] for k in range(4, 10))
              and not any(e["type"] == "JOURNAL_GATE"
                          for e in revs),
              "")
        _check_checker("cycle-run-ahead", rrep)

        # ---- cycle-journal-rewrite: the journal
        # gate ----
        jrep = reports["cycle_journal_rewrite"]
        jevs = _events(work / "cycle-journal-rewrite")
        jgates = [e for e in jevs
                  if e["type"] == "JOURNAL_GATE"]
        jappends = [e for e in jevs
                    if e["type"] == "JOURNAL_APPEND"]
        check("cycle-journal-rewrite: the rewrite "
              "attempt records exactly one journal "
              "gate, the transition is not counted — "
              "six appends stand, not seven — and the "
              "following proper append, extending the "
              "accepted journal, is accepted and "
              "closes cycle 2; the run files in ten "
              "iterations",
              len(jgates) == 1
              and len(jappends) == 6
              and any(
                  _payload(a)["cycle"] == 2
                  and a["event_seq"]
                  > jgates[0]["event_seq"]
                  for a in jappends)
              and jrep["outcome"] == "yield"
              and jrep["iterations"] == 10
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in jevs),
              f"{len(jgates)} gates / "
              f"{len(jappends)} appends")
        jpkg = _cycle_packages("cycle-journal-rewrite")
        check("cycle-journal-rewrite: the journal "
              "gate's correction rides the next "
              "package, naming the accepted journal as "
              "the ground to extend — and the journal "
              "on disk at the end is the accepted "
              "chain whole: the six notes in order, "
              "the rewrite nowhere in it",
              "journal_gate_correction" in jpkg[4][0]
              and (work / "cycle-journal-rewrite"
                   / "run" / "sandbox" / JOURNAL
                   ).read_text() == "".join(NOTES),
              "")
        _check_checker("cycle-journal-rewrite", jrep)

        # ---- cycle-offoffer: the offer/resolution
        # split ----
        orep = reports["cycle_offoffer"]
        oevs = _events(work / "cycle-offoffer")
        opkg = _cycle_packages("cycle-offoffer")
        rejections = [e for e in oevs
                      if e["type"] == "REJECTION"]
        check("cycle-offoffer: the granted call "
              "outside the offer set — sandbox.search, "
              "offered in no cycle package — resolves "
              "against the sealed catalogue and "
              "dispatches; the ungranted call — a "
              "write against a stocked source — is "
              "refused at the doorway with its "
              "rejection recorded, and never "
              "dispatches",
              any(e["type"] == "TOOL_DISPATCHED"
                  and _payload(e).get("tool")
                  == "sandbox.search" for e in oevs)
              and len(rejections) == 1
              and _payload(rejections[0]).get("tool")
              == "sandbox.write"
              and not any(
                  e["type"] == "TOOL_DISPATCHED"
                  and _payload(e).get("request_id")
                  == _payload(rejections[0])
                  .get("request_id") for e in oevs)
              and all("sandbox.search" not in
                      _offer_names(opkg[k][0])
                      for k in opkg),
              "")
        check("cycle-offoffer: the walk then runs "
              "the honest rhythm to a filed brief — "
              "ten iterations, six appends, no cycle "
              "or journal gate — the off-offer work "
              "costing one wake, not the walk",
              orep["outcome"] == "yield"
              and orep["iterations"] == 10
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in oevs)
              and sum(1 for e in oevs
                      if e["type"] == "JOURNAL_APPEND")
              == 6
              and not any(e["type"] in (
                  "CYCLE_GATE", "JOURNAL_GATE")
                  for e in oevs),
              f"{orep['outcome']} / {orep['iterations']}")
        _check_checker("cycle-offoffer", orep)

        # ---- cycle-budget: the road's spill ----
        # witness (the §6 amendment, rebased
        # 2026-11-26: this scenario asserted the
        # per-call refusal until the amendment
        # retired it; it now asserts the road's
        # answer to the same giant block)
        brep = reports["cycle_budget"]
        bevs = _events(work / "cycle-budget")
        refusals = [e for e in bevs
                    if e["type"] == "BUDGET_REFUSAL"]
        bcaps = [json.loads(line) for line in
                 (work / "cycle-budget" / "captures.jsonl")
                 .read_text().splitlines() if line.strip()]
        loop_calls = 0
        for c in bcaps:
            if c["mode"] != "chat":
                continue
            body = json.loads(base64.b64decode(
                c["request_b64"]))
            text = json.dumps(body)
            if "Your wake package:" in text:
                loop_calls += 1
        spills = [e for e in
                  brep["road_presentation_events"]
                  if e.get("kind") == "spill"]
        check("cycle-budget: under the road the "
              "giant block's package is ADMITTED — "
              "no budget refusal stands in the "
              "record; the block's content rides "
              "spilled (its reference, fingerprint "
              "and a bounded preview, counted over "
              "the 4,096 threshold) in the road's "
              "presentation events; the walk "
              "completes in four iterations — "
              "opening, the spilled block's wake, "
              "summarize, the filing — the brief "
              "stands filed, and four loop requests "
              "stand in the captures",
              len(refusals) == 0
              and brep["outcome"] == "yield"
              and brep["iterations"] == 4
              and any(
                  e.get("surface") == "block_content"
                  and e.get("counted_tokens", 0) > 4096
                  for e in spills)
              and loop_calls == 4,
              f"{loop_calls} loop calls, "
              f"{len(spills)} spills, outcome "
              f"{brep['outcome']}")
        _check_checker("cycle-budget", brep)
        print(f"office-cycle section: "
              f"{CHECKS[0] - cycle_before} checks")

        # ============= office cycle v2 — the
        # split-on-return successor (the amendment
        # as stripped by the director's ruling of
        # 2026-11-25) =============
        # The successor contract's witnesses: the
        # honest path as the control (the v1 script
        # step for step under the new seal); the
        # six-block batch — the shape demo-gptoss5
        # died on — presenting one block at the batch
        # wake, carrying no correction, and standing
        # within budget at every wake; the re-pull
        # pair (the current block's re-pull answered
        # in the carriage, an earlier block's re-pull
        # refreshing its pointer alone); and the
        # opening's room lines, stated once. The
        # checker is not run over these records in
        # this build: the ruling deferred the
        # checker-correspondence work, and the
        # checker's population stands at v1 (the
        # v1 sections above run it as ever).
        cycle2_before = CHECKS[0]
        ROOM_PHRASES = ("4,000 estimated tokens",
                        "one block per wake",
                        "costs you nothing and gains "
                        "you nothing")

        def _block_read_entries(package):
            return [e for e in
                    package.get("tool_results") or []
                    if isinstance(
                        (e.get("result") or {}).get(
                            "path"), str)
                    and (e["result"]["path"]
                         .startswith("sources/"))]

        # ---- cycle2-honest: the control ----
        hrep = reports["cycle2_honest"]
        hwork = work / "cycle2-honest"
        hevs = _events(hwork)
        hpkg = _cycle_packages("cycle2-honest")
        check("cycle2-honest: the honest path under "
              "the split-on-return seal completes in "
              "nine iterations and the brief stands "
              "filed — the v1 path's own shape",
              hrep["outcome"] == "yield"
              and hrep["iterations"] == 9
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in hevs),
              f"{hrep['outcome']} / {hrep['iterations']}")
        check("cycle2-honest: the sealed record "
              "declares the split-on-return contract, "
              "no worked example stands in the seal, "
              "the journal baseline is v1's, and the "
              "sealed block map is the v1 run's own "
              "map — the same portioning under the "
              "new name",
              hrep["sealed_presentation_contract"]
              == "office-cycle-v2"
              and hrep["sealed_worked_example"] is None
              and hrep["sealed_journal_baseline"] == {
                  "address": JOURNAL,
                  "initial_sha256": sha256_hex(b"")}
              and hrep["sealed_block_map"]
              == crep["sealed_block_map"],
              f"{hrep['sealed_presentation_contract']}")
        opening2 = hpkg[1][0]
        room_lines = (opening2.get("poster") or {}).get(
            "room_knowledge") or ""
        check("cycle2-honest: the opening states "
              "the room's rules once — the per-call "
              "budget in plain figures, the one-block-"
              "per-wake return, and that pulling ahead "
              "costs and gains nothing — and every "
              "package names the successor contract",
              all(phrase in room_lines
                  for phrase in ROOM_PHRASES)
              and all(
                  hpkg[k][0]["presentation"]["contract"]
                  == "office-cycle-v2"
                  for k in range(1, 10)),
              f"{room_lines[:80]}")
        check("cycle2-honest: the room lines stand "
              "in the opening alone — no later package "
              "repeats them, and the v1 control's "
              "opening carries none",
              all("one block per wake" not in
                  canonical(hpkg[k][0]).decode(
                      "utf-8", "replace")
                  for k in range(2, 10))
              and "room_knowledge" not in (
                  cpkg[1][0].get("poster") or {}),
              "")
        presented2 = {}
        for k in range(1, 10):
            bc = hpkg[k][0].get("block_content")
            if bc is not None:
                presented2.setdefault(
                    bc["block_id"], []).append(k)
        hsandbox = hwork / "run" / "sandbox"
        hcontents = {}
        for address in ("sources/stock-take.md",
                        "sources/a3-pass.md",
                        "sources/index-tail.md"):
            hcontents[address] = (
                hsandbox / address).read_bytes()

        def _block_bytes2(block):
            data = hcontents[block["address"]]
            if block["line_start"] is None:
                return data
            lines = tool_policy.split_lines(data)
            return b"".join(lines[
                block["line_start"] - 1:
                block["line_end"]])

        sealed_by_id2 = {b["block_id"]: b
                         for b in hrep["sealed_block_map"]}
        check("cycle2-honest: each block's content "
              "is presented exactly once, at its own "
              "cycle's package, and the presented "
              "content is the block's exact bytes — "
              "the v1 presentation, unchanged",
              presented2 == {f"B{i}": [i + 1]
                             for i in range(1, 7)}
              and all(
                  hpkg[k][0]["block_content"]["content"]
                  == _block_bytes2(sealed_by_id2[
                      hpkg[k][0]["block_content"]
                      ["block_id"]]).decode("utf-8")
                  for k in range(2, 8)),
              f"{presented2}")
        check("cycle2-honest: on the honest path "
              "the carriage matches v1's shapes — at "
              "each cycle package exactly one block-"
              "read entry rides, stubbed to the "
              "block_content component",
              all(
                  len(_block_read_entries(hpkg[k][0]))
                  == 1
                  and _block_read_entries(
                      hpkg[k][0])[0]["result"].get(
                          "presented_in")
                  == "block_content"
                  for k in range(2, 8)),
              "")
        estimates2 = hrep["call_estimates"]
        print(f"cycle2-honest: opening package "
              f"estimated at "
              f"{estimates2[0]['serialized_bytes']} "
              f"bytes / "
              f"{estimates2[0]['estimated_tokens']} "
              f"tokens; largest package "
              f"{max(e['serialized_bytes'] for e in estimates2)} "
              f"bytes / "
              f"{max(e['estimated_tokens'] for e in estimates2)} "
              f"tokens")
        check("cycle2-honest: every serialized "
              "request's estimate stands at or under "
              "the per-call budget of 4,000 tokens — "
              "the opening, carrying the room lines, "
              "included",
              len(estimates2) == 9
              and all(e["estimated_tokens"] <= 4000
                      for e in estimates2),
              f"{estimates2}")

        # ---- cycle2-batch: the batch wake ----
        trep = reports["cycle2_batch"]
        twork = work / "cycle2-batch"
        tevs = _events(twork)
        tpkg = _cycle_packages("cycle2-batch")
        tgates = [e for e in tevs
                  if e["type"] == "CYCLE_GATE"]
        check("cycle2-batch: the batch walk "
              "completes in nine iterations and files "
              "— the gate arithmetic stands exactly "
              "as under v1 (five cycle gates, cycles "
              "1-5, each recorded as its append came "
              "due), and no budget refusal stands",
              trep["outcome"] == "yield"
              and trep["iterations"] == 9
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in tevs)
              and [_payload(g)["cycle"] for g in tgates]
              == [1, 2, 3, 4, 5]
              and not any(
                  e["type"] == "BUDGET_REFUSAL"
                  for e in tevs),
              f"{trep['outcome']} / {trep['iterations']}"
              f" / {[ _payload(g)['cycle'] for g in tgates]}")
        check("cycle2-batch: no package in the run "
              "carries a cycle-gate correction — the "
              "gates stand in the record, and the "
              "metered presentation and the opening's "
              "standing lines carry their content",
              all("cycle_gate_correction" not in
                  tpkg[k][0] for k in range(1, 10)),
              "")
        batch_wake = tpkg[2][0]
        bw_entries = _block_read_entries(batch_wake)
        check("cycle2-batch: the batch wake "
              "presents exactly one block's content "
              "(B1, the current cycle's) and its "
              "carriage carries exactly that block's "
              "stub — the other five pulls of the "
              "batch response ride nowhere: not as "
              "content, not as stubs",
              (batch_wake.get("block_content")
               or {}).get("block_id") == "B1"
              and len(bw_entries) == 1
              and bw_entries[0]["result"].get("path")
              == "sources/stock-take.md"
              and bw_entries[0]["result"].get(
                  "presented_in") == "block_content",
              f"{[(e['result'].get('path'), e['result'].get('presented_in')) for e in bw_entries]}")
        presented_t = {}
        for k in range(1, 10):
            bc = tpkg[k][0].get("block_content")
            if bc is not None:
                presented_t.setdefault(
                    bc["block_id"], []).append(k)
        check("cycle2-batch: across the walk each "
              "block's content is still presented "
              "exactly once, at its own cycle — the "
              "batch pull created no early "
              "presentation of any block",
              presented_t == {f"B{i}": [i + 1]
                              for i in range(1, 7)},
              f"{presented_t}")
        estimates_t = trep["call_estimates"]
        print(f"cycle2-batch: the batch wake "
              f"estimated at "
              f"{estimates_t[1]['serialized_bytes']} "
              f"bytes / "
              f"{estimates_t[1]['estimated_tokens']} "
              f"tokens; largest package "
              f"{max(e['serialized_bytes'] for e in estimates_t)} "
              f"bytes / "
              f"{max(e['estimated_tokens'] for e in estimates_t)} "
              f"tokens")
        check("cycle2-batch: every serialized "
              "request's estimate stands at or under "
              "the per-call budget of 4,000 tokens — "
              "the batch wake included, the wake the "
              "live batch run died on at 4,273 under "
              "v1's arrival-bundled carriage",
              len(estimates_t) == 9
              and all(e["estimated_tokens"] <= 4000
                      for e in estimates_t),
              f"{estimates_t}")

        # ---- cycle2-repull: the re-pull pair ----
        prep2 = reports["cycle2_repull"]
        pwork = work / "cycle2-repull"
        pevs = _events(pwork)
        ppkg = _cycle_packages("cycle2-repull")
        check("cycle2-repull: the walk completes "
              "in ten iterations and files, and the "
              "re-pulls record no gate of any kind",
              prep2["outcome"] == "yield"
              and prep2["iterations"] == 10
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in pevs)
              and not any(
                  e["type"] in ("CYCLE_GATE",
                                "JOURNAL_GATE")
                  for e in pevs),
              f"{prep2['outcome']} / {prep2['iterations']}")
        wake4 = ppkg[4][0]
        w4_entries = _block_read_entries(wake4)
        a3_text = hcontents[
            "sources/a3-pass.md"].decode("utf-8")
        check("cycle2-repull: the wake after the "
              "current block's re-pull carries no "
              "block_content (the cycle presentation "
              "stands spent) and answers the re-pull "
              "in its carriage — the a3-pass result "
              "rides with its content, the file's "
              "exact bytes",
              wake4.get("block_content") is None
              and len(w4_entries) == 1
              and w4_entries[0]["result"].get("path")
              == "sources/a3-pass.md"
              and w4_entries[0]["result"].get(
                  "content") == a3_text,
              f"{[(e['result'].get('path'), 'content' in e['result']) for e in w4_entries]}")
        wake6 = ppkg[6][0]
        w6_entries = _block_read_entries(wake6)
        check("cycle2-repull: the wake after an "
              "earlier block's re-pull carries that "
              "block nowhere — no stock-take entry "
              "rides; the current block's stub rides "
              "as ever, its content in block_content",
              all(e["result"].get("path")
                  != "sources/stock-take.md"
                  for e in w6_entries)
              and len(w6_entries) == 1
              and w6_entries[0]["result"].get(
                  "presented_in") == "block_content"
              and (wake6.get("block_content")
                   or {}).get("block_id") == "B4",
              f"{[(e['result'].get('path'), e['result'].get('presented_in')) for e in w6_entries]}")
        estimates_p = prep2["call_estimates"]
        print(f"cycle2-repull: largest package "
              f"{max(e['serialized_bytes'] for e in estimates_p)} "
              f"bytes / "
              f"{max(e['estimated_tokens'] for e in estimates_p)} "
              f"tokens")
        check("cycle2-repull: every serialized "
              "request's estimate stands at or under "
              "the per-call budget of 4,000 tokens",
              len(estimates_p) == 10
              and all(e["estimated_tokens"] <= 4000
                      for e in estimates_p),
              f"{estimates_p}")
        print(f"office-cycle-v2 section: "
              f"{CHECKS[0] - cycle2_before} checks")

        # ============= office cycle v3 — the
        # draft-page successor (the director's
        # ruling of 2026-11-25 21:16 MST, ordered
        # after demo-gptoss6) =============
        # The successor contract's witnesses: the
        # opening's journal contract carries the
        # draft-page correction as specific
        # step-by-step instructions — the three
        # numbered steps — where the v2 control's
        # opening carries none of them; the room
        # knowledge stands in the v3 opening
        # unchanged; the honest walk completes and
        # files with the journal standing as draft
        # whole, no passage a copy of its block;
        # the batch walk completes and files; and
        # every measured package stands within the
        # per-call budget. The checker is not run
        # over these records: the ruling's
        # checker-correspondence deferral stands,
        # and the checker's population stands at
        # v1, exactly as for the v2 section above.
        cycle3_before = CHECKS[0]
        STEP_PHRASES = ("(1) read the block",
                        "(2) in your journal, write "
                        "the draft",
                        "(3) when that draft stands "
                        "in the journal")

        # ---- cycle3-honest: the draft walk ----
        h3rep = reports["cycle3_honest"]
        h3work = work / "cycle3-honest"
        h3evs = _events(h3work)
        h3pkg = _cycle_packages("cycle3-honest")
        check("cycle3-honest: the honest path under "
              "the draft-page seal completes in nine "
              "iterations and the brief stands filed "
              "— the v1 and v2 paths' own shape",
              h3rep["outcome"] == "yield"
              and h3rep["iterations"] == 9
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in h3evs),
              f"{h3rep['outcome']} / "
              f"{h3rep['iterations']}")
        check("cycle3-honest: the sealed record "
              "declares the draft-page contract, no "
              "worked example stands in the seal, "
              "the journal baseline is v1's, and the "
              "sealed block map is the v1 run's own "
              "map — the same portioning under the "
              "new name",
              h3rep["sealed_presentation_contract"]
              == "office-cycle-v3"
              and h3rep["sealed_worked_example"]
              is None
              and h3rep["sealed_journal_baseline"]
              == {"address": JOURNAL,
                  "initial_sha256": sha256_hex(b"")}
              and h3rep["sealed_block_map"]
              == crep["sealed_block_map"],
              f"{h3rep['sealed_presentation_contract']}")
        opening3 = h3pkg[1][0]
        contract3 = (opening3.get("journal")
                     or {}).get("contract") or ""
        check("cycle3-honest: the opening's journal "
              "contract carries the draft-page "
              "correction as specific step-by-step "
              "instructions — the three numbered "
              "steps stand in the opening package — "
              "and every package names the successor "
              "contract",
              all(step in contract3
                  for step in STEP_PHRASES)
              and all(
                  h3pkg[k][0]["presentation"]
                  ["contract"] == "office-cycle-v3"
                  for k in range(1, 10)),
              f"{contract3[:80]}")
        contract2 = (opening2.get("journal")
                     or {}).get("contract") or ""
        check("cycle3-honest: the v2 control "
              "carries none of the steps — its "
              "opening's journal contract is the "
              "research-log wording, and no package "
              "of its walk carries the step-by-step "
              "text; the successor's build left the "
              "v2 presentation untouched",
              all(step not in contract2
                  for step in STEP_PHRASES)
              and all(
                  step not in canonical(
                      hpkg[k][0]).decode(
                          "utf-8", "replace")
                  for k in range(1, 10)
                  for step in STEP_PHRASES),
              "")
        room3 = (opening3.get("poster") or {}).get(
            "room_knowledge") or ""
        check("cycle3-honest: the room's rules "
              "stand in the v3 opening unchanged — "
              "the same standing lines, word for "
              "word, that the v2 opening carries",
              room3 == room_lines
              and all(phrase in room3
                      for phrase in ROOM_PHRASES),
              f"{room3[:80]}")
        h3sandbox = h3work / "run" / "sandbox"
        h3contents = {}
        for address in ("sources/stock-take.md",
                        "sources/a3-pass.md",
                        "sources/index-tail.md"):
            h3contents[address] = (
                h3sandbox / address).read_bytes()
        DRAFTS = [rehearsal.CYCLE_DRAFT_1,
                  rehearsal.CYCLE_DRAFT_2,
                  rehearsal.CYCLE_DRAFT_3,
                  rehearsal.CYCLE_DRAFT_4,
                  rehearsal.CYCLE_DRAFT_5,
                  rehearsal.CYCLE_DRAFT_6]
        appends3 = [_payload(e) for e in h3evs
                    if e["type"] == "JOURNAL_APPEND"]
        chain3 = [sha256_hex(b"")]
        for draft in DRAFTS:
            chain3.append(sha256_hex(
                "".join(DRAFTS[:len(chain3)])
                .encode("utf-8")))
        check("cycle3-honest: the journal that "
              "stands at the walk's end is the "
              "draft whole — six accepted appends, "
              "each extending the last from the "
              "empty baseline, the final hash the "
              "hash of the six passages in order — "
              "and no passage is a copy of its "
              "block's text: the end work created "
              "gradually, as the contract describes",
              len(appends3) == 6
              and all(
                  a["before_sha256"] == chain3[i]
                  and a["after_sha256"]
                  == chain3[i + 1]
                  for i, a in enumerate(appends3))
              and all(
                  draft.strip() not in
                  h3contents[address].decode("utf-8")
                  for draft, address in zip(
                      DRAFTS,
                      ("sources/stock-take.md",
                       "sources/a3-pass.md",
                       "sources/index-tail.md",
                       "sources/index-tail.md",
                       "sources/index-tail.md",
                       "sources/index-tail.md"))),
              f"{len(appends3)} journal appends")
        estimates3 = h3rep["call_estimates"]
        print(f"cycle3-honest: opening package "
              f"estimated at "
              f"{estimates3[0]['serialized_bytes']} "
              f"bytes / "
              f"{estimates3[0]['estimated_tokens']} "
              f"tokens; largest package "
              f"{max(e['serialized_bytes'] for e in estimates3)} "
              f"bytes / "
              f"{max(e['estimated_tokens'] for e in estimates3)} "
              f"tokens")
        check("cycle3-honest: every serialized "
              "request's estimate stands at or "
              "under the per-call budget of 4,000 "
              "tokens — the opening, carrying the "
              "step-by-step journal contract, "
              "included",
              len(estimates3) == 9
              and all(e["estimated_tokens"] <= 4000
                      for e in estimates3),
              f"{estimates3}")

        # ---- cycle3-batch: the batch wake ----
        t3rep = reports["cycle3_batch"]
        t3work = work / "cycle3-batch"
        t3evs = _events(t3work)
        t3gates = [e for e in t3evs
                   if e["type"] == "CYCLE_GATE"]
        check("cycle3-batch: the batch walk "
              "completes in nine iterations and "
              "files — the gate arithmetic stands "
              "exactly as under v1 and v2 (five "
              "cycle gates, cycles 1-5), and no "
              "budget refusal stands",
              t3rep["outcome"] == "yield"
              and t3rep["iterations"] == 9
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in t3evs)
              and [_payload(g)["cycle"]
                   for g in t3gates] == [1, 2, 3, 4, 5]
              and not any(
                  e["type"] == "BUDGET_REFUSAL"
                  for e in t3evs),
              f"{t3rep['outcome']} / "
              f"{t3rep['iterations']} / "
              f"{[_payload(g)['cycle'] for g in t3gates]}")
        estimates_t3 = t3rep["call_estimates"]
        print(f"cycle3-batch: largest package "
              f"{max(e['serialized_bytes'] for e in estimates_t3)} "
              f"bytes / "
              f"{max(e['estimated_tokens'] for e in estimates_t3)} "
              f"tokens")
        check("cycle3-batch: every serialized "
              "request's estimate stands at or "
              "under the per-call budget of 4,000 "
              "tokens — the batch wake included",
              len(estimates_t3) == 9
              and all(e["estimated_tokens"] <= 4000
                      for e in estimates_t3),
              f"{estimates_t3}")
        print(f"office-cycle-v3 section: "
              f"{CHECKS[0] - cycle3_before} checks")

        # ============= office cycle v4 — the
        # cleaned-opening successor (the director's
        # orders of 2026-11-25 21:33/21:36 MST,
        # after demo-gptoss7) =============
        # The successor contract's witnesses: the
        # opening is the director's plain-text
        # structure behind the compressed outcome
        # frame — his section headings and the
        # resolution-1 deliverable line stand in the
        # rendered prompt, and none of the stale
        # strings the v3 opening carried stand
        # anywhere in it (the key-points journal
        # line, the write-it-with-a-tool deliverable,
        # the contribute-is-NOT-the-deliverable
        # sentence, the shell memory line, a
        # catalogue JSON); the v3 opening stands
        # unchanged as the control; the honest walk
        # completes and files through the contribute
        # door; the batch walk completes and files;
        # and every measured package stands within
        # the per-call budget. The checker is not
        # run over these records: the ruling's
        # checker-correspondence deferral stands,
        # exactly as for the v2 and v3 sections
        # above.
        cycle4_before = CHECKS[0]

        def _cycle4_opening(scenario):
            """The v4 opening's rendered prompt, read
            from the wire the scenario's captures
            recorded: the first loop capture's user
            content — the compressed frame followed
            by the plain-text structure."""
            captures = [json.loads(line) for line in
                        (work / scenario
                         / "captures.jsonl")
                        .read_text().splitlines()
                        if line.strip()]
            chat = {c["index"]: c for c in captures
                    if c["mode"] == "chat"}
            body = json.loads(base64.b64decode(
                chat[1]["request_b64"]))
            for message in body.get("messages") or []:
                content = message.get("content")
                if isinstance(content, str) and \
                        "Opening package — " in content:
                    return content
            return ""

        # ---- cycle4-honest: the cleaned walk ----
        h4rep = reports["cycle4_honest"]
        h4work = work / "cycle4-honest"
        h4evs = _events(h4work)
        check("cycle4-honest: the honest path under "
              "the cleaned-opening seal completes in "
              "nine iterations and the brief stands "
              "filed through the contribute door — "
              "the v1, v2 and v3 paths' own shape",
              h4rep["outcome"] == "yield"
              and h4rep["iterations"] == 9
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in h4evs),
              f"{h4rep['outcome']} / "
              f"{h4rep['iterations']}")
        check("cycle4-honest: the sealed record "
              "declares the cleaned-opening contract, "
              "no worked example stands in the seal, "
              "the journal baseline is v1's, and the "
              "sealed block map is the v1 run's own "
              "map — the same portioning under the "
              "new name",
              h4rep["sealed_presentation_contract"]
              == "office-cycle-v4"
              and h4rep["sealed_worked_example"]
              is None
              and h4rep["sealed_journal_baseline"]
              == {"address": JOURNAL,
                  "initial_sha256": sha256_hex(b"")}
              and h4rep["sealed_block_map"]
              == crep["sealed_block_map"],
              f"{h4rep['sealed_presentation_contract']}")
        opening4 = _cycle4_opening("cycle4-honest")
        HEADINGS4 = ("Role & identity", "Task",
                     "Sources (must all be read)",
                     "Working method (cycles)",
                     "Tools available (only these)",
                     "Standing memory (role knowledge)",
                     "Position")
        check("cycle4-honest: the opening's user "
              "content is the compressed frame "
              "followed by the director's structure — "
              "the frame's first line stands at its "
              "head, the header names the seat, and "
              "every one of his section headings "
              "stands in it, in his order",
              opening4.startswith(
                  "You are a seat in a recorded "
                  "collaborative run. Answer with "
                  "exactly one JSON object")
              and "Opening package — crew-1"
              in opening4
              and all(h in opening4 for h in HEADINGS4)
              and [opening4.index(h) for h in HEADINGS4]
              == sorted(opening4.index(h)
                        for h in HEADINGS4),
              f"{opening4[:80]}")
        check("cycle4-honest: the deliverable line "
              "is the resolution-1 line — the brief "
              "delivered as the contribute outcome, "
              "the office files it at "
              "scratch/brief.md, only a filed brief "
              "completes the assignment",
              "Deliverable: the brief is delivered "
              "as the \"contribute\" outcome"
              in opening4
              and "the office files it at "
              "scratch/brief.md" in opening4
              and "only a filed brief completes "
              "the assignment" in opening4,
              "")
        STALE4 = ("log its name and the key points",
                  "Write it with a tool",
                  "\"contribute\" outcome is NOT "
                  "the deliverable",
                  "working shell",
                  "Your tool catalogue",
                  "Your wake package:",
                  "\"case_essentials\"",
                  "\"snapshot\"")
        check("cycle4-honest: none of the stale "
              "strings stand in the opening — not "
              "the key-points journal line, not the "
              "write-it-with-a-tool deliverable, not "
              "the contribute-is-NOT sentence, not "
              "the shell memory line, and no "
              "catalogue JSON or component assembly "
              "anywhere in it",
              all(s not in opening4 for s in STALE4),
              "")
        check("cycle4-honest: the v3 control's "
              "opening stands unchanged — its "
              "captured package is the JSON component "
              "assembly under the draft-page seal, "
              "carrying no opening_text and no "
              "plain-text structure; the successor's "
              "build left the v3 presentation "
              "untouched",
              "opening_text" not in opening3
              and opening3["presentation"]
              ["contract"] == "office-cycle-v3"
              and "Opening package — " not in
              canonical(opening3).decode(
                  "utf-8", "replace"),
              "")
        estimates4 = h4rep["call_estimates"]
        print(f"cycle4-honest: opening package "
              f"estimated at "
              f"{estimates4[0]['serialized_bytes']} "
              f"bytes / "
              f"{estimates4[0]['estimated_tokens']} "
              f"tokens; largest package "
              f"{max(e['serialized_bytes'] for e in estimates4)} "
              f"bytes / "
              f"{max(e['estimated_tokens'] for e in estimates4)} "
              f"tokens")
        check("cycle4-honest: every serialized "
              "request's estimate stands at or "
              "under the per-call budget of 4,000 "
              "tokens — the cleaned opening included",
              len(estimates4) == 9
              and all(e["estimated_tokens"] <= 4000
                      for e in estimates4),
              f"{estimates4}")

        # ---- cycle4-batch: the batch wake ----
        t4rep = reports["cycle4_batch"]
        t4work = work / "cycle4-batch"
        t4evs = _events(t4work)
        t4gates = [e for e in t4evs
                   if e["type"] == "CYCLE_GATE"]
        check("cycle4-batch: the batch walk "
              "completes in nine iterations and "
              "files — the gate arithmetic stands "
              "exactly as under v1, v2 and v3 (five "
              "cycle gates, cycles 1-5), and no "
              "budget refusal stands",
              t4rep["outcome"] == "yield"
              and t4rep["iterations"] == 9
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in t4evs)
              and [_payload(g)["cycle"]
                   for g in t4gates] == [1, 2, 3, 4, 5]
              and not any(
                  e["type"] == "BUDGET_REFUSAL"
                  for e in t4evs),
              f"{t4rep['outcome']} / "
              f"{t4rep['iterations']} / "
              f"{[_payload(g)['cycle'] for g in t4gates]}")
        estimates_t4 = t4rep["call_estimates"]
        print(f"cycle4-batch: largest package "
              f"{max(e['serialized_bytes'] for e in estimates_t4)} "
              f"bytes / "
              f"{max(e['estimated_tokens'] for e in estimates_t4)} "
              f"tokens")
        check("cycle4-batch: every serialized "
              "request's estimate stands at or "
              "under the per-call budget of 4,000 "
              "tokens — the batch wake included",
              len(estimates_t4) == 9
              and all(e["estimated_tokens"] <= 4000
                      for e in estimates_t4),
              f"{estimates_t4}")
        print(f"office-cycle-v4 section: "
              f"{CHECKS[0] - cycle4_before} checks")

        # ============= office cycle v5 — the
        # carryover successor (the director's
        # orders of 2026-11-25 22:09 MST, after
        # demo-gptoss8) =============
        # The successor contract's presentation
        # witnesses stand below: the statement line
        # from the sealed delivery declaration (the
        # stale "written with a tool" prose in no
        # v5 package), the journal gate's correction
        # riding the package after a refused append,
        # the journal carried as his draft so far
        # with the one next step stated, and
        # split-on-return standing. The brief's
        # remaining two witnesses — the honest and
        # batch walks completing and filing, and
        # every measured package within the 4,000
        # budget — DO NOT STAND, and this section
        # witnesses that exactly, as its closing
        # checks: the v4 walks already stood at
        # 3,880–3,996 estimated tokens on the
        # near-ceiling blocks (B3/B4/B5 at
        # 11,612/11,898/11,535 bytes against the
        # 16,000-byte budget line), and the
        # carryover's own content — the journal
        # whole, the corrections riding — carries
        # the cycle-4 and cycle-5 packages and the
        # batch wake over the line, where the
        # budget gate refuses them before the call.
        # The collision is the forced decision the
        # build's report carries; these checks pin
        # its measured shape so the ruling lands on
        # numbers, not impressions. The checker is
        # not run over these records: the ruling's
        # checker-correspondence deferral stands,
        # exactly as for the v2, v3 and v4 sections
        # above.
        cycle5_before = CHECKS[0]
        DRAFTS5 = [rehearsal.CYCLE_DRAFT_1,
                   rehearsal.CYCLE_DRAFT_2,
                   rehearsal.CYCLE_DRAFT_3,
                   rehearsal.CYCLE_DRAFT_4,
                   rehearsal.CYCLE_DRAFT_5,
                   rehearsal.CYCLE_DRAFT_6]

        # ---- cycle5-honest: the seal and the
        # opening ----
        h5rep = reports["cycle5_honest"]
        h5work = work / "cycle5-honest"
        h5evs = _events(h5work)
        h5pkg = _cycle_packages("cycle5-honest")
        check("cycle5-honest: the sealed record "
              "declares the carryover contract, no "
              "worked example stands in the seal, "
              "the journal baseline is v1's, and the "
              "sealed block map is the v1 run's own "
              "map — the same portioning under the "
              "new name",
              h5rep["sealed_presentation_contract"]
              == "office-cycle-v5"
              and h5rep["sealed_worked_example"]
              is None
              and h5rep["sealed_journal_baseline"]
              == {"address": JOURNAL,
                  "initial_sha256": sha256_hex(b"")}
              and h5rep["sealed_block_map"]
              == crep["sealed_block_map"],
              f"{h5rep['sealed_presentation_contract']}")
        opening5 = _cycle4_opening("cycle5-honest")
        check("cycle5-honest: the opening is v4's "
              "structure whole — the compressed "
              "frame, his section headings in his "
              "order, the resolution-1 deliverable "
              "line — with the contract line naming "
              "the sealed contract, office-cycle-v5, "
              "as it named v4 under the v4 seal",
              opening5.startswith(
                  "You are a seat in a recorded "
                  "collaborative run. Answer with "
                  "exactly one JSON object")
              and "Opening package — crew-1"
              in opening5
              and "- Contract: office-cycle-v5"
              in opening5
              and all(h in opening5 for h in HEADINGS4)
              and [opening5.index(h) for h in HEADINGS4]
              == sorted(opening5.index(h)
                        for h in HEADINGS4)
              and "Deliverable: the brief is "
              "delivered as the \"contribute\" "
              "outcome" in opening5,
              f"{opening5[:80]}")

        # ---- the statement line and the stale
        # prose (brief item 1) ----
        r5pkg = _cycle_packages("cycle5-rewrite")
        openings5 = [_cycle4_opening(s) for s in (
            "cycle5-honest", "cycle5-batch",
            "cycle5-rewrite")]
        wire5 = list(openings5)
        for pkg_map in (h5pkg, r5pkg):
            for k in sorted(pkg_map):
                wire5.append(canonical(
                    pkg_map[k][0]).decode(
                        "utf-8", "replace"))
        statements5 = [
            (h5pkg[k][0].get("cover") or {})
            .get("statement") or ""
            for k in sorted(h5pkg)] + [
            (r5pkg[k][0].get("cover") or {})
            .get("statement") or ""
            for k in sorted(r5pkg)]
        check("cycle5: the stale prose stands in "
              "no v5 package that went on the wire — "
              "not in the three walks' openings, not "
              "in any cycle package they reached — "
              "and every reached cycle package's "
              "statement line names the contribute "
              "door and the sealed destination, "
              "formatted from the delivery "
              "declaration (the §6 amendment's "
              "rebase, 2026-11-26: the walks run to "
              "completion under the road, so the "
              "statement count is the completed "
              "walks' package count, not the seven "
              "the budget stall used to leave)",
              all("written with a tool" not in blob
                  for blob in wire5)
              and len(statements5)
              == len(h5pkg) + len(r5pkg)
              and len(statements5) > 7
              and all(
                  "delivered as your contribute "
                  "outcome" in s
                  and "the office files it at "
                  "scratch/brief.md" in s
                  for s in statements5),
              f"{statements5[0][:100] if statements5 else ''}")

        # ---- the carryover and the next step
        # (brief item 3) ----
        pkg3_5 = h5pkg[3][0]
        pkg4_5 = h5pkg[4][0]
        check("cycle5-honest: the package after the "
              "first landed append carries the "
              "journal's current content as its "
              "centre — the journal_draft component "
              "holds the first draft exactly, "
              "labelled his draft so far — the next "
              "package carries the two drafts "
              "standing, and the first package's "
              "cycle instruction states the one next "
              "step: the append for the block whose "
              "read stands",
              (pkg3_5.get("journal_draft") or {})
              .get("content") == DRAFTS5[0]
              and "draft so far" in (
                  (pkg3_5.get("journal_draft") or {})
                  .get("label") or "")
              and (pkg4_5.get("journal_draft") or {})
              .get("content")
              == "".join(DRAFTS5[:2])
              and (pkg3_5.get("current_cycle") or {})
              .get("instruction") == (
                  "Next: append your summary of "
                  "sources/a3-pass.md to your "
                  "journal at scratch/journal.md — "
                  "the journal as it stands, plus "
                  "your summary at the end, in one "
                  "sandbox.write. That append "
                  "completes this cycle."),
              "")
        check("cycle5: the next step for a block "
              "whose read has not stood is the "
              "brief's own example made literal — "
              "read the block's lines, then append "
              "the summary — derived from the cycle "
              "state by the same derivation the "
              "packages carry",
              loop_module._cycle_next_step_v5(
                  {"address":
                   "sources/index-tail.md",
                   "line_start": 1, "line_end": 6,
                   "read_stands": False}, JOURNAL)
              == ("Next: read "
                  "sources/index-tail.md lines 1–6, "
                  "then append your summary of it "
                  "to your journal at "
                  "scratch/journal.md — the journal "
                  "as it stands, plus your summary "
                  "at the end, in one sandbox.write."),
              "")
        presented5 = {}
        for k in sorted(h5pkg):
            bc = h5pkg[k][0].get("block_content")
            if bc is not None:
                presented5.setdefault(
                    bc["block_id"], []).append(k)
        a3_text5 = (h5work / "run" / "sandbox"
                    / "sources/a3-pass.md").read_text()
        check("cycle5-honest: split-on-return "
              "stands under the carryover seal — "
              "each block's content is presented in "
              "the package where its read lands and "
              "not in the following package: B1..B6 "
              "at their own cycles' packages, and "
              "the a3-pass text stands nowhere in "
              "the package after its own (the §6 "
              "amendment's rebase: under the old "
              "budget the walk stalled at cycle 4 "
              "and only B1..B3 stood reached; the "
              "road carries the walk through all "
              "six)",
              presented5 == {f"B{i}": [i + 1]
                             for i in range(1, 7)}
              and a3_text5 not in canonical(
                  pkg4_5).decode("utf-8", "replace"),
              f"{presented5}")

        # ---- cycle5-rewrite: the refused append
        # and its correction (brief item 2) ----
        r5rep = reports["cycle5_rewrite"]
        r5work = work / "cycle5-rewrite"
        r5evs = _events(r5work)
        r5gates = [e for e in r5evs
                   if e["type"] == "JOURNAL_GATE"]
        corr5 = (r5pkg[4][0].get(
            "journal_gate_correction") or {})
        check("cycle5-rewrite: the scripted "
              "non-append write is refused — exactly "
              "one journal gate stands in the record "
              "— and the next package carries the "
              "gate's correction, derived fresh: "
              "what was refused (a write that did "
              "not begin with the journal as it "
              "stands) and the exact action that "
              "passes (the standing journal plus "
              "the new part at the end); the "
              "package's carried draft is the "
              "accepted journal still — the rewrite "
              "did not move it",
              len(r5gates) == 1
              and "did not begin with your journal "
              "as it stands" in corr5.get(
                  "what_arrived", "")
              and "what stands, plus your new "
              "bits appended at the end" in corr5.get(
                  "instruction", "")
              and (r5pkg[4][0].get("journal_draft")
                   or {}).get("content")
              == DRAFTS5[0],
              f"{len(r5gates)} journal gates")

        # ---- cycle5-batch: the gate arithmetic
        # across the completed walk ----
        t5rep = reports["cycle5_batch"]
        t5work = work / "cycle5-batch"
        t5evs = _events(t5work)
        t5gates = [e for e in t5evs
                   if e["type"] == "CYCLE_GATE"]
        check("cycle5-batch: the cycle gate's "
              "arithmetic stands exactly as under "
              "v1–v4 — each batch wake's build "
              "records the gate for the cycle its "
              "run-ahead left standing, its "
              "correction computed into that "
              "package: cycles 1..5 gated in order "
              "across the walk (the §6 amendment's "
              "rebase: the old budget refused the "
              "first batch wake, so only the "
              "cycle-1 gate ever stood; under the "
              "road the walk completes and every "
              "gate stands)",
              [_payload(g)["cycle"] for g in t5gates]
              == [1, 2, 3, 4, 5],
              f"{[_payload(g)['cycle'] for g in t5gates]}")

        # ---- the road's completion (the §6
        # amendment's rebase, 2026-11-26: this
        # section witnessed the budget collision —
        # the three v5 walks stalling on the
        # per-call budget at their measured joints,
        # the carryover's cost made visible. The
        # amendment retired the refusal: the same
        # walks, at the same joints, are now paced
        # and counted instead of refused, and run
        # to their filings. The collision's figures
        # stand in the record above; what stands
        # witnessed here is that nothing refuses
        # anymore and the cost is still measured —
        # every call's road event, predicted and
        # reconciled, in each walk's report) ----
        def _refusals(evs):
            return [e for e in evs
                    if e["type"] == "BUDGET_REFUSAL"]

        check("cycle5-honest: under the road the "
              "walk completes — nine iterations, no "
              "budget refusal anywhere in the "
              "record, the brief filed, and ten "
              "road-governed calls stand in the "
              "report (the identify and the nine "
              "loop calls), each with its predicted "
              "and reconciled figures",
              h5rep["outcome"] == "yield"
              and h5rep["iterations"] == 9
              and not _refusals(h5evs)
              and any(
                  e["type"] == "DELIVERABLE_FILED"
                  for e in h5evs)
              and len(h5rep["road_transport_events"])
              == 10,
              f"{h5rep['outcome']} / "
              f"{h5rep['iterations']} / "
              f"{len(h5rep['road_transport_events'])} "
              f"road events")
        check("cycle5-batch: under the road the "
              "batch wake is paced, not refused — "
              "the walk completes in nine "
              "iterations, no budget refusal "
              "stands, the brief is filed, and ten "
              "road-governed calls stand in the "
              "report",
              t5rep["outcome"] == "yield"
              and t5rep["iterations"] == 9
              and not _refusals(t5evs)
              and any(
                  e["type"] == "DELIVERABLE_FILED"
                  for e in t5evs)
              and len(t5rep["road_transport_events"])
              == 10,
              f"{t5rep['outcome']} / "
              f"{t5rep['iterations']} / "
              f"{len(t5rep['road_transport_events'])} "
              f"road events")
        check("cycle5-rewrite: under the road the "
              "rewrite walk completes at the same "
              "joint the honest walk passes — ten "
              "iterations, no budget refusal, the "
              "brief filed, and eleven "
              "road-governed calls stand in the "
              "report",
              r5rep["outcome"] == "yield"
              and r5rep["iterations"] == 10
              and not _refusals(r5evs)
              and any(
                  e["type"] == "DELIVERABLE_FILED"
                  for e in r5evs)
              and len(r5rep["road_transport_events"])
              == 11,
              f"{r5rep['outcome']} / "
              f"{r5rep['iterations']} / "
              f"{len(r5rep['road_transport_events'])} "
              f"road events")
        for name5, rep5 in (
                ("cycle5-honest", h5rep),
                ("cycle5-batch", t5rep),
                ("cycle5-rewrite", r5rep)):
            est5 = rep5["call_estimates"]
            print(f"{name5}: largest package "
                  f"{max(e['serialized_bytes'] for e in est5)} "
                  f"bytes / "
                  f"{max(e['estimated_tokens'] for e in est5)} "
                  f"tokens (every package the walk "
                  f"sent, the road's accounting "
                  f"standing over each)")
        print(f"office-cycle-v5 section: "
              f"{CHECKS[0] - cycle5_before} checks")

        # ---- office-cycle-v6: zero carryover and
        # the slimmed blocks ----
        # The director's rulings of 2026-11-25
        # 22:29/22:30 MST, answering the collision
        # the v5 section above pins: item 3 reversed
        # (zero carryover — the journal is
        # append-never-carry; it stands in his
        # scratch and he reads it himself; the only
        # carry is the intro brief carrying him to
        # the next part of the job) and the block
        # bookkeeping slimmed by his tap, which is
        # what makes room at the batch joint for the
        # corrections that ride. The v5 section
        # stands unaltered above — its collision
        # witnesses are the record of why this
        # contract exists. The checker is not run
        # over these records: the ruling's
        # checker-correspondence deferral stands,
        # exactly as for the v2–v5 sections above.
        cycle6_before = CHECKS[0]
        DRAFTS6 = [rehearsal.CYCLE_DRAFT_1,
                   rehearsal.CYCLE_DRAFT_2,
                   rehearsal.CYCLE_DRAFT_3,
                   rehearsal.CYCLE_DRAFT_4,
                   rehearsal.CYCLE_DRAFT_5,
                   rehearsal.CYCLE_DRAFT_6]

        # ---- cycle6-honest: the seal and the
        # opening ----
        h6rep = reports["cycle6_honest"]
        h6work = work / "cycle6-honest"
        h6evs = _events(h6work)
        h6pkg = _cycle_packages("cycle6-honest")
        check("cycle6-honest: the sealed record "
              "declares the zero-carryover contract, "
              "no worked example stands in the seal, "
              "the journal baseline is v1's, and the "
              "sealed block map is the v1 run's own "
              "map — the same portioning under the "
              "new name",
              h6rep["sealed_presentation_contract"]
              == "office-cycle-v6"
              and h6rep["sealed_worked_example"]
              is None
              and h6rep["sealed_journal_baseline"]
              == {"address": JOURNAL,
                  "initial_sha256": sha256_hex(b"")}
              and h6rep["sealed_block_map"]
              == crep["sealed_block_map"],
              f"{h6rep['sealed_presentation_contract']}")
        opening6 = _cycle4_opening("cycle6-honest")
        check("cycle6-honest: the opening is v5's "
              "structure whole — the compressed "
              "frame, his section headings in his "
              "order, the resolution-1 deliverable "
              "line — with the contract line naming "
              "the sealed contract, office-cycle-v6",
              opening6.startswith(
                  "You are a seat in a recorded "
                  "collaborative run. Answer with "
                  "exactly one JSON object")
              and "Opening package — crew-1"
              in opening6
              and "- Contract: office-cycle-v6"
              in opening6
              and all(h in opening6 for h in HEADINGS4)
              and [opening6.index(h) for h in HEADINGS4]
              == sorted(opening6.index(h)
                        for h in HEADINGS4)
              and "Deliverable: the brief is "
              "delivered as the \"contribute\" "
              "outcome" in opening6,
              f"{opening6[:80]}")

        # ---- zero carryover (brief item 1) ----
        t6rep = reports["cycle6_batch"]
        t6work = work / "cycle6-batch"
        t6evs = _events(t6work)
        t6pkg = _cycle_packages("cycle6-batch")
        r6rep = reports["cycle6_rewrite"]
        r6work = work / "cycle6-rewrite"
        r6evs = _events(r6work)
        r6pkg = _cycle_packages("cycle6-rewrite")

        def _no_draft_carried(package):
            """No journal content carried in a
            package: no component holds any draft's
            text — except inside the one tool-results
            entry answering his own journal read,
            which is his pull answered once, not
            carriage."""
            for key, value in package.items():
                if key == "tool_results":
                    for entry in value:
                        result = entry.get("result") \
                            if isinstance(entry, dict) \
                            else None
                        if isinstance(result, dict) \
                                and result.get("path") \
                                == JOURNAL:
                            continue
                        blob = canonical(entry).decode(
                            "utf-8", "replace")
                        if any(d[:40] in blob
                               for d in DRAFTS6):
                            return False
                    continue
                blob = canonical(value).decode(
                    "utf-8", "replace")
                if any(d[:40] in blob for d in DRAFTS6):
                    return False
            return True

        all6 = [h6pkg[k][0] for k in sorted(h6pkg)] \
            + [t6pkg[k][0] for k in sorted(t6pkg)] \
            + [r6pkg[k][0] for k in sorted(r6pkg)]
        check("cycle6: zero carryover — no package "
              "in any of the three walks carries a "
              "journal_draft component, and no landed "
              "append's text is findable in the "
              "package that follows it or in any "
              "later package: the journal stands in "
              "his scratch, and what reaches him is "
              "the intro alone (his own journal read, "
              "where he pulls it, is answered once "
              "under its own ID, as any pull is)",
              all("journal_draft" not in pkg
                  for pkg in all6)
              and all(_no_draft_carried(pkg)
                      for pkg in all6),
              "")
        direction6 = (h6pkg[2][0].get(
            "presentation") or {}).get("direction")
        summarize6 = next(
            h6pkg[k][0] for k in sorted(h6pkg)
            if (h6pkg[k][0].get("presentation")
                or {}).get("package") == "summarize")
        check("cycle6-honest: the cycle direction "
              "states the truth again in the job's "
              "plain words — the journal is not "
              "carried; it stands in his scratch at "
              "scratch/journal.md; he reads it when "
              "he needs it, a pull like any other — "
              "and the summarize package's intro "
              "sends him to read his journal whole "
              "and combine, naming the sealed "
              "destination",
              direction6
              == loop_module.CYCLE_DIRECTION_CYCLE_V6
              .format(journal=JOURNAL)
              and "Read your journal whole and "
              "assemble the brief from the draft "
              "that stands in it" in (
                  (summarize6.get("presentation")
                   or {}).get("direction") or "")
              and "Read your journal whole, with "
              "sandbox.read at scratch/journal.md"
              in ((summarize6.get("current_cycle")
                   or {}).get("instruction") or "")
              and "the office files it at "
              "scratch/brief.md" in (
                  (summarize6.get("current_cycle")
                   or {}).get("instruction") or ""),
              f"{direction6}")

        # ---- the slimmed blocks (brief item 2) ----
        blocks6 = [entry for pkg in all6
                   for entry in pkg.get("blocks") or []]
        check("cycle6: the blocks component is "
              "slimmed to place and state — every "
              "entry in every v6 cycle package "
              "carries exactly block_id and state, no "
              "address, no range, no sha256 or "
              "dispatch fingerprints — and the map "
              "still walks: the honest walk's "
              "summarize package stands all six "
              "blocks done, in order",
              len(blocks6) > 0
              and all(set(entry) == {"block_id",
                                     "state"}
                      for entry in blocks6)
              and summarize6.get("blocks") == [
                  {"block_id": f"B{i}",
                   "state": "done"}
                  for i in range(1, 7)],
              f"{blocks6[:2]}")

        # ---- items 1–2 of v5 stand (the statement
        # line; the corrections riding) ----
        openings6 = [_cycle4_opening(s) for s in (
            "cycle6-honest", "cycle6-batch",
            "cycle6-rewrite")]
        wire6 = list(openings6)
        for pkg_map in (h6pkg, r6pkg):
            for k in sorted(pkg_map):
                wire6.append(canonical(
                    pkg_map[k][0]).decode(
                        "utf-8", "replace"))
        statements6 = [
            (pkg.get("cover") or {}).get("statement")
            or "" for pkg in all6
            if (pkg.get("cover") or {})
            .get("statement")]
        check("cycle6: the stale prose stands in "
              "no v6 package that went on the wire, "
              "and every cycle package's statement "
              "line names the contribute door and "
              "the sealed destination, formatted "
              "from the delivery declaration — v5's "
              "item 1 whole under the new seal",
              all("written with a tool" not in blob
                  for blob in wire6)
              and len(statements6) > 0
              and all(
                  "delivered as your contribute "
                  "outcome" in s
                  and "the office files it at "
                  "scratch/brief.md" in s
                  for s in statements6),
              f"{statements6[0][:100] if statements6 else ''}")
        r6gates = [e for e in r6evs
                   if e["type"] == "JOURNAL_GATE"]
        corr6 = (r6pkg[4][0].get(
            "journal_gate_correction") or {})
        check("cycle6-rewrite: the scripted "
              "non-append write is refused — exactly "
              "one journal gate stands in the record "
              "— and the next package carries the "
              "gate's correction, derived fresh: "
              "what was refused and the exact action "
              "that passes (the standing journal "
              "plus the new part at the end) — v5's "
              "item 2 whole under the new seal",
              len(r6gates) == 1
              and "did not begin with your journal "
              "as it stands" in corr6.get(
                  "what_arrived", "")
              and "what stands, plus your new "
              "bits appended at the end" in corr6.get(
                  "instruction", ""),
              f"{len(r6gates)} journal gates")
        t6gates = [e for e in t6evs
                   if e["type"] == "CYCLE_GATE"]
        check("cycle6-batch: the cycle gate's "
              "correction rides the batch wake "
              "itself, on the wire at last — the "
              "wake the v5 seal refused before the "
              "call now carries the correction "
              "naming the cycle the walk stands on "
              "and the append that advances it (the "
              "gate arithmetic stands exactly as "
              "under v1–v5: five gates, cycles 1–5, "
              "each recorded as its append came due)",
              [_payload(g)["cycle"] for g in t6gates]
              == [1, 2, 3, 4, 5]
              and "cycle_gate_correction"
              in t6pkg[2][0]
              and "Append them at "
              "scratch/journal.md" in (
                  (t6pkg[2][0].get(
                      "cycle_gate_correction") or {})
                  .get("instruction") or ""),
              f"{[_payload(g)['cycle'] for g in t6gates]}")

        # ---- the walks complete and file, inside
        # the budget ----
        check("cycle6-honest: the honest walk "
              "completes in nine iterations and the "
              "brief stands filed — six appends, no "
              "budget refusal: the joint that "
              "stalled the v5 honest walk at "
              "iteration 5 now stands inside the "
              "budget",
              h6rep["outcome"] == "yield"
              and h6rep["iterations"] == 9
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in h6evs)
              and sum(1 for e in h6evs
                      if e["type"] == "JOURNAL_APPEND")
              == 6
              and not any(e["type"] == "BUDGET_REFUSAL"
                          for e in h6evs),
              f"{h6rep['outcome']} / "
              f"{h6rep['iterations']}")
        check("cycle6-batch: the batch walk "
              "completes in nine iterations and the "
              "brief stands filed — the batch wake "
              "sent, where the v5 seal's was refused "
              "at 4,243 estimated tokens",
              t6rep["outcome"] == "yield"
              and t6rep["iterations"] == 9
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in t6evs)
              and not any(e["type"] == "BUDGET_REFUSAL"
                          for e in t6evs),
              f"{t6rep['outcome']} / "
              f"{t6rep['iterations']}")
        check("cycle6-rewrite: the rewrite walk "
              "completes in ten iterations and the "
              "brief stands filed — six appends "
              "stand, the rewrite counted as none",
              r6rep["outcome"] == "yield"
              and r6rep["iterations"] == 10
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in r6evs)
              and sum(1 for e in r6evs
                      if e["type"] == "JOURNAL_APPEND")
              == 6
              and not any(e["type"] == "BUDGET_REFUSAL"
                          for e in r6evs),
              f"{r6rep['outcome']} / "
              f"{r6rep['iterations']}")
        for name6, rep6 in (
                ("cycle6-honest", h6rep),
                ("cycle6-batch", t6rep),
                ("cycle6-rewrite", r6rep)):
            est6 = rep6["call_estimates"]
            print(f"{name6}: largest package "
                  f"{max(e['serialized_bytes'] for e in est6)} "
                  f"bytes / "
                  f"{max(e['estimated_tokens'] for e in est6)} "
                  f"tokens")
        check("cycle6: every measured package in "
              "the three walks stands within the "
              "per-call budget of 4,000 estimated "
              "tokens — no package refused, none "
              "sent over the line",
              all(e["estimated_tokens"] <= 4000
                  for rep6 in (h6rep, t6rep, r6rep)
                  for e in rep6["call_estimates"]),
              "")
        print(f"office-cycle-v6 section: "
              f"{CHECKS[0] - cycle6_before} checks")

        # ---- office-cycle-v7: the package opens
        # with the step ----
        # The director's order of 2026-11-25 22:41
        # MST, after demo-gptoss9's packages were
        # seen on the live wire to describe state —
        # the cycle, the block, its read standing —
        # and leave the deciding to the worker.
        # Under this seal every package opens with
        # the Next line: the one next step stated
        # as an imperative, derived at presentation
        # from the cycle state the package opens,
        # the state below it as its support and the
        # gates' corrections standing below it
        # unmerged. Everything else is v6's whole:
        # zero carryover, the slimmed blocks, the
        # statement line from the seal, the riding
        # corrections. The checker is not run over
        # these records: the ruling's
        # checker-correspondence deferral stands,
        # exactly as for the v2–v6 sections above.
        cycle7_before = CHECKS[0]
        NEXT_READ_STOCK = (
            "Next: read sources/stock-take.md in "
            "full. Then append your summary of it "
            "to your journal.")
        NEXT_APPEND_STOCK = (
            "Next: append your summary of "
            "sources/stock-take.md to your journal "
            "— the standing journal plus your new "
            "part at the end, in one write.")
        NEXT_APPEND_A3 = (
            "Next: append your summary of "
            "sources/a3-pass.md to your journal "
            "— the standing journal plus your new "
            "part at the end, in one write.")
        NEXT_COMBINE = (
            "Next: read your journal at "
            "scratch/journal.md, combine its "
            "summaries into the brief (about 600 "
            "words), and deliver the brief as your "
            "contribute outcome.")

        # ---- cycle7-honest: the seal and the
        # opening ----
        h7rep = reports["cycle7_honest"]
        h7work = work / "cycle7-honest"
        h7evs = _events(h7work)
        h7pkg = _cycle_packages("cycle7-honest")
        check("cycle7-honest: the sealed record "
              "declares the imperative-first "
              "contract, no worked example stands "
              "in the seal, the journal baseline is "
              "v1's, and the sealed block map is "
              "the v1 run's own map — the same "
              "portioning under the new name",
              h7rep["sealed_presentation_contract"]
              == "office-cycle-v7"
              and h7rep["sealed_worked_example"]
              is None
              and h7rep["sealed_journal_baseline"]
              == {"address": JOURNAL,
                  "initial_sha256": sha256_hex(b"")}
              and h7rep["sealed_block_map"]
              == crep["sealed_block_map"],
              f"{h7rep['sealed_presentation_contract']}")
        opening7 = _cycle4_opening("cycle7-honest")
        opening6_again = _cycle4_opening(
            "cycle6-honest")
        check("cycle7-honest: the opening opens "
              "with the step — the compressed "
              "frame, then the first block's Next "
              "line, then the director's structure, "
              "byte-identical to the v6 opening "
              "but for the Next line and the "
              "contract line naming the sealed "
              "contract, office-cycle-v7",
              opening7.startswith(
                  "You are a seat in a recorded "
                  "collaborative run. Answer with "
                  "exactly one JSON object")
              and opening7.index(NEXT_READ_STOCK)
              < opening7.index(
                  "Opening package — crew-1")
              and opening7.replace(
                  NEXT_READ_STOCK + "\n\n", "", 1)
              .replace("office-cycle-v7",
                       "office-cycle-v6")
              == opening6_again
              and "- Contract: office-cycle-v7"
              in opening7
              and all(h in opening7
                      for h in HEADINGS4)
              and [opening7.index(h)
                   for h in HEADINGS4]
              == sorted(opening7.index(h)
                        for h in HEADINGS4),
              f"{opening7[:80]}")

        # ---- the derivation, in its four forms
        # ----
        _nl = loop_module._cycle_next_line_v7
        check("cycle7: the Next line's derivation "
              "in its four forms — the read in "
              "full, the read by range, the append "
              "where the read stands, and the "
              "combine at summarize — each derived "
              "from the state it opens, in the "
              "brief's own wordings",
              _nl({"address":
                   "sources/stock-take.md",
                   "line_start": None,
                   "line_end": None,
                   "read_stands": False},
                  JOURNAL) == NEXT_READ_STOCK
              and _nl({"address":
                       "sources/index-tail.md",
                       "line_start": 7,
                       "line_end": 13,
                       "read_stands": False},
                      JOURNAL)
              == ("Next: read "
                  "sources/index-tail.md lines "
                  "7–13. Then append your summary "
                  "of it to your journal.")
              and _nl({"address":
                       "sources/stock-take.md",
                       "line_start": None,
                       "line_end": None,
                       "read_stands": True},
                      JOURNAL) == NEXT_APPEND_STOCK
              and _nl(None, JOURNAL)
              == NEXT_COMBINE,
              "")

        # ---- every package opens with the step
        # ----
        t7rep = reports["cycle7_batch"]
        t7work = work / "cycle7-batch"
        t7evs = _events(t7work)
        t7pkg = _cycle_packages("cycle7-batch")
        r7rep = reports["cycle7_rewrite"]
        r7work = work / "cycle7-rewrite"
        r7evs = _events(r7work)
        r7pkg = _cycle_packages("cycle7-rewrite")
        s7rep = reports["cycle7_readstep"]
        s7work = work / "cycle7-readstep"
        s7evs = _events(s7work)
        s7pkg = _cycle_packages("cycle7-readstep")
        all7 = [h7pkg[k][0] for k in sorted(h7pkg)] \
            + [t7pkg[k][0] for k in sorted(t7pkg)] \
            + [r7pkg[k][0] for k in sorted(r7pkg)] \
            + [s7pkg[k][0] for k in sorted(s7pkg)]
        check("cycle7: every cycle and summarize "
              "package in all four walks opens "
              "with the Next line — it is the "
              "package's first component, ahead of "
              "the identity keys and every state "
              "component — and no package carries "
              "a journal_draft: v6's zero carryover "
              "stands whole under the new seal",
              len(all7) > 0
              and all(next(iter(pkg))
                      == "next_step"
                      for pkg in all7)
              and all(isinstance(
                  pkg["next_step"], str)
                  and pkg["next_step"].startswith(
                      "Next: ")
                  for pkg in all7)
              and all("journal_draft" not in pkg
                      for pkg in all7),
              "")
        check("cycle7-honest: the first cycle "
              "package opens with the append step "
              "for the block whose read stands — "
              "the stock-take, read in the "
              "opening's answer, its summary owed "
              "to the journal",
              h7pkg[2][0]["next_step"]
              == NEXT_APPEND_STOCK,
              f"{h7pkg[2][0].get('next_step')}")
        check("cycle7-readstep: a cycle package "
              "before the block's read opens with "
              "the read step itself — the stock-"
              "take in full, then the append it "
              "feeds — and the delivery stage "
              "gate's correction for the refused "
              "early contribution stands in the "
              "same package below it, unmerged: "
              "the Next line commands, the "
              "correction explains",
              s7pkg[2][0]["next_step"]
              == NEXT_READ_STOCK
              and "delivery_stage_gate_correction"
              in s7pkg[2][0]
              and list(s7pkg[2][0]).index(
                  "next_step")
              < list(s7pkg[2][0]).index(
                  "delivery_stage_gate_correction"),
              f"{s7pkg[2][0].get('next_step')}")
        check("cycle7-rewrite: the package "
              "following the refused rewrite opens "
              "with the append step that passes — "
              "a3-pass's summary, the standing "
              "journal plus the new part at the "
              "end — and the journal gate's "
              "correction stands below it, "
              "unmerged, naming what arrived",
              r7pkg[4][0]["next_step"]
              == NEXT_APPEND_A3
              and "did not begin with your "
              "journal as it stands" in (
                  (r7pkg[4][0].get(
                      "journal_gate_correction")
                   or {}).get("what_arrived", ""))
              and list(r7pkg[4][0]).index(
                  "next_step")
              < list(r7pkg[4][0]).index(
                  "journal_gate_correction"),
              f"{r7pkg[4][0].get('next_step')}")
        check("cycle7-batch: the batch wake "
              "opens with the append step for the "
              "cycle the walk stands on, the cycle "
              "gate's correction riding in the same "
              "package below it — the wake v5's "
              "seal refused and v6's carried, now "
              "commanded first",
              t7pkg[2][0]["next_step"]
              == NEXT_APPEND_STOCK
              and "cycle_gate_correction"
              in t7pkg[2][0],
              f"{t7pkg[2][0].get('next_step')}")
        summarize7 = next(
            h7pkg[k][0] for k in sorted(h7pkg)
            if (h7pkg[k][0].get("presentation")
                or {}).get("package") == "summarize")
        check("cycle7-honest: the summarize "
              "package opens with the combine "
              "step — read the journal at its "
              "address, combine its summaries "
              "into the brief, deliver by the "
              "contribute outcome",
              summarize7["next_step"]
              == NEXT_COMBINE,
              f"{summarize7.get('next_step')}")

        # ---- the walks complete and file, inside
        # the budget ----
        check("cycle7-honest: the honest walk "
              "completes in nine iterations and "
              "the brief stands filed — six "
              "appends, no budget refusal",
              h7rep["outcome"] == "yield"
              and h7rep["iterations"] == 9
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in h7evs)
              and sum(1 for e in h7evs
                      if e["type"] == "JOURNAL_APPEND")
              == 6
              and not any(e["type"] == "BUDGET_REFUSAL"
                          for e in h7evs),
              f"{h7rep['outcome']} / "
              f"{h7rep['iterations']}")
        check("cycle7-batch: the batch walk "
              "completes in nine iterations and "
              "the brief stands filed — no budget "
              "refusal, the Next line's cost "
              "standing inside the line at the "
              "batch joint",
              t7rep["outcome"] == "yield"
              and t7rep["iterations"] == 9
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in t7evs)
              and not any(e["type"] == "BUDGET_REFUSAL"
                          for e in t7evs),
              f"{t7rep['outcome']} / "
              f"{t7rep['iterations']}")
        check("cycle7-rewrite: the rewrite walk "
              "completes in ten iterations and "
              "the brief stands filed — six "
              "appends stand, the rewrite counted "
              "as none, no budget refusal",
              r7rep["outcome"] == "yield"
              and r7rep["iterations"] == 10
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in r7evs)
              and sum(1 for e in r7evs
                      if e["type"] == "JOURNAL_APPEND")
              == 6
              and not any(e["type"] == "BUDGET_REFUSAL"
                          for e in r7evs),
              f"{r7rep['outcome']} / "
              f"{r7rep['iterations']}")
        check("cycle7-readstep: the read-step "
              "walk completes in ten iterations "
              "and the brief stands filed — the "
              "refused early contribution counted "
              "as no delivery, six appends stand, "
              "no budget refusal",
              s7rep["outcome"] == "yield"
              and s7rep["iterations"] == 10
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in s7evs)
              and sum(1 for e in s7evs
                      if e["type"] == "JOURNAL_APPEND")
              == 6
              and not any(e["type"] == "BUDGET_REFUSAL"
                          for e in s7evs),
              f"{s7rep['outcome']} / "
              f"{s7rep['iterations']}")
        for name7, rep7 in (
                ("cycle7-honest", h7rep),
                ("cycle7-batch", t7rep),
                ("cycle7-rewrite", r7rep),
                ("cycle7-readstep", s7rep)):
            est7 = rep7["call_estimates"]
            print(f"{name7}: largest package "
                  f"{max(e['serialized_bytes'] for e in est7)} "
                  f"bytes / "
                  f"{max(e['estimated_tokens'] for e in est7)} "
                  f"tokens")
        check("cycle7: every measured package "
              "in the four walks stands within "
              "the per-call budget of 4,000 "
              "estimated tokens — no package "
              "refused, none sent over the line",
              all(e["estimated_tokens"] <= 4000
                  for rep7 in (h7rep, t7rep, r7rep,
                               s7rep)
                  for e in rep7["call_estimates"]),
              "")
        print(f"office-cycle-v7 section: "
              f"{CHECKS[0] - cycle7_before} checks")

        # ---- office-cycle-v8: the walk's unit is
        # the file ----
        # The director's orders of 2026-11-25
        # 23:03 MST (the blocks diagnosis: the
        # shipping crate had been made into his
        # task list — six blocks, six cycles, six
        # gates, journal drafts demanded per
        # quarter-document, while the brief's
        # sections cut across the blocks) and his
        # restatement of the job at 22:08 (read
        # file one, write the summary in the
        # journal, read file two, write the
        # summary, read file three, write the
        # summary, combine): under this seal the
        # walk's unit is the FILE — three files —
        # and the third file's four standing
        # line-range slices are plumbing inside
        # its step: no cycle gate, no cycle
        # advance and no journal append stands
        # between them, the cycle gate fires once
        # per file when the file's read and its
        # append both stand, and the evidence rule
        # is unchanged (all four ranges must stand
        # for the file to stand). Everything else
        # is v7's whole: the Next line first,
        # derived from the file state; zero
        # carryover; the statement line from the
        # seal; the corrections riding, derived
        # fresh. The checker is not run over these
        # records: the ruling's
        # checker-correspondence deferral stands,
        # exactly as for the v2–v7 sections above.
        cycle8_before = CHECKS[0]
        NEXT_PART_7_13 = (
            "Next: read sources/index-tail.md "
            "lines 7–13 — the next part of the "
            "file.")
        NEXT_PART_21_24 = (
            "Next: read sources/index-tail.md "
            "lines 21–24 — the next part of the "
            "file.")
        NEXT_APPEND_TAIL = (
            "Next: append your summary of "
            "sources/index-tail.md to your journal "
            "— the standing journal plus your new "
            "part at the end, in one write.")
        HEADINGS8 = ("Role & identity", "Task",
                     "Sources (must all be read)",
                     "Working method (files)",
                     "Tools available (only these)",
                     "Standing memory (role knowledge)",
                     "Position")

        # ---- cycle8-honest: the seal and the
        # opening ----
        h8rep = reports["cycle8_honest"]
        h8work = work / "cycle8-honest"
        h8evs = _events(h8work)
        h8pkg = _cycle_packages("cycle8-honest")
        check("cycle8-honest: the sealed record "
              "declares the file-grain contract, "
              "no worked example stands in the "
              "seal, the journal baseline is v1's, "
              "the sealed block map is the v1 "
              "run's own map, and the sealed file "
              "map groups it into the walk's three "
              "files — the two whole files one "
              "block each, index-tail its four",
              h8rep["sealed_presentation_contract"]
              == "office-cycle-v8"
              and h8rep["sealed_worked_example"]
              is None
              and h8rep["sealed_journal_baseline"]
              == {"address": JOURNAL,
                  "initial_sha256": sha256_hex(b"")}
              and h8rep["sealed_block_map"]
              == crep["sealed_block_map"]
              and h8rep["sealed_file_map"]
              == tool_policy.compute_file_map(
                  crep["sealed_block_map"])
              and [len(f["block_ids"])
                   for f in h8rep["sealed_file_map"]]
              == [1, 1, 4]
              and [f["file_id"]
                   for f in h8rep["sealed_file_map"]]
              == ["F1", "F2", "F3"],
              f"{h8rep['sealed_presentation_contract']}")
        opening8 = _cycle4_opening("cycle8-honest")
        check("cycle8-honest: the opening opens "
              "with the step — the compressed "
              "frame, then the first file's Next "
              "line, then the director's structure "
              "rendered at the file grain: the "
              "contract line names office-cycle-v8, "
              "the sources stand one line per "
              "file with the third noted as "
              "arriving in parts with its ranges, "
              "the method is the file rhythm, and "
              "the position counts files — File 1 "
              "of 3",
              opening8.startswith(
                  "You are a seat in a recorded "
                  "collaborative run. Answer with "
                  "exactly one JSON object")
              and opening8.index(NEXT_READ_STOCK)
              < opening8.index(
                  "Opening package — crew-1")
              and "- Contract: office-cycle-v8"
              in opening8
              and "File 1 of 3" in opening8
              and "- F1: sources/stock-take.md"
              in opening8
              and "- F3: sources/index-tail.md — "
              "arrives in parts (lines 1-6, "
              "lines 7-13, lines 14-20, "
              "lines 21-24), read part by part "
              "inside this file's step"
              in opening8
              and "Working method (files)"
              in opening8
              and all(h in opening8
                      for h in HEADINGS8)
              and [opening8.index(h)
                   for h in HEADINGS8]
              == sorted(opening8.index(h)
                        for h in HEADINGS8),
              f"{opening8[:80]}")

        # ---- the Next line's derivation at the
        # file grain ----
        _nl8 = loop_module._cycle_next_line_v8
        _f1_unread = {
            "file_id": "F1",
            "address": "sources/stock-take.md",
            "read_stands": False,
            "blocks": [{
                "address": "sources/stock-take.md",
                "line_start": None, "line_end": None,
                "read_stands": False}]}
        _f3_partial = {
            "file_id": "F3",
            "address": "sources/index-tail.md",
            "read_stands": False,
            "blocks": [
                {"address": "sources/index-tail.md",
                 "line_start": 1, "line_end": 6,
                 "read_stands": True},
                {"address": "sources/index-tail.md",
                 "line_start": 7, "line_end": 13,
                 "read_stands": False},
                {"address": "sources/index-tail.md",
                 "line_start": 14, "line_end": 20,
                 "read_stands": False},
                {"address": "sources/index-tail.md",
                 "line_start": 21, "line_end": 24,
                 "read_stands": False}]}
        _f3_read = dict(
            _f3_partial, read_stands=True,
            blocks=[dict(b, read_stands=True)
                    for b in _f3_partial["blocks"]])
        check("cycle8: the Next line's derivation "
              "at the file grain, in its forms — "
              "the whole file's read where the "
              "file stands unread, the next part's "
              "read inside a multi-part file, the "
              "append where the file's read "
              "stands, and the combine at "
              "summarize",
              _nl8(_f1_unread, JOURNAL)
              == NEXT_READ_STOCK
              and _nl8(_f3_partial, JOURNAL)
              == NEXT_PART_7_13
              and _nl8(_f3_read, JOURNAL)
              == NEXT_APPEND_TAIL
              and _nl8(None, JOURNAL)
              == NEXT_COMBINE,
              "")

        # ---- every package: the file grain's
        # shape ----
        t8rep = reports["cycle8_batch"]
        t8work = work / "cycle8-batch"
        t8evs = _events(t8work)
        t8pkg = _cycle_packages("cycle8-batch")
        all8 = [h8pkg[k][0] for k in sorted(h8pkg)] \
            + [t8pkg[k][0] for k in sorted(t8pkg)]
        check("cycle8: every cycle and summarize "
              "package in both walks opens with "
              "the Next line as its first "
              "component, carries the files "
              "component and no blocks component, "
              "names its position by file and "
              "never by cycle, and carries no "
              "journal_draft — v7's discipline "
              "whole at the file grain",
              len(all8) > 0
              and all(next(iter(pkg)) == "next_step"
                      for pkg in all8)
              and all(isinstance(
                  pkg["next_step"], str)
                  and pkg["next_step"].startswith(
                      "Next: ")
                  for pkg in all8)
              and all("files" in pkg
                      and "blocks" not in pkg
                      for pkg in all8)
              and all("file" in (
                  pkg.get("presentation") or {})
                  and "cycle" not in (
                      pkg.get("presentation") or {})
                  for pkg in all8)
              and all("journal_draft" not in pkg
                      for pkg in all8),
              "")

        # ---- the honest walk at the file
        # rhythm ----
        check("cycle8-honest: the first cycle "
              "package opens with the append step "
              "for the file whose read stands — "
              "the stock-take, read in the "
              "opening's answer, its summary owed "
              "to the journal",
              h8pkg[2][0]["next_step"]
              == NEXT_APPEND_STOCK,
              f"{h8pkg[2][0].get('next_step')}")
        check("cycle8-honest: inside the third "
              "file's step the walk does not "
              "advance — the package after its "
              "first part stands on file 3 with "
              "the part counted in its state, its "
              "Next line the next part's read, "
              "and the part's content at the "
              "package's centre",
              (h8pkg[4][0].get("presentation")
               or {}).get("file") == 3
              and h8pkg[4][0]["files"] == [
                  {"file_id": "F1", "state": "done"},
                  {"file_id": "F2", "state": "done"},
                  {"file_id": "F3",
                   "state": "current (1 of 4 parts "
                            "read)"}]
              and h8pkg[4][0]["next_step"]
              == NEXT_PART_7_13
              and (h8pkg[4][0].get("block_content")
                   or {}).get("block_id") == "B3",
              f"{h8pkg[4][0].get('next_step')}")
        check("cycle8-honest: two parts pulled "
              "in one answer present split inside "
              "the step — the most recent part's "
              "content at the centre, the earlier "
              "part standing as its pointer in "
              "the file's state, no correction of "
              "any gate in the package, the walk "
              "still on file 3, its Next line the "
              "last part's read",
              (h8pkg[5][0].get("block_content")
               or {}).get("block_id") == "B5"
              and h8pkg[5][0]["files"][2]["state"]
              == "current (3 of 4 parts read)"
              and "cycle_gate_correction"
              not in h8pkg[5][0]
              and "journal_gate_correction"
              not in h8pkg[5][0]
              and (h8pkg[5][0].get("presentation")
                   or {}).get("file") == 3
              and h8pkg[5][0]["next_step"]
              == NEXT_PART_21_24,
              f"{h8pkg[5][0].get('next_step')}")
        check("cycle8-honest: the file's step "
              "completes only when its last part "
              "stands — the package after it "
              "opens with the file's append step, "
              "the last part's content at its "
              "centre",
              h8pkg[6][0]["next_step"]
              == NEXT_APPEND_TAIL
              and (h8pkg[6][0].get("block_content")
                   or {}).get("block_id") == "B6",
              f"{h8pkg[6][0].get('next_step')}")
        summarize8 = next(
            h8pkg[k][0] for k in sorted(h8pkg)
            if (h8pkg[k][0].get("presentation")
                or {}).get("package") == "summarize")
        check("cycle8-honest: the summarize "
              "package opens with the combine "
              "step, as v7's does — read the "
              "journal, combine its summaries, "
              "deliver by the contribute outcome",
              summarize8["next_step"] == NEXT_COMBINE
              and (summarize8.get("current_file")
                   or {}).get("stage") == "summarize",
              f"{summarize8.get('next_step')}")
        check("cycle8-honest: the honest walk "
              "completes in eight iterations and "
              "the brief stands filed — THREE "
              "journal appends stand, attributed "
              "to the three files in order, NO "
              "cycle gate event stands anywhere "
              "in the walk (no gate fires between "
              "a file's parts, and no file ran "
              "ahead), and no budget refusal",
              h8rep["outcome"] == "yield"
              and h8rep["iterations"] == 8
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in h8evs)
              and [_payload(e).get("cycle")
                   for e in h8evs
                   if e["type"] == "JOURNAL_APPEND"]
              == [1, 2, 3]
              and not any(e["type"] == "CYCLE_GATE"
                          for e in h8evs)
              and not any(e["type"] == "BUDGET_REFUSAL"
                          for e in h8evs),
              f"{h8rep['outcome']} / "
              f"{h8rep['iterations']}")

        # ---- the batch walk: one gate, at the
        # file grain ----
        check("cycle8-batch: the batch wake "
              "opens with the append step for the "
              "file the walk stands on, the cycle "
              "gate's correction riding below it "
              "in file words — the file it names "
              "F1, its instruction still on file "
              "F1, the arrival it answers the "
              "read of file F2 — and the wake "
              "presents the first file's content "
              "alone: its read stubbed to the "
              "block_content component, the other "
              "two files' reads not carried at "
              "all",
              t8pkg[2][0]["next_step"]
              == NEXT_APPEND_STOCK
              and "cycle_gate_correction"
              in t8pkg[2][0]
              and (t8pkg[2][0].get(
                      "cycle_gate_correction")
                   or {}).get("file_id") == "F1"
              and "file F1" in (
                  (t8pkg[2][0].get(
                      "cycle_gate_correction")
                   or {}).get("instruction", ""))
              and "file F2" in (
                  (t8pkg[2][0].get(
                      "cycle_gate_correction")
                   or {}).get("what_arrived", ""))
              and (t8pkg[2][0].get("block_content")
                   or {}).get("block_id") == "B1"
              and len(t8pkg[2][0].get(
                  "tool_results") or []) == 1
              and ((t8pkg[2][0]["tool_results"][0]
                    .get("result") or {})
                   .get("presented_in"))
              == "block_content",
              f"{t8pkg[2][0].get('next_step')}")
        check("cycle8-batch: the batch walk "
              "completes in six iterations and "
              "the brief stands filed — the gate "
              "arithmetic stands at the file "
              "grain exactly as v1's stands at "
              "the block grain (five gates over "
              "six blocks there): TWO cycle gate "
              "events, at files 1 and 2, each "
              "recorded at the wake its append "
              "came due with a later file's read "
              "standing ahead — and none at file "
              "3, whose parts never owe one — "
              "three appends attributed to the "
              "three files, no budget refusal",
              t8rep["outcome"] == "yield"
              and t8rep["iterations"] == 6
              and any(e["type"] == "DELIVERABLE_FILED"
                      for e in t8evs)
              and [_payload(e).get("cycle")
                   for e in t8evs
                   if e["type"] == "CYCLE_GATE"]
              == [1, 2]
              and [_payload(e).get("cycle")
                   for e in t8evs
                   if e["type"] == "JOURNAL_APPEND"]
              == [1, 2, 3]
              and not any(e["type"] == "BUDGET_REFUSAL"
                          for e in t8evs),
              f"{t8rep['outcome']} / "
              f"{t8rep['iterations']}")
        for name8, rep8 in (
                ("cycle8-honest", h8rep),
                ("cycle8-batch", t8rep)):
            est8 = rep8["call_estimates"]
            print(f"{name8}: largest package "
                  f"{max(e['serialized_bytes'] for e in est8)} "
                  f"bytes / "
                  f"{max(e['estimated_tokens'] for e in est8)} "
                  f"tokens")
        check("cycle8: every measured package "
              "in both walks stands within the "
              "per-call budget of 4,000 estimated "
              "tokens — no package refused, none "
              "sent over the line",
              all(e["estimated_tokens"] <= 4000
                  for rep8 in (h8rep, t8rep)
                  for e in rep8["call_estimates"]),
              "")
        print(f"office-cycle-v8 section: "
              f"{CHECKS[0] - cycle8_before} checks")

        # ============ cycle9-reread: the process tree
        # (office-cycle-v9; the build scope of
        # 2026-11-26, acceptance stage 1) ============
        cycle9_before = CHECKS[0]
        rep9 = reports["cycle9_reread"]
        pkg9 = _cycle_packages("cycle9-reread")
        check("cycle9-reread: the sealed record "
              "declares office-cycle-v9 and carries "
              "the sealed process tree beside it — "
              "six nodes, the redrawn tree of the "
              "settled method",
              rep9["sealed_presentation_contract"]
              == "office-cycle-v9"
              and (rep9["sealed_tree"] or {}).get(
                  "contract")
              == "process-tree-checklist-v1"
              and len((rep9["sealed_tree"] or {}).get(
                  "nodes") or []) == 6,
              f"{rep9['sealed_presentation_contract']}")
        evs9 = _events(work / "cycle9-reread")
        check("cycle9-reread: the walk files its "
              "brief — the re-read knock did not "
              "strand it",
              any(e["type"] == "DELIVERABLE_FILED"
                  and _payload(e).get("destination")
                  == "scratch/brief.md" for e in evs9),
              f"{rep9['outcome']}")
        opening9 = _cycle4_opening("cycle9-reread")
        check("cycle9-reread: the opening package "
              "carries the process tree — the map in "
              "hand from the first wake, the "
              "onboarding node standing current",
              "Process tree — The Brief" in opening9
              and "[current] 1. Know the job"
              in opening9,
              "")
        all9 = [pkg9[k][0] for k in sorted(pkg9)]
        refusal_pkg = None
        for pkg in all9:
            for entry in pkg.get(
                    "tool_results") or []:
                if isinstance(entry, dict) and \
                        entry.get(
                            "refusal_class") == \
                        "doorway_refused":
                    refusal_pkg = pkg
        check("cycle9-reread: a package presents "
              "the doorway's refusal of the re-read "
              "knock",
              refusal_pkg is not None, "")
        if refusal_pkg is not None:
            refusal_entry = next(
                entry for entry in refusal_pkg[
                    "tool_results"]
                if isinstance(entry, dict) and
                entry.get("refusal_class")
                == "doorway_refused")
            check("cycle9-reread: the refusal SPEAKS "
                  "— it names what the worker already "
                  "holds whole and the next act, the "
                  "journal bit for the held source "
                  "(Amendment 2: the correction names "
                  "the next action, not only the "
                  "state)",
                  "You already hold, whole:"
                  in (refusal_entry.get("error") or "")
                  and "Your next act is to write "
                  "the journal bit for the held "
                  "source that lacks one"
                  in (refusal_entry.get("error") or ""),
                  f"{refusal_entry.get('error')}")
            nodes9 = {
                node["id"]: node
                for node in (refusal_pkg.get(
                    "process_tree") or {}).get(
                        "nodes") or []}
            check("cycle9-reread: the tree in the "
                  "same package agrees with the "
                  "refusal — one computation: the "
                  "first gather node stands current, "
                  "its source held whole with reads "
                  "closed, summarize blocked on the "
                  "unfinished gathers",
                  nodes9.get(
                      "gather-stock-take", {}).get(
                          "state") == "current"
                  and any(
                      "you hold this source whole"
                      in fact
                      for fact in nodes9.get(
                          "gather-stock-take", {}).get(
                              "facts") or [])
                  and nodes9.get(
                      "summarize", {}).get("state")
                  == "blocked",
                  f"{nodes9}")
        check("cycle9-reread: every cycle package "
              "carries the process tree component",
              all("process_tree" in pkg
                  for pkg in all9
                  if "tool_results" in pkg),
              "")
        first_cycle9 = all9[0] if all9 else {}
        check("cycle9-reread: the journal read at "
              "the walk's first step stands answered "
              "— the office stocked the journal empty "
              "at generation, where demo-nemotron8's "
              "unstocked room failed the same read "
              "three times",
              any(isinstance(entry, dict)
                  and isinstance(
                      entry.get("result"), dict)
                  and entry["result"].get("path")
                  == JOURNAL
                  for entry in first_cycle9.get(
                      "tool_results") or []),
              "")
        check("cycle9-reread: the terminal readout "
              "rendered (the checker's v9 derivation "
              "stands deferred by the strip ruling — "
              "the scenario asserts its tree states "
              "against the record directly, as the "
              "plan names)",
              rep9["terminal_readout"]["rendered"]
              is True)
        print(f"office-cycle-v9 section: "
              f"{CHECKS[0] - cycle9_before} checks")

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
