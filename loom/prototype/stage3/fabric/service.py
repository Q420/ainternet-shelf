"""Fabric service — Loom spec v0.1 Rev 9, section 4A, as corrected.

Stage 2 corrections round (2026-11-21). The service is the fabric's
OS-level boundary made real: it runs under its own OS identity
(loomfab), owns the event store and the sealed ground-truth file
inside a directory that identity alone can enter, and serves agent
operations over a Unix data socket. Agent processes run under a
different identity (loomagent) and hold only fabric/client.py: the
data socket protocol is the whole of their reach.

Two sockets, two trust levels:

- data socket (sock/fabric.sock): the agent operations —
  view_pattern, consult_index, open_region, submit, read_breadth,
  and (Stage 3) examine, assess, claim_completion — each
  authenticated by a per-run token. There is NO issuance
  operation on this socket, by design: an issuance attempt is an
  unknown operation.
- admin socket (service/admin.sock, inside the loomfab-only
  directory): the operator path — issue_token, open_run,
  record_probe_attestation, history, status, shutdown. The agent
  identity cannot even traverse the directory that holds it.

Run failure (Vane's correction conditions, section 3): when the
harness raises HardLineBreach, the service — the run's owner —
appends the system RUN_FAILED event through the engine's atomic
commit path, so the append and the transition to failed state are
one act; the fold derives the failed state from the history, and
every data operation refuses from then on, across restarts. If the
append itself fails, the service fails closed anyway: it latches
in-process (all further agent operations refused), writes an
external diagnostic record into the service failures directory
distinguishing the unrecordable failure, and never fabricates a
RUN_FAILED event. The fault can be injected for tests by starting
the service with LOOM_FAULT_INJECT=run_failed_append.

Corrections round 2 (2026-11-21, Vane's examination of the
corrections round, blockers B1 and B2):

- B1 — the attestation is an ADMISSION GATE, enforced by this
  service's state machine, not by the operator's sequence. The gate
  is derived from the history: a run admits agents only when
  RUN_OPENED stands at seq 1 and a valid, successful BOUNDARY_PROBE
  attestation stands at seq 2 — re-validated from the recorded
  payload (required outcomes, provenance, result hash) every time
  the gate is consulted, so the state survives restarts and does
  not trust the recording path. The admin issue_token operation
  refuses unless the gate holds, and every data-socket operation
  refuses (kind "not_attested") unless the gate holds. The
  attestation handler VALIDATES before recording: a result whose
  required outcomes are missing or not passing, whose provenance
  is absent, or whose supplied result hash does not recompute is
  refused at the admin path and NOT recorded — a failed or
  malformed attestation leaves the run simply unattested, and
  admission stays blocked until a valid one stands.
- B2 — an unrecordable failure is terminal ACROSS RESTART. The
  constructor scans the service failures directory before any
  socket serves: an unrecorded-failure diagnostic belonging to
  this store's run restores the terminal latch, so a fresh service
  on the same runtime refuses every agent operation without
  inventing a RUN_FAILED event. Status reports such a run as
  "failed_unrecorded" (never "open"), and shows whether a durable
  diagnostic marker exists. A second injectable fault,
  LOOM_FAULT_INJECT=diagnostic_write, makes the diagnostic write
  itself fail: the service still latches closed in-process, and
  its status says diagnostic_written is false — with no durable
  marker there is no durable stop, and the status does not
  pretend otherwise.

Posture (the probe bootstrap, recorded in the round-2 notes): a
complete attestation result cannot exist before some service has
admitted a probe agent, so exactly one admission must precede the
first attestation. That admission is confined to the disposable
twin: probe2 starts the twin's service with
LOOM_SERVICE_POSTURE=probe_target, a startup posture in which the
admission gate does not block (the twin must admit the probe agent
so the probe can gather its legitimate-access outcomes) and
record_probe_attestation is REFUSED — a probe target never
carries an attestation, so its history can never present itself
as an attested run. The posture is reported in status and in the
probe result's provenance. Every other service runs in the
default "enforced" posture, where the gate has no exceptions.

Corrections round 3 (2026-11-21, Vane's examination of round 2,
findings B1.1, B1.2, B2.1):

- B1.1 — the probe_target posture is structurally confined to
  the disposable twin. Every runtime carries a rig identity
  (service/rig.json, written by runtime_setup at build time,
  before any service starts): which rig it is ("experimental" or
  "probe_twin"), its root, and — once the service opens the run —
  the store's run id. LOOM_SERVICE_POSTURE=probe_target is now a
  REQUEST only: this service honours it solely when its own
  runtime's rig identity says probe_twin and names this runtime.
  A missing, unreadable, or mismatched rig identity refuses the
  posture at startup — the service raises and exits before any
  socket serves; it never silently falls back to open admission,
  and the environment variable alone can no longer put any
  service into the bootstrap posture.
- B1.2 — attestation provenance is validated, not merely
  present, and the evidence is tied to the actual twin. The
  validator checks the VALUES of every provenance entry (owner
  name, owner uid, mode — the boundary's established values),
  requires the probe posture to be "probe_target", and requires
  the twin service's build identity (the code copy's per-file
  SHA-256 set) to equal this service's own build. At recording
  time the service additionally LIVE-VERIFIES the claim: it stats
  the named twin runtime as it actually stands, reads the twin's
  rig identity (which must say probe_twin and name the twin
  store's actual run) and hashes the twin's live code copy. A
  claim that disagrees with the filesystem, points at this
  service's own runtime, or names a rig that is not a probe twin
  is refused and NOT recorded — a hash of the supplied object
  proves its consistency, never its truth; the live check is
  what ties the record to the probe that actually ran.
- B2.1 — the unrecordable-failure diagnostic is written
  ATOMICALLY (temporary file in the failures directory, flush +
  fsync, atomic rename, directory fsync), so an interruption can
  no longer leave a truncated diagnostic at the final path. And
  the startup scan now fails closed on uncertainty: a candidate
  failure marker that is unreadable or malformed is an UNCERTAIN
  failure condition — the latch is restored, no event is
  invented, and status reports the marker state honestly
  (diagnostic_state "unreadable") instead of treating the file
  as no marker at all.

Corrections round 4 (2026-11-21, Vane's examination of round 3 —
B1.1 residual, B1.2 execution evidence; B2.1 closed, untouched):

- B1.1 residual — the rig/store run binding is UNCONDITIONAL.
  Whenever the store already holds a run, the rig identity must
  carry a run_id that is a non-empty string equal to that run —
  missing, null, malformed, or mismatched refuses startup, in
  every posture (round 3 checked the pair only under
  probe_target, and only when both ids were non-null). The
  runtime factory now builds experimental runtimes only; the
  twin is built through runtime_setup.build_twin_runtime.
- B1.2 — the attestation is bound to evidence of the ACTUAL
  probe execution, held in the twin's own records. A probe now
  runs inside a probe SESSION: the twin service (probe_target
  posture only) opens a session on its admin path, records
  PROBE_SESSION_OPENED in its own history, and issues a
  session-bound token. The socket attempts are labelled with the
  session, so the service OBSERVES the forged-token refusal, the
  issuance refusal, and the legitimate successes itself. The
  four filesystem attempts happen in the agent process; the
  agent files their outcomes through the data socket under the
  session token, and the service checks each reported denial for
  ENTAILMENT — the attempted path is one of the twin's probe
  paths and the twin's live owner/mode configuration denies the
  agent identity read access to it — before recording
  PROBE_EVIDENCE in the twin's history: the full outcome set,
  each outcome marked observed-by-service or
  agent-reported-with-entailment-verified. The experimental
  service, at attestation time, opens the twin's store itself,
  verifies its hash chain, extracts the outcomes FROM THE TWIN'S
  RECORDS, and requires the submitted outcomes to match them
  exactly. A twin that merely EXISTS, however well configured,
  no longer attests anything: no execution record, no gate.

Corrections round 5 (2026-11-21, Vane's examination of round 4 —
B1.2.1, the one remaining blocker; B1.1 and B2.1 closed,
untouched; B1.2.2's qualification accepted and preserved):

- B1.2.1 — the witness must describe precisely what it
  witnessed. Round 4's observation logic matched a label to a
  loose outcome class: any refused request with a non-session
  token could stand as the forged-token refusal, any refused
  unknown operation as the issuance refusal, and any successful
  session-token request as either legitimate outcome. Each
  observation label is now bound to its EXACT expected request:
  forged_token_open records only an open_region with a
  non-session token, refused; issuance_attempt_on_data_socket
  only an issue_token request, refused (an unknown operation
  such as "nonsense" no longer satisfies it);
  legitimate_pattern_view only a view_pattern with the session
  token, successful; legitimate_region_open only an open_region
  with the session token AND the probe's expected region,
  successful. A mislabeled request records nothing: the
  session's evidence is simply incomplete, and the attestation
  fails on the missing observed basis exactly as it fails on a
  missing outcome. The expected region is the fixture's
  established probe target (fabric.fixture.COMPONENTS — the
  same constant probe2 hands the probe agent as its region_id),
  read by the service from the fixture itself, so neither the
  agent nor the session opener can move the expectation.

Corrections round 6 (2026-11-21, Vane's examination of round 5 —
the one remaining B1.2.1 item; everything else closed or
accepted, untouched):

- Token presence is part of the forged-token claim. Round 5's
  forged_token_open branch tested only that the supplied value
  differed from the session token, which an absent, null, or
  empty token also satisfies — so a request that omitted its
  credential could be recorded as an attempted use of a foreign
  one. A missing credential is not a forged credential: the
  branch now requires the token to be a non-empty string that
  differs from the session token, on an open_region, refused.
  Nothing else changed.

Stage 3 (2026-11-21, built to the settled Stage 3 design brief
Rev 3): the data socket gains the three noticing/judgment
operations — examine, assess, claim_completion — dispatched to
the harness under exactly the admission regime the existing
operations live under: refused while the failure latch holds,
refused once the run has failed, refused before a valid boundary
attestation stands (kind "not_attested"), and authenticated by
the per-run token, from which all authorship derives. A request
line that is not a JSON object is a transport refusal at the
socket, before any dispatch. Nothing about the gate, the probe
sessions, or the attestation machinery changes.
"""
import argparse
import json
import os
import pwd
import socketserver
import threading
import uuid
from datetime import datetime, timezone

