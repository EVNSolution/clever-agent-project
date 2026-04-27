# 3레포 시작 모델 정합성 정리

이 문서는 현재 CLEVER 3레포 시작 모델을 한 번에 정리하고, 정본 문서와 현재 문서 사이에 남아 있는 어긋남과 덜 작성된 지점을 기록한다.

## 현재 기준 모델

현재 canonical model은 아래처럼 읽는다.

- generic CLEVER startup: `clever-agent-project`
- 해석 정본: `clever-context-monorepo`
- 승인·추적 정본: `clever-change-control`
- root canonical identifier: `project-start issue #`
- `change_id`: root가 아니라 scoped execution identifier
- repo-local maintenance: 현재 레포가 직접 수정 대상이면 그 레포에서 계속

즉 `항상 clever-agent-project에서 시작`이 아니라, 정확히는 아래가 맞다.

- target repo나 작업 라인이 아직 안 정해진 generic startup은 `clever-agent-project`
- `clever-context-monorepo` 또는 `clever-change-control` 자체를 수정하는 세션은 해당 레포에서 시작 가능

## 현재 정본으로 보는 문서

시작 모델 기준 문서는 아래 우선순위로 본다.

1. `clever-agent-project/AGENTS.md`
2. `clever-agent-project/.agent/skills/bootstrap-clever-work/SKILL.md`
3. `clever-context-monorepo/docs/root/authority-boundaries.md`
4. `clever-context-monorepo/docs/root/agent-runtime-governance.md`
5. `clever-change-control/README.md`

## 이번에 맞춘 부분

아래는 현재 모델에 맞춰 이미 정리된 영역이다.

- `preflight` 자동 감지 추가
- `agent_action` 기준 분기
  - `proceed-with-hard-gate`
  - `current-repo-maintenance`
  - `switch-to-clever-agent-project`
  - `stop-and-fix-workspace`
- 현재 저장소 직접 수정 세션은 `--current-repo-maintenance`로 명시
- `project-start issue #`와 `change_id` 계층 분리
- generic intake에서 확정 `target_service` 비강제
- sibling repo용 경량 `AGENTS.md` 추가
  - generic startup은 `clever-agent-project`로 redirect
  - repo-local maintenance는 현재 레포 유지

## 직접 충돌하던 문구

이번 정리 기준에서 직접 충돌하던 문구는 아래 두 종류였다.

### 1. 절대 표현

예전 문구는 `세션은 항상 clever-agent-project에서 시작한다`처럼 읽혔다.

이 표현은 generic startup에는 맞지만, 아래에는 맞지 않는다.

- `clever-context-monorepo` 자체 수정
- `clever-change-control` 자체 수정

그래서 현재는 `generic startup은 clever-agent-project`, `repo-local maintenance는 현재 레포 유지`로 정리한다.

### 2. 실패와 위치 전환의 혼동

예전 스모크 테스트 문서는 아래 두 경우를 충분히 분리하지 못했다.

- workspace가 실제로 불완전한 경우
- 3레포는 다 있는데 시작 위치만 잘못된 경우

현재는 아래처럼 분리한다.

- incomplete workspace: `stop-and-fix-workspace`
- wrong startup surface with healthy workspace: `switch-to-clever-agent-project`
- current control-plane repo edit with healthy workspace: `current-repo-maintenance`

## 아직 남아 있는 어긋남

아래는 아직 남아 있는 문서 어긋남 또는 주의점이다.

### 1. sibling repo README는 아직 startup model을 충분히 설명하지 않는다

`clever-context-monorepo/README.md`와 `clever-change-control/README.md`는 각 레포의 역할은 설명하지만, 아직 아래를 전면에 두지는 않는다.

- generic startup vs repo-local maintenance 분기
- `preflight` 우선 실행
- `switch-to-clever-agent-project`와 `stop-and-fix-workspace`의 차이

현재는 이 역할을 각 레포의 `AGENTS.md`가 대신한다.

### 2. `docs/setting.md`의 읽기 순서 링크는 GitHub mirror 중심이다

`docs/setting.md`는 클릭 가능한 링크를 위해 GitHub URL을 사용한다.

이 자체가 틀린 것은 아니지만, 실제 authority는 로컬 sibling repo 파일이라는 점을 항상 같이 설명해야 한다.

즉 아래처럼 읽어야 한다.

- 링크는 remote mirror
- authority 판단은 local workspace

### 3. 시작 모델의 end-to-end 검증은 아직 수동 시나리오 중심이다

현재 자동 검증은 `bootstrap_clever_work.py --preflight`와 helper 테스트 수준이다.

아직 없는 것은 아래다.

- 실제 에이전트 첫 응답이 hard gate를 따르는지 보는 end-to-end 자동 검증
- runtime별 차이를 반영한 startup contract 검증

즉 지금은 `helper verification은 자동`, `agent conversation verification은 수동` 상태다.

### 4. repo-local maintenance 시나리오는 설명이 더 필요하다

현재는 `AGENTS.md`에 예외 규칙이 들어갔지만, 아래는 아직 더 적어도 좋다.

- 어떤 요청을 generic startup으로 볼지
- 어떤 요청을 repo-local maintenance로 볼지
- ambiguous case에서 에이전트가 어떤 추가 질문을 해야 하는지

### 5. sibling repo에서의 `preflight` 경로는 sibling layout을 전제로 한다

현재 경량 `AGENTS.md`는 아래 명령을 사용한다.

```bash
python3 ../clever-agent-project/scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --json
```

이건 3레포가 같은 workspace root 아래 sibling으로 있는 구조를 전제로 한다.

즉 현재 모델은 의도적으로 `single-repo portable startup`이 아니라 `fixed sibling workspace startup`이다.

## 덜 작성된 점

현재 기준에서 아직 보강하면 좋은 문서는 아래다.

### 1. sibling repo README의 startup section

권장 추가 항목:

- generic startup이면 `clever-agent-project`로 이동
- repo-local maintenance면 현재 레포 유지
- `preflight` 우선 실행

### 2. repo-local maintenance 예시 문서

권장 내용:

- `clever-context-monorepo` 문서 수정 예시
- `clever-change-control` template 수정 예시
- generic startup과의 구분 기준

### 3. startup decision table

권장 형식:

| 현재 위치 | workspace 상태 | 작업 성격 | 기대 action |
| --- | --- | --- | --- |
| `clever-agent-project` | complete | generic startup | `proceed-with-hard-gate` |
| sibling repo | complete | generic startup | `switch-to-clever-agent-project` |
| sibling repo | complete | repo-local maintenance | `current-repo-maintenance` |
| any repo | incomplete | any | `stop-and-fix-workspace` |

### 4. runtime별 startup behavior note

권장 내용:

- Codex
- Claude Code
- Cursor
- Gemini CLI

같은 `AGENTS.md`와 `SKILL.md`를 읽더라도 실제 첫 응답 반영 방식에는 차이가 있을 수 있다는 운영 메모가 있으면 좋다.

## 현재 결론

현재 모델은 아래처럼 읽으면 된다.

- 시작 계약은 3레포 공통이다.
- generic startup surface는 `clever-agent-project`다.
- `clever-context-monorepo`, `clever-change-control`은 직접 수정할 때만 local start를 허용한다.
- root는 `project-start issue #`, scoped execution은 `change_id`다.
- 아직 덜 적힌 부분은 sibling README startup section, repo-local maintenance 예시, startup decision table, end-to-end startup verification이다.
