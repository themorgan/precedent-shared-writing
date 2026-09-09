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
# Then: a repo declaring no output_paths at all must SKIP, not fail.
#
# The fixture creates precedent.json and MANIFEST.json because this source
# repo has neither -- but it APPENDS to whatever it finds rather than
# replacing it (fixture-owns-its-state), so running this in a consuming
# repo, where MANIFEST.json carries 140 real practices, tests the check
# rather than testing what the fixture just deleted.
set -euo pipefail
cd "$(dirname "$0")/../../.."
ROOT="$(pwd)"

seed_repo () {
  mkdir -p deliverables doc-recipes-holder/doc-recipes internal-notes
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

run () {
  local label="$1" expect="$2" fn="$3"
  local scratch; scratch="$(mktemp -d)"
  git clone -q "$ROOT" "$scratch"
  (
    cd "$scratch"
    "$fn"
    out="$(python3 tools/checks/check_deliverables_carry_no_process.py 2>&1)" && got=clean || got=fires
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
        if ! printf '%s' "$out" | grep -q '^SKIPPED: this repo declares no output_paths'; then
          echo "FAIL: $label -- expected the no-output_paths skip, got: $out" >&2; exit 1
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
run "a repo declaring no output_paths"                 skipped plant_no_output_paths

if ! python3 tools/checks/check_deliverables_carry_no_process.py > /dev/null; then
  echo "FAIL: check_deliverables_carry_no_process.py is not clean on the real, current repo" >&2
  exit 1
fi
echo "ok: clean on real content"
