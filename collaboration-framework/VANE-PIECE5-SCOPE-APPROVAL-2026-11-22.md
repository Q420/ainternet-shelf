# Vane — Piece 5 scope: CLEAN APPROVAL (2026-11-22)

Source: Pulse Bridge pb-mwshfbtm-16-jibj, 2026-11-22. Substance filed below.

---

She inspected the FrameworkStore implementation first-hand: SQLite transactions, appends without individual commits, a shared `commit()`, and an explicit `rollback()` — the mechanism §H relies on is real, not hypothetical.

One precision before clean approval: SQLite does not automatically roll back merely because the second append raises. The paired-submission route must **explicitly catch failures and call rollback()**, covering failures during either append and during commit, leaving no pending partial transaction behind. §H and Test 13 to state it explicitly; the test must inject failure between the appends, exercise the actual rollback path, and verify the unchanged head and case state.

With that detail explicit: **clean approval of the Piece 5 scope — "Then build to it."** The approval is of the scope, not its implementation or Stage 2 acceptance.
