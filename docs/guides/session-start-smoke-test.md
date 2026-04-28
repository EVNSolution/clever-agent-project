# 세션 시작 스모크 테스트 시나리오

이 문서는 `clever-agent-project`에서 새 세션을 열었을 때, 에이전트가 시작 규칙을 제대로 따르는지 빠르게 검증하는 운영 시나리오다.

[README.md](../../README.md)는 첫 화면용 포털이고, [docs/setting.md](../setting.md)는 운영 설명서이며, [docs/guides/clever-project-workflows.md](clever-project-workflows.md)는 전체 작업 흐름 설명서다. 이 문서는 그중에서도 `새 세션 시작이 제대로 걸리는지`만 본다.

## 목적

이 스모크 테스트는 아래를 검증한다.

1. generic startup의 세션 시작점이 `clever-agent-project`로 고정되는지
2. 에이전트가 첫 응답에서 시작 하드 게이트를 적용하는지
3. `3레포 로컬 워크스페이스` 전제를 먼저 확인하는지
4. 너무 이른 `change_id` 또는 확정 `target_service` 강제가 없는지
5. `project-start` 이전에 구현으로 바로 뛰지 않는지
6. 시작 위치가 잘못되면 `clever-agent-project`로 이동하라고 분기하는지
7. 현재 control-plane 저장소 자체를 수정하는 세션은 여기서 계속하라고 분기하는지

## 이 테스트가 다루는 범위

이 문서는 아래까지만 본다.

- 첫 세션 시작
- 시작 템플릿 적용
- 자유문 입력 정규화
- 최소한의 문맥 해석
- `project-start` 초안으로 넘어갈 준비 상태

이 문서는 아래는 직접 검증하지 않는다.

- 실제 GitHub issue 생성
- target repo 생성 또는 clone
- 구현, 테스트, 배포

## 사전 조건

아래 조건이 먼저 만족되어야 한다.

1. 같은 로컬 workspace root 아래에 아래 3개 레포가 있어야 한다.
   - `clever-agent-project`
   - `clever-context-monorepo`
   - `clever-change-control`
2. 이 문서의 성공 시나리오는 generic startup 기준으로 `clever-agent-project` 루트에서 시작하거나, 자동 감지가 `switch-to-clever-agent-project`를 먼저 해결한 상태를 전제로 한다.
3. 에이전트는 아래 문서를 읽을 수 있어야 한다.
   - `README.md`
   - `docs/setting.md`
   - `docs/guides/clever-project-workflows.md`
   - `.agent/skills/bootstrap-clever-work/SKILL.md`
4. 로컬 파일 접근이 가능해야 한다. 웹 링크만 있는 상태는 통과 조건이 아니다.

운영 환경에서는 첫 질문 전에 아래 자동 감지 명령을 먼저 돌린다.

```bash
CLEVER_EXPECTED_GITHUB_LOGIN="<github-login-or-profile-url>" \
  python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --json
```

이 문서의 시나리오는 그 결과가 `preflight_check.ready=true`이고
`workspace_check.agent_action=proceed-with-hard-gate`일 때 시작 하드 게이트가 제대로 적용되는지 보는 테스트다.

현재 control-plane 저장소 자체를 직접 수정하는 세션은 아래처럼 유지보수 모드로 따로 확인한다.

```bash
CLEVER_EXPECTED_GITHUB_LOGIN="<github-login-or-profile-url>" \
  python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --current-repo-maintenance --json
```

## 시작 템플릿 기준

스모크 테스트에서 기대하는 첫 분기 템플릿은 전문 용어를 앞세우지 않는다. 사용자가 먼저 한 줄로 말하고, 모르는 항목은 `아직 모름`으로 남길 수 있어야 한다.

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

## 합격 기준

아래를 모두 만족하면 스모크 테스트 통과로 본다.

- 첫 응답이 시작 템플릿 또는 그와 동등한 구조로 시작한다.
- 질문 순서가 먼저 `하려는 일 -> 작업 성격 -> 대상 범위 -> 목표 수준`을 따른다.
- 사용자가 모르면 `아직 모름`을 남길 수 있다.
- 첫 템플릿에서 MONO/MSA, `target_service`, change id 같은 전문 용어를 강제하지 않는다.
- 이름/링크/주의사항은 선택 정보로 받고, 선행 조건을 몰라도 시작할 수 있다.
- 사용자가 자유문으로 시작해도 에이전트가 같은 구조로 다시 정리한다.
- `change-control` 타입 해석은 에이전트가 맡고, 사용자가 내부 taxonomy를 직접 채우게 하지 않는다.
- `change_id`를 루트 시작 식별자로 사용하지 않는다.
- 확정 `target_service`를 generic intake에서 필수로 강제하지 않는다.
- 바로 구현, repo bootstrap, scoped change 생성으로 넘어가지 않는다.

## 실패 기준

아래 중 하나라도 나오면 실패로 본다.

