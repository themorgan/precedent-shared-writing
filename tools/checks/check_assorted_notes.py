#!/usr/bin/env python3
"""check_assorted_notes.py -- the mechanical check for practices/assorted-notes.md.

# practice: assorted-notes

Scope: tree, over every file tracked in the repo. The practice's Rule is
that nothing outside `content/ASSORTED_NOTES.md` (or a legacy equivalent
not yet renamed) may *cite* an idea from inside it -- but a plain link
from a listing context is allowed, since inventorying that the file
exists is not the same as citing something inside it. Two such contexts:
a directory-listing document (any `README.md` or `MAP.md`, at any
depth), and a "## See also" section in ANY file -- a page-to-page
cross-reference footer is the same listing move distributed per-page
instead of centralized in one index. A real citation, in a repo whose
own standing convention is "doc references are links, never bare
filenames" (`doc-references-are-links`), takes the form of a markdown
link whose target path ends in one of the recognized filenames. This
check looks for exactly that: a markdown link `[...](...ASSORTED_NOTES.md)`
(or a legacy name) outside the practice file, the notes file itself, any
listing document, and any "## See also" section -- and not a link whose own
text is the file's name or path with no `#fragment`, which names the file
rather than citing anything in it (see _names_the_file_itself).

It cannot see a prose reference with no link ("see the notes file for
why") -- that's a judgment call with no reliable mechanical signature,
same as `checkable-gets-checked`'s own standing allowance for a practice
that is only partly checkable. The link form is the common, catchable
case in a repo that otherwise always links.

A link's target is matched by its *basename* exactly, not by whether it
ends in one of the recognized filenames as a substring -- a real link to
`content/MARKETING_IDEAS.md` or `content/RANDOM_NOTES.md` is not a
reference to `ASSORTED_NOTES.md`/`NOTES.md`/`IDEAS.md` just because its
own filename happens to end the same way. The same basename-exact rule
applies to the listing-document exemption: a file merely named
`SOMETHING_README.md` doesn't qualify -- only a basename that is exactly
`README.md` or `MAP.md` does.

Exit 0 and print nothing when clean. Exit 1 and print the practice's own
Rule text (never a paraphrase) plus the specific finding(s) on a violation.
"""
import os
import pathlib
import re
import subprocess
import sys

# TWO different questions, which used to share one name -- and that is exactly
# how a practice file went missing. SOURCE_ROOT is the practice set this script
# ships in; ROOT is the repository it AUDITS.
#
# They are the same directory in both normal cases: run in place inside its own
# set, and materialized into a consuming repo (where precedent_materialize.py
# has written practices/ and tools/checks/ side by side). They differ in the
# third case -- a repo that DECLARES this source but never materializes it, and
# runs the script in place against itself. Precedent's own repo is exactly
# that: its practices/ is the universal catalogue, so `parents[2]/practices/`
# resolved to a directory this practice was never in, and rule_text() raised
# FileNotFoundError from inside the violation printer (2026-09-06). The rule
# text always ships beside the script, so it is looked up against SOURCE_ROOT
# and can no longer be absent; only what to audit is overridable.
SOURCE_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ROOT = pathlib.Path(os.environ.get("PRECEDENT_CHECK_ROOT") or SOURCE_ROOT)
PRACTICE_FILE = SOURCE_ROOT / "practices" / "assorted-notes.md"

# Legacy names this practice says to consolidate into ASSORTED_NOTES.md --
# a link to any of these, in an unrenamed legacy repo, is the same violation.
LEGACY_FILENAMES = ("BRAINSTORM.md", "NOTES.md", "IDEAS.md")
CANONICAL_FILENAME = "ASSORTED_NOTES.md"


def _canonical_exists() -> bool:
    """Is there an ASSORTED_NOTES.md anywhere in the tracked tree?

    Asked by basename, at any depth, NOT at a hardcoded `content/`. The
    directory is this practice's *default*, not its definition -- and
    `content-directory`, which supplies that default, says in as many words
    that an established layout wins over it. A repo that keeps its working
    files somewhere better-named still has a catch-all, and the migration
    this check gates on is just as done there.

    2026-09-07: a consuming repo renamed `content/` to `business-modeling/`
    so that every content directory of its own said what it held. Its
    ASSORTED_NOTES.md moved intact, with the rename -- and this check,
    testing one literal path, silently concluded the legacy-name migration
    had never happened and re-armed BRAINSTORM.md/NOTES.md/IDEAS.md as live
    legacy names across that whole repo. It kept passing by luck: the only
    links to its `book-moses/NOTES.md` happened to sit in a MAP.md and a
    README.md, both exempt as listing documents. One ordinary link from any
    other file would have failed the repo for a violation that was never
    there -- the exact false positive the docstring below this one was
    written to stop, reintroduced through the directory name instead of the
    filename.
    """
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "*" + CANONICAL_FILENAME],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Not a git repo, or git unavailable. Fall back to the old literal
        # path rather than guessing: a wrong "migration is done" here would
        # silently narrow the check, and failing open is the worse direction
        # for a rule about not citing unformed notes.
        return (ROOT / "content" / CANONICAL_FILENAME).is_file()
    return any(pathlib.PurePosixPath(line).name == CANONICAL_FILENAME
               for line in result.stdout.splitlines() if line.strip())


