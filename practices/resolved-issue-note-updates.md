---
slug:        resolved-issue-note-updates
title:       A resolved 'known issue' note is updated in the same commit that resolves it
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "a commit fixes, closes, or resolves something a document names in prose as a known, open issue"
gates:       []
index_clause: "When a commit fixes a bug, closes a gap, or resolves a limitation that some ..."
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-09-02
approved_by: "Morgan F, 2026-09-02"
source_practice_number: null
---
## Rule
When a commit fixes a bug, closes a gap, or resolves a limitation that some document names in prose as known-and-open ('not yet fixed', 'a real gap', 'currently unsupported'), update that document in the same commit -- mark it resolved with what changed, or remove the stale claim. Never leave a fixed issue described in prose as still open.

## Why
Raised via Precedent's creation pipeline (Stage 1 signal: review-found-defect), promoted at team level, approved by Morgan F on 2026-09-02.

## Story
BestPractice's spec/PHASE5_BRIEF.md named a real bug in prose: 'A known bug, found while writing this brief, not yet fixed' (precedent_candidate.py create's same-day recurrence collision). This deep-check session fixed the bug in tools/precedent_candidate.py, but the brief's own 'not yet fixed' sentence would have kept reading that way indefinitely if the session hadn't gone back to it on purpose -- nothing flags a stale not-yet-fixed claim once the code it describes has actually changed. The same shape recurs with any 'known issue' or 'open gap' note written into a spec, README, or backlog document: the note and the code drift apart the moment one of them moves without the other.

**Moved to `precedent-team-writing` on 2026-09-09**, from `precedent-team-maintainers`, in the subject split recorded at Precedent's `TODO.md#split-team-sets-by-subject`. The rule is about the craft of writing for a human reader, which is nobody's single team's business: a document project needs it as much as a software repo. While it lived in a set named for the people who happened to write it, neither could reach it without also taking twenty-odd rules about syncs, gates and branch setup. The copy left behind is `status: deduplicated` and points here; nothing was deleted and the rule was never out of force for a moment (`spec/MOVING_PRACTICES.md`, land first, deduplicate second).

## Install
No mechanical check yet -- reached via occasion only, per checkable-gets-checked's own standing rule, a real check should still be attempted before this stays null indefinitely.