- 첫 응답에서 시작 템플릿 없이 바로 구현 질문으로 들어간다.
- 첫 템플릿에서 MONO/MSA, `target_service`, change id, rollout scope를 묻는다.
- `change_id`를 시작 시점 필수값으로 요구한다.
- `target_service`를 generic intake에서 확정값으로 강제한다.
- `project-start` line 없이 scoped change부터 열려고 한다.
- `clever-context-monorepo`, `clever-change-control` 없이도 충분하다고 가정한다.
- 웹 링크만 있으면 된다고 설명한다.

## 권장 테스트 순서

운영 기준으로는 아래 다섯 가지를 한 묶음으로 보는 것이 가장 안정적이다.

1. 구조화된 입력 성공 시나리오
2. 자유문 입력 정규화 시나리오
3. 불완전 워크스페이스 실패 시나리오
4. 시작 위치 전환 시나리오
5. 현재 저장소 직접 수정 시나리오

## 시나리오 1: 구조화된 입력 성공

가장 기본적인 통과 시나리오다. 사용자가 쉬운 시작 템플릿을 그대로 채워 넣는 경우를 본다.

### 테스트 입력

```text
[시작 분기]
먼저 하려는 일을 한 줄로 적어 주세요.
선택지에 맞춰 답해도 되고, 애매하면 문장으로 편하게 설명해도 됩니다.

- 하려는 일: 정산 서비스에 월별 집계 기준을 추가하고 싶다.

아래 항목은 모르면 `아직 모름`으로 둬도 됩니다.
각 항목은 선택지 중 하나를 골라도 되고, 선택지에 딱 맞지 않으면 직접 설명해도 됩니다.

1. 작업 성격은 어디에 가깝나요?
- 기존 기능 확장/수정

2. 대상 범위는 무엇인가요?
- 기존 앱/서비스/기능
- API

3. 이번 작업의 목표 수준은 어디까지인가요?
- 요구사항 정리

4. 알고 있는 이름이나 링크가 있나요? 없으면 비워도 됩니다.
- repo:
- service/app: service-settlement
- 화면:
- API:
- DB/model:
- 문서:
- issue/PR/Figma/회의 메모/에러 로그:

5. 현재 상태를 알고 있나요? 모르면 `아직 모름`으로 둬도 됩니다.
- 이미 되어 있는 것: 아직 모름
- 아직 없는 것: 월별 집계 기준
- 먼저 확인해야 할 것: 기존 정산 서비스 계약

6. 주의할 점이 있나요? 없으면 비워도 됩니다.
- 꼭 지킬 것: 기존 API 계약을 바로 깨면 안 된다.
- 피할 것:
- 건드리면 안 되는 범위:
- 보안/운영/배포 관련 주의사항:
```

### 기대 동작

에이전트는 아래처럼 움직여야 한다.

1. 입력을 intake로 받아들인다.
2. 쉬운 답변을 `work_nature=feature_change`, `target_scope=existing_app_service_feature`, `goal_level=requirements`로 정규화하고 `project_scope=existing_project`, `service_scope=existing_service_change`, `session_goal=requirements_definition`을 파생한다.
3. 구조는 첫 질문에서 묻지 않고, 서비스 문서와 repo 문맥을 읽은 뒤 추론한다.
4. 내부적으로는 `change-control` taxonomy 후보를 해석하되, 사용자가 taxonomy 필드를 직접 채우게 하지 않는다.
5. `clever-context-monorepo/docs/services/service-settlement/index.md` 같은 관련 서비스 문서를 읽을 준비를 한다.
6. 필요한 경우에만 부족한 칸을 좁혀 묻는다.
7. 바로 `change_id`를 만들지 않는다.
8. 바로 구현 계획으로 뛰지 않는다.
9. 목표는 `project-start` payload 초안 준비 상태까지다.

### 합격 포인트

- 에이전트가 입력 구조를 그대로 유지한다.
- `project-start issue #`가 루트 식별자라는 원칙을 유지한다.
- service 문맥 해석을 먼저 하고, scoped execution은 나중으로 미룬다.

## 시나리오 2: 자유문 입력 정규화 성공

실제 운영에서는 사용자가 템플릿 없이 자유문으로 시작하는 경우가 많다. 이 시나리오는 에이전트가 자유문을 쉬운 시작 템플릿 구조로 되돌릴 수 있는지 본다.

### 테스트 입력

```text
정산 쪽을 좀 손봐야 하는데, 월별 마감 집계 기준이 지금 운영 방식이랑 안 맞아요.
어떤 레포인지 정확히는 모르고, 일단 설명을 정리해서 시작하고 싶어요.
```

### 기대 동작

에이전트는 아래처럼 움직여야 한다.

1. 자유문을 그대로 받되, 바로 구현으로 들어가지 않는다.
2. 사용자의 문장을 쉬운 시작 템플릿 구조로 다시 정리한다.
3. 먼저 아래를 분명하게 만든다.
   - `하려는 일`
   - `1. 작업 성격은 어디에 가깝나요?`
   - `2. 대상 범위는 무엇인가요?`
   - `3. 이번 작업의 목표 수준은 어디까지인가요?`
