#!/usr/bin/env python3
"""Probe 3: STATUS destruction isolated by residue KIND, with the
residue in the correct direction — queued in the EXITING process's
receive queue (parent/supervisor sends, child/launcher exits).

Questions:
Q-A: do ONLY plain zero-length records unread at exit destroy the
     final STATUS? (3 zeros; 1500 zeros)
Q-B: does a single zero-length ancillary record alone destroy it?
Q-C: does a single data record alone destroy it?
Q-D: on the mixed residue (3 zeros + ancillary zero + data):
     plain vs Correction-1 drain vs purge-only vs purge+drain.
"""
import array, fcntl, os, socket, struct, time

def send_residue(a, spec):
    if spec == "zeros3":
        for _ in range(3): a.send(b"")
    elif spec == "zeros1500":
        a.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 16777216)
        a.setblocking(False)
        deadline = time.time() + 5; sent = 0
        while sent < 1500:
            try: a.send(b""); sent += 1
            except BlockingIOError:
                if time.time() > deadline: break
                time.sleep(0.01)
        a.setblocking(True)
        return sent
    elif spec == "anc1":
        r, w = os.pipe()
        a.sendmsg(b"", [(socket.SOL_SOCKET, socket.SCM_RIGHTS,
                         array.array("i", [r]))])
        os.close(r); os.close(w)
    elif spec == "data1":
        a.send(b"XYZ")
    elif spec == "mixed":
        for _ in range(3): a.send(b"")
        r, w = os.pipe()
        a.sendmsg(b"", [(socket.SOL_SOCKET, socket.SCM_RIGHTS,
                         array.array("i", [r]))])
        os.close(r); os.close(w)
        a.send(b"XYZ")
    return None

def anc_recv(sock):
    data, anc, flags, _ = sock.recvmsg(64, socket.CMSG_SPACE(4 * 4))
    fds = []
    for lvl, typ, dat in anc:
        if lvl == socket.SOL_SOCKET and typ == socket.SCM_RIGHTS:
            arr = array.array("i"); arr.frombytes(dat); fds = list(arr)
    return data, fds

def drain_corr1(b):
    """The Correction-1 algorithm, as built."""
    b.setblocking(False)
    records = 0
    while records < 1024:
        try:
            d, fds = anc_recv(b)
        except (BlockingIOError, OSError):
            return
        records += 1
        for f in fds: os.close(f)
        if d == b"" and not fds:
            avail = struct.unpack("i", fcntl.ioctl(
                b.fileno(), 0x541B, struct.pack("i", 0)))[0]
            if avail == 0:
                return

def run_case(spec, variant, trials):
    lost = 0
    for t in range(trials):
        a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        note = send_residue(a, spec)
        if spec == "zeros1500" and t == 0:
            print(f"  [zeros1500: {note} records queued]", flush=True)
        pid = os.fork()
        if pid == 0:
            a.close()
            b.send(b"\x07STATUS-word")
            if variant == "plain":
                pass
            elif variant == "purge":
                b.shutdown(socket.SHUT_RD)
            elif variant == "drain":
                drain_corr1(b)
            elif variant == "purge+drain":
                b.shutdown(socket.SHUT_RD)
                drain_corr1(b)
            os._exit(0)
        b.close()
        os.waitpid(pid, 0)
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
    return lost

print("Q-A zeros3 / plain:", run_case("zeros3", "plain", 20), "lost /20", flush=True)
print("Q-A zeros1500 / plain:", run_case("zeros1500", "plain", 10), "lost /10", flush=True)
print("Q-B anc1 / plain:", run_case("anc1", "plain", 20), "lost /20", flush=True)
print("Q-C data1 / plain:", run_case("data1", "plain", 20), "lost /20", flush=True)
print("Q-D mixed / plain:", run_case("mixed", "plain", 20), "lost /20", flush=True)
print("Q-D mixed / drain:", run_case("mixed", "drain", 20), "lost /20", flush=True)
print("Q-D mixed / purge:", run_case("mixed", "purge", 20), "lost /20", flush=True)
print("Q-D mixed / purge+drain:", run_case("mixed", "purge+drain", 20), "lost /20", flush=True)
print("PROBE DONE", flush=True)
