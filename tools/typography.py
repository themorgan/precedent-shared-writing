#!/usr/bin/env python3
"""typography.py -- the one place plain Markdown typing becomes finished
typography, for every format built for an outside reader.

# practice: curly-quotes

Markdown is written with plain keys: straight quotes, a hyphen, and two
hyphens for a long dash. Nothing in a Markdown file has to change. Real
dashes and curly quotes typed into one are fine too, and pass through
untouched. The conversion happens when a builder makes something an
outside reader sees -- a Word document (create_word_doc.py), a web page,
whatever format comes next -- and every such builder calls smarten() here
rather than carrying a copy of its own (Morgan, 2026-10-13: "whenever we
format it for external use, such as creating a [Microsoft] Word document or on a
website, then the double dashes should always become an M dash").

The rules:
  "--" and "---"        always an em dash, spacing kept as typed
  1990-2000, 9-5,       a hyphen between two numbers that make a range is
  pages 10-20, 3:00-5:00  an en dash
  2026-10-13, 555-123-4567, PR-173, B-52
                        stay hyphens: a hyphen inside a run of three or more
                        number groups (a date, a phone number) or next to a
                        letter is never a range
  "word" / it's         curly quotes, opening after a space, an opening
                        bracket or a dash, closing anywhere else
A range in words ("Monday-Friday") keeps its hyphen: telling it from an
ordinary hyphenated word takes judgment a script cannot make, so a writer
who wants the en dash there types it.

Code is never changed: a code span (`--check`, `it's`) keeps every
character, and a builder sets a fenced code block as typed without calling
smarten() on it at all, because in code "--" and "-" mean something
exactly. A web link's address and a backslash-escaped character are never
changed either.
A caller that has already pulled links out of the text marks an address
with LINK_OPEN before it and LINK_MID after it (create_word_doc.py does).

    python3 tools/typography.py "a \\"quote\\" -- 1990-2000"   # prints the result
"""
import re
import sys

LINK_OPEN, LINK_MID = "\x01", "\x02"
EM, EN = "—", "–"
OPENS_AFTER = set(" \t\n([{<" + EM + EN + "-/“‘" + LINK_MID)

# A number: digits, optionally with one decimal, thousands or time part.
_NUM = r"\d+(?:[.,:]\d+)?"
# A hyphen between two numbers, neither of which is joined to a letter,
# another hyphen, or a further number group. The lookarounds are what keep
# 2026-10-13 and 555-123-4567 whole: every hyphen in them touches a
# neighbouring "-digit" group.
RANGE_RE = re.compile(
    r"(?<![\w.,:\-])(" + _NUM + r")-(" + _NUM + r")(?![\w\-]|[.,:]\d)")


def _ranges(segment):
    return RANGE_RE.sub(lambda m: m.group(1) + EN + m.group(2), segment)


def smarten(text):
    """Curly quotes, em dashes for "--"/"---", en dashes for number ranges.
    An asterisk run is looked through, so '**"word"**' opens and closes
    properly."""
    out, prev, i, in_url = [], " ", 0, False
    plain_start = 0          # where the current run of plain text began in `out`
    while i < len(text):
        ch = text[i]
        if ch == LINK_OPEN:
            in_url = True
        elif ch == LINK_MID:
            in_url = False
        if in_url or ch in (LINK_OPEN, LINK_MID):
            out.append(ch)
            prev = LINK_MID if ch == LINK_MID else prev
            i += 1
            continue
        if ch == "`":
            # A code span is code: "--check" and "it's" stay as typed.
            run = len(text) - i - len(text[i:].lstrip("`"))
            close = text.find("`" * run, i + run)
            while close != -1 and close + run < len(text) and text[close + run] == "`":
                close = text.find("`" * run, close + run + 1)
            if close != -1:
                out.append(text[i:close + run])
                prev = "`"
                i = close + run
                continue
        if ch == "\\" and i + 1 < len(text):
            out.append(text[i:i + 2])
            prev = text[i + 1]
            i += 2
            continue
        if text.startswith("--", i):
            run = len(text) - i - len(text[i:].lstrip("-"))
            # Two or three hyphens are a dash; four or more are something
            # else (a rule drawn in text) and stay as typed.
            out.append(EM if run <= 3 else "-" * run)
            prev = out[-1][-1]
            i += run
            continue
        if ch == '"':
            ch = "“" if prev in OPENS_AFTER else "”"
        elif ch == "'":
            ch = "‘" if prev in OPENS_AFTER else "’"
        out.append(ch)
        if ch != "*":
            prev = ch
        i += 1
    return _apply_ranges("".join(out))


# What the range step never touches: a marked link address, and a code span
# (a run of backticks, its text, the same run again).
PROTECTED_RE = re.compile(
    LINK_OPEN + "[^" + LINK_MID + "]*" + LINK_MID + r"|(`+)(?!`).*?(?<!`)\1(?!`)",
    re.S)


def _apply_ranges(text):
    """Number ranges, everywhere but inside a marked link address, a code
    span, or right after a backslash escape."""
    done, at = [], 0
    for m in list(PROTECTED_RE.finditer(text)) + [None]:
        part = text[at:m.start() if m else len(text)]
        # Keep an escaped hyphen ("1990\-2000") a hyphen: split it out.
        bits = re.split(r"(\\-)", part)
        done.append("".join(x if x == "\\-" else _ranges(x) for x in bits))
        if m is None:
            break
        done.append(m.group(0))
        at = m.end()
    return "".join(done)


if __name__ == "__main__":
    print(smarten(" ".join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read()))
