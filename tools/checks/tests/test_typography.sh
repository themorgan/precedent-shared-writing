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
]
bad = [(i, smarten(i), want) for i, want in cases if smarten(i) != want]
for i, got, want in bad:
    print(f"FAIL: {i!r} -> {got!r}, wanted {want!r}", file=sys.stderr)
sys.exit(1 if bad else 0)
PY
echo "ok: typography.py turns -- into an em dash, a number range into an en dash, curls quotes, and leaves dates, codes, links and escapes alone"
