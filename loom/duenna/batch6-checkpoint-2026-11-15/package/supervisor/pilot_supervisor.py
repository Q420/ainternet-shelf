#!/usr/bin/env python3
"""PILOT SUPERVISOR — Stage 5 Build Spec Rev 26 §3.5 points 2-9,
as amended by the STATUS-pipe amendment (fd 4) and whole-plan
Rev 8 Part B (launch-evidence records).

Single-purpose programme, run as the OS identity
pilot-supervisor. It owns issuance, the commitments store, its
session records and its launch-evidence records. It spawns the
custody launcher (the harness child's OS parent and sole
waitpid() holder while it lives), validates the pidfd handoff,
observes the gate, computes every committed value itself from
the run's record file, and closes the attempt on the facts —
never on a caller's word.

Protocol constants cross-checked against launcher-c3.c
(sha256 001543f3...) at build time by check_abort_reasons.py:
message codes 0x01..0x0A; ABORT reasons 1..7.
"""
import argparse
import ctypes
import errno
import hashlib
import json
import os
import pwd
import select
import signal
import socket
import stat
import struct
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pilot_jcs  # pinned at Batch 0 (sha256 8a131cfc...)

libc = ctypes.CDLL(None, use_errno=True)

# ---- protocol catalogue (§3.5 point 3, as amended) ----
MSG_LAUNCH_REQUEST = 0x01
MSG_PIDFD_HANDOFF = 0x02
MSG_HANDOFF_ACK = 0x03
MSG_GATE_READY = 0x04
MSG_RELEASE = 0x05
MSG_GATE_ACTUATED = 0x06
MSG_STATUS = 0x07          # dedicated STATUS pipe ONLY (amendment)
MSG_STATUS_ACK = 0x08
MSG_ABORT = 0x09
MSG_GATE_WRITE_FAILED = 0x0A

# ABORT reasons — identical numbering to launcher-c3.c RSN_*.
ABORT_REASONS = {
    1: "CHILD_LOST_IN_ESTABLISHMENT",
    2: "CHILD_TERMINATED_PRE_RELEASE",
    3: "CHILD_TERMINATED_AT_HANDOFF",
    4: "IDENTITY_RECHECK_FAILED",
    5: "SETTLING_FAILED",
    6: "READINESS_UNVERIFIABLE",
    7: "SUPERVISOR_ABORT",
}
REASON_BY_NAME = {v: k for k, v in ABORT_REASONS.items()}
# reasons whose launcher->supervisor form carries a raw
# wait_status word (7-byte packet); all others are 3-byte.
WORD_CARRYING_REASONS = {1, 3}

READINESS_DEADLINE_S = 1.0        # §3.5 readiness contract
PRE_RELEASE_CLOSE_BOUND_S = 5.0   # class-T bound
CLOSE_OUT_WINDOW_S = 5.0          # S9 launcher-exit window
STATUS_POST_REAP_GRACE_S = 2.0    # STATUS receiver NO_EOF grace
CHANNEL_FD = 3                    # launcher's channel end
STATUS_FD = 4                     # launcher's STATUS pipe write end

F_GETFD, F_SETFD, F_DUPFD_CLOEXEC, FD_CLOEXEC = 1, 2, 1030, 1


def utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> bytes:
    return pilot_jcs.canonicalise(value)


# ---- strict wait_status validation (§3.5 point 3) ----
def validate_wait_status(word):
    """-> (valid, decode). Accepted encodings ONLY: exited
    (bits 0-7 == 0, bits 8-15 = exit code) or signalled
    (bits 0-6 = signal 1..64, bit 7 = core flag, bits 8-15
    == 0); bits 16-31 must be zero in every accepted case.
    Anything else is rejected; the word is recorded verbatim
    by the caller and the classification stays UNRESOLVED."""
    if not isinstance(word, int) or word < 0 or word > 0xFFFFFFFF:
        return False, {"reason": "word out of u32 range"}
    if word & 0xFFFF0000:
        return False, {"reason": "bits 16-31 nonzero"}
    low = word & 0xFF
    if low == 0:
        return True, {"kind": "exited", "exit_code": (word >> 8) & 0xFF}
    sig = word & 0x7F
    if low == 0x7F or low == 0xFF:
        return False, {"reason": "stopped/continued encoding"}
    if 1 <= sig <= 64 and ((word >> 8) & 0xFF) == 0:
        return True, {"kind": "signalled", "signal": sig,
                      "core_dump": bool(word & 0x80)}
    return False, {"reason": "no accepted encoding matches"}


def proc_start_time_and_ppid(pid):
    """-> (start_time, ppid) from /proc/<pid>/stat field 22 /
    field 4, or None if the process is gone/unreadable."""
    try:
        with open(f"/proc/{pid}/stat", "rb") as fh:
            data = fh.read().decode("utf-8", "replace")
    except OSError:
        return None
    rp = data.rfind(")")
    if rp < 0:
        return None
    fields = data[rp + 2:].split()
    # fields[0] is field 3 (state); ppid = field 4 -> idx 1;
    # starttime = field 22 -> idx 19.
    try:
        return int(fields[19]), int(fields[1])
    except (IndexError, ValueError):
        return None


