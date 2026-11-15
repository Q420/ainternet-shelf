#!/usr/bin/env python3
"""Step 0 verification checks (approved sheet C6-1, verification (a)-(c)).
Real Batch 4 pairs for the genuine paths; synthetic variants in temp dirs
for the adversarial cases. Fixture receipts/issuance entries constructed in
the supervisor's formats are marked FIXTURE where they occur."""
import hashlib, json, shutil, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pilot_examiner import step0, CustodyFailure

BUNDLE = Path.home() / "workspace/ssh-door/batch4/checkpoint-bundle"
RESULTS = []

def case(name):
    def deco(fn):
        try:
            fn()
            RESULTS.append((name, "PASS"))
        except Exception as e:
            RESULTS.append((name, f"FAIL: {type(e).__name__}: {e}"))
    return deco

def stage(run_id, files):
    """Copy a run's record + receipts + issuance into a fresh temp dir."""
    d = Path(tempfile.mkdtemp(prefix="step0-"))
    (d / "receipts").mkdir()
    shutil.copy(BUNDLE / "artefacts" / f"{run_id}.run-record.jsonl", d / "record.jsonl")
    for f in files:
        shutil.copy(BUNDLE / "receipts" / f, d / "receipts" / f)
    shutil.copy(BUNDLE / "receipts" / "issuance-record.jsonl", d / "issuance.jsonl")
    return d

def expect_pass(name, run_id, files):
    @case(name)
    def _():
        d = stage(run_id, files)
        v = step0(d / "record.jsonl", d / "receipts", d / "issuance.jsonl")
        assert v["step0"] == "PASS", v

def expect_fail(name, run_id, files, mutate=None):
    @case(name)
    def _():
        d = stage(run_id, files)
        if mutate:
            mutate(d)
        try:
            step0(d / "record.jsonl", d / "receipts", d / "issuance.jsonl")
        except CustodyFailure:
            return
        raise AssertionError("examination did not fail closed")

SMOKE = "B4SMOKE-20261114-001"
CRASH = "B4CRASH-20261114-101"

# (a) valid START+TERMINAL passes — genuine Batch 4 pair
expect_pass("(a) valid START+TERMINAL", SMOKE, [f"{SMOKE}.start.json", f"{SMOKE}.terminal.json"])
# (b) valid START+CRASH passes — genuine Batch 4 pair (crash between events)
expect_pass("(b) valid START+CRASH", CRASH, [f"{CRASH}.start.json", f"{CRASH}.crash.json"])

# (b2) torn-tail CRASH fixture: first two B4SMOKE lines + a torn third line;
# FIXTURE crash receipt + issuance entries computed over the torn bytes.
@case("(b2) torn-tail CRASH bounds to complete events")
def _():
    d = stage(SMOKE, [f"{SMOKE}.start.json"])
    lines = (d / "record.jsonl").read_bytes().split(b"\n")
    torn = lines[0] + b"\n" + lines[1] + b"\n" + lines[2][:40]  # third line cut mid-bytes, no newline
    (d / "record.jsonl").write_bytes(torn)
    ev2 = json.loads(lines[1])
    crash = {"event_count": 2, "final_event_sha256": ev2["event_sha256"],
             "issued_at_utc": "2026-11-14T21:57:34Z", "kind": "CRASH",
             "record_file_sha256": hashlib.sha256(torn).hexdigest(), "run_id": SMOKE,
             "termination_observed": {"basis": "FIXTURE termination observed", "observed_at_utc": "2026-11-14T21:57:34Z", "status_word": 9}}
    (d / "receipts" / f"{SMOKE}.crash.json").write_text(json.dumps(crash, sort_keys=True, separators=(",", ":")) + "\n")
    digest = hashlib.sha256((d / "receipts" / f"{SMOKE}.crash.json").read_bytes()).hexdigest()
    with open(d / "issuance.jsonl", "a") as f:
        f.write(json.dumps({"issued_at_utc": crash["issued_at_utc"], "kind": "CRASH", "receipt_sha256": digest, "run_id": SMOKE}, sort_keys=True) + "\n")
    v = step0(d / "record.jsonl", d / "receipts", d / "issuance.jsonl")
    assert v["anchor"] == "CRASH" and v["complete_events"] == 2 and v["tail_bytes"] == 40, v
    # (c5) completing the torn tail afterwards breaks the CRASH commitment
    full = (BUNDLE / "artefacts" / f"{SMOKE}.run-record.jsonl").read_bytes()
    (d / "record.jsonl").write_bytes(full)
    try:
        step0(d / "record.jsonl", d / "receipts", d / "issuance.jsonl")
    except CustodyFailure:
        return
    raise AssertionError("completed torn tail did not fail closed")

# (c1) missing closure receipt
expect_fail("(c1) missing receipt", SMOKE, [f"{SMOKE}.start.json"])
# (c2) coexisting TERMINAL+CRASH
def _add_crash(d):
    shutil.copy(BUNDLE / "receipts" / f"{CRASH}.crash.json", d / "receipts" / f"{SMOKE}.crash.json")
expect_fail("(c2) TERMINAL+CRASH coexist", SMOKE, [f"{SMOKE}.start.json", f"{SMOKE}.terminal.json"], _add_crash)
# (c3) tampered receipt (event_count edited; hash leaves the issuance set)
def _tamper(d):
    p = d / "receipts" / f"{SMOKE}.terminal.json"
    obj = json.loads(p.read_text()); obj["event_count"] = 99
    p.write_text(json.dumps(obj, sort_keys=True) + "\n")
expect_fail("(c3) tampered receipt hash", SMOKE, [f"{SMOKE}.start.json", f"{SMOKE}.terminal.json"], _tamper)
# (c4) receipt absent from issuance-record
def _drop_issuance(d):
    lines = (d / "issuance.jsonl").read_text().splitlines()
    kept = [ln for ln in lines if not (SMOKE in ln and '"TERMINAL"' in ln)]
    (d / "issuance.jsonl").write_text("\n".join(kept) + "\n")
expect_fail("(c4) receipt absent from issuance-record", SMOKE, [f"{SMOKE}.start.json", f"{SMOKE}.terminal.json"], _drop_issuance)
# (c6) record bytes altered under a TERMINAL commitment
def _alter_record(d):
    p = d / "record.jsonl"
    raw = p.read_bytes().replace(b"stub-step", b"stub-st3p", 1)
    p.write_bytes(raw)
expect_fail("(c6) record altered under TERMINAL commitment", SMOKE, [f"{SMOKE}.start.json", f"{SMOKE}.terminal.json"], _alter_record)

for name, res in RESULTS:
    print(f"{res:8} {name}")
print(f"\n{sum(1 for _, r in RESULTS if r == 'PASS')}/{len(RESULTS)} checks passed")
sys.exit(0 if all(r == "PASS" for _, r in RESULTS) else 1)
