#!/bin/bash

# A fixture commit is not a person's commit: the global commit backstop
# (commit-identity.sh, 2026-09-07) reaches the throwaway repositories
# this test builds and would refuse them.
export PRECEDENT_ALLOW_ANY_AUTHOR=1
# Two-direction test for check_assorted_notes.py:
#   1. plant the exact violation in a scratch copy -- require the check to fire;
#   2. plant a NON-violation -- a link to a filename that merely ENDS the
#      same way (MARKETING_IDEAS.md, RANDOM_NOTES.md) -- require the check
#      to stay clean (real incident: a substring match on the link target
#      flagged these purely for ending in IDEAS.md/NOTES.md);
#   3. plant a listing-document link -- a README.md and a MAP.md, each
#      linking to ASSORTED_NOTES.md -- require the check to stay clean
#      (the 2026-09-05 revision's whole point: a directory listing may
#      link to it; only a citation of its content may not);
#   4. plant a "## See also" link to ASSORTED_NOTES.md in an ordinary
#      page, alongside an ordinary (non-exempt) link to it earlier in
#      the same file -- require the check to fire on the ordinary link
#      but not on the See also one;
#   5. the real, current, unplanted repo -- require the check to stay clean.
#   Later cases, each with its own comment: the migration once
#   ASSORTED_NOTES.md exists, a catch-all outside content/, a headline-cased
#   See Also, and a link whose text is the notes file's own name or path.
set -euo pipefail
cd "$(dirname "$0")/../../.."
ROOT="$(pwd)"
SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT

git clone -q "$ROOT" "$SCRATCH"
cd "$SCRATCH"
git config user.name "Fixture Author"
git config user.email "fixture@example.com"
mkdir -p content
echo "whatever is on my mind" > content/ASSORTED_NOTES.md
mkdir -p docs
echo "See [the notes](../content/ASSORTED_NOTES.md) for why." > docs/planted-reference.md
git add content/ASSORTED_NOTES.md docs/planted-reference.md
git commit -q -m "planted violation: a doc links to ASSORTED_NOTES.md"

# Exit 1 exactly: a missing or crashing script (2) is not "fired".
if [ "$(python3 tools/checks/check_assorted_notes.py > /dev/null 2>&1; echo $?)" != 1 ]; then
  echo "FAIL: check_assorted_notes.py did not fire on a planted reference" >&2
  exit 1
fi
echo "ok: fires on planted violation"

cd "$ROOT"
SCRATCH2="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH2"
(
  cd "$SCRATCH2"
  git config user.name "Fixture Author"
  git config user.email "fixture@example.com"
  mkdir -p content
  echo "marketing copy" > content/MARKETING_IDEAS.md
  echo "loose thoughts" > content/RANDOM_NOTES.md
  mkdir -p docs
  cat > docs/planted-non-reference.md <<'EOF'
Real links, to real files that just happen to end the same way:
[marketing](../content/MARKETING_IDEAS.md) and [notes](../content/RANDOM_NOTES.md).
EOF
  git add content/MARKETING_IDEAS.md content/RANDOM_NOTES.md docs/planted-non-reference.md
  git commit -q -m "planted non-violation: links to MARKETING_IDEAS.md and RANDOM_NOTES.md"
  if ! python3 tools/checks/check_assorted_notes.py > /dev/null; then
    echo "FAIL: check_assorted_notes.py fired on links to MARKETING_IDEAS.md/RANDOM_NOTES.md (false positive)" >&2
    exit 1
  fi
  echo "ok: stays clean on planted non-violation (MARKETING_IDEAS.md, RANDOM_NOTES.md)"
)
status=$?
rm -rf "$SCRATCH2"
if [ "$status" -ne 0 ]; then
  exit "$status"
fi

cd "$ROOT"
SCRATCH3="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH3"
(
  cd "$SCRATCH3"
  git config user.name "Fixture Author"
  git config user.email "fixture@example.com"
  mkdir -p content
  echo "whatever is on my mind" > content/ASSORTED_NOTES.md
  cat > README.md <<'EOF'
# Scratch repo

- [content/ASSORTED_NOTES.md](content/ASSORTED_NOTES.md) -- notes with no obvious home elsewhere.
EOF
  cat > MAP.md <<'EOF'
# Map

| content/ASSORTED_NOTES.md | General notes, listed here for discoverability. |
|---|---|
| [content/ASSORTED_NOTES.md](content/ASSORTED_NOTES.md) | as above |
EOF
  git add content/ASSORTED_NOTES.md README.md MAP.md
  git commit -q -m "planted non-violation: README.md and MAP.md link to ASSORTED_NOTES.md"
  if ! python3 tools/checks/check_assorted_notes.py > /dev/null; then
    echo "FAIL: check_assorted_notes.py fired on a README.md/MAP.md listing link (false positive)" >&2
    exit 1
  fi
  echo "ok: stays clean on a README.md/MAP.md listing link"
)
status=$?
rm -rf "$SCRATCH3"
if [ "$status" -ne 0 ]; then
  exit "$status"
