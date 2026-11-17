# Stage 6 Battery Preparation — Amendment 01: Credential Route 1

Status: OWNER-RULED 2026-11-17 03:34 MST (tap + confirming words).
Amends: `duenna/STAGE6-BATTERY-PREPARATION-2026-11-17.md` (the credential
route of §3/§4, and verification items §6(b)/(c) as they applied to the
retired design). Everything not named here stands as filed and ruled.

## 1. What changes

The credential route. Route 2 (VM-side relay + SSH tunnel, surrogate
attached on the VM) is SUPERSEDED by Route 1: the NVIDIA key lives in
the laptop room, placed there by the owner himself.

- The relay (`battery_relay.py`) and the tunnel retire as load-bearing
  components. Their §6(b) construction evidence stands as the record
  of the retired design.
- §6(c) retires with that design: UNPROVEN, not failed. The tunnel hop
  measurements remain filed in the relay build evidence.

## 2. The Route 1 mechanism

- The owner writes the key through a no-echo prompt into a staging
  file in his WSL home (`~/.battery-nvidia-key`, mode 0600). The value
  never passes through chat, the orchestrator, or any log.
- At room staging (root), the key is installed to the room's credential
  location with harness-identity ownership, mode 0400. The staging
  file is then removed.
- The battery adapter variant reads the installed file at call time
  and attaches `Authorization: Bearer` directly to
  `https://integrate.api.nvidia.com/v1/chat/completions`.
- The key value never appears in any log, capture, or record. §3.4
  redaction is unchanged; captures record credential PRESENCE only.

Adapter differences from the relay variant: the base URL is the real
endpoint (no tunnel endpoint); the credential is attached by the
adapter from the installed file (the relay variant attached nothing).
Per-instance ceilings are unchanged (10,240 / 6,144 / 20,480 groups,
as ruled); retry remains max_attempts 2, as ruled.

## 3. Placement incident and rotation

On 2026-11-17 ~03:46 MST, during placement preparation, the owner
pasted the existing key (the connector's key) at a bare shell prompt
and photographed the terminal to the orchestrator. The value was
exposed in that image and in terminal scrollback.

Containment, verified: history was cleared in-session before any
write; the history file contains zero trace (checked by match count —
the orchestrator did not read the value); the staging file was never
created. The orchestrator has not copied or used the exposed value.

Consequence: the key placed in the room will be a NEWLY GENERATED key.
Once it is placed and vaulted for the connector, the exposed key is
deleted at the provider.

## 4. Replacement verification for §6(c) (Route 1 form)

- (c1) Placement attestation: the owner confirms placement; a
  room-side presence check reads metadata only (exists, owner, mode,
  byte-length range). No value is read into any record.
- (c2) Adapter construction check against a local capture point, no
  live call: the constructed request shows Authorization presence and
  the Bearer scheme; the value is never recorded. Same test-mode
  discipline as §6(b).
- (c3) First live use remains the battery itself, under the owner's
  separate execution authority.

## 5. What does not change

Venue (the laptop room, joint 6). Budget ceilings as ruled. The retry
ruling. The dress rehearsal evidence. The battery pass bar. Execution
still requires the owner's separate word.

## 6. Ask of the examiner

Inspect this amendment. Rule on (c1)–(c3) as the §6(c) replacement.
Confirm whether the package is otherwise ready for the final §6(e)
inspection once the Route 1 staging evidence (adapter variant + (c2))
is filed.
