#!/usr/bin/env python3
"""Generate unit_test_c3.c from unit_test_c2.c:
include switched to launcher-c3.c; the C2 block's
refused/EPIPE assertions updated to the named classes;
a Correction 3 block appended inducing SW_ERROR (EBADF)
and SW_COMPLETE_EINTR (full pipe + signal + drain).
SW_SHORT is documented as unforceable on a real pipe
and is not claimed. Replacements are count-checked."""
import hashlib, sys

SRC = "unit_test_c2.c"
DST = "unit_test_c3.c"

text = open(SRC).read()

def rep(old, new, want=1):
    global text
    n = text.count(old)
    if n != want:
        sys.exit(f"count {n} != {want} for: {old[:60]!r}")
    text = text.replace(old, new)

rep('#include "launcher-c2.c"', '#include "launcher-c3.c"')
rep('-> refused, no write",\n            send_status() == -1',
    '-> refused (SW_REFUSED), no write",\n            send_status() == SW_REFUSED')
rep('/* EPIPE: reader gone -> -1, and the process lives */',
    '/* EPIPE: reader gone -> SW_EPIPE, and the process lives */')
rep('chk("C2 send: EPIPE -> -1 (no signal death)", send_status() == -1);',
    'chk("C2 send: EPIPE -> SW_EPIPE (no signal death)", send_status() == SW_EPIPE);')
# The C2 EPIPE fixture is descriptor-aliased: when the
# fresh pipe's read end lands on STATUS_FD, the dup2
# replaces it and the blind close(p4[0]) then closes
# the WRITE end, producing EBADF — which the collapsed
# C2 return (-1) could not distinguish from EPIPE.
# The fixture never reliably induced EPIPE. Fix it to
# close the read end by its current number.
rep('        if (p4[1] != STATUS_FD) { dup2(p4[1], STATUS_FD); close(p4[1]); }\n'
    '        close(p4[0]);',
    '        /* close the READ end by its current number:\n'
    '         * if p4[0] == STATUS_FD the dup2 replaces it\n'
    '         * (read end already gone); a blind close(p4[0])\n'
    '         * would close the write end itself and yield\n'
    '         * EBADF, not EPIPE — the aliased C2 form did\n'
    '         * exactly that under the collapsed return. */\n'
    '        if (p4[1] != STATUS_FD) {\n'
    '            int rd = (p4[0] == STATUS_FD) ? -1 : p4[0];\n'
    '            dup2(p4[1], STATUS_FD); close(p4[1]);\n'
    '            if (rd >= 0) close(rd);\n'
    '        } else {\n'
    '            close(p4[0]);\n'
    '        }')

HELPERS = """#include <pthread.h>
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

int main(void) {"""
rep("int main(void) {", HELPERS)

C3_BLOCK = """    }

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
"""

rep('    }\n\n    printf("unit: %d/%d PASS\\n", total - fails, total);',
    C3_BLOCK + '\n    printf("unit: %d/%d PASS\\n", total - fails, total);')

open(DST, "w").write(text)
print(f"{DST}: {len(text.splitlines())} lines, "
      f"sha256 {hashlib.sha256(text.encode()).hexdigest()}")
