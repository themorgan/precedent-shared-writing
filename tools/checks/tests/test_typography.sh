#!/bin/bash
# Cases for tools/typography.py (practice: curly-quotes): the one place
# Markdown's plain quotes and hyphens become finished typography for a
# format an outside reader sees. Each case is input -> expected output.
set -euo pipefail
cd "$(dirname "$0")/../../.."
python3 - <<'PY'
import sys
sys.path.insert(0, "tools")
from typography import smarten, LINK_OPEN, LINK_MID
cases = [
    # "--" and "---" are always an em dash, spacing kept as typed.
    ("word--word", "word—word"),
    ("a -- b", "a — b"),
    ("x---y", "x—y"),
    ("1990--2000", "1990—2000"),
    ("a ---- rule", "a ---- rule"),
    # A hyphen in a number range is an en dash.
    ("1990-2000", "1990–2000"),
    ("pages 10-20", "pages 10–20"),
    ("9-5, 3:00-5:00, 2.5-3", "9–5, 3:00–5:00, 2.5–3"),
    # Dates, phone numbers and a hyphen beside a letter stay hyphens.
    ("on 2026-10-13", "on 2026-10-13"),
    ("555-123-4567", "555-123-4567"),
    ("PR-173, B-52, 1-on-1, 10-K", "PR-173, B-52, 1-on-1, 10-K"),
    ("Monday-Friday", "Monday-Friday"),
    # Real dashes and curly quotes already typed pass through.
    ("a — b – c “q”", "a — b – c “q”"),
    # Quotes curl.
    ('a "quote" and it\'s', "a “quote” and it’s"),
    ('**"bold"**', "**“bold”**"),
    # A link address and an escape never change.
    (LINK_OPEN + "https://x/1990-2000--a" + LINK_MID + "t", LINK_OPEN + "https://x/1990-2000--a" + LINK_MID + "t"),
    ("1990\\-2000", "1990\\-2000"),
    # Code is never typography: a code span keeps every character.
    ("run `git push --force` -- now", "run `git push --force` \u2014 now"),
    ("`1990-2000` and 1990-2000", "`1990-2000` and 1990\u20132000"),
    ("``a `b` \"c\" --d``", "``a `b` \"c\" --d``"),
]
bad = [(i, smarten(i), want) for i, want in cases if smarten(i) != want]
for i, got, want in bad:
    print(f"FAIL: {i!r} -> {got!r}, wanted {want!r}", file=sys.stderr)
sys.exit(1 if bad else 0)
PY
echo "ok: typography.py turns -- into an em dash, a number range into an en dash, curls quotes, and leaves dates, codes, code spans, links and escapes alone"

# An HTML output gets the same finish, on the text a reader sees only: never
# a tag, an attribute, a comment, a script, or code (Morgan, 2026-10-16).
python3 - <<'PY'
import sys
sys.path.insert(0, "tools")
from typography import smarten_html
cases = [
    ('<p>The shape ("if we build this, here&#x27;s what") -- done.</p>',
     '<p>The shape (“if we build this, here’s what”) — done.</p>'),
    # A quote around an inline tag reads through it; an attribute never changes.
    ('<p>"<b>word</b>" and <a href="x--y.html" title="a \'t\'">it\'s</a></p>',
     '<p>“<b>word</b>” and <a href="x--y.html" title="a \'t\'">it’s</a></p>'),
    # Code, a comment and a script are set as typed.
    ('<pre>git push --force "x"</pre><p>"a"</p>', '<pre>git push --force "x"</pre><p>“a”</p>'),
    ('<p>run <code>--check</code> -- and 1990-2000</p>',
     '<p>run <code>--check</code> — and 1990–2000</p>'),
    ('<!-- a -- "b" --><script>var a="--";</script><p>&quot;q&quot; &amp; 2026-10-16</p>',
     '<!-- a -- "b" --><script>var a="--";</script><p>“q” &amp; 2026-10-16</p>'),
    # A new block starts a new run: each list item's quote opens.
    ('<li>"one"</li><li>"two"</li>', '<li>“one”</li><li>“two”</li>'),
]
bad = [(i, smarten_html(i), w) for i, w in cases if smarten_html(i) != w]
bad += [(w, smarten_html(w), w) for _i, w in cases if smarten_html(w) != w]
for i, got, want in bad:
    print(f"FAIL: {i!r} -> {got!r}, wanted {want!r}", file=sys.stderr)
sys.exit(1 if bad else 0)
PY
echo "ok: smarten_html() finishes the text a reader sees, leaves tags, attributes, comments, scripts and code alone, and a second run changes nothing"
