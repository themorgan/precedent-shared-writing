---
slug:              todo-2026-09-10-mirrored-prefixes-helper-duplicated
kind:              analysis
domain:            null
severity:          null
status:            open
disposition:       wait
remind_on:         null
blocked_on:        "a way for a check to share code with its siblings that survives being copied alone; that convention belongs upstream, next to the copy-alone rule it has to satisfy."
batch:             null
decision:          null
decision_strength: null
waiting_on:        null
noted:             2026-09-10
closed:            null
---
## What

3. <a id="mirrored-prefixes-helper-duplicated"></a>**The `_mirrored_prefixes()` wrapper is duplicated in two checks.**
   Both checks that scan every tracked markdown file carry their own copy
   of the same short wrapper: put the engine on `sys.path`, call
   `mirrored_prefixes()`, fall back to the manifest-only answer when the
   import fails. The duplication is deliberate today — a check script is
   copied *alone* into fixtures that carry no sibling module, so importing
   a neighbour takes those fixtures down, which is the same reason
   `rule_text()` is duplicated across the whole catalogue. It is still two
   places for one answer to drift in. **Blocked-on:** a way for a check to
   share code with its siblings that survives being copied alone; that
   convention belongs upstream, next to the copy-alone rule it has to
   satisfy.

## How It Closes

Not open until: a way for a check to share code with its siblings that survives being copied alone; that convention belongs upstream, next to the copy-alone rule it has to satisfy.

## Notes

2026-09-19: migrated from TODO.md by tools/todo_migrate.py.
