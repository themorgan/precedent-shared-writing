#!/bin/bash

# A fixture commit is not a person's commit: the global commit backstop
# (commit-identity.sh, 2026-09-07) reaches the throwaway repositories
# this test builds and would refuse them.
export PRECEDENT_ALLOW_ANY_AUTHOR=1
# Two-direction test for check_buenos_aires_dates.py:
#   1. plant the exact violation in a scratch copy -- require the check to fire;
#   2. the real, current, unplanted repo -- require the check to stay clean.
set -euo pipefail
cd "$(dirname "$0")/../../.."
ROOT="$(pwd)"
SCRATCH="$(mktemp -d)"
RESOLVE_DIR="$(mktemp -d)"
trap 'rm -rf "$SCRATCH" "$RESOLVE_DIR"' EXIT

# Nothing here may depend on the machine's own Precedent configuration: a
# real ~/.config/precedent/config.json would resolve an identity for the
# fixtures below that deliberately declare none, and the shared-repo case
# would quietly stop testing what it says it tests. Each case that wants a
# user-level config points this at one of its own.
export PRECEDENT_USER_CONFIG="$RESOLVE_DIR/no-such-config.json"
unset PRECEDENT_COMMIT_EMAIL PRECEDENT_COMMIT_NAME PRECEDENT_COMMIT_TZ

# --- the engine module these checks now resolve the identity through ------
#
# check_commit_author.py and check_buenos_aires_dates.py stopped reading a
# root identity.json themselves on 2026-09-10 and call
# precedent_resolve.declared_identity() instead (see either script's own
# block for why: requiring a root identity.json made both permanently red in
# every SHARED consuming repo, where having one is forbidden). So every
# fixture below has to be able to import that module, or the check reports
# SKIPPED -- and a SKIP satisfies an `if ! check` assertion exactly as a
# violation does, which is how a whole test file can go green while proving
# nothing. Every assertion here therefore tests the EXIT CODE and the
# MESSAGE, never just "non-zero".
#
# Real module if this repo can see one. `precedent_identity.py` is the one
# to look for first: the resolution moved there from precedent_resolve.py
# upstream on 2026-09-10, into ENGINE_FILES rather than
# CONSUMER_ENGINE_FILES, so every kind of repo vendors it -- including a
# practice SET, which is the case that made the move necessary. An older
# vendored engine still has the names on the resolver, which is the second
# candidate, and matches the fallback the check itself makes.
#
# Where the repo vendors NEITHER -- an engine that predates the split, in a
# set that therefore never got the module -- this file used to write a
# 68-line stand-in reproducing declared_identity()'s three resolution steps.
# That was a FORK of the engine: one vendored engine, thin host shims, never a
# second implementation (engine-plus-host-shims). A fixture that reimplements
# the resolution it exists to test is free to drift from it, and it drifts in
# the direction that keeps the test green -- the stand-in passes while the
# engine the checks actually call is broken. It is gone.
#
# So there is no stand-in, and nothing here restates the engine: the real
# module is copied or there is none. Where there is none these fixtures have
# no resolution to exercise at all, and the one case that IS meaningful in
# that repo is the last in this file -- the check must report SKIPPED and name
# what it tried. assert_engine_absent runs exactly that, and stops.
#
# The candidates are the four places a repo can be vendoring the module, in
# the same order the check's own _identity_module() tries them, spelled out
# once here rather than in each place that walks them.
ENGINE_CANDIDATES=(
  "$ROOT/tools/precedent_identity.py"
  "$ROOT/process/upstream/tools/precedent_identity.py"
  "$ROOT/tools/precedent_resolve.py"
  "$ROOT/process/upstream/tools/precedent_resolve.py"
)
ENGINE_MODULE=""                        # the one provide_resolve found, if any

# No engine module can supply the declared identity -> the check must report
# SKIPPED (exit 2) with the reason, never ERRORED and never a silent pass.
# Run with an empty PYTHONPATH and from $ROOT, the way a person would.
assert_engine_absent() {
  local out status=0
  out="$(cd "$ROOT" && PYTHONPATH= python3 tools/checks/check_buenos_aires_dates.py 2>&1)" && status=0 || status=$?
  if [ "$status" != 2 ]; then
    echo "FAIL: engine module absent -- expected exit 2, got $status:" >&2
    echo "$out" >&2
    exit 1
  fi
  case "$out" in
    *"no engine module could supply the declared identity"*"precedent_identity.py"*) ;;
    *) echo "FAIL: engine module absent -- output did not name the modules it tried:" >&2
       echo "$out" >&2
       exit 1 ;;
  esac
  echo "ok: the engine module absent -> SKIPPED (exit 2) naming the module"
}

