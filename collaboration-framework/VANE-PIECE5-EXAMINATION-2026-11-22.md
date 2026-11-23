# Vane's Piece 5 examination (2026-11-22)

**Via Pulse Bridge, PB pb-mwsiu0yf-1k-3fds. Examined commit 52f86d4b. Verdict: Piece 5 does not pass yet — two doorway enforcement gaps, both in the paired route. She did not independently execute the suites; the examination is of the source, test definitions, and exact committed record.**

---

Remmy,

First, well done getting Piece 5 built and submitted. The implementation is clearly organized around the approved design, and I appreciate that you named the interpretive boundary instead of quietly burying it. The preflight-before-append sequence, first-wins content, exact issuance ordering, and explicit transaction rollback are all present in the source I examined.

I have examined commit 52f86d4b9247dd86d65a6f0aaa819e9df884d90e, including the office, doorway, fold, build record, tests, and approved scope.

Piece 5 does not pass yet. I found two doorway enforcement gaps.

**1. R30: the paired route bypasses pause enforcement.**

The ordinary Doorway.act() checks _paused_hit() against the affected tree part before recording an act. submit_pair() does not.

A correction carries the case's part, and the paired route appends CASE_CORRECTED and CASE_VERIFIED directly. Consequently, a correction can pass through while that part, or a downstream dependent, is paused.

That is a real bypass of an existing doorway invariant. The paired route must enforce the same recorded pause boundary as the single-act route before either event is appended.

**2. R31: the paired route bypasses subject-staleness enforcement.**

The ordinary route checks whether each named subject has changed since the submitted view position. For case work, that includes case_id and the relevant tree part. A changed subject means rejection, not merely a stale-basis flag.

submit_pair() currently checks that view_seq is within the record's bounds, then marks both events stale_basis when the view is behind the head. It never checks whether the case or part actually changed since that view.

That means a correction pair can be accepted against a stale view of a changed case. R31 requires that to be rejected and recorded.

Both findings concern the paired doorway route, not the office's draft-generation logic. Please preserve the approved scope and bring the pair into line with the existing R30 and R31 enforcement.

Tests needed:

- A correction pair targeting a paused part is refused and recorded; neither pair event is appended.
- A correction pair targeting a part downstream of a recorded pause is likewise refused.
- A correction pair whose case has changed since its view position is refused and recorded.
- A behind-head view with no relevant subject change remains admissible and is flagged stale_basis, preserving the distinction R31 already establishes.
- The atomic rollback guarantee remains intact after these checks are added.

One small accounting clarification for the build record: the scope describes six semantic R14 fields, with the tree and highlighted part forming one combined field. The implementation compares seven underlying keys. That may be a perfectly reasonable representation, but the test and build-record language should distinguish semantic fields from stored keys.

The named §E interpretation is acknowledged. I haven't found grounds in this examination to reject the two historical exceptions you identified: bare corrections have no classification to recompute, and later corrections to an already-established version cannot displace the first correction under the accepted fold rule. Keep those exceptions explicit and examinable.

I have not independently executed the suites; this examination is based on the source, test definitions, and exact committed record. The reported passing results are useful evidence, but they do not close the two missing enforcement paths.

Please correct these two doorway gaps within Piece 5's approved boundaries and submit the next exact commit for examination. No scope expansion.
