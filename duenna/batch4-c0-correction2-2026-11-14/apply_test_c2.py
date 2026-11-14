#!/usr/bin/env python3
"""Build test_launcher_c2.py from test_launcher.py.

Correction 2 (chunk sheet K6/K7): the Peer stub gains the
contract supervisor half — a status pipe (pipe2 O_CLOEXEC)
whose writer rides fd 4, the stub's own copy closed at
spawn, and the contract \u00a75 receiver (classify_status_fd)
run after the launcher is reaped. STATUS-positive cases
(P1, P3a, P5, P6, NQ2', NQ5', D-C2) convert from channel
STATUS reads to pipe acceptance plus a channel-must-be-
empty assertion. New K7 cases are appended before the
summary. The fork-spawn mode runs the stub's literal
CLOEXEC procedure (placement, F_SETFD clear, F_GETFD
read-back, reject on failure) for both fd mappings.
Every replacement is exact-match and count-checked."""
import hashlib, sys

SRC = "test_launcher.py"
DST = "test_launcher_c2.py"
EXPECTED_SHA256 = None  # filled from the file itself below

src = open(SRC).read()

def rep(old, new, count=1):
    global src
    found = src.count(old)
    assert found == count, f"anchor found {found}x (want {count}): {old[:70]!r}"
    src = src.replace(old, new)

# ---- R1: header note ----
rep('Run as root in the room."""',
    'Run as root in the room.\n\nC2 (Batch 4 Correction 2): STATUS travels the dedicated\npipe on fd 4 (contract \u00a73.5); the channel never carries\n0x07. The Peer stub is the contract supervisor: pipe2\n(O_CLOEXEC), writer on fd 4, own copy closed at spawn,\nreceiver per contract \u00a75 run after the launcher is\nreaped."""')

