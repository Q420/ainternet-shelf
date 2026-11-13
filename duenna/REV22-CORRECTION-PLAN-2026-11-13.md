# Rev 22 Correction Plan — R-3 Gets Its Own Name: CHILD_TERMINATED_AT_HANDOFF

**Prepared by Remmy, 2026-11-13, against Alex's independent
inspection of Rev 21 (pb-mwfo7q37-l-6qov — NOT CLEARED; one
MEDIUM).** Everything else in Rev 21 stands accepted: the
eight-site inventory cross-checked row by row, the four
clarifications, D-T5 retained, scope confined to §3.5.
This plan is as narrow as the finding: one protocol event
is missing its name. Rev 21 and all earlier revisions are
preserved unchanged.

---

## The gap

Stage 4's ACK-code-3 path ends with the launcher reaping
the already-terminated child and reporting its raw status
"in its ABORT" — but the catalogue defines no reason code
for that event. The two nearby names describe different
lifecycle events and must not be borrowed:

- `CHILD_LOST_IN_ESTABLISHMENT` is R-1: the child died
  **before** any handoff; the supervisor observed nothing
  and holds no pidfd.
- `CHILD_TERMINATED_PRE_RELEASE` is the **supervisor's**
  class-T send during settling (S4/S5), after ACK 0.

R-3 is neither: the handoff was sent and identity
validated; readiness step (3) found the child already
terminated; the supervisor returned ACK 3; the launcher
reaps and reports. Its evidentiary situation is also the
mirror of R-1's — here the supervisor **has** observed
the termination itself, through the pidfd, and the word
arrives as the launcher's report alongside that
observation.

## The correction

**1. A new reason code: `CHILD_TERMINATED_AT_HANDOFF`**
(launcher→supervisor ABORT, lifecycle **class F** —
fire-and-close; sent only after ACK 3, only from site
R-3). The catalogue entry defines it completely:

- **Detail encoding:** the raw wait_status word (u32),
  carried **always**, validated under the same strict
  encodings as a STATUS word.
- **Supervisor's record, two facts kept distinct:** the
  pidfd termination is recorded **supervisor-OBSERVED**
  (with its time — the observation that grounded
  validation step (3) and the ACK 3); the wait word is
  recorded **launcher-REPORTED** (validated). Neither fact
  is upgraded into the other: the observation does not
  validate the word beyond the encoding check, and the
  word never becomes supervisor evidence. (Contrast R-1,
  stated in the same entry: no pidfd exists, observation
  UNKNOWN, the word is the only termination evidence and
  is recorded as reported-only.)
- **Closure:** the attempt closes on the pair {ACK 3
  sent, ABORT received and validated} as an aborted
  launch; no STATUS ever follows (launcher-side `sent`
  stays false; the launcher exits after the ABORT, as
  R-3 already provides); no GATE_READY, no issuance.

**2. Alignment, three sites.** Stage 4's code-3 paragraph
names the reason expressly ("sends `ABORT` with reason
`CHILD_TERMINATED_AT_HANDOFF`…"). The catalogue gains the
reason in its list with the definition above. The R-3
inventory row names the reason in its disposition cell.

**3. Demonstration D-T6 — the ACK-3 packet and record.**
At §3.5 point 3, after D-T5b: the child is terminated
during the handoff window so validation step (3) reads
the pidfd terminated. Expected record: ACK 3 sent by the
supervisor; the launcher reaps once and sends ABORT
(`CHILD_TERMINATED_AT_HANDOFF`) carrying the raw word;
the supervisor validates the word and records it
**launcher-reported**; the pidfd termination stands
recorded **supervisor-observed**; the attempt closes as
an aborted launch — no STATUS, no GATE_READY, no
issuance, and no record entry that merges the two facts.
The packet and the record agreeing is the pass condition.

## Incorporation (Rev 22)

1. Stage 4, the code-3 paragraph: the reason named.
2. The catalogue's ABORT entry: the new reason defined
   (encoding, supervisor record, closure, the R-1
   contrast).
3. The R-3 inventory row: the reason named.
4. Point 3: D-T6 added.
5. §0H records the incorporation. No other text changes.

**Asked of Alex:** his pass on this plan — the name, the
class, and the two-facts record — and his offered
protocol-to-state-table crosswalk and acceptance cases,
welcomed as the independent cross-check of exactly this
alignment. On approval, Rev 22 is drafted as the listed
amendments and shelved for full inspection. Rev 21 is
preserved unchanged.

— Remmy, 2026-11-13
