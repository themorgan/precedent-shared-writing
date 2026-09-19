---
slug:        branch-links
title:       A mentioned branch is always a link
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "naming a git branch in a document, reply, or status update"
gates:       []
index_clause: "link every git branch mentioned to its tree view"
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-08-31
approved_by: "Morgan F, migrated from RepoPersonalPreferences by the private-set migration session"
---
## Rule
Any time a reply or document names a git branch -- not only in a files-touched footer, but anywhere in running text, a status update, a decision note -- link it, to that branch's tree view on whichever host the repo actually lives on. A bare branch name in backticks or plain prose is the failure mode this rule exists to catch.

## Detail


## Why
A doc-references-are-links convention covers files at the repo's current tree; it doesn't reach a branch, since a branch is a ref rather than a path at the current tree, so it needs its own explicit rule.

## Story
Migrated here from RepoPersonalPreferences by the phase-3 private-set
migration; the Story is backfilled from that pack's own text, which recorded
a gap rather than an incident.

The gap is precise. The universal rule that references in documents are
links covers files at the repo's current tree, and a relative markdown link
is the right form for those. A git branch is not a path at the current tree
-- it is a ref -- so that rule does not reach it, and a bare branch name in
backticks sails past a reader with nothing to click. That is the failure
mode this rule exists to catch, and it is the same failure an unlinked
filename is, one category over.

Hence the extension rather than a new idea: link a branch anywhere it is
named, not only in a files-touched footer, to that branch's tree view on
whichever host the repo actually lives on. A branch in some other repo a
reply happens to mention gets linked on that repo's host, not this one's.

**Moved to `precedent-team-writing` on 2026-09-09**, from `precedent-team-maintainers`, in the subject split recorded at BestPractice's own [`split-team-sets-by-subject`](https://github.com/alex137/BestPractice/blob/precedent-beta-v01/todo/todo-2026-09-08-split-team-sets-by-subject.md) item, DONE 2026-09-09. The rule is about the craft of writing for a human reader, which is nobody's single team's business: a document project needs it as much as a software repo. While it lived in a set named for the people who happened to write it, neither could reach it without also taking twenty-odd rules about syncs, gates and branch setup. The copy left behind is `status: deduplicated` and points here; nothing was deleted and the rule was never out of force for a moment (`spec/MOVING_PRACTICES.md`, land first, deduplicate second).

## Install
No mechanical check: it governs free-form prose (chat replies, status updates, any document) naming a branch, which has no reliable syntactic signature distinguishing "a git branch was named here" from any other backticked or plain-text token (a filename, a variable, a package name). A static scan would either miss real mentions or misfire constantly on lookalikes.
