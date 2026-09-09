---
slug:        durable-list-anchors
title:       A durable numbered list gets a permanent slug and anchor per entry
tier:        on-demand
severity:    default
applies_to:  ["**/*.md"]
occasion:    "a numbered list's entries are durable content likely to be cited by position"
gates:       []
index_clause: "anchor and slug each entry of a durable numbered list, not just its number"
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-08-31
approved_by: "Morgan F, migrated from RepoPersonalPreferences by the private-set migration session"
---
## Rule
A numbered list whose entries hold real, durable content -- standing rules, named ideas, arguments meant to last -- likely to be cited elsewhere as "item N" or "rule N," gets the same treatment a rules document's own rules get: each entry an `<a id="slug"></a>` anchor, every citation using the slug form, the visible number left as pure reading-order furniture nobody actually cites.

## Detail
Doesn't reach a short bullet list -- three or four quick options, a set of open questions -- that nothing outside it is likely to reference by position. Stops at the edge of anything vendored: a numbered list inside a tree that must stay byte-identical to its upstream source is not ours to renumber or re-anchor; cite it by its own file-qualified form instead (`SOMEFILE.md §17`) and raise any real need for slugs upstream. Even a list that already uses real headings needs an explicit anchor -- a host's auto-generated heading anchor bakes the visible number into the slug, so it still breaks on renumbering without one.

## Why
Position-only numbering makes every future insertion a choice between distorting the list's own logical order or paying for a repo-wide citation sweep; a slug removes that choice entirely.

## Story
Migrated here from RepoPersonalPreferences by the phase-3 private-set
migration; the Story is backfilled from that pack's own text, and the
incident behind it is a good one because the damage was invisible.

In a dependent repo -- named in general terms here, since this text ships
into consuming repos (`private-repo-scrub`) -- a session had a new idea to
add to a numbered list and folded it into an existing item as an awkward
corollary instead of inserting it where it belonged. The reason was
mechanical, not editorial: a plain insertion would have forced a sweep
renumbering every "item N" cross-reference pointing past it, so the session
distorted the list's own logical order to avoid paying for the sweep.

That is the failure worth naming, because nothing about the result looks
broken. The list still reads, the cross-references still resolve, and only
the shape of the argument quietly got worse. Position-only numbering makes
every future insertion a choice between distorting the order and paying a
renumbering cost, and sessions will keep choosing the cheap side.

A slugged list has nothing to renumber: insert the entry where it actually
belongs and every existing citation keeps working untouched. A list that
already uses real headings still needs the anchor explicitly, because the
host's auto-generated anchor bakes the number into the slug and so breaks on
renumbering anyway.

The rule deliberately stops at the edge of anything vendored. A numbered
list inside a vendored tree is not ours to renumber or re-anchor -- that
tree has to stay byte-identical to what its sync mirrored, so a local anchor
is just a merge conflict on the next sync.

**Moved to `precedent-team-writing` on 2026-09-09**, from `precedent-team-maintainers`, in the subject split recorded at Precedent's `TODO.md#split-team-sets-by-subject`. The rule is about the craft of writing for a human reader, which is nobody's single team's business: a document project needs it as much as a software repo. While it lived in a set named for the people who happened to write it, neither could reach it without also taking twenty-odd rules about syncs, gates and branch setup. The copy left behind is `status: deduplicated` and points here; nothing was deleted and the rule was never out of force for a moment (`spec/MOVING_PRACTICES.md`, land first, deduplicate second).

## Install
No mechanical check: whether a given numbered list holds "durable content likely to be cited by position" versus a short, disposable set of options is exactly the judgment the rule turns on, and the Detail section's own carve-outs (a short bullet list; a list vendored byte-identical from upstream) need the same judgment to apply correctly. A check that flagged every unanchored numbered list would misfire on most of them.

