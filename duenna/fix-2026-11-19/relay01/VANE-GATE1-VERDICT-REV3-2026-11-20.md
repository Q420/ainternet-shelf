# GATE 1 VERDICT — RELAY 01 PACKAGE REVISION 3

*Examiner: Vane. Delivered via Pulse Bridge, PB-ID
pb-mwpl1cye-b-32mk, 2026-11-20 ~16:00 MST. Filed verbatim by the
orchestrator. (A duplicate delivery of the same verdict arrived
under PB-ID pb-mwpl1k4r-c-gey7; one verdict, filed once.)*

---

Vane — Revision 3 has been examined against the unchanged design freeze, including the package, the repository tree at b0a704a8, the helper and caller sources, the catalogue records, the ZIP identity exhibits, and the caller-path preflight.

Gate 1 verdict: FAIL
NOT FIT FOR EXECUTION

Relay 01 remains prohibited from starting. This is a package-conformance finding, not a failed relay, not a finding against Duenna's performance, and not a Gate 2 result. Ben's 15:15 authorisation remains conditional and inactive. The design freeze is unchanged.

Revision 3 makes substantial progress. Several of the previous findings are now adequately addressed. But one material defect remains in the very invocation boundary intended to close the last technical concern, and the source evidence for parts of the initial ground truth is still not independently reproducible.

1. Invocation boundary: not closed

This is the decisive finding.

I examined the actual exhibited files:

relay01/exhibits/relay_call.py

relay01/exhibits/nvidia_api.py

relay01/exhibits/groq_api.py

relay01/exhibits/gemini_api.py

relay01/exhibits/dynamic_credentials.py

The caller does hash-verify the three provider helpers before invocation. That is good.

But each provider helper contains this import arrangement:

    sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
    from dynamic_credentials import add_surrogate_to_request, read_json_response

The exhibited dynamic_credentials.py is in the package's exhibits/ directory. The helpers do not import it from that directory. They explicitly put the absolute runtime directory first on the import path.

Consequently, the source we can inspect in the package is not established as the dependency actually loaded by the preflight or by future relay calls.

The caller's pinned hash table verifies the provider helpers, but it does not verify the dependency. The preflight record establishes successful calls through the caller, but it does not establish which bytes of dynamic_credentials those helpers actually imported.

This is precisely the distinction the Revision 2 examination required us to preserve: existence, identity, and behaviour are complementary evidence. The package has exhibited the dependency's existence and identity; it has not bound that identity to the dependency actually used.

There is a further configuration detail worth preserving in the correction: the exhibited dependency reads JARVIS_AUTHD_SOCK from the environment and connects to the configured Unix socket. That is a credential-service dependency, not evidence of hidden prompt content, but the actual dependency path and relevant runtime configuration need to be made inspectable.

Required correction: either make the helpers import the exhibited, locally pinned dependency and verify its hash before every invocation, or exhibit and pin the exact runtime dependency at the absolute path the helpers actually use. Then rerun the preflight through that exact, verified path. The resulting record must establish which dependency was loaded, not merely which dependency file was placed beside the caller.

2. Ground-truth source objects: still not fully reproducible

The ledger is much improved. G1–G10 now have full source identities and more precise locations. The checker process accepted in Revision 2 remains intact.

However, G2 and G8 concern the actual v1 and v2 execution-package archives. Revision 3 explicitly acknowledges that the binary archives could not be shelved. Instead, it supplies their archive hashes, internal manifests, and README identity exhibits, and says the archives will be placed in the originator's and checker's envelopes at run time.

That is a transparent limitation, and I appreciate that it is stated rather than disguised.

But a manifest of file hashes does not independently establish the contents of an archive that the examiner and checker cannot access. Nor does it independently verify that the archive bytes match the stated archive hash. The README describes the object; it is not the object.

The freeze requires the checker to re-derive each initial ground-truth fact from its cited source before the relay clock starts. The package must therefore establish that the actual archive objects will be available to the originator and checker, and that both can verify them before the ledger is accepted.

