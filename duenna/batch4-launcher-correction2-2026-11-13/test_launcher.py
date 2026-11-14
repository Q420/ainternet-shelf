#!/usr/bin/env python3
"""Acceptance suite for the corrected pilot launcher
(Batch 4 source correction, plan Rev 3). The suite acts
as the supervisor peer on the status channel and exercises
the TEST build (PILOT_TEST_HOOKS) against the test harness
programme. It never touches the production path.

Cases: P1 happy path (+handoff identity) - P2 launcher
kill window - P3 descriptor closure (+forced failure) -
P5 class-T ABORT (+malformed variants) - P6 orderly EOF,
malformed packet, injected receive error - P7 ancillary
violations - P8 request-stage violation - P9 unknown
message. Run as root in the room."""
import ctypes, os, pwd, socket, struct, subprocess, sys, time

LAUNCHER = "/srv/nemotron-pilot/batch4/test/launcher-test"
RESULTS = "/srv/nemotron-pilot/batch4/test-results"
CLOSED_LOG = "/srv/nemotron-pilot/batch4/test-hooks/closed-fds.log"
HARNESS_UID = pwd.getpwnam("pilot-harness").pw_uid
HARNESS_GID = pwd.getpwnam("pilot-harness").pw_gid
libc = ctypes.CDLL("libc.so.6", use_errno=True)

fails = 0
total = 0
def chk(name, cond, detail=""):
    global fails, total
    total += 1
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" -- {detail}" if detail and not cond else ""))
    if not cond:
        fails += 1

def u32(b, o): return struct.unpack(">I", b[o:o + 4])[0]
def u64(b, o): return struct.unpack(">Q", b[o:o + 8])[0]

def exited(word): return (word & 0x7F) == 0
def exit_code(word): return (word >> 8) & 0xFF
def signalled(word): return (word & 0x7F) not in (0, 0x7F)
def term_sig(word): return word & 0x7F

