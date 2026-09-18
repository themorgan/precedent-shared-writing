#!/usr/bin/env python3
"""create_word_doc.py -- convert a book-*/MANUSCRIPT.md into a .docx,
with a confidential-draft footer stamped on every page.

# practice: create-word-doc

Parses the manuscript's plain Markdown (headings up to ###, **bold**,
*italic*, "- " bullet lists, and multi-line blocks such as song lyrics
where each physical line is a hard break within one paragraph) and
renders it as a Word document using python-docx's built-in Title/
Heading 1/Heading 2/List Bullet styles, so the result carries real
heading structure (Word's Navigation Pane, an auto-updating TOC) rather
than merely looking like headings.

Every page's footer carries two centered lines:
  Page <n> of <total>
  CONFIDENTIAL - DRAFT BOOK: <SHORT NAME> - <date>
using live PAGE/NUMPAGES fields so the count stays correct after Word
repaginates the content.

Every Part (##) and chapter (###) heading starts on a new page -- a
page break before it, not after the previous paragraph, so a chapter
that ends mid-page never bleeds into the next one's heading. The title
page is the one exception: nothing precedes it, so no break is needed.

Default page is A4, default line spacing is 1.3x. A "Words: <count>"
line (with an optional trailing parenthetical, e.g. "(PART 1)") is
replaced with a live Word NUMWORDS field and the parenthetical dropped
-- so the count always reflects the whole manuscript and never goes
stale the way a number typed once into the source would.

Usage:
  python3 tools/create_word_doc.py book-joseph/MANUSCRIPT.md --out /path/to/Joseph.docx
  python3 tools/create_word_doc.py book-moses/MANUSCRIPT.md --out /path/to/Moses.docx --short-name Moses
  python3 tools/create_word_doc.py book-joseph/MANUSCRIPT.md --out /path/to/Joseph.docx --no-footer

The short book name defaults to the manuscript's book-*/ directory name
with "book-" stripped and the remainder title-cased (book-joseph ->
Joseph). The date defaults to today in Buenos Aires time (this repo's
own dates-are-Buenos-Aires-time convention -- see local/practices/ or
the universal source's buenos-aires-dates practice), overridable with
--date for a reproducible build.

The output .docx is a generated deliverable, not a source file: this
script never writes into the repo itself, and the caller is responsible
for where the file goes (a scratch path, sent straight to the person who
asked for it).
"""
import argparse
import pathlib
import re
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import precedent_time  # noqa: E402  (practice: timestamps-carry-offset)

INLINE_RE = re.compile(r"(\*\*[^*]+?\*\*|\*[^*]+?\*)")
# practice: create-word-doc -- a manuscript's own word-count line becomes a
# live NUMWORDS field instead of a number that goes stale as soon as the
# text changes; any trailing "(PART 1)"-style note is dropped with it.
WORDS_LINE_RE = re.compile(r"^Words:\s*[\d,]+\s*(\(.*\))?\s*$", re.IGNORECASE)


def parse_inline(text):
    """Split a line into (text, bold, italic) runs on **bold**/*italic*."""
    runs = []
    last = 0
    for m in INLINE_RE.finditer(text):
        if m.start() > last:
            runs.append((text[last : m.start()], False, False))
        token = m.group(0)
        if token.startswith("**"):
            runs.append((token[2:-2], True, False))
        else:
            runs.append((token[1:-1], False, True))
        last = m.end()
    if last < len(text):
        runs.append((text[last:], False, False))
    if not runs:
        runs.append(("", False, False))
    return runs


def group_blocks(lines):
    """Blank-line-separated blocks, except a heading line always starts
    and ends its own block even with no blank line around it -- the
    manuscript's section headers are immediately followed by body text
    with no blank line, and merging them would leak the '#' markers into
    the paragraph as literal text."""
    is_heading = lambda l: re.match(r"^#{1,3}\s", l)
    blocks, current = [], []

    def flush():
        if current:
            blocks.append(list(current))
            current.clear()

    for line in lines:
        if line.strip() == "":
            flush()
        elif is_heading(line):
            flush()
            blocks.append([line])
        else:
            current.append(line)
    flush()
    return blocks


def add_field(paragraph, instr, cached_text="1"):
    """Insert a live Word field (e.g. PAGE, NUMPAGES) into a paragraph."""
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    run._r.append(begin)

    run = paragraph.add_run()
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = f" {instr} "
    run._r.append(instr_el)

    run = paragraph.add_run()
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    run._r.append(sep)

    paragraph.add_run(cached_text)

    run = paragraph.add_run()
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(end)


