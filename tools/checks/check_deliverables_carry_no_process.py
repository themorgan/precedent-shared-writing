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

Three exemptions, all narrow. The `<!-- Last updated ... -->` header that
file-header requires is invisible in every rendering, so HTML-comment
lines are skipped. A doc-recipes/ directory is skipped outright: a
recipe's whole job is to state the rules for one file, and it never ships.
And a section the repo declares under `unpublished_sections` in
precedent.json -- {"path": ..., "heading": ...} -- is skipped from its
heading to the next heading of any level, because the repo's own page
builder cuts it before anything is sent. That list is the one declaration
both read: a builder that cut a section the check still scanned produced
findings for text no reader would ever see (48 of 50 on one page,
2026-09-25), and a check that skipped a section the builder still shipped
would hide a real leak. Neither side may keep its own copy.

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

Exit 0 when clean, 1 on a violation, and 2 -- reported as SKIPPED -- when
the check could not run. The three could-not-run paths all returned 0
until 2026-09-10, so "no document was in scope" reported as PASS: this
file printed the word SKIPPED and then handed the runner a clean exit,
which is the exact failure precedent_check.py's own docstring says has
bitten this project four times ("a scan with an empty input set printing
OK"). Found auditing this set's checks alongside the
`source-checks-adopt-engine-helpers` fix; nothing had gone wrong yet
because this repo declares no output_paths, so the wrong answer and the
right one looked the same from here.
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
HEADING = re.compile(r"^(#{1,6}) (.+)$")


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


class CannotRun(Exception):
    """This check could not run here. Reported as SKIPPED (exit 2), never as
    a violation and never as a pass."""


def _tracked_markdown():
    # `except Exception: return []` swallowed a failing `git ls-files` into
    # an empty file list, and an empty file list is what a clean tree looks
    # like -- so a repo git could not read reported OK. The same trap as an
    # under-fetched clone: nothing found is not nothing there.
    try:
        out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
    except Exception as e:
        raise CannotRun(f"`git ls-files` could not list tracked files under "
                        f"{ROOT} ({e}), so there is no file set to scan -- an "
                        f"empty scan is not a clean one")
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


def _unpublished_sections():
    """{repo-relative path: {heading text}} from precedent.json's
    `unpublished_sections`. An entry missing either half is ignored rather
    than guessed at: a section with no heading cannot be located, and one
    with no path would exempt that heading in every document."""
    out = {}
    for e in _declared("unpublished_sections"):
        if isinstance(e, dict) and e.get("path") and e.get("heading"):
            out.setdefault(e["path"], set()).add(str(e["heading"]).strip())
    return out


def _mask_unpublished(text, headings):
    """Blank each named section, heading line included, keeping every
    offset intact so line numbers in the findings stay honest.

    A section runs from its heading to the next heading of ANY level --
    the boundary the consuming repo's page builder cuts on. Matching a
    narrower boundary here would scan text the builder drops; a wider one
    would skip text it ships."""
    if not headings:
        return text
    out, skipping = [], False
    for line in text.split("\n"):
        m = HEADING.match(line)
        if m:
            skipping = m.group(2).strip() in headings
        out.append(" " * len(line) if skipping else line)
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
        # Exit 2, not 0. This whole check is scoped by a declaration the
        # repo may not have made, and "nobody has told me which documents
        # face outward" is not "no document here leaks process".
        print("SKIPPED: this repo declares no output_paths, so no document "
              "here is marked as written for an outside reader")
        return 2
    internals = _declared("internal_paths")
    unpublished = _unpublished_sections()
    slugs = _manifest_slugs()

    findings, scanned = [], 0
    for rel in _tracked_markdown():   # raises CannotRun, never returns []
        if not _in_scope(rel, outputs, internals):
            continue
        scanned += 1
        path = ROOT / rel
        try:
            text = _mask_unpublished(
                _mask_comments(path.read_text(encoding="utf-8")),
                unpublished.get(rel, set()))
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

    # An empty scan is not a clean one. output_paths is declared, so
    # documents are meant to be there; zero IN SCOPE means either the
    # declaration and the tree disagree, or everything under those paths was
    # exempt -- and in both cases nothing was examined. Reporting PASS on it
    # is how a check that no longer looks at anything keeps looking green.
    if not scanned:
        print(f"SKIPPED: this repo declares {len(outputs)} output path(s) "
              f"({', '.join(sorted(outputs))}) but no tracked markdown file "
              f"under them was in scope -- either nothing is there, or every "
              f"document found was exempt (a doc-recipes/ file, or one under "
              f"a declared internal_path). Nothing was scanned")
        return 2

    # Say which halves actually ran. The slug half needs a committed
    # MANIFEST.json and silently does nothing without one -- a partial skip
    # the 0/1/2 protocol cannot express, so the message carries it instead
    # of an OK line that overstates what was checked.
    slug_half = (f"practice slugs (against {len(slugs)} in MANIFEST.json)"
                 if slugs else
                 "NOT practice slugs -- no MANIFEST.json here to tell a "
                 "citation from an ordinary hyphenated word")
    print(f"OK: {scanned} output document(s) across {len(outputs)} declared "
          f"output path(s); no attribution stamps, no links into the practice "
          f"layer, and {slug_half}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CannotRun as e:
        print(f"SKIPPED: {e}")
        sys.exit(2)
