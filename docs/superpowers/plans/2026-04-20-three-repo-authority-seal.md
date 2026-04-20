# Three-Repo Authority Seal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Seal the three-repo control plane so `project-start` is the root start record, context rules are authoritative, and scoped execution rules no longer conflict.

**Architecture:** Add the missing root `project-start` issue template to `clever-change-control`, introduce a single authority-boundary document in `clever-context-monorepo`, then align intake/bootstrap docs, helper output, and tests in `clever-agent-project` to the same root/scoped identifier model. Keep the existing three-repo split intact and strengthen it with explicit authority and verification.

**Tech Stack:** GitHub issue forms, Markdown governance docs, Python helper script, pytest

---

### Task 1: Add Root Project-Start Template

**Files:**
- Create: `clever-change-control/.github/ISSUE_TEMPLATE/project-start.yml`
- Modify: `clever-change-control/README.md`
- Modify: `clever-change-control/.github/ISSUE_TEMPLATE/change-request.yml`

- [ ] **Step 1: Write the failing test or verification target**

Define the expected root intake shape:
- `project-start` exists as a dedicated root issue template
- root canonical identifier is the created `project-start` issue number
- `change id` remains scoped to post-approval change execution

- [ ] **Step 2: Add the root issue template**

Create a GitHub issue form for:
- request summary
- business intent
- constraints
- expected outcome
- candidate template lineage
- candidate target repo/service
- intake mode
- approval status

- [ ] **Step 3: Align README and scoped change template**

Update the README and change-request template so the root/scoped distinction is explicit and consistent.

- [ ] **Step 4: Verify content**

Run:

```bash
rg -n "project-start|change id|root canonical" /Users/jiin/Documents/Files/03_Work_EVnSolution/01_Repos/03_CLEVER_Agent/clever-change-control
```

Expected:
- `project-start.yml` is found
- README describes root issue first, scoped change second

### Task 2: Add Authority Boundary SSOT

**Files:**
- Create: `clever-context-monorepo/docs/root/authority-boundaries.md`
- Modify: `clever-context-monorepo/README.md`
- Modify: `clever-context-monorepo/docs/root/index.md`
- Modify: `clever-context-monorepo/docs/root/agent-runtime-governance.md`
- Modify: `clever-context-monorepo/docs/root/pipeline-governance.md`
- Modify: `clever-context-monorepo/docs/root/architecture-principles.md`
- Modify: `clever-context-monorepo/docs/root/domain-glossary.md`

- [ ] **Step 1: Write the failing verification target**

Define the required authority model:
- start surface: `clever-agent-project`
- interpretation SSOT: `clever-context-monorepo`
- approval/trace SSOT: `clever-change-control`
- root ID: `project-start issue #`
- scoped ID: `change id`

- [ ] **Step 2: Add the authority doc**

Write one root document that states:
- which repo owns which authority
- which fields are required at root intake
- which fields become mandatory only after approval and scope fixation

- [ ] **Step 3: Remove drift from nearby root docs**

Update runtime, pipeline, architecture, and glossary docs so they no longer imply:
- `change id` is the root start identifier
- `target service` is mandatory for general intake

- [ ] **Step 4: Verify content**

Run:

```bash
rg -n "project-start issue|change id|target service|authority" /Users/jiin/Documents/Files/03_Work_EVnSolution/01_Repos/03_CLEVER_Agent/clever-context-monorepo/docs/root /Users/jiin/Documents/Files/03_Work_EVnSolution/01_Repos/03_CLEVER_Agent/clever-context-monorepo/README.md
```

Expected:
- new authority doc is linked from root index
- root/scoped identifier language is consistent

### Task 3: Align Intake and Bootstrap Rules

**Files:**
- Modify: `clever-agent-project/README.md`
- Modify: `clever-agent-project/docs/setting.md`
- Modify: `clever-agent-project/docs/guides/clever-project-workflows.md`
- Modify: `clever-agent-project/.agent/skills/bootstrap-clever-work/SKILL.md`
- Modify: `clever-agent-project/.agent/skills/bootstrap-clever-work/scripts/bootstrap_clever_work.py`
- Modify: `clever-agent-project/tests/test_bootstrap_clever_work.py`

- [ ] **Step 1: Write the failing tests**

Add/adjust tests so they expect:
- helper packet keeps `project-start` as root identifier
- helper output explains `change id` is for scoped work after approval
- SSOT doc list includes the new authority-boundary doc

- [ ] **Step 2: Update intake docs and skill**

Make the start rules explicit:
- intake requires intent, constraints, expected result, candidate lineage, candidate repo/service if known
- intake does not require fixed `target_service` or `change_id`
- approval leads to `project-start`
- scoped change work later requires `change_id`

- [ ] **Step 3: Update helper output minimally**

Keep the existing packet shape, but strengthen the canonical linkage text and SSOT doc list to match the new authority model.

- [ ] **Step 4: Verify tests**

Run:

```bash
pytest /Users/jiin/Documents/Files/03_Work_EVnSolution/01_Repos/03_CLEVER_Agent/clever-agent-project/tests/test_bootstrap_clever_work.py -q
```

Expected:
- all bootstrap tests pass

### Task 4: Final Cross-Repo Verification

**Files:**
- Test: `clever-agent-project/tests/test_bootstrap_clever_work.py`

- [ ] **Step 1: Run targeted verification**

Run:

```bash
pytest /Users/jiin/Documents/Files/03_Work_EVnSolution/01_Repos/03_CLEVER_Agent/clever-agent-project/tests/test_bootstrap_clever_work.py -q
```

```bash
rg -n "project-start|change id|authority|target service" /Users/jiin/Documents/Files/03_Work_EVnSolution/01_Repos/03_CLEVER_Agent/clever-agent-project /Users/jiin/Documents/Files/03_Work_EVnSolution/01_Repos/03_CLEVER_Agent/clever-context-monorepo /Users/jiin/Documents/Files/03_Work_EVnSolution/01_Repos/03_CLEVER_Agent/clever-change-control
```

Expected:
- bootstrap tests are green
- no root doc still claims `change id` is the start identifier
- no general intake doc still requires a fixed `target service`

- [ ] **Step 2: Commit**

```bash
git -C /Users/jiin/Documents/Files/03_Work_EVnSolution/01_Repos/03_CLEVER_Agent/clever-change-control add .github/ISSUE_TEMPLATE/project-start.yml README.md .github/ISSUE_TEMPLATE/change-request.yml
git -C /Users/jiin/Documents/Files/03_Work_EVnSolution/01_Repos/03_CLEVER_Agent/clever-context-monorepo add README.md docs/root/index.md docs/root/authority-boundaries.md docs/root/agent-runtime-governance.md docs/root/pipeline-governance.md docs/root/architecture-principles.md docs/root/domain-glossary.md
git -C /Users/jiin/Documents/Files/03_Work_EVnSolution/01_Repos/03_CLEVER_Agent/clever-agent-project add README.md docs/setting.md docs/guides/clever-project-workflows.md .agent/skills/bootstrap-clever-work/SKILL.md .agent/skills/bootstrap-clever-work/scripts/bootstrap_clever_work.py tests/test_bootstrap_clever_work.py docs/superpowers/plans/2026-04-20-three-repo-authority-seal.md
```
