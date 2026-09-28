# precedent-shared-writing — a shared practice set

**Renamed 2026-09-19 from `precedent-team-writing`** — the `team` level
itself was renamed `shared`; see
[practices/source-naming.md](https://github.com/alex137/BestPractice/blob/staging/practices/source-naming.md)'s
Story.

This is **precedent-shared-writing's own space** — a set for one kind of work or one team, holding the
conventions its members have agreed on. Its
[`precedent-source.json`](precedent-source.json) says what it is,
including that this repository is public.

## What's here

| File | What it's for |
|---|---|
| [`approvers.json`](approvers.json) | The list of people who can say yes to a change here. Run `python3 tools/build_codeowners.py` after editing it: that writes `CODEOWNERS`, which is what actually makes GitHub require an approver's review. Never hand-edit `CODEOWNERS`; it is regenerated wholesale. |
| [`practices/`](practices/) | This set's practices, one file each — [MAP.md](MAP.md) lists them. |
| [`leak-blocklist.txt`](leak-blocklist.txt) | The private-term blocklist for Precedent's leak gate — client names, code words, anything that must never reach a public repo. Fill it in; see the file's own header for the format and the two environment/git settings that switch it on. |
| `tools/` | The vendored engine (`build_views.py`, `build_codeowners.py`, `precedent_gate.py`, `precedent_paths.py`, `precedent_show.py`, `split_practices.py`, `routing_scope.json`, `precedent_vendor_engine.py`) — never hand-edit these; refresh them with `python3 tools/precedent_vendor_engine.py refresh <bestpractice-clone>` (see `tools/ENGINE_MANIFEST.json` and [`spec/BOOTSTRAP_NEW_SOURCES.md`](https://github.com/alex137/BestPractice/blob/staging/spec/BOOTSTRAP_NEW_SOURCES.md#the-vendored-engine)'s "The vendored engine"). The engine files are named rather than linked because they arrive when the set is bootstrapped; nothing under `tools/` exists in this skeleton yet. |

## Writing practices

Each practice is one file under `practices/`, in Precedent's phase-1
format — frontmatter plus `## Rule` / `## Detail` / `## Why` / `## Story` /
`## Install`. The full spec is
[Precedent's `spec/PRACTICE_FORMAT.md`](https://github.com/alex137/BestPractice/blob/staging/spec/PRACTICE_FORMAT.md);
[`practices/draft-marker.md`](practices/draft-marker.md) in this repo shows the shape directly.

## Approval

An assistant proposes a practice and asks an approver to look at it — a
review on this repo, so the approval *is* the record. `approvers.json`
holds the list `tools/precedent_land.py` checks a proposer's name against;
adding or removing an approver is itself a change to that file, so it
needs a current approver's own agreement, which is what stops someone
quietly adding themselves.

If the approver is also the person proposing the change — for a small
team, it usually is — there's no waiting: their "yes" in the conversation
*is* the approval, landed directly in the same sitting.

**Nobody is ever blocked waiting for a team approval to *use* a practice
right now.** Put it in your own individual set instead, where it applies
immediately with nobody's permission; offering it to the team is a
separate step, whenever it suits you.
