#!/usr/bin/env python3
"""Trials ledger service. Runs ONLY as the loomledger OS identity. Holds the
hash-chained, append-only event sequence (Rev 4 SS13). The interface offers
exactly three operations: append, head, list. There is NO update, delete, or
rewrite operation. The store file is owned by loomledger (mode 600 inside a
mode-700 directory); producing components hold no credential for it and can
reach the sequence only through this service's append operation."""
import hashlib, json, os, socket, sys

RUNTIME = "/tmp/loom-trials-runtime"
STORE = RUNTIME + "/ledger-store/sequence.jsonl"
SOCK = RUNTIME + "/sock/ledger.sock"

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def load_events():
    if not os.path.exists(STORE):
        return []
    return [json.loads(l) for l in open(STORE) if l.strip()]

def event_hash(seq, etype, payload, prev_hash):
    body = {"seq": seq, "type": etype, "payload": payload, "prev_hash": prev_hash}
    return hashlib.sha256(prev_hash.encode() + canonical(body)).hexdigest()

def do_append(req):
    events = load_events()
    seq = len(events) + 1
    prev = events[-1]["hash"] if events else req["genesis_prev"]
    h = event_hash(seq, req["type"], req["payload"], prev)
    ev = {"seq": seq, "type": req["type"], "payload": req["payload"],
          "timestamp": req["timestamp"], "prev_hash": prev, "hash": h}
    with open(STORE, "a") as f:
        f.write(json.dumps(ev, sort_keys=True) + "\n")
        f.flush(); os.fsync(f.fileno())
    return {"ok": True, "seq": seq, "hash": h}

def handle(req):
    op = req.get("op")
    if op == "append":
        return do_append(req)
    if op == "head":
        evs = load_events()
        return {"ok": True, "seq": len(evs), "hash": evs[-1]["hash"] if evs else None,
                "type": evs[-1]["type"] if evs else None}
    if op == "list":
        return {"ok": True, "events": load_events()}
    if op == "verify":
        evs = load_events()
        for i, ev in enumerate(evs):
            prev = evs[i - 1]["hash"] if i else ev["prev_hash"]
            if ev["prev_hash"] != prev: return {"ok": False, "at": ev["seq"], "why": "prev_hash mismatch"}
            if event_hash(ev["seq"], ev["type"], ev["payload"], ev["prev_hash"]) != ev["hash"]:
                return {"ok": False, "at": ev["seq"], "why": "hash mismatch"}
        return {"ok": True, "events": len(evs)}
    return {"ok": False, "error": "unknown_op: the ledger interface has no such operation"}

def main():
    if os.path.exists(SOCK): os.unlink(SOCK)
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(SOCK); os.chmod(SOCK, 0o666); s.listen(8)
    while True:
        conn, _ = s.accept()
        data = b""
        while not data.endswith(b"\n"):
            chunk = conn.recv(65536)
            if not chunk: break
            data += chunk
        try:
            resp = handle(json.loads(data.decode()))
        except Exception as e:
            resp = {"ok": False, "error": str(e)}
        conn.sendall(json.dumps(resp).encode() + b"\n")
        conn.close()

if __name__ == "__main__":
    main()
