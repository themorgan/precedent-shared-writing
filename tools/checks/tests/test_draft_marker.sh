#!/bin/bash

# A fixture commit is not a person's commit: the global commit backstop
# (commit-identity.sh, 2026-09-07) reaches the throwaway repositories this
# test builds and would refuse them.
export PRECEDENT_ALLOW_ANY_AUTHOR=1
# Multi-direction test for check_draft_marker.py.
#
#   A.  a live draft marker in tracked markdown           -- must fire;
#   B.  the real, current, unplanted repo                 -- must be clean,
#       which also covers the marker's own illustration inside backtick
#       code, the way the practice file itself writes it;
#   C.  the same marker inside a §1 mirror (process/upstream/ plus a
#       process/manifest.json naming it)                  -- must be silent;
#   D.  the same marker inside a §0 mirror (a precedent.json-declared
#       source path, NO process/manifest.json)            -- must be silent;
#   E.  a live marker in a SOURCE SET's own content, with precedent.json
#       declaring `path: "."`                             -- must still fire;
#   F.  a root git cannot list                            -- must SKIP (2).
#
# WHY C, D AND E ARE NEW (2026-09-10). This check had NO mirror exclusion at
# all, while scanning the identical file set as check_no_stale_counts.py --
# every tracked `*.md` in the repo. So it reached a consuming repo's
# vendored copy of somebody else's catalogue, where a leftover marker is
# real but not actionable: editing a mirror is forbidden and the next sync
# overwrites it. `no-stale-counts` got the exclusion because it FIRED in a
# real install; this one had simply never been pointed at a repo with a
# mirror in it. Found auditing the rest of this set's checks alongside the
# `source-checks-adopt-engine-helpers` fix -- which is the whole reason
# that audit was asked for.
#
# E is the over-exclusion control. mirrored_prefixes() deliberately does
# not treat the repo root as a mirror, because a source set declares
# `path: "."` and its content is hand-authored; blinding this check to a
# practice set's own drafts would be a worse failure than the one fixed.
set -uo pipefail
cd "$(dirname "$0")/../../.."
ROOT="$(pwd)"

# precedent_resolve.py is not vendored here, and should not be: upstream
# puts it in CONSUMER_ENGINE_FILES but not ENGINE_FILES, because a practice
# set resolves no catalogue. The engine cases therefore need a BestPractice
# clone, found the way `precedent_vendor_engine.py refresh <clone>` finds
# one -- told, not guessed. No stub: a stub would test the stub. Without a
# clone those cases report SKIPPED and do not fail the suite, which is a
# real gap, recorded in
# [TODO.md](../../../TODO.md#engine-cases-need-a-bestpractice-clone); set
# PRECEDENT_REQUIRE_ENGINE_CASES=1 to turn the skip into a failure.
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

MARKER_LINE='**➡️ FILL IN THE NUMBERS ONCE FINANCE CONFIRMS THEM ⬅️**'

plant_marker_in () {
  mkdir -p "$(dirname "$1")"
  {
    echo "# A document"
    echo
    echo "Some finished prose here."
    echo
    echo "$MARKER_LINE"
    echo
    echo "More finished prose."
  } > "$1"
}

