# V2 QUALIFICATION — STAGE 1 REPORT
## Nemotron governed-subject pilot (Plan 01, adopted by Ben 2026-11-12; Alex adjudication pb-mwe90lo6)

**Kind of work:** source inspection plus ONE executed test (the
`reference_insert` probe, §3). All code was run in a scratch copy at
`~/workspace/duenna-letters/qual-scratch/`; no shelf file was modified,
nothing was pushed, no letters were sent. Scratch copies verified
byte-identical to the pinned shelf inputs before execution.

**Pinned inputs (sha256):**

| Artefact | sha256 |
|---|---|
| `duenna/qwen-ab/run_ab.py` | `acb647bd50bfa2f6a219415dd60242a3efbacbf5a68a2d16ac7c3dbd57663d53` |
| `duenna/qwen-ab/v2/tools.py` | `e78f45d31ed6831253ed5fed1dc3f5dd22938b70e7c47cd15e190b912161cc1d` |
| `duenna/qwen-ab/v2/demo_tools.py` | `6c960e442009c6c8978eaeab506311626f74df014aac50ef7bff42ff5bdb4648` |
| `duenna/qwen-ab/v2/PROCESS-TREES.md` | `5528ab69bec2f7fcdea776748e9bdc2e84ec97b4fa1d4be35bf7fd386e24b0ad` |
| `duenna/qwen-ab/v2/V2-PACKAGE.md` | `3dcda7b285f3eb26c979a4bf48b410196d0c804cf5b4f24482882cbe2cc3754f` |
| `duenna/qwen-ab/v2/DEMO-RESULTS.json` | `baaca7a840d19a194a9754be513d8a95f92657ba2624a0cc62ec1f1663b02dbf` |

## Verdict summary

- **Driver verdict:** the V2 package contains **no driver**. Nothing in
  the package executes the nine process trees end-to-end. The only
  executable artefact is a three-part fixture demo. The one historical
  full-battery attempt ran on a *different, later stack* (run_c.py +
  tools23) and was ruled **NULL** by Ben (2026-11-10). Full-battery
  execution on the V2 stack: **NOT PRESENT / NOT ESTABLISHED**.
- **`reference_insert` verdict: YES — an unextracted result, and even a
  hand-fabricated result, can be inserted and is represented in the
  ledger as verified evidence (`verification: "PASS"`).** Executed
  evidence in §3. `reference_insert` performs no origin check, no
  hash check, and no state restriction beyond a two-value allowlist
  (`"EXTRACTED"`, `"FOUND"`) that any caller-supplied dict can claim.
- **Capability counts (of the ten capabilities in §4):**
  EXECUTABLE **4** · FIXTURE-ONLY **2** · NOT PRESENT **4**.

---

## 1. EXECUTION PATH — is there a driver for the nine trees?

**No.** The `v2/` package contains exactly two Python files:
`tools.py` (the five tools) and `demo_tools.py` (the fixture demo).
`PROCESS-TREES.md` is a prose specification: nine trees (T01–T09),
each a list of `[TOOL]` / `[MODEL]` / `[rule]` steps with inputs,
verification, failure and recovery conditions. No code in the package
parses, schedules, or executes those steps; no code in the package
calls a model at all.

A tree-wide search of the whole `qwen-ab/` tree confirms this: the
only files that reference tree step ids (`T0x-STEP…`) are the
per-version demo scripts (`v2/demo_tools.py`, `v21/demo21.py`, …,
`v24/demo24.py`). Each demo hand-codes a fragment of its own version's
trees; none is a general driver.

**What `demo_tools.py` actually executes** (source + the shipped
`DEMO-RESULTS.json`, whose `tool_call_log` holds exactly **19** logged
calls: `verify_field` ×10, `source_extract` ×4, `receipt_worksheet`
×4, `shelf_lookup` ×1; `reference_insert` takes no operation_id and is
not logged):

- **Demo 1 — a partial, hand-coded walk of T05's construction steps.**
  One `shelf_lookup` of a shelf-manifest row; four `source_extract`
  calls against corpus section `r60-revision-change-record#009`; one
  cross-record `verify_field`; then **eight `reference_insert` calls
  made directly by demo code** — of which **four were fed hand-built
  dicts, not tool results** (demo_tools.py:48–64): `artifact`
  (claimed `FOUND`), `version` (claimed `EXTRACTED`; the value was
  produced by an inline regex in the demo at :40–42, because
  `tools.py` has no version extractor), `correction_b` (claimed
  `EXTRACTED`, `source_hash: None`), `evidence` (claimed `FOUND`).
  Finally `verify_field` on each field against
  `run_ab.EXPECTED_RECORD`. T05 STEP-01 (contract load), STEP-06
  ([MODEL] correction) and STEP-07 (verify + report assembly) are not
  implemented; the demo approximates STEP-02…05 only.
