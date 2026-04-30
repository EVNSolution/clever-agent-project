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

Before showing the first-response template, infer the GitHub account from gh CLI first, then automatically inspect the local workspace,
`gh auth status`, GitHub login, remotes, repo visibility, and issue/PR/ruleset read access:

```bash
python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --json
```

Ask the user for their GitHub login or profile URL only if gh CLI cannot infer the authenticated account or the user needs to override it. In that case, pass it with `CLEVER_EXPECTED_GITHUB_LOGIN` or `--expected-github-login`.

If the session is explicitly about editing the current control-plane repo itself, run:

```bash
python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --current-repo-maintenance --json
```

Interpret the result like this:

- `preflight_check.ready=false`: stop and show the failed checks before asking startup questions.
- `preflight_check.ready=true`: continue by reading `workspace_check.agent_action`.
- `auto_skipped_questions`: do not ask these questions again; tool evidence already answered them.
- `recovery_actions`: use these concrete commands/actions to fix failed checks before continuing.
- `next_questions`: ask only these remaining user questions after automatic checks.
- `workspace_check.agent_action=proceed-with-hard-gate`: continue in the current session
- `workspace_check.agent_action=current-repo-maintenance`: stay in the current control-plane repo and treat it as the target
- `workspace_check.agent_action=switch-to-clever-agent-project`: move startup to `clever-agent-project` first
- `workspace_check.agent_action=stop-and-fix-workspace`: stop and clearly state that the local three-repository workspace is incomplete

There is no shared default GitHub login.
On first startup, infer the GitHub account from gh CLI first. Ask for a GitHub login/profile URL only when gh CLI cannot infer the account or the user needs to override it, then pass it with `CLEVER_EXPECTED_GITHUB_LOGIN` or `--expected-github-login`.
Preflight also checks active `EVNSolution` org membership. Repository creation
permission cannot be proven without the actual `gh repo create` write attempt,
so treat that command's success as the creation proof after preflight passes.

Before planning, implementation, `project-start` creation, or repo bootstrap, the agent must first normalize the session into the same opening structure.

Use this exact first-response template:

