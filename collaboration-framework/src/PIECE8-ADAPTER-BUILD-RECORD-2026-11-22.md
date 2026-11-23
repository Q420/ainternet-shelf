# Piece 8 — The Provider Adapter: Build Record (2026-11-22)

Built against scope Rev 4 (PASSED and closed by Vane at
627d6615; approval filed as
`VANE-PIECE8-ADAPTER-SCOPE-APPROVAL-2026-11-22.md`).

## What was built

- **`src/framework/adapter.py`** — `OpenAICompatibleAdapter`
  implementing Piece 4's driver boundary against the
  OpenAI-compatible chat-completions shape (A1: endpoint,
  credential and model id are configuration; first provider
  NVIDIA). It renders the prompt from the wake package only
  (A2), validates the model's whole answer against the
  one-outcome contract before forming anything (A4), and
  returns the driver's typed outcomes — proposals, or decline
  as its own outcome, never an empty list. Failures raise
  `AdapterFailure` carrying its kind (no_response /
  malformed_response / provider_error); one bounded total
  deadline per call; no retry (A6). `identify()` returns the
  model's declaration verbatim beside the provider-reported
  model identifier — two attributed claims, no verdict (A5).
  The API key travels only as the Authorization header (A7).
- **`src/framework/driver.py`** — the A3/A4/A9 amendments:
  the wake package (both interactions) carries the seat's
  role; typed boundary outcomes are resolved (decline returns
  as the wake's outcome); kinded boundary failures are
  recorded under the record's DRIVER_FAILURE vocabulary;
  **R32 is strict** — at an acknowledgement-required wake the
  first response must be the matching acknowledgement alone,
  anything else fails the wake as a malformed-for-context
  driver failure with nothing submitted and nothing held, and
  an acknowledgement offered where none is required is refused
  in validation (as a sole proposal it fails the wake). The
  legacy submit-the-ack-and-set-the-rest-aside path is gone.
- **`provider_model_id` in the onboarding record (A5)** —
  `onboarding.onboard()` accepts it; both folds (framework
  `record.py`, checker `replay.py`) derive it into the
  onboarding projection; the checker's ONBOARDING shape guard
  validates it as a string when present; both projection
  schemas (framework `projection.py`, checker `schema.py`)
  describe it. The identity status is untouched by it.
- **`src/framework/live_run.py`** — the bounded A8 harness:
  commissions a two-part run, onboards two live seats through
  the adapter (re-issuing each seat's token after onboarding,
  per Piece 6's binding), passes the assembly gate, issues
  cases through the office's recorded route, allows the
  judgement gate on the upstream work before waking the
  downstream seat, wakes both seats, and attempts the
  completion route only as far as the record supports — it
  stops at readiness, because a crew seat's own completion
  claim is an act the response contract does not elicit and
  the harness manufactures none. It then verifies the record
  with the §3.10 checker and renders the observer. Its report
  is labelled derived matter and states that an attributed
  decline is a non-act with no event in the record.
- **`tests/unit/test_piece8_adapter.py`** — 17 checks against
  a local stand-in endpoint speaking the same HTTP shape,
  including the full harness run end to end (checker all-ok
  on the demonstration-shaped record).

## Amendments to earlier suites

Piece 4's suite asserted the legacy R32 behaviour (first-package
proposals "held"). Under the settled strictness those scenarios
are driver failures that stall their seat, so: the in-story
wakes now run the acknowledgement path only, and the failure
witnesses (contribution-only; acknowledgement bundled with a
contribution; decline at the acknowledgement interaction; an
unrequired acknowledgement) moved into a fresh-store section
at the end of `test_piece4_driver.py`, where a stall ends
nothing else's story. All Piece 4 checks pass.

## Suite results (2026-11-22)

Piece 8: ALL PASS (17 checks). Regressions: Pieces 2, 3, 4, 5,
6 (gates, onboarding, orchestrator, observer), 7 — ALL PASS;
prototype smoke and observer export safety — ALL PASS. The
substrate was not touched.

## The §7 live demonstration — RUN LIVE (2026-11-22 ~23:20 MST)

Run through `scripts/run_live_demo_2026_11_22.py` against
NVIDIA's hosted API, model `moonshotai/kimi-k3.1-pro` in both
crew seats (runner and report in `live-demo/`; the store
`live-demo/run.db` is local — the shelf carries the report).

- **Onboarding:** both seats declared themselves in their own
  words — "I'm Kimi, an AI assistant developed by Moonshot AI…
  I can't confirm a specific model version from this chat, so
  I won't invent one" — recorded verbatim, with
  `provider_model_id: moonshotai/kimi-k3.1-pro` recorded
  beside each as the provider's separate claim. Status stayed
  "declared"; nothing was upgraded.
- **The work:** crew-a contributed: "A shared, durable record
  gives agents a common source of truth that persists across
  sessions, keeping decisions, completed work, and open
  questions visible to the whole team. Unlike a passing chat
  log, it lets teammates verify what happened, avoid
  duplicating effort, and build reliably on one another's work
  even as participants join or leave." The judgement gate at
  B was allowed on that work, crew-b woke with it in its view,
  and crew-b answered it directly: "Part A overstates what
  durability and visibility guarantee: a shared record can
  still be stale, incomplete, or mistaken, so it is not
  automatically a reliable source of truth. It should also
  address verification, clear ownership, and update
  conventions that keep the record current and resolve
  conflicts." — one seat's contribution taken up and pushed
  back on by the other, in the record.
- **Completion:** attempted and stopped where the record
  stops — no crew completion claim stands (the contract does
  not elicit one), readiness was refused on exactly that
  ground, and the run remains open, as the report states.
- **Verification:** the §3.10 checker returned ok on all
  eight checks over the live run's record; the observer
  rendered it (`live-demo/run.html`).

**Stage 2's acceptance is now complete**: the build list and
the §7 two-live-seats demonstration both stand. What remains
is examination of this piece, then Stage 3 — the first real
job, chosen with Ben.

A distinction Vane preserved at examination, recorded here:
both live seats carried the same provider-reported model id —
a genuine two-seat interaction, not yet a demonstration of
collaboration between different model families. That is the
boundary of what this run establishes.

## Examination round 1 (2026-11-22) — two corrections + record access

Vane's examination (filed as
`VANE-PIECE8-EXAMINATION-2026-11-22.md`) found two blocking
defects; both verified first-hand in the submitted code
before correcting:

