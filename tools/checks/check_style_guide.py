#!/usr/bin/env python3
"""check_style_guide.py -- the mechanical check for
practices/visual-style-guide.md, and the generator of the guide it checks.

# practice: visual-style-guide

Scope: tree. Reads the audited repository's own visual practices
(visual-logo, visual-palette, visual-type, visual-imagery) from its
repo-local source -- the values are that project's, never this set's --
and refuses:

  - a missing one, or one whose ## Rule lacks the shape the practice names;
  - a style guide that is missing or differs from what --write would build;
  - in every file the palette's applies_to matches, minus the sketches the
    logo practice declares: a hex color outside the palette, a gradient
    when the palette says "No gradients.", a font outside the type table,
    and an <img> of a logo file shown under its smallest size.

Run: python3 tools/checks/check_style_guide.py           # check
     python3 tools/checks/check_style_guide.py --print   # print the guide
     python3 tools/checks/check_style_guide.py --write   # rewrite the guide

Exit 0 silent when clean, 1 with findings, 2 (SKIPPED, with the reason)
when it cannot run -- including a repo that declares no visual identity,
which is a normal state and not a pass.
"""
import json
import os
import pathlib
import re
import subprocess
import sys

# SOURCE_ROOT is the practice set this script ships in (its rule text sits
# beside it); ROOT is the repository it audits. See check_draft_marker.py.
SOURCE_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ROOT = pathlib.Path(os.environ.get("PRECEDENT_CHECK_ROOT") or SOURCE_ROOT)
PRACTICE_FILE = SOURCE_ROOT / "practices" / "visual-style-guide.md"
SECTIONS = [("Logo", "visual-logo"), ("Color", "visual-palette"),
            ("Type", "visual-type"), ("Imagery", "visual-imagery")]
COMMAND = "python3 tools/checks/check_style_guide.py --write"
STRENGTH_WORDS = {"assented": "decided weakly", "decided": "decided"}

HEX_RE = re.compile(r"#([0-9a-fA-F]{8}|[0-9a-fA-F]{6})\b"
                    r"|(?::\s*|(?:fill|stroke|color|stop-color)=[\"'])#([0-9a-fA-F]{3})\b")
GRADIENT_RE = re.compile(r"(linear|radial|conic)-gradient|<(linear|radial)Gradient", re.I)
LOAD_RE = re.compile(r"fonts\.googleapis\.com/css2?\?[^\"'\s>]*")
FAMILY_PARAM_RE = re.compile(r"family=([^&:\"'\s]+)")
DECL_RE = re.compile(r"font-family\s*[:=]\s*[\"']?([^;}\"'\n]*(?:[\"'][^\"']*[\"'][^;}\"'\n]*)*)")
GENERIC = {"inherit", "initial", "unset", "serif", "sans-serif", "monospace", "system-ui",
           "ui-monospace", "ui-serif", "ui-sans-serif"}
IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
LINK_RE = re.compile(r"(\]\()([^)\s]+)(\))")
LOGO_LINES = [
    (r"\*\*(?!One\b)\w+ colou?rs?\b", "a line for the mark's colors (e.g. **Two colors:**)"),
    (r"\*\*One colou?r\b", "a **One color** line"),
    (r"\*\*Smallest size:?\*\*[^\n]*?\d+\s*px", "a **Smallest size:** line with a size in px"),
    (r"\*\*Clear space:?\*\*", "a **Clear space:** line"),
    (r"\*\*Lockup:?\*\*", "a **Lockup:** line"),
    (r"\*\*Don['’]?t\*\*", "a **Don't** line"),
]


class CannotRun(Exception):
    """Reported as SKIPPED (exit 2), never as a violation."""


def rule_section(text):
    if "## Rule" not in text:
        return ""
    return text.split("## Rule", 1)[1].split("\n## ", 1)[0].strip()


def frontmatter(text):
    parts = text.split("---\n", 2)
    return parts[1] if len(parts) == 3 and not parts[0].strip() else ""


def table(rule, first, second):
    """Rows (as cell lists) of the first markdown table whose header starts
    with the columns `first` and `second`."""
    rows, inside = [], False
    for line in rule.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            if inside:
                break
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not inside:
            if len(cells) >= 2 and cells[0].lower() == first and cells[1].lower() == second:
                inside = True
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        rows.append(cells)
    return rows


