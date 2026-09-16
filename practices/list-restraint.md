---
slug:        list-restraint
title:       Use a list only when the content is actually a list
tier:        on-demand
severity:    default
applies_to:  ["**/*.md"]
occasion:    "about to format connected prose as bullet points"
gates:       []
index_clause: "don't reformat connected reasoning as bullet fragments"
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-08-31
approved_by: "Morgan F, migrated from RepoPersonalPreferences by the private-set migration session"
---
## Rule
A bulleted or numbered list is sometimes reached for because it looks more organized than the same content written as connected sentences, not because the content is a set of discrete, parallel items. Ask: does this content name several parallel, roughly interchangeable items the reader will scan or reference individually (a list), or does it make one continuous point with reasoning tying it together (prose)? When genuinely unsure, prose is the safer default.

## Detail
A genuine enumeration a reader will scan or reference individually -- ingredients, steps in a procedure, a set of options, a checklist -- is never what this rule targets. What it catches: content with connective logic ("because," "so," one point building on the last) reformatted as bullet fragments that erase those connections. The tell: reading the bullets back as plain sentences joined by ordinary connectives loses nothing and reads more naturally.

## Why
A paragraph that could have been a list costs the reader little; a list that erases an argument's reasoning costs more.

## Story
Migrated here from RepoPersonalPreferences by the phase-3 private-set
migration. That pack recorded no dated incident; it named a pattern, and
this Story records the pattern rather than inventing an origin.

The pattern is a list reached for as a reflex, because it looks more
organized and thorough than the same content as connected sentences. The
tell given is a good one: reading the bullets back as plain sentences joined
by ordinary connectives loses nothing, which means the bullets were never
carrying anything the prose did not.

Two limits keep the rule honest. It has no argument with a genuine
enumeration -- ingredients, steps, options, findings, a checklist -- and
says so at length, because a rule against lists would be a worse rule than
no rule. And it admits outright that nothing can tell from the outside a
five-item enumeration from a three-sentence argument chopped into three
bullets; both are a list on the page. Hence the default: when genuinely
unsure, prose, since a paragraph that could have been a list costs the
reader little while a list that erases reasoning costs more.

**Moved to `precedent-team-writing` on 2026-09-09**, from `precedent-team-maintainers`, in the subject split recorded in BestPractice's own history (2026-09-09) -- its TODO.md has since moved that content into per-item files, so the old anchor no longer resolves. The rule is about the craft of writing for a human reader, which is nobody's single team's business: a document project needs it as much as a software repo. While it lived in a set named for the people who happened to write it, neither could reach it without also taking twenty-odd rules about syncs, gates and branch setup. The copy left behind is `status: deduplicated` and points here; nothing was deleted and the rule was never out of force for a moment (`spec/MOVING_PRACTICES.md`, land first, deduplicate second).

## Install
No mechanical check: telling "connected reasoning reformatted as bullet fragments" apart from "a genuine enumeration a reader will scan individually" is precisely the semantic call the rule's own Detail section describes -- reading the bullets back as plain sentences and judging whether the connective logic survives. No syntax-level property of a markdown list captures that.
