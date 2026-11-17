# Stage 6 Battery — Actions Venue Preparation Package (2026-11-17)

Built by the orchestrator under the owner's go (2026-11-17 05:57 MST),
implementing the examiner's venue-change disposition @ 77c1018:
the (c1) injection record, the (c2) adapter construction check inside
the workflow, and the fail-closed custody probe gate. The dress
rehearsal on Actions is NOT in this package; it is the next
preparation step. No execution, arming or live call is contained in
or authorised by this package.

## Contents (sha256)

- actions_adapter.py — 9b80c37a19b751f765581e0a15476559edaef16c9b85c713dcc09d7bbeca4890
  The pinned Actions adapter variant, built by exact-match transform
  of the filed Route 1 adapter (route1_adapter.py,
  cb56901e03f9e158…). Differences are enumerated in its footer: the
  credential is read at call time from the platform-injected
  environment variable named at construction (credential_env)
  instead of a room credential file; an unset or empty variable
  fails the attempt closed as a captured CredentialError. Transport,
  per-instance ceilings, canonical config pinning, retry
  (max_attempts 2), capture format, §3.4 redaction and §4
  classification are unchanged.
- actions-adapter-config.json — f8ecb4ee31a7e21d16cc43155a9655f6e480fa13c7a160a212dd0da8bfe01658
  Identical to the Route 1 config except the configuration_of text.
- pilot_jcs.py — 8a131cfce23c97623aff6962e5315faf1543fbeb1533af8cd96a91feb9660d6c
  The pinned RFC 8785 canonicalisation helper, byte-identical to
  the accepted stacks.
- capture_server.py — 65cce265f643dfc10b2be649e58041158cef0afef1e4a048c4776e60138268cc
  The (c2) loopback capture service: binds 127.0.0.1 only, records
  booleans only (header present, Bearer scheme, value matched the
  injected secret — compared in memory), returns a canned response.
- c2_driver.py — 7d9aa495d134168c8513a47ee8d6c3c538bbf87327646046dcfdb65393c875ef
  Runs the adapter once against the capture service in stage5
  isolation mode and writes prep-results/c2-result.json; fail-closed.
- battery-prep.yml — 98f2730eba319e97ed2af9388eba5d7dcafd276337ab42cab9367fba9341318a
  The Battery repo workflow (placed at .github/workflows/): custody
  probe gate (stops unless CUSTODY_FEASIBLE), credential injection
  record (credential_injected: true only — never value, length or
  hash), the (c2) check, and the prep results committed back to the
  repo.
- probe_host.py — c6b07684a9330603f253638e688736a1e79ce0f6ab65b773d83b90a75276623b
  The filed custody probe instrument, unchanged.

## Local mechanics verification (orchestrator, 2026-11-17)

Before filing, the adapter + capture service + driver were run
end-to-end on the orchestrator's VM with a DUMMY credential value
(not the owner's key): c2-result passed=true, all nine checks true,
credential_recorded_by_server=false, driver exit 0. This verifies
the construction mechanics only. It is NOT the (c2) evidence — the
(c2) evidence is this package's run inside the Actions workflow
against the owner's injected secret.

## Placement

Target repo: Q420/Battery (private; owner-created). Files go to the
repo root; battery-prep.yml goes to .github/workflows/. The
orchestrator's connector cannot see the private repo until the owner
adds the Muse GitHub App to it, and cannot place workflow files in
any repo (platform restriction) — the workflow file is placed via
the owner's signed-in browser, as the venue probe workflow was.