provide_resolve() {                     # $1 = fixture engine dir's parent
  local dest="$1/tools/precedent_identity.py" real
  mkdir -p "$1/tools"
  for real in "${ENGINE_CANDIDATES[@]}"; do
    if [ -f "$real" ]; then
      cp "$real" "$dest"
      ENGINE_MODULE="$real"
      return 0
    fi
  done
  echo "skip: this repo vendors no identity engine module (looked for ${ENGINE_CANDIDATES[*]}) -- the fixtures below have nothing to resolve an identity through, and this file will not fork declared_identity() to give them one. The one case that is meaningful here:"
  assert_engine_absent
  exit 0
}

# 0 clean, 1 violated, 2 could-not-run (SKIPPED). Asserting the exact code,
# and then the message, is the whole point: the three are not interchangeable
# and the difference between them is what this change is about.
LAST_OUT=""
expect_exit() {                         # $1 = wanted code, $2 = label, $3 = script
  local want="$1" label="$2" script="$3" status=0
  LAST_OUT="$(python3 "$script" 2>&1)" || status=$?
  if [ "$status" != "$want" ]; then
    echo "FAIL: $label -- expected exit $want, got $status:" >&2
    echo "$LAST_OUT" >&2
    exit 1
  fi
}

expect_message() {                      # $1 = substring, $2 = label
  case "$LAST_OUT" in
    *"$1"*) ;;
    *) echo "FAIL: $2 -- output did not mention '$1':" >&2
       echo "$LAST_OUT" >&2
       exit 1 ;;
  esac
}

provide_resolve "$RESOLVE_DIR"
export PYTHONPATH="$RESOLVE_DIR/tools${PYTHONPATH:+:$PYTHONPATH}"

git clone -q "$ROOT" "$SCRATCH"
cd "$SCRATCH"
git config user.name "Morgan F"
git config user.email "morgan@westegg.com"
touch planted-violation.txt
git add planted-violation.txt
TZ="UTC" git commit -q -m "planted violation: wrong tz offset"

expect_exit 1 "planted UTC-offset commit" tools/checks/check_buenos_aires_dates.py
expect_message "author-date offset is '+0000'" "planted UTC-offset commit"
echo "ok: fires on planted violation"

cd "$ROOT"

# The "clean on real content" direction is a claim about THIS check's home
# repo -- that its own commits satisfy the practice. A consuming repo
# materializes this test too, and there the claim is false for a legitimate
# reason: its history predates its adoption of the practice, and
# no-rewrite-for-warnings forbids rewriting published commits to satisfy a
# check. Failing there would train people to ignore a red suite.
#
# Only this direction is skipped. The planted-violation direction above is
# self-contained -- it creates the condition it tests, in a throwaway clone --
# so it still proves the check works, which is what a test is for.
#
# MANIFEST.json is written by precedent_materialize.py and exists ONLY in a
# consuming repo; no practice source has one. Checked against $ROOT rather
# than the working directory, because the scratch clone above is a copy of
# ROOT and carries the same file.
if [ -f "$ROOT/MANIFEST.json" ]; then
  echo "skip: 'clean on real content' (every commit carries the Buenos Aires offset) is a claim about this check's home repo; this is a consuming repo, where its history legitimately predates the practice"
else
  expect_exit 0 "clean on real content" tools/checks/check_buenos_aires_dates.py
  echo "ok: clean on real content"
fi

# --- per-repo grandfathering (identity.json's grandfathered_commit_shas) ---
# See test_commit_author.sh's identical block for the full rationale --
# same mechanism, shared field in identity.json, same 2026-09-07 origin.

SCRATCH2="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH2"
(
  cd "$SCRATCH2"
  git config user.name "Morgan F"
  git config user.email "morgan@westegg.com"
  touch planted-grandfathered.txt
  git add planted-grandfathered.txt
  TZ="UTC" git commit -q -m "planted violation: wrong tz offset, to be grandfathered"
  sha="$(git rev-parse HEAD)"
  python3 -c "
import json, pathlib
p = pathlib.Path('identity.json')
d = json.loads(p.read_text())
d.setdefault('grandfathered_commit_shas', []).append({'sha': '$sha', 'note': 'test plant'})
p.write_text(json.dumps(d, indent=2))
"
  expect_exit 0 "a per-repo grandfathered SHA in identity.json" tools/checks/check_buenos_aires_dates.py
  echo "ok: a per-repo grandfathered SHA in identity.json is exempted"

  python3 -c "
import json, pathlib
p = pathlib.Path('identity.json')
d = json.loads(p.read_text())
d.setdefault('grandfathered_commit_shas', []).append({'sha': 'not-a-real-sha', 'note': 'malformed on purpose'})
p.write_text(json.dumps(d, indent=2))
"
  expect_exit 1 "a malformed grandfathered_commit_shas entry" tools/checks/check_buenos_aires_dates.py
  expect_message "is not a" "a malformed grandfathered_commit_shas entry"
  echo "ok: a malformed grandfathered_commit_shas entry is reported, not silently ignored"
)
status=$?
rm -rf "$SCRATCH2"
[ "$status" = 0 ] || exit "$status"


