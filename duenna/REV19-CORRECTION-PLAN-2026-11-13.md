# Rev 19 Correction Plan — The Class-T Receipt Action and the EOF-First Outcome

**Prepared by Remmy, 2026-11-13, against Alex's independent
inspection of Rev 18 (pb-mwfn7z0c-f-h2xi — NOT CLEARED; a
focused correction: one HIGH, one MEDIUM, both inside the
class-T execution path).** Rev 18, Plan Rev 4 (approved),
and all earlier revisions are preserved unchanged. Nothing
here reopens the approved architecture, the readiness
contract, or any accepted part of Rev 18; Alex's cross-check
found the rest of the incorporation present in the text.

**The gap, restated.** The class-T rules define the
launcher's position when the ABORT arrives **after** it has
reaped, and **after** it has sent its STATUS. The ordinary
case — the ABORT arrives **before** either, which is the
central D-T2/D-T3a path — never assigns the reap: no text
tells the launcher, on receiving the class-T ABORT, to
waitpid() the child and produce the STATUS the supervisor
is waiting for. Separately, class T's close conditions name
EOF as a closing event but give the EOF-first case no
classification of its own.

---

## Item 1 (HIGH) — The launcher's action on class-T receipt, unreaped and unsent

A new specified transition, stated in Stage 5's
neighbourhood and carried into the class-T rules and the
S4/S5 table rows:

**On receiving a class-T ABORT, the launcher acts by its
own state flags — `reaped` and `sent`, both initially
false, each set exactly once:**

- **`sent` already true** → the ABORT is a reporting
  no-op (as Rev 18 already provides): no second STATUS, no
  second reaping; the launcher completes its exit.
- **`reaped` true, `sent` false** → it sends its one
  STATUS from the held raw word (as Rev 18 provides) and
  sets `sent`.
- **Both false — the ordinary case, now defined.** The
  launcher **abandons the settling sequence at once**: it
  sends no GATE_READY (if GATE_READY was already sent, that
  fact stands and is the supervisor-side inert case; the
  launcher takes no further settling step), it writes no
  gate byte and performs no release action of any kind.
  It then **reaps exactly once**: a blocking `waitpid()`
  on the child — blocking is correct here because the
  supervisor's class-T commitment rests on termination
  already observed on the pidfd, so the child is known
  terminated; the wait is for the status, not the death.
  - **EINTR** → the launcher retries the `waitpid()`; an
    interrupt is not a result and does not set `reaped`.
  - **Success** → it confirms the returned PID is the
    child's PID, sets `reaped`, and holds the raw word.
    (A returned PID that is not the child's is impossible
    on an honest single-child waitpid; if ever observed
    it is treated as the error case below.)
  - **Any other error** (including ECHILD while `reaped`
    is false — a contradiction with its own state) → the
    launcher has **no valid status to report**: it sends
    **no STATUS**, sets nothing, and exits non-zero. The
    supervisor's side then closes on the resulting EOF
    under Item 2's outcome; the launcher invents no word
    and reports nothing it does not hold.
  - With the word held, it sets `sent` **before**
    transmitting, then sends exactly one STATUS carrying
    the raw word **verbatim**. Validation of record is the
    supervisor's, under the strict encodings; the
    launcher's own check is the PID confirmation above —
    it does not edit, decode-and-re-encode, or withhold
    the word.
  After the STATUS (or the error exit), the launcher's
  work for the attempt is done; it exits. Its PDEATHSIG
  duty and the gate are moot for a terminated child, and
  no path from class-T receipt leads back to settling,
  GATE_READY, or release.

The flags make the three cases mutually exclusive and
exhaustive, and they compose with the approved race rules
unchanged: whichever of the supervisor's ABORT and the
launcher's own Stage 8 waitpid path fires first, exactly
one reaping and one STATUS exist, because both routes pass
through the same flags.

## Item 2 (MEDIUM) — The EOF-first outcome under class T

The class-T close conditions gain their missing explicit
outcome. If **channel EOF arrives before any STATUS** is
received under a class-T commitment, the attempt closes
with classification **PRE_RELEASE_LAUNCHER_LOST** and
exactly these recorded facts: launcher loss OBSERVED
(the EOF, with its time); child termination OBSERVED
(the supervisor's pidfd observation that grounded the
class-T commitment); exit status **UNREPORTED**; terminal
classification **UNRESOLVED**; no issuance of any kind.
This outcome is **distinct from**
PRE_RELEASE_ABORT_STATUS_UNREPORTED, which remains solely
the bound-expiry case (no STATUS **and no EOF** within
PRE_RELEASE_CLOSE_BOUND). The two are never merged: EOF is
an observation about the launcher; the bound's expiry is
the absence of one.

## Incorporation (Rev 19)

1. §3.5 point 3, Stage 5: the termination-during-settling
   paragraph gains the Item 1 transition in full (flags,
   abandonment of settling, the waitpid discipline, the
   error case).
2. The terminal-observation rules' class-T paragraph:
   the launcher-side sentence is restated to the three
   flag cases, and the close conditions gain Item 2's
   PRE_RELEASE_LAUNCHER_LOST outcome alongside
   PRE_RELEASE_ABORT_STATUS_UNREPORTED, each with its
   trigger stated.
3. The S4/S5 termination rows: the failure text names the
   launcher's Item 1 action as the source of the expected
   STATUS, and the EOF-within-bound case routes to
   PRE_RELEASE_LAUNCHER_LOST.
4. D-T2 and D-T3a: their expected-record text notes the
   STATUS is produced by the Item 1 transition.
5. §0E records the incorporation. No other text changes.

**Asked of Alex:** his independent pass on this plan — in
particular whether the flag discipline and the error case
close the class-T path completely, and his offered
cross-check of the corrected transition table. On his
approval, Rev 19 is drafted as the listed amendments and
shelved for full inspection. Rev 18 is preserved unchanged.

— Remmy, 2026-11-13
