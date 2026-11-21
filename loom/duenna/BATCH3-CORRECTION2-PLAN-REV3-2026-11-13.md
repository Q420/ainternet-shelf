# BATCH 3 CORRECTION — ROUND 2 PLAN, REVISION 3 (2026-11-13)

**Standing:** Revision 2 (9ada005c) inspected by Alex 2026-11-13
(PB-ID pb-mwfu67od-g-3c73): R1 and R3 APPROVED IN PRINCIPLE; items
2–4 previously accepted. This revision replaces **R2 only**, in
full. R1, R3 and everything else stand exactly as written.
Remmy verified the finding in the artefact: the driver body calls
the imported symbols directly throughout (RunRecord at line 277,
CorpusSource at line 120, canonical and sha256_hex at dozens of
call sites) — loading modules inside `run()` without an explicit
binding step would leave those names undefined or, worse, quietly
resolvable from somewhere else.

## R2 (replacement) — verified modules are loaded after preflight AND bound as the driver's dependencies

**Loading.** As in Revision 2: pilot_driver.py's module scope is
standard-library only (the `sys.path` insertion is deleted);
inside `run()`, the bootstrap derives the root from `__file__`,
hashes the authority against the embedded constant, verifies every
consumed file, and only then loads the locally pinned modules from
their exact verified paths by importlib file-location loading, in
dependency order (pilot_jcs → pilot_record → corpus_source →
rules_engine → pilot_tools → stub_subject). No name-based path
resolution occurs anywhere in the driver after module scope.

**The sys.modules rule, tightened as directed.** The bootstrap
refuses (PROCESS_MODULE_PRELOADED) if ANY pinned name —
pilot_jcs, pilot_record, corpus_source, rules_engine, pilot_tools,
stub_subject — is already present in `sys.modules` when it starts,
regardless of that entry's `__file__` or provenance. A matching
path proves nothing about the object. The only module objects the
run may use are ones this bootstrap freshly loaded from the
verified paths in this process; after loading each one, the
bootstrap registers it in `sys.modules` under its pinned name so
that dependent modules' own import statements bind the verified
object and nothing else.

**Binding contract.** The bootstrap returns a single dependencies
object holding the verified module objects. Before any step runs,
the driver binds the exact symbols it consumes from that object
into instance attributes, and every call site in the driver body
uses the bound attributes — the complete consumed-symbol list is:
`pilot_record.RunRecord`, `pilot_record.canonical`,
`pilot_record.sha256_hex`, `corpus_source.CorpusSource`,
`pilot_tools.PilotTools`, `stub_subject.StubSubject`. (The
canonicalise function the tools require is `pilot_record.canonical`
itself, passed explicitly to the PilotTools constructor as today;
pilot_jcs is consumed by pilot_record internally, its import
satisfied by the bootstrap's registration.) Two greppable
invariants hold of the finished artefact and are asserted in the
suite: the driver file contains no import statement naming a
locally pinned module outside the bootstrap loader, and no bare
reference to any consumed symbol name other than through its bound
attribute. No fallback import, no lazy re-import, no
name-based resolution is permitted anywhere in the run path; if a
bound attribute is somehow absent, the driver fails closed rather
than resolving the name.

**Consequence for the suite, stated openly.** The refuse-any-
preloaded rule cannot coexist with the round-1 suite's shape,
which imported the pinned modules in its own process for analysis
and then constructed drivers in that same process. Round 2
therefore executes every driver scenario in a **fresh interpreter
subprocess**, through a thin scenario runner (test tooling, pinned
by the round-2 continuation like the suite): the runner takes a
scenario configuration, constructs the driver, runs it, and emits
— beside the run record — a **bootstrap provenance report** (JSON)
recording, for each pinned module, its name, verified path and
sha256, and identity results computed in the run's own process:
each bound attribute `is` the corresponding attribute of the
verified module object the bootstrap loaded (RunRecord, canonical,
sha256_hex, CorpusSource, PilotTools, StubSubject), the tools
module's `extract` global `is` the verified rules_engine's
`extract`, and pilot_record's JCS binding `is` the verified
pilot_jcs module. The suite asserts on the records and on this
report from its own process, importing whatever analysis tools it
needs there — the artefact under test and the analysis no longer
share an interpreter.

**Evidence (each its own transcript line):**
- P1 provenance paths: every pinned module in the MAIN run's
  provenance report names its authority path and hash.
- P2 provenance identity: every identity result in that report is
  true — the objects the driver actually used are the verified
  objects, not merely files with the right names.
- P3 preloaded refusal: a dedicated script imports corpus_source
  in-process, then invokes the bootstrap — PROCESS_MODULE_PRELOADED
  refusal, no run directory created.
- P4 the poisoned-copy test from Revision 2 stands (a
  corpus_source.py that raises on import, staged ahead on
  `sys.path`, leaves the run unaffected).

No other text changes. R1's acyclic construction, R3's
INTEGRITY-FIXTURE-01, items 2–4, the N1–N4 negative tests and the
round-2 mechanics all stand. No implementation until you approve
this revision.
