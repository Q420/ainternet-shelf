#!/bin/bash
# BATCH 0 RE-RUN — Stage 5 build, Nemotron pilot (Spec Rev 13 at pin bab720b2, section 4).
# Runs INSIDE the Ubuntu room on Ben's laptop, as wsl root.
# The frozen Batch 0 artefacts arrive byte-identical (manifest-verified at Step 1);
# the environment-dependent items execute here. Evidence only — the checkpoint
# verdict is Remmy's report from this transcript. A failed check never triggers
# a fallback; it is recorded and the checkpoint fails.
exec > >(tee -a /home/ben/batch0-rerun.log) 2>&1
set -u
STAGE=/mnt/c/Users/ben
ROOT=/srv/nemotron-pilot
FAIL=0
exp() { grep "^$1 " "$STAGE/expected-hashes.txt" | cut -d' ' -f2; }
chk() { # chk <file> <expected> <label>
  local got; got=$(sha256sum "$1" 2>/dev/null | cut -d' ' -f1)
  echo "$3: got $got / expected $2"
  if [ "$got" = "$2" ]; then echo "[$3] PASS"; else echo "[$3] FAIL"; FAIL=1; fi
}
banner() { echo; echo "===== $* ====="; }

banner "BATCH 0 RE-RUN — Nemotron pilot, Ubuntu room on Ben's laptop"
date; hostname; uname -r; systemd-detect-virt || true

if ! command -v python3 >/dev/null; then
  echo "python3 not present — installing (disclosed prep, same class as the probe's gcc)"
  apt-get update -qq && apt-get install -y python3 || { echo "[prep] FAIL python3"; FAIL=1; }
fi
command -v gcc >/dev/null || { echo "gcc not present — installing (disclosed prep)"; apt-get install -y gcc libc6-dev; }

banner "STEP 1 — frozen artefacts staged and verified byte-identical"
mkdir -p "$ROOT/freeze" "$ROOT/rerun-evidence" "$ROOT/probe"
tar -xf "$STAGE/freeze.tar" -C "$ROOT/freeze"
cp "$STAGE/expected-hashes.txt" "$STAGE/freeze-manifest.sha256" "$STAGE/batch0-rerun.sh" "$ROOT/rerun-evidence/"
if (cd "$ROOT/freeze" && sha256sum -c "$STAGE/freeze-manifest.sha256"); then
  echo "[artefacts] PASS — every staged freeze file byte-identical to the VM originals"
else
  echo "[artefacts] FAIL — a staged artefact differs; per spec section 4 this stops the build"
  FAIL=1
fi

banner "STEP 2 — the governing spec, at its pin"
cp "$STAGE/STAGE5-BUILD-SPEC-13.md" "$ROOT/STAGE5-BUILD-SPEC-13.md"
chk "$ROOT/STAGE5-BUILD-SPEC-13.md" "$(exp SPEC)" "spec-rev13"

banner "STEP 3 — corpus snapshot verification (the freeze's own verifier, in-room)"
cd "$ROOT/freeze/PILOT-CORPUS-SNAPSHOT-01"
chk sections.jsonl "$(exp SECTIONS)" "corpus-sections-pin"
chk manifest.json "$(exp MANIFESTJSON)" "corpus-manifest-pin"
OUT=$(python3 verify_snapshot.py 2>&1); echo "$OUT"
if echo "$OUT" | grep -q '"all_sections_verified": true' \
   && echo "$OUT" | grep -q '"sections_file_pin_match": true' \
   && echo "$OUT" | grep -q '"manifest_file_pin_match": true'; then
  echo "[snapshot] PASS — pins equal; every section hash and document chain recomputes in-room"
else
  echo "[snapshot] FAIL — corpus pin mismatch stops the build (spec section 4)"; FAIL=1
fi

banner "STEP 4 — PILOT-JCS conformance re-run (frozen implementation, frozen runner)"
mkdir -p /root/workspace/snapshotter/snapshots/snap-live-rfc8785/page-001
cp "$STAGE/rfc8785-text.md" /root/workspace/snapshotter/snapshots/snap-live-rfc8785/page-001/text.md
chk /root/workspace/snapshotter/snapshots/snap-live-rfc8785/page-001/text.md "$(exp RFCTEXT)" "rfc8785-source"
chk "$ROOT/freeze/jcs/pilot_jcs.py" "$(exp JCSIMPL)" "pilot-jcs-source"
cp "$ROOT/freeze/jcs/jcs-conformance-results.json" "$ROOT/freeze/jcs/rfc8785-test-vectors.json" "$ROOT/rerun-evidence/"
cd "$ROOT/freeze/jcs"
python3 run_conformance.py; RC=$?
echo "conformance exit code: $RC"
if [ "$RC" = 0 ] && grep -q '"all_pass": true' jcs-conformance-results.json; then
  echo "[jcs] PASS — conformance re-executed in-room, all vectors pass"
else
  echo "[jcs] FAIL"; FAIL=1
fi
if diff -q "$ROOT/rerun-evidence/jcs-conformance-results.json" jcs-conformance-results.json >/dev/null; then
  echo "[jcs-results] regenerated results byte-identical to the frozen results"
