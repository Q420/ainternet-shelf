# LAUNCHER BEHAVIOUR-AND-INTERFACE FREEZE — BATCH 0

**Frozen:** 2026-11-12, at Batch 0 of the Stage 5 build.
**Authority:** Stage 5 Build Specification 13, §3.5 points 2–4 and the
blocks following point 4 (descriptor destinations; exec condition and
identity continuity), as directed for Batch 0 by Spec §4 ("Launcher
behaviour-and-interface freeze", Rev 12, Claude's finding 5).
**Effect:** Batch 4 implements the launcher **against this freeze** and
pins the resulting source by dated addition at the Batch 4 checkpoint.
Freezing the interface changes nothing about the launcher's specified
behaviour — only **when** its target is fixed. Any divergence between
an implementation and this freeze is a defect in the implementation,
or else a spec amendment through Ben/Alex — never a builder's
settlement (§2.1).

## 1. Identity and form

- A minimal, single-purpose binary, owned by **root**, **setuid-root**,
  mode **`4710`** with group **`pilot-supervisor`** — only the
  `pilot-supervisor` identity can execute it.
- Implemented in **C**, compiled at build time (the approved exception
  to the Python default, §6.3 item 4: Linux ignores the setuid bit on
  interpreted scripts).
- **Single-threaded across the whole launch lifecycle**: no thread
  creation anywhere in the pinned implementation; launch evidence
  records `Threads == 1` from the launcher's `/proc` status for each
  test launch.
- Source small enough to be read in full at inspection; pinned by
  sha256 in the re-freeze amendment by dated addition at Batch 4.
- **Setuid preconditions, verified fail-closed:** supported OS is
  Linux. The assumption that the launcher actually receives effective
  root is verified by probe (Batch 0 probe evidence), never presumed:
  a probe invocation must observe effective uid `0` inside the
  privileged window, with the `nosuid` mount condition and any
  inherited `no_new_privs` flag checked and recorded. **A failed
  privilege assumption stops the build; no fallback to a weaker
  launch arrangement exists.**

## 2. Operation set — one operation

The launcher's entire operation set is the **single fixed spawn**:

- It accepts **no arbitrary input**. The harness programme path and
  the argument-vector shape are **compiled into the binary**; there
  is no configuration file.
- The sole variable field is the **run identifier**, in its fixed
  argv position, validated against a strict pattern (see §7,
  residual R-1). The run identifier's grammar is the record's
  (§3.4): `<battery-id>-<UTC date>-<counter>`.
- Any other invocation — different programme, extra or missing
  arguments, malformed run identifier — is **refused**: the launcher
  exits non-zero and spawns nothing.
- It invokes **no shell**, opens **no network connection**, loads **no
  code beyond the fixed exec**, and contains **no operation** that
  modifies, replaces, renames, unlinks, or redirects the protected
  installation tree, and **no ambient-capability raising** (no
  `prctl(PR_CAP_AMBIENT)` call).
- **The privileged window performs no file writes at all.** Its only
  acts are the gate-pipe creation, the fork, the two privilege
  transitions, the gate release, and the exec.

## 3. The gate protocol (the spawn sequence, §3.5 point 3)

**Pre-fork (parent):**
1. Create the private launch-gate pipe with `pipe2(O_CLOEXEC)`: read
   end passes to the child; write end held by the parent; no other
   process holds either end.
2. Capture the **expected parent identity** — the parent's own
   `getpid()` — in a variable the child inherits across the fork.

**Child, in order:**
3. First act: `getppid()` must equal the inherited expected parent
   identity; on mismatch, `_exit()` at once (the parent died before
   the child's first instruction and any later-captured identity
   could be the reaper's).
4. Clear supplementary groups; `setresgid()` then `setresuid()`,
   each setting **all three** ids to `pilot-harness`; verify by
   `getresgid()`/`getresuid()` read-back — every position exactly
   `pilot-harness`. Any failure or mismatch: `_exit()` immediately;
   never continue into the exec on a failed or partial transition.
5. **Capability read-back** (part of the same post-drop verification,
   before arming, descriptor close, and gate): read own `CapEff`,
   `CapPrm`, `CapAmb` by **Method A** — the `/proc/self/status`
   fields read and verified directly — or **Method B** — `capget`
   for effective and permitted, **plus** `prctl(PR_CAP_AMBIENT,
   PR_CAP_AMBIENT_IS_SET, …)` for **every** capability number 0 to
   the kernel maximum, each required to return 0 (capget does not
   return the ambient set; a method that cannot observe it does not
   satisfy the requirement). **All three sets must be empty.** Any
   nonzero value, or an unsuccessful / incomplete / malformed /
   unavailable read-back, bars the launch identically: `_exit()`.
   The three masks as read are preserved as launch evidence.
6. Arm the parent-death backstop: `prctl(PR_SET_PDEATHSIG, SIGKILL)`
   — **after** the transitions (Linux clears the setting on any
   effective-uid/gid change; no credential change follows it).
   Fail-closed on the `prctl()` return; immediately read back with
   `prctl(PR_GET_PDEATHSIG)` and require `SIGKILL`; any failure:
   `_exit()`.
7. Re-check the parent relationship: `getppid()` must still equal
   the pre-fork expected identity; on mismatch, `_exit()` at once.
8. Close **every inherited descriptor except the declared allowlist**
   — fds `0`, `1`, `2` (retained only in their declared roles at
   their verified destinations) and the gate read end (pre-exec
   window only) — by exhaustive close (`close_range(3, ~0U)` sparing
   the gate descriptor, or `/proc/self/fd` enumeration).
9. **Block at the gate**: read exactly one byte from the gate read
   end. Only the parent's single release byte proceeds — to the exec
   of the harness at the fixed path (the exec closes the gate read
   end via `O_CLOEXEC`). On end-of-file, any other byte value, or
   any read error: `_exit()` immediately, without executing.

**Parent, in order:**
10. Immediately and irrevocably drop: supplementary groups cleared,
    `setresgid()` then `setresuid()`, all three ids to
    `pilot-supervisor`, verified by the same read-back. The parent
    holds **no writable commitment descriptor** across a launch.
11. **Own capability read-back** before any release: `CapEff`,
    `CapPrm`, `CapAmb` by the same Method A / Method B. All three
    must be **successfully and unambiguously read and verified
    empty** — an unobserved capability state releases nothing. The
    observed masks join the child's in the launch record.
12. **Pre-release identity re-check** (identity continuity, layer
    3): re-resolve the fixed executable/interpreter paths
    canonically and re-stat the resolved objects; `st_dev`,
    `st_ino`, mode bits, and capability set must match the verified
    identity records **exactly**.
13. Only on a fully verified drop — identity and capability state —
    and a passing re-check: **release the gate** (write the single
    release byte; close the write end). Thereafter the parent is the
    run's supervisor: it holds the `waitpid()` relationship (every
    termination witnessed by the OS), and **computes and writes
    every commitment itself**, from the record file, which it reads
    directly (read-only access to `runs/` for this purpose). The
    supervisor never issues over harness-supplied values.

**Failure cleanup — two windows (§3.5 point 3):**
- **Window 1** (failure detected **before** the parent's drop takes
  effect; the parent is still privileged): the parent `SIGKILL`s the
  waiting child, closes the gate write end without a release byte,
  reaps with `waitpid()`, then terminates itself.
- **Window 2** (failure detected **after** the drop, including a
  nonzero or unobserved capability state or an identity re-check
  mismatch): no cross-uid signal is assumed — the gate is the kill
  switch. The parent closes the gate write end unreleased; the
  child observes end-of-file and `_exit()`s itself; the parent
  reaps it and terminates. The abort is recorded (with observed
  masks / identity values, as applicable).
- In neither window is any issuance made; no harness is left
  running and no child left waiting. The kernel backstop
  (child-armed `PR_SET_PDEATHSIG`) covers parent death at any point
  after arming, including after release — a second guarantee behind
  the gate's end-of-file path, not a replacement for it. The stated
  residual stands: a child disobeying end-of-file while the parent
  lives is excluded **by construction** (the pinned child sequence
  has exactly two post-read branches), not handled by authority.

**Ordering invariant:** the supervisor's independent observation and
issuance capability is fully established — parent dropped, verified,
holding `waitpid()` — before the subject begins work. No
interleaving exists in which the harness executes while the
supervisor side has failed.

## 4. Declared descriptor destinations (pre-launch verification)

- fd `0`: `/dev/null`, or a read-only pipe.
- fds `1` and `2`: pipes whose read ends the supervisor itself holds
  and drains into the run log, **or** one designated append-only
  (`O_APPEND`) log file in the supervisor-owned **run-log area** —
  a tree outside `commitments/` and outside every other protected
  store.
- **No retained descriptor** may be a file inside `commitments/`, a
  receipt, or `issuance-record.jsonl`, nor a writable handle to any
  of them, in any mode.
- Before invoking the launcher, the supervisor verifies each of fds
  `0`/`1`/`2`: resolve the `/proc/self/fd/` destination and read the
  access mode (`fcntl(F_GETFL)`), asserting a match with this
  declaration — for a pipe, the match must establish the pipe's
  **identity** (the descriptor is the actual pipe end whose other
  end the supervisor holds), not merely the `pipe:[...]` target
  form. Any mismatch or unresolvable destination: **no launch**;
  the abort is recorded in the run log (run identifier, offending
  descriptor, observed destination and mode).

## 5. Exec condition and identity continuity

- **Three-part exec condition**, verified at freeze time and again
  by the supervisor before **every** launch: the fixed harness
  executable is **not setuid, not setgid, and carries no file
  capabilities** — the condition binds the object the kernel
  actually invokes (where the harness path is a script, its
  **interpreter** binary). Checks are recorded as read: `stat` mode
  and `getcap` output preserved in the gate evidence. A failing
  target means no launch; the abort is recorded (run identifier,
  failing artefact, observed mode and capability set).
- **Layer 1 — protected placement:** the harness executable and any
  interpreter live under a protected installation tree: the files
  and **every directory component** of their resolved paths are
  root-owned and not writable by any other identity (directories
  `0755` or stricter). Three trust classes, stated as the spec
  states them: the **untrusted in-model identities**
  (`pilot-harness`, `pilot-supervisor`) are OS-prevented from
  modifying the tree — *on the verified capability state* (a
  process holding a DAC-bypassing capability is not bound by
  discretionary enforcement, which is why §3 step 5/11 observe the
  masks); the **launcher** is trusted pinned code containing no
  such operation (no OS-impossibility is claimed for its privileged
  window); the **operator/root** outside the launcher is outside
  the threat model (detection only, via layer 3, for substitutions
  landing before the re-check).
- **Layer 2 — canonical resolution and identity record:** at the
  freeze and at each pre-launch verification, paths are resolved
  canonically (as `realpath`) and the resolved objects' identity is
  recorded — `st_dev`, `st_ino`, mode bits, capability set, for
  executable and interpreter alike. At the freeze, an **audit of
  every path component** (owner and mode) evidences layer 1; a
  failing component means the tree is not recorded as protected
  until corrected.
- **Layer 3 — pre-release identity re-check:** §3 step 12 above.
  Its detection claim is scoped exactly as the spec scopes it:
  substitution at or before the re-check is detectable;
  substitution after it, by an actor authorised to write, is
  outside the threat model; the final interval's protection is the
  absence of an in-model writer, not the re-check.

## 6. What this freeze does not do

It builds nothing, installs nothing, and pins no launcher source
(there is none yet — Batch 4). It freezes the **behaviour and
interface** so Batches 1–3 can build on the custody assumption, and
Batch 4 implements against a fixed target.

## 7. residuals carried visibly

- **R-1 (run-identifier pattern):** the spec requires a "strict
  pattern" for the run identifier and gives the identifier's
  grammar (§3.4: `<battery-id>-<UTC date>-<counter>`) but does not
  pin the battery-id alphabet or the pattern itself. This freeze
  records the grammar as the frozen contract; the concrete pattern
  is Batch 4's implementation detail **against** that grammar, and
  the underspecification is named here rather than silently
  settled (checkpoint report, ambiguity A-1).
