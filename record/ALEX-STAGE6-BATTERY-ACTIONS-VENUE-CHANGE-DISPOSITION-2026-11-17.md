# Alex — Stage 6 Battery: GitHub Actions Venue Change and Evidence Disposition (2026-11-17)

Status: OWNER OVERRIDE RECORDED; VENUE CHANGE ACCEPTED. Preparation evidence remains open. No execution, arming, scheduling, or live call is authorised by this ruling.

## 1. Authority and venue disposition

The owner overruled joint ruling 6 on 2026-11-17 at 05:27 MST, conditionally: “I'm overruling if it works then this is the change.”

The condition is met by the owner's venue probe filed at Shelf commit `b3c1342fbe5fbdce4d58c59088a22b4358a14aa3`:

- Verdict: `CUSTODY_FEASIBLE`.
- `NoNewPrivs=0`: PASS.
- Functional setuid elevation: PASS (helper ran as uid 65534 and euid 0).
- Setuid-capable mount: PASS.
- Loopback bind/connect: PASS.
- Required toolchain: PASS.
- Runner resources: 4 CPUs and approximately 16 GB RAM.
- Outbound HTTPS: UNKNOWN; not tested.

I therefore ACCEPT the owner's overrule. For the Stage 6 battery, the custody venue is GitHub Actions, replacing the laptop room. Joint ruling 6 is superseded for this battery by the owner's later conditional ruling and its satisfied condition. The earlier VM result does not govern this Actions runner: the same probe measured different kernel and privilege capabilities.

Evidence:
- [Venue probe result commit](https://github.com/Q420/ainternet-shelf/commit/b3c1342fbe5fbdce4d58c59088a22b4358a14aa3)
- [Probe implementation](https://github.com/Q420/ainternet-shelf/blob/b3c1342fbe5fbdce4d58c59088a22b4358a14aa3/duenna/online-venue-test-2026-11-17/probe_host.py)
- [Probe workflow](https://github.com/Q420/ainternet-shelf/blob/b3c1342fbe5fbdce4d58c59088a22b4358a14aa3/.github/workflows/venue-probe.yml)
- [Prior joint ruling 6](https://github.com/Q420/ainternet-shelf/blob/b3c1342fbe5fbdce4d58c59088a22b4358a14aa3/record/REVAMP-JOINT-RULINGS-2026-11-17.md)

## 2. Scope of the probe

The probe establishes the runner's measured host-level prerequisites: privilege elevation, a setuid-capable filesystem, loopback operation, tools, and basic resources. It does not establish that the complete Stage 6 supervisor, launcher, harness, examiner, and evidence chain operates correctly on that runner. Nor does it test outbound HTTPS.

This is not a reason to withhold the venue change. It defines what the preparation must still demonstrate on the newly selected venue.

The existing dress rehearsal remains accepted as a laptop-room rehearsal. It is not evidence that the production process tree has already been exercised on Actions.

## 3. (c1) Repository-secret placement — required evidence

The old laptop file-metadata test is not the applicable evidence for this venue. The credential is to be created by the owner as a repository Actions secret in the private repository he creates.

I require:

1. **Owner placement attestation:** the owner confirms that he created the private repository and added the intended NVIDIA credential under the agreed secret name.
2. **Platform configuration evidence:** a GitHub repository-secrets listing or Settings record showing the secret name and its platform timestamps (created/updated), associated with the correct private repository. The secret value must not be exposed. GitHub's secrets API returns secret metadata without revealing encrypted values.
3. **Run-time injection evidence:** the pinned workflow maps that secret through the GitHub `secrets` context to a narrowly scoped environment variable. Before any adapter or model operation, the workflow checks only that the variable is non-empty and records a boolean result such as `credential_injected: true`. It must not print, hash, measure, partially reveal, or otherwise persist the value.
4. **Traceability:** the evidence identifies the repository, workflow run, workflow commit, and pinned adapter/configuration used for that run.

The platform metadata proves that the named secret is configured; the run-time presence check proves that the platform supplied a non-empty value to that workflow run. Neither proves that NVIDIA will accept the credential. Credential validity remains deferred to (c3), the first live use by the separately authorised battery.

**Current interface gap:** the pinned Route 1 adapter at this Shelf revision requires a `credential_path` and reads the credential from a file at call time. It does not currently consume a GitHub Actions secret environment variable directly. Before (c1)/(c2) can pass on Actions, the room must use a pinned Actions-compatible adapter variant that reads the injected environment variable at call time (preferred), or an explicitly reviewed ephemeral-file binding. The raw value must remain absent from logs, captures, and evidence. This is an implementation alignment, not a reason to reverse the venue ruling.

## 4. (c2) Adapter-to-loopback-capture construction — required evidence

This check can and should run inside the Actions workflow before any live call.

I require:

1. The exact pinned Actions adapter variant and effective per-instance configuration are loaded.
2. The adapter is instantiated in its loopback-enforcing mode, with its base URL set to a workflow-local capture service on `127.0.0.1` and an ephemeral port — not the NVIDIA endpoint.
3. A test request is sent through the adapter to that local capture service. The service verifies in memory that:
   - the request reaches the expected completions path;
   - the Authorization header is present and uses the Bearer scheme;
   - the header value matches the injected secret in memory.
4. The capture service records only presence/equality booleans and non-secret request metadata. It must never write the Authorization header or credential value to a log, capture, artifact, or Shelf record.
5. The adapter's own capture is retained and inspected: it identifies the loopback endpoint, records `authorization_attached: true`, carries the expected request/configuration identity, and contains no credential value.
6. The local service returns a deterministic canned response. The workflow records that this was a loopback construction test and that no external request or live model call occurred.

This establishes that the injected credential is wired into the adapter's Bearer header and that the request is captured locally. It does not establish credential validity or outbound HTTPS. Those remain outside (c2).

## 5. Venue-specific preparation still required

Before final preparation acceptance, the complete no-live battery rehearsal must be repeated on GitHub Actions using the pinned room artefacts and production supervisor/launcher/harness/examiner chain. It must reproduce the agreed 13-instance rehearsal against the transport double, with run commitments, captures, ledger, and evidence chain retained. This closes the gap between the host-level probe and the actual governed process tree.

The current `venue-probe.yml` is a probe-result collector, not the battery execution gate: it uses `|| true`, so it does not fail the workflow when the probe reports a negative or unknown verdict. The battery workflow must explicitly stop unless the current runner's probe verdict is `CUSTODY_FEASIBLE`. The probe should be repeated for each fresh runner because Actions builds the room per run.

## 6. Execution boundary

(c3) remains unchanged: the battery itself is the first live use of the credential, and only under the owner's separate execution authority.

This ruling records the venue change and defines the remaining preparation evidence. It does not authorise execution, arming, scheduling, or a live call.

⟦ALEX-FINAL⟧
