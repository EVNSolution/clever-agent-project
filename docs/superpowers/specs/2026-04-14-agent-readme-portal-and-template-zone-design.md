# Agent README Portal And Template Zone Design

## 목적

`clever-agent-project`의 현재 `README.md`는 레포 소개, 설치, bootstrap 절차, taxonomy, 자산 설명을 한 문서에 함께 담고 있다.

이 설계의 목표는 아래와 같다.

- `README.md`를 GitHub 첫 화면용 포털 문서로 재구성한다.
- 설치/설정/상세 절차는 `docs/setting.md`로 분리한다.
- 신규 개발과 유지보수의 시작 흐름을 한눈에 보이게 만든다.
- 템플릿 후보를 설명만 하지 않고, 물리적으로 분리된 `템플릿 영역`으로 보여준다.
- 유지보수 시에는 항상 서비스 메타를 먼저 읽고 진행한다는 메시지를 전면에 둔다.

## 기준 저장소

- 시작점 repo: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project`
- 템플릿/서비스 메타 정본 repo: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo`
- 변경 추적 repo: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control`
- 외부 템플릿 예시 repo: `https://github.com/EVNSolution/TEST-Erik-project-template`

## 현재 상태

현재 `README.md`는 아래 역할을 동시에 수행하고 있다.

- 레포 소개
- 필수 도구 설치 안내
- `superpowers` 설치 안내
- bootstrap 시작 절차
- work type / template 선택 규칙
- 폴더 구조 설명

이 구조는 정보량은 충분하지만, GitHub 첫 화면에서 아래 문제가 있다.

- 처음 보는 사용자가 어디부터 읽어야 하는지 판단하기 어렵다.
- `이 레포가 실제로 무슨 역할을 하는지`보다 절차 세부사항이 먼저 보인다.
- 템플릿 선택과 유지보수 메타 확인 흐름이 시각적으로 분리되어 보이지 않는다.

## 핵심 결정

### 1. `README.md`는 포털 문서로 축소한다

`README.md`는 더 이상 전체 운영 매뉴얼이 아니다.

이 문서의 역할은 아래로 제한한다.

- 이 레포의 목적 한 줄 설명
- 시작 흐름 요약
- 신규 개발 / 기존 서비스 변경의 진입 차이
- 템플릿 영역
- 핵심 폴더와 문서 링크
- 상세 설정 문서 링크

설치나 세부 절차는 `README.md`에서 직접 길게 설명하지 않는다.

### 2. 상세 운영 문서는 `docs/setting.md`로 분리한다

아래 내용은 `docs/setting.md`로 이동한다.

- GitHub CLI 설치와 인증
- `superpowers` 설치
- bootstrap helper 실행 방법
- 먼저 읽을 문서 순서
- work type 분기 상세
- template/deploy metadata 설명

즉 `README.md`는 입구이고, `docs/setting.md`는 운영 설명서다.

### 3. 템플릿은 별도 `템플릿 영역`으로 보이게 한다

템플릿은 본문 중간 문장으로만 설명하지 않는다.

`README.md`에는 별도 섹션을 두고, 템플릿 후보를 카드형 표 또는 구획 블록처럼 보이게 배치한다.

이 영역은 최소 아래 정보를 보여준다.

- `template_id@version`
- 상태 (`recommended`, `legacy`, `deprecated`, `candidate`)
- 용도
- 배포 프로파일 요약
- 상세 문서 링크

이 구조의 목표는 사용자가 GitHub 첫 화면에서 바로 아래를 이해하게 하는 것이다.

- 신규 개발은 템플릿을 먼저 보고 선택한다.
- 유지보수는 기존 메타를 먼저 읽고 같은 계열을 유지할지 판단한다.
- 템플릿 원본은 별도 템플릿 레포 또는 registry entry에 있다.

### 4. 유지보수 시나리오는 `서비스 메타 먼저 읽기`를 전면에 둔다

`README.md`와 `docs/setting.md` 모두에서 아래 원칙을 명시한다.

- 변경 또는 유지보수는 바로 수정하지 않는다.
- 먼저 `clever-context-monorepo`의 서비스 문서를 읽는다.
- `template_id`, `template_version`, `deploy_profile`, `override_scope`, `lifecycle_state`를 확인한다.
- 그 다음 같은 계열 유지인지, migration인지 판단한다.

즉 유지보수의 시작점은 코드 수정이 아니라 메타 해석이다.

### 5. Mermaid는 GitHub에서 보이되, `README.md`에서는 기본적으로 접어 둔다

큰 흐름도는 GitHub에서 렌더되는 `mermaid`를 사용한다.

다만 `README.md`에서는 첫 화면이 어지럽지 않도록 아래 원칙을 둔다.

- 전체 흐름도는 `<details>` 안에 넣는다.
- 요약 문장과 링크는 접지 않고 기본 노출한다.
- 더 복잡한 전체 절차도는 `docs/setting.md` 또는 별도 diagram 문서에 둔다.

### 6. 템플릿은 설명 개념이 아니라 선택 가능한 공간처럼 보여야 한다

문서 표현상 템플릿은 단순 링크 목록보다 한 단계 더 강하게 보여야 한다.

