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
When a numbered list's entries are durable content likely to be cited by position:
  durable-list-anchors — anchor and slug each entry of a durable numbered list, not just its number
When a paragraph just got a substantial edit, or the piece is done:
  trim-prose — trim a paragraph right after editing it, and before calling it done
When a standing constraint on one file gets stated a second time:
  doc-recipe — present-tense rules for one file, in doc-recipes/<name>.recipe.md
When about to commit a document that characterizes a real, identifiable person:
  sensitive-characterization-scrub — soften or ask before committing a blunt description of a real person
When about to format connected prose as bullet points:
  list-restraint — don't reformat connected reasoning as bullet fragments
When citing support for a claim in a formal document:
  brainstorm-citations — cite a formal document for support, never a raw brainstorm entry
When drafting or reviewing prose meant to persuade or be judged:
  push-back — argue a real counter-case before building on a stated stance
When drafting or revising a list, or a document with list-like sections:
  list-item-parity — keep list items comparable in length; default to the shorter side
When leaving a placeholder or fill-in-later note mid-draft:
  draft-marker — wrap a draft placeholder in ➡️ TEXT ⬅️, bold and all caps
When mentioning a repo file in a chat reply, PR description, or commit message:
  file-mention-links — every file mention in chat or PR/commit text is a live GitHub link
When naming a git branch in a document, reply, or status update:
  branch-links — link every git branch mentioned to its tree view
When naming anything that has a destination, in a document or a reply:
  rule-links — link anything mentioned that has a destination, on first use
When reviewing a draft's balance before calling it done:
  proportional-emphasis — give a point space matching its importance, not its drafting mood
When root has accumulated three or more deliverable-content documents:
  content-subdirs — group deliverable content under a named subdirectory -- a recommendation
When writing a sentence that cites an exact, changeable count:
  no-stale-counts — drop a count that will go stale; say "several", not the number
When writing or editing a document in a declared output path -- anything an outside reader will see:
  deliverables-carry-no-process — an output document carries no attribution stamps, practice slugs or convention notes -- the practice layer keeps that record
```

## Standing instruction

Before starting work of a kind named in the occasion index above, run `python3 tools/precedent_show.py SLUG` for each listed slug to load its Rule. When editing a file, `python3 tools/precedent_paths.py FILE` prints any on-demand practice whose `applies_to` matches it, without needing the index at all. At a named moment — before pushing, ending a turn and writing the reply — run `python3 tools/precedent_gate.py push|reply`: some practices fire at a moment rather than in a file, and no path glob reaches those.

<!-- END GENERATED -->

## Working in this repo

- **Practices are in [practices/](practices/)**, one file per practice, in
  Precedent's phase-1 format — frontmatter plus `## Rule` / `## Detail` /
  `## Why` / `## Story` / `## Install`.
- **Regenerate the block above** with `python3 tools/build_views.py` after
  any practice change; it rebuilds [MAP.md](MAP.md) and
  [GLOSSARY.md](GLOSSARY.md) alongside it. Never hand-edit it.
- **Before committing:** `python3 tools/precedent_check.py` — what matters
  is `0 violated`, never the passed or skipped count. Since 2026-09-13
  [`.github/workflows/precedent-check.yml`](.github/workflows/precedent-check.yml)
  runs the same suite on every pull request, so a violation is caught either
  way; running it yourself is how you find out before the push rather than
  after.
- **Approval** is a listed approver's own yes, in
  [approvers.json](approvers.json).
