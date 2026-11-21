#!/usr/bin/env python3
"""C6-8 audit — examiner re-derivation of the G1 scratch record
(Criteria §8: verified by re-derivation, not by trusting the
summary). Independently:

  1. verifies the record's hash chain (pilot_record.verify_chain);
  2. checks the RUN_STARTED pin block against the artefacts on
     disk (tools, rules, examiner, snapshot copy);
  3. re-executes every recorded tool invocation in order through
     a fresh PilotTools, following the record's own HARNESS_NOTE
     corpus swaps (genuine copy <-> preserved perturbed copy),
     and compares every emitted (type, payload) pair — results,
     the single LEDGER_ENTRY, all five INSERT_REFUSED events —
     against the preserved record;
  4. reconstructs the issuance registry from the record alone
     (Step 4) and compares it to the preserved issuance records;
  5. recomputes S4 from the preserved perturbed artefact;
  6. re-reads the zero-egress + adapter evidence artefacts and
     verifies the proxy-check capture with the examiner's own
     Step 5 capture verification;
  7. asserts the sheet's G1 verification list verbatim.
Writes G1-REDERIVATION-REPORT.md into the scratch run directory.
"""
import hashlib, json, sys, tempfile
from pathlib import Path

H = Path.home()
B6 = H / "workspace/ssh-door/batch6/build"
B3 = H / "workspace/ssh-door/batch3"
TOOLS = B6 / "tools"
SCRATCH = H / "workspace/ssh-door/batch6/scratch/g1-run"
DATA_DIR = H / "workspace/nemotron-pilot/batch1-2026-11-13"
# The G1 record was made under the pre-T03-amendment rules pin
# (61095f21…). The remediation (2026-11-15) superseded that pin;
# G1's evidence verifies against the rules as they stood when
# the record was made — the preserved pre-amendment copy.
RULES_PATH = (H / "workspace/ssh-door/t03-remediation"
              "/EXTRACTOR-RULES-02.pre-amendment.json")
F2 = (H / "workspace/ainternet-shelf/duenna/batch5-checkpoint-2026-11-14"
      "/sources/adapter-config-f2-2026-11-12.canonical.json")
CR = "r60-revision-change-record#009"

sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(B3))
sys.path.insert(0, str(B6))
from corpus_source import CorpusSource  # noqa: E402
from pilot_record import read_events, verify_chain  # noqa: E402
from pilot_tools import PilotTools, IssuanceRegistry, \
    ScratchRecord  # noqa: E402
from pilot_examiner import step5_capture  # noqa: E402

RESULTS = []


def case(name):
    def deco(fn):
        try:
            fn()
            RESULTS.append((name, "PASS"))
        except Exception as e:
            RESULTS.append((name, f"FAIL: {type(e).__name__}: {e}"))
    return deco


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


EVENTS = read_events(SCRATCH / "run-record.jsonl")
BY_TYPE = {}
for e in EVENTS:
    BY_TYPE.setdefault(e["event_type"], []).append(e)
RETURNS = {e["payload"]["operation_id"]: e["payload"]["result"]
           for e in BY_TYPE.get("TOOL_RETURNED", [])}
REFUSALS = [e["payload"] for e in BY_TYPE.get("GOVERNANCE_EVENT", [])
            if e["payload"].get("kind") == "INSERT_REFUSED"]


@case("chain integrity: hash chain verifies, one RUN_CLOSED")
def _():
    ok, detail = verify_chain(SCRATCH / "run-record.jsonl")
    assert ok, detail


@case("pin block: RUN_STARTED pins match the artefacts on disk")
def _():
    block = BY_TYPE["RUN_STARTED"][0]["payload"]["pinned_input_block"]
    for name, digest in block["tools"].items():
        assert sha256_file(TOOLS / name) == digest, name
    assert sha256_file(RULES_PATH) == \
        block["rules"]["EXTRACTOR-RULES-02.json"]
    # The examiner has since been corrected (Gate G4 step-4
    # pairing fix, 2026-11-15); G1's pin verifies against the
    # preserved pre-fix copy, whose reconstruction hashes
    # exactly to the pinned 36bf23e1… value.
    assert sha256_file(B6.parent / "prefix-artefacts"
                       / "pilot_examiner.py") == \
        block["examiner"]["pilot_examiner.py"]
    assert sha256_file(SCRATCH / "snap-genuine/sections.jsonl") == \
        block["snapshot"]["sections_jsonl_sha256"]


