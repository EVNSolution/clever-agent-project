# AGENTS.md

## Scope

This file defines the startup contract for agents working from `clever-agent-project`.

This repository is **not** a standalone execution environment.
It is the entrypoint of a **local three-repository control-plane workspace**.

## Workspace Contract

Before doing any real work, confirm that all of the following repositories exist in the same local workspace root:

1. `clever-agent-project`
2. `clever-context-monorepo`
3. `clever-change-control`

Recommended local layout:

```text
<CLEVER_ROOT>/
  clever-agent-workspace/
    clever-agent-project/
    clever-context-monorepo/
    clever-change-control/
  projects/
    <project-slug>/
      <target-repo>/
```

`<CLEVER_ROOT>` is the top-level CLEVER work root. Keep the three agent/control
repositories inside `<CLEVER_ROOT>/clever-agent-workspace/`. Put real product/service target
repositories under `<CLEVER_ROOT>/projects/<project-slug>/<target-repo>/`. When
bootstrapping a target repo, clone or pull the remote repo into that project
folder, then inject the agent documents into the target repo root.

If any of these repositories are missing, the workspace is incomplete.
Do not pretend web links are a substitute for local context.
Stop and state that the three-repository local workspace is required.

At startup, infer the GitHub account from gh CLI first, then run this automatic preflight:

```bash
python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --json
```

Ask the current user for their GitHub login or profile URL only if gh CLI cannot infer the authenticated account or the user needs to override it. In that case, pass it with `CLEVER_EXPECTED_GITHUB_LOGIN` or `--expected-github-login`.

If the session is explicitly about editing the current control-plane repo itself, run:

```bash
python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --current-repo-maintenance --json
```

The preflight must verify at least:

- local `git` and `gh` CLIs
- `gh auth status`
- GitHub login inferred from `gh api user --jq .login`
- optional user-provided GitHub login via `CLEVER_EXPECTED_GITHUB_LOGIN` or
  `--expected-github-login` when inference fails or an account override is needed
- active membership in the `EVNSolution` GitHub org
- local three-repository workspace readiness
- control-plane origin remotes under `EVNSolution/*`
- clean control-plane worktrees
- remote fetch access
- GitHub repo visibility and issue/PR/ruleset read access

If `preflight_check.ready` is false, stop before startup questions and report the
failed checks.

Read these preflight output fields before asking anything:

- `auto_skipped_questions`: questions already answered by tool evidence, such as
  GitHub login inference, startup location, or dirty-state inspection.
- `recovery_actions`: concrete commands or actions for failed checks.
- `next_questions`: the minimal remaining user questions after automatic checks.

If it is true, use the returned `workspace_check.agent_action` field as the
startup branch:

- `proceed-with-hard-gate`
- `current-repo-maintenance`
- `switch-to-clever-agent-project`
- `stop-and-fix-workspace`

Before creating a target repo, applying rulesets, or changing GitHub protection
settings, run admin preflight with the target repo:

```bash
python3 scripts/bootstrap_clever_work.py \
  --cwd "$PWD" \
  --admin-preflight \
  --target-repo-full-name EVNSolution/<target-repo> \
  --json
```

Repository creation permission cannot be proven without the actual write attempt.
Treat org membership and token/API access as the pre-create gate, then treat
`gh repo create` success as the creation proof.

## Clone-Ready Startup Contract

This section exists for a fresh clone of `clever-agent-project`.

When a new agent session opens in this repository after clone, the agent must be
ready to receive the startup answers and must leave the startup questions in the
conversation if the answers are not already present.

First action:

```bash
python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --json
```

Then apply the result:

- `preflight_check.ready=false`: show failed checks and stop before asking
  project-start questions.
- `preflight_check.ready=true`: read `workspace_check.agent_action` and continue.
- `proceed-with-hard-gate`: 작업 시작 질문을 남긴다.
- `switch-to-clever-agent-project`: tell the user to reopen or continue from
  `clever-agent-project`, then 작업 시작 질문을 남긴다.
- `current-repo-maintenance`: ask only for the control-plane maintenance target
  and expected result.
