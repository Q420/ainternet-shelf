#!/usr/bin/env python3
"""Generate test_launcher_c3.py from test_launcher_c2.py,
implementing chunk C3-2: a "cloexec-sabotage" placement
mode whose read-back genuinely fails (placement and
clear performed, FD_CLOEXEC then deliberately re-set),
plus a peer case asserting the supervisor-side
rejection happens BEFORE exec (helper exit 91, no
handoff, harness never executed). The raw case stays,
relabelled in its comment as the launcher-precondition
case it is. Replacements are count-checked."""
import hashlib, sys

SRC = "test_launcher_c2.py"
DST = "test_launcher_c3.py"

text = open(SRC).read()

def rep(old, new, want=1):
    global text
    n = text.count(old)
    if n != want:
        sys.exit(f"count {n} != {want} for: {old[:60]!r}")
    text = text.replace(old, new)

rep('negative case; exec drops the descriptor."""',
    'negative case; exec drops the descriptor.\n'
    '        mode "cloexec-sabotage": placement and clear\n'
    '        performed, then FD_CLOEXEC deliberately re-set;\n'
    '        the read-back must observe it and reject\n'
    '        pre-exec (exit 91)."""')
rep('if mode in ("cloexec", "cloexec-raw") and src != target:',
    'if mode in ("cloexec", "cloexec-raw", "cloexec-sabotage") and src != target:')
rep('        rb = libc.fcntl(target, F_GETFD)\n'
    '        if rb < 0 or (rb & FD_CLOEXEC):\n'
    '            os._exit(91)',
    '        if mode == "cloexec-sabotage":\n'
    '            cur = libc.fcntl(target, F_GETFD)\n'
    '            if cur < 0 or libc.fcntl(target, F_SETFD, cur | FD_CLOEXEC) != 0:\n'
    '                os._exit(91)\n'
    '        rb = libc.fcntl(target, F_GETFD)\n'
    '        if rb < 0 or (rb & FD_CLOEXEC):\n'
    '            os._exit(91)')
rep('"raw": "cloexec-raw"}[case]',
    '"raw": "cloexec-raw",\n                            "sabotage": "cloexec-sabotage"}[case]')
rep('# negative raw form (clear skipped on fd 4: exec drops it).',
    '# negative raw form (clear skipped on fd 4: exec drops it;\n'
    '# a LAUNCHER-precondition case — renamed as such by C3).')
rep('\nprint(f"peer: {total - fails}/{total} PASS")',
    '\n# ---------------- C3: supervisor-side verification failure (K6/K7g) ----------------\n'
    '# The sabotage form performs placement and the F_SETFD\n'
    '# clear, then deliberately re-sets FD_CLOEXEC; the stub\n'
    '# procedure\'s own F_GETFD read-back must observe it and\n'
    '# reject the launch BEFORE exec (helper exit 91). The\n'
    '# launcher never runs: no exit 13, no handoff, no\n'
    '# result file.\n'
    'rid = "PEERC3SAB-20261114-001"\n'
    'p = Peer(rid, spawn_mode="fork", cloexec_case="sabotage")\n'
    'st = p.wait_exit()\n'
    'chk("C3 sabotage: supervisor verification rejected the launch pre-exec (exit 91)",\n'
    '    exited(st) and exit_code(st) == 91, f"status {st:#x}")\n'
    'chk("C3 sabotage: no handoff (the launcher never ran)", p.handoff() is None)\n'
    'chk("C3 sabotage: harness never executed", not os.path.exists(result_path(rid)))\n'
    'p.close()\n'
    '\nprint(f"peer: {total - fails}/{total} PASS")')

open(DST, "w").write(text)
print(f"{DST}: {len(text.splitlines())} lines, "
      f"sha256 {hashlib.sha256(text.encode()).hexdigest()}")
