---
slug:        trim-prose
title:       Trim iteratively-edited prose on two state-free triggers
tier:        on-demand
severity:    default
applies_to:  ["**/*.md"]
occasion:    "a paragraph just got a substantial edit, or the piece is done"
gates:       []
index_clause: "trim a paragraph right after editing it, and before calling it done"
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-08-31
approved_by: "Morgan F, migrated from RepoPersonalPreferences by the private-set migration session"
---
## Rule
Prose revised repeatedly in the same conversation tends to only grow -- each pass adds a clause without removing what the new wording made redundant. Fix it with two cheap, state-free triggers rather than a running count: trim a paragraph immediately after any substantial edit to it (a rewritten sentence, or roughly a sentence or more added), and give the whole piece a final trim pass before calling it done, independent of edit size, for any paragraph that's grown noticeably longer than the point it's making warrants.

## Detail


## Why
Both triggers fire at a checkpoint that already exists -- making an edit, declaring the piece finished -- rather than a mechanical count needing counters or stored baselines.

## Story
Migrated here from RepoPersonalPreferences by the phase-3 private-set
migration. No dated incident was recorded; the rule names a drift, and the
interesting part is the mechanism it rejected.

The drift is that prose tweaked repeatedly in one conversation only grows:
each pass adds a clause or qualifier without anyone removing what the new
wording made redundant, and the result is a paragraph several times its
original length carrying the same point plus a pile of overlapping caveats.

The rejected fix is a running count -- edits since the last trim, or current
length against an earlier baseline. That needs state persisted across edits
and often across sessions, which is a cost out of all proportion to a minor
writing problem. So both triggers are deliberately state-free and fire at
checkpoints that already exist: making a substantial edit, where the
paragraph is already open and being reworked, and declaring the piece done.

The second trigger is not redundant with the first. It exists to catch slow
drift from a run of edits each too small on its own to fire the immediate
one -- which is the way a paragraph usually gets long.

**Moved to `precedent-team-writing` on 2026-09-09**, from `precedent-team-maintainers`, in the subject split recorded at BestPractice's own [`split-team-sets-by-subject`](https://github.com/alex137/BestPractice/blob/precedent-beta-v01/todo/todo-2026-09-08-split-team-sets-by-subject.md) item, DONE 2026-09-09. The rule is about the craft of writing for a human reader, which is nobody's single team's business: a document project needs it as much as a software repo. While it lived in a set named for the people who happened to write it, neither could reach it without also taking twenty-odd rules about syncs, gates and branch setup. The copy left behind is `status: deduplicated` and points here; nothing was deleted and the rule was never out of force for a moment (`spec/MOVING_PRACTICES.md`, land first, deduplicate second).

## Install
No mechanical check: whether a paragraph has "grown noticeably longer than the point it's making warrants" is a judgment about proportion between content and substance -- word or sentence count alone can't distinguish a legitimately long, dense point from one padded by iterative edits, so a length-based trigger would flag exactly the paragraphs this rule doesn't target as often as the ones it does.