- **Demo 2 — one `verify_field` call** showing the v1 error value
  FAILs against its expected value.
- **Demo 3 — T09's worksheet operation only:** `receipt_worksheet`
  over the four receipt fixtures (FR-A/FR-B/FR-C → REJECT,
  FR-VALID → CLOSE). No [MODEL] step (T09 STEP-03) is executed.

No `[MODEL]` step of any tree is executed anywhere in the package.
T01, T02, T03, T04, T06, T07 and T08 are not executed at all, even in
part.

**The historical battery does not cure this.** A driver (`run_c.py`)
did exist outside the package, and a battery was attempted with it —
but per `duenna/qwen-ab/v2-battery-voided/VOIDED.md` that attempt
used **tools23**, not this package's `tools.py`; it stopped at T01
Arm C on a tools23 defect, was patched at driver level mid-run, and
Ben ruled the whole attempt **NULL** (2026-11-10). Its stated clean-
rerun conditions (defect fixed inside a new tools revision, full
stack frozen and hashed, from-zero run) were never carried out for
the V2 stack. Copies of `run_c.py` survive only under the
`v24*-foundation/` directories.

**Label for the full-battery execution claim: NOT PRESENT in the
package; NOT ESTABLISHED by any executed run on this stack.** The
V2-PACKAGE.md "Execution model" section describes how a battery
*will* run under a driver; that driver is a Stage 3 deliverable,
not an existing artefact.

## 2. MODEL COUPLING — how tools.py is tied to the Qwen trial

`tools.py` never calls a model itself. Its coupling is through its
data plane: at import time it binds itself to the Qwen A/B trial's
runner, corpus, fixtures and ground truth. Every coupling point:

**In `v2/tools.py`:**

- **:18–19** — `sys.path.insert(0, str(HERE.parent))` then
  `import run_ab`. Importing the tools *executes the trial runner's
  module level*: corpus load, pack construction, fixture constants.
- **:21** — `BY_ID = run_ab.BY_ID`. The tools' entire source universe
  is the trial's frozen corpus.
- **:22** — `MANIFEST_MD = pathlib.Path.home() /
  "workspace/ainternet-shelf/MANIFEST.md"`. An absolute path to the
  **live shelf tree in the home directory**, outside the package and
  outside any pinned input set. `shelf_lookup("shelf-manifest:…")`
  reads that live file at call time (this probe's demo-path reads
  therefore touched the live manifest, read-only).
- **:52–59** — `shelf_lookup` serves section text from `BY_ID` with
  `verification: "FOUND"`.
- **:61–66** — `_EXTRACTORS`: the only four extraction rules are
  regexes written for one document family's phrasing
  (`(\d+) fixtures executed`, `(\d+) PASS`,
  `Harness sha256 **…**`, `results sha256 **…**` — the R60 revision
  change record). Any other field, from any other document, is
  NOT FOUND by construction.

**In `run_ab.py` (executed transitively by the import):**

- **:15–20** — `INDEX = ~/workspace/pulse-bridge/index`;
  `sys.path.insert(0, INDEX)`; `from query import load`;
  `SECS, _MAN = load()` at module level. The corpus is the
  pulse-bridge index's `sections.jsonl` — the frozen Duenna
  programme record — loaded from a home-tree path outside the
  package. If that path or file is absent, `import tools` fails.
- **:20** — `MODEL = "qwen/qwen3.8-27b"`: the subject is pinned in
  the runner.
- **:18** — `GROQ = ~/workspace/custom-connectors/custom.groq/bin/
  groq_api.py`; **:356–375** `call_qwen` invokes that helper as a
  subprocess with `model=MODEL`. The transport is a Groq-connector
  shell-out, hard-wired.
- **:~95–152** — the battery's task inputs are module-level
  constants: packs `P_T01`…`P_T09` built from named corpus section
  ids, the `OBLIGATION_T09` spec (:136) and the `RECEIPTS` fixtures
  (:148).
