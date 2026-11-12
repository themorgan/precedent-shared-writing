---
slug:        create-word-doc
title:       Every Word document built for a reader carries a Page X of Y footer and opens without asking anything; a structured export runs tools/create_word_doc.py
tier:        on-demand
severity:    default
applies_to:  ["tools/create_word_doc.py"]
applies_to_why: "The glob is where the script changes; building a Word file edits no file here, so index_required keeps the occasion-index line that reaches a session doing it. Decided 2026-10-17."
occasion:    "building a Word (.docx) document for someone to download"
gates:       []
index_clause: "a Word file for a reader: a footer, and it opens without an update-fields prompt"
index_required: true
checked_by:  tools/checks/check_create_word_doc.py
ships:       ["tools/create_word_doc.py"]
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-09-18
approved_by: "Morgan F, 2026-09-18, via Go Update -- moved here from a private repo-local set, generalized from a book-*/MANUSCRIPT.md-specific rule to any structured-document export; revised again 2026-09-18, Morgan F, via Go Update, to switch the chapter-break mechanism from a heading paragraph property to an explicit page-break run in the preceding paragraph; revised a third time same day, Morgan F, via Go Update, to skip the break when a heading has no body of its own before the next heading (found via Part II, verified on Microsoft (MS) Word desktop macOS 16.78.3); revised 2026-10-04 at Morgan F's own request, to set a \"> \" block as an indented block quotation rather than printing the markers; revised 2026-10-05 at Morgan F's own request, so a downloaded document never asks to update its fields when it opens; revised 2026-10-05 at Morgan F's own request, so a heading straight after the title shares its page, with an optional running header image on every page but the first; revised 2026-10-05 at Morgan F's own request, to set bullet lists half an inch in from the margin rather than flush with it; revised 2026-09-26, Morgan F, \"Go ahead on shared writing\" (strength: assented), to declare the script in ships: so it travels with the practice instead of being copied in by hand; revised 2026-10-05 at Morgan F's own request, so no emphasis asterisk reaches a Word document's text -- italic nested in bold, or wrapped over two lines, printed its asterisks in the Joseph manuscript; revised again the same day at his own request, so crossed emphasis takes the outer mark's form; revised again the same day at his own request, for a sans-serif footer a touch smaller than the body, a running header logo half as big again, and a Heading 1 clearly bigger than Heading 2; revised again the same day at his own request, so a contents page looks like one; revised again the same day at his own request, for 0.75-inch page margins on all four sides; revised again the same day at his own request, so each contents entry is set in the footer's sans-serif face and underlined, to read as a link; revised 2026-10-13 at Morgan F's own request (\"in precedent-shared-writing we have a bunch of rules about making .md docs into MS Word docs and let's do that with this doc - including using the Pesty logo in the header\"), for the first non-manuscript document built with it: backslash escapes, web links kept as links, #### headings, a footer label of the document's own, and the logo on page one; revised again 2026-10-13 at his own request: lists a quarter inch in (\"half an inch ... is far too much for my taste\"), real numbered lists, and curly quotes and dashes in every Word document (\"they ALWAYS should\"), dashes by judgment (\"--\" between two words without spaces is always an em dash); and the same day, that a lead-in line has no space between it and its list, and a list's end half the normal space; and that a lead-in always stays on the page of its list; revised 2026-10-14 at his own request (\"I think we need that same space before the bullet list\"), so a lead-in leaves the same half gap above its list as the list leaves below it; revised 2026-10-15 from a consuming repository's root-issues handoff, which Morgan F passed to this set's maintainers without a word on approval (strength: unknown): no --short-name demanded when nothing uses it, and every document records its build for --rebuild; revised 2026-10-16 at Morgan F's own request (\"Please leave a bit more space ... this is a small tweak\"; the front-page logo \"about 60% size it is now ... consistent for ALL pages as a sort of default practice\"), for a small gap under the running header's logo and a 1.56-inch front-page logo by default; revised 2026-10-17 by the session under Morgan F's delegation of that day (\"Fix the other issues you found including the checks that never run. Tell me what you decide. I will be offline so don't wait for me. Approved, act, and Booked.\"): index_required, so a session building a Word file sees it; where the file goes and its name deferred to generated-docs-in-output and dated-download-names; the procedure moved from the Rule into Detail; revised 2026-11-11 from a consuming repository's handoff that Morgan F asked for (\"Yes, do that fix in a new session you start rooted in the writing practice repo\"), with his own words on headings (\"Your Header 2 and Header 3 are almost identical, including the same color\"): tables, front matter, rules, nested bullets, a \"# Part\" after the title, emphasis in headings and in-page links, and a distinct look for each heading level; and the same day at his own request (\"Fix the builder, as per your recommendation\"), so --contents drops a contents list written by hand instead of printing two; revised 2026-11-12 at Morgan F's own request (\"It wasn't followed, so you should do a fix to make sure it's followed in the future\"), so page breaks go off only on the person's word, which --no-section-breaks now demands in --breaks-off-because; and the same day at his own request (\"for the sections with Heading 2 ... a line below it that goes across whole width, just like you did here for the title\"), so every Heading 2 carries the title's line under it; and the same day at his own request (\"the line you put below the second heading is soooo low it looks broken ... the heading 1 should be centered\"), so Heading 2 is single-spaced and its line sits just under the words, and Heading 1 is centered; and the same day at his own request (\"the number formatting is messed up and collapsed ... Please fix including at the root\"), so an indented paragraph inside a numbered list belongs to its item and the list's count carries on after it"
---
## Rule
**Any Word document built for someone to download carries a footer -- a
live "Page X of Y" and a line naming the document and its date -- and
opens without asking the reader anything.** That holds for a structured
export and a one-off alike.

