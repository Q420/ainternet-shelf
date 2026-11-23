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
6. The adapter's actual remaining deadline governs
   (VANE-CONNECTOR-TRANSPORT-EXAMINATION-2026-11-23.md,
   correction 1): with a 2s deadline established on the
   real adapter and ~half of it already elapsed before
   _call starts, a 10s sleeper is terminated at the
   ORIGINAL deadline — not granted a fresh full timeout —
   and raises no_response with the pid confirmed dead.
   Separately: with the deadline already expired before
   _call, the helper is never launched at all (its pid
   marker never appears) and no_response is raised.
7. Negative witness for the group confirmation
   (correction 2): the kill is real but the group-emptiness
   probe is patched to raise PermissionError during
   confirmation, so emptiness cannot be established ->
   transport_unresolved, never no_response, no outcome —
   even though the helper really is dead. An unknown or
   unprobable group is never treated as an empty one.
8. Process creation consumes the remaining deadline
   (VANE-CONNECTOR-TRANSPORT-REEXAMINATION-2026-11-23.md,
   item 3): the module's _Popen alias is patched to sleep
   ~1.5s before delegating to the real constructor,
   against an adapter deadline with ~1.0s remaining at
   call time and a stub that sleeps 10s before printing
   a valid success JSON. The pre-creation bound passes
   the launch check, but by the time the helper exists
   the deadline is gone: the wrapper must recompute,
   refuse the wait, and put the newly launched helper
   through the same cancellation procedure — no_response,
   the pid confirmed dead, no outcome, and still no
   outcome ~3s later (no late result).

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

# -- 6: the adapter's actual remaining deadline governs —
# a partially elapsed deadline terminates the helper at
# the ORIGINAL deadline, not at a fresh full timeout.
PIDFILE6 = os.path.join(TMP, "sleeper6.pid")
os.environ["STUB_PIDFILE"] = PIDFILE6
adapter6 = OpenAICompatibleAdapter(model="stub/model-1",
                                   timeout=30.0)
install_connector_transport(adapter6, SLEEP_PATH,
                            "stub/model-1")
SPAN6 = 2.0
t_begin6 = time.monotonic()
adapter6._begin_deadline(budget=SPAN6)
time.sleep(1.0)  # ~half the span elapses before _call runs
holder6 = {"result": None, "failure": None}
t_call6 = time.monotonic()
try:
    holder6["result"] = adapter6._call(
        [{"role": "user", "content": "hello"}])
except AdapterFailure as failure:
    holder6["failure"] = failure
t_end6 = time.monotonic()
failure6 = holder6["failure"]
check("6: expiry under a partially elapsed deadline raises "
      "no_response",
      failure6 is not None and failure6.kind == "no_response",
      f"kind={getattr(failure6, 'kind', None)}")
check("6: no outcome was produced",
      holder6["result"] is None)
check("6: the helper was terminated at the original "
      "deadline — the call ran out the remaining ~1s, not "
      "a fresh 30s timeout and not the stub's 10s",
      0.5 < (t_end6 - t_call6) < 2.5 and
      (t_end6 - t_begin6) < SPAN6 + 1.5,
      f"from-deadline={t_end6 - t_begin6:.2f}s "
      f"from-call={t_end6 - t_call6:.2f}s")
with open(PIDFILE6, encoding="utf-8") as fh:
    pid6 = int(fh.read().strip())
check("6: the helper pid is confirmed dead afterwards",
      pid_dead(pid6), f"pid={pid6}")
os.environ.pop("STUB_PIDFILE", None)

# -- 6b: no time remains -> the helper is never launched.
PIDFILE6B = os.path.join(TMP, "sleeper6b.pid")
os.environ["STUB_PIDFILE"] = PIDFILE6B
adapter6b = OpenAICompatibleAdapter(model="stub/model-1",
                                    timeout=30.0)
install_connector_transport(adapter6b, SLEEP_PATH,
                            "stub/model-1")
adapter6b._begin_deadline(budget=0.2)
time.sleep(0.4)  # the deadline is already past before _call
failure6b = None
try:
    adapter6b._call([{"role": "user", "content": "hello"}])
except AdapterFailure as failure:
    failure6b = failure
check("6: an already-expired deadline raises no_response",
      failure6b is not None and
      failure6b.kind == "no_response",
      f"kind={getattr(failure6b, 'kind', None)}")
check("6: with no time remaining the helper is never "
      "launched (its pid marker never appears)",
      not os.path.exists(PIDFILE6B))
os.environ.pop("STUB_PIDFILE", None)

