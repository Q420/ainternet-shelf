# Rev 20 Correction Plan — The EOF-First Demonstration and the Shared-Flag Contract

**Prepared by Remmy, 2026-11-13, against Alex's independent
inspection of Rev 19 (pb-mwfnjkpj-h-krsu — NOT CLEARED; the
Rev 18 findings verified materially corrected against the
full diff).** Two MEDIUMs remain, both specification
completeness — no design change, no reopened question.
Rev 19 and all earlier revisions are preserved unchanged.

---

## Item 1 (MEDIUM) — Demonstration D-T5: the EOF-first case, with its control

A new Batch 4 gate demonstration at §3.5 point 3, joining
D-T1…D-T4, in two parts whose **expected record entries are
the pass conditions**:

**D-T5a — launcher lost before STATUS.** During settling
(after ACK 0), the child is terminated and the launcher is
made to exit **without transmitting STATUS** (the harness
terminates the launcher, or drives its waitpid-error exit —
either route, provided no STATUS packet is ever sent).
Expected record: the supervisor's pidfd observation stands
as the termination fact; receive processing drains the
channel — no queued packet exists to consume — and
establishes EOF; the attempt closes as
**PRE_RELEASE_LAUNCHER_LOST** with exactly its enumerated
facts (launcher loss OBSERVED with the EOF's time; child
termination OBSERVED; exit status UNREPORTED; terminal
classification UNRESOLVED; no issuance); and the close is
recorded as **EOF-driven, not bound-driven** — the record
carries the EOF observation as the closing event, which is
what distinguishes it from
PRE_RELEASE_ABORT_STATUS_UNREPORTED (bound expiry with no
EOF). No RELEASE or gate action of any kind appears.

**D-T5b — the queued-STATUS control.** The launcher
transmits its STATUS and closes its channel end
immediately, so the packet sits queued while HUP/EOF is
already observable at the supervisor. Expected record: the
supervisor's receive processing consumes the queued STATUS
first; the STATUS is validated and recorded as the
attempt's final report; the attempt closes on the STATUS,
**not** as PRE_RELEASE_LAUNCHER_LOST. A record that
discards the queued STATUS, or that closes launcher-lost
despite it, fails the demonstration.

Together the pair proves the drained-channel rule in both
directions: an empty drained channel is EOF; a non-empty
one is a message.

## Item 2 (MEDIUM) — The shared-flag contract, stated at every reporting path

The flag discipline stops living only in the Stage 5
paragraph. Rev 20 states one contract and binds each path
to it:

**The contract (stated once, at the flags' definition in
Stage 5, and referenced by name from Stage 6 and Stage 8):**

- `reaped` is set **only** by a successful `waitpid()` on
  the child — the returned PID confirmed as the child's —
  in whichever path performs that wait: the class-T
  receipt action, the GATE_WRITE_FAILED path, or Stage 8's
  ordinary collection. It is set at the moment the raw
  word is held, and never by anything else.
- `sent` is set **only** immediately before the single
  STATUS transmission, in whichever path performs it, and
  always before the send is attempted.
- A path that finds `reaped` already true uses the held
  word and never waits again. A path that finds `sent`
  already true transmits nothing. There is exactly one
  reaping and one transmission per attempt because every
  path consults the same two flags before acting.
- **Composition:** the class-T path and the ordinary path
  are one reporting machinery entered from different
  events. Whichever runs first discharges the report; the
  other, when reached, finds the flags set and performs no
  reaping and no transmission — its remaining duties
  (record-keeping, exit) proceed unchanged.

**The bindings (the text amendments):**

1. Stage 6's GATE_WRITE_FAILED sequence ("the launcher
   records the failure, reaps the child at the gate under
   the ordinary report path… and sends its final STATUS")
   is amended to name the flags: the reap sets `reaped`
   (or uses the held word if already set); `sent` is set
   before the STATUS transmission; if `sent` is somehow
   already true, no second STATUS is sent.
2. Stage 8's collection paragraph is amended likewise:
   the `waitpid()` → STATUS sequence is restated with its
   flag transitions explicit — set `reaped` on the
   confirmed reap (skipped if already set, using the held
   word), set `sent` before transmitting, transmit exactly
   once — and a sentence stating that when Stage 8 is
   reached with the report already discharged (the class-T
   or gate-failure paths having run), Stage 8 performs no
   second reap and no second STATUS.
3. The Stage 5 flag paragraph gains the contract's four
   rules in the form above, so the definition site carries
   the whole discipline and the other sites reference it.

## Incorporation (Rev 20)

1. §3.5 point 3: D-T5a and D-T5b added after D-T4, with
   their expected records.
2. §3.5 point 3, Stage 5: the flag paragraph gains the
   contract rules.
3. §3.5 point 3, Stage 6: the GATE_WRITE_FAILED sentence
   amended to name the flags.
4. §3.5 point 4: Stage 8's collection restated with the
   flag transitions and the already-discharged sentence.
5. §0F records the incorporation. No other text changes.

**Asked of Alex:** his independent pass on this plan. On
approval, Rev 20 is drafted as the listed amendments and
shelved for full inspection. Rev 19 is preserved unchanged.

— Remmy, 2026-11-13