fi

cd "$ROOT"
SCRATCH4="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH4"
(
  cd "$SCRATCH4"
  git config user.name "Fixture Author"
  git config user.email "fixture@example.com"
  mkdir -p content
  echo "whatever is on my mind" > content/ASSORTED_NOTES.md
  cat > docs-page.md <<'EOF'
# An ordinary page

See [the notes](content/ASSORTED_NOTES.md) for background on this claim.

## See also

- [content/ASSORTED_NOTES.md](content/ASSORTED_NOTES.md) -- related notes.
EOF
  git add content/ASSORTED_NOTES.md docs-page.md
  git commit -q -m "planted: an ordinary citation plus a See also link in one file"
  out="$(python3 tools/checks/check_assorted_notes.py || true)"
  if ! echo "$out" | grep -q "docs-page.md:3:"; then
    echo "FAIL: check_assorted_notes.py did not fire on the ordinary (non-See-also) citation" >&2
    echo "$out" >&2
    exit 1
  fi
  if echo "$out" | grep -q "docs-page.md:7:"; then
    echo "FAIL: check_assorted_notes.py fired on a See also link (false positive)" >&2
    echo "$out" >&2
    exit 1
  fi
  echo "ok: fires on the ordinary citation, not on the See also link, in the same file"
)
status=$?
rm -rf "$SCRATCH4"
if [ "$status" -ne 0 ]; then
  exit "$status"
fi

# Once content/ASSORTED_NOTES.md exists the consolidation this practice
# describes has happened, and a legacy NAME is just a filename again. A repo
# with a real ASSORTED_NOTES.md was flagged for linking book-moses/NOTES.md,
# a manuscript brainstorm that is not its catch-all (2026-09-06).
SCRATCH5="$(mktemp -d)"
(
  set -e
  git clone -q "$ROOT" "$SCRATCH5"
  cd "$SCRATCH5"
  mkdir -p content book-moses
  echo "# Assorted notes" > content/ASSORTED_NOTES.md
  echo "# Moses notes" > book-moses/NOTES.md
  echo "See [the Moses notes](book-moses/NOTES.md) for that draft." > TODO.md
  git add -A
  git -c user.name="Test" -c user.email="test@example.com" commit -q -m "migrated repo, unrelated NOTES.md"
  if ! python3 tools/checks/check_assorted_notes.py > /dev/null; then
    echo "FAIL: fired on a legacy-named file in a repo that already has content/ASSORTED_NOTES.md" >&2
    exit 1
  fi
  echo "ok: legacy names stop counting once the migration is done"

  # ...and the canonical file is still guarded in that same repo, so the
  # case above cannot be met by a check that simply stopped running.
  echo "Per [the notes](content/ASSORTED_NOTES.md), we should ship it." > TODO.md
  git add -A
  git -c user.name="Test" -c user.email="test@example.com" commit -q -m "citation of the real notes file"
  # Exit 1 exactly: a missing or crashing script (2) is not "fired".
  if [ "$(python3 tools/checks/check_assorted_notes.py > /dev/null 2>&1; echo $?)" != 1 ]; then
    echo "FAIL: stopped guarding content/ASSORTED_NOTES.md itself" >&2
    exit 1
  fi
  echo "ok: still fires on a citation of the canonical notes file"
)
status=$?
rm -rf "$SCRATCH5"
if [ "$status" -ne 0 ]; then
  exit "$status"
fi

# The same migration test, in a repo whose catch-all is NOT under content/.
# `content/` is this practice's default directory, not its definition, and
# content-directory says an established layout wins over the default. A repo
# that renamed content/ (2026-09-07: one renamed it to business-modeling/ so
# every content directory said what it held) still has a migrated catch-all,
# and its unrelated NOTES.md is still just a filename.
SCRATCH6="$(mktemp -d)"
(
  set -e
  git clone -q "$ROOT" "$SCRATCH6"
  cd "$SCRATCH6"
  mkdir -p business-modeling book-moses
  echo "# Assorted notes" > business-modeling/ASSORTED_NOTES.md
  echo "# Moses notes" > book-moses/NOTES.md
  echo "See [the Moses notes](book-moses/NOTES.md) for that draft." > TODO.md
  git add -A
  git -c user.name="Test" -c user.email="test@example.com" commit -q -m "migrated repo, catch-all outside content/"
  if ! python3 tools/checks/check_assorted_notes.py > /dev/null; then
    echo "FAIL: fired on a legacy-named file in a repo whose ASSORTED_NOTES.md is outside content/" >&2
    exit 1
  fi
  echo "ok: the migration counts wherever the catch-all lives, not only under content/"

  # ...and the canonical file is still guarded at its new location, so the
  # case above cannot be met by a check that simply stopped running.
  echo "Per [the notes](business-modeling/ASSORTED_NOTES.md), we should ship it." > TODO.md
  git add -A
  git -c user.name="Test" -c user.email="test@example.com" commit -q -m "citation of the real notes file, outside content/"
  # Exit 1 exactly: a missing or crashing script (2) is not "fired".
  if [ "$(python3 tools/checks/check_assorted_notes.py > /dev/null 2>&1; echo $?)" != 1 ]; then
    echo "FAIL: stopped guarding ASSORTED_NOTES.md once it moved out of content/" >&2
    exit 1
  fi
  echo "ok: still fires on a citation of the catch-all at its new location"
)
status=$?
rm -rf "$SCRATCH6"
if [ "$status" -ne 0 ]; then
  exit "$status"