overlay_check_under_test () {
  # `git clone` carries COMMITTED state only, so without this every fixture
  # runs whatever is on HEAD rather than the script being edited -- a test
  # that is confidently testing the wrong version. Cost a real debugging
  # detour in this suite's sibling on 2026-09-10.
  cp "$ROOT/tools/checks/check_draft_marker.py" tools/checks/
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

declare_source () {   # $1 = path to declare as a source
  python3 - "$1" <<'PY'
import json, pathlib, sys
path = sys.argv[1]
p = pathlib.Path('precedent.json')
d = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
srcs = d.setdefault('sources', [])
if not any((s or {}).get('path') == path for s in srcs):
    srcs.append({'name': 'precedent', 'path': path})
p.write_text(json.dumps(d, indent=2, sort_keys=True) + '\n', encoding='utf-8')
PY
}

fixture_plain_marker () { plant_marker_in planted-draft.md; }

fixture_section1_mirror () {
  mkdir -p process/upstream
  cat > process/manifest.json <<'JSON'
{"upstream": {"repo": "https://example.invalid/upstream", "vendored_at": "process/upstream", "commit": "0000000000000000000000000000000000000000"}}
JSON
  plant_marker_in process/upstream/MIRRORED.md
}

fixture_section0_mirror () {
  rm -f process/manifest.json
  declare_source precedent/universal
  plant_marker_in precedent/universal/practices/some-upstream-practice.md
  if [ -e process/manifest.json ]; then
    echo "fixture bug: the §0 fixture must have no process/manifest.json" >&2
    return 1
  fi
}

fixture_source_set () {
  rm -f process/manifest.json
  declare_source .
  plant_marker_in planted-draft.md
}

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
    fail "$label -- could not clone the fixture"; rm -rf "$scratch"; return 0
  fi
  (
    set -e
    cd "$scratch"
    overlay_check_under_test
    "$fixture"
    if [ "$want_engine" = engine ]; then install_engine; else remove_engine; fi
    git add -A >/dev/null
    git -c user.name=Test -c user.email=test@example.com commit -q -m "fixture: $label"
    code=0
    out="$(python3 tools/checks/check_draft_marker.py 2>&1)" || code=$?
    # A non-zero exit is not evidence on its own: assert the message
    # (control-asserts-which-failure).
    case "$expect" in
      fires)
        [ "$code" = 1 ] || { echo "expected exit 1, got $code: $out" >&2; exit 1; }
        printf '%s' "$out" | grep -q 'VIOLATION: draft-marker' \
          || { echo "fired without this check's header: $out" >&2; exit 1; }
        printf '%s' "$out" | grep -q 'leftover draft marker' \
          || { echo "fired, but not on the planted marker: $out" >&2; exit 1; } ;;
      clean)
        [ "$code" = 0 ] || { echo "expected exit 0, got $code: $out" >&2; exit 1; }
        [ -z "$out" ] || { echo "clean run was not silent: $out" >&2; exit 1; } ;;
    esac
  )
  if [ $? -eq 0 ]; then pass "$label"; else fail "$label"; fi
  rm -rf "$scratch"
}

run "A. a live draft marker in tracked markdown"       fires fixture_plain_marker   no-engine
run "C. the same marker inside a §1 mirror"            clean fixture_section1_mirror no-engine
run "C+. the §1 mirror, engine present -- unchanged"   clean fixture_section1_mirror engine
run "D. the same marker inside a §0 mirror"            clean fixture_section0_mirror engine
run "E. a live marker in a source set's own content"   fires fixture_source_set      engine

# D': the §0 fixture with NO engine must still fire. Without this, a silent
# D could mean the marker was never in scope rather than correctly excluded.
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
  out="$(python3 tools/checks/check_draft_marker.py 2>&1)" || code=$?
  [ "$code" = 1 ] || { echo "expected exit 1 (no engine, no manifest, so no exclusion), got $code: $out" >&2; exit 1; }
  printf '%s' "$out" | grep -q 'some-upstream-practice.md' \
    || { echo "fired, but not inside the §0 mirror: $out" >&2; exit 1; }
)
if [ $? -eq 0 ]; then
  pass "D'. the §0 mirror with no engine still fires (D is testing the fix)"
else
  fail "D'. the §0 mirror with no engine still fires (D is testing the fix)"
fi
rm -rf "$SCRATCH"

# F. a root git cannot list. An empty file list is exactly what a clean tree
# looks like, so this must report SKIPPED rather than a silent pass.
NONGIT="$(mktemp -d)"
code=0
out="$(PRECEDENT_CHECK_ROOT="$NONGIT" python3 tools/checks/check_draft_marker.py 2>&1)" || code=$?
if [ "$code" = 2 ] && printf '%s' "$out" | grep -q 'git ls-files'; then
  pass "F. a root git cannot list reports SKIPPED, not a clean tree"
else
  fail "F. a root git cannot list -- expected exit 2 naming git ls-files, got $code: $out"
fi
rm -rf "$NONGIT"

# B. the real, current, unplanted repo -- last, so a fixture that leaked
# state into $ROOT would show up here.
if out="$(cd "$ROOT" && python3 tools/checks/check_draft_marker.py 2>&1)"; then
  pass "B. clean on real content (including the practice file's own backtick-quoted illustration)"
else
  fail "B. not clean on the real, current repo: $out"
fi

exit $status
