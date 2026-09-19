---
slug:              todo-2026-09-10-engine-cases-need-a-bestpractice-clone
kind:              manual
domain:            null
severity:          null
status:            open
disposition:       wait
remind_on:         null
blocked_on:        null
batch:             null
decision:          null
decision_strength: null
waiting_on:        null
noted:             2026-09-10
closed:            null
---
## What

1. <a id="engine-cases-need-a-bestpractice-clone"></a>**The mirror-exclusion test cases need a BestPractice clone, and skip
   without one.** [`check_no_stale_counts.py`](tools/checks/check_no_stale_counts.py)
   and [`check_draft_marker.py`](tools/checks/check_draft_marker.py) get
   their mirror exclusion from `precedent_resolve.mirrored_prefixes()`,
   which is in upstream's `CONSUMER_ENGINE_FILES` and not its
   `ENGINE_FILES` — so it is absent inside a practice set, correctly, and
   [`tools/ENGINE_MANIFEST.json`](tools/ENGINE_MANIFEST.json) does not list
   it. The cases that exercise the engine path therefore copy a real
   `precedent_resolve.py` in from a clone found via
   `PRECEDENT_BESTPRACTICE_CLONE`, and report `SKIPPED (not a pass)` where
   there is none. A stub was refused on purpose: it would test the stub.
   Each suite still asserts the no-engine direction unconditionally, so a
   run with no clone proves the fallback and not the fix.
   **What would close it:** a CI job that clones BestPractice once and runs
   [`tools/checks/tests/run_all.sh`](tools/checks/tests/run_all.sh) with
   `PRECEDENT_BESTPRACTICE_CLONE` and `PRECEDENT_REQUIRE_ENGINE_CASES=1`
   set, which turns the skip into a failure.

   **The stated blocker is stale.** This item said, as of 2026-09-10, that
   the blocker was having no Actions workflow at all to hang the job on.
   [`.github/workflows/precedent-check.yml`](.github/workflows/precedent-check.yml)
   has existed since 2026-09-12 and runs on every push, but it only calls
   `python3 tools/precedent_check.py` — the check REGISTRY, which runs each
   check once against this repo's own live tree. It never calls
   [`tools/checks/tests/run_all.sh`](tools/checks/tests/run_all.sh) — the
   TEST SUITES, which exercise each check's own correctness (including the
   fixtures this item is about) against planted fixtures rather than this
   repo's real content. Those are two different things this repo runs
   locally (`python3 tools/precedent_check.py`, `bash
   tools/checks/tests/run_all.sh`) and CI only picked up the first one. So
   the real blocker was never "no workflow" — it is that the existing
   workflow's one job does not reach these fixtures, and 2026-09-19's
   `no-stale-counts` fix (adding fixture pair J/K alongside existing H/I in
   [`test_no_stale_counts.sh`](tools/checks/tests/test_no_stale_counts.sh))
   landed with all four of those engine-path cases still unverified by CI —
   confirmed locally only, by hand, in that session.

   **Recommendation:** add a second job (or a step in the existing one) to
   `precedent-check.yml` that shallow-clones `alex137/BestPractice` (public;
   no credential needed) to `../BestPractice` relative to the checkout —
   `find_engine()` in `test_no_stale_counts.sh` already looks there by
   default, ahead of the `PRECEDENT_BESTPRACTICE_CLONE` env var, so cloning
   to that exact path may need no new configuration at all — then runs
   `PRECEDENT_REQUIRE_ENGINE_CASES=1 bash tools/checks/tests/run_all.sh`.
   Keep it a separate job from the existing one (or a separate step
   clearly named, per that workflow's own "four named steps, not one"
   reasoning) so a failure here reads as "the engine-path fixtures broke,"
   not folded into the registry job's one red X.

## How It Closes

(not yet stated by the migration -- a session filling this in should read ## What and say what has to be true for `status` to become `done`.)

## Notes

2026-09-19: migrated from TODO.md by tools/todo_migrate.py.