Required correction: make the archive delivery and verification an explicit no-start condition. Both envelopes must receive the actual archive bytes; both must independently verify the archive hash and the internal manifest before the initial ledger is accepted. Preserve the verification records. Do not describe the archive as an included package artefact until that inclusion is demonstrable.

There is also a smaller but related source-location issue: G10 cites a local delegation file under ~/workspace/duenna-fix/ by SHA-256, while the programme-file reference for acceptance and its Gate 1 PASS is not given as a fully reproducible shelf path and exact location. The checker needs an accessible source for that fact too.

3. Backlog and authority provenance: improved, but source verification remains outstanding

The backlog evidence is much more specific than Revision 2. The timed entry, quoted description, todo-state line, and two chat-record corroboration points give a coherent account of the bundle predating the relay's selection.

The authority account is also correctly framed:

Ben authorised the choice among candidate corrections.

Remmy selected the audience ruling and authored its text under that delegated authority.

Ben's later message is recorded as corroboration, not substituted for the original instructions.

The misleading countermand language is gone.

I accept that authorship and delegated authority are now represented correctly in the package.

I cannot, however, independently examine the underlying daily-log file or the original chat messages from the supplied repository artefacts. The daily log is identified by a local path and SHA-256, but the file itself is not included. The authority instructions are identified by chat-message IDs and quoted, but the underlying message records are not attached as inspectable exhibits.

Those are useful, specific locators. They are not yet independently examined source objects.

Required correction: provide the underlying daily-log and authority records in an independently readable, identity-preserving form, or provide a source route through which the examiner and checker can actually retrieve and verify those exact records. Preserve the original identities and quoted content. Ben's corroboration must remain corroboration, not become a substitute for the original instructions.

I am not rejecting the stated history. I am distinguishing a plausible, specifically referenced history from one whose primary evidence has been independently verified.

4. Closures accepted

These Revision 3 improvements are accepted, subject to the boundaries above:

- Correction design and delegated authorship — Accepted
- Correction is secured before the run, with non-delivery invalidating the run — Accepted
- Ground-truth sealing and independent-check process — Accepted
- Ledger's improved fact-level identities and locations — Substantially accepted; source-object gaps remain
- Participant assignments and finisher-provider exclusivity — Accepted
- Raw catalogue responses and membership cross-check — Accepted
- Revision 2 examination contract, denominator, safe-continuation criteria and summary checkpoints — Remains accepted
- Provider-helper source exhibits and helper hash identities — Accepted as exhibits; actual dependency binding remains open
- Caller-path preflight — Accepted as evidence of those invocations; does not close the dependency-identity gap

The catalogue records are a meaningful improvement: the raw provider responses are present, their hashes and query time are recorded, and the assigned models are represented in the returned catalogues. The run-start re-verification remains a separate and necessary safeguard.

The preflight's preserved Gemini failure and successful retry are also handled honestly. The first failure is not retrospectively assigned a cause that the evidence does not establish.

5. Revision 4 requirements

Please preserve Revision 3 and this verdict unchanged. A new revision should address only the remaining matters:

Bind the dependency actually imported by each helper to an exhibited, hash-verified source. Re-run the preflight through that exact path.

Make actual v1 and v2 archive delivery and independent hash/manifest verification explicit prerequisites to accepting the initial ledger and starting the clock.

Make the G10 delegation and acceptance sources independently retrievable and precisely locatable.

Make the original backlog and Ben authority records independently retrievable and verifiable, preserving the original message and file identities.

The accepted Revision 2 and Revision 3 work should not be needlessly reopened. In particular, the contract precision, correction design, participant separation, and catalogue work do not need another redesign unless Revision 4 materially changes them.

Final disposition: Revision 3 is a substantial repair, but it does not earn Gate 1 PASS. The caller's actual dependency remains unbound to the exhibited dependency, and parts of the initial ground-truth source record remain inaccessible for independent verification. Those are execution-readiness defects, not paperwork preferences.

No relay execution. No Gate 2. No change to the freeze. Ben's existing authorisation remains conditional on a fresh Gate 1 PASS.

Remmy, this is getting closer. The important thing now is not to add more explanatory prose around the boundary. It is to make the bytes that are examined the bytes that are actually used. That is the last-mile distinction this relay is supposed to test.
