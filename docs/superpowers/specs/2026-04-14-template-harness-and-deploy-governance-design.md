# Template Harness And Deploy Governance Design

## 목적

`clever-context-monorepo`에 버전 있는 템플릿 카탈로그와 배포 템플릿 정본을 두고, `clever-agent-project`는 항상 사용자에게 템플릿 선택지를 묻는 intake 하네스로 동작하게 고정한다.

이 설계의 목표는 아래와 같다.

- 외부 템플릿을 바로 내부화하지 않고 CLEVER 기준으로 관리 가능한 하네스로 편입한다.
- 템플릿 선택 결과를 서비스 메타와 change-control 기록에 남겨 이후 유지보수의 기본값으로 재사용한다.
- 배포 표준은 서비스 문서마다 중복 복사하지 않고 root 기준 문서와 공통 템플릿 자산으로 관리한다.
- 신규 개발과 유지보수 모두에서 에이전트가 템플릿 선택을 추론으로 결정하지 않고 항상 사용자에게 명시적으로 묻게 한다.

## 기준 저장소

- 시작점 및 intake 하네스 repo: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project`
- 템플릿/배포 정본 및 서비스 메타 repo: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo`
- 변경 추적 repo: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control`
- 외부 upstream 템플릿 후보: `https://github.com/EVNSolution/TEST-Erik-project-template`

## 현재 상태

현재 CLEVER에는 MSA/SaaS 복제형 분기와 서비스 정본 문서는 있지만, 아래 구조는 아직 없다.

- 버전 관리되는 템플릿 카탈로그
- 외부 프로젝트 템플릿을 채택하는 공통 하네스 규칙
- 서비스별 `template lineage` 메타
- root 수준의 배포 템플릿 정본

`clever-context-monorepo/templates/`는 아직 사실상 비어 있고, 서비스 문서의 `배포/운영 방식`은 반복되는 baseline을 각 문서에서 따로 설명하는 상태다.

## 핵심 결정

### 1. 외부 템플릿은 내부 복사보다 하네스 편입으로 시작한다

`TEST-Erik-project-template`는 1차에서 CLEVER 내부 표준 scaffold로 흡수하지 않는다.

대신 아래 방식으로 편입한다.

- upstream template는 외부 repo로 유지한다.
- CLEVER는 이 템플릿을 언제 채택하는지, 어디까지 재사용하는지, 어떤 배포 프로파일과 연결되는지 문서로 고정한다.
- 실제 새 작업 intake에서는 에이전트가 이 템플릿을 하나의 선택지로 제시한다.

이 방식은 유지비를 낮추면서도 추적성과 변경 통제를 확보한다.

### 2. 템플릿 선택지는 항상 사용자에게 묻는다

에이전트는 신규 개발과 유지보수 모두에서 템플릿 후보를 항상 제시한다.

에이전트가 후보를 하나로 추론해 자동 선택하지 않는다.

다만 유지보수에서는 기존 서비스 메타에 기록된 템플릿을 기본 추천으로 제시한다.

즉 원칙은 아래와 같다.

- 선택지는 항상 보여준다.
- 기본 추천은 기존 lineage 또는 recommended 템플릿을 사용한다.
- 최종 선택은 사용자가 한다.

### 3. 템플릿 카탈로그는 버전과 상태를 가진다

`clever-context-monorepo`에는 템플릿 registry를 둔다.

각 템플릿은 아래 정보를 가진다.

- `template_id`
- `version`
- `status` (`recommended`, `legacy`, `deprecated`)
- `use_case`
- `summary`
- `bootstrap_rules`
- `deploy_profile`
- `allowed_override_boundary`
- `known_constraints`

초기 등록 후보는 아래처럼 본다.

- `test-erik-project-template@v1`
- 향후 CLEVER 전용 `msa-saas-standard@v1`
- 향후 CLEVER 전용 `general-service-minimal@v1`

### 4. 서비스 유지보수의 정본은 service 문서 메타다

유지보수 시 에이전트는 과거 대화 로그나 intake repo만 기준으로 삼지 않는다.

정본은 `clever-context-monorepo/docs/services/<service-name>/index.md`의 서비스 메타와 root 거버넌스 문서다.

