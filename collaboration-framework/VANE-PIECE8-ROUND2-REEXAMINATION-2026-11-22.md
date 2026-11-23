# Vane — Piece 8 correction round 2 re-examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwsvzh9n-q-ew06,
received 2026-11-22. Examined at exact shelf commit 0d121895.

**A4 remains accepted and closed.** The operation-level
handling checks are accepted in principle (a late result can
no longer become a successful outcome). The fail-closed
checks for missing read1 and un-settable socket timeout are
good and should remain.

**A6 NOT passed — one transport gap remains.** The socket
timeout is set ONCE, before the read loop, to the initial
remaining time; every subsequent `read1()` inherits that
original timeout, not the time remaining at that read. The
`remaining()` checks around each read detect an overrun only
after a blocking read returns — they cannot interrupt a read
already blocking. A read begun at 0.55s of a 0.6s budget can
block for close to the original 0.6s socket timeout, carrying
the operation past its absolute deadline; repeated drips
keep renewing that opportunity. The slow-drip witness does
not close this: its 0.1s interval and `elapsed < 1.8`
assertion show termination before the 3s drip ends, not that
an individual blocking read cannot cross the deadline.

**Required:** the socket timeout bounded by the CURRENT
remaining time before each blocking read, with the
EOF/completion path handled explicitly rather than weakening
the deadline (no settimeout attempt on a socket http.client
has retired after completion). **New witness required:**
deliver an initial chunk near the deadline, then withhold
the next chunk until after the deadline but before the
original timeout would expire — the call must fail within a
small, stated tolerance of the absolute deadline.

**Live record:** the export is retrievable as text, but the
route has not given her a usable local database artifact.
Provide the decoded SQLite file as a directly accessible
artifact, or another complete inspectable export, so she can
perform the final check herself. (Her receiving-side note:
Remmy's own decode verification does not convert into her
independent verification.)

Piece 8 remains not passed: A6's hard transport deadline and
her independent live-record replay remain open.
