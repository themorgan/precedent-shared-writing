---
slug:        buenos-aires-dates
title:       Every date is Buenos Aires local time
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "writing a date or timestamp anywhere"
gates:       []
index_clause: "dates and commit timestamps are Buenos Aires time, not UTC"
checked_by:  tools/checks/check_buenos_aires_dates.py
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-08-31
approved_by: "Morgan F, migrated from RepoPersonalPreferences by the private-set migration session"
---
## Rule
Every date is my own local calendar date -- the timezone `identity.json` declares, at the root of this set, which is Buenos Aires -- never the session container's system clock and never UTC. That file is the one place the zone is written down: the `env` block derives from it, the `pre-commit` hook enforces it, and this practice's own check computes the expected offset from it. Two mechanisms: a prose date (a doc's "as of" note, a last-updated header) uses the Buenos Aires calendar date on the day the text was written; a git commit gets the right offset by running the commit itself under `TZ="America/Argentina/Buenos_Aires"` -- git resolves the offset from `TZ` at commit time, so no manual arithmetic is needed.

## Detail
Argentina has held UTC-3 year-round, with no daylight saving, since 2009 *(verified 2026-08-21)*. If that ever changes, every mechanism keyed to it -- this rule, and any scheduled workflow's cron line written against Buenos Aires time -- needs re-deriving; treat this note as a standing reminder to re-check the fact the next time this practice is touched.

## Why
It's my own timezone, and a document or commit timestamped in whatever timezone a session container happens to be running in is a fact about the infrastructure, not about when I actually did the work.

## Story
**2026-09-06: five commits landed on `main` with a `+0000` offset**, the same five that landed with the wrong author (see [`commit-author`](commit-author.md)'s Story) and for the same underlying reason: a hosted container's clock is UTC, and this practice was asking whoever was at the keyboard to remember to override that, on every commit, forever. They were grandfathered on Morgan's explicit instruction rather than rewritten, and the fix went forward: `TZ` is now declared in the project's `.claude/settings.json` `env` block, so a commit gets the right offset without anyone typing anything, and the `pre-commit` hook `bootstrap/commit-identity.sh` installs refuses a commit whose offset is wrong anyway.

**2026-09-07: two more**, from a session whose primary repo was BestPractice, not this one -- this set's `SessionStart` hook never ran for it, so neither the author nor the offset was corrected by construction. The wrong author was caught and fixed before pushing; the `+0000` offset was caught only after the commits had already been published, and grandfathered on Morgan's explicit approval rather than rewritten, for the same `git pull --ff-only` reason as the five above.

## Install
`TZ="America/Argentina/Buenos_Aires"` in front of a `git commit` still works and is still correct, but is no longer what this depends on: every project I work in declares `TZ` in its `.claude/settings.json` `env` block (the same block [`commit-author`](commit-author.md)'s Install section describes -- there is no separate snippet file for this half; `GIT_AUTHOR_NAME`/`GIT_AUTHOR_EMAIL`/`TZ` are one block, merged together), so every commit the session makes carries the offset by default. `bootstrap/commit-identity.sh`'s `pre-commit` hook is the backstop: it reads the offset git is about to record and refuses the commit if it is not `-0300`, naming the `TZ` command in its own message. For prose, resolve "today" in that timezone before writing a date into a document -- that half has no mechanism and cannot have one.

Checked mechanically, but only half of it: [`tools/checks/check_buenos_aires_dates.py`](../tools/checks/check_buenos_aires_dates.py) verifies every commit reachable from HEAD carries a `-0300` author-date offset. Scope is `tree` -- `ROOT`'s own history, where `ROOT` is this repo when the check runs here in place, and the consuming repo when materialized into one. That's the git-commit mechanism in full -- `TZ` at commit time is recorded verbatim, so a wrong offset is a hard, unambiguous signature. The prose-date mechanism has no such signature: nothing in the repo independently tells a check what the actual Buenos Aires wall-clock date was when a line of prose was written, so a check can't tell a correct date from a wrong one, only that *some* date-shaped string is present -- checking format wouldn't be checking the rule. It's covered partially by `file-header`'s own timestamp-format and version-continuity check for files that carry that header, but the general case stays a judgment call. Two-direction tested in [`tools/checks/tests/test_buenos_aires_dates.sh`](../tools/checks/tests/test_buenos_aires_dates.sh). The check's `GRANDFATHERED_SHAS` mechanism exempts an already-published commit by SHA rather than rewriting history to silence it -- see `no-rewrite-for-warnings` (BestPractice universal). Seven commits sit in that list today: the five of 2026-09-06 and the two of 2026-09-07 named in the Story above, all grandfathered on Morgan's explicit instruction. Two earlier ones (`ac525c9`, `0016903`) were instead rewritten in place on 2026-09-03, also on his explicit instruction; the list emptied then and refilled. Every commit made after that mechanism landed is fully checked.

**2026-09-07: a second, per-repo exemption list, because the first one can't reach a consuming repo's own history.** `GRANDFATHERED_SHAS` above is this set's own history, hardcoded -- fine as long as the check only ever audits the repo it ships in. The first real consumer to need this (`themorgan/HavrutaBrainstorm`, six commits, all predating this mechanism) can't add to that set: `tools/checks/` in a consuming repo is `precedent_materialize.py`'s own output, rewritten from this source on every sync, so an edit there is erased. `identity.json` is already the one per-`ROOT` file this check reads -- an optional `grandfathered_commit_shas` array there is the same mechanism, one level down, and shared verbatim with [`commit-author`](commit-author.md)'s identical field -- see that practice's own Install section for the format and the malformed-entry handling. Two-direction tested alongside the existing suite in the same test file.

**2026-09-10: the zone comes from the declared identity, and `precedent.json` carries the exemptions too.** Two changes, one cause. First, this check reported a violation when no `identity.json` sat at `ROOT` -- while a *shared* consuming repo must not have one, for the reason [`commit-author`](commit-author.md)'s Install section gives at length. It now resolves the person's zone through `declared_identity(repo)` -- imported from `precedent_identity`, the module upstream moved it into the same day so that a practice set vendors it too, falling back to `precedent_resolve` only for an older vendored engine -- and reports SKIPPED (exit 2) where nobody is declared: with no person, there is no zone for a commit's offset to be wrong against, and that is not a violation. Second, the per-repo exemption list above was still read from `identity.json` alone here, though `commit-author`'s copy of the same mechanism learned to read `precedent.json` as well on 2026-09-07 -- so one incident, grandfathered once, stayed exempt from the author check and kept failing the offset check, in exactly the shared repos that have nowhere else to declare it. Both files are read now, as that practice already does.
