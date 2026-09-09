---
slug:        content-subdirs
title:       Content-oriented repos group deliverable content in a subdirectory
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "root has accumulated three or more deliverable-content documents"
gates:       []
index_clause: "group deliverable content under a named subdirectory -- a recommendation"
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-08-31
approved_by: "Morgan F, migrated from RepoPersonalPreferences by the private-set migration session"
---
## Rule
In a content-oriented repo -- one whose deliverable is the writing itself, not software that runs -- once root accumulates three or more documents that are deliverable content rather than navigation, consider grouping that content under one or more named subdirectories (say `book/` and `brainstorm/`), while the navigation layer (a map, a glossary, a backlog document, a README, `AGENTS.md`, a getting-started guide) stays at root.

## Detail
A code-oriented repo doesn't get this recommendation at all -- its root-level clutter, if any, is a different problem with its own existing conventions. Not mechanically enforced, and not retroactive: raise it as a judgment call when a session actually notices root cluttered with deliverable content, never as a reason to force a restructure on its own.

## Why
Left alone, both kinds of root-level file pile up together, and enough deliverable content reads as cluttered even when the navigation layer is doing exactly what it should.

## Story
Migrated here from RepoPersonalPreferences by the phase-3 private-set
migration; the Story is backfilled from that pack's own text.

It was noticed in a real dependent repo, named here only in general terms
because this practice text ships into consuming repos (`private-repo-scrub`).
That repo's root had accumulated two different kinds of file at once: the
navigation layer that helps a reader find things, and the deliverable
writing itself. Left alone both pile up together, and enough of the second
kind reads as clutter even while the first is doing exactly its job. The fix
there was to group the manuscript and its supporting raw notes each into
their own named subdirectory while the navigation layer stayed at root.

Two limits came with it deliberately. It does not reach a code-oriented
repo, whose root clutter is a different problem with its own long-standing
idioms this set has nothing to add to. And it is not retroactive on its own:
a restructure means updating every relative link into the moved files, which
is real work with real link-churn, worth doing when somebody decides to do
it and not merely because a rule now exists.

It is also the one advisory rule in this group. Nothing checks it, and that
is on purpose -- it was written down mainly so a session would stop reading
root-level content clutter as an install-time defect the way a missing
manifest entry genuinely is.

**Moved to `precedent-team-writing` on 2026-09-09**, from `precedent-team-maintainers`, in the subject split recorded at Precedent's `TODO.md#split-team-sets-by-subject`. The rule is about the craft of writing for a human reader, which is nobody's single team's business: a document project needs it as much as a software repo. While it lived in a set named for the people who happened to write it, neither could reach it without also taking twenty-odd rules about syncs, gates and branch setup. The copy left behind is `status: deduplicated` and points here; nothing was deleted and the rule was never out of force for a moment (`spec/MOVING_PRACTICES.md`, land first, deduplicate second).

## Install
No mechanical check, and the practice says so itself: its own Detail section states it's "not mechanically enforced... raise it as a judgment call when a session actually notices," since telling deliverable content apart from navigation-layer files (and deciding whether root genuinely reads as cluttered) is exactly that kind of call.