# ---- R2: classify_status_fd + Peer rework ----
rep('''class Peer:
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
''',
'''def classify_status_fd(fd, deadline_s=2.0):
    """Contract \u00a75 receiver over a pipe read end. Run AFTER
    the launcher has been reaped (the NO_EOF rule is event-
    bound: post-reap, EOF must be reachable). Accumulate to
    EOF and classify: ACCEPT (exactly 10 bytes, code 0x07),
    TRUNCATED (<10 then EOF), EXTRA (>10 bytes), INVALID
    (10 bytes, bad code), NONE (0 bytes then EOF), NO_EOF
    (a writer is still open at the deadline)."""
    os.set_blocking(fd, False)
    data = b""
    end = time.time() + deadline_s
    while True:
        try:
            chunk = os.read(fd, 64)
        except BlockingIOError:
            if time.time() > end:
                return ("NO_EOF", data)
            time.sleep(0.02)
            continue
        if chunk == b"":
            break
        data += chunk
        if len(data) > 10:
            return ("EXTRA", data)
    if len(data) == 0:
        return ("NONE", data)
    if len(data) < 10:
        return ("TRUNCATED", data)
    if data[0] != 0x07:
        return ("INVALID", data)
    return ("ACCEPT", data)

class Peer:
    def __init__(self, run_id, env_extra=None, extra_fds=(),
                 status_mode="pipe", hold_status_writer=False,
                 close_status_reader=False, spawn_mode="posix",
                 cloexec_case=None):
        self.run_id = run_id
        self.extra_fds_saved = extra_fds
        self.status_mode = status_mode
        self.cloexec_case = cloexec_case
        self.sup, self.lch = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.sup.settimeout(6.0)
        logf = f"/srv/nemotron-pilot/batch4/test-logs/{run_id}.log"
        # the contract supervisor creates the STATUS pipe
        # with pipe2(O_CLOEXEC) before spawning the launcher
        self.st_r = None
        self.st_w = None
        self.reg_fd = None
        if status_mode in ("pipe", "readend"):
            self.st_r, self.st_w = os.pipe2(os.O_CLOEXEC)
        env = dict(os.environ)
        if env_extra:
            env.update(env_extra)
        if spawn_mode == "fork":
            self.pid = self._fork_spawn(env, logf)
        else:
            actions = [
                (os.POSIX_SPAWN_OPEN, 0, "/dev/null", os.O_RDONLY, 0),
                (os.POSIX_SPAWN_OPEN, 1, logf, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644),
                (os.POSIX_SPAWN_DUP2, 2, 1),
                (os.POSIX_SPAWN_DUP2, self.lch.fileno(), 3),
            ]
            if status_mode == "pipe":
                actions.append((os.POSIX_SPAWN_DUP2, self.st_w, 4))
            elif status_mode == "readend":
                actions.append((os.POSIX_SPAWN_DUP2, self.st_r, 4))
            elif status_mode == "regfile":
                self.reg_fd = os.open("/tmp/peer-status-regfile",
                                      os.O_CREAT | os.O_WRONLY, 0o644)
                actions.append((os.POSIX_SPAWN_DUP2, self.reg_fd, 4))
            for i, fd in enumerate(extra_fds):
                actions.append((os.POSIX_SPAWN_DUP2, fd, 7 + i))
            self.pid = os.posix_spawn(LAUNCHER, [LAUNCHER, run_id], env, file_actions=actions)
        self.lch.close()
        # the stub closes its own writer copy immediately
        # post-spawn (the contract's supervisor duty); the
        # receiver's NO_EOF outcome backstops a missed close
        self.writer_closed = False
        if status_mode == "pipe" and self.st_w is not None and not hold_status_writer:
            os.close(self.st_w)
            self.st_w = None
            self.writer_closed = True
        if close_status_reader and self.st_r is not None:
            os.close(self.st_r)
            self.st_r = None
        self.child_pid = None
        self.pidfd = None

    def _place(self, src, target, mode):
        """The stub's CLOEXEC procedure for one mapping
        (fork-spawn children only): land src on target, then
        F_SETFD-clear + F_GETFD read-back; a failed
        verification exits 91 pre-exec (launch rejected).
        mode "dup": dup2 placement. mode "cloexec":
        F_DUPFD_CLOEXEC placement, then clear in place (the
        same-descriptor branch). mode "cloexec-raw": the
        F_DUPFD_CLOEXEC placement WITHOUT the clear — the
        negative case; exec drops the descriptor."""
        F_GETFD, F_SETFD, F_DUPFD_CLOEXEC, FD_CLOEXEC = 1, 2, 1030, 1
        if mode in ("cloexec", "cloexec-raw") and src != target:
            try:
                os.close(target)
            except OSError:
                pass
            if libc.fcntl(src, F_DUPFD_CLOEXEC, target) != target:
                os._exit(91)
        elif src != target:
            os.dup2(src, target)
        if mode == "cloexec-raw":
            return
        fl = libc.fcntl(target, F_GETFD)
        if fl < 0:
            os._exit(91)
        if libc.fcntl(target, F_SETFD, fl & ~FD_CLOEXEC) != 0:
            os._exit(91)
        rb = libc.fcntl(target, F_GETFD)
        if rb < 0 or (rb & FD_CLOEXEC):
            os._exit(91)

    def _fork_spawn(self, env, logf):
        pid = os.fork()
        if pid == 0:
            try:
                case = self.cloexec_case or "differing"
                fd3_mode = "cloexec" if case == "inplace" else "dup"
                fd4_mode = {"differing": "dup", "inplace": "cloexec",
                            "raw": "cloexec-raw"}[case]
                self._place(self.lch.fileno(), 3, fd3_mode)
                if self.status_mode == "pipe":
                    self._place(self.st_w, 4, fd4_mode)
                null = os.open("/dev/null", os.O_RDONLY)
                lg = os.open(logf, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
                os.dup2(null, 0)
                os.dup2(lg, 1)
                os.dup2(1, 2)
                for i, fd in enumerate(self.extra_fds_saved):
                    os.dup2(fd, 7 + i)
                os.execve(LAUNCHER, [LAUNCHER, self.run_id], env)
            except Exception:
                os._exit(92)
        return pid

    def read_status(self):
        """-> (outcome, status_pid, status_word); the pid and
        word are set only on ACCEPT."""
        if self.st_r is None:
            return ("NONE", None, None)
        cls, data = classify_status_fd(self.st_r)
        if cls == "ACCEPT":
            return (cls, u32(data, 2), u32(data, 6))
        return (cls, None, None)
''')

# Peer.close(): also drop the status-pipe ends
rep('''    def close(self):
        try: self.sup.close()
        except OSError: pass
''',
'''    def close(self):
        try: self.sup.close()
        except OSError: pass
        for fd in (self.st_r, self.st_w, self.reg_fd):
            if fd is not None:
                try: os.close(fd)
                except OSError: pass
        self.st_r = self.st_w = self.reg_fd = None
''')
print("part 1 ok")
open(DST, "w").write(src)

