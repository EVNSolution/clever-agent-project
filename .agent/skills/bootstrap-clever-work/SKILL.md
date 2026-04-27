---
name: bootstrap-clever-work
description: Use when starting work from any CLEVER repo and the intake must be standardized against clever-context-monorepo and clever-change-control before planning or implementation begins
---

# Bootstrap CLEVER Work

## Overview

Use this skill as the single entry point for new CLEVER work.

It forces the same start sequence for every user and every repo:

1. Run the preflight gate.
2. Read the two SSOT repos first.
3. Collect the startup branch.
4. If it is MSA-oriented and service-specific, determine the target service by conversation and read the relevant root/service docs.
5. Infer the work context from the current repo.
6. Convert the request into a `project-start` draft packet.
7. Ask for one final approval.
8. Only then create the root issue, propose repo bootstrap, seed the target repo, clone the repo, and hand off.

**Core principle:** do not start CLEVER work from a freeform prompt when the SSOT repos are available.

The canonical identifier is the created `project-start` issue number in `clever-change-control`. Before issue creation, the workflow uses a `project-start` draft only.

When a new target repo is created or bootstrapped, keep execution rules and planning content separate:

- `AGENTS.md`: agent execution procedure, working order, issue/branch rules, verification, context update checks, and completion conditions
- `docs/project-brief.md`: project planning draft, purpose, constraints, scope, open questions, and next work list

Do not put the project planning draft into `AGENTS.md`.

## First-Response Hard Gate

Before showing the first-response template, automatically inspect the local workspace,
`gh auth status`, GitHub account, remotes, repo visibility, and issue/PR/ruleset read access:

```bash
python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --json
```

If the session is explicitly about editing the current control-plane repo itself, run:

```bash
python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --current-repo-maintenance --json
```

Interpret the result like this:

- `preflight_check.ready=false`: stop and show the failed checks before asking startup questions.
- `preflight_check.ready=true`: continue by reading `workspace_check.agent_action`.
- `workspace_check.agent_action=proceed-with-hard-gate`: continue in the current session
- `workspace_check.agent_action=current-repo-maintenance`: stay in the current control-plane repo and treat it as the target
- `workspace_check.agent_action=switch-to-clever-agent-project`: move startup to `clever-agent-project` first
- `workspace_check.agent_action=stop-and-fix-workspace`: stop and clearly state that the local three-repository workspace is incomplete

The expected GitHub login defaults to `OziinG`.
Use `CLEVER_EXPECTED_GITHUB_LOGIN` or `--expected-github-login` only when the user explicitly authorizes another account.
Preflight also checks active `EVNSolution` org membership. Repository creation
permission cannot be proven without the actual `gh repo create` write attempt,
so treat that command's success as the creation proof after preflight passes.

Before planning, implementation, `project-start` creation, or repo bootstrap, the agent must first normalize the session into the same opening structure.

Use this exact first-response template:

```text
[시작 분기]
1. 작업 종류:
- 새 작업 시작
- 기존 서비스 변경
- 현재 저장소 자체 수정

2. 구조:
- MONO
- MSA

3. 이번 세션 목표:
- 요구사항/문서 정의
- 서비스 온보딩 정의
- 구현 repo 작업
- 배포 준비

추가 설명
- 하려는 일:
- 왜 필요한지:
- 제약:
- 기대 결과:
- 알고 있는 repo/service가 있으면:
```

Rules:

- If the user pasted the template, keep the structure and fill only missing fields.
- If the user started in freeform, restate the request into this template and ask only for the missing parts.
- Do not skip straight to planning, implementation, `project-start` drafting, or repo bootstrap before this structure is sufficiently filled.
- `change-control` taxonomy is internal. The user does not need to choose `work_type_group` or `work_type_detail` directly.
- Fill the normalized branch state from `docs/templates/startup-branch-state-template.md` before continuing.

## SSOT Order

Interpret sources in this order:

1. `clever-context-monorepo`
2. `clever-change-control`
3. the current working repo

The current repo is the execution surface, not the source of truth for workflow rules.

Start-vs-scope authority is defined in `clever-context-monorepo/docs/root/authority-boundaries.md`.