from .canonical import canonical, sha256_hex
from .engine import Engine, verify_chain
from .fixture import (COMPONENTS, CONSTITUTION_HASH, SYSTEM_ACTOR,
                      load_ground_truth)
from .harness import (Harness, HardLineBreach, HarnessRefusal,
                      TransportRefusal)
from .store import EventStore

AGENT_OPS = ("view_pattern", "consult_index", "open_region", "submit",
             "read_breadth",
             # Stage 3 (2026-11-21): the noticing and judgment
             # operations — examine, assess, claim_completion —
             # on the same data socket, under the same token
             # identity and the same attestation admission gate
             # as the five Stage 2 operations.
             "examine", "assess", "claim_completion")

# B1: the outcomes a boundary-probe result must contain, with the
# values that count as success, before the service will record it
# as an attestation or honour it at the admission gate. The names
# are the probe agent's attempt names (fabric/probe_agent.py).
REQUIRED_PROBE_OUTCOMES = {
    "direct_read_store": "denied",
    "direct_read_ground_truth": "denied",
    "alternate_path_symlink": "denied",
    "alternate_path_traversal": "denied",
    "forged_token_open": "refused",
    "issuance_attempt_on_data_socket": "refused",
    "legitimate_pattern_view": "ok",
    "legitimate_region_open": "ok",
}

# Round 4 (B1.2): the outcome set splits by how the twin service
# can know it. The socket outcomes happen ON the twin service's
# own data socket, so the service observes them directly. The
# filesystem outcomes happen inside the agent process, so the
# agent reports them and the service verifies each reported
# denial for entailment against the twin's live configuration.
SOCKET_OBSERVED_OUTCOMES = (
    "forged_token_open", "issuance_attempt_on_data_socket",
    "legitimate_pattern_view", "legitimate_region_open",
)
FS_REPORTED_OUTCOMES = (
    "direct_read_store", "direct_read_ground_truth",
    "alternate_path_symlink", "alternate_path_traversal",
)

# Round 5 (B1.2.1): the region the probe's legitimate open must
# target before the service will record the legitimate_region_open
# observation. It is the fixture's established probe target — the
# same COMPONENTS constant probe2 hands the probe agent as its
# region_id — read by the service from the fixture itself, so the
# expectation is a property of the boundary fixture: neither the
# agent's label nor the session opener can move it.
PROBE_REGION_ID = COMPONENTS

# The provenance entries a probe result must carry: the twin
# configuration record (fabric/runtime_setup.py's stat_record).
REQUIRED_PROVENANCE_KEYS = (
    "service", "service/ground-truth.json", "service/failures",
    "service/code", "sock", "agent-home",
)

# B1.2: the VALUES each provenance entry must carry — the
# boundary's established owners and modes (runtime_setup's
# layout), checked as recorded owner name AND uid AND mode. The
# expected uids are resolved from the account database, not
# hardcoded, so the check names the identities themselves.
_SERVICE_UID = pwd.getpwnam("loomfab").pw_uid
_AGENT_UID = pwd.getpwnam("loomagent").pw_uid
EXPECTED_PROVENANCE = {
    "service": ("loomfab", _SERVICE_UID, "0o700"),
    "service/ground-truth.json": ("loomfab", _SERVICE_UID, "0o600"),
    "service/failures": ("loomfab", _SERVICE_UID, "0o700"),
    "service/code": ("loomfab", _SERVICE_UID, "0o750"),
    "sock": ("loomfab", _SERVICE_UID, "0o711"),
    "agent-home": ("loomagent", _AGENT_UID, "0o755"),
}


def _stat_entry(path):
    """The stat_record shape ({owner, uid, mode}) for one path —
    the same shape runtime_setup.stat_record produces, so a live
    stat can be compared to a claimed record entry for entry."""
    st = os.stat(path)
    return {"owner": pwd.getpwuid(st.st_uid).pw_name,
            "uid": st.st_uid,
            "mode": oct(st.st_mode & 0o7777)}


def _code_dir_hashes(code_dir):
    """{file name: SHA-256} for every .py file in a fabric package
    directory — the service build identity the runtime evidence
    computes (runtime_setup.code_copy_hashes), computed here for
    the service's own code directory and, at attestation time, for
    the twin's."""
    out = {}
    for fname in sorted(os.listdir(code_dir)):
        if fname.endswith(".py"):
            with open(os.path.join(code_dir, fname), "rb") as fh:
                out[fname] = sha256_hex(fh.read())
    return out


_AGENT_PWD = pwd.getpwnam("loomagent")


def _permits(st, uid, gid, bit):
    """True when the identity (uid, primary gid) holds permission
    `bit` (0o4 read, 0o1 traverse) on the stat'd path, by the
    usual owner/group/other resolution. The agent identity's
    supplementary groups are not consulted: the boundary layout
    grants the agent nothing through any group it could belong
    to (every boundary path is owned by loomfab/loomagent with
    group equal to the owner's own group)."""
    if st.st_uid == uid:
        shift = 6
    elif st.st_gid == gid:
        shift = 3
    else:
        shift = 0
    return bool((st.st_mode >> shift) & bit)


def _identity_can_read(uid, gid, path):
    """Simulate the kernel's read check for an identity on a path:
    traverse permission on every ancestor directory of the
    resolved path, read permission on the resolved file itself.
    Used to check a probe agent's reported filesystem denial for
    ENTAILMENT (round 4, B1.2): the denial is entailed when the
    twin's live owner/mode configuration, as it actually stands,
    denies this identity the read the agent says was denied."""
    resolved = os.path.realpath(path)
    ancestors = []
    cur = os.path.dirname(resolved)
    while True:
        ancestors.append(cur)
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    for directory in reversed(ancestors):
        try:
            st = os.stat(directory)
        except OSError:
            return False
        if not _permits(st, uid, gid, 0o1):
            return False
    try:
        st = os.stat(resolved)
    except OSError:
        return False
    return _permits(st, uid, gid, 0o4)