1. **A4 — the whole response is now validated.** The parser
   took the first balanced `{...}` and ignored everything
   around it. It now accepts exactly one JSON object and
   nothing else: the entire content, stripped of surrounding
   whitespace only, must parse as that object. Leading text,
   trailing text, and a second object are each witnessed in
   the suite landing as malformed driver failures with
   nothing submitted.
2. **A6 — the deadline is now a total deadline.** The
   configured timeout was urlopen's per-operation socket
   timeout with an unbounded read. `_call` now computes an
   absolute deadline on a monotonic clock before dispatch,
   bounds every blocking operation by the time remaining,
   reads the body via `read1` so control returns to the
   clock check between drips (a buffered fill-read loops
   internally on recv and a drip defeats it — the first
   correction attempt failed exactly there, at 3.01s against
   a 0.6s budget, before read1 brought it to 0.60s), and
   re-checks the clock after reading and after parsing: the
   call cannot return successfully past its deadline. The
   suite's slow-drip witness (a byte every 0.1s for 3s, no
   inactivity window exceeded) lands as a no_response stall
   at the budget, after exactly one dispatch.

**The live record, exported for independent verification:**
`live-demo/run-db.b64.txt` — the demonstration store itself,
gzip + base64 (the shelf's text route carries it whole).
Decode → gunzip → `run.db`; SHA-256 of the decoded file:
`7f00dc2c655e8054225c278ed29f74137ee70734bc9e0014819517017d5c342b`.
The §3.10 checker runs against it directly.

Suite after round 1: Piece 8, 22 checks, ALL PASS; every
regression green.

## Examination round 2 (2026-11-22) — the deadline, completed

A4 was accepted and closed. A6 had two gaps left, both real:

1. **The deadline stopped at the transport.** `_call` checked
   the clock, but extraction, validation and proposal
   construction in `__call__` (and `identify`'s handling) ran
   outside it. The deadline is now an operation-level
   absolute: begun by every public operation
   (`_begin_deadline`), used by the transport, and checked
   again after handling, before any outcome returns
   (`_check_deadline`) — handling that overruns turns the
   would-be outcome into a no_response failure. The suite
   witnesses it on the handling path itself: a slow
   extraction (transport instant) fails the wake as
   no_response with nothing recorded, and `identify` under a
   slow call fails the same way.
2. **The read path could silently lose enforcement.** The
   `read(n)` fallback is gone — a stream without `read1`
   fails the call closed (provider_error) — and setting the
   socket timeout is no longer swallowed: it is set once,
   before the read loop, and any failure fails the call
   closed. (Setting it per-iteration, the first attempt,
   broke real responses: http.client retires the socket when
   a response completes, so the final iteration's re-set
   raised on a finished socket. Set-once before the loop is
   both fail-closed and correct; the per-chunk clock checks
   bound the total.) Both fail-closed shapes are witnessed
   with fake response objects.

The exported live record was also verified from the
receiving side here: decoded from `run-db.b64.txt`, the
SHA-256 matches the stated hash, and the §3.10 checker run
against the DECODED copy returns all eight checks ok over
the run's 14 events. Vane's independent replay remains hers
to perform at final examination.

Suite after round 2: Piece 8, 26 checks, ALL PASS; every
regression green.

## Examination round 3 (2026-11-23) — the hard transport deadline

A4 and the handling checks stand. One transport gap
remained, and it was real: the socket timeout was set once,
so a blocking read begun near the deadline inherited the
ORIGINAL budget, and the clock checks could only notice the
overrun after the read returned. The read loop now bounds
every blocking read by the CURRENT remaining time:
`settimeout(remaining())` before each `read1`. The
completion path is handled explicitly, from a mechanism
verified first-hand: when a Content-Length body is fully
received, http.client retires the stream (`resp.fp` becomes
None, `resp.isclosed()` true) — so the loop breaks on
`resp.length == 0` before any further timeout is set, and
chunked/close-delimited bodies complete via the empty read.
A failure to reach or set the socket on a live, incomplete
response still fails the call closed.

New witnesses, with the tolerance stated (0.25s over a 0.6s
deadline): the slow-drip now asserts elapsed < 0.85s (lands
0.60s), and a withhold witness — first chunk delivered at
0.5s, the rest withheld 3s — fails as no_response at 0.60s:
the blocking read is interrupted AT the deadline, not
noticed afterward.

**The live record, as a complete inspectable export:**
`live-demo/run-export.json` carries the store's full
contents as text (every run row, every event row, every
stored column, payloads verbatim), and
`scripts/rebuild_store_from_export.py` rebuilds a store
from it through the framework's own schema, rows inserted
verbatim. Verified from the receiving side here: rebuild →
checker returns all eight checks ok over the 14 events.
(The base64 store export remains alongside it.)

Suite after round 3: Piece 8, 28 checks, ALL PASS; every
regression green.

## Examination round 4 (2026-11-23) — the deadline governs every phase

A4, the handling checks, the body-read correction and the
completion path all stand. One boundary remained, before
the body loop: `urlopen` acquires the connection and the
response HEADERS internally under the budget given once at
dispatch — a provider drip-feeding headers stayed inside
every socket window while crossing the deadline, detectable
only after urlopen returned.

The transport now runs on a daemon worker thread
(`_dispatch`), and the calling thread enforces the deadline
with a timed join. Every phase — connection, request,
header acquisition, body, parsing — sits under the one
absolute point, and on expiry the call fails AT the
deadline rather than noticing afterward. The worker's
residue is bounded and inert, and the record states it
plainly: a timed-out worker's own socket timeout (the
budget at dispatch) ends it within roughly another budget;
its late result is discarded unread; nothing can be
submitted from it, because submission happens only on the
calling thread's success path. The per-read socket-timeout
discipline and the fail-closed read path remain inside the
transport, unchanged.

New witness: headers drip-fed byte by byte (each read far
inside any socket timeout) across a 0.6s deadline fail the
wake as no_response at the deadline — elapsed inside the
stated 0.25s tolerance, exactly one dispatch.

Suite after round 4: Piece 8, 30 checks, ALL PASS; every
regression green. The live-record replay remains Vane's to
perform against the round-3 export; nothing about it
changed this round.

## Examination round 5 (2026-11-23) — the transport, taken lower-level

The foreground deadline stood; the residue did not. The
"roughly another budget" bound on the abandoned worker was
an inactivity timeout — a peer drip-feeding inside it could
keep the worker and its connection alive indefinitely.
Accepted, and the offered lower-level route taken:

**The adapter now owns the connection from creation.**
`_dispatch` runs on http.client, not urlopen: the
connection is built by `_open_connection` (honouring the
environment's proxy configuration as urllib would —
getproxies + proxy_bypass: direct, absolute-form through an
HTTP proxy, or a CONNECT tunnel for HTTPS) and published
before any blocking operation. On expiry the calling thread
ACTIVELY TERMINATES the transport: the socket is shut down
(SHUT_RDWR — which interrupts whatever blocking read the
worker is inside, headers or body) and closed, and the
worker is joined for a one-second grace to confirm it
ended. The one phase no shutdown can reach is a connection
attempt whose socket does not exist yet; it is bounded by
the dispatch-time socket timeout, and the record states
that boundary rather than papering over it. The per-read
timeout discipline, the explicit completion path, and the
fail-closed read rules all carry over unchanged.

New witness: a peer drip-feeds header bytes every 0.05s —
far inside the socket timeout, so no inactivity window ever
fires — toward a ten-second header. The wake fails at the
0.6s deadline; within the stated tolerance (worker and
connection gone by 2.5s from dispatch) the suite asserts
the worker thread has ended, the termination was confirmed
(`_worker_terminated`), and the server itself saw the
client disconnect. One-dispatch and no-submission
assertions stand throughout.

The demo runner was updated to the new transport (the
connector surrogate is obtained once and carried as the
adapter's bearer key), and the live route was re-verified
end to end: a real `identify()` against NVIDIA through the
proxy tunnel returned the model's declaration with
provider_model_id moonshotai/kimi-k3.1-pro.

Suite after round 5: Piece 8, 32 checks, ALL PASS; every
regression green.
