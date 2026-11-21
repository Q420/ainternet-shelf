#!/usr/bin/env python3
"""Generate launcher-c3.c from launcher-c2.c (pin
b6b373b0af158a99...), implementing chunk C3-1 of the
Correction 3 chunk sheet: send_status() returns the
contract's classification instead of collapsing every
outcome into 0/-1, and the three call sites treat the
two complete classes as success. Input hash-verified;
the send_status replacement is a marker splice with
assertions, the call-site change is count-checked."""
import hashlib, sys

SRC = "launcher-c2.c"
DST = "launcher-c3.c"
EXPECT = "b6b373b0af158a99c8ab245f9df7a64a75460e09e7cb6ee14627aab0cd8580c2"

text = open(SRC).read()
h = hashlib.sha256(text.encode()).hexdigest()
if h != EXPECT:
    sys.exit(f"INPUT HASH MISMATCH: {h} != {EXPECT}")

NEW_FN = """/* The STATUS transmission, on the dedicated pipe (the
 * S3.5 STATUS Pipe Contract section 4). The record is the
 * pin's 10-byte body, byte-identical; only the transport
 * changed. The return is the contract's classification
 * (Correction 3): SW_COMPLETE (0), an uninterrupted
 * complete write; SW_COMPLETE_EINTR (1), a complete
 * write that needed at least one EINTR retry;
 * SW_REFUSED (-1), the SIGPIPE disposition is not
 * SIG_IGN — no attempt is made and the descriptor is
 * left open; SW_EPIPE (-2); SW_ERROR (-3), any other
 * errno; SW_SHORT (-4), a count other than 10. The
 * descriptor is closed after an attempt, complete or
 * not. Callers treat the two complete classes as
 * success and every other class as STATUS transport
 * failure. The shared-flag contract is unchanged:
 * g_sent is set by the caller immediately before this
 * one transmission, never retried. */
enum status_write_class {
    SW_COMPLETE = 0,
    SW_COMPLETE_EINTR = 1,
    SW_REFUSED = -1,
    SW_EPIPE = -2,
    SW_ERROR = -3,
    SW_SHORT = -4
};
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
        return SW_REFUSED;
    }
    int retried = 0;
    ssize_t n;
    for (;;) {
        n = write(STATUS_FD, b, 10);
        if (n >= 0) break;
        if (errno == EINTR) { retried = 1; continue; }
        int e = errno;
        close(STATUS_FD);
        return e == EPIPE ? SW_EPIPE : SW_ERROR;
    }
    close(STATUS_FD);
    if (n != 10) return SW_SHORT;
    return retried ? SW_COMPLETE_EINTR : SW_COMPLETE;
}
"""

start_marker = "/* The STATUS transmission, on the dedicated pipe (the"
start = text.find(start_marker)
if start < 0 or text.find(start_marker, start + 1) >= 0:
    sys.exit("start marker not unique/found")
fn_sig = text.find("static int send_status(void) {", start)
if fn_sig < 0:
    sys.exit("send_status signature not found")
end = text.find("\n}\n", fn_sig)
if end < 0:
    sys.exit("send_status end not found")
end += len("\n}\n")
text = text[:start] + NEW_FN + text[end:]

n_sites = text.count("send_status() != 0")
if n_sites != 3:
    sys.exit(f"call-site count {n_sites} != 3")
text = text.replace("send_status() != 0", "send_status() < 0")

open(DST, "w").write(text)
print(f"{DST}: {len(text.splitlines())} lines, "
      f"sha256 {hashlib.sha256(text.encode()).hexdigest()}")
