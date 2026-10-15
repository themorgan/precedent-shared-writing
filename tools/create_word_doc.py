#!/usr/bin/env python3
"""create_word_doc.py -- convert a book-*/MANUSCRIPT.md into a .docx,
with a confidential-draft footer stamped on every page.

# practice: create-word-doc

Parses the manuscript's plain Markdown (headings up to ####, **bold**,
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
repaginates the content. The footer is set in a sans-serif face (Arial),
a touch smaller than the body (10 point against 12), so it reads as page
furniture against the serif text. style_footer() does the same for a
document built by hand.

Heading 1 is 20 point, between the title's 26 and Heading 2's 13: Word's
stock 14 point barely stood out from Heading 2. style_heading_1() does
the same for a document built by hand.

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

`--header-image PATH` puts a small copy of an image (a logo), 0.6 inch
tall, centered in the header of every page but the first, which already carries the
cover. add_header_image() does the same for a document built by hand.

A "> " block -- a long excerpt quoted from another text -- becomes a
block quotation, the way a printed book sets one off: indented half an
inch on both sides, a point smaller, tighter line spacing, no quotation
marks, and the ">" characters gone. A bare ">" line inside the block
starts a new paragraph of the same quotation. It uses Word's own "Quote"
style, restyled upright (the stock one is italic, which tires the eye
over a long passage), so the excerpts are findable and restylable in
Word's Styles pane all at once.

A "- " bullet list and a "1. " numbered list sit a quarter inch in from
the margin: the bullet or number at a quarter inch, each item's text a
quarter inch further, and an item's wrapped lines lined up under its own
text. A numbered list is a real Word list (List Number), restarting at its
own first number. Word's stock lists put the bullet flush against the
margin, which looks like a mistake beside indented block quotations.
style_list_bullet() and style_list_number() do the same for a document
built by hand.

Straight quotes become curly ones, single and double, "--" and "---"
always become an em dash, and a hyphen between two numbers that make a
range (1990-2000, pages 10-20) becomes an en dash, everywhere in the text
and the headings -- but never inside a web link's address, and never a
backslash-escaped character, and never in code: a fenced block is set
line for line in Courier New, and a code span keeps its characters in the
same face, without its backticks. The rules are typography.py's, shared with
every other builder for an outside reader; smarten() does the same for a
document built by hand.

Default page is A4 with 0.75-inch margins on all four sides, default
line spacing is 1.3x. A "Words: <count>"
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
  python3 tools/create_word_doc.py --rebuild old/Notes.docx --out /path/to/Notes.docx

The short book name is needed only by the default footer line, so a
document outside book-*/ that passes --footer-label or --no-footer needs
no --short-name either.

Every document records how it was built: the manuscript, the options and
an explicit --date, as JSON in the .docx's own Comments property (File >
Properties in Word), under the marker "create_word_doc.py build:". Paths
are kept relative to the repository the manuscript sits in.
--rebuild FILE.docx reads that record and builds again with the same
options from the current source -- dated today unless the record carries
a --date -- so a rebuild never has to guess the flags from the old file.
Any option given beside --rebuild wins over the recorded one.

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
import json
import os
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
    # The engine's one install call, beside this script in every repository
    # that has the engine (tools/precedent_python.py, 2026-10-15): it
    # retries pip's PEP 668 refusal, which a cloud container's system Python
    # gives -- this script's test failed on a fresh container for exactly
    # that. The same retry, here, for an engine that predates it.
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        from precedent_python import pip_install
        r = pip_install(sys.executable, [DOCX_PACKAGE])
    except ImportError:
        cmd = [sys.executable, "-m", "pip", "install", "--quiet", DOCX_PACKAGE]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode and "externally-managed" in (r.stderr + r.stdout):
            r = subprocess.run(cmd + ["--break-system-packages"],
                               capture_output=True, text=True)
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
from docx.opc.constants import RELATIONSHIP_TYPE as RT  # noqa: E402
from docx.shared import Emu, Inches, Mm, Pt  # noqa: E402

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
# practice: create-word-doc -- a link to the web, unlike a repository path,
# means the same thing in a Word file, so it stays a link there: a proposal
# that pointed its reader at "the original proposal" lost the address
# (Morgan, 2026-10-13). Marked here, made a real hyperlink in add_inline().
WEB_LINK_RE = re.compile(r"(?<!\\)\[([^\]]+)\]\(((?:https?|mailto):[^)\s]*)\)")
LINK_OPEN, LINK_MID, LINK_CLOSE = "\x01", "\x02", "\x03"
LINK_MARK_RE = re.compile("\x01([^\x02]*)\x02|\x03")
# practice: create-word-doc -- Markdown's backslash escape: "\\$15k" and
# "\\[A\\]" are "$15k" and "[A]" on the page, never with the backslash
# (Morgan, 2026-10-13, a proposal's prices).
ESCAPE_RE = re.compile(r"\\([!-/:-@\[-`{-~])")
# An HTML comment (a file header, a generated-block marker) is never text.
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
BULLET_RE = re.compile(r"^\s*-\s+")
NUMBER_RE = re.compile(r"^\s*(\d+)[.)]\s+")
# practice: create-word-doc -- a manuscript's own word-count line becomes a
# live NUMWORDS field instead of a number that goes stale as soon as the
# text changes; any trailing "(PART 1)"-style note is dropped with it.
WORDS_LINE_RE = re.compile(r"^Words:\s*[\d,]+\s*(\(.*\))?\s*$", re.IGNORECASE)
# practice: create-word-doc -- a "> " line is a block quotation, never text
# that starts with a ">" character.
QUOTE_LINE_RE = re.compile(r"^\s*>\s?")
# practice: curly-quotes -- code is never typography. A fenced block (``` or
# ~~~) is set line for line in a fixed-width face and never smartened; a
# code span keeps its characters and drops its backticks, in the same face.
# In code, "--" and "-" mean something exactly (Morgan, 2026-10-13: "double
# dashes and dashes have particular meanings in code").
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
CODE_SPAN_RE = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)")
CODE_OPEN, CODE_CLOSE = "\x04", "\x05"
CODE_MARK_RE = re.compile("\x04(\\d+)\x05")
CODE_FONT, CODE_SIZE = "Courier New", 10
CODE_SPANS = []


# practice: create-word-doc -- the footer's face and size. A sans-serif
# footer a touch smaller than the body reads as page furniture, set apart
# from the serif text (Morgan, 2026-10-05).
FOOTER_FONT = "Arial"
FOOTER_SIZE = 10
# practice: create-word-doc -- Heading 1 sits clearly between the title
# (26 point) and Heading 2 (13): Word's stock 14 point barely stood out
# from Heading 2 (Morgan, 2026-10-05).
HEADING_1_SIZE = 20
# practice: create-word-doc -- the page margin on all four sides, in inches.
# It was one inch until Morgan asked for 0.75 (2026-10-05). A builder that
# lays out its own page reads this rather than its own number.
PAGE_MARGIN = 0.75
# practice: create-word-doc -- the running header's logo, in inches tall.
# It was 0.4 until Morgan asked for it about half as big again (2026-10-05).
HEADER_IMAGE_HEIGHT = 0.6


def set_style_font(style, name):
    """Set a style's typeface in every slot Word reads (Latin, East Asian,
    complex script) and drop any theme font, which would otherwise win over
    the name in some viewers."""
    style.font.name = name
    rfonts = style.element.get_or_add_rPr().get_or_add_rFonts()
    for slot in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(slot), name)
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rfonts.get(qn(attr)) is not None:
            del rfonts.attrib[qn(attr)]


def style_footer(doc, size=None):
    """Set Word's built-in "Footer" style in FOOTER_FONT, a touch smaller
    than the body (FOOTER_SIZE, or `size` points for a document whose body
    is smaller than 12). Every footer paragraph must carry the style --
    python-docx gives one to the footer's first paragraph only, so add the
    others with style="Footer". Returns the style."""
    style = doc.styles["Footer"]
    set_style_font(style, FOOTER_FONT)
    style.font.size = Pt(size or FOOTER_SIZE)
    return style


def style_heading_1(doc, size=None):
    """Make Heading 1 HEADING_1_SIZE points (or `size`), clearly bigger than
    Heading 2 and still smaller than the title. Returns the style."""
    style = doc.styles["Heading 1"]
    style.font.size = Pt(size or HEADING_1_SIZE)
    return style


def style_contents(doc, section=None):
    """Word's own contents styles, "TOC 1" for a Part and "TOC 2" for a
    chapter, set so the list reads as a contents page at a glance
    (practice: create-word-doc, the contents page): a Part bold with a
    little space above it, its chapters indented under it, everything
    single-spaced -- body text's 1.3 line spacing turned a contents list
    into an unbroken column nobody recognized (Morgan, 2026-10-05). Both
    carry a dotted right-aligned tab at the text's right edge, so when a
    reader picks Update Field in Word, the page numbers it adds sit at the
    end of a dot leader, the way a printed book's do. Every entry is set in
    the footer's sans-serif face (FOOTER_FONT) and underlined, so it reads
    as a link -- which it is -- rather than as more text (Morgan,
    2026-10-05). Word rewrites the list with these same styles on that
    update, so it keeps the look. Returns (toc1, toc2)."""
    from docx.enum.style import WD_STYLE_TYPE
    from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
    section = section or doc.sections[0]
    width = section.page_width - section.left_margin - section.right_margin
    out = []
    for level in (1, 2):
        # Word knows its contents styles by the id "TOC1" and the internal
        # name "toc 1", and only a built-in style -- not a custom one of the
        # same look -- is what Update Field rewrites the list with.
        style = next((st for st in doc.styles
                      if st.style_id == f"TOC{level}"), None)
        if style is None:
            style = doc.styles.add_style(f"TOC {level}", WD_STYLE_TYPE.PARAGRAPH)
            style.base_style = doc.styles["Normal"]
            style.element.style_id = f"TOC{level}"
            style.element.name_val = f"toc {level}"
            style.element.attrib.pop(qn("w:customStyle"), None)
        style.next_paragraph_style = style
        pf = style.paragraph_format
        pf.line_spacing = 1.0
        pf.left_indent = Inches(0 if level == 1 else 0.3)
        pf.space_before = Pt(8 if level == 1 else 0)
        pf.space_after = Pt(2)
        style.font.bold = level == 1
        set_style_font(style, FOOTER_FONT)
        style.font.underline = True
        pf.tab_stops.add_tab_stop(width, WD_TAB_ALIGNMENT.RIGHT,
                                  WD_TAB_LEADER.DOTS)
        out.append(style)
    # A Part's first chapter line stays on the Part's page.
    out[0].paragraph_format.keep_with_next = True
    return tuple(out)


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


# practice: create-word-doc -- where a list's bullet (or number) sits, and how
# far past it the item's text starts. A builder that sets list indents by
# hand reads these rather than its own numbers, so every list matches.
# A quarter inch, not the half inch it was: Morgan found half an inch "far
# too much" (2026-10-13).
LIST_INDENT = 0.25
LIST_HANG = 0.25


def style_list_bullet(doc):
    """Move Word's built-in "List Bullet" LIST_INDENT in from the margin.
    Returns the style."""
    return style_list(doc, "List Bullet")


def style_list_number(doc):
    """Move Word's built-in "List Number" LIST_INDENT in from the margin,
    the same place as a bullet list. Returns the style."""
    return style_list(doc, "List Number")


def style_list(doc, name):
    """Move one of Word's built-in list styles LIST_INDENT in from the margin:
    the bullet at LIST_INDENT, the text (and every wrapped line under it) at
    LIST_INDENT + LIST_HANG. The stock style puts the bullet flush with the
    margin. The indent is set in both places Word reads it from -- the
    style's own paragraph settings and the bullet's numbering level, plus
    the tab stop after the bullet -- so no viewer is left with the old
    position from whichever one it happens to prefer. Returns the style."""
    style = doc.styles[name]
    pf = style.paragraph_format
    # practice: create-word-doc -- a list takes no space of its own before
    # it, so the gap between a lead-in line and its first item is exactly
    # what lead_into_list leaves there (Morgan, 2026-10-13).
    pf.space_before = Pt(0)
    pf.left_indent = Inches(LIST_INDENT + LIST_HANG)
    pf.first_line_indent = Inches(-LIST_HANG)
    num_pr = style.element.pPr.numPr if style.element.pPr is not None else None
    if num_pr is None or num_pr.numId is None:
        return style
    numbering = doc.part.numbering_part.element
    abstract_id = numbering.num_having_numId(num_pr.numId.val).abstractNumId.val
    twips = lambda inches: str(round(inches * 1440))  # noqa: E731
    for lvl in numbering.xpath(
            f'./w:abstractNum[@w:abstractNumId="{abstract_id}"]/w:lvl[@w:ilvl="0"]'):
        ppr = lvl.find(qn("w:pPr"))
        if ppr is None:
            ppr = OxmlElement("w:pPr")
            lvl.append(ppr)
        for tab in ppr.iter(qn("w:tab")):
            if tab.get(qn("w:val")) == "num":
                tab.set(qn("w:pos"), twips(LIST_INDENT + LIST_HANG))
        ind = ppr.find(qn("w:ind"))
        if ind is None:
            ind = OxmlElement("w:ind")
            ppr.append(ind)
        ind.set(qn("w:left"), twips(LIST_INDENT + LIST_HANG))
        ind.set(qn("w:hanging"), twips(LIST_HANG))
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


# practice: create-word-doc -- typography. Straight quotes become curly,
# "--"/"---" an em dash and a number range's hyphen an en dash, in every Word
# document (Morgan, 2026-10-13: "they ALWAYS should"). The rules live in
# typography.py, the one copy every builder for an outside reader shares
# (practice: curly-quotes).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from typography import LINK_MID as _TYPO_MID, LINK_OPEN as _TYPO_OPEN, smarten  # noqa: E402
assert (_TYPO_OPEN, _TYPO_MID) == (LINK_OPEN, LINK_MID), \
    "typography.py and create_word_doc.py must mark a link address alike"


def heading_text(raw):
    """A heading's text as it reads in Word: curly quotes, dashes, and
    escapes taken as their character."""
    return ESCAPE_RE.sub(r"\1", smarten(raw.strip()))


def parse_inline(text):
    """Split text into (text, bold, italic) runs on **bold**, *italic* and
    ***both***, nested either way round -- "**a *b* c**" gives a bold run
    with an italic-and-bold middle. A link becomes its text, a trailing
    backslash -- Markdown's hard line break, which the caller already makes
    a real one -- is dropped, and an escaped \\* or a spaced "5 * 3" is a
    plain asterisk. When marks cross ("**a *b** c*") the outer one wins.
    An asterisk placed like emphasis that nothing pairs never reaches the
    text: it is left out and noted in STRAY_ASTERISKS for a warning.
    The text may hold "\\n" (a line break inside the paragraph); emphasis
    carries across it, so an italic title wrapped over two source lines
    still comes out italic."""
    def hold(m):
        CODE_SPANS.append(m.group(2))
        return CODE_OPEN + str(len(CODE_SPANS) - 1) + CODE_CLOSE
    text = CODE_SPAN_RE.sub(hold, text)
    text = WEB_LINK_RE.sub(
        lambda m: LINK_OPEN + m.group(2) + LINK_MID + m.group(1) + LINK_CLOSE, text)
    text = LINK_RE.sub(r"\1", text)
    text = smarten(text)
    if text.endswith("\\"):
        text = text[:-1].rstrip()

    # Pieces: plain text (str) or a delimiter run (dict).
    pieces = []
    last = 0
    for m in STAR_RUN_RE.finditer(text):
        if m.start() > last:
            pieces.append(ESCAPE_RE.sub(r"\1", text[last:m.start()]))
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
        pieces.append(ESCAPE_RE.sub(r"\1", text[last:]))

    # Match closers to the nearest opener still holding asterisks, two at a
    # time (bold) when both sides have two, else one (italic). When marks
    # cross -- "**a *b** c*" -- the outer one wins (Morgan, 2026-10-05: "it
    # should always take the form of the OUTER one"): a closer that cannot
    # pair with the nearest opener's kind, but can with one further out,
    # closes that outer one, and the inner openers it skips are dropped.
    def fits(opener_left, closer_left):
        return opener_left >= 2 if closer_left >= 2 else opener_left in (1, 3)

    stack = []
    for piece in pieces:
        if isinstance(piece, str):
            continue
        piece["left"] = piece["n"]
        if piece["can_close"]:
            while piece["left"] and stack:
                if not fits(stack[-1]["left"], piece["left"]):
                    outer = next((i for i in range(len(stack) - 2, -1, -1)
                                  if fits(stack[i]["left"], piece["left"])), None)
                    if outer is not None:
                        del stack[outer + 1:]
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
        # An asterisk placed like emphasis that nothing paired -- a crossed
        # inner mark the outer one won over, or a typo -- never reaches the
        # page; it is reported instead, so the source gets fixed.
        if piece["left"] and (piece["can_open"] or piece["can_close"]):
            STRAY_ASTERISKS.append(plain[max(0, at - 40):at + 40])
        elif piece["left"]:
            emit("*" * piece["left"])  # spaced on both sides: "5 * 3"
        at += piece["n"]
        for kind in piece["closes"]:
            depth[kind] -= 1
        for kind in piece["opens"]:
            depth[kind] += 1
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
    link = None  # the w:hyperlink element runs go into, inside a web link
    for run_text, bold, italic in parse_inline("".join(joined)):
        for n, chunk in enumerate(run_text.split("\n")):
            if n:
                paragraph.add_run().add_break(WD_BREAK.LINE)
            at = 0
            for m in list(LINK_MARK_RE.finditer(chunk)) + [None]:
                piece = chunk[at:m.start() if m else len(chunk)]
                for k, bit in enumerate(CODE_MARK_RE.split(piece)):
                    if not bit:
                        continue
                    if k % 2:
                        r = paragraph.add_run(CODE_SPANS[int(bit)])
                        r.font.name = CODE_FONT
                        r.font.size = Pt(CODE_SIZE)
                        r.bold = bold
                        r.italic = italic
                        if link is not None:
                            link.append(r._r)
                    elif link is None:
                        r = paragraph.add_run(bit)
                        r.bold = bold
                        r.italic = italic
                    else:
                        link.append(hyperlink_run(bit, bold, italic))
                if m is None:
                    break
                at = m.end()
                if m.group(0) == LINK_CLOSE:
                    link = None
                else:
                    link = OxmlElement("w:hyperlink")
                    link.set(qn("r:id"), paragraph.part.relate_to(
                        m.group(1), RT.HYPERLINK, is_external=True))
                    paragraph._p.append(link)


def hyperlink_run(text, bold, italic):
    """One run of a web link's text, set the way Word sets a link: blue and
    underlined, so it reads as one (practice: create-word-doc)."""
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    if bold:
        rpr.append(OxmlElement("w:b"))
    if italic:
        rpr.append(OxmlElement("w:i"))
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    rpr.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    rpr.append(underline)
    run.append(rpr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    run.append(t)
    return run


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


def lead_into_list(doc, paragraph):
    """A body paragraph straight before a list keeps half the normal
    end-of-paragraph space after it, the same gap a list's end leaves
    (end_list), so a list is set off the same above and below. It was
    flush with the list until Morgan found it too tight (2026-10-14). A
    heading keeps its own spacing."""
    if paragraph is not None and paragraph.style.name == "Normal":
        paragraph.paragraph_format.space_after = Emu(paragraph_space_after(doc) // 2)
        # Never stranded at the foot of a page: the lead-in moves with its
        # list's first item (Morgan, 2026-10-13).
        paragraph.paragraph_format.keep_with_next = True


def end_list(doc, paragraph):
    """A list's last item keeps half the normal end-of-paragraph space
    after it: the next paragraph starts a new thought, so it needs a break,
    but a full one looked like a hole (Morgan, 2026-10-13). The lead-in
    above the list gets the same half gap (lead_into_list)."""
    paragraph.paragraph_format.space_after = Emu(paragraph_space_after(doc) // 2)


def paragraph_space_after(doc):
    """The body's end-of-paragraph space, in EMU: Normal's own, else the
    document default, else Word's stock 10 points."""
    own = doc.styles["Normal"].paragraph_format.space_after
    if own is not None:
        return own
    found = doc.styles.element.xpath("./w:docDefaults/w:pPrDefault/w:pPr/w:spacing/@w:after")
    return Pt(int(found[0]) / 20) if found else Pt(10)