else
  echo "[jcs-results] NOTE — regenerated results differ from the frozen file (see diff in evidence)"
  diff "$ROOT/rerun-evidence/jcs-conformance-results.json" jcs-conformance-results.json | head -10
fi

banner "STEP 5 — adapter configuration freeze (post-F-2 standing state)"
chk "$ROOT/freeze/adapter-config.canonical.json" "$(exp ADAPTERORIG)" "adapter-config-original(historical)"
chk "$ROOT/freeze/adapter-config-f2-2026-11-12.canonical.json" "$(exp ADAPTERF2)" "adapter-config-f2(standing)"

banner "STEP 6 — launcher interface freeze, A-1 amendment, F-2 disposition on record"
chk "$ROOT/freeze/launcher-interface-freeze.md" "$(exp LAUNCHERFREEZE)" "launcher-interface-freeze"
ls -la "$ROOT/freeze/A1-AMENDMENT-RUN-IDENTIFIER-GRAMMAR-2026-11-12.md" "$ROOT/freeze/F2-DISPOSITION-2026-11-12.md"

banner "STEP 7 — custody identities, read from the operating system"
for u in pilot-supervisor pilot-harness; do
  if id "$u" >/dev/null 2>&1; then
    echo "$u: $(id "$u") — pre-existing (created by the acceptance probe), verified from the OS"
  else
    echo "$u MISSING — creating now with the probe's shape (this creation is on this transcript)"
    groupadd "$u" 2>/dev/null; useradd -M -g "$u" -s /usr/sbin/nologin "$u"; id "$u"
  fi
done
getent passwd pilot-supervisor pilot-harness

banner "STEP 8 — custody trees under the build root (the F-3 test, in its real form)"
mkdir -p "$ROOT/runs" "$ROOT/commitments"
chown pilot-harness:pilot-harness "$ROOT/runs"; chmod 755 "$ROOT/runs"
chown pilot-supervisor:pilot-supervisor "$ROOT/commitments"; chmod 700 "$ROOT/commitments"
stat -c '%U:%G %a %n' "$ROOT" "$ROOT/runs" "$ROOT/commitments"
if runuser -u pilot-harness -- test -r "$ROOT/commitments"; then echo "[separation] FAIL — harness READ supervisor custody"; FAIL=1; else echo "[separation] harness read on commitments: DENIED (expected)"; fi
if runuser -u pilot-harness -- bash -c "echo x > $ROOT/commitments/.wtest" 2>/dev/null; then echo "[separation] FAIL — harness WROTE supervisor custody"; rm -f "$ROOT/commitments/.wtest"; FAIL=1; else echo "[separation] harness write on commitments: DENIED (expected)"; fi
if runuser -u pilot-supervisor -- test -r "$ROOT/commitments"; then echo "[separation] supervisor reads its own custody: OK"; else echo "[separation] FAIL — supervisor cannot read its own custody"; FAIL=1; fi
if runuser -u pilot-harness -- bash -c "touch $ROOT/runs/.wtest && rm $ROOT/runs/.wtest"; then echo "[separation] harness works in its own runs tree: OK"; else echo "[separation] FAIL — harness cannot use its own tree"; FAIL=1; fi

banner "STEP 9 — launcher environment probe (frozen source, the F-1 test, in its real form)"
chk "$ROOT/freeze/probe/setuid_probe.c" "$(exp PROBESRC)" "probe-source"
gcc -O2 -o "$ROOT/probe/setuid-probe" "$ROOT/freeze/probe/setuid_probe.c"
chown root:pilot-supervisor "$ROOT/probe/setuid-probe"; chmod 4710 "$ROOT/probe/setuid-probe"
stat -c '%U:%G %a %n' "$ROOT/probe/setuid-probe"
echo "mount options for the build root's filesystem:"; findmnt -T "$ROOT" -no TARGET,OPTIONS
echo "NoNewPrivs — PID 1: $(grep NoNewPrivs /proc/1/status) | this shell: $(grep NoNewPrivs /proc/self/status)"
echo "--- invocation A: as pilot-supervisor (the privileged window must open) ---"
runuser -u pilot-supervisor -- "$ROOT/probe/setuid-probe"; echo "invocation A exit: $?"
echo "--- invocation B: as pilot-harness (must be refused) ---"
runuser -u pilot-harness -- "$ROOT/probe/setuid-probe" 2>&1; echo "invocation B exit: $?"

banner "STEP 10 — G1 zero-egress evidence, Batch 0's part (this room, as it stands)"
ip -brief address; ip route
env | grep -i proxy || echo "(no proxy variables in this environment)"
findmnt -no TARGET,OPTIONS / | head -2
echo "Honest reading, same as Batch 0: the room as it stands is NOT zero-egress"
echo "(WSL NAT default route exists); a loopback-only namespace is constructible"
echo "(proven in the acceptance probe). Batch 0 pre-passes nothing of G1."

banner "EVIDENCE COMPLETE"
if [ "$FAIL" = 0 ]; then
  echo "ALL SCRIPTED CHECKS PASSED. The checkpoint verdict is Remmy's report from this transcript."
else
  echo "ONE OR MORE CHECKS FAILED — see the [FAIL] lines above. Per spec, the build stops; no fallback taken."
fi
date
