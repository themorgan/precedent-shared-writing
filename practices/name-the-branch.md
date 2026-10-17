---
slug:        name-the-branch
title:       Name the branch, never "the base branch"
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "naming a branch in anything written"
gates:       []
index_clause: "name it literally, never a role-word like 'the base branch'"
checked_by:  null
defines:     []
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-09-23"
approved_by: "Morgan F, 2026-09-23, moved from the individual set precedent-individual (there: Morgan F, 2026-09-11); reworded 2026-10-17 to address any reader rather than one person, meaning unchanged, by the session under Morgan F's delegation of that day (\"Fix the other issues you found including the checks that never run. Tell me what you decide. I will be offline so don't wait for me. Approved, act, and Booked.\")"
strength: decided
---
## Rule
When you tell the person anything about a specific branch, **name it**: `staging`, `main`, `claude/nice-newton-5o72z0`. Never a role-word standing in for the name — "the base branch", "the default branch", "the beta branch", "the working branch", "upstream's branch", "its base". This holds everywhere you write to a person or to the record: replies, commit messages, pull request titles and bodies, and comments posted to GitHub.

Where the statement is genuinely **generic** — a rule that holds for any repository, a script's docstring describing the `BASE` argument somebody passes it — the role-word is the correct word and this rule does not reach it. The test is whether the reader could sensibly ask "which one?". If they could, the name belongs there.

## Detail
The cost is asymmetric, which is why this is worth a rule rather than a preference. Writing the name costs nothing. Reading a role-word costs the reader a resolution step they cannot verify, on exactly the question they care most about — whether something they depend on has moved.

`alex137/BestPractice` is the case that makes it concrete: its configured **default** branch is `main`, and the branch the work lands on is `staging` (named `precedent-beta-v01` until 2026-09-25). So in that repository the role-word and the name point at *different branches*, and a reader who resolves "the base branch" the obvious way gets the wrong answer. "Red on the base branch" reads as "`main` is red" — alarming and false — when the true statement was "`staging` is red".

A wrong resolution is also **silent**. Nothing corrects it, no check fires, and the reader carries the wrong belief until something forces it into the open. That is the same shape as many failures these sets record: not a loud error, a confident wrong answer nobody had reason to re-examine.

The rule for landing work already requires the merge target to be said out loud before a merge, and its own Story records why — a pull request in that repository once merged silently into the wrong branch. This rule is that same requirement, extended from the one moment before a merge to every time a branch is mentioned at all. Naming it only at the merge is naming it after every decision the reader made from the summary.

## Why
Because the role-word puts the work on the wrong side. A person asked about a private repository's gate and got back a report about "the base branch" being red; the branch in question was `precedent-beta-v01`, but nothing in the sentence said so, and the branch they would actually worry about — `main` — was never involved. The sentence was true and they could not tell.

There is no upside to trade against. A branch name is one token, it is unambiguous, and it is clickable in the places these reports end up.

## Story
2026-09-11. A session reported a red check on `alex137/BestPractice` as "red on BestPractice's base branch", in a summary that was otherwise accurate — the check was `parallel-artifact-ledger`, it was pre-existing, and it had been reproduced on `precedent-beta-v01` with the contributing branch absent. None of that survived the phrasing. Morgan, verbatim:

```text
PLEASE DO NOT USE LANGUAGE LIKE "ON THE BASE BRANCH..." BECAUSE IT WORRIES ME THAT MAIN MIGHT BE CHANGED ON BESTPRACTICE. ONLY USE LANGUAGE WITH THE EXPLICIT BRANCH NAME, precedent-beta-v01.
```

The same session had already been careful about this in the place it is conventionally required — it confirmed each merge target out loud, against each pull request's own `base` field rather than a repository default, per `go-merge`. So the discipline was present at the merge and absent in the prose around it, which is the gap this rule closes.

2026-10-17: the rule still spoke as one person ("tell me", "worries me")
three weeks after it moved here from an individual set. The very deep
check of that day found it, and the session reworded the Rule, Detail and
Why to speak of the person and the reader, under Morgan's delegation of
that day ("Fix the other issues you found including the checks that never run. Tell me what you decide. I will be offline so don't wait for me. Approved, act, and Booked."). The meaning is unchanged; the quotation above stays
as he wrote it.

## Install
No mechanical check, and this one resists it for a specific reason rather than a general one: **the forbidden phrase is correct in this repository's own text.** `fresh-before-write`'s Rule says a branch may be "missing commits from `origin/<the base branch>`", which is a true statement about any repository and names no branch on purpose. `bootstrap/freshness-guard.sh`'s header documents its `BASE` argument the same way, and says in as many words that BestPractice's configured default is not its base — prose that exists precisely to prevent this confusion.

A check matching "the base branch" would fire on all of it. That is the failure `my-identity-is-not-private`'s Story records from the other direction: a gate whose findings cost real, correct content is a gate people learn to skip, and it takes the findings that mattered down with it. Distinguishing "a specific branch is meant here" from "this is a statement about any repository" is a judgment about the sentence, not a pattern in it.

What stands in for a check is the occasion index: the rule is `on-demand`, and its index line reaches a session whenever it names a branch in anything written. It was resident when written and moved to on-demand on 2026-09-11, when the resident block went over its cap.
