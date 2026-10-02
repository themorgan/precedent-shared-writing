---
slug:        rule-links
title:       A mentioned rule, item, or destination is always a link
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "naming a file, branch, doc or anything with a destination, in a doc, reply, PR or commit"
gates:       ["reply"]
index_clause: "link it on first use; files as GitHub links, branches to tree view; docs by name"
index_required: true
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   doc-references-are-links
added:       2026-08-31
approved_by: "Morgan F, migrated from RepoPersonalPreferences by the private-set migration session. Absorbed doc-link-text, file-mention-links and branch-links on 2026-10-01, in the reduction pass Morgan approved that day: \"Question 3 - all are great, approved\" (strength: decided)."
strength:    decided
---
## Rule
Anything mentioned that has a destination gets a link to that destination, the first time it's mentioned -- in any document in the repo, a commit message, a PR description, and a reply in chat, which is the one people forget. Naming a thing and leaving the reader to go find it costs the writer a few seconds and the reader a search every single time.

Three cases have a form of their own:

- **A file named in a chat reply, PR description, issue or commit message** is a clickable, absolute GitHub URL at every mention, not only the first, because a relative link does not resolve off the repo tree. The link wraps the file's code span. Link an open PR's own head branch while it is open, and the default branch once it is merged or when the reply is tied to no PR.
- **A git branch named anywhere** -- running text, a status update, a decision note, not only a files-touched footer -- links to its tree view on the host that repo lives on.
- **A document's link text is its name**: `[the Glossary](GLOSSARY.md)`, never `[GLOSSARY.md](GLOSSARY.md)`. The href stays the real `.md` file.

`## Detail` has the specifics.

## Detail
What has a destination: a file in the repo (a relative markdown link, never a bare backticked name); a named rule of this or another practice set (its permanent slug and anchor, never a positional number, which moves whenever the document is reorganized); a git branch (its tree view, below); a commit (the commit page, short SHA as the link text); a pull request or issue (its page -- not every host auto-links a bare `#43` inside repo markdown); a service, tool, spec, or documentation page named in prose (its canonical page).

Link a thing the first time a given document or reply names it, then use the plain name after that -- this is about the reader being able to get there, not about maximizing link density. Inside a document committed to the repo, a URL, path, or filename inside a code span or code block is a value, not a reference, and stays unlinked.

**Files in chat, PR and commit text.** A chat reply, and a PR description, issue, or commit message aimed straight at the host, are not part of the repo tree, so a relative link does not resolve there and the first-use default does not hold. On those surfaces only, every mention of a specific file is an absolute URL, and it stays inside its code span rather than growing a separate marker -- the code-span exception above is for documents committed to the repo. Where a harness offers a blocking turn-end hook, this is the one part of the documentation-link conventions worth enforcing mechanically -- reading the closing reply before a turn ends and blocking on an unlinked mention of a real, tracked file. Only the final contiguous run of text needs checking, not the whole turn: progress narration written between tool calls earlier in a turn was never meant as a citable deliverable the way the closing reply is.

**Branches.** A branch in some other repo a reply happens to mention gets linked on that repo's host, not this one's. A bare branch name in backticks or plain prose is the failure this catches.

**A document's link text is its name** -- its title, or the plain name people call it by, as in `[the repository map](MAP.md)`. The name is the document's own `# H1` heading where it has one, lowercase and folded into the sentence like any other noun, not Title Cased just because the heading is. A document with no heading of its own (a generated index, a data file) keeps its filename as the text; there is no name to substitute. Retitle only the anchor text, never the surrounding sentence's flow. Two links to the same document one paragraph apart each still carry the name form: this governs the shape of the link, not how often it appears.

A rule of any practice set has one canonical citation form: the slug, linked to its anchor. A positional number ("rule 14") is never a citation -- it names where a rule sits today, not which rule it is.

