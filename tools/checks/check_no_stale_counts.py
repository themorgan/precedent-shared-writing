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
    mirror EXCLUSION degrades without it.

    WHICH WAY A DEGRADED ANSWER COSTS is the whole test, and it is worth
    stating as a rule rather than re-deriving per check. An exclusion list
    that comes back SHORT costs extra findings, never missed ones, so
    failing open is the honest degradation here: the worst case is noise a
    reader can see and dismiss. Contrast an unresolvable IDENTITY, where
    failing open would mean judging a commit against nothing -- there the
    honest answer is `raise NotApplicable`, and
    `precedent_identity.NoDeclaredIdentity` is the cue for it. (Identity
    moved out of the resolver into upstream's `tools/precedent_identity.py`,
    which IS in ENGINE_FILES, so a practice set vendors it; a check here
    that ever needs identity imports it from there, not from
    precedent_resolve. `mirrored_prefixes()` stayed in the resolver,
    because it genuinely is catalogue resolution.)

    In a source set the two answers
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


def _declared_sources() -> list | None:
    """Every source ROOT/precedent.json declares, path-resolved against
    ROOT -- or None when there is no config, or it declares none.

    Deliberately NOT precedent_resolve.load_config(): that function can
    self-heal a missing universal or individual source by running a hook
    or cloning a repository over the network, which is far more machinery
    than a check that only wants to know how many sources contribute to
    THIS repo's own count needs -- the same reasoning _mirrored_prefixes()
    above gives (SIGNAL 3) for reading precedent.json directly rather than
    calling load_config() itself.
    """
    config = ROOT / "precedent.json"
    if not config.is_file():
        return None
    try:
        raw = json.loads(config.read_text(encoding="utf-8")).get("sources") or []
    except (ValueError, OSError):
        return None
    declared = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        level, path = entry.get("level"), entry.get("path")
        if not level or not path:
            continue
        p = pathlib.Path(os.path.expandvars(str(path))).expanduser()
        p = p if p.is_absolute() else (ROOT / p)
        declared.append({"level": level, "name": entry.get("name", level),
                         "path": str(p.resolve())})
    return declared or None


class _UnresolvedSources(Exception):
    """More than one declared source contributes to this repo's own
    tracked practice count, and this environment could not resolve all of
    them. The caller must report SKIPPED rather than guess either number."""


