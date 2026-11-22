# Piece 2 scope — record + doorway (2026-11-22)

Derived from the approved SPEC SHEET Rev 5, §3.1 (R1–R4), §3.2 (R5–R7), §4 (authority matrix), and the doorway-facing cross-cutting rules R30/R31. Mapped against the carried substrate (Piece 1) before any code.

## What the substrate already gives (used, not rebuilt)

- `fabric/store.py` — generic append-only, hash-chained event store (`append(type, actor, affected, payload)`); mutation refused by schema. Carries R1's chain link and no-edit rule directly.
- `fabric/canonical.py` — canonical serialisation + event hashing.
- `fabric/engine.py` — `verify_chain` and `state_hash` are generic pure functions and are used. Its fold (`apply_event`, `Engine`) is built for the prototype's event vocabulary, so the framework's state derivation is new code (below), per R4.
- `fabric/harness.py` — its token pattern (`issue_token` / authenticate) is the model for the doorway's binding, but the harness surface itself serves the prototype's exercise (regions, patterns, seals). The framework doorway is new code, per §3.2 "substrate harness, adapted".

## What Piece 2 builds (new package `src/framework/`, carried files untouched)

1. **`record.py` — the framework record layer (§3.1).**
   - The framework event-type vocabulary (R3): contribution, comment, disagreement, gate_outcome, finding, ruling, disposition, certification, case, onboarding, escalation — plus run lifecycle events (§5) and rejection events.
   - Claim status (R2): claim-bearing events carry a status from `claimed / evidenced / verified / disputed / stood_down`; transitions are events, enforced by authority — `evidenced` by the seat attaching evidence; `verified` by the examiner alone; `disputed` only following a recorded disagreement naming the claim; `stood_down` by the claim's author or the examiner at a gate. Any other attempt is refused here and recorded by the doorway (R6).
   - The framework fold: replaying the event history reproduces the run's recorded state (claims + statuses, disagreements with open/settled/open-at-close, gates, cases with versions, certifications with coverage) exactly (R4).
2. **`doorway.py` — the only route in (§3.2).**
   - Tokens bound to a seat's recorded identity; unbound or mismatched acts refused (R5).
   - The §4 authority matrix enforced mechanically; an out-of-authority act is rejected and the rejection recorded as an event authored by the doorway, naming the seat, the act and the ground (R6).
   - Evidence boundaries: reads of sealed material outside the seat's boundary are rejected and recorded (R7).
   - Staleness (R31): every act carries its view's record position; if the act's subject changed since, reject + record; otherwise record the act flagged `stale-basis` when its view was behind.
   - Pause scope (R30): acts for a recorded paused tree part or its downstream dependents are blocked at the doorway; unrelated branches validate normally.

## Deliberately NOT in this piece (later pieces, not silently absorbed)

- Onboarding proper (§3.6): Piece 2 takes a run's seat bindings as recorded onboarding records in their simplest form; the onboarding mechanism and its identity states are their own piece.
- Cases and the office (§3.5): the doorway reads boundaries and case versions from the record; issuing/correcting cases is a later piece.
- Gates as a mechanism (§3.7): Piece 2 enforces recorded pause sets and records gate outcomes as events; the gate mechanism itself is a later piece.
- The bubble (§3.3) and live seat drivers (§3.4): later pieces. No scheduler is built (R29).

## Acceptance for this piece (from §7, the items §3.1–3.2 carry)

- A claim's promotion to `verified` by anyone but the examiner is rejected and recorded; `disputed` follows a recorded disagreement.
- An out-of-authority act and an out-of-boundary read are rejected and recorded.
- A held gate's paused set blocks its part + downstream at the doorway while an unrelated branch's acts continue to validate (R30); the paused set is recorded.
- A stale-view act is flagged `stale-basis`; a subject-changed act is rejected and recorded (R31).
- Replay reproduces the recorded state exactly; the chain verifies (R4).

---

**Addendum (2026-11-22, correction round 1):** this note's R30 wording ("a GATE_OUTCOME with outcome hold") is superseded — R22's outcome vocabulary is exactly allow / correct / escalate, and the pause is the recorded state an escalate outcome carries. See the build record's correction-round section.
