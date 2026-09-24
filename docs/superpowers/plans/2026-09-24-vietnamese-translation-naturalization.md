# Vietnamese Translation Naturalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite all 173 Vietnamese AsciiDoc pages so the prose reads like natural technical Vietnamese written by a Vietnamese developer, while preserving technical meaning and AsciiDoc/code structure.

**Architecture:** Work directly in `content/modules/ROOT/pages/*.adoc`. Partition the sorted page list into six non-overlapping waves of at most 30 files; each worker edits exactly one assigned file. Run a second one-file-per-agent audit over the same partition, then perform repository-wide structural, terminology, and build validation.

**Tech Stack:** AsciiDoc, Antora, Git, Python 3 validation scripts, OpenCode parallel subagents.

---

## File Map

- Modify: `content/modules/ROOT/pages/*.adoc` — the 173 translated book pages, and the only book files workers may edit.
- Read-only context: `translation/GLOSSARY.md` and `translation/instructions/*.md` — translation, PostgreSQL terminology, semantic, and structure rules.
- Read-only validation: `scripts/test_migration.py`, `scripts/validate_migration.py`, `scripts/build-antora.sh`.
- Do not modify: `content/modules/ROOT/nav.adoc`, `source/`, `translation/`, `build/`, or generated site output.

## Worker Contract

Use this exact contract in every worker task and replace the path in the first line with the worker's one assigned file:

```text
You own exactly this file: [insert the absolute path assigned to this worker]

Read the full assigned file before editing. Also read:
- translation/GLOSSARY.md
- translation/instructions/00-core-rules.md
- translation/instructions/01-translation-style.md
- translation/instructions/02-postgresql-glossary.md
- translation/instructions/05-markdown-preservation.md
- translation/instructions/06-sql-code-output-fidelity.md
- translation/instructions/07-table-diagram-query-plan.md
- translation/instructions/08-semantic-review.md
- translation/instructions/09-qa-validation.md

Rewrite only prose in the assigned file. Make Vietnamese natural for a Vietnamese developer:
- translate by meaning, not English word order;
- keep English technical/domain terms when that is idiomatic and clarifies context, including
  system, backend, frontend, module, request, response, order, approval, inventory,
  procurement, finance, fulfillment, downstream, async, message, task, transaction, query,
  index, cache, lock, thread, API, and PostgreSQL terms;
- translate ordinary words when Vietnamese is clearer;
- decide by context and keep recurring terms consistent with nearby pages.

Do not add, remove, modernize, or reinterpret information. Do not translate or alter code,
SQL, commands, identifiers, API names, file paths, URLs, anchors, image targets, or literal
values. Preserve AsciiDoc headings, attributes, tables, listing blocks, links, and images.
Use apply_patch and edit no file other than the assigned file. Do not commit.

Before finishing, reread the entire file and check for:
1. word-by-word or machine-like phrasing;
2. excessive or forced English mixing;
3. meaning, negation, condition, qualifier, or recommendation-strength changes;
4. changed code/SQL/command/identifier or AsciiDoc delimiters.
Report whether the file changed and summarize only the checks performed.
```

## Task 1: Establish Baseline and Partition

**Files:** None.

- [ ] **Step 1: Confirm a clean starting worktree.**

Run:

```bash
git status --short
git diff --check
```

Expected: no output from either command. Stop and inspect if unrelated changes appear before editing.

- [ ] **Step 2: Create the deterministic page manifest outside the repository.**

Run:

```bash
rg --files content/modules/ROOT/pages -g '*.adoc' | sort > /tmp/learn-postgresql-adoc-pages.txt
test "$(wc -l < /tmp/learn-postgresql-adoc-pages.txt)" -eq 173
```

Expected: the count check succeeds. The manifest is lexical and is the sole assignment order for every wave.

- [ ] **Step 3: Record the pre-review commit for protected-content comparisons.**

Run:

```bash
git rev-parse HEAD > /tmp/learn-postgresql-review-base.txt
test -s /tmp/learn-postgresql-review-base.txt
```

Expected: the file contains the commit checked out immediately before the first content edit.

- [ ] **Step 4: Run baseline validation before content edits.**

Run:

```bash
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/validate_migration.py
```

