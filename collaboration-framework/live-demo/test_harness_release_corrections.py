"""Focused witness for the evidenced run's two release
corrections (INDEX 322):

1. The phase-2 report's evidence summary: a stub
   phase-2 run whose worker answers (a yield) produces
   a report whose evidence_summary carries the
   iteration's captured disposition with the artifact's
   identity as committed — checked three ways, against
   the report, the record's committed RESPONSE_EVIDENCE
   event, and the filed artifact itself. A second stub
   run whose helper fails the bounded call outright
   (no envelope) produces an unresolved disposition,
   and its summary entry carries the failure class and
   NO artifact fields.

2. The probed1 manifest as an explicit pre-activation
   identity condition: the real tree stages to the
   pinned hash (and the pin equals the hash recorded
   in probed1's own report); a stub root with a
   tampered source stages to a different hash and the
   identity problem fires; a fresh run staged from
   that root refuses before any run store exists; and
   a phase-1 directory whose standing manifest.json is
   tampered refuses phase 2 before any judgement
   stands — with the receipt's retention standing,
   proving the refusal is the manifest check's.

3. The phase-2 staged-file verification (INDEX 324):
   the manifest hash proves the manifest is the pinned
   manifest, not that the files under the phase-1
   sandbox still match it. A phase-1 directory whose
   staged source is altered after phase 1 — manifest
   .json untouched — refuses phase 2 (the refusal
   names the file) with no judgement and no
   activation; a directory whose staged source is
   deleted refuses the same way. Run A serves as the
   control: its untampered directory passed the gate,
   its record carrying the judgement and activation.

The real provider is never called: the stub helper
answers `chat` (identify), `chat-raw` (the probe's
five trials, natively) and `chat-raw-bounded` (the
loop) in the helpers' own shapes; its bounded mode
fails outright when STUB_BOUNDED_FAIL=1 stands in its
environment.

Run: PYTHONPATH=src python3 \
    live-demo/test_harness_release_corrections.py
Exits 0 when every check passes.
"""

import contextlib
import hashlib
import io
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
import base64, json, os, sys
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
body = json.dumps({
    "id": "chatcmpl-stub", "model": %r,
    "choices": [{"index": 0, "message": {
        "role": "assistant", "content": content}}]})
if argv and argv[0] == "chat-raw-bounded":
    if os.environ.get("STUB_BOUNDED_FAIL") == "1":
        # No envelope at all: the helper dies without
        # framing a response — the transport's seam
        # records helper_exit_no_envelope, an
        # unresolved disposition.
        sys.exit(3)
    print(json.dumps({
        "status": 200,
        "body_b64": base64.b64encode(
            body.encode("utf-8")).decode("ascii"),
        "body_complete": True, "stop_reason": "eof",
        "read_error_kind": None,
        "phase": "response_received",
        "error_kind": None}))
else:
    print(body)
