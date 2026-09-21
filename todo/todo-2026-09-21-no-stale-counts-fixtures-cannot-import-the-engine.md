---
slug:              todo-2026-09-21-no-stale-counts-fixtures-cannot-import-the-engine
kind:              analysis
domain:            mechanism
severity:          notable
status:            open
disposition:       wait
remind_on:         null
blocked_on:        "nothing technical -- deliberately deferred on Morgan's instruction, 2026-09-21, so a leak scrub could land without a test fix riding along."
batch:             null
decision:          null
decision_strength: null
waiting_on:        null
noted:             2026-09-21
closed:            null
---
## What

<a id="no-stale-counts-fixtures-cannot-import-the-engine"></a>**Five of
`tools/checks/tests/test_no_stale_counts.sh`'s cases fail, because the
fixture repositories cannot import `precedent_resolve`.** Cases A, C, L, M
and D' all expect the check to FIRE (exit 1) and get SKIPPED (exit 2)
instead, with the check's own reason:

```
SKIPPED: this repo declares more than one source, and precedent_resolve.py
could not be imported (No module named 'precedent_resolve') to tell whether
any of them is this repo's own tree -- so its own practice count could not
be verified
```

The module is present in this repo's `tools/`. What the fixtures do not get
is a path on which to find it, so every case whose fixture declares more
than one source degrades to the skip branch before it reaches the assertion
the case exists to make.

## Why it matters more than it used to

**The skip is the check behaving correctly and the test suite lying about
it.** A skip is not a pass -- the check says so itself -- but a test
harness that reports FAIL for five cases it cannot set up looks identical to
five real regressions, and a suite that is permanently five-red is a suite
people stop reading. That was survivable while CI re-ran things; as of
2026-09-21 this set runs no CI at all (`source-sets-run-no-ci`), so a local
run is the only run there is.

## Why it is not fixed here

**Pre-existing, and not this branch's.** Verified 2026-09-21 by counting
FAILs with the branch applied and with it stashed: five either way. The
branch that surfaced it changed comments only -- a private repo name scrubbed
out of two practice files, the check and this test. Morgan's call, in as many
words: leave the five alone, file this, and land the scrub without it. Mixing
a fixture fix into a leak scrub would have made a one-line-per-file change
into something needing a second review.

## What would close it

Establish why the fixture cannot see the engine -- most likely the fixture
tree is built without `tools/` and the check resolves its import relative to
the repo under test rather than to its own location -- and either give the
fixtures the module or have them assert the skip deliberately where the skip
is the honest answer. Worth checking whether the sibling suites that build
the same kind of fixture have the same hole and are simply not asserting
anything that would expose it.
