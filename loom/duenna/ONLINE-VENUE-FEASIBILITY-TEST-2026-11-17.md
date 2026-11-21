# ONLINE-VENUE FEASIBILITY TEST — RUDIMENTARY (2026-11-17)

Owner's tap, 2026-11-17 03:21 MST: checks only — no accounts,
no keys, no live call, no battery execution. Question: could
an online Linux host serve as the battery's custody venue
(the owner's laptop being the current ruled venue, its live
path blocked at §6(c))?

## The test

`probe_host.py` (in this directory on the shelf:
duenna/online-venue-test-2026-11-17/) measures the decisive
custody facts on any Linux host: NoNewPrivs, seccomp, the
room filesystem's suid capability, a FUNCTIONAL setuid
elevation test (a root-owned setuid helper run as nobody
must come back euid 0), loopback binding, toolchain
(gcc/python3/useradd/systemctl), and resources. Outbound
HTTPS is deliberately NOT tested (no live call in scope).

## Controls — the probe is validated both ways

- **This VM (known-bad): NOT_FEASIBLE.** NoNewPrivs=1; the
  elevation test fails even on a suid-capable mount
  (uid 65534, euid 65534). Matches the measured venue fact.
- **The laptop WSL room (known-good): CUSTODY_FEASIBLE.**
  NoNewPrivs=0; elevation passes (uid 65534 → euid 0);
  loopback and toolchain pass. Matches the room's live
  supervised runs.

First WSL run falsely failed: the probe's scratch dir sat on
WSL's nosuid /tmp tmpfs, not on a room-class filesystem. The
probe was fixed to test on a rootfs directory and re-run on
both controls; the VM's failure is unchanged and is now
attributable to NoNewPrivs alone. (venue-probe-vm.json /
venue-probe-wsl.json hold the final runs.)

## What an online host must provide (requirements sheet)

1. Real Linux with root (or full sudo): a VPS or dedicated
   box — NOT a container or user-namespace sandbox that
   forces NoNewPrivs.
2. NoNewPrivs=0 for the supervisor chain; setuid honoured
   on the room's filesystem (ordinary ext4/xfs rootfs).
3. Ability to create dedicated unprivileged users
   (supervisor/harness separation), gcc + python3 for the
   launcher and harness builds.
4. Persistent disk for the room and run records; loopback
   networking unrestricted; systemd or equivalent.
5. Outbound HTTPS to integrate.api.nvidia.com — untested
   here; verified at provider-selection time.

## What this test does NOT settle

- Provider choice, account, and cost are the owner's
  (account creation is never delegated).
- The credential route on an online host is a NEW decision:
  Route 2's surrogate/Sentinel path is specific to this VM;
  nothing about it carries to an online room.
- The owner's venue ruling (laptop, joint 6) stands until
  superseded by a new ruling; the examiner must inspect any
  new room before battery use, as with every venue change.

Verdict of the rudimentary test: the online-venue door is
REAL — the custody requirements are ordinary Linux facts,
satisfied by the known-good control and failed by the
known-bad one for exactly the measured reason. Whether to
walk through it is the owner's next decision.
