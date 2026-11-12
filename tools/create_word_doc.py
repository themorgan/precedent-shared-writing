#!/usr/bin/env python3
"""create_word_doc.py -- convert a book-*/MANUSCRIPT.md into a .docx,
with a confidential-draft footer stamped on every page.

# practice: create-word-doc

Parses the manuscript's plain Markdown (headings up to ######, **bold**,
*italic* and ***both***, nested either way and carried across a wrapped
line, as Markdown reads them, [links](...) printed as their text, "- " bullet lists whose
items may wrap onto indented lines, "> " block quotations, and
multi-line blocks such as song lyrics where each physical line is a hard
break within one paragraph; HTML comments are dropped) and
renders it as a Word document using python-docx's built-in Title/
Heading 1-4/List Bullet/List Number/Table Grid styles, so the result carries real
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

The first "# " is the title; "##" is a Heading 1 (a Part), "###" a Heading
2 (a chapter), "####" a Heading 3. A document with more "# " headings after
its title ("# Part One", "# Part Two") uses "#" for its Parts, so every level
moves down one: "#" a Heading 1, "##" a Heading 2, and so on. *Emphasis*
in a heading is read as it is in text.

Each heading level looks clearly different: sizes step down -- title 26,
Heading 1 20, Heading 2 17 (halfway between 1 and 3), Heading 3 14,
Heading 4 12 and italic -- and each goes a shade lighter in the same
heading blue. Word's stock Heading 2 and 3 were 13 and 12 point in one
color. Heading 2 also has a line under it across the whole width, like
the title's. style_headings() does the same for a document built by hand.

Every Part (Heading 1) and chapter (Heading 2) starts on a new page -- a
page break before it, not after the previous paragraph, so a chapter
that ends mid-page never bleeds into the next one's heading. The title
page is the one exception: nothing precedes it, so no break is needed --
and a heading that follows the title with nothing between them shares
the title's page, so a title never sits alone on an otherwise empty
page. `--no-section-breaks` turns the breaks off altogether, and only
when the person asked for that document's sections to flow on: it needs
`--breaks-off-because "<their words>"`, which the build records, and the
script refuses it without them.
`--soft-wraps` reads a source wrapped at a fixed width the way Markdown
does: a paragraph's lines join with a space, and only a line ending in a
backslash or two spaces breaks.

`--header-image PATH` puts a small copy of an image (a logo), 0.6 inch
tall, centered in the header of every page but the first, which already carries the
cover, with a small gap between it and the text. add_header_image() does
the same for a document built by hand. A logo on a front page is
COVER_LOGO_WIDTH (1.56 inches) wide unless a document says otherwise.

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

YAML front matter at the top of the file is left out. A "---" line is a
thin grey rule. A pipe table (a "| a | b |" row over a "|---|" row) is a
real Word table, its header row bold and shaded and repeated on each page,
every cell read like a paragraph. A "- " line indented under a list item is
a bullet nested under it, and a numbered list keeps counting after it. A
link to a heading in the same document, [Section](#section), jumps to it.

A line holding only an image, ![alt text](path), puts the picture itself
in the document, centered, at its own size up to IMAGE_MAX_WIDTH (4.5
inches), with the alt text as the picture's description for a screen
reader. The path is read relative to the manuscript, the way Markdown reads
it, and a missing file stops the build. A web address can't be fetched
here, so it prints as a link to the image instead. add_image() does the
same for a document built by hand.

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
      --no-section-breaks --breaks-off-because "Morgan: let the notes flow on" \
      --header-image logo.png
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
script writes only where --out says. A document the repository keeps goes
in its content folder's output/ (generated-docs-in-output) with its date
at the end of its name (dated-download-names); a one-off can go to a
scratch path and straight to the person who asked for it.
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
ANCHOR_LINK_RE = re.compile(r"(?<!\\)\[([^\]]+)\]\(#([^)\s]+)\)")
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
# (26 point) and Heading 2: Word's stock 14 point barely stood out from
# Heading 2 (Morgan, 2026-10-05).
HEADING_1_SIZE = 20
# practice: create-word-doc -- every heading level looks clearly different
# (Morgan, 2026-11-11: "Your Header 2 and Header 3 are almost identical,
# including the same color"). Word's stock Heading 2 and 3 were 13 and 12
# point in the same blue. Now each level steps down in size and goes a
# shade lighter in the same heading blue, and Heading 4 is italic, so
# no two levels share a look. Heading 2 sits halfway between Heading 1 and
# Heading 3. Heading 3 is not underlined, though Morgan suggested it: set
# beside a document's links, which are blue and underlined, an underlined
# blue heading read as one more link. Level: (points, color, italic,
# underline).
HEADING_LOOK = {
    1: (HEADING_1_SIZE, "1F3F6E", False, False),
    2: (17, "2E5C99", False, False),
    3: (14, "3D72B8", False, False),
    4: (12, "4F81BD", True, False),
}
# practice: create-word-doc -- Heading 2 carries a line under it across the
# whole width, the same line Word's Title style draws under the title
# (Morgan, 2026-11-12: "a line below it that goes across whole width, just
# like you did here for the title ... I think that will help differentiate
# the Header 2 from Header 3"). w:bottom attributes.
HEADING_2_RULE = (("val", "single"), ("sz", "8"), ("space", "4"),
                  ("color", "4F81BD"))
# practice: create-word-doc -- the page margin on all four sides, in inches.
# It was one inch until Morgan asked for 0.75 (2026-10-05). A builder that
# lays out its own page reads this rather than its own number.
PAGE_MARGIN = 0.75
# practice: create-word-doc -- the running header's logo, in inches tall.
# It was 0.4 until Morgan asked for it about half as big again (2026-10-05).
HEADER_IMAGE_HEIGHT = 0.6
# practice: create-word-doc -- where the running header's logo sits, and the
# room between it and the page's text. Word's own 0.5-inch header distance
# put the logo's foot right on the first line (Morgan, 2026-10-16), so the
# logo starts a little higher and keeps a small gap under it.
HEADER_DISTANCE = 0.35
HEADER_IMAGE_GAP = 12  # points
# practice: create-word-doc -- the logo on a front page, in inches wide,
# unless a document is told otherwise. It was 4.4, then 2.6 (2026-10-05),
# until Morgan asked for about 60% of that (2026-10-16). A builder that puts
# a logo on its cover reads this rather than its own number.
COVER_LOGO_WIDTH = 1.56
# practice: create-word-doc -- an image line becomes the picture, never the
# text "!alt" (Morgan, 2026-11-04: a memo's xkcd cartoon came out as its alt
# text, and a consuming repository patched the file after every build).
IMAGE_LINE_RE = re.compile(r"^\s*!\[([^\]]*)\]\(([^)\s]+)\)\s*$")
IMAGE_MAX_WIDTH = 4.5  # inches
# practice: create-word-doc -- ordinary Markdown that once came out wrong
# (2026-11-11, a guide for new account managers, which its repository had to
# rewrite before every build): YAML front matter printed as text, a "---"
# rule as a stray dash, a table as a line of pipes, a "# Part" after the
# title with its "#", and a bullet under a numbered item run into it.
HEADING_RE = re.compile(r"^(#{1,6})(?:\s+(.*?))?(?:\s+#+)?\s*$")
RULE_RE = re.compile(r"^\s{0,3}([-*_])(\s*\1){2,}\s*$")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
TABLE_HEADER_FILL = "DCE6F2"  # a pale tint of the heading blue
# A link to a heading in the same document, "[Section](#section)", becomes
# a link that jumps there: the heading's GitHub-style id -> its bookmark.
ANCHORS = {}
ANCHOR_ID_BASE = 100000  # bookmark ids clear of add_contents()' own


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


def style_headings(doc):
    """Give Heading 1 to 4 the sizes, shades and marks HEADING_LOOK sets,
    so each level reads as its own at a glance (practice: create-word-doc).
    A builder that makes its own headings calls this too. Returns the
    styles, Heading 1 first."""
    from docx.shared import RGBColor
    out = []
    for level, (size, color, italic, underline) in HEADING_LOOK.items():
        style = doc.styles[f"Heading {level}"]
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string(color)
        style.font.bold = True
        style.font.italic = italic
        style.font.underline = underline
        out.append(style)
    # The line under Heading 2, set on the style so every Heading 2 has it.
    p_pr = doc.styles["Heading 2"].element.get_or_add_pPr()
    for old in p_pr.findall(qn("w:pBdr")):
        p_pr.remove(old)
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    for key, val in HEADING_2_RULE:
        bottom.set(qn(f"w:{key}"), val)
    borders.append(bottom)
    p_pr.insert_element_before(
        borders, "w:shd", "w:tabs", "w:suppressAutoHyphens", "w:spacing",
        "w:ind", "w:jc", "w:outlineLvl", "w:rPr")
    return out


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


def style_list_nested(doc):
    """Word's built-in "List Bullet 2" for a bullet under a list item: its
    bullet sits under the item's text, LIST_HANG further in, and its own
    text LIST_HANG past that. Returns the style."""
    return style_list(doc, "List Bullet 2", indent=LIST_INDENT + LIST_HANG)


def style_list_number(doc):
    """Move Word's built-in "List Number" LIST_INDENT in from the margin,
    the same place as a bullet list. Returns the style."""
    return style_list(doc, "List Number")


def style_list(doc, name, indent=LIST_INDENT):
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
    pf.left_indent = Inches(indent + LIST_HANG)
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
                tab.set(qn("w:pos"), twips(indent + LIST_HANG))
        ind = ppr.find(qn("w:ind"))
        if ind is None:
            ind = OxmlElement("w:ind")
            ppr.append(ind)
        ind.set(qn("w:left"), twips(indent + LIST_HANG))
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
    # practice: create-word-doc -- a link to a heading in this document jumps
    # to it; one to an id no heading has prints as its text, like a path.
    text = ANCHOR_LINK_RE.sub(
        lambda m: (LINK_OPEN + "#" + ANCHORS[m.group(2).lower()] + LINK_MID
                   + m.group(1) + LINK_CLOSE)
        if m.group(2).lower() in ANCHORS else m.group(1), text)
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
                    if m.group(1).startswith("#"):
                        # In this document: jump to the heading's bookmark.
                        link.set(qn("w:anchor"), m.group(1)[1:])
                        link.set(qn("w:history"), "1")
                    else:
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


def strip_front_matter(text):
    """Drop a YAML front-matter block -- "---" on the first line, through
    the next "---" or "..." line -- which is data about the file, never
    text for the reader (practice: create-word-doc). Text without one
    comes back unchanged."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return "\n".join(lines[i + 1:]).lstrip("\n")
    return text