## When to Use

Use this skill when:

- work starts from any CLEVER repo and the intake needs to be standardized
- the user gives a goal but not all of `target repo` or implementation details
- different people or agents need to start work in the same format
- you need to prepare the root `project-start` record before planning

Do not use this skill when:

- the work is not inside the CLEVER workspace
- a `project-start` draft or issue has already been approved for the current task

## Required Inputs

The user only needs to provide the business intent and any known constraints.

You should infer or propose the rest:

- `user-session` or `request-context`
- `current-working-repo`
- `candidate-target-repo`
- `candidate-target-service`
- `purpose`
- `constraints`
- `ui-impact`
- `expected-result`
- `template-id`
- `template-version`
- `deploy-profile`
- `override-scope`
- `lifecycle-action`

The workflow must not require a fixed `target-service` for general work or a generated `change-id` at start time.

To clear the hard gate, the intake must have enough information for:

- `1. 작업 종류`
- `2. 구조`
- `3. 이번 세션 목표`
- `왜 필요한지`
- `제약`
- `기대 결과`

## Work-Type Branching

Before running the helper script, classify the task into one of these paths.

The user-facing questions stay simple, but the agent must interpret them against the internal `change-control` model.

### Interpretation Rules

Interpret the first three answers in this order:

1. `작업 종류`
2. `구조`
3. `이번 세션 목표`

Map them like this:

- `새 작업 시작` + `MSA`: default to MSA-oriented onboarding or requirements work
- `새 작업 시작` + `MONO`: default to general development onboarding or requirements work
- `기존 서비스 변경` + `MSA`: default to existing MSA workload change
- `기존 서비스 변경` + `MONO`: default to existing MONO workload change
- `현재 저장소 자체 수정`: treat the current control-plane repo as the target and do not route into generic startup

Then derive:

- `MONO` -> `workload_shape=single_workload`
- `MSA` -> `workload_shape=multiple_workloads`
- `요구사항/문서 정의` -> requirements-first session
- `서비스 온보딩 정의` -> service onboarding session
- `구현 repo 작업` -> target repo implementation session
- `배포 준비` -> deploy preparation session

If the explanation is still too vague after the first template pass, ask a short follow-up question before continuing.

After this interpretation, classify the task into one of these paths:

- `MSA/SaaS 복제형 작업`
- `일반 개발 작업`

Treat MSA-oriented new or existing service work as the MSA path.

Treat MONO-oriented service work as the general development path.

Treat `현재 저장소 자체 수정` as control-plane maintenance and do not force a target service.

### MSA/SaaS Replication Path

If the task is MSA-oriented:

1. Determine the target service or service family by conversation first.
2. Read `clever-context-monorepo/docs/root/msa-saas-replication-governance.md`.
3. Read `clever-context-monorepo/docs/root/clever-msa-platform-workspace.md`.
4. If the target service is fixed, read `clever-context-monorepo/docs/services/<service-name>/index.md`.
5. Only then run the helper script and continue with the normal `project-start` bootstrap flow.

This path is for document interpretation and repo selection. It does not change the canonical identifier rule: the canonical identifier is still the created `project-start` issue number.

### General Development Path

If the task is general development:

- do not force MSA/SaaS replication rules as the default
- do not require `target-service` before intake can start
- use the existing `project-start -> target repo -> handoff` bootstrap flow

## Template Harness Selection

After work-type branching, the agent must always present template choices to the user.

Use these sources first:

1. `clever-context-monorepo/docs/root/template-harness-governance.md`
2. `clever-context-monorepo/docs/root/deploy-template-governance.md`
3. `clever-context-monorepo/docs/templates/index.md`

If the task is maintenance and a target service is already known:

1. Read `clever-context-monorepo/docs/services/<service-name>/index.md`
2. Extract the recorded `template_id`, `template_version`, and `deploy_profile`
3. Present that lineage as the default recommendation
4. Still show the available template options and let the user choose

If the user selects a different template or a different template version than the recorded lineage, treat that as `migration`.

## First Step

First, clear the first-response hard gate and fill the startup branch state template.

