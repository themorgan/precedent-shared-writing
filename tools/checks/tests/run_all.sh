#!/bin/bash
# Runs every check's two-direction test. Exits non-zero if any test fails.
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
