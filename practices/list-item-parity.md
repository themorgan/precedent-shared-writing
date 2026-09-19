---
slug:        list-item-parity
title:       Cocreated list items stay roughly comparable in length -- default short
tier:        on-demand
severity:    default
applies_to:  ["**/*.md"]
occasion:    "drafting or revising a list, or a document with list-like sections"
gates:       []
index_clause: "keep list items comparable in length; default to the shorter side"
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-08-31
approved_by: "Morgan F, migrated from RepoPersonalPreferences by the private-set migration session"
---
## Rule
When cowriting a list, or a document with several short-ish sections in a row that function like one, keep each item to approximately the same length as its neighbors. Default to the shorter side for list items unless explicitly told otherwise.

## Detail
This matters most during revision: it's natural to edit one point, expand it while already in there, and leave the others untouched, even though nothing about that item's actual importance grew. If one item genuinely carries more weight, that's a signal to pull it out into its own section, not a license to let it balloon in place. Watch for this both when a list is first drafted and every time an existing item gets revised. This is a strong preference, not a hard rule -- a list can be genuinely uneven in what its items need to say.

## Why
Left unwatched, the list ends up looking like it ranks items by how recently someone touched them rather than by what they're worth.

## Story
Migrated here from RepoPersonalPreferences by the phase-3 private-set
migration. That pack recorded a failure mode rather than a dated incident,
and this Story keeps that distinction.

The failure is specifically about revision, not drafting. It is natural to
edit one item in a list, expand it while you are in there, and leave its
neighbors untouched -- even though nothing about that item's actual
importance grew relative to the rest. Left unwatched the list ends up
ranking its items by how recently someone touched them, which is why the
rule says to watch at both ends and names the revision end as the one that
actually bites.

The escape hatch is deliberate: an item that genuinely carries more weight
is a signal to pull it out into its own section, not a licence to let it
balloon in place. And it is a strong preference rather than a hard rule,
because padding a short item to match its neighbors makes it worse.

**Moved to `precedent-team-writing` on 2026-09-09**, from `precedent-team-maintainers`, in the subject split BestPractice recorded as its own `split-team-sets-by-subject` item, DONE 2026-09-09 -- that item did not survive BestPractice's own 2026-09-16 todo/gotcha migration (no `todo/` archive file, no row in `spec/TODO_GOTCHA_MIGRATION_MAP.md`), so there is no anchor left to cite. The rule is about the craft of writing for a human reader, which is nobody's single team's business: a document project needs it as much as a software repo. While it lived in a set named for the people who happened to write it, neither could reach it without also taking twenty-odd rules about syncs, gates and branch setup. The copy left behind is `status: deduplicated` and points here; nothing was deleted and the rule was never out of force for a moment (`spec/MOVING_PRACTICES.md`, land first, deduplicate second).

## Install
No mechanical check: "roughly comparable length" is deliberately not a fixed ratio (the rule's own Detail section calls it "a strong preference, not a hard rule"), and whether one item's extra length reflects genuinely greater weight or just drafting mood is a judgment about the content, not something a length comparison alone can settle without flagging plenty of legitimately uneven lists.
