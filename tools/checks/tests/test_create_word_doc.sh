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

# 4. --contents: Word's own table of contents on a page of its own before the
#    first Heading 1 -- a "Contents" paragraph in "TOC Heading", a TOC field
#    whose cached result lists the Heading 1 and 2 texts as links to
#    bookmarks on the headings, and the page break in a paragraph of its own
#    after the field. Never w:updateFields: that setting makes Word ask
#    "Do you want to update the fields in this document?" on opening
#    (Morgan, 2026-10-05). And the default build carries none of it.
printf '# Sample\n\nA preface.\n\n## Part I\n### One\nText.\n\n## Part II\n### Two\nMore.\n' \
  > "$SCRATCH/book-sample/MANUSCRIPT.md"
python3 "$SET_ROOT/tools/create_word_doc.py" "$SCRATCH/book-sample/MANUSCRIPT.md" \
  --out "$SCRATCH/out/Contents.docx" --date 2026-01-01 --contents > /dev/null
python3 "$SET_ROOT/tools/create_word_doc.py" "$SCRATCH/book-sample/MANUSCRIPT.md" \
  --out "$SCRATCH/out/Plain.docx" --date 2026-01-01 > /dev/null
if ! OUT="$(python3 - "$SCRATCH/out/Contents.docx" "$SCRATCH/out/Plain.docx" <<'PY' 2>&1
import re, sys, zipfile
import docx

def body(path):
    return [(p.style.name, p.text, p._p.xml) for p in docx.Document(path).paragraphs]

paras = body(sys.argv[1])
names = [(s, t) for s, t, _ in paras]
first_h1 = next(i for i, (s, _t) in enumerate(names) if s == "Heading 1")
head = names.index(("TOC Heading", "Contents"))
assert head < first_h1, "Contents is not before the first Heading 1"
entries = [t for _s, t, _x in paras[head + 1:first_h1 - 1]]
assert entries == ["Part I", "One", "Part II", "Two"], f"cached entries: {entries}"
assert 'w:fldCharType="begin"' in paras[head + 1][2], "field does not open in the first entry"
assert 'TOC \\o "1-2" \\h \\z \\u' in paras[head + 1][2], "TOC instruction missing"
assert 'w:fldCharType="end"' in paras[first_h1 - 2][2], "field does not close in the last entry"
brk = paras[first_h1 - 1]
assert brk[1] == "" and 'w:type="page"' in brk[2] and "fldChar" not in brk[2], \
    "the page break is not a paragraph of its own after the field"
for path in sys.argv[1:]:
    assert "updateFields" not in zipfile.ZipFile(path).read("word/settings.xml").decode(), \
        f"{path} asks Word to update its fields on opening"
xml = "".join(x for _s, _t, x in paras)
anchors = re.findall(r'w:hyperlink [^>]*w:anchor="([^"]+)"', xml)
marks = re.findall(r'w:bookmarkStart [^>]*w:name="([^"]+)"', xml)
assert len(anchors) == 4 and sorted(anchors) == sorted(marks), (anchors, marks)
plain = body(sys.argv[2])
assert not any(s == "TOC Heading" for s, _t, _x in plain), "the default build has a contents page"
PY
)"; then
  echo "FAIL: --contents did not build Word's contents page as specified: $OUT" >&2
  exit 1
fi
echo "ok: --contents puts Word's own TOC, linked to the headings, on its own page; no update-fields prompt"

# 5. A heading straight after the title shares the title's page (Morgan,
#    2026-10-05: a blurbs file's cover held only the logo and the title);
#    later headings still break. --no-section-breaks drops every break.
#    Links print as their text, a "- " item may wrap onto an indented line,
#    a trailing "\" hard break leaves no backslash, and an HTML comment is
#    never text.
printf '<!-- header -->\n# Sample\n\n## First\nSee [the notes](OTHER.md).\\\nNext line.\n\n- one item that\n  wraps\n- two\n\n## Second\nMore.\n' \
  > "$SCRATCH/book-sample/MANUSCRIPT.md"
python3 "$SET_ROOT/tools/create_word_doc.py" "$SCRATCH/book-sample/MANUSCRIPT.md" \
  --out "$SCRATCH/out/Flow.docx" --date 2026-01-01 > /dev/null
python3 "$SET_ROOT/tools/create_word_doc.py" "$SCRATCH/book-sample/MANUSCRIPT.md" \
  --out "$SCRATCH/out/NoBreaks.docx" --date 2026-01-01 --no-section-breaks > /dev/null
if ! OUT="$(python3 - "$SCRATCH/out/Flow.docx" "$SCRATCH/out/NoBreaks.docx" <<'PY' 2>&1
import sys
import docx

def breaks(path):
    return [p.text for p in docx.Document(path).paragraphs if 'w:type="page"' in p._p.xml]

