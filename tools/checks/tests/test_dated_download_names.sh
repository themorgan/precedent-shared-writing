#!/bin/bash
# Multi-direction test for check_dated_download_names.py and the tool it
# guards, on its own scratch fixture (practice: fixture-owns-its-state):
#   1. no tools/dated_name.py -- require SKIPPED (exit 2);
#   2. the real tool with a settings.json that lacks the hook -- require a
#      violation naming SendUserFile;
#   3. the same with the hook wired -- require clean;
#   4. the hook itself: refuses an undated .docx, lets a dated one and an
#      image through;
#   5. the copy: --to writes the dated name and leaves the source alone;
#   6. a document the repository keeps: undated fires, dated is clean;
#   7. replace(): a rebuild goes to the new dated name and retires every
#      older copy, the undated one included, and nothing else.
set -euo pipefail
cd "$(dirname "$0")/../../.."
SET_ROOT="$(pwd)"
SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT
export PRECEDENT_CHECK_ROOT="$SCRATCH"
CHECK="$SET_ROOT/tools/checks/check_dated_download_names.py"
TOOL="$SET_ROOT/tools/dated_name.py"

set +e
OUT="$(python3 "$CHECK")"; CODE=$?
set -e
if [[ $CODE -ne 2 ]] || [[ "$OUT" != SKIPPED:* ]]; then
  echo "FAIL: expected SKIPPED when tools/dated_name.py isn't vendored, got $CODE: $OUT" >&2
  exit 1
fi
echo "ok: SKIPPED when tools/dated_name.py isn't vendored"

mkdir -p "$SCRATCH/tools" "$SCRATCH/.claude"
cp "$TOOL" "$SCRATCH/tools/dated_name.py"
echo '{"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": []}]}}' > "$SCRATCH/.claude/settings.json"
OUT="$(python3 "$CHECK" || true)"
if ! grep -q "no PreToolUse hook on SendUserFile" <<<"$OUT"; then
  echo "FAIL: did not flag the missing SendUserFile hook" >&2; echo "$OUT" >&2; exit 1
fi
echo "ok: fires when the hand-over hook is not wired"

cat > "$SCRATCH/.claude/settings.json" <<'JSON'
{"hooks": {"PreToolUse": [{"matcher": "SendUserFile", "hooks": [{"type": "command",
  "command": "python3 $CLAUDE_PROJECT_DIR/tools/dated_name.py --hook"}]}]}}
JSON
if ! python3 "$CHECK" >/dev/null; then
  echo "FAIL: not clean with the hook wired" >&2; python3 "$CHECK" >&2 || true; exit 1
fi
echo "ok: clean with the hook wired"

hook() { printf '%s' "$1" | python3 "$TOOL" --hook 2>"$SCRATCH/hook.err"; }
set +e
hook '{"tool_name":"SendUserFile","tool_input":{"files":["out/holy-hardball-joseph-manuscript.docx"]}}'; C1=$?
ERR1="$(cat "$SCRATCH/hook.err")"
hook '{"tool_name":"SendUserFile","tool_input":{"files":["out/Joseph - 2026-10-05.docx","a/b-2026-10-05.pdf"]}}'; C2=$?
hook '{"tool_name":"SendUserFile","tool_input":{"files":["shot.png","page.html"]}}'; C3=$?
set -e
if [[ $C1 -ne 2 || $C2 -ne 0 || $C3 -ne 0 ]]; then
  echo "FAIL: hook exits were undated=$C1 (want 2), dated=$C2 (want 0), non-documents=$C3 (want 0)" >&2
  exit 1
fi
if ! grep -q "dated-download-names: a document handed over" <<<"$ERR1" \
    || ! grep -q "holy-hardball-joseph-manuscript.docx" <<<"$ERR1"; then
  echo "FAIL: the refusal did not come from the dated-name gate, naming the file: $ERR1" >&2
  exit 1
fi
echo "ok: the hook refuses an undated document and passes dated ones and images"

mkdir -p "$SCRATCH/src"
printf 'x' > "$SCRATCH/src/notes.docx"
OUT="$(python3 "$TOOL" "$SCRATCH/src/notes.docx" --to "$SCRATCH/send" --date 2026-12-31)"
OUT2="$(python3 "$TOOL" "$SCRATCH/src/notes.docx" --to "$SCRATCH/send" --date 2026-12-31 --spaced)"
if [[ ! -f "$SCRATCH/send/notes-2026-12-31.docx" || ! -f "$SCRATCH/send/notes - 2026-12-31.docx" \
      || ! -f "$SCRATCH/src/notes.docx" ]]; then
  echo "FAIL: --to did not write both dated copies, or moved the source: $OUT / $OUT2" >&2; exit 1
fi
echo "ok: --to copies under the dated name, both forms, source untouched"
rm -rf "$SCRATCH/src" "$SCRATCH/send" "$SCRATCH/hook.err"

mkdir -p "$SCRATCH/book/output"
printf 'x' > "$SCRATCH/book/output/Notes.docx"
OUT="$(python3 "$CHECK" || true)"
if ! grep -q "book/output/Notes.docx is a document kept for download with no date" <<<"$OUT"; then
  echo "FAIL: did not flag an undated kept document" >&2; echo "$OUT" >&2; exit 1
fi
mv "$SCRATCH/book/output/Notes.docx" "$SCRATCH/book/output/Notes-2026-12-30.docx"
if ! python3 "$CHECK" >/dev/null; then
  echo "FAIL: flagged a dated kept document" >&2; python3 "$CHECK" >&2 || true; exit 1
fi
echo "ok: a kept document fires undated and is clean dated"

printf 'x' > "$SCRATCH/book/output/Notes.docx"
printf 'x' > "$SCRATCH/book/output/Notes Extra-2026-12-29.docx"
GOT="$(cd "$SET_ROOT/tools" && python3 -c "
import sys, pathlib; import dated_name as d
new, old = d.replace(pathlib.Path(sys.argv[1]) / 'Notes.docx', '2026-12-31')
print(new.name, '|', ', '.join(sorted(o.name for o in old)))
" "$SCRATCH/book/output")"
WANT="Notes-2026-12-31.docx | Notes-2026-12-30.docx, Notes.docx"
if [[ "$GOT" != "$WANT" ]]; then
  echo "FAIL: replace() gave '$GOT', want '$WANT'" >&2; exit 1
fi
echo "ok: replace() retires the older copies of that document and no other"