- **:249** — `EXPECTED_RECORD`: the T05 ground truth lives in the
  runner. `demo_tools.py:19, 65–66, 83–84` imports `run_ab` for
  `EXPECTED_RECORD`, `RECEIPTS` and `OBLIGATION_T09` — the demo's
  pass/fail criteria are the trial's constants, not pilot data.

**What breaks if the subject model changes:**

1. **Calls:** nothing in `tools.py` breaks — it makes no calls — but
   every existing caller path does: `run_ab.call_qwen` is
   model- and transport-pinned, and `PROCESS-TREES.md` specifies the
   [MODEL] steps as the *worker's (Qwen's)*, consuming declared
   inputs. A new subject needs a new adapter and a driver that does
   not exist yet (Stage 2/3 work, as the plan states).
2. **Data:** the tools keep working only over the same frozen corpus,
   the same four extractors, and the same expected-record constants.
   A pilot whose inputs differ from the Qwen trial's packs gets
   NOT FOUND, not neutral behaviour — the tools cannot serve a
   model-neutral input set as they stand.
3. **Import:** any consumer of the tools inherits `run_ab`'s module
   level: corpus load from `~/workspace/pulse-bridge/index` and the
   trial's fixtures. There is no way to import the five tools
   "clean".

Corroboration that this coupling was real, not theoretical: the
voided battery (§1) had to move to a *new tools revision* (tools23)
and a separate driver rather than reuse this package as-is.


## 3. THE `reference_insert` TEST (executed)

Alex's flagged question: `tools.py:95` —
`ok = extraction["verification"] in ("EXTRACTED", "FOUND")` — can an
unextracted or otherwise unsuitable result be inserted and
represented as verified evidence?

**Executed answer: yes, twice over.** The probe below ran against
the unmodified scratch copy of `v2/tools.py` (hash-pinned, §header)
in the real environment, so the corpus load is genuine. Four cases:

- **(a) Genuine EXTRACTED** result from `source_extract` → inserted;
  ledger entry `verification: "PASS"` with the true value (38) and
  the true source hash. Correct behaviour.
- **(b) FOUND-state result** — the raw `shelf_lookup` output (whole
  section text as `value`, never passed through any extractor) →
  **inserted; ledger entry `verification: "PASS"`**, the entire
  section text recorded as the field's value with the section's real
  hash as provenance. An unextracted result is represented as
  verified evidence.
- **(c) Hand-fabricated dict** claiming `"EXTRACTED"`, with an
  invented value (12345; the true value is 38) and an invented
  source hash (`ffff…`) → **inserted; ledger entry
  `verification: "PASS"`**, recording the fabricated value *and the
  fabricated hash* as the field's provenance. `reference_insert`
  checks nothing about the dict's origin: no operation-id
  validation, no hash recomputation, no registry of issued results.
- **(d) NOT FOUND control** → the entry is marked
  `verification: "FAIL"` — but note the mechanism: `reference_insert`
  **never refuses**. It returns `(value, entry)` in every case
  (here `(None, FAIL-entry)`); the only guard is a label in the
  returned entry, which downstream code must check for itself.

This is not a hypothetical misuse path: the package's own demo
relies on it. Four of Demo 1's eight ledger fields were inserted
from hand-built dicts (demo_tools.py:48–64), including
`correction_b` — claimed `EXTRACTED` with `source_hash: None` — and
its shipped ledger entry in `DEMO-RESULTS.json` reads
`verification: "PASS"` (see §1). The demo's T05 record therefore
stands as verified partly on caller-asserted provenance.

For the record: later, non-pinned revisions noticed this too —
`v21/tools21.py`'s header states its `reference_insert` "is
hardened: it (a) refuses results with…". Those revisions are not
the package under qualification and were not themselves qualified
here; the note is included only because it corroborates that the
v2 behaviour is a defect, not a design intent.

### Probe code (verbatim; `~/workspace/duenna-letters/qual-scratch/probe_refinsert.py`, sha256 `4f41473665cb8ab5698b8a077f4905b56c4ba5cd1ec8aa5fae582d88ae3ef005`)

