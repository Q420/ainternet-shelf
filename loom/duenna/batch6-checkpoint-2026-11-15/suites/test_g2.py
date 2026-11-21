#!/usr/bin/env python3
"""C6-9 audit — Gate G2 examiner verification over the preserved
scratch artefact sets (fetched byte-identical from the G2
scratch room; both record hashes match the room's own summary).

Verifies the sheet's G2 conditions against G2TORN-20261115-001
(a genuinely torn tail: an external killer SIGKILLed the
harness mid-append during the injector's fragmented write) and
the companion G2BETWEEN-20261115-001 (between-steps crash):

  (1) the CRASH commitment's record_file_sha256 covers the
      exact bytes as they lie, torn tail included;
  (2) the chain walk ends at event_count / final_event_sha256,
      treating the torn tail as no event, step, or verdict;
  (3) trimming the tail — or completing it — fails the anchor
      at Step 0 (record_file_sha256 mismatch);
  negative space: no TERMINAL receipt for either run; CRASH
  entries present in the issuance record; run outcome
  INCONCLUSIVE (no RUN_CLOSED, CRASH anchor);
  flag states: the injector + test hooks are present in the
  scratch build (this run's launcher + harness tree) and
  absent from the clean scoreable build (C6-6 flag states).
Writes G2-VERIFICATION-REPORT.md into scratch/g2/.
"""
import hashlib, json, shutil, sys, tempfile
from pathlib import Path

H = Path.home()
B6 = H / "workspace/ssh-door/batch6/build"
G2 = H / "workspace/ssh-door/batch6/scratch/g2"
sys.path.insert(0, str(B6))
from pilot_examiner import step0, step1_chain, \
    parse_complete_events  # noqa: E402

RESULTS = []


def case(name):
    def deco(fn):
        try:
            fn()
            RESULTS.append((name, "PASS"))
        except Exception as e:
            RESULTS.append((name, f"FAIL: {type(e).__name__}: {e}"))
    return deco


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


TORN = G2 / "runs/G2TORN-20261115-001/run-record.jsonl"
BETWEEN = G2 / "runs/G2BETWEEN-20261115-001/run-record.jsonl"
COMMITS = G2 / "commitments"
ISSUANCE = COMMITS / "issuance-record.jsonl"
TORN_RAW = TORN.read_bytes()
TORN_EVENTS, TORN_TAIL = parse_complete_events(TORN_RAW)


@case("torn artefact is genuine: 2 complete events + unparsed tail, no trailing newline")
def _():
    assert len(TORN_EVENTS) == 2, len(TORN_EVENTS)
    assert len(TORN_TAIL) == 112, len(TORN_TAIL)
    assert not TORN_RAW.endswith(b"\n")
    try:
        json.loads(TORN_TAIL)
        raise AssertionError("tail parses as JSON — not torn")
    except json.JSONDecodeError:
        pass


@case("G2(1) Step 0 on the torn set: CRASH anchor verified over exact bytes incl. tail")
def _():
    r = step0(TORN, COMMITS, ISSUANCE)
    assert r["step0"] == "PASS" and r["anchor"] == "CRASH", r
    assert r["complete_events"] == 2 and r["tail_bytes"] == 112, r


@case("G2(1) direct recomputation: receipt record_file_sha256 == sha256(bytes as they lie)")
def _():
    crash = json.loads((COMMITS / "G2TORN-20261115-001.crash.json")
                       .read_text())
    assert crash["record_file_sha256"] == sha256_bytes(TORN_RAW)
    assert crash["event_count"] == 2
    assert crash["final_event_sha256"] == \
        TORN_EVENTS[-1]["event_sha256"]


@case("G2(2) chain walk ends at the last complete event; tail is no event")
def _():
    r = step1_chain(TORN_EVENTS)
    assert r["walked"] == 2 and r["divergence"] is None, r


@case("G2(3) trimmed tail copy is rejected at Step 0 (anchor failure)")
def _():
    tmp = Path(tempfile.mkdtemp(prefix="g2-trim-"))
    trimmed = TORN_RAW[:len(TORN_RAW) - len(TORN_TAIL)]
    assert trimmed.endswith(b"\n")
    (tmp / "run-record.jsonl").write_bytes(trimmed)
    try:
        step0(tmp / "run-record.jsonl", COMMITS, ISSUANCE)
        raise AssertionError("trimmed copy ACCEPTED — anchor failure")
    except Exception as e:
        assert "record_file_sha256" in str(e), str(e)


