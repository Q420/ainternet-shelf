# STAGE 6 BATTERY — RELAY + ADAPTER BUILD AND §6(b)/(c) TESTS (2026-11-17)

Built under the owner's tap of 2026-11-17 03:00 MST (relay +
battery adapter build, §6(b)/(c) tests, full package to the
examiner). NO live model call was made anywhere in this work:
the relay ran in TEST mode throughout (constructed requests
captured at the VM, canned responses returned, no upstream
call).

Artefacts in this directory: battery_adapter.py,
battery_relay.py, battery-adapter-config.json (the template;
sha256 in SHA256SUMS.txt), effective-config-digests.json,
relay-capture.json (the §6(b) capture record), relay-test.log.

## The battery adapter

Derived from the frozen pilot_adapter.py; differences are
enumerated in the module footer (endpoint = the relay tunnel
endpoint on laptop loopback; per-instance max_tokens from the
accepted ceiling table, substituted before canonical
verification; per-instance effective config digest computed
at start-up and recorded in every capture; retry carried by
config at the frozen max_attempts 2). Capture format,
redaction (§3.4), classification (§4) and the complete()
contract are unchanged from the frozen build.

Effective config digests (adapter_config_sha256 as recorded
per capture): 20,480 group f11e0dbb…; 10,240 group 59ca7abd…;
T03 (6,144) 71ea6b2c…. Worst cases under the 2,048/call input
allowance: 45,056 / 49,152 / 49,152 — within the 50,000
per-instance budget (examiner's revised budget ruling).

## §6(b) relay construction checks — PASS

Relay in test mode on the VM (loopback only), driven by the
battery adapter itself:
- Constructed upstream request captured: URL exactly
  https://integrate.api.nvidia.com/v1/chat/completions,
  method POST, Authorization header PRESENT with Bearer
  scheme and an `hsurr:` surrogate (presence and prefix
  recorded; the value is never recorded anywhere).
- The adapter completed the call against the canned
  response: HTTP 200, served model = pinned model, failure
  class None, envelope max_tokens 20,480 (T04 instance).
- Refusals verified: POST /v1/models → 404; POST /other →
  404; GET on the one path → 405. The relay's log records
  only timestamps, outcome class, status and byte counts.

## Adapter construction checks — PASS

- Per-instance ceilings construct correctly (T04 20,480 /
  T01 10,240 / T03 6,144) with distinct effective digests.
- An unknown instance ID is refused at start-up (ConfigError).
- A non-loopback base URL is refused at start-up (the frozen
  build's Stage 5 isolation, retained).

## §6(c) tunnel path proof — NOT YET PASSING (diagnosed)

Design: SSH remote-forward over the existing laptop door;
the relay endpoint appears on the laptop, the adapter calls
it from the WSL room. Measured facts:
- The VM-initiated SSH remote forward binds successfully on
  the laptop's Windows loopback (listener verified,
  127.0.0.1:18923, owned by sshd).
- The WSL room cannot reach that Windows loopback listener:
  WSL2's localhost forwarding does not mirror this sshd
  forward listener (127.0.0.1 → connection refused from WSL;
  the WSL gateway address and the laptop's Tailscale address
  on that port → timeout). Adapter calls through the tunnel
  therefore fail closed as TRANSPORT_ERROR captures — the
  failure mode the design specifies; no fallback exists.
- One hop IS proven: WSL reaches the laptop's sshd on its
  Tailscale address (100.104.166.7:22, banner exchanged).

Candidate completion (owner decision — it changes the
laptop's authorised-key surface): a dedicated keypair
generated inside WSL, its public key added to the laptop's
authorized_keys restricted to port-forwarding to the relay
port only; the tunnel then originates inside WSL
(ssh -L to the laptop sshd over its Tailscale address, the
sshd connecting onward to its own loopback forward listener
to the VM relay). No existing credential moves; the new key
can do nothing but forward that one port. Alternatives
(WSL mirrored-networking switch; a Windows-side forwarder)
are heavier on the owner's machine. §6(c) completes when the
owner rules and the end-to-end adapter call through the
tunnel is captured.