If the task has already been classified as MSA-oriented service work, finish the target service conversation and the required SSOT reads first.

After that, or immediately for general development, finish the template choice conversation and then run the helper script from this repository.

Run the helper script from this repository.

```bash
python3 scripts/bootstrap_clever_work.py \
  --cwd "$PWD" \
  --template-id "<template id>" \
  --template-version "<version>" \
  --deploy-profile "<deploy profile>" \
  --override-scope "<override scope>" \
  --lifecycle-action "<adopt|modify|migrate|retire>"
```

If the user already provided fields such as purpose or constraints, pass them through:

```bash
python3 scripts/bootstrap_clever_work.py \
  --cwd "$PWD" \
  --purpose "<purpose>" \
  --constraints "<constraints>" \
  --ui-impact "<있음|없음|unknown>" \
  --expected-result "<expected result>" \
  --target-repo "<target repo if known>" \
  --template-id "<template id>" \
  --template-version "<version>" \
  --deploy-profile "<deploy profile>" \
  --override-scope "<override scope>" \
  --lifecycle-action "<adopt|modify|migrate|retire>"
```

The script emits:

- the standardized bootstrap packet
- the SSOT docs it used
- a `project_start_issue` draft
- a `repo_bootstrap` proposal
- `target_repo_seed_files` for `AGENTS.md` and `docs/project-brief.md`
- a `repo_session_handoff` recommendation
- the selected or pending template/deploy metadata

## Approval Gate

After the script runs, present the packet in the conversation and ask exactly one approval question:

> "아래 project-start 초안과 repo bootstrap 제안으로 진행할까요? 틀리면 수정할 필드만 말해 주세요."

Do not create or update records before this approval.

## After Approval

Once the user approves:

1. Treat the packet as locked context for the rest of the task.
2. Create the `project-start` issue in `clever-change-control` using the root intake template.
3. Use the created issue number as the canonical identifier.
4. Propose creation or confirmation of the target repo after the issue exists.
   - 새 target repo는 public으로 생성한다.
   - Use `gh repo create <owner>/<repo> --public` for a newly created target repo.
   - GitHub Free organization rulesets are enforced on public repositories; private repository enforcement requires GitHub Team, GitHub Pro, or GitHub Enterprise Cloud.
5. Clone or pull the target repo locally.
6. Copy the target repo seed files before handoff:
   - `docs/templates/target-repo-AGENTS.md` -> target repo `AGENTS.md`
   - `docs/templates/target-repo-project-brief.md` -> target repo `docs/project-brief.md`
   - `docs/templates/apply-target-repo-rulesets.sh` -> target repo `scripts/apply-github-rulesets.sh`
   - `docs/templates/target-repo-PULL_REQUEST_TEMPLATE.md` -> target repo `.github/PULL_REQUEST_TEMPLATE.md`
7. Apply or confirm the branch operating contract in the target repo:
   - initial remote bootstrap commit may land on `main`
   - immediately after that, create and push `dev`
   - before applying rulesets or repository protection settings, run:
     `python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --admin-preflight --target-repo-full-name <owner>/<repo> --json`
   - after `dev` exists, run `scripts/apply-github-rulesets.sh <owner>/<repo>` when GitHub Administration write permission is available
   - GitHub rulesets should target only `main` and `dev`: both require PR-only updates with `required_approving_review_count=0`, and other branches stay unrestricted by ruleset
   - after `dev` exists, block direct local pushes to `main`
   - default new work to task branches from `dev` unless the work is intentionally direct-on-`dev`
8. Recommend a new session in the cloned target repo for planning or implementation.

Only after the root issue is approved and the execution scope is fixed should a scoped change request introduce a `change-id`.

Do not create service-doc drafts in the normal start path.

## Concurrent Work Gate

Before target-repository implementation, and again before opening a PR, verify
the target repo issue and clever-change-control issue together.

The agent must check active issues, active branches, and every open PR that can
affect the same target repo, service, API, data model, deployment surface, or
file path.

Record exactly one decision:

- `done`: the related issue already has a merged or closed PR and no active
  follow-up branch, so it is ignored as a blocker.