def local_practices_dir():
    cfg = ROOT / "precedent.json"
    if not cfg.is_file():
        raise CannotRun(f"no precedent.json at {ROOT}, so no repo-local source to read")
    try:
        sources = json.loads(cfg.read_text(encoding="utf-8")).get("sources") or []
    except ValueError as e:
        raise CannotRun(f"precedent.json does not parse: {e}")
    for s in sources:
        if s.get("level") == "repo-local" and s.get("path"):
            return (ROOT / s["path"] / "practices").resolve()
    raise CannotRun("precedent.json declares no repo-local source, so no visual identity here")


def load():
    """-> {slug: (path, text)} for the visual practices that exist."""
    d = local_practices_dir()
    found = {slug: (d / f"{slug}.md") for _, slug in SECTIONS}
    found = {slug: (p, p.read_text(encoding="utf-8")) for slug, p in found.items() if p.is_file()}
    if not found:
        raise CannotRun(f"no visual identity declared here (none of "
                        f"{', '.join(s for _, s in SECTIONS)} in {d.relative_to(ROOT) if d.is_relative_to(ROOT) else d})")
    return found


def guide_path():
    return (ROOT / "content" / "VISUAL_STYLE_GUIDE.md") if (ROOT / "content").is_dir() \
        else ROOT / "VISUAL_STYLE_GUIDE.md"