# --- the same list, declared in precedent.json ---------------------------
# check_commit_author.py learned to read the consumer-level declaration file
# on 2026-09-07 and this check, whose own comment says the two share the
# mechanism "verbatim", was left reading identity.json only -- so one
# incident, grandfathered once, stayed exempt from the author check and kept
# failing the offset check. A shared repo has nowhere else to put it: an
# identity.json at its root is the thing it must not have.

SCRATCH5="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH5"
(
  cd "$SCRATCH5"
  git config user.name "Morgan F"
  git config user.email "morgan@westegg.com"
  touch planted-grandfathered-in-precedent.txt
  git add planted-grandfathered-in-precedent.txt
  TZ="UTC" git commit -q -m "planted violation: wrong tz offset, exempted in precedent.json"
  expect_exit 1 "before the precedent.json exemption" \
    tools/checks/check_buenos_aires_dates.py
  sha="$(git rev-parse HEAD)"
  python3 -c "
import json, pathlib
p = pathlib.Path('precedent.json')
d = json.loads(p.read_text())
d.setdefault('grandfathered_commit_shas', []).append({'sha': '$sha', 'note': 'test plant'})
p.write_text(json.dumps(d, indent=2))
"
  expect_exit 0 "after the precedent.json exemption" \
    tools/checks/check_buenos_aires_dates.py
  echo "ok: a grandfathered SHA declared in precedent.json is exempted too"
)
status=$?
rm -rf "$SCRATCH5"
[ "$status" = 0 ] || exit "$status"


# --- the shared-repo case: NOT APPLICABLE, never a violation -------------
#
# THE DEFECT THIS CLOSES (2026-09-10). This check reported a VIOLATION when
# no identity.json sat at the repo root -- "identity.json could not supply a
# timezone ... so no commit offset can be checked without it" -- while an
# identity.json at a root MEANS the repo is somebody's individual practice
# source, which a shared consuming repo must not claim to be. Permanently
# red there, with the fix forbidden. Found installing precedent-beta-v01
# into a real private project via INSTALL.md section 0.
#
# exit 2 and exit 1 are both "non-zero", so this asserts the code AND the
# message: an assertion that only proved non-zero would have passed against
# the old behaviour just as happily.

SCRATCH3="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH3"
(
  cd "$SCRATCH3"
  git rm -q identity.json
  expect_exit 2 "a shared repo with no declared identity" \
    tools/checks/check_buenos_aires_dates.py
  expect_message "SKIPPED" "a shared repo with no declared identity"
  expect_message "no single person for an author to be wrong about" \
    "a shared repo with no declared identity"
  echo "ok: no identity declared anywhere -> SKIPPED (exit 2), not a violation"

  git config user.name "Morgan F"
  git config user.email "morgan@westegg.com"
  touch planted-in-a-shared-repo.txt
  git add planted-in-a-shared-repo.txt
  TZ="UTC" git commit -q -m "a UTC-stamped commit in a repo that names nobody"
  expect_exit 2 "a UTC-offset commit in a repo that declares nobody" \
    tools/checks/check_buenos_aires_dates.py
  echo "ok: still SKIPPED with an off-zone commit present -- nobody is declared,"
  echo "    so there is no zone for it to be wrong against"
)
status=$?
rm -rf "$SCRATCH3"
[ "$status" = 0 ] || exit "$status"


# --- the zone resolved from the USER-LEVEL config ------------------------
# The person's zone is a person-level fact, so a shared repo gets it the
# same way it gets their name: from the individual source their own machine
# declares. The offset check is live there, and says where the zone came
# from.