# ---- R3: P1 conversion ----
rep('''    p.send(b"\\x05\\x00")
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
''',
'''    p.send(b"\\x05\\x00")
    r = p.recv()
    chk("P1 GATE_ACTUATED", r and r[0] and r[0][0] == 0x06)
    st = p.wait_exit()
    chk("P1 launcher exit 0", exited(st) and exit_code(st) == 0, f"status {st:#x}")
    pkts = p.drain_until_eof()
    chk("P1 channel carries no STATUS (C2: STATUS is pipe-only)",
        all(q[0] != 0x07 for q in pkts), f"pkts {[q[0] for q in pkts]}")
    cls, spid, word = p.read_status()
    chk("P1 STATUS on the pipe, exactly one record + EOF", cls == "ACCEPT", cls)
    if cls == "ACCEPT":
        chk("P1 STATUS pid == child pid", spid == p.child_pid)
        chk("P1 STATUS word == exited 42", exited(word) and exit_code(word) == 42,
            f"word {word:#x}")
''')

# ---- R4: P3a conversion ----
rep('''if ok:
    p.send(b"\\x05\\x00")
    p.recv(); r = p.recv()
    time.sleep(0.2)
''',
'''if ok:
    p.send(b"\\x05\\x00")
    r = p.recv()
    chk("P3a GATE_ACTUATED", r and r[0] and r[0][0] == 0x06)
    time.sleep(0.2)
''')
rep('''        fd_line and fd_line[0].split()[1:] == ["0", "1", "2"], str(fd_line))
p.wait_exit(); p.close()
os.close(extra_file); os.close(extra_r); os.close(extra_w)
''',
'''        fd_line and fd_line[0].split()[1:] == ["0", "1", "2"], str(fd_line))
st3 = p.wait_exit()
cls, spid, word = p.read_status()
chk("P3a STATUS on the pipe (word 42) despite inherited extras",
    cls == "ACCEPT" and exited(word) and exit_code(word) == 42, cls)
p.close()
os.close(extra_file); os.close(extra_r); os.close(extra_w)
''')

# ---- R5: P5 class-T conversion ----
rep('''    p.send(b"\\x09\\x00\\x02")
    r = p.recv()
    ok2 = r and r[0] and r[0][0] == 0x07
    chk("P5 class-T: the one STATUS sent", bool(ok2))
    if ok2:
        word = u32(r[0], 6)
        chk("P5 STATUS word == signalled SIGKILL", signalled(word) and term_sig(word) == 9,
            f"word {word:#x}")
    st = p.wait_exit()
    chk("P5 launcher exit 0 after class-T receipt", exited(st) and exit_code(st) == 0)
''',
'''    p.send(b"\\x09\\x00\\x02")
    st = p.wait_exit()
    chk("P5 launcher exit 0 after class-T receipt", exited(st) and exit_code(st) == 0)
    pkts = p.drain_until_eof()
    chk("P5 channel carries no STATUS (C2)", all(q[0] != 0x07 for q in pkts))
    cls, spid, word = p.read_status()
    chk("P5 class-T: the one STATUS, on the pipe", cls == "ACCEPT", cls)
    if cls == "ACCEPT":
        chk("P5 STATUS word == signalled SIGKILL", signalled(word) and term_sig(word) == 9,
            f"word {word:#x}")
''')

# ---- R6: P6 conversion ----
rep('''    p.sup.shutdown(socket.SHUT_WR)
    r = p.recv()
    ok2 = r and r[0] and r[0][0] == 0x07
    chk("P6 EOF: STATUS still sent (orderly route)", bool(ok2))
    if ok2:
        word = u32(r[0], 6)
        chk("P6 STATUS word == child gate-refused exit 71",
            exited(word) and exit_code(word) == 71, f"word {word:#x}")
    st = p.wait_exit()
    chk("P6 launcher exit 0", exited(st) and exit_code(st) == 0)
''',
'''    p.sup.shutdown(socket.SHUT_WR)
    st = p.wait_exit()
    chk("P6 launcher exit 0", exited(st) and exit_code(st) == 0)
    cls, spid, word = p.read_status()
    chk("P6 EOF: STATUS delivered on the pipe (orderly route)", cls == "ACCEPT", cls)
    if cls == "ACCEPT":
        chk("P6 STATUS word == child gate-refused exit 71",
            exited(word) and exit_code(word) == 71, f"word {word:#x}")
''')