def origin_blob_prefixes():
    try:
        url = subprocess.run(["git", "-C", str(ROOT), "remote", "get-url", "origin"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    if not m:
        return None
    return re.compile(rf"https://github\.com/{re.escape(m.group(1))}/{re.escape(m.group(2))}"
                      r"/(?:blob|tree)/[^/]+/(.+)$", re.I)


def relink(rule, practice_dir, guide_dir, blob_re):
    """Make links work from the guide: a GitHub URL into this repository and
    a link relative to the practice both become relative to the guide."""
    def fix(m):
        target = m.group(2)
        path, anchor = (target.split("#", 1) + [""])[:2]
        if blob_re and blob_re.match(path):
            dest = ROOT / blob_re.match(path).group(1)
        elif path and not re.match(r"[a-z]+:|/", path):
            dest = (practice_dir / path).resolve()
        else:
            return m.group(0)
        rel = os.path.relpath(dest, guide_dir).replace(os.sep, "/")
        if target.endswith("/") and not rel.endswith("/"):
            rel += "/"
        return m.group(1) + rel + (f"#{anchor}" if anchor else "") + m.group(3)
    return LINK_RE.sub(fix, rule)


def logo_facts(rule):
    rows = table(rule, "file", "use")
    files = []  # (relative link, use)
    for r in rows:
        for link in re.findall(r"\]\(([^)\s]+)\)", r[0]):
            files.append((link, r[1].lower() if len(r) > 1 else ""))
    name = re.search(r"\*\*The mark is (.+?):\*\*", rule)
    size = re.search(r"\*\*Smallest size:?\*\*[^\n]*?(\d+)\s*px", rule)
    sketch = re.search(r"\*\*Sketches:\*\*\s*files in `([^`]+?)/?`\s*not named `([^`*]+)\*`", rule)
    return {"rows": rows, "files": files, "name": name.group(1) if name else None,
            "min_px": int(size.group(1)) if size else None,
            "sketch": (sketch.group(1).strip("/"), sketch.group(2)) if sketch else None}


def render(found):
    guide = guide_path()
    blob_re = origin_blob_prefixes()
    logo_path, logo_text = found["visual-logo"]
    fm = frontmatter(logo_text)
    facts = logo_facts(rule_section(logo_text))
    sources = ", ".join(os.path.relpath(found[s][0], ROOT).replace(os.sep, "/") for _, s in SECTIONS)
    out = [f"<!-- Generated by tools/checks/check_style_guide.py from {sources}. "
           f"Do not edit: change the practice, then run {COMMAND} -->",
           "# Visual style guide", ""]
    light = next((f for f, use in facts["files"] if "light" in use), None)
    if light:
        src = relink(f"]({light})", logo_path.parent, guide.parent, blob_re)[2:-1]
        alt = f"The logo, {facts['name']}" if facts["name"] else "The logo"
        out += [f'<img src="{src}" alt="{alt}" width="160">', ""]
    strength = re.search(r"\(strength: (\w+)\)", fm)
    added = re.search(r"^added:\s*\"?([0-9-]+)", fm, re.M)
    when = added.group(1) if added else "date not recorded"
    if strength:
        s = strength.group(1)
        out.append(f"**Status:** {STRENGTH_WORDS.get(s, s)} (strength: `{s}`), {when}.")
    else:
        out.append(f"**Status:** recorded {when}; decision strength not recorded.")
    for heading, slug in SECTIONS:
        path, text = found[slug]
        out += ["", f"## {heading}", "",
                relink(rule_section(text), path.parent, guide.parent, blob_re)]
    return "\n".join(out) + "\n"


def shape_findings(found):
    hits = []
    for _, slug in SECTIONS:
        if slug not in found:
            hits.append(f"{slug}: missing -- a visual identity is all four practices")
    if hits:
        return hits
    rule = {slug: rule_section(t) for slug, (_, t) in found.items()}
    for slug in rule:
        if not rule[slug]:
            hits.append(f"{slug}: no ## Rule section")
    if hits:
        return hits
    f = logo_facts(rule["visual-logo"])
    if not f["name"]:
        hits.append("visual-logo: does not open with **The mark is NAME:**")
    uses = [u for _, u in f["files"]]
    for want, test in (("a light row", lambda u: "light" in u), ("a dark row", lambda u: "dark" in u),
                       ("a small-size row", lambda u: re.search(r"favicon|under|small", u))):
        if not any(test(u) for u in uses):
            hits.append(f"visual-logo: the | File | Use | table has no {want} with a linked file")
    for rx, what in LOGO_LINES:
        if not re.search(rx, rule["visual-logo"]):
            hits.append(f"visual-logo: no {what}")
    if "**Sketches:**" in rule["visual-logo"] and not f["sketch"]:
        hits.append("visual-logo: the **Sketches:** line is not in the form "
                    "files in `<folder>/` not named `<prefix>*`")
    rows = table(rule["visual-palette"], "name", "light")
    if not rows:
        hits.append("visual-palette: no | Name | Light | Dark | Use | table")
    for r in rows:
        for cell in r[1:3]:
            if not re.fullmatch(r"`#[0-9a-fA-F]{6}`", cell):
                hits.append(f"visual-palette: {r[0]}: {cell or '(empty)'} is not a six-digit hex in backticks")
    grad = [bool(re.search(r"\bNo gradients\.", rule["visual-palette"])),
            bool(re.search(r"\bGradients allowed\.", rule["visual-palette"]))]
    if sum(grad) != 1:
        hits.append("visual-palette: says neither (or both) `No gradients.` and `Gradients allowed.`")
    if not palette_scope(found):
        hits.append("visual-palette: applies_to names no files, so nothing is checked against it")
    rows = table(rule["visual-type"], "role", "face")
    faces = [r for r in rows if len(r) > 1 and re.search(r"`[^`]+`", r[1])]
    if not any("head" in r[0].lower() for r in faces) or not any("body" in r[0].lower() for r in faces):
        hits.append("visual-type: the | Role | Face | table needs a headings row and a body row, "
                    "each face in backticks")
    if not re.search(r"^\s*-\s*\*\*Show", rule["visual-imagery"], re.M):
        hits.append("visual-imagery: no bullet opening **Show")
    if not re.search(r"^\s*-\s*\*\*(No|Avoid)\b", rule["visual-imagery"], re.M):
        hits.append("visual-imagery: no bullet opening **No or **Avoid")
    return hits


def palette_scope(found):
    m = re.search(r"^applies_to:\s*(\[.*\])\s*$", frontmatter(found["visual-palette"][1]), re.M)
    try:
        return [g for g in json.loads(m.group(1)) if g] if m else []
    except ValueError:
        return []


def glob_regex():
    for candidate in (ROOT / "tools", SOURCE_ROOT / "tools"):
        if (candidate / "precedent_paths.py").is_file():
            sys.path.insert(0, str(candidate))
            break
    try:
        from precedent_paths import _glob_regex
    except ImportError:
        raise CannotRun("the vendored engine's tools/precedent_paths.py is not here, "
                        "so the palette's applies_to cannot be matched")
    return _glob_regex


def visual_files(found):
    globs = palette_scope(found)
    rx = [glob_regex()(g) for g in globs]
    sketch = logo_facts(rule_section(found["visual-logo"][1]))["sketch"]
    for path in sorted(ROOT.rglob("*")):
        if ".git" in path.relative_to(ROOT).parts or not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if not any(r.fullmatch(rel) for r in rx):
            continue
        if sketch and rel.startswith(sketch[0] + "/") and not path.name.startswith(sketch[1]):
            continue
        yield rel, path


def use_findings(found):
    rule = {slug: rule_section(t) for slug, (_, t) in found.items()}
    colors = {h.lower() for r in table(rule["visual-palette"], "name", "light")
              for h in re.findall(r"`#([0-9a-fA-F]{6})`", " ".join(r[1:3]))}
    no_gradients = bool(re.search(r"\bNo gradients\.", rule["visual-palette"]))
    faces = {f.lower() for r in table(rule["visual-type"], "role", "face") if len(r) > 1
             for f in re.findall(r"`([^`]+)`", r[1])}
    facts = logo_facts(rule["visual-logo"])
    big_logos = {os.path.basename(f) for f, use in facts["files"]
                 if not re.search(r"favicon|under|small", use)}
    hits = []
    for rel, path in visual_files(found):
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for m in HEX_RE.finditer(line):
                h = (m.group(1) or m.group(2)).lower()
                full = "".join(c * 2 for c in h) if len(h) == 3 else h[:6]
                if full not in colors:
                    hits.append(f"{rel}:{n}: #{h} is not in the palette")
            if no_gradients and GRADIENT_RE.search(line):
                hits.append(f"{rel}:{n}: a gradient, and the palette says none")
            for url in LOAD_RE.findall(line):
                for fam in FAMILY_PARAM_RE.findall(url):
                    fam = fam.replace("+", " ")
                    if fam.lower() not in faces:
                        hits.append(f"{rel}:{n}: loads the font \"{fam}\", not in the type table")
            for decl in DECL_RE.findall(line):
                first = decl.split(",")[0].strip().strip("\"'").strip()
                if first and not first.startswith("var(") and first.lower() not in faces | GENERIC:
                    hits.append(f"{rel}:{n}: font-family \"{first}\" is not in the type table")
            if facts["min_px"]:
                for tag in IMG_RE.findall(line):
                    src = re.search(r"\bsrc=[\"']?([^\"'\s>]+)", tag)
                    if not src or os.path.basename(src.group(1).split("?")[0]) not in big_logos:
                        continue
                    for dim, val in re.findall(r"\b(width|height)=[\"']?(\d+)", tag):
                        if int(val) < facts["min_px"]:
                            hits.append(f"{rel}:{n}: logo shown at {dim} {val}px, under the "
                                        f"smallest size of {facts['min_px']}px -- use the small-size file")
    return hits


def main():
    try:
        found = load()
        hits = shape_findings(found)
        if not hits:
            guide = render(found)
            target = guide_path()
            if "--print" in sys.argv:
                sys.stdout.write(guide)
                return 0
            if "--write" in sys.argv:
                if not target.is_file() or target.read_text(encoding="utf-8") != guide:
                    target.write_text(guide, encoding="utf-8")
                    print(f"visual-style-guide: regenerated {target.relative_to(ROOT)}", file=sys.stderr)
                return 0
            if not target.is_file():
                hits.append(f"{target.relative_to(ROOT)}: missing -- run {COMMAND}")
            elif target.read_text(encoding="utf-8") != guide:
                hits.append(f"{target.relative_to(ROOT)}: differs from its practices -- "
                            f"change the practice, never the guide, then run {COMMAND}")
            hits += use_findings(found)
        elif "--write" in sys.argv or "--print" in sys.argv:
            print("cannot build the guide until the practices have the right shape:", file=sys.stderr)
    except CannotRun as e:
        print(f"SKIPPED: {e}")
        return 2
    if not hits:
        return 0
    print(f"VIOLATION: {PRACTICE_FILE.stem}")
    for h in hits:
        print(f"  {h}")
    if PRACTICE_FILE.is_file():
        print("\nthe rule:")
        print("  " + rule_section(PRACTICE_FILE.read_text(encoding="utf-8")).replace("\n", "\n  "))
    return 1


if __name__ == "__main__":
    sys.exit(main())