HANDMADE_CONTENTS_HEADING_RE = re.compile(
    r"^#{1,6}\s+(?:table\s+of\s+)?contents\s*$", re.IGNORECASE)
HANDMADE_CONTENTS_ITEM_RE = re.compile(
    r"^\s*(?:[-*+]|\d+[.)])\s+\[[^\]]+\]\(#[^)\s]*\)\s*$")
RULE_LINE_RE = re.compile(r"^\s*(?:-\s*){3,}$|^\s*(?:\*\s*){3,}$|^\s*(?:_\s*){3,}$")


def strip_handmade_contents(text):
    """Drop a contents list written by hand -- a "Contents" (or "Table of
    Contents") heading whose section is nothing but list items that each
    link inside the page -- and a "---" rule right after it. With
    --contents, Word builds its own list, and keeping the hand-made one
    gave the reader two, the second listing "Contents" itself as an entry
    (practice: create-word-doc, the contents page; the AM guide,
    2026-11-11). A "Contents" section with any prose in it is kept: it is
    writing, not a list of links. Text without one comes back unchanged."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if not HANDMADE_CONTENTS_HEADING_RE.match(line):
            continue
        j, items = i + 1, 0
        while j < len(lines) and not lines[j].lstrip().startswith("#"):
            if HANDMADE_CONTENTS_ITEM_RE.match(lines[j]):
                items += 1
            elif RULE_LINE_RE.match(lines[j]) and items:
                j += 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                break
            elif lines[j].strip():
                items = 0  # prose in the section: writing, keep it
                break
            j += 1
        at_heading = j >= len(lines) or lines[j].lstrip().startswith("#")
        if items and at_heading:
            return "\n".join(lines[:i] + lines[j:])
    return text


def heading_slug(raw, seen):
    """The id GitHub gives a heading, so "[Section](#section)" finds it:
    lower case, markup and punctuation gone, spaces as hyphens, and "-1",
    "-2" after a repeat. `seen` counts the ids already given."""
    text = ANCHOR_LINK_RE.sub(r"\1", LINK_RE.sub(r"\1", raw))
    text = re.sub(r"[*_`]", "", text).strip().lower()
    slug = re.sub(r"[^\w\- ]", "", text).replace(" ", "-")
    n = seen.get(slug, 0)
    seen[slug] = n + 1
    return slug if n == 0 else f"{slug}-{n}"


def add_bookmark(paragraph, name, bookmark_id):
    """Put a bookmark called `name` around a paragraph's text, for an
    in-document link to jump to."""
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bookmark_id))
    start.set(qn("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bookmark_id))
    p_pr = paragraph._p.pPr
    if p_pr is not None:
        p_pr.addnext(start)
    else:
        paragraph._p.insert(0, start)
    paragraph._p.append(end)


def table_rows(block):
    """A pipe table's rows as lists of cell text, header row first, or None
    when the block is not one: every line a "| ... |" row and the second
    line the "|---|" row under the header (practice: create-word-doc). An
    escaped "\\|" stays a character in its cell."""
    if len(block) < 2 or not all(TABLE_ROW_RE.match(l) for l in block) \
            or not TABLE_SEP_RE.match(block[1]):
        return None
    rows = []
    for line in [block[0]] + block[2:]:
        body = line.strip()[1:-1].replace("\\|", "\x06")
        rows.append([c.strip().replace("\x06", "|") for c in body.split("|")])
    width = max(len(r) for r in rows)
    return [r + [""] * (width - len(r)) for r in rows]


def add_table(doc, rows, soft_wraps):
    """A real Word table: a grid, the header row bold on a pale tint of the
    heading blue and repeated at the top of each page the table runs onto,
    every cell's text read like a paragraph's -- bold, italic, links."""
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = doc.styles["Table Grid"]
    for r, row in enumerate(rows):
        for c, cell_text in enumerate(row):
            cell = table.cell(r, c)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            add_inline(p, [cell_text], soft_wraps)
            if r == 0:
                for run in p.runs:
                    run.bold = True
                for run in p._p.iter(qn("w:r")):
                    rpr = run.find(qn("w:rPr"))
                    if rpr is None:
                        rpr = OxmlElement("w:rPr")
                        run.insert(0, rpr)
                    if rpr.find(qn("w:b")) is None:
                        rpr.insert(0, OxmlElement("w:b"))
                shade = OxmlElement("w:shd")
                shade.set(qn("w:val"), "clear")
                shade.set(qn("w:color"), "auto")
                shade.set(qn("w:fill"), TABLE_HEADER_FILL)
                cell._tc.get_or_add_tcPr().append(shade)
    header = table.rows[0]._tr.get_or_add_trPr()
    header.append(OxmlElement("w:tblHeader"))
    return table


def list_items(block, marker_re):
    """A list's items as [level, text] pairs, or None when the block is not
    a list whose first line matches `marker_re`. Level 0 is the list
    itself; an indented "- " line under an item is a bullet nested under
    it, level 1 (practice: create-word-doc: it was being run into the item's
    own text). Any other indented line continues the item before it."""
    if not marker_re.match(block[0]):
        return None
    indent = lambda l: len(l) - len(l.lstrip())  # noqa: E731
    base = indent(block[0])
    items = []
    for line in block:
        if marker_re.match(line) and indent(line) <= base:
            items.append([0, marker_re.sub("", line).strip()])
        elif BULLET_RE.match(line) and indent(line) > base:
            items.append([1, BULLET_RE.sub("", line).strip()])
        elif indent(line) > base or line[:1].isspace():
            items[-1][1] += " " + line.strip()
        else:
            return None
    return items


def bullet_items(block):
    """A "- " list's [level, text] items, or None when the block is not a
    list. See list_items()."""
    return list_items(block, BULLET_RE)


def tighten_nesting(paragraphs, items):
    """No gap where a list steps into or out of a nested bullet: Word drops
    the space between two items of one style by itself, but not between a
    numbered item and the bullet under it."""
    for p, (level, _), nxt in zip(paragraphs, items, items[1:]):
        if nxt[0] != level:
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.space_before = Pt(0)


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
    """A "1. " list's (start, [level, text] items), or None when the block
    is not one. Nesting and wrapping work as in list_items(): a bullet
    under a numbered item nests under it, and the numbering carries on
    after it."""
    m = NUMBER_RE.match(block[0])
    items = list_items(block, NUMBER_RE) if m else None
    if items is None:
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
    # The gap under the logo: Word starts the text below the header's full
    # height, its spacing included, so this is room above the first line.
    p.paragraph_format.space_after = Pt(HEADER_IMAGE_GAP)
    p.paragraph_format.line_spacing = 1.0  # a 1.3 line would pad the image
    section.header_distance = Inches(HEADER_DISTANCE)
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
    the paragraph as literal text. A "---" rule is a block of its own the
    same way."""
    is_heading = lambda l: HEADING_RE.match(l) or RULE_RE.match(l)  # noqa: E731
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


