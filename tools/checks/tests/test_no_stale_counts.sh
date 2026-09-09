#!/bin/bash

# A fixture commit is not a person's commit: the global commit backstop
# (commit-identity.sh, 2026-09-07) reaches the throwaway repositories
# this test builds and would refuse them.
export PRECEDENT_ALLOW_ANY_AUTHOR=1
# Two-direction test for check_no_stale_counts.py:
#   1. plant a wrong "<N> practices" count in a tracked markdown file --
#      require the check to fire;
#   2. the real, current, unplanted repo -- require the check to stay clean.
set -euo pipefail
cd "$(dirname "$0")/../../.."
ROOT="$(pwd)"
SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT

git clone -q "$ROOT" "$SCRATCH"
cd "$SCRATCH"
echo "" >> README.md
echo "This set has 999 practices, definitely not the real count." >> README.md
git add README.md
git -c user.name="Test" -c user.email="test@example.com" commit -q -m "planted violation: wrong practice count"

if python3 tools/checks/check_no_stale_counts.py > /dev/null; then
  echo "FAIL: check_no_stale_counts.py did not fire on a planted wrong count" >&2
  exit 1
fi
echo "ok: fires on planted violation"

cd "$ROOT"
if ! python3 tools/checks/check_no_stale_counts.py > /dev/null; then
  echo "FAIL: check_no_stale_counts.py is not clean on the real, current repo (including its own 40-practices line)" >&2
  exit 1
fi
echo "ok: clean on real content"

# 3. the same planted violation, but inside a path this repo mirrors and may
#    not hand-edit -- require the check to stay SILENT. Added 2026-09-06,
#    when a consuming repo's run reported dozens of violations that were all
#    inside its byte-identical vendored copy of upstream's own prose: real
#    findings, but not actionable where reported, and loud enough to bury
#    the ones that were. The mirror is declared by process/manifest.json's
#    own upstream.vendored_at -- nothing here is hardcoded.
SCRATCH2="$(mktemp -d)"
trap 'rm -rf "$SCRATCH" "$SCRATCH2"' EXIT
git clone -q "$ROOT" "$SCRATCH2"
cd "$SCRATCH2"
mkdir -p process/upstream
cat > process/manifest.json <<'JSON'
{"upstream": {"repo": "https://example.invalid/upstream", "vendored_at": "process/upstream", "commit": "0000000000000000000000000000000000000000"}}
JSON
echo "This mirrored copy claims 999 practices, which is not the real count." > process/upstream/MIRRORED.md
git add process/manifest.json process/upstream/MIRRORED.md
git -c user.name="Test" -c user.email="test@example.com" commit -q -m "planted violation inside the declared mirror"

if ! python3 tools/checks/check_no_stale_counts.py > /dev/null; then
  echo "FAIL: check_no_stale_counts.py fired on a violation inside the declared vendored mirror, which this repo may not hand-edit" >&2
  exit 1
fi
echo "ok: silent on a violation inside a declared mirror"
