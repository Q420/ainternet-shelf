"""Focused witness for the connector transport
(live-demo/connector_transport.py) — the examiner's
cancellation-boundary conditions
(VANE-FIRST-WORKER-RUN-TRANSPORT-EXAMINATION-2026-11-23.md,
INDEX 192), exercised entirely against STUB helpers written
to a temp dir. The real provider is never called.

1. Success path preserved: a stub returning a canned
   OpenAI chat JSON -> the real adapter with the wrapper
   installed returns the content and the provider-reported
   model id unaltered at the _call level, the typed yield
   outcome at the __call__ level, and identify()'s
   declaration + provider id verbatim.
2. Expiry + termination: a stub that sleeps 10s -> a ~1s
   bound raises no_response in well under 10s, and the
   helper pid is CONFIRMED dead afterwards (kill(pid, 0)
   raises — the process is gone and reaped, not abandoned).
3. No late success: ~3s after the expiry the helper is
   still gone and no outcome exists. This witnesses the
   property because the wrapper is synchronous with a
   single return point that already raised: there is no
   worker thread, callback or future in the design that
   could deliver the helper's late bytes, and the process
   that would have produced them (at 10s, had it merely
   been abandoned) no longer exists.
4. Unresolved branch: with the process-group kill patched
   to fail, expiry raises the distinct kind
   transport_unresolved — never no_response.
5. Request fidelity: the body the stub received names the
   model and carries the messages verbatim, field-for-field
   what the adapter's own _dispatch sends
   ({model, messages, temperature: 0.2} — no other fields).

Run: PYTHONPATH=src python3 live-demo/test_connector_transport.py
Exits 0 when every check passes.
"""

import json
import os
import shutil
import signal
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)

from framework.adapter import (AdapterFailure,  # noqa: E402
                               OpenAICompatibleAdapter)
import connector_transport  # noqa: E402
from connector_transport import (  # noqa: E402
    install_connector_transport)

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name +
          (("  " + detail) if detail else ""))
    if not cond:
        FAILURES.append(name)


DECLARATION = ("I am StubModel 1.0, provided by "
               "StubProvider for tests.")
YIELD_CONTENT = json.dumps(
    {"outcome": "yield", "summary": "the stub stands"})
STUB_OK = '''\
import json, os, sys
raw = sys.stdin.buffer.read()
rec = os.environ.get("STUB_RECORD")
if rec:
    with open(rec, "wb") as fh:
        fh.write(raw)
if b"State your identity" in raw:
    content = %r
else:
    content = %r
print(json.dumps({
    "id": "chatcmpl-stub", "model": "stub/model-1",
    "choices": [{"index": 0, "message": {
        "role": "assistant", "content": content}}]}))
''' % (DECLARATION, YIELD_CONTENT)

STUB_SLEEP = '''\
import json, os, sys, time
pidfile = os.environ.get("STUB_PIDFILE")
if pidfile:
    with open(pidfile, "w") as fh:
        fh.write(str(os.getpid()))
sys.stdin.buffer.read()
time.sleep(10)
print(json.dumps({
    "id": "chatcmpl-stub", "model": "stub/model-1",
    "choices": [{"index": 0, "message": {
        "role": "assistant", "content": %r}}]}))
''' % YIELD_CONTENT

TMP = tempfile.mkdtemp(prefix="connector-transport-witness-")
OK_PATH = os.path.join(TMP, "stub_ok.py")
SLEEP_PATH = os.path.join(TMP, "stub_sleep.py")
RECORD = os.path.join(TMP, "last_request.json")
PIDFILE = os.path.join(TMP, "sleeper.pid")
with open(OK_PATH, "w", encoding="utf-8") as fh:
    fh.write(STUB_OK)
with open(SLEEP_PATH, "w", encoding="utf-8") as fh:
    fh.write(STUB_SLEEP)

PACKAGE = {"case_id": "case-crew-1", "case_version": 1,
           "seat": "crew-1", "position": 3,
           "case": {"part": "part-A"}}


