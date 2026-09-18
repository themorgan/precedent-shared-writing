---
slug:        curly-quotes
title:       Outward-facing prose uses curly quotes, never straight ones
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "writing or pasting text into any document under a repo's declared output_paths"
gates:       []
index_clause: "a straight \" or ' in outward-facing prose becomes a typographic curly quote"
checked_by:  tools/checks/check_curly_quotes.py
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-09-18
approved_by: "Morgan F, 2026-09-18, via Go Update -- moved here from themorgan/HavrutaBrainstorm's repo-local set, generalized from a hardcoded directory list to a repo's own declared output_paths"
strength:    decided
---
## Rule
A straight quotation mark (`"`) or straight apostrophe/single quote (`'`)
never appears in the prose of a document under a repo's own declared
`output_paths` (`precedent.json`) -- the same boundary
`deliverables-carry-no-process` already reads, so "outward" never drifts
between the two rules. Convert it to the matching typographic curly form
-- `"` / `"` for double quotes, `'` / `'` for a single quote or an
apostrophe -- the same conversion already applied when incorporating
pasted text under `fix-typos-keep-ambiguity`, where that practice is in
force.

## Detail
- Applies to prose, not to code: a straight quote inside a fenced or
  inline code span, a URL, or a file path is exactly what it should be --
  this rule is about the words a reader reads, not about literal strings.
- A straight quote inside a directly quoted source that itself used
  straight quotes (a court filing, a statute, program output) stays as
  quoted -- fidelity to the source wins there, the same exception
  `no-invented-specifics` and `quote-discipline` already carve out for
  exact figures and wording.
- **The backlog is the consuming repo's own, never this set's.** A repo
  adopting this practice for the first time is very likely to find its
  entire existing outward-facing corpus predates the convention -- this
  is a large pre-existing-content problem, not a new-content-only rule
  invented to dodge it. That repo declares its own `curly_quotes_
  grandfathered` list in its `precedent.json` (an array of paths, exactly
  like `output_paths`/`internal_paths`), and the check below skips every
  path on it. A path drops off that list the day someone actually
  converts it, per `no-rewrite-for-warnings` -- the backlog shrinks by
  real cleanup, never by editing the exemption list to match new
  violations.

## Why
Untidy typography is one of the cheapest "reads like it wasn't cared for"
signals a reader hits, and it is entirely mechanical to avoid -- there is
never a reason to leave a straight quote in finished prose once a
project's own house style has settled on curly quotes. Making it a
standing rule means every future paste or draft gets the conversion by
default, instead of a session having to notice and fix it by eye each
time.

## Story
Raised by Morgan, 2026-09-18, in `themorgan/HavrutaBrainstorm`, in the
same thread that produced `hebrew-term-parenthetical` and `fix-typos-
keep-ambiguity`, asking for a third standing practice specifically about
converting straight quotes to curly ones. Writing the mechanical check
per `checkable-gets-checked` surfaced that essentially the entire
existing outward-facing corpus predated the convention -- all 23 outward
files that repo had at the time carried at least one straight quote in
prose scope -- so the check was wired in with that full list
grandfathered rather than left `checked_by: null` or shipped in a form
that would fail every future push until someone did an unplanned,
unscoped rewrite of the whole cluster.

Same day: Morgan asked whether `book-joseph/MANUSCRIPT.md` -- the file
the practice's own Why section pointed to as the house style's own
example -- had actually been converted. It hadn't: it was sitting on the
grandfather list from the initial audit, unconverted, and the Word export
(`create-word-doc`) was faithfully carrying the straight quotes through
from source, which is what surfaced the gap. Converted (19 straight-
double-quote pairs, all self-contained with no nesting; no straight
apostrophes were present) and dropped from the list.

**Moved to `precedent-team-writing` on 2026-09-18**, from
`themorgan/HavrutaBrainstorm`'s repo-local set, alongside `create-word-
doc` in the same reconsideration: the rule is about the craft of writing
for a reader, not about that repo's subject. The move required real
generalization, not a copy -- the original check imported that repo's
own `tools/title_case.py` for its outward-file boundary and hardcoded its
23-file grandfather list; both are repo-specific and cannot travel as
team content. The boundary is now the `output_paths`/`internal_paths`
`deliverables-carry-no-process` already reads generically, and the
grandfather list is now a repo-declared `precedent.json` key the
consuming repo owns. `Go update`.

## Install
Checked by [`tools/checks/check_curly_quotes.py`](../tools/checks/check_curly_quotes.py):
reads the consuming repo's own declared `output_paths` / `internal_paths`
and `curly_quotes_grandfathered` from its `precedent.json`, strips fenced
code, inline code, link targets and autolinks first, and flags a
remaining straight `"` or `'` in any in-scope, non-grandfathered tracked
markdown file. SKIPPED (not a pass, not a violation) when the repo
declares no `output_paths` at all, or when `output_paths` is declared but
nothing tracked was actually in scope -- an empty scan is not a clean
one. Exit 0 and no output when clean (including "clean because every
current violation is grandfathered"); exit 1 naming the file and count
otherwise.
