---
slug:        proportional-emphasis
title:       Length and emphasis scale with a point's actual importance
tier:        on-demand
severity:    default
applies_to:  ["**/*.md"]
occasion:    "reviewing a draft's balance before calling it done"
gates:       []
index_clause: "give a point space matching its importance, not its drafting mood"
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-08-31
approved_by: "Morgan F, migrated from RepoPersonalPreferences by the private-set migration session"
---
## Rule
How much space, prominence, or emphasis a point gets in a document -- a paragraph versus a sentence, a bolded callout versus a plain clause -- should track how important that point actually is, not how much attention it happened to get while drafting. Ask: does the space this point takes up match how much a reader who doesn't already know the material would need it weighted, or does it just reflect how long it took to get the wording right?

## Detail
Overridable on request: if the user explicitly asks for a point to be emphasized, expanded, or called out beyond what its importance alone would warrant, that instruction governs -- this rule only covers emphasis that wasn't asked for. Distinct from keeping list items comparable (parity between neighbors) and trimming over-edited prose (reversing edit-driven growth): this is about calibrating weight to importance throughout a document, in prose and lists alike.

## Why
A minor caveat that grows to three paragraphs and bold text reads, to anyone but the person who just wrote it, as if it were a central claim -- the document ends up structured by the mood of composition instead of by what the reader needs weighted.

## Story
Migrated here from RepoPersonalPreferences by the phase-3 private-set
migration. No dated incident was recorded; the rule names a drift and this
Story records it as such.

The drift is that a document ends up structured by the order and mood of
composition rather than by what a reader needs weighted. A minor caveat that
happened to take three paragraphs and a bold callout to get right reads, to
anyone but the person who just wrote it, as a central claim. The writer
cannot see this, because for them the space genuinely does track effort.

It is the same failure `list-item-parity` names for items in a list,
generalized past lists to prose, sections and emphasis. The test offered is
deliberately about the reader rather than the writer: does the space this
point takes up match how much someone who does not already know the material
would need it weighted, or does it just reflect how long the wording took?

Overridable on request, since a deliberate decision to give a minor point
outsized emphasis is a legitimate thing to ask for.

**Moved to `precedent-team-writing` on 2026-09-09**, from `precedent-team-maintainers`, in the subject split recorded in BestPractice's own history (2026-09-09) -- its TODO.md has since moved that content into per-item files, so the old anchor no longer resolves. The rule is about the craft of writing for a human reader, which is nobody's single team's business: a document project needs it as much as a software repo. While it lived in a set named for the people who happened to write it, neither could reach it without also taking twenty-odd rules about syncs, gates and branch setup. The copy left behind is `status: deduplicated` and points here; nothing was deleted and the rule was never out of force for a moment (`spec/MOVING_PRACTICES.md`, land first, deduplicate second).

## Install
No mechanical check: whether a point's space "matches how much a reader who doesn't already know the material would need it weighted" requires judging the material's own substance, which is exactly what the rule's own test asks a person (or a session) to do -- there's no structural proxy (paragraph count, bold density) that reliably stands in for actual importance.
