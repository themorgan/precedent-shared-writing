---
slug:        no-stale-counts
title:       Don't state a count that will drift -- describe it instead
tier:        on-demand
severity:    default
applies_to:  ["**/*.md"]
occasion:    "writing a sentence that cites an exact, changeable count"
gates:       []
index_clause: "drop a count that will go stale; say \"several\", not the number"
checked_by:  tools/checks/check_no_stale_counts.py
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-08-31
approved_by: "Morgan F, migrated from RepoPersonalPreferences by the private-set migration session"
---
## Rule
Prose that cites an exact count of something that changes over time -- how many rules a document has, how many warnings a lint tool currently reports -- reads precisely today and goes stale the moment that thing changes, with nothing to flag it. When the exact count isn't the point being made, don't state it: rewrite to the qualitative form ("numbered sections" instead of "twenty-nine numbered sections"). Dropping the number outright is usually the right fix, not swapping it for a vaguer-but-still-numeric approximation that will just go stale on a slower clock.

## Detail
This isn't a rule against numbers in general -- a version number, a date, or a count genuinely maintained alongside the thing it counts all stay exact. The target is specifically a count that can change independent of the sentence stating it, where the number isn't actually the point.

A count sitting inside a **closed historical item** -- a `todo/` item already at `status: done` or `status: dropped`, whose prose is written once and never hand-rewritten afterward -- is the first case, not the second: it is the record of what that specific run actually measured, at the time, tied to the event it counts rather than to whatever the repo holds today. Reopening a closed item to keep its own historical sentence current would defeat the point of closing it.

## Why
No audit checks a sentence like "twenty-nine numbered sections" against the actual count, so it just sits there being wrong until a session happens to notice.

## Story
Migrated here from RepoPersonalPreferences by the phase-3 private-set
migration; the Story is backfilled from that pack's own text, and this one
has two concrete instances found on the same day the rule was written.

The first: an entry-point document said "Twenty-nine numbered sections" while
the pack it described already had thirty. Nothing had gone wrong mechanically
-- the sentence was simply true when written and quietly stopped being true,
and no audit compares a sentence like that against the real count, so it sat
there being wrong until somebody happened to notice. The second, written the
same day, was in another rule's own text: "over a hundred" pre-existing lint
warnings, a figure that shifts on nearly every edit to the files it
describes. Both were fixed as part of adding the rule.

That pairing is what makes the rule's shape right. In neither case was the
number the point being made -- both sentences only needed to convey "there
are several" or "a real backlog exists". So the fix is to drop the figure
rather than replace it with a vaguer but still numeric approximation, which
only goes stale on a slower clock.

It is deliberately not a rule against numbers. A version, a date, or a count
genuinely maintained alongside the thing it counts all stay exact. The
target is a count that can change independently of the sentence stating it,
where the number was scene-setting detail that happened to be numeric. That
distinction needs intent to judge, so nothing enforces it mechanically.

**Moved to `precedent-team-writing` on 2026-09-09**, from `precedent-team-maintainers`, in the subject split recorded at BestPractice's own [`split-team-sets-by-subject`](https://github.com/alex137/BestPractice/blob/precedent-beta-v01/todo/todo-2026-09-08-split-team-sets-by-subject.md) item, DONE 2026-09-09. The rule is about the craft of writing for a human reader, which is nobody's single team's business: a document project needs it as much as a software repo. While it lived in a set named for the people who happened to write it, neither could reach it without also taking twenty-odd rules about syncs, gates and branch setup. The copy left behind is `status: deduplicated` and points here; nothing was deleted and the rule was never out of force for a moment (`spec/MOVING_PRACTICES.md`, land first, deduplicate second).

**Carved out closed `todo/` items on 2026-09-20**, found against `themorgan/HavrutaPlanning`: a `status: done` item's own historical prose (`"Materialized <N> practices..."`) stayed true when written and went stale the moment the repo's real count moved on, same as every other instance this rule already covers -- except this one sat inside a record of what a specific past run actually measured, not an ongoing description, and this project's own convention (`todo_migrate.py`'s "written once, rarely touched again" design) never hand-rewrites a closed item's prose to keep it current. The item was parked on two options -- extend this carve-out, or break that convention once and hand-edit the line -- and Morgan picked the carve-out (`todo/todo-2026-09-19-migration-split-defeats-diff-based-checks-and-surfaces-a-stale-count.md`, "Go with A").

## Install
Checked mechanically, but only half of it: [`tools/checks/check_no_stale_counts.py`](../tools/checks/check_no_stale_counts.py), scope `tree`, catches the one shape of violation that needs no writer intent to judge -- a sentence stating "`<N> practices`" is a claim about this repo's own `practices/` directory, and that claim is either currently true or it isn't, independent of intent. It's deliberately narrow: it does not (and, per this file's own Detail section, cannot) tell a "genuinely maintained" count apart from one that merely happens to be accurate today, and it doesn't push toward the Rule's preferred fix of dropping the number outright -- it only catches a count that has already gone stale, which is the concrete harm the Rule names. A general digit-plus-noun scan across arbitrary count types stays a judgment call, for the reason already given.

A closed `todo/` item -- filename `todo/todo-*.md`, frontmatter `status: done` or `status: dropped` -- is excluded from the scan entirely (`_is_closed_todo_item()`), per this file's own Detail section: its prose is a historical record, not an ongoing claim. Narrowed to that filename shape and that frontmatter key on purpose -- `status: done` means something else inside a practice file (retirement), and this exemption is not about those. Two-direction tested in [`tools/checks/tests/test_no_stale_counts.sh`](../tools/checks/tests/test_no_stale_counts.sh).
