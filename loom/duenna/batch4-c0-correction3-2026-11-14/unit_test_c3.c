/* Unit tests for the corrected launcher's pure functions
 * plus the C0 Correction 2 STATUS-pipe functions:
 * the run-ID validator (finding 1) and the file-capability
 * check (finding 4). Built with -DPILOT_UNIT_TESTS
 * -DPILOT_TEST_HOOKS against launcher.c; run under ASan. */
#define PILOT_UNIT_TESTS 1
#include "launcher-c3.c"

static int fails = 0, total = 0;
static void chk(const char *name, int cond) {
    total++;
    printf("[%s] %s\n", cond ? "PASS" : "FAIL", name);
    if (!cond) fails++;
}

#include <pthread.h>
static void eintr_nop(int sig) { (void)sig; }
static pthread_t eintr_main;
static int eintr_ep = -1;
static void *eintr_helper(void *arg) {
    (void)arg;
    struct timespec ts = {0, 150 * 1000 * 1000};
    nanosleep(&ts, NULL);
    pthread_kill(eintr_main, SIGUSR1);
    nanosleep(&ts, NULL);
    int fl = fcntl(eintr_ep, F_GETFL);
    fcntl(eintr_ep, F_SETFL, fl | O_NONBLOCK);
    static char sink[8192];
    while (read(eintr_ep, sink, sizeof sink) > 0) { }
    return NULL;
}