- `stop-and-fix-workspace`: show the missing repository list and stop before
  asking project-start questions.

### 작업 시작 질문

The user may either fill the block or describe the work naturally.
양식을 채워도 되고, 자연어로 편하게 설명해도 된다.
In both cases, the agent must normalize the input into the startup branch fields
before drafting `project-start`.

If the user has not already provided the startup branch, leave this exact block:

```text
작업 시작

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

If the user starts with free-form text, do not discard it. Restate it into the
same block and mark missing values as `needs-input`.

### 자연어 입력 처리 규칙

When the user writes naturally instead of filling the form:

1. Preserve the user's intent in `하려는 일` first.
2. Convert the easy choices into internal `work_nature`, `target_scope`, and `goal_level` values.
3. Derive `project_scope`, `service_scope`, and `session_goal` from those values only when clear.
4. Infer `architecture_kind` only when the wording or repository context is clear; otherwise keep it `unknown`.
5. Do not ask 전문 용어 such as MONO/MSA, `target_service`, rollout scope, or `change_id` in the first response.
6. Mark ambiguous or missing fields as `needs-input`.
7. Ask only for the missing fields that block the next step.

Example:

```text
사용자 입력:
회원가입, 로그인, 사용자 확인 기능이 있는 단순한 인증 시스템을 만들고 싶다.
작업 성격은 신규 개발이고, 대상 범위는 새 앱/서비스/기능이다.
이번에는 실제 코드 변경까지 하고 싶고, 권한 관리나 소셜 로그인은 나중에 하고 싶다.

정규화:
- work_nature: new_development
- target_scope: new_app_service_feature
- goal_level: code_change
- project_scope: new_project
- service_scope: new_service
- architecture_kind: unknown
- session_goal: implementation_work
- requested_work_summary: 회원가입, 로그인, 사용자 확인 기능이 있는 단순한 인증 시스템 개발
- constraints: 권한 관리와 소셜 로그인은 초기 범위 제외
- needs-input: 알려진 repo/service가 있는지, 꼭 지켜야 할 추가 조건이 있는지
```

### 질문 원장

When information is partial, leave a short question ledger before continuing:

```text
질문 원장
- known answer:
  - 하려는 일:
  - 작업 성격:
  - 대상 범위:
  - 목표 수준:
  - 알고 있는 이름이나 링크:
  - 현재 상태:
  - 주의할 점:
- normalized:
  - work_nature:
  - target_scope:
  - goal_level:
  - project_scope:
  - service_scope:
  - architecture_kind:
  - session_goal:
- needs-input:
  - <missing field 1>
  - <missing field 2>
