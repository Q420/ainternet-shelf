#!/usr/bin/env python3
"""Drain Bench — the standing instrument for teardown-drain questions.

Fixed topology (can never be transcribed wrong again):
  parent = SUPERVISOR role. It queues the named residue INTO the
  child's receive queue BEFORE the fork, then reads the final
  STATUS only AFTER the child has fully exited (the F-3
  non-concurrent reader shape).
  child  = LAUNCHER role. It sends the STATUS word on its end,
  performs the plugged exit behaviour, and exits.

Residue shapes are a named catalogue. Peer state is part of the
case: "open" (supervisor alive, socket open) or "closed"
(supervisor shut its write side after queueing — the stub/NQ5'
shape). Exit behaviours are pluggable functions of the child fd.

The bench sizes its own buffers, fills queues non-blocking with a
deadline and reports the count actually queued (a shape that
cannot form is reported, never silently shrunk), prints every
case as it completes, and sanity-checks itself first: empty
residue + plain exit must survive 10/10 or the bench is broken.
"""
import array, fcntl, os, select, socket, struct, sys, time

STATUS = b"\x07STATUS-word"
TRIALS = 10

# ---------- residue catalogue: functions of the parent end ------
def _zeros(a, n):
    for _ in range(n):
        a.send(b"")

def _anc(a):
    r, w = os.pipe()
    a.sendmsg(b"", [(socket.SOL_SOCKET, socket.SCM_RIGHTS,
                     array.array("i", [r]))])
    os.close(r); os.close(w)

def _data(a):
    a.send(b"XYZ")

def _big(a, n=1500):
    a.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 16777216)
    a.setblocking(False)
    deadline = time.time() + 5
    sent = 0
    while sent < n:
        try:
            a.send(b""); sent += 1
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
    "anc-one":         lambda a: _anc(a) or 1,
    "data-one":        lambda a: _data(a) or 1,
    "nq5":             lambda a: (_zeros(a, 2), _anc(a), 3)[2],
    "mixed-data-last": lambda a: (_zeros(a, 3), _anc(a), _data(a), 5)[3],
    "trailing-zeros":  lambda a: (_anc(a), _data(a), _zeros(a, 3), 5)[3],
    "queue-1500":      lambda a: _big(a),
}

# ---------- exit behaviours: functions of the child end ---------
def _recv(b):
    data, anc, flags, _ = b.recvmsg(64, socket.CMSG_SPACE(4 * 4))
    fds = []
    for lvl, typ, dat in anc:
        if lvl == socket.SOL_SOCKET and typ == socket.SCM_RIGHTS:
            arr = array.array("i"); arr.frombytes(dat); fds = list(arr)
    return data, fds, flags

def beh_plain(b):
    return 0

def beh_drain_corr1(b):
    """Faithful port of the Correction-1 teardown_drain: nonblocking
    receive loop, cap 1024; after a zero without ancillary, stop if
    the closure triple holds (FIONREAD==0, RDHUP/HUP on a zero poll,
    head peek with control buffer shows no ancillary / no CTRUNC)."""
    b.setblocking(False)
    consumed = 0
    while consumed < 1024:
        try:
            d, fds, _fl = _recv(b)
        except (BlockingIOError, OSError):
            break
        consumed += 1
        for f in fds: os.close(f)
        if d == b"" and not fds:
            try:
                avail = struct.unpack("i", fcntl.ioctl(
                    b.fileno(), 0x541B, struct.pack("i", 0)))[0]
            except OSError:
                break
            if avail != 0: continue
            p = select.poll(); p.register(b, select.POLLIN)
            ev = dict(p.poll(0)).get(b.fileno(), 0)
            if not (ev & (0x2000 | 0x0010)):  # POLLRDHUP | POLLHUP
                continue
            try:
                _pd, panc, pflags, _ = b.recvmsg(
                    64, socket.CMSG_SPACE(4 * 4), socket.MSG_PEEK)
                for lvl, typ, dat in panc:
                    if lvl == socket.SOL_SOCKET and typ == socket.SCM_RIGHTS:
                        arr = array.array("i"); arr.frombytes(dat)
                        for f in arr: os.close(f)
                if panc or (pflags & 0x08):  # MSG_CTRUNC
                    continue
            except (BlockingIOError, OSError):
                break
            break  # closure triple held
    return consumed

def beh_drain_eagain(b):
    """Reference: consume until EAGAIN, cap 20000 (peer-open proof;
    in the peer-closed state it burns the cap on phantom zeros —
    the consumed count makes the waste visible)."""
    b.setblocking(False)
    consumed = 0
    while consumed < 20000:
        try:
            d, fds, _fl = _recv(b)
        except BlockingIOError:
            break
        except OSError:
            break
        consumed += 1
        for f in fds: os.close(f)
    return consumed

BEHAVIOURS = {
    "plain": beh_plain,
    "drain-corr1": beh_drain_corr1,
    "drain-eagain": beh_drain_eagain,
}

# ---------- one case ---------------------------------------------
def run_case(shape, peer_state, behaviour):
    lost = 0
    consumed_total = 0
    formed = None
    for _ in range(TRIALS):
        a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        n = SHAPES[shape](a)
        if formed is None: formed = n
        if peer_state == "closed":
            a.shutdown(socket.SHUT_WR)
        rp, wp = os.pipe()
        pid = os.fork()
        if pid == 0:
            a.close(); os.close(rp)
            b.send(STATUS)
            consumed = BEHAVIOURS[behaviour](b)
            os.write(wp, str(consumed).encode())
            os._exit(0)
        os.close(wp)
        b.close()
        os.waitpid(pid, 0)
        rep = os.read(rp, 16).decode()
        os.close(rp)
        consumed_total += int(rep) if rep else 0
        a.settimeout(0.5)
        found = False
        try:
            while True:
                d = a.recv(64)
                if d == b"": break
                if d.startswith(b"\x07STATUS"): found = True
        except (socket.timeout, ConnectionResetError):
            pass
        if not found: lost += 1
        a.close()
    return formed, lost, consumed_total // TRIALS

def main():
    only = sys.argv[1:] or None
    print("BENCH SANITY: empty/open/plain must be 0 lost", flush=True)
    _f, lost, _c = run_case("empty", "open", "plain")
    print(f"  sanity: {lost} lost /{TRIALS}", flush=True)
    if lost != 0:
        print("BENCH BROKEN — topology or reader discipline wrong. Stop.")
        return
    print(f"{'shape':<18}{'peer':<8}{'behaviour':<14}{'queued':<8}"
          f"{'lost':<10}{'avg consumed'}", flush=True)
    for shape in SHAPES:
        for peer in ("open", "closed"):
            for beh in BEHAVIOURS:
                if only and beh not in only: continue
                formed, lost, cons = run_case(shape, peer, beh)
                print(f"{shape:<18}{peer:<8}{beh:<14}{formed:<8}"
                      f"{lost}/{TRIALS:<8}{cons}", flush=True)
    print("BENCH DONE", flush=True)

if __name__ == "__main__":
    main()
