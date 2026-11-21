"""Boundary runtime setup — Stage 2 corrections round (2026-11-21).

Driver-side (orchestrator) tooling: builds the two-OS-context
runtime the corrected section 4A boundary runs in, starts and stops
the fabric service under its own OS identity, and speaks to the
service's operator/admin socket. Nothing here is agent-facing.

Layout of one runtime (name = "experimental", "twin", ...):

    <base>/<name>/
      service/            loomfab, 700 — the service's whole world
        code/fabric/      loomfab, 750/640 — byte-identical copy of
                          the fabric package (hashes verified against
                          the tree by the corrections tests)
        events.db         created by the service; loomfab, 600
        ground-truth.json loomfab, 600 — the sealed material as a file
        admin.sock        operator socket; inside the 700 directory,
                          reachable only by loomfab and root
        failures/         loomfab, 700 — unrecordable-failure records
      sock/               loomfab, 711 — traverse-only; holds ONLY
        fabric.sock       the data socket (chmod 777 by the service:
                          the access control is the token protocol;
                          the OS boundary protects the files)
      agent-home/         loomagent, 755 — client.py, agent_runner.py,
                          probe_agent.py (copies, 644) and store-link,
                          a symlink to the store file planted for the
                          probe's alternate-path attempt

LOCATION NOTE (recorded, not silent): the brief placed the runtime
under ~/workspace/loom-prototype/boundary-runtime/, but this
machine's workspace filesystem denies chown to this sandbox
(EPERM — the workspace sits on an overlay outside the sandbox's
capability set), so no ownership boundary can exist there. The
runtime therefore lives on tmpfs at /tmp/loom-boundary-runtime,
where ownership and permissions are enforceable and were verified
by direct experiment before the build. The workspace directory
~/workspace/loom-prototype/boundary-runtime/ holds the durable
record of the runtime (README + the evidence the tests write).
Runtimes are disposable and rebuilt by build_runtime on every run.
"""
import json
import os
import pwd
import shutil
import socket
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fabric.canonical import canonical, sha256_hex  # noqa: E402
from fabric.fixture import ground_truth_document  # noqa: E402

SERVICE_USER = "loomfab"
AGENT_USER = "loomagent"
RUNTIME_BASE = "/tmp/loom-boundary-runtime"
TREE_FABRIC = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fabric")
AGENT_FILES = ("client.py", "agent_runner.py", "probe_agent.py")


def _uid(user):
    return pwd.getpwnam(user).pw_uid


def _own(path, user, mode):
    os.chown(path, _uid(user), _uid(user))
    os.chmod(path, mode)


def runtime_paths(base, name):
    root = os.path.join(base, name)
    service = os.path.join(root, "service")
    sock_dir = os.path.join(root, "sock")
    agent_home = os.path.join(root, "agent-home")
    return {
        "root": root,
        "service_dir": service,
        "code_dir": os.path.join(service, "code"),
        "store_path": os.path.join(service, "events.db"),
        "ground_truth_path": os.path.join(service, "ground-truth.json"),
        "failures_dir": os.path.join(service, "failures"),
        "admin_sock": os.path.join(service, "admin.sock"),
        "sock_dir": sock_dir,
        "data_sock": os.path.join(sock_dir, "fabric.sock"),
        "agent_home": agent_home,
        "symlink_path": os.path.join(agent_home, "store-link"),
        "traversal_path": os.path.join(sock_dir, "..", "service",
                                       "events.db"),
    }


def build_runtime(base, name):
    """Create a fresh runtime layout. Returns the paths dict."""
    os.makedirs(base, exist_ok=True)
    # The base must be traversable by both identities regardless of
    # the caller's umask (a 770 base silently walls the service out
    # of its own runtime).
    os.chmod(base, 0o755)
    p = runtime_paths(base, name)
    if os.path.exists(p["root"]):
        shutil.rmtree(p["root"])
    os.makedirs(p["service_dir"])
    os.makedirs(p["sock_dir"])
    os.makedirs(p["agent_home"])
    os.makedirs(p["failures_dir"])
    # The service's private copy of the fabric package.
    pkg_dir = os.path.join(p["code_dir"], "fabric")
    os.makedirs(pkg_dir)
    for fname in sorted(os.listdir(TREE_FABRIC)):
        if fname.endswith(".py"):
            shutil.copyfile(os.path.join(TREE_FABRIC, fname),
                            os.path.join(pkg_dir, fname))
    # The sealed ground truth, as a service-side file.
    with open(p["ground_truth_path"], "wb") as fh:
        fh.write(canonical(ground_truth_document()))
    # Agent-side code: copies the agent identity can read and run.
    for fname in AGENT_FILES:
        shutil.copyfile(os.path.join(TREE_FABRIC, fname),
                        os.path.join(p["agent_home"], fname))
    # The planted alternate path: a symlink in the agent's own home
    # pointing straight at the store file.
    os.symlink(p["store_path"], p["symlink_path"])
    # Ownership and permissions — the boundary itself.
    _own(p["service_dir"], SERVICE_USER, 0o700)
    _own(p["failures_dir"], SERVICE_USER, 0o700)
    _own(p["ground_truth_path"], SERVICE_USER, 0o600)
    for dirpath, _dirnames, filenames in os.walk(p["code_dir"]):
        _own(dirpath, SERVICE_USER, 0o750)
        for fname in filenames:
            _own(os.path.join(dirpath, fname), SERVICE_USER, 0o640)
    _own(p["sock_dir"], SERVICE_USER, 0o711)
    _own(p["agent_home"], AGENT_USER, 0o755)
    for fname in AGENT_FILES:
        _own(os.path.join(p["agent_home"], fname), AGENT_USER, 0o644)
    os.chmod(p["root"], 0o755)
    return p