def numbered_items(block):
    """A "1. " list's (start, items), or None when the block is not one.
    Wrapping works as in bullet_items()."""
    m = NUMBER_RE.match(block[0])
    if not m:
        return None
    items = []
    for line in block:
        if NUMBER_RE.match(line):
            items.append(NUMBER_RE.sub("", line).strip())
        elif line[:1].isspace():
            items[-1] += " " + line.strip()
        else:
            return None
    return int(m.group(1)), items


def restart_numbering(doc, paragraph, start):
    """Give a numbered list its own count, starting at `start`, so a second
    list in the document starts again rather than carrying on from the
    first. Called on the list's first paragraph; the caller puts the rest on
    the same numId."""
    style = doc.styles["List Number"]
    num_id = style.element.pPr.numPr.numId.val
    numbering = doc.part.numbering_part.element
    abstract_id = numbering.num_having_numId(num_id).abstractNumId.val
    num = numbering.add_num(abstract_id)
    override = num.add_lvlOverride(ilvl=0)
    override.add_startOverride(start)
    return num.numId


def set_num_id(paragraph, num_id):
    num_pr = paragraph._p.get_or_add_pPr().get_or_add_numPr()
    num_pr.get_or_add_ilvl().val = 0
    num_pr.get_or_add_numId().val = num_id


