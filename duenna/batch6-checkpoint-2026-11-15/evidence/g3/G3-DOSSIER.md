# GATE G3 DOSSIER — SE-1…SE-7 (C6-10)

Structural inspection + adversarial demonstration record for
the supervisor properties SE-1…SE-7 (Rev 26 §3.5; Harness
§4.5). Tools file under inspection: build/tools/pilot_tools.py
(sha256 df1045f7…, the pinned PILOT-TOOLS-01 copy). Line
numbers cite that file. Behavioural pairings cite the executed
gates; no property below rests merely on non-invocation —
each structural note is paired with an executed demonstration
or a cleared prior demonstration carried by pin citation
under Alex's C6-0a Gap 2 ruling.

## SE-1…SE-6 — structural inspection, paired with Gate G1

**SE-1 — Sole issuer.** Operation identifiers are minted in
exactly one place: `PilotTools._invoke` (line 204) increments
`self._op_seq` and forms `op-<n>`; every tool entry point
funnels through `_invoke`. Registry entries are created at
exactly one call site: `self.registry.register(...)` inside
`source_extract` (line 242), on that tool's TOOL_RETURNED.
Nothing else in the file calls `register`, `consume`, or
`consume_citation` outside the insert paths. *Behavioural
pairing (G1):* a presentation claiming the guessable next
sequence number (op-4, never issued) was refused NO_ISSUANCE.

**SE-2 — No caller-supplied provenance.** A reference_insert
presentation is a closed tagged union, validated by
`_presentation_form` (line 248): the extracted form is exactly
{form, operation_id}; the carried form is exactly
{form, citation{event_id, payload_sha256}}. Any other shape
refuses PRESENTATION_FORM (line ~292) before any registry
access. The carried path additionally requires the citation to
resolve to a STEP_PROGRESS produced artefact whose recorded
payload hash equals the citation, whose producing step's
CHECK_RESULT is PASS, in the same tree and step context
(`_insert_carried`: NO_CITATION / CITATION_CONTEXT_MISMATCH /
CITATION_FIELD_MISMATCH / CITATION_HASH_MISMATCH /
CITATION_CHECK_FAILED). A caller can present identifiers, but
every provenance fact is recomputed from harness-held state.
*Behavioural pairing:* Batch 3 replay (C6-3) — invalid carried
provenance (hash), non-null carried source_ref, and unpaired
INSERT_REFUSED fixtures all fail closed; G1 S1/S2.

**SE-3 — Registry unreachable by the subject.** The
IssuanceRegistry is "Private harness state (§3.3)" (class
docstring, line 105); its only mutations are register /
consume / consume_citation, all called from harness-side tool
code. The subject's entire interface is the adapter contract:
`complete(step_inputs)` with the closed key set
{correlation_id, tree_id, step_id, messages} (Batch 5 adapter;
C6-5 stub contract) — the subject emits model text only and
receives classified results; no message content is ever
interpreted as a registry operation. *Behavioural pairing
(C6-5):* the real adapter against the stub service withholds
raw output and classifies by identity; the subject cannot
address the harness at all except through a step invocation
the harness itself issued.

**SE-4 — Insert-time and replay recomputation.** On the
extracted path, after the registry checks,
`_insert_extracted` recomputes against the *current* corpus
before consuming (line ~330, "recomputation at insert time
(§3.3, Harness §4.2)"): section presence (SOURCE_GONE), the
snapshot's stated hash vs the current text (SNAPSHOT_MISMATCH),
the presented source hash vs the entry's (SOURCE_HASH_MISMATCH),
then a fresh rule application whose outcome, rule, value, and
evidence must each match the entry (RECOMPUTE_<outcome> /
RULE_MISMATCH / VALUE_MISMATCH / EVIDENCE_MISMATCH). Only then
is the entry consumed and the LEDGER_ENTRY emitted.
*Behavioural pairing (G1):* S4 — a genuine extraction whose
source was perturbed after issuance refused SNAPSHOT_MISMATCH
with the recomputed hash in the refusal detail; the examiner's
Step 3 replay (C6-3, C6-8) independently recomputes every
invocation.

**SE-5 — Single use.** `consume()` (line 139) flips the
entry's consumed flag, called only on a successful insert;
the ALREADY_CONSUMED check precedes recomputation, so a
replay is refused even against an unchanged corpus. Citations
are likewise consumed once (CITATION_CONSUMED).
*Behavioural pairing (G1):* S3 — first insert succeeded,
identical replay refused ALREADY_CONSUMED; the whole battery
record contains exactly one LEDGER_ENTRY.

**SE-6 — Sterile refusal.** Every refusal flows through the
single `refuse()` closure in `reference_insert` (line ~280):
it emits a GOVERNANCE_EVENT of kind INSERT_REFUSED carrying
the full claimed-vs-recomputed detail and returns
{refused: true, reason, claimed, recomputed} — no value, and
no LEDGER_ENTRY (the module header states it at line 64:
"refusal emits NO LEDGER_ENTRY and returns NO value (SE-6)").
*Behavioural pairing (G1):* all five refusals in the battery
record carry the refusal object, emit INSERT_REFUSED, return
no value, and write no ledger entry — re-derived by the
examiner in test_g1.py.

## SE-7(i)–(iv) — demonstrations executed for this gate

**(i) OS-boundary custody (executed 2026-11-15, scratch
room).** Run G3VAULT-20261115-001, inside the genuine harness
boundary (scratch launcher → pilot-harness): attempts to
create a file in commitments/, overwrite the run's own START
receipt, append to issuance-record.jsonl, and delete the
START receipt **all failed with EACCES** — the inability is
the OS's (the store is pilot-supervisor-owned, mode 700),
not the code's politeness. The harness contains no write path
to commitments/ (its only store writes are its own run
directory). Artefacts: scratch/g3/runs/G3VAULT-20261115-001/
artefacts/vault-attempts.json; the run's START + TERMINAL
receipts in scratch/g3/commitments/ (Step 0 verified).

**(ii) Supervisor independent computation + falsified pin
block (executed 2026-11-15, scratch room).** Run
G3FALSE-20261115-001: the harness variant wrote a RUN_STARTED
pin block carrying a falsified pin (ffff…). The supervisor's
START receipt commits the falsified block's actual bytes —
genesis_sha256 == pinned_input_block_sha256 ==
34079eb6e9a65995…, recomputed by the examiner from the
record's RUN_STARTED payload and matched (Step 0 PASS: the
custody chain is internally consistent). No issuance path
accepts a value from the harness; every committed value is
the supervisor's own computation from its read of the file.
The falsification is then a replay finding, exactly as
designed: the falsified pin appears in no pin authority or
freeze record, while the genuine stub pin appears in the
companion run's block. Artefacts: scratch/g3/runs/
G3FALSE-20261115-001/run-record.jsonl + its START/TERMINAL
receipts.

