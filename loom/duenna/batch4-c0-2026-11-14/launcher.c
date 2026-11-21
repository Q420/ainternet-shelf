/*
 * pilot-launcher.c — the Nemotron pilot custody launcher.
 *
 * Implements the LAUNCHER BEHAVIOUR-AND-INTERFACE FREEZE
 * (Batch 0; sha256 6bb9ae80...) under Stage 5 Build
 * Specification Rev 26 (as amended), section 3.5 points 2-3
 * (Option A three-process model): the launcher is the harness
 * child's OS parent and reaper, the holder of the launch gate,
 * and the reporter of the child's raw exit status over the
 * SOCK_SEQPACKET status channel — nothing more. It never
 * issues, never computes a committed value, and never writes
 * to commitments/ or to any supervisor record. Its privileged
 * window performs no file writes at all.
 *
 * Fixed at build time (no configuration file):
 *   - the harness programme path and argv shape (below);
 *   - the child's and the launcher's own target identities,
 *     resolved by account name at run time;
 *   - the identity records the pre-release re-check compares
 *     against (identity_records.h, generated at build time).
 *
 * The status channel arrives on descriptor 3, placed there by
 * the supervisor without close-on-exec; it is the only
 * descriptor the launcher accepts beyond 0/1/2.
 *
 * Test hooks for the D-T1..D-T6 demonstrations exist only
 * under -DPILOT_TEST_HOOKS (compile-time; the production
 * build excludes them and the flag state is recorded in the
 * gate evidence).
 *
 * CORRECTION (Batch 4 source correction, plan Rev 3,
 * approved by Alex at bd7ba6b6): the seven findings of
 * Alex's inspection of pin ba4cb865... are corrected —
 * (1) run-ID parser rewritten positionally with real
 * calendar validation; (2) the child's first act is the
 * inherited-parent check, closes after it; (3) descriptor
 * closure checked and verified by enumeration, fail-
 * closed; (4) only ENODATA establishes an absent file
 * capability set; (5) incoming ABORT packets fully
 * validated before dispatch; (6) receive outcomes kept
 * distinct (-1 EOF / -2 malformed / -3 error / -4
 * ancillary violation) with the Rev 3 cleanup contract
 * and exit codes (8 violation, 9 receive error);
 * (7) no ancillary data is accepted on any received
 * message and every delivered descriptor is closed.
 *
 * CORRECTION ROUND 2 (plan Revision 4; Treatment A
 * ruled by Alex at pb-mwg2c6a8): the two findings
 * reopened at pin 6430b9f... — a zero-length receive is
 * classified AFTER the ancillary walk (ancillary -4)
 * by the poll + peek sequence
 * (record -2 / shutdown -1), never as EOF by default;
 * and the ACK-wait ABORT is validated by
 * abort_packet_valid() before dispatch.
 *
 * C0 REWORK (Batch 4 whole plan Revision 8, CLEARED
 * 2026-11-14; C0 chunk sheet 0710bb9d...): the receive
 * path is COLLECT-THEN-CLASSIFY. chan_recv() is a
 * receipt layer only — it reports what arrived (packet,
 * pending zero, ancillary/truncated violation, malformed,
 * error) and never classifies. Each receive site collects
 * entries into a per-site collection; a zero-length
 * receive becomes a pending-zero entry and is classified
 * only when the collection closes, from the collected
 * ordering — no clock participates. Closure-equivalence
 * requires the full observation triple of plan section
 * A.2: FIONREAD == 0, RDHUP/HUP observed, and a head
 * peek WITH a control buffer showing no ancillary data;
 * any failed observation closes the collection with the
 * site's receive-error outcome. The residue Ben ruled
 * acceptable (2026-11-14, fcc9c452) stands as disclosed
 * in plan section A.2: an ancillary record queued behind
 * a further plain zero takes the closure outcome; the
 * ancillary rules stand in full wherever a record is
 * observable. The former classifier function and its
 * bounded watch are deleted.
 */

#define _GNU_SOURCE
#include <arpa/inet.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <limits.h>
#include <pwd.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/ioctl.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/xattr.h>
#include <time.h>
#include <unistd.h>
#include <linux/capability.h>
#include <sys/syscall.h>

#include "identity_records.h"

/* ---- compiled-in constants ---------------------------------- */

#ifndef HARNESS_PATH
#define HARNESS_PATH   "/srv/nemotron-pilot/harness/pilot-harness"
#endif
#define CHANNEL_FD     3
#define RELEASE_BYTE   0x52u
#define MAX_PACKET     128

#define CHILD_ACCOUNT  "pilot-harness"
#define SUPERVISOR_ACCOUNT "pilot-supervisor"

/* message codes (Rev 26 section 3.5 point 3, catalogue) */
#define MSG_LAUNCH_REQUEST 0x01u
#define MSG_PIDFD_HANDOFF  0x02u
#define MSG_HANDOFF_ACK    0x03u
#define MSG_GATE_READY     0x04u
#define MSG_RELEASE        0x05u
#define MSG_GATE_ACTUATED  0x06u
#define MSG_STATUS         0x07u
#define MSG_STATUS_ACK     0x08u
#define MSG_ABORT          0x09u
#define MSG_GATE_WRITE_FAILED 0x0Au

/* ABORT reason codes (builder's assignment, fixed by this
 * source and recorded in the submission letter; the
 * supervisor implements the same table) */
#define RSN_CHILD_LOST_IN_ESTABLISHMENT   1u
#define RSN_CHILD_TERMINATED_PRE_RELEASE  2u
#define RSN_CHILD_TERMINATED_AT_HANDOFF   3u
#define RSN_IDENTITY_RECHECK_FAILED       4u
#define RSN_SETTLING_FAILED               5u
#define RSN_READINESS_UNVERIFIABLE        6u
#define RSN_SUPERVISOR_ABORT              7u

/* child establishment failure exit codes (internal to the
 * child; observed by the launcher only as a wait status) */
#define CHILD_EXIT_PARENT_LOST   70
#define CHILD_EXIT_GATE_REFUSED  71
#define CHILD_EXIT_EXEC_FAILED   72
#define CHILD_EXIT_SETUP_FAILED  73

