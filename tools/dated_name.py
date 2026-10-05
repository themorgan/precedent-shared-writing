#!/usr/bin/env python3
"""dated_name.py -- a document handed over for download carries its date at
the end of its name, just before the extension.

# practice: dated-download-names

Two accepted forms, nothing else:

  Joseph Manuscript-2026-12-31.docx
  Joseph Manuscript - 2026-12-31.docx

Three ways in:

  python3 tools/dated_name.py FILE... --to DIR [--date YYYY-MM-DD] [--spaced]
      Copy each FILE into DIR under its dated name and print the new path.
      The way to hand over a file the repository keeps under a fixed name
      (book-joseph/output/holy-hardball-joseph-manuscript.docx): the
      repository copy stays put, and the person receives
      holy-hardball-joseph-manuscript-2026-10-05.docx. A FILE whose name is
      already dated is copied as it is. The date defaults to today in the
      person's own zone (tools/precedent_time.py), never the container's.

  python3 tools/dated_name.py --check NAME...
      Exit 1, naming each one, if any NAME is a downloadable document whose
      name is not dated. Exit 0 otherwise.

  python3 tools/dated_name.py --hook
      A Claude Code PreToolUse hook on SendUserFile: reads the hook's JSON
      on stdin and refuses (exit 2, reason on stderr) a call that would hand
      over an undated document, saying how to make the dated copy. Wired in
      a repository's .claude/settings.json; check_dated_download_names.py
      fails where this tool is vendored and the hook is not wired.

"Downloadable document" is the DOC_EXTENSIONS list below -- a file a
reader saves and opens elsewhere. Images, web pages, source code and plain
text files are not on it: a screenshot or a page rendered in the side panel
is looked at, not filed away.
"""
import argparse
import datetime
import json
import pathlib
import re
import shutil
import sys

DOC_EXTENSIONS = frozenset({
    ".docx", ".doc", ".dotx", ".pdf", ".xlsx", ".xls", ".xlsm", ".csv",
    ".pptx", ".ppt", ".odt", ".ods", ".odp", ".rtf", ".epub",
    ".pages", ".numbers", ".key",
})

# The date, then the extension: "-2026-12-31" or " - 2026-12-31".
DATED_STEM_RE = re.compile(r"(?:-| - )(\d{4}-\d{2}-\d{2})$")


def is_document(name) -> bool:
    return pathlib.PurePath(str(name)).suffix.lower() in DOC_EXTENSIONS


def is_dated(name) -> bool:
    """True when the file name ends in a real date just before its extension."""
    m = DATED_STEM_RE.search(pathlib.PurePath(str(name)).stem)
    if not m:
        return False
    try:
        datetime.date.fromisoformat(m.group(1))
    except ValueError:
        return False
    return True


def today(root=None) -> str:
    """Today in the person's zone, from the engine's one time emitter."""
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import precedent_time  # practice: timestamps-carry-offset
    return precedent_time.today(root)


def dated_name(name, date=None, spaced=False) -> str:
    """NAME with the date added before its extension; unchanged if dated."""
    p = pathlib.PurePath(str(name))
    if is_dated(p.name):
        return p.name
    date = date or today()
    datetime.date.fromisoformat(date)  # refuse a malformed --date
    sep = " - " if spaced else "-"
    return f"{p.stem}{sep}{date}{p.suffix}"


def undated(names) -> list:
    return [n for n in names if is_document(n) and not is_dated(n)]


def hook() -> int:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    if payload.get("tool_name") != "SendUserFile":
        return 0
    files = (payload.get("tool_input") or {}).get("files") or []
    bad = undated(str(f) for f in files)
    if not bad:
        return 0
    script = pathlib.Path(__file__).resolve()
    lines = [
        "dated-download-names: a document handed over for download carries "
        "its date at the end of its name, before the extension "
        "(Name-2026-12-31.docx or Name - 2026-12-31.docx). Not dated:",
    ]
    lines += [f"  {f}" for f in bad]
    lines.append(
        "Make a dated copy in the scratchpad and send that instead -- the "
        f"repository copy keeps its own name:\n  python3 {script} "
        + " ".join(f'"{f}"' for f in bad)
        + " --to <your scratchpad directory>"
    )
    print("\n".join(lines), file=sys.stderr)
    return 2


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("files", nargs="*", help="files to copy, or names to check")
    ap.add_argument("--to", type=pathlib.Path, help="directory to copy into")
    ap.add_argument("--date", help="YYYY-MM-DD (default: today, your zone)")
    ap.add_argument("--spaced", action="store_true",
                    help='"Name - 2026-12-31.docx" rather than "Name-2026-12-31.docx"')
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any name is an undated document")
    ap.add_argument("--hook", action="store_true",
                    help="run as a PreToolUse hook on SendUserFile")
    args = ap.parse_args(argv)

    if args.hook:
        return hook()
    if args.check:
        bad = undated(args.files)
        for n in bad:
            print(f"not dated: {n}")
        return 1 if bad else 0
    if not args.files or args.to is None:
        ap.error("give FILE... and --to DIR (or --check, or --hook)")

    date = args.date or today()
    args.to.mkdir(parents=True, exist_ok=True)
    for f in args.files:
        src = pathlib.Path(f)
        if not src.is_file():
            print(f"dated_name: no such file: {src}", file=sys.stderr)
            return 1
        dest = args.to / dated_name(src.name, date, args.spaced)
        shutil.copy2(src, dest)
        print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