def attestation_problems(result, own_code_hashes=None):
    """Validate a supplied boundary-probe result as an attestation:
    every required outcome present with its passing value, the
    summary flags set, the probe posture correct, the twin
    identified, the twin service's build identity matching this
    service's own build (when own_code_hashes is given), and the
    twin-configuration provenance present WITH ITS REQUIRED
    VALUES — owner name, owner uid, and mode per entry (B1.2:
    presence is not validity). Returns a list of problems; empty
    means the result is a valid, successful attestation. The
    live-filesystem verification of the claim happens separately,
    at recording time (_verify_twin_live): this function judges
    the object; that one judges the world it claims to describe."""
    problems = []
    if not isinstance(result, dict):
        return ["the probe result is not a JSON object"]
    attempts = result.get("attempts")
    if not isinstance(attempts, list):
        problems.append("the probe result carries no attempts list")
    else:
        by_name = {}
        for a in attempts:
            if isinstance(a, dict) and isinstance(a.get("attempt"), str):
                by_name[a["attempt"]] = a.get("outcome")
        for name, want in REQUIRED_PROBE_OUTCOMES.items():
            got = by_name.get(name)
            if got != want:
                problems.append(
                    f"required outcome {name!r} is {got!r}, "
                    f"not {want!r}")
    for flag in ("all_reads_denied", "socket_attacks_refused",
                 "legitimate_access_ok"):
        if result.get(flag) is not True:
            problems.append(f"the probe result's {flag} is not true")
    if result.get("service_posture") != "probe_target":
        problems.append(
            "the probe result's service_posture is "
            f"{result.get('service_posture')!r}, not 'probe_target': "
            "the attested probe must have run against the disposable "
            "twin in its bootstrap posture")
    if not isinstance(result.get("twin_root"), str) \
            or not result.get("twin_root"):
        problems.append(
            "the probe result does not identify the twin runtime "
            "(twin_root is missing)")
    claimed_build = result.get("service_code_hashes")
    if not isinstance(claimed_build, dict) or not claimed_build:
        problems.append(
            "the probe result carries no service build identity "
            "(service_code_hashes is missing)")
    elif own_code_hashes is not None \
            and claimed_build != own_code_hashes:
        problems.append(
            "the twin service's build identity does not match this "
            "service's build: the attested probe ran against a "
            "different service build")
    # Round 4 (B1.2): the result must POINT at the execution
    # evidence in the twin's own records. Presence and shape are
    # judged here; the pointed-to record itself is verified at
    # recording time (_verify_execution_evidence), which reads the
    # twin's store and extracts the outcomes from it — the pointer
    # alone establishes nothing.
    evidence = result.get("execution_evidence")
    if not isinstance(evidence, dict):
        problems.append(
            "the probe result carries no execution-evidence "
            "pointer (execution_evidence is missing): an attestation "
            "must be bound to the twin's own record of the probe "
            "execution (B1.2)")
    else:
        if evidence.get("twin_root") != result.get("twin_root"):
            problems.append(
                "the execution-evidence pointer names a different "
                "twin than the probe result itself (B1.2)")
        if not isinstance(evidence.get("session_id"), str) \
                or not evidence.get("session_id"):
            problems.append(
                "the execution-evidence pointer carries no probe "
                "session id (B1.2)")
        seq = evidence.get("event_seq")
        if not isinstance(seq, int) or isinstance(seq, bool) \
                or seq < 2:
            problems.append(
                "the execution-evidence pointer's event_seq is "
                f"{seq!r}, not the sequence of an evidence event "
                "in the twin's history (B1.2)")
        ev_hash = evidence.get("event_hash")
        if not isinstance(ev_hash, str) or len(ev_hash) != 64 \
                or any(c not in "0123456789abcdef" for c in ev_hash):
            problems.append(
                "the execution-evidence pointer's event_hash is "
                "not a SHA-256 hash (B1.2)")
    config = result.get("twin_config")
    if not isinstance(config, dict) or not config:
        problems.append(
            "the probe result carries no provenance "
            "(twin_config is missing)")
    else:
        for key in REQUIRED_PROVENANCE_KEYS:
            if key not in config:
                problems.append(
                    f"the provenance (twin_config) lacks {key!r}")
                continue
            entry = config[key]
            owner, uid, mode = EXPECTED_PROVENANCE[key]
            if not isinstance(entry, dict) \
                    or entry.get("owner") != owner \
                    or entry.get("uid") != uid \
                    or entry.get("mode") != mode:
                problems.append(
                    f"the provenance for {key!r} is {entry!r}, not "
                    f"owner {owner!r} (uid {uid}) with mode {mode}: "
                    "provenance values are validated, not merely "
                    "present (B1.2)")
    return problems


def _ok(result):
    return {"ok": True, "result": result}


def _err(kind, error):
    return {"ok": False, "kind": kind, "error": error}


