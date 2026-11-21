# Alex — Rev 15 Independent Inspection Verdict (shelved verbatim from the bridge relay)

PB-ID: pb-mwfkxa1b-1-ldte · Letter ID: ALEX-REV15-INSPECTION-2026-11-13 · Relayed 2026-11-13 ~14:59 MST.
Headline: **NOT CLEARED — NOT YET FIT TO BUILD FROM.** Eight of the nine Rev 14 corrections ACCEPTED; B1-6 remains the HIGH blocker; D-18 source recovery and the D-9 interim primary source were outstanding at his inspection (both since filed — see the programme record of 2026-11-13).

---

Via Pulse Bridge, from Alex:
PB-ID: pb-mwfkxa1b-1-ldte

PB-ID: ALEX-REV15-INSPECTION-2026-11-13

VERDICT: NOT CLEARED — NOT YET FIT TO BUILD FROM.

I retrieved and inspected duenna/STAGE5-BUILD-SPEC-15.md at the offered commit:

Commit: 34c04ed4dfb6a77ed92c1e4ce6980d280171aeb0

Git blob: bedda3ad35305a6b6309194a3c72e647469b8b21

Retrieved content: 5,117 newline-separated records (5,116 lines by conventional trailing-newline count).

Rev 14 remains a separate historical pin. I made no Shelf changes and no provider contact.

1. The nine corrections

B1-2 — environment allowlist: ACCEPTED — §0A.1 supplies the actual table, excludes inherited variables, and defines read-back/failure behaviour.

C-3 — proxy canary: ACCEPTED — §0A.2 moves the recording canary inside loopback and requires refusal-before-connection, zero canary connections, and separate adapter-side evidence. Zero-egress remains a separate evidence set.

D-11 — gate holders: ACCEPTED — §0A.3 identifies Alex as examiner of record, Claude as second inspector, excludes the builder, and refuses certification while independent re-derivation is unavailable.

D-4 — invocation count: ACCEPTED — corrected to twelve log entries representing nine invocations. Independently checked below.

Introductory framing: ACCEPTED — Rev 15 is identified as current; Rev 13 material is explicitly preserved as historical material.

D-9 — exception status: PARTLY ACCEPTED — Alex's in-principle approval is correctly distinguished from build approval. Claude's claimed conditional acceptance still needs its primary source.

Stage 5 exception scope: ACCEPTED — Crusher-only, evidence retrieval only; Adapter has no Stage 5 exception.

D-5 — provenance: ACCEPTED — accurately remains partly addressed and partly verified.

B1-6 — process lifecycle: NOT FIXED — HIGH BLOCKER. The original architectural contradiction remains.

2. B1-6 remains a fundamental architectural contradiction

I checked both operative locations again.

§0.5 B1-6 says:

Supervisor spawns launcher.

Launcher creates the harness child.

Launcher returns the child PID and status to the supervisor.

Launcher exits.

Supervisor owns wait, terminal-event closure and issuance consequences.

§3.5 points 2–3 say:

Launcher forks the harness child.

Launcher is the child's OS parent.

The launcher remains alive throughout the child's lifecycle.

The same launcher thread drops privilege, releases the gate and owns the waitpid() relationship.

These are mutually incompatible process models.

This is especially consequential because the PR_SET_PDEATHSIG design depends on the launcher remaining alive as the child's parent. If the launcher exits immediately as §0.5 says, the child-parent relationship and its parent-death behaviour change. This is not a matter of choosing which paragraph is more authoritative.

The architecture must settle, as one coherent model:

Which process is the harness child's OS parent?

Which process owns waitpid()?

Which process owns terminal-event closure and issuance?

What does launcher exit mean?

Which parent does PR_SET_PDEATHSIG monitor?

What happens on launcher death and supervisor death at every relevant lifecycle point?

B1-6 remains OPEN and blocks clearance. I will not accept a wording-only reconciliation.

3. D-4 — full log independently inspected

I retrieved the newly shelved full log and compared it with the earlier extract.

Content reconciliation passed

Full log: 159 entries, all parseable.

Entries dated 2026-11-13: 12.

Distinct invocation IDs: 9.

All 12 Stage 5 entries match the shelved extract exactly.

No Stage 5 entries are missing from either record.

The three HTTP 429 failures and their paired log entries are preserved.

Q6 remains a non-answer, not an UNKNOWN.

The full-log reconciliation is now independently inspectable and reproduced at content level. I have not independently recomputed the supplied SHA256; the retrieved Git blob identifier is recorded above.

4. Additional issues

D-9 — Claude's conditional acceptance

Rev 15 states that Claude conditionally accepted the C launcher in his Rev 14 interim. I could not verify that statement from the Rev 14 specification pin or a retrievable primary interim record in the material inspected.

Keep it labelled as reported until the actual interim source is available. Do not turn it into an established inspector disposition from a summary.

The new C-language rationale needs technical tightening.

§0A.6 argues that C produces a static binary without a runtime, interpreter, garbage collector or unexamined standard-library machinery. Those are not guaranteed by choosing C alone. Static linking, libc dependencies, compiler and linker behaviour are build properties; other compiled languages can also produce small binaries without a managed runtime.

The rationale should distinguish:

Why a compiled launcher is necessary.

Which concrete properties the chosen C implementation must exhibit.

Why C is preferred over other viable compiled options.

Which compiler, linker, dependency and binary properties will be pinned and inspected.

I accept the need for a small, inspectable privileged component. I do not accept language choice by itself as proof of those properties.

D-18 remains an inspection blocker.

The Rev 11 finding texts must be recovered verbatim from the authorised 2026-11-12 chat record and made retrievable. No finding may be dispositioned from summaries. I agree with leaving D-18 OPEN.

5. Disposition

B1-2: ACCEPTED.

C-3: ACCEPTED.

D-11: ACCEPTED.

D-4: ACCEPTED; full-log reconciliation reproduced.

Introductory framing: ACCEPTED.

Stage 5 exception scope: ACCEPTED.

D-5: ACCEPTED as a qualified, partial verification.

D-9: PARTIALLY ACCEPTED; Claude's primary interim disposition remains unverified.

B1-6: OPEN — HIGH — BLOCKS BUILD CLEARANCE.

D-18: OPEN — BLOCKS INSPECTION COMPLETENESS.

C-language rationale: AMENDMENT REQUIRED.

Batch 1 remains CLEARED. Batch 2 remains CLOSED. Stage 6 remains UNAUTHORISED. No implementation or provider contact is authorised by this inspection.

6. Next work

Remmy, please preserve Rev 15 unchanged and prepare a considered architectural resolution for B1-6 before drafting another revision. Resolve the process model first, then align the specification and its failure demonstrations to that model. Keep the Claude Rev 11 recovery moving independently.

I can take the next independent pass on the proposed B1-6 architecture and the recovered D-18 source material, so you can keep your attention on the drafting and coordination.
