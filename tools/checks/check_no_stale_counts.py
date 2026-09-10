#!/usr/bin/env python3
"""check_no_stale_counts.py -- the mechanical check for
practices/no-stale-counts.md.

# practice: no-stale-counts

Scope: tree. The practice's own Install text is right that the general
case -- telling a count "genuinely maintained alongside the thing it
counts" apart from one that "will drift" -- needs the writer's intent,
which no scan can read. But one specific, common shape of that violation
IS objectively checkable with no intent required: a sentence in this
repo's own tracked markdown stating "<N> practices" is a claim about
THIS repo's own practices/ directory, and that claim is either currently
true or it isn't -- independent of anyone's intent in writing it.

This only catches a count that has ALREADY gone stale (the concrete harm
the practice names: "goes stale... with nothing to flag it"). It says
nothing about whether stating the count at all was the right call, or
whether some other document's exact-count sentence should be rewritten to
the qualitative form the Rule prefers -- that's still a judgment call, per
the practice's own Install text, and stays one.

Exit 0 and print nothing when clean. Exit 1 and print the practice's own
Rule text (never a paraphrase) plus the specific finding(s) on a violation.
Exit 2, with a reason, when the check COULD NOT RUN -- the runner reports
that as SKIPPED, and a skip is not a pass. Added 2026-09-10: the two
could-not-run cases below (no practices/ tree to count, and a `git
ls-files` that fails) used to reach exit 1 and an uncaught traceback
respectively, so "I could not check" was reported as "I found a
violation" and as "I broke". Both are lies a green or red run cannot be
read through.
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
PRACTICE_FILE = SOURCE_ROOT / "practices" / "no-stale-counts.md"
PRACTICES_DIR = ROOT / "practices"

# Deliberately narrow: "<N> practices" naming THIS repo's own count. Does not
# match "N rules", "N practices" describing some OTHER repo's set (context a
# script can't resolve from text alone), or a count inside a code span.
COUNT_RE = re.compile(r"(?<![`\w])(\d+)\s+practices\b")



# --- Findings this repo cannot act on where they are reported -------------
#
# A consuming repo mirrors trees it must NOT hand-edit: the vendored
# universal catalogue (byte-identical to upstream, re-mirrored wholesale)
# and any generated or re-synced copy of another repo's files. A finding
# inside one of those is real, but it is not actionable HERE -- the fix
# belongs in the repo that owns the text, and editing the mirror is
# forbidden and would be overwritten by the next sync anyway. Reporting
# them buries the findings that ARE actionable: one consuming repo's run
# showed dozens of violations, every single one inside its vendored copy
# of upstream's own prose (2026-09-06).
#
# Nothing is hardcoded. All three signals already exist and are already
# authoritative in any repo that has them:
#   1. Which of this repo's trees are MIRRORS -- asked of the engine, via
#      precedent_resolve.mirrored_prefixes(), never re-derived here. See
#      _mirrored_prefixes() below for why that question moved out of this
#      file.
#   2. A "GENERATED FILE" / "do not hand-edit" / "DERIVED" marker in the
#      file's opening lines (practice: derived-file-marker).
#   3. MANIFEST.json's per-practice `level` -- practices/ is materialized
#      output, so a practice from any source but repo-local is owned
#      elsewhere. Attributing by the COMMITTED manifest rather than by
#      live source resolution is deliberate: a bare CI checkout cannot
#      reach a team sibling clone or a private user-level config, and
#      "did not resolve here" is not "owned here".
# A repo with none of these files loses nothing -- every part fails open.
_GENERATED_RE = re.compile(
    r"generated file|do not hand[- ]edit|DERIVED from", re.I)


def _mirrored_prefixes_from_manifest() -> tuple:
    """The one signal this file used to read on its own: §1's bookkeeping.

    Kept ONLY as the fallback for an environment with no engine to ask --
    see _mirrored_prefixes(). It is the weaker answer, and the reason is
    exactly that it reads a §1-only path.
    """
    manifest = ROOT / "process" / "manifest.json"
    if not manifest.is_file():
        return ()
    try:
        upstream = json.loads(manifest.read_text(encoding="utf-8")).get("upstream", {})
    except (ValueError, OSError):
        return ()
    at = str(upstream.get("vendored_at") or "").strip("/")
    return (at + "/",) if at else ()


def _mirrored_prefixes() -> tuple:
    """-> repo-relative POSIX prefixes whose contents ROOT mirrors from
    somewhere else, and may therefore not hand-edit.

    ASKED OF THE ENGINE, NOT RE-DERIVED HERE (2026-09-10, closing the
    `precedent-team-writing` half of BestPractice's TODO item
    `source-checks-adopt-engine-helpers`). This function used to BE
    _mirrored_prefixes_from_manifest() above: it read
    `process/manifest.json`'s `upstream.vendored_at` and nothing else.
    That file is INSTALL.md §1's bookkeeping, and §0 step 5 says outright
    to skip it -- so in a §0 install this returned () and the exclusion
    the comment above argues for silently evaporated, putting the whole
    vendored catalogue back in scope. A real §0 install on 2026-09-10
    reported Precedent's own historical prose as stale ("states 34
    practices, but practices currently holds 121"), none of it actionable:
    editing a mirror is forbidden and the next sync would overwrite it.
    The adopter's workaround was to hand-write a `process/manifest.json`
    carrying nothing but an `upstream` block, purely to feed this signal --
    a file the install had been told not to create.

    precedent_resolve.mirrored_prefixes() reads three signals instead of
    one: the manifest (kept), a `process/upstream/` tree with or without a
    manifest naming it, and every source `path` declared in
    `precedent.json` that resolves inside the repo -- which is the
    authority that EXISTS in exactly the repos the manifest is missing
    from. It never raises, and () is one of its valid answers.

    WHY THE FALLBACK IS THE OLD BEHAVIOUR AND NOT `exit 2`. The engine
    module is absent here by design: `precedent_resolve.py` is in
    upstream's CONSUMER_ENGINE_FILES but not its ENGINE_FILES, because a
    practice set resolves no catalogue -- so inside this very repo the
    import fails every time. Reporting SKIPPED there would trade one
    silent failure for a louder one: this check's actual job, auditing
    this set's own count claims, needs no engine at all, and only the
    mirror EXCLUSION degrades without it. In a source set the two answers
    are identical anyway (no `sources`, no manifest, no `process/upstream/`
    -- both return ()), which is what makes falling back honest rather
    than merely convenient. Exit 2 is reserved for what genuinely cannot
    run; see CannotRun below for the cases that earn it.
    """
    # ROOT before SOURCE_ROOT: in a materialized consuming repo they are
    # the same directory, and where they differ the engine that belongs to
    # the repo being AUDITED is the one to ask.
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
        # Documented never to raise. Belt and braces anyway: a check that
        # takes a whole run down over its own exclusion list is worse than
        # one that excludes less than it should.
        return _mirrored_prefixes_from_manifest()


class CannotRun(Exception):
    """This check could not run here. Reported as SKIPPED (exit 2), never as
    a violation and never as a crash -- the engine's own rule, in
    precedent_check.py's docstring: "A CHECK THAT CANNOT RUN REPORTS THAT
    IT DID NOT RUN. Every graceful-failure path here ends in SKIPPED with a
    reason, never in a pass."

    Distinct from the fail-open exclusions above, which degrade the check's
    PRECISION while leaving it able to answer. These are the cases where
    there is no answer to give.
    """


def _is_generated(rel: str) -> bool:
    try:
        with (ROOT / rel).open(encoding="utf-8") as fh:
            head = "".join([next(fh, "") for _ in range(3)])
    except (OSError, UnicodeDecodeError):
        return False
    return bool(_GENERATED_RE.search(head))


def _foreign_practice(rel: str) -> bool:
    if not (rel.startswith("practices/") and rel.endswith(".md")):
        return False
    manifest = ROOT / "MANIFEST.json"
    if not manifest.is_file():
        return False
    try:
        entries = json.loads(manifest.read_text(encoding="utf-8")).get("practices", [])
    except (ValueError, OSError):
        return False
    slug = pathlib.PurePath(rel).stem
    for entry in entries:
        if entry.get("slug") == slug:
            return entry.get("level") != "repo-local"
    return False


def not_actionable_here(rel: str) -> bool:
    prefixes = _mirrored_prefixes()
    return (bool(prefixes) and rel.startswith(prefixes)) \
        or _foreign_practice(rel) or _is_generated(rel)

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


def tracked_markdown() -> list[str]:
    # `check=True` here used to raise CalledProcessError straight out of the
    # scan -- reported as ERRORED, which is not what it means. This is a
    # scope: tree check reading the index, so a `git ls-files` that fails
    # (not a repository, git absent, an unreadable index) yields an EMPTY
    # file list, and an empty input set is the shape that reads as "clean".
    # The same trap as an under-fetched clone: nothing found is not nothing
    # there.
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "*.md"],
            capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError) as e:
        raise CannotRun(f"`git ls-files` could not list tracked files under "
                        f"{ROOT} ({e}), so there is no file set to scan -- an "
                        f"empty scan is not a clean one")
    return [line for line in result.stdout.splitlines()
            if line.strip() and not not_actionable_here(line.strip())]


def find_violations() -> list[str]:
    # ACTIVE practices, not files on disk. A retired practice keeps its
    # file -- so `supersedes:` still points at something real -- while not
    # being in force, and the generated loader block has always counted
    # what is in force. Counting files made this check disagree with the
    # very figure it was auditing the moment a practice was retired:
    # 2026-09-06, an engine refresh brought a build_views.py that writes
    # "3 of 39 practices" (39 active of 41 files), and this check called
    # that correct figure stale. A checker that contradicts the generator
    # it checks is worse than no checker: it teaches the next session that
    # the generated number is the unreliable one.
    #
    # AND: no practices/ tree at all is NOT a count of zero. Every finding
    # this check prints is a comparison against `actual`, so a repo that
    # declares this source without materializing it -- or one whose
    # catalogue lives at a path `precedent.json` names rather than at
    # `practices/` -- would have every "<N> practices" sentence in it
    # reported as "states N practices, but practices currently holds 0".
    # That is shape 2 of the §1-assumption audit (2026-09-10): the absence
    # of an optional tree read as a violation instead of as "not applicable
    # here". A tree that EXISTS with no active practice in it is a real
    # zero and still checked.
    if not PRACTICES_DIR.is_dir():
        raise CannotRun(f"{PRACTICES_DIR} does not exist, so this repo has no "
                        f"practice count for a sentence to be stale against")
    practice_files = sorted(PRACTICES_DIR.glob("*.md"))
    if not practice_files:
        raise CannotRun(f"{PRACTICES_DIR} holds no practice file, so nothing "
                        f"here has been materialized to count")
    actual = 0
    for f in practice_files:
        try:
            body = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if re.search(r"^status:\s+active\s*$", body, re.M):
            actual += 1
    findings = []
    for rel in tracked_markdown():
        path = ROOT / rel
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in COUNT_RE.finditer(line):
                # Skip a match sitting inside an inline code span -- a value,
                # not prose making a claim about this repo.
                before = line[:m.start()]
                if before.count("`") % 2 == 1:
                    continue
                stated = int(m.group(1))
                if stated != actual:
                    findings.append(
                        f"{rel}:{lineno}: states {stated!r} practices, but "
                        f"{PRACTICES_DIR.relative_to(ROOT)} currently holds "
                        f"{actual}: {line.strip()!r}")
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
