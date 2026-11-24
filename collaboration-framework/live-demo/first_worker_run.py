"""The first generated-worker run — execution harness.

Implements FIRST-WORKER-RUN-SCOPE-2026-11-23.md (Rev 2, PASSED)
exactly: one generated worker (A1 assembly), sealed sandbox
grants (A2), a bounded loop (A3), a real model behind the
Piece 8 adapter, and a modest real assignment — read three
fixed source documents and write an outsider-readable status
brief of this framework. Nothing here redesigns anything: the
case travels the office's real route, the assembly the A1
lifecycle, every tool call the doorway and the executor, and
the record is checked afterwards by the independent checker.

The sources are fixed before the run by a manifest (the
examiner's correction A): each staged source's SHA-256 and
provenance are recorded in manifest.json beside the sandbox,
the manifest's own hash is computed over its canonical JSON,
and the issued case identifies that hash in its evidence
boundary. The office derives a case's evidence boundary from
MATERIAL_SEALED records (Piece 5), so the harness seals the
manifest and each source as materials whose boundary includes
the crew seat, with material ids naming the manifest hash and
the source paths; the pre-activation verification below reads
the issued case back and refuses to proceed unless the hash
stands in the boundary and the bounds are the scoped ones,
and unless the staged files still hash to the manifest.

Grants: sandbox.read is confined to sources/ (the worker
cannot read its own brief back — the scope's deliberate
choice). For sandbox.write the scope names the sandbox root;
the registry's ceiling contract (framework.tool_policy and
the checker's own copy, identical) treats a path_prefix by
its non-empty segments, so "/" — a non-empty string whose
segment list is empty — is the root: every normalised
relative path lies under it, while the executor still
confines all paths to the sandbox directory itself. ("" is
rejected as a malformed ceiling; "." can never match; an
omitted key would leave the ceiling empty rather than naming
the root.)

Run it:  PYTHONPATH=src python3 live-demo/first_worker_run.py \
             [run-suffix]
With no argument the run directory is live-demo/first-worker;
a suffix gives live-demo/first-worker-<suffix> for a rerun.
An existing run.db is never overwritten — the script refuses.

Configuration is by environment, as in the Piece 8 live
harness: ADAPTER_ENDPOINT (default the NVIDIA endpoint),
ADAPTER_MODEL (default moonshotai/kimi-k3.1-pro),
ADAPTER_TIMEOUT (default 120).

The attempt-7 retrieval mode (ATTEMPT7-RELEASE-PROPOSAL-
2026-11-23.md; INDEX 256/257) is a distinct configuration
of this same harness, selected by WORKER_ROUTE=groq with
RETRIEVAL=1 (any other RETRIEVAL value refuses): the
assembly declares the retrieval contract, the grants are
the two-path set, and the case's assignment names the
deliverable's exact path, scratch/brief.md, which the
pre-activation verification checks against the configured
and the sealed grants. The historical configuration —
this mode's absence — is attempts 1–6 exactly as they
ran. `--verify-config` runs the mode's dry self-check:
the assembly inputs built and asserted in a throwaway
directory, with no activation and no provider call.

The probed mode (native-mode probe piece, INDEX 285/289)
is a further configuration of the retrieval mode —
PROBED=1 (any other PROBED value refuses), defined only
on the Groq route with RETRIEVAL=1 — and it runs in TWO
PHASES, because the examiner's judgement stands between
them in the lifecycle: `--probe-phase1` assembles with
the probe contract declared, runs the probe stage (five
live trials over the Groq connector transport's raw
call), records construction verification naming the
probe evidence, and stops BEFORE judgement, exporting
the record and writing probe-evidence.json;
`--probe-phase2 --decision-receipt <file>` reopens that
run directory and records the examiner's judgement FROM
THE EXAMINER'S DURABLE DECISION RECEIPT (INDEX 293): a
JSON document identifying the exact phase-1 run, the
assembly, its generated-record hash, the probe event
and evidence hash and the configuration fingerprint,
with the selected mode, its grounds, the examiner's
recorded label and the decision's recorded time. Phase
2 validates every field against the standing phase-1
record and refuses on any mismatch, binds the receipt's
canonical hash into the judgement it records, and
carries the assembly through packing, authorisation,
activation and the loop exactly as the retrieval mode
runs it. The judgement the harness records states in
its own payload that the harness-issued examiner token
is the recording mechanism, not independent
authentication of the examiner's identity. The adapter's transport,
however, is NOT the environment-variable key route: attempt
1 died on it before activation (the key it surfaced was
rejected, HTTP 401 — INDEX 191). The run's calls are
carried through the registered connector helper instead,
so the credential travels its sanctioned Secure Vault path
(connector_transport.py, with the examiner's cancellation
boundary — INDEX 192). No environment key is consulted by
this harness, and no key appears in it or in the record.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from framework import probe as probe_module  # noqa: E402
from framework import projection  # noqa: E402
from framework import tool_policy  # noqa: E402
from framework.adapter import (AdapterFailure,  # noqa: E402
                               OpenAICompatibleAdapter)
from framework.doorway import (Doorway,  # noqa: E402
                               established_case_content)
from framework.executor import Executor  # noqa: E402
from framework.generator import Generator  # noqa: E402
from framework.loop import Loop  # noqa: E402
from framework.office import Office  # noqa: E402
from framework.onboarding import (  # noqa: E402
    instance_onboarding_record)
from framework.record import (CONSTITUTION_HASH,  # noqa: E402
                              FrameworkStore,
                              assembly_record_hash)

from fabric.canonical import canonical  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from connector_transport import (  # noqa: E402
    install_connector_transport)
from groq_connector_transport import (  # noqa: E402
    install_groq_connector_raw_call,
    install_groq_connector_transport)

RUN_ID = "run-first-worker-1"
MODEL_DEFAULT = "moonshotai/kimi-k3.1-pro"
CONNECTOR_HELPER = os.path.expanduser(
    "~/workspace/custom-connectors/custom.nvidia/bin/"
    "nvidia_api.py")

# The Groq route (GROQ-TRANSPORT-SCOPE-2026-11-23.md Rev 2,
# INDEX 228-231): selected by WORKER_ROUTE=groq, with the
# model pinned — no fallback, no alias, no automatic
# selection. The helper path is overridable via
# GROQ_HELPER_PATH so witnesses can substitute a stub.
GROQ_CONNECTOR_HELPER = os.path.expanduser(
    "~/workspace/custom-connectors/custom.groq/bin/"
    "groq_api.py")
GROQ_MODEL_PIN = "openai/gpt-oss-120b"
GROQ_ENDPOINT = ("https://api.groq.com/openai/v1/chat/"
                 "completions")


def resolve_worker_route(raw):
    """Route selection, fail-closed (INDEX 230, correction
    3): unset or empty preserves the existing NVIDIA route;
    "groq" selects the Groq route; any other non-empty
    value is refused — a typo must never silently change
    the experiment by falling back to NVIDIA."""
    if raw is None or raw == "":
        return "nvidia"
    if raw == "groq":
        return "groq"
    raise ValueError(
        f"WORKER_ROUTE={raw!r} is not a recognised route "
        f"(expected unset for the NVIDIA route, or 'groq'); "
        f"refusing to run")


def resolve_retrieval_mode(raw):
    """The attempt-7 retrieval mode flag (RETRIEVAL),
    fail-closed in the route selection's discipline: unset
    or empty preserves the historical configuration;
    "1" selects the retrieval mode (defined on the Groq
    route — the caller refuses it elsewhere); any other
    value is refused, so a typo can never silently change
    the experiment."""
    if raw is None or raw == "":
        return False
    if raw == "1":
        return True
    raise ValueError(
        f"RETRIEVAL={raw!r} is not a recognised value "
        f"(expected unset for the historical configuration, "
        f"or '1' for the attempt-7 retrieval mode); "
        f"refusing to run")


def resolve_probed_mode(raw):
    """The probed-mode flag (PROBED), in the same
    fail-closed discipline: unset or empty preserves the
    unprobed configurations; "1" selects the probed mode
    (defined only on the Groq route with the retrieval
    mode — the caller refuses it elsewhere); any other
    value is refused, so a typo can never silently change
    the experiment."""
    if raw is None or raw == "":
        return False
    if raw == "1":
        return True
    raise ValueError(
        f"PROBED={raw!r} is not a recognised value "
        f"(expected unset for the unprobed configurations, "
        f"or '1' for the probed mode); refusing to run")


class ModelPinMismatchError(Exception):
    """The provider-reported model id does not equal the
    pinned model id (INDEX 230, correction 2): a
    pre-activation stop, never a silent substitution."""

    def __init__(self, provider_model_id, pinned_model):
        super().__init__(
            f"provider-reported model id "
            f"{provider_model_id!r} does not match the "
            f"pinned model {pinned_model!r}")
        self.provider_model_id = provider_model_id
        self.pinned_model = pinned_model


def check_model_pin(provider_model_id, pinned_model):
    """The identity pin comparison, factored so the
    witness drives the real code path: returns True on an
    exact match, raises ModelPinMismatchError otherwise."""
    if provider_model_id != pinned_model:
        raise ModelPinMismatchError(provider_model_id,
                                    pinned_model)
    return True


def make_pinned_identify(adapter, pinned_model):
    """Wrap the adapter's identify() with the pin stop:
    the identity result is compared against the pin the
    moment it is known — inside generation, before any
    onboarding is recorded and long before activation —
    and a mismatch raises ModelPinMismatchError, so no
    activation and no worker call can follow it."""
    def _identify():
        identity = adapter.identify()
        provider_model_id = identity.get(
            "provider_model_id") if isinstance(
                identity, dict) else None
        check_model_pin(provider_model_id, pinned_model)
        return identity
    return _identify
BOUNDS = {"step_ceiling": 12, "deadline_seconds": 600}
TRACE = ("Ben's ruling 2026-11-23 (a modest real assignment "
         "before A4); FIRST-WORKER-RUN-SCOPE-2026-11-23.md "
         "Rev 2 (scope PASSED)")
ASSIGNMENT = (
    "Read the source documents in your sandbox: "
    "sources/stock-take.md, sources/a3-pass.md, and "
    "sources/index-tail.md. Write brief.md: a plain-words "
    "brief, at most ~600 words, that a newcomer could read "
    "to learn what this framework is, what has actually been "
    "proven, what has not been proven, and what remains to "
    "be built. Stay accurate to the sources; invent nothing; "
    "where the sources disagree with each other, say so.")
VERIFICATION_LIST = [
    "the brief is accurate to the three named sources, claim "
    "by claim",
    "the brief states what has not been proven as plainly as "
    "what has",
    "the brief invents nothing the sources do not contain",
]
GRANTS = [
    {"tool": "sandbox.read",
     "scope_ceiling": {"path_prefix": "sources/"},
     "side_effect_class": "read", "bound": {"count": 6},
     "authority_trace": TRACE},
    {"tool": "sandbox.write",
     "scope_ceiling": {"path_prefix": "/"},
     "side_effect_class": "write", "bound": {"count": 4},
     "authority_trace": TRACE},
]

# The attempt-7 retrieval configuration (ATTEMPT7-RELEASE-
# PROPOSAL-2026-11-23.md; Ben's authorisation, INDEX 256;
# the examiner's release examination, INDEX 257). A
# distinct mode — RETRIEVAL=1 on the Groq route — and the
# historical configuration above stands exactly as it was.
# The assembly declares the retrieval contract; the grants
# are the proposal's two-path set: the retrieval tools
# under the sources scope (the sealed evidence) and under
# the scratch scope (the worker's own desk), and the write
# grant under scratch alone. The scope prefixes are the
# registry's exact scope names — the doorway's retrieval
# admission matches a grant's prefix to the authority
# path's scope by equality, so "sources"/"scratch" here
# are load-bearing spellings, not style. The case's
# assignment names the deliverable's exact path,
# scratch/brief.md (INDEX 257, blocker 2): the worker is
# instructed to write where its grants permit, and the
# harness collects the brief from that path.
RETRIEVAL_TRACE = ("ATTEMPT7-RELEASE-PROPOSAL-2026-11-23.md; "
                   "Ben's authorisation (INDEX 256); the "
                   "examiner's release examination "
                   "(INDEX 257)")
ASSIGNMENT_RETRIEVAL = (
    "Read the source documents in your sandbox: "
    "sources/stock-take.md, sources/a3-pass.md, and "
    "sources/index-tail.md. Write scratch/brief.md: a "
    "plain-words brief, at most ~600 words, that a newcomer "
    "could read to learn what this framework is, what has "
    "actually been proven, what has not been proven, and "
    "what remains to be built. Stay accurate to the "
    "sources; invent nothing; where the sources disagree "
    "with each other, say so.")
BRIEF_SANDBOX_PATH = "scratch/brief.md"


def _retrieval_grant(tool, prefix, count):
    return {"tool": tool,
            "scope_ceiling": {"path_prefix": prefix},
            "side_effect_class":
                "write" if tool == "sandbox.write" else "read",
            "bound": {"count": count},
            "authority_trace": RETRIEVAL_TRACE}


GRANTS_RETRIEVAL = (
    [_retrieval_grant(tool, "sources", 12)
     for tool in ("sandbox.list", "sandbox.search",
                  "sandbox.read_range", "sandbox.read")]
    + [_retrieval_grant("sandbox.write", "scratch", 4)]
    + [_retrieval_grant(tool, "scratch", 12)
       for tool in ("sandbox.list", "sandbox.search",
                    "sandbox.read_range", "sandbox.read")])


def _commission_brief(assignment, manifest_hash):
    """The crew brief the commission carries, in either
    mode: the assignment (the mode's own text), the
    verification list, the evidence boundary naming the
    manifest hash and the three source paths, and the
    scoped bounds."""
    return {
        "part": "part-A",
        "assignment": assignment,
        "verification_list": list(VERIFICATION_LIST),
        "evidence_boundary":
            f"source manifest sha256:{manifest_hash}; "
            "sources: sources/stock-take.md, "
            "sources/a3-pass.md, sources/index-tail.md",
        "loop_bounds": dict(BOUNDS),
    }


def _write_grant_problem(grants):
    """Why the grant set cannot lawfully receive the
    deliverable, or None (INDEX 257, blocker 2): some
    sandbox.write grant's scope ceiling must admit
    scratch/brief.md under the v3 ceiling contract — the
    same pure check the doorway applies — so the case's
    instruction and the sealed authority cannot disagree
    about where the brief may be written."""
    for grant in grants or []:
        if not isinstance(grant, dict) or \
                grant.get("tool") != "sandbox.write":
            continue
        ok, _ground = tool_policy.check_ceiling(
            "sandbox.write", grant.get("scope_ceiling"),
            {"path": BRIEF_SANDBOX_PATH, "content": "x"},
            version=tool_policy.RETRIEVAL_REGISTRY_VERSION)
        if ok:
            return None
    return ("no sandbox.write grant's scope covers "
            f"{BRIEF_SANDBOX_PATH}; the case instructs the "
            "worker to write where no grant permits")

# (filed document in the project root, staged name, provenance)
SOURCES = [
    ("VANE-STOCK-TAKE-2026-11-23.md", "stock-take.md",
     "collaboration-framework/VANE-STOCK-TAKE-2026-11-23.md "
     "(Vane's stock-take; INDEX 187)"),
    ("VANE-PIECE-A3-PASS-2026-11-23.md", "a3-pass.md",
     "collaboration-framework/VANE-PIECE-A3-PASS-2026-11-23.md "
     "(Vane's Piece A3 pass letter; INDEX 186)"),
]
INDEX_FIRST, INDEX_LAST, INDEX_NEXT = 165, 187, 188


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path):
    with open(path, "rb") as fh:
        return _sha256_bytes(fh.read())


def extract_index_entries(index_path, first=INDEX_FIRST,
                          last=INDEX_LAST, nxt=INDEX_NEXT):
    """The INDEX entries `first`..`last` as one text: from the
    line opening entry `first` to just before the line opening
    entry `nxt`. Raises if either boundary is missing, so a
    renumbered INDEX fails loudly rather than staging the
    wrong slice."""
    with open(index_path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    start = end = None
    for i, line in enumerate(lines):
        if start is None and re.match(rf"^{first}\.\s", line):
            start = i
        elif start is not None and \
                re.match(rf"^{nxt}\.\s", line):
            end = i
            break
    if start is None:
        raise ValueError(f"INDEX entry {first} not found")
    if end is None:
        end = len(lines)
    text = "\n".join(lines[start:end]).rstrip() + "\n"
    if not re.search(rf"^{last}\.\s", text, re.M):
        raise ValueError(f"INDEX entry {last} not in the slice")
    return text


# The first-worker assignment's source-set identity
# (evidenced-run release examination, INDEX 322): the
# manifest hash the probed1 run staged and sealed — read
# from live-demo/first-worker-probed1/report.json, where
# it stands as that run's manifest_hash. Verifying a
# freshly built manifest against itself proves internal
# consistency only; THIS value is the identity of the
# released source set, and a run of this line whose
# staged manifest hashes to anything else is not the
# released assignment, however consistent it is
# internally. It is therefore an explicit pre-activation
# release condition in both phases (below).
EXPECTED_MANIFEST_HASH = (
    "bd6f3cae7cb5fa1624a78a501566721099a55abe3d35852784"
    "b4ae3a287d904f")


def _manifest_identity_problem(manifest_hash):
    """Why a staged manifest is not the released source
    set, or None: the built hash must EQUAL the probed1
    manifest hash — the first-worker assignment's
    source-set identity — not merely verify against the
    files it was built from."""
    if manifest_hash != EXPECTED_MANIFEST_HASH:
        return (f"the staged source manifest hashes to "
                f"{manifest_hash}, not the first-worker "
                f"assignment's source-set identity "
                f"{EXPECTED_MANIFEST_HASH} (the probed1 "
                f"manifest); the staged source set is not "
                f"the released one")
    return None


def _staged_source_problem(manifest, sandbox):
    """Why the staged sources under sandbox do not stand
    as the manifest says, or None: every manifest entry's
    file must stand under sandbox and hash to the entry's
    sha256. The fresh path runs this after issue, before
    activation; phase 2 runs it against the phase-1
    sandbox after the manifest identity check (INDEX
    324) — the manifest hash proves the manifest is the
    pinned manifest, while this proves the files the
    worker will actually read still match it. A missing
    file is a problem in its own right, named as such:
    _sha256_file would raise on it rather than refuse."""
    for entry in manifest["sources"]:
        staged = os.path.join(sandbox, entry["path"])
        if not os.path.exists(staged):
            return (f"staged {entry['path']} is missing "
                    f"from the sandbox")
        if _sha256_file(staged) != entry["sha256"]:
            return (f"staged {entry['path']} no longer "
                    f"hashes to the manifest")
    return None


def stage(run_dir, root=ROOT):
    """Stage the sandbox and the source manifest under
    run_dir. Returns (manifest, manifest_hash). Idempotent:
    the staged sources are recopied from the filed documents
    every time, so what the manifest hashes is what stands
    in the sandbox."""
    sources_dir = os.path.join(run_dir, "sandbox", "sources")
    os.makedirs(sources_dir, exist_ok=True)
    entries = []
    for filed, staged, provenance in SOURCES:
        dest = os.path.join(sources_dir, staged)
        shutil.copyfile(os.path.join(root, filed), dest)
        entries.append({
            "path": f"sources/{staged}",
            "sha256": _sha256_file(dest),
            "provenance": provenance})
    tail = extract_index_entries(os.path.join(root, "INDEX.md"))
    tail_path = os.path.join(sources_dir, "index-tail.md")
    with open(tail_path, "w", encoding="utf-8") as fh:
        fh.write(tail)
    entries.append({
        "path": "sources/index-tail.md",
        "sha256": _sha256_file(tail_path),
        "provenance": "collaboration-framework/INDEX.md, "
                      f"entries {INDEX_FIRST}–{INDEX_LAST} "
                      "(the A2/A3 arc), extracted verbatim"})
    entries.sort(key=lambda e: e["path"])
    manifest = {"sources": entries}
    canonical = json.dumps(manifest, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    manifest_hash = _sha256_bytes(canonical)
    with open(os.path.join(run_dir, "manifest.json"), "w",
              encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1)
        fh.write("\n")
    return manifest, manifest_hash


def _act(doorway, token, type_, payload):
    return doorway.act(token, type_, payload,
                       view_seq=doorway.store.head_seq())


def run_checker(store):
    """The §3.10 checker over the store, exactly as the A3
    suite runs it: quiesce the WAL, hand it the store path,
    the run id and the projection snapshot on stdin, read
    the verdict as JSON."""
    store._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    req = {"store_path": store.path,
           "run_id": store.get_run_id(),
           "snapshot": projection.snapshot(store)}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=SRC)
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "checker"],
        input=json.dumps(req), capture_output=True, text=True,
        env=env, cwd=ROOT)
    return json.loads(proc.stdout)


def export_store(store_path, out_path):
    """The store's complete contents as text, in the live
    demo's export shape ({"runs": [...], "events": [...]},
    every stored column verbatim) so the record can be
    rebuilt and replayed from text alone."""
    conn = sqlite3.connect(store_path)
    try:
        runs = [dict(zip(("run_id", "constitution_hash",
                           "status"), row))
                for row in conn.execute(
                    "SELECT run_id, constitution_hash, status "
                    "FROM runs ORDER BY run_id")]
        cols = ("event_seq", "event_id", "run_id", "type",
                "actor", "affected", "payload", "ts",
                "prev_hash", "hash")
        events = [dict(zip(cols, row)) for row in conn.execute(
            "SELECT event_seq, event_id, run_id, type, actor, "
            "affected, payload, ts, prev_hash, hash FROM "
            "events ORDER BY event_seq")]
    finally:
        conn.close()
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump({"runs": runs, "events": events}, fh,
                  indent=1)
    return len(events)


def verify_config():
    """The dry self-check for the retrieval mode (INDEX
    257, blocker 2): builds the attempt-7 assembly inputs —
    staging, commission, sealing, the office issue and its
    pre-activation verification, and generation under a
    stub identity — in a throwaway directory, asserting the
    release configuration without activating and without
    any provider call. The stub identity is a plain mapping
    (the generator accepts one), so no adapter exists here
    at all. Asserts: the issued case's assignment names
    scratch/brief.md exactly (and not the historical
    deliverable instruction); the sealed record declares
    the retrieval contract and carries exactly the two-path
    grant set; a sealed write grant's scope covers
    scratch/brief.md under the v3 ceiling contract; the
    collection path is the sandbox's scratch/brief.md; and
    no activation or iteration stands in the record.
    Prints the outcome as JSON; returns 0 or 1."""
    problems = []

    def expect(label, cond):
        if not cond:
            problems.append(label)
        return cond

    tmp = tempfile.mkdtemp(prefix="first-worker-verify-")
    run_dir = os.path.join(tmp, "run")
    os.makedirs(run_dir)
    sandbox = os.path.join(run_dir, "sandbox")
    manifest, manifest_hash = stage(run_dir)
    expect("the staged manifest is the first-worker "
           "assignment's source-set identity (the probed1 "
           "manifest hash, INDEX 322)",
           _manifest_identity_problem(manifest_hash)
           is None)
    store = FrameworkStore(os.path.join(run_dir, "run.db"))
    store.insert_run(RUN_ID, CONSTITUTION_HASH)
    store.append("RUN_COMMISSIONED", "dir-1", [], {
        "run_id": RUN_ID,
        "tree": {"part-A": []},
        "seats": {
            "orch-1": {"role": "orchestrator",
                       "identity_status": "declared"},
            "exam-1": {"role": "examiner",
                       "identity_status": "declared"},
            "dir-1": {"role": "director",
                      "identity_status": "declared"},
            "crew-1": {"role": "crew",
                       "identity_status": "unverified"},
        },
        "briefs": {"crew-1": _commission_brief(
            ASSIGNMENT_RETRIEVAL, manifest_hash)},
    })
    store.commit()
    doorway = Doorway(store)
    office = Office(doorway)
    gen = Generator(doorway)
    tok = {s: doorway.issue_token(s)
           for s in ("orch-1", "exam-1", "dir-1", "crew-1")}
    _act(doorway, tok["orch-1"], "MATERIAL_SEALED", {
        "material_id": f"source-manifest sha256:"
                       f"{manifest_hash}",
        "boundary": ["crew-1"]})
    for entry in manifest["sources"]:
        _act(doorway, tok["orch-1"], "MATERIAL_SEALED", {
            "material_id": f"{entry['path']} "
                           f"sha256:{entry['sha256']}",
            "boundary": ["crew-1"]})
    issued = office.issue_new(tok["orch-1"], "crew-1")
    if not expect("the case issues through the office route",
                  bool(issued.get("ok"))):
        print(json.dumps({"verify_config": "failed",
                          "problems": problems}, indent=1))
        return 1
    _act(doorway, tok["exam-1"], "CASE_JUDGED",
         {"case_id": issued["case_id"],
          "version": issued["version"]})
    office.authorise(tok["orch-1"], issued["case_id"],
                     issued["version"])
    content, _version = established_case_content(
        doorway.state(), issued["case_id"])
    content = content or {}
    boundary = content.get("evidence_boundary") or []
    expect("the issued case's evidence boundary identifies "
           "the source manifest hash",
           any(manifest_hash in str(item) for item in boundary))
    expect("the issued case carries the scoped bounds "
           "{12, 600}",
           content.get("loop_bounds") == BOUNDS)
    assignment = content.get("assignment") or ""
    expect("the issued case's assignment names "
           "scratch/brief.md exactly",
           BRIEF_SANDBOX_PATH in assignment)
    expect("the issued case's assignment does not carry "
           "the historical deliverable instruction",
           "Write brief.md" not in assignment)
    gen.propose(tok["orch-1"], "crew-1", part="part-A",
                role_requirements="a model able to read three "
                                  "source documents and write "
                                  "a short, accurate, "
                                  "plain-words brief")
    generated = gen.generate(
        tok["orch-1"], "crew-1",
        {"declaration": "verify-config stub identity (no "
                        "provider call is made by this check)",
         "provider_model_id": GROQ_MODEL_PIN},
        skills=[], grants=GRANTS_RETRIEVAL,
        model_requested=GROQ_MODEL_PIN, retrieval=True)
    if not expect("generation succeeds under the stub "
                  "identity", bool(generated.get("ok"))):
        print(json.dumps({"verify_config": "failed",
                          "problems": problems}, indent=1))
        return 1
    sealed = doorway._generated_payload(
        generated["assembly_id"]) or {}
    expect("the sealed record declares the retrieval "
           "contract",
           sealed.get("catalogue_contract")
           == tool_policy.RETRIEVAL_CATALOGUE_CONTRACT)
    sealed_pairs = sorted(
        (g.get("tool"),
         (g.get("scope_ceiling") or {}).get("path_prefix"))
        for g in sealed.get("grants") or [])
    expected_pairs = sorted(
        (g["tool"], g["scope_ceiling"]["path_prefix"])
        for g in GRANTS_RETRIEVAL)
    expect("the sealed grants are exactly the two-path set "
           "(retrieval tools under sources and scratch; the "
           "write grant under scratch)",
           sealed_pairs == expected_pairs)
    expect("a sealed write grant's scope covers "
           "scratch/brief.md under the v3 ceiling contract",
           _write_grant_problem(sealed.get("grants")) is None)
    collection = os.path.join(sandbox, *BRIEF_SANDBOX_PATH
                              .split("/"))
    expect("the collection path is the run sandbox's "
           "scratch/brief.md",
           os.path.relpath(collection, sandbox)
           == os.path.join("scratch", "brief.md"))
    events = store.all_events()
    expect("no activation stands in the record (the check "
           "does not activate)",
           not any(e["type"] == "INSTANCE_ACTIVATED"
                   for e in events))
    expect("no loop iteration stands in the record (the "
           "check does not run)",
           not any(e["type"] == "LOOP_ITERATION"
                   for e in events))
    report = {
        "verify_config": "ok" if not problems else "failed",
        "mode": "attempt-7 retrieval (WORKER_ROUTE=groq, "
                "RETRIEVAL=1)",
        "manifest_hash": manifest_hash,
        "case_assignment_names": BRIEF_SANDBOX_PATH,
        "sealed_catalogue_contract":
            sealed.get("catalogue_contract"),
        "sealed_grant_pairs": [list(p) for p in sealed_pairs],
        "collection_path": "sandbox/" + BRIEF_SANDBOX_PATH,
        "activation_performed": False,
        "provider_call_made": False,
        "problems": problems,
    }
    print(json.dumps(report, indent=1))
    return 0 if not problems else 1


def _finish_probe_phase1(store, store_path, run_dir,
                         doorway, assembly_id, instance_id,
                         generated, probe_result):
    """Phase 1's close: export the record as it stands
    (generated, probed, verified — unjudged), write
    probe-evidence.json (the ASSEMBLY_PROBED payload's
    essentials; derived matter, labelled as such), and
    print the plain summary the examiner's judgement will
    answer to. No judgement, no packing, no activation,
    no loop."""
    export_store(store_path,
                 os.path.join(run_dir, "run-export.json"))
    probed = doorway._probed_payload(assembly_id) or {}
    trials = [
        {"trial": t.get("trial"),
         "behaviour": t.get("behaviour"),
         "delivery": t.get("delivery"),
         "payload_form": t.get("payload_form"),
         "settled": t.get("settled"),
         "evidence_complete": t.get("evidence_complete")}
        for t in probed.get("trials") or []]
    evidence = {
        "kind": "first probed-mode run, phase 1 — probe "
                "evidence (derived matter, not record)",
        "run_id": RUN_ID,
        "assembly_id": assembly_id,
        "instance_id": instance_id,
        "generated_record_hash":
            (generated or {}).get("record_hash"),
        "suite": probed.get("suite"),
        "suite_hash": probed.get("suite_hash"),
        "route": probed.get("route"),
        "model": probed.get("model"),
        "fingerprint": probed.get("fingerprint"),
        "evidence_hash": probed.get("evidence_hash"),
        "settled_count": probed.get("settled_count"),
        "counts": probed.get("counts"),
        "recommended_mode": probed.get("recommended_mode"),
        "trials": trials,
    }
    evidence_path = os.path.join(run_dir,
                                 "probe-evidence.json")
    with open(evidence_path, "w", encoding="utf-8") as fh:
        json.dump(evidence, fh, indent=1)
    counts = probed.get("counts") or {}
    print("probe phase 1 complete — the assembly stands "
          "generated, probed and verified; no judgement "
          "recorded, nothing packed or activated")
    print(f"probe trials: settled "
          f"{probed.get('settled_count')} of {len(trials)}; "
          f"behaviour {counts.get('behaviour')}; delivery "
          f"{counts.get('delivery')}")
    print(f"recommended mode: "
          f"{probed.get('recommended_mode')}")
    print(f"probe evidence hash: "
          f"{probed.get('evidence_hash')}")
    print(f"probe evidence: {evidence_path}")
    return 0


def _receipt_problem(receipt, run_dir_assembly_id,
                       generated_hash, entry, probed):
    """Why an examiner decision receipt may not carry a
    phase-2 judgement, or None (INDEX 293): every field
    must identify the exact phase-1 run and its standing
    record — the run, the one assembly, its generated
    record by hash, the probe event by sequence, the
    probe evidence by hash, the configuration fingerprint
    — and the decision itself must be complete: a mode
    the adapter speaks, stated grounds, the examiner's
    recorded label and the decision's recorded time."""
    if not isinstance(receipt, dict):
        return "the decision receipt is not a JSON object"
    if receipt.get("run_id") != RUN_ID:
        return (f"the receipt names run "
                f"{receipt.get('run_id')!r}; this harness's "
                f"run is {RUN_ID!r}")
    if receipt.get("assembly_id") != run_dir_assembly_id:
        return (f"the receipt names assembly "
                f"{receipt.get('assembly_id')!r}; the "
                f"phase-1 record's assembly is "
                f"{run_dir_assembly_id!r}")
    if receipt.get("generated_record_hash") != \
            generated_hash:
        return ("the receipt's generated-record hash "
                f"{receipt.get('generated_record_hash')!r} "
                f"is not the standing generated record's "
                f"hash {generated_hash} — the receipt must "
                f"identify the exact record the examiner "
                f"judged")
    if receipt.get("probed_seq") != entry.get("probed_seq"):
        return (f"the receipt names probe event "
                f"{receipt.get('probed_seq')!r}; the "
                f"assembly's probe stands at "
                f"{entry.get('probed_seq')}")
    if receipt.get("probe_evidence_hash") != \
            probed.get("evidence_hash"):
        return ("the receipt's probe evidence hash "
                f"{receipt.get('probe_evidence_hash')!r} "
                f"is not the standing probe evidence's hash "
                f"{probed.get('evidence_hash')} — the "
                f"receipt must identify the exact evidence "
                f"the examiner weighed")
    if receipt.get("fingerprint") != \
            probed.get("fingerprint"):
        return ("the receipt's configuration fingerprint "
                f"{receipt.get('fingerprint')!r} is not "
                f"the standing probe's fingerprint "
                f"{probed.get('fingerprint')}")
    if receipt.get("adapter_mode") not in \
            probe_module.ADAPTER_MODES:
        return (f"the receipt selects adapter mode "
                f"{receipt.get('adapter_mode')!r}; the "
                f"modes are {probe_module.ADAPTER_MODES}")
    grounds = receipt.get("mode_grounds")
    if not isinstance(grounds, str) or not grounds.strip():
        return ("the receipt records no grounds for its "
                "mode; a decision without grounds does not "
                "carry a judgement")
    if not isinstance(receipt.get("examiner"), str) or \
            not receipt.get("examiner").strip():
        return ("the receipt names no examiner; the "
                "decision's recorded label is part of its "
                "provenance")
    if not isinstance(receipt.get("decided_at"), str) or \
            not receipt.get("decided_at").strip():
        return ("the receipt records no decided_at; the "
                "decision's recorded time is part of its "
                "provenance")
    return None


