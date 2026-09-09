#!/usr/bin/env python3
"""An output document carries none of the process that made it.

deliverables-carry-no-process. A document in one of a repo's declared
`output_paths` has a reader who is not in the project. Three things that
belong in a working note leak into it and cost that reader attention:

  1. an attribution stamp -- `(Morgan, 2026-09-08)`, or the same without
     the parentheses, closing a sentence;
  2. a practice-slug citation -- `` (`assorted-notes`) `` -- which names
     nothing the reader can look up;
  3. a link into practices/, process/ or tools/checks/.

Two exemptions, both narrow. The `<!-- Last updated ... -->` header that
file-header requires is invisible in every rendering, so HTML-comment
lines are skipped. A doc-recipes/ directory is skipped outright: a
recipe's whole job is to state the rules for one file, and it never ships.

WHY THE SLUG HALF READS THE MANIFEST rather than matching hyphenated
words. Real slugs include `install` and `push-back`, which are also
ordinary English; matching by shape would fire on "push-back from the
market" in a marketing document, which is exactly the kind of false
positive that gets a check switched off. So a slug counts only when it is
BACKTICKED or LINKED and appears in the repo's committed MANIFEST.json --
a deliberate citation, not a word.

THE INCIDENT (cite-the-incident). 2026-09-08, in a repo whose
business-modeling/ cluster renders into one HTML page sent to people as a
link. Morgan read the rendering: two `(Morgan, 2026-09-08)` stamps, four
backticked slugs, and a hub section telling the reader that two files were
derived and should be regenerated rather than edited in place -- repo
maintenance addressed to somebody without the repo. Every one of them was
a session being honest about where a decision came from or which rule it
followed. Good instincts in a working note; wrong in the one artifact that
leaves the building, which is why this is a check and not a reminder.
"""
import json
import os
import pathlib
import re
import subprocess
import sys

SOURCE_ROOT = pathlib.Path(__file__).resolve().parents[2]
ROOT = pathlib.Path(os.environ.get("PRECEDENT_CHECK_ROOT") or SOURCE_ROOT)

# "Morgan, 2026-09-08" / "(Morgan F, 2026-09-08)" / "Morgan's list,
# 2026-09-08" -- a capitalised name, optionally possessive, optionally
# followed by a few words, then an ISO date. Still narrow on purpose: a bare
# date in content ("through 2026-09") is legitimate and must not fire, so the
# comma-then-date is required.
#
# The first version demanded the comma IMMEDIATELY after the name and allowed
# only further capitalised words, which the possessive breaks: `[a-zA-Z]+`
# stops at "Morgan", and the next character is an apostrophe, not a comma. It
# hid five real stamps in the repo this check was written for -- "Morgan's
# list, 2026-09-08" and four of "Morgan's request, 2026-09-08" -- and the
# clean run said so with a count that looked like proof.
STAMP = re.compile(
    r"[A-Z][a-zA-Z]+(?:'s)?(?:[ \t]+[A-Za-z][a-zA-Z]*\.?){0,3}"
    r",\s{0,4}\d{4}-\d{2}-\d{2}")
BACKTICKED = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`")
LINK = re.compile(r"\[(?:`[^`]*`|[^\]]*)\]\(([^)\s]+)\)")
INTERNAL_LINK = re.compile(r"(^|/)(practices|process|tools/checks)/")
HTML_COMMENT = re.compile(r"^\s*<!--")


def _declared(key):
    cfg = ROOT / "precedent.json"
    if not cfg.is_file():
        return []
    try:
        return json.loads(cfg.read_text(encoding="utf-8")).get(key) or []
    except Exception:
        return []


def _manifest_slugs():
    """Every practice slug this repo has materialized.

    Read from the COMMITTED manifest, never from live resolution: a bare CI
    checkout cannot reach a team source's sibling clone or an individual
    source's user-level config, and a slug that "did not resolve here" is
    still a slug a reader cannot look up.
    """
    m = ROOT / "MANIFEST.json"
    if not m.is_file():
        return set()
    try:
        entries = json.loads(m.read_text(encoding="utf-8")).get("practices", [])
    except Exception:
        return set()
    return {e.get("slug") for e in entries if e.get("slug")}


def _tracked_markdown():
    try:
        out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
    except Exception:
        return []
    return [p for p in out.splitlines() if p]


def _mask_comments(text):
    """Blank out HTML-comment lines, keeping every offset intact.

    The file-header comment file-header requires carries a name and a date,
    and is invisible in every rendering, so it must not fire. Masking rather
    than dropping keeps the line numbers in the findings honest.
    """
    out = []
    for line in text.split("\n"):
        out.append(" " * len(line) if HTML_COMMENT.match(line) else line)
    return "\n".join(out)


def _in_scope(rel, outputs, internals):
    if not any(rel == o or rel.startswith(o.rstrip("/") + "/") for o in outputs):
        return False
    if any(rel == i or rel.startswith(i.rstrip("/") + "/") for i in internals):
        return False
    return "/doc-recipes/" not in "/" + rel


def main():
    outputs = _declared("output_paths")
    if not outputs:
        print("SKIPPED: this repo declares no output_paths, so no document "
              "here is marked as written for an outside reader")
        return 0
    internals = _declared("internal_paths")
    slugs = _manifest_slugs()

    findings, scanned = [], 0
    for rel in _tracked_markdown():
        if not _in_scope(rel, outputs, internals):
            continue
        scanned += 1
        path = ROOT / rel
        try:
            text = _mask_comments(path.read_text(encoding="utf-8"))
        except OSError:
            continue

        def at(offset):
            return text.count("\n", 0, offset) + 1

        for m in STAMP.finditer(text):
            findings.append(
                f"  {rel}:{at(m.start())}: attribution stamp "
                f"{' '.join(m.group(0).split())!r} -- who decided this and "
                f"when belongs in the commit and the open-items list, not in "
                f"a document sent to readers")
        for m in BACKTICKED.finditer(text):
            if m.group(1) in slugs:
                findings.append(
                    f"  {rel}:{at(m.start())}: practice slug `{m.group(1)}` "
                    f"cited in an output document -- it names nothing a "
                    f"reader outside the project can look up")
        for m in LINK.finditer(text):
            if INTERNAL_LINK.search(m.group(1)):
                findings.append(
                    f"  {rel}:{at(m.start())}: link to {m.group(1)!r} points "
                    f"into the practice layer from a document written for "
                    f"readers")

    if findings:
        print("VIOLATION: deliverables-carry-no-process")
        for f in findings:
            print(f)
        return 1
    print(f"OK: {scanned} output document(s) across {len(outputs)} declared "
          f"output path(s); no attribution stamps, practice slugs or links "
          f"into the practice layer")
    return 0


if __name__ == "__main__":
    sys.exit(main())