def pid_dead(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return False


# -- 1: the success path, preserved end to end.
adapter = OpenAICompatibleAdapter(model="stub/model-1",
                                  timeout=10.0)
install_connector_transport(adapter, OK_PATH, "stub/model-1")
content, pmid = adapter._call(
    [{"role": "user", "content": "hello"}])
check("1: _call returns the stub's content unaltered",
      content == YIELD_CONTENT)
check("1: _call returns the provider-reported model id "
      "unaltered", pmid == "stub/model-1")
outcome = adapter(PACKAGE)
check("1: the adapter's typed outcome crosses whole (yield)",
      outcome == {"outcome": "yield",
                  "summary": "the stub stands"})
identity = adapter.identify()
check("1: identify() returns the declaration verbatim",
      identity["declaration"] == DECLARATION)
check("1: identify() returns the provider id verbatim",
      identity["provider_model_id"] == "stub/model-1")

# -- 5: request fidelity (the stub recorded its stdin).
os.environ["STUB_RECORD"] = RECORD
MESSAGES = [{"role": "system", "content": "s"},
            {"role": "user", "content": "u"}]
adapter._call(MESSAGES)
with open(RECORD, "rb") as fh:
    sent = json.loads(fh.read().decode("utf-8"))
check("5: the body carries exactly the adapter's own fields "
      "(model, messages, temperature)",
      set(sent) == {"model", "messages", "temperature"})
check("5: the body names the model",
      sent.get("model") == "stub/model-1")
check("5: the messages cross verbatim",
      sent.get("messages") == MESSAGES)
check("5: temperature is the adapter's own 0.2",
      sent.get("temperature") == 0.2)
os.environ.pop("STUB_RECORD", None)

# -- 2 + 3: expiry, confirmed termination, no late success.
os.environ["STUB_PIDFILE"] = PIDFILE
adapter2 = OpenAICompatibleAdapter(model="stub/model-1",
                                   timeout=1.0)
install_connector_transport(adapter2, SLEEP_PATH,
                            "stub/model-1")
holder = {"result": None, "failure": None}
t0 = time.monotonic()
try:
    holder["result"] = adapter2._call(
        [{"role": "user", "content": "hello"}])
except AdapterFailure as failure:
    holder["failure"] = failure
elapsed = time.monotonic() - t0
raised_at = time.monotonic()
failure = holder["failure"]
check("2: expiry raises AdapterFailure of the adapter's own "
      "expiry kind, no_response",
      failure is not None and failure.kind == "no_response",
      f"kind={getattr(failure, 'kind', None)}")
check("2: no outcome was produced",
      holder["result"] is None)
check("2: the call returned in well under the stub's 10s "
      "sleep", elapsed < 4.0, f"elapsed={elapsed:.2f}s")
with open(PIDFILE, encoding="utf-8") as fh:
    sleeper_pid = int(fh.read().strip())
check("2: the helper pid is confirmed dead afterwards "
      "(gone and reaped, not abandoned)",
      pid_dead(sleeper_pid), f"pid={sleeper_pid}")
time.sleep(max(0.0, 3.0 - (time.monotonic() - raised_at)))
check("3: ~3s after expiry the helper is still gone and "
      "still no outcome exists — no late success path",
      pid_dead(sleeper_pid) and holder["result"] is None and
      holder["failure"] is failure)
os.environ.pop("STUB_PIDFILE", None)

# -- 4: the unresolved branch — termination cannot be
# effected, so the kind is transport_unresolved.
PIDFILE2 = os.path.join(TMP, "sleeper2.pid")
os.environ["STUB_PIDFILE"] = PIDFILE2
adapter3 = OpenAICompatibleAdapter(model="stub/model-1",
                                   timeout=1.0)
install_connector_transport(adapter3, SLEEP_PATH,
                            "stub/model-1")
real_killpg = connector_transport._killpg


def broken_killpg(pgid, sig):
    raise OSError("patched: process-group kill unavailable")


connector_transport._killpg = broken_killpg
failure4 = None
try:
    adapter3._call([{"role": "user", "content": "hello"}])
except AdapterFailure as failure:
    failure4 = failure
finally:
    connector_transport._killpg = real_killpg
check("4: unconfirmable termination raises the distinct "
      "kind transport_unresolved, never no_response",
      failure4 is not None and
      failure4.kind == "transport_unresolved",
      f"kind={getattr(failure4, 'kind', None)}")
# Cleanup: the unresolved helper is still alive by design;
# kill it directly so the witness leaves nothing running.
# The stub is this process's own child (the wrapper spawned
# it here), so reap it with waitpid — an unreaped zombie
# still answers kill(pid, 0) and would masquerade as alive.
try:
    with open(PIDFILE2, encoding="utf-8") as fh:
        pid2 = int(fh.read().strip())
    os.kill(pid2, signal.SIGKILL)
    deadline = time.monotonic() + 3.0
    reaped = False
    while time.monotonic() < deadline:
        try:
            done, _status = os.waitpid(pid2, os.WNOHANG)
            reaped = done == pid2
        except ChildProcessError:
            reaped = True
        if reaped or pid_dead(pid2):
            break
        time.sleep(0.05)
    print(f"cleanup: unresolved stub pid {pid2} killed, "
          f"reaped={reaped}, dead={pid_dead(pid2)}")
except Exception as exc:
    print(f"cleanup warning: {exc}")
os.environ.pop("STUB_PIDFILE", None)

shutil.rmtree(TMP, ignore_errors=True)
print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES")
    sys.exit(1)
print("ALL PASS")
