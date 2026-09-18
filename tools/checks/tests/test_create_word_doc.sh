#!/bin/bash
# Two-direction test for check_create_word_doc.py, built on its own scratch
# fixture (practice: fixture-owns-its-state) rather than assuming a
# particular repo has or lacks the script:
#   1. no tools/create_word_doc.py at all -- require SKIPPED (exit 2), not
#      a pass and not a violation;
#   2. a truncated stand-in (too small, no practice citation) -- require
#      the check to fire and name the specific findings.
set -euo pipefail
cd "$(dirname "$0")/../../.."
SET_ROOT="$(pwd)"
SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT

export PRECEDENT_CHECK_ROOT="$SCRATCH"

set +e
OUT="$(python3 "$SET_ROOT/tools/checks/check_create_word_doc.py")"
CODE=$?
set -e
if [[ $CODE -ne 2 ]] || [[ "$OUT" != SKIPPED:* ]]; then
  echo "FAIL: expected SKIPPED (exit 2) when the script isn't vendored, got exit $CODE: $OUT" >&2
  exit 1
fi
echo "ok: SKIPPED when tools/create_word_doc.py isn't vendored here"

mkdir -p "$SCRATCH/tools"
printf '# not a real script\n' > "$SCRATCH/tools/create_word_doc.py"

OUT="$(python3 "$SET_ROOT/tools/checks/check_create_word_doc.py" || true)"
if ! grep -q "looks truncated" <<<"$OUT"; then
  echo "FAIL: check_create_word_doc.py did not flag the undersized stand-in" >&2
  echo "$OUT" >&2
  exit 1
fi
if ! grep -q "does not cite this practice" <<<"$OUT"; then
  echo "FAIL: check_create_word_doc.py did not flag the missing practice citation" >&2
  echo "$OUT" >&2
  exit 1
fi
echo "ok: fires on an undersized, uncited stand-in script"

cp "$SET_ROOT/tools/create_word_doc.py" "$SCRATCH/tools/create_word_doc.py"
if ! python3 "$SET_ROOT/tools/checks/check_create_word_doc.py" > /dev/null; then
  echo "FAIL: check_create_word_doc.py is not clean on this set's own real script" >&2
  python3 "$SET_ROOT/tools/checks/check_create_word_doc.py" >&2 || true
  exit 1
fi
echo "ok: clean on this set's own real, current tools/create_word_doc.py"
