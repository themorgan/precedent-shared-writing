#!/bin/bash
# Multi-direction test for check_deliverables_carry_no_process.py:
#   A. an attribution stamp in an output document        -- must fire;
#   B. a backticked practice slug in an output document  -- must fire;
#   B2. an attribution stamp WRAPPED across a line break -- must fire;
#   B3. a POSSESSIVE stamp ("Morgan's list, DATE") -- must fire; the first
#      version stopped at the name and demanded a comma, so the apostrophe
#      hid five real stamps behind a clean run;
#      the name ends one line and the date starts the next, which is what
#      the first, per-line version of this check missed entirely;
#   C. a link into practices/ from an output document    -- must fire;
#   D. the SAME three tells in a doc-recipes/ file       -- must NOT fire;
#      a recipe's whole job is to state the rules for one file;
#   E. the same tells in a file OUTSIDE any output path  -- must NOT fire;
#   F. a backticked hyphenated word the manifest does not carry -- must
#      NOT fire. This is what stops ordinary English (`push-back`,
#      `two-person`) from reading as a citation, and is the false positive
#      that would get the check switched off, so it is tested, not assumed.
#   G. a bare date with no name ("through 2026-09") and a name with no date
#      -- must NOT fire.
#   J. a slug and a practices/ link inside a section declared under
#      `unpublished_sections` -- must NOT fire. The repo's page builder
#      cuts that section before sending, so no reader sees it;
#   K. the same slug in the section right AFTER a declared one -- must
#      fire. The skip ends at the next heading of any level, and this is
#      what proves it does not run on to the end of the file.
# Then two could-not-run cases, which must SKIP -- exit 2, reported as
# SKIPPED -- and not pass:
#   H. a repo declaring no output_paths at all;
#   I. a repo declaring output_paths that no tracked markdown resolves
#      under. Both returned exit 0 until 2026-09-10 while PRINTING the word
#      SKIPPED, so the runner recorded a PASS -- "a scan with an empty input
#      set printing OK", which precedent_check.py's own docstring says has
#      bitten this project four times. The exit code is asserted now, not
#      just the message: the message was already right and the answer was
#      still wrong. This test tolerated it too -- its `skipped` branch
#      checked the text and never the status.
#
# The fixture creates precedent.json and MANIFEST.json because this source
# repo has neither -- but it APPENDS to whatever it finds rather than
# replacing it (fixture-owns-its-state), so running this in a consuming
# repo, where MANIFEST.json carries 140 real practices, tests the check
# rather than testing what the fixture just deleted.
set -euo pipefail
cd "$(dirname "$0")/../../.."
ROOT="$(pwd)"

overlay_check_under_test () {
  # `git clone` carries COMMITTED state only, so without this every fixture
  # runs whatever is on HEAD rather than the script being edited -- a test
  # confidently exercising the wrong version of its own subject. Cost a real
  # debugging detour in a sibling suite on 2026-09-10.
  cp "$ROOT/tools/checks/check_deliverables_carry_no_process.py" tools/checks/
}

seed_repo () {
  mkdir -p deliverables doc-recipes-holder/doc-recipes internal-notes
  # One CLEAN in-scope document, in every fixture. Since 2026-09-10 a scan
  # that examined nothing reports SKIPPED rather than OK, so a fixture whose
  # point is SCOPING -- D (a doc-recipes/ file is exempt) and E (a file
  # outside every output path) -- has to give the check something real to
  # scan, or "clean" and "did not look" are the same result again. It also
  # makes each of those cases strictly stronger than before: the check
  # provably ran and provably did not report the out-of-scope file.
  cat > deliverables/index.md <<'CLEAN'
# Index
Plain prose with nothing in it that this check looks for.
CLEAN
  python3 - <<'PY'
import json, pathlib
p = pathlib.Path('precedent.json')
d = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
for path in ('deliverables', 'doc-recipes-holder'):
    if path not in (d.get('output_paths') or []):
        d.setdefault('output_paths', []).append(path)
p.write_text(json.dumps(d, indent=2, sort_keys=True) + '\n', encoding='utf-8')

m = pathlib.Path('MANIFEST.json')
d = json.loads(m.read_text(encoding='utf-8')) if m.exists() else {}
have = {e.get('slug') for e in d.get('practices', [])}
if 'assorted-notes' not in have:
    d.setdefault('practices', []).append(
        {'slug': 'assorted-notes', 'level': 'individual',
         'source': 'precedent-individual'})
m.write_text(json.dumps(d, indent=2, sort_keys=True) + '\n', encoding='utf-8')
PY
  git add -A >/dev/null
}

plant_stamp () {
  seed_repo
  cat > deliverables/page.md <<'MD'
# Page
The middle tier is a program rather than an audience (Morgan, 2026-09-08).
MD
  git add -A >/dev/null
}

