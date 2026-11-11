# CLAUDE — VERIFICATION REPORT: R60 REVISION RE-EXAMINATION

Received via Ben 2026-11-10 (Claude pulled the shelf himself at
commit 48d3f4b). Examiner: Claude, Duenna's primary independent
reviewer. His text as delivered:

---

I re-examined the R60 revision from `origin/main` at commit `48d3f4b`. The mutable-registry sabotage fails FX-R60h, as the implementer's addendum expected. But the revision doesn't close Correction B: the registry can still be rebound at module level, and the verdict check accepts the substituted result.

**Hashes checked**

All four revision files match the letter and the MANIFEST:
- `harness-r60rev.py` `6cb326ef…88ebd04`
- `results-r60rev.json` `c7068f05…1364712`
- `R60-REVISION-CHANGE-RECORD.md` `b31f966a…37b5d8e09`
- `R60-REVISION-UNRESOLVED.md` `5d809370…2b90c`

All 71 MANIFEST entries match their files. The v0.8 spec is `3e053efc…`, and the v0.10 spec is `9241a8b4…`, both unchanged.

**Re-run**

I ran the harness in an isolated copy. It gives 34/34 PASS, and its output matches `results-r60rev.json` apart from the Python version string. The 31 original IDs are preserved.

**Correction A: FX-R60f, PASS**

Removing the digest comparison fails FX-R60f alone. FX-R60d still passes, so the old fixture never reached the branch.

**Correction B: FX-R60g, PASS as far as it goes; not closed**

FX-R60g rejects an unrecognised procedure identity at construction. I didn't re-run the implementer's binding-removal sabotage.

**Bounded repair: FX-R60h, sabotage A caught**

- Replacing the `MappingProxyType` with a plain dict makes FX-R60h fail alone. The control run is clean.
- FX-R60h only checks that the in-place assignment is rejected. It builds the contract before the remap and then calls `run()` on the already-bound callable, so it doesn't test dispatch.

**What the revision still misses**

Rebinding the module-level name `PROCEDURE_REGISTRY` to a substitute bypasses the immutability repair entirely:

- After `harness.PROCEDURE_REGISTRY = {"REQ-I-3 preservation check": lambda p, s: s}`, a contract constructed afterwards dispatches to the substitute.
- For a tampered payload, it returns `preserved`.
- `validate_verdict` accepts that verdict. Its implementation hash comes from the original `_preservation_check` source, not from the callable that actually ran.
- No fixture catches this.

So the declared identity is not the executed procedure under global rebinding, which is the property Correction B was supposed to establish. I'd treat Correction B as open until a fixture covers that path, or the registry and the dispatched callable are bound together.

**Other notes**

- The change record's body still shows the superseded hashes `3c393fce…` and `f257fbd5…`. The addendum gives the current ones, but the record should be cleaned up.
- The `pinned=True` qualification and the R65 caller-supplied required set are still open. The four gaps are still open and untouched, and v0.10 is still NOT APPROVED.

---

Implementer's note on the hash mechanism (Remmy, from the
source, harness lines 702–783): `run()` computes the verdict's
implementation_hash from the dispatched callable
(`self._procedure_fn`); `validate_verdict` compares it against
the same contract's bound callable. Under rebinding, therefore,
the hash follows the SUBSTITUTE — the acceptance holds because
validation checks the contract's internal consistency, with no
trusted external reference for what the named procedure's hash
must be. Claude's central observation stands on the code as
written: construction reads the module global (lines 740/744),
so a prior rebind changes dispatch, and no fixture covers it.
Whether module-level rebinding is inside Correction B's threat
model is the adjudicator's call.
