---
slug:              todo-2026-09-17-todo-gotcha-stale-reference-exempted
kind:              analysis
domain:            null
severity:          null
status:            done
disposition:       wait
remind_on:         null
blocked_on:        null
batch:             null
decision:          null
decision_strength: null
waiting_on:        null
noted:             2026-09-17
closed:            2026-09-19
---
## What

4. <a id="todo-gotcha-stale-reference-exempted"></a>**`todo-gotcha-stale-reference` flags this file, exempted.** The
   2026-09-17 engine refresh brought in a check that flags any old-format
   TODO anchor string. It caught two things here: the instructional
   example near the top of this file (a placeholder, not a real link),
   and the link to BestPractice's own
   `source-checks-adopt-engine-helpers` item two items up, which was
   genuinely stale — that item had gone missing from BestPractice's
   current `todo/` tree and its own `spec/TODO_GOTCHA_MIGRATION_MAP.md`
   during a migration that dropped it. A BestPractice-rooted session
   traced it, restored the archive file, and fixed the migration map
   (2026-09-19); the link two items up now points at the restored
   `todo/todo-2026-09-10-source-checks-adopt-engine-helpers.md` and is no
   longer stale. What remains is only the instructional placeholder,
   which is not a real link and will always match this pattern set by
   design — still declared `not_binding` in `precedent.json` for that one
   reason.

## How It Closes

Closes when the instructional placeholder itself is gone -- i.e. when
`TODO.md` stops being the hand-edited, bulleted file that placeholder lived
in.

## Notes

2026-09-19: migrated from TODO.md by tools/todo_migrate.py.

2026-09-19: closed by the same migration this item was filed to explain the
fallout of. `tools/todo_migrate.py --apply` moved every real item (this one
included) under `todo/`, and `TODO.md` was then replaced with the
"# TODO has moved" redirect stub — the instructional placeholder this item
was about does not exist in that stub, so `todo-gotcha-stale-reference`
finds nothing left to flag. Removed the now-unneeded `not_binding` entry
from `precedent.json`; re-ran the check with it gone and it stayed clean.
