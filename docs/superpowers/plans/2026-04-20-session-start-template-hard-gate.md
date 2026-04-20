# Session Start Template Hard Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a simple developer-leaning session-start template and hard gate so every new CLEVER intake starts from the same first-response structure.

**Architecture:** Keep the user-facing intake short in `README.md`, expand the operational explanation in `docs/setting.md`, and enforce the same structure in the bootstrap skill with a hard gate before any planning, implementation, or repo bootstrap. The agent interprets the answers into change-control taxonomy instead of asking users to fill formal internal fields.

**Tech Stack:** Markdown docs, bootstrap skill instructions

---

### Task 1: Add User-Facing Session Start Template

**Files:**
- Modify: `README.md`
- Modify: `docs/setting.md`

- [ ] **Step 1: Add the copy-paste opening template**

Include the three fixed questions:
- 새 서비스 개발 vs. 기존 서비스 추가
- 서비스 기반: MSA vs. MONO
- 타입 명확하게 분류하기

Also include short free-text support fields for:
- 하려는 일
- 왜 필요한지
- 제약
- 기대 결과
- 관련 repo/service if known

- [ ] **Step 2: Explain how the template is used**

Document that:
- users can paste the template directly
- freeform input is allowed
- the agent must normalize freeform input back into the same structure

### Task 2: Add Hard Gate to Bootstrap Skill

**Files:**
- Modify: `.agent/skills/bootstrap-clever-work/SKILL.md`

- [ ] **Step 1: Add first-response hard gate**

Before any planning or implementation, the agent must:
- present the session-start template, or
- reframe the user’s freeform request into that template

- [ ] **Step 2: Add interpretation rules**

Document that the agent interprets:
- `새 서비스 개발` vs. `기존 서비스 추가`
- `MSA` vs. `MONO`
- user description

into the internal `change-control` work type model.

- [ ] **Step 3: Define stop conditions**

The agent must not proceed to:
- project-start creation
- repo bootstrap
- implementation planning

until the first-step template and basic intent/constraint/outcome fields are sufficiently filled.

### Task 3: Verify Wording Consistency

**Files:**
- Test: `README.md`
- Test: `docs/setting.md`
- Test: `.agent/skills/bootstrap-clever-work/SKILL.md`

- [ ] **Step 1: Run text verification**

Run:

```bash
rg -n "새 서비스 개발|기존 서비스 추가|MSA vs\\. MONO|하드 게이트|project-start|freeform" /Users/jiin/Documents/Files/03_Work_EVnSolution/01_Repos/03_CLEVER_Agent/clever-agent-project/README.md /Users/jiin/Documents/Files/03_Work_EVnSolution/01_Repos/03_CLEVER_Agent/clever-agent-project/docs/setting.md /Users/jiin/Documents/Files/03_Work_EVnSolution/01_Repos/03_CLEVER_Agent/clever-agent-project/.agent/skills/bootstrap-clever-work/SKILL.md
```

Expected:
- the same first-response structure appears in all three places
- the hard gate is explicit in the skill

- [ ] **Step 2: Commit**

```bash
git -C /Users/jiin/Documents/Files/03_Work_EVnSolution/01_Repos/03_CLEVER_Agent/clever-agent-project add README.md docs/setting.md .agent/skills/bootstrap-clever-work/SKILL.md docs/superpowers/plans/2026-04-20-session-start-template-hard-gate.md
```
