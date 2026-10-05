#!/usr/bin/env python3
"""create_word_doc.py -- convert a book-*/MANUSCRIPT.md into a .docx,
with a confidential-draft footer stamped on every page.

# practice: create-word-doc

Parses the manuscript's plain Markdown (headings up to ###, **bold**,
*italic* and ***both***, nested either way and carried across a wrapped
line, as Markdown reads them, [links](...) printed as their text, "- " bullet lists whose
items may wrap onto indented lines, "> " block quotations, and
multi-line blocks such as song lyrics where each physical line is a hard
break within one paragraph; HTML comments are dropped) and
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
page is the one exception: nothing precedes it, so no break is needed --
and a heading that follows the title with nothing between them shares
the title's page, so a title never sits alone on an otherwise empty
page. `--no-section-breaks` turns the breaks off altogether, for a
shorter document (notes, a brainstorm) whose sections should flow on.
`--soft-wraps` reads a source wrapped at a fixed width the way Markdown
does: a paragraph's lines join with a space, and only a line ending in a
backslash or two spaces breaks.

`--header-image PATH` puts a small copy of an image (a logo) centered in
the header of every page but the first, which already carries the
cover. add_header_image() does the same for a document built by hand.

A "> " block -- a long excerpt quoted from another text -- becomes a
block quotation, the way a printed book sets one off: indented half an
inch on both sides, a point smaller, tighter line spacing, no quotation
marks, and the ">" characters gone. A bare ">" line inside the block
starts a new paragraph of the same quotation. It uses Word's own "Quote"
style, restyled upright (the stock one is italic, which tires the eye
over a long passage), so the excerpts are findable and restylable in
Word's Styles pane all at once.

Default page is A4, default line spacing is 1.3x. A "Words: <count>"
line (with an optional trailing parenthetical, e.g. "(PART 1)") is
replaced with a live Word NUMWORDS field and the parenthetical dropped
-- so the count always reflects the whole manuscript and never goes
stale the way a number typed once into the source would.

Usage:
  python3 tools/create_word_doc.py book-joseph/MANUSCRIPT.md --out /path/to/Joseph.docx
  python3 tools/create_word_doc.py book-moses/MANUSCRIPT.md --out /path/to/Moses.docx --short-name Moses
  python3 tools/create_word_doc.py book-joseph/MANUSCRIPT.md --out /path/to/Joseph.docx --no-footer
  python3 tools/create_word_doc.py book-joseph/MANUSCRIPT.md --out /path/to/Joseph.docx --contents
  python3 tools/create_word_doc.py notes/NOTES.md --out /path/to/Notes.docx --short-name Notes \
      --no-section-breaks --header-image logo.png

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
import importlib
import pathlib
import re
import site
import subprocess
import sys

DOCX_PACKAGE = "python-docx"


def ensure_docx():
    """Import python-docx, installing it with pip the first time it is missing.

    practice: create-word-doc -- this script is delivered to every repo that
    resolves this set (the practice's ships:), but nothing installs its one
    third-party package, so a fresh container fails on the import. Installing
    at session start would slow every session to serve the few that export a
    Word file, so the script fetches it itself, the same shape as
    ensure_gate_packages in tools/precedent_push_check.py. If pip cannot
    install it, stop with one line naming the command -- never run on
    half-broken."""
    try:
        import docx  # noqa: F401
        return
    except ImportError:
        pass
    print(f"create_word_doc: installing {DOCX_PACKAGE}, which this script needs...",
          file=sys.stderr)
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet", DOCX_PACKAGE],
        capture_output=True, text=True,
    )
    # A --user install can land in a site dir that did not exist when this
    # interpreter started, so it is not on sys.path yet; add it before retrying.
    user_site = site.getusersitepackages()
    if pathlib.Path(user_site).is_dir() and user_site not in sys.path:
        site.addsitedir(user_site)
    importlib.invalidate_caches()
    try:
        import docx  # noqa: F401
    except ImportError:
        tail = (r.stderr or r.stdout or "").strip().splitlines()
        said = f" ({tail[-1]})" if tail else ""
        sys.exit(
            f"error: {DOCX_PACKAGE} is missing and pip could not install it{said}"
            f" -- run `{sys.executable} -m pip install {DOCX_PACKAGE}`, then this again"
        )


ensure_docx()

from docx import Document  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Inches, Mm, Pt  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import precedent_time  # noqa: E402  (practice: timestamps-carry-offset)

# practice: create-word-doc -- emphasis is matched the way Markdown matches
# it, not with one flat pattern: a run of asterisks opens when text follows
# it and closes when text precedes it, and the nearest compatible opener
# wins. A flat pattern could not see *italic* inside **bold**, so
# "**a *b* c**" reached Word as literal asterisks around italic text
# (Morgan, 2026-10-05, the Joseph manuscript's Introduction).
STAR_RUN_RE = re.compile(r"\\\*|\*+")
# Where build_doc's last run left an emphasis-like asterisk unmatched.
STRAY_ASTERISKS = []
# practice: create-word-doc -- a Markdown link prints as its text: the
# target is usually a path inside the source's repository, which means
# nothing to someone reading the Word file.
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)\s]*\)")
# An HTML comment (a file header, a generated-block marker) is never text.
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
BULLET_RE = re.compile(r"^\s*-\s+")
# practice: create-word-doc -- a manuscript's own word-count line becomes a
# live NUMWORDS field instead of a number that goes stale as soon as the
# text changes; any trailing "(PART 1)"-style note is dropped with it.
WORDS_LINE_RE = re.compile(r"^Words:\s*[\d,]+\s*(\(.*\))?\s*$", re.IGNORECASE)
# practice: create-word-doc -- a "> " line is a block quotation, never text
# that starts with a ">" character.
QUOTE_LINE_RE = re.compile(r"^\s*>\s?")


def style_block_quote(doc):
    """Restyle Word's built-in "Quote" style as a book's block quotation:
    indented both sides, upright, a point smaller than the body, a little
    tighter. Spacing between paragraphs is left to the document default, so a
    quotation sits in the text the way any paragraph does. Returns the style."""
    style = doc.styles["Quote"]
    style.font.italic = False
    style.font.size = Pt(11)
    pf = style.paragraph_format
    pf.left_indent = Inches(0.5)
    pf.right_indent = Inches(0.5)
    pf.first_line_indent = Inches(0)
    pf.line_spacing = 1.15
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return style


def quote_paragraphs(block):
    """Split a "> " block into its paragraphs: a bare ">" line separates
    them, and the other lines lose their ">" marker."""
    paras, current = [], []
    for line in block:
        body = QUOTE_LINE_RE.sub("", line, count=1).rstrip()
        if body.strip() == "":
            if current:
                paras.append(current)
                current = []
        else:
            current.append(body.strip())
    if current:
        paras.append(current)
    return paras


def parse_inline(text):
    """Split text into (text, bold, italic) runs on **bold**, *italic* and
    ***both***, nested either way round -- "**a *b* c**" gives a bold run
    with an italic-and-bold middle. A link becomes its text, a trailing
    backslash -- Markdown's hard line break, which the caller already makes
    a real one -- is dropped, and an escaped \\* is a plain asterisk. An
    asterisk nothing closes stays a plain character, as in Markdown.
    The text may hold "\\n" (a line break inside the paragraph); emphasis
    carries across it, so an italic title wrapped over two source lines
    still comes out italic."""
    text = LINK_RE.sub(r"\1", text)
    if text.endswith("\\"):
        text = text[:-1].rstrip()

    # Pieces: plain text (str) or a delimiter run (dict).
    pieces = []
    last = 0
    for m in STAR_RUN_RE.finditer(text):
        if m.start() > last:
            pieces.append(text[last:m.start()])
        if m.group(0) == "\\*":
            pieces.append("*")
        else:
            before = text[m.start() - 1] if m.start() > 0 else " "
            after = text[m.end()] if m.end() < len(text) else " "
            pieces.append(dict(n=len(m.group(0)), left=0, opens=[], closes=[],
                               can_open=not after.isspace(),
                               can_close=not before.isspace()))
        last = m.end()
    if last < len(text):
        pieces.append(text[last:])

    # Match closers to the nearest opener still holding asterisks, two at a
    # time (bold) when both sides have two, else one (italic). Openers
    # skipped over by a match can no longer close anything: they stay plain.
    stack = []
    for piece in pieces:
        if isinstance(piece, str):
            continue
        piece["left"] = piece["n"]
        if piece["can_close"]:
            while piece["left"] and stack:
                opener = stack[-1]
                use = 2 if opener["left"] >= 2 and piece["left"] >= 2 else 1
                kind = "bold" if use == 2 else "italic"
                opener["left"] -= use
                piece["left"] -= use
                opener["opens"].append(kind)
                piece["closes"].append(kind)
                if not opener["left"]:
                    stack.pop()
        if piece["can_open"] and piece["left"]:
            stack.append(piece)

    runs = []
    depth = {"bold": 0, "italic": 0}

    def emit(chunk):
        if not chunk:
            return
        style = (depth["bold"] > 0, depth["italic"] > 0)
        if runs and runs[-1][1:] == style:
            runs[-1] = (runs[-1][0] + chunk,) + style
        else:
            runs.append((chunk,) + style)

    plain = "".join(x if isinstance(x, str) else "*" * x["n"] for x in pieces)
    at = 0
    for piece in pieces:
        if isinstance(piece, str):
            emit(piece)
            at += len(piece)
            continue
        if piece["left"] and (piece["can_open"] or piece["can_close"]):
            STRAY_ASTERISKS.append(plain[max(0, at - 40):at + 40])
        at += piece["n"]
        for kind in piece["closes"]:
            depth[kind] -= 1
        if piece["opens"]:
            emit("*" * piece["left"])  # unmatched, outside the emphasis
            for kind in piece["opens"]:
                depth[kind] += 1
        else:
            emit("*" * piece["left"])
    if not runs:
        runs.append(("", False, False))
    return runs


def add_inline(paragraph, lines, soft_wraps):
    """Add one paragraph's lines as runs, parsing emphasis across the whole
    paragraph so a *phrase* wrapped over two source lines stays one italic
    phrase. Lines end as line_end() says: a space when soft_wraps joins
    them, otherwise a line break."""
    joined = []
    for idx, line in enumerate(lines):
        body = line.strip()
        if body.endswith("\\"):
            body = body[:-1].rstrip()
        joined.append(body)
        if idx < len(lines) - 1:
            hard = (not soft_wraps or line.rstrip().endswith("\\")
                    or line.endswith("  "))
            joined.append("\n" if hard else " ")
    for run_text, bold, italic in parse_inline("".join(joined)):
        for n, chunk in enumerate(run_text.split("\n")):
            if n:
                paragraph.add_run().add_break(WD_BREAK.LINE)
            if chunk:
                r = paragraph.add_run(chunk)
                r.bold = bold
                r.italic = italic


def line_end(paragraph, line, soft_wraps):
    """End one source line inside a paragraph. By default every line is a
    line of its own -- verse, lyrics. With soft_wraps, a source wrapped at
    a fixed width reads as Markdown does: the lines join with a space, and
    only a line ending in a backslash or two spaces breaks."""
    if soft_wraps and not (line.rstrip().endswith("\\") or line.endswith("  ")):
        paragraph.add_run(" ")
    else:
        paragraph.add_run().add_break(WD_BREAK.LINE)


def strip_comments(text):
    """Drop HTML comments, and any line they leave empty, so no marker
    ever reaches the page as text and none splits a paragraph in two."""
    lines = COMMENT_RE.sub("\x00", text).split("\n")
    kept = [ln.replace("\x00", "") for ln in lines
            if not (ln.strip("\x00 ") == "" and "\x00" in ln)]
    return "\n".join(kept).lstrip("\n")


def bullet_items(block):
    """A "- " list's items, or None when the block is not a list. An item
    may wrap: a line that does not start with "- " but is indented
    continues the item before it."""
    if not BULLET_RE.match(block[0]):
        return None
    items = []
    for line in block:
        if BULLET_RE.match(line):
            items.append(BULLET_RE.sub("", line).strip())
        elif line[:1].isspace():
            items[-1] += " " + line.strip()
        else:
            return None
    return items


def add_header_image(section, image_path, height=None):
    """A small copy of an image (a logo) centered in the header of every
    page but the first (practice: create-word-doc, the running header).

    The first page gets a header and footer of its own -- Word's "different
    first page" -- so the header there is left empty, under the cover, and
    the footer is copied onto it: without the copy, page one would lose
    its "Page X of Y". Call this after the footer is written."""
    import copy
    section.different_first_page_header_footer = True
    header = section.header
    header.is_linked_to_previous = False
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0  # a 1.3 line would pad the image
    p.add_run().add_picture(str(image_path), height=height or Inches(0.4))

    section.first_page_header.is_linked_to_previous = False
    first_footer = section.first_page_footer
    first_footer.is_linked_to_previous = False
    target = first_footer._element
    for old in list(target):
        target.remove(old)
    for el in section.footer._element:
        target.append(copy.deepcopy(el))


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


def add_contents(doc):
    """Word's own table of contents, on a page of its own just before the
    first Heading 1 (practice: create-word-doc, the contents page).

    A "Contents" paragraph in the "TOC Heading" style -- it looks like a
    Heading 1 but stays out of the contents and the Navigation Pane, where a
    Heading 1 would list itself. Then a TOC field (TOC \\o "1-2" \\h \\z \\u)
    whose cached result is the finished list: each Heading 1 and Heading 2,
    as a link that jumps to a bookmark on the heading itself.

    The document never asks Word to update its fields when it opens (no
    updateFields setting): that is the "This document contains fields that
    may refer to other files" prompt, and a document sent to someone must
    open without it (Morgan, 2026-10-05). So the list carries no page
    numbers -- only Word knows where its pages break -- and a reader who
    wants them right-clicks the list and picks Update Field. The page break
    after the list is a paragraph of its own: updating the field rewrites
    everything inside it, and a break there would go too."""
    first_part = next((p for p in doc.paragraphs
                       if p.style.name == "Heading 1"), None)
    if first_part is None:
        raise SystemExit("create_word_doc: --contents needs a Heading 1 (a "
                         "`## ` heading) to put the contents page before")
    headings = [p for p in doc.paragraphs
                if p.style.name in ("Heading 1", "Heading 2")]

    # A bookmark around each heading's text, named the way Word names its
    # own (_Toc...), so updating the field later finds the same targets.
    names = []
    for i, h in enumerate(headings, start=1):
        name = f"_Toc{i:08d}"
        start = OxmlElement("w:bookmarkStart")
        start.set(qn("w:id"), str(i))
        start.set(qn("w:name"), name)
        end = OxmlElement("w:bookmarkEnd")
        end.set(qn("w:id"), str(i))
        pPr = h._p.pPr
        if pPr is not None:
            pPr.addnext(start)
        else:
            h._p.insert(0, start)
        h._p.append(end)
        names.append(name)

    first_part.insert_paragraph_before("Contents", style="TOC Heading")

    def field_char(paragraph, kind):
        el = OxmlElement("w:fldChar")
        el.set(qn("w:fldCharType"), kind)
        paragraph.add_run()._r.append(el)

    # The field opens in the first entry's paragraph and closes in the last,
    # so its cached result is the list of headings itself.
    paras = []
    for h, name in zip(headings, names):
        p = first_part.insert_paragraph_before()
        p.paragraph_format.left_indent = Inches(
            0.3 if h.style.name == "Heading 2" else 0)
        paras.append((p, h.text, name))
    first = paras[0][0]
    field_char(first, "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = ' TOC \\o "1-2" \\h \\z \\u '
    first.add_run()._r.append(instr)
    field_char(first, "separate")
    for p, text, name in paras:
        link = OxmlElement("w:hyperlink")
        link.set(qn("w:anchor"), name)
        link.set(qn("w:history"), "1")
        run = OxmlElement("w:r")
        t = OxmlElement("w:t")
        t.set(qn("xml:space"), "preserve")
        t.text = text
        run.append(t)
        link.append(run)
        p._p.append(link)
    field_char(paras[-1][0], "end")
    first_part.insert_paragraph_before().add_run().add_break(WD_BREAK.PAGE)


def build_doc(manuscript_path, short_name, add_footer, date_str, contents=False,
              section_breaks=True, header_image=None, soft_wraps=False):
    text = strip_comments(manuscript_path.read_text(encoding="utf-8"))
    STRAY_ASTERISKS.clear()
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
    quote_style = style_block_quote(doc)  # practice: create-word-doc

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
            # A heading straight after the title shares its page: a break
            # there would leave the title alone on page one (Morgan,
            # 2026-10-05, on a blurbs file whose cover held nothing else).
            last_was_heading = True
            continue

        if re.match(r"^## ", first) and len(block) == 1:
            # practice: create-word-doc (chapter page breaks) -- the break
            # is an explicit page-break RUN appended to the END of the
            # paragraph that comes BEFORE this heading, never a property
            # set on the heading paragraph itself. That way the break lives
            # in a different, earlier paragraph and can't land after the
            # heading's own text -- the heading paragraph carries no
            # page-break marking of its own at all.
            if section_breaks and last_para is not None and not last_was_heading:
                last_para.add_run().add_break(WD_BREAK.PAGE)
            last_para = doc.add_heading(first[3:].strip(), level=1)
            last_was_heading = True
            continue

        if re.match(r"^### ", first) and len(block) == 1:
            if section_breaks and last_para is not None and not last_was_heading:
                last_para.add_run().add_break(WD_BREAK.PAGE)
            last_para = doc.add_heading(first[4:].strip(), level=2)
            last_was_heading = True
            continue

        if all(QUOTE_LINE_RE.match(l) for l in block):
            # practice: create-word-doc (block quotations)
            paras = quote_paragraphs(block)
            for lines_ in paras:
                p = doc.add_paragraph(style=quote_style)
                add_inline(p, lines_, soft_wraps)
                last_para = p
            if paras:
                last_was_heading = False
            continue

        items = bullet_items(block)
        if items is not None:
            for item in items:
                p = doc.add_paragraph(style="List Bullet")
                add_inline(p, [item], soft_wraps)
            last_para = p
            last_was_heading = False
            continue

        p = doc.add_paragraph()
        # Text lines go in together, so emphasis can span them; a word-count
        # line splits the paragraph's text where it sits.
        pending = []
        for idx, l in enumerate(block):
            if WORDS_LINE_RE.match(l.strip()):
                if pending:
                    add_inline(p, pending, soft_wraps)
                    line_end(p, pending[-1], soft_wraps)
                    pending = []
                p.add_run("Words: ")
                add_field(p, "NUMWORDS", cached_text=word_count_cache)
                if idx < len(block) - 1:
                    line_end(p, l, soft_wraps)
            else:
                pending.append(l)
        if pending:
            add_inline(p, pending, soft_wraps)
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

    if header_image is not None:
        add_header_image(section, header_image)

    if contents:
        add_contents(doc)

    # practice: create-word-doc -- an asterisk placed like emphasis that
    # nothing closed is almost always a typo in the source; say where, never
    # pass it silently. An escaped \\* or a spaced "5 * 3" is not reported.
    for where in STRAY_ASTERISKS:
        print(f"create_word_doc WARNING: a stray asterisk reached the text: "
              f"...{where}...", file=sys.stderr)

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
    ap.add_argument(
        "--contents",
        action="store_true",
        help="add Word's own table of contents (Parts and chapters) on a page "
             "of its own before the first Part",
    )
    ap.add_argument(
        "--no-section-breaks",
        action="store_true",
        help="let sections flow on instead of starting each ## and ### on a new page",
    )
    ap.add_argument(
        "--soft-wraps",
        action="store_true",
        help="join a paragraph's source lines with a space, as Markdown does, "
             "for a source wrapped at a fixed width (a backslash or two "
             "trailing spaces still break the line)",
    )
    ap.add_argument(
        "--header-image",
        type=pathlib.Path,
        default=None,
        help="an image (a logo) to put, small and centered, in the header of "
             "every page but the first",
    )
    args = ap.parse_args()

    if not args.manuscript.is_file():
        sys.exit(f"error: {args.manuscript} does not exist")

    short_name = args.short_name or derive_short_name(args.manuscript)
    # practice: timestamps-carry-offset -- one shared module resolves the zone
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    date_str = args.date or precedent_time.today(repo_root)

    if args.header_image is not None and not args.header_image.is_file():
        sys.exit(f"error: {args.header_image} does not exist")
    doc = build_doc(args.manuscript, short_name, not args.no_footer, date_str,
                    contents=args.contents,
                    section_breaks=not args.no_section_breaks,
                    soft_wraps=args.soft_wraps,
                    header_image=args.header_image)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(args.out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