Expected: unit tests pass and migration validation prints `Migration validation passed`. Record any pre-existing failure rather than attributing it to translation edits.

## Task 2: Naturalize Pages in Six Parallel Waves

**Files:** The wave's assigned subset of `content/modules/ROOT/pages/*.adoc`.

For wave number `wave` from `1` through `6`, assign the file at zero-based manifest index `(wave - 1) * 30 + i` to worker `i` for `i` from `0` through `29`, stopping when the manifest ends. This gives five waves of 30 files and a final wave of 23 files. Never dispatch two workers for the same path in one wave.

- [ ] **Step 1: Dispatch one fresh general-purpose subagent per assigned file.**

For each path, use the Worker Contract above and explicitly include the absolute assigned path. Workers may read neighboring pages for terminology context but may write only their assigned path. Dispatch all paths in the current wave concurrently, up to 30 subagents.

- [ ] **Step 2: Wait for every worker in the wave and inspect its result.**

Require each worker to report the assigned path, changed/unchanged status, and any uncertainty. If a worker reports uncertainty about meaning or source extraction, inspect that file manually before continuing; do not ask another worker to edit the same file during the wave.

- [ ] **Step 3: Verify the wave touched only assigned content pages.**

Run:

```bash
git status --short
git diff --check
git diff --name-only
```

Expected: every changed path is under `content/modules/ROOT/pages/` and belongs to the current wave; no `nav.adoc`, `translation/`, `source/`, or generated file is changed.

- [ ] **Step 4: Review and commit the completed wave.**

Read the diff for the current wave, paying special attention to code blocks, tables, headings, and sentences with changed qualifiers. Then commit only the reviewed page files:

```bash
wave=1
start=$(( (wave - 1) * 30 + 1 ))
end=$(( wave * 30 ))
mapfile -t wave_files < <(sed -n "${start},${end}p" /tmp/learn-postgresql-adoc-pages.txt)
git add -- "${wave_files[@]}"
git diff --cached --check
git commit -m "docs: naturalize Vietnamese translation wave ${wave}"
```

Set `wave` to each one-based wave number before repeating the command. This stages only paths assigned by the deterministic manifest, not files from another wave. Repeat Task 2 for all six waves.

## Task 3: Run a Second One-File-Per-Agent Language Audit

**Files:** The same 173 files under `content/modules/ROOT/pages/`.

- [ ] **Step 1: Reuse the manifest and dispatch a second six-wave review.**

Use the same 30-worker partition and Worker Contract, but tell workers this is a final audit. They must compare the current prose with the style target, inspect nearby chapter pages for terminology consistency, and edit their one assigned file only when a concrete issue remains. They must not undo a natural rewrite merely to preserve the original sentence order.

- [ ] **Step 2: Focus the audit on residual machine-translation signals.**

Require workers to inspect:

- English sentence order copied into Vietnamese;
- unnatural passive constructions and repeated filler phrases;
- `the/of/for`-style English fragments left in prose;
- forced translations of technical terms that Vietnamese developers normally keep in English;
- inconsistent choices for recurring terms such as `system`, `backend`, `request`, `response`, `query`, `transaction`, `lock`, `replication`, `backup`, and `restore`;
- awkward headings, captions, callouts, table cells, and list items.

- [ ] **Step 3: Validate and commit each audit wave.**

After each wave, run `git status --short`, `git diff --check`, and `git diff --name-only`; inspect the diff; then commit only that wave's page files with:

```bash
wave=1
start=$(( (wave - 1) * 30 + 1 ))
end=$(( wave * 30 ))
mapfile -t audit_files < <(sed -n "${start},${end}p" /tmp/learn-postgresql-adoc-pages.txt)
git add -- "${audit_files[@]}"
git diff --cached --check
git commit -m "docs: polish Vietnamese translation audit wave ${wave}"
```

Set `wave` to each one-based wave number before repeating the command.

## Task 4: Repository-Wide Consistency and Protected-Content Checks

**Files:** No new files. Modify a page only when a confirmed issue is found.

- [ ] **Step 1: Confirm target inventory and non-empty pages.**

Run:

```bash
test "$(rg --files content/modules/ROOT/pages -g '*.adoc' | wc -l)" -eq 173
while IFS= read -r page; do test -s "$page" || exit 1; done < /tmp/learn-postgresql-adoc-pages.txt
```

