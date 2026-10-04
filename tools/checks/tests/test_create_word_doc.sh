#!/bin/bash
# Two-direction test for check_create_word_doc.py, built on its own scratch
# fixture (practice: fixture-owns-its-state) rather than assuming a
# particular repo has or lacks the script:
#   1. no tools/create_word_doc.py at all -- require SKIPPED (exit 2), not
#      a pass and not a violation;
#   2. a truncated stand-in (too small, no practice citation) -- require
#      the check to fire and name the specific findings;
#   3. the real script run end to end on a small manuscript -- require a
#      .docx. The script installs python-docx itself when it is missing, so
#      this step never skips for want of the package: a skip would hide the
#      very gap (a shipped script whose package nothing installed) that the
#      self-install exists to close.
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

mkdir -p "$SCRATCH/book-sample"
printf '# Sample\n\n## Part I\n### One\nSome **bold** text.\n\n- a\n- b\n' \
  > "$SCRATCH/book-sample/MANUSCRIPT.md"
if ! python3 "$SET_ROOT/tools/create_word_doc.py" "$SCRATCH/book-sample/MANUSCRIPT.md" \
    --out "$SCRATCH/out/Sample.docx" --date 2026-01-01 > /dev/null \
    || [[ ! -s "$SCRATCH/out/Sample.docx" ]]; then
  echo "FAIL: tools/create_word_doc.py did not write a .docx from a small manuscript" >&2
  exit 1
fi
echo "ok: tools/create_word_doc.py writes a .docx end to end (installing python-docx if missing)"

# A "> " block is a block quotation: Word's Quote style, indented, and no
# ">" left anywhere in the text (Morgan, 2026-10-04: the markers were
# printing as literal text in the Joseph manuscript's Word file).
printf '# Sample\n\n## Part I\nBody.\n\n> One *verse*.\n>\n> Two.\n\nAfter.\n' \
  > "$SCRATCH/book-sample/MANUSCRIPT.md"
python3 "$SET_ROOT/tools/create_word_doc.py" "$SCRATCH/book-sample/MANUSCRIPT.md" \
  --out "$SCRATCH/out/Quote.docx" --date 2026-01-01 > /dev/null
if ! OUT="$(python3 - "$SCRATCH/out/Quote.docx" <<'PY'
import sys
from docx import Document
d = Document(sys.argv[1])
quotes = [p for p in d.paragraphs if p.style.name == "Quote"]
assert [p.text for p in quotes] == ["One verse.", "Two."], [p.text for p in quotes]
assert not any(">" in p.text for p in d.paragraphs), "a > marker reached the text"
style = d.styles["Quote"]
assert style.paragraph_format.left_indent and style.paragraph_format.right_indent
assert style.font.italic is False
PY
)"; then
  echo "FAIL: a > block did not become an indented Quote-style block quotation" >&2
  exit 1
fi
echo "ok: a > block becomes an indented, upright Quote-style block quotation"
