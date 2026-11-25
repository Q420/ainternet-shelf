#!/usr/bin/env python3
"""The combined configuration — the pull enablement's
OFFLINE rehearsal (INDEX 476).

Ben's direction (2026-11-24 ~18:48 MST): "we haven't
actually enabled him to pull the information that he
needs. That's our next step. Then we can have a full
run." The combined configuration widens the
demonstration assembly's grants from the execution
tool only to the combined surface — container.exec,
the retrieval four (sandbox.list, sandbox.search,
sandbox.read_range, sandbox.read) under sources/ and
under scratch/, and sandbox.write under scratch/ —
and this rehearsal proves that configuration offline
before the full run: a deterministic scripted stand-in
drives the REAL loop, the REAL native adapter (with
the NVIDIA route's name translation), the REAL
doorway and the REAL rig, through a stub at the REAL
NVIDIA connector seam — the gate 4 rehearsal's pattern,
a sibling driver so the gate 4 witness stands
unchanged. No provider is contacted, no credential is
spent, and nothing here is a live run.

The configuration rehearsed is the live driver's own:
the grants, the assignment and the glossary are
imported from demo_run — the very objects the full
run will seal and carry — so what is proven here is
the run's configuration, not a rehearsal-only copy of
it.

The stand-in's sequence:
  (1) a PULL — sandbox.read of sources/stock-take.md
      through the doorway, returning the shelf content
      itself (its hash is the manifest's);
  (2) an exec read of sources/a3-pass.md in the room —
      the same glossary address through the other door;
  (3) the utilise-only witness (Ben's refinement,
      2026-11-24: "access doesnt mean overwrite. it
      means utlilize") — an exec attempt to OVERWRITE
      the stocked sources/stock-take.md inside the
      room; the source's SHA-256 is taken again after
      the attempt and the record states whether the
      briefcase's stock held, and by what mechanism —
      or, if it did not hold, carries that plainly as
      an open item for the examiner;
  (4) the brief written via sandbox.write to
      scratch/brief.md and collected from the
      framework sandbox — the write path that does not
      depend on his exec dialect;
  (5) an out-of-grants reach — sandbox.write under
      sources/ — refused at the doorway (no write
      grant touches sources/);
  (6) the yield.

The glossary chain (Ben's briefcase design,
2026-11-16): the case carries the glossary as its own
component; the wake package (captured at the seam)
shows it standing inside the case; and every pull the
stand-in makes cites the glossary entry it answers to
in the report's pull evidence — glossary → pull
request → shelf content, each link witnessed.

The room's lifetime is single-process, as in gate 4:
this process stocks the room via stock_demo, holds it
for the whole rehearsal, snapshots its state, and
destroys it at the end. The mode judgement is
rehearsal furniture (a scripted stand-in examiner's
receipt), exactly as in gate 4.

Outputs land in the rehearsal work directory: the run
record, the stub's captures, the decision receipt, the
stocking record, the room's final state, the terminal
readout, the collected brief, and report.json.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "src"
RIG = ROOT / "room" / "rig"
for _p in (str(SRC), str(HERE), str(RIG)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fabric.canonical import canonical  # noqa: E402

from framework.adapter import (  # noqa: E402
    OpenAICompatibleAdapter)
from framework.doorway import (  # noqa: E402
    Doorway, established_case_content)
from framework.executor import Executor  # noqa: E402
from framework.generator import Generator  # noqa: E402
from framework.loop import Loop  # noqa: E402
from framework.office import Office  # noqa: E402
from framework.record import (  # noqa: E402
    CONSTITUTION_HASH, FrameworkStore)

from connector_transport import (  # noqa: E402
    install_connector_transport)
from nvidia_connector_transport import (  # noqa: E402
    install_nvidia_connector_raw_call)
from first_worker_run import (  # noqa: E402
    BOUNDS, RUN_ID, _act, _commission_brief, export_store,
    run_checker)
from demo_run import (  # noqa: E402
    ASSIGNMENT_COMBINED, GLOSSARY, GRANTS_COMBINED, MODEL,
    _stage_sandbox_sources)
from gate4_rehearsal import BRIEF_TEXT  # noqa: E402

import room as room_mod  # noqa: E402
import stock_demo  # noqa: E402

ENDPOINT = ("https://integrate.api.nvidia.com/v1/chat/"
            "completions")
ROUTE = "nvidia"

# The utilise-only witness's attempt: overwrite the
# stocked stock-take inside the room, from the worker's
# working directory, at the glossary's own address.
OVERWRITE_CMD = [
    "/bin/sh", "-c",
    "echo OVERWRITTEN-BY-THE-WORKER > sources/stock-take.md"]
OVERWRITE_TARGET = "sources/stock-take.md"


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _native_call(call_id, name, arguments):
    """One scripted provider response carrying a single
    native tool call — the gate 4 rehearsal's shape."""
    return {
        "id": f"stub-{call_id}",
        "model": MODEL,
        "choices": [{
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": call_id,
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": json.dumps(arguments),
                    },
                }],
            },
            "finish_reason": "tool_calls",
        }],
    }


