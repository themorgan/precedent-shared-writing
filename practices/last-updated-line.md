---
slug:        last-updated-line
title:       A document's "last updated" line moves with every change a reader can see, silently
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "No locus: any document may carry such a line, in any folder and any format, and nothing about the path says which do. Reached through the occasion index."
occasion:    "changing a document that carries a 'last updated' line"
gates:       []
index_clause: "set it to now, in the reader's zone, before any rebuild; never mention it"
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-11-11
approved_by: "Morgan F, 2026-11-11, in his words: \"every time you update the guide, update the timestamp (and you don't need to tell me you did it, just do it)\", then, asked whether it should be a rule for every document with such a line: \"yes, but do that in a different session and booked and produce that in that session.\" (strength: decided)"
---
## Rule
**When a document carries a "last updated" line, every change to what a
reader sees sets that line to the current time**, whatever its wording:
"Date last updated", "Last updated", "Updated". The time is the person's
own, with the zone named -- for Morgan, Buenos Aires:
`Last updated: 2026-11-11 20:09 (Buenos Aires time)`.

**Read the clock; never invent a time.** Take it from
[`tools/precedent_time.py`](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_time.py), never from the container's clock or
from memory.

**Do it before anything is rebuilt from the document** -- a Word file, a
PDF -- so the copy a reader gets carries the same time as its source.

**Do it silently.** The reply never says the line was updated; the person
assumes it, and saying so is noise.

## Detail
**What moves it:** any change a reader would notice -- a word, a heading, a
table cell, a link. **What doesn't:** whitespace, a comment, a reflowed line,
anything that renders the same. A change that moves nothing a reader sees
leaves the time alone, so the line stays honest about when the content last
changed.

**Keep the line's own form.** Change only the date and time; its label,
place and layout stay as the document had them. Where it carries a date
alone, write the date alone.

**What this is not:** the hidden `<!-- Last updated ... -->` comment some
repositories require at the top of a file. That one never renders, follows
its own repository's file-header rule, and is not what a reader sees
([deliverables-carry-no-process](deliverables-carry-no-process.md) explains why it may stay
in a deliverable).

## Why
A reader trusts the line to say how fresh the document is. A line left
behind after an edit tells them the document is older than it is, and one
moved by a whitespace fix tells them something changed when nothing did.
Updating it is routine housekeeping, so mentioning it costs the reader a
sentence that changes nothing for them.

## Story
2026-11-11: a consuming repository's guide had a per-file recipe line
saying the guide's "Date last updated" moves on every update. Morgan said,
working on that guide, "every time you update the guide, update the
timestamp (and you don't need to tell me you did it, just do it)", then
agreed the rule should cover every document that carries such a line, not
that guide alone. It lives here, in the writing set, so every repository
that declares the set gets it.

## Install
No mechanical check: whether a change is one a reader sees, and whether
the time written is the time it was made, are judgments about a specific
edit. A check could find a stale line only by guessing which commit changed
content, and would flag every whitespace fix.
