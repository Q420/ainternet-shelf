#!/usr/bin/env python3
"""Client for the trials ledger service. Producing components use ONLY this
client (append / head / list / verify). It holds no store credential."""
import json, socket, sys

SOCK = "/tmp/loom-trials-runtime/sock/ledger.sock"

def call(req):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(SOCK)
    s.sendall(json.dumps(req).encode() + b"\n")
    data = b""
    while not data.endswith(b"\n"):
        chunk = s.recv(1 << 20)
        if not chunk: break
        data += chunk
    s.close()
    return json.loads(data.decode())

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "append":
        print(json.dumps(call({"op": "append", "type": sys.argv[2],
                               "payload": json.loads(sys.argv[3]), "timestamp": sys.argv[4],
                               "genesis_prev": sys.argv[5] if len(sys.argv) > 5 else ""})))
    elif cmd in ("head", "list", "verify"):
        print(json.dumps(call({"op": cmd})))
    else:
        print(json.dumps(call({"op": cmd})))  # any other op: the service answers unknown_op
