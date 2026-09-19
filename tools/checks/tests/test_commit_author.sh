#!/bin/bash

# A fixture commit is not a person's commit: the global commit backstop
# (commit-identity.sh, 2026-09-07) reaches the throwaway repositories
# this test builds and would refuse them.
export PRECEDENT_ALLOW_ANY_AUTHOR=1
# Two-direction test for check_commit_author.py:
#   1. plant the exact violation in a scratch copy -- require the check to fire;
#   2. the real, current, unplanted repo -- require the check to stay clean.
#
# Since 2026-09-06 the check has a second half -- the mechanism that stops a
# wrong-author commit being made at all, rather than only reporting one
# already made -- so there is a plant per layer of that mechanism too,
# further down. Those plants touch publisher paths (bootstrap/,
# .claude/settings.json), so they stand down in a consuming repo the same
# way the "clean on real content" direction below does.
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
  out="$(cd "$ROOT" && PYTHONPATH= python3 tools/checks/check_commit_author.py 2>&1)" && status=0 || status=$?
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
git config user.name "Someone Else"
git config user.email "someone@example.com"
touch planted-violation.txt
git add planted-violation.txt
GIT_AUTHOR_NAME="Someone Else" GIT_AUTHOR_EMAIL="someone@example.com" \
GIT_COMMITTER_NAME="Someone Else" GIT_COMMITTER_EMAIL="someone@example.com" \
  git commit -q -m "planted violation: wrong author"

expect_exit 1 "planted wrong-author commit" tools/checks/check_commit_author.py
expect_message "author is 'Someone Else'" "planted wrong-author commit"
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
  echo "skip: 'clean on real content' (every commit is authored by Morgan) is a claim about this check's home repo; this is a consuming repo, where its history legitimately predates the practice"
else
  expect_exit 0 "clean on real content" tools/checks/check_commit_author.py
  echo "ok: clean on real content"
fi


# --- the prevention half (bootstrap/commit-identity.sh + the env block) ---
# One plant per layer, each the exact regression that would let the six
# already-grandfathered commits happen a seventh time.

run_case() {
  local label="$1"
  local mutate="$2"
  local scratch
  scratch="$(mktemp -d)"
  git clone -q "$ROOT" "$scratch"
  (
    cd "$scratch"
    eval "$mutate"
    # A plant that could not find its anchor produced no evidence: the check
    # never saw a broken subject, so "it did not fire" says nothing about the
    # check. Skip, with the reason -- never a pass, and never a FAIL blamed on
    # the check for something that moved in the file being planted into
    # (practice: fixture-owns-its-state).
    if [ -f .plant-could-not-anchor ]; then
      echo "SKIPPED (not a pass): $label -- $(cat .plant-could-not-anchor)"
      exit 0
    fi
    expect_exit 1 "$label" tools/checks/check_commit_author.py
    echo "ok: fires on planted violation ($label)"
  )
  local status=$?
  rm -rf "$scratch"
  return $status
}

if [ -f "$ROOT/MANIFEST.json" ]; then
  echo "skip: the prevention-half plants target publisher paths (bootstrap/, .claude/settings.json); this is a consuming repo, which has neither"
  exit 0
fi

run_case "identity script loses its executable bit" '
chmod -x bootstrap/commit-identity.sh
git add bootstrap/commit-identity.sh
'

