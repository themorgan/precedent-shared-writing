---
slug:              todo-2026-09-10-internal-link-pattern-assumes-section-1-layout
kind:              analysis
domain:            null
severity:          null
status:            open
disposition:       wait
remind_on:         null
blocked_on:        "that upstream helper."
batch:             null
decision:          null
decision_strength: null
waiting_on:        null
noted:             2026-09-10
closed:            null
---
## What

2. <a id="internal-link-pattern-assumes-section-1-layout"></a>**`INTERNAL_LINK` in the deliverables check names §1's paths.**
   [`check_deliverables_carry_no_process.py`](tools/checks/check_deliverables_carry_no_process.py)
   reports a link *out of* a reader-facing document *into* the practice
   layer, and recognises that layer by the literal path segments
   `practices/`, `process/` and `tools/checks/`. The first survives every
   install model, since a §0 install's vendored catalogue still has a
   `practices/` directory inside it. The other two are §1's shape: a §0
   install puts the engine at `tools/`, so a link to, say,
   `tools/precedent_show.py` reads as ordinary content. That direction is a
   false negative — a leak this check quietly permits — not a false
   positive, which is why it was recorded rather than guessed at.
   **The fix belongs upstream, not here,** and is recorded in
   BestPractice's own follow-ups next to
   [`mirrored_prefixes()`](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_resolve.py).
   Deciding what counts as "the practice layer" in a §0 install is the same
   kind of question `mirrored_prefixes()` answered for mirrors; matching
   more path shapes *here* would re-create exactly the private
   re-derivation that
   [BestPractice's `source-checks-adopt-engine-helpers` item](https://github.com/alex137/BestPractice/blob/staging/todo/todo-2026-09-10-source-checks-adopt-engine-helpers.md)
   exists to remove. So this item stays open as a pointer: it is closed by
   an engine helper arriving, not by work in this repo.
   **Blocked-on:** that upstream helper.

## How It Closes

Not open until: that upstream helper.

## Notes

2026-09-19: migrated from TODO.md by tools/todo_migrate.py.
