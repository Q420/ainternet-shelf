"""Agent-side client — Loom spec v0.1 Rev 9, section 4A.

The client is the whole of what agent-side code holds: a Unix-socket
transport to the fabric service and the five agent operations. It
contains NO token-issuance path — issuance lives only inside the
service, behind its operator/admin socket — and no other route to
the fabric: no store handle, no engine, no fixture, no file paths
beyond the one data socket it is given. An agent process holding
this client can ask for exactly what the harness serves, with a
token the operator handed it, and nothing else.

Standard library only, so the module can be copied into an agent
execution context (the boundary runtime's agent home) and imported
there without the fabric package.
"""
import json
import socket


class ClientRefusal(Exception):
    """The service refused the call. Carries the service's error kind
    (e.g. "refusal", "run_failed", "unknown_op") so callers and tests
    can distinguish a failed run from an ordinary refusal."""

    def __init__(self, kind, error):
        super().__init__(f"{kind}: {error}")
        self.kind = kind
        self.error = error


class FabricClient:
    def __init__(self, data_sock_path: str, timeout: float = 15.0):
        self._sock_path = data_sock_path
        self._timeout = timeout

    def _request(self, op: str, **fields) -> dict:
        req = {"op": op}
        req.update(fields)
        line = (json.dumps(req) + "\n").encode("utf-8")
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(self._timeout)
            s.connect(self._sock_path)
            s.sendall(line)
            buf = b""
            while not buf.endswith(b"\n"):
                chunk = s.recv(65536)
                if not chunk:
                    break
                buf += chunk
        resp = json.loads(buf.decode("utf-8"))
        if not resp.get("ok"):
            raise ClientRefusal(resp.get("kind", "error"),
                                resp.get("error", "unknown error"))
        return resp["result"]

    # -- the five agent operations (and no others) -------------------
    def view_pattern(self, token) -> dict:
        return self._request("view_pattern", token=token)

    def consult_index(self, token) -> dict:
        return self._request("consult_index", token=token)

    def open_region(self, token, region_id) -> dict:
        return self._request("open_region", token=token,
                             region_id=region_id)

    def submit(self, token, response) -> dict:
        return self._request("submit", token=token, response=response)

    def read_breadth(self, token) -> float:
        return self._request("read_breadth", token=token)["read_breadth"]
