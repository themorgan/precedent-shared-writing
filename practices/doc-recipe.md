---
slug:        doc-recipe
title:       A recipe holds a file's standing rules, with reasons -- never its history
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "a standing constraint on one file gets stated a second time"
gates:       []
index_clause: "present-tense rules for one file, in doc-recipes/<name>.recipe.md"
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-08-31
approved_by: "Morgan F, migrated from RepoPersonalPreferences by the private-set migration session"
---
## Rule
A recipe is the spec for one file: what the next pass should produce, or how a document is always to be written. It is present tense and rewritable -- the rules in force now, not a record of how they got that way. History belongs where history already lives: `git log`, and a repo's own decision records.

## Detail
Placement and name: recipes live in a `doc-recipes/` subdirectory beside the documents they govern, and each keeps a `.recipe.md` infix (`book/CHAPTER1.md` is governed by `book/doc-recipes/CHAPTER1.recipe.md`) -- the subdirectory so a recipe doesn't double every listing in the directory a reader actually browses, the infix because editor tabs and search results show bare basenames.

Format: a file-header, a title, a `Source:` line when there is one, and a flat list of rules, one per line. A reason rides on the line as an em-dash clause, only where a reader might otherwise delete the rule as arbitrary; where the reason won't compress to a clause, cite the originating commit's short SHA in parentheses instead of retelling it.

`Source:` present means the file is derived (see the derived-file practice) and the recipe says what a regeneration pass should produce; absent means standing constraints on a document written directly, and nothing replaces it -- the rules simply always apply.

When a recipe is created: for a derived file, at the same moment as the file, with no judgment call involved. For a document written directly, never at creation -- a recipe starts the second time the same constraint is restated about that file.

When a recipe is updated: on two triggers -- the output was corrected, or a constraint already stated once was stated again. Adding a line means rereading the whole recipe, pruning contradictions and near-duplicates while it's still short enough to make that cheap; any line a repo-wide convention now covers gets deleted rather than kept as harmless. A rule appearing in a second recipe was never per-file -- promote it to the repo's own conventions and delete it from both. Editing a recipe never triggers a regeneration.

## Why
A running log of "we added X, then softened it, then changed to Y" only grows, is never pruned, and by its tenth entry costs more to read than the document it governs.

## Story
Migrated here from RepoPersonalPreferences by the phase-3 private-set
migration; the Story is backfilled from that pack's own text, and it rests
on a drift that repo had already caught and reversed once.

Its own decision records had turned into essays. A running log of "we added
X, then softened it, then changed to Y" only ever grows, is never pruned,
and by its tenth entry costs more to read than the document it governs. That
is the failure this rule is shaped to avoid repeating one level down, which
is why a recipe is defined as present tense and rewritable -- the rules in
force now -- with history left where history already lives, in `git log` and
in decision records.

Two smaller choices have their own reasons. Recipes sit in a `doc-recipes/`
subdirectory rather than beside the documents they govern, because a recipe
next to its document doubles every listing in the directory a reader
actually browses -- a tax on every read, paid to serve a file opened rarely.
The `.recipe.md` infix is kept even though the directory already implies it,
because editor tabs, search results and `git log --name-only` all show bare
basenames, and two files both displaying as the same name is a daily
confusion. The subdirectory is used from the first recipe onward rather than
adopted at a threshold, since a threshold buys a little tidiness now in
exchange for a migration and a batch of stale references later.

`Source:` is what distinguishes a derived file's recipe from a written
document's, so there is one mechanism rather than two, and a document can
become derived later by gaining that line with no rename and no migration.

**Moved to `precedent-team-writing` on 2026-09-09**, from `precedent-team-maintainers`, in the subject split recorded at BestPractice's own [`split-team-sets-by-subject`](https://github.com/alex137/BestPractice/blob/staging/todo/todo-2026-09-08-split-team-sets-by-subject.md) item, DONE 2026-09-09. The rule is about the craft of writing for a human reader, which is nobody's single team's business: a document project needs it as much as a software repo. While it lived in a set named for the people who happened to write it, neither could reach it without also taking twenty-odd rules about syncs, gates and branch setup. The copy left behind is `status: deduplicated` and points here; nothing was deleted and the rule was never out of force for a moment (`spec/MOVING_PRACTICES.md`, land first, deduplicate second).

## Install
No mechanical check: recognizing that "a standing constraint on one file gets stated a second time" -- the trigger for creating a recipe at all -- requires comparing two pieces of prose for semantic restatement, not syntactic match. Whether an existing recipe's own format (file-header, title, optional `Source:` line, flat rule list) is well-formed is checkable in principle, but the actual judgment this practice turns on -- was this really restated, does a line still belong, has a per-file rule become a repo-wide one -- isn't.
