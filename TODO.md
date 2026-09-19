# TODO — open items for precedent-team-writing

Open items for this practice set itself: the checks it ships, and the
harness around them. Practice *content* is proposed by a pull request
against [practices/](practices/), not tracked here.

**Cite an item by its anchor, never by its number.** Every item carries an
`<a id="...">` slug, and the visible number is reading-order furniture that
shifts whenever anything is added or reordered
([durable-list-anchors](practices/durable-list-anchors.md)). Write
`` [TODO.md's `slug` item](TODO.md#slug) ``.

**No `**Disposition:**` lines yet, deliberately.** The default disposition
is `wait`, and `wait` is written as nothing; the other two values carry a
stamp naming *who* set them, and nobody has been asked about these items
yet. A stamp with a fabricated name is worse than no stamp.

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
   [`mirrored_prefixes()`](https://github.com/alex137/BestPractice/blob/precedent-beta-v01/tools/precedent_resolve.py).
   Deciding what counts as "the practice layer" in a §0 install is the same
   kind of question `mirrored_prefixes()` answered for mirrors; matching
   more path shapes *here* would re-create exactly the private
   re-derivation that
   [BestPractice's `source-checks-adopt-engine-helpers` item](https://github.com/alex137/BestPractice/blob/precedent-beta-v01/TODO.md#source-checks-adopt-engine-helpers)
   exists to remove. So this item stays open as a pointer: it is closed by
   an engine helper arriving, not by work in this repo.
   **Blocked-on:** that upstream helper.
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
4. <a id="todo-gotcha-stale-reference-exempted"></a>**`todo-gotcha-stale-reference` flags this file, exempted for now.** The
   2026-09-17 engine refresh brought in a check that flags any
   `TODO.md#anchor` string. It caught two things here: the instructional
   example near the top of this file (`` `TODO.md#slug` ``, a placeholder,
   not a real link), and the link to BestPractice's own
   `source-checks-adopt-engine-helpers` item two items up, which is
   genuinely stale — that item is gone from BestPractice's current
   `todo/` tree and its own `spec/TODO_GOTCHA_MIGRATION_MAP.md`, and
   nothing found here confidently says where it went. Repointing that
   link needs someone to trace it in BestPractice's own history, not a
   guess made from this repo. Declared `not_binding` in `precedent.json`
   until then. **Blocked-on:** tracing the real destination of the
   `source-checks-adopt-engine-helpers` item in BestPractice.
