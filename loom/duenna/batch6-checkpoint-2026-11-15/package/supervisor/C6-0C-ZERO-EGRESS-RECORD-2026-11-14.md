# C6-0C — ZERO-EGRESS ENVIRONMENT VERIFICATION RECORD (2026-11-14)

Pre-batch gate C6-0c of the approved Batch 6 chunk sheet (disposition ALEX-C6-0A-2026-11-14). Executed live in the Ubuntu room on Ben's laptop (WSL2, kernel 6.18.58.1-microsoft-standard-WSL2) via the SSH door, as root, 2026-11-15 08:02 UTC. Probe script: c6_0c_probe.sh; full transcript: c6-0c-transcript.txt (this directory).

## Standing state inspected

- Network namespaces: none standing (the Batch 0 model constructs the loopback-only namespace per run; the room itself is not zero-egress, as recorded at Batch 0).
- Links: lo (up), eth0 (up, NAT).
- Firewall: iptables and nft binaries are NOT installed in the room — no rules exist to inspect; the governing isolation mechanism is the namespace construction, verified below. (Batch 0's design does not rely on room firewall rules.)

## Construction + egress attempts (fresh namespace `c6-0c-test`, loopback only)

- Namespace created; `lo` brought up (127.0.0.1/8, ::1/128); route table EMPTY.
- Egress attempt 1 — ICMP ping 1.1.1.1: `Network is unreachable`, exit 2. BLOCKED.
- Egress attempt 2 — TCP connect 1.1.1.1:443 (python socket, 3 s timeout): `OSError [Errno 101] Network is unreachable`. BLOCKED.
- Egress attempt 3 — DNS resolution of example.com: `gaierror [Errno -3] Temporary failure in name resolution`. BLOCKED.
- Loopback sanity: ping 127.0.0.1 inside the namespace — 1 transmitted, 1 received, 0% loss. The namespace is functional; the block is the absence of any external route, not a broken stack.

## Cleanup

Test namespace deleted; final `ip netns list` empty. The room was left exactly as found; no standing state was created or altered.

## Result: C6-0c SATISFIED

The Batch 0 sandbox construction still enforces zero egress in the current environment. Carried forward to G1: the Batch 6 runs inherit this construction; G1's own zero-egress evidence is produced with the battery (C6-11) as the sheet requires.
