# Bridge as Sensor — Amendment 1

**Amends:** `record/BRIDGE-AS-SENSOR-DESIGN-2026-11-15.md`.
**Required by:** Alex's review ruling, ACCEPT WITH AMENDMENTS
(`record/ALEX-BRIDGE-SENSOR-RULING-2026-11-15.md`). Each section below
incorporates one required amendment, in his order. Where this amendment and
the base paper disagree, this amendment governs.

## A1. The notice path supersedes write-armed wake (ruling amendment 1)

The approved Notification Rethink holds that writing a pending inbox item
and arming its wake are one operation, and the wake fires on that write. The
base paper's notice path runs the other way: the bridge delivers the notice,
the delivery starts the orchestrator's turn, and the inbox write is her
first act inside it. Both cannot be authoritative for the same path.

**Ruled:** for the notice path, the write-armed wake rule is SUPERSEDED.
The bridge's delivered notice is the wake. The inbox write that follows is
a record write, and it is bound by three requirements:

- **Idempotent:** the write settles by identity (seat + conversation +
  source identity) against any existing item for the same reply; a repeated
  notice never creates a second actionable item.
- **Durable:** the item is appended and fsync'd before the orchestrator
  acts on it. No action is taken on an unrecorded notice.
- **Visible on failure:** if the write cannot be completed, that failure is
  the first thing the woken turn reports, and the wait falls back to the
  dead-man floor's aged-wait escalation. A notice is never silently lost.

All other inbox paths (judged jobs, system items, capture-health alerts)
keep the write-armed wake rule unchanged.

## A2. Bridge proof-of-life, independent of traffic (ruling amendment 2)

The base paper detected bridge_down from the age of the bridge's last
ledger event. That cannot distinguish a quiet, healthy bridge from a dead
one: absence of traffic is not absence of life.

**Ruled:** the bridge carries a distinct, lightweight proof-of-life record,
emitted on its own cadence, independent of message traffic, carrying the
bridge instance identity, a monotonic beat count, and the beat timestamp —
and NO state field (the standing rule: heartbeat and state are different
instruments; death is judged by an observer, never self-reported). The
dead-man floor and the health panel read the beat's age against a named
freshness threshold and distinguish three conditions:

- beat fresh, no notices: bridge alive, seats silent — normal;
- beat fresh, capture-drop alerts present: bridge alive, a target unhealthy;
- beat stale past the threshold: bridge presumed unavailable — escalate per
  the approved design (wake the orchestrator, alert in the panel, no push
  to the owner).

The inbox canary is unchanged and is not a substitute: it tests the
inbox/wake/action path, not the bridge's seat-tab detection.

## A3. Capture-drop classification is reason-dependent (ruling amendment 3)

Not every `pb-capture-drop` proves target_unhealthy. Classification follows
the drop's recorded reason:

- A drop whose reason demonstrates that the registered target cannot
  complete the required detection operation (page gone, composer/detection
  surface absent, target logged out) → **target_unhealthy**.
- A transient or ambiguous drop (reason indeterminate, single occurrence
  amid otherwise healthy mutation traffic) → **unresolved**: an inbox alert
  item is written, no failure is charged to any component, and the
  classification is revisited only on further evidence.
- A healthy target with no reply → **seat_silent**, as in the base paper.

No periodic target probe is introduced. The resident's continuous mutation
traffic is its round-trip evidence.

## A4. Identity and ownership guarantees (ruling amendment 4)

- **Unresolved identity stays unresolved.** An IDENTITY-UNKNOWN notice
  creates an inbox item in an explicitly unresolved state. It cannot settle
  as an ordinary identity-confirmed duplicate, and it cannot be marked
  acted, until the orchestrator establishes the source occurrence from the
  seat page herself. Reading the page may resolve it; guessing must not.
- **Registration is authoritative or it is nothing.** A wait is registered
  only from the orchestrator/owner side. A seat's echoed marker — in a
  reply, a letter, or any seat-originated content — is never sufficient
  authority to register, amend, or retire a wait (the watchdog contract's
  §4 rule, restated for this substrate).
- **One owner per notice identity.** Notice identities are issued by the
  bridge router's single state machine, which is the authoritative owner of
  each registered wait. A second detection path claiming the same wait and
  source identity is journalled as DUPLICATE_OBSERVED and produces no
  second notice and no second inbox item.

## Registration mechanics (ruling §8, question 4)

Kept OPEN, as ruled. Before any build, the design must name the
registration mechanism and show: authoritative registration, protection
against untrusted seat echoes, and protection against duplicate claims.
The other three §8 questions are settled by the ruling: new envelope type
(accept), light path with durable attempt identity, delivery evidence,
idempotency and ambiguous-send discipline (accept with conditions —
conditions incorporated above), capture-drop sufficiency (accept as
amended by A3).
