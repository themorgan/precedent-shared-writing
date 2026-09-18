#!/bin/bash
# Three-direction test for check_curly_quotes.py. This set itself declares
# no output_paths (see check_deliverables_carry_no_process.py's own
# comment), so the check has nothing to scan here -- the fixture owns its
# own scope instead of borrowing this repo's (practice: fixture-owns-its-
# state): a scratch git repo with its own precedent.json declaring one
# output_path and one grandfathered file, built fresh so nothing here is
# inherited or assumed.
#
#   1. plant a straight quote in a fresh, non-grandfathered file under the
#      declared output_path -- require the check to fire, and to name that
#      file (control-asserts-which-failure: a non-zero exit alone is not
#      evidence the right thing tripped);
#   2. plant a straight quote into the declared-grandfathered file --
#      require the check to stay quiet, proving the exemption actually
#      exempts;
#   3. the fixture's starting state -- require the check to stay clean.
set -euo pipefail
cd "$(dirname "$0")/../../.."
SET_ROOT="$(pwd)"
SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT

cd "$SCRATCH"
export PRECEDENT_CHECK_ROOT="$SCRATCH"
git init -q
git config user.name "Test"
git config user.email "test@example.com"

mkdir -p output
cat > precedent.json <<'EOF'
{
  "output_paths": ["output"],
  "internal_paths": [],
  "curly_quotes_grandfathered": ["output/GRANDFATHERED.md"]
}
EOF
printf '# Grandfathered\n\nA "straight-quoted" sentence, present from the start.\n' > output/GRANDFATHERED.md
git add precedent.json output/GRANDFATHERED.md
git commit -q -m "fixture: declared output_path, one grandfathered file"

if ! python3 "$SET_ROOT/tools/checks/check_curly_quotes.py" > /dev/null; then
  echo "FAIL: check_curly_quotes.py is not clean on the fixture's starting state" >&2
  python3 "$SET_ROOT/tools/checks/check_curly_quotes.py" >&2 || true
  exit 1
fi
echo "ok: clean on the fixture's starting state (its one violation is grandfathered)"

printf '# Planted\n\nA "straight-quoted" sentence.\n' > output/PLANTED_TEST.md
git add output/PLANTED_TEST.md
git commit -q -m "planted violation: a fresh, non-grandfathered file"

OUT="$(python3 "$SET_ROOT/tools/checks/check_curly_quotes.py" || true)"
if ! grep -q "output/PLANTED_TEST.md" <<<"$OUT"; then
  echo "FAIL: check_curly_quotes.py did not report the planted file" >&2
  echo "$OUT" >&2
  exit 1
fi
echo "ok: fires on a straight quote in a fresh, non-grandfathered file"

git rm -q output/PLANTED_TEST.md
git commit -q -m "revert planted file"

printf '\n\nA second "straight-quoted" addition.\n' >> output/GRANDFATHERED.md
git commit -q -am "planted violation: a straight quote in the grandfathered file"

OUT="$(python3 "$SET_ROOT/tools/checks/check_curly_quotes.py" || true)"
if grep -q "output/GRANDFATHERED.md" <<<"$OUT"; then
  echo "FAIL: check_curly_quotes.py fired on a grandfathered file" >&2
  echo "$OUT" >&2
  exit 1
fi
echo "ok: stays quiet on a straight quote in a declared-grandfathered file"