**A structured export runs [`tools/create_word_doc.py`](../tools/create_word_doc.py)**
-- a manuscript, a long report, anything with real section headings --
rather than a conversion script of its own. It builds the document and its
footer in one pass, with the defaults `## Detail` lists. **A one-off built
any other way puts the same footer, and the same defaults where they apply,
into whatever script makes it.**

**Every Part and chapter starts on a new page, unless the person asked,
for that document, for its sections to flow on.** A session never turns
the breaks off on its own judgment, not even to save half-empty pages: the
script's `--no-section-breaks` takes the person's own words with it, in
`--breaks-off-because`, and refuses to build without them.

**Where the built file goes and what it is called are other rules'.** A
document the repository keeps is committed in its content folder's
`output/`, per the ladder set's `generated-docs-in-output`, and every document carries its date at the end of its name
(`Name-2026-12-31.docx`), per
[dated-download-names](dated-download-names.md). The script writes where
`--out` tells it to and decides neither.

## Detail
### What a Word document carries

**Any Word document built for someone to download carries a footer --
not just a structured, multi-section export.** Two paths, one
requirement:

- **A structured export** -- a manuscript, a long report, anything with
  real chapter/section headings -- runs [`tools/create_word_doc.py`](../tools/create_word_doc.py) rather
  than a one-off conversion script; what follows is what it includes in the
  same pass.
- **Anything else** -- a one-off built from a business note, a
  brainstorm doc, or any other unstructured source -- has no shared tool
  yet, so the footer is built by hand into whatever script generates the
  `.docx` (the same way the first structured export was, before it became
  [`tools/create_word_doc.py`](../tools/create_word_doc.py)). It still needs both pieces the structured
  export's footer has: a live "Page `<n>` of `<total>`" field, and a
  second line naming the document and the date (`<TITLE> - <date>`).
  "CONFIDENTIAL - DRAFT" is a reasonable prefix for anything drawn from
  proprietary material, but the structured export's own "DRAFT BOOK"
  wording (below) is that use case's own convention and doesn't transfer
  as-is. With `docx-js` (Node), that's a `Footer` on the section, with
  `PageNumber.CURRENT`/`PageNumber.TOTAL_PAGES` inside a `TextRun`'s
  `children` for the live fields -- simpler than `python-docx`'s manual
  `w:fldChar` Office Open XML (OOXML) (`add_field()` in
  [`tools/create_word_doc.py`](../tools/create_word_doc.py) is that lower-level approach, for when
  `python-docx` is the tool already in use).

[`tools/create_word_doc.py`](../tools/create_word_doc.py) builds the `.docx` (real Title/Heading 1/
Heading 2/List Bullet structure, not paragraphs that merely look like
headings) **and** stamps a footer on every page in the same pass, so the
two never drift apart into "the doc" and "the doc with the footer someone
forgot":

```
python3 tools/create_word_doc.py some-manuscript/MANUSCRIPT.md --out /path/to/Draft.docx
```

The footer (on by default; `--no-footer` to skip it) carries two
centered lines on every page:

```
Page <n> of <total>
CONFIDENTIAL - DRAFT BOOK: <SHORT NAME> - <date>
```

**The footer is set in a sans-serif face, a touch smaller than the
body** -- Arial, 10 point against the body's 12 -- so it reads as page
furniture, set apart from the serif text. It lives in Word's own
**Footer** style, which every footer paragraph carries, so it is one
style to change. A Word document built by hand calls `style_footer(doc)`
(passing a smaller size when its body is smaller than 12 point) and adds
each footer paragraph with `style="Footer"`.

