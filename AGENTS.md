# Repository notes for agents

This repo IS `precedent-team-writing` — a **team** source for
[Precedent](https://github.com/alex137/BestPractice/tree/precedent-beta-v01),
named for a **subject** rather than for a roster. Its subject is **the craft of writing for a human reader**: length and emphasis, when a list is really a list, drafting markers, citation and linking, and keeping a reader's material out of a deliverable that is not for them.

**Any team whose work includes that subject declares this set alongside its
own**, and a repo may declare several team sets — see
[README.md](README.md) for what is here, and Precedent's `INSTALL.md`
("Which team sets does this repo declare?") for how a project picks.

<!-- BEGIN GENERATED: precedent-loader -->

<!-- Regenerate with: python3 tools/build_views.py -- do not hand-edit this block; `python3 tools/build_views.py --check` exits non-zero on drift. Source: practices/ -- edit the practice file, never this block. -->

## Occasion index

```
When a commit fixes, closes, or resolves something a document names in prose as a known, open issue:
  resolved-issue-note-updates — When a commit fixes a bug, closes a gap, or resolves a limitation that some ...
When a standing constraint on one file gets stated a second time:
  doc-recipe — present-tense rules for one file, in doc-recipes/<name>.recipe.md
When about to commit a document that characterizes a real, identifiable person:
  sensitive-characterization-scrub — soften or ask before committing a blunt description of a real person
When drafting or reviewing prose meant to persuade or be judged:
  push-back — argue a real counter-case before building on a stated stance
When leaving a placeholder or fill-in-later note mid-draft:
  draft-marker — wrap a draft placeholder in ➡️ TEXT ⬅️, bold and all caps
When making the first commit in a fresh clone or session:
  commit-author — git config user.name/email to Morgan F, don't ask
When naming a git branch in a document, reply, or status update:
  branch-links — link every git branch mentioned to its tree view
When naming anything that has a destination, in a document or a reply:
  rule-links — link anything mentioned that has a destination, on first use
When root has accumulated three or more deliverable-content documents:
  content-subdirs — group deliverable content under a named subdirectory -- a recommendation
When writing a date or timestamp anywhere:
  buenos-aires-dates — dates and commit timestamps are Buenos Aires time, not UTC
When writing or pasting text into any document under a repo's declared output_paths:
  curly-quotes — a straight " or ' in outward-facing prose becomes a typographic curly quote

(More on-demand practices are not listed here: one whose applies_to names real paths, or which declares a gate, is reached by those channels instead -- `precedent_paths.py FILE` and `precedent_gate.py MOMENT`. A trigger a PERSON SAYS cannot be reached that way and is always listed above. `precedent_show.py --index-omitted` names the omitted ones.)
```

## Standing instruction

Before starting work of a kind named in the occasion index above, run `python3 tools/precedent_show.py SLUG` for each listed slug to load its Rule. When editing a file, `python3 tools/precedent_paths.py FILE` prints any on-demand practice whose `applies_to` matches it, without needing the index at all. At a named moment — before pushing, ending a turn and writing the reply — run `python3 tools/precedent_gate.py push|reply`: some practices fire at a moment rather than in a file, and no path glob reaches those. If `.precedent/SESSION_PRACTICES.md` exists, read it too: it carries the practices in force from the other sources this repo declares, which are NOT in this block and bind work here exactly as these do. It is regenerated at session start and is deliberately untracked — never commit it or quote it into a pull request.

<!-- END GENERATED -->

## Working in this repo

- **Practices are in [practices/](practices/)**, one file per practice, in
  Precedent's phase-1 format — frontmatter plus `## Rule` / `## Detail` /
  `## Why` / `## Story` / `## Install`.
- **Regenerate the block above** with `python3 tools/build_views.py` after
  any practice change; it rebuilds [MAP.md](MAP.md) and
  [GLOSSARY.md](GLOSSARY.md) alongside it. Never hand-edit it.
- **Before committing:** `python3 tools/precedent_check.py` — what matters
  is `0 violated`, never the passed or skipped count. This is the ONLY
  check a working branch gets:
  [`.github/workflows/precedent-check.yml`](.github/workflows/precedent-check.yml)
  ran on every push to every branch from 2026-09-14, but was narrowed to
  `push: branches: [main]` on 2026-09-19 (billing; see the file's own
  header), so a violation on a working branch is caught only if you run
  this yourself before the push, same as before 2026-09-14.
- **Approval** is a listed approver's own yes, in
  [approvers.json](approvers.json).