/* ---- launcher state (the shared-flag contract, Stage 5) ---- */

static bool     g_reaped = false;   /* set only by a confirmed reap */
static bool     g_sent   = false;   /* set only just before the one STATUS */
static uint32_t g_held_word = 0;    /* raw wait_status, verbatim */
static pid_t    g_child = -1;
static int      g_gate_w = -1;      /* launcher-held gate write end */
static bool     g_privileged = true;/* false after the launcher's drop */

/* ---- small helpers ------------------------------------------ */

static void put_u32(uint8_t *p, uint32_t v) {
    uint32_t be = htonl(v);
    memcpy(p, &be, 4);
}
static void put_u64(uint8_t *p, uint64_t v) {
    uint8_t b[8];
    for (int i = 7; i >= 0; i--) { b[i] = (uint8_t)(v & 0xffu); v >>= 8; }
    memcpy(p, b, 8);
}
static uint32_t get_u32(const uint8_t *p) {
    uint32_t be;
    memcpy(&be, p, 4);
    return ntohl(be);
}

/* Send one protocol packet. Returns 0 on a complete send. */
static int chan_send(const uint8_t *buf, size_t len, int anc_fd) {
    struct iovec iov = { (void *)buf, len };
    char cbuf[CMSG_SPACE(sizeof(int))];
    struct msghdr mh;
    memset(&mh, 0, sizeof mh);
    mh.msg_iov = &iov;
    mh.msg_iovlen = 1;
    if (anc_fd >= 0) {
        mh.msg_control = cbuf;
        mh.msg_controllen = sizeof cbuf;
        struct cmsghdr *c = CMSG_FIRSTHDR(&mh);
        c->cmsg_level = SOL_SOCKET;
        c->cmsg_type = SCM_RIGHTS;
        c->cmsg_len = CMSG_LEN(sizeof(int));
        memcpy(CMSG_DATA(c), &anc_fd, sizeof(int));
    }
    ssize_t n;
    do { n = sendmsg(CHANNEL_FD, &mh, MSG_NOSIGNAL); } while (n < 0 && errno == EINTR);
    return (n == (ssize_t)len) ? 0 : -1;
}

/* Test hooks: fault injection + closed-descriptor
 * accounting. Compiled only under PILOT_TEST_HOOKS. */
#ifdef PILOT_TEST_HOOKS
static int g_recv_calls = 0;
static void hook_note_closed(int count) {
    if (count <= 0) return;
    int fd = open("/srv/nemotron-pilot/batch4/test-hooks/closed-fds.log",
                  O_WRONLY | O_CREAT | O_APPEND | O_CLOEXEC, 0600);
    if (fd < 0) return;
    char line[32];
    int m = snprintf(line, sizeof line, "closed %d\n", count);
    if (m > 0) { ssize_t w = write(fd, line, (size_t)m); (void)w; }
    close(fd);
}
static int hook_fail_recvmsg(void) {
    const char *e = getenv("PILOT_HOOK_FAIL_RECVMSG_AT");
    if (!e) return 0;
    return g_recv_calls == atoi(e);
}
/* C0 fault injection at the closure check (NQ6' cases):
 * force the FIONREAD observation or the head-ancillary
 * peek to fail, so the fail-closed error route is
 * exercised per site. */
static int hook_fail_fionread(void) {
    const char *e = getenv("PILOT_HOOK_FAIL_FIONREAD");
    return e && atoi(e);
}
static int hook_fail_peek(void) {
    const char *e = getenv("PILOT_HOOK_FAIL_PEEK");
    return e && atoi(e);
}
/* C0 D-series stalls: bounded delays at named points in
 * the collection path (delays stay within the existing
 * site/lifecycle bounds; outcomes must be identical to
 * the unstalled forms — classification has no clock). */
static void hook_stall_ms(const char *name) {
    const char *e = getenv(name);
    if (!e) return;
    long ms = atol(e);
    if (ms <= 0) return;
    struct timespec ts = { ms / 1000, (ms % 1000) * 1000000L };
    nanosleep(&ts, NULL);
}
#define hook_stall_recv()  hook_stall_ms("PILOT_HOOK_STALL_RECV_MS")
#define hook_stall_check() hook_stall_ms("PILOT_HOOK_STALL_CHECK_MS")
#else
#define hook_note_closed(count) ((void)0)
#define hook_fail_fionread() 0
#define hook_fail_peek() 0
#define hook_stall_recv()  ((void)0)
#define hook_stall_check() ((void)0)
#endif

/* ---- the receipt layer, the collection, classification ----
 * (C0 rework; whole plan Rev 8 Part A.) chan_recv() reports
 * RECEIPT FACTS only and never classifies: what arrived is a
 * packet, a pending zero, an ancillary/truncated violation,
 * a malformed (truncated) packet, or a receive error. The
 * launcher accepts NO ancillary data on any received
 * message: any control message of any level or type makes
 * the receipt a violation, and every descriptor the kernel
 * delivered is closed unexamined, on every path (Rev 3,
 * findings 6 and 7). */
#define RCV_PACKET     1  /* packet; *out_len bytes in buf */
#define RCV_ZERO       2  /* zero-length receive, no ancillary */
#define RCV_ANCILLARY  3  /* violation entry: ancillary at receipt */
#define RCV_TRUNCATED  4  /* violation entry: control truncated */
#define RCV_MALFORMED  5  /* packet bytes truncated (MSG_TRUNC) */
#define RCV_ERROR      6  /* receive failure */

