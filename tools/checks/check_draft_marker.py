#!/usr/bin/env python3
"""check_draft_marker.py -- the mechanical check for practices/draft-marker.md.

# practice: draft-marker

Scope: tree, over markdown files (where a draft placeholder actually
lives). The practice's own Detail section names the actual mechanical
moment: "before showing or sharing any document, scan it for the marker
specifically." Nothing committed to the repo should still carry a live
`**➡️ ... ⬅️**` placeholder -- if it's there, it was either missed on
that scan or the placeholder never got resolved before commit.

A line that only *illustrates* the marker's own format inside backtick
code -- as this practice's own Rule text does, and as this check's source
necessarily would if it weren't excluded -- is not a live placeholder, so
inline code spans are stripped before matching; only a marker sitting in
real document prose counts.

Exit 0 and print nothing when clean. Exit 1 and print the practice's own
Rule text (never a paraphrase) plus the specific finding(s) on a violation.
Exit 2, with a reason, when the check COULD NOT RUN -- reported as SKIPPED,
and a skip is not a pass.
"""
import json
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
PRACTICE_FILE = SOURCE_ROOT / "practices" / "draft-marker.md"

CODE_SPAN_RE = re.compile(r"`[^`]*`")
MARKER_RE = re.compile(r"\*\*\s*➡️.*?⬅️\s*\*\*")


class CannotRun(Exception):
    """This check could not run here. Reported as SKIPPED (exit 2), never as
    a violation and never as a crash."""


# --- Findings this repo cannot act on where they are reported -------------
#
# THE SAME EXCLUSION check_no_stale_counts.py carries, and this file was
# missing it entirely (found 2026-09-10, auditing the rest of this set's
# checks alongside the `source-checks-adopt-engine-helpers` fix). Both
# checks scan the identical file set -- every tracked `*.md` in ROOT -- so
# both reach a consuming repo's vendored copy of somebody else's
# catalogue, and a leftover draft marker inside a mirror is real but not
# actionable HERE: editing the mirror is forbidden and the next sync would
# overwrite it. `no-stale-counts` got the exclusion because it FIRED; this
# one had simply never been pointed at a repo with a mirror in it, which is
# precisely the gap the audit exists to close.
#
# Narrower than no-stale-counts' version on purpose: only mirrors. That
# check also skips generated files and foreign practices, both of which
# turn on a count of THIS repo's practices/ tree; a draft marker in a
# generated file means the recipe that generates it still carries one,
# which is worth reporting where a reader can see it.


def _mirrored_prefixes_from_manifest() -> tuple:
    """The §1-only signal, kept only as the fallback -- see below."""
    manifest = ROOT / "process" / "manifest.json"
    if not manifest.is_file():
        return ()
    try:
        upstream = json.loads(
            manifest.read_text(encoding="utf-8")).get("upstream", {})
    except (ValueError, OSError):
        return ()
    at = str(upstream.get("vendored_at") or "").strip("/")
    return (at + "/",) if at else ()


def _mirrored_prefixes() -> tuple:
    """-> repo-relative POSIX prefixes ROOT mirrors from somewhere else.

    Asked of precedent_resolve.mirrored_prefixes(), which reads three
    signals -- `process/manifest.json`'s `upstream.vendored_at`, a
    `process/upstream/` tree, and every source `path` in `precedent.json`
    that resolves inside the repo -- and deliberately does NOT treat the
    repo root, `local/`, an out-of-repo source, or the materialized
    `practices/` tree as mirrors. Over-excluding would blind this check to a
    practice set's own content, which is a worse failure than the one being
    fixed.

    DUPLICATED from check_no_stale_counts.py rather than shared through a
    sibling module, deliberately: a check script is copied ALONE into
    fixtures that carry no sibling tools (precedent_check.py's own
    `_open_item_disposition` comment records the ModuleNotFoundError that
    taught this), so an import of a neighbour takes those fixtures down.
    The same reason rule_text() is duplicated across every check in the
    catalogue.

    Falls back to the manifest-only answer when the engine is absent --
    `precedent_resolve.py` is in upstream's CONSUMER_ENGINE_FILES but not
    its ENGINE_FILES, so it does not exist inside a practice set. Not exit
    2: scanning for a leftover marker needs no engine, and only the
    exclusion degrades without one.

    The rule behind that, stated at length in
    check_no_stale_counts.py's copy: an exclusion list that comes back
    SHORT costs extra findings, never missed ones, so failing open is the
    honest degradation. Where a degraded answer would cost missed findings
    instead -- an unresolvable identity, judged against nothing -- the
    honest answer is `raise NotApplicable`, from
    `precedent_identity.NoDeclaredIdentity`.
    """
    for candidate in (ROOT / "tools", SOURCE_ROOT / "tools"):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
    try:
        import precedent_resolve as pr
    except Exception:
        return _mirrored_prefixes_from_manifest()
    try:
        return tuple(pr.mirrored_prefixes(ROOT))
    except Exception:
        return _mirrored_prefixes_from_manifest()


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


def tracked_md_files() -> list[str]:
    # A `git ls-files` that fails used to raise CalledProcessError straight
    # out of the scan (ERRORED, which is not what it means) -- and an empty
    # file list is the shape that reads as a clean tree, so it must not be
    # reached by accident either.
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "*.md"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as e:
        raise CannotRun(f"`git ls-files` could not list tracked files under "
                        f"{ROOT} ({e}), so there is no file set to scan -- an "
                        f"empty scan is not a clean one")
    mirrored = _mirrored_prefixes()
    return [line for line in result.stdout.splitlines()
            if line.strip()
            and not (mirrored and line.strip().startswith(mirrored))]


def find_violations() -> list[str]:
    findings = []
    in_fence = False
    for rel in tracked_md_files():
        path = ROOT / rel
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        in_fence = False
        for lineno, line in enumerate(text.splitlines(), start=1):
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            stripped = CODE_SPAN_RE.sub("", line)
            if MARKER_RE.search(stripped):
                findings.append(f"{rel}:{lineno}: leftover draft marker: {line.strip()!r}")
    return findings


if __name__ == "__main__":
    try:
        findings = find_violations()
    except CannotRun as e:
        print(f"SKIPPED: {e}")
        sys.exit(2)
    if findings:
        print(f"VIOLATION: {PRACTICE_FILE.stem}")
        for f in findings:
            print(f"  {f}")
        print("\nthe rule:")
        print("  " + rule_text().replace("\n", "\n  "))
        sys.exit(1)
    sys.exit(0)