SCRATCH4="$(mktemp -d)"
INDIV="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH4"
(
  cd "$SCRATCH4"
  python3 -c "
import json, pathlib
ident = json.loads(pathlib.Path('identity.json').read_text())
cfg = pathlib.Path('precedent.json')
d = json.loads(cfg.read_text())
# EXTEND, never assign: a fixture owns the state it adds and nothing else
# (fixture-owns-its-state). Assigning wiped whatever precedent.json already
# grandfathered -- nothing in THIS repo, whose exemptions all live in
# identity.json, but in a consuming repo that grandfathers SHAs there it
# dropped them, and the check then fired on real pre-existing commits: a
# failure the fixture caused itself and reported as the repo's.
d.setdefault('grandfathered_commit_shas', []).extend(
    ident.get('grandfathered_commit_shas', []))
cfg.write_text(json.dumps(d, indent=2))
"
  git rm -q identity.json
  cp "$ROOT/identity.json" "$INDIV/identity.json"
  printf '{"individual": {"path": "%s"}}\n' "$INDIV" > "$INDIV/config.json"
  export PRECEDENT_USER_CONFIG="$INDIV/config.json"

  expect_exit 0 "zone resolved from the user-level config" \
    tools/checks/check_buenos_aires_dates.py
  echo "ok: a repo that names nobody is CHECKED against the zone its user-level"
  echo "    config's individual source declares, and is clean"

  git config user.name "Morgan F"
  git config user.email "morgan@westegg.com"
  touch planted-against-user-config.txt
  git add planted-against-user-config.txt
  TZ="UTC" git commit -q -m "planted violation: wrong offset, zone from user config"
  expect_exit 1 "wrong offset against a user-config zone" \
    tools/checks/check_buenos_aires_dates.py
  expect_message "author-date offset is '+0000'" \
    "wrong offset against a user-config zone"
  expect_message "the individual practice source at $INDIV" \
    "wrong offset against a user-config zone"
  echo "ok: the violation still fires, and names where the expected zone came from"
)
status=$?
rm -rf "$SCRATCH4" "$INDIV"
[ "$status" = 0 ] || exit "$status"


# --- a repository with NO COMMITS: SKIPPED, and saying which -------------
#
# A fresh install is exactly this -- `git init`, nothing committed yet --
# and until 2026-09-14 the check read `git log` with check=True, so an
# unborn HEAD exited 128, the CalledProcessError escaped find_violations(),
# and precedent_check.py printed the traceback as a VIOLATION of the
# practice itself. Every INSTALL.md section 0 install hit it, in both
# identity checks at once. It is invisible from inside a practice set,
# which has years of history to log -- which is why the fixture here is a
# repository built from nothing rather than a clone of $ROOT.
#
# TWO DIRECTIONS, and the second is what makes the first worth anything.
# Exit 2 alone would pass against a skip for the WRONG REASON -- a repo
# that declares no identity skips too -- so the message is asserted; and
# the same fixture, once it carries one commit by the declared person, must
# run CLEAN rather than stay skipped forever.
EMPTY="$(mktemp -d)"
(
  cd "$ROOT"
  git init -q "$EMPTY"
  # The declaration travels with the fixture: ROOT is overridden below, so
  # the check resolves the identity from the EMPTY repo, not from this one.
  cp "$ROOT/identity.json" "$EMPTY/identity.json"
  export PRECEDENT_CHECK_ROOT="$EMPTY"

  expect_exit 2 "a repository with no commits" \
    tools/checks/check_buenos_aires_dates.py
  expect_message "SKIPPED" "a repository with no commits"
  expect_message "no commits yet" "a repository with no commits"
  echo "ok: a repo with no commits -> SKIPPED (exit 2) saying so, never a traceback"

  # The declared person and zone, read from the fixture's own declaration
  # rather than written out here a second time (registry-source-of-truth).
  name="$(python3 -c "import json;print(json.load(open('$EMPTY/identity.json'))['name'])")"
  email="$(python3 -c "import json;print(json.load(open('$EMPTY/identity.json'))['email'])")"
  zone="$(python3 -c "import json;print(json.load(open('$EMPTY/identity.json'))['timezone'])")"
  : > "$EMPTY/first.txt"
  git -C "$EMPTY" add first.txt
  TZ="$zone" GIT_AUTHOR_NAME="$name" GIT_AUTHOR_EMAIL="$email" \
  GIT_COMMITTER_NAME="$name" GIT_COMMITTER_EMAIL="$email" \
    git -C "$EMPTY" commit -q -m "the first commit, on the declared zone"
  expect_exit 0 "the same fixture, once it carries one correct commit" \
    tools/checks/check_buenos_aires_dates.py
  echo "ok: and the same repo, with one commit on the declared zone, runs clean"
)
status=$?
rm -rf "$EMPTY"
[ "$status" = 0 ] || exit "$status"


# --- the engine module absent -------------------------------------------
# Asserted by assert_engine_absent, above, and only ever from there. Reaching
# this line means provide_resolve found a module -- it exits in that function
# otherwise -- and in a CONSUMING repo the check finds the module at tools/ or
# process/upstream/tools/ on its own, so `PYTHONPATH=` cannot make it absent
# there, which is exactly what it is supposed to do.
echo "skip: 'engine module absent' -- this repo vendors $(basename "$ENGINE_MODULE")"

exit 0
