#!/usr/bin/env python3
"""Bench 3 — head-to-head: STATUS pipe vs dedicated STATUS socketpair.

Fixed topology, mirroring bench v2: the parent (supervisor role)
pre-queues the named residue into the child's CONTROL socket
receive queue, forks the real-C candidate child, waits for FULL
exit, and only then reads the candidate STATUS transport
(non-concurrent reader). The child never reads the control socket.

Candidates (bench3_child.c):
  pipe — STATUS on a dedicated pipe; parent assembles the fixed
         10-byte record, validates it exactly, then requires EOF.
  pair — STATUS on a dedicated SEQPACKET pair; child AUDITS its
         receive queue first (any record = supervisor-originated
         violation -> exit 44, STATUS withheld). Prevention variant:
         the parent shutdown(SHUT_WR)s its status end post-spawn.

A cell passes only if every trial yields exactly one valid STATUS
(pipe/pair main matrix) or the specified failure behaviour
(violation / writer-failure cases). One bad trial fails the cell.
"""
import os, socket, struct, sys, time, array

TRIALS = 10
CHILD = "/mnt/c/Users/ben/b4c/bench3_child"
WORD = 0x11223344

def _zeros(a, n):
    for _ in range(n): a.send(b"")
def _anc(a):
    r, w = os.pipe()
    a.sendmsg(b"", [(socket.SOL_SOCKET, socket.SCM_RIGHTS,
                     array.array("i", [r]))])
    os.close(r); os.close(w)
def _data(a): a.send(b"XYZ")
def _big(a, n=1500):
    a.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 16777216)
    a.setblocking(False)
    deadline = time.time() + 5; sent = 0
    while sent < n:
        try: a.send(b""); sent += 1
        except BlockingIOError:
            if time.time() > deadline: break
            time.sleep(0.01)
    a.setblocking(True)
    return sent

SHAPES = {
    "empty":           lambda a: 0,
    "one-zero":        lambda a: _zeros(a, 1) or 1,
    "two-zeros":       lambda a: _zeros(a, 2) or 2,
    "three-zeros":     lambda a: _zeros(a, 3) or 3,
    "five-zeros":      lambda a: _zeros(a, 5) or 5,
    "anc-one":         lambda a: _anc(a) or 1,
    "anc-three":       lambda a: (_anc(a), _anc(a), _anc(a), 3)[3],
    "data-one":        lambda a: _data(a) or 1,
    "nq5":             lambda a: (_zeros(a, 2), _anc(a), 3)[2],
    "mixed-data-last": lambda a: (_zeros(a, 3), _anc(a), _data(a), 5)[3],
    "trailing-zeros":  lambda a: (_anc(a), _data(a), _zeros(a, 3), 5)[3],
    "queue-1500":      lambda a: _big(a),
}

def expected(pid):
    return b"\x07\x00" + struct.pack("<I", pid) + struct.pack("<I", WORD)

def run_trial(shape, peer, cand, violation=None, kill_reader=False):
    """Returns one of: VALID, LOST, INVALID, EXIT:<n>, EPIPE-AT-PEER,
    VIOLATION-DETECTED, WRITEFAIL-EXPLICIT."""
    a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    SHAPES[shape](a)
    if peer == "closed":
        a.shutdown(socket.SHUT_WR)
    rp = wp = sa = sb = None
    if cand == "pipe":
        rp, wp = os.pipe()
    else:
        sa, sb = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    pid = os.fork()
    if pid == 0:
        a.close()
        os.dup2(b.fileno(), 3)
        if cand == "pipe":
            os.close(rp); os.dup2(wp, 4)
        else:
            os.dup2(sb.fileno(), 5)
        os.execl(CHILD, "bench3_child", cand)
        os._exit(127)
    b.close()
    if cand == "pipe":
        os.close(wp)
        if kill_reader:
            os.close(rp); rp = None
    else:
        sb.close()
        if violation == "V1":
            sa.shutdown(socket.SHUT_WR)
            try:
                sa.send(b"\x09FORBIDDEN")
                vres = "SEND-SUCCEEDED?!"
            except OSError:
                vres = "EPIPE-AT-PEER"
        elif violation == "V2":
            sa.send(b"\x09FORBIDDEN")
            vres = None
    _wp, status = os.waitpid(pid, 0)
    code = os.waitstatus_to_exitcode(status)
    exp = expected(pid)
    if violation == "V1":
        # Required: send failed at the peer AND the audit read the
        # EOF state as clean AND STATUS arrived exactly valid.
        if code != 0:
            return f"{vres}+AUDIT-FALSE-POSITIVE(exit={code})"
        got = sa.recv(64)
        return vres + "+VALID" if got == exp else vres + "+STATUS-BAD"
    if violation == "V2":
        if code == 44:
            return "VIOLATION-DETECTED"
        return f"NOT-DETECTED(exit={code})"
    if cand == "pipe":
        if kill_reader:
            return "WRITEFAIL-EXPLICIT" if code == 45 else f"EXIT:{code}"
        buf = b""
        while True:
            chunk = os.read(rp, 64)
            if not chunk: break
            buf += chunk
        os.close(rp)
        if code != 0: return f"EXIT:{code}"
        return "VALID" if buf == exp else ("LOST" if buf == b"" else "INVALID")
    else:
        sa.settimeout(0.5)
        try:
            got = sa.recv(64)
        except (socket.timeout, ConnectionResetError):
            got = None
        sa.close()
        a.close()
        if code != 0: return f"EXIT:{code}"
        if got is None or got == b"": return "LOST"
        return "VALID" if got == exp else "INVALID"

def run_cell(shape, peer, cand, **kw):
    results = {}
    for _ in range(TRIALS):
        r = run_trial(shape, peer, cand, **kw)
        results[r] = results.get(r, 0) + 1
    return results

def main():
    import platform
    u = platform.uname()
    print(f"BENCH3 on kernel {u.release} {u.version} {u.machine}", flush=True)
    fd0 = len(os.listdir("/proc/self/fd"))
    print("SANITY: pipe/empty/open must be 10 VALID", flush=True)
    r = run_cell("empty", "open", "pipe")
    print(f"  sanity: {r}", flush=True)
    if r.get("VALID", 0) != TRIALS:
        print("BENCH BROKEN. Stop."); return
    print(f"{'shape':<18}{'peer':<8}{'cand':<7}results", flush=True)
    for shape in SHAPES:
        for peer in ("open", "closed"):
            for cand in ("pipe", "pair"):
                r = run_cell(shape, peer, cand)
                print(f"{shape:<18}{peer:<8}{cand:<7}{r}", flush=True)
    print("VIOLATION + FAILURE CASES", flush=True)
    for shape in ("empty", "three-zeros"):
        r = run_cell(shape, "closed", "pair", violation="V1")
        print(f"V1-prevention {shape:<14}pair   {r}", flush=True)
        r = run_cell(shape, "closed", "pair", violation="V2")
        print(f"V2-audit      {shape:<14}pair   {r}", flush=True)
    r = run_cell("empty", "open", "pipe", kill_reader=True)
    print(f"writer-failure empty         pipe   {r}", flush=True)
    fd1 = len(os.listdir("/proc/self/fd"))
    print(f"parent fd count before={fd0} after={fd1}", flush=True)
    print("BENCH3 DONE", flush=True)

if __name__ == "__main__":
    main()
