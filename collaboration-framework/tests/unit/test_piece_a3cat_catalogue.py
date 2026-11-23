"""Piece A3-CAT tests — the worker-facing tool catalogue,
against the passed scope PIECE-A3CAT-SCOPE-2026-11-23.md and
its Settlements (INDEX 204), answering Vane's first-worker-run
examination: attempt 2's worker declined after three refusals
for inventing `read_file`, because the wake package never named
its granted tools. These tests exercise the ACTUAL loop package
construction against real assembled instances (the A3 suite's
harness pattern, a stub callable capturing packages):

- every advertised entry corresponds to a sealed grant with
  identical ceiling / bound / side-effect class, and every
  grant is advertised (both directions, against the sealed
  ASSEMBLY_GENERATED payload itself);
- descriptions and parameter schemas match the registry
  contract in BOTH policy copies;
- a grant for an unregistered tool advertises nothing, and
  its requests still refuse at the doorway;
- a registered tool stripped of its description (a test-side
  registry mutation) fails package construction closed: an
  attributable LOOP_STALLED runtime_failure, zero model
  calls, no iteration recorded;
- the recorded LOOP_ITERATION hash equals the real checker's
  independent reconstruction — the checker run over the
  produced record is ok — and hand-appended iterations with
  a wrong hash, an unknown registry version, or a version
  carrying no worker-facing layer are each divergent under
  their own named kind;
- the catalogue is identical across the iterations of one
  activation, hash and version recorded on each;
- the end-to-end inversion of attempt 2: the stub callable
  reads the ADVERTISED name from the captured package's
  catalogue and requests it — the read of a real staged file
  dispatches and settles with the file's content;
- the adapter renders the catalogue verbatim in its own
  prompt section, and a package without a tools field
  renders byte-identically to the legacy construction.

Run: PYTHONPATH=src python3 tests/unit/test_piece_a3cat_catalogue.py
Exits 0 when every check passes.
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from fabric.canonical import canonical, sha256_hex  # noqa: E402
from framework import projection  # noqa: E402
from framework import tool_policy as fw_policy  # noqa: E402
import framework.adapter as adapter_mod  # noqa: E402
from framework.adapter import OpenAICompatibleAdapter  # noqa: E402
from framework.doorway import Doorway  # noqa: E402
from framework.executor import Executor  # noqa: E402
from framework.generator import Generator  # noqa: E402
from framework.loop import Loop  # noqa: E402
from framework.office import Office  # noqa: E402
from framework.record import (CONSTITUTION_HASH,  # noqa: E402
                              FrameworkStore)
import checker.tool_policy as ck_policy  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + "  " + detail)
    if not cond:
        FAILURES.append(name)


DECL = "I am ExampleModel 4.2, served by Provider P, build 9917."
PROVIDER_ID = "example/model-4.2"
SKILLS = [{"name": "drafting", "version": "1.2.0"}]
FULL = {"part": "part-A", "assignment": "Draft the A section",
        "verification_list": ["check the figures"]}
TRACE = "commission brief, crew seat"
GRANTS = [
    {"tool": "sandbox.write",
     "scope_ceiling": {"path_prefix": "notes/"},
     "side_effect_class": "write", "bound": {"count": 3},
     "authority_trace": TRACE},
    {"tool": "sandbox.read",
     "scope_ceiling": {"path_prefix": "notes/"},
     "side_effect_class": "read", "bound": {"count": 3},
     "authority_trace": TRACE},
    {"tool": "sandbox.flaky",
     "scope_ceiling": {"path_prefix": "notes/"},
     "side_effect_class": "write", "bound": {"count": 4},
     "authority_trace": TRACE},
]
BOUNDS = {"step_ceiling": 5, "deadline_seconds": 60}


def identify():
    return {"declaration": DECL, "provider_model_id": PROVIDER_ID}


def fresh(bounds=BOUNDS):
    path = os.path.join(tempfile.mkdtemp(), "run.db")
    store = FrameworkStore(path)
    store.insert_run("run-1", CONSTITUTION_HASH)
    brief = dict(FULL)
    if bounds is not None:
        brief["loop_bounds"] = dict(bounds)
    store.append("RUN_COMMISSIONED", "dir-1", [], {
        "run_id": "run-1",
        "tree": {"part-A": ["part-B"], "part-B": []},
        "seats": {
            "orch-1": {"role": "orchestrator",
                       "identity_status": "declared"},
            "exam-1": {"role": "examiner",
                       "identity_status": "declared"},
            "dir-1": {"role": "director",
                      "identity_status": "declared"},
            "crew-1": {"role": "crew",
                       "identity_status": "unverified"},
            "crew-2": {"role": "crew",
                       "identity_status": "unverified"},
        },
        "briefs": {"crew-1": dict(brief), "crew-2": dict(brief)},
    })
    store.commit()
    d = Doorway(store)
    office = Office(d)
    gen = Generator(d)
    tok = {s: d.issue_token(s) for s in
           ("orch-1", "exam-1", "dir-1", "crew-1", "crew-2")}
    return store, d, office, gen, tok


def issue_case(d, office, tok, seat):
    r = office.issue_new(tok["orch-1"], seat)
    assert r["ok"], r
    d.act(tok["exam-1"], "CASE_JUDGED",
          {"case_id": f"case-{seat}", "version": 1},
          view_seq=d.store.head_seq())
    office.authorise(tok["orch-1"], f"case-{seat}", 1)


def activate(store, d, office, gen, tok, seat="crew-1",
             grants=GRANTS):
    issue_case(d, office, tok, seat)
    gen.propose(tok["orch-1"], seat, part="part-A",
                role_requirements="a careful drafting model")
    r = gen.generate(tok["orch-1"], seat, identify,
                     skills=SKILLS, grants=grants)
    assert r["ok"], r
    gen.verify(tok["orch-1"], r["assembly_id"])
    d.act(tok["exam-1"], "ASSEMBLY_JUDGED",
          gen.judgement(r["assembly_id"]),
          view_seq=store.head_seq())
    packed = gen.pack(tok["orch-1"], r["assembly_id"])
    gen.authorise(tok["orch-1"], r["assembly_id"])
    gen.activate(tok["orch-1"], r["assembly_id"])
    return r, packed["instance_token"]


def events_of(store, type_):
    return [e for e in store.all_events() if e["type"] == type_]


def sealed_grants(store, assembly_id):
    for e in events_of(store, "ASSEMBLY_GENERATED"):
        if e["payload"].get("assembly_id") == assembly_id:
            return e["payload"].get("grants")
    return None


def make_executor(d, deadline=2.0, executor_id="executor-1"):
    base = tempfile.mkdtemp()
    sandbox = os.path.join(base, "sandbox")
    claims = os.path.join(base, "claims")
    ex = Executor(d, sandbox, claim_dir=claims, deadline=deadline,
                  executor_id=executor_id)
    return ex, sandbox, claims


def quiesce(store):
    store._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")


def run_checker(store):
    quiesce(store)
    req = {"store_path": store.path, "run_id": "run-1",
           "snapshot": projection.snapshot(store)}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=SRC)
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "checker"],
        input=json.dumps(req), capture_output=True, text=True,
        env=env, cwd=ROOT)
    return json.loads(proc.stdout)


def loop_check(store):
    return run_checker(store)["checks"]["loop_correspondence"]


class Script:
    """A scripted fake model (the A3 harness's): each step is
    a response dict, an exception, or a function of the
    package; every call is captured with its budget."""

    def __init__(self, steps):
        self.steps = list(steps)
        self.calls = []

    def __call__(self, package, budget=None):
        self.calls.append({"package": package, "budget": budget})
        step = self.steps.pop(0)
        if isinstance(step, Exception):
            raise step
        if callable(step):
            return step(package)
        return step


def contribute(text="draft text", cid="c-1"):
    return {"outcome": "proposals", "proposals": [{
        "type": "CONTRIBUTION",
        "payload": {"contribution_id": cid, "tree_part": "part-A",
                    "text": text}}]}


def tool_req(tool, parameters):
    return {"outcome": "tool_requests",
            "tool_requests": [{"tool": tool,
                               "parameters": parameters}]}


def yield_(summary="the work stands"):
    return {"outcome": "yield", "summary": summary}


# -- CAT1 (i): the advertised catalogue is exactly the sealed
# grants — both directions, limits copied from the grant.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
model = Script([contribute(), yield_()])
res = Loop(d, itok, model).run()
pkg = model.calls[0]["package"]
catalogue = pkg.get("tools")
grants = sealed_grants(store, r["assembly_id"])
check("CAT1 the run yields and the package carries a "
      "catalogue",
      res["ok"] and res["outcome"] == "yield"
      and isinstance(catalogue, list), json.dumps(res)[:200])
by_tool = {e["tool"]: e for e in catalogue} \
    if isinstance(catalogue, list) else {}
grant_by_tool = {}
for g in grants or []:
    grant_by_tool.setdefault(g["tool"], g)
check("CAT1 every grant is advertised and every advertised "
      "entry is a grant (both directions)",
      set(by_tool) == set(grant_by_tool)
      and len(catalogue) == len(grant_by_tool),
      f"advertised={sorted(by_tool)} "
      f"granted={sorted(grant_by_tool)}")
check("CAT1 each entry's ceiling, bound and side-effect "
      "class are the grant's own values",
      all(by_tool[t]["scope_ceiling"] == g["scope_ceiling"]
          and by_tool[t]["bound"] == g["bound"]
          and by_tool[t]["side_effect_class"]
          == g["side_effect_class"]
          for t, g in grant_by_tool.items()))
check("CAT1 the catalogue is in canonical tool order and "
      "each entry carries exactly the catalogue fields",
      [e["tool"] for e in catalogue] == sorted(by_tool)
      and all(set(e) == {"tool", "description", "parameters",
                         "scope_ceiling", "bound",
                         "side_effect_class"}
              for e in catalogue))
entry = by_tool["sandbox.read"]
entry["scope_ceiling"]["path_prefix"] = "tampered/"
sealed_read = next(g for g in sealed_grants(
    store, r["assembly_id"]) if g["tool"] == "sandbox.read")
copies_hold = sealed_read["scope_ceiling"] == \
    {"path_prefix": "notes/"}
entry["scope_ceiling"]["path_prefix"] = "notes/"
check("CAT1 an entry's limits are copies: mutating the "
      "package leaves the sealed grant untouched",
      copies_hold)

# -- CAT2 (ii): descriptions and schemas are the registry
# contract, in both copies.
check("CAT2 every entry's description and parameter schema "
      "match the registry contract in BOTH policy copies",
      all(e["description"]
          == fw_policy.worker_facing(e["tool"])["description"]
          == ck_policy.worker_facing(e["tool"])["description"]
          and e["parameters"]
          == fw_policy.worker_facing(e["tool"])["parameters"]
          == ck_policy.worker_facing(e["tool"])["parameters"]
          for e in catalogue))

# -- CAT3 (vi): identical across iterations; hash + version
# recorded on every iteration event.
iters = events_of(store, "LOOP_ITERATION")
check("CAT3 the catalogue is identical across the "
      "activation's iterations",
      len(model.calls) == 2
      and model.calls[0]["package"]["tools"]
      == model.calls[1]["package"]["tools"])
check("CAT3 every iteration records the catalogue hash and "
      "the registry version",
      len(iters) == 2
      and all(e["payload"].get("catalogue_hash")
              for e in iters)
      and len({e["payload"]["catalogue_hash"]
               for e in iters}) == 1
      and all(e["payload"].get("registry_version")
              == "tool-registry-v2"
              == fw_policy.REGISTRY_VERSION
              == ck_policy.REGISTRY_VERSION for e in iters))

# -- CAT4 (v): the recorded hash is the catalogue's canonical
# hash, and the real checker's independent reconstruction
# over the produced record is ok.
expected_hash = sha256_hex(canonical(catalogue))
check("CAT4 the recorded hash is the canonical hash of the "
      "catalogue the package carried",
      all(e["payload"]["catalogue_hash"] == expected_hash
          for e in iters))
lc = loop_check(store)
check("CAT4 the checker verifies the produced record's loop "
      "correspondence, catalogue reconstruction included",
      lc["result"] == "ok", json.dumps(lc))

# -- CAT5 (v, negatives): hand-appended iterations whose
# catalogue commitments do not verify are divergent under
# their own kinds. (Appended directly, as the A3 suite's
# hand-appends are: the doorway route records only the
# loop's own derivation.)
def append_iteration(store, mutate):
    last = events_of(store, "LOOP_ITERATION")[-1]
    payload = copy.deepcopy(last["payload"])
    payload["iteration"] = last["payload"]["iteration"] + 1
    payload["cursor_from"] = last["payload"]["cursor_to"]
    payload["cursor_to"] = last["payload"]["cursor_to"]
    mutate(payload)
    store.append("LOOP_ITERATION", "loop",
                 [payload["instance_id"]], payload)
    store.commit()


store2, d2, office2, gen2, tok2 = fresh()
r2, itok2 = activate(store2, d2, office2, gen2, tok2)
Loop(d2, itok2, Script([yield_()])).run()
append_iteration(store2, lambda p: p.update(
    catalogue_hash="0" * 64))
lc = loop_check(store2)
check("CAT5 a recorded hash that differs from the "
      "reconstruction is divergent: catalogue_hash_mismatch",
      lc["result"] == "divergent"
      and any(p["kind"] == "catalogue_hash_mismatch"
              for p in lc["problems"]), json.dumps(lc))

store3, d3, office3, gen3, tok3 = fresh()
r3, itok3 = activate(store3, d3, office3, gen3, tok3)
Loop(d3, itok3, Script([yield_()])).run()
append_iteration(store3, lambda p: p.update(
    registry_version="tool-registry-v99"))
lc = loop_check(store3)
check("CAT5 a catalogue recorded under a registry version "
      "the checker does not hold is divergent: "
      "catalogue_registry_version_unknown",
      lc["result"] == "divergent"
      and any(p["kind"] == "catalogue_registry_version_unknown"
              for p in lc["problems"]), json.dumps(lc))

store4, d4, office4, gen4, tok4 = fresh()
r4, itok4 = activate(store4, d4, office4, gen4, tok4)
Loop(d4, itok4, Script([yield_()])).run()
append_iteration(store4, lambda p: p.update(
    registry_version="tool-registry-v1"))
lc = loop_check(store4)
check("CAT5 a catalogue hash recorded under v1 — a version "
      "carrying no worker-facing layer to reconstruct from — "
      "is an explicit inability to verify: "
      "catalogue_not_derivable, never a silent ok",
      lc["result"] == "divergent"
      and any(p["kind"] == "catalogue_not_derivable"
              for p in lc["problems"]), json.dumps(lc))

# -- CAT6 (iii): an unregistered granted tool advertises
# nothing, and its requests still refuse at the doorway.
EVIL = {"tool": "evil.tool", "scope_ceiling": {},
        "side_effect_class": "write", "bound": {"count": 1},
        "authority_trace": TRACE}
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok,
                   grants=GRANTS + [EVIL])
model = Script([tool_req("evil.tool", {}), yield_()])
res = Loop(d, itok, model).run()
advertised = [e["tool"]
              for e in model.calls[0]["package"]["tools"]]
check("CAT6 the unregistered granted tool is not "
      "advertised; the registered grants are",
      "evil.tool" not in advertised
      and sorted(advertised) == ["sandbox.flaky",
                                 "sandbox.read",
                                 "sandbox.write"],
      f"advertised={advertised}")
check("CAT6 a request for the unregistered tool still "
      "refuses at the doorway and dispatches nothing",
      res["ok"] and res["outcome"] == "yield"
      and any(x.get("type") == "TOOL_REQUESTED"
              for x in res["refused"])
      and not any(e["payload"].get("tool") == "evil.tool"
                  for e in events_of(store, "TOOL_DISPATCHED")),
      json.dumps(res.get("refused")))

# -- CAT7 (iv): a registered tool stripped of its description
# fails construction closed — attributable runtime_failure,
# zero model calls, no iteration.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
model = Script([yield_()])
entry_v2 = fw_policy._TOOLS_V2["sandbox.read"]
saved_description = entry_v2.pop("description")
try:
    res = Loop(d, itok, model).run()
finally:
    entry_v2["description"] = saved_description
stalled = events_of(store, "LOOP_STALLED")
detail = stalled[0]["payload"].get("detail") or "" \
    if stalled else ""
check("CAT7 an undescribable granted tool stalls the loop "
      "as an attributable runtime_failure",
      not res["ok"] and res["ground"] == "runtime_failure"
      and res.get("stall_recorded") and len(stalled) == 1
      and stalled[0]["payload"]["ground"] == "runtime_failure"
      and stalled[0]["payload"]["iterations"] == 0,
      json.dumps(res)[:300])
check("CAT7 the failure happens at package construction: "
      "zero model calls, no iteration recorded, and the "
      "stall's detail names the undescribable tool",
      model.calls == []
      and events_of(store, "LOOP_ITERATION") == []
      and "sandbox.read" in detail
      and "package construction failed" in detail, detail)

# -- CAT8 (vii): the inversion of attempt 2 — the worker
# reads the ADVERTISED name out of the catalogue and asks
# for exactly that; the read of a real staged file
# dispatches and settles with the file's content.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
ex, sandbox, _claims = make_executor(d)
os.makedirs(os.path.join(sandbox, "notes"), exist_ok=True)
with open(os.path.join(sandbox, "notes", "staged.txt"),
          "w") as fh:
    fh.write("the staged words")
seen = {}


def ask_advertised(package):
    # The worker's whole knowledge of its tools is the
    # catalogue: take the read tool's name from the entry
    # whose registry description says it reads, verbatim.
    entry = next(e for e in package["tools"]
                 if e["tool"] == "sandbox.read")
    seen["advertised_name"] = entry["tool"]
    seen["advertised_description"] = entry["description"]
    return tool_req(entry["tool"],
                    {"path": "notes/staged.txt"})


def take_result(package):
    results = package["tool_results"]
    assert results and results[-1]["outcome"] == "result", \
        results
    seen["content"] = results[-1]["result"]["content"]
    return yield_("read the staged file")


model = Script([ask_advertised, take_result])
res = Loop(d, itok, model, executor=ex).run()
dispatched = events_of(store, "TOOL_DISPATCHED")
check("CAT8 the advertised name, requested verbatim, "
      "dispatches and the run yields",
      res["ok"] and res["outcome"] == "yield"
      and seen.get("advertised_name") == "sandbox.read"
      and any(e["payload"].get("tool") == "sandbox.read"
              for e in dispatched), json.dumps(res)[:200])
check("CAT8 the settled outcome presented to the worker "
      "carries the staged file's content",
      seen.get("content") == "the staged words")
check("CAT8 the name the worker used is the catalogue's, "
      "whose description is the registry's read description",
      seen.get("advertised_description")
      == fw_policy.worker_facing("sandbox.read")
      ["description"])

# -- CAT9: the adapter renders the catalogue verbatim in its
# own section; a tools-less package renders byte-identically
# to the legacy construction.
captured = {}


def fake_call(messages):
    captured["messages"] = messages
    return json.dumps({"outcome": "yield",
                       "summary": "done"}), "stand-in-model"


ad = OpenAICompatibleAdapter(
    endpoint="http://127.0.0.1:1/v1/chat/completions",
    model="stand-in-model", api_key="test-key", timeout=5.0)
ad._call = fake_call
package = {"case_id": "case-crew-1", "case_version": 1,
           "seat": "crew-1", "tools": catalogue}
ad(package)
prompt = captured["messages"][1]["content"]
check("CAT9 the adapter renders the catalogue verbatim, "
      "as structured data in its own section",
      json.dumps(catalogue, indent=1, default=str) in prompt
      and "Your tool catalogue" in prompt
      and all(e["description"] in prompt for e in catalogue))
bare = {"case_id": "case-crew-1", "case_version": 1,
        "seat": "crew-1"}
ad(bare)
legacy = adapter_mod._CONTRACT + "\n\nYour wake package:\n" \
    + json.dumps(bare, indent=1, default=str)
check("CAT9 a package without a tools field renders "
      "byte-identically to the legacy construction",
      captured["messages"][1]["content"] == legacy)

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES")
    sys.exit(1)
print("ALL PASS")