서비스 문서에는 최소 아래 메타를 둔다.

- `template_id`
- `template_version`
- `deploy_profile`
- `override_scope`
- `lifecycle_state`

이 메타는 유지보수 에이전트가 아래를 빠르게 판단하게 한다.

- 기존 템플릿을 그대로 유지하는지
- 템플릿 영향 범위가 있는 수정인지
- 배포 프로파일 변경인지
- 템플릿 migration 또는 retire가 필요한지

### 5. 템플릿 선택 결과는 세 곳에 남긴다

선택 결과는 대화에만 남기지 않는다.

아래 세 곳에 같은 의미를 남긴다.

- `clever-agent-project` bootstrap packet
- `clever-context-monorepo` 서비스 메타
- `clever-change-control` 이슈 본문

공통 필드는 아래를 기준으로 한다.

- `template_id`
- `template_version`
- `deploy_profile`
- `override_scope`
- `lifecycle_action`

`lifecycle_action`의 초기 후보는 아래와 같다.

- `adopt`
- `modify`
- `migrate`
- `retire`

### 6. 배포 템플릿 baseline은 root 정본과 공통 자산으로 분리한다

배포 표준은 서비스 문서마다 반복 복사하지 않는다.

`clever-context-monorepo` root 문서와 `templates/deploy/` 자산으로 baseline을 관리한다.

서비스 문서는 아래만 적는다.

- 해당 서비스의 실제 deploy profile
- 고객사별 override
- 서비스별 rollout 주의점

공통 baseline은 아래를 root로 끌어올린다.

- image build
- central deploy
- env/secret 분리
- rollout/rollback
- public contract probe
- customer-specific override 기록 규칙

## 문서 배치 설계

### `clever-context-monorepo`

이 repo가 템플릿 정본과 서비스 lineage 정본을 가진다.

추가 후보 문서는 아래와 같다.

- `docs/root/template-harness-governance.md`
- `docs/root/deploy-template-governance.md`
- `docs/templates/index.md`
- `docs/templates/<template-id>/index.md`
- `docs/templates/<template-id>/versions/<version>.md`

추가 후보 자산 경로는 아래와 같다.

- `templates/deploy/README.md`
- `templates/deploy/checklist.md`
- `templates/deploy/env-template.example`
- `templates/deploy/override-guide.md`

`TEST-Erik-project-template`는 `docs/templates/test-erik-project-template/` 아래의 registry entry로 먼저 편입한다.

여기에는 아래를 적는다.

- upstream repo URL
- 채택 적합 조건
- 채택 제외 범위
- 대응되는 deploy profile
- CLEVER 기준에서 해석한 bootstrap 규칙
- known constraints

### `clever-agent-project`

이 repo는 intake 하네스와 질문 절차만 가진다.

수정 후보는 아래와 같다.

- `README.md`
- `.agent/skills/bootstrap-clever-work/SKILL.md`
- `scripts/bootstrap_clever_work.py`

이 repo에는 아래 규칙을 반영한다.

- 템플릿 선택지는 항상 사용자에게 묻는다.
- 신규 개발과 유지보수 모두 템플릿 후보 요약을 보여준다.
- 유지보수면 기존 서비스 메타의 `template_id/version`을 기본 추천으로 제시한다.
- bootstrap packet에 template/deploy 메타를 포함한다.

### `clever-change-control`

이 repo는 추적 저장소로 유지한다.

1차에서는 form 체계를 크게 바꾸기보다 본문 규칙과 README에 아래 메타만 추가한다.

- `template_id`
- `template_version`
- `deploy_profile`
- `lifecycle_action`

즉 change-control은 템플릿 선택의 정본이 아니라, 해당 change 시점의 선택 결과를 추적하는 위치다.

## 사용자 질문 흐름

### 1. 작업 성격 분류 후 템플릿 선택으로 들어간다

에이전트는 먼저 작업을 아래 둘 중 하나로 분류한다.

- `MSA/SaaS 복제형 작업`
- `일반 개발 작업`

그 다음에는 두 분기 모두 템플릿 선택 질문으로 들어간다.

### 2. 템플릿 후보는 항상 제시한다