def run_probe_phase2(run_dir, receipt_path):
    """Phase 2: reopen a phase-1 run directory and carry
    its assembly from the examiner's judgement to the
    finished run, exactly as the retrieval mode runs it.
    The judgement is recorded FROM THE EXAMINER'S
    DECISION RECEIPT (INDEX 293): the receipt is loaded
    and every field validated against the standing
    phase-1 record before anything is recorded, its
    canonical hash is bound into the judgement, and the
    judgement payload itself states that the harness-
    issued examiner token is the recording mechanism,
    not independent authentication of the examiner's
    identity. The receipt's exact bytes are retained
    in the run directory as decision-receipt.json
    before the judgement is recorded (INDEX 295) —
    the record carries the hash, and the retained file
    is the very document that hash identifies; a
    retention failure refuses before any judgement
    stands. Refuses — before recording anything — where
    the receipt is missing, unreadable or mismatched, or
    where the store does not stand exactly as phase 1
    left it: a probe must stand, no judgement may stand
    yet, and nothing may stand activated."""
    try:
        with open(receipt_path, encoding="utf-8") as fh:
            receipt = json.load(fh)
    except (OSError, ValueError) as exc:
        print(f"ABORT: the examiner decision receipt at "
              f"{receipt_path} cannot be read: {exc}",
              file=sys.stderr)
        return 1
    store_path = os.path.join(run_dir, "run.db")
    if not os.path.exists(store_path):
        print(f"ABORT: no phase-1 run store stands at "
              f"{store_path}; run --probe-phase1 first",
              file=sys.stderr)
        return 1
    store = FrameworkStore(store_path)
    doorway = Doorway(store)
    gen = Generator(doorway)
    tok = {s: doorway.issue_token(s)
           for s in ("orch-1", "exam-1", "dir-1", "crew-1")}
    state = doorway.state()
    assemblies = state.get("assemblies") or {}
    if len(assemblies) != 1:
        print(f"ABORT: the record carries "
              f"{len(assemblies)} assemblies, not the one "
              f"phase 1 assembles; refusing to run",
              file=sys.stderr)
        return 1
    assembly_id, entry = next(iter(assemblies.items()))
    instance_id = entry.get("instance_id")
    event_types = [e["type"] for e in store.all_events()]
    if "ASSEMBLY_PROBED" not in event_types:
        print("ABORT: no ASSEMBLY_PROBED stands in the "
              "record; this run directory is not a phase-1 "
              "probed run", file=sys.stderr)
        return 1
    if "ASSEMBLY_JUDGED" in event_types:
        print("ABORT: an ASSEMBLY_JUDGED already stands "
              "in the record; phase 2 records the "
              "judgement exactly once", file=sys.stderr)
        return 1
    if "INSTANCE_ACTIVATED" in event_types:
        print("ABORT: the instance already stands "
              "activated; this run has already been "
              "carried through phase 2", file=sys.stderr)
        return 1
    probed = doorway._probed_payload(assembly_id) or {}
    generated_hash = assembly_record_hash(
        doorway._generated_payload(assembly_id) or {})
    problem = _receipt_problem(
        receipt, assembly_id, generated_hash, entry, probed)
    if problem is not None:
        print(f"ABORT: the decision receipt does not "
              f"carry this run: {problem}", file=sys.stderr)
        return 1
    receipt_hash = hashlib.sha256(
        canonical(receipt)).hexdigest()
    mode = receipt["adapter_mode"]
    # The retention (INDEX 295): the receipt's exact
    # bytes are copied into the run directory BEFORE
    # the judgement is recorded — the record carries
    # the canonical hash, and decision-receipt.json is
    # the very document that hash identifies, standing
    # with the run's evidence. A failed copy fails
    # phase 2 here, before any judgement stands: the
    # retention is part of the decision's evidence.
    try:
        with open(receipt_path, "rb") as fh:
            receipt_bytes = fh.read()
        with open(os.path.join(
                run_dir, "decision-receipt.json"),
                "wb") as fh:
            fh.write(receipt_bytes)
    except OSError as exc:
        print(f"ABORT: the decision receipt could not "
              f"be retained in the run directory: {exc}",
              file=sys.stderr)
        return 1
    with open(os.path.join(run_dir, "manifest.json"),
              encoding="utf-8") as fh:
        manifest = json.load(fh)
    manifest_hash = _sha256_bytes(json.dumps(
        manifest, sort_keys=True,
        separators=(",", ":")).encode("utf-8"))
    # The source-set identity, phase 2's form (INDEX
    # 322): the standing manifest must BE the probed1
    # manifest. The refusal lands here — after the
    # receipt's validation and retention, before the
    # judgement is recorded and before any activation.
    identity_problem = _manifest_identity_problem(
        manifest_hash)
    if identity_problem is not None:
        print(f"ABORT: {identity_problem}",
              file=sys.stderr)
        return 1
    # The staged files themselves (INDEX 324): the
    # manifest hash proves the standing manifest IS the
    # pinned manifest; it does not prove the files under
    # the phase-1 sandbox still match it — between the
    # phases they could change while manifest.json
    # stands untouched. Re-verify every entry against
    # its staged file here — after the manifest
    # identity, before the adapter is built, any
    # judgement is recorded or anything activates.
    staged_problem = _staged_source_problem(
        manifest, os.path.join(run_dir, "sandbox"))
    if staged_problem is not None:
        print(f"ABORT: {staged_problem}",
              file=sys.stderr)
        return 1
    adapter = _build_adapter("groq")
    judgement = gen.judgement(
        assembly_id, adapter_mode=mode,
        mode_grounds=receipt["mode_grounds"],
        decision_receipt_hash=receipt_hash,
        decision_examiner=receipt["examiner"])
    if judgement is None:
        print("ABORT: the judgement payload cannot be "
              "computed; the generated record does not "
              "stand", file=sys.stderr)
        return 1
    print(f"probe phase 2 — the examiner's judgement, "
          f"recorded from decision receipt "
          f"{receipt_hash}: mode {mode!r}, on the standing "
          f"probe evidence {probed.get('evidence_hash')}")
    return _judge_pack_run(
        doorway, gen, tok, store, store_path, run_dir,
        os.path.join(run_dir, "sandbox"), "groq", True,
        adapter, manifest, manifest_hash, assembly_id,
        instance_id, judgement,
        {"probed_mode": True, "adapter_mode": mode,
         "decision_receipt_hash": receipt_hash,
         "decision_receipt_file": "decision-receipt.json",
         "decision_examiner": receipt["examiner"],
         "decision_recording":
             judgement.get("decision_recording")},
        pace_iterations=True)


