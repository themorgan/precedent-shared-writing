#!/bin/bash

# A fixture commit is not a person's commit: the global commit backstop
# (commit-identity.sh, 2026-09-07) reaches the throwaway repositories
# this test builds and would refuse them.
export PRECEDENT_ALLOW_ANY_AUTHOR=1
# Multi-direction test for check_no_stale_counts.py.
#
#   A.  a wrong "<N> practices" count in tracked markdown   -- must fire;
#   B.  the real, current, unplanted repo                   -- must be clean;
#   C.  the same count inside a §1 mirror (process/upstream/ plus a
#       process/manifest.json naming it)                    -- must be silent;
#   D.  the same count inside a §0 mirror (a precedent.json-declared source
#       path, and NO process/manifest.json)                 -- must be silent;
#   D'. the SAME §0 fixture with the engine removed         -- must fire, which
#       is the defect this change fixes, asserted so D cannot pass for some
#       other reason;
#   E.  a wrong count in a SOURCE SET's own content, with precedent.json
#       declaring `path: "."`                               -- must still fire;
#   F.  a repo with no practices/ tree at all               -- must SKIP (2);
#   G.  a root git cannot list                              -- must SKIP (2).
#
# WHY D AND D' ARE A PAIR. Until 2026-09-10 this check derived the mirror
# exclusion itself, from process/manifest.json's upstream.vendored_at --
# INSTALL.md §1's bookkeeping, which §0 step 5 says outright to skip. So a
# §0 install had no exclusion at all, and a real one that day reported
# Precedent's own historical prose as stale ("states 34 practices, but
# practices currently holds 121"), none of it actionable: editing a mirror
# is forbidden and the next sync overwrites it. The exclusion now comes
# from precedent_resolve.mirrored_prefixes(), which also reads
# precedent.json's declared source paths -- the authority that exists in
# exactly the repos the manifest is missing from. D asserts the fix; D'
# asserts that D is testing it.
#
# WHY E EXISTS. mirrored_prefixes() deliberately does not treat the repo
# root as a mirror: a source set declares `path: "."` and its practices/
# tree is hand-authored. Over-excluding would blind this check to a
# practice set's own content -- a worse failure than the one being fixed --
# so it is asserted rather than trusted.
set -uo pipefail
cd "$(dirname "$0")/../../.."
ROOT="$(pwd)"

# --- Reaching a real precedent_resolve.py ---------------------------------
#
# It is NOT vendored here, and that is correct: upstream puts it in
# CONSUMER_ENGINE_FILES but not ENGINE_FILES, because a practice set
# resolves no catalogue (tools/ENGINE_MANIFEST.json lists what this repo
# does carry). So the engine cases need a BestPractice clone, found the same
# way `precedent_vendor_engine.py refresh <clone>` finds one: told, not
# guessed. A STUB would test the stub, so there is deliberately no stub --
# without a clone, D/C+/E report SKIPPED and say what to set.
#
# A LOUD SKIP, NOT A FAILURE, and that is a real gap, recorded in
# [TODO.md](../../../TODO.md#engine-cases-need-a-bestpractice-clone). Failing
# would make this suite permanently red wherever no clone exists, and a gate
# nobody can get green is a gate nobody runs -- this repo's own documented
# lesson. Set PRECEDENT_REQUIRE_ENGINE_CASES=1 to turn the skip into a
# failure, which is what a CI job that DOES provide a clone should do. D'
# needs no clone and always runs, so the suite still asserts that the §0
# mirror is in scope without the engine.
#
# precedent_resolve.py imports split_practices and build_views at module
# level; both ARE vendored here, so a fixture cloned from this repo needs
# only the one file copied in.
find_engine () {
  local c
  for c in "${PRECEDENT_BESTPRACTICE_CLONE:-}" "${BESTPRACTICE_CLONE:-}" \
           "$ROOT/../BestPractice" "$ROOT/../bestpractice" "/tmp/bp"; do
    [ -n "$c" ] && [ -f "$c/tools/precedent_resolve.py" ] && {
      printf '%s' "$c/tools/precedent_resolve.py"; return 0; }
  done
  return 1
}
ENGINE="$(find_engine || true)"