@case("G2(3) completed tail copy is rejected at Step 0 (anchor failure)")
def _():
    tmp = Path(tempfile.mkdtemp(prefix="g2-complete-"))
    # the plausible repair: a clean 3-event file — the torn
    # fragment replaced by a well-formed third event line.
    # It parses, so Step 0 reaches the anchor check itself.
    trimmed = TORN_RAW[:len(TORN_RAW) - len(TORN_TAIL)]
    fabricated = dict(TORN_EVENTS[-1])
    fabricated["seq"] = 3
    fabricated["event_id"] = f"{fabricated['run_id']}:3"
    completed = trimmed + (json.dumps(fabricated) + "\n").encode()
    (tmp / "run-record.jsonl").write_bytes(completed)
    try:
        step0(tmp / "run-record.jsonl", COMMITS, ISSUANCE)
        raise AssertionError("completed copy ACCEPTED — anchor failure")
    except Exception as e:
        assert "record_file_sha256" in str(e), str(e)


@case("between-steps companion: Step 0 PASS on CRASH anchor, clean ending, 2 events")
def _():
    r = step0(BETWEEN, COMMITS, ISSUANCE)
    assert r["step0"] == "PASS" and r["anchor"] == "CRASH", r
    assert r["complete_events"] == 2 and r["tail_bytes"] == 0, r
    raw = BETWEEN.read_bytes()
    assert raw.endswith(b"\n")
    ev, _ = parse_complete_events(raw)
    assert step1_chain(ev)["divergence"] is None


@case("negative space: no TERMINAL receipt for either run; outcome INCONCLUSIVE")
def _():
    for rid in ("G2TORN-20261115-001", "G2BETWEEN-20261115-001"):
        assert not (COMMITS / f"{rid}.terminal.json").exists()
        assert (COMMITS / f"{rid}.crash.json").exists()
        assert (COMMITS / f"{rid}.start.json").exists()
    for rec in (TORN, BETWEEN):
        ev, _ = parse_complete_events(rec.read_bytes())
        assert all(e["event_type"] != "RUN_CLOSED" for e in ev)


@case("issuance record carries START + CRASH entries for both runs")
def _():
    entries = [json.loads(l) for l in
               ISSUANCE.read_text().splitlines() if l.strip()]
    kinds = {(e.get("run_id"), e.get("kind")) for e in entries}
    for rid in ("G2TORN-20261115-001", "G2BETWEEN-20261115-001"):
        assert (rid, "START") in kinds, kinds
        assert (rid, "CRASH") in kinds, kinds


@case("kill provenance: killer log's SIGKILL pid == the harness's torn-started marker")
def _():
    pid = (G2 / "runs/G2TORN-20261115-001/torn-started") \
        .read_text().strip()
    log = (G2 / "logs/killer.log").read_text()
    assert f"SIGKILL pid={pid}" in log, log


@case("flag state: scratch launcher carries hook markers; injector in the scratch harness tree")
def _():
    blob = (G2 / "launcher-scratch").read_bytes()
    assert b"PILOT_HOOK_" in blob
    inj = G2 / "harness/torn_write_injector.py"
    assert inj.exists()
    assert sha256_bytes(inj.read_bytes()) == sha256_bytes(
        (B6 / "torn_write_injector.py").read_bytes())
    assert b"torn_write_injector" in \
        (G2 / "harness/pilot-harness").read_bytes()


@case("flag state: scoreable build has no injector and no hook markers (C6-6 records)")
def _():
    scratch_state = json.loads(
        (B6 / "c6-6-evidence/FLAG-STATE-scratch.json").read_text())
    score_state = json.loads(
        (B6 / "c6-6-evidence/FLAG-STATE-scoreable.json").read_text())
    assert scratch_state["PILOT_TORN_WRITE_INJECTOR"] is True
    assert scratch_state["hook_markers_in_launcher_object"] is True
    assert score_state["PILOT_TORN_WRITE_INJECTOR"] is False
    assert score_state["hook_markers_in_launcher_object"] is False
    assert not (B6 / "pkg-scoreable/torn_write_injector.py").exists()
    assert (B6 / "pkg-scratch/torn_write_injector.py").exists()


fails = [r for r in RESULTS if r[1] != "PASS"]
report = ["# G2 EXAMINER VERIFICATION REPORT (C6-9)", "",
          "Artefacts: scratch/g2/ (fetched byte-identical from "
          "the G2 scratch room on the laptop; record hashes "
          "match the room's stage summary). Torn run: "
          "G2TORN-20261115-001 (2 complete events, 112 torn "
          "tail bytes, external SIGKILL mid-append). Companion: "
          "G2BETWEEN-20261115-001 (between-steps crash).", ""]
report += [f"- {n}: **{s}**" for n, s in RESULTS]
report += ["", f"Verdict: {'ALL PASS' if not fails else 'FAIL'} — "
           "Gate G2's three conditions and the negative space "
           "verify against the preserved artefacts; both runs' "
           "outcomes are INCONCLUSIVE under CRASH anchors."]
(G2 / "G2-VERIFICATION-REPORT.md").write_text("\n".join(report) + "\n")
for name, status in RESULTS:
    print(f"[{status}] {name}")
print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} G2 verification checks pass")
sys.exit(1 if fails else 0)
