#!/usr/bin/env python3
"""Standalone NQ5' reproduction probe: runs the residue
sequence 10 times with timing prints, to characterise the
flake seen in peer runs 3/4 (exit 0, no packets drained)."""
import os, socket, struct, sys, time
sys.path.insert(0, "/srv/nemotron-pilot/batch4/test-src")
import importlib.util
spec = importlib.util.spec_from_file_location("tl", "/srv/nemotron-pilot/batch4/test-src/test_launcher.py")

# Do NOT import the suite (it executes). Re-declare the Peer bits.
import ctypes, pwd
LAUNCHER = "/srv/nemotron-pilot/batch4/test/launcher-test"
HARNESS_UID = pwd.getpwnam("pilot-harness").pw_uid
HARNESS_GID = pwd.getpwnam("pilot-harness").pw_gid

def u32(b, o): return struct.unpack(">I", b[o:o + 4])[0]

class Peer:
    def __init__(self, run_id, env_extra=None):
        self.run_id = run_id
        self.sup, self.lch = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.sup.settimeout(6.0)
        logf = f"/srv/nemotron-pilot/batch4/test-logs/{run_id}.log"
        actions = [
            (os.POSIX_SPAWN_OPEN, 0, "/dev/null", os.O_RDONLY, 0),
            (os.POSIX_SPAWN_OPEN, 1, logf, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644),
            (os.POSIX_SPAWN_DUP2, 2, 1),
            (os.POSIX_SPAWN_DUP2, self.lch.fileno(), 3),
        ]
        env = dict(os.environ)
        if env_extra: env.update(env_extra)
        self.pid = os.posix_spawn(LAUNCHER, [LAUNCHER, run_id], env, file_actions=actions)
        self.lch.close()
        self.pidfd = None
    def send(self, data, fds=()):
        if fds:
            self.sup.sendmsg([data], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, struct.pack("i" * len(fds), *fds))])
        else:
            self.sup.send(data)
    def recv(self):
        try:
            data, anc, flags, _ = self.sup.recvmsg(4096, socket.CMSG_SPACE(16))
        except (socket.timeout, TimeoutError):
            return ("TIMEOUT", [])
        except ConnectionResetError:
            return None
        if not data: return None
        got = []
        for level, typ, dat in anc:
            if level == socket.SOL_SOCKET and typ == socket.SCM_RIGHTS:
                got = list(struct.unpack("i" * (len(dat) // 4), dat))
        return (data, got)
    def request(self):
        self.send(struct.pack(">B B I I I", 0x01, 0, os.getpid(), HARNESS_UID, HARNESS_GID) + self.run_id.encode())
    def handoff(self):
        r = self.recv()
        if not r or r == ("TIMEOUT", []) or not r[0]: return None
        pkt, fds = r
        if pkt[0] != 0x02 or len(fds) != 1: return None
        self.pidfd = fds[0]
        return pkt
    def ack(self, code=0):
        self.send(struct.pack(">BBB", 0x03, 0, code))
    def wait_exit(self, timeout=6.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            wpid, status = os.waitpid(self.pid, os.WNOHANG)
            if wpid == self.pid: return status
            time.sleep(0.02)
        os.kill(self.pid, 9)
        _, status = os.waitpid(self.pid, 0)
        return status

for i in range(10):
    rid = f"PROBENQ5-20261114-{i+1:03d}"
    p = Peer(rid, env_extra={"PILOT_HOOK_STALL_RECV_MS": "400"})
    t0 = time.time()
    p.request()
    h = p.handoff()
    if h is None:
        print(f"iter {i}: NO HANDOFF"); continue
    p.ack(0)
    r = p.recv()
    gate = r and r != ("TIMEOUT", []) and r[0] and r[0][0] == 0x04
    if not gate:
        print(f"iter {i}: NO GATE_READY r={r}"); p.wait_exit(); continue
    afd = os.open("/tmp/peer-ancillary", os.O_CREAT | os.O_RDWR, 0o644)
    p.send(b"")
    p.send(b"")
    p.send(b"", fds=(afd,))
    os.close(afd)
    p.sup.shutdown(socket.SHUT_WR)
    pkts = []
    while True:
        r = p.recv()
        if r is None or r == ("TIMEOUT", []):
            pkts.append(("EOF/TIMEOUT", time.time() - t0))
            break
        pkts.append((r[0][0], time.time() - t0))
    st = p.wait_exit()
    print(f"iter {i}: exit_word={st:#x} pkts={pkts}")
    try: p.sup.close()
    except OSError: pass
    if p.pidfd is not None:
        try: os.close(p.pidfd)
        except OSError: pass
