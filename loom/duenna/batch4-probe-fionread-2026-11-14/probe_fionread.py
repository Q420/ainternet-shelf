#!/usr/bin/env python3
"""probe_fionread.py — does FIONREAD (SIOCINQ) on AF_UNIX SOCK_SEQPACKET
report bytes across the WHOLE receive queue, or only the head record?

Alex's Rev 5 test sequence: [zero record, zero record, packet, shutdown].
Question: after consuming the first zero record, with a zero record at
the head and a byte-bearing packet behind it, what do the candidate
primitives report?

Primitives tested at each step:
  - MSG_PEEK recv (head record only, by construction)
  - FIONREAD ioctl (0x541B)
  - poll events (POLLIN / POLLRDHUP)
"""
import array
import fcntl
import select
import socket
import termios

FIONREAD = 0x541B


def fionread(s):
    b = array.array("i", [0])
    fcntl.ioctl(s.fileno(), FIONREAD, b, True)
    return b[0]


def peek_len(s):
    try:
        data, anc, flags, addr = s.recvmsg(4096, 0, socket.MSG_PEEK | socket.MSG_DONTWAIT)
        return len(data)
    except BlockingIOError:
        return "EAGAIN"
    except OSError as e:
        return f"ERR {e.errno}"


def poll_state(s):
    p = select.poll()
    p.register(s, select.POLLIN | select.POLLRDHUP)
    ev = dict(p.poll(0))
    r = ev.get(s.fileno(), 0)
    names = []
    if r & select.POLLIN:
        names.append("POLLIN")
    if r & select.POLLRDHUP:
        names.append("POLLRDHUP")
    if r & select.POLLHUP:
        names.append("POLLHUP")
    if r & select.POLLERR:
        names.append("POLLERR")
    return "|".join(names) if names else "none"


def state(s, label):
    print(f"  {label}: FIONREAD={fionread(s)} PEEK={peek_len(s)} POLL={poll_state(s)}")


def seq(label, sends, shutdown):
    print(f"== {label} ==")
    a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    for payload in sends:
        b.send(payload)
    if shutdown:
        b.shutdown(socket.SHUT_WR)
    state(a, "before any recv")
    for i in range(len(sends) + 1):
        try:
            data, anc, flags, addr = a.recvmsg(4096, 0, socket.MSG_DONTWAIT)
            print(f"  recv#{i + 1}: n={len(data)} flags={flags}")
        except BlockingIOError:
            print(f"  recv#{i + 1}: EAGAIN")
            break
        state(a, f"after recv#{i + 1}")
    a.close()
    b.close()
    print()


# Alex's sequence: Z, Z, P, shutdown
seq("T1 [Z, Z, P(5 bytes), shutdown]", [b"", b"", b"HELLO"], True)
# Z, Z, shutdown (no packet anywhere)
seq("T2 [Z, Z, shutdown]", [b"", b""], True)
# P queued alone behind nothing, channel open
seq("T3 [P(5 bytes)] open", [b"HELLO"], False)
# Z, P, shutdown (single zero ahead of the packet)
seq("T4 [Z, P(5 bytes), shutdown]", [b"", b"HELLO"], True)
# nothing at all, peer shutdown only
seq("T5 [shutdown only]", [], True)
