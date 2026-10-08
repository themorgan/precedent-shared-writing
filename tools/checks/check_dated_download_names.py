#!/usr/bin/env python3
"""check_dated_download_names.py -- the mechanical check for
practices/dated-download-names.md.

# practice: dated-download-names

The rule's moment is a hand-over: a session sending a person a file. That
happens in a tool call, not in the tree, so this check makes sure the gate
on that tool call is in place rather than looking for files:

  1. tools/dated_name.py, where vendored, parses, cites this practice, and
     still tells a dated name from an undated one (a handful of fixed
     cases, run in-process);
  2. where the repository has a Claude Code .claude/settings.json, a
     PreToolUse hook on SendUserFile runs `dated_name.py --hook`, so an
     undated document is refused at the moment it would be sent. Wired in
     settings.json itself, or -- since 2026-10-07, when the engine stopped
     adding hooks there -- listed in process/practice_hooks.json, which the
     settings' fixed precedent-hooks.sh PreToolUse entry runs;
  3. every document the repository keeps FOR A READER is named with its
     date, the same way, so the file a reader downloads from the repository
     is as clearly dated as one sent. Which documents those are is the
     repository's outbox: OUTBOX.md at its root, one table row per document,
     whose File column links the file. Each listed file must exist -- a row
     whose file moved or vanished is a finding that names the last commit
     that had it -- and be dated. A repository with no OUTBOX.md falls back
     to its declared `output_paths` (precedent.json), minus `internal_paths`;
     with neither, no kept document is in scope (parts 1 and 2 still run).
     A document outside the outbox -- history, an as-filed record, someone
     else's source PDF, a book kept to search -- is not a download the
     repository produces, and keeps the name it has. (Alex Jacobson's
     alex137/BestPractice#927, 2026-10-06, adopted 2026-10-07.)

SKIPPED (exit 2) where tools/dated_name.py is not vendored. Whether a file
handed over some other way -- an attachment to an email, a link into the
repository -- carried its date is session judgment; the gate covers the
hand-over Claude Code makes itself.

Exit 0 and print nothing when clean; exit 1 with the practice's own Rule
text and the findings on a violation.

ROOT follows the materialized-path convention of the rest of tools/checks/
(tools/checks/<this> -> tools/checks -> tools -> repo root).
"""
import ast
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys

SOURCE_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ROOT = pathlib.Path(os.environ.get("PRECEDENT_CHECK_ROOT") or SOURCE_ROOT)
PRACTICE_FILE = SOURCE_ROOT / "practices" / "dated-download-names.md"
SCRIPT = ROOT / "tools" / "dated_name.py"
SETTINGS = ROOT / ".claude" / "settings.json"
PRACTICE_HOOKS = ROOT / "process" / "practice_hooks.json"

CASES = {
    "Joseph Manuscript-2026-12-31.docx": True,
    "Joseph Manuscript - 2026-12-31.docx": True,
    "joseph-manuscript.docx": False,
    "report_2026-12-31.pdf": False,      # underscore is not one of the forms
    "report-2026-13-45.pdf": False,      # not a real date
    "report-2026-12-31-final.pdf": False,  # the date is not last
}


def rule_text() -> str:
    if not PRACTICE_FILE.is_file():
        return "(practice file not found -- has it been materialized?)"
    text = PRACTICE_FILE.read_text(encoding="utf-8")
    m = re.search(r"## Rule\n(.*?)\n## ", text, re.S)
    return m.group(1).strip() if m else "(no Rule found)"


def hook_wired(settings: dict) -> bool:
    for entry in (settings.get("hooks") or {}).get("PreToolUse") or []:
        matcher = entry.get("matcher") or ""
        try:
            if not re.fullmatch(matcher, "SendUserFile"):
                continue
        except re.error:
            continue
        for h in entry.get("hooks") or []:
            cmd = h.get("command") or ""
            if "dated_name.py" in cmd and "--hook" in cmd:
                return True
    return False


def registered_hook(settings: dict) -> bool:
    """True when process/practice_hooks.json lists the hand-over hook and
    settings.json runs the list at PreToolUse (precedent-hooks.sh)."""
    try:
        listed = json.loads(PRACTICE_HOOKS.read_text(encoding="utf-8")).get("hooks") or []
    except (OSError, ValueError, AttributeError):
        return False
    on_list = any(isinstance(h, dict) and h.get("event") == "PreToolUse"
                  and "dated_name.py" in str(h.get("command") or "")
                  and "--hook" in str(h.get("command") or "")
                  and _matches(h.get("matcher") or "") for h in listed)
    runs_list = any("precedent-hooks.sh PreToolUse" in (h.get("command") or "")
                    for entry in (settings.get("hooks") or {}).get("PreToolUse") or []
                    for h in entry.get("hooks") or [])
    return on_list and runs_list


NOTES = []


def engine_wires_hooks() -> bool:
    """True when this repository's engine wires a practice's declared
    hooks at sync: tools/precedent_hooks.py (the per-event list, since
    2026-10-07), or add_practice_hooks in the vendored engine (since
    2026-10-06). An older engine cannot, so the missing hook is its to
    bring, not a finding against the repository."""
    if (ROOT / "tools" / "precedent_hooks.py").is_file():
        return True
    try:
        return "def add_practice_hooks" in (ROOT / "tools" / "precedent_vendor_engine.py").read_text(
            encoding="utf-8", errors="ignore")
    except OSError:
        return False


def _matches(matcher: str) -> bool:
    try:
        return bool(re.fullmatch(matcher, "SendUserFile"))
    except re.error:
        return False