int main(void) {
    /* Finding 1 — the valid path FIRST (the draft's smoke
     * test never exercised it; that is how the offset bug
     * passed) */
    chk("runid valid canonical", run_id_valid("PILOT-20261113-001") == 1);
    chk("runid valid battery len 1", run_id_valid("A-20261113-001") == 1);
    {
        char buf[128];
        memset(buf, 'B', 64);
        buf[64] = '\0';
        strcat(buf, "-20261113-999");
        chk("runid valid battery len 64, counter 999", run_id_valid(buf) == 1);
        strcat(buf, "X");
        chk("runid invalid over-long", run_id_valid(buf) == 0);
    }
    chk("runid valid leap date 20280229", run_id_valid("PILOT-20280229-001") == 1);
    chk("runid invalid counter 000", run_id_valid("PILOT-20261113-000") == 0);
    chk("runid invalid counter 2 digits", run_id_valid("PILOT-20261113-01") == 0);
    chk("runid invalid counter 4 digits", run_id_valid("PILOT-20261113-0001") == 0);
    chk("runid invalid month 00", run_id_valid("PILOT-20260013-001") == 0);
    chk("runid invalid month 13", run_id_valid("PILOT-20261313-001") == 0);
    chk("runid invalid day 00", run_id_valid("PILOT-20261100-001") == 0);
    chk("runid invalid day 32", run_id_valid("PILOT-20261132-001") == 0);
    chk("runid invalid Feb 29 non-leap 2027", run_id_valid("PILOT-20270229-001") == 0);
    chk("runid invalid Feb 30", run_id_valid("PILOT-20280230-001") == 0);
    chk("runid invalid Apr 31", run_id_valid("PILOT-20260431-001") == 0);
    chk("runid valid Apr 30", run_id_valid("PILOT-20260430-001") == 1);
    chk("runid invalid separator inside date", run_id_valid("PILOT-2026-113-001") == 0);
    chk("runid invalid missing separator", run_id_valid("PILOT20261113-001") == 0);
    chk("runid invalid battery leading dash", run_id_valid("-PILOT-20261113-001") == 0);
    chk("runid invalid battery trailing dash", run_id_valid("PILOT--20261113-001") == 0);
    chk("runid invalid battery bad char", run_id_valid("PI_LOT-20261113-001") == 0);
    chk("runid invalid empty", run_id_valid("") == 0);
    chk("runid invalid two chars (no OOB)", run_id_valid("a-") == 0);
    chk("runid invalid short junk (no OOB)", run_id_valid("x-y") == 0);
    chk("runid invalid date letters", run_id_valid("PILOT-2026AA13-001") == 0);

    /* Finding 4 — file capability check */
    {
        char tmpl[] = "/tmp/captestXXXXXX";
        int fd = mkstemp(tmpl);
        chk("caps: fixture created", fd >= 0);
        if (fd >= 0) close(fd);
        chk("caps: plain file (ENODATA) is empty", file_caps_empty(tmpl) == 0);
        /* crafted nonzero capability set via the raw xattr,
         * in the kernel's real layout: magic_etc, then
         * permitted/inheritable word pairs (20 bytes) */
        struct {
            uint32_t magic_etc;
            struct { uint32_t permitted, inheritable; } d[2];
        } cap;
        memset(&cap, 0, sizeof cap);
        cap.magic_etc = 0x02000000u;              /* VFS_CAP_REVISION_2 */
        cap.d[0].permitted = (1u << 13);          /* CAP_NET_RAW */
        ssize_t r = setxattr(tmpl, "security.capability", &cap, sizeof cap, 0);
        if (r == 0) {
            chk("caps: nonzero capability set fails", file_caps_empty(tmpl) == -1);
            /* and an all-zero rev2 set reads as empty */
            memset(&cap, 0, sizeof cap);
            cap.magic_etc = 0x02000000u;
            r = setxattr(tmpl, "security.capability", &cap, sizeof cap, 0);
            chk("caps: all-zero rev2 set is empty", r == 0 && file_caps_empty(tmpl) == 0);
            /* effective vector alone (inside magic_etc) fails */
            cap.magic_etc = 0x02000000u | 1u;
            r = setxattr(tmpl, "security.capability", &cap, sizeof cap, 0);
            chk("caps: effective-only set fails", r == 0 && file_caps_empty(tmpl) == -1);
        } else {
            printf("[SKIP] caps: setxattr unavailable in this context (errno %d)\n", errno);
        }
        /* an error other than ENODATA fails closed */
        setenv("PILOT_HOOK_XATTR_ERROR", "95", 1); /* ENOTSUP */
        chk("caps: ENOTSUP fails closed", file_caps_empty(tmpl) == -1);
        setenv("PILOT_HOOK_XATTR_ERROR", "5", 1); /* EIO */
        chk("caps: EIO fails closed", file_caps_empty(tmpl) == -1);
        unsetenv("PILOT_HOOK_XATTR_ERROR");
        chk("caps: missing file fails", file_caps_empty("/nonexistent-xyz") == -1);
        unlink(tmpl);
    }

    /* C0 — classification as a pure function of the
     * collected-entry representation (chunk C0-7) */
    {
        struct collection c;
        memset(&c, 0, sizeof c);
        c.has_packet = 1;
        chk("C0 classify: clean packet -> PROCEED", classify(&c) == CLS_PROCEED);
        c.pending_zeros = 2;
        chk("C0 classify: zeros + packet -> POISONED", classify(&c) == CLS_POISONED);
        memset(&c, 0, sizeof c);
        c.pending_zeros = 1; c.closure = 1;
        chk("C0 classify: zeros + closure -> CLOSURE", classify(&c) == CLS_CLOSURE);
        memset(&c, 0, sizeof c);
        c.violation = 1;
        chk("C0 classify: ancillary entry -> VIOLATION", classify(&c) == CLS_VIOLATION);
        memset(&c, 0, sizeof c);
        c.pending_zeros = 1; c.violation = 2;
        chk("C0 classify: zeros + truncated entry -> VIOLATION", classify(&c) == CLS_VIOLATION);
        memset(&c, 0, sizeof c);
        c.malformed = 1;
        chk("C0 classify: malformed entry -> VIOLATION", classify(&c) == CLS_VIOLATION);
        memset(&c, 0, sizeof c);
        c.error = 1;
        chk("C0 classify: error -> ERROR", classify(&c) == CLS_ERROR);
        memset(&c, 0, sizeof c);
        chk("C0 classify: empty collection -> ERROR (guard)", classify(&c) == CLS_ERROR);
    }

    /* C0 — collect() itself, driven over a socketpair
     * placed on descriptor 3 (the channel descriptor).
     * All sends for a case happen BEFORE the receive end
     * is dup2'd onto 3: socketpair may hand back fd 3 as
     * the SEND end, and dup2 would clobber it mid-case. */
    {
        int sv[2];
        struct collection c;
        uint8_t rel[2] = { 0x05, 0x00 };

        chk("C0 collect: socketpair 1", socketpair(AF_UNIX, SOCK_SEQPACKET, 0, sv) == 0);
        send(sv[0], rel, 2, MSG_NOSIGNAL);
        if (sv[1] != 3) { dup2(sv[1], 3); close(sv[1]); }
        collect(&c);
        chk("C0 collect: packet only -> PROCEED",
            c.has_packet == 1 && c.pending_zeros == 0 && classify(&c) == CLS_PROCEED);
        close(sv[0]); close(3);

        chk("C0 collect: socketpair 2", socketpair(AF_UNIX, SOCK_SEQPACKET, 0, sv) == 0);
        send(sv[0], "", 0, MSG_NOSIGNAL);
        send(sv[0], rel, 2, MSG_NOSIGNAL);
        if (sv[1] != 3) { dup2(sv[1], 3); close(sv[1]); }
        collect(&c);
        chk("C0 collect: zero then packet -> POISONED",
            c.has_packet == 1 && c.pending_zeros == 1 && classify(&c) == CLS_POISONED);
        close(sv[0]); close(3);

        chk("C0 collect: socketpair 3", socketpair(AF_UNIX, SOCK_SEQPACKET, 0, sv) == 0);
        send(sv[0], "", 0, MSG_NOSIGNAL);
        shutdown(sv[0], SHUT_WR);
        if (sv[1] != 3) { dup2(sv[1], 3); close(sv[1]); }
        collect(&c);
        chk("C0 collect: zero then shutdown -> CLOSURE",
            c.closure == 1 && classify(&c) == CLS_CLOSURE);
        close(sv[0]); close(3);

        /* zero, then a zero-length descriptor-bearing
         * record at the head, then shutdown (NQ4' shape):
         * the head-ancillary check sees it, the real
         * receive collects it as a violation entry, and
         * the descriptor is closed at receipt */
        chk("C0 collect: socketpair 4", socketpair(AF_UNIX, SOCK_SEQPACKET, 0, sv) == 0);
        {
            int pipefd[2];
            if (pipe(pipefd) != 0) { /* counted below via chk path */ }
            send(sv[0], "", 0, MSG_NOSIGNAL);
            struct iovec iov = { (void *)"", 0 };
            char cbuf[CMSG_SPACE(sizeof(int))];
            struct msghdr mh;
            memset(&mh, 0, sizeof mh);
            mh.msg_iov = &iov; mh.msg_iovlen = 1;
            mh.msg_control = cbuf; mh.msg_controllen = sizeof cbuf;
            struct cmsghdr *cm = CMSG_FIRSTHDR(&mh);
            cm->cmsg_level = SOL_SOCKET; cm->cmsg_type = SCM_RIGHTS;
            cm->cmsg_len = CMSG_LEN(sizeof(int));
            memcpy(CMSG_DATA(cm), &pipefd[0], sizeof(int));
            sendmsg(sv[0], &mh, MSG_NOSIGNAL);
            shutdown(sv[0], SHUT_WR);
            if (sv[1] != 3) { dup2(sv[1], 3); close(sv[1]); }
            int fds_before = 0, fds_after = 0;
            DIR *d = opendir("/proc/self/fd");
            while (readdir(d)) fds_before++;
            closedir(d);
            collect(&c);
            chk("C0 collect: zero + head ancillary record -> VIOLATION (NQ4' shape)",
                c.violation == 1 && classify(&c) == CLS_VIOLATION);
            d = opendir("/proc/self/fd");
            while (readdir(d)) fds_after++;
            closedir(d);
            chk("C0 collect: peek/receipt descriptors closed (fd count stable)",
                fds_after == fds_before);
            close(pipefd[0]); close(pipefd[1]);
        }
        close(sv[0]); close(3);

        /* zero, plain zero, descriptor-bearing record,
         * shutdown (NQ5' shape — Ben's ruled residue):
         * the closure outcome is taken */
        chk("C0 collect: socketpair 5", socketpair(AF_UNIX, SOCK_SEQPACKET, 0, sv) == 0);
        {
            int pipefd[2];
            if (pipe(pipefd) != 0) { /* counted below via chk path */ }
            send(sv[0], "", 0, MSG_NOSIGNAL);
            send(sv[0], "", 0, MSG_NOSIGNAL);
            struct iovec iov = { (void *)"", 0 };
            char cbuf[CMSG_SPACE(sizeof(int))];
            struct msghdr mh;
            memset(&mh, 0, sizeof mh);
            mh.msg_iov = &iov; mh.msg_iovlen = 1;
            mh.msg_control = cbuf; mh.msg_controllen = sizeof cbuf;
            struct cmsghdr *cm = CMSG_FIRSTHDR(&mh);
            cm->cmsg_level = SOL_SOCKET; cm->cmsg_type = SCM_RIGHTS;
            cm->cmsg_len = CMSG_LEN(sizeof(int));
            memcpy(CMSG_DATA(cm), &pipefd[0], sizeof(int));
            sendmsg(sv[0], &mh, MSG_NOSIGNAL);
            shutdown(sv[0], SHUT_WR);
            if (sv[1] != 3) { dup2(sv[1], 3); close(sv[1]); }
            collect(&c);
            chk("C0 collect: zero + zero + ancillary behind -> CLOSURE (ruled residue)",
                c.closure == 1 && classify(&c) == CLS_CLOSURE);
            close(pipefd[0]); close(pipefd[1]);
        }
        close(sv[0]); close(3);
    }


    /* ---- C0 Correction 2: the STATUS pipe ---- */
    {
        /* the disposition guard fires before any write:
         * with SIGPIPE at SIG_DFL the send must refuse */
        signal(SIGPIPE, SIG_DFL);
        int sp[2];
        chk("C2 pipe: fixture", pipe(sp) == 0);
        if (sp[1] != STATUS_FD) { dup2(sp[1], STATUS_FD); close(sp[1]); }
        g_child = 4242; g_held_word = 0x2A00u; /* exited 42 */
        chk("C2 send: SIGPIPE not ignored -> refused (SW_REFUSED), no write",
            send_status() == SW_REFUSED);
        {
            int fl = fcntl(sp[0], F_GETFL); fcntl(sp[0], F_SETFL, fl | O_NONBLOCK);
            char buf[16];
            chk("C2 send: refused send wrote nothing", read(sp[0], buf, 16) < 0);
            fcntl(sp[0], F_SETFL, fl);
        }
        close(sp[0]);
        close(STATUS_FD);   /* the matrix starts from absent */
        signal(SIGPIPE, SIG_IGN);
        /* status_fd_valid: the precondition matrix */
        chk("C2 valid: writer absent -> 0", status_fd_valid() == 0);
        int p2[2];
        chk("C2 pipe: fixture 2", pipe(p2) == 0);
        if (p2[1] != STATUS_FD) { dup2(p2[1], STATUS_FD); close(p2[1]); }
        chk("C2 valid: pipe writer -> 1", status_fd_valid() == 1);
        {
            int fl = fcntl(STATUS_FD, F_GETFD);
            fcntl(STATUS_FD, F_SETFD, fl | FD_CLOEXEC);
            chk("C2 valid: CLOEXEC set -> 0", status_fd_valid() == 0);
            fcntl(STATUS_FD, F_SETFD, fl & ~FD_CLOEXEC);
            chk("C2 valid: CLOEXEC cleared -> 1", status_fd_valid() == 1);
        }
        dup2(p2[0], STATUS_FD);
        chk("C2 valid: pipe read end -> 0", status_fd_valid() == 0);
        {
            char tmpl[] = "/tmp/statustestXXXXXX";
            int rf = mkstemp(tmpl);
            dup2(rf, STATUS_FD); close(rf); unlink(tmpl);
            chk("C2 valid: regular file -> 0", status_fd_valid() == 0);
        }
        /* a complete send: exact record, descriptor closed */
        if (p2[1] != STATUS_FD) { /* p2[1] was closed by the dups; reopen path */ }
        int p3[2];
        chk("C2 pipe: fixture 3", pipe(p3) == 0);
        if (p3[1] != STATUS_FD) { dup2(p3[1], STATUS_FD); close(p3[1]); }
        g_child = 4242; g_held_word = 0x2A00u;
        chk("C2 send: complete write returns 0", send_status() == 0);
        chk("C2 send: descriptor closed after the attempt",
            fcntl(STATUS_FD, F_GETFD) < 0);
        {
            uint8_t rb[10];
            ssize_t rn = read(p3[0], rb, 10);
            uint32_t pid_be, word_be;
            memcpy(&pid_be, rb + 2, 4); memcpy(&word_be, rb + 6, 4);
            chk("C2 send: record is MSG_STATUS + pid + word verbatim",
                rn == 10 && rb[0] == MSG_STATUS && ntohl(pid_be) == 4242
                && ntohl(word_be) == 0x2A00u);
        }
        /* EPIPE: reader gone -> SW_EPIPE, and the process lives */
        int p4[2];
        chk("C2 pipe: fixture 4", pipe(p4) == 0);
        /* close the READ end by its current number:
         * if p4[0] == STATUS_FD the dup2 replaces it
         * (read end already gone); a blind close(p4[0])
         * would close the write end itself and yield
         * EBADF, not EPIPE — the aliased C2 form did
         * exactly that under the collapsed return. */
        if (p4[1] != STATUS_FD) {
            int rd = (p4[0] == STATUS_FD) ? -1 : p4[0];
            dup2(p4[1], STATUS_FD); close(p4[1]);
            if (rd >= 0) close(rd);
        } else {
            close(p4[0]);
        }
        chk("C2 send: EPIPE -> SW_EPIPE (no signal death)", send_status() == SW_EPIPE);
        chk("C2 send: alive after EPIPE", 1);
    }

    /* Correction 3 — the classification, induced class by
     * class (chunk C3-1). SW_SHORT is documented as
     * unforceable on a real pipe (10 < PIPE_BUF) and is
     * not claimed here. */
    {
        struct sigaction ign; memset(&ign, 0, sizeof ign);
        ign.sa_handler = SIG_IGN; sigaction(SIGPIPE, &ign, NULL);
        g_child = 4242; g_held_word = 0x11223344;
        /* suite hygiene: SIGUSR1 must be deliverable in
         * this thread for the induction below, whatever
         * earlier checks left in the signal mask */
        sigset_t usr1; sigemptyset(&usr1); sigaddset(&usr1, SIGUSR1);
        pthread_sigmask(SIG_UNBLOCK, &usr1, NULL);

        /* SW_ERROR: descriptor 4 closed -> write is EBADF */
        close(STATUS_FD);
        chk("C3 class: closed fd -> SW_ERROR", send_status() == SW_ERROR);

        /* SW_COMPLETE_EINTR: fill the pipe so the write
         * blocks, interrupt it with SIGUSR1 (handler
         * without SA_RESTART), drain so the retry
         * completes. Up to 3 attempts; the class must be
         * observed at least once. */
        int eintr_seen = 0;
        for (int attempt = 0; attempt < 3 && !eintr_seen; attempt++) {
            int ep[2];
            if (pipe(ep) != 0) break;
            /* place the write end on STATUS_FD without
             * destroying the read end: if the read end
             * landed on STATUS_FD, re-home it first — a
             * dup2 onto it closes the pipe's only reader
             * and every write EPIPEs (the aliasing the
             * C3 debug round found in this fixture). */
            int rd = ep[0];
            if (rd == STATUS_FD) {
                int nrd = fcntl(rd, F_DUPFD, STATUS_FD + 1);
                close(rd); rd = nrd;
            }
            if (ep[1] != STATUS_FD) { dup2(ep[1], STATUS_FD); close(ep[1]); }
            int fl = fcntl(STATUS_FD, F_GETFL);
            fcntl(STATUS_FD, F_SETFL, fl | O_NONBLOCK);
            static char filler[4096]; memset(filler, 'f', sizeof filler);
            long filled = 0; ssize_t w;
            while ((w = write(STATUS_FD, filler, sizeof filler)) > 0) filled += w;
            fcntl(STATUS_FD, F_SETFL, fl);
            if (filled < 4096) { close(rd); close(STATUS_FD); continue; }
            struct sigaction sa; memset(&sa, 0, sizeof sa);
            sa.sa_handler = eintr_nop;
            sigaction(SIGUSR1, &sa, NULL);
            eintr_ep = rd;
            eintr_main = pthread_self();
            pthread_t th;
            if (pthread_create(&th, NULL, eintr_helper, NULL) != 0) {
                close(rd); close(STATUS_FD); continue;
            }
            int rc = send_status();
            pthread_join(th, NULL);
            if (rc == SW_COMPLETE_EINTR) eintr_seen = 1;
            close(rd);
        }
        chk("C3 class: interrupted completion -> SW_COMPLETE_EINTR (induced)",
            eintr_seen == 1);
    }

    printf("unit: %d/%d PASS\n", total - fails, total);
    return fails ? 1 : 0;
}
