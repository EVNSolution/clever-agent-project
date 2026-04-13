# MSA SaaS Entry Governance Design

## 목적

`clever-agent-project`를 CLEVER 작업의 시작점으로 유지하면서, MSA 기반 SaaS 복제형 작업과 일반 개발 작업을 초기에 분기하는 기준을 고정한다.

이 설계의 목표는 아래와 같다.

- 시작 세션에서 에이전트가 작업 성격을 먼저 분류하게 한다.
- MSA SaaS 복제형 작업은 `clever-context-monorepo`의 정본 문서를 먼저 읽게 한다.
- 일반 개발 작업은 기존 `project-start -> target repo 확정 -> 구현 repo handoff` 흐름을 유지하게 한다.
- 운영 원칙의 정본과 탐색 입구를 분리해 문서 중복을 막는다.

## 기준 저장소

- 시작점 repo: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project`
- 운영 원칙 및 서비스 문서 정본 repo: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo`
- 변경 추적 참고 repo: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control`

## 핵심 결정

### 1. 시작점과 정본을 분리한다

`clever-agent-project`는 intake/orchestration 시작점으로 유지한다. 전역 운영 원칙과 서비스별 정본은 `clever-context-monorepo`에 둔다.

이 결정의 이유는 아래와 같다.

- 시작 세션에서 에이전트가 어디서 출발해야 하는지 명확하다.
- 전역 규칙 변경과 서비스 leaf 문서 변경의 정본 위치를 유지할 수 있다.
- `docs/wiki`를 탐색 허브로 유지하고, 실제 판단은 `docs/root`와 `docs/services`로 되돌아가게 할 수 있다.

### 2. 시작 시점에 작업 성격을 먼저 분류한다

에이전트는 `clever-agent-project`에서 시작한 뒤, 아래 두 패턴 중 어느 쪽인지 먼저 판단한다.

- `MSA/SaaS 복제형 작업`
- `일반 개발 작업`

MSA/SaaS 복제형 작업은 "플랫폼 템플릿과 배포 표준을 바탕으로 서비스를 복제하고, 고객사별로 수정/변경을 얹어 SaaS로 전개하는 작업"으로 본다.

일반 개발 작업은 위 분류에 속하지 않는 일반적인 신규 개발, 수정, 변경, 리팩토링, 특정 repo 구현 작업으로 본다.

### 3. MSA/SaaS 복제형 작업은 target service 확정 후 정본 문서를 읽는다

MSA/SaaS 복제형으로 분류되면, 에이전트는 대화로 target service 또는 대상 서비스 군을 먼저 정한다.

그 다음 아래 순서로 `clever-context-monorepo` 문서를 읽는다.

1. 새 전역 root 문서 `docs/root/msa-saas-replication-governance.md`
2. 기존 root 문서 `docs/root/clever-msa-platform-workspace.md`
3. 필요 시 관련 root 문서와 glossary
4. target service가 정해졌으면 `docs/services/<service-name>/index.md`

이 분기에서는 MSA 전용 규칙을 일반 개발의 기본값으로 취급하지 않는다.

### 4. 일반 개발 작업은 기존 bootstrap 흐름을 유지한다

일반 개발로 분류되면, 에이전트는 MSA SaaS 복제형 문서를 강제하지 않는다.

기본 흐름은 아래를 유지한다.

1. `project-start` 초안 작성
2. 승인
3. target repo 제안 또는 확정
4. target repo handoff
5. target repo 중심 구현

## 문서 배치 설계

### `clever-agent-project`에 둘 내용

이 repo에는 짧은 시작점 규칙만 둔다.

후보 위치:

- `README.md`의 시작 흐름 섹션 보강
- 또는 repo-local skill 문서에 "작업 성격 분류" 규칙 추가

여기에 둘 내용은 아래 수준으로 제한한다.

- 작업 시작 시 먼저 `MSA/SaaS 복제형`인지 `일반 개발`인지 분류한다.
- MSA/SaaS 복제형이면 target service를 대화로 정한다.
- 이후 `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo`의 root/service 문서를 읽는다.
- 일반 개발이면 기존 bootstrap 흐름으로 간다.

### `clever-context-monorepo`에 둘 내용

전역 정본은 `docs/root`에 둔다.

새 문서 후보:

- `docs/root/msa-saas-replication-governance.md`

이 문서에는 아래를 담는다.

- MSA SaaS 복제형 작업의 정의
- 복제 / 수정 / 변경 / 신규의 구분 기준
- 언제 새 서비스로 보고, 언제 기존 서비스의 고객사별 변형으로 보는지
- 컨테이너마다 다른 이미지를 올리는 운영 방식의 문서화 기준
- 고객사별 배포 표준, 환경 분리, 이미지 태깅, 설정 분리 원칙
- target service 확정 전과 후의 문서 읽기 순서
- 일반 개발 흐름과 충돌하지 않도록 하는 분기 규칙

서비스별 정본은 기존 규칙대로 `docs/services/<service-name>/index.md`에 둔다.

서비스 leaf 문서에는 아래를 추가로 담을 수 있다.

- 이 서비스가 SaaS 복제형 대상으로 적합한지
- 고객사별로 달라질 수 있는 지점
- 공통 이미지/설정과 고객사별 override 경계
- 배포 시 tenant/customer 분기 주의사항

### `docs/wiki` 처리 원칙

`docs/wiki`는 탐색 허브로만 유지한다.

따라서 새 MSA SaaS 규칙의 정본을 `docs/wiki`에 직접 두지 않는다. 필요하면 `docs/wiki/index.md` 또는 `docs/wiki/services.md`에서 새 root 문서와 서비스 문서로 연결하는 링크만 추가한다.

## 에이전트 판단 절차 초안

에이전트는 시작점에서 아래 절차를 따른다.

1. 현재 작업이 MSA/SaaS 복제형인지 확인한다.
2. 맞다면 target service를 대화로 정한다.
3. `clever-context-monorepo`의 MSA SaaS 전용 root 문서를 읽는다.
4. target service가 정해졌으면 해당 service leaf 문서를 읽는다.
5. target repo 또는 target service repo로 handoff 한다.
6. 일반 개발이면 기존 bootstrap 흐름만 따른다.

## 문서화 시 피해야 할 것

- MSA 규칙을 모든 개발 작업의 기본값으로 선언하지 않는다.
- `clever-agent-project`에 전역 정본을 복제하지 않는다.
- `docs/wiki`를 정본 위치로 승격하지 않는다.
- target service가 정해지지 않았는데 임의 서비스 leaf 문서를 먼저 만들지 않는다.

## 구현 대상 파일 초안

다음 구현 단계에서 아래 파일을 후보로 수정한다.

- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/README.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/root/index.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/root/clever-msa-platform-workspace.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/root/msa-saas-replication-governance.md`
- 필요 시 `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/wiki/index.md`

## 확인 필요 항목

- repo-local skill 문서까지 같이 고칠지, `README.md` 수준의 시작 규칙만 먼저 둘지
- `복제 / 수정 / 변경 / 신규`의 경계 문구를 얼마나 운영적으로 강하게 고정할지
- 고객사별 SaaS 분기를 서비스 leaf 문서에 공통 템플릿으로 강제할지 여부
