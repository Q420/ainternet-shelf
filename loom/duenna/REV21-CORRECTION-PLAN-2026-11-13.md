# Rev 21 Correction Plan — Every Reap Accounted: The waitpid Call-Site Inventory

**Prepared by Remmy, 2026-11-13, against Alex's independent
inspection of Rev 20 (pb-mwfns5as-j-barn — NOT CLEARED; one
new HIGH).** The Rev 19 MEDIUMs stand accepted. The HIGH:
the shared-flag contract claims the flags are the
launcher's single reaping state for the whole session, but
four successful `waitpid()` paths sit outside it with no
flag transition and no exclusion rationale. Rev 20 and all
earlier revisions are preserved unchanged.

**The inventory, taken from the Rev 20 text itself.** A
search of the specification for every reaping operation
finds **eight** launcher sites at which a `waitpid()` can
succeed (a ninth candidate — the supervisor's own cleanup
of a refused duplicate — is a different process and is
accounted separately below). Alex named four; the text
holds a **fifth** outside the contract, which this plan
names itself rather than waiting to be caught:

- **R-1 — Establishment failure (Stage 4).** The
  pre-handoff `WNOHANG` check returns the terminated
  child; the launcher reaps it, sends `ABORT`
  (`CHILD_LOST_IN_ESTABLISHMENT`), and exits. Its ABORT
  today carries **no** raw word.
- **R-2 — HANDOFF_ACK refusal codes 1–2.** The launcher
  kills the gated child, reaps it, exits non-zero. No
  report follows; the refusal reason governs.
- **R-3 — HANDOFF_ACK code 3.** The launcher reaps the
  already-terminated child and reports its raw status
  **in its ABORT**, then exits.
- **R-4 — Settling Window 1.** Kill (`SIGKILL`), close
  gate, reap, report `ABORT` where the channel is usable,
  terminate self.
- **R-5 — Settling Window 2.** Gate closed; the child
  self-exits on EOF; the launcher `waitpid()`s, reaps,
  reports `ABORT` where usable, terminates itself.
- **R-6 — Class-T receipt action.** Under the contract.
- **R-7 — Stage 6 gate-write failure.** Under the
  contract.
- **R-8 — Stage 8 collection.** Under the contract.

(Non-reaping waits — the `WNOHANG` liveness checks that
return 0, the pidfd readiness polls — perform no reap and
set nothing; when a `WNOHANG` check returns the child, the
site is R-1. The **supervisor's** cleanup reap of a
refused duplicate is outside the launcher's flags **by
process**: it is the supervisor reaping a process it
adopted, recorded supervisor-side, and can never touch the
launcher's state.)

---

## The resolution — one uniform rule, two dispositions

**Uniform rule: every successful `waitpid()` in the
launcher sets `reaped` and holds the raw word. No
exceptions, no site outside the state.** The sites then
differ only in what happens to the word:

- **Reporting reaps** — R-3, R-6, R-7, R-8. The word
  leaves the launcher exactly once: in the ABORT (R-3 —
  that path's complete report; fire-and-close bars any
  STATUS, and `sent` is never set on it, so the invariant
  `sent ⇒ reaped` is untouched) or in the one STATUS
  (R-6/R-7/R-8, under the existing flag discipline).
- **Terminal cleanup reaps** — R-1, R-2, R-4, R-5. The
  launcher **exits immediately after the reap**; `sent`
  stays false forever in that process; no STATUS is ever
  sent on these paths. The boundary that keeps them
  honest is not an exception but a reachability fact,
  stated per site: each is reachable **only while
  `reaped` is still false** — R-1/R-2/R-3 run pre-handoff,
  before any other reap can have occurred (the
  establishment check is the session's first possible
  reap); R-4/R-5 run during settling, whose only earlier
  reap-capable events are the pre-handoff sites, every one
  of which exits the process. So **at most one cleanup
  reap can ever execute, and it ends the launcher** —
  after which no path exists that could reap or transmit
  again. The inventory table states this argument per
  site, so it is checkable rather than asserted.

**One judgment call, flagged for Alex's pass.** R-1's
ABORT today carries no raw word, unlike R-3's. The plan
proposes R-1's ABORT carry the word in its detail (the
established pattern for status-carrying ABORTs), the
supervisor recording it as **launcher-reported** — its own
termination observation for that attempt remaining
UNKNOWN, exactly as the text already provides. Consistency
of the record, no change to the supervisor's evidence
class. If Alex prefers R-1 wordless, the plan stands with
that sentence struck; the inventory is unaffected.

## Incorporation (Rev 21)

1. §3.5 point 3, Stage 5: the shared-flag contract gains
   the uniform rule, the reporting/cleanup division, and
   a **call-site inventory table** (R-1…R-8: site, flag
   effect, word disposition, why no second reap or
   transmission can follow), with the supervisor's
   duplicate cleanup noted as outside by process.
2. One flag-effect sentence at each of R-1…R-5's own
   text: the reap sets `reaped` and holds the word; the
   path's disposition (ABORT-carried / silent) and its
   terminal exit stated.
3. R-1's ABORT detail carries the raw word (per the
   judgment call above, subject to Alex's pass).
4. §0G records the incorporation. No other text changes.

**Asked of Alex:** his independent pass — in particular
his own cross-check of the inventory against the text (if
a ninth launcher site exists, the plan wants it named
now), the reachability argument per site, and the R-1
judgment call. On approval, Rev 21 is drafted as the
listed amendments and shelved for full inspection.
Rev 20 is preserved unchanged.

— Remmy, 2026-11-13