d = docx.Document(sys.argv[1])
texts = [p.text for p in d.paragraphs]
assert not any("<!--" in t for t in texts), "an HTML comment reached the text"
assert texts[0] == "Sample", texts
assert breaks(sys.argv[1]) == ["two"], f"page breaks after: {breaks(sys.argv[1])}"
assert "See the notes.\nNext line." in texts, texts
bullets = [p.text for p in d.paragraphs if p.style.name == "List Bullet"]
assert bullets == ["one item that wraps", "two"], bullets
assert breaks(sys.argv[2]) == [], f"--no-section-breaks still broke after: {breaks(sys.argv[2])}"
PY
)"; then
  echo "FAIL: title page, links, wrapped bullets or --no-section-breaks: $OUT" >&2
  exit 1
fi
echo "ok: a heading after the title shares its page; links, wrapped bullets, comments, --no-section-breaks"

# 6. --header-image: the image in the header of every page but the first,
#    whose own header stays empty and whose footer still carries Page X of Y.
python3 - "$SCRATCH/logo.png" <<'PY'
import struct, sys, zlib
def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
# a 2x2 PNG in the logo purple, written by hand so the test needs no image library
png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0))
       + chunk(b"IDAT", zlib.compress((b"\x00" + b"\x40\x24\x54" * 2) * 2))
       + chunk(b"IEND", b""))
open(sys.argv[1], "wb").write(png)
PY
python3 "$SET_ROOT/tools/create_word_doc.py" "$SCRATCH/book-sample/MANUSCRIPT.md" \
  --out "$SCRATCH/out/Header.docx" --date 2026-01-01 --header-image "$SCRATCH/logo.png" > /dev/null
if ! OUT="$(python3 - "$SCRATCH/out/Header.docx" "$SCRATCH/out/Flow.docx" <<'PY' 2>&1
import sys
import docx

s = docx.Document(sys.argv[1]).sections[0]
assert s.different_first_page_header_footer, "first page is not different"
assert "graphicData" in s.header._element.xml, "no image in the running header"
assert "graphicData" not in s.first_page_header._element.xml, "the first page's header has the image"
first_footer = s.first_page_footer._element.xml
assert "PAGE" in first_footer and "NUMPAGES" in first_footer, "page one lost its Page X of Y"
plain = docx.Document(sys.argv[2]).sections[0]
assert not plain.different_first_page_header_footer, "the default build changed the first page"
assert "graphicData" not in plain.header._element.xml, "the default build has a header image"
PY
)"; then
  echo "FAIL: --header-image did not put the image on every page but the first: $OUT" >&2
  exit 1
fi
echo "ok: --header-image on every page but the first; page one keeps its footer"

# 7. --soft-wraps: a paragraph's lines join with a space; a trailing "\"
#    still breaks. Without it, every source line is a line break (verse).
printf '# Sample\n\nOne wrapped\nparagraph.\n\nKept\\\nbreak.\n' > "$SCRATCH/book-sample/MANUSCRIPT.md"
python3 "$SET_ROOT/tools/create_word_doc.py" "$SCRATCH/book-sample/MANUSCRIPT.md" \
  --out "$SCRATCH/out/Soft.docx" --date 2026-01-01 --soft-wraps > /dev/null
python3 "$SET_ROOT/tools/create_word_doc.py" "$SCRATCH/book-sample/MANUSCRIPT.md" \
  --out "$SCRATCH/out/Hard.docx" --date 2026-01-01 > /dev/null
if ! OUT="$(python3 - "$SCRATCH/out/Soft.docx" "$SCRATCH/out/Hard.docx" <<'PY' 2>&1
import sys
import docx
soft = [p.text for p in docx.Document(sys.argv[1]).paragraphs]
hard = [p.text for p in docx.Document(sys.argv[2]).paragraphs]
assert soft[1:] == ["One wrapped paragraph.", "Kept\nbreak."], soft
assert hard[1:] == ["One wrapped\nparagraph.", "Kept\nbreak."], hard
PY
)"; then
  echo "FAIL: --soft-wraps did not join wrapped lines, or the default did: $OUT" >&2
  exit 1
fi
echo "ok: --soft-wraps joins a wrapped paragraph; a backslash still breaks; the default keeps every line"

# 8. The check fails on any script under tools/ that writes Word's
#    updateFields setting, the shared script or a hand-built one-off.
mkdir -p "$SCRATCH/tools"
cp "$SET_ROOT/tools/create_word_doc.py" "$SCRATCH/tools/create_word_doc.py"
printf 'el = OxmlElement("w:updateFields")\n' > "$SCRATCH/tools/one_off_docx.py"
OUT="$(python3 "$SET_ROOT/tools/checks/check_create_word_doc.py" || true)"
if ! grep -q "one_off_docx.py writes Word's updateFields" <<<"$OUT"; then
  echo "FAIL: the check did not flag a script that writes updateFields: $OUT" >&2
  exit 1
fi
rm "$SCRATCH/tools/one_off_docx.py"
echo "ok: the check fails on a script that makes a document ask to update its fields"