class FabricService:
    def __init__(self, runtime_dir):
        self.runtime_dir = runtime_dir
        self.service_dir = os.path.join(runtime_dir, "service")
        self.sock_dir = os.path.join(runtime_dir, "sock")
        self.store_path = os.path.join(self.service_dir, "events.db")
        self.gt_path = os.path.join(self.service_dir, "ground-truth.json")
        self.failures_dir = os.path.join(self.service_dir, "failures")
        self.data_sock = os.path.join(self.sock_dir, "fabric.sock")
        self.admin_sock = os.path.join(self.service_dir, "admin.sock")
        # Fault injection is a comma-separated set of named faults
        # (round 1 had exactly one member: run_failed_append).
        self.fault_inject = {
            f.strip() for f in
            os.environ.get("LOOM_FAULT_INJECT", "").split(",")
            if f.strip()}
        # Service posture: "enforced" (the default — the admission
        # gate has no exceptions) or "probe_target" (the disposable
        # twin's bootstrap posture; see the module docstring).
        # Round 3 (B1.1): LOOM_SERVICE_POSTURE=probe_target is a
        # REQUEST, not a switch. It is honoured only when this
        # runtime's own rig identity (service/rig.json, written by
        # runtime_setup at build time) says this runtime IS a
        # probe twin. Anything else — an experimental rig, a
        # missing or unreadable identity, an identity naming a
        # different runtime — refuses the posture at startup: the
        # constructor raises, the process exits, and no socket ever
        # serves. There is no silent fallback to open admission.
        self.rig_identity = self._read_rig_identity()
        requested_posture = os.environ.get("LOOM_SERVICE_POSTURE",
                                           "enforced")
        self.posture = "enforced"
        if requested_posture == "probe_target":
            rig = self.rig_identity
            if rig is None:
                raise RuntimeError(
                    "probe_target posture refused: this runtime "
                    "carries no rig identity (service/rig.json is "
                    "missing or unreadable), so nothing establishes "
                    "that it is a disposable probe twin (B1.1)")
            if rig.get("rig") != "probe_twin":
                raise RuntimeError(
                    "probe_target posture refused: this runtime's "
                    f"rig identity is {rig.get('rig')!r}, not "
                    "'probe_twin' — the bootstrap posture is a "
                    "property of the probe rig, not of an "
                    "environment variable (B1.1)")
            if os.path.realpath(str(rig.get("runtime_root", ""))) \
                    != os.path.realpath(self.runtime_dir):
                raise RuntimeError(
                    "probe_target posture refused: the rig identity "
                    f"names runtime {rig.get('runtime_root')!r}, "
                    f"not this runtime ({self.runtime_dir!r}) "
                    "(B1.1)")
            self.posture = "probe_target"
        # This service's build identity (B1.2): the per-file hashes
        # of the code copy this process is actually running, taken
        # once at startup. An attestation must name the same build.
        self._own_code_hashes = _code_dir_hashes(
            os.path.dirname(os.path.abspath(__file__)))
        self._latched = False
        self._latch_info = None
        # Probe sessions (round 4, B1.2): live only in the
        # probe_target posture, in this process's memory. The
        # durable record of a session is the twin's own event
        # history (PROBE_SESSION_OPENED / PROBE_EVIDENCE); this
        # dict holds the session-bound token and the socket
        # outcomes the service observes while the probe runs.
        self._probe_sessions = {}
        self._diagnostic_written = False
        self._diagnostic_restored = False
        # The durable-marker state, reported honestly in status:
        # "none" (no latch, or a latch with no marker), "written"
        # (this process wrote a diagnostic), "restored" (the latch
        # came from a clean diagnostic at startup), "unreadable"
        # (the latch came from a candidate marker that could not
        # be read — the B2.1 uncertain failure condition).
        self._diagnostic_state = "none"
        self._stopped = threading.Event()
        os.umask(0o077)
        # The sealed ground truth: loaded from the service-side file
        # at startup and held in memory. It is never served, never
        # written to an event, and no operation returns any part of
        # it; loading it here proves the service identity can read
        # what the agent identity cannot.
        self._ground_truth = load_ground_truth(self.gt_path)
        self.store = EventStore(self.store_path, check_same_thread=False)
        self.engine = Engine(self.store)
        self.harness = Harness(self.engine)
        # B1.1, second half of the identity check — made
        # UNCONDITIONAL in round 4 (Vane's round-3 examination):
        # whenever the store already holds a run (any restart),
        # the rig identity must carry a run_id that is a non-empty
        # string EQUAL to the store's run. Missing, null,
        # malformed (non-string), or mismatched refuses startup,
        # in every posture: the identity binding is a property of
        # the runtime, not of the posture it is started in. (Round
        # 3 checked the pair only under probe_target, and only
        # when both ids were non-null — a rig with no run id at
        # all slipped the check entirely.)
        store_run = self.store.get_run_id()
        if store_run is not None:
            rig_run = (self.rig_identity or {}).get("run_id")
            if not isinstance(rig_run, str) or not rig_run \
                    or rig_run != store_run:
                raise RuntimeError(
                    "startup refused: the store already holds run "
                    f"{store_run!r} but the rig identity's run_id "
                    f"is {rig_run!r} — the identity must name the "
                    "store's actual run (B1.1)")
        # B2: before any socket serves, restore the terminal latch
        # from an unrecorded-failure diagnostic left by a previous
        # service process on this runtime. The diagnostic is a
        # durable stop marker, not merely a report.
        self._restore_latch()
        # All dispatch is serialised: the store connection and the
        # engine's append+fold transactions are single-threaded
        # objects, and section 3's atomicity is defined over a
        # serial history anyway.
        self._lock = threading.RLock()

    # -- run state ---------------------------------------------------
    @property
    def failed(self):
        return self.engine.state.get("run_status") == "failed"

    # -- the admission gate (B1) --------------------------------------
    def _attested(self):
        """True when the history itself carries a valid, successful
        attestation: RUN_OPENED at seq 1 and a BOUNDARY_PROBE at
        seq 2 whose recorded probe result re-validates (required
        outcomes, provenance) and whose recorded result hash
        recomputes from the canonical result. Derived from the
        history on every call, so the gate state survives restarts
        and never merely trusts that the recording path validated."""
        events = self.store.all_events()
        if len(events) < 2:
            return False
        if events[0]["type"] != "RUN_OPENED":
            return False
        ev = events[1]
        if ev["type"] != "BOUNDARY_PROBE":
            return False
        payload = ev["payload"]
        if payload.get("attestation") is not True:
            return False
        result = payload.get("probe")
        if attestation_problems(result, self._own_code_hashes):
            return False
        return payload.get("probe_result_hash") == sha256_hex(
            canonical(result))

    def _admission_open(self):
        """The gate as enforced: in the enforced posture, admission
        requires the attestation; in the probe-target posture (the
        disposable twin's bootstrap), the gate does not block."""
        if self.posture == "probe_target":
            return True
        return self._attested()

    # -- rig identity (B1.1) -------------------------------------------
    def _read_rig_identity(self):
        """This runtime's rig identity record (service/rig.json),
        or None if it is missing or unreadable. The record is
        written by runtime_setup at build time; the service only
        reads it (and, at open_run, fills in the run id)."""
        try:
            with open(os.path.join(self.service_dir, "rig.json"),
                      encoding="utf-8") as fh:
                record = json.load(fh)
            return record if isinstance(record, dict) else None
        except (OSError, ValueError):
            return None

    def _record_rig_run_id(self, run_id):
        """Fill this runtime's run id into its rig identity when
        the run opens, so the identity names the store's actual
        run from then on. Best-effort bookkeeping: the posture was
        already decided at startup, and a failure here fails
        closed downstream (a twin whose rig does not name its
        store's run fails the B1.2 live verification)."""
        if not isinstance(self.rig_identity, dict):
            return
        self.rig_identity["run_id"] = run_id
        try:
            with open(os.path.join(self.service_dir, "rig.json"),
                      "w", encoding="utf-8") as fh:
                json.dump(self.rig_identity, fh, indent=2,
                          sort_keys=True)
        except OSError:
            pass

    # -- live twin verification (B1.2) ----------------------------------
    def _verify_twin_live(self, result):
        """Verify a probe result's claims against the twin runtime
        AS IT ACTUALLY STANDS, at attestation time: the named twin
        must not be this runtime; its rig identity must say
        probe_twin, name this twin root, and name the twin store's
        actual run; the claimed provenance entries must equal live
        stats of the twin's paths; and the twin's live service
        code copy must hash to the claimed build identity. This
        service runs as loomfab, which owns both runtimes, so the
        twin is directly stat-able. Returns a list of problems;
        empty means the claim matches the world. Performed only at
        recording time — the gate's re-validation of a recorded
        attestation (see _attested) deliberately does NOT re-stat
        the twin, which is disposable and may since have been
        rebuilt; what the gate re-checks is the recorded claim's
        values against the required ones."""
        problems = []
        twin_root = os.path.realpath(result.get("twin_root") or "")
        if twin_root == os.path.realpath(self.runtime_dir):
            return ["the attestation names this service's own "
                    "runtime as the twin: experimental-runtime "
                    "provenance is not probe evidence (B1.2)"]
        twin_service = os.path.join(twin_root, "service")
        try:
            with open(os.path.join(twin_service, "rig.json"),
                      encoding="utf-8") as fh:
                rig = json.load(fh)
        except (OSError, ValueError):
            return ["the named twin carries no readable rig "
                    "identity, so nothing establishes that it is "
                    "the disposable probe twin (B1.2)"]
        if not isinstance(rig, dict) or rig.get("rig") != "probe_twin":
            problems.append(
                "the named twin's rig identity is "
                f"{rig.get('rig') if isinstance(rig, dict) else rig!r}"
                ", not 'probe_twin' (B1.2)")
        if not isinstance(rig, dict) \
                or os.path.realpath(str(rig.get("runtime_root", ""))) \
                != twin_root:
            problems.append(
                "the twin's rig identity does not name the twin "
                "runtime the attestation claims (B1.2)")
        twin_store_path = os.path.join(twin_service, "events.db")
        if not os.path.exists(twin_store_path):
            problems.append("the named twin has no event store")
        elif isinstance(rig, dict):
            twin_store = EventStore(twin_store_path,
                                    check_same_thread=False)
            try:
                twin_run = twin_store.get_run_id()
            finally:
                twin_store._conn.close()
            if twin_run is None:
                problems.append(
                    "the twin store holds no run: no probe run "
                    "stands behind this attestation (B1.2)")
            elif rig.get("run_id") != twin_run:
                problems.append(
                    "the twin's rig identity names run "
                    f"{rig.get('run_id')!r} but the twin store's "
                    f"run is {twin_run!r} (B1.2)")
        claimed = result.get("twin_config") or {}
        for key in REQUIRED_PROVENANCE_KEYS:
            path = os.path.join(twin_root, *key.split("/"))
            try:
                live = _stat_entry(path)
            except OSError:
                problems.append(
                    f"the twin path for {key!r} cannot be examined "
                    "as it stands (B1.2)")
                continue
            if live != claimed.get(key):
                problems.append(
                    f"the claimed provenance for {key!r} disagrees "
                    f"with the twin as it actually stands: claimed "
                    f"{claimed.get(key)!r}, live {live!r} (B1.2)")
        try:
            live_build = _code_dir_hashes(
                os.path.join(twin_service, "code", "fabric"))
        except OSError:
            problems.append(
                "the twin's service code copy cannot be examined "
                "as it stands (B1.2)")
        else:
            if live_build != result.get("service_code_hashes"):
                problems.append(
                    "the claimed service build identity disagrees "
                    "with the twin's live service code copy (B1.2)")
        return problems

    def _verify_execution_evidence(self, result):
        """Verify the attestation against the twin's OWN record of
        the probe execution (round 4, B1.2). Opens the twin's
        store, verifies its hash chain, locates the
        PROBE_EVIDENCE event the result's pointer names, and
        extracts the outcomes FROM THAT RECORD: every required
        outcome must stand there with its passing value and its
        required basis (socket outcomes observed by the twin
        service itself; filesystem outcomes agent-reported with
        entailment verified by it), the session must have been
        opened earlier in the same chain, and the submitted
        result's outcomes must match the recorded ones exactly.
        A well-configured twin with no execution record — Vane's
        round-3 attack: genuine twin, no probe ever run,
        fabricated all-passing outcomes — fails here, because
        there is nothing in the twin's records to extract.
        Returns a list of problems; empty means the execution
        evidence verifies."""
        problems = []
        pointer = result.get("execution_evidence") or {}
        twin_root = os.path.realpath(result.get("twin_root") or "")
        twin_store_path = os.path.join(twin_root, "service",
                                       "events.db")
        if not os.path.exists(twin_store_path):
            return ["the named twin has no event store, so it "
                    "holds no execution evidence (B1.2)"]
        twin_store = EventStore(twin_store_path,
                                check_same_thread=False)
        try:
            events = twin_store.all_events()
        finally:
            twin_store._conn.close()
        ok, bad_seq = verify_chain(events, CONSTITUTION_HASH)
        if not ok:
            return ["the twin's event history does not verify "
                    f"(chain fails at seq {bad_seq}), so its "
                    "execution evidence cannot be trusted (B1.2)"]
        seq = pointer.get("event_seq")
        evidence_ev = None
        session_ev = None
        for ev in events:
            if ev["event_seq"] == seq:
                evidence_ev = ev
            if ev["type"] == "PROBE_SESSION_OPENED" \
                    and ev["payload"].get("session_id") \
                    == pointer.get("session_id"):
                session_ev = ev
        if evidence_ev is None \
                or evidence_ev["type"] != "PROBE_EVIDENCE" \
                or evidence_ev["hash"] != pointer.get("event_hash"):
            return ["the execution-evidence pointer names no "
                    "PROBE_EVIDENCE event in the twin's verified "
                    "history (B1.2)"]
        payload = evidence_ev["payload"]
        if payload.get("session_id") != pointer.get("session_id"):
            problems.append(
                "the twin's execution evidence names session "
                f"{payload.get('session_id')!r}, not the pointed-to "
                f"session {pointer.get('session_id')!r} (B1.2)")
        if session_ev is None \
                or session_ev["event_seq"] >= evidence_ev["event_seq"]:
            problems.append(
                "the twin's history holds no PROBE_SESSION_OPENED "
                "for this session before the evidence event: the "
                "execution was not a session the twin service "
                "opened (B1.2)")
        recorded = payload.get("outcomes") or {}
        submitted = {}
        for a in result.get("attempts") or []:
            if isinstance(a, dict) and isinstance(a.get("attempt"), str):
                submitted[a["attempt"]] = a.get("outcome")
        for name, want in REQUIRED_PROBE_OUTCOMES.items():
            entry = recorded.get(name)
            if not isinstance(entry, dict) \
                    or entry.get("outcome") != want:
                problems.append(
                    f"the twin's execution evidence records "
                    f"{name!r} as {entry!r}, not the passing "
                    f"outcome {want!r} (B1.2)")
                continue
            want_basis = ("observed" if name in SOCKET_OBSERVED_OUTCOMES
                          else "agent_reported_entailment_verified")
            if entry.get("basis") != want_basis:
                problems.append(
                    f"the twin's execution evidence records "
                    f"{name!r} with basis {entry.get('basis')!r}, "
                    f"not {want_basis!r} (B1.2)")
            if submitted.get(name) != want:
                problems.append(
                    f"the submitted outcome for {name!r} is "
                    f"{submitted.get(name)!r}, which does not match "
                    "the twin's execution evidence (B1.2)")
        return problems

    # -- unrecordable failure: latch restoration (B2, B2.1) -------------
    @staticmethod
    def _is_diagnostic_candidate(name):
        """A file in the failures directory is a candidate failure
        marker if it carries the diagnostic naming pattern: a
        completed diagnostic (unrecorded-failure-*.json) or the
        stranded temporary of an interrupted atomic write
        (unrecorded-failure-*.json.tmp). Unrelated names are not
        candidates and are ignored."""
        return name.startswith("unrecorded-failure-") and (
            name.endswith(".json") or name.endswith(".json.tmp"))

    def _restore_latch(self):
        """Scan the failures directory for an unrecorded-failure
        diagnostic belonging to this store's run. If one exists,
        restore the terminal latch: every agent-facing operation is
        refused, and no RUN_FAILED event is invented — the history
        stays exactly as the failed append left it.

        Round 3 (B2.1): a candidate marker that is UNREADABLE or
        malformed is not skipped. It is an uncertain failure
        condition — a failure may have occurred whose record
        cannot be read, and its run cannot even be determined —
        so the latch is restored for THIS runtime (the conservative
        reading), no event is invented, and status reports the
        marker state as "unreadable" rather than dressing the run
        as healthy. A well-formed diagnostic for a DIFFERENT run,
        and files that are not diagnostic candidates at all, keep
        being ignored for this run."""
        if not os.path.isdir(self.failures_dir):
            return
        run_id = self.store.get_run_id()
        for name in sorted(os.listdir(self.failures_dir)):
            if not self._is_diagnostic_candidate(name):
                continue
            try:
                with open(os.path.join(self.failures_dir, name),
                          encoding="utf-8") as fh:
                    record = json.load(fh)
                if not isinstance(record, dict):
                    raise ValueError("diagnostic is not a JSON object")
            except (OSError, ValueError):
                self._latched = True
                self._diagnostic_state = "unreadable"
                self._latch_info = {
                    "breach": None,
                    "append_error": None,
                    "marker_unreadable": name,
                }
                return
            if record.get("kind") != "unrecordable_run_failure":
                continue
            if record.get("run_id") != run_id:
                continue  # a different run's marker, not this run's
            self._latched = True
            self._diagnostic_written = True
            self._diagnostic_restored = True
            self._diagnostic_state = "restored"
            self._latch_info = {
                "breach": record.get("breach"),
                "append_error": record.get("append_error"),
                "restored_from_diagnostic": name,
            }
            return

    # -- agent-facing dispatch ----------------------------------------
    def dispatch_data(self, req):
        with self._lock:
            return self._dispatch_data(req)

    def _dispatch_data(self, req):
        resp = self._dispatch_data_inner(req)
        self._note_probe_observation(req, resp)
        return resp

    def _dispatch_data_inner(self, req):
        if not isinstance(req, dict):
            # A request line that parses to a non-object is a
            # transport refusal for every operation (Stage 3's
            # recordability step, applied at the socket): no event
            # is appended and nothing is dispatched.
            return _err("transport_refusal",
                        "the request was not a JSON object")
        op = req.get("op")
        if op == "probe_report":
            # Round 4 (B1.2): the probe agent files its filesystem
            # outcomes with the twin service. The operation exists
            # only inside a probe session on a probe target; on any
            # other service it is simply not an agent operation.
            return self._handle_probe_report(req)
        if op not in AGENT_OPS:
            return _err("unknown_op",
                        f"the agent interface has no operation {op!r}")
        if self._latched:
            return _err(
                "run_failed_unrecorded",
                "the run failed and the failure could not be "
                "recorded; this service is latched closed — see the "
                "diagnostic record in the service failures directory")
        if self.failed:
            return _err(
                "run_failed",
                "the run has failed (RUN_FAILED is in its history); "
                "no further agent activity is admitted")
        if not self._admission_open():
            return _err(
                "not_attested",
                "the run has no valid boundary attestation: agent "
                "operations are not admitted until a successful "
                "pre-run boundary probe stands attested at seq 2")
        token = req.get("token")
        try:
            if op == "view_pattern":
                return _ok(self.harness.view_pattern(token))
            if op == "consult_index":
                return _ok(self.harness.consult_index(token))
            if op == "open_region":
                return _ok(self.harness.open_region(
                    token, req.get("region_id")))
            if op == "read_breadth":
                # Same trust domain (service-side): resolve the token
                # to its identity, then report that identity's breadth.
                agent = self.harness._authenticate(token)
                return _ok({"read_breadth":
                            self.harness.read_breadth(agent)})
            if op == "submit":
                return _ok(self.harness.submit(token, req.get("response")))
            if op == "examine":
                return _ok(self.harness.examine(
                    token, req.get("report")))
            if op == "assess":
                return _ok(self.harness.assess(
                    token, req.get("assessment")))
            if op == "claim_completion":
                # The harness receives the whole request envelope:
                # the claim contract's recordability rule turns on
                # the distinction between the top-level submission
                # and its nested claim field.
                return _ok(self.harness.claim_completion(token, req))
        except HardLineBreach as breach:
            self._fail_run(breach)
            if self._latched:
                return _err(
                    "run_failed_unrecorded",
                    f"hard-line breach; the run has failed and the "
                    f"failure could not be recorded, so this service "
                    f"is latched closed: {breach}")
            return _err("run_failed",
                        f"hard-line breach; the run has failed: {breach}")
        except TransportRefusal as exc:
            return _err("transport_refusal", str(exc))
        except HarnessRefusal as exc:
            return _err("refusal", str(exc))
        except Exception as exc:  # never hang an agent on a bug
            return _err("internal", f"{type(exc).__name__}: {exc}")
        return _err("internal", "unreachable dispatch state")

    # -- probe sessions (round 4, B1.2) --------------------------------
    def _note_probe_observation(self, req, resp):
        """Record a socket outcome the service OBSERVED during a
        probe session. The probe agent labels each socket attempt
        with the session id and the attempt name; the service
        records the outcome only when the request that actually
        arrived on its socket is the EXACT request the label
        names, with the result that label claims (round 5,
        B1.2.1: the witness describes precisely what it
        witnessed):

        - forged_token_open: an open_region carrying a
          non-session token, refused — and (round 6) the token
          must actually have been supplied, as a non-empty
          string: a missing, null, empty, or non-string token
          is an omitted credential, not a forged one, and
          records nothing;
        - issuance_attempt_on_data_socket: an issue_token
          request, refused (an unknown operation, however
          refused, is not an issuance attempt);
        - legitimate_pattern_view: a view_pattern carrying the
          session token, successful;
        - legitimate_region_open: an open_region carrying the
          session token AND naming the probe's expected region
          (PROBE_REGION_ID), successful.

        A request that does not match its label's expected pair
        exactly records nothing — the session's evidence is
        simply incomplete, and the attestation later fails on
        the missing observed basis, exactly as it fails on a
        missing outcome. The label names the attempt; it cannot
        manufacture the outcome, and it cannot redescribe a
        different request as the attempt it names."""
        if self.posture != "probe_target":
            return
        if not isinstance(req, dict):
            return
        sid = req.get("probe_session")
        label = req.get("probe_attempt")
        session = self._probe_sessions.get(sid) \
            if isinstance(sid, str) else None
        if session is None or session["finalized"]:
            return
        ok = bool(resp.get("ok"))
        op = req.get("op")
        if label == "forged_token_open":
            supplied = req.get("token")
            if op == "open_region" \
                    and isinstance(supplied, str) and supplied \
                    and supplied != session["token"] \
                    and not ok:
                session["observations"][label] = "refused"
        elif label == "issuance_attempt_on_data_socket":
            if op == "issue_token" and not ok:
                session["observations"][label] = "refused"
        elif label == "legitimate_pattern_view":
            if op == "view_pattern" \
                    and req.get("token") == session["token"] and ok:
                session["observations"][label] = "ok"
        elif label == "legitimate_region_open":
            if op == "open_region" \
                    and req.get("token") == session["token"] \
                    and req.get("region_id") == PROBE_REGION_ID \
                    and ok:
                session["observations"][label] = "ok"

    def _probe_fs_paths(self):
        """The four filesystem paths the probe attempts, as this
        twin's layout spells them — the same spellings
        runtime_setup hands the probe agent."""
        return {
            "direct_read_store": self.store_path,
            "direct_read_ground_truth": self.gt_path,
            "alternate_path_symlink": os.path.join(
                self.runtime_dir, "agent-home", "store-link"),
            "alternate_path_traversal": os.path.join(
                self.sock_dir, "..", "service", "events.db"),
        }

    def _fs_denial_entailed(self, name, report):
        """Check one agent-reported filesystem denial for
        ENTAILMENT: the reported path is the twin's own path for
        that attempt; the reported outcome is a denial with the
        OS's permission errno; and the twin's live owner/mode
        configuration denies the agent identity read access to
        the resolved target (for the alternate paths, the symlink
        or traversal spelling must resolve to the store it aims
        at). The service cannot see the agent's open() call — what
        it can do is establish that, given the configuration as it
        actually stands, the read the agent reports being denied
        is a read the configuration denies. Returns (entailed,
        reason)."""
        expected_path = self._probe_fs_paths()[name]
        detail = report.get("detail")
        if not isinstance(detail, dict):
            return False, "the report carries no detail"
        if detail.get("path") != expected_path:
            return False, (
                f"the reported path {detail.get('path')!r} is not "
                f"this twin's {name} path")
        if report.get("outcome") != "denied":
            return False, (
                f"the reported outcome is "
                f"{report.get('outcome')!r}, not a denial")
        if detail.get("errno") != 13:  # EACCES — PermissionError
            return False, (
                f"the reported errno is {detail.get('errno')!r}, "
                "not EACCES (13): the denial the agent reports is "
                "not the operating system's permission denial")
        resolved = os.path.realpath(expected_path)
        if name == "alternate_path_symlink" \
                and (not os.path.islink(expected_path)
                     or resolved != os.path.realpath(self.store_path)):
            return False, ("the planted symlink does not resolve "
                           "to this twin's store")
        if resolved not in (os.path.realpath(self.store_path),
                            os.path.realpath(self.gt_path)):
            return False, ("the attempted path does not resolve "
                           "to a sealed file of this twin")
        if _identity_can_read(_AGENT_PWD.pw_uid, _AGENT_PWD.pw_gid,
                              resolved):
            return False, ("the twin's live configuration does "
                           "NOT deny the agent identity this read: "
                           "the reported denial is not entailed")
        return True, "entailed by the live configuration"

    def _handle_probe_report(self, req):
        """Finalise a probe session from the agent's filesystem
        outcome report, and record the execution evidence in THIS
        twin's history (PROBE_EVIDENCE). Exists only in the
        probe_target posture, only under the session-bound token,
        only once per session."""
        if self.posture != "probe_target":
            return _err("unknown_op",
                        "the agent interface has no operation "
                        "'probe_report'")
        if self._latched or self.failed:
            return _err("refusal",
                        "this probe target's run is stopped; no "
                        "probe evidence can be finalised")
        sid = req.get("probe_session")
        session = self._probe_sessions.get(sid) \
            if isinstance(sid, str) else None
        if session is None:
            return _err("refusal",
                        "no open probe session carries that id")
        if session["finalized"]:
            return _err("refusal",
                        "this probe session's evidence is already "
                        "recorded; a session finalises once")
        try:
            agent = self.harness._authenticate(req.get("token"))
        except HarnessRefusal as exc:
            return _err("refusal", str(exc))
        if req.get("token") != session["token"] \
                or agent != session["agent_id"]:
            return _err("refusal",
                        "the probe report must be filed under the "
                        "session-bound token the session was "
                        "opened for")
        reports = req.get("attempts")
        if not isinstance(reports, list):
            return _err("refusal",
                        "the probe report carries no attempts list")
        by_name = {}
        for rep in reports:
            if isinstance(rep, dict) \
                    and isinstance(rep.get("attempt"), str):
                by_name[rep["attempt"]] = rep
        outcomes = {}
        for name in SOCKET_OBSERVED_OUTCOMES:
            observed = session["observations"].get(name)
            outcomes[name] = {
                "outcome": observed,
                "basis": "observed" if observed is not None
                         else "not_observed",
            }
        for name in FS_REPORTED_OUTCOMES:
            rep = by_name.get(name)
            if rep is None:
                outcomes[name] = {"outcome": None,
                                  "basis": "not_reported"}
                continue
            entailed, reason = self._fs_denial_entailed(name, rep)
            outcomes[name] = {
                "outcome": rep.get("outcome"),
                "basis": "agent_reported_entailment_verified"
                         if entailed
                         else "agent_reported_unverified",
                "entailment": reason,
            }
        # Corroboration from this history itself: the legitimate
        # region open the service observed also stands in the
        # record as a DISCOVERY by the session's agent.
        discovery_seqs = [
            e["event_seq"] for e in self.store.all_events()
            if e["type"] == "DISCOVERY"
            and e["actor"] == session["agent_id"]
            and e["event_seq"] > session["opened_seq"]]
        payload = {
            "session_id": sid,
            "agent_id": session["agent_id"],
            "outcomes": outcomes,
            "observed_discovery_seqs": discovery_seqs,
            "summary": "Probe execution evidence, recorded by the "
                       "twin service itself: the socket outcomes "
                       "were observed on this service's data "
                       "socket during the session; the filesystem "
                       "outcomes were reported by the probe agent "
                       "and each denial was checked for entailment "
                       "against this twin's live configuration "
                       "before being recorded as verified.",
        }
        ev = self.engine.commit_events(
            [("PROBE_EVIDENCE", SYSTEM_ACTOR, [], payload)])[0]
        session["finalized"] = True
        return _ok({"session_id": sid,
                    "event_seq": ev["event_seq"],
                    "event_hash": ev["hash"]})

    # -- run failure ----------------------------------------------------
    def _fail_run(self, breach):
        declared = set(breach.declared_read_set)
        recorded = set(breach.recorded_read_set)
        payload = {
            "breach": "hard_line_read_record",
            "declared_read_set": breach.declared_read_set,
            "recorded_read_set": breach.recorded_read_set,
            "claimed_but_not_made": sorted(declared - recorded),
            "made_but_not_claimed": sorted(recorded - declared),
            "detail": str(breach),
            "summary": "The run failed: a contribution declared a "
                       "read set that does not match the harness "
                       "read record — a hard-line breach (section "
                       "9). The run is stopped; no further agent "
                       "activity is admitted.",
        }
        try:
            if "run_failed_append" in self.fault_inject:
                raise RuntimeError(
                    "injected fault (LOOM_FAULT_INJECT): the "
                    "RUN_FAILED append failed")
            self.engine.commit_events(
                [("RUN_FAILED", SYSTEM_ACTOR, [], payload)])
        except Exception as exc:
            # Failure of failure: fail closed WITHOUT fabricating the
            # event. Latch in-process and preserve the evidence
            # externally, so the record distinguishes a recorded
            # failure from an unrecordable one.
            self._latched = True
            self._latch_info = {
                "breach": payload,
                "append_error": f"{type(exc).__name__}: {exc}",
            }
            self._write_diagnostic()

    def _write_diagnostic(self):
        record = {
            "kind": "unrecordable_run_failure",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "run_id": self.store.get_run_id(),
            "breach": self._latch_info["breach"],
            "append_error": self._latch_info["append_error"],
            "note": "The RUN_FAILED event could not be appended. The "
                    "service latched closed in-process and refused "
                    "all further agent operations. No RUN_FAILED "
                    "event exists in the history; this file is the "
                    "record of the failure, and it is deliberately "
                    "NOT part of the event history. On startup a "
                    "later service process restores the terminal "
                    "latch from this record (corrections round 2, "
                    "B2): it is a durable stop marker, not merely a "
                    "report. It was written atomically (temporary "
                    "file, fsync, rename, directory fsync — "
                    "corrections round 3, B2.1), so this file is "
                    "complete or was never there.",
            "summary": "An unrecordable run failure occurred and was "
                       "preserved as an external diagnostic record; "
                       "the service failed closed.",
        }
        try:
            if "diagnostic_write" in self.fault_inject:
                raise OSError(
                    "injected fault (LOOM_FAULT_INJECT): the "
                    "diagnostic write failed")
            os.makedirs(self.failures_dir, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime(
                "%Y%m%dT%H%M%S.%fZ")
            path = os.path.join(self.failures_dir,
                                f"unrecorded-failure-{stamp}.json")
            # B2.1: the write is ATOMIC. The record goes to a
            # temporary file in the same directory, is flushed and
            # fsynced, and is then renamed onto the final path,
            # with the directory fsynced after the rename — so the
            # final path only ever holds a complete diagnostic, or
            # none. An interruption leaves at most the stranded
            # temporary, which the startup scan treats as an
            # uncertain failure condition (see _restore_latch).
            tmp_path = path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as fh:
                json.dump(record, fh, indent=2, sort_keys=True)
                fh.flush()
                os.fsync(fh.fileno())
            os.rename(tmp_path, path)
            dir_fd = os.open(self.failures_dir, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
            self._diagnostic_written = True
            self._diagnostic_state = "written"
        except OSError:
            # The latch still holds in this process, but there is
            # NO durable marker: a restart cannot restore what was
            # never written. Status reports diagnostic_written as
            # false so the absence is never dressed as recovery.
            self._diagnostic_written = False
            self._diagnostic_state = "none"

    # -- operator/admin dispatch ----------------------------------------
    def dispatch_admin(self, req):
        with self._lock:
            return self._dispatch_admin(req)

    def _dispatch_admin(self, req):
        op = req.get("op")
        try:
            if op == "status":
                events = self.store.all_events()
                if self.failed:
                    run_status = "failed"
                elif self._latched:
                    # B2: a run stopped by an unrecordable failure
                    # is never reported "open".
                    run_status = "failed_unrecorded"
                elif not events:
                    run_status = "unopened"
                elif self._admission_open():
                    run_status = "open"
                else:
                    run_status = "unattested"
                return _ok({
                    "run_id": self.store.get_run_id(),
                    "events": len(events),
                    "head_hash": events[-1]["hash"] if events else None,
                    "run_status": run_status,
                    "posture": self.posture,
                    # B1.1: the rig identity this service verified
                    # at startup — evidence of which rig the
                    # posture was decided against.
                    "rig": (self.rig_identity or {}).get("rig"),
                    "attested": self._attested(),
                    "latched_unrecorded_failure": self._latched,
                    # Whether a durable diagnostic marker exists for
                    # an unrecorded failure: true when one was
                    # written by this process or restored from disk
                    # at startup; false when the latch has no
                    # durable marker (or there is no latch).
                    "diagnostic_written": self._diagnostic_written,
                    "diagnostic_restored": self._diagnostic_restored,
                    # B2.1: the marker state in one word — "none",
                    # "written", "restored", or "unreadable" (the
                    # latch came from a candidate marker that
                    # could not be read: an uncertain failure
                    # condition, failed closed, never dressed as a
                    # clean diagnostic or as no marker).
                    "diagnostic_state": self._diagnostic_state,
                })
            if op == "history":
                return _ok({"events": self.store.all_events()})
            if op == "issue_token":
                if not self._admission_open():
                    return _err(
                        "refusal",
                        "no token may be issued before a valid, "
                        "successful boundary attestation stands at "
                        "seq 2 (B1: the attestation is an admission "
                        "gate, enforced by the service)")
                return _ok({"token": self.harness.issue_token(
                    req.get("agent_id"))})
            if op == "open_run":
                if self.store.all_events():
                    return _err("refusal",
                                "the store already holds a run")
                self.engine = Engine.open_run(self.store,
                                              req.get("run_id"))
                self.harness = Harness(self.engine)
                # B1.1: the rig identity now names the store's
                # actual run, so the identity and the store agree
                # from here on (checked at startup on restart, and
                # for the twin at attestation time).
                self._record_rig_run_id(req.get("run_id"))
                return _ok({"run_id": req.get("run_id"), "events": 1})
            if op == "open_probe_session":
                # Round 4 (B1.2): a probe session is the twin's
                # bootstrap made evidentiary. Only a probe target
                # opens one. The session is recorded in the twin's
                # own history BEFORE the probe runs, and the token
                # issued for it is bound to the session (its hash
                # stands in the record; the token itself does not).
                if self.posture != "probe_target":
                    return _err(
                        "refusal",
                        "probe sessions exist only on the "
                        "disposable probe twin (probe_target "
                        "posture); this service is not a probe rig")
                agent_id = req.get("agent_id")
                token = self.harness.issue_token(agent_id)
                session_id = str(uuid.uuid4())
                ev = self.engine.commit_events(
                    [("PROBE_SESSION_OPENED", SYSTEM_ACTOR, [], {
                        "session_id": session_id,
                        "agent_id": agent_id,
                        "token_sha256": sha256_hex(
                            token.encode("utf-8")),
                        "summary": "A boundary-probe session "
                                   "opened on the disposable twin: "
                                   "the session-bound token was "
                                   "issued to the probe agent, whose "
                                   "socket attempts this service "
                                   "will observe and whose "
                                   "filesystem outcomes it will "
                                   "check for entailment before "
                                   "recording the execution "
                                   "evidence.",
                    })])[0]
                self._probe_sessions[session_id] = {
                    "agent_id": agent_id,
                    "token": token,
                    "opened_seq": ev["event_seq"],
                    "observations": {},
                    "finalized": False,
                }
                return _ok({"session_id": session_id, "token": token,
                            "event_seq": ev["event_seq"]})
            if op == "record_probe_attestation":
                if self.posture == "probe_target":
                    return _err(
                        "refusal",
                        "a probe target never records an attestation: "
                        "its history is the probe rig's scaffolding, "
                        "never evidence")
                events = self.store.all_events()
                if len(events) != 1 or events[0]["type"] != "RUN_OPENED":
                    return _err(
                        "refusal",
                        "the attestation must be the second event: "
                        "the run must be open and no other event may "
                        "precede it")
                result = req.get("probe_result")
                # B1: validate BEFORE recording. A result that is
                # malformed, incomplete, or failing is refused here
                # and NOT recorded; the run remains unattested and
                # admission stays blocked until a valid, successful
                # attestation stands.
                problems = attestation_problems(
                    result, self._own_code_hashes)
                if problems:
                    return _err(
                        "refusal",
                        "the supplied probe result is not a valid, "
                        "successful attestation and was not "
                        "recorded: " + "; ".join(problems))
                # B1.2: validate the claim against the WORLD, not
                # only the object — live-verify the named twin as
                # it actually stands (rig identity, the twin
                # store's run, live stats of the claimed paths,
                # the twin's live service build). A claim that
                # disagrees with the filesystem is refused here
                # and NOT recorded, exactly like a malformed one.
                problems = self._verify_twin_live(result)
                if problems:
                    return _err(
                        "refusal",
                        "the supplied probe result's provenance "
                        "does not verify against the twin runtime "
                        "as it actually stands, and the attestation "
                        "was not recorded: " + "; ".join(problems))
                # Round 4 (B1.2): verify the EXECUTION evidence —
                # the outcomes are extracted from the twin's own
                # records, not accepted from the submitted object.
                # A twin that merely exists, with no probe ever
                # executed against it, holds no PROBE_EVIDENCE and
                # fails here however genuine its configuration is.
                problems = self._verify_execution_evidence(result)
                if problems:
                    return _err(
                        "refusal",
                        "the supplied probe result's outcomes do "
                        "not verify against the twin's own "
                        "execution evidence, and the attestation "
                        "was not recorded: " + "; ".join(problems))
                supplied_hash = req.get("probe_result_hash")
                if supplied_hash is not None and supplied_hash \
                        != sha256_hex(canonical(result)):
                    return _err(
                        "refusal",
                        "the supplied probe_result_hash does not "
                        "recompute from the canonical probe result; "
                        "the attestation was not recorded")
                payload = {
                    "attestation": True,
                    "probe": result,
                    "probe_result_hash": sha256_hex(canonical(result)),
                    "summary": "Boundary probe attestation: before "
                               "this run opened, the pre-run "
                               "boundary probe ran against a "
                               "disposable twin of this runtime (same "
                               "layout, owners, permissions and "
                               "service build) from the agent OS "
                               "context. The twin's store and "
                               "ground-truth files denied every "
                               "direct and alternate-path read; "
                               "forged-token and issuance attempts "
                               "on the data socket were refused; "
                               "legitimate operations through the "
                               "harness succeeded. This event "
                               "attests to that twin probe — the "
                               "experimental store itself was not "
                               "probed, and no probe reads are in "
                               "this history.",
                }
                ev = self.engine.commit_events(
                    [("BOUNDARY_PROBE", SYSTEM_ACTOR, [], payload)])[0]
                return _ok({"event_seq": ev["event_seq"]})
            if op == "shutdown":
                threading.Timer(0.1, self._stopped.set).start()
                return _ok({"shutting_down": True})
        except HarnessRefusal as exc:
            return _err("refusal", str(exc))
        except Exception as exc:
            return _err("internal", f"{type(exc).__name__}: {exc}")
        return _err("unknown_op", f"no such admin operation {op!r}")

    # -- serving ---------------------------------------------------------
    def serve(self):
        service = self

        class Handler(socketserver.StreamRequestHandler):
            admin = False

            def handle(self):
                line = self.rfile.readline(1 << 21)
                if not line:
                    return
                try:
                    req = json.loads(line.decode("utf-8"))
                except Exception:
                    resp = _err("transport", "request was not JSON")
                else:
                    resp = (service.dispatch_admin(req) if self.admin
                            else service.dispatch_data(req))
                self.wfile.write((json.dumps(resp) + "\n").encode("utf-8"))

        class AdminHandler(Handler):
            admin = True

        class Server(socketserver.ThreadingUnixStreamServer):
            daemon_threads = True
            allow_reuse_address = True

        for path in (self.data_sock, self.admin_sock):
            if os.path.exists(path):
                os.unlink(path)
        data_server = Server(self.data_sock, Handler)
        os.chmod(self.data_sock, 0o777)
        admin_server = Server(self.admin_sock, AdminHandler)
        threads = [
            threading.Thread(target=data_server.serve_forever,
                             daemon=True),
            threading.Thread(target=admin_server.serve_forever,
                             daemon=True),
        ]
        for t in threads:
            t.start()
        self._stopped.wait()
        data_server.shutdown()
        admin_server.shutdown()
        data_server.server_close()
        admin_server.server_close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-dir", required=True)
    args = parser.parse_args()
    FabricService(args.runtime_dir).serve()


if __name__ == "__main__":
    main()
