"""Retrieval piece tests — structured, agent-directed
retrieval (RETRIEVAL-SCOPE-2026-11-23, Rev 5, accepted with
single carriage ruled inside the piece, INDEX 249), against
the scope's witnesses R1–R7 and the task's additional
witnesses:

- R1 discovery without contents: sandbox.list over the run
  sources returns structure maps — a small fraction of the
  corpus, no body text beyond headings;
- R2 selective retrieval: one named section crosses, exactly
  the section's bytes, and nothing else;
- R3 the bounds hold: an oversized range and an oversized
  whole-file read refused with the bound named, nothing
  partial returned; the aggregate bound — four ceiling-sized
  retrievals in one iteration, the fourth refused BEFORE
  execution (no dispatch recorded; the refusal names the
  aggregate bound and the remaining allowance), the formed
  package within the aggregate ceiling, serialized admission
  visible in the record's order; an uncertain outcome
  counting its full ceiling against the window; the
  byte-window path over a fixture line longer than the
  ceiling, with a multibyte character straddling the
  requested boundary — two slices, byte-for-byte
  reconstruction, the character in exactly one slice, the
  served windows recorded;
- R4 search within the wall, completely: labelled passages
  from permitted material only; a search outside sources/
  and a list of a non-permitted path refused; deterministic
  paging with total_matches and continuation, no duplicates
  and no silent gap; an ambiguous heading refused with the
  match count and line numbers named; an oversized matching
  line reported as a content-free stub;
- R5 successive, agent-directed retrieval through the real
  loop (list → search → read_range, each informed by the
  last), with the retention rule (an iteration-1 result not
  re-presented in iteration 3's package; re-pulling
  reproduces byte-identical content under the same hash),
  the notebook round-tripping under its own scratch grant,
  a non-scratch non-source path still refused, and SINGLE
  CARRIAGE: the record retains each result in full while
  the rendered package carries it exactly once — counted in
  the rendered request itself. Every rendered request of
  the run is measured (actual serialized size + the
  attempt-6 component breakdown), written to
  live-demo/retrieval-r5-measurements.json;
- R6 the whole-collection proof over R5's run;
- R7 checker correspondence: the R5 record replays clean
  under the independent checker with the v3 registry in
  both copies — plus the registry agreement battery, the
  historical exemption (a pre-v3 assembly's oversized read
  keeps its old shape and behaviour whole), and a forged
  provenance record the checker names divergent.

Run: PYTHONPATH=src python3 tests/unit/test_piece_retrieval.py
Exits 0 when every check passes.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from fabric.canonical import canonical, sha256_hex  # noqa: E402
from framework import projection  # noqa: E402
from framework import tool_policy as fw_policy  # noqa: E402
from framework.adapter import _render_prompt  # noqa: E402
from framework.doorway import (Doorway,  # noqa: E402
                               DoorwayRefusal)
from framework.executor import Executor  # noqa: E402
from framework.generator import Generator  # noqa: E402
from framework.loop import Loop  # noqa: E402
from framework.office import Office  # noqa: E402
from framework.record import (CONSTITUTION_HASH,  # noqa: E402
                              FrameworkStore)
import checker.tool_policy as ck_policy  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + "  " + detail)
    if not cond:
        FAILURES.append(name)


DECL = "I am ExampleModel 4.2, served by Provider P, build 9917."
PROVIDER_ID = "example/model-4.2"
SKILLS = [{"name": "drafting", "version": "1.2.0"}]
FULL = {"part": "part-A", "assignment": "Draft the A section",
        "verification_list": ["check the figures"]}
TRACE = "commission brief, crew seat"
BOUNDS = {"step_ceiling": 12, "deadline_seconds": 300}
CEILING = fw_policy.RETRIEVAL_RESULT_CEILING
AGGREGATE = fw_policy.RETRIEVAL_AGGREGATE_CEILING


def _grant(tool, prefix, count=60):
    return {"tool": tool, "scope_ceiling": {"path_prefix": prefix},
            "side_effect_class":
                "write" if tool == "sandbox.write" else "read",
            "bound": {"count": count},
            "authority_trace": TRACE}


GRANTS = [
    _grant("sandbox.list", "sources"),
    _grant("sandbox.read_range", "sources"),
    _grant("sandbox.read_range", "scratch"),
    _grant("sandbox.search", "sources"),
    _grant("sandbox.read", "sources"),
    _grant("sandbox.write", "scratch"),
]

# ------------------------------------------------------- fixtures
ALPHA_LINES = [
    "# Alpha Report",                                        # 1
    "",                                                      # 2
    "Opening line about the alpha survey.",                  # 3
    "",                                                      # 4
    "## Findings",                                           # 5
    "",                                                      # 6
    "The alpha findings marker QXZ-ALPHA-FINDINGS stands here.",  # 7
    "More findings detail follows here.",                    # 8
    "",                                                      # 9
    "## Methods",                                            # 10
    "",                                                      # 11
    "The methods section explains the alpha procedure.",     # 12
    "It spans two lines of method detail.",                  # 13
    "",                                                      # 14
    "## Findings",                                           # 15
    "",                                                      # 16
    "A second findings section, repeating the heading.",     # 17
    "",                                                      # 18
    "## Appendix",                                           # 19
    "",                                                      # 20
    "Appendix material for alpha, with the word lantern in it.",  # 21
]
BETA_LINES = [
    "# Beta Notes",                                          # 1
    "",                                                      # 2
    "## Summary",                                            # 3
    "",                                                      # 4
    "The beta summary mentions the word lantern once here.",  # 5
    "",                                                      # 6
    "## Details",                                            # 7
    "",                                                      # 8
    "Beta details: lantern appears again in this line.",     # 9
    "More beta detail without the word.",                    # 10
]
GAMMA_LINES = [
    "Gamma reference sheet line one.",
    "Gamma line two with the word compass.",
    "Gamma line three plain.",
]
MANY_LINES = [
    f"tally entry {i}" if i % 4 == 1 else f"filler line {i}"
    for i in range(1, 241)
]
STRADDLE_LINE = "a" * 11990 + "é" + "b" * 2000     # 13,992 bytes
LONGLINE_LINE = "a" * 11990 + "é" + "b" * 28000    # 39,992 bytes


def _text(lines):
    return ("\n".join(lines) + "\n").encode("utf-8")


CORPUS = {
    "sources/alpha.md": _text(ALPHA_LINES),
    "sources/beta.md": _text(BETA_LINES),
    "sources/gamma.log": _text(GAMMA_LINES),
    "sources/many.md": _text(MANY_LINES),
    "sources/straddle.md":
        ("# Straddle Fixture\n" + STRADDLE_LINE).encode("utf-8"),
    "sources/longline.md":
        ("# Long Line Fixture\n" + LONGLINE_LINE).encode("utf-8"),
}
UNSEALED = {"sources/unsealed.md":
            b"# Unsealed\n\nThis file was never sealed.\n"}
CORPUS_TOTAL = sum(len(b) for b in CORPUS.values())


def identify():
    return {"declaration": DECL, "provider_model_id": PROVIDER_ID}


def fresh(bounds=BOUNDS):
    path = os.path.join(tempfile.mkdtemp(), "run.db")
    store = FrameworkStore(path)
    store.insert_run("run-1", CONSTITUTION_HASH)
    brief = dict(FULL)
    if bounds is not None:
        brief["loop_bounds"] = dict(bounds)
    store.append("RUN_COMMISSIONED", "dir-1", [], {
        "run_id": "run-1",
        "tree": {"part-A": ["part-B"], "part-B": []},
        "seats": {
            "orch-1": {"role": "orchestrator",
                       "identity_status": "declared"},
            "exam-1": {"role": "examiner",
                       "identity_status": "declared"},
            "dir-1": {"role": "director",
                      "identity_status": "declared"},
            "crew-1": {"role": "crew",
                       "identity_status": "unverified"},
        },
        "briefs": {"crew-1": dict(brief)},
    })
    store.commit()
    d = Doorway(store)
    office = Office(d)
    gen = Generator(d)
    tok = {s: d.issue_token(s) for s in
           ("orch-1", "exam-1", "dir-1", "crew-1")}
    return store, d, office, gen, tok


def world(grants=GRANTS, retrieval=True, bounds=BOUNDS):
    """A complete retrieval world: the corpus staged in a
    sandbox, the sources sealed into the case's evidence
    boundary through the office route (as the first-worker
    harness seals them), a generated instance — declaring
    the retrieval contract, unless `retrieval` is False —
    activated over it, and the real executor on the sandbox.
    Returns (store, doorway, tokens, instance_token,
    executor, sandbox)."""
    base = tempfile.mkdtemp()
    sandbox = os.path.join(base, "sandbox")
    for rel, data in list(CORPUS.items()) + list(UNSEALED.items()):
        full = os.path.join(sandbox, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as fh:
            fh.write(data)
    store, d, office, gen, tok = fresh(bounds)
    for rel, data in CORPUS.items():
        digest = hashlib.sha256(data).hexdigest()
        d.act(tok["orch-1"], "MATERIAL_SEALED",
              {"material_id": f"{rel} sha256:{digest}",
               "boundary": ["crew-1"]},
              view_seq=store.head_seq())
    r = office.issue_new(tok["orch-1"], "crew-1")
    assert r["ok"], r
    d.act(tok["exam-1"], "CASE_JUDGED",
          {"case_id": "case-crew-1", "version": 1},
          view_seq=store.head_seq())
    office.authorise(tok["orch-1"], "case-crew-1", 1)
    gen.propose(tok["orch-1"], "crew-1", part="part-A",
                role_requirements="a careful drafting model")
    r = gen.generate(tok["orch-1"], "crew-1", identify,
                     skills=SKILLS, grants=grants,
                     retrieval=retrieval)
    assert r["ok"], r
    gen.verify(tok["orch-1"], r["assembly_id"])
    d.act(tok["exam-1"], "ASSEMBLY_JUDGED",
          gen.judgement(r["assembly_id"]),
          view_seq=store.head_seq())
    packed = gen.pack(tok["orch-1"], r["assembly_id"])
    gen.authorise(tok["orch-1"], r["assembly_id"])
    gen.activate(tok["orch-1"], r["assembly_id"])
    ex = Executor(d, sandbox,
                  claim_dir=os.path.join(base, "claims"),
                  deadline=5.0)
    return store, d, tok, packed["instance_token"], ex, sandbox


def refused(fn):
    try:
        fn()
    except DoorwayRefusal:
        return True
    return False


def events_of(store, type_):
    return [e for e in store.all_events() if e["type"] == type_]


def dispatch_and_execute(d, ex, itok, tool, parameters, rid):
    """One doorway dispatch, performed by the real executor;
    returns the dispatch summary. A refusal raises
    DoorwayRefusal, as the doorway raises it."""
    out = d.request_tool(itok, tool, parameters, rid)
    if not out.get("duplicate"):
        ex.execute(out["dispatch_id"])
    return out


def outcome_of(store, dispatch_id):
    for ev in events_of(store, "TOOL_OUTCOME"):
        if ev["payload"].get("dispatch_id") == dispatch_id:
            return ev["payload"]
    return None


def quiesce(store):
    store._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")


def run_checker(store):
    quiesce(store)
    req = {"store_path": store.path, "run_id": "run-1",
           "snapshot": projection.snapshot(store)}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=SRC)
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "checker"],
        input=json.dumps(req), capture_output=True, text=True,
        env=env, cwd=ROOT)
    return json.loads(proc.stdout)


class Script:
    """A scripted fake model, as the A3 suite's: each step is
    a response dict or a function of the package; every call
    is captured."""

    def __init__(self, steps):
        self.steps = list(steps)
        self.calls = []

    def __call__(self, package, budget=None, deadline=None):
        self.calls.append({"package": package, "budget": budget,
                           "deadline": deadline})
        step = self.steps.pop(0)
        if callable(step):
            return step(package)
        return step


def tool_req(*requests):
    return {"outcome": "tool_requests",
            "tool_requests": [{"tool": t, "parameters": p}
                              for t, p in requests]}


def yield_(summary="the work stands"):
    return {"outcome": "yield", "summary": summary}


# ---------------------------------------------------------- R1
def test_r1():
    store, d, tok, itok, ex, _ = world()
    listed = {}
    for path in ("sources/alpha.md", "sources/beta.md",
                 "sources/gamma.log"):
        out = dispatch_and_execute(
            d, ex, itok, "sandbox.list", {"path": path},
            f"r1-{os.path.basename(path)}")
        listed[path] = outcome_of(store, out["dispatch_id"])
    res = {p: o["result"] for p, o in listed.items()}
    alpha = res["sources/alpha.md"]
    rendered = alpha["content"].split("\n")[1:]
    check("R1 the alpha map names its headings with line numbers",
          rendered == ["line 1: # Alpha Report",
                       "line 5: ## Findings",
                       "line 10: ## Methods",
                       "line 15: ## Findings",
                       "line 19: ## Appendix"],
          json.dumps(rendered))
    check("R1 the map states size and line count",
          alpha["size_bytes"] == len(CORPUS["sources/alpha.md"])
          and alpha["line_count"] == 21)
    body_line = "Opening line about the alpha survey."
    check("R1 no body text crosses in a structure map",
          all(body_line not in r["content"]
              for r in res.values())
          and "QXZ-ALPHA-FINDINGS" not in alpha["content"])
    gamma = res["sources/gamma.log"]
    check("R1 a file kind without headings maps to header and "
          "line count only",
          gamma["line_count"] == 3
          and "\n" not in gamma["content"]
          and "Gamma line two" not in gamma["content"])
    total = sum(r["content_bytes"] for r in res.values())
    check("R1 discovery costs a small fraction of the corpus",
          total * 10 < CORPUS_TOTAL,
          f"{total} listed bytes vs {CORPUS_TOTAL} corpus bytes")
    check("R1 every list outcome records its authority path",
          all(o["result"]["authority_path"] == "source"
              for o in listed.values()))


# ---------------------------------------------------------- R2
def test_r2():
    store, d, tok, itok, ex, _ = world()
    out = dispatch_and_execute(
        d, ex, itok, "sandbox.read_range",
        {"path": "sources/alpha.md", "heading": "Methods"},
        "r2-methods")
    o = outcome_of(store, out["dispatch_id"])
    expected = "".join(line + "\n" for line in ALPHA_LINES[9:14])
    check("R2 the section crosses exactly — its own bytes and "
          "nothing else",
          o["outcome"] == "result"
          and o["result"]["content"] == expected,
          repr(o["result"]["content"][:60]))
    check("R2 the pull carries no findings material",
          "Findings" not in o["result"]["content"]
          and "QXZ" not in o["result"]["content"])
    check("R2 the outcome records the served span and hash",
          (o["result"]["start_line"], o["result"]["end_line"])
          == (10, 14)
          and o["result"]["content_bytes"]
          == len(expected.encode("utf-8"))
          and o["result"]["content_sha256"]
          == sha256_hex(expected.encode("utf-8")))


# ---------------------------------------------------------- R3
def test_r3_oversize_and_windows():
    store, d, tok, itok, ex, _ = world()
    out = dispatch_and_execute(
        d, ex, itok, "sandbox.read_range",
        {"path": "sources/longline.md", "start_line": 2,
         "end_line": 2}, "r3-oversize-range")
    o = outcome_of(store, out["dispatch_id"])
    check("R3 an oversized range is refused at execution with "
          "the bound named — nothing partial returned",
          o["outcome"] == "failure" and "12000" in o["detail"]
          and "result" not in o, o.get("detail", "")[:80])
    out = dispatch_and_execute(
        d, ex, itok, "sandbox.read",
        {"path": "sources/longline.md"}, "r3-oversize-read")
    o = outcome_of(store, out["dispatch_id"])
    check("R3 an oversized whole-file read is refused the same "
          "way under the governed regime",
          o["outcome"] == "failure" and "12000" in o["detail"])
    out = dispatch_and_execute(
        d, ex, itok, "sandbox.read",
        {"path": "sources/gamma.log"}, "r3-small-read")
    o = outcome_of(store, out["dispatch_id"])
    check("R3 a fitting read carries the retrieval provenance "
          "under the governed regime",
          o["outcome"] == "result"
          and o["result"]["content"]
          == CORPUS["sources/gamma.log"].decode("utf-8")
          and o["result"]["authority_path"] == "source"
          and o["result"]["content_bytes"]
          == len(CORPUS["sources/gamma.log"]))


def test_r3_straddle():
    store, d, tok, itok, ex, _ = world()
    line = STRADDLE_LINE.encode("utf-8")
    e_acute = "é".encode("utf-8")
    assert len(line) == 13992 and line[11990:11992] == e_acute
    slices = []
    windows = [(0, 11991), (11991, 13992)]
    for i, (bs, be) in enumerate(windows):
        out = dispatch_and_execute(
            d, ex, itok, "sandbox.read_range",
            {"path": "sources/straddle.md", "start_line": 2,
             "end_line": 2, "byte_start": bs, "byte_end": be},
            f"r3-slice-{i}")
        o = outcome_of(store, out["dispatch_id"])
        slices.append(o["result"])
    first, second = slices
    joined = (first["content"].encode("utf-8")
              + second["content"].encode("utf-8"))
    check("R3 two byte-window slices reconstruct the fixture "
          "line byte-for-byte",
          joined == line, f"{len(joined)} of {len(line)} bytes")
    check("R3 the straddling character appears whole in "
          "exactly one slice",
          e_acute in first["content"].encode("utf-8")
          and e_acute not in second["content"].encode("utf-8")
          and first["content"].endswith("é"))
    check("R3 the served windows are recorded — the start "
          "advanced past the straddler, the end extended to "
          "include it",
          (first["byte_start"], first["byte_end"]) == (0, 11992)
          and (second["byte_start"], second["byte_end"])
          == (11992, 13992)
          and (first["requested_byte_start"],
               first["requested_byte_end"]) == (0, 11991),
          json.dumps([(s["byte_start"], s["byte_end"])
                      for s in slices]))


def test_r3_aggregate_iteration():
    store, d, tok, itok, ex, _ = world()
    windows = [(0, 11991), (11991, 23988), (23988, 35985),
               (35985, 39992)]

    def four_requests(package):
        return tool_req(*[
            ("sandbox.read_range",
             {"path": "sources/longline.md", "start_line": 2,
              "end_line": 2, "byte_start": bs, "byte_end": be})
            for bs, be in windows])

    script = Script([four_requests, yield_()])
    result = Loop(d, itok, script, executor=ex).run()
    check("R3 the iteration holding the refused fourth "
          "retrieval still yields lawfully",
          result["outcome"] == "yield", str(result)[:80])
    evs = store.all_events()
    reqs = [e for e in evs if e["type"] == "TOOL_REQUESTED"]
    disps = [e for e in evs if e["type"] == "TOOL_DISPATCHED"]
    rejs = [e for e in evs if e["type"] == "REJECTION"
            and e["payload"].get("attempted_type")
            == "TOOL_DISPATCHED"]
    check("R3 three retrievals dispatched; the fourth refused "
          "with no dispatch recorded",
          len(reqs) == 4 and len(disps) == 3 and len(rejs) == 1,
          f"{len(reqs)} requests, {len(disps)} dispatches, "
          f"{len(rejs)} refusals")
    ground = rejs[0]["payload"]["ground"] if rejs else ""
    check("R3 the refusal names the aggregate bound and the "
          "remaining allowance",
          "36000" in ground and "leaving 15" in ground, ground)
    settled = {}
    for e in evs:
        p = e["payload"]
        if e["type"] == "TOOL_OUTCOME" and p.get("outcome") \
                == "result":
            settled[p["dispatch_id"]] = p["result"][
                "content_bytes"]
    check("R3 the settled window sums to the three served "
          "windows, within the aggregate ceiling",
          sum(settled.values()) == 35985
          and sum(settled.values()) <= AGGREGATE,
          json.dumps(settled))
    pkg2 = script.calls[1]["package"]
    carried = sum(tr["result"]["content_bytes"]
                  for tr in pkg2["tool_results"])
    check("R3 the package the fourth request would have "
          "joined carries exactly the admitted total",
          carried == 35985 and len(pkg2["tool_results"]) == 3)
    seq = {}
    for e in evs:
        if e["type"] == "TOOL_REQUESTED":
            seq.setdefault("req", []).append(e["event_seq"])
        elif e["type"] == "TOOL_OUTCOME":
            seq.setdefault("out", []).append(e["event_seq"])
    check("R3 admission is serialized: each outcome settles "
          "before the next request is admitted",
          all(seq["out"][i] < seq["req"][i + 1] for i in range(3)),
          json.dumps(seq))
    verdict = run_checker(store)
    check("R7 the checker recomputes the aggregate window "
          "clean (R3's store)",
          verdict["checks"]["dispatch_correspondence"]["result"]
          == "ok", json.dumps(verdict["checks"][
              "dispatch_correspondence"])[:160])


def test_r3_uncertain_counts_ceiling():
    store, d, tok, itok, ex, _ = world()

    def window(bs, be):
        return {"path": "sources/longline.md", "start_line": 2,
                "end_line": 2, "byte_start": bs, "byte_end": be}

    out = dispatch_and_execute(d, ex, itok, "sandbox.read_range",
                               window(0, 11991), "r3u-1")
    o = outcome_of(store, out["dispatch_id"])
    assert o["result"]["content_bytes"] == 11992
    out2 = d.request_tool(itok, "sandbox.read_range",
                          window(11991, 23988), "r3u-2")
    d.record_tool_outcome(
        out2["dispatch_id"], "uncertain",
        detail="witness: the outcome was never established")
    out3 = dispatch_and_execute(d, ex, itok, "sandbox.read_range",
                                window(23988, 35985), "r3u-3")
    o3 = outcome_of(store, out3["dispatch_id"])
    assert o3["result"]["content_bytes"] == 11997
    check("R3 with one settled window and one uncertainty the "
          "third is still admitted (35,989 ≤ 36,000 counting "
          "the uncertainty at its full ceiling)", True)
    hit = refused(lambda: d.request_tool(
        itok, "sandbox.read_range", window(35985, 39992),
        "r3u-4"))
    rejs = [e for e in events_of(store, "REJECTION")
            if e["payload"].get("request_id") == "r3u-4"]
    ground = rejs[0]["payload"]["ground"] if rejs else ""
    check("R3 the uncertainty counted at its ceiling: a "
          "fourth retrieval is refused, naming what remains",
          hit and "leaving 11" in ground, ground)
    verdict = run_checker(store)
    check("R7 the checker verifies the window including the "
          "outstanding uncertain dispatch at stall",
          verdict["checks"]["dispatch_correspondence"]["result"]
          == "ok", json.dumps(verdict["checks"][
              "dispatch_correspondence"])[:160])


# ---------------------------------------------------------- R4
def test_r4():
    store, d, tok, itok, ex, _ = world()
    out = dispatch_and_execute(
        d, ex, itok, "sandbox.search", {"query": "lantern"},
        "r4-lantern")
    o = outcome_of(store, out["dispatch_id"])
    r = o["result"]
    match_lines = [(p["path"], p["start"], p["end"])
                   for p in r["passages"]]
    check("R4 search returns labelled passages from permitted "
          "material, in (path, line) order",
          r["total_matches"] == 3 and r["returned"] == 3
          and r["continuation_offset"] is None
          and "sources/alpha.md:21:" in r["content"]
          and "sources/beta.md:5:" in r["content"]
          and "sources/beta.md:9:" in r["content"],
          json.dumps(match_lines))
    check("R4 the search outcome records the source path",
          r["authority_path"] == "source")
    check("R4 a search of a path outside sources/ is refused "
          "at the doorway",
          refused(lambda: d.request_tool(
              itok, "sandbox.search",
              {"query": "x", "path": "notes/secret.md"},
              "r4-outside")))
    check("R4 a list of a non-permitted path is refused at "
          "the doorway",
          refused(lambda: d.request_tool(
              itok, "sandbox.list", {"path": "notes/x.md"},
              "r4-list-outside")))
    check("R4 a read of an unsealed source is refused — the "
          "grant alone does not admit",
          refused(lambda: d.request_tool(
              itok, "sandbox.read_range",
              {"path": "sources/unsealed.md", "start_line": 1,
               "end_line": 1}, "r4-unsealed")))

    page_calls = [0]

    def page(offset):
        page_calls[0] += 1
        params = {"query": "tally"}
        if offset is not None:
            params["offset"] = offset
        out = dispatch_and_execute(
            d, ex, itok, "sandbox.search", params,
            f"r4-tally-{offset}-{page_calls[0]}")
        return outcome_of(store, out["dispatch_id"])["result"]

    p1 = page(None)
    p2 = page(p1["continuation_offset"])
    m1 = {ln for p in p1["passages"] for ln in p["match_lines"]}
    m2 = {ln for p in p2["passages"] for ln in p["match_lines"]}
    expected = {i for i in range(1, 241) if i % 4 == 1}
    check("R4 paging: every page states the total and its "
          "continuation",
          p1["total_matches"] == 60
          and p1["continuation_offset"] == p1["returned"]
          and 0 < p1["returned"] < 60
          and p2["total_matches"] == 60)
    check("R4 paging: no passage duplicated, no silent gap — "
          "pages continue in order under the line cap",
          not (m1 & m2) and max(m1) < min(m2)
          and m1 | m2 <= expected
          and all(p["end"] - p["start"] + 1 <= 40
                  for p in p1["passages"] + p2["passages"]),
          f"page sizes {len(m1)}, {len(m2)}")
    again = page(None)
    check("R4 paging is deterministic — the same query "
          "returns the identical page",
          again["content"] == p1["content"]
          and again["content_sha256"] == p1["content_sha256"])
    out = dispatch_and_execute(
        d, ex, itok, "sandbox.read_range",
        {"path": "sources/alpha.md", "heading": "Findings"},
        "r4-ambiguous")
    o = outcome_of(store, out["dispatch_id"])
    check("R4 an ambiguous heading is refused with the match "
          "count and line numbers named",
          o["outcome"] == "failure"
          and "matches 2 headings" in o["detail"]
          and "5, 15" in o["detail"], o.get("detail", ""))
    out = dispatch_and_execute(
        d, ex, itok, "sandbox.search", {"query": "b" * 5000},
        "r4-stub")
    o = outcome_of(store, out["dispatch_id"])
    r = o["result"]
    check("R4 an oversized matching line is a content-free "
          "stub, fetchable by byte window",
          r["total_matches"] == 1
          and r["passages"][0].get("stub") is True
          and r["passages"][0]["line_bytes"] == 39992
          and r["content"] == "",
          json.dumps(r["passages"])[:120])


# ------------------------------------------------- measurements
_SYSTEM = ("You are a seat in a recorded collaborative run. "
           "Answer exactly as the contract specifies.")
_MODEL = "openai/gpt-oss-120b"


def _esc(text):
    """The bytes a string contributes inside the enclosing
    JSON string of the transport body: its escaped length.
    Escaping is per-character, so spans partition exactly."""
    return len(json.dumps(text)) - 2


def _embedded_span(value):
    """The span a value occupies as a top-level value of an
    indent=1 dump: its standalone dump with one space of
    indentation added after each newline."""
    return json.dumps(value, indent=1, default=str).replace(
        "\n", "\n ")


def measure_request(package):
    """Render one captured loop package exactly as the
    adapter renders it and the connectors carry it (the
    attempt-6 method, INDEX 247), and attribute every byte
    to the attempt-6 categories. The partition is exact —
    verified by reconstructing the prompt and the dump from
    their parts — so the components sum to the serialized
    size with residual zero."""
    from framework.adapter import _CONTRACT, _TOOL_SECTION
    prompt = _render_prompt(package)
    body_pkg = {k: v for k, v in package.items() if k != "tools"}
    dump = json.dumps(body_pkg, indent=1, default=str)
    tools_dump = json.dumps(package["tools"], indent=1,
                            default=str)
    prefix = _CONTRACT + "\n\nYour wake package:\n"
    assert prompt == prefix + dump + _TOOL_SECTION + tools_dump
    items = [" " + json.dumps(k) + ": " + _embedded_span(v)
             for k, v in body_pkg.items()]
    assert dump == "{\n" + ",\n".join(items) + "\n}"
    body = json.dumps({"model": _MODEL, "messages": [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": prompt}],
        "temperature": 0.2})
    final = len(body.encode("utf-8"))
    retrieved = 0
    for tr in package.get("tool_results", []):
        res = tr.get("result")
        if isinstance(res, dict) and isinstance(
                res.get("content"), str):
            retrieved += _esc(json.dumps(res["content"]))
    case = _esc(_embedded_span(body_pkg["case"]))
    catalogue = _esc(tools_dump)
    provenance = sum(
        _esc(_embedded_span(v)) for k, v in body_pkg.items()
        if k != "case") - retrieved
    components = {
        "retrieved_content": retrieved,
        "case_view_and_assignment": case,
        "tool_catalogue": catalogue,
        "provenance_and_dispatch": provenance,
    }
    components["remaining_overhead"] = final - sum(
        components.values())
    return {"body": body, "serialized_bytes": final,
            "components": components,
            "residual": final - sum(components.values())}


# ---------------------------------------------------------- R5
def test_r5():
    store, d, tok, itok, ex, sandbox = world()
    seen = {}

    def step1(package):
        seen["tools"] = [t["tool"] for t in package["tools"]]
        return tool_req(("sandbox.list",
                         {"path": "sources/alpha.md"}))

    def step2(package):
        seen["pkg2"] = package
        return tool_req(("sandbox.search", {"query": "lantern"}))

    def step3(package):
        seen["pkg3"] = package
        return tool_req(
            ("sandbox.read_range",
             {"path": "sources/alpha.md", "start_line": 5,
              "end_line": 9}),
            ("sandbox.write",
             {"path": "scratch/notes.md",
              "content": "Notebook entry: findings at lines "
                         "5-9.\n"}))

    def step4(package):
        seen["pkg4"] = package
        return tool_req(
            ("sandbox.read_range",
             {"path": "scratch/notes.md", "start_line": 1,
              "end_line": 1}),
            ("sandbox.list", {"path": "sources/alpha.md"}))

    def step5(package):
        seen["pkg5"] = package
        return yield_()

    script = Script([step1, step2, step3, step4, step5])
    result = Loop(d, itok, script, executor=ex).run()
    check("R5 the successive run completes: list → search → "
          "read_range → notebook, then yield",
          result["outcome"] == "yield"
          and result["iterations"] == 5, str(result)[:90])
    check("R5 the catalogue offers the v3 retrieval tools "
          "from the grants",
          {"sandbox.list", "sandbox.read_range", "sandbox.search"}
          <= set(seen["tools"]), json.dumps(seen["tools"]))
    versions = {e["payload"]["registry_version"]
                for e in events_of(store, "LOOP_ITERATION")}
    check("R5 the run's iterations record the v3 registry",
          versions == {"tool-registry-v3"},
          json.dumps(sorted(versions)))

    measures = [measure_request(c["package"])
                for c in script.calls]
    list_result = seen["pkg2"]["tool_results"][0]["result"]
    check("single carriage: the record retains the list "
          "result in full",
          list_result["content"].count("## Appendix") == 1
          and list_result["content_bytes"]
          == len(list_result["content"].encode("utf-8"))
          and list_result["content_sha256"]
          == sha256_hex(list_result["content"].encode("utf-8")))
    check("single carriage: the rendered package carries the "
          "result exactly once (the delta does not repeat it)",
          measures[1]["body"].count("Appendix") == 1
          and measures[3]["body"].count("Appendix") == 0,
          f"counts "
          f"{[m['body'].count('Appendix') for m in measures]}")
    check("single carriage: the section pull is carried "
          "exactly once in its package",
          measures[3]["body"].count("QXZ-ALPHA-FINDINGS") == 1)
    check("single carriage: the breakdown counts the "
          "retrieved content once",
          measures[1]["components"]["retrieved_content"]
          == _esc(json.dumps(list_result["content"])))

    pkg3 = seen["pkg3"]
    first_dispatch = seen["pkg2"]["tool_results"][0][
        "dispatch_id"]
    check("R5 retention: iteration 1's result is not "
          "re-presented in iteration 3's package",
          len(pkg3["tool_results"]) == 1
          and pkg3["tool_results"][0]["result"]["query"]
          == "lantern"
          and pkg3["tool_results"][0]["dispatch_id"]
          != first_dispatch
          and json.dumps(list_result["content"])
          not in json.dumps(pkg3))
    pkg5 = seen["pkg5"]
    tool_of = {e["payload"]["dispatch_id"]: e["payload"]["tool"]
               for e in events_of(store, "TOOL_DISPATCHED")}
    repulled = [tr for tr in pkg5["tool_results"]
                if tool_of.get(tr["dispatch_id"])
                == "sandbox.list"]
    check("R5 retention: iteration 5 presents only the "
          "re-pull, never the original outcome again",
          len(repulled) == 1
          and repulled[0]["dispatch_id"] != first_dispatch
          and all(tr["dispatch_id"] != first_dispatch
                  for tr in pkg5["tool_results"]))
    check("R5 re-pulling a pinned source reproduces "
          "byte-identical content under the same hash",
          repulled[0]["result"]["content"]
          == list_result["content"]
          and repulled[0]["result"]["content_sha256"]
          == list_result["content_sha256"])
    notebook = [tr for tr in pkg5["tool_results"]
                if tool_of.get(tr["dispatch_id"])
                == "sandbox.read_range"][0]
    check("R5 the notebook round-trips under its own scratch "
          "grant, recorded on the scratch path",
          notebook["result"]["content"]
          == "Notebook entry: findings at lines 5-9.\n"
          and notebook["result"]["authority_path"] == "scratch")
    source_pull = [tr for tr in seen["pkg4"]["tool_results"]
                   if (tr["result"] or {}).get("authority_path")
                   == "source"
                   and "content" in (tr["result"] or {})][0]
    check("R5 the source pull in the same run is recorded on "
          "the source path — the two paths stay distinct",
          source_pull["result"]["authority_path"] == "source")
    check("R5 a non-scratch non-source path is still refused "
          "beside the notebook's grant",
          refused(lambda: d.request_tool(
              itok, "sandbox.read_range",
              {"path": "notes/x.md", "start_line": 1,
               "end_line": 1}, "r5-outside")))

    # R6 over this run's record.
    total = 0
    each_ok = True
    for e in events_of(store, "TOOL_OUTCOME"):
        r = e["payload"].get("result")
        if isinstance(r, dict) and "authority_path" in r:
            total += r["content_bytes"]
            each_ok = each_ok and r["content_bytes"] <= CEILING
    check("R6 the run's total retrieved content is a fraction "
          "of the corpus it reasoned over",
          total < CORPUS_TOTAL and each_ok,
          f"{total} retrieved of {CORPUS_TOTAL} corpus bytes")

    artifact = {
        "artifact": "retrieval-r5-measurements",
        "scope": "RETRIEVAL-SCOPE-2026-11-23 Rev 5 — witness "
                 "R5, with single carriage (INDEX 249)",
        "method": "Each rendered request is the real loop "
                  "package of the scripted R5 run rendered "
                  "through the adapter's prompt renderer and "
                  "carried in the connectors' transport body "
                  "form — the attempt-6 method (INDEX 247). "
                  "Components are exact serialized spans of "
                  "the final body: retrieved_content = the "
                  "JSON literal of each tool result's content, "
                  "counted once (single carriage); "
                  "case_view_and_assignment = the case span; "
                  "tool_catalogue = the tools-section dump; "
                  "provenance_and_dispatch = the view, delta, "
                  "tool_results, standing-dispatch, bounds "
                  "and position spans minus the retrieved "
                  "content literals; remaining_overhead = the "
                  "remainder (contract, framing, system "
                  "message, body skeleton). Components sum to "
                  "the serialized size; residual is stated "
                  "per request.",
        "model": _MODEL,
        "requests": [
            {"iteration": i + 1,
             "serialized_bytes": m["serialized_bytes"],
             "components": m["components"],
             "residual": m["residual"]}
            for i, m in enumerate(measures)],
    }
    out_path = os.path.join(
        ROOT, "live-demo", "retrieval-r5-measurements.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(artifact, fh, indent=1)
        fh.write("\n")
    check("R5 every rendered request measured and reconciled "
          "(components sum to the serialized size)",
          all(m["residual"] == 0 for m in measures)
          and all(m["components"]["remaining_overhead"] > 0
                  for m in measures),
          json.dumps([(m["serialized_bytes"],
                       m["components"]["retrieved_content"])
                      for m in measures]))

    verdict = run_checker(store)
    check("R7 the R5 record replays clean under the "
          "independent checker — dispatch and loop "
          "correspondence both ok",
          verdict["checks"]["dispatch_correspondence"]["result"]
          == "ok"
          and verdict["checks"]["loop_correspondence"]["result"]
          == "ok"
          and all(c["result"] == "ok"
                  for c in verdict["checks"].values()),
          json.dumps({k: v["result"] for k, v in
                      verdict["checks"].items()}))


# ------------------------------------------- registry & history
def test_registry_agreement():
    tools = ["sandbox.read", "sandbox.write", "sandbox.list",
             "sandbox.read_range", "sandbox.search"]
    same = True
    for version in ("tool-registry-v1", "tool-registry-v2",
                    "tool-registry-v3"):
        for tool in tools:
            fw_reg = fw_policy.registered(tool, version)
            ck_reg = ck_policy.registered(tool, version)
            same = same and fw_reg == ck_reg
            if fw_reg:
                fw_w = fw_policy.worker_facing(tool, version)
                ck_w = ck_policy.worker_facing(tool, version)
                same = same and canonical(fw_w) == canonical(ck_w)
    check("R7 the two registry copies agree on every version "
          "— v1 and v2 frozen, v3 identical in both",
          same and fw_policy.REGISTRY_VERSION
          == ck_policy.REGISTRY_VERSION
          == "tool-registry-v2")
    src = {"path_prefix": "sources"}
    cases = [
        ("sandbox.list", src, {"path": "sources/a.md"}),
        ("sandbox.list", src, {"path": "notes/a.md"}),
        ("sandbox.read_range", src,
         {"path": "sources/a.md", "heading": "Methods"}),
        ("sandbox.read_range", src,
         {"path": "sources/a.md", "heading": "M",
          "start_line": 1}),
        ("sandbox.read_range", src,
         {"path": "sources/a.md", "start_line": 2, "end_line": 2,
          "byte_start": 0, "byte_end": 11997}),
        ("sandbox.read_range", src,
         {"path": "sources/a.md", "start_line": 2, "end_line": 2,
          "byte_start": 0, "byte_end": 11998}),
        ("sandbox.read_range", src,
         {"path": "sources/a.md", "start_line": 2, "end_line": 5,
          "byte_start": 0, "byte_end": 10}),
        ("sandbox.search", src, {"query": "x"}),
        ("sandbox.search", src, {"query": ""}),
        ("sandbox.search", src, {"query": "x", "offset": -1}),
    ]
    agree = all(
        fw_policy.check_ceiling(tool, ceiling, params,
                                "tool-registry-v3")
        == ck_policy.check_ceiling(tool, ceiling, params,
                                   "tool-registry-v3")
        for tool, ceiling, params in cases)
    window_problem = fw_policy.check_ceiling(
        "sandbox.read_range", src,
        {"path": "sources/a.md", "start_line": 2,
         "end_line": 2, "byte_start": 0, "byte_end": 11998},
        "tool-registry-v3")[1]
    check("R7 the ceiling contract agrees across the copies "
          "on the v3 battery (window bound 11,997 named)",
          agree and window_problem is not None
          and "11997" in window_problem, str(window_problem))


def test_historical_exemption():
    grants = [_grant("sandbox.read", "notes")]
    store, d, tok, itok, ex, sandbox = world(
        grants=grants, retrieval=False)
    big = os.path.join(sandbox, "notes")
    os.makedirs(big, exist_ok=True)
    with open(os.path.join(big, "big.txt"), "wb") as fh:
        fh.write(LONGLINE_LINE.encode("utf-8"))
    out = dispatch_and_execute(
        d, ex, itok, "sandbox.read", {"path": "notes/big.txt"},
        "hist-read")
    o = outcome_of(store, out["dispatch_id"])
    disp = [e for e in events_of(store, "TOOL_DISPATCHED")][0]
    gen_ev = [e for e in events_of(store, "ASSEMBLY_GENERATED")
              ][0]
    check("history: a pre-v3 assembly keeps the old read "
          "whole — old result shape, no ceiling applied",
          o["outcome"] == "result"
          and set(o["result"]) == {"path", "content"}
          and len(o["result"]["content"].encode("utf-8"))
          == 39992)
    check("history: its dispatch stands under v2 and its "
          "assembly declares the a3-cat contract",
          disp["payload"]["registry_version"]
          == "tool-registry-v2"
          and gen_ev["payload"]["catalogue_contract"]
          == "a3-cat")


def test_forged_provenance():
    store, d, tok, itok, ex, _ = world()
    base = dispatch_and_execute(
        d, ex, itok, "sandbox.read_range",
        {"path": "sources/gamma.log", "start_line": 1,
         "end_line": 1}, "forge-base")
    iid = base["instance_id"]
    params = {"path": "sources/gamma.log", "start_line": 1,
              "end_line": 3}
    store.append("TOOL_REQUESTED", "crew-1", [], {
        "instance_id": iid, "request_id": "forged-1",
        "tool": "sandbox.read_range", "parameters": params,
        "fingerprint": fw_policy.request_fingerprint(
            "sandbox.read_range", params)})
    store.append("TOOL_DISPATCHED", "doorway", [], {
        "instance_id": iid, "request_id": "forged-1",
        "dispatch_id": "dispatch-forged",
        "tool": "sandbox.read_range", "parameters": params,
        "ceiling": {"path_prefix": "sources"},
        "authority_trace": TRACE,
        "registry_version": "tool-registry-v3"})
    store.append("TOOL_OUTCOME", "executor", [], {
        "instance_id": iid, "dispatch_id": "dispatch-forged",
        "outcome": "result",
        "result": {"path": "sources/gamma.log",
                   "content": "tampered text",
                   "content_bytes": 13,
                   "content_sha256": "0" * 64,
                   "authority_path": "source",
                   "start_line": 1, "end_line": 3}})
    store.commit()
    verdict = run_checker(store)
    dc = verdict["checks"]["dispatch_correspondence"]
    kinds = {p["kind"] for p in dc["problems"]}
    check("R7 a forged retrieval provenance is named "
          "divergent by the checker",
          dc["result"] == "divergent"
          and "retrieval_provenance_mismatch" in kinds,
          json.dumps(sorted(kinds)))


def main():
    test_registry_agreement()
    test_r1()
    test_r2()
    test_r3_oversize_and_windows()
    test_r3_straddle()
    test_r3_aggregate_iteration()
    test_r3_uncertain_counts_ceiling()
    test_r4()
    test_r5()
    test_historical_exemption()
    test_forged_provenance()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURES:")
        for name in FAILURES:
            print("  " + name)
        return 1
    print("RETRIEVAL TESTS: ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
