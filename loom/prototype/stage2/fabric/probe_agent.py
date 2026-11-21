"""Probe agent — the agent-context half of boundary probe v2.

Runs INSIDE the agent OS context (as the loomagent identity),
spawned by fabric/probe2.py against a disposable twin runtime.
Standard library only; imports nothing from the fabric package;
holds no sealed material and never prints file contents — a read
that unexpectedly succeeds is reported by size and SHA-256 only, so
the probe output itself can never become the leak it hunts for.

Config (one JSON object on stdin):
  {data_sock, store_path, ground_truth_path, symlink_path,
   traversal_path, token, region_id}

Attempts, in order: the two literal direct reads section 4A names
(the event store, the sealed ground truth); two alternate-path reads
(a symlink planted in the agent home, and a traversal spelling of
the store path); a forged-token operation and a token-issuance
attempt on the data socket; and legitimate operations with the
properly issued token — the probe must prove the agent is isolated,
not disabled.

Prints one JSON object: {"attempts": [{attempt, outcome, detail}]}.
"""
import hashlib
import json
import socket
import sys


def _read_attempt(name, path):
    try:
        with open(path, "rb") as fh:
            data = fh.read()
        return {"attempt": name, "outcome": "EXPOSED",
                "detail": {"path": path, "bytes": len(data),
                           "sha256": hashlib.sha256(data).hexdigest()}}
    except PermissionError as exc:
        return {"attempt": name, "outcome": "denied",
                "detail": {"path": path, "errno": exc.errno,
                           "error": "PermissionError: "
                                    f"{exc.strerror}"}}
    except OSError as exc:
        return {"attempt": name, "outcome": "error",
                "detail": {"path": path, "errno": exc.errno,
                           "error": f"{type(exc).__name__}: "
                                    f"{exc.strerror}"}}


def _socket_request(sock_path, req):
    line = (json.dumps(req) + "\n").encode("utf-8")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.settimeout(15.0)
        s.connect(sock_path)
        s.sendall(line)
        buf = b""
        while not buf.endswith(b"\n"):
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
    return json.loads(buf.decode("utf-8"))


def main() -> int:
    cfg = json.loads(sys.stdin.read())
    attempts = []

    # The two literal direct reads section 4A prescribes.
    attempts.append(_read_attempt("direct_read_store", cfg["store_path"]))
    attempts.append(_read_attempt("direct_read_ground_truth",
                                  cfg["ground_truth_path"]))
    # Alternate paths to the same files (Vane's condition: denial must
    # hold "including through alternate paths").
    attempts.append(_read_attempt("alternate_path_symlink",
                                  cfg["symlink_path"]))
    attempts.append(_read_attempt("alternate_path_traversal",
                                  cfg["traversal_path"]))

    # A forged token must be refused.
    resp = _socket_request(cfg["data_sock"], {
        "op": "open_region", "token": "forged-token-not-issued",
        "region_id": cfg["region_id"]})
    attempts.append({
        "attempt": "forged_token_open",
        "outcome": "refused" if not resp.get("ok") else "EXPOSED",
        "detail": {"kind": resp.get("kind"), "error": resp.get("error")}})

    # Token issuance must not exist on the data socket at all.
    resp = _socket_request(cfg["data_sock"], {
        "op": "issue_token",
        "agent_id": "99999999-9999-4999-8999-999999999999"})
    attempts.append({
        "attempt": "issuance_attempt_on_data_socket",
        "outcome": "refused" if not resp.get("ok") else "EXPOSED",
        "detail": {"kind": resp.get("kind"), "error": resp.get("error")}})

    # Legitimate access through the harness: isolated, not disabled.
    resp = _socket_request(cfg["data_sock"], {
        "op": "view_pattern", "token": cfg["token"]})
    attempts.append({
        "attempt": "legitimate_pattern_view",
        "outcome": "ok" if resp.get("ok") else "failed",
        "detail": {"regions": len(resp.get("result", {})
                                  .get("regions", []))}
        if resp.get("ok") else {"kind": resp.get("kind"),
                                "error": resp.get("error")}})
    resp = _socket_request(cfg["data_sock"], {
        "op": "open_region", "token": cfg["token"],
        "region_id": cfg["region_id"]})
    result = resp.get("result") or {}
    attempts.append({
        "attempt": "legitimate_region_open",
        "outcome": "ok" if resp.get("ok") else "failed",
        "detail": {"title": result.get("title"),
                   "version": result.get("version"),
                   "content_bytes": len(result.get("content", ""))}
        if resp.get("ok") else {"kind": resp.get("kind"),
                                "error": resp.get("error")}})

    print(json.dumps({"attempts": attempts}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