def notes_filenames() -> tuple:
    """The canonical name always; the legacy names only until the migration
    this practice describes has actually happened.

    "In an unrenamed legacy repo" is the condition the comment above states
    and the check did not test: it matched any file named NOTES.md, anywhere,
    forever. Once an ASSORTED_NOTES.md exists the consolidation is
    done, and a file that merely shares a legacy name is an ordinary file
    with its own subject -- 2026-09-06, a repo with a perfectly good
    content/ASSORTED_NOTES.md was flagged for linking `book-moses/NOTES.md`,
    a manuscript-scoped brainstorm about Moses that is not this repo's
    catch-all and was never meant to become it. Reading the legacy names as
    permanent turns a one-time migration rule into a standing ban on a
    common filename."""
    if _canonical_exists():
        return (CANONICAL_FILENAME,)
    return (CANONICAL_FILENAME,) + LEGACY_FILENAMES


def _mirrored_prefixes_without_the_engine() -> tuple:
    """Exclude nothing, which is exactly what this check did before it asked
    the question at all -- so a repo with no precedent_resolve.py behaves as
    it always has, and the gain is confined to the repos that have one."""
    return ()


# --- what this repo MIRRORS from elsewhere, and may not edit -------------
#
# THE ENGINE ANSWERS THIS NOW (2026-09-10). Several source-supplied checks
# need the same list -- anything that scans prose and would otherwise report
# findings inside a vendored copy of somebody else's catalogue -- and each
# derived it privately, from whichever single file it happened to know
# about. That is how a real defect got in: a check reading only
# `process/manifest.json`'s `upstream.vendored_at` loses its exclusion
# entirely in an INSTALL.md section 0 install, because section 0 step 5 says
# outright to SKIP that file, and a section 0 install puts the engine at
# `tools/` instead. A real section 0 install's run reported dozens of
# findings inside Precedent's own historical prose, none of them actionable:
# editing a mirror is forbidden and the next sync would overwrite it anyway.
#
# precedent_resolve.mirrored_prefixes(ROOT) reads `precedent.json`'s declared
# source paths as well as the manifest -- and precedent.json is the file that
# EXISTS in exactly the repos process/manifest.json is missing from. It never
# raises; an empty tuple is a valid answer (it is what a source set and a
# fresh repo return).
#
# FAILS OPEN, deliberately, where the two identity checks report SKIPPED for
# the same missing module. precedent_resolve.py is in upstream's
# CONSUMER_ENGINE_FILES but not its ENGINE_FILES, so a practice-set repo does
# not vendor it -- and an exclusion that comes back empty costs extra
# findings, never a missed one, while an identity that cannot be resolved
# would make every verdict wrong. Different failure, different degrade.
def _mirrored_prefixes() -> tuple:
    for _d in (ROOT / "tools", ROOT / "process" / "upstream" / "tools",
               pathlib.Path(__file__).resolve().parent.parent,
               SOURCE_ROOT / "tools"):
        if (_d / "precedent_resolve.py").is_file():
            sys.path.insert(0, str(_d))
            break
    try:
        import precedent_resolve
        return tuple(precedent_resolve.mirrored_prefixes(ROOT))
    except Exception:
        return _mirrored_prefixes_without_the_engine()


_MIRRORED = _mirrored_prefixes()


# Matches any markdown link's target; the target is then checked against
# notes_filenames() by basename, not by this regex, so a filename that merely
# ends the same way (MARKETING_IDEAS.md, RANDOM_NOTES.md) doesn't match.
LINK_RE = re.compile(r"\]\(([^)]+)\)")

# Files allowed to mention the notes file's own path without that counting
# as a reference to its *content* -- the practice file that documents the
# convention, and the notes file itself (a self-link, e.g. a header anchor).
# Any README.md or MAP.md, at any depth, is also exempt: a directory listing
# names what exists, which isn't citing anything inside it -- see the Rule's
# own "listing vs. citation" distinction.
EXEMPT_BASENAMES = (
    {"assorted-notes.md", "readme.md", "map.md"}
    | {n.lower() for n in notes_filenames()}
)

# This check's own machinery: its docstring illustrates the exact link
# pattern it looks for, and its test plants that pattern as a fixture --
# neither is a real reference to real notes content.
EXEMPT_PATHS = {
    "tools/checks/check_assorted_notes.py",
    "tools/checks/tests/test_assorted_notes.sh",
}