def _stub_probe_captures():
    """The probed verify-config's scripted raw captures:
    five captures in the probe protocol's shape — a
    native-catalogue answer, a text-contract answer, the
    commentary hybrid the provider refuses to deliver
    (the empirical run's shape, INDEX 274), then the two
    again — so the dry run exercises the probe stage's
    classification of every shape that matters without
    any provider call."""
    native_body = json.dumps({
        "id": "chatcmpl-probe-verify",
        "model": GROQ_MODEL_PIN,
        "choices": [{"index": 0, "message": {
            "role": "assistant", "content": None,
            "tool_calls": [{
                "id": "fc_verify1", "type": "function",
                "function": {
                    "name": "probe.lookup",
                    "arguments": json.dumps(
                        {"object": "brass lantern"})}}]}}]})
    text_body = json.dumps({
        "id": "chatcmpl-probe-verify",
        "model": GROQ_MODEL_PIN,
        "choices": [{"index": 0, "message": {
            "role": "assistant",
            "content": json.dumps({
                "outcome": "tool_requests",
                "tool_requests": [{
                    "tool": "probe.lookup",
                    "parameters": {
                        "object": "brass lantern"}}]})}}]})
    hybrid_error = json.dumps({"error": {
        "message": "attempted to call tool 'commentary' "
                   "which was not in request.tools",
        "code": "tool_use_failed",
        "failed_generation": json.dumps({
            "name": "commentary",
            "arguments": json.dumps({"tool_requests": [{
                "tool": "probe.lookup",
                "parameters": {
                    "object": "brass lantern"}}]})})}})
    accepted = {"http_status": 200, "error_body": None,
                "diagnostics": None,
                "metadata": {"id": "chatcmpl-probe-verify",
                             "model": GROQ_MODEL_PIN}}
    return [
        dict(accepted, body=native_body),
        dict(accepted, body=text_body),
        {"body": None, "error_body": hybrid_error,
         "http_status": 400,
         "diagnostics": "stub helper: provider error "
                        "(scripted capture)",
         "metadata": {}},
        dict(accepted, body=native_body),
        dict(accepted, body=text_body),
    ]


