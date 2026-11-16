#!/usr/bin/env python3
"""Watchdog live runner — one scheduler pass over the live pool.

Armed by the owner's tap, 2026-11-15 17:32 MST. Assembles the
accepted stages per seat (registry -> ledger -> detector ->
scheduler -> wake) on the live layout:

  watchdog-live/registry.json       the job registry (owner's
                                    file; jobs are registered
                                    here when an assignment is
                                    sent with its marker)
  watchdog-live/<seat>/             per-seat registry pin state
                                    and ledger state
  spool/watchdog-wake-outbox.jsonl  the wake outbox (the wake
                                    module's DEFAULT_OUTBOX —
                                    the checker hook reads here)
  spool/watchdog-wake-state.json    the wake state cache (A1:
                                    a cache, never authority)

Owner §11 values (watchdog/WATCHDOG-S11-VALUES.md on the
shelf): alert_age 3600, cooldown 600, stale_interval 300,
buffer 25, idle_after_s 3660 — the last is wake-layer config
only (A5: no code default; the owner value is wired here).

The judge is the accepted NvidiaJudge; its credential comes
only through the connector's secure route (the
dynamic_credentials helper, put on sys.path below). With
--stub, a StubJudge that always answers NO is used instead:
no network, for dry verification of the wiring.

v1 limitation: jobs are grouped by seat — each seat stack
loads only its own jobs, so a job's dependencies must live
on the same seat. Cross-seat dependency chains are not
registered in v1.

Usage:
  watchdog_live.py pass [--stub] [--home DIR] [--events DIR]
                        [--outbox PATH] [--wake-state PATH]

Prints one JSON summary. Exit 0 when the pass ran (an idle
pass with no jobs is a success); non-zero only when the pass
itself could not run.
"""

import argparse
import json
import os
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
# The connector framework's credential-surrogate helper — the
# ONLY credential route for the judge (contract §11, D5).
sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")

import watchdog_detector as wd
import watchdog_ledger as wl
import watchdog_scheduler as ws
import watchdog_wake as ww

OWNER_CONFIG = {"alert_age_s": 3600,
                "cooldown_default_s": 600,
                "stale_interval_s": 300}
DETECTOR_CONFIG = dict(OWNER_CONFIG, buffer_size=25)
WAKE_CONFIG = {"idle_after_s": 3660}
DEFAULT_MODEL = "nvidia/llama-3.1-nemotron-ultra-253b-v1"


def seat_pool_files(events_dir):
    """Map seat_id -> pool file, from each file's first event."""
    out = {}
    if not os.path.isdir(events_dir):
        return out
    for name in sorted(os.listdir(events_dir)):
        if not name.endswith(".jsonl"):
            continue
        path = os.path.join(events_dir, name)
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        seat = json.loads(line).get("seat_id")
                        if seat:
                            out[seat] = path
                        break
        except (OSError, ValueError):
            continue
    return out


def _write_if_changed(path, obj):
    text = json.dumps(obj, indent=1, sort_keys=True)
    try:
        with open(path) as f:
            if f.read() == text:
                return
    except OSError:
        pass
    with open(path, "w") as f:
        f.write(text)


def run_pass(home, events_dir, outbox_path, wake_state_path,
             stub=False):
    registry_path = os.path.join(home, "registry.json")
    if os.path.exists(registry_path):
        with open(registry_path) as f:
            registry_doc = json.load(f)
    else:
        registry_doc = {"jobs": []}
    jobs = registry_doc.get("jobs", [])
    pools = seat_pool_files(events_dir)
    if stub == "yes":
        judge = wd.StubJudge(responder=lambda p, c: "YES")
    elif stub:
        judge = wd.StubJudge()
    else:
        judge = wd.NvidiaJudge(model=DEFAULT_MODEL)
    now = time.time()
    summary = {"jobs_total": len(jobs), "seats": {},
               "outbox_before": len(ww.Outbox(outbox_path).records())}
    by_seat = {}
    for job in jobs:
        by_seat.setdefault(job["seat_id"], []).append(job)
    for seat, seat_jobs in sorted(by_seat.items()):
        seat_dir = os.path.join(home, seat)
        os.makedirs(seat_dir, exist_ok=True)
        seat_registry = os.path.join(seat_dir, "registry.json")
        _write_if_changed(seat_registry, {"jobs": seat_jobs})
        reg = wl.load_registry(
            seat_registry,
            state_dir=os.path.join(seat_dir, "reg-state"))
        led = wl.Ledger(os.path.join(seat_dir, "ledger"),
                        dict(OWNER_CONFIG), registry=reg)
        pool_path = pools.get(seat)
        if pool_path is None:
            summary["seats"][seat] = {
                "error": "no pool file for seat"}
            continue
        det = wd.Detector(reg, led, wd.PoolReader(pool_path),
                          judge, dict(DETECTOR_CONFIG))
        sch = ws.Scheduler(reg, led, det)
        report = sch.run_pass(now=now)
        wake = ww.WakeLayer(outbox_path, wake_state_path,
                            ledger=led, config=dict(WAKE_CONFIG))
        wake.consume(report, now=now)
        summary["seats"][seat] = {
            "jobs": [{"job_id": e["job_id"],
                      "outcome": e.get("outcome"),
                      "reason": e.get("reason")}
                     for e in report["jobs"]],
            "pending": len(report.get("pending", [])),
            "alerts": len(report.get("alerts", []))}
    summary["outbox_after"] = len(
        ww.Outbox(outbox_path).records())
    summary["new_outbox_records"] = (
        summary["outbox_after"] - summary["outbox_before"])
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["pass"])
    ap.add_argument("--stub", nargs="?", const="no",
                    choices=["no", "yes"],
                    help="offline judge: 'no' (default stub) or "
                         "'yes' (smoke tests); omit for the "
                         "live NvidiaJudge")
    ap.add_argument("--home",
                    default=os.path.join(BASE, "watchdog-live"))
    ap.add_argument("--events",
                    default=os.path.join(BASE, "events"))
    ap.add_argument("--outbox", default=ww.DEFAULT_OUTBOX)
    ap.add_argument("--wake-state", default=ww.DEFAULT_STATE)
    args = ap.parse_args(argv)
    summary = run_pass(args.home, args.events, args.outbox,
                       args.wake_state, stub=args.stub)
    summary["stub"] = args.stub
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
