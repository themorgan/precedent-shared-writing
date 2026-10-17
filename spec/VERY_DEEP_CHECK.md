---
title:         Very deep check -- run record
kind:          record
status:        live
opened:        2026-10-17
closed:        null
superseded_by: null
supersedes:    []
audience:      session
summary:       "The run record of the very deep check in this repo: what each pass found, what was fixed here, and what belongs upstream."
---
# Very deep check -- run record

The state of the current very deep check in this repository (practice:
very-deep-check, carried in the vendored catalogue). A later session resumes
at the first pass below that is not marked done.

## Current run

| Pass | Status | Date | Notes |
|---|---|---|---|
| 1 -- installs and updates | partial | 2026-10-17 | A scratch consumer declaring this set resolves it (with `rule-links` replacing universal `doc-references-are-links`). No real consumer was attached, and the bootstrap-drift comparison runs only upstream, so this pass stays partial. README now carries the one-line declaration. |
| 2 -- mechanisms | done | 2026-10-17 | Own gates clean: `precedent_check.py --full-sweep` 57 passed, 0 violated; leak gate OK; check tests 100 ok with a BestPractice clone set (9 skip without one, the open item's subject). Warnings 86 to 16 open: links fixed, five permanent exclusions in `tools/warning_exclusions.json`. `precedent.json` recorded under `not_generated`. |
| 3 -- coherence read | done | 2026-10-17 | Stale text fixed in README, AGENTS.md, `precedent.json` and two practices. Reported, not changed: `create-word-doc` is unreachable from the occasion index and contradicts `dated-download-names` on committing outputs; `language-variety`'s prose-date form is contradicted by the whole corpus; `name-the-branch` is a shared rule written to one reader; the public set's `leak-blocklist.txt` invites private terms. **Fixed the same day under Morgan's delegation** ("Approved, act, and Booked."), on branch `2026-10-17-themorgan-fx-sets` (precedent-shared-writing): `create-word-doc` carries `index_required: true`, defers placement and naming to `generated-docs-in-output` and `dated-download-names`, and keeps its procedure in Detail; `language-variety` keeps year-month-day dates in records; `name-the-branch` speaks of the person; the blocklist header and README say the set is public; AGENTS.md's CI history moved to [spec/WORKING_IN_THIS_REPO.md](WORKING_IN_THIS_REPO.md). |
| 4 -- catalogue, backlog, branches | done (branches) | 2026-10-17 | Two merged branches from today's Update Vendors, delete once that session ends; two `data-` branches are the engine's and stay. Open items and gotchas were judged by another helper. |

## Upstream findings

Every finding of this run that is better fixed upstream, as one paste-ready
prompt for a session rooted in the upstream repository, and what the person
said about band-aids here until it lands. Filled in by the session during the
run.

````text
From: the very deep check session (session_015pVTsH9zWGrgpmmwrFgX2q, https://claude.ai/code/session_015pVTsH9zWGrgpmmwrFgX2q), its set-writing helper -- a session wrote this, not a person typing it.
For: a new session rooted in alex137/BestPractice.

A very deep check of a shared practice set (2026-10-17, read on `main` at e412961, vendored engine 66e05b79bb78) found these engine and template problems. Every one is in BestPractice, so fix them there; name the set only in general terms ("a shared set") in anything you commit. No merge authorization comes with this handoff: land on `staging` (BestPractice) by the repo's usual route and ask before merging.

1. **The set skeleton READMEs describe a set that no longer exists.** `templates/practice-set-shared/README.md` lines 20-21, 28-45 and `templates/practice-set-individual/README.md` lines 26-27, 34-45: the `tools/` row names eight engine files and says "nothing under `tools/` exists in this skeleton yet" (a refreshed set carries 108 manifest files); the `.github/workflows/` row promises two CI gates "at bootstrap", which `source-sets-run-no-ci` retired on 2026-09-21; "Before you push" runs the bare `precedent_check.py`, which every set's own AGENTS.md calls a trap (`--full-sweep`); and it quotes "7 passed, 42 skipped" / "8 passed, 41 skipped", where a real set measures 57 passed / 62 skipped today. A new set's owner reads that CI is checking their pushes. Rewrite both rows and the section, and drop the counts (`no-stale-counts`).
2. **A public set is handed a private-term blocklist to fill in.** `templates/practice-set-shared/leak-blocklist.txt` (and `templates/leak-blocklist.txt.template`) ship into every new set whatever its `visibility`, with a header asking for client names and code words; in a public set, filling it in publishes them. The header's switch-on steps (export `PRECEDENT_LEAK_BLOCKLIST`, `git config precedent.requireVocabulary true`) also predate `leak_gate.discovered_neighbour_blocklists()` (2026-10-01), which reads every sibling's list with no setup. Bootstrap a public set without one (or with a header saying its terms belong in a private set's list), and describe the current discovery.
3. **`very_deep_check.py` skips a linked git worktree as "not its own git checkout".** Lines 5354 and 5543 test `(repo_dir / '.git').is_dir()`; in a worktree `.git` is a file, so the checkout's branch sweep and its live-session half print "skipped" and `record/stale_branches.md` is written with "checkout ... skipped". From the same worktree the UPSTREAM section said "no clone beside this one" though a BestPractice clone sits beside the main clone, and the run resolved the set's own main clone as a second shared source of itself. Use `git rev-parse` to detect a checkout and `--git-common-dir`'s parent for siblings, as `leak_gate.discovered_neighbour_blocklists()` already does. Reproduce: `git worktree add` any set, run the tool from it.
4. **The occasion index drops a practice whose occasion is an act, not an edit.** `build_views.py` leaves out a practice whose `applies_to` names real paths, on the reasoning that `precedent_paths.py` reaches it. A shared set's Word-document practice has `applies_to: ["tools/create_word_doc.py"]` and the occasion "producing any Word (.docx) document for someone to download"; producing one never edits that script, so no session building a Word file is shown the practice (`precedent_show.py --index-omitted` lists it "via: paths tools/create_word_doc.py"). Either keep a practice in the index when its occasion names no file edit, or have a check flag a narrow `applies_to` whose occasion is not an edit to those paths and point at `index_required: true`.
5. **`write_generated_files()` never seeds `not_generated` for `precedent.json`.** Every set's `precedent.json` is written in place by `precedent_branches.py` (line ~1106), so every set's very deep check lists it under GENERATED FILES; none of the three sets on this machine records it. BestPractice's own registry already carries the entry; seed the same one in `precedent_bootstrap_source.write_generated_files()`.
6. **`tools/warning_exclusions.json`'s `_comment` never names the `why` key.** It says "each with its reason" and lists `source`, `kind`, `path`, `match`, `term`, `decided` and `by`; `warning_review.py`'s `ENTRY_KEYS`/`TERMS` require `why`. An entry written from the comment uses `reason` and is rejected as an unknown key. Name `why` (and `revisit`) in the comment.

Each fix runs `python3 tools/precedent_push_check.py` bare before the push; findings 3 and 4 want a planted case.
````

**Band-aids here until these land:** asked of Morgan in the run's reply, 2026-10-17; his answer goes here. Upstream is a repository the same session lands in, so several items were fixed there in that run (BestPractice, branch 2026-10-17-themorgan-very-deep-check-fgx2q-568u9: the worktree scans, the warnings link, the record files' registration, the freshness verdicts); the rest are filed there. Its run account says which.

## Runs so far

| Run | Passes completed | What it changed |
|---|---|---|

## Warnings

<!--vdc-embed:warnings: never hand-edit -- written by tools/very_deep_check.py's WARNINGS section; refresh with --refresh-warnings -->
Measured 2026-10-17: **56 warning(s), 15 still open** (neither fixed nor excluded). For comparison, open when this run started: 16.

| Source | Kind | Warnings | Open | Excluded for good | Excluded until a date |
|---|---|---|---|---|---|
| doc_lint | unlinked file reference | 55 | 14 | 41 | 0 |
| precedent_session_check | undetermined | 1 | 1 | 0 | 0 |

**Exclusions decided this run: 5.**
- doc_lint / unlinked file reference / `practices/assorted-notes.md`: permanent, by the session -- Every hit is a filename the rule is about (ASSORTED_NOTES.md, the legacy BRAINSTORM/NOTES/IDEAS names, README.md and MAP.md as listing documents) or a path in another repository's story; none is a file in this repository to link to.
- doc_lint / unlinked file reference / `practices/dated-download-names.md`: permanent, by the session -- OUTBOX.md is the file the rule asks a consuming repository to keep at its root; this set has none, so there is nothing here to link.
- doc_lint / unlinked file reference / `practices/doc-link-text.md`: permanent, by the session -- Deduplicated stub kept word for word (in_force_at: rule-links); its hits are the GLOSSARY.md, MAP.md and README.md examples of the link-text rule itself, which must show the bare filename to make the point.
- doc_lint / unlinked file reference / `practices/doc-recipe.md`: permanent, by the session -- Every hit is the naming convention the rule defines (.recipe.md, book/CHAPTER1.md and its recipe), an example, not a file in this repository.
- doc_lint / unlinked file reference / `practices/visual-style-guide.md`: permanent, by the session -- VISUAL_STYLE_GUIDE.md and content/VISUAL_STYLE_GUIDE.md name the file the rule generates in a consuming project; this set has none.
- Not read: model_audit: not read -- no tools/model_audit.py here

Exclusions live in [tools/warning_exclusions.json](../tools/warning_exclusions.json); [tools/warning_review.py](../tools/warning_review.py) lists every open group.
<!--/vdc-embed:warnings-->