class Peer:
    def __init__(self, run_id, env_extra=None, extra_fds=()):
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
        for i, fd in enumerate(extra_fds):
            actions.append((os.POSIX_SPAWN_DUP2, fd, 7 + i))
        env = dict(os.environ)
        if env_extra:
            env.update(env_extra)
        self.pid = os.posix_spawn(LAUNCHER, [LAUNCHER, run_id], env, file_actions=actions)
        self.lch.close()
        self.child_pid = None
        self.pidfd = None

    def send(self, data, fds=()):
        if fds:
            self.sup.sendmsg([data], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, struct.pack("i" * len(fds), *fds))])
        else:
            self.sup.send(data)

    def recv(self):
        """-> (packet, [fds]) or None on EOF/timeout"""
        try:
            data, anc, flags, _ = self.sup.recvmsg(4096, socket.CMSG_SPACE(16))
        except (socket.timeout, TimeoutError):
            return ("TIMEOUT", [])
        except ConnectionResetError:
            return None
        if not data:
            return None
        got = []
        for level, typ, dat in anc:
            if level == socket.SOL_SOCKET and typ == socket.SCM_RIGHTS:
                got = list(struct.unpack("i" * (len(dat) // 4), dat))
        return (data, got)

    def request(self):
        pkt = struct.pack(">B B I I I", 0x01, 0, os.getpid(), HARNESS_UID, HARNESS_GID) + self.run_id.encode()
        self.send(pkt)

    def handoff(self):
        r = self.recv()
        if not r or r == ("TIMEOUT", []) or not r[0]:
            return None
        pkt, fds = r
        if pkt[0] != 0x02 or len(fds) != 1:
            return None
        self.child_pid = u32(pkt, 2)
        self.start_time = u64(pkt, 6)
        self.pidfd = fds[0]
        return pkt

    def ack(self, code=0):
        self.send(struct.pack(">BBB", 0x03, 0, code))

    def wait_gate_ready(self):
        r = self.recv()
        return r and r != ("TIMEOUT", []) and r[0] and r[0][0] == 0x04

    def wait_exit(self, timeout=6.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            wpid, status = os.waitpid(self.pid, os.WNOHANG)
            if wpid == self.pid:
                return status
            time.sleep(0.02)
        os.kill(self.pid, 9)
        _, status = os.waitpid(self.pid, 0)
        return status

    def drain_until_eof(self):
        pkts = []
        while True:
            r = self.recv()
            if r is None or r == ("TIMEOUT", []):
                return pkts
            pkts.append(r[0])

    def close(self):
        try: self.sup.close()
        except OSError: pass
        if self.pidfd is not None:
            try: os.close(self.pidfd)
            except OSError: pass
            self.pidfd = None

def result_path(run_id):
    return os.path.join(RESULTS, run_id + ".txt")

def to_gate_ready(run_id, **kw):
    p = Peer(run_id, **kw)
    p.request()
    if p.handoff() is None:
        return p, False
    p.ack(0)
    return p, p.wait_gate_ready()

def closed_fd_count():
    try:
        with open(CLOSED_LOG) as f:
            return sum(int(l.split()[1]) for l in f if l.startswith("closed"))
    except FileNotFoundError:
        return 0

def proc_start_time(pid):
    with open(f"/proc/{pid}/stat") as f:
        data = f.read()
    return int(data[data.rindex(")") + 2:].split()[19])

# ---------------- P1: happy path ----------------
rid = "PEERP1-20261113-001"
p = Peer(rid)
p.request()
h = p.handoff()
chk("P1 handoff received with one pidfd", h is not None)
if h is not None:
    with open(f"/proc/self/fdinfo/{p.pidfd}") as f:
        fdinfo_pid = int([l for l in f if l.startswith("Pid:")][0].split()[1])
    chk("P1 fdinfo target == handoff child pid", fdinfo_pid == p.child_pid,
        f"fdinfo {fdinfo_pid} vs packet {p.child_pid}")
    chk("P1 handoff start time == /proc start time",
        p.start_time == proc_start_time(p.child_pid))
    p.ack(0)
    chk("P1 GATE_READY", p.wait_gate_ready())
    p.send(b"\x05\x00")
    r = p.recv()
    chk("P1 GATE_ACTUATED", r and r[0] and r[0][0] == 0x06)
    r = p.recv()
    ok = r and r[0] and r[0][0] == 0x07
    chk("P1 STATUS received", bool(ok))
    if ok:
        word = u32(r[0], 6)
        chk("P1 STATUS pid == child pid", u32(r[0], 2) == p.child_pid)
        chk("P1 STATUS word == exited 42", exited(word) and exit_code(word) == 42,
            f"word {word:#x}")
    st = p.wait_exit()
    chk("P1 launcher exit 0", exited(st) and exit_code(st) == 0, f"status {st:#x}")
    time.sleep(0.2)
    rp = result_path(rid)
    if os.path.exists(rp):
        body = open(rp).read()
        chk("P1 result file: harness uid", f"uid={HARNESS_UID}" in body, body)
        fd_line = [l for l in body.splitlines() if l.startswith("fds:")]
        chk("P1 result file: fds exactly 0 1 2", fd_line and fd_line[0].split()[1:] == ["0", "1", "2"],
            str(fd_line))
    else:
        chk("P1 result file exists", False)
p.close()

# ---------------- P2: launcher kill window ----------------
no_exec = True
leftovers = True
for i in range(20):
    rid = f"PEERP2-20261113-{i + 1:03d}"
    p = Peer(rid)
    p.request()
    h = p.handoff()
    if i >= 10 and h is not None:
        time.sleep(0.005 * (i - 9))
    os.kill(p.pid, 9)
    p.wait_exit()
    time.sleep(0.25)
    if os.path.exists(result_path(rid)):
        no_exec = False
    # any gated child must be gone (gate EOF / PDEATHSIG)
    try:
        out = subprocess.run(["pgrep", "-f", "batch4/test/test-harness"],
                             capture_output=True, text=True)
        if out.stdout.strip():
            leftovers = False
    except Exception:
        pass
    p.close()
chk("P2 kill window (20x): harness never executed", no_exec)
chk("P2 kill window (20x): no harness process left behind", leftovers)

# ---------------- P3a: inherited descriptors closed ----------------
rid = "PEERP3-20261113-001"
extra_file = os.open("/tmp/peer-extra-file", os.O_CREAT | os.O_RDWR, 0o644)
extra_r, extra_w = os.pipe()
p, ok = to_gate_ready(rid, extra_fds=(extra_file, extra_r))
chk("P3a reached gate with extra fds in launcher", ok)
if ok:
    p.send(b"\x05\x00")
    p.recv(); r = p.recv()
    time.sleep(0.2)
    rp = result_path(rid)
    body = open(rp).read() if os.path.exists(rp) else ""
    fd_line = [l for l in body.splitlines() if l.startswith("fds:")]
    chk("P3a harness fds exactly 0 1 2 despite inherited extras",
        fd_line and fd_line[0].split()[1:] == ["0", "1", "2"], str(fd_line))
p.wait_exit(); p.close()
os.close(extra_file); os.close(extra_r); os.close(extra_w)

# ---------------- P3b: forced close failure ----------------
# The child dies at establishment step (g) with exit 73; the
# supervisor peer observes the termination on the pidfd
# (readiness) and answers ACK 3 — the R-3 path: the launcher
# reaps, reports ABORT/CHILD_TERMINATED_AT_HANDOFF carrying
# the word, and exits 3.
rid = "PEERP3-20261113-002"
p = Peer(rid, env_extra={"PILOT_HOOK_FAIL_CLOSE_RANGE": "1"})
p.request()
h = p.handoff()
chk("P3b handoff received", h is not None)
if h is not None:
    import select as _sel
    rdy, _, _ = _sel.select([p.pidfd], [], [], 3.0)
    chk("P3b child terminated during establishment (pidfd readable)", bool(rdy))
    p.ack(3)
    r = p.recv()
    ok = r and r[0] and r[0][0] == 0x09 and len(r[0]) == 7
    chk("P3b ABORT received (R-3)", bool(ok))
    if ok:
        word = u32(r[0], 3)
        chk("P3b ABORT reason CHILD_TERMINATED_AT_HANDOFF (3)", r[0][2] == 3,
            f"reason {r[0][2]}")
        chk("P3b ABORT word == child exit 73 (setup failed)",
            exited(word) and exit_code(word) == 73, f"word {word:#x}")
    st = p.wait_exit()
    chk("P3b launcher exit 3", exited(st) and exit_code(st) == 3, f"status {st:#x}")
    chk("P3b harness never executed", not os.path.exists(result_path(rid)))
p.close()

# ---------------- P5: class-T ABORT ----------------
rid = "PEERP5-20261113-001"
p, ok = to_gate_ready(rid)
chk("P5 reached gate", ok)
if ok:
    rc = libc.syscall(424, p.pidfd, 9, None, 0)  # pidfd_send_signal SIGKILL
    chk("P5 pidfd_send_signal delivered", rc == 0)
    p.send(b"\x09\x00\x02")
    r = p.recv()
    ok2 = r and r[0] and r[0][0] == 0x07
    chk("P5 class-T: the one STATUS sent", bool(ok2))
    if ok2:
        word = u32(r[0], 6)
        chk("P5 STATUS word == signalled SIGKILL", signalled(word) and term_sig(word) == 9,
            f"word {word:#x}")
    st = p.wait_exit()
    chk("P5 launcher exit 0 after class-T receipt", exited(st) and exit_code(st) == 0)
    chk("P5 harness never executed", not os.path.exists(result_path(rid)))
p.close()

# ---------------- P5 malformed ABORT variants ----------------
for tag, packet in [("word-carrying", b"\x09\x00\x02" + b"\x00\x00\x00\x00"),
                    ("nonzero flags", b"\x09\x01\x02"),
                    ("unknown reason", b"\x09\x00\x63")]:
    rid = f"PEERP5-20261113-{2 + ['word-carrying','nonzero flags','unknown reason'].index(tag):03d}"
    p, ok = to_gate_ready(rid)
    if not ok:
        chk(f"P5 malformed ABORT ({tag}): reached gate", False)
        p.close(); continue
    p.send(packet)
    pkts = p.drain_until_eof()
    st = p.wait_exit()
    chk(f"P5 malformed ABORT ({tag}): exit 8, no STATUS",
        exited(st) and exit_code(st) == 8 and all(q[0] != 0x07 for q in pkts),
        f"status {st:#x} pkts {[q[0] for q in pkts]}")
    chk(f"P5 malformed ABORT ({tag}): harness never executed",
        not os.path.exists(result_path(rid)))
    p.close()

# ---------------- P6: orderly EOF at the Stage 6 wait ----------------
rid = "PEERP6-20261113-001"
p, ok = to_gate_ready(rid)
chk("P6 reached gate", ok)
if ok:
    p.sup.shutdown(socket.SHUT_WR)
    r = p.recv()
    ok2 = r and r[0] and r[0][0] == 0x07
    chk("P6 EOF: STATUS still sent (orderly route)", bool(ok2))
    if ok2:
        word = u32(r[0], 6)
        chk("P6 STATUS word == child gate-refused exit 71",
            exited(word) and exit_code(word) == 71, f"word {word:#x}")
    st = p.wait_exit()
    chk("P6 launcher exit 0", exited(st) and exit_code(st) == 0)
    chk("P6 harness never executed", not os.path.exists(result_path(rid)))
p.close()

# ---------------- P6b: malformed packet at Stage 6 ----------------
rid = "PEERP6-20261113-002"
p, ok = to_gate_ready(rid)
if ok:
    p.send(b"\x05")
    pkts = p.drain_until_eof()
    st = p.wait_exit()
    chk("P6b truncated packet: exit 8, no STATUS",
        exited(st) and exit_code(st) == 8 and all(q[0] != 0x07 for q in pkts))
    chk("P6b harness never executed", not os.path.exists(result_path(rid)))
else:
    chk("P6b reached gate", False)
p.close()

# ---------------- P6c: injected receive error (finding 6, -3) ----------------
rid = "PEERP6-20261113-003"
p, ok = to_gate_ready(rid, env_extra={"PILOT_HOOK_FAIL_RECVMSG_AT": "3"})
chk("P6c reached gate", ok)
if ok:
    pkts = p.drain_until_eof()
    st = p.wait_exit()
    chk("P6c receive error: exit 9, no STATUS, not EOF-classified",
        exited(st) and exit_code(st) == 9 and all(q[0] != 0x07 for q in pkts),
        f"status {st:#x}")
    chk("P6c harness never executed", not os.path.exists(result_path(rid)))
    # the child was collected via the gate-EOF route: pidfd readable, proc gone
    import select
    rdy, _, _ = select.select([p.pidfd], [], [], 2.0)
    chk("P6c child terminated (pidfd readable)", bool(rdy))
p.close()

# ---------------- P7: ancillary violations (finding 7) ----------------
before = closed_fd_count()
rid = "PEERP7-20261113-001"
p, ok = to_gate_ready(rid)
if ok:
    afd = os.open("/tmp/peer-ancillary", os.O_CREAT | os.O_RDWR, 0o644)
    p.send(b"\x05\x00", fds=(afd,))
    os.close(afd)
    pkts = p.drain_until_eof()
    st = p.wait_exit()
    chk("P7 RELEASE with ancillary fd: exit 8, no GATE_ACTUATED/STATUS",
        exited(st) and exit_code(st) == 8 and all(q[0] not in (0x06, 0x07) for q in pkts),
        f"status {st:#x} pkts {[q[0] for q in pkts]}")
    chk("P7 harness never executed", not os.path.exists(result_path(rid)))
else:
    chk("P7 reached gate", False)
p.close()
time.sleep(0.2)
chk("P7 delivered descriptor was closed by the launcher",
    closed_fd_count() >= before + 1, f"before {before} after {closed_fd_count()}")

rid = "PEERP7-20261113-002"
before = closed_fd_count()
p, ok = to_gate_ready(rid)
if ok:
    afd = os.open("/tmp/peer-ancillary", os.O_CREAT | os.O_RDWR, 0o644)
    p.send(b"\x05\x00" + b"\x00" * 198, fds=(afd,))  # oversized -> MSG_TRUNC, with fd
    os.close(afd)
    pkts = p.drain_until_eof()
    st = p.wait_exit()
    chk("P7b truncated packet with fd: exit 8, no STATUS",
        exited(st) and exit_code(st) == 8 and all(q[0] != 0x07 for q in pkts))
else:
    chk("P7b reached gate", False)
p.close()
time.sleep(0.2)
chk("P7b descriptor on truncated packet was closed",
    closed_fd_count() >= before + 1, f"before {before} after {closed_fd_count()}")

# ---------------- P8: ancillary on the launch request ----------------
rid = "PEERP8-20261113-001"
p = Peer(rid)
afd = os.open("/tmp/peer-ancillary", os.O_CREAT | os.O_RDWR, 0o644)
pkt = struct.pack(">B B I I I", 0x01, 0, os.getpid(), HARNESS_UID, HARNESS_GID) + rid.encode()
p.send(pkt, fds=(afd,))
os.close(afd)
st = p.wait_exit()
chk("P8 ancillary on LAUNCH_REQUEST: exit 8 before any fork",
    exited(st) and exit_code(st) == 8, f"status {st:#x}")
chk("P8 harness never executed", not os.path.exists(result_path(rid)))
p.close()

# ---------------- P9: unknown message at Stage 6 ----------------
rid = "PEERP9-20261113-001"
p, ok = to_gate_ready(rid)
if ok:
    p.send(b"\x7f\x00")
    pkts = p.drain_until_eof()
    st = p.wait_exit()
    chk("P9 unknown message: exit 8, no STATUS",
        exited(st) and exit_code(st) == 8 and all(q[0] != 0x07 for q in pkts))
else:
    chk("P9 reached gate", False)
p.close()

# ---------------- Round 2: zero-length records (Fix A) ----------------
# Z1: empty record WITH descriptor at the Stage 6 wait
before = closed_fd_count()
rid = "PEERZ1-20261113-001"
p, ok = to_gate_ready(rid)
if ok:
    afd = os.open("/tmp/peer-ancillary", os.O_CREAT | os.O_RDWR, 0o644)
    p.send(b"", fds=(afd,))
    os.close(afd)
    pkts = p.drain_until_eof()
    st = p.wait_exit()
    chk("Z1 empty record + fd at Stage 6: exit 8 (not EOF route), no STATUS",
        exited(st) and exit_code(st) == 8 and all(q[0] != 0x07 for q in pkts),
        f"status {st:#x} pkts {[q[0] for q in pkts]}")
    chk("Z1 harness never executed", not os.path.exists(result_path(rid)))
else:
    chk("Z1 reached gate", False)
p.close()
time.sleep(0.2)
chk("Z1 delivered descriptor was closed", closed_fd_count() >= before + 1,
    f"before {before} after {closed_fd_count()}")

# Z2: empty record WITH descriptor at the ACK wait
before = closed_fd_count()
rid = "PEERZ2-20261113-001"
p = Peer(rid)
p.request()
h = p.handoff()
chk("Z2 handoff received", h is not None)
if h is not None:
    afd = os.open("/tmp/peer-ancillary", os.O_CREAT | os.O_RDWR, 0o644)
    p.send(b"", fds=(afd,))
    os.close(afd)
    pkts = p.drain_until_eof()
    st = p.wait_exit()
    chk("Z2 empty record + fd at ACK wait: exit 8, no STATUS",
        exited(st) and exit_code(st) == 8 and all(q[0] != 0x07 for q in pkts),
        f"status {st:#x}")
    chk("Z2 harness never executed", not os.path.exists(result_path(rid)))
p.close()
time.sleep(0.2)
chk("Z2 delivered descriptor was closed", closed_fd_count() >= before + 1,
    f"before {before} after {closed_fd_count()}")

# Z3: empty record WITHOUT ancillary data at the Stage 6 wait —
# the discriminator test: must NOT take the EOF route
rid = "PEERZ3-20261113-001"
p, ok = to_gate_ready(rid)
if ok:
    p.send(b"")
    pkts = p.drain_until_eof()
    st = p.wait_exit()
    chk("Z3 bare empty record at Stage 6: exit 8, no STATUS (not EOF)",
        exited(st) and exit_code(st) == 8 and all(q[0] != 0x07 for q in pkts),
        f"status {st:#x} pkts {[q[0] for q in pkts]}")
    chk("Z3 harness never executed", not os.path.exists(result_path(rid)))
else:
    chk("Z3 reached gate", False)
p.close()

# Z4: bare empty record at the ACK wait
rid = "PEERZ4-20261113-001"
p = Peer(rid)
p.request()
h = p.handoff()
if h is not None:
    p.send(b"")
    pkts = p.drain_until_eof()
    st = p.wait_exit()
    chk("Z4 bare empty record at ACK wait: exit 8, no STATUS",
        exited(st) and exit_code(st) == 8 and all(q[0] != 0x07 for q in pkts),
        f"status {st:#x}")
    chk("Z4 harness never executed", not os.path.exists(result_path(rid)))
else:
    chk("Z4 handoff received", False)
p.close()

# ---------------- Round 2: ACK-wait ABORT matrix (Fix B) ----------------
import select as _sel2
for tag, packet, want in [
        ("nonzero flags", b"\x09\x01\x02", 8),
        ("unknown reason", b"\x09\x00\x63", 8),
        ("word-carrying", b"\x09\x00\x02" + b"\x00\x00\x00\x00", 8),
        ("truncated", b"\x09\x00", 8),
        ("well-formed (regression)", b"\x09\x00\x07", 6)]:
    rid = f"PEERA-{tag[:4].upper().replace(' ', '')}-20261113-001".replace("(", "").replace(")", "")
    p = Peer(rid)
    p.request()
    h = p.handoff()
    if h is None:
        chk(f"ACK-ABORT {tag}: handoff received", False)
        p.close(); continue
    p.send(packet)
    pkts = p.drain_until_eof()
    st = p.wait_exit()
    rdy, _, _ = _sel2.select([p.pidfd], [], [], 2.0) if p.pidfd is not None else ([], [], [])
    chk(f"ACK-ABORT {tag}: exit {want}, no STATUS, child collected",
        exited(st) and exit_code(st) == want and all(q[0] != 0x07 for q in pkts) and bool(rdy),
        f"status {st:#x} pkts {[q[0] for q in pkts]} rdy {bool(rdy)}")
    chk(f"ACK-ABORT {tag}: harness never executed", not os.path.exists(result_path(rid)))
    p.close()

# ---------------- Round 2: NQ1 / NQ2 (Revision 4) ----------------
# NQ1: empty record, then a valid RELEASE, then shutdown (Stage 6 wait).
# The peek must expose the queued packet: violation, not clean EOF.
rid = "PEERNQ1-20261113-001"
p, ok = to_gate_ready(rid)
if ok:
    p.send(b"")
    p.send(b"\x05\x00")
    p.sup.shutdown(socket.SHUT_WR)
    pkts = p.drain_until_eof()
    st = p.wait_exit()
    chk("NQ1 queued RELEASE behind empty record + shutdown: exit 8, no STATUS/ACTUATED",
        exited(st) and exit_code(st) == 8 and all(q[0] not in (0x06, 0x07) for q in pkts),
        f"status {st:#x} pkts {[q[0] for q in pkts]}")
    chk("NQ1 harness never executed", not os.path.exists(result_path(rid)))
else:
    chk("NQ1 reached gate", False)
p.close()

# NQ2 (ACCEPTED LIMITATION, Treatment A — demonstrates the limit;
# it is NOT a pass of the original violation expectation):
# empty A, empty B, shutdown at the Stage 6 wait -> orderly EOF outcome.
rid = "PEERNQ2-20261113-001"
p, ok = to_gate_ready(rid)
if ok:
    p.send(b"")
    p.send(b"")
    p.sup.shutdown(socket.SHUT_WR)
    pkts = p.drain_until_eof()
    st = p.wait_exit()
    stat = [q for q in pkts if q[0] == 0x07]
    word_ok = False
    if stat:
        word = u32(stat[0], 6)
        word_ok = exited(word) and exit_code(word) == 71
    chk("NQ2 LIMITATION at Stage 6: EOF outcome (STATUS, exit 0), no actuation",
        exited(st) and exit_code(st) == 0 and len(stat) == 1 and word_ok
        and all(q[0] != 0x06 for q in pkts),
        f"status {st:#x} pkts {[q[0] for q in pkts]}")
    chk("NQ2 harness never executed", not os.path.exists(result_path(rid)))
else:
    chk("NQ2 reached gate", False)
p.close()

# NQ2 at the ACK wait: handoff, then A, B, shutdown -> EOF outcome there
# is cleanup + exit 6, no STATUS.
rid = "PEERNQ2B-20261113-001"
p = Peer(rid)
p.request()
h = p.handoff()
if h is not None:
    p.send(b"")
    p.send(b"")
    p.sup.shutdown(socket.SHUT_WR)
    pkts = p.drain_until_eof()
    st = p.wait_exit()
    chk("NQ2 LIMITATION at ACK wait: EOF outcome (exit 6), no STATUS",
        exited(st) and exit_code(st) == 6 and all(q[0] != 0x07 for q in pkts),
        f"status {st:#x} pkts {[q[0] for q in pkts]}")
    chk("NQ2-ACK harness never executed", not os.path.exists(result_path(rid)))
else:
    chk("NQ2-ACK handoff received", False)
p.close()

print(f"peer: {total - fails}/{total} PASS")
sys.exit(1 if fails else 0)
