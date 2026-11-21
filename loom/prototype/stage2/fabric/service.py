"""Fabric service — Loom spec v0.1 Rev 9, section 4A, as corrected.

Stage 2 corrections round (2026-11-21). The service is the fabric's
OS-level boundary made real: it runs under its own OS identity
(loomfab), owns the event store and the sealed ground-truth file
inside a directory that identity alone can enter, and serves agent
operations over a Unix data socket. Agent processes run under a
different identity (loomagent) and hold only fabric/client.py: the
data socket protocol is the whole of their reach.

Two sockets, two trust levels:

- data socket (sock/fabric.sock): the five agent operations —
  view_pattern, consult_index, open_region, submit, read_breadth —
  each authenticated by a per-run token. There is NO issuance
  operation on this socket, by design: an issuance attempt is an
  unknown operation.
- admin socket (service/admin.sock, inside the loomfab-only
  directory): the operator path — issue_token, open_run,
  record_probe_attestation, history, status, shutdown. The agent
  identity cannot even traverse the directory that holds it.

Run failure (Vane's correction conditions, section 3): when the
harness raises HardLineBreach, the service — the run's owner —
appends the system RUN_FAILED event through the engine's atomic
commit path, so the append and the transition to failed state are
one act; the fold derives the failed state from the history, and
every data operation refuses from then on, across restarts. If the
append itself fails, the service fails closed anyway: it latches
in-process (all further agent operations refused), writes an
external diagnostic record into the service failures directory
distinguishing the unrecordable failure, and never fabricates a
RUN_FAILED event. The fault can be injected for tests by starting
the service with LOOM_FAULT_INJECT=run_failed_append.
"""
import argparse
import json
import os
import socketserver
import threading
from datetime import datetime, timezone

from .canonical import canonical, sha256_hex
from .engine import Engine
from .fixture import SYSTEM_ACTOR, load_ground_truth
from .harness import (Harness, HardLineBreach, HarnessRefusal,
                      TransportRefusal)
from .store import EventStore

AGENT_OPS = ("view_pattern", "consult_index", "open_region", "submit",
             "read_breadth")


def _ok(result):
    return {"ok": True, "result": result}


def _err(kind, error):
    return {"ok": False, "kind": kind, "error": error}


