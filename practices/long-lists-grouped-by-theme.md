---
slug:        long-lists-grouped-by-theme
title:       "A long list of semi-related items is grouped by theme, the most important first"
tier:        on-demand
severity:    default
applies_to:  ["**/*.md"]
applies_to_why: "Any document can hold a long list, as with this set's list-restraint and list-item-parity; a project whose tools build long lists adds its own builder and registry paths where it installs this."
occasion:    "writing, building or reviewing a list of more than about a dozen items that are only partly related"
gates:       []
index_clause: "group it into themed sub-lists; themes and items by importance, never A-Z"
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-11-24
approved_by: "Morgan F, 2026-11-24 -- \"long lists of only semi-related things are always confusing. So maybe this should be a practice ... that we should organize long lists into sublists thematically. And usually ordered in each subsection is usually in the order of importance\" (strength: decided); adopted into this set on his go-ahead of the same day, relayed by the session that drafted it: \"You can open that new session with that and update produce there\""
---
## Rule
**A long list of things that are only partly related is split into sub-lists
by theme, so similar items sit together.** A reader looking for one item
scans the theme names, not every line. **The themes go in order of
importance, and so do the items inside each.** Alphabetical order, or the
order the items happened to be found, is never the order.

## Detail
- **"Long" is about a dozen items or more**, or fewer when they cover
  clearly different subjects.
- **A theme is what a reader would look under to find the item**: "Talking
  to Clients", not "Miscellaneous". An item that fits no theme gets a new
  one, not a forced place.
- **A list built by a tool takes its themes from one registry file**, so
  every view of the same entries groups them the same way, and a new entry
  must name its theme before the list will build.
- **Importance** is the entry's weight where it has one (high, medium,
  low), else the writer's judgment of what the reader most needs first.
- **Sub-lists in a document that becomes a Word file use headings that flow
  on** (`###` and below, or a bold line), never a `##` per theme, which
  would start each on a new page.

## Why
A flat list of mixed items makes the reader do the sorting, and they
can't tell which entries belong together or which matter most. Grouping
them once, in the list, does that work for every reader.

## Story
On 2026-11-24 Morgan read a long guide built as a Word file. Its list of
process details put one blog workflow near the top and two closely related
ones far below, after unrelated subjects, and its rules lists ran to dozens
of lines in alphabetical order. He asked for them grouped by subject, for
every future entry to go in the right group, and for the principle to be a
practice.

The session doing that work wrote the practice into its own project's
local set first, so it was in force there at once, and asked for it to
live here. It belongs in this set rather than in that project's because
the failure is about writing for a reader, not about that project's
subject: any document with a long list can make it. It sits beside
[list-restraint](list-restraint.md), which asks whether content is a list
at all, and [list-item-parity](list-item-parity.md), which keeps a list's
items comparable in length; this one says how a long list is ordered.
Adopted here the same day, keeping that project's Rule, Detail and Why,
with its registry example made generic.

## Install
No mechanical check for documents in general: whether a list's items are
"only partly related" is a judgment. A project whose tools build long lists
can enforce the registry half itself, with a builder that refuses an entry
whose theme is not in the registry.
