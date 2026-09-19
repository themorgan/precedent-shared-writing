---
slug:        draft-marker
title:       Temporary in-document notes get a marker loud enough to catch on a skim
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "leaving a placeholder or fill-in-later note mid-draft"
gates:       []
index_clause: "wrap a draft placeholder in ➡️ TEXT ⬅️, bold and all caps"
checked_by:  tools/checks/check_draft_marker.py
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-08-31
approved_by: "Morgan F, migrated from RepoPersonalPreferences by the private-set migration session"
---
## Rule
A temporary note left mid-draft -- a placeholder to fill in later, a reminder to the future editor, an "insert X here" -- is only safe to leave in a document if whoever next looks at it actually notices it. Wrap it in a marker built to fail a skim on purpose: `**➡️ TEXT OF THE NOTE ⬅️**` -- bold, all caps, a directional arrow hugging the outer edge of the first and last word.

## Detail
Before showing or sharing any document, scan it for the marker specifically -- a text search for the arrow character confirms none remain, cheaper than rereading the whole document.

## Why
Plain caps alone isn't enough: an all-caps placeholder still reads as ordinary body text on a fast scan once the eye has adjusted to a document that already uses bold and caps for other things. Nothing else on the page looks like the arrow marker.

## Story
Migrated here from RepoPersonalPreferences by the phase-3 private-set
migration; the Story is backfilled from that pack's own text, and it records
a real failure.

In a dependent repo -- named only in general terms here, since this text
ships into consuming repos (`private-repo-scrub`) -- a draft still carried
an all-caps fill-in-later placeholder when somebody scanned it quickly
before showing it to someone else. The caps did not register as an alarm;
they read as ordinary body text, and the document got shown anyway.

That is the whole argument for the specific marker. Bold and caps alone stop
working in a document that already uses bold and caps for other things -- the
eye adjusts, and the placeholder becomes texture. The arrows are the
load-bearing part rather than decoration, because nothing else on a page
looks like an arrow hugging the first and last word.

The scan-before-sharing half exists for the same reason: a marker only helps
if something actually looks for it. Grepping for the arrow is cheaper than
rereading the document, and it answers the one question that matters before
sharing.

**Moved to `precedent-team-writing` on 2026-09-09**, from `precedent-team-maintainers`, in the subject split recorded at BestPractice's own [`split-team-sets-by-subject`](https://github.com/alex137/BestPractice/blob/precedent-beta-v01/todo/todo-2026-09-08-split-team-sets-by-subject.md) item, DONE 2026-09-09. The rule is about the craft of writing for a human reader, which is nobody's single team's business: a document project needs it as much as a software repo. While it lived in a set named for the people who happened to write it, neither could reach it without also taking twenty-odd rules about syncs, gates and branch setup. The copy left behind is `status: deduplicated` and points here; nothing was deleted and the rule was never out of force for a moment (`spec/MOVING_PRACTICES.md`, land first, deduplicate second).

## Install
Checked mechanically by [`tools/checks/check_draft_marker.py`](../tools/checks/check_draft_marker.py), scope `tree`, over tracked markdown files. It implements the Detail section's own described check -- a text search for the marker -- rather than a new invention: any `**➡️ ... ⬅️**` sitting in real document prose (not inside backtick code, which is how this practice's own Rule text illustrates the format) is a marker that should have been caught and cleared before the content was committed. Two-direction tested in [`tools/checks/tests/test_draft_marker.sh`](../tools/checks/tests/test_draft_marker.sh), which also confirms the check doesn't misfire on this file's own illustration of the format.