def add_image(doc, image_path, alt=""):
    """A picture on a paragraph of its own, centered, at its own size up to
    IMAGE_MAX_WIDTH inches wide, with alt as its description."""
    from docx.image.image import Image as DocxImage

    native = DocxImage.from_file(str(image_path))
    width = min(IMAGE_MAX_WIDTH, native.px_width / (native.horz_dpi or 96))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(image_path), width=Inches(width))
    if alt:
        for doc_pr in p._p.iter(qn("wp:docPr")):
            doc_pr.set("descr", alt)
    return p


def add_heading(doc, raw, level):
    """A heading whose text is read like a paragraph's: *italic* inside it
    is italic, never asterisks (practice: create-word-doc, 2026-11-11:
    "## From *Beloved by Clients*" printed its asterisks)."""
    p = doc.add_heading("", level=level)
    add_inline(p, [raw], False)
    # Plain text takes the heading style's own weight and slant: a run
    # marked "not bold" would turn a bold heading style off.
    for run in p.runs:
        if run.bold is False:
            run.bold = None
        if run.italic is False:
            run.italic = None
    return p


def add_rule(doc):
    """A "---" line as a thin rule across the text, never a stray dash: an
    empty paragraph with a light border under it."""
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.0
    p_pr = p._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    for key, val in (("val", "single"), ("sz", "6"), ("space", "1"),
                     ("color", "A6A6A6")):
        bottom.set(qn(f"w:{key}"), val)
    borders.append(bottom)
    p_pr.insert_element_before(
        borders, "w:shd", "w:tabs", "w:suppressAutoHyphens", "w:spacing",
        "w:ind", "w:jc", "w:outlineLvl", "w:rPr", "w:sectPr")
    return p


