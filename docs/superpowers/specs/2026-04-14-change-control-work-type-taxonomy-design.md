# Change Control Work Type Taxonomy Design

## 목적

`clever-change-control`의 변경 요청 이슈에 상위/하위 개발 타입 체계를 도입하고, 에이전트가 이슈 생성 시 같은 규칙으로 제목과 본문을 작성하도록 고정한다.

이 설계의 목표는 아래와 같다.

- `change-control`에 세부 개발 타입을 구조적으로 남긴다.
- GitHub issue form의 제약에 기대기보다, 에이전트가 읽고 따르는 문서 규칙으로 기준을 고정한다.
- 이슈 제목과 본문에 같은 타입 정보를 중복 기록해 사람이 봐도 분류가 명확하도록 한다.
- `clever-agent-project`의 draft 템플릿과 동기화 스크립트가 같은 taxonomy를 쓰게 만든다.
- 기존 단일 `work_type` 자산은 점진적으로 새 구조로 옮기되, 당장 깨지지 않도록 호환 경로를 둔다.

## 기준 저장소

- 시작점 및 draft/동기화 도구 repo: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project`
- 변경 요청 이슈 관리 repo: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control`
- 규칙 및 서비스 문서 정본 repo: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo`

## 현재 상태

현재 `clever-change-control`은 요청 타입 기준으로만 구조가 있다.

- `변경 요청`
- `롤백 요청`

반면 세부 개발 타입은 `clever-agent-project`의 draft 템플릿과 동기화 스크립트에서만 부분적으로 사용한다.

- `신규 개발`
- `수정`
- `변경`
- `리팩토링`

즉, 지금은 `change-control`과 `agent-project` 사이에 세부 타입 체계가 분리돼 있다.

## 핵심 결정

### 1. 정식 taxonomy는 상위/하위 2단 구조로 고정한다

상위 타입은 아래 두 개로 제한한다.

- `MSA/SaaS`
- `일반 개발`

하위 타입은 상위 타입별로 아래처럼 고정한다.

#### `MSA/SaaS`

- `복제`
- `수정`
- `변경`
- `신규`

#### `일반 개발`

- `신규 개발`
- `수정`
- `변경`
- `리팩토링`

이 구조는 이후 문서, 이슈 제목, 이슈 본문, draft 동기화 규칙의 공통 기준이 된다.

### 2. 제목과 본문 둘 다에 타입을 남긴다

정식 제목 형식은 아래로 고정한다.

```text
[상위 타입][하위 타입] 짧은 제목
```

예:

- `[MSA/SaaS][복제] 배차 서비스 고객사 배포 분기 추가`
- `[일반 개발][리팩토링] bootstrap packet 구조 정리`

이슈 본문에도 타입을 구조적으로 남긴다.

예:

```text
work_type_group: MSA/SaaS
work_type_detail: 복제
```

에이전트는 제목과 본문의 타입 값을 항상 일치시켜야 한다.

### 3. GitHub issue form은 검증기보다 안내 문서 역할로 둔다

GitHub issue form의 입력 방식만으로 상위/하위 타입의 정합성을 완전히 강제하지 않는다.

대신 아래 원칙을 따른다.

- issue template에는 상위/하위 타입 필드를 명시한다.
- 설명 문구에 제목 형식과 본문 형식을 같이 적는다.
- 실제로 올바른 조합을 선택하고 제목을 구성하는 책임은 에이전트에 둔다.

즉, 폼은 에이전트에게 필요한 구조를 보여주는 수단이고, 최종 규칙의 정본은 README와 문서다.

### 4. `agent-project`와 `change-control`은 같은 taxonomy를 쓴다

`clever-change-control`에 상위/하위 타입 규칙을 넣더라도, `clever-agent-project`가 계속 단일 `work_type`만 쓰면 곧 다시 어긋난다.

따라서 아래를 함께 바꾼다.

- `clever-change-control` README와 issue template
- `clever-agent-project` README
- `clever-agent-project` draft 템플릿
- `clever-agent-project` issue sync 스크립트
- 관련 테스트

### 5. 전환 초기에는 구형 `work_type` 입력을 호환 처리한다

새 정식 구조는 `work_type_group` + `work_type_detail`다.

다만 기존 draft 자산이 있을 수 있으므로, 동기화 스크립트는 일정 기간 아래 규칙으로 동작한다.

- 새 필드가 있으면 새 필드를 우선 사용한다.
- 새 필드가 없고 기존 `work_type`만 있으면 구형 값을 상/하위 타입으로 변환한다.
- 문서와 템플릿은 즉시 새 형식을 기본값으로 바꾼다.

이렇게 하면 기존 자산을 깨지 않으면서도 앞으로는 새 구조로 수렴시킬 수 있다.

## 문서 및 구현 반영 위치

### `clever-change-control`

#### `README.md`

아래를 명시한다.

- 변경 요청 이슈는 상/하위 개발 타입을 가진다.
- 제목 형식은 `[상위 타입][하위 타입] 짧은 제목`이다.
- 본문에도 `work_type_group`, `work_type_detail`를 남긴다.
- 에이전트는 두 위치의 타입을 일치시켜야 한다.

#### `.github/ISSUE_TEMPLATE/change-request.yml`

아래를 반영한다.

- `work_type_group`
- `work_type_detail`
- 제목 안내 문구
- 본문 타입 안내 문구

필드 형식은 이슈 작성 경험을 해치지 않는 범위에서 선택하되, 중요한 것은 필드 존재보다 설명 문구와 구조 일치다.

### `clever-agent-project`

#### `README.md`

아래를 반영한다.

- `change-control` 이슈 생성 시 상/하위 타입을 반드시 채운다.
- 제목은 `[상위 타입][하위 타입] 짧은 제목`으로 만든다.
- 본문에도 같은 타입 구조를 남긴다.

#### `docs/templates/issue-edit-template.md`

기존 단일 `work_type` 대신 아래 구조를 기본값으로 둔다.

- `work_type_group`
- `work_type_detail`

필요하면 기존 `work_type`는 호환용으로만 유지한다.

#### `scripts/sync_issue_from_md.py`

아래를 반영한다.

- 새 상/하위 필드를 읽는다.
- 제목을 `[상위 타입][하위 타입] 짧은 제목` 형식으로 만든다.
- 새 필드가 없으면 기존 `work_type`를 상/하위 타입으로 변환한다.
- 제목 길이 단축과 종결어 제거 규칙은 유지한다.

#### `tests/test_sync_issue_from_md.py`

아래를 검증한다.

- 새 형식 draft 입력이 올바른 제목으로 변환되는지
- 구형 `work_type` 입력이 새 형식으로 호환 변환되는지

## taxonomy 해석 기준

### `MSA/SaaS`

`clever-context-monorepo`에서 정의한 MSA/SaaS 복제형 분기와 같은 맥락을 쓴다.

- `복제`: 기존 서비스 경계와 책임을 유지하고 고객사별 전개를 위해 복제하는 경우
- `수정`: 고객사별 예외나 기존 SaaS 분기의 좁은 범위 조정
- `변경`: 운영 구조, 연결 방식, 배포 방식이 눈에 띄게 달라지는 경우
- `신규`: 기존 서비스 복제로 보기 어려운 새로운 서비스 단위 또는 새 SaaS 라인

### `일반 개발`

- `신규 개발`: 새로운 기능 또는 새 작업 단위를 개발하는 일반 케이스
- `수정`: 버그 수정, 국소적 로직 수정
- `변경`: 기능/동작/요구사항 변경
- `리팩토링`: 동작 유지 전제의 구조 개선

## 문서화 시 피해야 할 것

- `change-control`에 단일 `work_type`만 정식 기준으로 계속 남겨 두지 않는다.
- 제목에는 타입이 있는데 본문에는 타입이 없는 상태를 허용하지 않는다.
- 본문과 제목 타입이 다른 상태를 허용하지 않는다.
- `MSA/SaaS`와 `일반 개발`의 하위 타입을 한 목록으로 평면화해 의미를 흐리지 않는다.
- GitHub form 제약 때문에 taxonomy 자체를 약하게 만들지 않는다.

## 구현 대상 파일 초안

다음 구현 단계에서 아래 파일을 후보로 수정한다.

- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control/README.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control/.github/ISSUE_TEMPLATE/change-request.yml`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/README.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/templates/issue-edit-template.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/scripts/sync_issue_from_md.py`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/tests/test_sync_issue_from_md.py`

## 확인 필요 항목

- `change-request.yml`에서 상/하위 타입을 각각 dropdown으로 둘지, input으로 둘지, 또는 한쪽만 dropdown으로 둘지
- 구형 `work_type` 값에서 상/하위 타입으로 변환하는 정확한 매핑 표
- 기존 open issue나 draft markdown을 소급 수정할지 여부