def add_header_image(section, image_path, height=None, first_page=False):
    """A small copy of an image (a logo), HEADER_IMAGE_HEIGHT inches tall
    unless `height` says otherwise, centered in the header of every page
    but the first (practice: create-word-doc, the running header).

    The first page gets a header and footer of its own -- Word's "different
    first page" -- so the header there is left empty, under the cover, and
    the footer is copied onto it: without the copy, page one would lose
    its "Page X of Y". Call this after the footer is written.

    With first_page, page one carries the logo too, for a document whose
    first page is no cover -- a letter, a proposal -- where the logo at the
    top of page one is the letterhead (Morgan, 2026-10-13)."""
    import copy
    section.different_first_page_header_footer = not first_page
    header = section.header
    header.is_linked_to_previous = False
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0  # a 1.3 line would pad the image
    p.add_run().add_picture(str(image_path), height=height or Inches(HEADER_IMAGE_HEIGHT))
    if first_page:
        return

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
    fence = None   # the fence a code block opened with, while inside one

    def flush():
        if current:
            blocks.append(list(current))
            current.clear()

    for line in lines:
        # practice: curly-quotes -- a fenced code block is one block, blank
        # lines and all, from its opening fence to the matching close.
        m = FENCE_RE.match(line)
        if fence is not None:
            current.append(line)
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and not line.strip()[len(m.group(1)):].strip():
                fence = None
                flush()
            continue
        if m:
            flush()
            fence = m.group(1)
            current.append(line)
            continue
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
    as a link that jumps to a bookmark on the heading itself, in Word's own
    "TOC 1" and "TOC 2" styles as style_contents() sets them.

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
    toc1, toc2 = style_contents(doc)
    paras = []
    for h, name in zip(headings, names):
        p = first_part.insert_paragraph_before(
            style=toc2 if h.style.name == "Heading 2" else toc1)
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
              section_breaks=True, header_image=None, soft_wraps=False,
              header_on_first_page=False, footer_label=None):
    text = strip_comments(manuscript_path.read_text(encoding="utf-8"))
    STRAY_ASTERISKS.clear()
    CODE_SPANS.clear()
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
        setattr(section, side, Inches(PAGE_MARGIN))

    word_count_cache = str(len(text.split()))
    quote_style = style_block_quote(doc)  # practice: create-word-doc
    style_footer(doc)  # practice: create-word-doc
    style_heading_1(doc)  # practice: create-word-doc
    style_list_bullet(doc)  # practice: create-word-doc
    style_list_number(doc)

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

        if FENCE_RE.match(first):
            # practice: curly-quotes -- set as typed, never smartened.
            body = block[1:]
            if body and FENCE_RE.match(body[-1]):
                body = body[:-1]
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            for n, code_line in enumerate(body):
                r = p.add_run()
                r.font.name = CODE_FONT
                r.font.size = Pt(CODE_SIZE)
                if n:
                    r.add_break(WD_BREAK.LINE)
                r.add_text(code_line)
            last_para = p
            last_was_heading = False
            continue

        if not saw_title and re.match(r"^# ", first) and len(block) == 1:
            last_para = doc.add_heading(heading_text(first[2:]), level=0)
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
            last_para = doc.add_heading(heading_text(first[3:]), level=1)
            last_was_heading = True
            continue

        if re.match(r"^### ", first) and len(block) == 1:
            if section_breaks and last_para is not None and not last_was_heading:
                last_para.add_run().add_break(WD_BREAK.PAGE)
            last_para = doc.add_heading(heading_text(first[4:]), level=2)
            last_was_heading = True
            continue

        # practice: create-word-doc -- a "#### " sub-section heading is a
        # real Heading 3, never text with "####" in front of it (Morgan,
        # 2026-10-13, a proposal's People and Processes). It flows on: a
        # page break is for a Part or a chapter, not a sub-section.
        if re.match(r"^#### ", first) and len(block) == 1:
            last_para = doc.add_heading(heading_text(first[5:]), level=3)
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

        numbered = numbered_items(block)
        if numbered is not None:
            lead_into_list(doc, last_para)
            # practice: create-word-doc -- a "1. " list is a real Word list,
            # never numbers typed as text (Morgan, 2026-10-13).
            start, items = numbered
            num_id = None
            for item in items:
                p = doc.add_paragraph(style="List Number")
                if num_id is None:
                    num_id = restart_numbering(doc, p, start)
                set_num_id(p, num_id)
                add_inline(p, [item], soft_wraps)
            end_list(doc, p)
            last_para = p
            last_was_heading = False
            continue

        items = bullet_items(block)
        if items is not None:
            lead_into_list(doc, last_para)
            for item in items:
                p = doc.add_paragraph(style="List Bullet")
                add_inline(p, [item], soft_wraps)
            end_list(doc, p)
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
        page_para.style = doc.styles["Footer"]
        page_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        page_para.add_run("Page ")
        add_field(page_para, "PAGE")
        page_para.add_run(" of ")
        add_field(page_para, "NUMPAGES")

        conf_para = footer.add_paragraph(style="Footer")
        conf_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # practice: create-word-doc -- "DRAFT BOOK" is a manuscript's own
        # wording; any other document names itself (Morgan, 2026-10-13).
        label = footer_label or f"CONFIDENTIAL - DRAFT BOOK: {short_name.upper()}"
        conf_para.add_run(f"{label} - {date_str}")

    if header_image is not None:
        add_header_image(section, header_image, first_page=header_on_first_page)

    if contents:
        add_contents(doc)

    # practice: create-word-doc -- an asterisk placed like emphasis that
    # nothing closed is almost always a typo in the source; say where, never
    # pass it silently. An escaped \\* or a spaced "5 * 3" is not reported.
    for where in STRAY_ASTERISKS:
        print(f"create_word_doc WARNING: a stray asterisk was left out of the "
              f"text -- fix the source: "
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


# practice: create-word-doc -- a document carries its own build settings, so
# rebuilding it never means reverse-engineering the flags from the old file
# (a consuming repository, 2026-10-15: a proposal's rebuild had to read its
# footer text, its header image's hash and its first-page header to learn
# how it had been built; a wrong guess ships a differently formatted
# document to an outside reader).
BUILD_MARK = "create_word_doc.py build: "
# Recorded options: argparse destination -> how it is stored.
RECORDED_PATHS = ("manuscript", "header_image")
RECORDED_VALUES = ("short_name", "date", "footer_label")
RECORDED_FLAGS = ("no_footer", "contents", "no_section_breaks", "soft_wraps",
                  "header_on_first_page")


def repo_root(start):
    """The nearest directory at or above start holding .git, or None."""
    start = pathlib.Path(start).resolve()
    for d in (start, *start.parents):
        if (d / ".git").exists():
            return d
    return None


def build_record(args):
    """The JSON a document carries: paths relative to the manuscript's
    repository (absolute when it sits in none), and only what was set."""
    root = repo_root(args.manuscript.resolve().parent)
    rec = {}
    for key in RECORDED_PATHS:
        path = getattr(args, key)
        if path is None:
            continue
        path = path.resolve()
        if root is not None:
            try:
                path = path.relative_to(root)
            except ValueError:
                pass
        rec[key] = path.as_posix()
    for key in RECORDED_VALUES:
        if getattr(args, key) is not None:
            rec[key] = getattr(args, key)
    for key in RECORDED_FLAGS:
        if getattr(args, key):
            rec[key] = True
    return rec


def read_record(docx_path):
    """The recorded options of a document this script built, with paths
    resolved against the repository the document sits in (else the
    current directory's)."""
    comments = Document(str(docx_path)).core_properties.comments or ""
    if not comments.startswith(BUILD_MARK):
        raise SystemExit(
            f"error: {docx_path} carries no build record (built before "
            "create_word_doc.py recorded one, or by something else) -- "
            "build it once with its flags given in full")
    rec = json.loads(comments[len(BUILD_MARK):])
    root = (repo_root(pathlib.Path(docx_path).resolve().parent)
            or repo_root(pathlib.Path.cwd()) or pathlib.Path.cwd())
    for key in RECORDED_PATHS:
        if key in rec:
            path = pathlib.Path(rec[key])
            if not path.is_absolute():
                path = pathlib.Path(os.path.relpath(root / path))
            rec[key] = path
    return rec


def command_line(rec, out):
    """The command a record amounts to, printed on a rebuild."""
    parts = ["python3", "tools/create_word_doc.py", str(rec["manuscript"]),
             "--out", str(out)]
    for key in ("header_image", *RECORDED_VALUES):
        if rec.get(key) is not None:
            parts += ["--" + key.replace("_", "-"), str(rec[key])]
    for key in RECORDED_FLAGS:
        if rec.get(key):
            parts.append("--" + key.replace("_", "-"))
    return " ".join(json.dumps(p) if (" " in p or not p) else p for p in parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("manuscript", type=pathlib.Path, nargs="?",
                    help="path to a book-*/MANUSCRIPT.md (or any Markdown "
                         "file); omitted with --rebuild")
    ap.add_argument("--out", type=pathlib.Path, required=True, help="output .docx path")
    ap.add_argument(
        "--rebuild",
        type=pathlib.Path,
        default=None,
        metavar="FILE.docx",
        help="build again with the options recorded in FILE.docx, a document "
             "this script built; options given here win over the recorded ones",
    )
    ap.add_argument(
        "--short-name",
        default=None,
        help="short book name for the footer (default: derived from the book-*/ "
             "directory name; unused with --footer-label or --no-footer)",
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
    ap.add_argument(
        "--header-on-first-page",
        action="store_true",
        help="put the header image on page one as well, for a document whose "
             "first page is no cover (a letter, a proposal)",
    )
    ap.add_argument(
        "--footer-label",
        default=None,
        help='the footer\'s second line, before " - <date>" (default: '
             '"CONFIDENTIAL - DRAFT BOOK: <SHORT NAME>")',
    )
    args = ap.parse_args()
    if args.rebuild is not None:
        if not args.rebuild.is_file():
            sys.exit(f"error: {args.rebuild} does not exist")
        # The record becomes the defaults, so anything given here wins.
        ap.set_defaults(**read_record(args.rebuild))
        args = ap.parse_args()
        print(f"rebuilding as: {command_line(vars(args), args.out)}")
    if args.manuscript is None:
        ap.error("the manuscript is required (or --rebuild FILE.docx)")

    if not args.manuscript.is_file():
        sys.exit(f"error: {args.manuscript} does not exist")

    # practice: create-word-doc -- the short name appears only in the default
    # footer line, so it is derived (and its absence an error) only when that
    # line is built (a consuming repository, 2026-10-15: a proposal outside
    # book-*/ with --footer-label was refused for want of --short-name).
    short_name = args.short_name
    if not short_name and not args.no_footer and not args.footer_label:
        short_name = derive_short_name(args.manuscript)
    # practice: timestamps-carry-offset -- one shared module resolves the zone
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    date_str = args.date or precedent_time.today(repo_root)

    if args.header_image is not None and not args.header_image.is_file():
        sys.exit(f"error: {args.header_image} does not exist")
    doc = build_doc(args.manuscript, short_name, not args.no_footer, date_str,
                    contents=args.contents,
                    section_breaks=not args.no_section_breaks,
                    soft_wraps=args.soft_wraps,
                    header_image=args.header_image,
                    header_on_first_page=args.header_on_first_page,
                    footer_label=args.footer_label)
    # Set on the element itself: python-docx refuses any core property over
    # 255 characters, a cap of its own -- the file format has none -- and a
    # record with two repository paths and a footer label passes it.
    doc.core_properties._element._get_or_add("description").text = (
        BUILD_MARK + json.dumps(build_record(args), ensure_ascii=False,
                                sort_keys=True))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(args.out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