각 후보는 최소 아래 정보를 가진다.

- `template_id@version`
- `status`
- 한 줄 목적
- 배포 방식 요약
- 현재 작업에 적합한 이유

`deprecated` 템플릿도 필요하면 보여줄 수 있지만 기본 추천안으로 올리지 않는다.

### 3. 신규 개발 질문 방식

신규 개발에서는 템플릿 후보를 항상 나열하고 사용자가 고르게 한다.

예시 형식은 아래와 같다.

```text
신규 개발 기준으로 아래 템플릿 중 어떤 안으로 진행할까요?
1. test-erik-project-template@v1
2. msa-saas-standard@v1
3. general-service-minimal@v1
```

선택 결과는 bootstrap packet과 이후 service 메타에 기록한다.

### 4. 유지보수 질문 방식

유지보수에서는 기존 서비스 메타를 먼저 읽는다.

그 다음 아래처럼 묻는다.

```text
현재 이 서비스는 test-erik-project-template@v1 기반입니다.
기본값은 이 템플릿 유지입니다.
아래 후보 중 어떤 안으로 진행할까요?
```

즉 유지보수에서도 선택지는 항상 보여주되, 기존 lineage를 기본 추천으로 둔다.

### 5. 템플릿 전환은 별도 변화로 기록한다

사용자가 기존 템플릿과 다른 버전이나 다른 템플릿을 선택하면 일반 수정으로 흡수하지 않는다.

이 경우는 `lifecycle_action=migrate` 또는 템플릿 전환 성격의 change로 기록한다.

## 운영 예외 처리

### lineage 정보가 없는 기존 서비스

기존 서비스 문서에 `template_id/version` 메타가 없으면 `lineage unknown`으로 선언한다.

그 다음 템플릿 후보를 다시 제시하고, 이번 선택부터 새 메타를 기록한다.

### 비등록 템플릿 요청

사용자가 registry에 없는 템플릿을 원하면 차단하지 않는다.

다만 아래처럼 기록한다.

- `unregistered template candidate`
- 추후 registry 편입 검토 대상

### deprecated 템플릿 선택

`deprecated` 템플릿은 경고를 주되, 사용자가 원하면 진행할 수 있게 둔다.

단 이 경우에는 change-control과 서비스 메타에 상태를 그대로 남긴다.

### 템플릿과 현재 구조의 충돌

선택된 템플릿과 현재 서비스 구조가 충돌하면 일반 수정으로 밀지 않는다.

이 경우는 아래 중 하나로 분리한다.

- `template mismatch`
- `migration`

## 검증 기준

에이전트는 템플릿 선택 후 아래 일치성을 확인한다.

- bootstrap packet의 template/deploy 메타
- `clever-context-monorepo` 서비스 문서 메타
- `clever-change-control` 이슈 본문 메타

신규 개발이면 선택 템플릿이 registry에 실제 존재하는지 확인한다.

유지보수면 기존 service 메타와 이번 선택이 같은지, 다르면 `migration`으로 분류됐는지 확인한다.

배포 관련 작업이면 `deploy_profile`이 root 배포 문서와 충돌하지 않는지 확인한다.

## 구현 대상 파일 초안

다음 구현 단계에서 아래 파일을 후보로 수정한다.

- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/README.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/.agent/skills/bootstrap-clever-work/SKILL.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/scripts/bootstrap_clever_work.py`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/root/index.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/root/template-harness-governance.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/root/deploy-template-governance.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/templates/index.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/templates/test-erik-project-template/index.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/templates/test-erik-project-template/versions/v1.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/templates/deploy/README.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/templates/deploy/checklist.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/templates/deploy/env-template.example`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/templates/deploy/override-guide.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/services/service-template.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control/README.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control/.github/ISSUE_TEMPLATE/change-request.yml`

## 확인 필요 항목

- 1차 구현에서 `change-control` form 필드까지 즉시 확장할지, README와 본문 규칙만 먼저 반영할지
- `service-template.md`에서 메타를 front matter로 둘지, 명시적 섹션으로 둘지
- `TEST-Erik-project-template` 외 추가 후보 템플릿을 1차부터 같이 등록할지
