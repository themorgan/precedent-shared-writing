#!/usr/bin/env python3
"""check_create_word_doc.py -- the mechanical check for
practices/create-word-doc.md.

# practice: create-word-doc

Scope: purely structural, and conditional on the script actually being
vendored here. `tools/create_word_doc.py` travels by copy, not by
materialization (see the practice's own Detail section), so a repo in
this set may legitimately never have it -- that repo is doing every Word
export as a hand-built one-off, which the Rule explicitly allows. SKIPPED
(exit 2), not a violation, in that case.

Where the script IS present: it must be syntactically valid Python,
non-trivial in size (catching an accidental deletion or a truncated
re-copy), and must cite this practice. It cannot check the Rule's own
behavior -- that a session actually reached for this script instead of
writing a fresh one, that a generated .docx was reviewed before being
handed over, or that a hand-built one-off carried a footer at all -- that
is session judgment.

Exit 0 and print nothing when clean. Exit 1 and print the practice's own
Rule text (never a paraphrase) plus the specific finding(s) on a
violation. Exit 2 (SKIPPED) when the script isn't vendored here.

Note on ROOT: materialized (copied byte-for-byte) into tools/checks/ of
any consuming repo by precedent_materialize.py -- it never runs from this
set's own tools/checks/ in place, so parent.parent.parent is written
correct for the MATERIALIZED path (tools/checks/check_create_word_doc.py
-> tools/checks -> tools -> repo root), same convention as the rest of
tools/checks/.
"""
import ast
import os
import pathlib
import re
import sys

SOURCE_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ROOT = pathlib.Path(os.environ.get("PRECEDENT_CHECK_ROOT") or SOURCE_ROOT)
PRACTICE_FILE = SOURCE_ROOT / "practices" / "create-word-doc.md"
SCRIPT = ROOT / "tools" / "create_word_doc.py"

MIN_BYTES = 4_000


def rule_text() -> str:
    if not PRACTICE_FILE.is_file():
        return "(practice file not found -- has it been materialized?)"
    text = PRACTICE_FILE.read_text(encoding="utf-8")
    m = re.search(r"## Rule\n(.*?)\n## ", text, re.S)
    return m.group(1).strip() if m else "(no Rule found)"


def find_violations() -> list[str]:
    findings = []

    size = SCRIPT.stat().st_size
    if size < MIN_BYTES:
        findings.append(
            f"{SCRIPT.relative_to(ROOT)} is only {size} bytes "
            f"(expected at least {MIN_BYTES}) -- looks truncated"
        )

    source = SCRIPT.read_text(encoding="utf-8")
    try:
        ast.parse(source, filename=str(SCRIPT))
    except SyntaxError as e:
        findings.append(f"{SCRIPT.relative_to(ROOT)} does not parse as Python: {e}")

    if "practice: create-word-doc" not in source:
        findings.append(
            f"{SCRIPT.relative_to(ROOT)} does not cite this practice "
            "(practice: code-cites-practice)"
        )

    return findings


if __name__ == "__main__":
    if not SCRIPT.is_file():
        print(
            f"SKIPPED: {SCRIPT.relative_to(ROOT)} is not vendored in this "
            "repo -- nothing to check (see the practice's own Detail "
            "section on vendoring by copy)"
        )
        sys.exit(2)

    findings = find_violations()
    if findings:
        print("VIOLATION: create-word-doc")
        for f in findings:
            print(f"  {f}")
        print("\nthe rule:")
        print("  " + rule_text().replace("\n", "\n  "))
        sys.exit(1)
    sys.exit(0)