def verify_config_probed():
    """The dry self-check for the probed mode: the
    retrieval configuration's assembly path, plus
    generation under the probe contract, the probe stage
    run against a STUB raw call (scripted captures — no
    provider call of any kind), and construction
    verification naming the probe evidence. Asserts the
    record's event sequence (GENERATED -> PROBED ->
    VERIFIED, and nothing past it) and the probe
    payload's shape, with no judgement, no packing and
    no activation. Prints the outcome as JSON; returns
    0 or 1."""
    problems = []

    def expect(label, cond):
        if not cond:
            problems.append(label)
        return cond

    tmp = tempfile.mkdtemp(prefix="first-worker-verify-"
                                 "probed-")
    run_dir = os.path.join(tmp, "run")
    os.makedirs(run_dir)
    manifest, manifest_hash = stage(run_dir)
    expect("the staged manifest is the first-worker "
           "assignment's source-set identity (the probed1 "
           "manifest hash, INDEX 322)",
           _manifest_identity_problem(manifest_hash)
           is None)
    store = FrameworkStore(os.path.join(run_dir, "run.db"))
    store.insert_run(RUN_ID, CONSTITUTION_HASH)
    store.append("RUN_COMMISSIONED", "dir-1", [], {
        "run_id": RUN_ID,
        "tree": {"part-A": []},
        "seats": {
            "orch-1": {"role": "orchestrator",
                       "identity_status": "declared"},
            "exam-1": {"role": "examiner",
                       "identity_status": "declared"},
            "dir-1": {"role": "director",
                      "identity_status": "declared"},
            "crew-1": {"role": "crew",
                       "identity_status": "unverified"},
        },
        "briefs": {"crew-1": _commission_brief(
            ASSIGNMENT_RETRIEVAL, manifest_hash)},
    })
    store.commit()
    doorway = Doorway(store)
    office = Office(doorway)
    gen = Generator(doorway)
    tok = {s: doorway.issue_token(s)
           for s in ("orch-1", "exam-1", "dir-1", "crew-1")}
    _act(doorway, tok["orch-1"], "MATERIAL_SEALED", {
        "material_id": f"source-manifest sha256:"
                       f"{manifest_hash}",
        "boundary": ["crew-1"]})
    for entry in manifest["sources"]:
        _act(doorway, tok["orch-1"], "MATERIAL_SEALED", {
            "material_id": f"{entry['path']} "
                           f"sha256:{entry['sha256']}",
            "boundary": ["crew-1"]})
    issued = office.issue_new(tok["orch-1"], "crew-1")
    if not expect("the case issues through the office route",
                  bool(issued.get("ok"))):
        print(json.dumps({"verify_config": "failed",
                          "problems": problems}, indent=1))
        return 1
    _act(doorway, tok["exam-1"], "CASE_JUDGED",
         {"case_id": issued["case_id"],
          "version": issued["version"]})
    office.authorise(tok["orch-1"], issued["case_id"],
                     issued["version"])
    content, _version = established_case_content(
        doorway.state(), issued["case_id"])
    content = content or {}
    boundary = content.get("evidence_boundary") or []
    expect("the issued case's evidence boundary identifies "
           "the source manifest hash",
           any(manifest_hash in str(item) for item in boundary))
    expect("the issued case carries the scoped bounds "
           "{12, 600}",
           content.get("loop_bounds") == BOUNDS)
    assignment = content.get("assignment") or ""
    expect("the issued case's assignment names "
           "scratch/brief.md exactly",
           BRIEF_SANDBOX_PATH in assignment)
    gen.propose(tok["orch-1"], "crew-1", part="part-A",
                role_requirements="a model able to read three "
                                  "source documents and write "
                                  "a short, accurate, "
                                  "plain-words brief")
    generated = gen.generate(
        tok["orch-1"], "crew-1",
        {"declaration": "verify-config stub identity (no "
                        "provider call is made by this check)",
         "provider_model_id": GROQ_MODEL_PIN},
        skills=[], grants=GRANTS_RETRIEVAL,
        model_requested=GROQ_MODEL_PIN, retrieval=True,
        probe=True)
    if not expect("generation succeeds under the stub "
                  "identity", bool(generated.get("ok"))):
        print(json.dumps({"verify_config": "failed",
                          "problems": problems}, indent=1))
        return 1
    assembly_id = generated["assembly_id"]
    sealed = doorway._generated_payload(assembly_id) or {}
    expect("the sealed record declares the retrieval "
           "contract",
           sealed.get("catalogue_contract")
           == tool_policy.RETRIEVAL_CATALOGUE_CONTRACT)
    expect("the sealed record declares the probe "
           "contract",
           sealed.get("probe_contract")
           == probe_module.PROBE_CONTRACT)
    sealed_pairs = sorted(
        (g.get("tool"),
         (g.get("scope_ceiling") or {}).get("path_prefix"))
        for g in sealed.get("grants") or [])
    expected_pairs = sorted(
        (g["tool"], g["scope_ceiling"]["path_prefix"])
        for g in GRANTS_RETRIEVAL)
    expect("the sealed grants are exactly the two-path set",
           sealed_pairs == expected_pairs)
    expect("a sealed write grant's scope covers "
           "scratch/brief.md under the v3 ceiling contract",
           _write_grant_problem(sealed.get("grants")) is None)
    captures = _stub_probe_captures()
    scripted = iter(captures)

    def stub_raw_call(request):
        return next(scripted)

    probed_result = gen.probe(
        tok["orch-1"], assembly_id, stub_raw_call,
        route="groq", model=GROQ_MODEL_PIN)
    expect("the probe stage records against the stub raw "
           "call", bool(probed_result.get("ok")))
    probed = doorway._probed_payload(assembly_id) or {}
    trials = probed.get("trials") or []
    expect("the probe payload carries five trials",
           len(trials) == 5)
    behaviours = [t.get("behaviour") for t in trials]
    expect("the scripted native answers classify "
           "native_catalogue (x2)",
           behaviours.count("native_catalogue") == 2)
    expect("the scripted text answers classify "
           "text_contract (x2)",
           behaviours.count("text_contract") == 2)
    hybrid = trials[2] if len(trials) > 2 else {}
    expect("the scripted hybrid classifies as "
           "environment_tool_attempt x provider_refused "
           "with payload_form text_contract_json",
           hybrid.get("behaviour") ==
           "environment_tool_attempt" and
           hybrid.get("delivery") == "provider_refused" and
           hybrid.get("payload_form") ==
           "text_contract_json")
    expect("all five scripted trials settle",
           probed.get("settled_count") == 5)
    expect("the split scripted distribution recommends no "
           "mode (2 native, 2 text, 1 refused attempt — "
           "no strict majority of the settled)",
           probed.get("recommended_mode") is None)
    expect("the probe payload's fingerprint is the Groq "
           "configuration's fingerprint",
           probed.get("fingerprint") ==
           probe_module.configuration_fingerprint(
               "groq", GROQ_MODEL_PIN))
    expect("the probe payload's evidence hash recomputes "
           "from the payload",
           probed.get("evidence_hash") ==
           probe_module.evidence_hash(probed))
    gen.verify(tok["orch-1"], assembly_id)
    events = store.all_events()
    seqs = {}
    for e in events:
        seqs.setdefault(e["type"], e["event_seq"])
    order = [seqs.get(t) for t in (
        "ASSEMBLY_GENERATED", "ASSEMBLY_PROBED",
        "ASSEMBLY_VERIFIED")]
    expect("the event sequence runs ASSEMBLY_GENERATED "
           "-> ASSEMBLY_PROBED -> ASSEMBLY_VERIFIED in "
           "that order",
           all(s is not None for s in order) and
           order == sorted(order))
    verified = [e for e in events
                if e["type"] == "ASSEMBLY_VERIFIED"]
    expect("the construction verification names the probe "
           "evidence hash",
           bool(verified) and
           verified[0]["payload"].get(
               "probe_evidence_hash") ==
           probed.get("evidence_hash"))
    event_types = [e["type"] for e in events]
    for absent in ("ASSEMBLY_JUDGED", "ASSEMBLY_PACKED",
                   "ASSEMBLY_ISSUE_AUTHORISED",
                   "INSTANCE_ACTIVATED", "LOOP_ITERATION"):
        expect(f"no {absent} stands in the record (the "
               f"check stops before judgement)",
               absent not in event_types)
    report = {
        "verify_config": "ok" if not problems else "failed",
        "mode": "probed (WORKER_ROUTE=groq, RETRIEVAL=1, "
                "PROBED=1)",
        "manifest_hash": manifest_hash,
        "sealed_catalogue_contract":
            sealed.get("catalogue_contract"),
        "sealed_probe_contract": sealed.get("probe_contract"),
        "probe": {
            "suite": probed.get("suite"),
            "fingerprint": probed.get("fingerprint"),
            "evidence_hash": probed.get("evidence_hash"),
            "settled_count": probed.get("settled_count"),
            "counts": probed.get("counts"),
            "recommended_mode":
                probed.get("recommended_mode"),
            "trials": [
                {"trial": t.get("trial"),
                 "behaviour": t.get("behaviour"),
                 "delivery": t.get("delivery"),
                 "payload_form": t.get("payload_form")}
                for t in trials],
        },
        "event_sequence": [
            e["type"] for e in events
            if e["type"].startswith("ASSEMBLY_")],
        "judgement_recorded": False,
        "activation_performed": False,
        "provider_call_made": False,
        "problems": problems,
    }
    print(json.dumps(report, indent=1))
    return 0 if not problems else 1


