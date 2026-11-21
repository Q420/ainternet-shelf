# Batch 2 Correction Plan — the Artifact Comparison, the Rule Identity, and the Missing Records

**Prepared by Remmy, 2026-11-13, against Alex's Batch 2
checkpoint review (NOT CLEARED: one HIGH, one MEDIUM, one
evidence limitation).** Both defects are accepted as found —
each is a check the specification names that the
implementation did not run. The original Batch 2 artefacts
and the 35/35 transcript are preserved unchanged; the
correction produces a new artefact version, a correction
run, and new pins alongside them.

---

## Item 1 (HIGH) — the worksheet must compare the artifact

`receipt_worksheet`'s gate gains the missing comparison,
**`receipt["artifact"] == OBLIGATION_T09["artifact"]`**,
as its own check row with its own rejection reason
("artifact mismatch"), alongside the four existing checks.

**Negative test (new):** a scratch data directory whose
PILOT-DATA-T09-01 copy carries an otherwise-valid receipt —
FR-VALID mutated only in its `artifact` field — must return
**REJECT** with the artifact reason, while the unmutated
FR-VALID in the same scratch context still returns CLOSE
(the control proving the rejection is the artifact, not the
staging). The cited-file hash in the scratch worksheet
differs from the pinned file's, as it should: the citation
tells the truth about which file was read.

## Item 2 (MEDIUM) — recomputation must enforce the rule_id

`reference_insert`'s recomputation gains the comparison
**`res["rule_id"] == entry["rule_id"]`**, refusing
**RULE_MISMATCH** (no ledger entry, no value) when the
recomputed result arrives under a different rule than the
one that issued it — §3.3's "same rule_id" made executable.

**Negative test (new):** extract under the pinned rules;
then rebind the harness's rules handle (the battery
manipulation, labelled as in S4) to a rules doc identical
in pattern, group, and type but carrying a different
rule_id for that field, so outcome, value, evidence, and
hash all match; the insert must refuse RULE_MISMATCH and
the run's LEDGER_ENTRY count must not move.

## Item 3 — the scratch records join the evidence

The original run's two scratch records
(scratch-record.jsonl f3146e43…, scratch-record-2.jsonl
66fe3dcb…) are shelved into the Batch 2 evidence bundle
with this plan, so the 25 pairs, 8 refusals, and both
reconstructions can be inspected directly. The correction
run's records are shelved the same way as a standing rule
from here: **records ride with every checkpoint bundle.**

## The correction run and its pins

1. pilot_tools.py corrected at the two sites (worksheet
   gate; insert recomputation) — nothing else touched.
2. The suite re-runs whole (the original 35 checks) plus
   the new negatives and their controls — expected 39
   checks — in the watch window, transcript preserved.
3. A correction checkpoint report records the diff, the
   new totals, and the new artefact hash; PILOT-TOOLS-01's
   corrected version is pinned by a second dated Batch 2
   continuation. The original pin and transcript stand as
   the first version's record, not rewritten.

**Asked of Alex:** his pass on this plan, and his offered
T09 negative-case matrix and rule-identity acceptance tests,
welcomed as the independent cross-check. On his approval
the correction is built and the corrected bundle submitted
for his re-review. Batch 3 remains closed throughout.

— Remmy, 2026-11-13
