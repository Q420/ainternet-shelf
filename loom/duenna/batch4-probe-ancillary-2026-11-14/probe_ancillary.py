#!/usr/bin/env python3
"""probe_ancillary.py — Alex's Rev 7 question: can a ZERO-LENGTH record
carrying SCM_RIGHTS ancillary data exist on AF_UNIX SOCK_SEQPACKET, and
if so, what do the closure observations (FIONREAD / poll / MSG_PEEK)
report while it is queued behind a pending zero?

Sequences:
  A  possibility, channel open: [Z+rights]
  B  Alex's sequence: [Z, Z+rights, shutdown], step by step
  C  deep sequence: [Z, Z, Z+rights, shutdown] (ancillary behind a
     plain zero at check time)
  D  peek semantics on an ancillary record (repeat peek, fd accounting)
  E  peek / nonblocking-recv results on an EMPTY queue, peer open vs
     peer shutdown (drain-termination evidence)
"""
import array
import fcntl
import os
import select
import socket
import sys

FIONREAD = 0x541B
ANCBUF = socket.CMSG_SPACE(64)


def fionread(s):
    b = array.array("i", [0])
    fcntl.ioctl(s.fileno(), FIONREAD, b, True)
    return b[0]


def poll_state(s):
    p = select.poll()
    p.register(s, select.POLLIN | select.POLLRDHUP)
    ev = dict(p.poll(0))
    r = ev.get(s.fileno(), 0)
    names = []
    for bit, name in ((select.POLLIN, "POLLIN"), (select.POLLRDHUP, "POLLRDHUP"),
                      (select.POLLHUP, "POLLHUP"), (select.POLLERR, "POLLERR")):
        if r & bit:
            names.append(name)
    return "|".join(names) if names else "none"


def anc_summary(anc):
    out = []
    for level, typ, data in anc:
        if level == socket.SOL_SOCKET and typ == socket.SCM_RIGHTS:
            fds = array.array("i")
            fds.frombytes(data[: len(data) - (len(data) % 4)])
            out.append(f"SCM_RIGHTS{fds.tolist()}")
        else:
            out.append(f"lvl{level}/typ{typ}({len(data)}B)")
    return ",".join(out) if out else "no-ancillary"


def peek_full(s):
    try:
        data, anc, flags, _ = s.recvmsg(4096, ANCBUF, socket.MSG_PEEK | socket.MSG_DONTWAIT)
        ctrunc = " MSG_CTRUNC" if (flags & socket.MSG_CTRUNC) else ""
        return f"n={len(data)} anc=[{anc_summary(anc)}] flags={flags}{ctrunc}"
    except BlockingIOError:
        return "EAGAIN"
    except OSError as e:
        return f"ERR errno={e.errno}"


def recv_full(s):
    try:
        data, anc, flags, _ = s.recvmsg(4096, ANCBUF, socket.MSG_DONTWAIT)
        ctrunc = " MSG_CTRUNC" if (flags & socket.MSG_CTRUNC) else ""
        return f"n={len(data)} anc=[{anc_summary(anc)}] flags={flags}{ctrunc}", anc
    except BlockingIOError:
        return "EAGAIN", None
    except OSError as e:
        return f"ERR errno={e.errno}", None


def state(s, label):
    print(f"  {label}: FIONREAD={fionread(s)} POLL={poll_state(s)} PEEK={peek_full(s)}")


def send_zero_rights(s, fd):
    s.sendmsg([b""], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array("i", [fd]))])


def fd_count():
    return len(os.listdir("/proc/self/fd"))


print(f"python {sys.version.split()[0]}")
print(f"kernel {os.uname().sysname} {os.uname().release} {os.uname().machine}")
print()

# --- A: possibility, channel open -------------------------------------
print("== A [Z+rights] channel OPEN ==")
a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
r, w = os.pipe()
n_sent = send_zero_rights(b, r)
print(f"  sendmsg zero+rights returned: {n_sent}")
state(a, "after send")
res, anc = recv_full(a)
print(f"  recv#1: {res}")
got = None
if anc:
    for level, typ, data in anc:
        if typ == socket.SCM_RIGHTS:
            got = array.array("i")
            got.frombytes(data[:4])
if got:
    os.write(w, b"K")
    print(f"  received fd {got[0]} readable: {os.read(got[0], 1)!r}")
    os.close(got[0])
os.close(r); os.close(w); a.close(); b.close()
print()

# --- B: Alex's sequence ------------------------------------------------
print("== B [Z, Z+rights, shutdown] ==")
a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
r, w = os.pipe()
b.send(b"")
send_zero_rights(b, r)
b.shutdown(socket.SHUT_WR)
state(a, "before any recv")
for i in range(3):
    res, anc = recv_full(a)
    print(f"  recv#{i + 1}: {res}")
    if anc:
        for level, typ, data in anc:
            if typ == socket.SCM_RIGHTS:
                fds = array.array("i"); fds.frombytes(data[:4])
                os.close(fds[0])
                print(f"    (delivered fd {fds[0]} closed by receiver)")
    state(a, f"after recv#{i + 1}")
os.close(r); os.close(w); a.close(); b.close()
print()

# --- C: deep sequence ---------------------------------------------------
print("== C [Z, Z, Z+rights, shutdown] ==")
a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
r, w = os.pipe()
b.send(b"")
b.send(b"")
send_zero_rights(b, r)
b.shutdown(socket.SHUT_WR)
state(a, "before any recv")
for i in range(4):
    res, anc = recv_full(a)
    print(f"  recv#{i + 1}: {res}")
    if anc:
        for level, typ, data in anc:
            if typ == socket.SCM_RIGHTS:
                fds = array.array("i"); fds.frombytes(data[:4])
                os.close(fds[0])
                print(f"    (delivered fd {fds[0]} closed by receiver)")
    state(a, f"after recv#{i + 1}")
os.close(r); os.close(w); a.close(); b.close()
print()

# --- D: peek semantics on an ancillary record ---------------------------
print("== D peek on [Z+rights], channel OPEN ==")
a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
r, w = os.pipe()
send_zero_rights(b, r)
base = fd_count()
print(f"  fd_count before peeks: {base}")
print(f"  peek#1: {peek_full(a)}")
print(f"  peek#2: {peek_full(a)}")
print(f"  fd_count after peeks: {fd_count()} (peek installs nothing if unchanged)")
res, anc = recv_full(a)
print(f"  recv after peeks: {res}")
print(f"  fd_count after recv: {fd_count()} (rises by 1 if the fd was delivered exactly once, at recv)")
if anc:
    for level, typ, data in anc:
        if typ == socket.SCM_RIGHTS:
            fds = array.array("i"); fds.frombytes(data[:4])
            os.write(w, b"K")
            print(f"  received fd {fds[0]} readable: {os.read(fds[0], 1)!r}")
            os.close(fds[0])
os.close(r); os.close(w); a.close(); b.close()
print()

# --- E: empty-queue termination states ---------------------------------
print("== E empty queue: peek / nonblocking recv ==")
a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
print(f"  peer OPEN:     PEEK={peek_full(a)}  RECV={recv_full(a)[0]}  POLL={poll_state(a)}")
a.close(); b.close()
a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
b.shutdown(socket.SHUT_WR)
print(f"  peer SHUTDOWN: PEEK={peek_full(a)}  RECV={recv_full(a)[0]}  POLL={poll_state(a)}")
print(f"  again:         PEEK={peek_full(a)}  RECV={recv_full(a)[0]}  POLL={poll_state(a)}")
a.close(); b.close()
print()
print("probe complete")