OUTBOX = "OUTBOX.md"
_LINK = re.compile(r"\]\(([^)\s]+)\)")


def _declared(key: str) -> list:
    try:
        got = json.loads((ROOT / "precedent.json").read_text(encoding="utf-8")).get(key) or []
    except (OSError, ValueError, AttributeError):
        return []
    return [str(x).strip("/") for x in got if str(x).strip("/")] if isinstance(got, list) else []


def _under(rel: str, dirs: list) -> bool:
    return any(rel == d or rel.startswith(d + "/") for d in dirs)


def outbox_files():
    """The files OUTBOX.md lists, repo-relative, or None when there is no
    OUTBOX.md. A row is a markdown table row; its File column is the first
    cell holding a relative link (a link with a scheme is skipped)."""
    path = ROOT / OUTBOX
    if not path.is_file():
        return None
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("|") or set(line.strip()) <= set("|-: "):
            continue
        for cell in line.strip().strip("|").split("|"):
            m = _LINK.search(cell)
            if m and "://" not in m.group(1) and not m.group(1).startswith("#"):
                out.append(m.group(1).split("#", 1)[0])
                break
    return out


def _last_commit(rel: str) -> str:
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%h %as",
                            "HEAD", "--", rel], capture_output=True, text=True)
        return r.stdout.strip()
    except OSError:
        return ""


def kept_for_readers() -> tuple:
    """-> (documents a reader is meant to get, findings about the outbox)."""
    listed = outbox_files()
    if listed is not None:
        present = [rel for rel in listed if (ROOT / rel).is_file()]
        findings = []
        for rel in (r for r in listed if r not in present):
            last = _last_commit(rel)
            findings.append(f"{OUTBOX} lists {rel}, which is not in the tree"
                            + (f" (last seen in commit {last}: `git show "
                               f"{last.split()[0]}:{rel}`)" if last else "")
                            + " -- point the row at where the document is now, or drop it")
        return present, findings
    outputs, internals = _declared("output_paths"), _declared("internal_paths")
    if not outputs:
        return [], []
    return [p for p in kept_files() if _under(p, outputs) and not _under(p, internals)], []


def kept_files() -> list:
    """The repository's tracked files; every file, where it is not a git
    checkout (a test fixture)."""
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"],
                             capture_output=True, text=True, check=True).stdout
        return [p for p in out.split("\0") if p]
    except (OSError, subprocess.CalledProcessError):
        return [str(p.relative_to(ROOT)) for p in ROOT.rglob("*")
                if p.is_file() and ".git" not in p.relative_to(ROOT).parts]


def find_violations() -> list:
    findings = []
    rel = SCRIPT.relative_to(ROOT)
    source = SCRIPT.read_text(encoding="utf-8")
    try:
        ast.parse(source, filename=str(SCRIPT))
    except SyntaxError as e:
        return [f"{rel} does not parse as Python: {e}"]
    if "practice: dated-download-names" not in source:
        findings.append(f"{rel} does not cite this practice (practice: code-cites-practice)")

    spec = importlib.util.spec_from_file_location("dated_name", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        for name, want in CASES.items():
            if mod.is_dated(name) != want:
                findings.append(
                    f"{rel} reads {name!r} as "
                    f"{'dated' if not want else 'undated'}; it should be the opposite"
                )

        kept, outbox_findings = kept_for_readers()
        findings.extend(outbox_findings)
        for name in mod.undated(kept):
            findings.append(
                f"{name} is a document kept for download with no date in its "
                "name -- its builder should save it as <name>-YYYY-MM-DD"
                "<extension> (dated_name.replace() says where, and which "
                "older copy it retires)"
            )
    except Exception as e:  # a broken tool is a finding, not a crash
        findings.append(f"{rel} could not be loaded: {e}")

    if SETTINGS.is_file():
        try:
            settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
        except ValueError as e:
            findings.append(f"{SETTINGS.relative_to(ROOT)} is not valid JSON: {e}")
        else:
            if not (hook_wired(settings) or registered_hook(settings)):
                if not engine_wires_hooks():
                    # An engine older than wiring a practice's `hooks:` cannot
                    # satisfy this, and the repo may not be allowed to edit
                    # its own settings by hand: a note, never a refusal
                    # (2026-10-07, an unrelated merge refused in a consumer).
                    NOTES.append(
                        f"{SETTINGS.relative_to(ROOT)} does not run the hand-over "
                        "hook yet, and this repository's engine predates wiring "
                        "a practice's hooks: run Update Vendors, which wires it")
                    return findings
                findings.append(
                    f"{SETTINGS.relative_to(ROOT)} has no PreToolUse hook on "
                    "SendUserFile running dated_name.py --hook, so an undated "
                    "document can be handed over. Add to hooks.PreToolUse:\n"
                    '    {"matcher": "SendUserFile", "hooks": [{"type": "command", '
                    '"command": "python3 $CLAUDE_PROJECT_DIR/tools/dated_name.py --hook"}]}'
                )
    return findings


if __name__ == "__main__":
    if not SCRIPT.is_file():
        print(f"SKIPPED: {SCRIPT.relative_to(ROOT)} is not vendored in this repo")
        sys.exit(2)
    findings = find_violations()
    for note in NOTES:
        print(f"NOTE: {note}")
    if findings:
        print("VIOLATION: dated-download-names")
        for f in findings:
            print(f"  {f}")
        print("\nthe rule:")
        print("  " + rule_text().replace("\n", "\n  "))
        sys.exit(1)
    sys.exit(0)
