#!/usr/bin/env python3
"""UNIX_DIAG probe: does the netlink socket-diag path report
receive-queue accounting for an AF_UNIX SOCK_SEQPACKET socket
that counts zero-length records? Reads UNIX_DIAG_RQLEN and
UNIX_DIAG_MEMINFO for our own socket (matched by inode) at each
queue state. Cross-checks /proc/net/unix presence only.
"""
import array, os, socket, struct

NETLINK_SOCK_DIAG = 4
SOCK_DIAG_BY_FAMILY = 20
NLM_F_REQUEST = 1
NLM_F_DUMP = 0x300
UNIX_DIAG_RQLEN = 4
UNIX_DIAG_MEMINFO = 5

def diag_query(target_ino):
    nl = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW,
                       NETLINK_SOCK_DIAG)
    # unix_diag_req: family, proto, ext, pad, states, ino, show, cookie[2]
    req = struct.pack("BBBBIII II", 1, 0, 0, 0, 0xFFFFFFFF, 0,
                      (1 << UNIX_DIAG_RQLEN) | (1 << UNIX_DIAG_MEMINFO),
                      0xFFFFFFFF, 0xFFFFFFFF)
    hdr = struct.pack("IHHII", 16 + len(req), SOCK_DIAG_BY_FAMILY,
                      NLM_F_REQUEST | NLM_F_DUMP, 1, 0)
    nl.send(hdr + req)
    found = {}
    while True:
        data = nl.recv(65535)
        off = 0
        done = False
        while off + 16 <= len(data):
            mlen, mtype, _flags, _seq, _pid = struct.unpack_from(
                "IHHII", data, off)
            if mlen < 16: break
            if mtype == 3:  # NLMSG_DONE
                done = True; break
            if mtype == 2:  # NLMSG_ERROR
                err = struct.unpack_from("i", data, off + 16)[0]
                raise OSError(f"diag error {err}")
            body = off + 16
            _fam, _typ, _state, _pad, ino = struct.unpack_from(
                "BBBBI", data, body)
            if ino == target_ino:
                aoff = body + 16  # unix_diag_msg: fam/type/state/pad + ino + cookie[2] = 16
                while aoff + 4 <= off + mlen:
                    alen, atype = struct.unpack_from("HH", data, aoff)
                    if alen < 4: break
                    payload = data[aoff + 4: aoff + alen]
                    if atype == UNIX_DIAG_RQLEN and len(payload) >= 8:
                        rq, wq = struct.unpack_from("II", payload, 0)
                        found["rqlen"] = (rq, wq)
                    elif atype == UNIX_DIAG_MEMINFO and len(payload) >= 4:
                        words = struct.unpack(
                            f"<{len(payload)//4}I",
                            payload[:len(payload)//4*4])
                        found["meminfo"] = words
                    aoff += (alen + 3) & ~3
            off += (mlen + 3) & ~3
        if done: break
    nl.close()
    return found

def state(r, label):
    ino = os.fstat(r.fileno()).st_ino
    q = diag_query(ino)
    print(f"  {label} (ino {ino}): {q}", flush=True)

r, s = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
print("== diag accounting by queue state ==")
state(r, "empty")
for _ in range(5): s.send(b"")
state(r, "5 plain zeros queued")
r.recv(64); state(r, "after 1 recv")
r.recv(64); r.recv(64); r.recv(64)
state(r, "after 4 recvs (1 zero left)")
r.recv(64); state(r, "after 5 recvs (empty)")
pr, pw = os.pipe()
s.sendmsg(b"", [(socket.SOL_SOCKET, socket.SCM_RIGHTS,
                 array.array("i", [pr]))])
os.close(pr)
state(r, "1 ancillary zero queued")
d, anc, _f, _ = r.recvmsg(64, socket.CMSG_SPACE(16))
for lvl, typ, dat in anc:
    aa = array.array("i"); aa.frombytes(dat)
    for f in aa: os.close(f)
state(r, "ancillary consumed")
os.close(pw)
s.send(b"XYZ")
state(r, "1 data record queued")
r.recv(64); state(r, "data consumed")
print("PROBE DONE")