Expected: both commands succeed.

- [ ] **Step 2: Search for structural or prohibited translation artifacts.**

Run:

```bash
rg -n '```|~~~|<<<<<<<|=======|>>>>>>>|TODO|TBD' content/modules/ROOT/pages -g '*.adoc'
```

Expected: no Markdown fences, conflict markers, or unfinished placeholders. A legitimate prose occurrence must be inspected and cleared or documented.

- [ ] **Step 3: Compare protected source blocks against the pre-review commit.**

Run this complete check from the repository root:

```bash
python3 - <<'PY'
import re
import subprocess
from pathlib import Path

root = Path('content/modules/ROOT/pages')
pattern = re.compile(r'(?ms)^\[source[^\n]*\]\n^\.\.\.\.\n.*?^\.\.\.\.\n')

def protected(text):
    return pattern.findall(text)

errors = []
for path in sorted(root.glob('*.adoc')):
    base = Path('/tmp/learn-postgresql-review-base.txt').read_text(encoding='utf-8').strip()
    old = subprocess.check_output(['git', 'show', f'{base}:{path.as_posix()}'], text=True)
    new = path.read_text(encoding='utf-8')
    if protected(old) != protected(new):
        errors.append(path.as_posix())
if errors:
    raise SystemExit('protected source blocks changed:\n' + '\n'.join(errors))
print('Protected source blocks unchanged')
PY
```

If the check reports a difference, inspect the exact block and restore only an accidental translation change; never alter a code block to make prose validation pass.

- [ ] **Step 4: Run targeted terminology searches and manually resolve confirmed inconsistencies.**

Use:

```bash
rg -n -i '\b(system|backend|frontend|module|request|response|order|approval|inventory|procurement|finance|fulfillment|downstream|async|message|task|transaction|query|index|cache|lock|thread|api)\b' content/modules/ROOT/pages -g '*.adoc'
```

Review the surrounding sentences rather than replacing matches mechanically. Keep each term in English where it is the natural technical choice and translate ordinary surrounding grammar into Vietnamese.

- [ ] **Step 5: Reread changed prose samples from every chapter.**

Use the recorded base commit and changed-file list to sample every chapter, including headings, summaries, requirements, reference sections, tables, warnings, and pages with code-heavy content:

```bash
base=$(cat /tmp/learn-postgresql-review-base.txt)
git diff --stat "${base}..HEAD"
while IFS= read -r page; do
  git diff -- "${page}"
done < <(git diff --name-only "${base}..HEAD" -- content/modules/ROOT/pages)
```

Fix any remaining stiff or word-by-word sentence directly with `apply_patch`.

## Task 5: Run Full Validation and Antora Build

**Files:** Validation may update ignored `build/site/`; do not edit generated source files.

- [ ] **Step 1: Run migration unit tests.**

```bash
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

Expected: all tests pass.

- [ ] **Step 2: Run migration and AsciiDoc structural validation.**

```bash
python3 scripts/validate_migration.py
```

Expected: `Migration validation passed`, with balanced listing/table/quote blocks and no Markdown fences.

- [ ] **Step 3: Build the Antora site.**

```bash
scripts/build-antora.sh
test -f build/site/learn-postgresql/main/front-matter.html
test -f build/site/learn-postgresql/main/index.html
```

Expected: the build completes and both HTML files exist. If neither `antora` nor `npx` is available, report the environment limitation and retain the successful non-Node validation results.

- [ ] **Step 4: Perform final worktree and diff checks.**

```bash
base=$(cat /tmp/learn-postgresql-review-base.txt)
git diff --check
git status --short
git diff --stat "${base}..HEAD"
```

Expected: only the approved design/plan artifacts and the 173 target page files are present in the review history; no `nav.adoc`, source, translation instruction, or untracked generated artifact is included.

- [ ] **Step 5: Commit any final confirmed fixes.**

```bash
mapfile -t final_files < <(git diff --name-only -- content/modules/ROOT/pages)
git add -- "${final_files[@]}"
git diff --cached --check
git commit -m "docs: finalize Vietnamese translation review"
```

Do not make a final success claim until the tests, structural validation, protected-content check, and available site build have produced the expected results.