def _text_response(call_id, content):
    return {
        "id": f"stub-{call_id}",
        "model": MODEL,
        "choices": [{
            "message": {"role": "assistant",
                        "content": content},
            "finish_reason": "stop",
        }],
    }


def build_stub_script():
    """The stand-in's script: five probe trials settling
    native, then the chat sequence — identify, the six
    rehearsal iterations in order. The stand-in answers
    in the names the route's provider would emit: the
    wire (dash) forms of the offered tools, which the
    route's translation carries back to the framework's
    canonical names."""
    probe_step = {
        "respond": _native_call(
            "fc-probe", "probe-lookup",
            {"object": "brass lantern"}),
        "action": None}
    chat = [
        # 0 — the identity call (generation's onboarding).
        {"respond": _text_response(
            "identify",
            f"I am {MODEL}, a model served on the "
            "NVIDIA route. (Scripted stand-in "
            "declaration for the combined-configuration "
            "offline rehearsal; no provider was "
            "contacted.)"),
         "action": None},
        # 1 — (1) the pull: sandbox.read of the first
        # glossary entry's address, through the doorway.
        {"respond": _native_call(
            "fc-cx-1", "sandbox-read",
            {"path": "sources/stock-take.md"}),
         "action": None},
        # 2 — (2) the same briefcase through the other
        # door: an in-room exec read of the second
        # glossary entry's address.
        {"respond": _native_call(
            "fc-cx-2", "container-exec",
            {"cmd": ["/bin/cat", "sources/a3-pass.md"]}),
         "action": None},
        # 3 — (3) the utilise-only witness: an exec
        # attempt to overwrite the stocked stock-take
        # inside the room.
        {"respond": _native_call(
            "fc-cx-3", "container-exec",
            {"cmd": OVERWRITE_CMD}),
         "action": None},
        # 4 — (4) the brief via the doorway write path.
        {"respond": _native_call(
            "fc-cx-4", "sandbox-write",
            {"path": "scratch/brief.md",
             "content": BRIEF_TEXT}),
         "action": None},
        # 5 — (5) the out-of-grants reach: a write under
        # sources/, where no grant reaches — refused at
        # the doorway.
        {"respond": _native_call(
            "fc-cx-5", "sandbox-write",
            {"path": "sources/brief.md",
             "content": "this write must be refused: "
                        "no grant covers writing under "
                        "sources/"}),
         "action": None},
        # 6 — the yield.
        {"respond": _text_response(
            "yield",
            json.dumps({
                "outcome": "yield",
                "summary": "Pulled the stock-take through "
                           "the doorway, read the A3 pass "
                           "in-room, attempted the "
                           "stocked source's overwrite, "
                           "wrote the brief via "
                           "sandbox.write, and met the "
                           "doorway's refusal on the "
                           "sources/ write."})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": [dict(probe_step)
                                 for _ in range(5)]}


STUB_SOURCE = '''#!/usr/bin/env python3
"""The combined rehearsal's stub helper: stands in for
the NVIDIA connector helper at its own seam. Invoked
exactly as the real helper is — [python, helper,
"chat"|"chat-raw-bounded", model], the request JSON on
stdin — it records the exact request bytes to the
captures file and answers from the script: the provider
JSON itself for "chat"; for "chat-raw-bounded", the
bounded envelope the real helper frames, wrapping the
same provider JSON. No network, no credential, no
provider."""
import base64
import hashlib
import json
import os
import sys


def main():
    mode = sys.argv[1]
    model = sys.argv[2]
    body = sys.stdin.buffer.read()
    with open(os.environ["COMBINED_STUB_SCRIPT"],
              encoding="utf-8") as fh:
        script = json.load(fh)
    state_path = os.environ["COMBINED_STUB_STATE"]
    try:
        with open(state_path, encoding="utf-8") as fh:
            state = json.load(fh)
    except (OSError, ValueError):
        state = {}
    index = int(state.get(mode, 0))
    state[mode] = index + 1
    with open(state_path, "w", encoding="utf-8") as fh:
        json.dump(state, fh)
    with open(os.environ["COMBINED_STUB_CAPTURES"], "a",
              encoding="utf-8") as fh:
        fh.write(json.dumps({
            "mode": mode, "model": model, "index": index,
            "request_sha256": hashlib.sha256(body).hexdigest(),
            "request_bytes": len(body),
            "request_b64": base64.b64encode(body).decode(
                "ascii")}) + "\\n")
    steps = script.get(mode) or []
    if index >= len(steps):
        sys.stderr.write(
            f"combined stub: script exhausted for mode "
            f"{mode} at index {index}\\n")
        return 3
    payload = json.dumps(
        steps[index]["respond"]).encode("utf-8")
    if mode == "chat-raw-bounded":
        envelope = {
            "phase": "response_received", "status": 200,
            "body_b64": base64.b64encode(payload).decode(
                "ascii"),
            "body_complete": True, "stop_reason": "eof",
            "error_kind": None, "read_error_kind": None}
        sys.stdout.write(json.dumps(envelope))
    else:
        sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _package_from_capture(capture):
    """The loop package a captured chat request carried:
    the native rendering frames the package JSON in a
    prose preamble ("Your wake package:") and carries
    the tools as the request's own parameter rather
    than in the package, so the package is the one JSON
    object embedded in a message that carries both
    "case" and "tool_results", or None."""
    body = json.loads(base64.b64decode(
        capture["request_b64"]))
    decoder = json.JSONDecoder()
    for message in body.get("messages") or []:
        content = message.get("content")
        if not isinstance(content, str):
            continue
        for start in range(len(content)):
            if content[start] != "{":
                continue
            try:
                parsed, _end = decoder.raw_decode(
                    content[start:])
            except ValueError:
                continue
            if isinstance(parsed, dict) and \
                    "case" in parsed and \
                    "tool_results" in parsed:
                return parsed
    return None


def run_rehearsal(work_dir):
    """Run the whole combined-configuration rehearsal in
    `work_dir` (created fresh; must not already hold a
    rehearsal). Returns the report dict (also written to
    work_dir/report.json). The room is destroyed before
    this returns, on every path."""
    work_dir = Path(work_dir).resolve()
    if work_dir.exists() and any(work_dir.iterdir()):
        raise RuntimeError(
            f"rehearsal work directory {work_dir} is not "
            f"empty; refusing to overwrite a standing "
            f"rehearsal")
    run_dir = work_dir / "run"
    rooms_base = work_dir / "rooms"
    run_dir.mkdir(parents=True, exist_ok=True)
    rooms_base.mkdir(parents=True, exist_ok=True)

    stub_path = work_dir / "stub_helper.py"
    stub_path.write_text(STUB_SOURCE, encoding="utf-8")
    stub_path.chmod(0o755)
    script_path = work_dir / "stub_script.json"
    script_path.write_text(
        json.dumps(build_stub_script(), indent=1),
        encoding="utf-8")
    state_path = work_dir / "stub_state.json"
    state_path.write_text("{}", encoding="utf-8")
    captures_path = work_dir / "captures.jsonl"
    captures_path.write_text("", encoding="utf-8")
    os.environ["COMBINED_STUB_SCRIPT"] = str(script_path)
    os.environ["COMBINED_STUB_STATE"] = str(state_path)
    os.environ["COMBINED_STUB_CAPTURES"] = str(captures_path)

    room = None
    try:
        # STOCK (hop 2) — the paper §1 stocking, verified
        # by its smoke set; the room is then held in THIS
        # process for the whole rehearsal.
        stocking = stock_demo.stock_demo_room(
            rooms_base, "demo")
        room = room_mod.load_room(rooms_base, "demo")
        manifest = stocking["source_manifest"]
        manifest_hash = manifest["manifest_sha256"]
        manifest_sha = {e["path"]: e["sha256"]
                        for e in manifest["sources"]}

        # COMMISSION — the combined assignment, the
        # stocking manifest as the sealed source set, and
        # the case's glossary: the office must carry the
        # brief's glossary into the issued case unchanged.
        store_path = str(run_dir / "run.db")
        store = FrameworkStore(store_path)
        store.insert_run(RUN_ID, CONSTITUTION_HASH)
        brief = _commission_brief(
            ASSIGNMENT_COMBINED, manifest_hash,
            glossary=GLOSSARY)
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
               for s in ("orch-1", "exam-1", "dir-1",
                         "crew-1")}
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
        if not issued.get("ok"):
            raise RuntimeError(
                f"case issue failed: {issued.get('problems')}")
        _act(doorway, tok["exam-1"], "CASE_JUDGED",
             {"case_id": issued["case_id"],
              "version": issued["version"]})
        office.authorise(tok["orch-1"], issued["case_id"],
                         issued["version"])
        content, _version = established_case_content(
            doorway.state(), issued["case_id"])
        boundary = (content or {}).get(
            "evidence_boundary") or []
        if not any(manifest_hash in str(item)
                   for item in boundary):
            raise RuntimeError(
                "the issued case's evidence boundary does "
                "not identify the source manifest hash")
        if (content or {}).get("loop_bounds") != BOUNDS:
            raise RuntimeError(
                "the issued case's loop_bounds are not the "
                "scoped bounds")
        case_glossary = (content or {}).get("glossary")
        if case_glossary != GLOSSARY:
            raise RuntimeError(
                "the issued case does not carry the "
                "commissioned glossary as its own "
                "component")

        # STAGE THE PULL DOOR — the executor sandbox's
        # sources at the glossary's addresses, each
        # hash-verified against the manifest (the live
        # driver's own staging).
        staging_problem = _stage_sandbox_sources(
            run_dir / "sandbox", manifest)
        if staging_problem is not None:
            raise RuntimeError(
                f"sandbox staging failed: "
                f"{staging_problem}")

        # ASSEMBLE — the adapter on the NVIDIA route's
        # seam, its transport the stub helper; generation
        # under the probe contract and the exec catalogue
        # contract, grants the combined set.
        adapter = OpenAICompatibleAdapter(
            endpoint=ENDPOINT, model=MODEL, timeout=300.0,
            route=ROUTE)
        install_connector_transport(
            adapter, str(stub_path), MODEL)
        gen.propose(
            tok["orch-1"], "crew-1", part="part-A",
            role_requirements="a model able to read three "
                              "source documents — in its "
                              "room and by pulling them "
                              "through the doorway — and "
                              "write a short, accurate, "
                              "plain-words brief")
        generated = gen.generate(
            tok["orch-1"], "crew-1", adapter.identify,
            skills=[], grants=GRANTS_COMBINED,
            model_requested=MODEL, probe=True,
            exec_room=True)
        if not generated.get("ok"):
            raise RuntimeError(
                f"generation failed: "
                f"{generated.get('problems')}")
        assembly_id = generated["assembly_id"]
        sealed = None
        for ev in store.all_events():
            if ev["type"] == "ASSEMBLY_GENERATED" and \
                    ev["payload"].get(
                        "assembly_id") == assembly_id:
                sealed = ev["payload"]

        # PROBE — five scripted trials through the real
        # NVIDIA raw-call seam over the stub.
        raw_call = install_nvidia_connector_raw_call(
            helper_path=str(stub_path), model=MODEL)
        probe_result = gen.probe(
            tok["orch-1"], assembly_id, raw_call,
            route=ROUTE, model=MODEL)
        gen.verify(tok["orch-1"], assembly_id)

        # JUDGE (hop 1) — the rehearsal's decision
        # receipt, retained before the judgement is
        # recorded; the judgement binds its canonical
        # hash, as the live phases bind the examiner's.
        probed_payload = None
        for ev in store.all_events():
            if ev["type"] == "ASSEMBLY_PROBED" and \
                    ev["payload"].get(
                        "assembly_id") == assembly_id:
                probed_payload = ev["payload"]
        receipt = {
            "run_id": RUN_ID,
            "assembly_id": assembly_id,
            "generated_record_hash":
                probed_payload["generated_record_hash"],
            "probed_seq": probe_result["probed_seq"],
            "probe_evidence_hash":
                probe_result["evidence_hash"],
            "fingerprint": probed_payload["fingerprint"],
            "adapter_mode": "native",
            "mode_grounds":
                "Combined-configuration offline "
                "rehearsal: the scripted stand-in's probe "
                "trials settled 5/5 native (probe.lookup), "
                "and the demonstration preparation paper "
                "§3.1 proposes native for the room "
                "configuration. This judgement is "
                "rehearsal furniture by a scripted "
                "stand-in examiner; the live run's mode "
                "judgement is the examiner's at the "
                "release gate.",
            "examiner": "combined-configuration rehearsal "
                        "(scripted stand-in examiner)",
            "decided_at": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        receipt_path = work_dir / "decision-receipt.json"
        with open(receipt_path, "w", encoding="utf-8") as fh:
            json.dump(receipt, fh, indent=1)
            fh.write("\n")
        receipt_hash = _sha256_bytes(canonical(receipt))
        judgement = gen.judgement(
            assembly_id, adapter_mode="native",
            mode_grounds=receipt["mode_grounds"],
            decision_receipt_hash=receipt_hash,
            decision_examiner=receipt["examiner"])
        _act(doorway, tok["exam-1"], "ASSEMBLY_JUDGED",
             judgement)
        packed = gen.pack(tok["orch-1"], assembly_id)
        gen.authorise(tok["orch-1"], assembly_id)

        # RUN — the executor holds the room and the
        # staged sandbox; the loop drives the real
        # adapter/doorway/rig path.
        executor = Executor(
            doorway, str(run_dir / "sandbox"),
            claim_dir=str(run_dir / "claims"),
            deadline=150.0, room=room,
            exec_timeout=stock_demo.PER_EXECUTION_WALL_S)
        gen.activate(tok["orch-1"], assembly_id)
        result = Loop(doorway, packed["instance_token"],
                      adapter, executor=executor,
                      evidence_store=str(run_dir)).run()

        # COLLECT — before teardown: both brief resting
        # places, the utilise-only witness's after-hash,
        # and the room's final state; then the checker,
        # the export, and the terminal readout.
        room_brief_path = room.tree / "scratch" / "brief.md"
        room_brief_sha256 = _sha256_bytes(
            room_brief_path.read_bytes()) \
            if room_brief_path.exists() else None
        fw_brief_path = run_dir / "sandbox" / "scratch" \
            / "brief.md"
        fw_brief_bytes = fw_brief_path.read_bytes() \
            if fw_brief_path.exists() else None
        fw_brief_sha256 = _sha256_bytes(fw_brief_bytes) \
            if fw_brief_bytes is not None else None
        if fw_brief_bytes is not None:
            (work_dir / "brief.md").write_bytes(
                fw_brief_bytes)
        room_stock_after_path = room.tree / "work" / \
            OVERWRITE_TARGET
        room_stock_after = _sha256_bytes(
            room_stock_after_path.read_bytes()) \
            if room_stock_after_path.exists() else None
        sandbox_stock_after_path = run_dir / "sandbox" / \
            OVERWRITE_TARGET
        sandbox_stock_after = _sha256_bytes(
            sandbox_stock_after_path.read_bytes()) \
            if sandbox_stock_after_path.exists() else None
        room_state = json.loads(room.state_path.read_text())
        (work_dir / "room-state.json").write_text(
            json.dumps(room_state, indent=1),
            encoding="utf-8")
        (work_dir / "stocking.json").write_text(
            json.dumps(stocking, indent=1),
            encoding="utf-8")
        events = store.all_events()
        verdict = run_checker(store)
        export_store(store_path,
                     str(run_dir / "run-export.json"))
        readout_path = work_dir / "terminal-readout.md"
        readout = subprocess.run(
            [sys.executable, str(HERE / "terminal_readout.py"),
             "render", str(run_dir / "run-export.json"),
             "-o", str(readout_path)],
            capture_output=True, text=True)

        # The evidence, derived from the record and the
        # captures — never from the script's intentions.
        outcomes = {}
        requests = {}
        for e in events:
            if e["type"] == "TOOL_OUTCOME":
                outcomes[e["payload"].get("dispatch_id")] \
                    = e["payload"]
            elif e["type"] == "TOOL_REQUESTED":
                requests[e["payload"].get("request_id")] \
                    = e["payload"]
        dispatches = []
        for e in events:
            if e["type"] != "TOOL_DISPATCHED":
                continue
            p = e["payload"]
            outcome = outcomes.get(p.get("dispatch_id"))
            dispatches.append({
                "dispatch_id": p.get("dispatch_id"),
                "tool": p.get("tool"),
                "registry_version":
                    p.get("registry_version"),
                "parameters": (requests.get(
                    p.get("request_id")) or {}).get(
                    "parameters"),
                "outcome": (outcome or {}).get("outcome"),
                "result": (outcome or {}).get("result"),
            })
        rejections = [
            {"tool": e["payload"].get("tool"),
             "ground": e["payload"].get("ground")}
            for e in events if e["type"] == "REJECTION"
            and e["payload"].get("attempted_type")
            == "TOOL_DISPATCHED"]

        def glossary_entry(address):
            for entry in GLOSSARY:
                if entry["address"] == address:
                    return entry
            return None

        pulls = []
        for d in dispatches:
            params = d["parameters"] or {}
            path = params.get("path")
            if d["tool"] in ("sandbox.list", "sandbox.search",
                             "sandbox.read_range",
                             "sandbox.read"):
                res = d["result"] or {}
                pulls.append({
                    "door": "doorway (pull)",
                    "tool": d["tool"],
                    "path": path,
                    "glossary_entry": glossary_entry(path)
                    if path else None,
                    "outcome": d["outcome"],
                    "content_sha256":
                        res.get("content_sha256"),
                    "authority_path":
                        res.get("authority_path"),
                    "shelf_sha256":
                        manifest_sha.get(path),
                })
            elif d["tool"] == "container.exec":
                cmd = params.get("cmd") or []
                target = None
                for token in cmd:
                    if token in manifest_sha:
                        target = token
                if target is not None and \
                        cmd != OVERWRITE_CMD:
                    res = d["result"] or {}
                    stdout = res.get("stdout")
                    pulls.append({
                        "door": "room (exec)",
                        "tool": d["tool"],
                        "path": target,
                        "glossary_entry":
                            glossary_entry(target),
                        "outcome": d["outcome"],
                        "stdout_sha256": _sha256_bytes(
                            stdout.encode("utf-8"))
                        if isinstance(stdout, str)
                        else None,
                        "shelf_sha256":
                            manifest_sha.get(target),
                    })

        # The utilise-only witness: the overwrite
        # dispatch's own outcome, and the stocked
        # source's hash in the room after the attempt.
        overwrite_dispatch = None
        for d in dispatches:
            if d["tool"] == "container.exec" and \
                    (d["parameters"] or {}).get("cmd") \
                    == OVERWRITE_CMD:
                overwrite_dispatch = d
        ow_result = (overwrite_dispatch or {}).get(
            "result") or {}
        stock_before = manifest_sha[OVERWRITE_TARGET]
        held = room_stock_after == stock_before
        if held:
            stderr_text = ow_result.get("stderr") or ""
            if "Read-only file system" in stderr_text:
                mechanism = (
                    "a read-only mount: the room refused "
                    "the write at the filesystem (the "
                    "outcome's stderr names a read-only "
                    "file system)")
            elif "Permission denied" in stderr_text:
                mechanism = (
                    "file permissions: the room refused "
                    "the write (the outcome's stderr names "
                    "permission denied)")
            else:
                mechanism = (
                    "the attempt did not take effect "
                    "inside the room (see the outcome "
                    "recorded here); the stocked bytes "
                    "stand unchanged")
            open_item = None
        else:
            mechanism = (
                "none — the overwrite SUCCEEDED and "
                "persisted in the room tree. The rig "
                "binds the whole room tree read-write "
                "into every execution (room.py "
                "bwrap_cmd: --bind <tree> /room), and "
                "room creation chowns every stocked "
                "file to the room uid the worker runs "
                "as; no read-only bind, permission "
                "separation, or other mechanism protects "
                "the stocked sources under work/sources/ "
                "from the worker's own writes")
            open_item = (
                "OPEN ITEM for the examiner: Ben's "
                "ruling (2026-11-24) — briefcase access "
                "is utilise-only; the worker does not "
                "alter the stock. The doorway side "
                "conforms (no write grant touches "
                "sources/, and this rehearsal's sources/ "
                "write was refused), but the ROOM does "
                "not currently enforce utilise-only for "
                "its stocked sources: a worker writing "
                "through his own execution tool can "
                "overwrite them, as this attempt "
                "demonstrates. Recorded as a finding; "
                "the rig is unchanged by this rehearsal.")
        overwrite = {
            "target": OVERWRITE_TARGET,
            "cmd": OVERWRITE_CMD,
            "dispatch_outcome": (overwrite_dispatch
                                 or {}).get("outcome"),
            "exit_status": ow_result.get("exit_status"),
            "stderr_excerpt": (ow_result.get("stderr")
                               or "")[:300],
            "source_sha256_before": stock_before,
            "source_sha256_after_in_room":
                room_stock_after,
            "source_sha256_after_in_sandbox":
                sandbox_stock_after,
            "held": held,
            "mechanism": mechanism,
            "open_item": open_item,
        }

        # The wake package's glossary, from the first
        # iteration's captured request.
        captures = [json.loads(line) for line in
                    captures_path.read_text(
                        encoding="utf-8").splitlines()
                    if line.strip()]
        chat_captures = [c for c in captures
                         if c["mode"] == "chat"]
        wake_package = _package_from_capture(
            chat_captures[1]) if len(chat_captures) > 1 \
            else None
        package_glossary = ((wake_package or {}).get(
            "case") or {}).get("glossary")

        report = {
            "kind": "combined-configuration offline "
                    "rehearsal report (derived matter, "
                    "not record)",
            "run_id": RUN_ID,
            "model": MODEL,
            "route": "nvidia (stub at the connector "
                     "seam; no provider contacted)",
            "manifest_hash": manifest_hash,
            "assembly_id": assembly_id,
            "configuration": {
                "catalogue_contract": (sealed or {}).get(
                    "catalogue_contract"),
                "sealed_grants": (sealed or {}).get(
                    "grants"),
            },
            "glossary": {
                "case_glossary": case_glossary,
                "package_glossary": package_glossary,
            },
            "probe": {
                "settled_count":
                    probe_result["settled_count"],
                "recommended_mode":
                    probe_result["recommended_mode"],
                "counts": probe_result["counts"],
                "evidence_hash":
                    probe_result["evidence_hash"],
            },
            "decision_receipt_hash": receipt_hash,
            "loop_result": {
                "ok": result.get("ok"),
                "outcome": result.get("outcome"),
                "ground": result.get("ground"),
                "iterations": result.get("iterations"),
            },
            "dispatches": [
                {"tool": d["tool"],
                 "registry_version":
                     d["registry_version"],
                 "outcome": d["outcome"]}
                for d in dispatches],
            "rejections": rejections,
            "pulls": pulls,
            "overwrite_attempt": overwrite,
            "brief": {
                "path_used": "framework_scratch"
                if fw_brief_bytes is not None
                else ("room" if room_brief_sha256
                      is not None else None),
                "framework_scratch_sha256":
                    fw_brief_sha256,
                "room_sha256": room_brief_sha256,
                "expected_sha256": _sha256_bytes(
                    BRIEF_TEXT.encode("utf-8")),
                "collected_path": str(
                    work_dir / "brief.md")
                if fw_brief_bytes is not None else None,
            },
            "checker": verdict.get("checks"),
            "event_count": len(events),
            "terminal_readout": {
                "rendered": readout.returncode == 0,
                "path": str(readout_path),
                "stderr": readout.stderr[-500:]
                if readout.returncode != 0 else None,
            },
        }
        with open(work_dir / "report.json", "w",
                  encoding="utf-8") as fh:
            json.dump(report, fh, indent=1)
        return report
    finally:
        if room is not None:
            try:
                room.destroy(remove_tree=True)
            except Exception:
                pass


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1:
        print("usage: combined_rehearsal.py <work-dir>",
              file=sys.stderr)
        return 2
    report = run_rehearsal(argv[0])
    ow = report["overwrite_attempt"]
    print(f"outcome: {report['loop_result']['outcome']} "
          f"(ok={report['loop_result']['ok']}), "
          f"iterations: "
          f"{report['loop_result']['iterations']}, brief "
          f"(framework scratch): "
          f"{report['brief']['framework_scratch_sha256']}")
    print(f"utilise-only witness: stocked source held: "
          f"{ow['held']}")
    if ow["open_item"]:
        print(f"OPEN ITEM: {ow['open_item']}")
    print(f"report: {Path(argv[0]) / 'report.json'}")
    return 0 if report["loop_result"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
