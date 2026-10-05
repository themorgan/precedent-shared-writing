---
slug:        create-word-doc
title:       Every Word (.docx) document built for a reader carries a footer -- a structured export runs tools/create_word_doc.py (footer, section page breaks, A4, 1.3 line spacing, live word count, indented block quotations all included); anything else still needs the same Page X of Y + title/date footer built into whatever script makes it
tier:        on-demand
severity:    default
applies_to:  ["tools/create_word_doc.py"]
occasion:    "producing any Word (.docx) document for someone to download -- a structured export (a manuscript, a report) or an ad hoc one-off built from a business note or brainstorm doc"
gates:       []
index_clause: "a Word file for a reader: a footer, and it opens without an update-fields prompt"
checked_by:  tools/checks/check_create_word_doc.py
ships:       ["tools/create_word_doc.py"]
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-09-18
approved_by: "Morgan F, 2026-09-18, via Go Update -- moved here from a private repo-local set, generalized from a book-*/MANUSCRIPT.md-specific rule to any structured-document export; revised again 2026-09-18, Morgan F, via Go Update, to switch the chapter-break mechanism from a heading paragraph property to an explicit page-break run in the preceding paragraph; revised a third time same day, Morgan F, via Go Update, to skip the break when a heading has no body of its own before the next heading (found via Part II, verified on Microsoft (MS) Word desktop macOS 16.78.3); revised 2026-10-04 at Morgan F's own request, to set a \"> \" block as an indented block quotation rather than printing the markers; revised 2026-10-05 at Morgan F's own request, so a downloaded document never asks to update its fields when it opens; revised 2026-10-05 at Morgan F's own request, so a heading straight after the title shares its page, with an optional running header image on every page but the first; revised 2026-09-26, Morgan F, \"Go ahead on shared writing\" (strength: assented), to declare the script in ships: so it travels with the practice instead of being copied in by hand"
---
## Rule
**Any Word document built for someone to download carries a footer --
not just a structured, multi-section export.** Two paths, one
requirement:

- **A structured export** -- a manuscript, a long report, anything with
  real chapter/section headings -- runs `tools/create_word_doc.py` rather
  than a one-off conversion script; see below for what it includes in the
  same pass.
- **Anything else** -- a one-off built from a business note, a
  brainstorm doc, or any other unstructured source -- has no shared tool
  yet, so the footer is built by hand into whatever script generates the
  `.docx` (the same way the first structured export was, before it became
  `tools/create_word_doc.py`). It still needs both pieces the structured
  export's footer has: a live "Page `<n>` of `<total>`" field, and a
  second line naming the document and the date (`<TITLE> - <date>`).
  "CONFIDENTIAL - DRAFT" is a reasonable prefix for anything drawn from
  proprietary material, but the structured export's own "DRAFT BOOK"
  wording (below) is that use case's own convention and doesn't transfer
  as-is. With `docx-js` (Node), that's a `Footer` on the section, with
  `PageNumber.CURRENT`/`PageNumber.TOTAL_PAGES` inside a `TextRun`'s
  `children` for the live fields -- simpler than `python-docx`'s manual
  `w:fldChar` Office Open XML (OOXML) (`add_field()` in
  `tools/create_word_doc.py` is that lower-level approach, for when
  `python-docx` is the tool already in use).

`tools/create_word_doc.py` builds the `.docx` (real Title/Heading 1/
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

`<n>`/`<total>` are live Word PAGE/NUMPAGES fields, not a computed
count, so they stay correct after Word repaginates. `<SHORT NAME>`
defaults to a `book-*/` ancestor directory's name (this tool's own
manuscript-export convention -- `book-example` -> `Example`) with `--short-
name` required whenever the source isn't under a `book-*/` directory or
that mechanical derivation isn't what's wanted. The date defaults to
today via `tools/precedent_time.py` (practice: timestamps-carry-offset)
-- a bare `date.today()` would silently stamp the container's UTC date,
which is wrong for part of every day.

**Every `##` and `###` heading starts on a fresh page** -- a page break
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
altogether, for a shorter document -- notes, a brainstorm -- whose
sections are better read flowing on than one to a page.

**A running header is optional: `--header-image PATH`**
(`header_image=` to `build_doc()`). It puts a small copy of the image --
a logo, 0.4 inch tall -- centered in the header of every page but the
first, which carries the cover and so gets Word's "different first page"
with an empty header and a copy of the footer (without the copy, page one
would lose its "Page X of Y"). A Word document built by hand gets the
same header from `add_header_image(section, path)`, called once its
footer is written.

**Page is A4, default line spacing is 1.3x**, set once on the `Normal`
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

**A contents page is optional: `--contents`** (`contents=True` to
`build_doc()`; off by default). It puts Word's own table of contents on a
page of its own before the first Part -- a "Contents" line in Word's
table of contents (TOC) heading style, **TOC Heading**, which stays out of the contents and the Navigation
Pane, then a table-of-contents field listing the Parts and chapters
(Heading 1 and 2).
The field is written already filled in: each title is a link that jumps
to its heading. It carries no page numbers, since only Word knows where
its pages break and the file must not ask Word to work them out on
opening (below); a reader who wants them right-clicks the list and picks
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

The generated `.docx` is a deliverable, not a source file: the script
never writes into the repo, and nothing about this practice implies
committing the output.

## Detail
The parser handles a working subset of Markdown: `#`/`##`/`###` headings
(even when not followed by a blank line -- some manuscripts' own section
headers have none, and an earlier draft of this script merged the
heading into the following paragraph and leaked the `#` characters into
the body text as a result), `**bold**` and `*italic*` inline spans, `[links](...)` printed as their
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
`tools/create_word_doc.py` on its next sync, alongside the check and its
test, and never copies it by hand. A repository that only ever needs the ad
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
`book-*/MANUSCRIPT.md` path or `tools/create_word_doc.py` itself, so it
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

## Install
`tools/checks/check_create_word_doc.py` is structural only: it confirms
`tools/create_word_doc.py`, where vendored, is syntactically valid
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
