# Bridge as Sensor — Amendment 2: Registration by Marker

**Amends:** `record/BRIDGE-AS-SENSOR-DESIGN-2026-11-15.md` as amended by
Amendment 1 (`record/BRIDGE-AS-SENSOR-DESIGN-AMENDMENT-1-2026-11-15.md`).
**Purpose:** closes the registration-mechanics item that Alex's ruling
(`record/ALEX-BRIDGE-SENSOR-RULING-2026-11-15.md`, §8 question 4) retained
as open and required to be resolved before any build.
**Owner authority:** the marker set in §2 was presented to the owner and
accepted by him on 2026-11-15 ("Accepted", 21:28 MST), including the two
refusals in §4 and the closing rule in §5.
**Status:** DESIGN PAPER ONLY. No implementation is authorised. The owner's
stop otherwise remains in force.

## 1. The mechanism

A wait is registered by a marker in the orchestrator's outbound letter. The
bridge reads the marker at carriage — in a letter it is itself delivering
from the orchestrator — and registers, holds, resumes, or retires the wait
accordingly.

The authority is the marker's PROVENANCE, not its text. The bridge acts on
a marker because it witnessed the marker inside a letter it carried from
the orchestrator (or in a bridge-facing control from the orchestrator or
owner, §2). A marker appearing in seat-originated content — a reply, an
echo, a quotation — has NO effect on registration: it never registers,
amends, holds, resumes, or closes a wait. This restates Amendment 1 §A4
for this mechanism and is not negotiable within it.

Job references inside markers are orchestrator-issued identifiers (the
`⟦WD:…⟧` precedent's form). A marker naming an unknown job reference
registers a wait under that reference; job meaning lives in the
orchestrator's job record, never in the marker.

## 2. The marker set

Five behaviours. Syntax follows the established `⟦…⟧` form.

| Marker | Meaning | Bridge behaviour |
|---|---|---|
| `⟦ASK:<job>⟧` | A reply is owed for this job. | On delivery of the letter, register a wait on that conversation for that job. Each reply landing fires a notice. |
| `⟦ASK:<job>×<n>⟧` | A reply is owed in n parts. | As ASK, but the wait tracks parts received against n. Each part landing fires a notice. The wait closes on the nth part. If the escalation age passes with parts outstanding, the wait escalates as PARTIAL — never silently, never as complete. |
| `⟦TELL⟧` | No reply is owed. | No wait is registered. A reply that arrives anyway is ordinary traffic and fires no notice. |
| `⟦HOLD:<job>⟧` | Suspend the open wait for this job. | Notices for the wait are suppressed; the registration is kept. |
| `⟦RESUME:<job>⟧` | Lift a hold. | Notices for the wait resume. Bridge-facing only (below). |
| `⟦CLOSE:<job>⟧` | Retire the wait for this job. | The registration is removed. No further notices for that job in that conversation. |

**Parameters on ASK:** the job reference (required); the part count
(optional, above); an escalation age (optional — how long the wait may
stand before it escalates under the inbox's age rules; the job record's
default applies when absent).

**Placement.** ASK and TELL ride in seat letters — the seat can see them;
they are how the orchestrator's intent is on the record. HOLD and CLOSE
ride in a seat letter when the seat should know the wait's state has
changed, and are otherwise issued bridge-facing. RESUME is bridge-facing
only: the seat was never a party to the hold. Bridge-facing controls are
issued through the bridge's own registration channel (panel or equivalent);
the channel's concrete form is a build decision, its trust requirement is
not — it accepts controls from the orchestrator/owner side only.

**Conflicts and duplicates.** One wait per (job, conversation). A second
ASK for a job and conversation with a wait already open is journalled as a
duplicate claim (the ledger's DUPLICATE_OBSERVED discipline) and the
existing wait stands — Amendment 1 §A4's one-owner rule applied to
registration. An ASK for the same job in a DIFFERENT conversation opens a
separate wait; multi-seat asks are separate waits sharing a job reference,
each with its own notices. HOLD on a job with no open wait, RESUME on a
wait not held, and CLOSE on a job with no wait are each journalled and
otherwise no-ops — never errors that disturb other waits.

**Reply matching.** Unchanged from the base paper and Amendment 1: a reply
is matched to a wait by conversation and source identity, never by any
marker or content in the reply itself.

## 3. What the notice says about the wait

The notice (base paper §2) gains one field from this amendment: the wait's
state at firing — `part <k> of <n>` for a multi-part ASK, `resumed` for
the first notice after a RESUME. Identity-only still holds; these are
facts about the registration, not about the reply's content.

## 4. The two refusals (owner-accepted)

- **No seat-side authority markers.** There is no FINAL, PROVISIONAL, or
  kin marker with any bridge effect. Whether a reply is the final ruling
  or a provisional is the orchestrator's judgement, made when she reads
  the reply. The notice fires for every landing, provisional included.
- **No urgency marker.** The notice is already immediate; there is no
  faster lane to mark. Letter priority remains an envelope property,
  where the bridge already has it.

## 5. The closing rule

The set in §2 is closed. A new marker earns its place only if it changes
bridge behaviour — opens, holds, resumes, or closes a wait, or changes
what a notice does. Markers never describe content, kind, or quality of a
job; that lives in the job record. Any future addition is an amendment to
this paper, reviewed the same way.

## 6. Effect on the design

With this amendment, the registration-mechanics item retained in Alex's
ruling is resolved on paper, subject to his review of this amendment:
registration is authoritative (provenance, §1), protected against
untrusted seat echoes (§1, §4), and protected against duplicate claims
(§2). No other section of the base paper or Amendment 1 changes.
