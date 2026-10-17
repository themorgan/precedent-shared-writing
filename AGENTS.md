# Repository notes for agents

This repo IS `precedent-shared-writing` — a **shared** source for
[Precedent](https://github.com/alex137/BestPractice/tree/staging),
named for a **subject** rather than for a roster. Its subject is **the craft of writing for a human reader**: length and emphasis, when a list is really a list, drafting markers, citation and linking, and keeping a reader's material out of a deliverable that is not for them.

**Any team whose work includes that subject declares this set alongside its
own**, and a repo may declare several shared sets — see
[README.md](README.md) for what is here, and Precedent's
[INSTALL.md](https://github.com/alex137/BestPractice/blob/staging/INSTALL.md)
("Which shared sets does this repo declare?") for how a project picks.

<!-- BEGIN GENERATED: precedent-loader -->

<!-- Regenerate with: python3 tools/build_views.py -- do not hand-edit this block; `python3 tools/build_views.py --check` exits non-zero on drift. Source: practices/ -- edit the practice file, never this block. -->

## Resident block (~149 of 2000 token budget, 2 of 19 practices)

**default-register.** **The register of a reply belongs to its reader.** Where the person you are working with has declared their own -- their individual practice set is where they do it -- that declaration governs and this rule steps aside. **Where none resolves, write to a reader who is not technical**, because on this team they generally are not; `## Detail` says what that means in full.

**language-variety.** **Write English as an American writes it and Spanish as an Argentine
writes it** (*color*, *apartment*; *vos tenés*, *celular*) in replies,
documents and commit messages. **Quoted material, proper names, and a
variety asked for on a given piece keep their own form**; `## Detail` has
the specifics.

## Occasion index

```
When a standing constraint on one file gets stated a second time:
  doc-recipe — present-tense rules for one file, in doc-recipes/<name>.recipe.md
When about to commit a document that characterizes a real, identifiable person:
  sensitive-characterization-scrub — soften or ask before committing a blunt description of a real person
When building a Word (.docx) document for someone to download:
  create-word-doc — a Word file for a reader: a footer, and it opens without an update-fields prompt
When handing a person a document to download:
  dated-download-names — the date goes at the end of its name: Name-2026-12-31.docx
When leaving a placeholder or fill-in-later note mid-draft:
  draft-marker — wrap a draft placeholder in ➡️ TEXT ⬅️, bold and all caps
When naming a branch in anything written:
  name-the-branch — name it literally, never a role-word like 'the base branch'
When naming a file, branch, doc or anything with a destination, in a doc, reply, PR or commit:
  rule-links — link it on first use; files as GitHub links, branches to tree view; docs by name
When starting a catch-all notes file, or renaming a legacy BRAINSTORM, NOTES or IDEAS file:
  assorted-notes — one ASSORTED_NOTES.md for ideas never cited elsewhere; listing it is fine
When writing a document an outside reader will see (a declared output path):
  deliverables-carry-no-process — no attribution stamps, practice slugs or convention notes in an output document

(More on-demand practices are not listed here: one whose applies_to names real paths, or which declares a gate, is reached by those channels instead -- `precedent_paths.py FILE` and `precedent_gate.py MOMENT`. A trigger a PERSON SAYS cannot be reached that way and is always listed above. `precedent_show.py --index-omitted` names the omitted ones.)
```

## Standing instruction

Before starting work of a kind named in the occasion index above, run `python3 tools/precedent_show.py SLUG` for each listed slug to load its Rule. When editing a file, `python3 tools/precedent_paths.py FILE` prints any on-demand practice whose `applies_to` matches it, without needing the index at all. At a named moment — before pushing, ending a turn and writing the reply — run `python3 tools/precedent_gate.py push|reply`: some practices fire at a moment rather than in a file, and no path glob reaches those. If .precedent/SESSION_PRACTICES.md exists, read it too: it carries the practices in force from the other sources this repo declares, which are NOT in this block and bind work here exactly as these do. It is regenerated at session start and is deliberately untracked — never commit it or quote it into a pull request.

<!-- END GENERATED -->

## Working in this repo

- **Practices are in [practices/](practices/)**, one file per practice, in
  Precedent's phase-1 format — frontmatter plus `## Rule` / `## Detail` /
  `## Why` / `## Story` / `## Install`.
- **Regenerate the block above** with `python3 tools/build_views.py` after
  any practice change; it rebuilds [MAP.md](MAP.md) and
  [GLOSSARY.md](GLOSSARY.md) alongside it. Never hand-edit it.
- **Before committing:** `python3 tools/precedent_check.py --full-sweep` — what matters
  is `0 violated`, never the passed or skipped count. **Nothing else runs
  it, on any branch**: a practice source runs no CI (universal
  `source-sets-run-no-ci`), so the check runs before the push or not at all.
  **Run it with `--full-sweep`; the bare command is a trap** -- bare, a
  check whose practice applies to `**`, most of this set's, is reached only
  by a one-in-ten rotation. The incidents behind both, and the CI this repo
  used to carry, are in
  [spec/WORKING_IN_THIS_REPO.md](spec/WORKING_IN_THIS_REPO.md).
- **Approval** is a listed approver's own yes, in
  [approvers.json](approvers.json).
