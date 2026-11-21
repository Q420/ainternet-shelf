# STAGE 5 BUILD SPECIFICATION 15 — THE NEMOTRON PILOT PACKAGE, BUILT AND PROVEN BEFORE ANY MODEL IS CALLED

**Pilot:** Nemotron governed-subject pilot (Plan 01, ADOPTED by Ben
2026-11-12; Alex adjudication pb-mwe90lo6)
**Stage:** 5 — Build + Independent Inspection (Plan 01, Stage 5)
**Status:** SPECIFICATION ONLY. This document authorises nothing.
Rev 15 is drafted against Alex's independent inspection of Rev 14
(pb-mwfkgkm5-i-gog7 — NOT CLEARED), whose nine required corrections
§0A answers item by item. Rev 15 is offered for Alex's next
independent inspection at its Shelf pin. It is not fit to build
from unless and until the inspections clear that pin and Ben
issues a re-issued build go naming the builder (§0.9, §0A).
Claude's inspection of Rev 14 was interrupted at interim by his
usage limit; his interim findings are on the record, and Ben has
directed the path be carried by Alex and Remmy meanwhile. Claude's
final dispositions remain his to give when he resumes.
Rev 15 is drafted by Remmy from the Rev 14 text at shelf pin
a1a188197bc599848f0e9b6f8c72b56744500e39 (file sha256
d1d390cdd75221cf857a14396ae19864c6e233f858d1ce17652c9b2b30a09789,
verified byte-identical at the working copy's creation), against
Alex's Rev 14 inspection verdict (shelved verbatim at commit
43f58ccfb10687494f9cf2f5eb142d4f36be364d as
duenna/ALEX-REV14-INSPECTION-VERDICT-2026-11-13.md). Rev 14
remains immutable history at its pin and is not modified by this
draft; Rev 13 likewise.
It is the paper the Stage 5 build will be worked from and judged
against. Rev 01 was drafted 2026-11-12 under Ben's tap of the
same date ("Draft the Stage 5 build spec (paper only, Alex
inspects before any build)"), from the verified design package
(§2), and shelved at commit
`49c505833b561ed24601d6b30f3753d64e7ef452`. Rev 02 was shelved
at commit `cb1035b7d0f3be2c1ea10025cf180622aceb0118`.
Rev 03 was shelved at commit
`df882598ea3301b8072d069b2814e289060985fa`.
Rev 04 was shelved at commit
`c48b1d60b3441b6170cb0c41b5d3a568b1441b14`.
Rev 05 was shelved at commit
`5329b74bdfad032bccb1610eca88f9c93802332a`.
Rev 06 was shelved at commit
`bf9626cf3353c12f0f2e715fc2e5a5352471266b`.
Rev 07 was shelved at commit
`0a40d630db20252233a4d9c4a285c88ff1f8763a`.
Rev 08 was shelved at commit
`6cd1716d7d655e7b379f5295fb4f358402aa3f5c`.
Rev 09 was shelved at commit
`4654725f701c4560ce29b961b425e9ba1578263f`.
Rev 10 was shelved at commit
`3d1488d2bf8bec71c4b034ed5ba7eab3bf0a04b2`.
Rev 11 was shelved at commit
`ce74026c1d8a527ed7d25812942fd995ebc40fa0`.
Rev 12 was shelved at commit
`875d91c01906b2d1822921ddb13f2fdcd2d55c8d`.
**Rev 15 (this document)** succeeds Rev 14; §0A records its
amendments. The material immediately following, through the
Rev 13 amendment summary, is **Rev 13's record preserved as
history**: it speaks of Rev 13 in Rev 13's own voice and states
nothing about Rev 15's status. It begins: Rev 13 answered Alex's
re-inspection of Rev 12 (pb-mwel2vwg). That re-inspection
**accepted Item 2's reversal expressly** — the Batch 0
catalogue listing struck from Stage 5, the design-time
snapshot carried into the freeze, the live listing at
Stage 6 pre-flight — and **accepted Items 3–9 entire**
and **Item 1 in substance**. One precision correction
remained, and it is the whole of this revision: the
Stage 5 isolation boundary is now **total**. Rev 12
barred a direct route to the provider host; a loopback
base URL, however, does not by itself prove the adapter
cannot reach an external service through a configured
HTTP proxy or another local forwarding service, and
blocking a direct route does not exclude an indirect
one. Item 1 now states the boundary as **no
non-loopback network egress at all** — loopback
interfaces only — the adapter **honours no proxy
configuration or forwarding mechanism** in Stage 5
mode, and gate G1's evidence must show the **actual
environment's** isolation: its interfaces inspected,
no external route, and **no available external proxy
or connector path** (Item 1, tightened; §3.7, §5,
§6.3 item 2). Itemised in the Rev 13 Amendment Summary
below. Everything else in Rev 12 — including
everything Alex accepted in it — is unchanged.** No code is built, no model call is made
or authorised, no shelf file is modified, by this document.
**What this spec is for.** Plan 01 Stage 5: "Build the adapter
and harness to the frozen specifications, then the constructed
pilot package is inspected BEFORE any live model execution." This
specification is the frozen build instruction for that stage: it
states what is to be built, in what order, against which pinned
sources, and which gates the constructed package must pass
before it is offered for independent inspection. The build
itself requires Ben's separate Stage 5 go (§7). Execution —
the first call to the subject — is Stage 6, under Ben's separate
authorisation, and **no part of Stage 5 calls the subject**: all
build verification runs against a scripted stub subject and a
local transport double (§3.7, §5).
**Inspection of this spec.** Two independent inspectors judge
this specification before any build: Alex (his offered
source-to-requirement crosswalk and harness-architecture
review), and Claude, independently (Ben's addition, 2026-11-12:
an extra set of eyes). Neither inspector is the builder
(Criteria §2: builder ≠ scorer ≠ examiner). Rev 13 is offered
to Alex for re-inspection against the single correction
itemised in the Rev 13 Amendment Summary: his Rev 12
re-inspection (pb-mwel2vwg) accepted Items 2–9 and Item 1's
substance, and withheld clearance on the Item 1
network-isolation precision alone; that precision is
answered here on its own terms.

---

## AMENDMENT SUMMARY — REV 13 (answering Alex's re-inspection, pb-mwel2vwg)

**Why this revision exists.** Alex's re-inspection of
Rev 12 (pb-mwel2vwg) **accepted Item 2's reversal
expressly** — his earlier acceptance of the Batch 0
catalogue listing is withdrawn on the reasoning Rev 12
gave: an authenticated request to the provider's live
host is provider contact, whatever it returns, and
Stage 5's boundary is zero provider contact. **Items
3–9 are accepted entire**, and the Rev 11 substance
his earlier clearance covered is preserved — Rev 12
added exactly one file, Rev 11 byte-identical at both
commits. **Item 1 is accepted in substance** — its
three layers (the adapter's loopback refusal, no
provider credential in the build environment, G1's
zero-egress evidence) are sound — with **one precision
correction** required. The verdict was **NOT CLEARED
on that point alone**. This revision makes exactly
that correction, and nothing else.

**The correction — Item 1's boundary is total (§3.7;
§5, gate G1; §6.3 item 2).** Rev 12's enforcement
framed the environment's isolation as **no outbound
route to the provider host**. Alex's gap: a loopback
base URL does not, by itself, prove the adapter cannot
reach an external service through a **configured HTTP
proxy or another local forwarding service**, and
blocking a direct route to the provider host does not
exclude an **indirect route through a proxy or
connector**. The boundary is therefore restated, in
each of the three places, as **total isolation**: the
Stage 5 build and gate environment has **no
non-loopback network egress at all** — loopback
interfaces only; the loopback transport double remains
available and unaffected. The adapter rule gains the
**proxy clause**: in Stage 5 mode the adapter **does
not use proxy configuration or any other forwarding
mechanism** to reach an external service — proxy
settings, however supplied, by environment or by
configuration, are **not honoured** in Stage 5 mode.
Gate G1's evidence is widened to match: the preserved
evidence must show the isolation of the **actual
environment** — its **interfaces inspected** (Alex's
example stands: a network namespace with no external
route), the **absence of any external route**, and the
**absence of an available external proxy or connector
path**; an environment whose evidence addresses only
direct routes **does not pass G1**. The fail-closed
consequences and the evidence preservation are exactly
Rev 12's; only the boundary's scope and the evidence's
required coverage change. The zero-provider-contact
requirement is now mechanically true of the
environment, not dependent on the intended behaviour
of a configuration.

**Accepted and untouched.** Items 2–9 stand as Alex
accepted them in pb-mwel2vwg and are **not amended**:
the catalogue reversal (Item 2), the C launcher as the
approved exception (Item 3), the honest sudo rationale
(Item 4), the Batch 0 launcher interface freeze (Item
5), the torn-write injector flag (Item 6), the JCS
implementation pin (Item 7), the stub-labelling check
recorded with no change (Item 8), and Batch 0's
custody-setup artefact and named probe (Item 9).

**Not changed.** Everything else carries over
untouched: the custody design entire, the record,
driver, tools, and registry specifications, the
adapter specification apart from Item 1's clauses,
gates G2–G5 entire and G1 apart from the widened
evidence above, the batch order, §6 apart from item
2's mirror of Item 1, and §7 entire. The Rev 12
Amendment Summary follows below as the record of the
previous round, unaltered.

**Flagged extra touches.** None beyond the round's
record: the header and this summary. The three
normative sites state the boundary once each,
consistently; no parallel text is added elsewhere, and
Rev 12's historical summaries are unaltered.

## AMENDMENT SUMMARY — REV 12 (answering Claude's independent inspection of Rev 11)

**Why this revision exists.** Rev 11 was **cleared by
Alex** (pb-mwefvrrm) — the specification he inspected
needed nothing further from him. Ben had also
commissioned **Claude as a second, independent
inspector** (his addition, 2026-11-12), and Claude's
inspection of Rev 11 — conducted cold, without Alex's
findings — returned **not yet fit to build**: three
High findings, three Medium, two Low, and two gaps,
each stated against the text he read, with his read's
own limits declared (a substantial partial inspection;
§§3.1–3.4, 3.6, and 4 less checked than the custody
and gate sections). Ben directed the findings folded
in (2026-11-12, 22:10 MST). This revision does exactly
that, and nothing else: every change below maps to a
numbered Claude finding or gap, and **the substance
Alex cleared carries over byte-for-byte apart from
these sites**.

**Item 2 first, because it reverses Alex — catalogue
evidence (Claude's finding 2, High).** Rev 01 recorded,
and Alex **accepted**, a read-only `GET /v1/models`
listing at Batch 0 as the freeze's catalogue evidence:
a listing is not a subject call. Claude's finding
strikes the default: the listing is an **authenticated
request to the provider's live host** — provider
contact, whatever it returns — and §3.7's no-call
wording named only chat completions, so the listing
passed the rule's letter against Stage 5's intent.
**Rev 12 takes Claude's ruling:** §6.3 item 5's default
is now the former fallback — the **design-time
catalogue snapshot carried into the freeze** — the
live listing is **removed from Stage 5** and taken at
**Stage 6 pre-flight** instead, where the catalogue is
re-evidenced against the live host before any run; the
Batch 0 text (§4) and §3.6's catalogue bullet are
aligned to match. **Alex's re-inspection is asked to
adjudicate this reversal expressly** — it strikes a
point he accepted, on the second inspector's
reasoning, and his clearance of Rev 11 does not extend
over it until he says so.

**Item 1 — the no-call rule is enforced, not stated
(Claude's finding 1, High; §3.7, §6.3 item 2, gate
G1).** Rev 11 *stated* that Stage 5 calls nothing;
nothing in it *stopped* a misconfigured adapter from
reaching the live endpoint, and the gates would still
have passed. Three enforcements are added. **(a)** In
Stage 5 mode the adapter **refuses any non-loopback
base URL**: a configuration naming a non-loopback
provider address fails closed at start-up, before any
run. **(b)** The build environment holds **no provider
credential** — credentials remain in the connector's
custody, outside the build environment — so the build
has nothing to authenticate with even if misconfigured.
**(c)** Gate **G1 records a zero-egress check**: the
build/gate environment runs with **no outbound route
to the provider host** (Claude's example: a network
namespace with no route out), the check and its result
are recorded in G1's evidence, and an environment where
egress cannot be shown absent does not pass G1. With
Item 2, §3.7's no-call wording is aligned once to cover
**any contact with the provider host** in Stage 5, not
only chat completions.

**Item 3 — the launcher's language is named (Claude's
finding 3, High; §3.5 point 2, §6.3 item 4).** §6.3
item 4 fixes Python as the build's default language
and Rev 11 never named the launcher's language or
flagged the exception — yet the launcher **cannot** be
Python: **Linux ignores the setuid bit on interpreted
scripts**, and §3.5 already describes the launcher as
compiled at build time. The launcher is now named as
implemented in **C**, compiled at build time, and
recorded in §6.3 item 4 as the **approved exception**
to the Python default, with the reason stated. The
rest of the build remains Python under item 4.

**Item 4 — the sudo rationale states the trade
honestly (Claude's finding 4, Medium; §3.5 point
4(iv)).** Claude accepted the custody design; the
*rationale* overclaimed. Rev 11 rejected a sudo rule
partly because it would "leave a standing privilege
rule invocable outside any run" — but the mode-`4710`
launcher is **equally** a standing privilege, invocable
by the `pilot-supervisor` identity outside any run.
(The brief for this revision cited this passage as
point 2(iv); the sudo rejection stands in the text at
point 4(iv) — the file's only sudo passage — and is
amended there.) The rationale now acknowledges the
equivalence, states that a **narrow sudoers entry is a
smaller trusted base than custom root code**, and
gives the one reason the launcher is nevertheless
chosen: it performs the whole custody sequence as
**one constrained program** — fixed operation, no
arguments, no shell, no general exec path — where sudo
would confer a general launch path onto whatever it
invokes, reintroducing interpreter ambiguity. The cost
is named plainly: custom root code is the larger
trusted base, mitigated by the pinned source, the
Batch 0 interface freeze (Item 5), and the code-order
inspections. The custody design itself is unchanged.

