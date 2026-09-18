#!/usr/bin/env python3
"""check_curly_quotes.py -- the mechanical check for
practices/curly-quotes.md.

# practice: curly-quotes

Scope: every tracked markdown file under a consuming repo's own declared
`output_paths` (precedent.json), minus any `internal_paths` -- the same
generic boundary `deliverables-carry-no-process`'s own check already
reads, so "outward" never drifts between the two rules. A repo that
declares no `output_paths` has nothing in scope here: SKIPPED (exit 2),
never a pass and never a violation -- an undeclared scope is not the same
claim as "nothing here leaks straight quotes" (same discipline as
check_deliverables_carry_no_process.py's own docstring explains).

For each in-scope file, strip fenced code, inline code spans, link
targets and autolinks (a URL or a path is never prose), then look for a
straight `"` or `'` in what's left. A path listed in the repo's own
declared `curly_quotes_grandfathered` (precedent.json) is skipped
entirely -- see the practice's own Detail section for why that list lives
in the consuming repo, never hardcoded here.

Exit 0 and print nothing when clean. Exit 1 and print the practice's own
Rule text plus the specific finding(s) otherwise. Exit 2 (SKIPPED) when
the repo declares no output_paths, or when output_paths is declared but
nothing tracked was actually in scope.
"""
import json
import os
import pathlib
import re
import subprocess
import sys

SOURCE_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ROOT = pathlib.Path(os.environ.get("PRECEDENT_CHECK_ROOT") or SOURCE_ROOT)
PRACTICE_FILE = SOURCE_ROOT / "practices" / "curly-quotes.md"

FENCE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
LINK_URL_RE = re.compile(r"\]\([^)]*\)")
AUTOLINK_RE = re.compile(r"<https?://[^>]*>")
STRAIGHT_QUOTE_RE = re.compile(r'["\']')


def rule_text() -> str:
    if not PRACTICE_FILE.is_file():
        return "(practice file not found -- has it been materialized?)"
    text = PRACTICE_FILE.read_text(encoding="utf-8")
    body = text.split("## Rule", 1)[-1]
    return body.split("\n## ", 1)[0].strip()


def _declared(key):
    cfg = ROOT / "precedent.json"
    if not cfg.is_file():
        return []
    try:
        return json.loads(cfg.read_text(encoding="utf-8")).get(key) or []
    except Exception:
        return []


def _in_scope(rel, outputs, internals):
    if not any(rel == o or rel.startswith(o.rstrip("/") + "/") for o in outputs):
        return False
    return not any(rel == i or rel.startswith(i.rstrip("/") + "/") for i in internals)


class CannotRun(Exception):
    """This check could not run here. Reported as SKIPPED (exit 2), never
    as a violation and never as a pass."""


def _tracked_markdown():
    try:
        out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT,
                              capture_output=True, text=True, check=True).stdout
    except Exception as e:
        raise CannotRun(f"`git ls-files` could not list tracked files under "
                         f"{ROOT} ({e}), so there is no file set to scan -- "
                         f"an empty scan is not a clean one")
    return [p for p in out.splitlines() if p]


def prose_only(text):
    text = FENCE_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    text = LINK_URL_RE.sub("", text)
    text = AUTOLINK_RE.sub("", text)
    return text


def main() -> int:
    outputs = _declared("output_paths")
    if not outputs:
        print("SKIPPED: this repo declares no output_paths, so no document "
              "here is marked as written for an outside reader")
        return 2

    internals = _declared("internal_paths")
    grandfathered = set(_declared("curly_quotes_grandfathered"))

    try:
        tracked = _tracked_markdown()
    except CannotRun as e:
        print(f"SKIPPED: {e}")
        return 2

    findings, scanned = [], 0
    for rel in tracked:
        if not _in_scope(rel, outputs, internals):
            continue
        scanned += 1
        if rel in grandfathered:
            continue
        path = ROOT / rel
        text = path.read_text(encoding="utf-8", errors="replace")
        n = len(STRAIGHT_QUOTE_RE.findall(prose_only(text)))
        if n:
            findings.append(
                f"  {rel}: {n} straight quote character(s) in prose scope "
                f"(outside code spans, fences, and link targets)"
            )

    if findings:
        print("VIOLATION: curly-quotes")
        for f in findings:
            print(f)
        print("\nthe rule:")
        print("  " + rule_text().replace("\n", "\n  "))
        return 1

    if not scanned:
        print(f"SKIPPED: this repo declares {len(outputs)} output path(s) "
              f"({', '.join(sorted(outputs))}) but no tracked markdown file "
              f"under them was in scope -- either nothing is there, or "
              f"every document found was under a declared internal_path. "
              f"Nothing was scanned")
        return 2

    print(f"OK: {scanned} output document(s) across {len(outputs)} declared "
          f"output path(s) scanned, {len(grandfathered)} grandfathered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
