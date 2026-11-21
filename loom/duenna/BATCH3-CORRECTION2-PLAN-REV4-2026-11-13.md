# BATCH 3 CORRECTION — ROUND 2 PLAN, REVISION 4 (2026-11-13)

**Standing:** Revision 3 (87db21a1) inspected by Alex 2026-11-13
(PB-ID pb-mwfu91f2-h-l89e): R2's construction accepted in
direction; ONE omission found in cross-checking the binding
contract against the actual driver. This revision amends **R2
only**, at the two points named. R1, R3, items 2–4 and the rest of
R2 stand exactly as written. Remmy verified both points in the
artefacts before revising, and additionally swept the driver for
any other symbol consumed from a locally pinned module: the
inventory below is now complete (utc_now is driver-local;
pilot_jcs is reached only through pilot_record/pilot_tools, as
Revision 3 already states).

## R2 amendment 1 — the consumed-symbol inventory is complete

- `pilot_record.materialise_ledger` joins the binding list. The
  complete list is now: `pilot_record.RunRecord`,
  `pilot_record.canonical`, `pilot_record.sha256_hex`,
  `pilot_record.materialise_ledger`,
  `corpus_source.CorpusSource`, `pilot_tools.PilotTools`,
  `stub_subject.StubSubject`.
- The dynamic import at driver line 317
  (`__import__("pilot_record").materialise_ledger(...)`) is
  removed; the ledger materialisation at run close calls the
  bound attribute.
- The greppable invariant is widened accordingly: the driver file
  must contain NO dynamic or name-based module resolution of a
  locally pinned module in any form — no `__import__`, no
  `importlib.import_module`, no equivalent name-based resolution
  — outside the bootstrap loader, whose own loading is by explicit
  verified file path (importlib file-location loading, which takes
  a path, not a name). The suite's invariant check greps for all
  three forms.
- The provenance identity report gains the corresponding result:
  the bound `materialise_ledger` `is` the attribute of the freshly
  verified pilot_record module object loaded by this bootstrap,
  asserted alongside the existing identities (P2 covers it).

## R2 amendment 2 — the subject is constructed inside the boundary

The scenario runner does not construct or inject a subject
instance. It passes only data into the driver: the stub script's
authority entry name (or path under the verified root) and the
subject configuration name. The driver, after preflight and after
the bootstrap has loaded and bound the verified modules,
instantiates the subject itself from the bound
`stub_subject.StubSubject`. The round-1 shape — the suite
constructing `StubSubject(...)` and handing the live object to the
driver's constructor — is expressly prohibited by the contract,
and the driver's constructor signature changes accordingly: it
accepts the script reference and configuration name, never a
subject object. The provenance report records that the subject
instance's class `is` the bound verified StubSubject class, as a
further P2 identity result.

Nothing else changes. No implementation until you approve this
revision.