# ---- R7: NQ2' conversion ----
rep('''    stat = [q for q in pkts if q[0] == 0x07]
    word_ok = False
    if stat:
        word = u32(stat[0], 6)
        word_ok = exited(word) and exit_code(word) == 71
    chk("NQ2' LIMITATION at Stage 6: EOF outcome (STATUS, exit 0), no actuation",
        exited(st) and exit_code(st) == 0 and len(stat) == 1 and word_ok
        and all(q[0] != 0x06 for q in pkts),
        f"status {st:#x} pkts {[q[0] for q in pkts]}")
''',
'''    cls, spid, word = p.read_status()
    word_ok = cls == "ACCEPT" and exited(word) and exit_code(word) == 71
    chk("NQ2' LIMITATION at Stage 6: EOF outcome (STATUS on pipe, exit 0), no actuation",
        exited(st) and exit_code(st) == 0 and word_ok
        and all(q[0] not in (0x06, 0x07) for q in pkts),
        f"status {st:#x} pkts {[q[0] for q in pkts]} pipe {cls}")
''')

# ---- R8: NQ5' conversion ----
rep('''    stat = [q for q in pkts if q[0] == 0x07]
    word_ok = False
    if stat:
        word = u32(stat[0], 6)
        word_ok = exited(word) and exit_code(word) == 71
    # STRONG FORM (C0 Correction 1): with the teardown drain
    # the STATUS can no longer be reset away — it must arrive,
    # word 71, exactly one packet, exit 0. The loss branch is
    # deleted; a missing STATUS fails this case.
    chk("NQ5' LIMITATION at Stage 6: closure outcome over the residue, STATUS delivered (exit 0, word 71)",
        exited(st) and exit_code(st) == 0 and word_ok and len(pkts) == 1,
        f"status {st:#x} pkts {[q[0] for q in pkts]}")
''',
'''    cls, spid, word = p.read_status()
    word_ok = cls == "ACCEPT" and exited(word) and exit_code(word) == 71
    # STRONG FORM (C2): the STATUS travels the dedicated pipe,
    # independent of the channel residue by construction — it
    # must arrive on the pipe, word 71, exactly one record +
    # EOF, exit 0, and the channel itself must carry NOTHING.
    chk("NQ5' LIMITATION at Stage 6: closure outcome over the residue, STATUS delivered on the pipe (exit 0, word 71)",
        exited(st) and exit_code(st) == 0 and word_ok and len(pkts) == 0,
        f"status {st:#x} pkts {[q[0] for q in pkts]} pipe {cls}")
''')

# ---- R9: D-C2 conversion ----
rep('''    stat = [q for q in pkts if q[0] == 0x07]
    chk("D-C2 stall 300 ms at receive, NQ2' form: still closure outcome, exit 0",
        exited(st) and exit_code(st) == 0 and len(stat) == 1,
        f"status {st:#x} pkts {[q[0] for q in pkts]}")
''',
'''    cls, spid, word = p.read_status()
    chk("D-C2 stall 300 ms at receive, NQ2' form: still closure outcome, STATUS on pipe, exit 0",
        exited(st) and exit_code(st) == 0 and cls == "ACCEPT",
        f"status {st:#x} pkts {[q[0] for q in pkts]} pipe {cls}")
''')

# ---- R10: pipe-NONE strengtheners on three negative cases ----
rep('''    chk("P6b truncated packet: exit 8, no STATUS",
        exited(st) and exit_code(st) == 8 and all(q[0] != 0x07 for q in pkts))
''',
'''    chk("P6b truncated packet: exit 8, no STATUS",
        exited(st) and exit_code(st) == 8 and all(q[0] != 0x07 for q in pkts))
    cls, _, _ = p.read_status()
    chk("P6b pipe: no record", cls == "NONE", cls)
''')
rep('''    chk("P9 unknown message: exit 8, no STATUS",
        exited(st) and exit_code(st) == 8 and all(q[0] != 0x07 for q in pkts))
''',
'''    chk("P9 unknown message: exit 8, no STATUS",
        exited(st) and exit_code(st) == 8 and all(q[0] != 0x07 for q in pkts))
    cls, _, _ = p.read_status()
    chk("P9 pipe: no record", cls == "NONE", cls)
''')
rep('''    chk("Z1 empty record + fd at Stage 6: exit 8 (not EOF route), no STATUS",
        exited(st) and exit_code(st) == 8 and all(q[0] != 0x07 for q in pkts),
        f"status {st:#x} pkts {[q[0] for q in pkts]}")
''',
'''    chk("Z1 empty record + fd at Stage 6: exit 8 (not EOF route), no STATUS",
        exited(st) and exit_code(st) == 8 and all(q[0] != 0x07 for q in pkts),
        f"status {st:#x} pkts {[q[0] for q in pkts]}")
    cls, _, _ = p.read_status()
    chk("Z1 pipe: no record", cls == "NONE", cls)
''')
print("part 2 ok")
open(DST, "w").write(src)

