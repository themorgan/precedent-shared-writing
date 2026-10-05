---
slug:        dated-download-names
title:       A document handed to someone to download carries its date at the end of its name, just before the extension
tier:        on-demand
severity:    default
applies_to:  ["**"]
applies_to_why: "No locus: the moment is a hand-over, a SendUserFile call or an attachment, and nothing about it is written to the tree. Reached through the occasion index, and enforced at the call itself by the hook. Decided: 2026-10-05, when the practice landed."
occasion:    "handing a person a document to download -- a Word file, a PDF, a spreadsheet, a deck"
gates:       []
index_clause: "the date goes at the end of its name: Name-2026-12-31.docx"
checked_by:  tools/checks/check_dated_download_names.py
ships:       ["tools/dated_name.py"]
defines:     []
status:      active
supersedes:  []
overrides:   null
added:       2026-10-05
approved_by: "Morgan F, 2026-10-05, at his own request, in his words: \"whenever it gives the user a doc to download, always put the date in the filename in the format of \\\"-2026-12-31\\\" or \\\" - 2026-12-31\\\" at the end of the filename before the extension. Add a Practice for this or add it to the relevant practice - and add a check for this.\" (strength: decided). Revised the same day at his own request, so a document the repository keeps is dated too: \"Yes, so it's consistent and has the same file name, and also so it's super clear which vesion/when is it from.\" (strength: decided)"
---
## Rule
**Every document you hand someone to download has the date at the end of
its name, right before the extension**, in one of two forms:

```
Joseph Manuscript-2026-12-31.docx
Joseph Manuscript - 2026-12-31.docx
```

The date is the day you hand it over, in the reader's own time zone, never
the container's. It goes last: `report-2026-12-31-final.pdf` and
`report_2026-12-31.pdf` do not count.

This covers a Word file, a PDF, a spreadsheet, a CSV, a deck, an e-book --
anything the reader saves and opens somewhere else. It does not cover an
image, a web page shown in the side panel, or source code.

**A document the repository keeps for download is dated the same way**,
with the day it was last built: `book/output/manuscript-2026-10-05.docx`.
The copy in the repository and the copy you are sent then have the same
name, and either one says when it is from. A rebuild that changes the
document saves it under the new day's name and deletes the older copy, so
the folder holds one copy of each document; a rebuild that changes nothing
leaves the file and its date alone. Because the name moves, link to the
folder (`book-joseph/output/`), never to the file.

A one-off built straight into the scratchpad is simply saved under its
dated name. A file whose name you cannot change gets a dated copy to send:

```
python3 tools/dated_name.py some/file.docx --to <scratchpad>
```

**Claude Code refuses to send an undated document.** A `PreToolUse` hook on
`SendUserFile` runs `tools/dated_name.py --hook`, which stops the call and
prints the command that makes the dated copy.

## Detail
[`tools/dated_name.py`](../tools/dated_name.py) is the one place the format lives: the list of
document extensions, the two accepted forms, and the date, which it takes
from [`tools/precedent_time.py`](../tools/precedent_time.py) so it is the reader's day and not UTC's.
`--check NAME...` answers whether names pass, for any script that wants to
ask before it saves.
A builder that keeps a document in the repository calls
`dated_name.current(base)` to find the copy there now and
`dated_name.replace(base, date)` for where the rebuild goes and which older
copies to delete, where `base` is the name without a date.

The hook is wired by hand in each repository's `.claude/settings.json`,
because a practice set ships files and not harness wiring:

```
{"matcher": "SendUserFile", "hooks": [{"type": "command",
  "command": "python3 $CLAUDE_PROJECT_DIR/tools/dated_name.py --hook"}]}
```

## Why
A downloads folder fills with copies of the same document from different
days, and once the browser has added "(1)" and "(2)" nobody can tell which
is the latest without opening each one. A date in the name sorts them and
answers that at a glance.

## Story
2026-10-05: Morgan, after a day of rebuilding the Joseph Word files several
times over, asked that every document he is handed carry its date at the
end of its name, and that something check it. The first version kept the
committed copies under fixed names and dated only the copy sent. He asked
the same day for the committed copies to carry the date too, "so it's
consistent and has the same file name, and also so it's super clear which
version/when is it from."

## Install
[`tools/checks/check_dated_download_names.py`](../tools/checks/check_dated_download_names.py) confirms, wherever
[`tools/dated_name.py`](../tools/dated_name.py) is vendored, that the tool parses, cites this
practice and still tells dated names from undated ones, that a
repository with a `.claude/settings.json` wires the `SendUserFile` hook
above, and that every document the repository tracks has a dated name. It is SKIPPED where the tool is not vendored. A document handed over
any other way -- attached to an email, linked in the repository -- is
session judgment.