```

Ask only for fields listed under `needs-input`.
Do not ask for `change_id`, fixed `target_service`, or rollout scope at clone
startup.

## What Each Repository Owns

- `clever-agent-project`
  - Entry point
  - Intake
  - Bootstrap packet generation
  - Handoff into target repositories

- `clever-context-monorepo`
  - Canonical interpretation
  - Template lineage
  - Service metadata
  - Deploy baseline

- `clever-change-control`
  - `project-start` root
  - Scoped change requests
  - Rollout / rollback trace
  - Release evidence linkage

Actual implementation work happens in a separate **target repository**.
The three repositories above form the control plane, not the product implementation plane.

## Document Roles Inside This Repository

Treat the main documents in `clever-agent-project` as separate layers:

- `README.md`
  - Human-facing portal
  - Workspace-first summary
  - Quick navigation into the control plane

- `docs/setting.md`
  - Operational manual
  - Runtime prerequisites
  - Workspace topology
  - Bootstrap expectations
  - Startup rules and local operating assumptions

- `docs/guides/clever-project-workflows.md`
  - Scenario guide
  - New build vs. maintenance vs. handoff flow

- `docs/guides/session-start-smoke-test.md`
  - Startup smoke test scenario
  - First-session validation examples
  - Pass / fail expectations for the hard gate

- `docs/templates/startup-branch-state-template.md`
  - Normalized startup branch state
  - Mapping from first-response answers into internal intake fields
  - Required pre-packet state

- `.agent/skills/bootstrap-clever-work/SKILL.md`
  - Agent execution rulebook
  - Startup hard gate
  - Bootstrap behavior

Do not collapse these roles into one document in your own reasoning.
Read `docs/setting.md` as the detailed operating reference for this repository.

## Startup Read Order

When starting work from this repository, read in this order:

1. `README.md`
2. `docs/setting.md`
3. `docs/templates/startup-branch-state-template.md`
4. `docs/guides/clever-project-workflows.md`
5. `docs/guides/session-start-smoke-test.md`
6. `.agent/skills/bootstrap-clever-work/SKILL.md`
7. `../clever-context-monorepo/docs/root/authority-boundaries.md`
8. `../clever-context-monorepo/docs/root/index.md`
9. `../clever-change-control/README.md`

If the task is service-specific, also read:

- `../clever-context-monorepo/docs/services/<service>/index.md`

If the task is template-specific, also read:

- `../clever-context-monorepo/docs/templates/index.md`

## First-Response Contract

Do not jump straight into implementation.

If the automatic preflight report returns `workspace_check.agent_action=stop-and-fix-workspace`, do not continue as if the environment were complete.

For a new session, begin by collecting the startup branch first.

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

Normalize the answers into the startup branch state template in:

- `docs/templates/startup-branch-state-template.md`

The template must be filled before `project-start` drafting, repo bootstrap, or implementation planning.

If the user starts in free-form text, restate the request into this structure and ask only for the missing fields.

## Authority Rules

These rules are mandatory:

- The canonical root start record is `project-start issue #`
- `change_id` is **not** the root start identifier
- `change_id` only becomes required after scoped execution is fixed
- Do not require a fixed `target_service` at generic intake start
- Do not assume the implementation repository is already known at session open

Short version:

- start in `clever-agent-project`
- interpret in `clever-context-monorepo`
- anchor and trace in `clever-change-control`
- implement in the target repository

## Target Repository GitHub Workflow Gate

This gate applies to every non-trivial development task in a target repository.
It exists so the agent interprets implementation requests as a GitHub
issue-linked workflow, not as an immediate local edit.

Do not treat GitHub automatic references as sufficient traceability. Plain issue
mentions such as `<context-owner>/<root-context-repo>#<issue>` or
`<control-owner>/clever-change-control#<issue>` may create links in GitHub, but
the agent must still build and maintain the working trace.

Do not hard-code a GitHub organization, root context repository, or target
repository name in this rule. Resolve repository identifiers from the current
workspace, `git remote -v`, issue URLs, or explicit user instructions.

Before any implementation, commit, or PR in a target repository, complete this
sequence in order:

1. Create or identify the target repository issue for the actual work.
2. When the work needs scoped change tracking, create or identify the matching
   `clever-change-control` issue.
3. Link the target issue and the `clever-change-control` issue to each other
   with explicit issue mentions.
4. Create the work branch from the target issue with GitHub Development. Do not
   run `git checkout -b` first.
5. Verify the linked branch after creation.
6. Only after the target issue, optional change-control issue, and linked branch
   are ready may the agent implement, commit, or open a PR.

CLI branch creation must use this shape, with the actual target repo resolved
from the task context:

```bash
gh issue develop <target-issue-number> \
  --repo <target-repo-full-name> \
  --base dev \
  --name cc-<change-control-issue-number>-<short-scope> \
  --checkout
```

Then verify the GitHub Development linked branch:

```bash
gh issue develop --list <target-issue-number> \
  --repo <target-repo-full-name>
```

For a task explicitly targeting `EVNSolution/thundercrew-domain`, the command
uses `--repo EVNSolution/thundercrew-domain` and `--base dev`.

Branch and PR rules:

- Work branches always start from `dev`.
- The branch name format is exactly
  `cc-<change-control-issue-number>-<short-scope>`, for example
  `cc-74-dashboard-mapstate-frontend`.
- If a change-control issue is genuinely not needed, create a target issue first
  and record why no `clever-change-control` issue is needed before choosing a
  branch name.