def _names_the_file_itself(line: str, start: int, target: str, path: str) -> bool:
    """Is this link a reference to the notes file AS A WHOLE?

    True when the target carries no `#fragment` and the link's own text is
    the file's name or path -- `[ASSORTED_NOTES.md](../ASSORTED_NOTES.md)`,
    `[philosophy/ASSORTED_NOTES.md](../philosophy/ASSORTED_NOTES.md)`. That
    is the same move as a listing: it says the file exists and where, and
    cites nothing inside it. A citation reads differently -- "per [the
    notes](...)" -- or points into the file with a fragment, and both still
    fire.

    WHY (2026-09-28). Run against the engine's own repository, this check
    flagged a doc recipe that names the notes file as the one document its
    rule does not reach, and a todo item recording where a file lives. Each
    link's text was the file's own path; neither borrowed an idea from it.

    The text is read back to the nearest `[` on the same line. A link whose
    text wraps onto an earlier line has no text here, and is judged as it
    always was.
    """
    if "#" in target:
        return False
    opening = line.rfind("[", 0, start)
    if opening == -1:
        return False
    text = line[opening + 1:start].strip().strip("`").strip()
    if not text or any(c.isspace() for c in text):
        return False
    bare = target.split()[0] if target.split() else target
    if text in (bare, pathlib.PurePosixPath(bare).name):
        return True
    # A repo-rooted spelling of the same file ("philosophy/ASSORTED_NOTES.md"
    # for a target of "../philosophy/ASSORTED_NOTES.md" from todo/) is its
    # path too: resolve the target from the linking file and compare tails.
    resolved = os.path.normpath(
        os.path.join(os.path.dirname(path), bare)).replace(os.sep, "/")
    text = text.removeprefix("./").removeprefix("/")
    return resolved == text or resolved.endswith("/" + text)


# A "## See also" section is a listing context too -- exempt lines inside
# one, from its heading to the next "## " heading or end of file.
# Case-insensitive: in a repo that declares `output_paths`,
# headline-capitalization rewrites "## See also" to "## See Also", and a
# literal match stops recognising the listing context entirely -- every
# footer link to the notes file then reads as a citation. Seen 2026-09-07
# in a consuming repo on the sweep that applied the rule. The heading's
# capitalization is that rule's business, not this check's.
SEE_ALSO_RE = re.compile(r"^## See also\s*$", re.I)
HEADING_RE = re.compile(r"^## ")


def rule_text() -> str:
    # A materialized check runs in whatever repo its source was resolved
    # into, and the practice file it quotes is not guaranteed to be there:
    # a repo that declares the source but never materializes it, or a
    # practice retired out of the tree, both leave PRACTICE_FILE absent.
    # Unguarded, this raised FileNotFoundError from inside the violation
    # PRINTER -- so the finding was correctly detected, correctly printed,
    # and then buried under a traceback. Found 2026-09-06 running every
    # source-supplied check against BestPractice; 14 of the 16 shared this
    # exact body. The Rule text being unavailable is not the check failing.
    if not PRACTICE_FILE.is_file():
        return "(practice file not found at %s)" % PRACTICE_FILE
    text = PRACTICE_FILE.read_text(encoding="utf-8")
    m = re.search(r"## Rule\n(.*?)\n## ", text, re.S)
    return m.group(1).strip() if m else "(no Rule found)"


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def find_violations() -> list[str]:
    findings = []
    for path in tracked_files():
        # A citation inside a vendored copy of somebody else's catalogue is
        # not this repo's to fix: the fix belongs in the source, and the
        # next sync overwrites a hand-edit here.
        if _MIRRORED and path.startswith(_MIRRORED):
            continue
        if pathlib.Path(path).name.lower() in EXEMPT_BASENAMES:
            continue
        if path in EXEMPT_PATHS:
            continue
        full = ROOT / path
        try:
            text = full.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        in_see_also = False
        for lineno, line in enumerate(text.splitlines(), start=1):
            if SEE_ALSO_RE.match(line):
                in_see_also = True
                continue
            if HEADING_RE.match(line):
                in_see_also = False
            if in_see_also:
                continue
            for m in LINK_RE.finditer(line):
                target = m.group(1)
                if pathlib.Path(target).name in notes_filenames():
                    if _names_the_file_itself(line, m.start(), target, path):
                        continue
                    findings.append(f"{path}:{lineno}: links to {target!r}")
    return findings


if __name__ == "__main__":
    findings = find_violations()
    if findings:
        print(f"VIOLATION: {PRACTICE_FILE.stem}")
        for f in findings:
            print(f"  {f}")
        print("\nthe rule:")
        print("  " + rule_text().replace("\n", "\n  "))
        sys.exit(1)
    sys.exit(0)
