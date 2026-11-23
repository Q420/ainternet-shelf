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
ADAPTER_TIMEOUT (default 120). The adapter's transport,
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from framework import projection  # noqa: E402
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
                              FrameworkStore)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from connector_transport import (  # noqa: E402
    install_connector_transport)
from groq_connector_transport import (  # noqa: E402
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


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # Route selection first, before any staging or assembly
    # work (INDEX 230, correction 3): an invalid value
    # refuses outright and nothing is staged.
    try:
        route = resolve_worker_route(
            os.environ.get("WORKER_ROUTE"))
    except ValueError as exc:
        print(f"ABORT: {exc}", file=sys.stderr)
        return 2
    name = "first-worker" + (f"-{argv[0]}" if argv else "")
    run_dir = os.path.join(ROOT, "live-demo", name)
    store_path = os.path.join(run_dir, "run.db")
    if os.path.exists(store_path):
        print(f"refusing to overwrite the existing run store "
              f"at {store_path}; rerun with a suffix argument "
              f"for a fresh directory", file=sys.stderr)
        return 1
    os.makedirs(run_dir, exist_ok=True)
    sandbox = os.path.join(run_dir, "sandbox")

    # 1. STAGE — sources fixed by manifest before anything
    # is commissioned.
    manifest, manifest_hash = stage(run_dir)
    print(f"manifest sha256: {manifest_hash}")

    # 2. COMMISSION — one part, four seats, the crew brief
    # carrying the assignment, the bounds, and (as recorded
    # brief matter) the evidence boundary naming the
    # manifest hash and the three source paths.
    store = FrameworkStore(store_path)
    store.insert_run(RUN_ID, CONSTITUTION_HASH)
    brief = {
        "part": "part-A",
        "assignment": ASSIGNMENT,
        "verification_list": list(VERIFICATION_LIST),
        "evidence_boundary":
            f"source manifest sha256:{manifest_hash}; "
            "sources: sources/stock-take.md, "
            "sources/a3-pass.md, sources/index-tail.md",
        "loop_bounds": dict(BOUNDS),
    }
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
    for entry in manifest["sources"]:
        staged = os.path.join(sandbox, entry["path"])
        if _sha256_file(staged) != entry["sha256"]:
            print(f"ABORT: staged {entry['path']} no longer "
                  f"hashes to the manifest", file=sys.stderr)
            return 1
    print("pre-activation verification: manifest hash in the "
          "issued case's evidence boundary; bounds as scoped; "
          "staged sources hash to the manifest")

    # The adapter, configured as the Piece 8 live harness
    # configures it (endpoint / model / timeout from the
    # environment), with its transport then carried through
    # the registered connector helper (INDEX 191/192): the
    # environment-variable key route is not used by this
    # harness — attempt 1 was rejected on it before
    # activation — and the connector credential in the
    # Secure Vault is the sanctioned route. The adapter's
    # contract, strict validation, outcome typing and
    # deadline behaviour are unchanged; only _call's
    # transport is replaced, under the examiner's
    # cancellation boundary (connector_transport.py).
    if route == "groq":
        # The Groq route: the model is PINNED (the pin
        # overrides ADAPTER_MODEL for the run) and the
        # transport is the Groq twin, through the Groq
        # connector helper (GROQ_HELPER_PATH overridable
        # for witnesses).
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
    else:
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
            skills=[], grants=GRANTS,
            model_requested=adapter.model)
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
    gen.verify(tok["orch-1"], assembly_id)
    _act(doorway, tok["exam-1"], "ASSEMBLY_JUDGED",
         gen.judgement(assembly_id))
    packed = gen.pack(tok["orch-1"], assembly_id)
    gen.authorise(tok["orch-1"], assembly_id)
    executor = Executor(doorway, sandbox,
                        claim_dir=os.path.join(run_dir,
                                               "claims"))
    gen.activate(tok["orch-1"], assembly_id)
    instance_token = packed["instance_token"]

    # 5. RUN — the bounded loop, the real model driving.
    result = Loop(doorway, instance_token, adapter,
                  executor=executor).run()

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
    brief_path = os.path.join(sandbox, "brief.md")
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