```python
#!/usr/bin/env python3
"""PROBE (Stage 1 qualification): what does v2/tools.py reference_insert
actually accept? Cases:
 (a) a genuine EXTRACTED result from source_extract;
 (b) a FOUND-state result (raw shelf_lookup output, never extracted);
 (c) a hand-fabricated dict claiming EXTRACTED, with an invented
     value and an invented source_hash;
 (d) a NOT FOUND result (control: the only non-accepted class).
Run from the v2 directory's parent layout: this file lives in
qual-scratch/, imports the scratch copy of v2/tools.py unmodified.
"""
import json, sys, pathlib

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE / "qwen-ab" / "v2"))
import tools  # noqa: E402  (scratch copy of v2/tools.py, unmodified)

SEC = "r60-revision-change-record#009"

def show(label, result_dict, inserted):
    value, entry = inserted
    print(f"--- {label}")
    print("input verification state:", result_dict.get("verification"))
    print("input value (repr, truncated):", repr(result_dict.get("value"))[:120])
    print("reference_insert returned value:", repr(value)[:120])
    print("ledger entry:", json.dumps(entry))
    print()

# (a) genuine EXTRACTED
ext = tools.source_extract(SEC, "fixtures_executed")
print("source_extract result:", json.dumps(ext))
show("(a) GENUINE EXTRACTED", ext,
     tools.reference_insert("fixtures_total", "PROBE-STEP-A", ext))

# (b) FOUND-state result, obtained from shelf_lookup (never extracted)
look = tools.shelf_lookup(SEC)
print("shelf_lookup verification:", look["verification"],
      "| value type:", type(look["value"]).__name__)
show("(b) FOUND (shelf_lookup result passed directly)", look,
     tools.reference_insert("whole_section_text", "PROBE-STEP-B", look))

# (c) hand-fabricated dict claiming EXTRACTED
fake = {"operation_id": "op-999", "tool": "source_extract",
        "source_ref": SEC, "source_hash": "f" * 64,
        "value": 12345, "verification": "EXTRACTED",
        "evidence_line": "38 fixtures executed, 38 PASS",
        "failure_reason": None}
show("(c) FABRICATED dict claiming EXTRACTED", fake,
     tools.reference_insert("fixtures_total", "PROBE-STEP-C", fake))

# (d) NOT FOUND control
nf = tools.source_extract("no-such-section#000", "fixtures_executed")
print("missing-section extract result:", json.dumps(nf))
show("(d) NOT FOUND (control)", nf,
     tools.reference_insert("fixtures_total", "PROBE-STEP-D", nf))
```

### Raw output (verbatim, stdout, exit 0)