PACING_MIN_INTERVAL_SECONDS = 65.0


class IterationPacer:
    """Pacing at the harness/transport boundary (first
    live demonstration release examination, INDEX 412,
    phase-2 matter 1): the wrapper the phase-2 path
    places around the adapter as the loop's model
    callable, enforcing at least
    PACING_MIN_INTERVAL_SECONDS between successive
    outbound iteration calls.

    The spacing is start-to-start, measured on a
    monotonic clock at the actual call-start boundary —
    the moment the wrapped callable is invoked — never
    inferred from event timestamps. The first call of a
    run is not delayed; spacing binds successive calls
    only. The shortfall is re-measured on the monotonic
    clock after every sleep, as in the paced probe
    piece, so a sleeper that returns early leaves the
    boundary unmoved. After the pacing step the
    activation's absolute deadline — the monotonic
    deadline the loop hands every call — is rechecked:
    if it has expired, no provider request is made; the
    wrapper raises AdapterFailure and the loop takes
    its standing deadline path. The wrapper paces only:
    it never retries a request, never alters what is
    sent, in what order, or how outcomes are handled,
    and creates no second control loop.

    Transparency: the loop reads and writes adapter
    state through its model handle (the response-
    evidence seam, the BD-1 flag staging, render
    timings). Every attribute read delegates to the
    wrapped adapter and every attribute write lands on
    it, so the wrapper is invisible to both sides
    except for the wait. The clock and sleeper are
    injectable seams, as in the paced probe piece, so
    witnesses run on a simulated clock."""

    _OWN = ("_model", "_min_interval",
            "_monotonic_clock", "_sleeper",
            "_last_call_start")

    def __init__(self, model,
                 min_interval=PACING_MIN_INTERVAL_SECONDS,
                 monotonic_clock=None, sleeper=None):
        object.__setattr__(self, "_model", model)
        object.__setattr__(self, "_min_interval",
                           float(min_interval))
        object.__setattr__(
            self, "_monotonic_clock",
            monotonic_clock if monotonic_clock is not None
            else time.monotonic)
        object.__setattr__(
            self, "_sleeper",
            sleeper if sleeper is not None else time.sleep)
        object.__setattr__(self, "_last_call_start", None)

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._model, name)

    def __setattr__(self, name, value):
        if name in IterationPacer._OWN:
            object.__setattr__(self, name, value)
        else:
            setattr(self._model, name, value)

    def __call__(self, package, *args, **kwargs):
        clock = self._monotonic_clock
        if self._last_call_start is not None:
            earliest = self._last_call_start \
                + self._min_interval
            while clock() < earliest:
                self._sleeper(earliest - clock())
            deadline = kwargs.get("deadline")
            if deadline is not None \
                    and clock() >= deadline:
                raise AdapterFailure(
                    "no_response",
                    "the pacing wait carried this call "
                    "past the activation's absolute "
                    "deadline; no provider request was "
                    "made")
        object.__setattr__(self, "_last_call_start",
                           clock())
        return self._model(package, *args, **kwargs)


