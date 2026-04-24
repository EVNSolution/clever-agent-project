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

If any of these repositories are missing, the workspace is incomplete.
Do not pretend web links are a substitute for local context.
Stop and state that the three-repository local workspace is required.

At startup, run this automatic check first:

```bash
python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --workspace-check --json
```

If the session is explicitly about editing the current control-plane repo itself, run:

```bash
python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --workspace-check --current-repo-maintenance --json
```

Use the returned `agent_action` field as the startup branch:

- `proceed-with-hard-gate`
- `current-repo-maintenance`
- `switch-to-clever-agent-project`
- `stop-and-fix-workspace`

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

If the automatic workspace check returns `stop-and-fix-workspace`, do not continue as if the environment were complete.

For a new session, begin by collecting the startup branch first.

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

## Target Repository Traceability Gate

This gate applies to every target project opened with this three-repository control
plane, regardless of the directory where the agent session starts.

Do not treat GitHub automatic references as sufficient traceability. Plain issue
mentions such as `<context-owner>/<root-context-repo>#<issue>` or
`<control-owner>/clever-change-control#<issue>` may create links in GitHub, but
the agent must still build and maintain the working trace.

Do not hard-code a GitHub organization, root context repository, or target
repository name in this rule. Resolve repository identifiers from the current
workspace, `git remote -v`, issue URLs, or explicit user instructions.

Before any target-repository implementation, the agent must establish an
issue-to-branch trace chain anchored in `clever-change-control`.

Required chain:

1. Identify the root context issue when one exists, such as
   `<context-owner>/<root-context-repo>#<issue>`.
2. Identify or create the `clever-change-control` anchor:
   - `project-start` issue for the root start record
   - `change-request` issue for scoped execution
3. Identify or create the target repository issue for the actual work, such as
   `<target-owner>/<target-repo>#<issue>`.
4. Cross-link the records with explicit issue mentions:
   - the `clever-change-control` issue mentions the root context issue and target
     repository issue
   - the target repository issue mentions the `clever-change-control` issue
5. Create or confirm a branch for the scoped work before implementation.

Branch rules:

- A branch must correspond to a tracked issue or scoped work item.
- One parent issue may have many child branches.
- Prefer branch names that include the trace identifier, for example:
  - `cc-12-issue-34-login-timeout`
  - `issue-34-login-timeout`
- If multiple branches belong to one issue, list all active branches on the
  `clever-change-control` issue.

The agent must not begin implementation if the trace chain is missing. First
create or identify the required issue records, add the bidirectional mentions,
and state the branch that will carry the work.

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

If local branch protection is requested or available, prefer a repo-local `pre-push` guard for `main`.

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

1. Verify the three-repository local workspace
2. Gather the startup frame
   - collect `work_kind`, `architecture_kind`, `session_goal`
   - fill the startup branch state template
3. Read canonical context
4. Draft the `project-start` payload
5. Anchor the root line in `clever-change-control`
6. Fix scoped execution
7. Apply or confirm the repo branch operating contract
8. Handoff to the target repository
9. Feed rollout / rollback / release evidence back into `clever-change-control`

## If The Workspace Is Incomplete

Say this clearly:

> CLEVER requires a local three-repository workspace:
> `clever-agent-project`, `clever-context-monorepo`, and `clever-change-control`.
> This workspace is incomplete, so startup interpretation and traceability are degraded.

Do not continue as if the environment were complete.