static int chan_recv(uint8_t *buf, size_t cap, ssize_t *out_len) {
#ifdef PILOT_TEST_HOOKS
    g_recv_calls++;
    if (hook_fail_recvmsg()) return RCV_ERROR;
#endif
    char cbuf[CMSG_SPACE(sizeof(int) * 4)];
    struct iovec iov = { buf, cap };
    struct msghdr mh;
    memset(&mh, 0, sizeof mh);
    mh.msg_iov = &iov;
    mh.msg_iovlen = 1;
    mh.msg_control = cbuf;
    mh.msg_controllen = sizeof cbuf;
    ssize_t n;
    do { n = recvmsg(CHANNEL_FD, &mh, MSG_CMSG_CLOEXEC); } while (n < 0 && errno == EINTR);
    if (n < 0) return RCV_ERROR;
    /* Ancillary accounting comes FIRST, for every receive
     * that delivered anything — a zero-length record
     * included (correction round 2, Fix A). */
    int violation = 0;
    int closed = 0;
    if (mh.msg_controllen > 0) violation = 1; /* any control data at all */
    for (struct cmsghdr *c = CMSG_FIRSTHDR(&mh); c; c = CMSG_NXTHDR(&mh, c)) {
        if (c->cmsg_level == SOL_SOCKET && c->cmsg_type == SCM_RIGHTS) {
            int cnt = (int)((c->cmsg_len - CMSG_LEN(0)) / sizeof(int));
            int *fds = (int *)CMSG_DATA(c);
            for (int i = 0; i < cnt; i++) { close(fds[i]); closed++; }
        } else {
            violation = 1;
        }
    }
    hook_note_closed(closed);
    if (mh.msg_flags & MSG_CTRUNC) return RCV_TRUNCATED;
    if (violation) return RCV_ANCILLARY;
    if (mh.msg_flags & MSG_TRUNC) return RCV_MALFORMED;
    if (n == 0) return RCV_ZERO;  /* a pending zero — never a classification */
    *out_len = n;
    return RCV_PACKET;
}

/* The closure observation (plan A.2): taken after a pending
 * zero, it decides whether the collection may close as
 * closure-equivalent. ALL THREE must hold: (i) FIONREAD
 * (the whole-queue byte count, the one byte primitive)
 * reports 0; (ii) RDHUP/HUP is observed (a zero-timeout
 * poll, an observation only — it classifies nothing);
 * (iii) ONE head peek WITH a control buffer shows no
 * ancillary data at the head of the queue. Any failed
 * observation is OBS_FAIL — fail-closed, never read as a
 * passing condition. Bytes queued (OBS_CONTINUE) or an
 * ancillary head record (OBS_ANC_HEAD) both mean the
 * collection CONTINUES: the queued record is collected by
 * a real receive and takes its own branch. */
#define OBS_CLOSURE  1
#define OBS_CONTINUE 2
#define OBS_ANC_HEAD 3
#define OBS_FAIL     4

static int closure_check(void) {
    int avail = 0;
    if (hook_fail_fionread()) return OBS_FAIL;
    if (ioctl(CHANNEL_FD, FIONREAD, &avail) != 0) return OBS_FAIL;
    if (avail > 0) return OBS_CONTINUE;
    struct pollfd pfd;
    pfd.fd = CHANNEL_FD;
    pfd.events = POLLIN | POLLRDHUP; /* RDHUP is reported only when requested */
    pfd.revents = 0;
    int pr;
    do { pr = poll(&pfd, 1, 0); } while (pr < 0 && errno == EINTR);
    if (pr < 0) return OBS_FAIL;
    short rev = pfd.revents;
    if (!(rev & (POLLRDHUP | POLLHUP))) {
        if (rev & (POLLERR | POLLNVAL)) return OBS_FAIL;
        return OBS_CONTINUE;  /* peer still open: nothing classifiable yet */
    }
    /* The head-ancillary check: ONE peek WITH a control
     * buffer. A peek installs real descriptors for the
     * head record's ancillary data; they are closed on
     * sight — the peek is an observation, never a receipt. */
    if (hook_fail_peek()) return OBS_FAIL;
    unsigned char scratch[64];
    char pcbuf[CMSG_SPACE(sizeof(int) * 4)];
    struct iovec piov = { scratch, sizeof scratch };
    struct msghdr pmh;
    memset(&pmh, 0, sizeof pmh);
    pmh.msg_iov = &piov;
    pmh.msg_iovlen = 1;
    pmh.msg_control = pcbuf;
    pmh.msg_controllen = sizeof pcbuf;
    ssize_t pn;
    do { pn = recvmsg(CHANNEL_FD, &pmh, MSG_PEEK | MSG_DONTWAIT); } while (pn < 0 && errno == EINTR);
    if (pn < 0) return OBS_FAIL;
    int closed = 0;
    for (struct cmsghdr *c = CMSG_FIRSTHDR(&pmh); c; c = CMSG_NXTHDR(&pmh, c)) {
        if (c->cmsg_level == SOL_SOCKET && c->cmsg_type == SCM_RIGHTS) {
            int cnt = (int)((c->cmsg_len - CMSG_LEN(0)) / sizeof(int));
            int *fds = (int *)CMSG_DATA(c);
            for (int i = 0; i < cnt; i++) { close(fds[i]); closed++; }
        }
    }
    hook_note_closed(closed);
    if (pmh.msg_controllen > 0 || (pmh.msg_flags & MSG_CTRUNC)) return OBS_ANC_HEAD;
    return OBS_CLOSURE;
}

/* One site's collection (plan A.1). Entries: the packet
 * (at most one — the first packet closes the collection),
 * the pending-zero count, a violation entry (1 ancillary,
 * 2 truncated), a malformed entry, a closure-equivalent
 * entry, or a receive/observation error. The collection
 * closes on the first of: a packet, any violation or
 * malformed entry, a closure-equivalent entry, or an
 * error. It introduces no timeout of its own. Teardown is
 * not a collection close and produces no classification
 * (plan A.6): nothing here runs at teardown. */
struct collection {
    int     pending_zeros;
    int     has_packet;
    uint8_t pkt[MAX_PACKET];
    ssize_t pkt_len;
    int     violation;   /* 0 none, 1 ancillary, 2 truncated */
    int     malformed;
    int     closure;
    int     error;
};

