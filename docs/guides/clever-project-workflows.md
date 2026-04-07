# CLEVER 프로젝트 작업 흐름

이 문서는 CLEVER 작업을 어떻게 시작해야 하는지, 그리고 아래 상황을 어떻게 구분해야 하는지 설명한다.

- 완전히 새로운 프로젝트를 시작하는 경우
- 이미 존재하는 repo를 개선하는 경우
- 기존 repo 또는 서비스를 재구현하는 경우

## 핵심 원칙

작업의 진짜 시작은 repo 생성이 아니다.

작업의 진짜 시작은 `clever-change-control`에 `project-start` 이슈를 만드는 것이다.

그리고 그 이슈 번호가 전체 작업 라인의 canonical identifier가 된다.

## 저장소별 역할

- `clever-agent-project`: 작업 시작점, intake, orchestration
- `clever-change-control`: root issue, child issue, 승인, 추적
- `clever-context-monorepo`: 규칙, 용어, 문서 경계의 SSOT

## 항상 지켜야 하는 규칙

모든 경우에 아래 규칙은 공통이다.

1. 시작은 `clever-agent-project`에서 한다.
2. 초안 작성 전에 SSOT를 읽는다.
3. repo를 만들거나 바꾸기 전에 `project-start` 초안을 만든다.
4. 승인 전에는 GitHub issue 생성이나 repo bootstrap을 하지 않는다.
5. 생성된 `project-start issue #`를 최상위 식별자로 사용한다.
6. `target_service`는 시작 시 선택 정보로 본다.
7. canonical `change_id`는 만들지 않는다.

## 흐름 1: 새 프로젝트 시작

이 흐름은 작업이 기존 `project-start` 아래에 속하지 않을 때 사용한다.

보통 이런 경우다.

- 완전히 새로운 initiative다.
- 첫 번째 구체적 결정이 “repo를 하나 만들지 둘 이상으로 나눌지”일 수 있다.
- 프로젝트 경계, repo 구조, service 분리가 아직 열려 있다.

실행 순서는 아래와 같다.

1. `clever-agent-project`에서 시작한다.
2. `clever-context-monorepo`와 `clever-change-control`을 읽는다.
3. `project-start` 초안을 만든다.
4. 승인을 받는다.
5. `project-start` 이슈를 생성한다.
6. 생성된 issue 번호를 root identifier로 쓴다.
7. 첫 target repo를 결정한다.
8. 필요하면 GitHub repo를 만든다.
9. 로컬에 clone 또는 pull 한다.
10. 그 target repo에서 새 세션으로 이동한다.

결과는 아래와 같다.

- 하나의 root `project-start`
- 그 root 아래에 0개 이상 repo가 연결될 수 있음
- 이후 child issue들이 같은 root에 매달림

## 흐름 2: 기존 repo 개선

이 흐름은 작업이 이미 진행 중인 프로젝트 라인에 분명히 속할 때 사용한다.

보통 이런 경우다.

- repo가 이미 존재한다.
- initiative에 연결된 유효한 `project-start`가 이미 있다.
- 이번 작업은 그 라인 안의 추가 기능, 수정, 구조 변경이다.

실행 순서는 아래와 같다.

1. 기존 parent `project-start #`를 확인한다.
2. initiative 경계가 바뀌지 않았다면 새 root issue를 만들지 않는다.
3. 작업 성격에 맞는 child issue를 만든다.
4. child issue에서 parent `project-start #`를 참조한다.
5. 기존 target repo의 로컬 checkout을 확인하거나 refresh 한다.
6. 그 repo 세션에서 구현을 계속한다.

child issue 유형은 보통 아래 중 하나다.

- `new`
- `fix`
- `change`
- `refactoring`

결과는 아래와 같다.

- root `project-start`는 그대로 유지
- 그 아래에 새 child issue 추가
- 승인된 변경이 명시적으로 요구하지 않는 한 새 repo는 만들지 않음

## 흐름 3: 기존 repo 또는 서비스 재구현

재구현은 두 갈래로 나뉜다.

### 경우 A: 같은 initiative 안의 큰 내부 재작성

아래에 해당하면 기존 `project-start`를 유지한다.

- 제품 라인이 같다.
- 비즈니스 initiative가 같다.
- 현재 프로젝트의 연장선으로 추적하는 것이 맞다.

이 경우에는 보통 새 root issue 대신 child issue를 만든다. 대개 `refactoring`, 경우에 따라 `change`가 된다.

### 경우 B: 기존 repo를 쓰지만 사실상 새 initiative

아래에 해당하면 새 `project-start`를 만든다.

- 프로젝트가 사실상 재시작되거나 방향이 바뀐다.
- 추적 루트를 새로 나눠야 할 정도로 범위가 크다.
- 비즈니스 목표가 이전과 실질적으로 다르다.
- 승인 흐름, bootstrap 판단, 후속 이슈를 이전 라인과 분리해야 한다.

이 경우에는 repo가 같을 수 있다. 서비스가 같을 수도 있다. 코드베이스가 같을 수도 있다.

하지만 root governance line은 새 `project-start`가 된다.

## 새 `project-start`를 만들지, 기존 것을 쓸지 판단하는 법

질문은 하나다.

이 작업이 같은 initiative 경계 안의 후속 작업인가, 아니면 새로운 root traceability line이 필요한가?

같은 initiative 경계 안이라면:

- 기존 `project-start`를 유지한다.
- 새 child issue를 만든다.

새 root traceability line이 필요하다면:

- 새 `project-start`를 만든다.
- repo가 이미 있어도 그렇게 한다.

## 사용자가 보통 처음에 줘야 하는 정보

대부분의 경우 시작 시 필요한 것은 아래 정도다.

- 목적 또는 배경 1~2문장
- 이미 알고 있는 중요한 제약

처음부터 아래를 모두 확정하게 만들면 안 된다.

- target repo
- target service
- repo 개수
- 상세 구현 계획

## 승인 후 에이전트가 할 수 있는 것

승인 후에는 에이전트가 아래까지 수행할 수 있다.

1. `project-start` 이슈 생성
2. 생성된 issue 번호를 canonical identifier로 사용
3. target repo 제안 또는 확정
4. repo 생성 또는 확인
5. 로컬 clone 또는 pull
6. target repo 기준 새 세션으로 handoff

## 일반 프로젝트에서 하면 안 되는 것

일반적인 프로젝트 실행 중에는 아래를 하면 안 된다.

- SSOT repo를 일반 구현 대상 repo처럼 다루기
- SSOT source를 함부로 수정하기
- `change_id`를 다시 root identifier로 되돌리기
- root issue 초안 전에 `target_service`를 필수로 요구하기

## 짧은 요약

- 새 initiative면 새 `project-start`를 만든다.
- 기존 initiative의 기존 repo 작업이면 기존 `project-start` 아래 child issue로 간다.
- 기존 repo를 쓰더라도 새 initiative면 새 `project-start`를 만든다.
