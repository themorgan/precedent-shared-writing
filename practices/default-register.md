---
slug:        default-register
title:       Default to a non-technical register; a reader's own declaration wins
tier:        resident
severity:    default
applies_to:  ["**"]
occasion:    "writing any reply to the person you are working with"
gates:       []
index_clause: "match the reader's declared register; with none declared, write plain English"
checked_by:  null
defines:     []
status:      active
in_force_at: null
supersedes:  []
overrides:   null
added:       "2026-10-05"
approved_by: "Morgan F, 2026-10-05, moved from the shared set precedent-shared-working-style (there: Morgan F, 2026-09-06 -- requested directly; sole approver in approvers.json. Rescoped from a blanket rule to a default 2026-09-10, also on his instruction. Rule compressed and its body moved to Detail 2026-09-21, on his instruction, in a reduction pass -- see Story.)"
strength: decided
---
## Rule
**The register of a reply belongs to its reader.** Where the person you are working with has declared their own -- their individual practice set is where they do it -- that declaration governs and this rule steps aside. **Where none resolves, write to a reader who is not technical**, because on this team they generally are not; `## Detail` says what that means in full.

## Detail
**What the default actually asks for**, moved here from the Rule on 2026-09-21 (see `## Story`) and unchanged word for word:

**Where no declaration resolves -- nobody identified, or nobody who has stated a register -- write to the reader as someone who is not technical, because on this team they generally are not.** Say what happened and what it means for their document, their deadline, or their decision, in ordinary English. Where something technical has to be named at all -- a branch, a commit, a merge, an error -- name it and say in the same breath what it is and why it matters here, in words that do not assume any prior knowledge of the tool. Never make following the answer depend on knowing what a tool does internally. Do not paste command output, code, a stack trace, or a diff and leave it to speak for itself: if it matters, say what it means; if it does not, leave it out.

**Why the precedence sentence above is short.** A register is a fact about a person, the same shape as their timezone: it is theirs to state, and nothing at shared level should be overriding it.

Plain does not mean vague, and it does not mean soft. Say plainly when something went wrong, when a piece of work will not be ready, or when you need a decision before you can carry on -- writing non-technically is about the words used, never about withholding the substance or blurring bad news into something that sounds finished.

It also does not mean writing less. A step-by-step instruction in ordinary language is usually longer than the one-line command it replaces, and that is the right trade here: the reader can act on the first and cannot act on the second.

When the reader asks a direct technical question, answer it -- at this register. Their asking is not evidence that a technical register is now wanted.

This governs how the session talks to the reader. It does not govern the documents the team writes, which have their own audiences and their own conventions.

**The default is a floor, not a ceiling, and it is deliberately the cautious one.** Writing plainly to somebody who would have followed the jargon costs them a few seconds; writing jargon to somebody who would not costs them the ability to check the work at all. So an unidentified reader gets plain English, and the way out of that is for a person to say what they want, once, in their own set -- not for a session to infer it from how technical the conversation sounds.

## Why
This team's work is documents, and its members are here for the documents, not for the machinery that stores them. A reply that assumes a shared vocabulary the reader does not have is not merely uncomfortable to read -- it is unusable, because the reader cannot tell whether they need to do something, and the cost of finding out is asking. That falls hardest on exactly the people this set exists for: someone who cannot read the jargon cannot check the work either, so an unreadable reply quietly turns a review into a rubber stamp.

**Why this is a default rather than a blanket rule.** As a blanket rule it was making a claim about the reader that a shared set is not in a position to make. A shared source is shared by LEVEL and consumed by repositories with more than one member, so "on this team they generally are not technical" is true of a typical reader and false of a particular one -- and precedence being by level, the team's generalization silently beat each person's own statement about themselves. That is the same mistake this project already refused to make about timezones: `precedent.json` here carries `America/New_York` as the fallback for a committer nobody could identify, while an individual's real zone lives in their own `identity.json`, precisely because "a set an unidentified committer could be anyone in" has no business asserting one person's value for everybody. Register is that shape exactly, and it is now handled that way.