class FabricService:
    def __init__(self, runtime_dir):
        self.runtime_dir = runtime_dir
        self.service_dir = os.path.join(runtime_dir, "service")
        self.sock_dir = os.path.join(runtime_dir, "sock")
        self.store_path = os.path.join(self.service_dir, "events.db")
        self.gt_path = os.path.join(self.service_dir, "ground-truth.json")
        self.failures_dir = os.path.join(self.service_dir, "failures")
        self.data_sock = os.path.join(self.sock_dir, "fabric.sock")
        self.admin_sock = os.path.join(self.service_dir, "admin.sock")
        self.fault_inject = os.environ.get("LOOM_FAULT_INJECT", "")
        self._latched = False
        self._latch_info = None
        self._stopped = threading.Event()
        os.umask(0o077)
        # The sealed ground truth: loaded from the service-side file
        # at startup and held in memory. It is never served, never
        # written to an event, and no operation returns any part of
        # it; loading it here proves the service identity can read
        # what the agent identity cannot.
        self._ground_truth = load_ground_truth(self.gt_path)
        self.store = EventStore(self.store_path, check_same_thread=False)
        self.engine = Engine(self.store)
        self.harness = Harness(self.engine)
        # All dispatch is serialised: the store connection and the
        # engine's append+fold transactions are single-threaded
        # objects, and section 3's atomicity is defined over a
        # serial history anyway.
        self._lock = threading.RLock()

    # -- run state ---------------------------------------------------
    @property
    def failed(self):
        return self.engine.state.get("run_status") == "failed"

    # -- agent-facing dispatch ----------------------------------------
    def dispatch_data(self, req):
        with self._lock:
            return self._dispatch_data(req)

    def _dispatch_data(self, req):
        op = req.get("op")
        if op not in AGENT_OPS:
            return _err("unknown_op",
                        f"the agent interface has no operation {op!r}")
        if self._latched:
            return _err(
                "run_failed_unrecorded",
                "the run failed and the failure could not be "
                "recorded; this service is latched closed — see the "
                "diagnostic record in the service failures directory")
        if self.failed:
            return _err(
                "run_failed",
                "the run has failed (RUN_FAILED is in its history); "
                "no further agent activity is admitted")
        token = req.get("token")
        try:
            if op == "view_pattern":
                return _ok(self.harness.view_pattern(token))
            if op == "consult_index":
                return _ok(self.harness.consult_index(token))
            if op == "open_region":
                return _ok(self.harness.open_region(
                    token, req.get("region_id")))
            if op == "read_breadth":
                # Same trust domain (service-side): resolve the token
                # to its identity, then report that identity's breadth.
                agent = self.harness._authenticate(token)
                return _ok({"read_breadth":
                            self.harness.read_breadth(agent)})
            if op == "submit":
                return _ok(self.harness.submit(token, req.get("response")))
        except HardLineBreach as breach:
            self._fail_run(breach)
            if self._latched:
                return _err(
                    "run_failed_unrecorded",
                    f"hard-line breach; the run has failed and the "
                    f"failure could not be recorded, so this service "
                    f"is latched closed: {breach}")
            return _err("run_failed",
                        f"hard-line breach; the run has failed: {breach}")
        except TransportRefusal as exc:
            return _err("transport_refusal", str(exc))
        except HarnessRefusal as exc:
            return _err("refusal", str(exc))
        except Exception as exc:  # never hang an agent on a bug
            return _err("internal", f"{type(exc).__name__}: {exc}")
        return _err("internal", "unreachable dispatch state")

    # -- run failure ----------------------------------------------------
    def _fail_run(self, breach):
        declared = set(breach.declared_read_set)
        recorded = set(breach.recorded_read_set)
        payload = {
            "breach": "hard_line_read_record",
            "declared_read_set": breach.declared_read_set,
            "recorded_read_set": breach.recorded_read_set,
            "claimed_but_not_made": sorted(declared - recorded),
            "made_but_not_claimed": sorted(recorded - declared),
            "detail": str(breach),
            "summary": "The run failed: a contribution declared a "
                       "read set that does not match the harness "
                       "read record — a hard-line breach (section "
                       "9). The run is stopped; no further agent "
                       "activity is admitted.",
        }
        try:
            if self.fault_inject == "run_failed_append":
                raise RuntimeError(
                    "injected fault (LOOM_FAULT_INJECT): the "
                    "RUN_FAILED append failed")
            self.engine.commit_events(
                [("RUN_FAILED", SYSTEM_ACTOR, [], payload)])
        except Exception as exc:
            # Failure of failure: fail closed WITHOUT fabricating the
            # event. Latch in-process and preserve the evidence
            # externally, so the record distinguishes a recorded
            # failure from an unrecordable one.
            self._latched = True
            self._latch_info = {
                "breach": payload,
                "append_error": f"{type(exc).__name__}: {exc}",
            }
            self._write_diagnostic()

    def _write_diagnostic(self):
        record = {
            "kind": "unrecordable_run_failure",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "run_id": self.store.get_run_id(),
            "breach": self._latch_info["breach"],
            "append_error": self._latch_info["append_error"],
            "note": "The RUN_FAILED event could not be appended. The "
                    "service latched closed in-process and refused "
                    "all further agent operations. No RUN_FAILED "
                    "event exists in the history; this file is the "
                    "record of the failure, and it is deliberately "
                    "NOT part of the event history.",
            "summary": "An unrecordable run failure occurred and was "
                       "preserved as an external diagnostic record; "
                       "the service failed closed.",
        }
        try:
            os.makedirs(self.failures_dir, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime(
                "%Y%m%dT%H%M%S.%fZ")
            path = os.path.join(self.failures_dir,
                                f"unrecorded-failure-{stamp}.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(record, fh, indent=2, sort_keys=True)
        except OSError:
            pass  # the latch still holds; nothing else can be done

    # -- operator/admin dispatch ----------------------------------------
    def dispatch_admin(self, req):
        with self._lock:
            return self._dispatch_admin(req)

    def _dispatch_admin(self, req):
        op = req.get("op")
        try:
            if op == "status":
                events = self.store.all_events()
                return _ok({
                    "run_id": self.store.get_run_id(),
                    "events": len(events),
                    "head_hash": events[-1]["hash"] if events else None,
                    "run_status": ("failed" if self.failed else
                                   "open" if events else "unopened"),
                    "latched_unrecorded_failure": self._latched,
                })
            if op == "history":
                return _ok({"events": self.store.all_events()})
            if op == "issue_token":
                return _ok({"token": self.harness.issue_token(
                    req.get("agent_id"))})
            if op == "open_run":
                if self.store.all_events():
                    return _err("refusal",
                                "the store already holds a run")
                self.engine = Engine.open_run(self.store,
                                              req.get("run_id"))
                self.harness = Harness(self.engine)
                return _ok({"run_id": req.get("run_id"), "events": 1})
            if op == "record_probe_attestation":
                events = self.store.all_events()
                if len(events) != 1 or events[0]["type"] != "RUN_OPENED":
                    return _err(
                        "refusal",
                        "the attestation must be the second event: "
                        "the run must be open and no other event may "
                        "precede it")
                result = req.get("probe_result")
                payload = {
                    "attestation": True,
                    "probe": result,
                    "probe_result_hash": sha256_hex(canonical(result)),
                    "summary": "Boundary probe attestation: before "
                               "this run opened, the pre-run "
                               "boundary probe ran against a "
                               "disposable twin of this runtime (same "
                               "layout, owners, permissions and "
                               "service build) from the agent OS "
                               "context. The twin's store and "
                               "ground-truth files denied every "
                               "direct and alternate-path read; "
                               "forged-token and issuance attempts "
                               "on the data socket were refused; "
                               "legitimate operations through the "
                               "harness succeeded. This event "
                               "attests to that twin probe — the "
                               "experimental store itself was not "
                               "probed, and no probe reads are in "
                               "this history.",
                }
                ev = self.engine.commit_events(
                    [("BOUNDARY_PROBE", SYSTEM_ACTOR, [], payload)])[0]
                return _ok({"event_seq": ev["event_seq"]})
            if op == "shutdown":
                threading.Timer(0.1, self._stopped.set).start()
                return _ok({"shutting_down": True})
        except HarnessRefusal as exc:
            return _err("refusal", str(exc))
        except Exception as exc:
            return _err("internal", f"{type(exc).__name__}: {exc}")
        return _err("unknown_op", f"no such admin operation {op!r}")

    # -- serving ---------------------------------------------------------
    def serve(self):
        service = self

        class Handler(socketserver.StreamRequestHandler):
            admin = False

            def handle(self):
                line = self.rfile.readline(1 << 21)
                if not line:
                    return
                try:
                    req = json.loads(line.decode("utf-8"))
                except Exception:
                    resp = _err("transport", "request was not JSON")
                else:
                    resp = (service.dispatch_admin(req) if self.admin
                            else service.dispatch_data(req))
                self.wfile.write((json.dumps(resp) + "\n").encode("utf-8"))

        class AdminHandler(Handler):
            admin = True

        class Server(socketserver.ThreadingUnixStreamServer):
            daemon_threads = True
            allow_reuse_address = True

        for path in (self.data_sock, self.admin_sock):
            if os.path.exists(path):
                os.unlink(path)
        data_server = Server(self.data_sock, Handler)
        os.chmod(self.data_sock, 0o777)
        admin_server = Server(self.admin_sock, AdminHandler)
        threads = [
            threading.Thread(target=data_server.serve_forever,
                             daemon=True),
            threading.Thread(target=admin_server.serve_forever,
                             daemon=True),
        ]
        for t in threads:
            t.start()
        self._stopped.wait()
        data_server.shutdown()
        admin_server.shutdown()
        data_server.server_close()
        admin_server.server_close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-dir", required=True)
    args = parser.parse_args()
    FabricService(args.runtime_dir).serve()


if __name__ == "__main__":
    main()