```
source_extract result: {"operation_id": "op-001", "tool": "source_extract", "source_ref": "r60-revision-change-record#009", "source_hash": "5db36f75948ce78dc24e930f48db783de0f224ecf727353b01d8328161e0af15", "value": 38, "verification": "EXTRACTED", "evidence_line": "- Full suite: **38 fixtures executed, 38 PASS, 0 FAIL** (31", "failure_reason": null}
--- (a) GENUINE EXTRACTED
input verification state: EXTRACTED
input value (repr, truncated): 38
reference_insert returned value: 38
ledger entry: {"field": "fixtures_total", "value": 38, "process_step": "PROBE-STEP-A", "source_ref": "r60-revision-change-record#009", "source_hash": "5db36f75948ce78dc24e930f48db783de0f224ecf727353b01d8328161e0af15", "operation": "reference_insert", "verification": "PASS", "verification_method": "tool_result_reference"}

shelf_lookup verification: FOUND | value type: str
--- (b) FOUND (shelf_lookup result passed directly)
input verification state: FOUND
input value (repr, truncated): '## Addendum 3 — Verdict provenance implemented (2026-11-10)\n\nAlex authorised implementation of the revised FX-R60j/k\
reference_insert returned value: '## Addendum 3 — Verdict provenance implemented (2026-11-10)\n\nAlex authorised implementation of the revised FX-R60j/k\
ledger entry: {"field": "whole_section_text", "value": "## Addendum 3 — Verdict provenance implemented (2026-11-10)\n\nAlex authorised implementation of the revised FX-R60j/k\nproposal (pb-mwbhu9zh), with his precision requirement: identity\nby retained object references and `is` comparisons, not id()\nintegers. Implemented as harness **v2.4**:\n\n- The factory closure holds a private **issuance record**. Each\n  entry retains the actual contract instance, the actual\n  verdict object it returned, and the fingerprint of the\n  verdict's canonical contents at issuance.\n- `validate_verdict` (after the existing field checks, which\n  are unchanged and fire first) requires: an entry where\n  `recorded contract is this contract` and `recorded verdict is\n  this verdict` — else \"REJECTED: verdict not issued by this\n  contract\" — and the current fingerprint equal to the issuance\n  fingerprint — else \"REJECTED: verdict altered after\n  issuance\".\n- New fixtures **FX-R60j** (forgery with the genuine pinned\n  hash rejected; genuine verdict accepted), **FX-R60k**\n  (cross-contract replay rejected — different digest, and\n  identical issued contents; same-contract control accepted),\n  **FX-R60l** (issued object mutated after return rejected;\n  genuine accepted).\n- Full suite: **38 fixtures executed, 38 PASS, 0 FAIL** (31\n  original identities + FX-R60f/g/h/i/j/k/l). Harness sha256\n  **854a3e8644817ef1acb9c83be01a0164d3f987ada19e25fe972d86a7e0b2f9d5**;\n  results sha256\n  **902936d8aa27e6e75b48644cb2961f1ccbeeaa2344cf79c8573a77f9b470ad66**.\n\n**Sabotage evidence:** the **integrity sabotage was executed\nby the implementer** — with the fingerprint comparison removed,\n**FX-R60l fails alone (37 PASS / 1 FAIL)**, the rest of the\nsuite unaffected. The **identity sabotage** (removing the\nobject-identity provenance check) could not be constructed by\nthe implementer — her tooling blocked the weakened variant\nagain — and is **assigned to independent examination**, with\nthe still-outstanding v2.3 sabotage runs (mutable-registry\nvariant vs FX-R60h under the factory; restored-global-dispatch\nvariant vs FX-R60i) and the executed reproduction of the v2.3\ncross-contract replay (FX-R60k, established by inspection).\nThis record claims none of those as implementer-run.\n\n", "process_step": "PROBE-STEP-B", "source_ref": "r60-revision-change-record#009", "source_hash": "5db36f75948ce78dc24e930f48db783de0f224ecf727353b01d8328161e0af15", "operation": "reference_insert", "verification": "PASS", "verification_method": "tool_result_reference"}

--- (c) FABRICATED dict claiming EXTRACTED
input verification state: EXTRACTED
input value (repr, truncated): 12345
reference_insert returned value: 12345
ledger entry: {"field": "fixtures_total", "value": 12345, "process_step": "PROBE-STEP-C", "source_ref": "r60-revision-change-record#009", "source_hash": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "operation": "reference_insert", "verification": "PASS", "verification_method": "tool_result_reference"}

missing-section extract result: {"operation_id": "op-004", "tool": "source_extract", "source_ref": "no-such-section#000", "source_hash": null, "value": null, "verification": "NOT FOUND", "failure_reason": "no such section: no-such-section#000"}
--- (d) NOT FOUND (control)
input verification state: NOT FOUND
input value (repr, truncated): None
reference_insert returned value: None
ledger entry: {"field": "fixtures_total", "value": null, "process_step": "PROBE-STEP-D", "source_ref": "no-such-section#000", "source_hash": null, "operation": "reference_insert", "verification": "FAIL", "verification_method": "tool_result_reference"}

EXIT=0
```

(The output above is complete. The untruncated capture is also
preserved at `~/workspace/duenna-letters/qual-scratch/probe-output.txt`,
4,993 bytes.)

## 4. CAPABILITY TABLE

Labels: **EXECUTABLE** = runs today, outside a single canned demo,
within its stated substrate · **FIXTURE-ONLY** = demonstrated only
inside the package's fixtures, or its rule set covers only those
fixtures · **NOT PRESENT** = no implementation, or specification
only.

