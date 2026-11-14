import select, socket

def masks(ev):
    names = []
    for name in ["POLLIN","POLLPRI","POLLOUT","POLLERR","POLLHUP","POLLRDHUP","POLLNVAL"]:
        bit = getattr(select, name, 0)
        if bit and ev & bit: names.append(name)
    return "|".join(names) or "-"

def newpair():
    a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    p = select.poll(); p.register(b, select.POLLIN | select.POLLRDHUP)
    return a, b, p

def poll0(p):
    ev = p.poll(0)
    return masks(ev[0][1]) if ev else "none"

def peek(b):
    try:
        data, anc, fl, _ = b.recvmsg(128, socket.CMSG_SPACE(32), socket.MSG_PEEK | socket.MSG_DONTWAIT)
        return f"n={len(data)} controllen={sum(1 for _ in anc)}"
    except BlockingIOError:
        return "EAGAIN"
    except Exception as e:
        return f"{type(e).__name__}"

def recv0(b):
    data, anc, fl, _ = b.recvmsg(128, socket.CMSG_SPACE(32))
    return len(data)

# Q1: empty record -> receive -> poll
a, b, p = newpair(); a.send(b"")
print(f"Q1 recv n={recv0(b)} poll0={poll0(p)}")
a.close(); b.close()
# Q2: shutdown -> receive -> poll, peek
a, b, p = newpair(); a.shutdown(socket.SHUT_WR)
print(f"Q2 recv n={recv0(b)} poll0={poll0(p)} peek={peek(b)}")
a.close(); b.close()
# Q3: empty record -> shutdown -> receive -> poll, peek  (the named-limit sequence)
a, b, p = newpair(); a.send(b""); a.shutdown(socket.SHUT_WR)
print(f"Q3 recv n={recv0(b)} poll0={poll0(p)} peek={peek(b)}")
a.close(); b.close()
# Q4: empty record -> data record -> shutdown -> receive -> poll, peek (pending-data control)
a, b, p = newpair(); a.send(b""); a.send(b"\x05\x00"); a.shutdown(socket.SHUT_WR)
print(f"Q4 recv n={recv0(b)} poll0={poll0(p)} peek={peek(b)}")
a.close(); b.close()
# Q5: data record -> shutdown: first receive returns the DATA (records precede EOF)
a, b, p = newpair(); a.send(b"\x05\x00"); a.shutdown(socket.SHUT_WR)
print(f"Q5 recv n={recv0(b)} poll0={poll0(p)}")
a.close(); b.close()
# Q6: empty record -> another empty record: receive -> poll, peek
a, b, p = newpair(); a.send(b""); a.send(b"")
print(f"Q6 recv n={recv0(b)} poll0={poll0(p)} peek={peek(b)}")
a.close(); b.close()