- PRs for non-trivial development go from the work branch into `dev`.
- The PR body must list both the target issue and the `clever-change-control`
  issue, or explicitly state why no change-control issue was needed.

Forbidden actions:

- Do not create the work branch manually with `git checkout -b` before GitHub
  Development links it to the target issue.
- Do not work on a branch that is not linked to a GitHub issue through
  `gh issue develop`.
- Do not develop or commit directly on `dev`.
- Do not create a branch without an issue.
- Do not implement without a linked branch.
- Do not merge into `dev` without a PR.
- Do not expose internal agent/tool names in public commit titles, PR titles,
  merge commit titles, or GitHub attribution unless they are directly relevant.
- Do not leave internal automation attribution such as `Co-authored-by: OmX` in
  public development history.

Merge rules:

- Prefer a merge method where the PR trace is visible in `dev` history, such as
  a merge commit.
- If squash merge is necessary, the squash commit title must include the PR
  number, for example `Dashboard map-state frontend integration (#62)`.
- Do not create PR-numberless squash commits, commit titles that look like direct
  commits to `dev`, or merge commits with unclear provenance.

Minimum verification before opening the PR:

```bash
npm run check:workspace
npm run lint
npm run typecheck
npm run build
```

If frontend tests exist, also run:

```bash
npm run test:service-ops
# plus the relevant frontend test command
```

If backend code changed, also run:

```bash
cd development/service-ops-api && ./gradlew test
cd development/service-ops-api && ./gradlew build
```

Every work report must include:

1. target issue number
2. change-control issue number, or the recorded reason it was not needed
3. linked branch name
4. PR number
5. merge commit
6. verification command results
7. remaining follow-up work

## Concurrent Work Gate

Before target-repository implementation, and again before opening a PR, verify
the target repo issue and the matching clever-change-control issue together.
The check must include active issues, active branches, and every open PR that
can affect the same target repo, service, API, data model, deployment surface,
or file path.

Record one decision:

- `done`: the related issue already has a merged or closed PR and no active
  follow-up branch, so the agent may ignore it as a blocker.
- `blocked`: another issue or open PR is still in progress and the work overlaps,
  so the agent must not proceed.
- `allowed-with-non-overlap`: another issue or open PR is in progress, but the
  agent judges at issue level that the service, API, data, deploy, and file
  scope do not overlap. Record the non-overlap reason before proceeding.
- `user-forced-proceed`: the user explicitly says `완전 무시모드`, `강제 진행`,
  or `user-forced-proceed`. In this mode the agent does not use concurrent
  issue, branch, or open PR overlap as a blocking condition. The agent records
  conflict candidates, known merge risk, and that this is 사용자 강제 진행, then
  continues until a real git conflict, test failure, or merge failure must be
  resolved.

The decision and evidence must be written to both the target repo issue and the
clever-change-control issue. The PR body must repeat the final parallel work
decision.

## PR Scope Grouping Gate

Before opening a PR, decide whether the current changes belong in one PR or
must be split.

Prefer one PR when the work is the same document/operating-rule cleanup and the
same validation command is enough to review it. Do not split small operational
documentation cleanup only because it touches several policy or template files;
that creates repeated issue linkage and context-completion records without a
clearer review unit.

Keep one PR when:

- the changes are under the same issue and the same document/operating-rule
  cleanup axis
- the same validation command covers the full change
- the touched files are sync targets for the same policy, such as `AGENTS.md`,
  PR templates, startup state templates, project brief templates, design source
  policy, or merge title template sync

Split into separate PRs when:

- the work touches a different app/service/contract surface
- the test scope and likely failure point are different
- there is a merge order dependency between parts
- a failure would require a different rollback unit

Examples that should usually be split: OpenAPI schema changes, Admin Web smoke
screen work, Rider App smoke screen work, and Spring service mock endpoint work.

During and after the work, update the `clever-change-control` issue with:

- current session phase: documentation, implementation, verification, or release
  preparation
- target repository
- branch name
- relevant commits
- PR link, when one exists
- current status
- next action