**Item 5 — the launcher's target is frozen at Batch 0
(Claude's finding 5, Medium; §4, Batches 0 and 4).**
Rev 11 pinned the launcher's source only at the Batch 4
checkpoint, after Batches 0–3 had been built on the
custody assumption. Batch 0 now freezes the launcher's
**required behaviour and interface** — operation set,
invocation contract, gate protocol, identity and
capability sequence obligations — alongside the other
freeze artefacts; Batch 4 implements **against the
frozen interface** and pins the resulting source at its
checkpoint, as before. Nothing about the launcher's
specified behaviour changes — only **when** its target
is fixed.

**Item 6 — the fault injector must not ship (Claude's
finding 6, Medium; §5, gate G2).** The torn-write test's
test-only slow/partial write path now exists only under
a **build-time flag** (`PILOT_TORN_WRITE_INJECTOR`),
settable only in the scratch/test build configuration.
A build outside the scratch context **refuses to compile
with the flag set**; the flag's state for the build
under examination is **recorded in G2's gate evidence**;
and a build carrying the injector is **not a scoreable
build** — its absence from any production or scoreable
build is demonstrated by the recorded flag state, not
asserted.

**Item 7 — the RFC 8785 implementation is pinned
(Claude's finding 8, Low; §3.4).** Rev 11 pins the
**standard** (RFC 8785) and names **no implementation**
— checked: §3.4 specifies the form and its rejection
rules without naming a library. Rev 12 adds the pin
obligation without inventing a library: the JCS
implementation is frozen at Batch 0 by **name, version,
and artefact hash** in the freeze evidence, must pass
the **RFC 8785 conformance vectors** as part of the
freeze checks, and any change of implementation or
version is a **re-freeze event**. No library is named
in this text; the pin is taken at Batch 0, from the
implementation the build actually uses.

**Item 8 — stub labelling: checked, no change (Claude's
finding 7, Low; §3.7).** Claude asked whether the
synthetic label is a field in the canonical record or
only a filename convention, and recorded that he did
not verify which. It was checked against §3.7's text
for this revision: the labelling is **structural** —
the governing passage reads: "the capture's subject
identity is the stub's visibly named configuration,
never the pinned model id; the run's `RUN_STARTED`
block pins the stub configuration as such; and the
examiner verifies the label as part of re-deriving the
stub run." The label lives in the capture record and
the run's genesis block, not in any filename. **No
amendment is made**; this item is recorded so Alex sees
the check was made.

**Item 9 — Batch 0's two gaps closed (Claude's gaps;
§4, Batch 0).** **(a)** The account, group, and
launcher-permission **setup** — operator work in Rev 11
with no recorded artefact — is preserved as a Batch 0
freeze artefact: the setup script, or a recorded
transcript of the manual steps. SE-7(vii) reads the
resulting state from the OS; the artefact evidences
**how the state came to be**. **(b)** The launcher
environment probe (§3.5 point 2: setuid viability,
`nosuid`, `no_new_privs`) names its owner and evidence
destination: **run by the operator**, its output
**preserved in the Batch 0 freeze evidence**; a failed
probe stops the build, as §3.5 already rules.

**Not changed.** Everything else carries over
untouched: the custody design entire — the gated
launch, both failure windows, the capability read-backs
and their methods, the three-class trust boundary, the
identity-continuity arrangement, demonstrations
(i)–(ix) — the record, driver, tools, and registry
specifications, the adapter specification apart from
Item 2's catalogue-evidence alignment in §3.6, gates
G3–G5 entire and G1/G2 apart from Items 1(c) and 6,
the batch order, §6 apart from items 2, 4, and 5 as
amended, and §7 entire. The Rev 11 Amendment Summary
follows below as the record of the previous round,
unaltered.

**Flagged extra touches.** Two, both alignments under
items above rather than new substance: §3.6's
catalogue bullet is aligned under Item 2 (it stated
the listing as captured at the Batch 0 freeze, which
Item 2 removes); and Item 4's amendment stands at
§3.5 point 4(iv) — the text's only sudo passage —
where this revision's brief cited point 2(iv). The
header and this summary are the round's record, as in
every revision.

## AMENDMENT SUMMARY — REV 11 (answering Alex's re-inspection, pb-mwefothz)

Alex's re-inspection of Rev 10 returned **NOT CLEARED —
two narrow precision corrections**. The
capability-state requirement is **accepted in
substance**: the child checks after its uid/gid
transitions and read-back, before the `PDEATHSIG`
arming, the descriptor closure, and the gate; the
parent checks after its own transition and read-back,
before the gate release; all three sets must be empty;
the observations are retained as launch evidence; a
child-side nonzero terminates the launch immediately,
without execution or issuance; a parent-side nonzero
invokes Window 2's cleanup — no release, the gate
closed unreleased, the child reaped, no issuance; and
demonstration (vii) requires the evidence for both
dropped processes and tests both fail-closed branches,
with a declared code-inspection alternative for each
side. The rationale correctly rests the guarantee on
the observed capability state, not on an assumption
derived from the transitions. The drift check found
**none**: Rev 09 fetched at Rev 10's commit returns
the same blob as at its own commit, and Rev 10 adds
exactly one file. What remains is the permitted
**method** of observation, one unclosed outcome, and
an agreed one-line alignment:

**Correction 1 — the observation method must
genuinely cover the ambient set (§3.5 point 3, child
half, where the method is defined; the parent half
takes it by its existing cross-reference).** Rev 10
permitted the read-back by the `/proc/self/status`
fields "**or an equivalent `capget` read-back**." The
equivalence is **false** for one of the three sets:
`capget` returns the effective, permitted, and
**inheritable** sets; it does **not** return the
**ambient** set, which is queried through `prctl`'s
`PR_CAP_AMBIENT` interface. A `capget`-only
implementation therefore cannot establish that all
three required sets are empty. The clause now
distinguishes the methods. **Method A:** the
`CapEff`, `CapPrm`, and `CapAmb` fields of
`/proc/self/status`, read and verified directly.
**Method B:** `capget` for the effective and
permitted sets, **plus** an explicit ambient
read-back — `prctl(PR_CAP_AMBIENT,
PR_CAP_AMBIENT_IS_SET, …)` queried for **every**
capability number from `0` to the maximum the kernel
supports, each query required to return `0`. The
clause closes in so many words: **a method that
cannot observe the ambient set does not satisfy this
requirement**. The zero requirement, the fail-closed
consequences, and the preservation of the observed
masks are exactly as Rev 10 specified them; only the
method text changes. The capability passage in the
identity-continuity block and demonstration (vii)'s
capability part were examined for the same defect:
neither names or restates the methods — the passage
speaks of the read-back without specifying it, and
(vii) cites the values recorded by point 3's
read-backs — so neither required correction, and the
single method definition in point 3 governs both
halves. Rev 10's Amendment Summary, following below
as the previous round's record, restates the
corrected equivalence ("or an equivalent `capget`
read-back"); it stands **unaltered** as that record,
and where it differs from §3.5's corrected method
text, the normative text governs.

**Correction 2 — the parent's failed read-back fails
closed expressly (§3.5 point 3, parent half).** Rev
10's child clause already barred the launch on a
capability state that was never observed; the parent
clause specified the consequence of a **nonzero**
observation but not of a **failed** one. The parent
clause now states the rule in full: the parent
**must not release the gate unless all three sets
have been successfully and unambiguously read and
verified empty**; any failure to obtain or interpret
the complete state — an unsuccessful, incomplete,
malformed, or unavailable read-back — is a failure
detected after the drop, and **Window 2's cleanup**
applies: no release byte, the gate closed unreleased,
the child reaped, no issuance, and the abort recorded
**noting the read-back failure as its cause**. One
alignment rides with this correction, flagged here
rather than made silently: the child clause's
failed-observation wording ("observed nonzero, or was
never observed") is aligned to the same express
standard — a capability state **not successfully and
unambiguously observed in full** bars the launch
identically — so the two halves state one standard.

**Alignment 3 — demonstration (viii)'s sequence
enumeration (agreed; one line).** The install-window
case's code-order enumeration now names **the
capability read-back** at its position in the pinned
sequence — "…transitions; verification; **the
capability read-back**; arming…" — so the enumeration
agrees with §3.5 point 3. Alex does not treat the
omission as a separate security blocker —
demonstration (vii) carries its own capability
inspection route — and nothing else in (viii)
changes.

**Not changed.** Everything else carries over
untouched: the capability requirement in substance
entire — both read-backs' placement in the sequence,
the three sets required empty, the observed masks as
launch and gate evidence, both fail-closed
consequences apart from Correction 2's express
failed-read-back rule and its flagged child-clause
alignment — Conditions 1, 2, and 3 entire, the
three-class trust boundary and the scoped
final-interval claims, the identity-continuity
mechanisms entire, the descriptor route recorded and
not adopted, both failure windows, the gate mechanics
and ordering, descriptor separation entire,
demonstrations (i)–(ix) apart from (viii)'s one-line
enumeration alignment, corrections B (RFC 8785,
§3.4) and C (the S7 pin and the §2 sweep), the
synthetic-capture specification (§3.7), gates G1–G5,
the no-model-call rule, the batch order, §6 entire,
and §7 entire. The Rev 10 Amendment Summary follows
below as the record of the previous round, unaltered.

---

## AMENDMENT SUMMARY — REV 10 (answering Alex's re-inspection, pb-mwefh3g8)

Alex's re-inspection of Rev 09 returned **NOT CLEARED —
one remaining evidence requirement**. Both of Rev 09's
corrections are **accepted**. The three-class trust
boundary stands as now stated: `pilot-harness` and
`pilot-supervisor` are untrusted identities whose
access is restricted by OS permissions; the privileged
launcher is trusted, pinned TCB code with root
authority in its privileged window, its restriction
established by its implementation and not by any
pretence that OS permissions bind root; the operator
and root outside the launcher stand outside the threat
model. The final-interval claims stand as scoped:
changes at or before the pre-release re-check are
detected and refused; changes after it, by an actor
with write authority, are not guaranteed detectable
and stand outside the threat model; the final
interval's protection is the absence of an in-model
writer, not the re-check. Demonstration (ix)'s scope
is consistent with its tests. And there was **no
drift**: Rev 08 fetched at Rev 09's commit returns the
same blob, byte-identical; Conditions 1–3, the
launcher sequence, the gate ordering, both failure
windows, descriptor separation, and demonstrations
(i)–(ix) are unchanged in Rev 09's stated scope. What
remains is a single evidentiary link underneath an
accepted claim: layer (1)'s permission guarantee
assumes the untrusted processes cannot bypass
discretionary access control, and Rev 09 nowhere
required that assumption to be checked. **Rev 10 adds
that check, and nothing else**: the capability-state
verification itemised below, in §3.5 point 3 (both
halves), in a capability passage in the
identity-continuity block, in SE-7 demonstration
(vii) — extended, not renumbered — and in point 4(v)'s
shorthand for those tests. No mechanism, ordering,
demonstration case, or other acceptance obligation
changes.

**The addition — observed capability state, required
empty, fail-closed (§3.5, point 3, child and parent
halves; identity-continuity block; demonstration
(vii), third part).** The permission enforcement layer
(1) relies on is discretionary: it does not bind a
process holding a capability that bypasses it —
`CAP_DAC_OVERRIDE`, `CAP_DAC_READ_SEARCH`, and
`CAP_FOWNER` are the bypass-relevant examples.
Point 3 therefore now requires, for **both** dropped
processes: **(a)** the **child**, after its credential
transitions and their `getres*` verification — with
the post-drop verification cluster, before the
`PDEATHSIG` arming, the descriptor close, and the
gate — reads its own capability state (the `CapEff`,
`CapPrm`, and `CapAmb` fields of `/proc/self/status`,
or an equivalent `capget` read-back) and requires
**all three sets empty**; any nonzero value in any set
means immediate `_exit()` — fail closed, the launch
does not proceed. **(b)** The **parent**, after its
own drop and `getres*` verification and **before** it
writes the release byte, performs the same read-back
on itself under the same requirement; any nonzero
value is a failure detected after the drop, and
**Window 2's cleanup applies** — no release byte, the
gate closed unreleased, the child reaped, no issuance
— with the abort recorded including the observed
masks. **(c)** The observed masks for both processes
are **preserved as launch evidence** — in the launch
record, alongside the launcher's `Threads` observation
(point 2) — so the guarantee rests on the observed
state at the point of reliance, not on the intended
uid/gid transitions alone. **(d)** Demonstration (vii)
gains a **third part**: the gate evidence for the
launcher tests must include the observed
`CapEff`/`CapPrm`/`CapAmb` values for both dropped
processes, each required zero, plus a **fail-closed
case** — a nonzero observation induced through the
test build's fault-injection hook feeding a synthetic
nonzero mask to the check — exercised against each
side's check, with the code-order-inspection route of
demonstration (viii)'s install-window case as the
stated substitute where a test build cannot interpose
on one side, and the gate evidence stating which proof
was used for each side. The rationale passage in the
identity-continuity block states why the expectation
is reasonable and why it is nevertheless verified: the
exec target's freedom from file capabilities
(Condition 3) is why the harness process cannot gain
capabilities at the exec, and the launcher's pinned
operation set contains no ambient-capability raising
(no `prctl(PR_CAP_AMBIENT)`) — and neither support is
treated as a substitute for observing the resulting
state.

**Not changed.** Everything else carries over
untouched: Conditions 1, 2, and 3 entire, the
three-class trust boundary and the scoped
final-interval claims as corrected in Rev 09, the
identity-continuity mechanisms entire (protected
placement, canonical resolution and the identity
record, the pre-release re-check, the freeze-time
path-component audit), the descriptor route recorded
and not adopted, point 3's sequence apart from the two
verification insertions above, point 4 apart from
(v)'s shorthand alignment, both failure windows, the
gate mechanics and ordering, descriptor separation
entire, demonstrations (i)–(ix) apart from (vii)'s
added third part and its retitling to name it,
corrections B (RFC 8785, §3.4) and C (the S7 pin and
the §2 sweep), the synthetic-capture specification
(§3.7), gates G1–G5, the no-model-call rule, the batch
order, §6 entire, and §7 entire. The Rev 09 Amendment
Summary follows below as the record of the previous
round, unaltered.

---

## AMENDMENT SUMMARY — REV 09 (answering Alex's re-inspection, pb-mwefa549)

Alex's re-inspection of Rev 08 returned **NOT CLEARED —
two remaining precision issues**, both in the new
identity-continuity material, and both about what the
document **claims**, not what it builds. The arrangement
itself stands: Rev 08 closes the original in-model
path-substitution gap in principle; Conditions 1 and 2
remain accepted — the pre-fork expected-parent capture
and both comparisons, the single-threaded launcher
requirement and its evidence; Condition 3's three-part
restriction remains accepted; the credential-transition
ordering, the fail-closed `PDEATHSIG` arming and its
read-back, both failure windows, the gate mechanics,
descriptor separation, and the prior demonstrations are
all carried forward; demonstration (ix) was added
without renumbering (i)–(viii); and there was **no
drift** — Rev 07 fetched at Rev 08's commit returns the
same blob, byte-identical. **Rev 09 changes only claim
language**: in §3.5's identity-continuity block and
point 3's exec-condition passage, in demonstration
(ix)'s framing, in point 4(v)'s shorthand for those
tests, and in this summary and the header. No
mechanism, ordering, demonstration case, or acceptance
obligation changes. Itemised:

**Correction 1 — layer (1) and the privileged launcher
(§3.5, verification block; point 3's summary phrase
aligned).** Rev 08's layer (1) said no identity
participating in a launch — explicitly including the
launcher in either of its identities — can modify,
replace, rename, or unlink the executable, the
interpreter, or any path component, and that for
in-model identities substitution is impossible because
the write access it requires does not exist. That is
**false as stated about the launcher**: the launcher is
a setuid-root binary, and in its privileged window its
effective identity is root; root can write root-owned
files and `0755` directories, and OS permissions do not
prevent it. The claim mistook a property of the
launcher's pinned code for a property of the operating
system. The text now states the trust structure in
three classes, explicitly: **(a)** the **untrusted
in-model identities** — `pilot-harness` and
`pilot-supervisor` — for whom OS permissions genuinely
prevent alteration of the protected tree, so that for
these identities substitution is impossible by
permission; **(b)** the **privileged launcher** —
trusted, pinned TCB code: during its privileged window
it **has** the OS-level ability, and the boundary rests
on its pinned implementation, which contains no
operation that modifies, replaces, renames, unlinks, or
redirects the protected installation tree (its
operation set is the spawn sequence only; it performs
no file writes while privileged), evidenced by the
source pin, the specified operation set, and the SE-7
launcher demonstrations — the same footing on which
point 4's corrected TCB wording states the launcher's
authority in its privileged window; **(c)** the
**operator and root** acting outside the launcher —
outside the threat model, as already stated. Point 3's
one-line summary of the arrangement ("protected
placement no in-model identity can modify") is aligned
to the same distinction.

**Correction 2 — the final interval and what the
re-check detects (§3.5, verification block, layers (1)
and (3); demonstration (ix)'s framing; point 4(v)'s
shorthand aligned).** Rev 08's layer (3) — and layer
(1)'s parenthetical, which said layer (3) addresses
out-of-model substitutions "as detection" — claimed the
re-check makes any out-of-model substitution
**detectable and fail-closed**. Too broad: a
substitution by an actor holding write authority over
the tree, landing **after** the parent's pre-release
re-check and **before** the child's `execve`, would not
be detected by that re-check. The statements are now
consistent in every place they appear: a substitution
landing **at or before** the re-check is detected by it
— identity mismatch, no release, gate cleanup, recorded
abort; a substitution landing **after** the re-check,
by an actor with write authority, stands outside the
threat model and is **not guaranteed detectable** — no
detection is claimed for it; and the final interval's
protection is stated as what it is — the **absence of
an in-model writer** under layer (1) as corrected —
not the re-check, whose role is to bind the verified
identity to the moment of release against everything
that happened before it. Demonstration (ix)'s framing
now says the same of its cases: they demonstrate
detection of substitution arranged before launch and of
redirection arranged after pre-launch verification but
before the pre-release re-check; they do **not**
demonstrate detection of a substitution landing after
the re-check, and no claim implies they do.
Demonstration (ix)'s cases themselves are unchanged.

**A note on the previous summary.** The Rev 08
Amendment Summary below stands unaltered as the record
of its round, per the standing convention — including
its restatements of both claims corrected here ("no
identity that participates in a launch … can modify,
replace, rename, or unlink"; the re-check making any
out-of-model substitution "detectable and
fail-closed"). Those restatements are the historical
record of what Rev 08 claimed; the normative text of
§3.5 as corrected here is what Rev 09 claims, and where
the two differ the normative text governs.

**Not changed.** Everything else carries over
untouched: Conditions 1, 2, and 3 entire — the pre-fork
identity capture and both comparisons, the fail-closed
arming, the `PR_GET_PDEATHSIG` read-back, the
single-threaded launcher and its evidence, the
three-part exec restriction and its two verification
points — the identity-continuity **mechanisms** entire
(protected placement, canonical resolution and the
identity record, the pre-release re-check, the
freeze-time path-component audit), the descriptor route
recorded and not adopted, both failure windows, the
gate mechanics and ordering, descriptor separation
entire, point 4's custody account apart from point
4(v)'s shorthand alignment named above, demonstrations
(i)–(ix) apart from (ix)'s added framing paragraph,
corrections B (RFC 8785, §3.4) and C (the S7 pin and
the §2 sweep), the synthetic-capture specification
(§3.7), gates G1–G5, the no-model-call rule, the batch
order, §6 entire, and §7 entire. The Rev 08 Amendment
Summary follows below as the record of the previous
round, unaltered.

---

## AMENDMENT SUMMARY — REV 08 (answering Alex's re-inspection, pb-mwef1a9w)

Alex's re-inspection of Rev 07 returned **NOT CLEARED —
one remaining verification gap**, in Condition 3.
**Conditions 1 and 2 are accepted outright**: the
pre-fork identity capture — the parent capturing its own
identity before the fork, the child's two comparisons
against that inherited value — closes the false-success
scenario of Rev 06; and the single-threaded launcher is
accepted as a normative design requirement, the
specification correctly reflecting that the `PDEATHSIG`
parent is the thread that created the child, with the
source restriction and the launch-time `/proc` `Threads`
check as complementary evidence. **Condition 3's
restriction semantics are accepted**: the three-part
restriction itself — not setuid, not setgid, no
associated file capabilities — is correct, it applies to
the actual executable the kernel invokes, interpreter
included, and the build-time and pre-launch checks are
sensible as far as they go. Demonstration (viii) as
revised is accepted, including the pre-first-instruction
case and the corrected code-order sequence. There was
**no drift**: the comparison from Rev 06 to Rev 07
reports exactly one added file, and Rev 06 fetched at
both commits returns the same blob — byte-identical.
**Rev 08 changes only §3.5's executable-verification
material — point 3's exec-condition passage, point
4(v)'s test list, and the verification block after
point 4 — the SE-7 list, where a new demonstration (ix)
is added with (i)–(viii) untouched, the
demonstration-range citations this forces in §4 Batch 4
and §5 gate G3, and this summary and the header.**
Itemised:

**The gap — the check does not yet bind to the use.**
Rev 07 requires the supervisor to `stat` and `getcap`
the executable and any interpreter before invoking the
launcher, and the launcher then executes a **fixed
path**. Those checks establish the properties of the
files **at inspection time**; they do not by themselves
establish that the exact same executable objects are
still present when the child executes them. If the file
or an interpreter can be replaced, or a symlink or a
writable directory component can redirect resolution,
**between verification and execution**, the child could
execute an object whose setuid bit, setgid bit, or file
capabilities were never checked — and the backstop whose
persistence the condition exists to protect would be
cleared by an exec the verification never saw. A
time-of-check/time-of-use gap, inside the one condition
whose whole purpose is what the exec does to the
backstop.

**The correction — identity continuity, in three layers
(§3.5, the verification block after point 4; point 3's
exec-condition passage aligned).** **(1) Protected
placement — the writer is removed.** The harness
executable and any interpreter it runs through live
under a protected installation tree: the files
themselves, and **every directory component of their
resolved paths**, are owned by root and not writable by
any other identity (directories mode `0755` or stricter;
the executables root-owned, not writable by group or
other). Within the pilot's threat model, no identity
that participates in a launch — `pilot-harness`,
`pilot-supervisor`, the launcher in either of its
identities — can modify, replace, rename, or unlink the
executable, the interpreter, or any path component:
replacement is not merely detected, it is **impossible**
for in-model identities. (The machine's operator and
root remain outside the threat model, per the standing
limit stated in §3.5.) **(2) Canonical resolution and
identity record — the object is named, not the path.**
At the freeze (Batch 0 re-freeze) and at the
supervisor's pre-launch verification, the executable and
interpreter paths are resolved **canonically** — every
symlink resolved — and the verification records the
resolved object's **identity**: device and inode
(`st_dev`, `st_ino`), mode bits, and capability set, for
both the executable and the interpreter, alongside the
three-part restriction checks themselves. The freeze
additionally records an **audit of every path
component's owner and mode**, evidencing layer (1).
These identity records are part of the gate evidence
and of the run's pre-launch record. **(3) Pre-release
identity re-check — check and use are bound.** After
the child's setup and before the parent writes the
release byte, the launcher parent **re-resolves** the
fixed paths and **re-stats** the resolved objects; the
device and inode, mode, and capability results must
match the verified identity records **exactly**. Any
mismatch is a launch failure on the established pattern:
no release byte is written, the gate cleanup runs per
the applicable failure window, no issuance occurs, and
the supervisor records the abort with the observed
identity values — the same abort-record discipline as a
descriptor-destination mismatch. The closing argument is
stated in the text: the interval between this re-check
and the child's `execve` is covered by layer (1) — no
in-model identity holds write access to the objects or
their paths during it — so the object re-checked is the
object executed; and the re-check makes any out-of-model
substitution (by the operator, say) **detectable and
fail-closed** rather than silent. The limit is stated
with it, honestly: against an actor who can write the
protected tree — root, the operator — acting inside
that interval, no arrangement at this layer suffices,
and that actor already stands outside the stated threat
model.

**The descriptor route — recorded, not adopted.** One
passage in the same block records the stronger
arrangement and the judgement against it as baseline:
executing through pre-verified open file descriptors
(`execveat` with `AT_EMPTY_PATH`) would eliminate the
interval by construction, and is **not** adopted — the
harness's interpreter-mediated invocation makes the
descriptor form for the interpreter-and-script pair
substantially more intricate, and the
protection-plus-identity arrangement above is the
specified mechanism. The passage is a recorded design
judgement the inspector may strike; it leaves no menu
open for the builder — layers (1)–(3) are normative.

**Demonstration (ix) — executable identity continuity
(SE-7 list).** A new demonstration proves the
arrangement adversarially, in a scratch tree: **(a)** a
**substitution** case — an out-of-model writer (the test
harness acting as root) replaces the executable with a
scratch copy carrying a setuid bit **after** the
freeze-time verification; the substitution is arranged
before any launch, so the supervisor's **pre-launch
verification** is the checkpoint expected to fire first
— with the case also satisfied if the parent's
pre-release re-check is the one that fires, provided
the substituted object is never executed; **(b)** a
**redirection** case — a symlink component in a scratch
path is repointed **after** the supervisor's pre-launch
verification has passed, so the parent's **pre-release
re-check** is the checkpoint expected to fire first,
canonical re-resolution and identity comparison catching
what the path alone would have hidden; **(c)** the
freeze-time **path-component audit** itself evidenced —
a component in a scratch tree deliberately made
group-writable (or mis-owned), which the audit must
flag, the tree's identity record not established as
verified until the defect is corrected. In (a) and (b)
the refusal carries the established consequences: no
execution of the unchecked object, the gate cleanup
where a launch had begun, and the abort recorded with
both identity records.

**Cross-references forced by the new demonstration.**
§3.5 point 4(v)'s range, §4 Batch 4's checkpoint, and
§5 gate G3 now cite the launcher demonstrations as
**(v)–(ix)**, and point 4(v)'s enumeration gains the
identity-continuity tests — the same pattern as prior
revisions. No other cross-reference needed changing:
demonstration (ix) is an addition to the SE-7 list, not
a renumbering, and (i)–(viii) stand exactly as written.

**Not changed.** Everything Alex accepted in pb-mwef1a9w
carries over untouched: Conditions 1 and 2 entire — the
pre-fork identity capture, both comparisons against the
inherited expected value, the fail-closed arming and
the `PR_GET_PDEATHSIG` read-back, the single-threaded
launcher and its evidence — Condition 3's three-part
restriction itself, the two failure windows entire, the
gate mechanics, ordering, and release condition, the
honest residual and its exclusion by construction,
descriptor separation entire — the exhaustive close,
the declared destinations and their verification, the
pipe-identity sentence — the supervisor-side invariant,
the gate-read-end reconciliation, demonstrations
(i)–(viii) entire, corrections B (RFC 8785, §3.4) and C
(the S7 pin and the §2 sweep), the synthetic-capture
specification (§3.7), gates G1–G5 apart from G3's
demonstration range above, the no-model-call rule, the
batch order, §6 entire, and §7 entire. The Rev 07
Amendment Summary follows below as the record of the
previous round, unaltered.

---

## AMENDMENT SUMMARY — REV 07 (answering Alex's re-inspection, pb-mweestgx)

Alex's re-inspection of Rev 06 returned **NOT CLEARED —
three remaining technical conditions**, all in the
parent-death backstop's parent-identity semantics. The
Rev 05 defect itself is **correctly fixed and accepted**:
the credential ordering — arming after the verified
transitions — is right, and the post-release proof is the
correct proof of persistence across credential drop and
exec. Also accepted, unchanged: the **two failure
windows** and demonstration (viii)'s coverage of both;
the **gate mechanics and release ordering**; **pipe
identity and descriptor separation** entire; and the
**install-window proof**, with one qualification carried
into Condition 1 below. There was **no drift**: the
commit comparison shows exactly one added file, Rev 05
byte-identical at the Rev 06 commit, and the accepted
material stands as accepted. **Rev 07 changes only
§3.5's backstop and launch material — point 2's launcher
properties, point 3's child sequence and backstop
restatement, point 4(v)'s test list, and the
destination-verification block — demonstration (viii)'s
install-window coverage, and this summary and the
header.** Itemised:

**Condition 1 — the expected parent identity is captured
before the fork (the blocking race).** Rev 06 had the
child record its parent's identity by a `getppid()` taken
immediately after the fork, and compare a later
`getppid()` against that recorded value. The comparison
is only as good as the value recorded — and that value
can already be wrong. If the parent dies **before the
child's first instruction**, the child is reparented
before it ever runs; its first `getppid()` returns the
**reaper's** identity, not the launcher's; the
post-arming comparison against that same reaper value
then **passes falsely**, and the child proceeds — armed,
moreover, against a parent thread that has already
terminated, in which case the manual states no signal
will be sent. The exact race the re-check was intended
to close remained open at its first step. **Corrected
(§3.5 point 3):** the expected parent identity is
captured by the **parent, before the fork** — its own
`getpid()` — and reaches the child as an **inherited,
immutable** value in its memory image, which nothing
outside the child's own pinned code can alter after the
fork. The child's sequence is now: **(1)** a first
comparison, as its first act — `getppid()` against the
inherited expected value; a mismatch (a death before the
child's first instruction) means `_exit()` without
proceeding; **(2)** supplementary groups,
`setresgid()`/`setresuid()`, and the read-back
verification, exactly as before; **(3)** the arming,
under the fail-closed conditions below; **(4)** the
re-check — `getppid()` against the **same** expected
value; a mismatch (a death between the first comparison
and the completed arming) means `_exit()`; **(5)**
descriptor closure and the gate wait, exactly as before.
The two comparisons against the one pre-fork value close
**both** intervals Alex named, and the text states the
manual's warning in substance: if the parent thread has
already terminated by the time `PR_SET_PDEATHSIG` is
called, no signal will be sent — which is why the
identity the child arms against must be proven live at
both checks.

**Condition 2 — the backstop's parent is the forking
thread; the launcher is single-threaded (§3.5 point 2,
and the backstop restated in point 3).** Linux defines
the `PDEATHSIG` parent as **the thread that created the
child**, not necessarily the parent process as a whole.
In a multithreaded launcher the forking thread could
terminate while the process lives on — triggering the
parent-death semantics — while a process-level
`getppid()` comparison still sees the same process
identity; Rev 06 spoke of the parent process throughout,
which does not meet the documented semantics.
**Corrected:** §3.5 now states the thread semantics as
documented, and makes the distinction empty by
construction as a normative property of the design: the
launcher is a **single-threaded** programme across the
whole launch lifecycle — its pinned implementation
contains no thread creation — so the forking thread is
the process's only thread, thread identity and process
identity coincide, the pre-fork capture records that one
identity, and that same thread is the one that drops
privilege, releases the gate, and `waitpid()`s, alive
until the child's lifecycle completes. The gate evidence
gains a launch-time record of the fact — the `Threads`
field of the launcher's `/proc` status equal to `1` at
launch — in addition to the source property under the
pin.

**Condition 3 — the exec must exclude setgid and file
capabilities too (§3.5 point 3, and the verification
block after point 4).** Rev 06 conditioned the
backstop's persistence across the exec on the target
being non-setuid. That is necessary and not sufficient:
Linux also clears the setting when the exec'd binary is
**setgid**, or carries **associated file capabilities**.
**Corrected:** the exec condition is now three-part —
the fixed harness executable must be **not setuid, not
setgid, and without associated file capabilities** — and
it applies to the **actual executable the kernel
invokes**, including the interpreter binary where the
fixed harness path runs through one. The verification
duties land with it: at build and freeze time — at the
Batch 0 re-freeze, and whenever the executable or its
interpreter is produced, replaced, or pinned — the mode
bits and capability set of the executable (and of any
interpreter) are checked and recorded in the gate
evidence (the `stat` mode; the `getcap` output); and
the supervisor's **pre-launch verification** — the same
pass that verifies the retained descriptors'
destinations — **re-checks** them for the specific
launch, and a target failing any of the three conditions
means no launch, with the abort recorded as for a
descriptor mismatch.

**The arming's own fail-closed conditions (§3.5 point
3).** Folded into the same passage, as Alex required: a
**non-zero return** from `prctl(PR_SET_PDEATHSIG, …)`
means the child `_exit()`s immediately and **never**
continues to the descriptor close or the gate; and a
**`PR_GET_PDEATHSIG` read-back** follows a successful
arming — the child requires the value read back to equal
`SIGKILL` before proceeding, the read-back standing as
the direct evidence the requested setting is present.
Failure or mismatch at either step means immediate
`_exit()`.

**Demonstration (viii) — the corrected sequence is what
gets proven.** The install-window case's
code-order-inspection alternative must now inspect the
**corrected** sequence — the pre-fork identity capture,
both comparisons against the inherited expected value,
the `prctl()` return-value check, and the
`PR_GET_PDEATHSIG` read-back; an inspection of any
shorter sequence proves the wrong sequence. A
**pre-first-instruction case** is added: the parent
killed in the interval between the fork and the child's
first comparison, the child shown exiting at that
comparison without proceeding to the transitions, the
arming, or the gate — induced directly where the test
build can hold that interval, otherwise covered by the
same code-order route, with the gate evidence stating
which proof was used; omitting the case satisfies
neither route. The post-release parent-death case and
both failure-window cases stand unchanged.

**Not changed.** Everything Alex accepted in pb-mweestgx
carries over untouched: the credential ordering entire,
the two failure windows entire, the gate mechanics,
ordering, and release condition, the honest residual and
its exclusion by construction, descriptor separation
entire — the exhaustive close, the declared destinations
and their verification, the pipe-identity sentence — the
supervisor-side invariant, demonstrations (v), (vi), and
(vii) entire, demonstration (viii) apart from the
install-window and pre-first-instruction coverage above,
the cross-references to demonstrations (v)–(viii) in §4
Batch 4 and §5 gate G3, corrections B (RFC 8785, §3.4)
and C (the S7 pin and the §2 sweep), the
synthetic-capture specification (§3.7), gates G1–G5,
the no-model-call rule, the batch order, §6 entire, and
§7 entire. The Rev 06 Amendment Summary follows below as
the record of the previous round, unaltered — including
its restatement of the exec condition as non-setuid
alone, which stands as that round's record; the
normative condition is §3.5's, extended here.

---

## AMENDMENT SUMMARY — REV 06 (answering Alex's re-inspection, pb-mweekpmz)

Alex's re-inspection of Rev 05 returned **NOT CLEARED — one
blocking technical defect**, in the parent-death backstop
Rev 05 added. The rest of Rev 05 was accepted: the **two
failure windows** — Window 1's direct `SIGKILL` while the
parent still holds privilege, Window 2's gate-close cleanup
once it does not, neither window issuing or releasing — are
**accepted**, and demonstration (viii) now tests both,
including the post-drop verification mismatch; the
**pipe-identity clarification** is **accepted**; and the
accepted material showed **no drift** — Rev 04 itself
stands byte-identical at the Rev 05 commit, and the Rev 05
diff was the one new file. **Rev 06 changes only the
child's setup ordering in §3.5 point 3 — with the backstop
restated in point 3's parent half and point 4(v) aligned —
SE-7 demonstration (viii)'s backstop coverage, the false
claim wherever it appeared, and this summary and the
header.** Itemised:

**The defect — a factual error about Linux, caught by
inspection.** Rev 05 placed the child's arming of
`PR_SET_PDEATHSIG` **before** its `setresgid()` /
`setresuid()` transitions, and justified the placement by
stating the setting is "a per-process attribute the child
may set for itself, which survives the child's credential
change." **That statement is false.** The Linux `prctl(2)`
documentation states that the parent-death signal setting
is **cleared** when the process changes its effective user
ID or effective group ID. The child's own credential
transitions therefore **silently disarmed the backstop**
Rev 05 claimed: in exactly the phase the backstop exists
for — a parent death once the launch is under way, above
all after the gate has been released and the harness is
running — no backstop was in fact armed. The gate remained
the primary pre-execution protection throughout, and Rev
05's two failure windows are untouched by this defect;
what did not exist was the kernel-level guarantee stated
behind them.

**The correction — the child's normative setup sequence in
§3.5 point 3 reordered.** (1) The child records its
parent's identity (`getppid()`) immediately after the
fork. (2) It establishes its supplementary groups and
completes its GID/UID transitions (`setresgid()`, then
`setresuid()`, all three ids), exactly as before. (3) It
verifies the resulting credentials by the existing
read-back; any failure still means immediate `_exit()`.
(4) **Only then** does it arm the backstop —
`prctl(PR_SET_PDEATHSIG, SIGKILL)` — and **no credential
change follows the arming** anywhere in the sequence: the
exec that ends it is a plain exec of a non-setuid
programme under the same identity and changes no
credentials, so the armed backstop **persists into the
running harness** — which is what makes the post-release
parent-death case work. (5) Immediately after arming, the
child **re-checks the parent relationship**: `getppid()`
must still return the parent recorded at step 1; if it
differs — the parent died during the setup window, before
the signal existed, and the child has been reparented —
the child `_exit()`s without proceeding, closing the
install-window race. (6) Only then the descriptor closure
and the gate wait, exactly as before. The parent half of
point 3 restates the backstop with the corrected placement
and semantics, the setup-window interval and its re-check
closure stated there too; point 4(v)'s test list is
aligned to name the post-release case. The false
"survives the child's credential change" claim is
corrected **wherever it appeared**: §3.5 point 3, both
halves — and, by deliberate exception to this document's
convention that prior amendment summaries stand unaltered,
the backstop paragraph of the Rev 05 Amendment Summary
below, corrected in place and marked as corrected there.
A statement of mechanism that is false is not left
standing in a current specification for a later reader to
rely on; the error, and this correction of it, are
recorded in both places so neither is silent.

**Demonstration (viii) — the backstop's coverage extended,
so the test proves the arming survives.** A **post-release
parent-death case** is now an explicit required case: a
full launch completes — credentials dropped and verified,
backstop armed after the drop, gate released, the harness
(the stub, in the test build) running — the parent is then
killed, and the evidence must show the running child
terminated by the backstop's `SIGKILL`. The pre-release
parent-death variant is retained, but it exercises a child
that has not yet exec'd and **cannot by itself prove** the
arming persisted past the credential transitions and the
exec; the post-release case is that proof. An
**install-window case** is also required: the parent
killed during the child's setup window, before arming
completes, with the child shown exiting at its step-5
re-check without executing — induced directly where the
test build can hold the child in that window; where it
cannot induce the timing deterministically, the obligation
is met by **code-order inspection** of the pinned child
sequence against the pinned source, and the gate evidence
must state which of the two proofs was used. Omitting the
case satisfies neither route.

**Not changed.** Everything Alex accepted in pb-mweekpmz
carries over untouched: the two failure windows entire,
the gate mechanics, ordering, and release condition, the
honest residual and its exclusion by construction,
descriptor separation entire — the exhaustive close, the
declared destinations and their verification, the
pipe-identity sentence — the supervisor-side invariant,
demonstrations (v), (vi), and (vii) entire, demonstration
(viii) apart from the backstop coverage above, the
cross-references to demonstrations (v)–(viii) in §4 Batch 4
and §5 gate G3, corrections B (RFC 8785, §3.4) and C (the
S7 pin and the §2 sweep), the synthetic-capture
specification (§3.7), gates G1–G5, the no-model-call rule,
the batch order, §6 entire, and §7 entire. The Rev 05
Amendment Summary follows below as the record of the
previous round — with its backstop paragraph corrected in
place, as recorded above.

---

## AMENDMENT SUMMARY — REV 05 (answering Alex's re-inspection, pb-mweedh0x)

Alex's re-inspection of Rev 04 returned **NOT CLEARED — one
remaining failure-path inconsistency** in the gated launch.
Both of Rev 04's requested amendments were found
substantially correct: the retained-descriptor gap is
**closed** — the declared destinations, the pre-launch
verification of destination and access mode, the refusal
with the abort recorded, the negative test, and the gate
read-end reconciliation are all accepted — and the gated
launch **closes the original parent-transition race**: the
child drops, verifies, closes, and blocks; the parent drops,
verifies, and releases only on success; parent death before
release yields end-of-file and the child exits unexecuted.
The accepted Rev 03 material and the cross-references to
demonstrations (v)–(viii) were compared section by section
and show **no substantive drift**. **Rev 05 changes only
the parent-failure cleanup in §3.5 point 3 (with point 4(v)
aligned and the backstop placed in point 3's child half),
SE-7 demonstration (viii), one clarifying sentence in
§3.5's destination-verification paragraph — Alex's noted
implementation detail on the accepted descriptor material —
and this summary and the header.** Itemised:

**Amendment 1 — The parent-failure cleanup rebuilt around
the gate (§3.5 point 3 rewritten in its parent half; the
child half gains the backstop's placement; §3.5 point 4(v)
aligned; SE-7 demonstration (viii) extended).** Rev 04
required the parent, on any transition failure or mismatch,
to kill the waiting child with `SIGKILL` and reap it. But
the parent drops all three of its ids to `pilot-supervisor`;
a failure surfaced by the post-drop verification read-back
is discovered at a moment when the parent may no longer hold
permission to signal a `pilot-harness` child across the uid
boundary — the cleanup assumed authority the parent may
already have surrendered. Rev 05 distinguishes the **two
failure windows** and makes **the gate itself the kill
switch**:

- **Window 1 — the failure is detected before the parent's
  drop has taken effect** (a `setres*()` call itself fails;
  the parent is still privileged). Direct termination is
  available in this window and is used: the parent kills
  the waiting child (`SIGKILL`), closes the gate write end
  without writing the release byte, reaps the child with
  `waitpid()`, and only then terminates itself. No issuance.
- **Window 2 — the failure is detected after the drop** (the
  `getres*()` read-back mismatches, or any later pre-release
  failure). The parent does **not** rely on signalling: it
  closes the gate write end without writing the release
  byte; the waiting child observes end-of-file and
  `_exit()`s itself, under the gate rule already stated;
  the parent `waitpid()`s and reaps it, then terminates
  itself. No issuance. In **neither** window is the release
  byte written, and in neither window does the child
  execute.

**Parent-death backstop (same amendment; placement and
grounds corrected by Rev 06 — see the Rev 06 Amendment
Summary above).** As corrected by Rev 06, the child sets
**`PR_SET_PDEATHSIG`** to `SIGKILL` on itself **after** its
verified privilege drop, and re-checks the parent
relationship immediately after arming. Rev 05 as originally
written placed the arming before the drop and claimed the
setting "survives the child's credential change"; that
claim was false — the setting is **cleared** by an
effective-credential change — and the placement silently
disarmed the backstop. As corrected: if the parent dies at
**any** point after arming, mid-failure, mid-cleanup,
during the run, or otherwise, the kernel terminates the
child directly, with no process needing signal authority
over it. This is a second, kernel-level guarantee
**behind** Rev 04's end-of-file path, not a replacement
for it: in the orderly failure windows the gate resolves
first; the backstop covers the parent vanishing in a state
where orderly cleanup never runs.

**The residual, stated honestly.** If a child were to
disobey end-of-file while the parent lives, no unprivileged
mechanism remains to the parent — this spec does not assume
one. That case is excluded **by construction**, not handled
by authority: the pinned child sequence has exactly two
post-read branches — the release byte, and only the release
byte, leads to the exec; **anything else, including
end-of-file, leads to `_exit()`** — the child's code is part
of the pinned trusted computing base (§3.5 point 4(iv)), and
demonstration (viii) exercises that pinned sequence's
behaviour directly. No stronger mechanism is claimed.

**Demonstration (viii) extended.** The induced-failure cases
now include **Window 2 explicitly** — a verification
mismatch induced to surface **after** the parent's effective
root is gone — alongside the pre-drop failure and the
parent-death variant, so the test cannot prove only the easy
case. The assertions stand in every case: the harness never
executes; no child process survives; the child is reaped by
the parent — in the parent-death variant the child is
kernel-terminated (by the gate's end-of-file or by the
death-signal backstop) and its exit is observable in the
test's recorded evidence — and no START commitment or
issuance entry exists for the aborted launch.

**Amendment 2 — Alex's builder note on the accepted
descriptor material (§3.5, declared-destinations block; a
clarification, not a design change).** Where a retained
descriptor's declared destination is a pipe, verification
must establish that it is **the actual pipe end held and
drained by the supervisor** — the identity of the pipe,
matched against the supervisor's own held descriptors — not
merely that the `/proc/self/fd/` target has the form
`pipe:[...]`.

**Not changed.** Everything Alex accepted in pb-mweedh0x
carries over untouched: the retained-descriptor declaration
and verification (subject only to Amendment 2's
clarification), the gated launch's ordering, gate rule, and
release condition (subject only to Amendment 1's cleanup
correction), the descriptor close and the supervisor-side
invariant, demonstrations (v), (vi), and (vii) entire, the
cross-references to demonstrations (v)–(viii) in §4 Batch 4
and §5 gate G3, corrections B (RFC 8785, §3.4) and C (the
S7 pin and the §2 sweep), the synthetic-capture
specification (§3.7), gates G1–G5, the no-model-call rule,
the batch order, §6 entire, and §7 entire. Rev 04's
Amendment Summary follows below, unaltered, as the record
of the previous round.

---

## AMENDMENT SUMMARY — REV 04 (answering Alex's re-inspection, pb-mwee6msu)

Alex's re-inspection of Rev 03 returned **NOT CLEARED — two
remaining custody gaps** in §3.5's launcher design. Everything
else in Rev 03 was **accepted**: the descriptor close from
fd `3` upward, the supervisor-side rule against holding
writable commitment descriptors across a launch, the
adversarial inherited-descriptor test, the precise
`setresgid()`/`setresuid()` transitions with verification
(subject to the handshake below), group separation and its OS
evidence, the Linux setuid probe with the `nosuid` /
`no_new_privs` checks, and the corrected root-authority and
TCB wording. The Batch 4 and G3 cross-references to
demonstrations (v)–(vii) were also confirmed correct. **Rev 04
changes only §3.5's launch and descriptor material, the SE-7
demonstration list, the two cross-references the new
demonstration forces, and this summary and the header.**
Itemised:

**Amendment 1 — Declared and verified destinations for the
retained descriptors (§3.5 point 3 allowlist wording; the
descriptor-separation block; SE-7 demonstration (vi)
extended).** Rev 03 retained fds `0`/`1`/`2` as "the logging
channel" without establishing what they point at — and a
standard descriptor redirected to a writable file inside
`commitments/` would survive the close of everything from
fd `3` up and remain a live route in. Rev 04 **declares** the
permitted destinations: fd `0` is `/dev/null` or a read-only
pipe; fds `1`/`2` are pipes drained by the supervisor into the
run log, or a single designated append-only log file in the
supervisor-owned run-log area — outside `commitments/` and
outside the issuance store. No retained descriptor may be a
file inside `commitments/`, a commitment receipt, or
`issuance-record.jsonl`, nor a writable handle to any of them.
Verification is a **normative supervisor duty**: before
invoking the launcher, the supervisor resolves each retained
descriptor's destination (`/proc/self/fd/`) and access mode
(`fcntl(F_GETFL)`) and asserts both match the declaration; on
any mismatch the launch does not happen, and the abort is
recorded. Demonstration (vi) now also verifies the retained
descriptors' destinations and modes from inside the child,
including the **negative arrangement** — stdout deliberately
pointed at a scratch protected file pre-launch, which the
verification must catch and refuse, with no launch occurring.

**Amendment 2 — The launch handshake: parent-confirmed
execution (§3.5 point 3 rewritten; §3.5 point 4(v) aligned;
SE-7 demonstration (viii), new).** Rev 03's sequence let the
child drop, close, and exec on its own success alone — so if
the parent then failed its own privilege drop and terminated,
an already-executing harness could be left orphaned, with no
supervisor able to observe it or issue over it. Rev 04 orders
the launch through a **private gate pipe** created before the
fork: the child drops, verifies, closes descriptors, and then
**blocks reading one byte**; the parent drops and verifies,
and **only then** writes the single release byte; only on
receiving it does the child exec. On any parent failure the
release byte is never written — the parent kills the waiting
child (`SIGKILL`), reaps it, and only then terminates, with
no issuance of any kind. If the parent dies before releasing,
the child sees end-of-file on the gate and `_exit()`s without
executing. The invariant, in Alex's terms: **the supervisor's
independent observation and issuance capability is fully
established before the subject begins work; there is no
interleaving in which the harness executes while the
supervisor side has failed.** The gate read end is reconciled
with the descriptor declarations in the descriptor-separation
block: read-only, not a writable handle to any protected
artefact, `O_CLOEXEC` so the exec itself closes it — it does
not exist in the harness. New demonstration **(viii)** proves
the fail-closed outcome by fault injection (a test-only hook,
compiled out of the production launcher): an induced parent
failure leaves no executing harness, no run artefacts, and no
START commitment or issuance entry; and the parent-death
variant leaves the child exited at the gate, unexecuted.

**Cross-reference alignments (the only changes outside §3.5
and the SE-7 list):** §4 Batch 4's checkpoint and §5 gate G3
now cite the launcher demonstrations as **(v)–(viii)** — the
same alignment Rev 03 made for (vi) and (vii), so the gate
evidence cannot omit the handshake test.

**Not changed.** Everything Alex accepted in pb-mwee6msu
carries over untouched: the Rev 03 amendments in their
substance (subject only to the two amendments above),
corrections B (RFC 8785, §3.4) and C (the S7 pin and the §2
sweep), the synthetic-capture specification (§3.7), gates
G1–G5 apart from G3's citation, the no-model-call rule, the
batch order, and §6 entire. Rev 03's Amendment Summary follows
below, unaltered, as the record of the previous round.

---

## AMENDMENT SUMMARY — REV 03 (answering Alex's re-inspection, pb-mwee0se4)

Alex's re-inspection of Rev 02 returned **NOT CLEARED — one
remaining blocking security defect**, with corrections B
(RFC 8785 canonicalisation) and C (the corrected S7 pin)
**accepted**, and the synthetic-capture condition **accepted**.
The one blocker is in §3.5's launcher design: the custody
boundary as specified was **path-based only**. A file
descriptor already open at `fork()` survives into the child
across `exec()`, and filesystem permissions do not revoke
access through it — a harness child inheriting a writable
descriptor to `commitments/` could write through it whatever
the directory's mode says. **Rev 03 changes only the launcher
material of §3.5, the SE-7 demonstration list, and this
summary and the header.** Itemised:

**Amendment 1 — Descriptor separation (§3.5 point 3; new
descriptor-separation block after point 4; SE-7 demonstration
(vi), new).** In the child, after the privilege drop and
before the exec, the launcher now closes **every** inherited
file descriptor except an explicitly declared minimal
allowlist — fds `0`, `1`, `2` only, retained solely in their
standard roles as inherited from the supervisor's invocation
context (the logging channel) — by an exhaustive close
(`close_range(3, ~0U)` or an equivalent `/proc/self/fd`
enumeration). Any descriptor the harness opens after the exec
is its own, under its own identity's permissions. On the
supervisor side, a stated design invariant: the supervisor
holds **no** open writable descriptor to `commitments/` or to
`issuance-record.jsonl` at the moment it invokes the launcher
— commitment-store files are opened per write, written, and
closed, never held open across a launch. New SE-7
demonstration **(vi)** arranges the hazard deliberately: a
launching process holding an open writable descriptor to a
scratch commitments-like file, after which the
harness-identity child attempts to write through every
inherited descriptor number; the test passes only if no
inherited descriptor is usable for writing (the allowlist
excepted, in its declared roles) and the scratch file is
byte-unchanged.

**Amendment 2 — Privilege-transition precision, fail-closed
(§3.5 point 3).** Both transitions — child to
`pilot-harness`, parent to `pilot-supervisor` — are now
specified as `setresgid()` then `setresuid()`, each setting
all three ids (real, effective, saved), each followed by a
`getresgid()`/`getresuid()` verification read-back. On any
failure or mismatch the process **terminates immediately**: the
child never continues into the exec, and the parent never
continues into waiting or issuance, on a failed or partial
transition.

**Amendment 3 — Group separation (§3.5 point 1; SE-7
demonstration (vii), new).** Stated as a build precondition:
`pilot-harness` is not a member of the `pilot-supervisor`
group, and `pilot-supervisor` is not a member of any group
conferring `pilot-harness` privilege — because the launcher's
mode `4710` group-execute is the control limiting who may
invoke it, and that control proves nothing if the memberships
do not separate. Demonstration (vii) reads the membership from
the operating system into the gate evidence and **fails** the
custody evidence if the separation does not hold.

**Amendment 4 — Setuid-environment verification (§3.5
point 2; SE-7 demonstration (vii)).** The supported operating
system is named (Linux), and the design's reliance on setuid
elevation is made a verified precondition, not a presumption:
a probe invocation must observe effective uid `0` in the
privileged window on the build host, and the conditions that
silently defeat setuid — a `nosuid` mount on the launcher's
filesystem, an inherited `no_new_privs` flag — are checked and
recorded. **A failed privilege assumption stops the build; it
never triggers a fallback to a weaker launch arrangement.**

**Amendment 5 — Wording correction (§3.5 point 4(ii), with
(iv) aligned).** A setuid-root process **has** root's
filesystem authority while privileged. Rev 02's phrasing
("holds no open path to `commitments/`", framing the point as
why the launcher *cannot* modify commitments) claimed more
than that. It is replaced with the defensible claim: the
launcher's pinned implementation contains **no
commitment-writing operation and no path to the
`commitments/` store**, it performs no file writes while
privileged, and it drops privilege before the supervisor
performs any commitment work; the launcher remains named in
the trusted computing base with that authority acknowledged,
and the standing limit — no protection against the machine's
operator or root — is unchanged.

**Cross-reference alignments (the only changes outside §3.5
and the SE-7 list):** §4 Batch 4's checkpoint and §5 gate G3
now cite the launcher demonstrations as **(v)–(vii)**, so the
gate evidence cannot omit the new tests.

**Not changed.** Correction B (RFC 8785, §3.4) and correction
C (the S7 pin and the §2 sweep), both accepted; the
synthetic-capture specification (§3.7), accepted; gates
G1–G5, the no-model-call rule, the batch order, and §6's open
items and flagged decisions carry over from Rev 02 unchanged.
Rev 02's Amendment Summary follows below, unaltered, as the
record of the previous round.

---

## AMENDMENT SUMMARY — REV 02 (answering Alex's inspection, pb-mwedjeu4)

Alex's independent inspection of Rev 01 returned **NOT CLEARED —
amendments required**: three blocking findings (A: the
supervisor launch mechanism missing; B: canonical serialisation
under-specified; C: a malformed pin) and one condition on an
accepted proposal (the stub subject must satisfy the capture
contract). **Rev 02 changes exactly those four things.** Every
other section carries over from Rev 01 unchanged; where a
correction forces a wording alignment in a neighbouring section,
that alignment is listed here, not made silently.

**Amendment 1 — Correction A: the supervisor launch mechanism
(§3.5).** Rev 01's custody model named two OS identities but no
mechanism by which the supervisor could spawn the harness under
the other identity — an ordinary unprivileged process cannot do
that. §3.5 now specifies a narrowly constrained **privileged
launcher**: a minimal root-owned setuid-root binary, executable
only by the `pilot-supervisor` group, with a compiled-in
allowlist (fixed harness path and argument shape; no arbitrary
input), which forks, drops the child to `pilot-harness` for the
exec, drops itself irrevocably to `pilot-supervisor`, and
`waitpid()`s — so termination, including crashes, is witnessed
by the operating system, and every commitment is computed and
written only by code running as `pilot-supervisor` after the
drop. §3.5 answers Alex's five required points explicitly, and
the SE-7 demonstrations gain the launcher separation tests (new
item (v)). Consequential alignments: §2.4 lists the launcher
binary among the produced artefacts; §4 Batch 4's checkpoint
and §5 gate G3 reference demonstration (v). The custody model,
the issuance semantics, and the threat model — no protection
claimed against the machine's operator or root — are unchanged.

**Amendment 2 — Correction B: canonical serialisation (§3.4).**
Rev 01's description (UTF-8, sorted keys, no insignificant
whitespace) did not fully define canonical bytes. §3.4 now pins
**RFC 8785 (JSON Canonicalization Scheme)** as the canonical
form for every structured artefact the harness serialises and
hashes, with the implementable contract (number serialisation,
string escaping, and key ordering per the RFC) and rejection
rules for values that cannot be safely represented (NaN,
infinities, duplicate keys at parse, lone surrogates —
rejected, never coerced). Hashes over raw byte artefacts —
captured HTTP bodies, the record file's exact bytes, corpus and
snapshot files — remain sha256 over the bytes exactly as they
lie; canonicalisation never applies to them. The contract is
frozen at Batch 0 before any hash is generated; changing it
afterwards is a re-freeze amendment. Consequential alignments:
§3.1's serialisation reference, §4 Batch 0's re-freeze
contents, §5 gate G5 (the canonicalisation standard identifier
is now one of the mechanically checked configuration values),
and §6.3 item 3.

**Amendment 3 — Correction C: the malformed pin, and a full
pin sweep (§2).** The S7 hash printed in Rev 01 had 54
hexadecimal characters. It is corrected to the sha256 computed
from the actual bytes of `V2-QUALIFICATION-01.md`:
`6ae47780785001b6ffc68b73bc2b0a3e11cc9b0a8def493d958b86d60e2f623a`
(the Rev 01 text had dropped a ten-character segment). The
sweep the finding prompted covered **every file-hash pin in
§2 — 18 pins** (§2.2: S1, S3, S4, S5, S6, S7, S10; §2.3: rows
2–12). **Result:** every pin is now exactly 64 hexadecimal
characters; S3, S4, S5, S6, S10 and all eleven §2.3 pins verify
byte-for-byte against the local files; S7 is corrected as
above. One further finding is recorded here and **not
altered**: S1's pin verifies exactly against its cited source
(PILOT-MANIFEST-01 row 1 — the plan in its adopted state, 7,497
B), but the living local copy of the plan file has been amended
since the Stage 0 freeze (now 8,205 B; sha256 `743e7dd4…`).
S1's referent is the frozen adopted-state bytes, so this
amendment does not re-pin S1 to the living file — whether the
programme re-freezes the plan is a decision for Ben/Alex, and
the divergence is stated here so it is never discovered later
by accident.

**Amendment 4 — Alex's condition on proposal 2: synthetic
captures (§3.7).** The stub-subject specification now requires
the stub full-battery run to produce examiner-verifiable,
**explicitly labelled synthetic capture artefacts** satisfying
Criteria §1.1(6) — a linked `ADAPTER-CAPTURE-02` record for
every [MODEL] step, with capture hashes and attempt-level
response bodies preserved and recomputing — instead of scripted
text that bypasses the evidence contract. The doubles' boundary
is restated: the transport double exercises the real adapter's
HTTP handling (retries, error-body capture, redaction); the
stub subject exercises the harness's step and capture machinery;
neither substitutes for the other. Consequential alignment:
§6.3 item 2 records the condition.

**Not changed.** Gates G1–G5 (beyond the G3/G5 alignments
listed above), the no-model-call rule, the batch order, the
open items of §6.1 (still no defaults taken), the mechanism
section (§1), and the accepted proposals — Python (§6.3 item 4)
and the read-only catalogue GET with its response preserved and
hashed and credentials never captured (§6.3 item 5) — carry over
unchanged.

---

## 0. REV 14 GOVERNING AMENDMENTS — WHOLE-SYSTEM BOUNDARY, LANE REGISTER, AND PROVIDER-CONTACT POLICY

**Status for this section.** Sections 0.1–0.9 carry Alex's crosswalk
sections A–G entire: the whole-system boundary and lane register (A),
the provider-contact policy (B), the D-4 breach record (C), the
High-finding corrections and qualifications (D), the disposition
register (E), the acceptance-evidence pairings (F), and the authority
and sequencing restatement (G). They are governing amendments for
Rev 14: where an earlier Rev 13 clause distributed an assumption
about what counts as inside the system, or about when contact with a
model provider is permitted, these sections replace that assumption.
The full-document consistency pass required by the crosswalk is
complete (§0.7, D-26). This draft is complete and is offered for
independent inspection at its Shelf pin; inspection, not this text,
decides whether it is fit to build from.

### 0.1 The whole-system boundary

The pilot system is not only the harness, supervisor, adapter, and
subject. For accountability, the system boundary includes **every
component, process, lane, connector, bridge, retrieval mechanism,
tool, model interface, helper, launcher, and supporting service that
participates in the pilot's operation or in the production of evidence
about the pilot**. A lane does not leave the boundary because it is a
separate process, uses a different model, runs on a different machine,
is operated through a browser or bridge, is described as test or
infrastructure work, or is used only to gather evidence.

Boundary membership establishes **accountability only**. It does not
grant permission to act. Permission is established separately, lane by
lane, by §0.3. No lane may infer permission from any of the following:
that the lane exists; that it is inside the boundary; that a credential
or connector is available; that another lane has standing approval;
that the contact is small, read-only, a listing, a probe, a test, a
retry, or an evidence-retrieval operation; or that the contact is
intended to prove that contact did or did not occur.

Every lane that participates in the pilot or its evidence must be
entered in the lane register at §0.2 before it is relied on. An
unregistered lane is treated as unauthorised for pilot work until the
register is amended through the same inspection path as this
specification. The register is reconciled against the actually
deployed components and process paths as acceptance evidence (crosswalk
F); a deployed component missing from the register is a defect, and a
register entry with no deployed component is a defect of the register.

### 0.2 Lane register

For each lane, the register declares: identifier and purpose; the
components and processes it can invoke; whether it can communicate
externally; whether it can contact a model provider or another
external service; permitted destinations and protocols; who may
authorise its operation; whether authorisation is standing, scoped, or
per-operation; applicable stage and batch restrictions; what evidence
it produces and where that evidence is recorded; how its activity is
independently verified; and its failure, timeout, retry, and refusal
behaviour. The entries below are the minimum register required by the
crosswalk; additional lanes may be added only by amendment through
inspection.

**LANE-BRIDGE — Pulse Bridge (seat correspondence).**
Purpose: transport of letters between Remmy and the Alex seat, and any
other seat Ben expressly places on the bridge. Components/processes it
can invoke: the bridge extension in Ben's browser, the seat tabs it is
connected to, and Remmy's chat surface. External communication: yes —
it carries text to and from model-interface seats. Provider contact:
it is transport to a model interface; it does not itself call a model
provider API, and it must not be used to route a request to a provider
lane that the provider-contact policy does not permit. Permitted
destinations/protocols: the bridge's own seat channels only, as
installed and watched by Ben. Authoriser: Ben for any new seat,
occupant switch, or bridge build; Remmy for ordinary letters inside an
already-authorised programme thread. Authorisation type: scoped to the
programme thread. Stage/batch restrictions: correspondence only; it
authorises no build step, no provider retrieval, and no Stage 6
contact. Evidence produced: PB-ID and dated slug on each letter, the
letter text in the conversation record, and the shelf copies where a
letter is shelved. Independent verification: Ben watches the bridge
live; letter provenance is checked against PB-ID, slug, and shelf pin
where one exists. Failure behaviour: a failed, duplicated, or stacked
delivery is reported as a transport defect; silence is never treated
as delivery, and an unacknowledged assignment is re-triggered rather
than assumed received.

**LANE-CRUSHER — Crusher retrieval lane.**
Purpose: grounded retrieval from Crusher's canonical index, answering
with provenance or UNKNOWN, for seats or processes that cannot pull
the Shelf themselves. Components/processes it can invoke: the local
Crusher harness (`crusher.py`), its canonical index, the Groq
connector, and the Qwen model occupant named in the harness record.
External communication: yes. Provider contact: **yes — invoking
Crusher is provider contact**, because the harness calls its model
provider to answer. Permitted destinations/protocols: only the
provider endpoint and model recorded in the harness configuration, for
retrieval questions within the declared corpus. Authoriser: **Ben
only**, for any invocation not already covered by an express standing
authorisation recorded in this specification or in Ben's own recorded
ruling. Alex, Claude, Remmy, the harness, and the existence of an
evidence need cannot authorise an invocation. Authorisation type:
per-operation by default; any standing or scoped authorisation must
name the stage, purpose, corpus, and expiry or completion condition.
Stage/batch restrictions: **not authorised as part of the Stage 5
build or its gates**; Stage 5 evidence must be produced from local and
Shelf sources. A Stage 5 invocation requires Ben's explicit
authorisation for that operation, recorded before the invocation, and
the invocation is then recorded as authorised provider contact — never
relabelled as a test, probe, or infrastructure operation. Evidence
produced: the harness log entry for every call (call identifier,
timestamp, requester, question scope, status, and provider response
class), the unedited answer or recorded non-answer, and the preserved
return artefact where one is made. Independent verification: the log
is append-only from the invoker's side; answers are delivered
unedited; provenance is verified against the log and any shelved
extract by hash. Failure behaviour: a provider refusal, rate limit,
timeout, or malformed answer is recorded as a failure or non-answer,
never as UNKNOWN and never as evidence; there is **no automatic retry
after a rate-limit response**; a later attempt is a new invocation,
separately authorised and separately logged, linked to the failed
attempt it follows.

**LANE-SHELF — Shelf retrieval and source access.**
Purpose: read access to the pinned Shelf record (the ainternet-shelf
repository) and to local source files, for drafting, verification, and
inspection. Components/processes it can invoke: the GitHub connector
(read path), the local shelf clone, local file reads, and hash tools.
External communication: yes, for repository reads and writes.
Provider contact: no model provider contact. Permitted
destinations/protocols: the Q420/ainternet-shelf repository and the
local workspace only. Authoriser: Remmy for reads inside an authorised
task; Ben for publication to the Shelf (shelf publication
authorisation remains Ben's). Authorisation type: reads are standing
inside an authorised programme task; writes/publications are scoped
per operation. Stage/batch restrictions: shelf reads may support any
stage's evidence; shelf writes follow the publication gate for the
task in hand and do not authorise build or execution steps. Evidence
produced: commit identifiers, file hashes, read-back verification
results, and the local staging record. Independent verification: any
party with repository access can re-read the pinned file and recompute
its hash; index files are system-written only and are never edited by
a lane. Failure behaviour: a failed read-back or hash mismatch stops
reliance on that artefact until reconciled; absence of a file is
reported as not found in the searched location, never as proof that
the artefact does not exist.

**LANE-HARNESS — Harness and supervisor (pilot runtime core).**
Purpose: the Duenna frame for the pilot — issuing work to the subject
only through the adapter, checking calls and evidence, writing the
canonical record, and holding custody of commitments. Components/
processes it can invoke: the driver, the five pilot tools, the
canonical record writer, the supervisor, the setuid launcher, and the
stub subject / transport double during Stage 5 verification. External
communication: **no non-loopback egress in Stage 5**; loopback only,
per Item 1 as tightened in Rev 13 and carried into this revision.
Provider contact: none in Stage 5; the lane reaches the subject only
through LANE-ADAPTER and only at Stage 6 under Ben's authorisation.
Permitted destinations/protocols: loopback interfaces and the local
custody trees. Authoriser: Ben's build go names the builder and scope
for any build of this lane; no build go is given by this draft.
Authorisation type: scoped per batch. Stage/batch restrictions: built
and verified batch by batch against the stub subject only; Batch 2
(the five tools) and later batches remain closed until a valid
re-issued go against the inspected Rev 14. Evidence produced: the
canonical execution record, gate evidence, checkpoint reports, and
hash-pinned artefacts per batch. Independent verification: the gates
in §5, exercised by inspectors against the offered artefacts, not by
builder report alone. Failure behaviour: fail closed — a custody,
issuance, or record-integrity failure halts the batch and is recorded;
the supervisor's death, a torn write, or a missing terminal event is a
recorded defect, never a silent continuation.

**LANE-ADAPTER — Adapter and connector paths to the subject provider.**
Purpose: the single mediated path between the harness and the subject
model (NVIDIA Nemotron), capturing the raw request and response under
the Stage 2 adapter design. Components/processes it can invoke: the
adapter, its configuration, the NVIDIA connector/helper path where the
design uses it, and the loopback transport double in Stage 5 mode.
External communication: Stage 5 — loopback only; Stage 6 — only the
authorised subject endpoint. Provider contact: Stage 5 — **none**;
Stage 6 — yes, only under Ben's Stage 6 authorisation and the
pre-flight record. Permitted destinations/protocols: the pinned
provider base URL and model identifier from the frozen adapter
configuration; resolved peer addresses and redirects are part of the
contact record, not merely the configured URL. Authoriser: Ben only
for first contact and for any change of endpoint, model, or
configuration. Authorisation type: per-stage; Stage 6 authorisation
does not retroactively authorise Stage 5 contact, and design-time
catalogue evidence does not authorise live contact. Stage/batch
restrictions: in Stage 5 the adapter is built and tested against the
transport double with proxy configuration present-and-refused tests;
no live listing, probe, or completion is permitted. Evidence produced:
the capture record (raw request/response hashed; headers never
captured), the adapter configuration hash, pre-flight records, and
refusal-test evidence. Independent verification: inspectors recompute
configuration and capture hashes and re-run the refusal tests against
the offered artefact. Failure behaviour: any unexpected egress,
honoured proxy, redirect to an unpinned destination, or capture-write
failure is a build-acceptance failure, recorded with the artefact
identified; the adapter does not fall back to a direct or alternate
route.

**LANE-SUBJECT — Subject provider lane (Nemotron as governed subject).**
Purpose: the governed model execution that Stage 6 exists to run —
the battery administered to the pinned subject inside the frame.
Components/processes it can invoke: none; the subject is invoked only
through LANE-ADAPTER and has no tool access in this pilot.
External communication: responses only, through the adapter.
Provider contact: constitutes the Stage 6 contact itself.
Permitted destinations/protocols: not applicable outbound; inbound
responses are captured by the adapter. Authoriser: Ben, by the Stage 6
authorisation, whose current status is governed by §0.3 and the D-3
qualification recorded later in this revision: as the record stands,
no Stage 6 model call is authorised by the Rev 14 commission, by the
earlier Stage 6 authorisation's chronology, or by this draft; Ben
retains the Stage 6 decision at pre-flight. Authorisation type:
per-battery, scoped by the pre-flight record. Stage/batch
restrictions: no subject contact in any Stage 5 batch. Evidence
produced: adapter capture records, the canonical execution record,
examiner records, and the battery report. Independent verification:
the examiner lane and the anchor-first replay and calibration gates
in §5. Failure behaviour: an interrupted, refused, or unrecorded
subject call is a battery defect to be dispositioned at pre-flight
rules, never quietly re-run as if it were the first attempt.

**LANE-INSPECT — Independent inspection lanes (Alex and Claude).**
Purpose: independent adjudication and inspection of specifications,
evidence packs, and the built package. Components/processes they can
invoke: their own model interfaces, their own repository read access
where Ben has granted it, and — for Claude — the review branch Ben's
repository permissions allow; neither inspector invokes pilot
components, the Crusher lane, or the adapter. External communication:
yes, as model-interface correspondence, normally through LANE-BRIDGE
or by Ben's ferry. Provider contact: their correspondence is programme
communication, not pilot runtime contact; it is not a route for
obtaining operational or retrieval evidence from any provider lane,
and an inspector's request does not authorise contact by any other
lane. Permitted destinations/protocols: the seat interfaces and the
Shelf read paths Ben has granted. Authoriser: Ben commissions each
inspection; Alex's adjudication role inside the Duenna/Alex programme
loop stands as Ben recorded it, with spend, outreach, publishes, and
accounts remaining Ben's. Authorisation type: scoped per inspection.
Stage/batch restrictions: inspectors judge pinned artefacts; an
inspection never opens a batch, and incorporation of findings is not
itself an inspection of the amended text. Evidence produced:
inspection letters and reports with PB-ID/slug or file hash, verdicts,
and finding registers. Independent verification: each inspector works
from the same pin independently; verdicts are recorded with their
evidence class (verified / partly verified / not verified) preserved.
Failure behaviour: an inspector who cannot retrieve the pinned
artefact reports the retrieval failure; no verdict is issued against
an uninspected text.

**LANE-RESEARCH — Research and evidence retrieval (non-Crusher).**
Purpose: retrieval of public or already-held evidence that is not in
the Shelf or local record — for example provider documentation needed
to draft or check a specification. Components/processes it can invoke:
Remmy's web search and page reads, and public documentation.
External communication: yes. Provider contact: reading public
documentation pages is not model-provider contact; calling a provider
API, listing endpoint, or model is, and is governed by the lane that
owns that endpoint, not by this lane. Permitted destinations/
protocols: public web sources and local files. Authoriser: Remmy
inside an authorised research task; Ben where the research would
create accounts, spend, or contact a provider API. Authorisation type:
scoped per task. Stage/batch restrictions: research may inform a
draft; it produces no gate evidence unless the source is preserved
with a hash or a dated capture. Evidence produced: cited sources with
retrieval dates; claims labelled by evidence class. Independent
verification: sources are re-readable at their cited addresses, or
preserved as captures where they are not. Failure behaviour: an
unreachable or unverifiable source is reported as such; its content
is not reconstructed from summaries.

**LANE-EXEC — Launchers, helpers, and supporting execution processes.**
Purpose: the small processes that make the other lanes run — the
setuid launcher, the SSH door and Ubuntu room on Ben's laptop, the
watch window, build scripts, hash and test helpers, and the doorbell
notification helper. Components/processes they can invoke: only the
specific helper each entry names, inside the environment that hosts
it. External communication: only as the hosted lane permits (for
example the SSH door carries Remmy's session to Ben's laptop over the
tailnet; the watch window is display only). Provider contact: none of
these helpers contacts a model provider; a helper that would do so is
a different lane and must be registered as one. Permitted
destinations/protocols: the laptop room and workspace volumes, the
local VM workspace, and the doorbell endpoint for notifications Ben
has authorised. Authoriser: Ben for access to his machines and for
notification classes; Remmy for ordinary build/test helpers inside an
authorised task. Authorisation type: scoped per environment and task.
Stage/batch restrictions: helpers inherit the restrictions of the work
they serve; a helper never widens a lane's permission. Evidence
produced: command outputs preserved in checkpoint reports, file
hashes, service states, and log files named in the relevant checkpoint
record. Independent verification: the environment acceptance probe and
checkpoint re-runs are executed against the live environment, not
against a description of it. Failure behaviour: a helper failure is
recorded with its actual output; a quiet helper is never reported as
a finished helper.

**LANE-OWNER — Owner authority channel (Ben).**
Purpose: the channel through which project authority is exercised —
taps, recorded rulings, ferries of inspection packages, and decisions
reserved to Ben. This is not an execution lane: the system does not
invoke it, and no component may simulate, infer, or pre-empt its
output. External communication: as Ben chooses. Provider contact: not
applicable. Permitted destinations/protocols: not applicable.
Authoriser: Ben is the authority. Authorisation type: each exercise
is its own record. Stage/batch restrictions: approvals are scoped to
the operation named in the approval; an approval of one stage, batch,
or lane is not an approval of another, and a summary record of an
approval is labelled as a summary (Ben's ruling: the gate record can
be intent, not vernacular). Evidence produced: the approval record in
the conversation, the scope ledger, and the gate ledger where one
applies. Independent verification: approvals are cited by date, form,
and location in the record; an approval whose identity, scope, or
status cannot be verified is void until re-established. Failure
behaviour: ambiguity in an authority record is resolved by asking
Ben, never by broadening the approval.

### 0.3 Provider-contact policy (single authoritative statement)

This policy is the one authoritative statement of provider-contact
permission for the whole system. Any other clause in this
specification, any letter, and any standing practice is read subject
to it; where a conflict appears, the conflict is a defect to be
corrected through inspection, not resolved silently in favour of
permission.

1. **Default.** Provider contact is **denied by default** for every
   lane, at every stage, unless this policy — or a later inspected
   amendment to it — expressly permits the contact for that lane,
   stage, purpose, and authoriser.
2. **What counts.** Provider contact includes a chat completion, a
   model listing, a catalogue fetch, a probe, a health check that
   reaches the provider, a retrieval invocation whose harness calls a
   provider (LANE-CRUSHER), and the Stage 6 subject battery
   (LANE-SUBJECT via LANE-ADAPTER). The size, cost, read-only nature,
   or evidentiary purpose of a contact does not change its class.
3. **Stage 5.** During the Stage 5 build and its gates, **no lane
   makes provider contact for the pilot's operation or evidence**,
   except under a per-operation authorisation by Ben recorded before
   the contact, naming the lane, provider, endpoint, purpose, and the
   evidence the contact is expected to produce. Stage 5 verification
   uses the scripted stub subject and the loopback transport double.
   The design-time catalogue snapshot carried in the freeze is
   historical evidence; it is not contact and does not authorise
   contact.
4. **Stage 6.** Subject contact occurs only at Stage 6 pre-flight and
   execution, under Ben's Stage 6 decision as recorded at that time,
   with the fresh full catalogue capture and pinned-identifier check
   the pre-flight requires.
5. **Inspection correspondence.** Correspondence with Alex and Claude
   through LANE-BRIDGE or Ben's ferry is programme communication. It
   does not authorise, and must not be used to obtain, provider
   contact by any other lane. A request from an inspector for evidence
   is satisfied from existing local and Shelf sources; if it cannot
   be, the gap is reported and any invocation is decided by Ben.
6. **Event record.** Every provider contact, and every attempted
   contact, produces a contact event record at the time it occurs,
   carrying: lane identifier; authoriser and the authorisation record
   relied on; stage and batch; provider and endpoint; purpose and
   classification (live, test, probe, retrieval, or battery);
   timestamp; outcome — **authorised / unauthorised /
   attempted-but-unsuccessful / provenance-unestablishable** — and,
   for completed contacts, the response class and the artefact the
   contact produced, with its hash where an artefact exists. Retries
   are separate events linked to the attempt they follow.
7. **No inference from silence.** A missing contact record is not
   proof that no contact occurred. Where provenance cannot be
   established, the contact is recorded as
   provenance-unestablishable and the gap is reported to Ben; records
   are never back-filled from summaries or reconstructed from memory.
8. **Breaches.** Contact outside this policy is a breach: it is
   recorded as a breach with its facts preserved (as the D-4 record
   later in this revision does), it is not reclassified as an
   exception or waiver after the fact, and the policy correction that
   follows it does not rewrite the event as compliant.

### 0.4 D-4 breach record (crosswalk C)

This subsection is the breach record required by finding D-4. Its
source is the D-4 evidence pack, preserved unchanged:
`duenna/D4-BREACH-EVIDENCE-PACK-2026-11-13.md`, shelf commit 34243892,
file sha256
a4874c61362547988a66110df1bf90347372e6a32d3c752cd1c4d35d0205b9b9.
Alex has acknowledged the pack as **reported** (pb-mwfjby6l-h-ek0l);
his independent inspection of it remains part of his Rev 14
inspection. Nothing in this record is reconstructed: where the pack
records UNKNOWN, this record records UNKNOWN.

**The rule broken.** Rev 13 §6.3 item 5, at pin bab720b2: Stage 5
makes no contact with the provider host under any circumstances — no
chat completion, no listing, no probe; the first contact of any kind
is Stage 6's.

**The lane.** LANE-CRUSHER: local harness `crusher.py` v2.2, a
stateless retrieval worker running qwen/qwen3.8-27b via the Groq
connector. Every invocation is a provider request. Under Ben's
boundary ruling of 2026-11-13, the lane is inside the pilot system
boundary (§0.1).

**The contact.** Twelve log entries representing nine distinct harness invocations in the Stage 5 window,
2026-11-13 20:17:57Z–20:21:51Z (13:17–13:21 MST), recorded in
`crusher-log.jsonl` (full log 159 entries, sha256 8e44d502…) and
shelved verbatim as an extract at commit 4c6e0b31 (file sha256
017a413a…). One lane check (requester ben, answered); six retrieval
questions decomposed from Alex's required F-B1-2 scope (requester
alex): Q1, Q2, Q4, and Q5 answered UNKNOWN; Q3's first attempt FAILED
with HTTP 429 and a separate later invocation answered UNKNOWN; Q6
was attempted twice, both attempts FAILED with HTTP 429 (Groq
on-demand output-token-per-minute cap), and Q6 stands as a recorded
**non-answer**, not an UNKNOWN. The unedited return is preserved at
commit 105e4d50 (file sha256 c78f718b…). Provider-side request
identifiers beyond the harness call identifiers are **UNKNOWN**; none
were retrieved, and retrieving them would itself be provider contact.

**Authorisation context.** The Crusher stop order had been lifted by
Ben on 2026-11-13 (~06:40 MST), conditioned on verifiability; the
original retrieval dispatch was authorised by Ben at ~06:40 MST;
Alex's final Batch 1 adjudication required Crusher's independent
Shelf-side evidence for the freeze; and the harness was in fact
invoked only after Ben's ~13:16 MST question exposed that the marker
letters had been posted without the harness ever being run.

**Disposition.** Ben ruled (2026-11-13 14:06–14:08 MST): **this was a
breach** — provider contact inside the system's boundary during Stage
5, contrary to §6.3 item 5 as written. All three facts stand together
and none cancels another: the contact happened; it broke the rule as
written; it was undertaken openly, under the owner's authorisations,
for evidence the process required. It is not an exception, not a
waiver, and not misconduct or concealment. It does **not** disturb
the Batch 1 freeze (disposition at commit 260796c8). The technical
correction — the lane register and the single provider-contact policy
at §§0.2–0.3 — prevents recurrence by defining the lane inside the
boundary with Ben-only authorisation; it does not rewrite this event
as compliant. The design defect the breach teaches is also recorded:
Rev 13's zero-contact rule was written without accounting for the
evidence lane the same process demanded.

### 0.5 Corrections to the adjudicated High findings (crosswalk D)

The clauses below state the operative Rev 14 corrections for the
twelve High findings Alex held to stand outright. Their per-finding
dispositions are entered in the disposition register (sitting 3) and
their acceptance-evidence pairings in the acceptance section
(sitting 4); a clause here is the correction of the specification
text, and no clause claims its own test has already been run.

**A-1 — Refusal objects expose no value.** Where a tool contract
states that a refusal returns no value, the refusal artefact contains
exactly these fields and no others: artefact kind, tool identifier,
reason code (from the contract's enumerated set), the input reference
as a hash only, and the record identifier. It must not contain a
candidate value, a recomputed value, an expected or actual value, or
evidence text that carries any of them. Any earlier wording that a
refusal both returns a structured object and returns "no value" is
replaced by this definition: the object is metadata only.

**A-2 — Raw and redacted error bodies are separate artefacts.** A
provider or transport error body is preserved as two artefacts: a
restricted raw artefact, held in local custody, never published, and
a redacted artefact, which is the only form quoted in reports or
offered for inspection. Both are hashed; the canonical record carries
both hashes and the capture identifier that links them. Access to the
raw artefact is limited to the builder and the examiner of record for
the run that produced it. If redaction cannot be performed safely,
the record carries the raw artefact's hash and length and marks the
body unavailable-for-inspection; it is never published unredacted to
make inspection easier.

**B1-2 — The child process environment is fixed completely.** A child
created through the launcher starts with: an environment consisting
exactly of the allowlisted variables named in the build's environment
table (no inherited credentials, no inherited proxy variables, and no
uncontrolled Python environment variables); the custody working
directory as its current directory; umask 0077; signal dispositions
reset to default except those the supervisor design expressly owns;
and an empty signal mask outside the launcher's handoff window. The
child's actual environment, working directory, and umask are read
back and recorded before the child's first record write; any mismatch
is a fail-closed defect.

**B1-8 — Supplementary groups are cleared before the group change.**
The child calls setgroups(0, NULL) **before** setresgid(), then
setresuid(). After the transition, getgroups() must return an empty
list and getresgid()/getresuid() must return the recorded custody
identities; the parent independently reads the child's group state
from the operating system. Any failure or non-empty group list is a
fail-closed defect and no exec follows.

**B2-1 — No-new-privileges is set and verified in the child.** Before
exec, the child sets PR_SET_NO_NEW_PRIVS and reads it back with
PR_GET_NO_NEW_PRIVS; exec proceeds only on a read-back of 1. The
build's acceptance evidence includes a setuid-reachability probe: an
attempt, from the child context, to execute a setuid-root helper must
produce no privilege gain. If the flag cannot be set or read back,
the child does not exec.

**B1-6 — Launcher/supervisor handoff and lifecycle are owned once.**
The supervisor spawns the launcher and passes exactly one launch
request over an inherited descriptor. The launcher performs the
privilege transition, creates the child, returns the child PID and a
status word to the supervisor, and exits; it owns nothing further.
The **supervisor** owns the child's lifecycle from that point: wait,
terminal-event closure, and issuance consequences. The harness never
waits on the launcher and never treats launcher exit as child
completion. Launcher death before the status word, and supervisor
death after it, are recorded defects with the outcomes the
disposition register states.

**C-2 — Sabotage insertion outcomes are stated per test.** The S3
first-insertion rule and the blanket insertion rule are reconciled
by a per-test expected-outcome table in the gate evidence: for each
sabotage test, the expected result of the first insertion attempt
(accepted, refused, or no-op) is stated in advance, and the blanket
idempotence rule governs only insertions after a terminal record
exists. A result that matches neither the per-test expectation nor
the blanket rule is a gate failure, not a pass under the other rule.

**C-3 — G1 tests the adapter's refusals, not only the environment.**
In addition to the environment isolation evidence, G1 includes
adapter-level refusal tests executed against the offered build:
loopback operation succeeds against the transport double; with proxy
environment variables set and pointing at a recording external
canary, the adapter refuses and the canary records no connection;
with a forwarding configuration present, the adapter refuses.
Environment snapshots in the evidence record variable names only,
never values that are credentials.

**C-4 — G2's torn-write test runs against the offered artefact.** The
torn-write test is executed by fault injection against the actual
production artefact offered for inspection, identified by its hash —
not against a scratch build, a test double, or a flag record. If the
artefact's hash changes for any reason, the test result does not
carry; it is re-run against the new artefact before G2 is claimed.

**C-7 — Batch 0 checkpoint evidence is complete or labelled open.**
The checkpoint record for the environment of record must carry: the
launcher interface freeze and its hash; the custody-tree setup
record; the setuid viability probe result; the measured identities;
and the corpus and serialisation verification results. Any element
the original Batch 0 record lacks is entered as NOT YET RUN or OPEN
in the disposition register — never implied passed — and is supplied
or dispositioned before the batch that depends on it.

**C-13 — G5 has a real UNANSWERABLE bound.** An examiner step is
ANSWERABLE only when it was executed against the offered artefacts
and produced a determinate finding. G5 fails if any mandatory step
is UNANSWERABLE, if the receipt-confirmation steps are UNANSWERABLE,
or if UNANSWERABLE non-mandatory steps exceed one in ten with each
instance carrying a named reason and an inspector disposition. A
result of 13/13 UNANSWERABLE is an automatic G5 failure. A gate
summary must report the ANSWERABLE and UNANSWERABLE counts beside
any pass claim.

**D-10 — Examiner receipt confirmation is an independent artefact.**
Receipt confirmation is produced by the examiner of record from the
canonical record and gate outputs, and is recorded as its own
artefact carrying the examiner's identity, the record hash it
confirms, and its timestamp. Builder-run gate steps — including any
G3/G4 step-0 output — are inputs to that confirmation and cannot
discharge it. The gate holder for receipt confirmation is the
examiner of record, never the builder.

### 0.6 Qualifications, baseline amendments, and further schedule corrections (crosswalk D qualifications + E schedule)

**D-1 — The earlier build go is not executable.** Ben's Stage 5 build
go of 2026-11-12 22:22 MST ("Alex approves it, I approve it") is
recorded as **not presently executable**: it was given against Rev 13,
which both inspectors have since held not fit to build from, and its
§7 precondition (both inspections standing) was not met at the time.
This revision does not revive it. Any future build go must reference
the inspected Rev 14 pin, name the builder, and state its scope;
Ben's authority to issue it is unchanged and entirely his.

**D-2 — Inspection chronology, recorded as it happened.** Claude's
only Rev 11 verdict ("not yet") was returned through Ben as chat text
on 2026-11-12; his findings were folded into Rev 12 and Rev 13; Alex's
Rev 12 re-inspection and Rev 13 clearance were therefore made with
Claude's findings visible and were not independent in §7's strict
sense. This chronology is not rewritten. Rev 14 cures the defect
prospectively: Alex and Claude each inspect the same Rev 14 pin
independently, their verdicts are recorded separately, and neither
verdict is an input to the other.

**D-3 — Stage 6 authorisation chronology.** Ben's Stage 6
authorisation (2026-11-12 ~19:13 MST) was given before the Stage 5
build existed and before its gates could pass. It stands on the
record as Ben's intent, with the sequencing defect stated; as it
stands it authorises **no model call**. Ben retains the Stage 6
decision and re-decides at pre-flight, after the Stage 5 freeze
event, on the pre-flight record (fresh catalogue capture, battery
composition, and the §9 Q3 repetition question).

**D-6 — Status vocabulary; no informal waivers.** Gate records
distinguish **NOT YET RUN** from **FAILED** everywhere; the two are
never merged. No informal agreement, summary, or conversation waives
a mandatory gate. For the avoidance of doubt: G1's status against the
environment of record is **NOT YET RUN** (it is Batch 6's obligation);
nothing in this revision or its source records claims G1 has passed.

**D-8 — Operative baseline amendments (formal).** The operative
baseline differs from Rev 13's text in the following particulars,
each carried with its evidence, and each subject to reinspection of
this amended baseline:
(a) **Environment of record** — Ben's laptop, Ubuntu 26.04.1 LTS
under WSL2, accepted by Alex (pb-mwep7new) on the acceptance-probe
evidence (bundle at shelf commit 844439bc). The Batch 0 re-run in
that room PASSED (bundle 894bde0b; Alex's clearance pb-mwepiog4) and
supersedes the VM's NOT PASSED checkpoint as the operative baseline;
the VM record (10bf5931) remains history and is not deleted.
(b) **Measured identities** — in the room, pilot-supervisor is
uid 999 / gid 986 and pilot-harness is uid 997 / gid 985 (the reverse
of the VM's assignment); build and gate work uses the measured
identities of the environment it runs in, never the assumed ones.
(c) **Adapter configuration** — the standing adapter_config_sha256 is
6cf57195d9ae27ca28d304dbb0dc8b8335e888e67a42bfba126629999a1f21eb
(F-2 incorporation, commit 82111456); the catalogue evidence is the
recovered design-time response (helper-serialisation sha256
bacf2ec8…; bare body 8a80b8e7…), labelled
RECOVERED-DESIGN-TIME-RESPONSE, and is not a live listing.
(d) **S1 re-pin (also Claude finding F1)** — S1 is pinned to **both**
states explicitly: the adopted state (7,497 B, sha256 2449c259…),
which remains the freeze's historical referent, and the amended
shelved state (8,205 B, sha256
743e7dd4fa0a7296c81ee8e317c234b39f7bb326bb79f441e1929b4e489aa949),
which is the operative governing-plan text and is on the Shelf at
`duenna/NEMOTRON-PILOT-PLAN-01-DRAFT.md`. The §2.2 S1 row is amended
in this revision to carry both pins. The discrepancy Claude found —
a pin describing the adopted bytes beside a description claiming the
index amendment — is thereby closed: the index amendment's text
exists only in the amended state, and each pin says which state it
covers.

**D-9 — The C launcher exception is pending, not self-approved.**
The setuid launcher's implementation in C is an exception to this
specification's Python implementation baseline. This specification
does not and cannot approve its own exception. The exception's status
is **PENDING explicit inspector disposition** at the Rev 14
inspections; if either inspector rejects it, Batch 4 does not proceed
on a C launcher, and the launcher design returns to the inspectors
before any build.

**Further schedule corrections (crosswalk E).** A-3: the stub subject
is a loopback HTTP endpoint **behind the adapter** — the adapter's
real request, capture, and hashing path runs against it; the
transport double is a separate loopback endpoint returning scripted
wire events; neither substitutes for the other, and synthetic
captures are produced through the adapter against the stub.
A-7: in Stage 5 mode the adapter checks the **resolved peer address**
on every connection and **disables redirects**; a resolution or
redirect to a non-loopback address fails closed before any outbound
attempt. A-8: a pre-flight failure is recorded in a named artefact —
the adapter preflight record, written to the batch checkpoint area
before RUN_STARTED, carrying the failure class, the check that
failed, and the configuration hash. A-9: a capture-write failure
raises the distinct error CAPTURE_WRITE_FAILED, returns no result to
the harness, and halts the run as an infrastructure failure; it is
part of the error taxonomy and of G2's test list. B1-1: the
supervisor's program, interpreter, and every module on its import
path are root-owned or supervisor-owned with no write for
pilot-harness at any path component; the supervisor runs with a
fixed sys.path and no working-directory entry; gate evidence includes
a negative test in which pilot-harness attempts to plant a module on
that path and fails at the OS boundary. B1-12: harness-owned run
records are protected against symlink, FIFO, and hard-link
substitution — records are opened with no-follow, exclusive-create
semantics and their inode identity is verified against the run's
record index before any append. B2-6: issuance occurs only after
RUN_STARTED is committed and read back. B2-7: every issuance reaches
exactly one terminal event; a gate run that finds an open issuance
fails that gate. B2-8: supervisor death is detected (child
reparenting or descriptor closure), halts the run, and is recorded
as SUPERVISOR_LOST; no process silently continues the run. B2-9: the
production launcher build contains no test hooks; absence is
established by artefact inspection of the offered binary, not by a
build flag claim. D-11: every gate record names its gate holder, the
evidence location, the evidence hash, and the independent party who
can re-derive the result; a gate record lacking any of the four is
incomplete. D-12: any future build go names the builder (see D-1).
D-13: the decision on an interrupted write — repeat, disposition, or
stop — belongs to the examiner of record at the gate, and the Stage 5
result is recorded as PASSED or BLOCKED with the reason stated.
D-16: the **Stage 5 freeze event** is defined as one named event: the
shelving of the completed build package and its gate evidence at a
single commit, with Alex's clearance of that commit recorded — no
earlier or partial state is a freeze. D-17: in all records under this
specification, VERBATIM is used only for byte-identical carries;
summaries are labelled SUMMARY, and paraphrases are labelled as such;
earlier headings that claimed verbatim for summarised content are
corrected wherever this revision touches them. D-19: the Crusher log
count is reconciled — the full log held **159 entries** at the D-4
pack's assembly; earlier figures in letters referred to extracts or
earlier states; Q6's status is a recorded non-answer (see §0.4).
D-20: the authoritative T09 fixture identifier is the canonical V2
id **`obligation-spec`**; artefacts ship under that label, and the
v1-era `obligation-spec-text` rendering is a rendering difference
only (F-B1-2, resolved). D-21: the S1–S5 sabotage battery and the
zero-egress evidence are **separate evidence sets** within G1; a
pass in one is never presented as evidence for the other. D-22: G1
evidence includes, from the actual environment, a credential-absence
scan of the build environment and an enumeration of connector paths,
each preserved as an inspectable artefact. D-25: `shelf_lookup` reads
the **pinned snapshot** taken at Batch 0, never the live Shelf,
during any gate, calibration, or scored run.

### 0.7 Disposition register — every finding, individually (crosswalk E)

Every finding from Claude's Rev 13 inspection set (branch
claude-reviewer-test at 15d8a00c: REVIEWER-A/B1/B2/C/D plus finding F1
from his findings log) and Alex's adjudication of it
(pb-mwfivrac-f-hb9z) is entered exactly once below: **FIXED** (the
Rev 14 text carries the correction), **CLOSED** (withdrawn or
resolved by ruling), or **OPEN** (carried into the Rev 14 inspections,
with its blocking effect stated). Provenance is preserved: Claude's
own verification classes stand as he recorded them — the High
findings he listed as verified, partly verified (B1-6, D-2, D-6), or
not verified (A-3, B1-1, D-5); the Medium and Low findings were **not
individually verified** by Claude and are legitimate review inputs,
not established facts. A FIXED entry means the specification text is
corrected; it never means a test has been run. D-18 (Claude's Rev 11
findings dispositioned individually) is OPEN: the Rev 11 finding
texts were returned as chat text and are not held as a retrievable
artefact, so individual disposition awaits that text; it blocks
inspection completeness, not drafting. D-26 (§6.3 status labels
reconciled with acceptance records) is FIXED: the sitting-4
consistency pass read §6.3 against the acceptance record, and the
§6.3 head note added by this revision binds every status label in
that section to the register and the gate records.

| Finding | Severity | Disposition | Basis / blocking effect |
|---|---|---|---|
| A-1 | High | FIXED | Operative correction at §0.5. Acceptance pairing at §0.8 (sitting 4). |
| A-10 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-11 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-12 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-13 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-14 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-15 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-16 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-17 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-18 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-19 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-2 | High | FIXED | Operative correction at §0.5. Acceptance pairing at §0.8 (sitting 4). |
| A-20 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-21 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-22 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-23 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-24 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-25 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-26 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-3 | High | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| A-4 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-5 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-6 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| A-7 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| A-8 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| A-9 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| B1-1 | High | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| B1-10 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B1-11 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B1-12 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| B1-13 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B1-14 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B1-15 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B1-2 | High | FIXED | Operative correction at §0.5. Acceptance pairing at §0.8 (sitting 4). |
| B1-3 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B1-4 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B1-5 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B1-6 | High | FIXED | Operative correction at §0.5. Acceptance pairing at §0.8 (sitting 4). |
| B1-7 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B1-8 | High | FIXED | Operative correction at §0.5. Acceptance pairing at §0.8 (sitting 4). |
| B1-9 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B2-1 | High | FIXED | Operative correction at §0.5. Acceptance pairing at §0.8 (sitting 4). |
| B2-10 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B2-11 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B2-12 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B2-13 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B2-14 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B2-15 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B2-2 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B2-3 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B2-4 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B2-5 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| B2-6 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| B2-7 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| B2-8 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| B2-9 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| C-1 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| C-10 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| C-11 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| C-12 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| C-13 | High | FIXED | Operative correction at §0.5. Acceptance pairing at §0.8 (sitting 4). |
| C-14 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| C-15 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| C-16 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| C-17 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| C-18 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| C-19 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| C-2 | High | FIXED | Operative correction at §0.5. Acceptance pairing at §0.8 (sitting 4). |
| C-3 | High | FIXED | Operative correction at §0.5. Acceptance pairing at §0.8 (sitting 4). |
| C-4 | High | FIXED | Operative correction at §0.5. Acceptance pairing at §0.8 (sitting 4). |
| C-5 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| C-6 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| C-7 | High | FIXED | Operative correction at §0.5. Acceptance pairing at §0.8 (sitting 4). |
| C-8 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| C-9 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| D-1 | High | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| D-10 | High | FIXED | Operative correction at §0.5. Acceptance pairing at §0.8 (sitting 4). |
| D-11 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| D-12 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| D-13 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| D-14 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| D-15 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| D-16 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| D-17 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| D-18 | Medium | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| D-19 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| D-2 | High | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| D-20 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| D-21 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| D-22 | Medium | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| D-23 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| D-24 | Low | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| D-25 | Low | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| D-26 | Low | FIXED | §6.3 status labels reconciled with the acceptance record by the sitting-4 consistency pass; the §6.3 head note binds every label there to this register and the gate records. |
| D-3 | High | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| D-4 | High | FIXED | Breach record at §0.4, from the shelved evidence pack (34243892). |
| D-5 | High | OPEN | Not individually verified by Claude and not yet individually corrected; carried into the Rev 14 inspections with its provenance preserved. Blocks: no batch at draft; an inspector may promote it at inspection. |
| D-6 | High | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| D-7 | High | CLOSED | Alex withdrew the verbatim requirement under Ben's ruling (gate record = intent, not vernacular); the labelled summary stands. |
| D-8 | High | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| D-9 | High | FIXED | Correction or qualification recorded at §0.6. Acceptance pairing at §0.8 (sitting 4). |
| F1 | Medium | FIXED | S1 re-pin at §0.6 D-8(d); §2.2 S1 row amended to pin both plan states explicitly. |

Register totals: 102 entries — FIXED 41, CLOSED 1, OPEN 60.

### 0.8 Acceptance evidence — every correction paired with its proof (crosswalk F)

No correction in §§0.5–0.6 is accepted on the builder's report. Each
correction names below the test or inspectable record that discharges
it; the artefact is preserved so an independent party can reproduce
or inspect it, and the gate record that claims the correction carries
the artefact's hash and its holder (§0.6, D-11). Statuses are stated
as NOT YET RUN until the record exists.

1. **Lane inventory (crosswalk A).** The deployed components and
   process paths in the environment of record are enumerated and
   reconciled one-for-one against the §0.2 register. A deployed
   component with no register entry, or an entry with no deployed
   component, is a defect recorded in the inventory artefact.
2. **Provider-contact policy (crosswalk B).** The policy is tested
   against one permitted lane (LANE-BRIDGE correspondence inside an
   authorised thread) and one forbidden lane (a Stage 5 live attempt
   through LANE-ADAPTER, which must refuse and record the refusal).
   Contact event records are exercised for each outcome class —
   authorised, refused, timed-out, failed, and a retry recorded as a
   separate linked event. The D-4 reconciliation stands as the worked
   example already executed: evidence pack (34243892) checked against
   the full harness log and the shelved extract (4c6e0b31),
   call-for-call.
3. **Privilege boundary (B1-2, B1-8, B2-1, B1-1, B1-12).** OS-level
   tests in the environment of record: the child's environment,
   working directory, and umask read back from the operating system
   and compared to the §0.5 declaration; getgroups() read back empty
   in the child and independently from the parent; PR_GET_NO_NEW_PRIVS
   read back as 1 before exec, with the setuid-reachability probe
   showing no privilege gain; a module-plant attempt by pilot-harness
   on the supervisor's import path failing at the OS boundary; and
   symlink/FIFO/hard-link substitution attempts against run records
   refused and recorded.
4. **Adapter controls (C-3, A-7, A-3).** Against the offered build:
   loopback operation against the transport double succeeds; the
   proxy-canary test records no canary connection and an adapter
   refusal; a hostname resolving to a non-loopback address fails
   closed; a loopback endpoint answering with a redirect to a
   non-loopback address fails closed; and the stub/double separation
   is shown by captures produced through the adapter's real path
   against the stub, distinct from wire-event captures against the
   double.
5. **Record integrity (C-4, B2-6, B2-7, B2-8, A-9).** The torn-write
   test runs by fault injection against the offered production
   artefact at its recorded hash. Issuance ordering is tested under
   interruption: no issuance precedes a committed, read-back
   RUN_STARTED; every issuance in the test run reaches exactly one
   terminal event; a supervisor-death drill produces the recorded
   SUPERVISOR_LOST outcome and no silent continuation; a forced
   capture-write failure produces CAPTURE_WRITE_FAILED and a halted
   run.
6. **Checkpoint and production purity (C-7, B2-9).** The Batch 0
   checkpoint bundle for the environment of record is checked for
   completeness against the §0.5 C-7 list, with missing elements
   labelled NOT YET RUN or OPEN. The offered production launcher
   artefact is inspected for test-hook absence by artefact scan; the
   scan output is the evidence, not a build flag.
7. **Examiner independence (D-10, C-13).** Receipt confirmation is
   reproduced by the examiner of record from the canonical record
   hash, independently of the builder's gate outputs, and filed as
   its own artefact. G5 publishes its ANSWERABLE and UNANSWERABLE
   counts; as a control, an examiner run with artefacts withheld must
   fail G5 under the §0.5 C-13 bound — a G5 that passes on withheld
   artefacts is itself a defect.
8. **Gate records (D-11).** Every gate record in the build is
   inspected for the four required fields — gate holder, evidence
   location, evidence hash, independent re-deriver — and an
   incomplete record fails its gate.

### 0.9 Authority and sequencing (crosswalk G)

1. **Ben** owns project authority: the build go, the Stage 6
   decision, shelf publication, spend, outreach, and accounts. No
   other party's approval substitutes for his on those matters.
2. **Alex** performs technical adjudication and independent
   inspection inside the programme loop Ben has established.
3. **Claude** performs a fresh independent inspection of the same
   pin. Neither inspector's verdict is an input to the other's.
4. **Remmy** drafts this specification, coordinates the loop, and
   builds only when named as builder in Ben's go for that scope.
5. This revision, drafted and inspected, **authorises no
   implementation and no provider contact**. Batch 1 stands CLEARED
   and frozen. Batch 2 remains CLOSED until all of the following
   stand: this specification shelved at a pin; independent
   inspections of that exact pin by Alex and by Claude; findings
   adjudicated and corrected; final verdicts recorded; and Ben's
   re-issued build go naming the builder and the scope.
6. Stage 6 follows its own sequence (§0.6, D-3): the Stage 5 freeze
   event (§0.6, D-16), then pre-flight on Ben's decision, then — and
   only then — subject contact through LANE-ADAPTER.

## 0A. REV 15 AMENDMENTS — ANSWERING ALEX'S REV 14 VERDICT

This section is Rev 15's governing amendment layer, drafted by
Remmy against Alex's independent inspection of Rev 14
(pb-mwfkgkm5-i-gog7; verdict shelved verbatim at commit
43f58ccfb10687494f9cf2f5eb142d4f36be364d). §0 remains Rev 14's
governing amendment layer. Where §0A and §0 or the body §§1–7
conflict, §0A governs, under the same rule §0 states for itself.
Nothing in §0A authorises any build step, provider contact, or
Stage 6 action.

### 0A.1 B1-2 — the child environment allowlist (B1-2 FIXED)

§0.5's B1-2 clause referenced "the build's environment table";
no such table existed. This subsection IS that table. The
complete environment of every child the supervisor spawns —
the launcher, and through it the harness programme — is exactly:

| Variable | Value |
|---|---|
| PATH | /usr/bin:/bin |
| LANG | C |
| LC_ALL | C |
| TZ | UTC0 |
| HOME | /srv/nemotron-pilot/homes/<account> (the child's own account) |
| TMPDIR | /srv/nemotron-pilot/tmp/<run-id> (created mode 0700 by the supervisor before spawn; removed at terminal closure) |
| PYTHONPATH | /srv/nemotron-pilot/build/<build-pin>/lib (the frozen import root, and nothing else) |
| PYTHONNOUSERSITE | 1 |
| PYTHONDONTWRITEBYTECODE | 1 |
| PYTHONHASHSEED | 0 |

Every variable not listed is ABSENT — expressly including all
proxy variables, all credentials and API keys, all SSH and agent
variables, and anything the parent's environment happens to
hold. The supervisor constructs the environment from this table
alone, with no inheritance; the launcher passes it through
unchanged and adds nothing. The run identifier travels by
argument vector only, never by environment. Read-back and
halt-on-deviation follow §0.5's B1-2 clause: any variable
present that is not in this table is a build defect and the run
halts as an infrastructure failure before the first record
write.

### 0A.2 C-3 — loopback proxy canary (C-3 FIXED)

§0.5's C-3 clause, §3.7, and §0.8 named a recording EXTERNAL
canary as the proxy-refusal witness. Under the Stage 5
zero-egress rule that canary is unreachable, so its silence
would prove nothing about the adapter. Superseded as follows:
the proxy variables the adapter honours are pointed at a
recording canary bound to loopback (127.0.0.1, an ephemeral
test port) INSIDE the permitted Stage 5 boundary. The test
passes only when (a) the adapter's refusal record states
proxy-configuration refusal before any connection attempt,
(b) the canary's log shows zero connections, and (c) the
adapter-side connection evidence shows no connect to the
canary address. The separate zero-egress evidence set is
preserved unchanged and is not discharged by this test.

### 0A.3 D-11 — gate holders and re-derivers (D-11 FIXED)

§7 required gate records to name a holder without naming the
holders. They are:

| Gate | Holder | Independent re-deriver |
|---|---|---|
| G1 | Examiner of record | Second inspector |
| G2 | Examiner of record | Second inspector |
| G3 | Examiner of record | Second inspector |
| G4 | Examiner of record | Second inspector |
| G5 | Examiner of record | Second inspector |

The Examiner of record is Alex, or a successor inspector Ben
names. The second inspector is Claude. The builder is never a
holder and never a re-deriver; supervisor and harness outputs
are evidence inputs only. While no second inspector is
available, a gate is NOT certified — re-derivation pending is
recorded as such, never waived. A gate record missing any of
D-11's four fields (holder, evidence location, evidence hash,
independent re-deriver) is incomplete.

### 0A.4 D-4 — invocation count corrected

§0.4's count is corrected in place: twelve log entries
representing nine distinct harness invocations. The D-4
evidence pack is historical evidence and is NOT altered. The
full 159-entry harness log is shelved at
duenna/CRUSHER-LOG-FULL-2026-11-13.jsonl (commit 43f58ccf,
sha256 8e44d5021e272bb5c036879c0920d2fc9cd50b22ae7434fc9e4f0f7996590b5e),
so the pack's full-log reconciliation is independently
inspectable rather than only reported.

### 0A.5 Introductory material

The front matter is corrected in place: Rev 15 is identified
as the current revision, and the Rev 13 material that follows
is fenced as preserved history in Rev 13's own voice.

### 0A.6 D-9 — launcher exception status; why C

Status, stated uniformly wherever this document speaks of the
launcher: the exception is **approved in principle by Alex**
(pb-mwfkgkm5-i-gog7), subject to inspection of the actual
source and binary, the pinned interface, and SE-7 evidence;
**Claude's conditional acceptance is recorded at his Rev 14
interim**, and his final disposition remains pending. Every
earlier unqualified statement in this document calling the
exception "approved" — including the preserved Rev 13
narrative — is superseded by this subsection. D-9 remains
OPEN in one respect only: Claude's final disposition.

Why C, and not another compiled language (Alex's question):
the launcher sits in the trusted computing base with root
authority, so its mass is its risk. C compiles to a single
static binary with no runtime, no interpreter, no garbage
collector and no standard-library machinery beyond what the
source itself names; its syscall surface is exactly the
surface the pinned source shows, and the whole component is
small enough to be read in full at SE-7 inspection — the
property the exception's conditions depend on. A managed or
runtime-carrying compiled language would put a runtime the
inspectors did not read inside the one component they must
read completely. (Drafter's rationale, offered for
adjudication.)

### 0A.7 Stage 5 exception scope — lanes

The §0.3 per-operation exception for Stage 5 provider contact
is available ONLY to LANE-CRUSHER, and only for evidence
retrieval. LANE-ADAPTER has no Stage 5 exception of any kind;
the adapter's first contact is Stage 6's. No other lane may
receive a Stage 5 provider-contact exception under this
specification; widening this scope requires a new revision,
fresh inspection, and Ben's ruling. §3.7's wording is aligned
in place. (This states the boundary as Ben ruled it on
2026-11-13 — Crusher's lane is inside the system, and its
contact is governed contact, not an outside lane's freedom —
and is offered for Alex's adjudication.)

### 0A.8 D-5 — precise status

D-5 remains OPEN, restated precisely: PARTLY ADDRESSED,
PARTLY VERIFIED (Alex, pb-mwfkgkm5-i-gog7). The provenance
record and the recovered catalogue artefact verify against
their Shelf copies; the original main-session transcript line
and execution timestamp are not independently verifiable
because the transcript is not a Shelf artefact. Nothing
further is claimed for the recovered response.

### 0A.9 Register state as amended by Rev 15

B1-2: FIXED (§0A.1). C-3: FIXED (§0A.2). D-11: FIXED (§0A.3).
D-4: the record wording corrected (§0A.4); the breach
disposition is unchanged. D-9: OPEN in the single respect
named at §0A.6. D-5: OPEN as restated (§0A.8). D-18: OPEN —
recovery of Claude's Rev 11 finding texts from the authorised
local record (this programme's chat record of 2026-11-12, the
only place the returned text exists) is underway; until the
verbatim texts are filed as a retrievable artefact, D-18
continues to block inspection completeness, and no disposition
of its findings is made from summaries. All other §0.7 entries
stand unchanged.

## 1. MECHANISM — THE FLOW THIS BUILD IMPLEMENTS

*This section is the build spec's opening named section, as
required by Alex's Rev 03 verification (pb-mweay8ri) and recorded
in REVISION-04-NOTE.md. It states, in Ben's terms
(NOTE-20261112-duenna-flow-both, voice call 2026-11-12), how
Duenna and the subject relate — so the build is judged against
the flow its owner can picture, not against sections the flow is
distributed across.*

Ben's question was whether Duenna should be a tool the subject
accesses, or the underlying framework around the subject. His
answer: **both.** Duenna has two complementary roles:

**Role 1 — the outer governance frame.** Duenna is the
accountable structure that holds the subject: it defines the
work, the authority under which the work runs, the permitted
operations, the validation rules, the evidence preservation, and
the lifecycle (trigger, progress, satisfaction, failure,
closure). The subject works inside the frame and owns none of
it. What the frame issues is the work; what the frame keeps is
the record; what the frame alone may do is validate and write.

**Role 2 — the mediated tool interface (intended architecture;
DISABLED in this pilot).** Where enabled, the model may request
Duenna-provided operations — "the mechanism that it uses to get
information from the index, the files, the spec sheets" (Ben).
The governed cycle is: Duenna issues work and permitted tools →
the model requests an operation → Duenna validates the request
and executes it within the permission boundary → Duenna
validates the returned evidence → the system-controlled write
and record. The cycle may turn — "it's not a circle and it
should be a circle; it's not a looping circle" (Ben) — but the
gate in the circle never moves: **the model proposes, the system
verifies, nothing flips. The work can loop, but authority and
the write boundary never move to the model** (Alex's summary,
accepted). The model never directly controls the underlying
source or the record.

**What this pilot builds is Role 1 only.** Per Alex's
correction (pb-mweay8ri), accepted and recorded: the current
pilot does **not** implement the tool-calling circle, and this
build must not quietly add it. Concretely, in this pilot:

- Nemotron has **no tool access**. It receives only the declared
  inputs the harness assembles for each [MODEL] step (Harness
  §1.3), and nothing else: no corpus access, no filesystem or
  process access, no access to any prior step's output except as
  a declared input of the current step.
- The harness executes the [TOOL] steps **itself**, deterministically,
  against the pinned corpus snapshot. The five tools are harness
  machinery, not subject capabilities.
- The adapter exposes **no model tool-calling interface**: its
  single operation is `complete(step_inputs)` (Adapter §5). If a
  [MODEL] step's output asks for a tool call, that text is just
  `raw_output` — preserved evidence, acted on only as the trees
  declare, never as a command channel.

The full tool-calling cycle of Role 2 is specified here as the
intended Duenna architecture so the boundary is explicit and
inspectable. Building any part of Role 2 — a request channel, a
tool schema offered to the subject, an execution path keyed to
subject output — is outside this specification and outside the
pilot. A build found to contain one has failed this section,
whatever else it passes.

---

## 2. SOURCES — THE PINNED SET THIS BUILD FOLLOWS

### 2.1 The Build Law rule

**The build follows this specification and its pinned sources —
nothing else.** Where this spec and a governing source conflict,
or where a source underdetermines a behaviour the build must
exhibit, the builder **stops and asks** (Ben/Alex, through the
Stage 5 inspection channel); the builder never improvises a
settlement into code. Settlements reached are recorded as dated
amendments to this spec or to PILOT-MANIFEST-01, before the
affected batch proceeds — never retrofitted after the fact.
Design positions the sources carry as open questions with
recommended defaults are adopted as the build baseline in §6.2,
each named; an inspector striking any one of them converts it to
an amendment item, not a builder's choice.

### 2.2 Governing documents — the current set

| # | Document | Pin / commit | Role for the build |
|---|----------|--------------|--------------------|
| S1 | `NEMOTRON-PILOT-PLAN-01-DRAFT.md` (Plan 01, ADOPTED) | **Rev 14 dual pin (§0.6 D-8(d)):** adopted state — sha256 `2449c259cf73d688932d1ad1c91fb12a225eb35dc7cb3494d5e62adaeb1cb6f1` (7,497 B; PILOT-MANIFEST-01 row 1), the freeze's historical referent; amended shelved state (operative) — sha256 `743e7dd4fa0a7296c81ee8e317c234b39f7bb326bb79f441e1929b4e489aa949` (8,205 B; on the Shelf at `duenna/NEMOTRON-PILOT-PLAN-01-DRAFT.md`) | The governing plan: pilot question, stage structure, exclusions, retained core, and the 2026-11-12 amendment recording Ben's index rule (index artefacts are system-written only; read access only for every agent, tool, seat, and harness). |
| S2 | `PILOT-MANIFEST-01.md` (Stage 0 source freeze) | The freeze itself; its 12 rows are the V2 source pins (table §2.3) | The Stage 0 freeze. Amended at Stage 5 by the re-freeze amendment (§4, Batch 0) — amended, never rewritten. |
| S3 | `PILOT-HARNESS-DESIGN-03.md` (Rev 03) | Shelf content of commit `dae374ba073fe3bc86b20c6fbaabc6781fc09e42`; file sha256 `b0fca1259c0f6432437535ad92224ad8cd824f71a078d91b7f455182c8df0d04` | The harness specification: driver (§1), record schema `PILOT-RUN-RECORD-01` (§2), tools (§3), provenance rule + SE-1…SE-7 (§4), corpus snapshot (§5), stops (§6), replay (§7). |
| S4 | `NEMOTRON-ADAPTER-DESIGN-03.md` (Rev 03) | Shelf content of commit `dae374ba…`; file sha256 `5be7eb0e59793b98f5352c55778ca2da755e6078be70c00859e3dcc8174909bb` | The adapter specification: identity pin (§1), request contract (§2), capture schema `ADAPTER-CAPTURE-02` (§3), failure taxonomy (§4), interface boundary (§5). |
| S5 | `PILOT-ACCEPTANCE-CRITERIA-04.md` (Rev 04) | Shelf commit `14b3087352c2e697f52ded70b57eeebdb2ab6fdc`; file sha256 `7608d74eef511b59ae59c33d18b299ac050c943ebebc10aeed816e101a822e2e` | The acceptance criteria: scoreability (§1), scoring ownership (§2), breach list (§3), sabotage battery S1–S5 + interrupted-write test (§4), calibration (§5), outcomes and stops (§7), re-derivation test (§8). |
| S6 | `INTERPRETATION-NOTE-01.md` | File sha256 `94d40cc7477fccc040013a24caf693826b1e28a07a7f3f1f6367fc7f8eb61771`; pinned by hash in the Batch 0 re-freeze | The pinned model-neutral reading of the nine trees (rules R1–R8). The pinned tree text prevails on any conflict with the note. |
| S7 | `V2-QUALIFICATION-01.md` | File sha256 `6ae47780785001b6ffc68b73bc2b0a3e11cc9b0a8def493d958b86d60e2f623a`; shelved in the Rev 01 package | Stage 1 qualification: capability labels, the §3 executed `reference_insert` finding (the defect the provenance rule fixes), the §5 declared changes this build implements. |
| S8 | Rev 01 design package (Harness/Adapter/Criteria Rev 01) | Shelf commit `96c74478c576aadc150361998114c3b58a463f41` | The inspected set of record. Superseded as design by Rev 03/04; retained as the inspection baseline and pin provenance. |
| S9 | `REVISION-02-NOTE.md`, `REVISION-03-NOTE.md`, `REVISION-04-NOTE.md` | Shelved with their revisions (`499cad09…`, `dae374ba…`, `14b30873…`) | The rulings history: corrections A–F and their dispositions; Alex's parameter ruling; the CRASH commitment; the four extraction outcomes; the mechanism-section requirement (Rev 04 note); the Rev 03 pin clarification (Rev 04 note). |
| S10 | `NOTE-20261112-duenna-flow-both.md` | File sha256 `a2eacc3aa1e32e6d7c6003087811f2eee3f92690df1273b659491551d753f257` | Source of §1: Ben's mechanism statement with Alex's correction appended. |

### 2.3 The frozen V2 sources (PILOT-MANIFEST-01 rows 2–12)

The build's raw material, pinned at Stage 0; any mismatch voids
the pin and stops the affected work (§6 of the harness design;
Criteria §7.2(1)):

| Row | Artefact | sha256 |
|-----|----------|--------|
| 2 | `duenna/qwen-ab/v2/V2-PACKAGE.md` | `3dcda7b285f3eb26c979a4bf48b410196d0c804cf5b4f24482882cbe2cc3754f` |
| 3 | `duenna/qwen-ab/v2/PROCESS-TREES.md` (the nine trees, T01–T09) | `5528ab69bec2f7fcdea776748e9bdc2e84ec97b4fa1d4be35bf7fd386e24b0ad` |
| 4 | `duenna/qwen-ab/v2/tools.py` (the qualified V2 baseline; **never edited** — PILOT-TOOLS-01 is a new artefact, Harness §4.4) | `e78f45d31ed6831253ed5fed1dc3f5dd22938b70e7c47cd15e190b912161cc1d` |
| 5 | `duenna/qwen-ab/v2/demo_tools.py` | `6c960e442009c6c8978eaeab506311626f74df014aac50ef7bff42ff5bdb4648` |
| 6 | `duenna/qwen-ab/v2/DEMO-RESULTS.json` | `baaca7a840d19a194a9754be513d8a95f92657ba2624a0cc62ec1f1663b02dbf` |
| 7 | `duenna/qwen-ab/run_ab.py` (dependency source only; its constants become pilot data, Harness §3.3) | `acb647bd50bfa2f6a219415dd60242a3efbacbf5a68a2d16ac7c3dbd57663d53` |
| 8 | EXTERNAL `~/workspace/pulse-bridge/index/query.py` (corpus loader; the snapshot's provenance) | `f8f2c7cad78089451399564dff19e22aa1c6fc6038f9efb832a9c01954905e32` |
| 9 | EXTERNAL `~/workspace/pulse-bridge/index/sections.jsonl` (the frozen corpus: 1,156 sections, 3,709,804 B) | `b107e8926abc5fed666c460591850adf41efd5b7d46067f2ee2f546e49c5823e` |
| 10 | EXTERNAL `~/workspace/pulse-bridge/index/manifest.json` | `c93eaa1906a068c53bf7fc54e872941b5556a97200ba6129aaf350a65ac4c452` |
| 11 | `MANIFEST.md` (shelf root; source of the pilot-manifest rows that replace the live read) | `3b4462fbfb5c1ea644272e905d0e4ee3bf9121df57ab9a6a282346b7634ce21f` |
| 12 | `duenna/qwen-ab/QWEN-AB-EVIDENCE-MANIFEST.json` (T01's cited source) | `d544cad83cd86b5b54ebcd02120037c74451e678aa7d1d0e7415ede921bfd56d` |

**The corpus and Ben's index law.** Rows 8–10 live under the
bridge index folder, outside the shelf. The build reads them
**once, read-only**, to take the pinned snapshot (Harness §5;
§3.2 below); it writes nothing there, at any batch, for any
reason. The Stage 0 pins are the tripwire: if either corpus file
fails its pin at snapshot time, Batch 0 stops and the mismatch
is reported — the build does not proceed on a moved evidence
base, and no re-freeze is improvised.

### 2.4 What the build produces (new artefacts, all pinned at Batch 0's re-freeze or at their batch checkpoint)

- **PILOT-TOOLS-01** — the model-neutral tools revision (Harness
  §§3–4), a new artefact; the pinned `tools.py` is never edited.
- **EXTRACTOR-RULES-02** — the extractor rules as versioned pilot
  data (Harness §3.2).
- **PILOT-DATA-PACKS-01, PILOT-DATA-EXPECTED-01,
  PILOT-DATA-T09-01, PILOT-DATA-FIXTURES-01** — the pilot data
  files (Harness §3.3).
- **PILOT-CORPUS-SNAPSHOT-01** — the pinned corpus snapshot
  (Harness §5).
- The **driver + record writer** implementing `PILOT-RUN-RECORD-01`
  (Harness §§1–2).
- The **issuance registry** (Harness §4.2) — harness-internal
  state, specified here, built in Batch 2.
- The **run supervisor** and the `commitments/` store (§3.5),
  and the **privileged launcher binary** (§3.5) — root-owned,
  setuid, its source pinned in the re-freeze amendment; part of
  the inspected build.
- The **adapter** implementing `ADAPTER-CAPTURE-02` (Adapter
  §§2–5), including the helper wrapper of Adapter §3.2.
- The **examiner tooling** implementing the replay procedure
  (Harness §7; Criteria §8) as a runnable artefact, so inspection
  and Stage 6 examination run the same code path the criteria
  describe.
- **PILOT-CALIBRATION-01** — the calibration certificate
  (Criteria §5), produced in Batch 6.
- The **Stage 5 evidence pack**: the sabotage battery's scratch
  record, the interrupted-write test's artefacts, the SE-1…SE-7
  demonstration results, the stub-subject full-battery record,
  and its re-derivation report — preserved for inspection,
  verified by re-derivation, not by summary (Criteria §4, §8).

---

## 3. COMPONENT SPECIFICATIONS

Each subsection states what the builder builds, the governing
source for every behaviour, and the checkpoint evidence the
batch must produce. Where a behaviour is specified in a source
by section number, this spec cites it and does not restate it
loosely: the source text governs.

### 3.1 Driver (Harness §1)

Build a driver that executes the nine pinned trees
(`PROCESS-TREES.md`, row 3) as read under INTERPRETATION-NOTE-01
(S6). Requirements:

- **Order and dependency.** Steps execute in declared order;
  dependencies are the trees' chains; the driver never reorders,
  parallelises, or skips a step whose dependencies are satisfied
  (Harness §1.1). A step whose dependency failed does not
  execute; the tree follows its failure path.
- **Step types.** [TOOL] and [RULE] steps execute
  deterministically in harness code; [MODEL] steps call the
  adapter's `complete()` exactly once per step attempt with the
  assembled `step_inputs`; every step's declared *Verify*
  condition executes as a distinct [CHECK] phase with its own
  record event (Harness §1.2). A step is satisfied only when its
  operation completed **and** its [CHECK] passed.
- **Declared-inputs-only assembly.** Before any [MODEL] call
  the driver assembles the step's input manifest — exactly the
  artefacts the tree declares, each cited by record reference
  and hash — and writes it to the record **before** the call
  (Harness §1.3). Messages are constructed only from the pinned
  tree text (verbatim) and the manifest's artefacts, serialised
  in the canonical form pinned at §3.4 (RFC 8785), per
  Adapter §2.2.
  The subject never hunts raw sources; tree source prohibitions
  are enforced structurally (e.g. T05-STEP-06 never receives the
  draft's own values; T08's seeded draft is an input to
  diagnosis only).
- **Failure branches — the trees' rules, no others** (Harness
  §1.4): STOP steps halt the tree; return-once recoveries
  re-attempt once with the failure named in the re-attempt's
  declared inputs; bounded corrections (T05-STEP-06,
  T08-STEP-04) allow at most 2 attempts; absence-as-finding
  answers UNKNOWN by rule; the T09 decision-stands rule keeps
  the worksheet as the system decision. An ADAPTER_FAILURE
  closes the tree `INVALIDATED-INFRASTRUCTURE` unless a tree
  declares a covering recovery (none does). A GOVERNANCE_FAILURE
  is recorded and follows the tree's failed-verification path —
  never retried away, never reclassified.
- **No verdicts.** The driver emits the record and nothing else:
  no score, no pass/fail for any tree (Harness §1.5; Criteria
  §2).
- **Budgets and stops** (Harness §6; Criteria §7.2): [TOOL]/[RULE]
  step 60 s; [MODEL] step 300 s; tree 3,600 s; run 4 h wall
  clock; the lane-failure rule (3rd INVALIDATED-INFRASTRUCTURE
  closure stops the run); the integrity rule (snapshot hash
  re-verified at every `TREE_TRIGGERED`); stop finality (after
  `RUN_STOPPED`, nothing further is written).

### 3.2 Tools — PILOT-TOOLS-01 (Harness §§3–4)

Build the five tools as a **new, versioned artefact** standing
on the model-neutral interfaces — never as an edit of the
pinned `tools.py`.

- **Corpus interface** (Harness §3.1): implement `CorpusSource`
  (`get_section`, `get_manifest_row`) satisfied by exactly one
  implementation: a reader over **PILOT-CORPUS-SNAPSHOT-01** —
  the Stage 0 corpus files copied read-only into the pilot set
  at Batch 0, each section's recorded hash and both files'
  Stage 0 pins verified equal at copy time and the equality
  recorded in the re-freeze amendment (Harness §5) — plus the
  pilot-manifest data (§3.3 data files) serving the
  `pilot-manifest:` namespace. The tools import this interface
  and nothing else: no trial runner, no module-level corpus load
  from a home-tree path, no subject code. After Batch 0 the
  bridge index folder is out of the pilot's runtime path
  entirely.
- **Extractor rules as data** (Harness §3.2): implement
  `EXTRACTOR-RULES-02` as a versioned JSON data file
  (`{field, rule_id, pattern, group, value_type, version}`),
  covering the four V2 fields plus each further field the trees
  name, each added by declaration. A field with no rule is NOT
  FOUND by declared design, visible in the data.
- **The four outcomes, exactly** (Harness §3.2, Rev 03):
  no pattern match → **NOT FOUND** (absence + reason recorded);
  matches exist but all fail type validation → **TYPE FAILURE**
  (matched text + expected type recorded, **no value**);
  exactly one valid match → **EXTRACTED** (value + evidence
  line); more than one valid match → **AMBIGUOUS** (every
  candidate recorded, **no value**). Mixed valid/invalid matches:
  type-failing matches are recorded as rejected candidates and
  the count runs over the valid ones. There is **no tie-break of
  any kind** — no first-match, last-match, or longest-match
  selection anywhere in the extractor, the tools, or the
  harness. AMBIGUOUS and TYPE FAILURE are first-class result
  states: not insertable, satisfying no extraction requirement.
- **The five tools** (Harness §3.4), result schema unchanged
  from V2-PACKAGE with the `verification` set extended as above:
  `shelf_lookup` via `CorpusSource` only (no live shelf, no
  absolute paths); `source_extract` per the rules data and the
  four outcomes; `reference_insert(field, process_step,
  operation_id)` with the §3.3 provenance rule — its signature
  takes a harness-issued `operation_id`, and **a caller-built
  dict is not a representable input**; `verify_field` with
  `expected` sourced from PILOT-DATA-EXPECTED-01 or a prior
  verified extraction, cited in the record; `receipt_worksheet`
  over the PILOT-DATA-T09-01 artefacts, cited by hash.
- **Pilot data files** (Harness §3.3): produce
  PILOT-DATA-PACKS-01 (the `P_T01…P_T09` packs as data),
  PILOT-DATA-EXPECTED-01 (ground truth incl. `EXPECTED_RECORD`),
  PILOT-DATA-T09-01 (`OBLIGATION_T09`; receipts FR-A / FR-B /
  FR-C / FR-VALID verbatim), PILOT-DATA-FIXTURES-01 (T08's seeded
  invalid draft, T04's arm instruction set / boundary-table
  source, T07's register fixture, T01's pack manifest reference).
  Content is transcribed from the pinned `run_ab.py` constants —
  transcription is verified value-by-value against the pinned
  source at the Batch 1 checkpoint, and each file is pinned by
  sha256 in the re-freeze amendment.
- **Logging contract** (Harness §3.5): every tool invocation —
  including `reference_insert` and including refused inserts —
  produces its `TOOL_INVOKED`/`TOOL_RETURNED` event pair; every
  insert additionally produces its `LEDGER_ENTRY` or
  `GOVERNANCE_EVENT`. There is no tool call in a run that is not
  in the record.

### 3.3 The provenance rule and the issuance registry (Harness §4)

- **Acceptance set.** `reference_insert` inserts only a result
  that is (1) `verification == "EXTRACTED"`, issued by
  `source_extract` — FOUND, NOT FOUND, AMBIGUOUS, and TYPE
  FAILURE results are never insertable; (2) present in the
  issuance registry, unconsumed, issued in this run to the same
  tree/step context that presents it; and (3) recomputed
  successfully at insert time (below).
- **Recomputation at insert time** (Harness §4.2): re-fetch the
  section via `CorpusSource`; recompute its sha256 and require
  equality with the result's `source_hash` **and** the snapshot's
  recorded hash; re-apply the field's rule (same `rule_id`, from
  the pinned rules data) under the four-outcome semantics and
  require exactly one valid match, the value byte-for-byte, and
  the evidence line verbatim in the section text; require the
  registry entry's recorded value/hash to equal the presented
  ones.
- **Consumption.** Exactly once, for one field; the registry
  marks the entry consumed. A second presentation is a refusal
  (no tree declares reuse). Multi-field use of one source is
  served by separate extractions.
- **Refusal behaviour** (Harness §4.3): on any failed condition
  the insert **refuses** — returns `{refused: true, reason,
  claimed, recomputed}`, emits **no** `LEDGER_ENTRY`, returns
  **no** value, and the harness records a `GOVERNANCE_EVENT`
  (kind `INSERT_REFUSED`) with the full claimed-vs-recomputed
  detail. A refused insert is never retried with a repaired,
  edited, or re-labelled presentation; recovery is only via a
  fresh `source_extract`.
- **Registry — the five properties** (Harness §4.2, Alex's
  correction B): (1) the registry is **private to the harness** —
  harness state, created and held by harness code, readable and
  writable by nothing outside it; (2) **an identifier alone
  cannot manufacture an entry** — entries come into existence
  only when the harness itself executes a tool and registers its
  result (at the `TOOL_RETURNED` event for `source_extract`);
  presenting an id with no entry is a refusal, and the id's
  guessability is irrelevant because guessing buys nothing;
  (3) every entry is **bound to its run, tree, step, and tool
  invocation** — the registry records `{operation_id, tool,
  source_ref, source_hash, value, evidence_line, rule_id,
  issued_at_seq, tree_id, step_id}`; presentation from a
  different context is a refusal; (4) consumption is
  **exactly-once**, and the consumption mark is part of the
  entry; (5) registry state is **independently reconstructable
  from the event record alone** — the registry is a cache of the
  record, not a second source of truth.
- **Identifiers.** Operation ids are harness-issued and
  sequential within the run (`op-<seq>`). Sequential ids are
  **not** unguessable, and unpredictability is **not** a security
  property of this design; no inspection may credit an id form
  as a security measure (Harness §4.2).
- **Structural requirements SE-1…SE-6** (Harness §4.5) are
  properties of the built code's structure, demonstrated at the
  §5 gates: **SE-1** the harness is the sole issuer of extraction
  results; **SE-2** the insert interface accepts no
  caller-supplied provenance — its only handle is the
  `operation_id`; **SE-3** the registry cannot be modified by
  the subject (the subject has no access path of any kind to
  harness state); **SE-4** value and source are recomputed
  against the pinned snapshot at insert time and again at
  replay; **SE-5** a consumed operation cannot be used again;
  **SE-6** a refusal produces no ledger entry and no usable
  value, and no fallback path (default value, cached result,
  insert-anyway branch) exists anywhere in the insert call
  graph.

### 3.4 Canonical execution record (Harness §2)

- **Form** (Harness §§2.1–2.2): one run = one append-only JSON
  Lines file, `run-record.jsonl` — one JSON object per line,
  written and flushed at the moment the event occurs, never
  edited afterwards. Event schema `PILOT-RUN-RECORD-01`: `seq`
  (strictly increasing from 1; a gap voids the record),
  `event_id` (`"<run_id>:<seq>"`), `run_id`
  (`<battery-id>-<UTC date>-<counter>`), `recorded_at_utc`,
  `event_type` (the closed §2.3 list), `tree_id`/`step_id`,
  `payload` (full content, never a summary or a pointer to
  harness memory), `prev_event_sha256`, `event_sha256`.
- **The chain's claim, qualified** (Harness §2.6, Alex's
  correction A): the hash chain makes insertion, deletion, or
  reordering **detectable relative to the chain's own links**,
  and — with the §3.5 commitments — detectable absolutely. The
  chain alone detects accidental corruption and ordinary,
  partial edits; **wholesale rewrite is defeated by the external
  anchor, not by the chain**, and no build artefact, comment, or
  report may claim otherwise.
- **Event vocabulary** (Harness §2.3): the run/tree/step event
  types as specified there, including `TOOL_INVOKED`/
  `TOOL_RETURNED` with complete payloads verbatim (nothing
  truncated), `MODEL_CALL_LINKED` carrying `{capture_id,
  record_sha256, request_sha256, response_sha256}` plus the
  verbatim `raw_output`, `CHECK_RESULT` with the declared verify
  condition quoted, and `LEDGER_ENTRY` in the established schema
  plus the §4 provenance additions (`operation_id`, recomputation
  evidence). `ledger.json` is materialised from the record by
  the declared mechanical extraction (all `LEDGER_ENTRY`
  payloads in `seq` order); the record is canonical, the file is
  a view, and re-running the extraction must yield the identical
  ledger.
- **Organisation without an index** (Harness §2.4): the
  `runs/<run_id>/` + `commitments/` layout as specified there.
  Discovery is the directory listing; linkage is by reference
  and hash, never by index. The harness writes **nothing**
  outside the run directory — never to the bridge index, the
  shelf, or any manifest; its inputs arrive read-only. It has
  **no write path to `commitments/`** (§3.5).
- **Pinned-input block** (Harness §2.5): `RUN_STARTED` embeds
  the run's complete pin set — every artefact consumed, each as
  `{path, sha256}`, verified at pre-flight against
  PILOT-MANIFEST-01 + the Stage 5 re-freeze amendment; any
  mismatch and the run does not start. The block is the chain's
  genesis; its hash is the content of the START commitment.
- **Canonical serialisation — RFC 8785, pinned (Rev 02, Alex's
  correction B).** The sources require hashes over "canonical
  serialisations" without pinning the exact byte form; Rev 01's
  description (UTF-8, sorted keys, no insignificant whitespace)
  did not fully define canonical bytes — number representation,
  string escaping, and duplicate-key handling could still differ
  between implementations, and the event chain, the receipts,
  and replay all depend on exact byte-level agreement. This spec
  therefore pins a complete standard: **RFC 8785 (JSON
  Canonicalization Scheme, JCS)** is the canonical form for
  every structured artefact the harness serialises and hashes —
  run-record events (the `event_sha256` / `prev_event_sha256`
  preimages), the receipts and commitments as serialised,
  ledger entries, capture records, registry-relevant records,
  the pinned-input block, and the issuance-record entries. The
  contract the builders implement against: number serialisation
  exactly per RFC 8785 (the ECMAScript number-to-string
  algorithm the RFC normatively adopts); string escaping
  exactly per RFC 8785 (the minimal escape set it prescribes);
  object members ordered by the UTF-16 code unit sequence of
  their names; no insignificant whitespace; the output encoded
  UTF-8. **Rejection rules:** a value that cannot be safely
  represented is **rejected, never coerced** — NaN and positive
  or negative infinity; duplicate object keys, detected at
  parse; strings containing lone surrogates; and any parsed
  value that cannot be re-serialised to identical canonical
  bytes. A rejection is a failure surfaced in the open, never a
  silent substitution. **Raw bytes are never canonicalised:**
  hashes over raw byte artefacts are sha256 over the bytes
  exactly as they lie — captured HTTP request and response
  bodies (`request_sha256`, `response_body_sha256`), the record
  file's exact bytes (`record_file_sha256` in TERMINAL and
  CRASH receipts), corpus and snapshot files, and every file
  pin. Canonicalisation applies to harness-serialised JSON
  only. **Freeze rule:** this contract — the standard
  identifier ("RFC 8785") recorded in the frozen configuration —
  is frozen at Batch 0 in the re-freeze amendment **before**
  any hash is generated; changing the canonicalisation standard
  afterwards is a re-freeze amendment, and hashes taken under a
  superseded form do not carry over. Two canonical forms in one
  record void the record. **Implementation pin (Rev 12,
  Claude's finding 8):** the standard is pinned; the
  implementation is pinned with it. The JCS implementation the
  build uses is frozen at Batch 0 by **name, version, and
  artefact hash**, recorded in the re-freeze amendment's freeze
  evidence alongside the standard identifier above; it must
  pass the **RFC 8785 conformance test vectors** as part of the
  Batch 0 freeze checks, with the vector results preserved in
  the freeze evidence; and **any change of implementation or
  version is a re-freeze event** of the same kind as changing
  the standard — hashes taken under a superseded implementation
  do not carry over. This spec names no implementation: the pin
  is taken at Batch 0, from the implementation the build
  actually uses.

### 3.5 Supervisor and commitments — the custody design, settled (Harness §2.6; SE-7)

Harness §8 Q10 left the supervisor's concrete form as a Stage 5
build decision, with the default "the lightest form that keeps
the write path outside the harness's privilege boundary." This
spec **settles** that decision as follows. It is stated plainly
as a proposal: the inspectors judge it, and an inspector
requiring a stronger form converts it to an amendment before
Batch 4 begins — the builder does not substitute another form
unilaterally.

**The design — a separate supervisor program under a separate
OS identity, owning the commitments store.**

1. **Two OS identities.** The pilot runs under two distinct
   unprivileged OS user accounts on the build machine:
   `pilot-harness` (owns and runs the harness, the tools, the
   adapter, and the run directories) and `pilot-supervisor`
   (owns the supervisor program and the `commitments/` tree).
   Neither account is the operator's interactive account, and
   neither has write access to the other's trees:
   `runs/` is owned by `pilot-harness`; `commitments/` is owned
   by `pilot-supervisor` with directory/file permissions that
   grant `pilot-harness` **no write, no create, no delete, and
   no read** on receipts or the issuance record (mode `0700` on
   the directory, `0600` on files, ownership
   `pilot-supervisor`). The mechanism that keeps the harness
   from the receipts is therefore the operating system's
   ownership and permission enforcement — named, inspectable,
   and testable — not a convention in harness code. The harness
   needs no read on `commitments/` at all: the record never
   cites the commitments back (Harness §2.4), and examination is
   performed by the examiner tooling (§3.7) running under the
   operator's authority, not the harness's.
   **Group separation (Rev 03).** As a build precondition,
   `pilot-harness` is **not** a member of the
   `pilot-supervisor` group, and `pilot-supervisor` is not a
   member of any group that confers `pilot-harness`
   privileges. The launcher's mode `4710` group-execute
   (point 2) is the control that limits who may invoke it, and
   that control proves separation only if the memberships
   actually separate — which is why the fact is read from the
   operating system and demonstrated, not inferred from the
   accounts' names (SE-7 demonstration (vii), below).
2. **The supervisor launches the harness — through the
   privileged launcher (Rev 02, Alex's correction A).** The
   supervisor is a single-purpose program run as
   `pilot-supervisor`. It cannot itself spawn a child under
   another identity — no unprivileged process can — so the
   spawn goes through a dedicated **launcher**: a minimal,
   single-purpose binary, owned by **root**, **setuid-root**,
   mode `4710` with group `pilot-supervisor`, so only the
   `pilot-supervisor` identity can execute it. Its source is
   small enough to be read in full at inspection; it is pinned
   by sha256 in the re-freeze amendment (by dated addition at
   the Batch 4 checkpoint, when it is built) and is part of the
   inspected build. **Language (Rev 12, Claude's finding 3):**
   the launcher is implemented in **C**, compiled at build
   time — Linux **ignores the setuid bit on interpreted
   scripts**, so the setuid launcher cannot be an interpreted
   programme. This is the launcher-language exception to §6.3
   item 4's Python default, recorded in that item; the rest of
   the build remains Python. The launcher accepts **no arbitrary
   input**: the harness programme path and the argument-vector
   shape are **compiled into the binary** at build time — there
   is no configuration file — and the sole variable field is
   the run identifier, validated against a strict pattern and
   passed to the harness in its fixed position. Any other
   invocation — a different programme, extra or missing
   arguments, a malformed run identifier — is refused: the
   launcher exits non-zero and spawns nothing. It invokes no
   shell, opens no network connection, and loads no code beyond
   the fixed exec. **Single-threaded across the launch
   lifecycle (Rev 07).** The launcher is a **single-threaded**
   programme: it creates no threads at any point in the launch
   lifecycle — its pinned implementation contains no thread
   creation — so the thread that calls `fork()` is the
   process's only thread; it is that same thread which drops
   privilege, releases the gate, and holds the `waitpid()`
   relationship, and it remains alive until the child's
   lifecycle completes. The constraint is a requirement of
   the backstop's semantics, not a style preference: Linux
   defines the parent for `PR_SET_PDEATHSIG` purposes as
   **the thread that created the child** (point 3), and this
   design's parent-identity reasoning is stated against a
   launcher in which thread identity and process identity
   coincide. The gate evidence includes, for each test
   launch, a launch-time record that the launcher process
   was single-threaded — the `Threads` field of its `/proc`
   status equal to `1` at launch — in addition to the source
   property itself, which stands under the launcher's pin.
   **Setuid preconditions — verified,
   fail-closed (Rev 03).** The supported operating system for
   the build environment is Linux. This design relies on the
   launcher actually receiving effective root privilege, and
   that assumption is **verified, not presumed**: a probe
   invocation (SE-7 demonstration (vii)) must observe
   effective uid `0` inside the privileged window, and the
   conditions that silently defeat setuid — the launcher's
   filesystem mounted `nosuid`, an inherited `no_new_privs`
   flag — are checked and recorded alongside it. **A failed
   privilege assumption stops the build; it never triggers a
   fallback to a weaker launch arrangement.**
3. **The spawn sequence — a gated launch (Rev 04).** The
   supervisor driver, running as `pilot-supervisor`, invokes
   the launcher once per run. Before the fork, the launcher
   creates a **private launch-gate pipe** (`pipe2(O_CLOEXEC)`;
   both ends close-on-exec except as this sequence specifies):
   the read end passes to the child, the write end is held by
   the parent, and no other process holds either end. Also
   before the fork, the parent captures the **expected
   parent identity** — its own `getpid()` — in a variable
   the child inherits across the fork as part of its memory
   image: an inherited, expected value that nothing outside
   the child's own pinned code can alter after the fork
   (Rev 07). The launcher forks. The **child**'s first act
   is a comparison: `getppid()` must equal the inherited
   expected parent identity. If it differs — the parent
   died before the child's first instruction, and the child
   has already been reparented, so a `getppid()` taken now
   returns the reaper's identity rather than the launcher's
   — the child `_exit()`s at once, without proceeding: an
   expected identity captured only after the fork could
   itself be the wrong identity, and a later comparison
   against it would pass falsely. The child then clears its
   supplementary groups and drops privilege precisely
   (Rev 03):
   `setresgid()` followed by `setresuid()`, each setting
   **all three** ids — real, effective, and saved — to
   `pilot-harness`, and verifies the result by reading back
   `getresgid()`/`getresuid()`: every position must equal
   `pilot-harness` exactly. If any `setres*()` call fails or
   the read-back mismatches, the child **terminates
   immediately** (`_exit()`); it never continues into the exec
   on a failed or partial transition, and never falls back to
   any other identity or programme. With the verified
   drop — and as part of the same post-drop verification,
   standing before the arming below, the descriptor
   close, and the gate — the child also reads back its
   own **capability state**, by one of two methods
   (Rev 10; methods distinguished, Rev 11).
   **Method A:** the `CapEff`, `CapPrm`, and `CapAmb`
   fields of `/proc/self/status`, read and verified
   directly. **Method B:** `capget`, for the effective
   and permitted sets, **plus** an explicit ambient
   read-back — `prctl(PR_CAP_AMBIENT,
   PR_CAP_AMBIENT_IS_SET, …)` queried for every
   capability number from `0` to the maximum the kernel
   supports, each query required to return `0`. The
   distinction is load-bearing: `capget` returns the
   effective, permitted, and **inheritable** sets; it
   does **not** return the ambient set, so a
   `capget`-only read-back cannot observe one of the
   three sets this clause requires. **A method that
   cannot observe the ambient set does not satisfy this
   requirement.** **All three
   sets must be empty.** Any nonzero value in any set
   means the child **terminates immediately**
   (`_exit()`), fail-closed, exactly as for a failed or
   partial transition above: the launch does not proceed
   on a dropped identity whose capability state was
   observed nonzero, or was not successfully and
   unambiguously observed in full — an unsuccessful,
   incomplete, malformed, or unavailable read-back
   bars the launch identically (Rev 11). The reason
   is stated with layer (1) in the identity-continuity
   block below: the permission guarantees this design
   relies on are discretionary, and they bind only a
   process holding no capability that bypasses them, so
   the guarantee is claimed on the **observed** state at
   the point of reliance, not inferred from the intended
   transition. The three masks as read are **preserved
   as launch evidence** — recorded in the launch record,
   alongside the launcher's `Threads` observation
   (point 2) — and are evidenced for the demonstrated
   launches in demonstration (vii). **Only after the
   verified drop and the capability verification** does
   the child arm its parent-death backstop —
   `prctl(PR_SET_PDEATHSIG, SIGKILL)` (specified with the
   parent-failure cleanup in the parent half of this point;
   placement corrected, Rev 06). The arming is **fail-closed
   on its own result (Rev 07)**: if `prctl()` returns
   non-zero, the child `_exit()`s immediately and **never**
   continues to the descriptor close or the gate; and
   immediately after a successful arming the child reads
   the setting back — `prctl(PR_GET_PDEATHSIG)` — and
   requires the value read back to equal `SIGKILL` before
   proceeding: the read-back is the direct evidence the
   requested setting is present, and a failed read-back or
   a mismatched value likewise means immediate `_exit()`.
   The ordering is dictated by
   the Linux semantics, stated plainly: **the parent-death
   signal setting is cleared whenever the process changes
   its effective user or group id** (`prctl(2)`), so it is
   armed after the transitions, and **no credential change
   follows it** anywhere in this sequence — the exec that
   ends the sequence is a plain exec, under the same
   identity and changing no credentials, of a programme
   that is **not setuid, not setgid, and carrying no file
   capabilities** — the three-part exec condition (Rev 07),
   whose verification duties are stated in the block after
   point 4, and which bind the object actually executed,
   under the identity-continuity arrangement stated in
   that block (Rev 08; claim language corrected, Rev 09)
   — protected placement no untrusted in-model identity
   can modify and the trusted launcher's pinned code
   contains no operation to modify, canonical resolution
   with the resolved object's recorded identity, and the
   parent's
   pre-release identity re-check, on which the gate's
   release additionally depends — so the armed backstop
   persists into the
   running harness: Linux clears the setting on an exec
   that changes credentials **and** on executing a binary
   with associated file capabilities, and every one of
   those routes is excluded. Immediately after arming and
   read-back, the child
   **re-checks the parent relationship**: `getppid()` must
   still return the **expected parent identity captured
   before the fork** — the inherited value, not merely
   whatever a post-fork call first returned. If it differs
   — the parent died between the first comparison and the
   completed arming, before the signal could cover the
   death, and the child has been reparented — the child
   `_exit()`s at once,
   without proceeding: the manual's warning governs both
   checks — **if the parent thread has already terminated
   by the time `PR_SET_PDEATHSIG` is called, no signal will
   be sent** — so the identity the child arms against must
   be proven live at the first comparison and again at the
   re-check, against the one pre-fork value; the two
   comparisons close both intervals — a death before the
   child's first instruction, and a death between the first
   comparison and the completed arming, the install-window
   race (demonstration (viii)). After the
   verified drop, the arming, and the re-check, and before
   the exec, the child closes **every inherited
   file descriptor except the declared allowlist** — fds `0`,
   `1`, and `2`, retained solely in their declared standard
   roles and only at their verified destinations (Rev 04; the
   descriptor-separation block after point 4), and the gate
   read end, which joins the allowlist for the pre-exec
   window only — by an exhaustive close (`close_range(3,
   ~0U)` sparing the gate descriptor, or an equivalent
   enumeration of `/proc/self/fd`), so no descriptor the
   supervisor or the launcher held open survives into the
   harness beyond the declared set. Any descriptor the
   harness opens after the exec is its own, opened under its
   own identity's permissions. The child then **blocks at the
   launch gate**: it reads exactly one byte from the gate
   read end, and only on receiving the parent's single
   release byte (point 3, parent half) does it exec the
   harness at the fixed path — the exec itself closes the
   gate read end (`O_CLOEXEC`), so the gate does not exist in
   the harness. On end-of-file — the parent's write end
   closed without a release, because the parent died or
   failed — on any other byte value, or on any read error,
   the child `_exit()`s immediately, **without executing the
   harness**: the gate never resolves in the child's favour
   by default. The **parent** immediately and irrevocably drops its
   own privileges the same precise way — supplementary groups
   cleared, `setresgid()` then `setresuid()` setting real,
   effective, and saved ids to `pilot-supervisor`, verified by
   the same read-back — so privilege cannot be regained. With
   the verified drop, and **before** the gate is
   released, the parent also reads back its own
   **capability state** — `CapEff`, `CapPrm`, and
   `CapAmb`, by the same read-back as the child half
   (Rev 10; methods distinguished, Rev 11) — and
   requires **all three sets empty**; the
   observed masks join the child's in the launch record,
   as launch evidence. Any nonzero value in any set is a
   failure detected **after** the drop, and is handled
   exactly as one: **Window 2's cleanup** (below)
   applies — the parent never writes the release byte,
   closes the gate unreleased, reaps the child, and
   makes no issuance — and the abort is recorded with
   the observed masks. **The parent must not release
   the gate unless all three sets have been
   successfully and unambiguously read and verified
   empty (Rev 11).** A read-back that fails —
   unsuccessful, incomplete, malformed, or unavailable
   — is likewise a failure detected **after** the drop,
   handled exactly as a nonzero value is: **Window 2's
   cleanup** applies — no release byte, the gate closed
   unreleased, the child reaped, no issuance — and the
   abort is recorded **noting the read-back failure as
   its cause**. An unobserved capability state releases
   nothing. Only
   on a **fully verified** parent drop — verified, that
   is, in identity and in capability state — does the parent
   **release the gate**: it writes the single release byte to
   the gate write end and closes that end. On any failure or
   mismatch the parent **never writes the release byte**, and
   the cleanup that follows depends on **when the failure is
   detected** (Rev 05): the parent is itself dropping all
   three ids to `pilot-supervisor`, so authority it holds
   before the drop it may no longer hold after it, and this
   sequence never assumes otherwise. **Window 1 — the
   failure is detected before the parent's drop has taken
   effect** (a `setres*()` call itself fails; the parent is
   still privileged): direct termination is available in
   this window and is used — the parent **kills the waiting
   child** (`SIGKILL`), closes the gate write end without
   writing the release byte, **reaps the child** with
   `waitpid()`, and only then terminates itself. **Window 2
   — the failure is detected after the drop** (the
   `getres*()` read-back mismatches, or any later failure
   before the gate is released): the parent does **not**
   rely on signalling — it may no longer hold permission to
   signal a `pilot-harness` child across the uid boundary.
   Instead the gate itself is the kill switch: the parent
   **closes the gate write end** without writing the release
   byte; the waiting child observes end-of-file and
   `_exit()`s itself, under the gate rule above; the parent
   `waitpid()`s, reaps it, and only then terminates itself.
   In **neither** window is any issuance of any kind made,
   and in neither window is a harness left running or a
   child left waiting: a failed transition never continues
   into waiting or issuance, and never leaves an executing
   or a waiting child behind (SE-7 demonstration (viii)).
   **Parent death is backstopped by the kernel (Rev 05;
   placement corrected, Rev 06; identity semantics
   corrected, Rev 07):** after its verified
   privilege drop, and before the descriptor close, the
   child sets **`PR_SET_PDEATHSIG`** to `SIGKILL` on itself
   (the child half of this point) — fail-closed on the
   `prctl()` return value and proven by the
   `PR_GET_PDEATHSIG` read-back — against the **expected
   parent identity the parent captured before the fork**,
   which the child's first comparison and its post-arming
   re-check both test. The "parent" in this mechanism is,
   in Linux's documented semantics, **the thread that
   created the child**, not necessarily the parent process
   as a whole; this design makes that distinction empty by
   construction — the launcher is single-threaded across
   the launch lifecycle (point 2), so the forking thread
   is the process's only thread, the identity the pre-fork
   capture records is that thread's process identity, and
   it is the same thread that later holds the `waitpid()`
   relationship and remains alive until the child's
   lifecycle completes. The placement is load-bearing, and Rev 05's
   was wrong: `prctl(2)` documents that the parent-death
   signal setting is **cleared** when the process changes
   its effective user or group id, so Rev 05's arming
   before the child's transitions was silently undone by
   those very transitions, and its claim that the setting
   "survives the child's credential change" was false; both
   are corrected here. Armed after the transitions, with no
   credential change following it — the exec changes no
   credentials — the setting persists, so if the parent
   dies at **any** point after arming, mid-failure,
   mid-cleanup, after the gate has been released and the
   harness is running, or otherwise, the kernel terminates
   the child directly, and no process needs signal
   authority over it. The intervals the backstop cannot
   cover are the ones before the arming completes — a
   death before the child's first instruction, and a death
   after the fork but before the arming — and those
   intervals are closed by the child's two comparisons
   against the inherited expected identity (child half): a
   child whose actual parent is no longer the expected
   parent `_exit()`s without proceeding — at the first
   comparison, or at the post-arming re-check,
   respectively. This is a
   second, kernel-level guarantee **behind** the gate's
   end-of-file path, not a replacement for it: in the
   orderly failure windows above, the gate resolves first;
   the backstop covers the parent vanishing in a state
   where orderly cleanup never runs — and, uniquely, a
   parent death **after** release, which the gate cannot
   reach. **The residual, stated
   plainly (Rev 05):** if a child were to disobey the gate's
   end-of-file while the parent lives, no unprivileged
   mechanism remains to the parent, and this design does
   not assume one. That case is excluded **by
   construction**, not handled by authority: the pinned
   child sequence has exactly two post-read branches — the
   release byte, and only the release byte, proceeds to the
   exec; anything else, including end-of-file, `_exit()`s —
   the child's code is part of the pinned trusted computing
   base (point 4(iv)), and demonstration (viii) exercises
   the pinned sequence's behaviour directly, in both
   windows. No stronger mechanism is claimed. Thereafter — the
   gate released — the parent runs as the run's supervisor: it
   holds the `waitpid()` relationship to the harness child, so
   termination, and its basis, are **witnessed by the operating
   system**, never reported by the harness (as §2.6's CRASH
   content requires); and it performs every issuance itself
   (points 5–7 below). **The privileged window performs no file
   writes at all** — its only acts are the gate-pipe creation,
   the fork, the two privilege transitions, the gate release,
   and the exec. **The ordering is the invariant (Rev 04): the
   supervisor's independent observation and issuance capability
   is fully established — parent dropped, verified, and holding
   the `waitpid()` relationship — before the subject begins
   work; there is no interleaving in which the harness executes
   while the supervisor side has failed.** Every committed value
   is computed, and every receipt written, by code running as
   `pilot-supervisor` **after** the drop. The harness cannot
   ask the supervisor to issue a receipt over values the
   harness supplies: **the supervisor computes every committed
   value itself**, from the record file, which it reads
   directly (read access to `runs/` granted to
   `pilot-supervisor` for this purpose, read-only).
4. **Alex's five points, answered.** (i) **Who may start a
   process as `pilot-harness`:** only the launcher, and only
   via its compiled-in fixed path — no account, including
   `pilot-supervisor`, holds a general ability to become, or to
   spawn as, `pilot-harness`. (ii) **What constrains the
   launcher from modifying or issuing commitments:** while
   privileged, the launcher **has root's filesystem
   authority** — this spec does not claim otherwise, and any
   earlier phrasing suggesting it lacks the OS-level
   *ability* to reach `commitments/` is withdrawn. The
   defensible claim is about its pinned implementation, not
   its authority: its code contains **no commitment-writing
   operation and no path to the `commitments/` store**, it
   performs no file writes while privileged, and it drops
   privilege before the supervisor performs any commitment
   work. The constraint relied on is therefore the smallness
   and pinnedness of that code — which is exactly why the
   launcher stands named in the trusted computing base
   (point (iv)). (iii) **How termination
   is independently observed:** the post-drop parent is the
   child's parent in the OS process tree; `waitpid()` returns
   the exit status or the killing signal directly from the
   kernel — a crash is observed, not announced. (iv) **How the
   threat model is preserved:** the launcher is a named,
   minimal addition to the trusted computing base — pinned
   source, one fixed action, no inputs beyond the validated run
   identifier, no shell, no network. The comparison with the alternatives is stated
   honestly (Rev 12, Claude's finding 4). The mode-`4710`
   launcher is itself a **standing privilege**: the
   `pilot-supervisor` identity can invoke it outside any run,
   exactly as a sudo rule would be invocable — the earlier
   rationale claimed a distinction there that does not exist,
   and it is withdrawn. The honest trade: a **narrow sudoers
   entry is a smaller trusted base than custom root code** —
   established, widely audited policy machinery against new
   privileged code written for this pilot. The launcher is
   nevertheless chosen, for one reason: it performs the **whole
   custody sequence** — the fixed spawn, the transitions, the
   gate — as **one constrained program**: a single fixed
   operation, no arguments beyond the validated run identifier,
   no shell, and **no general exec path**. A sudo rule, by
   contrast, confers a general launch path onto **whatever
   programme it names**: the custody sequence would then live in
   that programme, and which interpreter and which code actually
   run under the privilege becomes a property of the named path
   and its own protections — reintroducing the interpreter
   ambiguity the exec condition of point 3 (Rev 07) exists to
   exclude. The cost is named plainly: **custom root code is
   the larger trusted base**, carried knowingly, mitigated by
   the launcher's pinned source, by its behaviour and interface
   frozen at Batch 0 (Rev 12), and by the code-order inspections
   of demonstrations (vii) and (viii) — not by any claim that
   the alternative was wider; a root daemon would add a
   persistent privileged service with an IPC surface. The
   launcher exists for the milliseconds of one spawn and then
   holds no privilege at all — but while it holds it, that
   privilege is root's, filesystem authority included, and is
   acknowledged as such ((ii) above). The standing prohibition is
   unchanged and applies to the launcher too: **nothing in this
   design defends against the machine's operator or root**,
   and no artefact may claim otherwise. (v) **How the
   separation is tested:** demonstrations (v)–(ix) in the
   SE-7 list below — execution refusal as the harness
   identity, allowlist refusal, a mid-run attempt by the
   harness to invoke the launcher, descriptor isolation under
   a deliberately inherited writable descriptor,
   retained-descriptor destination verification,
   group-separation, setuid-precondition, and
   capability-state evidence (Rev 10),
   observed-uid evidence from a test run, and the
   launch-handshake tests: induced parent failures in both
   failure windows (Rev 05) — before the parent's drop takes
   effect, and after it, where the gate's end-of-file, not a
   signal, ends the waiting child — a parent death before
   the child's first instruction, a parent death before
   release, a parent death during the child's setup window,
   and a parent death after release, ended by the backstop
   armed after the child's own drop (Rev 06) and proven
   against the expected parent identity captured before
   the fork (Rev 07), and executable identity continuity —
   a substituted or redirected exec target caught between
   verification and the pre-release re-check (Rev 08;
   scope of the claim corrected, Rev 09) — each proven to
   leave no executing harness.

**Descriptor separation — path permissions are not enough
(Rev 03).** Filesystem permissions govern access by path; they
do **not** revoke access through an already-open file
descriptor inherited across `fork()` and `exec()`. A child
that inherited a writable descriptor to `commitments/` could
write through it whatever the directory's mode says, and the
privilege drop in point 3 does not by itself close that route.
The custody design therefore establishes **descriptor
separation** alongside path separation, in three parts. The
child part is point 3's exhaustive pre-exec close (allowlist:
fds `0`/`1`/`2` at their declared destinations, and the gate
read end for the pre-exec window only). The destination and
verification part (Rev 04) is stated below. The supervisor half is
an invariant of the supervisor's own design, not a hope about
its behaviour: **the supervisor holds no open writable
descriptor to `commitments/` or to `issuance-record.jsonl` at
the moment it invokes the launcher** — commitment-store files
are opened per write, written, and closed, and are never held
open across a launch. The general rule all three parts
instantiate: **the harness child must not inherit any
supervisor-owned writable handle that bypasses the custody
boundary.** It is demonstrated adversarially in SE-7 (vi).

**Declared destinations of the retained descriptors
(Rev 04).** The exhaustive close retains fds `0`/`1`/`2`;
retention is only as good as what those descriptors point
at — a standard descriptor redirected to a protected file
would remain a live route in, past the close of everything
from fd `3` up. The destinations are therefore **declared**,
here: fd `0` is `/dev/null`, or a read-only pipe; fds `1`
and `2` are pipes whose read ends are held by the supervisor
and drained into the run log, or a single designated
append-only log file — opened with `O_APPEND` — in the
supervisor-owned **run-log area**, a tree outside
`commitments/` and outside every other protected store.
**No retained descriptor may be a file inside
`commitments/`, a commitment receipt, or
`issuance-record.jsonl`, and none may be a writable handle
to any of them**, in any mode. Before invoking the launcher,
the supervisor **verifies** what it is about to pass on: for
each of fds `0`/`1`/`2` it resolves the descriptor's
destination (the `/proc/self/fd/` target) and reads its
access mode (`fcntl(F_GETFL)`), and asserts that destination
and mode match this declaration. Where a declared
destination is a pipe, that match must establish the
pipe's **identity** — the descriptor is the actual pipe
end whose other end the supervisor itself holds and
drains, one of the supervisor's own held pipe descriptors
— and not merely that the `/proc/self/fd/` target has the
form `pipe:[...]` (Rev 05; Alex's noted implementation
detail on this accepted material, pb-mweedh0x — a
clarification of how the verification is performed, not a
change to what is verified). On any mismatch — or any
destination it cannot resolve and classify — the launch
**does not happen**: the supervisor aborts the launch and
records the abort (run identifier, offending descriptor,
observed destination and mode) in the run log. The child-side
post-drop state inherits only what passed this check.

**The exec condition, verified at build time and again
before every launch (Rev 07); identity continuity
between verification and execution (Rev 08).** Point 3's three-part
exec condition — the fixed harness executable is **not
setuid, not setgid, and without associated file
capabilities** — applies to the **actual executable the
kernel invokes**: where the fixed harness path is a
script, the executable the kernel runs is its
interpreter, and the condition applies to that
interpreter binary as it stands on the build machine.
At build and freeze time — at the Batch 0 re-freeze, and
at every later point where the executable or its
interpreter is produced, replaced, or pinned — the mode
bits and the capability set of the executable (and of
any such interpreter) are **checked and recorded in the
gate evidence**: the `stat` mode and the `getcap`
output, preserved as read. And the supervisor's
pre-launch verification above **re-checks** them **for
the specific launch**, alongside the descriptor
destinations: before invoking the launcher, the
supervisor stats the executable (and any interpreter)
and asserts that neither the setuid nor the setgid bit
is set and that `getcap` reports no capabilities. A
target failing any of the three conditions means **no
launch**: the supervisor aborts and records the abort in
the run log (run identifier, the failing artefact, and
the observed mode and capability set), exactly as for a
descriptor mismatch. A build whose gate evidence lacks
these recorded checks has not established the condition
the backstop's persistence across the exec depends on.

**Identity continuity — the checked object is the
executed object (Rev 08).** The checks above establish
the executable's and the interpreter's properties **at
inspection time**. The launcher, however, executes a
**fixed path**, and a path is a name, not an object:
between a check and the exec, the object the name
resolves to can change — the file or the interpreter
replaced, a symlink repointed, a writable directory
component redirecting resolution — and the child would
then execute an object whose setuid bit, setgid bit, or
file capabilities no check ever saw. The condition above
is therefore bound to the object actually executed by a
three-layer arrangement. **(1) Protected placement.**
The harness executable and any interpreter it runs
through live under a protected installation tree: the
files themselves, and **every directory component of
their resolved paths**, are owned by **root** and are
**not writable by any other identity** — directories
mode `0755` or stricter, the executables root-owned and
not writable by group or other. What that placement
establishes depends on the identity, and the three
classes are distinguished explicitly (claim corrected,
Rev 09). **The untrusted in-model identities** —
`pilot-harness` and `pilot-supervisor` — cannot modify,
replace, rename, or unlink the executable, the
interpreter, or any path component: OS permissions
genuinely prevent it, and for these identities
substitution is not merely detectable; the write access
it requires does not exist. **The privileged launcher**
is a different class, and no OS-impossibility is claimed
for it: in its privileged window the launcher's
effective identity **is** root, root can write
root-owned files and `0755` directories, and OS
permissions do **not** prevent it. The boundary for the
launcher is its **pinned implementation**: the launcher
is trusted TCB code whose specified operation set is
the spawn sequence only — it contains no operation that
modifies, replaces, renames, unlinks, or redirects the
protected tree, and it performs no file writes while
privileged (point 3) — evidenced the same way its other
code properties are: by the source pin, the specified
operation set, and the SE-7 launcher demonstrations.
That is the same footing on which point 4 states the
launcher's authority in its privileged window: the
ability is acknowledged, and the claim rests on the
code. **The operator and root** acting outside the
launcher stand outside the threat model — the standing
limit of this section's threat-model statement — and
layer (3) below addresses their substitutions only as
detection, and only for substitutions landing before
its re-check.
**The capability state the permission claim stands
on (Rev 10).** Layer (1)'s claim for the untrusted
identities is a claim about the operating system's
permission enforcement, and that enforcement is
**discretionary** access control: it does not bind a
process holding a capability that bypasses it. A
process carrying `CAP_DAC_OVERRIDE`,
`CAP_DAC_READ_SEARCH`, or `CAP_FOWNER` — the
bypass-relevant examples — could modify, replace, or
unlink the protected tree whatever its uid and
whatever the tree's ownership and modes, and layer
(1)'s guarantee would be false of it. The guarantee
is therefore claimed only on a **verified** capability
state, and two standing properties frame the
expectation without substituting for the verification.
The exec target's freedom from file capabilities —
the three-part exec condition, verified above — is
why the harness process cannot **gain** capabilities
at the exec; and the launcher's pinned operation set
contains **no ambient-capability raising** (no
`prctl(PR_CAP_AMBIENT)` call), so nothing in the spawn
sequence lifts a capability into the ambient set an
exec would inherit. Point 3 closes the evidentiary
link: after each privilege drop — the child's to
`pilot-harness`, the parent's to `pilot-supervisor` —
the dropped process reads back its own effective,
permitted, and ambient capability sets; the launch
proceeds only if all three are empty for both
processes, failing closed otherwise; and the observed
masks stand in the gate evidence (demonstration
(vii)). The claim rests on the **observed** state at
the point of reliance, not on the intended uid/gid
transition alone.
**(2) Canonical resolution and identity record.** At
each of the checkpoints above — the freeze, and the
supervisor's pre-launch verification — the executable
and interpreter paths are first resolved **canonically**
(every symlink resolved, in the manner of `realpath`),
and the verification records the resolved object's
**identity** alongside the restriction checks
themselves: the device and inode (`st_dev`, `st_ino`),
the mode bits, and the capability set, for the
executable and for the interpreter alike. At the freeze,
the verification additionally records an **audit of
every path component** of both resolved paths — each
component's owner and mode — evidencing layer (1)
rather than presuming it; a component failing the audit
means the freeze does not record the tree as protected
until the defect is corrected. The identity records are
part of the gate evidence and of the run's pre-launch
record. **(3) Pre-release identity re-check.** The
gate's release (point 3) additionally depends on this:
after the child's setup is complete and before the
parent writes the release byte, the parent
**re-resolves** the fixed paths and **re-stats** the
resolved objects, and the device and inode, the mode
bits, and the capability set must match the verified
identity records **exactly**. Any mismatch is a launch
failure on the established pattern: the parent **does
not write the release byte**; the gate cleanup runs per
the applicable failure window — in the ordinary sequence
the parent has already dropped, so the cleanup is
Window 2's: the gate closed unreleased, the child
exiting on end-of-file, the parent reaping it; **no
issuance** of any kind occurs; and the supervisor
records the abort in the run log with the **observed
identity values** — the same abort-record discipline as
a descriptor-destination mismatch above. What this
establishes, stated plainly — with the detection claim
scoped to what the re-check can actually see (claim
corrected, Rev 09): a substitution landing **at or
before** this re-check — whenever in the launch it was
arranged — is detected by it: the identity comparison
fails, the release is withheld, and the launch fails
closed, instead of the substituted object passing
silently. A substitution landing **after** this
re-check and before the child's `execve`, by an actor
holding write authority over the tree, is **not**
detected by the re-check, and no detection is claimed
for it: that actor stands outside the threat model, and
against them acting inside the re-check-to-exec
interval itself no arrangement at this layer suffices —
the standing limit, restated because it bounds this
layer too. What protects the final interval is
therefore **not** the re-check. It is the absence of an
in-model writer under layer (1) as there stated:
neither untrusted in-model identity holds write access
to the objects or to any component of their paths
during that interval, and the one participant that ever
held root authority in the launch — the launcher — has
in the ordinary sequence already dropped it before this
point, and its pinned code contains no tree-modifying
operation in any case. So within the threat model the
object the re-check verified is the object the exec
runs; the re-check's own role is to bind the verified
identity to the moment of release against everything
that happened **before** it.

**The descriptor route — considered, not adopted
(Rev 08).** A stronger construction exists: the
supervisor could pass pre-verified **open file
descriptors** for the executable and interpreter, and
the child could execute through them (`execveat` with
`AT_EMPTY_PATH`), eliminating the
verification-to-execution interval by construction —
there is no path left to redirect. It is **not** the
baseline. The harness's invocation is
interpreter-mediated, and the descriptor form for an
interpreter-and-script pair — the interpreter executed
from a descriptor, the script itself delivered to it
without a path the interpreter re-opens, the pair's
identities both pinned — is substantially more
intricate than the single-binary case, and intricacy in
the launcher is its own custody risk. The
protection-plus-identity arrangement above is the
specified mechanism; this paragraph records the
alternative and the judgement, so an inspector may
strike the judgement with full knowledge of what it
trades — but it leaves no choice open to the builder:
layers (1)–(3) are normative.

**The gate read end, reconciled (Rev 04).** The launch gate
(point 3) adds one descriptor to the child's pre-exec
allowlist, and its presence is reconciled with the
declarations above explicitly: the gate read end is a
**read-only** descriptor to a pipe whose write end the parent
holds; it is **not a writable handle to any protected
artefact** — the child cannot write through it at all, and
reading it yields at most the single release byte; it is
created `O_CLOEXEC` and therefore **closed by the exec
itself**, so it does not exist in the harness; and it never
appears in the retained set the destination verification
covers, because it is created by the launcher after the
supervisor's pre-launch check and is gone before the harness
exists. No other descriptor joins the allowlist.

5. **Issuance — START.** When the supervisor observes the
   `RUN_STARTED` event flushed in the record file, it parses
   that event itself, recomputes the genesis hash
   (`prev_event_sha256` preimage: the pinned-input manifest
   block) and the pin-block hash from the file's own bytes, and
   writes the START receipt — `{run_id, kind: "START",
   issued_at_utc, genesis_sha256, run_started_event_sha256,
   pinned_input_block_sha256}` (Harness §2.6) — then appends its
   issuance entry (below).
6. **Issuance — TERMINAL.** When the supervisor observes the
   run's terminal event (`RUN_CLOSED` or `RUN_STOPPED`) flushed
   and the record file closed, it computes `record_file_sha256`
   over the file's **exact bytes as closed**, counts the events
   by its own parse, takes the final event's `event_sha256` from
   its own parse, and writes the TERMINAL receipt
   (`{run_id, kind: "TERMINAL", issued_at_utc,
   terminal_event_type, final_event_sha256, event_count,
   record_file_sha256}`).
7. **Issuance — CRASH.** When the supervisor observes the child
   harness process terminate **without** a terminal event having
   been flushed, it writes **no** TERMINAL receipt and instead
   issues the CRASH receipt over the partial file **exactly as
   it lies** at observation: `{run_id, kind: "CRASH",
   issued_at_utc, record_file_sha256, event_count,
   final_event_sha256, termination_observed}` — the file hash
   over the exact bytes including any incomplete trailing bytes,
   the count of **complete** events from its own parse, the last
   complete event's hash, and its own record of the termination
   (when, and on what basis: the child's exit as witnessed by
   its parent). TERMINAL and CRASH never coexist for one run;
   a run presented with both is a custody finding. No receipt of
   any kind is ever back-filled, edited, or re-issued: a
   correction is a new artefact about the run, never an edit
   (Criteria §7.2(6)).
8. **The issuance record.** Alongside the receipts, in the same
   supervisor-owned tree, the supervisor keeps its append-only
   **issuance record** (`issuance-record.jsonl`): one entry per
   issuance, written by the supervisor at the moment of
   issuance — `{run_id, kind, issued_at_utc, receipt_sha256}`.
   It is written by the supervisor only; the harness has no
   write path to it (same ownership and permissions as the
   receipts), and no agent, tool, or seat may write it (Ben's
   index rule; Harness §2.6). It is not an index: it is the
   supervisor's own account of its own acts, and it enumerates
   nothing outside the commitments it issued.
9. **Examiner verification.** The examiner (§3.7) verifies every
   receipt relied on **against the issuance record** (Harness
   §7 step 0): a receipt with no corresponding entry, or whose
   hash differs from its entry, is not evidence — it is a
   custody finding. Replay begins at the anchor, always.

**Threat model, stated honestly.** This custody design defends
the anchor against the harness — and against any agent, tool,
seat, or subject acting through the harness's privilege
boundary. It does not defend against the machine's operator or
root account, who stand outside the pilot's threat model (§2.6
frames the defect as "anyone with write access to the whole
record file"; the anchor's purpose is that the *harness* cannot
rewrite evidence and anchor together). A deployment claiming
operator-level adversaries would need a stronger form (e.g.
receipts countersigned to storage the operator cannot alter);
that claim is **not** made here and must not be made for this
build.

**How SE-7's four proof obligations are demonstrated** (Harness
§4.5 SE-7; §5 gate G3):

- **(i) The harness cannot write, replace, or delete receipts.**
  By inspection: no code path in the built harness references
  `commitments/` for writing. By adversarial test, executed **as
  the `pilot-harness` identity** from inside the harness's own
  privilege boundary: attempts to create a file in
  `commitments/`, to overwrite a receipt, to delete a receipt,
  and to append to the issuance record must **all fail at the OS
  boundary** (permission denied), and the failures are preserved
  as test evidence. A test that only shows harness code
  *declining* to write does not satisfy this obligation — the
  inability must be the OS's, not the code's politeness.
- **(ii) The supervisor independently records START, TERMINAL,
  and CRASH.** By inspection of the supervisor program: every
  committed value is computed by the supervisor from its own
  read of the record file; no issuance path accepts a hash,
  count, or event value from the harness. By test: a harness
  build variant (scratch context) that writes a falsified
  `RUN_STARTED` pin block produces a START receipt over the
  falsified block's actual bytes — the supervisor commits what
  the file says, never what the harness claims — and the
  discrepancy is then a replay finding, exactly as designed.
- **(iii) The separation is demonstrated, including the crash
  case.** The interrupted-write crash test (§5 gate G2) is the
  demonstration: harness killed mid-append → CRASH receipt over
  the partial file as it lies → no TERMINAL receipt → issuance
  entry present. Plus the between-steps crash case (kill at a
  step boundary) for completeness of the same obligation.
- **(iv) The examiner verifies the issuance record.** The replay
  implementation (§3.7) performs issuance-record verification as
  step 0 by construction; the gate evidence includes a negative
  test: a receipt file planted in `commitments/` without an
  issuance entry (planted under the operator's authority, in a
  scratch commitments tree) must be rejected by the examiner
  tooling as a custody finding, not accepted as an anchor.
- **(v) The launcher separation (Rev 02).** By adversarial
  test: the launcher invoked **as the `pilot-harness`
  identity** fails — it is not executable by that identity
  (permission denied at the OS boundary); the launcher invoked
  by `pilot-supervisor` with **any non-allowlist programme or
  argument shape** refuses and spawns nothing; a harness
  process, **mid-run**, attempting to invoke the launcher to
  spawn a second process fails at the OS boundary, and the
  run's own evidence shows the attempt changed nothing. (The
  commitment forgery, replacement, and deletion attempts as
  `pilot-harness` remain obligation (i)'s tests.) By
  observation evidence: a test run's preserved artefacts
  include the supervisor's own record of the harness child's
  uid/gid as observed from the OS (the child's `/proc` status,
  read by the post-drop parent) — the child ran as
  `pilot-harness`; the witnessing parent ran as
  `pilot-supervisor`.
- **(vi) Descriptor isolation (Rev 03; destinations
  Rev 04).** By adversarial scratch test: the launching
  process deliberately holds an open **writable** descriptor
  to a scratch commitments-like file at fork time — the
  hazard, arranged on purpose. After the launch, the
  harness-identity child attempts to write through **every**
  inherited descriptor number it can probe. The test passes
  only if no inherited descriptor is usable for writing — the
  allowlisted `0`/`1`/`2` excepted, in their declared
  standard roles only — **and** the scratch file is
  byte-unchanged. This instantiates the general rule of
  §3.5's descriptor-separation block: the child must not
  inherit any supervisor-owned writable handle that bypasses
  the boundary. A test in which the hazard was never actually
  arranged does not satisfy this obligation.
  **Retained-descriptor verification (Rev 04):** the same
  test run also records, from inside the child, the resolved
  destinations (`/proc/self/fd/` targets) and access modes of
  the retained fds `0`/`1`/`2`, and asserts each matches
  §3.5's declared set — and the **negative arrangement**:
  standard output deliberately pointed at a scratch protected
  file before launch, which the supervisor-side pre-launch
  verification must catch; the launch is refused, no harness
  process exists, and the abort is recorded with the
  offending descriptor and its observed destination and mode.
  A test that verifies only the close of descriptors `3` and
  above does not satisfy this obligation.
- **(vii) Group separation and setuid preconditions
  (Rev 03); capability state of the dropped processes
  (Rev 10).** By operating-system evidence: the group
  membership of both accounts is read from the OS (`id` /
  `getgrouplist`, or `/etc/group`) and preserved in the gate
  evidence — `pilot-harness` must not appear in the
  `pilot-supervisor` group, and `pilot-supervisor` must not
  appear in any group conferring `pilot-harness` privilege.
  If the separation does not hold, the custody evidence
  **fails**: the launcher's group-execute control would not
  limit invocation to the intended identity. By probe:
  before the custody design is relied on, a probe invocation
  of the launcher on the build host (supported OS: Linux)
  must observe effective uid `0` inside the privileged
  window, and the checks for the conditions that silently
  defeat setuid — the launcher's filesystem mounted `nosuid`,
  an inherited `no_new_privs` flag — are recorded with it.
  **If the probe or any check fails, the build stops; there
  is no fallback to a weaker launch arrangement.**
  **Capability state of the dropped processes
  (Rev 10).** The gate evidence for the launcher tests
  must also include the **observed capability state of
  both dropped processes**: the `CapEff`, `CapPrm`, and
  `CapAmb` values recorded by point 3's read-backs for
  the child running as `pilot-harness` and for the
  parent running as `pilot-supervisor` — and **each of
  the six values must be zero**. Layer (1)'s permission
  guarantee is evidenced by this observed state, not
  inferred from the uid/gid transitions the read-backs
  accompany. **The fail-closed case:** a capability
  read-back is made to return a **nonzero** observation
  — induced through the test build's fault-injection
  hook feeding a synthetic nonzero mask to the check
  (the hook of demonstration (viii), extended in the
  test build to interpose on the capability read-back;
  the production launcher contains no such feed) —
  exercised **once against the child-side check and
  once against the parent-side check**. The child-side
  case must show the launch aborting at the check: the
  child `_exit()`s, the harness never executes, and no
  issuance occurs. The parent-side case must show
  Window 2's outcome end to end: **no release byte** is
  written, the gate is closed unreleased, the child is
  reaped, **no issuance** occurs, and the abort is
  recorded with the synthetic masks as the observed
  values. Where a test build cannot interpose the
  synthetic observation on one side's read-back, that
  side's case is met by **code-order inspection** — the
  check's presence in the pinned sequence, its
  all-three-sets-empty requirement, and its fail-closed
  branch, read against the pinned launcher source —
  and the gate evidence must state which of the two
  proofs was used for **each** side. Omitting a side
  satisfies neither route.
- **(viii) The launch handshake (Rev 04; failure cleanup
  Rev 05).** By fault injection, through the launcher's test
  hook — a test-only build feature, present only in the test
  build of the launcher and **compiled out of the production
  launcher** — which forces the parent's privilege
  transition to fail after the fork, in **each of the two
  failure windows** of §3.5 point 3: **Window 1**, the
  failure surfacing before the parent's drop has taken
  effect (an induced `setres*()` failure; the parent still
  privileged, and its direct `SIGKILL` available); and
  **Window 2**, the failure surfacing **after** the drop — a
  verification mismatch induced to surface only once the
  parent's effective root is gone, so the parent cannot
  signal across the uid boundary and the cleanup runs
  through the gate: the parent closes the gate write end
  unreleased, the waiting child observes end-of-file and
  `_exit()`s, and the parent reaps it. A test that exercises
  only Window 1 proves only the easy case and does not
  satisfy this obligation. In **every** induced case the
  test proves the fail-closed outcome end to end: the
  harness **never executes** (no harness process persists;
  no run artefacts appear); **no child process survives**;
  the child is **reaped by the parent**; and **no START
  commitment and no issuance entry exists** for the aborted
  launch — the supervisor's trees contain nothing for it but
  the recorded abort. The **parent-death variant**: the
  parent is killed after the fork but before releasing the
  gate; the child exits without executing the harness — by
  end-of-file on the gate or by its `PR_SET_PDEATHSIG`
  backstop (§3.5 point 3) — leaving no harness process, and
  the child's termination, kernel-signalled or gate-exited,
  is observable in the test's recorded evidence even though
  no parent survives to reap it. A test in which the parent
  failure is simulated only in the supervisor's bookkeeping
  — the child's gate never actually exercised — does not
  satisfy this obligation.
  **Post-release parent death (Rev 06) — a required case,
  distinct from the variant above:** a full launch completes
  — the child's credentials dropped and verified, the
  backstop armed **after** the drop, the gate released, the
  harness (the stub, in the test build) **running** — and
  the parent is then killed; the recorded evidence must show
  the running child terminated by the backstop's `SIGKILL`.
  The pre-release variant exercises a child that has not yet
  exec'd; it cannot by itself prove the arming persisted
  past the child's `setresgid()`/`setresuid()` transitions
  and the exec — and Rev 05's placement, arming before those
  transitions, would silently have failed here. This case,
  and only this case, is the proof the backstop survives
  the credential transition.
  **Install-window parent death (Rev 06; sequence
  corrected, Rev 07):** the parent is
  killed during the child's setup window — after the fork,
  before the child's arming completes — and the evidence
  must show the child exiting at its parent-relationship
  re-check (`getppid()` no longer returning the **expected
  parent identity captured before the fork**) **without
  executing the harness**.
  Where the test build can hold the child inside the setup
  window (a test-only hold at that point, compiled out of
  the production launcher like the failure hook above), the
  case is induced directly. Where a test build cannot
  induce that timing deterministically, this part of the
  obligation is met by **code-order inspection** — the
  pinned child sequence (**pre-fork capture of the
  expected parent identity by the parent; the child's
  first comparison of `getppid()` against the inherited
  expected value; transitions; verification; the
  capability read-back; arming, with its return-value
  check; the `PR_GET_PDEATHSIG`
  read-back; the re-check against the same expected value;
  close; gate**) read against
  the pinned launcher source — and the gate evidence must
  state which of the two proofs was used. An inspection of
  any shorter sequence proves the wrong sequence (Rev 07).
  Omitting the case
  satisfies neither route.
  **Pre-first-instruction parent death (Rev 07):** the
  parent is killed in the interval between the fork and
  the child's first comparison, so the child has already
  been reparented when it first runs; the evidence must
  show the child exiting at that first comparison — its
  `getppid()` differing from the inherited expected parent
  identity — **without proceeding** to the transitions,
  the arming, or the gate, and without executing the
  harness. Where the test build can induce that timing (a
  test-only hold interposed between the fork and the
  child's first instruction, compiled out of the
  production launcher like the other hooks), the case is
  induced directly; where it cannot be induced
  deterministically, the code-order-inspection route above
  covers it — that inspection now reads the corrected
  sequence — and the gate evidence must state which of
  the two proofs was used. Omitting the case satisfies
  neither route.
- **(ix) Executable identity continuity (Rev 08).** By
  adversarial test of the arrangement in §3.5's
  verification block, in a scratch installation tree.
  **(a) Substitution:** the test harness, acting under
  the operator's authority — an out-of-model writer —
  replaces the executable with a scratch copy carrying a
  **setuid bit**, after the freeze-time verification has
  recorded the genuine object's identity. The
  substitution is arranged before any launch, so the
  supervisor's **pre-launch verification** is the
  checkpoint expected to fire first: the resolved
  object's identity — device, inode, mode, capability
  set — no longer matches the freeze record, the launch
  is refused, no harness process exists, and the abort is
  recorded with **both** identity records, the freeze's
  and the observed. The case is also satisfied if the
  parent's **pre-release re-check** is the checkpoint
  that fires, provided the substituted object is never
  executed and the abort is recorded the same way.
  **(b) Redirection:** a symlink component in the
  scratch executable's path is repointed to a scratch
  target **after** the supervisor's pre-launch
  verification has passed against the genuine object, so
  the parent's **pre-release re-check** is the checkpoint
  expected to fire first: canonical re-resolution lands
  on the substituted object, the identity comparison
  fails, **no release byte is written**, the gate cleanup
  runs (Window 2's pattern — gate closed unreleased,
  child exiting on end-of-file, parent reaping), no
  issuance occurs, and the abort is recorded with both
  identity records. Either checkpoint firing satisfies
  the case, provided the substituted object is never
  executed. **(c) The path-component audit, evidenced:**
  one directory component of a scratch tree's resolved
  path is deliberately made **group-writable** (a second
  arrangement: owned by a non-root identity); the
  freeze-time audit must **flag** the component — its
  owner and mode recorded against the protected-placement
  requirement — and the tree's identity record must not
  be established as verified until the defect is
  corrected. A freeze that records identities without
  auditing the components does not satisfy this part. A
  test in which the substitution or the repointing was
  never actually arranged does not satisfy this
  obligation. **Scope of what (ix) demonstrates.** These
  cases demonstrate detection of a substitution arranged
  before launch and of a redirection arranged after
  pre-launch verification but before the parent's
  pre-release re-check — the two checkpoints firing on
  changes that land before the re-check. They do **not**
  demonstrate detection of a substitution landing
  **after** the pre-release re-check, and nothing in
  this demonstration claims it: that case stands outside
  the threat model, under layer (3)'s statement as
  corrected (Rev 09).

### 3.6 Adapter (Adapter §§1–5)

Build the adapter to the Stage 2 specification exactly:

- **Single operation.** `complete(step_inputs) ->
  {capture_record_id, raw_output}` (Adapter §5) — nothing else
  is accepted: no parameters, no options, no overrides.
  `capture_record_id` is returned in **all** outcomes; failure
  is data in the record, not an exception across the boundary.
  `raw_output` is `choices[0].message.content` of the final
  attempt, verbatim (reasoning content and final answer as one
  preserved artefact — never split, stripped, or re-presented),
  or `null` when no usable response exists.
- **The adapter never** executes or knows of tools; writes the
  ledger or any execution-record entry (capture records only);
  interprets, scores, summarises, or repairs a response; modifies
  `messages`; adds any content of its own — no adapter system
  prompt, prefix, suffix, reformatting, or trimming (Adapter
  §§2.3, 5).
- **Pinned identity** (Adapter §1.2): `model` is
  `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`, exactly, and
  must equal the helper's MODEL argument on every call.
  Alternates (Adapter §1.2) are declared, never automatic: no
  code path in the adapter or harness selects an alternate at
  run time; moving to one is a re-pin by amendment.
- **Catalogue pin and pre-flight re-check** (Adapter §1.4): the
  pin is the pair *(model id, catalogue snapshot sha256 +
  capture date)*. The catalogue evidence at the Batch 0 freeze is the
  **design-time snapshot, carried into the freeze** and pinned
  by its hash (Rev 12; §6.3 item 5); the full `GET /v1/models`
  response is captured and hashed **at Stage 6 pre-flight**,
  against the live host, before any run. If the pinned id is **absent** from the pre-flight
  catalogue, **the run does not start** — no substitution, no
  improvisation; re-pin by amendment (new catalogue evidence,
  Alex notified) before any execution. If the id is present but
  the first call returns 404, or a response reports a different
  served model id, that is an ADAPTER_FAILURE and execution
  halts (§3.6, failure classification). (Batch 0 takes **no listing call at all** — Stage 5 makes
  no provider contact of any kind (Rev 12; §3.7; §6.3 item 5).)
- **Pinned envelope** (Adapter §2.3) — the adapter adds only
  these fields, from pinned configuration, never varied per
  call:

  | Field | Pinned value |
  |---|---|
  | `model` | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` |
  | `temperature` | `0.6` |
  | `top_p` | `0.95` |
  | `max_tokens` | `20480` |
  | `stream` | `false` |
  | `chat_template_kwargs` | `{"enable_thinking": true, "reasoning_budget": 16384}` at the body root |

  The request body is sent byte-for-byte as constructed; its
  sha256 is `request_sha256`; a retry resends the identical
  bytes. Configuration is hashed (`adapter_config_sha256`);
  changing it is a design amendment producing a new hash. The
  frozen configuration's **values** are checked mechanically at
  calibration (Criteria §5.1(6)): a frozen configuration
  deviating on any of temperature / top_p / reasoning_budget /
  max_tokens — a silent return to temperature 0 is the named
  case — is a freeze defect.
- **Capture — schema `ADAPTER-CAPTURE-02`** (Adapter §3): every
  call, successful, failed, or retried, produces exactly one
  30-field capture record, written before the adapter returns.
  One JSON file per capture (`captures/<capture_id>.json`),
  written once, never edited; the adapter keeps **no index** of
  its own. Top-level request/response fields describe the final
  attempt; **every attempt** is preserved in `attempts[]` with
  its `response_body_raw` verbatim and `response_body_sha256`
  — including the error body of a 429 or 5xx that triggered a
  retry; `null` only when no body was received. A success after
  a retry is recorded as a success **with** the retry and the
  failed attempt's body visible; retries are never silent.
- **Helper wrapper (normative build requirement, Adapter
  §3.2).** The sanctioned helper raises on HTTP error, surfacing
  status and body as an exception. The build must therefore wrap
  the helper invocation (or implement the identical call through
  the same credential mechanism) so that **every** attempt's
  status, raw body, timing, and exception detail are capturable.
  A build in which any attempt can end without its available
  body and hash in `attempts` fails this specification; the
  Batch 5 checkpoint tests it with forced 429/500 sequences
  against the transport double (§3.7).
- **Never captured** (Adapter §3.4): headers are not part of the
  record — the `Authorization` header above all. The credential
  transits only inside the connector's surrogate mechanism; the
  adapter never sees, holds, or records the key or any fragment
  of it. `request_raw` is the request **body** only. Any failure
  detail or error body that would quote a header is redacted
  before writing; the Batch 5 checkpoint includes a redaction
  test.
- **Failure taxonomy** (Adapter §4): ADAPTER_FAILURE is
  determined by the adapter at capture time and by no one else —
  404 not-served; 401/403; a 400 rejecting the pinned envelope;
  429/5xx exhausted after the declared retries; timeout (120 s
  per attempt); transport failure; helper error; served model
  id ≠ pinned id; pinned id absent at pre-flight (recorded as a
  pre-flight failure, no call made). SUBJECT_FAILURE and
  GOVERNANCE_FAILURE are determined downstream, from the capture
  record, never by the adapter.
- **The pre-classified 400 (Adapter §§1.3(e), 4.2).** Hosted
  acceptance of `chat_template_kwargs` for this model is
  UNSETTLED. An HTTP 400 whose preserved body identifies that
  field as the rejected parameter is **an ADAPTER_FAILURE,
  never a subject failure**, is never retried, halts the
  affected tree under the adapter-failure rule, and its remedy
  is a configuration amendment decided by Ben/Alex against the
  capture — never an in-run envelope change.
- **Retry rule** (Adapter §4.3): maximum **2 attempts** (original
  + one retry); retryable classes only — HTTP 429, HTTP 5xx,
  timeout, connection error; never any other 4xx, never a
  received-and-captured response; fixed **5 s** delay;
  byte-identical resend (`request_sha256` invariant across
  attempts). The policy is part of the pinned configuration.
- **Served status.** The pin is carried as **PINNED-LISTED,
  SERVED-UNVERIFIED** through Stage 5 and into Stage 6 (Adapter
  §1.3(f)). Nothing in the build asserts, implies, or tests its
  way into a served claim: Stage 5 makes **no subject call at
  all** (§3.7), and served status is established only by the
  first authorised Stage 6 call, under the Adapter §1.4
  procedure if it fails.

### 3.7 Examiner tooling, stub subject, and transport double

- **Examiner (Harness §7; Criteria §§2, 8).** Build the replay
  procedure as a runnable artefact that re-derives outcomes
  **from the preserved record and pinned rules alone**: step 0
  anchor verification (START/TERMINAL/CRASH against recomputed
  hashes, every receipt checked against the supervisor's
  issuance record); chain integrity; input identity;
  deterministic re-execution of every [TOOL]/[RULE] step and
  [CHECK] phase byte-for-byte against the recorded payloads
  (extractions re-executed under the four-outcome semantics — an
  outcome mismatch in any pairing is a divergence); the insert
  audit with the **registry reconstructed from the event
  sequence**, never read from the build's own state; subject
  outputs taken as preserved artefacts from `response_raw`,
  **never re-sampled**. The examiner does not accept the
  operator's scoring worksheet as truth: it re-derives each
  verdict and confirms or overturns the worksheet, verdict by
  verdict (Criteria §2, divergence rule). Governance
  re-derivation is exact; why the hosted model produced its
  output is not re-derivable and is not claimed (Harness §7).
- **Stub subject (spec decision, flagged).** The sources require
  Stage 5 verification without a model call (Plan Stage 5;
  Criteria §5.1 stubs [MODEL] steps for calibration) but do not
  name the stub's form. This spec fixes it: a **scripted stub
  subject** behind the adapter's harness-facing boundary — a
  deterministic test double implementing the `complete()`
  contract's harness side, returning declared outputs per
  (tree, step) from a pinned stub script, including scripted
  cases the verification needs (a well-formed output; a
  malformed output; a refusal-shaped output; a truncation-shaped
  output) so [MODEL]-step handling, [CHECK] phases, and failure
  branches are exercised end-to-end with no live call. The stub
  is test scaffolding **outside the run path**: it is selected
  by pinned test configuration in scratch contexts only, and no
  scored run can be configured to use it (the run's
  `RUN_STARTED` block pins the adapter configuration; a stub
  configuration is a different, visibly named configuration used
  only in scratch runs, whose records are labelled as such and
  are never offered as run evidence).
- **Synthetic captures — the stub run satisfies the capture
  contract (Rev 02, Alex's condition on §6.3 item 2).** A
  stubbed [MODEL] step must not return scripted text *around*
  the evidence machinery: the stub responder sits behind the
  adapter so that `complete()` runs the adapter's full capture
  path, and the Batch 6 stub full-battery run produces genuine
  `ADAPTER-CAPTURE-02` records — one per [MODEL] step, linked
  from the record by `MODEL_CALL_LINKED`, with `record_sha256`,
  `request_sha256`, and `response_sha256` recomputing — and
  **every entry in `attempts[]` carrying its preserved
  `response_body_raw` with a recomputing
  `response_body_sha256`** wherever that attempt received a
  body, satisfying Criteria §1.1(6) exactly as a live run must.
  Where a verification case needs a retried call, the stub
  scripts an attempt sequence — a failed attempt with its own
  preserved body, then the success — so the failed attempt's
  body is present in `attempts[]`, never summarised away. Every
  synthetic capture is **explicitly labelled**: the capture's
  subject identity is the stub's visibly named configuration,
  never the pinned model id; the run's `RUN_STARTED` block pins
  the stub configuration as such; and the examiner verifies the
  label as part of re-deriving the stub run — a synthetic
  capture that could be mistaken for a served-model capture
  fails this section. The doubles' boundary is unchanged and
  **neither substitutes for the other**: the **transport
  double** exercises the real adapter's HTTP handling —
  retries, error-body capture, redaction — against scripted
  wire sequences; the **stub subject** exercises the harness's
  step, linkage, and capture machinery end-to-end. Batch 5's
  transport-double checkpoints and Batch 6's stub full-battery
  run are separate evidences for separate boundaries.
- **Transport double (spec decision, flagged).** Adapter
  behaviour that only appears on the wire — per-attempt capture
  of error bodies, retry timing, the pre-classified 400 — is
  verified against a **local scripted HTTP double** (a loopback
  test endpoint replaying declared status/body sequences:
  200-with-body, 429-then-200, 500-then-200, 400 rejecting
  `chat_template_kwargs`, timeout), never against the live
  endpoint. The adapter under test is the real adapter; only
  the endpoint is doubled, and the double's identity is recorded
  in every test artefact it touches. Stage 5 makes **no contact
  with the provider host** — no chat completion, no listing, no
  probe — **except a LANE-CRUSHER evidence retrieval under a
  prior, per-operation authorisation recorded by Ben under
  §0.3** (§0A.7). LANE-ADAPTER contact has no Stage 5 exception
  of any kind; the adapter's first contact is Stage 6's.
- **No provider contact — enforced, not merely stated (Rev 12,
  Claude's finding 1; isolation boundary total, Rev 13).** A rule the build can break silently is
  a statement, not an enforcement, so Stage 5 carries three.
  **(a) Loopback refusal:** in Stage 5 mode the adapter
  **refuses any non-loopback base URL** — a configuration
  naming a non-loopback provider address **fails closed at
  start-up, before any run**; the transport double's loopback
  endpoint is the only address a Stage 5 adapter can be
  configured to reach. **No proxy path (Rev 13):** in
  Stage 5 mode the adapter **does not use proxy
  configuration or any other forwarding mechanism** to
  reach an external service — proxy settings, however
  supplied, by environment or by configuration, are
  **not honoured** in Stage 5 mode, so no indirect route
  through a local proxy or forwarding service is open
  to it. **(b) No credential in the build
  environment:** the build environment holds **no provider
  credential** — credentials remain in the connector's custody,
  outside the build environment — so the build has nothing to
  authenticate with even if it is misconfigured. **(c)
  Zero-egress evidence:** the build and gate environment has
  **no non-loopback network egress at all** (Rev 13) —
  loopback interfaces only: not merely no route to the
  provider host, and no indirect route through a proxy or
  a connector either. Gate **G1 records the zero-egress
  check and its result** (§5), on evidence showing the
  **actual environment's** isolation — its interfaces
  inspected (for example, a network namespace with no
  external route), no external route present, and **no
  available external proxy or connector path**. An
  environment in which non-loopback egress cannot be
  shown absent — or whose evidence addresses only direct
  routes — does not pass G1. **Nemotron is not called
  in Stage 5, and nothing else at the provider host is
  contacted either**: enforcement, not wording, is what makes
  that a fact about the build rather than about its
  intentions.

---

## 4. BUILD ORDER — BATCHES WITH VERIFICATION CHECKPOINTS

The build proceeds in batches. **Each batch's checkpoint must
pass before the next batch begins**; a failed checkpoint returns
the batch to build, and the failure and its remedy are recorded.
No batch may reach forward into a later batch's components to
make its own checkpoint pass. All verification in every batch
runs offline or against the §3.7 doubles — **no subject call
occurs in any batch**.

**Batch 0 — Re-freeze and freeze checks.**
Take PILOT-CORPUS-SNAPSHOT-01 by read-only copy from the Stage 0
corpus files; verify each section's recorded hash and both
files' Stage 0 pins (`b107e892…`, `c93eaa19…`) equal at copy
time. Freeze the adapter configuration (identity pin §3.6;
envelope values §3.6; retry policy) and carry the
**design-time catalogue snapshot** into the freeze as the
Batch 0 catalogue evidence (Adapter §1.4; §6.3 item 5) —
**no live listing is taken in Stage 5** (Rev 12). Issue the **dated
Stage 5 re-freeze amendment to PILOT-MANIFEST-01** pinning what
exists at the freeze: the corpus snapshot,
INTERPRETATION-NOTE-01, the canonicalisation contract
(RFC 8785, §3.4), the adapter configuration and its
`adapter_config_sha256`, PILOT-TOOLS-01's specification inputs,
and this specification. Artefacts the build itself creates —
EXTRACTOR-RULES-02 and the pilot data files (Batch 1),
PILOT-TOOLS-01 (Batch 2) — are pinned by **dated additions to
the same amendment at their batch checkpoints**, before any
later batch or any run depends on them; the amendment is the
Stage 0 freeze's continuation, never its rewrite (Harness
§4.4).
**Launcher behaviour-and-interface freeze (Rev 12, Claude's
finding 5).** Batch 0 also freezes the **launcher's required
behaviour and interface** (§3.5 point 2): its operation set
(the single fixed spawn), its invocation contract (the
compiled-in harness path and argument-vector shape; the
validated run identifier), the **gate protocol** it must
implement (point 3's sequence obligations — the transitions
and their read-backs, the capability verification, the
arming, the descriptor close, the gate), and the identity
obligations it must satisfy. The freeze is pinned in the
re-freeze amendment with the other freeze artefacts, so the
custody target exists **before** Batches 1–3 build on the
custody assumption; Batch 4 **implements against the frozen
interface** and pins the resulting source at its checkpoint,
as §3.5 point 2 provides. Freezing the interface changes
nothing about the launcher's specified behaviour — only
**when** its target is fixed.
**Custody setup evidence (Rev 12, Claude's gap).** The
creation of the two OS accounts, the group memberships
(§3.5 point 1), and the launcher's ownership and mode is
**operator work**, and it is preserved as a freeze artefact
of this batch: the **setup script**, or a **recorded
transcript** of the manual steps where no script is used.
SE-7 demonstration (vii) reads the resulting state from the
operating system; this artefact evidences **how the state
came to be**, so the custody identities' creation is on the
record, not only their later state.
**Launcher environment probe — owner and evidence (Rev 12,
Claude's gap).** The setuid-viability probe of §3.5 point 2 —
effective uid `0` observed inside the privileged window, the
`nosuid` mount condition and any inherited `no_new_privs`
flag checked — is **run by the operator** at this batch, and
its output is **preserved in the Batch 0 freeze evidence**. A
failed probe stops the build, as §3.5 point 2 already rules;
this names who runs it and where its output goes.
*Checkpoint:* every Stage 0 pin recomputes; snapshot equality to
the Stage 0 corpus pins is recorded; any corpus pin mismatch
**stops the build here** and is reported (§2.3).

**Batch 1 — Corpus interface and pilot data.**
Implement `CorpusSource` over the snapshot + pilot-manifest data
(§3.2); transcribe and verify the four pilot data files against
the pinned `run_ab.py` constants, value by value; finalise
EXTRACTOR-RULES-02 covering every field the trees name.
*Checkpoint:* interface contract tests pass (section resolution,
`pilot-manifest:` resolution, NOT FOUND behaviour); data-file
transcription verification is complete and recorded; the rules
data reproduces the four V2 fields' behaviour on the pinned
sections (Qualification §4 precedent) and produces AMBIGUOUS on
a synthetic two-match section and TYPE FAILURE on a synthetic
type-defeating section (Criteria §5.1(5)'s synthetic exercises,
run early).

**Batch 2 — PILOT-TOOLS-01 and the registry.**
Implement the five tools on the Batch 1 interfaces, the issuance
registry with the five properties (§3.3), `reference_insert`
with recomputation, consumption, and refusal behaviour, and the
logging contract.
*Checkpoint:* the four-outcome semantics verified against the
rules data on production sections and synthetics; refusal
mechanics verified at unit level (forged id → refusal; FOUND id
→ refusal; second consumption → refusal); every invocation,
including refusals, appears in a scratch record with its event
pair. (The formal sabotage battery is gate G1, §5; this
checkpoint is its smoke run, and the formal battery runs on the
completed tools before Batch 3 closes — its record is preserved
either way.)

**Batch 3 — Record and driver.**
Implement the record writer (`PILOT-RUN-RECORD-01`, §3.4), the
hash chain, `ledger.json` materialisation, and the driver (§3.1)
with budgets and stops.
*Checkpoint:* a scratch run against the **stub subject** (§3.7)
executes a declared subset of trees end-to-end and produces a
complete record; the chain verifies; the materialised ledger
reproduces identically on re-extraction; stop finality and the
budget stops are demonstrated in scratch contexts (a run stopped
mid-tree leaves the §6.4 partial-record shape).

**Batch 4 — Supervisor and commitments.**
Implement the supervisor of §3.5 (two OS identities, launcher,
self-computed issuance, issuance record) and the `commitments/`
store. The launcher is built **against the
behaviour-and-interface freeze of Batch 0** (Rev 12, Claude's
finding 5); its source is pinned by dated addition at this
checkpoint, as §3.5 point 2 provides.
*Checkpoint:* SE-7's demonstrations (i), (ii), (iv), and the
launcher tests of (v)–(ix) run as specified in §3.5 — OS-boundary
refusal tests executed as the `pilot-harness` identity,
including the launcher's refusal of the harness identity and
of non-allowlist invocations; supervisor self-computation
verified against a falsified pin block in a scratch run; the
planted-receipt negative test rejected by a prototype anchor
check. The
crash cases (between-steps kill; the interrupted-write test) run
formally at gate G2 on the assembled package.

**Batch 5 — Adapter.**
Implement the adapter (§3.6) including the helper wrapper, the
capture writer, redaction, the failure taxonomy, and the retry
policy.
*Checkpoint:* against the **transport double** (§3.7) only —
forced 429-then-200 and 500-then-200 sequences captured with
every attempt's body and hash present and the resend
byte-identical; a forced 400 rejecting `chat_template_kwargs`
classified ADAPTER_FAILURE and not retried; a timeout sequence
classified and captured; **redaction test**: no capture field in
any test artefact contains header or credential material; the
envelope as sent equals the pinned configuration byte-for-byte
in every test capture (`request_envelope` vs
`adapter_config_sha256` preimage).

**Batch 6 — Examiner, calibration, and full verification.**
Implement the examiner tooling (§3.7); run the **calibration
pass** (Criteria §5) producing PILOT-CALIBRATION-01 — every
[TOOL]/[RULE] step of all 13 instances executed offline against
the pinned snapshot, rules, and data, [MODEL] steps stubbed as
not exercised, all six §5.1 items recorded, each instance
certified ANSWERABLE or named UNANSWERABLE with its cause; run
a **stub-subject full-battery scratch run** (all 13 instances)
and re-derive it end-to-end with the examiner tooling.
*Checkpoint:* the §5 build-acceptance gates, run in full, on the
assembled package.

**End state.** A constructed pilot package — tools, driver,
record, supervisor, adapter, examiner — plus the Stage 5
evidence pack (§2.4), offered for independent inspection (§7).
Nothing in the end state has called the subject.

---

## 5. BUILD-ACCEPTANCE GATES

**All five gates must pass before the constructed package is
offered for independent inspection.** A failed gate returns the
build to the relevant batch; there is no partial pass and no
waiver recorded in prose — a gate either passes on preserved
evidence or the build is not done. Every gate's evidence is
preserved as an artefact and verified by re-derivation
(Criteria §8), not by trusting its summary.

- **G1 — The sabotage battery S1–S5** (Criteria §4), run against
  the built PILOT-TOOLS-01 in a scratch run context. S1 forged
  `operation_id` (the *guessable next sequence number* is the
  preferred form — refusal must come from the absence of an
  issuance entry, never from the id being surprising) → refusal.
  S2 genuine FOUND result presented for insertion → refusal.
  S3 genuine EXTRACTED result inserted (succeeds), then
  presented again → second presentation refused. S4 genuine
  EXTRACTED result whose `source_hash` no longer recomputes
  against a perturbed scratch snapshot → refusal. S5 extraction
  under a rule producing two valid matches → recorded AMBIGUOUS
  with all candidates and no value; its insert → refused. Each
  test's required outcome: the refusal object returned, an
  `INSERT_REFUSED` governance event with full
  claimed-vs-recomputed detail, **no** `LEDGER_ENTRY`, **no**
  value returned. **Any insertion succeeding — a ledger entry
  emitted or a value returned, in any test — fails the build,
  full stop**; and a tool that refuses everything has also
  failed (S3's first insert must succeed). The battery's scratch
  record is preserved and cited in the inspection.
  **Zero-egress evidence (Rev 12, Claude's finding 1;
  widened, Rev 13).** The battery runs in the Stage 5 build
  environment, and this gate's evidence records that
  environment's **zero-egress check**: the environment has
  **no non-loopback network egress at all** — loopback
  interfaces only — and the preserved evidence shows the
  isolation of the **actual environment**: its **interfaces
  inspected** (for example, a network namespace with no
  external route), the **absence of any external route**,
  and the **absence of an available external proxy or
  connector path**. The check is performed and its result
  recorded alongside the battery's record; an environment
  in which non-loopback egress cannot be shown absent —
  or whose evidence addresses only direct routes — **does
  not pass this gate**. The no-contact rule is enforced by
  the environment, by the adapter's loopback refusal, and
  by its refusal of proxy configuration (§3.7); this gate
  is where that enforcement is evidenced.
- **G2 — The interrupted-write crash test** (Criteria §4, Rev
  04; Harness §2.6; SE-7(iii)), with **Alex's qualification**:
  the evidence must demonstrate a **genuinely torn write**. The
  harness is killed **while an event is being appended** — in
  the scratch context the append is fault-injected (a declared
  test-only slow/partial write path) so the kill lands
  mid-append deterministically; a kill that happens to leave a
  complete final event or no partial bytes **does not satisfy
  the test**, and the test is re-run until a torn tail is
  genuinely produced and that artefact set is the preserved one.
  **The injector must not ship (Rev 12, Claude's finding 6).**
  The slow/partial write path exists only under a **build-time
  flag** — `PILOT_TORN_WRITE_INJECTOR` — settable only in the
  scratch/test build configuration. A build outside the scratch
  context **refuses to compile with the flag set**; the flag's
  state for the build under examination is **recorded in this
  gate's evidence**; and a build carrying the injector is **not
  a scoreable build** — the injector's absence from any
  production or scoreable build is demonstrated by the recorded
  flag state, not asserted.
  The examiner verifies all three: (1) the incomplete trailing
  bytes are **inside** the CRASH commitment's
  `record_file_sha256` (recomputed over the file's exact bytes
  as they lie); (2) the trailing bytes are **never treated as a
  complete event** — chain verification and replay end at the
  last complete event the commitment's `event_count` and
  `final_event_sha256` name; the tail parses as no event,
  satisfies no step, enters no verdict; (3) the trailing bytes
  **cannot be silently discarded** — a trimmed or
  after-the-fact-completed record fails hash recomputation as a
  §3.1(ix) anchor failure. The test also confirms the negative
  space: **no TERMINAL receipt exists** for the crashed run, the
  CRASH receipt appears in the supervisor's issuance record, and
  the run's outcome under the criteria is INCONCLUSIVE. All
  three verifications hold, or the Stage 5 build fails this
  obligation. Artefacts preserved: the partial record, the CRASH
  receipt, the issuance-record entry.
- **G3 — SE-1…SE-7 demonstrated** (Harness §4.5). SE-1…SE-6 by
  structural inspection of the built code (the properties are of
  what code paths exist and what they can reach) **and** the
  adversarial tests of G1; SE-7 by the §3.5 demonstrations:
  OS-boundary refusal tests as the harness identity, supervisor
  self-computation, the launcher separation tests (§3.5(v)–(ix)),
  the crash cases (G2), and issuance-record verification
  including the planted-receipt negative test. A
  build in which any SE property holds only because no caller
  has tried to violate it has not met this gate.
- **G4 — Anchor-first replay over a full run record.** The
  Batch 6 stub-subject full-battery record (all 13 instances) is
  re-derived end-to-end by the examiner tooling following
  Harness §7 steps 0–6 in order: anchor verification first
  (START + TERMINAL against recomputed hashes, receipts against
  the issuance record), chain integrity, input identity,
  deterministic re-execution byte-for-byte, the insert audit
  with the registry reconstructed from events, subject
  artefacts (the stub's preserved outputs) never re-sampled, and
  outcome reconstruction matching the record. Any divergence
  localised by the chain is a gate failure with the localising
  event named.
- **G5 — Calibration certificate complete.** PILOT-CALIBRATION-01
  exists, is pinned, and certifies all 13 instances ANSWERABLE —
  or names the UNANSWERABLE exceptions with their causes
  (Criteria §5.3). An UNANSWERABLE instance is not a build
  failure; it is a named limit the Stage 6 authorisation packet
  must carry. But a calibration pass that was not run, or whose
  §5.1(6) configuration-freeze check was skipped, fails this
  gate: the frozen adapter configuration's **values** (temperature
  0.6, top_p 0.95, reasoning_budget 16384, max_tokens 20480)
  must be mechanically verified, not merely hashed. The
  mechanically checked configuration values also include the
  **canonicalisation standard identifier** (§3.4): the frozen
  configuration must record RFC 8785 (JCS) as the canonical
  form, and calibration verifies that recorded value — a
  configuration naming any other form, or none, is a freeze
  defect of the same kind.

**Stub-subject rule, restated as a gate condition.** Every gate
above runs against the scripted stub subject and the local
transport double (§3.7). **Nemotron is not called in Stage 5 —
not for a gate, not for a checkpoint, not for a smoke test.**
The first model call belongs to Stage 6, under Ben's separate
authorisation (§7; §6.4).

---

## 6. OPEN ITEMS — CARRIED VISIBLY, NOT SILENTLY DECIDED

### 6.1 Open for decision (no build default taken)

1. **Interrupted-write test at Stage 6 pre-flight — UNDECIDED.**
   Criteria §9 Q3's repetition default covers the S1–S5 battery
   at Stage 6 pre-flight (repeat S3/S4/S5 only if the tools
   revision, the rules, or the snapshot changed after Stage 5).
   The interrupted-write test sits in §4 **outside** that
   battery, so the default does not extend to it (REVISION-04-
   NOTE sweep note). Alex asked for the test at Stage 5 only and
   has not decided its pre-flight repetition; neither does this
   spec. It must be decided — by Alex/Ben — in the Stage 6
   authorisation, not discovered there.
2. **The smoke-call question.** Served status (§3.6) and hosted
   acceptance of `chat_template_kwargs` (Adapter §1.3(e)) can
   only be closed by a call. Adapter §7 Q7's default stands:
   **no smoke call** — served status is established by the first
   authorised Stage 6 call, and a 404 there follows the §1.4
   re-pin procedure. Whether any declared smoke call is ever
   made is **Ben's Stage 6 decision**; Stage 5 neither makes one
   nor builds a facility for one beyond the adapter itself.
3. **Stage 6 battery composition.** Run count, repetitions, and
   scheduling are set at Ben's Stage 6 authorisation (Plan
   Stage 6), not here. This spec builds for the 13-instance
   battery the criteria define and asserts nothing about how
   many runs Stage 6 will comprise.

### 6.2 Adopted defaults (design open questions, taken as the build baseline)

The sources carry the following as open questions **with
recommended defaults** (Harness §8; Adapter §7; Criteria §9).
This spec adopts each default as the build baseline, named here
so an inspector can strike any one of them into an amendment
item:

- Corpus access: **pinned snapshot**, read-in-place rejected
  (Harness §§5, 8 Q1). Solo arm: **excluded** (Harness §6.6;
  Criteria §6). FOUND inserts: **EXTRACTED-only, no exceptions**
  for the nine trees (Harness §8 Q3).
- Adapter-failure handling: tree invalidated, run continues,
  **3rd invalidation stops the run** (Harness §§6.3, 8 Q4;
  Criteria §§3.3, 7.2(3), 9 Q1 — INVALID allowance in SUCCESS
  ≤ 2 stands with it).
- Time budgets: **60 s / 300 s / 3,600 s / 4 h** (Harness §6.1;
  Criteria §7.2(2)). Operation-id consumption: **single-use**,
  reuse only by tree declaration, none declared (Harness §8 Q7).
  Orphan captures: cited by governance event, never retro-fitted
  (Harness §8 Q9).
- Adapter: **`seed` omitted** in configuration v1 (Adapter §7
  Q3); retry bounds **2 attempts, 5 s** (§7 Q5); per-attempt
  timeout **120 s** (§7 Q6); capture format **one JSON file per
  capture, no adapter index** (§7 Q8); catalogue evidence
  **re-captured at Stage 6 pre-flight** (§7 Q9).
- Criteria: T05's evidentiary weight **follows whatever
  calibration pins** — a disagreement between the manifest row
  and the change record is programme record, never "fixed" in
  the pinned data (Criteria §9 Q4); the examiner **confirms
  receipts against the issuance record at Stage 5 inspection**
  (Criteria §9 Q5 — discharged by gate G3/G4's step-0
  verification and recorded in the evidence pack).

### 6.3 Flagged spec-level decisions (this spec settles what the sources leave open; inspectors judge them)

**Rev 14 consistency note (finding D-26).** Every status label in
this section is read against the disposition register (§0.7) and the
gate records, which govern in case of any difference. Item 5's
no-contact statement is read subject to §0.3 — the single
authoritative provider-contact policy, including its
Ben-authorised per-operation exception — and to the D-4 breach
record at §0.4, which records the one Stage 5 contact event and its
disposition. No label in this section claims a gate has passed
unless the corresponding gate record says so.

1. **Supervisor concrete form** (§3.5): the two-OS-identity
   launcher design. Harness §8 Q10 authorised a Stage 5 decision
   and stated the default ("lightest form that keeps the write
   path outside the harness's privilege boundary"); this is that
   decision, stated as a proposal for the inspectors. Rev 02
   completes it with the privileged launcher mechanism (§3.5),
   answering Alex's correction A; the custody model itself is
   unchanged.
2. **Stub subject and transport double forms** (§3.7): required
   by the no-call rule and by Adapter §3.2's forced-429/500
   testing requirement, unnamed in the sources; fixed here as a
   scripted responder behind the adapter boundary and a loopback
   scripted HTTP endpoint, both confined to scratch contexts and
   labelled in every artefact they touch. Rev 02 adds the
   synthetic-capture requirement of §3.7 (Alex's condition on
   this item): the stub run's captures must satisfy Criteria
   §1.1(6), explicitly labelled. **Rev 12 adds the enforcement
   of the no-call rule this item serves (Claude's finding 1):
   in Stage 5 mode the adapter refuses any non-loopback base
   URL, the build environment holds no provider credential,
   and gate G1 records a zero-egress check (§3.7, §5).
   **Rev 13 makes the isolation total (Alex's correction,
   pb-mwel2vwg): the environment has no non-loopback egress
   at all, the adapter honours no proxy configuration or
   forwarding mechanism in Stage 5 mode, and G1's evidence
   shows the actual environment's isolation, proxy and
   connector paths included (§3.7, §5).**
3. **Canonical serialisation** (§3.4): Rev 01 fixed a
   description (UTF-8, sorted keys, no insignificant
   whitespace); Alex's inspection found it under-specified, and
   **Rev 02 replaces it with the pinned RFC 8785 contract**
   (§3.4), frozen at Batch 0 before any hash is generated. The
   item remains a flagged spec-level decision, in its corrected
   form.
4. **Implementation language.** The sources do not pin one. This
   spec fixes the default: **the same language as the pinned V2
   code and the connector helper (Python)** — for continuity of
   inspection (the inspectors read the V2 baseline and the
   helper already), for byte-exact control of serialisation and
   hashing, and because the adapter's live path (§3.6) runs
   through the sanctioned helper. A different language for any
   component is an inspector-approved amendment with its
   rationale recorded, not a builder's preference. **Rev 12
   names the one exception (Claude's finding 3): the privileged
   launcher (§3.5) is implemented in **C**, compiled at build
   time, and is recorded here as the launcher-language exception to
   this item's default — **approved in principle by Alex**
   (pb-mwfkgkm5-i-gog7), subject to inspection of the actual
   source and binary, the pinned interface, and SE-7 evidence;
   Claude's conditional acceptance is recorded at his Rev 14
   interim, his final disposition pending. This records an
   inspector disposition, not a build approval.
   The reason is mechanical: **Linux ignores the setuid bit on
   interpreted scripts**, so a setuid launcher cannot be an
   interpreted programme. Everything else in the build, the
   launcher apart, is Python under this item.
5. **Batch 0 catalogue evidence.** Adapter §1.4 requires
   date-stamped catalogue evidence at the Stage 5 freeze.
   **Rev 12 reverses the Rev 01 default (Claude's finding 2):**
   the freeze evidence is the **design-time catalogue snapshot,
   carried into the freeze** — the snapshot the design stage
   took, pinned by its hash in the re-freeze amendment — and
   **no request to the provider host is made in Stage 5 at
   all**. The Rev 01–Rev 11 default — a read-only
   `GET /v1/models` listing through the connector at Batch 0,
   accepted by Alex in the Rev 01 inspection on the ground that
   a listing is not a subject call — is **removed from Stage
   5**: an authenticated request to the provider's live host is
   **provider contact**, whatever it returns, and Stage 5's rule
   (Rev 12, §3.7) is zero provider contact. The live listing is
   taken at **Stage 6 pre-flight** instead, where the catalogue
   is re-evidenced against the live host before any run (§3.6;
   Adapter §1.4) — the position §6.2's adopted default
   (Adapter §7 Q9) already assumes. **Alex's re-inspection is
   asked to adjudicate this reversal expressly:** it strikes a
   point he accepted, on the second inspector's reasoning.

### 6.4 Builder identity and role separation

Criteria §2 binds: **builder ≠ scorer ≠ examiner**, the
examiner's independence being the term that never yields. This
spec therefore does **not** name the builder: who builds is
Ben's decision at his Stage 5 go (§7), and whoever builds may
not examine the package they built, nor score a run on it
without the examiner's re-derivation standing behind every
verdict. If the builder and the operator/scorer of first
instance are the same party, that overlap is declared in the
scoring worksheet itself (Criteria §9 Q2).

---

## 7. GATES AND ROLES — NO STEP AUTHORISES THE NEXT

The Stage 5 sequence, with each gate held by its named holder.
**No step in this list authorises the next**; each is a separate
act by its holder, recorded as such.

1. **This specification** is drafted (this document) and
   **shelved**. Shelving is publication of the paper, not
   approval of it.
2. **Alex inspects** the specification (source-to-requirement
   crosswalk; harness-architecture review; the §3.5 custody
   proposal; the §6.3 flagged decisions) **and Claude inspects
   it independently** (Ben's addition, 2026-11-12). The two
   inspections are independent: neither inspector's verdict is
   an input to the other's. Findings are answered by amendment
   to this spec, re-inspected as the finding requires.
3. **Ben's Stage 5 build go.** Only after both inspections stand
   does Ben authorise the build — his separate decision, against
   this spec as inspected. The go names the builder (§6.4).
4. **The build** proceeds by the §4 batches, each checkpoint
   recorded. Deviations from this spec stop the batch (§2.1).
5. **Build-acceptance gates G1–G5** (§5) pass on preserved
   evidence.
6. **Independent inspection of the constructed package** — Alex
   (per Plan Stage 5 and his offers) and Claude independently,
   against this spec and the design package: structural
   inspection of SE-1…SE-7, re-derivation of the battery, crash
   test, and stub-run records, and confirmation of the receipts
   against the supervisor's issuance record (Criteria §9 Q5).
   The builder does not examine (Criteria §2).
7. **Ben's Stage 6 execution authorisation** — a separate
   decision, against the inspected package, the calibration
   certificate (§5.3), and these criteria, setting run count,
   battery composition, and stopping conditions (Plan Stage 6),
   and deciding the §6.1 open items (interrupted-write
   repetition; any smoke call). The first model call happens
   only here, if Ben authorises it.

**Roles.** Ben: owner — adoption, the Stage 5 go, the Stage 6
authorisation; his index law binds every stage. Alex: design
adjudicator and examiner — inspections at steps 2 and 6, the
crosswalk, re-derivation over the worksheet. Claude: independent
second inspector at steps 2 and 6. Builder: named at step 3;
builds to this spec; examines nothing they built. Operator /
scorer of first instance: applies the criteria mechanically to
preserved records and produces the scoring worksheet —
provisional until the examiner's re-derivation stands behind it
(Criteria §2). The subject: Nemotron, pinned (§3.6), called only
at Stage 6.

---

## Scope notes

- This specification inherits Plan 01's exclusions in full: no
  D3 v0.10 completion or conformance claim; no general obligation
  lifecycle; no live Shelf integration (inputs are frozen and
  pinned); no role-enforcement claim from T04's behavioural
  refusal; nothing here touches the ratio study, the Approved
  Pool indexing idea, or the Crusher comparison — Alex's rulings
  on Ben's two parked ideas (REVISION-02-NOTE) keep both as
  separate future projects, expressly **not** smuggled into
  Stage 5.
- Claims discipline: every claim this spec makes about the build
  is a claim about what the build **must exhibit to be
  inspected**, not a claim that anything has been built or
  verified. At the time of drafting, nothing in §2.4 exists.
- Where this spec restates a source, the source governs on any
  divergence discovered at inspection; the divergence is an
  amendment item against this spec, never a silent preference
  for either text.