`<n>`/`<total>` are live Word PAGE/NUMPAGES fields, not a computed
count, so they stay correct after Word repaginates. `<SHORT NAME>`
defaults to a `book-*/` ancestor directory's name (this tool's own
manuscript-export convention -- `book-example` -> `Example`) with `--short-
name` required whenever the source isn't under a `book-*/` directory or
that mechanical derivation isn't what's wanted. It is needed only by that
default line: with `--footer-label` or `--no-footer` it goes unused, and
nothing asks for it. The date defaults to
today via [`tools/precedent_time.py`](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_time.py) (practice: timestamps-carry-offset)
-- a bare `date.today()` would silently stamp the container's UTC date,
which is wrong for part of every day.

**Every Part and chapter heading (Heading 1 and Heading 2) starts on a
fresh page** -- a page break
before the heading, not after whatever came before it, so a section that
ends mid-page never runs its last paragraph into the next section's
title. The break is an explicit page-break run appended to the end of
whatever paragraph precedes the heading, never a property on the
heading's own paragraph -- that way it structurally cannot land after
the heading's own text. **Two headings with nothing between them --
a `##` Part immediately followed by a `###` with no body prose of its
own, e.g. `book-example`'s "Part II"** -- stack together on the same
fresh page rather than each forcing a separate break: the second heading
does not get its own break when the one right before it was itself a
heading with nothing of its own to separate them. The title page is the
one exception that needs no break of its own: it opens the document, so
nothing precedes it. **The title counts as a heading for this**: a `##`
straight after the title, with nothing between them, shares the title's
page, so a title never sits alone on an otherwise empty page.
`--no-section-breaks` (`section_breaks=False`) turns the breaks off
altogether, for a document the person wants read flowing on -- notes, a
brainstorm -- and only on their word: it needs `--breaks-off-because
"<their words, and who said them>"`, which the build record keeps so
`--rebuild` carries it, and without it the script stops before building
anything. `build_doc()` called directly takes no such argument; a script
that calls it with `section_breaks=False` answers for the same consent.

**A running header is optional: `--header-image PATH`**
(`header_image=` to `build_doc()`). It puts a small copy of the image --
a logo, 0.6 inch tall -- centered in the header of every page but the
first, which carries the cover and so gets Word's "different first page"
with an empty header and a copy of the footer (without the copy, page one
would lose its "Page X of Y"). A Word document built by hand gets the
same header from `add_header_image(section, path)`, called once its
footer is written. **The logo sits a little high and keeps a small gap
under it**: the header starts 0.35 inch from the page's top edge rather
than Word's 0.5, and 12 points separate the logo's foot from the text, so
the text below never runs up against it.

**A logo on a front page is 1.56 inches wide by default**
(`COVER_LOGO_WIDTH`), centered at the top, unless the document is told
otherwise. A builder that puts a logo on its cover reads that constant
rather than keeping a number of its own, so every document's cover logo
is the same size.

**A document that is no manuscript names itself in the footer and can
carry its logo on page one.** `--footer-label TEXT` (`footer_label=`)
replaces the footer's second line up to the date -- `CONFIDENTIAL - CHIEF
OF STAFF PROPOSAL - 2026-10-13` -- since "DRAFT BOOK" is the manuscript's
own wording. `--header-on-first-page` (`header_on_first_page=`, or
`add_header_image(..., first_page=True)`) puts the header image on page
one as well, for a letter or proposal whose first page is no cover and
whose logo there is the letterhead.

**A list is set off by half the normal gap, above and below.** A body
paragraph straight before a bullet or numbered list ("I see four possible
outcomes:") has half the normal end-of-paragraph space after it, and the
list's last item has the same half space after it: a full gap looked like
a hole, and a lead-in flush on its list looked cramped (Morgan,
2026-10-14). The items sit close together (Word's contextual spacing) and
the list styles carry no space before. The lead-in is kept with the
list's first item, so it never sits alone at the foot of a page. A
heading before a list keeps its own spacing.

**A `1. ` list is a real Word numbered list** (List Number), never
numbers typed as text: it sits where a bullet list sits, and each list
restarts at its own first number rather than carrying on from the last
one. `style_list_number(doc)` styles it for a document built by hand.

**Typography is always finished.** Every straight quote, single or double,
becomes the curly one; `--` and `---` always become an em dash (—); and a
hyphen between two numbers that make a range (1990-2000, pages 10-20)
becomes an en dash (–), while a date like 2026-10-13 keeps its hyphens. A
web link's address and a backslash-escaped character are left alone. The
rules are [curly-quotes](curly-quotes.md)'s, in
[`tools/typography.py`](https://github.com/alex137/BestPractice/blob/staging/tools/typography.py), an engine file every
repository has (since 2026-10-16; this set shipped it before), shared with
every other builder for an outside reader; `smarten(text)` does it for a document
built by hand. The Markdown source keeps its plain quotes and hyphens.
**Code stays code:** a fenced block is set line for line as typed, and a
code span keeps its characters without its backticks, both in a
fixed-width face (Courier New, 10 point), never converted.

**What Markdown means, the Word file means too.** A backslash escape
prints as its character (`\$15k` is `$15k`, `\[A\]` is `[A]`); a link
to the web (`http:`, `https:`, `mailto:`) stays a real hyperlink, blue and
underlined, while a link to a path in the repository still prints as its
text alone; and a `####` heading is a real Heading 3 that flows on with
no page break. A link to a heading in the same document
(`[Section](#section)`, as a hand-made contents list writes it) jumps to
that heading; one to an id no heading has prints as its text. `*italic*`
inside a heading is italic, never asterisks.

