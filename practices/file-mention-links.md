---
slug:        file-mention-links
title:       In chat and PR/commit text, every file mention is a clickable link
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "mentioning a repo file in a chat reply, PR description, or commit message"
gates:       ["reply"]
index_clause: "every file mention in chat or PR/commit text is a live GitHub link"
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-08-31
approved_by: "Morgan F, migrated from RepoPersonalPreferences by the private-set migration session"
---
## Rule
A file gets linked the first time it's mentioned inside a document actually committed to the repo, using a relative link, leaving a filename inside a code span alone. Neither default holds on two other surfaces -- a chat reply, and a PR description, issue, or commit message aimed straight at the host -- since neither is part of the repo tree and a relative link doesn't resolve there. On those two surfaces only: every mention of a specific file is a clickable, absolute URL to that file, staying inside its code span rather than growing a separate marker.

## Detail
Which branch to link: an open PR's own head branch while it's still open, the default branch once merged or when the reply isn't tied to a particular PR. Where a harness offers a blocking turn-end hook, this is the one part of the documentation-link conventions worth enforcing mechanically -- reading the closing reply before a turn ends and blocking on an unlinked mention of a real, tracked file. Only the final contiguous run of text needs checking, not the whole turn: progress narration written between tool calls earlier in a turn was never meant as a citable deliverable the way the closing reply is.

## Why
A reader skimming a long reply or PR body has no "first mention" to scroll back to -- they want whichever mention is in front of them to work.

## Story
Migrated here from RepoPersonalPreferences by the phase-3 private-set
migration; the Story is backfilled from that pack's own text, and the
incident is about a rule that could not survive on good intentions.

The rule was originally written as session habit, and the same direct ask
had to be made twice before it was mechanically enforced -- the habit kept
lapsing in exactly the way a promise to remember predicts. That second ask
is what bought the hook: a turn-end checkpoint that reads the closing reply
about to be sent and blocks it if a real tracked file's basename appears
unlinked.

Building the check produced a second, smaller finding worth keeping. The
first version examined the whole turn rather than the closing reply, and the
first time it ran for real it flagged routine progress narration written
between tool calls -- "now let's update X" -- instead of anything in the
actual summary. Narration between tool calls was never meant as a citable
deliverable the way the closing reply is, so the check was narrowed to the
final contiguous run of text.

Two limits are stated rather than papered over. Only the chat-reply surface
is enforced; a pull request description or commit message is not text a
turn-end hook can see before it is posted, so those still ride on habit. And
the check is a heuristic that can occasionally flag a mention never meant as
a reference to this repo -- accepted deliberately, since clearing a false
positive costs exactly what complying costs, which is adding a link.

**Moved to `precedent-team-writing` on 2026-09-09**, from `precedent-team-maintainers`, in the subject split recorded in BestPractice's own history (2026-09-09) -- its TODO.md has since moved that content into per-item files, so the old anchor no longer resolves. The rule is about the craft of writing for a human reader, which is nobody's single team's business: a document project needs it as much as a software repo. While it lived in a set named for the people who happened to write it, neither could reach it without also taking twenty-odd rules about syncs, gates and branch setup. The copy left behind is `status: deduplicated` and points here; nothing was deleted and the rule was never out of force for a moment (`spec/MOVING_PRACTICES.md`, land first, deduplicate second).

## Install
No mechanical check: the surfaces this rule governs -- a chat reply, a PR description, an issue, a commit message -- aren't content this repo's own tree contains, so there's nothing here to scan. The practice's own Detail section names the one place this is worth enforcing mechanically: a harness's blocking turn-end hook reading the closing reply, which is a property of the harness, not of this repo.
