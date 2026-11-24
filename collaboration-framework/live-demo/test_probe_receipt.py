"""Focused witness for the probed run's phase 2
(INDEX 293, correction B): the examiner decision
receipt. Phase 1 runs as a harness subprocess against a
STUB helper (its probe trials answer natively, so the
probe recommends the native mode); phase 2 is then
driven in-process against that standing record:

- a receipt with a wrong probe evidence hash refuses,
  before any ASSEMBLY_JUDGED stands;
- a receipt with a wrong generated-record hash refuses;
- a receipt with a wrong configuration fingerprint
  refuses;
- a missing receipt refuses;
- the correct receipt records ASSEMBLY_JUDGED carrying
  the receipt's canonical hash and the decision-
  recording note, packs, activates, completes the loop,
  and the independent checker is all-ok over the full
  probed record;
- the exact receipt file stands retained in the run
  directory as decision-receipt.json, byte-identical
  to the receipt supplied, its canonical hash the
  hash bound in the judgement (INDEX 295).

The real provider is never called: the stub helper
answers `chat` (identify + loop) and `chat-raw` (the
probe's five trials) in the helpers' own shapes.

Run: PYTHONPATH=src python3 \
    live-demo/test_probe_receipt.py
Exits 0 when every check passes.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)

from fabric.canonical import canonical  # noqa: E402
from framework import projection  # noqa: E402
from framework.record import FrameworkStore  # noqa: E402
import first_worker_run as harness  # noqa: E402

PIN = "openai/gpt-oss-120b"
FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name +
          (("  " + detail) if detail else ""))
    if not cond:
        FAILURES.append(name)


DECLARATION = ("I am StubModel 1.0, provided by "
               "StubProvider for tests.")
YIELD_CONTENT = json.dumps(
    {"outcome": "yield",
     "summary": "stub worker: the brief stands"})

STUB_HELPER = '''\
import base64, json, sys
argv = sys.argv[1:]
raw = sys.stdin.buffer.read()
if argv and argv[0] == "chat-raw":
    body = json.dumps({
        "id": "chatcmpl-stub", "model": %r,
        "choices": [{"index": 0, "message": {
            "role": "assistant", "content": None,
            "tool_calls": [{"id": "fc_stub1",
                            "type": "function",
                            "function": {
                                "name": "probe.lookup",
                                "arguments": json.dumps(
                                    {"object":
                                     "brass lantern"})}}]}}]})
    print(json.dumps({"status": 200, "body_b64":
        base64.b64encode(
            body.encode("utf-8")).decode("ascii")}))
    sys.exit(0)
if b"State your identity" in raw:
    content = %r
else:
    content = %r
print(json.dumps({
    "id": "chatcmpl-stub", "model": %r,
    "choices": [{"index": 0, "message": {
        "role": "assistant", "content": content}}]}))
''' % (PIN, DECLARATION, YIELD_CONTENT, PIN)

TMP = tempfile.mkdtemp(prefix="probe-receipt-witness-")
STUB_PATH = os.path.join(TMP, "stub_helper.py")
with open(STUB_PATH, "w", encoding="utf-8") as fh:
    fh.write(STUB_HELPER)

SUFFIX = "witnessreceipt"
RUN_DIR = os.path.join(ROOT, "live-demo",
                       f"first-worker-{SUFFIX}")
shutil.rmtree(RUN_DIR, ignore_errors=True)

# -- Phase 1, as a harness subprocess against the stub.
env = dict(os.environ, WORKER_ROUTE="groq", RETRIEVAL="1",
           PROBED="1", GROQ_HELPER_PATH=STUB_PATH,
           ADAPTER_TIMEOUT="10")
proc1 = subprocess.run(
    [sys.executable,
     os.path.join(HERE, "first_worker_run.py"),
     "--probe-phase1", SUFFIX],
    capture_output=True, text=True, env=env, cwd=ROOT)
check("phase 1 completes against the stub helper",
      proc1.returncode == 0,
      f"rc={proc1.returncode} "
      f"stderr={proc1.stderr.strip()[:200]}")
evidence_path = os.path.join(RUN_DIR, "probe-evidence.json")
evidence = None
if os.path.exists(evidence_path):
    with open(evidence_path, encoding="utf-8") as fh:
        evidence = json.load(fh)
check("phase 1 wrote probe-evidence.json recommending "
      "the native mode on five settled trials",
      evidence is not None and
      evidence.get("recommended_mode") == "native" and
      evidence.get("settled_count") == 5,
      f"evidence={evidence and evidence.get('recommended_mode')}")
export_path = os.path.join(RUN_DIR, "run-export.json")
with open(export_path, encoding="utf-8") as fh:
    export = json.load(fh)
probed_events = [e for e in export["events"]
                 if e["type"] == "ASSEMBLY_PROBED"]
probed_ev = probed_events[0] if probed_events else {}
probed_payload = probed_ev.get("payload") or {}
if isinstance(probed_payload, str):
    probed_payload = json.loads(probed_payload)

RECEIPT = {
    "run_id": harness.RUN_ID,
    "assembly_id": (evidence or {}).get("assembly_id"),
    "generated_record_hash":
        (evidence or {}).get("generated_record_hash"),
    "probed_seq": probed_ev.get("event_seq"),
    "probe_evidence_hash": probed_payload.get(
        "evidence_hash"),
    "fingerprint": probed_payload.get("fingerprint"),
    "adapter_mode": "native",
    "mode_grounds": "the probe's recommendation: five "
                    "settled trials, all native_catalogue "
                    "x provider_accepted",
    "examiner": "exam-1",
    "decided_at": "2026-11-23T20:45:00-07:00",
}
RECEIPT_HASH = hashlib.sha256(
    canonical(RECEIPT)).hexdigest()


def write_receipt(name, receipt):
    path = os.path.join(TMP, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh)
    return path


def judged_events():
    store = FrameworkStore(
        os.path.join(RUN_DIR, "run.db"))
    return [e for e in store.all_events()
            if e["type"] == "ASSEMBLY_JUDGED"]


# Phase 2 runs in-process; its adapter reads the stub
# path from the environment, as the harness configures.
os.environ["GROQ_HELPER_PATH"] = STUB_PATH
os.environ["ADAPTER_TIMEOUT"] = "10"

# -- The refusals: each returns 1, and no judgement
# stands after any of them.
wrong = dict(RECEIPT, probe_evidence_hash="f" * 64)
rc = harness.run_probe_phase2(
    RUN_DIR, write_receipt("wrong-evidence.json", wrong))
check("phase 2 refuses a receipt whose probe evidence "
      "hash is wrong", rc == 1 and judged_events() == [])
wrong = dict(RECEIPT, generated_record_hash="e" * 64)
rc = harness.run_probe_phase2(
    RUN_DIR, write_receipt("wrong-record.json", wrong))
check("phase 2 refuses a receipt whose generated-"
      "record hash is wrong",
      rc == 1 and judged_events() == [])
wrong = dict(RECEIPT, fingerprint="d" * 64)
rc = harness.run_probe_phase2(
    RUN_DIR, write_receipt("wrong-fingerprint.json",
                           wrong))
check("phase 2 refuses a receipt whose configuration "
      "fingerprint is wrong",
      rc == 1 and judged_events() == [])
rc = harness.run_probe_phase2(
    RUN_DIR, os.path.join(TMP, "no-such-receipt.json"))
check("phase 2 refuses a missing receipt",
      rc == 1 and judged_events() == [])

# -- The correct receipt carries the run through.
GOOD_RECEIPT_PATH = write_receipt("receipt.json", RECEIPT)
rc = harness.run_probe_phase2(RUN_DIR, GOOD_RECEIPT_PATH)
check("phase 2 with the correct receipt completes "
      "the run", rc == 0, f"rc={rc}")
store = FrameworkStore(os.path.join(RUN_DIR, "run.db"))
events = store.all_events()
types = [e["type"] for e in events]
judged = [e for e in events
          if e["type"] == "ASSEMBLY_JUDGED"]
jp = judged[0]["payload"] if judged else {}
check("the recorded judgement binds the decision "
      "receipt's canonical hash",
      jp.get("decision_receipt_hash") == RECEIPT_HASH,
      f"hash={jp.get('decision_receipt_hash')}")
check("the judgement carries the examiner's recorded "
      "label and the decision-recording note — the "
      "token authenticates the recording act, not the "
      "examiner's identity",
      jp.get("decision_examiner") == "exam-1" and
      "authenticates the recording act" in
      (jp.get("decision_recording") or ""))
check("the assembly packed and activated under the "
      "receipt's mode",
      "ASSEMBLY_PACKED" in types and
      "INSTANCE_ACTIVATED" in types and
      jp.get("adapter_mode") == "native")
report_path = os.path.join(RUN_DIR, "report.json")
report = None
if os.path.exists(report_path):
    with open(report_path, encoding="utf-8") as fh:
        report = json.load(fh)
check("report.json names the probed mode and the "
      "decision receipt hash",
      report is not None and
      report.get("probed_mode") is True and
      report.get("adapter_mode") == "native" and
      report.get("decision_receipt_hash") ==
      RECEIPT_HASH)

# -- The retention (INDEX 295): the exact receipt file
# stands in the run directory, byte-identical to the
# receipt supplied, and the canonical hash of what
# stands there is the hash bound in the judgement — an
# auditor reads the very document the hash identifies.
# The phase-2 report names the retained file.
retained_path = os.path.join(RUN_DIR,
                             "decision-receipt.json")
retained_bytes = None
if os.path.exists(retained_path):
    with open(retained_path, "rb") as fh:
        retained_bytes = fh.read()
with open(GOOD_RECEIPT_PATH, "rb") as fh:
    supplied_bytes = fh.read()
retained_hash = None
if retained_bytes is not None:
    retained_hash = hashlib.sha256(canonical(
        json.loads(retained_bytes.decode("utf-8")))
    ).hexdigest()
check("the exact receipt file stands retained in the "
      "run directory — byte-identical to the receipt "
      "supplied, its canonical hash the hash bound in "
      "ASSEMBLY_JUDGED, and the phase-2 report names "
      "the retained file",
      retained_bytes is not None and
      retained_bytes == supplied_bytes and
      retained_hash == RECEIPT_HASH and
      jp.get("decision_receipt_hash") == retained_hash
      and report is not None and
      report.get("decision_receipt_file") ==
      "decision-receipt.json",
      f"retained_hash={retained_hash}")

# -- The independent checker over the full probed
# record (the probe suite's own runner shape).
store._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
req = {"store_path": store.path,
       "run_id": harness.RUN_ID,
       "snapshot": projection.snapshot(store)}
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
           PYTHONPATH=os.path.join(ROOT, "src"))
proc = subprocess.run(
    [sys.executable, "-B", "-m", "checker"],
    input=json.dumps(req), capture_output=True,
    text=True, env=env, cwd=ROOT)
verdict = json.loads(proc.stdout)
assembly = verdict["checks"]["assembly_correspondence"]
check("the independent checker is all-ok over the "
      "full probed record",
      assembly["result"] == "ok",
      json.dumps(assembly.get("problems", []))[:200])

shutil.rmtree(RUN_DIR, ignore_errors=True)
shutil.rmtree(TMP, ignore_errors=True)
print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES")
    sys.exit(1)
print("ALL PASS")