status=0
pass () { echo "ok: $1"; }
fail () { echo "FAIL: $1" >&2; status=1; }

# --- Fixture builders -----------------------------------------------------
#
# Each APPENDS to whatever it finds rather than replacing it
# (fixture-owns-its-state): run inside a consuming repo, where
# precedent.json already declares real sources, a builder that overwrote the
# file would test what it had just deleted.

seed_mirror_source () {   # $1 = the mirror path to declare as a source
  python3 - "$1" <<'PY'
import json, pathlib, sys
path = sys.argv[1]
p = pathlib.Path('precedent.json')
d = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
srcs = d.setdefault('sources', [])
if not any((s or {}).get('path') == path for s in srcs):
    srcs.append({'name': 'precedent', 'path': path})
# Two entries mirrored_prefixes() must NOT return, asserted by their absence
# from the exclusion rather than by a separate case: the repo-local source,
# and a source resolving outside this repo.
for extra in ({'name': 'local', 'path': 'local'},
              {'name': 'sibling', 'path': '../a-sibling-clone'}):
    if not any((s or {}).get('path') == extra['path'] for s in srcs):
        srcs.append(extra)
p.write_text(json.dumps(d, indent=2, sort_keys=True) + '\n', encoding='utf-8')
PY
}

plant_in () {   # $1 = file to write the wrong count into
  mkdir -p "$(dirname "$1")"
  cat > "$1" <<'MD'
# A document with a count in it
This set has 999 practices, definitely not the real count.
MD
}

