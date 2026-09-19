---
slug:        deliverables-carry-no-process
title:       a document written for outside readers carries none of the process that made it
tier:        on-demand
severity:    error
applies_to:  ["**"]
occasion:    "writing or editing a document in a declared output path -- anything an outside reader will see"
gates:       ["push"]
index_clause: "an output document carries no attribution stamps, practice slugs or convention notes -- the practice layer keeps that record"
checked_by:  tools/checks/check_deliverables_carry_no_process.py
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-09-08
approved_by: "Morgan F, 2026-09-08"
source_practice_number: null
---
## Rule
A document in one of a repo's declared `output_paths` is written **for its reader**. It carries no record of the process that produced it:

- **No attribution stamps.** Not `(Morgan, 2026-09-08)`, not `Morgan, 2026-09-07` closing a sentence, not "per Morgan" attached to a decision. Who decided a thing, and when, is what git history and the practice layer are for.
- **No practice-slug citations.** Not `` (`assorted-notes`) ``, not a link into `practices/` or `process/`. A slug means nothing to a reader outside the project and reads as a leaked internal reference.
- **No notes about the repo's own conventions.** "Both are derived files -- regenerate them when a major change lands, don't edit them in place" is an instruction to a maintainer, addressed to somebody who does not have the repo.

**Two exemptions, and they are narrow.** The `<!-- Last updated ... -->` comment `file-header` requires is invisible in every rendering, so it stays. A `doc-recipes/` directory is exempt outright: a recipe's whole job is to state the rules for one file, and it is never shipped.

**Where the record goes instead.** A decision worth keeping goes in the repo's own open-items list or its brainstorm notes; a rule goes in the practice layer, at whichever level it belongs; a date goes in the commit. None of those travel with the deliverable, which is the point.

## Why
An output document has a reader who is not in the project and does not want to be. Every stamp, slug and maintenance note in it costs that reader attention and buys them nothing -- worse, it tells them they are reading somebody's working file rather than a finished piece, which is exactly the impression a deliverable exists to avoid.

The universal [deliverables-look-like-output](https://github.com/alex137/BestPractice/blob/precedent-beta-v01/practices/deliverables-look-like-output.md) already says the deliverable holds only what its audience needs. This is the same rule with the specific tells named and a check behind it, because "only what the audience needs" is a judgement that loses to the drafting habit of noting who said what, every time, and the residue accumulates one clause at a time until somebody reads the rendering.

## Story
2026-09-08, in a book-and-business repo whose `business-modeling/` cluster renders into a single HTML page meant to be sent to people as a link. Morgan read the rendering and found the process showing through: `(Morgan, 2026-09-08)` closing two sentences, four backticked practice slugs in the directory README and the action-items page, and -- the one that prompted this -- a whole hub section explaining that two files were derived and should be regenerated rather than edited in place. His words, on the vendored BestPractice (BP) set: *"BP keeps the record, but these documents (that will be for external purposes) shouldn't document rules."*

None of it was written carelessly. Each stamp was a session being honest about where a decision came from, and each slug was a session citing the rule it was following -- both good instincts in a working note, and both wrong in the one artifact that leaves the building. That is why this is a check rather than a reminder: the habit that produces the residue is a virtue everywhere else in the repo.

The check keys off `output_paths` rather than a fixed directory list, because which documents are outward-facing is a per-repo declaration and already written down.

**Moved to `precedent-team-writing` on 2026-09-09**, from `precedent-individual`, in the subject split BestPractice recorded as its own `split-team-sets-by-subject` item, DONE 2026-09-09 -- that item did not survive BestPractice's own 2026-09-16 todo/gotcha migration (no `todo/` archive file, no row in `spec/TODO_GOTCHA_MIGRATION_MAP.md`), so there is no anchor left to cite. The rule is about the craft of writing for a human reader, which is nobody's single team's business: a document project needs it as much as a software repo. While it lived in a set named for the people who happened to write it, neither could reach it without also taking twenty-odd rules about syncs, gates and branch setup. The copy left behind is `status: deduplicated` and points here; nothing was deleted and the rule was never out of force for a moment (`spec/MOVING_PRACTICES.md`, land first, deduplicate second).

## Install
Reached via occasion, and gated at `push`. Checked mechanically by [`tools/checks/check_deliverables_carry_no_process.py`](../tools/checks/check_deliverables_carry_no_process.py): it reads `precedent.json` for `output_paths` and `internal_paths`, then scans every tracked markdown file under an output path -- skipping `doc-recipes/` and HTML-comment lines -- for three tells. An attribution stamp (`Name, YYYY-MM-DD`, parenthesised or not, possessive or not, and tolerating a few words between the name and the date -- `Morgan's list, 2026-09-08` is the shape that taught it that) -- matched against the whole file rather than line by line, because these documents are hard wrapped and the first version missed a stamp whose name ended one line and whose date began the next; a **backticked or linked** practice slug drawn from the repo's committed `MANIFEST.json`, which is what keeps a hyphenated word that is not a slug from firing as a citation. The residual is narrow and deliberate: a word that IS a slug in that repo -- `install`, `push-back` -- fires even used as English, which is why the check requires the backticks that make it a citation rather than matching the word; and a markdown link whose target points into `practices/`, `process/` or `tools/checks/`. A repo that declares no `output_paths` is skipped, not failed. Scope is `tree`. Tested in both directions -- every tell, every exemption -- in [`tools/checks/tests/test_deliverables_carry_no_process.sh`](../tools/checks/tests/test_deliverables_carry_no_process.sh).

It cannot catch the third bullet of the Rule -- a maintenance note in prose has no shape a regex knows. That one is read, not checked, and the incident above is the example to read against.