Because this practice replaces universal `doc-references-are-links` (`overrides:`), it carries that practice's other two clauses too: write `≈` for "approximately", never `~` (two tildes on one line render as strikethrough on GitHub); and keep links plain markdown, never a raw HTML anchor for `target=`, which GitHub's sanitizer strips (*as of 2026-08*).

## Why
A reply that says "fixed in the header rule, see the backlog item" is exactly as unhelpful as a document that says it -- a reply is usually more disposable, which is why it needs the links more, not less. This is stricter than a plain doc-references-are-links convention about where the link lands and what counts as mentionable, so it replaces that practice rather than sitting beside it.

A reader skimming a long reply or PR body has no "first mention" to scroll back to -- they want whichever mention is in front of them to work, which is why a file there is linked every time. A branch is a ref, not a path at the current tree, so a rule about files alone never reached it. And `[GLOSSARY.md](GLOSSARY.md)` makes the reader parse a filename as if it were a word in the sentence; docs get names for a reason, and using the name lets the sentence read naturally while the link still does its job.

## Story
Migrated here from RepoPersonalPreferences by the phase-3 private-set
migration; the Story is backfilled from that pack's own text.

The rule generalizes: `branch-links` closed the gap the universal
references-are-links rule leaves for a git branch, and this one closes the
rest and names the principle both are instances of. The surface people
forget is chat -- a reply that says "fixed in the header rule, see the TODO
item" is exactly as unhelpful as a document that says it, and a reply is
more disposable, so it needs the link more rather than less.

There is a real incident behind one detail. The mechanical half fails a
positional citation to one of this set's own rules, since a number names
where a rule sits today rather than which rule it is, while leaving the
file-qualified form alone for documents whose numbering this set does not
control. The first version of that check carried a fixed list of filenames
and produced a false positive against another vendored pack's own numbered
file on 2026-08-29 -- a legitimate citation, correctly formed, flagged
because the check did not know that pack existed. It was rewritten to
recognize the shape generically, so a newly vendored pack needs no update to
the check at all.

The enforcement boundary is stated rather than implied: only the slug half
is checkable. A commit, a pull request number or an external page cannot be
told from ordinary prose without flagging every hex string and product name,
so those ride on the review half of `deep-check` instead of on a gate.

**Moved to `precedent-team-writing` on 2026-09-09**, from `precedent-team-maintainers`, in the subject split recorded at BestPractice's own [`split-team-sets-by-subject`](https://github.com/alex137/BestPractice/blob/staging/todo/todo-2026-09-08-split-team-sets-by-subject.md) item, DONE 2026-09-09. The rule is about the craft of writing for a human reader, which is nobody's single team's business: a document project needs it as much as a software repo. While it lived in a set named for the people who happened to write it, neither could reach it without also taking twenty-odd rules about syncs, gates and branch setup. The copy left behind is `status: deduplicated` and points here; nothing was deleted and the rule was never out of force for a moment (`spec/MOVING_PRACTICES.md`, land first, deduplicate second).

**Absorbed `doc-link-text`, `file-mention-links` and `branch-links` on 2026-10-01**, in the reduction pass Morgan approved that day ("Question 3 - all are great, approved", strength: decided). The four were one principle -- a mentioned destination is a link -- split into four occasion lines that every session paid for. Every instruction of the three moved into `## Detail` and `## Why` above, and this practice took over `file-mention-links`' `reply` gate and its `index_required: true`. Each absorbed file stays, word for word, as `status: deduplicated` with `in_force_at: rule-links`.

## Install
No mechanical check in this set: recognizing that something was "mentioned" in free-form prose, as opposed to a coincidentally similar word, has no reliable syntactic signature to key a check off -- a bare branch name looks like any other backticked token, and telling a doc named by its filename from one named by its title needs the target's own heading. The chat-reply surface for files is the exception named in `## Detail`: a harness's blocking turn-end hook reading the closing reply, which is a property of the harness, not of this repo, and is why this practice declares the `reply` gate. A PR description or commit message is not text a turn-end hook can see before it is posted, so those still ride on habit.
