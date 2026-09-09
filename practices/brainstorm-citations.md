---
slug:        brainstorm-citations
title:       A formal document cites another formal document, never a specific point in the brainstorm
tier:        on-demand
severity:    default
applies_to:  ["**/*.md"]
occasion:    "citing support for a claim in a formal document"
gates:       []
index_clause: "cite a formal document for support, never a raw brainstorm entry"
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-08-31
approved_by: "Morgan F, migrated from RepoPersonalPreferences by the private-set migration session"
---
## Rule
Some repos keep an explicit brainstorm document -- a running, loosely organized dump of raw ideas, explicitly not vetted prose. A formal document -- an essay, a reasons write-up, a rules-in-force checklist, anything meant to state a settled or settling claim -- links another formal document for a substantive point, never a specific entry inside a brainstorm document. If the idea hasn't been promoted into some formal document's own text yet, add it there first, then link there instead.

## Detail
What this doesn't reach: a document's own provenance note ("promoted out of the brainstorm") states a true fact about history, not a citation used as support, and stays fine linking to the brainstorm directly. Linking the brainstorm document itself as an object -- pointing a reader there to browse it -- isn't the pattern this catches either; only a specific interior point cited as justification is.

## Why
Citing a specific brainstorm entry as a claim's own support borrows a credibility the entry never earned -- it's raw material precisely because nobody has argued it through yet.

## Story
Migrated here from RepoPersonalPreferences by the phase-3 private-set
migration. That pack recorded the reasoning rather than a dated incident,
and this Story keeps that distinction rather than manufacturing one.

The rule exists because a general rule of this set has a blind spot here.
`rule-links` says anything mentioned gets a link to its destination -- good
almost everywhere, and wrong for one case. A formal document citing a
specific entry inside a brainstorm as that claim's support borrows
credibility the entry never earned: the entry is raw material precisely
because nobody has argued it through yet, so pointing at it as backing is
citing an idea to itself.

The originating context was a repo that keeps a running brainstorm document
alongside its formal ones, which is the shape the rule assumes. The fix is
deliberately cheap: promote the idea into whichever formal document it fits,
then link there. What the rule does not reach matters as much as what it
does -- a document's own provenance note, or a link to the brainstorm as an
object, states a true fact rather than borrowing support, and stays fine.

**Moved to `precedent-team-writing` on 2026-09-09**, from `precedent-team-maintainers`, in the subject split recorded at Precedent's `TODO.md#split-team-sets-by-subject`. The rule is about the craft of writing for a human reader, which is nobody's single team's business: a document project needs it as much as a software repo. While it lived in a set named for the people who happened to write it, neither could reach it without also taking twenty-odd rules about syncs, gates and branch setup. The copy left behind is `status: deduplicated` and points here; nothing was deleted and the rule was never out of force for a moment (`spec/MOVING_PRACTICES.md`, land first, deduplicate second).

## Install
No mechanical check: catching a violation requires classifying a document as "formal" versus "brainstorm" and telling a citation used as substantive support apart from a provenance note or a link to the brainstorm document as a whole -- both genuinely allowed by the rule's own Detail section. Nothing in a link's syntax carries that distinction; it's a judgment about what the link is doing in context.

