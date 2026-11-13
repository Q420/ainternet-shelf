#!/bin/bash
# Nemotron pilot — custody setup (Stage 5 Build Spec §3.5 point 1).
#
# Batch 0 freeze artefact (Spec §4, "Custody setup evidence"): this script
# is how the custody state came to be. It creates the two OS identities
# and the custody trees exactly as §3.5 point 1 specifies:
#
#   * pilot-harness     — owns and runs the harness, the tools, the
#                         adapter, and the run directories (runs/).
#   * pilot-supervisor  — owns the supervisor program and commitments/.
#   * commitments/ is mode 0700, owned by pilot-supervisor, so
#     pilot-harness has no write, no create, no delete, and no read
#     on receipts or the issuance record.
#   * Group separation (§3.5 point 1, Rev 03): pilot-harness is NOT a
#     member of the pilot-supervisor group; pilot-supervisor is NOT a
#     member of any group conferring pilot-harness privilege. Each
#     account gets only its own primary group.
#
# Operator work, run as root. Idempotent: existing accounts and trees
# are verified, not recreated. No other accounts, groups, or paths
# are touched.
set -u

BUILD_ROOT=/home/hatch/workspace/nemotron-pilot

echo "== custody setup: accounts =="
if id pilot-harness >/dev/null 2>&1; then
    echo "pilot-harness already exists:"
    id pilot-harness
else
    useradd --system --no-create-home --shell /usr/sbin/nologin \
        --user-group pilot-harness
    echo "created pilot-harness:"
    id pilot-harness
fi
if id pilot-supervisor >/dev/null 2>&1; then
    echo "pilot-supervisor already exists:"
    id pilot-supervisor
else
    useradd --system --no-create-home --shell /usr/sbin/nologin \
        --user-group pilot-supervisor
    echo "created pilot-supervisor:"
    id pilot-supervisor
fi

echo "== custody setup: trees =="
mkdir -p "$BUILD_ROOT/runs" "$BUILD_ROOT/commitments"
chown pilot-harness:pilot-harness "$BUILD_ROOT/runs"
chown pilot-supervisor:pilot-supervisor "$BUILD_ROOT/commitments"
chmod 0700 "$BUILD_ROOT/commitments"
echo "trees set:"
stat -c '%U:%G %a %n' "$BUILD_ROOT/runs" "$BUILD_ROOT/commitments"

echo "== custody setup: group separation read-back (from the OS) =="
getent group pilot-harness pilot-supervisor
echo "pilot-harness memberships:    $(id -Gn pilot-harness)"
echo "pilot-supervisor memberships: $(id -Gn pilot-supervisor)"
echo "== custody setup: done =="
