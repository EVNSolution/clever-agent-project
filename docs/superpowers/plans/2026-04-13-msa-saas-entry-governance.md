# MSA SaaS Entry Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add start-time branching so CLEVER work distinguishes `MSA/SaaS 복제형` from `일반 개발`, then sends MSA work to the right `clever-context-monorepo` root and service docs.

**Architecture:** Keep `clever-agent-project` as the intake surface with short branching rules only. Put the authoritative MSA SaaS governance in `clever-context-monorepo/docs/root`, then link it from existing root and wiki entry points. Extend the service template so future service docs can record SaaS replication-specific guidance without duplicating global rules.

**Tech Stack:** Markdown documentation, repo-local skill docs, git

---

### Task 1: Save the plan and allow plan/spec tracking

**Files:**
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/.gitignore`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/superpowers/plans/2026-04-13-msa-saas-entry-governance.md`
- Reference: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/superpowers/specs/2026-04-13-msa-saas-entry-governance-design.md`

- [x] **Step 1: Allow `docs/superpowers/plans/*.md` and `docs/superpowers/specs/*.md` in `.gitignore`**

Edit the whitelist rules so design and plan docs are trackable in this repo.

- [x] **Step 2: Write this implementation plan**

Save this plan under `docs/superpowers/plans/`.

- [ ] **Step 3: Verify the new tracked docs are visible to git**

Run: `git status --short`
Expected: `.gitignore` and the plan/spec docs are shown as tracked or modified files, not ignored.

- [ ] **Step 4: Commit the planning docs**

Run:

```bash
git add .gitignore docs/superpowers/specs/2026-04-13-msa-saas-entry-governance-design.md docs/superpowers/plans/2026-04-13-msa-saas-entry-governance.md
git commit -m "docs: capture msa saas entry governance plan"
```

Expected: one commit containing the planning assets only.

### Task 2: Update the intake repo to branch by work type

**Files:**
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/README.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/.agent/skills/bootstrap-clever-work/SKILL.md`

- [ ] **Step 1: Add a short work-type branching section to `README.md`**

Document that work begins in `clever-agent-project`, then branches into:
- `MSA/SaaS 복제형`: determine target service by conversation, then read `clever-context-monorepo` root/service docs
- `일반 개발`: continue with the existing `project-start -> target repo` flow

- [ ] **Step 2: Update `bootstrap-clever-work` with the same branching rule**

Make the repo-local skill explicit about:
- classifying the work first
- not requiring `target-service` for general work
- requiring `target-service` discussion only when the task is MSA/SaaS replication-oriented
- reading `clever-context-monorepo` root/service docs before handoff in that branch

- [ ] **Step 3: Verify documentation formatting**

Run:

```bash
git diff --check -- README.md .agent/skills/bootstrap-clever-work/SKILL.md
```

Expected: no whitespace or patch format errors.

- [ ] **Step 4: Commit the intake repo changes**

Run:

```bash
git add README.md .agent/skills/bootstrap-clever-work/SKILL.md
git commit -m "docs: add msa saas intake branching"
```

Expected: one commit in `clever-agent-project` for the intake rules.

### Task 3: Add the authoritative MSA SaaS governance to the context repo

**Files:**
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/root/msa-saas-replication-governance.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/root/index.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/root/clever-msa-platform-workspace.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/wiki/index.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/wiki/services.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/services/service-template.md`

- [ ] **Step 1: Create the new root governance doc**

Document:
- what qualifies as `MSA/SaaS 복제형`
- how to distinguish `복제`, `수정`, `변경`, `신규`
- when to decide target service before implementation
- how tenant/customer-specific deployment should be represented
- how this branch differs from ordinary work

- [ ] **Step 2: Link the new governance doc from root entry points**

Update `docs/root/index.md` and `docs/root/clever-msa-platform-workspace.md` so MSA/SaaS branching is discoverable from existing official entry points.

- [ ] **Step 3: Link it from wiki entry points without making wiki the source of truth**

Update `docs/wiki/index.md` and `docs/wiki/services.md` to point readers back to the new root doc and service docs.

- [ ] **Step 4: Extend the service template with SaaS replication guidance**

Add a short section to `docs/services/service-template.md` so future service docs can record customer-specific variation points while still referencing the root governance doc for global rules.

- [ ] **Step 5: Verify the context repo docs**

Run:

```bash
git diff --check -- docs/root docs/wiki docs/services/service-template.md
```

Expected: no patch format problems.

- [ ] **Step 6: Commit the context repo changes**

Run:

```bash
git add docs/root/msa-saas-replication-governance.md docs/root/index.md docs/root/clever-msa-platform-workspace.md docs/wiki/index.md docs/wiki/services.md docs/services/service-template.md
git commit -m "docs: add msa saas replication governance"
```

Expected: one commit in `clever-context-monorepo` for the new authoritative docs.

### Task 4: Final verification and report

**Files:**
- Review: both git repos above

- [ ] **Step 1: Confirm each repo is clean except for intentional changes**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project status --short
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo status --short
```

Expected: no unexpected modifications remain.

- [ ] **Step 2: Capture commit hashes for the report**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project rev-parse --short HEAD
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo rev-parse --short HEAD
```

Expected: one short hash per repo.
