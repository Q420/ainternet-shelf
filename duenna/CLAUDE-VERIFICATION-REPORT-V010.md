# CLAUDE — VERIFICATION REPORT, D3 v0.10 RE-EXAMINATION

*Saved verbatim from Ben's relay of Claude's window, 2026-11-10
(~15:08 PST). Claude pulled the evidence himself from
github.com/Q420/ainternet-shelf (clone at commit 9b97219a) under
the pull letter (CLAUDE-PULL-LETTER-V010-REEXAMINATION.md). This
file is the relayed text as received, including his working
narration; the dispositions are in the structured report at the
end.*

---

I'll pull the v0.10 evidence from the shelf repository, starting with a fresh clone.

The `gh` clone failed because this session doesn't allow GraphQL. I'll attach the repository through the session's repo tool instead.

The repository is cloned. Next I'll check the file hashes against the MANIFEST and the hashes given in the letter.

The hash prefixes match the letter. I'll now check every MANIFEST entry against the files in the clone, not just the ones I was asked about.

All 59 MANIFEST entries match their files. Next I'll diff the v0.10 spec against the v0.9 seed, since the letter claims everything from "Source of record:" onward is identical.

The diff output looks cut off after the header. I'll print the full remainder to check whether anything changed past the header.

Only the header differs. The spec body from "Source of record:" onward is byte-identical to the v0.9 seed. Next I'll re-run the v0.10 harness in an isolated copy and compare its output with the delivered results.

The re-run matches the delivered results, and all 31 fixture IDs are the same as in v0.9. Next I'll read the R47, R60, and R65 mechanisms in the v0.10 harness.

The R47 mechanism now reads trigger content. The fold records it, and the mutation control shows the record changes when content is removed. But the content never affects the outcome, so the "content fails" variant is covered only by that same invariant, not by a fixture of its own. Next, R65 and R60.

The R60 trio and its rejection checks look real. However, the corrupted-payload fixture (FX-R60d) fails through a `corrupt` flag the artefact sets itself, before the digest comparison runs. I'll check whether any fixture reaches the digest-mismatch branch, and whether R61 uses the same procedure.

No fixture sends a mismatched payload into `CheckerContract.run` without the `corrupt` flag, so the digest-mismatch branch is never exercised. FX-R61 also tests its own copy of the logic, not `_preservation_check`. I'll test this directly by running sabotaged copies of the harness.

Sabotage results: removing the digest comparison (S1) went undetected, so the executable preservation check's rejection path is not tested. The other four sabotages each fail their own fixture. Next I'll read the v0.10 change record and the unresolved-items record, then check the regression conditions.

The change record says the repair is evidence rather than appearance, and that a repair which can't be made to fail by removing its mechanism is only appearance. The digest-mismatch branch fails that test. Next I'll confirm the regression items: fixture IDs, gap coverage, the execution contract, and what the v0.9 ledger required for R60 and R65.

I've examined v0.10 from the shelf repository. R65 passes and R47 passes in a narrow form. R60 fails as a whole: the trio stamping and its rejection hold, but the executable preservation check's mismatch rejection is never tested.

**What I pulled and verified**

- I cloned `Q420/ainternet-shelf` (commit `9b97219a`) and checked all 59 MANIFEST entries against the files. All match, and no entries are missing.
- Full hashes I relied on:
  - v0.10 spec `9241a8b40f93b4e303b03ba5d5f31d244c3c361769263adedb7393626e6acd2e`
  - v0.10 change record `b8d769a53551d16c193f7f4d34a8b38717a9d26a72b8f9ea3b1c4e25dd8dbd54`
  - v0.10 traceability `931da270f422308faa3ac74f1cc72b515a6dab4affda91b2575e1ee307ef1333`
  - harness v2.1 `efe69df64a964bf5fb45cc2234c539908e3b7e600cd209de5867ccf0ad78ee6c`
  - fixture results `11b42cb4a740647d5788e8ea7eebe03a5593848c9d4ace79cdff4c03c88a9821`
  - fixture register `772c394d25de14b77a461fe3f3d23032b3c028131b7966c1c215ad5da1a9a3a1`
  - results JSON `ad4dc13754c543520dea2b93c80165df85595a18e873438f2d600779e355ce38`
  - unresolved items `b9e8e457c4858def403f8a9321bf5e16ef537015eb102c76ec3659776efecb33`
  - v0.8 spec `3e053efc97d876d50f649eb0b4c8c740ab6085314aa54f9132fdf33e243d97d4`
  - v0.9 spec `ac2a2484dd4e170948f868d4ac1680221fbcd3a905c75d1d2da21f4d0d0485dc`
  - execution contract `c7e689011312c32e4a69211984b37264c107a88a12b3f27c6da8cbcd9b07dec3`