```text
[시작 분기]
먼저 하려는 일을 한 줄로 적어 주세요.
선택지에 맞춰 답해도 되고, 애매하면 문장으로 편하게 설명해도 됩니다.

- 하려는 일:

아래 항목은 모르면 `아직 모름`으로 둬도 됩니다.
각 항목은 선택지 중 하나를 골라도 되고, 선택지에 딱 맞지 않으면 직접 설명해도 됩니다.

1. 작업 성격은 어디에 가깝나요?
- 신규 개발
- 기존 기능 확장/수정
- 버그 수정
- 리팩터링/구조 개선
- 문서/설정/운영 정리
- 아직 모름
- 직접 설명:

2. 대상 범위는 무엇인가요?
- 새 앱/서비스/기능
- 기존 앱/서비스/기능
- 화면/UI
- API
- DB/model
- CI/CD 또는 배포 workflow
- 문서/운영 설정
- 아직 모름
- 직접 설명:

3. 이번 작업의 목표 수준은 어디까지인가요?
- 요구사항 정리
- 설계 문서 작성
- 구현 계획 수립
- 실제 코드 변경
- 테스트/검증
- 배포/운영 준비
- 1차 MVP 개발 및 배포
- 운영 반영
- 아직 모름
- 직접 설명:

4. 알고 있는 이름이나 링크가 있나요? 없으면 비워도 됩니다.
- repo:
- service/app:
- 화면:
- API:
- DB/model:
- 문서:
- issue/PR/Figma/회의 메모/에러 로그:

5. 현재 상태를 알고 있나요? 모르면 `아직 모름`으로 둬도 됩니다.
- 이미 되어 있는 것:
- 아직 없는 것:
- 먼저 확인해야 할 것:

6. 주의할 점이 있나요? 없으면 비워도 됩니다.
- 꼭 지킬 것:
- 피할 것:
- 건드리면 안 되는 범위:
- 보안/운영/배포 관련 주의사항:
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

To clear the first hard gate, the intake only needs enough non-technical information for:

- `하려는 일`
- `1. 작업 성격은 어디에 가깝나요?`
- `2. 대상 범위는 무엇인가요?`
- `3. 이번 작업의 목표 수준은 어디까지인가요?`

Known names, links, current state, constraints, and background are optional at first. Do not force users to answer prerequisites they may not know yet.

## Work-Type Branching

Before running the helper script, classify the task into one of these paths.

The user-facing questions stay simple, but the agent must interpret them against the internal `change-control` model.

### Interpretation Rules

Interpret the easy answers in this order:

1. `하려는 일`
2. `작업 성격은 어디에 가깝나요?`
3. `대상 범위는 무엇인가요?`
4. `이번 작업의 목표 수준은 어디까지인가요?`

Map work nature like this:

- `신규 개발` -> `work_nature=new_development`
- `기존 기능 확장/수정` -> `work_nature=feature_change`
- `버그 수정` -> `work_nature=bugfix`
- `리팩터링/구조 개선` -> `work_nature=refactor`
- `문서/설정/운영 정리` -> `work_nature=docs_ops`
- `아직 모름` or `직접 설명` -> keep or infer the matching internal field later

Map target scope like this:

- `새 앱/서비스/기능` -> `target_scope=new_app_service_feature`
- `기존 앱/서비스/기능` -> `target_scope=existing_app_service_feature`
- `화면/UI` -> `target_scope=ui`
- `API` -> `target_scope=api`
- `DB/model` -> `target_scope=db_model`
- `CI/CD 또는 배포 workflow` -> `target_scope=cicd_deploy_workflow`
- `문서/운영 설정` -> `target_scope=docs_ops_config`
- `아직 모름` or `직접 설명` -> keep or infer the matching internal field later

Map goal level like this:

- `요구사항 정리` -> `goal_level=requirements`
- `설계 문서 작성` -> `goal_level=design_doc`
- `구현 계획 수립` -> `goal_level=implementation_plan`
- `실제 코드 변경` -> `goal_level=code_change`
- `테스트/검증` -> `goal_level=test_verification`
- `배포/운영 준비` -> `goal_level=deploy_preparation`
- `1차 MVP 개발 및 배포` -> `goal_level=mvp_develop_deploy`
- `운영 반영` -> `goal_level=operations_rollout`
- `아직 모름` or `직접 설명` -> keep or infer the matching internal field later

Then derive `project_scope`, `service_scope`, and `session_goal` from the combination. MONO/MSA is not user-facing in the first template; infer `architecture_kind` from context later, or keep it `unknown`.

If the explanation is still too vague after the first template pass, ask a short follow-up question before continuing.

After this interpretation, classify the task into one of these paths:

- `MSA/SaaS 복제형 작업`
- `일반 개발 작업`

Treat MSA-oriented new or existing service work as the MSA path.

Treat MONO-oriented service work as the general development path, but do not ask users to choose MONO/MSA terminology in the first response.

Treat `현재 control-plane 저장소 자체 수정` as control-plane maintenance and do not force a target service.

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
7. 첫 main push 전에는 target repo 루트 `AGENTS.md`가 존재하고, copied source `docs/templates/target-repo-AGENTS.md`의 실행 절차가 반영되어 initial commit에 staged 되었는지 확인한다. 루트 `AGENTS.md`가 없거나 비어 있거나 staged 상태가 아니면 push하지 않는다. 먼저 stage한 뒤 `git status --short`와 `git diff --cached -- AGENTS.md`로 확인한다.
8. Apply or confirm the branch operating contract in the target repo:
   - initial remote bootstrap commit may land on `main`
   - immediately after that, create and push `dev`
   - before applying rulesets or repository protection settings, run:
     `python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --admin-preflight --target-repo-full-name <owner>/<repo> --json` (add `CLEVER_EXPECTED_GITHUB_LOGIN` only when gh CLI inference fails or needs override)
   - after `dev` exists, run `scripts/apply-github-rulesets.sh <owner>/<repo>` when GitHub Administration write permission is available
   - GitHub rulesets should target only `main` and `dev`: both require PR-only updates with `required_approving_review_count=0`, and other branches stay unrestricted by ruleset
   - after `dev` exists, block direct local pushes to `main`
   - default new work to task branches from `dev` unless the work is intentionally direct-on-`dev`
9. Recommend a new session in the cloned target repo for planning or implementation.

### Scoped Target Work After Bootstrap

For every non-trivial development task after the target repo exists, the agent
must treat the request as a GitHub issue-linked workflow before editing files:

1. Create or identify the target repository issue.
2. Create or identify the matching `clever-change-control` issue when scoped
   change tracking is needed.
3. Link both issues with explicit mentions.
4. Create the branch only through GitHub Development:

```bash
gh issue develop <target-issue-number> \
  --repo <target-repo-full-name> \
  --base dev \
  --name cc-<change-control-issue-number>-<short-scope> \
  --checkout
```

5. Verify the linked branch:

```bash
gh issue develop --list <target-issue-number> \
  --repo <target-repo-full-name>
```

Do not use `git checkout -b` first. Do not implement, commit, or open a PR until
the issue link and GitHub Development linked branch are ready. PRs for normal
work branch into `dev`, and PR bodies list the target issue plus the
`clever-change-control` issue.

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

## PR Scope Grouping Gate

Before opening a PR, decide whether the changes should stay together or be
split.

Keep one PR when the changes share the same document/operating-rule cleanup and
the same validation command covers them. This includes small sync work across
`AGENTS.md`, PR templates, startup state templates, project brief templates,
design source policy, and merge title template sync when they all express the
same operating rule.

Split PRs when the work crosses a different app/service/contract surface, has a
different test scope or likely failure point, has a merge order dependency, or
would need a different rollback unit.

OpenAPI schema changes, Admin Web smoke screen work, Rider App smoke screen
work, and Spring service mock endpoint work are examples that usually deserve
separate PRs.

## Standard Packet

Before the helper script, every run should normalize the startup branch state into this shape:

```yaml
startup_branch:
  work_nature:
  target_scope:
  goal_level:
  project_scope:
  service_scope:
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
- Skipping the easy startup template because the request "already sounds clear enough."
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