def heading_levels(blocks):
    """Each heading block's Word level, by block index: 0 for the title
    (the first "# "), and for the rest one less than its "#" count -- "##"
    a Heading 1, "###" a Heading 2. A document with more "# " headings
    after its title (a "# Part One", a "# Part Two") uses "#" for its
    Parts, so every level moves down one: "#" a Heading 1, "##" a Heading 2,
    "###" a Heading 3 (practice: create-word-doc, 2026-11-11: such a Part
    printed as "# Part One")."""
    found = []
    for i, block in enumerate(blocks):
        m = HEADING_RE.match(block[0]) if len(block) == 1 else None
        if m:
            found.append((i, len(m.group(1))))
    title = next((i for i, n in found if n == 1), None)
    shift = 1 if any(n == 1 and i != title for i, n in found) else 0
    return {i: 0 if i == title else min(9, max(1, n - 1 + shift))
            for i, n in found}


def build_doc(manuscript_path, short_name, add_footer, date_str, contents=False,
              section_breaks=True, header_image=None, soft_wraps=False,
              header_on_first_page=False, footer_label=None):
    text = strip_front_matter(strip_comments(
        manuscript_path.read_text(encoding="utf-8")))
    if contents:
        text = strip_handmade_contents(text)
    STRAY_ASTERISKS.clear()
    CODE_SPANS.clear()
    lines = text.split("\n")
    blocks = group_blocks(lines)
    levels = heading_levels(blocks)
    # A heading something links to ("[Section](#section)") gets a bookmark
    # to jump to; one nothing links to is left without.
    ANCHORS.clear()
    linked = {m.group(2).lower() for m in ANCHOR_LINK_RE.finditer(text)}
    seen, bookmarks = {}, {}
    for i in levels:
        slug = heading_slug(HEADING_RE.match(blocks[i][0]).group(2) or "", seen)
        if slug in linked:
            bookmarks[i] = ANCHORS[slug] = f"_md{len(bookmarks) + 1}"

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
    style_headings(doc)
    style_list_bullet(doc)  # practice: create-word-doc
    style_list_number(doc)
    style_list_nested(doc)

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
    for index, block in enumerate(blocks):
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

        image = IMAGE_LINE_RE.match(first) if len(block) == 1 else None
        if image and not re.match(r"^(?:https?:)?//", image.group(2)):
            # practice: create-word-doc (images)
            image_path = (manuscript_path.parent / image.group(2)).resolve()
            if not image_path.is_file():
                sys.exit(f"error: image {image.group(2)} in "
                         f"{manuscript_path} does not exist")
            last_para = add_image(doc, image_path, image.group(1))
            last_was_heading = False
            continue
        if image:
            # A web image can't be fetched here: print it as a link to it.
            block = [f"[{image.group(1) or image.group(2)}]({image.group(2)})"]
            first = block[0]

        if index in levels:
            level = levels[index]
            raw = HEADING_RE.match(first).group(2) or ""
            if level == 0:
                last_para = add_heading(doc, raw, 0)
                # A heading straight after the title shares its page: a
                # break there would leave the title alone on page one
                # (Morgan, 2026-10-05, on a blurbs file whose cover held
                # nothing else).
            else:
                # practice: create-word-doc (chapter page breaks) -- a Part
                # (Heading 1) or a chapter (Heading 2) starts a new page. The
                # break is an explicit page-break RUN appended to the END of
                # the paragraph that comes BEFORE this heading, never a
                # property set on the heading paragraph itself. That way the
                # break lives in a different, earlier paragraph and can't
                # land after the heading's own text. A sub-section (Heading 3
                # and below, "####" -- Morgan, 2026-10-13, a proposal's People
                # and Processes) flows on.
                if section_breaks and level <= 2 and last_para is not None \
                        and not last_was_heading:
                    last_para.add_run().add_break(WD_BREAK.PAGE)
                last_para = add_heading(doc, raw, level)
            if index in bookmarks:
                add_bookmark(last_para, bookmarks[index], ANCHOR_ID_BASE + index)
            last_was_heading = True
            continue

        if RULE_RE.match(first) and len(block) == 1:
            last_para = add_rule(doc)
            last_was_heading = False
            continue

        rows = table_rows(block)
        if rows is not None:
            add_table(doc, rows, soft_wraps)
            # The text after a table starts a little below it, and a page
            # break for the next chapter lands here, never inside a cell.
            last_para = doc.add_paragraph()
            last_para.paragraph_format.line_spacing = 1.0
            last_was_heading = False
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
            made = []
            for level, item in items:
                if level:
                    # A bullet under a numbered item; the numbering carries
                    # on after it, since the items share one count.
                    p = doc.add_paragraph(style="List Bullet 2")
                else:
                    p = doc.add_paragraph(style="List Number")
                    if num_id is None:
                        num_id = restart_numbering(doc, p, start)
                    set_num_id(p, num_id)
                add_inline(p, [item], soft_wraps)
                made.append(p)
            tighten_nesting(made, items)
            end_list(doc, p)
            last_para = p
            last_was_heading = False
            continue

        items = bullet_items(block)
        if items is not None:
            lead_into_list(doc, last_para)
            made = []
            for level, item in items:
                p = doc.add_paragraph(
                    style="List Bullet 2" if level else "List Bullet")
                add_inline(p, [item], soft_wraps)
                made.append(p)
            tighten_nesting(made, items)
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
RECORDED_VALUES = ("short_name", "date", "footer_label", "breaks_off_because")
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
        help="let sections flow on instead of starting each ## and ### on a new page; "
             "needs --breaks-off-because",
    )
    ap.add_argument(
        "--breaks-off-because",
        default=None,
        metavar="WORDS",
        help="the person's own words asking for this document's sections to flow "
             "on, quoted with who said them; required by --no-section-breaks",
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
    # practice: create-word-doc -- page breaks go off only on the person's
    # word, never a session's judgment (2026-11-12: a 28-page guide was
    # built without them because "most pages were half empty").
    if args.no_section_breaks and not (args.breaks_off_because or "").strip():
        ap.error("--no-section-breaks needs --breaks-off-because \"<the person's "
                 "own words>\": every Part and chapter starts on a new page "
                 "unless the person asked for this document's sections to flow "
                 "on (practice: create-word-doc)")

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