- I re-ran the harness in an isolated copy. It gives 31 PASS, and its output matches `results-v010.json` apart from the Python version string. The fixture IDs are the same 31 as in v0.9.
- The v0.10 spec differs from v0.9 only in the title and status header. The body from "Source of record:" onward is byte-identical.

**R47: PASS, narrow**

- The fold now reads each entry's `content_predicates` and returns them as `examined_trigger_content`.
- Mutation control: removing the content from the trigger changes the examination record. Sabotage S4, which removes the examination, fails FX-R47b.
- Admitting the content into the running set (sabotage S5) also fails FX-R47b.
- Caveat: the examined content never affects the outcome. Only qualifying content is tested. No fixture covers a trigger whose content fails. By construction, that trigger can't pass either.

**R60: FAIL (partial repair)**

- The trio is stamped on verdicts: version, implementation hash, and input identity. `validate_verdict` rejects a forged procedure, a missing or altered implementation hash, and a missing input identity or version. FX-R60b exercises each rejection. Sabotage S2, which disables the implementation-hash check, fails FX-R60b.
- The executable preservation check is `_preservation_check`, a digest comparison. No fixture sends a mismatched payload into `CheckerContract.run()` without the `corrupt` flag, which short-circuits the check. Sabotage S1 removes the digest comparison and every fixture still passes, so the rejection path is not exercised.
- FX-R61 tests its own copy of the logic and never calls `_preservation_check`.
- `pinned=True` is still caller-supplied, as Vane noted in the ledger. The repair doesn't address that.

**R65: PASS**

- Each required reference is deleted in turn, and an empty references dict is tested. The validator rejects missing, unexpected, and `components_present`-mismatched references.
- Sabotage S3, which removes the missing-reference check, fails FX-R65 and nothing else.
- Caveat: the values are checked against the test's own constants. Authenticity of the underlying records is not established, as Vane also noted.

**Regression conditions**

- v0.8 immutable: confirmed, the file matches its MANIFEST hash.
- 31 fixture cases with the same IDs: confirmed.
- The four gaps (R38 (v)/(vi), R48, R53, R55) are untouched and still open: confirmed. The harness has no fixture for any of them, and the spec body is unchanged.
- UX-1…UX-5 unchanged and no status changes: confirmed. The body is byte-identical to v0.9.
- EXECUTION-CONTRACT untouched: it matches its MANIFEST hash.
- No Stage 2, v0.10 not approved: the header says NOT APPROVED. The "no Stage 2" claim rests on the package's own statements.
- S2: I did not reopen it. My v0.9 classification was FAIL, Vane's was clarification, and the adjudication treats it as a clarification.

**Implementer-run evidence**

Sabotage S1–S5 are my own variants. S2, S3, S4, and S5 correspond to the implementer's M2, M3, and M1, and each fails exactly its own fixture. S1 is the one the implementer did not run, and it is the gap that matters.

**Not pulled or not verified**

- I did not read `D3-V010-TRACEABILITY.md` or `FIXTURE-RESULTS-V010.md` in full, so I haven't checked their claims. The change record's sabotage claims are consistent with what I reproduced.
- The four v0.9 examination reports: I used the ledger's summary of Vane's and my own findings, not those reports directly.
- Alex's adjudication letter and the scope ledger in `~/workspace` are not in the shelf, so I can't check those authorisations.

The R60 gap is small and easy to close: add one fixture that sends a payload with a wrong digest and no `corrupt` flag through `CheckerContract.run()`, and confirm it returns a failure path. Sabotage S1 would then fail.

---

*Remmy's independent confirmation (2026-11-10 ~15:10): read in the
source (fixtures-v010/harness.py) — CheckerContract.run() checks
the `corrupt` flag (line 734) before the digest call (line 736);
FX-R60d's only invalid-artefact case carries the flag (line 814);
no fixture reaches the digest-mismatch branch (lines 737–738);
FX-R61 uses its own local preservation_outcome() and never calls
_preservation_check. Claude's mechanism is confirmed in full.
Dispositions stand as examiner findings; adjudication is Alex's.*