**Which heading is which level.** The first `#` is the title. Normally
`##` is a Heading 1 (a Part), `###` a Heading 2 (a chapter), `####` a
Heading 3. **A document with more `#` headings after its title** -- a
`# Part One`, a `# Part Two` -- uses `#` for its Parts, so every level
moves down one: `#` a Heading 1, `##` a Heading 2, `###` a Heading 3,
`####` a Heading 4. Either way the page breaks follow the Word level, not
the number of `#`s: Heading 1 and 2 start a page, the rest flow on.

**More Markdown, read as Markdown means it.** YAML front matter (`---`
... `---` at the very top) is data about the file and never printed. A
`---` line on its own is a thin grey rule across the text. A pipe table
(`| a | b |` over a `|---|` row) is a real Word table: a grid, its header
row bold on a pale tint of the heading blue and repeated on each page the
table runs onto, each cell keeping its bold, italic and links. A `- `
line indented under a list item is a bullet nested under it, and a
numbered list's count carries on after it. **An indented paragraph after
a blank line is the item's own second paragraph**: it is set under the
item's text, and the items after it carry on the same count -- "3." after
item 2's extra paragraph is item 3, never typed into that paragraph as
text (Morgan, 2026-11-12: "the number formatting is messed up and
collapsed").

**Every heading level has a look of its own.** Each steps down in size
and goes a shade lighter in the same heading blue: Heading 1 is 20 point
(the title is 26), Heading 2 17, halfway between Heading 1 and Heading
3, Heading 3 14, and Heading 4 12 and italic. Word's stock sizes put
Heading 2 and 3 at 13 and 12 point in one color, and Morgan could not
tell them apart (2026-11-11). **Heading 2 also has a line under it across
the whole width**, the same line Word's Title style draws under the title,
so a Heading 2 never reads as a Heading 3 (Morgan, 2026-11-12); it is
single-spaced, as the title is, so that line sits just under its words:
at body text's 1.3 spacing it hung a whole gap below and looked broken
(Morgan, 2026-11-12). **Heading 1 is centered**, so a Part never reads as
a chapter (Morgan, 2026-11-12). Heading 3
is not underlined, though that
was considered: beside a document's links, which are blue and
underlined, it read as one more link. `style_headings(doc)` sets all
four (`style_heading_1(doc)` sets Heading 1 alone); `build_doc()` calls
it, and a document built by hand with its own sizes keeps the same order.
A project with a palette of its own (`visual-palette`) may restyle them
in its own colors.

**Page is A4 with 0.75-inch margins on all four sides, default line
spacing is 1.3x**, set once on the `Normal`
style and the section's page size rather than per paragraph, so every
paragraph inherits both without the parser having to know about them.

**A `Words: <count>` line in the source becomes a live Word `NUMWORDS`
field**, the same mechanism as the footer's page count, and any trailing
parenthetical after it (`(PART 1)`, or anything else) is dropped. A
number typed once into a source document is exactly the kind of count
that goes stale the moment the text changes; the field recalculates
instead of needing someone to notice and retype it.

**A `> ` block is a block quotation, set the way a printed book sets
one off** -- indented half an inch on both sides, a point smaller than
the body, a little tighter, upright, with no quotation marks and no `>`
anywhere in the text. A bare `>` line inside the block starts a new
paragraph of the same quotation. Every quotation paragraph carries Word's
own **Quote** style, restyled that way, so a reader who wants them
italic, or wider, changes one style in Word's Styles pane and every
excerpt follows. Write a long excerpt from another text -- scripture, a
letter, a speech -- as a `> ` block in the source, never as a quoted
paragraph of body text: the block is what tells the export it is an
excerpt.

**A bullet list and a numbered list sit a quarter inch in from the
margin**, never flush with it and never half an inch in: the bullet or
number at a quarter inch, the item's text a quarter inch past it, and every wrapped line of an item lined up under its own
text. Word's stock **List Bullet** style puts the bullet right on the
margin, which reads as a mistake, most of all beside block quotations
indented half an inch. `style_list_bullet(doc)` moves it, in the style
and in the bullet's numbering level both, so every List Bullet paragraph
follows; `build_doc()` calls it, and a Word document built by hand calls
it once, after creating the document. A builder that sets a list's
indents itself -- a numbered list written with literal numbers, a list
nested inside another -- takes them from `LIST_INDENT` and `LIST_HANG`
in the same script, so every list in every document sits in the same
place.

**A contents page is optional: `--contents`** (`contents=True` to
`build_doc()`; off by default). It puts Word's own table of contents on a
page of its own before the first Part -- a "Contents" line in Word's
table of contents (TOC) heading style, **TOC Heading**, which stays out of the contents and the Navigation
Pane, then a table-of-contents field listing the Parts and chapters
(Heading 1 and 2). **A contents list written by hand in the Markdown is
dropped** when `--contents` is on: a "Contents" heading whose section is
nothing but links inside the page, and a `---` rule right after it, so the
reader gets one contents list, not two. A "Contents" section with any
prose in it is kept, and without `--contents` the hand-made list stays.
The field is written already filled in: each title is a link that jumps
to its heading. **It looks like a contents page**, in Word's own **TOC 1**
and **TOC 2** styles: each Part bold, with a little space above it, its
chapters indented under it, and the whole list single-spaced, never in
the body's 1.3 spacing. **Every entry is set in the footer's sans-serif
face and underlined**, so it reads at a glance as a link, which it is,
rather than as more of the text. Both styles carry a dotted tab at the right
margin, so the page numbers Word adds on **Update Field** land at the end
of a dot leader, and Word keeps the styles when it rewrites the list. A
document that builds its own contents list by hand calls
`style_contents(doc)` and sets each entry in those styles. It carries no page numbers, since only Word knows where
its pages break and the file must not ask Word to work them out on
opening (next paragraph); a reader who wants them right-clicks the list and picks
**Update Field**. Ask for it when the reader will move around a long
document; a short one does not need it.

**A Word document built for someone to download never asks anything when
it opens.** In particular it never sets Word's "update fields on open"
setting (`updateFields` in the document's settings), which is what puts
up *"This document contains fields that may refer to other files. Do you
want to update the fields in this document?"* -- a question that alarms
the reader, and that a document from someone they trust should never
raise. Every field in the file either updates by itself (the footer's
page number and page count) or is written already showing the right
result (the contents list, the word count). This holds for a hand-built
one-off as much as for this script's output, and the check below fails
on any script under `tools/` that writes the setting.

**No asterisk that marks emphasis ever reaches a Word document's text.**
A `*phrase*` in the source is italic in Word, a `**phrase**` is bold, and
`***phrase***` is both -- the asterisks themselves are gone. That holds
when one sits inside the other (`**a long bold sentence with a *phrase*
in italics**`, the commonest way authors stress a word inside a stressed
sentence) and when an italic title wraps from one source line onto the
next. Word can show both at once (bold italic), so it does. **Where it
cannot -- the marks cross, as in `**a *b** c*`, or an inner one is never
closed -- the outer one wins**: the text takes the outer mark's form, and the
inner mark's asterisks are left out. [`tools/create_word_doc.py`](../tools/create_word_doc.py)
reads emphasis the way Markdown does, applies the outer-wins rule, and warns
on stderr, quoting the passage, about any asterisk placed like emphasis that
nothing pairs, which it leaves out of the text; an escaped `\*` and a spaced
`5 * 3` stay plain characters and are not reported. A warning is a typo to
fix in the source before the file goes to anyone. A hand-built
one-off carries the same promise: whatever script builds it confirms, after
building, that no `*` (and no other Markdown or HTML markup) is left in the
document's text, and fails if one is.

**A document says how it was built, and can be built again the same
way.** The script writes its own options -- the manuscript, every flag set,
and a `--date` if one was given -- as JSON into the `.docx`'s Comments
property (File > Properties in Word), behind the marker
`create_word_doc.py build:`, with paths relative to the manuscript's
repository. `--rebuild OLD.docx --out NEW.docx` reads that record and
builds from the current source with the same options, dated today unless
the record carries a date; an option given beside it wins. It prints the
command it amounts to. A file built before the record existed is refused
with a message saying so: build it once with its flags in full, and every
later rebuild has them. A guessed flag is a differently formatted document
for an outside reader (a page break before every section, no logo on page
one), and nothing in the old file says which flags made it.

### The parser, and how the script travels

The parser handles a working subset of Markdown: `#` to `######` headings
(even when not followed by a blank line -- some manuscripts' own section
headers have none, and an earlier draft of this script merged the
heading into the following paragraph and leaked the `#` characters into
the body text as a result), `**bold**`, `*italic*` and `***both***` inline
spans -- nested either way round and carried across a wrapped line, matched
the way Markdown matches them rather than with one flat pattern, which could
not see an italic inside a bold and printed its asterisks as text --
`[links](...)` printed as their
text (the target is a path in the source's repository, which means
nothing in a Word file), `- ` bullet blocks whose items may wrap onto
indented continuation lines, `> ` block quotations (a block counts as one only when
every line of it starts with `>`), and multi-line blocks such as a lyrics or verse excerpt,
where each physical line becomes a hard line-break within one paragraph
rather than its own paragraph. A source wrapped at a fixed width -- a
note whose paragraphs run over several lines of seventy-odd characters --
asks for `--soft-wraps` (`soft_wraps=True`) instead, and reads the way
Markdown does: a paragraph's lines join with a space, and only a line
ending in `\` or two spaces breaks. A trailing `\` (Markdown's own hard
line break) is dropped either way, since the line already breaks, and HTML comments -- a
file header, a generated-block marker -- are removed before parsing.

python-docx, not a Node/docx-js script, so the tool matches a repo whose
`tools/` is otherwise all-Python -- and, incidentally, python-docx's
stock template already defines a proper `Normal` style, sidestepping a
real bug an earlier docx-js draft of this script hit: a missing explicit
`Normal` style definition (legal per the OOXML spec, since real Word
falls back to document defaults) that made `python-docx` and `pandoc`'s
own docx reader return `None` for every paragraph's resolved style.

**Vendoring:** the script travels with the practice. It is listed in this
practice's `ships:` (universal practice
[practice-carries-its-files](https://github.com/alex137/BestPractice/blob/staging/practices/practice-carries-its-files.md)), so
the materializer delivers it: every repository that resolves this set receives
[`tools/create_word_doc.py`](../tools/create_word_doc.py) on its next sync, alongside the check and its
test, and never copies it by hand. That copy is tracked where the
repository declares this set. Where the set reaches it only through a
person's individual set instead, the session start and each sync put it
in place untracked, kept out of git by the clone's own exclude file; that
route needs an engine from 2026-10-13 or later. A repository that only ever needs the ad
hoc, built-by-hand half can decline it in its own `precedent.json` under
`declined_ships`, with a reason; the check below skips cleanly where the
script is absent, though this practice's own test then fails there, since it
exercises the real script. `ships:` needs an engine from 2026-09-26 or later;
an older engine ignores the field and delivers nothing.

## Why
The first version of this workflow was a scratch script written once,
in a session's own scratchpad, for a single conversion -- functional,
but with nowhere for the footer requirement to live once that session
ended, so the next export request would have re-derived (or missed) the
footer from scratch. Landing the script under `tools/` and gating it
with a practice means the footer is part of what "export a structured
document" *means*, not a step a future session has to remember to ask
about.

## Story
2026-09-18, in a private repo: first Word export of
an example manuscript file, done as a one-off script in a session
scratchpad. Morgan came back asking for a page-numbered "Page X of Y"
footer plus a "CONFIDENTIAL - DRAFT BOOK: <NAME> - <DATE>" line, and to
turn the whole thing into a standing practice with `Go Merge` -- so the
footer becomes something every future export carries automatically
rather than a detail re-requested each time.

Same day, next request: a page break before every chapter, again with
`Go Merge`. Folded into the same Rule rather than a separate practice --
it is the same "what does exporting a structured document mean here"
question the footer already answers, not a new occasion.

Same day again: A4 paper, 1.3x line spacing, and the manuscript's own
"Words: 4,944 (PART 1)" line turned into a live, whole-document count
with the `(PART 1)` dropped. Same reasoning as the two requests before
it -- these become defaults of the export, not something re-requested
per document.

Same day, later: a session built a `.docx` from an unrelated brainstorm
note (not a manuscript) with a one-off `docx-js` script, and shipped it
with no footer at all -- the practice's `applies_to` only ever matched a
`book-*/MANUSCRIPT.md` path or [`tools/create_word_doc.py`](../tools/create_word_doc.py) itself, so it
had no way to fire for a one-off built from an unrelated source file.
Morgan asked why, then said `Go merge` on the Rule above: the footer
requirement now covers every Word document built for him, not only
structured exports.

**Moved to `precedent-team-writing` on 2026-09-18**, from
a private repo-local set, on Morgan's own
reconsideration in the same thread: the footer requirement isn't about
that repo's subject (a book and its brainstorm) at all, it's the craft
of handing someone a finished document -- exactly this set's subject.
The book-*/MANUSCRIPT.md-specific wording is generalized to "a structured
export" throughout; nothing about the mechanism changed. `Go update`.

Same day, later still: Morgan opened an export and reported the break
landing after a chapter's own heading, not before it -- the opposite of
this Rule. The mechanism at the time was `paragraph_format.page_break_
before = True` set on each heading paragraph, which is unambiguously
"before" per the OOXML spec (verified directly in the generated XML and
via `python-docx`'s own paragraph model, across every heading in a real
export, twice) -- but Morgan, looking at the actual rendered file rather
than the XML, was firm it was still wrong on a second, freshly-generated
copy. Rather than keep arguing from a spec reading neither of us could
render to confirm (`soffice`/`pandoc` both broken in the working
session), the mechanism was switched to a more defensive one: an
explicit page-break **run**, appended to the end of the paragraph that
precedes each heading, rather than a property on the heading paragraph
itself. `Go update`.

Morgan checked the re-export on MS Word desktop (macOS, version 16.78.3)
and reported it still wrong, specifically at "Part II" -- naming the
exact heading pinned the actual bug down for real this time. The example
manuscript's `## Part II: [Section Title]` has
no body text of its own: it's immediately followed by `### Introduction`
with nothing between them (same shape at `## Part I` -> `### [Chapter
Title]`). Both page-break mechanisms so far gave every `##`/`###` heading
its own break unconditionally -- so when a Part heading has no body
before the next heading, that second break has nowhere to land but
inside the FIRST heading's own paragraph (the run-based version) or
isolates it alone on a page (the property-based version before it) --
either way, from a reader's perspective, "Part II" is immediately
followed by a page break with nothing in between: exactly "a page break
after the chapter name."

**The actual fix**: track whether the paragraph a heading is about to
break from is itself a heading with no body of its own, and skip the
break in that case, so two headings with nothing between them stack on
the same fresh page instead of each forcing a separate one. Verified
directly in the regenerated file's XML: no heading paragraph, including
both `Part I` and `Part II`, carries a trailing page-break run anymore.
`Go update`.

2026-10-04: Morgan opened the Joseph manuscript's Word file and found its
long Torah excerpts printed with a literal `>` at the start of each line
-- the tool had never been taught Markdown's block-quote marker, so it
fell through to the plain-paragraph path and kept the characters as
text. "That is confusing and not clear." The fix is the book convention
for a long excerpt: set it off by indentation, not by marks, using Word's
own Quote style so the look can be changed in one place. Upright rather
than the stock style's italic, because some excerpts run to several
paragraphs, and a long run of italic tires the eye.

2026-10-15: a consuming repository rebuilding a chief of staff proposal hit
two things at once. The run was refused for want of `--short-name`,
though `--footer-label` had already replaced the only line that uses it.
And nothing recorded how the last copy had been built, so the session
read the old file's footer text, its header image's hash and its
first-page header to work the four flags out. The short name is now asked
for only when the default footer line needs it, and every document records
its own build for `--rebuild`. The same pass found that the script's own
install of python-docx failed outright on a Python that marks itself
managed by the system (Python Enhancement Proposal (PEP) 668), as a fresh cloud container's does; it now
retries the way the engine's own installer does.

2026-10-17: the very deep check found two faults here. The practice never
reached a session building a Word file: its `applies_to` names only the
script, which drops it from the occasion index, and building a document
edits no script. And its Rule said nothing implies committing the output,
while dated-download-names and the ladder set's generated-docs-in-output,
both from 2026-10-05, say a kept document is committed under its folder's
`output/` with its date in its name. The session chose, under Morgan's
delegation of that day ("Fix the other issues you found including the
checks that never run. Tell me what you decide. I will be offline so don't
wait for me. Approved, act, and Booked."), to set `index_required: true`,
to defer placement and naming to those two rules, and to move the
script's whole procedure from the Rule into `## Detail`, so the Rule says
only what must be true.

2026-11-12: the Account Manager guide, a 28-page document in a consuming
repository, had been built with `--no-section-breaks` since its first
Word file, its recipe saying only that "with breaks, most pages were half
empty." Nobody had asked for that; a session had judged it. Morgan, on
seeing it: "there should be a page-break before each major section ...
It wasn't followed, so you should do a fix to make sure it's followed in
the future." The flag was the opening: the Rule left "a shorter document"
to judgment, and the script took the flag from anyone. So the Rule now
says the breaks go off only on the person's word, and the script refuses
`--no-section-breaks` without `--breaks-off-because` carrying it.

## Install
[`tools/checks/check_create_word_doc.py`](../tools/checks/check_create_word_doc.py) is structural only: it confirms
[`tools/create_word_doc.py`](../tools/create_word_doc.py), where vendored, is syntactically valid
Python, non-trivial in size, and cites this practice. It is SKIPPED, not
failed, in a repo that hasn't vendored the script at all -- that repo may
still be doing every Word export as a hand-built one-off, which this
practice's Rule explicitly allows. It cannot check the Rule's own
behavior -- that a session actually reached for this script instead of
writing a fresh one, that a generated `.docx` was reviewed before being
handed over, or that a hand-built one-off carried a footer at all -- that
is session judgment.

2026-10-05: the first blurbs file built with this script put its first
blurb on page two, leaving the cover with nothing but the logo and the
title. Morgan asked for it to flow on the way the manuscript's cover
does, and in the same message for a tiny copy of the project's logo in
the header of every page but the first, as part of the template rather
than one document's script. Both landed here; so did the inline links,
wrapped list items and HTML comments a first brainstorm-note export
needed, the last of which a consumer had been stripping in its own
wrapper, and `--soft-wraps`, since that note is wrapped at seventy-odd
characters and every wrap came out as a line break.

Same day: Morgan opened the rebuilt Joseph manuscript and Word asked
*"This document contains fields that may refer to other files. Do you
want to update the fields in this document?"* The contents page had
turned on Word's update-fields-on-open setting so that Word would fill in
the page numbers. He asked that a downloaded document never do this. The
setting is gone; the contents list is written finished, as links to the
headings, without page numbers; and the check now fails on any script
that writes the setting.

Same day, later: Morgan opened the Word files and found every bullet
sitting flush against the left margin -- "That looks a bit funny." The
line-up of each item's own wrapped lines was right; only the bullets
were out. He asked for them about half an inch in, in every Word file
and in this practice. `style_list_bullet()` landed here and in the
script, so the next build of every document picks it up.

Same day, evening: Morgan asked for three more defaults. The footer, in
the body's serif face and size, did not stand apart from the text; he
wanted it sans-serif and a touch smaller. The logo in the running header
was "a bit too small", so it went from 0.4 inch to 0.6. And Heading 1, at
Word's stock 14 point against Heading 2's 13, hardly looked like a level
above it; he wanted it bigger, though not as big as the title. All three
went into the script and this Rule, so every document built from it picks
them up.

Same evening: Morgan opened the rebuilt manuscript and found the
contents page "unrecognizable". Every entry was a body-text paragraph --
same weight, 1.3 spacing, chapters set off only by a small indent -- so
forty lines ran down two pages looking like more text. He asked that a
contents page always look like one. The entries now carry Word's contents
styles: Parts bold, chapters indented, single-spaced, with a dot-leader
tab ready for page numbers.

Later the same evening: Morgan asked for 0.75-inch margins on all sides
as the default, in place of an inch. The script's `PAGE_MARGIN` holds the
number, so a builder that lays out its own page -- table widths, say --
reads it from there and moves with it.

Later still: Morgan asked for the contents entries in the same
sans-serif face as the footer, and underlined, "so it's clear it's a
link". Each entry already jumped to its heading; nothing on the page said
so. Both go on Word's TOC 1 and TOC 2 styles, so Update Field keeps them.

2026-10-13: the first document built with this script that was no
manuscript -- a proposal to a company's CEO, with the company's logo in
the header -- came out with four faults: every price read `\$15k`, the
link to the original proposal lost its address, the `#### People` and
`#### Processes` sub-headings printed their hash marks, and the footer
called the proposal a DRAFT BOOK. The logo also skipped page one, which
on a proposal is the letterhead, not a cover. All five were fixed here,
in the script every repository receives, rather than in a wrapper for
that one document.

2026-10-16: on the social media ideas file, the text on every page after
the first sat right under the header's logo -- Word's 0.5-inch header
distance plus a 0.6-inch logo ended about where the 0.75-inch margin
pushed the text, with nothing between them. Morgan asked for "a bit more
space", a small tweak: the logo now starts higher and keeps a 12-point gap
under it. In the same message he asked for the front-page logo at about
60% of its size, as the default for every document. It had already come
down once, from 4.4 inches to 2.6 (2026-10-05), and the 2026-10-13 logo
swap kept that size, since the new image has the old one's shape; 2.6 was
simply still too big. Two builders in one repository each carried their
own 2.6, so the size moved here as `COVER_LOGO_WIDTH` and they read it.

Same day, later: Morgan opened that proposal and asked for four more
defaults. Bullets half an inch in were "far too much for my taste"; a
quarter inch now. The numbered list of four outcomes came out as numbers
typed as text; it is a real Word list now. And the quotes stayed straight
and `--` stayed two hyphens: every Word document gets curly quotes and
real dashes, the dashes chosen by judgment, since `--` between two words
with no spaces is always an em dash.


Later still, 2026-10-13: the dash rules moved into
[`tools/typography.py`](https://github.com/alex137/BestPractice/blob/staging/tools/typography.py), shared with every builder
for an outside reader, and changed with them. `--` is now always an em
dash, spaced or between numbers, and a hyphen between two numbers in a
range is the en dash (Morgan: "the double dashes should always become an
M dash"; [curly-quotes](curly-quotes.md) has the rest).