static void collect(struct collection *c) {
    memset(c, 0, sizeof *c);
    uint8_t buf[MAX_PACKET];
    for (;;) {
        hook_stall_recv();
        ssize_t len = 0;
        int k = chan_recv(buf, sizeof buf, &len);
        if (k == RCV_PACKET) {
            memcpy(c->pkt, buf, (size_t)len);
            c->pkt_len = len;
            c->has_packet = 1;
            return;
        }
        if (k == RCV_ANCILLARY) { c->violation = 1; return; }
        if (k == RCV_TRUNCATED) { c->violation = 2; return; }
        if (k == RCV_MALFORMED) { c->malformed = 1; return; }
        if (k == RCV_ERROR)     { c->error = 1; return; }
        /* RCV_ZERO: enters the collection as a pending zero.
         * The closure observation decides whether the
         * collection may close here as closure-equivalent;
         * every other observation result keeps collecting. */
        c->pending_zeros++;
        hook_stall_check();
        int obs = closure_check();
        if (obs == OBS_FAIL)    { c->error = 1; return; }
        if (obs == OBS_CLOSURE) { c->closure = 1; return; }
        /* OBS_CONTINUE / OBS_ANC_HEAD: keep collecting. */
    }
}

/* Classification (plan A.3): a pure function of the
 * collected sequence. The site maps the class onto its own
 * exit routes and packet contracts. */
#define CLS_PROCEED   0  /* exactly the expected sequence: a clean packet */
#define CLS_POISONED  1  /* pending zeros before an otherwise valid packet */
#define CLS_VIOLATION 2  /* violation or malformed entry in the collection */
#define CLS_CLOSURE   3  /* closure-equivalent, only pending zeros before it */
#define CLS_ERROR     4  /* receive or observation error */

static int classify(const struct collection *c) {
    if (c->error) return CLS_ERROR;
    if (c->violation || c->malformed) return CLS_VIOLATION;
    if (c->closure) return CLS_CLOSURE;
    if (c->has_packet) return c->pending_zeros > 0 ? CLS_POISONED : CLS_PROCEED;
    return CLS_ERROR;  /* unreachable: collect() closes only on an entry */
}

/* Validate framing shared by all packets: code + zero flags,
 * exact length, unused bytes zero. */
static int frame_ok(const uint8_t *b, ssize_t n, uint8_t code,
                    ssize_t exact_len, size_t used) {
    if (n != exact_len) return -1;
    if (b[0] != code || b[1] != 0) return -1;
    for (size_t i = used; i < (size_t)n; i++) if (b[i] != 0) return -1;
    return 0;
}

static int send_simple(uint8_t code) {
    uint8_t b[2] = { code, 0 };
    return chan_send(b, 2, -1);
}

static int send_abort(uint8_t reason, bool with_word, uint32_t word) {
    uint8_t b[7];
    memset(b, 0, sizeof b);
    b[0] = MSG_ABORT;
    b[2] = reason;
    if (with_word) { put_u32(b + 3, word); return chan_send(b, 7, -1); }
    return chan_send(b, 3, -1);
}

static int send_status(void) {
    /* the shared-flag contract: g_sent is set by the caller
     * immediately before this transmission, never retried */
    uint8_t b[10];
    memset(b, 0, sizeof b);
    b[0] = MSG_STATUS;
    put_u32(b + 2, (uint32_t)g_child);
    put_u32(b + 6, g_held_word);
    return chan_send(b, 10, -1);
}

/* Reap the child exactly once under the flag contract.
 * Returns 0 when g_reaped holds a valid word afterwards
 * (including when it already did), -1 on a waitpid error
 * while unreaped. */
static int ensure_reaped(void) {
    if (g_reaped) return 0;
    int st;
    pid_t r;
    do { r = waitpid(g_child, &st, 0); } while (r < 0 && errno == EINTR);
    if (r != g_child) return -1;
    g_held_word = (uint32_t)st;
    g_reaped = true;
    return 0;
}

/* The class-T / supervisor-ABORT receipt action (Stage 5):
 * dispatch on the flags; transmit at most the one STATUS;
 * the launcher's work for the attempt then ends. */
static _Noreturn void abort_receipt_exit(void) {
    if (g_sent) _exit(0);
    if (!g_reaped) {
        if (ensure_reaped() != 0) _exit(4); /* no valid word: no STATUS */
    }
    g_sent = true;
    (void)send_status();
    _exit(0);
}

/* Fatal cleanup with a gated or running child, by window:
 * Window 1 (still privileged): kill directly, close the
 * gate unreleased, reap (word held, never transmitted).
 * Window 2 (dropped): the gate's EOF is the kill switch. */
static void cleanup_child(void) {
    if (g_child <= 0 || g_reaped) return;
    if (g_privileged) kill(g_child, SIGKILL);
    if (g_gate_w >= 0) { close(g_gate_w); g_gate_w = -1; }
    (void)ensure_reaped();
}

/* ---- run identifier (A-1 grammar) ---------------------------
 * <battery-id>-<UTC date YYYYMMDD>-<counter 001-999>;
 * battery-id 1-64 bytes of [A-Za-z0-9-], not starting or
 * ending with '-'; the date's fields range-checked (month
 * 01-12, day 01-31); counter exactly three digits, not 000. */
static int run_id_valid(const char *s) {
    size_t len = strlen(s);
    if (len < 14 || len > 64 + 1 + 8 + 1 + 3) return 0;
    /* counter: the final three characters, preceded by '-' */
    if (s[len - 4] != '-') return 0;
    const char *ctr = s + len - 3;
    for (int i = 0; i < 3; i++) if (ctr[i] < '0' || ctr[i] > '9') return 0;
    if (memcmp(ctr, "000", 3) == 0) return 0;
    /* date: the eight characters before that '-', itself
     * preceded by '-' */
    if (s[len - 13] != '-') return 0;
    const char *d = s + len - 12;
    for (int i = 0; i < 8; i++) if (d[i] < '0' || d[i] > '9') return 0;
    int year = (d[0] - '0') * 1000 + (d[1] - '0') * 100 + (d[2] - '0') * 10 + (d[3] - '0');
    int mon = (d[4] - '0') * 10 + (d[5] - '0');
    int day = (d[6] - '0') * 10 + (d[7] - '0');
    static const int dim[12] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    if (mon < 1 || mon > 12) return 0;
    int max_day = dim[mon - 1];
    if (mon == 2 && ((year % 4 == 0 && year % 100 != 0) || year % 400 == 0)) max_day = 29;
    if (day < 1 || day > max_day) return 0;
    /* battery id: everything before the date's separator */
    size_t blen = len - 13;
    if (blen < 1 || blen > 64) return 0;
    if (s[0] == '-' || s[blen - 1] == '-') return 0;
    for (size_t i = 0; i < blen; i++) {
        char ch = s[i];
        if (!((ch >= 'A' && ch <= 'Z') || (ch >= 'a' && ch <= 'z') ||
              (ch >= '0' && ch <= '9') || ch == '-')) return 0;
    }
    return 1;
}

