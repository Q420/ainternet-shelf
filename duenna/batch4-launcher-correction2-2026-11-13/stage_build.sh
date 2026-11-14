#!/bin/bash
set -x
B=/srv/nemotron-pilot/batch4
mkdir -p $B/test $B/test-src $B/test-results $B/test-hooks $B/test-logs /srv/nemotron-pilot/test-hooks
cp /mnt/c/Users/ben/b4c/launcher.c /mnt/c/Users/ben/b4c/unit_test.c /mnt/c/Users/ben/b4c/test_harness.c /mnt/c/Users/ben/b4c/test_launcher.py /mnt/c/Users/ben/b4c/gen_identity_records.sh /mnt/c/Users/ben/b4c/identity_records.h $B/test-src/
chown -R pilot-harness:pilot-harness $B/test-results
chown -R pilot-supervisor:pilot-supervisor $B/test-hooks
cd $B/test-src
# helper (the exec target of the test build)
gcc -std=c11 -O2 -Wall -Wextra -Werror -o $B/test/test-harness test_harness.c || exit 11
chmod 755 $B/test/test-harness
# identity records for the test build (helper as both entries)
bash gen_identity_records.sh $B/test/test-harness $B/test/test-harness $B/test/identity_records.h || exit 12
grep -c "0u, 0u" $B/test/identity_records.h || true
# production compile check (committed zero-placeholder header)
gcc -std=c11 -O2 -Wall -Wextra -Werror -c launcher.c -o /tmp/prod.o || exit 13
# test build: the quote-include resolves identity_records.h beside
# launcher.c first, so stage the generated header there, build, restore
cp identity_records.h identity_records.zero.h
cp $B/test/identity_records.h identity_records.h
gcc -std=c11 -O2 -Wall -Wextra -Werror -DPILOT_TEST_HOOKS -DHARNESS_PATH="\"$B/test/test-harness\"" -o $B/test/launcher-test launcher.c || exit 14
cp identity_records.zero.h identity_records.h
# unit suite under ASan/UBSan
gcc -std=c11 -O1 -g -fsanitize=address,undefined -DPILOT_TEST_HOOKS -o $B/test/unit-test unit_test.c || exit 15
$B/test/unit-test; echo "UNIT EXIT: $?"
