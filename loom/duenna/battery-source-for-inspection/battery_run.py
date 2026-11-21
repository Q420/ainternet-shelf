#!/usr/bin/python3
"""G2 scratch-room supervisor runner (Batch 4 hazard_run.py
pattern, without the hazard): arrange the supervisor's stdio,
drop to pilot-supervisor, exec the supervisor programme
against the Batch 6 G2 scratch room only.

Usage: g2_run.py <run-id>
"""
import os
import pwd
import sys

G2 = "/srv/nemotron-pilot/batch6-g2"
RID = sys.argv[1]
sup = pwd.getpwnam("pilot-supervisor")

devnull = os.open("/dev/null", os.O_RDONLY)
os.dup2(devnull, 0)
logfd = os.open(os.path.join(G2, "logs", RID + ".stdio.log"),
                os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
os.dup2(logfd, 1)
os.dup2(logfd, 2)

os.setgroups([])
os.setgid(sup.pw_gid)
os.setuid(sup.pw_uid)
env = {"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"}
os.execve("/usr/bin/python3",
          ["/usr/bin/python3",
           os.path.join(G2, "sup", "pilot_supervisor.py"),
           "--run-id", RID,
           "--launcher", os.path.join(G2, "launcher-scratch"),
           "--runs-root", os.path.join(G2, "runs"),
           "--commitments", os.path.join(G2, "commitments"),
           "--log-dir", os.path.join(G2, "logs"),
           "--evidence-dir", os.path.join(G2, "evidence"),
           "--identity-records",
           os.path.join(G2, "sup", "identity_records.json"),
           "--watchdog", "9000"],
          env)
