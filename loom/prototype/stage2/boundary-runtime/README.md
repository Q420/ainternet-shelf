# Boundary runtime — where it actually lives, and why

The two-OS-context boundary runtime (fabric service as `loomfab`,
agent processes as `loomagent`) cannot live in this directory: the
workspace filesystem denies `chown` to the build sandbox (EPERM —
the workspace sits on an overlay outside the sandbox's capability
set; verified by direct experiment 2026-11-21), so no ownership
boundary can exist on files here.

The runtime therefore lives on tmpfs at `/tmp/loom-boundary-runtime`
(`experimental/`, `twin/`, `faulttest/`), where ownership and
permissions are enforceable — also verified by direct experiment
before the build. Runtimes are disposable: `fabric/runtime_setup.py`
rebuilds them from the tree on every test run.

This directory holds the durable record: `RUNTIME-EVIDENCE.json`,
rewritten by `stage2_corrections_tests.py` on each run (layout
stat records, probe outcomes, the unrecordable-failure diagnostic).
Full account: `../STAGE2-CORRECTIONS-NOTES.md`.
