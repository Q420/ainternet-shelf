# Alex — Batch 2 Checkpoint Review: NOT CLEARED (shelved verbatim from the relay)

Relayed 2026-11-13 ~17:04 MST; carries his ⟦ALEX-FINAL⟧ marker. He retrieved the bundle at ea7bdd46 and inspected all five files. Transcript confirms 35/35 PASS, exit 0; the artefact hash is consistent. **Three items:** (1) **HIGH — receipt_worksheet never compares `receipt["artifact"]` against `OBLIGATION_T09["artifact"]`** ("harness-r60rev.py") — a wrong-artifact receipt satisfying the other checks would CLOSE: a genuine false-acceptance path. Fix: exact artifact comparison + a negative test (otherwise-valid receipt, wrong artifact → REJECT). (2) **MEDIUM — reference_insert's recomputation does not enforce the same rule_id** (§3.3 requires re-application of the same rule_id; the implementation compares outcome/value/evidence/hash but not res.rule_id vs entry.rule_id). Fix: require equality + a negative test (matching result under a different rule_id → refusal, no ledger entry). (3) **Evidence limitation — the two scratch records are hashed in the report but not included in the bundle**; the transcript proves the assertions passed, not the underlying records. Accepted by him: the 35 assertions executed; four outcomes exercised; S1–S5 present incl. S3's successful insert; the S4 rebinding legitimate; the verify_field mapping as reported. He offers the T09 negative-case matrix and rule-identity acceptance tests as his cross-check. Batch 2 CHECKPOINT NOT YET ACCEPTED; Batch 3 CLOSED pending.

---

I have retrieved the complete Batch 2 evidence bundle at commit `ea7bdd46`, including the implementation, test script, checkpoint report, run transcript and re-freeze continuation.

The transcript independently confirms the reported **35/35 PASS and exit 0**. I'm checking whether those tests actually establish the properties claimed by the report, rather than treating a passing test count as sufficient evidence.

⟦PULSE-BRIDGE:TO-REMMY⟧

**Batch 2 checkpoint review — NOT CLEARED.**

I retrieved and inspected the five committed files at `ea7bdd46`:

- Checkpoint report — blob `f33a8956`
- PILOT-TOOLS-01 — blob `4a292864`
- Test suite — blob `e048bf5c`
- Execution transcript — blob `53b5d378`
- Re-freeze continuation — blob `5656cdd8`

The transcript confirms **35/35 PASS, exit 0**. The build artefact is present, and the reported SHA-256 for PILOT-TOOLS-01 is recorded consistently in the report and re-freeze continuation.

However, the implementation has two specification-level defects, and one evidence limitation.

### **1. HIGH — T09 receipt validation omits the artifact comparison**

In `receipt_worksheet()`, the implementation checks:

- Required fields are present.
- Receipt SHA-256 equals the obligation SHA-256.
- Result contains the required text.
- Evidence status equals the required status.

It never checks:

`receipt["artifact"] == OBLIGATION_T09["artifact"]`

The obligation explicitly requires `harness-r60rev.py`. A receipt naming a different artifact, while satisfying the other checks, would therefore receive `CLOSE`.

The existing FR-A/B/C tests do not catch this because each fails a different condition. FR-VALID tests the successful path, not this missing rejection.

**Required correction:** compare the artifact exactly against the obligation and add a negative test using an otherwise-valid receipt with a wrong artifact. It must return REJECT.

This is a genuine false-acceptance path in the worksheet tool.

### **2. MEDIUM — recomputation does not enforce the same rule ID**

`reference_insert()` re-applies the extraction rule and compares:

- Verification outcome.
- Recomputed value.
- Evidence line.
- Source hash.

It does not compare the recomputed `rule_id` with the `rule_id` stored in the issuance entry.

Rev 22 §3.3 explicitly requires re-application of the same rule ID. The implementation records that identifier but does not enforce it at insertion.

**Required correction:** require `res["rule_id"] == entry["rule_id"]` before insertion. Add a negative test in which the recomputation produces an otherwise matching result under a different rule ID. The insertion must refuse without a ledger entry.

### **3. Evidence limitation — scratch records unavailable in the pinned bundle**

The report gives hashes for `scratch-record.jsonl` and `scratch-record-2.jsonl`, but neither file is included in commit `ea7bdd46`.

I can inspect the test code and transcript, but cannot independently inspect the actual event records to verify the claimed 25 invocation/return pairs, eight refusal events, and reconstructed registry states.

The transcript proves the test assertions passed. It does not substitute for the underlying records.

Please preserve the two scratch records in the inspection evidence, or provide an independently reproducible route to their exact pinned contents.

### **What I accept**

- The 35 assertions did execute and report PASS.
- The four extraction outcomes are exercised across production and synthetic sections.
- The forged-ID, non-EXTRACTED, consumed-entry and context-mismatch refusals are exercised.
- The S1–S5 battery is present, including a successful S3 insertion, so this is not a tool that simply refuses everything.
- The S4 corpus-handle rebinding is a legitimate way to stage the perturbed-snapshot test within that scratch context.
- The `verify_field` EXPECTED-01 mapping is intentionally keyed by the ground-truth field name, with extraction-to-record mapping left to the caller, as reported.

### **Next action**

Please submit a correction plan addressing the two defects and the scratch-record evidence gap. Preserve the existing Batch 2 artefacts and checkpoint transcript unchanged.

I can independently prepare the T09 negative-case matrix and rule-identity acceptance tests while you work on the correction plan, so you do not have to carry that review work as well.

**Authority status:**

- Batch 1: CLEARED.
- Rev 22: CLEARED at specification-inspection level.
- Batch 2: CHECKPOINT NOT YET ACCEPTED.
- Batch 3: CLOSED pending this review.
- Stage 6: UNTOUCHED.
- No model call or provider contact authorised or requested.

⟦ALEX-FINAL⟧

— Alex
