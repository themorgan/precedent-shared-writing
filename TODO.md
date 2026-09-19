# TODO has moved

**This file is a redirect stub**, kept so that anything still linking here
lands somewhere useful rather than at a 404 -- the same reason BestPractice
kept its own root `TODO.md` as a stub after its 2026-09-16 migration. Open
items live under [todo/](todo/) now, one file per item, and the list a
person actually reads is generated: [todo/TODO.md](todo/TODO.md) (open) and
[todo/CLOSED.md](todo/CLOSED.md) (done or dropped), rebuilt by
`python3 tools/build_todo_index.py` the same way [MAP.md](MAP.md) is
rebuilt from `practices/*.md`.

**A new item is never added here.** File it under `todo/` instead, as a new
`todo/todo-<date>-<slug>.md` file, per BestPractice's
[spec/OPEN_ITEM_AND_GOTCHA_PLAN.md](https://github.com/alex137/BestPractice/blob/precedent-beta-v01/spec/OPEN_ITEM_AND_GOTCHA_PLAN.md)
Part 1 (this repo drives that format with the vendored
[`tools/build_todo_index.py`](tools/build_todo_index.py) and
[`tools/todo_migrate.py`](tools/todo_migrate.py) but does not vendor the
spec document itself).

Migrated 2026-09-19 by `tools/todo_migrate.py`, 4 items, old anchor -> new
file:

| Old anchor | New file |
|---|---|
| `engine-cases-need-a-bestpractice-clone` | [todo/todo-2026-09-10-engine-cases-need-a-bestpractice-clone.md](todo/todo-2026-09-10-engine-cases-need-a-bestpractice-clone.md) |
| `internal-link-pattern-assumes-section-1-layout` | [todo/todo-2026-09-10-internal-link-pattern-assumes-section-1-layout.md](todo/todo-2026-09-10-internal-link-pattern-assumes-section-1-layout.md) |
| `mirrored-prefixes-helper-duplicated` | [todo/todo-2026-09-10-mirrored-prefixes-helper-duplicated.md](todo/todo-2026-09-10-mirrored-prefixes-helper-duplicated.md) |
| `todo-gotcha-stale-reference-exempted` | [todo/todo-2026-09-17-todo-gotcha-stale-reference-exempted.md](todo/todo-2026-09-17-todo-gotcha-stale-reference-exempted.md) |