# -- 7: the negative witness — the expiry kill is real,
# but the group-emptiness probe fails during confirmation,
# so emptiness cannot be established and the result must
# be transport_unresolved, never a false confirmation.
PIDFILE7 = os.path.join(TMP, "sleeper7.pid")
os.environ["STUB_PIDFILE"] = PIDFILE7
adapter7 = OpenAICompatibleAdapter(model="stub/model-1",
                                   timeout=1.0)
install_connector_transport(adapter7, SLEEP_PATH,
                            "stub/model-1")
real_killpg7 = connector_transport._killpg


def probe_denied_killpg(pgid, sig):
    if sig == 0:
        raise PermissionError(
            "patched: group emptiness probe denied")
    return real_killpg7(pgid, sig)


connector_transport._killpg = probe_denied_killpg
holder7 = {"result": None, "failure": None}
try:
    holder7["result"] = adapter7._call(
        [{"role": "user", "content": "hello"}])
except AdapterFailure as failure:
    holder7["failure"] = failure
finally:
    connector_transport._killpg = real_killpg7
failure7 = holder7["failure"]
check("7: unestablishable group emptiness raises "
      "transport_unresolved, never no_response",
      failure7 is not None and
      failure7.kind == "transport_unresolved",
      f"kind={getattr(failure7, 'kind', None)}")
check("7: no outcome was produced",
      holder7["result"] is None)
with open(PIDFILE7, encoding="utf-8") as fh:
    pid7 = int(fh.read().strip())
check("7: the helper really was killed — the unresolved "
      "kind is about unprovable emptiness, not a surviving "
      "process", pid_dead(pid7), f"pid={pid7}")
os.environ.pop("STUB_PIDFILE", None)

# -- 8: process creation consumes the remaining deadline.
# The constructor is patched to sleep ~1.5s before it
# delegates, against a deadline with ~1.0s remaining at
# call time. The pre-creation bound (~1.0s) passes the
# launch check; by the time the helper exists, the
# deadline is gone. The wrapper must NOT hand the wait
# the stale bound — it must terminate the newly launched
# helper through the same cancellation procedure.
PIDFILE8 = os.path.join(TMP, "sleeper8.pid")
os.environ["STUB_PIDFILE"] = PIDFILE8
adapter8 = OpenAICompatibleAdapter(model="stub/model-1",
                                   timeout=30.0)
install_connector_transport(adapter8, SLEEP_PATH,
                            "stub/model-1")
real_popen8 = connector_transport._Popen
holder8 = {"proc": None, "result": None, "failure": None}


def slow_popen8(*args, **kwargs):
    time.sleep(1.5)  # creation eats the remaining deadline
    proc = real_popen8(*args, **kwargs)
    holder8["proc"] = proc
    return proc


connector_transport._Popen = slow_popen8
SPAN8 = 1.0
t_begin8 = time.monotonic()
adapter8._begin_deadline(budget=SPAN8)
try:
    holder8["result"] = adapter8._call(
        [{"role": "user", "content": "hello"}])
except AdapterFailure as failure:
    holder8["failure"] = failure
finally:
    connector_transport._Popen = real_popen8
t_end8 = time.monotonic()
raised8_at = time.monotonic()
failure8 = holder8["failure"]
proc8 = holder8["proc"]
check("8: creation consuming the deadline raises "
      "no_response",
      failure8 is not None and failure8.kind == "no_response",
      f"kind={getattr(failure8, 'kind', None)}")
check("8: no outcome was produced",
      holder8["result"] is None)
check("8: the helper was not granted the stale bound past "
      "the deadline — total elapsed stays close to the "
      "deadline and well under the stub's 10s",
      (t_end8 - t_begin8) < SPAN8 + 4.0,
      f"from-deadline={t_end8 - t_begin8:.2f}s")
check("8: the helper really was launched (creation was "
      "patched and slow, not skipped)", proc8 is not None)
check("8: the helper pid is confirmed dead afterwards",
      proc8 is not None and pid_dead(proc8.pid),
      f"pid={getattr(proc8, 'pid', None)}")
time.sleep(max(0.0, 3.0 - (time.monotonic() - raised8_at)))
check("8: ~3s later still no outcome exists and the "
      "helper is still gone — no late result can arrive",
      holder8["result"] is None and
      holder8["failure"] is failure8 and
      proc8 is not None and pid_dead(proc8.pid))
os.environ.pop("STUB_PIDFILE", None)

shutil.rmtree(TMP, ignore_errors=True)
print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES")
    sys.exit(1)
print("ALL PASS")