run_case "identity script stops setting the local config" '
python3 -c "
import pathlib
p = pathlib.Path(\"bootstrap/commit-identity.sh\")
t = p.read_text()
anchor = t.split(chr(10))
out = []
done = False
for line in anchor:
    out.append(line)
    if not done and line.startswith(\"git -C\") and \"rev-parse --git-dir\" in line:
        out.append(\"exit 0\")
        done = True
if not (done):
    pathlib.Path(\".plant-could-not-anchor\").write_text(\"the git-repo guard moved -- update this plant\")
    raise SystemExit(0)
p.write_text(chr(10).join(out))
"
'

# THE PLANT MUST DISABLE BOTH HOOKS, and the reason is worth stating because
# the obvious diagnosis is wrong. commit-identity.sh installs TWO per-repo
# hooks -- "$hooks_dir/pre-commit" and "$hooks_dir/prepare-commit-msg" -- and
# either one refuses a wrong-author commit on its own. A plant that renamed
# only the pre-commit target left prepare-commit-msg installed and refusing,
# so check_commit_author.py correctly reported the backstop WORKING and this
# case reported that it did not fire. Measured 2026-09-08 by replicating the
# fixture by hand: the hooks directory held `pre-commit-disabled` and
# `prepare-commit-msg`, and the refusal that came back was the local-identity
# one. Negative control: weaken this plant back to pre-commit only and the
# case fails again.
#
# NOT the global core.hooksPath backstop, which an earlier reading blamed:
# check_commit_author.py already pins the throwaway repo's LOCAL
# core.hooksPath to its own hooks directory and runs the script under a
# scratch HOME, so the global installer is neutralised before this plant
# runs. Ruled out by measurement, not reasoning -- the fixture's global hooks
# path resolved under the scratch HOME, and local config outranks it.
#
# Practice: fixture-owns-its-state. A plant owns every path that can satisfy
# the assertion, or the assertion silently becomes about the one path it
# happened to think of.
run_case "the commit backstop is no longer installed (neither hook)" '
python3 -c "
import pathlib
p = pathlib.Path(\"bootstrap/commit-identity.sh\")
t = p.read_text()
# chr(36) is a dollar sign, spelled this way so the shell that evals this
# plant cannot expand the variable name out of the string being searched for.
d = chr(36)
q = chr(34)
for var, hook in ((\"target=\", \"/pre-commit\"), (\"merge_target=\", \"/prepare-commit-msg\")):
    old = var + q + d + \"hooks_dir\" + hook + q
    if not (old in t):
        pathlib.Path(\".plant-could-not-anchor\").write_text(\"the \" + hook + \" target moved -- update this plant\")
        raise SystemExit(0)
    t = t.replace(old, old.replace(hook, hook + \"-disabled\"), 1)
p.write_text(t)
"
'

run_case "env no longer carries the author identity" '
python3 -c "
import json, pathlib
p = pathlib.Path(\".claude/settings.json\")
d = json.loads(p.read_text())
d[\"env\"].pop(\"GIT_AUTHOR_EMAIL\", None)
p.write_text(json.dumps(d, indent=2))
"
'

run_case "env overrides the committer as well" '
python3 -c "
import json, pathlib
p = pathlib.Path(\".claude/settings.json\")
d = json.loads(p.read_text())
d[\"env\"][\"GIT_COMMITTER_EMAIL\"] = \"someone@example.invalid\"
p.write_text(json.dumps(d, indent=2))
"
'

# The declared identity is the one place these values live, so the check has
# to fail when a derived copy drifts from it -- that check IS what makes "one
# place" true rather than merely intended.
run_case "the env block drifts from the declared identity" '
python3 -c "
import json, pathlib
p = pathlib.Path(\"identity.json\")
d = json.loads(p.read_text())
d[\"email\"] = \"someone-else@example.invalid\"
p.write_text(json.dumps(d, indent=2))
"
'

# An identity.json that is PRESENT but declares no usable identity is still a
# violation: a root identity.json means this repository IS somebody's
# individual practice source, so a broken one is a broken declaration and
# this check is what reports it. Only ABSENCE stands down (next block).
run_case "identity.json is present but declares no email" '
python3 -c "
import json, pathlib
p = pathlib.Path(\"identity.json\")
d = json.loads(p.read_text())
d.pop(\"email\", None)
p.write_text(json.dumps(d, indent=2))
"
'

# --- per-repo grandfathering (identity.json's grandfathered_commit_shas) ---
# 2026-09-07: this mechanism only ever ran against ITS OWN history before
# (the hardcoded GRANDFATHERED_SHAS set above); themorgan/HavrutaBrainstorm
# was the first consumer that needed to exempt commits in ITS OWN history,
# which the hardcoded set can't do (it lives in a file
# precedent_materialize.py overwrites on every sync). Two directions: a
# planted wrong-author commit whose SHA is declared, correctly-formed, in
# identity.json is NOT reported; a malformed entry IS reported, so a typo'd
# SHA doesn't silently fail to exempt anything.

SCRATCH2="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH2"
(
  cd "$SCRATCH2"
  git config user.name "Someone Else"
  git config user.email "someone@example.com"
  touch planted-grandfathered.txt
  git add planted-grandfathered.txt
  GIT_AUTHOR_NAME="Someone Else" GIT_AUTHOR_EMAIL="someone@example.com" \
  GIT_COMMITTER_NAME="Someone Else" GIT_COMMITTER_EMAIL="someone@example.com" \
    git commit -q -m "planted violation: wrong author, to be grandfathered"
  sha="$(git rev-parse HEAD)"
  python3 -c "
import json, pathlib
p = pathlib.Path('identity.json')
d = json.loads(p.read_text())
d.setdefault('grandfathered_commit_shas', []).append({'sha': '$sha', 'note': 'test plant'})
p.write_text(json.dumps(d, indent=2))
"
  expect_exit 0 "a per-repo grandfathered SHA in identity.json" tools/checks/check_commit_author.py
  echo "ok: a per-repo grandfathered SHA in identity.json is exempted"

  python3 -c "
import json, pathlib
p = pathlib.Path('identity.json')
d = json.loads(p.read_text())
d.setdefault('grandfathered_commit_shas', []).append({'sha': 'not-a-real-sha', 'note': 'malformed on purpose'})
p.write_text(json.dumps(d, indent=2))
"
  expect_exit 1 "a malformed grandfathered_commit_shas entry" tools/checks/check_commit_author.py
  expect_message "is not a" "a malformed grandfathered_commit_shas entry"
  echo "ok: a malformed grandfathered_commit_shas entry is reported, not silently ignored"
)
status=$?
rm -rf "$SCRATCH2"
[ "$status" = 0 ] || exit "$status"


# --- the shared-repo case: NOT APPLICABLE, never a violation -------------
#
# THE DEFECT THIS CLOSES (2026-09-10). This check reported a VIOLATION when
# there was no identity.json at the repo root -- "identity.json could not be
# read ... nothing downstream can be checked without it" -- while this same
# file's per-repo-exemption comment says a shared consuming repo must NOT
# have one, because an identity.json at a root means the repo IS somebody's
# individual practice source and putting one in a shared repo pins one
# person's identity onto everyone committing there. Both checks were
# therefore permanently red in every shared consumer, with the fix forbidden
# by the same file that demanded it. Found installing precedent-beta-v01
# into a real private project via INSTALL.md section 0.
#
# The negative control matters as much as the case: exit 2 and exit 1 are
# both "non-zero", so this asserts the code AND the message. An assertion
# that only proved non-zero would have passed against the old behaviour.

SCRATCH3="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH3"
(
  cd "$SCRATCH3"
  git rm -q identity.json
  expect_exit 2 "a shared repo with no declared identity" \
    tools/checks/check_commit_author.py
  expect_message "SKIPPED" "a shared repo with no declared identity"
  expect_message "no single person for an author to be wrong about" \
    "a shared repo with no declared identity"
  echo "ok: no identity declared anywhere -> SKIPPED (exit 2), not a violation"

  # And the negative control for the negative control: a wrong-author commit
  # in that same repo is still not a violation, because there is nobody for
  # it to be wrong ABOUT. If this ever starts exiting 1, the stand-down has
  # silently become a pass-through.
  git config user.name "Someone Else"
  git config user.email "someone@example.com"
  touch planted-in-a-shared-repo.txt
  git add planted-in-a-shared-repo.txt
  GIT_AUTHOR_NAME="Someone Else" GIT_AUTHOR_EMAIL="someone@example.com" \
  GIT_COMMITTER_NAME="Someone Else" GIT_COMMITTER_EMAIL="someone@example.com" \
    git commit -q -m "a commit by somebody else, in a repo that names nobody"
  expect_exit 2 "a wrong-author commit in a repo that declares nobody" \
    tools/checks/check_commit_author.py
  echo "ok: still SKIPPED with a foreign commit present -- a violation must mean"
  echo "    'a commit has the wrong author', never 'this repository is shared'"
)
status=$?
rm -rf "$SCRATCH3"
[ "$status" = 0 ] || exit "$status"


# --- the identity resolved from the USER-LEVEL config --------------------
# The third step of the resolution order, and the one that makes a shared
# repo checkable at all: the repo names nobody, the person's own machine
# names their individual practice source, and the check judges commits
# against the identity found there -- reporting WHERE it came from, so a
# finding can be argued with.

SCRATCH4="$(mktemp -d)"
INDIV="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH4"
(
  cd "$SCRATCH4"
  # The exemptions have to move with it. identity.json carries this repo's
  # grandfather list, and a shared repo cannot keep one there -- precedent.json
  # is the consumer-level declaration file that exists for exactly this.
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

  expect_exit 0 "identity resolved from the user-level config" \
    tools/checks/check_commit_author.py
  echo "ok: a repo that names nobody is CHECKED against the individual source"
  echo "    its user-level config declares, and is clean"

  git config user.name "Someone Else"
  git config user.email "someone@example.com"
  touch planted-against-user-config.txt
  git add planted-against-user-config.txt
  GIT_AUTHOR_NAME="Someone Else" GIT_AUTHOR_EMAIL="someone@example.com" \
  GIT_COMMITTER_NAME="Someone Else" GIT_COMMITTER_EMAIL="someone@example.com" \
    git commit -q -m "planted violation: wrong author, identity from user config"
  expect_exit 1 "wrong author against a user-config identity" \
    tools/checks/check_commit_author.py
  expect_message "author is 'Someone Else'" \
    "wrong author against a user-config identity"
  expect_message "the individual practice source at $INDIV" \
    "wrong author against a user-config identity"
  echo "ok: the violation still fires, and names where the expected identity"
  echo "    came from"
)
status=$?
rm -rf "$SCRATCH4" "$INDIV"
[ "$status" = 0 ] || exit "$status"


# --- a SHARED repo must NOT be required to hardcode env.GIT_AUTHOR_* -----
#
# 2026-09-19. env_findings() used to demand a literal GIT_AUTHOR_NAME /
# GIT_AUTHOR_EMAIL / TZ in every repo's tracked .claude/settings.json,
# unconditionally -- which is exactly the pattern
# tools/precedent_check.py's own no-hardcoded-git-identity check exists to
# flag in a repo that is NOT an individual source (no root identity.json):
# a literal value there overrides commit-identity.sh's per-person
# resolution for every collaborator who loads the file, not only the one
# who wrote it. The two checks fought each other in exactly this
# situation -- a consuming repo that stripped the two keys to satisfy
# no-hardcoded-git-identity immediately failed this one instead. This
# fixture is that situation: identity resolves from the user-level config
# (rung 3), same as the block above, so ROOT declares nobody of its own.
SCRATCH5="$(mktemp -d)"
INDIV5="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH5"
(
  cd "$SCRATCH5"
  python3 -c "
import json, pathlib
ident = json.loads(pathlib.Path('identity.json').read_text())
cfg = pathlib.Path('precedent.json')
d = json.loads(cfg.read_text())
d.setdefault('grandfathered_commit_shas', []).extend(
    ident.get('grandfathered_commit_shas', []))
cfg.write_text(json.dumps(d, indent=2))
"
  git rm -q identity.json
  cp "$ROOT/identity.json" "$INDIV5/identity.json"
  printf '{"individual": {"path": "%s"}}\n' "$INDIV5" > "$INDIV5/config.json"
  export PRECEDENT_USER_CONFIG="$INDIV5/config.json"

  python3 -c "
import json, pathlib
p = pathlib.Path('.claude/settings.json')
d = json.loads(p.read_text())
d['env'].pop('GIT_AUTHOR_NAME', None)
d['env'].pop('GIT_AUTHOR_EMAIL', None)
p.write_text(json.dumps(d, indent=2))
"
  expect_exit 0 "a shared repo with no hardcoded env.GIT_AUTHOR_* and identity from user config" \
    tools/checks/check_commit_author.py
  echo "ok: a repo with no root identity.json is not required to hardcode"
  echo "    env.GIT_AUTHOR_NAME/EMAIL -- that would be the pattern"
  echo "    no-hardcoded-git-identity exists to catch, not a fix for this"

  # Still fires on a real wrong-author commit: dropping the literal env
  # check must not have turned into dropping the check.
  git config user.name "Someone Else"
  git config user.email "someone@example.com"
  touch planted-shared-no-hardcode.txt
  git add planted-shared-no-hardcode.txt
  GIT_AUTHOR_NAME="Someone Else" GIT_AUTHOR_EMAIL="someone@example.com" \
  GIT_COMMITTER_NAME="Someone Else" GIT_COMMITTER_EMAIL="someone@example.com" \
    git commit -q -m "planted violation: wrong author, shared repo, no hardcoded env"
  expect_exit 1 "wrong author, shared repo with no hardcoded env" \
    tools/checks/check_commit_author.py
  expect_message "author is 'Someone Else'" \
    "wrong author, shared repo with no hardcoded env"
  echo "ok: the commit-scan half still fires with no literal env identity present"
)
status=$?
rm -rf "$SCRATCH5" "$INDIV5"
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
    tools/checks/check_commit_author.py
  expect_message "SKIPPED" "a repository with no commits"
  expect_message "no commits yet" "a repository with no commits"
  echo "ok: a repo with no commits -> SKIPPED (exit 2) saying so, never a traceback"

  # The declared person, read from the fixture's own declaration rather than
  # written out here a second time (practice: registry-source-of-truth).
  name="$(python3 -c "import json;print(json.load(open('$EMPTY/identity.json'))['name'])")"
  email="$(python3 -c "import json;print(json.load(open('$EMPTY/identity.json'))['email'])")"
  : > "$EMPTY/first.txt"
  git -C "$EMPTY" add first.txt
  GIT_AUTHOR_NAME="$name" GIT_AUTHOR_EMAIL="$email" \
  GIT_COMMITTER_NAME="$name" GIT_COMMITTER_EMAIL="$email" \
    git -C "$EMPTY" commit -q -m "the first commit, by the declared person"
  expect_exit 0 "the same fixture, once it carries one correct commit" \
    tools/checks/check_commit_author.py
  echo "ok: and the same repo, with one commit by the declared person, runs clean"
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