/* ---- identity helpers --------------------------------------- */

static int account_ids(const char *name, uid_t *uid, gid_t *gid) {
    struct passwd *pw = getpwnam(name);
    if (!pw) return -1;
    *uid = pw->pw_uid;
    *gid = pw->pw_gid;
    return 0;
}

/* Drop every id (real, effective, saved) to (uid, gid):
 * supplementary groups cleared, setresgid then setresuid,
 * verified by read-back of every position. 0 on success. */
static int drop_to(uid_t uid, gid_t gid) {
    if (setgroups(0, NULL) != 0) return -1;
    if (setresgid(gid, gid, gid) != 0) return -1;
    if (setresuid(uid, uid, uid) != 0) return -1;
    uid_t ru, eu, su;
    gid_t rg, eg, sg;
    if (getresuid(&ru, &eu, &su) != 0) return -1;
    if (getresgid(&rg, &eg, &sg) != 0) return -1;
    if (ru != uid || eu != uid || su != uid) return -1;
    if (rg != gid || eg != gid || sg != gid) return -1;
    return 0;
}

/* Capability read-back, Method A (freeze section 3 step 5):
 * CapEff / CapPrm / CapAmb from /proc/self/status, all three
 * required present and zero. 0 on verified-empty. */
static int caps_verified_empty(void) {
    int fd = open("/proc/self/status", O_RDONLY | O_CLOEXEC);
    if (fd < 0) return -1;
    char buf[8192];
    ssize_t n = read(fd, buf, sizeof buf - 1);
    close(fd);
    if (n <= 0) return -1;
    buf[n] = '\0';
    const char *names[3] = { "CapEff:", "CapPrm:", "CapAmb:" };
    for (int i = 0; i < 3; i++) {
        const char *p = strstr(buf, names[i]);
        if (!p) return -1;
        p += strlen(names[i]);
        while (*p == ' ' || *p == '\t') p++;
        char *end = NULL;
        unsigned long long v = strtoull(p, &end, 16);
        if (end == p || v != 0) return -1;
    }
    return 0;
}

/* The file capability set of a path, via the
 * security.capability xattr: absent means empty; present
 * must parse as the kernel's vfs_cap_data with every mask
 * zero. 0 on verified-empty. */
static ssize_t caps_xattr_get(const char *path, void *buf, size_t size) {
#ifdef PILOT_TEST_HOOKS
    const char *e = getenv("PILOT_HOOK_XATTR_ERROR");
    if (e) { errno = atoi(e); return -1; }
#endif
    return getxattr(path, "security.capability", buf, size);
}

static int file_caps_empty(const char *path) {
    /* The on-disk vfs_cap_data layout is: magic_etc (the
     * revision in the top byte, the effective vector in
     * the low bits), then permitted/inheritable word
     * pairs — there is no per-entry effective field. The
     * value is parsed as words so every capability word
     * is actually inspected (the correction's unit tests
     * caught a field-layout error here against a crafted
     * capability xattr). */
    uint32_t words[6];
    ssize_t n = caps_xattr_get(path, words, sizeof words);
    /* only ENODATA establishes that the attribute — and
     * so the capability set — is absent; ENOTSUP and every
     * other failure mean the inspection could not be
     * performed and the check fails closed (finding 4) */
    if (n < 0) return (errno == ENODATA) ? 0 : -1;
    if (n != 20 && n != 24) return -1;
    uint32_t rev = words[0] & 0xff000000u;
    if (rev != 0x02000000u && rev != 0x03000000u) return -1;
    if (words[0] & 0x00ffffffu) return -1;   /* effective vector */
    for (int i = 1; i <= 4; i++)
        if (words[i] != 0) return -1;        /* permitted/inheritable */
    return 0;
}

/* Identity of one object for the re-check: canonical path,
 * stat, capability set. */
struct object_identity { dev_t dev; ino_t ino; mode_t mode; };
static int object_identity(const char *path, struct object_identity *out) {
    char resolved[PATH_MAX];
    if (!realpath(path, resolved)) return -1;
    struct stat st;
    if (stat(resolved, &st) != 0) return -1;
    if (file_caps_empty(resolved) != 0) return -1;
    out->dev = st.st_dev;
    out->ino = st.st_ino;
    out->mode = st.st_mode;
    return 0;
}

static int identity_matches(const struct object_identity *o,
                            unsigned long long dev, unsigned long long ino,
                            unsigned long long mode) {
    return (unsigned long long)o->dev == dev &&
           (unsigned long long)o->ino == ino &&
           (unsigned long long)(o->mode & 07777) == (mode & 07777) &&
           ((o->mode & (S_ISUID | S_ISGID)) == 0);
}

/* The pre-release identity re-check (layer 3): the harness
 * executable and its interpreter, against the records
 * compiled in at build time. 0 on an exact match. */
static int identity_recheck(void) {
    struct object_identity o;
    if (object_identity(HARNESS_PATH, &o) != 0) return -1;
    if (!identity_matches(&o, IDREC_HARNESS_DEV, IDREC_HARNESS_INO,
                          IDREC_HARNESS_MODE)) return -1;
    if (object_identity(INTERPRETER_PATH, &o) != 0) return -1;
    if (!identity_matches(&o, IDREC_INTERP_DEV, IDREC_INTERP_INO,
                          IDREC_INTERP_MODE)) return -1;
    return 0;
}