''' % (PIN, DECLARATION, YIELD_CONTENT, PIN)

TMP = tempfile.mkdtemp(prefix="release-corrections-")
STUB_PATH = os.path.join(TMP, "stub_helper.py")
with open(STUB_PATH, "w", encoding="utf-8") as fh:
    fh.write(STUB_HELPER)


def run_dir_for(suffix):
    return os.path.join(ROOT, "live-demo",
                        f"first-worker-{suffix}")


def phase1(suffix):
    """Phase 1 as a harness subprocess against the
    stub helper; returns the CompletedProcess."""
    run_dir = run_dir_for(suffix)
    shutil.rmtree(run_dir, ignore_errors=True)
    env = dict(os.environ, WORKER_ROUTE="groq",
               RETRIEVAL="1", PROBED="1",
               GROQ_HELPER_PATH=STUB_PATH,
               ADAPTER_TIMEOUT="10")
    env.pop("STUB_BOUNDED_FAIL", None)
    return subprocess.run(
        [sys.executable,
         os.path.join(HERE, "first_worker_run.py"),
         "--probe-phase1", suffix],
        capture_output=True, text=True, env=env, cwd=ROOT)


def build_receipt(run_dir, grounds):
    """The examiner receipt for a standing phase-1
    directory, in the receipt suite's shape."""
    with open(os.path.join(run_dir,
                           "probe-evidence.json"),
              encoding="utf-8") as fh:
        evidence = json.load(fh)
    with open(os.path.join(run_dir, "run-export.json"),
              encoding="utf-8") as fh:
        export = json.load(fh)
    probed_ev = next(e for e in export["events"]
                     if e["type"] == "ASSEMBLY_PROBED")
    probed_payload = probed_ev.get("payload") or {}
    if isinstance(probed_payload, str):
        probed_payload = json.loads(probed_payload)
    receipt = {
        "run_id": harness.RUN_ID,
        "assembly_id": evidence.get("assembly_id"),
        "generated_record_hash":
            evidence.get("generated_record_hash"),
        "probed_seq": probed_ev.get("event_seq"),
        "probe_evidence_hash":
            probed_payload.get("evidence_hash"),
        "fingerprint": probed_payload.get("fingerprint"),
        "adapter_mode": evidence.get("recommended_mode"),
        "mode_grounds": grounds,
        "examiner": "exam-1",
        "decided_at": "2026-11-23T22:40:00-07:00",
    }
    path = os.path.join(TMP,
                        f"receipt-{os.path.basename(run_dir)}"
                        ".json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh)
    return path


def load_report(run_dir):
    path = os.path.join(run_dir, "report.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


os.environ["GROQ_HELPER_PATH"] = STUB_PATH
os.environ["ADAPTER_TIMEOUT"] = "10"

# ================= Run A: the captured disposition ==
SUFFIX_A = "witnessrelA"
DIR_A = run_dir_for(SUFFIX_A)
proc = phase1(SUFFIX_A)
check("run A: phase 1 completes against the stub "
      "helper", proc.returncode == 0,
      f"rc={proc.returncode} "
      f"stderr={proc.stderr.strip()[:200]}")
rc = harness.run_probe_phase2(
    DIR_A, build_receipt(DIR_A, "witness: the probe's "
                                "recommendation"))
check("run A: phase 2 completes the run", rc == 0,
      f"rc={rc}")
report_a = load_report(DIR_A)
summary_a = (report_a or {}).get("evidence_summary")
check("run A: report.json carries an evidence_summary "
      "with one entry for the one entered iteration",
      isinstance(summary_a, list) and len(summary_a) == 1,
      f"summary={summary_a}")
entry_a = summary_a[0] if summary_a else {}
store_a = FrameworkStore(os.path.join(DIR_A, "run.db"))
disp_a = [e for e in store_a.all_events()
          if e["type"] == "RESPONSE_EVIDENCE"]
dp_a = disp_a[0]["payload"] if disp_a else {}
l1_a = (dp_a.get("layers") or {}).get("L1") or {}
check("run A: the summary entry records the captured "
      "disposition for iteration 1",
      entry_a.get("iteration") == 1 and
      entry_a.get("disposition") == "captured",
      f"entry={entry_a}")
check("run A: the summary's artifact identity is the "
      "record's committed identity (hash, L1 byte "
      "count, stop_reason, body_complete)",
      entry_a.get("artifact_sha256") ==
      dp_a.get("artifact_sha256") and
      entry_a.get("l1_byte_count") ==
      l1_a.get("byte_count") and
      isinstance(entry_a.get("l1_byte_count"), int) and
      entry_a.get("l1_byte_count", 0) > 0 and
      entry_a.get("stop_reason") == "eof" and
      entry_a.get("body_complete") is True,
      f"entry={entry_a}")
artifact_path_a = os.path.join(
    DIR_A, "responses",
    f"iteration-{entry_a.get('iteration_seq')}.json")
file_hash_a = None
if os.path.exists(artifact_path_a):
    with open(artifact_path_a, "rb") as fh:
        file_hash_a = hashlib.sha256(fh.read()).hexdigest()
check("run A: the filed artifact stands where the "
      "summary names it, its bytes hash to the "
      "committed artifact hash, and the summary's "
      "cross-check says ok",
      file_hash_a is not None and
      file_hash_a == entry_a.get("artifact_sha256") and
      entry_a.get("artifact_check") == "ok",
      f"file_hash={file_hash_a} "
      f"check={entry_a.get('artifact_check')}")

# ============ Run B: the unresolved disposition =====
SUFFIX_B = "witnessrelB"
DIR_B = run_dir_for(SUFFIX_B)
proc = phase1(SUFFIX_B)
check("run B: phase 1 completes against the stub "
      "helper", proc.returncode == 0,
      f"rc={proc.returncode} "
      f"stderr={proc.stderr.strip()[:200]}")
os.environ["STUB_BOUNDED_FAIL"] = "1"
try:
    rc = harness.run_probe_phase2(
        DIR_B, build_receipt(DIR_B, "witness: the "
                                    "probe's "
                                    "recommendation"))
finally:
    os.environ.pop("STUB_BOUNDED_FAIL", None)
check("run B: phase 2 completes (the run stalls on "
      "the failed call, and the report is written)",
      rc == 0, f"rc={rc}")
report_b = load_report(DIR_B)
summary_b = (report_b or {}).get("evidence_summary")
entry_b = summary_b[0] if summary_b else {}
check("run B: the summary's first entry records the "
      "unresolved disposition under its failure class",
      entry_b.get("disposition") == "unresolved" and
      entry_b.get("failure_class") ==
      "helper_exit_no_envelope",
      f"entry={entry_b}")
check("run B: the unresolved entry carries NO "
      "artifact fields, and no artifact stands for "
      "its iteration",
      summary_b and
      all("artifact_sha256" not in e and
          "l1_byte_count" not in e and
          "stop_reason" not in e and
          "body_complete" not in e
          for e in summary_b) and
      not os.path.exists(os.path.join(
          DIR_B, "responses",
          f"iteration-{entry_b.get('iteration_seq')}"
          ".json")),
      f"summary={summary_b}")

# ============ The manifest identity condition =======
real_dir = os.path.join(TMP, "stage-real")
_, real_hash = harness.stage(real_dir)
with open(os.path.join(
        ROOT, "live-demo", "first-worker-probed1",
        "report.json"), encoding="utf-8") as fh:
    probed1_hash = json.load(fh)["manifest_hash"]
check("the pinned EXPECTED_MANIFEST_HASH is the "
      "manifest hash recorded in probed1's own report",
      harness.EXPECTED_MANIFEST_HASH == probed1_hash,
      f"pinned={harness.EXPECTED_MANIFEST_HASH}")
check("the real tree stages to the probed1 manifest "
      "hash and the identity problem does not fire",
      real_hash == probed1_hash and
      harness._manifest_identity_problem(real_hash)
      is None,
      f"staged={real_hash}")

STUB_ROOT = os.path.join(TMP, "stub-root")
os.makedirs(STUB_ROOT)
for filed in ("VANE-STOCK-TAKE-2026-11-23.md",
              "VANE-PIECE-A3-PASS-2026-11-23.md",
              "INDEX.md"):
    shutil.copyfile(os.path.join(ROOT, filed),
                    os.path.join(STUB_ROOT, filed))
with open(os.path.join(
        STUB_ROOT, "VANE-STOCK-TAKE-2026-11-23.md"),
        "ab") as fh:
    fh.write(b"\ntampered: one byte too many\n")
tampered_dir = os.path.join(TMP, "stage-tampered")
_, tampered_hash = harness.stage(tampered_dir,
                                 root=STUB_ROOT)
check("a tampered source stages to a different "
      "manifest hash and the identity problem fires, "
      "naming both hashes",
      tampered_hash != probed1_hash and
      harness._manifest_identity_problem(tampered_hash)
      is not None and
      tampered_hash in
      harness._manifest_identity_problem(tampered_hash)
      and probed1_hash in
      harness._manifest_identity_problem(tampered_hash),
      f"tampered={tampered_hash}")

real_stage = harness.stage
harness.stage = lambda run_dir: real_stage(
    run_dir, root=STUB_ROOT)
try:
    fresh_dir = os.path.join(TMP, "fresh-refused")
    os.makedirs(fresh_dir)
    rc = harness._run_fresh(fresh_dir, "groq", True,
                            False, False)
finally:
    harness.stage = real_stage
check("a fresh run staged from the tampered root "
      "refuses pre-activation (rc 1) and no run store "
      "is ever created",
      rc == 1 and not os.path.exists(
          os.path.join(fresh_dir, "run.db")),
      f"rc={rc}")

SUFFIX_C = "witnessrelC"
DIR_C = run_dir_for(SUFFIX_C)
proc = phase1(SUFFIX_C)
check("run C: phase 1 completes against the stub "
      "helper", proc.returncode == 0,
      f"rc={proc.returncode} "
      f"stderr={proc.stderr.strip()[:200]}")
manifest_path_c = os.path.join(DIR_C, "manifest.json")
with open(manifest_path_c, encoding="utf-8") as fh:
    manifest_c = json.load(fh)
manifest_c["sources"][0]["provenance"] += " (tampered)"
with open(manifest_path_c, "w", encoding="utf-8") as fh:
    json.dump(manifest_c, fh, indent=1)
    fh.write("\n")
rc = harness.run_probe_phase2(
    DIR_C, build_receipt(DIR_C, "witness: the probe's "
                                "recommendation"))
store_c = FrameworkStore(os.path.join(DIR_C, "run.db"))
judged_c = [e for e in store_c.all_events()
            if e["type"] == "ASSEMBLY_JUDGED"]
check("phase 2 refuses a run directory whose standing "
      "manifest is not the probed1 manifest — rc 1, no "
      "judgement stands, and the receipt's retention "
      "stands (the refusal is the manifest check's, "
      "past receipt validation)",
      rc == 1 and judged_c == [] and
      os.path.exists(os.path.join(
          DIR_C, "decision-receipt.json")),
      f"rc={rc} judged={len(judged_c)}")

# ====== Phase-2 staged-file verification (324) =====
# The control: run A's directory was never touched
# between its phases, and its phase 2 completed — its
# record carries the judgement and the activation,
# which stand only past the staged-file gate.
types_a = [e["type"] for e in store_a.all_events()]
check("control: run A's untampered directory passed "
      "the phase-2 staged-file gate — the judgement "
      "and the activation stand in its record",
      "ASSEMBLY_JUDGED" in types_a and
      "INSTANCE_ACTIVATED" in types_a,
      f"judged={'ASSEMBLY_JUDGED' in types_a} "
      f"activated={'INSTANCE_ACTIVATED' in types_a}")


def staged_entry_path(run_dir):
    """The first manifest entry's staged file, under
    the run directory's sandbox."""
    with open(os.path.join(run_dir, "manifest.json"),
              encoding="utf-8") as fh:
        manifest = json.load(fh)
    entry_path = manifest["sources"][0]["path"]
    return entry_path, os.path.join(
        run_dir, "sandbox", entry_path)


def phase2_capturing(run_dir):
    """Phase 2 in-process with stderr captured, so the
    refusal's own words can be checked."""
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = harness.run_probe_phase2(
            run_dir, build_receipt(
                run_dir, "witness: the probe's "
                         "recommendation"))
    return rc, err.getvalue()


def judged_or_activated(run_dir):
    store = FrameworkStore(
        os.path.join(run_dir, "run.db"))
    types = [e["type"] for e in store.all_events()]
    return ("ASSEMBLY_JUDGED" in types,
            "INSTANCE_ACTIVATED" in types)


SUFFIX_D = "witnessrelD"
DIR_D = run_dir_for(SUFFIX_D)
proc = phase1(SUFFIX_D)
check("run D: phase 1 completes against the stub "
      "helper", proc.returncode == 0,
      f"rc={proc.returncode} "
      f"stderr={proc.stderr.strip()[:200]}")
entry_path_d, staged_d = staged_entry_path(DIR_D)
with open(staged_d, "ab") as fh:
    fh.write(b"\naltered after phase 1\n")
rc, err_d = phase2_capturing(DIR_D)
check("phase 2 refuses a staged source altered after "
      "phase 1, manifest.json untouched — rc 1, and "
      "the refusal names the altered file",
      rc == 1 and entry_path_d in err_d,
      f"rc={rc} stderr={err_d.strip()[:200]}")
judged_d, activated_d = judged_or_activated(DIR_D)
check("run D: no ASSEMBLY_JUDGED and no activation "
      "stand after the staged-file refusal",
      not judged_d and not activated_d,
      f"judged={judged_d} activated={activated_d}")

SUFFIX_E = "witnessrelE"
DIR_E = run_dir_for(SUFFIX_E)
proc = phase1(SUFFIX_E)
check("run E: phase 1 completes against the stub "
      "helper", proc.returncode == 0,
      f"rc={proc.returncode} "
      f"stderr={proc.stderr.strip()[:200]}")
entry_path_e, staged_e = staged_entry_path(DIR_E)
os.remove(staged_e)
rc, err_e = phase2_capturing(DIR_E)
check("phase 2 refuses a staged source missing after "
      "phase 1 — rc 1, and the refusal names the "
      "missing file",
      rc == 1 and entry_path_e in err_e,
      f"rc={rc} stderr={err_e.strip()[:200]}")
judged_e, activated_e = judged_or_activated(DIR_E)
check("run E: no ASSEMBLY_JUDGED and no activation "
      "stand after the missing-file refusal",
      not judged_e and not activated_e,
      f"judged={judged_e} activated={activated_e}")

for suffix in (SUFFIX_A, SUFFIX_B, SUFFIX_C,
               SUFFIX_D, SUFFIX_E):
    shutil.rmtree(run_dir_for(suffix),
                  ignore_errors=True)
shutil.rmtree(TMP, ignore_errors=True)
print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES")
    sys.exit(1)
print("ALL PASS")