- `blocked`: another issue, branch, or open PR is still in progress and overlaps
  the same scope, so implementation must not proceed.
- `allowed-with-non-overlap`: another issue, branch, or open PR is active, but
  the agent judges at issue level that service, API, data, deploy, and file
  scope do not overlap.
- `user-forced-proceed`: the user explicitly says `완전 무시모드`, `강제 진행`,
  or `user-forced-proceed`. This is a user override, not an agent safety
  approval. The agent must record conflict candidates, known merge risk, and
  사용자 강제 진행 in the target repo issue, clever-change-control issue, and PR
  body, then continue until a real git conflict, test failure, or merge failure
  must be resolved.

## Standard Packet

Before the helper script, every run should normalize the startup branch state into this shape:

```yaml
startup_branch:
  work_kind:
  architecture_kind:
  session_goal:

context:
  requested_work_summary:
  why_now:
  constraints:
  expected_result:
  known_repo:
  known_service:

workspace:
  current_repo:
  workspace_check_mode:
  workspace_check_result:

routing:
  start_surface:
  interpretation_source:
  tracking_source:

derived:
  workload_shape:
  deploy_template_candidate:
  deploy_profile_candidate:
  next_action:

deferred:
  project_start_issue_number:
  change_id:
  target_repo:
  target_service:
  rollout_scope:
```

After that, the helper run should normalize the project-start packet into this shape:

```text
user-session:
current-working-repo:
current-working-repo-path:
target-repo:
purpose:
constraints:
ui-impact:
expected-result:
template-id:
template-version:
deploy-profile:
override-scope:
lifecycle-action:
ssot-docs-read:
project-start-issue:
repo-bootstrap:
repo-session-handoff:
next-step:
```

Never replace this with a looser narrative summary.

## Git Branch Meaning

After a target repo exists, enforce this git meaning:

- `main = deploy`
- `dev = work`
- `branch = role-specific work`

Rules:

- the initial commit to a brand-new remote repo may use `main`
- after that initial remote publish, create and push `dev`
- once `dev` exists, do not use direct push to `main`
- direct work on `dev` is allowed, but task branches are the preferred default
- child branches from task branches are allowed when the work is explicitly nested
- a PR into `dev` or `main` must finish review-agent work with wiki/service context updates, or a documented not-needed decision
- do not upload PR information to the wiki; update only service, operational, contract, or navigation context
- issue close should refer to the PR review completion result instead of duplicating the context/wiki decision

## PR Branch Cleanup

PR 완료 후 branch 정리:

After a PR is merged, or closed with the source branch intentionally abandoned,
clean up the task branch unless it still has an open PR, linked follow-up issue,
child branch, or active release/hotfix use.

Default command sequence:

```bash
git switch dev
git pull --ff-only origin dev
git branch -d <source-branch>
git push origin --delete <source-branch>
git fetch --prune origin
```

- `main`과 `dev`는 삭제 대상이 아니다.
- Use `git branch -d <source-branch>` by default.
- Use `git branch -D <source-branch>` only when the PR was closed without merge
  and the user explicitly confirms the branch can be discarded.
- Do not delete a remote branch if it still backs an open PR, follow-up issue,
  child branch, or active release/hotfix.
- If GitHub already deleted the remote branch, still run `git fetch --prune origin`.

## Common Mistakes

- Treating MSA/SaaS replication rules as the default path for every CLEVER task.
- Treating the current repo as the workflow SSOT.
- Skipping the three-step opening template because the request "already sounds clear enough."
- Skipping the template choice conversation because one option looks obvious.
- Starting implementation before the `project-start` issue is drafted and approved.
- Requiring an inferred `target-service` before the intake can begin for general work.
- Generating a canonical `change-id` before the root issue exists.
- Letting template changes slip through as an ordinary edit instead of `migration`.
- Creating service-doc work in the normal bootstrap path.
- Editing change-control or repo resources before the final approval step.

## Real-World Impact

This skill exists to reduce user effort without reducing control:

- non-developers can give business intent instead of process details
- agents start from the same intake structure every time
- root issue creation, repo bootstrap, and session handoff stay aligned from the beginning
