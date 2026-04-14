# Change Control Work Type Taxonomy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a two-level work type taxonomy to `clever-change-control` issues and align `clever-agent-project` templates and sync logic so agents generate `[상위 타입][하위 타입] 짧은 제목` plus matching body fields.

**Architecture:** Keep the taxonomy definition in documentation and issue template guidance, not in GitHub issue form logic. Treat `clever-change-control` as the issue-creation contract and `clever-agent-project` as the draft/sync toolchain that must emit the same structure, with temporary backward compatibility for legacy `work_type` input.

**Tech Stack:** Markdown docs, GitHub issue form YAML, Python 3, pytest, git

---

### Task 1: Update `clever-change-control` to document and collect the taxonomy

**Files:**
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control/README.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control/.github/ISSUE_TEMPLATE/change-request.yml`

- [ ] **Step 1: Add taxonomy and title/body rules to the README**

Document these exact rules in `README.md`:
- upper groups: `MSA/SaaS`, `일반 개발`
- lower types for `MSA/SaaS`: `복제`, `수정`, `변경`, `신규`
- lower types for `일반 개발`: `신규 개발`, `수정`, `변경`, `리팩토링`
- issue title format: `[상위 타입][하위 타입] 짧은 제목`
- body must carry both `work_type_group` and `work_type_detail`
- agent must keep title and body type values identical

- [ ] **Step 2: Extend the change request issue template**

Add new fields to `change-request.yml`:
- `work_type_group`
- `work_type_detail`

The field descriptions must explicitly say:
- agents should write titles as `[상위 타입][하위 타입] 짧은 제목`
- body type values must match the title
- the form is guidance for agents, not the only source of truth

- [ ] **Step 3: Verify patch formatting in `clever-change-control`**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control diff --check -- README.md .github/ISSUE_TEMPLATE/change-request.yml
```

Expected: no output

- [ ] **Step 4: Commit the `clever-change-control` doc changes**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control add README.md .github/ISSUE_TEMPLATE/change-request.yml
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control commit -m "docs: add change request work type taxonomy"
```

Expected: one commit that changes only the README and issue template

### Task 2: Update `clever-agent-project` docs and markdown draft template

**Files:**
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/README.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/templates/issue-edit-template.md`

- [ ] **Step 1: Update the README issue-editing section**

Replace the current single `work_type` guidance with:
- `work_type_group`
- `work_type_detail`
- the same upper/lower taxonomy from the spec
- the new title format `[상위 타입][하위 타입] 짧은 제목`
- the rule that body fields and title must match

- [ ] **Step 2: Update the markdown issue draft template**

Change the front matter from:

```yaml
work_type: 신규 개발
```

to the new default structure:

```yaml
work_type_group: 일반 개발
work_type_detail: 신규 개발
```

Keep `repo`, `issue_number`, and `title`.

Add a visible body section near the top of the markdown body that mirrors the type fields, for example:

```markdown
## Work Type
- Group: 일반 개발
- Detail: 신규 개발
```

- [ ] **Step 3: Verify patch formatting in `clever-agent-project` docs**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project diff --check -- README.md docs/templates/issue-edit-template.md
```

Expected: no output

- [ ] **Step 4: Commit the `clever-agent-project` doc/template changes**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project add README.md docs/templates/issue-edit-template.md
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project commit -m "docs: align issue draft taxonomy fields"
```

Expected: one commit for docs/template changes only

### Task 3: Convert the sync script to the new taxonomy with backward compatibility

**Files:**
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/scripts/sync_issue_from_md.py`
- Test: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/tests/test_sync_issue_from_md.py`

- [ ] **Step 1: Write failing tests for the new format**

Add tests that assert:
- parsing succeeds when front matter contains `work_type_group` and `work_type_detail`
- the formatted title becomes `[일반 개발][수정] 제목` or `[MSA/SaaS][복제] 제목`
- a mismatch or missing required new fields raises a clear error unless legacy `work_type` is present
- legacy `work_type: 신규 개발` still works via compatibility mapping

Use concrete test snippets in `tests/test_sync_issue_from_md.py`, for example:

```python
assert draft.work_type_group == "MSA/SaaS"
assert draft.work_type_detail == "복제"
assert draft.formatted_title == "[MSA/SaaS][복제] 배차 서비스 고객사 배포 분기 추가"
```

- [ ] **Step 2: Run the targeted test file and confirm failure**

Run:

```bash
pytest /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/tests/test_sync_issue_from_md.py -q
```

Expected: failures because the script still expects `work_type`

- [ ] **Step 3: Refactor the script data model**

Change the script to:
- require `repo`, `issue_number`, `title`, plus either:
  - `work_type_group` and `work_type_detail`, or
  - legacy `work_type`
- add compatibility conversion from legacy `work_type` values to new upper/lower values
- store both values on `IssueDraft`
- format titles as `[상위 타입][하위 타입] {normalized_title}`

Use an explicit mapping table such as:

```python
LEGACY_WORK_TYPE_MAP = {
    "신규 개발": ("일반 개발", "신규 개발"),
    "신규": ("일반 개발", "신규 개발"),
    "수정": ("일반 개발", "수정"),
    "변경": ("일반 개발", "변경"),
    "리팩토링": ("일반 개발", "리팩토링"),
}
```

Also add a validation table for allowed detail values under each group:

```python
WORK_TYPE_GROUPS = {
    "MSA/SaaS": {"복제", "수정", "변경", "신규"},
    "일반 개발": {"신규 개발", "수정", "변경", "리팩토링"},
}
```

- [ ] **Step 4: Update the CLI output expectations**

Ensure `--dry-run` still prints JSON but the `title` field now contains the new bracketed format.

Concrete expected example:

```json
{
  "repo": "EVNSolution/clever-change-control",
  "issue_number": "3",
  "title": "[MSA/SaaS][복제] 배차 서비스 고객사 배포 분기 추가",
  "dry_run": true,
  "updated": false
}
```

- [ ] **Step 5: Run the targeted test file and confirm pass**

Run:

```bash
pytest /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/tests/test_sync_issue_from_md.py -q
```

Expected: all tests pass

- [ ] **Step 6: Run the script in dry-run mode against the template**

Run:

```bash
python3 /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/scripts/sync_issue_from_md.py \
  /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/templates/issue-edit-template.md \
  --dry-run
```

Expected: JSON output with a bracketed title using the new taxonomy

- [ ] **Step 7: Commit the script and tests**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project add scripts/sync_issue_from_md.py tests/test_sync_issue_from_md.py
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project commit -m "feat: add change control work type taxonomy sync"
```

Expected: one commit for the parser/title-format behavior

### Task 4: Final verification and cleanup

**Files:**
- Review both repositories above

- [ ] **Step 1: Verify repository state**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project status --short
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control status --short
```

Expected:
- `clever-agent-project`: clean
- `clever-change-control`: only pre-existing local artifacts such as `.DS_Store` may remain untracked

- [ ] **Step 2: Capture final commit hashes**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project rev-parse --short HEAD
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control rev-parse --short HEAD
```

Expected: one short hash per repo for the final report