def code_copy_hashes(p):
    """SHA-256 of every copied package file, keyed by file name."""
    pkg_dir = os.path.join(p["code_dir"], "fabric")
    out = {}
    for fname in sorted(os.listdir(pkg_dir)):
        with open(os.path.join(pkg_dir, fname), "rb") as fh:
            out[fname] = sha256_hex(fh.read())
    return out


def tree_hashes():
    out = {}
    for fname in sorted(os.listdir(TREE_FABRIC)):
        if fname.endswith(".py"):
            with open(os.path.join(TREE_FABRIC, fname), "rb") as fh:
                out[fname] = sha256_hex(fh.read())
    return out


def stat_record(p):
    """{relative path: {owner, mode}} for the runtime's boundary
    surface — the equivalence evidence Vane's conditions require."""
    entries = {
        "service": p["service_dir"],
        "service/ground-truth.json": p["ground_truth_path"],
        "service/failures": p["failures_dir"],
        "service/code": p["code_dir"],
        "sock": p["sock_dir"],
        "agent-home": p["agent_home"],
    }
    if os.path.exists(p["store_path"]):
        entries["service/events.db"] = p["store_path"]
    if os.path.exists(p["data_sock"]):
        entries["sock/fabric.sock"] = p["data_sock"]
    out = {}
    for rel, path in entries.items():
        st = os.stat(path)
        out[rel] = {"owner": pwd.getpwuid(st.st_uid).pw_name,
                    "mode": oct(st.st_mode & 0o7777)}
    return out


# -- service process management --------------------------------------
def start_service(p, fault_inject=None):
    """Start the fabric service as loomfab; wait until its admin
    socket answers. Returns the Popen handle."""
    log_path = os.path.join(p["root"], "service.log")
    env_args = [f"PYTHONPATH={p['code_dir']}",
                "PYTHONDONTWRITEBYTECODE=1"]
    if fault_inject:
        env_args.append(f"LOOM_FAULT_INJECT={fault_inject}")
    cmd = ["runuser", "-u", SERVICE_USER, "--", "/usr/bin/env",
           *env_args, "python3", "-m", "fabric.service",
           "--runtime-dir", p["root"]]
    log = open(log_path, "ab")
    proc = subprocess.Popen(cmd, stdout=log, stderr=log)
    deadline = time.time() + 30
    while time.time() < deadline:
        if proc.poll() is not None:
            with open(log_path, "rb") as fh:
                tail = fh.read()[-2000:].decode("utf-8", "replace")
            raise RuntimeError(
                f"service exited early (rc={proc.returncode}): {tail}")
        try:
            status = admin_request(p, {"op": "status"})
            if status.get("ok"):
                return proc
        except OSError:
            pass
        time.sleep(0.1)
    proc.terminate()
    raise RuntimeError("service did not become ready in 30s")


def stop_service(proc, p):
    try:
        admin_request(p, {"op": "shutdown"})
    except OSError:
        pass
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.terminate()
        proc.wait(timeout=10)


# -- socket clients (driver side) --------------------------------------
def _line_request(sock_path, req, timeout=15.0):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        s.connect(sock_path)
        s.sendall((json.dumps(req) + "\n").encode("utf-8"))
        buf = b""
        while not buf.endswith(b"\n"):
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
    return json.loads(buf.decode("utf-8"))


def admin_request(p, req):
    """Operator path: the admin socket lives inside the loomfab-only
    service directory; root reaches it, the agent identity cannot
    even traverse to it."""
    return _line_request(p["admin_sock"], req)


def agent_call(p, op, token, args=None):
    """Perform one agent operation in a genuine loomagent process."""
    req = {"sock": p["data_sock"], "op": op, "token": token,
           "args": args or {}}
    return run_agent_script(p, "agent_runner.py", req)


def run_agent_script(p, script, payload):
    """Run one of the agent-home scripts as loomagent with a JSON
    payload on stdin; return its parsed JSON stdout."""
    cmd = ["runuser", "-u", AGENT_USER, "--", "python3",
           os.path.join(p["agent_home"], script)]
    proc = subprocess.run(cmd, input=json.dumps(payload),
                          capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(
            f"agent script {script} failed rc={proc.returncode}: "
            f"{proc.stderr[-1000:]}")
    return json.loads(proc.stdout.strip().splitlines()[-1])
