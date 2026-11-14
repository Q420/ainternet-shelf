#define _GNU_SOURCE  /* as in launcher.c's own preamble (line 97) */
/* bench_child.c — the Correction-1 drain, lifted VERBATIM
 * from launcher.c pin 3e0482c050ddf263a5b1021d84073259591a00d4193
 * (closure_check lines 350-400, teardown_drain lines 470-546,
 * hook stubs in their production (non-test) macro form).
 * Bench main at the bottom: send the STATUS word on fd 3,
 * run teardown_drain(), exit. Nothing else. */
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
#define hook_note_closed(count) ((void)0)
#define hook_note_drained(records, fds) ((void)0)
#define hook_fail_fionread() 0
#define hook_fail_peek() 0
#define hook_stall_recv()  ((void)0)
#define hook_stall_check() ((void)0)
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
/* Teardown drain (C0 Correction 1, F-3; Ben's ruling).
 * Runs after the protocol is complete, before exit, on
 * every exit path: receive-and-discard whatever records
 * remain queued until the queue is empty of records, so
 * the exit leaves nothing unread for the kernel to reset
 * against the final STATUS. Emptiness is the section A.2
 * closure triple, reused as an observation only. Drained
 * records are never examined, classified or acted on; a
 * descriptor arriving with one is closed on sight through
 * the receipt ancillary accounting and is never installed.
 * Best effort by design: any observation or receive
 * failure simply ends the drain; teardown never hangs,
 * never retries the protocol and never changes an exit
 * code. No-ops when fd 3 is not the SEQPACKET channel. */
static void teardown_drain(void) {
    int stype = 0;
    socklen_t sl = sizeof stype;
    if (getsockopt(CHANNEL_FD, SOL_SOCKET, SO_TYPE, &stype, &sl) != 0) return;
    if (stype != SOCK_SEQPACKET) return;
    int records = 0, fds_closed = 0;
    uint8_t buf[MAX_PACKET];
    char cbuf[CMSG_SPACE(sizeof(int) * 8)];
    for (int i = 0; i < 1024; i++) {
        struct iovec iov = { buf, sizeof buf };
        struct msghdr mh;
        memset(&mh, 0, sizeof mh);
        mh.msg_iov = &iov;
        mh.msg_iovlen = 1;
        mh.msg_control = cbuf;
        mh.msg_controllen = sizeof cbuf;
        ssize_t n;
        do { n = recvmsg(CHANNEL_FD, &mh, MSG_DONTWAIT); }
        while (n < 0 && errno == EINTR);
        if (n < 0) {
            if (errno != EAGAIN) break;
            /* EAGAIN says no record is receivable this instant;
             * keep draining only on a demonstrable race — bytes
             * queued between the receive and this check. */
            int avail = -1;
            if (ioctl(CHANNEL_FD, FIONREAD, &avail) == 0 && avail > 0)
                continue;
            break;
        }
        int closed = 0;
        for (struct cmsghdr *c = CMSG_FIRSTHDR(&mh); c;
             c = CMSG_NXTHDR(&mh, c)) {
            if (c->cmsg_level == SOL_SOCKET &&
                c->cmsg_type == SCM_RIGHTS) {
                int cnt = (int)((c->cmsg_len - CMSG_LEN(0)) /
                                sizeof(int));
                int *fds = (int *)CMSG_DATA(c);
                for (int j = 0; j < cnt; j++) {
                    close(fds[j]);
                    closed++;
                }
            }
        }
        if (closed > 0) {
            hook_note_closed(closed);
            fds_closed += closed;
        }
        if (n == 0 && closed == 0) {
            /* A zero with nothing behind it is indistinguishable
             * from the empty-queue phantom (probe sequence E):
             * when the closure triple says the queue is empty of
             * records, the drain is done and the zero is not
             * counted — the drained count is a floor, never an
             * over-claim. */
            int obs = closure_check();
            if (obs == OBS_CLOSURE || obs == OBS_FAIL) break;
            /* OBS_CONTINUE / OBS_ANC_HEAD: a real zero, with
             * more records queued behind it. */
        }
        records++;
    }
    hook_note_drained(records, fds_closed);
}

int main(void) {
    static const unsigned char status[12] =
        { 0x07, 'S','T','A','T','U','S','-','w','o','r','d' };
    struct iovec iov = { (void *)status, sizeof status };
    struct msghdr mh;
    memset(&mh, 0, sizeof mh);
    mh.msg_iov = &iov;
    mh.msg_iovlen = 1;
    (void)sendmsg(CHANNEL_FD, &mh, 0);
    teardown_drain();
    return 0;
}