def proc_cap_masks(pid):
    """-> dict of raw CapEff/CapPrm/CapAmb hex strings from
    /proc/<pid>/status, or None on any failure."""
    try:
        with open(f"/proc/{pid}/status", "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return None
    out = {}
    for line in text.splitlines():
        for key in ("CapEff", "CapPrm", "CapAmb"):
            if line.startswith(key + ":"):
                out[key] = line.split(":", 1)[1].strip()
    if set(out) != {"CapEff", "CapPrm", "CapAmb"}:
        return None
    return out


def pidfd_termination_observed(pidfd):
    """One zero-time readiness poll. -> True (termination
    observed), False (no events: not observed at this
    instant), or None (poll failure: fail closed; the caller
    records the outcome).

    Kernel mask reality (probed on the room kernel,
    2026-11-14): an exited-but-unreaped target reports
    POLLIN alone (0x1); once the parent (the launcher) has
    reaped it, the mask is POLLIN|POLLHUP (0x11). POLLIN is
    therefore the termination bit in either case; POLLHUP
    merely adds that the process is fully gone. POLLERR /
    POLLNVAL without POLLIN is a poll failure."""
    poller = select.poll()
    poller.register(pidfd, select.POLLIN)
    try:
        events = poller.poll(0)
    except InterruptedError:
        return None
    except OSError:
        return None
    if not events:
        return False
    mask = events[0][1]
    if mask & select.POLLIN:
        return True
    return None


def readiness_poll(pidfd):
    """The §3.5 readiness operation: zero-time polls, EINTR
    re-polled against READINESS_DEADLINE (CLOCK_MONOTONIC
    from entry). -> "TERMINATED" | "NOT_OBSERVED" |
    "POLL_INCOMPLETE" | "POLL_FAILED"."""
    deadline = time.monotonic() + READINESS_DEADLINE_S
    while True:
        poller = select.poll()
        poller.register(pidfd, select.POLLIN)
        try:
            events = poller.poll(0)
        except InterruptedError:
            if time.monotonic() >= deadline:
                return "POLL_INCOMPLETE"
            continue
        except OSError:
            return "POLL_FAILED"
        if not events:
            return "NOT_OBSERVED"
        mask = events[0][1]
        # POLLIN is the termination bit; POLLHUP may
        # accompany it once the launcher has reaped the
        # child (probed kernel behaviour, 2026-11-14).
        # POLLERR/POLLNVAL fail closed.
        if mask & select.POLLIN and not mask & (
                select.POLLERR | select.POLLNVAL):
            return "TERMINATED"
        return "POLL_FAILED"


# ---- configuration ----
class Config:
    def __init__(self, args):
        self.run_id = args.run_id
        self.launcher_path = args.launcher
        self.runs_root = args.runs_root
        self.commitments_dir = args.commitments
        self.log_dir = args.log_dir
        self.evidence_dir = args.evidence_dir
        self.identity_records = args.identity_records
        self.harness_uid = pwd.getpwnam("pilot-harness").pw_uid
        self.harness_gid = pwd.getpwnam("pilot-harness").pw_gid
        self.supervisor_uid = pwd.getpwnam("pilot-supervisor").pw_uid
        self.supervisor_gid = pwd.getpwnam("pilot-supervisor").pw_gid
        self.watchdog_s = args.watchdog
        self.demo_delay_point = args.demo_delay_point
        self.demo_delay_s = args.demo_delay_s
        self.env_extra = {}
        if args.hook_env:
            for pair in args.hook_env:
                key, _, val = pair.partition("=")
                self.env_extra[key] = val

    @property
    def record_path(self):
        return os.path.join(self.runs_root, self.run_id,
                            "run-record.jsonl")

    @property
    def session_path(self):
        return os.path.join(self.log_dir, self.run_id + ".session.jsonl")


class SessionRecord:
    """The supervisor's own session record: one canonical
    JSON line per fact, in the supervisor-owned run-log area
    (never in commitments/). Facts are never overwritten;
    each entry carries its source class."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.seq = 0
        os.makedirs(cfg.log_dir, exist_ok=True)
        self._fh = open(cfg.session_path, "w", encoding="utf-8")

    def add(self, kind, **facts):
        self.seq += 1
        entry = {"seq": self.seq, "run_id": self.cfg.run_id,
                 "at_utc": utc_now(), "kind": kind}
        entry.update(facts)
        self._fh.write(canonical(entry).decode("utf-8") + "\n")
        self._fh.flush()
        return entry

    def close(self):
        self._fh.close()


# ---- descriptor placement (the contract procedure) ----
def place_fd(src, target):
    """Land src on target in the forked child, then clear
    FD_CLOEXEC via F_SETFD and verify by F_GETFD read-back.
    Any failure exits 91 pre-exec: the launch is rejected,
    never continued on an unverified descriptor."""
    if src == target:
        # same-descriptor branch: F_DUPFD_CLOEXEC to a scratch
        # slot is unnecessary; clear in place and read back.
        pass
    elif src > 0:
        os.dup2(src, target)
    fl = libc.fcntl(target, F_GETFD)
    if fl < 0:
        os._exit(91)
    if libc.fcntl(target, F_SETFD, fl & ~FD_CLOEXEC) != 0:
        os._exit(91)
    rb = libc.fcntl(target, F_GETFD)
    if rb < 0 or (rb & FD_CLOEXEC):
        os._exit(91)


def file_caps_empty(path):
    """True iff the file carries no capability xattr set."""
    try:
        val = os.getxattr(path, "security.capability")
    except OSError as exc:
        if exc.errno in (errno.ENODATA, errno.ENOTSUP):
            return True
        return False
    return len(val) == 0


def object_identity(path):
    """-> dict(dev, ino, mode) of the resolved object, or
    None if it fails the exec condition (missing, not a
    regular file, setuid/setgid bit set, file caps present)."""
    try:
        resolved = os.path.realpath(path)
        st = os.stat(resolved)
    except OSError:
        return None
    if not stat.S_ISREG(st.st_mode):
        return None
    if st.st_mode & 0o6000:
        return None
    if not file_caps_empty(resolved):
        return None
    return {"path": resolved, "dev": st.st_dev, "ino": st.st_ino,
            "mode": st.st_mode & 0o7777}


class Supervisor:
    def __init__(self, cfg):
        self.cfg = cfg
        self.rec = SessionRecord(cfg)
        self.chan = None            # supervisor's channel end
        self.status_r = None        # STATUS pipe read end
        self.launcher_pid = None
        self.launcher_reaped = False
        self.launcher_exit = None   # raw waitpid status word
        self.child_pid = None
        self.child_start = None
        self.pidfd = None
        self.chan_eof = False
        self.eof_state = None
        self.state = "S0"
        self.status_buf = b""
        self.status_eof = False
        self.status_record = None   # (pid, word) once validated
        self.status_raw = None      # classification detail
        self.term_observed = False
        self.term_at = None
        self.gate_actuated = False
        self.gate_write_failed = None
        self.start_issued = False
        self.final_issued = False
        self.record_offset = 0
        self.record_partial = b""
        self.events_seen = 0
        self.last_event_sha = None
        self.terminal_event = None
        self.abort_sent = None
        self.abort_received = None
        self.class_t = False
        self.class_t_deadline = None
        self.outcome = None
        self._held = []  # packets drained during a demo delay

    # ---------- Stage 1: standing verifications ----------
    def stage1_checks(self):
        cfg = self.cfg
        checks = {}
        # (a) retained stdio destinations
        def fd_target(fd):
            try:
                return os.readlink(f"/proc/self/fd/{fd}")
            except OSError:
                return None

        def fd_flags(fd):
            return libc.fcntl(fd, 3)  # F_GETFL

        t0 = fd_target(0)
        checks["fd0_devnull"] = (t0 == "/dev/null"
                                 and (fd_flags(0) & os.O_ACCMODE) == os.O_RDONLY)
        log_target = os.path.join(cfg.log_dir, cfg.run_id + ".stdio.log")
        t1, t2 = fd_target(1), fd_target(2)
        checks["fd1_append_log"] = (
            t1 == log_target
            and (fd_flags(1) & os.O_APPEND) != 0
            and (fd_flags(1) & os.O_ACCMODE) in (os.O_WRONLY, os.O_RDWR))
        checks["fd2_same_log"] = (t2 == log_target
                                  and (fd_flags(2) & os.O_APPEND) != 0)
        # (b) exec condition + identity records
        expected = {}
        if cfg.identity_records:
            with open(cfg.identity_records, "r", encoding="utf-8") as fh:
                expected = json.load(fh)
        for name in ("harness", "interpreter"):
            ident = object_identity(expected[name]["path"]) if name in expected else None
            ok = ident is not None and all(
                ident[k] == expected[name][k] for k in ("dev", "ino", "mode"))
            checks[f"identity_{name}"] = ok
            if ident is not None:
                checks[f"identity_{name}_observed"] = ident
            elif name in expected:
                # SE-7 (ix): a refused launch records BOTH
                # identity records — the freeze's (in the
                # identity-records file) and the observed
                # object's raw stat, even when the object
                # fails the exec condition itself.
                try:
                    rst = os.stat(os.path.realpath(
                        expected[name]["path"]))
                    checks[f"identity_{name}_observed_raw"] = {
                        "dev": rst.st_dev, "ino": rst.st_ino,
                        "mode": rst.st_mode & 0o7777,
                        "setuid": bool(rst.st_mode & 0o4000),
                        "setgid": bool(rst.st_mode & 0o2000)}
                except OSError as exc:
                    checks[f"identity_{name}_observed_raw"] = {
                        "error": str(exc)}
        # (c) custody: commitments dir ownership/mode; no open
        # writable descriptor into commitments/ or the
        # issuance record at launch time.
        st = os.stat(cfg.commitments_dir)
        checks["commitments_custody"] = (
            st.st_uid == cfg.supervisor_uid
            and (st.st_mode & 0o777) == 0o700)
        writable = []
        for fdname in os.listdir("/proc/self/fd"):
            try:
                fd = int(fdname)
            except ValueError:
                continue
            target = fd_target(fd)
            if target and target.startswith(cfg.commitments_dir):
                fl = fd_flags(fd)
                if (fl & os.O_ACCMODE) in (os.O_WRONLY, os.O_RDWR):
                    writable.append(fd)
        checks["no_writable_commitments_fd"] = not writable
        self.rec.add("STAGE1_CHECKS", checks=checks,
                     passed=all(v is True for k, v in checks.items()
                                if not k.endswith("_observed")))
        return all(v is True for k, v in checks.items()
                   if not k.endswith("_observed"))


    # ---------- spawn (Stage 1/2 of §3.5 point 3) ----------
    def spawn_launcher(self):
        cfg = self.cfg
        sup_end, lch_end = socket.socketpair(socket.AF_UNIX,
                                             socket.SOCK_SEQPACKET)
        st_r, st_w = os.pipe2(os.O_CLOEXEC)
        lch_fd = lch_end.fileno()
        pid = os.fork()
        if pid == 0:
            try:
                place_fd(lch_fd, CHANNEL_FD)
                place_fd(st_w, STATUS_FD)
                # close every other inherited descriptor: the
                # supervisor's channel end, both pipe ends'
                # originals, and anything else that rode in.
                keep = {0, 1, 2, CHANNEL_FD, STATUS_FD}
                try:
                    names = os.listdir("/proc/self/fd")
                except OSError:
                    names = []
                for name in names:
                    try:
                        fd = int(name)
                    except ValueError:
                        continue
                    if fd not in keep:
                        try:
                            os.close(fd)
                        except OSError:
                            pass
                env = dict(cfg.env_extra)
                os.execve(cfg.launcher_path,
                          [cfg.launcher_path, cfg.run_id], env)
            except Exception:
                os._exit(92)
            os._exit(92)
        # parent: retain our channel end + the pipe read end;
        # close the launcher's ends at once.
        self.launcher_pid = pid
        self.chan = sup_end
        self.chan.setblocking(False)
        lch_end.close()
        os.close(st_w)
        self.status_r = st_r
        os.set_blocking(self.status_r, False)
        # self-audit: no copy of the STATUS pipe WRITER may
        # remain in this process (a retained writer defeats
        # the pipe's EOF). Identify the pipe by its inode.
        pipe_ino = os.fstat(self.status_r).st_ino
        offenders = []
        for name in os.listdir("/proc/self/fd"):
            try:
                fd = int(name)
            except ValueError:
                continue
            if fd == self.status_r:
                continue
            try:
                fst = os.fstat(fd)
            except OSError:
                continue
            if fst.st_ino == pipe_ino:
                fl = libc.fcntl(fd, 3)  # F_GETFL
                if (fl & os.O_ACCMODE) in (os.O_WRONLY, os.O_RDWR):
                    offenders.append(fd)
        self.rec.add("LAUNCHER_SPAWNED", launcher_pid=pid,
                     status_writer_self_audit=(
                         "CLEAN" if not offenders else offenders))
        if offenders:
            return False
        self.rec.add("STATE", state="S0")
        return True

    def send_packet(self, data, fds=()):
        try:
            if fds:
                self.chan.sendmsg(
                    [data],
                    [(socket.SOL_SOCKET, socket.SCM_RIGHTS,
                      struct.pack("i" * len(fds), *fds))])
            else:
                self.chan.sendall(data)
            return True
        except OSError as exc:
            self.rec.add("SEND_FAILED", bytes=list(data[:2]),
                         error=str(exc))
            return False

    def send_launch_request(self):
        cfg = self.cfg
        pkt = struct.pack(">BBIII", MSG_LAUNCH_REQUEST, 0,
                          os.getpid(), cfg.harness_uid,
                          cfg.harness_gid) + cfg.run_id.encode()
        ok = self.send_packet(pkt)
        self.rec.add("LAUNCH_REQUEST_SENT", ok=ok,
                     expected_supervisor_pid=os.getpid())
        if ok:
            self.state = "S1"
        return ok

    def send_abort(self, reason, cls):
        pkt = struct.pack(">BBB", MSG_ABORT, 0, reason)
        ok = self.send_packet(pkt)
        self.abort_sent = {"reason": reason,
                           "reason_name": ABORT_REASONS[reason],
                           "class": cls, "delivered": ok}
        self.rec.add("ABORT_SENT", **self.abort_sent)
        if cls == "T":
            self.class_t = True
            self.class_t_deadline = (time.monotonic()
                                     + PRE_RELEASE_CLOSE_BOUND_S)
        return ok

    # ---------- channel receive (drained-EOF discipline) ----------
    def drain_channel(self):
        """Consume every queued packet before EOF is
        established. Returns a list of (data, [fds]) packets
        received in this drain; sets self.chan_eof when the
        drained stream reaches end-of-stream."""
        packets = []
        while True:
            try:
                data, anc, flags, _ = self.chan.recvmsg(
                    4096, socket.CMSG_SPACE(16))
            except BlockingIOError:
                break
            except InterruptedError:
                continue
            except ConnectionResetError:
                # the peer is gone and the queue is drained:
                # end-of-stream, as in the C0 peer receiver
                if not self.chan_eof:
                    self.chan_eof = True
                    self.eof_state = self.state
                    self.rec.add("LAUNCHER_EXIT_OBSERVED",
                                 source="channel RESET (drained)",
                                 state_at_observation=self.state)
                break
            except OSError as exc:
                self.rec.add("CHANNEL_RECV_ERROR", error=str(exc))
                break
            if data == b"" and not anc:
                # drained end-of-stream (queued packets were
                # consumed above, in order, before this point)
                if not self.chan_eof:
                    self.chan_eof = True
                    self.eof_state = self.state
                    self.rec.add("LAUNCHER_EXIT_OBSERVED",
                                 source="channel EOF (drained)",
                                 state_at_observation=self.state)
                break
            fds = []
            for level, typ, dat in anc:
                if level == socket.SOL_SOCKET and typ == socket.SCM_RIGHTS:
                    fds = list(struct.unpack(
                        "i" * (len(dat) // 4), dat))
            if flags & getattr(socket, "MSG_CTRUNC", 0):
                for fd in fds:
                    os.close(fd)
                self.rec.add("PROTOCOL_VIOLATION",
                             detail="MSG_CTRUNC on receive",
                             packet=list(data[:8]))
                continue
            packets.append((data, fds, flags))
        return packets

    # ---------- STATUS pipe receiver ----------
    def drain_status_pipe(self):
        if self.status_r is None or self.status_eof:
            return
        while True:
            try:
                chunk = os.read(self.status_r, 4096)
            except BlockingIOError:
                return
            except InterruptedError:
                continue
            except OSError:
                return
            if chunk == b"":
                self.status_eof = True
                return
            self.status_buf += chunk
            if len(self.status_buf) > 10:
                return  # EXTRA: classification at finalise

    def finalise_status(self):
        """Classify the pipe's contents once the launcher has
        been reaped (the NO_EOF rule is event-bound: post-
        reap, EOF must be reachable within the grace)."""
        deadline = time.monotonic() + STATUS_POST_REAP_GRACE_S
        while not self.status_eof and time.monotonic() < deadline:
            self.drain_status_pipe()
            if self.status_eof:
                break
            time.sleep(0.02)
        data = self.status_buf
        if not self.status_eof and len(data) <= 10:
            cls = "NO_EOF"
        elif len(data) == 0:
            cls = "NONE"
        elif len(data) < 10:
            cls = "TRUNCATED"
        elif len(data) > 10:
            cls = "EXTRA"
        elif data[0] != MSG_STATUS or data[1] != 0:
            cls = "INVALID"
        else:
            cls = "ACCEPT"
        detail = {"classification": cls, "bytes": len(data)}
        if cls == "ACCEPT":
            pid = struct.unpack(">I", data[2:6])[0]
            word = struct.unpack(">I", data[6:10])[0]
            valid, decode = validate_wait_status(word)
            detail.update({"child_pid": pid, "raw_word": word,
                           "word_valid": valid, "decode": decode})
            if pid == self.child_pid and valid:
                self.status_record = (pid, word)
                detail["accepted"] = True
            else:
                detail["accepted"] = False
                if pid != self.child_pid:
                    detail["reject_reason"] = "child_pid mismatch"
                else:
                    detail["reject_reason"] = "invalid wait_status word"
        self.status_raw = detail
        self.rec.add("STATUS_RECORD", **detail)
        return detail

    # ---------- launcher reaping ----------
    def poll_launcher(self):
        if self.launcher_pid is None or self.launcher_reaped:
            return
        try:
            wpid, status = os.waitpid(self.launcher_pid,
                                       os.WNOHANG)
        except ChildProcessError:
            self.launcher_reaped = True
            return
        if wpid == self.launcher_pid:
            self.launcher_reaped = True
            self.launcher_exit = status
            self.rec.add("LAUNCHER_EXIT", raw_wait_status=status,
                         exited=os.WIFEXITED(status),
                         exit_code=(os.WEXITSTATUS(status)
                                    if os.WIFEXITED(status) else None),
                         signalled=os.WIFSIGNALED(status),
                         signal=(os.WTERMSIG(status)
                                 if os.WIFSIGNALED(status) else None))

    # ---------- record file watching + issuance ----------
    def _record_file_bytes(self):
        try:
            with open(self.cfg.record_path, "rb") as fh:
                return fh.read()
        except OSError:
            return None

    def poll_record(self):
        """Parse newly completed (newline-terminated) events
        from the run's record file; issue START on the first
        RUN_STARTED. The supervisor parses the file itself —
        no value is taken from the harness's word."""
        data = self._record_file_bytes()
        if data is None:
            return
        if len(data) < self.record_offset:
            return
        new = data[self.record_offset:]
        self.record_partial += new
        self.record_offset = len(data)
        while b"\n" in self.record_partial:
            line, self.record_partial = self.record_partial.split(b"\n", 1)
            if not line.strip():
                continue
            try:
                event = json.loads(line.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                continue
            self.events_seen += 1
            self.last_event_sha = event.get("event_sha256")
            if event.get("event_type") == "RUN_STARTED" and not self.start_issued:
                self._issue_start(event)
            if event.get("event_type") in ("RUN_CLOSED", "RUN_STOPPED"):
                self.terminal_event = event

    def _write_receipt(self, kind, receipt):
        cfg = self.cfg
        name = {"START": ".start.json", "TERMINAL": ".terminal.json",
                "CRASH": ".crash.json"}[kind]
        path = os.path.join(cfg.commitments_dir, cfg.run_id + name)
        blob = canonical(receipt)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.write(fd, blob)
            os.fsync(fd)
        finally:
            os.close(fd)
        os.chmod(path, 0o600)
        receipt_sha = sha256_hex(blob)
        entry = {"run_id": cfg.run_id, "kind": kind,
                 "issued_at_utc": receipt["issued_at_utc"],
                 "receipt_sha256": receipt_sha}
        ipath = os.path.join(cfg.commitments_dir,
                             "issuance-record.jsonl")
        fd = os.open(ipath, os.O_WRONLY | os.O_CREAT | os.O_APPEND,
                     0o600)
        try:
            os.write(fd, canonical(entry) + b"\n")
            os.fsync(fd)
        finally:
            os.close(fd)
        os.chmod(ipath, 0o600)
        self.rec.add("ISSUANCE", receipt_kind=kind,
                     receipt_sha256=receipt_sha, receipt_path=path)
        return receipt_sha

    def _issue_start(self, event):
        payload = event.get("payload")
        genesis = event.get("prev_event_sha256")
        recomputed_genesis = sha256_hex(canonical(payload))
        body = {k: v for k, v in event.items() if k != "event_sha256"}
        recomputed_event = sha256_hex(canonical(body))
        receipt = {
            "run_id": self.cfg.run_id,
            "kind": "START",
            "issued_at_utc": utc_now(),
            "genesis_sha256": genesis,
            "run_started_event_sha256": event.get("event_sha256"),
            "pinned_input_block_sha256": sha256_hex(canonical(payload)),
        }
        self.rec.add("START_SELF_COMPUTATION",
                     genesis_in_file=genesis,
                     genesis_recomputed=recomputed_genesis,
                     genesis_match=(genesis == recomputed_genesis),
                     event_sha_match=(
                         recomputed_event == event.get("event_sha256")))
        self._write_receipt("START", receipt)
        self.start_issued = True

    def issue_final(self, termination_basis):
        """TERMINAL if a terminal event was flushed, else
        CRASH over the partial file exactly as it lies."""
        if self.final_issued:
            return
        data = self._record_file_bytes()
        if data is None:
            data = b""
        file_sha = sha256_hex(data)
        if self.terminal_event is not None:
            receipt = {
                "run_id": self.cfg.run_id,
                "kind": "TERMINAL",
                "issued_at_utc": utc_now(),
                "terminal_event_type": self.terminal_event.get("event_type"),
                "final_event_sha256": self.terminal_event.get("event_sha256"),
                "event_count": self.events_seen,
                "record_file_sha256": file_sha,
            }
            self._write_receipt("TERMINAL", receipt)
        else:
            receipt = {
                "run_id": self.cfg.run_id,
                "kind": "CRASH",
                "issued_at_utc": utc_now(),
                "record_file_sha256": file_sha,
                "event_count": self.events_seen,
                "final_event_sha256": self.last_event_sha,
                "termination_observed": termination_basis,
            }
            self._write_receipt("CRASH", receipt)
        self.final_issued = True


    # ---------- event tick ----------
    def _tick(self):
        packets = self.drain_channel()
        self.drain_status_pipe()
        self.poll_record()
        self.poll_launcher()
        if self.pidfd is not None and not self.term_observed:
            if pidfd_termination_observed(self.pidfd) is True:
                self.term_observed = True
                self.term_at = utc_now()
                self.rec.add("TERMINATION_OBSERVED",
                             source="pidfd (supervisor-observed)",
                             child_pid=self.child_pid, at=self.term_at)
        return packets

    def _sleep_tick(self, seconds=0.02):
        time.sleep(seconds)

    # ---------- packet parsing ----------
    def _parse_abort(self, data):
        if len(data) == 3 and data[1] == 0:
            reason = data[2]
            return {"reason": reason,
                    "reason_name": ABORT_REASONS.get(reason),
                    "word": None}
        if len(data) == 7 and data[1] == 0:
            reason = data[2]
            word = struct.unpack(">I", data[3:7])[0]
            return {"reason": reason,
                    "reason_name": ABORT_REASONS.get(reason),
                    "word": word}
        return None

    def _record_abort_received(self, data):
        parsed = self._parse_abort(data)
        if parsed is None or parsed["reason_name"] is None:
            self.rec.add("PROTOCOL_VIOLATION",
                         detail="malformed ABORT packet",
                         packet=list(data))
            return None
        entry = {"reason": parsed["reason"],
                 "reason_name": parsed["reason_name"],
                 "class": "F"}
        if parsed["word"] is not None:
            valid, decode = validate_wait_status(parsed["word"])
            entry.update({"raw_word": parsed["word"],
                          "word_valid": valid, "decode": decode,
                          "word_class": "LAUNCHER-REPORTED"})
        self.abort_received = entry
        self.rec.add("ABORT_RECEIVED", **entry)
        return entry

    # ---------- handoff validation (Stage 4) ----------
    def validate_handoff(self, data, fds):
        cfg = self.cfg
        detail = {}
        if len(data) != 14 or data[0] != MSG_PIDFD_HANDOFF or data[1] != 0:
            return 1, {"failure": "handoff framing invalid"}
        if len(fds) != 1:
            return 1, {"failure": f"ancillary count {len(fds)} != 1"}
        pidfd = fds[0]
        self.child_pid = struct.unpack(">I", data[2:6])[0]
        self.child_start = struct.unpack(">Q", data[6:14])[0]
        detail["child_pid"] = self.child_pid
        detail["claimed_start_time"] = self.child_start
        # (1) descriptor target via fdinfo
        try:
            with open(f"/proc/self/fdinfo/{pidfd}", "r",
                      encoding="utf-8") as fh:
                fdinfo = fh.read()
        except OSError as exc:
            return 2, {**detail, "failure": f"fdinfo unreadable: {exc}"}
        target = None
        for line in fdinfo.splitlines():
            if line.startswith("Pid:"):
                target = int(line.split(":", 1)[1].strip())
        detail["fdinfo_target"] = target
        if target != self.child_pid:
            return 1, {**detail, "failure": "fdinfo target mismatch"}
        # (2) instance binding via /proc/<pid>/stat
        binding = proc_start_time_and_ppid(self.child_pid)
        if binding is None:
            return 2, {**detail, "failure": "child /proc entry gone"}
        start_time, ppid = binding
        detail["observed_start_time"] = start_time
        detail["observed_ppid"] = ppid
        if start_time != self.child_start or ppid != self.launcher_pid:
            return 1, {**detail, "failure": "instance binding mismatch"}
        # (3) readiness
        outcome = readiness_poll(pidfd)
        detail["readiness"] = outcome
        if outcome == "TERMINATED":
            self.term_observed = True
            self.term_at = utc_now()
            self.rec.add("TERMINATION_OBSERVED",
                         source="pidfd readiness at handoff validation",
                         child_pid=self.child_pid, at=self.term_at)
            return 3, detail
        if outcome != "NOT_OBSERVED":
            return 1, {**detail,
                       "failure": f"readiness poll outcome {outcome}"}
        self.pidfd = pidfd
        return 0, detail

    # ---------- Part B capability observation ----------
    def part_b_observation(self):
        cfg = self.cfg
        observed_at = utc_now()
        record = {
            "run_id": cfg.run_id,
            "attempt_id": cfg.run_id + "-A1",
            "issuance_reference": None,  # none exists pre-release
            "reader": "pilot-supervisor",
            "observed_at_utc": observed_at,
            "launcher_pid": self.launcher_pid,
            "child_pid": self.child_pid,
            "child_start_time": self.child_start,
            "launcher_binding": None,
            "processes": {},
            "expected": {"CapEff": "0000000000000000",
                         "CapPrm": "0000000000000000",
                         "CapAmb": "0000000000000000"},
        }
        binding = proc_start_time_and_ppid(self.launcher_pid)
        if binding is not None:
            record["launcher_binding"] = {
                "start_time": binding[0], "ppid": binding[1]}
        ok = True
        failure = None
        for label, pid in (("launcher", self.launcher_pid),
                           ("child", self.child_pid)):
            path = f"/proc/{pid}/status"
            masks = proc_cap_masks(pid)
            entry = {"pid": pid, "status_path": path, "masks": masks}
            if masks is None:
                ok = False
                failure = f"{label} /proc observation unavailable/malformed"
            else:
                for key, raw in masks.items():
                    try:
                        if int(raw, 16) != 0:
                            ok = False
                            failure = f"{label} {key} nonzero: {raw}"
                    except ValueError:
                        ok = False
                        failure = f"{label} {key} malformed: {raw}"
            record["processes"][label] = entry
        record["comparison"] = "PASS" if ok else "FAIL"
        if failure:
            record["failure"] = failure
        os.makedirs(cfg.evidence_dir, exist_ok=True)
        path = os.path.join(cfg.evidence_dir,
                            cfg.run_id + ".launch-evidence.json")
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.write(fd, canonical(record))
            os.fsync(fd)
        finally:
            os.close(fd)
        self.rec.add("LAUNCH_EVIDENCE", path=path,
                     comparison=record["comparison"],
                     failure=failure)
        return ok, record

    # ---------- class-T wait ----------
    def class_t_wait(self):
        """After a class-T ABORT: the launcher owes exactly
        one STATUS (on the pipe) — or the drained channel
        reaches EOF without one (PRE_RELEASE_LAUNCHER_LOST)
        — or the bound expires
        (PRE_RELEASE_ABORT_STATUS_UNREPORTED)."""
        while True:
            packets = self._tick()
            for data, fds, _flags in packets:
                for fd in fds:
                    os.close(fd)
                if data and data[0] == MSG_GATE_READY:
                    self.rec.add("GATE_READY_INERT",
                                 note="received after class-T commitment")
                elif data and data[0] == MSG_ABORT:
                    self._record_abort_received(data)
                elif data:
                    self.rec.add("PROTOCOL_VIOLATION",
                                 detail="message after class-T ABORT",
                                 packet=list(data[:8]))
            if self.launcher_reaped and len(self.status_buf) >= 10:
                detail = self.finalise_status()
                if detail.get("accepted"):
                    self.outcome = "PRE_RELEASE_TERMINATED"
                    self.rec.add("CLASS_T_OUTCOME", outcome=self.outcome)
                    return self.outcome
            if self.chan_eof:
                self.outcome = "PRE_RELEASE_LAUNCHER_LOST"
                self.rec.add("CLASS_T_OUTCOME", outcome=self.outcome,
                             facts={
                                 "launcher_loss": "OBSERVED (EOF)",
                                 "child_termination": "OBSERVED (pidfd)",
                                 "exit_status": "UNREPORTED",
                                 "classification": "UNRESOLVED"})
                return self.outcome
            if time.monotonic() >= self.class_t_deadline:
                self.outcome = "PRE_RELEASE_ABORT_STATUS_UNREPORTED"
                self.rec.add("CLASS_T_OUTCOME", outcome=self.outcome)
                return self.outcome
            self._sleep_tick()

    # ---------- demonstration delay (checkpoint rig only) ----------
    def demo_delay(self, point):
        """Widen a real protocol race window for the D-T
        demonstrations: at the named point, keep ticking
        (the pidfd watch stays live) for the configured
        seconds before proceeding. Packets drained meanwhile
        are held, in order, for the next phase. This is
        rig scaffolding only; the protocol path exercised
        afterwards is the production path."""
        cfg = self.cfg
        if cfg.demo_delay_point != point or cfg.demo_delay_s <= 0:
            return
        self.rec.add("DEMO_DELAY", point=point,
                     seconds=cfg.demo_delay_s)
        end = time.monotonic() + cfg.demo_delay_s
        while time.monotonic() < end:
            self._held.extend(self._tick())
            self._sleep_tick()

    # ---------- teardown (Part A.6: no classification) ----------
    def teardown(self, why):
        self.rec.add("TEARDOWN", why=why)
        if self.launcher_pid is not None and not self.launcher_reaped:
            try:
                os.kill(self.launcher_pid, signal.SIGKILL)
            except OSError:
                pass
            deadline = time.monotonic() + 5
            while not self.launcher_reaped and time.monotonic() < deadline:
                self.poll_launcher()
                self._sleep_tick()
        self.outcome = "TEARDOWN"
        return 0


    # ---------- helpers ----------
    def wait_launcher_exit(self, bound=5.0):
        end = time.monotonic() + bound
        while not self.launcher_reaped and time.monotonic() < end:
            self._tick()
            self._sleep_tick()

    def _status_candidate(self):
        """Tentative parse of the first 10 pipe bytes once
        they have all arrived (final acceptance happens in
        finalise_status, post-reap)."""
        if len(self.status_buf) < 10:
            return None
        data = self.status_buf[:10]
        if data[0] != MSG_STATUS or data[1] != 0:
            return False
        pid = struct.unpack(">I", data[2:6])[0]
        word = struct.unpack(">I", data[6:10])[0]
        if pid != self.child_pid:
            return False
        valid, _decode = validate_wait_status(word)
        return valid

    def finish(self, outcome):
        """Common attempt tail: final record poll, issuance
        over the record as it lies (TERMINAL or CRASH when
        the attempt reached the record), session close."""
        self.outcome = outcome
        self.poll_record()
        if not self.final_issued and (
                self.terminal_event is not None
                or (self.term_observed and self.events_seen > 0)):
            self.issue_final({
                "observed_at_utc": self.term_at,
                "basis": "pidfd termination observed (supervisor)",
                "status_word": (self.status_record[1]
                                if self.status_record else None)})
        if self.pidfd is not None:
            try:
                os.close(self.pidfd)
            except OSError:
                pass
            self.pidfd = None
        self.rec.add("ATTEMPT_CLOSED", outcome=outcome,
                     state=self.state)
        self.rec.close()
        return 0

    # ---------- the attempt ----------
    def run(self):
        cfg = self.cfg
        deadline = time.monotonic() + cfg.watchdog_s
        if not self.stage1_checks():
            self.rec.add("ATTEMPT_CLOSED", outcome="STAGE1_REFUSAL")
            self.rec.close()
            return 2
        if not self.spawn_launcher():
            return self.teardown("STATUS writer self-audit failed")
        if not self.send_launch_request():
            self.wait_launcher_exit()
            return self.finish("SX_LAUNCH_REQUEST_FAILED")

        # Phase B: await the pidfd handoff.
        handoff = None
        while time.monotonic() < deadline:
            for data, fds, _fl in self._tick():
                if data and data[0] == MSG_PIDFD_HANDOFF:
                    handoff = (data, fds)
                    break
                if data and data[0] == MSG_ABORT:
                    for fd in fds:
                        os.close(fd)
                    self._record_abort_received(data)
                    self.wait_launcher_exit()
                    return self.finish("SX_PRE_HANDOFF_ABORT")
                for fd in fds:
                    os.close(fd)
                if data:
                    self.rec.add("PROTOCOL_VIOLATION",
                                 detail="unexpected pre-handoff packet",
                                 packet=list(data[:8]))
            if handoff:
                break
            if self.chan_eof or self.launcher_reaped:
                self.rec.add("STAGE9_FACTS",
                             branch="launcher lost before handoff",
                             child_release="NOT_RELEASED",
                             child_termination="UNKNOWN",
                             pdeathsig="DESIGN EXPECTATION (not evidence)",
                             issuance="none")
                return self.finish("SX_LAUNCHER_LOST_PRE_HANDOFF")
        if handoff is None:
            return self.teardown("watchdog: no handoff")

        # Phase C: validation + acknowledgement.
        self.demo_delay("handoff")
        data, fds = handoff
        code, detail = self.validate_handoff(data, fds)
        self.rec.add("HANDOFF_VALIDATION", ack_code=code, **detail)
        self.send_packet(struct.pack(">BBB", MSG_HANDOFF_ACK, 0, code))
        self.rec.add("HANDOFF_ACK_SENT", ack_code=code)
        if code != 0:
            for fd in fds:
                try:
                    os.close(fd)
                except OSError:
                    pass
            if self.pidfd is not None:
                try:
                    os.close(self.pidfd)
                except OSError:
                    pass
                self.pidfd = None
        if code in (1, 2):
            self.wait_launcher_exit()
            return self.finish("SX_HANDOFF_REFUSED")
        if code == 3:
            # the launcher reaps only and reports by ABORT
            # CHILD_TERMINATED_AT_HANDOFF carrying the word.
            end = time.monotonic() + PRE_RELEASE_CLOSE_BOUND_S
            while time.monotonic() < end and not self.launcher_reaped:
                for pdata, pfds, _fl in self._tick():
                    for fd in pfds:
                        os.close(fd)
                    if pdata and pdata[0] == MSG_ABORT:
                        self._record_abort_received(pdata)
                self._sleep_tick()
            self.wait_launcher_exit()
            return self.finish("SX_CHILD_TERMINATED_AT_HANDOFF")
        self.state = "S4"
        self.demo_delay("settle")

        # Phase D: await GATE_READY.
        gate_ready = False
        while time.monotonic() < deadline:
            batch = self._held + self._tick()
            self._held = []
            for data, fds, _fl in batch:
                for fd in fds:
                    os.close(fd)
                if not data:
                    continue
                if data[0] == MSG_GATE_READY and len(data) == 2:
                    if self.term_observed:
                        # the termination commitment wins; a
                        # GATE_READY now is recorded and inert
                        self.rec.add("GATE_READY_INERT",
                                     note="termination already observed")
                    else:
                        gate_ready = True
                elif data[0] == MSG_ABORT:
                    self._record_abort_received(data)
                    self.wait_launcher_exit()
                    return self.finish("SX_ABORT_PRE_RELEASE")
                else:
                    self.rec.add("PROTOCOL_VIOLATION",
                                 detail="unexpected packet awaiting GATE_READY",
                                 packet=list(data[:8]))
            if self.term_observed:
                self.send_abort(
                    REASON_BY_NAME["CHILD_TERMINATED_PRE_RELEASE"], "T")
                self.class_t_wait()
                return self.finish(self.outcome)
            if gate_ready:
                break
            if self.chan_eof:
                self.rec.add("STAGE9_FACTS",
                             branch="launcher lost at S4",
                             child_release="NOT_RELEASED",
                             child_termination=(
                                 "OBSERVED" if self.term_observed
                                 else "UNKNOWN"),
                             issuance="none")
                return self.finish("SX_LAUNCHER_LOST")
        if not gate_ready:
            return self.teardown("watchdog: no GATE_READY")
        self.state = "S5"
        self.rec.add("GATE_READY")
        self.demo_delay("s5")
        for data, fds, _fl in self._held:
            for fd in fds:
                os.close(fd)
            if data and data[0] == MSG_ABORT:
                self._record_abort_received(data)
                self.wait_launcher_exit()
                return self.finish("SX_ABORT_PRE_RELEASE")
        self._held = []

        # Phase E: Part B observation, readiness guard, RELEASE.
        # A termination already observed in S5 commits to
        # class-T before any observation is attempted (the
        # state table's S5 termination row).
        if self.term_observed:
            self.send_abort(
                REASON_BY_NAME["CHILD_TERMINATED_PRE_RELEASE"], "T")
            self.class_t_wait()
            return self.finish(self.outcome)
        ok, _evidence = self.part_b_observation()
        if not ok:
            self.send_abort(REASON_BY_NAME["SUPERVISOR_ABORT"], "F")
            try:
                self.chan.close()
            except OSError:
                pass
            self.wait_launcher_exit()
            return self.finish("SX_PART_B_OBSERVATION_FAILED")
        guard = readiness_poll(self.pidfd)
        self.rec.add("PRE_RELEASE_GUARD", outcome=guard)
        if guard == "TERMINATED":
            if not self.term_observed:
                self.term_observed = True
                self.term_at = utc_now()
            self.send_abort(
                REASON_BY_NAME["CHILD_TERMINATED_PRE_RELEASE"], "T")
            self.class_t_wait()
            return self.finish(self.outcome)
        if guard != "NOT_OBSERVED":
            self.send_abort(REASON_BY_NAME["READINESS_UNVERIFIABLE"], "F")
            try:
                self.chan.close()
            except OSError:
                pass
            self.wait_launcher_exit()
            return self.finish("SX_READINESS_UNVERIFIABLE")
        self.send_packet(struct.pack(">BB", MSG_RELEASE, 0))
        self.state = "S6"
        self.rec.add("RELEASE_SENT")

        # Phase F: post-release — actuation, STATUS, closure.
        closed = False
        s8_recorded = False
        while time.monotonic() < deadline:
            for data, fds, _fl in self._tick():
                for fd in fds:
                    os.close(fd)
                if not data:
                    continue
                code_b = data[0]
                if code_b == MSG_GATE_ACTUATED and len(data) == 2:
                    if self.gate_write_failed is not None:
                        self.rec.add("PROTOCOL_VIOLATION",
                                     detail="GATE_ACTUATED after GATE_WRITE_FAILED")
                    else:
                        self.gate_actuated = True
                        self.state = "S7"
                        self.rec.add("GATE_ACTUATED")
                elif code_b == MSG_GATE_WRITE_FAILED and len(data) == 5:
                    if self.gate_actuated:
                        self.rec.add("PROTOCOL_VIOLATION",
                                     detail="GATE_WRITE_FAILED after GATE_ACTUATED")
                    else:
                        self.gate_write_failed = {
                            "error_class": data[2],
                            "errno": struct.unpack(">H", data[3:5])[0],
                            "class_source": "LAUNCHER-REPORTED"}
                        self.rec.add("GATE_WRITE_FAILED",
                                     **self.gate_write_failed)
                elif code_b == MSG_ABORT:
                    self._record_abort_received(data)
                elif code_b == MSG_STATUS:
                    self.rec.add("PROTOCOL_VIOLATION",
                                 detail="STATUS on channel (pipe-only)")
                else:
                    self.rec.add("PROTOCOL_VIOLATION",
                                 detail="unexpected post-release packet",
                                 packet=list(data[:8]))
            cand = self._status_candidate()
            if cand and self.term_observed:
                closed = True
                break
            if cand and not s8_recorded:
                self.state = "S8"
                s8_recorded = True
                self.rec.add("STATE", state="S8")
            if self.abort_received is not None:
                self.wait_launcher_exit()
                return self.finish("SX_ABORT_POST_RELEASE")
            # A valid STATUS candidate with termination not
            # yet observed is S8: channel EOF and the
            # launcher's exit block nothing — the progression
            # to S8F proceeds on the pidfd alone.
            if self.chan_eof and self.launcher_reaped and not cand:
                self.rec.add("STAGE9_FACTS",
                             branch="launcher lost post-release",
                             actuation=("PROVEN" if self.gate_actuated
                                        else "UNKNOWN"),
                             classification="UNRESOLVED")
                return self.finish("SX_LAUNCHER_LOST_POST_RELEASE")
        if not closed:
            return self.teardown("watchdog: no closure")

        # Closure: S8F on the consistent pair, then S9.
        self.state = "S8F"
        self.wait_launcher_exit()
        detail = self.finalise_status()
        if not detail.get("accepted"):
            self.rec.add("STAGE9_FACTS",
                         branch="STATUS not accepted at finalise",
                         classification="UNRESOLVED")
            return self.finish("SX_STATUS_UNRESOLVED")
        self.state = "S9"
        self.rec.add("STATE", state="S9",
                     terminal_facts={
                         "status_child_pid": self.status_record[0],
                         "status_word": self.status_record[1],
                         "pidfd_termination_observed": True})
        # STATUS_ACK: attempted, outcome recorded separately;
        # closure never depends on it.
        if self.chan_eof:
            ack_outcome = "STATUS_ACK_UNDELIVERABLE"
        else:
            ack_outcome = ("ACK_DELIVERED"
                           if self.send_packet(struct.pack(
                               ">BB", MSG_STATUS_ACK, 0))
                           else "STATUS_ACK_UNDELIVERABLE")
        self.rec.add("STATUS_ACK_OUTCOME", outcome=ack_outcome)
        # Close-out window for the launcher-exit observation.
        if not self.chan_eof:
            end = time.monotonic() + CLOSE_OUT_WINDOW_S
            while not self.chan_eof and time.monotonic() < end:
                self._tick()
                self._sleep_tick()
            if not self.chan_eof:
                self.rec.add("LAUNCHER_EXIT_UNOBSERVED")
                try:
                    self.chan.close()
                except OSError:
                    pass
        return self.finish("S9_CLOSED")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pilot-supervisor")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--launcher",
                    default="/srv/nemotron-pilot/launcher")
    ap.add_argument("--runs-root", default="/srv/nemotron-pilot/runs")
    ap.add_argument("--commitments",
                    default="/srv/nemotron-pilot/commitments")
    ap.add_argument("--log-dir",
                    default="/srv/nemotron-pilot/supervisor/logs")
    ap.add_argument("--evidence-dir",
                    default="/srv/nemotron-pilot/supervisor/launch-evidence")
    ap.add_argument("--identity-records",
                    default="/srv/nemotron-pilot/supervisor/identity_records.json")
    ap.add_argument("--watchdog", type=float, default=120.0)
    ap.add_argument("--demo-delay-point", default="",
                    choices=["", "handoff", "settle", "s5"],
                    help="checkpoint rig only: widen a race window")
    ap.add_argument("--demo-delay-s", type=float, default=0.0)
    ap.add_argument("--hook-env", action="append", default=[],
                    help="KEY=VALUE passed to the launcher (test builds only)")
    args = ap.parse_args(argv)
    cfg = Config(args)
    sup = Supervisor(cfg)
    try:
        return sup.run()
    except Exception as exc:  # supervisor internal failure
        try:
            sup.rec.add("SUPERVISOR_INTERNAL_ERROR", error=repr(exc))
            sup.rec.close()
        except Exception:
            pass
        raise


if __name__ == "__main__":
    sys.exit(main())
