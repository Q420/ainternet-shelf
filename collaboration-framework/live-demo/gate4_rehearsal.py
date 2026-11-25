#!/usr/bin/env python3
"""Gate 4 — the doorway connection's OFFLINE rehearsal.

The demonstration preparation paper (DEMONSTRATION-PREPARATION-
2026-11-24.md §2/§3) connects the worker's own execution tool —
`container.exec`, {cmd: [string, ...]} — through the doorway to
the stocked demonstration room, and gate 4 rehearses that whole
path offline before any live run is released: a deterministic
scripted stand-in model drives the REAL loop, the REAL native
adapter, the REAL doorway and the REAL rig, through a stub at
the REAL NVIDIA connector seam — the same helper seam the live
route's transports invoke (`chat` for the adapter's typed calls,
`chat-raw-bounded` for the probe stage's raw call). The stub
captures the exact request bytes each transport constructs for
transmission (hop 3) and returns scripted provider responses;
no provider is contacted, no credential is spent, and nothing
here is a live run.

The rehearsal's sequence is assignment-shaped (the paper §3.4
assignment, room paths): the stand-in reads a source inside the
room, writes scratch work, writes the deliverable, reaches for
an ungranted tool name (refused at translation), proposes a
malformed exec shape (refused at the doorway), executes against
a tampered rig state (the room's precondition refusal travels
back as a result in the §2.3 contract, not a crash), executes
clean again after restoration, and yields.

The room's lifetime is single-process (the paper's standing
constraint, gate 3's closure): this process stocks the room via
stock_demo, holds it for the whole rehearsal, snapshots its
state, and destroys it at the end. The room is never loaded
across processes — its live-mount check would rightly refuse.

The mode judgement is rehearsal furniture: the probe stage runs
against the stub (its scripted trials settle native), and the
decision receipt this driver files names a scripted stand-in
examiner. The live run's judgement is the examiner's, at the
release gate — nothing here substitutes for it.

Outputs land in the rehearsal work directory: the run record
(run/run.db, run/run-export.json, run/responses/), the stub's
captures (captures.jsonl — every transmitted request's exact
bytes), the decision receipt, the stocking record, the room's
final state, the terminal readout rendered from the export,
and report.json summarising the rehearsal as derived matter.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
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

from framework import tool_policy  # noqa: E402
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
    BOUNDS, RUN_ID, _act, _commission_brief,
    _filed_artifact_check, export_store, run_checker)

import room as room_mod  # noqa: E402
import stock_demo  # noqa: E402

MODEL = "openai/gpt-oss-120b"
ENDPOINT = ("https://integrate.api.nvidia.com/v1/chat/"
            "completions")

# The paper §3.4 assignment, with the sandbox now the room
# (the harness's retrieval-mode adaptation, carried to the
# room configuration): the sources at work/sources/ relative
# to the worker's /room/work, the deliverable at
# scratch/brief.md.
ASSIGNMENT_EXEC = (
    "Read the source documents in your office: "
    "sources/stock-take.md, sources/a3-pass.md, and "
    "sources/index-tail.md (your working directory is "
    "/room/work). Write scratch/brief.md: a plain-words "
    "brief, at most ~600 words, that a newcomer could read "
    "to learn what this framework is, what has actually been "
    "proven, what has not been proven, and what remains to "
    "be built. Stay accurate to the sources; invent nothing; "
    "where the sources disagree with each other, say so.")

EXEC_TRACE = (
    "DEMONSTRATION-PREPARATION-2026-11-24.md §2/§3.2 "
    "(gate 4 rehearsal); Ben's own-tool-first direction "
    "(INDEX 421)")

# The paper §3.2 grant set: the execution tool ONLY. No
# retrieval tools are offered in this configuration.
GRANTS_EXEC = [
    {"tool": "container.exec",
     "scope_ceiling": {},
     "side_effect_class": "execute",
     "bound": {"count": 12},
     "authority_trace": EXEC_TRACE},
]

# The deliverable the scripted stand-in writes: fixed text,
# so the brief the room holds and the hash the evidence
# expects cannot drift apart. The rehearsal's worker is
# scripted; the brief's content is furniture, and its
# accuracy is not a rehearsal claim.
BRIEF_TEXT = (
    "# Brief — the collaborative agent framework\n\n"
    "The framework assembles one generated agent for one "
    "bounded task: a model, an identity declared at "
    "assembly, the skills the task needs, exactly the tool "
    "grants the case allows, and the case itself. The work "
    "is carried in a durable record; a doorway checks every "
    "framework tool call against the sealed grants before "
    "anything is dispatched, and an independent checker "
    "reconstructs each run from its record afterwards.\n\n"
    "What has been proven: the record, doorway, assembly "
    "and bounded loop stand built and examined; a worker "
    "has read its sources through the doorway under the "
    "record. What has not been proven: a worker composing "
    "an assignment end to end, and agents collaborating "
    "through shared work — the demonstration this brief "
    "was written inside is the first room run, and its "
    "own result is not claimed here.\n")

DRAFT_TEXT = "draft: stock-take read in-room; brief in progress\n"


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _native_call(call_id, name, arguments):
    """One scripted provider response carrying a single
    native tool call (content null beside the call — the
    shape the adapter's native path reads)."""
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
    native, then the chat sequence — identify, the eight
    rehearsal iterations in order.

    The stand-in answers in the names the route's provider
    would emit: it was offered the wire names (the route's
    name translation, Ben's ruling 2026-11-24), so its
    calls to the offered tools carry the dash forms —
    container-exec, probe-lookup — and the framework's
    translation carries them back. The one exception is
    step (d)'s ungranted reach, which names a framework
    tool it was never offered, in that tool's canonical
    form: it stands as emitted and is refused at
    translation like any unknown name."""
    brief_b64 = base64.b64encode(
        BRIEF_TEXT.encode("utf-8")).decode("ascii")
    write_brief_cmd = [
        "/usr/bin/python3", "-c",
        "import base64, pathlib; "
        "pathlib.Path('/room/scratch/brief.md')"
        ".write_bytes(base64.b64decode('"
        + brief_b64 + "'))"]
    write_draft_cmd = [
        "/bin/bash", "-c",
        "printf '%s' '" + DRAFT_TEXT.replace("'", "") + "' "
        "> /room/scratch/draft.txt && "
        "cat /room/scratch/draft.txt"]
    probe_step = {
        "respond": _native_call(
            "fc-probe", "probe-lookup",
            {"object": "brass lantern"}),
        "action": None}
    chat = [
        # 0 — the identity call (generation's onboarding).
        {"respond": _text_response(
            "identify",
            "I am openai/gpt-oss-120b, a model served on "
            "the NVIDIA route. (Scripted stand-in "
            "declaration for the gate 4 offline rehearsal; "
            "no provider was contacted.)"),
         "action": None},
        # 1 — (a) read a source inside the room.
        {"respond": _native_call(
            "fc-g4-1", "container-exec",
            {"cmd": ["/bin/cat", "sources/stock-take.md"]}),
         "action": None},
        # 2 — (b) write scratch work, and read it back.
        {"respond": _native_call(
            "fc-g4-2", "container-exec",
            {"cmd": write_draft_cmd}),
         "action": None},
        # 3 — (c) write the deliverable.
        {"respond": _native_call(
            "fc-g4-3", "container-exec",
            {"cmd": write_brief_cmd}),
         "action": None},
        # 4 — (d) an ungranted tool name: refused at
        # translation (unknown_tool), never dispatched.
        {"respond": _native_call(
            "fc-g4-4", "sandbox.read",
            {"path": "sources/stock-take.md"}),
         "action": None},
        # 5 — (d) a malformed exec shape: cmd as a string,
        # not an array — schema-valid at translation,
        # refused at the doorway's shape check.
        {"respond": _native_call(
            "fc-g4-5", "container-exec",
            {"cmd": "/bin/cat sources/stock-take.md"}),
         "action": None},
        # 6 — (e) the rig state tampered before this call:
        # the doorway dispatches; the room refuses on its
        # rig-integrity precondition; the refusal returns
        # as a result in the contract.
        {"respond": _native_call(
            "fc-g4-6", "container-exec",
            {"cmd": ["/bin/cat", "sources/a3-pass.md"]}),
         "action": "tamper_reaper"},
        # 7 — the rig state restored before this call: a
        # clean execution, its output the third source's
        # in-room hash.
        {"respond": _native_call(
            "fc-g4-7", "container-exec",
            {"cmd": ["/usr/bin/sha256sum",
                     "sources/index-tail.md"]}),
         "action": "restore_reaper"},
        # 8 — the yield.
        {"respond": _text_response(
            "yield",
            json.dumps({
                "outcome": "yield",
                "summary": "Read the stock-take in-room, "
                           "drafted in scratch, and wrote "
                           "scratch/brief.md; the ungranted "
                           "and malformed calls were refused "
                           "and one execution met the room's "
                           "rig-integrity refusal before the "
                           "clean final read."})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": [dict(probe_step)
                                 for _ in range(5)]}


STUB_SOURCE = '''#!/usr/bin/env python3
"""The gate 4 rehearsal's stub helper: stands in for the
NVIDIA connector helper at its own seam. Invoked exactly as
the real helper is — [python, helper, "chat"|"chat-raw-
bounded", model], the request JSON on stdin — it records the
exact request bytes to the captures file (hop 3's evidence),
performs any scripted room action, and answers from the
script: the provider JSON itself for "chat"; for
"chat-raw-bounded", the bounded envelope the real helper
frames, wrapping the same provider JSON. No network, no
credential, no provider."""
import base64
import hashlib
import json
import os
import sys

FORGED_REAPER = (
    "# forged reaper - gate 4 rehearsal tamper\\n"
    "# (never executed: the room's rig-integrity "
    "precondition refuses first)\\n")


def main():
    mode = sys.argv[1]
    model = sys.argv[2]
    body = sys.stdin.buffer.read()
    with open(os.environ["GATE4_STUB_SCRIPT"],
              encoding="utf-8") as fh:
        script = json.load(fh)
    state_path = os.environ["GATE4_STUB_STATE"]
    try:
        with open(state_path, encoding="utf-8") as fh:
            state = json.load(fh)
    except (OSError, ValueError):
        state = {}
    index = int(state.get(mode, 0))
    state[mode] = index + 1
    with open(state_path, "w", encoding="utf-8") as fh:
        json.dump(state, fh)
    with open(os.environ["GATE4_STUB_CAPTURES"], "a",
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
            f"gate4 stub: script exhausted for mode {mode} "
            f"at index {index}\\n")
        return 3
    step = steps[index]
    action = step.get("action")
    if action in ("tamper_reaper", "restore_reaper"):
        target = os.path.join(os.environ["GATE4_ROOM_TREE"],
                              "rig", "reaper.py")
        if action == "tamper_reaper":
            with open(target, "w", encoding="utf-8") as fh:
                fh.write(FORGED_REAPER)
        else:
            with open(os.environ["GATE4_REAPER_BACKUP"],
                      "rb") as fh:
                genuine = fh.read()
            with open(target, "wb") as fh:
                fh.write(genuine)
    payload = json.dumps(step["respond"]).encode("utf-8")
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


def run_rehearsal(work_dir):
    """Run the whole gate 4 rehearsal in `work_dir` (created
    fresh; must not already hold a rehearsal). Returns the
    report dict (also written to work_dir/report.json). The
    room is destroyed before this returns, on every path."""
    # Resolved absolute: the rig verifies the room's backing
    # against the LIVE mount table, which records absolute
    # paths — a relative base would make that verification
    # fail (and the room would rightly refuse, storage-
    # backing, as a relative-path rehearsal invocation
    # demonstrated before this hardening).
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

    # The stub and its script, written before any transport
    # can invoke them; the stub's channels travel in the
    # environment the transports pass to the helper.
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
    os.environ["GATE4_STUB_SCRIPT"] = str(script_path)
    os.environ["GATE4_STUB_STATE"] = str(state_path)
    os.environ["GATE4_STUB_CAPTURES"] = str(captures_path)

    room = None
    try:
        # STOCK (hop 2) — the paper §1 stocking, verified by
        # its smoke set before any worker exists; the room
        # is then held in THIS process for the whole
        # rehearsal.
        stocking = stock_demo.stock_demo_room(
            rooms_base, "demo")
        room = room_mod.load_room(rooms_base, "demo")
        manifest = stocking["source_manifest"]
        manifest_hash = manifest["manifest_sha256"]
        backup_path = work_dir / "reaper-genuine.py"
        backup_path.write_bytes(
            (room.tree / "rig" / "reaper.py").read_bytes())
        os.environ["GATE4_ROOM_TREE"] = str(room.tree)
        os.environ["GATE4_REAPER_BACKUP"] = str(backup_path)

        # COMMISSION — the harness's flow, with the room
        # configuration's assignment and the stocking
        # manifest as the sealed source set.
        store_path = str(run_dir / "run.db")
        store = FrameworkStore(store_path)
        store.insert_run(RUN_ID, CONSTITUTION_HASH)
        brief = _commission_brief(ASSIGNMENT_EXEC,
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

        # ASSEMBLE — the adapter on the NVIDIA route's seam,
        # its transport the stub helper; generation under
        # the probe contract and the exec catalogue
        # contract, grants the execution tool only. The
        # adapter carries the route the probe act records
        # below ("nvidia"), so the route's name translation
        # governs its definitions and extraction.
        adapter = OpenAICompatibleAdapter(
            endpoint=ENDPOINT, model=MODEL, timeout=300.0,
            route="nvidia")
        install_connector_transport(
            adapter, str(stub_path), MODEL)
        gen.propose(
            tok["orch-1"], "crew-1", part="part-A",
            role_requirements="a model able to read three "
                              "source documents in its room "
                              "and write a short, accurate, "
                              "plain-words brief")
        generated = gen.generate(
            tok["orch-1"], "crew-1", adapter.identify,
            skills=[], grants=GRANTS_EXEC,
            model_requested=MODEL, probe=True, exec_room=True)
        if not generated.get("ok"):
            raise RuntimeError(
                f"generation failed: "
                f"{generated.get('problems')}")
        assembly_id = generated["assembly_id"]

        # PROBE — five scripted trials through the real
        # NVIDIA raw-call seam over the stub.
        raw_call = install_nvidia_connector_raw_call(
            helper_path=str(stub_path), model=MODEL)
        probe_result = gen.probe(
            tok["orch-1"], assembly_id, raw_call,
            route="nvidia", model=MODEL)
        gen.verify(tok["orch-1"], assembly_id)

        # JUDGE (hop 1) — the rehearsal's decision receipt,
        # retained before the judgement is recorded; the
        # judgement binds its canonical hash, as the live
        # phases bind the examiner's.
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
                "Gate 4 offline rehearsal: the scripted "
                "stand-in's probe trials settled 5/5 native "
                "(probe.lookup), and the demonstration "
                "preparation paper §3.1 proposes native for "
                "the room configuration. This judgement is "
                "rehearsal furniture by a scripted stand-in "
                "examiner; the live run's mode judgement is "
                "the examiner's at the release gate.",
            "examiner": "gate-4 rehearsal (scripted "
                        "stand-in examiner)",
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

        # RUN — the executor holds the room; the loop drives
        # the real adapter/doorway/rig path under the
        # evidence regime rooted at the run directory.
        executor = Executor(
            doorway, str(run_dir / "sandbox"),
            claim_dir=str(run_dir / "claims"), deadline=150.0,
            room=room,
            exec_timeout=stock_demo.PER_EXECUTION_WALL_S)
        gen.activate(tok["orch-1"], assembly_id)
        result = Loop(doorway, packed["instance_token"],
                      adapter, executor=executor,
                      evidence_store=str(run_dir)).run()

        # COLLECT — the deliverable's hash at the wall
        # (hop 9) and the room's final state, both taken
        # before teardown; then the checker (hop 10), the
        # export, and the terminal readout over the export.
        brief_path = room.tree / "scratch" / "brief.md"
        brief_sha256 = _sha256_bytes(
            brief_path.read_bytes()) if brief_path.exists() \
            else None
        room_state = json.loads(room.state_path.read_text())
        (work_dir / "room-state.json").write_text(
            json.dumps(room_state, indent=1),
            encoding="utf-8")
        (work_dir / "stocking.json").write_text(
            json.dumps(stocking, indent=1), encoding="utf-8")
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
        report = {
            "kind": "gate 4 doorway-connection offline "
                    "rehearsal report (derived matter, not "
                    "record)",
            "run_id": RUN_ID,
            "model": MODEL,
            "route": "nvidia (stub at the connector seam; "
                     "no provider contacted)",
            "manifest_hash": manifest_hash,
            "assembly_id": assembly_id,
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
            "brief_sha256": brief_sha256,
            "brief_expected_sha256": _sha256_bytes(
                BRIEF_TEXT.encode("utf-8")),
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
        print("usage: gate4_rehearsal.py <work-dir>",
              file=sys.stderr)
        return 2
    report = run_rehearsal(argv[0])
    print(f"outcome: {report['loop_result']['outcome']} "
          f"(ok={report['loop_result']['ok']}), iterations: "
          f"{report['loop_result']['iterations']}, brief: "
          f"{report['brief_sha256']}")
    print(f"report: {Path(argv[0]) / 'report.json'}")
    return 0 if report["loop_result"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
