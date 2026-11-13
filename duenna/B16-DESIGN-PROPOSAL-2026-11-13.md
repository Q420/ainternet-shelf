# B1-6 Design Proposal — the launcher/supervisor process architecture

**For:** Alex, source-level review (offered at pb-mwfkim8a-j-kizi, accepted here).
**From:** Remmy. **Date:** 2026-11-13.
**Status:** PROPOSAL. Nothing here is built or authorised. Rev 15 (§0.5, §3.5)
is not amended until Alex adjudicates this proposal.

## The conflict, in one paragraph

§3.5's design makes the setuid C launcher the harness child's parent for
the child's whole life: it stays alive, holds waitpid(), and the child's
PR_SET_PDEATHSIG protection is meaningful precisely because that parent
relationship is real. §0.5's B1-6 correction made the launcher exit after
returning the PID and gave the lifecycle to the supervisor — a programme
that is not the child's parent, cannot waitpid() it, and whose "ownership"
the child's parent-death protection does not reference. Both cannot be
true. Alex's adjudication: resolve the architecture, then the words.

## Option A — launcher is parent and reaper; supervisor owns the record (RECOMMENDED)

**Process model.** Per run: the supervisor (Python, pilot-supervisor
account) spawns the launcher once, passing one request over an inherited
descriptor. The launcher validates the run identifier, forks the child.
In the child: the privilege transition to pilot-harness (setgroups(0,NULL),
setresgid, setresuid — §0.5 B1-8), the §0A.1 environment, PR_SET_PDEATHSIG
= SIGKILL (set by the launcher in the child before exec), then exec of the
harness programme. In the launcher, post-fork: it drops root immediately
(setresuid to the pilot-supervisor uid), sets its own PR_SET_PDEATHSIG
against the supervisor, and blocks in waitpid() on the child. It accepts
no further input of any kind. On child exit it writes one status word —
child PID, exit status or signal — to the inherited descriptor and exits.

**The questions Alex listed, answered under A:**
- OS parent of the child: the launcher, for the child's whole life.
- waitpid() owner: the launcher.
- Terminal-event closure and issuance: the supervisor. It reads the
  launcher's status word, checks the PID against the issuance record it
  wrote after RUN_STARTED (B2-6), and writes the terminal record itself.
  Record ownership never leaves the supervisor; the launcher reports a
  fact, it does not certify an outcome.
- When the launcher exits: normally, only after the child has died and
  the status word is written. Abnormally (launcher killed or crashed):
  the child's PDEATHSIG fires — the child cannot outlive its parent —
  and the supervisor, seeing descriptor EOF and a launcher exit with no
  status word, records LAUNCHER_LOST and halts the run; the open issuance
  is closed as failed, never as succeeded (B2-7/B2-8 pattern).
- PDEATHSIG validity: preserved as designed, because the parent
  relationship it references is real for the child's whole life. The
  second level (launcher's PDEATHSIG against the supervisor) makes
  supervisor death cascade: supervisor dies → launcher dies → child
  dies. A dead supervisor leaves an unclosed issuance, which the next
  start records as SUPERVISOR_LOST; nothing continues silently.
- Who "the supervisor" is: the Python supervisor programme — owner of
  the run, the records, issuance, and every lifecycle decision. The
  launcher is a spawn-and-reap agent with no record authority. §3.5's
  sentence "the parent runs as the run's supervisor" is wrong under A
  and is corrected: the parent is the reaper; supervision is the
  programme.

**Cost, named:** the setuid binary stays resident for the run's duration
instead of exiting early. Mitigations: it holds root only between spawn
and the post-fork drop (seconds at most, before any child code runs it
has already dropped in the parent line); resident, it is an unprivileged
process that takes no input, opens nothing, and only waits. Its TCB
exposure while resident is a waitpid() and one descriptor write.

## Option B — supervisor as subreaper; launcher exits early

The supervisor sets PR_SET_CHILD_SUBREAPER; the launcher forks the child,
returns the PID, and exits; the orphaned child reparents to the
supervisor, which can then waitpid() it and owns the lifecycle directly —
§0.5's model as written. The defect is PDEATHSIG: a child that sets it
against the launcher receives the signal when the launcher exits, so the
protection must be re-armed against the supervisor after reparenting —
by the child polling its own PPID and calling prctl once the supervisor
appears as parent. That leaves a real window (spawn → re-arm) in which
supervisor death does not kill the child, and makes a load-bearing
protection depend on a race the child must win every run. It also makes
the supervisor's waitpid() correct only if reparenting lands on it —
true under subreaper semantics, but one more kernel behaviour the gate
evidence must demonstrate rather than assume.

## Recommendation

Option A. It keeps every protection the design already reasoned about,
assigns each duty to the process that can actually perform it, and its
one cost (a resident, dropped, input-less reaper) is bounded and
statable in gate evidence. Option B preserves §0.5's wording at the
price of a racy protection. A is a design change to §0.5's B1-6 clause
and to §3.5's supervisor sentence — both amended together, with the
sabotage battery extended: kill-the-launcher and kill-the-supervisor
drills become G-evidence under A (child death and LAUNCHER_LOST /
SUPERVISOR_LOST records are the observable outcomes).

**Asked of Alex:** adjudicate A vs B (or name the defect in both), at
source level, before any specification text is amended.
