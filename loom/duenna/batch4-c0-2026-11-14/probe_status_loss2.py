#!/usr/bin/env python3
"""Discriminating probe for the STATUS-loss mechanism.
L is a forked child (the launcher's position): it holds one
end of a SEQPACKET socketpair; S (parent, the supervisor's
position) sends two plain zero records + one zero-length
fd-carrying record and shuts down its write side BEFORE L
reads anything. L reads ONE zero, peeks (plain zero head),
classifies closure, sends a 10-byte STATUS, then tears down
per variant and _exit(0)s. S waits until L has fully exited,
THEN reads: did STATUS survive? 30 iterations per variant."""
import os, socket, struct, sys, time

N = 20
STATUS = b"\x07\x00\x00\x00\x92\xe7\x00\x00\x47\x00"

def child(l_sock, variant):
    try:
        # read one zero record
        data, anc, flags, _ = l_sock.recvmsg(64, socket.CMSG_SPACE(16))
        # closure peek at head (plain zero expected)
        data, anc, flags, _ = l_sock.recvmsg(64, socket.CMSG_SPACE(16),
                                             socket.MSG_PEEK)
        for lv, tp, dat in anc:
            if tp == socket.SCM_RIGHTS:
                for fd in struct.unpack("i" * (len(dat) // 4), dat):
                    os.close(fd)
        l_sock.send(STATUS)
        if variant == "shut_rd":
            l_sock.shutdown(socket.SHUT_RD)
        elif variant == "shut_rdwr":
            l_sock.shutdown(socket.SHUT_RDWR)
        elif variant == "drain":
            l_sock.setblocking(False)
            try:
                while True:
                    d2, a2, f2, _ = l_sock.recvmsg(64, socket.CMSG_SPACE(16))
                    if not d2 and not a2:
                        break
                    for lv, tp, dat in a2:
                        if tp == socket.SCM_RIGHTS:
                            for fd in struct.unpack("i" * (len(dat) // 4), dat):
                                os.close(fd)
            except (BlockingIOError, ConnectionResetError):
                pass
            # EOF (peer shut down, queue empty) also ends the drain
        # "plain": nothing
    finally:
        os._exit(0)

def run(variant):
    lost = 0
    reset_after = 0
    for _ in range(N):
        s_sock, l_sock = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        s_sock.settimeout(2.0)
        pid = os.fork()
        if pid == 0:
            s_sock.close()
            child(l_sock, variant)
        l_sock.close()
        afd = os.open("/tmp/probe-junk", os.O_CREAT | os.O_RDWR, 0o644)
        s_sock.send(b"")
        s_sock.send(b"")
        s_sock.sendmsg([b""], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, struct.pack("i", afd))])
        os.close(afd)
        s_sock.shutdown(socket.SHUT_WR)
        os.waitpid(pid, 0)
        time.sleep(0.05)
        got = None
        try:
            data, anc, flags, _ = s_sock.recvmsg(64, socket.CMSG_SPACE(16))
            got = data
            # try a second read to note the reset
            s_sock.settimeout(0.3)
            try:
                s_sock.recvmsg(64, socket.CMSG_SPACE(16))
            except ConnectionResetError:
                reset_after += 1
        except ConnectionResetError:
            pass
        except socket.timeout:
            pass
        if got != STATUS:
            lost += 1
        s_sock.close()
    print(f"{variant}: STATUS lost {lost}/{N}, reset-after-status {reset_after}/{N}", flush=True)

for v in ("plain", "shut_rd", "drain"):
    run(v)