@case("sheet list: exactly one LEDGER_ENTRY (S3's), value 38, EXTRACTED")
def _():
    entries = BY_TYPE.get("LEDGER_ENTRY", [])
    assert len(entries) == 1, len(entries)
    p = entries[0]["payload"]
    assert p["value"] == 38 and p["verification"] == "EXTRACTED"
    assert p["operation_id"] == "op-1" and p["field"] == \
        "fixtures_executed"


@case("sheet list: five INSERT_REFUSED, claimed-vs-recomputed, in order")
def _():
    assert len(REFUSALS) == 5, len(REFUSALS)
    reasons = [r["reason"] for r in REFUSALS]
    assert reasons == ["ALREADY_CONSUMED", "NO_ISSUANCE",
                       "NOT_EXTRACTED", "NOT_EXTRACTED",
                       "SNAPSHOT_MISMATCH"], reasons
    for r in REFUSALS:
        assert "claimed" in r and "recomputed" in r, r["reason"]


@case("sheet list: every refusal returned the refusal object, no value")
def _():
    for op, res in RETURNS.items():
        if op in ("op-3", "op-4", "op-6", "op-8", "op-10"):
            assert res.get("refused") is True and "value" not in res, op
    assert RETURNS["op-2"].get("inserted") is True


@case("sheet list: S5 extraction AMBIGUOUS, all candidates, no value")
def _():
    res = RETURNS["op-7"]
    assert res["verification"] == "AMBIGUOUS"
    assert len(res["candidates"]) == 2 and "value" not in res


@case("sheet list: S2 extraction TYPE FAILURE, matched, no value")
def _():
    res = RETURNS["op-5"]
    assert res["verification"] == "TYPE FAILURE"
    assert res["matched"] and "value" not in res


@case("re-execution: full replay reproduces the record's tool events")
def _():
    rules_doc = json.loads(RULES_PATH.read_text())
    tmp = Path(tempfile.mkdtemp(prefix="g1-replay-"))
    rec = ScratchRecord(tmp / "replay.jsonl")
    ctx = {"run_id": "G1SCRATCH-20261115-001", "tree_id": None,
           "step_id": None}
    tools = PilotTools(CorpusSource(SCRATCH / "snap-genuine",
                                    DATA_DIR),
                       rules_doc, DATA_DIR, rec, ctx)
    swaps = [e for e in EVENTS if e["event_type"] == "GOVERNANCE_EVENT"
             and e["payload"].get("kind") == "HARNESS_NOTE"]
    swap_seqs = {e["seq"]: e["payload"] for e in swaps}
    for e in EVENTS:
        if e["seq"] in swap_seqs:
            note = swap_seqs[e["seq"]]["note"]
            if "perturbed" in note and "rebound to the perturbed" in note:
                tools._corpus = CorpusSource(
                    SCRATCH / "snap-perturbed", DATA_DIR)
            elif "genuine" in note:
                tools._corpus = CorpusSource(
                    SCRATCH / "snap-genuine", DATA_DIR)
        if e["event_type"] != "TOOL_INVOKED":
            continue
        p = e["payload"]
        ctx["tree_id"], ctx["step_id"] = p["tree_id"], p["step_id"]
        tool, args = p["tool"], p["args"]
        if tool == "source_extract":
            tools.source_extract(args["source_ref"], args["field"])
        elif tool == "reference_insert":
            tools.reference_insert(args["field"],
                                   args["process_step"],
                                   args["presentation"])
        else:
            raise AssertionError(f"unexpected tool {tool}")
    rec.close()
    replay = [json.loads(l) for l in
              (tmp / "replay.jsonl").read_text().splitlines()]
    mine = [(e["event_type"],
             {k: v for k, v in e.items()
              if k not in ("seq", "event_type")}) for e in replay]
    theirs = [(e["event_type"], e["payload"]) for e in EVENTS
              if e["event_type"] in ("TOOL_INVOKED", "TOOL_RETURNED",
                                     "LEDGER_ENTRY",
                                     "GOVERNANCE_EVENT")
              and e["payload"].get("kind") != "HARNESS_NOTE"]
    assert len(mine) == len(theirs), (len(mine), len(theirs))
    for (mt, mp), (tt, tp) in zip(mine, theirs):
        assert mt == tt, (mt, tt)
        if mt == "GOVERNANCE_EVENT":
            # refusal events: compare the load-bearing fields
            for k in ("kind", "reason", "claimed", "recomputed"):
                assert mp.get(k) == tp.get(k), (k, mp, tp)
        else:
            assert mp == tp, (mt, mp, tp)


