---
slug:        create-word-doc
title:       Every Word (.docx) document built for a reader carries a footer -- a structured export runs tools/create_word_doc.py (footer, section page breaks, A4, 1.3 line spacing, live word count all included); anything else still needs the same Page X of Y + title/date footer built into whatever script makes it
tier:        on-demand
severity:    default
applies_to:  ["tools/create_word_doc.py"]
occasion:    "producing any Word (.docx) document for someone to download -- a structured export (a manuscript, a report) or an ad hoc one-off built from a business note or brainstorm doc"
gates:       []
index_clause: "creating any Word (.docx) document means it carries a footer -- a structured export runs tools/create_word_doc.py (A4, 1.3 line spacing, footer, section page breaks, live word count, all in the same pass); anything else still needs a live Page X of Y footer plus a title/date line, built by hand into whatever script makes it"
checked_by:  tools/checks/check_create_word_doc.py
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-09-18
approved_by: "Morgan F, 2026-09-18, via Go Update -- moved here from themorgan/HavrutaBrainstorm's repo-local set, generalized from a book-*/MANUSCRIPT.md-specific rule to any structured-document export; revised again 2026-09-18, Morgan F, via Go Update, to switch the chapter-break mechanism from a heading paragraph property to an explicit page-break run in the preceding paragraph"
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
manuscript-export convention -- `book-joseph` -> `Joseph`) with `--short-
name` required whenever the source isn't under a `book-*/` directory or
that mechanical derivation isn't what's wanted. The date defaults to
today via `tools/precedent_time.py` (practice: timestamps-carry-offset)
-- a bare `date.today()` would silently stamp the container's UTC date,
which is wrong for part of every day.

**Every `##` and `###` heading starts on a fresh page** -- a page break
before the heading, not after whatever came before it, so a section that
ends mid-page never runs its last paragraph into the next section's
title. The title page is the one exception: it opens the document, so
nothing needs to break before it.

**Page is A4, default line spacing is 1.3x**, set once on the `Normal`
style and the section's page size rather than per paragraph, so every
paragraph inherits both without the parser having to know about them.

**A `Words: <count>` line in the source becomes a live Word `NUMWORDS`
field**, the same mechanism as the footer's page count, and any trailing
parenthetical after it (`(PART 1)`, or anything else) is dropped. A
number typed once into a source document is exactly the kind of count
that goes stale the moment the text changes; the field recalculates
instead of needing someone to notice and retype it.

The generated `.docx` is a deliverable, not a source file: the script
never writes into the repo, and nothing about this practice implies
committing the output.

## Detail
The parser handles a working subset of Markdown: `#`/`##`/`###` headings
(even when not followed by a blank line -- some manuscripts' own section
headers have none, and an earlier draft of this script merged the
heading into the following paragraph and leaked the `#` characters into
the body text as a result), `**bold**` and `*italic*` inline spans, `- `
bullet blocks, and multi-line blocks such as a lyrics or verse excerpt,
where each physical line becomes a hard line-break within one paragraph
rather than its own paragraph.

python-docx, not a Node/docx-js script, so the tool matches a repo whose
`tools/` is otherwise all-Python -- and, incidentally, python-docx's
stock template already defines a proper `Normal` style, sidestepping a
real bug an earlier docx-js draft of this script hit: a missing explicit
`Normal` style definition (legal per the OOXML spec, since real Word
falls back to document defaults) that made `python-docx` and `pandoc`'s
own docx reader return `None` for every paragraph's resolved style.

**Vendoring:** like the rest of a team source's `tools/`, this script
travels by copy, not by materialization -- `precedent_materialize.py`
copies a source's `practices/` and `tools/checks/`, never an arbitrary
tool script (see its own docstring). A consuming repo that wants the
structured-export half of this practice copies `tools/create_word_doc.py`
in by hand, the same way it already vendors the engine scripts
(INSTALL.md's existing model); a repo that only ever needs the ad hoc,
built-by-hand half doesn't need the file at all, and the check below
skips cleanly when it's absent.

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
2026-09-18, in `themorgan/HavrutaBrainstorm`: first Word export of
`book-joseph/MANUSCRIPT.md`, done as a one-off script in a session
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
`themorgan/HavrutaBrainstorm`'s repo-local set, on Morgan's own
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
itself. The break now physically lives in a different, earlier
paragraph -- it cannot be misattributed to landing after the heading's
own text, because it is not in that paragraph at all. `Go update`. Not
independently confirmed as the actual root cause of what Morgan saw
(the failure was never reproduced outside his own rendering), but it is
the standard, most broadly compatible technique for this in
`python-docx`, and removes the ambiguity either way.

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