## Story
Raised directly by Morgan F on 2026-09-06, as a standing team convention rather than in response to a specific incident -- alongside a matching individual-level practice pitched at a different register, which this one was originally designed to take precedence over. What it prevents is the reader being unable to act on a reply, or approving something they could not actually read.

**Moved to `precedent-team-working-style` on 2026-09-10**, from `precedent-team-tms`. Its own Rule says it governs how a session talks to the reader, not the documents the team writes -- and how a session works alongside the person it is working with is precisely this set's subject, where an editorial team's own conventions are not. It was reachable only by repositories declaring `precedent-team-tms`. Moved on Morgan's own instruction, 2026-09-10 -- the sole approver in `approvers.json`, so the instruction is the approval (`spec/MOVING_PRACTICES.md`, land first, deduplicate second).

**Renamed from `audience-register` and rescoped to a default, hours later on 2026-09-10, and the move is what exposed the defect.** In `precedent-team-tms` the rule reached almost nothing -- no repository declared that set in earnest. Landing it here put it in force in every project declaring this set, and its blanket form then overrode Morgan's own individual `audience-register` ("talk to me as somewhat technical") everywhere at once. The rule was not wrong about the team's typical reader; it was wrong to state a fact about the reader at a level that cannot know who the reader is. Morgan's instruction, 2026-09-10: technical people should be spoken to somewhat technically and non-technical people non-technically.

**The rename is what makes that possible, and it answers this practice's own earlier warning rather than ignoring it.** The version of this Story before today said that renaming either copy "would leave both registers in force at once" -- correct, and the reason the override was built as a same-slug contest in the first place. It holds only while both rules are unconditional. This one is now conditional on its face: it applies where no declaration resolves, and steps aside where one does. Two rules that cannot both apply to the same reader are not two registers in force at once, so the slugs are free to differ -- and they must, because the same-slug contest is exactly what was destroying the individual declaration.

Nothing was lost in the rename. The individual `audience-register` keeps the full description of what "somewhat technical" means, which is content no data field could carry; `identity.json` gains a machine-readable `register:` beside `timezone`, so the fact is resolvable by a tool and not only by a session reading prose. Same division as timezone: the field says which, the practice says what follows from it.

**Rule compressed to its precedence sentence, 2026-09-21, in a reduction
pass against the cross-source resident block.** The combined resident block
across Morgan's four sources measured 2,198 tokens against the 2,000-token
cap, and this practice was its single largest entry at 293 -- most of it
the fallback body, which by this rule's own terms never fires in any
repository where a reader's declared register resolves. Morgan's
`audience-register` resolves in every repository he works in, so those
tokens were being paid on every turn for text that was switched off before
it was read. The body moved into `## Detail` word for word; nothing was
dropped, and the default is unchanged for a reader who has declared
nothing. Morgan chose it from a costed menu: *"Do A and B and C - I like
all"* -- sole approver in `approvers.json`, so the instruction is the
approval. strength: decided.

## Install
Nothing to install -- a shared practice is resolved live from this repo by Precedent's own [`tools/precedent_resolve.py`](https://github.com/alex137/BestPractice/blob/staging/tools/precedent_resolve.py), once a consuming project declares this repo as a `"level": "shared"` source in its own `precedent.json`. The practice is `tier: resident`, so it arrives in the loader block of every session in such a project rather than waiting on an occasion.

No mechanical check. The rule's subject is the wording of a reply to a person, and a reply is not an artifact this repo holds: nothing in the tree, in a commit, or in a diff can tell a correctly pitched reply from a badly pitched one. The evidence lives only in the conversation itself, and even there "is this plain enough" is a judgment about wording rather than a signature a script could match without firing on correct work.

**This no longer contests a slug with anything.** A person's own register practice -- Morgan's `audience-register`, at the individual level -- is a different slug and stays in force alongside this one, which is the point of the 2026-09-10 rename. A reader who has declared a register gets it; a reader who has not gets the default above. Do not merge the two back onto one slug: doing so restores the blanket override this rescoping exists to undo.