@case("registry audit (Step 4): reconstruction == preserved issuance")
def _():
    rebuilt = IssuanceRegistry.reconstruct(EVENTS)
    preserved = json.loads(
        (SCRATCH / "issuance-records.json").read_text())
    assert rebuilt.snapshot() == preserved["registry_entries"]
    assert rebuilt.snapshot()["op-1"]["consumed"] is True
    assert rebuilt.snapshot()["op-9"]["consumed"] is False
    assert rebuilt.citations_snapshot() == \
        preserved["citations_consumed"] == []


@case("S4 artefact recomputation: perturbed hash == refusal detail")
def _():
    refusal = REFUSALS[-1]
    assert refusal["reason"] == "SNAPSHOT_MISMATCH"
    sec = next(json.loads(l) for l in
               (SCRATCH / "snap-perturbed/sections.jsonl")
               .read_text().splitlines()
               if json.loads(l)["section_id"] == CR)
    recomputed = hashlib.sha256(sec["text"].encode()).hexdigest()
    assert refusal["recomputed"]["recomputed_source_hash"] == \
        recomputed
    assert refusal["recomputed"]["entry"]["source_hash"] == \
        sec["sha256"]  # the genuine stated hash the claim carried


@case("zero-egress evidence: inspection record shows a sealed namespace")
def _():
    env = json.loads((SCRATCH / "ENV-INSPECTION.json").read_text())
    assert "default" not in env["routes_v4"]
    assert env["external_tcp_1_1_1_1_443"].startswith("blocked")
    assert env["dns_example_com"].startswith("blocked")
    assert env["credential_env_var_names_present"] == []
    assert env["proxy_env_present"] == {}


@case("adapter evidence: §3.7 checks + capture verifies (Step 5)")
def _():
    checks = json.loads((SCRATCH / "ADAPTER-CHECKS.json").read_text())
    assert "non-loopback" in checks["non_loopback_refused"]["raised"]
    px = checks["proxy_ignored"]
    assert px["failure_class"] == "ADAPTER_FAILURE"
    assert 200 in px["attempt_http_status"]
    cap = json.loads((SCRATCH / "captures"
                      / (px["capture"] + ".json")).read_text())
    cfg = json.loads(F2.read_text())
    assert not step5_capture(cap, cfg)["findings"], \
        step5_capture(cap, cfg)["findings"]


@case("battery result artefact: 19/19 runner checks, all pass")
def _():
    outcome = json.loads((SCRATCH / "BATTERY-RESULT.json").read_text())
    assert outcome["all_pass"] and len(outcome["checks"]) == 19


fails = [r for r in RESULTS if r[1] != "PASS"]
report = ["# G1 EXAMINER RE-DERIVATION REPORT (C6-8)", "",
          f"Record: scratch/g1-run/run-record.jsonl "
          f"({len(EVENTS)} events, hash-chained RunRecord).",
          "Method: chain verification; pin recomputation; full "
          "re-execution of every recorded invocation through a "
          "fresh PilotTools, following the record's HARNESS_NOTE "
          "corpus swaps against the preserved perturbed copy; "
          "registry reconstruction from the record alone; S4 "
          "recomputed from the preserved perturbed artefact; "
          "adapter capture verified with Step 5.", ""]
report += [f"- {n}: **{s}**" for n, s in RESULTS]
report += ["", f"Verdict: {'ALL PASS' if not fails else 'FAIL'} — "
           "Gate G1's five sabotage outcomes and the zero-egress "
           "environment evidence re-derive from the preserved "
           "artefacts."]
(SCRATCH / "G1-REDERIVATION-REPORT.md").write_text(
    "\n".join(report) + "\n")
for name, status in RESULTS:
    print(f"[{status}] {name}")
print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} re-derivation checks pass")
sys.exit(1 if fails else 0)
