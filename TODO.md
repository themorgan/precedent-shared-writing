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
   set, which turns the skip into a failure. **Blocked-on:** this repo
   has no Actions workflow at all yet, so there is nowhere to hang that
   job; adding one is a larger decision than this item.
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
   **Blocked-on:** deciding what counts as "the practice layer" in a §0
   install is a question for the engine, the way `mirrored_prefixes()`
   answered the mirror question; matching more path shapes here would
   re-create exactly the private re-derivation that
   [BestPractice's `source-checks-adopt-engine-helpers` item](https://github.com/alex137/BestPractice/blob/precedent-beta-v01/TODO.md#source-checks-adopt-engine-helpers)
   exists to remove.
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
