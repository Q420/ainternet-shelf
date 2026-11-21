import socket

def flags_str(f):
    names = []
    for name, bit in [("MSG_EOR", socket.MSG_EOR), ("MSG_TRUNC", socket.MSG_TRUNC),
                      ("MSG_CTRUNC", socket.MSG_CTRUNC), ("MSG_ERRQUEUE", getattr(socket, "MSG_ERRQUEUE", 0))]:
        if bit and f & bit: names.append(name)
    return "|".join(names) or "-"

def scenario(tag, actions):
    a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    b.settimeout(2)
    for act in actions:
        if act == "empty": a.send(b"")
        elif act == "data": a.send(b"\x05\x00")
        elif act == "shutdown_wr": a.shutdown(socket.SHUT_WR)
        elif act == "recv":
            try:
                data, anc, fl, _ = b.recvmsg(128, socket.CMSG_SPACE(16))
                print(f"  {tag} recv -> n={len(data)} flags={flags_str(fl)}")
            except Exception as e:
                print(f"  {tag} recv -> {type(e).__name__} {e}")
        elif act == "peek":
            try:
                data, anc, fl, _ = b.recvmsg(128, socket.CMSG_SPACE(16), socket.MSG_PEEK | socket.MSG_DONTWAIT)
                print(f"  {tag} peek -> n={len(data)} flags={flags_str(fl)}")
            except BlockingIOError:
                print(f"  {tag} peek -> EAGAIN")
            except Exception as e:
                print(f"  {tag} peek -> {type(e).__name__} {e}")
    a.close(); b.close()

print("S1 empty record, then peek, then recv, then peek")
scenario("S1", ["empty", "peek", "recv", "peek"])
print("S2 shutdown, then recv, then peek")
scenario("S2", ["shutdown_wr", "recv", "peek"])
print("S3 empty record then shutdown: recv, peek")
scenario("S3", ["empty", "shutdown_wr", "recv", "peek"])
print("S4 two empty records: recv, recv, peek")
scenario("S4", ["empty", "empty", "recv", "recv", "peek"])
print("S5 data record: recv flags")
scenario("S5", ["data", "recv"])
print("S6 nothing sent: peek")
scenario("S6", ["peek"])