plant_wrapped_stamp () {
  # The shape that got through the first version: these files are hard
  # wrapped, so the name ends one line and the date starts the next. A
  # per-line scan saw neither half. POSITIONING.md was exactly this.
  seed_repo
  cat > deliverables/page.md <<'MD'
# Page
That is the rule for this whole idea, in every piece of copy. Morgan,
2026-09-08.
MD
  git add -A >/dev/null
}

plant_possessive_stamp () {
  # "Morgan's list, 2026-09-08" -- the shape the first version could not
  # see at all: `[a-zA-Z]+` stops at the name and the next character is an
  # apostrophe, not the comma the pattern demanded. Five real stamps hid
  # behind it while the check reported a clean run.
  seed_repo
  cat > deliverables/page.md <<'MD'
# Page
Morgan's list, 2026-09-08. Unranked and unargued.
MD
  git add -A >/dev/null
}

plant_slug () {
  seed_repo
  cat > deliverables/page.md <<'MD'
# Page
Parked material lives in the notes file (`assorted-notes`).
MD
  git add -A >/dev/null
}

plant_internal_link () {
  seed_repo
  cat > deliverables/page.md <<'MD'
# Page
The convention is written up in [assorted-notes](practices/assorted-notes.md).
MD
  git add -A >/dev/null
}

plant_recipe () {
  seed_repo
  cat > doc-recipes-holder/doc-recipes/PAGE.recipe.md <<'MD'
# Recipe: page.md
Headings are headline case (`assorted-notes`), decided by Morgan, 2026-09-08,
and the rule itself is in [assorted-notes](practices/assorted-notes.md).
MD
  git add -A >/dev/null
}

plant_outside_output_path () {
  seed_repo
  cat > internal-notes/working.md <<'MD'
# Working note
Decided this way (Morgan, 2026-09-08) per (`assorted-notes`), see
[it](practices/assorted-notes.md).
MD
  git add -A >/dev/null
}

plant_english_that_looks_like_a_slug () {
  # The token must be one no manifest anywhere carries. The first version
  # used `push-back`, which is a real universal slug -- true to the point
  # being made, and false as a fixture: in the consuming repo this case
  # first ran in, MANIFEST.json carries push-back, so the check fired and
  # the case failed on state it inherited rather than owned
  # (fixture-owns-its-state). What is actually invariant, and what this
  # asserts, is that a backticked hyphenated word ABSENT from the manifest
  # does not fire.
  seed_repo
  cat > deliverables/page.md <<'MD'
# Page
We expect `no-such-slug-anywhere` and a `two-person` video format.
MD
  git add -A >/dev/null
}

plant_innocent_dates_and_names () {
  # The pattern got wider to catch the possessive, so what it must NOT
  # match got more important: a bare date with no name in front of it,
  # names with no date after them, and a date reached without the comma
  # the pattern requires.
  seed_repo
  cat > deliverables/page.md <<'MD'
# Page
Through 2026-09 the plan is unchanged. Dani and Morgan record the videos.
The intensive runs from 2026-09-08 for one week, in Buenos Aires.
MD
  git add -A >/dev/null
}

declare_unpublished () {
  python3 - <<'DECLARE'
import json, pathlib
p = pathlib.Path('precedent.json')
d = json.loads(p.read_text(encoding='utf-8'))
d.setdefault('unpublished_sections', []).append(
    {'path': 'deliverables/page.md', 'heading': 'Maintainer List'})
p.write_text(json.dumps(d, indent=2, sort_keys=True) + '\n', encoding='utf-8')
DECLARE
}

plant_slug_in_unpublished_section () {
  seed_repo
  declare_unpublished
  cat > deliverables/page.md <<'MD'
# Page
Plain prose for the reader.

## Maintainer List
- (`assorted-notes`), see [it](practices/assorted-notes.md)
MD
  git add -A >/dev/null
}

plant_slug_after_unpublished_section () {
  seed_repo
  declare_unpublished
  cat > deliverables/page.md <<'MD'
# Page

## Maintainer List
- (`assorted-notes`), see [it](practices/assorted-notes.md)

## For Readers
Parked material lives in the notes file (`assorted-notes`).
MD
  git add -A >/dev/null
}

plant_no_output_paths () {
  # REMOVE output_paths rather than assume none. In this source repo
  # precedent.json has none and doing nothing looked equivalent; in a
  # consuming repo it declares real ones, so the check scanned them, found
  # them clean, and the case failed expecting a skip it had done nothing to
  # cause -- the second fixture-owns-its-state slip in this one file.
  python3 - <<'CLEAR'
import json, pathlib
p = pathlib.Path('precedent.json')
if p.exists():
    d = json.loads(p.read_text(encoding='utf-8'))
    d.pop('output_paths', None)
    p.write_text(json.dumps(d, indent=2, sort_keys=True) + '\n', encoding='utf-8')
CLEAR
  cat > page.md <<'MD'
# Page
Decided (Morgan, 2026-09-08).
MD
  git add -A >/dev/null
}

