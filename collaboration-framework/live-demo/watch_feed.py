"""Watch-wall feed for the first-worker run (prototype, 2026-11-23).

Polls the run's record store and renders three plain-text feed
files — run.log (every event), worker.log (the worker's steps and
tool calls), status.txt (a snapshot) — pushing them to Ben's
laptop feed directory over the SSH door whenever they change, so
the tmux wall's panes move while the run is live.

Delivery route (harness fix, 2026-11-23): the panes on the laptop
hold the live files open, and an scp overwrite of a held-open
file does not reliably move what the pane shows. Each feed file
is therefore scp'd to a `.new` sibling in the feed directory,
and a placer script — itself scp'd alongside — is then run
inside the laptop's WSL (ssh laptop "wsl -d Ubuntu -- bash
/mnt/c/Users/Ben/feed-place.sh"), where a plain cp moves each
`.new` onto its live name from inside the same filesystem the
panes read. The watcher's interface and rendering are unchanged;
only the delivery route changed.

Usage: python3 live-demo/watch_feed.py [run_dir]
Exits ~2 minutes after the run's report.json appears.
"""
import json
import os
import subprocess
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

RUN_DIR = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else \
    os.path.join(ROOT, "live-demo", "first-worker")
STORE = os.path.join(RUN_DIR, "run.db")
REPORT = os.path.join(RUN_DIR, "report.json")
FEED = os.path.expanduser("~/workspace/.scratch-office/feed")
SSH_CONFIG = os.path.expanduser("~/workspace/ssh-door/ssh_config")
WORKER_TYPES = {"LOOP_ITERATION", "TOOL_REQUESTED", "TOOL_DISPATCHED",
                "TOOL_STARTED", "TOOL_OUTCOME", "CONTRIBUTION",
                "LOOP_STALLED"}

os.makedirs(FEED, exist_ok=True)
push_lock = threading.Lock()
dirty = threading.Event()

FEED_FILES = ("run.log", "worker.log", "status.txt")
LAPTOP_FEED = "C:/Users/Ben/office-feed"
PLACER_NAME = "feed-place.sh"
PLACER_LOCAL = os.path.join(FEED, PLACER_NAME)
PLACER_REMOTE = "/mnt/c/Users/Ben/feed-place.sh"
PLACER_SCRIPT = """#!/bin/bash
# Places staged feed files onto their live names. Runs inside
# the laptop's WSL, where the watch-wall panes hold the live
# files open: cp from inside replaces what the panes read,
# where an scp overwrite from outside did not reliably land.
cd /mnt/c/Users/Ben/office-feed || exit 1
for name in run.log worker.log status.txt; do
  if [ -f "$name.new" ]; then
    cp "$name.new" "$name"
    rm -f "$name.new"
  fi
done
"""


def stage_commands(files):
    """The staging route: one scp per feed file, each landing
    at its `.new` sibling in the laptop's feed directory —
    never on the live name — plus one scp carrying the placer
    script itself."""
    commands = []
    for local in files:
        name = os.path.basename(local)
        commands.append(
            ["scp", "-F", SSH_CONFIG, "-q", local,
             f"laptop:{LAPTOP_FEED}/{name}.new"])
    commands.append(
        ["scp", "-F", SSH_CONFIG, "-q", PLACER_LOCAL,
         f"laptop:{LAPTOP_FEED}/{PLACER_NAME}"])
    return commands


def place_command():
    """The placement route: run the placer inside the laptop's
    WSL, where its cp moves each staged `.new` onto the live
    name the panes hold open."""
    return ["ssh", "-F", SSH_CONFIG, "laptop",
            f"wsl -d Ubuntu -- bash {PLACER_REMOTE}"]


def push():
    if not push_lock.acquire(blocking=False):
        return
    try:
        files = [os.path.join(FEED, n) for n in FEED_FILES]
        with open(PLACER_LOCAL, "w") as fh:
            fh.write(PLACER_SCRIPT)
        for command in stage_commands(files):
            subprocess.run(command, timeout=60,
                           capture_output=True)
        subprocess.run(place_command(), timeout=60,
                       capture_output=True)
    except Exception:
        pass
    finally:
        push_lock.release()


def pusher():
    while True:
        dirty.wait(timeout=5)
        dirty.clear()
        push()


def brief(p):
    if not isinstance(p, dict):
        return ""
    bits = []
    for k in ("tool", "outcome", "iteration", "ground", "part",
              "case_id", "path"):
        if k in p:
            bits.append(f"{k}={p[k]}")
    params = p.get("parameters")
    if isinstance(params, dict) and "path" in params:
        bits.append(f"path={params['path']}")
    if "text" in p:
        bits.append("text=" + str(p["text"])[:80].replace("\n", " "))
    return " ".join(bits)[:220]


def main():
    from framework.record import FrameworkStore
    run_log = open(os.path.join(FEED, "run.log"), "a")
    worker_log = open(os.path.join(FEED, "worker.log"), "a")
    run_log.write("\n=== FIRST WORKER RUN — feed started "
                  f"{time.strftime('%H:%M:%S')} ===\n")
    run_log.flush()
    threading.Thread(target=pusher, daemon=True).start()
    dirty.set()
    last_seq = 0
    report_seen_at = None
    started = time.time()
    while True:
        events = []
        if os.path.exists(STORE):
            try:
                store = FrameworkStore(STORE)
                events = store.all_events()
            except Exception:
                events = []
        new = [e for e in events if e["event_seq"] > last_seq]
        for e in new:
            last_seq = e["event_seq"]
            line = (f"#{e['event_seq']} {e['type']} "
                    f"({e['actor']}) {brief(e['payload'])}\n")
            run_log.write(line)
            if e["type"] in WORKER_TYPES:
                worker_log.write(line)
        iters = sum(1 for e in events if e["type"] == "LOOP_ITERATION")
        disps = [e for e in events if e["type"] == "TOOL_DISPATCHED"]
        outs = [e for e in events if e["type"] == "TOOL_OUTCOME"]
        brief_path = os.path.join(RUN_DIR, "sandbox", "brief.md")
        phase = "waiting for the run to start"
        if events:
            phase = "RUNNING"
        outcome_line = ""
        if os.path.exists(REPORT):
            if report_seen_at is None:
                report_seen_at = time.time()
                try:
                    rep = json.load(open(REPORT))
                    res = rep.get("loop_result") or {}
                    outcome_line = (f"outcome: {res.get('outcome')} "
                                    f"ground: {res.get('ground')}")
                except Exception:
                    outcome_line = "report written"
                run_log.write(f"=== RUN FINISHED — {outcome_line} "
                              "===\n")
                worker_log.write(f"=== RUN FINISHED — "
                                 f"{outcome_line} ===\n")
            phase = "FINISHED"
        status = (
            f"FIRST WORKER RUN — {phase}\n"
            f"elapsed: {int(time.time() - started)}s\n"
            f"events in the record: {len(events)}\n"
            f"worker steps: {iters} of 12\n"
            f"tool dispatches: {len(disps)}   outcomes: {len(outs)}\n"
            f"brief.md written: "
            f"{'YES' if os.path.exists(brief_path) else 'not yet'}\n"
            f"{outcome_line}\n")
        with open(os.path.join(FEED, "status.txt"), "w") as fh:
            fh.write(status)
        run_log.flush()
        worker_log.flush()
        dirty.set()
        if report_seen_at and time.time() - report_seen_at > 120:
            break
        time.sleep(2)


if __name__ == "__main__":
    main()
