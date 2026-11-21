/* Bench 3 child — candidate STATUS transports, real C.
 *
 * fd 3 = control SEQPACKET socket (residue pre-queued by the
 *        parent; the child NEVER reads it — the F-3 condition).
 * mode "pipe": fd 4 = STATUS pipe write end. Write the 10-byte
 *        STATUS record (code, own pid, test word), close, exit 0.
 *        Write failure -> exit 45 (transport failure, explicit).
 * mode "pair": fd 5 = dedicated STATUS SEQPACKET socket. AUDIT
 *        first: the receive queue must be empty (FIONREAD 0 and a
 *        non-blocking recvmsg returns EAGAIN). Any record present
 *        is supervisor-originated -> contract violation: exit 44,
 *        STATUS withheld. Otherwise send the record, exit 0;
 *        send failure -> exit 45.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <poll.h>
#include <stdint.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#define TEST_WORD 0x11223344u

static void put_u32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)(v & 0xffu); p[1] = (uint8_t)((v >> 8) & 0xffu);
    p[2] = (uint8_t)((v >> 16) & 0xffu); p[3] = (uint8_t)((v >> 24) & 0xffu);
}

static void build_record(uint8_t b[10]) {
    memset(b, 0, 10);
    b[0] = 0x07u;
    put_u32(b + 2, (uint32_t)getpid());
    put_u32(b + 6, TEST_WORD);
}

int main(int argc, char **argv) {
    if (argc != 2) return 46;
    uint8_t rec[10];
    build_record(rec);
    if (strcmp(argv[1], "pipe") == 0) {
        size_t off = 0;
        while (off < 10) {
            ssize_t n = write(4, rec + off, 10 - off);
            if (n < 0) {
                if (errno == EINTR) continue;
                return 45;
            }
            if (n == 0) return 45;
            off += (size_t)n;
        }
        close(4);
        return 0;
    }
    if (strcmp(argv[1], "pair") == 0) {
        /* Audit v2 (bench-proven correction): a bare recvmsg
         * return of 0 is ambiguous — EOF (peer write side shut,
         * the prevention state) and a queued zero-length packet
         * look identical. The poll mask captured BEFORE the read
         * separates them: RDHUP/HUP set + 0 = EOF, clean; no
         * RDHUP + 0 = a live zero-length packet, violation.
         * Residual corner (named in the report): a zero packet
         * queued BEFORE the peer's shutdown is indistinguishable
         * from clean EOF; prevention is therefore mandatory and
         * ordered before any other supervisor activity. */
        int avail = -1;
        if (ioctl(5, FIONREAD, &avail) != 0) return 45;
        if (avail != 0) return 44;
        struct pollfd pfd;
        pfd.fd = 5; pfd.events = POLLIN | POLLRDHUP; pfd.revents = 0;
        if (poll(&pfd, 1, 0) < 0) return 45;
        if (!(pfd.revents & POLLIN)) {
            /* nothing readable: clean (EAGAIN state) */
        } else {
            int eof_state = (pfd.revents & (POLLRDHUP | POLLHUP)) != 0;
            uint8_t buf[64];
            struct msghdr mh;
            struct iovec iov;
            memset(&mh, 0, sizeof mh);
            iov.iov_base = buf; iov.iov_len = sizeof buf;
            mh.msg_iov = &iov; mh.msg_iovlen = 1;
            ssize_t pn = recvmsg(5, &mh, MSG_DONTWAIT);
            if (pn > 0) return 44;            /* byte-bearing packet */
            if (pn == 0 && !eof_state) return 44; /* live zero packet */
            if (pn == 0 && eof_state) {
                /* EOF: clean, nothing was queued */
            } else if (pn < 0 && errno != EAGAIN && errno != EWOULDBLOCK)
                return 45;
        }
        ssize_t n;
        do { n = sendmsg(5, &(struct msghdr){
                 .msg_iov = &(struct iovec){.iov_base = rec,
                                            .iov_len = 10},
                 .msg_iovlen = 1}, MSG_NOSIGNAL); } while (n < 0 && errno == EINTR);
        if (n != 10) return 45;
        close(5);
        return 0;
    }
    return 46;
}
