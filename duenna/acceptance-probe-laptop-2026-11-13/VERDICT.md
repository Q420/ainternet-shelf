# Acceptance probe — Ben's laptop, Ubuntu room (WSL2) — 2026-11-13

Candidate environment: Ubuntu 26.04.1 LTS under WSL2 on Ben's laptop
(MuseGadget0C94; kernel 6.18.58.1-microsoft-standard-WSL2). Probe run by
Remmy through the SSH door, as wsl root, 2026-11-13 00:58–01:03 MST
(room clock -07:00). Full raw transcript: ACCEPTANCE-PROBE-TRANSCRIPT.log
(byte-identical to the in-room log /home/ben/acceptance-probe.log, fetched
back and compared: 5,758 bytes each). Scripts as run: acceptance-probe.sh,
acceptance-probe-part2.sh. Probe source: setuid_probe.c, sha256
64625db91420e93222b9d307139c8aa0c278a6099540ebb0054134291499dc53 — the
frozen Batch 0 source, hash verified in-transcript before compiling.

## Results against the acceptance table

- 0.1 Virtualisation: `systemd-detect-virt` reports **wsl**. Recorded
  verbatim. WSL2 is a dedicated-kernel VM (its own kernel string above),
  not a container sharing a host kernel and not a user-namespace nest;
  classification against the requirement's intent is Alex's adjudication.
- 0.2 uid_map: identity map (0 0 4294967295), as root and as ben — PASS.
- 0.3 NoNewPrivs: PID 1 (systemd) = 0; entire invocation ancestry = 0 —
  PASS. (The incumbent VM failed exactly here: PID 1 = 1.)
- 0.4 Launcher filesystem: / is rw,relatime — no nosuid, no noexec — PASS.
- 1.1 Identities: pilot-supervisor uid 999 / gid 986; pilot-harness
  uid 997 / gid 985; separate groups; harness not in the supervisor
  group — PASS.
- 1.2 Custody: commitments/ chowned pilot-supervisor:pilot-supervisor,
  mode 0700, read back as assigned; parent chain traversable — PASS.
  (Incumbent failed here: chown denied on the workspace volume.)
- 1.3 Separation: harness denied read AND write on supervisor custody;
  supervisor reads its own; harness writes its own runs/ — PASS ×4.
- CENTREPIECE (F-1): probe installed root:pilot-supervisor, mode 4710.
  Invocation A as pilot-supervisor: **ruid=999 euid=0, NoNewPrivs 0,
  "PRIVILEGED WINDOW OBSERVED", exit 0 — PASS.** Invocation B as
  pilot-harness: Permission denied, exit 1 — PASS (refused, as designed).
  Probe binary sha256 on the laptop:
  7324b677deca67cdce1506850f16b5038a79898b059a895a3f4af17d5a9948df.
  First pass note: the centrepiece initially did not run — gcc installed
  but the minimal image lacked libc headers (stdio.h); a completion pass
  installed libc6-dev and ran the identical test. Both passes are in the
  transcript, undisguised.
- Capabilities: as pilot-harness, CapInh/CapPrm/CapEff/CapAmb all zero,
  CapBnd full (a ceiling, not a grant); ambient sets NONE for harness
  and ben (PR_CAP_AMBIENT_IS_SET) — PASS (observable and empty).
- Network: no proxy variables in the distro environment; default routes
  via WSL NAT recorded in the transcript. Inside a fresh user+network
  namespace (unshare -Urn as ben): route table empty, egress to a
  non-provider address (1.1.1.1:53) failed "Network is unreachable",
  loopback connect refused by the stack (alive) — PASS (loopback-only
  isolation constructible).

## Disclosed environment changes made by the probe
apt install gcc, then libc6-dev (compiler toolchain, required to build
the frozen probe source). Test identities, custody tree
(/srv/nemotron-pilot-probe), and the probe binary were left in place as
exhibits, as scoped.

## Remmy's verdict
Every acceptance check that ran PASSED, including the two mechanisms
whose failure stopped Batch 0 on the incumbent VM (F-1 setuid elevation,
F-3 custody). The 0.1 classification (wsl) and the final acceptance of
this environment for a Batch 0 re-run are Alex's adjudication, on this
evidence.
