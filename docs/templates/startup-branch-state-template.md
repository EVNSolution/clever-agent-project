# startup branch state template

## 목적

이 문서는 세션 첫 대화에서 받은 분기값을 에이전트가 어떤 내부 템플릿으로 정규화해야 하는지 고정한다.

이 템플릿은 `project-start` packet보다 먼저 채운다.

즉 순서는 아래다.

1. 첫 진입시 대화문으로 분기값 수집
2. 이 문서의 startup branch state 채우기
3. SSOT 해석
4. `project-start` 초안과 bootstrap packet 생성

## 사용자에게 보여주는 입력 양식

에이전트는 첫 응답에서 아래처럼 비전공자도 바로 적을 수 있는 템플릿을 사용한다. 전문 용어는 내부 정규화 단계에서만 쓴다.

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

## normalized startup branch state

```yaml
startup_branch:
  work_nature: new_development | feature_change | bugfix | refactor | docs_ops | unknown
  target_scope: new_app_service_feature | existing_app_service_feature | ui | api | db_model | cicd_deploy_workflow | docs_ops_config | unknown
  goal_level: requirements | design_doc | implementation_plan | code_change | test_verification | deploy_preparation | mvp_develop_deploy | operations_rollout | unknown
  project_scope: new_project | existing_project | control_plane_maintenance | unknown
  service_scope: new_service | existing_service_change | docs_or_ops_only | unknown
  architecture_kind: mono | msa | unknown
  session_goal: requirements_definition | design_documentation | planning | implementation_work | test_verification | deploy_preparation | operations_rollout | unknown

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

- `신규 개발` -> `work_nature: new_development`
- `기존 기능 확장/수정` -> `work_nature: feature_change`
- `버그 수정` -> `work_nature: bugfix`
- `리팩터링/구조 개선` -> `work_nature: refactor`
- `문서/설정/운영 정리` -> `work_nature: docs_ops`
- `아직 모름` 또는 `직접 설명` -> `work_nature: unknown` or infer later

- `새 앱/서비스/기능` -> `target_scope: new_app_service_feature`
- `기존 앱/서비스/기능` -> `target_scope: existing_app_service_feature`
- `화면/UI` -> `target_scope: ui`
- `API` -> `target_scope: api`
- `DB/model` -> `target_scope: db_model`
- `CI/CD 또는 배포 workflow` -> `target_scope: cicd_deploy_workflow`
- `문서/운영 설정` -> `target_scope: docs_ops_config`
- `아직 모름` 또는 `직접 설명` -> `target_scope: unknown` or infer later

- `요구사항 정리` -> `goal_level: requirements`
- `설계 문서 작성` -> `goal_level: design_doc`
- `구현 계획 수립` -> `goal_level: implementation_plan`
- `실제 코드 변경` -> `goal_level: code_change`
- `테스트/검증` -> `goal_level: test_verification`
- `배포/운영 준비` -> `goal_level: deploy_preparation`
- `1차 MVP 개발 및 배포` -> `goal_level: mvp_develop_deploy`
- `운영 반영` -> `goal_level: operations_rollout`
- `아직 모름` 또는 `직접 설명` -> `goal_level: unknown` or infer later

- `project_scope`, `service_scope`, and `session_goal` are derived from the above values.
- 첫 입력에서는 MONO/MSA를 묻지 않는다.
- 요청 내용이나 repo 문맥에서 명확하면 `architecture_kind: mono | msa`를 채운다.
- 명확하지 않으면 `architecture_kind: unknown`으로 둔다.

### context

- `하려는 일` -> `requested_work_summary`
- `알고 있는 이름이나 링크` -> `known_repo`, `known_service`, UI/API/DB/document/issue/PR/Figma/log references
- `현재 상태` -> current-state notes in `requested_work_summary` or follow-up context
- `주의할 점` -> `constraints`
- 목표 수준은 `expected_result` and `session_goal` candidates로 함께 사용한다.
- 배경/왜 필요한지는 사용자가 자연어로 말했을 때만 `why_now`에 채운다.

repo와 service가 둘 다 확정되지 않았으면 빈 값으로 둔다.

### workspace

- 시작 전에 `preflight` 결과와 `workspace_check.agent_action`을 기록한다.
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
  - `deploy_template_candidate: Clever-OIDC-deploy@v1`
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
