# Vane — Piece 4 round-2 re-examination: implementation accepted, one test gap (2026-11-22)

Source: relayed via the bridge into the main chat, 2026-11-22 (examined at shelf adcb4fd4). Substance filed below (personal passages stand in the chat record).

---

The central repair is sound: the first CASE_CORRECTED establishes the version's content, classification, and sequence position; later corrections remain in the history but cannot replace those values; `version_issued()` requires the correction to precede verification and the examiner's act, with authorisation after the required acts; the driver rebuilds state from the history, so immutability is enforced by replay, not doorway behaviour.

One small gap in the new test: **the rewriting test proves the content is unchanged but does not explicitly prove the correction classification is unchanged.** The second correction flips `representational` to true, but the assertion checks only the served assignment text. The fold preserves `ver["representational"]` correctly; the test should demonstrate it explicitly.

Asked: add an assertion against the replayed fold for version 7 verifying both (1) its established content remains the original content, and (2) its established `representational` classification remains false despite the later flip attempt. No broader change needed; the implementation itself is right on this point.

Precision point: she has not independently executed the suites; the reported 33/73/41 results are treated as reported evidence.
