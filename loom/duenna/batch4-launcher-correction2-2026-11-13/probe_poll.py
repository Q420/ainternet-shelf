import select, socket

def masks(ev):
    names = []
    for name in ["POLLIN","POLLPRI","POLLOUT","POLLERR","POLLHUP","POLLRDHUP","POLLNVAL","POLLRDNORM","POLLWRNORM"]:
        bit = getattr(select, name, 0)
        if bit and ev & bit: names.append(name)
    return "|".join(names) or "-"

def scenario(tag, actions):
    a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    poller = select.poll()
    poller.register(b, select.POLLIN | getattr(select, "POLLRDHUP", 0))
    for act in actions:
        if act == "empty": a.send(b"")
        elif act == "shutdown_wr": a.shutdown(socket.SHUT_WR)
        elif act == "poll":
            ev = poller.poll(300)
            print(f"  {tag} poll -> {[(fd, masks(e)) for fd, e in ev] if ev else 'timeout/none'}")
        elif act == "recv":
            data, anc, fl, _ = b.recvmsg(128, socket.CMSG_SPACE(16))
            print(f"  {tag} recv -> n={len(data)}")
    a.close(); b.close()

print("T1 empty record queued: poll")
scenario("T1", ["empty", "poll"])
print("T2 shutdown: poll")
scenario("T2", ["shutdown_wr", "poll"])
print("T3 empty then shutdown: poll")
scenario("T3", ["empty", "shutdown_wr", "poll"])
print("T4 nothing: poll")
scenario("T4", ["poll"])
print("T5 shutdown then poll again after recv")
scenario("T5", ["shutdown_wr", "poll", "recv", "poll"])
