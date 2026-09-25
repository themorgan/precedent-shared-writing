---
slug:        name-the-branch
title:       Name the branch, never "the base branch"
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "naming a branch in a reply, a commit message, a pull request, or a GitHub comment"
gates:       []
index_clause: "name a branch literally (precedent-beta-v01, main), never \"the base branch\" or \"the default branch\""
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       "2026-09-23"
approved_by: "Morgan F, 2026-09-23, moved from the individual set precedent-individual (there: Morgan F, 2026-09-11)"
in_force_at: null
strength: decided
---
## Rule
When you tell me anything about a specific branch, **name it**: `precedent-beta-v01`, `main`, `claude/nice-newton-5o72z0`. Never a role-word standing in for the name — "the base branch", "the default branch", "the beta branch", "the working branch", "upstream's branch", "its base". This holds everywhere you write to me or to the record: replies, commit messages, pull request titles and bodies, and comments posted to GitHub.

Where the statement is genuinely **generic** — a rule that holds for any repository, a script's docstring describing the `BASE` argument somebody passes it — the role-word is the correct word and this rule does not reach it. The test is whether I could sensibly ask "which one?". If I could, the name belongs there.

## Detail
The cost is asymmetric, which is why this is worth a rule rather than a preference. Writing the name costs nothing. Reading a role-word costs me a resolution step I cannot verify, on exactly the question I care most about — whether something I depend on has moved.

`alex137/BestPractice` is the case that makes it concrete: its configured **default** branch is `main`, and the branch all the work happens on is `precedent-beta-v01`. So in that repository the role-word and the name point at *different branches*, and a reader who resolves "the base branch" the obvious way gets the wrong answer. "Red on the base branch" reads as "`main` is red" — alarming and false — when the true statement was "`precedent-beta-v01` is red".

A wrong resolution is also **silent**. Nothing corrects it, no check fires, and I carry the wrong belief until something forces it into the open. That is the same shape as every other failure this set keeps recording: not a loud error, a confident wrong answer nobody had reason to re-examine.

[`go-merge`](https://github.com/alex137/BestPractice/blob/staging/practices/go-merge.md) already requires the merge target to be said out loud before a merge, and its own Story records why — a pull request in that repository once merged silently into the wrong branch. This rule is that same requirement, extended from the one moment before a merge to every time a branch is mentioned at all. Naming it only at the merge is naming it after every decision I made from the summary.

## Why
Because the role-word puts the work on the wrong side. I asked a question about a private repository's gate and got back a report about "the base branch" being red; the branch in question was `precedent-beta-v01`, but nothing in the sentence said so, and the branch I would actually worry about — `main` — was never involved. The sentence was true and I could not tell.

There is no upside to trade against. A branch name is one token, it is unambiguous, and it is clickable in the places these reports end up.

## Story
2026-09-11. A session reported a red check on `alex137/BestPractice` as "red on BestPractice's base branch", in a summary that was otherwise accurate — the check was `parallel-artifact-ledger`, it was pre-existing, and it had been reproduced on `precedent-beta-v01` with the contributing branch absent. None of that survived the phrasing. Morgan, verbatim:

```text
PLEASE DO NOT USE LANGUAGE LIKE "ON THE BASE BRANCH..." BECAUSE IT WORRIES ME THAT MAIN MIGHT BE CHANGED ON BESTPRACTICE. ONLY USE LANGUAGE WITH THE EXPLICIT BRANCH NAME, precedent-beta-v01.
```

The same session had already been careful about this in the place it is conventionally required — it confirmed each merge target out loud, against each pull request's own `base` field rather than a repository default, per `go-merge`. So the discipline was present at the merge and absent in the prose around it, which is the gap this rule closes.

## Install
No mechanical check, and this one resists it for a specific reason rather than a general one: **the forbidden phrase is correct in this repository's own text.** `fresh-before-write`'s Rule says a branch may be "missing commits from `origin/<the base branch>`", which is a true statement about any repository and names no branch on purpose. `bootstrap/freshness-guard.sh`'s header documents its `BASE` argument the same way, and says in as many words that BestPractice's configured default is not its base — prose that exists precisely to prevent this confusion.

A check matching "the base branch" would fire on all of it. That is the failure `my-identity-is-not-private`'s Story records from the other direction: a gate whose findings cost real, correct content is a gate people learn to skip, and it takes the findings that mattered down with it. Distinguishing "a specific branch is meant here" from "this is a statement about any repository" is a judgment about the sentence, not a pattern in it.

What stands in for a check is the `resident` tier: this rule is in the loader block of every session rather than fetched when something reminds a session to look for it, because the moment it applies is every time a branch is mentioned, with nothing to trigger a lookup.