def build_doc(manuscript_path, short_name, add_footer, date_str):
    text = manuscript_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    blocks = group_blocks(lines)

    doc = Document()
    doc.styles["Normal"].font.name = "Times New Roman"
    doc.styles["Normal"].font.size = Pt(12)
    doc.styles["Normal"].paragraph_format.line_spacing = 1.3  # practice: create-word-doc

    section = doc.sections[0]
    section.page_width = Mm(210)  # A4 -- practice: create-word-doc
    section.page_height = Mm(297)
    for side in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(section, side, Inches(1))

    word_count_cache = str(len(text.split()))

    saw_title = False
    last_para = None  # practice: create-word-doc (chapter page breaks)
    # A heading with no body of its own -- a "## Part" immediately followed
    # by a "### Chapter" and no prose between them, e.g. book-joseph's own
    # "Part II" -> "Introduction" -- must NOT also force its own break: that
    # break has nowhere to land but inside the Part heading's own paragraph,
    # which is exactly "a page break right after the heading name" (Morgan,
    # 2026-09-18, reported on Word desktop macOS). Track whether last_para
    # is itself a heading we just broke to; skip the next break when it is,
    # so two headings with nothing between them stack on the SAME page.
    last_was_heading = False
    for block in blocks:
        first = block[0]

        if not saw_title and re.match(r"^# ", first) and len(block) == 1:
            last_para = doc.add_heading(first[2:].strip(), level=0)
            saw_title = True
            last_was_heading = False
            continue

        if re.match(r"^## ", first) and len(block) == 1:
            # practice: create-word-doc (chapter page breaks) -- the break
            # is an explicit page-break RUN appended to the END of the
            # paragraph that comes BEFORE this heading, never a property
            # set on the heading paragraph itself. That way the break lives
            # in a different, earlier paragraph and can't land after the
            # heading's own text -- the heading paragraph carries no
            # page-break marking of its own at all.
            if last_para is not None and not last_was_heading:
                last_para.add_run().add_break(WD_BREAK.PAGE)
            last_para = doc.add_heading(first[3:].strip(), level=1)
            last_was_heading = True
            continue

        if re.match(r"^### ", first) and len(block) == 1:
            if last_para is not None and not last_was_heading:
                last_para.add_run().add_break(WD_BREAK.PAGE)
            last_para = doc.add_heading(first[4:].strip(), level=2)
            last_was_heading = True
            continue

        if all(re.match(r"^-\s+", l.strip()) for l in block):
            for l in block:
                p = doc.add_paragraph(style="List Bullet")
                for run_text, bold, italic in parse_inline(re.sub(r"^-\s+", "", l.strip())):
                    r = p.add_run(run_text)
                    r.bold = bold
                    r.italic = italic
            last_para = p
            last_was_heading = False
            continue

        p = doc.add_paragraph()
        for idx, l in enumerate(block):
            stripped = l.strip()
            if WORDS_LINE_RE.match(stripped):
                p.add_run("Words: ")
                add_field(p, "NUMWORDS", cached_text=word_count_cache)
            else:
                for run_text, bold, italic in parse_inline(stripped):
                    r = p.add_run(run_text)
                    r.bold = bold
                    r.italic = italic
            if idx < len(block) - 1:
                p.add_run().add_break(WD_BREAK.LINE)
        last_para = p
        last_was_heading = False

    if add_footer:
        footer = section.footer
        footer.is_linked_to_previous = False

        page_para = footer.paragraphs[0]
        page_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        page_para.add_run("Page ")
        add_field(page_para, "PAGE")
        page_para.add_run(" of ")
        add_field(page_para, "NUMPAGES")

        conf_para = footer.add_paragraph()
        conf_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        conf_para.add_run(
            f"CONFIDENTIAL - DRAFT BOOK: {short_name.upper()} - {date_str}"
        )

    return doc


def derive_short_name(manuscript_path):
    book_dir = None
    for parent in manuscript_path.resolve().parents:
        if parent.name.startswith("book-"):
            book_dir = parent.name
            break
    if not book_dir:
        raise SystemExit(
            f"could not derive a short book name from {manuscript_path} "
            "(expected it under a book-*/ directory) -- pass --short-name"
        )
    return book_dir[len("book-") :].capitalize()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("manuscript", type=pathlib.Path, help="path to a book-*/MANUSCRIPT.md")
    ap.add_argument("--out", type=pathlib.Path, required=True, help="output .docx path")
    ap.add_argument(
        "--short-name",
        default=None,
        help="short book name for the footer (default: derived from the book-*/ directory name)",
    )
    ap.add_argument(
        "--date",
        default=None,
        help="date for the footer, YYYY-MM-DD (default: today, Buenos Aires time)",
    )
    ap.add_argument(
        "--no-footer",
        action="store_true",
        help="skip the Page X of Y / CONFIDENTIAL footer",
    )
    args = ap.parse_args()

    if not args.manuscript.is_file():
        sys.exit(f"error: {args.manuscript} does not exist")

    short_name = args.short_name or derive_short_name(args.manuscript)
    # practice: timestamps-carry-offset -- one shared module resolves the zone
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    date_str = args.date or precedent_time.today(repo_root)

    doc = build_doc(args.manuscript, short_name, not args.no_footer, date_str)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(args.out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
