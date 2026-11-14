#!/usr/bin/env python3
"""Raw mechanism probe: does closing a SEQPACKET socket with
an UNREAD record in its receive queue destroy a packet it
just sent to its peer? Variants: plain close; shutdown(WR)
then close; shutdown(RD) then close; shutdown(RDWR) then
close; drain-then-close (control). 50 iterations each.
Roles: L = the closer (launcher's position), S = reader."""
import os, socket, sys

N = 50

def run(variant):
    lost = 0
    reset = 0
    for _ in range(N):
        s_sock, l_sock = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        s_sock.settimeout(2.0)
        # S sends junk: a zero-length record carrying an fd,
        # which L never receives (the residue shape)
        afd = os.open("/tmp/probe-junk", os.O_CREAT | os.O_RDWR, 0o644)
        import struct as st
        s_sock.sendmsg([b""], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, st.pack("i", afd))])
        os.close(afd)
        # L sends its STATUS-equivalent, then tears down
        l_sock.send(b"\x07\x00STATUS!!")
        if variant == "plain":
            pass
        elif variant == "shut_wr":
            l_sock.shutdown(socket.SHUT_WR)
        elif variant == "shut_rd":
            l_sock.shutdown(socket.SHUT_RD)
        elif variant == "shut_rdwr":
            l_sock.shutdown(socket.SHUT_RDWR)
        elif variant == "drain":
            l_sock.setblocking(False)
            try:
                while True:
                    data, anc, flags, _ = l_sock.recvmsg(64, socket.CMSG_SPACE(16))
                    for lv, tp, dat in anc:
                        if tp == socket.SCM_RIGHTS:
                            for fd in st.unpack("i" * (len(dat) // 4), dat):
                                os.close(fd)
                    if not data and not anc:
                        break
            except BlockingIOError:
                pass
            l_sock.setblocking(True)
        l_sock.close()
        # S reads what it can
        got = None
        try:
            data, anc, flags, _ = s_sock.recvmsg(64, socket.CMSG_SPACE(16))
            got = data
        except ConnectionResetError:
            reset += 1
        except socket.timeout:
            pass
        if got != b"\x07\x00STATUS!!":
            lost += 1
        s_sock.close()
    print(f"{variant}: lost {lost}/{N}, reset-raises {reset}/{N}")

for v in ("plain", "shut_wr", "shut_rd", "shut_rdwr", "drain"):
    run(v)