이를 위해 `README.md`는 아래 섹션 구성을 가진다.

- `신규 개발 시작`
- `기존 서비스 변경`
- `템플릿 영역`
- `핵심 폴더`
- `상세 문서`

이 중 `템플릿 영역`은 물리적으로 다른 블록처럼 보이게 한다.

초기에는 dummy entry를 포함해도 된다.

- `erik-project-template@v1`
- `msa-saas-standard@v1`
- `general-service-minimal@v1`
- `custom candidate`

이 더미/예시 영역은 나중에 실제 registry 상태와 연결되는 시각적 자리 역할을 한다.

## 문서 배치 설계

### `README.md`

상단부터 아래 순서로 재구성한다.

1. 레포 목적 요약
2. `이 레포는 시작점이고, 정본은 다른 repo에 있다`는 설명
3. 신규 개발 / 유지보수 진입 요약
4. `템플릿 영역`
5. 접힌 전체 Mermaid 흐름도
6. 핵심 폴더 링크
7. 상세 문서 링크

이 문서는 사용자가 처음 보고 방향을 잡는 데 필요한 최소 정보만 직접 담는다.

### `docs/setting.md`

이 문서는 실제 운영 설명서로 사용한다.

포함할 내용은 아래와 같다.

- 필수 도구와 인증
- workspace 전제
- 먼저 읽을 문서 순서
- 신규 개발 진입 절차
- 기존 서비스 변경 진입 절차
- template/deploy metadata 설명
- bootstrap helper 사용 예시
- 폴더별 역할 상세
- 관련 repo 링크

### 선택적 보조 문서

필요하면 아래 보조 문서를 추가한다.

- `docs/diagrams/agent-entry-flow.md`

이 문서는 복잡한 Mermaid 다이어그램만 따로 보여주는 용도로 사용할 수 있다.

단, 1차 구현에서는 `README.md`와 `docs/setting.md`만으로도 충분하다.

## README 표현 설계

### 1. 신규 개발 영역

짧은 설명과 함께 아래 메시지를 보여준다.

- 신규 개발은 템플릿 후보를 먼저 검토하고 시작한다.
- 선택된 템플릿과 배포 프로파일이 bootstrap packet 기준이 된다.

### 2. 기존 서비스 변경 영역

짧은 설명과 함께 아래 메시지를 보여준다.

- 유지보수는 먼저 서비스 메타를 읽는다.
- 기존 `template_id / template_version / deploy_profile`을 확인한다.
- 같은 계열 유지인지, template migration인지 결정한 뒤 진행한다.

### 3. 템플릿 영역

템플릿 영역은 표나 블록으로 분리한다.

예시 컬럼은 아래와 같다.

- 템플릿
- 용도
- 배포 방식
- 상태
- 상세 링크

이 영역은 나중에 실제 registry 문서 링크로 연결된다.

### 4. 핵심 폴더 영역

최소 아래 경로를 설명과 함께 링크한다.

- `.agent/skills/bootstrap-clever-work/`
- `docs/`
- `scripts/`
- `tests/`

### 5. 상세 문서 영역

최소 아래 문서를 링크한다.

- `docs/setting.md`
- `docs/guides/clever-project-workflows.md`
- `.agent/skills/bootstrap-clever-work/SKILL.md`

## Mermaid 설계 기준

### `README.md`용 다이어그램

목표는 첫 화면에서 전체 관계를 한눈에 보여주는 것이다.

- 방향: `flowchart TB`
- 언어: 한글
- 기본 상태: 접힘
- 범위:
  - 사용자 요청
  - `clever-agent-project`
  - 신규 / 유지보수 분기
  - 템플릿 영역
  - 서비스 메타 확인
  - `clever-context-monorepo`
  - `clever-change-control`
  - 대상 repo handoff

### `docs/setting.md`용 다이어그램

목표는 실제 절차를 더 자세히 보여주는 것이다.

- 방향: `flowchart TB`
- 언어: 한글
- 기본 상태: 펼침
- 범위:
  - 신규 개발
  - 유지보수
  - 템플릿 선택
  - service metadata read
  - bootstrap packet
  - issue / change tracking
  - repo handoff

## 변경 후 기대 효과

- GitHub 첫 화면에서 레포 역할이 더 빨리 이해된다.
- 템플릿 선택이 실제 시작 절차의 핵심이라는 점이 더 잘 보인다.
- 유지보수도 메타 기반으로 시작한다는 규칙이 눈에 들어온다.
- 긴 설치/절차 문서를 `README.md`에서 걷어내어 진입 피로를 낮춘다.
- 템플릿 레지스트리와의 연결 지점이 문서상 명확해진다.

## 구현 대상 파일 초안

- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/README.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/setting.md`

필요 시 아래도 조정할 수 있다.

- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/guides/clever-project-workflows.md`

## 확인 필요 항목

- 템플릿 영역을 Markdown 표로 시작할지, `blockquote` 기반 카드형 블록으로 시작할지
- 복잡한 다이어그램을 `README.md`에만 둘지, 별도 diagram 문서를 추가할지
- `docs/setting.md` 외에 `docs/diagrams/`를 1차부터 둘지
