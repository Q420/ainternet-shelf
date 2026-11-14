#!/bin/bash
bash /mnt/c/Users/ben/b4c/stage_build.sh > /srv/nemotron-pilot/batch4/test-logs/build.log 2>&1
echo "BUILD TAIL:"; tail -8 /srv/nemotron-pilot/batch4/test-logs/build.log
python3 /srv/nemotron-pilot/batch4/test-src/test_launcher.py > /srv/nemotron-pilot/batch4/test-logs/peer.log 2>&1
echo "PEER EXIT: $?"
cat /srv/nemotron-pilot/batch4/test-logs/peer.log
