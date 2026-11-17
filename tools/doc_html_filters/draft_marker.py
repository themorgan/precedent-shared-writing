"""draft_marker.py -- sets every draft-marker note in bright red on a web page.

# practice: draft-marker

The draft-marker rule says a ➡️ ... ⬅️ note is bright red (#FF0000), arrows
included, wherever a document is rendered. create_word_doc.py does it for
Word; this does it for the pages tools/doc_html.py renders. That renderer
loads every module in tools/doc_html_filters/ and knows nothing of what
any one is for: the rule's look lives here, with the rule.

Text inside <pre> and <code> is left alone: there a marker is being shown,
not left as a note.
"""
import re

CSS = ".draft-marker { color: #FF0000; font-weight: 700; }\n"

# A note's arrows, with or without the emoji variation selector; [^<] keeps
# a match inside one run of text, so it never spans a tag.
_MARKER_RE = re.compile("(➡️?[^<]*?⬅️?)")
_CODE_RE = re.compile(r"(<pre\b.*?</pre>|<code\b.*?</code>)", re.S)


def filter(body):
    """Wrap each note in <span class="draft-marker">, outside code."""
    parts = _CODE_RE.split(body)
    for i in range(0, len(parts), 2):
        parts[i] = _MARKER_RE.sub(r'<span class="draft-marker">\1</span>', parts[i])
    return "".join(parts)
