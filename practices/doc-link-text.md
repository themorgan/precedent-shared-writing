---
slug:        doc-link-text
title:       A doc link's text is the document's name, not its filename
tier:        on-demand
severity:    default
applies_to:  ["**"]
occasion:    "linking to a document in prose, a reply, or a table"
gates:       []
index_clause: "link text is the doc's name -- keep the href as the .md file"
checked_by:  null
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-09-19
approved_by: "Morgan F"
---
## Rule
When `rule-links` puts a link on a mentioned document, the link text is the document's name -- its title, or the plain name people call it by -- never the bare filename. The href still points at the real file. Write `[the Glossary](GLOSSARY.md)` or `[the repository map](MAP.md)`, not `[GLOSSARY.md](GLOSSARY.md)`.

## Detail
The document's name is its own `# H1` heading where it has one place in the reader's flow -- "the Glossary" for `GLOSSARY.md`, "the repository map" for `MAP.md` -- lowercase and folded into the sentence like any other noun, not Title Cased just because the heading is. A document with no heading of its own (a generated index, a data file) keeps its filename as the text; there is no name to substitute.

This changes the text only. The target is still the actual path, exactly as `rule-links` already requires -- a relative link to the file at the repo's current tree. A reader who hovers or clicks still lands on `GLOSSARY.md`; they just aren't made to read the filename twice to get there.

Retitle only the *anchor text*, never the surrounding sentence's flow -- "see the Glossary for the canonical names" reads as prose either way. Two links to the same document one paragraph apart still each carry the name form; this is about the shape of the link, not a first-use/plain-name rule like the rest of `rule-links`.

## Why
`[GLOSSARY.md](GLOSSARY.md)` makes the reader parse a filename as if it were a word in the sentence, twice over -- once in the brackets, once implied by the destination. Docs get names for a reason; using the name in place of the reader lets the sentence read naturally and the link still does its job.

## Story
Raised by Morgan, 2026-09-19: across two of his own private projects the habit had been to link a document as its own filename -- `[GLOSSARY.md](GLOSSARY.md)`, `[MAP.md](MAP.md)` -- everywhere it was mentioned, because that was the quickest thing to type once `rule-links` said "link it." The href was always right; only the visible text was ever the filename standing in for the name.

This is the same shape of gap `branch-links` closed for a git branch: `rule-links` says destinations get linked, not what the link text should say once they do. Landed directly -- Morgan is this set's proposer and its sole approver (`approvers.json`), so per this repo's own `README.md` ("Approval"), his yes here is the record.

## Install
No mechanical check: telling "a doc named by its own filename" apart from "a doc named by its actual name" needs knowing the target file's own title, which the same free-form-prose limits `rule-links` and `branch-links` already note apply here too. Existing links updated in each consuming repo as this practice landed there, not gated as a new check.
