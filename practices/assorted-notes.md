---
slug:        assorted-notes
title:       "Deduplicated: assorted-notes is the ladder set's assorted-notes-is-deleted, which is stricter"
tier:        on-demand
severity:    advisory
applies_to:  []
applies_to_why: "DEDUPLICATED 2026-11-18 -- the ladder set's assorted-notes-is-deleted is the rule, and supersedes this one. Kept so links to assorted-notes.md resolve, and so a repository that declares this set but not the ladder set still keeps a strict copy in force until the ladder set arrives."
occasion:    "starting a catch-all notes file, or renaming a legacy BRAINSTORM, NOTES or IDEAS file"
gates:       []
index_clause: "deduplicated 2026-11-18; the ladder set's assorted-notes-is-deleted, stricter"
checked_by:  null
defines:     []
status:      deduplicated
in_force_at: assorted-notes-is-deleted
supersedes:  []
overrides:   null
added:       "2026-10-05"
approved_by: "Morgan F, 2026-10-05, moved from the shared set precedent-shared-working-style (there: Morgan F, 2026-09-23, moved from the individual set precedent-individual (there: Morgan F, 2026-09-04; revised 2026-09-05, Morgan F, to exempt plain directory-listing links, then again the same day to exempt any See also section)). Deduplicated: Morgan F, 2026-11-18: \"I think we should deprecate the older rule and keep the new one. We should be strict but also this isn't just for 'writing' but generally about how I work.\""
strength: decided
source_practice_number: null
---
## Rule
**Deduplicated.** The rule is the ladder set's `assorted-notes-is-deleted`
(precedent-shared-ladder), which supersedes this one; read that. Where it
has not arrived yet, this copy binds as it says: a repo keeps one
`ASSORTED_NOTES.md`, renaming a legacy `BRAINSTORM.md`, `NOTES.md` or
`IDEAS.md` to it; what is in it counts as deleted; and only a `README.md`
or `MAP.md` may link it -- not a `## See also` section, not a link naming
the file.

## Detail
This copy used to allow a link from any `## See also` section and a link
whose text was the file's own name. Both are gone: they are how a cut item
came back onto the page it left. Its check, `check_assorted_notes.py`,
went to the ladder set as `check_assorted_notes_is_deleted.py`, strict.

## Why
Two rules about one file disagreed, and a session followed the weaker
one's check. One rule, one check.

## Story
2026-11-18: deduplicated to the ladder set's `assorted-notes-is-deleted`
(approved by Morgan F). In a planning repository a session had moved links
to the notes file into See also sections because this set's check passed
them there, while the ladder set's new rule said nothing links it. Morgan:
"I think we should deprecate the older rule and keep the new one. We
should be strict." The filename and renaming parts moved there; the check
moved there without its See also and names-the-file exemptions, and was
removed here.

2026-09-29: the `content/` default went with `content-directory`, retired that day for [organize-scattered-content](https://github.com/alex137/BestPractice/blob/staging/practices/organize-scattered-content.md). The filename rule stands on its own; where the file lives now follows wherever the repo keeps its content.

2026-09-05, working in a dependent content repo: a session read the Rule as written -- "nothing anywhere else... may reference or link to" -- literally, and de-linked `content/ASSORTED_NOTES.md` even from that repo's own root `README.md`, `content/README.md`, and `MAP.md`, files whose entire purpose is inventorying what's in the repo. Caught and corrected the same session: "I know I said don't [link] to ASSORTED_NOTES but an exception to that is, in 'lists of files', it's still there to be examined if people want -- I just meant the ideas within it aren't yet ready to be referenced elsewhere." Revised here at the source rather than as a repo-local override, since the distinction (citation vs. listing) is true of every repo this practice reaches, not particular to that one.

2026-09-07, the directory half: a consuming repo renamed `content/` to `business-modeling/`, so that every content directory it had said what it held. Its `ASSORTED_NOTES.md` moved with the rename, intact -- and the check, which tested one literal path, concluded the legacy-name migration had never happened and re-armed `BRAINSTORM.md`/`NOTES.md`/`IDEAS.md` as live legacy names across that whole repo. It kept passing by luck alone: the only links to that repo's `book-moses/NOTES.md` happened to sit in a `MAP.md` and a `README.md`, both exempt as listing documents, and one ordinary link from anywhere else would have failed it for a violation that was never there. That is the same false positive the 2026-09-06 fix above was written to stop, reintroduced through the directory name instead of the filename -- so the Rule now says which half is fixed and which is a default, and the check asks the tracked tree for an `ASSORTED_NOTES.md` at any depth rather than testing one path.

Extended the same day: the same session then adopted a convention (`content-page-footer-links`, repo-local to that same repo) requiring every content page to end with a `## See also` linking every other content page, `content/ASSORTED_NOTES.md` included -- and the listing-document-only exemption didn't cover it, since a page's own footer isn't a `README.md` or `MAP.md`. Widened here rather than left as a gap: a `## See also` section is the same listing move as a directory index, just distributed one page at a time instead of centralized.

## Install
Nothing to install: deduplicated. The check that used to ship here, and its test, are removed; the ladder set ships the strict one.

As it read before 2026-11-18:

Reached via occasion. Checked mechanically by `tools/checks/check_assorted_notes.py`: a markdown link anywhere in the tracked tree, outside this practice file, the notes file itself, any file whose basename is `README.md` or `MAP.md`, and any `## See also` section (from that heading to the next `## ` heading or end of file) in any file, whose target path ends in `ASSORTED_NOTES.md` (or one of the legacy names it replaces) fails the check. Whether the legacy names still count is decided by asking `git ls-files` for an `ASSORTED_NOTES.md` at any depth -- not by testing `content/`, per the Rule's own default-vs-fixed distinction. Scope is `tree`. It can't catch a bare prose reference with no link -- only the linked form, which is the catchable case in a repo whose own standing convention is to always link ([rule-links](rule-links.md), this set's, which replaces universal's [doc-references-are-links](https://github.com/alex137/BestPractice/blob/staging/practices/doc-references-are-links.md) wherever this set is declared). Two-direction tested in `tools/checks/tests/test_assorted_notes.sh`.

**2026-09-10: citations inside a mirrored tree are out of scope.** The scan ran over every tracked file with no exclusion at all, so in a consuming repo it reported links sitting inside a vendored copy of somebody else's catalogue -- unactionable by construction, since editing a mirror is forbidden and the next sync overwrites it. It now asks `precedent_resolve.mirrored_prefixes(repo)`, the one place that question is answered, and skips those prefixes. Where the engine module is absent the answer is "exclude nothing", which is exactly what this check did before, so no repo loses a finding it used to get.
