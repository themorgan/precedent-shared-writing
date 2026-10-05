---
slug:        assorted-notes
title:       ASSORTED_NOTES.md holds ideas never cited elsewhere -- but may be listed
tier:        on-demand
severity:    advisory
applies_to:  ["**"]
occasion:    "starting a catch-all notes file, or renaming a legacy BRAINSTORM, NOTES or IDEAS file"
gates:       []
index_clause: "one ASSORTED_NOTES.md for ideas never cited elsewhere; listing it is fine"
checked_by:  tools/checks/check_assorted_notes.py
defines:     ["ASSORTED_NOTES.md"]
status:      active
supersedes:  []
overrides:   null
added:       "2026-10-05"
approved_by: "Morgan F, 2026-10-05, moved from the shared set precedent-shared-working-style (there: Morgan F, 2026-09-23, moved from the individual set precedent-individual (there: Morgan F, 2026-09-04; revised 2026-09-05, Morgan F, to exempt plain directory-listing links, then again the same day to exempt any See also section))"
source_practice_number: null
in_force_at: null
strength: decided
---
## Rule
A repo keeps a single file, `ASSORTED_NOTES.md`, for random notes, observations, comments, and things to use later -- content not yet organized or ready to be relied on as support for something else. When upgrading a legacy repo that already has an equivalent file under a different name (`BRAINSTORM.md`, `NOTES.md`, `IDEAS.md`, or similar), rename it to `ASSORTED_NOTES.md`, keeping its content, for consistency across repos.

**The filename is fixed; the directory is not.** It sits with the repo's other content -- in the directory that holds it, or at the root when there is none -- as `<that directory>/ASSORTED_NOTES.md`, and nothing below is any different for it. Older repos keep theirs in `content/`.

Nothing anywhere else in the repo may **cite** an idea from inside `ASSORTED_NOTES.md` as support for an argument, a decision, or a claim -- the moment something in it is actually needed that way, it has graduated out of the file into wherever referenceable content belongs, and the reference should point there instead. This does **not** forbid the file itself from appearing as a plain link in a listing context: a directory-listing document (a repo's own root `README.md`, a `README.md` inside `content/` or any other directory, or a `MAP.md`-style index, whose whole job is saying what exists and where), or a `## See also` cross-reference section in any file (the same listing move, distributed per-page instead of centralized in one index). Listing the file so a reader can go open and skim it is not the same as citing something inside it; only the second is what this practice forbids.

## Why
One consistently named catch-all for not-yet-formed thoughts, kept apart from anything actually cited, means a note can be dropped there freely without it quietly turning into something else depends on. That concern is about citation, not visibility -- a repo's own orientation documents still need to be able to tell a reader the file exists, or the file becomes undiscoverable rather than merely uncited, which is a worse outcome for a "read this if you're curious" catch-all. A consistent filename across repos also means a session upgrading any of them knows exactly what to look for and what to rename.

## Story
2026-09-29: the `content/` default went with `content-directory`, retired that day for [organize-scattered-content](https://github.com/alex137/BestPractice/blob/staging/practices/organize-scattered-content.md). The filename rule stands on its own; where the file lives now follows wherever the repo keeps its content.

2026-09-05, working in a dependent content repo: a session read the Rule as written -- "nothing anywhere else... may reference or link to" -- literally, and de-linked `content/ASSORTED_NOTES.md` even from that repo's own root `README.md`, `content/README.md`, and `MAP.md`, files whose entire purpose is inventorying what's in the repo. Caught and corrected the same session: "I know I said don't [link] to ASSORTED_NOTES but an exception to that is, in 'lists of files', it's still there to be examined if people want -- I just meant the ideas within it aren't yet ready to be referenced elsewhere." Revised here at the source rather than as a repo-local override, since the distinction (citation vs. listing) is true of every repo this practice reaches, not particular to that one.

2026-09-07, the directory half: a consuming repo renamed `content/` to `business-modeling/`, so that every content directory it had said what it held. Its `ASSORTED_NOTES.md` moved with the rename, intact -- and the check, which tested one literal path, concluded the legacy-name migration had never happened and re-armed `BRAINSTORM.md`/`NOTES.md`/`IDEAS.md` as live legacy names across that whole repo. It kept passing by luck alone: the only links to that repo's `book-moses/NOTES.md` happened to sit in a `MAP.md` and a `README.md`, both exempt as listing documents, and one ordinary link from anywhere else would have failed it for a violation that was never there. That is the same false positive the 2026-09-06 fix above was written to stop, reintroduced through the directory name instead of the filename -- so the Rule now says which half is fixed and which is a default, and the check asks the tracked tree for an `ASSORTED_NOTES.md` at any depth rather than testing one path.

Extended the same day: the same session then adopted a convention (`content-page-footer-links`, repo-local to that same repo) requiring every content page to end with a `## See also` linking every other content page, `content/ASSORTED_NOTES.md` included -- and the listing-document-only exemption didn't cover it, since a page's own footer isn't a `README.md` or `MAP.md`. Widened here rather than left as a gap: a `## See also` section is the same listing move as a directory index, just distributed one page at a time instead of centralized.

## Install
Reached via occasion. Checked mechanically by [`tools/checks/check_assorted_notes.py`](../tools/checks/check_assorted_notes.py): a markdown link anywhere in the tracked tree, outside this practice file, the notes file itself, any file whose basename is `README.md` or `MAP.md`, and any `## See also` section (from that heading to the next `## ` heading or end of file) in any file, whose target path ends in `ASSORTED_NOTES.md` (or one of the legacy names it replaces) fails the check. Whether the legacy names still count is decided by asking `git ls-files` for an `ASSORTED_NOTES.md` at any depth -- not by testing `content/`, per the Rule's own default-vs-fixed distinction. Scope is `tree`. It can't catch a bare prose reference with no link -- only the linked form, which is the catchable case in a repo whose own standing convention is to always link ([doc-references-are-links](https://github.com/alex137/BestPractice/blob/staging/practices/doc-references-are-links.md), universal). Two-direction tested in [`tools/checks/tests/test_assorted_notes.sh`](../tools/checks/tests/test_assorted_notes.sh).

**2026-09-10: citations inside a mirrored tree are out of scope.** The scan ran over every tracked file with no exclusion at all, so in a consuming repo it reported links sitting inside a vendored copy of somebody else's catalogue -- unactionable by construction, since editing a mirror is forbidden and the next sync overwrites it. It now asks `precedent_resolve.mirrored_prefixes(repo)`, the one place that question is answered, and skips those prefixes. Where the engine module is absent the answer is "exclude nothing", which is exactly what this check did before, so no repo loses a finding it used to get.