install_engine () {   # copy the real engine in; caller has checked ENGINE
  # The WHOLE engine directory's modules, not precedent_resolve.py alone.
  # It imports siblings at module level (split_practices, build_views, and
  # through them precedent_identity), so a lone copy raises
  # ModuleNotFoundError on import -- and the check under test catches that
  # and falls back to the manifest answer. In the D fixture there is no
  # manifest, so the fallback returns an EMPTY exclusion and the planted
  # violation fires: a case that exists to prove the mirror exclusion works
  # instead proved it absent, and said so in the voice of the check being
  # wrong rather than the fixture being short a file. Copying every
  # top-level module means the next sibling this engine picks up does not
  # break the case again. tools/checks/ is deliberately untouched --
  # overlay_check_under_test() has already put the check under test there,
  # and the engine directory has no checks/ of its own to clobber it with.
  mkdir -p tools
  cp "$(dirname "$ENGINE")"/*.py tools/
}

remove_engine () {   # the inverse of install_engine, and it has to exist
  # A "no-engine" case used to get its way for free: this repo vendored no
  # precedent_resolve.py, so a clone of it had none. That stopped being true
  # when the engine started vendoring the resolver into every practice set --
  # and the D' fixture, which ASSERTED the absence rather than arranging it,
  # began failing with "fixture bug: this case requires NO engine" on a tree
  # where nothing was wrong except the assumption. Arranging the condition is
  # what a fixture is for; asserting somebody else's tree still happens to
  # satisfy it is a fixture waiting to break.
  #
  # precedent_resolve.py alone is the switch, not the whole engine directory:
  # it is the module the check imports to ask which trees are mirrors, and the
  # check falls back to the manifest answer when that import fails. Removing
  # it is exactly the "no resolver reachable" state these cases mean.
  rm -f tools/precedent_resolve.py
}

overlay_check_under_test () {
  # `git clone` carries COMMITTED state only, so every fixture was running
  # whatever check_no_stale_counts.py is on HEAD -- not the one being
  # edited. Found 2026-09-10 while adding the §0 cases below: the new
  # exit-2 and mirror-exclusion behaviour was uncommitted, so three cases
  # failed against the old script and one of them (F) reported a clean
  # exit 0 that looked like the check disagreeing with its own test. A
  # test that silently exercises a different version of its subject than
  # the one you are changing is worse than no test: it is confidently
  # wrong. Overlaying the WORKING-TREE copy makes the fixture test what is
  # in front of you, committed or not.
  cp "$ROOT/tools/checks/check_no_stale_counts.py" tools/checks/
}

fixture_plain_violation () {
  echo "" >> README.md
  echo "This set has 999 practices, definitely not the real count." >> README.md
}

fixture_section1_mirror () {
  # The classic §1 layout: a vendored tree plus the manifest that names it.
  mkdir -p process/upstream
  cat > process/manifest.json <<'JSON'
{"upstream": {"repo": "https://example.invalid/upstream", "vendored_at": "process/upstream", "commit": "0000000000000000000000000000000000000000"}}
JSON
  plant_in process/upstream/MIRRORED.md
}

fixture_section0_mirror () {
  # A §0 install: the catalogue sits at whatever precedent.json names, and
  # there is NO process/manifest.json -- step 5 says to skip it. Asserted,
  # because the whole defect was reading a file this shape does not have.
  rm -f process/manifest.json
  seed_mirror_source precedent/universal
  plant_in precedent/universal/practices/catalogue-carries-stories.md
  if [ -e process/manifest.json ]; then
    echo "fixture bug: the §0 fixture must have no process/manifest.json" >&2
    return 1
  fi
}

fixture_source_set () {
  # A source set declares itself: `path: "."`. The planted count goes in
  # this set's OWN content, which must stay in scope.
  rm -f process/manifest.json
  python3 - <<'PY'
import json, pathlib
p = pathlib.Path('precedent.json')
d = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
srcs = d.setdefault('sources', [])
if not any((s or {}).get('path') == '.' for s in srcs):
    srcs.append({'name': 'precedent-team-writing', 'path': '.'})
p.write_text(json.dumps(d, indent=2, sort_keys=True) + '\n', encoding='utf-8')
PY
  echo "" >> README.md
  echo "This set has 999 practices, definitely not the real count." >> README.md
}

fixture_multi_source_own_count () {
  # A practice SET whose own practices/ tree IS a declared source
  # (universal, path ".") that ALSO declares a repo-local source living
  # in its own separate directory -- the shape whose real total spans
  # more than one directory, which PRACTICES_DIR alone undercounted
  # (the alex137/BestPractice case this fixes: universal at "." plus
  # repo-local at "local").
  rm -f process/manifest.json
  # This fixture clones precedent-team-writing itself and asks it to stand
  # in for a universal source at path "." -- BestPractice's own shape, not
  # this repo's. But the clone carries this repo's REAL precedent-source.json
  # (name "precedent-team-writing", level "shared", added 2026-09-19 by
  # practice: source-naming), and check_source_manifest() now refuses any
  # declared source whose name or level disagrees with what the clone at its
  # path calls itself. Left as-is, the fixture's own declaration (name
  # "precedent", level "universal") stopped matching the thing it points at,
  # so resolve() correctly refused it as a wrong-repository mismatch and the
  # check reported SKIPPED instead of clean -- not the defect under test,
  # but a second-order break from a later, unrelated practice landing on the
  # same path this fixture already used. Overwriting the manifest here makes
  # the clone answer to the identity the fixture declares, the same way a
  # real BestPractice checkout would.
  cat > precedent-source.json <<'JSON'
{
  "name": "precedent",
  "level": "universal"
}
JSON
  python3 - <<'PY'
import json, pathlib
p = pathlib.Path('precedent.json')
d = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
srcs = d.setdefault('sources', [])
if not any((s or {}).get('path') == '.' and (s or {}).get('level') == 'universal'
           for s in srcs):
    srcs.append({'level': 'universal', 'name': 'precedent', 'path': '.'})
if not any((s or {}).get('path') == 'local' for s in srcs):
    srcs.append({'level': 'repo-local', 'name': 'local', 'path': 'local'})
p.write_text(json.dumps(d, indent=2, sort_keys=True) + '\n', encoding='utf-8')
PY
  mkdir -p local/practices
  cat > local/practices/multi-source-fixture-practice.md <<'MD'
---
slug: multi-source-fixture-practice
status: active
---
## Rule
Fixture-only practice, planted to prove a repo-local source's active
count is added to the universal (path ".") count this repo also
declares -- never a real rule.
MD
  local base total
  base="$(python3 - <<'PY'
import pathlib, re
n = 0
for f in pathlib.Path('practices').glob('*.md'):
    if re.search(r'^status:\s+active\s*$', f.read_text(encoding='utf-8'), re.M):
        n += 1
print(n)
PY
)"
  total=$((base + 1))
  echo "" >> README.md
  echo "This set has $total practices, correctly counted across both its" \
       "universal (path \".\") and repo-local sources." >> README.md
}

fixture_no_practices_tree () {
  git rm -r -q practices
}

# --- The runner -----------------------------------------------------------
#
# expect is one of: fires | clean | skipped. A non-zero exit is not evidence
# on its own, so `fires` asserts the check's own header AND the specific
# finding, and `skipped` asserts exit 2 AND the reason
# (control-asserts-which-failure). Exit 2 is the runner's could-not-run
# signal, reported as SKIPPED and never folded into a pass.
run () {
  local label="$1" expect="$2" fixture="$3" want_engine="$4"
  if [ "$want_engine" = engine ] && [ -z "$ENGINE" ]; then
    echo "SKIPPED (not a pass): $label -- no precedent_resolve.py reachable." \
         "Set PRECEDENT_BESTPRACTICE_CLONE to a BestPractice clone to run it."
    if [ -n "${PRECEDENT_REQUIRE_ENGINE_CASES:-}" ]; then
      fail "$label -- PRECEDENT_REQUIRE_ENGINE_CASES is set and the engine is not reachable"
    fi
    return 0
  fi
  local scratch; scratch="$(mktemp -d)"
  if ! git clone -q "$ROOT" "$scratch"; then
    fail "$label -- could not clone the fixture"
    rm -rf "$scratch"
    return 0
  fi
  (
    set -e
    cd "$scratch"
    overlay_check_under_test
    "$fixture"
    if [ "$want_engine" = engine ]; then install_engine; else remove_engine; fi
    git add -A >/dev/null
    git -c user.name=Test -c user.email=test@example.com commit -q -m "fixture: $label"
    # `out=$(...); code=$?` would never be reached under `set -e` when the
    # check exits non-zero -- which is what most of these cases EXPECT. The
    # || keeps the assignment a tested command.
    code=0
    out="$(python3 tools/checks/check_no_stale_counts.py 2>&1)" || code=$?
    case "$expect" in
      fires)
        [ "$code" = 1 ] || { echo "expected exit 1, got $code: $out" >&2; exit 1; }
        printf '%s' "$out" | grep -q 'VIOLATION: no-stale-counts' \
          || { echo "fired without this check's header: $out" >&2; exit 1; }
        printf '%s' "$out" | grep -q "states 999 practices" \
          || { echo "fired, but not on the planted count: $out" >&2; exit 1; } ;;
      clean)
        [ "$code" = 0 ] || { echo "expected exit 0, got $code: $out" >&2; exit 1; }
        [ -z "$out" ] || { echo "clean run was not silent: $out" >&2; exit 1; } ;;
      skipped)
        [ "$code" = 2 ] || { echo "expected exit 2 (SKIPPED), got $code: $out" >&2; exit 1; }
        printf '%s' "$out" | grep -q '^SKIPPED: ' \
          || { echo "exited 2 without a reason: $out" >&2; exit 1; }
        printf '%s' "$out" | grep -qi 'practice' \
          || { echo "skip reason names nothing recognisable: $out" >&2; exit 1; } ;;
    esac
  )
  if [ $? -eq 0 ]; then pass "$label"; else fail "$label"; fi
  rm -rf "$scratch"
}

run "A. a wrong count in tracked markdown"                  fires   fixture_plain_violation    no-engine
run "C. the same count inside a §1 mirror (manifest)"       clean   fixture_section1_mirror    no-engine
run "C+. the §1 mirror, engine present -- unchanged"        clean   fixture_section1_mirror    engine
run "D. the same count inside a §0 mirror (no manifest)"    clean   fixture_section0_mirror    engine
run "E. a wrong count in a source set's own content"        fires   fixture_source_set         engine
run "F. a repo with no practices/ tree"                     skipped fixture_no_practices_tree  no-engine

# H/I: the multi-source undercount this change fixes (2026-09-19, closing
# BestPractice's todo-2026-09-18-no-stale-counts-undercounts-a-multi-
# source-catalogue.md). A repo whose own practices/ tree IS a declared
# source and which ALSO declares a repo-local source has its real total
# split across more than one directory -- H asserts the correct combined
# figure now reads as current, not stale; I asserts that when this
# environment cannot resolve every declared source, the check reports
# SKIPPED rather than guess and repeat the false violation.
run "H. a repo whose own count spans >1 declared source"    clean   fixture_multi_source_own_count engine
run "I. the same repo, no engine reachable -- SKIPPED"       skipped fixture_multi_source_own_count no-engine

# D': the §0 fixture WITHOUT the engine. This is the pre-2026-09-10
# behaviour and it must still fire, or D proves nothing -- a silent D could
# equally mean the planted count was never in scope.
SCRATCH="$(mktemp -d)"
git clone -q "$ROOT" "$SCRATCH" || fail "D' -- could not clone the fixture"
(
  set -e
  cd "$SCRATCH"
  overlay_check_under_test
  fixture_section0_mirror
  git add -A >/dev/null
  git -c user.name=Test -c user.email=test@example.com commit -q -m "fixture: D-prime"
  remove_engine
  code=0
  out="$(python3 tools/checks/check_no_stale_counts.py 2>&1)" || code=$?
  [ "$code" = 1 ] || { echo "expected exit 1 (the old, manifest-only behaviour), got $code: $out" >&2; exit 1; }
  printf '%s' "$out" | grep -q 'catalogue-carries-stories.md' \
    || { echo "fired, but not inside the §0 mirror: $out" >&2; exit 1; }
)
if [ $? -eq 0 ]; then
  pass "D'. the §0 mirror with no engine still fires (D is testing the fix)"
else
  fail "D'. the §0 mirror with no engine still fires (D is testing the fix)"
fi
rm -rf "$SCRATCH"

# G. a root git cannot list. The practices/ guard is reached first, so the
# fixture carries a practices/ tree with an active practice in it and is
# deliberately NOT a git repository.
NONGIT="$(mktemp -d)"
mkdir -p "$NONGIT/practices"
printf 'status: active\n\n## Rule\nx\n## Detail\ny\n' > "$NONGIT/practices/some-practice.md"
out="$(PRECEDENT_CHECK_ROOT="$NONGIT" python3 tools/checks/check_no_stale_counts.py 2>&1)"; code=$?
if [ "$code" = 2 ] && printf '%s' "$out" | grep -q 'git ls-files'; then
  pass "G. a root git cannot list reports SKIPPED, not a clean tree"
else
  fail "G. a root git cannot list -- expected exit 2 naming git ls-files, got $code: $out"
fi
rm -rf "$NONGIT"

# B. the real, current, unplanted repo -- last, so a fixture that leaked
# state into $ROOT would show up here.
if out="$(cd "$ROOT" && python3 tools/checks/check_no_stale_counts.py 2>&1)"; then
  pass "B. clean on the real, current repo"
else
  fail "B. not clean on the real, current repo: $out"
fi

exit $status
