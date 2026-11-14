#!/usr/bin/env python3
"""Apply C0 Correction 2 (STATUS pipe transport, chunks K1-K5)
to the Correction-1 pin, producing launcher-c2.c. Every
replacement is exact-match and count-checked; the input hash
is verified against the pin before any edit."""
import hashlib, sys

SRC = "launcher.c"
DST = "launcher-c2.c"
PIN = "3e0482c050ddf263a5b1021d84073259591a00d4193bf84be66beb0ab8771a26"

data = open(SRC, "rb").read()
h = hashlib.sha256(data).hexdigest()
if h != PIN:
    sys.exit(f"INPUT HASH MISMATCH: {h} != pin {PIN}")
text = data.decode()

def rep(old, new, count=1):
    global text
    n = text.count(old)
    if n != count:
        sys.exit(f"REPLACEMENT COUNT {n} != {count} for: {old[:60]!r}...")
    text = text.replace(old, new)

# ---- K1: constants (STATUS_FD, transport-failure exit) ----
rep("""/* child establishment failure exit codes (internal to the
 * child; observed by the launcher only as a wait status) */""",
"""/* STATUS transport (Freeze Amendment 2026-11-14-A; the
 * S3.5 STATUS Pipe Contract): the dedicated pipe write end
 * on its reserved descriptor, supervisor-placed pre-exec. */
#define STATUS_FD 4

/* launcher exit: the STATUS write failed on a
 * STATUS-producing path (transport failure; never 0) */
#define EXIT_STATUS_TRANSPORT_FAILED 17

/* child establishment failure exit codes (internal to the
 * child; observed by the launcher only as a wait status) */""")

# ---- K4 (+K2 helper): replace the channel send_status ----
rep("""static int send_status(void) {
    /* the shared-flag contract: g_sent is set by the caller
     * immediately before this transmission, never retried */
    uint8_t b[10];
    memset(b, 0, sizeof b);
    b[0] = MSG_STATUS;
    put_u32(b + 2, (uint32_t)g_child);
    put_u32(b + 6, g_held_word);
    return chan_send(b, 10, -1);
}""",
"""/* STATUS descriptor verification (Freeze Amendment
 * 2026-11-14-A section 3.2): present, a FIFO, open for
 * writing, FD_CLOEXEC clear. Inspection establishes these
 * properties only; the peer relationship is established
 * by the controlled creation-and-handoff procedure. */
static int status_fd_valid(void) {
    int fl = fcntl(STATUS_FD, F_GETFD);
    if (fl < 0) return 0;
    if (fl & FD_CLOEXEC) return 0;
    struct stat sb;
    if (fstat(STATUS_FD, &sb) != 0) return 0;
    if (!S_ISFIFO(sb.st_mode)) return 0;
    int acc = fcntl(STATUS_FD, F_GETFL);
    if (acc < 0) return 0;
    int mode = acc & O_ACCMODE;
    if (mode != O_WRONLY && mode != O_RDWR) return 0;
    return 1;
}

/* The STATUS transmission, on the dedicated pipe (the
 * S3.5 STATUS Pipe Contract section 4). The record is the
 * pin's 10-byte body, byte-identical; only the transport
 * changed. Returns 0 on a complete write, -1 on any
 * non-complete outcome (EPIPE, other error, short write).
 * The descriptor is closed after the attempt, complete
 * or not. The shared-flag contract is unchanged: g_sent
 * is set by the caller immediately before this one
 * transmission, never retried. */
static int send_status(void) {
    uint8_t b[10];
    memset(b, 0, sizeof b);
    b[0] = MSG_STATUS;
    put_u32(b + 2, (uint32_t)g_child);
    put_u32(b + 6, g_held_word);
    /* the write is survivable only while SIGPIPE is
     * ignored; verify the disposition in force first */
    struct sigaction cur;
    memset(&cur, 0, sizeof cur);
    if (sigaction(SIGPIPE, NULL, &cur) != 0 || cur.sa_handler != SIG_IGN) {
        return -1;
    }
    ssize_t n;
    do { n = write(STATUS_FD, b, 10); } while (n < 0 && errno == EINTR);
    int ok = (n == 10);
    close(STATUS_FD);
    return ok ? 0 : -1;
}""")

# ---- K5 site 1: class-T abort_receipt_exit (pin line 608) ----
rep("""    g_sent = true;
    (void)send_status();
    teardown_drain();
    _exit(0);""",
"""    g_sent = true;
    if (send_status() != 0) { teardown_drain(); _exit(EXIT_STATUS_TRANSPORT_FAILED); }
    teardown_drain();
    _exit(0);""")

# ---- K3: child closes the STATUS writer explicitly ----
rep("""    close(CHANNEL_FD);   /* the status channel is never the child's */""",
"""    close(CHANNEL_FD);   /* the status channel is never the child's */
    close(STATUS_FD);    /* the status writer is never the child's */""")

# ---- K2: precondition verification in launcher_run ----
rep("""        if (so_type != SOCK_SEQPACKET) return 13;
    }
""",
"""        if (so_type != SOCK_SEQPACKET) return 13;
    }
    /* The STATUS pipe write end: descriptor 4, verified
     * per Freeze Amendment 2026-11-14-A section 3.2. */
    if (!status_fd_valid()) return 13;
""")

# ---- K5 site 2: gate-write-failure branch (pin line 1169) ----
rep("""                if (!g_sent) { g_sent = true; (void)send_status(); }
                return 0;""",
"""                if (!g_sent) { g_sent = true; if (send_status() != 0) return EXIT_STATUS_TRANSPORT_FAILED; }
                return 0;""")

# ---- K5 site 3: ordinary Stage 8 termination (pin line 1181) ----
rep("""    if (ensure_reaped() != 0) return 4;
    if (!g_sent) { g_sent = true; (void)send_status(); }
    return 0;""",
"""    if (ensure_reaped() != 0) return 4;
    if (!g_sent) { g_sent = true; if (send_status() != 0) return EXIT_STATUS_TRANSPORT_FAILED; }
    return 0;""")

open(DST, "w").write(text)
out = open(DST, "rb").read()
print(f"{DST}: {len(text.splitlines())} lines sha256 {hashlib.sha256(out).hexdigest()}")
