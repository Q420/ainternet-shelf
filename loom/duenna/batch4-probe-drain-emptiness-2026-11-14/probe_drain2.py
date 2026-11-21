#!/usr/bin/env python3
"""Probe: can shutdown(SHUT_RD) purge an AF_UNIX SOCK_SEQPACKET
receive queue — and does purging (vs the Correction-1 recv-drain)
preserve the final STATUS for a non-concurrent reader against
adversarial residue (many plain zeros, an ancillary record, a
data record; and a >1024-record queue)?

Part 1 (in-process): purge semantics — queued data record must
NOT be receivable after SHUT_RD; a queued pipe fd must be closed
by the kernel (write to the held write-end raises EPIPE); the
send direction must be unaffected.
Part 2 (forked closer, non-concurrent reader): STATUS survival
per variant: plain / recvdrain (Correction-1 algorithm) / purge /
purge+drain.
Part 3: 1500-record queue: purge vs recvdrain STATUS survival.
"""
import os, socket, sys, time

def anc_recv(sock):
    data, anc, flags, _ = sock.recvmsg(64, socket.CMSG_SPACE(4 * 4))
    fds = []
    for lvl, typ, dat in anc:
        if lvl == socket.SOL_SOCKET and typ == socket.SCM_RIGHTS:
            import array
            a = array.array("i"); a.frombytes(dat)
            fds = list(a)
    return data, fds

print("== Part 1: SHUT_RD purge semantics (in-process) ==")
s1, s2 = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
r, w = os.pipe()
s2.send(b"HELLO")
s2.send(b"")
s2.send(b"")
s2.sendmsg(b"", [], )  # plain zero
s2.sendmsg(b"", [(socket.SOL_SOCKET, socket.SCM_RIGHTS,
                  __import__("array").array("i", [r]))])
os.close(r)
s1.shutdown(socket.SHUT_RD)
got = []
s1.settimeout(0.5)
for _ in range(3):
    try:
        got.append(s1.recv(64))
    except socket.timeout:
        got.append(b"<timeout>")
print("recvs after SHUT_RD:", got, "-> data record purged:", got[0] == b"")
try:
    os.write(w, b"x")
    print("pipe write: SUCCEEDED -> queued fd NOT closed by kernel")
except BrokenPipeError:
    print("pipe write: EPIPE -> queued fd WAS closed by the kernel on purge")
os.close(w)
s1.send(b"STATUS!")
print("send after SHUT_RD, peer received:", s2.recv(64))
s1.close(); s2.close()

def run_variant(variant, residue_zeros=3, big=False, trials=20):
    """Forked closer sends STATUS, queues residue, acts per
    variant, exits. Parent waits for full exit, THEN reads."""
    lost = 0
    for _ in range(trials):
        a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        pid = os.fork()
        if pid == 0:
            a.close()
            try:
                b.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 16777216)
            except OSError:
                pass
            b.send(b"\x07STATUS-word")
            n = 1500 if big else residue_zeros
            b.setblocking(False)
            deadline = time.time() + 5
            sent = 0
            while sent < n:
                try:
                    b.send(b"")
                    sent += 1
                except BlockingIOError:
                    if time.time() > deadline:
                        break
                    time.sleep(0.01)
            if big and _ == 0:
                os.write(2, f"[big queue: {sent} zero records queued]\n".encode())
            b.setblocking(True)
            rr, ww = os.pipe()
            b.sendmsg(b"", [(socket.SOL_SOCKET, socket.SCM_RIGHTS,
                             __import__("array").array("i", [rr]))])
            os.close(rr); os.close(ww)
            b.send(b"XYZ")
            b.shutdown(socket.SHUT_WR)
            if variant == "plain":
                pass
            elif variant == "recvdrain":
                # Correction-1 algorithm: recv until EAGAIN, or a
                # zero whose closure triple says empty.
                import fcntl
                b.setblocking(False)
                for _i in range(1024):
                    try:
                        d, fds = anc_recv(b)
                    except BlockingIOError:
                        break
                    except OSError:
                        break
                    for f in fds: os.close(f)
                    if d == b"":
                        # bytes queued?
                        avail = fcntl.ioctl(b.fileno(), 0x541B,
                                            __import__("struct").pack("i", 0))
                        import struct as _s
                        if _s.unpack("i", avail)[0] == 0:
                            break
            elif variant == "purge":
                b.shutdown(socket.SHUT_RD)
            elif variant == "purge+drain":
                b.shutdown(socket.SHUT_RD)
                b.setblocking(False)
                for _i in range(64):
                    try:
                        d, fds = anc_recv(b)
                    except OSError:
                        break
                    for f in fds: os.close(f)
            os._exit(0)
        b.close()
        os.waitpid(pid, 0)
        a.settimeout(0.5)
        found = False
        try:
            while True:
                d = a.recv(64)
                if d == b"":
                    break
                if d.startswith(b"\x07STATUS"):
                    found = True
        except (socket.timeout, ConnectionResetError):
            pass
        if not found:
            lost += 1
        a.close()
    return lost

print("== Part 2: STATUS survival, residue = 3 zeros + rights + data, 20 trials ==")
for v in ("plain", "recvdrain", "purge", "purge+drain"):
    print(f"variant {v}: lost {run_variant(v)}/20")

print("== Part 3: 1500-record queue, 10 trials ==")
for v in ("recvdrain", "purge"):
    print(f"variant {v}: lost {run_variant(v, big=True, trials=10)}/10")
print("PROBE DONE")