Use `fixes`, `closes`, or similar GitHub keywords only when the PR merge is
intended to close the referenced issue. For context linking without automatic
closure, use plain issue mentions.

## Control-plane Main Branch Contract

The three CLEVER control-plane repositories are public and their `main`
branches are protected by the GitHub ruleset `CLEVER protect main`:

- `clever-agent-project`
- `clever-context-monorepo`
- `clever-change-control`

Do not push directly to `main` for control-plane changes. Use a role-prefixed
branch and open a PR into `main`. `main` requires a PR but does not require
approving reviews. Merge/write access is limited to repository admins.
Admin bypass is allowed only in `pull_request` mode.

## Branch Operating Contract

Treat git branch roles like this:

- `main`
  - deployment branch
  - remote bootstrap branch only for the first repository publish
  - after `dev` exists, do not push directly to `main`
- `dev`
  - working integration branch
  - default base branch for follow-up work after the initial remote bootstrap
- task branches
  - role-specific or unit-of-work branches
  - preferred default for non-trivial work
  - may branch from `dev`
  - may also branch from another task branch when the work is explicitly a child branch of that branch

Operational rule:

1. A newly created remote repo may use `main` for the initial remote bootstrap commit.
2. Immediately after that initial remote commit, create and push `dev`.
3. After `dev` exists, set a local guard that blocks direct pushes to `main`.
4. Small or urgent work may happen directly on `dev`, but the preferred default is a task branch.
5. Promotion into `main` happens as a reviewed merge unit, not as normal day-to-day working push traffic.

When the agent bootstraps or confirms a target repo, it should preserve this meaning:

- `main = deploy`
- `dev = work`
- `branch = role-specific work`

첫 main push 전에는 target repo 루트 `AGENTS.md`가 `docs/templates/target-repo-AGENTS.md`에서 복사되어 initial commit에 포함되는지 반드시 확인한다. 누락, 빈 파일, stage 누락 상태이면 먼저 seed 파일을 복사/stage하고 `git status --short`, `git diff --cached -- AGENTS.md`로 확인하기 전에는 push하지 않는다.

If local branch protection is requested or available, prefer a repo-local `pre-push` guard for `main`.

## PR Merge Commit Title Contract

When merging a PR into `main`, make the resulting main commit visibly PR-based.
Use the GitHub default-style merge subject. If the agent uses squash merge,
set the subject explicitly:

```bash
gh pr merge <pr-number> --squash \
  --subject "Merge pull request #<pr-number> from <owner>/<source-branch>" \
  --body-file <merge-body-file>
```

Merge body should start with the PR title, then include:

- merge summary
- validation evidence
- wiki/service context update result

Do not use a plain feature/doc commit title as the main merge commit subject.

## PR Branch Cleanup Contract

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

## What Not To Do

Do not:

- treat this repository as the only source of truth
- treat GitHub links as sufficient when local repositories are missing
- open scoped execution before the root line is understood
- force `change_id` too early
- force a concrete `target_service` too early
- implement product code in control-plane repositories unless the task is explicitly about the control plane

## Expected Flow

The expected operating flow is:

1. Infer the current GitHub account from gh CLI first, ask for GitHub login/profile URL only when inference fails or needs override, then run preflight for the three-repository local workspace and GitHub account
2. Gather the startup frame
   - collect `work_nature`, `target_scope`, `goal_level`, then derive `project_scope`, `service_scope`, `architecture_kind`, `session_goal`
   - fill the startup branch state template
3. Read canonical context
4. Draft the `project-start` payload
5. Anchor the root line in `clever-change-control`
6. Fix scoped execution
7. Apply or confirm the repo branch operating contract
8. Handoff to the target repository under `<CLEVER_ROOT>/projects/<project-slug>/<target-repo>/`
9. Feed rollout / rollback / release evidence back into `clever-change-control`

## If The Workspace Is Incomplete

Say this clearly:

> CLEVER requires a local three-repository workspace:
> `clever-agent-project`, `clever-context-monorepo`, and `clever-change-control`.
> This workspace is incomplete, so startup interpretation and traceability are degraded.

Do not continue as if the environment were complete.
