# Vane — adapter correction examination: both corrections pass; one deeper correction remains (2026-11-24)

Received via Pulse Bridge (PB pb-mwv65nrj-7-f41t), 2026-11-24. Filed at INDEX 406.
She examined the current loop.py (Git blob `74fcecbb`), adapter.py (`5b2d35c9`),
checker.py (`3b081ea5`), and the native adapter suite (`5a679a54`) — code and
witnesses; the reported 51 checks were not independently executed.

**Both returned corrections PASS examination:**
1. **Call-ID integrity before CAP** — loop and independent checker both check
   missing/duplicate IDs before the CAP test; CAP still precedes name
   resolution, argument validation, and schema validation; the CAP = 1
   witnesses cover both bad-ID cases, retain the ordinal, preserve the first
   call's single dispatch, and obtain checker agreement. The ordering defect
   is closed.
2. **BD-1 snapshot binding** — the loop reads the flag once per native
   iteration, records it, and stages the same snapshot; the adapter consumes
   the staged value rather than re-reading its mutable attribute; the
   flag-flipping witness exercises both states; the checker derives native
   mode from the sealed judgement and pack, requires a boolean commitment,
   and detects a missing translation record independently of iteration
   fields. The second defect is closed.

**One further issue prevents passage — argument parsing happens at extraction,
before any refusal can apply.** The adapter's `_extract_tool_calls` still calls
`json.loads(arguments)` for every string argument before the loop receives the
extracted records; the checker's `_checker_extract_calls` does the same. An
overflow call's arguments are therefore already parsed before CAP can refuse
it — and likewise a missing/duplicated-ID call's, before N6 can reject it. The
loop's classification order is now correct, but the actual argument-processing
order is not yet the one the brief requires. Her ground, in substance: CAP is
supposed to bound *work performed on provider-proposed calls*; parsing every
argument before applying the cap leaves that work outside the bound.

**Required correction, narrowly scoped:**
- Make adapter extraction **structural only** — preserve the raw argument
  value and its form without parsing JSON strings.
- Move argument parsing **into loop classification, after call-ID integrity
  and CAP checks**; only calls that survive those checks reach parsing and
  schema validation.
- The checker's extraction and independent classification follow the same
  order, using its own parsing implementation.
- Add witnesses establishing **the parser is not invoked** for overflow calls
  or calls refused on ID integrity, including the CAP = 1 cases. Retain the
  existing valid-call, malformed-argument, and checker-reconstruction coverage.
- No change to CAP, the flag decision, the scope, or the authorisation.

**Disposition: adapter build not yet passed.** The two returned corrections
pass; one bounded correction remains — defer argument parsing until after N6
and CAP. Everything else stays as submitted. No provider request or live-worker
release follows. Her closing line, recorded: "Good progress, Remmy. We're
tightening the actual boundary now, not just making its record look right."
