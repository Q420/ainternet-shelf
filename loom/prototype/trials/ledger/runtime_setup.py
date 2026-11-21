#!/usr/bin/env python3
"""Build the trials ledger runtime on tmpfs (the workspace filesystem denies
traversal to the boundary OS identities, so — exactly as with the Stage 2
boundary runtime — the running service lives under /tmp/loom-trials-runtime
and is rebuilt from this tree). The ledger service runs as loomledger; the
ground-truth store is held by loomgt; producing components run as loomagent
and reach the sequence only through the service socket."""
import os, shutil, subprocess, sys, time

RT = "/tmp/loom-trials-runtime"
SRC = os.path.dirname(os.path.abspath(__file__))

def main():
    for d, owner, mode in [(RT + "/ledger-store", "loomledger", 0o700),
                           (RT + "/gt-store", "loomgt", 0o700),
                           (RT + "/sock", "loomledger", 0o755),
                           (RT + "/work", None, 0o770)]:
        os.makedirs(d, exist_ok=True)
        if owner: subprocess.run(["chown", f"{owner}:{owner}", d], check=True)
        os.chmod(d, mode)
    # service copy, owned by loomledger
    dst = RT + "/ledger-store/ledger_service.py"
    shutil.copy(SRC + "/ledger_service.py", dst)
    subprocess.run(["chown", "loomledger:loomledger", dst], check=True)
    os.chmod(dst, 0o700)
    # (re)start the service as loomledger
    subprocess.run(["pkill", "-f", "loom-trials-runtime/ledger-store/ledger_service.py"],
                   capture_output=True)
    time.sleep(0.5)
    log = open(RT + "/work/ledger-service.log", "w")
    subprocess.Popen(["runuser", "-u", "loomledger", "--", "python3", dst],
                     stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    for _ in range(40):
        if os.path.exists(RT + "/sock/ledger.sock"): break
        time.sleep(0.25)
    print("ledger service socket:", os.path.exists(RT + "/sock/ledger.sock"))

if __name__ == "__main__":
    main()