# ---- R11: the K7 case block, before the summary ----
K7 = '''
# ---------------- C2-A: the zeros catalogue on the pipe (K7a) ----------------
# The zeros family at the Stage 6 wait takes the closure
# outcome; the STATUS must arrive on the pipe — exactly one
# record + EOF, word 71 — and the channel must stay empty.
# (Ancillary and data shapes at Stage 6 keep their protocol
# outcomes — violation, exit 8, pipe NONE — asserted by the
# Z1 / NQ3' / NQ4' / P9 cases above.)
for tag, zeros in (("0", 0), ("1", 1), ("2", 2), ("3", 3), ("5", 5), ("1500", 1500)):
    rid = f"PEERC2A-{tag}-20261114-001"
    p, ok = to_gate_ready(rid)
    if not ok:
        chk(f"C2-A zeros x{tag}: reached gate", False)
        p.close(); continue
    for _ in range(zeros):
        p.send(b"")
    p.sup.shutdown(socket.SHUT_WR)
    pkts = p.drain_until_eof()
    st = p.wait_exit()
    cls, spid, word = p.read_status()
    chk(f"C2-A zeros x{tag}: closure outcome, STATUS on pipe (word 71), channel empty",
        exited(st) and exit_code(st) == 0 and cls == "ACCEPT"
        and exited(word) and exit_code(word) == 71 and len(pkts) == 0,
        f"status {st:#x} pkts {len(pkts)} pipe {cls}")
    chk(f"C2-A zeros x{tag}: harness never executed", not os.path.exists(result_path(rid)))
    p.close()

# ---------------- C2-B: writer failure at the three STATUS sites (K7b) ----------------
# (i) Ordinary Stage 8, reader closed before launch: the
# harness still runs (result file), the write meets EPIPE,
# the launcher exits 17 — never 0.
rid = "PEERC2B-ORD-20261114-001"
p, ok = to_gate_ready(rid, close_status_reader=True)
chk("C2-B(i) reached gate (reader closed)", ok)
if ok:
    p.send(b"\\x05\\x00")
    r = p.recv()
    chk("C2-B(i) GATE_ACTUATED", r and r[0] and r[0][0] == 0x06)
    st = p.wait_exit()
    chk("C2-B(i) transport failure at Stage 8: exit 17, never 0",
        exited(st) and exit_code(st) == 17, f"status {st:#x}")
    chk("C2-B(i) harness still ran (result file exists)",
        os.path.exists(result_path(rid)))
p.close()

# (ii) Class-T site, reader closed: exit 17.
rid = "PEERC2B-CLT-20261114-001"
p, ok = to_gate_ready(rid, close_status_reader=True)
chk("C2-B(ii) reached gate (reader closed)", ok)
if ok:
    rc = libc.syscall(424, p.pidfd, 9, None, 0)
    chk("C2-B(ii) pidfd_send_signal delivered", rc == 0)
    p.send(b"\\x09\\x00\\x02")
    st = p.wait_exit()
    chk("C2-B(ii) transport failure at class-T: exit 17, never 0",
        exited(st) and exit_code(st) == 17, f"status {st:#x}")
    chk("C2-B(ii) harness never executed", not os.path.exists(result_path(rid)))
p.close()

# (iii) Gate-write-failure site: child killed, RELEASE meets
# a dead gate pipe. Reader closed: MSG_GATE_WRITE_FAILED
# (class EPIPE) still arrives on fd 3, launcher exits 17.
rid = "PEERC2B-GWF-20261114-001"
p, ok = to_gate_ready(rid, close_status_reader=True)
chk("C2-B(iii) reached gate (reader closed)", ok)
if ok:
    rc = libc.syscall(424, p.pidfd, 9, None, 0)
    chk("C2-B(iii) pidfd_send_signal delivered", rc == 0)
    time.sleep(0.2)
    p.send(b"\\x05\\x00")
    r = p.recv()
    okf = r and r[0] and r[0][0] == 0x0A
    chk("C2-B(iii) MSG_GATE_WRITE_FAILED still reported on fd 3", bool(okf),
        f"pkt {r[0][0] if r and r[0] else None}")
    if okf:
        chk("C2-B(iii) failure class EPIPE (1)", r[0][2] == 1, f"cls {r[0][2]}")
    st = p.wait_exit()
    chk("C2-B(iii) transport failure at gate-fail branch: exit 17, never 0",
        exited(st) and exit_code(st) == 17, f"status {st:#x}")
p.close()

# (iii)+ Companion, reader open: the fd-3 report arrives and
# the STATUS lands on the pipe carrying the SIGKILL word.
rid = "PEERC2B-GWO-20261114-001"
p, ok = to_gate_ready(rid)
chk("C2-B(iii)+ reached gate (reader open)", ok)
if ok:
    rc = libc.syscall(424, p.pidfd, 9, None, 0)
    time.sleep(0.2)
    p.send(b"\\x05\\x00")
    r = p.recv()
    chk("C2-B(iii)+ MSG_GATE_WRITE_FAILED on fd 3", bool(r and r[0] and r[0][0] == 0x0A))
    st = p.wait_exit()
    cls, spid, word = p.read_status()
    chk("C2-B(iii)+ STATUS on pipe with the SIGKILL word, exit 0",
        exited(st) and exit_code(st) == 0 and cls == "ACCEPT"
        and signalled(word) and term_sig(word) == 9,
        f"status {st:#x} pipe {cls}")
p.close()

# ---------------- C2-C: NO_EOF (K7c) ----------------
# The stub retains a writer copy past the launcher's exit:
# the receiver must report NO_EOF — the attempt is not a
# success even though a valid record arrived.
rid = "PEERC2C-20261114-001"
p, ok = to_gate_ready(rid, hold_status_writer=True)
chk("C2-C reached gate (stub holds a writer copy)", ok)
if ok:
    p.send(b"\\x05\\x00")
    r = p.recv()
    st = p.wait_exit()
    chk("C2-C launcher exit 0", exited(st) and exit_code(st) == 0)
    cls, spid, word = p.read_status()
    chk("C2-C receiver outcome NO_EOF (writer copy outlived the launcher)",
        cls == "NO_EOF", cls)
p.close()

# ---------------- C2-D: receiver state machine (K7d) ----------------
def _classify_bytes(chunks):
    r, w = os.pipe()
    for c in chunks:
        os.write(w, c)
    os.close(w)
    out = classify_status_fd(r)
    os.close(r)
    return out

cls, _ = _classify_bytes([b"\\x07" + b"\\x00" * 8])
chk("C2-D 9 bytes + EOF: TRUNCATED", cls == "TRUNCATED", cls)
_good = bytes([0x07, 0x00]) + struct.pack(">I", 4242) + struct.pack(">I", 0x2A00)
cls, _ = _classify_bytes([_good + b"\\x00"])
chk("C2-D 10 bytes + 1 extra: EXTRA", cls == "EXTRA", cls)
cls, _data = _classify_bytes([_good])
chk("C2-D exactly 10 valid bytes + EOF: ACCEPT", cls == "ACCEPT" and u32(_data, 2) == 4242, cls)
cls, _ = _classify_bytes([b"\\x08" + _good[1:]])
chk("C2-D 10 bytes, bad code: INVALID", cls == "INVALID", cls)
cls, _ = _classify_bytes([])
chk("C2-D 0 bytes + EOF: NONE", cls == "NONE", cls)

# ---------------- C2-E: STATUS descriptor preconditions (K7e) ----------------
for tag, mode in (("absent", "absent"), ("regular file", "regfile"), ("read end", "readend")):
    rid = f"PEERC2E-{tag[:3].upper()}-20261114-001"
    p = Peer(rid, status_mode=mode)
    st = p.wait_exit()
    chk(f"C2-E fd 4 {tag}: exit 13 at preconditions, nothing forked",
        exited(st) and exit_code(st) == 13, f"status {st:#x}")
    chk(f"C2-E fd 4 {tag}: harness never executed", not os.path.exists(result_path(rid)))
    p.close()

# ---------------- C2-F: the CLOEXEC procedure (K6 / K7g) ----------------
# Fork-spawned Peers run the stub's literal procedure in the
# child for BOTH mappings (fd 3 channel, fd 4 writer):
# placement, F_SETFD clear, F_GETFD read-back, exit 91 on a
# failed verification. Forms: differing (dup2), in-place
# (F_DUPFD_CLOEXEC onto the number, then clear), and the
# negative raw form (clear skipped on fd 4: exec drops it).
for tag, case, want_ok in (("differing", "differing", True),
                           ("in-place", "inplace", True),
                           ("raw", "raw", False)):
    rid = f"PEERC2F-{tag[:4].upper()}-20261114-001"
    p, ok = to_gate_ready(rid, spawn_mode="fork", cloexec_case=case)
    if want_ok:
        chk(f"C2-F {tag}: reached gate (fd 3 + fd 4 procedure verified)", ok)
        if ok:
            p.send(b"\\x05\\x00")
            r = p.recv()
            st = p.wait_exit()
            cls, spid, word = p.read_status()
            chk(f"C2-F {tag}: full run, STATUS on pipe, exit 0",
                exited(st) and exit_code(st) == 0 and cls == "ACCEPT",
                f"status {st:#x} pipe {cls}")
    else:
        st = p.wait_exit()
        chk("C2-F raw: exec dropped fd 4 (CLOEXEC left set), launcher exit 13",
            exited(st) and exit_code(st) == 13, f"status {st:#x}")
        chk("C2-F raw: harness never executed", not os.path.exists(result_path(rid)))
    p.close()

print(f"peer: {total - fails}/{total} PASS")'''
rep('print(f"peer: {total - fails}/{total} PASS")', K7)
print("part 3 ok")
open(DST, "w").write(src)
print("wrote", DST, len(src.splitlines()), "lines")