4. repo/service 이름은 모르면 비워 둔다.
5. 사용자가 `change-control` taxonomy를 직접 선택하게 하지 않는다.
6. 필요한 경우 `service-settlement` 같은 candidate service를 제안하되, generic intake 시작 단계에서 확정 강제는 하지 않는다.

### 합격 포인트

- 자유문이 intake 구조로 다시 정리된다.
- 질문이 너무 많이 한 번에 쏟아지지 않는다.
- 여전히 `change_id`와 scoped execution은 뒤로 미뤄진다.

## 시나리오 3: 불완전 워크스페이스 실패

이 시나리오는 환경이 불완전할 때 에이전트가 그 사실을 분명히 말하는지 본다.

### 실패 조건 예시

- `clever-context-monorepo`가 로컬에 없음
- `clever-change-control`이 로컬에 없음

### 기대 동작

에이전트는 아래 원칙을 따라야 한다.

1. `3레포 로컬 워크스페이스`가 불완전하다고 먼저 말한다.
2. 웹 링크만으로는 해석과 추적 품질이 떨어진다고 설명한다.
3. 부족한 레포를 보완하기 전에는 완전한 startup interpretation으로 가장하지 않는다.
4. 구현이나 scoped execution으로 바로 넘어가지 않는다.

### 기대 문구 예시

```text
CLEVER requires a local three-repository workspace:
`clever-agent-project`, `clever-context-monorepo`, and `clever-change-control`.
This workspace is incomplete, so startup interpretation and traceability are degraded.
```

## 시나리오 4: 시작 위치 전환

이 시나리오는 3레포 로컬 workspace는 완전하지만, generic startup을 잘못된 control-plane repo에서 시작했을 때를 본다.

### 시작 위치 예시

- `clever-context-monorepo`
- `clever-change-control`

### 기대 동작

에이전트는 아래처럼 움직여야 한다.

1. 먼저 `preflight`를 돌린다.
2. 로컬 3레포 workspace가 완전하다고 확인한다.
3. 하지만 현재 위치가 generic startup surface가 아니라는 점을 인식한다.
4. `switch-to-clever-agent-project`로 분기한다.
5. 이 경우 실패처럼 중단하지 않고, 시작 위치만 옮기도록 안내한다.

### 기대 문구 예시

```text
The control-plane workspace is present, but startup should begin from `clever-agent-project`.
Switch there before applying the first-response hard gate.
```

## 시나리오 5: 현재 저장소 직접 수정

이 시나리오는 `clever-context-monorepo` 또는 `clever-change-control` 자체를 직접 수정하는 세션을 본다.

### 시작 위치 예시

- `clever-context-monorepo`에서 root 문서 수정
- `clever-change-control`에서 issue template 수정

### 기대 동작

에이전트는 아래처럼 움직여야 한다.

1. 먼저 `preflight`를 돌린다.
2. 로컬 3레포 workspace가 완전하다고 확인한다.
3. 현재 control-plane 저장소 자체를 수정하는 세션이라고 본다.
4. `current-repo-maintenance`로 분기한다.
5. 이 경우 `clever-agent-project`로 redirect하지 않고 현재 저장소에서 계속한다.

### 기대 문구 예시

```text
This session appears to be editing the current control-plane repository itself.
Stay in the current repository and treat it as the target for this session.
```

## 운영자 체크리스트

새 세션을 눈으로 검토할 때는 아래만 보면 된다.

- 시작 위치가 `clever-agent-project`인가
- 첫 응답이 시작 템플릿 구조인가
- `하려는 일 -> 작업 성격 -> 대상 범위 -> 목표 수준` 질문 순서를 먼저 지키는가
- 모르는 항목을 억지로 요구하지 않고 `아직 모름`을 허용하는가
- `change_id`를 너무 일찍 꺼내지 않는가
- `target_service`를 generic intake에서 확정 강제하지 않는가
- `project-start` 이전에 구현 계획으로 뛰지 않는가
- 워크스페이스가 비었으면 그 사실을 분명히 말하는가
- 3레포가 다 있어도 시작 위치가 틀리면 `clever-agent-project`로 이동시키는가
- 현재 control-plane 저장소 직접 수정 세션은 여기서 계속하도록 분기하는가

## 권장 운영 방법

가장 가벼운 검증은 아래처럼 한다.

1. `clever-agent-project` 루트에서 새 세션 시작
2. 시나리오 1 입력으로 한 번 확인
3. 자유문으로 시나리오 2 한 번 확인
4. 필요하면 의도적으로 sibling repo 하나를 치운 상태에서 시나리오 3 확인
5. `clever-context-monorepo` 또는 `clever-change-control`에서 generic startup을 시작해 시나리오 4 확인
6. `clever-context-monorepo` 또는 `clever-change-control` 자체 수정 작업으로 시나리오 5 확인

이 다섯 가지가 모두 통과하면, 최소한 시작 게이트와 시작 위치 분기는 의도대로 동작한다고 볼 수 있다.

## 다음 단계

이 스모크 테스트가 통과한 뒤에 다음으로 보는 것은 아래 중 하나다.

1. `project-start` payload 초안 품질
2. target repo handoff 규칙
3. preflight 자동화