def _build_adapter(route):
    """The run's adapter, configured as the Piece 8 live
    harness configures it (endpoint / model / timeout from
    the environment), with its transport then carried
    through the registered connector helper (INDEX
    191/192): the environment-variable key route is not
    used by this harness — attempt 1 was rejected on it
    before activation — and the connector credential in
    the Secure Vault is the sanctioned route. The
    adapter's contract, strict validation, outcome typing
    and deadline behaviour are unchanged; only _call's
    transport is replaced, under the examiner's
    cancellation boundary (connector_transport.py). On
    the Groq route the model is PINNED (the pin overrides
    ADAPTER_MODEL for the run) and the transport is the
    Groq twin, through the Groq connector helper
    (GROQ_HELPER_PATH overridable for witnesses)."""
    if route == "groq":
        adapter = OpenAICompatibleAdapter(
            endpoint=os.environ.get("ADAPTER_ENDPOINT",
                                    GROQ_ENDPOINT),
            model=GROQ_MODEL_PIN,
            timeout=float(os.environ.get("ADAPTER_TIMEOUT",
                                         "120")))
        install_groq_connector_transport(
            adapter,
            os.environ.get("GROQ_HELPER_PATH",
                           GROQ_CONNECTOR_HELPER),
            adapter.model)
        return adapter
    adapter = OpenAICompatibleAdapter(
        endpoint=os.environ.get(
            "ADAPTER_ENDPOINT",
            "https://integrate.api.nvidia.com/v1/chat/"
            "completions"),
        model=os.environ.get("ADAPTER_MODEL",
                             MODEL_DEFAULT),
        timeout=float(os.environ.get("ADAPTER_TIMEOUT",
                                     "120")))
    install_connector_transport(adapter, CONNECTOR_HELPER,
                                adapter.model)
    return adapter


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    verify_only = "--verify-config" in argv
    argv = [a for a in argv if a != "--verify-config"]
    phase1 = "--probe-phase1" in argv
    argv = [a for a in argv if a != "--probe-phase1"]
    phase2 = "--probe-phase2" in argv
    argv = [a for a in argv if a != "--probe-phase2"]
    receipt_path = None
    if "--decision-receipt" in argv:
        at = argv.index("--decision-receipt")
        following = argv[at + 1:]
        if not following:
            print("ABORT: --decision-receipt takes the "
                  "examiner decision receipt's file: "
                  "--decision-receipt <file>",
                  file=sys.stderr)
            return 2
        receipt_path = following[0]
        argv = argv[:at] + following[1:]
    # Route and mode selection first, before any staging or
    # assembly work (INDEX 230, correction 3): an invalid
    # value refuses outright and nothing is staged.
    try:
        route = resolve_worker_route(
            os.environ.get("WORKER_ROUTE"))
        retrieval = resolve_retrieval_mode(
            os.environ.get("RETRIEVAL"))
        probed = resolve_probed_mode(
            os.environ.get("PROBED"))
    except ValueError as exc:
        print(f"ABORT: {exc}", file=sys.stderr)
        return 2
    if retrieval and route != "groq":
        print("ABORT: RETRIEVAL=1 selects the attempt-7 "
              "retrieval mode, which is defined on the Groq "
              "route (WORKER_ROUTE=groq); refusing to run",
              file=sys.stderr)
        return 2
    if probed and not (route == "groq" and retrieval):
        print("ABORT: PROBED=1 selects the probed mode, "
              "which is defined on the Groq route with the "
              "retrieval mode (WORKER_ROUTE=groq, "
              "RETRIEVAL=1); refusing to run",
              file=sys.stderr)
        return 2
    if (phase1 or phase2) and not probed:
        print("ABORT: --probe-phase1 / --probe-phase2 "
              "require the probed mode (PROBED=1); refusing "
              "to run", file=sys.stderr)
        return 2
    if phase1 and phase2:
        print("ABORT: --probe-phase1 and --probe-phase2 "
              "are distinct invocations; refusing to run",
              file=sys.stderr)
        return 2
    if verify_only:
        if probed:
            return verify_config_probed()
        if not retrieval:
            print("ABORT: --verify-config verifies the "
                  "retrieval mode's configuration; set "
                  "WORKER_ROUTE=groq and RETRIEVAL=1",
                  file=sys.stderr)
            return 2
        return verify_config()
    name = "first-worker" + (f"-{argv[0]}" if argv else "")
    run_dir = os.path.join(ROOT, "live-demo", name)
    if phase2:
        if receipt_path is None:
            print("ABORT: --probe-phase2 requires the "
                  "examiner's decision receipt: "
                  "--probe-phase2 --decision-receipt "
                  "<file>; the judgement is recorded from "
                  "the receipt, never from bare mode and "
                  "grounds arguments (INDEX 293)",
                  file=sys.stderr)
            return 2
        return run_probe_phase2(run_dir, receipt_path)
    if receipt_path is not None:
        print("ABORT: --decision-receipt belongs to "
              "--probe-phase2; refusing to run",
              file=sys.stderr)
        return 2
    if probed and not phase1:
        print("ABORT: PROBED=1 runs in two phases "
              "(--probe-phase1, then --probe-phase2 "
              "--decision-receipt <file>); there is no "
              "single-invocation probed run, because the "
              "examiner's judgement stands between the "
              "phases", file=sys.stderr)
        return 2
    store_path = os.path.join(run_dir, "run.db")
    if os.path.exists(store_path):
        print(f"refusing to overwrite the existing run store "
              f"at {store_path}; rerun with a suffix argument "
              f"for a fresh directory", file=sys.stderr)
        return 1
    os.makedirs(run_dir, exist_ok=True)
    return _run_fresh(run_dir, route, retrieval, probed,
                      phase1)