| # | Capability (Plan Stage 1 + Alex §2) | Label | Evidence (one line) |
|---|---|---|---|
| 1 | Nine-tree execution | **NOT PRESENT** | Trees exist only as prose in PROCESS-TREES.md; no driver in the package (§1); the sole battery attempt used a later stack and was ruled NULL. |
| 2 | Five tools | **EXECUTABLE** | All five import and run in scratch against the real corpus/manifest (probe §3; demo log of 19 calls). |
| 3 | Per-field ledger emission | **EXECUTABLE** | `reference_insert` emits the §6-shaped entry per field (probe (a); demo's 8-entry ledger) — emission works; the entries' *trustworthiness* is the §3 defect, counted there, not here. |
| 4 | Receipt comparison | **EXECUTABLE** | `receipt_worksheet` executed: FR-A/FR-B/FR-C → REJECT, FR-VALID → CLOSE (demo 3, DEMO-RESULTS.json). |
| 5 | Field verification | **EXECUTABLE** | `verify_field` equality check executed; demo 2 FAILs the real v1 error value with reason recorded. |
| 6 | Deterministic extraction | **FIXTURE-ONLY** | Mechanism runs (probe (a)), but `_EXTRACTORS` holds exactly four rules written for the R60 change record's phrasing (tools.py:61–66); every other field/document is NOT FOUND by construction. |
| 7 | Model independence | **NOT PRESENT** | Subject pinned (`MODEL = "qwen/qwen3.8-27b"`, Groq shell-out transport) and the tools' data plane is the Qwen trial's corpus/fixtures/ground truth (§2). |
| 8 | Live shelf retrieval | **NOT PRESENT** | `shelf_lookup` reads the frozen index corpus (BY_ID) and a local MANIFEST.md by absolute home path; the package itself claims no live-shelf access. |
| 9 | Obligation lifecycle | **FIXTURE-ONLY** | `receipt_worksheet` computes CLOSE/REJECT + OPEN/CLOSED for the single T09 fixture obligation; T07 is specification only; there is no lifecycle engine and no state store — state is a string in a returned dict. |
| 10 | Role enforcement | **NOT PRESENT** | T04's enforcement is behavioural — the tree loads the boundary table, "the refusal is still the model's" (V2-PACKAGE limitations; PROCESS-TREES T04). No code mechanically prohibits an out-of-role action. |

**Counts: EXECUTABLE 4 · FIXTURE-ONLY 2 · NOT PRESENT 4** (of 10).

## 5. MODEL-NEUTRAL CHANGES — to be DECLARED and VERSIONED at Stages 2/3

Declared only, per the tasking. Nothing below has been changed;
each item names the coupling (§2) it retires. Any adoption of these
produces new, re-hashed artefacts — the pinned V2 package is not to
be edited into neutrality in place.

1. **Corpus interface.** Replace `tools.py`'s `import run_ab` /
   `BY_ID` binding (:19–21) with the pilot's pinned source set
   supplied as a versioned input (Stage 0 manifest), so the tools
   import no trial runner and execute no trial module level.
2. **Manifest location.** Replace the absolute home-path
   `MANIFEST_MD` (tools.py:22) with the pilot's own frozen manifest
   inside the pinned input set; live-shelf reads are excluded by the
   plan in any case.
3. **Extractor rule set as data.** Move `_EXTRACTORS`
   (tools.py:61–66) out of code into a declared, versioned rule set
   covering the pilot's actual documents; a field with no rule
   remains NOT FOUND, by declared design.
4. **Fixtures and ground truth as pilot data.** `EXPECTED_RECORD`,
   `OBLIGATION_T09`, `RECEIPTS` and the `P_T01…P_T09` pack
   definitions move from `run_ab.py` module constants into declared
   pilot fixtures with hashes (Stage 0), identical for every subject.
5. **Subject boundary in the trees.** `PROCESS-TREES.md` specifies
   [MODEL] steps as Qwen's. A versioned revision (or a declared,
   versioned interpretation note) must restate them against the
   Stage 2 subject interface: declared step inputs in, structured
   result out, raw request/response captured.
6. **`reference_insert` provenance rule.** Declare the acceptance
   set explicitly — which verification states may enter which field
   classes, and whether insertion must establish that a result was
   actually issued by a tool (the v2 code cannot distinguish an
   issued result from a caller-built dict, §3). Any tightening is a
   declared tools revision, re-hashed and re-qualified; the pilot
   must not silently inherit v2's allowlist and call it verified
   provenance.
7. **Execution record ownership.** The canonical record (Stage 3)
   must own the tool-call log; in v2 the log exists only because
   demo code chose to keep one, and `reference_insert` — the
   ledger-emitting operation — is not in it (it takes no
   operation_id). Declare the logging contract for every tool,
   including insertion.

## Scope notes

- Qualification covers the pinned `v2/` package and its import chain
  (`run_ab.py`). The `v21`–`v248` directories are separate, later,
  non-pinned revisions; they were searched for drivers (§1) and
  cited once as corroboration (§3), but not qualified.
- The probe ran in this environment, where the pulse-bridge index
  corpus and the live shelf manifest exist at the absolute paths the
  code expects. That is itself a qualification finding: the package
  is executable **here**, on this machine's home tree — portability
  to any other environment is NOT ESTABLISHED.
- No shelf file was modified; the only writes are this report, the
  scratch copy, the probe script and its captured output, all under
  `~/workspace/duenna-letters/`.
