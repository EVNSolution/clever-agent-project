# startup branch state template

## 목적

이 문서는 세션 첫 대화에서 받은 분기값을 에이전트가 어떤 내부 템플릿으로 정규화해야 하는지 고정한다.

이 템플릿은 `project-start` packet보다 먼저 채운다.

즉 순서는 아래다.

1. 첫 진입시 대화문으로 분기값 수집
2. 이 문서의 startup branch state 채우기
3. SSOT 해석
4. `project-start` 초안과 bootstrap packet 생성

## 첫 진입시 대화문

에이전트는 첫 응답에서 아래 템플릿을 사용한다.

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

## normalized startup branch state

```yaml
startup_branch:
  work_kind: new_start | existing_change | repo_maintenance
  architecture_kind: mono | msa
  session_goal: requirements_definition | service_onboarding | implementation_work | deploy_preparation

context:
  requested_work_summary: ""
  why_now: ""
  constraints: ""
  expected_result: ""
  known_repo: ""
  known_service: ""

workspace:
  current_repo: ""
  workspace_check_mode: generic_startup | current_repo_maintenance
  workspace_check_result: proceed-with-hard-gate | current-repo-maintenance | switch-to-clever-agent-project | stop-and-fix-workspace

routing:
  start_surface: clever-agent-project | current-repo
  interpretation_source: clever-context-monorepo
  tracking_source: clever-change-control

derived:
  workload_shape: single_workload | multiple_workloads
  deploy_template_candidate: ""
  deploy_profile_candidate: ""
  next_action: ""

deferred:
  project_start_issue_number: null
  change_id: null
  target_repo: null
  target_service: null
  rollout_scope: null
```

## 값 채우기 규칙

### startup_branch

- `새 작업 시작` -> `work_kind: new_start`
- `기존 서비스 변경` -> `work_kind: existing_change`
- `현재 저장소 자체 수정` -> `work_kind: repo_maintenance`

- `MONO` -> `architecture_kind: mono`
- `MSA` -> `architecture_kind: msa`

- `요구사항/문서 정의` -> `session_goal: requirements_definition`
- `서비스 온보딩 정의` -> `session_goal: service_onboarding`
- `구현 repo 작업` -> `session_goal: implementation_work`
- `배포 준비` -> `session_goal: deploy_preparation`

### context

- `하려는 일` -> `requested_work_summary`
- `왜 필요한지` -> `why_now`
- `제약` -> `constraints`
- `기대 결과` -> `expected_result`
- `알고 있는 repo/service가 있으면` -> `known_repo`, `known_service`

repo와 service가 둘 다 확정되지 않았으면 빈 값으로 둔다.

### workspace

- 시작 전에 `workspace-check` 결과를 기록한다.
- generic startup이면 `workspace_check_mode: generic_startup`
- 현재 저장소 직접 수정이면 `workspace_check_mode: current_repo_maintenance`

### routing

- generic startup이면 `start_surface: clever-agent-project`
- 현재 저장소 직접 수정이면 `start_surface: current-repo`
- 해석 정본은 항상 `clever-context-monorepo`
- 추적 정본은 항상 `clever-change-control`

### derived

- `mono` -> `workload_shape: single_workload`
- `msa` -> `workload_shape: multiple_workloads`

초기 후보는 아래처럼 둔다.

- MSA 새 작업 또는 MSA 기존 변경:
  - `deploy_template_candidate: Clever-ODIC-deploy@v1`
  - `deploy_profile_candidate: image-build-once-central-release`
- MONO는 같은 값을 자동 확정하지 않고, 현재 템플릿/서비스 lineage를 읽은 뒤 채운다.
- `repo_maintenance`는 deploy template 후보를 비워도 된다.

`next_action`은 아래 중 하나로 채운다.

- `collect-missing-startup-fields`
- `read-ssot-and-service-context`
- `draft-project-start`
- `handoff-to-target-repo`
- `stay-in-current-repo-maintenance`

### deferred

아래 값은 시작 분기 단계에서 채우지 않는다.

- `project_start_issue_number`
- `change_id`
- `target_repo`
- `target_service`
- `rollout_scope`

이 값들은 승인 이후 또는 scope 고정 이후에만 채운다.

## 사용 규칙

- 사용자가 자유문으로 시작하면 에이전트가 이 템플릿 구조로 다시 정리한다.
- 부족한 값만 추가 질문한다.
- startup branch state가 비어 있으면 `project-start` 초안으로 넘어가지 않는다.
- 이 템플릿은 helper script output을 대체하지 않는다.
- 이 템플릿은 helper script 실행 전의 intake 정규화 상태를 고정한다.