# ---- R12: P3b — assert BOTH lawful branches of the Stage 4 race ----
rep('''rid = "PEERP3-20261113-002"
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
''',
'''rid = "PEERP3-20261113-002"
p = Peer(rid, env_extra={"PILOT_HOOK_FAIL_CLOSE_RANGE": "1"})
p.request()
# Two lawful branches, decided by a genuine race: if the
# child is still alive at the launcher's Stage 4 WNOHANG
# poll, the pidfd handoff is sent and the peer drives the
# R-3 path (ACK 3 -> ABORT reason 3). If the child has
# already died and been reaped at that poll, the launcher
# sends ABORT reason 1 (CHILD_LOST_IN_ESTABLISHMENT, with
# the word) directly and exits 3 — no handoff exists on
# that branch. Both branches are asserted in full; which
# one a run takes is scheduling, not correctness. (The C2
# suite's first five-run series hit branch B once in five;
# the C1 form of this case asserted branch A only.)
r0 = p.recv()
if r0 and r0[0] and r0[0][0] == 0x02 and len(r0[1]) == 1:
    p.child_pid = u32(r0[0], 2)
    p.start_time = u64(r0[0], 6)
    p.pidfd = r0[1][0]
    chk("P3b branch A: handoff received", True)
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
elif r0 and r0[0] and r0[0][0] == 0x09 and len(r0[0]) == 7:
    chk("P3b branch B: direct ABORT received (child lost in establishment)", True)
    word = u32(r0[0], 3)
    chk("P3b ABORT reason CHILD_LOST_IN_ESTABLISHMENT (1)", r0[0][2] == 1,
        f"reason {r0[0][2]}")
    chk("P3b ABORT word == child exit 73 (setup failed)",
        exited(word) and exit_code(word) == 73, f"word {word:#x}")
    st = p.wait_exit()
    chk("P3b launcher exit 3", exited(st) and exit_code(st) == 3, f"status {st:#x}")
    chk("P3b harness never executed", not os.path.exists(result_path(rid)))
else:
    chk("P3b first packet is a handoff or a direct ABORT", False,
        f"got {r0[0][0] if r0 and r0[0] else r0}")
p.close()
''')
print("part 4 ok")
open(DST, "w").write(src)
print("rewrote", DST, len(src.splitlines()), "lines")
