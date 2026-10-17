# Working in this repo — the long version

**[AGENTS.md](../AGENTS.md)'s "Working in this repo" section carries the
instructions. This file carries the history behind them**, moved here on
2026-10-17 so that every session stops paying for it (universal
`reduction-pass`: move, never delete). The very deep check of that day
found AGENTS.md retelling this repository's old CI in every session, and
the session moved it under Morgan's delegation of that day ("Fix the other
issues you found including the checks that never run. Tell me what you
decide. I will be offline so don't wait for me. Approved, act, and
Booked."). Nothing was shortened on the way out: the section below is the
bullet that used to sit in [AGENTS.md](../AGENTS.md), word for word.

## The full sweep, and why there is no CI

- **Before committing:** `python3 tools/precedent_check.py --full-sweep` — what matters
  is `0 violated`, never the passed or skipped count. **Nothing else runs
  it, on any branch.** This repo carried a `precedent-check.yml` workflow
  from 2026-09-14 and a `leak-gate.yml` from 2026-09-20; on 2026-09-21 the
  vendored engine deleted both on refresh, because a practice source
  installs no CI at all — universal's `source-sets-run-no-ci`, decided on a
  usage export in which four sets running two workflows each were 127 of
  143 billed minutes in one day. So there is no after-the-push gate here
  any more, and none of the older ones is coming back: the check runs
  before the push, or it does not run.
  **Run it with `--full-sweep`; the bare command is a trap.** Bare, it runs
  only the checks this diff routes to plus a one-in-ten rotation, and a
  check whose practice applies to `**` -- most of this set's -- is reached
  only by the rotation. In a sibling set, that let two links to a private
  repo, added 2026-09-23, sit on `main` past a clean bare run until a sweep
  found them on 2026-09-24. The sweep takes about five seconds.