/* ---- test hooks (demonstrations D-T1..D-T6) ------------------
 * Compile-time only. A hold point waits while its hold file
 * exists in the test-hooks directory; the demonstration
 * driver creates and removes the files. Never compiled into
 * the production build. */
#ifdef PILOT_TEST_HOOKS
static void test_hold(const char *point) {
    char path[PATH_MAX];
    snprintf(path, sizeof path, "/srv/nemotron-pilot/test-hooks/%s.hold", point);
    while (access(path, F_OK) == 0) {
        struct timespec ts = { 0, 50 * 1000 * 1000 };
        nanosleep(&ts, NULL);
    }
}
#else
#define test_hold(point) ((void)0)
#endif

/* Descriptor closure for the child (finding 3): the
 * close_range calls are checked, and the result is then
 * verified by enumerating /proc/self/fd — only 0, 1, 2 and
 * the gate read end may remain. Any failure, or any
 * survivor, returns -1 and the child exits without
 * proceeding. */
static int fd_allowed(int fd, int gate_r, int dir_fd) {
    return fd == 0 || fd == 1 || fd == 2 || fd == gate_r || fd == dir_fd;
}
static int close_child_fds(int gate_r) {
#ifdef PILOT_TEST_HOOKS
    if (getenv("PILOT_HOOK_FAIL_CLOSE_RANGE")) return -1;
#endif
    int rc;
    if (gate_r == 3) {
        rc = close_range(4, ~0U, 0);
    } else {
        rc = 0;
        if (gate_r > 3 && close_range(3, (unsigned)(gate_r - 1), 0) != 0) rc = -1;
        if (close_range((unsigned)(gate_r + 1), ~0U, 0) != 0) rc = -1;
    }
    if (rc != 0) return -1;
    for (int pass = 0; pass < 2; pass++) {
        DIR *dir = opendir("/proc/self/fd");
        if (!dir) return -1;
        int dir_fd = dirfd(dir);
        int bad = 0;
        struct dirent *de;
        while ((de = readdir(dir)) != NULL) {
            if (de->d_name[0] == '.') continue;
            int fd = atoi(de->d_name);
            if (fd_allowed(fd, gate_r, dir_fd)) continue;
            if (pass == 0) { if (close(fd) != 0) bad = 1; }
            else bad = 1; /* a survivor on the verify pass */
        }
        closedir(dir);
        if (bad) return -1;
    }
    return 0;
}

/* ---- the child (Stage 3) -------------------------------------
 * Runs only in the forked child. Every failure is an
 * immediate _exit; the sequence never continues into the
 * exec on a failed or partial step. */
static _Noreturn void child_main(int gate_r, int gate_w, pid_t expected_parent,
                                 uid_t h_uid, gid_t h_gid,
                                 const char *run_id) {
    /* (a) parent check — the child's FIRST act, before any
     * other call (freeze section 3 step 3; finding 2) */
    if (getppid() != expected_parent) _exit(CHILD_EXIT_PARENT_LOST);
    close(gate_w);       /* the write end is the launcher's alone */
    close(CHANNEL_FD);   /* the status channel is never the child's */
    /* (b) privilege transition to pilot-harness */
    if (drop_to(h_uid, h_gid) != 0) _exit(CHILD_EXIT_SETUP_FAILED);
    /* (c) capability read-back — all three sets empty */
    if (caps_verified_empty() != 0) _exit(CHILD_EXIT_SETUP_FAILED);
    /* (d) arm the parent-death backstop, after the drop */
    if (prctl(PR_SET_PDEATHSIG, SIGKILL) != 0) _exit(CHILD_EXIT_SETUP_FAILED);
    /* (e) arming read-back */
    {
        int pd = 0;
        if (prctl(PR_GET_PDEATHSIG, (unsigned long)&pd) != 0 || pd != SIGKILL)
            _exit(CHILD_EXIT_SETUP_FAILED);
    }
    /* (f) parent re-check */
    if (getppid() != expected_parent) _exit(CHILD_EXIT_PARENT_LOST);
    /* (g) exhaustive descriptor close, sparing 0/1/2 and the
     * gate read end — checked, then verified by enumeration;
     * any failure or survivor ends the child here */
    if (close_child_fds(gate_r) != 0) _exit(CHILD_EXIT_SETUP_FAILED);
    /* (h) the gate: exactly one byte, the release byte */
    uint8_t byte = 0;
    ssize_t n;
    do { n = read(gate_r, &byte, 1); } while (n < 0 && errno == EINTR);
    if (n != 1 || byte != RELEASE_BYTE) _exit(CHILD_EXIT_GATE_REFUSED);
    /* Stage 7: the exec (closes the gate read end, O_CLOEXEC) */
    char *const argv[] = { (char *)HARNESS_PATH, (char *)run_id, NULL };
    char *const envp[] = { NULL };
    execve(HARNESS_PATH, argv, envp);
    _exit(CHILD_EXIT_EXEC_FAILED);
}

/* An incoming ABORT is dispatched on only after complete
 * validation (finding 5): the supervisor-to-launcher form
 * is exactly the reason-only packet — code, zero flags,
 * a reason in the assigned table, length 3. */
static int abort_packet_valid(const uint8_t *b, ssize_t n) {
    if (n != 3) return -1;
    if (b[0] != MSG_ABORT || b[1] != 0) return -1;
    if (b[2] < 1 || b[2] > 7) return -1;
    return 0;
}

/* ---- main ---------------------------------------------------- */