fi

# The See also exemption must survive headline-capitalization. A repo that
# declares output_paths gets "## See also" rewritten to "## See Also", and a
# literal match then reads every footer link as a citation -- every page at
# once, on the very sweep that applies the rule (2026-09-07, a consuming repo).
SCRATCH7="$(mktemp -d)"
(
  set -e
  git clone -q "$ROOT" "$SCRATCH7"
  cd "$SCRATCH7"
  mkdir -p content
  echo "# Assorted notes" > content/ASSORTED_NOTES.md
  cat > a-page.md <<'EOF'
# An ordinary page

## See Also

- [content/ASSORTED_NOTES.md](content/ASSORTED_NOTES.md) -- related notes.
EOF
  git add -A
  git -c user.name="Test" -c user.email="test@example.com" commit -q -m "See Also in headline case"
  if ! python3 tools/checks/check_assorted_notes.py > /dev/null; then
    echo "FAIL: fired on a headline-cased See Also footer (the exemption must not be case-sensitive)" >&2
    exit 1
  fi
  echo "ok: the See also exemption survives headline capitalization"
)
status=$?
rm -rf "$SCRATCH7"
if [ "$status" -ne 0 ]; then
  exit "$status"
fi

# A link whose own text is the notes file's name or path, with no #fragment,
# names the file as a whole and cites nothing in it -- the listing move,
# made inline. Run against the engine's own repository on 2026-09-28, this
# check flagged a doc recipe naming the notes file as the one document its
# rule does not reach, and a todo item recording where a file lives. The
# control, in the same file, is a link to the same target whose text is not
# the file's name: it must still fire.
SCRATCH8="$(mktemp -d)"
(
  set -e
  git clone -q "$ROOT" "$SCRATCH8"
  cd "$SCRATCH8"
  mkdir -p content docs
  echo "# Assorted notes" > content/ASSORTED_NOTES.md
  cat > docs/names-the-file.md <<'EOF'
# A page that names the notes file

The one document this rule does not reach is [ASSORTED_NOTES.md](../content/ASSORTED_NOTES.md).
It lives at [content/ASSORTED_NOTES.md](../content/ASSORTED_NOTES.md), spelled from the root,
or at [`../content/ASSORTED_NOTES.md`](../content/ASSORTED_NOTES.md), spelled from here.
EOF
  git add -A
  git -c user.name="Test" -c user.email="test@example.com" commit -q -m "links that name the notes file"
  if ! out="$(python3 tools/checks/check_assorted_notes.py)"; then
    echo "FAIL: fired on a link whose text is the notes file's own name or path" >&2
    echo "$out" >&2
    exit 1
  fi
  echo "ok: a link naming the notes file itself is not a citation"

  cat >> docs/names-the-file.md <<'EOF'
As [OTHER_NOTES.md](../content/ASSORTED_NOTES.md) says, we should ship it.
EOF
  git add -A
  git -c user.name="Test" -c user.email="test@example.com" commit -q -m "a link whose text names a different file"
  out="$(python3 tools/checks/check_assorted_notes.py || true)"
  if ! grep -q "docs/names-the-file.md:6:" <<<"$out"; then
    echo "FAIL: stopped firing on a citation whose text is not the notes file's name" >&2
    echo "$out" >&2
    exit 1
  fi
  if grep -qE "docs/names-the-file.md:[345]:" <<<"$out"; then
    echo "FAIL: fired on a line that only names the notes file" >&2
    echo "$out" >&2
    exit 1
  fi
  echo "ok: still fires when the link text is not the notes file's name or path"
)
status=$?
rm -rf "$SCRATCH8"
if [ "$status" -ne 0 ]; then
  exit "$status"
fi

if ! python3 tools/checks/check_assorted_notes.py > /dev/null; then
  echo "FAIL: check_assorted_notes.py is not clean on the real, current repo" >&2
  exit 1
fi
echo "ok: clean on real content"
