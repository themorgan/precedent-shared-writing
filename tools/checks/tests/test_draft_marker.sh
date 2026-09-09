#!/bin/bash
# Two-direction test for check_draft_marker.py:
#   1. plant a live draft marker in a scratch copy -- require the check to fire;
#   2. the real, current, unplanted repo -- require the check to stay clean.
# Also confirms the check does NOT fire on the marker's own illustration
# inside backtick code, the way the practice file itself uses it.
set -euo pipefail
cd "$(dirname "$0")/../../.."
ROOT="$(pwd)"
SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT

git clone -q "$ROOT" "$SCRATCH"
cd "$SCRATCH"
cat > planted-draft.md <<'EOF'
# A document

Some finished prose here.

**➡️ FILL IN THE NUMBERS ONCE FINANCE CONFIRMS THEM ⬅️**

More finished prose.
EOF
git add planted-draft.md
git -c user.name="Test" -c user.email="test@example.com" commit -q -m "planted violation: leftover draft marker"

if python3 tools/checks/check_draft_marker.py > /dev/null; then
  echo "FAIL: check_draft_marker.py did not fire on a planted live marker" >&2
  exit 1
fi
echo "ok: fires on planted violation"

cd "$ROOT"
if ! python3 tools/checks/check_draft_marker.py > /dev/null; then
  echo "FAIL: check_draft_marker.py is not clean on the real, current repo" >&2
  exit 1
fi
echo "ok: clean on real content (including the practice file's own backtick-quoted illustration)"