**(iii) Crash separation (executed at C6-9, Gate G2).**
G2TORN-20261115-001 (mid-append SIGKILL; record ends in 112
genuinely torn bytes; CRASH receipt over the bytes as they
lie; no TERMINAL) and G2BETWEEN-20261115-001 (between-steps
crash). Examiner verification: scratch/g2/
G2-VERIFICATION-REPORT.md (12/12).

**(iv) Examiner issuance-record verification + planted-
receipt negatives (executed in test_g3.py on scratch
copies).** Step 0 verifies every receipt against the
issuance record by construction. Negatives, all rejected as
custody findings: (a) the TERMINAL entry removed from a
copied issuance record → the genuine receipt is reported
absent from issuance; (b) a planted TERMINAL receipt whose
bytes differ from the issued receipt (issuance untouched) →
digest mismatch against the issuance entry; (c) a planted
CRASH receipt beside a genuine TERMINAL → TERMINAL/CRASH
coexistence refusal. Artefacts: the G3VAULT set in
scratch/g3/ + test_g3.py output.

## SE-7(v)–(ix) — carried by pin citation (Gap 2 ruling)

Alex's C6-0a ruling (ALEX-C6-0A-2026-11-14): SE-7 (v)–(ix)
ride into G3 by pin citation where the launcher pin is
unchanged. C6-0b verified the condition live: the installed
launcher is sha256 9ea9b615a22bc7ea035d375fd3dd17c8fb5c7e8cd
c9861a152882e382a637722 (owner root:pilot-supervisor, mode
4710), identical to the C4-12 pin record
(C6-0B-PIN-VERIFICATION-MANIFEST-2026-11-14.md). The Batch 4
checkpoint is CLEARED (adjudication sha256 79cbadea0b60f8f5…;
crosswalk erratum sha256 77d20e5f61e0aab7…; filings shelved @
905b9eb3). The demonstrations cited, from the Batch 4
checkpoint bundle (ssh-door/batch4/checkpoint-bundle/ +
checkpoint-evidence/):

- **(v) Launcher separation** — B4INVOKE-20261114-001 (mid-run
  invocation attempt refused at the OS boundary, run's own
  evidence shows the attempt changed nothing) + the
  checkpoint's invocation/identity evidence.
- **(vi) Descriptor isolation** — B4FDS-20261114-001…004
  (hazard arrangement: inherited writable descriptor probed
  on every fd; retained-descriptor destinations recorded;
  negative arrangement refused at Stage 1).
- **(vii) Group separation, setuid preconditions, capability
  state** — the checkpoint's probe evidence (setuid probe,
  group read-backs, CapEff/CapPrm/CapAmb zero read-backs for
  both dropped processes, induced nonzero fail-closed cases).
- **(viii) Launch handshake** — the checkpoint's test-hooks
  fault-injection evidence (Window 1 + Window 2 + parent-
  death variant; hooks compiled out of the production
  launcher, re-verified at C6-6/C6-9 by strings scan).
- **(ix) Identity continuity** — the checkpoint's launch-
  evidence comparisons (identity records read-backs across
  the launch; Part B launch-evidence comparison PASS in the
  Batch 4 build record).

## Crosswalk

Every SE-1…SE-6 note above cites a code path in the pinned
tools file (verified mechanically by test_g3.py) and an
executed behavioural pairing. Every SE-7 item cites either
artefacts executed for this gate or the G2 gate (i–iv), or
cleared Batch 4 artefacts under a verified unchanged pin
(v–ix). test_g3.py is the crosswalk check.