plant_output_paths_with_nothing_under_them () {
  # output_paths declared, and no tracked markdown resolving under any of
  # them -- the declaration and the tree disagree. The directory is created
  # so the path is not merely a typo, and left EMPTY so nothing is in scope;
  # git tracks no empty directory, which is exactly the point.
  python3 - <<'DECLARE'
import json, pathlib
p = pathlib.Path('precedent.json')
d = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
d['output_paths'] = ['no-such-deliverables']
p.write_text(json.dumps(d, indent=2, sort_keys=True) + '\n', encoding='utf-8')
DECLARE
  mkdir -p no-such-deliverables
  git add -A >/dev/null
}

run () {
  local label="$1" expect="$2" fn="$3"
  local scratch; scratch="$(mktemp -d)"
  git clone -q "$ROOT" "$scratch"
  (
    cd "$scratch"
    overlay_check_under_test
    "$fn"
    code=0
    out="$(python3 tools/checks/check_deliverables_carry_no_process.py 2>&1)" || code=$?
    case "$code" in 0) got=clean ;; 2) got=skipped ;; *) got=fires ;; esac
    case "$expect" in
      # A non-zero exit is not evidence on its own: assert the message
      # (control-asserts-which-failure).
      fires)
        if [ "$got" != fires ]; then
          echo "FAIL: $label -- expected a violation, got: $out" >&2; exit 1
        fi
        if ! printf '%s' "$out" | grep -q 'VIOLATION: deliverables-carry-no-process'; then
          echo "FAIL: $label -- fired, but not with this check's message: $out" >&2; exit 1
        fi ;;
      clean)
        if [ "$got" != clean ]; then
          echo "FAIL: $label -- expected clean, got: $out" >&2; exit 1
        fi ;;
      skipped)
        # Exit 2 AND the reason. Asserting only the message is what let the
        # exit-0 silent pass stand: the text said SKIPPED and the runner
        # read PASS.
        if [ "$code" != 2 ]; then
          echo "FAIL: $label -- expected exit 2 (SKIPPED), got $code: $out" >&2; exit 1
        fi
        if ! printf '%s' "$out" | grep -q '^SKIPPED: this repo declares'; then
          echo "FAIL: $label -- exited 2 without a reason naming the declaration: $out" >&2; exit 1
        fi ;;
    esac
    echo "ok: $label ($got, as required)"
  )
  local status=$?
  rm -rf "$scratch"
  return $status
}

run "attribution stamp in an output document"          fires   plant_stamp
run "attribution stamp wrapped across two lines"       fires   plant_wrapped_stamp
run "possessive stamp (\"Morgan's list, DATE\")"          fires   plant_possessive_stamp
run "backticked practice slug in an output document"   fires   plant_slug
run "link into practices/ from an output document"     fires   plant_internal_link
run "the same three tells inside doc-recipes/"         clean   plant_recipe
run "the same tells outside every output path"         clean   plant_outside_output_path
run "hyphenated English that is not in the manifest"   clean   plant_english_that_looks_like_a_slug
run "a bare date, and names with no date"              clean   plant_innocent_dates_and_names
run "J. slug and link inside a declared unpublished section" clean plant_slug_in_unpublished_section
run "K. slug in the section after a declared one"      fires   plant_slug_after_unpublished_section
run "H. a repo declaring no output_paths"               skipped plant_no_output_paths
run "I. output_paths with no document under them"      skipped plant_output_paths_with_nothing_under_them

# The real, current repo. This assertion used to be hardcoded to "declares
# no output_paths", which is only ever true of the repo this test was
# authored against -- checks-plant-their-state: what "the real repo"
# declares is itself state the test has to read, not assume, since a
# materialized copy of this same file runs against whatever repo it was
# vendored into. A repo WITH output_paths gets the honest answer for that
# case instead: exit 0, a real scan (asserted as "OK:" specifically, so a
# crash reported as exit 0 by accident would not pass this silently).
code=0
out="$(python3 tools/checks/check_deliverables_carry_no_process.py 2>&1)" || code=$?
if python3 -c "import json,sys; sys.exit(0 if json.load(open('precedent.json')).get('output_paths') else 1)" 2>/dev/null; then
  if [ "$code" != 0 ]; then
    echo "FAIL: on the real, current repo -- expected exit 0 (this repo declares output_paths), got $code: $out" >&2
    exit 1
  fi
  case "$out" in
    OK:*) ;;
    *) echo "FAIL: on the real, current repo -- exit 0 but output did not start with 'OK:': $out" >&2
       exit 1 ;;
  esac
  echo "ok: reports a real scan, not SKIPPED, on the real repo (output_paths declared)"
else
  if [ "$code" != 2 ]; then
    echo "FAIL: on the real, current repo -- expected exit 2 (this repo declares no output_paths), got $code: $out" >&2
    exit 1
  fi
  echo "ok: reports SKIPPED, not a pass, on the real repo (no output_paths declared)"
fi
