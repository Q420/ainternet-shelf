# Claude — Independent Inspection of Stage 5 Build Specification Rev 11 (RECOVERED VERBATIM)

**Provenance:** Claude's inspection was returned through Ben in the TerrAIrium
chat on 2026-11-12 (~22:09 MST) and existed only in that chat paste. This file
is that message recovered verbatim from the chat record on 2026-11-13, at
Alex's direction (D-18: recover from an authorised local record; never
reconstruct from summaries). The text below is the relayed message exactly as
recorded, including Claude's narration lines preceding the inspection itself.
Nothing has been edited, condensed, or reworded.

---

I'll start by confirming the pinned commit and the files it names, read-only.

The commit exists and the named files are there. Next I'll check the size and structure of the spec.

The spec is about 190 KB, so I'll read it in sections. I'll start with §1 and §6.3, since §6.3 holds the rulings Ben asked for.

Next I'll map the §3.5 custody section by its subheadings, since it is the largest part of the spec.

The custody design is detailed. Before judging whether it's proportionate, I'll check whether the spec considered simpler spawn mechanisms, and read its stated threat model.

The spec did consider a sudo rule and rejected it. I'll test that rejection against its own stated threat model, along with the gate definitions and the stub and catalogue rulings.

Two more checks: whether the spec's key terms match the verified design package, and whether the setuid launcher's language is consistent with the Python default.

# Independent inspection: STAGE5-BUILD-SPEC-11 (Rev 11)

**Scope of my read.** I read the pinned commit `ce74026c` (`duenna/`). I went through §6.3, the custody design's threat model and its rejected alternatives, the G1–G2 gates, §3.7 (stub and transport double), the catalogue listing, and the batch order. I also spot-checked that the design package's key terms carry into the spec, including the four extraction outcomes. I have not read all 190 KB or every design-package line, so §3.1–3.4, §3.6 and §4 are less checked than the custody and gate sections. Treat this as a substantial partial inspection, not a full one.

**Fidelity.** The spec carries the design faithfully at the level I checked. START/TERMINAL/CRASH, the four outcomes (NOT FOUND, TYPE FAILURE, AMBIGUOUS, FOUND) and SE-7 all match the design package. The torn-write requirement is stated precisely.

## Findings by severity

**High**

1. **The no-model-call rule is stated, not enforced.** Spec §3.7 says Stage 5 makes "no call to `integrate.api.nvidia.com` chat completions." Nothing in the build stops the adapter from reaching the live endpoint. The base URL is not required to be loopback in Stage 5, and no gate proves zero outbound connections to the provider host. A misconfigured run could contact the live endpoint and the gates would still pass. *Fix:* in Stage 5 mode the adapter refuses any non-loopback base URL; the build environment holds no provider credential; and gate G1 records a zero-egress check (for example, a network namespace with no route out).

2. **The catalogue listing contradicts the Stage 5 intent.** §6.3 item 5 proposes a live `GET /v1/models` through the connector as the default freeze evidence. That is an authenticated request to the provider's live host. The no-call wording names only chat completions, so the listing passes the letter of the rule while contacting the provider. Section 3.7 also says the transport double is used "never against the live endpoint." *Ruling: strike the default and take the fallback* (carry the design-time snapshot, re-evidence at Stage 6 pre-flight).

3. **The launcher's language conflicts with the Python default.** §6.3 item 4 makes Python the default and requires an inspector-approved amendment for any other language. The launcher, though, is a setuid-root binary that uses `fork()`, `PR_SET_PDEATHSIG` and `waitpid()`, and the spec says it is "compiled at build time." On Linux the setuid bit is ignored on interpreted scripts, so this launcher cannot be Python. The spec never names its language or flags it as an amendment. *Fix:* name the launcher's language explicitly and record it as the approved exception to item 4.

**Medium**

4. **The sudo rejection doesn't hold on its own stated reasoning.** Spec §3.5 point 2(iv) rejects a sudo rule because it "leave[s] a standing privilege rule invocable outside any run." Mode `4710` with group `pilot-supervisor` is also a standing privilege, invocable by that identity at any time. The real difference is that the launcher is custom root code, which is a larger trusted base than a narrow, fixed sudoers entry. The choice may still be right, but the justification should say that. *Ruling on §6.3 item 1:* accept the two-identity custody design; amend the rationale. An inspector who prefers a sudoers entry can strike the launcher and still keep everything else in §3.5.

5. **The launcher's source is frozen late.** It is pinned only at the Batch 4 checkpoint, after Batches 0–3 have been built on top of the custody assumption. *Fix:* freeze the launcher's required behaviour and interface at Batch 0, so the target exists before anything depends on it.

6. **The torn-write fault injector must not ship.** The test-only slow/partial write path is needed for G2, but nothing in the spec stops it from reaching the production build. *Fix:* a build-time flag that refuses to compile it outside the scratch context, with the flag state recorded in gate evidence.

**Low**

7. **Stub labelling needs checking in the record.** §3.7 requires every stub artefact to be labelled. The label should be a field in the canonical record, not just a filename convention. I did not verify which one the spec specifies.

8. **RFC 8785 needs a pinned implementation.** The spec pins the standard but I did not find a pinned library or version for the Python implementation. This is unverified.

## Rulings on the §6.3 proposals

| Item | Ruling | Reason |
|---|---|---|
| 1. Supervisor form | **Accept with amendment** | Custody design sound; amend the sudo rationale (finding 4) and freeze the launcher at Batch 0 (finding 5). |
| 2. Stub and transport double | **Accept with amendment** | Add the loopback enforcement and zero-egress check (finding 1). |
| 3. RFC 8785 | **Accept** | Pin the implementation version as a condition of acceptance (finding 8). |
| 4. Python | **Accept with amendment** | Record the launcher as the approved non-Python exception (finding 3). |
| 5. Catalogue listing | **Strike the default; accept the fallback** | Live provider contact is not Stage 5 work (finding 2). |

## Gaps the build would trip over

- **Account and group setup is operator work, and the spec doesn't say how it is evidenced.** SE-7(vii) reads the group state from the OS, which is good. But the creation of the two accounts, the group memberships and the launcher's permissions is a manual step with no recorded artefact. A script or a recorded transcript of that step belongs in Batch 0.
- **Batch 0 needs an explicit go/no-go for the launcher probe.** The probe needs root on the build machine. The spec says the build stops if it fails, but doesn't say who runs it or where its output goes.

## Position

**Fit to build from: not yet.** Findings 1–3 need amendments before dispatch. Findings 4–6 are necessary, but the build could start on everything else. Once the five rulings are amended and findings 1–3 are closed, I'd consider the spec buildable. Stage 6 stays unauthorised regardless, as the commission says.

I'm not pushing anything, and the hook is wrong again. The remote branch `claude-review-bench` is at `756cdf1`, which matches my local HEAD, so there are no unpushed commits. The review I just gave you is in chat and hasn't been filed to the shelf.