#ifndef PILOT_UNIT_TESTS
int main(int argc, char **argv) {
    /* Point 2, signal establishment — before anything else. */
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = SIG_IGN;
    sigemptyset(&sa.sa_mask);
    if (sigaction(SIGPIPE, &sa, NULL) != 0) return 10;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = SIG_DFL;
    sa.sa_flags = 0; /* no SA_NOCLDWAIT, no SA_NOCLDSTOP */
    sigemptyset(&sa.sa_mask);
    if (sigaction(SIGCHLD, &sa, NULL) != 0) return 10;
    struct sigaction back;
    if (sigaction(SIGCHLD, NULL, &back) != 0) return 10;
    if (back.sa_handler != SIG_DFL || (back.sa_flags & (SA_NOCLDWAIT | SA_NOCLDSTOP))) return 10;

    /* Backstop against the supervisor (point 2). */
    pid_t expected_supervisor = getppid();
    if (prctl(PR_SET_PDEATHSIG, SIGKILL) != 0) return 11;
    {
        int pd = 0;
        if (prctl(PR_GET_PDEATHSIG, (unsigned long)&pd) != 0 || pd != SIGKILL) return 11;
    }
    if (getppid() != expected_supervisor) return 11;

    /* The one operation: argv is exactly the run identifier. */
    if (argc != 2) return 12;
    const char *run_id = argv[1];
    if (!run_id_valid(run_id)) return 12;

    /* Descriptor preconditions: 0/1/2 present; the channel is
     * descriptor 3 and is a SEQPACKET socket. */
    for (int fd = 0; fd <= 2; fd++) if (fcntl(fd, F_GETFD) < 0) return 13;
    if (fcntl(CHANNEL_FD, F_GETFD) < 0) return 13;
    {
        int so_type = 0;
        socklen_t sl = sizeof so_type;
        if (getsockopt(CHANNEL_FD, SOL_SOCKET, SO_TYPE, &so_type, &sl) != 0) return 13;
        if (so_type != SOCK_SEQPACKET) return 13;
    }

    /* Target identities, resolved by name. */
    uid_t h_uid, s_uid;
    gid_t h_gid, s_gid;
    if (account_ids(CHILD_ACCOUNT, &h_uid, &h_gid) != 0) return 14;
    if (account_ids(SUPERVISOR_ACCOUNT, &s_uid, &s_gid) != 0) return 14;

    /* Stage 2 — the launch request (collect-then-classify).
     * The collection completes before any fork: a violation
     * entry keeps the receipt-level route (exit 8, as
     * today); closure-equivalent, a poisoned request, and a
     * receive error all take the pre-fork refusal route
     * (exit 15) — no child, no STATUS, no issuance. */
    uint8_t pkt[MAX_PACKET];
    struct collection col;
    collect(&col);
    int cls = classify(&col);
    if (cls == CLS_VIOLATION) return 8;
    if (cls != CLS_PROCEED) return 15;
    memcpy(pkt, col.pkt, (size_t)col.pkt_len);
    ssize_t n = col.pkt_len;
    if (n < 15 || pkt[0] != MSG_LAUNCH_REQUEST || pkt[1] != 0) return 15;
    {
        uint32_t exp_pid = get_u32(pkt + 2);
        uint32_t c_uid = get_u32(pkt + 6);
        uint32_t c_gid = get_u32(pkt + 10);
        size_t rid_len = (size_t)n - 14;
        if (exp_pid != (uint32_t)expected_supervisor) return 15;
        if (exp_pid != (uint32_t)getppid()) return 15;
        if (c_uid != (uint32_t)h_uid || c_gid != (uint32_t)h_gid) return 15;
        if (strlen(run_id) != rid_len || memcmp(pkt + 14, run_id, rid_len) != 0) return 15;
    }

    /* Stage 3 — establishment. The gate pipe first, then the
     * pre-fork expected parent identity, then the fork. */
    int gate[2];
    if (pipe2(gate, O_CLOEXEC) != 0) return 16;
    pid_t expected_parent = getpid();
    pid_t child = fork();
    if (child < 0) return 16;
    if (child == 0) {
        child_main(gate[0], gate[1], expected_parent, h_uid, h_gid, run_id);
    }
    g_child = child;
    close(gate[0]);
    g_gate_w = gate[1];

    /* Stage 4 — pre-handoff liveness observation (site R-1). */
    {
        int st;
        pid_t r;
        do { r = waitpid(child, &st, WNOHANG); } while (r < 0 && errno == EINTR);
        if (r == child) {
            g_held_word = (uint32_t)st;
            g_reaped = true;
            (void)send_abort(RSN_CHILD_LOST_IN_ESTABLISHMENT, true, g_held_word);
            return 3;
        }
        if (r < 0) { /* no word exists; nothing may be fabricated */
            cleanup_child();
            return 4;
        }
    }
    test_hold("after-wnohang");

    /* The pidfd handoff. */
    long start_time = 0;
    {
        char procpath[64];
        snprintf(procpath, sizeof procpath, "/proc/%d/stat", (int)child);
        int fd = open(procpath, O_RDONLY | O_CLOEXEC);
        if (fd < 0) { cleanup_child(); return 5; }
        char buf[4096];
        ssize_t m = read(fd, buf, sizeof buf - 1);
        close(fd);
        if (m <= 0) { cleanup_child(); return 5; }
        buf[m] = '\0';
        char *rp = strrchr(buf, ')');
        if (!rp) { cleanup_child(); return 5; }
        /* fields after comm: field 3 is the first token; the
         * start time is field 22 — token index 19 after comm */
        char *p = rp + 2;
        for (int i = 0; i < 19; i++) {
            p = strchr(p, ' ');
            if (!p) { cleanup_child(); return 5; }
            p++;
        }
        char *end = NULL;
        start_time = strtol(p, &end, 10);
        if (end == p) { cleanup_child(); return 5; }
    }
    int pidfd = (int)syscall(SYS_pidfd_open, child, 0);
    if (pidfd < 0) { cleanup_child(); return 5; }
    {
        uint8_t b[14];
        memset(b, 0, sizeof b);
        b[0] = MSG_PIDFD_HANDOFF;
        put_u32(b + 2, (uint32_t)child);
        put_u64(b + 6, (uint64_t)start_time);
        if (chan_send(b, 14, pidfd) != 0) { close(pidfd); cleanup_child(); return 5; }
    }
    close(pidfd);

    /* The handoff acknowledgement (collect-then-classify).
     * Closure-equivalent keeps the EOF outcome (cleanup,
     * exit 6); a poisoned or violating collection takes the
     * violation route and the packet is not acted on; a
     * receive error takes cleanup + exit 9. A clean ABORT is
     * dispatched per abort_packet_valid(); any other clean
     * packet that is not a well-framed HANDOFF_ACK is a
     * wrong-type violation under plan A.3. (The base source
     * routed non-ABORT framing failures at this site to
     * exit 6; the A.3 reading is recorded in the C0
     * discharge report for Alex's matrix check.) */
    {
        struct collection col2;
        collect(&col2);
        int cls2 = classify(&col2);
        if (cls2 == CLS_VIOLATION || cls2 == CLS_POISONED) { cleanup_child(); return 8; }
        if (cls2 == CLS_ERROR) { cleanup_child(); return 9; }
        if (cls2 == CLS_CLOSURE) { cleanup_child(); return 6; }
        memcpy(pkt, col2.pkt, (size_t)col2.pkt_len);
        n = col2.pkt_len;
    }
    if (pkt[0] == MSG_ABORT) {
        if (abort_packet_valid(pkt, n) != 0) { cleanup_child(); return 8; }
        cleanup_child();
        return 6;
    }
    if (frame_ok(pkt, n, MSG_HANDOFF_ACK, 3, 3) != 0) {
        cleanup_child(); /* wrong type / bad framing: violation route */
        return 8;
    }
    uint8_t ack = pkt[2];
    if (ack == 1 || ack == 2) {          /* site R-2 */
        cleanup_child();
        return 6;
    }
    if (ack == 3) {                      /* site R-3 */
        if (ensure_reaped() != 0) return 4;
        (void)send_abort(RSN_CHILD_TERMINATED_AT_HANDOFF, true, g_held_word);
        return 3;
    }
    if (ack != 0) { cleanup_child(); return 6; }

    /* Stage 5 — the launcher settles. The drop first: a
     * setres failure is Window 1 (still privileged). */
    if (setgroups(0, NULL) != 0 || setresgid(s_gid, s_gid, s_gid) != 0 ||
        setresuid(s_uid, s_uid, s_uid) != 0) {
        (void)send_abort(RSN_SETTLING_FAILED, false, 0);
        cleanup_child();                 /* site R-4 */
        return 7;
    }
    g_privileged = false;
    {
        uid_t ru, eu, su;
        gid_t rg, eg, sg;
        int bad = 0;
        if (getresuid(&ru, &eu, &su) != 0 || getresgid(&rg, &eg, &sg) != 0) bad = 1;
        else if (ru != s_uid || eu != s_uid || su != s_uid ||
                 rg != s_gid || eg != s_gid || sg != s_gid) bad = 1;
        if (!bad && caps_verified_empty() != 0) bad = 1;
        if (bad) {
            (void)send_abort(RSN_SETTLING_FAILED, false, 0);
            cleanup_child();             /* site R-5 (gate EOF) */
            return 7;
        }
    }
    if (identity_recheck() != 0) {
        (void)send_abort(RSN_IDENTITY_RECHECK_FAILED, false, 0);
        cleanup_child();                 /* site R-5 (gate EOF) */
        return 7;
    }
    test_hold("before-gate-ready");
    if (send_simple(MSG_GATE_READY) != 0) {
        cleanup_child();
        return 7;
    }

    /* Stage 6 — await RELEASE (or an ABORT, or EOF),
     * collect-then-classify. Closure-equivalent keeps the
     * EOF outcome (gate handling, STATUS, exit 0); a
     * poisoned collection takes the violation route and
     * the packet is not acted on — a poisoned RELEASE does
     * not actuate and a poisoned ABORT is not dispatched. */
    for (;;) {
        struct collection col3;
        collect(&col3);
        int cls3 = classify(&col3);
        if (cls3 == CLS_VIOLATION || cls3 == CLS_POISONED) { cleanup_child(); return 8; }
        if (cls3 == CLS_ERROR) { cleanup_child(); return 9; }
        if (cls3 == CLS_CLOSURE) {
            /* EOF outcome: release the gated child by the
             * gate's own rule before collecting, or the reap
             * would wait on a child that waits on us */
            if (g_gate_w >= 0) { close(g_gate_w); g_gate_w = -1; }
            break;
        }
        memcpy(pkt, col3.pkt, (size_t)col3.pkt_len);
        n = col3.pkt_len;
        if (pkt[0] == MSG_ABORT) {
            if (abort_packet_valid(pkt, n) != 0) { cleanup_child(); return 8; }
            if (pkt[2] == RSN_CHILD_TERMINATED_PRE_RELEASE)
                abort_receipt_exit(); /* class T: the one STATUS */
            cleanup_child();          /* class F: no STATUS may follow */
            return 8;
        }
        if (frame_ok(pkt, n, MSG_RELEASE, 2, 2) == 0) {
            uint8_t rel = RELEASE_BYTE;
            ssize_t w;
            do { w = write(g_gate_w, &rel, 1); } while (w < 0 && errno == EINTR);
            if (w == 1) {
                close(g_gate_w);
                g_gate_w = -1;
                (void)send_simple(MSG_GATE_ACTUATED);
            } else {
                int e = (w < 0) ? errno : 0;
                uint8_t cls = (w < 0 && e == EPIPE) ? 1 : 2;
                uint8_t b[5];
                memset(b, 0, sizeof b);
                b[0] = MSG_GATE_WRITE_FAILED;
                b[2] = cls;
                b[3] = (uint8_t)((e >> 8) & 0xff);
                b[4] = (uint8_t)(e & 0xff);
                (void)chan_send(b, 5, -1);
                /* report under the flag contract (site R-7) */
                if (ensure_reaped() != 0) return 4;
                if (!g_sent) { g_sent = true; (void)send_status(); }
                return 0;
            }
            break; /* actuated: proceed to Stage 8 */
        }
        /* any other message here is a protocol violation */
        cleanup_child();
        return 8;
    }

    /* Stage 8 — termination and closure (site R-8). */
    if (ensure_reaped() != 0) return 4;
    if (!g_sent) { g_sent = true; (void)send_status(); }
    return 0;
}
#endif /* PILOT_UNIT_TESTS */
