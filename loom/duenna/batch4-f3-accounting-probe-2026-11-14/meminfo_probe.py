#!/usr/bin/env python3
"""Receive-memory accounting probe (Alex's F-3 design candidate).

Question: on this kernel, does getsockopt(SOL_SOCKET, SO_MEMINFO)
field SK_MEMINFO_RMEM_ALLOC [0] read non-zero for EVERY queued
record on an AF_UNIX SOCK_SEQPACKET socket — zero-length records
included — and exactly zero once the last real record is consumed,
with phantom EOF receives contributing nothing?

Accounting is read with ctypes libc getsockopt so optlen, short
buffers and failing calls are all observable.
"""
import array, ctypes, os, platform, socket

libc = ctypes.CDLL("libc.so.6", use_errno=True)
SOL_SOCKET = 1
SO_MEMINFO = 55

def meminfo(fd, nwords=16, optname=SO_MEMINFO):
    buf = (ctypes.c_uint32 * nwords)()
    ln = ctypes.c_uint32(nwords * 4)
    rc = libc.getsockopt(fd, SOL_SOCKET, optname,
                         ctypes.byref(buf), ctypes.byref(ln))
    err = ctypes.get_errno()
    return rc, err, ln.value, list(buf)

def rmem(fd):
    rc, err, ln, vals = meminfo(fd)
    assert rc == 0, f"getsockopt failed rc={rc} errno={err}"
    return vals[0], ln, vals

print("kernel:", platform.uname().release, platform.uname().version)
print("machine:", platform.uname().machine)

def pair():
    r, s = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    return r, s

def anc_recv(sock):
    data, anc, flags, _ = sock.recvmsg(64, socket.CMSG_SPACE(4 * 4))
    fds = []
    for lvl, typ, dat in anc:
        if lvl == socket.SOL_SOCKET and typ == socket.SCM_RIGHTS:
            a = array.array("i"); a.frombytes(dat); fds = list(a)
    return data, fds

print("\n== baseline: empty socket, peer open ==")
r, s = pair()
v, ln, allv = rmem(r.fileno())
print(f"rmem_alloc={v} optlen={ln} meminfo={allv}")
r.close(); s.close()

print("\n== empty CLOSED socket: phantom EOF, then accounting ==")
r, s = pair()
s.shutdown(socket.SHUT_WR)
print("phantom recv ->", r.recv(64))
v, ln, _ = rmem(r.fileno())
print(f"rmem_alloc after phantom = {v} (must be 0)")
r.close(); s.close()

print("\n== plain zeros: accounting after EACH receive ==")
r, s = pair()
for _ in range(5): s.send(b"")
s.shutdown(socket.SHUT_WR)
seq = []
v, _, _ = rmem(r.fileno()); seq.append(("queued 5", v))
for i in range(5):
    d, fds = anc_recv(r)
    v, _, _ = rmem(r.fileno()); seq.append((f"after recv {i+1} ({d!r})", v))
d, fds = anc_recv(r)  # phantom
v, _, _ = rmem(r.fileno()); seq.append(("after phantom", v))
for k, v in seq: print(f"  {k}: rmem_alloc={v}")
r.close(); s.close()

print("\n== ancillary zero: accounting + descriptor ==")
r, s = pair()
pr, pw = os.pipe()
s.sendmsg(b"", [(socket.SOL_SOCKET, socket.SCM_RIGHTS,
                 array.array("i", [pr]))])
os.close(pr)
v, _, _ = rmem(r.fileno()); print(f"  queued anc-zero: rmem_alloc={v}")
d, fds = anc_recv(r)
print(f"  received: data={d!r} fds={fds}")
for f in fds: os.close(f)
v, _, _ = rmem(r.fileno()); print(f"  after consume+close: rmem_alloc={v}")
os.close(pw)
r.close(); s.close()

print("\n== mixed: data + trailing zeros, accounting each step ==")
r, s = pair()
s.send(b"XYZ")
for _ in range(3): s.send(b"")
s.shutdown(socket.SHUT_WR)
v, _, _ = rmem(r.fileno()); print(f"  queued [data,Z,Z,Z]: rmem_alloc={v}")
for i in range(4):
    d, fds = anc_recv(r)
    v, _, _ = rmem(r.fileno()); print(f"  after recv {i+1} ({d!r}): rmem_alloc={v}")
r.close(); s.close()

print("\n== 1500 zeros: sampled accounting ==")
r, s = pair()
s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 16777216)
for _ in range(1500): s.send(b"")
s.shutdown(socket.SHUT_WR)
v, _, _ = rmem(r.fileno()); print(f"  queued 1500: rmem_alloc={v}")
for target in (500, 1000, 1499, 1500):
    done = 0
    # consume up to target cumulative
    cur = 1500 - (1500 - target)  # placeholder, tracked below
    break
consumed = 0
marks = {500, 1000, 1499, 1500}
while consumed < 1500:
    d, fds = anc_recv(r)
    consumed += 1
    if consumed in marks:
        v, _, _ = rmem(r.fileno())
        print(f"  after {consumed} consumed: rmem_alloc={v}")
r.close(); s.close()

print("\n== failure + short-buffer behaviour ==")
r, s = pair()
s.send(b"")
rc, err, ln, vals = meminfo(r.fileno(), nwords=1)
print(f"  short buffer (1 word): rc={rc} errno={err} optlen={ln} vals={vals}")
rc, err, ln, vals = meminfo(r.fileno(), optname=9999)
print(f"  bad optname 9999: rc={rc} errno={err} (ENOPROTOOPT=92)")
rc, err, ln, vals = meminfo(r.fileno(), nwords=8)
print(f"  8-word buffer: rc={rc} errno={err} optlen={ln} rmem={vals[0]}")
r.close(); s.close()
print("\nPROBE DONE")