def _resolved_active_count() -> int | None:
    """-> the real active-practice total for a repo whose own tracked
    count is not just PRACTICES_DIR, or None when PRACTICES_DIR alone
    already IS the whole answer (the ordinary case, and every consuming
    repo whose declared sources are already materialized into one
    practices/ tree).

    MIRRORS how build_views.py's loader_practices() builds the very
    "<N> of <M> practices" figure this check audits: sources_for_tracked_
    block() (asked of the engine, never re-derived -- same reasoning as
    _mirrored_prefixes() above) decides which of this repo's declared
    sources actually count toward its own committed total, and
    precedent_resolve.resolve() merges them the same way the generator
    does, engine-dev scoping included.

    THE SHAPE THIS FIXES. A practice SET whose own practices/ tree IS a
    declared source (typically universal, `path: "."`) and which ALSO
    declares a repo-local source keeps that second source in its OWN
    separate directory (local/practices/) rather than merging it into
    practices/ -- committing a merged copy would duplicate text that
    source already owns (sources_for_tracked_block()'s own reasoning). So
    PRACTICES_DIR is this repo's own catalogue, not necessarily its whole
    COUNT. Reported 2026-09-18 against BestPractice: a universal source at
    "." (124 active) plus a repo-local source at "local" (5 active) made
    its own generated "11 of 129 practices" header -- verified correct by
    `build_views.py --check` -- read as stale by a check that only ever
    counted the 124 in PRACTICES_DIR.

    A repo whose declared sources are already fully materialized into
    PRACTICES_DIR never reaches the merge below -- but sources_for_tracked_
    block() alone does not say so: for a repo that is neither a practice
    source nor declared public, its own branch tracks EVERY declared
    source unconditionally (nothing is deferred there), so an ordinary
    private consumer declaring two or more already-materialized sources
    also gets `len(tracked) > 1`, the same as the shape above. What
    actually tells the two apart is whether ROOT is itself one of the
    tracked sources: precedent_materialize.py refuses to materialize a
    source living at its own --out directory (a consuming repo's
    materialize run always has out_dir == ROOT, so every tracked source's
    content already landed in PRACTICES_DIR), and forces exactly this
    shape's kind of source -- one whose own path IS out_dir -- to keep its
    extra content in a separate directory instead. So the merge below is
    only useful, and only entered, when some tracked source's path
    resolves to this same repository; otherwise PRACTICES_DIR already is
    the whole answer and re-resolving from scratch would just repeat, on
    fresh input, all the filtering (retired status, blocked overrides,
    engine-dev scoping) materialize() already applied once when it wrote
    what is on disk. Confusing `len(tracked) > 1` for that condition on its
    own reached this merge for an ordinary multi-source consumer with no
    self-referential source at all, and applied the same-repository-only
    exclusion below to a set of sources none of which was ROOT --
    stripping engine-dev-scoped practices a second time out of a total
    that had already excluded them on disk, undercounting a repo whose own
    AGENTS.md and practices/ agreed.

    Raises _UnresolvedSources when more than one source contributes and
    this environment cannot fully resolve all of them (the engine is
    unreachable, or a declared source is missing here) -- guessing either
    number in that situation risks exactly the false violation this
    exists to prevent.
    """
    declared = _declared_sources()
    # A single declared source can never resolve to more than one tracked
    # source below, whichever way sources_for_tracked_block() classifies
    # it -- so the common case (one source, or none) never needs the
    # engine at all, and an environment where it happens to be unreachable
    # must not report SKIPPED over a question this repo never asked.
    if not declared or len(declared) <= 1:
        return None
    for candidate in (ROOT / "tools", SOURCE_ROOT / "tools"):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
    try:
        import precedent_resolve as pr
    except Exception as e:
        raise _UnresolvedSources(
            f"this repo declares more than one source contributing to its "
            f"own practice count, but precedent_resolve.py could not be "
            f"imported ({e}) to resolve them")
    try:
        tracked, _deferred, _notes = pr.bv.sources_for_tracked_block(ROOT, declared)
    except Exception as e:
        raise _UnresolvedSources(
            f"{ROOT / 'precedent.json'}'s declared sources could not be "
            f"split into tracked and deferred ({e}), so this repo's own "
            f"practice count could not be resolved")
    if len(tracked) <= 1:
        return None
    # The condition the docstring above actually needs -- not merely more
    # than one tracked source, but ROOT itself being one of them. Every
    # other repo already has all of `tracked` merged into PRACTICES_DIR by
    # materialize() (out_dir == ROOT there), so re-resolving it here would
    # only repeat that work and, worse, re-apply the engine-dev-scope
    # exclusion below to a total that was already stripped once on disk.
    if not any(pr.bv._same_repository(s["path"], ROOT) for s in tracked):
        return None
    try:
        res = pr.resolve(tracked)
    except Exception as e:
        raise _UnresolvedSources(
            f"the {len(tracked)} sources this repo's own practice count is "
            f"built from could not be resolved ({e})")
    if res["missing"]:
        names = ", ".join(f"{m['name']!r} ({m['reason']})" for m in res["missing"])
        raise _UnresolvedSources(
            f"this repo's own practice count is built from {len(tracked)} "
            f"sources, and {names} could not be reached here, so it cannot "
            f"be verified")
    practices = res["practices"]
    if not any(s["level"] == "universal" and pr.bv._same_repository(s["path"], ROOT)
               for s in tracked):
        practices = {slug: v for slug, v in practices.items()
                     if not pr.bv._is_engine_dev_scoped(v["fm"])}
    return len(practices)


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
    try:
        resolved_total = _resolved_active_count()
    except _UnresolvedSources as e:
        raise CannotRun(str(e))
    if resolved_total is not None:
        actual = resolved_total
    else:
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
