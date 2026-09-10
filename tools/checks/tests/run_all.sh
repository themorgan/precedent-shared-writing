#!/bin/bash
# Runs every check's multi-direction test. Exits non-zero if any test fails.
#
# Two suites carry cases that need a real precedent_resolve.py, which is not
# vendored here (see TODO.md's engine-cases-need-a-bestpractice-clone item).
# Point PRECEDENT_BESTPRACTICE_CLONE at a BestPractice clone to run them,
# and add PRECEDENT_REQUIRE_ENGINE_CASES=1 to make skipping them a failure:
#
#   PRECEDENT_BESTPRACTICE_CLONE=../BestPractice \
#     PRECEDENT_REQUIRE_ENGINE_CASES=1 bash tools/checks/tests/run_all.sh
set -uo pipefail
cd "$(dirname "$0")"
status=0
for t in test_*.sh; do
  echo "--- $t ---"
  if ! bash "$t"; then
    status=1
  fi
done
exit $status
