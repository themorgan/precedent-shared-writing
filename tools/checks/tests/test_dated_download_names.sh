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
# An engine too old to wire a practice's hooks: a note naming Update
# Vendors, never a refusal (2026-10-07, an unrelated merge in a consumer).
set +e
OUT="$(python3 "$CHECK")"; CODE=$?
set -e
if [[ $CODE -ne 0 ]] || ! grep -q "^NOTE: .*run Update Vendors" <<<"$OUT"; then
  echo "FAIL: an engine that cannot wire hooks should get a note, exit 0; got $CODE" >&2; echo "$OUT" >&2; exit 1
fi
echo "ok: a note, not a refusal, where the engine cannot wire the hook"
: > "$SCRATCH/tools/precedent_hooks.py"
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
hook '{"tool_name":"SendUserFile","tool_input":{"files":["out/joseph-manuscript.docx"]}}'; C1=$?
ERR1="$(cat "$SCRATCH/hook.err")"
hook '{"tool_name":"SendUserFile","tool_input":{"files":["out/Joseph - 2026-10-05.docx","a/b-2026-10-05.pdf"]}}'; C2=$?
hook '{"tool_name":"SendUserFile","tool_input":{"files":["shot.png","page.html"]}}'; C3=$?
set -e
if [[ $C1 -ne 2 || $C2 -ne 0 || $C3 -ne 0 ]]; then
  echo "FAIL: hook exits were undated=$C1 (want 2), dated=$C2 (want 0), non-documents=$C3 (want 0)" >&2
  exit 1
fi
if ! grep -q "dated-download-names: a document handed over" <<<"$ERR1" \
    || ! grep -q "joseph-manuscript.docx" <<<"$ERR1"; then
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

mkdir -p "$SCRATCH/book/output" "$SCRATCH/archive" "$SCRATCH/content/sources"
printf 'x' > "$SCRATCH/archive/Ledger.xlsx"
printf 'x' > "$SCRATCH/content/sources/a-book.pdf"
printf 'x' > "$SCRATCH/book/output/Notes.docx"
if ! python3 "$CHECK" >/dev/null; then
  echo "FAIL: flagged a kept document with no OUTBOX.md and no output_paths" >&2
  python3 "$CHECK" >&2 || true; exit 1
fi
echo "ok: with no outbox and no output_paths, no kept document is in scope"

cat > "$SCRATCH/OUTBOX.md" <<'MD'
# Outbox

| Document | File | Built by |
|---|---|---|
| Notes | [book/output/Notes.docx](book/output/Notes.docx) | hand |
MD
OUT="$(python3 "$CHECK" || true)"
if ! grep -q "book/output/Notes.docx is a document kept for download with no date" <<<"$OUT"; then
  echo "FAIL: did not flag an undated document the outbox lists" >&2; echo "$OUT" >&2; exit 1
fi
if grep -qE "archive/Ledger.xlsx|a-book.pdf" <<<"$OUT"; then
  echo "FAIL: flagged a document the outbox does not list" >&2; echo "$OUT" >&2; exit 1
fi
mv "$SCRATCH/book/output/Notes.docx" "$SCRATCH/book/output/Notes-2026-12-30.docx"
sed -i 's#Notes.docx](book/output/Notes.docx)#Notes-2026-12-30.docx](book/output/Notes-2026-12-30.docx)#' "$SCRATCH/OUTBOX.md"
if ! python3 "$CHECK" >/dev/null; then
  echo "FAIL: flagged a dated document the outbox lists" >&2; python3 "$CHECK" >&2 || true; exit 1
fi
echo "ok: the outbox decides: a listed document fires undated and is clean dated; an unlisted one is never read"

printf '| Gone | [book/output/Gone-2026-12-01.pdf](book/output/Gone-2026-12-01.pdf) | hand |\n' >> "$SCRATCH/OUTBOX.md"
OUT="$(python3 "$CHECK" || true)"
if ! grep -q "OUTBOX.md lists book/output/Gone-2026-12-01.pdf, which is not in the tree" <<<"$OUT"; then
  echo "FAIL: did not flag an outbox row whose file is missing" >&2; echo "$OUT" >&2; exit 1
fi
echo "ok: an outbox row whose file is gone is a finding"
rm -f "$SCRATCH/OUTBOX.md"

echo '{"output_paths": ["book/"], "internal_paths": ["book/drafts/"]}' > "$SCRATCH/precedent.json"
mkdir -p "$SCRATCH/book/drafts"
printf 'x' > "$SCRATCH/book/Undated.docx"
printf 'x' > "$SCRATCH/book/drafts/Scratch.docx"
OUT="$(python3 "$CHECK" || true)"
if ! grep -q "book/Undated.docx is a document kept for download" <<<"$OUT" \
    || grep -qE "archive/Ledger.xlsx|a-book.pdf|book/drafts/Scratch.docx" <<<"$OUT"; then
  echo "FAIL: the output_paths fallback (minus internal_paths) did not scope the check" >&2; echo "$OUT" >&2; exit 1
fi
echo "ok: with no outbox, output_paths minus internal_paths decides"
rm -f "$SCRATCH/book/Undated.docx" "$SCRATCH/precedent.json" "$SCRATCH/archive/Ledger.xlsx"
rm -rf "$SCRATCH/content" "$SCRATCH/book/drafts"

# The hook listed in process/practice_hooks.json and run by the fixed
# precedent-hooks.sh entry (the engine's route since 2026-10-07).
cat > "$SCRATCH/.claude/settings.json" <<'JSON'
{"hooks": {"PreToolUse": [{"hooks": [{"type": "command",
  "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/precedent-hooks.sh PreToolUse"}]}]}}
JSON
mkdir -p "$SCRATCH/process"
cat > "$SCRATCH/process/practice_hooks.json" <<'JSON'
{"hooks": [{"event": "PreToolUse", "matcher": "SendUserFile",
  "command": "python3 $CLAUDE_PROJECT_DIR/tools/dated_name.py --hook"}]}
JSON
if ! python3 "$CHECK" >/dev/null; then
  echo "FAIL: not clean with the hook on the practice-hooks list" >&2; python3 "$CHECK" >&2 || true; exit 1
fi
echo '{"hooks": []}' > "$SCRATCH/process/practice_hooks.json"
if python3 "$CHECK" >/dev/null; then
  echo "FAIL: clean with the hook neither in settings nor on the list" >&2; exit 1
fi
echo "ok: the hook counts when listed in process/practice_hooks.json, and only then"
rm -rf "$SCRATCH/process"

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