def _run_fresh(run_dir, route, retrieval, probed, phase1):
    """A fresh run directory's front flow: staging,
    commission, issue, pre-activation verification and
    assembly — and, in the probed mode, the probe stage
    and construction verification. The unprobed
    configurations finish from the judgement onward
    through _judge_pack_run; the probed mode's phase 1
    stops before judgement (_finish_probe_phase1), and
    its phase 2 reopens the directory and finishes the
    same way (run_probe_phase2)."""
    store_path = os.path.join(run_dir, "run.db")
    sandbox = os.path.join(run_dir, "sandbox")

    # 1. STAGE — sources fixed by manifest before anything
    # is commissioned.
    manifest, manifest_hash = stage(run_dir)
    print(f"manifest sha256: {manifest_hash}")
    # The source-set identity (INDEX 322): the staged
    # manifest must BE the probed1 manifest, not merely a
    # manifest that verifies against its own files. The
    # refusal lands here — before commission, before any
    # record event, long before activation.
    identity_problem = _manifest_identity_problem(
        manifest_hash)
    if identity_problem is not None:
        print(f"ABORT: {identity_problem}",
              file=sys.stderr)
        return 1

    # 2. COMMISSION — one part, four seats, the crew brief
    # carrying the assignment, the bounds, and (as recorded
    # brief matter) the evidence boundary naming the
    # manifest hash and the three source paths.
    store = FrameworkStore(store_path)
    store.insert_run(RUN_ID, CONSTITUTION_HASH)
    brief = _commission_brief(
        ASSIGNMENT_RETRIEVAL if retrieval else ASSIGNMENT,
        manifest_hash)
    store.append("RUN_COMMISSIONED", "dir-1", [], {
        "run_id": RUN_ID,
        "tree": {"part-A": []},
        "seats": {
            "orch-1": {"role": "orchestrator",
                       "identity_status": "declared"},
            "exam-1": {"role": "examiner",
                       "identity_status": "declared"},
            "dir-1": {"role": "director",
                      "identity_status": "declared"},
            "crew-1": {"role": "crew",
                       "identity_status": "unverified"},
        },
        "briefs": {"crew-1": brief},
    })
    store.commit()
    doorway = Doorway(store)
    office = Office(doorway)
    gen = Generator(doorway)
    tok = {s: doorway.issue_token(s)
           for s in ("orch-1", "exam-1", "dir-1", "crew-1")}

    # The office derives the issued case's evidence boundary
    # from MATERIAL_SEALED records (Piece 5): seal the
    # manifest and each source, boundary naming the crew
    # seat, ids naming the manifest hash / the source paths
    # and their hashes.
    _act(doorway, tok["orch-1"], "MATERIAL_SEALED", {
        "material_id": f"source-manifest sha256:"
                       f"{manifest_hash}",
        "boundary": ["crew-1"]})
    for entry in manifest["sources"]:
        _act(doorway, tok["orch-1"], "MATERIAL_SEALED", {
            "material_id": f"{entry['path']} "
                           f"sha256:{entry['sha256']}",
            "boundary": ["crew-1"]})

    # 3. ISSUE through the real office route, then VERIFY
    # before activation (the examiner's emphasis): the
    # issued case must identify the manifest by hash in its
    # evidence boundary and carry the scoped bounds, and the
    # staged files must still hash to the manifest.
    issued = office.issue_new(tok["orch-1"], "crew-1")
    if not issued.get("ok"):
        print(f"ABORT: case issue failed: "
              f"{issued.get('problems')}", file=sys.stderr)
        return 1
    _act(doorway, tok["exam-1"], "CASE_JUDGED",
         {"case_id": issued["case_id"],
          "version": issued["version"]})
    office.authorise(tok["orch-1"], issued["case_id"],
                     issued["version"])
    content, _version = established_case_content(
        doorway.state(), issued["case_id"])
    boundary = (content or {}).get("evidence_boundary") or []
    if not any(manifest_hash in str(item) for item in boundary):
        print("ABORT: the issued case's evidence boundary "
              "does not identify the source manifest hash",
              file=sys.stderr)
        return 1
    if (content or {}).get("loop_bounds") != BOUNDS:
        print(f"ABORT: the issued case's loop_bounds are "
              f"{(content or {}).get('loop_bounds')}, not the "
              f"scoped {BOUNDS}", file=sys.stderr)
        return 1
    staged_problem = _staged_source_problem(manifest,
                                            sandbox)
    if staged_problem is not None:
        print(f"ABORT: {staged_problem}", file=sys.stderr)
        return 1
    print("pre-activation verification: manifest hash in the "
          "issued case's evidence boundary; bounds as scoped; "
          "staged sources hash to the manifest")
    if retrieval:
        # The retrieval mode's additions (INDEX 257,
        # blocker 2): the case itself must instruct the
        # deliverable's exact path, and the configured
        # grants must be able to receive it — verified here,
        # before assembly, and again against the sealed
        # record after generation (below).
        case_assignment = (content or {}).get(
            "assignment") or ""
        if BRIEF_SANDBOX_PATH not in case_assignment:
            print("ABORT: the issued case's assignment does "
                  f"not name {BRIEF_SANDBOX_PATH}: "
                  f"{case_assignment!r}", file=sys.stderr)
            return 1
        grant_problem = _write_grant_problem(GRANTS_RETRIEVAL)
        if grant_problem is not None:
            print(f"ABORT: {grant_problem}", file=sys.stderr)
            return 1
        print("pre-activation verification (retrieval "
              "mode): the issued case's assignment names "
              f"{BRIEF_SANDBOX_PATH}; the configured write "
              "grant's scope covers it")

    # The adapter and its connector transport (see
    # _build_adapter): the sanctioned credential route,
    # never the environment-variable key route.
    adapter = _build_adapter(route)

    # 4. ASSEMBLE — the full A1 lifecycle. identify() is the
    # adapter's own identity call; skills are honestly empty
    # (governed skill use is A4's, unbuilt). The executor is
    # constructed BEFORE activation, over the staged sandbox.
    gen.propose(tok["orch-1"], "crew-1", part="part-A",
                role_requirements="a model able to read three "
                                  "source documents and write "
                                  "a short, accurate, "
                                  "plain-words brief")
    identify_callable = adapter.identify
    if route == "groq":
        identify_callable = make_pinned_identify(
            adapter, GROQ_MODEL_PIN)
    try:
        generated = gen.generate(
            tok["orch-1"], "crew-1", identify_callable,
            skills=[],
            grants=GRANTS_RETRIEVAL if retrieval else GRANTS,
            model_requested=adapter.model,
            retrieval=retrieval, probe=probed)
    except ModelPinMismatchError as mismatch:
        # The pre-activation stop (INDEX 230, correction 2):
        # record the abort and its reason, export the record
        # as it stands (no activation event in it), and exit
        # non-zero. No activation, no worker call.
        events_now = store.all_events()
        export_store(store_path,
                     os.path.join(run_dir, "run-export.json"))
        abort_report = {
            "kind": "first generated-worker run harness "
                    "abort (derived matter, not record)",
            "run_id": RUN_ID,
            "worker_route": route,
            "model_pinned": GROQ_MODEL_PIN,
            "model_requested": adapter.model,
            "manifest_hash": manifest_hash,
            "aborted": True,
            "abort_stage": "pre-activation identity pin",
            "abort_reason": str(mismatch),
            "provider_model_id": mismatch.provider_model_id,
            "pinned_model": mismatch.pinned_model,
            "activation_performed": any(
                e["type"] == "INSTANCE_ACTIVATED"
                for e in events_now),
            "event_count": len(events_now),
        }
        with open(os.path.join(run_dir, "report.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(abort_report, fh, indent=1)
        print(f"ABORT: model identity pin mismatch: "
              f"{mismatch}; the run stops before activation",
              file=sys.stderr)
        return 1
    except AdapterFailure as failure:
        print(f"ABORT: the identity call failed "
              f"({failure.kind}: {failure.detail}); the "
              f"run's calls travel the registered connector "
              f"credential route — check the connector "
              f"helper and its credential", file=sys.stderr)
        return 1
    if not generated.get("ok"):
        print(f"ABORT: generation failed: "
              f"{generated.get('problems')}", file=sys.stderr)
        return 1
    assembly_id = generated["assembly_id"]
    instance_id = generated["instance_id"]
    if retrieval:
        # The sealed record itself, still before activation:
        # it must declare the retrieval contract, and a
        # sealed write grant's scope must cover the
        # deliverable's path (INDEX 257, blocker 2).
        sealed = doorway._generated_payload(assembly_id) or {}
        if sealed.get("catalogue_contract") != \
                tool_policy.RETRIEVAL_CATALOGUE_CONTRACT:
            print("ABORT: the sealed assembly record does "
                  "not declare the retrieval contract: "
                  f"{sealed.get('catalogue_contract')!r}",
                  file=sys.stderr)
            return 1
        grant_problem = _write_grant_problem(
            sealed.get("grants"))
        if grant_problem is not None:
            print(f"ABORT: the sealed grants cannot receive "
                  f"the deliverable: {grant_problem}",
                  file=sys.stderr)
            return 1
    probe_result = None
    if probed:
        # The probe stage (probe scope §2): five bounded
        # trials against the pinned model, captured below
        # interpretation over the Groq connector
        # transport's raw call — the adapter's own
        # probe_raw_call rides its built-in transport and
        # cannot travel this route (see
        # groq_connector_transport.py). The stage records
        # ASSEMBLY_PROBED between generation and
        # verification, binding its evidence to the exact
        # generated record; nothing it captures is
        # dispatched or executed, and no tool results are
        # sent back.
        raw_call = install_groq_connector_raw_call(
            adapter,
            os.environ.get("GROQ_HELPER_PATH",
                           GROQ_CONNECTOR_HELPER),
            adapter.model)
        probe_result = gen.probe(
            tok["orch-1"], assembly_id, raw_call,
            route="groq", model=GROQ_MODEL_PIN)
    gen.verify(tok["orch-1"], assembly_id)
    if phase1:
        # Phase 1 stops here — before judgement, whose
        # mode and grounds are the examiner's, supplied in
        # phase 2. The record as it stands is exported and
        # the probe evidence written beside it.
        return _finish_probe_phase1(
            store, store_path, run_dir, doorway,
            assembly_id, instance_id, generated,
            probe_result)
    return _judge_pack_run(
        doorway, gen, tok, store, store_path, run_dir,
        sandbox, route, retrieval, adapter, manifest,
        manifest_hash, assembly_id, instance_id,
        gen.judgement(assembly_id), None)


def _filed_artifact_check(run_dir, iteration_seq,
                          disposition_payload):
    """Cross-check one captured disposition against the
    artifact filed under the run directory (INDEX 322):
    the file the store contract names —
    responses/iteration-<iteration_seq>.json — must
    stand, its bytes must hash to the artifact hash the
    disposition committed, and its own L1 statement must
    agree with the L1 summary the disposition committed.
    Returns "ok", or a plain statement of the
    disagreement: the summary reports the evidence as it
    stands, never smoothed over."""
    path = os.path.join(run_dir, "responses",
                        f"iteration-{iteration_seq}.json")
    if not os.path.exists(path):
        return (f"the artifact the disposition names "
                f"does not stand at {path}")
    with open(path, "rb") as fh:
        data = fh.read()
    if _sha256_bytes(data) != \
            disposition_payload.get("artifact_sha256"):
        return ("the filed artifact's sha256 is not the "
                "artifact hash the disposition committed")
    try:
        artifact = json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return "the filed artifact is not readable JSON"
    filed_l1 = ((artifact.get("layers") or {})
                .get("L1") or {})
    committed_l1 = ((disposition_payload.get("layers")
                     or {}).get("L1") or {})
    for key in ("byte_count", "sha256", "stop_reason",
                "body_complete"):
        if filed_l1.get(key) != committed_l1.get(key):
            return (f"the filed artifact's L1 {key} "
                    f"({filed_l1.get(key)!r}) disagrees "
                    f"with the committed summary "
                    f"({committed_l1.get(key)!r})")
    return "ok"


def _evidence_summary(events, run_dir):
    """The report's evidence summary (evidenced-run
    release examination, INDEX 322): one entry per
    entered iteration, derived from the record's
    committed events — the CALL_ENTERED boundaries and
    the RESPONSE_EVIDENCE dispositions that answer
    them — cross-checked against the artifacts filed
    under run_dir/responses/. Derived matter: an index
    into the evidence, never a replacement for it. A
    captured entry carries the artifact's identity as
    committed (its hash, the L1 byte count, stop_reason,
    body_complete) and the filed artifact's cross-check;
    a no_response or unresolved entry carries its
    failure class and no artifact fields, because no
    artifact stands for it; an entered iteration with
    no disposition — the evidence-capture-failure
    terminal's case — is stated as exactly that."""
    dispositions = {}
    capture_failures = {}
    for e in events:
        if e["type"] == "RESPONSE_EVIDENCE":
            dispositions[e["payload"].get(
                "iteration_seq")] = e
        elif e["type"] == "EVIDENCE_CAPTURE_FAILED":
            capture_failures[e["payload"].get(
                "iteration_seq")] = e
    summary = []
    for e in events:
        if e["type"] != "CALL_ENTERED":
            continue
        payload = e["payload"]
        iteration_seq = payload.get("iteration_seq")
        entry = {"iteration": payload.get("iteration"),
                 "iteration_seq": iteration_seq,
                 "call_entered_seq": e["event_seq"]}
        disp = dispositions.get(iteration_seq)
        if disp is None:
            entry["disposition"] = None
            failed = capture_failures.get(iteration_seq)
            if failed is not None:
                entry["disposition_note"] = (
                    "no disposition stands; the "
                    "evidence capture failure terminal "
                    "answers this iteration, and the "
                    "disposition obligation stands "
                    "undischarged")
                entry["evidence_capture_failed"] = {
                    "operation": failed["payload"].get(
                        "operation"),
                    "event_seq": failed["event_seq"]}
            else:
                entry["disposition_note"] = (
                    "no disposition stands for this "
                    "entered iteration")
            summary.append(entry)
            continue
        dp = disp["payload"]
        entry["disposition"] = dp.get("outcome")
        entry["disposition_seq"] = disp["event_seq"]
        if dp.get("failure_class") is not None:
            entry["failure_class"] = dp["failure_class"]
        if dp.get("outcome") == "captured":
            l1 = (dp.get("layers") or {}).get("L1") or {}
            entry["artifact_sha256"] = dp.get(
                "artifact_sha256")
            entry["l1_byte_count"] = l1.get("byte_count")
            entry["stop_reason"] = l1.get("stop_reason")
            entry["body_complete"] = l1.get(
                "body_complete")
            entry["artifact_check"] = \
                _filed_artifact_check(run_dir,
                                      iteration_seq, dp)
        summary.append(entry)
    return summary


def _judge_pack_run(doorway, gen, tok, store, store_path,
                    run_dir, sandbox, route, retrieval,
                    adapter, manifest, manifest_hash,
                    assembly_id, instance_id,
                    judgement_payload, extra_report,
                    pace_iterations=False):
    """The lifecycle from the examiner's judgement onward,
    exactly as the run modes have always carried it:
    judgement, pack, issue authorisation, the executor
    constructed before activation, activation, the bounded
    loop, and the report. Under the probe regime the
    judgement payload is the caller's — computed by
    gen.judgement with the examiner's mode and grounds —
    and the loop reads the mode from the packed act
    itself, so nothing here selects or overrides it."""
    _act(doorway, tok["exam-1"], "ASSEMBLY_JUDGED",
         judgement_payload)
    packed = gen.pack(tok["orch-1"], assembly_id)
    gen.authorise(tok["orch-1"], assembly_id)
    executor = Executor(doorway, sandbox,
                        claim_dir=os.path.join(run_dir,
                                               "claims"))
    gen.activate(tok["orch-1"], assembly_id)
    instance_token = packed["instance_token"]

    # 5. RUN — the bounded loop, the real model driving.
    # The response-evidence piece: the loop runs under the
    # evidence regime, its store rooted at the run
    # directory (artifacts in run_dir/responses/). Under
    # the demonstration's phase-2 release the loop's model
    # is the adapter paced at the call-start boundary
    # (INDEX 412, phase-2 matter 1); every other run mode
    # hands the loop the adapter exactly as it always has.
    model = IterationPacer(adapter) if pace_iterations \
        else adapter
    result = Loop(doorway, instance_token, model,
                  executor=executor,
                  evidence_store=run_dir).run()

    # 6. REPORT — derived matter, labelled as such; the
    # checker finding and any accuracy judgement are
    # separate findings, and only the checker's is recorded
    # here (accuracy is the examiner's, afterwards).
    events = store.all_events()
    stalls = [e for e in events if e["type"] == "LOOP_STALLED"]
    outcomes = {}
    for e in events:
        if e["type"] == "TOOL_OUTCOME":
            outcomes[e["payload"].get("dispatch_id")] = \
                e["payload"].get("outcome")
    dispatches = [
        {"dispatch_id": e["payload"].get("dispatch_id"),
         "tool": e["payload"].get("tool"),
         "request_id": e["payload"].get("request_id"),
         "outcome": outcomes.get(e["payload"].get(
             "dispatch_id"))}
        for e in events if e["type"] == "TOOL_DISPATCHED"]
    brief_rel = BRIEF_SANDBOX_PATH if retrieval else "brief.md"
    brief_path = os.path.join(sandbox, *brief_rel.split("/"))
    brief_exists = os.path.exists(brief_path)
    brief_words = None
    if brief_exists:
        with open(brief_path, encoding="utf-8") as fh:
            brief_words = len(fh.read().split())
        shutil.copyfile(brief_path,
                        os.path.join(run_dir, "brief.md"))
    identity = instance_onboarding_record(doorway,
                                          instance_id) or {}
    verdict = run_checker(store)
    export_store(store_path,
                 os.path.join(run_dir, "run-export.json"))
    report = {
        "kind": "first generated-worker run harness report "
                "(derived matter, not record)",
        "run_id": RUN_ID,
        "scope": "FIRST-WORKER-RUN-SCOPE-2026-11-23.md Rev 2",
        "worker_route": route,
        "retrieval_mode": retrieval,
        "brief_sandbox_path": brief_rel,
        "model_pinned": (GROQ_MODEL_PIN if route == "groq"
                         else None),
        "model_requested": adapter.model,
        "manifest_hash": manifest_hash,
        "manifest": manifest,
        "loop_result": result,
        "iterations": result.get("iterations"),
        "call_timings": result.get("call_timings") or [],
        "call_timings_note":
            "per-iteration stage timings measured directly "
            "by the loop, the adapter and the connector "
            "transport (INDEX 217/219): package construction, "
            "prompt rendering, and the transport's stages, "
            "with stages the interface cannot separate "
            "labelled as such and unmeasured stages null. "
            "Local cancellation of a helper process never "
            "proves the upstream provider stopped processing "
            "its request.",
        "stall": ({"ground": stalls[0]["payload"].get(
                       "ground"),
                   "event_seq": stalls[0]["event_seq"]}
                  if stalls else None),
        "evidence_summary": _evidence_summary(events,
                                              run_dir),
        "dispatches": dispatches,
        "brief_exists": brief_exists,
        "brief_word_count": brief_words,
        "identity_evidence": {
            "declaration": identity.get("declaration"),
            "provider_model_id":
                identity.get("provider_model_id"),
            "identity_status":
                identity.get("identity_status"),
            "note": "declaration and provider-reported id as "
                    "recorded at the instance's onboarding; "
                    "neither is independent proof of the "
                    "model the provider actually served"},
        "event_count": len(events),
        "checker": verdict.get("checks"),
    }
    if extra_report:
        report.update(extra_report)
    report_path = os.path.join(run_dir, "report.json")
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1)
    print(f"outcome: {result.get('outcome')} "
          f"(ok={result.get('ok')}), iterations: "
          f"{result.get('iterations')}, dispatches: "
          f"{len(dispatches)}, brief: "
          f"{'written, ' + str(brief_words) + ' words'
             if brief_exists else 'not written'}")
    print(f"report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
